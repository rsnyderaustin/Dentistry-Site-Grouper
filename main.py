import pandas as pd

from analysis.analysis_enums import AnalysisFunctions
from program_management import program_manager

prog_manager = program_manager.ProgramManager(
    worksites_path="C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv",
    year_end_path="C:/Users/austisnyder/programming/programming_i_o_files/dds_all_years_data.csv"
)

df = prog_manager.analyze(AnalysisFunctions.AGE_BY_ORG_SIZE)

df.to_excel("C:/Users/austisnyder/programming/programming_i_o_files/ages_by_org_size.xlsx")


