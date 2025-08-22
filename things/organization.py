
from .worksite import Worksite


class Organization:

    def __init__(self, ultimate_parent_worksite: Worksite):
        self.ultimate_parent_worksite = ultimate_parent_worksite

        self.worksites_by_id = {
            ultimate_parent_worksite.worksite_id: ultimate_parent_worksite
        }

    @property
    def worksites(self):
        return set(self.worksites_by_id.values())

    @property
    def ultimate_parent_worksite_id(self):
        return self.ultimate_parent_worksite.worksite_id

    def determine_number_of_dentists(self, year: int):
        provider_assignments = [assignment for worksite in self.worksites for assignment in worksite.fetch_provider_assignments(year=year)]
        providers = set(assignment.provider for assignment in provider_assignments)
        return len(providers)

    def add_worksite(self, worksite: Worksite):
        self.worksites_by_id[worksite.worksite_id] = worksite

    def fetch_worksites(self, year: int) -> set[Worksite]:
        assignments = self.fetch_provider_assignments(year=year)
        return {assignment.worksite for assignment in assignments}

    def fetch_worksite_attributes(self, year: int, attribute):
        worksites = self.fetch_worksites(year=year)
        return [getattr(ws, attribute) for ws in worksites]

    def fetch_provider_assignments(self, year: int = None) -> list['ProviderAssignment']:
        return [assignment for worksite in self.worksites for assignment in worksite.fetch_provider_assignments(year=year)]




