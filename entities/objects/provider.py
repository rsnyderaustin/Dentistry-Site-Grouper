

class Hcp:

    def __init__(self, hcp_id: int, **params):
        self.hcp_id = hcp_id

        for k, v in params.items():
            setattr(self, k, v)




