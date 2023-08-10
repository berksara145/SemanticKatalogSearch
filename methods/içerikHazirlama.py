import pandas as pd
import numpy as np
from dotenv import load_dotenv
import openai
import os

def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print("BASEDIR: içerik", BASEDIR)
    BASEDIR = os.path.dirname(BASEDIR)
    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  

loadingEnv()


"""
Will convert the embedding string to a list
open mongo db cosmos with azure script
method to upload the vectors
vector search
a system to convert the incoming vector result id from içerik to id via tables (arrays)
testing using 12 eğitim with 300 içerik (galiba) and determining if it works good
google translate integration with api 
"""

# içerik ve ait olduğu eğitimler ve açıklamalarla dolu büyük tablo
def readCSV():
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    data = pd.read_csv(os.path.join( os.path.dirname(BASEDIR) , 'IcerikKatalog761.csv'),  sep=',')
    print(data.head())
    print(data.shape)
    print("read the data \n")
    return data
#içerik açıklamalarını çıkarıyor
def getİçerikArray():
    içerikArr = data['ICERIK_ACIKLAMA'].values
    print(içerikArr[59])
    print("got the İçerikArray \n")
    return içerikArr 
# eğitim isimleri arrayi. Katalogdaki içerik tablosundan çıkarıyor
def getEğitimArray():
    eğitimArr = []
    # Iterate through the specific column
    for index, row in data.iterrows():
        column_value = row['ETKINLIK_ADI']  
        if(data.iloc[index - 1, 0] != column_value):
            eğitimArr.append(column_value)

    print("got the eğitimArray")
    print(len(eğitimArr))
    return eğitimArr
# eğitim ve denk geldiği içerikleri bulmak için eğitim ve içerik idleri eşleştiren tablo
def getMatchingArray():
    df = pd.DataFrame(index=np.arange(data.shape[0]), columns=np.arange(2))
    df.columns = ["EğitimIndex","İçerikIndex"]

    indexTitle = 1 
    for index, row in data.iterrows():
        df.iat[index, 0] =  indexTitle
        df.iat[index, 1] =  index + 1
        if(index != data.shape[0] - 1 and data.iloc[index + 1, 0] != data.iloc[index , 0]):
            indexTitle += 1

    print(df)
    print("Done matching array")
    return df
# sakın çalışıtırma içerik açıklamayı embedliyor
def embeddingİçerik(data):
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    embeddedArr = []
    model_id = "text-embedding-ada-002"

   
    for i in range(10):
        embedding = openai.Embedding.create(input=data[i], model=model_id)['data'][0]['embedding']
        print("embeded" + str(i))
        embeddedArr.append(arrToString(embedding))
    
    """
    sayi = 1
    for i in data:
        embedding = openai.Embedding.create(input=i, model=model_id)['data'][0]['embedding']
        print("embeded " + str(sayi) + "\n")
        print(i)
        embeddedArr.append(arrToString(embedding))
        sayi += 1
    """

    df = pd.DataFrame(embeddedArr)
    df.columns = ["embeddedİçerik"]
    
    print(df.shape)
    df.to_csv('e.csv', index=False)
    print("embedded içerik açıklamaları")
# arrayi string içine koyuyor csv depolamak için
def arrToString(arr):
    string = '['

    for i in arr:
        string += str(i)
        string += ","

    string = string[:-1]

    string += ']'
    return string 
# input olan ID hangi içeriğe denk geliyorsa açıklamasını döndürür
def getİçerikDescriptions(idArray):
    içerikArr = data['ICERIK_ACIKLAMA']
    matchingİçerikArr = []
    for i in idArray:
        matchingİçerikArr.append(içerikArr[int(i) - 1])
    return matchingİçerikArr

data = readCSV()