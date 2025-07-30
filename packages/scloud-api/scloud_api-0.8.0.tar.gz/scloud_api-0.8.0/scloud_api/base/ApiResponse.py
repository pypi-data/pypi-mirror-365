class ApiResponse:
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.payload = response['Items'] if 'Items' in response else response
        self.total_results = response['TotalResults'] if 'TotalResults' in response else None