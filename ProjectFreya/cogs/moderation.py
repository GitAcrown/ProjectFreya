import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
from collections import deque
from cogs.utils.chat_formatting import escape_mass_mentions
import os
import logging
import asyncio


class Mod:
    """Outils de modération."""

    def __init__(self, bot):
        self.bot = bot
        self.whitelist_list = dataIO.load_json("data/mod/whitelist.json")
        self.blacklist_list = dataIO.load_json("data/mod/blacklist.json")
        self.ignore_list = dataIO.load_json("data/mod/ignorelist.json")
        self.filter = dataIO.load_json("data/mod/filter.json")
        self.past_names = dataIO.load_json("data/mod/past_names.json")
        self.past_nicknames = dataIO.load_json("data/mod/past_nicknames.json")

    @commands.group(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def modset(self, ctx):
        """Change les paramètres."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @modset.command(name="adminrole", pass_context=True, no_pm=True)
    async def _modset_adminrole(self, ctx, role_name: str):
        """Change le rôle d'administrateur sur le serveur."""
        server = ctx.message.server
        if server.id not in settings.servers:
            await self.bot.say("N'oubliez pas le rôle de modérateur.")
        settings.set_server_admin(server, role_name)
        await self.bot.say("Reglé à '{}'".format(role_name))

    @modset.command(name="modrole", pass_context=True, no_pm=True)
    async def _modset_modrole(self, ctx, role_name: str):
        """Change le rôle de modérateur sur le serveur."""
        server = ctx.message.server
        if server.id not in settings.servers:
            await self.bot.say("N'oubliez pas le rôle d'administrateur aussi.")
        settings.set_server_mod(server, role_name)
        await self.bot.say("Reglé à '{}'".format(role_name))

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member):
        """Kick un utilisateur."""
        author = ctx.message.author
        try:
            await self.bot.kick(user)
            logger.info("{}({}) à kické {}({})".format(
                author.name, author.id, user.name, user.id))
            await self.bot.say("Fait.")
        except discord.errors.Forbidden:
            await self.bot.say("Je ne suis pas autorisé à faire ça.")
        except Exception as e:
            print(e)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, days: int=1):
        """Ban un utilisateur et supprime x jours de messages.

        Par défaut le dernier jour."""
        author = ctx.message.author
        if days < 0 or days > 7:
            await self.bot.say("Les jours doivent être compris entre 0 et 7.")
            return
        try:
            await self.bot.ban(user, days)
            logger.info("{}({}) banned {}({}), deleting {} days worth of messages".format(
                author.name, author.id, user.name, user.id, str(days)))
            await self.bot.say("Fait.")
        except discord.errors.Forbidden:
            await self.bot.say("Je ne suis pas autorisé à le faire.")
        except Exception as e:
            print(e)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def neutral(self, ctx, user: discord.Member):
        """Renvoie l'utilisateur et efface un jour de message

        Différent d'un ban ou d'un kick."""
        server = ctx.message.server
        channel = ctx.message.channel
        can_ban = channel.permissions_for(server.me).ban_members
        author = ctx.message.author
        if can_ban:
            try:
                try: # We don't want blocked DMs preventing us from banning
                    msg = await self.bot.send_message(user, "Tu as été neutralisé. Nous venons d'effacer tes messages, tu peux si tu veux rejoindre à nouveau le serveur.")
                except:
                    pass
                await self.bot.ban(user, 1)
                logger.info("{}({}) à neutralisé {}({}) ".format(author.name, author.id, user.name,
                     user.id))
                await self.bot.unban(server, user)
                await self.bot.say("Fait.")
            except discord.errors.Forbidden:
                await self.bot.say("Je n'ai pas le droit de faire ça.")
                await self.bot.delete_message(msg)
            except Exception as e:
                print(e)
        else:
            await self.bot.say("Je n'ai pas les autorisations pour faire ça.")

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user : discord.Member, *, nickname=""):
        """Change le pseudo d'un utilisateur (Sur le serveur)."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(user, nickname)
            await self.bot.say("Fait")
        except discord.Forbidden:
            await self.bot.say("Je n'ai pas les autorisations pour le faire")

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def cleanup(self, ctx):
        """Supprime les messages (Voir les différents modes)"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @cleanup.command(pass_context=True, no_pm=True)
    async def text(self, ctx, text: str, number: int):
        """Supprime les X derniers messages contenant le texte désiré."""

        channel = ctx.message.channel
        server = channel.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        def check(m):
            if text in m.content:
                return True
            elif m == ctx.message:
                return True
            else:
                return False

        to_delete = [ctx.message]

        if not has_permissions:
            await self.bot.say("Je ne suis pas autorisé à faire ça.")
            return

        tries_left = 5
        tmp = ctx.message

        while tries_left and len(to_delete) - 1 < number:
            async for message in self.bot.logs_from(channel, limit=100,
                                                    before=tmp):
                if len(to_delete) - 1 < number and check(message):
                    to_delete.append(message)
                tmp = message
            tries_left -= 1

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @cleanup.command(pass_context=True, no_pm=True)
    async def user(self, ctx, user: discord.Member, number: int):
        """Supprime les X derniers messages d'un utilisateur."""

        channel = ctx.message.channel
        server = channel.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        def check(m):
            if m.author == user:
                return True
            elif m == ctx.message:
                return True
            else:
                return False

        to_delete = [ctx.message]

        if not has_permissions:
            await self.bot.say("Je ne suis pas autorisé à faire ça.")
            return

        tries_left = 5
        tmp = ctx.message

        while tries_left and len(to_delete) - 1 < number:
            async for message in self.bot.logs_from(channel, limit=100,
                                                    before=tmp):
                if len(to_delete) -1 < number and check(message):
                    to_delete.append(message)
                tmp = message
            tries_left -= 1

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @cleanup.command(pass_context=True, no_pm=True)
    async def after(self, ctx, message_id : int):
        """Supprime les messages après un message spécifique (ID nécéssaire)
        """

        channel = ctx.message.channel
        server = channel.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        after = await self.bot.get_message(channel, message_id)

        if not has_permissions:
            await self.bot.say("Je ne suis pas autorisé à faire ça.")
            return
        elif not after:
            await self.bot.say("Message inexistant.")
            return

        async for message in self.bot.logs_from(channel, limit=2000,
                                                after=after):
            to_delete.append(message)

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @cleanup.command(pass_context=True, no_pm=True)
    async def mess(self, ctx, number: int):
        """Supprime les X derniers messages."""

        channel = ctx.message.channel
        server = channel.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        if not has_permissions:
            await self.bot.say("Je ne suis pas autorisé à faire ça.")
            return

        async for message in self.bot.logs_from(channel, limit=number+1):
            to_delete.append(message)

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def blacklist(self, ctx):
        """Interdit un utilisateur l'utilisation du bot"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @blacklist.command(name="add")
    async def _blacklist_add(self, user: discord.Member):
        """Ajoute l'utilisateur à la BL"""
        if user.id not in self.blacklist_list:
            self.blacklist_list.append(user.id)
            dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
            await self.bot.say("Ajouté à la blacklist.")
        else:
            await self.bot.say("Utilisateur déjà blacklisté.")

    @blacklist.command(name="remove")
    async def _blacklist_remove(self, user: discord.Member):
        """Enlève un utilisateur de la BL."""
        if user.id in self.blacklist_list:
            self.blacklist_list.remove(user.id)
            dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
            await self.bot.say("Retiré de la blacklist.")
        else:
            await self.bot.say("Cet utilisateur n'est pas dans la BL.")

    @blacklist.command(name="clear")
    async def _blacklist_clear(self):
        """Permet de nettoyer la blacklisy"""
        self.blacklist_list = []
        dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
        await self.bot.say("Vidée.")

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def whitelist(self, ctx):
        """Utilisateurs qui seront autorisés à utiliser le bot."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @whitelist.command(name="add")
    async def _whitelist_add(self, user: discord.Member):
        """Ajoute des utilisateurs à la WL"""
        if user.id not in self.whitelist_list:
            if not self.whitelist_list:
                msg = "\nLes utilisateurs qui ne sont pas dans la WL serot ignorés (Admins et modérateurs exclus)"
            else:
                msg = ""
            self.whitelist_list.append(user.id)
            dataIO.save_json("data/mod/whitelist.json", self.whitelist_list)
            await self.bot.say("Ajouté." + msg)
        else:
            await self.bot.say("Déjà dans la WL.")

    @whitelist.command(name="remove")
    async def _whitelist_remove(self, user: discord.Member):
        """Removes user from bot's whitelist"""
        if user.id in self.whitelist_list:
            self.whitelist_list.remove(user.id)
            dataIO.save_json("data/mod/whitelist.json", self.whitelist_list)
            await self.bot.say("Retiré.")
        else:
            await self.bot.say("Il n'est pas dans la WL.")

    @whitelist.command(name="clear")
    async def _whitelist_clear(self):
        """Efface la whitelist"""
        self.whitelist_list = []
        dataIO.save_json("data/mod/whitelist.json", self.whitelist_list)
        await self.bot.say("Vidée.")

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def ignore(self, ctx):
        """Ajoute un serveur ou un channel à la liste des ignorés."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say(self.count_ignored())

    @ignore.command(name="channel", pass_context=True)
    async def ignore_channel(self, ctx, channel: discord.Channel=None):
        """Ignore le channel"""
        current_ch = ctx.message.channel
        if not channel:
            if current_ch.id not in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].append(current_ch.id)
                fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
                await self.bot.say("Ajouté à la liste.")
            else:
                await self.bot.say("Il est déjà ignoré.")
        else:
            if channel.id not in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].append(channel.id)
                fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
                await self.bot.say("CAjouté à la liste.")
            else:
                await self.bot.say("Déjà ignoré.")

    @ignore.command(name="server", pass_context=True)
    async def ignore_server(self, ctx):
        """Ignore le serveur"""
        server = ctx.message.server
        if server.id not in self.ignore_list["SERVERS"]:
            self.ignore_list["SERVERS"].append(server.id)
            fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
            await self.bot.say("Ajouté à la ligne.")
        else:
            await self.bot.say("Déjà ignoré.")

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def unignore(self, ctx):
        """Retire un channel ou un serveur de la liste des ignorés."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            await self.bot.say(self.count_ignored())

    @unignore.command(name="channel", pass_context=True)
    async def unignore_channel(self, ctx, channel: discord.Channel=None):
        """Enlève le channel des ignorés"""
        current_ch = ctx.message.channel
        if not channel:
            if current_ch.id in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].remove(current_ch.id)
                fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
                await self.bot.say("Retiré.")
            else:
                await self.bot.say("Ce channel n'est pas présent dans la liste.")
        else:
            if channel.id in self.ignore_list["CHANNELS"]:
                self.ignore_list["CHANNELS"].remove(channel.id)
                fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
                await self.bot.say("Retiré.")
            else:
                await self.bot.say("Ce channel n'est pas présent dans la liste.")

    @unignore.command(name="server", pass_context=True)
    async def unignore_server(self, ctx):
        """Removes current server from ignore list"""
        server = ctx.message.server
        if server.id in self.ignore_list["SERVERS"]:
            self.ignore_list["SERVERS"].remove(server.id)
            fileIO("data/mod/ignorelist.json", "save", self.ignore_list)
            await self.bot.say("Serveur retiré.")
        else:
            await self.bot.say("Ce serveur n'est pas dans la liste des ignorés.")

    def count_ignored(self):
        msg = "```Ignorés:\n"
        msg += str(len(self.ignore_list["CHANNELS"])) + " channels\n"
        msg += str(len(self.ignore_list["SERVERS"])) + " servers\n```\n"
        return msg

    @commands.group(name="filter", pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def _filter(self, ctx):
        """Ajoute/Retire des mots du filtre."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            server = ctx.message.server
            author = ctx.message.author
            msg = ""
            if server.id in self.filter.keys():
                if self.filter[server.id] != []:
                    word_list = self.filter[server.id]
                    for w in word_list:
                        msg += '"' + w + '" '
                    await self.bot.send_message(author, "Mots filtrés sur ce serveur: " + msg)

    @_filter.command(name="add", pass_context=True)
    async def filter_add(self, ctx, *words: str):
        """Ajoute un mot au filtre

        Utilisez des guillemets pour une chaine de mots."""
        if words == ():
            await send_cmd_help(ctx)
            return
        server = ctx.message.server
        added = 0
        if server.id not in self.filter.keys():
            self.filter[server.id] = []
        for w in words:
            if w.lower() not in self.filter[server.id] and w != "":
                self.filter[server.id].append(w.lower())
                added += 1
        if added:
            fileIO("data/mod/filter.json", "save", self.filter)
            await self.bot.say("Mots ajoutés.")
        else:
            await self.bot.say("Mots déjà dans le filtre.")

    @_filter.command(name="remove", pass_context=True)
    async def filter_remove(self, ctx, *words: str):
        """Retire des mots du filtre"""
        if words == ():
            await send_cmd_help(ctx)
            return
        server = ctx.message.server
        removed = 0
        if server.id not in self.filter.keys():
            await self.bot.say("Il n'y a pas de mots filtrés sur ce serveur.")
            return
        for w in words:
            if w.lower() in self.filter[server.id]:
                self.filter[server.id].remove(w.lower())
                removed += 1
        if removed:
            fileIO("data/mod/filter.json", "save", self.filter)
            await self.bot.say("Mots retirés.")
        else:
            await self.bot.say("Mots non présents dans le filtre.")

    @commands.group(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def editrole(self, ctx):
        """Change les paramètres de rôles"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @editrole.command(aliases=["color"], pass_context=True)
    async def colour(self, ctx, role: discord.Role, value: discord.Colour):
        """Change la couleur d'un rôle."""
        author = ctx.message.author
        try:
            await self.bot.edit_role(ctx.message.server, role, color=value)
            logger.info("{}({}) à changé la couleur de '{}'".format(
                author.name, author.id, role.name))
            await self.bot.say("Fait.")
        except discord.Forbidden:
            await self.bot.say("Je n'ai pas ce qu'il faut pour faire ça.")
        except Exception as e:
            print(e)
            await self.bot.say("Hum, j'ai pas réussi à le faire.")

    @editrole.command(name="name", pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def edit_role_name(self, ctx, role: discord.Role, name: str):
        """Chnage le nom d'un rôle."""
        if name == "":
            await self.bot.say("Le nom ne peut pas être vide.")
            return
        try:
            author = ctx.message.author
            old_name = role.name  # probably not necessary?
            await self.bot.edit_role(ctx.message.server, role, name=name)
            logger.info("{}({}) à changé le nom de '{}' à '{}'".format(
                author.name, author.id, old_name, name))
            await self.bot.say("Fait.")
        except discord.Forbidden:
            await self.bot.say("J'ai besoin des permissions d'abord.")
        except Exception as e:
            print(e)
            await self.bot.say("Quelque chose s'est mal passé...")

    @commands.command()
    async def names(self, user : discord.Member):
        """Montre les anciens noms d'un utilisateur."""
        server = user.server
        names = self.past_names[user.id] if user.id in self.past_names else None
        try:
            nicks = self.past_nicknames[server.id][user.id]
            nicks = [escape_mass_mentions(nick) for nick in nicks]
        except:
            nicks = None
        msg = ""
        if names:
            names = [escape_mass_mentions(name) for name in names]
            msg += "**20 derniers noms**:\n"
            msg += ", ".join(names)
        if nicks:
            if msg:
                msg += "\n\n"
            msg += "**20 derniers surnoms**:\n"
            msg += ", ".join(nicks)
        if msg:
            await self.bot.say(msg)
        else:
            await self.bot.say("Cet utilisateur est clean à ma connaissance.")

    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.delete_message(messages)
            await asyncio.sleep(1.5)

    async def slow_deletion(self, messages):
        for message in messages:
            try:
                await self.bot.delete_message(message)
            except:
                pass
            await asyncio.sleep(1.5)

    async def _delete_message(self, message):
        try:
            await self.bot.delete_message(message)
        except discord.errors.NotFound:
            pass
        except:
            raise

    def immune_from_filter(self, message):
        user = message.author
        server = message.server
        admin_role = settings.get_server_admin(server)
        mod_role = settings.get_server_mod(server)

        if user.id == settings.owner:
            return True
        elif discord.utils.get(user.roles, name=admin_role):
            return True
        elif discord.utils.get(user.roles, name=mod_role):
            return True
        else:
            return False

    async def check_filter(self, message):
        if message.channel.is_private:
            return
        server = message.server
        can_delete = message.channel.permissions_for(server.me).manage_messages

        if (message.author.id == self.bot.user.id or
        self.immune_from_filter(message) or not can_delete): # Owner, admins and mods are immune to the filter
            return

        if server.id in self.filter.keys():
            for w in self.filter[server.id]:
                if w in message.content.lower():
                    # Something else in discord.py is throwing a 404 error
                    # after deletion
                    try:
                        await self._delete_message(message)
                    except:
                        pass
                    print("Message supprime, filtré: " + w)

    async def check_names(self, before, after):
        if before.name != after.name:
            if before.id not in self.past_names.keys():
                self.past_names[before.id] = [after.name]
            else:
                if after.name not in self.past_names[before.id]:
                    names = deque(self.past_names[before.id], maxlen=20)
                    names.append(after.name)
                    self.past_names[before.id] = list(names)
            dataIO.save_json("data/mod/past_names.json", self.past_names)

        if before.nick != after.nick and after.nick is not None:
            server = before.server
            if not server.id in self.past_nicknames:
                self.past_nicknames[server.id] = {}
            if before.id in self.past_nicknames[server.id]:
                nicks = deque(self.past_nicknames[server.id][before.id],
                              maxlen=20)
            else:
                nicks = []
            if after.nick not in nicks:
                nicks.append(after.nick)
                self.past_nicknames[server.id][before.id] = list(nicks)
                dataIO.save_json("data/mod/past_nicknames.json",
                                 self.past_nicknames)

def check_folders():
    folders = ("data", "data/mod/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    ignore_list = {"SERVERS": [], "CHANNELS": []}

    if not os.path.isfile("data/mod/blacklist.json"):
        print("Creating empty blacklist.json...")
        fileIO("data/mod/blacklist.json", "save", [])

    if not os.path.isfile("data/mod/whitelist.json"):
        print("Creating empty whitelist.json...")
        fileIO("data/mod/whitelist.json", "save", [])

    if not os.path.isfile("data/mod/ignorelist.json"):
        print("Creating empty ignorelist.json...")
        fileIO("data/mod/ignorelist.json", "save", ignore_list)

    if not os.path.isfile("data/mod/filter.json"):
        print("Creating empty filter.json...")
        fileIO("data/mod/filter.json", "save", {})

    if not os.path.isfile("data/mod/past_names.json"):
        print("Creating empty past_names.json...")
        fileIO("data/mod/past_names.json", "save", {})

    if not os.path.isfile("data/mod/past_nicknames.json"):
        print("Creating empty past_nicknames.json...")
        fileIO("data/mod/past_nicknames.json", "save", {})



def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("mod")
    # Prevents the logger from being loaded again in case of module reload
    if logger.level == 0:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/mod/mod.log', encoding='utf-8', mode='a')
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = Mod(bot)
    bot.add_listener(n.check_filter, "on_message")
    bot.add_listener(n.check_names, "on_member_update")
    bot.add_cog(n)
