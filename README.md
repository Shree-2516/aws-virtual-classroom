# AWS Hosted Virtual Classroom and Learning Platform

A cloud-based Virtual Classroom and Learning Platform developed using Flask, MySQL, and AWS services including EC2, RDS, and S3. This project allows students to register, log in, access course materials, and download learning resources online.

---
## Live Project : http://54.162.83.214/
## Youtube Demo : https://youtu.be/vifi_VLign8

# Project Overview

This project is designed to create a scalable and secure online learning platform hosted on AWS Cloud.

The platform provides:

* Student Registration and Login
* Secure Password Authentication
* Course Material Management
* PDF/Notes Access
* File Storage using AWS S3
* Database Management using AWS RDS MySQL
* Cloud Hosting using AWS EC2

---

# Technologies Used

## Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript

## Backend

* Python
* Flask

## Database

* MySQL
* AWS RDS MySQL

## Cloud Services

* AWS EC2
* AWS S3
* AWS RDS

## Deployment Tools

* GitHub
* Gunicorn
* Nginx

---

# Project Architecture

```text
User Browser
     ↓
Flask Application (EC2)
     ↓
AWS RDS MySQL Database
     ↓
AWS S3 Bucket Storage
```

---

# Main Features

## Student Features

* Register account
* Login securely
* View dashboard
* Access course materials
* Download PDFs and Notes
* Logout

## Admin Features

* Upload course materials
* Manage learning resources
* Store files in AWS S3
* Update course content

---

# Folder Structure

```text
aws_virtual_classroom/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── database/
│   ├── db_connection.py
│   ├── init_db.py
│   ├── schema.sql
│   └── __pycache__/
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   └── js/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── upload.html
│
├── uploads/
│
├── snapshots/
│
├── virtual-classroom.pem
│
└── venv/
```

---

# Local Setup Guide

## Step 1: Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK

cd aws_virtual_classroom
```

---

## Step 2: Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux/Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure Environment Variables

Create `.env` file:

```env
SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=virtual_classroom

AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=ap-south-1
```

---

## Step 5: Setup MySQL Database

Open MySQL Workbench and run:

```sql
CREATE DATABASE virtual_classroom;
```

### Create Users Table

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(255),
    role VARCHAR(20)
);
```

### Create Courses Table

```sql
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255),
    file_url TEXT,
    uploaded_by VARCHAR(100)
);
```

---

## Step 6: Run Flask Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

# AWS Deployment Guide

# AWS Services Used

| AWS Service | Purpose                |
| ----------- | ---------------------- |
| EC2         | Host Flask Application |
| RDS         | Store User Database    |
| S3          | Store Course Materials |

---

## Step 1: Create AWS Account

Go to:

```text
https://aws.amazon.com/
```

Create AWS account and login to AWS Console.

---

## Step 2: Create S3 Bucket

### Steps

1. Open AWS S3 Console
2. Create Bucket
3. Give unique bucket name
4. Upload PDFs and Notes
5. Configure bucket permissions

### Example Bucket Name

```text
aws-virtual-classroom-storage
```

---

## Step 3: Create RDS MySQL Database

### Steps

1. Open AWS RDS Console
2. Create Database
3. Select MySQL
4. Choose Free Tier
5. Set username and password
6. Enable public access for testing
7. Configure security groups

### Database Name

```text
virtual_classroom
```

---

## Step 4: Create EC2 Instance

### Steps

1. Open EC2 Console
2. Launch Ubuntu Instance
3. Select t2.micro
4. Configure security group

### Allow Ports

| Port | Purpose |
| ---- | ------- |
| 22   | SSH     |
| 80   | HTTP    |
| 443  | HTTPS   |

5. Download PEM key file

---

## Step 5: Connect EC2 using SSH

```bash
ssh -i virtual-classroom.pem ubuntu@YOUR_PUBLIC_IP
```

---

## Step 6: Install Required Packages on EC2

```bash
sudo apt update -y

sudo apt install python3-pip -y

sudo apt install nginx -y

pip3 install virtualenv
```

---

## Step 7: Clone GitHub Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK

cd aws_virtual_classroom
```

---

## Step 8: Create Virtual Environment on EC2

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Step 9: Install Requirements

```bash
pip install -r requirements.txt
```

---

## Step 10: Run Flask Application

```bash
python3 app.py
```

---

## Step 11: Configure Gunicorn

### Install Gunicorn

```bash
pip install gunicorn
```

### Run Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

---

## Step 12: Configure Nginx

### Edit Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/flaskapp
```

### Add Configuration

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

### Enable Configuration

```bash
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled
```

### Restart Nginx

```bash
sudo systemctl restart nginx
```

---

# Application Workflow

## Student Workflow

1. Student registers account
2. Password is hashed securely
3. User data stored in RDS
4. Student logs in
5. Dashboard loads course materials
6. PDFs fetched from S3
7. Student downloads resources

---

## Admin Workflow

1. Admin logs in
2. Uploads new course materials
3. Files stored in AWS S3
4. Database updated automatically
5. Students access latest materials

---

# Test Scenarios

## Scenario 1

* Register new student
* Login successfully
* Access dashboard

## Scenario 2

* Upload new course material
* Verify S3 upload
* Verify dashboard update

## Scenario 3

* Download PDF from dashboard
* Verify successful download

---

# Security Features

* Password Hashing
* Session Management
* Secure Database Connection
* AWS IAM Access Control
* Environment Variables Protection

---

# Future Improvements

* Video Lectures
* Live Classroom Integration
* Assignment Upload
* Attendance Tracking
* Admin Analytics Dashboard
* Email Notifications

---


# GitHub Commands

## Initialize Git

```bash
git init
```

## Add Files

```bash
git add .
```

## Commit Files

```bash
git commit -m "Initial Commit"
```

## Connect GitHub Repository

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_LINK
```

## Push Code

```bash
git push -u origin main
```

---

# Requirements

Example `requirements.txt`

```text
Flask
mysql-connector-python
boto3
python-dotenv
gunicorn
Werkzeug
```

---

# Author

## Shreeyash Paraj

Cloud Practitioner Project
AWS Hosted Virtual Classroom and Learning Platform

---

# Conclusion

This project demonstrates how AWS cloud services can be integrated with Flask and MySQL to create a scalable online learning platform. The system provides secure authentication, cloud-based file storage, and reliable deployment architecture using AWS infrastructure.
