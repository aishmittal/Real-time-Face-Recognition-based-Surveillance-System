# Real-time Face Recognition based Surveillance System

Real-time Face Recognition based Surveillance System uses [MS-FACE](https://azure.microsoft.com/en-in/services/cognitive-services/face/) API for face recognition based identification. It itentifies the unknown persons that are not registered and stores their images in a folder named unknown with current date and time. So it can be used for surviellance for security purposes as we can view all the unknown persons (besides staff) that visited a particular place on given date and time-interval. It consists of two apps register(register.py) and main(main.py) where register app is used to register new users and main.py is used for surveillance.  

### New User Registration
Register application used to register the new user by taking some information about user and storing the information in a database and creating personid using Microsoft Face APIs. After the Face Dataset is generated using Opencv2. this generated face dataset is later uploaded to cloudinary and Microsoft cognitive service face APIs. after uploading dataset to microsoft cognitive service a model is build and trained.


#### Steps for Registeration of a new person
1. Run register.py file using ```python register.py```. It will open pyqt GUI window.
2. Edit the details of users to be registered.
3. Click Verify Data button.
4. Click Create User button if verification is successful. This will create user entry in database and create the new person id in msface api.
5. Go to Generate face dataset tab.
6. Click Start button to start the camera.
7. Take 8 snapshot of face at different angles to train the model.
8. Click Upload Dataset button to upload face images to cloudinary and send their links in msface api calls.
9. Click train model to train the face identification model for given person.
10. Close the register.py window register is now complete.

#### Create User Tab
![register1](/screenshots/register1.png)

#### Generate Face Dataset Tab
![register2](/screenshots/register2.png)


### Surveillance
Surveillance app takes images at a regular time interval defined by *detection_interval* in ms (default value=10000, means 10 seconds). After taking images it extract all faces from the images using ***haarcascade*** classifier in opencv. These face images are then uploaded to cloudinary and the cloudinary link is passed with api request to msface api. Two requests are send for a face identification first to add the face and generate a *face_id* and second to get *person_id* from the *face_id*. The *person_id* is used to get the information of the person from sqlite3 database (users.db). A green rectangle is drawn around the identified persons faces with there name while for unidentified persons a red rectangle is drawn with Unknown as their names. faces of all unknown persons are stored in *Unknowns* folder in the main directory with the current date and time which can be checked later for surveillance.

![main1](/screenshots/main1.png)

 
## Language used

 Python 2.7
 

## Python Packages Required
 1. Opencv 2
 2. PtQt 4
 3. Sqlite3
 4. PIL
 
 
## APIs used
 1. Microsoft Cognitive Services Face APIs (for building face identification model)
 2. Cloudinary APIs (for storing dataset)
 3. YouTube APIs (for getting video information of playlists)

## Project Structure
 

## Database used
 sqlite3
