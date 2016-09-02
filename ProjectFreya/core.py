from discord.ext import commands
import discord
from cogs.utils.settings import Settings
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import inline
import asyncio
import os
import time
import sys
import logging
import logging.handlers
import shutil
import traceback

#
# Freya, Discord Bot dérivé de Red de Twentysix26. Version publique.
#

description = """
Freya - Open Discord Bot (French)
"""

formatter = commands.HelpFormatter(show_check_failure=False)

bot = commands.Bot(command_prefix=["_"], formatter=formatter,
                   description=description, pm_help=None)

settings = Settings()

from cogs.utils import checks


@bot.event
async def on_ready():
    users = str(len(set(bot.get_all_members())))
    servers = str(len(bot.servers))
    channels = str(len([c for c in bot.get_all_channels()]))
    if not "uptime" in dir(bot): #prevents reset in case of reconnection
        bot.uptime = int(time.perf_counter())
    print('------')
    print("{} est maintenant en ligne.".format(bot.user.name))
    print('------')
    print("Connecté à :")
    print("{} serveurs".format(servers))
    print("{} channels".format(channels))
    print("{} utilisateurs".format(users))
    print("\n{0} modules actifs avec {1} commandes\n".format(
        len(bot.cogs), len(bot.commands)))
    if settings.login_type == "token":
        print("------")
        print("URL d'invitation :")
        url = await get_oauth_url()
        bot.oauth_url = url
        print(url)
        print("------")
    await bot.get_cog('Owner').disable_commands()


@bot.event
async def on_command(command, ctx):
    pass


@bot.event
async def on_message(message):
    if user_allowed(message):
        await bot.process_commands(message)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel,
            "Commande desactivée.")
    elif isinstance(error, commands.CommandInvokeError):
        logger.exception("Exception dans la commande '{}'".format(
            ctx.command.qualified_name), exc_info=error.original)
        oneliner = "Erreur dans '{}' - {}: {}".format(
            ctx.command.qualified_name, type(error.original).__name__,
            str(error.original))
        await ctx.bot.send_message(ctx.message.channel, inline(oneliner))
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        logger.exception(type(error).__name__, exc_info=error)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)


def user_allowed(message):

    author = message.author

    mod = bot.get_cog('Mod')

    if mod is not None:
        if settings.owner == author.id:
            return True
        if not message.channel.is_private:
            server = message.server
            names = (settings.get_server_admin(
                server), settings.get_server_mod(server))
            results = map(
                lambda name: discord.utils.get(author.roles, name=name), names)
            for r in results:
                if r is not None:
                    return True

        if author.id in mod.blacklist_list:
            return False

        if mod.whitelist_list:
            if author.id not in mod.whitelist_list:
                return False

        if not message.channel.is_private:
            if message.server.id in mod.ignore_list["SERVERS"]:
                return False

            if message.channel.id in mod.ignore_list["CHANNELS"]:
                return False
        return True
    else:
        return True


async def get_oauth_url():
    try:
        data = await bot.application_info()
    except AttributeError:
        return "Discord.py dépassé, lien indisponible."
    return discord.utils.oauth_url(data.id)


def check_folders():
    folders = ("data", "data/red", "cogs", "cogs/utils")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creation du fichier " + folder )
            os.makedirs(folder)


def check_configs():
    if settings.bot_settings == settings.default_settings:
        print("Freya - Initialisation\n")
        print("Si ce n'est pas déjà fait, créez un compte BOT en suivant ce tutoriel :\n"
              "https://twentysix26.github.io/Red-Docs/red_guide_bot_accounts/"
              "#creating-a-new-bot-account")
        print("et copiez le token.")
        print("\nInsérez le token:")

        choice = input("> ")

        if "@" not in choice and len(choice) >= 50:  # Assuming token
            settings.login_type = "token"
            settings.email = choice
        elif "@" in choice:
            settings.login_type = "email"
            settings.email = choice
            settings.password = input("\nPassword> ")
        else:
            os.remove('data/red/settings.json')
            input("Invalide. Redémarrez le bot et réesayez.")
            exit(1)

        print("\nChoix d'un préfixe: C'est le symbole avant une commande.\n"
              "Généralement ! ou &. Choissisez le préfixe :")
        confirmation = False
        while confirmation is False:
            new_prefix = ensure_reply("\nPrefix> ").strip()
            print("\nÊtes-vous sûr de vouloir {0} comme préfixe ?\nVous "
                  "Pourrez le changer la prochaine fois."
                  "\nTapez 'yes' pour confirmer.".format(new_prefix))
            confirmation = get_answer()

        settings.prefixes = [new_prefix]

        print("\nAprès la configuration, tapez "
              "'{}set owner' *dans un tchat Discord*\npour vous définir Propriétaire.\n"
              "Appuyez sur Entrer pour continuer.".format(new_prefix))
        settings.owner = input("")
        if settings.owner == "":
            settings.owner = "id_here"
        if not settings.owner.isdigit() or len(settings.owner) < 17:
            if settings.owner != "id_here":
                print("\nERROR: Ce n'est pas un ID valable. Mettez vous "
                      "propriétaire plus tard avec {}set owner".format(new_prefix))
            settings.owner = "id_here"

        print("\nMettez le rôle d'administrateur qui pourront "
              "utiliser les commandes d'admin.")
        print("Laissez vide pour mettre le rôle par défaut (Transistor)")
        settings.default_admin = input("\nRole d'admin> ")
        if settings.default_admin == "":
            settings.default_admin = "Transistor"

        print("\nMettez le rôle de modérateur."
              " Ils pourront utiliser les commandes qui leurs sont liés.")
        print("Laissez vide pour le rôle de base (Process)")
        settings.default_mod = input("\nRole de modérateur> ")
        if settings.default_mod == "":
            settings.default_mod = "Process"

        print("\nLa configuration est terminée. Cette fenêtre va maintenant passer en lecture seulement. N'oubliez pas 'set owner'.")
        input("\n")

    if not os.path.isfile("data/red/cogs.json"):
        print("Creating new cogs.json...")
        dataIO.save_json("data/red/cogs.json", {})

def set_logger():
    global logger
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(
        filename='data/red/discord.log', encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]"))
    logger.addHandler(handler)

    logger = logging.getLogger("red")
    logger.setLevel(logging.INFO)

    red_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(red_format)
    stdout_handler.setLevel(logging.INFO)

    fhandler = logging.handlers.RotatingFileHandler(
        filename='data/red/red.log', encoding='utf-8', mode='a',
        maxBytes=10**7, backupCount=5)
    fhandler.setFormatter(red_format)

    logger.addHandler(fhandler)
    logger.addHandler(stdout_handler)

def ensure_reply(msg):
    choice = ""
    while choice == "":
        choice = input(msg)
    return choice

def get_answer():
    choices = ("yes", "y", "no", "n")
    c = ""
    while c not in choices:
        c = input(">").lower()
    if c.startswith("y"):
        return True
    else:
        return False

def set_cog(cog, value):
    data = dataIO.load_json("data/red/cogs.json")
    data[cog] = value
    dataIO.save_json("data/red/cogs.json", data)

def load_cogs():
    try:
        if sys.argv[1] == "--no-prompt":
            no_prompt = True
        else:
            no_prompt = False
    except:
        no_prompt = False

    try:
        registry = dataIO.load_json("data/red/cogs.json")
    except:
        registry = {}

    bot.load_extension('cogs.owner')
    owner_cog = bot.get_cog('Owner')
    if owner_cog is None:
        print("AAAAH, je ne peux pas démarrer sans le module Owner ! Veuillez me fournir une nouvelle copie de ce module !.")
        exit(1)

    failed = []
    extensions = owner_cog._list_cogs()
    for extension in extensions:
        if extension.lower() == "cogs.owner":
            continue
        in_reg = extension in registry
        if in_reg is False:
            if no_prompt is True:
                registry[extension] = False
                continue
            print("\nNouvelle extension: {}".format(extension))
            print("La charger ?(y/n)")
            if not get_answer():
                registry[extension] = False
                continue
            registry[extension] = True
        if not registry[extension]:
            continue
        try:
            owner_cog._load_cog(extension)
        except Exception as e:
            print("{}: {}".format(e.__class__.__name__, str(e)))
            logger.exception(e)
            failed.append(extension)
            registry[extension] = False

    if extensions:
        dataIO.save_json("data/red/cogs.json", registry)

    if failed:
        print("\nImpossible de charger: ", end="")
        for m in failed:
            print(m + " ", end="")
        print("\n")

    return owner_cog


def main():
    global settings
    global checks

    check_folders()
    check_configs()
    set_logger()
    owner_cog = load_cogs()
    if settings.prefixes != []:
        bot.command_prefix = settings.prefixes
    else:
        print("Aucun préfix reglé, par défaut !")
        bot.command_prefix = ["!"]
        if settings.owner != "id_here":
            print("Utilisez !set prefix pour la régler.")
        else:
            print("Dès que vous serez propriétaire utilisez !set prefix pour changer le prefixe.")
    if settings.owner == "id_here":
        print("Aucun propriétaire. Faîtes '{}set owner' dans le tchat pour changer "
              "le propriétaire.".format(bot.command_prefix[0]))
    else:
        owner_cog.owner.hidden = True  # Hides the set owner command from help
    print("--- Chargement en cours ---")
    print("Soyez sûr de garder le bot à jour avec 'git pull' dans le terminal.")
    if settings.login_type == "token":
        try:
            yield from bot.login(settings.email)
        except TypeError as e:
            print(e)
            msg = ("\nDiscord.py est dépassé.\n"
                   "pour mettre à jour discord.py lancez dans le terminal "
                   "\npip3 install --upgrade git+https://"
                   "github.com/Rapptz/discord.py@async")
            sys.exit(msg)
    else:
        yield from bot.login(settings.email, settings.password)
    yield from bot.connect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except discord.LoginFailure:
        logger.error(traceback.format_exc())
        choice = input("Login invalide. "
            "Si ça marchait avant c'est que l'erreur vient de Discord. "
            "t\nDans ce cas, quittez la fenêtre et réesayez plus tard "
            ".\nSinon, tapez 'reset' pour "
            "supprimer la configuration et remettre un paramétrage usine "
            "au prochain démarrage.\n> ")
        if choice.strip() == "reset":
            shutil.copy('data/red/settings.json',
                        'data/red/settings-{}.bak'.format(int(time.time())))
            os.remove('data/red/settings.json')
    except:
        logger.error(traceback.format_exc())
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
