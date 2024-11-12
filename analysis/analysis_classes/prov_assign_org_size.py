import pandas as pd

from .analysis_class import AnalysisClass
from column_enums import OutputDataColumns, ProgramDataColumns, ProviderDataColumns, WorksiteDataColumns
from entities import RequiredEntitiesColumns
from environment import Environment


class Data:

    def __init__(self):
        self._data = {}

    def add_provider_assignments(self, year, org_size, provider_assignments):
        if year not in self._data:
            self._data[year] = {}

        if org_size not in self._data[year]:
            self._data[year][org_size] = set()

        self._data[year][org_size].update(provider_assignments)

    def provider_assignments_generator(self):
        for year, org_data in self._data.items():
            for org_size, provider_assignments in org_data.items():
                for provider_assign in provider_assignments:
                    yield year, org_size, provider_assign


class Formatter:

    def __init__(self):
        self.output = {
            ProgramDataColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderDataColumns.PRAC_ARR_NAME.value: [],
            ProviderDataColumns.PROVIDER_ID.value: []
        }

    def format_prov_assign_by_org_size(self, data: Data):
        for year, org_size, provider_assign in data.provider_assignments_generator():
            self.output[ProgramDataColumns.YEAR.value].append(year)
            self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
            self.output[ProviderDataColumns.PRAC_ARR_NAME.value].append(
                getattr(provider_assign, ProviderDataColumns.PRAC_ARR_NAME.value)
            )
            self.output[ProviderDataColumns.PROVIDER_ID.value].append(
                getattr(provider_assign.provider, ProviderDataColumns.PROVIDER_ID.value)
            )
        return pd.DataFrame(self.output)


class ProvAssignByOrgSize(AnalysisClass):

    def __init__(self):
        super().__init__()
        self.data = Data()

    def process_data(self, environments):
        for environment in environments:
            for organization in environment.organizations:
                org_size = len(organization.worksites)

                self.data.add_provider_assignments(
                    year=environment.year,
                    org_size=org_size,
                    provider_assignments=organization.all_provider_assignments
                )

    def get_dataframe(self):
        formatter = Formatter()
        df = formatter.format_prov_assign_by_org_size(data=self.data)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[],
                                       provider_columns=[ProviderDataColumns.PROVIDER_ID.value,
                                                         ProviderDataColumns.PRAC_ARR_NAME.value],
                                       provider_at_worksite_columns=[])
