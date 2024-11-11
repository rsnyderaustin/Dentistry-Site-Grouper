import pandas as pd

from analysis.analysis_funcs import AnalysisFunctions
from program_management import program_manager

prog_manager = program_manager.ProgramManager(
    worksites_path="C:/Users/austisnyder/programming/programming_i_o_files/worksites_parents.csv",
    year_end_path="C:/Users/austisnyder/programming/programming_i_o_files/dds_all_years_data.csv"
)

hcpids_by_size = prog_manager.func(AnalysisFunctions.HCP_IDS_BY_ORG_SIZE)

output = {
    'year': [],
    'org_size': [],
    'practice_arr_name': [],
    'hcpids': []
}
all_org_sizes = {}
for year, org_size_data in hcpids_by_size.items():
    all_org_sizes.update(org_size_data.keys())
all_org_sizes = sorted(all_org_sizes)

for year, org_size_data in hcpids_by_size.items():
for org_size, ages in hcpids_by_size.items():
    output['org_size'].extend([org_size for _ in list(range(len(ages)))])
    output['hcpids'].extend(ages)
df = pd.DataFrame(output)
df.to_excel("C:/Users/austisnyder/programming/programming_i_o_files/hcp_ids_by_org_size.xlsx")


