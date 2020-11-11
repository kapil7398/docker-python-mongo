FROM python:latest

WORKDIR /user/src/app
COPY requirements.txt .

RUN pip install -r requirements.txt 

COPY . .

ENTRYPOINT [ "python", "app.py" ] 
