---

### Data Processing Pipeline

The original data format is `.DCM`, while the model input format must be `.mp4`.  
Therefore, a converter pipeline is needed:

`.DCM` → `.nii` → `.PNG` → `.mp4`

We provide the full pipeline as follows:

1. `dicom2nii.py` — `.DCM` → `.nii`  
2. `nii2rgb_auto.py` — `.nii` → `.PNG`  
3. `add_layer_info.py` — image preprocessing  
4. `img2mp4.py` — `.PNG` → `.mp4`  
5. `make_dataset_2stage.py` — build dataset for training  

---