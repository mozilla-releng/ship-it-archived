from unittest import TestCase
from kickoff.versions import MozVersion


class TestMozVersion(TestCase):

    def test_major(self):
        self.assertTrue(MozVersion("2") > MozVersion("1"))
        self.assertTrue(MozVersion("20") > MozVersion("1"))
        self.assertTrue(MozVersion("10") > MozVersion("1"))
        self.assertTrue(MozVersion("10") > MozVersion("2"))

    def test_release_version(self):
        self.assertTrue(MozVersion("2.0") > MozVersion("1.0"))
        self.assertTrue(MozVersion("20.0") > MozVersion("1.0"))
        self.assertTrue(MozVersion("10.0") > MozVersion("1.0"))
        self.assertTrue(MozVersion("10.0") > MozVersion("2.0"))

    def test_nightly_version(self):
        self.assertTrue(MozVersion("2.0a1") > MozVersion("1.0a1"))
        self.assertTrue(MozVersion("20.0a1") > MozVersion("1.0a1"))
        self.assertTrue(MozVersion("10.0a1") > MozVersion("1.0a1"))
        self.assertTrue(MozVersion("10.0a1") > MozVersion("2.0a1"))

    def test_aurora_version(self):
        self.assertTrue(MozVersion("2.0a2") > MozVersion("1.0a2"))
        self.assertTrue(MozVersion("20.0a2") > MozVersion("1.0a2"))
        self.assertTrue(MozVersion("10.0a2") > MozVersion("1.0a2"))
        self.assertTrue(MozVersion("10.0a2") > MozVersion("2.0a2"))

    def test_beta_version(self):
        self.assertTrue(MozVersion("2.0b1") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("20.0b1") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("10.0b1") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("10.0b1") > MozVersion("2.0b1"))

        self.assertTrue(MozVersion("2.0b2") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("20.0b2") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("10.0b2") > MozVersion("1.0b1"))
        self.assertTrue(MozVersion("10.0b2") > MozVersion("2.0b1"))

    def test_esr_version(self):
        self.assertTrue(MozVersion("2.0esr") > MozVersion("1.0esr"))
        self.assertTrue(MozVersion("2.0.1esr") > MozVersion("2.0esr"))
        self.assertTrue(MozVersion("2.0.1esr") > MozVersion("2.0.0esr"))
        self.assertTrue(MozVersion("2.0.2esr") > MozVersion("2.0.1esr"))
        self.assertTrue(MozVersion("2.1.2esr") > MozVersion("2.0.3esr"))

    def test_esr_and_release(self):
        # Fallback to default LooseVersion behaviour
        self.assertTrue(MozVersion("2.0") < MozVersion("2.0esr"))
