import base64
from google.cloud import pubsub_v1
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
import google.auth
import os
# from urllib.parse import urlparse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

publisher = pubsub_v1.PublisherClient()
project_id = os.environ["GCP_PROJECT"]


def store_food_item_db(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    food_item = json.loads(pubsub_message)
    print(food_item["category"])

    cred = credentials.ApplicationDefault()
    try:
        firebase_admin.get_app()
        print('firebase already intialized.')
    except ValueError as e:
        print('firebase not initialized. initialize.')
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection_id="default"
    document_id=str(food_item["food_item_id"])
    if food_item["category"] == "cooked_food":
        collection_id='soup_kitchen'
    elif food_item["category"] == "produce":
        collection_id = 'individuals'
    elif food_item["category"] == "packed_food" or food_item["category"] == "house_supply":
        collection_id = 'food_banks'
    else:
        collection_id = 'default'

    doc_ref = db.collection(collection_id).document(document_id)
    doc_ref.set({
        'food_item_id': food_item["food_item_id"],
        'image': food_item["image"],
        'title': food_item["title"],
        'pickup': food_item["pickup"],
        'description': food_item["description"],
        'category': food_item["category"],
        'location': firestore.GeoPoint(float(food_item["lat"]), float(food_item["long"])),
        'address': food_item["address"],
        'available': food_item["available"],
        'date': food_item["date"],
        'collection_id': collection_id
    })

    print("data uploaded")


