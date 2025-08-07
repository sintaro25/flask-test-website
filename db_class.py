import os
import sqlite3


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