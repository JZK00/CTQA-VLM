import json
import os.path
import shutil
import re
import random
from collections import defaultdict


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
    target = "reports"
    stage = 2
    data_list = []

    if stage == 2:
        user_prompt = """
你是一个医疗图像质量检测专家，你能从 a.完整性扫描检查，b.金属异物/伪影检查，c.呼吸运动伪影检查 d.剂量噪声检查 4个方面评判一份ct视频数据是否存在质量异常。
现在仔细观察这个ct<video>，先判断是否存在质量异常，再重点观察异常出现的层(layer)!!!，输出详细的诊断报告，格式如下：

一、完整性检查
检测结果：扫描完整/不完整，具体哪一侧不完整
二、金属异物/伪影检查
检测结果：未检测到金属伪影/检测到疑似金属伪影，具体出现在ct哪些layer(重点!!!)
三、呼吸运动伪影检查
检测结果：未检测到呼吸运动伪影/检测到疑似呼吸运动伪影，具体出现在ct哪些layer(重点!!!)
四、剂量噪声检查
检测结果：剂量噪声检查是否合格
"""
    elif stage == 1:
        user_prompt = """
你是一个医疗图像专家，仔细观察这个ct视频<video>, 从 a.完整性扫描检查，b.金属异物/伪影检查，c.呼吸运动伪影检查，d.剂量噪声检查 4个方面评判并输出如下格式报告：

一、完整性扫描检查
检测结果：(扫描是否完整)
二、金属异物/伪影检查
检测结果：(是否有检测到疑似金属伪影)
三、呼吸运动伪影检查
检测结果：(是否有检测到疑似呼吸运动伪影)
四、剂量噪声检查
检测结果：剂量噪声检查是否合格
"""

    tar_path = os.path.join(base_dir, target)
    target_paths = os.listdir(tar_path)
    random.shuffle(target_paths)  # 随机打乱
    for r in target_paths:
        report_path = os.path.join(tar_path, r)
        video_path = report_path.replace(".txt", ".mp4").replace("reports", "videos")
        if os.path.exists(video_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            # print(report_path)
            # results = re.findall(r'检测结果：(.*)', content)
            pattern = re.compile(
                r'完整性扫描检查\s*检测结果：(.*?)\s*二、金属异物/伪影检查\s*检测结果：(.*?)\s*三、呼吸运动伪影检查\s*检测结果：(.*?)\s*四、剂量噪声检查\s*检测结果：(.*?)(?:报告产出机构|$)',
                re.S)

            match = pattern.search(content)
            if match:
                result1 = match.group(1).replace('\n', '').strip()
                result2 = match.group(2).replace('\n', '').strip()
                result3 = match.group(3).replace('\n', '').strip()
                result4 = match.group(4).replace('\n', '').strip()

                if stage==1:
                    if "不完整" in result1:
                        result1 = "扫描不完整，建议重新扫描"
                    else:
                        result1 = "扫描完整"
                    if "未检测到" not in result2:
                        result2 = "检测到疑似金属伪影"
                    if "未检测到" not in result3:
                        result3 = "检测到疑似呼吸运动伪影"
                    if not "检测到疑似" in result3:
                        print(result3)

                    assistant_answer = f"""
一、完整性扫描检查
检测结果：{result1}
二、金属异物/伪影检查
检测结果：{result2}
三、呼吸运动伪影检查
检测结果：{result3}
四、剂量噪声检查
检测结果：{"剂量"+result4.split("剂量")[-1]}
"""


                else:
                    assistant_answer = f"""
一、完整性扫描检查
检测结果：{result1.replace("建议重新扫描", "")}
二、金属异物/伪影检查
检测结果：{result2.replace("请检查对应的切片", "")}
三、呼吸运动伪影检查
检测结果：{result3.replace("请检查对应的切片", "")}
四、剂量噪声检查
检测结果：{"剂量"+result4.split("剂量")[-1]}
"""


                #video_path_prefix = "/data/wanghaoyu/paper_datasets/ct2report/train/videos/"
                video_path_prefix = "/data2/wanghaoyu/datasets/ct2repo/train/videos/"
                message = {"messages":[{"content":user_prompt, "role":"user"}, {"content":assistant_answer, "role": "assistant"}],
                           "videos": [video_path_prefix+r.replace(".txt", ".mp4")]}

                #print(message)
                data_list.append(message)
    print("ori:", len(data_list))
    # data_list = data_list[0: len(data_list]

    if stage == 2:
        # 剔除一些异常分布
        d_cnt = 0
        remove_list_must = []
        remove_list_random_huxi = []
        for n, d in enumerate(data_list):
            if "呼吸运动伪影，主要位于0-49层" in d["messages"][1]["content"] and "金属伪影，主要位于0-49层" in d["messages"][1]["content"]:
                d_cnt += 1
                remove_list_must.append(n)
        print("and:", d_cnt)

        d_cnt = 0
        for n, d in enumerate(data_list):
            if "呼吸运动伪影，主要位于0-49层" in d["messages"][1]["content"] and "未检测到金属伪影" in d["messages"][1]["content"]:
                d_cnt += 1
                remove_list_random_huxi.append(n)

        print("huxi:", d_cnt)

        new_data = []
        remove_list = list(set(remove_list_must+remove_list_random_huxi))
        remove_list = remove_list[0:int(0.8*len(remove_list))]
        for n, d in enumerate(data_list):
            if n in remove_list:
                continue
            else:
                new_data.append(d)
        print("new_data:", len(new_data))


        #second round remove
        remove_list_random_jinshu = []
        hx = defaultdict(int)
        d_cnt = 0
        for n, d in enumerate(new_data):
            if "金属伪影，主要位于0-49层" in d["messages"][1]["content"]:
                pattern = r'检测到疑似呼吸运动伪影，主要位于0-\d+层，请检查对应的切片'
                d_cnt += 1
                if re.search(pattern, d["messages"][1]["content"]):
                    remove_list_random_jinshu.append(n)
                #print(d["messages"][1]["content"])
        print("jinshu:", d_cnt)
        random.shuffle(remove_list_random_jinshu)

        data_list = []
        remove_list = remove_list_random_jinshu[0:int(0.8*len(remove_list_random_jinshu))]
        for n, d in enumerate(new_data):
            if n in remove_list:
                continue
            else:
                data_list.append(d)
        print("final_data:", len(data_list))

    with open(os.path.join(base_dir, "test_vqa_one-stage.json"), "w", encoding="utf-8") as d:
        json.dump(data_list, d, indent=4)