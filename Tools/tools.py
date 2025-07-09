from Tools.email_client import handle_save_draft_request
from Tools.geo import get_location_by_city_and_state

def add(a: int, b: int) -> int:
    """Adds two numbers and returns the sum."""
    return a + b

def saveDraftEmailContent(to_email: str, subject: str, body: str):
    """Save a draft email by providing email recipient address, email subject and the body of the email."""

    handle_save_draft_request(to_email, subject, body,[])
    return f"Draft email saved for {to_email} with subject: {subject}"

def getGeoLocation(city: str, state: str) -> str:
    """Get geolocation coordinates based on city and state"""
    return get_location_by_city_and_state(city, state)