import pandas as pd

from .organization_creator import OrganizationCreator
from entities import RequiredEntitiesColumns, Worksite, WorksiteFactory
from worksite_data import worksite_parent_relations
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
                 site_relations: worksite_parent_relations.WorksiteParentRelations,
                 required_entities_cols: RequiredEntitiesColumns):
        self.yearend_df = yearend_df
        self.site_relations = site_relations
        self.required_entities_cols = required_entities_cols

        self.ultimate_parent_ids = {worksite_id for worksite_id in self.site_relations.worksite_to_parent.keys()
                                    if self.site_relations.worksite_to_parent[worksite_id] == worksite_id}

        self.worksite_factory = WorksiteFactory(worksites_df=worksites_df)

        self.organizations = {}
        self.worksites = {}

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

    def create_environment(self):
        self.yearend_df.apply(_apply_create_worksites,
                              yearend_df=self.yearend_df,
                              worksites=self.worksites,
                              extra_params=self.required_entities_cols.worksite_columns,
                              axis=1)
        self._create_uncreated_parents()

        relevant_site_ids = self.yearend_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        org_creator = OrganizationCreator(worksites=self.worksites)
        self.organizations = org_creator.create_organizations(relevant_site_ids=relevant_site_ids)

