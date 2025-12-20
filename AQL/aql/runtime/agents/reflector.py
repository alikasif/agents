from typing import Dict, Any
def reflector_agent_call(inputs: Dict[str, Any]) -> Dict[str, Any]:
    question = inputs.get('question','')
    prompt = inputs.get('prompt','')
    thoughts = inputs.get('thoughts','')
    answer = inputs.get('answer','')
    critique = inputs.get('critique','')
    improved_prompt = prompt
    changes = []
    if 'missing_verification' in critique or 'missing_verification_step' in critique:
        improved_prompt += ' | ADD: include explicit verification steps.'
        changes.append('added verification')
    if 'invalid_assumption' in critique:
        improved_prompt += ' | ADD: never assume missing numeric values; state uncertainty instead.'
        changes.append('assumption_guard')
    confidence = 0.9 if not changes else 0.7
    return {'improved_prompt': improved_prompt, 'confidence': confidence, 'changes': changes}
