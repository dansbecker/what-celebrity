import concurrent.futures
import indicoio
import json
import os
import socket
import urllib.request
from os.path import join, exists
from PIL import Image, ImageDraw


class Grabber(object):
    def __enter__(self):
        try:
            with open(self._captured_data_path, 'r') as f:
                self.captured_data = json.load(f)
        except:
            self.captured_data = []

        try:
            with open(self._failed_to_capture_path, 'r') as f:
                self.failed_to_capture = json.load(f)
        except:
            self.failed_to_capture = []
        return(self)

    def __exit__(self, *args):
        with open(self._captured_data_path, 'w') as f:
            json.dump(self.captured_data, f)
        with open(self._failed_to_capture_path, 'w') as f:
            json.dump(self.failed_to_capture, f)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as worker_pool:
            list_to_capture = self._make_list_to_capture()
            for img_src, search_term in list_to_capture: # img_src can be url or local file path
                worker_pool.submit(self._grab_one(img_src, search_term))

class ImageGrabber(Grabber):
    def __init__(self, celeb_urls_dict):
        self.celeb_urls_dict = celeb_urls_dict
        self._failed_to_capture_path = join('work', 'failed_to_capture_images.json')
        self._captured_data_path = join('work', 'captured_image_info.json')
        socket.setdefaulttimeout(5)

    def _url_to_fname(self, url):
        return ''.join([i for i in url if i.isalpha()])

    def _make_target_dir(self, celeb_name):
        name_for_path = celeb_name.replace(" ", "_").casefold()
        path = join('work', name_for_path)
        if not exists(path):
            os.mkdir(path)
        return path

    def _grab_one(self, url, search_term):
        print(url)
        local_img_path = self._get_file_path(url, search_term)
        try:
            url, _ = urllib.request.urlretrieve(url, local_img_path)
            self.captured_data.append((url, local_img_path, search_term))
        except:
            self.failed_to_capture.append((url, local_img_path, search_term))

    def _get_file_path(self, url, search_term):
        search_term_dir = self._make_target_dir(search_term)
        local_img_path = join(search_term_dir, self._url_to_fname(url)+".jpg")
        return local_img_path

    def _make_list_to_capture(self):
        output = []
        for search_term, url_list in self.celeb_urls_dict.items():
            for url in url_list:
                if not exists(self._get_file_path(url, search_term)):
                    output.append((url, search_term))
        return output


class FacialFeatsGrabber(Grabber):
    def __init__(self):
        self._failed_to_capture_path = join('work', 'failed_to_featurize.json')
        self._captured_data_path = join('work', 'facial_feats_data.json')
        indicoio.config.api_key = os.environ['INDICO_API_KEY']
        socket.setdefaulttimeout(5)

    def _grab_one(self, local_img_path, search_term):
        try:
            img = Image.open(local_img_path)
            self.captured_data.append(  {'celeb': search_term,
                                        'face_feats': indicoio.facial_features(img),
                                        'face_corners': self._get_single_face_corners(img),
                                        'local_img_path': local_img_path
                                        })
        except:
            self.failed_to_capture.append((local_img_path, search_term))

    def _get_single_face_corners(self, img):
        """
        returns x and y coords of upper and lower left pixel of face in img (a PIL Image object)
        """
        try:
            face_corners = indicoio.facial_localization(img)[0]
            x0, y0 = face_corners['top_left_corner']
            x1, y1 = face_corners['bottom_right_corner']
            return (x0, y0, x1, y1)
        except:
            return ()

    def _make_list_to_capture(self):
        output = []
        already_featurized_paths = [img['local_img_path'] for img in self.captured_data]
        celeb_dirs = [d for d in os.listdir('work') if os.path.isdir(join('work', d))]
        for celeb in celeb_dirs:
            for fname in os.listdir(join('work', celeb)):
                local_img_path = join('work', celeb, fname)
                if local_img_path not in already_featurized_paths:
                    output.append((local_img_path, celeb))
        return output
