from .worksite import Worksite
from .provider_assignment import ProviderAssignment
from column_enums import PracticeArrangements, ProviderAtWorksiteDataColumns


class Organization:

    def __init__(self, ult_parent_worksite: Worksite):
        self.ult_parent_worksite = ult_parent_worksite

        self.worksites_by_id = {
            self.ult_parent_worksite.worksite_id: self.ult_parent_worksite
        }
        self.providers = set()
        self.provider_assignments = set()

    @property
    def number_of_dentists(self):
        return len(self.providers)

    @property
    def ultimate_parent_id(self):
        return self.ult_parent_worksite.worksite_id

    def add_worksite(self, parent: Worksite, worksite: Worksite):
        current_parent = parent
        while current_parent != self.ult_parent_worksite:
            current_parent.child_worksites[worksite.worksite_id] = worksite
            current_parent = self.worksites_by_id[current_parent.parent_id]

        self.worksites_by_id[worksite.worksite_id] = worksite

    def add_provider_assignment(self, worksite: Worksite, provider_assignment: ProviderAssignment):
        if worksite.worksite_id not in self.worksites_by_id:
            raise KeyError(f"Attempted to add provider assignment to worksite with Worksite ID {worksite.worksite_id},"
                           f"when that Worksite ID is not present in this Organization's worksites.")
        self.provider_assignments.add(provider_assignment)

        worksite = self.worksites_by_id[worksite.worksite_id]
        worksite.add_provider_assignment(provider_assignment)

    def has_which_worksites(self, worksite_ids):
        has_worksites = {worksite for worksite in self.worksites_by_id.values() if worksite.worksite_id in worksite_ids}
        return has_worksites

    def determine_organization_size_classification(self, simplify: bool = False):
        organization_specialties = {provider_specialty for worksite in self.worksites_by_id.values() for provider_specialty in worksite.provider_specialties}
        specialties_class = 'Single Specialty' if len(organization_specialties) == 1 else 'Multi-Specialty'

        if simplify:
            practice_arrangements_by_org_size = {
                1: 'Solo Practice',
                2: f'2 Member Partnership',
                3: f'3-4 Member Group',
                4: f'3-4 Member Group',
                5: f'5-6 Member Group',
                6: f'5-6 Member Group',
            }
        else:
            practice_arrangements_by_org_size = {
                1: 'Solo Practice',
                2: f'2 Member Partnership / {specialties_class}',
                3: f'3-4 Member Group / {specialties_class}',
                4: f'3-4 Member Group / {specialties_class}',
                5: f'5-6 Member Group / {specialties_class}',
                6: f'5-6 Member Group / {specialties_class}',
            }

        if len(self.providers) >= 7:
            return f'7+ Member Group / {specialties_class}'

        return practice_arrangements_by_org_size[len(self.providers)]

    def classify(self, simplify: bool = False) -> dict:
        is_corporate = any([getattr(prov_assign, ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value) == PracticeArrangements.CORPORATE.value
                           for prov_assign in self.provider_assignments])
        if is_corporate:
            return {worksite.worksite_id: PracticeArrangements.CORPORATE.value for worksite in self.worksites_by_id.values()}

        is_hospital_sponsored = any(getattr(prov_assign, ProviderAtWorksiteDataColumns.PRAC_ARR_NAME.value) == PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value
                                    for prov_assign in self.provider_assignments)

        if is_hospital_sponsored:
            return {worksite.worksite_id: PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value for worksite in self.worksites_by_id.values()}

        ft_sites = 0
        for worksite in self.worksites_by_id.values():
            if worksite.has_full_time_provider():
                ft_sites += 1

        if ft_sites >= 2:
            return {worksite.worksite_id: PracticeArrangements.MULTISITE_DENTAL_GROUP.value for worksite in self.worksites_by_id.values()}

        classifications = {}
        primary_worksite = None
        for worksite in self.worksites_by_id.values():
            total_hours_visited = sum([getattr(prov_assign, ProviderAtWorksiteDataColumns.WK_WEEKS.value)
                                       for prov_assign in worksite.provider_assignments])
            if total_hours_visited < 30:
                classifications[worksite.worksite_id] = PracticeArrangements.SATELLITE.value
            else:
                primary_worksite = worksite

        if primary_worksite:
            classifications[primary_worksite.worksite_id] = self.determine_organization_size_classification(simplify=simplify)

        return classifications





