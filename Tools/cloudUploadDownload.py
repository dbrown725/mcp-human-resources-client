import base64
import requests
import os
from io import BytesIO
import logging
from dotenv import load_dotenv
import json

load_dotenv() 

# Configure logging
logging.basicConfig(
    filename='/var/log/mcp-human-resources-client/mcp-human-resources-client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("cloudUploadDownload")

def upload_file_to_gcs_cloud(file_path: str, target_directory: str) -> str:
    """
    Uploads a file to the Spring Boot endpoint at http://localhost:8081/upload,
    prepending the target_directory to the filename.

    Args:
        file_path (str): Relative path to the file you want to upload.
        target_directory (str): Directory to prepend to the filename.

    Returns:
        str: The response text returned by the Spring Boot controller.
    """
    url = "http://localhost:8081/upload"
    filename = os.path.basename(file_path)
    # Added to ensure no trailing slash was added by the user or LLM
    target_directory = target_directory.rstrip("/")

    if target_directory:
        upload_filename = f"{target_directory.rstrip('/')}/{filename}"
    else:
        upload_filename = filename

    logger.info(f"upload_filename: {upload_filename}")

    full_path = os.getenv('LOCAL_FILE_STORAGE') + "/" + file_path
    logger.info(f"file_path: {file_path}")
    logger.info(f"full_path: {full_path}")
    with open(full_path, "rb") as f:
        files = {"file": (upload_filename, f)}
        response = requests.post(url, files=files)

    response.raise_for_status()
    logger.info(f"response: {response.text}")

    return response.text

def download_file_from_gcs_cloud(file_name: str, target_directory: str) -> str:
    """
    Downloads a file from the Spring Boot endpoint at http://localhost:8081/download-file/{fileName}
    and saves it to the specified local target directory.

    Args:
        file_name (str): The name of the file to download.
        target_directory (str): The local directory to save the downloaded file.

    Returns:
        str: The path to the saved file.
    """
    logger.info(f"download_file_from_spring_boot called with file_name='{file_name}', target_directory='{target_directory}'")
    
    url = f"http://localhost:8081/download-file?fileName={file_name}"

    full_target_directory = os.getenv('LOCAL_FILE_STORAGE') + "/" + target_directory
    logger.info(f"full_target_directory: {full_target_directory}")

    file_name = os.path.basename(file_name)
    logger.info(f"os.path.basename(file_name): file_name {file_name}")
    local_path = os.path.join(full_target_directory, file_name)
    logger.info(f"os.path.join(target_directory, file_name: local_path {local_path}")
    os.makedirs(full_target_directory, exist_ok=True)
    logger.info(f"Downloading {url} to {local_path}")

    response = requests.get(url)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(response.content)

    logger.info(f"File saved to {local_path}")
    return f"File '{file_name}' has been saved to '{full_target_directory}'"

def summarize_images_in_cloud_folder(folder_name: str) -> dict:
    """
    Calls the REST endpoint to summarize all images in the specified cloud folder.

    Args:
        folder_name (str): The cloud folder to summarize images from.

    Returns:
        dict: The summary data returned by the endpoint.
    """
    url = f"http://localhost:8081/summarize-images-in-folder?folder={folder_name}"
    logger.info(f"Requesting image summary for folder: {folder_name} from {url}")
    response = requests.get(url)
    response.raise_for_status()
    summary = response.json()
    logger.info(f"Summary received: {summary}")
    return summary

def generate_expense_report(folder_name: str) -> dict:
    """
    Calls the REST endpoint to generate an expense report for all receipts in the specified cloud folder.

    Args:
        folder_name (str): The cloud folder containing expense receipts.

    Returns:
        dict: The expense report data returned by the endpoint.
    """
    url = f"http://localhost:8081/generate-expense-report?folder={folder_name}"
    logger.info(f"Requesting expense report for folder: {folder_name} from {url}")
    response = requests.get(url)
    response.raise_for_status()
    # report = response.json()
    report = response.text
    logger.info(f"Expense report received: {report}")
    return report
