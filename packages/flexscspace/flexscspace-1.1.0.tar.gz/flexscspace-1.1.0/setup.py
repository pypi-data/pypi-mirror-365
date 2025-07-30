from setuptools import setup, find_packages
from pathlib import Path
LONG_DESC = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
setup(
    name="flexscspace",                     
    version="1.1.0",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",                        
    author="wangmy2025",
    author_email="wangmy2022@gmail.com",
    description="The update to SCSpace provides more flexible version options",
    url="https://github.com/wangmy2025/flexcspace",  
    packages=find_packages(include=["flexscspace", "flexscspace.*"]),              
    python_requires=">=3.8",                
    install_requires=[],
    include_package_data=True,                   
)




