from enum import Enum
from itertools import product
from typing import Iterable

import pandas as pd

from utils.classify_provider_fte import ProviderFteClassifier, IsWeekly
from environment import Environment
from analysis.analysis_classes.analysis_base_class import AnalysisClass
from things import Organization, ProviderAssignment, Worksite
from utils import OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums, OrganizationEnums

import logging


def _determine_worksite_status(year: int, worksite: Worksite):
    total_hours = 0
    provider_assignments = worksite.fetch_provider_assignments(year=year)
    for assignment in provider_assignments:
        total_hours += (assignment[ProviderEnums.AssignmentAttributes.WK_HOURS.value]
                        *
                        assignment[ProviderEnums.AssignmentAttributes.WK_WEEKS.value])


def _determine_specialties_class(assignments: Iterable[ProviderAssignment]):
    organization_specialties = {
        getattr(assignment, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value)
        for assignment in assignments
    }
    specialties_class = 'Single Specialty' if len(organization_specialties) == 1 else 'Multi-Specialty'
    return specialties_class


def _determine_organization_size_classification(worksites: Iterable[Worksite], year: int, simplify: bool = False):
    assignments = {assignment for worksite in worksites for assignment in worksite.fetch_provider_assignments(year=year)}

    specialties_class = _determine_specialties_class(assignments=assignments)

    if simplify:
        return 'Main Worksite'
    else:
        practice_arrangements_by_org_size = {
            1: 'Solo Practice',
            2: f'2 Member Partnership / {specialties_class}',
            3: f'3-4 Member Group / {specialties_class}',
            4: f'3-4 Member Group / {specialties_class}',
            5: f'5-6 Member Group / {specialties_class}',
            6: f'5-6 Member Group / {specialties_class}',
        }
        if len(assignments) >= 7:
            return f'7+ Member Group / {specialties_class}'

    return practice_arrangements_by_org_size[len(assignments)]


class Formatter:

    def __init__(self):
        self.row_data = dict()
        self.rows_inputted = 0

    def output_data(
            self,
            year: int,
            worksite: Worksite,
            organization: Organization,
            organization_structure: OrganizationEnums.Structure,
            practice_arrangement: WorksiteEnums.PracticeArrangements
    ):
        if self.rows_inputted == 0:
            self.row_data[ProgramColumns.YEAR.value] = []
            self.row_data[OutputDataColumns.ORG_SIZE.value] = []
            self.row_data[WorksiteEnums.Attributes.WORKSITE_ID.value] = []
            self.row_data[WorksiteEnums.Attributes.WORKSITE_NAME.value] = []
            self.row_data[WorksiteEnums.Attributes.PRAC_ARR_NAME.value] = []
            self.row_data[OrganizationEnums.Attributes.STRUCTURE.value] = []

        self.row_data[ProgramColumns.YEAR.value].append(year)
        self.row_data[OutputDataColumns.ORG_SIZE.value].append(organization.determine_number_of_dentists(year=year))
        self.row_data[WorksiteEnums.Attributes.WORKSITE_ID.value].append(worksite.worksite_id)
        self.row_data[WorksiteEnums.Attributes.WORKSITE_NAME.value].append(getattr(worksite, WorksiteEnums.Attributes.WORKSITE_NAME.value))
        self.row_data[WorksiteEnums.Attributes.PRAC_ARR_NAME.value].append(practice_arrangement.value)
        self.row_data[OrganizationEnums.Attributes.STRUCTURE.value].append(organization_structure.value)

        self.rows_inputted += 1


class PracticeArrangement(AnalysisClass):
    FULL_TIME_WEEKLY_HOURS = 32 * 48

    org_structure_terms = {
        OrganizationEnums.Structure.GOVERNMENT_MANAGED: [
            'Correctional',
            'Penitent'
        ],
        OrganizationEnums.Structure.COMMUNITY_HEALTH: [
            'Community',
            'Health Center',
            'Infinity Health',
            'Primary Health Care',
            'AllCare'
        ]
    }

    def __init__(self):
        super().__init__()

        self.formatter = Formatter()

    def analyze_environment(self, years: list[int], env: Environment, simplify: bool = True) -> pd.DataFrame:
        for year, organization in product(years, env.organizations):
            self.classify(
                organization=organization,
                year=year
            )

        logging.info(f"There are {len(set(self.formatter.row_data[WorksiteEnums.Attributes.WORKSITE_ID.value]))} distinct worksite ID's in the output data.")
        df = pd.DataFrame(self.formatter.row_data)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[WorksiteEnums.Attributes.PRAC_ARR_NAME,
                                                         WorksiteEnums.Attributes.SITE_TYPE_NAME,
                                                         WorksiteEnums.Attributes.WORKSITE_NAME,
                                                         OutputDataColumns.WORKSITE_ID],
                                       provider_columns=[],
                                       provider_at_worksite_columns=[ProviderEnums.AssignmentAttributes.WK_WEEKS,
                                                                     ProviderEnums.AssignmentAttributes.WK_HOURS,
                                                                     ProviderEnums.AssignmentAttributes.SPECIALTY_NAME,
                                                                     ProviderEnums.AssignmentAttributes.WORKSITE_TYPE]
                                       )

    @staticmethod
    def _name_has_term(name: str, terms: list[str]):
        name = name.lower()
        for term in terms:
            if term.lower() in name:
                return True

        return False

    @classmethod
    def _determine_if_community_health(cls, organization: Organization, year: int) -> bool:
        ultimate_parent_name = getattr(
            organization.ultimate_parent_worksite,
            WorksiteEnums.Attributes.WORKSITE_NAME.value
        )

        if cls._name_has_term(
                ultimate_parent_name,
                PracticeArrangement.org_structure_terms[OrganizationEnums.Structure.COMMUNITY_HEALTH]
        ):
            return True

        assignments = organization.fetch_provider_assignments(year=year)
        activities = [
            getattr(
                assignment,
                ProviderEnums.AssignmentAttributes.ACTIVITY.value
            ) for assignment in assignments
        ]
        return any([activity == 'Community Health/Local Government' for activity in activities])

    @staticmethod
    def _determine_if_dso(organization: Organization) -> bool:
        ultimate_parent_site_type = getattr(
            organization.ultimate_parent_worksite,
            WorksiteEnums.Attributes.SITE_TYPE_NAME.value
        )

        return 'MSO' in ultimate_parent_site_type

    @staticmethod
    def _determine_if_corporate(organization: Organization, year: int) -> bool:
        practice_arrangements = organization.fetch_worksite_attributes(
            year=year,
            attribute=WorksiteEnums.Attributes.PRAC_ARR_NAME.value
        )

        return any([prac_arr == 'Corporate' for prac_arr in practice_arrangements])

    @staticmethod
    def _determine_if_government(organization: Organization, year: int) -> bool:
        ultimate_parent_name = getattr(
            organization.ultimate_parent_worksite,
            WorksiteEnums.Attributes.WORKSITE_NAME.value
        )

        if 'university' in ultimate_parent_name.lower():
            return True

        assignments = organization.fetch_provider_assignments(year=year)
        activities = [
            getattr(
                assignment,
                ProviderEnums.AssignmentAttributes.ACTIVITY.value
            )
            for assignment in assignments
        ]
        gov_terms = ['State/Federal Government', 'Veterans Administration', 'Dental School Faculty']
        return any([activity in gov_terms for activity in activities])

    @classmethod
    def _determine_if_hospital_network(cls, organization: Organization, year: int):
        ultimate_parent_name = getattr(
            organization.ultimate_parent_worksite,
            WorksiteEnums.Attributes.WORKSITE_NAME.value
        )
        assignments = organization.fetch_provider_assignments(year=year)
        activities = [
            getattr(
                assignment,
                ProviderEnums.AssignmentAttributes.ACTIVITY.value
            ) for assignment in assignments
        ]
        practice_arrangements = [
            getattr(
                worksite,
                WorksiteEnums.Attributes.PRAC_ARR_NAME.value
            ) for worksite in organization.worksites
        ]
        site_types = [
            getattr(
                worksite,
                WorksiteEnums.Attributes.SITE_TYPE_NAME.value
            ) for worksite in organization.worksites
        ]
        return (
            cls._name_has_term(ultimate_parent_name, ['hospital', 'health system'])
            or any(['hospital' in prac_arr.lower() for prac_arr in practice_arrangements])
            or any(['hospital' in site_type.lower() for site_type in site_types])
            or any([activity == 'Hospital Staff Dentist' for activity in activities])
        )

    def classify(self, organization: Organization, year: int):

        worksites = organization.fetch_worksites(year=year)
        if not worksites:
            return

        # Determine DSO before corporate because DSO is sort-of a more specific version of a corporate relationship and there is overlap
        if self._determine_if_dso(organization):
            print("Organization is a DSO.")
            for worksite in worksites:
                prac_arr = (
                    WorksiteEnums.PracticeArrangements.SATELLITE if not worksite.is_staffed_full_time(year=year)
                    else WorksiteEnums.PracticeArrangements.FULL_TIME_CLINIC
                )
                self.formatter.output_data(
                    year=year,
                    worksite=worksite,
                    organization=organization,
                    organization_structure=OrganizationEnums.Structure.DENTAL_SERVICES_ORGANIZATION,
                    practice_arrangement=prac_arr
                )
            return

        if self._determine_if_corporate(organization, year=year):
            print("Organization is corporate.")
            for worksite in worksites:
                prac_arr = (
                    WorksiteEnums.PracticeArrangements.SATELLITE if not worksite.is_staffed_full_time(year=year)
                    else WorksiteEnums.PracticeArrangements.FULL_TIME_CLINIC
                )
                self.formatter.output_data(
                    year=year,
                    worksite=worksite,
                    organization=organization,
                    organization_structure=OrganizationEnums.Structure.CORPORATION,
                    practice_arrangement=prac_arr
                )
            return

        if self._determine_if_government(organization, year=year):
            print("Organization is government.")
            correctional_terms = [
                'Correctional',
                'Penitent'
            ]
            for worksite in worksites:
                if self._name_has_term(
                        getattr(
                            worksite,
                            WorksiteEnums.Attributes.WORKSITE_NAME.value
                        ),
                        correctional_terms
                ):
                    prac_arr = WorksiteEnums.PracticeArrangements.CORRECTIONAL_FACILITY
                else:
                    assignments = worksite.fetch_provider_assignments(year=year)
                    activities = [getattr(assignment, ProviderEnums.AssignmentAttributes.ACTIVITY.value) for assignment in assignments]
                    if any([activity == 'Veterans Administration' for activity in activities]):
                        prac_arr = WorksiteEnums.PracticeArrangements.VETERANS_ADMINISTRATION
                    else:
                        prac_arr = WorksiteEnums.PracticeArrangements.OTHER_GOV

                self.formatter.output_data(
                    year=year,
                    worksite=worksite,
                    organization=organization,
                    organization_structure=OrganizationEnums.Structure.GOVERNMENT_MANAGED,
                    practice_arrangement=prac_arr
                )
            return

        if self._determine_if_community_health(organization, year=year):
            print("Organization is community health.")
            for worksite in worksites:
                self.formatter.output_data(
                    year=year,
                    worksite=worksite,
                    organization=organization,
                    organization_structure=OrganizationEnums.Structure.COMMUNITY_HEALTH,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.COMMUNITY_HEALTH
                )
            return
        
        if self._determine_if_hospital_network(organization, year=year):
            print("Organization is hospital netework.")
            for worksite in worksites:
                prac_arr = (
                    WorksiteEnums.PracticeArrangements.FULL_TIME_CLINIC if worksite.is_staffed_full_time(year=year)
                    else WorksiteEnums.PracticeArrangements.SATELLITE
                )
                self.formatter.output_data(
                    year=year,
                    worksite=worksite,
                    organization=organization,
                    organization_structure=OrganizationEnums.Structure.HOSPITAL_NETWORK,
                    practice_arrangement=prac_arr
                )

        print("Organization is independent.")
        org_structure = OrganizationEnums.Structure.INDEPENDENT
        for worksite in worksites:
            prac_arr = (
                WorksiteEnums.PracticeArrangements.FULL_TIME_CLINIC if worksite.is_staffed_full_time(year=year)
                else WorksiteEnums.PracticeArrangements.SATELLITE
            )
            self.formatter.output_data(
                year=year,
                worksite=worksite,
                organization=organization,
                organization_structure=org_structure,
                practice_arrangement=prac_arr
            )
