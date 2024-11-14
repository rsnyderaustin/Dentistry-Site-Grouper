from enum import Enum


class ProgramDataColumns(Enum):
    YEAR = 'year'


class WorksiteDataColumns(Enum):
    ULTIMATE_PARENT_ID = 'ultimateparentid'
    WORKSITE_ID = 'worksiteid'
    PARENT_ID = 'parentid'


class ProviderDataColumns(Enum):
    AGE = 'age'
    PROVIDER_ID = 'hcpid'


class ProviderAtWorksiteDataColumns(Enum):
    PRAC_ARR_NAME = 'practicearrname'


class OutputDataColumns(Enum):
    ORG_SIZE = 'org_size'

