FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir discord.py docker

COPY bot.py .

CMD ["python", "bot.py"]
