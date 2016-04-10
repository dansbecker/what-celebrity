import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from PIL import Image, ImageDraw

def reformat_face_corners(df):
    df['face_left_x'] = df.apply(lambda x: x.face_corners[0], axis=1)
    df['face_upper_y'] = df.apply(lambda x: x.face_corners[1], axis=1)
    df['face_right_x'] = df.apply(lambda x: x.face_corners[2], axis=1)
    df['face_lower_y'] = df.apply(lambda x: x.face_corners[3], axis=1)
    df = df.drop('face_corners', axis=1)
    return df

def get_image_dims(df):
    all_dims = df.local_img_path.apply(lambda x:Image.open(x).getbbox())
    df['image_width'] = all_dims.apply(lambda x: x[2])
    df['image_height'] = all_dims.apply(lambda x: x[3])
    return df

def plot_with_boxed_face(df):
    assert(df.shape[0]) < 100 #we almost never want to print that many images
    for img in df.iterrows():
        img = Image.open(img.local_img_path)
        dr = ImageDraw.Draw(img)
        dr.rectangle(xy=(face_left_x, face_upper_y, face_right_x, face_lower_y))
        img.show()
    return

def add_face_dims_and_margins(df):
    output = (df.assign(face_width = lambda x: x.face_right_x - x.face_left_x,
                       face_height = lambda x: x.face_lower_y - x.face_upper_y,
                       face_left_margin = lambda x: x.face_left_x,
                       face_right_margin = lambda x: x.image_width - x.face_right_x,
                       face_top_margin = lambda x: x.face_upper_y,
                       face_lower_margin = lambda x: x.image_height - x.face_lower_y))
    return output

def filter_by_face_size_and_loc(df,
                                min_face_size=55,  # many of the smaller face boxes are inaccurate
                                min_pct_horiz_face_border=0.05,
                                min_pct_vert_face_border=0.25):
    output = (df.query("face_width > @min_face_size")
               .query("face_top_margin / face_height > @min_pct_vert_face_border")
               .query("face_lower_margin / face_height > @min_pct_vert_face_border")
               .query("face_right_margin / face_height > @min_pct_horiz_face_border")
               .query("face_left_margin / face_height > @min_pct_horiz_face_border"))
    return output


if __name__ == "__main__":
    with open('work/facial_feats_data.json', 'r') as f:
        img_dat = json.load(f)
    imgs_with_faces = [i for i in img_dat if len(i['face_corners'])>0]
    img_df = (pd.DataFrame(imgs_with_faces)
                .pipe(get_image_dims)
                .pipe(reformat_face_corners)
                .pipe(add_face_dims_and_margins)
                .pipe(filter_by_face_size_and_loc)
                )
    img_df.to_csv('work/image_and_face_dims.csv', index=False)
    #sns.distplot(img_df.face_width, bins=40, kde=True)
    #plt.show()
