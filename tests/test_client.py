"""Tests for the Oura API client using mocked HTTP responses.

These tests validate that the client correctly parses responses from
the Oura API (mirroring the sandbox endpoint response shapes).
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from oura_client.auth import OuraAuth
from oura_client.client import OuraClient
from oura_client.models import (
    DailyActivity,
    DailyReadiness,
    DailyResilience,
    DailyStress,
    HeartRate,
    PersonalInfo,
    RingConfiguration,
    Sleep,
    VO2Max,
    Workout,
)


@pytest.fixture()
def auth():
    return OuraAuth(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token",
    )


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    resp.headers = {}
    return resp


class TestModels:
    def test_personal_info_parsing(self):
        data = {"id": "abc123", "age": 32, "weight": 75.5, "height": 180.0, "biological_sex": "male", "email": "test@example.com"}
        info = PersonalInfo.model_validate(data)
        assert info.age == 32
        assert info.email == "test@example.com"

    def test_personal_info_optional_fields(self):
        data = {"id": "abc123"}
        info = PersonalInfo.model_validate(data)
        assert info.age is None
        assert info.email is None

    def test_sleep_model_parsing(self):
        data = {
            "id": "sleep1",
            "average_breath": 15.2,
            "average_heart_rate": 58.0,
            "average_hrv": 42,
            "awake_time": 3600,
            "bedtime_end": "2025-01-02T07:00:00+00:00",
            "bedtime_start": "2025-01-01T23:00:00+00:00",
            "day": "2025-01-02",
            "deep_sleep_duration": 5400,
            "efficiency": 88,
            "heart_rate": None,
            "hrv": None,
            "latency": 600,
            "light_sleep_duration": 14400,
            "low_battery_alert": False,
            "lowest_heart_rate": 48,
            "movement_30_sec": "11122211",
            "period": 0,
            "readiness": None,
            "readiness_score_delta": 5,
            "rem_sleep_duration": 7200,
            "restless_periods": 3,
            "sleep_phase_5_min": "44123321",
            "sleep_score_delta": 10,
            "sleep_algorithm_version": "v2",
            "time_in_bed": 28800,
            "total_sleep_duration": 27000,
            "type": "long_sleep",
        }
        s = Sleep.model_validate(data)
        assert s.day == date(2025, 1, 2)
        assert s.deep_sleep_hours == pytest.approx(1.5)
        assert s.rem_sleep_hours == pytest.approx(2.0)
        assert s.total_sleep_hours == pytest.approx(7.5)
        assert s.sleep_phases_list() == [4, 4, 1, 2, 3, 3, 2, 1]

    def test_daily_activity_parsing(self):
        data = {
            "id": "act1",
            "class_5_min": "01234",
            "score": 82,
            "active_calories": 450,
            "average_met_minutes": 1.8,
            "contributors": {"meet_daily_targets": 90, "move_every_hour": 85},
            "equivalent_walking_distance": 8000,
            "high_activity_met_minutes": 120,
            "high_activity_time": 1800,
            "inactivity_alerts": 2,
            "low_activity_met_minutes": 200,
            "low_activity_time": 7200,
            "medium_activity_met_minutes": 150,
            "medium_activity_time": 3600,
            "met": None,
            "meters_to_target": 500,
            "non_wear_time": 3600,
            "resting_time": 28800,
            "sedentary_met_minutes": 300,
            "sedentary_time": 36000,
            "steps": 9500,
            "target_calories": 500,
            "target_meters": 8500,
            "total_calories": 2200,
            "day": "2025-01-15",
            "timestamp": "2025-01-15T04:00:00+00:00",
        }
        a = DailyActivity.model_validate(data)
        assert a.steps == 9500
        assert a.high_activity_minutes == pytest.approx(30.0)
        assert a.sedentary_hours == pytest.approx(10.0)

    def test_daily_readiness_parsing(self):
        data = {
            "id": "r1",
            "contributors": {
                "activity_balance": 80,
                "body_temperature": 90,
                "hrv_balance": 75,
                "previous_day_activity": 85,
                "previous_night": 70,
                "recovery_index": 88,
                "resting_heart_rate": 92,
                "sleep_balance": 78,
                "sleep_regularity": 82,
            },
            "day": "2025-01-15",
            "score": 85,
            "temperature_deviation": 0.2,
            "temperature_trend_deviation": -0.1,
            "timestamp": "2025-01-15T04:00:00+00:00",
        }
        r = DailyReadiness.model_validate(data)
        assert r.score == 85
        assert r.contributors.hrv_balance == 75

    def test_daily_stress_parsing(self):
        data = {
            "id": "s1",
            "day": "2025-01-15",
            "stress_high": 3600,
            "recovery_high": 7200,
            "day_summary": "normal",
        }
        s = DailyStress.model_validate(data)
        assert s.stress_high_minutes == pytest.approx(60.0)
        assert s.recovery_high_minutes == pytest.approx(120.0)
        assert s.day_summary.value == "normal"

    def test_heart_rate_parsing(self):
        data = {"bpm": 72, "source": "awake", "timestamp": "2025-01-15T10:00:00+00:00"}
        h = HeartRate.model_validate(data)
        assert h.bpm == 72
        assert h.source.value == "awake"

    def test_workout_parsing(self):
        data = {
            "id": "w1",
            "activity": "running",
            "calories": 350.0,
            "day": "2025-01-15",
            "distance": 5000.0,
            "end_datetime": "2025-01-15T08:30:00+00:00",
            "intensity": "moderate",
            "label": "Morning run",
            "source": "autodetected",
            "start_datetime": "2025-01-15T08:00:00+00:00",
        }
        w = Workout.model_validate(data)
        assert w.activity == "running"
        assert w.duration_minutes == pytest.approx(30.0)

    def test_daily_resilience_parsing(self):
        data = {
            "id": "res1",
            "day": "2025-01-15",
            "contributors": {"sleep_recovery": 80.0, "daytime_recovery": 70.0, "stress": 60.0},
            "level": "solid",
        }
        r = DailyResilience.model_validate(data)
        assert r.level.value == "solid"
        assert r.contributors.sleep_recovery == 80.0

    def test_vo2_max_parsing(self):
        data = {"id": "v1", "day": "2025-01-15", "timestamp": "2025-01-15T04:00:00+00:00", "vo2_max": 42.5}
        v = VO2Max.model_validate(data)
        assert v.vo2_max == pytest.approx(42.5)

    def test_ring_configuration_parsing(self):
        data = {
            "id": "ring1",
            "color": "titanium",
            "design": "heritage",
            "firmware_version": "3.0.1",
            "hardware_type": "gen3",
            "set_up_at": "2024-06-01T00:00:00+00:00",
            "size": 9,
        }
        r = RingConfiguration.model_validate(data)
        assert r.hardware_type.value == "gen3"
        assert r.size == 9


class TestClient:
    def test_sandbox_path(self, auth):
        client = OuraClient(auth=auth, sandbox=True)
        assert client._path("sleep") == "/v2/sandbox/usercollection/sleep"

    def test_production_path(self, auth):
        client = OuraClient(auth=auth, sandbox=False)
        assert client._path("sleep") == "/v2/usercollection/sleep"

    @patch("oura_client.client.httpx.Client")
    def test_get_sleep_parses_response(self, mock_http_cls, auth):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http
        mock_http.request.return_value = _mock_response({
            "data": [
                {
                    "id": "s1",
                    "average_breath": 14.0,
                    "average_heart_rate": 55.0,
                    "average_hrv": 50,
                    "awake_time": 1800,
                    "bedtime_end": "2025-01-02T07:00:00+00:00",
                    "bedtime_start": "2025-01-01T23:00:00+00:00",
                    "day": "2025-01-02",
                    "deep_sleep_duration": 3600,
                    "efficiency": 92,
                    "heart_rate": None,
                    "hrv": None,
                    "latency": 300,
                    "light_sleep_duration": 10800,
                    "low_battery_alert": False,
                    "lowest_heart_rate": 45,
                    "movement_30_sec": None,
                    "period": 0,
                    "readiness": None,
                    "readiness_score_delta": None,
                    "rem_sleep_duration": 5400,
                    "restless_periods": 2,
                    "sleep_phase_5_min": None,
                    "sleep_score_delta": None,
                    "sleep_algorithm_version": "v2",
                    "time_in_bed": 28800,
                    "total_sleep_duration": 21600,
                    "type": "long_sleep",
                }
            ],
            "next_token": None,
        })

        client = OuraClient(auth=auth, sandbox=True)
        client._http = mock_http
        result = client.get_sleep(start_date="2025-01-01", end_date="2025-01-07")

        assert len(result) == 1
        assert isinstance(result[0], Sleep)
        assert result[0].efficiency == 92

    @patch("oura_client.client.httpx.Client")
    def test_pagination(self, mock_http_cls, auth):
        mock_http = MagicMock()
        mock_http_cls.return_value = mock_http

        base_sleep = {
            "average_breath": None, "average_heart_rate": None, "average_hrv": None,
            "awake_time": None, "bedtime_end": "2025-01-02T07:00:00", "bedtime_start": "2025-01-01T23:00:00",
            "day": "2025-01-02", "deep_sleep_duration": None, "efficiency": None,
            "heart_rate": None, "hrv": None, "latency": None, "light_sleep_duration": None,
            "low_battery_alert": False, "lowest_heart_rate": None, "movement_30_sec": None,
            "period": 0, "readiness": None, "readiness_score_delta": None,
            "rem_sleep_duration": None, "restless_periods": None, "sleep_phase_5_min": None,
            "sleep_score_delta": None, "sleep_algorithm_version": None,
            "time_in_bed": 28800, "total_sleep_duration": None, "type": "long_sleep",
        }

        page1 = _mock_response({
            "data": [{**base_sleep, "id": "s1"}],
            "next_token": "page2_token",
        })
        page2 = _mock_response({
            "data": [{**base_sleep, "id": "s2"}],
            "next_token": None,
        })
        mock_http.request.side_effect = [page1, page2]

        client = OuraClient(auth=auth, sandbox=True)
        client._http = mock_http
        result = client.get_sleep()

        assert len(result) == 2
        assert result[0].id == "s1"
        assert result[1].id == "s2"

    def test_auth_headers(self, auth):
        assert auth.headers() == {"Authorization": "Bearer test_token"}

    def test_authorization_url(self, auth):
        url = auth.get_authorization_url(scopes=["daily", "heartrate"])
        assert "cloud.ouraring.com/oauth/authorize" in url
        assert "daily" in url
        assert "heartrate" in url

    def test_context_manager(self, auth):
        with OuraClient(auth=auth) as client:
            assert client._sandbox is False
