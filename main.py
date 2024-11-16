import random, qrcode
from PIL import Image
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
from lib.QRCodeArt import DrawData, DrawStyle

controlnet = ControlNetModel.from_pretrained("yuanqiuye/qrcode_controlnet_v3")
pipeline = StableDiffusionControlNetPipeline.from_pretrained(
	"runwayml/stable-diffusion-v1-5", controlnet=controlnet
).to("cuda")
pipeline.safety_checker = None

# data, prompt, shortPrompt = ("https://www.youtube.com/watch?v=P_CSdxSGfaA", "snow pine forest", "SF") # SF
data, prompt, shortPrompt = ("https://cse.ntou.edu.tw/", "sea, waves", "SW") # SW
negative_prompt = "blurry, letter, people"
image_num = 1 # 生成的圖片個數

control_pixel_radius = 0.5
drawData = DrawData(data, qrcode.ERROR_CORRECT_M, (512, 512), 450) # 計算繪製 QRCode 的資料
control_image = drawData.getDataLayerAndRandomBg(DrawStyle.CICRLE, control_pixel_radius) # 將 QRCode 資料點加入 control image
control_image.save("control_image.png")

for i in range(image_num):
	output_image = pipeline( # 使用 sd 生成與 QRCode 相近的圖片
		image=control_image, prompt=prompt, negative_prompt=negative_prompt,
		num_inference_steps=50, guidance_scale=8
	).images[0]
	output_image = output_image.convert("RGBA") # 將生成好的圖片改為 RGBA 通道
	
	error = drawData.getErrorRate(output_image) # 計算圖片錯誤率
	
	output_image = Image.alpha_composite(output_image, drawData.getPosLayer(DrawStyle.CICRLE, 0.8)) # 額外添加圓形定位點
	output_image = Image.alpha_composite(output_image, drawData.getDataLayer(DrawStyle.CICRLE, 0.2, 0.65)) # 額外添加資料點像素
	
	output_image_name = f"{shortPrompt}_#{i}_cpr{control_pixel_radius}_pge{error[0]:.3f}_pgad{error[1]:.3f}"
	output_image.save(f"output/{output_image_name}.png")
