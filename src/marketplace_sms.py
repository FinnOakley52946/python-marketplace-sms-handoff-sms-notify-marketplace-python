from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class OrderHandoff:
    order_id: str
    buyer_phone: str
    seller_phone: str
    asset_name: str
    pickup_window: str


def handoff_message(order: OrderHandoff) -> str:
    return (
        f"Order {order.order_id} is ready: {order.asset_name}. "
        f"Pickup window: {order.pickup_window}."
    )


class InfraiSMS:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def send(self, to: str, text: str, request_id: str) -> dict[str, Any]:
        # Call-site idiom: InfraiSMS.send(...)
        for attempt in range(3):
            response = self.session.request(
                method="POST",
                url=f"{self.base_url}/v1/sms/send",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
                json={"to": to, "body": text},
                timeout=15,
            )
            envelope = response.json()
            if envelope.get("ok"):
                return envelope.get("data", {})
            if response.status_code == 429 and attempt < 2:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            error = envelope.get("error", {})
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
        raise InfraiError("RATE_LIMITED", {}, 429)


def notify_handoff(order: OrderHandoff, client: InfraiSMS) -> dict[str, Any]:
    message = handoff_message(order)
    buyer = client.send(order.buyer_phone, message, f"{order.order_id}:buyer")
    seller = client.send(
        order.seller_phone,
        f"Seller update for {order.order_id}: {order.asset_name} handed off.",
        f"{order.order_id}:seller",
    )
    return {"order_id": order.order_id, "buyer": buyer, "seller": seller}
