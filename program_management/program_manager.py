from entities import RequiredEntitiesColumns
import pandas as pd

from organizations import OrganizationsManager


class ProgramManager:

    def __init__(self,
                 worksites_df: pd.DataFrame,
                 yearend_df: pd.DataFrame,
                 required_entities_cols: RequiredEntitiesColumns
                 ):
        self.worksites_df = worksites_df
        self.yearend_df = yearend_df
        self.required_entities_cols = required_entities_cols

        self.organizations_manager = OrganizationsManager()

    def create_organizations(self):
        worksites = create_worksites(self.worksites_df)
        parent_ids = set(ws.parent_id for ws in worksites)

        non_worksite_parents = set()
        for parent_id in parent_ids:
            if parent_id not in worksites.keys():
                non_worksite_parents.add(parent_id)

