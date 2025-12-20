from typing import Dict, Any
TEMPLATE = """# Auto-generated AQL transpiled runner
from aql.runtime.graph import TLRGraph, AgentRunner
from aql.runtime.agents.generator import generator_agent_call
from aql.runtime.agents.interpreter import interpreter_agent_call
from aql.runtime.agents.reflector import reflector_agent_call
import json
def build_graph():
    agents = {
        'generator': AgentRunner(generator_agent_call),
        'interpreter': AgentRunner(interpreter_agent_call),
        'reflector': AgentRunner(reflector_agent_call),
    }
    graph = TLRGraph(agents=agents, loop_max={max_iter}, loop_cond_threshold={threshold})
    return graph
if __name__ == '__main__':
    g = build_graph()
    res = g.run(question={question!r}, initial_prompt={prompt!r}, max_iter={max_iter})
    print(json.dumps(res, indent=2))
"""

def transpile_ast_to_code(ast, exec_args: Dict[str,Any]):
    wf = list(ast.workflows.values())[0]
    max_iter = wf.max_iter or 5
    threshold = 0.85
    question = exec_args.get('question','Example question')
    prompt = exec_args.get('initial_prompt','Summarize briefly')
    return TEMPLATE.format(max_iter=max_iter, threshold=threshold, question=question, prompt=prompt)

def compile_to_graph_spec(ast):
    nodes = []
    for name, ag in ast.agents.items():
        nodes.append({'id': name, 'role': ag.role, 'expose': ag.expose})
    wf = list(ast.workflows.values())[0]
    steps = []
    for st in wf.steps:
        steps.append({'type': st.type, 'raw': st.raw, 'data': st.data})
    return {'agents': nodes, 'workflow': {'name': wf.name, 'inputs': wf.inputs, 'steps': steps, 'loop_condition': wf.loop_condition, 'max_iter': wf.max_iter}}
