from setuptools import setup, find_packages

setup(
    name="deepeye-models",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch",
        "numpy",
        "huggingface_hub",
    ],
    description="DeepEye: EEG-based AI Eye-Tracking Models",
    author="Radim Urban",
)
