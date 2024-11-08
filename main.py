import pandas as pd

from analysis import Analyzer
from environment import EnvironmentManager


worksites_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv")
yearend_df = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/dds_all_years_data.csv")
worksites_df.columns = [col.lower().replace(' ', '') for col in worksites_df.columns]
yearend_df.columns = [col.lower().replace(' ', '') for col in yearend_df.columns]

environment_manager = EnvironmentManager(yearend_df=yearend_df,
                                         worksites_df=worksites_df)
analyzer = Analyzer(environment=environment_manager.environment)
hcp_request = analyzer.get_dentist_id_by_organization_size()

environment_manager.fill_environment(required_cols=hcp_request.required_cols)

hcpids_by_size = analyzer(hcp_request)

output = {
    'year': [],
    'org_size': [],
    'practice_arr_name': [],
    'hcpids': []
}
for org_size, ages in hcpids_by_size.items():
    output['org_size'].extend([org_size for _ in list(range(len(ages)))])
    output['hcpids'].extend(ages)
df = pd.DataFrame(output)
df.to_excel("C:/Users/austisnyder/programming/programming_i_o_files/hcp_ids_by_org_size.xlsx")


