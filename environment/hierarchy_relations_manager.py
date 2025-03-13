
from .hierarchy_relationship import HierarchyRelationship


class HierarchyRelationsManager:

    def __init__(self, relationships: list[HierarchyRelationship]):
        self.relationships = relationships

        self._child_to_parent = {}
        self._parent_to_children = {}

        self._fill_dicts()

    @property
    def ultimate_parent_ids(self):
        return set(relationship.parent_id for relationship in self.relationships
                   if relationship.worksite_id == relationship.parent_id)

    def _fill_dicts(self):
        for relation in self.relationships:
            worksite_id = relation.worksite_id
            parent_id = relation.parent_id
            
            if worksite_id not in self._child_to_parent:
                self._child_to_parent[worksite_id] = parent_id

            if worksite_id not in self.ultimate_parent_ids:  # Parents are not their own children
                if parent_id not in self._parent_to_children:
                    self._parent_to_children[parent_id] = set()
                self._parent_to_children[parent_id].add(worksite_id)

    def get_worksite_ids(self, parent_id: int):
        return self._parent_to_children[parent_id]

    def get_parent_id(self, worksite_id: int):
        if worksite_id in self.ultimate_parent_ids:
            return worksite_id

        return self._child_to_parent[worksite_id]




