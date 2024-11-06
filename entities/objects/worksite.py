

class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, **params):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        for k, v in params.items():
            setattr(self, k, v)

        self._child_worksites = set()
        self._providers = set()

    def add_child_worksites(self, worksites):
        for worksite in worksites:
            if worksite.worksite_id == self.worksite_id:
                continue

            self._child_worksites.add(worksite)

    def has_worksite(self, worksite_id):
        return worksite_id == self.worksite_id or worksite_id in self._child_worksites

    @property
    def is_ultimate_parent(self):
        return self.worksite_id == self.parent_id
