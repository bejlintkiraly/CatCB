# Security and responsible disclosure

Please do not open public issues containing passwords, access tokens, company recipient lists, internal incident information, or screenshots of private systems.

If a secret is accidentally committed, remove it from the working tree immediately and rotate/revoke it. Deleting it from the latest commit is not sufficient if it remains in Git history. Follow GitHub's documentation for removing sensitive data from a repository.

CatCB is a personal project. Use only approved accounts, systems, and data. Do not use it to bypass company endpoint controls or mail permissions.

The local update feature should only be used with update packages obtained from a trusted source. SHA-256 detects mismatched/corrupt files, but is not publisher authentication by itself. For wider distribution, use a trusted release location and consider organization-approved code signing.
