from analysis_enums import AnalysisFunctions


def get_longest_list_length(output_data):
    top_length = -1
    for year, size_data in output_data:
        max_length = max(len(_) for _ in size_data.values())
        top_length = max(top_length, max_length)

    return top_length


def get_unique_org_sizes(output_data):
    all_org_sizes = {}
    for year, org_size_data in output_data.items():
        all_org_sizes.update(org_size_data.keys())
    all_org_sizes = sorted(all_org_sizes)
    return all_org_sizes

class HcpIdOrgSizeFormatter:

    def __init__(self):
        self.output = {
            'year': [],
            'org_size': [],
            'practice_arr_name': [],
            'hcpids': []
        }

    def format(self, output_data):
        longest_list_length = get_longest_list_length(output_data)
        org_sizes = get_unique_org_sizes(output_data)
        self.fill_data_with_blanks(output_data=output_data,
                                   unique_org_sizes=org_sizes,
                                   max_list_length=longest_list_length)

        for year, org_size_data in output_data.items():
            self.output['year'] = [year for _ in longest_list_length]
            # Have to figure out how to get practice arr name here

    def fill_data_with_blanks(self, output_data, unique_org_sizes, max_list_length):
        for year, org_size_data in output_data.items():
            org_sizes_to_add = {size for size in unique_org_sizes if size not in org_size_data.keys()}
            for size in org_sizes_to_add:
                org_size_data[size] = [None for _ in list(range(max_list_length))]
            for size, hcp_ids in org_size_data.items():
                spaces_to_fill = list(range(max_list_length - len(hcp_ids)))
                hcp_ids.append([None for _ in spaces_to_fill])

class OutputFormatter:

    def __init__(self):
        self.formatters = {
            AnalysisFunctions.HCP_IDS_BY_ORG_SIZE:
        }