import pandas as pd

from .organization_creator import OrganizationCreator
from .worksite_parent_relations import WorksiteParentRelations
from algo import HierarchyAlgo, WorksiteNode
from entities import RequiredEntitiesColumns, Worksite, WorksiteFactory
from worksite_data.worksite_data_enums import WorksiteDataColumns


def _apply_create_worksites(row, yearend_df, extra_params, worksites):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]

    worksite_row = yearend_df.loc[yearend_df[WorksiteDataColumns.WORKSITE_ID.value] == worksite_id].iloc[0]
    extra_data = {param: worksite_row[param.value] for param in extra_params}

    new_worksite = Worksite(
        worksite_id=worksite_id,
        parent_id=parent_id,
        **extra_data
    )
    worksites[worksite_id] = new_worksite


class EnvironmentManager:

    def __init__(self,
                 yearend_df: pd.DataFrame,
                 worksites_df: pd.DataFrame,
                 required_entities_cols: RequiredEntitiesColumns):
        self.yearend_df = yearend_df
        self.worksites_df = worksites_df
        self.site_relations = WorksiteParentRelations(worksites_df=worksites_df)
        self.required_entities_cols = required_entities_cols

        self.ultimate_parent_ids = {worksite_id for worksite_id in self.site_relations.worksite_to_parent.keys()
                                    if self.site_relations.worksite_to_parent[worksite_id] == worksite_id}

        self.worksite_factory = WorksiteFactory(worksites_df=worksites_df)

        self.organizations = set()
        self.worksites = dict()

    def _recursive_create_uncreated_parents(self, uncreated_parents: set):
        new_parent_ids = set()
        for worksite_id in uncreated_parents:
            new_worksite = self.worksite_factory.create_worksite(
                worksite_id=worksite_id,
                parent_id=self.site_relations.get_parent_id(worksite_id)
            )
            self.worksites[new_worksite.worksite_id] = new_worksite
            new_parent_ids.add(new_worksite.worksite_id)

        uncreated_ids = {id_ for id_ in new_parent_ids if id_ not in self.worksites}
        if len(uncreated_ids) == 0:
            return

        self._recursive_create_uncreated_parents(uncreated_ids)

    def _create_uncreated_parents(self):
        parent_ids = set(ws.parent_id for ws in self.worksites.values())
        uncreated_ids = set(parent_id for parent_id in parent_ids if parent_id not in self.worksites.keys())
        self._recursive_create_uncreated_parents(uncreated_ids)

    def _create_organizations_from_nodes(self, nodes: set[WorksiteNode]):
        organizations = set()
        for node in nodes:
            if node.is_ultimate_parent:
                organizations.add(self.worksites[node.worksite_id])

            worksite = self.worksites[node.worksite_id]
            child_worksites = set(self.worksites[child_node.worksite_id] for child_node in node.child_nodes)
            worksite.add_child_worksites(child_worksites)

    def create_environment(self):
        child_parent_tuples = zip(
            self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value],
            self.worksites_df[WorksiteDataColumns.PARENT_ID.value]
        )
        algo = HierarchyAlgo(child_parent_tuples=child_parent_tuples)
        algo_nodes = algo.create_hierarchy()

        self.yearend_df.apply(_apply_create_worksites,
                              yearend_df=self.yearend_df,
                              worksites=self.worksites,
                              extra_params=self.required_entities_cols.worksite_columns,
                              axis=1)
        self._create_uncreated_parents()

        self._create_organizations_from_nodes(nodes=algo_nodes)

        relevant_site_ids = self.yearend_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        org_creator = OrganizationCreator(worksites=self.worksites)
        self.organizations = org_creator.create_organizations(relevant_site_ids=relevant_site_ids)

