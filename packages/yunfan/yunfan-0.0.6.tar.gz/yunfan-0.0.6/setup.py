from setuptools import setup, find_packages

VERSION = '0.0.6' 
DESCRIPTION = 'Yunfan platform interface toolkit.'
LONG_DESCRIPTION = 'Yunfan platform interface toolkit. The toolkit includes: dataset offline pulling, dataset online reading, etc.'

# 配置
setup(
        name="yunfan",
        version=VERSION,
        author="Wei Zhang",
        author_email="<zhangw355@foxmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],

        keywords=['python', 'yunfan'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
        ]
)