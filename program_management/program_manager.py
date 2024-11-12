import logging
import pandas as pd
import time

from analysis import analysis_funcs, AnalysisFunctions
from environment import EnvironmentManager

logging.basicConfig(level=logging.INFO)


class ProgramManager:

    def __init__(self, worksites_path: str, year_end_path: str):
        self.worksites_df = pd.read_csv(worksites_path)
        self.year_end_df = pd.read_csv(year_end_path)

        self.worksites_df.columns = [col.lower().replace(' ', '') for col in self.worksites_df.columns]
        self.year_end_df.columns = [col.lower().replace(' ', '') for col in self.year_end_df.columns]

    def func(self, analysis_func_enum):
        environment_manager = EnvironmentManager(year_end_df=self.year_end_df,
                                                 worksites_df=self.worksites_df)
        required_cols = analysis_funcs.get_required_columns(func_enum=analysis_func_enum)
        environment_manager.fill_environments(required_cols=required_cols)

        func_class =
        prov_assigns_by_size = {}
        for year, env in environment_manager.environments.items():
            b_time = time.time()
            prov_assigns_by_size[year] = analysis_funcs.process_analysis_function(
                func_enum=AnalysisFunctions.PROV_ASSIGNS_BY_ORG_SIZE,
                environment=env
            )
            logging.info(f"Time to process func {AnalysisFunctions.PROV_ASSIGNS_BY_ORG_SIZE} for year {year}: {time.time() - b_time}")

        format_class =


