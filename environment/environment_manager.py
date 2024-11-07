import pandas as pd

from .worksite_parent_relations import WorksiteParentRelations
from algo import HierarchyAlgo, WorksiteNode
from entities import Organization, RequiredEntitiesColumns, Worksite, worksite_factory
from column_enums import WorksiteDataColumns


class EnvironmentManager:

    def __init__(self,
                 yearend_df: pd.DataFrame,
                 worksites_df: pd.DataFrame,
                 required_entities_cols: RequiredEntitiesColumns):
        self.yearend_df = yearend_df
        self.worksites_df = worksites_df
        child_parent_tuples = set(zip(
            self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value],
            self.worksites_df[WorksiteDataColumns.PARENT_ID.value]
        ))
        self.site_relations = WorksiteParentRelations(child_parent_tuples=child_parent_tuples)
        self.algo = HierarchyAlgo(child_parent_tuples=child_parent_tuples)
        self.required_entities_cols = required_entities_cols

        self.ultimate_parent_ids = {worksite_id for worksite_id in self.site_relations.child_to_parent.keys()
                                    if self.site_relations.child_to_parent[worksite_id] == worksite_id}

        self.organizations = set()
        self.worksites = dict()

    def _create_providers(self):
        

    def _create_worksites_from_nodes(self, nodes: set[WorksiteNode]):
        for node in nodes:
            new_worksite = Worksite(worksite_id=node.worksite_id,
                                    parent_id=node.parent_id)
            self.worksites[node.worksite_id] = new_worksite

        for node in nodes:
            worksite = self.worksites[node.worksite_id]
            child_worksites = {self.worksites[child_node.worksite_id] for child_node in node.child_nodes}
            worksite.add_child_worksites(child_worksites)

    def _create_organizations_from_nodes(self, nodes: set[WorksiteNode]):
        ultimate_parent_nodes = {node for node in nodes if node.is_ultimate_parent}
        self.organizations = {Organization(self.worksites[node.worksite_id]) for node in ultimate_parent_nodes}

    def create_environment(self):
        algo_nodes = self.algo.create_hierarchy()

        self._create_providers()
        self._create_worksites_from_nodes(nodes=algo_nodes)
        self.yearend_df.apply(worksite_factory.apply_create_worksite,
                              worksites=self.worksites,
                              extra_params=self.required_entities_cols.worksite_columns,
                              axis=1)

        self._create_organizations_from_nodes(nodes=algo_nodes)

        relevant_site_ids = self.yearend_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        self.organizations = set(org for org in self.organizations
                                 if any({org.has_worksite(worksite_id) for worksite_id in relevant_site_ids}))
