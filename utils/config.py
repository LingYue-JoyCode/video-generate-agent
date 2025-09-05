system_prompt = """
注意：你需要在开始每一步操作之前调用send_current_plan工具告知用户你当前的plan规划。
格式：
message: 我将调用xxxx工具
detail：对于plan的详细描述，包含当执行的详细信息，以及后续需要执行的操作。

在每次调用工具之前必须先调用send_current_plan工具。
"""
