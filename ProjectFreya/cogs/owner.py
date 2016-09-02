import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import set_cog, send_cmd_help, settings
from .utils.dataIO import fileIO

import importlib
import traceback
import logging
import asyncio
import threading
import datetime
import glob
import os
import time
import aiohttp

log = logging.getLogger("red.owner")


class CogNotFoundError(Exception):
    pass


class CogLoadError(Exception):
    pass


class NoSetupError(CogLoadError):
    pass


class CogUnloadError(Exception):
    pass


class OwnerUnloadWithoutReloadError(CogUnloadError):
    pass


class Owner:
    """Commandes pour le Propriétaire (Debug..)
    """

    def __init__(self, bot):
        self.bot = bot
        self.setowner_lock = False
        self.disabled_commands = fileIO("data/red/disabled_commands.json", "load")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def load(self, *, module: str):
        """Charge un module"""
        module = module.strip()
        if "cogs." not in module:
            module = "cogs." + module
        try:
            self._load_cog(module)
        except CogNotFoundError:
            await self.bot.say("Module Introuvable.")
        except CogLoadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say("Il y a eu une erreur au chargement du module.")
        except Exception as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say('Le module n\'a pas été chargé à cause d\'un problème. Pour plus d\'infos voir la console')
        else:
            set_cog(module, True)
            await self.disable_commands()
            await self.bot.say("Module activé.")

    @commands.group(invoke_without_command=True)
    @checks.mod_or_permissions(administrator=True)
    async def unload(self, *, module: str):
        """Decharge un module"""
        module = module.strip()
        if "cogs." not in module:
            module = "cogs." + module
        if not self._does_cogfile_exist(module):
            await self.bot.say("Ce module n'existe pas.")
        else:
            set_cog(module, False)
        try:  # No matter what we should try to unload it
            self._unload_cog(module)
        except OwnerUnloadWithoutReloadError:
            await self.bot.say("Il y a déjà un processus en cours.")
        except CogUnloadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say('Impossible de décharger le module sans dangers.')
        else:
            await self.bot.say("Module désactivé.")

    @unload.command(name="all")
    @checks.mod_or_permissions(administrator=True)
    async def unload_all(self):
        """Décharge tout les modules"""
        cogs = self._list_cogs()
        still_loaded = []
        for cog in cogs:
            set_cog(cog, False)
            try:
                self._unload_cog(cog)
            except OwnerUnloadWithoutReloadError:
                pass
            except CogUnloadError as e:
                log.exception(e)
                traceback.print_exc()
                still_loaded.append(cog)
        if still_loaded:
            still_loaded = ", ".join(still_loaded)
            await self.bot.say("Modules non déchargés : "
                "{}".format(still_loaded))
        else:
            await self.bot.say("Tout les modules ont été déchargés.")

    @checks.mod_or_permissions(administrator=True)
    @commands.command(name="reload")
    async def _reload(self, module):
        """Recharge un module"""
        if "cogs." not in module:
            module = "cogs." + module

        try:
            self._unload_cog(module, reloading=True)
        except:
            pass

        try:
            self._load_cog(module)
        except CogNotFoundError:
            await self.bot.say("Ce module n'a pas été trouvé.")
        except NoSetupError:
            await self.bot.say("Ce module n'a pas de setup.")
        except CogLoadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say("Ce module ne peut pas être rechargé. Voir l'invité de commande.")
        else:
            set_cog(module, True)
            await self.disable_commands()
            await self.bot.say("Module rechargé")

    @commands.command(pass_context=True, hidden=True)
    @checks.mod_or_permissions(administrator=True)
    async def debug(self, ctx, *, code):
        """Evalue le code"""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        global_vars = globals().copy()
        global_vars['bot'] = self.bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        global_vars['server'] = ctx.message.server

        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        if asyncio.iscoroutine(result):
            result = await result

        result = python.format(result)
        if not ctx.message.channel.is_private:
            censor = (settings.email, settings.password)
            r = "[EXPUNGED]"
            for w in censor:
                if w != "":
                    result = result.replace(w, r)
                    result = result.replace(w.lower(), r)
                    result = result.replace(w.upper(), r)
        await self.bot.say(result)

    @commands.group(name="set", pass_context=True)
    async def _set(self, ctx):
        """Pour changer un reglage global."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            return

    @_set.command(pass_context=True)
    async def owner(self, ctx):
        """Change le propriétaire"""
        if settings.owner != "id_here":
            await self.bot.say("L'ID du propriétaire à déjà été reglé.")
            return

        if self.setowner_lock:
            await self.bot.say("Une commande d'ID est déjà en attente.")
            return

        await self.bot.say("Confirmez dans la console que vous êtes le propriétaire.")
        self.setowner_lock = True
        t = threading.Thread(target=self._wait_for_answer,
                             args=(ctx.message.author,))
        t.start()

    @_set.command()
    @checks.mod_or_permissions(administrator=True)
    async def prefix(self, *prefixes):
        """Change le prefixe"""
        if prefixes == ():
            await self.bot.say("Exemple: setprefix [ ! ^ .")
            return

        self.bot.command_prefix = sorted(prefixes, reverse=True)
        settings.prefixes = sorted(prefixes, reverse=True)
        log.debug("Setting prefixes to:\n\t{}".format(settings.prefixes))

        if len(prefixes) > 1:
            await self.bot.say("Prefixes reglés")
        else:
            await self.bot.say("Prefix reglé")

    @_set.command(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def name(self, ctx, *, name):
        """Change le nom de LiteRB"""
        name = name.strip()
        if name != "":
            await self.bot.edit_profile(settings.password, username=name)
            await self.bot.say("Fait.")
        else:
            await send_cmd_help(ctx)

    @_set.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(administrator=True)
    async def nickname(self, ctx, *, nickname=""):
        """SChange le surnom."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(ctx.message.server.me, nickname)
            await self.bot.say("Fait.")
        except discord.Forbidden:
            await self.bot.say("Je ne peux pas le faire, il me manque des permissions.")

    @_set.command(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def status(self, ctx, *, status=None):
        """Change le statut de LiteRB"""

        if status:
            status = status.strip()
            await self.bot.change_status(discord.Game(name=status))
            log.debug('Statut reglé en "{}" par le propriétaire'.format(status))
        else:
            await self.bot.change_status(None)
            log.debug('Statut reglé')
        await self.bot.say("Fait.")

    @_set.command()
    @checks.mod_or_permissions(administrator=True)
    async def avatar(self, url):
        """Change l'avatar de LiteRB"""
        try:
            async with self.session.get(url) as r:
                data = await r.read()
            await self.bot.edit_profile(settings.password, avatar=data)
            await self.bot.say("Fait.")
            log.debug("à changé d'avatar")
        except Exception as e:
            await self.bot.say("Erreur, regardez la console pour plus d'infos.")
            log.exception(e)
            traceback.print_exc()

    @_set.command(name="token")
    @checks.mod_or_permissions(administrator=True)
    async def _token(self, token):
        """Change le token de LiteRB"""
        if len(token) < 50:
            await self.bot.say("Token invalide.")
        else:
            settings.login_type = "token"
            settings.email = token
            settings.password = ""
            await self.bot.say("Token reglé. Il faut me redémarrer maintenant.")
            log.debug("Token changé.")

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def shutdown(self):
        """Eteint LiteRB"""
        await self.bot.logout()

    @commands.group(name="command", pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def command_disabler(self, ctx):
        """Active/Désactive une commande."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            if self.disabled_commands:
                msg = "Commandes désactivées :\n```xl\n"
                for cmd in self.disabled_commands:
                    msg += "{}, ".format(cmd)
                msg = msg.strip(", ")
                await self.bot.whisper("{}```".format(msg))

    @command_disabler.command()
    async def disable(self, *, command):
        """Active ou désactive plusieurs subcommandes"""
        comm_obj = await self.get_command(command)
        if comm_obj is KeyError:
            await self.bot.say("Cette commande n'existe pas.")
        elif comm_obj is False:
            await self.bot.say("Vous ne pouvez pas désactiver ce module.")
        else:
            comm_obj.enabled = False
            comm_obj.hidden = True
            self.disabled_commands.append(command)
            fileIO("data/red/disabled_commands.json", "save", self.disabled_commands)
            await self.bot.say("Commande désactivée.")

    @command_disabler.command()
    async def enable(self, *, command):
        """Active ou  désactive des subcommandes"""
        if command in self.disabled_commands:
            self.disabled_commands.remove(command)
            fileIO("data/red/disabled_commands.json", "save", self.disabled_commands)
            await self.bot.say("Activée.")
        else:
            await self.bot.say("Cette commande n'est pas désactivable.")
            return
        try:
            comm_obj = await self.get_command(command)
            comm_obj.enabled = True
            comm_obj.hidden = False
        except:  
            pass 

    async def get_command(self, command):
        command = command.split()
        try:
            comm_obj = self.bot.commands[command[0]]
            if len(command) > 1:
                command.pop(0)
                for cmd in command:
                    comm_obj = comm_obj.commands[cmd]
        except KeyError:
            return KeyError
        if comm_obj.cog_name == "Owner":
            return False
        return comm_obj

    async def disable_commands(self): # runs at boot
        for cmd in self.disabled_commands:
            cmd_obj = await self.get_command(cmd)
            try:
                cmd_obj.enabled = False
                cmd_obj.hidden = True
            except:
                pass

    @commands.command()
    @checks.mod_or_permissions(administrator=True)
    async def join(self, invite_url: discord.Invite=None):
        """Pour rejoindre un nouveau serveur."""
        if hasattr(self.bot.user, 'bot') and self.bot.user.bot is True:
            # Check to ensure they're using updated discord.py
            msg = ("Le tag BOT m'oblige à utiliser un autre moyen de connexion appellé OAUTH2")
            await self.bot.say(msg)
            if hasattr(self.bot, 'oauth_url'):
                await self.bot.whisper("Voici mon lien OAUTH2:\n{}".format(
                    self.bot.oauth_url))
            return

        if invite_url is None:
            await self.bot.say("J'ai besoin d'une invitation Discord.")
            return

        try:
            await self.bot.accept_invite(invite_url)
            await self.bot.say("Serveur rejoint.")
            log.debug("J'ai rejoint {}".format(invite_url))
        except discord.NotFound:
            await self.bot.say("Invitation invalide.")
        except discord.HTTPException:
            await self.bot.say("Je n'ai pas pu accepter cette invitation.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def leave(self, ctx):
        """Quitte le serveur."""
        message = ctx.message

        await self.bot.say("Voulez-vous que je quitte le serveur ? 'oui' pour confirmer.")
        response = await self.bot.wait_for_message(author=message.author)

        if response.content.lower().strip() == "oui":
            await self.bot.say("D'accord, Bye :wave:")
            log.debug('Je quitte "{}"'.format(message.server.name))
            await self.bot.leave_server(message.server)
        else:
            await self.bot.say("D'accord, je reste donc.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def servers(self, ctx):
        """Liste et autorise des serveurs."""
        owner = ctx.message.author
        servers = list(self.bot.servers)
        server_list = {}
        msg = ""
        for i in range(0, len(servers)):
            server_list[str(i)] = servers[i]
            msg += "{}: {}\n".format(str(i), servers[i].name)
        msg += "\nPour quitter un serveur tapez le nombre."
        await self.bot.say(msg)
        while msg != None:
            msg = await self.bot.wait_for_message(author=owner, timeout=15)
            if msg != None:
                msg = msg.content.strip()
                if msg in server_list.keys():
                    await self.leave_confirmation(server_list[msg], owner, ctx)
                else:
                    break
            else:
                break

    @commands.command(pass_context=True)
    async def contact(self, ctx, *, message : str):
        """Envoye un message au propriétaire."""
        if settings.owner == "id_here":
            await self.bot.say("Il n'y a pas de propriétaire.")
            return
        owner = discord.utils.get(self.bot.get_all_members(), id=settings.owner)
        author = ctx.message.author
        sender = "Venant de {} ({}):\n\n".format(author, author.id)
        message = sender + message
        try:
            await self.bot.send_message(owner, message)
        except discord.errors.InvalidArgument:
            await self.bot.say("Je ne peux pas envoyer votre message, je ne retrouve pas mon propriétaire *tousse*")
        except discord.errors.HTTPException:
            await self.bot.say("Message trop long.")
        except:
            await self.bot.say("Je ne peux pas livrer votre message, désolé.")

    @commands.command()
    async def info(self):
        """Montre les infos de LiteRB."""
        await self.bot.say(
        "Instance de LiteRB, crée par Acrown, dérivé en partie de Red de Twentysix26.")

    async def leave_confirmation(self, server, owner, ctx):
        if not ctx.message.channel.is_private:
            current_server = ctx.message.server
        else:
            current_server = None
        answers = ("oui", "o")
        await self.bot.say("Voulez-vous que je quitte ? "
                    "(oui/non)".format(server.name))
        msg = await self.bot.wait_for_message(author=owner, timeout=15)
        if msg is None:
            await self.bot.say("Je ne crois pas..")
        elif msg.content.lower().strip() in answers:
            await self.bot.leave_server(server)
            if server != current_server:
                await self.bot.say("Fait.")
        else:
            await self.bot.say("D'accord.")

    @commands.command()
    async def uptime(self):
        """Montre depuis combien de temps LiteRB est activé."""
        up = abs(self.bot.uptime - int(time.perf_counter()))
        up = str(datetime.timedelta(seconds=up))
        await self.bot.say("`Activé depuis: {}`".format(up))

    @commands.command()
    async def version(self):
        """Montre la dernière version du bot."""
        response = self.bot.loop.run_in_executor(None, self._get_version)
        result = await asyncio.wait_for(response, timeout=10)
        await self.bot.say(result)

    def _load_cog(self, cogname):
        if not self._does_cogfile_exist(cogname):
            raise CogNotFoundError(cogname)
        try:
            mod_obj = importlib.import_module(cogname)
            importlib.reload(mod_obj)
            self.bot.load_extension(mod_obj.__name__)
        except SyntaxError as e:
            raise CogLoadError(*e.args)
        except:
            raise

    def _unload_cog(self, cogname, reloading=False):
        if not reloading and cogname == "cogs.owner":
            raise OwnerUnloadWithoutReloadError(
                "On ne peux pas décharger le module Owner.")
        try:
            self.bot.unload_extension(cogname)
        except:
            raise CogUnloadError

    def _list_cogs(self):
        cogs = glob.glob("cogs/*.py")
        clean = []
        for c in cogs:
            c = c.replace("/", "\\")  # Linux fix
            clean.append("cogs." + c.split("\\")[1].replace(".py", ""))
        return clean

    def _does_cogfile_exist(self, module):
        if "cogs." not in module:
            module = "cogs." + module
        if module not in self._list_cogs():
            return False
        return True

    def _wait_for_answer(self, author):
        print(author.name + " a demandé à être propriétaire. Si c'est vous tapez oui. Autrement appuyez sur Entrer.")
        print()
        print("Ne mettez *PAS* quelqu'un d'autre comme propriétaire.")

        choice = "None"
        while choice.lower() != "oui" and choice == "None":
            choice = input("> ")

        if choice == "oui":
            settings.owner = author.id
            print(author.name + " a été mis propriétaire.")
            self.setowner_lock = False
            self.owner.hidden = True
        else:
            print("la requête à été ignoré.")
            self.setowner_lock = False

    def _get_version(self):
        getversion = os.popen(r'git show -s HEAD --format="%cr|%s|%h"')
        getversion = getversion.read()
        version = getversion.split('|')
        return 'Last updated: ``{}``\nCommit: ``{}``\nHash: ``{}``'.format(
            *version)

def check_files():
    if not os.path.isfile("data/red/disabled_commands.json"):
        print("Creating empty disabled_commands.json...")
        fileIO("data/red/disabled_commands.json", "save", [])

def setup(bot):
    check_files()
    n = Owner(bot)
    bot.add_cog(n)
