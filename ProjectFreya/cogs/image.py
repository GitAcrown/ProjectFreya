import discord
from discord.ext import commands
from random import randint
import aiohttp
import random

class Image:
    """Image related commands."""

    def __init__(self, bot):
        self.bot = bot
        #Reserved for further ... stuff

    """Commands section"""

    @commands.command(no_pm=True)
    async def imgur(self, *text):
        """Renvoie une image de imgur

        imgur search [mot clef] - Revoie le premier résultat
        imgur [section] [top ou new] - Renvoie les 3 dernières ou meilleures images d'une section, ex. 'funny'."""
        imgurclient = ImgurClient("1fd3ef04daf8cab", "f963e574e8e3c17993c933af4f0522e1dc01e230")
        if text == ():
            rand = randint(0, 59) #60 results per generated page
            items = imgurclient.gallery_random(page=0)
            await self.bot.say(items[rand].link)
        elif text[0] == "search":
            items = imgurclient.gallery_search(" ".join(text[1:len(text)]), advanced=None, sort='time', window='all', page=0)
            if len(items) < 1:
                await self.bot.say("Votre recherche ne donne aucun résultat.")
            else:
                await self.bot.say(items[0].link)
        elif text[0] != ():
            try:
                if text[1] == "top":
                    imgSort = "top"
                elif text[1] == "new":
                    imgSort = "time"
                else:
                    await self.bot.say("Seul Top ou New sont siponibles.")
                    return
                items = imgurclient.subreddit_gallery(text[0], sort=imgSort, window='day', page=0)
                if (len(items) < 3):
                    await self.bot.say("Cette section n'existe pas. Essayez 'funny'")
                else:
                    await self.bot.say("{} {} {}".format(items[0].link, items[1].link, items[2].link))
            except:
                await self.bot.say("Tapez *help imgur* pour avoir des détails.")

    @commands.command(no_pm=True)
    async def gif(self, *text):
        """Renvoie le premier résultat de la recherche giphy
        
        gif [mot clef]"""
        if len(text) > 0:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "http://api.giphy.com/v1/gifs/search?q=" + msg + "&api_key=dc6zaTOxFJmzC"
                    async with aiohttp.get(search) as r:
                        result = await r.json()
                    if result["data"] != []:
                        url = result["data"][0]["url"]
                        await self.bot.say(url)
                    else:
                        await self.bot.say("Aucun résultat.")
                except:
                    await self.bot.say("Erreur.")
            else:
                await self.bot.say("Recherche invalide.")
        else:
            await self.bot.say("gif [texte]")

    @commands.command(no_pm=True)
    async def gifr(self, *text):
        """Renvoie un gif au hasard parmis les résultats de la recherche

        gifr [mot clef]"""
        random.seed()
        if len(text) > 0:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "http://api.giphy.com/v1/gifs/random?&api_key=dc6zaTOxFJmzC&tag=" + msg
                    async with aiohttp.get(search) as r:
                        result = await r.json()
                        if result["data"] != []:
                            url = result["data"]["url"]
                            await self.bot.say(url)
                        else:
                            await self.bot.say("Aucun résultat.")
                except:
                    await self.bot.say("Erreur.")
            else:
                await self.bot.say("Recherche invalide.")
        else:
            await self.bot.say("gifr [texte]")

class ModuleNotFound(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message

def setup(bot):
    global ImgurClient
    try:
        from imgurpython import ImgurClient
    except:
        raise ModuleNotFound("imgurpython n'est pas installé. Faîtes 'pip3 install imgurpython' pour utiliser ce module.")
    bot.add_cog(Image(bot))
