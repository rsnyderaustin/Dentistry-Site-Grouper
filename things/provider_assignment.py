from .provider import Provider
from .worksite import Worksite
from utils.enums import ProviderEnums


class ProviderAssignment:

    def __init__(self, provider: Provider, worksite: Worksite, **kwargs):
        self.provider = provider
        self.worksite = worksite

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def hcp_id(self):
        return getattr(self.provider, ProviderEnums.Attributes.HCP_ID.value)

    def __hash__(self):
        return hash(self.hcp_id)
