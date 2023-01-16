import discord
import asyncio
import openai
from better_profanity import profanity
from config import *


intents = discord.Intents.all()


class filter_value:
    """Check if it should filter messages."""

    def __init__(self):
        self.filter_content = False


class ai:
    """Class that connects with the OpenAI API to generate a response."""

    def __init__(self):
        self.temp = 0.7
        self.tokens = 50
        self.top_p = 1
        self.f_p = 0
        self.p_p = 0

    ### AI bot response ###

    def ai_bot(self, question):
        """Function request a response from the OpenaAI engine."""

        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=question,
            temperature=self.temp,
            max_tokens=self.tokens,
            top_p=self.top_p,
            frequency_penalty=self.f_p,
            presence_penalty=self.p_p
        )

        return response['choices'][0]['text']

    ### Update values ###

    def set_values(self, value, msg, lim, min, value_name):
        try:
            value = int(msg.content.split()[-1])

        except:
            value = value

        if value > lim:
            value = lim
            yield f'{value_name} limit is {lim}.'

        if value < min:
            value = min
            yield f'{value_name} minimum is {min}.'

        yield f'{value_name} set to {value}'


class my_client(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_member_join(self, member):
        ### Welcome ###

        channel = client.get_channel(general_channel_id)
        await channel.send(f'{member.mention} Welcome to my server!\nFor a list of available commands please type !help')

    async def on_message(self, message):
        ### Bot check ###

        if message.author == self.user:
            return

        ### Help ###

        if message.content.startswith('!help clear'):
            await message.channel.send(embed=discord.Embed(
                title='!clear',
                description='Clears all messages in the current channel.',
                color=0xFF5733))
            return

        if message.content.startswith('!help poll'):
            await message.channel.send(embed=discord.Embed(
                title='!poll',
                description='Creates an ambeded message that people can vote on through reactions.',
                color=0xFF5733))
            return

        if message.content.startswith('!help filter'):
            await message.channel.send(embed=discord.Embed(
                title='!filter',
                description='Used to manage the profanity filter (default is off).\n!filter to check if its on.\n!filter on / !filter off to turn it on/off.',
                color=0xFF5733))
            return

        if message.content.startswith('!help ai'):
            embed = discord.Embed(
                title='AI bot',
                description='An AI bot that you can ask questions and with the use of OpenAI and the GPT-3 text davinci engine.',
                color=0xFF5733)

            embed.add_field(
                name='**AI commands**',
                value='',
                inline=False
            )

            embed.add_field(
                name='!ai',
                value='Follow the command with what question you want to ask the AI.',
                inline=False
            )

            embed.add_field(
                name='!ai temp',
                value='Controlls randomness. Lowering the value results in less random outputs (0 - 1). \n Default: 0.7',
                inline=False
            )

            embed.add_field(
                name='!ai tokens',
                value='Controlls length of output (10 - 100). \n Default: 50',
                inline=False
            )

            embed.add_field(
                name='!ai topp',
                value='Controlls diversity through nucleus sampling (0 - 1). \n Default: 1',
                inline=False
            )

            await message.channel.send(embed=embed)
            return

        if message.content.startswith('!help'):
            embed = discord.Embed(
                title='Commands', description='To see the description of each command use **!help <command>**\n!clear\n!poll\n!filter\n!ai', color=0xFF5733)
            await message.channel.send(embed=embed)
            return

        ### Clear ###

        if message.content.startswith('!clear'):
            embed = discord.Embed(
                title='Clearing...', description='', color=0xFF5733)
            await message.channel.send(embed=embed)
            msg = []
            async for n in message.channel.history(limit=300):
                msg.append(n)

            for n in range(0, len(msg), 300):
                await message.channel.delete_messages(msg[n:n+300])
            return

        ### Filter ###

        if message.content.startswith('!filter on'):
            filter_content.filter_content = True
            await message.channel.send(f'Filter now set to True')
            return

        if message.content.startswith('!filter off'):
            filter_content.filter_content = False
            await message.channel.send(f'Filter now set to False')
            return

        if message.content.startswith('!filter'):
            await message.channel.send(f'Filter currently set to {filter_content.filter_content}')
            return

        if filter_content.filter_content == True and profanity.contains_profanity(message.content) == True:
            await message.delete()
            await message.channel.send(f'{message.author.mention} did a bit of a naughty but I have corrected his ways.\n{profanity.censor(message.content)}')
            return

        ### Poll ###

        if message.content.startswith('!poll'):
            msg = message.content.replace('!poll', '')
            embed = discord.Embed(
                title=f'Poll: {msg}', description='', color=0xFF5733)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction('\N{THUMBS UP SIGN}')
            await msg.add_reaction('\N{THUMBS DOWN SIGN}')

            self.poll_finish = client.loop.create_task(self.poll_test(message))
            return

        ### AI bot ###

        if message.channel.id == ai_bot_channel_id and message.content.startswith('!ai'):

            ### Set temprature ###

            if message.content.startswith('!ai temp'):
                for n in ai_bot.set_values(ai_bot.temp, message, 1, 0, 'Temprature'):
                    await message.channel.send(n)
                return

            ### Set tokens ###

            if message.content.startswith('!ai tokens'):
                for n in ai_bot.set_values(ai_bot.tokens, message, 100, 10, 'Tokens'):
                    await message.channel.send(n)
                return

            ### Set top p ###

            if message.content.startswith('!ai topp'):
                for n in ai_bot.set_values(ai_bot.top_p, message, 1, 0, 'Top P'):
                    await message.channel.send(n)
                return

            await message.channel.send(f'{message.author.mention}' + ai_bot.ai_bot(message.content + '.'))
            return

        ### Invalid command ###

        if message.content.startswith('!'):
            await message.channel.send('Type **!help** for a list of commands.')
            return

    ### Remove reactions from poll ###

    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        emoji = payload.emoji

        message = await client.get_channel(channel_id).fetch_message(message_id)
        reaction_users = []
        self.reactions_up = []
        self.reactions_down = []

        for reaction in message.reactions:
            async for user in reaction.users():
                reaction_users.append(user)

        if user_id in [user.id for user in reaction_users] and user_id != self.user.id:
            user_reaction_count = reaction_users.count(
                client.get_user(user_id))

            if user_reaction_count >= 2:
                await message.remove_reaction(emoji, client.get_user(user_id))

            else:
                if emoji.name == '\N{THUMBS UP SIGN}':
                    self.reactions_up.append(message.reactions)

                if emoji.name == '\N{THUMBS DOWN SIGN}':
                    self.reactions_down.append(message.reactions)

    ### Poll results ###

    async def poll_test(self, message):
        while True:
            await asyncio.sleep(20)
            embed = discord.Embed(
                title=f"Poll **{message.content.replace('!poll', '')}** results:",
                description=f'',
                color=0xFF5733
            )

            embed.add_field(
                name='\N{THUMBS UP SIGN}',
                value=len(self.reactions_up) + 1,
                inline=True
            )

            embed.add_field(
                name='\N{THUMBS DOWN SIGN}',
                value=len(self.reactions_down) + 1,
                inline=True
            )

            await message.channel.send(embed=embed)

            self.poll_finish.cancel()


filter_content = filter_value()
ai_bot = ai()
client = my_client(intents=intents)


if __name__ == '__main__':
    client.run(token)
