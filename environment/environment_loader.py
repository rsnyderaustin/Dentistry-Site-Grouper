

from .worksite_parent_relations import WorksiteParentRelations
from environment.environment import Environment
from column_enums import ProviderDataColumns, WorksiteDataColumns
from entities import Organization, Provider, ProviderAssignment, RequiredEntitiesColumns, Worksite
import preprocessing


class CurrentLoad:

    def __init__(self, year_end_df, year, env):
        self.year_end_df = year_end_df
        self.year = year
        self.env = env


class EnvironmentLoader:

    def __init__(self, worksites_df, year_end_df, required_cols: RequiredEntitiesColumns, worksite_parent_relations: WorksiteParentRelations):
        self.worksites_df = worksites_df
        self.year_end_dataframes = preprocessing.YearEndDataFrames(year_end_df=year_end_df)
        self.required_cols = required_cols
        self.worksite_parent_relations = worksite_parent_relations

        self.organizations_loaded = False
        self.current_load = None

        self.org_id = 0

    def _load_organizations(self):
        for relation in self.worksite_parent_relations.relationships:
            if relation.worksite_id not in self.current_load.env.worksites:
                worksite_rows = self.worksites_df.query(f"{WorksiteDataColumns.WORKSITE_ID.value} == {relation.worksite_id}")
                worksite_row = worksite_rows.iloc[0]
                worksite_data = {col: worksite_row[col] for col in self.required_cols.worksite_columns}
                new_worksite = Worksite(relation.worksite_id,
                                        parent_id=relation.parent_id,
                                        worksite_data=worksite_data)
                self.current_load.env.worksites[relation.worksite_id] = new_worksite

                if relation.parent_id == relation.worksite_id and relation.worksite_id not in self.current_load.env.organizations:
                    org_id = self.org_id
                    self.org_id += 1
                    new_org = Organization(ult_parent_worksite=new_worksite,
                                           org_id=org_id)
                    self.current_load.env.organizations[org_id] = new_org

    def _apply_create_entities(self, row, required_cols: RequiredEntitiesColumns):
        hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
        worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
        parent_id = self.worksite_parent_relations.get_parent_id(worksite_id)

        if worksite_id not in self.current_load.env.worksites and not self.organizations_loaded:
            worksite_data = {col: row[col] for col in required_cols.worksite_columns}
            new_worksite = Worksite(worksite_id=worksite_id,
                                    parent_id=parent_id,
                                    worksite_data=worksite_data)
            self.current_load.env.worksites[worksite_id] = new_worksite

        if hcp_id not in self.current_load.env.providers:
            provider_data = {col: row[col] for col in required_cols.provider_columns}
            new_provider = Provider(hcp_id=hcp_id,
                                    provider_data=provider_data)
            self.current_load.env.providers[hcp_id] = new_provider

        provider = self.current_load.env.providers[hcp_id]
        worksite = self.current_load.env.worksites[worksite_id]

        if worksite_id == parent_id and not self.organizations_loaded:
            org_id = self.org_id
            self.org_id += 1
            new_organization = Organization(ult_parent_worksite=worksite,
                                            org_id=org_id)
            self.current_load.env.organizations[org_id] = new_organization

        provider_at_worksite_data = {col: row[col] for col in required_cols.provider_at_worksite_columns}

        prov_assign = ProviderAssignment(
            provider_id=hcp_id,
            worksite_id=worksite_id,
            assignment_data=provider_at_worksite_data
        )

        provider.assignments.add(prov_assign)
        worksite.provider_assignments.add(prov_assign)

    def load_environment(self, required_cols: RequiredEntitiesColumns, year):
        if not self.organizations_loaded:
            self._load_organizations()

        self.current_load = CurrentLoad(year_end_df=self.year_end_dataframes.get_dataframe(year),
                                        year=year,
                                        env=Environment(year=year))
        self.current_load.year_end_df.apply(self._apply_create_entities, required_cols=required_cols, axis=1)

        return self.current_load.env
