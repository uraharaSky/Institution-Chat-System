# 💬 Institution Chat System  

<p align="left">
  <img src="https://img.shields.io/badge/FLASK-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLALCHEMY-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white"/>
  <img src="https://img.shields.io/badge/JWT-A855F7?style=for-the-badge&logo=jsonwebtokens&logoColor=white"/>
  <img src="https://img.shields.io/badge/BCRYPT-4C1D95?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PYTHON-FACC15?style=for-the-badge&logo=python&logoColor=black"/>
</p>

An institutional communication system built with Flask, enabling secure messaging, group chats, attendance tracking, notices, and polls within an organized academic environment.

---

## 🚀 Live Demo  

👉 **Live Link:**  

---

## 🚀 Features  

### 🔐 Authentication & Security  
- JWT-based authentication for secure API access  
- Password hashing using Bcrypt  
- Role-based user system (faculty / student / admin)  

### 💬 Messaging System  
- One-to-one chat with message status (sent, delivered, read)  
- Chat identification using unique `chat_id`  
- Message timestamps and delivery tracking  

### 👥 Group Chat  
- Create and manage groups  
- Add/remove members  
- Group-based messaging system  

### 📊 Attendance System  
- Faculty can create sessions with unique codes  
- Students can mark attendance  
- Session tracking with timestamps  

### 📢 Notices & Reactions  
- Post notices with title and content  
- Users can react to notices  
- Timestamped announcements  

### 🗳️ Polling System  
- Create polls with multiple options  
- Single or multi-select voting  
- Vote tracking per user  

---

## 🛠️ Tech Stack  

### Backend  
- Flask  
- Flask-SQLAlchemy  
- Flask-JWT-Extended  
- Flask-Bcrypt  

### Database  
- SQLite (can be extended to PostgreSQL/MySQL)  

### Architecture  
- Modular routing using Flask Blueprints  
- RESTful API design  
- Scalable model structure  

---

## 📂 Project Structure  

```bash
/routes
  auth.py
  chats.py
  attendance.py
  notices.py
  polls.py
  admin.py
  groups.py

models.py
extensions.py
app.py
requirement.txt

---

## ⚙️ Installation & Setup 

```bash
git clone https://github.com/uraharaSky/Institution-Chat-System.git
cd Institution-Chat-System
pip install -r requirement.txt
python app.py
