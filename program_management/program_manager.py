import logging
import pandas as pd

from analysis import AnalysisClass
from utils.enums import ProgramColumns, WorksiteEnums
from environment import EnvironmentManager

logging.basicConfig(level=logging.INFO)


def apply_filter_dataframe(row, rows: list, valid_worksite_ids_by_year: dict):
    year = row[ProgramColumns.YEAR.value]
    worksite_id = row[WorksiteEnums.Attributes.WORKSITE_ID.value]

    if worksite_id in valid_worksite_ids_by_year[year]:
        rows.append(row)


def dataframe_contains_columns(df: pd.DataFrame, columns):
    return all([column in df.columns for column in columns])


class ProgramManager:

    def __init__(self, worksites_path: str, year_end_path: str):
        worksites_df = pd.read_csv(worksites_path)
        worksites_df.columns = [col.lower().replace(' ', '') for col in worksites_df.columns]

        year_end_df = pd.read_csv(year_end_path)
        year_end_df.columns = [col.lower().replace(' ', '') for col in year_end_df.columns]

        self.environment_manager = EnvironmentManager(year_end_df=year_end_df,
                                                      worksites_df=worksites_df)

        # Worksites are valid if they are originally included in the data, otherwise they are created as empty worksites
        # to allow the program to function
        self.valid_worksite_ids_by_year = year_end_df.groupby(ProgramColumns.YEAR.value)[
            WorksiteEnums.Attributes.WORKSITE_ID.value].unique()

    def analyze(self, analysis_class: AnalysisClass, **kwargs):
        self.environment_manager.fill_environments(required_cols=analysis_class.required_columns)
        analysis_class.process_data(environments=self.environment_manager.environments)
        df = analysis_class.get_dataframe()

        # If these columns are not included in the dataframe then we aren't doing analysis that requires filtering
        if dataframe_contains_columns(df=df, columns=[ProgramColumns.YEAR.value, WorksiteEnums.Attributes.WORKSITE_ID.value]):
            df = df[df.apply(
                lambda row: row[ProgramColumns.YEAR.value] in self.valid_worksite_ids_by_year
                            and row[WorksiteEnums.Attributes.WORKSITE_ID.value] in self.valid_worksite_ids_by_year[row[ProgramColumns.YEAR.value]],
                axis=1
            )]
        return df
