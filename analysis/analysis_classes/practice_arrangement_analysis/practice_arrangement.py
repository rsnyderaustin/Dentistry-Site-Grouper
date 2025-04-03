
import configparser
from dataclasses import dataclass
from itertools import product
import logging
import pandas as pd

from .classify_provider_fte import ProviderFteClassifier
from environment import Environment
from analysis.analysis_classes.analysis_base_class import AnalysisClass
from things import Organization, ProviderAssignment, Worksite
from utils import config, OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums

import logging


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
            ProviderEnums.AssignmentAttributes.ACTIVITY.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: [],
            ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value: []
        }

    def _output_data(self, assignment: ProviderAssignment, year: int, org_size: int, ultimate_parent_id: int,
                     practice_arrangement, worksite_type: str):
        self.output[ProgramColumns.YEAR.value].append(year)
        self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
        self.output[ProviderEnums.Attributes.HCP_ID.value].append(getattr(assignment.provider, ProviderEnums.Attributes.HCP_ID.value))
        self.output[ProviderEnums.Attributes.AGE.value].append(getattr(assignment.provider, ProviderEnums.Attributes.AGE.value))
        self.output[OutputDataColumns.WORKSITE_ID.value].append(getattr(assignment.worksite, WorksiteEnums.Attributes.WORKSITE_ID.value))
        self.output[OutputDataColumns.CLASSIFICATION.value].append(practice_arrangement),
        self.output[ProviderEnums.AssignmentAttributes.ACTIVITY.value].append(getattr(assignment, ProviderEnums.AssignmentAttributes.ACTIVITY.value)),
        self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(ultimate_parent_id),
        self.output[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value].append(worksite_type)

    def classify(self, organization: Organization, year: int):
        organization_assignments = organization.fetch_provider_assignments(year=year)
        worksites = {assignment.worksite for assignment in organization_assignments}
        if any([worksite.worksite_id == 161699 for worksite in worksites]):
            x=0
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
                    practice_arrangement=WorksiteEnums.PracticeArrangements.CORPORATE.value,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
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
                    practice_arrangement=WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
                )
            return

        # We do greater or equal to 27 here because there's so much variability in what was considered "all year"
        # during data entry throughout the years. For instance, some people put 48 weeks as "all year" to account for vacation
        weekly_assignments = {assignment for assignment in organization_assignments
                              if ProviderFteClassifier.provider_is_weekly(assignment)}
        weekly_worksites = {assignment.worksite for assignment in weekly_assignments}
        non_weekly_assignments = {assignment for assignment in organization_assignments if assignment not in weekly_assignments}

        # Member, partnership, etc (non-multi site dental group)
        if len(weekly_worksites) == 1:
            # Primary location
            primary_practice_arrangement = _determine_organization_size_classification(
                organization_assignments=organization_assignments,
                simplify=config.getboolean('PracticeArrangement', 'simplify')
            )
            for assignment in weekly_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=primary_practice_arrangement,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
                )

            # Satellites
            for assignment in non_weekly_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.SATELLITE.value,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
                )

            return
        # Multi-site dental group
        else:
            for assignment in weekly_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
                )

            for assignment in non_weekly_assignments:
                self._output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.SATELLITE.value,
                    worksite_type=assignment.assignment_data[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value]
                )

            return

        raise RuntimeError(f"No classification done for organization with worksites {worksites}")


class PracticeArrangement(AnalysisClass):

    def __init__(self):
        super().__init__()

    def analyze_environment(self, years: list[int], env: Environment, simplify: bool = True) -> pd.DataFrame:
        formatter = Formatter()

        for year, organization in product(years, env.organizations):
            formatter.classify(
                organization=organization,
                year=year
            )

        logging.info(f"There are {len(set(formatter.output[ProviderEnums.Attributes.HCP_ID.value]))} distinct provider ID's in the output data.")
        logging.info(f"There are {len(set(formatter.output[WorksiteEnums.Attributes.WORKSITE_ID.value]))} distinct worksite ID's in the output data.")
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
                                                                     ProviderEnums.AssignmentAttributes.SPECIALTY_NAME,
                                                                     ProviderEnums.AssignmentAttributes.WORKSITE_TYPE]
                                       )

