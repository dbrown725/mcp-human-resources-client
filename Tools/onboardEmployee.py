import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mcp_human_resources_client_agent")

BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL", "http://localhost:8081")


def onboard_employee(
    employee_image_path: str,
    csv_file_path: str,
    first_name: str,
    last_name: str,
    personal_email: str,
    base_url: str = f"{BACKEND_SERVER_URL}/onboarding",
    timeout: int = 300,
) -> str:
    """
    Initiates the employee onboarding workflow by posting to the back-end /onboarding endpoint.

    Args:
        employee_image_path (str): Relative path (within the ALLOWED directory) to the employee's photo file (jpg, png, etc.).
        csv_file_path (str): Relative path (within the ALLOWED directory) to the CSV file with one header row and one data row
                             containing employee and address fields.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        personal_email (str): Employee's personal email address.
        base_url (str): The endpoint URL (defaults to BACKEND_SERVER_URL/onboarding).

    Returns:
        str: A summary report of the onboarding result (success or failure with rollback details).
    """
    logger.info(
        "onboard_employee called (first_name=%s, last_name=%s, personal_email=%s)",
        first_name,
        last_name,
        personal_email,
    )

    local_storage = os.getenv("LOCAL_FILE_STORAGE", "")

    image_full_path = os.path.join(local_storage, employee_image_path)
    csv_full_path = os.path.join(local_storage, csv_file_path)

    logger.info("employee_image full path: %s", image_full_path)
    logger.info("csv_file full path: %s", csv_full_path)

    if not os.path.isfile(image_full_path):
        raise FileNotFoundError(f"Employee image not found: {image_full_path}")
    if not os.path.isfile(csv_full_path):
        raise FileNotFoundError(f"CSV file not found: {csv_full_path}")

    opened_files = []
    try:
        image_handle = open(image_full_path, "rb")
        opened_files.append(image_handle)

        csv_handle = open(csv_full_path, "rb")
        opened_files.append(csv_handle)

        files = [
            ("employeeImage", (os.path.basename(image_full_path), image_handle)),
            ("csvFile", (os.path.basename(csv_full_path), csv_handle, "text/csv")),
        ]

        data = {
            "firstName": first_name,
            "lastName": last_name,
            "personalEmail": personal_email,
        }

        response = requests.post(base_url, data=data, files=files, timeout=timeout)
        response.raise_for_status()

        logger.info(
            "onboard_employee response received (status=%d, response_length=%d)",
            response.status_code,
            len(response.text or ""),
        )
        return response.text
    finally:
        for fh in opened_files:
            try:
                fh.close()
            except Exception:
                pass
