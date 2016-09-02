import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import user_allowed, send_cmd_help
import os

#Red's Original

class CustomCommands:
    """Commandes customisées."""

    def __init__(self, bot):
        self.bot = bot
        self.c_commands = fileIO("data/customcom/commands.json", "load")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(administrator=True)
    async def addcom(self, ctx, command : str, *, text):
        """Ajoute une commande custom
        """
        server = ctx.message.server
        command = command.lower()
        if command in self.bot.commands.keys():
            await self.bot.say("Cette commande est déjà une commande basique.")
            return
        if not server.id in self.c_commands:
            self.c_commands[server.id] = {}
        cmdlist = self.c_commands[server.id]
        if command not in cmdlist:
            cmdlist[command] = text
            self.c_commands[server.id] = cmdlist
            fileIO("data/customcom/commands.json", "save", self.c_commands)
            await self.bot.say("Ajoutée.")
        else:
            await self.bot.say("La commande existe déjà. Utilisez editcom pour l'éditer.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(administrator=True)
    async def editcom(self, ctx, command : str, *, text):
        """Edite une commande custom
        """
        server = ctx.message.server
        command = command.lower()
        if server.id in self.c_commands:
            cmdlist = self.c_commands[server.id]
            if command in cmdlist:
                cmdlist[command] = text
                self.c_commands[server.id] = cmdlist
                fileIO("data/customcom/commands.json", "save", self.c_commands)
                await self.bot.say("Editée..")
            else:
                await self.bot.say("Cette commande n'existe pas. Utilisez addcom pour la créer.")
        else:
             await self.bot.say("Aucune commande n'a été enregistrée sur ce serveur.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(administrator=True)
    async def delcom(self, ctx, command : str):
        """Supprime une commande custom."""
        server = ctx.message.server
        command = command.lower()
        if server.id in self.c_commands:
            cmdlist = self.c_commands[server.id]
            if command in cmdlist:
                cmdlist.pop(command, None)
                self.c_commands[server.id] = cmdlist
                fileIO("data/customcom/commands.json", "save", self.c_commands)
                await self.bot.say("Supprimée.")
            else:
                await self.bot.say("Cette commande n'existe pas.")
        else:
            await self.bot.say("Aucune commande enregistrée sur ce serveur.")

    @commands.command(pass_context=True, no_pm=True)
    async def customcommands(self, ctx):
        """Montre la liste des commandes custom."""
        server = ctx.message.server
        if server.id in self.c_commands:
            cmdlist = self.c_commands[server.id]
            if cmdlist:
                i = 0
                msg = ["```Commandes custom:\n"]
                for cmd in sorted([cmd for cmd in cmdlist.keys()]):
                    if len(msg[i]) + len(ctx.prefix) + len(cmd) + 5 > 2000:
                        msg[i] += "```"
                        i += 1
                        msg.append("``` {}{}\n".format(ctx.prefix, cmd))
                    else:
                        msg[i] += " {}{}\n".format(ctx.prefix, cmd)
                msg[i] += "```"
                for cmds in msg:
                    await self.bot.whisper(cmds)
            else:
                await self.bot.say("Aucune commande enregistrée sur ce serveur.")
        else:
            await self.bot.say("Il n'y a pas de commandes sur ce serveur.")

    async def checkCC(self, message):
        if message.author.id == self.bot.user.id or len(message.content) < 2 or message.channel.is_private:
            return

        if not user_allowed(message):
            return

        msg = message.content
        server = message.server
        prefix = self.get_prefix(msg)

        if prefix and server.id in self.c_commands.keys():
            cmdlist = self.c_commands[server.id]
            cmd = msg[len(prefix):]
            if cmd in cmdlist.keys():
                await self.bot.send_message(message.channel, cmdlist[cmd])
            elif cmd.lower() in cmdlist.keys():
                await self.bot.send_message(message.channel, cmdlist[cmd.lower()])

    def get_prefix(self, msg):
        for p in self.bot.command_prefix:
            if msg.startswith(p):
                return p
        return False

def check_folders():
    if not os.path.exists("data/customcom"):
        print("Creating data/customcom folder...")
        os.makedirs("data/customcom")

def check_files():
    f = "data/customcom/commands.json"
    if not fileIO(f, "check"):
        print("Creating empty commands.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = CustomCommands(bot)
    bot.add_listener(n.checkCC, "on_message")
    bot.add_cog(n)
