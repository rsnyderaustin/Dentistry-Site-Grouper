from .worksite_node import WorksiteNode


class HierarchyAlgo:

    def __init__(self, child_parent_tuples: set[tuple]):
        self.nodes = {WorksiteNode(tup[0], tup[1]) for tup in child_parent_tuples}
        self.worksite_nodes = {
            'non_ultimate': {node for node in self.nodes if not node.is_ultimate_parent},
            'ultimate': {node for node in self.nodes if node.is_ultimate_parent}
        }

    def _create_hierarchy_recursive(self, parent_nodes):
        new_child_nodes = set()

        no_children_found = True
        for parent_node in parent_nodes:
            children_nodes = {node for node in self.worksite_nodes['non_ultimate']
                              if node.parent_id == parent_node.worksite_id}

            if len(children_nodes) == 0:
                continue

            no_children_found = False
            parent_node.child_nodes.update(children_nodes)
            new_child_nodes.update(children_nodes)

        if no_children_found:
            return

        self._create_hierarchy_recursive(parent_nodes=new_child_nodes)

    def create_hierarchy(self):
        self._create_hierarchy_recursive(parent_nodes=self.worksite_nodes['ultimate'])
        return self.nodes


