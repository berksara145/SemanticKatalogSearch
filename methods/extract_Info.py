import os
import json
import openai
from dotenv import load_dotenv

def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    print("BASEDIR: info", BASEDIR)
    BASEDIR = os.path.dirname(BASEDIR)
    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  

loadingEnv()

def get_info(
        input: str,
        path: str=None,
        model: str="gpt-4",
        temperature: float=0.0
    ) -> dict:

    openai.api_key = os.getenv('OPENAI_API_KEY')
    prompt = get_prompt(input)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"user", "content":prompt}],
        temperature=temperature
    )

    response = response.get("choices")[0]["message"]["content"]
    response_dict = json.loads(response)
    return response_dict

def get_prompt(input: str) -> str:
    prompt = f"""
    Eğitim videoları satan bir şirket düşün, bu videolardan 
    yararlanmak isteyen bir müşteriye neye ihtiyacı olduğu soruluyor. 
    Senden istediğimiz ise müşterinin verdiği 
    bu cevaptan bize bazı önemli bilgileri çıkarman.

    Müşterinin cevabı: {input}

    Şu bilgileri çıkar: 

    Müşterinin ihtiyacı: Müşterinin cevabından neye ihtiyacı 
    olduğunu onun ağzından aktaran bir cümle kur. Örneğin, 
    müşteri 'Son zamanlarda oldukça stresliyim.' diyorsa, 
    'Stres yönetimi ile ilgili eğitimlere ihtiyacım var.' yaz. 
    Eğer müşteri verdiği cevapta ihtiyacını veya sorununu 
    belirtmemişse, '-' yaz.

    Minimum eğitim süresi: Eğitim videosunun dakika olarak en az ne kadar süre 
    uzunlukta olması gerektiğini yaz. Örneğin '1-2 saatlik 
    videolar istiyorum.' dediyse '60' yaz. Müşteri alt sınır belirtmemişse 
    '0' yaz. Sayısal bir süre değeri bulamazsan da cümlenin anlamından yaklaşık bir süre çıkar. Eğer eğitim süresine dair bir 
    bilgi verilmediyse, '-' yaz. Mesela 'Videoların ne kadar 
    sürdüğü önemli değil.' dediyse '-' yaz. Müşteri eğitim süresi için 
    spesifik bir süre belirttiyse, o süreyi yaz. Örneğin '50 dakikalık eğitimler istiyorum.' 
    dediyse, '50' yaz. 

    Maksimum eğitim süresi: Eğitim videosunun dakika olarak en çok ne kadar süre 
    uzunlukta olması gerektiğini yaz. Örneğin müşteri '1-2 saatlik 
    videolar istiyorum.' dediyse '120' yaz. Örneğin 'En çok 3 saatlik 
    videolar istiyorum.' dediyse '180' yaz. Müşteri eğitim süresi için 
    spesifik bir süre belirttiyse, o süreyi yaz. Örneğin '50 dakikalık eğitimler istiyorum.' 
    dediyse, '50' yaz. Eğer müşterinin cümlesinde bir olayı ne kadar sürede yaptığını belirten bir ifade varsa bunu sayısal değere çevir. 
    Örneğin: 'bir basket maçı süresi kadar eğitim ver' dediyse üst limiti 90 yap
    Eğer eğitim süresine dair bir bilgi verilmediyse, '-' yaz.

    Eğitim seviyesi: Eğitim videosunun hangi seviyede olması gerektiğini yaz. 
    3 seviye var: Başlangıç, Orta ve İleri. Örneğin müşteri 'İleri seviyede eğitimler 
    istiyorum.' dediyse 'İleri' yaz. Örneğin müşteri 'Basit eğitimler istiyorum.' 
    dediyse 'Başlangıç' yaz. Eğer müşteri cevabında eğitim seviyesinden bahsetmiyorsa 
    '-' yaz.

    Çıkardığın bilgileri JSON olarak şu 'key'lerle formatla:
    need
    min_time
    max_time
    level

    Lütfen sadece JSON formatında oluşturduğun data'yı yaz.
    """

    return prompt