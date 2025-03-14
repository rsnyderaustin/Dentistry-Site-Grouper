from .worksite import Worksite


class Organization:

    def __init__(self, ultimate_parent_worksite: Worksite):
        self.ultimate_parent_worksite = ultimate_parent_worksite

        self.worksites_by_id = {
            ultimate_parent_worksite.worksite_id: ultimate_parent_worksite
        }

    @property
    def worksites(self):
        return list(self.worksites_by_id.values())

    @property
    def ultimate_parent_worksite_id(self):
        return self.ultimate_parent_worksite.worksite_id

    def determine_number_of_dentists(self, year: int):
        provider_assignments = [assignment for worksite in self.worksites for assignment in worksite.fetch_provider_assignments(year=year)]
        providers = set(assignment.provider for assignment in provider_assignments)
        return len(providers)

    def add_worksite(self, worksite: Worksite):
        self.worksites_by_id[worksite.worksite_id] = worksite

    def fetch_provider_assignments(self, year: int = None) -> list:
        return [assignment for worksite in self.worksites_by_id.values() for assignment in worksite.fetch_provider_assignments(year=year)]




