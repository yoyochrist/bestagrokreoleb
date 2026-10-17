"""IEEE-CIS transaction scoring with strictly historical shared-attribute features."""
import argparse
import json
from pathlib import Path
import duckdb
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

p=argparse.ArgumentParser()
p.add_argument('--data-dir',type=Path,required=True)
p.add_argument('--output-dir',type=Path,default=Path('outputs/ieee_cis'))
p.add_argument('--limit',type=int,default=60000,help='Earliest N chronological labelled rows; 0 means all')
a=p.parse_args()
a.output_dir.mkdir(parents=True,exist_ok=True)
c=duckdb.connect()
# Parameterized input paths; read IDs as strings to preserve anonymized categories.
c.execute('CREATE TABLE tx AS SELECT * FROM read_csv_auto(?,all_varchar=true)',[str(a.data_dir/'train_transaction.csv')])
c.execute('CREATE TABLE ident AS SELECT * FROM read_csv_auto(?,all_varchar=true)',[str(a.data_dir/'train_identity.csv')])
for table in ['tx','ident']:
    n,u=c.execute(f'SELECT count(*),count(DISTINCT TransactionID) FROM {table}').fetchone()
    if n!=u: raise ValueError(f'Duplicate or null TransactionID in {table}')
required=['TransactionID','TransactionDT','TransactionAmt','ProductCD','card1','card2','card3','card4','card5','card6','addr1','addr2','P_emaildomain','isFraud']
if not set(required)<=set(r[0] for r in c.execute('DESCRIBE tx').fetchall()):
    raise ValueError('Missing required transaction columns')
c.execute('''CREATE TABLE joined AS SELECT t.*,i.DeviceInfo,i.DeviceType
FROM tx t LEFT JOIN ident i USING(TransactionID)''')
c.execute('''CREATE TABLE ordered AS SELECT *,CAST(TransactionDT AS BIGINT) AS dt,
CAST(TransactionAmt AS DOUBLE) AS amount,CAST(isFraud AS INTEGER) AS y
FROM joined ORDER BY CAST(TransactionDT AS BIGINT),TransactionID''')
if a.limit:
    if a.limit<100: raise ValueError('Use at least 100 rows')
    c.execute('DELETE FROM ordered WHERE TransactionID NOT IN (SELECT TransactionID FROM ordered ORDER BY dt,TransactionID LIMIT ?)',[a.limit])
# Fixed time boundaries, never divide transactions with the same timestamp.
times=[r[0] for r in c.execute('SELECT DISTINCT dt FROM ordered ORDER BY dt').fetchall()]
if len(times)<10: raise ValueError('Insufficient distinct times')
b1=times[int(len(times)*.60)];b2=times[int(len(times)*.80)]
c.execute('''CREATE TABLE nodes AS SELECT *,
CASE WHEN card1 IS NOT NULL AND card2 IS NOT NULL AND card3 IS NOT NULL
AND card4 IS NOT NULL AND card5 IS NOT NULL AND card6 IS NOT NULL
THEN CAST(to_json(list_value(card1,card2,card3,card4,card5,card6)) AS VARCHAR) END AS card_proxy
FROM ordered''')
# Incidence graph: transaction -> attribute value. Missing values create NO edge.
# DeviceInfo, domains and card composites are proxies, NOT unique real entities.
c.execute('''CREATE TABLE edges AS
SELECT TransactionID,dt,'card_proxy' AS kind,card_proxy AS value FROM nodes WHERE card_proxy IS NOT NULL
UNION ALL SELECT TransactionID,dt,'device_attribute',DeviceInfo FROM nodes WHERE DeviceInfo IS NOT NULL
UNION ALL SELECT TransactionID,dt,'email_domain',P_emaildomain FROM nodes WHERE P_emaildomain IS NOT NULL''')
# RANGE ends at dt-1; tied-time events cannot observe each other. 7-day lookback.
c.execute('''CREATE TABLE history AS SELECT *,
count(*) OVER(PARTITION BY kind,value ORDER BY dt RANGE BETWEEN 604800 PRECEDING AND 1 PRECEDING) AS prior_7d
FROM edges''')
c.execute('''CREATE TABLE features AS SELECT n.TransactionID,n.dt,n.y,n.amount,
CASE WHEN n.DeviceInfo IS NULL THEN 1 ELSE 0 END AS device_missing,
CASE WHEN n.card_proxy IS NULL THEN 1 ELSE 0 END AS card_proxy_missing,
coalesce(max(CASE WHEN h.kind='card_proxy' THEN h.prior_7d END),0) AS card_history,
coalesce(max(CASE WHEN h.kind='device_attribute' THEN h.prior_7d END),0) AS device_history,
coalesce(max(CASE WHEN h.kind='email_domain' THEN h.prior_7d END),0) AS domain_history
FROM nodes n LEFT JOIN history h USING(TransactionID)
GROUP BY n.TransactionID,n.dt,n.y,n.amount,n.DeviceInfo,n.card_proxy''')
rows=c.execute('SELECT * FROM features ORDER BY dt,TransactionID').fetchall()
y=np.array([r[2] for r in rows]); dt=np.array([r[1] for r in rows])
X=np.array([[float(v) if v is not None else np.nan for v in r[3:]] for r in rows])
if not np.all(np.isin(y,[0,1])): raise ValueError('isFraud must be binary')
if not np.isfinite(X[:,0]).all(): raise ValueError('Invalid transaction amounts')
train=dt<b1;cal=(dt>=b1)&(dt<b2);test=dt>=b2
for name,mask in [('train',train),('calibration',cal),('test',test)]:
    if len(np.unique(y[mask]))!=2: raise ValueError(f'{name} needs both classes; increase --limit')
# Modest numeric baseline for teaching; not a leaderboard-complete feature set.
# No current/future labels or historical fraud rates are graph inputs.
prob={}
for name,idx in [('transaction',list(range(3))),('graph',list(range(6)))]:
    m=HistGradientBoostingClassifier(max_iter=80,max_leaf_nodes=15,random_state=42)
    m.fit(X[train][:,idx],y[train]);prob[name]=m.predict_proba(X[:,idx])[:,1]
iso=IsolationForest(n_estimators=100,random_state=42,n_jobs=1)
iso.fit(X[train,:3]);raw=-iso.score_samples(X[:,:3])
ref=np.sort(raw[train]);anomaly=np.searchsorted(ref,raw,side='right')/len(ref)
# Training-only reference for an illustrative high-amount rule.
threshold=np.quantile(X[train,0],.95)
rule=(X[:,0]>threshold).astype(float)
# Graph activity is a structural frequency signal, not a fraud probability.
gref=np.sort(np.log1p(X[train,3:].sum(axis=1)))
graw=np.log1p(X[:,3:].sum(axis=1))
gscore=np.searchsorted(gref,graw,side='right')/len(gref)
scores={'supervised_transaction':prob['transaction'],'supervised_graph':prob['graph']}
for name,z in [('hybrid_without_graph',np.column_stack([rule,prob['transaction'],anomaly])),
               ('hybrid_with_graph',np.column_stack([rule,prob['graph'],anomaly,gscore]))]:
    m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42))
    m.fit(z[cal],y[cal]);scores[name]=m.predict_proba(z)[:,1]
report={'rows':len(rows),'split_counts':{'train':int(train.sum()),'calibration':int(cal.sum()),'test':int(test.sum())},
        'time_boundaries':[int(b1),int(b2)],'label_availability_assumption':'Training labels available at fitting; actual confirmation times unavailable',
        'protocol':'Online replay: later transactions may use earlier unlabelled observations, never same-time or future observations',
        'metrics':{}}
for name,s in scores.items():
    yy=y[test];ss=s[test];k=min(100,len(yy));top=np.argsort(-ss,kind='stable')[:k]
    report['metrics'][name]={'average_precision':float(average_precision_score(yy,ss)),
    'brier_score':float(brier_score_loss(yy,ss)),'precision_at_k':float(yy[top].mean()),
    'recall_at_k':float(yy[top].sum()/yy.sum()),'k':k,'prevalence':float(yy.mean())}
(a.output_dir/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
for table in ['features','edges']:
    dest=str(a.output_dir/f'{table}.parquet').replace("'","''")
    c.execute(f"COPY {table} TO '{dest}' (FORMAT PARQUET)")
print(json.dumps(report,indent=2))
