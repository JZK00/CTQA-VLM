# Data Processing Pipeline

The original medical data format is `.DCM`, while this model requires `.mp4` as input.  
Therefore, we provide a complete conversion pipeline:

`.DCM` → `.nii` → `.PNG` → `.mp4`

---

## Pipeline Scripts

1. **`dicom2nii.py`**  
   Convert DICOM files to NIfTI format.  
   **Input:** `.DCM`  
   **Output:** `.nii`

2. **`nii2rgb_auto.py`**  
   Convert NIfTI volumes to RGB image slices.  
   **Input:** `.nii`  
   **Output:** `.PNG`

3. **`add_layer_info.py`**  
   Preprocess images and add layer-related information.  
   **Input:** `.PNG`  
   **Output:** processed `.PNG`

4. **`img2mp4.py`**  
   Convert PNG image sequences to MP4 videos.  
   **Input:** `.PNG` sequence  
   **Output:** `.mp4`

5. **`make_dataset_2stage.py`**  
   Build the final dataset for two-stage model training.  
   **Input:** processed data  
   **Output:** training dataset

---

## Recommended Execution Order

Run the scripts in the following order:

```bash
python dicom2nii.py
python nii2rgb_auto.py
python add_layer_info.py
python img2mp4.py
python make_dataset_2stage.py
