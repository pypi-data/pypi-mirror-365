import os
from huggingface_hub import hf_hub_download

def get_model():
    model_local_path = os.path.expanduser("~/.phydcm/mri_best_model.keras")
    
    if not os.path.exists(model_local_path):
        print("Downloading model from Hugging Face...")
        model_local_path = hf_hub_download(
            repo_id="PhyDCM/phydcm-models",
            filename="mri_best_model.keras",
            cache_dir=os.path.expanduser("~/.phydcm")
        )
    
    return model_local_path
