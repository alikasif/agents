import json
import sqlite3

def get_connection(db_path):
    """
    Returns a connection to the SQLite database at db_path.
    """
    return sqlite3.connect(db_path)

def execute_sql(sql, db_path):
    """
    Executes the given SQL statement on the SQLite database at db_path.
    For SELECT statements, returns (columns, rows) and prints a formatted table.
    For other statements, returns a success message and prints it.
    On error, returns (None, error_message) and prints the error.
    """
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        if sql.strip().lower().startswith('select'):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            # Print formatted table
            if rows:
                col_widths = [max(len(str(col)), max((len(str(row[i])) for row in rows), default=0)) for i, col in enumerate(columns)]
                header = ' | '.join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
                separator = '-+-'.join('-' * col_widths[i] for i in range(len(columns)))
                print(header)
                print(separator)
                for row in rows:
                    print(' | '.join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))
            else:
                print('No results.')
        else:
            conn.commit()
            print('SQL executed successfully.')
    except Exception as e:
        print(f'Error executing SQL: {e}')
    finally:
        if 'conn' in locals():
            conn.close()

def init_db(db_path):
    """
    Initializes the SQLite database with 'emp' and 'dept' tables and inserts sample records based on the classic emp-dept schema.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    # Create dept table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dept (
            deptno INTEGER PRIMARY KEY,
            dname TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    # Create emp table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emp (
            empno INTEGER PRIMARY KEY,
            ename TEXT NOT NULL,
            job TEXT NOT NULL,
            mgr INTEGER,
            hiredate TEXT,
            sal REAL,
            comm REAL,
            deptno INTEGER NOT NULL,
            FOREIGN KEY(deptno) REFERENCES dept(deptno)
        )
    ''')
    # Insert sample departments
    cursor.executemany(
        "INSERT OR IGNORE INTO dept (deptno, dname, location) VALUES (?, ?, ?)",
        [
            (10, 'ACCOUNTING', 'NEW YORK'),
            (20, 'RESEARCH', 'DALLAS'),
            (30, 'SALES', 'CHICAGO'),
            (40, 'OPERATIONS', 'BOSTON')
        ]
    )
    # Insert sample employees
    cursor.executemany(
        "INSERT OR IGNORE INTO emp (empno, ename, job, mgr, hiredate, sal, comm, deptno) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (7369, 'SMITH', 'CLERK', 7902, '1993-06-13', 800.00, 0.00, 20),
            (7499, 'ALLEN', 'SALESMAN', 7698, '1998-08-15', 1600.00, 300.00, 30),
            (7521, 'WARD', 'SALESMAN', 7698, '1996-03-26', 1250.00, 500.00, 30),
            (7566, 'JONES', 'MANAGER', 7839, '1995-10-31', 2975.00, None, 20),
            (7698, 'BLAKE', 'MANAGER', 7839, '1992-06-11', 2850.00, None, 30),
            (7782, 'CLARK', 'MANAGER', 7839, '1993-05-14', 2450.00, None, 10),
            (7788, 'SCOTT', 'ANALYST', 7566, '1996-03-05', 3000.00, None, 20),
            (7839, 'KING', 'PRESIDENT', None, '1990-06-09', 5000.00, 0.00, 10),
            (7844, 'TURNER', 'SALESMAN', 7698, '1995-06-04', 1500.00, 0.00, 30),
            (7876, 'ADAMS', 'CLERK', 7788, '1999-06-04', 1100.00, None, 20),
            (7900, 'JAMES', 'CLERK', 7698, '2000-06-23', 950.00, None, 30),
            (7934, 'MILLER', 'CLERK', 7782, '2000-01-21', 1300.00, None, 10),
            (7902, 'FORD', 'ANALYST', 7566, '1997-12-05', 3000.00, None, 20),
            (7654, 'MARTIN', 'SALESMAN', 7698, '1998-12-05', 1250.00, 1400.00, 30)
        ]
    )
    conn.commit()
    conn.close()

def get_table_metadata(table_names, db_path):
    """
    Reads metadata for one or more tables from the SQLite database and returns it as JSON.
    Accepts a single table name (str) or a list of table names (list).
    """
    if isinstance(table_names, str):
        table_names = [table_names]
    result = {}
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        for table_name in table_names:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            if not columns:
                result[table_name] = {'error': 'Table not found'}
            else:
                result[table_name] = {
                    'columns': [
                        {
                            'name': col[1],
                            'type': col[2],
                            'primary_key': bool(col[5])
                        } for col in columns
                    ]
                }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        if 'conn' in locals():
            conn.close() 