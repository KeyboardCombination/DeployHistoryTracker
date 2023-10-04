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

AttemptIncrement = 0
FailIncrementrement = 0

token = open("tokenclientsearch.txt", "r").read()
Webhook = discord.SyncWebhook.from_url(token)

Webhook.send(f'Started!')  

def handleWaybackException(exception):
    open("log.txt", "a").write(str(exception) + "\n")
    print("exception!")
    AttemptIncrement = AttemptIncrement + 1
    print(AttemptIncrement)
    time.sleep(15 * AttemptIncrement)

def archiveURLS(pkgManifest):
    FailIncrement = 0
    for v in pkgManifest:
        AttemptIncrement = 0
        
        while True:
            if (AttemptIncrement > 16):
                print("wayback doesn't like us!")
                FailIncrement = FailIncrement + 1
                break
            try:
                #versionFile = requests.get(f"https://setup.rbxcdn.com/{version}-{v}")
                #if versionFile.status_code < 400:
                #    open(f"out/{version}-{v}", "wb").write(versionFile.content)
                ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{version}-{v}")
                print(ArchiveUrl)
                open("log.txt", "a").write(f"Attempting to capture {ArchiveUrl}...\n")
                break
            except Exception as exception:
                handleWaybackException(exception)
    
    Webhook.send(f'Done crawling to web.archive.org! Failed Archives: {FailIncrement}')    

while True:
    for i in range(0, 2):#4):
        print(f"Trying {i}")
        CurrentBinaryType = BinaryTypes[i]
        
        requestsincone = 0
        while True:
            if (requestsincone > 4):
                print("roblox doesn't like us!")
                break
            try:
                fetch = requests.get(f"https://clientsettings.roblox.com/v2/client-version/{CurrentBinaryType}")
                break
            except requests.exceptions.RequestException as e:
                open("log.txt", "a").write(str(e) + "\n")
                print("exception!")
                requestsincone = requestsincone + 1
                print(requestsincone)
                time.sleep(15)

        cachedDeploy = open(f"{CurrentBinaryType}.txt", "r").read()
        
        print(cachedDeploy)
        version = fetch.json().get("clientVersionUpload", '')
        
        if (cachedDeploy != version):
            NewDeployEmbed = discord.Embed(title="New Roblox Deploy!", description = version)

            
            NewDeployEmbed.add_field(name = f'Log Time', value = datetime.now().strftime("%x %X"), inline = False)
            NewDeployEmbed.add_field(name = f'binaryType', value = CurrentBinaryType, inline = False)

            NewDeployEmbed.set_image(url="https://cdn.discordapp.com/attachments/986993599742873650/1103331826489114745/deployhistoryupdate.gif")
            
            Webhook.send(embed = NewDeployEmbed)
            print("NEWDEPLOY!!!")
            open(f"{CurrentBinaryType}.txt", "w").write(version)
                    
            requestsinctwo = 0
            while True:
                if (requestsinctwo > 4):
                    print("roblox doesn't like us!")
                    break
                try:
                    rbxPkgManifest = requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{version}-rbxPkgManifest.txt")
                    break
                except requests.exceptions.RequestException as e:
                    open("log.txt", "a").write(str(e) + "\n")
                    print("exception!")
                    requestsinctwo = requestsinctwo + 1
                    print(requestsinctwo)
                    time.sleep(15)
            
            fileListEmbed = discord.Embed(title=f"{version} File List:", description = f"From https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt")
            pkgManifest = []
            for v in rbxPkgManifest.text.splitlines():
                if v.find(".") != -1:
                    print(v)
                    pkgManifest.append(v)
                    fileListEmbed.add_field(name = v, value = f"https://setup.rbxcdn.com/{version}-{v}", inline = False)
            fileListEmbed.set_image(url="https://cdn.discordapp.com/attachments/976287740771598379/1105135729744543776/clientsearch_folder2.png")
            
            Webhook.send(embed=fileListEmbed)
            x = threading.Thread(target=archiveURLS, args=(pkgManifest,))
            x.start()
    time.sleep(600)
