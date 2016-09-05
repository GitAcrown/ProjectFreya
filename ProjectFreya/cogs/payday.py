#  Bankheist.py was created by Redjumpman for Redbot
#  This will create a system.JSON file and a data folder
#  This will modify values your bank.json from economy.py
import os
import asyncio
import random
import time
import discord
from operator import itemgetter
from discord.ext import commands
from .utils.dataIO import fileIO
from random import randint
from .utils import checks
from __main__ import send_cmd_help
try:   # Check if Tabulate is installed
    from tabulate import tabulate
    tabulateAvailable = True
except:
    tabulateAvailable = False


class Payday:
    """Un vol de banque... mais c'est légal"""

    def __init__(self, bot):
        self.bot = bot
        self.system = fileIO("data/bankheist/system.json", "load")
        self.good = [["{} prépare la voiture, prêt à partir +25 points.", 25],
                     ["{} coupe le courant +50 points.", 50],
                     ["{} efface l'enregistrement vidéo +50 points", 50],
                     ["{} hack le systeme de sécurité et remplace la vidéo par Vitas - The 7th element +75 points", 75],
                     ["{} tue le garde qui tentait d'appuyer sur l'alarme +50 points", 50],
                     ["{} assome le garde de sécurité +50 points", 50],
                     ["{} a tué un random qui tentait de faire le héros +50 points", 50],
                     ["{} a réussit à forcer la police a livrer une pizza pour tout le monde +25 points", 25],
                     ["{} a acheté des masques pour cacher son identité +25 points", 25],
                     ["{} trouve la porte de derrière +25 points", 25],
                     ["{} s'est entrainé sur Payday 2 +25 points", 25],
                     ["{} a ammené des munitions supplémentaires pour le crew +25 points", 25],
                     ["{} perce le coffre comme dans du beurre +25 points", 25],
                     ["{} garde les otages sous contrôle +25 points", 25],
                     ["{} apporte des explosifs pour la porte +50 points", 50],
                     ["{} campe comme un kikoo-callof sur le toît +100 points", 100],
                     ["{} distrait le garde en se déshabillant devant la caméra +25 points", 25],
                     ["{} a pris du café pour le crew +25 points", 25],
                     ["{} agite les bras pour faire peur aux enfants +25 points", 25],
                     ["{} s'équipe du baton à 250€ pour repousser les policiers +25 points", 25],
                     ["{} a infiltré la banque en employé +25 points", 25],
                     ["{} se sert d'un enfant cancéreux comme bouclier humain +50 points", 50],
                     ["{} distribue des gants pour ne pas laisser ses empreintes +50 points", 50],
                     ["{} trouve une boite de diamants sur un civil +25 points", 25]]
        self.bad = ["Un tir à eu lieu avec la police locale et {} est touché." + "\n" +
                    "`{} hors jeu.`",
                    "Les policiers ont trouvés des empreintes de chaussures sur le sol provenant de {}" + "\n" +
                    "`{} hors jeu.`",
                    "{} se crash avec sa Volvo sur le chemin de la banque" + "\n" +
                    "`{} hors jeu.`",
                    "{} se fait coincé en train de jouer à Pokemon Go" + "\n" +
                    "`{} hors jeu.`",
                    "{} se fait chopper en train de prendre son goûté" + "\n" +
                    "`{} hors jeu.`",
                    "{} glisse sur une plaque de verglas à l'entrée de la Banque" + "\n" +
                    "`{} hors jeu.`",
                    "{} a cru pouvoir dépasser le crew et à payé pour ça." + "\n" +
                    "`{} hors jeu.`",
                    "{} explose un pneu et s'explose surtout la tronche" + "\n" +
                    "`{} hors jeu.`",
                    "Le pistolet de {} s'enraye et il s'explose la main" + "\n" +
                    "`{} hors jeu.`",
                    "{} est resté dans la banque pendant que le crew partait" + "\n" +
                    "`{} hors jeu.`",
                    "{} a été captué en partant aux toilettes" + "\n" +
                    "`{} hors jeu.`",
                    "{} se mange la porte et reste allongé sur le sol" + "\n" +
                    "`{} hors jeu.`",
                    "{} s'est montré devant la police, tellement bourré qu'il était incapable de voir que ce n'était pas le crew." + "\n" +
                    "`{} hors jeu.`",
                    "{} trop occupé à compter les billets s'est fait attrapé." + "\n" +
                    "`{} hors jeu.`",
                    "Le sac d'argent de {} contenait une cartouche explosive de marqueur bleu, permettant à la police de remonter le suspect" + "\n" +
                    "`{} hors jeu.`",
                    "{} a été snipé par un sniper du GIGN" + "\n" +
                    "`{} hors jeu.`",
                    "Le crew à décidé d'abandonner {} pour servir d'appât" + "\n" +
                    "`{} hors jeu.`",
                    "{} a été tué par un tir allié" + "\n" +
                    "`{} hors jeu.`",
                    "{} effrayé par le petit chien de sécurité cours rapidement en dehors de la banque." + "\n" +
                    "`{} hors jeu.`",
                    "Un civil a filmé {} ce qui a permis de le retrouver" + "\n" +
                    "`{} hors jeu.`",
                    "{} révèle son identité sur facebook." + "\n" +
                    "`{} hors jeu.`",
                    "{} prend un selfie avec un gardien assassiné." + "\n" +
                    "`{} hors jeu.`",
                    "Le GIGN a envoyé du Zyklon B, {} dort comme un bébé" + "\n" +
                    "`{} hors jeu.`",
                    "{} reste enfermé à cause du système de sécurité de la banque" + "\n" +
                    "`{} hors jeu.`",
                    "{} n'avait pas envie de le faire, en fait." + "\n" +
                    "`{} hors jeu.`",
                    "'FLASH BANG!', à été la dernière chose que {} à entendu" + "\n" +
                    "`{} hors jeu.`",
                    "'GRENAAADE!', {} dort maintenant avec les rats, à côté des poubelles" + "\n" +
                    "`{} hors jeu.`",
                    "{} active un laser et se fait chopper par la police" + "\n" +
                    "`{} hors jeu.`",
                    "Un garde taze {}, il est maintenant en train de baver sur le sol." + "\n" +
                    "`{} hors jeu.`",
                    "{} se fait tabasser par un civil go-muscu et le crew est déjà parti." + "\n" +
                    "`{} hors jeu.`"]

    @commands.group(pass_context=True, no_pm=True)
    async def payday(self, ctx):
        """Commandes Payday"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @payday.command(name="role", pass_context=True)
    async def _role_payday(self, ctx):
        """Vous donne le rôle @Payday pour être notifié au début de chaque partie.

        Si le rôle n'existe pas sur le serveur, il sera créé automatiquement."""
        server = ctx.message.server
        user = ctx.message.author
        # Regarde si le rôle existe
        if 'Payday' not in [r.name for r in server.roles]:
            await self.bot.say("Le rôle n'existe pas. Je vais donc le créer...")
            try:
                perms = discord.Permissions.none()
                # Active les permissions voulues (si nécéssaire)
                await self.bot.create_role(server, name="Payday", permissions=perms)
                await self.bot.say("Rôle crée ! Refaites la commande pour obtenir le rôle !")
                try:
                    for c in server.channels:
                        if c.type.name == 'text':
                            perms = discord.PermissionOverwrite()
                            perms.send_messages = False
                            r = discord.utils.get(ctx.message.server.roles, name="Payday")
                            await self.bot.edit_channel_permissions(c, r, perms)
                        await asyncio.sleep(1.5)
                except discord.Forbidden:
                    await self.bot.say("Une erreur est apparue.")
            except discord.Forbidden:
                await self.bot.say("Je ne peux pas créer le rôle.")
        else:
            server = ctx.message.server
            if user.id == self.bot.user.id:
                await self.bot.say("Je ne peux pas avoir ce rôle...")
            r = discord.utils.get(ctx.message.server.roles, name="Payday")
            if 'Payday' not in [r.name for r in user.roles]:
                await self.bot.add_roles(user, r)
                await self.bot.say("{} Vous avec maintenant le rôle Payday".format(user.name))
            else:
                await self.bot.remove_roles(user, r)
                await self.bot.say("{} Vous n'avez plus le rôle Payday".format(user.name))
      

    @payday.command(name="play", pass_context=True)
    async def _play_payday(self, ctx, bet: int):
        """Commence un vol de banque en fonction du nombre de joueurs"""
        user = ctx.message.author
        server = ctx.message.server
        r = discord.utils.get(ctx.message.server.roles, name="Payday")
        if bet >= 50:
            if self.account_check(user):
                if self.enough_points(user.id, bet, server):
                    if await self.check_cooldowns():  # time between heists
                        if self.heist_started:  # Checks if a heist is currently happening
                            if self.heist_plan():  # checks if a heist is being planned or not
                                self.system["Config"]["Min Bet"] = bet
                                self.heist_ptoggle()
                                self.heist_stoggle()
                                self.crew_add(user.id, user.name, bet)
                                self.subtract_bet(user.id, bet, server)
                                wait = self.system["Config"]["Wait Time"]
                                wait_time = int(wait / 2)
                                half_time = int(wait_time / 2)
                                split_time = int(half_time / 2)
                                await self.bot.change_status(discord.Game(name="Payday"))
                                await self.bot.say( r.mention + " **Une partie de Payday à été lancé par " + user.name + "**" +
                                                   "\n" + "*" + str(wait) + " secondes avant que ça ne commence*")
                                await asyncio.sleep(wait_time)
                                await self.bot.say("*"+ str(wait_time) + " secondes avant que la partie démarre*")
                                await asyncio.sleep(half_time)
                                await self.bot.say("*"+ str(half_time) + " secondes avant que la partie démarre*")
                                await asyncio.sleep(split_time)
                                await self.bot.say("Hop hop hop ! " + "*" + str(split_time) + " secondes avant que le jeu commence*")
                                await asyncio.sleep(split_time)
                                if self.system["Config"]["Players"] >= 2:
                                    await self.bot.say("**Fermeture de la session. La partie va commencer.**")
                                    self.system["Config"]["Bankheist Running"] = "Yes"
                                    fileIO("data/bankheist/system.json", "save", self.system)
                                    bank = self.check_banks()
                                    await asyncio.sleep(split_time)
                                    await self.bot.say("**Le crew à décidé de viser " + bank + "**")
                                    j = self.game_outcomes()
                                    j_temp = j[:]
                                    while j_temp is not None:
                                        result = random.choice(j_temp)
                                        j_temp.remove(result)
                                        await asyncio.sleep(10)
                                        await self.bot.say(result)
                                        if len(j_temp) == 0:
                                            self.system["Config"]["Bankheist Running"] = "No"
                                            fileIO("data/bankheist/system.json", "save", self.system)
                                            await asyncio.sleep(2)
                                            await self.bot.say("**La partie est terminée.**")
                                            await asyncio.sleep(2)
                                            if self.system["Heist Winners"]:
                                                target = self.system["Config"]["Bank Target"]
                                                amount = self.system["Banks"][target]["Vault"] / self.system["Config"]["Players"]
                                                winners_names = [subdict["Name"] for subdict in self.system["Heist Winners"].values()]
                                                pullid = ', '.join(subdict["User ID"] for subdict in self.system["Heist Winners"].values())
                                                winners_bets = [subdict["Bet"] for subdict in self.system["Heist Winners"].values()]
                                                winners_bonuses = [subdict["Bonus"] for subdict in self.system["Heist Winners"].values()]
                                                winners = pullid.split()
                                                vtotal = self.system["Banks"][target]["Vault"]
                                                vault_remainder = vtotal - amount * len(winners)
                                                self.system["Banks"][target]["Vault"] -= int(round(vault_remainder))
                                                fileIO("data/bankheist/system.json", "save", self.system)
                                                multiplier = self.system["Banks"][target]["Multiplier"]
                                                sm_raw = [int(round(x)) * multiplier for x in winners_bets]
                                                success_multiplier = [int(round(x)) for x in sm_raw]
                                                cs_raw = [amount] * int(round(self.system["Config"]["Players"]))
                                                credits_stolen = [int(round(x)) for x in cs_raw]
                                                total_winnings = [int(round(x)) + int(round(y)) + int(round(z)) for x, y, z in zip(success_multiplier, credits_stolen, winners_bonuses)]
                                                self.add_total(winners, total_winnings, server)
                                                z = list(zip(winners_names, winners_bets, success_multiplier, credits_stolen, winners_bonuses, total_winnings))
                                                t = tabulate(z, headers=["Joueurs", "Offres", "Résultat", "Crédits volés", "Bonus", "Total"])
                                                await self.bot.say("Le total à été partagé entre  " +
                                                                   "les gagnants: ")
                                                await self.bot.say("```Python" + "\n" + t + "```")
                                                self.system["Config"]["Time Remaining"] = int(time.perf_counter())
                                                fileIO("data/bankheist/system.json", "save", self.system)
                                                self.heistclear()
                                                self.winners_clear()
                                                await self.bot.change_status(None)
                                                break
                                            else:
                                                await self.bot.say("Personne n'a réussi à s'enfuir.")
                                                self.system["Config"]["Time Remaining"] = int(time.perf_counter())
                                                fileIO("data/bankheist/system.json", "save", self.system)
                                                self.heistclear()
                                                await self.bot.change_status(None)
                                                break
                                        else:
                                            continue
                                else:
                                    await self.bot.say("Impossible de démarrer la partie, il n'y a pas assez de joueurs.")
                                    self.heistclear()
                                    await self.bot.change_status(None)
                                        
                            elif self.system["Config"]["Bankheist Running"] == "No":
                                if bet >= self.system["Config"]["Min Bet"]:
                                    if self.crew_check(user.id):  # join a heist that was started
                                        self.crew_add(user.id, user.name, bet)
                                        self.subtract_bet(user.id, bet, server)
                                        await self.bot.say(user.name + " a rejoint le crew !")
                                    else:
                                        await self.bot.say("Vous êtes déjà dans le crew")
                                else:
                                    minbet = self.system["Config"]["Min Bet"]
                                    await self.bot.say("L'Offre doit être égale ou supérieure" +
                                                       " à l'offre de départ de " + str(minbet))
                            elif self.system["Config"]["Bankheist Started"] == "Yes":
                                await self.bot.say("Vous ne pouvez pas rejoindre une partie en cours")
                            else:
                                await self.bot.say("Si vous voyez ce message, c'est qu'il y a un gros problème.")
                        else:
                            await self.bot.say("Vous ne pouvez pas rejoindre une partie en cours")
                else:
                    await self.bot.say("Vous n'avez pas assez de crédit pour ça.")
            else:
                await self.bot.say("Vous avez besoin d'un compte bancaire.")
        else:
            await self.bot.say("L'Offre de départ doit être supérieure à 50§.")

    @payday.command(name="reset", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _reset_heist(self, ctx):
        """EN CAS D'URGEEEEENCE"""
        self.heistclear()
        await self.bot.change_status(None)
        await self.bot.say("Reset effectué.")

    @payday.command(name="banks", pass_context=True)
    async def _banks_heist(self, ctx):
        """Montre les infos d'une banque"""
        column1 = [subdict["Name"] for subdict in self.system["Banks"].values()]
        column2 = [subdict["Crew"] for subdict in self.system["Banks"].values()]
        column3 = [subdict["Multiplier"] for subdict in self.system["Banks"].values()]
        column4 = [subdict["Vault"] for subdict in self.system["Banks"].values()]
        column5 = [subdict["Success"] for subdict in self.system["Banks"].values()]
        sr = [str(x) + "%" for x in column5]
        m = list(zip(column1, column2, column3, column4, sr))
        m = sorted(m, key=itemgetter(1), reverse=True)
        t = tabulate(m, headers=["Banque", "Crew", "Multiplicateur", "Coffre", "% Réussite"])
        await self.bot.say("```Python" + "\n" + t + "```")

    @payday.command(name="info", pass_context=True)
    async def _info_heist(self, ctx):
        """Affiche les informations à propos du jeu en MP"""
        msg = "```\n"
        msg += "Pour commencer une partie: !payday play. " + "\n"
        msg += "L'Offre initiale est le minimum que les autres membres doivent placer." + "\n"
        msg += "Une période est donnée pour que d'autres personnes rejoignent le crew." + "\n"
        msg += "D'autres joueurs peuvent rejoindre en tapant !payday play" + "\n"
        msg += "Une fois que la partie commence la session est bloquée." + "\n"
        msg += "Le jeu se déroule à travers des scénario aléatoires. *(Vous voulez rajouter une action dans le scénario ? Contactez @Acrown#4424)*" + "\n"
        msg += "Ceux qui réussissent à passer le scénario gagnent de l'argent de la banque et leur offre est multipliée" + "\n"
        msg += "Les grosses banques ont des plus gros coffres, et des plus gros multiplicateurs, mais il faudra un plus gros crew." + "\n"
        msg += "Les banques se rechargent dans le temps." + "\n"
        msg += "Pour voir les banques, tapez !payday banks" + "\n"
        msg += "Pour changer les paramètres, tapez !setpayday (admins seulement)" + "```"
        await self.bot.whisper(msg)

    @payday.command(name="crew", pass_context=True)
    async def _crew_heist(self, ctx):
        """Affiche le crew de la partie en cours."""
        total = self.system["Config"]["Players"]
        if total > 0:
            column1 = [subdict["Name"] for subdict in self.system["Players"].values()]
            column2 = [subdict["Bet"] for subdict in self.system["Players"].values()]
            m = list(zip(column1, column2))
            m = sorted(m, key=itemgetter(1), reverse=True)
            t = tabulate(m, headers=["Joueurs", "Offre"])
            await self.bot.say("```Python" + "\n" + t + "```")
            await self.bot.say("**Total de {} joueurs**".format(total))
        else:
            await self.bot.say("Il n'y a pas de crew.")
    
    @commands.group(pass_context=True, no_pm=True)
    async def setpayday(self, ctx):
        """Set different options in the heist config"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @setpayday.command(name="bankname", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _bankname_setpayday(self, ctx, level: int, *, name: str):
        """Sets the name of the bank for each level (1-5).
        """
        if level > 0 and level <= 5:
            banklvl = "Lvl " + str(level) + " Bank"
            self.system["Banks"][banklvl]["Name"] = name
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("Changed {}'s name to {}".format(banklvl, name))
        else:
            await self.bot.say("You need to pick a level from 1 to 5")

    @setpayday.command(name="vaultmax", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _vaultmax_setpayday(self, ctx, banklvl: int, maximum: int):
        """Sets the maximum credit amount a vault can hold.
        """
        if banklvl > 0 and banklvl <= 5:
            if maximum > 0:
                banklvl = "Lvl " + str(banklvl) + " Bank"
                self.system["Banks"][banklvl]["Max"] = maximum
                fileIO("data/bankheist/system.json", "save", self.system)
                await self.bot.say("Changed {}'s vault max to {}".format(banklvl, maximum))
            else:
                await self.bot.say("Need to set a maximum higher than 0.")
        else:
            await self.bot.say("You need to pick a level from 1 to 5.")

    @setpayday.command(name="multiplier", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _multiplier_setpayday(self, ctx, multiplier: float, banklvl: int):
        """Set the payout multiplier for a bank
        """
        if multiplier > 0:
            if banklvl > 0 and banklvl <= 5:
                banklvl = "Lvl " + str(banklvl) + " Bank"
                self.system["Banks"][banklvl]["Multiplier"] = multiplier
                fileIO("data/bankheist/system.json", "save", self.system)
                await self.bot.say("```" + banklvl + "'s multiplier is now set to " +
                                   str(multiplier) + "```")
            else:
                await self.bot.say("This bank name does not exist")
        else:
            await self.bot.say("You need to specify a multiplier")

    @setpayday.command(name="time", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _time_setpayday(self, ctx, seconds: int):
        """Set the wait time for a heist to start
        """
        if seconds > 0:
            self.system["Config"]["Wait Time"] = seconds
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("I have now set the wait time to " + str(seconds) + " seconds.")
        else:
            await self.bot.say("Time must be greater than 0.")

    @setpayday.command(name="cooldown", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _cooldown_setpayday(self, ctx):
        """Toggles cooldowns on/off and sets the time"""
        if self.system["Config"]["Cooldown"]:
            self.system["Config"]["Cooldown"] = False
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("Heist cooldowns are now OFF.")
        else:
            self.system["Config"]["Cooldown"] = True
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("heist cooldowns are now ON.")

    @setpayday.command(name="cdtime", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _cdtime_setpayday(self, ctx, timer: int):
        """Set's the cooldown timer in seconds. 3600"""
        if timer > 0:
            self.system["Config"]["Default CD"] = timer
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("Setting the cooldown timer to {}".format(self.time_format(timer)))
        else:
            await self.bot.say("Needs to be higher than 0. If you don't want a cooldown turn it off.")

    @setpayday.command(name="success", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _success_setpayday(self, ctx, rate: int, banklvl: int):
        """Set the success rate for a bank. 1-100 %
        """
        if banklvl > 0 and banklvl <= 5:
            banklvl = "Lvl " + str(banklvl) + " Bank"
            if rate > 0 and rate <= 100:
                self.system["Banks"][banklvl]["Success"] = rate
                fileIO("data/bankheist/system.json", "save", self.system)
                await self.bot.say("I have now set the success rate for " + banklvl + " to " + str(rate) + ".")
            else:
                await self.bot.say("Success rate must be greater than 0 or less than or equal to 100.")

    @setpayday.command(name="crew", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _crew_setpayday(self, ctx, crew: int, banklvl: int):
        """Sets the crew size needed for each bank level
        """
        if banklvl > 0 and banklvl <= 5:
            if banklvl < 2:
                nlvl = "Lvl " + str(banklvl + 1) + " Bank"
                lvl = "Lvl " + str(banklvl) + " Bank"
                if crew < self.system["Banks"][nlvl]["Crew"]:
                    self.system["Banks"][lvl]["Crew"] = crew
                    fileIO("data/bankheist/system.json", "save", self.system)
                    await self.bot.say("```Python\nSetting Level 1 Bank to crew size {}.```".format(str(crew)))
                else:
                    await self.bot.say("Level 1 bank's crewsize should be lower than the Level 2 Bank.")
            elif banklvl > 1 and banklvl < 5:
                nlvl = "Lvl " + str(banklvl + 1) + " Bank"
                lvl = "Lvl " + str(banklvl) + " Bank"
                plvl = "Lvl " + str(banklvl - 1) + " Bank"
                if crew < self.system["Banks"][nlvl]["Crew"] and crew > self.system["Banks"][plvl]["Crew"]:
                    self.system["Banks"][lvl]["Crew"] = crew
                    fileIO("data/bankheist/system.json", "save", self.system)
                    await self.bot.say("```Python\nSetting {} to crew size {}.```".format(lvl, str(crew)))
                else:
                    await self.bot.say("The crew size for {} must be higher than {}, but lower than {}".format(lvl, plvl, nlvl))
            else:
                lvlfive = "Lvl " + str(banklvl) + " Bank"
                lvlfour = "Lvl " + str(banklvl - 1) + " Bank"
                if crew > self.system["Banks"][lvlfour]["Crew"]:
                    self.system["Banks"][lvlfive]["Crew"] = crew
                    fileIO("data/bankheist/system.json", "save", self.system)
                    await self.bot.say("```Python\nSetting Level 5 Bank to crew size {}.```".format(str(crew)))
                else:
                    await self.bot.say("The crewsize for the Lvl 5 bank must be higher than the lvl 4 bank.")
        else:
            await self.bot.say("You need to pick a level from 1 to 5")

    @setpayday.command(name="vault", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _vault_setpayday(self, ctx, amount: int, banklvl: int):
        """Set the amount of credits in a bank's vault.
        """
        if amount > 0:
            if banklvl > 0 and banklvl <= 5:
                banklvl = "Lvl " + str(banklvl) + " Bank"
                self.system["Banks"][banklvl]["Vault"] = amount
                fileIO("data/bankheist/system.json", "save", self.system)
                await self.bot.say("I have set " + banklvl + "'s vault to " + str(amount) + " credits.")
            else:
                await self.bot.say("That bank level does not exist. Use levels 1 through 5")
        else:
            await self.bot.say("You need to enter an amount higher than 0.")

    @setpayday.command(name="frequency", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _frequency_setpayday(self, ctx, seconds: int):
        """Sets how frequently banks regenerate credits. Default: 60 seconds.
        """
        if seconds > 0:
            self.system["Config"]["Vault Frequency"] = seconds
            fileIO("data/bankheist/system.json", "save", self.system)
            await self.bot.say("Vaults will now increase in credits every " + str(seconds) + " seconds.")
        else:
            await self.bot.say("You need to enter an amount higher than 0.")

    async def vault_update(self):
        while self == self.bot.get_cog("Payday"):
            if self.system["Banks"]["Lvl 1 Bank"]["Vault"] < self.system["Banks"]["Lvl 1 Bank"]["Max"]:
                self.system["Banks"]["Lvl 1 Bank"]["Vault"] += 22
            if self.system["Banks"]["Lvl 2 Bank"]["Vault"] < self.system["Banks"]["Lvl 2 Bank"]["Max"]:
                self.system["Banks"]["Lvl 2 Bank"]["Vault"] += 31
            if self.system["Banks"]["Lvl 3 Bank"]["Vault"] < self.system["Banks"]["Lvl 3 Bank"]["Max"]:
                self.system["Banks"]["Lvl 3 Bank"]["Vault"] += 48
            if self.system["Banks"]["Lvl 4 Bank"]["Vault"] < self.system["Banks"]["Lvl 4 Bank"]["Max"]:
                self.system["Banks"]["Lvl 4 Bank"]["Vault"] += 53
            if self.system["Banks"]["Lvl 5 Bank"]["Vault"] < self.system["Banks"]["Lvl 5 Bank"]["Max"]:
                self.system["Banks"]["Lvl 5 Bank"]["Vault"] += 60
            fileIO("data/bankheist/system.json", "save", self.system)
            frequency = self.system["Config"]["Vault Frequency"]
            await asyncio.sleep(frequency)  # task runs every 60 seconds

    def account_check(self, uid):
        bank = self.bot.get_cog('Economy').bank
        if bank.account_exists(uid):
            return True
        else:
            return False

    async def check_cooldowns(self):
        if self.system["Config"]["Cooldown"] is False:
            return True
        elif abs(self.system["Config"]["Time Remaining"] - int(time.perf_counter())) >= self.system["Config"]["Default CD"]:
            return True
        elif self.system["Config"]["Time Remaining"] == 0:
            return True
        else:
            s = abs(self.system["Config"]["Time Remaining"] - int(time.perf_counter()))
            seconds = abs(s - self.system["Config"]["Default CD"])
            await self.bot.say("La police est en alerte. Attendez que ça se calme avant d'y retourner.")
            await self.time_formatting(seconds)
            return False

    def time_format(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            msg = "{} heures, {} minutes, {} secondes".format(h, m, s)
        elif h == 0 and m > 0:
            msg = "{} minutes, {} secondes".format(m, s)
        elif m == 0 and h == 0 and s > 0:
            msg = "{} secondes".format(s)
        elif m == 0 and h == 0 and s == 0:
            msg = "Aucun cooldown"
        return msg

    async def time_formatting(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            await self.bot.say("```{} heures, {} minutes et {} secondes restantes```".format(h, m, s))
        elif h == 0 and m > 0:
            await self.bot.say("{} minutes, {} secondes restantes".format(m, s))
        elif m == 0 and h == 0 and s > 0:
            await self.bot.say("{} secondes restantes".format(s))

    def heistclear(self):
        self.winners_clear()
        del self.system["Players"]
        del self.system["Heist Winners"]
        self.system["Players"] = {}
        self.system["Config"]["Bankheist Running"] = "No"
        self.system["Config"]["Planning Heist"] = "No"
        self.system["Config"]["Bankheist Started"] = "No"
        self.system["Heist Winners"] = {}
        self.system["Config"]["Min Bet"] = 0
        self.system["Config"]["Players"] = 0
        self.system["Config"]["Bank Target"] = ""
        fileIO("data/bankheist/system.json", "save", self.system)

    def enough_points(self, uid, amount, server):
        bank = self.bot.get_cog('Economy').bank
        mobj = server.get_member(uid)
        if self.account_check(mobj):
            if bank.can_spend(mobj, amount):
                return True
            else:
                return False
        else:
            return False

    def check_banks(self):
        if self.system["Config"]["Players"] <= self.system["Banks"]["Lvl 1 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 1 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 1 Bank"]["Name"]
        elif self.system["Config"]["Players"] <= self.system["Banks"]["Lvl 2 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 2 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 2 Bank"]["Name"]
        elif self.system["Config"]["Players"] <= self.system["Banks"]["Lvl 3 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 3 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 3 Bank"]["Name"]
        elif self.system["Config"]["Players"] <= self.system["Banks"]["Lvl 4 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 4 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 4 Bank"]["Name"]
        elif self.system["Config"]["Players"] <= self.system["Banks"]["Lvl 5 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 5 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 5 Bank"]["Name"]
        elif self.system["Config"]["Players"] > self.system["Banks"]["Lvl 5 Bank"]["Crew"]:
            self.system["Config"]["Bank Target"] = "Lvl 5 Bank"
            fileIO("data/bankheist/system.json", "save", self.system)
            return self.system["Banks"]["Lvl 5 Bank"]["Name"]

    def winners(self):
        for subdict in self.system["Heist Winners"].values():
            return subdict['Name']

    def game_outcomes(self):
        players = []
        for subdict in self.system["Players"].values():
            players.append(subdict)
        temp_good_things = self.good[:]  # coping the lists
        temp_bad_things = self.bad[:]
        chance = self.heist_chance()
        results = []
        for player in players:
            if randint(0, 100) <= chance:
                key = player["Name"]
                good_thing = random.choice(temp_good_things)
                temp_good_things.remove(good_thing)
                results.append(good_thing[0].format(key))
                self.system["Heist Winners"][key] = {"Name": key,
                                                     "User ID": player["User ID"],
                                                     "Bet": player["Bet"],
                                                     "Bonus": good_thing[1]}
                fileIO("data/bankheist/system.json", "save", self.system)
            else:
                key = player["Name"]
                bad_thing = random.choice(temp_bad_things)
                temp_bad_things.remove(bad_thing)
                results.append(bad_thing.format(key, key))
        return results

    def heist_chance(self):
        if self.system["Config"]["Bank Target"] == "Lvl 1 Bank":
            return self.system["Banks"]["Lvl 1 Bank"]["Success"]
        elif self.system["Config"]["Bank Target"] == "Lvl 2 Bank":
            return self.system["Banks"]["Lvl 2 Bank"]["Success"]
        elif self.system["Config"]["Bank Target"] == "Lvl 3 Bank":
            return self.system["Banks"]["Lvl 3 Bank"]["Success"]
        elif self.system["Config"]["Bank Target"] == "Lvl 4 Bank":
            return self.system["Banks"]["Lvl 4 Bank"]["Success"]
        elif self.system["Config"]["Bank Target"] == "Lvl 5 Bank":
            return self.system["Banks"]["Lvl 5 Bank"]["Success"]

    def winners_clear(self):
        del self.system["Heist Winners"]
        self.system["Heist Winners"] = {}
        fileIO("data/bankheist/system.json", "save", self.system)

    def crew_add(self, uid, name, bet):
        self.system["Players"][uid] = {"Name": name,
                                       "Bet": int(bet),
                                       "User ID": uid}
        self.system["Config"]["Players"] = self.system["Config"]["Players"] + 1
        fileIO("data/bankheist/system.json", "save", self.system)

    def crew_check(self, uid):
        if uid not in self.system["Players"]:
            return True
        else:
            return False

    def add_total(self, winners, totals, server):
        bank = self.bot.get_cog('Economy').bank
        i = -1
        for winner in winners:
            i = i + 1
            userid = winner.replace(',', '')
            mobj = server.get_member(userid)
            bank.deposit_credits(mobj, totals[i])

    def subtract_bet(self, userid, bet, server):
        bank = self.bot.get_cog('Economy').bank
        mobj = server.get_member(userid)
        if self.account_check(mobj):
            bank.withdraw_credits(mobj, bet)

    def player_counter(self, number):
        self.system["Players"] = self.system["Players"] + number
        fileIO("data/bankheist/system.json", "save", self.system)

    def heist_plan(self):
        if self.system["Config"]["Planning Heist"] == "No":
            return True
        else:
            return False

    def heist_started(self):
        if self.system["Config"]["Bankheist Started"] == "No":
            return True
        else:
            return False

    def heist_stoggle(self):
        if self.system["Config"]["Bankheist Started"] == "Yes":
            self.system["Config"]["Bankheist Started"] = "No"
            fileIO("data/bankheist/system.json", "save", self.system)
        elif self.system["Config"]["Bankheist Started"] == "No":
            self.system["Config"]["Bankheist Started"] = "Yes"
            fileIO("data/bankheist/system.json", "save", self.system)

    def heist_ptoggle(self):
        if self.system["Config"]["Planning Heist"] == "No":
            self.system["Config"]["Planning Heist"] = "Yes"
            fileIO("data/bankheist/system.json", "save", self.system)
        elif self.system["Config"]["Planning Heist"] == "Yes":
            self.system["Config"]["Planning Heist"] = "No"
            fileIO("data/bankheist/system.json", "save", self.system)

    def cooldown(self):
        if self.system["Cooldown"] == "No":
            return True
        else:
            return False


def check_folders():
    if not os.path.exists("data/bankheist"):
        print("Creating data/bankheist folder...")
        os.makedirs("data/bankheist")


def check_files():
    system = {"Players": {},
              "Config": {"Bankheist Started": "No", "Planning Heist": "No",
                         "Cooldown": False, "Time Remaining": 0, "Default CD": 0,
                         "Bankheist Running": "No", "Players": 0,
                         "Min Bet": 0, "Wait Time": 120, "Bank Target": "",
                         "Vault Frequency": 120},
              "Heist Winners": {},
              "Banks": {"Lvl 1 Bank": {"Name": "Serveur", "Crew": 2, "Multiplier": 0.32, "Success": 46, "Vault": 1500, "Max": 1500},
                        "Lvl 2 Bank": {"Name": "4chan", "Crew": 4, "Multiplier": 0.41, "Success": 40, "Vault": 4000, "Max": 4000},
                        "Lvl 3 Bank": {"Name": "Madmoizelle", "Crew": 6, "Multiplier": 0.49, "Success": 37, "Vault": 7000, "Max": 7000},
                        "Lvl 4 Bank": {"Name": "Webedia", "Crew": 8, "Multiplier": 0.54, "Success": 32, "Vault": 10500, "Max": 10500},
                        "Lvl 5 Bank": {"Name": "Valve", "Crew": 10, "Multiplier": 0.61, "Success": 28, "Vault": 18000, "Max": 18000},
                        },
              }

    f = "data/bankheist/system.json"
    if not fileIO(f, "check"):
        print("Creating default bankheist system.json...")
        fileIO(f, "save", system)
    else:  # consistency check
        current = fileIO(f, "load")
        if current.keys() != system.keys():
            for key in system.keys():
                if key not in current.keys():
                    current[key] = system[key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Config"].keys() != system["Config"].keys():
            for key in system["Config"].keys():
                if key not in current["Config"].keys():
                    current["Config"][key] = system["Config"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"].keys() != system["Banks"].keys():
            try:
                del current["Banks"]["The Local Bank"]
                del current["Banks"]["First National Bank"]
                del current["Banks"]["PNC Bank"]
                del current["Banks"]["Bank of America"]
                del current["Banks"]["Fort Knox"]
                for key in system["Banks"].keys():
                    if key not in current["Banks"].keys():
                        current["Banks"][key] = system["Banks"][key]
                        print("Adding " + str(key) +
                              " field to bankheist system.json")
                fileIO(f, "save", current)
            except:
                for key in system["Banks"].keys():
                    if key not in current["Banks"].keys():
                        current["Banks"][key] = system["Banks"][key]
                        print("Adding " + str(key) +
                              " field to bankheist system.json")
                fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"].keys() != system["Banks"].keys():
            for key in system["Banks"].keys():
                if key not in current["Banks"].keys():
                    current["Banks"][key] = system["Banks"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"]["Lvl 1 Bank"].keys() != system["Banks"]["Lvl 1 Bank"].keys():
            for key in system["Banks"]["Lvl 1 Bank"].keys():
                if key not in current["Banks"]["Lvl 1 Bank"].keys():
                    current["Banks"]["Lvl 1 Bank"][key] = system["Banks"]["Lvl 1 Bank"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"]["Lvl 2 Bank"].keys() != system["Banks"]["Lvl 2 Bank"].keys():
            for key in system["Banks"]["Lvl 2 Bank"].keys():
                if key not in current["Banks"]["Lvl 2 Bank"].keys():
                    current["Banks"]["Lvl 2 Bank"][key] = system["Banks"]["Lvl 2 Bank"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"]["Lvl 3 Bank"].keys() != system["Banks"]["Lvl 3 Bank"].keys():
            for key in system["Banks"]["Lvl 3 Bank"].keys():
                if key not in current["Banks"]["Lvl 3 Bank"].keys():
                    current["Banks"]["Lvl 3 Bank"][key] = system["Banks"]["Lvl 3 Bank"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"]["Lvl 4 Bank"].keys() != system["Banks"]["Lvl 4 Bank"].keys():
            for key in system["Banks"]["Lvl 4 Bank"].keys():
                if key not in current["Banks"].keys():
                    current["Banks"]["Lvl 4 Bank"][key] = system["Banks"]["Lvl 4 Bank"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)
        current = fileIO(f, "load")
        if current["Banks"]["Lvl 5 Bank"].keys() != system["Banks"]["Lvl 5 Bank"].keys():
            for key in system["Banks"]["Lvl 5 Bank"].keys():
                if key not in current["Banks"]["Lvl 5 Bank"].keys():
                    current["Banks"]["Lvl 5 Bank"][key] = system["Banks"]["Lvl 5 Bank"][key]
                    print("Adding " + str(key) +
                          " field to bankheist system.json")
            fileIO(f, "save", current)


def setup(bot):
    check_folders()
    check_files()
    n = Payday(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.vault_update())
