from entities import Organization


class Analyzer:

    def __init__(self, organizations: set[Organization]):
        self.organizations = organizations

    def get_organization_sizes(self) -> dict:
        org_sizes = {}
        for organization in self.organizations:
            org_size = organization.ult_parent_worksite.number_of_child_worksites + 1
            org_sizes[organization] = org_size
        return org_sizes
