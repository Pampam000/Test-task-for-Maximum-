from . import settings as st


class UnexpectedAPIStatusCode(Exception):
    def __init__(self, response):
        message = st.UNEXPECTED_STATUS_CODE_FROM_API_MESSAGE.format(
            status_code=response.status_code,
            reason_phrase=response.reason_phrase,
            url=response.url
        )
        super().__init__(message)


class TooMuchTimePassed(Exception):
    def __init__(self, report_id: int):
        message = st.TIME_FOR_CREATING_REPORT_PASSED_MESSAGE.format(
            report_id=report_id)
        super().__init__(message)
