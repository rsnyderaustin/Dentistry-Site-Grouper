
import configparser
from dataclasses import dataclass
from itertools import product
import logging
import pandas as pd

from environment import Environment
from .analysis_base_class import AnalysisClass
from things import Organization, ProviderAssignment, Worksite
from utils import config, OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums

import logging


@dataclass
class HoursWeeks:
    hours: int
    weeks: int


class WeirdFteTable:

    table = {
        4: 5,
        5: 7,
        6: 8,
        7: 9,
        8: 10,
        9: 12,
        10: 13,
        11: 14,
        12: 16,
        13: 17,
        14: 18,
        15: 20,
        16: 21,
        17: 22,
        18: 23,
        19: 25,
        21: 27,
        22: 29,
        23: 30,
        24: 31,
        25: 33,
        26: 34,
        27: 35,
        28: 26,
        29: 38,
        30: 39,
        31: 40,
        32: 42,
        33: 43,
        34: 44,
        35: 46,
        36: 47,
        37: 48,
        38: 49,
        39: 51
    }

    @classmethod
    def convert_assignment_hours(cls, assignment: ProviderAssignment):
        hours = assignment.assignment_data[ProviderEnums.AssignmentAttributes.WK_HOURS.value]
        weeks = assignment.assignment_data[ProviderEnums.AssignmentAttributes.WK_WEEKS.value]

        if weeks == cls.table[hours]:
            return HoursWeeks(hours=hours, weeks=52)
        else:
            return HoursWeeks(hours=hours, weeks=weeks)


full_time_hours = 8 * 52


def _determine_worksite_status(year: int, worksite: Worksite):
    total_hours = 0
    provider_assignments = worksite.fetch_provider_assignments(year=year)
    for assignment in provider_assignments:
        total_hours += (assignment.assignment_data[ProviderEnums.AssignmentAttributes.WK_HOURS.value]
                        *
                        assignment.assignment_data[ProviderEnums.AssignmentAttributes.WK_WEEKS.value])



def _determine_organization_size_classification(organization_assignments, simplify: bool = False):
    organization_specialties = {
        assignment.assignment_data[ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value]
        for assignment in organization_assignments
    }
    number_of_providers = len(set(assignment.provider for assignment in organization_assignments))
    specialties_class = 'Single Specialty' if len(organization_specialties) == 1 else 'Multi-Specialty'

    if simplify:
        if number_of_providers == 1:
            return 'Solo Practice'
        elif number_of_providers == 2:
            return '2 Member Partnership'
        elif number_of_providers <= 5:
            return '3 - 5 Member Group'
        elif number_of_providers <= 8:
            return '6 - 8 Member Group'
        elif number_of_providers >= 9:
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
        if len(organization_assignments) >= 7:
            return f'7+ Member Group / {specialties_class}'

    return practice_arrangements_by_org_size[len(organization_assignments)]


class Formatter:

    def __init__(self):
        self.output = {
            ProgramColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            ProviderEnums.Attributes.HCP_ID.value: [],
            ProviderEnums.Attributes.AGE.value: [],
            OutputDataColumns.WORKSITE_ID.value: [],
            OutputDataColumns.CLASSIFICATION.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: []
        }

    def _output_data(self, assignment: ProviderAssignment, year: int, org_size: int, ultimate_parent_id: int, practice_arrangement):
        self.output[ProgramColumns.YEAR.value].append(year)
        self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
        self.output[ProviderEnums.Attributes.HCP_ID.value].append(getattr(assignment.provider, ProviderEnums.Attributes.HCP_ID.value))
        self.output[ProviderEnums.Attributes.AGE.value].append(getattr(assignment.provider, ProviderEnums.Attributes.AGE.value))
        self.output[OutputDataColumns.WORKSITE_ID.value].append(getattr(assignment.worksite, WorksiteEnums.Attributes.WORKSITE_ID.value))
        self.output[OutputDataColumns.CLASSIFICATION.value].append(practice_arrangement),
        self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(ultimate_parent_id)

    def classify(self, organization: Organization, year: int):
        organization_assignments = organization.fetch_provider_assignments(year=year)
        worksites = {assignment.worksite for assignment in organization_assignments}
        if not worksites:
            return
        providers = {assignment.provider for assignment in organization_assignments}

        is_corporate = any([getattr(assignment.worksite,
                                    WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.CORPORATE.value
                            for assignment in organization_assignments])
        if is_corporate:
            for assignment in organization_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.CORPORATE.value
                )
            return

        is_hospital_sponsored = any([getattr(worksite,
                                             WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value
                                     for worksite in worksites])
        if is_hospital_sponsored:
            for assignment in organization_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value
                )
            return

        # We do greater or equal to 27 here because there's so much variability in what was considered "all year"
        # during data entry throughout the years. For instance, some people put 48 weeks as "all year" to account for vacation
        weekly_assignments = {assignment for assignment in organization_assignments
                            if WeirdFteTable.convert_assignment_hours(assignment).weeks >= 27}
        weekly_worksites = {assignment.worksite for assignment in weekly_assignments}
        non_weekly_assignments = {assignment for assignment in organization_assignments if assignment not in weekly_assignments}

        # Member, partnership, etc (non-multi site dental group)
        if len(weekly_worksites) == 1:
            # Primary location
            primary_practice_arrangement = _determine_organization_size_classification(
                organization_assignments=organization_assignments,
                simplify=config.getboolean('PracticeArrangement', 'simplify')
            )
            self._output_data(
                assignment=next(iter(weekly_assignments)),
                year=year,
                org_size=len(providers),
                ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                practice_arrangement=primary_practice_arrangement
            )

            # Satellites
            for assignment in non_weekly_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.SATELLITE.value
                )
        # Multi-site dental group
        else:
            for assignment in weekly_assignments:
                self._output_data(
                    assignment=next(iter(weekly_assignments)),
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value
                )

            for assignment in non_weekly_assignments:
                self._output_data(
                    assignment=next(iter(weekly_assignments)),
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.SATELLITE.value
                )
                

class PracticeArrangement(AnalysisClass):

    def __init__(self, simplify_practice_arrangements: bool = False):
        super().__init__()
        self.simplify = simplify_practice_arrangements

    def analyze_environment(self, years: list[int], env: Environment, simplify: bool = True) -> pd.DataFrame:
        formatter = Formatter()

        for year, organization in product(years, env.organizations):
            formatter.classify(
                organization=organization,
                year=year
            )

        df = pd.DataFrame(formatter.output)
        return df

    @property
    def required_columns(self):
        return RequiredEntitiesColumns(worksite_columns=[WorksiteEnums.Attributes.PRAC_ARR_NAME,
                                                         OutputDataColumns.WORKSITE_ID],
                                       provider_columns=[ProviderEnums.Attributes.AGE],
                                       provider_at_worksite_columns=[ProviderEnums.AssignmentAttributes.FTE,
                                                                     ProviderEnums.AssignmentAttributes.WK_WEEKS,
                                                                     ProviderEnums.AssignmentAttributes.WK_HOURS,
                                                                     ProviderEnums.AssignmentAttributes.SPECIALTY_NAME]
                                       )

