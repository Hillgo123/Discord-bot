import discord
import openai
from better_profanity import profanity
from config import *


intents = discord.Intents.all()


class filter_value:
    """Check if it should filter messages."""

    def __init__(self):
        self.filter_content = False


class my_client(discord.Client):
    ### AI bot response ###

    def ai_bot(self, question):
        """Function request a response from the OpenaAI engine."""
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=1,
            max_tokens=80,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response['choices'][0]['text']

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_member_join(self, member):
        ### Welcome ###

        channel = client.get_channel(general_channel_id)
        await channel.send((f"{member.mention} Welcome to my server!\nFor a list of available commands please type $help"))

    async def on_message(self, message):
        ### Bot check ###

        if message.author == self.user:
            return

        ### Help ###

        if message.content.startswith('$help clear'):
            await message.channel.send(embed=discord.Embed(
                title='$clear', description='Clears all messages in the current channel.', color=0xFF5733))
            return

        if message.content.startswith('$help poll'):
            await message.channel.send(embed=discord.Embed(
                title='$poll', description='Clears all messages in the current channel.', color=0xFF5733))
            return

        if message.content.startswith('$help filter'):
            await message.channel.send(embed=discord.Embed(
                title='$filter', description='Used to manage the profanity filter (default is off).\n$filter to check if its on.\n$filter on / $filter off to turn it on/off.', color=0xFF5733))
            return

        if message.content.startswith('$help'):
            embed = discord.Embed(
                title='Info', description='To see the description of each command use **$help <command>**', color=0xFF5733)
            embed.add_field(name="AI bot",
                            value="An AI bot that you can ask questions and with the use of OpenAI and it's GPT-3 text davinci engine.To use the AI type anything in the AI bot channel.",
                            inline=False)
            embed.add_field(name="Commands",
                            value="$clear\n$poll\n$filter",
                            inline=False)
            await message.channel.send(embed=embed)
            return

        ### Clear ###

        if message.content.startswith('$clear'):
            await message.channel.send(embed=self.embed("Clearing...", ""))
            msg = []
            async for n in message.channel.history(limit=100):
                msg.append(n)

            for n in range(0, len(msg), 100):
                await message.channel.delete_messages(msg[n:n+100])
            return

        ### Filter ###

        if message.content.startswith('$filter on'):
            filter_content.filter_content = True
            await message.channel.send(f'Filter now set to True')
            return

        if message.content.startswith('$filter off'):
            filter_content.filter_content = False
            await message.channel.send(f'Filter now set to False')
            return

        if message.content.startswith('$filter'):
            await message.channel.send(f'Filter currently set to {filter_content.filter_content}')
            return

        if filter_content.filter_content == True and profanity.contains_profanity(message.content) == True:
            await message.delete()
            await message.channel.send(f'{message.author.mention} did a bit of a naughty but I have corrected his ways.\n{profanity.censor(message.content)}')
            return

        ### Poll ###

        if message.content.startswith('$poll'):
            msg = message.content.replace('$poll', '')
            msg = await message.channel.send(embed=self.embed(f'Poll: {msg}', ''))
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            return

        ### Invalid command ###

        if message.content.startswith('$'):
            await message.channel.send('Type **$help** for a list of commands.')
            return

        ### AI bot ###

        if message.channel.id == ai_bot_channel_id:
            await message.channel.send(f"{message.author.mention}\n" + self.ai_bot(message.content + '.'))
            return

    ### Remove reactions from poll ###

    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        emoji = payload.emoji

        message = await client.get_channel(channel_id).fetch_message(message_id)
        reaction_users = []

        for reaction in message.reactions:
            async for user in reaction.users():
                reaction_users.append(user)

        if user_id in [user.id for user in reaction_users] and not user_id == self.user:
            user_reaction_count = reaction_users.count(
                client.get_user(user_id))

            if user_reaction_count >= 2:
                await message.remove_reaction(emoji, client.get_user(user_id))


filter_content = filter_value()
client = my_client(intents=intents)


if __name__ == '__main__':
    client.run(token)
