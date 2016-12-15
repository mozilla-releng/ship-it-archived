from datetime import timedelta, datetime
import mock

from kickoff import app
from kickoff.model import FennecRelease
from kickoff.test.base import TestBase


class TestRelease(TestBase):
    def testGetRecent(self):
        with app.test_request_context():
            got = [r.name for r in FennecRelease.getRecent(age=timedelta(days=1))]
            # These two fennec build don't have any date.
            # Ship-it will consider today's date
            self.assertEquals(['Fennec-1.0-build1', 'Fennec-4.0-build4'], got)

    def testGetRecentShipped(self):
        with app.test_request_context():
            with mock.patch('kickoff.model.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2015, 3, 1)
                got = [r.name for r in FennecRelease.getRecentShipped(age=timedelta(days=2))]
                self.assertEquals(['Fennec-23.0b2-build4', 'Fennec-24.0-build4'], got)
