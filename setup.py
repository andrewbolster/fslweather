from setuptools import setup

setup(name='fslweather',
	version='0.1',
	description='The funniest joke in the world',
	author='Andrew Bolster',
	author_email='bolster@farsetlabs.org.uk',
	license='MIT',
	packages=['fslweather'],
	zip_safe=False,
	entry_points = {
		'console_scripts': ['fslweather=fslweather.__init__:main'],
	}
)
