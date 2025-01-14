# src/engine/executor/tool/tools/calculator/add.py

class Add:
    @staticmethod
    def metadata():
        return {
            "id": "calculator.add",
            "name": "calculator_add",
            "description": "执行加法运算",
            "inputs": [
                {"name": "addend", "type": "number", "description": "第一个加数"},
                {"name": "augend", "type": "number", "description": "第二个加数"}
            ],
            "outputs": [
                {"name": "sum", "type": "number", "description": "加法结果"}
            ]
        }

    @staticmethod
    def run(inputs):
        addend = inputs["addend"]
        augend = inputs["augend"]
        return {"sum": addend + augend}