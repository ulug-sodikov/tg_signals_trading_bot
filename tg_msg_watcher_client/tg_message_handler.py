from os import getenv

from dotenv import load_dotenv
from telethon import TelegramClient, events

from utils import async_post_request


load_dotenv()


API_ID = int(getenv('API_ID'))
API_HASH = getenv('API_HASH')

SIGNALS_CHANNEL_ID = int(getenv('SIGNALS_CHANNEL_ID'))


client = TelegramClient('session_file', API_ID, API_HASH)


@client.on(events.NewMessage(chats=SIGNALS_CHANNEL_ID))
async def on_message(event):
    request_json = {'message': event.message.raw_text}
    if event.message.is_reply:
        request_json['reply_to_msg_id'] = (
            event.message.reply_to.reply_to_msg_id
        )

    await async_post_request(
        'http://supervisor:8756/new_message', request_json
    )


# This environmental variable is optional.
TEST_CHANNEL_ID = getenv('TEST_CHANNEL_ID')
if TEST_CHANNEL_ID is not None:
    TEST_CHANNEL_ID = int(TEST_CHANNEL_ID)

    @client.on(events.NewMessage(chats=TEST_CHANNEL_ID))
    async def on_message(event):
        await event.respond("Watcher is running!")


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
