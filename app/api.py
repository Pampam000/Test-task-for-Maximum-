import abc
import asyncio
import json
import uuid
from datetime import datetime

import httpx

from . import exceptions as exc
from . import settings as st
from .logger import logger


class ReportBase(metaclass=abc.ABCMeta):
    """
    Base abstract class for handling http-requests
    Notice: do not instantiate this class otherwise TypeError will be raised
    """
    _client = None
    _sleeping_time: int = None
    _expected_2xx_status_codes: tuple = None

    async def connect(self, sleep: bool):
        """
        Creating client and sending first request
        """
        try:
            async with httpx.AsyncClient(headers=st.HEADERS,
                                         base_url=st.BASE_URL) as client:
                self._client = client
                await self._run(sleep=sleep)
        except httpx.ConnectTimeout:
            logger.warning(st.CONNECTION_FAILED_MESSAGE)
            await self.connect(sleep=sleep)

    async def _run(self, sleep: bool = True):
        """
        Sleeping for a _sleeping_time if sleep==True,
        then sending a new request
        """
        if sleep:
            await asyncio.sleep(self._sleeping_time)
        try:
            await self._send_request()
        except httpx.HTTPStatusError as ex:
            logger.error(ex)
            await self._check_exception(ex)
        except exc.UnexpectedAPIStatusCode as ex:
            logger.error(ex)
            raise SystemExit()

    @abc.abstractmethod
    async def _send_request(self):
        """
        This method must be overridden in child classes.
        """
        pass

    async def _check_exception(self, ex: Exception):
        pass

    def _check_response(self, response: httpx.Response):
        response.raise_for_status()
        if response.status_code not in self._expected_2xx_status_codes:
            raise exc.UnexpectedAPIStatusCode(response=response)


class ReportCreator(ReportBase):
    _expected_2xx_status_codes = \
        (st.REQUESTS_FOR_CREATING_REPORT_SUCCESSFULLY_SENT_STATUS_CODE,)
    _sleeping_time = st.TIME_BETWEEN_REQUESTS_FOR_CREATING_REPORTS_IN_SECONDS

    async def _send_request(self):
        """
        Sending a POST-request to create report and running 2 async tasks:
            1. Checking if report is ready
            2. Sending new POST-request in a minute
        """
        report_id = str(uuid.uuid4())
        response = await self._client.post(url="reports",
                                           data=json.dumps({'id': report_id}))
        
        self._check_response(response)

        datetime_created = self.__get_timestamp_from_response(response)

        logger.info(st.POST_REQUEST_WAS_SENT_SUCCESSFULLY_MESSAGE.format(
            report_id=report_id,
            time=st.MIN_TIME_FOR_RETRIEVING_REPORT_IN_SECONDS))

        report_checker = ReportChecker(report_id, datetime_created)
        await asyncio.gather(report_checker.connect(sleep=True), self._run())

    async def _check_exception(self, ex: httpx.HTTPStatusError):
        """
        Sending a new request to create a report if it already exists
        """
        status_code = ex.response.status_code
        response_text = ex.response.text.rstrip()

        if status_code == st.REPORT_ALREADY_EXISTS_STATUS_CODE:
            logger.warning(response_text + st.TRYING_AGAIN_MESSAGE)
            await self._run(sleep=False)
        else:
            logger.warning(response_text)
            raise SystemExit(0)

    @staticmethod
    def __get_timestamp_from_response(response: httpx.Response) -> float:
        """
        Date from headers example:
            Sun, 19 Mar 2023 13:01:34 GMT
        :return: datetime as timestamp
        """
        datetime_created_str = response.headers['date']
        datetime_created = datetime.strptime(datetime_created_str,
                                             '%a, %d %b %Y %H:%M:%S %Z')
        return datetime_created.timestamp()


class ReportChecker(ReportBase):
    """
    Checking if the report is ready
    """

    def __init__(self, report_id: str, timestamp_created: float):
        self.__report_id = report_id
        self.__timestamp_created = timestamp_created

    _expected_2xx_status_codes = (st.REPORT_RETRIEVED_STATUS_CODE,
                                  st.REPORT_STILL_NOT_AVAILABLE_STATUS_CODE)
    _sleeping_time = st.MIN_TIME_FOR_RETRIEVING_REPORT_IN_SECONDS

    async def _run(self, sleep: bool = True):
        try:
            await super()._run(sleep)
        except exc.TooMuchTimePassed as ex:
            logger.error(ex)

    async def _send_request(self):
        count = 0
        response = await self.__make_request_and_check_response()

        while response.status_code != st.REPORT_RETRIEVED_STATUS_CODE:
            time_passed = self.__check_time_elapsed()

            count += 1
            logger.debug(st.REPORT_STILL_NOT_AVAILABLE_MESSAGE.format(
                report_id=self.__report_id, time_passed=time_passed,
                count=count))

            await asyncio.sleep(st.TIME_BETWEEN_GET_REQUESTS_IN_SECONDS)
            response = await self.__make_request_and_check_response()

        self.__report_retrieved(response)

    async def __make_request_and_check_response(self) -> httpx.Response:
        response = await self._client.get(f"reports/{self.__report_id}")
        self._check_response(response)
        return response

    def __check_time_elapsed(self) -> int:
        """
        :return: time elapsed from the moment the request for the creation
         of the report was submitted until now
        """
        time_elapsed = datetime.utcnow().timestamp() - self.__timestamp_created

        if time_elapsed > st.MAX_TIME_FOR_RETRIEVING_REPORT_IN_SECONDS:
            raise exc.TooMuchTimePassed(self.__report_id)
        return round(time_elapsed, 1)

    def __report_retrieved(self, response: httpx.Response):
        logger.info(st.REPORT_SUCCESSFULLY_RETRIEVED_MESSAGE.format(
            self.__report_id))
        value = response.json()['value']
        self.__add_new_line_to_csv(value)

    def __add_new_line_to_csv(self, value: str):
        with open('results.csv', 'a') as file:
            line = st.LINE_FOR_CSV.format(timestamp=self.__timestamp_created,
                                          value=value)
            file.write(line)
