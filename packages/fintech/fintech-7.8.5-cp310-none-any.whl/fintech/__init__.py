
###########################################################################
#
# LICENSE AGREEMENT
#
# Copyright (c) 2014-2024 joonis new media, Thimo Kraemer
#
# 1. Recitals
#
# joonis new media, Inh. Thimo Kraemer ("Licensor"), provides you
# ("Licensee") the program "PyFinTech" and associated documentation files
# (collectively, the "Software"). The Software is protected by German
# copyright laws and international treaties.
#
# 2. Public License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this Software, to install and use the Software, copy, publish
# and distribute copies of the Software at any time, provided that this
# License Agreement is included in all copies or substantial portions of
# the Software, subject to the terms and conditions hereinafter set forth.
#
# 3. Temporary Multi-User/Multi-CPU License
#
# Licensor hereby grants to Licensee a temporary, non-exclusive license to
# install and use this Software according to the purpose agreed on up to
# an unlimited number of computers in its possession, subject to the terms
# and conditions hereinafter set forth. As consideration for this temporary
# license to use the Software granted to Licensee herein, Licensee shall
# pay to Licensor the agreed license fee.
#
# 4. Restrictions
#
# You may not use this Software in a way other than allowed in this
# license. You may not:
#
# - modify or adapt the Software or merge it into another program,
# - reverse engineer, disassemble, decompile or make any attempt to
#   discover the source code of the Software,
# - sublicense, rent, lease or lend any portion of the Software,
# - publish or distribute the associated license keycode.
#
# 5. Warranty and Remedy
#
# To the extent permitted by law, THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF QUALITY, TITLE, NONINFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, regardless of
# whether Licensor knows or had reason to know of Licensee particular
# needs. No employee, agent, or distributor of Licensor is authorized
# to modify this warranty, nor to make any additional warranties.
#
# IN NO EVENT WILL LICENSOR BE LIABLE TO LICENSEE FOR ANY DAMAGES,
# INCLUDING ANY LOST PROFITS, LOST SAVINGS, OR OTHER INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR THE INABILITY TO USE THE
# SOFTWARE, EVEN IF LICENSOR OR AN AUTHORIZED DEALER OR DISTRIBUTOR HAS
# BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES, OR FOR ANY CLAIM BY
# ANY OTHER PARTY. This does not apply if liability is mandatory due to
# intent or gross negligence.


"""The Python Fintech package"""

__version__ = '7.8.5'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcvQdYlMe6OP61LSzLgogU69pZ2F1ALNixA0tRkahY2IVdYBUW2IJCFkUBlyLF3gt2rKBYo8bMxPTkpCdykpyYc05ienKTk+R6cuJvZr7dpRpN7r3P83/++vDtV6a8'
        b'M/P2eWfm71SXfxL0F43+LFZ00VOplJ5OpfXMQcbAGjgDXcY00qmCLCpVqGf1XDmlE+kFeiH6FReLrSKruIwqo2lqIaUXJVMcZfAoiqKpVAlNFcv0IoMkzVMvRlcpufci'
        b'V5lBsp7Wi1IlSySr6FWUR7nC435/yYJsg3xukTU7zySfbTRZDRnZ8nxdxkpdlkGiYD8XIdA+F+OLAF3aaHUG3aEFLPoTOX8to9HFQWXSetSGcnEJXUmVUSVMsYedLkNQ'
        b'2pkyiqbW0GuY5A73CIosBZuY0bFbhOhvHPrrjQvlSNckUwp5Yhv1A/68IAeDE+EvoMRUQzIdrVV+FtiX+ozP+93UJqpHCElhURhCxkE52EzWDSX9WFCWd4XSVXhnKLlE'
        b'Wzi6h5sngLJkFdwOGxbASuUTsBLWhM2LWRATAmvhRkVvcANWwY0sNTNFCM8tg63G1mHXOEsoyhm166UvtV9oczK/0gYblJ+odDG6r7SvpPtlZGfmMOfXf/NLUFQktS5b'
        b'FH/mVwVjHY5ygGPwLCjzRCWH4kITbKoQ+DSquTqMoQaBCxw8B3YWWgfilIfWSGD9alAD6mG9BiUFtaBeRMl82YGgrL/ZAyVRsG1MsMKMMZO/4Jf3fSZlmvOKDSZ5Jo8g'
        b'U9pkOovFYLampduMOVajicGdgMdNGiSjOdosdWVtYtu4TJspo02Ulma2mdLS2jzT0jJyDDqTLT8tTcF2qAlfmmizDN974gsupC8u2A9dfO4JGYYW0vjK0cLf8NU2FH1Y'
        b'OM5Po1QnqkJAVRLfu7gXxKCapZSRAtgEzhlzMCTK1BfpVwRif8/8W/S/A4vG2CiCR4c1NmbukG99KO269OW2fr2dePTxVPJ1k2EF/TZT6eMp1y5RLZnKZ7H0YxC9BaZ5'
        b'UdqcH+fY+ZeICikpJS6k5FrpOz4zKJsavZtNgwZPcEKJIKqE9cnh82ElqNJiVAhWq4JhZVhIbAJNLV0ijgdovBS0bRgepbOwClz2RC3SqCTBsBqcAyc4NKJ1VF9wgwO7'
        b'4XZw1oaHcwnYCM7gwQxD7ca/IspzImhNYuBmuD7TNgAlGR2q6TraYeAqHvBecIuCtfmjNFOUoFEFmzQqRVyCgBImM/7wMDxMssOb8Cqs1JBujY1VMZQnPDAV7GTgCVC9'
        b'0CZHKRbBPeACrEmC1XEJalgVD05xlC8oY8HRUFgKz3mgOvAQgn2jYbMmVhmrIigqoAK9ZLCaTUyKIiDAqpkz8Few3SKgOI4GB+AWUG0bjHOeDgIHecROiIW1ilhUPtzC'
        b'gkawFVwDO+Ep1GsE1GY1vKIZFYnSaGBdUqyA8h7MIjg3ThwHTqM0QShNH3DdGyeJTeBTyOBZlhJFFESh74PQ9zGgBe71jEHDlQ9rps6DGzW4zX5wLwuPwUO9UVv6Y4jO'
        b'gwPgaVijTIR1sUq1kPIsGQouMPAC3JxExiUTVIKbobAuHnW7UqGKE1C9B7JgPdwGt/QCewjSwv3wMryoSVLFhqK+rYpVxoWpYxLg5qlCSkkJ4K4loJGvqwHVdgnWwI2h'
        b'6LuaRgOwNRgeYuDlkbQNs4tkUCHVkO+4UXODNYj46+BGuAeuRwg3VyWkZnBCWAo2wUOkYukSBEYNrEqKnxccEw/rEuOTUnAqG9isnCCYBS+Buk5cjunIiw8SBu+gEQtl'
        b'HZxD4BA6RA6xw8MhcXg6pA4vh8zh7fBx9HL4Ono7/Bx9HP6OAEegI8jR19HP0d8xwDHQMcghdwx2DHEMdQxzDHeMcIx0BDsUjhBHqEPpUDnUjjBHuCPCMcoR6RjtGOMY'
        b'mznOyaapSg6xaRqxaYqwaZqwZsSckzvc9yRMvJ1MpDObLk+0DUH3M7MTu/CO2L48YyasIxduJgPaBzaNJnSWqFKo0OAiKvKFewu0LDgLdnna+uCBujEdVM0BR2ENQkCW'
        b'YtbS0dNW2wLwl+Oj4PZQ0AQuDVPGIOwG5TQsoyMIQsJrcD1oClWoYCVCRyE4ySxFjzp4lHwFV1fBVjxYYBPiIWjwuVga3OgFWwjNeINrcIcGVs2Hh+LxNw8aHPWIJFUO'
        b'hvVIKNSEzQcHYjA0XAwNLmi0NsxHpR6gDO5XhKoVDMWAS3TqKLiDZFrug9AVnEQkKqSEOQzYAi8Ew5OpPCQOuG+FBrGiDSaImAmqbSgNzhQgPkS+VgwBO8A6uI/gIY2K'
        b'raPjEVfYTHpmpGehhmCckqaEYxkJaAyYM9YWiFtfi7haU2gcorMk1PpoJo6WgVJ4gHwElXawhxQYrEIZVzOgcVlEADxNGqEDR8b4mBCdB6NGmOgpsAK08ozkAHDMBKd7'
        b'o8bHYUB20rPjwUlCSrBGDo95gVOEWhSYsMXgaQa17BDYa8PYgXr5QEyWH6xJUCK8t9NT/fqQjoFn4KEQG/p6ClbjL+ACvQDeHEDq662do8F8AG7kKGFfBm7tLRkDrvKg'
        b'bO4FqsD2DFgTA86gbCX07PngadIlWZoMsAFWI7apxkBW03OKwX5bP/TFNj3BU4FYCy4xVB2LeiZRQAVkc6OMHGnEk/AUaAE1IzWhWC7E4cH1EDJgG6LwExlMB7THmN5Z'
        b'7UFKj4N2qz1MJVJuSlhETwyhJ5bQELOGTe5w3xM94X/d1R420aj3eYq2TEEvdq8+8KX2pfR72sqse+iXe3Nj9G6PmEjamCn3enax0nPRuknbKzZulA6I/u/MhgmXZBu0'
        b'wtf8qbcFsh/X7HnzuEJkxZSZMgN1HpFcCEsa4Y4kBayN5QWY/3COXQTqrJjr92cz4EFwqSeNRhdqJdL0+uIYQrvKBMQWq9rTDAKbwko4uGkJvGElgqYZXETypCISp05C'
        b'+ArqcDIJbEAjDk+DSisegEIsDSKcSeLVCEhcHcsOzoInrRhvo+BGcC1UFRObNEWJaFoMWxlQPh6csY7g69gFywk4TvEAriO5r4rjQRoeIkiKA3udilgX1Yi8JYpRG5er'
        b's6wkKhdWlsRrxDT+L6MlWPXq7Uqr4NpYvcXaxlrMGWbMBs0++C3TXiS6x9Rk7uMqmWReS7lUrrIeVC5CEVs9hiIyQbIeIaqQ4pSIGQjh9Yfr3WN5BGQymf8NrZvrCf2m'
        b'aVIYC8acxfeFX2qX3nr9mYbbh3u//0zDc60Nm3q9IMv8OF5ERUdx/74zA+nNhMM8BZrSNMpgxCJ1cLOGRvzgFFMUHUBU5cGRSjdSISWuo6a8BR7k+5fpeXBsVmOOWx+m'
        b'1vqI0aD4U+36MJuXvqLn8UDab6B7KHCWSlwMvqHWyf67h8HAn8Bhw7JQ1fRxWG4hxmymkW6yz6fTWNDOv2QXVHZ065GpoBN5uIPcLWhvhsyUl5aXnmmzZOisxjzTRvTu'
        b'B9wqjrEFo58JSPPcjDgp6aOkuFBVYiJSm/rDTYjI6lkqFFwQwN1asOsx4Cj/XTg8XEAYGvA7wiQxIfrBbULEQPmaEaH5DgRPQaR33ggEmx+OiBMwItIYFZEJyP1BZOzG'
        b'C2mqJ14o6JzIxYkHuesnnNjBuev/07wY1y/piRg8Bm7lLDMx9tllpz65p/1K+4L+njYVvP984Gs+r9wCc8Fcxe0X5r5864W5t999Zil8/ZVFL8+Frz+78zpk/E5lBGcp'
        b'sz7OoSndaem84RUKmlDEsOD+FnAmJhHZLVX8IKdpesEGFjTDFmRL0DxH4bpyrS7UIUjL0OXw5OFDyIPx90GcS4ywWVzK/Fbc15JtzLSmGczmPLN6Uk4eSm2ZoiaZXEyN'
        b'05mzLG3ClavwbwdC6mZLMmYMt3mQm6SwxNjeTlK+X/ZAUlhWImNtA9yFNHhYGR+KVEOkU1eHwc3ggifEdntVUiLSIJBavgXUiOaPp0D1VA942QovGtMq0xiLApVwbPOc'
        b'lVnZWTmvNWclZiTq4nUr7p4w3NOe1N1Dlr0kE3eu4VXhy9+/wTfqMTvPs0PndOQwfSRC82B3Uq+eOsPcy90LOOXWDr3wdQ+9gBkp3NGvsEsfMPA8PEf1A9c4cAKum/1w'
        b'OuvmCno8Csvuid0z3TCcS1xg/I+fH2fBAn68skmjw8pGjO7tl7jNGxXysb136r/RijM/fgWpWneEpQPeVXC8iD8G9iCVHQvvRKUqkefpveBGGWhlQR286GlV4VQVcBu4'
        b'SYR0fj4y04PjVGpQl4R6oj40FpwJ5mX+ojRxJjyqJR6YiYgNbud1AmeixUh55tP1hds4ZPudYYlaIwVnZaRkRVx8YkJcvM9KWMfrGcOGCgbATeBaR4ToMPReNlNGts5o'
        b'MujTDKuJpmeRksEXDhLiwcOSf4griwIJGZSqnTaanAhGm4e60QCn3t+OBtK/94AGRIHaC3arQolVHQM3WmATUkoTEEIgXiCkhhcLksDW4E5j5kIErCm4GB4xGP/nDJej'
        b'epL+4sQc3BfXcz3EVwa+KKWjX1qzx3Jn6fKssUXJS2iKqCySQdpQFbyAVOot4CKFTOxDNLg4cwjxDPUV/+C91ZsOboj9iv5tkWrgNt6j4xFLMYHxIjGVr0uLCZTwLxcO'
        b'8aXu5SagO+3SzPg5lHH3yHCBJQ89/3ISaHR63QnDCcNX2nxd5cXThi8QwX+hNWWG+J7Upd5qAK0NvUKeE/u9dVrHnPzklOGs7rTOX/QF86Z0iHZCxR06JiDO//w74X3u'
        b'sLd3zV/UP7C5iVZPe6m5LfJt5lXlu8KTmVKC0lK/AS0HvkFcGesKaUvBFY3T5aGAV5HCCRqYvIApPfOSR3IYLltnySbYNYJgl3ikGGmV+D+vY0po5j+cQOp84n5lSjmB'
        b'eXg73vEct50n9wwFzScjaIgzH+vAjf76EDXHG+yJwabU5QCkcyIs6IPM3aULHuHqpbu4epk/h3a4Qzy6oZ000eaL7rNmwV1wC5sIr1FUGBUGL88jiHJtFkeh3+CJ07VK'
        b'2F/MY8/GKOw5pII/kmqVb/mLKDNm4D1d2ug042/H9jEWrAEm7JmjeiVCwkT4VNz9ecSLmUMLn1jypM7in9RcseiOVBK66N764DsvjXg+xrRi/ct+aRH1D/6+ZVhiYPPH'
        b'lf9+N/1TZUDRt5WFI4NnX/eJ2FWx6U5ISvWJoIb8yPqSf7+3/uV9qbZZJz88mfb1nqqshaseVL8395dJb684MEM/OCJvyJDeT2+4OG7I0rUR4iEvfdei8CQ8DG6GzSNd'
        b'tlknu8wTnuCQBrbIKkfJosBmcMKiVChgdXyIKtZGBEi8hqFClgjA0/0WEPvND65H/y8kwotaZCLxMobygqXsaHiiLykmApaNx5WBy0jb7GLiwUPQQahgdQk8H6pGYrsK'
        b'OxnAGSOoY1TLQA2xAH0LUP7uFuB00ECMQGQCTkyyYr1yOarlamgcdsbEI7PbE7QUgOsM3DcCricaELyWU4SMcmWIQg3rkbZLUYFyWAZOcsvBDrCbQAv3gS3AwYsCVBcv'
        b'ApAJGZDPICu1NZpAq4+08maHBu4ER512hxXW8FbJdq+S0ERVLOo4hpKKwUZwnBWDY2Gd7LbfsQ2F+bb0HCMvIYIJDTMTZLQPIinmgZDxQ+TEOakX069QIKGl6D+SHiPd'
        b'5QT0WEWQm2RxyqvtJOvzQg8ki1OPhg2z1bA0NDgBViNjWYiM4WYGlGaOJNVkCDtQGCYksYvCfFlsGdjpIKpEWCmyCyupMqZEZBdZRhSL7OxByi5spEvECymTB0dZ6aJ+'
        b'NIX/L6ZMnquQwmwX43x2IS5hEqWncU5zqV2QH2qkSgR2wUGmkZpJLUtYypR4lEhw+XaPMsZcQmri0N0Cu/Ag20jKOMiRtNISz0oWpfO0M5mskbJLjtB1NE0VzDYNIbmk'
        b'CD5ppYddWEYjiCWVYnxXRpOcYpJT3CVnhl1qLqyU8jlcsNKErxSE4ysp1xNBs7mSrqQKKfNmBI1AzzTSzna50tBWYSaD0h2t9CTpjlYyuNQuqYQoxaVKAUmBfjun0LMH'
        b'RXpOLyhH9uZMqoxGveulFx4U2b0OivUivbiRwW/sXua/6D3sXv5UiZdD5PBE6h2rl6BcYjuLc5XIULtlZbRevJIx/9Mu03uicZCZfNxvOfMPeimuyy5rpP3xN0bvVSKz'
        b'Mw3I7EVQ0hhKdC/Sy+wofQBiypkMSudtGmKn7cxKFn3rrffG9873/nofO3/Xq0P+4fpefH7yhUNpcG3edm+97zj864XSTLLLyNVb39sus3vh8vA3k8jujb/kT7N74Wcr'
        b'P6a4DT6oDX4rOZTLbPfBbdP3KaTQUyr/hPJkoTux632enn/C71Ere+n90TOlD6hggih7LwK/D6o9sNIL17BCYvdxwWDH7Sy30nbvMno9bfXkf5FQCkpccF+Ug6xxkyri'
        b'PqOUd5J9jFP+EdMaO2+yEAktE5TQdnoFtYkpYLCh7dQt28RpaSZdriEtTcG0MerwNtra1eqWTMoxWqwZebn5U37BJTKERov7Z2QbMlYiu6vdNGtPeJ+V55nv08rPMVz3'
        b'JXmZcmtRvkE+3NINUIGL0uUuQD3xbLEdC2jGwlQioMtoJ9CZ7aAhFhhKZGPh7zBAM1bhf3XBPJD6HFd631snL9Tl2AxyBFXwcIuCCNn7gRZDgc1gyjDIjVZDrny4EX8e'
        b'Odwy8n4v8gLful9x5Nq7Q0pX7vse8lybxSpPN8jvexuM1myDGbUadQa6fs77eO7TI+/TQ+57DLcsUavVy9B7rLHe76WUZ+VZXf00Af0ppG0Co0lvWN0meQIDPAvbeugV'
        b'qtXSxmXk5Re1cSsNRcj+RTXn6Q1tHulFVoPObNahDyvyjKY2odmSn2O0tnFmQ77ZHII7zGMBqoCUpPBt88jIM1mxJWFuY1FJbRxGhTYh6R5LmwDDYmkTW2zp/J2AfMAv'
        b'jFZdeo6hjTa2sehTm9DCJ6BXtomNljSrLR995KwWq7mNK8RXNteShbJjMNoEBbY8q0Hh1aP6+UcuSHec68ZSsQsdX8XjXYdlCIN9oAwtIzKNeSDmxE6J5+PUYqW0P3ov'
        b'YfEbf6csRLLxB+6Br48veuND+6I/P6Ev+eaP0mMJ6UNzjBD9+qInGS1hpNhnwYjJGxmDfa+BNJKtDxhUth/jj0pE5TJk6hOWw4sibDwlwLpEk1EZh3SXNHZ8Gijr5LDH'
        b'0k/oootP0AVJK8ZOHaSIBMpC0oot4eysxatAaEXqK/4zIum2l8Uyzc7Y2UmIfszBSP7RiMcH25GsCKIOMohbskFUI5I5SA5xSAJwWFpYRtm5LBqVx6Gyg5HMYrEkQTIi'
        b'AVEhlg0CPS5PoOdQGSx+Qr9IFuJyCkbzEsacrOfyF+ixZBbYRaQuofO7gK+dlMNMosgz53zmJlEFQjuhbIUgERFyEh5OMqbz8CXJfYffKQTmGXikWYvB2sbq9Po2oS1f'
        b'r7MazLPwV3GbCCNhri6/Taw3ZOpsOVaEu/iV3phhNSe6CmwTG1bnGzKsBr15Pn6H7TeF8BHo1sEXiqMc9GmucgfSTvuIY3wItvnQTkwg447xJZD2Qd8wLiFdCJs4T6Qj'
        b's5mfRwdVYaBJidChCu6HNXjuLhRcFsDtS727GR24dqyZktq6zbtSeOY109Nl3djpZKfDvKtR5Nas9OhSiUearkKyfgWVL0ZYhjKa+yLM8EJvaCxHy2hPpBcQSYVwAsk/'
        b'upKt9MT3VTh2hkOA4OolCBxpptjtxPSwMxiHkntw42DExn1KfKD3MBCcHasMVHEKqpjF90RdCkEoz6DKEGhl9EoKgYXu7AiQEtbkScATIuQeiu/QG4amTL3sLHk3phIr'
        b'NIgMsJpVKcRI71S1EOCo5EElrJ2Ui9LOqhQiZGWRUsOZhPgevSdPds68EAsfRESkHDvnLCMKKZu+SNnkrIJMpmgljRRJmirmUGcJsHDWo+c1AhxShUgDkaWdxvmcLnaE'
        b'Z9h4aBMV6szEc8lmIVxGbNW8cpV5OsYxDY+N7c7KBfhCkNdAkN9gNivEj80m2/FWmkYYZD6qONcyDWMtjk0SY4xlZISzIe6IuFcgzZRizoksAYZDfAxZ9fd9RWLskX0g'
        b'Y4rDdRkZhnyrpV3o6w0ZeWadtbOLtr0qJKjx8JMWIQonET3kxUr8wvPPsn62TYQ7EBEyX6Te3VAPN0BRtGtWjMWSYCBqY19GElTc9+FtcOkW6bi4XHwv+VNyKd0NjshZ'
        b'2Rja6S+Qs9xQ4oaKB03wpiY+cbp/oipYIaQ81Qw8kjW8m89T7Py1PIEuBioVoVgqQ8hf6HJnpLJbxbyDA1GjR6aAxAiKy+hUzv0eswoRYhF83CD+JnBQHJUqJKgpauvl'
        b'jPebbcwxxOfp9Abzw+eQiSOPQUUiPtRh5oJ9rJmLzD8UPGdOzbGAM8ExCerYhHnYqE+Kj1WBFlg+H1YmJQdj5kliVsB6eMJjsXWQMez6cxSZev7gg9IvtV9pv9BmZ4Z8'
        b'qiChcy/woXPpX2lfSx+wO/XWB89svd3asGkTfWLD+P3DKwbvXBfpRUUAz1TraIWA9xJXDFDAC3CjCsdnFai8YT3vluhr48AGcATsI86AKbBpsnuG0AKOdJwhPOvLh9vV'
        b'6e2umWJ4CB7oMFsMdmcRa38h3JuDJ4uVsQJYC645p4uHCK1zcP4yUAUPg5pV7viefHwXCy86u6QaVx8Gq+NhPZIucCNKXk/DcgtCQpRmlxdshBWw2Tlv8ghegWwCo8lo'
        b'TUvr4Fum1kqyZUi/kdDFfbuhitqVwT0vYzHkZLYJc8jX35mXQaRmxvcFrrrN+eiShWkFdwm1jlrnu6u7S+H3QHg42k7h0ZZFlIAFqDBT6EZd7s+hbs+TfqJEPgqtyU/d'
        b'Ho4FG9jZ4BglAydZH7A7zhaBUsTA0nQ8b0qiQXFK2BLOx24hTHe60y4iJWVpsAhuBVdhmQ0bNPZAuAUlbgI3SPBgMELIGBWsBk0LguMSYL1SHauKS0Di0NtjcoqFTNCC'
        b'TeCoOFn1RAzcqIhLQHxngZOSULLRYLsQXAVnhsH6hcb/ppNZCzYbZ77z85faF9NPGE7oFt3aCa40tOw8V66oaNowbW/jrpaqlsOvlDUt4l7IErasDJyw6OXA6n+U2rf3'
        b'FUY02z0sohkiS+RbzHbZ9oqNz0j3BlGfXfM9l7kMURS2RacaomBNr/EaEvnHDaTBoZJUEk0xBF6St3vUFoFTvFONWw4qAgktRoGjqMntxMhT4lrQRIgxCN4k5cMLK3Sh'
        b'amEvVYyKoYTgCBOuERJXJbiaDqs06rgEZSyoJe5KcH4G7mIBNXyOIHUZuOKaent8ZdArw2xACmhabp7elmMg1OLnpBZhAZahWKKKic1QPKg7ynbK7SJNTAqIfrBka6cb'
        b'wcOFDcMTj9VNQRZ0MXWkIP/NPVDQo8DpRkZup/dMFxm5tE9MTOJMj/8pMeFK3N4ANzHJEkk4JqwA++HZTuQUD1p5coI3lXygtSMZjWxHegrLfyg5hYAbJCwXnJf14/P0'
        b'SEmgaa6LmBDbvvH7IQwYYKTwOkMYFHQbndnVmSKelKPLTdfrplTQTrcER9lS0M8g0xjLQ3g73KwBZ2KQidCcAOrcjna4DVzoMAHNjvK1gC3zfeEZCpyGG3qBUrChhHTd'
        b'bNDs73TRb4Q1SiJ4MmMp2Xw2AkmNzgESAqpDgALhl7yOz+ChdvNLloh6Dg0xS4aYI8PKruGSO9w/jF+6DZCO/BJrFAJwE1zX4NlFNR9VkBwTCqthfQoid5UC1hUvjI9N'
        b'cY+kgAIHDRJ4E16H+8l8SukSPMnSrKKjtTn1vixlC0MvCwuRMOxYJB98j3QHEiwyG1YrMRPMXesRCK6DqySPFJwYpEH8CY1AwrxgWLWQZ5ZY+6hdKSCVowFbCltE8BzY'
        b'UGx8cdIxymJEGcdWfnNq/hck3O3FTPUnIbp4XQ7RNpTzv9K+mv5S+mvpsbrN+hfSzxjuRX/yTjiVEsqkRJYtcET+4/vz4VubU76IHFUqn7v3aNmsvUmt9LCFsrffe6bh'
        b'xdefuV7eUh+BlBOWWl0f8PULpxUiKx6gkVp4rcvcS+/lrqg4cyyZhIgBO0ArZpoesK4T3yRMM9fPSiKQHXNAUyfWSEo7B47yvBFuWUwqRFi5HawjaowP3ICnGXlFxwue'
        b'ZwPV+WQWB+zNk2hgnWv+e4ZBjVRb3zUs6s/jI8jUCtwxU8inmLiMj732HMcgjWc9qCZ8HrbAerC7Pb5kw3g+xIQPMAGXx/5xPi3DMSNp+eY8KzH8CaMe6GTU1FrGlxg/'
        b'2ERH7JorxZMgxNgZ051HGlYbMpwcst186Fw6T/wC3i5pN+QeNRHqnC+VuTMQZr4KXeoxq+jrZOaInX/XwxzLMvRVYoUNv89DHs4/jsMbOIiFBZvHwxbBLHg1GlwcDpoU'
        b'SCxv81sxCNzIwUAOjw7kfvT9ziSi7o78L+ZSxNHFDppMm382ahfdzKZ6U9HaUR+Y37f2osjrvNT/8t46cms/Zu7H9G+BS33uUMavQ7awliPoW8S7CcPjNbL14X72t5jc'
        b'Z66Muitffmviamrp9dEtmsFn7z23+cer30sbVs/VLH117bNc8ZbXJc9t+D5K8cT0ycOvy19dHZL67d7QswG+kfeafCsjf0hYceZ2TvT3ptSc7LjM3wK/+nj18z9VPb/r'
        b'87jFn01IvnQzHRa2tJyeHjDv0ofxkZO+GbbtSnnYlMoVE2K23Ppm5gc/+dk+DzZmvvphxfU4SevTEx6wQ79WZnw3S+HFz+TVgoPSLnGloBUcIBq+P7hEEL8YXgabu0wJ'
        b'gs0TsQJzOYEUA/aAOolTgVFM6UKK4KTFiqOFxoCDy3hDgQxkwSo0lKASjRoaRt5mGKsXLoPrU4jNAK+CrdND1UTZgTexKocUHnhjNdF4QpNN/KBvRsKgfeAFVL8xHKiB'
        b'58ER62xcRjMae960WI1j9h7bumg3LYaA64SRpIJj4KSTJbkziqg+cDO8CtexsHWFkGcSF3151oVXOpCYF1ifR8lS2OAC0EyYBLKNWwX84gQSnq2GV8BRZjU4D2vJ92lB'
        b'yzsH3kplxJgKgHWkr2fjBTFdhJ4d7nJKPbjXikUQPAMuIYKJpym636IoCtY9OfshxOnxRx0AQjfv8ezAMjrMxCINcY1LQ5QQ3yH2ukgYDjEhoTdH+zE+jD9dPOB3WVAn'
        b'nVHofNfOaESPAytjLqI6WWCr0eXJjvpj/4oe9MffBwxVTWYbJGnOF2lpbdK0tAKbLoefbSJ2HlFVSX1tXnglmM5iyTAgVuo0I/+E66WJbvNwloRKIc3B8TgG2mnHiikf'
        b'hhH504x0CL9mBpzpA2oexjSZMQw1AdwQgl1gPazr5rRwTVpbcFNdjhkDq+cVJopElTJ6ttwDO2KIs0VAvLICt7Nlrs6KOtCEOi8xg+tSsttsjUYXp67t9PtmipyKGFcp'
        b'QoqYACliHFHEBET54tagetrvH6aIdde1BYlkiYsH3JnbSdPGajbYC08hy3XLZAVDQsG80avKjqmwSK/DC5g4qu9MLgaeBkeI+ilWDeuYLDQEWa6nY4RUXwuXAqunGq9v'
        b'MtCWWJRwYOStL7WLbzVgazPmUnlLWUvZ1V1GOlmkEa0U/XX6p6n+azb03TDkc9l2v2OjZsu9/mGIGBf5bvizke+Fc5FHqIisvpTK7MNUDVBwhMlowGVLZ37cHzqIQbkd'
        b'nrDiOPflGlDtZJ5CuDcR8841KcQY1QsR/BtNBHANqMJsCmkxBhac1sut2HknXByqSOrAnwhzcghdqsnjUF7HwOZMhARp2ObrZENSayVKPyniDCz2xXJfF/frhjdqd06e'
        b'ZoRtbEaOpU2cacshlNbG5aO0bUKrzpxlsD5SCeHM6/D9enwpw5dyN1soJeTVSRMJfLcHxvB7MCqYROwDx/RiLsaXJwmHJPSaa7Bm5+lJNWa7q3u6T+6WuAHCaxOO007T'
        b'S0wxzECaeDtgfWpaO0WLnUv4yAI+uBvUMtREuRAcnzuAWA0/F7D2ZhbfaXNSomZT3aZdOpNhp4kXNxlSJIbx0QvSupEhhrx7MFlQIrFDAuBOWG2BFwbOgq2eBTZ4CakB'
        b'l2GLtRBe9CwEtd75UthCUZPhMQFsngsabdhcQ/LxPF59WBUPGphEWBuamEIM4Vj0U5Wkcq09BmdgpVINWuYT12kruCaBT8PKhEculmZJoMf/wrKNh/IesH41OBwKTsS7'
        b'B5ACOydQvRewsEYSya8CPVzEr1uMxw3sC+sS4bZQ0BRMU33BJs7cmzZaXv9IYIlHSV/qU9+n+hmv0nDps+qFq8MF6cfO+nhUec8ftO/u+0PubP0062X/vy2TDptS/ffN'
        b'k/1rfhz45vaAcW+8uuvMtfDcvdNzbIHPyuY8X/Dg+b2+8/LHKwR8TNZ58JQwNAPuVSvIEjAhOM1EwgtexPmUZOsfivGNgpfmUtw4Gpwds5RYTmA/qJIQN4M/0j6qVSQR'
        b'4qHr2BVI/aokJZtKIF7kVo1VFnbEeIobT4OWRXA7rw+hkRc7I8Vo2Ap285FioAU+9cglQp66/HwDokDMCQh/8XfzF+k8jninxGS9EPfv4hDEJdJyjBkGk8WQlmnOy03L'
        b'NHY0dToU5aqX8InfcfHSfApCsxvQ5S+dmYhPcw/mDJ6UFek4TZIKa5rOoU4EtUnEI4B+eTnd2QUCtzg7CDFsvoP1qN+vTfLJjfYg6wj7BMpDERHtwT0cOZahBHA/DVrj'
        b'4omcGg5OqhHltKwqhK0FUnF+gbSAo/wnIsl/jM3KGkRmbqPTOQtshS0eXoVeEpkYnl+FcrQWCOARcJwa5suVIDuqlizeg7vhOnhdg6QPGU40Ws2WeQxS85s9ybKCZGYW'
        b'OAW3IIKuig+JU4KTcOsqZTD2NMTjxTPEVyF2rgunVysocARc8JxhHW6biJHhBNge7MwMDvd7ZH4KbM+RwAqk8TtsmPciK7p5FajJLwD1q+AleBkxGStSlS8jVLxsE4DN'
        b'86lhyRxYNxCUk3XdoDzYQIDdocE2PRKK8aJo8BTlDTex8/vAkzY8I71kGNutxFWwRSoRpiRTw2I5ZAmcghuJXkyWbU4GR8FT4AKDdIabFDWRmrgG3iQ9lwHPZcItSYlg'
        b'iyoWbgfnYmJFlHQyA/dnzSZscV4u6glVWi+8LFKzkG9xB0YHLhKmtgyuE4HrYH+oDSNl72ngVLJw5UKKGkYNAwdTCevf+qQHhT5m/6zVKtnl+XxUbi4jpJCiuAgotPH/'
        b'mRaH1GPy2lNFgnXlw4Ra6Q2ftXzaKekkrXxHiDZ+9JLelC0SvXxSIscmXih2IFURp1GVAq7vCcQ8UCougddBs3H/tfcFlmhEFoWnn06YOzERRvvZ86bW7Yu627ty5ixW'
        b'dPBQI13ANvgIPuy9fb3fi3Xcq6ayTecX9F/3oTqgdHNoPlX8bMTqlSOfaE39dmPWR9lZkcEf91k6SlBfTqsCT9Tt9AzzmvmRts/3v76uOBcbuDN8xk6jaEqE1/JKgXLz'
        b'k7Gb39aseONfxya/6X3omuG98CtxScy7X321+tw/L7z13J7zP197ozxJseTJpr+trnuq6ZnZcdZPVWlNM/oK7ka2SVZ7rPK4PI2dF5a19+KAefQTUdp/2S8s+dftD++3'
        b'XvjmU+veJ18+M/pNb2aRjeWqF6r+e8rnHq/87cD7Ae+p8g7bB6Z/8f6Kw/9pGPnL6SmB9dk7fpj68tFev6ZOOLZD89qtNycYZ9aO/vSbv81+/SP6F2X0zKxfb6zfdvOB'
        b'+J20zyq+GDdi3pN/+ebbX4/vit79rGzMlIwnfmVNI20Ty19VeJPJNhocgjc0SBc9ivRNvIK2GvuPPOF5ltEjfooDTOHG2fmIu9AUU5gyiZ4WC9YTtW454iI3/MA1novz'
        b'LHwyOGTFIaxR4CmxJh5eBDUhav6zZw4Dj0xeTb6Cw0Yr2QcAjzBe61mTMIYpGQl2EH1SIIVPhyYFw6sYFqyLiBA4NxlEcltSSPYCcCPJxd4xa58ItjFF8Cm4i3B/Gzj5'
        b'RChCpdOGWGUsEiKwWkB5T2Izc0EZP7t4IBbu0eB5UlS0QpWIsDUgHuwQcdGwGVwmFcCdmXBz6PBe7ZHRdYwK7ID7eegPTrOBHWQVHzLva0QUp6LBGTM8xX9dBypAGdgD'
        b'ngqNS0DWMjeYBvvAUXiQ99fthGUDnRHXmBujEhB2B6Ce3PQEF7MW1luxvMnQwsuhy+H+jmIzLYePpT4Pq4O6BVPXjeKWwxvwyKPcfI9n5Xa0yPv0KOOIZFyKLgzNy0Zu'
        b'No4bkxL5iCx0RiLxYXyRjY7uGB/Whw5kXDETUrLeVkL3fyAl8V8MH3H2s9TTh+FE0vskbuwBJ5D+Zna4RHMT8wcN9Q5hjbiQ211U8Ws9SFE8W+iZEdBJimZau8tRAbXc'
        b'KgbbJvRy7gKig82rYI0GXJ3QPktXOJVwZy3YjfAjEZxZBm7GO7234CIDj06cwq90vwLLckMRBoYI0RgfZODVJyPtURlsF93P36X/LUeXbhtIUO4tJOhOm0gwjj6Z/u45'
        b'CMFjzUFkK9i7w9DYSuQd/s03ZBktVoPZIrdmG7rudKSWdEoba5UbLXKzocBmNBuQ9Zcnx+5elBG9xbvZ4BWx8jwcOJpuyMwzG+Q6U5HcYkvn/R6disrQmXBgqDE3P89s'
        b'NejV8oVGZPPYrHISkWrUy51ISaBylY0+WIsQCJ1KMhssVrMRe5u7QDuBRN3Isek3QY53c8J3OEAVF+ksHrWwhywrDUU4iJTP5XzoklEvL0R9hmDqsQCbBX3ks7vTz5oe'
        b'OyOZfJEb9RZ58AKDMcdkyM41mFWxMy2KzuU4e9sVP6uT4zaasnDwrE6OQ4sxOK6y1PLEPNRx+fmoLhyL2q0kYybJxXcoGqt0HQYIjRUaG0uG2Zhv7daQbi4SGdXVTPFM'
        b'tOEF7KAxDFxKDnPNEs5fGINU0OSYOMH88eNBk0ICrxaNB9uih8TB6+P7ULABnpAGhU7uRgY+rvLndyYDykkItJsQGId3ps8fnH7rFnpHFrh1a5IqEaUj3KV7tGD32Amn'
        b'I8o9F/i4ZmCPLqju6/cEzuXfmFsb+zWNYCzYMZn49r4vtarMWJ008572c21u5lfU+Wn6CTMiM/omB83YlC0aGnN9y5j6q2VjBsSsCreFl87cHbQsMP32ymfurwgcFnSr'
        b'eNfuIE1QjTUo6NaI41nrbweEK7kLOYGSf05YFBCu1mv197TCXT6v3Nolo8oFA9b+bZmCIfbcPG9TqCo4RsVkw6cQO9vNqAKnEmk2ETYPDgV7FbAOq9ecjYZVkXj7oT86'
        b'MSVIW2XW5XeZj0KiZzhHByKhIWR8aD/E1X1JaHKxwuzkWx1C7ZwY3uENLtG5vwAf4douZx4BWBPNZyBCphpdhiDILP3dQoZa5/9BD2JmMh5FsC831EUOeHk0scvGT2lf'
        b'Hd1uxs3yVYTFKfHE9AlvIzKUjj0i0owlbpc/vka+m+dBQPXkeRAl2nAAMTgrghWR4aNT4LVRYyPGRILLoNlqNRcW2CzEMmpFasol2AIvwgveYqlE5uHlCepBJdjIIOMM'
        b'XvaAZ1h4jNgFXxnjqK3U6/liH+2K6Ysm8sZCXe9YqoE6MYfVaiX3R1qcGJ51ZQ9DlI4Nf1/Q5/lGr9JwH8HrD85lTaDl4peb6XcP+C/tHTP34LcLEp7PHnf0xI4d96Lu'
        b'KhtjdNv7PH+9psbBbBm2+NrdVaWnjJLLNzULn3twOnxnYvaw/Ttb33z/yuDlg06d9hvyzhaEzFi3zYe77EjFNEx2K5lMkQRph1isj5GCa27fA/E8HELqYAtq+Onfiz15'
        b'dCCZOc+alo5tbdd8ggvDIzmE1X4Er3E4frHysXDbWZxr3sMdwP37IWYkRTtm16JLeFfM9n2tB8yehr6LgcOvO2Y/BK9hdRioSloROGosSxWCGh+1FWwiw392EerWqGIa'
        b'+xk/nGajyHLR0CdhGdyCMBJZgZvUlNoYTtLeTkB25SQ9Tcm1OT/5BfL48/5SjhKP/hdHRWvjU1RzePwhX3YOElM+ypUcpdXG317ptGMHTEI4GLhNQPlo4z7oK+Bf1o/r'
        b'Rclz7giofK3yh8gUive4nURtqE1G1tLWlDFGuDccVnOUcD4NTsO98CrJl5zWjxqtV9OosP7581fyhV2f10KXIhnxneZ27qKEu8N5t8dWRCUNOAxnawpsgtdgrYBitfQU'
        b'L3iGyM2x8BTeIq7dZs+ErchsgZXKOOycxCYMibOA9aHYDABVoRJF8hIyl/yPcOGC75govEum9M6ij9JSKLLSm+0/Uv2Lr88oWhuvMWeoxuXPfW1s9YjDHL8fShk8gobr'
        b'Ao33/oGXE6gEVPhJAv7fF06krAteZlGbfJc+MZBv0yrjFKqcooKjF48sWrRszyJ+i7++Uyn7MERB4dr5Mwr68ymHjVLRWobyuTW+NWfnEKaYvNSK3qNbWSrmVkCbbZH5'
        b'7hjyMjVrDr2VoaJvpVwp2jm2wpu8/G6YH41R8NZyjxWB4ZU68nLzMiv1HfqN7hdYElh8g/c8rDMtoE+oMxGcOs0H8Vl87T9ENNDBLBV+a8aPq3ZKvMLIyw32RdQVpFNE'
        b'l7yVHjhCsJi8PJY9hI5nqKhbif6Zi0QDQ8jLRVEDqZm4maaPbO9r7JPJy6+VCfRB3CLbobyd4jU55GXNIn9aOWI7RsWSm+OT+dqPBbxBH+x9naa0urATJU/yL9vynqUq'
        b'VQ9QQ7VGOM65xnmbrYT6JfvfQmqu1j89Yxj/Uj31Q+qKxy8selk0I2wF//JAtpQK1BbR6GX8qRJn9p/H51OlaOzy5+nXLuiXs9T4ouZ9xrIbvSmqn5cyN7bu7WifV06/'
        b'Whhm2nC7do/h/R1F7Jzl0YN8RKbG/WVHt2cPHTz3nRdLV6qz92stH1d+6n29bFz+XVof5OGxbe+mXn1ee+mVRa1Frf+1LVf20fykG19eWPNR2P1/vjZt2tpXZsxPeLrN'
        b'GLjo7q93HccXWe1PPMucPXZh+mrFdb/W9WPbjniX5+x9/9YLc2QhhqEC1YnZ6f/163uKlp3py9/aPWHb21nld+SvNa3//qstE0Ql8y9GNd/b+rbm2urmX5PeWz70b3Or'
        b'+yjuPjPz+zHHvn72Va+Ly/RXZg/PmQoFN6ZOU/z2zoZ8477flqaUpydMTIl9+qP+6kN9X4kpu70pPv3GT5fmOfIiBvVX1ysvvP95xbdveQ1Qz38nqmb2tS378wULJw5Y'
        b'+vaVDZKVS+fUepk+HmG6O7auQLSqwPtnw2bR8ruNHpdzftpk/f79fpPGn8n4721prwdIdo37OilmTphxrf5e7k+/BSRPmL/qTsEL3AHJtYWtn63y+yzq81/G3ygcXN+W'
        b'9eL3n15eNWXlj+MvX1AcXrtr/GeQaT1apdBty1n20/m3lsQVF9wXxXxc/dbTZQoxcRkMBVfBTt4psADWuPwN8ORyfuINbAKlobAyDG+h1kiHhMydAnZYsWoqAIfgidA4'
        b'lUYFjw4NSRRQUiGDvQDwKik2CZYrO8mpeHgStIC9eqKVqcHFUMQ3kmLzzOA0h3euG7IU7CWTgbDGgpiJWhEX6tx00hs2BcNSNg+ehZv5mIRKUNsnNIl30JRGdPTRHFIT'
        b'P0XoEkOXXW9wSBI8IwTN4JDpj8YI+Pzx2e3HVivFLtFJ5G52B7krHczR/oyPjJG4Fn7LnBs64OURgei/L90ficH+DEe24pHg5W60L+uPZLWEZn5jGPFvHMuRKCns+GB+'
        b'k7ISlJcjDhDuQXHfh8txXikVkNUsbSKnidkmIHZjBwH+P18YiBRfskEUWTazyS338aLAAV3lfsjdHuQ+VjvF8AA4QwT/AssjRb+AAg6AdMDrsBmsJz52G2hdROawnI5g'
        b'UApOwspEcMbpNQkDrQJ4GuyEh4gUVoPSUWTejp/ouAiOLkcKiw+sYAdaQSPhhr9msUQ5/njsCunh4l48i0yNIltLyOWpJUpWNJ9/WTiOOKZ9fJ7QK+ms2ZSxfNNdmgRd'
        b'3f5p0JiNCbL10dLZS4QbdNTaiOc8V9P1n8z32rPhinDHFyDC+Jl/cXLoc7c1befOHfjlo+Wl4R+zhuc8+iXeMb8m2LH0+/Lj1z8efu7abt9RSQHfCed7LymIO6ynBy6u'
        b'G/HuG7c/PRlQ8CbX+z8DnvWeSMc9/+kXFVtfXDrpjhe3FPab9/Vv8rNT/zP/mbFvrM2pLdTuiWsq+u2i7WVr4eEMj5++Ox61lvr+n2G2KWcVIuJWXCRmPEPAucCOWxm3'
        b'b2PMgUP8dNwFAWjo4LWMH0iDM/C6hhQRBw74dhwlEtxY5xePZwr3c3lzzITws6aGdEw0B1xB7ME3hAUnwsBF4r0FVdR4nMQ1el4zBJQMnGVnJsFWnrs0gjp4AdSEqRJV'
        b'sDpeAXaBaiHl3Z9NS4fH+N3+NoDD4AqoSXJqO2SOxgR3Yi7SD2zi0NeDYJfLgPT/X+cNj805XORLOIeyA+fg+otphhlBS2eT+Eh+SSyDg5bwlkMyzC3+bd7iLq0et6P3'
        b'/zXgm93EjWsWdSXusT/3QNwYbRIngUanUg9r5DiCw3ssmzl7YY8T1fifRUq3x/jo6VRWz6RyejZVoOdShehPhP7EWVSqB/qVbGW3cnpBLb+3HA4U4PRCvYgsuvI0SPVi'
        b'vUc5pZfoPWuZVC/0LCXPXuRZhp5l5NmbPHujZx/y3Is8+6ASiZsUlemr710uTu3lro121+an70Nq80XfxPi/3r8W7zOHN10M0AeSb717+Bak70u++Tmf++n7oxr6OJ8G'
        b'6AeiJ389R6LcB7XJ4nm+nqAz6bIM5ruirm5W7ArsnEZOQj06JXpUDqMF+/yI41VfZNLlGrH7tUiu0+uxY9BsyM0rNHTwM3YuHGVCibCP3+nH5J2Ibv8kyaGWz80x6CwG'
        b'uSnPin2vOitJbLPgbe87uRQtOIncYMIOR708vUjuXGisdnqJdRlWY6HOigvOzzMRp7EB12jKKersaUyx8M5nVJXO3MFfSrzKq3RF5G2hwWzMNKK3uJFWA2o0KtOgy8h+'
        b'iCvY2QvOWtWkM61mncmSacCea73OqsNA5hhzjVa+Q1EzOzfQlJlnziWbPMpXZRszsru6vm0mIyocQWLUG0xWY2aRs6eQuO9U0P0B2VZrvmVCWJgu36hekZdnMlrUekOY'
        b'c8/4+yNcnzPRYKbrMlZ2T6POyDIm4g0q8hHGrMoz6x/uJZpEOdcjkoVdmYI/viLxfkV3T7TJaDXqcozFBjSu3ZDSZLHqTBld5wrwP6c33AU17xBHD8YsE+rDaXNj3Z+6'
        b'e78fY3tTIR8cFAVL4YXu61ago/siMLAOnLfhfXqQblLNC0uslICjo7BeEhyjVKthPd4ieSzYIXxyVpaCJhrJeEuhBiVIUuGlE7VJNOWLd38DZSxcBy5NNQ4O/xdjwcvy'
        b'Xwk5iJeKBaej68KB6cpPv9DGONc9qP2DdXE65kJQQPiq8DD90lvnGxq3XC1T1Fwsu1oWUaOquLqjqWz4/slk5eUA6sndvdZ8qUQGBA61gAeW411/nXK5DB5yCXCX9AYn'
        b'IL8Nb/zSOUQ4w71wg1u9IuI5rw8/v7gR7PXxBPu9UKsVbj2iD3BwYj1oJI7evn5weyisi5HmjeYoFj5Fm7JSiT0SD+rBPs1C+DTfFTTZUw316PGZxKcGT3iAJlijUYnw'
        b'TtfwNKyiNeBMGlFNksF5cC50KIK9Lmb0qDEsJSqm4W5ORhxuMnA9krSuMiEemSA7hBTSBml4dRBscq0feIyJQBxE2yWihyj5fmQPTSSS/enigM6o23mpZhMfO2zeSVGP'
        b'XKHQxPDJOq/VrGZcvut1rv9+P/QQFvgwMB6+ogprsnZqhWt7WgUO7XXNYDXRPBidV1eZC9FlF+PcnVZIdavUtfjqftBDp8ZQNaw+L+OxwMriwRKnOW0Z876HwLQXwWPG'
        b'Gyze9+swPeaaZVP/scowtzXqLQ+t7IC7MiWuzKXQ9TAbl5FjRFxcZUHMXPGHgPBMM6zON5qJoHgoHIfccAzFcLTnwJKoa8d3rt7F3cm2kYS7O/fJdQg6cPfHmwXoNvHU'
        b'adehjnwVeyayF4AdybCWo8CpQRS4SCHyPzqFbAkPm8fAVnAKgVlCjQLbSzzhQf5YhgtIty+DNbFEpY/kKHh4uRjUMHFWuM44bPIwzpKKUqmr7wyoedHrllzKrfIany2v'
        b'PSrwG7Yi/Jx96YbPR8vODaidvLVQuct6Paf/3CivLb/Ghqie3H1le9Mni8uEG/s+WPT5nm97l8VNPRS1cvfSMTeUg358ofbNKT7+QWzGYYWELL1YEIMM1BrYAPd1tndc'
        b'7NIOT/Gmyn5YAUuxozWWTAPAU2C9GD7FIGbblMlHilwF62LcsSjgCNhKpgq8JYRTxkychuwx1sJHBiTSoHlqOOGUcaikU9g3Aw5GtE8jtICdfqTUCLDeEzM8NTiKeZ6L'
        b'3yXP4yNMHIidb8Ah5A46DJzgKG4sDa7PgOuJXwfuGr3KuTKemjKRXxc/YyWpFZ4B1/w07nM+ClBj8KaXLDxCWpuqhE/BmhgjOENWUPIs3BecYuEGs77TNnqPw28R8RlM'
        b'GeaifCthusTSaGe6CgnZEoj3mZD5um48z5m747KNx9sl07l9cTvrPY4uR3tgve8/Dut1gvF/plBl9ahQzcjWmbIMfMiFSwVycYEu6hXSkh5XszIZVj2uQoWb2331KZfo'
        b'PDXGF2wUdtJ4TCzWeZC+I4SHjHa/DwWWHJTs8tqAPq8M9gfhfjPf2PVr2m6J/zO+17ZLElMSFnDHmLdODhHSOYPvGOHVz+6M9H8h5G8jwrZumzvv6oyGrIm/PPXNBztL'
        b'YMCzAzw+6j970ieVK2T/+mnY9+Mu+5nfk+2QRPxcdUCelg7K79qYX474L931T4UH7+TYBM+nDIBXsYbi0k/gbljHRwZX+IwZhZ0PSXiZKzipDKYpGaxlDQvnW/lmbYXn'
        b'yMETLgJYanKSwKAFpHgj0iVPP4F3lwhDWiRNcWE0YmpXWF4P22rB6zzwfr+aJFArh1fD2jXGcHhQOH4K3EqcuisywX5YszTQqQzRGlgKHDx174Mn4BXStzOntCtRfXnO'
        b'AM5Pg02kaUtAs1tPgmcZ0jzfWWCPS1EiTANeH4n4BtwFLv1x+vXOIDiY5kKYHnQnyQQZifnq/6AvUzywC+V0yc6XvPuhZGve46bXJnRp7oFeX+2BXh9Rq4JtE2bnWaxG'
        b'fZsHogirCasDbUJeLXj4MiJC05x7CZHAvYRI8FhLiBBN351OdzHw8b9pej02kDAddtAveOPSLd0fSsx8Q3hSjkH3sTNdLCFdZ1rZnaDdPMDZbj7nXP4RZQ7W2EzINFXF'
        b'zuwhuKhDoJIrJzbEcbZOgUmKnuA1G6w2s8kyQa5dYLYZtDi+iN8wQa+Ua2frciz8O10OeqkvQuoO1rpM1j/Fk9hE45df3mMt2IH91uHyL7XLb73+zPvPvP3M+Yar2xvL'
        b'GsvG17TsajlweXvLhoiapg2N9YP3rqsaXLFOIN6zKyhofZA0qNrwUlBQUHS4b2Vy6bIT6XuNVPyrXikqHwXLawEXQfWazixjCbInEdcAe8YTwQouwe1gvZMlwP3gMs8W'
        b'+oObZCPdJ8DlTE18LKhKSoDV8WpQh12fDESZKAXYKEDy9nrSH6dPmU6vTzOkGzMsRMsl5OnbiTxlGjzvMOxB8YAuRNI5J2/cCHmBeRJfTuHL6c6ytuNxG1yHZAXutIR2'
        b'z6LLjR5o91ZPyyJ/F6z/M+osR9Q5pyfqnE/8Y4hATTxG4ni6DmTawTP2/z9Cxdlik5PkvE/LyrvAiOGRaTTpcuR6Q46hexDg45PoF998y5PovN2H/4ckmr5XRcV/6ZUw'
        b'xXLqNUSiWLPMXzi5A4GCk6DUKdfDwW6iFcvBsSSePmFNhlNqD51mJRv+HLLC06FxsBbWhmkijKC2E5VSU0GdyBfcBFv+OIX24h2ujyDSVCeRdtHr1N0y8yWf60KM5mY3'
        b'7Z1Hl1d6oL2WHmjvkbU94lAi2kF1OJTo8faHx77D9B6ojqAgIQ+TLTcdURrCug5O6nbXb4bNbEZiIqeog6H+ZxFSl3mLs8SgF4JPzPjco+aGRoKKET2jYtbgDsg4/OUO'
        b'yBhEvf+Z59kDcoSKZN+PTYPgvs7SAjyFeD1CRngelvE7EZxbChqd4gLpay08PkaP5/HxaRWoQEpkGLJKscjQSNrRMUSI8PGqSA6vgV1dDqTqEQEz8mwma4dBtfSAgOL0'
        b'hyBgt8yuQMmCh0oG3r9BkLEVXf7aHRllhx4DGbvV/H+EjKaHImN7DPVjI6I8OATrdUaTvHCsenRID5z68RBzxJfbBAQxBwasfAzE7Bkt31ZiLnmH9Xypnx0hJoldu54E'
        b'9uLlcN2MH2TSHCRWyVLKD2ElaObaTRtNuBW7w0FpKItD0ZRqXouBV8HGDkgZBRxCcGGm4DFw0gd37KNQcoUTJQd1QYyueflyLz4cCy+jy997wMLdPe3y9YjKFAFdF2OL'
        b'0tL0eRlpaW1cms2c0+aFr2muWZo2T/e6GaPevBdnasSXw/hylHK6hNvE+ea8fIPZWtQmdvlVSUBGm8jpu2yTdPAfYlcGsY+IokU4PqE00tA/vRNEB2ckPuDIhjsshuAn'
        b'x3CeHN3+X8z40YyXkGZwp7E9//pyYk8/Wir1oaUyH1om8xWT9aC9FoI97VEb8GICMpLj4Y6ZSUjIBoN1grXgKtzZbVIHE360C0M6zykTXzfb1tu5JMU5emS77vvyWavx'
        b'TqLYgZqB15uYTViZ66C8JSIrtPNomq+4e6KLg/YWunzJuBfPoz5x7odxER6FFe3L52Gzq3U2VcjaeDJzEicRgfqYVTa8EdxS+PSkyPDRo8ZGDAbH/kzQNDyc3Y0Terp4'
        b'CB4w56oDqvMRs+1bHf/ZZei4ou5uYGmigiUxNBIPTwqLLh/JuJz3p1WlkBjUXxgRhXQzOTXinUF3AoNXLaZycGzxhQGTBJ8HPhNqTXrgOW6+eWHjlJSpcxfaIgTzRg+o'
        b'Lcge1W/xhEFLVsXZrk04ljJz1r8X/9jvQd9XxvUtLgrVzROLVvr9ZcAPDJwsHe0XdSWiYvTzJYUJUcPXBveeGJyyeuolLs33aP65QelpfzW2ioakHNEaouJWvuLxdezk'
        b'UK+A7EVmQemQT2cWSr6wFOYHB9yZddIzyOva2gfIvMg36r35oNzNNIPPon2q0OWiJv5pcArwO6d52UhgUdQOqVYp6e8M8qxV+FLI0Iv6htMutRTr+JcxSQGUEuHLFLXW'
        b'PnTFEIpsu5cPz0yDNQkqdWK8MCIpxbVjGqzXiOAm0FQEq2aBbYLhFCgf4QEbJ03hw5lH4SPbqcDbGm1OmswZQ/paHolbog7KtcqY5cH85r3Hnt2dQU16H5MNvTLUeOjF'
        b'L2kLXgD3nxTx8NoWGZRLZ/5lZ/lcm/cJzYOmp7W2z/1t5UeV36TdOvBccM1LO5K+fe1a75Ovz1qc9+qAVf+UFZT9dvpmdNSMX9nakM9PfnCiQekxaO2kp4etPHxg/MLN'
        b'8sGNE2y3x1xLtX45+61BrTOKHP9689extS9d8hn1lSmo9lXPyC9zQguiMuLXDL6ZtH39iEyjl4LjneYts3prYO1gcNTpiSZuaE/YQJzz4Aw8D9Z5hiwW9xzNBC7wM5Wg'
        b'GewGN0JV+Bhc3IMCyhNeY6Lz4WVQBY7wvvCDxqBQWB3SD1zEnjS8xm58lLx71Puf3Vm5474BZouuk8MbbyrVLtE4u4S4urGz24eREz6K783AVQw+8B1HHXRQrP4sWE20'
        b'+Vk388IV/NRdAsodPUT7kN0X6uDWoNCQRLCxXU0oCKb6gX0cOBU9pRv/6Wmryw78x73V5Z9e+9TzFJTExXscaifvGbvRv3jMizMJ7zGVYN4jtnuT+Pe02Dd43rNg7WTB'
        b'YuqdCPP/p3hPZV6yB2nKriI28y5RCrXx3xlFPJ1PHOc7+1kaM3ftJI5bQ5mx6ku+vLOQW72aRZgSrY3foM/hX96wivw+ppCRIddKJ6YNpPijFKp7wc0dZt1k4TxTa8kx'
        b'3jtYJLDgzbuz6H+oXm7xguFS7uzIW8eXn/9k7L6PU85XLJR/cMSSu3B66V/8vz/WSI0b9svP1omDKz+8uSDo36XHhZ+tH/fz8c/6xF2e+uzrb/pYVtzbmHPtTPXAn6r+'
        b'Zjo+663+f5e8fOj08f8M/+3jf/UtObvz8tSQwwNiXyxX0Lw3ez3cCRo0rmPl4TrQKF7GGILiOumRfyxWuCtN6g3tNDmsE00iqvQW49MnCDViupTygbm0+Tl3QfBPQHDb'
        b'TXy4HDHrPLClnfiodf1/7IH8yAzp1b4RPPXFJvDER+dR/bQcaAxc1m19Iv4ju4/GIKqsFPBHA9jpgxSmuUamhCH3rJ5D96yVxt9nUsvWL2VKuBJ8fICgkrIy5BSkMcUi'
        b'u+Agqxc00iWChZRpJd60v2g0f0IU+YLPjkLEY1q+CtGreTPJjXOm2FnzdJRC0MifEiUk5254oTqEJaJK2i7ChwvoRbUovV04CZ/9NJnkFaC8FpRXi0+5QHALEHwCAh/O'
        b'K+6WV4zy6k2DSF4hOd/p8fOVVgr5tOiZsuOTNPz4gxTImUuNdkrvEYSYivN0X0ki4sQGQ/5sM2ZpC+4LbNZMVZQZMxmEl8/jccUfzGTLdbyNhUJkxmHjbR4Gky3XYMan'
        b'bOBtyNuEeKt8vaFNmmIy4huimvJ5Z/Bo1b7jZXux5BADsgBrIb6MwiXRK/7oLllSfLyNZRS/Krgv69yTSczyS/RlzqNe0O8Djhz9gleW+eEDXpiO9/wdfzQHDpMhwU6q'
        b'VcNBdS/+yPuxIXiPAhL/Lx/IwZaVUd1CI9x7fmPPhx2xcD2dTOHDucgAMO6DL0hXmie6moF3BLY8xIb0Io1Ls+al5eSZsiayTtUcx9rLaLLDSq8CsIuHENSBRnsYrOL3'
        b'WcSKFjUCVAiKwDHY2u2AJXcI2WgCq55eSZuF2NLQs3Z8LBat5w5S+MAlBLnAn2qk7XQAhUUbfkOQR+hsB+bS95nhq8nSs88ZvkGC4kxjTo6CaaNNbXT2wxqH24TbRho5'
        b'HTdOQoaOP1dHzJ+LEgca4HpskaMWgfowcHIwbmISabKQGjEQNbCce8QSZbrHJcqP7T7pvkTZXXyH9aLta+/mrSmgPkZacniGxT5Qr+VfDo6+jZCBkjdzS/SNXDj/ssJb'
        b'RGLyw0eYhao1CsoI4w/yh7D4fbjqS+0y7BPZcrGsqezirjcqBj9xaXvjhsayxo0tMa1lNjrDa4bk79Mj2WOJ706v67tBEO8ZVJ0y+NAA5YBXxkhf3aiI9432PcQEPyce'
        b'NbxisTT4Uun4CsPgjHA2qy+lnh8UY61FWipRHk/CI6Pwiua8YWR39N2MKt95mD1sHgLKXQcezgF15MxDBu4DTeAmSdDLLiD7m1TF4z06buLDCj3BKQaejQGn+H191/kg'
        b'2+5UHNnI/vhKWIW00zXMELAdHPnjC6N75ebpx4/jDxJJ0xuzjD2FXFBrxfOkJM6NP7fEnza/6y6m5nEq3OiqkGTU9CTW/HtwNZOdNWAjrEMUV4N3km8ZTTY8xuc64eOB'
        b'SR+BA+AITUWB48I144Y/nIVgtZhnHFjGNfIkxyS2CXSWDKMR6b0vUS75O6xzH4myDatzjJlFKawz4k3GkkAGUJvZj0z4L0MDgfdHAqc4ZEhUMPDaknEPBwTzQXxyDhGB'
        b'EnzcFAanxAkcCf5iEs3vUUQZn+0C6vc2HvOwmZwgpmIQyck/LI6Q4bd0r40Ex0NhLQHVDWfvMeIFLNw3tPup9b/XY+Uu0MzvP6y3PNLHjubPSdOhksxtlPPw+PHQMVIz'
        b'KjLWHUPkDVt6D2Ynwgq49X+js8x/fayuQtDxojUTQ/chhg6PpRRUwaMYPJdCKRNDBzzLRoAWUNctZs596h/eYkxPI96OFSbK3MeKOT9bxiB1giph+YPA7EwAOVbMIrQz'
        b'+X3tND6Wy3kUV9uw8IhRkaPHjB0XNX7a9BkzZ82eExMbp4lPSEyaO29+8oKUJxYuWpzKywHSzURloJF2YCxEhKvg2oT8tEebICNbZ7a0CfHuG5FjeUXAo2vTI8fyA5PL'
        b'Og/sISvM+IPbfpOyNn6TILAD7tCMGtse7OWdCfcFsBPgcbjv4QMldSKLnj+OiiDKXRcAiC/9vUdUiRzLD8Yq1rlLv4TlrY5r8IoBA+EeDpsCHmHD87IJLk3KhA2hiQnw'
        b'xESyURo+1AdcY2Az3Aq2PMLfz3Ty9//JI9J7Po9EgCOcCI+/OgxW8f4HFdnR1BteAesXskvgYQUf47jzSbAbmVF4OgdcXEItmVRoDMpMYS3YXy68o/5Su4j33W8YXNNS'
        b'FlHRsiOiInbv4J3rPpt0QUAtiRGKst9QMHxgXlXvgFBVLOqHGnBUFiaiPCIZ0AhOwzI+AGHjigl4Z646vANRQ0AYrE5Q0lTvMBZui7C5xMVDlAmjJS/Nasw1WKy63Pwe'
        b'XO1EMLA+QvM99zizbWKSo/OpGh0tMtr8uasGks/Ouhwe6zr+lz142NHox+xm0iCkuSC1pTyLdHIs3IhExQizYC24CdfN7hZx19nTyToj7jr4OR2029P5p7e9wOqHdzes'
        b'6JVIVkItTIMOjdIMjybiDfU4StiXwVsFVvEOubn+2N/nE25aLjKuXECRo3wHgFOhkaNAy6hwaggF9kaLEmmwB94AFTyOnbXBg+jzpVHgIjeEmoe3St9Bg0vgGErQCyUY'
        b'B3eEDKHJtgdqSg2bhaSmoNhAChkf4eGJ+3pnj53L60z/yA6m5uKXg1+zNCSPpUh+GTVx3nBwgSGbBsIWsJck/fIJsplfePhs+cjZUQv4/OusxMkoDxd+FGPXWNEgk4O3'
        b'wI014KQmFpxWzoQNQorrT4PzC8AhkiXePo0qxQrdYmXUurEj+XLenDEFcRAqMHzxjz7PpZr4l++u4RdZhj9RqZkp8aWMv779Bm15C335hPt2VuKrcew06W+bd935vO5i'
        b'gHfu3+DhvLvTuPppz0z3PiXf9srtaTF9SjZ8OG7M0aO+N31++S39n8MlJt2L1Y3fNzePmp59qKQl/P+19yXgUVRZo7X1mk5nIWRhDUsgO7vIvgdCSEBZxaVNUh3I1h2q'
        b'OyyxoyhodxMWN0BBBUQGBMENEJSRmSrndzZnHNehdXR8buM44zI6LplR3jnnVnW6SaI4/7z/m/e+Rz6q61bduuu5555z7lkKj1o3Tlm3pfXc6t/cJoV7TNjdWPPpnv5X'
        b'vDBzS+/FdxX0tnnXnrrk8PEfjzz2QKZ27uXSyadrZr86c+OXDxxr/9m9N6R92mvNmxu13DMHpvyp//R3e9WNvnzHNXMT3ruy+PqVN7+/6I5fvzzg6w07h97z8LPr/nr8'
        b'xWz3zWPqXjm0rkdw2HP3/fjUTx99Qvvx2Bv+mPjNi/0rXp/64qvX5pnpkPcy7ey8KOpTN2jbULSh7ZVoxU/Rbs7SCciB6pMVBgGpPdXIFIp2age0XQXFYwOxHui0PdoB'
        b'oh6TtBPaYx1qydPXMqVkbZd6knlQPaXu0k4mxJlwFA8hIw51r/Y0nfVpd2uHluPESpxQx2ubLVPUO0wXHy3v3yEzTWyC7c7tAhR16SXDRxBymtwJOUmJurk0bnFiH9jm'
        b'zLwkDAQG1k6xIzP5PsSckoE1L3yl/DmKyJjPk4i9xqtUu10U/bIDn/0rseoE5UOOi/WOgnXd0jXyy/57F8gvG3Ll3DC+YE5hfoW6pdqO3MFW9Ynho4ZL3GBeUrevUvew'
        b'zeUJAIazSJ4M4FTgT0arN1Yb5pX4L04fCoUPIR4jnoaBfcMolSFkVk0BSUkPmOC/BJu6KZNLg1wZkCcg7OVJV1nfQ0OiLBrfbRBZJGvIJSojQtJejCos7hOgZEZtSxWd'
        b'uOZo+FWkPSgssZ3xxAEoMIMCYnYblJionK43L4pIfMQgKvpwLdlVDV7gcJiKUleRlBlpJUZMzU1NbkXBfSIiEcttjkh+91o/UCtYhK+2xR2x+dyoOeXHMMFramX/SuWv'
        b'mF+U3Z3DJEMDP8b7j6Kw64hty35Rd0SO8hUreQHox0vnJRFdGxK7nqDuLVaf1E6UYUT3+YzxadM38v7afZJ2XDt7fScSNTqwOMNIohIVzQEV7SDJHsYXhxnfi0MNG5Us'
        b'4lCT3E9QRsAsC7IEOcSAiHHZMQ5tq4izSSUUwVOKi47vITfsjLKJaHFzRXvuxKumrG1sKC6YQsRmrWfFpCsHDr0698pr4FqQh/fF+VOumjKZqPYPsLFMHPZzjhhJ5Hgi'
        b'Zp+7UqleGTGtULzNTRETyqLgp8G7Bubml7RAIyLUErE0ocaZ4omYYCzhA6tR6XcxAcnomBK+dhmZHxV1GZMkIr5IIzcLhkQX/5g73zNXqVvJyaP6MDrPUWE2tpgnIpVM'
        b'3jgt3KV5ZnXnHHVnHP0RdwB6P80GMAFCGodsAeNjlElo96Ok4nUvv4/zZQQEGdiGAOdCiyBB6Y9XejMwAKyEC/7P5K62tRJvBKWJGTAvPLdqMOW+JJp7AstNEedRSskr'
        b'8yjH7GiOivgcFFprI6zUCG9vF7KzaWpgLAl6v6JF4a+sbYCFIrkb3I0wJe7V7obvWIkRR5Pi9qMJK474T0VduOAQmT+qZArfm0z30vk05FrPN1MYud1Le2sPSgW5c4vy'
        b'iGVVN7NR57kB6v2m3JHzu7chx3Z2nPcDmuKWi26JgnVyGJDzTrHOXGdZboVnGKQTn1ncljqbbDFSGMQTUBxakFuX2+WBOtuQIDs22pYnRNOJshPSDj0OhRS01pjkJDkZ'
        b'vkmMe5Yip8IzZ/SJJPeQ0+BJUlyunnI6PEsmy3FueYo8KCjW8GQbblueKg+mVD+5P6R6yDnwjRlakC0PgHQaRb3oSUh2SCRhFsyM2+OfDrxgHCQaYsqFBsLtkPdTtGlO'
        b'lox7g0HlWwkCPjgP/9r58UC+YwiJB/VgeJdHpzpmcblosVK0e19TZbX7lSgaFlr6xDSt+MKMXTKX1FbkVZH3B6g15BB8BcIbj1jXX7miK+O4iK2pobLW44LXEaMJDqGl'
        b'Z2wTojk61S0YdadyzCrPazFWp26f96AQMblwZ6B10aV5Hq6atwypUbLYkhxbN37aaXqi1TpoehAByNEKecXJY/l81zW9Z9RkFzoxQFHpdEN02mkD4JlEmg5BBuOhD4v8'
        b'HBBloV5QeskowxAmYkRnWD2rOd8w2RQQ8Re2AB4PduCJhX2Vzhl5ZR6DoO9j4hlrRTs/LMLntwvFw2DKyD0wrlTFipPHX9duui6/NceHW6+vqaHWH7EDv6n4fWtqYVvF'
        b'bdgw4CLv9ohoInxTdyyrC5AN7Mxucpz/Z1GfPsNQzC704pMFYb2db8mKA8TYryrivIeKsWPXzwBDGjs/O4cQKOA7LBvDflZUemHPTL5mICSQhvDIhuIjdiFijwJ8N2cU'
        b'Sh/4/gucTIkan8rHAw6W+N9o5MqORiq9saUWLLCyoUHpy3dLT2XDq3aUmPWHm5YeFzYHvu4S01CLMPxjCAApJCH1ESKwrgMA3CJQ+3ijfRjJPmDIZR/kIyaPr7GyCZo6'
        b'MNpUM4uLoAfjjFjcrB0XZ8U9CEr4VtQNbe3AEyCx1ZIa2xdWfPeDO5x1RYh2RYh2RYjtCg41dCYqCRvA0y4a05FadNTkz9MBAx0gKoP5i7VHz4GckhTTk9ROPWHld5qU'
        b'qNQKDSFC0NKQCD3paWAEJRlJExaIvhV6g+QhrmO/oIORGDBE5yKs66mMPJCUTOwYUpqsdwkuF5BYtX53o8tl7BXl3Pc7slSGom2FpB9b2XUiLJlvyYhbrh2Fdz9T18YC'
        b'XeZ39Y/NFWLZ6MwO1mcWtkKaWVGfWSk2N+A2qUIZwhv06wA2fTQULnzQMdswHj6jycaUR51lXtyU50E5KZK+F7KRQXfpzPVA/OhEq/qeKKqG+HwRq6arLdTqclV5vQ0u'
        b'V28k01F+0JIWXxl7TcT7orjZMJgQ/IhIvhCslABXg8Qvj+TtPbDLPMBvZdu5WFECA/MNFyUY1wFSrvX4I0lIp8vu6oZKpsaKpvl+LzubNnYG/EwpxNGm8/ALpMxmxY3R'
        b'kfobYEVOlc4Df30+fsWwbCVddoJAKjvaCZnARha2SMQh8UxPwqCZpOoRoz1oPchCLUVs7rXVDc2+2tXuSCLuai5gOLFW32fYyGzooMc3aeBAOvcFzFZEOBl2pAbYIowu'
        b'jsDejcRLe+cuKsPgxaAOfIB9A0onbtPANsVhAxyKKFvyG7jU0ikFigKAFhjGOkabiATQD8z8Pjxz57O4q4RWU6s5YAoIq6FdtFJMWRiaSfDlsfsVPP5O1N8AzjAjal9l'
        b'DpjZc7jj6iRU+4CakqA8S6sVajYHLFCbJWDFoQ1YMjjIOQFyWlptAZtyZYD3LQLm9IqADd6LEzmPELAhxeKrDAi+SplaXwff1vI6C8NO03GBtpsGIbWVZ4s4YGUAY1nb'
        b'IMN0Ryx+r0uurfaTTgXtD7DD+AG2qiI2zIjLyEdUJmOA0DlVnp3tPfZqr8fHbA8jvIwHMFBohK9WErAYoVpmbvGIRP6I63ZjHQu5c3HqUEdEInyXRketTlrfqbTGzTwL'
        b'W4hBEJA1jd+A9U48SCQxLcQ8oaQkjy/JS79QT5m6csboimKK9szJM64bmWlGGiARQts+jQttOYSeCRMp+Xgp5nXYo17ERBO7aFFgTJgxbMuLoj4QVs4qChIwg5KA3YY7'
        b'p5jsSJbSpDRzqjnNYrU7JaeUaSKpmHZGu0fb58NYq1vKtS0Fq+YWVpi4xVzWVKlEPa1uX5THk18edY9XDRvWWtqB2RiWgcJ14kd5Zm6kbF60WnsActPByhOjvWVY5qFa'
        b'loPnEq4XtCNzRnRSMUQsQbpUqVEMUQuUjI7cVuq+PBor6906vaJkd4GnLPqczpZ0ZiVZIEl/9dJa6ltIO2A0xK7eJ2ht6oZrO/HABvLyIaEc5YGTKT4iar4Dxwu8pQTc'
        b'K898pS03MWPIGlHnds3oMQ3yWGSHnAi/VtkpJ21Ej2ts30+JOGY2Nzau01vbNblMmwyetzEWBrZfPobP5Dv4TCZ7gKtIcghJNjhPxRzdWC28zi3ATomLi1hQBsAf0cC5'
        b'kHj3RIkpWoBm9uxCPgntJuYbmNLM94OlBcupZ2yPfpjLHDa7yky+mx3UBrQKa8piY17NfEt6XIXRLN2Ta/rxKpEhscHPDeqqoguAYlQY4jOXa5lk8IZ8S+YFvY1m6r76'
        b'yTSVMg88oRlV3YhyBIyvpIZoIJAxx4bBRAsoGFSyiJ6KbbAYg49hpmgiadSIYMrlv/PcnjDPlQb5w5Cgk6RzXffnoukfZDVYu7qlgSwuV4Pb43LJxhACqZ12QZWUoXsZ'
        b'AnbGz60wNBYIH0i4wXRHdOE76IgBMdYuQJRyXCSFV9Jt7wiR1yFxV4aM3YW16NTdFLbvXbCZUGjZEpy9OdHNYS5eyqM7xPeEzFNmQKZ5kq5rYuXsotXsEJNFq80qOkTm'
        b'TO2IAtj9UfUJXx4ibvWoP4rnea6felrSdqoH1L3dI0L0nWYgwjvFOrFOWm5yM5U1FPVJbqnOAvSbngryNTwhSetyKxPOAWJkiNJGQjY7ERfWSOr8qjp3tZ8cB+rj9QNl'
        b'SCgsUBK7wRuE2fw4L0k4Lxmda/th8iOqLPm7pEfrsLIUePnDkZCCJvEX0qQIE61YZil2oF8XHfguzBM1b1Tg0mLzczoHRhTpUuiRBDzpul5MyZhwkBigY4oNgpm7gr03'
        b'rRurKyHze83E/Q2HPJYODnAfz/IafWIpXeGjg7MDcqa3AeAReylwCWuZOi7hMFwAEec0ohqb/bqibgc/fDGIbb2kw4gAjLwD6D+kAtNRw/ab7gdO5yYTLlyVFXE0HSP2'
        b'psYv0osK+4rleDqWZgcl5hAzRToPyStT71FPzdYen69tmltejNp4bfPKV8Wsz+nqQcuggHZj96uzV8zqJKKEThWBUBHZiWGkt9F/AyvNQM+m87ze+uamuGNNkw45PaIL'
        b'Tt+vQh3HGoDrB0fRkonR8ZJ/XZNb2Yu3tqhkrsv91NxAtW6VDHM+PBo63zLwO1pYzD7pwmJwUXQZXrBuLoMXbZKuQWLlkkXykn2ddlbdETPS6pEOPLhK21paWKydWqed'
        b'RJ1ebVtxERC721fZtV3qk4M6nUVFRSRYLmzkHIk8nLTAeMYCBvBsD0+L0kPIBHIhM3K3IY7uTYaos/2bGeSYBU2eq5t9fm9jbYtbzm4AhjabjueV7Fy3X3G70TestwOM'
        b'87r3S0vZx6P7CnJugzbTtSs8XgXq6JCaZld65GxkpNHbRqUs17LwXdn5OiOUm5efzVjveDvqmCbEV1HZ0OBd4yNfOkolht5CF7WeIsO1TLZOtfviiwNmi84qxWXl82Ah'
        b'IV8eSYipg8QSPzTk3BKY/Z2SjmvtVhYvFhXvSSXIorWN125WN6tt2iPaCUBt2qOosPfULFIxUtRgL7VN3TZQvZe9Fj38Zeqtjd0HVL8mZvXJHUdW5hoTHZbZloukK2WG'
        b'PRAPyqywP0p0NCbKFtmKzINsk+3AHJhjDsisyy20U1qJ+HBGHPqyKAf+R6ko6eSbJQqP6DhdBs4pBITLPWKrFBXfpQKHwNeimiW3gqdDCuQpBGVmVGDXPyDob4D8zOKA'
        b'r5BQRBAQfWPxjtJSFpSOQgnoCxMACgFhJiocmOA7k5GHBBTjDGFunSCbgZeTkJeLiv0sKD9fiAuYRHzT8EI0ZMez4R0oNmJ3kSDbhSJ22kiQcMrTneZQ7n4kJGxS3DW1'
        b'a12owknWHRHB47t4/6THJN1KSRAElAB9YzdZyWU40shmknUnk7ZLKt+Lj56C0aR0cDyxuMLCxeiJ/IhD9QyZvx9HWUAhEQ9pVHGFEZzBRESoG+DLIrGRRAIfh18ISKg/'
        b'QOwnJ0tbcLwLDAHSXglthpTx9AXAF5sVwEjmDTDbVMIgeG4BJF6Cedgb/TnhJbQL2iCwJ6scqIeAtBlg24hpIR4iRcRZHjkiVWCAdtOSyobmzmeMUYKJnTGigEsWVrN5'
        b'1lkWWOhXk1A3unXwXSnYkjPO3xoku4NrKYof42qvB3CLn1CUL1YFhflKhUJJJNwhUB5DLC+KAgkn6fIpH8U0ZBIrJDMAw9A+JvrcqyImryK7FRR5+pob/MRjNHbIob5L'
        b'J8IZ3z7NgCYrz3zc2nk7wpVATui/tYt90MBHSLULH0k9Wnp/R087HUVG5aklBFO4agEqereKQIaRLhFZlaUjlJGAXtzH5lwKiDK/mse1vlfAp/RM0Jk45HJQ5gpEsRvm'
        b'3OqqaUDNEA+NmiFFrcKxlfHi/h6ybCWP+oU69cN8/KbSKAjrpU6rR6+qy52WYCvExZ61o7p4AHviCFDk+r1IkIr7UGkc3rGDh9W4LvBOhLvBfsBMASEd9uebeNLcAAy2'
        b'jyeiF1YMrI+RKP70WI0nmAePYmUTu4MnMKrpTF5hrmBHrwIwdghn7emLPfUe7xpPxxabPTDHN7DdfF2OD09mzcpoHLIMAj+Gy5Qr8Ml0TqdyDckLQdqVnRmMSKLLg9pO'
        b'6OUbCvgQBxbtZJhlWDLPzjPSEU0JqXxLr/jhjf20E4aKyt5quNhzT4IcpGKQnhHYXS3wI0yfSbf4QyyEX5DlYsAckAj39/RL7LCrDvYFFGXfz1/OGXuAcchrVhp5HUyU'
        b'GrzQeqTDHmDf0XU+0OaWGHmU1RA6K5di0sbEzNCjmOXZtYTYA/m/NkARR8ouSgIbs36dEbletVgBy8HWJcdeE204dcETzxFcFL3SwSUsg68PG/SKlUuXknsm97fa0p2k'
        b'xHOt+nSpds+SDtGs9mi5thldY/XLkNSn1L3lXXpix38UqjNKmyQRX27QJCxMgkGR4JsLqRHkJHRahJR0UIzJ5i45Yp3nra4vqW1wVyjIJsTRI3GqEnM5Js1lTKfP7hdk'
        b'nlYgY6sFekcHoukowQTYgquJ5Jhmkmla0PTPZdUZcKmivQcGQM6WvW49wAESmO2WHF8xKgTifJGCgLnWh/loeUUslVU+VEuIWElpUK5VIhZUsfc2+yMmVyNF9qG4yhGL'
        b'C3MAeR2jLxGRMIeypgv+HGEhwaSDFS5EDH9ppj8735JiDFLX0lDEbnZjnDA4CNMhRTEgGjXauBZrCNcd4CPE00s5zwiyCgZSqVXguZacAKwuWagXlX434VdmJXcpMN+I'
        b'xa4nXTS9PL5eUkb6YRxx3OGZVZZYeUZej539ruHX4KkcjfxCbpUVdm9TxaIPUgi/VXubG2Qa8cpqirGQjSP1/q678d+DU/JswATCkNIwRUyN9TDIymq8t8xfSPx8xORW'
        b'FEBDGFcw4ri82YPZ9Te+Bre7SUeAEQvsPVRUXbfrOSJh5T1NuuYvmtMKZFZL53ZkjEO2muuFr802iRc+a0mMzgV+2b0JDjM8reOUnjQSCLu8MQdKBsyHZMxHnLZfDW2d'
        b'JuocAxpTrS86BCalEe9JRHUhP9zswQYNMenLn8WnAULzG0loSYo2muX6PsKLkZRRWRVQQ+HuROroOskNSK7QZNBafEtyDLzSy+6HKT+mPgRYXYYtMBk2HUXAMOkm3SSs'
        b'lZRbsC1rjQFS1kWbdqFFk8sFuBgls8NMhvEtEd9mUtCIaaSerZNCNP5H420ivmg2EwyZIQ4P0wjFw1i+QzEMoG8dzVV1gxfoRBw4Q0NGcrnXVnchYAbUA2v6ElP0JAR5'
        b'BEf8umd5UGiCeLKb3YRGhqZqE17a8LL1YkS/qyCTxWRI9Dmn5LQ7UlD867Aws8UHte1qCL0+zde2rtbaJql7KIR6Yp1oL1KPd9o4LPov2fpGRUqorC4BuxoVK6EO6HJJ'
        b'Tg6yqEFi0By01phJxGuDDSSFMbgU9wfPv2ywmTAXcXgKFsvabsxLjUglC2aWdEKMUZIEtdf8nE5MwLYBRITAGEljCuEX2hYS6iS0CKc0oEW/maX0TYTTz0/aExaswwpH'
        b'Zq/O8bUnQkIPqA5JQ0bJ/IKhN9SmyhXuiMPn9ruaFK/cXA1sgQO/di2ZdfnC0vkVkQR8R651AY0luFx6zHGXi6m3uzBIjUHYRZ0NfNeMYt3TDLBPJ7VexGotiVht1zxm'
        b'dyJr/eCiPWUhtCS7sdJDHkXRxw1ihp0dAM681VxIbWLPon2YA00iwXZLKjUk7mVFXHNMXIzk+b6Y2cPlh27ZAwITkdUJyrAQsLZ4h2rwwJqKwM4CKbCBKc3TfasIhL6Y'
        b'waF6Nj0F4mCvmSmLEGnKK/NCQGTKpg3CNicQp9JeS0BgG5wMYCRxG0SmRTaC881ewzNp9hWcrllGHgNQif4zUvvIyVk4a8G07M9wCJgO5VrFXWMnGj8irKnSQSRiBtKh'
        b'qdlPoxgxyc2NTT5mZozgSmerEdMaVH3QJaQM5dE40ydCzcqLNzBX7sUTHpOul+gkMsNBYOEgpTUUbdnPAz37LewZCTQ/rHkR2xx3w2q3v7a6UpmCBZHiKC6takN8hf/Q'
        b'KCfqRuhanrFZ+1C3i6c5QwKfdMBhPkR9vdH40z0wVUD0i/gmxPtNwGCa0jjUhkVXICzdm6WtsrnVJlta7UwI0ZoAsJBAWrP+VgewDo4srjUxYFOqjHyBRJhpK2y882Rb'
        b'a6InidJ2SF8pJ7Tao3Vbse5Vl8a3JeAIAPGaydUDdY5ly44MLotr8kJJzoBTuVtODDiBLbw74NTraAs4lBvxbEPHKVCW7AxYsCxZbLV5nJQTa78b36KOOqsJ36LWjGwJ'
        b'mAKJATuQDLY6vCbUOeSULWYoza48hLmgjWbCQ6kVH6C5ygc48os+wNl+P5h+7jdfLvz7lBISl7SLkyZNoumKiC7AJvwixmby2RF+esQyw9us1AIy4kvzhIjJ417jWst+'
        b'1uUlMgsDO+kBN9R63D6GpBorlRW1Hl+kByYqm/1eQm6uKsBd9RErPqzxeoAcVrzNHpmdvdyOkCpVuxsaItKyBV5fRJo3q2RRRLqC7itmLVuUl8Sgm1QIJCpAIuMek8+/'
        b'DsjpBGyAa6W7dsVKKJq1xo4ZXA3QHLd+D8wwVGFS3NCKiLmKiV9snuZGF33B9JUlvIen7rV+evy98bwTmB4qaZcvx8WDPCILIuogEiuZeVTUXatIuoyPWbqhe5Y+5I+I'
        b'yS3MdFbOlpr5PHogJBlGMi22mIq6FNTQPraWi19XdJbmpLN+ZIxyZCHMob2WXyTGC/dYKwp1Nui+TrLQ1IWXzQE+nWldSrIFsZzfpAtZzXGMtqgLW60Eb7b2XtMrFTQS'
        b'zx7lrRnHBP/kr8LX3Kj0gHluL7gYK/qi4uzBwwpyOhFcUR04FKGTBZqlFfrCBAlxtmew80zjOqzPJnXBVKHZWcggS9O5lv40yNj4UeO6sjr7AEtql/JzfPm0diqA//4L'
        b'FpRJMgOYGtKDj4jQ14iTIL0W+Ptqb4NX0bE5K9xg+ujgr2O3jre8fifazufg05uixJeQRmaRKN4ayOtYmBXLTv4lZR/2NR4Nd0MP3s3rSF/5Ga9XFCNd+IHesDrkDNug'
        b'nEmmqJwhWbJaMqU0Z3ounXyoh7K0p3wJ6i5tT9MqkRO0XfwA9Qn1MCoBRmmDCqKUKyrQSp88iO1abiqoKLdcH+9DYEQNas6JzcgWT57K6XaUG6UBattK/JaMkp2FwpDb'
        b'RHK35mgdPISr/eSzwaJvN1B/LZkHyhd9vbTHirR7cwaPuuL3T0zN/qnphKdw2tTbQuGZt65c5jh5cNLLX7xrG1e3vH5x3dVDioeOe//HX994nj+/8OMvP+37mvbWSN+b'
        b'rf/oHWhrOJ156Ts/H/389pHDh/zjJ8W13NuX80MesH4ui38q63vXnVnXzi3mX7xcqJFTfl805tptDwnXudN/P3T3T64/LfS5tfmPeydyzl+Y/vjIQ9zsdy5pWvTK+iuu'
        b'cN4z9Fzub18MJH1cPfqNT+8vfONva3/1u5nP1l+xb9Ydd368rPEp99unpy5sP2cr+tNjE1NO+W+qWH3mZN930zJ+799U8eGXtl9MG6XVX5VUNbp8xegJ0su1n0z4ZGLZ'
        b'+2mvKjN2T5567lffXPXOrOKfHvx1z2Or7u19pr/8p4lX/+mrTz4Kjnyn3yHP1IVvlSQfbPOXvtYyveB45cIRx+rOFw6c98mG7NKdtSXum/Jbrx3z19zFJy79Td5Ll73j'
        b'ntnrrT4f7/148HMvXPXs/nGlJ/6Qe2xxvyeV2vs2/bFNEc4Mfa38/Z8fMH369PiTP7M9k/dZ0Rt/nHCm7+A/2YuqbhflWYP2FdQ++OEe8/UFl9/w3rVPlgWLT/zxfe0z'
        b'y31v8/2mv+p+6bJp9xS9dO+Ej/q+nPT8yKsX9626/NHnjx4ODH1r5389c+zT5n5BJWm7a3/PRadeWP38gYf9/nuXTEg/2u+ZSPEpafvAvyz0Htj9j7Wv/Hpd2mJv5ey8'
        b'J6fV18x9u2TntK2T90feOfqTg7sXTX7l+JOfn3n5lU01rsTPr9l35ZCSh08mPf7kuebDvU7Of9x9n3Td7kscEzYdWZCxePqd5S+lHix/cr930LG/v9+09MpFo/5c+dy9'
        b'r+5894Wrn1zxVelze24+WfHaLR++8nrW/j/su1pbkTb/Or/rD6P+Nvj4MelN8193Oydd9c/Zi8ZsW37DA3teci6ffGp++7H31377jwPHPmtt+OOK9ln1t4//YsWyujNt'
        b'D519YcbjZ++8+1yvN03nQ9ePetlRt23YJ5kzjr0Z3vr33y1bWf2m86kzn7w5NmXt53cJfxl/6801O9842nbw0kn7DgZXL7pVvUz4+L5Tn//l+W/rXstfwd875oOkbxLH'
        b'jz989PDsnje84Hum5djH/3XJjsFLK79uu+Ynf5t+uNz1+mrHFw+cHJryobfF9lrZO6WH7cs/OL94eM7C2eHhfzjp97x8buhLU0LOw6deFua/VXHN7+pH3THvrtsW+h+5'
        b'f/uTr9319KFN7cLefwbfyH6x9+nX5z0479DAmjv/fN1rM+49/8KVuW8cdiY//Nqyp5reHXVmY7G3Sul9lfb3p/d/ueDpnQdqIs+oN7h+8bb3voeu/lXS0/yu/zr57rOV'
        b'eYl+lLhoT6jHp89XN+BRKfr1mj+vtEjdpG6zcD21G0XteMsECmqct0S9C7PMp9N1dStmSFmtrlfPiOodwJgeZi7bdzZod6FX1lJ187A5hVqY41J949RbRPW4dkS7h1wV'
        b'Diubp4XUneTrt6Ion+es2glB3eG5hjx0zCoovzDa+YLrtFtF9ZHL1JuYSf5Bm3bwAvXWQnUr6bdqbQqLvbhX26KdZefCNjQRx1C74xrVs6KrJzQDPcH1meyA6sloVS9J'
        b'DWsbtT1GB5mPM6Y9EBhvl3wWP25JDm37VTGVl5arWwvKCrUtebraQYzOwQ1ldk47pG7zYzxj9ZgaVO8crD7wffohgvYoVTQm/RJfMcWE2tZs5FGf1jYVdK5ojbbLpp7M'
        b'WUrzqd6XKc3WHuhOyFyn7iefXNfCdN7qS9Du7RfdIrR7EoAK/EE70nde8sb+Gwv7f+WSN5DRDP9XXAzxWIO3Una5yK0EUmICb74W3TGY+Yv/k95z9nXaUIldEPF/Ki/Y'
        b'gDi3pPFCKtz3yOWFBb14IV0AmstcOETInO7MyjRJUwUhk7+EFxqG8EIzcMhWPM4fzAvJAp9N1z680B/1xAQTXS2ZUC4KkAVRQM+Lpvh7By9Y2ROsfyAv9BH4dF5w0Hsn'
        b'XZOH8A6vRPbXgggtlKDEAf0gZybvsDiorH681Ym/0KYrBR5aPVrg83lHhfKb6Flf6P/DfzeXDu4AR+taTvf3sLaLaBbkgav+yvKOrUkN476jPaCdcWaJfftqR2rNZ5ZI'
        b'vn4Amq8u2Fp0+y88r0113LLi+LI33m5d85dnzlU/e+5O/1OfZ7XYWgpDadsPlO36Qn5/geWr4BOTb/rmRwd+dOP6r58eMGvTqOfHzhp/e3BGj9uvqX86ebz62PM90zfe'
        b'15T7+c3llSVr69X+c5eNeuvLO/9R23rnkh1N21LV2TuFXz5dM27+OOe8qV//dpO9OWfy6J8uf/hO2466t74NPLLI+/nGty4fv+utYff+16G73ju08qabv/x8+9w+Z3Lz'
        b'b9t09X27171z2YNHDp1puu/+FXtWv9K+7eS5X8/d/c/LZ/8tZ/LJHT1fS3nvq9c/+uyx/taE12898XPLYzu++s17v7z9V1fcsfX1x5ekTLj9je2ndr20rN69vzm89aEx'
        b'z1Q8NOZnv3noxDNfPHTi3Weci58LvDjAe2T/R96f/fXA40v+khmsu/pnx+596tmDO1qfTn/l7Wkj32l57Fc/k58Jjp+0blC/odXHhlx3VekXX5ecP7vF5rqiX9Ov/nbr'
        b'sztmTzwx8b1j79q+vPm5r0aPq37zlZPP/PbcdR+Ouvr0yId7Pyf/bfOJhEcfeify6cTTsvvND59Z+osxHw8ZO7HMc3rQmhFt0/9c/PrZ9tq5m1acfPUPv7yyZfc/jr5k'
        b'fTNrzZF1VUN2f/nSdd8+0vxA3WNfz2kNH5y8bfKnOWmj+5z6W9K6T26btr5Q+fn+9QN/+ftf3T7NtPilBbPF8uPPl1iu/vz5Z7kZf6naOOKLR7bZnE2hQX3elg5eqo37'
        b'0V1vCb6r/pf91VM/LZr++qQ3Xlx/y8Pntp/9/NWR77bN/3PbLyd9Ky4+/rLw+Zt5k4iKydGOtOjQtFlrK2TgpN6oHXdeLo5Qj6pn/dmQS2uzSJ1oHSB01mi3qHckardS'
        b'DOYk9WQlxh3FooZM1sOOOhPpnVm9pahAPVZo5rTT2uOCdiN/LZA/Zyiy4Xj1pvKCsqJ89HulbaMYg5vLoEZOvV19YMBCUyrSCeS+XXvQU5SQf6Hr9inaRt17+03qbUQy'
        b'zVXvVzeXQUZtcx5mLTBzQk3SWLFefVI9TZv97KvVw1rbsDnalvoMaOkcDNmkbfcjn+9oUfeXaVtzBU69K1fw8JNHV5NTo75p09SDQwrQJfx8E2eeKjhvUA+QN6ZiLThW'
        b'2wBjiARcbhHPmdcKIxrUkyws5F71dAJ0p74vNKYUiA6relaAHu3RTlMc10VLtCDQh0ARabtGCgF+inbXDVSfx7ZYPaJtghfqrXZBfZxftFLbwFy67Vf3qZuWaNvLCmOc'
        b'hcGk3UYf+rUH1BPkzJHjePVpoZUvWTCX3gCxU6+1zS/mOfX+pYK6iZ+tbWylMHI9p02AykJAteXP0XZg/NdQItJjSITljDbN1I5qZwle1Eemq48mAJVaVmTP1TapD6uH'
        b'JO2U+iDXS/2xpO6al0Xwou6aBLQjemGDESnWjql7S2HYKkxcxkpppLrPTK1ZCpP9BEzCXKhCvUNQ7+JL6jPozZys2gItNMzCpWnrBfUQv1Q9oAZptNQbM2swhMIWkZu3'
        b'TriBnzpdu4W8oo5O1B4uI5QIE4S8eoO6X71R0A5cq/2YDdqBfiPVtvnzi0pxCstNXOoEscisHsmqZB7/91Vph8pYnPP5FVREk3bQeb04U92n3UytWqYFCWjMHL+wVtsM'
        b'06DdmGlE6t0WYECpnsVoARSPF6CVOdy6L1G9RWtTH8TxHWzmOakKpkU9o+ld2j9p0nCurChvLjTKvFBIH6HtpFKFpJ4MhksRbBJm5Kt3Cdoh7YGpBONLZ9wAU9mh7itx'
        b'qeoGUT2Rp62fxHKo+8erwbLSwtIiapmJ03ZoTzm1TWLFTPUErQJ1h1+7G3No24dCoyVe3aOeHcH4ljvV3ctYl8phuPNKoXztDlHdPV990gLfkT/xR93qUwWl6tHcvGFz'
        b'EYCPaIeTtP2iur7XDBaLKgh/e8sK5pTmqXtgmfXiYTBvh0VK4pU7Bml3a2247LcNuwreXsarT2k/0u6gUZlard5SMNfE8WXVahsHLNQO7SHqVb56/yIAbgQtdFUKA6Nu'
        b'mRcQtHvUR9QHWa2nBmi3wVoMlc9Tb11u5qRkXt2VAUgKXy6HpbOrbG6edqSwYswonrNotwtm9UQ+zVTdZO1IvAvSAWKdtn/CoAW0lAFbmOJcgGrHRPVRxwjt1Fh6PzNn'
        b'chk5rDaWpavcqe4VZ2hnC9mq2KLtQWYw1s1qwiCAOfQIq90+hhZYurYhv7Mz1kWidtCv3av+WHuKeCFYOo8AKwcIpwgWSj7MEyzW2wGPzKNx2VxWpB5Wby6SuHL1iEW7'
        b'UVuv3sx427YJ2tkE5EOb4OOHAC43lyF0pWn3iDD2W7X1NLM9tbsaCZsVzykHbJEArT6r3S9oT9hhQyDYOq3eNJXcEOOGAMttonpGBbz+uPqQejcDjsd6CQXa1nnatrLC'
        b'vCKYyR79RHXfcO2OHsD/YUd7lqgnynA5QmfDpYVzh0FdE7QTZq6QM2l3r9NOsIgd98OYHdV3qC3z89A8s1TdghtQeo4kqrvUjQxeT6mb/Oizev582j8sABePAyJ8DJfM'
        b'rR4a/2U+7WzZXICceatJpAfcpsVcz2Vpj0tXqI9qxwkR9IDR2gTt0h7FsjCAUIp2RtROjVb3FWuP0Gamnh6nHcThgRJ61lk4qYhXj6bcQIgUXS4vxuYOi9nRoLUj1RNc'
        b'78GSukHd4KJtxt84W318YFlpeX65hTNLgjWfrdo69UewRaIz4zzoaREM7Tx1s3YAIGS8dtP3nasZDjvH/gewSv9xl+gZNLFte/EmwSpY+fg/O58sSCYHebLuAyS3wFsF'
        b'p/6GnaEYOlC6+wnBrt8nC2YsTcC4D2lxZTroHIbyC2i8I1EuOztxEdaK8V4J2Z95nJlnEnNdS9xGjhuam1yuDk+DxrHDb/nY/uENsRCOLzuzEJQjTjkikUMPoEw1wfcM'
        b'XKs4ma+Dv/CS0BLUaAsPhV8BfgX4FeE3HX4l+F0cWlLLwa89tARtF8P9MX8d5uSDfHCJoYPXyqH+XYPYKIWTGk2tfKO5VWi0tOLxokW2NVgbba0S3dsb7I0JrSa6T2hw'
        b'NCa2mune0eBsTGq14NGlPxlK7wm/KfDbA35T4bcf/PaAX3iPh6/hAQEulAS/SQFyXhROCKC/Xj6cDPnS4DcVfnvCrxN+0+E3BzXF4dcSkMIDZUs4QxbDmXJiOEt2hnvL'
        b'SeE+cnK4r5zSapVTW21yj3CvgChzoSzURg8PktPCeXLPcLGcHp4vZ4TL5czwAjkrPFvuFS6Ve4fz5T7hQrlvuEDuF86V+4dL5OzwSHlAeLw8MDxZHhSeIg8OXyrnhEfL'
        b'Q8Jj5KHhSXJueKqcF75Ezg9PlAvCY+XC8AS5KDxOLg6PkoeFR8jDw2XyiPAweWR4rjwqvFAeHZ4jjwnPki8JT5PHhovkS8OXyePCl8vjwxUh+wYuPFieEJ7uz4C7FHli'
        b'eJ48KTxDnhxeJE8JD5f58MyABd5kh4SANWCrwVFKCzqDGcH+wfIaSZ4qT4P5swfsYQepw3R4xHUGk4JpwXTImRnMCvYK9g72g28GBIcGi4PDgsOD04KzgiXBOcG5wbLg'
        b'wuCi4GKAhwHy9Gh51pAzZA3lbRDCtiCLcc/KdVDJycGUYGqwp156Xyh7YDAnOCSYF8wPFgZHBkcFRwfHBC8Jjg1eGhwXHB+cEJwYnBScHJwSnBqcHpwJNZcG5wXnQ53F'
        b'8oxonSao00R1mqE+VhOWPyRYAF/MDpbWJMgzo7kTgyIFMEiEfKnBHnprsoODoSVDoSUzoIaK4IKaHvIs45vWhJAzkEA1DKFvE6CWRBrPTBihPvD1IPo+F74vCBYFR0B7'
        b'S6icy4KX12TJJdHaRWirSCVJ19txHlsdoZyQI5QfcgQcodINAqp+0JNCelLInlzvCCSQbsxsFh2BnIZ0WJt0r/WGGyQz8QpxzbyS6Cd1yTreUCrX7ePae+b4cvOya5mC'
        b'amV2VXNtg7/WkycoGxAH5WNFuA9264DLVeMh6Rkqt91v0i3lHHQArfzOMJTJkwDdrXD7axS0zLC611aTMg4Zy+Oxurcm4jDUkUgNiUdnKo2AH+HOji7DG5sUt88HKbHB'
        b'uwKtqVFvTfkdlP0BdvkDcpmO7foAD68/wBCKH3CGdrZXdgOWJbcWqNkeEZu8TRE7lC67ayrRbsJa42JntcyGs8PtRRQzR8w1VE4kodrrqlRWUNhRDJrqql/j9TSsiz6y'
        b'wyMPKyzigHufv1J3ImqFVE1D5QpfxAJ3VJiNbjw+v4/ekj4+1bC6UulIoLYvpug7unHSU8VHShMeL5XTABNYWcU+UNzu1egeHhOoE0EJU3WDu1KJmBsqYYJHRMSq2hWk'
        b'xY7+dVgAkYgd41aze6Yi9Et9kv1KZbUbI1W6XJC9ysUm0gJ3qOQQkVyKuybidMm1vsqqBrerurJ6JVNQBsCQmfs3DLXSLuTmdQoWiIfLSIYxZ1sCi0yEaljoqgo9zaIK'
        b'wUw8phfIcFfYACzwqsSAoZvftebh97qeQuD8Z1Rpk2gChwG0cW0kVVejjcfhbcgCmM4BCysLWxLgAQcJNWjBkUQ+Nzmy6xBD2aQ8JgWkkL2ZU6aFHK2mgBBKqEd3U45W'
        b'syeNUpwyLORI4FpNIY4pm4XsoVR444S+OzJwLMwhC6T7bhAC5lBPqFHwLAgISik86xdKr0GnPGWoHgb19IB6llLuTPi6D5bmGQ/P+4dSKJ8vlAJ4x0JWcI5WK+S0hNIg'
        b'pwR7BYz1BrSwqQpIsIPwVJ4ZyrstZIZvbFRqb8iDM+GEHtrhe/27gA3u7HiH8ZMCtoUc63uIh+/PwHdJocQEwwJPDCXTu8RM9DucEEBvIAn4LiAApk3M4JhVGPlKtbFQ'
        b'ClE1PDaSv4bxt4d6Qb0CjkfAlEaWfdEReJXammGMAKnOrYjCieO/dbYx4D9AvvyDRNAIzWaz7hbBadCqArPxMsO9mSwEU1HDiFy0OshBazrRuWage9NRk0h0CslCH6Jy'
        b'rWIaL0nWbwDBC3HLJEXfeWiZvCDoy8QJU52nL5O02GUCb0WcvpAEu1Nm3MLB6SuAbyS6Q5A3BSSfP2QCQDSH8C8dpl1Erb2ARZkWsJBpjzUAtTHggYXSayLnqQv1Dg0K'
        b'DQHwz6oxoU8pAN3cVnsIdd/sUGpCwB7qDcuxHgAvKYHLwi1ZhHsn3gcctOCgnEACEIdJOgCTHiB7F7ADuM/1jA0NDiWGest8aBD8HwL/+4dya/hQCtYT6o/LKg2IS3je'
        b'K8SHkkPJSJTVWmhZmxCMYSGlBKzQm0QAePgNwNIIOTO5VmcoFUgBfOLM4GDZJBKJkABfAXGgPEXfw52MesZm1KFqNXlWw1NzKB9KTQokhTIpDyADaG9SKJtS2XpqMKUG'
        b'66kcSuXoqX6U6qenehktpVRvSvXWU4MoNUhPDaHUED3Vh1J99NRASg3UU30p1VdPDaDUAD3VPzpymMqiVBamapJgYyhC0j7AbUWUiYgA+hoaGkqEHicHkm9Fn2ESXS14'
        b'JWjJQGiBMmD0a9Bxud6bDA4ND2FEeyCUQakieZaQcOwRcdPzgoBEOrmS4U+gwyl5yv+RtZtX/B+AP/7ncdQUxFGbozjKqTtAQ51GM++keGapvCAJPPuT/mG12snDaxrp'
        b'Rwpfo+9//EsTUPNR+sruoIB0kt2cLtgBf8Ef392f9IkjNVlMBdyGh6XStw6Tg9yxx+E3w1SM8BvzpgkYDNjmkFXHb+YQF4PfxJCJtnMgWEI2IPgBrzFd8VhPKl1TKf+G'
        b'gAk0qEfNugKdjvhFQPJSp05ZjU6h65CQBMsEaQ8B0LKNdWQDqYEqPVB1PZSM7kPpuRSgnNDFxJAZd2gYiiRAVImItjGFSvAh+7ZMHktNCKXiMsTBIiQmmgDJhmxjgQSc'
        b'GKf+7rGO4HyzYpXfAQkCOgWEL+r3yVAKqXBjwCUqj4vb47se1B7/sxB9xhxVggcYFvBqt/ThzTAJqXwfgjH7hTBmj50OtM8C0hJFHwBF0emQ9OlIo+noCeSZ6EunN5hO'
        b'xzQ59R8IcOdAY2J6Z9+WSoOHBveWTLJOwFQXQz8hbuiB4AtZstCQVlJOBkRfhUGC81ifBAQl7s4mpRlDbCKmhX3NBDsQTHarpcWEwggyB7RJnJ9b12iU7OHXcPRFJvve'
        b't5iYc2cwGRjztGBGjUUPzmONqcWKmF+5I5SIT4yv2Z4IlIatRqiXlFPQliejJdtQCALfHIVv4Ak8t0W/ia19d6yBnO47Rqzo0tAn6hY4Gp4SORXoNAw7BbJA/xQYUwjd'
        b'ZXrTkXZdbTDbJYbsT/BXKe8gf/lX/ge7DIk4a30ub1WNa42CytyK1aLzMBIv6e5zCf7yeGLh/6XgJVn/SVvD62bdOpgtJFSFdwgO2hiwu32+tUsSOSrCeKRoLc3CvUgY'
        b'ldQufZyZZrdYhVTeYcG3uI3A9Z/SC1KRxOdlMhnF9VgXhQARfet8ygv47EW8vISXl5neNfoN8imvkKFBS0NtlfIq3TZW+lcqvycbb7hxV2J8CeUcGc7UykoOFQr8e0Ss'
        b'rALOf2WlDy3BIxbdFVbE4jNuVjR4qyobfHmJ/54BzFv6HyCj//+Xf+VQA2ES43j5MJiiIFil+AMNp5BpcvDsr/OBB/uTuvhzdPn0X/8z6/870g5zqihZ5onSGDtfI0p1'
        b'dj5blBzDRamPnZ8oSjPs6FDEiuwmkHAC9bMCDXNOcRRIwhUrA3S59BXZWNkEy9KvKDt4ZgxMHg/YWcrvaN3NWlvtbkKnUAoeMeLJSnVls8/tckXSXC5fcxPJDlHQhmYv'
        b'8DTB1ZFQvo53XxFjNTux0Ss3N7gn4zZAFB/sk1IyOuXt8oSHu8Hag/0KA9ES0lAflNC2u/1/A2ppLL0='
    ))))
