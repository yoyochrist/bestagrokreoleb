"""Behavior checks for the inspectable code embedded in the Session 8 notebook."""
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

NOTEBOOK = Path(__file__).with_name('Kreo_Digital_Session_08_Q_Learning_Fraud_Review.ipynb')
scope = {}
if NOTEBOOK.exists():
    notebook = json.loads(NOTEBOOK.read_text())
    for cell in notebook['cells']:
        if 'lesson-core' in cell.get('metadata', {}).get('tags', []):
            exec(''.join(cell['source']), scope)


class ReviewLessonTests(unittest.TestCase):
    def setUp(self):
        self.assertIn('ReviewEnv', scope, 'Notebook must expose its lesson-core cell')

    def test_budget_and_reward_trace(self):
        env = scope['ReviewEnv'](np.array([[0, 0], [1, 1]]), [1, 0], 1)
        self.assertEqual(env.reset(), (0, 0, 1, 0))
        state, reward, done = env.step(1)
        self.assertEqual((state, reward, done), ((1, 1, 0, 1), 10.0, False))
        with self.assertRaises(ValueError):
            env.step(1)
        self.assertEqual(env.position, 1)
        self.assertEqual(env.step(0), (None, 0.0, True))
        with self.assertRaises(RuntimeError):
            env.step(0)

    def test_all_four_rewards(self):
        for action, label, expected in [(1, 1, 10), (1, 0, -1), (0, 1, -10), (0, 0, 0)]:
            env = scope['ReviewEnv']([[0, 0]], [label], 1)
            self.assertEqual(env.step(action)[1], expected)

    def test_input_validation(self):
        for contexts, labels, budget in [([], [], 0), ([[0, 0]], [2], 1),
                                         ([[0, 0]], [0], -1), ([[0, 0]], [0], 2),
                                         ([[0, 0]], [0, 1], 1)]:
            with self.assertRaises(ValueError):
                scope['ReviewEnv'](contexts, labels, budget)

    def test_worked_update_and_masked_bootstrap(self):
        state, nxt = (0, 0, 1, 0), (0, 0, 0, 1)
        q = {state: np.array([2., 0.]), nxt: np.array([4., 999.])}
        scope['q_update'](q, state, 0, 3, nxt, False, alpha=.5, gamma=.9)
        self.assertAlmostEqual(q[state][0], 4.3)
        scope['q_update'](q, state, 1, 10, None, True, alpha=.5, gamma=.9)
        self.assertEqual(q[state][1], 5.)

    def test_mask_ties_and_unseen_states(self):
        choose = scope['choose_action']
        rng = np.random.default_rng(42)
        state = (0, 0, 0, 0)
        self.assertEqual(choose({state: np.array([-2., 999.])}, state, rng, 1), 0)
        q = {}
        self.assertEqual(choose(q, (0, 0, 1, 0), rng, 0), 0)
        self.assertEqual(q, {}, 'Evaluating unseen states must not mutate the Q-table')

    def test_deterministic_training_and_frozen_evaluation(self):
        ctx = np.array([[0, 0], [1, 1], [0, 0], [1, 1]])
        y = np.array([0, 1, 0, 1])
        kwargs = dict(episode_length=2, budget=1, epochs=3, seed=7)
        q1, history1 = scope['train_q'](ctx, y, **kwargs)
        q2, history2 = scope['train_q'](ctx, y, **kwargs)
        self.assertEqual(set(q1), set(q2))
        for key in q1:
            np.testing.assert_array_equal(q1[key], q2[key])
        pd.testing.assert_frame_equal(history1, history2)
        before = {key: value.copy() for key, value in q1.items()}
        metrics, trace = scope['evaluate_policy'](ctx, y, [1, 2, 3, 4], 'q', q=q1,
                                                 episode_length=2, budget=1)
        self.assertEqual(metrics['budget_violations'], 0)
        self.assertTrue((trace.groupby('episode').action.sum() <= 1).all())
        self.assertEqual(set(q1), set(before))
        for key in q1:
            np.testing.assert_array_equal(q1[key], before[key])

    def test_partial_windows_zero_denominators_and_short_data(self):
        ctx = np.zeros((5, 2), dtype=int)
        metrics, trace = scope['evaluate_policy'](ctx, [0]*5, np.arange(5), 'never',
                                                 episode_length=2, budget=1)
        self.assertEqual((metrics['evaluated_rows'], metrics['dropped_rows']), (4, 1))
        self.assertTrue(np.isnan(metrics['precision']))
        self.assertTrue(np.isnan(metrics['recall']))
        with self.assertRaises(ValueError):
            scope['evaluate_policy'](ctx[:1], [0], [1], 'never', episode_length=2, budget=1)

    def test_all_baselines_use_same_budget_and_rows(self):
        ctx, labels, amounts = np.zeros((7, 2), int), [0, 1, 0, 1, 0, 0, 1], [1, 4, 3, 7, 2, 6, 8]
        for policy in ['never', 'random', 'first', 'threshold', 'offline_amount', 'q']:
            metrics, trace = scope['evaluate_policy'](ctx, labels, amounts, policy,
                episode_length=3, budget=1, threshold=3, q={})
            self.assertEqual(metrics['evaluated_rows'], 6)
            self.assertEqual(metrics['dropped_rows'], 1)
            self.assertEqual(metrics['budget_violations'], 0)
            self.assertEqual(metrics['frauds_found'] + metrics['missed_fraud'], 2)

    def test_step_groups_and_training_only_amount_edges(self):
        frame = pd.DataFrame({'step': np.repeat(np.arange(1, 11), 10),
                              'type': ['PAYMENT']*100, 'amount': np.arange(100),
                              'isFraud': [0]*100})
        parts, contexts, edges, boundaries = scope['prepare_data'](frame)
        self.assertLess(parts['train'].step.max(), parts['validation'].step.min())
        self.assertLess(parts['validation'].step.max(), parts['test'].step.min())
        expected = np.unique(np.quantile(np.log1p(parts['train'].amount), [.25, .5, .75]))
        np.testing.assert_array_equal(edges, expected)
        altered = frame.copy()
        altered.loc[altered.step > boundaries[0], 'amount'] = 1e9
        altered.loc[altered.step > boundaries[0], 'isFraud'] = 1
        _, changed_contexts, changed_edges, _ = scope['prepare_data'](altered)
        np.testing.assert_array_equal(changed_edges, edges)
        np.testing.assert_array_equal(changed_contexts['train'], contexts['train'])


if __name__ == '__main__':
    unittest.main()
