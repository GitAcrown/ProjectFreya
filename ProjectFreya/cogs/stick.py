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
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import sys

#Freya Exclusive

default_img = {"IMG" : {}, "CAT" : {}}
memedir = "data/stock/memedir/"
imgdir = "data/stock/img/"

class Stock:
    """Permet de stocker des données en local pour des fonctions utiles."""

    def __init__(self, bot):
        self.bot = bot
        self.img = dataIO.load_json("data/stock/img.json")
        self.trg = dataIO.load_json("data/stock/trg.json")
        self.meme = dataIO.load_json("data/stock/meme.json")

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
        
    @imgset.command(name = "add", pass_context=True, no_pm=True)
    async def s_add(self, ctx, nom, cat, url):
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
                    await self.bot.send_file(ctx.message.channel, file)
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

    @imgset.command(name = "edit", pass_context=True, no_pm=True)
    async def s_edit(self, ctx, nom, cat, url : str = None):
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

    @imgset.command(name = "delete", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(kick_members=True)
    async def s_delete(self, ctx, nom):
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

    @imgset.command(name = "list", pass_context=True)
    async def s_list(self, ctx, cat: str = None):
        """Liste les images présentes dans la base de données.

        La liste peut être triée par catégorie si spécifiée."""
        msg = ""
        if cat is None:
            msg += "__**Images enregistrées par catégories:**__\n"
            for categorie in self.img["CAT"]:
                msg += "\n" + "**{}**\n".format(self.img["CAT"][categorie]["NOM"])
                msg += "*{}*\n".format(self.img["CAT"][categorie]["DESC"])
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
            msg += "*{}*\n".format(self.img["CAT"][cat]["DESC"])
            for image in self.img["IMG"]:
                if self.img["IMG"][image]["CAT"] == cat:
                    msg += "- {}\n".format(self.img["IMG"][image]["NOM"])
                else:
                    pass
            else:
                await self.bot.whisper(msg)

    #----------------- DETECTEUR -----------------------

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
                    elif img in self.meme:
                        chemin = self.meme[img]["CHEMIN"]
                        try:
                            await self.bot.send_file(channel, chemin)
                        except Exception as e:
                            print("Erreur, impossible d'upload l'image : {}".format(e))
                            print("Comme c'est un Meme, aucune URL n'est disponible.")
                            await self.bot.say("Je n'ai pas réussi à upload ce meme :( ")
                    else:
                        pass  
            else:
                pass
        else:
            pass

    #--------------- MEMES ----------------------

    @commands.group(pass_context=True)
    async def memeset(self, ctx):
        """Gestion des memes."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @memeset.command(pass_context=True)
    async def make(self, ctx, haut, bas, fichier, meme):
        """Crée un Meme.
        - Fichier = Nom du template à utiliser.
        - Meme = Nom du meme crée
        - Haut/Bas = Ce qui est marqué en haut et en bas. (Utilisez des guillemets)

        Vous pouvez laisser les guillemets vides pour garder vide le haut ou le bas."""
        fichier += ".jpg"
        fichierdir = memedir + fichier
        meme = meme.lower()
        if meme not in self.meme:
            if os.path.exists(fichierdir):
                try:
                    make_meme(haut, bas, fichierdir, meme)
                    name = meme + ".png"
                    namedir = imgdir + name
                    os.rename(name,namedir)
                    self.meme[meme] = {"NOM" : meme, "CHEMIN": namedir}
                    fileIO("data/stock/meme.json", "save", self.meme)
                    await self.bot.say("**Meme {} créé avec succès.**".format(meme))
                    await self.bot.send_file(ctx.message.channel, namedir)
                except Exception as e:
                    print("Erreur, impossible de créer le meme : {}".format(e))
                    await self.bot.say("Désolé mais cette opération à échoué.")
            else:
                await self.bot.say("Ce fichier n'existe pas.")      
        else:
            await self.bot.say("Meme déjà créé.")

    @memeset.command(pass_context=True)
    async def remove(self, ctx, nom):
        """Permet de retirer un meme crée"""
        fichier = imgdir + nom + ".png"
        if os.path.exists(fichier):
            os.remove(fichier)
            del self.meme[nom]
            await self.bot.say("J'ai supprimé ce meme.")
        else:
            await self.bot.say("Ce meme n'existe pas.")

    @memeset.command(pass_context=True)
    async def templates(self, ctx):
        """Donne une liste des templates disponibles."""
        msg = ""
        dispo = os.listdir(memedir)
        for file in dispo:
            msg += str(file[:-4]) + "\n"
        await self.bot.say(msg + "\n" + "*Utilisez '[p]memeset preview' pour prévisualiser un template*")

    @memeset.command(name = "list", pass_context=True)
    async def m_list(self, ctx):
        """Liste les memes disponibles."""
        msg = ""
        for meme in self.meme:
            msg += "- {}\n".format(self.meme[meme]["NOM"])
        else:
            await self.bot.whisper(msg)

    @memeset.command(pass_context=True)
    async def preview(self, ctx, nom):
        """Permet la preview d'un template."""
        fichier = nom + ".jpg"
        fichierdir = memedir + fichier
        if os.path.exists(fichierdir):
            try:
                await self.bot.say("**Upload de {} en cours...**".format(fichier))
                await self.bot.send_file(ctx.message.channel, fichierdir)
            except Exception as e:
                print("Erreur, impossible d'upload l'image : {}".format(e))
                await self.bot.say("Désolé, mais cette image ne peut pas être upload.")

    @memeset.command(name = "add", pass_context=True)
    async def m_add(self, ctx, nom, url):
        """Ajoute une image aux templates disponibles.

        - Une conversion en '.jpg' sera réalisée automatiquement.
        - Le template sera aussi enregistré dans les stickers (vierge)."""
        fichier = memedir + nom + ".jpg"
        if not os.path.exists(fichier):
            filename = url.split('/')[-1]
            if not ".jpg" in filename:
                await self.bot.say("*Conversion vers jpg...*")
                exten = filename.split(".")[1]
                filename = filename.replace(exten, 'jpg')
                await asyncio.sleep(0.5)
            try:
                f = open(filename, 'wb')
                f.write(request.urlopen(url).read())
                f.close()
                file = memedir + nom + ".jpg"
                os.rename(filename, file)
                await self.bot.say("**Template {} enregistré localement**".format(nom + ".jpg"))
                self.img["IMG"][nom] = {"NOM" : nom, "CHEMIN": file, "URL": url, "CAT": "AUTRES"}
                fileIO("data/stock/img.json", "save", self.img)
                await self.bot.say("*Ajouté dans les stickers, catégorie 'Autres'*".format(filename))
                await self.bot.send_file(ctx.message.channel, file)
            except Exception as e:
                print("Erreur, impossible de télécharger l'image : {}".format(e))
                await self.bot.say("Désolé, mais cette image ne peut pas être téléchargée.")
        else:
            await self.bot.say("Image déjà chargée.")

    @memeset.command(name = "delete", pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def m_delete(self, ctx, nom):
        """Supprime un template de la base de données."""
        fichier = memedir + nom + ".jpg"
        if os.path.exists(fichier):
            os.remove(fichier)
            await self.bot.say("J'ai supprimé le template.")
        else:
            await self.bot.say("Ce template n'existe pas.")

def make_meme(topString, bottomString, filename, memenom):

    img = Image.open(filename)
    imageSize = img.size

    # find biggest font size that works
    fontSize = int(imageSize[1]/5)
    font = ImageFont.truetype("ress/Impact.ttf", fontSize)
    topTextSize = font.getsize(topString)
    bottomTextSize = font.getsize(bottomString)
    while topTextSize[0] > imageSize[0]-20 or bottomTextSize[0] > imageSize[0]-20:
            fontSize = fontSize - 1
            font = ImageFont.truetype("ress/Impact.ttf", fontSize)
            topTextSize = font.getsize(topString)
            bottomTextSize = font.getsize(bottomString)

    # find top centered position for top text
    topTextPositionX = (imageSize[0]/2) - (topTextSize[0]/2)
    topTextPositionY = 0
    topTextPosition = (topTextPositionX, topTextPositionY)

    # find bottom centered position for bottom text
    bottomTextPositionX = (imageSize[0]/2) - (bottomTextSize[0]/2)
    bottomTextPositionY = imageSize[1] - bottomTextSize[1]
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)

    draw = ImageDraw.Draw(img)

    # draw outlines
    # there may be a better way
    outlineRange = int(fontSize/15)
    for x in range(-outlineRange, outlineRange+1):
            for y in range(-outlineRange, outlineRange+1):
                    draw.text((topTextPosition[0]+x, topTextPosition[1]+y), topString, (0,0,0), font=font)
                    draw.text((bottomTextPosition[0]+x, bottomTextPosition[1]+y), bottomString, (0,0,0), font=font)

    draw.text(topTextPosition, topString, (255,255,255), font=font)
    draw.text(bottomTextPosition, bottomString, (255,255,255), font=font)

    img.save(memenom + ".png")

def get_upper(somedata):
	'''
	Handle Python 2/3 differences in argv encoding
	'''
	result = ''
	try:
		result = somedata.decode("utf-8").upper()
	except:
		result = somedata.upper()
	return result

def get_lower(somedata):
	'''
	Handle Python 2/3 differences in argv encoding
	'''
	result = ''
	try:
		result = somedata.decode("utf-8").lower()
	except:
		result = somedata.lower()		

	return result



if __name__ == '__main__':

	args_len = len(sys.argv)
	topString = ''
	meme = 'standard'

	if args_len == 1:
		# no args except the launch of the script
		print('args plz')

	elif args_len == 2:
		# only one argument, use standard meme
		bottomString = get_upper(sys.argv[-1])

	elif args_len == 3:
		# args give meme and one line
		bottomString = get_upper(sys.argv[-1])
		meme = get_lower(sys.argv[1])

	elif args_len == 4:
		# args give meme and two lines
		topString = get_upper(sys.argv[-2])
		bottomString = get_upper(sys.argv[-1])
		meme = get_lower(sys.argv[1])
	else:
		# so many args
		# what do they mean
		# too intense
		print('to many argz')

	print(meme)	
	filename = str(meme)+'.jpg'
	make_meme(topString, bottomString, filename)	
            

def check_folders():
    if not os.path.exists("data/stock"):
        print("Creation du fichier Stock...")
        os.makedirs("data/stock")

    if not os.path.exists("data/stock/img"):
        print("Creation du fichier de Stockage d'images...")
        os.makedirs("data/stock/img")

    if not os.path.exists("data/stock/memedir"):
        print("Creation du fichier de Stockage de Memes...")
        os.makedirs("data/stock/memedir")

def check_files():
    
    if not os.path.isfile("data/stock/img.json"):
        print("Creation du fichier de stock img.json...")
        fileIO("data/stock/img.json", "save", default_img)

    if not os.path.isfile("data/stock/trg.json"):
        print("Creation du fichier de stock trg.json...")
        fileIO("data/stock/trg.json", "save", {})

    if not os.path.isfile("data/stock/meme.json"):
        print("Creation du fichier de stock meme.json...")
        fileIO("data/stock/meme.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Stock(bot)
    bot.add_listener(n.check_msg, "on_message")
    bot.add_cog(n)
