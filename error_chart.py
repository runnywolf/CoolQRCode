import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

for pixel_radius, curve_color in (("0", "#8f0"), ("0.2", "#0f8"), ("0.5", "#0ff"), ("1_full", "#00f")):
	a_pgad = []
	for img_name in os.listdir(f"img/radius_tests_100/cpr{pixel_radius}"): # 讀取所有圖片的 pgad
		a_pgad.append(float(img_name.rstrip(".png").split("_")[-1].lstrip("pgad")))
	
	a_pgad = [round(pgad, 2) for pgad in a_pgad] # 使分布圖的數值數目更加集中
	pgad, count = np.unique(a_pgad, return_counts=True)
	print(pgad, count)
	
	spl = make_interp_spline(pgad, count) # 使用 make_interp_spline 進行樣條插值
	x = np.linspace(min(pgad), max(pgad), 1000)
	y = spl(x)
	
	plt.plot(x, y, color=curve_color, linewidth=2, label=pixel_radius.replace("1_full", "1 (full)"))

plt.xlabel("pgad (error)")
plt.ylabel("images")
plt.legend(title="pixel radius")
plt.grid(True)
plt.show()
