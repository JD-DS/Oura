"""Pydantic models for all Oura API V2 response types."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --- Enums ---


class HeartRateSource(str, Enum):
    AWAKE = "awake"
    REST = "rest"
    SLEEP = "sleep"
    SESSION = "session"
    LIVE = "live"
    WORKOUT = "workout"


class SleepType(str, Enum):
    DELETED = "deleted"
    SLEEP = "sleep"
    LONG_SLEEP = "long_sleep"
    LATE_NAP = "late_nap"
    REST = "rest"


class SleepAlgorithmVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


class SleepAnalysisReason(str, Enum):
    FOREGROUND_SLEEP_ANALYSIS = "foreground_sleep_analysis"
    BEDTIME_EDIT = "bedtime_edit"


class MomentType(str, Enum):
    BREATHING = "breathing"
    MEDITATION = "meditation"
    NAP = "nap"
    RELAXATION = "relaxation"
    REST = "rest"
    BODY_STATUS = "body_status"


class MomentMood(str, Enum):
    BAD = "bad"
    WORSE = "worse"
    SAME = "same"
    GOOD = "good"
    GREAT = "great"


class WorkoutIntensity(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class WorkoutSource(str, Enum):
    MANUAL = "manual"
    AUTODETECTED = "autodetected"
    CONFIRMED = "confirmed"
    WORKOUT_HEART_RATE = "workout_heart_rate"


class DailyStressSummary(str, Enum):
    RESTORED = "restored"
    NORMAL = "normal"
    STRESSFUL = "stressful"


class LongTermResilienceLevel(str, Enum):
    LIMITED = "limited"
    ADEQUATE = "adequate"
    SOLID = "solid"
    STRONG = "strong"
    EXCEPTIONAL = "exceptional"


class SleepTimeRecommendation(str, Enum):
    IMPROVE_EFFICIENCY = "improve_efficiency"
    EARLIER_BEDTIME = "earlier_bedtime"
    LATER_BEDTIME = "later_bedtime"
    EARLIER_WAKE_UP_TIME = "earlier_wake_up_time"
    LATER_WAKE_UP_TIME = "later_wake_up_time"
    FOLLOW_OPTIMAL_BEDTIME = "follow_optimal_bedtime"


class SleepTimeStatus(str, Enum):
    NOT_ENOUGH_NIGHTS = "not_enough_nights"
    NOT_ENOUGH_RECENT_NIGHTS = "not_enough_recent_nights"
    BAD_SLEEP_QUALITY = "bad_sleep_quality"
    ONLY_RECOMMENDED_FOUND = "only_recommended_found"
    OPTIMAL_FOUND = "optimal_found"


class RingColor(str, Enum):
    BRUSHED_SILVER = "brushed_silver"
    GLOSSY_BLACK = "glossy_black"
    GLOSSY_GOLD = "glossy_gold"
    GLOSSY_WHITE = "glossy_white"
    GUCCI = "gucci"
    MATT_GOLD = "matt_gold"
    ROSE = "rose"
    SILVER = "silver"
    STEALTH_BLACK = "stealth_black"
    TITANIUM = "titanium"
    TITANIUM_AND_GOLD = "titanium_and_gold"


class RingDesign(str, Enum):
    BALANCE = "balance"
    BALANCE_DIAMOND = "balance_diamond"
    HERITAGE = "heritage"
    HORIZON = "horizon"


class RingHardwareType(str, Enum):
    GEN1 = "gen1"
    GEN2 = "gen2"
    GEN2M = "gen2m"
    GEN3 = "gen3"
    GEN4 = "gen4"


class WebhookOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class DataType(str, Enum):
    TAG = "tag"
    ENHANCED_TAG = "enhanced_tag"
    WORKOUT = "workout"
    SESSION = "session"
    SLEEP = "sleep"
    DAILY_SLEEP = "daily_sleep"
    DAILY_READINESS = "daily_readiness"
    DAILY_ACTIVITY = "daily_activity"
    DAILY_SPO2 = "daily_spo2"
    SLEEP_TIME = "sleep_time"
    REST_MODE_PERIOD = "rest_mode_period"
    RING_CONFIGURATION = "ring_configuration"
    DAILY_STRESS = "daily_stress"
    DAILY_CARDIOVASCULAR_AGE = "daily_cardiovascular_age"
    DAILY_RESILIENCE = "daily_resilience"
    VO2_MAX = "vo2_max"


# --- Shared sub-models ---


class Sample(BaseModel):
    """Time-series sample data (HR, HRV, MET, motion, etc.)."""

    interval: float = Field(description="Interval in seconds between sampled items")
    items: list[Optional[float]]
    timestamp: str = Field(description="ISO 8601 timestamp when sampling started")


class ActivityContributors(BaseModel):
    meet_daily_targets: Optional[int] = None
    move_every_hour: Optional[int] = None
    recovery_time: Optional[int] = None
    stay_active: Optional[int] = None
    training_frequency: Optional[int] = None
    training_volume: Optional[int] = None


class ReadinessContributors(BaseModel):
    activity_balance: Optional[int] = None
    body_temperature: Optional[int] = None
    hrv_balance: Optional[int] = None
    previous_day_activity: Optional[int] = None
    previous_night: Optional[int] = None
    recovery_index: Optional[int] = None
    resting_heart_rate: Optional[int] = None
    sleep_balance: Optional[int] = None
    sleep_regularity: Optional[int] = None


class SleepContributors(BaseModel):
    deep_sleep: Optional[int] = None
    efficiency: Optional[int] = None
    latency: Optional[int] = None
    rem_sleep: Optional[int] = None
    restfulness: Optional[int] = None
    timing: Optional[int] = None
    total_sleep: Optional[int] = None


class ResilienceContributors(BaseModel):
    sleep_recovery: float
    daytime_recovery: float
    stress: float


class ReadinessSummary(BaseModel):
    contributors: ReadinessContributors
    score: Optional[int] = None
    temperature_deviation: Optional[float] = None
    temperature_trend_deviation: Optional[float] = None


class SpO2AggregatedValues(BaseModel):
    average: float = Field(description="Average SpO2 percentage during sleep")


class SleepTimeWindow(BaseModel):
    day_tz: int = Field(description="Timezone offset from GMT in seconds")
    end_offset: int = Field(description="End offset from midnight in seconds")
    start_offset: int = Field(description="Start offset from midnight in seconds")


class RestModeEpisode(BaseModel):
    tags: list[str]
    timestamp: str


# --- Primary data models ---


class PersonalInfo(BaseModel):
    id: str
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    biological_sex: Optional[str] = None
    email: Optional[str] = None


class Sleep(BaseModel):
    """Detailed sleep period with stages, biometrics, and movement data."""

    id: str
    average_breath: Optional[float] = None
    average_heart_rate: Optional[float] = None
    average_hrv: Optional[int] = None
    awake_time: Optional[int] = None
    bedtime_end: str
    bedtime_start: str
    day: date
    deep_sleep_duration: Optional[int] = None
    efficiency: Optional[int] = None
    heart_rate: Optional[Sample] = None
    hrv: Optional[Sample] = None
    latency: Optional[int] = None
    light_sleep_duration: Optional[int] = None
    low_battery_alert: bool = False
    lowest_heart_rate: Optional[int] = None
    movement_30_sec: Optional[str] = None
    period: int = 0
    readiness: Optional[ReadinessSummary] = None
    readiness_score_delta: Optional[int] = None
    rem_sleep_duration: Optional[int] = None
    restless_periods: Optional[int] = None
    sleep_phase_5_min: Optional[str] = None
    sleep_score_delta: Optional[int] = None
    sleep_algorithm_version: Optional[SleepAlgorithmVersion] = None
    sleep_analysis_reason: Optional[SleepAnalysisReason] = None
    time_in_bed: int = 0
    total_sleep_duration: Optional[int] = None
    type: SleepType = SleepType.LONG_SLEEP

    @property
    def deep_sleep_hours(self) -> Optional[float]:
        return self.deep_sleep_duration / 3600 if self.deep_sleep_duration else None

    @property
    def light_sleep_hours(self) -> Optional[float]:
        return self.light_sleep_duration / 3600 if self.light_sleep_duration else None

    @property
    def rem_sleep_hours(self) -> Optional[float]:
        return self.rem_sleep_duration / 3600 if self.rem_sleep_duration else None

    @property
    def total_sleep_hours(self) -> Optional[float]:
        return self.total_sleep_duration / 3600 if self.total_sleep_duration else None

    @property
    def awake_hours(self) -> Optional[float]:
        return self.awake_time / 3600 if self.awake_time else None

    def sleep_phases_list(self) -> Optional[list[int]]:
        """Parse sleep_phase_5_min string into list of ints (1=deep, 2=light, 3=REM, 4=awake)."""
        if not self.sleep_phase_5_min:
            return None
        return [int(c) for c in self.sleep_phase_5_min]


class DailySleep(BaseModel):
    id: str
    contributors: SleepContributors
    day: date
    score: Optional[int] = None
    timestamp: str = ""


class DailyActivity(BaseModel):
    id: str
    class_5_min: Optional[str] = None
    score: Optional[int] = None
    active_calories: int = 0
    average_met_minutes: float = 0.0
    contributors: ActivityContributors = Field(default_factory=ActivityContributors)
    equivalent_walking_distance: int = 0
    high_activity_met_minutes: int = 0
    high_activity_time: int = 0
    inactivity_alerts: int = 0
    low_activity_met_minutes: int = 0
    low_activity_time: int = 0
    medium_activity_met_minutes: int = 0
    medium_activity_time: int = 0
    met: Optional[Sample] = None
    meters_to_target: int = 0
    non_wear_time: int = 0
    resting_time: int = 0
    sedentary_met_minutes: int = 0
    sedentary_time: int = 0
    steps: int = 0
    target_calories: int = 0
    target_meters: int = 0
    total_calories: int = 0
    day: date = Field(description="Date of the activity record")
    timestamp: str = ""

    @property
    def high_activity_minutes(self) -> float:
        return self.high_activity_time / 60

    @property
    def sedentary_hours(self) -> float:
        return self.sedentary_time / 3600


class DailyReadiness(BaseModel):
    id: str
    contributors: ReadinessContributors
    day: date
    score: Optional[int] = None
    temperature_deviation: Optional[float] = None
    temperature_trend_deviation: Optional[float] = None
    timestamp: str = ""


class DailyStress(BaseModel):
    id: str
    day: date
    stress_high: Optional[int] = None
    recovery_high: Optional[int] = None
    day_summary: Optional[DailyStressSummary] = None

    @property
    def stress_high_minutes(self) -> Optional[float]:
        return self.stress_high / 60 if self.stress_high else None

    @property
    def recovery_high_minutes(self) -> Optional[float]:
        return self.recovery_high / 60 if self.recovery_high else None


class DailyResilience(BaseModel):
    id: str
    day: date
    contributors: ResilienceContributors
    level: LongTermResilienceLevel


class DailySpO2(BaseModel):
    id: str
    day: date
    spo2_percentage: Optional[SpO2AggregatedValues] = None
    breathing_disturbance_index: Optional[int] = None


class DailyCardiovascularAge(BaseModel):
    day: date
    vascular_age: Optional[int] = None


class HeartRate(BaseModel):
    bpm: int
    source: HeartRateSource
    timestamp: str


class VO2Max(BaseModel):
    id: str
    day: date
    timestamp: str
    vo2_max: Optional[float] = None


class Workout(BaseModel):
    id: str
    activity: str
    calories: Optional[float] = None
    day: date
    distance: Optional[float] = None
    end_datetime: str
    intensity: WorkoutIntensity
    label: Optional[str] = None
    source: WorkoutSource
    start_datetime: str

    @property
    def duration_minutes(self) -> Optional[float]:
        try:
            start = datetime.fromisoformat(self.start_datetime)
            end = datetime.fromisoformat(self.end_datetime)
            return (end - start).total_seconds() / 60
        except (ValueError, TypeError):
            return None


class Session(BaseModel):
    id: str
    day: date
    start_datetime: str
    end_datetime: str
    type: MomentType
    heart_rate: Optional[Sample] = None
    heart_rate_variability: Optional[Sample] = None
    mood: Optional[MomentMood] = None
    motion_count: Optional[Sample] = None


class Tag(BaseModel):
    """Deprecated -- use EnhancedTag instead."""

    id: str
    day: date
    text: Optional[str] = None
    timestamp: str
    tags: list[str] = Field(default_factory=list)


class EnhancedTag(BaseModel):
    id: str
    tag_type_code: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    start_day: date
    end_day: Optional[date] = None
    comment: Optional[str] = None
    custom_name: Optional[str] = None


class SleepTime(BaseModel):
    id: str
    day: date
    optimal_bedtime: Optional[SleepTimeWindow] = None
    recommendation: Optional[SleepTimeRecommendation] = None
    status: Optional[SleepTimeStatus] = None


class RestModePeriod(BaseModel):
    id: str
    end_day: Optional[date] = None
    end_time: Optional[str] = None
    episodes: list[RestModeEpisode] = Field(default_factory=list)
    start_day: date
    start_time: Optional[str] = None


class RingConfiguration(BaseModel):
    id: str
    color: Optional[RingColor] = None
    design: Optional[RingDesign] = None
    firmware_version: Optional[str] = None
    hardware_type: Optional[RingHardwareType] = None
    set_up_at: Optional[str] = None
    size: Optional[int] = None


class WebhookSubscription(BaseModel):
    id: str
    callback_url: str
    event_type: WebhookOperation
    data_type: DataType
    expiration_time: datetime


# --- Paginated response wrappers ---


class PaginatedResponse(BaseModel):
    next_token: Optional[str] = None


class SleepResponse(PaginatedResponse):
    data: list[Sleep] = Field(default_factory=list)


class DailySleepResponse(PaginatedResponse):
    data: list[DailySleep] = Field(default_factory=list)


class DailyActivityResponse(PaginatedResponse):
    data: list[DailyActivity] = Field(default_factory=list)


class DailyReadinessResponse(PaginatedResponse):
    data: list[DailyReadiness] = Field(default_factory=list)


class DailyStressResponse(PaginatedResponse):
    data: list[DailyStress] = Field(default_factory=list)


class DailyResilienceResponse(PaginatedResponse):
    data: list[DailyResilience] = Field(default_factory=list)


class DailySpO2Response(PaginatedResponse):
    data: list[DailySpO2] = Field(default_factory=list)


class DailyCardiovascularAgeResponse(PaginatedResponse):
    data: list[DailyCardiovascularAge] = Field(default_factory=list)


class HeartRateResponse(PaginatedResponse):
    data: list[HeartRate] = Field(default_factory=list)


class VO2MaxResponse(PaginatedResponse):
    data: list[VO2Max] = Field(default_factory=list)


class WorkoutResponse(PaginatedResponse):
    data: list[Workout] = Field(default_factory=list)


class SessionResponse(PaginatedResponse):
    data: list[Session] = Field(default_factory=list)


class TagResponse(PaginatedResponse):
    data: list[Tag] = Field(default_factory=list)


class EnhancedTagResponse(PaginatedResponse):
    data: list[EnhancedTag] = Field(default_factory=list)


class SleepTimeResponse(PaginatedResponse):
    data: list[SleepTime] = Field(default_factory=list)


class RestModePeriodResponse(PaginatedResponse):
    data: list[RestModePeriod] = Field(default_factory=list)


class RingConfigurationResponse(PaginatedResponse):
    data: list[RingConfiguration] = Field(default_factory=list)
