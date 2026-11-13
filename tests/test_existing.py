"""已有接口的核心、边界及错误路径。"""
import unittest,tempfile
from pathlib import Path
from lake.storage import read_source,Objects,digest

class StorageTests(unittest.TestCase):
    def test_source_and_corruption(self):
        value=read_source()
        with tempfile.TemporaryDirectory() as d:
            o=Objects(d);key=o.put(value);self.assertEqual(o.get(key),value)
            self.assertEqual(o.put(value),key)
            Path(d,key).write_bytes(b'bad')
            with self.assertRaises(ValueError):o.get(key)
    def test_bad_object_identity(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):Objects(d).get('../bad')

from lake.plan import node_id,shareable
from lake.channels import Source

class FeatureTests(unittest.TestCase):
    def test_scopes(self):
        n={'op':'scan','snapshot':'s','schema':'v1','collation':'binary','visibility_scope':'A','determinism':'deterministic'}
        self.assertTrue(shareable(n));self.assertNotEqual(node_id(n),node_id(dict(n,visibility_scope='B')))
        self.assertFalse(shareable(dict(n,determinism='volatile')))
    def test_independent_cursors(self):
        s=Source([{'x':1},{'x':2}],1);a=s.open(s.digest);b=s.open(s.digest)
        self.assertEqual(a.pull()['seq'],0);a.close();self.assertEqual(b.pull()['rows'],[{'x':1}])
        with self.assertRaises(RuntimeError):a.pull()
        with self.assertRaises(ValueError):s.open('old')
