
import pandas as pd

from .analysis_base_class import AnalysisClass, Data
from utils.enums import OutputDataColumns, ProgramColumns, ProviderEnums, WorksiteEnums
from processing import classify
from things import RequiredEntitiesColumns


class Formatter:

    def __init__(self):
        self.output = {
            ProgramColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderEnums.Attributes.HCP_ID.value: [],
            ProviderEnums.Attributes.AGE.value: [],
            OutputDataColumns.WORKSITE_ID.value: [],
            OutputDataColumns.CLASSIFICATION.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: []
        }

    def format(self, data: Data, simplify_arrangements: bool = False):
        orgs_by_year = data.organizations_by_year
        for year, orgs in orgs_by_year.items():
            for org in orgs:
                classifications = classify(organization=org,
                                           simplify=simplify_arrangements)

                for worksite_id, classification in classifications.items():
                    worksite = org.worksites_by_id[worksite_id]
                    providers = {prov_assign.provider for prov_assign in worksite.provider_assignments}

                    for provider in providers:
                        self.output[ProviderEnums.Attributes.HCP_ID.value].append(getattr(provider, ProviderEnums.Attributes.HCP_ID.value))
                        self.output[ProviderEnums.Attributes.AGE.value].append(getattr(provider, ProviderEnums.Attributes.AGE.value))
                        self.output[ProgramColumns.YEAR.value].append(year)
                        self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(org.ultimate_parent_id)
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
        return RequiredEntitiesColumns(worksite_columns=[WorksiteEnums.Attributes.PRAC_ARR_NAME,
                                                         OutputDataColumns.WORKSITE_ID],
                                       provider_columns=[ProviderEnums.Attributes.AGE],
                                       provider_at_worksite_columns=[ProviderEnums.AssignmentAttributes.FTE,
                                                                     ProviderEnums.AssignmentAttributes.WK_WEEKS,
                                                                     ProviderEnums.AssignmentAttributes.WK_HOURS,
                                                                     ProviderEnums.AssignmentAttributes.SPECIALTY_NAME]
                                       )

