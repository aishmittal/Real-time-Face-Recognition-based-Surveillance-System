# Real-time Face Recognition based Surveillance System

Real-time Face Recognition based Surveillance System uses [MS-FACE](https://azure.microsoft.com/en-in/services/cognitive-services/face/) API for face recognition based identification. It itentifies the unknown persons that are not registered and stores their images in a folder named unknown with current date and time. So it can be used for surviellance for security purposes as we can view all the unknown persons (besides staff) that visited a particular place on given date and time-interval. It consists of two apps register(register.py) and main(main.py) where register app is used to register new users and main.py is used for surveillance.  

### New User Registration
Register application used to register the new user by taking some information about user and storing the information in a database and creating personid using Microsoft Face APIs. After the Face Dataset is generated using Opencv2. this generated face dataset is later uploaded to cloudinary and Microsoft cognitive service face APIs. after uploading dataset to microsoft cognitive service a model is build and trained.


### Surveillance


 
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
 

 ## Thanks
Feel free to post issues if you find any problem or contact me [Aishwarya Mittal](https://www.facebook.com/aishhmittal)<br>
©[MIT License](https://github.com/aishmittal/SOLAMS/blob/master/LICENSE)
