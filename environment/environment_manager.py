import pandas as pd

from entities import Worksite, WorksiteFactory
from organizations import worksite_parent_relations
from organizations.worksite_data_enums import WorksiteDataColumns


def _apply_create_worksites(self, row, worksites):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]

    worksite_row = self.yearend_df.loc[self.yearend_df[WorksiteDataColumns.WORKSITE_ID.value] == worksite_id].iloc[0]
    extra_data = {param: worksite_row[param.value] for param in self.extra_params}

    new_worksite = Worksite(
        worksite_id=worksite_id,
        parent_id=parent_id,
        **extra_data
    )
    worksites[worksite_id] = new_worksite


class EnvironmentManager:

    def __init__(self,
                 yearend_df: pd.DataFrame,
                 site_relations: worksite_parent_relations.WorksiteParentRelations):
        self.yearend_df = yearend_df
        self.site_relations = site_relations

        self.worksite_factory = WorksiteFactory(yearend_df=yearend_df)

    def _create_uncreated_parents(self, worksites: dict):
        parent_ids = set(ws.parent_id for ws in worksites)
        uncreated_parent_ids = set(parent_id for parent_id in parent_ids if parent_id not in worksites.keys())

        for parent_id in uncreated_parent_ids:
            worksites[parent_id] = self.worksite_factory.create_worksite(
                worksite_id=self.site_relations.get_worksite_id(parent_id),
                parent_id=parent_id
            )

    def create_environment(self):
        worksites = {}
        self.yearend_df.apply(_apply_create_worksites, worksites=worksites)
        self._create_uncreated_parents(worksites=worksites)



