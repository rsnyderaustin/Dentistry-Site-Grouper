
from abc import ABC, abstractmethod
import pandas as pd


class AnalysisClass(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def process_data(self, environments):
        pass

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def required_columns(self):
        pass
