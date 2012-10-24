def getReleaseName(product, version, buildNumber):
    return '%s-%s-build%s' % (product.title(), version, str(buildNumber))
