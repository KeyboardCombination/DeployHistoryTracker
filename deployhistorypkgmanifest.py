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

for i in BinaryTypes:
    open(i+".txt", "a+")

token = open("/home/red/tokenclientsearch.txt", "r").read()
Webhook = discord.SyncWebhook.from_url(token)

Webhook.send(f'Started!')  

def retry(func, retries=10, sleep_seconds=5):
    for i in range(retries):
        try:
            return func
        except Exception as e:
            print(f"Error: {e}")
            if i < retries - 1:
                print(f"Retrying in {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)
            else:
                print(f"Max retries reached. Giving up.")
                return None

ClientArchiveQueue = []
Queuelock = threading.Lock()
def WorkerThread():
    while True:
        time.sleep(0.1)
        while len(ClientArchiveQueue) > 0:
            with Queuelock:
                latest = ClientArchiveQueue.pop(0)
            archiveURLS(latest)

def archiveURLS(pkgManifest):
    for v in pkgManifest:
        print(v)
        retry(SaveClientNow(version, v))
    Webhook.send(f'Done crawling to web.archive.org! Failed Archives: {FailIncrement}')

def SaveClientNow(version, v):
    ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{version}-{v}")
    print(ArchiveUrl)
    open("log.txt", "a").write(f"Attempting to capture {ArchiveUrl}...\n")

def GetCurrentHash(CurrentBinaryType):
    return requests.get(f"https://clientsettings.roblox.com/v2/client-version/{CurrentBinaryType}")

def GetPkgManifest():
    return requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{version}-rbxPkgManifest.txt")

while True:
    for CurrentBinaryType in BinaryTypes:
        fetch = retry(GetCurrentHash(CurrentBinaryType))
        cachedDeploy = open(f"{CurrentBinaryType}.txt", "r").read()
        version = fetch.json().get("clientVersionUpload", '')
        
        if (cachedDeploy != version):
            NewDeployEmbed = discord.Embed(title="New Roblox Deploy!", description = version)
            NewDeployEmbed.add_field(name = f'Log Time', value = datetime.now().strftime("%x %X"), inline = False)
            NewDeployEmbed.add_field(name = f'binaryType', value = CurrentBinaryType, inline = False)
            NewDeployEmbed.set_image(url="https://media.discordapp.net/attachments/1121901772961763421/1157753486063173713/deploy.gif")
            Webhook.send(embed = NewDeployEmbed)

            print("NEWDEPLOY!!!")
            open(f"{CurrentBinaryType}.txt", "w").write(version)

            rbxPkgManifest = retry(GetPkgManifest())
            
            fileListEmbed = discord.Embed(title=f"{version} File List:", description = f"From https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt")
            pkgManifest = []
            for v in rbxPkgManifest.text.splitlines():
                if v.find(".") != -1:
                    pkgManifest.append(v)
                    fileListEmbed.add_field(name = v, value = f"https://setup.rbxcdn.com/{version}-{v}", inline = False)
            fileListEmbed.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1105135729744543776/clientsearch_folder2.png")
            Webhook.send(embed=fileListEmbed)

            with Queuelock:
                ClientArchiveQueue.append((pkgManifest))
    time.sleep(600)

x = threading.Thread(target=WorkerThread)
x.start()
