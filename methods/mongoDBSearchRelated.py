import pymongo
import pandas as pd
import os
import numpy as np
from dotenv import load_dotenv
import openai
from sklearn.metrics.pairwise import cosine_similarity
import json
import requests
from methods.içerikHazirlama import getİçerikDescriptions
from methods.chromadbDenemesi import queryChroma
from methods.extract_Info import get_info
import googletrans.client as c

def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  
    
loadingEnv()

OPENAI_ORG_ID  = "org-EZyyXoEzlXEW5aYgXath8T1K"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
K = 10
DATABASE_ID = "semanticDB"
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
COLLECTION_ID_EMBEDDINGS = "icerikEmbeds"
COLLECTION_ID_LOGS = "logs"
COLLECTION_ID_CATALOG_DESC = "catalogDesc"
COLLECTION_ID_MATCHING_TABLE = "matchingTable"
SOUND_APIKEY = os.getenv("SOUND_APIKEY")

"""def LoadEnvVariables():
    global MONGO_CONNECTION_STRING
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))    
    MONGO_CONNECTION_STRING = os.getenv("AZURE_MONGODB_CONNECTION_STRING")
"""



# verilen metnin ingilizce okunuşunun linkini returnler
def getSound(text):

    url = "https://api.deepzen.io/v1/sessions/"

    payload = json.dumps({
    "sessions": [
        {
        "text": "This is a short text.",
        "voice": "alice"
        },
        {
        "text": "<speak>" + text +" </speak>",
        "voice": "william",
        "ssml": True,
        "emotion": {
            "name": "happy",
            "intensity": "medium"
        }
        }
    ],
    "webhook_url": ""
    })
    headers = {
    'Authorization': 'ApiToken ' + SOUND_APIKEY,
    'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
   
    jso = json.loads(response.text)

    print(jso["data"][1]["session"]["wav_url"])
    return jso["data"][1]["session"]["wav_url"]
#sorular soruyu embedleyip vektör db de aratıp en iyi sonuçların 2 tanesini döndürüyor
def GenerateQuestionEmbeddings(db, question):
    # aşağıdaki ap_key bilgisinin gihub'a gönderilmiyor olması lazım. 
    # ek olarak mongodb connection string gibi bilgilerin de gönderilmiyor olması lazım. 
    print("OpenAI Connection")
    openai.organization = OPENAI_ORG_ID 
    openai.api_key = OPENAI_API_KEY    

    print("Generate Question Embeddings")

    # questionı embedleyip ona uygun K tane içerik döndürüyor
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']
    print(q_embeddings[:2])
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": q_embeddings,
                    "path": "vectorContent",
                    "k": K
                },
                "returnStoredSource": True
            }
        }
    ]
    print("Searching...")
    result = db[COLLECTION_ID_EMBEDDINGS].aggregate(pipeline)
    # Print the result
    print("Search results:")
    print(result)

    #bulunan içeriklerin idsini listeye ekle ve döndür
    list = []
    for document in result:
        print(document['id'])
        list.append(document['id'])

    print("listedeki içerik IDleri")
    print(list)
    return list
# sonuçların similarity scorelarını döndürüyor
def returnSimilarityScores(db, question):

    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": q_embeddings,
                    "path": "vectorContent",
                    "k": K
                },
                "returnStoredSource": True
            }
        }
    ]
    result = db[COLLECTION_ID_EMBEDDINGS].aggregate(pipeline)
    similarity_scores = []
    for document in result:
        document_id = document['id']
        embedding = document['vectorContent']
        similarity_score = cosine_similarity([q_embeddings], [embedding])[0][0]
        similarity_scores.append(similarity_score)
        print("Document ID:", document_id)
        print("Similarity Score:", similarity_score)

    return similarity_scores
# quesitonların logunu tutmak için dbye pushluyor
def QuestionLog(db, question, airesponse, egitimheaderArr, egitimdescArr, içerikDescriptions):
    item = {'question' : question,
            'airesponse' : airesponse,
            'egitimheaderArr' : egitimheaderArr, 
            'egitimdescArr' : egitimdescArr,
            'içerikDescriptions' : içerikDescriptions
            }
    db[COLLECTION_ID_LOGS].insert_one(item)
    print("question log record created")
# questiondan gerekli bilgileri çıkarıp (time level need) uygun eğitimi döner
def Answer(question):
    print("Most related course search")

    # keyleri setle
    openai.organization = OPENAI_ORG_ID 
    openai.api_key = OPENAI_API_KEY

    # questiondaki need time ve level ihtiyaçlarını çıkarır 
    print("Answer generation")
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    db=client[DATABASE_ID] 

    # gpt-4 ile çıkarma kısmı
    output_dict = get_info(
        input=question,
        model="gpt-4",
        temperature=0.0,
        path = r"C:\Users\berk.sara\Documents\GitHub\azureDeneme\.env",
    ) 
    
    need = output_dict["need"].capitalize()
    level = output_dict["level"].capitalize()
    minTime = output_dict["min_time"]
    maxTime = output_dict["max_time"]

    #test için print
    print("need, level, min, max time")
    print(need)
    print(level)
    print(minTime)
    print(maxTime)


    # Daha iyi çalışması için anahtar sözcükleri bulur ve questiondan çıkarılan neede ekler
    response = openai.ChatCompletion.create(
                messages = [
                    {'role': 'user', 'content': f'sana kendisine uygun bir eğitimi arayan bir kişinin yazdığı cümleyi vereceğim. Sen de cümlenin konusunu anlayarak ve kişinin dediklerinden yola çıkarak ihtiyacı olan eğitimi sadece anahtar sözcüklerle kısaca yazıcaksın. sözcükler kısa ve betimleyici olmalı \n Cümle: {need} \n anahtar sözcükler: '}
                ],temperature=0,
                max_tokens=50,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="gpt-3.5-turbo"
            )
    # test için bastırma
    print("anahtar sözcükler") 
    print(response)
    toEmbed = response["choices"][0]["message"]["content"]
    print(toEmbed)
    print()

    # anahtar sözcük ekleme kısmı
    needKeywords = need + " " + toEmbed 
    print(needKeywords)
    print()
    # questionın düzenlenmiş halini embede sokar ve çıkan sonuçların idsini array olarak döndürür
    results = GenerateQuestionEmbeddings(db, needKeywords)

    #chorma kullanıcak olursak diye yoruma aldım
    #chromaResult = queryChroma(needKeywords)

    #içeriklerin desclarını test için yazdırır
    print("içerik descriptionları")
    içerikDescriptions = getİçerikDescriptions(results) #chromaResult
    print(içerikDescriptions)
    print()

    # şimdi içeriklerin ID'lerini eşleşen eğitimlerin ID'sini bulmak için kullanıyoruz. (match table ile)

    found_Egitims = []

    # Perform a separate query for each ID and store the results in the desired order
    for icerik_id in results:
        result = db[COLLECTION_ID_MATCHING_TABLE].find_one({"id": icerik_id})
        found_Egitims.append(result)


    # eğitim ID leri arrayden çıkarmaca
    egitimIDList = []
    index = 0
    for i in found_Egitims:
        egitimIDList.append(str(found_Egitims[index]["egitimID"]))
        index += 1

    print("bulunan eğitim IDleri")
    print(egitimIDList)
    print()

    # eğitim Idlerden eğitimin name, description, time ve level döndür
    found_items = []
    
    for egitimID in egitimIDList:
        result = db[COLLECTION_ID_CATALOG_DESC].find_one({"id": egitimID})
        found_items.append(result)

    print("eğitim özellikleri")
    print(found_items)

    # level time'a göre filtrele
    filtered_items = filter(found_items, minTime=minTime, maxTime=maxTime, level=level) 
    print("filtred eğitimler")  
    print(filtered_items)
    
    # chatgptye göndermek üzere descriptionları concatinate et
    desc =""
    print("Related Courses:")
    print("------------------------------")

    #found booleanı filtre sonucunda buldu mu bulmadı mı için lazım
    found = False
    if filtered_items:
        found = True
        for item in filtered_items:
            desc = desc + item.get("desc")
    else:
        found = False
        filtered_items.append(found_items[0])
        filtered_items.append( findclosestTimeEgitim(found_items, minTime=int(minTime), maxTime=int(maxTime)) )
        filtered_items.append( findclosestLevelEgitim(found_items, level=level) )

        print('filter didn\'t work')

    print("Question Context:")
    print("-----------------------------------")
    print(desc)
    # desc bilgisi openAI'a soru ile birlikte gönderilir.
    
    print("OpenAI Connection")   

    #chatgpt ile güzel bir cevap alıyoruz
    response = openai.Completion.create(
                prompt=f"Soruya aşağıdaki içeriğe göre cevap ver. Eğer sorunun cevabı içerikte yer almıyorsa o zaman \"Sorunuza doğrudan cevap veremiyorum ama size çeşitli eğitim ve okuma başlığı önerebilirim.\" şeklinde cevap ver. \n\nİçerik: {filtered_items[0]['desc']}\n\n---\n\nSoru: {question}\nCevap:",
                temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="text-davinci-003"
            )
    
    # test için
    print(f'{response["usage"]["prompt_tokens"]} input tokens counted by the OpenAI API.')

    #chatgpt response texti al
    airesponse = response["choices"][0]["text"].strip().replace("'","")

    # hallettim array açtım found item kaç tane dönerse (max K) o kadar depoluyo
    egitimheaderArr = []
    egitimdescArr = []
    egitimtimeArr = []
    egitimlevelArr = []

    index = 0
    for i in filtered_items:
        egitimheaderArr.append(filtered_items[index]['header'].replace("'",""))
        egitimdescArr.append(filtered_items[index]['desc'].replace("'",""))
        egitimtimeArr.append(filtered_items[index]['time'])
        egitimlevelArr.append(filtered_items[index]['level'])
        index += 1

    
    #similarity_scores = returnSimilarityScores(db,question)
    engAnswer = translateApi(question)
    result = [question.replace("'",""), airesponse.replace("'","").replace('"',''), egitimheaderArr, egitimdescArr, egitimtimeArr, egitimlevelArr, engAnswer.replace("'",""), found]

    # sorulan soruları kaydetmek için loga yolla
    QuestionLog(db, question, airesponse, egitimheaderArr, egitimdescArr, içerikDescriptions)

    return result

def filter(lst, minTime, maxTime, level):

    if(minTime == "-"):
        minTime = 0
    else:
        minTime = int(minTime)

    if(maxTime == "-" or maxTime == "inf"):
        maxTime = float('inf')
    else:
        maxTime = int(maxTime)

    if(level == "-"):
        level = None
    
    filtered_arr = []
    for document in lst:
        if document not in filtered_arr:
            if document['time'] > minTime and document['time'] < maxTime:
                if(level == None):               
                    filtered_arr.append(document)
                else:
                    if(document['level'] == level):
                        filtered_arr.append(document)

    return filtered_arr

def findclosestLevelEgitim(found_items, level):
    levelItem = []
    index = 0
    while(len(levelItem) == 0 and index < len(found_items)):
        if(found_items[index]["level"] == level):
            levelItem.append(found_items[index])
        index += 1
    
    if(len(levelItem) == 0):    
        return "not found"
    else:
        return levelItem[0]

def findclosestTimeEgitim(found_items, minTime, maxTime):
    closestItem = None
    min_difference = float('inf')
    
    for item in found_items:
        itemTime = int(item["time"])

        if minTime > itemTime: 
            difference = minTime - itemTime

        if maxTime < itemTime: 
            difference = itemTime - maxTime

        if difference < min_difference:
            min_difference = difference
            closestItem = item

    return closestItem

def translateApi(text):
    a = c.Translator()
    response = a.translate(text, dest="en")
    print(response.text)
    return response.text

def find_closest_video_duration(video_durations, min_interval, max_interval):
    closest_video = None
    min_difference = float('inf')

    for duration in video_durations:
        
        if min_interval <= duration <= max_interval:

            difference = abs(duration - (min_interval + max_interval) / 2)

            if difference < min_difference:
                min_difference = difference
                closest_video = duration

    return closest_video