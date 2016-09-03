import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO, fileIO
from collections import namedtuple, defaultdict
from datetime import datetime
from random import randint
from copy import deepcopy
from .utils import checks
from __main__ import send_cmd_help
import os
import time
import logging

#Modifié

default_settings = {"BOOST" : 1, "PAYDAY_TIME" : 86400, "PAYDAY_CREDITS" : 150, "SLOT_MIN" : 5, "SLOT_MAX" : 500, "SLOT_TIME" : 120}

slot_payouts = """Gains possibles dans la machine:
    :two: :two: :six: Offre * 5000
    :four_leaf_clover: :four_leaf_clover: :four_leaf_clover: +1000
    :cherries: :cherries: :cherries: +800
    :two: :six: Offre * 4
    :cherries: :cherries: Offre * 3

    Trois symboles: +500
    Deux symboles: Offre * 2"""

class BankError(Exception):
    pass

class AccountAlreadyExists(BankError):
    pass

class NoAccount(BankError):
    pass

class InsufficientBalance(BankError):
    pass

class NegativeValue(BankError):
    pass

class SameSenderAndReceiver(BankError):
    pass

class Bank:
    def __init__(self, bot, file_path):
        self.accounts = dataIO.load_json(file_path)
        self.bot = bot

    def create_account(self, user):
        server = user.server
        if not self.account_exists(user):
            if server.id not in self.accounts:
                self.accounts[server.id] = {}
            if user.id in self.accounts: # Legacy account
                balance = self.accounts[user.id]["balance"]
            else:
                balance = 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            account = {"name" : user.name, "balance" : balance,
            "created_at" : timestamp}
            self.accounts[server.id][user.id] = account
            self._save_bank()
            return self.get_account(user)
        else:
            raise AccountAlreadyExists()

    def account_exists(self, user):
        try:
            self._get_account(user)
        except NoAccount:
            return False
        return True

    def withdraw_credits(self, user, amount):
        server = user.server

        if amount < 0:
            raise NegativeValue()

        account = self._get_account(user)
        if account["balance"] >= amount:
            account["balance"] -= amount
            self.accounts[server.id][user.id] = account
            self._save_bank()
        else:
            raise InsufficientBalance()

    def deposit_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] += amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def set_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] = amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def transfer_credits(self, sender, receiver, amount):
        server = sender.server
        if amount < 0:
            raise NegativeValue()
        if sender is receiver:
            raise SameSenderAndReceiver()
        if self.account_exists(sender) and self.account_exists(receiver):
            sender_acc = self._get_account(sender)
            if sender_acc["balance"] < amount:
                raise InsufficientBalance()
            self.withdraw_credits(sender, amount)
            self.deposit_credits(receiver, amount)
        else:
            raise NoAccount()

    def can_spend(self, user, amount):
        account = self._get_account(user)
        if account["balance"] >= amount:
            return True
        else:
            return False

    def wipe_bank(self, server):
        self.accounts[server.id] = {}
        self._save_bank()

    def get_server_accounts(self, server):
        if server.id in self.accounts:
            raw_server_accounts = deepcopy(self.accounts[server.id])
            accounts = []
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
            return accounts
        else:
            return []

    def get_all_accounts(self):
        accounts = []
        for server_id, v in self.accounts.items():
            server = self.bot.get_server(server_id)
            if server is None:# Servers that have since been left will be ignored
                continue      # Same for users_id from the old bank format
            raw_server_accounts = deepcopy(self.accounts[server.id])
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
        return accounts

    def get_balance(self, user):
        account = self._get_account(user)
        return account["balance"]

    def get_account(self, user):
        acc = self._get_account(user)
        acc["id"] = user.id
        acc["server"] = user.server
        return self._create_account_obj(acc)

    def _create_account_obj(self, account):
        account["member"] = account["server"].get_member(account["id"])
        account["created_at"] = datetime.strptime(account["created_at"],
                                                  "%Y-%m-%d %H:%M:%S")
        Account = namedtuple("Account", "id name balance "
                             "created_at server member")
        return Account(**account)

    def _save_bank(self):
        dataIO.save_json("data/economy/bank.json", self.accounts)

    def _get_account(self, user):
        server = user.server
        try:
            return deepcopy(self.accounts[server.id][user.id])
        except KeyError:
            raise NoAccount()

class Economy:
    """Soyez riche virtuellement !"""

    def __init__(self, bot):
        global default_settings
        self.bot = bot
        self.bank = Bank(bot, "data/economy/bank.json")
        self.settings = fileIO("data/economy/settings.json", "load")
        if "PAYDAY_TIME" in self.settings: #old format
            default_settings = self.settings
            self.settings = {}
        self.settings = defaultdict(lambda: default_settings, self.settings)
        self.payday_register = defaultdict(dict)
        self.slot_register = defaultdict(dict)

    @commands.group(name="bank", pass_context=True)
    async def _bank(self, ctx):
        """Opérations bancaires"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_bank.command(pass_context=True, no_pm=True, hidden=True) #Inutile depuis MAJ "auto_register"
    async def register(self, ctx):
        """Enregistre un compte dans Bank"""
        user = ctx.message.author
        try:
            account = self.bank.create_account(user)
            await self.bot.say("{} Compte ouvert. Vous avez: {}§".format(user.mention,
                account.balance))
        except AccountAlreadyExists:
            await self.bot.say("{} Tu as déjà un compte Bank.".format(user.mention))

    async def auto_register(self, message): #Enregistre automatiquement
        user = message.author
        server = message.server
        if server != None:
            try:
                account = self.bank.create_account(user)
            except AccountAlreadyExists:
                pass
        else:
            pass

    @_bank.command(pass_context=True)
    async def balance(self, ctx, user : discord.Member=None):
        """Montre l'argent possédé par quelqu'un.

        Par défaut, son argent."""
        if not user:
            user = ctx.message.author
            try:
                await self.bot.say("{} Vous avez: {}§".format(user.mention, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("{} Vous n'avez pas de compte chez Bank. Tapez {}bank register pour en ouvrir un.".format(user.mention, ctx.prefix))
        else:
            try:
                await self.bot.say("{} possède {}§".format(user.name, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("Cet utilisateur ne possède pas de compte Bank.")

    @_bank.command(pass_context=True)
    async def transfer(self, ctx, user : discord.Member, sum : int):
        """Transfert des crédits d'un utilisateur à un autre. (Taxe de 4%)"""
        author = ctx.message.author
        mult = sum * 0.96
        sum = round(mult)
        try:
            self.bank.transfer_credits(author, user, sum)
            logger.info("{}({}) transferred {} credits to {}({})".format(
                author.name, author.id, sum, user.name, user.id))
            await self.bot.say("{} crédits ont été transférés au compte de {}. (Taxe de 4%)".format(sum, user.name))
        except NegativeValue:
            await self.bot.say("Vous avez besoin de transférer au moins 1 crédit.")
        except SameSenderAndReceiver:
            await self.bot.say("Vous ne pouvez pas transférer des crédits à vous-même.")
        except InsufficientBalance:
            await self.bot.say("Vous n'avez pas cette somme dans votre compte.")
        except NoAccount:
            await self.bot.say("Cet utilisateur ne possède pas de compte.")

    @_bank.command(name="set", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set(self, ctx, user : discord.Member, sum : int):
        """Change la valeur d'un compte

        Admin/Proprio seulement."""
        author = ctx.message.author
        try:
            self.bank.set_credits(user, sum)
            logger.info("{}({}) set {} credits to {} ({})".format(author.name, author.id, str(sum), user.name, user.id))
            await self.bot.say("{} possède maintenant {}".format(user.name, str(sum)))
        except NoAccount:
            await self.bot.say("Cet utilisateur ne possède pas de compte.")

    @commands.command(pass_context=True, no_pm=True)
    async def rjd(self, ctx): # TODO
        """Pour avoir quelques crédits"""
        author = ctx.message.author
        server = author.server
        id = author.id
        sum = self.settings[server.id]["PAYDAY_CREDITS"] * self.settings[server.id]["BOOST"]
        if self.bank.account_exists(author):
            if id in self.payday_register[server.id]:
                seconds = abs(self.payday_register[server.id][id] - int(time.perf_counter()))
                if seconds  >= self.settings[server.id]["PAYDAY_TIME"]:
                    self.bank.deposit_credits(author, sum)
                    self.payday_register[server.id][id] = int(time.perf_counter())
                    await self.bot.say("{} Voilà quelques crédits ! (+{}§)".format(author.mention, str(sum)))
                else:
                    await self.bot.say("{} Trop tôt, il faudra attendre {}.".format(author.mention, self.display_time(self.settings[server.id]["PAYDAY_TIME"] - seconds)))
            else:
                self.payday_register[server.id][id] = int(time.perf_counter())
                self.bank.deposit_credits(author, sum)
                await self.bot.say("{} Voilà quelques crédits. (+{}§)".format(author.mention, str(sum)))
        else:
            await self.bot.say("{} Vous avez besoin d'un compte. tapez {}bank register pour en ouvrir un.".format(author.mention, ctx.prefix))

    

    @commands.group(pass_context=True)
    async def leaderboard(self, ctx):
        """Top par serveur ou global

        Par défaut le serveur"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._server_leaderboard)

    @leaderboard.command(name="server", pass_context=True)
    async def _server_leaderboard(self, ctx, top : int=10):
        """Poste un top des personnes les plus riche

        par défaut top 10""" #Originally coded by Airenkun - edited by irdumb
        server = ctx.message.server
        if top < 1:
            top = 10
        bank_sorted = sorted(self.bank.get_server_accounts(server),
         key=lambda x: x.balance, reverse=True)
        if len(bank_sorted) < top:
            top = len(bank_sorted)
        topten = bank_sorted[:top]
        highscore = ""
        place = 1
        for acc in topten:
            highscore += str(place).ljust(len(str(top))+1)
            highscore += (acc.name+" ").ljust(23-len(str(acc.balance)))
            highscore += str(acc.balance) + "\n"
            place += 1
        if highscore:
            if len(highscore) < 1985:
                await self.bot.say("```py\n"+highscore+"```")
            else:
                await self.bot.say("Trop gros pour être affiché.")
        else:
            await self.bot.say("Aucun compte à afficher.")

    @leaderboard.command(name="global")
    async def _global_leaderboard(self, top : int=10):
        """Affiche le top global mutli-serveur"""
        if top < 1:
            top = 10
        bank_sorted = sorted(self.bank.get_all_accounts(),
         key=lambda x: x.balance, reverse=True)
        unique_accounts = []
        for acc in bank_sorted:
            if not self.already_in_list(unique_accounts, acc):
                unique_accounts.append(acc)
        if len(unique_accounts) < top:
            top = len(unique_accounts)
        topten = unique_accounts[:top]
        highscore = ""
        place = 1
        for acc in topten:
            highscore += str(place).ljust(len(str(top))+1)
            highscore += ("{} |{}| ".format(acc.name, acc.server.name)).ljust(23-len(str(acc.balance)))
            highscore += str(acc.balance) + "\n"
            place += 1
        if highscore:
            if len(highscore) < 1985:
                await self.bot.say("```py\n"+highscore+"```")
            else:
                await self.bot.say("Trop gros pour être affiché.")
        else:
            await self.bot.say("Aucun compte à afficher.")

    def already_in_list(self, accounts, user):
        for acc in accounts:
            if user.id == acc.id:
                return True
        return False

    @commands.command()
    async def payouts(self):
        """Montre les gains possibles"""
        await self.bot.whisper(slot_payouts)

    @commands.command(pass_context=True, no_pm=True)
    async def slot(self, ctx, bid : int):
        """Joue à la machine à sous"""
        author = ctx.message.author
        server = author.server
        if not self.bank.account_exists(author):
            await self.bot.say("{} Tu as besoin d'un compte pour y jouer. Tape {}bank register pour en ouvrir un.".format(author.mention, ctx.prefix))
            return
        if self.bank.can_spend(author, bid):
            if bid >= self.settings[server.id]["SLOT_MIN"] and bid <= self.settings[server.id]["SLOT_MAX"]:
                if author.id in self.slot_register:
                    if abs(self.slot_register[author.id] - int(time.perf_counter()))  >= self.settings[server.id]["SLOT_TIME"]:
                        self.slot_register[author.id] = int(time.perf_counter())
                        await self.slot_machine(ctx.message, bid)
                    else:
                        await self.bot.say("La machine n'est pas encore disponible ! Attendez {} secondes entre chaque utilisation".format(self.settings[server.id]["SLOT_TIME"]))
                else:
                    self.slot_register[author.id] = int(time.perf_counter())
                    await self.slot_machine(ctx.message, bid)
            else:
                await self.bot.say("{0} L'offre doit être entre {1} et {2}.".format(author.mention, self.settings[server.id]["SLOT_MIN"], self.settings[server.id]["SLOT_MAX"]))
        else:
            await self.bot.say("{0} Tu as besoin d'un compte avec assez de fonds pour y jouer.".format(author.mention))

    async def slot_machine(self, message, bid):
        reel_pattern = [":cherries:", ":cookie:", ":two:", ":four_leaf_clover:", ":cyclone:", ":sunflower:", ":six:", ":mushroom:", ":heart:", ":snowflake:"]
        padding_before = [":mushroom:", ":heart:", ":snowflake:"] # padding prevents index errors
        padding_after = [":cherries:", ":cookie:", ":two:"]
        reel = padding_before + reel_pattern + padding_after
        reels = []
        for i in range(0, 3):
            n = randint(3,12)
            reels.append([reel[n - 1], reel[n], reel[n + 1]])
        line = [reels[0][1], reels[1][1], reels[2][1]]

        display_reels = "\n  " + reels[0][0] + " " + reels[1][0] + " " + reels[2][0] + "\n"
        display_reels += ">" + reels[0][1] + " " + reels[1][1] + " " + reels[2][1] + "\n"
        display_reels += "  " + reels[0][2] + " " + reels[1][2] + " " + reels[2][2] + "\n"

        if line[0] == ":two:" and line[1] == ":two:" and line[2] == ":six:":
            bid = bid * 5000
            await self.bot.send_message(message.channel, "{}{} 226 ! Offre * 5000! {}! ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == ":four_leaf_clover:" and line[1] == ":four_leaf_clover:" and line[2] == ":four_leaf_clover:":
            bid += 1000
            await self.bot.send_message(message.channel, "{}{} Trois trèfles ! +1000! ".format(display_reels, message.author.mention))
        elif line[0] == ":cherries:" and line[1] == ":cherries:" and line[2] == ":cherries:":
            bid += 800
            await self.bot.send_message(message.channel, "{}{} Trois cerises ! +800! ".format(display_reels, message.author.mention))
        elif line[0] == line[1] == line[2]:
            bid += 500
            await self.bot.send_message(message.channel, "{}{} Trois symboles ! +500! ".format(display_reels, message.author.mention))
        elif line[0] == ":two:" and line[1] == ":six:" or line[1] == ":two:" and line[2] == ":six:":
            bid = bid * 4
            await self.bot.send_message(message.channel, "{}{} 26 ! Offre * 4! {}! ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == ":cherries:" and line[1] == ":cherries:" or line[1] == ":cherries:" and line[2] == ":cherries:":
            bid = bid * 3
            await self.bot.send_message(message.channel, "{}{} Deux cerises ! Offre * 3! {}! ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == line[1] or line[1] == line[2]:
            bid = bid * 2
            await self.bot.send_message(message.channel, "{}{} Deux symvoles ! Offre * 2! {}! ".format(display_reels, message.author.mention, str(bid)))
        else:
            await self.bot.send_message(message.channel, "{}{} Rien ! Offre perdue. ".format(display_reels, message.author.mention))
            self.bank.withdraw_credits(message.author, bid)
            await self.bot.send_message(message.channel, "Crédits restant: {}".format(self.bank.get_balance(message.author)))
            return True
        self.bank.deposit_credits(message.author, bid)
        await self.bot.send_message(message.channel, "Crédits restant: {}".format(self.bank.get_balance(message.author)))

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def economyset(self, ctx):
        """Change les paramètres du module économie"""
        server = ctx.message.server
        settings = self.settings[server.id]
        if ctx.invoked_subcommand is None:
            msg = "```"
            for k, v in settings.items():
                msg += "{}: {}\n".format(k, v)
            msg += "```"
            await send_cmd_help(ctx)
            await self.bot.say(msg)

    @economyset.command(pass_context=True)
    async def wipe(self, ctx):
        """Efface entièrement Bank. N'efface pas les données des autres modules."""
        server = ctx.message.server
        self.bank.wipe_bank(server)
        await self.bot.say("Banque effacée.")

    @economyset.command(pass_context=True)
    async def boost(self, ctx, multiplicateur : int):
        """Active le boost et définit le multiplicateur"""
        self.settings["BOOST"] = mult
        if boost <= 0:
            await self.bot.say("Le boost ne peut pas être inférieur ou égal à 0")
            fileIO("data/economy/settings.json", "save", self.settings)
        if boost < 1:
            await self.bot.say("Le boost est maintenant de " + str(mult) + ", ce qui retire de l'argent à chaque distribution.")
            fileIO("data/economy/settings.json", "save", self.settings)
        if boost > 1:
            await self.bot.say("Le boost est maintenant de " + str(mult))
            fileIO("data/economy/settings.json", "save", self.settings)
        
    @economyset.command(pass_context=True)
    async def slotmin(self, ctx, bid : int):
        """Minimum slot machine bid"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_MIN"] = bid
        await self.bot.say("Minimum bid is now " + str(bid) + " credits.")
        fileIO("data/economy/settings.json", "save", self.settings)

    @economyset.command(pass_context=True)
    async def slotmax(self, ctx, bid : int):
        """Maximum slot machine bid"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_MAX"] = bid
        await self.bot.say("Maximum bid is now " + str(bid) + " credits.")
        fileIO("data/economy/settings.json", "save", self.settings)

    @economyset.command(pass_context=True)
    async def slottime(self, ctx, seconds : int):
        """Seconds between each slots use"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_TIME"] = seconds
        await self.bot.say("Cooldown is now " + str(seconds) + " seconds.")
        fileIO("data/economy/settings.json", "save", self.settings)

    @economyset.command(pass_context=True)
    async def paydaytime(self, ctx, seconds : int):
        """Seconds between each payday"""
        server = ctx.message.server
        self.settings[server.id]["PAYDAY_TIME"] = seconds
        await self.bot.say("Value modified. At least " + str(seconds) + " seconds must pass between each payday.")
        fileIO("data/economy/settings.json", "save", self.settings)

    @economyset.command(pass_context=True)
    async def paydaycredits(self, ctx, credits : int):
        """Credits earned each payday"""
        server = ctx.message.server
        self.settings[server.id]["PAYDAY_CREDITS"] = credits
        await self.bot.say("Every payday will now give " + str(credits) + " credits.")
        fileIO("data/economy/settings.json", "save", self.settings)

    def display_time(self, seconds, granularity=2): # What would I ever do without stackoverflow?
        intervals = (                               # Source: http://stackoverflow.com/a/24542445
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
            )

        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])

def check_folders():
    if not os.path.exists("data/economy"):
        print("Creating data/economy folder...")
        os.makedirs("data/economy")

def check_files():

    f = "data/economy/settings.json"
    if not fileIO(f, "check"):
        print("Creating default economy's settings.json...")
        fileIO(f, "save", {})

    f = "data/economy/bank.json"
    if not fileIO(f, "check"):
        print("Creating empty bank.json...")
        fileIO(f, "save", {})

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("red.economy")
    n = Economy(bot)
    bot.add_listener(n.auto_register, "on_message")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/economy/economy.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    bot.add_cog(n)
