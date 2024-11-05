import pandas as pd

from worksite_data_enums import WorksiteDataColumns


def _apply_create_relations(row, worksite_to_parent: dict, parent_to_children: dict):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]
    if worksite_id not in worksite_to_parent:
        worksite_to_parent[worksite_id] = parent_id

    if parent_id not in parent_to_children:
        parent_to_children[parent_id] = set()
    parent_to_children[parent_id].add(worksite_id)


class WorksiteParentRelations:

    def __init__(self, worksites_df: pd.DataFrame):
        self.worksite_to_parent = {}
        self.parent_to_children = {}
        worksites_df.apply(_apply_create_relations,
                           worksite_to_parent=self.worksite_to_parent,
                           parent_to_worksite=self.parent_to_children)

    def get_worksite_ids(self, parent_id: int):
        return self.parent_to_children[parent_id]

    def get_parent_id(self, worksite_id: int):
        return self.worksite_to_parent[worksite_id]




