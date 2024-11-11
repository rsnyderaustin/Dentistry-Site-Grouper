from column_enums import ProviderDataColumns


class ProviderAssignment:

    def __init__(self, provider, assignment_data: dict = None):
        self.provider = provider
        self.assignment_data = assignment_data

        for k, v in provider.__dict__.items():
            setattr(self, k, v)

        for k, v in assignment_data.items():
            setattr(self, k, v)


class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, worksite_data: dict = None):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        if worksite_data:
            for k, v in worksite_data.items():
                setattr(self, k, v)

        self.child_worksites = {}
        self.provider_assignments = {}

    def add_child_worksites(self, child_worksites):
        for child_worksite in child_worksites:
            if child_worksite.worksite_id == self.worksite_id:
                continue

            self.child_worksites[child_worksite.worksite_id] = child_worksite

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
            if worksite.has_one_of_child(worksite_ids):
                return True

        return False

    def add_provider_assignment(self, provider, assignment_data):
        provider_id = getattr(provider, ProviderDataColumns.PROVIDER_ID.value)
        self.provider_assignments[provider_id] = ProviderAssignment(provider,
                                                                    assignment_data)

    def _get_number_of_child_worksites_recursive(self, num_children=0):
        if len(self.child_worksites) == 0:
            return num_children

        for child_worksite_id, child_worksite in self.child_worksites.items():
            num_children += 1
            num_children = child_worksite._get_number_of_child_worksites_recursive(num_children)

        return num_children

    @property
    def number_of_child_worksites(self):
        return self._get_number_of_child_worksites_recursive()

    @property
    def all_child_worksites(self):
        child_worksites = set()

        for worksite in self.child_worksites.values():
            child_worksites.add(worksite)
            child_worksites.update(worksite.all_child_worksites)

        return child_worksites

    def get_all_data(self, col, data: list):
        provider_data = [getattr(prov_assign, col) for prov_assign in self.provider_assignments.values()]
        data.extend(provider_data)
        for child_worksite in self.child_worksites.values():
            child_worksite.get_all_data(col=col,
                                        data=data)

        return data
