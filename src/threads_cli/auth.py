"""Authentication module for Threads API."""

import json
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    def __init__(self, *args, callback_data: dict = None, **kwargs):
        self.callback_data = callback_data or {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            query = parse_qs(parsed.query)
            self.callback_data.update(query)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
<!DOCTYPE html>
<html>
<head><title>Authentication Complete</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 50px;">
    <h1 style="color: #0095f6;">Authentication Complete!</h1>
    <p>You can close this window now.</p>
    <script>setTimeout(function() { window.close(); }, 3000);</script>
</body>
</html>
""")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default logging


class AuthServer:
    """Local OAuth server for Threads API authentication."""

    def __init__(self, port: int = 8080):
        self.port = port
        self.callback_data = {}

    def start(self, auth_url: str, timeout: int = 300) -> dict:
        """Start the auth server and wait for callback."""
        server = HTTPServer(("localhost", self.port), lambda *args: CallbackHandler(*args, callback_data=self.callback_data))

        print(f"Opening browser to: {auth_url}")
        webbrowser.open(auth_url)

        print(f"Waiting for callback on port {self.port}...")

        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            server.handle_request()
            if self.callback_data:
                break

        server.server_close()
        return self.callback_data


def generate_auth_url(app_id: str, redirect_uri: str, scope: str = "threads_basic,threads_content_publish") -> str:
    """Generate the OAuth authorization URL."""
    return (
        f"https://threads.net/oauth/authorize"
        f"?client_id={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&response_type=code"
    )


def exchange_code_for_short_lived_token(app_id: str, app_secret: str, redirect_uri: str, code: str) -> str:
    """Exchange authorization code for short-lived access token.

    Returns:
        Short-lived access token
    """
    import requests

    url = "https://graph.threads.net/oauth/access_token"
    data = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    result = response.json()

    return result.get("access_token")


def exchange_for_long_lived_token(app_id: str, app_secret: str, short_lived_token: str) -> Tuple[str, Optional[str]]:
    """Exchange short-lived token for long-lived token.

    Long-lived tokens are valid for ~60 days.

    Returns:
        Tuple of (long_lived_access_token, refresh_token or None)
    """
    import requests

    url = "https://graph.threads.net/access_token"
    params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "th_exchange_token",
        "access_token": short_lived_token,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()

    return result.get("access_token"), result.get("refresh_token")


def get_user_id(access_token: str) -> str:
    """Get the user ID for the given access token."""
    import requests

    url = "https://graph.threads.net/v1.0/me"
    params = {
        "access_token": access_token,
        "fields": "id",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()

    return result.get("id")


def update_env_file(env_file: str, updates: dict) -> None:
    """Update the .env file with new values."""
    existing = {}

    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing[key.strip()] = value.strip().strip('"').strip("'")

    existing.update(updates)

    with open(env_file, "w") as f:
        f.write("# Threads API Configuration\n")
        f.write("# Get your credentials from https://developers.facebook.com/apps/\n\n")
        for key, value in existing.items():
            f.write(f'{key}="{value}"\n')

    print(f"Updated {env_file}")


def run_auth_local(env_file: str, port: int = 8080) -> dict:
    """Run local OAuth flow and save long-lived token to env file.

    This performs:
    1. OAuth authorization flow
    2. Exchange code for short-lived token
    3. Exchange short-lived for long-lived token (~60 day expiry)
    4. Fetch user ID

    Args:
        env_file: Path to the .env file
        port: Port for the callback server

    Returns:
        Token data from the exchange
    """
    from dotenv import load_dotenv

    load_dotenv(env_file)

    app_id = os.getenv("THREADS_APP_ID")
    app_secret = os.getenv("THREADS_APP_SECRET")
    redirect_uri = os.getenv("THREADS_REDIRECT_URI") or f"http://localhost:{port}/callback"
    scopes = os.getenv("THREADS_SCOPES") or "threads_basic,threads_content_publish"

    if not app_id or not app_secret:
        raise ValueError("THREADS_APP_ID and THREADS_APP_SECRET must be set in the .env file")

    auth_url = generate_auth_url(app_id, redirect_uri, scopes)

    server = AuthServer(port)
    callback_data = server.start(auth_url)

    if "error" in callback_data:
        raise ValueError(f"Auth error: {callback_data.get('error_description', callback_data['error'])}")

    code = callback_data.get("code", [None])[0]
    if not code:
        raise ValueError("No authorization code received")

    # Step 1: Exchange code for short-lived token
    print("Exchanging code for short-lived token...")
    short_lived_token = exchange_code_for_short_lived_token(app_id, app_secret, redirect_uri, code)

    # Step 2: Exchange for long-lived token
    print("Exchanging for long-lived token...")
    long_lived_token, refresh_token = exchange_for_long_lived_token(app_id, app_secret, short_lived_token)

    # Step 3: Get user ID
    print("Fetching user ID...")
    user_id = get_user_id(long_lived_token)

    updates = {
        "THREADS_ACCESS_TOKEN": long_lived_token,
        "THREADS_USER_ID": user_id,
    }
    if refresh_token:
        updates["THREADS_REFRESH_TOKEN"] = refresh_token

    update_env_file(env_file, updates)

    return {
        "access_token": long_lived_token,
        "refresh_token": refresh_token,
        "user_id": user_id,
    }