from ..analysis_enums import AnalysisFunctions
from .org_size import AgeByOrgSize


def get_analysis_class(func_enum: AnalysisFunctions):

    classes = {
        AnalysisFunctions.AGE_BY_ORG_SIZE: AgeByOrgSize
    }

    return classes[func_enum]

