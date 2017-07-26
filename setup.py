from setuptools import setup

setup(name='demiReportTelegram',
      version='0.4.0',
      description='A random funny telegram bot.',
      url='https://github.com/jossalgon/demiReportTelegram',
      author='Jose Luis Salazar Gonzalez',
      author_email='joseluis25sg@gmail.com',
      packages=['demiReportTelegram'],
      package_data={'demiReportTelegram': ['data/music/*', 'data/stickers/*', 'data/voices/*', 'data/gifs/*']},
      install_requires=[
          "requests",
          "ts3",
          "pymysql",
          "reportTelegram",
          "teamSpeakTelegram"
      ],

      zip_safe=False)
