import asyncio
import discord
import openai
import requests
from bs4 import BeautifulSoup
from better_profanity import profanity
import config

# Intents
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

        # Return only the response
        return response['choices'][0]['text']

    def set_values(self, value, msg, limit, minimum, value_name):
        """Update values"""

        # Check if the value is an integer
        try:
            value = int(msg.content.split()[-1])

        # If not, return an error message
        except Exception as e:
            print(e, '\nValue is not a valid integer.')

        # Check if the value is within the limit
        if value > limit:
            value = limit
            yield f'{value_name} limit is {limit}.'

        # Check if the value is above the minimum
        if value < minimum:
            value = minimum
            yield f'{value_name} minimum is {minimum}.'

        # Return the value
        yield f'{value_name} set to {value}'


class practice:
    """Class that handles the practice schedule."""

    def __init__(self):
        # URL to the practice schedule
        self.url = "https://www.uppsalavolley.com/sasongstider-schemaandringar/"
        self.current_html = requests.get(self.url, timeout=15).text

    ### Get schedule ###

    async def get_schedule(self):
        """Function to get schedule"""

        while True:
            # Get the current HTML
            soup = BeautifulSoup(self.current_html, "html.parser")
            a_tags = soup.find_all("a")

            channel = client.get_channel(config.schedule_channel_id)
            # Clear the channel
            await channel.purge(limit=10)

            # Send the schedule
            for a_tag in a_tags:
                if a_tag.get('href') and '.pdf' in a_tag.get('href'):
                    await channel.send(f'@everyone {"".join(a_tag.contents).replace("[", "").replace("]", "")}\n{a_tag.get("href")}')

            # Wait 3 days
            await asyncio.sleep(259200)


class my_client(discord.Client):
    """Main client"""

    async def on_ready(self):
        print('Logged on as', self.user)

        ### Practice schedule ###
        client.loop.create_task(
            practice_tracker.get_schedule())

    async def on_member_join(self, member):
        ### Welcome ###

        channel = client.get_channel(config.general_channel_id)
        await channel.send(f'{member.mention} Welcome to my server!\nFor a list of available commands please type !help')

    async def on_message(self, message):
        ### Bot check ###

        if message.author == self.user:
            return

        ### Help ###

        if message.content.startswith('!help clear'):
            await message.channel.send(embed=discord.Embed(
                title='!clear',
                description='Clears messages in the current channel.',
                color=0xFF5733))
            return

        if message.content.startswith('!help poll'):
            await message.channel.send(embed=discord.Embed(
                title='!poll [topic]',
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
                name='!ai [prompt]',
                value='Ask the AI questions.',
                inline=False
            )

            embed.add_field(
                name='!ai temp [0 - 1]',
                value='Controlls randomness. Lowering the value results in less random outputs. \n Default: 0.7',
                inline=False
            )

            embed.add_field(
                name='!ai tokens [10 - 100]',
                value='Controlls length of output. \n Default: 50',
                inline=False
            )

            embed.add_field(
                name='!ai topp [0 - 1]',
                value='Controlls diversity through nucleus sampling. \n Default: 1',
                inline=False
            )

            await message.channel.send(embed=embed)
            return

        if message.content.startswith('!help'):
            embed = discord.Embed(
                title='Commands', description='To see the description of each command use **!help [command]**\n!clear\n!poll\n!filter\n!ai', color=0xFF5733)

            embed.add_field(name='Schedule',
                            value='Every 3 days the AI scrapes the Uppsala volleyboll official website and gets the schedule and posts it in the schedule discord channel.',
                            inline=False)

            await message.channel.send(embed=embed)
            return

        ### Clear ###

        if message.content.startswith('!clear'):
            embed = discord.Embed(
                title='Clearing...', description='', color=0xFF5733)
            await message.channel.send(embed=embed)
            # Clear the channel
            await message.channel.purge(limit=100000)
            return

        ### Filter ###

        # Change the filter
        if message.content.startswith('!filter on'):
            filter_content.filter_content = True
            await message.channel.send('Filter now set to True')
            return

        # Change the filter
        if message.content.startswith('!filter off'):
            filter_content.filter_content = False
            await message.channel.send('Filter now set to False')
            return

        # Check the filter
        if message.content.startswith('!filter'):
            await message.channel.send(f'Filter currently set to {filter_content.filter_content}')
            return

        # Filter the message
        if filter_content.filter_content is True and profanity.contains_profanity(message.content) is True:
            await message.delete()
            await message.channel.send(f'{message.author.mention} did a bit of a naughty but I have corrected his ways.\n{profanity.censor(message.content)}')
            return

        ### Poll ###

        if message.content.startswith('!poll'):
            # Get the message without the command
            msg = message.content.replace('!poll', '')
            embed = discord.Embed(
                title=f'Poll: {msg}', description='', color=0xFF5733)
            msg = await message.channel.send(embed=embed)
            # Add initial reactions
            await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
            await msg.add_reaction('\N{CROSS MARK}')

            # Start the poll countdown for results
            self.poll_finish = client.loop.create_task(
                self.poll_result_countdown(message))
            return

        ### AI bot ###

        if message.channel.id == config.ai_bot_channel_id and message.content.startswith('!ai'):

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

        # Get message
        message = await client.get_channel(channel_id).fetch_message(message_id)
        reaction_users = []
        self.reactions_up = []
        self.reactions_down = []

        # Get all users that reacted to the message
        for reaction in message.reactions:
            async for user in reaction.users():
                reaction_users.append(user)

        # Remove reactions from users that reacted more than once
        if user_id in [user.id for user in reaction_users] and user_id != self.user.id:
            user_reaction_count = reaction_users.count(
                client.get_user(user_id))

            if user_reaction_count >= 2:
                await message.remove_reaction(emoji, client.get_user(user_id))

            # Get results
            else:
                if emoji.name == '\N{WHITE HEAVY CHECK MARK}':
                    self.reactions_up.append(message.reactions)

                if emoji.name == '\N{CROSS MARK}':
                    self.reactions_down.append(message.reactions)

    ### Poll results ###

    async def poll_result_countdown(self, message):
        """Poll results"""

        while True:
            # Wait 20 seconds
            await asyncio.sleep(20)

            # Poll results
            embed = discord.Embed(
                title=f"Poll **{message.content.replace('!poll', '')}** results:",
                description='',
                color=0xFF5733
            )

            embed.add_field(
                name='\N{WHITE HEAVY CHECK MARK}',
                value=len(self.reactions_up) + 1,
                inline=True
            )

            embed.add_field(
                name='\N{CROSS MARK}',
                value=len(self.reactions_down) + 1,
                inline=True
            )

            await message.channel.send(embed=embed)

            # Cancel the task
            self.poll_finish.cancel()


# Define the classes
filter_content = filter_value()
ai_bot = ai()
practice_tracker = practice()
client = my_client(intents=intents)


# Run the bot
if __name__ == '__main__':
    client.run(config.token)
