import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
@dataclass
class AgentDef:
    name: str
    role: str
    expose: List[str] = field(default_factory=list)
@dataclass
class WorkflowStep:
    type: str
    raw: str
    data: Dict[str, Any] = field(default_factory=dict)
@dataclass
class WorkflowDef:
    name: str
    inputs: List[str] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    loop_condition: Optional[str] = None
    max_iter: Optional[int] = None
@dataclass
class AQLProgram:
    agents: Dict[str, AgentDef] = field(default_factory=dict)
    workflows: Dict[str, WorkflowDef] = field(default_factory=dict)
    execute: Dict[str, Any] = field(default_factory=dict)
    
def parse_aql(source: str) -> AQLProgram:
    lines = [ln.rstrip() for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("//")]
    i = 0
    agents = {}
    workflows = {}
    execute = None
    while i < len(lines):
        ln = lines[i].strip()
        if ln.upper().startswith("AGENT "):
            name = ln.split()[1]
            role = None
            expose = []
            i += 1
            while i < len(lines) and not lines[i].strip().upper().startswith("END"):
                l = lines[i].strip()
                m = re.match(r"ROLE:\s*(\w+)", l, re.I)
                if m:
                    role = m.group(1)
                m = re.match(r"EXPOSE:\s*(.+)", l, re.I)
                if m:
                    expose = [s.strip() for s in m.group(1).split(",")]
                i += 1
            if not role:
                raise ValueError(f"Agent {name} missing ROLE")
            agents[name] = AgentDef(name=name, role=role, expose=expose)
            i += 1
            continue
        if ln.upper().startswith("WORKFLOW "):
            wf_name = ln.split()[1]
            inputs = []
            steps = []
            loop_condition = None
            max_iter = None
            i += 1
            in_steps = False
            while i < len(lines) and not lines[i].strip().upper().startswith("END"):
                l = lines[i].strip()
                if l.upper().startswith("INPUTS:"):
                    inputs = [s.strip() for s in l.split(":",1)[1].split(",")]
                elif l.upper().startswith("STEPS:"):
                    in_steps = True
                elif in_steps:
                    if l.upper().startswith("RUN "):
                        m = re.match(r"RUN\s+(\w+)\s+WITH\s+(.+?)\s+AS\s+\((.+)\)", l, re.I)
                        if not m:
                            m2 = re.match(r"RUN\s+(\w+)\s+WITH\s+(.+)", l, re.I)
                            if not m2:
                                raise ValueError(f"Cannot parse RUN step: {l}")
                            agent = m2.group(1)
                            with_args = [s.strip() for s in m2.group(2).split(",")]
                            out = []
                        else:
                            agent = m.group(1)
                            with_args = [s.strip() for s in m.group(2).split(",")]
                            out = [s.strip() for s in m.group(3).split(",")]
                        steps.append(WorkflowStep(type="RUN", raw=l, data={"agent":agent,"with":with_args,"out":out}))
                    elif l.upper().startswith("UPDATE "):
                        m = re.match(r"UPDATE\s+(.+)", l, re.I)
                        expr = m.group(1)
                        steps.append(WorkflowStep(type="UPDATE", raw=l, data={"expr":expr}))
                    else:
                        steps.append(WorkflowStep(type="RAW", raw=l, data={}))
                elif l.upper().startswith("LOOP UNTIL"):
                    m = re.match(r"LOOP\s+UNTIL\s+(.+?)(?:\s+MAX_ITER\s+(\d+))?$", l, re.I)
                    if m:
                        loop_condition = m.group(1).strip()
                        if m.group(2):
                            max_iter = int(m.group(2))
                i += 1
            workflows[wf_name] = WorkflowDef(name=wf_name, inputs=inputs, steps=steps, loop_condition=loop_condition, max_iter=max_iter)
            i += 1
            continue
        if ln.upper().startswith("EXECUTE "):
            m = re.match(r"EXECUTE\s+(\w+)\s+WITH\s+(.+)", ln, re.I)
            wf = m.group(1)
            args = {}
            for part in re.split(r',\s*(?=[\w_]+\s*=)', m.group(2)):
                k,v = part.split("=",1)
                args[k.strip()] = eval(v.strip())
            execute = {"workflow":wf,"args":args}
            i += 1
            continue
        i += 1
    return AQLProgram(agents=agents, workflows=workflows, execute=execute)
