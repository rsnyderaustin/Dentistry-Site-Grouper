from .worksite import Worksite


class Provider:

    def __init__(self, hcp_id: int, provider_data: dict = None):
        self.hcp_id = hcp_id

        if provider_data:
            for k, v in provider_data.items():
                setattr(self, k, v)
