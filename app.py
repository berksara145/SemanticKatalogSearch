from flask import Flask,jsonify, render_template
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import numpy as np
from numpy.linalg import norm
import openai
import pandas as pd
import string
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from methods.mongoDBSearchRelated import Answer
from methods.mongoDBSearchRelated import getSound

def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print("BASEDIR: app ", BASEDIR)
    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  

loadingEnv()

app = Flask(__name__)

def connectToMongoDB():
    # Send a ping to confirm a successful connection
    try:
        client = MongoClient( os.getenv("URL") ) 
        client.admin.command('ping')
        mydb = client["denemeDB"]
        mycol = mydb["denemeCol"]

        mydict = { "name": "berk", "address": "ev" }

        mycol.insert_one(mydict)
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
def connectTryOpenAI():
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.Model.list()

    response = openai.Completion.create(
                prompt= "hello how are you",
                temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="text-davinci-003"
            )
    text_string = "kırmızı elma"

    # choose an embedding
    model_id = "text-similarity-davinci-001"

    embedding = openai.Embedding.create(input=text_string, model=model_id)['data'][0]['embedding']
    print(embedding)
    print(response)

def testingFilter2(question):
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K" 
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.Completion.create(
                prompt=f"Sen bir eğitim koçusun. Aşağıdaki metini bir eğitim koçu olarak anlayacaksın. Eğitim ve koçluk gerekiyorsa \"cevap : evet\" yaz. Eğitime ve motivasyona ihtiyacı yoksa \"cevap : hayır\" yaz.\nMetin: {question}\ncevap: ",
                temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="text-davinci-003"
            )
    print(response)
    filtering2 = response["choices"][0]["text"].strip()
    
    filtering2 = "  Hayır. "
    translator = str.maketrans("", "", string.punctuation)
    str2 = filtering2.translate(translator)

    print(str2)

def testingFilter(question):
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K" 
    openai.api_key = os.getenv("OPENAI_API_KEY")
   
    response = openai.Completion.create(
                prompt=f"Aşağıda verdiğim cümlenin konusunu spesifik birkaç sözcükle cevapla.\nCümle: {question} \n Konu: ",
                temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="text-davinci-003"
            )
    print(response)
    filtering = response["choices"][0]["text"].strip()
    print(filtering)
    
    
    response = openai.Completion.create(
                prompt=f"Aşağıda verdiğim sözcüler mesleki bir yetenekle alakalı ise \"cevap : evet\" yaz. Alakalı değilse ve saçmaysa \"cevap : hayır\" yaz.\nSözcükler: Sorma\ncevap: ",
                temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="text-davinci-003"
            )
    print(response)
    filtering2 = response["choices"][0]["text"].strip()
    
    filtering2 = "  Hayır. "
    translator = str.maketrans("", "", string.punctuation)
    str2 = filtering2.translate(translator)

    if(str2.strip().lower() == "hayır" ):
        print("yee")
    print(str2.strip().lower())
    print(len(str2.strip().lower()))

def extractCSVtoDF():
    df = pd.read_csv("katalog.csv")

def chatWithGPT4():
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K" 
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.ChatCompletion.create(
                messages = [
                    {'role': 'user', 'content': '''The code below is connected to a flask application that renders this html and also returns an array but the script part doesn\'t work
                     <!doctype html>
<head>
    <title>Enocta Katalog</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='bootstrap/css/bootstrap.min.css') }}">
    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
<html>
   <body>
     <main>
        <div class="px-4 py-3 my-2">
            <img class="d-block mx-auto mb-4" src="{{ url_for('static', filename='images/enocta-logo.svg') }}" alt="Enocta Logo" width="192" height="192"/>
            <!-- <img  src="/docs/5.1/assets/brand/bootstrap-logo.svg" alt="" width="72" height="57"> -->
            <!-- <h1 class="display-8">{{name}}</h1> -->
            <p class="display-8"><b>Sorunuz</b></p>
            <p class="display-8">{{name[0]}}</p>

            <p class="display-8"><b>Enocta AI Cevabı</b></p>
            <p class="display-8">{{name[1]}}</p>

            <p class="display-8"><b>Enocta AI Cevabı ingilizcesi (sesli)  </b></p>
            <p class="display-8">{{name[5]}}</p>

            <audio id="audioPlayer" controls>
              <source src="{{ url }}" type="audio/wav">
              Your browser does not support the audio element.
            </audio> 

            <p class="display-8"><b>Enocta AI'ın Sorunuzla İlgili Enocta Kataloğundan Seçtikleri  </b></p>

            <div id="results"></div>

            <p class="fs-5">
                ---------
            </p>
            <a href="{{ url_for('index') }}" class="btn btn-primary btn-lg px-4 gap-3">Geri dön</a>
          </div>

          <script>
            const array = JSON.parse('{{ name | safe }}');
            const resultDiv = document.getElementById('results');
            array.forEach(item => {
                const newElement = document.createElement('p');
                newElement.textContent = item;
                resultDiv.appendChild(newElement);
            });
        </script>
     </main>  
   </body>
</html>'''}
                ],temperature=0,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                model="gpt-4"
            )
    print(response)

def embeddingCategories():
    print("hello")
    openai.organization = "org-EZyyXoEzlXEW5aYgXath8T1K" 
    openai.api_key = os.getenv("OPENAI_API_KEY")

    df = pd.read_csv("birleşikEmbed.csv")
    array = []
    print("Now embedding")
    for i in range(len(df)):
        embed = openai.Embedding.create(input=df.loc[i, "category"], engine='text-embedding-ada-002')['data'][0]['embedding'] 
        array.append(embed)
        print(embed)
    print("embedding done")
    return array            

def calculateSimScores(question, array):
    similarity_scores = []
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']  # this will be the question's embedding

    for embedding in array:
        similarity_score = cosine_similarity([q_embeddings], [embedding])[0][0]
        similarity_scores.append(similarity_score)
        print("Similarity Score:", similarity_score)
        
    return similarity_scores

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    connectTryOpenAI()
    return render_template("test.html")

@app.route("/test2")
def test2():
    url = getSound()
    print("rendering")
    return render_template("test2.html",url=url)
@app.route("/filter")
def filter():
    testingFilter2("Eğitime ihtiyacım var")
    return render_template("test.html")

@app.route("/context")
def context():
    array = embeddingCategories()
    calculateSimScores("kısa süren bir satış eğitimi istiyorum", array=array)
    print("next")
    calculateSimScores("orta süreli bir satış eğitimi istiyorum", array=array)
    print("next")
    calculateSimScores("uzun süren bir satış eğitimi istiyorum", array=array)
    print("next")
    return render_template("test.html")


@app.route('/question_logs')
def question_logs():
    # Read the CSV file
    csv_data = pd.read_csv('logsForGPT.csv')  # Replace 'your_csv_file.csv' with your actual CSV file path
    # Convert the CSV data to a list of dictionaries
    logs = csv_data.to_dict('records')
    # Render the HTML template with the logs data
    return render_template('questionLog.html', logs=logs)

"""
@app.route('/question_logs')
def question_logs():
    
    return render_template('index.html')
"""

@app.route("/chat")
def chat():
    chatWithGPT4()
    return render_template("test.html")

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')
   if name:
        print('Request for hello page received with name=%s' % name)
        returned = Answer(name)
        
        #found true ise
        if(returned[7]):
            returned.pop()
            return render_template('found.html',name=returned) #, url=getSound(engAnswer)
        else:
            returned.pop()
            return render_template('notFound.html', name=returned) #, url=getSound(engAnswer)
       
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()


