import pandas as pd

from analysis.analysis_funcs import AnalysisFunctions
from program_management import program_manager

prog_manager = program_manager.ProgramManager(
    worksites_path="C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv",
    year_end_path="C:/Users/austisnyder/programming/programming_i_o_files/dds_all_years_data.csv"
)

prov_assigns_by_size = prog_manager.func(AnalysisFunctions.PROV_ASSIGNS_BY_ORG_SIZE)

df.to_excel("C:/Users/austisnyder/programming/programming_i_o_files/hcp_ids_by_org_size.xlsx")


