import pandas as pd

from organizations.worksite_data_enums import WorksiteDataColumns
from entities.objects.worksite import Worksite


class WorksiteFactory:

    def __init__(self, yearend_df: pd.DataFrame):
        self.yearend_df = yearend_df

        self.worksites = {}
        self.worksites_created = False

    def create_worksite(self, worksite_id, parent_id, *extra_params):
        worksite_row = self.yearend_df.loc[self.yearend_df[WorksiteDataColumns.WORKSITE_ID.value] == worksite_id].iloc[
            0]
        extra_data = {param: worksite_row[param.value] for param in extra_params}
        new_worksite = Worksite(
            worksite_id=worksite_id,
            parent_id=parent_id,
            **extra_data
        )
        return new_worksite
