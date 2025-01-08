
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
            WorksiteDataColumns.ULTIMATE_PARENT_ID.value: []
        }

    def format(self, data: Data):
        for year, organizations in data.organizations_by_year.items():
            self.output[ProgramDataColumns.YEAR.value].extend([year for _ in range(len(organizations))])
            for org in organizations:
                self.output[OutputDataColumns.ORG_SIZE.value].append(org.number_of_dentists)
                self.output[WorksiteDataColumns.ULTIMATE_PARENT_ID.value].append(org.ultimate_parent_id)
        return pd.DataFrame(self.output)


class OrganizationSizes(AnalysisClass):

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
        df = formatter.format(data=self.data)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[],
                                       provider_columns=[],
                                       provider_at_worksite_columns=[])