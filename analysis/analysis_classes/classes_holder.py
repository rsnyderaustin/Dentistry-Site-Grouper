from ..analysis_enums import AnalysisFunctions
from .age import AgeByOrgSize
from .organization_sizes import OrganizationSizes
from .practice_arrangement import PracticeArrangement


def get_analysis_class(func_enum: AnalysisFunctions):

    classes = {
        AnalysisFunctions.AGE_BY_ORG_SIZE: AgeByOrgSize,
        AnalysisFunctions.CLASSIFICATIONS: PracticeArrangement,
        AnalysisFunctions.ORGANIZATION_SIZES: OrganizationSizes
    }

    return classes[func_enum]

