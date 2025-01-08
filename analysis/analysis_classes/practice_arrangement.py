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
            ProviderDataColumns.HCP_ID.value: [],
            ProviderDataColumns.AGE.value: [],
            OutputDataColumns.WORKSITE_ID.value: [],
            OutputDataColumns.CLASSIFICATION.value: [],
            WorksiteDataColumns.ULTIMATE_PARENT_ID.value: []
        }

    def format(self, data: Data, simplify_arrangements: bool = False):
        orgs_by_year = data.organizations_by_year
        for year, orgs in orgs_by_year.items():
            for org in orgs:
                classifications = org.classify(simplify_arrangements)

                for worksite_id, classification in classifications.items():
                    worksite = org.worksites_by_id[worksite_id]
                    providers = {prov_assign.provider for prov_assign in worksite.provider_assignments}

                    for provider in providers:
                        self.output[ProviderDataColumns.HCP_ID.value].append(getattr(provider, ProviderDataColumns.HCP_ID.value))
                        self.output[ProviderDataColumns.AGE.value].append(getattr(provider, ProviderDataColumns.AGE.value))
                        self.output[ProgramDataColumns.YEAR.value].append(year)
                        self.output[WorksiteDataColumns.ULTIMATE_PARENT_ID.value].append(org.ultimate_parent_id)
                        self.output[OutputDataColumns.ORG_SIZE.value].append(org.number_of_dentists)

                        self.output[OutputDataColumns.WORKSITE_ID.value].append(worksite_id)
                        self.output[OutputDataColumns.CLASSIFICATION.value].append(classification)

        return pd.DataFrame(self.output)


class PracticeArrangement(AnalysisClass):

    def __init__(self, simplify_practice_arrangements: bool = False):
        super().__init__()
        self.simplify = simplify_practice_arrangements

        self.data = Data()

    def get_dataframe(self):
        formatter = Formatter()
        df = formatter.format(data=self.data,
                              simplify_arrangements=self.simplify)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[OutputDataColumns.WORKSITE_ID.value],
                                       provider_columns=[ProviderDataColumns.AGE.value],
                                       provider_at_worksite_columns=[ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value,
                                                                     ProviderAtWorksiteDataColumns.WK_WEEKS.value,
                                                                     ProviderAtWorksiteDataColumns.WK_HOURS.value,
                                                                     ProviderAtWorksiteDataColumns.SPECIALTY_NAME.value]
                                       )

