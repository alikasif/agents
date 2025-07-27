import json
import os
from openai import OpenAI
from anthropic import Anthropic


def generate_sql(user_input, table_metadata_json):
    """
    Uses OpenAI GPT to generate SQL based on user input and table metadata.
    """
    # Enhanced system prompt
    system_prompt = (
        "You are an expert SQL generator. Your job is to generate syntactically correct and efficient SQL queries "
        "based strictly on the user's request and the provided table metadata.\n"
        "- Use only the columns and tables described in the metadata.\n"
        "- If multiple tables are provided, infer relationships based on column names (e.g., user_id in one table and id in another).\n"
        "- Use JOINs where appropriate.\n"
        "- If the user requests filtering, sorting, or aggregation, include the necessary SQL clauses.\n"
        "- Do not make up columns or tables that are not in the metadata.\n"
        "- Return only the SQL code, with no explanation or comments.\n"
        "- If the request is ambiguous, make reasonable assumptions but do not ask clarifying questions.\n"
        "- Always use best practices for SQL generation."
    )
    user_prompt = (
        f"User request: {user_input}\n"
        f"Table metadata: {table_metadata_json}"
    )
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        openai = OpenAI()
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=1024,
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        return sql
    except Exception as e:
        return f"-- Error generating SQL: {e}" 