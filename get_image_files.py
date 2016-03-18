from apiclient.discovery import build
import os
from pprint import pprint
import concurrent.futures
import urllib.request

def get_image_urls(search_term):
    try:
        key = os.environ['GOOGLE_CUSTOM_SEARCH_KEY']
        service = build("customsearch", "v1",
                        developerKey=key)

        res = service.cse().list(
                                q=search_term,
                                cx='017560911483415735967:xx4esjwh_qu', # my custom search engine id. Just google
                                searchType='image',
                                num=10,
                                imgSize="medium",
                                imgType="face",
                                fileType="jpg"
                                ).execute()

        links = [item['link'] for item in res['items']]
        return(links)
    except:
        print("Failed to get links for " + search_term)
        return []


def get_img(url, local_path):
    try:
        url, path = urllib.request.urlretrieve(url, local_path)
        return url, path
    except:
        print("Failed to download and save image: " + url)


if __name__ == "__main__":
    with open('celebs_list.txt', 'r') as celebs_file:
        celebs_list = [line.strip('\n') for line in celebs_file]
    for name in celebs_list:
        # OUGHT TO STORE LIST OF fname-URL pairs... these already come back from call to get_img
        name_for_path = name.replace(" ", "_").casefold()
        os.mkdir('work/' + name_for_path)
        image_urls = get_image_urls(name)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
            for i, url in enumerate(image_urls):
                local_path = os.path.join('.', 'work', name_for_path, str(i)+".jpg")
                e.submit(get_img, url, local_path)
