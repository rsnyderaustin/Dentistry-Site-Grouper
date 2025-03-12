
import logging

from analysis import PracticeArrangement
from program_management import program_manager

logging.basicConfig(level=logging.INFO)

prog_manager = program_manager.ProgramManager(
    worksites_path="C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv",
    year_end_path="C:/Users/austisnyder/programming/programming_i_o_files/dds_years_data.csv"
)

df = prog_manager.analyze(analysis_class=PracticeArrangement(),
                          simplify_practice_arrangements=False)

df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/practice_arrangements.csv",
          index=False)


