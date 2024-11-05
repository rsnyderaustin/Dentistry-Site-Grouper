import pandas as pd

from worksite_data_enums import WorksiteDataColumns


def _apply_create_relations(row, relations: dict):
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]
    parent_id = row[WorksiteDataColumns.PARENT_ID.value]
    if worksite_id not in relations:
        relations[worksite_id] = parent_id


class WorksiteParentRelations:

    def __init__(self, worksites_df: pd.DataFrame):
        self.ws_to_p = {}
        worksites_df.apply(_apply_create_relations, relations=self.ws_to_p)
        self.p_to_ws = {p_id: ws_id for ws_id, p_id in self.ws_to_p.items()}

    def get_worksite_id(self, parent_id: int):
        return self.p_to_ws[parent_id]

    def get_parent_id(self, worksite_id: int):
        return self.ws_to_p[worksite_id]




