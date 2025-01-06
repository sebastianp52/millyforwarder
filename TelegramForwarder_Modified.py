import time
import re
import asyncio
from telethon.sync import TelegramClient
from telethon import errors

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_a' + phone_number, api_id, api_hash)

    async def forward_messages_to_channel(self, source_chat_id, destination_channel_id, keywords):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        last_message_id = (await self.client.get_messages(source_chat_id, limit=1))[0].id

        while True:
            print("Checking for messages and forwarding them...")
            messages = await self.client.get_messages(source_chat_id, min_id=last_message_id, limit=None)

            for message in reversed(messages):
                if keywords:
                    if message.text and all(keyword in message.text.lower() for keyword in keywords):
                        if("Top holders:" not in message.text):
                            cleanedText = message.text.replace("`", "")
                            print(f"Message contains a keyword: {cleanedText}")
                                                
                            match = re.search(r"Dev Lock:\s*(\d+)h", cleanedText, re.IGNORECASE)
                            print("Match: ", match)
                        
                            if match:
                                hours = int(match.group(1).strip())
                                print("Hours: ", hours)
                            
                                if(hours >= 24):
                                    print("Dev Lock higher than 24 hours")
                                    await self.client.send_message(destination_channel_id, message.text)
                                    print("Message forwarded")
                                                    
                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)  # Adjust the delay time as needed

def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            print("Credentials file found.")
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None

def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")

        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    source_chat_id = int("-1002195541592")
    destination_channel_id = int("-4707410515")
    keywords = ['dev lock:', 'launch created']
    print("Keyworks used:", keywords)
        
    await forwarder.forward_messages_to_channel(source_chat_id, destination_channel_id, keywords)

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
