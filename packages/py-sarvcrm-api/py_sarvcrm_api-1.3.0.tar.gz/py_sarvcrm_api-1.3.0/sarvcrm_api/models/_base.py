class BaseModel:
    def __init__(self, client) -> None:
        from sarvcrm_api import SarvClient
        self._client: SarvClient = client