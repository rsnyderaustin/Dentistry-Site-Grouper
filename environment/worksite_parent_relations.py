

class Relationship:

    def __init__(self, worksite_id, parent_id):
        self.worksite_id = worksite_id
        self.parent_id = parent_id


class WorksiteParentRelations:

    def __init__(self, child_parent_tuples):
        self.relationships = {Relationship(worksite_id=tup[0], parent_id=tup[1]) for tup in child_parent_tuples}

        self._ultimate_parent_ids = set(tup[0] for tup in child_parent_tuples if tup[0] == tup[1])
        self._child_to_parent = {}
        self._parent_to_children = {}

        self._create_relations(child_parent_tuples)

    def _create_relations(self, child_parent_tuples):
        for tup in child_parent_tuples:
            worksite_id = tup[0]
            parent_id = tup[1]
            if worksite_id not in self._child_to_parent:
                self._child_to_parent[worksite_id] = parent_id

            if worksite_id not in self._ultimate_parent_ids:  # Parents are not their own children
                if parent_id not in self._parent_to_children:
                    self._parent_to_children[parent_id] = set()
                self._parent_to_children[parent_id].add(worksite_id)

    def get_worksite_ids(self, parent_id: int):
        return self._parent_to_children[parent_id]

    def get_parent_id(self, worksite_id: int):
        if worksite_id in self._ultimate_parent_ids:
            return worksite_id

        return self._child_to_parent[worksite_id]




