import requests
import discord
import time
import savepagenow
import threading
from datetime import datetime

BinaryTypes = [
    "WindowsPlayer",
    "WindowsStudio",
    #"MacPlayer",
    #"MacStudio" TODO: Mac client support
]

currentClientUrl = ""
currentFailedFiles = []

for i in BinaryTypes:
    open(i+".txt", "a+")

token = open("/home/red/tokenclientsearch.txt", "r").read()
Webhook = discord.SyncWebhook.from_url(token)

Webhook.send(f'Started!')

ClientArchiveQueue = []
Queuelock = threading.Lock()
def WorkerThread():
    while True:
        time.sleep(0.1)
        while len(ClientArchiveQueue) > 0:
            with Queuelock:
                latest = ClientArchiveQueue.pop(0)
            archiveURLS(latest)

def archiveURLS(curVerArgs):
    time.sleep(20)
    pkgManifest, curVersion = curVerArgs
    currentFailedFiles = []
    for v in pkgManifest:
        time.sleep(20)
        currentClientUrl = f"https://setup.rbxcdn.com/{curVersion}-{v}"
        print(currentClientUrl)
        for i in range(16):
            try:
                SaveClientNow(curVersion, v)
                time.sleep(8)
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

    FailedArchiveEmbed = discord.Embed(title=f"Done! Failed Archives: {len(currentFailedFiles)}", description = curVersion)
    for i in currentFailedFiles:
        FailedArchiveEmbed.add_field(name = "", value = i, inline = False)
    Webhook.send(embed=FailedArchiveEmbed)

    DeployHistoryFailFlag = False
    time.sleep(20)
    for i in range(16):
        try:
            ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/DeployHistory.txt")
        except Exception as e:
            time.sleep(60)
            if i == 15:
                DeployHistoryTxtArchive = discord.Embed(title="Attempted Archive Of Deployhistory.txt...", description = "Failed!")
                DeployHistoryTxtArchive.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1161763241454735480/billc.png")
                DeployHistoryFailFlag = True
    if not DeployHistoryFailFlag:
        DeployHistoryTxtArchive = discord.Embed(title="Attempted Archive Of Deployhistory.txt...", description = "Succeeded!")
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

x = threading.Thread(target=WorkerThread)
x.start()

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
        version = fetch.json().get("clientVersionUpload", '')

        if (cachedDeploy != version):
            NewDeployEmbed = discord.Embed(title="New Roblox Deploy!", description = version)
            NewDeployEmbed.add_field(name = f'Log Time', value = datetime.now().strftime("%x %X"), inline = False)
            NewDeployEmbed.add_field(name = f'binaryType', value = CurrentBinaryType, inline = False)
            NewDeployEmbed.set_image(url="https://cdn.discordapp.net/attachments/1121901772961763421/1157753486063173713/deploy.gif")
            Webhook.send(embed = NewDeployEmbed)

            print("NEWDEPLOY!!!")
            open(f"{CurrentBinaryType}.txt", "w").write(version)

            for i in range(16):
                try:
                    rbxPkgManifest = GetPkgManifest(version)
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    open("log.txt", "a").write(f"{e}\n")
                    time.sleep(8)

            fileListEmbed = discord.Embed(title=f"{version} File List:", description = f"From https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt")
            pkgManifest = []
            #open("testDoc.txt", "a").write(str(rbxPkgManifest.text))
            for v in rbxPkgManifest.text.splitlines():
                if v.find(".") != -1:
                    pkgManifest.append(v)
                    fileListEmbed.add_field(name = v, value = f"https://setup.rbxcdn.com/{version}-{v}", inline = False)
            fileListEmbed.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1105135729744543776/clientsearch_folder2.png")
            Webhook.send(embed=fileListEmbed)
            pkgManifest.append("rbxManifest.txt")
            if CurrentBinaryType == BinaryTypes[1]:
                pkgManifest.append("RobloxStudioLauncherBeta.exe")

            with Queuelock:
                print("LOCK")
                ClientArchiveQueue.append((pkgManifest, version))
    time.sleep(600)
