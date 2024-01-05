import io
import re
import threading
import time
from datetime import datetime

import discord
import requests
import savepagenow

import helpers
from urlTest import urlTest
from globalvals import globalvals

if globalvals.DEBUG_MODE == True:
    BinaryTypes = [globalvals.DEBUG_CHANNEL]
else:
    BinaryTypes = globalvals.BinaryTypes

Channels = [
    "LIVE",
    #"zcanary",
    #"zintegration"
]

currentClientUrl = ""
currentFailedFiles = []

for i in BinaryTypes:
    open(i+".txt", "a+")

if globalvals.DEBUG_MODE:
    globalvals.Webhook.send(f'Started (Debug)!')
else:
    globalvals.Webhook.send(f'Started!')

ClientArchiveQueue = []
Queuelock = threading.Lock()
def WorkerThread():
    while True:
        time.sleep(0.1)
        while len(ClientArchiveQueue) > 0:
            with Queuelock:
                latest = ClientArchiveQueue.pop(0)
            urlTest(latest)

x = threading.Thread(target=WorkerThread)
x.start()

def ChannelArchiveBot(channel):
    while True:
        for CurrentBinaryType in BinaryTypes:
            for i in range(16):
                try:
                    versionHashStatic = helpers.GetCurrentHash(CurrentBinaryType)
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    open("log.txt", "a").write(f"{e}\n")
                    time.sleep(8)

            cachedDeploy = open(f"{CurrentBinaryType}.txt", "r").read()
            version = versionHashStatic

            pattern = re.compile("^(version-)&*(?:[0-f]{16})+$")
            if not pattern.match(version):
                continue

            if channel != "LIVE":
                version = f"channel/{channel}/"

            if CurrentBinaryType.startswith("Mac"):
                version =  f"mac/{version}"
            print(f"Trying: {version}")

            if (cachedDeploy != versionHashStatic):
                NewDeployEmbed = discord.Embed(title="New Roblox Deploy!", description = versionHashStatic)
                NewDeployEmbed.add_field(name = f'Log Time', value = datetime.now().strftime("%x %X"), inline = False)
                NewDeployEmbed.add_field(name = f'binaryType', value = CurrentBinaryType, inline = False)
                NewDeployEmbed.set_image(url="https://media.discordapp.net/attachments/1121901772961763421/1157753486063173713/deploy.gif")
                globalvals.Webhook.send(embed = NewDeployEmbed)

                print("NEWDEPLOY!!!")
                open(f"{CurrentBinaryType}.txt", "w").write(versionHashStatic)

                for i in range(16):
                    try:
                        rbxPkgManifest = helpers.GetPkgManifest(version)
                        if CurrentBinaryType.find("Mac") == -1:
                            rbxPkgInstallerManifest = helpers.GetPkgInstallerManifest(version)
                        break
                    except Exception as e:
                        print(f"Error: {e}")
                        open("log.txt", "a").write(f"{e}\n")
                        time.sleep(8)

                if CurrentBinaryType.find("Mac") == -1:
                    fileListEmbed = discord.Embed(title=f"{versionHashStatic} File List:", description = f"From https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt")
                else:
                    fileListEmbed = discord.Embed(title=f"{versionHashStatic} File List:", description = f"From https://setup.rbxcdn.com/mac/")
                pkgManifest = []
                #open("testDoc.txt", "a").write(str(rbxPkgManifest.text))

                if CurrentBinaryType.find("Mac") == -1:
                    for v in rbxPkgManifest.text.splitlines():
                        if v.find(".") != -1:
                            pkgManifest.append(v)

                    for v in rbxPkgInstallerManifest.text.splitlines():
                        if v.find(".") != -1:
                            pkgManifest.append(v)

                    pkgManifest.append("rbxManifest.txt")
                    pkgManifest.append("rbxPkgManifest.txt")

                    if CurrentBinaryType.find("Studio") != -1:
                        pkgManifest.append("API-Dump.json")
                        pkgManifest.append("Full-API-Dump.json")
                        pkgManifest.append("RobloxStudioLauncherBeta.exe")
                else:
                    if CurrentBinaryType.find("Studio") != -1:
                        pkgManifest.append("RobloxStudio.dmg")
                        pkgManifest.append("RobloxStudio.zip")
                        pkgManifest.append("RobloxStudioApp.zip")
                    else:
                        pkgManifest.append("Roblox.dmg")
                        pkgManifest.append("Roblox.zip")
                        pkgManifest.append("RobloxPlayer.zip")

                with Queuelock:
                    print("LOCK")
                    ClientArchiveQueue.append((pkgManifest, version, versionHashStatic, fileListEmbed))
        time.sleep(10)

for i in Channels:
    ChannelThread = threading.Thread(target=ChannelArchiveBot, args=[i])
    ChannelThread.start()