# Insight Edge


## Features

- Describe your website [Fill this]

Language: Python v3.12.1

## Tech stack

1. Backend: FastAPI v0.92.0 FastAPI - Python web framework.
2. Fronted: [Fill this]
3. Containerization: Docker v20.10.23
4. Database: Mongo DB
5. Security:
    - JWT and OAuth2 implementation
    - Hashed passwords in database using passlib v1.7.4

## Getting started: Without Docker

a) Clone repository into your machine

```md
git clone 
cd Insight-Edge
```

b) Backend 

<details>
<summary>On Windows</summary>
1.Creating a virtual environment

```md
python -m venv venv
```

2.Activating it

a) Using CMD

```md
.\venv\Scripts\activate.bat
```

b) Using PowerShell

```md
.\venv\Scripts\Activate.ps1
```

3.Installing dependencies

```md
pip install -r requirements.txt
```

4.(OPTIONAL) Deactivating the virtual environment

```md
deactivate
```

</details>

<details>
<summary>On Linux/Mac</summary>
1. Creating a virtual environment

```md
python3 -m venv venv
```

2.Activating it

```md
source venv/bin/activate
```

3.Installing dependencies

```md
pip install -r requirements.txt
```

4.(OPTIONAL) Deactivating the virtual environment

```md
deactivate
```
</details>

c) Run app

```md
uvicorn app.main:app --reload
```


c) Frontend

1. Downloading node modules in the frontend

```md
npm install
```

2. Start the expo project

```md
npm start
```

d) Create an APK File

1. Install Expo CLI Globally (if not already installed)

```md
npm install -g expo-cli
```

2. Log in to Expo

Ensure you have an Expo account and are logged in.

```md
expo login
```

3. Build the APK

Initiate the build process for an Android APK:

```md
expo build:android
```





