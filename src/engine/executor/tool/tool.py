# src/engine/executor/tool/tool.py

from config import root_path
from engine.executor.executor import Executor
from engine.executor.tool.tool_manager import tool_manager as tm

class Tool(Executor):
    def __init__(self, id, secret):
        super().__init__(id, secret)
    
    # 执行流程
    def _execute(self, inputs):
        tool_class = tm.load_tool(self.id)
        instant = tool_class()
        outputs = instant.run(inputs)
        return outputs