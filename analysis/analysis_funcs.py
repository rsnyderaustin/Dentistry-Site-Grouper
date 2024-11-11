from .analysis_enums import AnalysisFunctions
from entities import RequiredEntitiesColumns
from environment import Environment



def get_required_columns(func_enum):
    func_cols = {
        AnalysisFunctions.AGE_BY_ORG_SIZE: RequiredEntitiesColumns(worksite_columns=[],
                                                                   provider_columns=['age'],
                                                                   provider_at_worksite_columns=[]),
        AnalysisFunctions.HCP_IDS_BY_ORG_SIZE: RequiredEntitiesColumns(worksite_columns=[],
                                                                       provider_columns=['hcpid'],
                                                                       provider_at_worksite_columns=[])
    }

    if func_enum not in func_cols:
        raise ValueError(f"Could not find function {func_enum} in function columns dictionary.")

    return func_cols[func_enum]


def process_analysis_function(func_enum: AnalysisFunctions, environment) -> dict:
    funcs = {
        AnalysisFunctions.AGE_BY_ORG_SIZE: _get_age_by_organization_size,
        AnalysisFunctions.HCP_IDS_BY_ORG_SIZE: _get_dentist_id_by_organization_size
    }
    func = funcs[func_enum]
    return func(environment)

def _get_age_by_organization_size(environment: Environment):
    org_data = {}
    for organization in environment.organizations:
        org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
        ages = organization.get_provider_data(col='age')

        if org_size not in org_data:
            org_data[org_size] = []
        org_data[org_size].extend(ages)
    return org_data


def _get_dentist_id_by_organization_size(environment: Environment):
    org_data = {}
    for organization in environment.organizations:
        org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
        hcp_ids = organization.get_provider_data(col='hcpid')

        if org_size not in org_data:
            org_data[org_size] = []
        org_data[org_size].extend(hcp_ids)

    return org_data
