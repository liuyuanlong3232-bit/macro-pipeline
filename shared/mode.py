#!/usr/bin/env python3
"""
Hermes Orchestrator Mode Manager
DEV / TEST / PROD 三模式管理
"""
import json
from pathlib import Path
from enum import Enum
from datetime import datetime


class RunMode(Enum):
    DEV = "DEV"
    TEST = "TEST"
    PROD = "PROD"


# 模式配置
MODE_CONFIG = {
    RunMode.DEV: {
        "max_requests_per_session": 5,
        "require_manual_trigger": True,
        "allow_mock": True,
        "allow_low_quality": True,
        "allow_full_pipeline": False,
        "allow_high_frequency": False,
        "count_in_risk_score": False,
        "jitter_range": (1, 3),
        "batch_size": 1,
    },
    RunMode.TEST: {
        "max_requests_per_batch": 20,
        "require_manual_trigger": False,
        "allow_mock": False,
        "allow_low_quality": False,
        "allow_full_pipeline": False,
        "allow_high_frequency": False,
        "count_in_risk_score": "local",
        "jitter_range": (2, 5),
        "batch_size": 10,
        "batch_cooldown": 300,
    },
    RunMode.PROD: {
        "max_requests_per_minute_per_domain": 6,
        "require_manual_trigger": False,
        "allow_mock": False,
        "allow_low_quality": False,
        "allow_full_pipeline": True,
        "allow_high_frequency": False,
        "count_in_risk_score": True,
        "jitter_range": (1, 5),
        "batch_size": 5,
        "time_window": (460, 520),  # 07:40-08:40 in minutes
    },
}


class ModeManager:
    """模式管理器"""

    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.current_mode = RunMode.DEV
        self.mode_history = []
        self._load()

    def _load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                self.current_mode = RunMode(data.get("mode", "DEV"))
                self.mode_history = data.get("history", [])
            except:
                pass

    def _save(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump({
                "mode": self.current_mode.value,
                "updated_at": datetime.now().isoformat(),
                "history": self.mode_history[-20:],
            }, f, indent=2)

    def get_mode(self) -> RunMode:
        return self.current_mode

    def get_config(self) -> dict:
        return MODE_CONFIG[self.current_mode]

    def set_mode(self, mode: RunMode, reason: str = ""):
        old = self.current_mode
        self.current_mode = mode
        self.mode_history.append({
            "from": old.value,
            "to": mode.value,
            "time": datetime.now().isoformat(),
            "reason": reason,
        })
        self._save()

    def can_switch_to(self, target: RunMode) -> tuple[bool, str]:
        current = self.current_mode
        if target == current:
            return False, "已在当前模式"

        if target == RunMode.PROD and current == RunMode.TEST:
            recent_test_runs = [h for h in self.mode_history
                                if h.get("to") == "TEST"][-3:]
            if len(recent_test_runs) < 3:
                return False, f"TEST→PROD需≥3次稳定运行(当前{len(recent_test_runs)}次)"

        return True, "OK"
