import os
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
import re

def find_files(root_dir, endwith=".png"):
    pdf_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(endwith):
                full_path = os.path.join(dirpath, filename)
                pdf_files.append(full_path)
    return pdf_files


def add_layer_info(img_path, save_path, layer_num):# 打开图片
    img = Image.open(img_path).convert("RGBA")  # 也可以用其他方式得到的Image对象

    # 创建一个可绘制对象
    draw = ImageDraw.Draw(img)

    # 设置文字
    text = f"layer: {layer_num}"

    font = font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

    # 使用textbbox获取文字边界框，返回值是(left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img_width, img_height = img.size
    x = img_width - text_width - 8
    y = img_height - text_height - 8

    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    # 保存图片
    img.save(save_path)



if __name__ == "__main__":
    after_fix = "adjust_private"  # adjust2
    base_dir = "/home/why/why/paper/mod_dataset/ct2report/private/"
    img_paths = find_files(base_dir)
    img_paths = [i for i in img_paths if after_fix in i]
    print(f"totally {len(img_paths)} imgs")
    for i in tqdm(img_paths):
        img_name = i.split("/")[-1]
        layer_num = int(re.findall(r'\d+', img_name)[0])
        # print(layer_num, "num")
        img_dir = i.replace(img_name, "")
        save_dir = img_dir.replace(after_fix, "layer")
        save_path = os.path.join(save_dir, img_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        #if not os.path.exists(save_path):
        add_layer_info(i, save_path, layer_num)
