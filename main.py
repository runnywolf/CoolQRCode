import random, qrcode
from PIL import Image
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
from lib.QRCodeArt import DrawData, DrawStyle

controlnet = ControlNetModel.from_pretrained("yuanqiuye/qrcode_controlnet_v3")
pipeline = StableDiffusionControlNetPipeline.from_pretrained(
	"runwayml/stable-diffusion-v1-5", controlnet=controlnet
).to("cuda")

random_data = "".join(chr(random.randint(32, 126)) for _ in range(50)) # 隨機字串, 用於生成 QRCode
random_data = "https://www.youtube.com/@bluenight1022"
drawData = DrawData(random_data, qrcode.ERROR_CORRECT_M, (512, 512), 450) # 計算繪製 QRCode 的資料
control_image = Image.new('RGBA', (512, 512), (255, 255, 255, 255)) # 灰色背景
control_image = Image.alpha_composite(control_image, drawData.getDataLayerAndRandomBg(DrawStyle.SQUARE, 1)) # 將 QRCode 資料點加入 control image
control_image.save("control_image.png")

prompt = "snow pine forest with lot of leaves"
negative_prompt = "blurry, letter"
image_num = 10 # 生成的圖片個數

for i in range(image_num):
	output_image = pipeline( # 使用 sd 生成與 QRCode 相近的圖片
		image=control_image, prompt=prompt, negative_prompt=negative_prompt,
		num_inference_steps=50, guidance_scale=8
	).images[0]
	output_image = output_image.convert("RGBA") # 將生成好的圖片改為 RGBA 通道
	
	output_image = Image.alpha_composite(output_image, drawData.getPosLayer(DrawStyle.CICRLE))
	output_image = Image.alpha_composite(output_image, drawData.getDataLayer(DrawStyle.CICRLE, 0.2, "a"))
	
	output_image.save("output/output_%s.png"%i)
