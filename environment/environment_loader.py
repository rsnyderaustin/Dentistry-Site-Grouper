import copy
import logging

from .worksite_parent_relations import WorksiteParentRelations
from environment.environment import Environment
from column_enums import ProviderDataColumns, WorksiteDataColumns
from things import Organization, Provider, ProviderAssignment, RequiredEntitiesColumns, Worksite
import preprocessing


class Repository:

    def __init__(self):
        self.worksites = {}
        self.organizations = {}


class CurrentLoad:

    def __init__(self, year_end_df, year, env):
        self.year_end_df = year_end_df
        self.year = year
        self.env = env


class EnvironmentLoader:

    def __init__(self, worksites_df, year_end_df, required_cols: RequiredEntitiesColumns,
                 worksite_parent_relations: WorksiteParentRelations):
        self.worksites_df = worksites_df
        self.year_end_dataframes = preprocessing.YearEndDataFrames(year_end_df=year_end_df)
        self.required_cols = required_cols
        self.worksite_parent_relations = worksite_parent_relations

        self.repository = Repository()

        self.worksite_id_to_ultimate_parent_id = {}

        self.organizations_loaded = False
        self.current_load = None

    def _load_organizations(self):
        # Fill repository with worksites and organizations
        logging.info("Starting to fill repository with worksites and organizations.")
        for relation in self.worksite_parent_relations.relationships:
            if relation.worksiteid not in self.repository.worksites:
                worksite_rows = self.worksites_df.query(
                    f"{WorksiteDataColumns.WORKSITE_ID.value} == {relation.worksiteid}")
                worksite_row = worksite_rows.iloc[0]
                worksite_data = {col: worksite_row[col] for col in self.required_cols.worksite_columns}
                new_worksite = Worksite(relation.worksiteid,
                                        parent_id=relation.parentid,
                                        worksite_data=worksite_data)
                self.repository.worksites[relation.worksiteid] = new_worksite

                if relation.parentid == relation.worksiteid and relation.worksiteid not in self.repository.organizations:
                    new_org = Organization(ult_parent_worksite=new_worksite)
                    self.repository.organizations[relation.worksiteid] = new_org
        logging.info("Finished filling repository.")

        # Add worksites to organizations
        non_ult_parent_worksites = {worksite for worksite in self.repository.worksites.values()
                                    if worksite.worksiteid != worksite.parentid}
        loops = 0
        while len(non_ult_parent_worksites) > 0:
            logging.info(f"Loop number {loops}")
            added_worksites = set()
            for org in self.repository.organizations.values():
                for worksite in non_ult_parent_worksites:
                    parent_worksite_id = self.worksite_parent_relations.get_parent_id(worksite.worksiteid)
                    if parent_worksite_id in org.worksites:
                        org.add_worksite(worksite=worksite,
                                         parent=self.repository.worksites[parent_worksite_id])
                        added_worksites.add(worksite)
            for worksite in added_worksites:
                non_ult_parent_worksites.remove(worksite)

            loops += 1

        # Fill worksite_id_to_ultimate_parent_id dict
        for ult_parent_id, org in self.repository.organizations.items():
            for worksite in org.worksites.values():
                self.worksite_id_to_ultimate_parent_id[worksite.worksiteid] = ult_parent_id

        self.organizations_loaded = True

    def _apply_create_entities(self, row, required_cols: RequiredEntitiesColumns):
        hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
        worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
        ult_parent_id = self.worksite_id_to_ultimate_parent_id[worksite_id]

        organization = self.current_load.env.organizations.get(
            ult_parent_id, copy.deepcopy(self.repository.organizations[ult_parent_id])
        )
        if ult_parent_id not in self.current_load.env.organizations:
            self.current_load.env.organizations[ult_parent_id] = organization

        worksite = organization.worksites[worksite_id]
        if worksite_id not in self.current_load.env.worksites:
            self.current_load.env.worksites[worksite_id] = worksite

        if hcp_id not in self.current_load.env.providers:
            provider_data = {col: row[col] for col in required_cols.provider_columns}
            provider = Provider(hcp_id=hcp_id,
                                provider_data=provider_data)
            self.current_load.env.providers[hcp_id] = provider

        provider = self.current_load.env.providers[hcp_id]

        provider_at_worksite_data = {col: row[col] for col in required_cols.provider_at_worksite_columns}

        prov_assign = ProviderAssignment(
            provider=self.current_load.env.providers[hcp_id],
            worksite=self.current_load.env.worksites[worksite_id],
            assignment_data=provider_at_worksite_data
        )

        provider.assignments.add(prov_assign)
        worksite.provider_assignments.add(prov_assign)
        organization.providers.add(provider)
        organization.add_provider_assignment(worksite=worksite,
                                             provider_assignment=prov_assign)

    def load_environment(self, required_cols: RequiredEntitiesColumns, year):
        if not self.organizations_loaded:
            self._load_organizations()

        self.current_load = CurrentLoad(year_end_df=self.year_end_dataframes.get_dataframe(year),
                                        year=year,
                                        env=Environment(year=year))
        self.current_load.year_end_df.apply(self._apply_create_entities, required_cols=required_cols, axis=1)

        return self.current_load.env
