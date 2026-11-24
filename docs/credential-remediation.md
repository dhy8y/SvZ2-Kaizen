# Embedded service credential remediation

A source/data audit found credential-like values in the tracked Unity DataBundle configuration (`DataBundles/English/ConfigSchema.txt`). They are embedded in a public repository and would also be shipped to clients if included in a build. Their validity and service permissions have not been tested.

## Affected integration families (values intentionally omitted)
- Advertising/monetization integration secrets and tokens
- GameSpy platform access/secret keys for test, iOS and Android
- Push-notification service secrets
- Advertising attribution/signature values

No credential values were copied into this document, a commit, or a chat message.

## Required owner action
1. Treat secret-like values as exposed. Rotate/revoke them in each provider console if still valid, and review logs/access for unexpected use.
2. Determine which integrations are still used by Kaizen. Removing entries blindly can break initialization, analytics, purchases, matchmaking, notifications or account flows.
3. Do not ship server-side secrets in a Unity mobile client. Replace client-facing integration settings with provider-supported public identifiers; move privileged operations behind a server you control.
4. Remove obsolete values from tracked DataBundles and update the application configuration after rotation. Review old Git history and coordinate history cleanup if needed; changing the current file alone does not purge earlier commits.
5. Keep new secrets out of Git and chat. Use protected CI secrets only for build-time operations that truly need them; do not bake server secrets into the APK.

This PR does not rotate or delete these service credentials. The owner must do that because the repository does not grant access to provider consoles, and indiscriminate deletion could break game features.
