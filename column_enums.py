from enum import Enum


class ProgramDataColumns(Enum):
    YEAR = 'year'


class WorksiteDataColumns(Enum):
    ULTIMATE_PARENT_ID = 'ultimate_parent_id'
    WORKSITE_ID = 'worksiteid'
    PARENT_ID = 'parentid'
    SITE_STATUS = 'site_status'
    LATITUDE = 'site_latitude'
    LONGITUDE = 'site_longitude'


class SiteStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class ProviderDataColumns(Enum):
    AGE = 'age'
    HCP_ID = 'hcpid'


class ProviderAtWorksiteDataColumns(Enum):
    PRAC_ARR_NAME = 'practice_arr_name'
    SPECIALTY_NAME = 'specialtyname'
    WK_WEEKS = 'wkweeks'
    WK_HOURS = 'wkhours'
    FULL_TIME = 'FT'
    PART_TIME = 'PT'


class PracticeArrangements(Enum):
    CORPORATE = 'Corporate'
    SOLO_PRACTICE = 'Solo Practice'
    HOSPITAL_SPONSORED_PRACTICE = 'Hospital Sponsored Practice'
    SATELLITE = 'Satellite'
    MULTISITE_DENTAL_GROUP = 'Multisite Dental Group'


class OutputDataColumns(Enum):
    ORG_SIZE = 'org_size'
    CLASSIFICATION = 'classification'
    WORKSITE_ID = 'worksiteid'

