"""Web-based OAuth2 flow for the Streamlit dashboard.

Uses st.query_params to capture the OAuth authorization code after
the redirect. All configuration loaded from config.py / .env.
"""

from __future__ import annotations

from urllib.parse import urlencode

import httpx
import streamlit as st

from config import (
    OURA_AUTHORIZE_URL,
    OURA_CLIENT_ID,
    OURA_CLIENT_SECRET,
    OURA_REDIRECT_URI,
    OURA_TOKEN_URL,
)

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


def get_auth_url(scopes: list[str] | None = None) -> str:
    params = {
        "client_id": OURA_CLIENT_ID,
        "redirect_uri": OURA_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(scopes or ALL_SCOPES),
    }
    return f"{OURA_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(code: str) -> dict:
    """Exchange an authorization code for access + refresh tokens."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": OURA_CLIENT_ID,
        "client_secret": OURA_CLIENT_SECRET,
        "redirect_uri": OURA_REDIRECT_URI,
    }
    resp = httpx.post(OURA_TOKEN_URL, data=data)
    resp.raise_for_status()
    return resp.json()


def refresh_token(refresh_tok: str) -> dict:
    """Use a refresh token to obtain a new access token."""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok,
        "client_id": OURA_CLIENT_ID,
        "client_secret": OURA_CLIENT_SECRET,
    }
    resp = httpx.post(OURA_TOKEN_URL, data=data)
    resp.raise_for_status()
    return resp.json()


def handle_callback() -> bool:
    """Check query params for an OAuth code and exchange it.

    Returns True if authentication was completed this call.
    """
    params = st.query_params
    code = params.get("code")
    if not code:
        return False

    try:
        tokens = exchange_code(code)
        st.session_state["access_token"] = tokens["access_token"]
        st.session_state["refresh_token"] = tokens.get("refresh_token", "")
        st.query_params.clear()
        return True
    except Exception as exc:
        st.error(f"Authentication failed: {exc}")
        st.query_params.clear()
        return False


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def get_access_token() -> str:
    return st.session_state.get("access_token", "")


def logout():
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("sandbox_mode", None)


def show_login_page():
    """Render a centered login screen with a Connect button."""
    st.markdown(
        "<h1 style='text-align:center; margin-top:2rem;'>Oura Health Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#888;'>Connect your Oura Ring to explore your health data</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        if OURA_CLIENT_ID:
            auth_url = get_auth_url()
            st.link_button(
                "Connect to Oura",
                auth_url,
                use_container_width=True,
                type="primary",
            )
        else:
            st.warning(
                "Set OURA_CLIENT_ID, OURA_CLIENT_SECRET, and OURA_REDIRECT_URI "
                "in your .env file or environment variables."
            )

        st.markdown("---")
        st.markdown("**Or explore with demo data:**")
        if st.button("Use Sandbox Mode", use_container_width=True):
            st.session_state["sandbox_mode"] = True
            st.session_state["access_token"] = "__sandbox__"
            st.rerun()
