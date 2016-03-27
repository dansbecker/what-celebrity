import json
import os
import concurrent.futures
import urllib.request
from os.path import join, exists

class ImageGrabber(object):
    def __init__(self, celeb_urls_dict):
        self.celeb_urls_dict = celeb_urls_dict
        self._failed_to_capture_path = join('work', 'failed_to_capture.json')

    def __enter__(self):
        try:
            with open(self._failed_to_capture_path, 'r') as f:
                self.failed_to_capture = json.load(f)
        except:
            self.failed_to_capture = []
        return(self)

    def __exit__(self, *args):
        print(*args)
        with open(self._failed_to_capture_path, 'w') as f:
            json.dump(self.failed_to_capture, f)

    def _url_to_fname(self, url):
        return ''.join([i for i in url if i.isalpha()])

    def _make_target_dir(self, celeb_name):
        name_for_path = celeb_name.replace(" ", "_").casefold()
        path = join('work', name_for_path)
        if not exists(path):
            os.mkdir(path)
        return path

    def _get_img(self, url, local_img_path, search_term):
        try:
            url, path = urllib.request.urlretrieve(url, local_img_path)
        except:
            self.failed_to_capture.append((url, search_term))

    def _get_file_path(self, url, search_term):
        search_term_dir = self._make_target_dir(search_term)
        local_img_path = join(search_term_dir, self._url_to_fname(url)+".jpg")
        return local_img_path

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as worker_pool:
            for search_term, url_list in self.celeb_urls_dict.items():
                local_img_paths = [self._get_file_path(url, search_term) for url in url_list]
                for url, local_img_path in zip(url_list, local_img_paths):
                    if not exists(local_img_path):
                        worker_pool.submit(self._get_img(url, local_img_path, search_term))

    def try_again_on_failed_images(self):
        # Should be few enough images that concurrency is unimportant
        for url, search_term in self.failed_to_capture:
            local_img_path = self._get_file_path(url, search_term)
            try:
                self._get_img(url, local_img_path, search_term)
                self.failed_to_capture.remove([url, search_term])
            except:
                pass
