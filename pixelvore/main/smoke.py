from smoketest import SmokeTest
from .models import Image


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = Image.objects.all().count()
        # all we care about is not getting an exception
        self.assertTrue(cnt > -1)
