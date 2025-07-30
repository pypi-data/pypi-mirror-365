from setuptools import setup, find_packages

setup(
    name='tg_notifier',
    version='0.1',
    author='imbecility',
    packages=find_packages(),
    url='https://github.com/imbecility/tg_notifier',
    license='MIT',
    description='отправка уведомлений в телеграм без зависимостей',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        # nothing
    ],
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)