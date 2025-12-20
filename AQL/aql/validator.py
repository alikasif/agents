import re
from typing import List
class AQLValidationError(Exception):
    def __init__(self, message, line_no=None, code=None):
        super().__init__(message)
        self.line_no = line_no
        self.code = code
    def __str__(self):
        return f"{self.code or 'AQL_ERROR'}: {super().__str__()}"
def validate_ast(ast) -> List[AQLValidationError]:
    errors = []
    agents = set(ast.agents.keys())
    if not ast.workflows:
        errors.append(AQLValidationError('No WORKFLOW defined', code='NO_WORKFLOW'))
    for wf_name, wf in ast.workflows.items():
        for step in wf.steps:
            if step.type == 'RUN':
                agent = step.data.get('agent')
                if agent not in agents:
                    errors.append(AQLValidationError(f"Agent '{agent}' referenced in workflow '{wf_name}' is not defined", code='UNKNOWN_AGENT'))
    for wf_name, wf in ast.workflows.items():
        cond = wf.loop_condition
        if cond and not re.match(r"^[\w\s><=!.()'\"+-]+$", cond):
            errors.append(AQLValidationError(f"Loop condition for '{wf_name}' contains unsupported characters", code='BAD_LOOP_COND'))
    return errors
