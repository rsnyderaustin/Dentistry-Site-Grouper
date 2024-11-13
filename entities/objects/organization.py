from entities.objects.worksite import Worksite
from entities.provider_assignment import ProviderAssignment


class Organization:

    def __init__(self, ult_parent_worksite: Worksite, org_id: int):
        self.ult_parent_worksite = ult_parent_worksite
        self.org_id = org_id

        self.worksites = {
            self.ult_parent_worksite.worksite_id: self.ult_parent_worksite
        }
        self.provider_assignments = set()

    def add_worksite(self, parent: Worksite, worksite: Worksite):
        current_parent = parent
        while current_parent != self.ult_parent_worksite:
            current_parent.child_worksites[worksite.worksite_id] = worksite
            current_parent = self.worksites[current_parent.parent_id]

        self.worksites[worksite.worksite_id] = worksite

    def add_provider_assignment(self, worksite: Worksite, provider_assignment: ProviderAssignment):
        if worksite.worksite_id not in self.worksites:
            raise KeyError(f"Attempted to add provider assignment to worksite with Worksite ID {worksite.worksite_id},"
                           f"when that Worksite ID is not present in this Organization's worksites.")

        worksite = self.worksites[worksite.worksite_id]
        worksite.add_provider_assignment(provider_assignment)

    def has_one_of_worksite_ids(self, worksite_ids):
        return any({worksite_id in self.worksites for worksite_id in worksite_ids})

    def all_provider_assignments(self):
        return self.provider_assignments

