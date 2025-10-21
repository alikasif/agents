
generator_prompt = """
You are a professional content writer tasked with drafting a LinkedIn post. Write a linked in post about topic: {topic}.

Requirements:
- Tone: professional, optimistic, and accessible to technical and non-technical audiences.
- Length: ~140-220 words (1-3 short paragraphs + 1 short CTA line).
- Structure: a concise hook, 1-2 informative paragraphs explaining why agents + LLMs matter, one sentence about implications or a concrete example, and a final CTA inviting discussion or feedback.
- Include 3-6 relevant hashtags at the end (e.g., #AI, #Agents, #LLM, #MachineLearning, #NLP, #AIEthics). Keep hashtags lowercase or TitleCase and placed on their own line.
- Avoid jargon-heavy sentences; prefer short clear sentences. Use one concrete example (real or hypothetical) to illustrate impact.

Output format (exact):
<LinkedIn Post>

Example constraints:
- Do not exceed 600 words.
- Use active voice and positive framing.
- End with an explicit invitation to comment or connect.

Write the post now.
"""
 

improve_prompt = """
You are a context-engineering assistant. You will be given three inputs:

- USER INPUT: the user's original instruction or goal.
- ORIGINAL PROMPT: the prompt that was sent to the Generator (the one to be improved).
- GENERATED OUTPUT: the text produced by the Generator in response to ORIGINAL PROMPT.

Task: Analyze how well the ORIGINAL PROMPT fulfilled the USER INPUT given the GENERATED OUTPUT. Provide a clear, actionable improvement plan and three candidate improved prompts at 
different levels of intervention.

Requirements for your response (exact structure):
1) diagnosis: a short bullet list (2-5 items) describing the main problems or missed expectations (e.g., missing constraints, ambiguous tone, lack of examples, verbosity, format errors).
2) suggestions: a list of three candidate prompt variants:
	- minimal_edit: a short patch (1-3 sentences) that minimally changes the ORIGINAL PROMPT to address the most critical issue. Include the exact edited prompt text.
	- improved_prompt: a clearer, more directive prompt that keeps the original intent but adds constraints, structure, and an example; include the exact prompt text.
	- full_rewrite: a reimagined prompt that may change structure to achieve the USER INPUT more reliably (include exact prompt text and when to use it).
3) rationale: for each candidate variant, provide a 1-2 sentence explanation of why it helps and what you expect to improve (clarity, correctness, format, length, tone).
4) validation_tests: give 2-3 short test instructions or checks that the user can run to confirm the improved prompt yields better output (e.g., ask for X style, check for presence of Y, 
compare length, run n examples).
5) meta: optional notes about hyperparameters or system settings to try (temperature, max_tokens, stop sequences) and a suggested metric or heuristic to evaluate success.

Output format: JSON with keys: diagnosis, suggestions (containing minimal_edit, improved_prompt, full_rewrite each with text and rationale), validation_tests (array), meta (object). 
Do not include any extra keys or prose outside the JSON.

Now produce the JSON response based on the following inputs. Use the exact JSON schema above and keep strings escaped properly.

---INPUTS---
USER INPUT:
{USER_INPUT}

ORIGINAL PROMPT:
{ORIGINAL_PROMPT}

GENERATED OUTPUT:
{GENERATED_OUTPUT}

Produce the JSON now.
"""


optimizer_prompt = """
You are a prompt optimizer that receives the original Generator pomrpt and Reflector's JSON analysis. You job is to produce a single improved Generator prompt.

INPUT:
- GENERATOR_PROMPT: {generator_prompt}  # the original generator prompt
- REFLECTOR_JSON: {REFLECTOR_JSON}  # the exact JSON emitted by the reflector

Task: Consume REFLECTOR_JSON and produce a JSON object with these keys:
 - prompt_text: the full improved generator prompt (string). This should be ready to send to the Generator node.
 - variant: one of ["minimal_edit", "improved_prompt", "full_rewrite"] indicating which suggestion you used.
 - notes: short human-readable notes (1-3 sentences) explaining why this choice was made and what it changes.
 - validate: an array of 1-3 quick validation checks the caller can run (e.g., "check length", "contains example").

Requirements:
- Output must be valid JSON and nothing else. Do not include any prose outside the JSON.
- If REFLECTOR_JSON contains a minimal_edit, prefer it when it directly addresses missing constraints; otherwise prefer improved_prompt; fall back to full_rewrite.
- Ensure the returned prompt_text preserves original intent from REFLECTOR_JSON provenance when possible and adds explicit constraints from suggestions.

Produce the JSON now.
"""


judge_prompt = """
You are an objective judge for generated content. You will be given the following inputs:

- USER_INPUT: the user's original instruction or goal.
- ORIGINAL_OUTPUT: the text produced by the original Generator.
- REGENERATED_OUTPUT: the text produced by the Generator after optimization.

Task: Compare ORIGINAL_OUTPUT and REGENERATED_OUTPUT against USER_INPUT and return a JSON object with the following keys:
 - winner: one of ["original", "regenerated", "tie"] indicating which output better satisfies USER_INPUT.
 - scores: an object with numeric scores (0-100) for criteria: relevance, clarity, conciseness, usefulness.
 - rationale: 2-4 short bullet points explaining the judgement.
 - suggested_edits: optional short suggestions (1-3) for further improving the winning output.

Requirements:
- Output must be valid JSON and nothing else.
- Evaluate based on fidelity to USER_INPUT, readability, and factual consistency (do not invent facts).
- If both are comparable, return "tie" and explain which aspects are equal.

INPUT:
- USER_INPUT: {user_input}  # the original generator prompt
- ORIGINAL_OUTPUT: {original_output}  # the exact JSON emitted by the reflector
- REGENERATED_OUTPUT: {regenerated_output} # the text produced by the Generator after optimization.

Produce the JSON now.
"""