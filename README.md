# ColorsOfBerlin
Finds the dominant colors of an image from the Berlin West Skyline [webcam](https://www.windy.com/-Webcams/Germany/Berlin/webcams/1641364745?radar,52.477,13.116,11) and uploads to Instagram [@_colors.of.berlin_](https://www.instagram.com/_colors.of.berlin_/). The script runs automatically using Github Actions at 13:00 Berlin time. Dominant colors are extracted using the k-means clustering algorithm. The sky is detected from the image assuming that the variance of sky is smaller than non-sky part. Then 5 dominant colors are selected from the output image without the non-sky elements which is weighted depending on the number of pixels assigned to each of the cluster/color.

## Current Setup
The python script runs automatically using Github Actions.

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
python ./ColorsOfBerlin/main.py
```

## Credits and Inspiration
- Idea comes from [laurendorman's Color of Berlin](https://github.com/laurendorman/color-of-berlin)
- The Sky detector script is from [sky-detector](https://github.com/cftang0827/sky-detector)
