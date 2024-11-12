from entities.objects.worksite import Worksite


class Organization:

    def __init__(self, ult_parent_worksite: Worksite):
        self.ult_parent_worksite = ult_parent_worksite

    @property
    def number_of_child_worksites(self):
        return self.ult_parent_worksite.number_of_child_worksites

    def has_worksite(self, worksite_id):
        return self.ult_parent_worksite.has_child(worksite_id)

    def has_one_of_worksites(self, worksite_ids):
        return self.ult_parent_worksite.has_one_of_child(worksite_ids)

    def get_provider_data(self, col):
        data = []
        self.ult_parent_worksite.get_all_data(col, data)
        return data

    @property
    def all_worksites(self):
        child_worksites = self.ult_parent_worksite.all_child_worksites
        all_worksites = child_worksites.add(self.ult_parent_worksite)
        return all_worksites

    @property
    def all_provider_assignments(self):
        return self.ult_parent_worksite.all_provider_assignments

