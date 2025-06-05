from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal

class UserGoals(BaseModel):
    # Budget and priorities
    budget: float = Field(default=1000.0, description="Total budget for the build")
    cpu_priority: Literal["low", "medium", "high"] = Field(default="medium")
    memory_priority: Literal["low", "medium", "high"] = Field(default="medium")
    storage_priority: Literal["low", "medium", "high"] = Field(default="medium")
    video_card_priority: Literal["low", "medium", "high"] = Field(default="medium")
    case_priority: Literal["low", "medium", "high"] = Field(default="medium")
    psu_priority: Literal["low", "medium", "high"] = Field(default="medium")
    monitor_priority: Literal["low", "medium", "high"] = Field(default="medium")
    keyboard_priority: Literal["low", "medium", "high"] = Field(default="medium")
    mouse_priority: Literal["low", "medium", "high"] = Field(default="medium")
    headphones_priority: Literal["low", "medium", "high"] = Field(default="medium")
    speakers_priority: Literal["low", "medium", "high"] = Field(default="medium")
    webcam_priority: Literal["low", "medium", "high"] = Field(default="medium")
    network_priority: Literal["low", "medium", "high"] = Field(default="medium")
    os_priority: Literal["low", "medium", "high"] = Field(default="medium")
    cooler_priority: Literal["low", "medium", "high"] = Field(default="medium")
    fan_priority: Literal["low", "medium", "high"] = Field(default="medium")
    accessory_priority: Literal["low", "medium", "high"] = Field(default="medium")

    # CPU requirements
    min_cores: Optional[int] = None
    cpu_min_core_clock: Optional[float] = None
    cpu_min_boost_clock: Optional[float] = None
    max_tdp: Optional[int] = None
    require_smt: Optional[bool] = None
    require_igpu: Optional[bool] = None
    preferred_cpu_brands: Optional[List[str]] = None

    # Memory requirements
    min_speed: Optional[int] = None
    min_modules: Optional[int] = None
    max_cas_latency: Optional[int] = None
    max_first_word_latency: Optional[int] = None
    memory_color: Optional[str] = None
    preferred_memory_brands: Optional[List[str]] = None

    # Storage requirements
    min_capacity: Optional[int] = None
    drive_type: Optional[str] = None
    min_cache: Optional[int] = None
    preferred_drive_brands: Optional[List[str]] = None

    # Video card requirements
    min_vram: Optional[int] = None
    gpu_min_core_clock: Optional[float] = None
    gpu_min_boost_clock: Optional[float] = None
    preferred_gpu_brands: Optional[List[str]] = None

    # Case requirements
    case_type: Optional[str] = None
    case_color: Optional[str] = None
    side_panel: Optional[str] = None
    min_external_bays: Optional[int] = None
    min_internal_bays: Optional[int] = None
    preferred_case_brands: Optional[List[str]] = None

    # PSU requirements
    psu_type: Optional[str] = None
    efficiency_rating: Optional[str] = None
    modular_preference: Optional[str] = None
    psu_color: Optional[str] = None
    preferred_psu_brands: Optional[List[str]] = None

    # Monitor requirements
    min_screen_size: Optional[float] = None
    min_resolution: Optional[str] = None
    min_refresh_rate: Optional[int] = None
    max_response_time: Optional[int] = None
    panel_type: Optional[str] = None
    aspect_ratio: Optional[str] = None
    preferred_monitor_brands: Optional[List[str]] = None

    # Keyboard requirements
    keyboard_style: Optional[str] = None
    switch_type: Optional[str] = None
    backlight_type: Optional[str] = None
    require_tenkeyless: Optional[bool] = None
    connection_type: Optional[str] = None
    keyboard_color: Optional[str] = None
    preferred_keyboard_brands: Optional[List[str]] = None

    # Mouse requirements
    tracking_method: Optional[str] = None
    connection_type: Optional[str] = None
    min_dpi: Optional[int] = None
    hand_orientation: Optional[str] = None
    mouse_color: Optional[str] = None
    preferred_mouse_brands: Optional[List[str]] = None

    # Headphones requirements
    headphone_type: Optional[str] = None
    min_frequency: Optional[int] = None
    max_frequency: Optional[int] = None
    require_microphone: Optional[bool] = None
    require_wireless: Optional[bool] = None
    enclosure_type: Optional[str] = None
    headphone_color: Optional[str] = None
    preferred_headphone_brands: Optional[List[str]] = None

    # Speakers requirements
    speaker_type: Optional[str] = None
    min_wattage: Optional[int] = None
    speaker_color: Optional[str] = None
    preferred_speaker_brands: Optional[List[str]] = None

    # Webcam requirements
    min_resolution: Optional[str] = None
    connection_type: Optional[str] = None
    focus_type: Optional[str] = None
    min_fov: Optional[float] = None
    preferred_webcam_brands: Optional[List[str]] = None

    # Network requirements
    wireless_protocol: Optional[str] = None
    interface_type: Optional[str] = None
    preferred_network_brands: Optional[List[str]] = None

    # OS requirements
    os_mode: Optional[str] = None
    preferred_os_brands: Optional[List[str]] = None

    # Cooler requirements
    cooler_color: Optional[str] = None
    max_noise_level: Optional[int] = None
    min_rpm: Optional[int] = None
    preferred_cooler_brands: Optional[List[str]] = None

    # Fan requirements
    fan_color: Optional[str] = None
    max_noise_level: Optional[int] = None
    min_rpm: Optional[int] = None
    min_airflow: Optional[int] = None
    pwm_required: Optional[bool] = None
    preferred_fan_brands: Optional[List[str]] = None

    # Accessory requirements
    accessory_type: Optional[str] = None
    preferred_accessory_brands: Optional[List[str]] = None

class BuildState(BaseModel):
    user_goals: UserGoals
    selected_parts: Dict[str, Optional[Dict[str, Any]]] = Field(default_factory=dict)
    current_total_cost: float = Field(default=0.0)
    compatibility_issues: List[str] = Field(default_factory=list)
    budget_violation: bool = Field(default=False)
    part_attempt_log: Dict[str, List[str]] = Field(default_factory=dict)
    downgrade_log: Dict[str, List[str]] = Field(default_factory=dict, description="Records which components were downgraded and why")
    build_complete: bool = Field(default=False)
