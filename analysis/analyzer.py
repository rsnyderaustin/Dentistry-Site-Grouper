
from entities import RequiredEntitiesColumns


class AnalysisRequest:

    def __init__(self, required_cols, analysis_func):
        self.required_cols = required_cols
        self.analysis_func = analysis_func


class Analyzer:

    def __init__(self, environment):
        self.environment = environment

    def __call__(self, analysis_request: AnalysisRequest):
        return analysis_request.analysis_func()

    def get_age_by_organization_size(self):
        required_cols = RequiredEntitiesColumns(worksite_columns=[],
                                                provider_columns=['age'],
                                                provider_at_worksite_columns=[])
        analysis_request = AnalysisRequest(required_cols=required_cols,
                                           analysis_func=self._get_age_by_organization_size_func)
        return analysis_request

    def _get_age_by_organization_size_func(self):
        org_data = {}
        for organization in self.environment.organizations:
            org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
            ages = organization.get_provider_data(col='age')

            if org_size not in org_data:
                org_data[org_size] = []
            org_data[org_size].extend(ages)
        return org_data

    def get_dentist_id_by_organization_size(self):
        required_cols = RequiredEntitiesColumns(worksite_columns=[],
                                                provider_columns=['hcpid'],
                                                provider_at_worksite_columns=[])
        analysis_request = AnalysisRequest(required_cols=required_cols,
                                           analysis_func=self._get_dentist_id_by_organization_size_func)
        return analysis_request

    def _get_dentist_id_by_organization_size_func(self):
        org_data = {}
        for organization in self.environment.organizations:
            org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
            hcp_ids = organization.get_provider_data(col='hcpid')


            if org_size not in org_data:
                org_data[org_size] = []
            org_data[org_size].extend(hcp_ids)

        return org_data


