"""
Utility functions for the GCP Assistant.
These functions provide non-GCP related capabilities like weather and time information.
"""

from typing import Dict

def get_weather(city: str) -> Dict[str, str]:
    """Retrieves the current weather report for a specified city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') 
              and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "new york":
        return {"status": "success",
                "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}
    else:
        return {"status": "error",
                "error_message": f"Weather information for '{city}' is not available."}

def get_current_time(city: str) -> Dict[str, str]:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        dict: A dictionary containing the current time information with a 'status' key ('success' or 'error')
              and a 'report' key with the current time details if successful, or an 'error_message' if an error occurred.
    """
    import datetime
    from zoneinfo import ZoneInfo

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {"status": "error",
                "error_message": f"Sorry, I don't have timezone information for {city}."}

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return {"status": "success",
            "report": f"""The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}"""} 