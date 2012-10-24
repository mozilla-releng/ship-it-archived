def getReleaseName(product, version, buildNumber):
    return '%s-%s-%s' % (product.title(), version, str(buildNumber))
