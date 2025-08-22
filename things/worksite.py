from .provider_assignment import ProviderAssignment
from .provider_assignments_tracker import ProviderAssignmentsTracker
from utils.enums import ProviderEnums


class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, **kwargs):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        self.organization_id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.provider_assignments_tracker = ProviderAssignmentsTracker()

    def __hash__(self):
        return hash(self.worksite_id)

    def fetch_worksite_size(self, year: int, primary_only: bool = False):
        year_assignments = self.provider_assignments_tracker.fetch_assignments(year=year)

        if primary_only:
            year_assignments = [assignment for assignment in year_assignments
                                if getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value) == ProviderEnums.WorksiteType.PRIMARY.value]

        year_providers = {assignment.provider for assignment in year_assignments}
        return len(year_providers)

    def fetch_provider_assignments(self, year: int = None):
        return self.provider_assignments_tracker.fetch_assignments(year=year)

    def add_provider_assignment(self, year: int, provider_assignment: ProviderAssignment):
        self.provider_assignments_tracker.add_assignment(year=year,
                                                         assignment=provider_assignment)

    def fetch_provider_specialties(self, year: int):
        assignments = self.fetch_provider_assignments(year=year)
        return {getattr(assignment, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value)
                for assignment in assignments}

    def is_staffed_full_time(self, year: int) -> bool:
        assignments = self.fetch_provider_assignments(year=year)
        hours = sum([
            getattr(assignment, ProviderEnums.AssignmentAttributes.WK_HOURS.value)
            for assignment in assignments
        ])
        weeks = sum([
            getattr(assignment, ProviderEnums.AssignmentAttributes.WK_WEEKS.value)
            for assignment in assignments
        ])

        return hours * weeks >= 32 * 48
