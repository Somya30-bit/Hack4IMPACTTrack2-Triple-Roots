def get_market_data(crop):
    crop = (crop or "").strip().lower()

    sample_data = {
        "tomato": {"price": 25, "trend": "up"},
        "potato": {"price": 18, "trend": "down"},
        "rice": {"price": 40, "trend": "stable"},
        "wheat": {"price": 30, "trend": "up"}
    }

    return sample_data.get(crop, {"price": 20, "trend": "unknown"})


def generate_market_advice(crop, data):
    price = data["price"]
    trend = data["trend"]

    advice = []

    if trend == "up":
        advice.append("Prices are increasing. You may wait to sell for better profit.")
    elif trend == "down":
        advice.append("Prices are decreasing. Consider selling soon.")
    elif trend == "stable":
        advice.append("Prices are stable. Sell based on your storage capacity.")
    else:
        advice.append("Market trend unclear. Monitor prices before selling.")

    advice.append(f"Current average price for {crop} is ₹{price}/kg.")

    return advice