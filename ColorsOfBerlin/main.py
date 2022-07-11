"""
ColorsOfBerlin python script.

Yukino Kondo
"""

import urllib.request
from datetime import datetime
from datetime import timedelta
import json
import os
from smtplib import SMTP, SMTPException
import requests
import cloudinary.uploader
import cloudinary
from PIL import Image, ImageDraw
from sklearn.cluster import KMeans
import cv2 as cv
import numpy as np

# Using mapped secrets as env variables
CLOUD_API_KEY = os.environ['CLOUD_API_KEY']
CLOUD_API_SECRET = os.environ['CLOUD_API_SECRET']
CLOUD_NAME = os.environ['CLOUD_NAME']
GMAIL_EMAIL = os.environ['GMAIL_EMAIL']
GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
IG_ACCESS_TOKEN = os.environ['IG_ACCESS_TOKEN']
IG_PASSWORD = os.environ['IG_PASSWORD']
IG_USERNAME = os.environ['IG_USERNAME']
IG_USER_ID = os.environ['IG_USER_ID']
WINDY_API_KEY = os.environ['WINDY_API_KEY']

# Configuration for the Cloudinary platform
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=CLOUD_API_KEY,
    api_secret=CLOUD_API_SECRET,
)


def pull_image():
    """
    Pulls webcam image from windy and saves a temporary local copy to use later.
    """

    url = 'https://api.windy.com/api/webcams/v2/list/webcam=1211725853?show=webcams:image'
    headers = {'x-windy-key': WINDY_API_KEY}

    req = requests.get(url, headers=headers)

    # Pulling URL for the latest daylight image from the Berlin - Potsdamer Platz webcam
    daylight_image = req.json(
    )['result']['webcams'][0]['image']['current']['preview']

    url = daylight_image

    # file_name_org_img = datetime.today().strftime('%Y-%m-%d') + '.jpg'

    absolute_path = os.path.abspath('temp.jpg')

    with urllib.request.urlopen(url) as url:
        with open(absolute_path, 'wb') as f:
            f.write(url.read())

    return f.name


def rgb_to_hex(rgb_values):
    """
    Converts RGB values to HEX values.
    """
    # pylint: disable=consider-using-f-string
    return '#%02x%02x%02x' % (rgb_values)


def extract_dom_colors(img, color_count):
    """
    Extracts dominant colors using the KMeans clustering method.
    """
    # Read in image
    img = cv.imread(img)
    # Convert image from BGR to RGB for color quantization
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    # Reshape the image to be a list of pixels
    X = img.reshape((-1, 3))
    # Using KMeans to cluster the color intensities
    km = KMeans(n_clusters=color_count)
    km.fit(X)
    # Get number of colors
    palette = len(np.unique(km.labels_))
    # Create a histogram of the number of pixels assigned to each cluster
    hist = np.histogram(km.labels_, bins=np.arange(0, palette + 1))
    # Convert to float to divide a float from the array
    # pylint: disable=no-member
    hist = hist[0].astype('float64')
    # Normalize histogram to get the percentage of a color/cluster present in image
    hist /= hist.sum()

    return hist, palette, km.cluster_centers_

# pylint: disable=too-many-locals
def create_palette(img):
    """
    Using the colors extracted by KMeans, create an image with the colors.
    """
    hist, palette, cluster_centers = extract_dom_colors(img, 5)

    # Preparing canvas
    size = 200
    columns = palette
    width = int(columns * size)
    height = int(columns * size)
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    canvas = ImageDraw.Draw(result)

    hex_arr = []

    for i, (percent, color) in enumerate(zip(hist, cluster_centers)):
        # Convert numpy array to a tuple
        color = tuple(map(int, color))
        hex_arr.append(rgb_to_hex(color))
        # The idea is to increase width of color based on their percentage present in image
        # The most dominant color in the image will have a wider width on canvas
        percent_width = int(percent * width)
        end_y = height
        if i == 0:
            start_x = 0
            start_y = 0
        else:
            start_x = end_x
        end_x = start_x + percent_width
        canvas.rectangle([(start_x, start_y), (end_x, end_y)],
                         fill=color, outline=(255, 255, 255))

    absolute_path = os.path.abspath("palette.png")

    result.save(absolute_path)

    return hex_arr


def upload_image_cloudinary(file_name):
    """
    Upload the color palette image to cloudinary.
    """
    uploaded_image = cloudinary.uploader.upload(file=file_name,
                                                use_filename=True,
                                                unique_filename=False,
                                                folder='/ColorsOfBerlin')

    image_url = uploaded_image['secure_url']
    public_id = uploaded_image['public_id']

    return image_url, public_id


def upload_insta(url, hex_val):
    """
    Uploads the hosted image to instagram with the hex value in the comments.
    """
    hex_str = ' '.join(hex_val)

    post_url = f'https://graph.facebook.com/v14.0/{IG_USER_ID}/media'

    payload = {
        'image_url': url,
        'caption': datetime.today().strftime('%Y-%m-%d') + "'s daytime colors:\n" + hex_str,
        'access_token': IG_ACCESS_TOKEN
    }

    r = requests.post(post_url, data=payload)

    result = json.loads(r.text)

    if 'id' in result:
        creation_id = result['id']

        media_publish_url = f'https://graph.facebook.com/v14.0/{IG_USER_ID}/media_publish'

        publish_payload = {
            'creation_id': creation_id,
            'access_token': IG_ACCESS_TOKEN
        }

        r = requests.post(media_publish_url, data=publish_payload)

def delete_img_cloudinary(public_id):
    """
    Deletes image from cloudinary to save some space.
    """
    cloudinary.uploader.destroy(public_id)


def send_email(subject, body):
    """
    Send an email with subject and body text.
    """

    from_email = GMAIL_EMAIL
    to_email = GMAIL_EMAIL
    # pylint: disable=unused-variable
    subject_text = subject
    body_text = body

    # Prepare the message
    message = f"""From: {GMAIL_EMAIL}\nTo: {GMAIL_EMAIL}\nSubject: {subject_text}\n\n{body_text}"""
    try:
        server = SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        server.sendmail(from_email, to_email, message)
        server.close()
        print('Sent Mail')
    except SMTPException:
        print("Failed to send email")

def main():
    """
    1. Pulls Image from Webcam
    2. Creates a color palette by extracting dominant colors in an image
    3. Uploads the color palette image to cloudinary
    4. Pulls the color palette image from cloudinary and upload it to instagram (can only post on Instagram from a hosted site)
    5. Delete the color palette image from cloudinary to save space
    """

    try:
        img_file = pull_image()
        hex_val = create_palette(img_file)
        image_url, public_id = upload_image_cloudinary('palette.png')
        upload_insta(image_url, hex_val)
        delete_img_cloudinary(public_id)
        token_change_date_plus_60 = datetime.strptime('2022-06-06', '%Y-%m-%d') + timedelta(days=60)
        print('Success!! Tokens expire on ' + str(token_change_date_plus_60))

    # pylint: disable=broad-except
    except Exception as e:
        send_email('Colors of Berlin Failed', e)
        print(e)


if __name__ == '__main__':
    main()
