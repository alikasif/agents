import logging
from typing import Dict, Any
logger = logging.getLogger(__name__)
class AgentRunner:
    def __init__(self, agent_callable):
        self.call = agent_callable
class TLRGraph:
    def __init__(self, agents: Dict[str, AgentRunner], loop_max=5, loop_cond_threshold=0.85):
        self.agents = agents
        self.loop_max = loop_max
        self.loop_cond_threshold = loop_cond_threshold
    def run(self, question: str, initial_prompt: str, max_iter: int = None):
        state = {'question': question, 'prompt': initial_prompt, 'iteration': 0, 'confidence': 0.0}
        max_iter = max_iter or self.loop_max
        logs = []
        while state['iteration'] < max_iter and state['confidence'] < self.loop_cond_threshold:
            state['iteration'] += 1
            logger.info(f"Iteration {state['iteration']} prompt={state['prompt']}")
            gen_out = self.agents['generator'].call({'question': state['question'], 'prompt': state['prompt']})
            state.update(gen_out)
            interp_out = self.agents['interpreter'].call({'prompt': state['prompt'], 'thoughts': state.get('thoughts'), 'answer': state.get('answer')})
            state['critique'] = interp_out.get('critique','')
            refl_out = self.agents['reflector'].call({'question': state['question'], 'prompt': state['prompt'], 'thoughts': state.get('thoughts'), 'answer': state.get('answer'), 'critique': state.get('critique')})
            state['prompt'] = refl_out.get('improved_prompt', state['prompt'])
            state['confidence'] = float(refl_out.get('confidence', 0.0))
            logs.append({'iter': state['iteration'], 'gen': gen_out, 'interp': interp_out, 'refl': refl_out, 'prompt': state['prompt'], 'confidence': state['confidence']})
        return {'state': state, 'logs': logs}
