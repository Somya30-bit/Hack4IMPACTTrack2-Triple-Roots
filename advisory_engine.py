def generate_weather_advisory(crop, weather_data):
    """
    Generate crop-specific advisories from OpenWeatherMap forecast data.
    Returns a list of advisory strings.
    """
    advisories = []

    if not weather_data or "list" not in weather_data:
        return ["Weather data unavailable. Please check the city name or try again later."]

    crop = (crop or "").strip().lower()
    forecast_list = weather_data.get("list", [])[:8]  # next 24 hours approx.

    if not forecast_list:
        return ["Forecast data is incomplete. Please try again later."]

    heavy_rain_detected = False
    moderate_rain_detected = False
    high_temp_detected = False
    strong_wind_detected = False
    high_humidity_detected = False
    low_temp_detected = False

    for item in forecast_list:
        main_data = item.get("main", {})
        wind_data = item.get("wind", {})
        rain_data = item.get("rain", {})

        temp = main_data.get("temp", 0)
        humidity = main_data.get("humidity", 0)
        wind_speed = wind_data.get("speed", 0)
        rain = rain_data.get("3h", 0)

        if rain >= 10:
            heavy_rain_detected = True
        elif rain >= 3:
            moderate_rain_detected = True

        if temp >= 35:
            high_temp_detected = True

        if temp <= 10:
            low_temp_detected = True

        if wind_speed >= 10:
            strong_wind_detected = True

        if humidity >= 85:
            high_humidity_detected = True

    # General advisories
    if heavy_rain_detected:
        advisories.append("Heavy rain expected in the next 24 hours. Risk of waterlogging may rise.")
        advisories.append("Avoid irrigation before rainfall and ensure proper field drainage.")
    elif moderate_rain_detected:
        advisories.append("Moderate rain may occur in the next 24 hours.")
        advisories.append("Plan irrigation carefully and avoid unnecessary watering before rain.")

    if high_temp_detected:
        advisories.append("High temperature expected. Crops may face heat stress.")
        advisories.append("Prefer irrigation in early morning or evening to reduce water loss.")

    if low_temp_detected:
        advisories.append("Low temperature expected. Sensitive crops may face cold stress.")
        advisories.append("Protect young plants if possible and avoid unnecessary watering at night.")

    if strong_wind_detected:
        advisories.append("Strong wind conditions expected.")
        advisories.append("Avoid pesticide spraying during strong winds and support weak plants.")

    if high_humidity_detected:
        advisories.append("Humidity is high, which may support fungal disease development.")

    # Crop-specific advisories
    if crop == "tomato":
        if high_humidity_detected or heavy_rain_detected or moderate_rain_detected:
            advisories.append("Tomato crop may face increased fungal disease risk due to humidity and rain.")
            advisories.append("Inspect leaves for early blight, leaf spots, or fungal infection.")

    elif crop == "potato":
        if high_humidity_detected or heavy_rain_detected or moderate_rain_detected:
            advisories.append("Potato crop may face higher late blight risk under humid and wet conditions.")
            advisories.append("Monitor leaves for dark lesions and avoid water stagnation.")

    elif crop in ["paddy", "rice"]:
        if heavy_rain_detected or moderate_rain_detected:
            advisories.append("Paddy fields may experience excess water accumulation.")
            advisories.append("Check drainage channels and monitor standing water levels.")

    elif crop == "wheat":
        if high_humidity_detected:
            advisories.append("Wheat may face fungal infection risk due to high humidity.")
            advisories.append("Regularly inspect for rust, mildew, or leaf infection symptoms.")

    elif crop in ["chilli", "chili"]:
        if high_humidity_detected:
            advisories.append("Chilli crop may be vulnerable to fungal and leaf curl related stress.")
            advisories.append("Check for leaf curling, discoloration, and fungal spots.")

    elif crop in ["maize", "corn"]:
        if high_temp_detected:
            advisories.append("Maize crop may experience heat stress under high temperature.")
            advisories.append("Maintain soil moisture and monitor for wilting.")

    elif crop:
        advisories.append(f"No specific crop rules found for '{crop}', but general weather warnings are shown.")
    else:
        advisories.append("Crop name missing, so only general weather warnings are shown.")

    # Remove duplicates while preserving order
    unique_advisories = []
    for advice in advisories:
        if advice not in unique_advisories:
            unique_advisories.append(advice)

    if not unique_advisories:
        unique_advisories.append("No major weather-related risk detected in the next 24 hours.")

    return unique_advisories