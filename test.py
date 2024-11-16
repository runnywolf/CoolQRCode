import random, qrcode
from PIL import Image
from lib.QRCodeArt import DrawData, DrawStyle

def mergeLayer(img_back: Image.Image, img_fore: Image.Image) -> Image.Image:
  return Image.alpha_composite(img_back, img_fore)

img = Image.open("img/night.png").convert("RGBA")
drawData = DrawData("https://www.youtube.com/@bluenight1022", qrcode.ERROR_CORRECT_M, img.size, img.size[0]) # 計算繪製 QRCode 的資料
img = mergeLayer(img, drawData.getPosLayer(DrawStyle.CICRLE, 1))
img = mergeLayer(img, drawData.getDataLayer(DrawStyle.CICRLE, 0.18, 0.66))
img.save("output/test.png")
