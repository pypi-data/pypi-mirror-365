import httpx
from typing import Optional, Union


class HTTPTransport:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)

    def post(self, data: dict, url: Optional[str] = None) -> Union[dict, str]:
        if not url:
            url = self.base_url
        try:
            response = self.client.post(url, data=data)
            if response.is_redirect:
                location = response.headers.get("Location")
                return location
            return response.json()
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")

    def close(self):
        self.client.close()
