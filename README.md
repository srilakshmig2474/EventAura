# 🎉 EventAura — Event Management & Certificate Generation Platform

**Celebrate Every Moment. Certify Every Achievement.**

EventAura is a web-based event management platform developed using Python Flask and PostgreSQL. It helps organizers manage events, track participant attendance using QR codes, generate certificates, and deliver certificates through email.

The project was developed to simplify event administration and reduce the manual effort involved in attendance tracking and certificate distribution.

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Application Screenshots](#-application-screenshots)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [How It Works](#-how-it-works)
- [Current Status](#-current-status)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

## 📖 Overview

Managing events manually can be time-consuming, especially when organizers need to handle registrations, record attendance, and prepare participation certificates.

EventAura provides a centralized application for these tasks. It combines event management, QR-based attendance, certificate generation, and email delivery in one workflow.

## ✨ Features

- **Event Management:** Create, view, and manage events.
- **Participant Registration:** Collect participant information for events.
- **QR-Based Attendance:** Support attendance tracking using QR codes.
- **Certificate Generation:** Generate certificates for participants.
- **Certificate Preview:** Preview certificates before delivery.
- **Email Delivery:** Send generated certificates to participants through email.
- **Database Integration:** Store and manage application data using PostgreSQL.
- **User Interface:** Provide a web interface using HTML, CSS, and JavaScript.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application programming |
| Flask | Backend web framework |
| PostgreSQL | Relational database |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactions |
| QR Code | Attendance tracking |
| Git and GitHub | Version control and source code management |

## 📸 Application Screenshots

The following screenshots can be added to showcase the application interface and its features.

> Create a folder named `screenshots` in the project root and save your actual application screenshots there using the filenames below.

### 1. Home Page

![EventAura Home Page](screenshots/home.png)

### 2. Login Page

![EventAura Login Page](screenshots/login.png)

### 3. Dashboard

![EventAura Dashboard](screenshots/dashboard.png)

### 4. Event Details

![EventAura Event Details](screenshots/event-details.png)

### 5. QR-Based Attendance

![EventAura QR Attendance](screenshots/qr-attendance.png)

### 6. Certificate Preview

![EventAura Certificate Preview](screenshots/certificate-preview.png)

*Replace these example screenshot references with screenshots of the corresponding features in your working application.*

## 📂 Project Structure

```text
EventAura/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── event_details.js
│   └── qr_codes/
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── register.html
│   ├── dashboard.html
│   ├── event_details.html
│   ├── edit_event.html
│   ├── attendance_result.html
│   ├── certificate_preview.html
│   ├── registration_success.html
│   └── upload_template.html
└── screenshots/
```

*This structure summarizes the main files in the project. Some generated folders may be created when the application runs.*

## 🚀 Getting Started

### Prerequisites

Install the following tools before running EventAura:

- Python 3
- PostgreSQL
- Git
- A code editor such as Visual Studio Code

### 1. Clone the repository

```bash
git clone https://github.com/srilakshmig2474/EventAura.git
cd EventAura
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the database connection and any other settings required by `app.py`.

For example, if your application uses these variable names:

```env
DATABASE_URL=your_database_connection_string
SECRET_KEY=your_application_secret
```

Use the exact variable names expected by your code. Configure email credentials only if required by your implementation.

**Security:** Never commit `.env` to GitHub. Do not place real passwords, API keys, or email credentials in this README.

### 5. Set up PostgreSQL

Create a PostgreSQL database and configure the connection according to your application's database settings.

Ensure the required tables and schema are created before starting the application. Use the database initialization procedure implemented in your project.

### 6. Run the application

```bash
python app.py
```

Open the local URL shown in the terminal, commonly:

`http://127.0.0.1:5000`

The exact address and port depend on your Flask configuration.

## 🔄 How EventAura Works

EventAura follows a step-by-step workflow that connects event management, participant registration, QR-based attendance, certificate generation, and email delivery.

### 📌 Complete Workflow

```text
              ┌──────────────────────┐
              │   Organizer Login    │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   Create an Event    │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Participant Register │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ QR-Based Attendance │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Record Attendance   │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Generate Certificate│
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Preview Certificate │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Email the Certificate│
              └──────────────────────┘
```

### 1. 🔐 Organizer Login

The organizer logs in to the EventAura application through the login page. After successful authentication, the organizer can access the dashboard and available event-management features.

### 2. 📅 Event Creation and Management

The organizer creates an event by entering the required event details. EventAura allows the organizer to view and manage events through the dashboard.

Event information is stored in the PostgreSQL database according to the application's database configuration.

### 3. 📝 Participant Registration

Participants register for an available event by providing the requested information, such as their name and email address.

The application processes the registration and stores the relevant participant and event information in the database.

### 4. 📱 QR-Based Attendance

EventAura supports QR-based attendance tracking. The QR code is used as part of the attendance workflow to identify or process the relevant event or participant.

The backend processes the attendance action and records the result according to the application's implementation.

### 5. 🗄️ Attendance Recording

The application maintains attendance information in the database. This information can be used to determine which participants have attended an event and are eligible for certificates, depending on the application's configured rules.

### 6. 🎓 Certificate Generation

The application generates a certificate using the available participant and event information. This reduces the need to prepare every certificate manually.

### 7. 👁️ Certificate Preview

Before delivery, the generated certificate can be previewed through the certificate preview interface. This helps the organizer check the certificate details.

### 8. 📧 Email Delivery

EventAura supports sending generated certificates to participants through email. The email functionality depends on the configured email service and valid credentials.

### 9. 🔗 Technologies Working Together

| Component | Responsibility |
|---|---|
| HTML, CSS, JavaScript | Provides the user interface and frontend interactions |
| Python Flask | Handles application routes and backend processing |
| PostgreSQL | Stores event, registration, and attendance data |
| QR Code functionality | Supports the attendance workflow |
| Certificate-generation logic | Produces participant certificates |
| Email service | Delivers generated certificates to recipients |

### ✅ Expected Outcome

EventAura brings several event-related activities together in one application. It helps organizers manage events, process participant registrations, track attendance, generate certificates, and deliver certificates electronically.

The application currently runs locally, and its source code is available on GitHub.

## 📍 Current Status

- Application developed using Flask.
- Main features tested locally.
- Source code maintained on GitHub.
- Cloud deployment has not been completed.

## 🔮 Future Enhancements

- Deploy the application to a cloud hosting platform.
- Improve certificate design customization.
- Add event analytics and attendance reports.
- Improve email delivery reliability.
- Enhance mobile responsiveness and accessibility.
- Add automated tests and deployment workflows.

## 👩‍💻 Author

**EventAura Project**

GitHub Repository: [srilakshmig2474/EventAura](https://github.com/srilakshmig2474/EventAura)

---

*EventAura — Celebrate Every Moment. Certify Every Achievement.*
