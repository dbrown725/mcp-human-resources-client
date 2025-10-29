from typing import Union, Optional
import requests

def query_advised(question: str,
                  base_url: str = "http://localhost:8081/rag/advised",
                  timeout: float = 5.0) -> Union[dict, str]:
    """
    Send a GET request to the /rag/advised endpoint with the given question.

    Returns parsed JSON if the response is JSON, otherwise returns raw text.
    Raises requests.exceptions.RequestException on network/HTTP errors.
    """
    params = {"question": question}
    resp = requests.get(base_url, params=params, timeout=timeout)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return resp.json()
    return resp.text