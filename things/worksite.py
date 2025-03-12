
from utils.enums import ProviderEnums


class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, **kwargs):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        self.organization_id = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.child_worksites = dict()
        self.provider_assignments = set()

    @property
    def provider_specialties(self):
        return {getattr(prov_assign, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value) for prov_assign in self.provider_assignments}

    def add_provider_assignment(self, provider_assignment):
        self.provider_assignments.add(provider_assignment)

    def has_child(self, worksite_id):
        if self.worksite_id == worksite_id:
            return True

        for worksite_id, worksite in self.child_worksites.items():
            if worksite.has_child(worksite_id):
                return True

        return False

    def has_one_of_child(self, worksite_ids):
        if self.worksite_id in worksite_ids:
            return True

        for worksite_id, worksite in self.child_worksites.items():
            if worksite.has_one_of_child([worksite_ids]):
                return True

        return False

    def get_all_data(self, col, data: list):
        provider_data = [getattr(prov_assign, col) for prov_assign in self.provider_assignments]
        data.extend(provider_data)
        for child_worksite in self.child_worksites.values():
            child_worksite.get_all_data(col=col,
                                        data=data)

        return data
