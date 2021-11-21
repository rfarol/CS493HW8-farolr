FROM python:3.9
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8000
ENV GOOGLE_APPLICATION_CREDENTIALS='./cs493hw8-farolr-2e05b45db2f9.json'
EXPOSE ${PORT}
CMD [ "python", "main.py" ]
