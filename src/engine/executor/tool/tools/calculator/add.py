# src/engine/executor/tool/calculator/add.py

class add:
    @staticmethod
    def metadata():
        return {
            "id": "calculator.add",
            "description": "执行加法运算",
            "input": [
                {"name": "addend", "type": "int", "description": "第一个加数"},
                {"name": "augend", "type": "int", "description": "第二个加数"}
            ],
            "output": [
                {"name": "sum", "type": "int", "description": "加法结果"}
            ]
        }

    @staticmethod
    def run(inputs):
        addend = inputs["addend"]
        augend = inputs["augend"]
        return {"sum": addend + augend}