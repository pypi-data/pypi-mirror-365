import json
from typing import Optional, Any


class EhrApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        data: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.data = data
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        data_dict = None
        if isinstance(self.data, dict):
            data_dict = self.data
        elif isinstance(self.data, str):
            try:
                data_dict = json.loads(self.data)
            except json.JSONDecodeError:
                # Not a valid JSON string, so we can't parse details from it.
                pass

        if isinstance(data_dict, dict):
            main_message = data_dict.get("message", self.message)
            detail_message = None
            details = data_dict.get("details")

            if isinstance(details, list) and details:
                first_detail = details[0]
                if isinstance(first_detail, dict):
                    detail_message = first_detail.get("message")
                elif isinstance(first_detail, str):
                    detail_message = first_detail

            if detail_message:
                return f"{main_message}{detail_message}"
            return str(main_message)

        return str(self.message)


class AuthenticationError(EhrApiError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, 401)
        self.name = "AuthenticationError"


class ValidationError(EhrApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 400)
        self.name = "ValidationError"
