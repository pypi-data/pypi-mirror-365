from setuptools import setup, find_packages

setup(
    name="wRodaCupom",
    version="1.0.0",
    description="Automação de agendamento e envio de relatórios de cupons.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Wedici Lins",
    author_email="wedici.lins@gmail.com",
    url="https://github.com/seu-repositorio/wRodaCupom",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "schedule",
        "pyodbc",
        "tk",
        "smtplib",
        "email"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
