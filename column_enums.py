from enum import Enum


class ProgramDataColumns(Enum):
    YEAR = 'year'


class WorksiteDataColumns(Enum):
    WORKSITE_ID = 'worksiteid'
    PARENT_ID = 'parentworksite'


class ProviderDataColumns(Enum):
    PROVIDER_ID = 'hcpid'

