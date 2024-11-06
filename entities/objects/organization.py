from entities.objects.worksite import Worksite


class Organization:

    def __init__(self, ult_parent_worksite: Worksite, **params):
        self.ult_parent_worksite = ult_parent_worksite

        for k, v in params.items():
            setattr(self, k, v)

        self.worksites = []

    @property
    def number_of_child_worksites(self):
        return self.ult_parent_worksite.number_of_child_worksites

    def has_worksite(self, worksite_id):
        return self.ult_parent_worksite.has_child(worksite_id)
