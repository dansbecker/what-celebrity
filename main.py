from apiclient.discovery import build
import json
import os
from data_grabbers import ImageGrabber, FacialFeatsGrabber



def show_box_on_face(img, face_corners, outpath, box_color="orange"):
    """saves copy of img to outpath with box drawn to outline face
    based on coordinates given by face_corners
    img is a PIL or Pillow Image object
    face_corners is a tuple (x0, y0, x1, y1) of upper left and lower right corners
    """
    dr = ImageDraw.Draw(img)
    dr.rectangle(xy=face_corners, outline=box_color)
    img.save(outpath)

def image_urls_api_call(search_term, previously_captured_num, imgSize="medium"):
    """returns list of image urls (with faces) from google image search on search_term"""
    try:
        key = os.environ['GOOGLE_CUSTOM_SEARCH_KEY']
        service = build("customsearch", "v1",
                        developerKey=key)

        res = service.cse().list(
                                q=search_term,
                                cx='018267786259991380019:ja65luoszbg', # my custom search engine id.
                                searchType='image',
                                filter='1',
                                num=10,
                                imgSize=imgSize,
                                imgType="face",
                                fileType="jpg",
                                start = previously_captured_num
                                ).execute()

        links = [item['link'] for item in res['items']]
        print('Added links for ' + search_term)
        return(links)
    except:
        print('Failed to get links for ' + search_term)
        return []


def update_image_urls(celebs_list):
    """
    Reads celeb_image_urls.json and adds urls for celebrities
    that have fewer stored urls than the minimum number + 10.  This is a tactic
    to gradually accrue more links over time without exceeding the daily api call
    limit
    """
    new_links_per_api_call = 10
    try:
        with open('work/celeb_image_urls.json', 'r') as f:
            urls = json.load(f)
    except:
        urls = {}


    min_link_count = min((len(urls[name]) for name in urls))
    for name in celebs_list:
        if name not in urls:
            urls[name] = []
        img_count = len(urls[name])
        if img_count < min_link_count + new_links_per_api_call + 1:
            try:
                def dedup(l): return list(set(l))
                urls[name] = dedup(urls[name] + image_urls_api_call(name, img_count))
            except:     # api call fails if hit daily usage limit
                pass


    with open('work/celeb_image_urls.json', 'w') as f:
        json.dump(urls, f)
    total_urls_stored = sum([len(i) for i in urls.values()])
    print('Total urls stored: ' + str(total_urls_stored))
    return urls

if __name__ == "__main__":
    with open('celebs_list.txt', 'r') as celebs_file:
        celebs_list = [line.strip('\n') for line in celebs_file]
    celeb_urls_dict = update_image_urls(celebs_list)
    with ImageGrabber(celeb_urls_dict) as ig:
        ig.run()
    with FacialFeatsGrabber() as ffg:
        ffg.run()
