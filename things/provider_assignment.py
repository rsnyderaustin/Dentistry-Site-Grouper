from .provider import Provider
from .worksite import Worksite
from column_enums import ProviderDataColumns, ProviderAtWorksiteDataColumns


class ProviderAssignment:

    def __init__(self, provider: Provider, worksite: Worksite, **kwargs):
        self.provider = provider
        self.worksite = worksite

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def hcp_id(self):
        return getattr(self.provider, ProviderDataColumns.HCP_ID.value)

    @property
    def fte(self):
        wkweeks = getattr(self, ProviderAtWorksiteDataColumns.WK_WEEKS.value)
        wkhours = getattr(self, ProviderAtWorksiteDataColumns.WK_HOURS.value)

        if (wkweeks, wkhours) in ((12, 16), (26, 34)):
            return ProviderAtWorksiteDataColumns.FULL_TIME.value

        fte = ProviderAtWorksiteDataColumns.FULL_TIME.value if wkweeks >= 42 else ProviderAtWorksiteDataColumns.PART_TIME.value
        return fte
