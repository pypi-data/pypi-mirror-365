
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
        b'eJzcfXdcm8f98D1DAxACY8zykjcCCbDx3ttM4RhPHBsJJEAGBGhgYwsbG4yYNt7GE7yNF3hvO3dJ6qRJ2mY1oWl/SZOm2W3SNk3dNHnv7pGEGB5Jf+/7xwsfHqR7bnzv'
        b'7rvve3cfgi4/3vhvOv6zlOGHHqQBPZPG6Nkm1sAZeANTzjYzaaJskCbWc3q+AugkepFejP9L18qtEqu0HJQzDFgCTFN5YPDK9TavYUCaNwPWKvQSg3e6j16KnzL62Zc+'
        b'5QbvTcwSMAboJWney72XgmXAxC7F31KBV7bS62E/74U5BsX8EmtOgUkx12iyGjJzFIW6zFxdtsFbyX0qwWB+KiUPEX60M1GZjEdvOPwncf63xOCHA2QxetyfCmkpUwXK'
        b'QSm71tvOlGOIj7CpwM6WAwasZ9YTCACGIEfJaTI9h0eM/8bhv96kQp4OUSpQKjTt4G/k9cI8AsrmeBHA/8OzpmtV70YtBX8Wyv512mnQI3S0stEEOtYBHFwW54aQ+ekQ'
        b'uiruDCGvsUXjz35mtD1VjXajBrh/2EJUpVqMqlBt9DNxC+MiUD2qU6JqVMeB2YvE6AI6rzSqygZwlkhc8I2UE59rP9PGN+ZlfaF98LFqe4QuTveF9pWMwMycrDz24qbQ'
        b'8bFg0wzJkskTlKxVgUuEp4/1wXVG+g4idSbb1BGoJpoFA+ElHl0IQi00Ezwq4WEt3Iq2JuI8sB5ulQBUji7JA7gBcA+6YvbCmZRcOxuuNBPMFB4k8aH/5CxzwVqDSZEl'
        b'IMXUdrnOYjGYrekZNmOe1WhiyQCQ+QKhMkbOmGWuoqe5dj7LZspsl6Snm22m9PR2n/T0zDyDzmQrTE9Xch4tkcdpxiwnn33Ig1QSRiomSeATf1bMsIw3fdqG4xQdOoqq'
        b'E1VRGnUErE7xHFMV2s7GitBpuAnV5xEwDIEvMcdWNfqAwvvMv5eWB1wFFHmmZVtZa05oL6DdmPGHhUWcE3nen0bfxozIZd5kgf/fFdp11tBMochSHQvwTM9f7K2VXRw0'
        b'XEhcs1wMMLTjW4ZpVWtjYgGd/7BcdMgHnlJhkKrQ1tSYBeg02i6gQHiUOhxVRUfEJzPg2eXSJFQNa5SMbRDtVFOwD+5RIqpdqPYORzXwAjzFgzB4h4f7YCM8YeuPc2Wi'
        b'jRityGTWi6Nxz8lHCfBJYdH22SrbQDLbe73gpi7TjcpQNSDTHbZKydmCcK758NzSRLUyIVkExKnoImpmg+BtP1s//GrWNFSRGIHuoloysPHxahb4wL0sOgV396MtKJeh'
        b'ClSbgmoSkqNwH29FJsEzPAiA5RwqgzeG4RbI5HEL0J3EeFW8mmKmKAaeA3JUw2lyY2whBMxTqBJeIxlEgEe1cBvPwMPwhsU2gLw8AMsLImnB5HgMReViZTxuAe3g4E19'
        b'CR4w0gDatQieShwVizMkoi0jMlJwTX6DuEmpC3EG0hF4BtUNIBnik9EWdKs/ySBH57mR/eFZ56DDJrR7nU8cnqpCeHUy7nFdIulvIDrAoRNwO6rHnemL800egc6gWhXa'
        b'otSgLfGqKDEekkssugTvxgiDfkWCNkWiLUl40FVKeBntVSeIQO8BHNoBj6NrtK0NqFmRmKKOj8Qdqo5XJURHxSWLgSpTDkSoER2EdwWgL6F9KwkgXnBjJM4RxQAfdIRF'
        b'16xoo01JMpwo5BNJhkjSrfnhiZjmt8Az3qgO49p8tRjM4sWo7Bl4yDYU507pQyeyOiXpmfC4JLRFk5SyCGeCbWg7UE0UzYHX4a1OnI315L0HKDN3MJhlcg7eIXKIHRKH'
        b'1OHl8Hb4OGQOX4fc4efwd/RyBDh6OwIdfRxBjmBHiCPUEebo6+jn6O8Y4BjoUDgGOQY7hjiGOoY5hjtGOMIdSkeEI9KhcqgdUY5oR4xjpGOUI9Yx2jHGMTZrnJMtgyoe'
        b's2UGs2XgZssMZcuYMTvZcnZXtuznZByd2fJmDR0KdA5d7ZWoGtG3J75BmcZ5YCP8Ep3EmHOCkFACaovWqJVqWEWoLEDLwfNL4ClKQKFr0CZUG78Bk0I9B9gNzHRYAW/a'
        b'ggkUOfBqJDw9D5Wr4jBywwoGlcPtBbSYSomuRirVqArjoli0GLawkc/CW5Qi0FW4ZxiZq15olwpPOx/PwDv9YBWtE92Ex9DlRFSdC5LIOy8GHoc7C2198Lu4QTmYtxjD'
        b'4wgkfBwDL/miFlsgKdUcik5FRuUNU7KAhVeZtHRYR8FA14vh5kTYgslTDMRoc988NnzdaPpKCg9JE1GNfAjCHAS3NISB59YtpA2JuHCCeCtheSSD69vCJMF9A2yh+E0u'
        b'2g0PJVJEUzFADC+EjWWD4Tm0m4IxwmCJTMCklYL7HMpMZ+UDUTUthvalYyIjuByuJsVqYeMadmQcPECLwUOB/TFlw3pUFY7hNzFTlbEUDjNsDsM9hnXoRAIBZC8zd4TA'
        b'dDJU8DwGIyAGzywhZCm8x0IH3IXbIwVR5Qz8uTZ57hwVxnQ7Mw21oK3C4NfhHrThea9BDrSHvIWXmIWJawVeVY4qxyWqMOmjOh6DuSkpjPUeBZvoeMFKPSxDtXFwJzyF'
        b'eRxgS5m5yxR00mBTJmb8mFPugnuiCKA1zLyx8CDlGBK0B+6lLAX3Pioej45GBIJzMAct50etnC7wgr3wDmpNjPSHN4k4SCDz6yVm4a6x8HIm64H3BNU76zhYw3Ewbh2H'
        b'rcIaTSmHiYl1ExNHiYldzzmJKevpdBxOY4xMKmEsU3HC+iPffn7oLe3LGZ9oq7I/wf/51+um7/OKi2WMWQrf55epfJZunLx7c12drP/0f2U1TLwqr9SKXwsCb4rk+7+c'
        b'pJQI2kldSW9BXKH6FCWqj6cSq1cgCBrGc/DkKCvhnQrYgjZ3EWqwEV2lQg2zzErrMJxrmBkeIpmiVcl4PqvRqfAOhWcgljBoWyRssBIBM0WLtpGcKRhh4Rby3hs1sOhA'
        b'Aa7rZibNAltgE+/MkxQFq3EmdR8g57hBWDDvtxJsg0cxWPsi1XFEiqGbaBeQosssrAgtsg7Br+PR/mwKjksuoLI0dYIAzrAIUQrcLXKqXl2UIZpKVaF2Pl9nyaVKFtWF'
        b'1ksZ4VfOeDPm3q68Sr6d01us7ZzFnGkmTNDsT1LZjirxZ0JS5j6ummnhDe6KyzspWQR5V62EhzCpoLPhGEfFgFdhPgCvih6tW48S8I7NYn+CZt2NhbvQuRvWDSyZwVgG'
        b'44Qv7436XPvs/V8/1/DCO881vHi5YVuvBxM2yrPez2PA9EWikP5nsHJMyLYPvLssUUXYYiKDOcEZFu1E5SVjxBTt0F64K68rRt2GGylGeaMDwriyPU+KzWrM69B8NwCp'
        b'P2MOAh2aL1eQsarnecB6boh7CkiRKlINyQXKwEO55yRQzrN/FtYr1KjCSOQU5sZmBt7rg250mgXG+Zfqgsgu2CyMRoA51A19RxfkpoL0gowsmyVTZzUWmOpIUcpRWFs4'
        b'aXdzEDqMGXMtvBJChiglIVKt0RCNFmsZHIiEl0RoH2od+hRwZD0WDi8XEIYGDxCIpgsd6JCMMM9bQ4XGscQMQOUcvLMe3Xs0Fo4lWMgQPMQ2Hv/fYCIDeuJ/os6ZXJx3'
        b'oLttynkdvLvtp+G9Pbbt3RMVvHjwBm9JxAkDZow+88dPtV9oP9F+linLlmZpdeG6Bx9HXMzQnzJo9acCPtGe19Xuz8k6azily2Ff3j/qGHjh85DBIYNDv9k7uOw2ZsQy'
        b'8NsffBu+yVMyAkUcm4ouWOC5OI3POGylOKe6F2rgYCu6Bm8pGYGT8F25VRfqEKVn6vIE8pAJ5BHEMjLGH3OttWGWHGOWNd1gNheYoybnFeCclqlRtICLkfE6c7alXZy7'
        b'mvz3IKJuFiNrJmhiHuAmJyIyd3uQ0xcBnuREJmd1n7lYSUdVSZFY/1NjxN5I7GW0HXP9aiwJNFhrgFexyl4rWTABwJppXugaOr7CGCUx8Baie49c+dvc7JzsvGxNpkaX'
        b'pFv1wSnDJ9oW3SfaN2FeljflQIZXxb8UbxI685QD5uMxKJ5cpY+/2KxwZ/XtaRDMvdy9Jzl3evT+q069J/IInZgEW7HUvOMxBoK/oC+8yWPt5ZDk0XTVza/zZIqq6Im3'
        b's92wmtcsNDZ9F8RbiJI+vv65RB1RJ+J0/PY6pWLssk9779V/pZVmvf8KANnvisv+Ha7krYTc0JYsSO3fFI1KrRHEai94mYvC2vaWwCCrGueB2/ouoiIY293hCeoouCUF'
        b'931rZDw8F44V6v1UrIOl6dKsEHTPSgDwnasQhL47W41SyBWGdvFwE5YhW61EDK1DJ4bQqmHbAmVCkiY5AZtXgi4xdIioP9bzPZHAY7p9babMHJ3RZNCnG9ZketLJQDEj'
        b'/JoHuYoosTDBuTro4LQTqRjzYPfUk9yHPKb+I5nn1JN8G+TjI6mZHIepui4xGU89JnQxGAa3qNaKUpRdjEDXzBM9wMXVqAn433FUHvQk26WaPNL/O1lSqX4uUBg2vFqS'
        b'F3Uhdn/A7dBxi3lA7W9YB/dNilTHY9q8QmZ1iQgdYeAVdB6VUTfP8wu/mfVa//CB7Pz3mR9C1ox8TXDPFE8DxGmzpjWlXn+0xCQkLpYHADLTMQPEPlWDEoBxlayGt5hw'
        b'yoejLifq9LpThlOGL7SFuir1KcNnmLw/05qyIhac1qXdb4CXG3pFvCgN9GnRsS3bTxvO687qgiSfsa/LBmsnbn6XiQsO6/PNmzF9vgYvNC54p21pv5DW08zLre2xb47q'
        b'I2beGiWOLTyBDYEV/R8E/QKzXaJEToGb/BOxKXoTYkVkC/FRSGEDW7AQ3e2ZcTyRnfA5OksORSuFgFYjiMLoTX8F5VHG8pgh00+MeWgHqgkMtYPl9tw+I2SjmEcKn/DA'
        b'vPcCumowPuPRZmwdocPwANYj8fz3wZYrapE/wUfLdPHRsk/Etm72CxkCr27YJtPYAgjz2DpnEdqB24VHsqNBtB3eoLixNxgP/+R/smC6VnataLGAMIf8CRLNxgBqk872'
        b'CQVmwp97erQz6UZ540TeUoO/tMYdVb8ySQ5j/Cs+CJ22fbyodDwzL/4weypnsXRYwJzCzQdqXhQ5Wgtq1EfUdzPm/fhv/0Uf1TF9X1szwHfynQ+/u3nmeHrK7DuRfO8o'
        b'6d5/vHhfX3HkYsAURcZvPl/643Fd6pC5eYtfyLr2+y9bto1bXvxjQmTU3/6hfivqxv0k+E9m47aBr76+//0B07bnD2n9/S+VPtSGUsEDfHdDC5tZ6IANW1rX7JStzcJa'
        b'fr1FpVSimqQIdbzgUUanrCyIWC6C93TosJUQZA7aPwhd0sBz1nG+TiHii8q40ejaOiuRw9Fps1zK9ZUstxFGdOteuRTtU9AdrNlGoSp4Yhmqpk6DLawac+QWK3HxKtAl'
        b'bDV32HJUR98X5GnLwaoiWtOKXmGRCcSjkoQt6JHoug9sY9FBWI32CnZcI9w6FVvYqghlFNqKVVgAQhRwFzrPr0yDm6kk0RGTjjJ93JLA7AvXE4MQXoV16AhtZSa27+56'
        b'WhMMamFL0CG4z0odKtcM8HKkRh2PRw5jyyiZlJNOm9nJAnuMlScutGXkGQVZMFog2okstvECMImKmUCGx08WsD/yLH7+wHP4+R+ex8/vxSIxJmsZIeTh7jqDe2wu1E21'
        b'JOcND6p9qZPxRy3b26giKTJ8GjyVjGqw/SvGlm0rC8vmjaAtZIo96IyQk9RFZ4M5ovbbmVBQKq6S2MVVoJwtldglFs1auZ1rAnZxM1MqXQJMgTywMrne5vEMIL/LgClo'
        b'KVaM7VJS0i4mdUwGeoaUNX9nFxUuNYJSkV3UxDaD2WBFw7NsqVepN2nB7lXOmjNoWzz+dMIubuKaaR1NPM0bWOpTxeF8PnY2i7N7b2EYULTFNJ2WkGHoZFVednE5g+H1'
        b'rpKST+UMLSWlpaQepZ63y8wfV8mE3C4YcfrfizIaWNNQWqNPOdvAmBVVTBXIFZNPGA6Rnm1mhNwNjOl7mo+xirNYmjehyseZN6GKJXW7c75Oc4pprsIqkTMX/tQp11k9'
        b'1yTR83pRBTYmZ4NyBo+wr17cJLH7Nkn1Er20mSUpdl9c9pjey+4bBEp9HRKHD1bnOL03Lie1c6RcqRz3X17O6KW5pMXX7XK9D54NuWmwO53H6X/Vy0iLdnkzE0Te8nrf'
        b'UrmdbWDNEzG8DIWXNYfo5XZcIhgz6iwW5/MzKeyMnc3l8LsYvR/57EyX6v3twqfBHuUX6nsJ5d15SGt+dj99wDjy3xfn2WSX06efvrddbvcl9ZF3Jrndj7wprLP7ku9W'
        b'YX79cS/8cS8CcS9Y81d2f9I7fR88pqz5rvANl3kHf5K6098WvpF03Mte+iD8HeiDN7OhwN6Lwu+PWw+p8iUtrPK2+7tgsHMNnDnQytj9yplNjElq9RE+OUVVqGbhQ0ke'
        b'Nr1N6pEPWZWikzRknRKR2tHEa5ONSWqFdyljZ1aBbWwRT6pwKpft0vR0ky7fkJ6uZNvZqJh2xtrVxPaenGe0WDML8gunfucShWLcyNp+mTmGzFxsZnVYYh1ZH3KKAvND'
        b'RvUpgeyhd0GWwlpSaFAMs3QDVeSifYUL1CCy7GsnQpu18FUY7HLGCXZ2B3CYN0ZQmVn8GM5oVuHH98BpExGovcGnpOGHfjpFsS7PZlBgyMKHWZRUAD8MsRiKbAZTpkFh'
        b'tBryFcOM5PWIYZYRD3vRBPLRncTTZ2+PnK7SD70U+TaLVZFhUDz0MxitOQYz7jkeEPz8VHDpPGRGPGQGP/QaZlkeFRW1AqcTJfZhL5Uiu8DqGquJ+E8paxcZTXrDmnbv'
        b'xQTgOcTMw0m4VUs7n1lQWNLO5xpKsMmLWy7QG9q9MkqsBp3ZrMMvVhUYTe1is6Uwz2ht582GQrOZ2KHtXgtxA7QmZUC7V2aByUoMCnM7h2tq5wlCtIvp8FjaRQQWS7vU'
        b'YssQPonoC5JgtOoy8gztjLGdw6/axRYhA5PbLjVa0q22QvySt1qs5na+mDy5fEs2Lk7AaBcV2QqsBqVvj8roT3lgfTLFjatSF0q+Sua8kqIY0V15hohDOSPmiNbK418p'
        b'4+/UaGVMIOtNvwfQdJyfDcKfw3BKEOMvDsSfxTg1iDpN5Yw/S8SpDKfibywRnnJW0IUDWDl1rYYwgT/iFn9k2UBcCgtYlq5W+MDWQqyiS9HGuGS0RaNKwApNOjdhLd/J'
        b'Fy8FQgADJYk/4gcWXKwdNAEqjF7Dgosr5e2cJaxIZsXaLPkzYkF3gCPizc7aucmYdMzzsShkcsX4PxYeoaCJxQyTCwXNWAxhscRjYcAT8WHR2/lsBtfH47rnYxHGEdGC'
        b'xeA+TIBESIj0pD6Rnsd1cOQb/o/FIqmnKEcQN+YTer7wlJ6IaZFdQtsSO9+LhNZpPexkQL/zzu/8ZFAks7PU0yjSYBrWkFmkUzmfPDTuTyRNKTLPJBPMWQzWdk6n17eL'
        b'bYV6ndVgnk3eStslBPfydYXtUr0hS2fLs2KUJUl6Y6bVnOyqsF1qWFNoyLQa9OZnSFoSKSx+ApZ5eD1J1II+3VXvAMzKLMMpkvEYWQiS+QuIQFCNGk0yJoT1Z/wpctnI'
        b'GgO6t3piYgQ8iK7S1XFYHQ1PqzA+VJNluUh4TYR2J87sZoeQ1onaTFvrtp4KyIpqlo/L2LEzLnOmq43kVrP0+FFFZpqpxkJ/FSj0x1iGC5pHY8zwxSkMEaXljA82eqiw'
        b'wjiBRSBTxVX5kM/VJAaGx4CQ5r0xOLIsqdtf6WVnCQ71ZMETxCZjSt2dHxMgeDvRHMDaI7hhjnym2tN8jPIsbgyDVs7kAgwW/mTHgJRypiAKnhgj91zyCafwBNnsHE0L'
        b'qiKaDSaDLPydoDzVvILspNaJpZyd1onzVVaJMaJyWLPhTTLyGafTb3benEdkDiYgXIedp+XzsMYZhTVO3irKYrHW+Q6DtUkGrJXhYRIRuUyDo3DaepErOAoTBx62LYzT'
        b'lY6xjJi97ZJinZl6KLlsjMmYl5pzV5tnEAxLEHCxwylJ5LeAunqK+gbMvKVPzRs7sFaWTrliIW443zLDjbMYP1mMm3KMo5j9sYT1BVFmKWNlGJeDsN0QxqyN0WVmGgqt'
        b'lg4ZrzdkFph11s4O2I4GsFzOIE2TfmCqplE5NGEVSfD5uVyea5eQYcPEK1SZ6e6elxug8YxrOYoTmP4AzHrDQteGPboPLlVCR6rLI5+9f5YI0rnBkTgbG8M4dSXAKYZQ'
        b'/p8XAxsTkzSoBd7RqMOVYuATxaJjQ9DBbk5OqfO/ZTF+GEAaVvvSWEr0YpdPI43bKRW8HJgGvbJENNJPWs6k8e50wiAkmDEI0X/kncgBeJAmpigpae/ljNSba8wzJBXo'
        b'9AbzoxeFqROPxVVi7uOxNMH9by0L8xobWf8LHYkOWeC58LjkqPhk1AiPPoOqSPBJvHoBqkpJDSe8ksSfALgJnfJaBg+vNkpT3xfR1eTj03p/rv1C+5k2Jyti9/hl4TT2'
        b'7YEQ+5bxhfa1jLT77z2384XLDdu2MacqJxwatnnQ3o2x/UHsBZ/s8GiliJryJnQXNqJLqE5NwqyKnK6JsFBg42GlJp/mmYLOCjFUcC826j2C4oh7IiXTSlefKp6xUQdG'
        b'I9rVsQBMl3+N06x0cb9mgda59AugY6mw8hunts4BZHExEJ6FtavdYTqFqDZvCBYX6IowGrCG+EaiUU0S2orqMASwGm3F3BrgDI2+qBnLl5vOBZEnMAes/xtNRmt6uqcj'
        b'eQPIIbqNnFkb1g1HolwF3AsuFkNeVrs4j759zIILprIi8rnQ1ba5AD+yCZkQFwAow7/7Pf1/j2v80Zg6UcBUDiM/kZTiLLEbW/knYmu3JYeeF/EkGiFqC+NmZkcsFWrg'
        b'QAm6LIctnD8qQ5UUo+EVtI0shDsDODsCrzBiO91oVxYAYIV3nw2XoJ19UZNtJMGAcngenhOKhcPz6FA4RsQ4NaqBpxeGJySjraqoeHVCMgNMfl5T0HG40zaClDqBzgWl'
        b'qhfHoTplQnISzmuAR50UhPOOhrvFQ43wrLHikJqzEPEiXxHwufaljFOGU7ql9/fC6w1tS09UKDefrpxxoLmxrbqt/PRS7kG2uC03ZOLSS+/W5JXZd4eJR7aGBti9LJJZ'
        b'EkvsG+xu+e7Ndc/JDqjB1x/3FmvWY0Ii6D3EB+s3tYQ2RIAfgBrzGXgEnrZT554SNoYQjxo8DG97etX4lWmrqc9txRJ0ujsR2rjlmAiXxNP6Q+E1uCsySj19WpyaBWJ4'
        b'jI2BDchBfZDoxpzSxKiEZFU8rHd7K0VwN9oHhs0TpQXD/a6ltadX/XwzzQasbqbnF+hteQZKLIEuYimiPjSWd7rE1w7sjredSrsok1ACJh8i0zrIRvRoMcMKtGNxE5CZ'
        b'cKxOBLQzyJOAngRINypy+7unu6jIpWUSWpJmef03tEQacBv7blqSa2isUr9Ry92U1BgtEBOlJLhpJqWIGeik6HFkNAadpJREyQjeRa22KEJ+G2ErrM5Ge5yk9DgyGr70'
        b'8eEIzkUpZziCkmlnsrr6SqST83T5GXrd1M24pJnwJNsSgpAH0Zl4iyc3J7z8Fjrk4udoeyI8F5cMt7jRFe3qtKjMjQqwwB0LAtA5AM+iyl6wDO0U02hDTOAX4E2nY74O'
        b'1ap4m1PWLOBGwnuhnfokAh7hBpRTCmo8S2bZzSk5Ktd5PLuce3Z5Orvcev5RIe2kGbd94ckpJ5EBOJCETiaSJcQoITAgNS4S1aCtizCBq5WwNQ9tSYpf5J5LLBGbDN7o'
        b'LroFq+gSSp8iHkjjlGRdRaXSqYCNLM7qx9o6VSmESGM9ISFS3dePRHzgic3f4BUCa9EFikPweiB0JCaSNUx4KSg++ZlwVL1E4I/PuBtfhHEItUnwqB5KM4I3IG/JJUWb'
        b'xp4xf0pj1V7KigpQ6pJ0eVSvUJk/076a8XLGaxnxuu36BxnnDJ9M/+NbMWDRJGZRbPlCR+xHytaYna0GS5/Yj47HjCpTzK88Xj7nADO070sNvwhk3vz9c79+7r1fhLxy'
        b'v1EO3joTcnZ1vlJC11tiYZUGXk/sccmF5+DWAMrrlBMR0VfOYYWoK7vEzBKnNtBYMsx8HcCTJw6Ae51DTVgiHqHLVmfkdFOIawH7+ogUZ4u+6CIX0jeDqjbmAnSEhFXi'
        b'LA0T6TJ3FNZlA9ZzqE4qpjnwzDahNpLnNFanSFVkWdJnHIvqF+TQvqGjg7U0VATtQ5u6BovANtj80xm0nASBpBeaC6zUvqccOszFoTeAAJY6e7CdzgYQlw22x9eO6c4e'
        b'DWsMmU7m2GEtdK5ZoH6RYIZ0WGtPWvZ0ro7K3QUoBy/Gj62MS5iU0d+/efJw27M4fRBmGLu78Q9P3hFW+jjuQQLft09AbaI56MZ0eGUYPK0Eg9GuwFXwyMo8At0bcSH8'
        b'37MaMT/5YMQ37NWR3+X+B9CF8QfDGplWSdw02XTtqPdGSQ0vCMk3en/jt9OvcbmwXh6z9EtgfG/0NtZyBL97Z0zJsLo7vjDGf/Nf3tXkjdgZN1p2P+SL+6B5/LIH1qGG'
        b'996PmxqWFTf2hV5v/fuNfz4/92HDr71frPx6snLxzBEvrzn82az2rxdc+sOUvqaggEmfvCR93nBlbMa4puLV6qirtksb6k1/vZ37z8sX7luPHklMPXVd+87F5c+2LPyi'
        b'd8TvfjV6yPS67+qit++Tv57VOi1g9YiEm18ltC+zbDjedJH9cusPX3NbB0eefN2i9KVomgpbsebkDuFbGdehxXvpqKYPb6Gj6FrnxT94ZQPRVOAeeIqGPbEBcFsXXQXt'
        b'kzvpLxvWWcnOHHTIL1agKmEO4QU8VVuw/riVzKHAr8fqxSuSUDPVbvLhdXQMazeCbnO5hKg3aLeEUjzcEQSPdhMXbWNFoO8YskDbmm0lPjEN2qLFJgTWP88+AnGeZESI'
        b'9JR1FMJKDKrAhdzlJGAOauuDNnLoMmybJAzWDbQNVQrRMnHJz8ByIZhFvogLhxXwAF32TcXMqk7YT0DCq+FOtEcKj7NrUM1qIZj3JDwoxOBSowm1+nXYTfAWLKc8CrVl'
        b'MB7yzmrokHdo0zQrEUDxPr1QbRKD5Q6sZsYDtCVc9wiy9Pqplr7YzXF8PJgFZTfhLnaz3q0Qst7EMUjcKvgTzwb4ifHTn/Vn1vZ/LPPppCKKnWkdLEbyNLCy5jWgk721'
        b'Gj/WdVIXHf081cXHg4QbpWsH3unOhPT0dll6epFNlyesIFF7juqktKV2X7JhS2exZBow+3Saiz/Du3Kaafdy1oRroR0hwTYG0hHyXsr6S1gmSIZ5JVkQQsfUAzqzyoOw'
        b'zgPrWTAR3hHDxg39u7klXKvSFlKPy+1i4PSChgRoQCir5yq8iJuFulJEgvva7UqZr7Pi0TPhkdNk8l1qdluok/HDqVc7fblZEqfmxVdJsOYlwpoX79a8RFTz4oln8dE2'
        b'ane9WqShW6FC0XnY3NlGRce8qGYdA+8pWRreNXcdHqKb8KJnPiy+UTUPwmbzcfBoNLV3DfDa5GfRLs9ckRFxYhBm4Rf1g7uM37zyMW+JxxmLx/7ic+2y+w3EoHzQUtFW'
        b'3lZ+o9HIpEoSJbmS3838OK0yrHLwJfnuwBN5xQrfjwwjx8W+HfN87G9j+NhjYGS2D/j6rfH/8DcdqlfylOJTsbp7JzIK7kItneMw+JXoeBjlmOgGVl1OOVlman/BILww'
        b'SdBHjqLb2RTqRFi9Au4Vdk4FGDh4Nm06tUhRGzqsJ3wJj8NeAUsoX8L6k1sVeRqa84xMzsJ4kE6MO8obAly8YQNQecsCGZ6TsthU7NsNcaLc5QSKEbdzmXmWdmmWLY/S'
        b'WTtfiPO2i606c7bB+kS1gzeXkc8byWMTeZS72cEGSlyddY93QzwZwuOgU7Ia4tQmLMFcQh5rKU+kdJpvsOYU6GkD5nWuYem+TGt3g7IeP066HKZS1rlPc244PNRBytI4'
        b'9lmy0c69y26SQgxPhvenBkJ9Pt1dWXhfplXdKZkGuq2gdKa+TmsobuoDNCjxJ+4Zcy1pdKa+UA01P/NhLbb7LqHLPkU2dBXL+2uozVqMrvgUw/qVvF+hDLURf+IJEWqN'
        b'g2dt0wgqHoQnsAKN1bckDaqP1Cyixm68D6zFn6pT1K7NwPAcqlJFwbYF1B16Gd70RvfgNfMT9y5zNGzjv9y73CO7oUrANXRxeCTakwhPJblnDuddyJFvSXQjY8nKMYTU'
        b'kszwMu0h2hUJT4czIAxu483oODpk/OjLMJGFrnwULv9c+/KfP9Om3W9taN5xuvz0g9PlI2uLmIYrDb0eSNoaJ+1dEJK6d1a/oFHlH00Kufhu7RcTQ4JayxbGjLLGiGKP'
        b'YYZCAiZfTwto8F/o9Eyh5nFLscmCalR48uBZdii6HCuCTTQMK6ovqoiMo8xlEjrEj2Pg+VS0kfKgdKys0C0NWGFSkyz9ESYqP7iRW5WEWmjNvlJ/nKGG6CUcSFbzExhs'
        b'ylyx0c0k/cVoBwn/CsI6i2s/SYkYXn3iDh4fXWGhAdMcofrObqcN4BmyUCOExnszayMwP0jPM2YaTBZDepa5ID89y+hpxnhU5GqVcoTHuGwZIQel0c348asu7OJSp8gv'
        b'sqSKxcgOa2KKmuiSLhSG9SnU2sf/BQWUWidwNzrhYaE4Y+NgdbQw/np4yD8fnR1Pl04s6Ai8FEkGNhbT0VgWiNAhBl6ev5oiFJcGKzDBtK0uRpeLZNLCIlkRvAgreRA0'
        b'ictGF2GV4Bw9hDXIWxZ0GbXFwgYv32Jfb7kUXVxNyLNIBIYG8KVwLyoT9gbv7JeHHCMSsbQRZlMKW1msB1el2Qj/gHuGwlPwDNqB6bk6KSJBBVvQztWqcOJKIF1e6dzp'
        b'kip17tdmADwGL/nMgvvFtgm4gtHw7OJHlPYoGi93Fd6d5402o32wjao4OejSIFhbWLQSp2xdja6ia5jHWLFCfA21oms23JdUHm7EoqycSncFOgZvU2j3EKGOjZ3aJAnG'
        b'3EYp2sYtwB3ZRffsLMF8p41UC+94d6p2NWqTeYvB0Hgea/51BqoB2wj1o/PoJAbhEgsWZIBJYBKsDKOjlxo0A+1IUcej3fBCXLwE9Bovm8KiQ2jnDBvZBoBuw2s5Pmqy'
        b'czFxiWvI3IwOXqEcLRHtXoE2SuDtZeOEgNsz8KA5VQz80WkwFAxFrXmU758P9QL+4IGY1WrzvimdKgTcmr0kQAaw3qvQ5jm8vLAmTJPfCiMy4sEUCdDKXmfThLwfK8gO'
        b'/Jgpvjhvb+N8YIsl81uHbhuJURdJfEXV1DmEoSwt7A5nASyTlsbh7CE7GJFlLKaPF99bkdwwRYOm+2/OfvvHLb1/GFLkNXFo4PHZgdbpjMg6ZFPGS9uTZ400ZQyN7tNr'
        b'xDv548WS96UHhg67tKX38XdLU/6y/+TBg89JPimUi73Ub9+fv6J6yYuZhXffuPvGhdQv95cFoqX9Zq67s21VzKDVNxepL39wad6Af/2lqH7ivnmBH7WkxXz7ZfMLcx+c'
        b'2/r23fCJY4O+vfXLndXKd1t3Fr/yj+JVrW/88UHel/+2xg05kzRzXVD0B8od+Q3P/elPh61fThpTnmZs+Hv+6murht06bm19N1li+sqycN0XjRs3t99zWK5vXL4GfJuc'
        b'tQIt61+ordz+8p3nVw02zXYEzZkW1XagdfuPXs8etvx+2a7IL9tWNWwxD3svOHLiVNGOpYWrvF+Yc/jwR80fTVueduJM+m/jfj1u3+A34jL/+bE4+MFn8u17NnyqLa4s'
        b'8VX6UQNxHDodlohH2edZsre1hjiFfNBFjh2J7lLDrtQXbcPcBd3rxQC2mJmBLoyykj2JC+ylkXFZeso5KNtGx9A5GnhbLPJKTIqAm9GJKIGx+OSx+OVxdJ02CM8shJXT'
        b'8NdalYbOqwhIUS1bOgLeobqjHNaMikxRwVOI7O0lqocEQ3SXRddg0wor4U1T0EW0L8XWaadgCWZ/TfSt3yAsDqviVfFUcIgAajL6TeayDIJiCx0x1H2Di9YlKtWYaO9o'
        b'sGYTnMRPhy3zaM/GLBtPwpxR9TqbK8q531zaM8xqm9BBAtP8IZimJYBXM1gruIcO04LwtnV6ZMIadDUZG8L8IAYenImtcLo+chTr0+eFWgm7wQwH3lyYiLE5GF7l4wow'
        b'Bycia/hSWE8FpTc665SVxIlxTTDCr65Ft9yeEeiAJ9wq+XrY+iS/3dMZsJ7Gdp8ehRsViAs6BOI8Ig55Gs/sz3qz/t74jw1gyNOb88dpIe5YBxkN5wqgGxlI4Jccp8vZ'
        b'ABom5s/KWHOlSw6fZn+i5e0Rf0gqeaGL0LzjqWPTEz/g5jhY30VoSvVdxaYIrLRK4a7kRUqObo3Im4tukiW2M/ifsMzGwCMWuJHueEH77UGoVoPxYWdOktMBC6+w6Lhh'
        b'mrAzdDeqhWcj1Rp1hBhP7c142MTGLoTXM7kual6QS9VLw49uxzgA90EOTKejHFhHn6wg93KC6LHLCRwNE+A/GIpn01vh8bPAkG20WA1mi8KaY+h6rlCUd6e88VaF0aIw'
        b'G4psRrNBr7AWKIjXFhfEqeQcGbJLVVFAIjszDFkFZoNCZypRWGwZgiujU1WZOhOJ3DTmFxaYrQZ9lGKJEZszNquChowa9QonGlKoXHXjF9YSDEKnmswGi9VsJE7jLtBO'
        b'pLEyCmLPTVSQs5PIJxJBSqp0Vo972EORXEMJifIUSjm/dCmoVxTjMcMw9ViBzYJfCsXd+efMjJ+VSt8ojHqLInyhwZhnMuTkG8zq+NkWZed6nKPtCnDVKUgfTdkkulWn'
        b'IPG/BBxXXVEKTQEeuMJC3BYJFu1WkzGLlhIGFM9Vho4AhOcKz40l02wstHbrSDfnhxx0tUZ8NHS/JqamazNTo10LfQuWxGFtMzUuQbRgwgR4WumNbpRMQJUquGv64Al9'
        b'AGpAp2ShxVndSMDfVb+mMwkAJxEwbiJgHX5Z/j9hFa1bdAzhHN1PIFFrcD7KVbrH9HUPfHC6ltzLeU9j5XUDhDTTfa+dyLkVm/BlY03I66yFuPsS4Fufa9Ufx+lkWZ9o'
        b'P9XmZ32hjdfx2z6VvVpnTHo3b05a/zrF15q3J1+Vv21V/P65N58DAcYsq67qrTOiz8/oGvTg88QJhlVZr3ysqsnQg/3SoPT7rf6vXNSFX/5Uu+L+9YaN25rLQ/UzY7js'
        b'ieCApP+38R8pWSri0PFhqyPV4YKXfN9MtIdV91FSU2weqo+IRFuiI5RwC5Z+NgbbG41o+09fVhKlrzbrCqmcGdAhZzaAYSSIOIQycX8mkBHTvTZrlWYny/KIjXMit0cK'
        b'qdG51V8IQ+0QL08A7DQjFKCyBYtbMBhDZgnqkC1l4P1Oq0fEowAvhqOjkS4i6GG3cofQmROgjE7Asn4uPJUGD/sZ0QlY/4SgMI46U37afvVuLkwR6MmnINHYZpFZbui9'
        b'NjZm9KixI8fEwmuw1Wo1FxfZLNTauYyVr6uoDV1Bl/ykMm+5l68P3AqrYF3iChbbXOiaFzq3GF2hqv6R0Qlkh7NUkWKMmPpMtqD/382NBw0AxJTFmiLalgx1ovbuS4Wc'
        b'ZQX+NH2ef59fDAooi5Hx92+NFtcydzdN/5pTXX9NMb+p96LZh3/zw84jxWNfL4KNs3a/MjQy6c0tJcHBfqHDn9k+Gv0FLHkjJKp094m6H5dpYw7Oj3+v9M2ZmX+q/Oo/'
        b'4DoKLI88gbGYbpa6jLZhrdZp/96Em506JDuG+ibhqf6wzeVXQOdgMweoZwFbz5cfFy3y5Mgvc4E1PSN2LEXuEE/kjiXIHYDRWkrj4teqngqtndW5li7cAdaPjwmjOTqQ'
        b'mpwkEdMNqV/vtC+UIAW8gi3as0+N1agmGlanjBqAzo/lQDGs9Y8aMI/O/6/6YqNQ9ryIbM58RhkPqLEJa3KGoB04bZUsCkTBClhH816wYVtRO09E7MqVeTMEBAqfzgNp'
        b'v/sMmK5N+nH0YAGB6Jv5xdg2lZXhmrWqrSm+zmPgTIlgZ7ieB/7ahHe8g4XE2St6AcX4CQwo1KremTQT0IiYPIy+h1JRPdq5aEwMquGBeAGqL2TgWTs8Q0sdlfQFo5c+'
        b'kOCqnj2bniNUZeRamTIuPN4bvL86xDItynn6k09UKqxPHYnrQvUiwGmZqej2cNsY/E7lX0q9cU4bHNsiqEqVQNyMxC4Jn08DI9DWSLr2WR3prcQ2/126CBwRLQYY0KWB'
        b'04Hs3aVfaZcAuhE7e8xwqXQZiDkx7EbR7r7s5ML5r41NGJbA28hZA30M2Ga5hIXLOFEySIZlWRTo6kkTgZVfQ3pifjXM2zmw86aCCjB/HDO/zByyaOcUmhgZNQ3Yl6Zw'
        b'IEYbcGFZLyHnkRkqRssWJkoUZZZ3bDGLaeK97LeZy5x0DOO/sWDpwskKmihdNo/ZyTbM5sDG3Hf6vDWXJo6f2YeJYbVpUlBWGiIbMZkmjsq2gr+C95M4UFa8d/2DKAFO'
        b'y0LmVFgqA/x1kb+0Rzuneew2Jpz7ZDzQlmWHDK7UCjvHvZaC6+A+8FWUrV1qCRhBE8/0GswksfNTuELcUIJ6Dk20mweA2eDXa73nl9lDiksjaOKyZ5OYJvb+dLmiLHcv'
        b'f2kJTcyeHMyoAtQ8Rr/Sa5jKaOKnQ3/NNPn8gwNaXfTOKTOFxF9NfR5UGa9wGCfjvwxMEBLfWmcH31kXsGC+Nmif12Qh8Zus98B15l0OJ4bWiWY5eaJYBkJyxCRR9qsB'
        b'vJC4zFYEyhhpmBi8nxG4bABjfNN8hrU046mM0acseuYl05vT/c+tzP+VfjIK8BvwrVr18qCBDZk/aOUMf22Ez0tv9309rm5C81c7Znz1bENKv23/mWbXvPZMS/+KCtWS'
        b't9at/09LS/+LWX1k90oubXpnwbyDX243/aG/tfblmTNLU0r1tmtnA0fLMn9TW3Cv3+azfYKXPdAm3nwQ8uc6y2uVl7yGf8MNCh0xWnrs6F9HLR5S8sKyLUMfVPcd9ou8'
        b'GmN87iqDPsXr0sZdO8qL4Zxi+cNBiYvfb9r1RXDJ29qvB144MPNmc4jP9vd+9fn9m2n/PLKsbeWbgWcU2tyS1CKV9k576ezX/ry7L1zVv/9u0aDlqcN8vi36ovV/JBM+'
        b'2SYuX357R9HLjZ9c/NH/9ef++G34mui/Xfud6WHC1wutfpeaStIO9VpdeG3RH8SbZwUu/XBAQl7hQL+/+m/9a0jKXwN/9dcD49Z9MHTlN8kDvx594cCLn7fI/lXwrx32'
        b'gD8bfygbMenk77eduBA/5cOVezb9Ef2hdvF3FX/r+9q3U778aJK35Xb+C6GlL5eG7Uw8ciQ4/fwBW/y5te/2S+nznzPW6H+OaFInx42a+OGG564tPK2eM/Xfdt/5uVsb'
        b'D/VSSgXn9rjFkVHhadTqd+2Xriyhr7BudGJ+JKqKBnCnHrCwmZmPToqoAwOex3z1ZGSCOlEdoREBmThGzqI7XvAsfYsqRw52ySY1qnaKpt6olmphKngwkRzD2FacEg/P'
        b'Yg6Wxw6G9UOpWFsCm+DFyChlQjTcJBzVKAJ+qIwrQGcmC+dzHIbnYEVkisrT74IOwM0slvw3M2gcUR90E54RAonuybvFER2D+37q+r7/T1+ffmpVUuqSmVTg2j0F7iAZ'
        b'w7NBcn9vnvE8oYv8H4D/h+DfAGYoI2b7YU1TTjeukSXEACaI7Ovu+tuR9gPLsj+IOTEV41K610OGa+TJckHYo4W6oJyK6OaTdonTymwXUdPRQ5r/95v3sAK8lXymaz0N'
        b'biWgHj/6d1MC/hThqQQQN/pgdGj906kAIngC3gXQAbFCeFvSmy4IDJsmLC66fbwaeM7pKkFXJ0TDyyJ0Fh1OoadJzYKVxR1rcjTQFF5a6Y82cwOKNwjMfQxGfvC+jcGK'
        b'xOtRTqZZ4kMOGY5bLsLKwcNUjZB4dhBxT4eHeCuwtN9QDIzLfb5iLIfxm3XP+vavmyKHMbK5Xw43vnH5T+OkRSPGHq9bfCxq8bvL52oVccUmZsn7FXvlKRenTdsQ8OK3'
        b'3hVeh8Mjo95p/dP2yPM3PtgdfPsj34KScdaFDSX/qljdYJpYs+TIHwMOJH918Vdfnwj+OmDHSx8wASdmlH3x3nt3tx04O2x+SVnFuu8ULVPWvxBpiXgn+OHWO7+Rf3Fu'
        b'9L4lG5aPO3np8MHt7/P/+JPkKzZ6xV+HKSXCETfo5AZ6anDHmcFwE6p0nxuMVbPrwkpbXUQ0qvXRkOAil3sSbmKEgMTD6DashrVqrMR7LBShrUlkIfAQX+BTSv2MtkzY'
        b'5jmRmEvAloUBERw5IPeQsNfiGDyxnuTRRKx1z6Acnudmo2PjBRX6GmxA52FttFoN72nUqCZJKQZ+/bj0WHSdnvyHLs+g5wNWwgspTg3IfVhZX7iNh0dRzXiX8Rj0v84j'
        b'npqDuEiWcpAITw7SjwQbsczwuTJK4yzZysoK+7nElGeYt+PcTvN9C+lG7//bcG9z0zNpWtKNnv891pOeqaxpWIEaIxMkkU6SZoHfWC5rOjrV4wI0+bHImI5QHT2TxunZ'
        b'NF7PpYn0fJoY/0nwnzQbpHnh/947uZ28XlQvnO5GFv55vVgvoTujfAwyvVTvVQH03nqfejbNF3+X0e++9Lscf5fT7370ux/+7k+/96Lf/XGN1CeK6wzQ966QpvVyt8a4'
        b'WwvU96GtBeB3UvKrD6onp72RMw+D9SH0Xe8e3oXqw+i7QOf3vvp+uIU+zm/99QPwtyA93SCvHNguTxK4eLLOpMs2mD+QdPWrEt9f5zwKGrbRKdOTShgtxMlHPa36EpMu'
        b'30j8rSUKnV5PPIFmQ35BscHDsdi5clwIZyJufKfjUvAauh2StESUYn6eQWcxKEwFVuJs1VlpZpuFnCrfyYdoIVkUBhPxMOoVGSUK5x7gKKdbWJdpNRbrrKTiwgIT9RIb'
        b'SIumvJLOrsVFFsHbjJvSmT0cpNSNvFpXQlOLDWZjlhGnkk5aDbjTuE6DLjPnEb5f5yg4W42ig2k160yWLANxVet1Vh0BMs+Yb7QKA4q72bmDpqwCcz49aVGxOseYmdPV'
        b'120zGXHlGBKj3mCyGrNKnCOFhXunih72z7FaCy0To6N1hcaoVQUFJqMlSm+Idh7P/nC463UWnswMXWZu9zxRmdlGDTk4ohBjzOoCs/7R/qHxwLlpkG7FyhI95bZBjkad'
        b'8A83d3c7m4xWoy7PuNaA57QbQposVp0ps+vCAPlxur5dEAveb/zFmG3C4zdjfrz7VXdX91OcLirW0HVteARdhTuEEJHWIY/fawJ3w3vCfvC7qHyhhxoSE/VMeJwqKgpt'
        b'jU5gwFi4R7xO21vJ0Fg+VMZPTcR5UtRky0N9SmIGAwLgAQ5thMfhEaNlwklgITvmG44sIbu6wv/4KX6qgj7Vxgl7Fb49qY1aHK5L0LGXQoNjVsdE65+9f7GheceNcmXt'
        b'lfIb5SNr1Ztv7DldPuzQFOfeyE0rex0qehXbD2TZUNcbXfMUxR7SGu4wFqxHwoop3DIIXafiGAvjEKOHOIbVq6k4HgDvwBM+uL8RIUr3nQN9oIOXDjULS5fbweRItCVu'
        b'NA84dIuxaE1w10i6Jpm/Dp0kQwB3LMKjwNCzzuDG7LH0JTqKKmF9EgnTSVRL6AnTiWg7BovKlv2RcCepdC0zehTW1SRrGbQPnoatgoawrQBdop2rSk4SA3ToWaz8MegG'
        b'aoatroD/p1juIxGwVDYHecrmDSBQRvceEA18bXBnvHVvaRRk82kh5te8B4An7ik4zQrZOu+orGFd7rwy9+93gZ5hfY+C4NHbn6ijAqxynQurJCG5rmWq04wAQOetUGYb'
        b'fjRiUOguqG5NuvZJPQx95OoXboTTF2Q+FVAVAlDSdKetYj7wCIgOuCB6GOixAuZaSIv6KSMgTSf81ai3PLKxw+7GVKQxl/LWw4JbZp4R8221BbNv5dMBkS0A4ZNuWFNo'
        b'NFPR8Eg4jrjhGELg6ChBZE/Xge/cvIuf05McKT93nk/rEHnw859xQm2nk388OSmhnDFoT3YqqucJXWK9/QqAW0vQFepAHILuRMMzGMTS8agGlManC4f9tsKd5GT2eKq1'
        b'x/JAWkT0eTYB3UGHjG+Vv8tZlpPRCPhj/9qXepXFyLhhI/oZy17MGcQlrYpbaX+28vfK4dFffpEz5rTfstG3b0/4tW7h+H/tWLjq6kfjT5zOuCHxDV/3feZx9dWJ4kn5'
        b'tRkXXpqQm9Y49ZPtvf/0L+AfHMq/Xq70pjwyCguAMoFJhui6GzVy2ECjTtDluDHEvRrvjBjZjIvdYrE9dMUghHachdvVHRElqAJupVElZSHUXbMels91+Ux4DZOXCFt7'
        b'oxuUzUX3yeiIQeQnMGjLSBKECFsoh0xITR8GOticwOPg8WRqrk2fHpOItkSTW0P4sQzahIf0Nrq0XvDzHIKbVrm2q0vHeNHd6vAaOkrBLVwNTyTS80Hp+ZORaCs5ghJb'
        b'z8eFk4Hr4Y6F5Ij7c3GC9FoLTxPJdYbD/PoyutzpmLun4bOY9gymTHNJoZUyW8LAPZitUkYDO7xpVCQ9Nrgbw3OW9txl8XSHVzoPDe7guMfx43gPHPf3j+e4TgD+H+pO'
        b's3J0pmyDEErh0nZcpN9Fk8IK0dMqUSbD6qfVnXo+T5PXOJWbwSvIDRAdyg1qgYdd6g1nMo6eN42jISjmg719X54UND0mkP914+3vbGMzB4V/5vhk9ISas4MiXg1v3aw/'
        b'+d7DmtCL8JcfxRre7RM4wP+jowft/y6v/s2IyYogWchI3eZnz/6wIriqzev2we/fFr/yybd+zY2BpplvKL0oqq+E5+Fmqn3A27BW0EBMmII2Ue1m5hyyGSqFbDuFLapw'
        b'BqB94+SonjNgJN9KPRazx0/3xPUguNGF62gX3CkoKrtQOWET0WqyW2wnA/hoBl6ank3dK4ED4WVy0i68lkvuvID10R36YAxqEk+A+8w0Fm5Dn4lORcd7KlV1bkdTaozG'
        b'LLNxPHI4R9OlJE3EHII0rs6A96BjJe2hWxEqRZcoY5qwGN7C+lNFVx6RBg/8dCr1y6Q4l+5CkK7hy+R3ojf1SgYyawd0oZEuhZ2ui8ZH0qZ5n5soT+JHaw9E+XononxC'
        b'g0quXZxTYLEa9e1eGPWtJiLs28WC0H/07h5KuLx7Z4/IvbNH9NidPRwVkvwHM5kuxjr5maHXE4OHEJuH5iAYim65/UiKFToh0Gsc/hw/20X3GTpTbneqdRO6s89CyfnC'
        b'V1w4PNFmwmamOn52D5FBHlFGrpLEqCbFOkUVKXuC12yw2swmy0SFdqHZZtCS4CDhvAK9SqGdq8uzCGm6PJyoL8GKDNGnTNanYDze3RgPpzGGHfkNZyF7JYfU/P1z7cr7'
        b'v37unefefO5iw43dzeXN5RNq2xrb0o/sbqscWXu6snnroAMbq5/b+dqHgxoGVelGzorZu0Ubx1wcHwt+ke47/8AGJSfsNbqDTo7ozCAOZgsMYlO0IPsvwoNoJ2zBQpIy'
        b'ACf1oyYobNVGp9HN6MSkeFidkoxqkqLgFhs6Gq0mcaFKWCeC50rEP50U5Tq9Pt2QYcy0UK2VUqJ/Z0pMJHS4tn8XouhczmmjiAUBeIo8TpNHS2fZ6XlhBe+RrdCdl5Lp'
        b'Wfy40wOZvtCJTB8P0f8VQqzAhDivJ0JcQN1amBZNAvKRuDcPivRwaP3/R5OkWHxqikJwRVkFzxW1HrKMJl2eQm/IM3QP1nt6ahzT/hVDqZEZOeppqbErLa5aTqkxKglT'
        b'IzXrj8B7fT2pMQO2AUqN+mIhgqzFoneSYdwEgRDl061kU1vyGHQlEl2BxxJQPaqPToT1LnIUaHEa3CIJwLS646cTYy/BO/oEekyj9NhFN4vqVtQpF891oTvzeTeZteLH'
        b'Kz2Q2dVOZPbEhp5wcw/jAB439zz+vHUnjT3M6IHAKLZRSjDZ8jMwUWEE83AjdzhnM21mM2b+eSUehvXPxb0vbzbx9BAx/d5mcjlQa0MzxbqRbqyb/sPj8A5kO3xa/Kuc'
        b'MmBAOtxHkW4CanRJAYp0cA+6Ldh3Dmw7HXfzf3QenSeoBysLrWQrDjo0WExMMWw+dkiBaCFWexo8hRrgDYkCXjV2uaGpR1zLLLCZrB7TaOkJ1zKkPeFat6IaV9Ri4SP5'
        b'veCEoHh3ET9+1wPenZQ/Du+6Nfq/jHfEOjI9Eu86IpifGucU4RFEMTOaFMVjo0ZH9MB/nw4HJ/X9hYCDY5dqCA7GWrpj4WNwcDnIPurz4tUvMQ7SjZgtcC+53rOD9aGb'
        b'6LKAhqjaJrhE22BzgIcSMg+rJJfgdnjeSpbHYfXYPiQyTBXVGQcVMRgLx0OHGOe9Bk8+BQ76kzF9EgquEo7O6oINXUs6ud2lR2PdFfz4sAesO9wJ657UjjK4685mSXq6'
        b'viAzPb2dT7eZ89p9yTPdtUzS7uPem2LUm/eTQmQ939xMHkeB0zPbLi00FxQazNaSdqnLzUnjH9olTldiu7eHO4+4FqgpQxUlysYpTdEu/uzjFDx8gzvww0aGai4gu655'
        b'H57x+GWlTKAvS24O+EHMPeI/H+CDc8lkjL+c/MmldE2j91C4kQRLwCv+ggsMXUnGpiw2RlkQDjeKNqBGdLLbugoh8+nAuVW+85KuEDLc3tu5BcQ5d/T86oeKOWvIeZvE'
        b'm5lJ9neYTUQp81DCNNhc7DyX5qvucejiLb2LH5+z7n3oPGMjp7ewaB/a0bERHbW6VkBs6ogZAXT1IsFbAreWwiobOb4xEO1Ji40RwyM/MWbZHbGMbsFj3diej4tpEB3J'
        b'GegPOt+p2nEG8M+5Xoc00t0lK9MoORq28upgHxAOQgZJgSLvHf/N3jQGdN0kCYkBVYC5eTPeCQlJ/R+QR2J5alIniz4NuZH945y+yhu589NbBp7Kvbl0U/g+zYvjRy+r'
        b'Vx1MOTfp+MQV/d+IOJLxH9XD5A2+H/f1Lb29qDW8YtaYhD9rSmZ8MEAc5t3vvaUz0z6cemv4gQXTFlb33xlxe+DymdHxC9b81q+t4MvR7dy2iAWFo/odH/Px7G/1rHl8'
        b'pG9wzlKzqGzwx7OLvT+zFBeGB787p8Un1Pfmhh+xdfDJArsP3aAqCySH4hBnsRxzSeovJs5iO7or3N88lwN8kgEPgVb2j7nxQtROtCYADPUnN2RpJ8+ZECkkvsgEA1UI'
        b'3Wlql87kAD3yER0dhOexNlkd1S+e3JfrOmQMbU2UoG3wdAmqngN3iYYBWDHcCzWjlkxa19AgEZDmTBeRu2Mcw8cLDRwLFgOZfgGDG5AdXl4kHG/7XMsAMnF/m8MAxv8b'
        b'4xfvfc9YHDih8qXPhtXf8uVGymYpX/pnUdD4vsuGT9KL+jCv91/Qnvxe+PJ39s99cczgAcqGhD5X975z7uvGpIk7Jf95fubGhMrKSWGLLr517JlBKwL+8IHdHvfbuemr'
        b'zw+dca3i5Rc3912hvrr65Kd+E7Xm++uM62/N7Z3+zqjvv5p7ITT5vd9lvf3Ckj9qs5PWD777w5mG4TtnvKDkBTv36gBYJniF4dVg98VE8AS8SO1cHZY0BzrFEcF6bBV3'
        b'3D++Lp5qU5FoN9oaqSYXwJIxFAG0Bzl80E0WXTMJjmtTv96R8AC8jWoiiLtLDJvYCVJ0r3u0+c89fdhzO77ZouvkfCZefw8xZudpdB458VvK+jMKwkXxZ/N9VzXkYnOy'
        b'5O+hPv1csE4zZuhmXaSBb3uQe3WKrpd5wQOoAR0YgaojIzSwzsNT0Rce5OGZeXBTN97T07mQHrzHfS7kz9pq1PNSkLeL7+yXEb4DgP/YuoV/Ez8XT/lOUCDlO1rrHBJ7'
        b'njt1kMB31iqmEL4zLmLmjz7jFpiXNE9dNG3+EttI0TOj+9cX5Yzqu2ziwOWrE2w3J55YNHvOv5f9ve+PYa+MC1tbEql7RirJDfxV/7+xaIpsdOD46yM3j/5FaXHy+GEb'
        b'wntPCl+0ZtpVPj3geOGFgRnpvzNelgxedExrGJ+Q+4rXl/FTnsB39ub8RaDm71NIjCBYGu+rVcmmjhUSg6N7k/vEloZwWrtcN19YqaNvcsby5EjFnIYZ2qRfBhcLidJC'
        b'emW8dmu4Nu+8KUrYK4BuTSEsh3A0PbZJ3RwNE8xOY4x4lIjeT2aTT1D/ss0Xkc0sJ1dePNCr4vK7DyL9C7e9tsj7VgBrv9o6zld0fdBz907+jpnxxbdHX35n0uQx4w+v'
        b'sawrWdlk/beqcnfl3tRZ2fo38hf9vbXg++JJqn0fhyxZGmSYkj/w64rf5v79xvvBR9p+YMZo+u9tlykZulY1D15ek0jE5rPzKA9YwRomopudtMafFqPblRj1hg5iHNqZ'
        b'GDcAP7LoHigoM5QgZZQ8zc+7K3ruZ0CA3FRH6pFyrqMGyzx+H3oerUVXOIrRueETYJNAdfHJLqLT8rAZ7pV02wZI/ug5nYsxNVaJhHPy7UwTILTWzJay9DOn5/FnzsqQ'
        b'97NBA7NC/ixbypeS0/RFVcDKkmsezIVr5XZRE6cXNTOloiXANICcZZ/rbc4Tbk+i78jNSiLh7HrTfTu5wSeG1kHKX7Rz5jqcS9Qs3KIkppdRhOGWxKWSKsYuISfu6yX1'
        b'OL9dPBkU7TStp2VF5eSmHM78gFz9gOEXYThF9IR/UlbarawUl/21aSYtK9xbFNOtZL9HlWxgiryrxEJunIJZMa4tXLhhwHkn0Xw70HuFYvbivFrWW4OZscFQONdM9hQt'
        b'fCiyWbPU483E/MEY+gKZYfLCTDZpm4lsV0rM2QTzvAwmW77BTC6gIMpzu5icKK83tMsWmYzkA9VNhbIzBQTrOCmyo1p6wj/d+0QOejeTI0rbmVU/9aQpGbnwxTJK2IYb'
        b'xjm3gpIz8GXOuyiEy0/INSbezqtPgjw+yZz/pfR6E6kgJDBSok2JsEUEr6vi1WMjyDkANAhfMYBHbfAcPNktTMF9TjaRQHZgkeqZVEAusqITwJazztOE6ECaJ7o6QQ7S'
        b'tTzCcvSlXUu3FqTnFZiyJ3Guy005YqHYCLXDSrg1TLiJHpun2OagxxQSVQsM798LbhaVTA/pduWQO4RrNIVUz+QyZhkxM/ScnVwYxej5JkCuIMJwi4JAM2PHeh4RbiSF'
        b'Io7Y2QsaVcEOW0N3fX3KCt0Rrc0y5uUp2XbG1M7kPKprpEekZ7SLMznnaXZk2uhVDMI0LCudRmxw3B9yDzjuXQrtqhgMHxcyQFQCN/k8YUMw0+OG4Cdfh9jjKXPuqj22'
        b'aHbsd/tyZBF4H4DxMb3nLFdnDRUSwxY+j3EAKFr1khkLQ5cKiRcXkAh44B8zN2dyXmovYAxYO4Knl5IceIX/XLuCHvZ0pfx0+ZXG32we9HbL7ubK5vJB++/EnSm3MZm+'
        b's7w/nHlC8/bMjWGVoiSf0BrRqw7Fkf6q/q+Mkb1ap0wKmB5whA1/UTpq2OZlsvCrZRM2GwZlxnDZYWDi8dDC769i/ZQuwu6Gm2CDc/vwBtgghvtY9VB417WMcyAxMgG2'
        b'wVOuqwGd9wLuQfeEMLcj0kGoViVCOzTYHERbVQzOcYZF59FxWCHs69wID8MmeCaBWI6omgGlaK94PTs4uOSnb0PulV+gnzBOuGcjXW/MNlq7HnDrPBFKSsmZkHEYY37T'
        b'XUnN0zRX62qOFkzsUaxd67S9mFjH3v1W4g7Wp8C20fSs3zh4EZ5NJnfZprgGZjw8KV4Pd4sezTKIHiwwCiLfmgUiYzXtIp0l02jEiu4D4JK7QzqPjCTHsCbPmFWyiIBL'
        b'wyk4ei52NmrW0HV4VIE20vN74Bke+KDNLLoJj6Jjj4aFMGlyiwyVfIHk6iUCUakTPidk5rcAVcDnuOB63BleXjaTE8q0DhZG9BB6Zho6hM72i6RHmFN4XbCSQ9MOFgz4'
        b'SYNW4QLN/PajBswrY+xo4aownceQES1yPDw4IXEUOgRvxsa7o3n8BnGTCtC2/2K4OmB656kGC8MnSNOsLoNFyW5vMtqDgTxZGBtPtEoaXIrOcyPhHnijW+ia+xo8slVd'
        b'z2DGTvQmYA63ErbPlbNYlwClnHA5lp3FTJ4tktrZwlF2hlxURb0kIk370JiRo2JHjxk7bvyEGTNnzZ4zd15cfEJiUrImZf4zC1IXLlq8ZOmyNEEEEJkkaAoMVgqMxZhu'
        b'lXy7WFjLaBdl5ujMlnYxOeUidqwg/726dj92rDA9+ZzrRg5OcMkRIU4HIRBtg3cSR8FyuH1sR9yVXzA3sRc68OiZkjnxRe+6nQnPy+9drWOe9D89YkvsWGE2VntgCwEi'
        b'Bl5FVRiIO6hxbGLHVBzjYtD1idTNEpkOD0ZqkjPRKXrsGLnxBmKzvVWsfIJPn+3k0/8ZZxT2fG2HiMQaUcd3WR+94HVQryqih4H6LeGWw/JUeqwZrIU3ifUEwPKJ0AGW'
        b'L0VVxr7LvmMsRC1865/s59qlwgJR5aDatvKRm9v2jNwcf4AETHOVHFiuEn3+l1lKlsqY2agtjFw7vQXVRkuAVyyL9hbD5qJFVIIEzAgmh1xhNlkLGwdGo5pkzCp7R3No'
        b'F7ru3mz0COXBaClItxrzDRarLr+w6wGjrl9OKjZ/5J5frl1KS3S+bsLTDmPMf3K1QMvZe5QAlfKuDoVF8GwR7QnVUcioRsWjOjUAw5PMZtGGOFQ7t1ugW2dvJucMdPPw'
        b'ZToYtzfzZwWYEj3DrxsK9NJQBEBNobAxkVxAckJDzqHjgTiM9Y6G94RbnJ8JAiqinkQFiAqHLATCkYD1WF0ojx0F20bFgMHwaAKQaBi4H90UTiiEOwJi8Muro+AVfrAd'
        b'3gQSuIeBV02z6YECWbA1MExCjxSIAlHoGrxMG9LHhoIYTEkxpvXSxFkrBOXojeXhYD5JfGbK0leH+wEa9toPXlcEw7PkrD1y0p6/D8369kxy+h3Ouvj7KfkFU4Ty97Vk'
        b'zyFQxAQ93/eKZhCeVhpTOx/WGxPj4VmVGPCoJb8fAy/KkYOWiFs5Hc8rVty8fpkXo1kpVHMgcBpmFSAkxhgfGVxSKCS+Gid2Km5ebEPWUmAc97cUkeUPBGHe+GTO/LYE'
        b'foYsedSl2FtFV+729vmDJDLx3v17rfOfG/XgAxh0Zpc+TDJoSfh6+NXhfX/asuOvAzbu2ROc8f3b3u+Vj3lRvOtE5If/p70vAY+qvBq+26yZTBZCFpYQ9qzsyCL7EgiB'
        b'hE1ZRMYkdxJCJpNwZ8ISJyqCzgy7yCYiBUUUFARZRYT2XutS/bSr1inYVm0RtVWrVqW1/uec997JhASL/fp/T///+cjDnfve+953P+c957xnyZDSLhy75/Ibc8e8v/bk'
        b'kUtHl8X3nLzgpV95Dv34zqZe1alPzj56V89314wTp92o3f3u+hlj7xm2a0HRX372q8wFcd0CR678MmHEVxOT3n73h+eH3tr9yUd/V3TxgxXOe6Zk/2x60fDfd3h13mvn'
        b'lohPTaveNye4q8uSDxZe2TyoOvHtH6ZOeePxFaHd9QfeOuW68KOuI390/6U7h2/83PrhsjMXu+SvHO9OHpJjJkGjrK2aa6A6Naw9Q9KMigI6TPPPVTfnubRHprSkF2vn'
        b'MmHoDm2T+mheH+0Y/MUYYKuPMIXf4agdGNUIjh/GWUkfuFbdyPQYzk1X70OLCbSXmD0hxmLCW0yIRt2hPqk9WwyXNWRpLSzmR2tntNXXHzDu3yEcja+H3c3tAuQ09IZ+'
        b'/QktjWiNluIlnglJYUcTHXwnoFjNgsR3Q6RCgRLT6RmLzan8MYrAmEuRiL2yTqlwuyj4YzMe+1fCtgnKJY6LdT6Cdd0rGhrFd7X4+3srOaq2faT2dN7k/FxS8Ub0d6rf'
        b'wH4S1+Mm7RleUre6ZhHsF2j71XWzYLpDHNeV6zpGO1JhWC/ivxY6S4s4pKUw1mcYmDSMzxhCftQUkJT8gAn+S7B/m9K5FMiVBnkCwh6e9IP13TIkyqLx3SqRBXOGXKJS'
        b'HpL2wPOAuFeAknmmbFjSijGOBh5Foo5i8aYwtjcABaZRKMgWAYRjI/ESNdP2fkVheJ8QuZjgwVnlnjpgZZgyUVsBhBkRJUZMDfX1bkWZhFMvEV9tjkh+93I/kCZYhK+6'
        b'0R2x+dyo4+THyLjLqmX/IgWj/EZE2d06OjA08UO8/yC6bB2xbXlENJRURasuGpH4zG8lEd0Kkltq7dyt6pZibY22Vd2nhUsZp7NW37+7aLsl7bj6ROdWtGh0bHGSkRYl'
        b'opkDojmdJHkYZRsmfQ+ONmxWsoijTXI+QSmHiRZkCXKIARHjk2MQ1iYRJ5RKmA9PKUo4vofc4ixONumCiivZIxaMXl7r6ZM3mujKam/VyFu69b41+5aFcM3Lwfs+uaMX'
        b'jB5FRPplbCwTeL3AEdOILE7E7HOXKRWLIqYqpa6hPmJCaRP8eOqWweS8ROAZEaGWiKUelcMUb8QEgwkfWI1Kv4vmT0TvjvC1y8h8VDROMkTJcHdA4VQZ3tAPZrvUApeO'
        b'bhPVp9BLDaDk3erDpYwgRkKk2MINzTGr233aQy0IkBYnnVtoOoDgF1I4ZAAY36L40dBG6YHXPfxeztcnIMjAIAQ4F5rgCMoovNKbCQFgKVzwfwJ3a3IT8UJQmpgGE8Nz'
        b'SyZTbk809waW29shwCsb6F3o6nf6MYlUEuHtV4SsLJoNGD5asZ8TIPjLqj0AHJLb466FWXAvdXu+A/4ijnrF7Ue7UBzkHzWPrUOPg5zIMxcReGiVwpNT5XbdB+VljxWn'
        b'FOQQO6quY2PMc13Vh03ZfBsH+FGbbAwT3nyAD3iJmy+6JYpQyWEUyi3iYvNiy3wrPMPIlPjM4rYstskWI4WRKwGnoUW2db5d7qZzBHGyY7VtfpzcXU/Hy05IO/TwDFLQ'
        b'WmmSE+RE+Ca+xbMkORmeOaNPJLmdnAJPElrkai+nwrNEssTm5ifJPYJiJU+21rb5yXJPSmXKXSDVTu4F35ihBVlyV0inUDCI9sSJ9I7ETYRJcXv944DJa7HsDNHjLAPD'
        b'NkvzKbAyJ0vGPbHNwHnyTTT5l7+Ff1f44UCiT+bI8I80sGZEZzkGlFwEmhTV3VdfVuF+I8q3CY2dYprW5+qMbTKO1FY8dEbGHhaqIWbgS2CpmXlEsv6yqrZMzyK2ek9Z'
        b'tdcFryMxTWgf24RojlZ1C0bdyRyzeatzGqCo139AiJhcuBEQSLRp/IYA8/tmtrUxMbZu/LTV9ESrddD0ILTLhs3fAWDJMKybiW+7pj8297IVuxOVOHui007onmdSZjrY'
        b'mIxHOizIcUCUhRpBGSSjaEIYgQGMAXpqzL5U2RQQ8RcQPo9HNvDEwr5K5Yy8Mo/xvnUhmrXkCt83wudeEfr0xSnD1iKkKhJOHn/7FdPtuU09fbjTsjDxduApFb9vWTXs'
        b'orjrGvZR5AkexybC11+LLXUBnoGN2E1O5j8QDS0v3Q4Lo+F0EJL5xowWyzD2m5IWzjfF2JHLNBYhjZyfnSsIFNkcgMYwiRSVFOyXydcAVAMSDF7Z0FfEDkTs0eV+jTMH'
        b'JRW+/6tBq2DTWy4bLPG/0cjVzY1U2mNLLVhgmcejpPHXJJ8y4NWVFk1qd3WToIQ2cQ21CkNRhGAphSSkNkK0sBfDElwvUBt5o40Ytj1gSDgP8BGT11dbVg/N7RhtrplF'
        b'EdBjUUYsbtaO6zOP7gQl/EPUDVk5Om5K5BuTY/vCir/2APdjXRGiXRGiXRFiu4LDDZ0RDPljB5620JiOVKOjI3+OvjjG4KUzf72G3hj6XZJa9CT5qp6w8ltNSlQshZxR'
        b'CFoaEqEnuQZOULKQEmFR15ugN0gOIiT7BX0piVHIFgGyxzDaQFKSsWN4NMl6F+dyAUlV7XfXulzGbjGV++deIZUsNHuQjMMoIreQ6GpMawGyzYVfe6YWxi66Pt/VPzZX'
        b'3tzovBbq8wpbIc2rqM+rZOTVcbJUonThDWq1A5s8GgisO2auYTR8RoONCY/6nby+Ce8G5SRJ+l5ojItTsJNFf8uxiVb1T8KJGrLx2ayatrZQq8tVXlfncbk6Ss07aErL'
        b'6lgGItZnt5gNg+lA+QNxtCGAlABXibQuj9TsLthntgsbeP24rxCG5msuSi2uAMRc7fVHEpAul90VnjKml4qm7/46dtps7A34mdITx5tOuK+SIZsVN8YO6tK8rBy88K0E'
        b'/1tCDMtW2GYnaEllRTsh07KRhfUScUQ804Ng0bhKIlJF/0FetN9jgYgiNvfyCk+Dr3qpOxKP+5oLOEys1fcZNjILOuj1jezWjU5zAbP1IrwMu5IHtgmji7nYuzy8/LV1'
        b'F5VseNE9Fh8I35qFlhsHtqkFNsChiHIhr8GlmsPDCeT+gRpYyDpGG4kE6x/49714js5ncAuEJlOTOWAKCDVm4OwRVkwZGLxI8M1k91U8/o7Q3wDOMCNqX+IImNlzuOMW'
        b'S6jOATVlQnmWJivUbA5YoDZLwIpDG7CkcZBzKeS0NNkCNuVkgPc9HkBlEBu8F0dwXilgQ5rFpwYEnypT6xfDt9W8zr+wM3IE0Sum7khv5dgiDoANYCSrPTJMd8Tir3PJ'
        b'1RV+0pKg/QF2GD+srfKIDTMiIPmIzmTcj5UnWQ/tPfaKOq+PWQBGeBnPVqDQCF+hWLAYoUJmbuWISP6Au+bm2g9yZ+PUUfg+ih5gJ9e3LBKAnU8mKDfrYfwk8uTRcgPW'
        b'O0EuGZAuJljMEQoLc/jCnNSrtY+pN2eM3ih8tHN2njHayD8zCgFpEdr9aWho1yEMTehI6Y6X3ry+/KgjMeG2rlvyFxOHC9vyC9ygUc5hFa2SwNsl9Ctml4D9Fp2ORClR'
        b'SjGnmJMtKXar5JScJnaEualskbZH2+XDUJTrp2nr85ZMyS8xcRljpELtZMnsHJ487ql7xxTkTfFqP4iaVGkUwhI/yDFzA2TzbO0ebSPkpjAy4yqLobyETJaB5+LuELQn'
        b'tB3ajlbqg4gxSFfKGcUQAX5DlFPhI3G1ZTVunVZRurSBoyz6fE5qRrTsvHFlvXoGu1WtHTTaYVd3C9raAdqDrVhgA3P5ZnMxLHAiRQ1ETXZgeIG1lIB55ZnrsfksSr1Q'
        b'KerMrhkdkEEei+yQ4+HXKjvlhNXowIz1JinimNBQW7tCb27b9HL0yJNxMLD38jFsJt/MZjJpA1xFkjxIsnHkqQjRfVXkdWYBNkqELOJA2dL9gEbOhdS7N0pJEfSZ2bOr'
        b'2SS0gihtRpNmPhP+N7aP7dH380bD3KAoI/hrbKA2IFRYU26KTizfmNqiwmiWa9Nq+skpUSGE2/Qg4AZpNa2NFcVIMERmLtfcmMrTr+ptNNO1qx9FUynzwBI6UHONyEZA'
        b'90qPEA0E8uWrKFrdHgGlgMoAnMiYBldF1a66MDqYJpJGjeilrvx3nskTzrmlmfqxkjDOSaK4tvpz3eQPHUEPiNbV1gxaXC6P2+tyyTFDmHJVlZTh2iIE7IyfqzKUNwgh'
        b'SLi7XIvmwnfQkZgaWy1RynEdPUROqvCavSMUvvg76mHEHTbZfvU2QtFWR+HsjYluC2PxMj66N7Bz32tP642QaaoxrVbRbraKDjHRBohfZM7JTmhPFfhyEtXziLDVQ/4o'
        b'eue5TPUZSduube9+bSSIvsgMJLhFXCwuluab3EwJDaV8kltabAHCTU8F+UqeEKR1vpXJ5QApMiRpI/manRCgNZJcWr7YXeEnH3z6SH1P8VEVwe81cAZhNX90TsTGtNb1'
        b'fT/hEe5BStx3iY5WNO86142EVhtISBnNtyZIcU00xSyszDY68V24x2rUimutMdnP6SwYEaRzoFcSsKQ1duUGpkFMeEgM0LnEKsHMzWM5TJBD0XWM+T1mYgBlyGVpZgL3'
        b'8iy30TOWilHsaGbxgKRpbyz1iL0ImIXlTM+WsBmCQsQ5lojHBr+ugdvMFl8PirtLikqsBFKcTSEkl/odw6czlXFXQ+eEFlQdI/eGtgTW64qMiuV4oyAaQ4s5xAY8VatS'
        b't6ph7ViptmbKtD6ob7d26rQlAKZLkchikDpOfczSXQ1qD10bUjvEQCoRJ3SaCASLbjEb6Wj038BN49Fh6NS6upqG+hbHmSZ9/bSLAp++b4VgPvU5BZzfOYqeTIyYl/wr'
        b'6t3Kbry1RUV0be6rZg/VukGKysOsfGO372hfH/ZBG3aAU6LgeBX0oPOHtQb0ADJEVdrbB8yJHed92h71iWaEuETbUJTfRzuJurraxj4FQDluXWLXdmp7tWCrs6eojATL'
        b'hc2cI6lHJwIxnvGAATzMg8FT8kPIBXIhM7K3IY7uTYa888o348k/ChouVzT4/HW11Y1uOcsDHG0WncUrWdluv+J2o7vVuuYlnHNtV6+UfTi6liAfM2j5XF3lrVOgjmbR'
        b'aVaZV85CTho9YZTJcjULgZWVq3NC2Tm5WYz3bmkNHdOEllWUeTx1y3zk0kYpw/BV6PXVW2B4eMnSSXdfy+KA1aLDSXHutKkARMiYR+Ji6iC5xPcN2TYV5n67ZKjeWZkb'
        b'MTr8RUFKJ+2oGlTXakfUB9T92gnAbNpRTntaW6eeI6ZlnnYul4LT79NC2hHMIHr5GQCiK1tBXzTc+MIY6JObT67MlSY6M7PNF0lBygz7IZ6XWWGvlOiETJQtshWZCNkm'
        b'24FJMMeck1nnW2jXtBLIOSMOHTCmASOklBS28psSXZN7ONSVqoa1JvO7xCYpKsPrAZwCX41KlFwVT2cVyFsISigqtxsVEPQ3QIZmcMBfSCgnCIg+L95RWsqA0lEyAX1h'
        b'UkAhIExARQMTfGcy8pCUQjEkuouFSni+geeNDdWMQvQiBF+S8g3DC9GRzc/YoWnE7iIhtgtF7LR7IN2Uo3uwoYzpJCKsV9yV1ctdqJlJthoRweu7fqefhyXD+ggQNPx9'
        b'YzbhwkHX2xK54EYtgkQ92GD0DIzmopnhiUUTFi5GLeQgTgnumLAcqiQcMBQS8UDSou4qDN69TESEugC+G0hsJJHAp5NfCEioL8AOWmXLehzqmw0B0h5JtsKOvJy+wEVE'
        b'EwIIybwKJppKmALP7YC/N2Ee9kZ/TmgJ7X1WCezJkk4B5tgjriRimoWHSBFxoleOSCUYttx0c5mnofUZY5RmYmeMKN6ShRpzrKkIQPksnKebonsG35bmLLm6fB2VF8jj'
        b'aEHLMa6o8wJa8RN28sXqmzA/pFAkCYSbxcl9iONFMSChI1025aOQgExahbQFIBfavkSfe0nEVKfIbgXFnb4Gj59YjNpmGdR36T84W7ZPkwzDUt5wHGsX7LwgoNm9+R9O'
        b'0S50Qms2ewrf2PE7+tnqGDIqSUWjpSoEPVw9NzSJQH2R4hBZi+Xj+iLRvLiXzbY1IMIublGsqIeCT+mZoUSMLA5KW4EmdsN8W12VHtQB8dKYGfLTuTiy8/Fyyz+hxBbC'
        b'+3eamU3mNjeZtMGuhhy9ojY3WFpVIS72lB31vwPYj3Q85SKxCMDUXtQCh3fsyAHe+ulOhLvJfkBGASEVtuW7eVLTAKS1lydaFyAF4EJGsac30XiCefAQVjaxO3gCY5rK'
        b'6B5zCTt0FVwuWmNXUm/y1njrlnmbd9asbj193a6Yb+/pwzNZs1KAA5ZES4/hMaWU+DxOJ2sNoQtbZa25i0i8y4tqTegzGwr4EIc1NWZhJeonGam8WUjkGzu0HN7YT1th'
        b'JxxjkrndxsWeedK6QeIFyRiB3VUDK8L0lnTLP8Q++AXZIwbMAYnQfa5fYodci2ErqIRSdguI9A2m3UwuiGh5KAvwQlBIBzzAs6P7eSDELTFCKKshZlb6Y9LGBMvQlxig'
        b'bFsmLEP+r5uZARgjESW/bLRaoW+9arEEwMDWJpu+INpw6oLckvy/LgKlmSUoga8PGmcpVim1fWIX4NmdzBzuvPaceo9PW1+thXTKVDs6TVuHHqsy0yT12V7aI216NMd/'
        b'FEk3SogkEENuECAs1IBBfuCbq0kPZBt0woMUc1B2ydO6T4xYp9ZV1BRWe9wlCvIELYiPFuoRUzgmv2V8pi/FL8g8wR7jpgV6R0egqSi2hFUFVxMJL80kyLSgCZ/Lqgsy'
        b'pZIr7TBOcJZc59aDBCBFecXS09cHdf5wvkgtwFztw3wEWBFLWbkPlREiVtILlKuViAVV5+sa/BGTq5Zi4VD44YjFhTmAno7RkYhImEOpbYMpx7UQZ4ouKwdRCMlEJZj5'
        b'xiRjkNoWgSJesxvjhBE8mKIoyv7QOLExMYTwBngIsfMczrtAt/Ft5AFD8VwjEGeLTYDFRWXE3fiVWZk6B3jth3uRrJCVxddIym1+iyzgmMMzq6yXNphDPIcGF/O4JU7g'
        b'ziU24rMgpaurmUouJxFSq6hr8Mg02GUVFKIgCwfp0s4H8N+B0bNzbMDtwXDSEEVMtTUwwGiJDANfOovY9ojJrSiAfOrxoWNmgxez6298Hre7Xkd7EQvsN1RU9TVhOSJh'
        b'7e1NhikD74RdNJFAWSCDWJwFtNVujI+OP35xbTOafI6JlJReMq1KWJO8MfJKL5gFyZgFfWRwezRRZ9gCMVX7ol02KbV4T3KoqxndBi82pJcpRl6OkVwaE6INZTn+GVHF'
        b'iEU5Rl5+57Xk5ejlyA3ILN/ULDpKjFmX9PLaQ5MbUx8uTF1ALTABNZ0zwNDo5td0NCMpAWyL1xgcpS7atKstkVwuwLkodu1rih4kW4m0hslLjmmknq2VdjP+n8PphDrN'
        b'YKohFMThYaqdeMzKNyt9wUqro3mq8NQBFYgDZ+i+SC738oo2pMeAYgB2b4idNvvV8M3yoCQE8eE1dg0aGZqqu/CyEi+rr0euWwWZLCadhbVKTrszyYGyXQsdaXXXnlPI'
        b'PdNO9dlSbcNSPbh4/GLR3s/WanOw6L9knhuVEaHWuQT8Z1ROhLqd8yU5Mcii64hBc9BaaSb5rQ02iSTGsVJ8HDzYssGGwTy34fFWS141OSIVTp9Q2Ar5RQkONBnyczqp'
        b'QIoAyBkaUwe/0K6QsFhCy21Km2TBb2YpfZMwTIauxE1fgZUNyFra03clHhJ6lHFIGuJG5roL3Y7Wl1W5Iw6f2++qV+rkhgog9h34tevmiTNnFZWWROLwHbmsBVQV53Lp'
        b'gbhdLqah7sJALgbJFnUI8F0ziXWPbV7uyaSlCyggHqttm3O8liRaVze5kjQLWpJVW+Yl953oigYxwvrmhc2cylxNR2LPon2YHEUPQmMyNaXF65IWDUKRYNSBTChm7hDw'
        b'0KN5QGBSr8WCsjAE7CreoSo7sJsisKiw2a9iiu903yQCES+mcahhTU9h+99jZgogRHbyyt0hICBl0yphYyIQntIeS0AwtrEZ3ExurqEXZmZ2qZ8hmNp79pw1cfrYrM+w'
        b'u0wHcrnirrQTpR4RlpXryyFiBjKgvsFPIxYxyQ219T5mBYzKknQ4GjEtQ8UFXbTJ0BqNKX0iVC66fsNv5X48ojEZCttk2G1GzSPauJJJLgVMYBzNAWtYxDbZ7Vnq9ldX'
        b'lCl4cMhUPhF4KgyJE/5LiJ2VxTxjk/aiThZP84IEOmlvw5iLOlTRGNM9MEVAtIv4JsT7TcAemlI41GNFxxws3ZGlrbK5ySZbmuxMeNAUB/MdR/quf2lCfRRHBtcUH7Ap'
        b'zxv5AvEwmyiW2CHbmuK9mZS2Q/qkHAdvjbqtWPeS+pZtCTgCQIKmczWccgHLlh1pXAZX/zaU5Aw4N/HKCDk+4Kyx4F3AyeqB+8yAA65YtkXHIFCm7AxYsExZbLJBK5ys'
        b'FfQlvEc9c1Ynvke9F9kSMAXiA3YgB2yL8Rq32CEnrTdDeXalHnNBa81EECSXXEYLk8s4B7Mv44xfCqa+9dqXs74YXUgijyviyJEjaeIioguwBz+bMYx8VoQfF7GMr2tQ'
        b'qgH58EU5QsTkdS9zLWc/K3LimYGAnXR5PdVet48hpdoypara64u0w0RZg7+OkJmrHHBVTcSKDyvrvEDeKnUNXpkdm4RwtUoVbo8nIs2dXueLSFMnFs6OSPPovmTi3Nk5'
        b'CWyFkx6ARAVIZI9j8vlXAHkchw1wLXJXVy2Collr7JjB5YHmuPV7YGuhCpPihlZEzOVMiGLzNtS66AumcyzhPTx1L/fT438a3jqOaZKShvh8BKASAiCrHgbTSTSgRNIF'
        b'xgpLuqSO7NLQZYrQiSR2ZvqCAR2Cm5kzf4v2arCjJxLYxVTUpsCF9iyFawlhdBTWiQ7skdGZIgthDo2s/CIxUrifWlE4s0r3QZKBtim8bA7wqUxvUpItiNP8Jl1Cao6y'
        b'zCLJSa200mxXOowrU9B8O2tgXeUwJrMnLxK+hlolHmb4St71GLcX9Mnq0TevZyuSKqq/huiJDMacTdALJgzQTcWqDKHdGK7ZWOyGNtgjJKxDplgrsS40wNj8gcPaMhK7'
        b'jFZAV6Tcnr5cgpsS4KXf53TZHJoeyaTHHhGhtxEnrfJq4NUr6jx1io7NWeEGA0cnds07c0vr6N9FW6rBp3ebDBEVOpciA0Y8KdBxsV4sUbjb6XiyBSq+BsW3kddRvvIs'
        b'r1cTIyf4nl6qmiUG90A5I01RiUGixSqlO1OyWWzwh+Sxvjh1n/pY/RIRXV3yXbU12hbU3ouSAKTWJpaUoP08eUd5UA1rq/NKpqlH1QMtbfvn5qDOm9iA+E07oB1Xt8zi'
        b'tHvUU2T7qG7PxDLIlPhLJ/OF1sl2W/72wGAY38LqPhV38L4HgNYTKsdPm/31nHZVKQ+9vFp++ujHt/zQdMKbP3bMfaHwhE2L5jpOPjbyovfFnW/Mv2XxoYeOn3h52Md/'
        b'sPzD8vfS2y+9e2NtQvCVV5u+/FPdXU+8uSq9fPikz49PWPdh0tHiD59fvS1cVHDfN4lNF3vtP1449cMR/R8ZEppXkOw7M+6jN3KPThoSeu7MmI9+0bn8/NvdnO+nLpn+'
        b'g6Tg5x2WzH0z3P3KpqEHH3y+/61x5a+/OHzFA/f3DnR5ccJvPl73acHrp4qmnvhmf7vhOwrP/en4hf2vXMp4deelue9PH9Jr1sqgb+hv/3qLt2rAO0JaWv3PzpZe7jH4'
        b's6dzTmRtGLZgwEeJN6W9/PEvPhtweMKCX8Td+vcS91OfF4+9ed/kH2ze8mju4AOvzNik3bSg5rH3L5a6s0fOvvjI/vwvslZ+eLrMM3JvuzPHJ/b3dvy2f+GOzVVjOwzp'
        b'38X9cO7tHw26ULL/ncnjBjz5SFbNukHd7n/69XO/mPvD8t+8+HDl/IW9y2aPevYvR1YLX9+9u/vHHy7svvSDsnnfJPR/874e7255b6Xnle5vxW0+fU/7EoUrqerx+aAn'
        b'Bn8261LdvJq+5bv+/EE42OubmZ//fXKqe8y9v24IN2zJqNreULr7i9c+sBy59zczgrtmj/g8d8a5zz5/RSlf9t7hqdNXvPSTj297qP3hU+UfDWh/uT6tY62l44ufbpvU'
        b'J1we/NugWy5vGzXviC/T/atnL8wwf3mk+rFBZQ3D/vj+sYOd34qfeXrjzx/Y/5b7j51rD9325U1VH7tHHOnfuL5p7sMPXhz346eb7i14edBbwV+f/Cj7qW5nHu/2yEdH'
        b'tklLP3npQqH6/lOfHF4648QHZdqtg7f/4ff9d8+9I/LJ9gOHyl5XLt77rHzib0OPBPq8syT02M9GDiz9+ftrPj/07ktL3//snW9vu6n4yS8qAsl/2vNAty8fe+bDifOu'
        b'fDnz1Hs5Qz7JGTVw5/HwN2kFNw277Y3XP73nouuF1zyzMu//Ntn11mLz+hdvb1w38M03f/jAuYGZZy4smzpi3j8+ftAaCKy661mn/5mfuZd++GnOyktf/fX5P736/qvV'
        b'mz8+17h8yTt31F/MvuS4seZ3N34W/8LU2UMO7r4psHH7ui9+fmF9TUH1gZ/+RVz4s79MyVu/pfHQ0D9VV5QOfGPj8mm/qflj0aT2g459+8RtN1eV3l928g87LsyouvPY'
        b'P8Yunf77Q6+9lP/xe73/7qnaHOdr5F/8sLD6zPoH1+ZOcnFbz/8ufuBzP3tw/dQt4ZuePzTgytvOeZeeWl784988Lr7w4ck3+iz8+uyTT7/yt10XTs5e8dz533fe+rH/'
        b'xH0njn712zmf/f3BoO93+yLfctVfnPzmRxdz4ilGTaq6Sj1Ax5wbtXDp1KICdY260cK111Zq4UWidlw7ox0iN9RLUrTNmK9Xh1I6IFc3YL4k9ayo3r9QXUd+MNpJ2glt'
        b'7bTazIIidV3fyflamOOS1XtF9XiO9gyZv4s91D3Iparb1NN5JQW5GBLrhKBu01ap+ynCVFM3bYtPPTRH3T25pFUY8OfUYxSYRzsrT1JPqYfbUlK1ZFCWIu18Ah3u7lE3'
        b'aCdsaNuNQWjV86JLfbTcPxCydNbu1s7mlah3TShQw6XRovCedZD5H2M6AIHhdslW7kfHbmoofUFMzUXTivO19TnNagO91RPGV3cW27nyMX7c2/oP7tWGcod6THuipXbH'
        b'dvWIfwjWcjeM0TZfHwzxQ4GUNjZ8h4rCMm2nTT1ZqD5GscvmqUe0tdBEdX9Wm6LjnCQW1flZ9Qda0BcXp52N7hjq5ilAC36v3ek7LzlD/o2F/f9yyenG6If/Jy6GMMxT'
        b'Vya7XCwmJhKPZWbeLJj57/H3R6mz0+ZETXSR/U+2AXFuEfiUZLhvJ/DZ0wW+Qyoeu3fLNwu9xqVnOE3pYyRB4NP5GzwC36sB8lklOpjvkYjXLLp26oLXZBNdobx0G94l'
        b'inhNMV1977AaT7D+bp0wleqg9066Qpm96hzIRHwrQS5scXpXgc+EnOkWB++gsjKdVvrtdQteOwzCa26J8nz05C74v6v/GpdmPgFH6zbOoL4fXh7rmIN09tf1r23enNQw'
        b'bDmjtQOcM0Ps3Lm4erD0lujrBisyefgXBZtfnvmbMYn3Vh2f+/an5zo6XqgcXNlOfva9DOXlYb8ytZ93JnHDDcEdB++8sm3Skd9mBUdMycw+ZHv04NfnLt98qnH/59Pu'
        b'2/De73+6et+bO/uu3nAk33+PaW/vTvamslk7kt7e+cmzyW9M/WrHX7IObfz5T5L/PGPcV7+bOeatN/Mv5by40pb97bwZew8/H+w198OtA340s+BCl/MFv+o4suz0lg2V'
        b'p196tH/u/mG5O2/7/chv9h78NNnSd82UfeXbL1Vmrpj9QW5u312PnX991J+e/KK09tgDW2/4+tEN7xUH5IK8k91f/fSBi5fcoxNTT3etuS/BXfDpQ/+1tef2Y706P1N1'
        b'qNsNW9/eenrnL+fWuB9pCP95Xk2o8y01ax6aXxP+0y01r4Q7H9z59f7xb9886eLEe39TXHXo1/2dvzqz5tYbl20szf9boODJF1fJL30hb1/7cmapv/EvhSOmFC6Y9tdn'
        b'Nnf6ZP0/7uxYce7pEe9t+8PqSdtmjTo14p3Df+j/5T3/9VWPYe7fvnHy+dd/ffuHvnOKe+GQnS+/l1GTVj7v5RPvrlBe/sm5N8NPba55e5p3+bYLyqQ/l6fe88tbT5/f'
        b'9dhT+5ZX3n7x0NlHTz3z2ynrP3loyamdL1aeXVH63KWEWyYdfOHBjb/cvvyDz95v5xo3VluZ9+0mS5cM6aVuwRH27IfXdZ49fWJ8w6CfToir9f90YkKTo9/zff7aTx3l'
        b'7PdC11473rG+OPRHOa/Vb8jo0+/Fnofr13e80O35i9rI+EVf7bz16+I7C2ad+2rfuccvvDt69V/ffHSXkDOSqIv56l0ufT2t09bm04Iq17Zyzplif/WMtsvfFRfduWX9'
        b'MBMjA4AAWhlL69yuHWCOfLYAS7QqJkInFPbAMF49qm271Y88k/r0IHVfnno4H/hfbaUyh78tcAuRXEnqvdqGvOKCXPRXpW1UV46jGH3rirW1Fq7rLFNytbaHtvEbF9/W'
        b'7FUdiJUjRoRl5lVdfTCdWqJtSo8rhnzauhzMmWdWnxnOJQwRa2q0h5hLoSe0zRTMerK2Hho699bJvHrMot1HzdR2dF1SrG3IFjjBG9C286OqtEdYTJEH1MPq4Tz01l5q'
        b'4sxj1JC6WXCq+4eSM2jtsG00xVHILuA58/LMDKH/Ldo28pC0UN2t3l0MHTuOGXKKgOqwqucFNei/kUVqOj56MFCJ+cAcBrRdy/jRwISeozcz1X3tobFr8JV6bMxt/Gzt'
        b'8Ezm4hPow8Li/KiLL2d7wa6eUXdRW2ZqR7SnyOMifNc0TDvMF2oPuKl3vXs6tbWlfXgob029dpKfxKvPkM/6Ra4uUFMICLfcydo2GAAkypAK6zlIC3Y3TZiknqbFoN2n'
        b'PbQiDijV4jTt0QJ7trZGfQrjqnZQn5PUnRnqI7Su1DXak+pZ8pwGQ6IezEG3acVAkaYtkgYsVDdQM3O03Z1gEqZgY3ZoBwbzhTCkW6mZo1aoT+Zpob4Y6vpx7a4F/Jyh'
        b'o9gw39ddfVBbW4QTJ9ypnruTH6M9lMfiwhxV70LvNRu1vQpgR5gnYt1XCtqj2iGNeZtKU9cuUdeWlhYU5U1Rt2pbKM5s8o2i+oTHRWSyurV0TjGLcltagiXAMtrIOe8Q'
        b'J2i71BAL4X1Y25YM7TZz/O3a8Vmc9sh49W6iH9X1d2qPRaPXum8t4dUjK2AqcRFAmU8v09aqB5irEUk7mFnOq+fU89p+KtWqhdUHiwtypsCn5lmDhwup2kGREfebxqtH'
        b'i3PVH6iP4JouwvUTp+4QtMdhSa1iEHoMeJbtMLE6OZ07hNxsJqurRO0uGK8nyBNXY+8xxUX5RQWsgdCNc5xTWyOWyOVszNWtw4opCq7UMV7i1R/M1bawMTnWeyzr1TQY'
        b'93nquZwiKFu7XwQM8ewE6l2ldn58XpF6KDun75R8TttdwCVoj4jqXdrjPdjIhPtOKc6bXATQpu3Tnu7Aq3u1e7TdLADvmak3aWsR+Dci1viBtn4Grz6rnhapVXPUu8fk'
        b'TTFxvHZSfbIYvY0d4KlKc8FwWOK9U3GJoV9RGJSAoO3SDgG/gBAyUFtzI8AbRfqUtLPq9kRe3amdstEyUjc0xBV31c4DlzR4IM9ZtM2CuWgOlcs71GeKB+huQrWD2n2G'
        b'q9AKH41GoXpQPYUZ0Fuaukld3eyn86C2k9g+m3Z+XDE5ldYBdCpAolPdI44foK2mQmYthe6vnXxjdoxTVN2B63MAaAhCwmhtTR5MuOE4dZC6t9l3qvbgUj+KzRck84hT'
        b'CgBUcmGGAGQBsU1TVy+YSqOyrrhAPShx09QnLNrKCmgdFqydG9whDnnRenU35IHPi3FJpWi7RG2/9sDtNApzteMc8aWrtVN5fSZPA4wRpz0saKfii6mL9eppYNUAvo8n'
        b'ltC2gKB2TNCOwYicpS6Oy1RP5Wkbpmobi/Nz1E3ayQKYxXaZona/tk07y5btEfXw9GIERuhnuCh/Sl/yWJlv157jTNoDY+P8PWn70U4DZLNdan2pdp96Ngc5xfW4B6X2'
        b'lETYj85So5bYtO3oU1p9SD1dWkpbiAWa9TSAynAXw14rNVgDxVPysWHPNC0lCR/wnhYuQzsmzevpYRC3Xz3pgnZpRwELlGoPeTG8T5IGu93eWu0cw78b9d2O7VKSxVnA'
        b'q4cGpdGGpj6qnu6MDe5bXCCr9xv72lpscMcekrqqEIAewWKo9qx2X3HRtNxpFs4sDdH2C1Ztj7aXUFWm+qQdvQ/31DaUYn8LYIS1R2GFpGqb/tkpm+Fic8h/ALv0H3eJ'
        b'nj4T63YQLlycIFj5q//sQqJJohOUdGB8BN7M/gsSj7mdLI9+rsIYOjtTORTs+h2UAKS7lcpOIcPr5j8HlYx58JjTQSbYVjr6dAhmcfmdXOu/YWaeydJ1p6c2csjQUO9y'
        b'NXsLNA4kfszH9hRvGEvxpSOGpaB3LdQi4jl048mUEnzPw7Wck/nF8Be+OXQz6quFe8OvAL8C/Irwmwq/EvzeFLq5moNfe+hmNEcMd8H8izEnH+SDNxsadk0catd5xFop'
        b'nFBrauJrzU1CraUJDxstss1jrbU1SXRv99hr45pMdB/ncdTGN5np3uFx1iY0WfAo058IpbeH3yT4bQe/yfCbCb/t4BftpM3w2zXAhRLgNyFA7ojCcQF0ssuHEyFfCvwm'
        b'w297+HXCbyr89kTNb/i1BKRwN9kSTpPFcLocH86QneGOckK4k5wY7iwnNVnl5Cab3C7cISDKXCgDtcvD3eWUcI7cPtxHTg2XymnhaXJ6eLqcEZ4kdwgXyR3DuXKncL7c'
        b'OZwnZ4az5S7hQjkrPEDuGh4udwuPkruHR8s9wkPlnuFBcq/wYLl3eKScHR4j54RvkHPDI+S88BA5P3yjXBAeJvcJD5T7hvvL/cLFcv9wX3lAeIo8MDxLHhSeLA8OT5Rv'
        b'CI+Vh4QL5KHhGfKw8Ex5eLgkZF/FhXvIN4bH+dPgLkkeEZ4qjwyPl0eFZ8ujw/1kPjwhYIE3WSEhYA3YKnGUUoLOYFqwS3BapSSPkcfC/NkD9rCDFGGaPdo6gwnBlGAq'
        b'5EwPZgQ7BDsGM+GbrsHewT7BvsF+wbHBicHC4OTglGBxcFZwdvAmWA9d5XHR8qwhZ8gaylklhG1BFhqeleugkhODScHkYHu99M5Qdrdgz2CvYE4wN5gfHBAcGBwUHBy8'
        b'ITgkODQ4LDg8eGNwRHBkcFRwdHBMcFxwAtRcFJwaLIU6+8jjo3WaoE4T1WmG+lhNWH6vYB58MSlYVBknT4jmjg+KFGkgHvIlB9vprckK9oCW9IaWjIcaSoLTgcOeaHzT'
        b'FBdyBuKohl70bRzUEk/jmQ4j1Am+7k7fZ8P3ecGCYH9obyGVMyM4szJDLozWLkJbRSpJusOO89jkCPUMOUK5IUfAESpaJaxCZQV8kk9P8tmTOxyBOFIGmsRCGZD1ADMB'
        b'QCxxbV03pBKYxVaIq7EpHfzolIRbzBvK4rp3lyvte/qyc7KqmfppWVZ5Q7XHX+3NEZQViH3oFBBZi2u61HJVekmKhiptD5t022KOjqOVFw27lxwJEF2V21+poK2F1b28'
        b'ghRxyP4dD9nrKiMOQxmJlJB4dI5SC5gR7uzo4Lu2XnH7fJASPXVVaCCN2mrK61D2ZezyZfJuju26vBwvqKF3mTN0r+tkN+BX8lGBGusRsb6uPmKH0mV3ZRnaQlgrXez0'
        b'lhljNvuwiOLkiLmSyonEVdS5ypQqigOK4UtdNcvqvJ4V0Ud2eORlhUUccO/zl+leQK2QqvSUVfkiFrijwmx04/X5ffSW9OyphqVlSnMCdXkxRd/RjZOeKj5SofDWUTke'
        b'mMCycvaB4nYvRU/umEANCUqYKjzuMiVi9pTBBPePiOXVVaSjjv5yWJiPiB1DRLN7pjT0kj7JfqWswo2hJF0uyF7uYhNpgTtUeYhILsVdGXG65GpfWbnH7aooq1jE1I9h'
        b'YcjMoRuSgVeE7JxWQf3wwBkJKeY8S2CRhFAFC11PobNYVCiYgEf3AlnhCquEJn5JhwAfNZXm2tBS+6eupHBx/j2qu6ZTAw62aFu0EZXUzEYbz8LbkAUwnQMAKwNbEuAB'
        b'BwmVaJmRKVPsHrLXEENZpDgmBaSQvcaq3B1yNJkCQiiuRlAmw73Zm00pTlkYcsRxTaYQxxTNQvZQMrxxQt8daTgW5pAF0p1XCQFzqD3UKHj3BQRlMzzLDKVWopOdbagw'
        b'BvW0g3oOU+50+LoTluZdDs+7hJIo3x9DSYB3LGTQlt5khZyWUArklGCvgLFehXYzzwck2EF4Ks9cY92EOsNm+MpG5XaEXIZTHjuUoH8ZsMGdHe8ozhGkZ3Gs/yGeyrgD'
        b'vk0IxccZJnViKJHexqejA2Fg+mQuEIfvAgLg2/g0jtl6kcNTG4t8EFXEo/GEMnfDPNhDHaB2AcclYEpBW5d0Ng7w/iS1OM0YiUAL1xg5jv/WWUfX/wCJ8/cSSuOqNpuj'
        b'ekZORq0SvYo6RmbBSppEyfCXKLLQS0y3iAVeMgN9m85LolNwCol8J/xOtFOYJqfQAliS9P2HgOWngg4sTpjqHB1YUmKBBd6KOHkhCfaofi3ABycvD76R6A4Xvikg+d4P'
        b'mWAxmkP4lwqTLqJOX8Ci3B2wkOGONQC1scUD4NJhBOeVQx1D3UO9AAgyKk3oKQqW7/Qmewj14exQalzAHuoIQPkGLLyEOC4DN2YR7p14H3AQ2EE5gTggERP0BUxaguxd'
        b'wE4BxbyhHqH4UEeZD3WH/73gf5dQdiUfSsJ6Ql0QuFKAxITnHUJ8KDGUiKRZtYWA24SLGIApKWCF3sTDgoffAIBGyJnONTlDyUAQ4BNnGgdgE0+EQhx8lU8hyPxUAtxX'
        b'Qo838E0m70fwxBzKhTITAgmhdHoPCAFamxDKolSWnupBqR56qieleuqpTEpl6qkORjsp1ZFSHfVUd0p111O9KNVLT3WiVCc91Y1S3fRUZ0p11lNdKdVVT3WJjhumMiiV'
        b'ganKBNgcCpC8D3AbEG0iEoC+hnqH4qHHiYHETYJvf0CiqwWvtFbScK1AGTD2leh/XO9NGocmhTCe7XCNQakiOYuQcOQRedPzvICEzwOS4RKm2bd40v8VuM3p8x+AO/7n'
        b'8dNoxE87mvETajQKVt2ntll0EqZKlsiCGf/+JlnxLfptRU8YyWaBg6fN/wWBS9bv7V9JDrR4RvdgDiFZtAMec/LX/PtESnaIiXyyaMVj1H9IJoeIvH4LTGcYhhGmY94y'
        b'AZcBGx2y6pjOHOJiMJ0YMtH2DgRMyAYMAGA4pjfegoxpk2r5NwQ/oAE+ZDb8BrABFnFAWnXKZnTqceyUBCCDtIgACDqZdWQVKYkCXWCCTiaie1B6LgUoJ3QxPmTGvRqG'
        b'IgFQVjwicEyhQnzIvrEXj6XGhZIRJHGwCJ2JJkC3IdsQIAlHxKjCA+oDJApoHgET7xPhC1LrxqhI9C13HQPY7n92JZ816z4tOVrDaBYlWex8JxHNgTqIuJrsLVeTPXbg'
        b'0QATiEoUesB6iQ68pA98Ng18eyDLRF8+vcF0KqbJHf8EWGEONA+md/aNHWjo0HTekk42CZhqMchA1IUsGWgGK8GOsjAg+tYYpDaPpUtAOOL+a1J+jQEvEZvCzmWCXQYm'
        b'scnSaEehA5n1pUicn6uxKz9hbnVYwE76Jh1LWLKFmHBnMBEY8JRgWqVFD6JjjanFitgd2pEaisdnxtds3wNqwgZQxdppwmu0dBuKPOjL6fAlPIM3tuiX0TYAgdqjOYhg'
        b'W2Y8UVe+0TCRyI1Ah2GAKd4EupPAuD/o4rIuHylT8glQFfWmlSNGBH+5EkEe8l3+e3v5iDirfa668krXMgXVtxWrJWpjI+kuIGmd5fDEpv9L4UUy/pNQ/wWzbjhlAEwi'
        b'XB20CaBqO/q4NKNfIQG3Artop2AsTt5sc4jpFnyabHHqwttkPiedSR6asHSKzCH6VviUl/DZy3j5CV5eYfrV6NjHp7xKxgSNnupy5b/otrbMv0h5jeyy4cZdhlEflNfJ'
        b'QKZaVnpQocCVR8SycuDnF5X50Ho7YtE9VkUsPuOmylNXXubx5cT/e4YsZ85/gPT9fy//ynEFrkkMseWL4DoXBOnqowqnKZ2OFPD4oPVRBvuT2vhztPn0X/8z6/+jabND'
        b'TLZI4tTBCHuVi/Ga5ZDEfp3wbsR4hEvBaibmURConyVofHOSo4APrljJnsulQ2RtWT2ApV9R1vHMsJe8FLCzkRcJ7iYur3DXo+cmBfVG8KSkoqzB53a5Iikul6+hniSC'
        b'KD5D0xZ4GudqTigft3Q2EWMBO6K2Tm7wuNEfG/NCKgFiSRSAGGrrvOZOrp3+vJtADncNxb//A+XP/UY='
    ))))
