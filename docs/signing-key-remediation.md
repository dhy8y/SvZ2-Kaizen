# Android signing key remediation

A tracked Android signing keystore was found in the repository root. Its filename indicated that a password was associated with the key. The binary was not downloaded or inspected.

## Change in this pull request
- Remove the tracked keystore from the default branch.
- Ignore local Android signing files and key configuration so they are not re-added.

## Required owner action
Treat the key as compromised. If it was used to sign a published app, rotate/revoke it where possible. For Google Play App Signing, follow the supported key-upgrade process. Generate a new key locally and store it outside Git, with CI access limited to protected secrets. Never paste key material, passwords, or Unity license contents into chat.

## History
This removes the file from the current branch only; older Git history still contains it. History rewriting is not included because it can disrupt collaborators. Consider coordinated history cleanup, but rotate the key regardless.
