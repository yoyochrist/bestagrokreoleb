-- Shared devices: SQL counterpart to DuckPGQ exercise A.
SELECT DISTINCT a.account_id AS account_a,b.account_id AS account_b,a.device_id
FROM visible_devices a JOIN visible_devices b
ON a.device_id=b.device_id AND a.account_id<b.account_id
ORDER BY account_a,account_b;
-- Account features / motifs.
SELECT * FROM features WHERE fan_in>=5 ORDER BY fan_in DESC;
SELECT * FROM features WHERE fan_out>=5 ORDER BY fan_out DESC;
SELECT * FROM features WHERE timed_cycle=1 ORDER BY account_id;
-- Time-ordered two-hop paths.
SELECT a.src,a.dst AS intermediary,b.dst,a.event_time,b.event_time
FROM visible_transfers a JOIN visible_transfers b
ON a.episode_id=b.episode_id AND a.dst=b.src
WHERE a.src<>b.dst AND a.event_time<b.event_time
AND b.event_time-a.event_time<=INTERVAL '30 minutes';
-- Bounded reachability with cycle prevention: depth 1..3, unique result pairs.
WITH RECURSIVE paths AS (
 SELECT src AS origin,dst AS node,1 AS depth,[src,dst] AS visited
 FROM visible_transfers WHERE src<>dst
 UNION ALL
 SELECT p.origin,t.dst,p.depth+1,list_append(p.visited,t.dst)
 FROM paths p JOIN visible_transfers t ON p.node=t.src
 WHERE p.depth<3 AND NOT list_contains(p.visited,t.dst)
)
SELECT origin,node,min(depth) AS hops FROM paths GROUP BY origin,node;
-- Future/late records excluded from the graph.
SELECT count(*) AS excluded FROM transfers t JOIN episodes e USING(episode_id)
WHERE t.event_time>e.cutoff OR t.observed_at>e.cutoff;
