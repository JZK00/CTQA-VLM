import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm
from PIL import Image

def load_nii(file_path):
    img = nib.load(file_path)
    return img.get_fdata().astype(np.float32)

def compute_percentile_range(arr, low_percentile=0.5, high_percentile=99.5):
    a = np.asarray(arr, dtype=np.float32)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return 0.0, 1.0
    vmin = np.percentile(a, low_percentile)
    vmax = np.percentile(a, high_percentile)
    if not np.isfinite(vmin):
        vmin = float(np.min(a))
    if not np.isfinite(vmax):
        vmax = float(np.max(a))
    if vmax <= vmin:
        vmax = vmin + 1.0
    return float(vmin), float(vmax)

def window_to_min_max(window_level, window_width):
    half = float(window_width) / 2.0
    vmin = float(window_level) - half
    vmax = float(window_level) + half
    if vmax <= vmin:
        vmax = vmin + 1.0
    return vmin, vmax

def normalize(data, vmin, vmax):
    d = np.clip(data, vmin, vmax)
    scale = vmax - vmin
    if scale <= 1e-6:
        return np.zeros_like(d, dtype=np.float32)
    return (d - vmin) / scale

def convert_to_rgb_image(slice_data, vmin, vmax):
    norm = normalize(slice_data.astype(np.float32), vmin=vmin, vmax=vmax)
    rgb = plt.cm.gray(norm)[:, :, :3]
    return rgb

def visualize_slice(data, slice_index, axis=2, vmin=None, vmax=None):
    if data.ndim != 3:
        raise ValueError("Only 3D data is supported.")
    if axis == 0:
        sl = data[slice_index, :, :]
    elif axis == 1:
        sl = data[:, slice_index, :]
    else:
        sl = data[:, :, slice_index]
    if vmin is None or vmax is None:
        vmin, vmax = compute_percentile_range(sl, 0.5, 99.5)
    rgb = convert_to_rgb_image(sl, vmin=vmin, vmax=vmax)
    plt.imshow(rgb)
    plt.axis('off')
    plt.show()

def save_slices_as_images(
    data,
    save_dir,
    axis=2,
    mode="window",            # "window" 或 "percentile"
    window_level=-600,        # 肺窗默认
    window_width=1500,
    low_percentile=0.5,
    high_percentile=99.5,
    use_global=True           # True: 全局固定范围；False: 每片单独范围
):
    if data.ndim != 3:
        raise ValueError("Only 3D data is supported.")
    os.makedirs(save_dir, exist_ok=True)

    # 计算全局 vmin/vmax（如果需要）
    if use_global:
        if mode == "window":
            vmin_global, vmax_global = window_to_min_max(window_level, window_width)
        elif mode == "percentile":
            vmin_global, vmax_global = compute_percentile_range(data, low_percentile, high_percentile)
        else:
            raise ValueError("mode must be 'window' or 'percentile'")
    else:
        vmin_global = vmax_global = None

    num_slices = data.shape[axis]
    for i in range(num_slices):
        if axis == 0:
            sl = data[i, :, :]
        elif axis == 1:
            sl = data[:, i, :]
        else:
            sl = data[:, :, i]

        if use_global:
            vmin, vmax = vmin_global, vmax_global
        else:
            if mode == "window":
                vmin, vmax = window_to_min_max(window_level, window_width)
            else:
                vmin, vmax = compute_percentile_range(sl, low_percentile, high_percentile)

        rgb = convert_to_rgb_image(sl, vmin=vmin, vmax=vmax)

        # numpy array 转成 PIL Image，先乘255转成 uint8格式
        img = Image.fromarray((rgb * 255).astype(np.uint8))

        # 用 PIL Image 的 resize 方法
        img = img.resize((256, 256), resample=Image.Resampling.LANCZOS)

        # 保存文件
        img.save(os.path.join(save_dir, f"slice_{i:03d}.png"))


def start_convert(
    nii_file_path,
    output_directory,
    axis=2,
    mode="window",            # "window" 或 "percentile"
    window_level=-600,        # 肺窗
    window_width=1500,
    low_percentile=0.5,
    high_percentile=99.5,
    use_global=True
):
    data = load_nii(nii_file_path)
    save_slices_as_images(
        data=data,
        save_dir=output_directory,
        axis=axis,
        mode=mode,
        window_level=window_level,
        window_width=window_width,
        low_percentile=low_percentile,
        high_percentile=high_percentile,
        use_global=use_global
    )


def find_nii_files(root_dir):
    nii_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.nii'):
                full_path = os.path.join(dirpath, filename)
                nii_files.append(full_path)
    return nii_files



base_dir = '/home/why/why/paper/mod_dataset/ct2report/private'
nii_file_list = find_nii_files(base_dir)
for n in tqdm(nii_file_list):
    input_file = n
    output_file = input_file.replace(".nii", "_rgb_adjust2")
    output_file_test_private = input_file.replace(".nii", "_rgb_adjust_private")
    print(f"wprkiong on: {output_file}")
    if os.path.exists(output_file):
        print("ignore")
    else:
        start_convert(
            input_file,
            output_file_test_private,
            mode="percentile",
            low_percentile=1.7,
            high_percentile=98.3,
            use_global=True)

# start_convert("/home/why/why/paper/mod_dataset/ct2report/train/CT_COVID19/dcm_CT_Images_In_COVID19-Part1/05/volume-covid19-A-0111.nii",
#               "/home/why/why/paper/mod_dataset/ct2report/train/CT_COVID19/dcm_CT_Images_In_COVID19-Part1/05/volume-covid19-A-0111_vnorm_rgb",
#               mode="percentile",
#               low_percentile=0.5,
#               high_percentile=99.5,
#               use_global=True)
