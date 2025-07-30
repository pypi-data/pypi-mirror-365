from setuptools import setup, find_packages

setup(
    name="utilskit",  # 패키지 이름 (pip install 시 사용될 이름)
    version="0.2.0",    # 버전
    packages=find_packages(),  # textbasic 폴더 내 모든 패키지 포함
    include_package_data=True,  # 이 설정을 통해 패키지 내 데이터 파일을 포함시킬 수 있음
    package_data={
    },
    install_requires=[ # 패키지 설치 시 같이 설치되도록 설정
        "matplotlib==3.10.3",
        "numpy==2.2.6",
        "pandas==2.3.1",
        "PyMySQL==1.1.1",
        "SQLAlchemy==2.0.41",
        "tqdm==4.67.1",
        "xlrd==2.0.2"
    ],
    # install_requires=[
	#    "pandas>=1.3.0,<2.0.0",  # 버전 범위 설정 방법
	# ],
    author="Kimyh",
    author_email="kim_yh663927@naver.com",
    description="description",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/Kim-YoonHyun/my_package",  # 깃허브 주소 등
    classifiers=[   # 패키지의 Meta 데이터
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",   # 제약없는 가장 자유로운 라이센스(MIT 대학에서 이름이 유래했을뿐 MIT 가 관리하는 라이센스는 아님)
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # 최소 지원할 파이썬 버전
)