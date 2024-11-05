

class Worksite:

    def __init__(self, worksite_id: int, parent_id: int, **params):
        self.worksite_id = worksite_id
        self.parent_id = parent_id

        for k, v in params.items():
            setattr(self, k, v)

        self.hcps = set()
