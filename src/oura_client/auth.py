"""OAuth2 authentication flow for the Oura API."""

from __future__ import annotations

import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from dotenv import load_dotenv, set_key

AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
TOKEN_URL = "https://api.ouraring.com/oauth/token"

ALL_SCOPES = [
    "email",
    "personal",
    "daily",
    "heartrate",
    "workout",
    "tag",
    "session",
    "spo2Daily",
]


class OuraAuth:
    """Handles OAuth2 authorization code flow for the Oura API.

    Reads credentials from environment variables (or .env file):
      - OURA_CLIENT_ID
      - OURA_CLIENT_SECRET
      - OURA_REDIRECT_URI  (default: http://localhost:8080/callback)
      - OURA_ACCESS_TOKEN   (populated after auth)
      - OURA_REFRESH_TOKEN  (populated after auth)
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        env_file: str | Path = ".env",
    ):
        load_dotenv(env_file)
        self._env_file = str(env_file)
        self.client_id = client_id or os.getenv("OURA_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("OURA_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.getenv(
            "OURA_REDIRECT_URI", "http://localhost:8080/callback"
        )
        self.access_token = access_token or os.getenv("OURA_ACCESS_TOKEN", "")
        self.refresh_token = refresh_token or os.getenv("OURA_REFRESH_TOKEN", "")

    @property
    def is_authenticated(self) -> bool:
        return bool(self.access_token)

    def get_authorization_url(self, scopes: list[str] | None = None) -> str:
        """Build the OAuth2 authorization URL the user should visit."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes or ALL_SCOPES),
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> dict:
        """Exchange an authorization code for access + refresh tokens."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        resp = httpx.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        tokens = resp.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token", "")
        self._save_tokens()
        return tokens

    def refresh(self) -> dict:
        """Use the refresh token to obtain a new access token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available. Run authorize() first.")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        resp = httpx.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        tokens = resp.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token", self.refresh_token)
        self._save_tokens()
        return tokens

    def authorize(
        self,
        scopes: list[str] | None = None,
        open_browser: bool = True,
    ) -> dict:
        """Run the full OAuth2 authorization code flow.

        1. Opens the browser to the Oura consent page.
        2. Starts a local HTTP server to capture the redirect with the auth code.
        3. Exchanges the code for tokens and persists them.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "OURA_CLIENT_ID and OURA_CLIENT_SECRET must be set in .env or passed directly."
            )

        url = self.get_authorization_url(scopes)
        parsed = urlparse(self.redirect_uri)
        port = parsed.port or 8080

        auth_code_holder: dict[str, str] = {}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                qs = parse_qs(urlparse(self.path).query)
                if "code" in qs:
                    auth_code_holder["code"] = qs["code"][0]
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h2>Authorization successful!</h2>"
                        b"<p>You can close this window and return to your terminal.</p>"
                        b"</body></html>"
                    )
                elif "error" in qs:
                    auth_code_holder["error"] = qs.get("error_description", qs["error"])[0]
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Authorization failed. Check your terminal.")
                else:
                    self.send_response(400)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # suppress noisy HTTP logs

        server = HTTPServer(("localhost", port), CallbackHandler)
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        print(f"Opening browser for Oura authorization...\n  {url}")
        if open_browser:
            webbrowser.open(url)

        server_thread.join(timeout=300)
        server.server_close()

        if "error" in auth_code_holder:
            raise RuntimeError(f"Authorization failed: {auth_code_holder['error']}")
        if "code" not in auth_code_holder:
            raise TimeoutError("Did not receive authorization code within 5 minutes.")

        return self.exchange_code(auth_code_holder["code"])

    def _save_tokens(self) -> None:
        """Persist tokens to the .env file."""
        env_path = Path(self._env_file)
        if env_path.exists():
            set_key(str(env_path), "OURA_ACCESS_TOKEN", self.access_token)
            set_key(str(env_path), "OURA_REFRESH_TOKEN", self.refresh_token)
        else:
            tokens_path = Path("tokens.json")
            tokens_path.write_text(
                json.dumps(
                    {
                        "access_token": self.access_token,
                        "refresh_token": self.refresh_token,
                    },
                    indent=2,
                )
            )

    def headers(self) -> dict[str, str]:
        """Return Authorization header dict for API requests."""
        return {"Authorization": f"Bearer {self.access_token}"}
