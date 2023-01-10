import discord
import openai
from config import *


intents = discord.Intents.default()
intents.message_content = True


class my_client(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    def ai_bot(self, question):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response['choices'][0]['text']

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id == ai_bot_channel_id:
            await message.channel.send(self.ai_bot(message.content + '.'))


client = my_client(intents=intents)
client.run(token)
