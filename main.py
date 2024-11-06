from entities import RequiredEntitiesColumns
from program_management import ProgramManager

import pandas as pd

required_cols = RequiredEntitiesColumns(
    worksite_columns=[],
    provider_columns=[]
)

worksites_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv")
yearend_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/dds_2023_data.csv")
prog_manager = ProgramManager(worksites_df=worksites_df,
                              yearend_df=yearend_df,
                              required_entities_cols=required_cols)
prog_manager.create_organizations()
x=0


