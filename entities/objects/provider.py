
class WorksiteAssignment:

    def __init__(self, worksite_id, worksite_data, provider_data):
        self.worksite_id = worksite_id
        self.worksite_data = worksite_data
        self.provider_data = provider_data

class Provider:

    def __init__(self, hcp_id: int, extra_data: dict = None):
        self.hcp_id = hcp_id

        self.worksite_assignments = {}

        if extra_data:
            for k, v in extra_data.items():
                setattr(self, k, [v])

    def add_worksite_data(self, worksite_id: int, data: dict):
        if worksite_id in self.worksite_assignments:
            self.worksite_assignments
        for k, v in data:
            getattr(self, k).



