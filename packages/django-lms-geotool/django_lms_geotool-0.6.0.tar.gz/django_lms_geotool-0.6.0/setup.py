from setuptools import setup, find_packages

setup(
    name="django-lms-geotool",
    version="0.6.0",
    author="MrYuGoui",
    author_email="MrYuGoui@163.com",
    description="LMS的地理信息工具集",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cuscri/geotool",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'django_lms_geotool': [
            'templates/*/*.html',  # 递归包含
            'static/*/*.*',
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Django",
        "numpy",
        "django-simpleui",
        "djangorestframework",
        "django-import-export"
    ],
)
