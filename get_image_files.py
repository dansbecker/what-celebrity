from apiclient.discovery import build
import json
import os
from image_grabber import ImageGrabber

def image_urls_api_call(search_term):
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


def update_image_urls(celebs_list):
    try:
        with open('work/celeb_image_urls.json', 'r') as f:
            old_celebs_urls_dict = json.load(f)
    except:
        old_celebs_urls_dict = {}

    # Avoid calling google search API on names we've called it on before due to API limit
    new_celeb_urls_dict = {name: image_urls_api_call(name) for name in celebs_list if
                                                name not in old_celebs_urls_dict.keys()}
    # handle failed api calls
    new_celeb_urls_dict = {k: v for k, v in new_celeb_urls_dict.items() if len(v)>0}
    new_celeb_urls_dict.update(old_celebs_urls_dict)
    with open('work/celeb_image_urls.json', 'w') as f:
        json.dump(new_celeb_urls_dict, f)
    return new_celeb_urls_dict

if __name__ == "__main__":
    with open('celebs_list.txt', 'r') as celebs_file:
        celebs_list = [line.strip('\n') for line in celebs_file]
    celeb_urls_dict = update_image_urls(celebs_list)
    with ImageGrabber(celeb_urls_dict) as g:
        g.run()
        g.try_again_on_failed_images()
