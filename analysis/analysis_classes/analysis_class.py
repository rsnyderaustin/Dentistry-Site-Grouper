
from abc import ABC, abstractmethod


class AnalysisClass(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def get_dataframe(self):
        pass

    @abstractmethod
    @property
    def required_columns(self):
        pass
