import qrcode
from PIL import Image
from lib.QRCodeArt import DrawData, DrawStyle

def makeCoolQRCode(
	qr_data: str = "https://www.youtube.com/watch?v=XZ29NGaFFMA",
	qr_correct_level: qrcode.constants = qrcode.ERROR_CORRECT_M,
	qr_width_scale: float = 0.9,
	qr_pos_style: DrawStyle = DrawStyle.CICRLE,
	qr_pos_alpha: float = 0.8,
	qr_module_style: DrawStyle = DrawStyle.CICRLE,
	qr_module_radius: float = 0.2,
	qr_module_alpha: float = 0.65,
	img_size: tuple[int, int] = (512, 512),
	img_number: int = 1,
	output_img_prefix: str = "",
	control_pixel_radius: float = 0.5,
	sd_positive_prompt: str = "snow pine forest",
	sd_negative_prompt: str = "blurry, letter, people",
	sd_steps: int = 50,
	sd_cfg_scale: float = 8.0
) -> None:
	from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
	controlnet = ControlNetModel.from_pretrained("yuanqiuye/qrcode_controlnet_v3")
	pipeline = StableDiffusionControlNetPipeline.from_pretrained(
		"runwayml/stable-diffusion-v1-5", controlnet=controlnet
	).to("cuda")
	
	qr_width = min(img_size) * qr_width_scale # 計算 qrcode 邊長
	drawData = DrawData(qr_data, qr_correct_level, img_size, qr_width) # 計算繪製 QRCode 的資料
	control_image = drawData.getDataLayerAndRandomBg(DrawStyle.CICRLE, control_pixel_radius) # 將 QRCode 資料點加入 control image
	control_image.save("control_image.png") # 保存 control image
	
	for i in range(img_number):
		img = pipeline( # 使用 sd 生成與 QRCode 相近的圖片
			image=control_image, prompt=sd_positive_prompt, negative_prompt=sd_negative_prompt,
			num_inference_steps=sd_steps, guidance_scale=sd_cfg_scale
		).images[0]
		
		img = img.convert("RGBA") # 將生成好的圖片改為 RGBA 通道
		error = drawData.getErrorRate(img) # 計算圖片錯誤率
		
		img = Image.alpha_composite(img, drawData.getPosLayer(qr_pos_style, qr_pos_alpha)) # 額外添加圓形定位點
		img = Image.alpha_composite(img, drawData.getDataLayer(qr_module_style, qr_module_radius, qr_module_alpha)) # 額外添加資料點像素
		
		img_name = f"#{i}_cpr{control_pixel_radius}_pgad{error[1]:.3f}"
		if output_img_prefix != "": img_name = f"{output_img_prefix}_{img_name}"
		img.save(f"output/{img_name}.png")

makeCoolQRCode()
