from enum import Enum


class ProgramDataColumns(Enum):
    YEAR = 'year'


class WorksiteDataColumns(Enum):
    WORKSITE_ID = 'worksiteid'
    PARENT_ID = 'parentworksite'


class ProviderDataColumns(Enum):
    AGE = 'age'
    PROVIDER_ID = 'hcpid'
    PRAC_ARR_NAME = 'practicearrname'


class OutputDataColumns(Enum):
    ORG_SIZE = 'org_size'

