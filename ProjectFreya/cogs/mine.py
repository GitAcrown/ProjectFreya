import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import random
import logging
import asyncio
import os

#Freya Exclusive
default = {"CHANNELS" : [], "MINECHAN" : None, "MINEUR" : None, "SPAWNED": None, "COMPTEUR" : 0, "MINIMUM" : 250, "MAXIMUM" : 1000, "LIMITE" : 500}

class Mine:
    """Il est temps de partir à la mine..."""

    def __init__(self, bot):
        self.bot = bot
        self.sys = dataIO.load_json("data/mine/sys.json")
        self.inv = dataIO.load_json("data/mine/inv.json")
        self.mine_commun = [["Fer", "kg de fer", 18, 3],
                            ["Sel", "kg de sel", 12, 3],
                            ["Cuivre", "kg de cuivre", 22, 3]]
        self.mine_altern = [["Argent", "g d'argent", 34, 4],
                            ["Or", "g d'or", 48, 4],
                            ["Platine", "g de platine", 60, 4]]
        self.mine_rare = [["Rubis", "mg de rubis", 68, 5],
                          ["Saphire", "mg de saphires", 78, 5],
                          ["Diamant", "mg de diamants", 90, 5]]
        self.mine_urare = [["Tritium", "µg de tritium", 140, 6],
                           ["Plutonium", "µg de plutonium", 196, 6],
                           ["Antimatière", "µg d'antimatière", 450, 7]]

    @commands.command(pass_context=True, hidden=True)
    async def mine_debug(self, ctx):
        """Debug du module Mine"""
        minimum = self.sys["MINIMUM"]
        maximum = self.sys["MAXIMUM"]
        limite = self.sys["LIMITE"]
        compteur = self.sys["COMPTEUR"]
        minerai = None
        if self.sys["SPAWNED"] != None:
            minerai = self.sys["SPAWNED"][0]
            minechan = self.sys["MINECHAN"]
            minechan = self.bot.get_channel(minechan)
        mineur = self.sys["MINEUR"]
        msg = "**--DEBUG--**\n"
        msg += "Minimum : {}\n".format(minimum)
        msg += "Maximum : {}\n".format(maximum)
        msg += "Limite : {}\n".format(limite)
        msg += "Compteur : {}\n".format(compteur)
        if minerai is not None:
            msg += "Minerai **{}** sur *{}*\n".format(minerai, minechan.name)
        else:
            msg += "Aucun minage en cours"
        await self.bot.say(msg)

    @commands.group(pass_context=True)
    async def mineset(self, ctx):
        """Règle le module de minage."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @mineset.command(aliases = ["add"], pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def addchannel(self, ctx, channelid):
        """Permet de rajouter un channel où génerer des minerais."""
        if channelid not in self.sys["CHANNELS"]:
            self.sys["CHANNELS"].append(channelid)
            fileIO("data/mine/sys.json", "save", self.sys)
            await self.bot.say("J'ai bien pris en compte le chan demandé.")
        else:
            await self.bot.say("J'ai déjà enregistré ce channel.")

    @mineset.command(aliases = ["remove"], pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def remchannel(self, ctx, channelid):
        """Permet d'enlever un channel où l'ont génere les minerais."""
        if channelid in self.sys["CHANNELS"]:
            self.sys["CHANNELS"].remove(channelid)
            fileIO("data/mine/sys.json", "save", self.sys)
            await self.bot.say("J'ai bien pris en compte la suppresion du chan demandé.")
        else:
            await self.bot.say("Ce channel n'est pas dans mes registres.")

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def minimum(self, ctx, val):
        """Change le minimum de messages à compter avant la génération"""
        self.sys["MINIMUM"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le minimum est maintenant de {}".format(val))

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def maximum(self, ctx, val):
        """Change le maximum de messages à compter avant la génération"""
        self.sys["MAXIMUM"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le maximum est maintenant de {}".format(val))

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def compteur(self, ctx, val):
        """Change la valeur du compteur de messages avant génération"""
        self.sys["COMPTEUR"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le compteur est reglé à {} pour cette session".format(val))

    @commands.group(pass_context=True)
    async def mine(self, ctx):
        """Règle le module de minage."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @mine.command(pass_context=True, no_pm=True)
    async def register(self, ctx):
        """Permet de s'enregistrer en avance."""
        author = ctx.message.author
        if author.id not in self.inv:
            await self.bot.say("Vous n''avez pas de pioche ! Laissez-moi vous en donner une...")
            await asyncio.sleep(1)
            self.inv[author.id] = {}
            fileIO("data/mine/inv.json", "save", self.inv)
            await self.bot.say("Voilà ! Si vous voulez miner, vous pouvez dès à présent refaire la commande.")
        else:
            await self.bot.say("Vous êtes déjà inscrit !")

    @mine.command(pass_context=True, no_pm=True)
    async def pioche(self, ctx):
        """Permet le minage de l'item apparu sur le channel où la commande est réalisée."""
        author = ctx.message.author
        channel = ctx.message.channel
        if author.id in self.inv:
            if channel.id in self.sys["CHANNELS"]:
                if channel.id == self.sys["MINECHAN"]:
                    if self.sys["MINEUR"] is None:
                        self.sys["MINEUR"] = author.id
                        minerai = self.sys["SPAWNED"]
                        await self.bot.say("{} Vous commencez à miner **{}** !".format(author.mention, minerai[0]))
                        quant = random.randint(2, 8)
                        time = int(minerai[3])
                        await asyncio.sleep(time)
                        await self.bot.say("**Terminé !** {} *{}* a été rajouté à votre inventaire.".format(quant, minerai[1]))
                        punite = int(minerai[2])
                        fileIO("data/mine/sys.json", "save", self.sys)
                        if minerai[0] not in self.inv[author.id]:
                            self.inv[author.id][minerai[0]] = {"NOM" : minerai[0], "PHRASE" : minerai[1], "QUANTITE" : quant, "PUNITE" : punite}
                            fileIO("data/mine/inv.json", "save", self.inv)
                            await self.bot.whisper("J'ai rajouté ce nouveau minerai à votre inventaire : {}.".format(minerai[0]))
                        else:
                            self.inv[author.id][minerai[0]]["QUANTITE"] += quant
                            fileIO("data/mine/inv.json", "save", self.inv)
                        self.reset()
                    else:
                        await self.bot.say("Quelqu'un est en train de miner !")
                else:
                    await self.bot.say("Il n'y a rien sur ce channel.")
            else:
                await self.bot.say("Ce channel n'est pas dans ma base de donnée")
        else:
            await self.bot.say("Vous n''avez pas de pioche ! Laissez-moi vous en donner une...")
            await asyncio.sleep(1)
            self.inv[author.id] = {}
            fileIO("data/mine/inv.json", "save", self.inv)
            await self.bot.say("Voilà ! Si vous voulez miner, vous pouvez dès à présent refaire la commande.")

    @mine.command(pass_context=True, no_pm=True)
    async def sell(self, ctx, quant : int, item : str):
        """Permet de vendre un item en fonction de sa valeur."""
        item = item.title()
        author = ctx.message.author
        bank = self.bot.get_cog('Economy').bank
        if author.id in self.inv:
            if item in self.inv[author.id]:
                if quant <= self.inv[author.id][item]["QUANTITE"]:
                    if bank.account_exists(author):
                        vente = self.inv[author.id][item]["PUNITE"] * quant
                        self.inv[author.id][item]["QUANTITE"] -= quant
                        bank.deposit_credits(author, vente)
                        await self.bot.say("Vous venez de vendre {} **{}**. Vous obtenez donc {}§".format(quant, item, vente))
                        fileIO("data/mine/inv.json", "save", self.inv)
                    else:
                        await self.bot.say("Vous n'avez pas de compte bancaire (Wtf ?)")
                else:
                    await self.bot.say("Vous n'avez pas cette quantité de cet item.")
            else:
                await self.bot.say("Vous n'avez pas cet item.")
        else:
            await self.bot.say("Votre inventaire est vide.")

    @mine.command(pass_context=True, no_pm=True)
    async def sellall(self, ctx):
        """Permet la vente de l'ensemble des items possédés."""
        author = ctx.message.author
        bank = self.bot.get_cog('Economy').bank
        msg = "__**Voici vos ventes :**__\n"
        if author.id in self.inv:
            if bank.account_exists(author):
                for item in self.inv[author.id]:
                    vente = self.inv[author.id][item]["PUNITE"] * self.inv[author.id][item]["QUANTITE"]
                    before = self.inv[author.id][item]["QUANTITE"]
                    self.inv[author.id][item]["QUANTITE"] = 0
                    bank.deposit_credits(author, vente)
                    msg += "Vous venez de vendre {} **{}**. Vous obtenez donc {}§\n".format(before, item, vente)
                else:
                    fileIO("data/mine/inv.json", "save", self.inv)
                    await self.bot.say(msg)
            else:
                await self.bot.say("Vous n'avez pas de compte bancaire.")
        else:
            await self.bot.say("Vous n'êtes pas inscrit.")

    @mine.command(pass_context=True)
    async def inventaire(self, ctx):
        """Montre votre inventaire de minerais minés"""
        author = ctx.message.author
        msg = "__**Voici votre inventaire** {}:__\n".format(author.mention)
        if author.id in self.inv:
            if len(self.inv[author.id]) > 0:
                for item in self.inv[author.id]:
                    msg += "{} **{}** | *{}*§ l'unité\n".format(self.inv[author.id][item]["QUANTITE"], self.inv[author.id][item]["NOM"], self.inv[author.id][item]["PUNITE"])
                else:
                    msg += "-------------"
                    await self.bot.whisper(msg)
            else:
                await self.bot.say("Vous n'avez rien !")
        else:
            await self.bot.say("Votre inventaire est vide.")

    @mine.command(pass_context=True)
    async def infos(self, ctx):
        """Affiche des informations sur les minerais disponibles."""
        msg = "__**Minerais disponibles :**__\n" + "\n"
        msg += "**------ COMMUNS ------**\n"
        msg += "*Sel*, 12§ l'unité\n"
        msg += "*Fer*, 18§ l'unité\n"
        msg += "*Cuivre*, 22§ l'unité\n"
        msg += "\n"
        msg += "**---- PEU COMMUNS ----**\n"
        msg += "*Argent*, 34§ l'unité\n"
        msg += "*Or*, 48§ l'unité\n"
        msg += "*Platine*, 60§ l'unité\n"
        msg += "\n"
        msg += "**------- RARES -------**\n"
        msg += "*Rubis*, 68§ l'unité\n"
        msg += "*Saphire*, 78§ l'unité\n"
        msg += "*Diamant*, 90§ l'unité\n"
        msg += "\n"
        msg += "**---- TRES RARES ----**\n"
        msg += "*Tritium*, 140§ l'unité\n"
        msg += "*Plutonium*, 196§ l'unité\n"
        msg += "*Antimatière*, 450§ l'unité\n"
        msg += "\n"
        msg += "*Il y a environ :*\n- 50% de chance de tomber sur un commun\n- 30% de chance pour peu commun\n- 15% de chance pour rare\n- 5% de chance pour très rare"
        await self.bot.whisper(msg)
        
    def reset(self):
        self.sys["MINEUR"] = None
        self.sys["MINECHAN"] = None
        self.sys["SPAWNED"] = None
        minimum = self.sys["MINIMUM"]
        maximum = self.sys["MAXIMUM"]
        self.sys["COMPTEUR"] = 0
        newcounter = random.randint(minimum, maximum)
        self.sys["LIMITE"] = newcounter
        fileIO("data/mine/sys.json", "save", self.sys)

    def gen_mine(self):
        aleat = random.randint(0, 11)
        if aleat < 5:
            choix = random.choice(self.mine_commun)
            return choix
        elif aleat >= 5 and aleat < 8:
            choix = random.choice(self.mine_altern)
            return choix
        elif aleat >= 8 and aleat < 10:
            choix = random.choice(self.mine_rare)
            return choix
        else:
            choix = random.choice(self.mine_urare)
            return choix

    async def counter(self, message):
        if self.sys["MINEUR"] is None: #Si il n'y a pas de minage
            self.sys["COMPTEUR"] += 1 #On ajoute 1 au compteur
            fileIO("data/mine/sys.json", "save", self.sys)
            if self.sys["COMPTEUR"] == self.sys["LIMITE"]: #Si le compteur atteint la limite
                minechan = random.choice(self.sys["CHANNELS"]) #On choisi un channel au hasard
                self.sys["MINECHAN"] = minechan #On enregistre l'ID du channel
                channel = self.bot.get_channel(minechan) #On obtient le channel lié à l'ID 
                minerai = self.gen_mine() #On génère un minerai
                self.sys["SPAWNED"] = minerai #On met le minerai dans la mémoire
                await self.bot.send_message(channel, "**{}** vient d'apparaitre ! Faîtes [p]mine pioche pour miner !".format(minerai[0])) #On fait spawner le minerai généré (en msg)
                fileIO("data/mine/sys.json", "save", self.sys)
            elif self.sys["COMPTEUR"] == self.sys["LIMITE"] + 50:
                await self.bot.send_message(channel, "**{}** est toujours sur le channel ! Faîtes [p]mine pioche pour miner !".format(minerai[0]))
            elif self.sys["COMPTEUR"] == self.sys["LIMITE"] + 100:
                await self.bot.send_message(channel, "**{}** n'est toujours pas miné ! Faîtes [p]mine pioche pour miner !".format(minerai[0]))
            else:
                pass
        else:
            pass

def check_folders():
    folders = ("data", "data/mine/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    if not os.path.isfile("data/mine/sys.json"):
        print("Creating empty data.json...")
        fileIO("data/mine/sys.json", "save", default)

    if not os.path.isfile("data/mine/inv.json"):
        print("Creating empty data.json...")
        fileIO("data/mine/inv.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Mine(bot)
    bot.add_listener(n.counter, 'on_message')
    bot.add_cog(n)    
