from Tools.email_client import handle_save_draft_request
from Tools.geo import get_location_by_city_and_state
from Tools.cloudUploadDownload import upload_file_to_gcs_cloud
from Tools.cloudUploadDownload import download_file_from_gcs_cloud

from dotenv import load_dotenv

load_dotenv()

def add(a: int, b: int) -> int:
    """Adds two numbers and returns the sum."""
    return a + b

def save_draft_email_content(to_email: str, subject: str, body: str, attachment_paths: list = []) -> str:
    """Save a draft email by providing email recipient address, email subject, body of the email and a list of attachments.
    ****IMPORTANT**** - The allowed directory is assumed to be known by this tool, do not prepend the allowed directory to what the user
    entered as a filename or directory/filename. This tool will prepend the allowed directory to the filename or directory/filename that were supplied by the user."""
    handle_save_draft_request(to_email, subject, body, attachment_paths)
    return f"Draft email saved for {to_email} with subject: {subject}"

def get_geo_location(city: str, state: str) -> str:
    """Get geolocation coordinates based on city and state"""
    return get_location_by_city_and_state(city, state)

def upload_file_to_cloud(input_file_path: str, destination_path: str) -> None:
    """The input_file_path should reflect exactly what the user entered, do not modify in any way. 
    Upload a file to the specified destination path. If the user doesn't specify a destination path, leave destination_path blank.
    It should be assumed the file is located in the allowed directory you have access to.
    Examples:
        If the user says "Upload the file Outgoing/intellicare_solutions.jpeg to the expense_receipts GCS directory."
            input_file_path should be "Outgoing/intellicare_solutions.jpeg"
            destination_path should be "expense_receipts"
        If the user says "Upload all files in the Outgoing directory to the expense_receipts" then this function should be called multiple times, once for each file in the Outgoing directory.
            input_file_path should be just the word "Outgoing" and the filename, for instance "Outgoing/intellicare_solutions.jpeg". 
                ****IMPORTANT**** - The allowed directory is assumed to be known by the tool, do not prepend the allowed directory to the file name or path/file name which was supplied by the user.
            destination_path should be "expense_receipts"
        If the user says "Upload the file test.jpg to the cloud" and does not specify a destination path then:
            input_file_path should be "test.jpg"
            destination_path should be "" (an empty string)
    """
    upload_file_to_gcs_cloud(input_file_path, destination_path)

def download_file_from_cloud(input_file_path: str, local_destination_path: str) -> None:
    """Download a file from the specified input_file_path, the input_file_path indicated by the user should not be changed in any way.
    local_destination_path supplied by the user should not be changed in any way."""
    download_file_from_gcs_cloud(input_file_path, local_destination_path)
