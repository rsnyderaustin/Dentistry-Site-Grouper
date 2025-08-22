import logging
import pandas as pd

from things import Organization, Provider, ProviderAssignment, Worksite
from utils import ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums
from .environment import Environment


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

    def _apply_create_worksites(self,
                                row):
        worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
        parent_id = row[WorksiteEnums.Attributes.PARENT_ID.value]

        worksite_data = {col_enum.value: row[col_enum.value] for col_enum in self.required_cols.worksite_columns}
        if worksite_id not in self.env.worksites_by_id:
            worksite = Worksite(worksite_id=worksite_id,
                                parent_id=parent_id,
                                **worksite_data)
            self.env.worksites_by_id[worksite_id] = worksite

    def _apply_create_providers(self,
                                row):
        hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
        year = row[ProgramColumns.YEAR.value]

        provider_data = {col_enum.value: row[col_enum.value] for col_enum in self.required_cols.provider_columns}

        # Handle AGE if it's in the required columns
        age = None
        if ProviderEnums.Attributes.AGE in self.required_cols.provider_columns:
            age = provider_data.pop(ProviderEnums.Attributes.AGE.value)
            year = row[ProgramColumns.YEAR.value]

        # Create or retrieve the provider
        provider = self.env.providers_by_id.get(hcp_id)
        if not provider:
            provider = Provider(hcp_id=hcp_id, **provider_data)
            self.env.providers_by_id[hcp_id] = provider

        # Set the age if applicable
        if age is not None:
            provider.set_age(age=age, year=year)

    def _apply_fill_worksite_provider_assignments(self, row):
        year = row[ProgramColumns.YEAR.value]
        hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
        worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
        worksite_type = row[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
        activity = row[ProviderEnums.AssignmentAttributes.ACTIVITY.value]

        provider = self.env.providers_by_id[hcp_id]
        worksite = self.env.worksites_by_id[worksite_id]

        assignment_data = {col_enum.value: row[col_enum.value] for col_enum in self.required_cols.provider_at_worksite_columns}

        provider_assignment = ProviderAssignment(
            worksite=worksite,
            provider=provider,
            assignment_data=assignment_data,
            worksite_type=worksite_type,
            activity=activity
        )

        provider.add_assignment(
            year=year,
            assignment=provider_assignment
        )

        worksite.add_provider_assignment(
            year=year,
            provider_assignment=provider_assignment
        )

    def _create_organizations(self, worksites_dataframe: pd.DataFrame):
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
        logging.info(f"There are {len(ultimate_parent_ids)} worksites that have the same worksite ID as their parent ID.")

        child_ids = set(worksite_id for worksite_id in worksite_ids if worksite_id not in ultimate_parent_ids)
        logging.info(f"There are {len(child_ids)} worksites that do not have the same worksite ID as their parent ID.")

        # Track unplaced children so we know what still needs to be placed in an organization. Track placed child ids
        # so that we know which parents have been placed
        unplaced_child_ids = child_ids.copy()

        # Create all Organizations
        worksite_id_to_organization = {
            worksite_id: Organization(ultimate_parent_worksite=self.env.worksites_by_id[worksite_id])
            for worksite_id in ultimate_parent_ids
        }

        for ultimate_id, organization in worksite_id_to_organization.items():
            self.env.organizations_by_id[ultimate_id] = organization

        loop = 0
        while len(unplaced_child_ids) > 0:
            placed_child_ids = set()
            logging.info(f"Loop {loop}")
            for worksite_id in unplaced_child_ids:
                worksite = self.env.worksites_by_id[worksite_id]

                parent_id = child_to_parent_ids[worksite_id]

                # Check if we've placed the parent at an organization yet
                if parent_id not in worksite_id_to_organization:
                    continue

                organization = worksite_id_to_organization[parent_id]

                # We only add the worksite to the organization if it actually has providers
                if worksite.fetch_provider_assignments():
                    organization.add_worksite(
                        worksite=self.env.worksites_by_id[worksite_id]
                    )

                worksite_id_to_organization[worksite_id] = organization
                placed_child_ids.add(worksite_id)

            logging.info(f"Placed {len(child_ids) - len(unplaced_child_ids)} of {len(child_ids)} child worksites into an organization. ")
            unplaced_child_ids -= placed_child_ids
            loop += 1

    def load_environment(self) -> Environment:
        worksites_with_hcps = set(self.year_end_df[WorksiteEnums.Attributes.WORKSITE_ID.value].unique())
        logging.info(f"There are {len(worksites_with_hcps)} worksites that have a provider in the source data.")
        logging.info(f"There are {len(self.worksites_df[WorksiteEnums.Attributes.WORKSITE_ID.value].unique())} distinct worksite ID's in the source data.")
        self.worksites_df.apply(self._apply_create_worksites,
                                axis=1)
        logging.info(f"Created {len(self.env.worksites_by_id.values())} worksites.")

        logging.info(f"There are {len(self.year_end_df[ProviderEnums.Attributes.HCP_ID.value].unique())} distinct provider ID's in the source data.")
        self.year_end_df.apply(self._apply_create_providers,
                               axis=1)
        logging.info(f"Created {len(self.env.providers_by_id.values())} providers.")

        self.year_end_df.apply(self._apply_fill_worksite_provider_assignments,
                               axis=1)

        self._create_organizations(
            worksites_dataframe=self.worksites_df
        )

        # Filter organizations to only those with at least one provider in history
        organization_ids_to_filter = [
            org.ultimate_parent_worksite.worksite_id
            for org in self.env.organizations_by_id.values() if not org.fetch_provider_assignments()
        ]
        for org_id in organization_ids_to_filter:
            del self.env.organizations_by_id[org_id]

        num_worksites_filtered = sum(
            len(org.worksites)
            for org in self.env.organizations_by_id.values()
            if org.ultimate_parent_worksite_id in self.env.organizations_by_id
        )
        logging.info(f"Filtered out {len(organization_ids_to_filter)} organizations ({num_worksites_filtered} worksites) that did not have any provider history out of "
                     f"{len(self.env.organizations_by_id.keys())} total organizations.")

        return self.env
