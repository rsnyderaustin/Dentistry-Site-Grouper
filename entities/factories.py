
from .objects import Organization, Provider, Worksite
from algo.worksite_node import WorksiteNode
from column_enums import ProviderDataColumns
from column_enums import WorksiteDataColumns


def create_organizations(worksite_nodes: set[WorksiteNode], valid_worksite_ids):
    ult_parent_nodes = {node for node in worksite_nodes if node.is_ultimate_parent}
    valid_ult_parents = {ult_parent_node for ult_parent_node in ult_parent_nodes
                         if any({ult_parent_node.has_child(valid_id) for valid_id in valid_worksite_ids})}
    ult_parent_worksites = {Worksite(worksite_id=ult_parent_node.worksite_id,
                                     parent_id=ult_parent_node.worksite_id) for ult_parent_node in valid_ult_parents}
    orgs = {Organization(ult_parent_worksite) for ult_parent_worksite in ult_parent_worksites}
    return orgs


def apply_create_worksite(row, worksites, worksite_cols: list = None):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]

    worksite_data = {col: row[col] for col in worksite_cols}

    if worksite_id not in worksites:
        worksites[worksite_id] = Worksite(worksite_id=worksite_id,
                                          parent_id=parent_id,
                                          worksite_data=worksite_data)


def apply_create_provider(row, providers, provider_cols: list = None):
    hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
    provider_data = {col: row[col] for col in provider_cols} if provider_cols else {}
    if hcp_id not in providers:
        provider = Provider(hcp_id=hcp_id,
                            provider_data=provider_data)
        providers[hcp_id] = provider
