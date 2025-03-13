import pandas as pd

from environment import HierarchyRelationship
from environment.environment_loader import EnvironmentLoader
from .hierarchy_relations_manager import HierarchyRelationsManager
from utils.enums import WorksiteEnums
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
            worksites_df[WorksiteEnums.Attributes.WORKSITE_ID.value],
            worksites_df[WorksiteEnums.Attributes.PARENT_ID.value]
        ))

        relationships = list(
            HierarchyRelationship(worksite_id=tup[0],
                                  parent_id=tup[1])
            for tup in child_parent_tuples
        )
        worksite_ids = set(worksites_df[WorksiteEnums.Attributes.WORKSITE_ID.value])
        parent_ids = set(worksites_df[WorksiteEnums.Attributes.PARENT_ID.value])

        missing_parent_sites = (parent_id for parent_id in parent_ids if parent_id not in worksite_ids)


        self.site_relations = HierarchyRelationsManager(relationships=relationships)

        worksite_ids = self.worksites_df[WorksiteEnums.Attributes.WORKSITE_ID.value].unique().tolist()
        self.ultimate_parent_ids = {worksite_id for worksite_id in worksite_ids
                                    if self.site_relations.get_parent_id(worksite_id) == worksite_id}

    def fill_environments(self, required_cols):
        env_loader = EnvironmentLoader(worksites_df=self.worksites_df,
                                       year_end_df=self.year_end_df,
                                       required_cols=required_cols,
                                       worksite_parent_relations=self.site_relations)

        for year in self.year_end_dataframes.years:
            new_env = env_loader.load_environment(required_cols=required_cols,
                                                  year=year)
            self.environments.add(new_env)




