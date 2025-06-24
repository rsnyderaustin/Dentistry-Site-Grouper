from enum import Enum


class WorksiteEnums:

    class Attributes(Enum):
        ULTIMATE_PARENT_ID = 'ultimate_parent_id'
        WORKSITE_ID = 'worksiteid'
        PARENT_ID = 'parentid'
        PRAC_ARR_NAME = 'practicearrname'
        PROGRAMMED_PRAC_ARR_NAME = 'programmed_prac_arr_name'

    class Status(Enum):
        OPEN = 'ACT'
        CLOSED = 'I'

    class PracticeArrangements(Enum):
        CORPORATE = 'Corporate'
        SOLO_PRACTICE = 'Solo Practice'
        HOSPITAL_SPONSORED_PRACTICE = 'Hospital Sponsored Practice'
        SATELLITE = 'Satellite'
        MULTISITE_DENTAL_GROUP = 'Multisite Dental Group'


class ProviderEnums:

    class Attributes(Enum):
        HCP_ID = 'hcpid'
        AGE = 'age'

    class AssignmentAttributes(Enum):
        ACTIVITY = 'activity'
        FTE = 'fte'
        SPECIALTY_NAME = 'specialtyname'
        WK_WEEKS = 'wkweeks'
        WK_HOURS = 'wkhours'
        WORKSITE_TYPE = 'worksitetype'

    class Fte(Enum):
        FULL_TIME = 'FT'
        PART_TIME = 'PT'

    class WorksiteType(Enum):
        PRIMARY = 'P'
        SECONDARY = 'S'


class ProgramColumns(Enum):
    YEAR = 'year'


class AnalysisFunctionAttributes(Enum):
    REQUIRED_PROVIDER_ATTRIBUTES_VARIABLE = 'REQUIRED_PROVIDER_ATTRIBUTES'


class OutputDataColumns(Enum):
    ORG_SIZE = 'org_size'
    CLASSIFICATION = 'classification'
    CLASSIFICATION_COMPLEX = 'classification_complex'
    WORKSITE_ID = 'worksiteid'
    NUMBER_OF_WORKSITE_SPECIALTIES = 'number_of_worksite_specialties'
    WORKSITE_SIZE = 'worksite_size'
    WORKSITE_SIZE_PRIMARY_ONLY = 'worksite_size_primary_only'
    SPECIALTIES_CLASS = 'specialties_class'
