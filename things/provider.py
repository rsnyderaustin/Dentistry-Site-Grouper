
import pandas as pd

from utils.enums import ProviderEnums


class Provider:

    def __init__(self, hcp_id: int, **kwargs):
        setattr(self, ProviderEnums.Attributes.HCP_ID.value, hcp_id)

        self.assignments = set()

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_assignment(self, worksite_id):
        for assignment in self.assignments:
            if assignment.worksite_id == worksite_id:
                return assignment

    @property
    def fte(self):
        if any([getattr(assignment, ProviderEnums.AssignmentAttributes.FTE.value) == ProviderEnums.Fte.FULL_TIME.value]
                for assignment in self.assignments):
            return ProviderEnums.Fte.FULL_TIME.value
        else:
            return ProviderEnums.Fte.PART_TIME.value
