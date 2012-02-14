rom setuptools import setup

def main():
    setup(
        name = 'wfreadable',
        version = '0.2',
        packages = ['wfreadable'],
        include_package_data = True,
        description = "preview and readability for waveface",
        license = 'copyright reserved',
        maintainer = 'Steven Shen',
        maintainer_email = 'steven.shen@waveface.com',
        install_requires = ['lxml', 'opengraph', 'readable'],
        zip_safe = False,
        url = "https://waveface.com"
    )


if __name__ == '__main__':
    main()


