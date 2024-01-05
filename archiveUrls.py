import io
import re
import threading
import time
from datetime import datetime

import discord
import requests
import savepagenow

import helpers
from globalvals import globalvals

def archiveURLS(curVerArgs):
    time.sleep(20)
    pkgManifest, curVersion, versionHashStatic = curVerArgs
    currentFailedFiles = []
    currentSuccessFiles = []
    for v in pkgManifest:
        time.sleep(20)
        currentClientUrl = f"https://setup.rbxcdn.com/{curVersion}-{v}"
        print(f"Archiving: {currentClientUrl}")
        for i in range(16):
            try:
                time.sleep(8)
                Succeeded = helpers.SaveClientNow(curVersion, v)
                currentSuccessFiles.append(Succeeded)
                break
            except Exception as e:
                print(f"Error: {e}")
                open("log.txt", "a").write(f"{e}\n")
                time.sleep(60)
                if i == 7:
                    try:
                        currentFailedFiles.index(currentClientUrl)
                    except Exception as h:
                        currentFailedFiles.append(currentClientUrl)
                        time.sleep(4)

    FailedArchiveEmbed = discord.Embed(title=f"Done! Failed Archives: {len(currentFailedFiles)}", description = versionHashStatic)
    for i in currentFailedFiles:
        FailedArchiveEmbed.add_field(name = "", value = i, inline = False)
    globalvals.Webhook.send(embed=FailedArchiveEmbed)

    SuccessArchivedFileList = discord.Embed(title=f"{versionHashStatic} Archived List:", description = f"Links returned by SavePageNow")

    clientSuccessListString = bytes("\n".join(currentSuccessFiles), encoding='utf8')
    ClientSuccessFileList = discord.File(io.BytesIO(clientSuccessListString), filename=f"{versionHashStatic}-ClientFiles.txt")

    globalvals.Webhook.send(embed=SuccessArchivedFileList)
    globalvals.Webhook.send(file=ClientSuccessFileList)

    DeployHistoryFailFlag = False
    if curVersion.startswith("mac"):
        DeployText = "mac/DeployHistory.txt"
    else:
        DeployText = "DeployHistory.txt"
    time.sleep(20)
    for i in range(16):
        try:
            ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{DeployText}")
            break
        except Exception as e:
            time.sleep(60)
            if i == 15:
                DeployHistoryTxtArchive = discord.Embed(title=f"Attempted Archive Of https://setup.rbxcdn.com/{DeployText}", description = "Failed!")
                DeployHistoryTxtArchive.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1161763241454735480/billc.png")
                DeployHistoryFailFlag = True
    if not DeployHistoryFailFlag:
        DeployHistoryTxtArchive = discord.Embed(title=f"Attempted Archive Of https://setup.rbxcdn.com/{DeployText}", description = "Succeeded!")
        DeployHistoryTxtArchive.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1161764162284830820/rfold.png")
    globalvals.Webhook.send(embed=DeployHistoryTxtArchive)
    if not DeployHistoryFailFlag:
        DeployHistoryInMemory = requests.get(f"http://setup.rbxcdn.com/{DeployText}")
        DeployHistoryMemAsFile = discord.File(io.BytesIO(DeployHistoryInMemory.content), filename=DeployText.replace("/", "-"))
        globalvals.Webhook.send(file=DeployHistoryMemAsFile)