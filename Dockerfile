FROM python:3.11-slim
WORKDIR /app
COPY trading_bot.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "trading_bot.py"]
