import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import random
import os
import logging
import asyncio

#Freya Exclusive

class Snap:
    """Outil de cryptage de ligne de textes"""

    def __init__(self, bot):
        self.bot = bot
        self.data = dataIO.load_json("data/snap/data.json")
        self.video = ["https://www.youtube.com/watch?v=ZZ5LpwO-An4", "https://www.youtube.com/watch?v=vTIIMJ9tUc8", "https://www.youtube.com/watch?v=z13qnzUQwuI",
                      "https://www.youtube.com/watch?v=y6120QOlsfU", "https://www.youtube.com/watch?v=zA52uNzx7Y4", "https://www.youtube.com/watch?v=IRvGZffXhfk",
                      "https://www.youtube.com/watch?v=jRx5PrAlUdY", "https://www.youtube.com/watch?v=GjsnYmi4z0U", "https://www.youtube.com/watch?v=BJ0xBCwkg3E",
                      "https://www.youtube.com/watch?v=jItz-uNjoZA", "https://www.youtube.com/watch?v=PGNiXGX2nLU", "https://www.youtube.com/watch?v=llHhiiNnIjY"]
                      

    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(kick_members=True)
    async def random(self, ctx):
        """Lance une vidéo au hasard..."""
        video = random.choice(self.video)
        await self.bot.say(video)

    @commands.group(pass_context=True)
    async def snap(self, ctx):
        """Gestion du codage de textes."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @snap.command(aliases=["n"], pass_context=True)
    async def new(self, ctx, temps: int, *msg):
        """Code une ligne de caractères et fournit un code de décryptage.
        Le temps doit être compris entre 10 et 500t.

        Format Normal = Plus de 60 (Format: 000TXXXXXC000)
        Format Flash = Maximum 60 (Format: 00-AAAA)"""
        server = ctx.message.server
        msg = " ".join(msg)
        user = ctx.message.author
        msgtype = self.gen_type(msg)
        if server == None:
            if temps >= 10 and temps <= 500:
                code = self.gen_code(temps)
                self.data[code] = {"Code": code, "Message": msg, "Auteur": user.name, "Type": msgtype}
                fileIO("data/snap/data.json", "save", self.data)
                await self.bot.whisper("Votre message a bien été codé. Le code est: **{}**".format(code))
                await asyncio.sleep(temps)
                if code in self.data:
                    del self.data[code]
                    fileIO("data/snap/data.json", "save", self.data)
                    await self.bot.whisper("**Votre code {} a expiré**".format(str(code)))
                else:
                    await self.bot.whisper("Votre code à été supprimé avant qu'il n'arrive à expiration")
            else:
                await self.bot.whisper("Le temps doit être compris entre 10 et 500 ticks.")
        else:
            await self.bot.say("Cette fonction ne peut-être utilisée qu'en MP avec le bot")

    @snap.command(aliases=["p"], pass_context=True)
    async def preview(self, ctx, code):
        """Demande au bot de quel type est le message lié à un code."""
        prev = "Le message est du type: "
        if code in self.data:
            prev += self.data[code]["Type"]
            await self.bot.whisper(prev)
        else:
            await self.bot.whisper("Ce code n'existe pas ou n'est plus exploitable")

    @snap.command(aliases=["r"], pass_context=True)
    async def reveal(self, ctx, code):
        """Révèle le message lié au code fournit."""
        msg = "**Voici le message:** "
        server = ctx.message.server
        if server == None:
            if code in self.data:
                data = self.data[code]["Message"]
                msg += str(data)
            else:
                msg += "Le message n'est plus exploitable ou n'existe pas."
        else:
            await self.bot.say("Cette fonction ne peut-être utilisée qu'en MP avec le bot")
        await self.bot.whisper(msg)

    @snap.command(aliases=["del"], pass_context=True, hidden=True)
    @checks.mod_or_permissions(kick_members=True)
    async def delete(self, ctx, code):
        """Supprime un message.

        Réservé à la modération"""
        if code in self.data:
            del self.data[code]
            fileIO("data/snap/data.json", "save", self.data)
            await self.bot.whisper("Le message lié au code {} a été supprimé.".format(str(code)))
        else:
            await self.bot.whisper("Ce code n'est plus exploitable ou n'existe pas.")

    @snap.command(aliases=["clr"], pass_context=True, hidden=True)
    @checks.mod_or_permissions(kick_members=True)
    async def clear(self, ctx):
        """Supprime l'ensemble des snap en cours.

        Réservé à la modération"""
        for code in self.data:
            del self.data[code]
            fileIO("data/snap/data.json", "save", self.data)
            await self.bot.whisper("Le message lié au code {} a été supprimé.".format(str(code)))
        else:
            await self.bot.whisper("**Le fichier est vide**")
    
#DEF

    def gen_code(self, temps):
        liste = ['A','B','C','D','E','Z','Y','X','W','V']
        if temps <= 60: #Code court type 18-AZBY
            code = str(random.randint(10,99)) + "-"
            echant = random.sample(liste,4)
            code += ''.join(x for x in echant if x)
            return code
        if temps > 60: #Code long type 674TDEZYXC159
            code = str(random.randint(100,999)) + "T"
            echant = random.sample(liste,5)
            code += ''.join(x for x in echant if x) + "C"
            code += str(random.randint(100,999))
            return code

    def gen_type(self, msg):#Cherche des termes dans le "msg" pour en sortir une preview
        msgtype = ""
        if "http" in msg:
            msgtype += " **Lien**"
            if ".png" in msg:
                msgtype += " **Image png**"
                return msgtype
            elif ".jpg" in msg:
                msgtype += " **Image jpg**"
                return msgtype
            elif ".gif" in msg:
                msgtype += " **Image gif**"
                return msgtype
            elif ".webm" in msg:
                msgtype += " **Video webm**"
                return msgtype
            elif ".mp4" in msg:
                msgtype += " **Video mp4**"
                return msgtype
            elif ".mp3" in msg:
                msgtype += " **MP3**"
                return msgtype
            elif "youtube" in msg:
                msgtype += " **Youtube**"
                return msgtype
            elif "google" in msg:
                msgtype += " **Google**"
                return msgtype
            elif "jeuxvideo.com" in msg:
                msgtype += " **JVC**"
                return msgtype
            elif "porn" in msg:
                msgtype += " **Pornographique**"
                return msgtype
            elif "4chan" in msg:
                msgtype += " **4chan**"
                return msgtype
            else:
                return msgtype
        else:
            msgtype += " **Texte ou Autre**"
            return msgtype
    
#DEMARRAGE

def check_folders():
    folders = ("data", "data/snap/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
     if not os.path.isfile("data/snap/data.json"):
        print("Creating empty data.json...")
        fileIO("data/snap/data.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Snap(bot)
    bot.add_cog(n)    
