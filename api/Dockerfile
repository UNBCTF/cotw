FROM python:3.12
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
