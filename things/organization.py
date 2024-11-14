from .worksite import Worksite
from .provider_assignment import ProviderAssignment


class Organization:

    def __init__(self, ult_parent_worksite: Worksite):
        self.ult_parent_worksite = ult_parent_worksite

        self.worksites = {
            self.ult_parent_worksite.worksiteid: self.ult_parent_worksite
        }
        self.providers = set()
        self.provider_assignments = set()

    def add_worksite(self, parent: Worksite, worksite: Worksite):
        current_parent = parent
        while current_parent != self.ult_parent_worksite:
            current_parent.child_worksites[worksite.worksiteid] = worksite
            current_parent = self.worksites[current_parent.parentid]

        self.worksites[worksite.worksiteid] = worksite

    def add_provider_assignment(self, worksite: Worksite, provider_assignment: ProviderAssignment):
        if worksite.worksiteid not in self.worksites:
            raise KeyError(f"Attempted to add provider assignment to worksite with Worksite ID {worksite.worksiteid},"
                           f"when that Worksite ID is not present in this Organization's worksites.")
        self.provider_assignments.add(provider_assignment)

        worksite = self.worksites[worksite.worksiteid]
        worksite.add_provider_assignment(provider_assignment)

    def has_which_worksites(self, worksite_ids):
        has_worksites = {worksite for worksite in self.worksites.values() if worksite.worksiteid in worksite_ids}
        return has_worksites

