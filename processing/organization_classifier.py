
import logging

from utils.enums import ProviderEnums, WorksiteEnums
from things import Organization, Worksite


def _total_worksite_hours(worksite: Worksite):
    total_hours = 0
    for assignment in worksite.provider_assignments:
        total_hours += (getattr(assignment, ProviderEnums.AssignmentAttributes.WK_HOURS.value)
                        *
                        getattr(assignment, ProviderEnums.AssignmentAttributes.WK_WEEKS.value))
    return total_hours

def _determine_organization_size_classification(organization: Organization, simplify: bool = False):
    organization_specialties = {provider_specialty for worksite in organization.worksites_by_id.values() for provider_specialty in worksite.provider_specialties}
    specialties_class = 'Single Specialty' if len(organization_specialties) == 1 else 'Multi-Specialty'

    if simplify:
        if len(organization.providers) == 1:
            return 'Solo Practice'
        elif len(organization.providers) == 2:
            return '2 Member Partnership'
        elif len(organization.providers) <= 5:
            return '3 - 5 Member Group'
        elif len(organization.providers) <= 8:
            return '6 - 8 Member Group'
        elif len(organization.providers) >= 9:
            return '9+ Member Group'
        else:
            return 'ERROR - NO PROVIDERS?'
    else:
        practice_arrangements_by_org_size = {
            1: 'Solo Practice',
            2: f'2 Member Partnership / {specialties_class}',
            3: f'3-4 Member Group / {specialties_class}',
            4: f'3-4 Member Group / {specialties_class}',
            5: f'5-6 Member Group / {specialties_class}',
            6: f'5-6 Member Group / {specialties_class}',
        }
        if len(organization.providers) >= 7:
            return f'7+ Member Group / {specialties_class}'

    return practice_arrangements_by_org_size[len(organization.providers)]


def classify(organization, simplify: bool = False) -> dict:
    if not organization.worksites:
        return dict()

    is_corporate = any([getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.CORPORATE.value
                        for worksite in organization.worksites])
    if is_corporate:
        return {worksite.worksite_id: WorksiteEnums.PracticeArrangements.CORPORATE.value for worksite in organization.worksites_by_id.values()}

    is_hospital_sponsored = any([getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value
                                 for worksite in organization.worksites])
    if is_hospital_sponsored:
        return {worksite.worksite_id: WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value for worksite in organization.worksites_by_id.values()}

    ft_sites = [worksite for worksite in organization.worksites
                if any([getattr(assignment, ProviderEnums.AssignmentAttributes.FTE.value) == ProviderEnums.Fte.FULL_TIME.value
                    for assignment in worksite.provider_assignments])]

    if len(ft_sites) >= 2:
        return {worksite.worksite_id: WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value for worksite in organization.worksites_by_id.values()}

    # At this point this organization has to be a primary site and a set of satellites
    satellites = [worksite for worksite in organization.worksites
                  if getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.SATELLITE.value]
    possible_primaries = [worksite for worksite in organization.worksites if worksite not in satellites]

    if not possible_primaries:
        logging.info(f"Organization with ultimate worksite {organization.ultimate_parent_id} and worksites "
                           f"{[w.worksite_id for w in organization.worksites]} has no non-satellites.")
        return dict()

    primary_worksite = max(
        possible_primaries,
        key=lambda w: _total_worksite_hours(worksite=w)
    )
    satellites = [worksite for worksite in organization.worksites if worksite != primary_worksite]

    return {
        primary_worksite.worksite_id: _determine_organization_size_classification(organization=organization,
                                                                                  simplify=simplify),
        **{worksite.worksite_id: WorksiteEnums.PracticeArrangements.SATELLITE.value for worksite in satellites}
    }