from django.test import TestCase
from .scoring import compute_scores

class ScoringTests(TestCase):
    def test_basic_scoring(self):
        tasks = [
            {'title':'A', 'due_date': None, 'estimated_hours': 0.5, 'importance': 8, 'dependencies': []},
            {'title':'B', 'due_date': '2025-12-01', 'estimated_hours': 4, 'importance': 9, 'dependencies': ['0']},
        ]
        res = compute_scores(tasks)
        self.assertEqual(len(res), 2)
        self.assertIn('score', res[0])

    def test_cycle_detection(self):
        tasks = [
            {'title':'A','dependencies':['1']}, 
            {'title':'B','dependencies':['0']},
        ]
        res = compute_scores(tasks)
        self.assertEqual(len(res), 2)
        self.assertTrue(any('cycle_penalty' in r['reason'] for r in res))

    def test_past_due_increases_urgency(self):
        tasks = [
            {'title':'Old','due_date':'2020-01-01','estimated_hours':1,'importance':5,'dependencies':[]},
            {'title':'Later','due_date':'2030-01-01','estimated_hours':1,'importance':5,'dependencies':[]},
        ]
        res = compute_scores(tasks)
        self.assertGreater(res[0]['score'], res[1]['score'])

    def test_missing_fields(self):
        tasks = [
            {'title':'Minimal'},
            {}
        ]
        res = compute_scores(tasks)
        self.assertEqual(len(res), 2)
        self.assertIn('score', res[0])
