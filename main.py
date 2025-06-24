
import logging

import pandas as pd

from analysis import PracticeArrangement
from program_management import program_manager

logging.basicConfig(level=logging.INFO)

worksites_path = "C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv"
worksites_df = pd.read_csv(worksites_path)

year_end_path = "C:/Users/austisnyder/programming/programming_i_o_files/old_dds_ye.csv"
year_end_df = pd.read_csv(year_end_path)
year_end_df = year_end_df[year_end_df['activity'] == 'Private Practice']
year_end_df = year_end_df[year_end_df['year'] == 2023]

prog_manager = program_manager.ProgramManager(
    worksites_df=worksites_df,
    year_end_df=year_end_df
)

df = prog_manager.analyze(analysis_class=PracticeArrangement())

df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/practice_arrangements.csv",
          index=False)


