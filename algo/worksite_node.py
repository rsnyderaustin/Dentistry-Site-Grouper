

class WorksiteNode:

    def __init__(self, worksite_id: int, parent_id: int):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        self.child_nodes = set()

    @property
    def is_ultimate_parent(self):
        return self.worksite_id == self.parent_id

    def has_child(self, worksite_id):
        if self.worksite_id == worksite_id:
            return True

        for child_node in self.child_nodes:
            if child_node.has_child(worksite_id):
                return True

        return False
