# Connection settings
TOKEN_TYPE = "Bearer"
TOKEN = "ca0e46a7-6846-4eb2-b7d5-76087412aa84"
BASE_URL = 'https://analytics.maximum-auto.ru/vacancy-test/api/v0.1'
HEADERS = {'Authorization': TOKEN_TYPE + " " + TOKEN}

# Time intervals
MIN_TIME_FOR_RETRIEVING_REPORT_IN_SECONDS = 30
MAX_TIME_FOR_RETRIEVING_REPORT_IN_SECONDS = 300  # 5 minutes
TIME_BETWEEN_REQUESTS_FOR_CREATING_REPORTS_IN_SECONDS = 60  # 1 minute
TIME_BETWEEN_GET_REQUESTS_IN_SECONDS = 0.8  # Time is chosen in such way that
# the real time between requests is as close as possible to one minute

# Status codes from API
REPORT_RETRIEVED_STATUS_CODE = 200
REQUESTS_FOR_CREATING_REPORT_SUCCESSFULLY_SENT_STATUS_CODE = 201
REPORT_STILL_NOT_AVAILABLE_STATUS_CODE = 202
REPORT_ALREADY_EXISTS_STATUS_CODE = 409

# Messages
# Base messages
POST_REQUEST_BASE_MESSAGE = "request to create report with id={report_id}"

TRYING_AGAIN_MESSAGE = "\nTrying again..."

# Error Messages
CONNECTION_FAILED_MESSAGE = "Connection failed. " + TRYING_AGAIN_MESSAGE

TIME_FOR_CREATING_REPORT_PASSED_MESSAGE = \
    "Time to create report with id ={report_id} has expired!"

UNEXPECTED_STATUS_CODE_FROM_API_MESSAGE = \
    "Unexpected status code from API '{status_code} " \
    "{reason_phrase}' for url '{url}'"

# Success messages
POST_REQUEST_WAS_SENT_SUCCESSFULLY_MESSAGE = \
    POST_REQUEST_BASE_MESSAGE.capitalize() + " sent successfully\n" + \
    "Waiting for {time} sec before starting to check if the report is ready..."

REPORT_SUCCESSFULLY_RETRIEVED_MESSAGE = 'Report {} retrieved successfully!'

# Debug messages
REPORT_STILL_NOT_AVAILABLE_MESSAGE = \
    'Report with id={report_id} still not available...\n' \
    'time elapsed since request to create report: {time_passed} seconds\n' \
    'GET-requests amount = {count}'

# .csv line
LINE_FOR_CSV = "{timestamp};{value}\\n\n"