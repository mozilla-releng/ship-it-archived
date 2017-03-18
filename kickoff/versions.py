from distutils.version import LooseVersion
from types import StringType


class MozVersion(LooseVersion):
    """Mozilla-specific implementation of version parsing"""
    def __cmp__(self, other):
        if isinstance(other, StringType):
            other = MozVersion(other)

        # Exclude "esr" from comparison only if both versions contain "esr".
        # See Bug 1348428 for the background.
        if "esr" in self.version and "esr" in other.version:
            return cmp([v for v in self.version if v != "esr"],
                       [v for v in other.version if v != "esr"])
        else:
            return cmp(self.version, other.version)
