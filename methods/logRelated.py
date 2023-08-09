import os
import pandas as pd
import pymongo
from dotenv import load_dotenv
import pandas as pd

"""
insanların sordukları soruların ve cevapların listesini bir csv dosyasına kaydeder.
"""

def loadingEnv():
    # Get the path to the directory this file is in
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Connect the path with your '.env' file name
    load_dotenv(os.path.join(BASEDIR, 'configvars.env'))  
    
loadingEnv()

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DATABASE_ID = "semanticDB"
COLLECTION_ID_LOGS = "logs"

def export_logs_to_csv():
    # Connect to MongoDB
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    db = client[DATABASE_ID]
    collection = db[COLLECTION_ID_LOGS]
    # Retrieve all documents from the collection
    documents = list(collection.find())

    # Create a DataFrame from the documents
    df = pd.DataFrame(documents)

    # Load existing IDs from the CSV file to a set
    existing_ids = set()
    csv_path = os.path.join(BASEDIR, 'logsForGPT.csv')
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        existing_ids = set(existing_df['_id'].apply(str))  # Convert ObjectIDs to strings

    # Filter new documents that are not in the existing set of IDs
    new_documents = [doc for doc in documents if str(doc['_id']) not in existing_ids]  # Convert ObjectID to string for comparison
    # Create a DataFrame from new documents
    new_df = pd.DataFrame(new_documents)

    if not new_df.empty:
        # Append the new DataFrame to the CSV file in append mode (mode='a')
        # without writing headers (header=False)
        new_df.to_csv(csv_path, index=False, mode='a', header=not os.path.exists(csv_path))

    print("Logs exported to logsForGPT.csv successfully!")

# Call the function to export logs to CSV
LoadEnvVariables()
export_logs_to_csv()