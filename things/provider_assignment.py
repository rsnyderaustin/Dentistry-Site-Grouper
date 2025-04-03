

class ProviderAssignment:

    def __init__(self, worksite, provider, assignment_data: dict, worksite_type: str, activity: str, fte: str):
        self.worksite = worksite
        self.provider = provider
        self.assignment_data = assignment_data
        self.worksite_type = worksite_type
        self.activity = activity
        self.fte = fte

