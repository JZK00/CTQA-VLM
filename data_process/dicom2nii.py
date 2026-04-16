import os
import pydicom
import nibabel as nib
import numpy as np
from tqdm import tqdm


def dicom_to_nifti(dicom_folder, output_file):
    # 获取DICOM文件列表
    dicom_files = [os.path.join(dicom_folder, f) for f in os.listdir(dicom_folder) if f.endswith('.dcm')]

    # 读取DICOM图像数据
    slices = [pydicom.dcmread(dcm) for dcm in dicom_files]
    slices.sort(key=lambda x: x.InstanceNumber)

    # 获取图像尺寸
    img_shape = list(slices[0].pixel_array.shape)
    img_shape.append(len(slices))
    img3d = np.zeros(img_shape)

    # 叠加图像数据
    try:
        for i, s in enumerate(slices):
            #print(s.pixel_array.shape)
            img3d[:, :, i] = s.pixel_array

        # 创建NIfTI图像
        nifti_img = nib.Nifti1Image(img3d, np.eye(4))

        # 保存NIfTI图像
        nib.save(nifti_img, output_file)
    except:
        print(f"wrong dcm folder: {dicom_folder}")


def find_pdf_files(root_dir):
    nii_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.pdf'):
                full_path = os.path.join(dirpath, filename)
                nii_files.append(full_path)
    return nii_files


base_dir = '/home/why/why/paper/mod_dataset/ct2report/private/'
pdf_file_list = find_pdf_files(base_dir)
dcm_dir_list = [i.replace(".pdf", "") for i in pdf_file_list]
for n in tqdm(dcm_dir_list):
    input_file = n
    if len(os.listdir(input_file)) > 1:
        print("working on:", input_file)
        output_file = input_file+'.nii'
        if not os.path.exists(output_file):
            dicom_to_nifti(input_file, output_file)

    #break
print("=====================================")