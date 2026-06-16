#!/usr/bin/env python3
"""
Hermes Macro Data Orchestrator
风控感知与自动调度优化

核心目标：长期稳定运行，不触发风控
"""
import time
import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from typing import Optional, Dict
import requests

log = logging.getLogger("orchestrator")


class RiskState(Enum):
    NORMAL = "NORMAL"
    THROTTLED = "THROTTLED"
    BLOCKED = "BLOCKED"


class SourceState:
    """单个数据源的状态跟踪"""

    def __init__(self, name: str):
        self.name = name
        self.state = RiskState.NORMAL
        self.last_request_time = 0
        self.last_status_code = 200
        self.consecutive_429 = 0
        self.consecutive_403 = 0
        self.cooldown_until = 0
        self.total_requests = 0
        self.total_errors = 0

    def is_cooling_down(self) -> bool:
        return time.time() < self.cooldown_until

    def cooldown_remaining(self) -> float:
        return max(0, self.cooldown_until - time.time())


class Orchestrator:
    """数据采集风控调度器"""

    def __init__(self, state_file: str = None):
        self.sources: Dict[str, SourceState] = {}
        self.state_file = state_file
        self.request_log = []
        self._load_state()

    def _load_state(self):
        """加载持久化状态"""
        if self.state_file and Path(self.state_file).exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                for name, info in data.get("sources", {}).items():
                    s = SourceState(name)
                    s.state = RiskState(info.get("state", "NORMAL"))
                    s.cooldown_until = info.get("cooldown_until", 0)
                    self.sources[name] = s
                log.info(f"已加载 {len(self.sources)} 个数据源状态")
            except Exception as e:
                log.warning(f"加载状态失败: {e}")

    def _save_state(self):
        """持久化状态"""
        if self.state_file:
            data = {
                "updated_at": datetime.now().isoformat(),
                "sources": {}
            }
            for name, s in self.sources.items():
                data["sources"][name] = {
                    "state": s.state.value,
                    "last_status_code": s.last_status_code,
                    "consecutive_429": s.consecutive_429,
                    "consecutive_403": s.consecutive_403,
                    "cooldown_until": s.cooldown_until,
                    "total_requests": s.total_requests,
                    "total_errors": s.total_errors,
                }
            Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)

    def get_source(self, name: str) -> SourceState:
        """获取或创建数据源状态"""
        if name not in self.sources:
            self.sources[name] = SourceState(name)
        return self.sources[name]

    def can_request(self, name: str) -> tuple[bool, str]:
        """检查是否可以向该数据源发请求"""
        s = self.get_source(name)

        if s.state == RiskState.BLOCKED:
            if s.cooldown_until > 0:
                remaining = s.cooldown_remaining()
                if remaining > 0:
                    return False, f"BLOCKED 冷却中 {remaining:.0f}s"
                else:
                    s.state = RiskState.THROTTLED
                    s.cooldown_until = 0
                    s.consecutive_403 = 0
                    log.info(f"[{name}] BLOCKED → THROTTLED (冷却结束)")
            else:
                return False, "BLOCKED 等待人工恢复"

        if s.is_cooling_down():
            remaining = s.cooldown_remaining()
            return False, f"THROTTLED 冷却中 {remaining:.0f}s"

        return True, "OK"

    def record_response(self, name: str, status_code: int, response_time: float,
                        data_rows: int = 0):
        """记录请求响应，更新状态"""
        s = self.get_source(name)
        s.total_requests += 1
        s.last_request_time = time.time()
        s.last_status_code = status_code

        old_state = s.state

        if status_code == 200:
            s.state = RiskState.NORMAL
            s.consecutive_429 = 0
            s.consecutive_403 = 0
            s.cooldown_until = 0

        elif status_code == 429:
            s.consecutive_429 += 1
            s.total_errors += 1
            if s.consecutive_429 >= 3:
                s.state = RiskState.BLOCKED
                s.cooldown_until = time.time() + random.uniform(600, 1800)
                log.warning(f"[{name}] → BLOCKED (连续{ s.consecutive_429 }次429, "
                            f"冷却{s.cooldown_remaining():.0f}s)")
            else:
                s.state = RiskState.THROTTLED
                wait = (2 ** s.consecutive_429) * 60 + random.uniform(0, 60)
                s.cooldown_until = time.time() + wait
                log.warning(f"[{name}] → THROTTLED (429, "
                            f"冷却{wait:.0f}s)")

        elif status_code in (403, 421):
            s.consecutive_403 += 1
            s.total_errors += 1
            if s.consecutive_403 >= 2:
                s.state = RiskState.BLOCKED
                s.cooldown_until = time.time() + 3600
                log.warning(f"[{name}] → BLOCKED (连续{ s.consecutive_403 }次{status_code}, "
                            f"冷却3600s)")
            else:
                s.state = RiskState.THROTTLED
                s.cooldown_until = time.time() + 300
                log.warning(f"[{name}] → THROTTLED ({status_code}, 冷却300s)")

        elif status_code >= 500:
            s.total_errors += 1

        if s.state != old_state:
            log.info(f"[{name}] {old_state.value} → {s.state.value}")

        self._log_request(name, status_code, response_time, data_rows)
        self._save_state()

    def _log_request(self, name: str, status_code: int, response_time: float,
                     data_rows: int):
        """记录请求日志"""
        entry = {
            "time": datetime.now().isoformat(),
            "source": name,
            "status": status_code,
            "response_time": round(response_time, 3),
            "data_rows": data_rows,
        }
        self.request_log.append(entry)
        if len(self.request_log) > 1000:
            self.request_log = self.request_log[-500:]

    def get_delay(self, name: str) -> float:
        """根据状态返回请求间隔"""
        s = self.get_source(name)
        if s.state == RiskState.BLOCKED:
            return 999
        if s.state == RiskState.THROTTLED:
            return random.uniform(5, 15)
        return random.uniform(1, 3)

    def get_status_summary(self) -> list:
        """获取所有数据源状态摘要"""
        result = []
        for name, s in sorted(self.sources.items()):
            result.append({
                "name": name,
                "state": s.state.value,
                "total_requests": s.total_requests,
                "total_errors": s.total_errors,
                "last_status": s.last_status_code,
                "cooldown_remaining": round(s.cooldown_remaining()),
            })
        return result

    def pause(self, name: str):
        """手动暂停数据源"""
        s = self.get_source(name)
        s.state = RiskState.BLOCKED
        s.cooldown_until = 0
        log.info(f"[{name}] 手动暂停")
        self._save_state()

    def resume(self, name: str):
        """手动恢复数据源"""
        s = self.get_source(name)
        s.state = RiskState.NORMAL
        s.cooldown_until = 0
        s.consecutive_429 = 0
        s.consecutive_403 = 0
        log.info(f"[{name}] 手动恢复")
        self._save_state()


def safe_request(orch: Orchestrator, source: str, url: str,
                 method: str = "GET", **kwargs) -> Optional[requests.Response]:
    """带风控的安全请求"""
    can, reason = orch.can_request(source)
    if not can:
        log.warning(f"[{source}] 跳过请求: {reason}")
        return None

    delay = orch.get_delay(source)
    if delay > 0 and delay < 100:
        time.sleep(delay)

    start = time.time()
    try:
        resp = requests.request(method, url, timeout=kwargs.pop("timeout", 30), **kwargs)
        elapsed = time.time() - start
        rows = 0
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict):
                    rows = len(data.get("data", data.get("results", [])))
                elif isinstance(data, list):
                    rows = len(data)
            except:
                pass
        orch.record_response(source, resp.status_code, elapsed, rows)
        return resp
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start
        orch.record_response(source, 0, elapsed, 0)
        log.error(f"[{source}] 请求异常: {e}")
        return None
