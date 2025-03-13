from .worksite import Worksite
from .provider_assignment import ProviderAssignment


class OrganizationAssignments:

    def __init__(self, year: int, assignments_by_worksite: dict):
        self.year = year
        self.assignments_by_worksite = assignments_by_worksite


class Organization:

    def __init__(self, ultimate_parent_worksite: Worksite):
        self.ultimate_parent_worksite = ultimate_parent_worksite

        self.worksites_by_id = dict()
        self.providers_by_id = dict()

    @property
    def ultimate_parent_worksite_id(self):
        return self.ultimate_parent_worksite.worksite_id

    def determine_number_of_dentists(self, year: int):
        providers = set()
        for provider in self.providers_by_id.values():
            assignments = provider.fetch_assignments(year=year, worksite_ids=self.worksites_by_id.keys())
            if assignments:
                providers.add(provider)

        return len(providers)

    def add_worksite(self, worksite: Worksite):
        self.worksites_by_id[worksite.worksite_id] = worksite

    def fetch_assignments(self, year: int) -> OrganizationAssignments:
        assignments_by_worksite = {
            worksite: worksite.fetch_provider_assignments(year=year) for worksite in self.worksites_by_id.values()
        }
        return OrganizationAssignments(year=year,
                                       assignments_by_worksite=assignments_by_worksite)




