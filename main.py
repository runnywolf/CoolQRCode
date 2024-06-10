import numpy as np
import qrcode
from PIL import Image, ImageDraw

def inRange(value: float, start: float, end: float) -> bool: # value 是否介於 start 和 end 之間
	return value >= start and value <= end 

def tupleAdd(t1: tuple[float, float], t2: tuple[float, float]) -> tuple[float, float]: # 將兩個 tuple[float, float] 相加
	return (t1[0]+t2[0], t1[1]+t2[1])

def tupleMulti(t: tuple[float, float], value: float): # 將 tuple[float, float] 每個分量都乘上常數 value
	return (t[0]*value, t[1]*value)

def getQRCodeArr(s_data: str, level: int) -> list[list[int]]: # 生成 QRCode 矩陣
	qr = qrcode.QRCode(error_correction=level, box_size=1, border=1) # 設定 QRCode 參數
	qr.add_data(s_data) # 放入資料
	qr.make(fit=True) # 計算 QRCode
	PILimg_QRCode = qr.make_image(fill_color="#000", back_color="#fff") # 生成 QRCode 圖片
	PILimg_QRCode.save("QRCode.png")
	NParr_QRCodeImg = np.array(PILimg_QRCode) # 圖片轉 np 陣列
	return [[0 if j[0] == 255 else 1 for j in i] for i in NParr_QRCodeImg] # 生成 白為0 黑為1 的矩陣

def drawColorDot(draw: ImageDraw, pos: tuple[float, float], radius: float, colorCode: str) -> None: # 繪製色點
	point1 = (pos[0]-radius, pos[1]-radius)
	point2 = (pos[0]+radius, pos[1]+radius)
	draw.ellipse([point1, point2], fill="#"+colorCode)

def drawColorRect(draw: ImageDraw, pos: tuple[float, float], radius: float, colorCode: str) -> None: # 繪製色點
	point1 = (pos[0]-radius, pos[1]-radius)
	point2 = (pos[0]+radius, pos[1]+radius)
	draw.rectangle([point1, point2], fill="#"+colorCode)

def insertQRCodeToImg(inputImageUrl: str, outputImageUrl: str, s_data: str, correctLevel: int, radiusRate: float = 1) -> None: # 將字串轉為 QRCode 後
	img_input = Image.open(inputImageUrl) # 讀取圖片
	imageOriginalSize = img_input.size
	img_input = img_input.resize((2048, 2048), Image.LANCZOS) # 等比例放大圖片
	
	a_QRCode = getQRCodeArr(s_data, correctLevel)
	QRCodeWidth = len(a_QRCode)
	pixelWidth = img_input.size[0] / QRCodeWidth
	
	draw = ImageDraw.Draw(img_input)
	for i in range(QRCodeWidth):
		for j in range(QRCodeWidth):
			color = "000" if a_QRCode[j][i] else "fff"
			if inRange(i, 1, QRCodeWidth-2) and inRange(j, 1, QRCodeWidth-2):
				drawColorDot(draw, tupleMulti((0.5+i, 0.5+j), pixelWidth), pixelWidth/2 * radiusRate, color)
			
			if (i < 9 and j < 9) or (i >= QRCodeWidth-9 and j < 9) or (i < 9 and j >= QRCodeWidth-9) or\
				 (inRange(i, QRCodeWidth-10, QRCodeWidth-6) and inRange(j, QRCodeWidth-10, QRCodeWidth-6)):
				drawColorRect(draw, tupleMulti((0.5+i, 0.5+j), pixelWidth), pixelWidth/2, color)
	
	img_input = img_input.resize(imageOriginalSize, Image.LANCZOS) # 等比例縮小圖片
	img_input.save(outputImageUrl)

#url = "https://www.youtube.com/@ShishiroBotan"
url = "https://www.youtube.com/@bluenight1022"
insertQRCodeToImg("night.png", "output.png", url, qrcode.ERROR_CORRECT_M, 0.13)
