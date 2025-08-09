import os
import sqlite3
import time
import math


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []
    
    def getImages(self):
        sql = '''SELECT * FROM images'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('Ошибка чтения из БД')
        return []
    
    def addImage(self, app, image):
        filename = image.filename
        filepath = app.config['UPLOAD_FOLDER'] + filename
        image.save(filepath)

        sql = f'''INSERT INTO images VALUES (NULL, '{filename}', 'images/{filename}')'''

        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка записи изображения в БД', str(e))
            return False
        return True
    
    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() AS count FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Пользователь с таким email уже существует')
                return False
            
            self.__cur.execute(f"INSERT INTO users VALUES (NULL, '{name}', '{email}', '{hpsw}', {math.floor(time.time())})")
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления пользователя в БД', str(e))
            return False
        return True