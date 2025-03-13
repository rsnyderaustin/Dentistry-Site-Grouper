
import logging
import pandas as pd

from things import Organization
from utils.enums import WorksiteEnums


def create_organizations(worksites_dataframe: pd.DataFrame, worksites_by_id: dict) -> dict:
    # Fill repository with worksites and organizations
    logging.info("Starting to fill repository with worksites and organizations.")

    worksite_ids = worksites_dataframe[WorksiteEnums.Attributes.WORKSITE_ID.value]
    parent_ids = worksites_dataframe[WorksiteEnums.Attributes.PARENT_ID.value]

    child_to_parent_ids = {
        worksite_id: parent_id for worksite_id, parent_id in zip(worksite_ids, parent_ids)
    }

    ultimate_parent_ids = set(worksite_id for worksite_id, parent_id in zip(worksite_ids, parent_ids)
                              if worksite_id == parent_id)

    child_ids = set(worksite_id for worksite_id in worksite_ids if worksite_id not in ultimate_parent_ids)

    # Track unplaced children so we know what still needs to be placed in an organization. Track placed child ids
    # so that we know which parents have been placed
    unplaced_child_ids = child_ids.copy()
    worksite_id_to_organization = {
        worksite_id: Organization(ultimate_parent_worksite=worksites_by_id[worksite_id])
        for worksite_id in ultimate_parent_ids
    }
    
    while len(unplaced_child_ids) > 0:
        for worksite_id in unplaced_child_ids:
            parent_id = child_to_parent_ids[worksite_id]
            if parent_id not in placed_child_ids:
                continue

            organization =


    relationships = [
        HierarchyRelationship(worksite_id=worksite_id,
                              parent_id=parent_id)
        for worksite_id, parent_id in zip(worksite_ids, parent_ids)
    ]
    missing_parent_worksites = [parent_id for parent_id in set(parent_ids) if parent_id not in set(worksite_ids)]

    hierarchy_relations_manager = HierarchyRelationsManager(relationships=relationships)

    for relation in self.worksite_parent_relations.relationships:

        if relation.worksite_id not in self.repository.worksites:
            worksite_rows = worksites_dataframe.query(
                f"{WorksiteEnums.Attributes.WORKSITE_ID.value} == {relation.worksite_id}")
            worksite_row = worksite_rows.iloc[0]
            worksite_data = {col_enum.value: worksite_row[col_enum.value] for col_enum in self.required_cols.worksite_columns}
            new_worksite = Worksite(worksite_id=relation.worksite_id,
                                    parent_id=relation.parent_id,
                                    **worksite_data)
            self.repository.worksites[relation.worksite_id] = new_worksite

            if relation.parent_id == relation.worksite_id and relation.worksite_id not in self.repository.organizations:
                new_org = Organization(ult_parent_worksite=new_worksite)
                self.repository.organizations[relation.worksite_id] = new_org
    logging.info("Finished filling repository.")

    # Add worksites to organizations
    non_ult_parent_worksites = set(worksite for worksite in self.repository.worksites.values()
                                   if worksite.worksite_id != worksite.parent_id)
    loops = 0
    while len(non_ult_parent_worksites) > 0:
        logging.info(f"Loop number {loops}")
        added_worksites = set()
        for org in self.repository.organizations.values():
            for worksite in non_ult_parent_worksites:
                parent_worksite_id = self.worksite_parent_relations.get_parent_id(worksite.worksite_id)
                if parent_worksite_id in org.worksites_by_id:
                    org.add_worksite(worksite=worksite,
                                     parent=self.repository.worksites[parent_worksite_id])
                    added_worksites.add(worksite)
        for worksite in added_worksites:
            non_ult_parent_worksites.remove(worksite)

        loops += 1

    # Fill worksite_id_to_ultimate_parent_id dict
    for ult_parent_id, org in self.repository.organizations.items():
        for worksite in org.worksites_by_id.values():
            self.worksite_id_to_ultimate_parent_id[worksite.worksite_id] = ult_parent_id

    self.organizations_loaded = True
    
    
    