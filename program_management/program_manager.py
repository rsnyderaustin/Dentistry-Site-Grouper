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
        yearend_df.columns = [col.lower().replace(' ', '') for col in yearend_df.columns]
        worksites_df.columns = [col.lower().replace(' ', '') for col in worksites_df.columns]

        self.environment_manager = EnvironmentManager(yearend_df=yearend_df,
                                                      worksites_df=worksites_df,
                                                      site_relations=WorksiteParentRelations(worksites_df),
                                                      required_entities_cols=required_entities_cols)

    def create_organizations(self):
        self.environment_manager.create_environment()
        x=0

