from rest_framework.exceptions import APIException


class IncorrectTimeException(APIException):
    status_code = 400
    default_detail = "The time entered is incorrect"
    default_code = "incorrect_time"


class TimeNotAllowedException(APIException):
    status_code = 400
    default_detail = "The entered time is outside of the opening time of the club"
    default_code = "time_not_allowed"


class NoOpeningTimesFound(APIException):
    status_code = 400
    default_detail = "No opening hours were found for this club"
    default_code = "no_opening_hours"


class NoPricingFound(APIException):
    status_code = 400
    default_detail = "No prices were found for this court at this time"
    default_code = "no_pricing_found"
