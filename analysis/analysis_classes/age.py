import pandas as pd

from .analysis_class import AnalysisClass, Data
from column_enums import (OutputDataColumns, ProgramDataColumns, ProviderAtWorksiteDataColumns, ProviderDataColumns,
                          WorksiteDataColumns)
from things import RequiredEntitiesColumns


class Formatter:

    def __init__(self):
        self.output = {
            ProgramDataColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderDataColumns.AGE.value: [],
            ProviderDataColumns.HCP_ID.value: [],
            ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value: [],
            ProviderAtWorksiteDataColumns.SPECIALTY_NAME.value: [],
            WorksiteDataColumns.WORKSITE_ID.value: [],
            WorksiteDataColumns.ULTIMATE_PARENT_ID.value: []
        }

    def format_prov_assign_by_org_size(self, data: Data):
        for year, ult_parent_id, org_size, provider_assignment in data.data_generator():
            provider = provider_assignment.provider
            worksite = provider_assignment.worksite
            self.output[ProgramDataColumns.YEAR.value].append(year)
            self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
            self.output[ProviderDataColumns.AGE.value].append(
                getattr(provider, ProviderDataColumns.AGE.value)
            )
            self.output[ProviderDataColumns.HCP_ID.value].append(
                getattr(provider, ProviderDataColumns.HCP_ID.value)
            )
            self.output[ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value].append(
                getattr(provider_assignment, ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value)
            )
            self.output[ProviderAtWorksiteDataColumns.SPECIALTY_NAME.value].append(
                getattr(provider_assignment, ProviderAtWorksiteDataColumns.SPECIALTY_NAME.value)
            )
            self.output[WorksiteDataColumns.WORKSITE_ID.value].append(
                getattr(worksite, WorksiteDataColumns.WORKSITE_ID.value)
            )
            self.output[WorksiteDataColumns.ULTIMATE_PARENT_ID.value].append(ult_parent_id)
        return pd.DataFrame(self.output)


class AgeByOrgSize(AnalysisClass):

    def __init__(self):
        super().__init__()

        self.data = Data()

    def process_data(self, environments):
        for environment in environments:
            for organization in environment.organizations.values():
                self.data.add_organization(
                    year=environment.year,
                    organization=organization)

    def get_dataframe(self):
        formatter = Formatter()
        df = formatter.format_prov_assign_by_org_size(data=self.data)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[],
                                       provider_columns=[ProviderDataColumns.AGE.value],
                                       provider_at_worksite_columns=[ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value,
                                                                     ProviderAtWorksiteDataColumns.SPECIALTY_NAME.value])

