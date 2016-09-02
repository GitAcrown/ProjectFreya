import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
from urllib import request
import re
import asyncio
import os

#Freya Exclusive

class Stick:
    """Ajout de stickers personnalisés."""

    def __init__(self, bot):
        self.bot = bot
        self.base = dataIO.load_json("data/stick/base.json")

    @commands.group(pass_context=True, no_pm=True)
    async def sticker(self, ctx):
        """Gestion du module de Stickers."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @sticker.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def add(self, ctx, nom, url):
        """Ajoute un sticker à la base de données."""
        if nom not in self.base:
            filename = url.split('/')[-1]
            if ".gif" in filename:
                filename = filename[:-4]
                filename = filename + ".png"
                await self.bot.say("Fichier converti de '.gif' en '.png'")
            try:
                f = open(filename, 'wb')
                f.write(request.urlopen(url).read())
                f.close()
                file = "data/autre/" + filename
                os.rename(filename,file)
                await self.bot.say("Fichier téléchargé et enregistré.")
                self.base[nom] = {"CHEMIN": file, "URL": url}
                fileIO("data/stick/base.json", "save", self.base)
            except Exception as e:
                print("Erreur, impossible de télécharger l'image : {}".format(e))
                await self.bot.say("Désolé, mais cette image ne peut pas être téléchargée")
        else:
            await self.bot.say("Sticker déjà chargé.")

    @sticker.command(pass_context=True, no_pm=True, hidden=True)
    @checks.mod_or_permissions(kick_members=True)
    async def manualadd(self, ctx, nom, chemin):
        """Ajoute un sticker à la base de données manuellement."""
        if nom not in self.base:
            self.base[nom] = {"CHEMIN" : chemin, "URL" : None}
            await self.bot.say("Enregistré.")
            fileIO("data/stick/base.json", "save", self.base)
        else:
            await self.bot.say("Déjà dans la base de données.")

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def convert(self, ctx, base: str, ext: str, url):
        """Permet de convertir basiquement le format d'un fichier.
        'base' : Extension fichier au départ
        'ext' : Extension fichier désiré
        'url' : Url de téléchargement
        /!\ Corruption possible. N'utilisez que des liens finissant par une extension. /!\
        """
        filename = url.split('/')[-1]
        channel = ctx.message.channel
        long = len(base)
        if base in filename:
            filename = filename[:-long]
            filename = filename + ext
            f = open(filename, 'wb')
            f.write(request.urlopen(url).read())
            f.close()
            file = "data/convert/" + filename
            os.rename(filename,file)
            await self.bot.say("Conversion du fichier de {} à {}...".format(base, ext))
            await asyncio.sleep(1)
            await self.bot.send_file(channel, file)
        else:
            await self.bot.say("Votre extension de base n'est pas reconnue dans l'URL.")
        

    @sticker.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def delete(self, ctx, nom):
        """Supprime un sticker de la base de données."""
        if nom in self.base:
            chemin = self.base[nom]["CHEMIN"]
            os.remove(chemin)
            del self.base[nom]
            await self.bot.say("Sticker supprime.")
        else:
            await self.bot.say("Ce sticker n'existe pas.")

    @sticker.command(pass_context=True, no_pm=True, hidden=True)
    @checks.mod_or_permissions(kick_members=True)
    async def reupload(self, ctx):
        """Essaye de reupload l'ensemble des images présentes dans base.json et base.bak"""
        present = os.listdir("data/autre/")
        msg = ""
        await self.bot.say("Je vais essayer de faire ça... (Cette opération peut prendre du temps)")
        for sticker in self.base:
            if sticker not in present:
                url = self.base[sticker]["URL"]
                filename = url.split('/')[-1]
                if url != None:
                    try:
                        f = open(filename, 'wb')
                        f.write(request.urlopen(url).read())
                        f.close()
                        await asyncio.sleep(0,25)
                        file = "data/autre/" + filename
                        os.rename(filename,file)
                        msg += "Fichier {} téléchargé et enregistré.".format(filename)
                        self.base[nom] = {"CHEMIN": file, "URL": url}
                        fileIO("data/stick/base.json", "save", self.base)
                    except Exception as e:
                        print("Erreur, impossible de télécharger l'image : {}".format(e))
                        msg += "Désolé, mais {} ne peut pas être téléchargée".format(filename)
                else:
                    "Désolé, mais {} ne peut pas être téléchargée car elle ne possède pas d'URL"
            else:
                pass
        else:
            await self.bot.say(msg)
            await self.bot.say("L'ensemble des fichiers non présents ont été upload.")

    @sticker.command(name = "list", pass_context=True, no_pm=True)
    async def _list(self, ctx):
        """Liste les stickers disponibles."""
        msg = "```Stickers disponibles:\n"
        for sticker in self.base:
            msg += ":{}:\n".format(sticker)
        else:
            msg += "```"
        await self.bot.whisper(msg)

    async def check_msg(self, message):
        channel = message.channel
        if ":" in message.content:
            output = re.compile(':(.*?):', re.DOTALL |  re.IGNORECASE).findall(message.content)
            if output:
                for sticker in output:
                    if sticker in self.base:
                        chemin = self.base[sticker]["CHEMIN"]
                        url = self.base[sticker]["URL"]
                        try:
                            await self.bot.send_file(channel, chemin)
                        except Exception as e:
                            print("Erreur, impossible d'upload l'image : {}".format(e))
                            if url != None:
                                await self.bot.send_message(channel, url)
                            else:
                                pass
                    else:
                        pass
            else:
                pass
        else:
            pass

def check_folders():
    # create data/sadface if not there
    if not os.path.exists("data/stick"):
        print("Creating data/stick folder...")
        os.makedirs("data/stick")

def check_files():
    # create server.json if not there
    # put in default values
    
    if not os.path.isfile("data/stick/base.json"):
        print("Creating default stick base.json...")
        fileIO("data/stick/base.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Stick(bot)
    # add an on_message listener
    bot.add_listener(n.check_msg, "on_message")
    bot.add_cog(n)
