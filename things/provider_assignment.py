from .provider import Provider
from .worksite import Worksite


class ProviderAssignment:

    def __init__(self, provider: Provider, worksite: Worksite, **kwargs):
        self.provider = provider
        self.worksite = worksite

        for k, v in kwargs.items():
            setattr(self, k, v)

