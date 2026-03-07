import os
import logging
from typing import List, Optional

import requests
from dotenv import load_dotenv
from logging_config import configure_app_logging

load_dotenv()

configure_app_logging()

logger = logging.getLogger("saveDraftEmail")


def save_draft_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
    storage_attachments: Optional[List[str]] = None,
    in_reply_to_message_id: Optional[str] = None,
    base_url: str = "http://localhost:8081/save-draft-email",
) -> str:
    """
    Save an email draft via the Java endpoint /save-draft-email.

    attachment_paths should reflect exactly what the user entered. The allowed directory is assumed
    to be known by this tool, so it prepends LOCAL_FILE_STORAGE to each attachment path provided.

    storage_attachments should include any storage identifiers/paths already known to the server.
    """
    logger.info("save_draft_email_via_endpoint called")

    data: List[tuple] = [
        ("toEmail", to_email),
        ("subject", subject),
        ("body", body),
    ]

    if storage_attachments:
        for storage_attachment in storage_attachments:
            data.append(("storageAttachments", storage_attachment))

    if in_reply_to_message_id:
        data.append(("inReplyToMessageId", in_reply_to_message_id))

    files = []
    opened_files = []

    try:
        if attachment_paths:
            for attachment_path in attachment_paths:
                full_path = os.path.join(os.getenv('LOCAL_FILE_STORAGE', ''), attachment_path)
                logger.info(f"Adding attachment: {full_path}")
                if not os.path.isfile(full_path):
                    raise FileNotFoundError(f"Attachment not found: {full_path}")
                file_handle = open(full_path, "rb")
                opened_files.append(file_handle)
                files.append(
                    (
                        "attachments",
                        (os.path.basename(attachment_path), file_handle, "application/octet-stream"),
                    )
                )

        response = requests.post(base_url, data=data, files=files, timeout=30)
        response.raise_for_status()
        logger.info(
            "save_draft_email_via_endpoint response received (status=%d, response_length=%d)",
            response.status_code,
            len(response.text or ""),
        )
        return response.text
    finally:
        for file_handle in opened_files:
            try:
                file_handle.close()
            except Exception:
                pass
