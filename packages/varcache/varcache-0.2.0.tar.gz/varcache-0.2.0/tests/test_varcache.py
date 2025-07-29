from unittest import TestCase

from varcache import Varcache, AlreadyLoadedError


class TestVarcache(TestCase):
    def setUp(self):
        self.vcache = Varcache(dirpath='./tmp')

    def tearDown(self):
        self.vcache.clear_all()

    def test(self):
        obj1 = self.vcache.load(name='obj1', default=dict)
        obj1['x'] = 25
        self.vcache.save(obj1)

        with self.assertRaises(AlreadyLoadedError):
            obj1_dup = self.vcache.load(name='obj1', default=dict)

        self.vcache.unbind(obj1)

        obj1_dup = self.vcache.load(name='obj1', default=dict)
        self.assertEqual(obj1_dup['x'], 25)
