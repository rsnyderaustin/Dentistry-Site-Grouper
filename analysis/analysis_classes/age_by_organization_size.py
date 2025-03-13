import pandas as pd

from .analysis_base_class import AnalysisClass
from utils import OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums


class Formatter:

    def __init__(self):
        self.output = {
            ProgramColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderEnums.Attributes.AGE.value: [],
            ProviderEnums.Attributes.HCP_ID.value: [],
            WorksiteEnums.Attributes.PRAC_ARR_NAME.value: [],
            ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value: [],
            WorksiteEnums.Attributes.WORKSITE_ID.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: []
        }

    def format_prov_assign_by_org_size(self, data: Data):
        for year, ult_parent_id, org_size, provider_assignment in data.data_generator():
            provider = provider_assignment.provider
            worksite = provider_assignment.worksite
            self.output[ProgramColumns.YEAR.value].append(year)
            self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
            self.output[ProviderEnums.Attributes.AGE.value].append(
                getattr(provider, ProviderEnums.Attributes.AGE.value)
            )
            self.output[ProviderEnums.Attributes.HCP_ID.value].append(
                getattr(provider, ProviderEnums.Attributes.HCP_ID.value)
            )
            self.output[WorksiteEnums.Attributes.PRAC_ARR_NAME.value].append(
                getattr(provider_assignment, WorksiteEnums.Attributes.PRAC_ARR_NAME.value)
            )
            self.output[ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value].append(
                getattr(provider_assignment, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value)
            )
            self.output[WorksiteEnums.Attributes.WORKSITE_ID.value].append(
                getattr(worksite, WorksiteEnums.Attributes.WORKSITE_ID.value)
            )
            self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(ult_parent_id)
        return pd.DataFrame(self.output)


class AgeByOrgSize(AnalysisClass):

    def __init__(self):
        super().__init__()

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
                                       provider_columns=[ProviderEnums.Attributes.AGE.value],
                                       provider_at_worksite_columns=[ProviderEnums.Attributes.PRAC_ARR_NAME.value,
                                                                     ProviderEnums.Attributes.SPECIALTY_NAME.value])

