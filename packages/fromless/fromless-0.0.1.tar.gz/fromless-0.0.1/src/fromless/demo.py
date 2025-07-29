from gtf import MustBeQualified
from dataclasses import dataclass

class Qualified(MustBeQualified):
    
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Qualified(name='{self.name}')" 