import enum
import json
from os import getenv

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()


SINGLE_MESSAGE_PROMPT = """I will give you a message and you should generate a trading order in accordance to this message.
Do not generate a trading order if the message is not related to trading order (creating trading order).
The message related to trading order contains trading symbol, order type, stoploss, takeprofit.
Example of message related to trading order: "EURUSD: 👑
BUY LIMIT FROM : 1.02200✨
SL : 1.01750 (45Pips)🤑
TP : 1.04000 (4RR)💰"

If the message is not related to trading order and contains something like "All pending and limit orders are now invalid." generate a trading order with action field equal to "DELETE_ALL".

This is the message that I am giving: "{message}"
"""


class Action(enum.Enum):
    BUY_MARKET = "BUY_MARKET"
    SELL_MARKET = "SELL_MARKET"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    BUY_STOP_LIMIT = "BUY_STOP_LIMIT"
    SELL_STOP_LIMIT = "SELL_STOP_LIMIT"
    UPDATE = 'UPDATE'
    CLOSE = 'CLOSE'
    # If limit order have not been triggered.
    DELETE = 'DELETE'
    # If we receive message like "All pending and limit messages are now invalid"
    DELETE_ALL = 'DELETE_ALL'


class OrderSchema(BaseModel):
    symbol: str | None
    action: Action
    price: float | None
    stoploss: float | None
    takeprofit: float | None


class Order(BaseModel):
    # If the message is not related to trading order then order should be None.
    order: OrderSchema | None


client = genai.Client(api_key=getenv('GEMINI_API_KEY'))


def get_cmnd(message):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite-preview-02-05",
            contents=SINGLE_MESSAGE_PROMPT.format(message=message),
            config={
                'response_mime_type': 'application/json',
                'response_schema': Order
            }
        )
    except genai.errors.ServerError:
        return None

    return json.loads(response.text)
