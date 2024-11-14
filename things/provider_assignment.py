from .provider import Provider
from .worksite import Worksite


class ProviderAssignment:

    def __init__(self, provider: Provider, worksite: Worksite, assignment_data: dict = None):
        self.provider = provider
        self.worksite = worksite
        self.assignment_data = assignment_data

        for k, v in assignment_data.items():
            setattr(self, k, v)

