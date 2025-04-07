
import configparser
from dataclasses import dataclass
from itertools import product
import logging
from typing import Iterable

import pandas as pd

from .classify_provider_fte import ProviderFteClassifier, IsWeekly
from environment import Environment
from analysis.analysis_classes.analysis_base_class import AnalysisClass
from things import Organization, ProviderAssignment, Worksite
from utils import config, OutputDataColumns, ProgramColumns, ProviderEnums, RequiredEntitiesColumns, WorksiteEnums

import logging


def _determine_worksite_status(year: int, worksite: Worksite):
    total_hours = 0
    provider_assignments = worksite.fetch_provider_assignments(year=year)
    for assignment in provider_assignments:
        total_hours += (assignment[ProviderEnums.AssignmentAttributes.WK_HOURS.value]
                        *
                        assignment[ProviderEnums.AssignmentAttributes.WK_WEEKS.value])


def _determine_organization_size_classification(worksites: Iterable[Worksite], year: int, simplify: bool = False):
    assignments = {assignment for worksite in worksites for assignment in worksite.fetch_provider_assignments(year=year)}
    organization_specialties = {
        getattr(assignment, ProviderEnums.AssignmentAttributes.SPECIALTY_NAME.value)
        for assignment in assignments
    }
    number_of_providers = len(set(assignment.provider for assignment in assignments))
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
        if len(assignments) >= 7:
            return f'7+ Member Group / {specialties_class}'

    return practice_arrangements_by_org_size[len(assignments)]


class Formatter:

    def __init__(self):
        self.output = {
            ProgramColumns.YEAR.value: [],
            OutputDataColumns.ORG_SIZE.value: [],
            OutputDataColumns.WORKSITE_SIZE.value: [],
            ProviderEnums.Attributes.HCP_ID.value: [],
            ProviderEnums.Attributes.AGE.value: [],
            OutputDataColumns.WORKSITE_ID.value: [],
            OutputDataColumns.CLASSIFICATION.value: [],
            OutputDataColumns.CLASSIFICATION_COMPLEX.value: [],
            ProviderEnums.AssignmentAttributes.ACTIVITY.value: [],
            WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value: [],
            ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value: [],
            OutputDataColumns.NUMBER_OF_WORKSITE_SPECIALTIES.value: []
        }

    def output_data(self, assignment: ProviderAssignment, year: int, org_size: int, ultimate_parent_id: int,
                    practice_arrangement, practice_arrangement_complex, worksite_type: str, number_of_specialties: int):
        self.output[ProgramColumns.YEAR.value].append(year)
        self.output[OutputDataColumns.ORG_SIZE.value].append(org_size)
        self.output[ProviderEnums.Attributes.HCP_ID.value].append(getattr(assignment.provider, ProviderEnums.Attributes.HCP_ID.value))
        self.output[ProviderEnums.Attributes.AGE.value].append(getattr(assignment.provider, ProviderEnums.Attributes.AGE.value))
        self.output[OutputDataColumns.WORKSITE_ID.value].append(getattr(assignment.worksite, WorksiteEnums.Attributes.WORKSITE_ID.value))
        self.output[OutputDataColumns.CLASSIFICATION.value].append(practice_arrangement),
        self.output[OutputDataColumns.CLASSIFICATION_COMPLEX.value].append(practice_arrangement_complex),
        self.output[ProviderEnums.AssignmentAttributes.ACTIVITY.value].append(getattr(assignment, ProviderEnums.AssignmentAttributes.ACTIVITY.value)),
        self.output[WorksiteEnums.Attributes.ULTIMATE_PARENT_ID.value].append(ultimate_parent_id),
        self.output[ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value].append(worksite_type),
        self.output[OutputDataColumns.NUMBER_OF_WORKSITE_SPECIALTIES.value].append(number_of_specialties)


class PracticeArrangement(AnalysisClass):

    def __init__(self):
        super().__init__()

        self.formatter = Formatter()

    def analyze_environment(self, years: list[int], env: Environment, simplify: bool = True) -> pd.DataFrame:
        for year, organization in product(years, env.organizations):
            self.classify(
                organization=organization,
                year=year
            )

        logging.info(f"There are {len(set(self.formatter.output[ProviderEnums.Attributes.HCP_ID.value]))} distinct provider ID's in the output data.")
        logging.info(f"There are {len(set(self.formatter.output[WorksiteEnums.Attributes.WORKSITE_ID.value]))} distinct worksite ID's in the output data.")
        df = pd.DataFrame(self.formatter.output)
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

    def _output_primary_and_satellites(self, primary_worksite: Worksite, year: int, ultimate_parent_id: int, satellites: Iterable[Worksite] = None):
        if not satellites:
            satellites = list()

        primary_practice_arrangement = _determine_organization_size_classification(
            worksites=[primary_worksite, *satellites],
            year=year,
            simplify=config.getboolean('PracticeArrangement', 'simplify')
        )
        primary_practice_arrangement_complex = _determine_organization_size_classification(
            worksites=[primary_worksite, *satellites],
            year=year,
            simplify=False
        )
        primary_assignments = primary_worksite.fetch_provider_assignments(year=year)
        satellite_assignments = {assignment for satellite in satellites for assignment in satellite.fetch_provider_assignments(year=year)}

        providers = {provider for provider in [*primary_assignments, *satellite_assignments]}

        for assignment in primary_assignments:
            self.formatter.output_data(
                assignment=assignment,
                year=year,
                org_size=len(providers),
                ultimate_parent_id=ultimate_parent_id,
                practice_arrangement=primary_practice_arrangement,
                practice_arrangement_complex=primary_practice_arrangement_complex,
                worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
            )

        for assignment in satellite_assignments:
            self.formatter.output_data(
                assignment=assignment,
                year=year,
                org_size=len(providers),
                ultimate_parent_id=ultimate_parent_id,
                practice_arrangement=WorksiteEnums.PracticeArrangements.SATELLITE.value,
                practice_arrangement_complex=WorksiteEnums.PracticeArrangements.SATELLITE.value,
                worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
            )

    @classmethod
    def _determine_worksite_weekly_statuses(cls, worksites: Iterable[Worksite], year: int) -> dict:
        is_weeklys_by_worksite = {
            worksite: []
            for worksite in worksites if worksite.fetch_provider_assignments(year=year)
        }

        assignments = {assignment for worksite in worksites for assignment in worksite.fetch_provider_assignments(year=year)}
        for assignment in assignments:
            is_weekly = ProviderFteClassifier.provider_is_weekly(assignment)
            assignment.is_weekly = is_weekly

            is_weeklys_by_worksite[assignment.worksite].append(assignment.is_weekly)

        worksites_statuses = {
            IsWeekly.TRUE: set(),
            IsWeekly.UNKNOWN: set(),
            IsWeekly.FALSE: set()
        }
        for worksite, classifications in is_weeklys_by_worksite.items():
            if any([classification == IsWeekly.TRUE for classification in classifications]):
                worksites_statuses[IsWeekly.TRUE].add(worksite)
            elif any([classification == IsWeekly.UNKNOWN for classification in classifications]):
                worksites_statuses[IsWeekly.UNKNOWN].add(worksite)
            else:
                worksites_statuses[IsWeekly.FALSE].add(worksite)

        return worksites_statuses

    def classify(self, organization: Organization, year: int):
        year_assignments = organization.fetch_provider_assignments(year=year)
        if not year_assignments:
            return

        year_worksites = {worksite for worksite in organization.worksites if worksite.fetch_provider_assignments(year=year)}
        year_providers = {assignment.provider for assignment in year_assignments}

        # CORPORATE
        is_corporate = any([getattr(assignment.worksite,
                                    WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.CORPORATE.value
                            for assignment in year_assignments])

        if is_corporate:
            for assignment in year_assignments:
                self.formatter.output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(year_providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.CORPORATE.value,
                    practice_arrangement_complex=WorksiteEnums.PracticeArrangements.CORPORATE.value,
                    worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                    number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
                )
            return

        # HOSPITAL SPONSORED
        hospital_sponsored_worksites = [
            worksite for worksite in organization.worksites
            if getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value
        ]
        if hospital_sponsored_worksites:
            non_hospital_sponsored_worksites = [worksite for worksite in year_worksites if worksite not in hospital_sponsored_worksites]
            if non_hospital_sponsored_worksites:
                raise RuntimeError(f"Oragnization with Ultimate Parent ID {organization.ultimate_parent_worksite_id} has a mix of "
                                   f"hospital sponsored and non-hospital sponsored worksites.")

            hospital_sponsored_assignments = {
                assignment for worksite in hospital_sponsored_worksites for assignment in worksite.fetch_provider_assignments(year=year)
            }
            for assignment in hospital_sponsored_assignments:
                self.formatter.output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(year_providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value,
                    practice_arrangement_complex=WorksiteEnums.PracticeArrangements.HOSPITAL_SPONSORED_PRACTICE.value,
                    worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                    number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
                )
            return

        # If there is only one worksite in the whole organization, then it's obviously just a solo practice
        if len(year_worksites) == 1:
            self._output_primary_and_satellites(
                primary_worksite=next(iter(year_worksites)),
                year=year,
                ultimate_parent_id=organization.ultimate_parent_worksite_id
            )
            return

        # If there is only one provider, then the organization is necessarily a solo practice with satellites
        if len(year_providers) == 1:
            if organization.ultimate_parent_worksite not in year_worksites:
                raise RuntimeError(f"Organization with Ultimate Parent ID {organization.ultimate_parent_worksite_id} has only one provider, but the"
                                   f"Ultimate Parent Worksite has no provider in year {year}. May not necessarily be a huge error - but need to deal with this.")
            satellites = {worksite for worksite in year_worksites if worksite != organization.ultimate_parent_worksite}
            self._output_primary_and_satellites(
                primary_worksite=organization.ultimate_parent_worksite,
                satellites=satellites,
                year=year,
                ultimate_parent_id=organization.ultimate_parent_worksite_id
            )
            return

        worksites_statuses = self._determine_worksite_weekly_statuses(worksites=year_worksites, year=year)

        # If there are at least 2 worksites with weekly employees, then the organization is a multi-site dental group
        if len(worksites_statuses[IsWeekly.TRUE]) >= 2:
            for assignment in year_assignments:
                self.formatter.output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(year_providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value,
                    practice_arrangement_complex=WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value,
                    worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                    number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
                )
            return
        elif len(worksites_statuses[IsWeekly.TRUE]) == 1 and len(worksites_statuses[IsWeekly.UNKNOWN]) == 0:
            primary_worksite = next(iter(worksites_statuses[IsWeekly.TRUE]))
            satellites = {worksite for worksite in year_worksites if worksite != primary_worksite}
            self._output_primary_and_satellites(
                primary_worksite=primary_worksite,
                satellites=satellites,
                year=year,
                ultimate_parent_id=organization.ultimate_parent_worksite_id
            )
            return

        # If there are multiple weeklys or unknown weeklys, but one of the worksites is labeled as a multi-site dental group then we can be fairly confident
        # that the organization is a multi-site dental group
        practice_arrangements = [getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) for worksite in year_worksites]
        if (len([*worksites_statuses[IsWeekly.TRUE], *worksites_statuses[IsWeekly.UNKNOWN]]) >= 2 and
                WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value in practice_arrangements):
            for assignment in year_assignments:
                self.formatter.output_data(
                    assignment=assignment,
                    year=year,
                    org_size=len(year_providers),
                    ultimate_parent_id=organization.ultimate_parent_worksite.worksite_id,
                    practice_arrangement=WorksiteEnums.PracticeArrangements.MULTISITE_DENTAL_GROUP.value,
                    worksite_type=getattr(assignment, ProviderEnums.AssignmentAttributes.WORKSITE_TYPE.value),
                    number_of_specialties=assignment.worksite.fetch_number_of_provider_specialties(year=year)
                )
            return

        # Now, we try to see if the Ultimate Parent Worksite is a viable primary worksite
        if organization.ultimate_parent_worksite in [*worksites_statuses[IsWeekly.TRUE], *worksites_statuses[IsWeekly.UNKNOWN]]:
            satellites = {worksite for worksite in year_worksites if worksite != organization.ultimate_parent_worksite}
            self._output_primary_and_satellites(primary_worksite=organization.ultimate_parent_worksite,
                                                satellites=satellites,
                                                year=year,
                                                ultimate_parent_id=organization.ultimate_parent_worksite_id)
            return

        # Now, we throw a bit of a hail mary here and see if there is a worksite that is not a satellite when the rest are
        satellite_worksites = {
            worksite for worksite in organization.worksites
            if getattr(worksite, WorksiteEnums.Attributes.PRAC_ARR_NAME.value) == WorksiteEnums.PracticeArrangements.SATELLITE.value
        }
        non_satellite_worksites = {worksite for worksite in organization.worksites if worksite not in satellite_worksites}

        # If all but one worksite are satellites, then we can pretty safely say that the non-satellite worksite
        # is the main site, and the rest are satellites. There could be issues here because changing a practice arrangement name changes it
        # forever in the database, so we can't be 100% sure of practice arrangement names throughout history, but we can make an
        # educated guess
        if len(non_satellite_worksites) == 1:
            self._output_primary_and_satellites(
                primary_worksite=next(iter(non_satellite_worksites)),
                satellites=satellite_worksites,
                year=year,
                ultimate_parent_id=organization.ultimate_parent_worksite_id
            )
            return

        logging.info(f"Reached the end of confident analysis for organization with Ultimate Parent ID {organization.ultimate_parent_worksite_id} in year {year}.")
        if organization.ultimate_parent_worksite in year_worksites:
            satellites = {worksite for worksite in year_worksites if worksite != organization.ultimate_parent_worksite}
            self._output_primary_and_satellites(
                primary_worksite=organization.ultimate_parent_worksite,
                satellites=satellites,
                year=year,
                ultimate_parent_id=organization.ultimate_parent_worksite_id
            )
            return

        raise RuntimeError(f"No classification done for organization with worksites {set(worksite.worksite_id for worksite in year_worksites)} in year {year}.")

