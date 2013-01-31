import re

FINAL_RELEASE_REGEX = "^\d+\.\d+$"

def getReleaseName(product, version, buildNumber):
    return '%s-%s-build%s' % (product.title(), version, str(buildNumber))

def isFinalRelease(version):
    return bool(re.match(FINAL_RELEASE_REGEX, version))
