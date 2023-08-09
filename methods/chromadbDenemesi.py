import chromadb
import openai
from chromadb.utils import embedding_functions
import csv
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_ORG_ID = "org-EZyyXoEzlXEW5aYgXath8T1K"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = chromadb.PersistentClient(path=r"C:\Users\berk.sara\Documents\GitHub\azureDeneme\temp")
#client = chromadb.HttpClient(host='20.168.252.4', port=443)
#a = client.get_version()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=OPENAI_API_KEY,
                model_name="text-embedding-ada-002"
            )

collection = client.get_collection(name="col", embedding_function=openai_ef)
#name = "col"
def createCollection(name):
    client.create_collection(name=name,metadata={"hnsw:space": "cosine"} ,embedding_function=openai_ef)

def deleteCollection(name):
    client.delete_collection(name=name)

def addToCollection(csvpath):

    data_list = []
    ids = []
    descs = []

    data = pd.read_csv(csvpath, on_bad_lines='skip', sep=',')
    print(data.head())
    print(data.shape)
    print("read the data \n")
        
    for i,row in data.iterrows():
        ids.append(str(i + 1))
        descs.append(row['ICERIK_ACIKLAMA'])
    
    embeds = pd.read_csv("embeddedİçerik761.csv", on_bad_lines='skip', sep=';')
    for i,row in embeds.iterrows():
        data_list.append(EmbeddingItem(row['embeddedİçerik']))


    print(len(ids))
    print(len(data_list))
    print(len(descs))

    collection.add(
        documents=descs,
        embeddings=data_list,
        ids=ids
    )

def EmbeddingItem(embedding):
    embedding_array = np.array(eval(embedding))
    item = embedding_array.tolist()
    return item

def deleteFromCollection():
    collection.delete(
        ids=["id1", "id2", "id3"]
    )

def addToCollectionDeneme():
    collection.add(
        documents=["yemek yemeyi severim", "yemek istiyorum", "hayat çok güzel", "yemek ne güzel ya"],
        metadatas=[{"c": "3"}, {"c": "3"}, {"c": "2"},{"c": "2"}],
        ids=["1", "2", "3","4"]
    )

def queryChroma(question):

    openai.organization = OPENAI_ORG_ID 
    openai.api_key = OPENAI_API_KEY    

    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    result = collection.query(
        query_embeddings=q_embeddings,
        n_results=10
    )

    print(result['documents'][0])
    return result['ids'][0]


#print(collection.peek()) # returns a list of the first 10 items in the collection
#print(collection.count()) # returns the number of items in the collection

#deleteCollection("deneme")
#createCollection("col")
#collection = client.get_collection(name="col", embedding_function=openai_ef)
#addToCollection("IcerikKatalog761.csv")

#query("ruhani yönümü geliştirmek istiyorum")

#queryChroma("javascript eğitimi")