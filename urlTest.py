import io
import re
import threading
import time
from datetime import datetime

import discord
import requests
import savepagenow

from globalvals import globalvals
import archiveUrls

def urlTest(curVerArgs):
    pkgManifest, curVersion, versionHashStatic, fileListEmbed = curVerArgs
    currentFailedFiles = []
    currentSuccessFiles = []
    currentSuccessFileNames = []
    for v in pkgManifest:
        print("-------------STARTING HEAD TEST-------------")
        currentClientUrl = f"https://setup.rbxcdn.com/{curVersion}-{v}"
        StatusCheck = requests.head(currentClientUrl)
        print(currentClientUrl)
        print(StatusCheck.status_code)
        print("-------------ENDING HEAD TEST--------------")
        if StatusCheck.status_code != 200:
            currentFailedFiles.append(currentClientUrl)
        elif  StatusCheck.status_code == 200:
            currentSuccessFiles.append(currentClientUrl)
            currentSuccessFileNames.append(v)
    clientListString = bytes("\n".join(currentSuccessFiles), encoding='utf8')
    ClientFileList = discord.File(io.BytesIO(clientListString), filename=f"{versionHashStatic}-ClientFiles.txt")

    globalvals.Webhook.send(embed=fileListEmbed)
    globalvals.Webhook.send(file=ClientFileList)

    if not globalvals.DEBUG_DISABLE_ARCHIVE:
        archiveUrls.archiveURLS((currentSuccessFileNames, curVersion, versionHashStatic))