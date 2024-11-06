import pandas as pd

from worksite_data.worksite_data_enums import WorksiteDataColumns
from entities.objects.worksite import Worksite


class WorksiteFactory:

    def __init__(self, worksites_df: pd.DataFrame):
        self.worksites_df = worksites_df

        self.worksites = {}
        self.worksites_created = False

    def create_worksite(self, worksite_id, parent_id, *extra_params):
        worksite_rows = self.worksites_df[self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value] == worksite_id]
        if len(worksite_rows) == 0:
            raise ValueError(f"Could not find row data for Worksite ID {worksite_id}")

        worksite_row = self.worksites_df.loc[self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value] == worksite_id].iloc[0]
        extra_data = {param: worksite_row[param.value] for param in extra_params}
        new_worksite = Worksite(
            worksite_id=worksite_id,
            parent_id=parent_id,
            **extra_data
        )
        return new_worksite
