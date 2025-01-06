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
            OutputDataColumns.WORKSITE_ID.value: [],
            OutputDataColumns.CLASSIFICATION.value: [],
            WorksiteDataColumns.ULTIMATE_PARENT_ID.value: []
        }

    def format(self, data: Data):
        orgs_by_year = data.organizations_by_year
        for year, orgs in orgs_by_year.items():
            for org in orgs:
                num_worksites = range(len(org.worksites_by_id))
                self.output[ProgramDataColumns.YEAR.value].extend([year for _ in num_worksites])
                self.output[WorksiteDataColumns.ULTIMATE_PARENT_ID.value].extend([org.ultimate_parent_id for _ in num_worksites])
                self.output[OutputDataColumns.ORG_SIZE.value].extend([org.number_of_dentists for _ in num_worksites])
                classifications = org.classify()

                for worksite_id, classification in classifications.items():
                    self.output[OutputDataColumns.WORKSITE_ID.value].append(worksite_id)
                    self.output[OutputDataColumns.CLASSIFICATION.value].append(classification)

        return pd.DataFrame(self.output)


class PracticeArrangement(AnalysisClass):

    def __init__(self):
        super().__init__()

        self.data = Data()

    def get_dataframe(self):
        formatter = Formatter()
        df = formatter.format(data=self.data)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[OutputDataColumns.WORKSITE_ID.value],
                                       provider_columns=[],
                                       provider_at_worksite_columns=[ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value,
                                                                     ProviderAtWorksiteDataColumns.WK_WEEKS.value])

