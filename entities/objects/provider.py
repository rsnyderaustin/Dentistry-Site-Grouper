from .worksite import Worksite

from column_enums import ProviderDataColumns


class Provider:

    def __init__(self, hcp_id: int, provider_data: dict = None):
        setattr(self, ProviderDataColumns.PROVIDER_ID.value, hcp_id)

        if provider_data:
            for k, v in provider_data.items():
                setattr(self, k, v)
