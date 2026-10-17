-- All graph features are calculated at the daily snapshot cutoff.
CREATE OR REPLACE VIEW visible_transfers AS
SELECT t.* FROM transfers t JOIN episodes e USING(episode_id)
WHERE t.event_time <= e.cutoff AND t.observed_at <= e.cutoff;

CREATE OR REPLACE VIEW visible_devices AS
SELECT d.* FROM device_use d JOIN episodes e USING(episode_id)
WHERE d.event_time <= e.cutoff AND d.observed_at <= e.cutoff;

CREATE OR REPLACE TABLE features AS
WITH incoming AS (
 SELECT episode_id, dst AS account_id, count(DISTINCT src) AS fan_in,
 sum(amount) AS amount_in FROM visible_transfers GROUP BY episode_id,dst
), outgoing AS (
 SELECT episode_id, src AS account_id, count(DISTINCT dst) AS fan_out,
 sum(amount) AS amount_out FROM visible_transfers GROUP BY episode_id,src
), sharing AS (
 SELECT a.episode_id,a.account_id,count(DISTINCT b.account_id) AS device_peers
 FROM visible_devices a JOIN visible_devices b
 ON a.episode_id=b.episode_id AND a.device_id=b.device_id
 AND a.account_id<>b.account_id GROUP BY a.episode_id,a.account_id
), cycles AS (
 SELECT DISTINCT a.episode_id,a.src AS account_id
 FROM visible_transfers a JOIN visible_transfers b
 ON a.episode_id=b.episode_id AND a.dst=b.src
 JOIN visible_transfers c ON b.episode_id=c.episode_id AND b.dst=c.src AND c.dst=a.src
 WHERE a.src<>a.dst AND a.src<>b.dst AND a.dst<>b.dst
 AND a.event_time<b.event_time AND b.event_time<c.event_time
 AND c.event_time-a.event_time<=INTERVAL '30 minutes'
)
SELECT a.episode_id,a.account_id,e.day,e.cutoff,a.age_days,
 coalesce(i.amount_in,0) AS amount_in,coalesce(o.amount_out,0) AS amount_out,
 coalesce(i.fan_in,0) AS fan_in,coalesce(o.fan_out,0) AS fan_out,
 coalesce(s.device_peers,0) AS device_peers,
 CASE WHEN c.account_id IS NULL THEN 0 ELSE 1 END AS timed_cycle,
 least(coalesce(i.amount_in,0),coalesce(o.amount_out,0)) /
 greatest(coalesce(i.amount_in,0),1) AS pass_through
FROM accounts a JOIN episodes e USING(episode_id)
LEFT JOIN incoming i USING(episode_id,account_id)
LEFT JOIN outgoing o USING(episode_id,account_id)
LEFT JOIN sharing s USING(episode_id,account_id)
LEFT JOIN cycles c USING(episode_id,account_id);
