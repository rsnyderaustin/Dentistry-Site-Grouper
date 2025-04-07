from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from things import ProviderAssignment
from utils import ProviderEnums


@dataclass
class HoursWeeks:
    hours: int
    weeks: int
    converted: bool


class IsWeekly(Enum):
    TRUE = True
    FALSE = False
    UNKNOWN = None


class WeirdFteTable:
    # We omit 20: 26 from this table because that is a valid entry
    wk_hours_to_wk_weeks_table = {
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
        28: 36,
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
    def assignment_in_table(cls, assignment: ProviderAssignment):
        hours = getattr(assignment, ProviderEnums.AssignmentAttributes.WK_HOURS.value)
        weeks = getattr(assignment, ProviderEnums.AssignmentAttributes.WK_WEEKS.value)

        if hours in cls.wk_hours_to_wk_weeks_table and weeks == cls.wk_hours_to_wk_weeks_table[hours]:
            return True


class ProviderFteClassifier:
    # There's been a lot of variation in what "weekly" weeks means, as some workers in the past have accounted for
    # things like vacation weeks. So we just play it safe here and put the number of weeks denoting "weekly" as 46
    weekly_wks = 46
    ft_wk_hours = 32
    full_time_hours = ft_wk_hours * weekly_wks

    @classmethod
    def provider_is_weekly(cls, assignment: ProviderAssignment) -> IsWeekly:
        hours = getattr(assignment, ProviderEnums.AssignmentAttributes.WK_HOURS.value)
        weeks = getattr(assignment, ProviderEnums.AssignmentAttributes.WK_WEEKS.value)

        # If the assignment wkhours and wkweeks falls within the weird, archaic FTE table then the wkweeks are based solely on the
        # wkhours. So we have no way of knowing the true number of weeks per year the provider worked in this assignment.
        if WeirdFteTable.assignment_in_table(assignment) or weeks == 0:
            return IsWeekly.UNKNOWN

        if weeks >= cls.weekly_wks:
            return IsWeekly.TRUE
        else:
            return IsWeekly.FALSE
