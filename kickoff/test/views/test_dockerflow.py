import os
from tempfile import mkstemp

from kickoff import app
from kickoff.test.views.base import ViewTest


class TestDockerflow(ViewTest):

    def setUp(self):
        ViewTest.setUp(self)
        self.version_fd, self.version_file = mkstemp()
        app.config["VERSION_FILE"] = self.version_file

        with open(self.version_file, "w+") as f:
            f.write("""
{
  "source":"https://github.com/mozilla/balrog",
  "version":"1.0",
  "commit":"abcdef123456"
}
""")

    def tearDown(self):
        os.close(self.version_fd)
        os.remove(self.version_file)
        ViewTest.tearDown(self)

    def testVersion(self):
        ret = self.get("/__version__")
        self.assertEqual(ret.data, """
{
  "source":"https://github.com/mozilla/balrog",
  "version":"1.0",
  "commit":"abcdef123456"
}
""")

    def testLbHeartbeat(self):
        ret = self.get("/__lbheartbeat__")
        self.assertEqual(ret.status_code, 200)
