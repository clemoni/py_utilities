'''
Helper for mysql database
Needs to have a env_secret.yml file at the root.
'''
from mysql.connector import connect, Error
import functools
from os import getcwd
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
from utilities import primary_tools as pt



def get_yml_to_dic(yml_path):
    with open(yml_path, 'r') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

env_secret_path=Path(f"{getcwd()}/env_secret.yml")

# because of IPYNB (UGLY)
if env_secret_path.exists()==False:
    env_secret_path=Path("../env_secret.yml")
    if env_secret_path.exists()==False:
        env_secret_path=Path("../../env_secret.yml")

env_secret=get_yml_to_dic(env_secret_path)


def init_db(fn):
    def wrapper(*args, **kwargs):
        try:
            cnx=connect(
            host=env_secret['DBHOST'],
            user=env_secret['DBUSERNAME'],
            password=env_secret['DBPASSWORD'],
            database=env_secret['DBNAME']

            )
            cursor= cnx.cursor(dictionary=True)
            return fn(*args, **kwargs)(cursor, cnx)

        except Error as e:
            cnx.rollback()
            print(e)
        finally:
            cnx.close()
    return wrapper


def select_data(stmt):
    def wrapper(cursor, cnx):
        cursor.execute(stmt)
        return cursor.fetchall()
    return wrapper


def select_data_with_clause(query, value_dic):
    def wrapper(cursor, cnx):
        cursor.execute(query, value_dic)
        return cursor.fetchall()
    return wrapper


def get_stored_procedure(store_procedure):
    def wrapper(cursor, cnx):
        cursor.callproc(store_procedure)
        return pt.flatten_list([result.fetchall() for result in cursor.stored_results()])

    return wrapper

def insert_many_data(query, value_dic):
    def wrapper(cursor, cnx):
        cursor.executemany(query, value_dic)
        cnx.commit()
    return wrapper
    
def insert_one_data(query, value_dic):
    def wrapper(cursor, cnx):
        cursor.execute(query, value_dic)
        cnx.commit()
        cursor.execute('SELECT LAST_INSERT_ID()')
        res = cursor.fetchone()
        return res
    return wrapper

def update_on(query, value_dic):
    def wrapper(cursor, cnx):
        cursor.execute(query, value_dic)
        cnx.commit()
    return wrapper

select_data_to_db = init_db(select_data)

select_data_with_clause_to_db = init_db(select_data_with_clause)

insert_one_data_to_db = init_db(insert_one_data)

insert_many_to_db = init_db(insert_many_data)

update_one_to_db = init_db(update_on)

get_stored_procedure_from_db=init_db(get_stored_procedure)