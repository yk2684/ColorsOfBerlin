# ColorsOfBerlin
Finds the dominant colors of an image from the Berlin Potsdamer Platz Skyline [webcam](https://www.windy.com/-Webcams/Germany/Berlin/Skyline-Potsdamer-Platz-LIVE-Stream/webcams/1260635090?radar,52.506,13.143,11) and uploads to Instagram [@_colors.of.berlin_](https://www.instagram.com/_colors.of.berlin_/). The script runs on a daily basis from my local machine at 15:00 Berlin time. Dominant colors are extracted using the k-means clustering algorithm. The output image selects 5 dominant colors in an image which is weighted depending on the number of pixels assigned to each of the cluster/color.

## Current Setup
Currently, I am running the python script on my local device using crontab. Ideally, I would host the script on a site like Pythonanywhere, but this is a fun project in which I didn't want to spend any money on.

## Installation
### Credentials Setup
1. Set up [Windy API Key](https://api.windy.com/webcams/docs#/list/region)
2. If wanting to upload palette canvas to Instagram, create a business Instagram account and link it to a Facebook page. Then create a Facebook developer account and you will be able to obtain an access token and an business instagram user id
3. Set up [Cloudinary](https://cloudinary.com/documentation/developer_overview)

### Support Modules

Install required packages by running:
``` bash
pip install -r requirements.txt
```

### How to Run
```bash
python ColorsOfBerlin/ColorsOfBerlin/main.py
```

## Credits and Inspiration
- Idea comes from [laurendorman's Color of Berlin](https://github.com/laurendorman/color-of-berlin)