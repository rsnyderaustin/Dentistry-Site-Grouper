from entities import Organization, Worksite


class HierarchyAlgo:

    def __init__(self, worksites: dict):
        self.worksites = worksites
        self.worksite_parent_tuples = {(ws.worksite_id, ws.parent_id) for ws in self.worksites.values()}

    def _create_hierarchy_recursive(self, parent_worksites: set[Worksite]):
        new_worksites = set()

        no_children_found = True
        for parent_worksite in parent_worksites:
            children_ids = {tup[0] for tup in self.worksite_parent_tuples if tup[1] == parent_worksite.worksite_id}
            children_ids = {c_id for c_id in children_ids if c_id != parent_worksite.worksite_id}

            if len(children_ids) == 0:
                continue

            no_children_found = False
            child_worksites = {self.worksites[child_id] for child_id in children_ids}
            parent_worksite.add_child_worksites(child_worksites)
            new_worksites.update(child_worksites)

        if no_children_found:
            return

        self._create_hierarchy_recursive(parent_worksites=new_worksites)

    def create_hierarchy(self):
        ult_parents = {ws for ws_id, ws in self.worksites.items() if ws.is_ultimate_parent}
        self._create_hierarchy_recursive(parent_worksites=ult_parents)
        return ult_parents


class OrganizationCreator:

    def __init__(self, worksites: dict):
        self.worksites = worksites

    def create_organizations(self, relevant_site_ids):
        hierarchy_algo = HierarchyAlgo(worksites=self.worksites)
        ult_parents = hierarchy_algo.create_hierarchy()
        valid_ult_parents = {ult_parent for ult_parent in ult_parents if any({ult_parent.has_worksite(valid_id)
                                                                             for valid_id in relevant_site_ids})}
        orgs = {Organization(ult_parent) for ult_parent in valid_ult_parents}
        return orgs


