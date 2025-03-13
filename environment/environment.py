
from dataclasses import dataclass


@dataclass
class Environment:
    providers_by_id: dict
    worksites_by_id: dict
    organizations_by_id: dict

    @property
    def organizations(self) -> list:
        return list(self.organizations_by_id.values())
