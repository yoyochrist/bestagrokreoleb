# Session 08: Q-Learning for Budgeted Fraud Review

## Intent and scope

Create one integrated, runnable Jupyter lesson following Session 7. The user selected sending transactions to review as the agent's task. The proposed implementation uses tabular Q-learning and the existing PaySim CSV. It teaches a simulated review policy, not production fraud prevention or autonomous payment blocking.

## Approaches

- Selected direction: sequential review selection with finite capacity. Reviewing now consumes capacity that could be used later, making future value relevant to Q-learning.
- Alternative: independently classify each transaction as review/pass. This is simpler but lacks an action-dependent future constraint and is closer to a contextual bandit.
- Alternative: approve/block payments. This requires assumptions about interventions and losses beyond the selected review task.

Tabular Q-learning, notebook format, episode size, reward values and state bins below are author proposals rather than user-specified requirements.

## Data and leakage controls

Reuse `session-07/data/PS_20174392719_1491204439457_log.csv`, with an environment variable override and explicit setup instructions. Validate the schema and sample uniformly without using fraud labels. Sort by step and source row index, then split by complete step groups into chronological training, validation and final test periods. Fit all transformations on training only. Freeze configuration after validation; evaluate the final test once.

Use transaction type and training-fitted amount bins for transaction context. Exclude account IDs, fraud labels, existing rule flags and all balance fields from policy inputs. Labels may be used inside the training reward simulator and for evaluation, with that distinction explained explicitly. Never use a future label or future transaction in the observed state.

## Environment and learning

An episode is a fixed-length chronological transaction window, proposed length 200 with 10 review slots. All policies see identical windows and initial budgets; use only complete windows and report dropped rows. No episode crosses a data split. State: type, amount bin, remaining budget and transaction position. Exact budget and position preserve resource accounting, while aggregated transaction features make this a simplified approximate state representation, not a claim of an exact Markov model of real fraud.

Actions: PASS or REVIEW. REVIEW is unavailable at zero budget. Advance one transaction after either action. Passing advances time; reviewing also decrements capacity. End at the final transaction; use zero bootstrap value on terminal transitions and mask invalid actions in both selection and the Bellman maximum.

Proposed illustrative utility: review fraud +10, review legitimate -1, pass fraud -10, pass legitimate 0. These are teaching assumptions, not measured money or guaranteed loss prevention. The simulator assumes labels are available after each training decision, including passed transactions. Explain that real review systems usually have selective and delayed feedback, and this simulation does not solve those issues.

Implement an inspectable NumPy Q-table, epsilon-greedy training, decaying epsilon, deterministic seeds, explicit update equation, one hand-calculated update and a tiny resource-allocation example. Keep the final policy frozen with exploration disabled. Document tie-breaking and unseen-state behavior. Do not repeatedly train against final-test results or claim convergence from a single run.

## Lesson structure

1. Learning objectives, relationship to Session 7 and simulation assumptions.
2. State, action, reward, episode, discount, exploration and Q-table concepts.
3. PaySim setup, validation, sampling and chronological splits.
4. Environment walkthrough with state and budget trace.
5. Bellman update and a worked numerical example.
6. Train tabular Q-learning; chart episode rewards and review usage.
7. Validate and freeze settings; explain sparse state coverage.
8. Compare on final test: never review, seeded random budget-feasible selection, chronological first-available review, training-fitted amount threshold, and offline top-amount ranking as a clearly labeled look-ahead reference.
9. Inspect policy decisions and remaining capacity; explain why Q-learning need not outperform baselines.
10. Exercises on rewards, budgets, discounting, leakage, delayed feedback and deployment limits, followed by an assessment rubric. Leave student answers unfilled.

Report undiscounted utility, review count, precision among reviewed transactions, fraud recall, missed fraud and budget violations. Define zero-denominator results explicitly. Keep reward optimization and fraud-detection metrics distinct. Reuse fixed validation-selected settings across comparisons. Run a small fixed collection of training seeds where runtime permits and describe observed variability without production claims.

## Artifacts and verification

Create `session-08/README.md`, `requirements.txt`, `VALIDATION.md` and one notebook; add the Session 8 link to root README. Ignore downloaded PaySim files and generated outputs at precise new-session paths. Preserve existing Session 7 user changes. No upload or push is included in this request.

Export manifest with data hash, versions, split boundaries, seed and utility assumptions; Q-table; training diagnostics; held-out policy metrics; decision trace; and executed notebook under ignored `session-08/outputs/`.

Verify notebook schema and syntax, terminal updates, invalid-action masking, capacity accounting, deterministic replay, split separation and budget-feasible evaluation. Execute all required cells on actual PaySim, capture outputs, and record exact execution scope. If Q-learning performs poorly, retain and explain the result. Never substitute generated fixture results for real-data evaluation.
