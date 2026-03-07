"""Typed Oura API V2 client with pagination, rate-limit handling, and sandbox mode."""

from __future__ import annotations

import time
from datetime import date, datetime
from typing import TypeVar

import httpx
from pydantic import BaseModel

from oura_client.auth import OuraAuth
from oura_client.models import (
    DailyActivity,
    DailyActivityResponse,
    DailyCardiovascularAge,
    DailyCardiovascularAgeResponse,
    DailyReadiness,
    DailyReadinessResponse,
    DailyResilience,
    DailyResilienceResponse,
    DailySleep,
    DailySleepResponse,
    DailySpO2,
    DailySpO2Response,
    DailyStress,
    DailyStressResponse,
    EnhancedTag,
    EnhancedTagResponse,
    HeartRate,
    HeartRateResponse,
    PaginatedResponse,
    PersonalInfo,
    RestModePeriod,
    RestModePeriodResponse,
    RingConfiguration,
    RingConfigurationResponse,
    Session,
    SessionResponse,
    Sleep,
    SleepResponse,
    SleepTime,
    SleepTimeResponse,
    Tag,
    TagResponse,
    VO2Max,
    VO2MaxResponse,
    WebhookSubscription,
    Workout,
    WorkoutResponse,
)

BASE_URL = "https://api.ouraring.com"
T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=PaginatedResponse)

_DATE_FMT = "%Y-%m-%d"


def _fmt_date(d: str | date | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d.strftime(_DATE_FMT)
    return d


def _fmt_datetime(d: str | datetime | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.isoformat()
    return d


class OuraClient:
    """High-level client for the Oura API V2.

    Args:
        auth: An OuraAuth instance (or one is created from env).
        sandbox: If True, route data requests through /v2/sandbox/... endpoints.
        auto_refresh: Automatically refresh the token on 401 responses.
        max_retries: Number of retries on rate-limit (429) responses.
    """

    def __init__(
        self,
        auth: OuraAuth | None = None,
        sandbox: bool = False,
        auto_refresh: bool = True,
        max_retries: int = 3,
    ):
        self._auth = auth or OuraAuth()
        self._sandbox = sandbox
        self._auto_refresh = auto_refresh
        self._max_retries = max_retries
        self._http = httpx.Client(base_url=BASE_URL, timeout=30.0)

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # --- internal helpers ---

    def _path(self, endpoint: str) -> str:
        if self._sandbox:
            return f"/v2/sandbox/usercollection/{endpoint}"
        return f"/v2/usercollection/{endpoint}"

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        for attempt in range(self._max_retries + 1):
            resp = self._http.request(method, path, headers=self._auth.headers(), **kwargs)

            if resp.status_code == 401 and self._auto_refresh and attempt == 0:
                self._auth.refresh()
                continue

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                if attempt < self._max_retries:
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()

            resp.raise_for_status()
            return resp

        raise RuntimeError("Exhausted retries")

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        return self._request("GET", path, params=clean)

    def _get_paginated(
        self,
        endpoint: str,
        response_cls: type[R],
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        start_datetime: str | datetime | None = None,
        end_datetime: str | datetime | None = None,
        next_token: str | None = None,
    ) -> R:
        """Fetch a single page from a paginated endpoint."""
        params: dict = {}
        if start_date is not None:
            params["start_date"] = _fmt_date(start_date)
        if end_date is not None:
            params["end_date"] = _fmt_date(end_date)
        if start_datetime is not None:
            params["start_datetime"] = _fmt_datetime(start_datetime)
        if end_datetime is not None:
            params["end_datetime"] = _fmt_datetime(end_datetime)
        if next_token is not None:
            params["next_token"] = next_token

        resp = self._get(self._path(endpoint), params)
        return response_cls.model_validate(resp.json())

    def _get_all_pages(
        self,
        endpoint: str,
        response_cls: type[R],
        **kwargs,
    ) -> list:
        """Auto-paginate through all pages and return the combined data list."""
        all_data: list = []
        token: str | None = None
        while True:
            page = self._get_paginated(endpoint, response_cls, next_token=token, **kwargs)
            all_data.extend(page.data)
            token = page.next_token
            if not token:
                break
        return all_data

    # --- Public data endpoints ---

    def get_personal_info(self) -> PersonalInfo:
        path = "/v2/usercollection/personal_info"
        resp = self._get(path)
        return PersonalInfo.model_validate(resp.json())

    def get_sleep(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[Sleep]:
        return self._get_all_pages("sleep", SleepResponse, start_date=start_date, end_date=end_date)

    def get_sleep_page(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        next_token: str | None = None,
    ) -> SleepResponse:
        return self._get_paginated("sleep", SleepResponse, start_date=start_date, end_date=end_date, next_token=next_token)

    def get_daily_sleep(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailySleep]:
        return self._get_all_pages("daily_sleep", DailySleepResponse, start_date=start_date, end_date=end_date)

    def get_daily_activity(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailyActivity]:
        return self._get_all_pages("daily_activity", DailyActivityResponse, start_date=start_date, end_date=end_date)

    def get_daily_readiness(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailyReadiness]:
        return self._get_all_pages("daily_readiness", DailyReadinessResponse, start_date=start_date, end_date=end_date)

    def get_daily_stress(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailyStress]:
        return self._get_all_pages("daily_stress", DailyStressResponse, start_date=start_date, end_date=end_date)

    def get_daily_resilience(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailyResilience]:
        return self._get_all_pages("daily_resilience", DailyResilienceResponse, start_date=start_date, end_date=end_date)

    def get_daily_spo2(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailySpO2]:
        return self._get_all_pages("daily_spo2", DailySpO2Response, start_date=start_date, end_date=end_date)

    def get_daily_cardiovascular_age(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[DailyCardiovascularAge]:
        return self._get_all_pages("daily_cardiovascular_age", DailyCardiovascularAgeResponse, start_date=start_date, end_date=end_date)

    def get_heart_rate(
        self,
        start_datetime: str | datetime | None = None,
        end_datetime: str | datetime | None = None,
    ) -> list[HeartRate]:
        return self._get_all_pages("heartrate", HeartRateResponse, start_datetime=start_datetime, end_datetime=end_datetime)

    def get_vo2_max(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[VO2Max]:
        return self._get_all_pages("vO2_max", VO2MaxResponse, start_date=start_date, end_date=end_date)

    def get_workouts(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[Workout]:
        return self._get_all_pages("workout", WorkoutResponse, start_date=start_date, end_date=end_date)

    def get_sessions(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[Session]:
        return self._get_all_pages("session", SessionResponse, start_date=start_date, end_date=end_date)

    def get_tags(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[Tag]:
        return self._get_all_pages("tag", TagResponse, start_date=start_date, end_date=end_date)

    def get_enhanced_tags(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[EnhancedTag]:
        return self._get_all_pages("enhanced_tag", EnhancedTagResponse, start_date=start_date, end_date=end_date)

    def get_sleep_time(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[SleepTime]:
        return self._get_all_pages("sleep_time", SleepTimeResponse, start_date=start_date, end_date=end_date)

    def get_rest_mode_periods(
        self,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> list[RestModePeriod]:
        return self._get_all_pages("rest_mode_period", RestModePeriodResponse, start_date=start_date, end_date=end_date)

    def get_ring_configurations(self) -> list[RingConfiguration]:
        return self._get_all_pages("ring_configuration", RingConfigurationResponse)

    # --- Webhook endpoints (not sandboxed, use client auth) ---

    def list_webhooks(self) -> list[WebhookSubscription]:
        resp = self._get("/v2/webhook/subscription")
        items = resp.json()
        if isinstance(items, list):
            return [WebhookSubscription.model_validate(i) for i in items]
        return [WebhookSubscription.model_validate(i) for i in items.get("data", items)]

    def create_webhook(
        self,
        callback_url: str,
        verification_token: str,
        event_type: str,
        data_type: str,
    ) -> WebhookSubscription:
        resp = self._request(
            "POST",
            "/v2/webhook/subscription",
            json={
                "callback_url": callback_url,
                "verification_token": verification_token,
                "event_type": event_type,
                "data_type": data_type,
            },
        )
        return WebhookSubscription.model_validate(resp.json())

    def delete_webhook(self, webhook_id: str) -> None:
        self._request("DELETE", f"/v2/webhook/subscription/{webhook_id}")
