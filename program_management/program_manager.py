import logging
import pandas as pd
import time

from analysis import get_analysis_class
from column_enums import ProgramDataColumns, WorksiteDataColumns
from environment import EnvironmentManager

logging.basicConfig(level=logging.INFO)


def apply_filter_dataframe(row, rows: list, valid_worksite_ids_by_year: dict):
    year = row[ProgramDataColumns.YEAR.value]
    worksite_id = row[WorksiteDataColumns.WORKSITE_ID.value]

    if worksite_id in valid_worksite_ids_by_year[year]:
        rows.append(row)

def dataframe_contains_columns(df: pd.DataFrame, columns):
    return all([column in df.columns for column in columns])


class ProgramManager:

    def __init__(self, worksites_path: str, year_end_path: str):
        self.worksites_df = pd.read_csv(worksites_path)

        self.year_end_df = pd.read_csv(year_end_path)

        # Worksites are valid if they are originally included in the data, otherwise they are created as empty worksites
        # to allow the program to function
        self.valid_worksite_ids_by_year = self.year_end_df.groupby(ProgramDataColumns.YEAR.value)[
            WorksiteDataColumns.WORKSITE_ID.value].unique()

        self.worksites_df.columns = [col.lower().replace(' ', '') for col in self.worksites_df.columns]
        self.year_end_df.columns = [col.lower().replace(' ', '') for col in self.year_end_df.columns]

    def analyze(self, analysis_func_enum, **kwargs):
        environment_manager = EnvironmentManager(year_end_df=self.year_end_df,
                                                 worksites_df=self.worksites_df)

        func_class = get_analysis_class(analysis_func_enum)(**kwargs)
        environment_manager.fill_environments(required_cols=func_class.required_columns)
        func_class.process_data(environments=environment_manager.environments)
        df = func_class.get_dataframe()

        # If these columns are not included in the dataframe then we aren't doing analysis that requires filtering
        if dataframe_contains_columns(df=df, columns=[ProgramDataColumns.YEAR.value, WorksiteDataColumns.WORKSITE_ID.value]):
            df = df[df.apply(
                lambda row: row[ProgramDataColumns.YEAR.value] in self.valid_worksite_ids_by_year
                            and row[WorksiteDataColumns.WORKSITE_ID.value] in self.valid_worksite_ids_by_year[row[ProgramDataColumns.YEAR.value]],
                axis=1
            )]
        return df
