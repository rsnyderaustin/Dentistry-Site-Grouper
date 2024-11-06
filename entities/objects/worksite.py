

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

    def has_child(self, worksite_id):
        if self.worksite_id == worksite_id:
            return True

        for worksite in self._child_worksites:
            if worksite.has_child(worksite_id):
                return True

        return False

    @property
    def is_ultimate_parent(self):
        return self.worksite_id == self.parent_id

    def get_number_of_child_worksites_recursive(self, num_children):
        if len(self._child_worksites) == 0:
            return

        for child_worksite in self._child_worksites:
            num_children += 1
            child_worksite.get_number_of_child_worksites_recursive(num_children)

    @property
    def number_of_child_worksites(self):
        num_children = 0
        self.get_number_of_child_worksites_recursive(num_children=num_children)
        return num_children

