from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    if isinstance(exc, ValidationError):
        response.data = {"status": "error", "errors": response.data}
        return response

    response.data = {
        "status": "error",
        "message": str(response.data.get("detail", "Unknown error")),
    }

    return response
