import pandas as pd

from environment.environment_loader import EnvironmentLoader
from .worksite_parent_relations import WorksiteParentRelations
from column_enums import WorksiteDataColumns
import preprocessing


class EnvironmentManager:

    def __init__(self,
                 year_end_df: pd.DataFrame,
                 worksites_df: pd.DataFrame):
        self.year_end_df = year_end_df
        self.worksites_df = worksites_df
        self.year_end_dataframes = preprocessing.YearEndDataFrames(year_end_df=year_end_df)

        self.environments = set()

        child_parent_tuples = set(zip(
            worksites_df[WorksiteDataColumns.WORKSITE_ID.value],
            worksites_df[WorksiteDataColumns.PARENT_ID.value]
        ))
        self.site_relations = WorksiteParentRelations(child_parent_tuples=child_parent_tuples)

        worksite_ids = self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value].unique().tolist()
        self.ultimate_parent_ids = {worksite_id for worksite_id in worksite_ids
                                    if self.site_relations.get_parent_id(worksite_id) == worksite_id}

    def fill_environments(self, required_cols):
        child_parent_tuples = list(zip(self.worksites_df[WorksiteDataColumns.WORKSITE_ID.value],
                                       self.worksites_df[WorksiteDataColumns.PARENT_ID.value]))
        worksite_parent_relations = WorksiteParentRelations(child_parent_tuples=child_parent_tuples)
        env_loader = EnvironmentLoader(worksites_df=self.worksites_df,
                                       year_end_df=self.year_end_df,
                                       required_cols=required_cols,
                                       worksite_parent_relations=worksite_parent_relations)

        for year in self.year_end_dataframes.years:
            new_env = env_loader.load_environment(required_cols=required_cols,
                                                  year=year)
            self.environments.add(new_env)




