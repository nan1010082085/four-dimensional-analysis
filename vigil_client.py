"""
Vigil 监控封装：基于官方 vigil-python SDK（Flask）。

环境变量：
  VIGIL_TOKEN — 必填，否则跳过
  VIGIL_SERVER_URL / VIGIL_ENDPOINT — ingest 基址
  VIGIL_ENV / FLASK_ENV — 环境名
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_SDK_ROOT = Path(__file__).resolve().parents[1] / "vigil" / "sdks" / "python"
if str(_SDK_ROOT) not in sys.path and _SDK_ROOT.is_dir():
    sys.path.insert(0, str(_SDK_ROOT))

try:
    from vigil import Vigil, ServiceInfo
    from vigil.integrations.flask import setup_flask
    from vigil.plugins import heartbeat_plugin, state_plugin
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "无法导入官方 vigil SDK。请安装: pip install -e ../vigil/sdks/python"
    ) from exc

_client: Optional[Vigil] = None


def _resolve_ingest_url(server_url: str) -> str:
    """将基址规范为完整 ingest URL。"""
    base = server_url.rstrip("/")
    if base.endswith("/ingest/v1/events"):
        return base
    return f"{base}/ingest/v1/events"


def get_vigil_client() -> Optional[Vigil]:
    """获取全局 Vigil 客户端。"""
    return _client


def shutdown_vigil() -> None:
    """关闭全局 Vigil 客户端。"""
    global _client
    if _client:
        _client.stop()
        _client = None


def setup_flask_vigil(app: Any) -> Optional[Vigil]:
    """
    从环境变量初始化并挂载官方 Flask 中间件。

    @param app Flask 应用
    @returns Vigil 实例或 None
    """
    import os

    global _client

    token = (os.environ.get("VIGIL_TOKEN") or "").strip()
    if not token:
        logger.info("[vigil] skip: no VIGIL_TOKEN")
        return None

    server_url = (
        os.environ.get("VIGIL_ENDPOINT")
        or os.environ.get("VIGIL_SERVER_URL")
        or "https://pyflow.icu/vigil-ingest"
    )
    environment = (
        os.environ.get("VIGIL_ENV")
        or os.environ.get("FLASK_ENV")
        or os.environ.get("ENV")
        or "development"
    )

    vigil = Vigil(
        token=token,
        service=ServiceInfo(name="four-dimensional-analysis-api", env=environment),
        endpoint=_resolve_ingest_url(server_url),
        on_error=lambda msg, detail: logger.error("[vigil] %s %s", msg, detail or ""),
        on_auth_error=lambda: logger.error("[vigil] AUTH ERROR 401"),
    )
    vigil.start([heartbeat_plugin, state_plugin])
    setup_flask(app, vigil)
    _client = vigil
    logger.info("[vigil] Flask monitoring started → %s", server_url)
    return vigil
