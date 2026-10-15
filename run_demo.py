import os

from src.marketplace_sms import InfraiSMS, OrderHandoff, notify_handoff


if __name__ == "__main__":
    recipient = os.environ.get("DEMO_PHONE")
    if not recipient:
        raise SystemExit("Set DEMO_PHONE to run the live handoff example")
    order = OrderHandoff("ORD-1042", recipient, recipient, "Oak desk", "Saturday 10:00-12:00")
    print(notify_handoff(order, InfraiSMS()))
