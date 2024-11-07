
from column_enums import WorksiteDataColumns
from entities.objects.worksite import Worksite


def apply_create_worksite(row, worksites, extra_params: list = None):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]

    if worksite_id not in worksites:
        worksites[worksite_id] = Worksite(worksite_id=worksite_id, parent_id=parent_id)

    extra_data = {param: row[param] for param in extra_params} if extra_params else {}
    worksites[worksite_id].add_data(extra_data)
