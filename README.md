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





