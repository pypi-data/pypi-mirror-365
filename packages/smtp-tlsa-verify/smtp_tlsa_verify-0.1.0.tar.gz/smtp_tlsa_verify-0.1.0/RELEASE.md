# How To Release a New Version

- Change the version number in pyproject.toml
- Change the version number in smtp_tlsa_verify/api.py
- run `uv build`
- run `uv publish`