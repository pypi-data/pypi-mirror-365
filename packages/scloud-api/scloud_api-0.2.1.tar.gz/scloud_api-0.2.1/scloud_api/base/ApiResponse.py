class ApiResponse:
    def __init__(self, response):
        self.payload = response['Items']
        self.total_results = response['TotalResults']