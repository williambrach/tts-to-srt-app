FROM python:3.12

WORKDIR /workspace
ADD requirements.txt app.py .env /workspace/
RUN pip install -r /workspace/requirements.txt
EXPOSE 8888
CMD ["python", "/workspace/app.py"]