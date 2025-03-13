
from analysis import RequiredEntitiesColumns
from things import Provider, ProviderAssignment, Worksite
from utils.enums import ProgramColumns, ProviderEnums, WorksiteEnums


def apply_create_entities(row,
                          required_cols: RequiredEntitiesColumns,
                          worksites_by_id: dict,
                          providers_by_id: dict):
    year = row[ProgramColumns.YEAR.value]
    hcp_id = row[ProviderEnums.Attributes.HCP_ID.value]
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]
    parent_id = row[WorksiteEnums.Attributes.PARENT_ID.value]

    if hcp_id not in providers_by_id:
        provider_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.provider_columns}
        provider = Provider(hcp_id=hcp_id,
                            **provider_data)
        providers_by_id[hcp_id] = provider

    if worksite_id not in worksites_by_id:
        worksite_data = {col_enum.value: row[col_enum.value] for col_enum in required_cols.worksite_columns}
        worksite = Worksite(worksite_id=worksite_id,
                            **worksite_data)
        worksites_by_id[worksite_id] = worksite

    provider = providers_by_id[hcp_id]
    worksite = worksites_by_id[worksite_id]

    provider_assignment = ProviderAssignment(
        provider=provider,
        worksite=worksite
    )

    provider.add_assignment(
        year=year,
        assignment=provider_assignment
    )

    worksite.add_provider_assignment(
        year=year,
        assignment=provider_assignment
