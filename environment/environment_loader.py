import logging
import pandas as pd

from things import Organization, Provider, ProviderAssignment, Worksite
from utils import ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums
from .environment import Environment


def _apply_create_worksites(row,
                            required_cols: RequiredEntitiesColumns,
                            worksites_by_id: dict):
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
    parent_id = row[WorksiteEnums.Attributes.PARENT_ID.value]

    worksite_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.worksite_columns}
    if worksite_id not in worksites_by_id:
        worksite = Worksite(worksite_id=worksite_id,
                            parent_id=parent_id,
                            **worksite_data)
        worksites_by_id[worksite_id] = worksite


def _apply_create_providers(row,
                            required_cols: RequiredEntitiesColumns,
                            worksites_by_id: dict,
                            providers_by_id: dict):
    year = row[ProgramColumns.YEAR.value]
    hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]

    provider_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_columns}
    if hcp_id not in providers_by_id:
        provider = Provider(hcp_id=hcp_id,
                            **provider_data)
        providers_by_id[hcp_id] = provider

    provider = providers_by_id[hcp_id]
    worksite = worksites_by_id[worksite_id]

    assignment_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_at_worksite_columns}

    provider_assignment = ProviderAssignment(
        worksite=worksite,
        provider=provider,
        assignment_data=assignment_data
    )

    provider.add_assignment(
        year=year,
        assignment=provider_assignment
    )

    worksite.add_provider_assignment(
        year=year,
        provider_assignment=provider_assignment
    )


def _create_organizations(worksites_dataframe: pd.DataFrame, worksites_by_id: dict, organizations_by_id: dict):
    """

    :param worksites_dataframe:
    :param worksites_by_id:
    :return:
    """

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

    # Create all Organizations
    worksite_id_to_organization = {
        worksite_id: Organization(ultimate_parent_worksite=worksites_by_id[worksite_id])
        for worksite_id in ultimate_parent_ids
    }

    for ultimate_id, organization in worksite_id_to_organization.items():
        organizations_by_id[ultimate_id] = organization

    loop = 0
    while len(unplaced_child_ids) > 0:
        placed_child_ids = set()
        logging.info(f"Loop {loop}")
        for worksite_id in unplaced_child_ids:
            worksite = worksites_by_id[worksite_id]
            # If there is a child worksite with no provider history, then just skip it and add it to placed_child_ids to be removed
            # from the list of ID's
            if not worksite.fetch_provider_assignments():
                placed_child_ids.add(worksite_id)
                continue

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


class EnvironmentLoader:

    def __init__(self,
                 worksites_df,
                 year_end_df,
                 required_cols: RequiredEntitiesColumns
                 ):
        self.worksites_df = worksites_df
        self.year_end_df = year_end_df
        self.required_cols = required_cols

        self.env = Environment()

        self.worksite_id_to_ultimate_parent_id = {}

        self.organizations_loaded = False

    def load_environment(self) -> Environment:
        self.worksites_df.apply(_apply_create_worksites,
                                required_cols=self.required_cols,
                                worksites_by_id=self.env.worksites_by_id,
                                axis=1)

        self.year_end_df.apply(_apply_create_providers,
                               required_cols=self.required_cols,
                               worksites_by_id=self.env.worksites_by_id,
                               providers_by_id=self.env.providers_by_id,
                               axis=1)

        _create_organizations(
            worksites_dataframe=self.worksites_df,
            worksites_by_id=self.env.worksites_by_id,
            organizations_by_id=self.env.organizations_by_id
        )

        # Filter organizations to only those with at least one provider in history
        self.env.organizations_by_id = {
            ultimate_parent_id: organization for ultimate_parent_id, organization in self.env.organizations_by_id.items()
            if organization.fetch_provider_assignments()
        }

        return self.env
