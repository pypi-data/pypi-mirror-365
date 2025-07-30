import random
from dataclasses import dataclass
from typing import List
import requests
import urllib3
from bs4 import BeautifulSoup
import requests
@dataclass
class User_agent:
    """A smart class to generate diverse User-Agents for different devices and operating systems"""
    
    @staticmethod
    def __random_version(base: int, variations: int = 5) -> str:
        """Generate a Random Version Number"""
        return f"{base}.{random.randint(0, 9)}.{random.randint(0, 50)}"
    
    @staticmethod
    def _random_safari_version() -> str:
        """Generate a Random Safari Version"""
        return f"{random.randint(600, 605)}.{random.randint(1, 50)}.{random.randint(1, 50)}"
    
    @classmethod
    def generate_iphone_ua(cls) -> str:
        """Generate a Random User-Agent for an iPhone"""
        ios_version = cls.__random_version(16)
        safari_version = cls._random_safari_version()
        return f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version.replace('.', '_')} like Mac OS X) AppleWebKit/{safari_version} (KHTML, like Gecko) Version/{ios_version} Mobile/15E148 Safari/{safari_version.split('.')[0]}"
    
    @classmethod
    def generate_samsung_ua(cls) -> str:
        """Generate a Random User-Agent for a Samsung Phone"""
        android_version = cls.__random_version(12)
        chrome_version = cls.__random_version(104)
        models = ["SM-G998B", "SM-S901B", "SM-N986B", "SM-F926B","SM-G781B",  "SM-A525F"]
        model = random.choice(models)
        return f"Mozilla/5.0 (Linux; Android {android_version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Mobile Safari/537.36"
    
    @classmethod
    def generate_windows_ua(cls) -> str:
        """Generate a Random User-Agent for Windows"""
        chrome_version = cls.__random_version(104)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
    
    @classmethod
    def generate_mac_ua(cls) -> str:
        """Generate a Random User-Agent for Mac"""
        safari_version = cls._random_safari_version()
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(12, 15)}_{random.randint(0, 5)}) AppleWebKit/{safari_version} (KHTML, like Gecko) Version/{random.randint(12, 16)}.0 Safari/{safari_version.split('.')[0]}"
    
    @classmethod
    def generate_linux_ua(cls) -> str:
        """Generate a Random User-Agent for Linux"""
        chrome_version = cls.__random_version(104)
        return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
    
    @classmethod
    def generate_tablet_ua(cls) -> str:
        """Generate a Random User-Agent for a Tablet"""
        if random.choice([True, False]):
            return cls.generate_ipad_ua()
        return cls.generate_android_tablet_ua()
    
    @classmethod
    def generate_ipad_ua(cls) -> str:
        """Generate a User-Agent for an iPad"""
        ios_version = cls.__random_version(15)
        safari_version = cls._random_safari_version()
        return f"Mozilla/5.0 (iPad; CPU OS {ios_version.replace('.', '_')} like Mac OS X) AppleWebKit/{safari_version} (KHTML, like Gecko) Version/{ios_version} Mobile/15E148 Safari/{safari_version.split('.')[0]}"
    
    @classmethod
    def generate_android_tablet_ua(cls) -> str:
        """Generate a Random User-Agent for an Android Table"""
        android_version = cls.__random_version(11)
        chrome_version = cls.__random_version(104)
        models =  ["SM-T870", "SM-T970","SM-X700","SM-X800"]
        model = random.choice(models)
        return f"Mozilla/5.0 (Linux; Android {android_version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"
    
    @classmethod
    def generate_random_ua(cls) -> str:
        """Generate a Random User-Agent from All Types"""
        methods = [
            cls.generate_iphone_ua,
            cls.generate_samsung_ua,
            cls.generate_windows_ua,
            cls.generate_mac_ua,
            cls.generate_linux_ua,
            cls.generate_tablet_ua
        ]
        return random.choice(methods)()

class RandUserAgent:
    """User-Agent Manager for Practical Use"""
    
    @staticmethod
    def get_user_agent(device_type: str = "random") -> str:
        """
        Get a User-Agent Based on the Desired Type

        Available options:

        'iphone' – to generate a User-Agent for an iPhone device
        'samsung' – to generate a User-Agent for a Samsung device
        'windows' – to generate a User-Agent for a Windows browser
        'mac' – to generate a User-Agent for a Mac browser
        'linux' – to generate a User-Agent for a Linux browser
        'tablet' – to generate a User-Agent for a tablet
        'random' – (default) to generate a random User-Agent from all types
        """
        generator = User_agent()
        
        if device_type == "iphone":
            return generator.generate_iphone_ua()
        elif device_type == "samsung":
            return generator.generate_samsung_ua()
        elif device_type == "windows":
            return generator.generate_windows_ua()
        elif device_type == "mac":
            return generator.generate_mac_ua()
        elif device_type == "linux":
            return generator.generate_linux_ua()
        elif device_type == "tablet":
            return generator.generate_tablet_ua()
        else:
            return generator.generate_random_ua()
    
    @staticmethod
    def get_random_mobile_ua() -> str:
        """Get a Random User-Agent for Phones Only"""
        return random.choice([
            User_agent.generate_iphone_ua(),
            User_agent.generate_samsung_ua()
        ])




class Proxy:
    def __init__(self):
        """DEEP FIND PROXY HTTPS INPUT True or not deep find and find top proxy inpot False or None"""
        
    def __runer(self, url):
        response = requests.get(url)
        sub = BeautifulSoup(response.content, 'html.parser')

        findr = sub.find_all('tr')
        r = []
        for i in findr:

            f = i.find_all('td')
            if len(f) >= 2:
                ips = f[0].find('a')
                ports = f[1].find('a')
               
                ip = ips.text.strip()
                port = ports.text.strip()
                r.append(f"{ip}:{port}")
        return r

    def get_proxy(self,deep=False):
        self.deep = deep

        self.urls = ['https://proxydb.net/?country=&offset=30&protocol=https','https://proxydb.net/?country=&offset=60&protocol=https','https://proxydb.net/?country=&offset=90&protocol=https']
        


# https://proxydb.net/?country=&offset=90&protocol=https
        if deep == False:
            return self.__runer('https://proxydb.net/?protocol=https&country=')
        
        elif deep == True:
            allprox = []
            for url in self.urls:
        
                allprox.extend(self.__runer(url))
            return allprox


    
    @staticmethod
    def check(proxy,verify=True):
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        """ proxy , verify True or False """
        try:
            before_ip = requests.get("https://api64.ipify.org?format=json", proxies={'https': f'{proxy}'},timeout=15,verify=verify).json()
            with open('Proxy-Check.txt', 'a') as file:
                file.write(f'{proxy}\n')
            return True,before_ip['ip']
        except requests.exceptions.RequestException:
            return False


 




    