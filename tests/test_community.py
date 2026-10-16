import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync_labels', ROOT / 'scripts/sync_labels.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

class LabelPlanTests(unittest.TestCase):
    def setUp(self):
        self.label = dict(name='bug', color='D73A4A', description='오류', scope='all')

    def test_idempotent_and_does_not_remove_custom_labels(self):
        old = [dict(self.label, color='d73a4a'), dict(name='custom', color='ffffff')]
        self.assertEqual(sync.plan([self.label], old), [])

    def test_update_preserves_label_identity(self):
        old = [dict(self.label, description='old')]
        self.assertEqual(sync.plan([self.label], old), [('update', self.label)])

    def test_community_labels_stay_in_community_repo(self):
        label = dict(self.label, name='소통: 공지', scope='community')
        self.assertEqual(sync.plan([label], []), [])
        self.assertEqual(sync.plan([label], [], community=True), [('create', label)])
