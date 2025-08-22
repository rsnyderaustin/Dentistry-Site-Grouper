from enum import Enum


class OrganizationEnums:

    class Attributes(Enum):
        STRUCTURE = 'organization_structure'

    class Structure(Enum):
        DENTAL_SERVICES_ORGANIZATION = 'DSO'
        CORPORATION = 'Corporation'
        INDEPENDENT = 'Independent'
        GOVERNMENT_MANAGED = 'Government-Managed'
        COMMUNITY_HEALTH = 'Community Health'
        HOSPITAL_NETWORK = 'Hospital Network'

class WorksiteEnums:

    class Attributes(Enum):
        ULTIMATE_PARENT_ID = 'ultimate_parent_id'
        WORKSITE_ID = 'worksiteid'
        WORKSITE_NAME = 'worksitename'
        PARENT_ID = 'parentid'
        PRAC_ARR_NAME = 'practicearrname'
        PROGRAMMED_PRAC_ARR_NAME = 'programmed_prac_arr_name'
        SITE_TYPE_NAME = 'sitetypename'

    class Status(Enum):
        OPEN = 'ACT'
        CLOSED = 'I'

    class PracticeArrangements(Enum):
        FULL_TIME_CLINIC = 'Full-Time Clinic'
        SATELLITE = 'Satellite Clinic'
        HOSPITAL_BASED = 'Hospital Based'
        COMMUNITY_HEALTH = 'Community Health'
        CORRECTIONAL_FACILITY = 'Correctional Facility'
        VETERANS_ADMINISTRATION = 'Veterans Administration'
        OTHER_GOV = 'Other Government'
        NON_CLINICAL_MANAGEMENT = 'Non-Clinical Management'


class ProviderEnums:

    class Attributes(Enum):
        HCP_ID = 'hcpid'
        AGE = 'age'

    class AssignmentAttributes(Enum):
        ACTIVITY = 'activityname'
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
    NUMBER_OF_WORKSITE_PROVIDERS = 'worksite_provider_count'
    NUMBER_OF_WORKSITE_SPECIALTIES = 'worksite_specialties_count'
    WORKSITE_SIZE = 'worksite_size'
    WORKSITE_SIZE_PRIMARY_ONLY = 'worksite_size_primary_only'
    SPECIALTIES_CLASS = 'specialties_class'
