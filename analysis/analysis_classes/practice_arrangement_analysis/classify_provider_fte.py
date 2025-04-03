from dataclasses import dataclass
from typing import Iterable

from things import ProviderAssignment
from utils import ProviderEnums


@dataclass
class HoursWeeks:
    hours: int
    weeks: int
    converted: bool


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

        if hours in cls.table and weeks == cls.table[hours]:
            return HoursWeeks(hours=hours, weeks=52, converted=True)
        else:
            return HoursWeeks(hours=hours, weeks=weeks, converted=False)


class ProviderFteClassifier:
    # There's been a lot of variation in what "weekly" weeks means, as some workers in the past have accounted for
    # things like vacation weeks. So we just play it safe here and put the weeks as 48
    full_time_hours = 8 * 48

    @classmethod
    def provider_is_weekly(cls, assignment: ProviderAssignment):
        hrs_wks = WeirdFteTable.convert_assignment_hours(assignment)
        if hrs_wks.hours * hrs_wks.weeks >= cls.full_time_hours:
            return True
        # If we don't know either hours or weeks then we can't really know if the provider is at the worksite one
        # day per week, so our best guess is their FTE
        elif hrs_wks.hours == 0 or hrs_wks.weeks == 0:
            is_weekly = True if getattr(assignment, ProviderEnums.AssignmentAttributes.FTE.value) == 'FT' else False
            return is_weekly
        else:
            return False
