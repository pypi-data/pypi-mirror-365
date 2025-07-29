from fromless import MustBeQualified   # note the irony

class Qualified(MustBeQualified):
    def __init__(self):
        super().__init__()

