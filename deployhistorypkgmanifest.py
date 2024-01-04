import requests
import discord
import time
import savepagenow
import threading
import io
from datetime import datetime

DEBUG_MODE = True

BinaryTypes = [
    "WindowsPlayer",
    "WindowsStudio64",
    "MacPlayer",
    "MacStudio"
]

Channels = [
    "LIVE",
    #"zcanary",
    #"zintegration"
]

currentClientUrl = ""
currentFailedFiles = []

for i in BinaryTypes:
    open(i+".txt", "a+")

token = open("/home/red/tokenclientsearch.txt", "r").read()
Webhook = discord.SyncWebhook.from_url(token)

if DEBUG_MODE:
    Webhook.send(f'Started (Debug)!')
else:
    Webhook.send(f'Started!')

ClientArchiveQueue = []
Queuelock = threading.Lock()
def WorkerThread():
    while True:
        time.sleep(0.1)
        while len(ClientArchiveQueue) > 0:
            with Queuelock:
                latest = ClientArchiveQueue.pop(0)
            urlTest(latest)

def urlTest(curVerArgs):
    pkgManifest, curVersion, versionHashStatic, fileListEmbed = curVerArgs
    currentFailedFiles = []
    currentSuccessFiles = []
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

    clientListString = bytes("\n".join(currentSuccessFiles), encoding='utf8')
    ClientFileList = discord.File(io.BytesIO(clientListString), filename=f"{versionHashStatic}-ClientFiles.txt")

    Webhook.send(embed=fileListEmbed)
    Webhook.send(file=ClientFileList)

    if not DEBUG_MODE:
        archiveURLS((currentSuccessFiles, curVersion, versionHashStatic))


def archiveURLS(curVerArgs):
    time.sleep(20)
    pkgManifest, curVersion, versionHashStatic = curVerArgs
    currentFailedFiles = []
    for v in pkgManifest:
        time.sleep(20)
        currentClientUrl = f"https://setup.rbxcdn.com/{curVersion}-{v}"
        print(currentClientUrl)
        for i in range(16):
            try:
                time.sleep(8)
                SaveClientNow(curVersion, v)
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
    Webhook.send(embed=FailedArchiveEmbed)

    DeployHistoryFailFlag = False
    time.sleep(20)
    for i in range(16):
        try:
            ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/DeployHistory.txt")
            break
        except Exception as e:
            time.sleep(60)
            if i == 15:
                DeployHistoryTxtArchive = discord.Embed(title="Attempted Archive Of https://setup.rbxcdn.com/DeployHistory.txt", description = "Failed!")
                DeployHistoryTxtArchive.set_image(url="https://media.discordapp.com/attachments/976287740771598379/1161763241454735480/billc.png")
                DeployHistoryFailFlag = True
    if not DeployHistoryFailFlag:
        DeployHistoryTxtArchive = discord.Embed(title="Attempted Archive Of https://setup.rbxcdn.com/DeployHistory.txt", description = "Succeeded!")
        DeployHistoryTxtArchive.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1161764162284830820/rfold.png")
    Webhook.send(embed=DeployHistoryTxtArchive)

def SaveClientNow(curVersion, v):
    ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{curVersion}-{v}")
    print(ArchiveUrl)
    open("log.txt", "a").write(f"Attempting to capture {ArchiveUrl[0]}...\n")

def GetCurrentHash(CurrentBinaryType):
    return requests.get(f"https://clientsettings.roblox.com/v2/client-version/{CurrentBinaryType}")

def GetPkgManifest(curVersion):
    return requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{curVersion}-rbxPkgManifest.txt")

def GetPkgInstallerManifest(curVersion):
    return requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{curVersion}-rbxInstallerPkgManifest.txt")

x = threading.Thread(target=WorkerThread)
x.start()

def ChannelArchiveBot(channel):
    while True:
        for CurrentBinaryType in BinaryTypes:
            for i in range(16):
                try:
                    fetch = GetCurrentHash(CurrentBinaryType)
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    open("log.txt", "a").write(f"{e}\n")
                    time.sleep(8)

            cachedDeploy = open(f"{CurrentBinaryType}.txt", "r").read()
            versionHashStatic = fetch.json().get("clientVersionUpload", '')
            version = versionHashStatic
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
                Webhook.send(embed = NewDeployEmbed)

                print("NEWDEPLOY!!!")
                open(f"{CurrentBinaryType}.txt", "w").write(versionHashStatic)

                for i in range(16):
                    try:
                        rbxPkgManifest = GetPkgManifest(version)
                        if CurrentBinaryType.find("Mac") == -1:
                            rbxPkgInstallerManifest = GetPkgInstallerManifest(version)
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
