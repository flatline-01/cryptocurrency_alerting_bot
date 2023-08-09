import os
import psycopg

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

connection = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host='localhost')
cursor = connection.cursor()


def save_alert(tg_id, crypto_abbr, option, price, delay):
    cursor.execute('INSERT INTO alerts (currency_abbr, price, telegram_id, delay, option) VALUES (%s,%s,%s,%s,%s)',
                   (crypto_abbr, price, tg_id, delay, option, ))
    connection.commit()


def read_all(tg_id):
    cursor.execute('SELECT * FROM alerts WHERE telegram_id = %s', (tg_id, ))
    return cursor.fetchall()


def remove_all(tg_id):
    cursor.execute('DELETE FROM alerts WHERE telegram_id = %s', (tg_id, ))
    connection.commit()