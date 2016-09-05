@echo off
pushd %~dp0
IF "%PROCESSOR_ARCHITECTURE%"=="x86" (GOTO 32bit) else (GOTO 64bit)
echo Système indetectable.
PAUSE
GOTO end

:32bit
echo Windows 32bit detecté. Vous devez installer le module manuellement. Pressez Entrer pour que j'ouvre la page web.
echo Suivez les insutructions.
PAUSE
start "" https://ffmpeg.zeranoe.com/builds/
echo Telechargez "FFmpeg 32-bit Static"
echo Ouvrez le fichier et copiez les 3 .exe de "bin" vers le dossier ProjectFreya
PAUSE
GOTO end

:64bit
echo Telechargement des fichiers... ne pas fermer.
echo Telechargement ffmpeg.exe (1/3)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/Twentysix26/Red-DiscordBot/raw/master/ffmpeg.exe', 'ffmpeg.exe')"
echo Telechargement ffplay.exe (2/3)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/Twentysix26/Red-DiscordBot/raw/master/ffplay.exe', 'ffplay.exe')"
echo Telechargement ffprobe.exe (3/3)...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/Twentysix26/Red-DiscordBot/raw/master/ffprobe.exe', 'ffprobe.exe')"
PAUSE

:end