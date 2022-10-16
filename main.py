import discord
from discord.ext import commands

from webserver import keep_alive

import os
from replit import db
import random
import requests
import json
from operator import itemgetter
import asyncio

token = os.environ['bot_token']


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + "\n-" + json_data[0]['a']
    return (quote)


def addTokens(user_id, amount):
    exists = False
    counter = -1
    if "userTokens" in db.keys():
        for user in db["userTokens"]:
            counter += 1

            if user[0] == user_id:
                old_tokens = user[1]
                del db["userTokens"][counter]

                tokens = old_tokens + amount
                db["userTokens"].append([user_id, tokens])
                exists = True
                break
            else:
                exists = False

        if (exists == False):
            db["userTokens"].append([user_id, amount])
    else:
        db["userTokens"] = [[user_id, amount]]


def subtractTokens(user_id, amount):
    exists = False
    counter = -1
    if "userTokens" in db.keys():
        for user in db["userTokens"]:
            counter += 1

            if user[0] == user_id:
                old_tokens = user[1]
                del db["userTokens"][counter]

                tokens = old_tokens - amount
                db["userTokens"].append([user_id, -amount])
                exists = True
                break
            else:
                exists = False

        if (exists == False):
            db["userTokens"].append([user_id, -tokens])
    else:
        db["userTokens"] = [[user_id, -amount]]


def getAllUsersTokens():
    if "userTokens" in db.keys():
        return db["userTokens"]
    else:
        db["userTokens"] = []
        return db["userTokens"]


def getUserTokens(user_id):
    exists = False
    if "userTokens" in db.keys():
        for user in db["userTokens"]:
            if user[0] == user_id:
                return int(user[1])
                exists = True
                break
            else:
                exists = False

        if exists == False:
            users = db["userTokens"]
            users.append([user_id, 0])

            for user in db["userTokens"]:
                if user[0] == user_id:
                    return int(user[1])
    else:
        db["userTokens"] = [[user_id, 0]]
        for user in db["userTokens"]:
            if user[0] == user_id:
                return int(user[1])


def addText(user_id, text):
    if "bot_textArray" in db.keys():
        texts = db["bot_textArray"]
        texts.append([user_id, text])

        db["bot_textArray"] = texts
    else:
        texts = [[user_id, text]]

        db["bot_textArray"] = texts


def getAllTexts():
    if "bot_textArray" in db.keys():
        return db["bot_textArray"]
    else:
        return None


def removeText(number):
    if "bot_textArray" in db.keys():
        texts = db["bot_textArray"]
        del texts[number]

        db["bot_textArray"] = texts


client = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix=">>", intents=discord.Intents.all())


@bot.event
async def on_message(message):
    author_id = message.author.id

    if message.author.bot:
        return
    else:
        addTokens(author_id, 1)

    await bot.process_commands(message)
    

@bot.command()
async def getRandText(ctx):
    text = getAllTexts()[random.randint(0, len(getAllTexts()))]
    user = await bot.fetch_user(text[0])
    username = user.name

    await ctx.send(f"{username}:\n{text[1]}")


@bot.command()
async def addToTextArray(ctx):

    def check(message: discord.Message):
        return message.channel == ctx.channel and message.author == ctx.author

    user_tokens = getUserTokens(ctx.author.id)
    if (user_tokens >= 100):
        await ctx.send("Enter your text!")

        try:
            text = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to add.')
        except:
            await ctx.send("Something went wrong.")
        else:
            await ctx.send(f"Sucessfully added your text: \"{text.content}\"")
            addText(ctx.author.id, text.content)
            subtractTokens(ctx.author.id, 300)
    else:
        await ctx.send(
            f"You do not have enough tokens to add to the tex array. You need {300-user_tokens} more tokens!"
        )


@bot.command()
async def showTextArray(ctx):
    await ctx.send("Here is **all** of the text from the TextArray.\n\n")

    counter = 0
    for text in getAllTexts():
        await ctx.send(f"{counter} >> {text}")
        counter += 1


@bot.command()
async def flipCoin(ctx, guess):
    amount = random.randint(2, 10)

    if (not guess):
        await ctx.send("You didn't enter `heads` or `tails`!")
    else:
        coin = random.choice(["heads", "tails"])
        if (guess.lower() == coin):
            await ctx.send(f"You got it correct! You gained {amount} tokens!")

            addTokens(ctx.author.id, amount)
        else:
            if (guess in ["heads", "tails"]):
                await ctx.send("You didn't get it :(")
            else:
                await ctx.send("You didn't enter `heads` or `tails`!")

            await ctx.send(f"You lost {amount} tokens.")
            subtractTokens(ctx.author.id, amount)


@bot.command()
async def getMemberTokens(ctx, user: discord.User = None):
    if (not user):
        await ctx.send(
            f"**{ctx.author.display_name}** currently has {getUserTokens(ctx.author.id)} tokens!"
        )
    else:
        try:
            username = user.display_name

            await ctx.send(
                f"**{username}** currently has {getUserTokens(user.id)} tokens!"
            )
        except Exception as e:
            await ctx.send(f"Error {e}")


@bot.command()
async def getTokenLeaderboard(ctx):
    users = []
    for thing in getAllUsersTokens()[0:10]:
        ruser = await bot.fetch_user(thing[0])
        username = ruser.name

        users.append([username, thing[1]])

    real_things = sorted(users, reverse=True, key=itemgetter(1))

    await ctx.send("**GLOBAL** Token Leaderboard:")
    counter = 1
    for user in real_things:
        await ctx.send(f"{counter} >> {user[0]} has {user[1]}")
        counter += 1


@bot.command()
async def getInspiringQuote(ctx):
    await ctx.send(f"{get_quote()}")


keep_alive()

bot.run(token)
