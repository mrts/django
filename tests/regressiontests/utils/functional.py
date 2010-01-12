from unittest import TestCase

from django.utils.functional import lazy


class FunctionalTestCase(TestCase):
    def test_lazy(self):
        t = lazy(lambda: tuple(range(3)), list, tuple)
        for a, b in zip(t(), range(3)):
            self.assertEqual(a, b)
