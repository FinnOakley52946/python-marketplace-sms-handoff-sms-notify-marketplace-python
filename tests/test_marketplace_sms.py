from src.marketplace_sms import OrderHandoff, handoff_message


def test_handoff_message_names_order_asset_and_window():
    order = OrderHandoff("ORD-7", "+15550001", "+15550002", "Blue bike", "Friday 15:00-17:00")
    assert handoff_message(order) == "Order ORD-7 is ready: Blue bike. Pickup window: Friday 15:00-17:00."
