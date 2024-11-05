from entities import RequiredEntitiesColumns
import pandas as pd

from environment import EnvironmentManager
from worksite_data import WorksiteParentRelations


class ProgramManager:

    def __init__(self,
                 worksites_df: pd.DataFrame,
                 yearend_df: pd.DataFrame,
                 required_entities_cols: RequiredEntitiesColumns
                 ):
        self.required_entities_cols = required_entities_cols

        self.environment_manager = EnvironmentManager(yearend_df=yearend_df,
                                                      site_relations=WorksiteParentRelations(worksites_df))

    def create_organizations(self):
        self.environment_manager.create_environment()
        x=0

