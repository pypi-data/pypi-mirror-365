import requests, json, re
from . import config
from .exceptions import CookieError, UserNotFound

class Instagram:
    def __init__(self, cookie: str) -> None:
        self.session = requests.session()
        self.session.cookies['cookie'] = cookie

        self.is_login = False 
        
    def login(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_login:
                self.user_login()

            return func(self, *args, **kwargs)
        return wrapper

    def user_login(self) -> bool:
        src = self.session.get(config.IGURL +'me').text
        try:
            setattr(self, 'username', re.search(r'"username":"(.*?)"', src).group(1))
            setattr(self, 'id', re.search(r'"id":"(.*?)"', src).group(1))
            setattr(self, 'name', re.search(r'"full_name":"(.*?)"', src).group(1))
            setattr(self, 'graphql_headers', {'authority': 'www.instagram.com','accept': '*/*','accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7','content-type': 'application/x-www-form-urlencoded','origin': 'https://www.instagram.com','referer': 'https://www.instagram.com/','sec-ch-prefers-color-scheme': 'dark','sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"','sec-ch-ua-full-version-list': '"Not A(Brand";v="8.0.0.0", "Chromium";v="132.0.6961.0"','sec-ch-ua-mobile': '?1','sec-ch-ua-model': '"23108RN04Y"','sec-ch-ua-platform': '"Android"','sec-ch-ua-platform-version': '"15.0.0"','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36','x-asbd-id': '359341','x-csrftoken': re.search(r'"csrf_token":"(.*?)"', src).group(1)})
            setattr(self, 'api_headers', {'authority': 'www.instagram.com','accept': '*/*','accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7','content-type': 'application/x-www-form-urlencoded','origin': 'https://www.instagram.com','referer': 'https://www.instagram.com/ivan.fmsyh','sec-ch-prefers-color-scheme': 'light','sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"','sec-ch-ua-full-version-list': '"Chromium";v="139.0.7339.0", "Not;A=Brand";v="99.0.0.0"','sec-ch-ua-mobile': '?0','sec-ch-ua-model': '""','sec-ch-ua-platform': '"Linux"','sec-ch-ua-platform-version': '""','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36','x-asbd-id': '359341','x-csrftoken': re.search(r'"csrf_token":"(.*?)"', src).group(1),'x-ig-app-id': '936619743392459','x-ig-www-claim': 'hmac.AR1ex5_OwFYv6vSWjrxVLTlRWmlRczzopy3Fm8Ff-VG4-N45','x-instagram-ajax': '1025144473','x-requested-with': 'XMLHttpRequest','x-web-session-id': '',})

            self.is_login = True
        except AttributeError:
            raise CookieError('Check your cookies.')

    @login 
    def user_data(self, username) -> dict:
        user = self.session.get(config.IGURL +'/api/v1/users/web_profile_info/?username='+ username.replace('@',''), headers=self.api_headers).json()['data']['user']
        try:
            return {
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "biography": user.get("biography"),
                "followers": user.get("edge_followed_by", {}).get("count"),
                "following": user.get("edge_follow", {}).get("count"),
                "is_private": user.get("is_private"),
                "is_verified": user.get("is_verified"),
                "profile_pic_url": user.get("profile_pic_url_hd"),
                "mutual_followers": [
                    edge["node"]["username"]
                    for edge in user.get("edge_mutual_followed_by", {}).get("edges", [])
                ]}
        except Exception as e:
            raise UserNotFound(f'User: {username} not found!!')


