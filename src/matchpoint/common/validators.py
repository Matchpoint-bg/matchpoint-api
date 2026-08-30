from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from cloudinary import CloudinaryResource
from django.core.files.uploadedfile import InMemoryUploadedFile
import datetime
from common.exceptions import IncorrectTimeException
from common.helpers import is_30_minutes_increment


@deconstructible
class Is30MinutesIncrement:
    def __init__(self, message=None) -> None:
        self.message = message

    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str | None):
        if not value:
            value = "The time is not a 30 minutes increment"
        self.__message = value

    def __call__(self, value: datetime.datetime | datetime.time) -> None:
        if not is_30_minutes_increment(value):
            raise IncorrectTimeException(detail=self.message)


@deconstructible
class CustomImageFormatValidator:
    def __init__(self, message=None):
        self.message = message

    @property
    def message(self, value: str | None) -> str:
        return self.__message

    @message.setter
    def message(self, value):
        if not value:
            value = "Incorrect image format"
        self.__message = value

    def __call__(self, value: CloudinaryResource | InMemoryUploadedFile):
        if isinstance(value, CloudinaryResource):
            if value.format not in ["png", "jpg", "jpeg", "webp"]:
                raise ValidationError(message=self.message)
        elif isinstance(value, InMemoryUploadedFile):
            name = value.name.lower()
            extension = name.split(".")[-1]
            if extension not in ["png", "jpg", "jpeg", "webp"]:
                raise ValidationError(message=self.message)
