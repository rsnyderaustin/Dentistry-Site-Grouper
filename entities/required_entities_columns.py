

class RequiredEntitiesColumns:

    def __init__(self, worksite_columns: list, provider_columns: list):
        self.worksite_columns = worksite_columns
        self.provider_columns = provider_columns

    @property
    def all_columns(self):
        return self.worksite_columns + self.provider_columns

