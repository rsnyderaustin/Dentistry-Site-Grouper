from enum import Enum


class ProgramDataColumns(Enum):
    YEAR = 'year'


class WorksiteDataColumns(Enum):
    ULTIMATE_PARENT_ID = 'ultimate_parent_id'
    WORKSITE_ID = 'worksite_id'
    PARENT_ID = 'parent_id'


class ProviderDataColumns(Enum):
    AGE = 'age'
    PROVIDER_ID = 'hcp_id'


class ProviderAtWorksiteDataColumns(Enum):
    PRAC_ARR_NAME = 'practice_arr_name'
    SPECIALTY_NAME = 'specialty_name'
    WK_WEEKS = 'wkweeks'


class PracticeArrangements(Enum):
    CORPORATE = 'Corporate'
    SOLO_PRACTICE = 'Solo Practice'
    HOSPITAL_SPONSORED_PRACTICE = 'Hospital Sponsored Practice'
    SATELLITE = 'Satellite'


class OutputDataColumns(Enum):
    ORG_SIZE = 'org_size'
    CLASSIFICATION = 'classification'
    WORKSITE_ID = 'worksite_id'

