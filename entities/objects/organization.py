from entities.objects.worksite import Worksite


class Organization:

    def __init__(self, ult_parent_id: int, **params):
        self.ult_parent_id = ult_parent_id

        for k, v in params.items():
            setattr(self, k, v)

        self.worksites = {}

    def worksite_belongs_to_org(self, worksite: Worksite):
        return worksite.parent_id in self.worksites.keys()

    def add_worksite(self, worksite):
        self.worksites[worksite.worksite_id] = worksite

