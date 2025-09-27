import os
import psycopg
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv("DB_HOST")

connection = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = connection.cursor()


def save_alert(tg_id, crypto_abbr, option, price, delay):
    cursor.execute('INSERT INTO alerts (currency_abbr, price, user_id, delay, option) VALUES (%s,%s,%s,%s,%s)',
                   (crypto_abbr, price, tg_id, delay, option, ))
    connection.commit()


def read_all(tg_id):
    cursor.execute('SELECT * FROM alerts WHERE user_id = %s', (tg_id, ))
    return cursor.fetchall()


def remove_all(tg_id):
    cursor.execute('DELETE FROM alerts WHERE user_id = %s', (tg_id, ))
    connection.commit()


def get_alert_by_user_id_and_alert_id(user_id, alert_id):
    cursor.execute('SELECT * FROM alerts WHERE user_id = %s AND id = %s', (user_id, alert_id, ))
    return cursor.fetchall()


def get_alert_by_id(alert_id):
    cursor.execute('SELECT * FROM alerts WHERE id = %s', (alert_id, ))
    return cursor.fetchone()


def remove_by_id(alert_id, user_id):
    cursor.execute('DELETE FROM alerts WHERE id = %s AND user_id = %s', (alert_id, user_id))
    connection.commit()


def get_user_by_id(user_id):
    cursor.execute('SELECT * FROM tg_users WHERE tg_id = %s', (user_id, ))
    return cursor.fetchone()


def save_user(user_id):
    cursor.execute('INSERT INTO tg_users(tg_id) VALUES(%s)', (user_id, ))
    connection.commit()