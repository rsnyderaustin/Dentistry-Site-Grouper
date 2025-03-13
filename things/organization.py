from .worksite import Worksite
from .provider_assignment import ProviderAssignment


class Organization:

    def __init__(self, ultimate_parent_worksite: Worksite):
        self.ultimate_parent_worksite = ultimate_parent_worksite

        self.worksites_by_id = dict()
        self.providers_by_id = dict()

    def determine_number_of_dentists(self, year: int):
        providers = set()
        for provider in self.providers_by_id.values():
            assignments = provider.fetch_assignments(year=year, worksite_ids=self.worksites_by_id.keys())
            if assignments:
                providers.add(provider)

        return len(providers)

    @property
    def ultimate_parent_worksite_id(self):
        return self.ultimate_parent_worksite.worksite_id

    @property
    def worksites(self):
        return list(self.worksites_by_id.values())

    def add_worksite(self, worksite: Worksite):
        self.worksites_by_id[worksite.worksite_id] = worksite





