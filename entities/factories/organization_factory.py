
from ..objects import Organization, Worksite
from algo.worksite_node import WorksiteNode


def create_organizations(worksite_nodes: set[WorksiteNode], valid_worksite_ids):
    ult_parent_nodes = {node for node in worksite_nodes if node.is_ultimate_parent}
    valid_ult_parents = {ult_parent_node for ult_parent_node in ult_parent_nodes
                         if any({ult_parent_node.has_child(valid_id) for valid_id in valid_worksite_ids})}
    ult_parent_worksites = {Worksite(worksite_id=ult_parent_node.worksite_id,
                                     parent_id=ult_parent_node.worksite_id) for ult_parent_node in valid_ult_parents}
    orgs = {Organization(ult_parent_worksite) for ult_parent_worksite in ult_parent_worksites}
    return orgs


