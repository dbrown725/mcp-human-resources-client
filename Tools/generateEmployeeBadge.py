import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL", "http://localhost:8081")

def generate_employee_badge(
    first_name: str,
    last_name: str,
    employee_number: str,
    existing_employee_image_name: str,
    base_url: str = f"{BACKEND_SERVER_URL}/generate-employee-badge"
) -> bytes:
    params = {
        "firstName": first_name,
        "lastName": last_name,
        "employeeNumber": employee_number,
        "existingEmployeeImageName": existing_employee_image_name
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.content

# Example usage:
# badge = generate_employee_badge(
#     "Randy", "Broussard", "6000", "original_images/randy_broussard.jpg"
# )