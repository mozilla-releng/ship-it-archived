# Process for l10n
## Adding a new locale to Aurora builds

1. Add the new locale code to `SUPPORTED_AURORA_LOCALES` in `kickoff/config.py`.

2. Make sure that the language name (both English and localized) is available in `kickoff/static/languages.json`.

3. Run `scripts/sync-and-check-l10n.py` to download `regionNames.properties` for this new locale.
