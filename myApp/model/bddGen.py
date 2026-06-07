import mysql.connector
from mysql.connector import pooling 
from flask import flash
from ..config import DB_SERVER, COLOR

cnx_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    pool_reset_session=True,
    **DB_SERVER
)

def connexion():
    try:
        cnx = cnx_pool.get_connection()
        return cnx
    except mysql.connector.Error as err:
        msg = f"{err} <br/> Veuillez vérifier les paramètres dans config.py"
        flash(msg, "danger")
        print(f"{COLOR['red']}{msg}{COLOR['end']}")
        return None
        
def queryData(type, sql, param, funct_name, message=None):
    cnx = connexion()
    if cnx is None:
        return None
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(sql, param)
        if type == 'select':
            res = cursor.fetchall()
        elif type == 'selectOne':
            res = cursor.fetchone()
        elif type == "addMany" or type == "add":
            res = cursor.lastrowid
        elif type == "delete" or type == "update":
            res = True
        else:
            res = False
        cnx.commit()
        cursor.close()
        if message:
            flash(message['ok'], "success")
        print(f"{COLOR['green']}{funct_name}{COLOR['end']}")
        return res
    except mysql.connector.Error as err:
        cnx.rollback()
        msg = f"{message['echec']} : {err}" if message else str(err)
        flash(msg, "danger")
        print(f"{COLOR['red']}{sql}\n{funct_name}\n{err}{COLOR['end']}")
        return None
    finally:
        if cnx:
            cnx.close()
        
def selectOneData(funct_name, sql, param=None, message=None):
    return queryData("selectOne", sql, param, funct_name, message)

def selectData(funct_name, sql, param=None, message=None):
    return queryData("select", sql, param, funct_name, message)

def addData(funct_name, sql, param=None, message=None):
    return queryData("add", sql, param, funct_name, message)

def updateData(funct_name, sql, param=None, message=None):
    return queryData("update", sql, param, funct_name, message)

def deleteData(funct_name, sql, param=None, message=None):
    return queryData("delete", sql, param, funct_name, message)