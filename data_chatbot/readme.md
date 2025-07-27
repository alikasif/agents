# Data Chatbot: SQL Generation and Execution Assistant

This project is an interactive Python-based assistant that helps users generate and execute SQL queries on a classic employee-department database using natural language. It leverages OpenAI's GPT models to generate SQL from user input and table metadata, and executes the queries on a local SQLite database.

## Project Structure

- **db_metadata.py**: Handles all database operations. It can initialize the database with the classic `emp` and `dept` tables and sample data, retrieve table metadata as JSON, and execute SQL queries, printing results in a nicely formatted table.
- **sql_generator.py**: Uses OpenAI's GPT (via the Chat Completion API) to generate SQL queries. It combines a system prompt (expert SQL generator) with user input and table metadata to produce context-aware SQL.
- **main.py**: The main entry point. It initializes the database, loads environment variables, and enters a loop to accept user requests, generate SQL, and execute it until the user types `exit`.

## Requirements

- Python 3.7+
- `openai` (for LLM-based SQL generation)
- `python-dotenv` (for loading environment variables)
- `IPython` (for Markdown display, optional for CLI usage)

Install dependencies with:

```bash
pip install openai python-dotenv ipython
```

## Setup

1. **Set your OpenAI API key**
   - Create a `.env` file in the `data-chatbot` directory with the following content:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

2. **(Optional) Adjust database path**
   - By default, the SQLite database is created as `emp_dept.db` in the current directory.

## How to Run

From the `data-chatbot` directory, run:

```bash
python main.py
```

- The assistant will initialize the database and prompt you for input.
- Type your request in natural language (e.g., `Show me all from emp` or `List all departments`).
- The assistant will generate the SQL, display it, execute it, and print the results.
- Type `exit` to quit.

## Example Usage

```
Enter your request (e.g., "Show me all from emp"): List all employees in the RESEARCH department

Generated SQL:
SELECT ...

empno | ename | job   | ...
------+-------+-------+-----
...
```

## Notes
- The project uses the classic EMP/DEPT schema and data, making it ideal for SQL learning and experimentation.
- The SQL generation uses OpenAI's GPT, so an internet connection and valid API key are required.
- All SQL execution is done on a local SQLite database for safety and convenience.

## License
This project is for educational and demonstration purposes.
