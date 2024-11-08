import pandas as pd

from .environment import Environment
from .worksite_parent_relations import WorksiteParentRelations
from algo import HierarchyAlgo, WorksiteNode
import entities
from entities import Organization, RequiredEntitiesColumns, Worksite
from column_enums import ProviderDataColumns, WorksiteDataColumns
import preprocessing


class EnvironmentManager:

    def __init__(self,
                 year_end_df: pd.DataFrame,
                 worksites_df: pd.DataFrame):
        self.year_end_dataframes = preprocessing.YearEndDataFrames(year_end_df=year_end_df)
        self.environments = {year: Environment() for year in self.year_end_dataframes.years}

        child_parent_tuples = set(zip(
            worksites_df[WorksiteDataColumns.WORKSITE_ID.value],
            worksites_df[WorksiteDataColumns.PARENT_ID.value]
        ))
        self.site_relations = WorksiteParentRelations(child_parent_tuples=child_parent_tuples)
        self.algo = HierarchyAlgo(child_parent_tuples=child_parent_tuples)

        self.ultimate_parent_ids = {worksite_id for worksite_id in self.site_relations.child_to_parent.keys()
                                    if self.site_relations.child_to_parent[worksite_id] == worksite_id}

    def _create_providers(self, required_cols):
        self.year_end_df.apply(entities.apply_create_provider,
                               providers=self.environment.providers,
                               provider_cols=required_cols.provider_columns,
                               axis=1)

    def _create_worksites_from_nodes(self, nodes: set[WorksiteNode]):
        for node in nodes:
            new_worksite = Worksite(worksite_id=node.worksite_id,
                                    parent_id=node.parent_id)
            self.environment.worksites[node.worksite_id] = new_worksite

    def _assign_worksite_children(self, nodes):
        for node in nodes:
            worksite = self.environment.worksites[node.worksite_id]
            child_worksites = {self.environment.worksites[child_node.worksite_id] for child_node in node.child_nodes}
            worksite.add_child_worksites(child_worksites)

    def _create_organizations_from_nodes(self, nodes: set[WorksiteNode]):
        ultimate_parent_nodes = {node for node in nodes if node.is_ultimate_parent}
        self.environment.organizations = {Organization(self.environment.worksites[node.worksite_id]) for node in
                                          ultimate_parent_nodes}

    def _apply_add_providers_to_worksites(self, row, required_cols):
        hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
        worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]

        provider_at_worksite_data = {col: row[col] for col in required_cols.provider_at_worksite_columns}
        self.environment.worksites[worksite_id].add_provider_assignment(provider=self.environment.providers[hcp_id],
                                                                        assignment_data=provider_at_worksite_data)

    def fill_environment(self, required_cols):
        algo_nodes = self.algo.create_hierarchy()

        self._create_providers(required_cols=required_cols)
        self._create_worksites_from_nodes(nodes=algo_nodes)
        self._assign_worksite_children(nodes=algo_nodes)
        self.year_end_df.apply(self._apply_add_providers_to_worksites,
                               required_cols=required_cols,
                               axis=1)
        self.year_end_df.apply(entities.apply_create_worksite,
                               worksites=self.environment.worksites,
                               worksite_cols=required_cols.worksite_columns,
                               axis=1)

        self._create_organizations_from_nodes(nodes=algo_nodes)

        relevant_site_ids = self.year_end_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        self.environment.organizations = set(org for org in self.environment.organizations
                                             if
                                             any({org.has_worksite(worksite_id) for worksite_id in relevant_site_ids}))
