"""Utilities for working with Oura sandbox endpoints.

Sandbox endpoints return mock data and don't require a real Oura ring.
They share the same rate limit as production endpoints (5000 req / 5 min).
"""

from __future__ import annotations

from oura_client.auth import OuraAuth
from oura_client.client import OuraClient

SANDBOX_DATA_TYPES = [
    "tag",
    "enhanced_tag",
    "workout",
    "session",
    "daily_activity",
    "daily_sleep",
    "daily_spo2",
    "daily_readiness",
    "sleep",
    "sleep_time",
    "rest_mode_period",
    "ring_configuration",
    "daily_stress",
    "daily_resilience",
    "daily_cardiovascular_age",
    "vO2_max",
    "heartrate",
]


def create_sandbox_client(auth: OuraAuth | None = None) -> OuraClient:
    """Create an OuraClient pre-configured for sandbox mode."""
    return OuraClient(auth=auth, sandbox=True)


def fetch_all_sandbox_data(client: OuraClient | None = None) -> dict:
    """Fetch one page of every sandbox data type. Useful for exploring the API schema.

    Returns a dict mapping data type names to their parsed response lists.
    """
    if client is None:
        client = create_sandbox_client()

    results: dict = {}
    results["sleep"] = client.get_sleep()
    results["daily_sleep"] = client.get_daily_sleep()
    results["daily_activity"] = client.get_daily_activity()
    results["daily_readiness"] = client.get_daily_readiness()
    results["daily_stress"] = client.get_daily_stress()
    results["daily_resilience"] = client.get_daily_resilience()
    results["daily_spo2"] = client.get_daily_spo2()
    results["daily_cardiovascular_age"] = client.get_daily_cardiovascular_age()
    results["heart_rate"] = client.get_heart_rate()
    results["vo2_max"] = client.get_vo2_max()
    results["workouts"] = client.get_workouts()
    results["sessions"] = client.get_sessions()
    results["tags"] = client.get_tags()
    results["enhanced_tags"] = client.get_enhanced_tags()
    results["sleep_time"] = client.get_sleep_time()
    results["rest_mode_periods"] = client.get_rest_mode_periods()
    results["ring_configurations"] = client.get_ring_configurations()
    return results
