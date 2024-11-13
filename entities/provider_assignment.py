

class ProviderAssignment:

    def __init__(self, provider_id, worksite_id, assignment_data: dict = None):
        self.provider_id = provider_id
        self.worksite_id = worksite_id
        self.assignment_data = assignment_data

        for k, v in assignment_data.items():
            setattr(self, k, v)

