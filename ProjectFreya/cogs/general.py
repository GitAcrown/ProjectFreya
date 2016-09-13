import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from random import randint
from random import choice as randchoice
import datetime
import time
import aiohttp
import asyncio
import requests
import os
from urllib import request
from cleverbot import Cleverbot

settings = {"POLL_DURATION" : 60}
cb = Cleverbot()
headers = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36"

class General:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.stopwatches = {}
        self.ball = ["A ce que je vois, oui.", "C'est certain.", "J'hésite.", "Plutôt oui.", "Il semble que oui.",
                     "Les esprits penchent pour un oui.", "Sans aucun doute.", "Oui.", "Oui - C'est sûr.", "Tu peux compter dessus.", "Je ne sais pas.",
                     "Ta question n'est pas très interessante...", "Je ne vais pas te le dire.", "Je ne peux pas prédire le futur.", "Vaut mieux pas que te révelle la vérité.",
                     "n'y comptes pas.", "Ma réponse est non.", "Des sources fiables assurent que oui.", "J'en doute.", "Non, clairement."]
        self.poll_sessions = []
        
    @commands.command(hidden=True)
    async def ping(self):
        """Pong."""
        await self.bot.say("Pong.")

    @commands.command(pass_context=True)
    async def make(self, ctx, *objet):
        """Fait un objet en particulier."""
        objet = " ".join(objet)
        user = ctx.message.author
        await self.bot.say("**{}** en préparation ...".format(objet))
        wait = randint(15, 25)
        await asyncio.sleep(wait)
        await self.bot.say("Voilà {}, votre **{}** est prêt(e) !".format(user.mention, objet))

    @commands.command()
    async def choose(self, *choices):
        """Choisi parmis plusieurs choix.
        """
        choices = [escape_mass_mentions(choice) for choice in choices]
        if len(choices) < 2:
            await self.bot.say('Il n\'y a pas assez de choix.')
        else:
            await self.bot.say(randchoice(choices))

    @commands.command(hidden = True, pass_context=True)
    async def barre(self, ctx):
        """Affiche une barre de chargement en MP (test)"""
        channel = ctx.message.channel
        n = 0
        await self.bot.whisper("*Ceci est une fonction test*")
        msg = "**Chargement**"
        await self.bot.whisper(msg)
        async for message in self.bot.logs_from(channel, limit=1):
            if message.author.name == self.bot.user.name:
                while n != 11:
                    m = n * 10
                    msg = "**Chargement [" + str(m) + "%]**"
                    await self.bot.edit_message(message, msg)
                    await asyncio.sleep(1)
                    n += 1
                msg = "**Chargement terminé**"
                await self.bot.edit_message(message, msg)

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(kick_members=True)
    async def upload(self, ctx, nom: str = None):
        """Test l'upload"""
        if nom == None:
            msg = "**Voici les fichiers disponibles:**\n"
            dire = os.listdir("data/stk/image/")
            msg += '; '.join(x for x in dire if x)
            await self.bot.say(msg)
        else:
            channel = ctx.message.channel
            chemin = 'data/stk/image/'
            chemin += nom
            if nom in os.listdir("data/stk/image/"):
                await self.bot.say("**Upload en cours...**")
                try:
                    await self.bot.send_file(channel, chemin)
                except:
                    await self.bot.say("Je n'ai pas pu upload ce fichier.")
            else:
                await self.bot.say("Ce fichier n'existe pas.")

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(kick_members=True)
    async def download(self, ctx, url):
        """Test le download"""
        filename = url.split('/')[-1]
        await self.bot.say("Test Download...")
        try:
            f = open(filename, 'wb')
            f.write(request.urlopen(url).read())
            f.close()
            file = "data/autre/" + filename
            os.rename(filename,file)
            await self.bot.say("Terminé.")
        except Exception as e:
            print(e)
            print("Erreur, Impossible de télécharger l'image.")

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(kick_members=True)
    async def manuel(self, ctx):
        """Upload le manuel du modération."""
        channel = ctx.message.channel
        chemin = 'data/autre/Manuel.rtf'
        await self.bot.say("**Patientez pendant l'Upload du fichier...**")
        try:
            await self.bot.send_file(channel, chemin)
        except:
            await self.bot.say("Je n'ai pas pu upload ce fichier.")
        
    @commands.command(pass_context=True)
    async def roll(self, ctx, number : int = 100):
        """Sort un nombre aléatoire entre 1 et X

        Par défaut 100.
        """
        author = ctx.message.author
        if number > 1:
            n = str(randint(1, number))
            return await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
        else:
            return await self.bot.say("{} Plus haut que 1 ?".format(author.mention))

    @commands.command(pass_context=True)
    async def flip(self, ctx, user : discord.Member=None):
        """Lance une pièce ou retourne un utilisateur..

        Par défaut une pièce.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "Bien essayé. Tu penses que c'est drôle ? Si on faisait *ça* à la place:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            return await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            return await self.bot.say("*Lance une pièce et... " + randchoice(["FACE !*", "PILE !*"]))

    @commands.command(pass_context=True)
    async def rps(self, ctx, choice : str):
        """Joue à Rock Paper Scissors (EN)"""
        author = ctx.message.author
        rpsbot = {"rock" : ":moyai:",
           "paper": ":page_facing_up:",
           "scissors":":scissors:"}
        choice = choice.lower()
        if choice in rpsbot.keys():
            botchoice = randchoice(list(rpsbot.keys()))
            msgs = {
                "win": " T'as gagné {}!".format(author.mention),
                "square": " Nous sommes à égalité {}!".format(author.mention),
                "lose": " T'as perdu {}!".format(author.mention)
            }
            if choice == botchoice:
                await self.bot.say(rpsbot[botchoice] + msgs["square"])
            elif choice == "rock" and botchoice == "paper":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "rock" and botchoice == "scissors":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
            elif choice == "paper" and botchoice == "rock":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
            elif choice == "paper" and botchoice == "scissors":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "scissors" and botchoice == "rock":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "scissors" and botchoice == "paper":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
        else:
            await self.bot.say("Choose rock, paper or scissors.")

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, *question):
        """Pose une question au bot

        Il ne réponds que par OUI ou NON.
        """
        question = " ".join(question)
        if question.endswith("?") and question != "?":
            return await self.bot.say("`" + randchoice(self.ball) + "`")
        else:
            return await self.bot.say("Ce n'est pas une question ça.")

    @commands.command(aliases=["t"], pass_context=True)
    async def talk(self, ctx, *msg):
        """Pour discuter avec le bot en public"""
        msg = " ".join(msg)
        await self.bot.say(str(cb.ask(msg)))

    @commands.command(aliases=["sw"], pass_context=True)
    async def stopwatch(self, ctx):
        """Démarre ou arrête un Compte à rebours."""
        author = ctx.message.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await self.bot.say(author.mention + " CaR démarré !")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await self.bot.say(author.mention + " CaR arrêté ! Temps: **" + str(tmp) + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, *, search_terms : str):
        """Crée un lien lmgtfy"""
        search_terms = escape_mass_mentions(search_terms.replace(" ", "+"))
        await self.bot.say("http://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(no_pm=True, hidden=True)
    async def hug(self, user : discord.Member, intensity : int=1):
        """Parce que tout le monde aime les calins.

        Avec 10 niveaux d'intensité.."""
        name = " *" + user.name + "*"
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ" + name + " ⊂(´・ω・｀⊂)"
        await self.bot.say(msg)

    @commands.command()
    async def updown(self, url):
        """Recherche si un site est disponible ou pas."""
        if url == "":
            await self.bot.say("Vous n'avez pas rentré de site à rechercher.")
            return
        if "http://" not in url or "https://" not in url:
            url = "http://" + url
        try:
            with aiohttp.Timeout(15):
                await self.bot.say("Test de " + url + "…")
                try:
                    response = await aiohttp.get(url, headers = { 'user_agent': headers })
                    if response.status == 200:
                        await self.bot.say(url + " semble répondre correctement.")
                    else:
                        await self.bot.say(url + " ne réponds pas. Le site est mort.")
                except:
                    await self.bot.say(url + " est down.")
        except asyncio.TimeoutError:
            await self.bot.say(url + " est down.")

    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, user : discord.Member = None):
        """Montre les informations à propos d'un utilisateur."""
        author = ctx.message.author
        if not user:
            user = author
        roles = [x.name for x in user.roles if x.name != "@everyone"]
        if not roles: roles = ["None"]
        data = "```python\n"
        data += "Nom: {}\n".format(escape_mass_mentions(str(user)))
        data += "ID: {}\n".format(user.id)
        passed = (ctx.message.timestamp - user.created_at).days
        data += "Crée: {} (Il y a {} jours)\n".format(user.created_at, passed)
        passed = (ctx.message.timestamp - user.joined_at).days
        data += "Join: {} (Il y a {} jours)\n".format(user.joined_at, passed)
        data += "Rôles: {}\n".format(", ".join(roles))
        data += "Avatar: {}\n".format(user.avatar_url)
        data += "```"
        await self.bot.say(data)

    @commands.command(aliases=["gen"], pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def generate(self, ctx, user : discord.Member = None):
        """Montre un ensemble d'infos sur un utilisateur. Réservé à la modération."""
        author = ctx.message.author
        server = user.server
        if user.id == "172376505354158080" or "173913763932667904":
            spy = "\n Alors, comme ça on espionne un Administrateur ?"
        if not user:
            user = author
        roles = [x.name for x in user.roles if x.name != "@everyone"]
        if not roles: roles = ["None"]
        data ="__**Infos**__"
        data += " (__Générés depuis \"**{}**\"__)\n".format(server.name)
        data += "**Nom**: {}\n".format(escape_mass_mentions(str(user)))
        data += "**ID**: {}\n".format(user.id)
        passed = (ctx.message.timestamp - user.created_at).days
        data += "**Crée**: {} (Il y a __{}__ jours)\n".format(user.created_at, passed)
        passed = (ctx.message.timestamp - user.joined_at).days
        data += "**Join**: {} (Il y a __{}__ jours)\n".format(user.joined_at, passed)
        data += "**Rôles**: {}\n".format(", ".join(roles))
        data += "**Avatar**: {}\n".format(user.avatar_url)
        await self.bot.whisper(data)

        server = user.server
        names = self.past_names[user.id] if user.id in self.past_names else None
        try:
            nicks = self.past_nicknames[server.id][user.id]
            nicks = [escape_mass_mentions(nick) for nick in nicks]
        except:
            nicks = None
        msg = "**__A propos du pseudo:__**\n"
        if names:
            names = [escape_mass_mentions(name) for name in names]
            msg += "**20 Derniers noms**:\n"
            msg += ", ".join(names)
        if nicks:
            if msg:
                msg += "\n\n"
            msg += "**20 Derniers surnoms**:\n"
            msg += ", ".join(nicks)
        if msg:
            await self.bot.whisper(msg)
        else:
            await self.bot.whisper("Je n'ai enregistré aucun changement de sa part.")

        await self.bot.whisper(spy)

    @commands.command(pass_context=True, no_pm=True)
    async def serverinfo(self, ctx):
        """Montre les infos du serveur."""
        server = ctx.message.server
        online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
        total_users = str(len(server.members))
        text_channels = len([x for x in server.channels if str(x.type) == "text"])
        voice_channels = len(server.channels) - text_channels

        data = "```python\n"
        data += "Nom: {}\n".format(server.name)
        data += "ID: {}\n".format(server.id)
        data += "Region: {}\n".format(server.region)
        data += "Utilisateurs: {}/{}\n".format(online, total_users)
        data += "Canaux Textuels: {}\n".format(text_channels)
        data += "Canaux Vocaux: {}\n".format(voice_channels)
        data += "Rôles: {}\n".format(len(server.roles))
        passed = (ctx.message.timestamp - server.created_at).days
        data += "Crée: {} (Il y a {} jours)\n".format(server.created_at, passed)
        data += "Propriétaire: {}\n".format(server.owner)
        data += "Icône: {}\n".format(server.icon_url)
        data += "```"
        await self.bot.say(data)

    @commands.command()
    async def urban(self, *, search_terms : str, definition_number : int=1):
        """Recherche dans le Urban Dictionnary (EN)

        Le nombre de définitions doit être entre 1 et 10"""
        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user
        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
        except ValueError:
            pos = 0
        search_terms = "+".join(search_terms)
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.get(url) as r:
                result = await r.json()
            if result["list"]:
                definition = result['list'][pos]['definition']
                example = result['list'][pos]['example']
                defs = len(result['list'])
                msg = ("**Definition #{} sur {}:\n**{}\n\n"
                       "**Exemple:\n**{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await self.bot.say(page)
            else:
                await self.bot.say("Aucun résultat")
        except IndexError:
            await self.bot.say("Aucune définition #{}".format(pos+1))
        except:
            await self.bot.say("Erreur.")

    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, ctx, *text):
        """Démarre ou arrête un poll."""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Eheh, bien essayé.")
                return
            p = NewPoll(message, self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await self.bot.say("poll question;option1;option2 (...)")
        else:
            await self.bot.say("Un poll est déjà en execution.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id: # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say("L'auteur ou l'admin sont les seuls à pouvoir stopper ça.")
        else:
            await self.bot.say("Aucun poll sur ce channel.")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                    self.getPollByChannel(message).checkAnswer(message)


class NewPoll():
    def __init__(self, message, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        msg = message.content[6:]
        msg = msg.split(";")
        if len(msg) < 2: # Au moins une question avec 2 réponses
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for answer in msg: # {id : {answer, votes}}
            self.answers[i] = {"ANSWER" : answer, "VOTES" : 0}
            i += 1

    async def start(self):
        msg = "**POLL DEMARRE !**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["ANSWER"])
        msg += "\nTapez le chiffre pour voter !"
        await self.client.send_message(self.channel, msg)
        await asyncio.sleep(settings["POLL_DURATION"])
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**POLL ARRETE !**\n\n{}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "*{}* - {} votes\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_sessions.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass

def setup(bot):
    n = General(bot)
    bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
