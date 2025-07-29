<h1 align="center">INSTAGRAM SPY</h1>

<p align="center">
<a href="https://choosealicense.com/licenses/mit/"> <img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/pypi/pyversions/instagpy"></a>
<a href="https://pypi.org/project/instagpy/"> <img src="https://img.shields.io/pypi/v/instagpy"></a>
<a href="https://github.com/jepluk/instaspy/commits"> <img src="https://img.shields.io/github/last-commit/jepluk/instaspy"></a>
</p>

## instalation
```bash
pip install instaspy
```

## features
- Login Using Cookie.
- retrieve user information.

## login
get cookies using this extension: https://....
```python
from instaspy import Instagram

cookie = 'your cookie'
ig = Instagram(cookie=cookie)
```
get your account data
```python
print(ig.name) # Instagram Name
print(ig.username) # Instagram Username
print(ig.id) # Instagram ID

# or using ig.user_data('me')
```

