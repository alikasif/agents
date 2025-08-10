

def get_code_writer():
    pass


def get_code_reviewer():
    pass


def run_llm(client, model, messages, max_tokens=1200, temperature=0.2):
    """
    Run the LLM with the given parameters.
    """
    return client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )


def write_code(user_input: str):
    
    messages = [
        {"role": "system", "content": "You are a code writer. You write code based on user input and also improve it based on review."},
        {"role": "user", "content": user_input}
    ]

    code_writer = get_code_writer()
    response = run_llm(code_writer, "gpt-4.1", messages)
    
    response = response.choices[0].message.content.strip()


def review_code(code_writer_response: str):
    messages = [
        {"role": "system", "content": "You are a code reviewer."},
        {"role": "user", "content": code_writer_response}
    ]

    code_reviewer = get_code_reviewer()
    response = run_llm(code_reviewer, "gpt-4.1", messages)
    
    response = response.choices[0].message.content.strip()


def write_and_review(user_input: str):
    
    i=0
    while i < 3:
        code_writer_response = write_code(user_input)
        if code_writer_response is "ALL_OK":
            break
        i += 1
        review_comments = review_code(code_writer_response)
        user_input = review_comments
        
    

if __name__ == '__main__':
    print("This module is designed for code writing and reviewing tasks.")
    print("Use the functions to get a code writer or reviewer, write code, or review code.")
