import pandas as pd

from analysis import Analyzer
from entities import RequiredEntitiesColumns
from environment import EnvironmentManager

required_cols = RequiredEntitiesColumns(
    worksite_columns=[],
    provider_columns=[]
)

worksites_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv")
yearend_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/dds_2023_data.csv")
worksites_df.columns = [col.lower().replace(' ', '') for col in worksites_df.columns]
yearend_df.columns = [col.lower().replace(' ', '') for col in yearend_df.columns]

environment_manager = EnvironmentManager(yearend_df=yearend_df,
                                         worksites_df=worksites_df,
                                         required_entities_cols=required_cols)
environment_manager.create_environment()
analyzer = Analyzer(organizations=environment_manager.organizations)
org_sizes = analyzer.get_organization_sizes()
x=0

