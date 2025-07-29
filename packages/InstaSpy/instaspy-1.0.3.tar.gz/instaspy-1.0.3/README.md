<h1 align="center">INSTAGRAM SPY</h1>

<p align="center">
<a href="https://choosealicense.com/licenses/mit/"> <img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/pypi/pyversions/instaspy"></a>
<a href="https://pypi.org/project/instaspy/"> <img src="https://img.shields.io/pypi/v/instaspy"></a>
<a href="https://github.com/jepluk/instaspy/commits"> <img src="https://img.shields.io/github/last-commit/jepluk/instaspy"></a>
</p>

## instalation
```bash
pip install instaspy
```

## features
click this link to view the [documentation ](https://github.com/jepluk/instaspy/blob/6f54afc86ee7cb7a8b34a37cb708f2436c1ef93c/instaspy/docs/DOCS.md)

- Login Using Cookie.
- retrieve user information.
- 
## example
get cookies using this [extension](https://chromewebstore.google.com/detail/get-cookies/hdablekeodiopcnddiamhahahkiiloph)
```python
Python 3.12.11 (main, Jun  9 2025, 15:36:10) [Clang 18.0.3 (https://android.googlesource.com/toolchain/llvm-project d8003a456 on linux
Type "help", "copyright", "credits" or "license" for more information.

# import library
>>> from instaspy import Instagram
# login using cookie
>>> ig = Instagram('datr=N3KAaKEGbz2ZWbEj1K5zzmmB; ig_did=91E41F0C-2704-46A3-ACE3-018E3C0CA9DB; mid=aIByNwABADBD5ss27FyYbViOr9; ps_l=1; ps_n=1; dpr=2.1988937854766846; ig_nrcb=1; csrftokenZQ53Vo5xBaKCJuP5sI3fqJMPxTZ; ds_user_id=65122839; wd=891x1718; sessionid=651228843Rq4qYNrDWiKRwq%3A15%3AAYfVgrOWPZVBT-cJZgGcU3p9jV2W9Bi06cEV0d5ihA; rur="EAG\05465122884339\0541785063859:01fed90bed8c10b2c00728cc712bda49e218140ba1562ecb68e3d16bf2b71fca2b425"')

# take your Instagram account name
>>> ig.name
'Ivan Firmansyah'
# get your Instagram account username
>>> ig.username
'ivanfmh15'
# get your Instagram account ID
>>> ig.id
'65122884339'
# take all your Instagram data
# change username to view other people's account information
>>> ig.user_data(ig.username)
{'username': 'ivanfmh15', 'full_name': 'Ivan Firmansyah', 'biography': '.', 'followers': 760, 'following': 21, 'is_private': True, 'is_verified': False, 'profile_pic_url': 'https://scontent.cdninstagram.com/v/t51.2885-19/475306390_9479437722090101_2305614903739138725_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2QEJYFddVd3edQ8kpLiqYxeq305TYlj-mIAHh4hkBL9VaGhHxjuoax9_C0TViV9qZpY&_nc_ohc=aGhpNu57wsUQ7kNvwGd9CKp&_nc_gid=XssF4u90Nx-ExkK4i5zgdw&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfQEUtKpJ6nMSB9EFzLZCjlMhELSGr2QFRIUcZJ4QF6kkA&oe=688A7657&_nc_sid=8b3546', 'mutual_followers': []}
```
## support
help me to be enthusiastic about developing and learning new codes with a small donation hehe.

[saweria](https://saweria.co/meizugxyz)
