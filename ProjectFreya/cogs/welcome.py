import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import send_cmd_help
import os


default_greeting = "Bienvenue à {0.name} sur {1.name} !"
default_departing = "Bye {0.name} !"
default_settings = {"GREETING": default_greeting, "ON": False, "CHANNEL": None, "GREETINGDEP" : default_departing, "ONDEP": False}

class Welcome:
    """Gère l'arrivée et le départ de membres sur le serveurs."""

    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/welcome/settings.json", "load")

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def welcomeset(self, ctx):
        """Change les paramètres pour l'arrivée"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["CHANNEL"] = server.default_channel.id
            fileIO("data/welcome/settings.json","save",self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            msg += "MESSAGE: {}\n".format(self.settings[server.id]["GREETING"])
            msg += "CHANNEL: #{}\n".format(self.get_welcome_channel(server)) 
            msg += "SUR: {}\n".format(self.settings[server.id]["ON"]) 
            msg += "```"
            await self.bot.say(msg)

    @welcomeset.command(pass_context=True)
    async def greetingw(self, ctx, *, format_msg):
        """Change le message d'acceuil.

        {0} est l'utilisateur
        {1} est le serveur
        Par défaut: 
            Bienvenue à {0.name} sur {1.name}!

        Exemples:
            {0.mention}.. Que fait-tu ici ?
            {1.name} acceuil un nouveau membre ! {0.name}#{0.discriminator} - {0.id}
            Un nouveau vient d'arriver ! Qui est-ce ?! D: Est-il là pour nous blesser ?!
        """
        server = ctx.message.server
        self.settings[server.id]["GREETING"] = format_msg
        fileIO("data/welcome/settings.json","save",self.settings)
        await self.bot.say("Message changé pour ce serveur.")
        await self.send_testing_msg(ctx, 0)

    @welcomeset.command(pass_context=True)
    async def togglew(self, ctx):
        """Active ou désactive cette fonction"""
        server = ctx.message.server
        self.settings[server.id]["ON"] = not self.settings[server.id]["ON"]
        if self.settings[server.id]["ON"]:
            await self.bot.say("Je vais désormais acceuillir les utilisateurs sur ce serveur.")
            await self.send_testing_msg(ctx, 0)
        else:
            await self.bot.say("je ne vais plus acceuillir les utilisateurs sur ce serveur.")
        fileIO("data/welcome/settings.json", "save", self.settings)

    @welcomeset.command(pass_context=True)
    async def channelw(self, ctx, channel : discord.Channel=None): 
        """Change le canal où le message est envoyé

        Si aucun canal n'est désigné, ce sera le canal d'entrée du serveur par défaut."""
        server = ctx.message.server
        if channel == None:
            channel = ctx.message.server.default_channel
        if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
            await self.bot.say("Je n'ai pas les permissions pour ce channel {0.mention}".format(channel))
            return
        self.settings[server.id]["CHANNEL"] = channel.id
        fileIO("data/welcome/settings.json", "save", self.settings)
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(channel,"Je vais maintenant envoyer un message sur {0.mention}".format(channel))
        await self.send_testing_msg(ctx, 0)

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def departset(self, ctx):
        """Change les paramètres pour le départ"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["CHANNEL"] = server.default_channel.id
            fileIO("data/welcome/settings.json","save",self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            msg += "MESSAGE: {}\n".format(self.settings[server.id]["GREETINGDEP"])
            msg += "CHANNEL: #{}\n".format(self.get_welcome_channel(server)) 
            msg += "ON: {}\n".format(self.settings[server.id]["ONDEP"]) 
            msg += "```"
            await self.bot.say(msg)

    @departset.command(pass_context=True)
    async def greetingd(self, ctx, *, format_msg):
        """Change le message de départ.

        {0} est l'utilisateur
        {1} est le serveur
        Par défaut: 
            Au revoir {0.name} sur {1.name}!

        Exemples:
            {0.mention}.. Pourquoi toi ?
            {1.name} se barre ! {0.name}#{0.discriminator} - {0.id}
            OH NON, ILS S'ECHAPPENT !
        """
        server = ctx.message.server
        self.settings[server.id]["GREETINGDEP"] = format_msg
        fileIO("data/welcome/settings.json","save",self.settings)
        await self.bot.say("Message changé pour ce serveur.")
        await self.send_testing_msg(ctx, 1)

    @departset.command(pass_context=True)
    async def toggled(self, ctx):
        """Active ou désactive cette fonction"""
        server = ctx.message.server
        self.settings[server.id]["ONDEP"] = not self.settings[server.id]["ONDEP"]
        if self.settings[server.id]["ONDEP"]:
            await self.bot.say("Je vais désormais acceuillir les utilisateurs sur ce serveur.")
            await self.send_testing_msg(ctx, 1)
        else:
            await self.bot.say("je ne vais plus acceuillir les utilisateurs sur ce serveur.")
        fileIO("data/welcome/settings.json", "save", self.settings)

    @departset.command(pass_context=True)
    async def channeld(self, ctx, channel : discord.Channel=None): 
        """Change le canal où le message est envoyé

        Si aucun canal n'est désigné, ce sera le canal d'entrée du serveur par défaut."""
        server = ctx.message.server
        if channel == None:
            channel = ctx.message.server.default_channel
        if not server.get_member(self.bot.user.id).permissions_in(channel).send_messages:
            await self.bot.say("Je n'ai pas les permissions pour ce channel {0.mention}".format(channel))
            return
        self.settings[server.id]["CHANNEL"] = channel.id
        fileIO("data/welcome/settings.json", "save", self.settings)
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(channel,"Je vais maintenant envoyer un message sur {0.mention}".format(channel))
        await self.send_testing_msg(ctx, 1)


    async def member_join(self, member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["CHANNEL"] = server.default_channel.id
            fileIO("data/welcome/settings.json","save",self.settings)
        if not self.settings[server.id]["ON"]:
            return
        if server == None:
            print("Il y a eu une erreur. L'utilisateur était {}".format(member.name))
            return
        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server):
            await self.bot.send_message(channel, self.settings[server.id]["GREETING"].format(member, server))
        else:
            print("Erreur de permissions, Utilisateur: {0.name}".format(member))
            print("Je n'ai pas les autorisations pour envoyer sur {0.name} #{1.name}".format(server,channel))

    async def member_remove(self, member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["CHANNEL"] = server.default_channel.id
            fileIO("data/welcome/settings.json","save",self.settings)
        if not self.settings[server.id]["ONDEP"]:
            return
        if server == None:
            print("Il y a eu une erreur. L'utilisateur qui est parti était {}".format(member.name))
            return
        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server):
            await self.bot.send_message(channel, self.settings[server.id]["GREETINGDEP"].format(member, server))
        else:
            print("Erreur de permissions, Utilisateur: {0.name}".format(member))
            print("Je n'ai pas les autorisations pour envoyer sur {0.name} #{1.name}".format(server,channel))


    def get_welcome_channel(self, server):
        return server.get_channel(self.settings[server.id]["CHANNEL"])

    def speak_permissions(self, server):
        channel = self.get_welcome_channel(server)
        return server.get_member(self.bot.user.id).permissions_in(channel).send_messages

    async def send_testing_msg(self, ctx, type):
        server = ctx.message.server
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(ctx.message.channel, "`Message de test envoyé sur`{0.mention}".format(channel))
        if type== 0:
            if self.speak_permissions(server):
                await self.bot.send_message(channel, self.settings[server.id]["GREETING"].format(ctx.message.author,server))
            else: 
                await self.bot.send_message(ctx.message.channel,"Je n'ai pas les autorisations pour {0.mention}".format(channel))
        else:
            if self.speak_permissions(server):
                await self.bot.send_message(channel, self.settings[server.id]["GREETINGDEP"].format(ctx.message.author,server))
            else: 
                await self.bot.send_message(ctx.message.channel,"Je n'ai pas les autorisations pour {0.mention}".format(channel))
        

def check_folders():
    if not os.path.exists("data/welcome"):
        print("Creating data/welcome folder...")
        os.makedirs("data/welcome")

def check_files():
    f = "data/welcome/settings.json"
    if not fileIO(f, "check"):
        print("Creating welcome settings.json...")
        fileIO(f, "save", {})


def setup(bot):
    check_folders()
    check_files()
    n = Welcome(bot)
    bot.add_listener(n.member_join,"on_member_join")
    bot.add_listener(n.member_remove,"on_member_remove")
    bot.add_cog(n)
