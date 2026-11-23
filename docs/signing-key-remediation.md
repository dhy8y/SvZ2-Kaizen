# Signing-key exposure remediation

A private Android signing keystore was found tracked in the repository root on the feature branch. The filename itself advertised that a password was associated with the file. The binary keystore was not downloaded, inspected, copied, or included in this work.

## Actions taken on this feature branch
- Deleted the tracked keystore from `chatgpt/unity-2022-migration`.
- Added ignore rules for Android signing-key files and local signing configuration.
- The pull request will carry the removal to the default branch if merged.

## Required owner action
Assume the key may be compromised. If it is or was used to sign a distributable app, determine the signing identity and rotate/revoke it where possible; do not reuse it. If a Play App Signing account is involved, follow Google's supported key-upgrade/rotation procedure. Replace local/CI signing credentials with a newly generated key stored outside the repository and in an appropriately protected secret store. Never send the key, passwords, or exported license file in chat.

## Git history
Deleting a file in the current branch does not erase earlier copies from Git history, nor does it remove the file from the default branch until the change is merged. History rewriting and force-pushing are intentionally not performed automatically because they can disrupt contributors. The repository owner should coordinate history cleanup if desired, and treat the old key as compromised regardless.
