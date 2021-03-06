import pymysql
from dotenv import load_dotenv
import os
import sys

assert load_dotenv() is True


def database_connection():
    """
    This function creates the database connection.
    :return: the SQL cursor
    """
    try:
        pswd = os.getenv("password")
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password=pswd,
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        return cursor
    except pymysql.err.OperationalError:
        print("☠️ You need to have a .env file with password = your_password!! ")
        sys.exit()


def create_database(cursor):
    """
    This function creates the database
    :param cursor: the SQL cursor
    """
    # CREATING DATABASE
    query = """CREATE DATABASE IF NOT EXISTS basketball_reference DEFAULT CHARACTER SET utf8;"""
    cursor.execute(query)


def use_database(cursor):
    """
    This function performs a SQL query to use the newly created database.
    """
    query = """USE basketball_reference;"""
    cursor.execute(query)


def create_table_players(cursor):
    """
    This function creates the table players.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.players(
      player_id INT NOT NULL AUTO_INCREMENT,
      player_name VARCHAR(45) NOT NULL,
      birth_month VARCHAR(45) NULL,
      birth_day INT NULL,
      birth_year YEAR NULL,
      country VARCHAR(3) NULL,
      height VARCHAR(5) NULL,
      weight INT NULL,
      PRIMARY KEY (player_id),
      CONSTRAINT Index_2 UNIQUE (player_id, player_name, birth_month, birth_day, birth_year, country, height))
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_teams(cursor):
    """
    This function creates the table teams.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.teams(
      team_id INT NOT NULL AUTO_INCREMENT,
      team_name VARCHAR(3) NULL UNIQUE,
      city VARCHAR(30) NULL,
      full_name VARCHAR(30) NULL,
      conference_name VARCHAR(30) NULL,
      division_name VARCHAR(30) NULL,
      team_id_api INT NULL,
      PRIMARY KEY (team_id))
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_rosters(cursor):
    """
    This function creates the table rosters
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.rosters (
      roster_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      player_number INT NULL,
      player_position VARCHAR(2) NULL,
      player_experience INT NULL,
      player_id INT NOT NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (roster_id),
      CONSTRAINT Index_2 UNIQUE (season, player_number, player_position, player_experience, player_id, team_id),
      CONSTRAINT fk_rosters_players1
        FOREIGN KEY (player_id)
        REFERENCES basketball_reference.players (player_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
      CONSTRAINT fk_rosters_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_salaries(cursor):
    """
    This function creates the table salaries.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.salaries (
      salary_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      salary INT NULL,
      player_id INT NOT NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (salary_id),
      CONSTRAINT Index_2 UNIQUE (season, salary, player_id, team_id),
      CONSTRAINT fk_salaries_players1
        FOREIGN KEY (player_id)
        REFERENCES basketball_reference.players (player_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
      CONSTRAINT fk_salaries_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_player_stats(cursor):
    """
    This function creates the table player stats.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.players_stats (
      players_stats_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      age INT NULL,
      games_played INT NULL,
      games_started INT NULL,
      mpg FLOAT NULL,
      fg_pg FLOAT NULL,
      fga_pg FLOAT NULL,
      fg_pct FLOAT NULL,
      fg3_pg FLOAT NULL,
      fg3a_pg FLOAT NULL,
      fg3_pct FLOAT NULL,
      fg2_pg FLOAT NULL,
      fg2a_pg FLOAT NULL,
      fg2_pct FLOAT NULL,
      ft_pg FLOAT NULL,
      fta_pg FLOAT NULL,
      ft_pct FLOAT NULL,
      efg_pct FLOAT NULL,
      orb_pg FLOAT NULL,
      drb_pg FLOAT NULL,
      trb_pg FLOAT NULL,
      ast_pg FLOAT NULL,
      stl_pg FLOAT NULL,
      blk_pg FLOAT NULL,
      tov_pg FLOAT NULL,
      pf_pg FLOAT NULL,
      pts_pg FLOAT NULL,
      player_id INT NOT NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (players_stats_id),
      CONSTRAINT Index_2 UNIQUE (season, player_id, team_id),
      CONSTRAINT fk_players_stats_players1
        FOREIGN KEY (player_id)
        REFERENCES basketball_reference.players (player_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
      CONSTRAINT fk_players_stats_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_teams_summaries(cursor):
    """
    This function creates the table teams summaries.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.teams_summaries (
      summary_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      n_wins INT NULL,
      n_loss INT NULL,
      conf_ranking INT NULL,
      coach_name VARCHAR(45) NULL,
      ppg FLOAT NULL,
      opp_ppg FLOAT NULL,
      pace FLOAT NULL,
      off_rtg FLOAT NULL,
      def_rtg FLOAT NULL,
      expected_wins INT NULL,
      expected_loss INT NULL,
      expected_overall_ranking INT NULL,
      preseason_odds VARCHAR(15) NULL,
      attendance INT NULL,
      playoffs VARCHAR(200) NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (summary_id),
      CONSTRAINT Index_2 UNIQUE (season, team_id),
      CONSTRAINT fk_teams_summaries_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_teams_stats(cursor):
    """
    This function creates the table teams stats
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.teams_stats (
      teams_stats_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      mp INT NULL,
      fg_team INT NULL,
      fga_team INT NULL,
      fg_pct_team FLOAT NULL,
      fg3_team INT NULL,
      fg3a_team INT NULL,
      fg3_pct_team FLOAT NULL,
      fg2_team INT NULL,
      fg2a_team INT NULL,
      fg2_pct_team FLOAT NULL,
      ft_team INT NULL,
      fta_team INT NULL,
      ft_pct_team FLOAT NULL,
      orb_team INT NULL,
      drb_team INT NULL,
      trb_team INT NULL,
      ast_team INT NULL,
      stl_team INT NULL,
      blk_team INT NULL,
      tov_team INT NULL,
      pf_team INT NULL,
      pts_team INT NULL,
      fg_opp INT NULL,
      fga_opp INT NULL,
      fg_pct_opp FLOAT NULL,
      fg3_opp INT NULL,
      fg3a_opp INT NULL,
      fg3_pct_opp FLOAT NULL,
      fg2_opp INT NULL,
      fg2a_opp INT NULL,
      fg2_pct_opp FLOAT NULL,
      ft_opp INT NULL,
      fta_opp INT NULL,
      ft_pct_opp FLOAT NULL,
      orb_opp INT NULL,
      drb_opp INT NULL,
      trb_opp INT NULL,
      ast_opp INT NULL,
      stl_opp INT NULL,
      blk_opp INT NULL,
      tov_opp INT NULL,
      pf_opp INT NULL,
      pts_opp INT NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (teams_stats_id),
      CONSTRAINT Index_2 UNIQUE (season, team_id),
      CONSTRAINT fk_teams_stats_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_teams_ranks(cursor):
    """
    This function creates the table teams ranks.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.teams_ranks (
      teams_ranks_id INT NOT NULL AUTO_INCREMENT,
      season YEAR NULL,
      mp INT NULL,
      fg_team INT NULL,
      fga_team INT NULL,
      fg_pct_team INT NULL,
      fg3_team INT NULL,
      fg3a_team INT NULL,
      fg3_pct_team INT NULL,
      fg2_team INT NULL,
      fg2a_team INT NULL,
      fg2_pct_team INT NULL,
      ft_team INT NULL,
      fta_team INT NULL,
      ft_pct_team INT NULL,
      orb_team INT NULL,
      drb_team INT NULL,
      trb_team INT NULL,
      ast_team INT NULL,
      stl_team INT NULL,
      blk_team INT NULL,
      tov_team INT NULL,
      pf_team INT NULL,
      pts_team INT NULL,
      fg_opp INT NULL,
      fga_opp INT NULL,
      fg_pct_opp INT NULL,
      fg3_opp INT NULL,
      fg3a_opp INT NULL,
      fg3_pct_opp INT NULL,
      fg2_opp INT NULL,
      fg2a_opp INT NULL,
      fg2_pct_opp INT NULL,
      ft_opp INT NULL,
      fta_opp INT NULL,
      ft_pct_opp INT NULL,
      orb_opp INT NULL,
      drb_opp INT NULL,
      trb_opp INT NULL,
      ast_opp INT NULL,
      stl_opp INT NULL,
      blk_opp INT NULL,
      tov_opp INT NULL,
      pf_opp INT NULL,
      pts_opp INT NULL,
      team_id INT NOT NULL,
      PRIMARY KEY (teams_ranks_id),
      CONSTRAINT Index_2 UNIQUE (season,  team_id),
      CONSTRAINT fk_teams_ranks_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_games(cursor):
    """
    This function creates the table games.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.games (
      game_id INT NOT NULL AUTO_INCREMENT,
      day INT NULL,
      month INT NULL,
      year YEAR NULL,
      home TINYINT NULL,
      url VARCHAR(100) NULL,
      team_id INT NOT NULL,
      opp_id INT NOT NULL,
      PRIMARY KEY (game_id),
      CONSTRAINT Index_2 UNIQUE (day,month,year,team_id),
      CONSTRAINT fk_games_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
      CONSTRAINT fk_games_teams2
        FOREIGN KEY (opp_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_boxscores(cursor):
    """
    This function creates the table boxscores.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.boxscores (
      boxscore_id INT NOT NULL AUTO_INCREMENT,
      mp VARCHAR(6) NULL,
      fg INT NULL,
      fga INT NULL,
      fg_pct FLOAT NULL,
      fg3 INT NULL,
      fg3a INT NULL,
      fg3_pct FLOAT NULL,
      ft INT NULL,
      fta INT NULL,
      ft_pct FLOAT NULL,
      orb INT NULL,
      drb INT NULL,
      trb INT NULL,
      ast INT NULL,
      stl INT NULL,
      blk INT NULL,
      tov INT NULL,
      pf INT NULL,
      pts INT NULL,
      plus_minus VARCHAR(5) NULL,
      ts_pct FLOAT NULL,
      efg_pct FLOAT NULL,
      fg3a_per_fga_pct FLOAT NULL,
      fta_per_fga_pct FLOAT NULL,
      orb_pct FLOAT NULL,
      drb_pct FLOAT NULL,
      trb_pct FLOAT NULL,
      ast_pct FLOAT NULL,
      stl_pct FLOAT NULL,
      blk_pct FLOAT NULL,
      tov_pct FLOAT NULL,
      usg_pct FLOAT NULL,
      off_rtg INT NULL,
      def_rtg INT NULL,
      bpm FLOAT NULL,
      player_id INT NOT NULL,
      game_id INT NOT NULL,
      PRIMARY KEY (boxscore_id),
      CONSTRAINT Index_2 UNIQUE (player_id, game_id),
      CONSTRAINT fk_boxscores_games1
        FOREIGN KEY (game_id)
        REFERENCES basketball_reference.games (game_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION,
      CONSTRAINT fk_boxscores_players1
        FOREIGN KEY (player_id)
        REFERENCES basketball_reference.players (player_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def create_table_standings(cursor):
    """
    This function creates the table standings.
    """
    query = """
    CREATE TABLE IF NOT EXISTS basketball_reference.standings (
      standings_id INT NOT NULL AUTO_INCREMENT,
      team_id INT NOT NULL,
      wins INT NOT NULL,
      loss INT NOT NULL,
      season INT NOT NULL,
      conference VARCHAR(20) NULL,
      conference_rank INT NULL,
      conference_wins INT NULL,
      conference_loss INT NULL,
      division VARCHAR(30) NULL,
      division_rank INT NULL,
      division_wins INT NULL,
      division_loss INT NULL,
      PRIMARY KEY (standings_id),
      CONSTRAINT Index_2 UNIQUE (season,  team_id),
      CONSTRAINT fk_standings_teams1
        FOREIGN KEY (team_id)
        REFERENCES basketball_reference.teams (team_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION)
    ENGINE = InnoDB;"""
    cursor.execute(query)


def creation_script():
    """
    This function runs all the database creation script.
    """
    cursor = database_connection()
    create_database(cursor)
    use_database(cursor)
    create_table_players(cursor)
    create_table_teams(cursor)
    create_table_rosters(cursor)
    create_table_salaries(cursor)
    create_table_player_stats(cursor)
    create_table_teams_summaries(cursor)
    create_table_teams_stats(cursor)
    create_table_teams_ranks(cursor)
    create_table_games(cursor)
    create_table_boxscores(cursor)
    create_table_standings(cursor)
