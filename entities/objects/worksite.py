
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

    def add_data(self, data: dict):
        for k, v in data.items():
            if not hasattr(self, k):
                setattr(self, k, v)
            else:
                current_val = getattr(self, k)
                if not isinstance(current_val, list):
                    setattr(self, k, list(current_val))
                getattr(self, k).append(v)

    @property
    def is_ultimate_parent(self):
        return self.worksite_id == self.parent_id

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
