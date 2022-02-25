FROM python:3
ENV TZ="Europe/Warsaw"

RUN mkdir -p /homie-web-ui
RUN mkdir -p /homie-web-ui/config
RUN mkdir -p /homie-web-ui/logs

WORKDIR /homie-web-ui

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main/main.py"]
EXPOSE 80
