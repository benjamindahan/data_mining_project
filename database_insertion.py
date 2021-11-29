import pymysql
import conf as c




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

def update_players_cut(players):
    query = f"""UPDATE players 
    SET birth_month = '{players[4]}',
    birth_day = {players[5]},
    birth_year = {players[6]},
    country = '{players[7]}',
    height = '{players[9]}',
    weight = '{players[10]}'
    WHERE player_name = '{players[2]}';
    """
    return query


def get_nr_players(cursor, team_id, season):
    query = f"SELECT COUNT(*) AS count FROM rosters WHERE season = {season} AND team_id = {team_id};"
    cursor.execute(query)
    return cursor.fetchone()['count']


def get_team_from_id(cursor,team_id):
    query = f'SELECT team_name FROM teams WHERE team_id={team_id}'
    cursor.execute(query)
    return cursor.fetchone()['team_name']


def get_boxscore_query(season):
    season = int(season)
    last_month = c.LAST_SEASON_MONTH
    if season == 2020:
        last_month = c.LAST_SEASON_MONTH_2020
    query = f"""SELECT * FROM games
        WHERE (year = {season} AND month >= {c.FIRST_SEASON_MONTH})
        OR (year = {season+1} AND month <= {last_month});"""
    return query