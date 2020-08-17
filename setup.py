# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xchk_multiple_choice_strategies']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.8,<4.9']

setup_kwargs = {
    'name': 'xchk-multiple-choice-strategies',
    'version': '0.1.4',
    'description': 'Checks and strategies for multiple choice questions in the xchk system',
    'long_description': None,
    'author': 'Vincent Nys',
    'author_email': 'vincentnys@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
