import indicoio
import concurrent.futures
import os
from PIL import Image, ImageDraw
from os.path import join
import json
from image_grabber import DataGrabber

class FacialFeatsGrabber(DataGrabber):
    def __init__(self):
        self._failed_to_capture_path = join('work', 'failed_to_featurize.json')
        self._captured_data_path = join('work', 'facial_feats_data.json')
        socket.setdefaulttimeout(5)

    def grab_one(self, url, local_img_path, search_term):
        try:
            img = Image.open(img_path)
            self.captured_data.append(  {'celeb': celeb,
                                        'face_feats': indicoio.facial_features(img),
                                        'face_corners': self._get_single_face_corners(img),
                                        'url': url
                                        'local_img_path': img_path,
                                        })
        except:
            self.failed_to_capture.append((url, local_img_path, search_term))

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


    def get_all_face_feats():
        """
        Creates facial_feats_data.json with features and image corners for each image
        stores list of images that could not be captured in failed_to_featurize.json
        """

        facial_feats_path = join("work", "facial_feats_data.json")
        failed_to_featurize_path = join("work", "failed_to_featurize.json")
        try:
            with open(facial_feats_path, 'r') as f:
                feats_data = json.load(f)
        except:
            feats_data = []
        try:
            with open(failed_to_featurize_path, 'r') as f:
                failed_to_featurize = json.load(f)
        except:
            failed_to_featurize = []

        indicoio.config.api_key = os.environ['INDICO_API_KEY']

        celeb_dirs = [d for d in os.listdir('work')
                          if os.path.isdir(join('work', d))]
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as worker_pool:
            for celeb in celeb_dirs:
                for fname in os.listdir(join('work', celeb)):
                    img_path = join('work', celeb, fname)
                    worker_pool.submit(add_single_face_data,
                                       celeb, img_path, feats_data, failed_to_featurize)
        with open('work/facial_feats_data.json', 'w') as f:
            json.dump(feats_data, f)
        with open('work/failed_to_featurize.json', 'w') as f:
            json.dump(failed_to_featurize, f)

def show_box_on_face(img, face_corners, outpath, box_color="orange"):
    """saves copy of img to outpath with box drawn to outline face
    based on coordinates given by face_corners
    img is a PIL or Pillow Image object
    face_corners is a tuple (x0, y0, x1, y1) of upper left and lower right corners
    """
    dr = ImageDraw.Draw(img)
    dr.rectangle(xy=face_corners, outline=box_color)
    img.save(outpath)
