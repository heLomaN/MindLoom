# src/engine/executor/executor.py

from config import root_path
from engine.base.base import Base

class Executor(Base):
    def __init__(self, id, secret):
        super().__init__(id, secret)

############## 执行相关逻辑 ##############

    def _execute(self, inputs):
        return {}