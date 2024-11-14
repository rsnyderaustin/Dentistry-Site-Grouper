
from column_enums import ProviderDataColumns


class Provider:

    def __init__(self, hcp_id: int, provider_data: dict = None):
        setattr(self, ProviderDataColumns.PROVIDER_ID.value, hcp_id)

        self.assignments = set()

        if provider_data:
            for k, v in provider_data.items():
                setattr(self, k, v)

    def get_assignment(self, worksite_id):
        for assignment in self.assignments:
            if assignment.worksiteid == worksite_id:
                return assignment
