from kickoff import app
from kickoff.test.base import TestBase


class ViewTest(TestBase):
    auth = {'REMOTE_USER': 'bob'}

    def setUp(self):
        TestBase.setUp(self)
        self.client = app.test_client()

    def get(self, *args, **kwargs):
        return self.client.get(*args, environ_base=self.auth, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, environ_base=self.auth, **kwargs)
