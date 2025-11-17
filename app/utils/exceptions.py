from fastapi import HTTPException, status

class WeakPasswordException(HTTPException):
    def __init__(self, details: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "WeakPassword",
                "message": details
            }
        )


class InvalidNameException(HTTPException):
    def __init__(self, details: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "InvalidName",
                "message": details
            }
        )
