import pandas as pd

from .analysis_class import AnalysisClass
from column_enums import OutputDataColumns, ProgramDataColumns, ProviderDataColumns, WorksiteDataColumns
from entities import RequiredEntitiesColumns


class Data:

    def __init__(self):
        self._data = {}

    def add_organization(self, year, organization):
        if year not in self._data:
            self._data[year] = {}

        self._data[year].add(organization)

    def data_generator(self):
        for year, org in self._data.items():
            org_size = len(org.providers)
            for provider in org.providers:
                yield year, org.ultimate_parent_worksite.worksite_id, org_size, provider


class Formatter:

    def __init__(self):
        self.output = {
            ProgramDataColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderDataColumns.AGE.value: [],
            ProviderDataColumns.PROVIDER_ID.value: [],
            ProviderDataColumns.PRAC_ARR_NAME.value: [],
            WorksiteDataColumns.WORKSITE_ID.value: []
        }

    def format_prov_assign_by_org_size(self, data: Data):
        for year, ult_parent_id, org_size, provider in data.data_generator():
            self.output[ProgramDataColumns.YEAR.value].append(year)
            self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
            self.output[ProviderDataColumns.AGE.value].append(
                getattr(provider, ProviderDataColumns.AGE.value)
            )
            self.output[ProviderDataColumns.PROVIDER_ID.value].append(
                getattr(provider, ProviderDataColumns.PROVIDER_ID.value)
            )
            self.output[ProviderDataColumns.PRAC_ARR_NAME.value].append(
                getattr(provider, ProviderDataColumns.PRAC_ARR_NAME.value)
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
                                       provider_columns=[ProviderDataColumns.AGE.value,
                                                         ProviderDataColumns.PRAC_ARR_NAME.value],
                                       provider_at_worksite_columns=[])
