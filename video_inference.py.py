import time

from transformers import Qwen3VLForConditionalGeneration, AutoProcessor
import torch
import os
import json

# 设置环境变量
os.environ['greedy'] = 'false'
os.environ['top_p'] = '0.8'
os.environ['top_k'] = '20'
os.environ['temperature'] = '0.7'
os.environ['repetition_penalty'] = '1.0'
os.environ['presence_penalty'] = '1.5'
os.environ['out_seq_length'] = '16384'

# 验证设置
print(os.environ.get('top_p'))  # 输出: 0.8


# default: Load the model on the available device(s)
model_path = "/data2/wanghaoyu/finetune/two-stage-test2"
model = Qwen3VLForConditionalGeneration.from_pretrained(
   model_path, dtype="auto", device_map="auto"
)
#model_path = "Qwen/Qwen3-VL-8B-Instruct"

# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# model = Qwen3VLForConditionalGeneration.from_pretrained(
#     model_path,
#     dtype=torch.bfloat16,
#     attn_implementation="flash_attention_2",
#     device_map="auto",
# )

processor = AutoProcessor.from_pretrained(model_path)

text_prompt = """
你是一个医疗图像质量检测专家，你能从 a.完整性扫描检查，b.金属异物/伪影检查，c.呼吸运动伪影检查 d.剂量噪声检查 4个方面评判一份ct视频数据是否存在质量异常。
现在仔细观察这个ct<video>，先判断是否存在质量异常，再重点观察异常出现的层(layer)!!!，输出详细的诊断报告，格式如下：

一、完整性检查
检测结果：扫描完整/不完整，具体哪一侧不完整
二、金属异物/伪影检查
检测结果：未检测到金属伪影/检测到疑似金属伪影，具体出现在ct的哪些层(重点!!!)
三、呼吸运动伪影检查
检测结果：未检测到呼吸运动伪影/检测到疑似呼吸运动伪影，具体出现在ct的哪些层(重点!!!)
四、剂量噪声检查
检测结果：剂量噪声检查是否合格
"""

# load data
log_file = open("./log_1gpu.txt", "a", encoding="utf-8")
video_dir = "/data2/wanghaoyu/datasets/ct2repo/test/videos"
for v in os.listdir(video_dir)[0:100]:
    st = time.time()
    video_path = os.path.join(video_dir, v)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": video_path,
                },
                {"type": "text", "text": text_prompt},
            ],
        }
    ]

    # Preparation for inference
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    )
    inputs = inputs.to(model.device)

    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    end = time.time()
    log_file.write(f"{end-st}\n")
    print(round(end-st, 4))
    print(output_text)
