import copy
import logging
import time

from .environment import Environment
from algo import worksite_node
from column_enums import ProgramDataColumns, ProviderDataColumns, WorksiteDataColumns
import entities
from entities import Organization, RequiredEntitiesColumns, Worksite
import preprocessing


class OrganizationsHandler:

    def __init__(self, nodes):
        self.nodes = nodes

        self.worksites = {}
        self.organizations = {}

    def create_organizations(self):
        self._create_worksites_from_nodes()
        self._assign_worksite_children()
        self._create_organizations_from_nodes()

    def _create_worksites_from_nodes(self):
        for node in self.nodes:
            new_worksite = Worksite(worksite_id=node.worksite_id,
                                    parent_id=node.parent_id)
            self.worksites[node.worksite_id] = new_worksite

    def _assign_worksite_children(self):
        for node in self.nodes:
            worksite = self.worksites[node.worksite_id]
            child_worksites = {self.worksites[child_node.worksite_id] for child_node in node.child_nodes}
            worksite.add_child_worksites(child_worksites)

    def _create_organizations_from_nodes(self):
        ultimate_parent_nodes = {node for node in self.nodes if node.is_ultimate_parent}
        self.organizations = {Organization(self.worksites[node.worksite_id]) for node in
                              ultimate_parent_nodes}

    def get_relevant_organizations(self, worksite_ids):
        return {org for org in self.organizations if org.has_one_of_worksites(worksite_ids)}

    def get_worksites(self, worksite_ids):
        return {self.worksites[id_] for id_ in worksite_ids}


class EnvironmentLoader:

    def __init__(self, worksites_df, year_end_df, algo_nodes):
        self.worksites_df = worksites_df
        self.year_end_dataframes = preprocessing.YearEndDataFrames(year_end_df=year_end_df)

        self.orgs_handler = OrganizationsHandler(algo_nodes)
        self.orgs_handler.create_organizations()

    def _apply_add_providers_to_worksites(self, row, env, required_cols):
        hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
        worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]

        provider_at_worksite_data = {col: row[col] for col in required_cols.provider_at_worksite_columns}
        self.orgs_handler.worksites[worksite_id].add_provider_assignment(provider=env.providers[hcp_id],
                                                                         assignment_data=provider_at_worksite_data)

    def load_environment(self, required_cols: RequiredEntitiesColumns, year):
        env = Environment(year=year)
        year_end_df = self.year_end_dataframes.get_dataframe(year)

        worksite_ids = year_end_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        relevant_orgs = {copy.deepcopy(org) for org in self.orgs_handler.get_relevant_organizations(worksite_ids=worksite_ids)}
        env.organizations = relevant_orgs
        env.worksites = {org.all_worksites for org in env.organizations}

        b_time = time.time()
        year_end_df.apply(entities.apply_create_provider,
                          providers=env.providers,
                          provider_cols=required_cols.provider_columns,
                          axis=1)
        logging.info(f"Time to create providers: {time.time() - b_time}")

        b_time = time.time()
        year_end_df.apply(self._apply_add_providers_to_worksites,
                          env=env,
                          required_cols=required_cols,
                          axis=1)
        logging.info(f"Time to add providers to worksites: {time.time() - b_time}")
        return env
