import numpy as np
import os
import pandas as pd
from PIL import Image, ImageDraw

def ensure_thumbnail_paths(img_df, thumbnails_path="work/thumbnails"):
    os.makedirs(thumbnails_path, exist_ok=True)
    for celeb in img_df.celeb.unique():
        os.makedirs(os.path.join(thumbnails_path, celeb), exist_ok=True)
    return

def make_training_thumbnails(img_df, horiz_pad_frac=0.05, vert_pad_frac=0.1,
                             output_height=100, data_outpath='work/thumbnail_px_and_targ.npy'):

    #assumes face width is same as face height. True in first indico facial capture api
    aspect_ratio = (1+2*horiz_pad_frac) / (1+2*vert_pad_frac)
    output_width = round(output_height * aspect_ratio)
    ensure_thumbnail_paths(img_df)

    pixel_level_data = np.empty([img_df.shape[0],
                                 output_height,
                                 output_width,
                                 3])
    modes = []
    for i, row in img_df.iterrows():
        fname = row.local_img_path.split('/')[-1][:-4] #discard the extension
        outpath = os.path.join('work', 'thumbnails', row.celeb, fname)+".png"
        img = Image.open(row.local_img_path)
        if img.mode != "RGB":  # Could revisit and deal with less common formats
            continue
        horiz_pad_px = horiz_pad_frac * row.face_width
        vert_pad_px = vert_pad_frac * row.face_height
        cropped_image = img.crop((row.face_left_x - horiz_pad_px,
                                  row.face_upper_y - vert_pad_px,
                                  row.face_right_x + horiz_pad_px,
                                  row.face_lower_y + vert_pad_px))
        thumbnail = cropped_image.resize((output_width, output_height))
        thumbnail.save(outpath)
        modes.append(img.mode)
        pixel_level_data[i, :, :, :] = np.array(thumbnail)
    np.savez(data_outpath, x=pixel_level_data, y=img_df.celeb.values)
    return

if __name__ == "__main__":
    img_df = pd.read_csv('work/image_and_face_dims.csv')
    make_training_thumbnails(img_df, 0.05, 0.20)
