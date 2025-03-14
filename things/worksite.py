
from .provider_assignment import ProviderAssignment
from .provider_assignments_tracker import ProviderAssignmentsTracker
from utils.enums import WorksiteEnums


class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, **kwargs):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        self.organization_id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.child_worksites = dict()
        self.provider_assignments_tracker = ProviderAssignmentsTracker()

    def __hash__(self):
        return hash(self.worksite_id)

    def fetch_provider_assignments(self, year: int = None):
        return self.provider_assignments_tracker.fetch_assignments(year=year)

    def add_provider_assignment(self, year: int, provider_assignment: ProviderAssignment):
        self.provider_assignments_tracker.add_assignment(year=year,
                                                         assignment=provider_assignment)
