import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MFAultra",
    version="0.1.0",
    author="LitDDD",
    author_email="cz_a340-600@qq.com",
    description="一个功能强大的身份验证模块，支持多因素认证和RBAC权限系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.douyin.com/user/MS4wLjABAAAACQczOtUtm27WBmLg8dcGpgTrWXR6LjKp2lyJJS3XwnM?from_tab_name=main",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        "pyotp>=2.8.0",
        "bcrypt>=4.0.1",
    ],
)    