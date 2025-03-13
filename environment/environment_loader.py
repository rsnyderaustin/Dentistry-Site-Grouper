
from utils import RequiredEntitiesColumns
import factories
from .environment import Environment


class EnvironmentLoader:

    def __init__(self,
                 worksites_df,
                 year_end_df,
                 required_cols: RequiredEntitiesColumns
                 ):
        self.worksites_df = worksites_df
        self.year_end_df = year_end_df
        self.required_cols = required_cols

        self.worksites_by_id = dict()
        self.providers_by_id = dict()
        self.organizations_by_id = dict()

        self.worksite_id_to_ultimate_parent_id = {}

        self.organizations_loaded = False

    def load_environment(self) -> Environment:
        self.year_end_df.apply(
            factories.apply_create_entities,
            required_cols=self.required_cols,
            worksites_by_id=self.worksites_by_id,
            providers_by_id=self.providers_by_id,
            axis=1
        )

        organizations = factories.create_organizations(
            worksites_dataframe=self.worksites_df,
            worksites_by_id=self.worksites_by_id
        )
        self.organizations_by_id = {
            organization.ultimate_parent_worksite_id: organization for organization in organizations
        }

        # Filter out any organizations that don't have a provider
        self.organizations_by_id = {
            ultimate_parent_id: organization for ultimate_parent_id, organization in self.organizations_by_id.items()
            if organization.providers_by_id
        }

        env = Environment(
            providers_by_id=self.providers_by_id,
            worksites_by_id=self.worksites_by_id,
            organizations_by_id=self.organizations_by_id
        )

        return env



