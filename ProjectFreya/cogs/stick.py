import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
from urllib import request
import re
import asyncio
import os
import random

#Freya Exclusive

default_img = {"IMG" : {}, "CAT" : {}}

class Stock:
    """Permet de stocker des données en local pour des fonctions utiles."""

    def __init__(self, bot):
        self.bot = bot
        self.img = dataIO.load_json("data/stock/img.json")
        self.trg = dataIO.load_json("data/stock/trg.json")

    #------------ IMG --------------#

    @commands.group(pass_context=True)
    async def imgset(self, ctx):
        """Gestion des images."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @imgset.command(pass_context=True, no_pm=True, hidden=True)
    @checks.mod_or_permissions(kick_members=True)
    async def erase(self):
        """Efface entièrement les données du module."""
        self.img = {default_img}
        fileIO("data/stock/img.json", "save", self.img)
        await self.bot.say("Suppression des données du module Stick réussie.")

    @imgset.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def catadd(self, ctx, nom, *descr):
        """Ajoute une catégorie au module."""
        nom = nom.upper()
        descr = " ".join(descr)
        if "URLONLY" in self.img["CAT"] and "AUTRES" in self.img["CAT"]:
            if descr != "":
                if nom not in self.img["CAT"]:
                    self.img["CAT"][nom] = {"NOM" : nom, "DESC" : descr}
                    fileIO("data/stock/img.json", "save", self.img)
                    await self.bot.say("**Votre catégorie {} à bien été admise**".format(nom))
                else:
                    await self.bot.say("Cette catégorie semble déjà exister. Utilisez [p]catdel pour supprimer une catégorie.")
            else:
                await self.bot.say("Vous devez ajouter une description rapide à votre catégorie.")
        else:
            await self.bot.say("Création de la catégorie par défaut 'URLONLY'\n*Placez des images dedans pour que le bot n'affiche que les URL plutôt que de les upload.*")
            self.img["CAT"]["URLONLY"] = {"NOM" : "URLONLY", "DESC" : "Seulement les URLs."}
            fileIO("data/stock/img.json", "save", self.img)
            await asyncio.sleep(1)
            await self.bot.say("Création de la catégorie par défaut 'AUTRES'\n*Les images sans catégories seront placés dedans.*")
            self.img["CAT"]["AUTRES"] = {"NOM" : "AUTRES", "DESC" : "Images sans catégories."}
            fileIO("data/stock/img.json", "save", self.img)
        

    @imgset.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def catdel(self, ctx, nom):
        """Retire une catégorie du module."""
        nom = nom.upper()
        if nom in self.img["CAT"]:
            if "AUTRES" not in self.img["CAT"]:
                self.img["CAT"]["AUTRES"] = {"NOM" : "AUTRES", "DESC" : "Images sans catégories."}
                fileIO("data/stock/img.json", "save", self.img)
            if "URLONLY" not in self.img["CAT"]:
                self.img["CAT"]["URLONLY"] = {"NOM" : "URLONLY", "DESC" : "Seulement les URLs."}
                fileIO("data/stock/img.json", "save", self.img)
            for image in self.img["IMG"]:
                if self.img["IMG"][image]["CAT"] == nom:
                    self.img["IMG"][image]["CAT"] = "AUTRES"
            del self.img["CAT"][nom]
            fileIO("data/stock/img.json", "save", self.img)
            await self.bot.say("**Votre catégorie {} à été retirée.**\n *Les images ayant cette catégorie sont déplacés dans 'AUTRES'.*".format(nom.title()))
        else:
            await self.bot.say("Cette catégorie n'existe pas. Utilisez [p]catadd pour l'ajouter.")
        
    @imgset.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def add(self, ctx, nom, cat, url):
        """Ajoute une image à la base de données.

        Vous pouvez créer des catégories avec [p]img cat"""
        cat = cat.upper()
        if cat in self.img["CAT"]:
            if nom not in self.img["IMG"]:
                filename = url.split('/')[-1]
                if ".gif" in filename:
                    await self.bot.say("*Vérifiez que l'image possède une taille suffisante pour ne pas être cachée par le logo 'GIF'.*")
                    await asyncio.sleep(0.5)
                if filename in os.listdir("data/stock/img/"):
                    exten = filename.split(".")[1]
                    nomsup = random.randint(1, 9999)
                    filename = filename.split(".")[0] + str(nomsup) + "." + exten
                try:
                    f = open(filename, 'wb')
                    f.write(request.urlopen(url).read())
                    f.close()
                    file = "data/stock/img/" + filename
                    os.rename(filename,file)
                    self.img["IMG"][nom] = {"NOM" : nom, "CHEMIN": file, "URL": url, "CAT": cat}
                    fileIO("data/stock/img.json", "save", self.img)
                    await self.bot.say("**Fichier {} enregistré localement**".format(filename))
                except Exception as e:
                    print("Erreur, impossible de télécharger l'image : {}".format(e))
                    await self.bot.say("Désolé, mais cette image ne peut pas être téléchargée.")
            else:
                await self.bot.say("Image déjà chargée.")
        else:
            await self.bot.say("Cette catégorie n'existe pas. Je vais vous envoyer une liste des catégories disponibles...")
            msg = ""
            for categorie in self.img["CAT"]:
                msg += "**{}** | *{}*\n".format(self.img["CAT"][categorie]["NOM"], self.img["CAT"][categorie]["DESC"])
            else:
                await self.bot.whisper(msg)

    @imgset.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def edit(self, ctx, nom, cat, url : str = None):
        """Permet d'éditer les données liés à une image. (Catégorie et URL)

        Si aucune URL n'est spécifiée, l'URL originale est conservée."""
        cat = cat.upper()
        if cat in self.img["CAT"]:
            if nom in self.img["IMG"]:
                if url == None:
                    url = self.img["IMG"][nom]["URL"]
                    await self.bot.say("URL conservée...")
                file = self.img["IMG"][nom]["CHEMIN"]
                self.img["IMG"][nom] = {}
                self.img["IMG"][nom] = {"NOM": nom, "CHEMIN": file, "URL": url, "CAT": cat}
                fileIO("data/stock/img.json", "save", self.img)
                await self.bot.say("**Données de {} édités**".format(nom))
            else:
                await self.bot.say("Ce nom n'est pas dans ma base de données")
        else:
            await self.bot.say("Cette catégorie n'existe pas. Je vais vous envoyer une liste des catégories disponibles...")
            msg = ""
            for categorie in self.img["CAT"]:
                msg += "**{}** | *{}*\n".format(self.img["CAT"][categorie]["NOM"], self.img["CAT"][categorie]["DESC"])
            else:
                await self.bot.whisper(msg)

    @imgset.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def delete(self, ctx, nom):
        """Supprime une image de la base de données."""
        if nom in self.img["IMG"]:
            chemin = self.img["IMG"][nom]["CHEMIN"]
            file = self.img["IMG"][nom]["CHEMIN"].split('/')[-1]
            splitted = "/".join(chemin.split('/')[:-1]) + "/"
            if file in os.listdir(splitted):
                os.remove(chemin)
                await self.bot.say("J'ai supprimé le fichier lié.")
            del self.img["IMG"][nom]
            await asyncio.sleep(0.5)
            await self.bot.say("Données supprimées.")
            fileIO("data/stock/img.json", "save", self.img)
        else:
            await self.bot.say("Cette image n'existe pas.")

    @imgset.command(pass_context=True)
    async def list(self, ctx, cat: str = None):
        """Liste les images présentes dans la base de données.

        La liste peut être triée par catégorie si spécifiée."""
        msg = ""
        if cat is None:
            msg += "__**Images enregistrées par catégories:**__\n"
            for categorie in self.img["CAT"]:
                msg += "\n" + "**{}**\n".format(self.img["CAT"][categorie]["NOM"])
                msg += "__Description:__ *{}*\n".format(self.img["CAT"][categorie]["DESC"])
                for image in self.img["IMG"]:
                    if self.img["IMG"][image]["CAT"] == categorie:
                        msg += "- {}\n".format(self.img["IMG"][image]["NOM"])
                    else:
                        pass
            else:
                await self.bot.whisper(msg)
        else:
            cat = cat.upper()
            msg += "__**Images ayant pour catégorie {}:**__\n".format(cat)
            msg += "__Description:__ *{}*\n".format(self.img["CAT"][cat]["DESC"])
            for image in self.img["IMG"]:
                if self.img["IMG"][image]["CAT"] == cat:
                    msg += "- {}\n".format(self.img["IMG"][image]["NOM"])
                else:
                    pass
            else:
                await self.bot.whisper(msg)

    async def check_msg(self, message):
        channel = message.channel
        if ":" in message.content:
            output = re.compile(':(.*?):', re.DOTALL |  re.IGNORECASE).findall(message.content)
            if output:
                for img in output:
                    if img in self.img["IMG"]:
                        if self.img["IMG"][img]["CAT"] != "URLONLY":
                            chemin = self.img["IMG"][img]["CHEMIN"]
                            url = self.img["IMG"][img]["URL"]
                            try:
                                await self.bot.send_file(channel, chemin)
                            except Exception as e:
                                print("Erreur, impossible d'upload l'image : {}".format(e))
                                print("Je vais envoyer l'URL liée à la place.")
                                if url != None:
                                    await self.bot.send_message(channel, url)
                                else:
                                    print("Je n'ai pas le lien non plus...")
                        else:
                            url = self.img["IMG"][img]["URL"]
                            if url != None:
                                await self.bot.send_message(channel, url)
                            else:
                                print("Image en catégorie 'URLONLY'.")
                    else:
                        pass
            else:
                pass
        else:
            pass
            

def check_folders():
    if not os.path.exists("data/stock"):
        print("Creation du fichier Stock...")
        os.makedirs("data/stock")

    if not os.path.exists("data/stock/img"):
        print("Creation du fichier de Stockage d'images...")
        os.makedirs("data/stock/img")

def check_files():
    
    if not os.path.isfile("data/stock/img.json"):
        print("Creation du fichier de stock img.json...")
        fileIO("data/stock/img.json", "save", default_img)

    if not os.path.isfile("data/stock/trg.json"):
        print("Creation du fichier de stock trg.json...")
        fileIO("data/stock/trg.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Stock(bot)
    bot.add_listener(n.check_msg, "on_message")
    bot.add_cog(n)
