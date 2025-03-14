
from .provider_assignment import ProviderAssignment


class ProviderAssignmentsTracker:

    def __init__(self):
        self.assignments_by_year = dict()

    def add_assignment(self, year: int, assignment: ProviderAssignment):
        if year not in self.assignments_by_year:
            self.assignments_by_year[year] = list()

        self.assignments_by_year[year].append(assignment)

    def fetch_assignments(self, year: int = None):
        if year:
            return self.assignments_by_year[year] if year in self.assignments_by_year else []
        else:
            return [assignment for year, assignments in self.assignments_by_year.items() for assignment in assignments]
