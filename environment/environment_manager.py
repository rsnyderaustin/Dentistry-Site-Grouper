import pandas as pd

from .environment import Environment
from .environment_loader import EnvironmentLoader
from .worksite_parent_relations import WorksiteParentRelations
from algo import HierarchyAlgo
from column_enums import ProgramDataColumns, WorksiteDataColumns
import preprocessing


def _generate_algo_nodes(child_parent_tuples):
    algo = HierarchyAlgo(child_parent_tuples=child_parent_tuples)
    algo_nodes = algo.create_hierarchy()
    return algo_nodes


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
        self.algo_nodes = _generate_algo_nodes(child_parent_tuples=child_parent_tuples)

        self.site_relations = WorksiteParentRelations(child_parent_tuples=child_parent_tuples)

        self.ultimate_parent_ids = {worksite_id for worksite_id in self.site_relations.child_to_parent.keys()
                                    if self.site_relations.child_to_parent[worksite_id] == worksite_id}

    def fill_environments(self, required_cols):
        env_loader = EnvironmentLoader(worksites_df=self.worksites_df,
                                       year_end_df=self.year_end_df,
                                       algo_nodes=self.algo_nodes)
        for year in self.year_end_dataframes.years:
            new_env = env_loader.load_environment(required_cols=required_cols,
                                                  year=year)
            self.environments.add(new_env)




