from setuptools import setup, find_packages

setup(
    name="klang_bas",
    version="0.1.2",
    description="Get current keyboard layout language (Windows only)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Abdelrahman",
    author_email="abdelrahmanmbartak@gmail.com",
    url="https://github.com/AbodyPrmaga/klang",  # اختياري لو عندك مستودع GitHub
    packages=find_packages(),
    install_requires=["pywin32"],  # مكتبة win32 ضرورية
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License"
    ],
    license="MIT",
)
