from scloud_api.auth import auth_token_client

class Client:
    def __init__(self, credentials=None):
        self._auth = auth_token(credentials)