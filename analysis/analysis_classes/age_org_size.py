
from .analysis_class import AnalysisClass


class AgeByOrgSize(AnalysisClass):

    def __init__(self, environments):
        super().__init__()
        self.environments = environments

    def process_data(self, environment: Environment):
        org_data = {}
        for organization in environment.organizations:
            org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
            ages = organization.get_provider_data(col='age')

            if org_size not in org_data:
                org_data[org_size] = []
            org_data[org_size].extend(ages)
        return org_data