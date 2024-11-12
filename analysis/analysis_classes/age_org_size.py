import pandas as pd

from .analysis_class import AnalysisClass
from column_enums import OutputDataColumns, ProgramDataColumns, ProviderDataColumns, WorksiteDataColumns
from entities import RequiredEntitiesColumns


class Data:

    def __init__(self):
        self._data = {}

    def add_providers(self, year, org_size, providers):
        if year not in self._data:
            self._data[year] = {}

        if org_size not in self._data[year]:
            self._data[year][org_size] = set()

        self._data[year][org_size].update(providers)

    def provider_generator(self):
        for year, org_data in self._data.items():
            for org_size, providers in org_data.items():
                for provider in providers:
                    yield year, org_size, provider


class Formatter:

    def __init__(self):
        self.output = {
            ProgramDataColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderDataColumns.AGE.value: [],
            ProviderDataColumns.PROVIDER_ID.value: [],
            ProviderDataColumns.PRAC_ARR_NAME.value: []
        }

    def format_prov_assign_by_org_size(self, data: Data):
        for year, org_size, provider in data.provider_generator():
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
        return pd.DataFrame(self.output)


class AgeByOrgSize(AnalysisClass):

    def __init__(self):
        super().__init__()

        self.data = Data()

    def process_data(self, environments):
        for environment in environments:
            for organization in environment.organizations:
                org_size = len(organization.worksites)
                prov_assigns = organization.all_provider_assignments
                providers = set(prov_assign.provider for prov_assign in prov_assigns)
                self.data.add_providers(
                    year=environment.year,
                    org_size=org_size,
                    providers=providers
                )

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
