from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
import torch, os
from PIL import Image, ImageDraw

class DepthStylizer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        try:
            base = "stabilityai/stable-diffusion-xl-base-1.0"
            cn = "diffusers/controlnet-depth-sdxl-1.0"
            controlnet = ControlNetModel.from_pretrained(cn, torch_dtype=torch.float16 if self.device=="cuda" else torch.float32)
            self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
                base, controlnet=controlnet, torch_dtype=torch.float16 if self.device=="cuda" else torch.float32
            )
            self.pipe.to(self.device)
        except Exception:
            self.pipe = None

    def stylize_with_depth(self, depth_png_path: str, prompt: str, out_path: str):
        if self.pipe is None:
            img = Image.open(depth_png_path).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, img.width, 40), fill=(0,0,0))
            draw.text((10,10), "Placeholder style image", fill=(255,255,255))
            draw.text((10, img.height-20), prompt[:120], fill=(255,255,255))
            img.save(out_path)
            return out_path
        depth = load_image(depth_png_path)
        image = self.pipe(prompt=prompt, image=depth, num_inference_steps=25, guidance_scale=5.0).images[0]
        image.save(out_path)
        return out_path
