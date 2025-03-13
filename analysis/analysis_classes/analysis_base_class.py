
from abc import ABC, abstractmethod
import pandas as pd

from environment import Environment


class AnalysisClass(ABC):

    def __init__(self):
        pass

    def analyze_environment(self, years: list[int], env: Environment):
        pass

    @property
    @abstractmethod
    def required_columns(self):
        pass

    @required_columns.setter
    @abstractmethod
    def required_columns(self, value):
        pass
