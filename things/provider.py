
from .provider_assignments_tracker import ProviderAssignmentsTracker
from utils.enums import ProviderEnums


class Provider:

    def __init__(self, hcp_id: int, **kwargs):
        setattr(self, ProviderEnums.Attributes.HCP_ID.value, hcp_id)

        self.assignments_tracker = ProviderAssignmentsTracker()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def fetch_assignments(self, year: int, worksite_ids=None):
        assignments = self.assignments_tracker.fetch_assignments(year=year)

        if worksite_ids:
            assignments = [
                assignment for assignment in assignments if assignment.worksite_id in worksite_ids
            ]

        return assignments

    def determine_fte(self, year: int):
        assignments = self.assignments_tracker.fetch_assignments(year=year)

        if any([getattr(assignment, ProviderEnums.AssignmentAttributes.FTE.value) == ProviderEnums.Fte.FULL_TIME.value]
                for assignment in assignments):
            return ProviderEnums.Fte.FULL_TIME.value
        else:
            return ProviderEnums.Fte.PART_TIME.value
