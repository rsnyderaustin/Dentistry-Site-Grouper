
import pandas as pd

from .analysis_base_class import AnalysisClass
from environment import Environment
from utils import OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums


class Formatter:

    def __init__(self):
        self.output = {
            ProgramColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: []
        }

    def format(self):
        for year, organizations in data.organizations_by_year.items():
            self.output[ProgramColumns.YEAR.value].extend([year for _ in range(len(organizations))])
            for org in organizations:
                self.output[OutputDataColumns.ORG_SIZE.value].append(org.number_of_dentists)
                self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(org.ultimate_parent_id)
        return pd.DataFrame(self.output)


class OrganizationSizes(AnalysisClass):

    def __init__(self):
        super().__init__()

    def analyze(self, env: Environment):
        pass

    def get_dataframe(self):
        pass

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[],
                                       provider_columns=[],
                                       provider_at_worksite_columns=[])