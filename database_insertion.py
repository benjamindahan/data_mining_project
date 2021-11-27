import pymysql





def create_sql_connection(pswd):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password=pswd,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection, connection.cursor()


def x_fetchall(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    values = list()
    for row in rows:
        for key, value in row.items():
            values.append(value)
    return values

def get_id(id_type, cursor, name):
    query = f'SELECT {id_type}_id FROM {id_type}s WHERE {id_type}_name="{name}"'
    cursor.execute(query)
    return cursor.fetchone()[f'{id_type}_id']

def get_table_columns_label(cursor, table_name):
    query = f'SHOW COLUMNS FROM {table_name};'
    # We want all the column names, except the first one which is the primary key (autoincremented)
    cursor.execute(query)
    return tuple([db["Field"] for db in cursor.fetchall()][1:])

def create_insert_query(table_name, cols):
    query = f"""INSERT INTO {table_name} {str(cols).replace("'", "").replace('[', '(').replace(']', ')')} 
                VALUES ({('%s, '*len(cols))[:-2]});"""
    return query