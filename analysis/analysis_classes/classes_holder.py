from ..analysis_enums import AnalysisFunctions
from .age import AgeByOrgSize
from .practice_arrangement import PracticeArrangement


def get_analysis_class(func_enum: AnalysisFunctions):

    classes = {
        AnalysisFunctions.AGE_BY_ORG_SIZE: AgeByOrgSize,
        AnalysisFunctions.CLASSIFICATIONS: PracticeArrangement
    }

    return classes[func_enum]

