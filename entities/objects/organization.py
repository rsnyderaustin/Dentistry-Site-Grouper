from entities.objects.worksite import Worksite


class Organization:

    def __init__(self, ult_parent_worksite: Worksite, **params):
        self.ult_parent_worksite = ult_parent_worksite

        for k, v in params.items():
            setattr(self, k, v)

        self.worksites = {}

    def add_worksite(self, worksite):
        self.worksites[worksite.worksite_id] = worksite

