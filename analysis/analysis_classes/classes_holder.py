from ..analysis_enums import AnalysisFunctions
from .age_org_size import AgeByOrgSize
from .prov_assign_org_size import ProvAssignByOrgSize


def get_analysis_class(func_enum: AnalysisFunctions):

    classes = {
        AnalysisFunctions.PROV_ASSIGNS_BY_ORG_SIZE: ProvAssignByOrgSize,
        AnalysisFunctions.AGE_BY_ORG_SIZE: AgeByOrgSize
    }

    return classes[func_enum]

