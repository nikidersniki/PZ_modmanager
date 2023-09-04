import requests
from bs4 import BeautifulSoup
import re
import eel
from configparser import ConfigParser

installedmods = []

name = "pzserver.ini"

eel.init('web')
data = ""
workshop_ids = []
def list_mods(content):
    global workshop_ids
    global data
    data = content
    workshop_line = None
    for line in data.split("\n"):
        if line.startswith("WorkshopItems="):
            workshop_line = line
            break

    # Extract the Workshop IDs separated by semicolons
    if workshop_line:
        # Split the line using semicolons and get rid of the "WorkshopItems=" prefix
        workshop_ids = workshop_line.replace("WorkshopItems=", "").split(";")

        # Remove any leading/trailing whitespace from each ID
        workshop_ids = [id.strip() for id in workshop_ids]
    else:
        print("No WorkshopItems found in the save file.")
@eel.expose
def install(ids,modid,mapid):
    config = ConfigParser()
    config.read("/Users/Nikol/Desktop/pzserver.ini")
    print(config['Config']['Mods'])
    config.set('Config','Mods','ids')
    print(ids, modid, mapid)



@eel.expose                         # Expose this function to Javascript
def search_mod_on_workshop(mod_name):
    # Replace with the URL of the Project Zomboid Workshop
    workshop_url = "https://steamcommunity.com/workshop/browse/?appid=108600&searchtext="+mod_name+"&childpublishedfileid=0&browsesort=textsearch&section="

    # Send a GET request to the workshop URL
    response = requests.get(workshop_url)
    if response.status_code != 200:
        print("Failed to retrieve workshop page")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all mod items on the page
    mod_items = soup.find_all('div', class_='workshopItemTitle ellipsis')
    mod_url = soup.find_all('a', class_='ugc')
    mod_imgs = soup.find_all('img', class_='workshopItemPreviewImage')
    mods = [] #multidimensional array combining the two outputs
    modidsarr = []# array from the output of first for loop 
    imgarr = []
    urlarr = []
    for mod_item in mod_items:
            modidsarr.append(mod_item.string)
    for img in mod_imgs:
            imgg = img['src']
            imgarr.append(imgg)
    for url in mod_url:
            modurl = url['href']
            urlarr.append(modurl)
    for item1, item2, item3 in zip(modidsarr, urlarr, imgarr):
        mods.append([item1, item2, item3])
    return mods

file = ""
@eel.expose
def get_file_content(text):
    file = text
    list_mods(file)

@eel.expose
def get_mod_details(url):
    url= "https://steamcommunity.com/sharedfiles/filedetails/?id="+url
    site = requests.get(url)
    ModIDs=[]
    Workshop=[]
    Maps=[]
    vehicleIDs=[]
    ModDetails=[]
    installed=0
    if site.status_code != 200:
        print("Failed to retrieve workshop page")
        return
    output = BeautifulSoup(site.content, 'html.parser')
    texts=[]
    dets = output.find('div', class_='workshopItemDescription')
    texts = dets.findAll(string=True)
    for mod in texts:
        if mod.startswith("Mod ID:"):
            modid = mod.split(":", 1)[-1].strip()
            ModIDs.append(modid)
        elif mod.startswith("Workshop ID:"):
            wid = mod.split(":", 1)[-1].strip()
            Workshop.append(wid)
        elif mod.startswith("Map Folder:"):
            mapf = mod.split(":", 1)[-1].strip()
            Maps.append(mapf)
        elif mod.startswith("Vehicle IDs:"):
            modid = mod.split(":", 1)[-1].strip()
            vehicleIDs.append(modid)
    for x in Workshop:
        if workshop_ids and x in workshop_ids:
            print("mod is installed")
            installed=1
    ModDetails = [ModIDs, Workshop, Maps, vehicleIDs, installed]
    return ModDetails
@eel.expose
def get_required_mods(url):
    all_a_tags = []
    links = []
    names = []
    req=[]
    url= "https://steamcommunity.com/sharedfiles/filedetails/?id="+url
    site = requests.get(url)
    if site.status_code != 200:
        print("Failed to retrieve workshop page")
        return
    output = BeautifulSoup(site.content, 'html.parser')
    div = output.find('div', class_='requiredItemsContainer')
    if div != None:
        a_tags = div.find_all('a')
        all_a_tags.extend(a_tags)
        for a_tag in all_a_tags:
            div_tag = a_tag.find('div')
            name = div_tag.get_text()
            name = re.sub(r'\s+', ' ', name).strip()
            names.append(name)
            links.append(a_tag.get('href'))
    req = [names, links]
    req = list(zip(*req))
    return req

eel.start('index.html', mode="electron")




