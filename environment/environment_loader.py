import copy
import logging
import pandas as pd

import factories
from .hierarchy_relations_manager import HierarchyRelationsManager
from .hierarchy_relationship import HierarchyRelationship
from environment.environment import Environment
from utils.enums import ProgramColumns, ProviderEnums, WorksiteEnums
from things import Organization, Provider, ProviderAssignment, RequiredEntitiesColumns, Worksite
import preprocessing


class EnvironmentLoader:

    def __init__(self,
                 worksites_df,
                 year_end_df,
                 required_cols: RequiredEntitiesColumns
                 ):
        self.worksites_df = worksites_df
        self.year_end_df = year_end_df
        self.required_cols = required_cols

        self.worksites_by_id = dict()
        self.providers_by_id = dict()

        self.worksite_id_to_ultimate_parent_id = {}

        self.organizations_loaded = False

    def load_environment(self):
        self.year_end_df.apply(
            factories.apply_create_entities,
            required_cols=self.required_cols,
            worksites_by_id=self.worksites_by_id,
            providers_by_id=self.providers_by_id
        )

        organizations = factories.create_organizations(
            worksites_dataframe=self.worksites_df,
            worksites_by_id=self.worksites_by_id
        )


    def _load_worksite_data(self, worksite_id):
        worksite_rows = self.worksites_df.query(
            f"{WorksiteEnums.Attributes.WORKSITE_ID.value} == {worksite_id}")
        worksite_row = worksite_rows.iloc[0]
        worksite_data = {col: worksite_row[col] for col in self.required_cols.worksite_columns}
        return worksite_data

    def _load_organizations(self):
        # Fill repository with worksites and organizations
        logging.info("Starting to fill repository with worksites and organizations.")

        worksite_ids = self.worksites_df[WorksiteEnums.Attributes.WORKSITE_ID.value]
        parent_ids = self.worksites_df[WorksiteEnums.Attributes.PARENT_ID.value]

        relationships = [
            HierarchyRelationship(worksite_id=worksite_id,
                                  parent_id=parent_id)
            for worksite_id, parent_id in zip(worksite_ids, parent_ids)
        ]
        missing_parent_worksites = [parent_id for parent_id in set(parent_ids) if parent_id not in set(worksite_ids)]

        hierarchy_relations_manager = HierarchyRelationsManager(relationships=relationships)

        for relation in self.worksite_parent_relations.relationships:

            if relation.worksite_id not in self.repository.worksites:
                worksite_rows = self.worksites_df.query(
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

    def _apply_create_entities(self, row, required_cols: RequiredEntitiesColumns, entities):
        year = row[ProgramColumns.YEAR.value]
        hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
        worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
        parent_id = row[WorksiteEnums.Attributes.PARENT_ID.value]



        organization = self.current_load.env.organizations.get(
            ult_parent_id, copy.deepcopy(self.repository.organizations[ult_parent_id])
        )
        if ult_parent_id not in self.current_load.env.organizations:
            self.current_load.env.organizations[ult_parent_id] = organization

        worksite = organization.worksites_by_id[worksite_id]
        if worksite_id not in self.current_load.env.worksites_by_id:
            self.current_load.env.worksites_by_id[worksite_id] = worksite

        if hcp_id not in self.current_load.env.providers_by_id:
            provider_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_columns}
            provider = Provider(hcp_id=hcp_id,
                                **provider_data)
            self.current_load.env.providers_by_id[hcp_id] = provider

        provider = self.current_load.env.providers_by_id[hcp_id]

        provider_at_worksite_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_at_worksite_columns}

        prov_assign = ProviderAssignment(
            provider=self.current_load.env.providers_by_id[hcp_id],
            worksite=self.current_load.env.worksites_by_id[worksite_id],
            **provider_at_worksite_data
        )

        provider.assignments.add(prov_assign)
        worksite.provider_assignments.add(prov_assign)
        organization.providers.add(provider)
        organization.add_provider_assignment(worksite=worksite,
                                             provider_assignment=prov_assign)

    def load_environment(self, required_cols: RequiredEntitiesColumns, year):
        organizations = self._load_organizations()
        self.year_end_df.apply(self._apply_create_entities, required_cols=required_cols, axis=1)

