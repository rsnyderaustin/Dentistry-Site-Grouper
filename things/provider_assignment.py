from utils import WorksiteEnums, ProviderEnums


class ProviderAssignment:

    def __init__(self, worksite, provider, assignment_data: dict, worksite_type: str, activity: str):
        self.worksite = worksite
        self.provider = provider

        for k, v in assignment_data.items():
            setattr(self, k, v)

        setattr(self, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value, worksite_type)
        setattr(self, ProviderEnums.AssignmentAttributes.ACTIVITY.value, activity)