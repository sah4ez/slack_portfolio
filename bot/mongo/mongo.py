# import pymongo
# import property
#
#
# def get_connection():
#     return pymongo.MongoClient(host=property.DB_HOST, port=property.DB_PORT)
#
#
# def close_connection(connection):
#     connection.close()
#
#
# def add_stocks(stock):
#     conn = get_connection()
#     try:
#         db = conn['stocks']
#         db.close()
#     finally:
#         close_connection(conn)

import mongoengine as me
import property
from mongo import Stock as s


def connect():
    return me.connect(property.DB_COLLECT, host=property.DB_HOST, port=property.DB_PORT)


def contains(trade_code):
    stock = s.Stock.objects(trade_code=trade_code)
    return stock


