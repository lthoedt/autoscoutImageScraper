import requests
import json
import re
import os
import sys, getopt

URL : str = "https://www.autoscout24.nl/_next/data/as24-search-funnel_main-4422/lst.json?cy=NL&page=";
downloadLocation = "./images";

loadedImages = 0;

def getUrl(page : int) -> str:
    return f"{URL}{page}";

class Image:
    def __init__(self, url):
        self.url = self.normalizeUrl(url);
        global loadedImages
        loadedImages = loadedImages + 1;

    def normalizeUrl(self, url) -> str:
        return re.sub("\/[0-9]*x[0-9]*\.[a-z]*", "", url);

    def getImageName(self) -> str:
        split = self.url.split("/")
        return split[len(split) - 1];

    def download(self, location) -> bool:
        print(f"Retrieving: {self.url}");
        response = requests.get(self.url);
        if (response.status_code != 200):
            print(f"Retrieving: failed.");
            return False;

        path = os.path.join(location, self.getImageName());

        print(f"Saving to: {path}");
        open(path, "wb").write(response.content);
        return True;

class Vehicle:
    def __init__(self, vehicleJson):
        self.make = vehicleJson['make'];
        self.model = vehicleJson['model'];

class Listing:
    def __init__(self, listingJson):
        self.images = list(map(lambda e: Image(e), list(listingJson['images'])));
        self.vehicle = Vehicle(listingJson['vehicle']);

def getListings(page : int) -> list[Listing] | None:
    response = requests.get(getUrl(page));
    if (response.status_code != 200) :
        return None;

    body = json.loads(response.text);
    listings = body['pageProps']['listings'];
    return list(map(lambda e: Listing(e), listings));

def main(argv):
    global loadedImages
    loadedImages = 0;
    nImages : int = 20;

    opts, args = getopt.getopt(argv,"hd:n:",["dir="])
    for opt, arg in opts:
        if opt == '-h':
            print ('main.py -d <directory> -n <image count>')
            sys.exit();
        elif opt in ("-d", "--dir"):
            global downloadLocation
            downloadLocation = arg;
        elif opt in ("-n"):
            nImages = int(arg);

    listings : list[Listing] = list();

    currentPageIndex = 1;

    while nImages > loadedImages:
        retrievedListings : list[Listing] | None = getListings(currentPageIndex);
        if (retrievedListings == None or len(retrievedListings) == 0):
            break;
        listings.extend(retrievedListings);
        currentPageIndex += currentPageIndex + 1;

    downloadedImages = 0;

    if not os.path.exists(downloadLocation):
        os.makedirs(downloadLocation);

    for listing in listings:
        for image in listing.images:
            if (downloadedImages >= nImages):
                break;

            if (image.download(downloadLocation)):
                downloadedImages = downloadedImages + 1;

if __name__ == "__main__":
   main(sys.argv[1:])