from setuptools import find_packages , setup
from typing import List

HYPEN_E_DOT ="-e ."


def get_requirements(file_path:str)->List[str]:
    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
        return requirements

setup(
    name='ML-Genius',
    version='0.0.2',
    author='PratikRathod',
    author_email='pratikr1521998@gmail.com',
    description="An AutoML framework with classification, regression, etc.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=get_requirements("requirements.txt"),
)