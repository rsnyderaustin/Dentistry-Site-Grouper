from entities.objects.worksite import Worksite
from worksite_factory import create_worksites


def _create_uncreated_worksites(worksites: dict):
    parent_ids = set(ws.parent_id for ws in worksites)
    uncreated_parent_ids = set(parent_id for parent_id in parent_ids if parent_id not in worksites.keys())
    for parent_id in uncreated_parent_ids:
        worksites[parent_id] = Worksite()

def create_organizations(yearend_df, worksites_df):

    worksites = create_worksites(worksites_df)
    parent_ids = set(ws.parent_id for ws in worksites)

    non_worksite_parents = set()
    for parent_id in parent_ids:
        if parent_id not in worksites.keys():
            non_worksite_parents.add(parent_id)

