"""
ColorsOfBerlin python script.

Yukino Kondo
"""

import credentials
import math
import urllib.request
from datetime import datetime
import cloudinary.uploader
import cloudinary
from colorthief import ColorThief
from PIL import Image, ImageDraw
import json
import requests
import smtplib

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


def create_palette(img):
    # Using the color thief package, get dominant colors from an image
    color_thief = ColorThief(img)
    palette = color_thief.get_palette(color_count=5)

    # Preparing canvas
    size = 200
    columns = len(palette)
    width = int(columns * size)
    height = int(columns * size)
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    canvas = ImageDraw.Draw(result)

    hex_arr = []

    # Drawing on canvas
    for i, color in enumerate(palette):
        hex_arr.append(rgb_to_hex(color))
        x = int((i % columns) * size)
        y = int(math.floor(i / columns) * size)
        canvas.rectangle([(x, y), (x + size - 1, height)],
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
        send_email('Colors of Berlin Failed', 'Go check on it')
        print(e)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
