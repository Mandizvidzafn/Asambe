FROM python:3.10.4
WORKDIR /asambe-app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
