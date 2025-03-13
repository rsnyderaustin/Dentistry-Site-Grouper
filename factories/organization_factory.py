
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
    # The dict is just the ultimate parent ID's as keys and the associated Organization as a value, so we can copy it
    # now to return later
    organizations_by_ultimate_parent_id = worksite_id_to_organization.copy()

    loop = 0
    while len(unplaced_child_ids) > 0:
        placed_child_ids = set()
        logging.info(f"Loop {loop}")
        for worksite_id in unplaced_child_ids:
            parent_id = child_to_parent_ids[worksite_id]

            # Check if we've placed the parent at an organization yet
            if parent_id not in worksite_id_to_organization:
                continue

            organization = worksite_id_to_organization[parent_id]
            organization.add_worksite(
                worksite=worksites_by_id[worksite_id]
            )

            worksite_id_to_organization[worksite_id] = organization
            placed_child_ids.add(worksite_id)

        unplaced_child_ids -= placed_child_ids
        loop += 1

    return organizations_by_ultimate_parent_id

    
    
    