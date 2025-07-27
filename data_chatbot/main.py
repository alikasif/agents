import db_metadata
import sql_generator
from dotenv import load_dotenv

DB_PATH = 'emp_dept.db'

def main():
    load_dotenv(override=True)
    print('Initializing database...')
    db_metadata.init_db(DB_PATH)
    print('Database ready. Type "exit" to quit.')
    while True:
        user_input = input('Enter your request (e.g., "Show me all from emp"): ')
        if user_input.strip().lower() == 'exit':
            print('Goodbye!')
            break
        # Extract table name (assume last word)
        table_names = ['emp', 'dept']
        metadata_json = db_metadata.get_table_metadata(table_names, DB_PATH)
        sql = sql_generator.generate_sql(user_input, metadata_json)
        print('\nGenerated SQL:')
        print(sql)
        db_metadata.execute_sql(sql, DB_PATH)
        
if __name__ == '__main__':
    main() 