
### Problem statement and Use case: 
This is an application for donating and finding extra/surplus/unused food. The application allows users to upload photos of food items
and to search food items based on their location. The app aims to reduce food wastage
by sharing unused/excess food with those in need. The application is inspired from apps
like Olio and Karma. The app uses Cloud vision API to classify the images uploaded by
users into 4 categories.
 * The cooked food dishes like pizza, spaghetti , fresh baked bread etc go to soup
kitchens, where it can feed the poor and the hungry. Hotels and restaurants can
donate such extra meal portions to soup kitchens.
* Fresh vegetables and oranges can be shared by individuals with other
individuals. This sort of perishable food can be shared within households in the
same locality. (Idea taken from Olio app)
* Generally food banks accept packaged goods like peanut butter, flour etc. I
have also added a category for household supplies. These supplies include toilet
paper, Tide etc.
* All other items that don't fit into any category are stored in the defaults category.


### Design Details:
* User interface: I have used Flask app along with general HTML and CSS for the front
end of the app. The flask app has various end points in the app.py file. The user
interface is contained in the src/templates folder. This folder has following files:
  * Donatefood.html: This file has the form to let users upload images, add location
details and pick up times for the item.
  * Getfood.html : This file has a form to take information like business type and
location and displays the food items nearest to the user specified location.
  * While uploading the image, I upload the image to a folder in the container and
then push that image to cloud storage from the flask code. I set various attributes
like pick up time, location etc as metadata to the file while uploading.
* Flask app endpoints: The flask app has various endpoints that connect UI to the
Firestore and google cloud storage. The end points and their function are as follows:
   * / and /home: This loads the home page
   * /getfood: This loads the ‘getfood’ html page
   * /donatefood: This loads the ‘donatefood’ html page
   * /upload-image: This is called when the form on ‘donatefood’ html page is
submitted. This method receives the file to be uploaded and other file data like
location, pickup time etc. This file is then uploaded to a GCS bucket called
‘upload-food-bucket’.
  * /get-food-listings: This is called when the user fills business type and location
information on the get food page and submits the form. This method gets data
from firestore that has an available flag set to true and is around the location
entered by the user and populates on the page.
  * /book-food: This endpoint is invoked when a user selects the food listings
populated on the get food page for pick up.
* Cloud functions: I have used two types of cloud functions. One is storage triggered and
the other one is pubsub triggered.
  * Storage triggered: The storage triggered cloud function gets the images
uploaded by the user and calls the Cloud Vision API to classify the image. The
function gives the image to cloud vision API and gets the labels and scores.
These scores and labels are used to classify images in a category. A message is
created and this category along with other metadata like pick up time and
location etc. This message is pushed to pubsub.
  * PubSub triggered: The pubsub triggered cloud function is invoked when the
above message is pushed to cloud pubsub. This function listens to the
store-food-item topic. The message is received in the cloud function, the category
is examined and the item is put in appropriate collection. (Refer store-food-item
cloud function for logic). The items with category ‘household’ and ‘packed_food’
are added to food_banks collection, the items with ‘produce’ category are added
to individuals collections. The items with the ‘cooked_food’ category are added to
the soup_kitchen collection. Please refer the comment in cloud function code for
more details.
  * Firestore: The images are categorized into 4 collections namely default, soup_kitchen,
individuals and food_banks.


### Cloud APIs used:
* Cloud Functions: For getting image from bucket and calling vision API and storing 
* Cloud Storage: to store image uploaded by user
* Firebase Firestore: Database to store documents 
* Cloud Run: To run containerized flask app and serve endpoints for backend
* Cloud Pubsub: to decouple the architecture of functions.
* Cloud Vision API: To classify images
* Cloud Build: To create image from flask app and upload to Google cloud container registry
* Cloud container registry 
* Google Map API, Geocoding API, Places: To get location of the user and display on map. Geocoding API used to reverse the geocode location of the user getting the food and find nearest food items.


### Weaknesses and Improvements:
* The system relies on Cloud VisionAPI to classify images uploaded, the classification labels might determine the correctness of the application logic. I have only tested the application for the sample images included in the submission folder. To build a robust system, we can create a custom model to train and classify food images specifically for the purpose of this project. Since this project is for the Cloud computing class, I haven't created a custom model and directly used the classification labels by Cloud Vision API. The correctness of this application logic is restricted to the images provided. 
* The endpoints exposed via cloud run are unauthenticated. Ideally authentication of the user can be performed via login feature for additional security. Another option is to use the API Gateway offerings by Google to secure the endpoints.
* I have used the public url of the GCS object to display images in the frontend. This can be a security issue for some apps with critical data.
