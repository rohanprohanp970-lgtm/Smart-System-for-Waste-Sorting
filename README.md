#  Smart System for Waste Sorting

An AI-powered waste sorting system that efficiently classifies waste into categories such as **recyclable, compostable, non-recyclable, dry, and wet waste**. This system helps reduce contamination in recycling streams and increases material recovery rates.

---

##  Features

### **Main Page**
- Provides information about waste types, disposal methods, and environmental impact.
- Includes a **login/register** menu at the top right.

### **Authentication**
- **Login**: Redirects users to the waste detection dashboard.
- **Register**: Allows new users to create an account.

### **User Dashboard**
- **Waste Detection by Uploading Images** 
  - Users can upload images of waste to be classified by the AI model.
- **Real-Time Waste Detection** 
  - Live waste classification using the camera.
- **Add Waste Location** 
  - Users can mark waste locations on a map with latitude and longitude.
- **View Location History** 
  - Users can track previously reported waste locations and their statuses.

### **Admin Dashboard**
- **Manage Waste Reports** 
  - View location details, usernames, latitude, and longitude.
  - Change the status of waste reports to **"Completed"**, which updates the user's history.
- **View Waste Locations on a Map** 
  - Interactive map showing all reported waste locations.

---
## **System Architecture**
The Smart Waste Sorting System uses a web-based frontend connected to a Flask backend that handles authentication, application logic, and communication with AI modules and the database. An AI waste detection module powered by TensorFlow, OpenCV, and deep learning models (CNN/YOLO/SSD) classifies waste from uploaded images and live camera input. A MySQL database and map interface store and display user data and waste locations, enabling tracking and management through user and admin dashboards.

![Img2](system%20images/architecture.png)

---

## **Technology Used**
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Machine Learning**: TensorFlow, OpenCV, CNN, YOLO/SSD for object detection
- **Database**: MySQL (for user data and waste location tracking)

---

## **Screenshots**
**Dashboard**
<p align="center">
  <img src="system%20images/dashboard.png" width="45%" />
  <img src="system%20images/userlogin.png" width="45%" />
</p>

**User Dashboard**
![Img1](system%20images/user.png)

**Waste Detection by Uploading Images** 
<p align="center">
  <img src="system%20images/imageupload.png" width="45%" />
  <img src="system%20images/imageupload1.png" width="45%" />
</p>

**Real Time waste detection**
<p align="center">
  <img src="system%20images/real.png" width="30%" />
  <img src="system%20images/real1.png" width="30%" />
  <img src="system%20images/real2.png" width="30%" />
  
</p>
<p align="center">
  <img src="system%20images/real4.png" width="30%" />
  <img src="system%20images/real5.png" width="30%" />
  <img src="system%20images/real6.png" width="30%" />
</p>

**Location History**
![Img2](system%20images/location.png)

**Admin Dashboard**
<p align="center">
  <img src="system%20images/admin.png" width="45%" />
  <img src="system%20images/adminmap.png" width="45%" />
</p>

---

**Note:** 
Due to the large number of files involved, the complete source code is not included in this repository.
