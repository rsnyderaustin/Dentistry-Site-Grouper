
from abc import ABC, abstractmethod
import pandas as pd


class Data:

    def __init__(self):
        self._data = {}

    @property
    def organizations_by_year(self):
        return self._data

    def add_organization(self, year, organization):
        if year not in self._data:
            self._data[year] = set()

        self._data[year].add(organization)

    def data_generator(self):
        for year, org_set in self._data.items():
            for org in org_set:
                org_size = len(org.providers_by_id)
                for provider_assignment in org.provider_assignments:
                    yield year, org.ult_parent_worksite.worksite_id, org_size, provider_assignment


class AnalysisClass(ABC):

    def __init__(self):
        self.data = Data()
        pass

    def process_data(self, environments):
        for environment in environments:
            for organization in environment.organizations.values():
                self.data.add_organization(
                    year=environment.year,
                    organization=organization)

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def required_columns(self):
        pass
