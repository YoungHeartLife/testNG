from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

PUSHPLUS_API = "https://www.pushplus.plus/send"
DEFAULT_PUSHPLUS_TOKEN = ""


def send_pushplus_report(title: str, html: str, token: str | None = None) -> dict[str, Any]:
    push_token = token or os.getenv("PUSHPLUS_TOKEN") or DEFAULT_PUSHPLUS_TOKEN
    if not push_token:
        return {"code": -1, "msg": "PUSHPLUS_TOKEN 未配置，已生成报告但未推送"}
    payload = json.dumps(
        {
            "token": push_token,
            "title": title,
            "content": html,
            "template": "html",
        }
    ).encode("utf-8")
    req = request.Request(PUSHPLUS_API, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10) as response:  # noqa: S310 - user-configured PushPlus endpoint
        body = response.read().decode("utf-8")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"raw": body}
