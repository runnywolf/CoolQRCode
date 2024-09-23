from enum import Enum
import numpy as np
from PIL import Image, ImageDraw
import qrcode
from lib.Tool import Vector2, inRange
import random

class DrawStyle(Enum): # QRCode 的定位點樣式
	SQUARE = 1
	CICRLE = 2

class DrawData: # 計算繪製參數
	SMOOTH_RATE = 4 # 保持像素平滑, 將圖層放大後再縮小
	
	def __init__(self, data: str, correct_level: int, size: tuple[int, int], qrcode_width: int) -> None:
		self.v2_output_size = Vector2.fromTuple(size) # 原始圖片的大小
		self.v2_qr_draw_size = Vector2(qrcode_width, qrcode_width) # QRCode 繪製範圍
		self.v2_qr_draw_pos = self.v2_output_size / 2 - self.v2_qr_draw_size / 2 # QRCode 的繪製座標
		self.qr_arr = _getQRCodeArr(data, correct_level) # 生成 白為0 黑為1 的 QRCode 像素點矩陣
		self.qr_pixel_width = qrcode_width / len(self.qr_arr) # 每個 QRCode 像素的實際邊長
	# 建構子
	
	def getPosLayer(self, draw_style: DrawStyle) -> Image.Image:
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		v2_img_size = self.v2_output_size * self.SMOOTH_RATE
		img = Image.new("RGBA", v2_img_size.tup(), (0, 0, 0, 0)) # 透明圖層, 用於繪製定位點
		imgDraw = ImageDraw.Draw(img) # 繪圖用
		
		if draw_style == DrawStyle.SQUARE: # 繪製方形大定位點
			for i in range(qr_w_pixels):
				for j in range(qr_w_pixels):
					if not self._isPosArea(Vector2(i, j)): continue
					v2_draw_pos = (self.v2_qr_draw_pos + Vector2(i + 0.5, j + 0.5) * self.qr_pixel_width) * self.SMOOTH_RATE
					pos_radius = (self.qr_pixel_width / 2) * self.SMOOTH_RATE
					pixel_color = "000" if self.qr_arr[j][i] else "fff" # QRCode 像素點是黑色還是白色
					_drawColorRect(imgDraw, v2_draw_pos, pos_radius, pixel_color) # 繪製定位點
		elif draw_style == DrawStyle.CICRLE: # 繪製圓形大定位點
			for pos in ((4.5, 4.5), (4.5, qr_w_pixels-4.5), (qr_w_pixels-4.5, 4.5)): # 繪製三個圓形的大定位點
				for pixel_radius, color_code in ((4.5, "fff"), (3.5, "000"), (2.5, "fff"), (1.5, "000")): # 每個大定位點都有黑白相間的圓
					v2_draw_pos = (self.v2_qr_draw_pos + Vector2.fromTuple(pos) * self.qr_pixel_width) * self.SMOOTH_RATE
					pos_radius = self.qr_pixel_width * pixel_radius * self.SMOOTH_RATE
					_drawColorDot(imgDraw, v2_draw_pos, pos_radius, color_code)
			
			for pixel_radius, color_code in ((2.5, "000"), (1.5, "fff"), (0.5, "000")): # 繪製右下角的小定位點
				v2_draw_pos = (self.v2_qr_draw_pos + Vector2(qr_w_pixels-7.5, qr_w_pixels-7.5) * self.qr_pixel_width) * self.SMOOTH_RATE
				pos_radius = self.qr_pixel_width * pixel_radius * self.SMOOTH_RATE
				_drawColorDot(imgDraw, v2_draw_pos, pos_radius, color_code)
		
		return img.resize(self.v2_output_size.tup())
	# 生成定位點圖層
	
	def getDataLayer(self, draw_style: DrawStyle, pixel_radius_scale: float, alpha_code: str = "f") -> Image.Image:
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		v2_img_size = self.v2_output_size * self.SMOOTH_RATE
		img = Image.new("RGBA", v2_img_size.tup(), (0, 0, 0, 0)) # 透明圖層, 用於繪製定位點
		imgDraw = ImageDraw.Draw(img) # 繪圖用
		
		for i in range(qr_w_pixels):
			for j in range(qr_w_pixels):
				if not self._isDataArea(Vector2(i, j)): continue
				
				v2_draw_pos = (self.v2_qr_draw_pos + Vector2(i + 0.5, j + 0.5) * self.qr_pixel_width) * self.SMOOTH_RATE
				pixel_radius = (self.qr_pixel_width / 2) * pixel_radius_scale * self.SMOOTH_RATE
				pixel_color = ("000" if self.qr_arr[j][i] else "fff") + alpha_code # QRCode 像素點是黑色還是白色
				if draw_style == DrawStyle.CICRLE:
					_drawColorDot(imgDraw, v2_draw_pos, pixel_radius, pixel_color) # 繪製定位點
				elif draw_style == DrawStyle.SQUARE:
					_drawColorRect(imgDraw, v2_draw_pos, pixel_radius, pixel_color) # 繪製定位點
		
		return img.resize(self.v2_output_size.tup())
	# 生成資料點圖層
	
	def getDataLayerAndRandomBg(self, draw_style: DrawStyle, pixel_radius_scale: float) -> Image.Image:
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		v2_img_size = self.v2_output_size * self.SMOOTH_RATE
		img = Image.new("RGBA", v2_img_size.tup(), (0, 0, 0, 0)) # 透明圖層, 用於繪製定位點
		imgDraw = ImageDraw.Draw(img) # 繪圖用
		
		expand_range = (self.v2_output_size - self.v2_qr_draw_size) / 2 / self.qr_pixel_width
		expand_pixels = (int(expand_range.x) + 2, int(expand_range.y) + 2)
		for i in range(-expand_pixels[0], qr_w_pixels + expand_pixels[0]):
			for j in range(-expand_pixels[1], qr_w_pixels + expand_pixels[1]):
				v2_draw_pos = (self.v2_qr_draw_pos + Vector2(i + 0.5, j + 0.5) * self.qr_pixel_width) * self.SMOOTH_RATE
				pixel_radius = (self.qr_pixel_width / 2) * pixel_radius_scale * self.SMOOTH_RATE
				
				if self._isDataArea(Vector2(i, j)):
					pixel_color = "000" if self.qr_arr[j][i] else "fff" # QRCode 像素點是黑色還是白色
				else:
					pixel_color = "000" if random.randint(0, 1) else "fff" # 將非資料區像素隨機塗黑或白
				
				if draw_style == DrawStyle.CICRLE:
					_drawColorDot(imgDraw, v2_draw_pos, pixel_radius, pixel_color) # 繪製定位點
				elif draw_style == DrawStyle.SQUARE:
					_drawColorRect(imgDraw, v2_draw_pos, pixel_radius, pixel_color) # 繪製定位點
		
		return img.resize(self.v2_output_size.tup())
	# 生成資料點圖層, 若非資料區域則隨機塗色
	
	def getErrorRate(self, img_sd_output: Image.Image) -> tuple[float, float]:
		if img_sd_output.size != self.v2_output_size.tup():
			print("[Warning][QRCodeArt.DrawData.getErrorRate] Image size is not same.")
			return 0
		
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		pixel_num = 0
		pixel_data = [0, 0] # 資料點的錯誤情形
		
		for i in range(qr_w_pixels):
			for j in range(qr_w_pixels):
				if not self._isDataArea(Vector2(i, j)): continue
				
				v2_draw_pos = (self.v2_qr_draw_pos + Vector2(i + 0.5, j + 0.5) * self.qr_pixel_width) # 像素點座標
				pixel_color = img_sd_output.getpixel(v2_draw_pos.tup()) # 像素點顏色
				pixel_color_grayscale = (pixel_color[0] * 0.299 + pixel_color[1] * 0.587 + pixel_color[2] * 0.114) / 255 # 像素點灰階值, 0黑 1白
				control_image_pixel_grayscale = 1 - self.qr_arr[j][i] # control net image 像素點灰階值, 0黑 1白
				
				pixel_num += 1 # 統計的資料點個數
				if (pixel_color_grayscale >= 0.5) != (control_image_pixel_grayscale == 1): pixel_data[0] += 1 # 資料點明暗錯誤率
				pixel_data[1] += abs(pixel_color_grayscale - control_image_pixel_grayscale) # 資料點明暗差異平均
		
		pixel_grayscale_error = pixel_data[0] / pixel_num # 資料點明暗錯誤率
		pixel_grayscale_avg_diff = pixel_data[1] / pixel_num # 資料點明暗差異平均
		
		return (pixel_grayscale_error, pixel_grayscale_avg_diff)
	# 生成圖片與 control image 比較的錯誤率
	
	def _isPosArea(self, v2: Vector2) -> bool:
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		if v2.x < 9 and v2.y < 9: return True # 左上定位點
		if v2.x >= qr_w_pixels-9 and v2.y < 9: return True # 右上定位點
		if v2.x < 9 and v2.y >= qr_w_pixels-9: return True # 左下定位點
		if inRange(v2.x, qr_w_pixels-10, qr_w_pixels-6) and inRange(v2.y, qr_w_pixels-10, qr_w_pixels-6): return True # 右下小定位點
		return False
	# 座標是否在定位點區域
	
	def _isDataArea(self, v2: Vector2) -> bool:
		qr_w_pixels = len(self.qr_arr) # QRCode 的像素邊長 (px)
		
		if self._isPosArea(v2): return False # 如果座標位於定位點區域, 那絕對不是資料區域
		if inRange(v2.x, 1, qr_w_pixels-2) and inRange(v2.y, 1, qr_w_pixels-2): return True # QRCode 周圍一圈白色像素並非資料區域
		return False
	# 座標是否在資料區域

def _getQRCodeArr(data: str, correct_level: int) -> list[list[int]]:
	qr = qrcode.QRCode(error_correction=correct_level, box_size=1, border=1) # 設定 QRCode 參數
	qr.add_data(data) # 放入資料
	qr.make(fit=True) # 計算 QRCode
	PILimg_QRCode = qr.make_image(fill_color="#000", back_color="#fff") # 生成 QRCode 圖片
	PILimg_QRCode.save("QRCode.png")
	NParr_QRCodeImg = np.array(PILimg_QRCode) # 圖片轉 np 陣列
	return [[0 if j[0] == 255 else 1 for j in i] for i in NParr_QRCodeImg] # 生成 白為0 黑為1 的矩陣
# 生成 白為0 黑為1 的 QRCode 矩陣, 容錯率依序為L/M/Q/H

def _drawColorDot(draw: ImageDraw, pos: Vector2, radius: float, color_code: str) -> None:
	point1 = (pos.x - radius, pos.y - radius)
	point2 = (pos.x + radius, pos.y + radius)
	draw.ellipse([point1, point2], fill="#%s"%color_code)
# 繪製色點

def _drawColorRect(draw: ImageDraw, pos: Vector2, radius: float, colorCode: str) -> None:
	point1 = (pos.x - radius, pos.y - radius)
	point2 = (pos.x + radius, pos.y + radius)
	draw.rectangle([point1, point2], fill="#"+colorCode)
# 繪製色點
