import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import random
import os
import logging
import asyncio
try:
    from tabulate import tabulate
    tabulateAvailable = True
except:
    tabulateAvailable = False

#Freya Exclusive

class Market:
    """Marché virtuel de TdK"""

    def __init__(self, bot):
        self.bot = bot
        self.shop = dataIO.load_json("data/market/shop.json")
        self.client = dataIO.load_json("data/market/client.json")

    #-------------- MARKET --------------#

    @commands.group(name="market", pass_context=True)
    async def _shop(self, ctx):
        """Gestion de magasin"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @_shop.command(pass_context=True)
    async def new(self, ctx, nom: str):
        """Création de son marché personnel.

        Le nom doit être en un seul nom et ne doit pas commencer par un chiffre."""
        author = ctx.message.author
        nom = nom.title()
        if not self.shop_exists(nom):
            if not self.already_in(author.id):
                self.shop[nom] = {"NOM" : nom, "PROP" : author.id, "ITEMS" : {}, "BANK": 0, "OPEN" : False}
                fileIO("data/market/shop.json", "save", self.shop)
                await self.bot.say("Votre boutique **{}** à été crée avec succès ! Vous pouvez ajouter des items avec *market edit*.".format(nom))
            else:
                await self.bot.say("Vous avez déjà une boutique.")
        else:
            await self.bot.say("Cette boutique existe déjà.")

    @_shop.command(pass_context=True)
    async def name(self, ctx, nom: str):
        """Changement du nom de votre boutique.

        Le nom doit être en un seul nom et ne doit pas commencer par un chiffre."""
        author = ctx.message.author
        nom = nom.title()
        if not self.shop_exists(nom):
            before = self.user_shop(author.id)
            if self.already_in(author.id):
                self.shop[nom] = {"NOM" : nom, "PROP" : author.id, "ITEMS" : self.shop[before]["ITEMS"] , "BANK": self.shop[before]["BANK"] , "OPEN" : self.shop[before]["OPEN"]}
                del self.shop[before]
                fileIO("data/market/shop.json", "save", self.shop)
                await self.bot.say("Votre boutique, maintenant **{}** à été éditée avec succès !".format(nom))
            else:
                await self.bot.say("Vous n'avez pas de boutique.")
        else:
            await self.bot.say("Cette boutique existe déjà.")

    @_shop.command(hidden = True, pass_context=True)
    async def quit(self, ctx):
        """Permet de fermer son magasin et d'effacer ce qu'il contient."""
        author = ctx.message.author
        if self.already_in(author.id):
            shop = self.user_shop(author.id)
            del self.shop[shop]
            await self.bot.say("Boutique supprimée.")
        else:
            await self.bot.say("Vous n'avez pas de magasin.")

    @_shop.command(pass_context=True)
    async def edit(self, ctx, nom: str, prix: int, categorie: str = None):
        """Edite un item. Si l'item n'existe pas, il sera crée automatiquement.

        Si aucune catégorie n'est spécifiée, elle sera dans 'Autres'."""
        nom = nom.lower()
        if categorie:
            categorie = categorie.title()
        author = ctx.message.author
        if self.already_in(author.id):
            shop = self.user_shop(author.id)
            self.edit_item(shop, nom, prix, categorie)
            await self.bot.say("**{}** | *{}*§ | *{}* \nItem créé pour *{}*".format(nom, prix, categorie, shop))
            fileIO("data/market/shop.json", "save", self.shop)
        else:
            await self.bot.say("Vous ne possédez aucune boutique.")

    @_shop.command(name = "del", pass_context=True)
    async def _del(self, ctx, nom: str):
        """Supprime un item de votre boutique."""
        author = ctx.message.author
        nom = nom.title()
        if self.already_in(author.id):
            shop = self.user_shop(author.id)
            if self.item_exists(shop, nom):
                del self.shop[shop]["ITEMS"][nom]
                await self.bot.say("Item supprimé.")
                fileIO("data/market/shop.json", "save", self.shop)
            else:
                await self.bot.say("Cet item n'existe pas.")
        else:
            await self.bot.say("Vous n'avez pas de boutique.")

    @_shop.command(pass_context=True)
    async def statut(self, ctx, stat: bool):
        """Ouvre ou Ferme votre boutique (True/False)"""
        author = ctx.message.author
        if self.already_in(author.id):
            shop = self.user_shop(author.id)
            self.shop[shop]["OPEN"] = stat
            if self.shop[shop]["OPEN"]:
                await self.bot.say("Boutique **{}** Ouvert".format(shop))
            else:
                await self.bot.say("Boutique **{}** Fermé".format(shop))
        else:
            await self.bot.say("Vous n'êtes pas inscrit.")
        fileIO("data/market/shop.json", "save", self.shop)

    @_shop.command(pass_context=True)
    async def recolte(self, ctx):
        """Permet de récolter l'argent présente dans les caisses."""
        author = ctx.message.author
        server = ctx.message.server
        if self.already_in(author.id):
            if server != None:
                bank = self.bot.get_cog('Economy').bank
                if bank.account_exists(author):
                    shop = self.user_shop(author.id)
                    caisses = self.shop[shop]["BANK"]
                    await asyncio.sleep(1)
                    await self.bot.whisper("Vous avez dans vos caisses *{}*§. Combien voulez-vous retirer ?".format(caisses))
                    reply = await self.bot.wait_for_message(timeout=15, author=author)
                    if not reply:
                        await self.bot.whisper("Aucune réponse. Recolte annulée.")
                    else:
                        reply = int(reply.content)
                        if reply <= self.shop[shop]["BANK"]:
                            await self.bot.whisper("Je vais vider {}§ de vos caisses et vous les mettre sur votre compte bancaire.".format(reply))
                            bank.deposit_credits(author, reply)
                            self.shop[shop]["BANK"] -= reply
                            money = bank.get_balance(author)
                            await self.bot.whisper("Fait. Vous avez {}§ sur votre compte bancaire.".format(money))
                            fileIO("data/market/shop.json", "save", self.shop)
                        else:
                            await self.bot.whisper("Vous ne pouvez pas retirer plus que ce qu'il y a dans votre caisse.")
                else:
                    await self.bot.say("Vous n'avez pas de compte bancaire.")
            else:
                await self.bot.say("Je suis désolé mais cette commande doit être lancée en publique pour que je puisse savoir depuis quel serveur vous le faîtes.")
        else:
            await self.bot.say("Vous n'êtes pas inscrit dans l'Economie Commune.")

    @_shop.command(pass_context=True)
    async def items(self, ctx):
        """Donne l'inventaire de la boutique."""
        author = ctx.message.author
        if self.already_in(author.id):
            shop = self.user_shop(author.id)
            column1 = [subdict["nom"] for subdict in self.shop[shop]["ITEMS"].values()]
            column2 = [subdict["prix"] for subdict in self.shop[shop]["ITEMS"].values()]
            column3 = [subdict["cat"] for subdict in self.shop[shop]["ITEMS"].values()]
            m = list(zip(column1, column2, column3))
            m.sort()
            t = tabulate(m, headers=["Nom", "Prix", "Catégorie"])
            header = "```"
            header += self.bordered("S T O C K")
            header += "```"
            await self.bot.whisper(header + "```Python\n" + t + "```")
        else:
            await self.bot.say("Vous n'avez pas de boutique.")

    #-------------- CLIENT --------------#

    @commands.group(name="clt", pass_context=True)
    async def _client(self, ctx):
        """Gestion de magasin"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @_client.command(pass_context=True)
    async def register(self, ctx):
        """Enregistre un compte à l'Economie Commune (Pour avoir un inventaire personnel)"""
        author = ctx.message.author
        if not self.user_registered(author.id):
            self.client[author.id] = {"NOM" : author.name, "ID" : author.id, "ITEMS" : {}}
            fileIO("data/market/client.json", "save", self.client)
            await self.bot.say("Vous êtes maintenant enregistré dans l'Economie Commune.")
        else:
            await self.bot.say("Vous êtes déjà enregistré.")

    @_client.command(pass_context=True)
    async def buy(self, ctx, boutique: str, item: str, quant:int = None):
        """Achete un item dans une boutique."""
        if quant == None:
            quant = 1
        boutique = boutique.title()
        item = item.lower()
        author = ctx.message.author
        server = ctx.message.server
        bank = self.bot.get_cog('Economy').bank
        if self.user_registered(author.id):
            if self.shop_exists(boutique):
                if self.item_exists(boutique, item):
                    prix = self.shop[boutique]["ITEMS"][item]["prix"] * quant
                    if bank.account_exists(author):
                        if bank.can_spend(author, prix):
                            propid = self.shop[boutique]["PROP"]
                            prop = server.get_member(propid)
                            await self.bot.send_message(prop, "*{}* vient d'acheter *{}* exemplaires de **{}** dans votre boutique.".format(author.name, quant, item))
                            bank.withdraw_credits(author, prix)
                            if item not in self.client[author.id]["ITEMS"]:
                                cat = self.shop[boutique]["ITEMS"][item]["cat"]
                                self.shop[boutique]["BANK"] += prix
                                self.client[author.id]["ITEMS"][item] = {"nom" : item, "qt" : quant, "cat" : cat}
                                await self.bot.say("Item acheté et ajouté à votre inventaire.")
                                fileIO("data/market/client.json", "save", self.client)
                            else:
                                self.shop[boutique]["BANK"] += prix
                                self.client[author.id]["ITEMS"][item]["qt"] += quant
                                await self.bot.say("Item acheté et ajouté à votre inventaire.")
                                fileIO("data/market/client.json", "save", self.client)
                        else:
                            await self.bot.say("Vous n'avez pas assez d'argent.")
                    else:
                        await self.bot.say("Vous n'avez pas de compte bancaire (Wtf ?)")
                else:
                    await self.bot.say("Cet item n'existe pas.")
            else:
                await self.bot.say("Cette boutique n'existe pas.")
        else:
            await self.bot.say("Vous n'êtes pas enregistré.")

    @_client.command(pass_context=True)
    async def sac(self, ctx):
        """Affiche ce que vous avez."""
        author = ctx.message.author
        id = author.id
        if self.user_registered(id):
            column1 = [subdict["nom"] for subdict in self.client[id]["ITEMS"].values()]
            column2 = [subdict["qt"] for subdict in self.client[id]["ITEMS"].values()]
            column3 = [subdict["cat"] for subdict in self.client[id]["ITEMS"].values()]
            m = list(zip(column1, column2, column3))
            m.sort()
            t = tabulate(m, headers=["Nom", "Quantité", "Catégorie"])
            header = "```"
            header += self.bordered("I N V E N T A I R E")
            header += "```"
            await self.bot.whisper(header + "```\n" + t + "```")
        else:
            await self.bot.say("Vous n'êtes pas enregistré. Faîtes *clt register* pour s'enregistrer.")

    @_client.command(pass_context=True)
    async def gift(self, ctx, item, user : discord.Member):
        """Permet d'offrir un item à un autre membre."""
        author = ctx.message.author
        item = item.lower()
        if self.user_registered(author.id):
            if self.user_registered(user.id):
                if item in self.client[author.id]["ITEMS"]:
                    if self.client[author.id]["ITEMS"][item]["qt"] > 1:
                        if item in self.client[user.id]["ITEMS"]:
                            self.client[author.id]["ITEMS"][item]["qt"] -= 1
                            self.client[user.id]["ITEMS"][item]["qt"] += 1
                            await self.bot.say("*{}* vient d'obtenir un exemplaire supplémentaire de **{}** venant de *{}* !".format(user.name, item, author.name))
                            fileIO("data/market/client.json", "save", self.client)
                        else:
                            self.client[author.id]["ITEMS"][item]["qt"] -= 1
                            shop = self.find_item(item)
                            cat = self.shop[shop]["ITEMS"][item]["cat"]
                            self.client[user.id]["ITEMS"][item] = {"nom" : item, "qt" : 1, "cat" : cat}
                            await self.bot.say("*{}* vient d'obtenir un exemplaire de **{}** venant de *{}* !".format(user.name, item, author.name))
                            fileIO("data/market/client.json", "save", self.client)
                    else:
                        if item in self.client[user.id]["ITEMS"]:
                            del self.client[author.id]["ITEMS"][item]
                            self.client[user.id]["ITEMS"][item]["qt"] += 1
                            await self.bot.say("*{}* vient d'obtenir un exemplaire supplémentaire de **{}** venant de *{}* !".format(user.name, item, author.name))
                            fileIO("data/market/client.json", "save", self.client)
                        else:
                            del self.client[author.id]["ITEMS"][item]
                            shop = self.find_item(item)
                            cat = self.shop[shop]["ITEMS"][item]["cat"]
                            self.client[user.id]["ITEMS"][item] = {"nom" : item, "qt" : 1, "cat" : cat}
                            await self.bot.say("*{}* vient d'obtenir un exemplaire de **{}** venant de *{}* !".format(user.name, item, author.name))
                            fileIO("data/market/client.json", "save", self.client)
                else:
                    await self.bot.say("Cet item n'est pas dans votre inventaire.")
            else:
                await self.bot.say("L'utilisateur n'est pas enregistré.")
        else:
            await self.bot.say("Vous n'êtes pas enregistré.")

    @_client.command(pass_context=True)
    async def find(self, ctx, item):
        """Permet de trouver dans quelle boutique est vendu un item."""
        item = item.lower()
        shop = self.find_shop(item)
        if shop:
            await self.bot.say("L'item recherché **{}** se trouve dans *{}*".format(item, shop))
        else:
            await self.bot.say("Cet item ne semble pas exister.")
                                                       
    def shop_exists(self, nom):
        if nom in self.shop:
            return True
        else:
            return False

    def user_shop(self, id):
        for nom in self.shop:
            if id == self.shop[nom]["PROP"]:
                return self.shop[nom]["NOM"]
            else:
                pass

    def already_in(self, id):
        for nom in self.shop:
            if id == self.shop[nom]["PROP"]:
                return True
            else:
                pass

    def item_exists(self, shop, name):
        for item in self.shop[shop]["ITEMS"]:
            if name == self.shop[shop]["ITEMS"][item]["nom"]:
                return True
            else:
                pass

    def find_shop(self, name):
        for shop in self.shop:
            for item in self.shop[shop]["ITEMS"]:
                if name == self.shop[shop]["ITEMS"][item]["nom"]:
                    return self.shop[shop]["NOM"]
                else:
                    pass

    def edit_item(self, shop, name, prix, cat = None):
        if cat == None:
            cat = "Autres"
        if self.shop_exists(shop):
            if not self.item_exists(shop, name):
                self.shop[shop]["ITEMS"][name] = {"nom" : name, "prix" : prix, "cat" : cat}
                fileIO("data/market/shop.json", "save", self.shop)
            else:
                self.shop[shop]["ITEMS"][name] = {}
                self.shop[shop]["ITEMS"][name] = {"nom" : name, "prix" : prix, "cat" : cat}
                fileIO("data/market/shop.json", "save", self.shop)
        else:
            return False

    def user_registered(self, id):
        if id in self.client:
            return True
        else:
            return False

    def bordered(self, text):
        lines = text.splitlines()
        width = max(len(s) for s in lines)
        res = ["┌" + "─" * width + "┐"]
        for s in lines:
            res.append("│" + (s + " " * width)[:width] + "│")
        res.append("└" + "─" * width + "┘")
        return "\n".join(res)
                

def check_folders():
    folders = ("data", "data/market/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    if not os.path.isfile("data/market/shop.json"):
        print("Creating empty data.json...")
        fileIO("data/market/shop.json", "save", {})

    if not os.path.isfile("data/market/client.json"):
        print("Creating empty data.json...")
        fileIO("data/market/client.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Market(bot)
    bot.add_cog(n) 
