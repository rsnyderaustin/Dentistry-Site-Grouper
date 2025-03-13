
from things import Provider, ProviderAssignment, Worksite
from utils import ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums


def apply_create_entities(row,
                          required_cols: RequiredEntitiesColumns,
                          worksites_by_id: dict,
                          providers_by_id: dict):
    year = row[ProgramColumns.YEAR.value]
    hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
    parent_id = row[WorksiteEnums.Attributes.PARENT_ID.value]

    provider_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_columns}
    if hcp_id not in providers_by_id:
        provider = Provider(hcp_id=hcp_id,
                            **provider_data)
        providers_by_id[hcp_id] = provider

    worksite_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.worksite_columns}
    if worksite_id not in worksites_by_id:
        worksite = Worksite(worksite_id=worksite_id,
                            **worksite_data)
        worksites_by_id[worksite_id] = worksite

    provider = providers_by_id[hcp_id]
    worksite = worksites_by_id[worksite_id]

    assignment_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_at_worksite_columns}

    provider_assignment = ProviderAssignment(
        **provider_data,
        **worksite_data,
        **assignment_data
    )

    provider.add_assignment(
        year=year,
        assignment=provider_assignment
    )

    worksite.add_provider_assignment(
        year=year,
        assignment=provider_assignment
    )
