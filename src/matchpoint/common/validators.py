from django.utils.deconstruct import deconstructible
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
