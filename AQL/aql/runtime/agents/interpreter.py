from typing import Dict, Any
def interpreter_agent_call(inputs: Dict[str, Any]) -> Dict[str, Any]:
    prompt = inputs.get('prompt','')
    thoughts = inputs.get('thoughts','')
    critique_items = []
    if 'assume' in thoughts.lower():
        critique_items.append('invalid_assumption: model made an unsupported assumption')
    if 'verify' not in prompt.lower():
        critique_items.append('missing_verification_step')
    crit_text = '; '.join(critique_items) or 'no_issues_found'
    return {'critique': crit_text}
