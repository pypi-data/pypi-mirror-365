import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UAC",
    version="1.0.1",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="A python library that is an exploit for UAC Bypass on Windows. It works on any version of Windows and can execute a pyload(exe) with admin access without confirmation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)