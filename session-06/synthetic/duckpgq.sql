-- Run AFTER run_lab.py, in a fresh connection to fraud.duckdb.
-- Requires compatible DuckPGQ binary; not exercised in the authoring environment.
INSTALL duckpgq FROM community;
LOAD duckpgq;
-- These physical tables are a point-in-time graph, not the raw future-inclusive data.
CREATE OR REPLACE TABLE graph_transfers AS SELECT * FROM visible_transfers;
CREATE OR REPLACE TABLE graph_devices AS SELECT * FROM visible_devices;
CREATE OR REPLACE TABLE devices AS SELECT DISTINCT device_id FROM graph_devices;
CREATE PROPERTY GRAPH fraud_graph
VERTEX TABLES (accounts, devices)
EDGE TABLES (
 graph_transfers SOURCE KEY (src) REFERENCES accounts (account_id)
 DESTINATION KEY (dst) REFERENCES accounts (account_id),
 graph_devices SOURCE KEY (account_id) REFERENCES accounts (account_id)
 DESTINATION KEY (device_id) REFERENCES devices (device_id)
);
-- Exercise A: shared device. Match results should equal the SQL answer below.
SELECT DISTINCT account_a,account_b,device_id
FROM GRAPH_TABLE (fraud_graph
 MATCH (a:accounts)-[x:graph_devices]->(d:devices)<-[y:graph_devices]-(b:accounts)
 WHERE a.account_id < b.account_id
 COLUMNS (a.account_id AS account_a,b.account_id AS account_b,d.device_id AS device_id)
) ORDER BY account_a,account_b;
-- Exercise B: directed two-hop transfer paths. This is reachability, not proof
-- that the same money flowed through both edges. Add time ordering as a task.
SELECT * FROM GRAPH_TABLE (fraud_graph
 MATCH (a:accounts)-[t1:graph_transfers]->(b:accounts)-[t2:graph_transfers]->(c:accounts)
 WHERE a.account_id <> c.account_id
 COLUMNS (a.account_id AS sender,b.account_id AS intermediary,c.account_id AS recipient)
) LIMIT 20;
-- Cleanup before repeating: DROP PROPERTY GRAPH fraud_graph;
