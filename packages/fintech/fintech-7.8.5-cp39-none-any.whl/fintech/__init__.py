
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
        b'eJzcfXdclEfe+DxlC7BUkWZba1jYBQTFrmjU0MHeZRd2kVVYYAsKWRQFWbrYGxbs2BF7z0xyl9zlcrkklxguyaXdXUxMLpdyb+Kl/Gbm2V2Wpib3vv/82A/PPjvPlO/M'
        b'8+3znZmPQJc/d/wfh/9NG/BFCxYDLbOY0bIHWR2n43VMOdvMLBatAIvFWk7LVwCNRCvSivG3tMTLLDFLy0E5w4AFwBDHA51bcQkDFrszoCRUK9G5Z3hopfgqo/ee9Oql'
        b'c9/ALACLgFay2H2Ju8Fd+I4CUThlDnCrULg97O8+N0cnTy825+Qb5DP1BrMuK0deoMlapVmhc1dw9yUY0PtSchHhSzsTkcW49IfD/xL7t2ksvthANqPFPaqQljJVoByU'
        b'siV+VqYcw2xlywED1jJr2Tku9xgSgCHJUXCpWa4DJcb/Y/B/H1IxTwdrDlDIU9vB1+Tx3FwCUs5oHuBv+ZdeRbIpaxPBP4SyX05pAT1CSSubSKBkbcDGZXNOSJlfD6mj'
        b'gc6Q8qmWCHxfiLbNnaNCO1DjXFSlnI+qUG3krPi5S8Piw1A9qlOgalTHgenzxOgc2rNcf+rrFsYUjsv9s2XnZ+pP1bnZD9ShOuWWME285oH65Uz/rJy5B7Nz2QsbgsfG'
        b'gA3FkkXe1QrWPAyXmCdCVz1wpeG4ylp4B9WlWFRhqCaSBYNgG4/Owe2w0jwYZ4R1cGchrIWb0KYkVAe3oa0psB5ukgAvP24gvAMPGt1wLgXXzoYqjARfhQtJfOgzMduY'
        b'X6IzyLMFRJnc7qUxmXRGc0amRZ9r1htYMgjk3YFgGePFGGWOoi1cO59tMWS1SzIyjBZDRka7R0ZGVq5OY7AUZGQoOJeWyKWFMXqRew9yIZWEkIr7k4o/8WHFDMuI6ZX9'
        b'gWXx+2HAT+SXhQxEaDasTVLC7UxEqioMVqe5DrQyRoRa4LVZuQSk1TEvzhjA7fIABXeZ/wRdmr4YUKT6eJiFNUtBgfqpLZkD5/8QZ0eq96fQp3P7rGTeYIHP++nWJf0n'
        b'aIUiW9dxgLz580MyZeXRI4XEpFIJwJD7lIWslRUW+QOKD/BMAH5N8IQSw1OFNs2Jmi2gRGiEKhRVRYYlpCyB1QxYukSaPBLVKxjLEFLoIryANnvg7iSp3ENRDTwHT/Cg'
        b'KDkE3uLhHngJtVn64Wy6nKXktUaSDt+aRG4lwCONRVueWWsZhJ+j/fCoxfni6UufiG4K7z0J7ldwlkCcKxGegaeSVKgRVikSU0RAPIcNgGcn0hamD0Hrk+h4JsAyLkHF'
        b'Ag+4i0Un4MEcywD83APd7o9q03IGoJrElAhUnQxP8cAPlnOobDx+xxbyEhVwtz4pQZmgIm8kBR42iIAXquFS54+39MWPB6GDXFKCNEeZIAI8z8AD8Bi6ZBmIn8SiBiNG'
        b'bngC7scFUxLw8CTg2tFWDl4v0uGhIrWnojZpUnRftDMGP09CDWm4Gu/B3ITFJTgDARE2wxp0KClagc7HJCSkCDm80FlupA9qxnnIQMFrsPpZj3gtuoBfUwGqRXVJpK/+'
        b'qIlDx0YMwx0hgxGBylA5qlWmooYEeLyPMkKMR6ONRW1D3Sm86BK8BLeEo4ZYuCMZD7lSoUoUgT4DObQV7plgIaSIKtCu6KQ0WMeqEsLxsFYnKBMjI+JTxEAJRGh3pIj2'
        b'aRV+x+cJFOER8eaklAgGj/MhFl3RTrE8RTAyA55JQrUBWpyBdCg9NAkTfgOqw+iVrhKDp3kxKludYxlOelaNrhKEQ9VpybNC45Oz8Fg2pCanzSMZleNFM9ButLMTd2Nd'
        b'+fARyuBtDGafnI23iWxim8QmtbnZ3G0eNpnN0+Zl87b52HxtfrY+Nn9bX1uALdAWZAu2hdj62frbBtgG2gbZ5LbBtiG2obZhtuG2EbanbKE2hS3MFm5T2lS2CFukLco2'
        b'0hZti7GNso22xWaPsbNoUMVjFs1gFg0oi2YoW8aMeY7LvZ1Fr+jKor3tDKQzi96YahlBxmTDUHRSia4mKXtjGPhFn6LIM3rCCEphqSotvKVQwSpCYn5qDp4NQxsp+qJt'
        b'hegGqsXIxwF5NruOiYPXfC1BAlJdneAHN4fDFmU8xm1YwaBy2JpkCSDvEB1BtnCFClWpJ2B8FMOTbDhrtQTjR7NgFToaJrw0JX73fAIDb2EIN1FqRbfQrafTViVhWiPP'
        b'3Bh4FK1HFbTSMTxm/Ycwd4kn0PDxDGyDVxZSMMUWdCk8QsEC1IpOsvAysxjuk9NCqHqcOgmeVCbkoTaME+JcNhS1Jgg9qIUHlgyEx5JQDcI8BDc3lIFnFoXQcqXovJzi'
        b'KANQZSALG5hkeNJEH8XPtCZRlMNDulvJAHEsG8gZaZXjsNjbHp6ICQydiUrDHY9jvTA7OUr7hkXTJVhJKw2NC1LhgmvYkePjaZ3r0CV0GtN3KAvgIXicNTCT0c4RFvKC'
        b'R6D9mAlFJjLgqTwW7mJmegBKr2hjBLIRQOoUhJrRkWIpvMNCmwRdpmMC18ehE6g2RYlv76hZKzNlATopALIVtZXAU6gGPwpCO1jYxsyFV4Los0K4fXwS4QHwtArV8UAc'
        b'wrp7wk32MbmF9qHaeHgGgCUz2FJmJmYYx+ijZegAPIBZJX5psHY5C2uYZ/piJCN8Ywq8ga5jvkJIODwiAY9NqggsRU2BOXw0q6I40Sca1iWFE0GQSF5tn2A3MYvl+7nE'
        b'LNYF6wmid9Z6sM5jY5xaD1uFdZtSDpMUS0mKo2TEruXmuNzbSariybQeLlX/1oavONNknPDmXo/P1L/L/ERdteIT/M2/VrdvRNwet/gYRp8t93x+kdJj4fqJOzbW1ckG'
        b'xH2f3Tj+slelWvzKKPD6P7xKi7YrJGYi+tBN1KYQZBaqT1Oget2aBEFbCRjOc/AmvGImhJnRT99ZsBGpBo9jwYb2MGbC+dAdoxelXWUK5ozVQj50OJVkHQQ382izFR4w'
        b'k/HH9La/H8mK8TUNNuAMaPMQ4I4a8Xtf3o9mQQdGYTEkZEmOgNW0PXRIyXGDVfC0meDF2lEB4ar4BCLGpOgi65EMK2AL2kFVNXgWq1llFBrU4BANBGoebpOA4WGitCWJ'
        b'diWsi1pEU6lS1M7naUyrqLpFFCWwVsoIHy/GnTH2ceRV8O2c1mRu50zGLCNhg0Yfksp2VInv/cl9X0fNtPA64FC3yh+hbpGO5i7vMxhSukENYsArMUtAx9HV3vXv8QIm'
        b'stnsr9C+s3vCQ74nPCypa2JMBIXelPzwmXrp3Vefa3zh3nONv7nYuNn3Ra/s959f+TI2xcbxP4Q3Yw2aSAeMF1tCsea4B+0IxSwziQFSeIot7ov2CXhxAlV4dMaylT6C'
        b'9jQL2oTRZnt+VRazPrdDM14HpD6MMQB0aMZcfubKnt8O1oODnC+GFKki1RBwQBl46PXoVzMGi6JmtL4wnOpamF8bGXgnanWnV8PY/+c4wLMKRg6TKnQg2NmVjv54GfIz'
        b'8jOzLaYsjVmfb6gjRSnjYS2h5Ao3YLZ3NhWzWjpaaYnhqtRUovFilYQD4bBNhPbAuuwngKPikXC4OYDQNbqAQHj90+MQFhykYbQ3CreNqdAPlXPw1vL83hGTMC2s2xDj'
        b'kMvm/zdMQwb0xCRFnTM52PQgJwyUTdt4Jwy/hFH3CIN7TwRyWvEWb0omTz9MOeX3ifqB+kXtJ+rF8N5vg/pvesXn5bswHabfv/ti+u/x//A/PbcUvfrywt+no1f5bfXa'
        b'eKbmrZEfF07N4eTJzKcfYFKaOdB72N+0CsZM+pEJr8BqEzwTn4rNGvt79xUloUYOa7LHgYIRWA/flb11IRxRRpYmV6AcmUA5ASzjg1mclCkJMeXos80ZOqMx3xgxMTcf'
        b'5zRNjqAFHJyP1xhXmNrFq1aTbxf66mZsskYiRIwDnZRGON8OF0p74Nc7pY3DObDWdRgdx7o+qkoOxyoktbzRFtiGO1+dlopVjmGwFV7Gmn+tZPY4AGumuKEr2KjbrefG'
        b'DuJNClzF1IWrV63IWZG7IjUr9cQRTbJm5QcndJ+oT2o+Uedmu2e/n8wB3TnxmTEvC717whH0cBklVw7U10dslDuzevY0KkZf53CQnNtchuOLRwwHNViPwNuosctwsKAf'
        b'PDsNXufhCcD2ToXdnEhPTn89KilsN9znU+fqrz74HW8isvjt8EVJGqKjxGv4LXUKeWyfXekt2i/U0uz3cxmw4ltx05WLCt48FGdFTVg01FCxn6pUpQpqBjoLT/rCixxs'
        b'QFvRfrOK9L5y5Dwq3LFND4/Bw6GJqgjYkIZHY1N4AjwTKugLCzOk2WhbCVUIvAvhekGd6JwnJAdXup2HG2JRHfXdYMWwsYTknLkoUpGYnJqSmIw1T6KjgGFDRQPMz7oi'
        b'hwsaeFoMWTkavUGnzdCtyXIlqEFiRvgYBzuKKLBAwrk6CKbFjmyMcYgTJUju/S4o8bGsd5QYSilkLKwPpzZ5POYHdUkpGC8wgxA/mwSGl4jSYDPT6dU5cILIMQdXpFbn'
        b'r+LM3SxCHvSkNkhTc8mwGIa7Bb3l86KMifvd2r2mt5cuXxHruQ2PGtW9x+BXc3mEb7gqAVPzJYDt9EMMvGSBZdSn9Oc5X6/eNiB0EJv+PvNT0HOifYIvyL2AyWmWACko'
        b'0EwpYYuFxOuhfZL7cfH4Tj2xbFwM0C/4q4oxGfDv77evStJoNSd0J3QP1AWaKtUJ3aeYE3yqNmSHzW7RLL7bCC82+ob9RurvcVLDntzSojurOa0JkHzKviYboh6/8W0m'
        b'PjCk71dvRPX9F3hh9+yF/YPOtzC/O98e80Z0XzHz52hxjKS94BgD2GUDXlyhwjybqD961DIsyek0kcJGdiqszEe30aaeucxjeQ+fozHlUFyTC7j2FNFP3elH0FVlLM/I'
        b'hDvGOKwD/wR23MGwe26fEbJRdCSFj7mg4zuP4FBU1zvhC7dgm+IcNs+w4oqRoS82nfGrPfYYxzHTxXHM/nrtgAyNWzcclKVSK1YrQ1hc4PYjYTUqA5Fo72SKNFWjeaD1'
        b'x6w5Tq2cZZgvYNK0ySwYW0jsALXSf8oQYCRcvqdLO5OhX1PxNmOqIeTr9ZTq5ZFeMMpn+p92X9r3vP8bH7NvNG3wOBI3d1R444bpjL6qqeY3H/r/O6V1xsUXwou++Ufe'
        b'thd9JwU0fXlvUXLTx2H/nDTrn7IXyjh2ZltU1KKjiQGjJw354u/Fp3+eXdAy61REUuuivAU3Vn78wvZ377x28o/W0qRLSUuUk6O27opl1m8ehF7r937+lHGnh/rGtys8'
        b'qNYwqs9AV1MvAd4Z3GHryZ6mHDBEhLavgZdMSoUC1SSHqRIcXu6wJSJsVTVJBV39+Gh4HbWlwjNm+2NPVIZLcqPQHnSTmoxwa9bw7jbjHFjBDRw3iRIEvKzoFx6BqlA1'
        b'cVrABhbuhBdVaDM8Ry1KNgS352JR+sAmZ0WCRTkdVpgJy5Ch/QHhiSpUlZCMTXkPtN4TtrJon8GTNjNkdBQ285Vhigi0yXMSVpMBCJLzy+GRPDoosHYpKhOEA25FkAvu'
        b'pQHEHL1sRXtpA6vQVXQzSWm3WlBlGDVc0FYvMzEeUNsoZXiqKgEPGQtk8OQkKSdFZaimkxX4CEtTXGDJzNULUkMpUPJ4FithPphuxYw/w+Mr/zPP8j/xHP8jz/M/iEVi'
        b'TOMyQtUjnHUF9thMsJOESc5rLiT80iMMTzJuCegyvB0emoJqsBEuBhP6StF5FpbNQbtoe1liF1Lzw/9SB6mFcsS6sDLBoFRcJbGKq0A5WyqxSkzJJV5W7iCwipuZUukC'
        b'YPDjgZkpjmVow4uAISAK69tWKSlnFZMaJgItQ0oaf7KKCubrQanIKjrINoPpYNmupWypW6k7qd/qVs4a1bQlHt+dsIoPcs20joM8zRtU6lHF4XweVjab0wOr+xGmgWFA'
        b'YZ1hOi0lw/DJqtys4nIGQ+xeJSV35QwtKaUlpV1K/sYqMz6okgklHLDi9IeF6kbWMIzW6lHONuL3U8VUgSJA7jA8Ii3bzAi5GxnDDzQfYxZnszRvepWHPW96FUvqduZ8'
        b'jeYU01xFVSJ7LnzXKddpLXdQouW1ogpsxk4H5QweZ0+t+KDE6nlQqpVopc0sSbF64rIntW5WzwBQ6mmT2DywPshp3XE5qZUj5Uq98Bh4lTNa6SrS4j2rl9YDvxUvwxBn'
        b'Oo/T/62VkRatXs1MAHnKaz1LvaxsI2uMw/AyFF7WOFDrZcUlAjHHzmZxPm+D3MpY2VUcfhar9Sb39nSp1scq3A1xKb9Y6yuUd+YhrXlbvbV+Y8i3J85TZfWiV29tH6uX'
        b'1ZPUR54ZvKze5EnBFqsn+W0W3rEP7oUP7oU/7gVr/MbqQ3qn7YvHlDU+L/zCZd7Dd1Jn+jvCL5KOe+mrDcC/gTZwIxsMrL4Ufh/celCVJ2lhpbvVxwGDlWvkjCFmxupd'
        b'zmxgDFKzh3Bnd7cEp859KMnFdr5BNfIhq5R3Eo+sXURSo514kVZgwlrmXspYmZVgM1vIkyrsKmm7NCPDoMnTZWQo2HY2IqqdMXe1590n5upN5qz8vILJ35FEInlL+mfl'
        b'6LJWYQuuw8jryPaQk+cbHzLK+wSqh+752XJzcYFOPtzUDUyRg/rlDjADyAS1lUhw1sRXYZDLGTvIKzoAwzwyjMrNokdwSCPhij84IL5PmnzorZEXaXItOjmGKXS4SUHF'
        b'78Mgk67QojNk6eR6sy5PPlxPHj813PTUQ1+aQG6dSTy99nHJ6Sj90E2eZzGZ5Zk6+UNvnd6cozPiPuOhwNf7ggvpIfPUQ2bIQ7fhpiURERHLcDrRbB/6KuUr8s2OURqP'
        b'/xWydpHeoNWtaXefTwCeQUxFnIRbNbXzWfkFxe38Kl0xtqNxy/laXbtbZrFZpzEaNfjByny9oV1sNBXk6s3tvFFXYDQSW7bdbS5ugNak8Gt3y8o3mInxYWzncE3tPEGD'
        b'djEdHlO7iMBiapeaLJnCnYg+IAl6syYzV9fO6Ns5/KhdbBIyMKvapXpThtlSgB/yZpPZ2M4XkSuXZ1qBixMw2kWFlnyzTuHZo476Sy5YzUxzYqjUgYx/IKhUSZGLqLQ8'
        b'QwSijBFzRJnl8UeKxaOg6MqYINad/g6g6Tg/G8D4MSE0xUfsj+/FODWAum6xWGWJQJXhVPyLJWLUixVUZD/Wizp4gxj/n3GLP7OsPy6FRa3g9ELr3WAdVt+xmlIdn4Ia'
        b'UpWJWKXJ4MalaTvNCxBBKHaQw4f4ggUXawUHARVGr2DBxZXyVs4UUigzY7WW/OuxoGviiHizslZuIiYbYzoWhUwRwN9YaASDgyxmlFwwaMbiB4skHgsBnogNk9bKr2Bw'
        b'fTyuOx2LL46IFCwG92DiI8JBpCX1ibQ8roMjv/A3FouknsIcQcwYj2n5ghNaIqRFVgltS2x/LhJap/WwEwH9zdt/8xNBoczKUseAKBXTbyp5j/RlppNLqvOOpClExmnk'
        b'FXMmnbmd02i17WJLgVZj1hmnk6fSdgnBvjxNQbtUq8vWWHLNGGlJklafZTamOCpsl+rWFOiyzDqtcRZJIw42hfgxeObiWiVxFNoMR70DMRszjaBoxmN0IWjmI6ACRgMx'
        b'taYIevkw5OPH0PnMZ+FpdBAeRNsdM/XVkWTKMUWYIgyHV0RohzqlmyVCmidYRJvrNsULyCRvtofD7LEyDndLV2vJqWVp8aWKvGqmGkv7laDAB6MZLmgchVHDE6cwRIaW'
        b'Mx7Y7KFSCiMFln1MFVflQe6rSYgOjwEhzbtjcGTZUqc/1M3KEiTqaUKAYDYZVOpO/YYAwVuJygBKTuKGOXJPVae5GOdZ3BgGrZxZBTBY+M6KASnlDAEUPDHG7pnkDqfw'
        b'GNtyrRxNC6giKg2mA6JyVYkJ1tvVrgArqXlyKWel9eK8NVVijK0cVmt4g4zc43T6y8obC4jQwVRE67Hy9joKsOIZhRVP3izKZos/ZLBSyYASfzxYIiKWaTQXTlsrMrgL'
        b'3ySaC9MJplErQ+qgg8KkYqQjZk67pEhjpH5QbgVGbMxcjatWG6cShEsUULPD9UnEuIDJWkoJOszNpU/MLDuQWJZB2WQBbjjPNNWJwhhdWdaH8knMD1nCC0Mo95SxMoza'
        b'IRiBBzIlUZqsLF2B2dQh7rW6rHyjxtzZzdvRABbRmaRp0g9M5DRsiCasJAkev5btc+0SMmyYloUqs5zdc3MCNJZxTL9xghQYiHlxSHBJSO99cGgVGlJdLrl3/1UySeME'
        b'R2JvbDRjdyMATj6Uzv+wqxckzQtOTk1VhSrEwCOCRdQv281FKrV/m+bjiw4sxrrfYpYyALHD07GY2yYVfB+YHt2yRTQ8UVrOLOad6YRZSDCTEEIWyTORDfBgsZj63yTt'
        b'vvbgwpn6XF1yvkarM/Y+W00dfiyuEnMil2kQ7omnQbo5/Bz8qVuUXhRJCF5ugmdC41MiElJmEYM/LTlBBVvhvtmoKm1OKGGfNEIGbkAn3BaNDtRHDq1lKJDiJR99pn6g'
        b'/lSdkx22I5RG6b1IovSyDX/IzXygfiVz8d13ntv2wsXGzZuZE5Xj9g/fOHjX+hhPEHPWI/u2u0JEHcuwDl41oTb81YbqVCQMrNDutQix8LASnUTV1PcxD16Etd18FvAq'
        b'Wk8i906hy9SxIYdbw7vOTcejPRw3GO2xUncBqtKh7eGqeHQbnXHOUMOKQoP5GfL0GtyLrsLa1TTygkQU0RCoBHTJPi41sAlVESAiUU0y2kSCN+pgNdqEWTnAmXZ7ouZZ'
        b'8LB9EuYxrAIbBXqD3pyR4eqTXgdyiOrjxZSEdMOZCEcB5ySPSZeb3S7OpU8fMcmDaa6Q3Bc42jbm48sKxuGeLMOfvb17DR8FSu94PE3AYw6TBpGp4myxE5f5/25Krzsu'
        b'S1KFsLNTcJsnDXMJx5hxiLw/1MhhNDnJ+XCplpE4y0yPZWRuNnIW2oaa4ufGO190OsZ9u+vt0mwAloZKcI5meMpCDJyF04OEUqGhGDfjVagGtswNTUxBm5QRCarEFAYY'
        b'vN1Q9cBJ8Ho6DUwrgPWoeo5qfjyqUySmJOPcdtLCWUeha+g83CEelhaib/y6ljMR2aOuL/lM/VLmCd0JzcK7u+DVxtaFxyoUG1sqpzY1726tbi1vWci9uELcuipo/MLf'
        b'B9Xklll3hIhHnre6mSRPS0wxr7M7vDx37dhY95ysSQW+2tHHw2cKpjDqd0JH8aeWUA2qXCIC/EAGHopRUHoZNBUdQvVwt9MJ53TBoRt9qAuuX3AgwpQJd4d2J054PIi2'
        b'APehY6HhEap4FWyIZ4EYHmGj0IHRAn1XwVNFSRGJKcoEWD8NnXI6OEVg+DOixagVtjrm855cU/TMMuqwdpqRl6+15Ooo+fg7yKeQut9Y3u5aLxnUHXc7lXbQKqENTFBE'
        b'5nUQkqh3McQK1GRykpQRXwydSGpbQO8k9TiwutGV01se76Arh4ZKqEua7fa/QV2kIae3wEldXqk0AhDdSBuU5KQXMp99cplAW7nosiWG5FgPj8ItAqX0TlsR6JKdvK7D'
        b'HTQyOAFtR+u7EVi+qBuJTSLT6Y+OnbD7buyxEwqmncnu6muRTszV5GVqNZM3Mna/hYVIf7gdHQKmnjk/vA5UaEsSPBOfAhucOIy2u8xyw8tctJ8Jbp3th84AbIdU+sIy'
        b'dCLBQtABboteaHfv16FaJZVMaHMi8JrNjcTNHu/UJRFwCYqgXFQwBljyvp1clKMaAY/fM0ffM0/fLbeWn+Ny/ygu6rRWXLkomYFeGwjPJZHpygghfAHVLJoTH04CH+dh'
        b'FqBSoIbkhHnONyoC8KDOHd1eKKLTMc2pwrKEqJmn+08eOMge+Y11L55WuXy2vdI5Quw31jGECBnCGPPWuQWhk9Ms0YSS4E24Ddvzt5KSyJQp1k1CUfUCgYnOcjY+DzNq'
        b'1CpB50bDy/qovSNEpjxcdsx3B08Z79P4u5eyI/wUmmRNbjZRSZTGT9V/yPxd5iuZCZot2hczz+g+iftM9+Gfo8C8Ccy8mPK5tpiPX2qN2nZ+3oiR0WXy9Kaj5TOamGGB'
        b'LzX+Vgve+MtzjS+9+tzNitZNI7EewwF+RPDg6o8VEjN5w9no9pDg8M5TOM75m1JYSTMF+y9CHWoOtlT3u3DTZLSRZlqSqnXwSxdmiSpyCL/sj1rpJI/yKVSBTiTZJ87T'
        b'7G15ogtcELrTl/L2VamLiUNEmFgfh+6ER2BF2G8th+r0cIeZmLuBWHM5gfMY0SF7NSLgMYZF9XP7UUiisP610R7JkoMFhSOYhYaypMDtv5xxe5EQlYwCY76Zugko5w5x'
        b'cO51wI+lXiNs7rN+dArFjykZ3Z1R6tbosuxsssPK6FyzQPwiwXzpsPIeN61qn331chagnL0IXzYRzj7EwdnLwNe983bLMpxrAmoc2gsvcWEkV+Cx3pgJie3fMg61imag'
        b'a3Hw0nDYogBD0Hb/lXrUmkuAbVIH8VHy+8MB+OCpr9jLI58VWxk6D588ZTdzXoJJMNgw8U3jaI0O0OQDqV97b/NmQr8Eg8Y8DLoWLQL63x7MF9HA9m1FG4cn3/CEUf7W'
        b'FRMub00f8qcokHWe4yo+fEm6c9ihmn79FZsqg/2qpxZOt/zcJ/B+yjSPoPCHHx1c6DYg9CNR648tObcKY5emDDv7erlv1R9Xtjx/Ju5fZxdbLw43rau7faoY/b36GfX1'
        b'V0//Y+WxtyWo4ceP5yx6IbY59y+bZ/LvJDS8U/dGcIa18Y3zffY+9+3+q+PSXzt6+PmGPX+JEW3vm/PsmfwpySbltS9eU3gKYSCYSyd2MQTwwO2hwYjoMLpiJgFM8OrE'
        b'5XalJglddtFr4E1fittotzYa9WByPIv2wcpl8DKNZlmNtsBmgcYcbxJuhZthFX5p+E0KBkasVrwM3kQnzCSKdIgY7aGaEFWD0M58Nio9RYjmPQrLsrsKEBHoN5pHt7xg'
        b'rRfcb55BsjX7w+uPNECcxkfCkJ7MD9gIr9HAGrSzBJsqAkMiZdG5xbS4BPRF6zl0EdnQSTpWaMeAbCFmh8CGM2Q+A7zmcaHoOLxAbaZlKdj4qxUAYNFpVA6k8Ci7pv80'
        b'qiH6LEEbO9tcWHifAl7Y6IJn0WGax5o3s5v4a4WnqfwTw6tmor3B20vRZlSbjOloLLY2V5LVHL2Qqdsv9RiInRzIw4V5UPYT6mA/a52KI+tO/I3EPYPveNbPW4yv/qwP'
        b'UzLgkcyokyoptqd1sBzJk8DKGteATpbaanx5tpNaaevfu1r5aAAxCHSKwj3DnpCR0S7LyCi0aHKF6SlqF1JNlrbb7knWqWlMpiwdZq52s/NX+GxamHY3e024FtotEuqj'
        b'I90iz6Wsj4RlAmSYd5IFgGPRZgM8gXb0xj9ZMB7eEsPd8JSum5/DMfNtIlNXDn+OjtMKChSg0a2slqtwI/4b6qMRUX1R5PTRpGvMePgMeOhSs/guNTuNW+IXtyvgdodx'
        b'tsSumPFVEqyYibBixlPFTESVMX4tbqfj/lGKWXcFXCQo4B5ys924vQ7vdDJuw1C5gqXhh0mYrC+6aulYvqNqHoRMR5XwMh+fAyyE5hP6+7tmCg+LF4MQk/cYfl6hr/6g'
        b'3zjGlIBzfRpS+5l60d1GYo6+eLKitby1/NpuPTNHkiRZJfnLtL8vrgypHNLmtcP/WPRMuefHupFjYt6M+iT0+Zi3oviYI2DkihAwLsNn3iunFTxVOKYhW59pE7sbm9Ph'
        b'Jco94eH8GIF7wrpxgh3pEyoEtWxBO9ABCnISrBbWiTGz/XQcVrQvl1ArtITp42RSYGgMZVErsSi1KylPQn2u8dXZGAUyiDlIuYSfg0usA0p3mT/Dc1IWG5f9uuFMhLOc'
        b'QC3idi4r19QuzbbkUhpr5wtw3naxWWNcoTM/ViHhjWXkfj25kGXTxnInY1hHCauzVvJ2UO+s4VGwKthU4jQnzMFYTC4llFdSis3TmXPytbQ547OOQeo+I2x1ArYWX447'
        b'HLJSFhM14bHRsCKOG9hB0tL4TgsMJ8jF8DgWrtuoFeG9gi4qVQM3da4yvy/oNmPTmRA7zdk4CRHQIMlfuWyOUHv3ALVgwWc6Gu6PMmHt4aJHoQVdhlWwbSC6gjXzInTJ'
        b'owjWexfIUCsAk9AxEToP98MLFuIuxRbugadRWy66iQVlKqoPT51HLeQE/FWdpnKsj4ZnUJUyArbOpk7Xi/C6O7qzGLU9dk03RwNF/pcCh3tlQb79uHB4IrmDdVQn45xz'
        b'OVTbHzVRBuSH+0FWbNr7iLaHw5ZQBoTAzTysnmJE5xfpfzrXLETf57bk9q1p9S2Lkj3/3qCQoJoNfS9s2LSh8ob/7g/ehu9tu7o11e+vT8uGubtPrvloy6SA2td2BI75'
        b'0x92n7keldc0LdcS9LzXM79d+/Nr9/y27zuvEAn+3duwchU2dbC52sYq8XuEp9kYMuRUx5iu8w0neAdbfAHgxzDwbN4SIdKsDJXBS9QFgWpU8XCjG2VO3nA9t3ICPEir'
        b'zpxiwBlqqBKzHR3AGDqOga1wwwz6dAK6E2cPQ4Pndfb1M3gsbj12NZOHpqBAhwmRMIbOvqx1YBaZHZLRiU93piQMs4yMXH2WzmDSZWQb8/MysvWuNpBLRY5WKdN4hGeY'
        b'EXJQwt2IL3/swlHaHhGJRiZ54SZ4Du5PSlMRNdTx0mF9GvUX4G9BcAumzXGri3XjGKvqyHg61Fq43ycPbZ5GZ29i1ojDyTjHxLJAhPYnwnMMvLhujeBLuQ3rl2Pia11d'
        b'hC4WyqQFhbLCSXAHDwImcCvQhdV0ITy65o7Om7CS2+rmWeTpjhXsFCl+Rmi2UASG+fGlujFUEMIKVDsH7VuahGUSaZHDL+48CythI7pqIaS1bCg2Ak6hrZjAq5PDEpXw'
        b'JKyA69G21cpQ4o1IdizumSO1L2NniLujzePphfC4haz3wup+E9rnWgEtLIWHei2/I9cdbfRXUGUIZ7qAzsHagkK4aTU2Za5gxpNTZMbK9BVMZ1csuDdzeLge60tVdHjy'
        b'4bV0Cu9OIvmxjVSbPAKdkwBvtJmbvRi2WQiTRw3zsf7dqU7c5VNm8rNV5i4GwxJ4WDMe2ajmbCHSbzpZFt/GogsTMK4DTBN5wpry6yK4F21Ng5fWqhLQDnguPkECZJNY'
        b'tD8LHaTMEp6PRnUeKrKkM2mB0GUH84PnQskk/SXK65ah9RJ40zSJtgavYjtj9xwxmAnAMDAMNSRTuQBUUoDx2Cc/S50bPXyqEAHsNklMNhuQnhqmln3ktxTr0DQ5P4bK'
        b'kKCDnurcIMM8IW8mR/PK1w1Ry2RYAFhiCcuCLWgPMQbDia+pmvqXOrNoCiI8C/eI8fiWSUsxl9msPxG7iTfNwPTibtqZkt6airD1/MfU146lePifeP8pn1xZ3z6Z6pPP'
        b'lwXd23/ijcTNexKTI5PmtGSvX7vhlvx2WaQm88OY8V89ODZP9/a119+98d3EDWOiXgpS+o1Xrm++2ufs6ewvJ77/4kdv350eO+KFVwMrG6/I7lVwy08OV24NTNlzaEbb'
        b'9NeDxoTuP5H5ysLjT3mFF36xJgt9PXHN3g9/lO25kJJ4ZflK0R9/NJy8tfPDfW9XvrXSdj317W1e/d+DphF5jc999nrGS+O/yeGPRss//c/aK5mqdxebL36enTnlfwrn'
        b'r3zz8ucH6waul2+Zp7+W9k/3+WNvXONlnyXEPhNrmvw/h+rGXR6we/OzQ/7pXtt8PuLb/u4R88cOuLBlQe2PGRM9ju8+W589b/CAtG3f3V74p5fG3Xtj/TPci+dW/fjN'
        b'vB9e+OMrn799IG3YiT53vn5Z/m3pVvd/vPgp89oLU6b9sfjVUJPCW5iRQPXwVBLZyqNWSVgIB+s9gAe6wLFFqI7ycHR6GtqOGc4CTClsETMVI9YNYRqiwQRbKHtfg+1P'
        b'gb3LYKOwvnHzbGhLSg6LoMxmOTwBPHJZdEQJNwnq5Q1MDkfhTthENzUgr5zMDNaypegkFDxumObvoOPhaQQqorRIUAU6QHZ9YNEVs68QNH3k2Ty4DZ1zRiMLMmALKqOP'
        b'py7ATK0KGzFXE5QJVNCIgPdEbJB42YOyY2FjEpmKxbUrVFgabU7FilFgMh83rpSKGGsOvOIalI0uLmZV6CjcLXTxDjwfSUHDhLUXXZUAXsXAM3nwCh22VUPhxXAyFbXZ'
        b'hwH8YAbuUwwV9kS5EICq7NUS/xOqg3vhliRMkYHEYIgMEQb3iEc8FauCTDXCXWxMKNxFhSdmUEfhFqdaD7eiUx3zSBf6Ps4/+GSGsasR37dHOUhl5+wO2fkMkZw89SP6'
        b'sO6sjzv+Z/0YcnXnfHBakDMWQ0bjz0Lpggw/XMYLp3uxJNCIxKTJWGOlQ2S3sL/QoncJlSSVvNBFvt7qXWOn85XoXOosu3SFB3qXsCKw3CyF25+BTQqOLrIvzBozHu0X'
        b'pv3sc36BaD0VeXNnoCMYRZrQyVR4Jtnu9oWXWHRUPI9K33FYwt0MV6Wq4IFRYWL8ug+yMSloexbXRUMMcGiJJOSk264YwLkvBtNpZwzW1jc7wDmJIXqiSQyO2sr8B8Pw'
        b'O3aXu/zN1q3Qm8w6o0luztF13cIpwr1T3gSzXG+SG3WFFr1Rp5Wb8+XEZ4wL4lSyPQ9ZzyvPJwGqmbrsfKNOrjEUy02WTMFV0qmqLI2BBKDq8wryjWadNkK+QI+NJItZ'
        b'TiNf9Vq5HTkpVI668QNzMQahU01Gncls1BOXdRdox9MIHzmxGcfLyTZV5I4EwpIq7dXjHvZQZJWumASrCqXsP7oU1MqL8JhhmHqswGLCD4XizvwzpiU8PYc+keu1Jnno'
        b'XJ0+16DLydMZVQnTTYrO9dhH2xGnq5GTPhpWkCBdjZwEMBNwHHVFyFPz8cAVFOC2SMxrt5r02bSUMKD4XWVqCED4XeF3Y8oy6gvM3TrSzafiBboaNB7CZBe8gw6grXMi'
        b'HRONsxfEYw11TjzWqHYmimaPGwdbFO7oWvE4uD1uyLi+ADWiE7Lgdb7diMHH0cL8zsQA7OTAOMmBtXln+/yKWbxu4X6Es3Tf2kWVivNRrtM9QrF7cIbdh+WcVvyvVhaS'
        b'5rqvLBTZl7ET/q3/z86TrIk4GK/WDPtMrfp7vOZKX1n2J+r76rzsB+oEDb/5vuwPdfpknWzG4gF18n+lvjnxstebZvm7z73xHPDTZ5s1VX8+JfrslKZRCz7TrcxW6pQ1'
        b'mVqwVxqQcfe8z8sXNKEX76uX3b3auH5zc3mwdloUt0IM9i8d8NPM2QqWSjJ0aTwqXw1rwlWhgpt+D6taC4/T5UKwERuCZ8JRA1HDeQvjjc5hY/Hq/F8+0yXKWG3UFFCR'
        b'NLBDJK0Dw0mANBY8mN/7MP6MGIsbKVOiMNr5mEuYnx3jXVJIjfZtE4QA2w5J9BjAWhihABVDWDKDIRgyugbYLobKwPuPmNAi7gtYiU57hzvIpNP6bhU2Aen67g75NMNP'
        b'EZmIVYWZ8IS3PhZeeky4G0ddOL9u1X83LBSBnhwYklQL8RUFF6FNMVGjomNHjo6BV+B5s9lYVOgvs5ioOXURqzKXUSvW0dq8pTJ3LzdPD2zgVsE6FitA6IobOoMNpcvU'
        b'kvjDhESyLlx6V1/knh3qJ5gXT+niQSMAUXETC8I2SCx2nP/n+lmMiU4Kfnqo728H+5VFyfi7N0aJa5nbG+L+xSmvviJPP9hn3vQDf/pp26Gi2NcK4e5DYU/veHlYeENx'
        b'YKB38IhZW0ahf4IFrwdFlO44VvfzInXUvvSEd0rfmJb1t8ovfgRXkX/5rJkYvakDpMFCNVC0Fx5x0ULXCAtd4ckJcL/Di8GhXfCO4MWYXvqoWJfHR7IZ880ZmcRax0Me'
        b'5IrvMQTf/TCmS+kygBLlE2G6vTrHhIozmvzRMW40Rweek705orrh+WuPWB37NM7XLwzaBDQPgvu6YnoPaI5qImF1WnQsB4pgrU8E3IDOU1SY7ssSRI+/yqqTJ7q5AwvZ'
        b'UsBqFaGtInRlEQARIAI1zaZZy+bS3fKiAkPVslUWRkClU0tENJDiYpo69/owiYBK9IkiyI1Im4LXc9W5UcqFQuKAeIqO6jh/9UpeqRcSn1vlA+QArGm3qpVninVACONp'
        b'hjvgyTmoHm2bNzoK1fBAPJtZBffB02jDOFps+fQQMAoX+ypQPbF/pptQV8Mz55kyLEO+nJAb+JH3X6fSBeGoEW5EDXNQiwmS6lC9CHBqZvKqURayb5rbgEkdjsB58di0'
        b'QVXKRNV8VAFvoypi6tBIDrQpnFgLsDrcXQEr0Dk6W10/RAKwsppTHA9kbwcNHzEC0OXp/uIR0vSnfKIZdXKSMUs1piD9ldhpEX+X0HXDsA6eQE2ojVHDcwCkgJTlORT0'
        b'lb4TgBmP75YgdfQbMyYK/fm0dDKoACA0btzLo6coi1bTRN8ZU4AVt3p9tDpa6WXfzPCgWcmoWeBzd1xuiaz4+hqaeFj0FnORA/F3x5zOqBafY2git2gms40FcXdHKwd9'
        b'7/1nK000rezLEDS8O1kWuM/vZCJNDBxrAV/i77gJp72/HBUpxM6Y+89lTrAgasxAjUfzUF+h9eD4RiaUA1F3Y3LDvwn9i+AH0ZQuAlexzhE36fR8+VOTigWMWT6USWbB'
        b'2LuTHyxdGdY2nyaqRw4E00k3J79sOeQbpKaJn49IYQ6SHo1+ec6MpXOMNPHY6EBGyYI1hqHqZS0DxgmtV/T/E3OQA2uytZrIvn2fFRK/ynkBVDGgoGSqWv8xSBcSfeeX'
        b'gu8wP4xapi7KLygUEmd5vguuMiD92wz1oqQRKUJiWaYMYB6Rc2m+WmZIsgiJpuxCUIb1h4KRJxd/OZqP0Z8/kyYyHcYpq66+N2/W7xtej/N5sN82aG99n4CCgjWR/wHP'
        b'a6aUfbSWGSf3eSeRUcwe9uGtsuzU7L+97fHV5sN/kPxrdJPvpOUVFTNff3fe2Zb7A20390vCb5z4x/t9L70xIq89tf3HouupBw/eyZ584di+M6Nlp9VffPf71c8Mzv8u'
        b'zHvclpqzxqCLz218f9qF7bnl9da0eJvvt3W56nOZoxvf2vLnuOSGc9v9vh6Z3Vd1Ytbm0oR7n80YNz7otxEX+rx69OT09T/OrM74eEb5/XU3i0Le3pKpTHip9D3+T3nJ'
        b'v/126Tc3mxeKZl6Y9db25/2q3/rL6tCP38lN2BV5CJ0e9rHH4lOzrU1jHxRN/Tb74HsfVr6s3VcUe/3Be5Wn0wqizr+s+/m9ywPuzJ7Y9120POq1M99U7b3655wDfP1f'
        b'QlvvDpi78MOILz6YPPD9wQM/GOn1r+kjJhjdf/vVa0+99oeWmDUPm91f8F47468vHm89/PCpI1feujgp2ry56IfvA+cs/XBS3r3jWw4kpL736vx9s3a9X4z+8c3tLxe9'
        b'GlFf0zDlx6LqpDHX53xb23po3fb7b3whu3jIVzH1H19Ffrz9zZIZm/845SdmbP9NS063KKSCcNmONk0Kh5WwzHXlOLZdLXR2rxgegvvCUVUk6AcvAhY2M+lLB9CCw9AW'
        b'JjxRlaQKSxUBmZhFVzCjvQWvoc1UK5sfqHSKLCyuMAPehkXWnH5U3sGD6AI8EY4OYcFdnZYAT/Nk474hWWPojGNfWD0yPALZRigSw+mmmyLgjcq4fHghmDpdMHe/ttzF'
        b'qSM4dHahSnSFLRDcI1fgjiVdt/PBfO8UrCMb+jQO+KXRCD6/fP78ibVOqUOWUkGc6SqIB8sYng3w8nHnGdft0sj3QPwdhD9+zDAsF/tjpdSLrt8j05x+TAD+dv+JZdmf'
        b'pJyYlpLSdSwyXI4nsxIhvYt0QVsV0YU17RK7Ldouogamiyz/71cqYo14E7mnK3ganSpAPZGM3VSAv4X1rgIQlz9sQqfglp51XUEDgDvhmQ4tQASgDWLl8Caqz6U+e1g3'
        b'AF6kc2ROh3KHqwXVwaZIeFGETsOLcB/1yAwSY1xvc/p2SPy5D9rImT0Hhiopd2SWE2WioFgK1LJ9Se4Cy3xnCQm19CmUxamVryilQuJkN6pLqDzl6uRLz8wD+jb9nxjT'
        b'AfzkLz6mAXWTvGCUbObnI/SvX/zbGGnhU7Hzj0TMf3vJTLU8vsjALHi/YpdX2oUpU9b5/ebf7hVuB0LDI+6d/9uW8LPXPtgRePNjz/zi9wLGmOc2Fn9fsbrRML5mwaEP'
        b'/ZpSvrjwx38dC/yX39aXPmD8jk0te/DOO7c3N50enl5cVvHsd/KTk9a+EG4Kuxf4cNOtP3k9ODNqz4J1S8Ycbzuwb8v7/Ld/k3zBRi6bLFFIaLz4QqwB7HPs5Wzfxxnb'
        b'ZJucezmH5lMrbixWxXfbvZ3U08kmwDP9YoSY8yO5JKDpNGUZTocZ2pRMpiH38/lJqEyIAbsMb6ImV30Oswe/MG7CJKxH3IRbKYeYPCqY5EiF+/o5X6EXPMtNxzhwnnIg'
        b'RqKHtZGqtagmVYVqkhVi4N2fy+gL9wlhWJfQ8XRYm442ptkVIOducP3InOjhKajMYV4G/K+zhidmHA4apowjzJVx9CcRUSwzYqaMEj1LFvKyAXTxmpiyCuMWnNtu4zeQ'
        b'bvT5v4Z7s5PASdOSbgT+n9jeCZwIFAMqN4Uneo+wEzgLvGO57AS4t8d5cPJnkjEd0URaZjGnZRfzWm6xSMsvFuN/Cf6XrgCL3fC3+zZuG68V1Qu76ZGABF4r1kroqjAP'
        b'nUwr1bpVAK271qOeXeyJf8vob0/62wv/9qK/velvb/zbh/72pb99cI3Uv4rr9NP2qZAu9nW2xjhb89f2pa354WdS8tEG1JNd9ci2k4HaIPqsTw/PgrUh9Jm//Xc/bX/c'
        b'Ql/7rwHagfhXgJZubKAY1O6VLPD4FI1Bs0Jn/EDS1TdL/Ied88hpQEmnTI8roTcRRyH11mqLDZo8PfHZFss1Wi3xJhp1eflFOhfnZOfKcSGciUwQ2J2fgufR6dSkJSLk'
        b'6bk6jUknN+SbicNWY6aZLSZyCEAnP6SJZJHrDMRLqZVnFsvti6Ej7K5lTZZZX6Qxk4oL8g3U06wjLRpyizu7J+eZBI81bkpjdHGyUlf0ak0xTS3SGfXZepxKOmnW4U7j'
        b'OnWarJxe/Mf2UbC3GkEH02zUGEzZOuLu1mrMGgJkrj5PbxYGFHezcwcN2fnGPLqvpXx1jj4rp6u/3GLQ48oxJHqtzmDWZxfbRwqL/k4VPRyQYzYXmMZHRmoK9BEr8/MN'
        b'elOEVhdp3zn/4QjH42z8MjM1Wau654nIWqFPJTtnFGCMWZ1v1PbuQYoD9gWTdKFZtugXLpnkKD7zDzd2d2Eb9Ga9JldfosPvthtiGkxmjSGr6yQD+bO70R2QC550/EO/'
        b'woDHcWp6gvNRd7f5E2zwKhaOV4DlsAZt6WlZWu7IrqtmTi+kq9KwuLv1tKteEhqvjIjAwjWRAbFj4C24U/wsujxRwdDVdOHoDqpJSlHhjGkqsmyjPo0BfrCJQ+vRznT9'
        b'nU9niUxkC4E+V9PI0rXQD+/jqzLgvjrevtwiYn6oJlHDtgUHRq2OitQuvXuhsXnrtXLFutraS+XXykfWqjZe29lSPnz/JPvK0A3LfPflpmJrgkyQTUJH/WGtcVbPMpxG'
        b'XNN48EPwCrIJItpVPmMRXjYdbUfH6eztcnjW0wN3WuE8GaIvtPFo9ygpuo4a7KvYFsBKbJ6sQQ3xo3jAoRuMYRCsEYyMDfDM6iRhIBh4O4ZuEQfXq8dQwwadgGWFqDZJ'
        b'JcFWTcOUFUxSX9Qm+JObY9GpcFJh9GhuQC6QlDBoD9yVLZhL9X3QUap9VKUki4EIVQ9Apxl0bd04x+qFJ5hTJAG7VGYHuMrsdcBfRhdSEFW9JLAz6jrXbgoyu0UIWDbu'
        b'BOCxCyRaWCFb54WkNaxjmXuZ8/Odf++RiL3B0/vCLqLZWsFKwd3LEL7g5jAxdC2MAE7nRV5GC77sxoAJO+l0bdKxAuxhcK9Ta7gRTpuf9URA5QhASTPsJo6xqReImhwQ'
        b'PfR3mV5zzNJFPFFj2Y7GCOPVa029NnbA2ZiSNOZQ8XqYzcvK1WOGrjJhvq54MiDsPfbI0K0p0BupzOgVjkNOOIYSODpKEKHUdeA7N+9g9HQrzDjQsUGwTeTC6P+LyYJO'
        b'+yO5slhCTwHwENozJwdtRvX4EbwE4CYAWwVf44lCtB+ewrCWAnQUNZauW049ou6jn0K1CYKKfwpujMEmGqxlE4dm6NfHXONMS3CW/0jiBtS+RKIeueFP9deX/SZnMJe8'
        b'Mn65dWnlu4oRkZ8/yBndMurmzXGvauaOLR7+/da5Ky9/PPZYS+Y1iWfosz9kHVVdHi+ekFebee6lcasW7578yZY+f/se+AQG8yPfV7hTm6Mf3A73uto1lHOiTbDJzj0x'
        b's6LuEbQpU0X8sAmoHq0fTOYK0A0WVqMd8CblX57wskqIZomF+x1TCfDkNDMZHWWGmBppsHwGCTFIZeD5fmg7ZW1ZkumCxwbuQDbBa0NCJS/D/bRZchJEvZ3zoU39KfMj'
        b'nK8AnhFYMf5xNgk1RKLdOnLcCx/LwJuJK+kzizaabi6fNMm5eB/dQLuEuY8z8eiKfR/PISn2nTzzUatSiPFsQNuJWR4PcTbCyjPRkQgi0U5xqFK1stOWgE/CezEF6gxZ'
        b'xuICM2XAdMf4DgasIDt9+FEPizuN3+zO9uylXZeNPNnun/Y9mzu48FF8OdoDF373l3BhOzj/p4pWTo+K1tM5GsMKnRDD4VCNHGyhi9qFtacn1bgMutVPqmiRLndfD8un'
        b'2g/OMY+WJblqQajpKbsiBOsn6b84tIWn607nPzugb91gv/Iof9Fff/9z+qcnx4lusQvizCdXDtlVtWdx+q4Fs65OM75e+faitje/zXxBtuiDtz7efaG/u/sC6VfafpvW'
        b'/g1+7FHk4z19jS7mw9IbH8V4Xdo/8ZR7S4vtclzyzhczGu9cr3J763vv/9keENHwtcJN2OByNzqAbGGoMtxFbYG3BlIynLQmCNamkZW88CS61F8ZygAvVM/pVj5DF34F'
        b'R5tdqCGCCVhjJwZ0LlKgpxa4R4L1zL3Ev4FqGMBHMrANlQ2km4AORgfhUWFP46Q0WB8p6JJe8DpRJ6PQQfG4NahMmHI/FgvPUgWpBJ4mOhKTBI9CgVXAZnJkk0O3IhSb'
        b'OQCrVkPQNcpkiqXRDv0Ja0/GLKw/rURHKBcZbMXjX7sINnVoUISJwFZ09ZfTsncWxcEMB8J0DcQmn/Hu1PEZypQM7EI7XQrbnSG7e6Vg4x4n6R7Hl/M9kO5rjyDdxzSv'
        b'4NrFOfkms17b7oYJw2wgakK7WFAXel/TRMmbd65nEjnXM4meaD2TI0ZrGtPFD0D+pmq1xIYiJOmiewg2qFPy90rXQmcEqo7H9wnTHdwhU2NY1Z22nezA3nehZLrwExcO'
        b'TbIYsAWrSpjeQ+CSSxCUoySx10mxTkFPip7gNerMFqPBNF6unmu06NQkdknY1kGrlKtnanJNQpomFydqi7EqRDQyg/lXsScuVX/kh/+wJuLz/rwl5DP18ruvPnfvuTee'
        b'u9B4bUdzeXP5uNrW3a0ZKT+c3NFaObK2pbJ50+Cm9dWDN64XSffuDg7eECwLrlHJgoKei/KrmlOW2aQHyWmesZYHCs4upWHLKif/IMwjty9lH2v6UtKEh9PnC4xhJKqw'
        b'8wb/tcJ28ae9RyclJ8Dq9NlpKagmOQI2RKpINKsC1ongGcw4jv9yEvXSaLUZukx9lolqvpRCfTpTaBKhz5IBXcijczm71SMWxOcJcmkhl5OdJa/rQSS8S7YCZ15Kvqfx'
        b'5VYP5PvCI8j30fD9nxJoBSbQZ3oi0NnUk4Zp1CAgJQnXc6FUFx/a/3+0SoolzEmTC94vs+Aso3ZJtt6gyZVrdbm67jGGT06lHndTBSp9pnxOJyqVznSh019GpZcrMJXS'
        b'1dtXl5LlIS5USmjUjI7qSuZTMtXC6/0ImcL9cU4R7j3dTPA1bQiqCk/E8rc+MgnWp6VwcL0rsU6BDRK/vuCXU6qv4Jd9DLEupsTaRcGL6FbULkzPdCFK41knDZ7Hl5d7'
        b'oMHLj6DBxzb7mEOcGBtwOcTpyXbC56gByj/M7IH6KCpSMjFY8jIxxWHsc3FrdziLsyxGI5YYucUu9vyvRUx//nXWRPY9uzXmZXJO1PnGZoqQI+0IKTraO0rWu6DkfXAv'
        b'0qP2ViVGSWpoXYHX0ZauOGmBBzgd2ojOU5VwIrwSgrES2bCF6UTLGSvNZKkotlaP+lDzr56coJIBN7nIkDAxxstrEjm6FdzlKK8eMTEr32Iwu7xWU0+YmCntCRO7FU11'
        b'BF8W9CoqBB8IxcoL+PKXHrDyeO8nVz0ehP8jrCT+b0OvWNkRs/3EGCkPDSO6nt4gL4qNGBXWA+t+Mgw903iRpxhaUDqzJwztFT/nRnXC0GBwL8qjbtBIu2oTC49Hd+Dn'
        b'BHjeYRmZiwXD5yo8GgFr4Wa018XwWQh3CPi5Hu1EzaiWRbfJuZQYRTvj51hoE8M2L9kT4KcPGdnHoedKYSOzLrjRtaSdT7b1jpGX8OWjHjDywCMw8nGtKgK7rhqXZGRo'
        b'87MyMtr5DIsxt92TXDMcEz3tHs51O3qtcS8pRGITjM3kchjYHcrt0gJjfoHOaC5ulzr8sTS+o11i93m2u7v4HYn3g9pRVBuj4oBSH+3wr960wsWJuRVfLGTgZhI8ZXkP'
        b'nnH5sFLG3xMPH8P+JOZ6+eb9PHAumYzx8SL/XlLh+NUbsAU2wlslHcEf6FIKNqexLcyCULhetG4FbO42JUR4QByw70rQeVZa2FOivY99JYz95dHdyB/KZ6whm6USv2sW'
        b'WeZiNBAlz0WpS8XGaueXabzsHIguft3b+PIZ61zkzzN0n0RYW4TOdKzxR+dxt9DhGNozx8RLorsEbhoBT9FwbOXa1TFR8A5q7hKR/cTx2PBcn2480cPBSUhAsH2VA+h8'
        b'Ym/Hds7/zQGMpLHuzmNZqoKjsTjPLnMHmF/E32DkuUGrw2bSwFZRupgEtsrBzFzl+KRxoQdALlENZ6RNEt0Purbi5xn9FNdWpWecHHRi1fWFG0L3pP5m7KhF9cp9aWcm'
        b'HB2/bMDrYYcyf1Q+TFnn+fd+nqU3550PrciqG7jK/48DvmbRJNko/7FXR24c9dvSopSxw9eF9pkQOm/NlMt8ht/RgnODMjP+or8oGTLviFo3NnHVy26fJ0wK9wzMWWgU'
        b'lQ35+/Qi909NRQWhgW/POOkR7Hl93c/Y+rg7MkEiBPpumd2P+LVhHU9cvg63dopOOO57PGveQBm4OrkqxR6e1Cb1i9gpHPHUv228VUhcMD0gSAwW4v6rJy7SqIBlFMGa'
        b'y5gQzqPaFFUEOY/ZsdEb2pQkQdgGLUbVM+B2uA02ioYDWDHCDTXn87S2r2WiiV8wPvRAoOXLVUITbwyS9I9jg0gTsu+1SmGT4u/Ox2dRynn1HWZvtH7OT0dFJhtOCJJU'
        b'Da+/4cmNlD2teOl/CgPG9ls0YoJWZLnvpfh8RGpzriY/JPitqjVH4sLm3cvMvPKbFdH30wd+08dDFBYc8kXO3Jfmb5250ZywZuPX/xqxrF/pO9e28O/6hfXr/+dAg/nS'
        b'vff2HZvySdlLzD+Pfv95SIpV8/svb6wYVZi/d1FgRnX5vpHfV3/3I3fq9Ijzb05U8GZ7OPUpVEYc2H5ZHUdR5ctkwtGpNmjjXEOjsIF+vNMx97VTBf2rqRgdDlfRo4Xx'
        b'KIoAbIVbPNB1FtNUPWwTVosegDvQrnA89FdQTRjxvJFlfuPC0I7ukfW/dh9p1z0OjCZNJ285XQLZIeKsPI04JFu5S1kfRk54Kr433nVU08K18ySEwUXt+rVgtTBG6ORj'
        b'pIF/9yAT6+S9hxDJyfhdEKPj4WGpsM5Fy+1HliDv4+GpkO5Hbfa0f6cLU3Lu3/lf7d3R82yWu4Mh5Yz2AKHa+VhnxAxpfMswypCCVkoEhpS9NfDtoAJ9lcCQ3hjzqxnS'
        b'06MT/5FaPPWDgeIQ9/7vLJy2+KPJN0Y0zZ6So1H8twwpZ5JRoPIPV9HlFeAvnurkhDWskNi4oA/AlBKXJFFbhzODhUlHoecL6WoK9e04de7gp/sLia/m0FhJNReuzs2X'
        b'9wPC6WjVcM9axxReSoiD06GLK/Si7w8BE9m33HL5K9XvWz0RWcdzfPmFB74VF99+Mfy86R9hM5YqmMlL7u2tZO+9+U7j+399/fMyedF/ZukejJk4euyge1enTDqXfr00'
        b'4Omkp19uaY65cP9yWMm9MWtvDAhIMdWFK2sv7P/3zjXws9EPl7Zafxq9asClZ0MUDPXzj4Qn4cUkIlTT4OEZhDMsY3Xwel4nHfOXRSJ3JU+troM8h3Umz3XAm8QS+AvK'
        b'DiVRGSVY4/POip77FRAgJx2SeqScYz+2MpfPw963O6NhKimoYr5AiAkpDjpEbTFqHjbDw6O6LZgk/3Rn1bmYQqtEwvkIVuYgIPTXzJay9J7T8vieMzPk+XTQyCyTLWVL'
        b'+VJyioKoCphZcr6H0VDiZRUd5LSiZqZUtAAY+pOzC4pXCodm0SfkOC3RImDAFGu4ayUHNkXQGkjp81bOWINziZqFw7PE9AySENyOuFRSxVgl5JwFraQe57eKJ4LCLYa1'
        b'tKwIl32Ay/6GnPiBoRdhKEX0XAdSVtqtrBSXfcUwjZYVjqmK6Fayf28lG5lCaZVYyI1TMKPGtYUK50rYj6BKtQKtWzBmNFZBSXJPxaxapyuYaSTrqeY+FFnM2aqxRhKA'
        b'hLH1BfK2yQNjJLmQvV4VEuMKgoVuOoMlT2ck544QRbtdTE4O0OraZfMMenJD1Vih7DQB2Tp29uyolp7kQFeBkZW4RrKIvp1Z+Uv3/5KRk35M0cLC5RDObmCTsw5k9iNI'
        b'hFNvyPk17vYzbwJc7mT2byk910YqCI0FqAG2JmEcTVDFhtE9isiSA3gzSz6QR615+m6RF86dzgkLsAKTVMvMAeTUMjr8bDlrFwJ0GI3jHV0gux6berE4PWnHMsz5Gbn5'
        b'hhUTOMe5uByxZSx0Xm/RJAFGbNBibkj3j6S6WBk8DEbAjaJi1JbQ7ZApZ5zaKAqqllnFGGXEINFyVnI8GKPlDwJy6BQGXBQAmhkrEwiItCMptBtiezdopAg7fA1d8Xaf'
        b'FfojKsnW5+Yq2HbG0M7k9NY30iXSNdrHaZx9e0Hy1nh6yhDdoWouvL2GrEvDfSKn0OMeptHuirP8wYiBouLRqx6zbprpcd30k5+G2c2OYFybcFmx2rHmj5MUgvcBGBuV'
        b'9beYLOBjXwgofZ6sw5Kfn9syf0z0EiExV0R3uPGJEh9fM2XFTKA3vuXG0hNpxAs3f6ZeRlwoWy+Vt5Rf2v2njYPfPLmjubK5vLmuNf5UuYXJ8nza/aNpx1LfnLY+pFKU'
        b'7BFcI5IfGqD0Uwx4ebTsD3WKZL84v0Ns6G+k0cM3LpKFXi4bt1E3OCuKW+EBJs4I3honxYos8TkvNCwPV4U+g3Y4V1ij/fCIMN+7JQWWuZwICVvzZrJo3zPoAnVnJ8OD'
        b'ZBdQZSqxHDcpGZzhlAfazaKzeQrqONTBLcPgqURUG+NLYhix3rqWHTKV/+UrtH3z8rXjxginqWRo9Sv05q7bEdu34JJSYiZEHMIY33BWUvMkzdU6mqMFk3oUcFcesfI6'
        b'DOdNUcHa0WaMsfVpsHUU3amZHHFFjlW2j9FYeFy8Fl2I7p1/EIVZ4BpE0DUz1BPNpraLNKYsvR5rxC8Chzge2nmYJDm6Nbn67OJ5BHYaGsJZiPyMQbvohmlXjXTLOgwK'
        b'PMUDD7SRRdeHwrO9g0LYNTlFiMpAf3L2FgGo1A6eHTDjnwFV1Gc4wHrUBmpuFoMdyMUd7IxoJxRQeBNt9g5H9TTUob+3E1Sya92+rGG/aMwqHKAZ3+xtvNwyY0cJp8Vp'
        b'XEaMCKpkdAHtToqOScBGWIub/axh78HcBNiILv4X49UB1L0nGi0MoCBYs7uMFqG/QnQaNhEgE9BFUYo9nBad5Uaiq+ZukXnO8w/JLlpaBvN4oj8BY6iZSACunMVaBSjl'
        b'hNPRrCzm92yh1MoWRFsZclIZfdei1PZhUSOjY0aNjh0zdtzUaU9PnzHzmfiExKTklNS09Fmz58ydN3/BwkWLBWlA9FJBZ2CweqAvwjSs4NvFwpxJuygrR2M0tYvJDiEx'
        b'sYIm4Na19zGxwuvJ4xynrnCCI49s9iPsCbcVY8uBpOhYbIknLHe8qEBu/Bpo6/09yezoohUO56JY/K6jccye/tojssTECu9itQuyEBY0axHWDTAECWsWOd/CES4KCyoK'
        b'4jB4Gl0PRydhY2oK3eaNHHIEsYV/3jfiMXMEbKc5gic3Np/wKBYRCZoiPvapaBs8LbgqMKM+raJ7tnov4JbMz6VbvKEqTRa2rAAIQW1LwJIUtEnvEzuUMxE9cd2PMZ+p'
        b'Fwre/srBta3lIzemTW7dOXJjQhOJFB8AloSLPt1WomCFKMYydBhtNcE95GDyBlQbKQFuMSxsRpsiBX/IBS8MRq0SNYxGm9PozlspmGv2ieTIecoHHKKjF51Cb8rPMOvz'
        b'dCazJq+g62awjg8nFRs/dr5srl1KS3Q+TMTVUmOMf3O0QMtZe5QMlb075qkmA0/Dw4Nox6gig0daFZGA6lRgXQwYYRStyxo4s1s0X2fnKGeP5nNxjdoYp3P0v4qspfu4'
        b'dkMP31S6xRS6MhM1JSWqsJxvQHU8EIew7vDaXKrBTJ0RAMpMi4gDz/qu+yAgHPB4Gm0eEhMNW6OjANyNLg4BklQG7oU1cKvw/BK8Pgk/vxwNL/HoRD/8HO5k4OW1cL2w'
        b'oeDlmX3QVhEAEahhDIjQw420rY90QeBBBoZbrV76uUFh3yRQHwrGeh0kidP+PCAJ0IDfdHgUf9rwcE6ADeg0mKBeSjMP10vBN4uGkMzJoqTRQg0JM3nwYkRf4phMjhkr'
        b'w++b9joWnTMlJfDoFDytFAO+PwMvwBq0nhZZNTMOLDSJGFCg9rtXaIfkdelksCvoJwCi1NFT4hKFRMsQMThBTF+5OtkrczrQ+x34AJgIq0kcVTEj/bnE5+NkKdGv746d'
        b'/8dlPpsGvuD9ZeTEqvdHVl199elvD2kjGqb9++B3bp8f2HPh94lrNt39/e89Rq7ViwzPhWSVJ75+7V+yDR5f3INmnVL+zYx+9/5170al37CIj1defvP/tfcl4FGVV8N3'
        b'm30yWQhZWELYs7Pvq4iREEiQTUB0THInITCZhDsTljhRBGRmWDW4ACKyuAGioIIKKu29tmptS1tbW6doW+uGy6etWtvU5T/nvPdOJiRB7df/e/r/z5d5cu9973335bzn'
        b'nPcsb56dvHOkY+GRRT9oWXnFgcLZ5ZtML5QeWm/3jz3d8taGo6+fSZu+pubzw32e+nRLv2d+7A6embqo9If+07/5S5L9jjkHD7QE1FG7Ht8b/DN3bnbtfVeH9mY1fJj1'
        b'z5aRtUlZ14sDV/z6mc831v7iw9+f811/7z1/fOOVKXuvPL3p82kfj3n93T77o9PeNYdzzcyd0Qz1McYHKVE33Mj4IJPVk0xi6X5t5xCGW6r3z9PRS0Auh6hPExOlt3ZG'
        b'3ZC/9Np26ukedR99dNibdVHoUpO63xCFlpykBVrYv7ujdLy2/mINEqu6W70rgPNjivpwz1JSPxcy1DuW81P4Sd/dgeC/g8Wa0AB7n8cN4Grs6KHDCFBN7AioEiSesVph'
        b'vxOdfC903CpIfD9eIEI1hc+gd8x5q/JODKQxIyxRe3W9UuVxk2/QNsj2r7jxE5R3OS7eXAuWtUk0tE/Xtft9eQluLMmbHVirbsqfUZBHku4ID58cOmKopD2tbucG8JJ6'
        b'R3rvRqzutcuXzOPS1DuAyOX6rqmqMvQ78a+dqNUyDpEudAsbAcoOPXmGkYg1BSWlIGiCfwm2elMGlwqx0iFOUNjPk1C0vrOGRVk00m0Qmb9viCUqlWFpP7wPigcEyJmh'
        b'u1JZB2o65qMWsT9y2ZzKaOUgZJhOTkN1h83LOjhsJryn892MvDUfFXUiuym70lsPxA+Te+rMxzRDtcSoqbGhwaMoeBAflYgQN0elgGdNADAYzMJf2+SJ2vweFMcKoAvl'
        b'1bVyYJmC7qCjouzp6EAaqvcBPr8fm77O+LocEg3pW9Gqs1IkPusbSURzjrT1lXPXlmqbtUg5I4SMPZ2f3UfbJ2lPaDsXd8BWY32Kg4vYKmHVHGDVGcTzQwfsMNj7sZdh'
        b's5JF7GXiCApKJQywIEsQQwyK6MIe/fQ2iziQlMMSeEsO5PE7xIYdUjbR4JrLWnMmLp2yps5blD+FMM9aX82ka/oNvjbnmuvgmp+Lz0V5U5ZOmUxY/AWsLGOO/ZgjEhOJ'
        b'oKjZ76lQqpZFTTVKfWND1IScKbh561fDwLxISzQqQilRSwPKsCm+qAk6EhJYjUIvRRQkoUVNSO02Ip8QDUtOomQYgyCPuwx2SMyoe/Kwq8k45ZwJ6qNoykeNlDPtC0RG'
        b'Si3c2Fyzetdc9Xg7LKTdqentNBZADwipHNIHjKpRAqhmpAzA637+AOcvCgoy0A9Bzo0KSIIyGa/0ZXoQKA43/E/nrk1pJkoJchPTYVR4buUMiu2Nxd7OYvt6BHllO30L'
        b'X/xNx2aksihvbxWys2kooO9oqn5GKyBQUeuFVSF5vJ46GALPKo/3Eosu6mxQPAFUl8Ue/mFbxzp1T9lJ5M6YnX2l8kxT8zSQrU/l58wszCVyVd3KOphHe9B391UPmnK0'
        b's9qzXSusoxP5NtEAAEncEtEjketSDt2T3i4uNy+3LLHCO3RZiu8sHstym2wxQujSFMAZqqtbl9jlfjrh4JCdG21LHHJ/PZwguyDs1N1rSCFrtUlOlJMgTUK7d8lyCrxz'
        b'xd5Icjc5Fd4ktovVXU6Dd0mkps4tSZYHhMRqnhTRbUtS5IEUypL7QKibPAjSmKEG2XJfCKeSM4/uRA8PjjqugKHx+ALTgBJsN/kMVuU8A7i2sf7J/TYnS8az7jw7yjfT'
        b'FLjwDfy18uMBd8cjvMO6A8CrYmMdt5rctDrdqFfob6io8rwao+6Epl5xVSu6OGKn5CXVFU+xkfiH6WrwIvgymHBmHmFsoKKmM/W7qK3BW1Hrc8PnaFwVusdXIRajQ9mC'
        b'UXYKx/T+6l3GgtQ1AA8LUZMb9wFaGJ0qAOKy+VMbcduUFF82Ju0wPLFinTQ8uOblWIFAq6HTPhPfeUnvtLWyA+UT41B7Y8NOEJ9nXGk6B5mB5z/ME3ZQlIUVgjJSRv6F'
        b'MBE9XMPqWcX502RTUMQ7wHweT3jgjYWlSuOMuDKPXuEPMI/U1rJWfkiUz2sViobgkGFtcaUqEg4ef0Or6Ya85oF+3Gj9Dd7aQNQOxKYS8K+uhU0UN11DO4xs9WPfRPmG'
        b'ruhVN0Ab2Ic95AbgfdEQJ9O10NC5UQ8hhW/KbDcN49OUtbNtKsb3XJYxCannAuwgQthPfXZAMNRCRSUV22XyNwLSgPiCTzaEJrEBUXtsundxSKGkQfq/iTrdiFVvP20w'
        b'x/9GJavbKql0x5paMMMKr1dJ57vEnDLhU2u7KnW7uEqQQ6ewhmqFKvthmEphCRGOME3s5TAFtwlUR96o4wGe58jF/LJcAaZ71OTz11U0QHV7xqprZn4edBekUYuH1eO7'
        b'KYz3ghy+FnVlXo6Q/iS+KSW+LSz7rjt4KGuKEGuKEGuKEN8U7G5ojKA3RunB00Ya15BatBEVyNUnx1S89Oa/q+p7FsSUpHYtSbmoJSz/DoMS41ohgRSGmoZFaEmeAROU'
        b'bMRHZMKym6E1iBHiSg4I+lQS9ZWNLLFWfirDECQlBRuGJ5msdQ63G7Cq2oCnzu02dotZ3Leb01SyUUFDMg6vCONCvKspvd2Sbcu865G6Ln7SFV2qfWysfHmxcS3WxxW2'
        b'QhpXUR9XyYirH2VJZUof3kBYe7DBo47AsuPGGnrDb1TYGPCYwc7vNuD9IJ9kSd8LjX5xCXaycdC+b2JFfYuzWIN/Pp8V09kWanW7K+vrvW53T6ltB01tXxyLQPj6/Haj'
        b'YdAdyJ0gDeEwrJQgV40YL4847V7YZ+7jtxuzqRi65h9cDGdcC4C51heIJiJqLnuqvBVM5BXV/wP17HDa2BswmTIQ+5sOxC/iNJsVD7p86tM2rZy88I0E/+1XDItW3Gkj'
        b'aEplxxoh07SRhW0SEUU8E5owmPpS1bCRPtREZP6jojbPmipvo792lSeagPuaGwhMLNX/KVYyGxro80/q148IU4Bsgwguw67khW3CaGIeti4fL3/r2EQlBz70j4cHwjdm'
        b'of3GgXVqBw2wK2K0yM/hUsvhCQYS/oANXMcaRhuJBPMfSPcDePDOZ3JLhWZTszloCgqrOCDqca2YMtHjlOCfy55reLxP1L8AzDAjaF/pDJrZe3jilkso/QElZUF+lmYr'
        b'lGwOWqA0S9CKXRu0pHMQcxXEtDTbgjblVJD3PwT06GNBG3wXJ3I+KWhDnMWvBgW/KlPtl0PaWoO1wM7UcYm2mvojvpVrizphbQAtWeuVYbijlkC9W66tCpBQBe0PsMME'
        b'YG5VRm0YEReSn/BMRgNZeWL50N5jr6r3+ZkOY5SX8QAGMo3yVYoFsxGqZGaRj5Dk97kuN9ehEDtHMljg5LTBTjaDmQMGO59Cq9yse2WUyLZJ+w1YbwSZpUC8mNZirlBc'
        b'nMsX56ZdLNdMrTlttEbhY42z84zWRhKaYQiIi9DuT11Duw5BaAJHSn+8DOb16UcNifOS9p0ZgHHu07Aur4i6RKJVtEoCb5fQAptdAgpcdDmTpCQp1ZxqTrGk2q2SS3KZ'
        b'iANeufIyP7qR3TZb25a/cmZBmYnL7LNyqlQcvGZ+LiPX1WeuT8mfqR1QT8R0vjRyRopJcs3ccNk8X7tFu08/wdHu7a+dKF22MJYrzzluFLSjWdqeDlKHCCNIrColBh9q'
        b'AY/RQZtussRRV7HCo2MrSp9OoJRFH9Er20AtnYYtXGDxT782rh52dZ+gbRmq7e1AARuAyz+fi6OAk8jpI4rIA70LlKUEtCvPzLItMTGNympRp3XNaJwN4lhkp5wAd6vs'
        b'khM3onE3BqWTo87pjXV1a/W6do4ux45FGQEDWy8fR2XybVQmYznAVST2g6STOqYyRYhtqyKv0wqwT+LCIgKUzdz3qdvciLz7YogULT4ze3cxlYT6FeVtUNLMZ8F/U/f4'
        b'Fn0/gzzMEowyke9i/7QBnsKqsiA2qnxTWrsCY1G6RtX041VCQnQzQIZDFmrz7E6mE8PAEJa53YviCs+4qLWxSF0XP5mGUuaBInSinBthjQDtlQFh6ggky7FiMNAC8gGV'
        b'4TiQ7SosxsFiGCkaSOo1Qpf68pc8tieQc00b8mMldpyLmHGdted7YT+sXl1iQBa32+vxud1yXBemXlQkReiag4CNCXA1TGBBhwYSbi5doVz4DRoSV2KHKUoxvkMLq6GF'
        b'xV22jiD48kuUw3A7rLL94l2EvOVOxtGbGtsVLsPL5bGt4Vuc/ykTINIsY1itot1sFZ1ikg3gvkjCeN21M1qLPxfhtXosEAcBtVPqwSz1aUm7K6eyayCI9tkMIHi7uFxc'
        b'Li0xeZjMGjL5JI+03AJ4mx4K8dU8AUjrEitjywFQZEDSRuw1O613azSlvHK5pypA9gn1nvqe3KONtH67gBkE1QKxMRGb0juW9/14R1Sc41Kco7VtW873B0LKFL4jPopz'
        b'ojluYmV10ohLwZ6YQiT6n29KCXA6BUb46NXQKgko0rUjmbQxQSExSOcSGwQzt5h9N6316dLI/H4z0X7XQxxLG/13gGdxjVaxUJx+QRt1B9hMd2OaR+0lQCesYRK5BMlw'
        b'GURdlxHe2BjQZXXbKOLvAt7WSTFmlQCkvBMwQMQD0y7RdTo96bh4ZU5vh9AxTG9s+4X6nXzZYj6+2PKMQ8OcIlN4e7JEvVd7vFzbPHN2EYrjbZk1e2XcKlXvUp+dpj5o'
        b'6S9oJ7pepT3iVikhJnSGCMiKblMl2tNovwGXLkdDqrPq61c0NrQ7xDTpc6dbbOHpe1YYxlNHLQDe946BJhPD46XA2gaPsg8fbTHuXKd7qtlLpW6XYqwwK9/U7xL1K2IJ'
        b'OlEunBlbihetHLRQscVYOQAIx8FtTp3aEtfR6tE2YLhS215SUIT23wGX3VGkhtWWQrRGv9Ku7Zlb2eHsKcYdQXEo2Mc54nf0otXFM+oviCd50HdKQRjpPy5sRsI2zNGz'
        b'6QATu+Zbv7qcbLughnRVoz9QX1fb5JGzvUDLZtNhvJKd4wkoHg9aoa1vm8G5XVvApejj0fwF2cdBFevaGl+9AmW0MU2zK3xyNtLQaK2jQpZrmXex7DydBsrJzctmVHd7'
        b'teu4KrQvosLrrV/tJ3M8SgV6BkNjuL5CwzpNto6y+9tnB0QWnUyKi2bPgjWEJHnUEVcGcSS+r4+8WTD0d0mGZJ6VmU+jU18SHn5cu7Ve3aId107C2noimddOoPfB/dpz'
        b'uhBQrrZee1Z7WN2i7mCRRB9/lXZSbemw+GKO4q+LW3xy25mVudpEp2W2JSJJSZlhK8STMitskxKdjYmyRbYi/SDbZDvQB+a4EzLrEgttmFbaJVxRp74uZgMBpJQVd7Dx'
        b'EpuT93EoKFULc03m94rNUox7NwCIBL4WZSy5Gp5OKZCsEJRwjGM3OSjoXwADzeSAtJCQQxAU/T58orCUCbkjTwLawvh/QlCYjtIFJkhnMuIQf0IxeLnLhWok5iQk5nhD'
        b'2suMLPQSXMHE4xuHF0Ij296xg9Oo3U0sbDcy2GkDQbQpV7e/QxEziEHYoHiqa9e4UXiTFDuigs//3Y2gPiIZaksAo+H3ldmEkwdNlEtkqhxFCJJ0D4+xEzAajzZ6Jx5U'
        b'WLg4eZAHOBTDkPmD2MECsod4CKNoK3TeJsYcQkEA/3BiGEnE6skICEEJhQWI+ORkaRt29UKDdbRfQsUhJUApYGqxAQGAZN4AA005FMN7C4DvrRiHfdHfE1hCxaANAnuz'
        b'MiPIdgsrQNqoaR4eIEXFK3xyVCpDv/OmhRXexo7nizGEiZ0vImtLFlbFNn+S/xCUeThKC2KbBt+ZaC2Z+jyHsgskW1LYvoer6n0AWAIEn/zxoibMDitkSczgNlZyEZG7'
        b'yAIkgKTzpfzkb5FxqhC5APBC+5fo96yMmuoV2aMgq9Pf6A0QfVHXxn+6lPiDq339NMnQUCX/GMhusgt2XhBQm9/8tUu0C71QCc6eyjf1vEQ7OxxBxrioxTSfcLHCjBjd'
        b'LAL6RfJCpFZWgDOM2PLiATbe1qAo86t4xYpiKPiW3hkHK0jfIKcVEGIPjLfVXe1FERAf9ZnBO12EPbsEL9d8Cyp2HXx/s43SZEaEU0gg7OJ1oxfU6RZLsyrMxZ+wo4B4'
        b'ENuRgSdcxBOBlXEAxcThGztuWIUrAp9EeJoRAHAUFNJgY17Pk6AGgK0DPKG6sFZgZcjI8vQlGW8wDh7Ayib2BG+gT9MY4mMuYweugttNc6w1bYFvha9+ta9tb83uN9Df'
        b'r9V8w0A/nsealULssGSaegyKKeVE5HE6XmtwXNgs60haRBPcPpRoQiPikMEH2K1kqZln9pmT9FOMNN4sJPFNPdp3b3zSDrApxnGr5uLPO2neIPqCiIzAnmqBDmFiS7qS'
        b'IMIfTEGKi0FzUCKAnxeQ2AHXctgMkH19kJ8bA/yG6WUzWUaiSaIsxQutRTriAbIdrfMDPm6J40NZDUazMgyDNsZahhbFLc3OucIyxP9HG00APSUi75f1WQcQrhctlsFi'
        b'sHVKqS+NVZyaILenAr4TotJGGZRB6iPGaYpVSuue1AfIdhcJp63qPayNFaudmK1tRXNaWki9JytdUs9oD4/q1Mw7/pED4xg6kkgUuYGGMD8MBhKCXy5GQJB20NEPEsxB'
        b'5iVjWiZFrbPqq1YU13o9ZQoSBu1QkHbiETM5xsFlhKY/NSDIPK0/Rk4L9I2OQNOQbwkzC64m4l6aiZNpQZU/t1UnN6Sy1m7onjlbrvfoHhQQr2y1DPQXocgfjhaJBZhr'
        b'/RiPFlfUUlHpR2GEqJXEAuVaJWpBmfr6xkDU5K4jN0Lk9TlqcWMMwKrjZCSiEsZQ6jqhynEmOEyxSeUkHCGF8AQz35RsdFLnPFCEbXYuTnSNyYgi8w+VGZuSwrjmABYh'
        b'hL6a81WSQvA6HmAUzzXNDMLKAnJMVMavxzRmpexqILcRgt1IYmd6bvwKSakMWGQBex3eWWU9PyPuShe7D0VCXWL9Po/Dtzrv+EIygbeq+kavTF1eUUVeHLKxq97dsxv/'
        b'Dk+Zn2sDwg86lToqaqpbAd2seOnkrXweUfBRk0dRAAw14Evn3EYfRte/+L0eT4MOAKMW2Hkoq9ou13NUwtK7mwwlO94F+2kS8TAFciSDY4GCvk0JsVHAFF2r3BRwjLOk'
        b'DJJpbsLM5I3+VwbBWEjGWMRI32KkeHljmphq/bEmm5Q6fCZ21MU0b6MPKzLIFMc2xwo3JcYqymJ8G3rFEEe5zY69clNXbHM0o+QBgFZgauMgJcXNTvrYddfkxZWH01Pn'
        b'UwuMT03HDdA1us42iZJJShDr4jM6R6mPVe1irSW3G+Aucl+HmGLHyVZCsWHwUuIqqUfrIN6M/1dzOsJOI5hm8Aaxe5iYJx628m2iXzDT6mmcqrz1gA9ixxkSMJLbs6aq'
        b'EyYyABpYwaPjh81+8SpncZApglCxi52DeoaGCn0UKjfjZeN3Ye/WQCSLSSdnrZLL7kp2IovXQvrgaot2i3oLGn9Sj1SWa9tX6b7cE5aLdm239mCHXcKi30mfN8YxQslz'
        b'CcjRGNcIhTyXSHJSiPkgEkPmkLXaTJxcG+wWyYyAJS9CeMRlg52DWY7Dg6540rU6NyUqFc+ZXtwBCsawDzyKCnA63gB7BOALAiMUjRGEO9QtLCyXUO2bwiZZCJhZSN8x'
        b'DA2zVsectVjg8OxVA/2tCRDQfbpD0GBAMhNhaDW1oaLGE3X6PQF3g1IvN1YB9u/E1O6FV8ydV1JeFnXgN7LACxDL4Xbrbs/dbiat7kaXNwYOFzMmcKkBxbIva5v1aSS4'
        b'C5AgAYvtnJDsii+tn760Js+DmmTXVfjI6igauUHAsK1tfjNzNRcjltiyWBtmxKCE0JRCVWn3uaxdhZBJGGMu740bP1x/aM49KDBG2HJBuS4MFCw+oWg7UKAiUK2w829g'
        b'gvD03CwCVi+mcyh0TW8BF9hvZtIghIfyyp1hwChl0wZhRw/ARKX9lqDAdjQZJpLEbRB5zpc0jPNvHcoxdvViThccI7MAKBb/KdbYPnDgvCvmXJb9KXYBE5Jco3iq7YTO'
        b'R4XVlfoUiZoBT2hoDFAvRk1yY12Dn+kSozQlHZ9GTatRskFngDKIR/1MSYTqZd9dlVzZiYc4JkOum1TFzSiaRKh9CrGvcvgmB40Lq1jUNsPjXeUJ1FZVKHi0yGRCcVFV'
        b'GYwp/EOdlZjhoOU8o6UOoNAWT2OFWDyJd8M4iPpKo36nZ6CcALMX8UuYD5iAhjSlcijoioY+WLgnC1tlc7NNtjTbGY+h2QFzwEECsX9tRoEVZybXnBC0Kc8b8YIJMMJW'
        b'2GV3ybbmBF8Whe0QPiU74KtRthXLXtnQvi5BZxBw1AxuBaecx7xlZzqXyTW8ATm5gq5beWWinBB0reLxKehi5cBzVtAJV8zbokMVyFN2BS2Ypyw226AWLlYLSgnfURCd'
        b'lYnfUTBGtgRNwYSgHTAF23K8OpY75eRtZsjPrjRgLKitmWBRStkF1EC5gGMw/wKO+LuhtNd+/sW8z6cUE1+kVZw0aRINXFR0A0Th5zOqks+O8tOilsvrG5VaAEh8Sa4Q'
        b'Nfk8q91r2G1tbgLTI7CTsK+31ufxM0BVV6HU1Pr80W4YqGgM1BOAc1cC/FoRteLL6nof4L9KfaNPZocrYZytUpXH641Ki+bU+6PSrCuK50elxfRcdsWi+bmJbIaTpIBE'
        b'GUikr2PyB9YC/uzACriXeWprlkHWrDZ2jOD2QnU8+jPQvlCESfFALaLmSsZpsfka69yUggklS/gMbz1rAvT6Wx2HO5ioKYmQLzHpSqmc7pzUSaKpSaRtYtXpZUln5pH+'
        b'GppgEXoRU485JmWLDpeb8xvUaoOtPokWXVwxnfJkaCdbw7VfX3Rc1osO9JEOmikLEQ7VrwIi0Vm4y1qRf7NBN2mSiQosvGwO8mlMrFKSLQjlAiadjWpuR1WLOjuVsYht'
        b'rT2mVSioCZ49or56HGPvk20Kf2OdkgCj3Jr/XdTkC4uyBwzJH9gB44oJuSGIIoUyVzO0hXENdFWyjQZ3byrXpkw2uhMaCvHusInTOX19qIux6iPGdaZEdgFdorZKeQP9'
        b'ebRuyoDUfg+zSSH2AAwMCbpHRWhp1EWzvBZI+ap6b72iQ3OWuUHh0ble227dXq/6j7FaapB0vcngY6HhKlJ0xAMFHRbr2RLyexcdYrYDxV0ggzt4HeQrZ3i9mDg2wve0'
        b'gNXGULgF8plkijEUkixWKcOVmkPKx+PVsyXiUL+jYaXICdoevu/EchTti6EEJPMmlpUZDktGqJvVI/nqevXwxeYB1GPXokCcSO7or7pcWzePU/cNIX1IdZcbM2BWZEQy'
        b'r5bU4Lre2SdzGnRsce3WXnfx/t2A/E37xcuz5//j6m41qfe8tFF+7MTH1/zAdNJXcNnU28KR6bcuW+Q89eCk130v7Hl1yTXLj93zxMmXxn38tuVry5flN7z75wl1iaGX'
        b'f9r8xUf1647+dkNG5fgrP3ti+tYPkk+UfvD8xjsjJYVJza8PeuCJ4lkfTBx2aEx4cWGK//S0D1/NO3HlmPCzp6d++ErvyrNv9HO9l7Zyzr3Joc96rFz020j/1lvHHrn7'
        b'+WHXOirPvTB+7e6dg4N9Xpj++4+3/qXw3JMls05+9UC38buKn/voifMPvPxu5k/3vLvovTljBs27OeQf+4e/XeOrGf6mkJ7e8Mtnyi8MGPXpY7kns7ePWzr8w6QF6S99'
        b'/Mqnwx+ZvvQVx7Vflnke/az0soX3zbi35fb780YdfvmqW7UFS1c8+N7r5Z6cSfNfP/RAwefZN3/wVIV30oFup5+4Ypiv5zfDine11FzWY8ywPp6DeTd8OPJ82QNvzpg2'
        b'/OFD2Su2juy387Fzz72y6AeVv3/hYPWS6wZXzJ985q/HNwr/WL+v/8cfXNd/1fsVi79KHPbb2wb8+fa3bva+3P81R8tTt3QvU7iymgGfjTw66tN579YvXjGkcu9/vR8J'
        b'Dfpq7mdfzkjzTN30u8ZI4+2ZNXc1lu/7/OfvW45v+v1Vob3zJ36Wd9Vzn372slK5+q1HZs1Z++JPPr7+nu6PPFn54fDuFxrSe9ZZer7wlzuvLIpUhv458poLd05efNyf'
        b'5fnNmfNXmb84XvvgyIrGce+89/iR3q8lzH1qx692P/Ca553edceu/2JBzceeiceHNW1rXnTw7ten/eix5k2FL418LfS7Ux/mPNrv9EP9Dn14/E5p1Scvni9W33v0k0dW'
        b'XXXy/Qrt2lF3vf2nYfsW3Rj95K7DxyrOKa9vOiOf/OfY48GiN1eGH/zlpBHlv3pv82fH/vziqvc+ffOb6xeUPvx5VTDlo/27+33x4NMfXLG49Yu5T76VO+aT3Mkj9jwR'
        b'+Sq9cMG4618995dbXnf/+OfeeVk7v0lxv7bcvO2FG5q2jvjtb3+w+7kRWafPr541cfHXH99tDQY3rDvjCjz9S8+qD/6Se/O7f//b8x/99L2f1rZ8/FzTmpVv3tjwes67'
        b'zgkr/jjh04Qfz5o/5si+BcEdd239/Ffnt60orD38i7+K1/3yrzPzt93edGzsR7VV5SNe3bFm9u9XvFNyZfeRj39z9PqFNeU7p1xXcertXeevqrnp8a8vWzXnT8d+/mLB'
        b'x28N/tJb0+LwN/EvfFBce3rb3VvyrnRzd5z9Y8KIZ39597ZZt0cWPH9seOsbrsXvPrqm9Ee/f0j88QenXi267h/PPPzYy//ce/7U/LXPnv1T7zs+Dpy87eSJv//h6k+/'
        b'vDvk/+N962/ian976g8/XZebQH6Nq5f0ogPQHVqkfFZJIcCCHRYuPa+7drOoPaHd08RcdBzXWtRTGA8Iz5IB2taCInU7RkxWnxHVndo69TnSfFc3qrfY0TZribo1kxsy'
        b'o0CLcFyKuklUnxgtMQ8EJ3iOTP6WFebxaKjhDqt2UlDvVJ/RbiX7GwvVk+OYB3WPejDeibqoHl+kPkDeHtV96iPqyQ4CrOpJdctUqVgNqfuoLKf6pHorOwC2zVioFOQh'
        b'YzVRPSu6By8P4OaindXWrYaakCaqnhc+o4SAirKukfkekhIohM1+vF1aPD6A6iwV45Yu1k7HFV8yu7RA25Z7kWgBJLqp1M6tyAoUYp3XqS0LLyX88Yx2ioQ/1OPaswG0'
        b'i6at0x7RHvYXkSOpHY2dSDA4pxgFrdb22NRTS3PJy+Uq7bb+nbCUrdotxFGem082CK6btcrJx+0SS9WnAPv7XvvRJS+5Y/6Nmf3/csntxzCG/ycuBmfMW18hu93McSii'
        b'ihVmMq7wPX7vSL1dNhcKp4vsP8UG6LhF4FNT4LmbwOfMEfgeaXgW36/ALAyalpHpMmVMlQSBz+BHewV+UCPEs0p0Wj8gCa/ZdO3VB68pJrpCfhk2fEoS8ZpquvjZaTXe'
        b'YPn9emEozUnfXXSFPAfVO5Fs+EaCWFjjjL4CnwUxMyxAKFBeWS4r3Qddg9ceI/GaV6Y8HzvQC/3v7O/i0kYVYG9dz+l6TtzBNZc2oKw+qD4LCGpsn1Ij6o7h6kkL58oU'
        b'e2un6mqH710q+fvDFB032VTY8tLc309N2lTzxKI3vmjmN7z2w12zb/2opebFW/xHtsyXL0ybUTY6tOvITa13Xnn8D9mhiTOzco7Z7j/yj+cuLHyy6YGEdz5bfNv2t/70'
        b'i433Xb3n3C3bjxcEbjEdGNzL1lxRuiv5jV2fHE15dfbfB77tW9Ln/jsGnj+w8ZMf3r/usSGLfz5vu9htzteHDk67PLJj1vFflXrW37LnzB9uvObI1U1qQ9/eP3vvTFnV'
        b'/Fn++SN/eP6GLy8f6NrX/Y4ZPyo699OCvz7063nz903YcdO9wSMPf1Ze9/ju+0f/45btb5UGlxXmL0x+5++//q9PH+tjd5y//eSLNzx2599ffecnLS8v3rn9/JMLu0+4'
        b'9Y3fPHXnrxev8BxKiPiuWbG59+IVkXsWrdjy0aIPXoz0PrL7tdOlbxRf+WyfzRMcNff/bpjrNzdsvnbC6nt3FFqCA73Pa/Lz2+QtW14a/fEHn731szV7tz5954cNo157'
        b'e8VX34weFKx9+oW6l5uzrsn6ZPfbfb8o2LEm2/ujF16y/fPUqcIbf/LGinsfvz//09O/nD/o3KIJ6S/PfKTbuRbHwr896wvuXvqXhcrPXnlr0xkl/ZWc+944/9XbE9/Y'
        b'+ebhjxrPfJb2Rquv/yh1zI9fX7Zv10uthZ/f+0Zdr8N7Hv7DK1PfPHzuYGKQNyVYHvny8qygnJS9pddfc/aHh+c9dHDT+B7LDt4yevx7B0OTzRmVGwu9VVt7f1i5ftKH'
        b'f+ZCY9VhZQ2bR8xauT2zqCGSv/TP5r6+Pv+1bMahuz78lfvv+bv/+trgz0vevu5rvqXvb19K/ix3EiEaawqD+oTaqm0pwBkFaA3MqLniMPWMulV3TaYe6oex4M16Ay9o'
        b'w3vUk7BVkx3o29T12eTEdFt3zFD3YaptEsnn83j1dvVsvvpIgRm22pt57ey11y+2ESaTPXdMfmlhHtq10nYAqnJKuxPTl2pbLFzfeaYUbyLt6JOaK+NsuTerpwvjTblr'
        b'R6+lFmnrtQe0E6UQUduai1HztfvHmrnEMeIK9V71PrKINPYGbaO2ZYh694gZ2jao5gz0pKM9RhjB4Ioxpdr2HIETfPyIeZO1ndoZ5rvtIXNl/ky7+iT6bjRx5qmCS7tN'
        b'IDtIgwcAngTonLZJ3ZGfU8hz5jXCsInqcYbr3bxIvQeaom5VoEIliIKoZwU1pN2qbaEC1VOT1gK2WAAEd5BvqpyinvBSgdrhzHz1qLYZP6iP8xXifPWYupG5sGxR94wv'
        b'LVDvK44zBqbtmMsqur+btp9MN0LCZl7dWVE8Vw3TEMzT9hRpW8qLeMhxM3+FFr6yF4wdDkHFLEAYj6K9jNyJ6XkztDuhDxA/Q6Rs4EjT9BXXE54sqbu0ow7AWksL7Tna'
        b'ZvVR9DWbo97TQ31WUveIqTQCA3PVYziZ7irEyuWjfbVSwEzTl0nDtafUZ1jj7nGoLTAEM7Equ3h1X99idfOsALIPx2fk5GvhIegZ/CFeO5Jz9SD1ENU+Xd2IDSvBIRNu'
        b'4mvVp6faAuSrXFuv3p1USlBxpnpgJPQzEu83C9r92kH1DEPKT6tPoJRjefrk8sKS/JkwhUxcygRRPTpRPUKmsJbdoN1dylwAl5dBFqMcZs51ozhdPb2Cxmlo/QSocIPZ'
        b'zPHzOO0QtJ5NJu3mGTDsKGD7EGVKbn0LK5idvQddS2HoD2u3aS3MGIlUyavPaWfVFmrSJO0x9XBpoXrv2NyZkNQ8T0grm0n1Hak+oN3DZnGJdlp9DieOQ90laA8NgnJx'
        b'LLSz5eqDMJqKuq1NxFcCQmODqK2TtcepZ9Tj/dVHS0sKSgpp1ah7tL1oF3GzWAYVuo/5Yn+k6qbSEm1/YUEJVF7i1XvHwyBhHZap2+dAw9T7myDpbOj33BLIX9spqqfz'
        b'mlnHH4KFtCm/RD2WkztkZsEo7QDHJWqHRHUdjNQmlv0u9eTw0vw+6tEZJbDUevDqgbk9yXdD2iogPbbkWSHydiRvpKt4gDCn1Duou7Xdtvz8mep+7V4Tx5dCNjMLqUsH'
        b'rIbu3AJE1XYtHOwPjYZ+CQraXvWkjYajoLg3rMVwgrYTHZxKSby6Rz2r7WTeIras0XaXztQOmwrKRo3gOYvWIpjVXTAY2Nzx2nPqodLhQHrchRZH48yN9tB2seaeUZ/p'
        b'BjEOaw+OKCmJt/WphtW7abmruwfcUEpmqpmhvj4qLE+Xul+8/KZkymOg+pD6FC1PsqvaGGcEVr3PSgto4uDV+dq21KS2WDHrq9qjAAKQ/BqkHp6BMKcQlkoejC2sVVhP'
        b's7XbxszCnoHyC9UjEjdbPWrRblb3NBEEXeLRTjhmwDLYDjRpAyYvxXmVqu0VtQfQczf1A6yZ8GQiT4tmqOsmzgZw4dAOCtqT6gPqbdTIDCAynyKTw9tLtJb+BUW43B4X'
        b'tMcXaE/TIGXM0CL52vY+2p5Z2o7SgtzCmSauW5ao7Zwwgjnm2A2lnS2FuXs/LEaY5JGSgplDyN5lAWfSdmsHtdtp74H9aOMk2nsOdEO1y/JcIOnUbbj7pA2URPWUdoC6'
        b'zKFtG4sWqsvLYQc5ot5GtpQc6mOwXghq0oI5oT1QXzoTZs6sVcTiA+rTwmVoLZna49Jih4Mabx6s7i8tV8NZhRAdskO3Qska7HMH+msh5mr7qesXYe+YFdqgpEJePQaU'
        b'PmvXsyNgOkF1h8TtZ1hZbUtVzwGSukF74gYG/55RdxSWlsxdMDtvtoUzS4JV3agepQnSOEt7ikwXowrTk+qOkkLoXe1+mB/aBnXrt52xGaY5x/wHkE7/cZfYeTSRcUc4'
        b'nDiCYOUv/tmFJJNE5ycZQAQBSs7+BYnH2C4WRz9VYcSdnUklCnb9CXIANN5KeaeSXnbbz0k5YxymryMJLD94L5jFNTdxHX/jzDzjpOvGUm1kr6Gxwe1usyloHEX8iI9v'
        b'KT4w8uILZ5fkBcVsJzqRAP9ofwUFF/zPw7WSk/nl8IssDC9E4bbIYLgLcBfgLsI9De4S3BeEF9ZycLeHF6LyYqQPxl+OMfkQH1poiOM1cyiK5xXrpEhinamZrzM3C3WW'
        b'Zjx4tMg2r7XO1izRs91rr3M0m+jZ4XXWJTSb6dnpddUlNlvwWDOQBLl3h3sy3LvBPQXuWXDvBnf4jge0kb5BLpwI98Qg2S6KOIJosJePJEG8VLinwL073F1wT4P7QBQW'
        b'h7slKEX6yZZIuixGMuSESKbsivSUEyO95KRIbzm52SqnNNvkbpEeQVHmwpkokB7pL6dGcuXukSI5LVIup0dmyxmROXJm5Eq5R6RE7hnJk3tFCuTekXw5K5Ij94kUy9mR'
        b'4XLfyHi5X2Sy3D8yRR4QGSsPjIyUB0VGyYMjk+ScyFQ5NzJazotMlPMjY+SCyAS5MDJOLoqMkIdEhslDI6XysMgQeXhkpjwiMk8eGZkhj4pcIY+OXCaPiRTKYyNXyeMi'
        b'c+XxkbKwfQMXGSBPiEwLpMNTsjwxMkueFLlcnhyZL0+JDJX5yPSgBb5kh4WgNWirxl5KDblC6aE+odnVkjxVvgzGzx60R5wkLNNmCdcVSgylhtIgZkYoM9Qj1DOUBWn6'
        b'hgaHikJDQkNDl4WuCBWHZoRmhkpD80LzQwtgPvSVp8Xys4ZdYWs4d4MQsVHOkp6vk3JOCiWHUkLd9dx7Q979QgNDg0K5obxQQWh4aERoZGhUaHRoTGhsaFxofGhCaGJo'
        b'UmhyaEpoamhaaDqUXBKaFSqHMovky2NlmqBME5VphvJYSZj/oFA+pLgyVFLtkKfHYieERHJjkADxUkLd9NpkhwZATQZDTS6HEspCc6q7yVcYaZodYVfQQSUMorQOKCWB'
        b'+jMDeqgXpO5P6XMgfX6oMDQM6ltM+VwVmludKRfHShehriLlJN1ox3FsdoYHhp3hvLAz6AyXbBBQLITeFNCbAvbmRmfQQYIhVzL/CHQIyXQGEGZ0LRKHuyZT8gpzjbzS'
        b'I4AWTLjlvCFdritDt3Yf6M/Jza5lsqoV2ZWNtd5ArS9XUNYiLKITQdzMu7S/5a72EX8NJd8OmnRNZI6OppUXDDWZXAnAXo0nUK2gcobVs6aKBHVIWx4P3Ouro05DWImE'
        b'lHi0pFIHcBKe7GgzvK5B8fj9EBK99TWoTo1Cbco5yPsCNvkC2UvHel3Ag+0LKOdzgTPEtOtlD0BbMmiBIu5RsaG+IWqH3GVPdQUqT1ir3ewkl6lvthm8iEHoqLma8ok6'
        b'qurdFUoN+SpFh6vuFavrfd61sVd2eOVjmUWd8OwPVOgWQ60QqvZW1PijFniizGz04PMH/PSVBPOphFUVSlsABX8xROnowUVvFT+JU/jqKR8vDGBFJUugeDyr0DY8BlBa'
        b'ggKmKq+nQomavRUwwMOiYmVtDYmzo3Ed5kMkakfP1+yZCRC9qA9yQKmo8qBLS7cbole62UBa4AnFH6KSW/FUR11uudZfUen1uKsqqpYxWWWYGDKz/ob63a1CTm4Hn4J4'
        b'+IzIGbO0JTAfRSiihXaq0KgsihdMxyN8gfR2hQ1AGq/sETSU6zsXS/xWu1M4Ob+MybbpuIGTTdp2dUQhNrNRx2fga9gCkM4JCysTaxLkAQYJ1ajKkSWTXyBS8BDD2SRY'
        b'JgWlsL2RU9aHnc2moBB2rBCUGfBs9uVQiFOuCzsdXLMpzDFBtLA9nAJfXNB2Zzr2hTlsgXDvDULQHO4OJQq++4KC0gLvssJp1WiR504UHoNyukE5j1DsDEjdC3PzrYH3'
        b'fcLJFO+dcDLAHQvpwGU0WyGmJZwKMSXYK6CvN6CizfNBCXYQnvIzN3K3omixGVLZKN+eEMuw4GOHHPSUQRs82fGJfChBeB7H2h/mKY8bIW1iOMFhaOGJ4ST6mpCBhoaB'
        b'CJS5oAO/BQWAtwnpHFMPIxupNuZLISaoR/0Jee6DcbCHe0DpAvZL0JSKyjEZrB/g+ymqcbrRE8F2Ouy5zv/WKUjf/wBe9PdiV+OsNsMs9pcReHYx3FUwFL7MgpWkilLg'
        b'lyQyt05Mzog5dTIDtpvBS6JLcAlJfC9MJ9rJBZRLaLdYkvX9hxbLrwV9sbhgqHP1xZIav1jgq4iDF5Zgjxrabvng4OVDGomecOKbgpL/vbAJJqM5jL80GHQR5fuCFmV9'
        b'0EKaPtYglMYmDyyXHhM5nxzuGe4fHgSLILPahGalYPrOabaHUTbODrk6gvZwT1iUr8LES3Rwmbgxi/Dswuegk5Yd5BN0AIqYqE9gkhhk34L2idzK232+8IBwQrinzIf7'
        b'w/8g+O8Tzqnmw8lYTrgPLq5UQDHhfY8wH04KJyFqVmuhxW3CSQyLKTlohdYkwISHexCWRtiVwTW7wimAEOAbVzoHyyaBEAUHpCog92ZrKAd4JrVVM8pZNZt8H8JbczgP'
        b'8k0MJoYzKA4ABahxYjibQtl6aACFBuihgRQaqIeyKJSlh3oYdaVQTwr11EP9KdRfDw2i0CA91ItCvfRQPwr100O9KdRbD/WlUF891CfWdxjKpFAmhqoTYYMoRBQ/yG1H'
        b'0ImAANoaHhxOgBYnBZNuFfxHghJdLXil+ZKO8wXygP6vRlvlemvSOdRDhD7thvMMchXJwISEvY8AnN7nByV8H5QMZydtdsiT/6+s3dyi/wD48T8Po6YgjNrcBqNQwlGw'
        b'6na4zaKLoFWKRErP+PunZMWvaOg1FRU3zYabarTg7fy75ES1aLQg5hTSRDtALxff5e8TKcUpJvEpohWPVb+WTE4R6f128M3QHSP4xgxqAgQD4jls1eGbOczFwTcxbKJN'
        b'HdCWsA3QfoBrTJq8HfLSKa7yb3CTQF16zGwYGGBdKmKHdGiU1WjUM9goCRYJYiACgOUU1pANJCgK2IAJGpmEFkTpvRSkmNDEhLAZd2joikQAVAkItjGEYvJh+46hPObq'
        b'CKfgIsTOIiAmmgDIhm1jABGc2FFAfnO8gDwAQQCnAPBF/TkJciFhb/S4RPlx7Xb4zju12//sfH7GbPBwaCajHpVksfO9RNQfKhJxhtnbzzB7/GCsQnQTUMNwIqLCscGQ'
        b'9MHIocHoDgia6C+gLxhOwzAZ8p8Os86JmsX0zb5jAHUd6t1bMkh7AUOddPyqdh0PKF/YkolatRLsNw1B0b/PQMR5LFECtBJ3Z5PyPrraRDgL+5oJ9h8Y7GZLkx1ZEqQh'
        b'mCJxAW7teSNvdBRKKTIw/cqHiEB3hZKAOE8NpVdbdMc81rgyrAj1b8WWJ+A7IzXbEwHTsFULK1gtTXiN5W5DdgilrISU8A6+2GIpY3UA5HV0m/+nztSAYjaBYw4qkVKB'
        b'5kKXk88KtE6BvoTQVmZ9AWKtqwxiu9jgAQqBSiWK9OWf+e9tNCTqqvW76yur3asVFPRWrJaYfo6k25KkmZfLEwn/L7kryfxP2hLO4xKaHreEkuDqpM0BReAHAeg3o5Ui'
        b'AbcIu2gn5y6AvNqcYoYF36ZYXDqbN4XPzWBciWbMnTx8iP61fuVFfPcSXn6Cl5eZHDaaCfIrPyWlgyZvbaXyM3qsqwgsU35O6t3w4KlADxLKOVKkqZWVAZQpUOxRsaIS'
        b'aP1lFX5UAo9adNtXUYvfeKjx1ldWeP25Cf+eLsu9+j+AT/+/l3/lYAPnJPrr8kdxnguCdPGhhsuUQYcPeNDQ8dDDqlvu6Phzdvr2X/+Z9f9Y2OwUUyySOGsUrr3q5XjN'
        b'dkri0F74NPFyXJeC1UyEpSBQO8tQSecUR54j3PFcP7dbX5F1FQ2wLAOKspVnusFk7ICdorxA6+6KNVWeBjQEpaAEBJ6pVFU0+j1udzTV7fY3NhC3EFlrqAQDbx3utoDy'
        b'cXvLFXFKtBPr6uVGrwetuzF7phIAliQBUKbOTnZu4rrp7/uhe2RXTKTw/wAJE3+m'
    ))))
