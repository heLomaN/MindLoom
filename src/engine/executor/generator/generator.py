# src/engine/executor/generator/generator.py

from config import root_path
from engine.executor.executor import Executor

class Generator(Executor):
    def __init__(self, id, secret):
        super().__init__(id, secret)

    def run(self, inputs):
        """ 执行流程 """
        return {}