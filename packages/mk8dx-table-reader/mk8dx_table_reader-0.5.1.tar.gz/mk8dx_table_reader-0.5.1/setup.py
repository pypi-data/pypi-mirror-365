from setuptools import setup, find_packages

setup(
    name="mk8dx_table_reader",      
    version="0.5.01",             
    author="Julien ABADIE",       
    author_email="julien.abadie@etu.uca.fr",
    description="A package to extract player names and scores from MK8DX tables using YOLO and EasyOCR.",
    long_description=open("README.md").read(),  # Read README
    long_description_content_type="text/markdown",
    url="https://github.com/PrizeWhipser/shortcat.tips",  # GitHub repo
    packages=find_packages(exclude=["build", "dataset", "discord_part", "datasetManager", "datasetDeopt", "labelingTools", "visualize_model_performance"]),     # Automatically find packages
    package_data={
    "your_package": [
        "models/*.pt",        
        "models/number_recognition_model.h5",     
    ],
    },
    include_package_data=True, 
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.11.11",      # Python version compatibility
    install_requires=[
        "pillow",
        "opencv-python",
        "easyocr",
        "keras",
        "numpy",
        "pathlib",
        "setuptools",
        "tensorflow",
        "tensorflow.keras",
        "ultralytics",
    ],
)