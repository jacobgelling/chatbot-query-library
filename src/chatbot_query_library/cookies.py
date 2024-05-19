#!/usr/bin/env python
"""Provides methods for managing cookies from browsers."""

import platform
from typing import Callable
from http.cookiejar import CookieJar
import browser_cookie3
import os

class CookieManager:
    def __init__(self, domain_name: str = "", prefix: str = None, browser: Callable = browser_cookie3.edge, cookie_files: list = None):
        self.domain_name = domain_name
        self.prefix = prefix
        self.browser = browser
        if browser == browser_cookie3.edge and not cookie_files:
            self.cookie_files = generate_edge_cookie_files()
        else:
            self.cookie_files = cookie_files
        self.current_cookie_file = self.cookie_files[0] if self.cookie_files else None

    def get_cookie_dict(self) -> dict:
        """Get cookies from the specified browser for the given domain and optional prefix."""
        if not self.current_cookie_file:
            raise Exception("No current cookie file.")

        cookie_dict = {
            cookie.name: cookie.value
            for cookie in self.browser(domain_name=self.domain_name, cookie_file=self.current_cookie_file)
            if not self.prefix or cookie.name.startswith(self.prefix)
        }
        return cookie_dict
    
    def get_u_cookie(self) -> str:
        """Get the _U cookie from the specified browser for the given domain and optional prefix."""
        cookie_dict = self.get_cookie_dict()
        return cookie_dict.get("_U")

    def get_cookie_jar(self) -> CookieJar:
        """Get cookies from the specified browser for the given domain and optional prefix as a CookieJar.
        """
        if not self.current_cookie_file:
            raise Exception("No current cookie file.")

        cookie_jar = CookieJar()
        for cookie in self.browser(domain_name=self.domain_name, cookie_file=self.current_cookie_file):
            if not self.prefix or cookie.name.startswith(self.prefix):
                cookie_jar.set_cookie(cookie)
        return cookie_jar
    
    def get_cookie_list(self) -> list:
        """Get cookies from the specified browser for the given domain and optional prefix as a list.
        """
        if not self.current_cookie_file:
            raise Exception("No current cookie file.")

        cookie_list = [
            {
                "domain": cookie.domain,
                "expirationDate": float(cookie.expires) if cookie.expires else None,
                "hostOnly": not cookie.domain_initial_dot,
                "httpOnly": "HTTPOnly" in cookie._rest,
                "name": cookie.name,
                "path": cookie.path,
                "sameSite": "no_restriction",
                "secure": bool(cookie.secure),
                "session": cookie.discard,
                "storeId": None,
                "value": cookie.value,
            }
            for cookie in self.browser(domain_name=self.domain_name, cookie_file=self.current_cookie_file)
            if not self.prefix or cookie.name.startswith(self.prefix)
        ]
        return cookie_list
    
    def rotate_cookie_file(self) -> None:
        """Rotate the list of cookie files, selecting the next one as the current cookie file."""
        if self.cookie_files and len(self.cookie_files) > 1:
            self.cookie_files = self.cookie_files[1:] + self.cookie_files[:1]
            self.current_cookie_file = self.cookie_files[0]

    def kill_cookie_file(self) -> None:
        """Remove the current cookie file from the list of cookie files."""
        if self.cookie_files and len(self.cookie_files) > 1:
            self.cookie_files = self.cookie_files[1:]
            self.current_cookie_file = self.cookie_files[0]
        else:
            raise Exception("Cannot kill the last cookie file.")

def generate_edge_cookie_files(default_profile: bool = False) -> list:
    """Automatically generate a list of Microsoft Edge cookie files."""
    # Get the directory for the Edge cookie files
    if platform.system() == "Windows":
        dir1 = os.path.join(os.getenv('LOCALAPPDATA'), "Microsoft/Edge/User Data")
        dir2 = "Network/Cookies"
    elif platform.system() == "Darwin":
        dir1 = os.path.join(os.getenv('HOME'), "Library/Application Support/Microsoft Edge")
        dir2 = "Cookies"
    elif platform.system() == "Linux":
        dir1 = os.path.join(os.getenv('HOME'), ".config/microsoft-edge")
        dir2 = "Cookies"
    else:
        raise Exception("Unsupported platform.")
    
    # Check dir1 exists
    if not os.path.exists(dir1):
        raise Exception(f"Directory {dir1} does not exist.")
    
    # Get profile cookie files
    cookie_files = [
        os.path.join(dir1, folder, dir2)
        for folder in os.listdir(dir1)
        if folder.startswith("Profile ")
    ]

    # Add the default profile cookie file
    default_cookie_file = os.path.join(dir1, "Default", dir2)
    if default_profile and os.path.exists(default_cookie_file):
        cookie_files.append(default_cookie_file)

    return cookie_files
