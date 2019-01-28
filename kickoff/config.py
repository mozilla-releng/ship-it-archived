# WARNING: If you update this file, please also keep
# https://github.com/mozilla/release-services/blob/master/src/shipit/api/shipit_api/config.py
# up to date. It's not used in production yet, but better to keep things in
# sync.
# To make flake8 happy
NIGHTLY_VERSION = "66.0a1"
LATEST_THUNDERBIRD_NIGHTLY_VERSION = "67.0a1"
LATEST_THUNDERBIRD_ALPHA_VERSION = "54.0a2"
SUPPORTED_NIGHTLY_LOCALES = ['ach', 'af', 'an', 'ar', 'as', 'ast', 'az', 'be', 'bg', 'bn-BD', 'bn-IN', 'br', 'bs', 'ca', 'cak', 'crh', 'cs', 'cy', 'da', 'de', 'dsb', 'el', 'en-CA', 'en-GB', 'en-US', 'en-ZA', 'eo', 'es-AR', 'es-CL', 'es-ES', 'es-MX', 'et', 'eu', 'fa', 'ff', 'fi', 'fr', 'fy-NL', 'ga-IE', 'gd', 'gl', 'gn', 'gu-IN', 'he', 'hi-IN', 'hr', 'hsb', 'hu', 'hy-AM', 'ia', 'id', 'is', 'it', 'ja', 'ja-JP-mac', 'ka', 'kab', 'kk', 'km', 'kn', 'ko', 'lij', 'lo', 'lt', 'ltg', 'lv', 'mai', 'mk', 'ml', 'mr', 'ms', 'my', 'nb-NO', 'ne-NP', 'nl', 'nn-NO', 'oc', 'or', 'pa-IN', 'pl', 'pt-BR', 'pt-PT', 'rm', 'ro', 'ru', 'si', 'sk', 'sl', 'sq', 'son', 'sr', 'sv-SE', 'ta', 'te', 'th', 'tl', 'tr', 'trs', 'uk', 'ur', 'uz', 'vi', 'wo', 'xh', 'zh-CN', 'zh-TW']
LATEST_FIREFOX_OLDER_VERSION = "3.6.28"
CURRENT_ESR = "60"
ESR_NEXT = ""
JSON_FORMAT_VERSION = "1.0"
JSON_FORMAT_L10N_VERSION = "1.0"
IOS_BETA_VERSION = ""
IOS_VERSION = "12.1"

# The keyword used in the ship-it db for old release before the changeset/json l10n files
LEGACY_KEYWORD = "legacy"
BETA_AGGREGATION_KEYWORD = "beta"

# TODO: remove when we start publishing Devedition
SUPPORTED_AURORA_LOCALES = ['ach', 'af', 'an', 'ar', 'as', 'ast', 'az', 'be', 'bg', 'bn-BD', 'bn-IN', 'br', 'bs', 'ca', 'cak', 'cs', 'cy', 'da', 'de', 'dsb', 'el', 'en-GB', 'en-US', 'en-ZA', 'eo', 'es-AR', 'es-CL', 'es-ES', 'es-MX', 'et', 'eu', 'fa', 'ff', 'fi', 'fr', 'fy-NL', 'ga-IE', 'gd', 'gl', 'gn', 'gu-IN', 'he', 'hi-IN', 'hr', 'hsb', 'hu', 'hy-AM', 'id', 'is', 'it', 'ja', 'ja-JP-mac', 'ka', 'kab', 'kk', 'km', 'kn', 'ko', 'lij', 'lt', 'ltg', 'lv', 'mai', 'mk', 'ml', 'mr', 'ms', 'my', 'nb-NO', 'ne-NP', 'nl', 'nn-NO', 'or', 'pa-IN', 'pl', 'pt-BR', 'pt-PT', 'rm', 'ro', 'ru', 'si', 'sk', 'sl', 'sq', 'son', 'sr', 'sv-SE', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'uz', 'vi', 'xh', 'zh-CN', 'zh-TW']
AURORA_VERSION = "54.0a2"
