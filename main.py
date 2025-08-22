
import pandas as pd

from analysis import PracticeArrangement
from program_management import program_manager

worksites_path = "C:/Users/austisnyder/programming/programming_i_o_files/dds_grouping_worksites_data.csv"
worksites_df = pd.read_csv(worksites_path)
worksites_df = worksites_df.fillna('')
worksites_df.columns = [col.lower() for col in worksites_df.columns]

year_end_path = "C:/Users/austisnyder/programming/programming_i_o_files/dds_grouping_data.csv"
year_end_df = pd.read_csv(year_end_path)
year_end_df = year_end_df.fillna('')
year_end_df.columns = [col.lower() for col in year_end_df.columns]

prog_manager = program_manager.ProgramManager(
    worksites_df=worksites_df,
    year_end_df=year_end_df
)

df = prog_manager.analyze(analysis_class=PracticeArrangement())

df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/corrected_prac_arrangements.csv",
          index=False)


