import logging
import pandas as pd
import time

from analysis import get_analysis_class
from environment import EnvironmentManager

logging.basicConfig(level=logging.INFO)


class ProgramManager:

    def __init__(self, worksites_path: str, year_end_path: str):
        self.worksites_df = pd.read_csv(worksites_path)
        self.year_end_df = pd.read_csv(year_end_path)

        self.worksites_df.columns = [col.lower().replace(' ', '') for col in self.worksites_df.columns]
        self.year_end_df.columns = [col.lower().replace(' ', '') for col in self.year_end_df.columns]

    def analyze(self, analysis_func_enum):
        environment_manager = EnvironmentManager(year_end_df=self.year_end_df,
                                                 worksites_df=self.worksites_df)

        func_class = get_analysis_class(analysis_func_enum)()
        environment_manager.fill_environments(required_cols=func_class.required_columns)
        func_class.process_data(environments=environment_manager.environments)
        df = func_class.get_dataframe()
        return df


