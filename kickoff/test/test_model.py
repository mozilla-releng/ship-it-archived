from datetime import timedelta

from kickoff import app
from kickoff.model import FennecRelease
from kickoff.test.base import TestBase


class TestRelease(TestBase):
    def testGetRecent(self):
        with app.test_request_context():
            got = [r.name for r in FennecRelease.getRecent(age=timedelta(days=1))]
            # These two fennec build don't have any date.
            # Ship-it will consider today's date
            self.assertEquals(['Fennec-1-build1', 'Fennec-4-build4'], got)
