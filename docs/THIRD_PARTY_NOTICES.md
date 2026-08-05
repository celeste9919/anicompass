# Third-Party Notices

AniCompass uses the following direct runtime dependencies:

- PySide6: Qt for Python bindings. Review Qt/PySide licensing before distributing
  binary releases.
- keyring: operating-system credential storage integration.
- httpx: HTTP client for catalog and AI provider calls.
- Pydantic: data validation and typed models.

Development and packaging tools:

- pytest: automated tests.
- Ruff: linting.
- PyInstaller: Windows executable packaging fallback.

Catalog data is retrieved through Jikan, an unofficial MyAnimeList API. Follow
Jikan and MyAnimeList terms, attribution expectations, and rate-limit guidance
when distributing or operating the app.
