

class ProviderAssignment:

    def __init__(self, worksite, provider, **kwargs):
        self.worksite = worksite
        self.provider = provider

        for k, v in kwargs.items():
            setattr(self, k, v)