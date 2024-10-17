class FinancialScraperError(Exception):
    """Base class for all exceptions raised by the FinancialScraper."""
    pass


class InvalidTypeError(FinancialScraperError):
    """Raised when an invalid statement type is provided."""
    def __init__(self, message="Invalid financial statement type provided."):
        self.message = message
        super().__init__(self.message)


class DateRangeError(FinancialScraperError):
    """Raised when the start date is later than the end date."""
    def __init__(self, message="start_date must be earlier than end_date."):
        self.message = message
        super().__init__(self.message)


class DataFetchError(FinancialScraperError):
    """Raised when there is an issue fetching data from the remote server."""
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code
        self.message = f"Failed to fetch data from {self.url}. HTTP Status code: {self.status_code}"
        super().__init__(self.message)


class DataParsingError(FinancialScraperError):
    """Raised when there is an error parsing the HTML data."""
    def __init__(self, message="Failed to parse financial data from the HTML content."):
        self.message = message
        super().__init__(self.message)


class NoDataError(FinancialScraperError):
    """Raised when no data is returned or data is missing from the server."""
    def __init__(self, message="No data found for the given stock ID and date range."):
        self.message = message
        super().__init__(self.message)


class ConnectionTimeoutError(FinancialScraperError):
    """Raised when the request to the server times out."""
    def __init__(self, message="Connection to the server timed out."):
        self.message = message
        super().__init__(self.message)


class InvalidDateFormatError(FinancialScraperError):
    """Raised when the date format is invalid or cannot be parsed."""
    def __init__(self, message="Invalid date format. Please use 'YYYY-MM-DD'."):
        self.message = message
        super().__init__(self.message)


class UnexpectedResponseError(FinancialScraperError):
    """Raised when the server returns an unexpected response or content type."""
    def __init__(self, message="Unexpected response from the server."):
        self.message = message
        super().__init__(self.message)
