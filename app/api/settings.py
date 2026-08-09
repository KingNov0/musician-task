"""全局设置读写。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import repository as repo

router = APIRouter(prefix="/api/settings", tags=["settings"])

_EDITABLE = {
    "default_send_time",
    "execution_interval_days",
    "max_monthly_sends",
    "local_listen_start_time",
    "local_listen_daily_max",
    "local_listen_monthly_max",
    "local_listen_play_percent",
    "log_retention_days",
    "headless",
    "login_method",
    "wecom_webhook_key",
    "custom_webhook_url",
    "custom_webhook_method",
    "custom_webhook_headers",
    "custom_webhook_body",
}


class SettingsUpdate(BaseModel):
    values: dict[str, str]


@router.get("")
def get_settings() -> dict:
    values = repo.get_all_settings()
    values.pop("admin_password_hash", None)
    return values


@router.put("")
def update_settings(body: SettingsUpdate) -> dict:
    for k, v in body.values.items():
        if k in _EDITABLE:
            if k in {"local_listen_daily_max", "local_listen_monthly_max"}:
                try:
                    if int(v) < 0:
                        raise ValueError
                except ValueError as exc:
                    raise HTTPException(422, f"{k} 必须是非负整数") from exc
            if k == "local_listen_play_percent":
                try:
                    if not 34 <= int(v) <= 100:
                        raise ValueError
                except ValueError as exc:
                    raise HTTPException(422, "播放比例必须在 34 到 100 之间") from exc
            if k == "log_retention_days":
                try:
                    if not 1 <= int(v) <= 3650:
                        raise ValueError
                except ValueError as exc:
                    raise HTTPException(422, "日志保留天数必须在 1 到 3650 之间") from exc
            if k == "local_listen_start_time":
                try:
                    hour, minute = str(v).split(":")
                    if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                        raise ValueError
                except (ValueError, AttributeError) as exc:
                    raise HTTPException(422, "本地互助开始时间格式必须为 HH:MM") from exc
            repo.set_setting(k, str(v))
    repo.cleanup_logs(repo.get_setting_int("log_retention_days", 3))
    # 时间/开关变更后重排调度
    try:
        from app.scheduler import reschedule_all

        reschedule_all()
    except Exception:
        pass
    return get_settings()
