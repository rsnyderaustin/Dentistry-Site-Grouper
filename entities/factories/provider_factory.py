from column_enums import ProviderDataColumns
from entities import Provider


def apply_create_provider(row, providers, provider_params: list = None):
    hcp_id = row[ProviderDataColumns.PROVIDER_ID.value]
    provider_data = {param.value: row[param.value] for param in provider_params} if provider_params else {}
    if hcp_id not in providers:
        new_provider = Provider(hcp_id=hcp_id,
                                extra_data=provider_data)
        providers[hcp_id] = new_provider
    else:
        provider = providers[hcp_id]
        provider.add_data(provider_data)



