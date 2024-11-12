from entities.objects.worksite import Worksite


class Organization:

    def __init__(self, ult_parent_worksite: Worksite):
        self.ult_parent_worksite = ult_parent_worksite

        self.worksites = {
            self.ult_parent_worksite.worksite_id: self.ult_parent_worksite
        }

    def add_worksite(self, parent: Worksite, worksite: Worksite):
        current_parent = parent
        while current_parent != self.ult_parent_worksite:
            current_parent.child_worksites[worksite.worksite_id] = worksite
            current_parent = self.worksites[current_parent.parent_id]

        self.worksites[worksite.worksite_id] = worksite

    def has_one_of_worksite_ids(self, worksite_ids):
        return any({worksite_id in self.worksites for worksite_id in worksite_ids})

    @property
    def all_provider_assignments(self):
        provider_assignments = set()
        for worksite_id, worksite in self.worksites.items():
            provider_assignments.update(worksite.provider_assignments)
        return provider_assignments

