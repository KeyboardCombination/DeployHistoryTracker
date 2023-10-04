import requests
import discord
import time
import savepagenow
import threading
from datetime import datetime

binaryType = [
    "WindowsPlayer",
    "WindowsStudio",
    #"MacPlayer",
    #"MacStudio"
]

deployServer = [
    "",
    ""
#    "mac/",
#    "mac/"
]

token = open("tokenclientsearch.txt", "r").read()
windows = discord.SyncWebhook.from_url(token)

windows.send(f'Started!')  
def archiveURLS(pkgManifest):
    failinc = 0
    for v in pkgManifest:
        tryinc = 0
        
        while True:
            if (tryinc > 16):
                print("wayback doesn't like us!")
                failinc = failinc + 1
                break
            try:
                versionFile = requests.get(f"https://setup.rbxcdn.com/{version}-{v}")
                #if versionFile.status_code < 400:
                #    open(f"out/{version}-{v}", "wb").write(versionFile.content)
                archive_url, captured = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{version}-{v}")
                print(archive_url)
                break
            except savepagenow.exceptions.WaybackRuntimeError as e:
                open("log.txt", "a").write(str(e) + "\n")
                print("exception!")
                tryinc = tryinc + 1
                print(tryinc)
                time.sleep(15)
            except requests.exceptions.RequestException as e:
                open("log.txt", "a").write(str(e) + "\n")
                print("exception!")
                tryinc = tryinc + 1
                print(tryinc)
                time.sleep(15)
            except requests.exceptions.TooManyRequests as e:
                open("log.txt", "a").write(str(e) + "\n")
                print("exception!")
                tryinc = tryinc + 1
                print(tryinc)
                time.sleep(15)
    
    windows.send(f'Done crawling to web.archive.org! Failed Archives: {failinc}')    

while True:
    for i in range(0, 2):#4):
        print(f"Trying {i}")
        CurrentType = binaryType[i]
        
        requestsincone = 0
        while True:
            if (requestsincone > 4):
                print("roblox doesn't like us!")
                break
            try:
                fetch = requests.get(f"https://clientsettings.roblox.com/v2/client-version/{CurrentType}")
                break
            except requests.exceptions.RequestException as e:
                open("log.txt", "a").write(str(e) + "\n")
                print("exception!")
                requestsincone = requestsincone + 1
                print(requestsincone)
                time.sleep(15)

        cachedDeploy = open(f"{CurrentType}.txt", "r").read()
        
        print(cachedDeploy)
        version = fetch.json().get("clientVersionUpload", '')
        
        if (cachedDeploy != version):
            embedder = discord.Embed(title="New Roblox Deploy!", description = version)

            
            embedder.add_field(name = f'Log Time', value = datetime.now().strftime("%x %X"), inline = False)
            embedder.add_field(name = f'binaryType', value = CurrentType, inline = False)

            embedder.set_image(url="https://cdn.discordapp.com/attachments/986993599742873650/1103331826489114745/deployhistoryupdate.gif")
            
            windows.send(embed=embedder)
            print("NEWDEPLOY!!!")
            open(f"{CurrentType}.txt", "w").write(version)
                    
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
            
            windows.send(embed=fileListEmbed)
            x = threading.Thread(target=archiveURLS, args=(pkgManifest,))
            x.start()
    time.sleep(600)
