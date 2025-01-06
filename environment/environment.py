

class Environment:

    def __init__(self, year):
        self.year = year

        self.providers_by_id = dict()
        self.worksites_by_id = dict()
        self.organizations = dict()
