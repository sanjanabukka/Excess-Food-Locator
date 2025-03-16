from flask import Flask, render_template, request, url_for, jsonify, redirect
from flask_bootstrap import Bootstrap
import os
from google.cloud import storage, pubsub_v1
import io
from io import BytesIO
import pandas
from flask_googlemaps import GoogleMaps
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
from os.path import join, dirname, realpath


app = Flask(__name__)
Bootstrap(app)


app.config['GOOGLEMAPS_KEY'] = "YOURKEY"
# upload_food_detail_topic = "upload-food-item"
project_id = "cloud-map-reduce"

GoogleMaps(app, key="YOURKEY",
           style="height:100%;width:100%;margin:0;")

publisher = pubsub_v1.PublisherClient()
futures = []


@app.route('/getfood')
def get_food():
    print("get food invoked")
    return render_template('getfood.html', title='getfood')


@app.route('/showmap', methods=["POST"])
def showmap():
    data = request.get_json()
    print("get food data", data)
    return render_template('getfood.html', title='getfood')


@app.route('/donatefood', methods=['GET'])
def donate_food():

    return render_template('donatefood.html', title='donatefood')


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', title='home')


#app.config["IMAGE_UPLOAD_LOC"] = "..\\..\\static\\uploads"

app.config["IMAGE_UPLOAD_LOC"] = "/tmp"
# basedir = os.path.abspath(os.path.dirname(__file__))


@app.route("/upload-image", methods=["POST"])
def upload_image():

    if request.method == "POST":

        if request.files:
            image = request.files["image"]

            image.save(os.path.join(
                app.config["IMAGE_UPLOAD_LOC"], image.filename))
            print("uploaded in flask")

            client = storage.Client(project='cloud-map-reduce')
            bucket = client.bucket('upload-food-bucket')
            filename = "%s" % (image.filename)
            blob = bucket.blob(filename)
            description = filename.split('.')[0]
            print("DESCRIPTION IS", description)
            metadata = {'filename': filename, 'lat': request.form["latval"], 'description': description,
                        'long': request.form["lngval"], 'pickuptime': request.form["time"], 'address': request.form["address"], 'available': True, 'date': request.form["date-picker"]}
            blob.metadata = metadata
            # blob.upload_from_filename(
            #     "..\\..\\static\\uploads\\"+image.filename)
            blob.upload_from_filename(
                "/tmp/"+image.filename)
            blob.make_public()

            print("Image saved")
            print("location", request.form["latval"])
            print("location", request.form["lngval"])
            print("ADDRESS", request.form["address"])
            print("details published")

    return "Item submitted"


@app.route("/   ", methods=["POST"])
def get_food_listings():

    if request.method == "POST":
        if request.form["business-type"] == "Soup Kitchen":
            business_type = "soup_kitchen"
        elif request.form["business-type"] == "Food bank":
            business_type = "food_banks"
        else:
            business_type = "individuals"

        cred = credentials.ApplicationDefault()
        try:
            firebase_admin.get_app()
            print('firebase already intialized.')
        except ValueError as e:
            print('firebase not initialized. initialize.')
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        doc_ref = db.collection(business_type)

        north_point = firestore.GeoPoint(
            float(request.form["latval"])+5, float(request.form["lngval"])+5)
        south_point = firestore.GeoPoint(
            float(request.form["latval"])-5, float(request.form["lngval"])-5)

        docs = doc_ref.where(
            'location', '<=', north_point).where('location', '>=', south_point).where('available', '==', "True").stream()

        results = {}
        for doc in docs:
            print('{}=>{}'.format(doc.id, doc.to_dict()))
            docdata = doc.to_dict()
            results[str(doc.id)] = dict()
            for key, val in docdata.items():

                if isinstance(docdata[key], firebase_admin.firestore.GeoPoint):
                    results[str(doc.id)
                            ]["latitude"] = docdata["location"].latitude
                    results[str(doc.id)
                            ]["longitude"] = docdata["location"].longitude
                else:
                    results[str(doc.id)][key] = docdata[key]

        if results:
            print("sending results")
            print(results)
            return jsonify({'success': results})
        else:
            print("sending error")
            return jsonify({'error': "No food items found"})


@app.route("/book-food", methods=["POST"])
def book_food():
    try:
        if request.method == "POST":
            cred = credentials.ApplicationDefault()
            try:
                firebase_admin.get_app()
                print('firebase already intialized.')
            except ValueError as e:
                print('firebase not initialized. initialize.')
                firebase_admin.initialize_app(cred)

            db = firestore.client()
            doc_ref = db.collection(request.form["collection_id"])

            doc_ref.document(request.form["itemId"]).update({
                "available": "False"
            })

            print("sending results")
            return jsonify({'success': "updated"})
    except Exception as e:
        print(e)
        return jsonify({'error': "Error while confirming pickup of item"})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
