from .worksite import Worksite


class WorksiteAssignment:

    def __init__(self, worksite, assignment_data):
        self.worksite_id = worksite.worksite_id
        self.worksite = worksite
        self.assignment_data = assignment_data


class Provider:

    def __init__(self, hcp_id: int, provider_data: dict = None):
        self.hcp_id = hcp_id

        if provider_data:
            for k, v in provider_data.items():
                setattr(self, k, v)

        self.worksite_assignments = {}

    def add_worksite_data(self, worksite: Worksite, assignment_data: dict):
        self.worksite_assignments[worksite.worksite_id] = WorksiteAssignment(worksite=worksite,
                                                                             assignment_data=assignment_data)
