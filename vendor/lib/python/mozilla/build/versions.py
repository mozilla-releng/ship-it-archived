import re

from mozilla.release.info import isFinalRelease

# Regex that matches all possible versions and milestones
ANY_VERSION_REGEX =\
    ('(\d+\.\d[\d\.]*)'  # A version number
    '((a|b)\d+)?'        # Might be an alpha or beta
    '(esr)?'             # Might be an esr
    '(pre)?')            # Might be a 'pre' (nightly) version

def getPossibleNextVersions(version):
    """Return possibly next versions for a given version.
       There's a few distinct cases here:
       * ESRs:  The only possible next version is the next minor version.
                Eg: 17.0.3esr -> 17.0.4esr
       * Betas: The next beta with the same major version and also the next
                major version's beta 1. Eg: 18.0b4 -> 18.0b5, 19.0b1
       * Other: The next major version's .0 release and the next minor version.
                Eg: 15.0 -> 15.0.1, 16.0; 17.0.2 -> 17.0.3, 18.0

       Versions with 'pre' are deprecated, and explicitly not supported.
    """
    ret = set()
    # Get the parts we care about from the version. The last group is the 'pre'
    # tag, which doesn't affect our work.
    m = re.match(ANY_VERSION_REGEX, version)
    if not m:
        return ret
    base, beta, _, esr = m.groups()[:4]
    # The next major version is used in a couple of places, so we figure it out
    # ahead of time. Eg: 17.0 -> 18.0 or 15.0.3 -> 16.0
    nextMajorVersion = increment(base.split('.')[0]) + '.0'
    # ESRs are easy, just increment the version to get the next minor version.
    if esr:
        ret.add(increment(version))
    # Betas are similar, except we need the next major version's beta 1, too.
    elif beta:
        ret.add(increment(version))
        ret.add('%sb1' % nextMajorVersion)
    # Other releases are a bit more complicated, because we need to handle
    # going from a x.y -> x.y.z version number.
    else:
        ret.add(nextMajorVersion)
        if isFinalRelease(version):
            ret.add('%s.1' % version)
        else:
            ret.add(increment(version))
    return ret


# The following function was copied from http://code.activestate.com/recipes/442460/
# Written by Chris Olds
lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
def increment(s):
    """ look for the last sequence of number(s) in a string and increment """
    m = lastNum.search(s)
    if m:
        next = str(int(m.group(1))+1)
        start, end = m.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s
