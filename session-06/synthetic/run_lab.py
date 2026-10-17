"""Synthetic educational experiment. Run from any directory; writes beside this file."""
from pathlib import Path
from datetime import datetime, timedelta
import csv
import json
import random
import duckdb
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, brier_score_loss

ROOT = Path(__file__).resolve().parent
rng = random.Random(42)
con = duckdb.connect(str(ROOT / 'fraud.duckdb'))
con.execute('''
CREATE OR REPLACE TABLE episodes(episode_id INTEGER,day INTEGER,cutoff TIMESTAMP);
CREATE OR REPLACE TABLE accounts(episode_id INTEGER,account_id VARCHAR PRIMARY KEY,age_days INTEGER);
CREATE OR REPLACE TABLE transfers(episode_id INTEGER,src VARCHAR,dst VARCHAR,amount DOUBLE,event_time TIMESTAMP,observed_at TIMESTAMP);
CREATE OR REPLACE TABLE device_use(episode_id INTEGER,account_id VARCHAR,device_id VARCHAR,event_time TIMESTAMP,observed_at TIMESTAMP);
CREATE OR REPLACE TABLE labels(account_id VARCHAR,y INTEGER,label_available_at TIMESTAMP);
''')
eps,acc,tx,dev,labels=[],[],[],[],[]
# 90 independent daily batches; identities never overlap across splits.
for day in range(1,91):
    cutoff=datetime(2026,1,1)+timedelta(days=day,hours=12)
    eps.append((day,day,cutoff))
    for case in range(10):
        ids=[f'D{day:02d}C{case}A{i}' for i in range(8)]
        fraud=rng.random()<0.18
        hub=(not fraud and rng.random()<0.25)
        for i,aid in enumerate(ids):
            acc.append((day,aid,rng.randint(1,90) if fraud else rng.randint(1,500)))
            # All accounts in a fraud case are labelled for this toy experiment.
            labels.append((aid,int(fraud),cutoff+timedelta(days=2)))
            shared=(fraud and i<6) or (hub and i<5)
            did=f'D{day}C{case}'+('SHARED' if shared else f'P{i}')
            dev.append((day,aid,did,cutoff-timedelta(hours=2),cutoff-timedelta(hours=2)))
        def add(s,d,minute):
            at=cutoff-timedelta(minutes=60-minute)
            tx.append((day,ids[s],ids[d],round(rng.uniform(50,900),2),at,at))
        # Normal traffic with similar amounts; graph structure carries extra context.
        for _ in range(rng.randint(3,7)):
            s,d=rng.sample(range(8),2); add(s,d,rng.randint(0,45))
        if fraud or hub:
            for i in range(1,6): add(i,0,5+i)
            for i in range(1,5): add(0,i,20+i)
        if fraud or rng.random()<0.03:
            add(0,6,30);add(6,7,35);add(7,0,40)
        # Poison records: event in the future, and past event arriving late.
        tx.append((day,ids[0],ids[1],999999,cutoff+timedelta(hours=1),cutoff+timedelta(hours=1)))
        tx.append((day,ids[1],ids[0],999999,cutoff-timedelta(hours=1),cutoff+timedelta(hours=1)))
for table,rows in [('episodes',eps),('accounts',acc),('transfers',tx),('device_use',dev),('labels',labels)]:
    con.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in rows[0])})",rows)
con.execute((ROOT/'features.sql').read_text())
assert con.execute('SELECT count(*) FROM features').fetchone()[0]==7200
assert con.execute('SELECT max(amount) FROM visible_transfers').fetchone()[0]<1000
# Test event-time and observation-time exclusion independently.
assert con.execute('SELECT count(*) FROM transfers').fetchone()[0]-con.execute('SELECT count(*) FROM visible_transfers').fetchone()[0]==1800
assert con.execute('SELECT count(*) FROM features WHERE timed_cycle=1').fetchone()[0]>0
rows=con.execute('''SELECT f.*,l.y FROM features f JOIN labels l USING(account_id)
ORDER BY day,account_id''').fetchall()
cols=[c[0] for c in con.description]
ix={c:i for i,c in enumerate(cols)}
# No identifiers, labels, timestamps, day, or case types enter the models.
base=['age_days','amount_in','amount_out']
graph=['fan_in','fan_out','device_peers','timed_cycle','pass_through']
X=np.array([[r[ix[c]] for c in base+graph] for r in rows],dtype=float)
y=np.array([r[ix['y']] for r in rows]); days=np.array([r[ix['day']] for r in rows])
train=days<=48; calibration=(days>=51)&(days<=63); test=days>=66
# Day 49-50 and 64-65 are embargoes so labels are available before next stage.
assert con.execute('''SELECT count(*) FROM labels l JOIN accounts a USING(account_id)
WHERE a.episode_id<=48 AND l.label_available_at>
(SELECT min(cutoff) FROM episodes WHERE day=51)''').fetchone()[0]==0
assert con.execute('''SELECT count(*) FROM labels l JOIN accounts a USING(account_id)
WHERE a.episode_id BETWEEN 51 AND 63 AND l.label_available_at>
(SELECT min(cutoff) FROM episodes WHERE day=66)''').fetchone()[0]==0

def classifier(indices):
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=42))
    model.fit(X[train][:,indices],y[train]); return model.predict_proba(X[:,indices])[:,1]
p=classifier(list(range(3)))
p_graph=classifier(list(range(8)))
iso=IsolationForest(n_estimators=100,contamination='auto',random_state=42,n_jobs=1)
iso.fit(X[train,:3]) # unlabelled mixed population; not selected by ground truth
raw=-iso.score_samples(X[:,:3])
reference=np.sort(raw[train]); anomaly=np.searchsorted(reference,raw,side='right')/len(reference)
rules=np.minimum(1,X[:,1]/4000)
graph_risk=np.clip(0.30*np.minimum(X[:,3]/5,1)+0.15*np.minimum(X[:,4]/5,1)
                   +0.30*np.minimum(X[:,5]/5,1)+0.25*X[:,6],0,1)
# Reproduce the deck's four-way formula, as an illustrative uncalibrated risk.
illustrative=.15*rules+.40*p+.15*anomaly+.30*graph_risk
# Learned logistic stacking on the later calibration window; never on test.
# Its output is a probability estimate; calibration is evaluated, not guaranteed.
z_base=np.column_stack([rules,p,anomaly])
z_graph=np.column_stack([rules,p_graph,anomaly,graph_risk])
scores={'A_rules':rules,'B_supervised':p,'E_deck_fixed_weights':illustrative}
for name,z in [('C_hybrid_without_graph',z_base),('D_hybrid_with_graph',z_graph)]:
    stack=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=42))
    stack.fit(z[calibration],y[calibration]); scores[name]=stack.predict_proba(z)[:,1]

def metrics(score):
    yt=y[test];st=score[test];k=50
    order=np.argsort(-st,kind='stable')[:k]
    return {'average_precision':float(average_precision_score(yt,st)),
            'precision_at_50':float(yt[order].mean()),
            'recall_at_50':float(yt[order].sum()/yt.sum()),
            'test_accounts':int(test.sum()),'test_prevalence':float(yt.mean())}
report={name:metrics(s) for name,s in scores.items()}
for name in ['B_supervised','C_hybrid_without_graph','D_hybrid_with_graph']:
    report[name]['brier_score']=float(brier_score_loss(y[test],scores[name][test]))
(ROOT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
# Review threshold selected ONLY on calibration set to target ~10% review rate.
final=scores['D_hybrid_with_graph']; threshold=float(np.quantile(final[calibration],.9))
queue=[]
for j,r in enumerate(rows):
    if test[j] and final[j]>=threshold:
        reasons=[]
        if X[j,3]>=5: reasons.append('FAN_IN')
        if X[j,5]>=4: reasons.append('SHARED_DEVICE')
        if X[j,6]: reasons.append('TIME_ORDERED_CYCLE')
        queue.append((r[ix['account_id']],round(float(final[j])*100,2),'|'.join(reasons) or 'MODEL_COMBINATION'))
queue.sort(key=lambda r:(-r[1],r[0]))
with (ROOT/'review_queue.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['account_id','risk_score','reason_codes']);w.writerows(queue)
# Export inputs for learners who prefer SQL or notebooks.
(ROOT/'data').mkdir(exist_ok=True)
for table in ['episodes','accounts','transfers','device_use','labels']:
    target=str(ROOT/'data'/f'{table}.csv').replace("'","''")
    con.execute(f"COPY {table} TO '{target}' (HEADER, DELIMITER ',')")
print(json.dumps(report,indent=2))
print(f'Checks passed. Review threshold={threshold:.4f}; queued={len(queue)}. Outputs in {ROOT}')
con.close()
