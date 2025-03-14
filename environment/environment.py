

class Environment:

    def __init__(self):
        self.providers_by_id = dict()
        self.worksites_by_id = dict()
        self.organizations_by_id = dict()

    @property
    def organizations(self) -> list:
        return list(self.organizations_by_id.values())
