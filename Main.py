import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os
import asyncio
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

with open("config.json") as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]
SERVER_ID = 1031787884832890971
C_QOTD = 1221538987123019786
QOTD_ROLE_NAME = "Mods"
ADMIN_USER_ID = 770668417367670866
role_idV = 1220863107891597312
#-------------COMMANDS-------------
@bot.event
async def on_ready():
    global role_mention
    global role_idV
    role_mention = role_idV
    if not role_mention:
        role_mention = None 
    print(role_idV)
    print(f"{bot.user} has connected to Discord!")
    print(SERVER_ID, C_QOTD, QOTD_ROLE_NAME, ADMIN_USER_ID)
    guild = discord.Object(id=SERVER_ID)
    await bot.tree.sync(guild=guild)
    print("Commands synced successfully!")
    role_id = role_idV
    role_mention = f"<@&{role_id}>"
    # Start the time-checking loop if it's not running
    if not check_new_day.is_running():
        check_new_day.start()

@bot.tree.command(name="add-question", description="Adds a question to the database")
async def add_question(interaction: discord.Interaction, question: str):
    try:
        # Admin bypass: Check if user is an admin (your user ID)
        if interaction.user.id == ADMIN_USER_ID or any(role.name == QOTD_ROLE_NAME for role in interaction.user.roles):
            questions = []
            if os.path.exists("questions.json"):
                with open("questions.json", "r") as file:
                    try:
                        questions = json.load(file)
                    except json.JSONDecodeError:
                        questions = []

            questions.append(question)

            with open("questions.json", "w") as file:
                json.dump(questions, file, indent=4)  

            await interaction.response.send_message(f"Question added: {question}", ephemeral=True)
            print(f"Question saved: {question}")
        else:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"Error adding question: {e}", ephemeral=True)
        print(f"Error adding question: {e}")



@bot.tree.command(name="manual-qotd", description="Manually trigger posting the Question of the Day")
async def manual_qotd(interaction: discord.Interaction):
    try:
        # Admin bypass: Check if user is an admin (your user ID)
        if interaction.user.id == ADMIN_USER_ID or any(role.name == QOTD_ROLE_NAME for role in interaction.user.roles):
            await post_qotd(interaction, is_manual=True)
        else:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"Error triggering QOTD: {e}", ephemeral=True)
        print(f"Error triggering QOTD: {e}")


#-----------------Time Check-----------------
@tasks.loop(hours=24)  # This will run every 24 hours, effectively checking for a new day
async def check_new_day():
    # Get the current date and time
    now = datetime.now()

    # Calculate when the next midnight will be
    midnight = datetime.combine(now + timedelta(days=1), datetime.min.time())
    time_until_midnight = (midnight - now).total_seconds()

    # Sleep until the new day starts (asynchronously)
    await asyncio.sleep(time_until_midnight)

    # Once it's a new day, send a message to the QOTD channel
    await post_qotd(None, is_manual=False)


async def post_qotd(interaction: discord.Interaction, is_manual: bool):
    """Posts the Question of the Day (QOTD) to the QOTD channel."""
    channel = bot.get_channel(C_QOTD)  
    if channel:
        questions = []
        if os.path.exists("questions.json"):
            with open("questions.json", "r") as file:
                try:
                    questions = json.load(file)
                except json.JSONDecodeError:
                    questions = []

        if questions:
            question = questions.pop(0) 

            with open("questions.json", "w") as file:
                json.dump(questions, file, indent=4)  
            await channel.send(f"Question of the Day {role_mention}: {question}")  

            if is_manual:
                await interaction.response.send_message(f"Question manually triggered {role_mention}: {question}", ephemeral=True)
            else:
                print(f"Question of the Day {role_mention}: {question}")
        else:
            await channel.send("No questions available for today.")
            if is_manual:
                await interaction.response.send_message("No questions available to post.", ephemeral=False)
    else:
        if is_manual:
            await interaction.response.send_message("Failed to find the channel.", ephemeral=True)
        else:
            print("Failed to find the channel.")


# Run the bot
bot.run(TOKEN)
