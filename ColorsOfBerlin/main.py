"""
ColorsOfBerlin python script.

Yukino Kondo
"""

import credentials
import urllib.request
from datetime import datetime
import cloudinary.uploader
import cloudinary
from PIL import Image, ImageDraw
import json
import requests
import smtplib
from sklearn.cluster import KMeans
import cv2 as cv
import numpy as np

# Configuration for the Cloudinary platform
cloudinary.config(
    cloud_name=credentials.cloud_name,
    api_key=credentials.cloud_api_key,
    api_secret=credentials.cloud_api_secret,
)


def pull_image():
    url = 'https://api.windy.com/api/webcams/v2/list/webcam=1260635090?show=webcams:image'
    headers = {'x-windy-key': credentials.api_key}

    req = requests.get(url, headers=headers)

    # Pulling URL for the latest daylight image from the Berlin - Potsdamer Platz webcam
    daylight_image = req.json(
    )['result']['webcams'][0]['image']['daylight']['preview']

    URL = daylight_image

    with urllib.request.urlopen(URL) as url:
        with open('temp.jpg', 'wb') as f:
            f.write(url.read())

    return f.name


def rgb_to_hex(tuple):
    return '#%02x%02x%02x' % (tuple)


def extract_dom_colors(img, color_count):
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
    hist, bins = np.histogram(km.labels_, bins=np.arange(0, palette + 1))
    # Convert to float to divide a float from the array
    hist = hist.astype('float64')
    # Normalize histogram to get the percentage of a color/cluster present in image
    hist /= hist.sum()

    return hist, palette, km.cluster_centers_


def create_palette(img):
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
        endY = height
        if i == 0:
            startX = 0
            startY = 0
        else:
            startX = endX
        endX = startX + percent_width
        canvas.rectangle([(startX, startY), (endX, endY)],
                         fill=color, outline=(255, 255, 255))

    result.save('palette.png')

    return hex_arr


def upload_image_cloudinary(file_name):
    uploaded_image = cloudinary.uploader.upload(file=file_name,
                                                use_filename=True,
                                                folder='/ColorsOfBerlin')

    image_url = uploaded_image['secure_url']
    public_id = uploaded_image['public_id']

    return image_url, public_id


def upload_insta(url, hex_val):
    hex_str = ' '.join(hex_val)

    post_url = 'https://graph.facebook.com/v12.0/{}/media'.format(
        credentials.ig_user_id)

    payload = {
        'image_url': url,
        'caption': datetime.today().strftime('%Y-%m-%d') + "'s daytime colors:\n" + hex_str,
        'access_token': credentials.access_token
    }

    r = requests.post(post_url, data=payload)

    result = json.loads(r.text)

    if 'id' in result:
        creation_id = result['id']

        media_publish_url = 'https://graph.facebook.com/v12.0/{}/media_publish'.format(
            credentials.ig_user_id)

        publish_payload = {
            'creation_id': creation_id,
            'access_token': credentials.access_token
        }

        r = requests.post(media_publish_url, data=publish_payload)


def delete_img_cloudinary(public_id):
    cloudinary.uploader.destroy(public_id)


def send_email(subject, body):

    FROM = credentials.gmail_email
    TO = credentials.gmail_email
    SUBJECT = subject
    TEXT = body

    # Prepare the message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (
        FROM, TO, SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(credentials.gmail_email, credentials.gmail_password)
        server.sendmail(FROM, TO, message)
        server.close()
        print('Sent Mail')
    except:
        print("Failed to send mail")


def main():
    try:
        img_file = pull_image()
        hex_val = create_palette(img_file)
        image_url, public_id = upload_image_cloudinary('palette.png')
        upload_insta(image_url, hex_val)
        delete_img_cloudinary(public_id)
        print('Success!!')

    except Exception as e:
        send_email('Colors of Berlin Failed', e)
        print(e)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
