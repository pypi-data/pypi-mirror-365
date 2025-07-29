import httpx

class APIError(Exception):
    def __init__(self, status_code, message):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message

    @classmethod
    def from_httpx(cls, resp: httpx.Response):
        try:
            msg = resp.json().get("detail", resp.text)
        except ValueError:
            msg = resp.text
        return cls(resp.status_code, msg)
