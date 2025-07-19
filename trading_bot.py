import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests, io
from PIL import Image
import pytesseract
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

BOT_TOKEN = ""

logging.basicConfig(level=logging.INFO)

def get_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    try:
        return float(requests.get(url).json()['price'])
    except:
        return None

def analyze_indicators(symbol):
    import pandas as pd
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100'
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=list(range(12)))
    df['close'] = df[4].astype(float)
    rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]
    ema = EMAIndicator(df['close'], window=20).ema_indicator().iloc[-1]
    return rsi, ema

def analyze_screenshot(img: Image.Image):
    text = pytesseract.image_to_string(img, lang='eng+ukr')
    resp = "📸 OCR текст:\n" + text
    return resp

async def start(u,c):
    await u.message.reply_text("Привіт! Надіслати повідомлення типу `BTCUSDT 1H` або фото позиції.")

async def handle_text(u,c):
    msg = u.message.text.upper().split()
    if len(msg)>=1:
        sym = msg[0].replace("/","")
        price = get_price(sym)
        if price:
            rsi, ema = analyze_indicators(sym)
            resp = f"💰 {sym}: {price}\nRSI(14): {rsi:.1f}\nEMA(20): {ema:.2f}"
            resp += "\n💡 "
            resp += "Ринок на перекупленості." if rsi>70 else "Можливий відкат." if rsi<30 else "Тренд стабільний."
            await u.message.reply_text(resp)
        else:
            await u.message.reply_text("⚠️ Пара не знайдена на Binance.")
    else:
        await u.message.reply_text("Напиши типу: `BTCUSDT 1H`")

async def handle_photo(u,c):
    img_data = await u.message.photo[-1].get_file().download_as_bytearray()
    img=Image.open(io.BytesIO(img_data))
    resp=analyze_screenshot(img)
    await u.message.reply_text(resp)

if __name__=="__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot started")
    app.run_polling()
