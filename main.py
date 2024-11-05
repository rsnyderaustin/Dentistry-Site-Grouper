from entities import RequiredEntitiesColumns
from program_management import ProgramManager

import pandas as pd

required_cols = RequiredEntitiesColumns(
    worksite_columns=[''],
    provider_columns=['']
)
prog_manager = ProgramManager(worksites_df=worksites_df,
                              yearend_df=yearend_df,
                              required_entities_cols=required_cols)
