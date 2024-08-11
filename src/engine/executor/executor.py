# src/engine/executor/executor.py

from config import root_path
from engine.base.base import Base

class Executor(Base):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self, inputs):
        return {}
        