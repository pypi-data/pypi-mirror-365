from setuptools import setup, find_packages
import os

# قراءة محتوى README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# قراءة requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="phydcm",
    version="1.5.0",
    author="PhyDCM Team",  # ضع اسمك هنا
    author_email="phydcm.team@outlook.com",  # ضع إيميلك هنا
    description="PhyDCM: Medical Image Classification using Vision Transformers for MRI, CT, and PET scans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhyDCM/phydcm",  # رابط مستودع GitHub
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=requirements + [
        "requests>=2.25.0",
        "tqdm>=4.62.0",
    ],
    include_package_data=True,
    package_data={
        "phydcm": [
            "data/*",
            "*.py",
        ],
    },
    entry_points={
        "console_scripts": [
            "phydcm-train=phydcm.train:main",
            "phydcm-predict=phydcm.predict:main",
        ],
    },
    keywords="medical imaging, deep learning, vision transformer, MRI, CT, PET, classification",
    project_urls={
        "Bug Reports": "https://github.com/PhyDCM/phydcm/issues",
        "Source": "https://github.com/PhyDCM/phydcm",
        "Documentation": "https://github.com/PhyDCM/phydcm/blob/main/README.md",
    },
)