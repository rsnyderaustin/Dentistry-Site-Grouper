

class WorksiteParentRelations:

    def __init__(self, child_parent_tuples):
        self.child_parent_tuples = child_parent_tuples

        self.ultimate_parent_ids = set(tup[0] for tup in child_parent_tuples if tup[0] == tup[1])
        self.child_to_parent = {}
        self.parent_to_children = {}

        self.create_relations()

    def create_relations(self):
        for tup in self.child_parent_tuples:
            worksite_id = tup[0]
            parent_id = tup[1]
            if worksite_id not in self.child_to_parent:
                self.child_to_parent[worksite_id] = parent_id

            if worksite_id not in self.ultimate_parent_ids:  # Parents are not their own children
                if parent_id not in self.parent_to_children:
                    self.parent_to_children[parent_id] = set()
                self.parent_to_children[parent_id].add(worksite_id)

    def get_worksite_ids(self, parent_id: int):
        return self.parent_to_children[parent_id]

    def get_parent_id(self, worksite_id: int):
        if worksite_id in self.ultimate_parent_ids:
            return worksite_id

        return self.child_to_parent[worksite_id]




