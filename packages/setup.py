from setuptools import setup, find_packages

setup(
    name='pyyaap',
    version='1.0.0',
    description='Python Yet Another Audio Package',
    author='Dzianis Ivanchuk',
    author_email='twihkapb@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "wave",
        "scipy",
        "opencv-python",
        "pydub",
        "psycopg2-binary"
    ],
)

