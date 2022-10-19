# Validator

## Write-up

1. "Invalid message" errors passed to `schema.Schema()` support Python string formatting.

2. We use that to access the secret key from the app, using a payload such as `{.__getattr__.__func__.__globals__[app].secret_key}`.

3. With the secret key, we forge a session that sets `isAdmin` to `true` to get the flag.

4. [Commented exploit script](./solve.py).
