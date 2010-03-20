import unittest
import pickle

from models import PickleMe

class PickleUgettextLazyTest(unittest.TestCase):
    def test_pickle_ugettext_lazy(self):
        qs1 = PickleMe.objects.filter(name__icontains="pickle")
        query_pickled = pickle.dumps(qs1.query)

        qs2 = PickleMe.objects.all()
        qs2.query = pickle.loads(query_pickled)

        self.assertEquals(str(qs1.query), str(qs2.query))
