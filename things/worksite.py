
from .provider_assignment import ProviderAssignment
from .provider_assignments_tracker import ProviderAssignmentsTracker
from utils.enums import ProviderEnums, WorksiteEnums


class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, active_status: WorksiteEnums.Status, **kwargs):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        self.active_status = active_status

        self.organization_id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.child_worksites = dict()
        self.provider_assignments_tracker = ProviderAssignmentsTracker()

    def fetch_provider_specialties(self, year: int):
        provider_assignments = self.provider_assignments_tracker.fetch_assignments(year=year)
        return {getattr(prov_assign, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value) for prov_assign in provider_assignments}

    def add_provider_assignment(self, year: int, provider_assignment: ProviderAssignment):
        self.provider_assignments_tracker.add_assignment(year=year,
                                                         assignment=provider_assignment)
