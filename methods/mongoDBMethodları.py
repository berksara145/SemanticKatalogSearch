import pymongo
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
import openai
from içerikHazirlama import getMatchingArray
    
def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print("BASEDIR: meto", BASEDIR)
    BASEDIR = os.path.dirname(BASEDIR)
    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  

loadingEnv()

DATABASE_ID = "semanticDB"
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
COLLECTION_ID_EMBEDDINGS = "icerikEmbeds"
COLLECTION_ID_LOGS = "logs"
COLLECTION_ID_CATALOG_DESC = "catalogDesc"
COLLECTION_ID_MATCHING_TABLE = "matchingTable"

# collectionları siliyor
def dropAllCollections():
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING )
    db=client[DATABASE_ID]
    db.drop_collection(COLLECTION_ID_EMBEDDINGS)
    db.drop_collection(COLLECTION_ID_LOGS)
    db.drop_collection(COLLECTION_ID_CATALOG_DESC)
    db.drop_collection(COLLECTION_ID_MATCHING_TABLE)
# collectionları oluşturuyor
def CreateEmbeddingsDatabase():
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING )
    db=client[DATABASE_ID]
    db.create_collection(COLLECTION_ID_EMBEDDINGS)
    db.create_collection(COLLECTION_ID_LOGS)
    db.create_collection(COLLECTION_ID_CATALOG_DESC)
    db.create_collection(COLLECTION_ID_MATCHING_TABLE)
    print("created collections")
# eğitimler ve açıklamalarını döndürüyor csvden
def readEğitimDesc():

    df_embeddings = pd.read_csv('newCSVs/egitimDesc1000~.csv', sep="~")    
    print(df_embeddings.head())
    print(df_embeddings.shape)

    return df_embeddings
# içerik açıklama embedlerini döndürüyor csvden
def readEmbeddings():
    df_embeddings = pd.read_csv('newCSVs/embeddedİçerik761.csv')    
    print(df_embeddings.head())
    print(df_embeddings.shape)

    return df_embeddings
# embeddings csv dosyasındaki embeddings verilerini cosmodb'ye yazar. Sadece indexi ve içerik embedi
def ExportAndCreateEmbeddings():
    print("ExportEmbeddings")
    embeddingList = readEmbeddings()
    CreateIcerikEmbeds(embeddingList) 
def CreateIcerikEmbeds(embeddingList):
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    db = client.get_database(DATABASE_ID)
    for index, row in embeddingList.iterrows():
        # convert index into a string
        i = str(index+1)
        print("index:") 
        print(i)
        embeding = EmbeddingItem(i, row['embeddedİçerik'])
        db[COLLECTION_ID_EMBEDDINGS].insert_one(embeding)
        print("item created")

    print("created içerik embeddings")
def EmbeddingItem(index, embedding):
    embedding_array = np.array(eval(embedding))
    item = {'id' : index,
            'vectorContent' : embedding_array.tolist()}
    return item
# cosmos db vektörler için index oluşturuyor
def CreateEmbeddingsVectorIndex():
    # Connect to the Cosmos DB using the Azure Cosmos Client
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING )
    db = client.get_database(DATABASE_ID)

    index_spec = [
    ('vectorContent', 'text')  # Specify the field and its type in a tuple
    ]

    # Create the index
    db[COLLECTION_ID_EMBEDDINGS].create_index(index_spec, name='vectorSearchIndex', cosmosSearchOptions={
        'kind': 'vector-ivf',
        'numLists': 100,
        'similarity': 'COS',
        'dimensions': 1536
    })
    print("Index created successfully")
# cosmos dbye eğitim ismini, açıklamasını ve indexini yazıyor
def CreateEğitimler():
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING )
    db=client[DATABASE_ID]   
    df_egitimDesc = readEğitimDesc()

    for index, row in df_egitimDesc.iterrows():
        # convert index into a string
        i = str(index+1)
        print("index:") 
        print(i)
        item = {'id'     : i,
                'header' : row['header'],
                'desc' : row['desc'],
                'time' : row['time'],
                'level' : row['level']
            }
        db[COLLECTION_ID_CATALOG_DESC].insert_one(item)
        print("Course record created")
    print("created eğitimler")
# cosmos dbye eğitim ve denk geldiği içeriği id şeklinde depoluyor
def CreateMatchingTable():
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING )
    db=client[DATABASE_ID]
    df = getMatchingArray()    
    
    # write a code that list first four items of df_embeddings
    print(df.head())
    # write a code that show the number of rows and columns of df_embeddings
    print(df.shape)

    for index, row in df.iterrows():
        # convert index into a string
        i = str(index+1)
        print("index:") 
        print(i)
        item = {'id'     : i,
                'egitimID' : row['EğitimIndex'],
                'icerikID' : row['İçerikIndex']
            }
        db[COLLECTION_ID_MATCHING_TABLE].insert_one(item)
        print("matching element record created")
    print("created matching table")

# silceksen sadece drop metodu
"""
dropAllCollections()
"""
# createliceksen alttaki 5 method
"""
CreateEmbeddingsDatabase()
ExportAndCreateEmbeddings()
CreateEmbeddingsVectorIndex()
CreateEğitimler()
CreateMatchingTable()
"""


