import os
import shutil
import subprocess

def convert_images_to_mp4(folder, output_dir, video_name, framerate=2):
    """
    将多个文件夹中的图片转换成mp4视频。

    :param folders: 文件夹路径列表，每个文件夹中包含图片
    :param output_dir: 输出视频保存的文件夹
    :param framerate: 视频帧率
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 确保路径存在
    if  os.path.exists(folder):
        output_path = os.path.join(output_dir, video_name + ".mp4")

        # 假设图片格式统一为jpg，并且命名格式类似img001.jpg,img002.jpg...
        input_pattern = os.path.join(folder, "slice_%03d.png")

        # ffmpeg命令，-y表示覆盖同名文件
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(framerate),
            "-i", input_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]

        print(f"转换文件夹 {folder} 中的图片到 {output_path}")
        try:
            subprocess.run(cmd, check=True)
            print("转换成功。")
        except subprocess.CalledProcessError:
            print(f"转换失败：{folder}")

    else:
        print(f"文件夹不存在：{folder}，跳过。")


def find_files(root_dir, endwith=".pdf"):
    pdf_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(endwith):
                full_path = os.path.join(dirpath, filename)
                pdf_files.append(full_path)
    return pdf_files


if __name__ == "__main__":
    base_dir = "/home/why/why/paper/mod_dataset/ct2report/private/"
    pdf_report_paths = find_files(base_dir)
    dir_tail = "_rgb_layer"
    rbg_img_dirs = [i.replace(".pdf", dir_tail) for i in pdf_report_paths]
    rbg_img_dirs = [i for i in rbg_img_dirs if os.path.exists(i)]
    output_directory = os.path.join(base_dir, "videos")
    private_output_directory = os.path.join(base_dir, "videos_private_test")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_report = os.path.join(base_dir, "reports")
    if not os.path.exists(output_report):
        os.makedirs(output_report)

    for i in rbg_img_dirs:
        video_name = i.replace("/home/why/why/paper/mod_dataset/ct2report/", "").replace("/", "--").replace(dir_tail, "")
        report_name = video_name+".txt"
        report_source = i.replace(dir_tail, ".txt")
        if not os.path.exists(os.path.join(output_report, report_name)):
            shutil.copy(report_source, os.path.join(output_report, report_name))
        print(i)
        if not os.path.exists(os.path.join(output_directory, video_name+".mp4")):
            convert_images_to_mp4(i, private_output_directory, video_name=video_name)
