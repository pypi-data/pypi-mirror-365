"""
تحميل النماذج المدربة من مصادر خارجية
"""

import os
import requests
import json
from pathlib import Path
from tqdm import tqdm
import hashlib

# روابط النماذج (يمكن استضافتها على GitHub Releases أو Google Drive أو Hugging Face)
MODEL_URLS = {
    'mri': {
        'model': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/mri_best_model.keras',
        'labels': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/mri_labels.json',
        'model_hash': 'sha256_hash_here',  # للتحقق من سلامة الملف
    },
    'ct': {
        'model': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/ct_best_model.keras',
        'labels': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/ct_labels.json',
        'model_hash': 'sha256_hash_here',
    },
    'pet': {
        'model': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/pet_best_model.keras',
        'labels': 'https://github.com/PhyDCM/phydcm-models/releases/download/v1.0.0/pet_labels.json',
        'model_hash': 'sha256_hash_here',
    }
}

def get_models_dir():
    """إنشاء مجلد النماذج في مجلد المستخدم"""
    home_dir = Path.home()
    models_dir = home_dir / '.phydcm' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir

def calculate_file_hash(file_path):
    """حساب hash للملف للتحقق من سلامته"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def download_file(url, local_path, expected_hash=None):
    """تحميل ملف من رابط مع شريط التقدم"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(local_path, 'wb') as file, tqdm(
        desc=f"تحميل {local_path.name}",
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                pbar.update(len(chunk))
    
    # التحقق من hash إذا تم توفيره
    if expected_hash:
        file_hash = calculate_file_hash(local_path)
        if file_hash != expected_hash:
            os.remove(local_path)
            raise ValueError(f"خطأ في تحميل الملف: hash غير متطابق")
    
    print(f"✅ تم تحميل {local_path.name} بنجاح")

def download_model(model_type):
    """تحميل نموذج محدد"""
    if model_type not in MODEL_URLS:
        raise ValueError(f"نوع النموذج غير مدعوم: {model_type}")
    
    models_dir = get_models_dir()
    model_info = MODEL_URLS[model_type]
    
    # مسارات الملفات المحلية
    model_path = models_dir / f"{model_type}_best_model.keras"
    labels_path = models_dir / f"{model_type}_labels.json"
    
    # تحميل النموذج إذا لم يكن موجوداً
    if not model_path.exists():
        print(f"تحميل نموذج {model_type.upper()}...")
        download_file(
            model_info['model'], 
            model_path, 
            model_info.get('model_hash')
        )
    
    # تحميل ملف التسميات إذا لم يكن موجوداً
    if not labels_path.exists():
        print(f"تحميل تسميات {model_type.upper()}...")
        download_file(model_info['labels'], labels_path)
    
    return model_path, labels_path

def check_model_exists(model_type):
    """فحص وجود النموذج محلياً"""
    models_dir = get_models_dir()
    model_path = models_dir / f"{model_type}_best_model.keras"
    labels_path = models_dir / f"{model_type}_labels.json"
    
    return model_path.exists() and labels_path.exists()

def get_model_paths(model_type):
    """الحصول على مسارات النموذج (تحميل تلقائي إذا لم يكن موجوداً)"""
    if not check_model_exists(model_type):
        return download_model(model_type)
    
    models_dir = get_models_dir()
    model_path = models_dir / f"{model_type}_best_model.keras"
    labels_path = models_dir / f"{model_type}_labels.json"
    
    return model_path, labels_path

def list_downloaded_models():
    """عرض النماذج المحملة"""
    models_dir = get_models_dir()
    downloaded = []
    
    for model_type in MODEL_URLS.keys():
        if check_model_exists(model_type):
            model_path = models_dir / f"{model_type}_best_model.keras"
            size_mb = model_path.stat().st_size / (1024 * 1024)
            downloaded.append({
                'type': model_type,
                'size_mb': round(size_mb, 2),
                'path': str(model_path)
            })
    
    return downloaded

def clear_models_cache():
    """حذف النماذج المحملة لتوفير مساحة"""
    models_dir = get_models_dir()
    deleted_files = []
    
    for file_path in models_dir.glob("*"):
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            deleted_files.append({
                'name': file_path.name,
                'size_mb': round(size_mb, 2)
            })
            file_path.unlink()
    
    return deleted_files