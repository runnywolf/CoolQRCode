import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

def get_image_pack_pgad_pd(folder_path: str) -> tuple[np.ndarray, np.ndarray]:
	a_pgad = []
	for img_name in os.listdir(folder_path): # 讀取所有圖片的 pgad
		a_pgad.append(float(img_name.rstrip(".png").split("_")[-1].lstrip("pgad")))
	image_num = len(a_pgad)
	
	a_pgad = [round(pgad, 2) for pgad in a_pgad] # 使分布圖的數值數目更加集中
	pgad, count = np.unique(a_pgad, return_counts=True)
	count = count / image_num # 求機率
	
	spl = make_interp_spline(pgad, count) # 使用 make_interp_spline 進行樣條插值
	x = np.linspace(min(pgad), max(pgad), 1000) # 解析度為 1000
	y = spl(x)
	
	return (x, y)
# 分析一個圖片包內所有圖片的檔名, 將所有圖片的 pgad 轉為機率分布曲線

def draw_chart(title: str, legend_name: str) -> None:
	plt.title(title) # 標題
	plt.xlabel("pgad (error)") # x 軸標籤
	plt.ylabel("probability") # y 軸標籤
	plt.xlim(0, 0.6) # x 軸範圍
	plt.ylim(0, 0.5) # y 軸範圍
	plt.legend(title=legend_name, loc="upper left") # 圖例名稱 & 圖例位置
	plt.grid(True) # 顯示網格
	plt.show() # 顯示圖表
# 繪製圖表

def pixel_radius_chart() -> None:
	for pixel_radius, curve_color in [("0", "#8f0"), ("0.2", "#0f8"), ("0.5", "#0ff"), ("0.7", "#08f"), ("1_full", "#f0f")]:
		x, y = get_image_pack_pgad_pd(f"img/test_radius/cpr{pixel_radius}")
		plt.plot(x, y, color=curve_color, linewidth=2, label=pixel_radius.replace("1_full", "1 (full)"))
	
	draw_chart("Control image - pixel radius", "pixel radius")
# control image 點半徑與錯誤率分布的關係

def qr_module_width_chart() -> None:
	for module_width, curve_color in [("25", "#8f0")]:
		x, y = get_image_pack_pgad_pd(f"img/test_qr-module-width/mw{module_width}")
		plt.plot(x, y, color=curve_color, linewidth=2, label=module_width)
	
	draw_chart("Control image - QRCode module width", "module width")
# control image 的 QRCode 複雜度與錯誤率分布的關係

pixel_radius_chart()
qr_module_width_chart()
