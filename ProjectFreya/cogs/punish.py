import discord
from discord.ext import commands
from .utils import checks
import asyncio
import os
import logging
log = logging.getLogger('red.punish')


class Punish:
    """Pour punir les utilisateurs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def createprison(self, ctx):
        """Place un utilisateur dans la prison. Si il y est déjà, l'enlève de la prison."""
        server = ctx.message.server
        # Regarde si le rôle existe
        if 'Prison' not in [r.name for r in server.roles]:
            await self.bot.say("Le rôle n'existe pas. Je vais donc le créer...")
            log.debug('Creation du rôle "Prison"')
            try:
                perms = discord.Permissions.none()
                # Active les permissions voulues (si nécéssaire)
                await self.bot.create_role(server, name="Prison", permissions=perms)
                await self.bot.say("Rôle crée ! Permissions reglées !\nAssurez-vous que les modérateurs soient au dessus du rôle.\nAttendez que le membre soit envoyé en prison !")
                try:
                    for c in server.channels:
                        if c.type.name == 'text':
                            perms = discord.PermissionOverwrite()
                            perms.send_messages = False
                            r = discord.utils.get(ctx.message.server.roles, name="Prison")
                            await self.bot.edit_channel_permissions(c, r, perms)
                        await asyncio.sleep(1.5)
                except discord.Forbidden:
                    await self.bot.say("Une erreur est apparue.")
            except discord.Forbidden:
                await self.bot.say("Je ne peux pas créer le rôle.")
        else:
            await self.bot.say("Ce rôle existe déjà !")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def prison(self, ctx, user: discord.Member, temps: int=None):
        """Met un utilisateur en prison pendant x minutes

        Si aucun temps n'est spécifié, il n'y aura pas de compte à rebours."""
        server = ctx.message.server
        if user.id == self.bot.user.id:
            await self.bot.say("Un robot doit protéger son existence tant que cette protection n'entre pas en conflit avec la première ou la deuxième loi d'Asimov. Or, si j'execute votre ordre, vous serez exposé au danger.")
        r = discord.utils.get(ctx.message.server.roles, name="Prison")
        if temps == None:
            if 'Prison' not in [r.name for r in user.roles]:
                await self.bot.add_roles(user, r)
                await self.bot.say("{} est maintenant en Prison !".format(user.name))
                log.debug('UID {} en Prison'.format(user.id))
                await self.bot.send_message(user, "Tu es maintenant en prison. Si tu as une réclamation à faire, va sur le canal *prison* du serveur.")
            else:
                await self.bot.remove_roles(user, r)
                await self.bot.say("L'utilisateur est maintenant plus en Prison !")
                log.debug('UID {} plus en Prison'.format(user.id))
                await self.bot.send_message(user, "Tu es libéré de la prison.")
        else:
            if temps >= 1:
                minutes = temps * 60 #On veut un temps en minutes
                if 'Prison' not in [r.name for r in user.roles]:
                    await self.bot.add_roles(user, r)
                    await self.bot.say("**{}** est maintenant en prison pour {} minute(s).".format(user.name, temps))
                    await self.bot.send_message(user, "Tu es maintenant en prison pour {} minute(s). Si tu as une réclamation à faire, va sur le canal *prison* du serveur.".format(temps))
                    log.debug('UID {} en Prison T'.format(user.id))
                    # ^ Mise en prison
                    await asyncio.sleep(minutes)
                    # v Sortie de prison
                    await self.bot.remove_roles(user, r)
                    await self.bot.say("**{}** à été libéré de la prison.".format(user.name))
                    await self.bot.send_message(user, "Tu es libéré de la prison.")
                    log.debug('UID {} plus en Prison T'.format(user.id))

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def cleanprison(self, ctx):
        """Retire tout le monde de la prison"""
        server = ctx.message.server
        r = discord.utils.get(ctx.message.server.roles, name="Prison")
        for user in server.members:
            if 'Prison' in [r.name for r in user.roles]:
                await self.bot.remove_roles(user, r)
                await self.bot.send_message(user, "Tu as été libéré de prison.")
            else:
                pass
        await self.bot.say("L'ensemble des prisonniers ont étés libérées")
                

    # Cherche un nouveau channel pour poursuivre la punition
    async def new_channel(self, c):
        if 'Prison' in [r.name for r in c.server.roles]:
            perms = discord.PermissionOverwrite()
            perms.send_messages = False
            r = discord.utils.get(c.server.roles, name="Prison")
            await self.bot.edit_channel_permissions(c, r, perms)
            log.debug('Le rôle Prison à été crée automatiquement pour : {}'.format(c.id))


def setup(bot):
    n = Punish(bot)
    bot.add_listener(n.new_channel, 'on_channel_create')
    bot.add_cog(n)
