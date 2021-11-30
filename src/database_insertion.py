import pymysql
import src.conf as c


def create_sql_connection(pswd):
    """
    This function creates the connection with MySQL
    :param pswd: the password that is in the dotenv file
    :return: the connection and the cursor
    """
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password=pswd,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection, connection.cursor()


def x_fetchall(cursor, query):
    """
    This function runs a query and gets all the values that were requested
    :param cursor: the SQL cursor
    :param query: the SQL query to run
    :return: the requested values
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    values = list()
    for row in rows:
        for key, value in row.items():
            values.append(value)
    return values


def get_id(id_type, cursor, name):
    """
    This function creates a query that given the name of the player or the team, it returns the team_id/player_id
    :param id_type: player/team name
    :param cursor: SQL cursor
    :param name: the name of the player/team  for whom the id is desired
    :return: the id
    """
    query = f'SELECT {id_type}_id FROM {id_type}s WHERE {id_type}_name="{name}"'
    cursor.execute(query)
    return cursor.fetchone()[f'{id_type}_id']


def get_table_columns_label(cursor, table_name):
    """
    This function creates a query that gets the name of all the columns in a selected table
    :param cursor: SQL cursor
    :param table_name: the name of the table where the columns are required
    :return: a list with all the column names
    """
    query = f'SHOW COLUMNS FROM {table_name};'
    # We want all the column names, except the first one which is the primary key (autoincremented)
    cursor.execute(query)
    return tuple([db["Field"] for db in cursor.fetchall()][1:])


def create_insert_query(table_name, cols):
    """
    This function creates a query that allows to insert values to a specific table
    :param table_name: the table where you want to add data
    :param cols: the name of the columns of that table
    :return: the desired query
    """
    query = f"""INSERT IGNORE INTO {table_name} {str(cols).replace("'", "").replace('[', '(').replace(']', ')')} 
                VALUES ({('%s, ' * len(cols))[:-2]});"""
    return query


def update_players_cut(players):
    """
    Some players get cut by their team: they have a salary but they are not in the team roster.
    For those players, the data in players needs to be updated
    :param players: a list of the players to update
    :return: the query that allows to update the players
    """
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
    """
    This function gets the number of players that played in a selected season in an specific team
    :param cursor: the SQL cursor
    :param team_id: the specific team
    :param season: the selected season
    :return: the nr of players
    """
    query = f"SELECT COUNT(*) AS count FROM rosters WHERE season = {season} AND team_id = {team_id};"
    cursor.execute(query)
    return cursor.fetchone()['count']


def get_team_from_id(cursor, team_id):
    """
    This function gets the team_name given the team_id
    :param cursor: the SQL cursor
    :param team_id: the team_id for which the team name is desired
    :return: the team name
    """
    query = f'SELECT team_name FROM teams WHERE team_id={team_id}'
    cursor.execute(query)
    return cursor.fetchone()['team_name']


def get_boxscore_query(season):
    """
    For boxscore, you need a specific season, which starts in one year and ends the following year.
    This function selects the correct dates from which to scrape the boxscore.
    :param season: the season desired
    :return: the query that allows to select the accurate dates.
    """
    season = int(season)
    last_month = c.LAST_SEASON_MONTH
    if season == 2020:
        last_month = c.LAST_SEASON_MONTH_2020
    query = f"""SELECT * FROM games
        WHERE (year = {season} AND month >= {c.FIRST_SEASON_MONTH})
        OR (year = {season + 1} AND month <= {last_month});"""
    return query
