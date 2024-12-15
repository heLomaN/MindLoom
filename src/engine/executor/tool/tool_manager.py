# src/engine/executor/tool/tool_manager.py

import importlib
import os
import inspect

class ToolManager:
    def __init__(self):
        """
        初始化工具管理器，加载所有工具并将其元数据存储到内存中。
        """
        self.tools = self._load_tools()
        print(self.tools)

    def _load_tools(self):
        """
        从 tools 目录加载所有工具，读取其元数据，并存储到内存。
        返回一个以 tool_id 为键的工具字典。
        """
        tools_directory = os.path.join(os.path.dirname(__file__), "tools")
        tools_metadata = {}

        # 遍历 tools 目录及其子目录，加载所有工具类
        for root, _, files in os.walk(tools_directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.relpath(os.path.join(root, file), tools_directory)
                    module_path = module_path.replace(os.sep, ".").replace(".py", "")

                    # 动态加载模块
                    try:
                        module = importlib.import_module(f".tools.{module_path}", package="engine.executor.tool")
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if hasattr(obj, "metadata") and callable(obj.metadata):
                                metadata = obj.metadata()
                                tool_id = metadata["id"]
                                tools_metadata[tool_id] = {
                                    "class": obj,
                                    "metadata": metadata
                                }
                    except Exception as e:
                        print(f"Error loading module {module_path}: {e}")

        return tools_metadata

    def load_tool(self, tool_id):
        """
        根据工具 ID 加载工具类的实例。
        """
        tool_info = self.tools.get(tool_id)
        if not tool_info:
            raise ValueError(f"Tool with ID '{tool_id}' not found.")
        return tool_info["class"]

    def get_metadata(self, tool_id):
        """
        根据工具 ID 获取工具的元数据。
        """
        tool_info = self.tools.get(tool_id)
        if not tool_info:
            raise ValueError(f"Tool with ID '{tool_id}' not found.")
        return tool_info["metadata"]

    def list_tools(self):
        """
        列出所有工具的 ID 和描述。
        返回一个包含元数据中 ID 和 description 的列表。
        """
        return [{"id": tool_id, "description": info["metadata"]["description"]}
                for tool_id, info in self.tools.items()]

    def export_metadata(self):
        """
        导出所有工具的元数据。
        返回一个包含所有元数据的列表。
        """
        return [info["metadata"] for info in self.tools.values()]