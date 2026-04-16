import os.path
from collections import defaultdict
import pdfplumber


def pdf_to_text_pdfplumber(pdf_path, output_txt_path=None):
    """
    使用pdfplumber提取PDF中的文字
    """
    all_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # 提取当前页文字
            text = page.extract_text()
            if text:
                all_text += f"--- 第 {page_num} 页 ---\n{text}\n\n"
            else:
                all_text += f"--- 第 {page_num} 页 (无文字内容) ---\n\n"

    # 如果指定了输出文件，则保存到文件
    if output_txt_path:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(all_text)
        # print(f"文字已保存到: {output_txt_path}")

    return all_text


def find_pdf_files(root_dir, endwith=".pdf"):
    pdf_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(endwith):
                full_path = os.path.join(dirpath, filename)
                pdf_files.append(full_path)
    return pdf_files


def stat_report(txt_path_list):
    standards = ["扫描完整", "未检测到金属伪影", "检测到疑似呼吸运动伪影", "剂量噪声检查合格"]
    stat = defaultdict(lambda : [0, 0])
    for txt_path in txt_path_list:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        for n, s in enumerate(standards):
            if n==0:
                if s in content:
                    stat["完整性扫描检查pos-neg"][0] += 1
                else:
                    stat["完整性扫描检查pos-neg"][1] += 1
                    # print(txt_path)

            elif n==1:
                if s in content:
                    stat["金属异物/伪影检查pos-neg"][0] += 1
                else:
                    stat["金属异物/伪影检查pos-neg"][1] += 1

            elif n==2:
                if s in content:
                    stat["呼吸运动伪影检查pos-neg"][1] += 1
                else:
                    stat["呼吸运动伪影检查pos-neg"][0] += 1
                    # print(txt_path)

            elif n==3:
                if s in content:
                    stat["剂量噪声检查pos-neg"][0] += 1
                else:
                    stat["剂量噪声检查pos-neg"][1] += 1

    print(stat)



# 使用示例
data_base = "/home/why/why/paper/mod_dataset/ct2report/private/"
pdf_list = find_pdf_files(data_base)
txt_list = [i.replace(".pdf", ".txt") for i in pdf_list]

for p in pdf_list:
    output_file = p.replace(".pdf", ".txt")
    if not os.path.exists(output_file):
        text_content = pdf_to_text_pdfplumber(p, output_file)

# stat_report(txt_list)

# data_base = "/home/why/why/paper/mod_dataset/ct2report/test&val/"
# pdf_list = find_pdf_files(data_base)
# pdf_list = [i.replace("test&val", "train") for i in pdf_list]
# data_base2 = "/home/why/why/paper/mod_dataset/ct2report/train/"
# pdf_list2 = find_pdf_files(data_base2)

print(len(pdf_list), len(pdf_list2), len(pdf_list)+len(pdf_list2), len(list(set(pdf_list2+pdf_list))))

