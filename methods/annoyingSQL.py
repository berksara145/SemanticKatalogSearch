# importing sqlite3 module
import sqlite3
import pandas as pd
import numpy as np


# 2. create database
connection=sqlite3.connect('aciklama.db')
curosr=connection.cursor()

# eğitim ve açıklamalarından SQL oluşturuyor
def createKatalogTime():
    # create the object of csv.reader()
    data = pd.read_csv("transformed_catalog_data.csv",delimiter=',')

    # 1. create query    
    Table_Query = '''CREATE TABLE if not Exists katalogTime(
    id INT PRIMARY KEY,
    NAME TEXT,
    DESC TEXT,
    TIME varchar(50),
    LEVEL varchar(30)
    );'''

    # 3. execute table query to create table
    curosr.execute(Table_Query)

    # 4. pase csv data
    for i, row in data.iterrows():
        # skip the first row

        
        name=row[1].replace("\"","\'")
        desc=row[2].replace("\"","\'")
        time=row[3]
        level=row[5].replace("\"","\'")
        
        print(i)
        print(name)
        print(desc)
        print(time)
        print(level)
        print("\n")

        # 5. create insert query
        InsertQuery=f'INSERT INTO katalogTime (id, NAME, DESC, TIME, LEVEL) VALUES ("{i + 1}","{name}","{desc}","{str(time)}","{level}")'
        # 6. Execute query
        curosr.execute(InsertQuery)    # 7. commit changes
# eğitim ve açıklamalarından SQL oluşturuyor
def createKatalogAciklamaSQL():
    # create the object of csv.reader()
    data = pd.read_csv("EgitimDesc761.csv",delimiter=',')

    # 1. create query    
    Table_Query = '''CREATE TABLE if not Exists katalogAciklama(
    id INT PRIMARY KEY,
    NAME TEXT,
    DESC TEXT 
    );'''

    # 3. execute table query to create table
    curosr.execute(Table_Query)

    # 4. pase csv data
    for i, row in data.iterrows():
        # skip the first row

        if(type(row[1]) == float):
            desc=row[0].replace("\"","\'")
        else:
            desc=row[1].replace("\"","\'")
        
        name=row[0].replace("\"","\'")
        
        print(i)
        print(name)
        print(desc)
        print("\n")

        # 5. create insert query
        InsertQuery=f'INSERT INTO katalogAciklama (id, NAME, DESC) VALUES ("{i + 1}","{name}","{desc}")'
        # 6. Execute query
        curosr.execute(InsertQuery)    # 7. commit changes

        print("commited")
# eğitim ve içindeki içeriklerden SQL oluşturuyor
def createIcerikKatalogSQL():
    # create the object of csv.reader()
    data = pd.read_csv("IcerikKatalog761.csv",delimiter=',')

    # 1. create query    
    Table_Query = '''CREATE TABLE if not Exists Icerikler(
    id INT PRIMARY KEY,
    NAME TEXT,
    IcerikAciklama TEXT
    );'''

    # 3. execute table query to create table
    curosr.execute(Table_Query)

    # 4. pase csv data
    for i, row in data.iterrows():
        
        #if there isn't any desc NAN then we use the name of it
        if(type(row[7]) == float):
            içerikAçıklama=row[1].replace("\"","\'")
        else:
            içerikAçıklama=row[7].replace("\"","\'")
        
        name=row[0].replace("\"","\'")
        
        # skip the first row
        print("\n")
        print(i)
        print(name)
        print(içerikAçıklama)
        
        
        InsertQuery=f'INSERT INTO Icerikler (id, NAME, IcerikAciklama) VALUES ("{i + 1}","{name}", "{içerikAçıklama}")'
        # 6. Execute query
        curosr.execute(InsertQuery)    # 7. commit changes
# ortak eğitimlerden açıklamalarını içeren SQL oluşturuyor
def createJoinedEgitimWithDesc():
    InsertQuery=f'''select a.NAME, a.DESC, coalesce(v.TIME, '80'), coalesce(v.LEVEL, 'Başlangıç')
    from katalogAciklama a 
    left outer join katalogTime v on a.Name = v.Name
    order by 1'''
    curosr.execute(InsertQuery)    # 7. commit changes
    records = curosr.fetchall()

    i = 1
    for row in records:
        print(i)
        print("name: ", row[0])
        print("desc: ", row[1])
        print("time: ", row[2])
        print("level: ", row[3])
        print("\n")
        i += 1

    df = pd.DataFrame(records)
    print(df.head)
    print(df.shape)
    df.to_csv('EgitimDesc1000.csv', index=False)
    print(df.iat[5,0])
# ortak eğitimlerden içerik ve ait olduğu eğitimlerin SQL ini oluşturuyor
def createJoinedIcerikWithDesc():
    InsertQuery=f'''select v.NAME, v.IcerikAciklama
    from Icerikler v 
    inner join (select NAME from
                katalogAciklama) a  on a.NAME = v.NAME  order by v.NAME'''
    curosr.execute(InsertQuery)    # 7. commit changes
    records = curosr.fetchall()

    i = 1
    for row in records:
        print(i)
        print("name: ", row[0])
        print("IcerikAciklama: ", row[1])
        print("\n")
        i += 1

    df = pd.DataFrame(records)
    print(df.head)
    print(df.shape)
    df.to_csv('IcerikKatalog761.csv', index=False)
    print(df.iat[5,0])

def trySelectQuery():
    InsertQuery = ''' SELECT * FROM KatalogTime '''
    curosr.execute(InsertQuery)    # 7. commit changes
    records = curosr.fetchall()

    i = 1
    for row in records:
        print(i)
        print("name: ", row[0])
        print("desc: ", row[1])
        print("\n")
        i += 1

"""
createKatalogAciklamaSQL()
createKatalogTime()
createJoinedEgitimWithDesc()
"""

#trySelectQuery()
# 8. close connection

connection.close()