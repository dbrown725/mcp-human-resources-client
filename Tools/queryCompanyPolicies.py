from typing import Union, Optional
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL", "http://localhost:8081")


def query_company_policies(
    question: str,
    topK: Optional[int] = None,
    similarityThreshold: Optional[float] = None,
    base_url: str = f"{BACKEND_SERVER_URL}/ai/company-policies",
    timeout: float = 30.0,
) -> Union[dict, str]:
    """
    Send a GET request to the /ai/company-policies endpoint.

    Args:
        question: The HR policy question to search for. 
        topK: The maximum number of similar documents to retrieve. If null or less than 1,
            the server defaults to its configured default value.
        similarityThreshold: The minimum similarity score (0.0 to 1.0) for matching
            documents. If null, the server defaults to its configured default value.
            Documents with lower similarity scores are filtered out.

    Returns parsed JSON if the response is JSON, otherwise returns raw text.
    Raises requests.exceptions.RequestException on network/HTTP errors.
    """
    params = {"question": question}

    if topK is not None:
        params["topK"] = topK
    if similarityThreshold is not None:
        params["similarityThreshold"] = similarityThreshold

    resp = requests.get(base_url, params=params, timeout=timeout)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return resp.json()
    print(resp.text)
    return resp.text