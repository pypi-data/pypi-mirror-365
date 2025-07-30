
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


"""
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAlcVNf1/5uVgWHfdwdEYNh3cBeRfVVAgwswwCCjrLPgFndU9kVEwHVwBRVFwX1L7k23tE2hpAGpTZOmbZKmCxob06Rtfnd5A4Oatvn/+/t//vPRx5x37z3v3HvP'
        b'8j3nPviI0fvw2J+fb0aXDiaTUTKBjJKTyXFklNy1vBWGzEufTG44h37zZu/IxOgub63AnQln78xH/4vQ2BjuWqE7k8nXjZBz1hq4M2unOEiY9QLDGqnwq2KjxKXRaZKy'
        b'iiJNqVxSUSxRl8glGVvUJRXlkjhFuVpeWCKplBVulK2XBxgZZZUoVLq+RfJiRblcJSnWlBeqFRXlKom6QlJYIi/cKJGVF0kKlXKZWi7B3FUBRoXOehNxQf/FeO7voEsu'
        b'k8vJ5ebycvm5glxhrkGuKNcw1yhXnGuca5JrmmuWa55rkWuZa5VrnWuTa5trl2uf65DrmOuU69zBZDtl22VbZouyDbJNsvnZZtlG2VbZxtmG2TbZTDYv2zzbPts6W5Bt'
        b'mm2bLc52yBZmc7M52Y7ZztkWYS54pTeIyl2ynKZXr9zVlcl2maazXae/S5hol2hXD8btFXeLmYW8WUwxB60oN61Qf89M0H8rPFU+2eb1jNQwrVSEvi9Schn+ay5IDfJT'
        b'tnh7MBpPdBM8ALtCYAOsS09ZDmthU7oUNiVmZ/jDDtglZLxi+fAhOJNDxh+bLWSMl4VwGUm+31fcZYxmHboJ67jwPhw0NFmegLg0JmYngH5vWOuXlArbMkWwLiEbcW2G'
        b'Lb7oCbA5IRU2r/ROSIHNaSnp2d6ooTYQPW95QlK2t3/CKvtEPw64wGfUoM4mAu4N14SgJyR4uSPOM1kgng2Bm8D15Ql+ybARPTYF1icKmGrQYrh2RUEhR285THXLsRUv'
        b'gUkuWhKyU3y0S0K0iyK0d0Zor4zRfppmm4WZsrvEyeLr7RIX7RJHb5e4M/aDE80lu/TS3aldKn5xl8Qv7VIf3SVDZwO0yjsM0CqXDleJGXKz34zH8JktHLx1xWur6U3L'
        b'WSLGvPQnPCY/3/iHsf705gLUT7TZksMsyTd+3zmI6WNKjdDtxwIH/jNL8wUmzIdeT7k3gkdi3+SUYoPXLuzmDKCHBc3d4fFY6Wpny5DbaUufmh0y43hPLnkq+Kf9Xw2U'
        b'zASjCcQeYT04hbajIXC5tzesD0zwh/WgL8sbbfcQ6IMtfgGJ/kmpHKbczHAhvA8eSgM1NkRL4AHYFadRGaMpwC4GHAY1r5MWcHIB2LcGdKiUAtTSwIBaeNxdY43HNEaB'
        b'ZinoVikNENHEgPpAAWmYBU6XWcOjKngD92plQOOaHYRXGdCaJIerQDNaU9jDgOPwHtxDn3INidcuN0RtXNR2igEn7Ko0eP0Xi5YjDT+kqsKPb0EPSfOjI7rB7fCMhSp4'
        b'VYgaOhjQCvrm0rl0ZMNTHmiIBg9pY0BDFDxLBNsMd5vCfeCUygSPOYl4LI6gQ67Dq8kusFsFB7FonYhbVSgZsjM3CV6eqwKNuNcxBhwBZ9fS2V/N9LUGe1RiLK8WsYI9'
        b'MaQB3IWnVTtgv2oTMmR4mAHNMRqNLW44r4THNoMbKjOGDukC9WAPbbqTBWrB0UA4aIKf349WPQgMaOxQUzXYA/aBAVgvJhtwEQ/rBOfJMHgFHM2ER1xBA9o2jogBl+EA'
        b'vM3OSAm6V6pV8Bre0IMMaIF7vEjLEnhbBDrnwkENj670IRdwmCz1Zi845BMthgP4QVfQFmzLptKdgfvhQ3gVHFVt4lJu9UwmmWyRuxPcnaqCN7HY3Qxoc4bH6PPvF3K9'
        b'wHGVGbudR5Bku+nGHQX75C7gNhwU4bYz6MbscDJVcBDuDjWAnagFS3AeSYAmfpfItsU7duEOOKgW0Oe0gLsMEcAJHlWCtuVw0FhIhxyPqqACPAjOBJfBOdSCV6AXMcty'
        b'JdNRbQY3oXYtHIRXsdSnkbL7gXoiQTIykQ7YAxqRw8SjLjOgJwJcZ2eUvnC5D2pgV+cUuA61pMVhFbgDroBe1IaXdIABp0PmEekywHVwNp+P1ppVuLY8W9Kg3Ar3ggMG'
        b'aL85dMQpo2UaB9TgAvaCO/Ao2slBOIjbLuAF6wP7iHxw/0ZwP8cbtxlQPTmB1rWZtJWDIXgcXoR70Aaysh8HV4PJ6qXOtzICx8QifP8GA86CZoYq0FnQsboMXhPDa5jf'
        b'dSQHvLyIDIHN4MHCdY7iagF9UHekI9X7/izQYS8Rwxt48a6ih+RWUy3Z7WyBBDuEWvBkB5EOO8I+IpobuA+HYD18iNoE9Dk9xvCwxhKLvdNf4ahSY8lqGbAfNKroavfL'
        b'wQV4bolYxafL3VUBu+lzULgCdfB6ntgIP+c2g/b4yEaNK27qAV3wAWiIgK1o4RsFDNrOBzx4ipOO5lWvccRdbmWUgIZqeAg0gXoBcmgu/BIO2L0W3NC44cceBPc5bPsW'
        b'eCxEx8gQNHHtUBy9KuWR1SmDF8BV2IC2G+zxqWAq4FUlmQ2ozYVnk5HI4DY4VcAUJEdozNFtkVd2Mhb2DhgsYoo2mdLFb6hMhrfgNb3JD4AmDQZys+H1MNgOa8HFCNAn'
        b'kKWCJnhmQww4vToVdQRnwlQC0IGm2kt3qss6wgNoVcQ26hhwIK5E44Xubw+DPToml5FaH1oN7hEqDFyEHXzGGTbxDQWrqek1IAW+CnbBEyo4xKFeu9nGmAiTswYepXzA'
        b'DaTkiBFsn5MALk/xAff5PHtwnKrH7aRFSY76YQSe0/jgJzyEHcjLs/L0YzZ58CorzyUqz0G+MBcepYtzwQQMgf2wFrle7CZOMODY/PWU02lkDydgewK4FEHs9RAYTCGM'
        b'QrB4iJE/D94CveAm1aQ78HCeN+hUKbEmHWBATSC4ppFiRrvmJEwtEFllcG+DWAIbQO9KK+yNDiZJDMSL4SU6s2a850Fl04FwdZbGF28WqHObsc706xXYhH9cwBKVbPBX'
        b'Cqpes6UKfBMcliWDuum4CfrBQ00AaoqLtZ6aVxOvAB61oUKB0/AI0gDQgBQgAd4SwuvIfz4kYtkKEkBHLPLzRES0kfBWucYDEXmwRkqZLUcBhKwT3jT+CuQzB3nIbWhB'
        b'C13qNtCwAJwHt1RGXLprHfCen2YubjoEL8j19r5pau/YjeudY5qKxb2UKixIZarAFRFS/CHYT1beHTb7RsEhFajnU+93LBZe0fjjJTgOmsuwcJfZHYS1PLTedQuRUneA'
        b'/cXI6I4wwfCkADR7z9fYE3eOFGifH9yvhyrgALhLNhIeKSuZoVnIOe+jGnqBamg7D94DZxLpfLs3gVpD2KAyxdM9gpQUnkRRy5vqitZ8xl5qvNmZ9lEVPcA3ACfj6D42'
        b'xMMDSKUf6gEaO7EmCPNBbjRyms/0sk2bDQI/DUzYNgHCMfu30ylehjfR3QEDPRCEnGaDJhg1clRQO+URppXsIuEdRvR+M2hiQmCLAGiRenQT5VBvhEccQPs0ePKG94gN'
        b'LYADi1+w6RtI6NopZmiq/XwR0G4jLibBemU8AnrTWKvMm+hrPry48CWpEMdLdMrErGFLuj9ytSq3aqIUy+fDwwmwFfEyoKH8EGyqIus5D0X+m/ng3jRug/vgBSKubZiV'
        b'7jEX8GNQIN2CFQXsl4BTyFbzC1PhfYMQDbIJYvK14eBgAbg2jfPAzSUaP7xnTfORk5vhWZF5wb2rvSPItAWGjAqcFMHGbQgTYVYRBUHwNNynBwxzYBeZu4sAaUu7bhte'
        b'NHsy9SzY4g8OC5DKRhNm85GqHbKJVNHofRxpnhc8QRbYMhm0ZuZPg0lw3JD4lkVoMWunVHsqEsRIYDt2UnCXHZMOTxgEGAEaHOENdRECszengRpsQfgAJwagzbt02rnM'
        b'kJrqANqq2/B4ALgr2OAMOonAm+EZeDx1tWqTgO57EzgJ+khauhPcWMFyIzuyKmlGaPHiwbvLUTDDeo1jbyJaxGN6MBEMIq+KLa5sGTip78oRl15qJP2YkRO8wYNXq2E7'
        b'hT8XEcpvWoZ8ObzJoXj8kAjuJys4f7mxjaEe3GwCNXTae1dZvWCJfTMtEe6G95iwKgHo2gF6iNk4IJh/pBAOqMw4FKEeY5aRWZeCepcZbqsO3saULvDwePDKaxmEx0rQ'
        b'4Ax3pemh3LhiosuwLhlZebtOWxCXpfDSTMs7jZzMDXCQRuZrEpRRtKGe06gY9gVrcB5rCy6APZhVBTz84vwIRz64ZpwavQz0ezJK2CGCrabgDNnYFHgSDKz31wfUDXNY'
        b'rwYbN8HDYgTlCBBA2nh47XLNbOw05lXphUszWEOtJ0YiYMKAVgBOmifTDb8JD2NFbUfYG2/4WQxhe0AbMRtrF5ROzFDDy3rxBLtr8yomFB4VgIP5KE5jkYwd3ZCz79fD'
        b'+PAy2EscbaAE+Yh2hKV7dE6oacpJkDs8tAImG8I5ywUGUbArj/CzB3WusfCYXmaAIvtZEpigtsA8mQQ0xIFw3I1iUf9MCLYCNBm4gT1GZH+cULe6NGQngxRDo8ke8URZ'
        b'LVZuoLWcrx/PCRMVPIf44EgeCq6jAKdmbS0F3J/FhShfMTWgiPe0mkWDCQB5TH0bOQe0VOsuUBu5itQO9McTNn6wRw2bFsNBGkSuIXjs7UWUV4ry/d3sBsKuNLruLCRw'
        b'BnuQxaJgdpVkIeAWQhynUY9LcLCKSy2tBS3TASJPAXiA4IO+2w/YoG8F4AAP3nEFg0SeGB7UBvAQGyF1ea1oivcJQLGCbUF0WkoEGqaMkosByk1k9QgL9NPAeAXcKULZ'
        b'1jn9lA0cqqbp9lGvnQsS9PI1sCeadYXggROo89DP2B5GEF/h6QduK0P10rWtoXS/9mTJZyz0FT51E5fpOg+gdUbI8iqZmNoJHgfdmXq5XRWg4Yc/FwFbrRq1sAZ0EOFR'
        b'ClR6NsGTrANhdXQJIYamHcgQ7AK3CB8UhlbDm9sQHwGFF+3wTBJ1aie3l7wMOcN0DgCrBRqFENQRATix2pKisQRQvwXcQGt4nTWj7uWrCLckeG1KMaa1IkyH9zA30JbG'
        b'BK8SIPfbq6Zu6QHsdIT9HJTBcunCa5ERXaKzPOy/fWbMwl5CF7PWoNQwI8VgLjy0jAbrcwYou0VOeDoXFuQQ4zaF9+Ddmb5iCkSxK4bc2BCyo4cC0OLtS/bWen4haJEh'
        b'ZgKanp4WuZMqJXLpWjvEDPbBI9MMuYWsdAj1gVsRFqA2nAOOLjFKA4cVRLoocCYH9vnoZ+PJSjLL9WXIz+krSxMKn/puXMqDN1F+N0i0UVosAS0rZyTurbCJYBJ4oQhP'
        b'81uwHUUSKRp/jaCS70J4rSlFXr8P9qNEX0iZHQO9EUSDzeFxWDMjNeop1UvVnOBtHtrsXlsyt7lwt8QZntGrF4SjAIhhB0oFb6MYOgMgbkB+e0b2+JBvCq9uJZxy4W5b'
        b'eEouFglpdn8GIdkzJAkthAd8ZqzSENhNfcUlKtBlHrwcTUuNKPmuYdSwS69OcTmBTEvkKH8JtE0p1FyUQ2X4GUTORu4J5+AeZusq5onVbORpB63bqddHi18HD8To1TqU'
        b'8Cx1FX3wErjoBfdOlxTAYB7N+s6BulBwLVRcjfn1odzIYQ4J45ud4IkZmBR2bpthytgLPoS94AqFLheQ779nDu6Lq/EjLjKgE43u1oTi1b4D6lA+h3TzGOx+hW6CwdVI'
        b'uWo2wNOrGeVGlGGF5dJQ3VIRhcLigekaDVqQK2QDLV1h7SscxHz0qIsCSza9uoRSBUdbIh4PefzdCNxd0qvrgCPOxAyVUUA7I7uamQ6SGBQPa/1Bu0ANtCgwUwyApNHC'
        b'Y6BGrx4EO2jVMG+u2jRVrxaENnoX3YieENAmh51iU6wB9xj0jCtwH7Xfk6AZNL/K6U3HfD4PXEbz6kFQhANvs6jXE3nUqX3CPT0NZvpMQVU4J0NkgMAYkgIv3io0zUMz'
        b'Zkw2FsVCeFtQgHYjlQmxE4BGXxSfiL87A+rmzUgFwF0Fqwu0sgGu8fngjh8tX7TCAwiU608E1L7OCtNPTaueL+Kh7BxH7eR1RDWmDfpC2QwznM+D981XUj06AA4gH/SS'
        b'J5npyVtgI1qjdgFyGvVVUhFZd0dkllfg4W1iUxwRHzAIVz6AvWSvliIoYWQmhldZm+xZBi6wKOo8SsCOr0VNeNAtXJdpX0orUrddY23niQ25dBPPw8FKtqgD98OLERFi'
        b'DVvl7oR7EbQnYbw2YYUxqJ8u98FT1sQpuCIjqiuHtWIVa7UntkO2GNoKb1UVoly3gfrB+8jvyOA1gozhJfd8dL8d1LKlPtDPmimoJdVBPhjMAg3ZzKp1KFZfFsKTQeCC'
        b'lE9D25CVE2xISYKNPMYhiAcfoIgA6mjtRgRPgZZklJVfzU0RMtxcTiC4D/s0TgQ6RgUlw+ZA2OQrxWdkxuZq0M+zQaZdT2aYZLvYN80/gc+Aujz+Eg5a4o7cQny4pPvg'
        b'Yx1y4lSNEz+h7hC0g8nmkGMwbjZDjsJ42eIwQ/YQjJ8l1DsEE7gy2XqHYtmCGcdd/GgBOQR76e7UIViJlCtbgDbNKAYf2aoksnJyVisprlBKqmWliiKFekuAkVEiPRH2'
        b'2VhRrq4gp7s+uvNgiQKNqpYpSmUFpXI/MjBerixjGanwOKMCWflGSWFFkZycCWNOhIdKU6Y7a5YVFlZoytWSck1ZgVwpkSnZLvIiiUxltEleWoqkmFcpU8rKJArEbp4k'
        b'q4QeK+Pz5oKp3gG6TgWKwnkSJPZ6RbW83I/2xA9fmhgzg7uinEgoQZ9CNDn5ZjUWSS4rLJFUoAblFEMin3KLPlO1TgS0BP+anxqfmLMcAiSpGpUay4zXKDPdPzQ4IkIS'
        b'nZKREC0JYQcWyaeeq5JXyshDffA3H4kcbYtGppaTg/b8/CylRp6fP0MWyoOVh64O2UpWNkmmonx9qVwSq1FWSDJkW8rk5WqVJFopl6FnKuVqjbJcNW+Ks6SifEoR/NDd'
        b'OFmpitzGi7NJoUKCzjhEFTAvHqJapMXRWD8AWqyS4dB0aSoB7iIHpIkLHZggRuTDzc9//eliT4Z4FOQnTzuBBoYJAg+ZHCYHtMto5yIjxpqZTBWZ56cciXCnR6xX55ox'
        b'zkxXhEFQvnFErpoeFK20RvlNB+ierrHE5EjNiFEjLJKH/OZlvbO8M2CIiJmJgtNe0GE6fZi3GUF5LFGwbYHQR+8o7wigRc/AGHgH3hfqneSZgP30bOBsvv2crdPHeIs0'
        b'FGFc8geHTeCguJJHs9FODp+6xCMVoFUcIK5is5SjO2AdebTCdBHUiqYP/bIgPQ4E9XHwVogXHFQJab5wEOHKDurTrpRvQCF5SP888DhopX5071pwFj5Es54+EsyEF+lh'
        b'3W4+2LNKo3cmCLW2RAjnHNi6ZqOYrMsNfFJ3O5eMmA1OZ5mh9HCQzPMoCnexcC8R7zUwiNz/frBHtcmA1tJapHCANK2Ed1AGf69gumyFgl6blEdluLsExbRD4dONWeAg'
        b'rX1vh10xTnqPArfpGawqBu6PA2enHyRgi/hrYWM5OCbTK+cVl0u5bL4ID3HAoQy9NgV8QJpmzUHYoAV26h0DF8Eaomt7woSMMZORbCDJ9/uTQQLV1lmgbS64tyM0CB8E'
        b'taN8ec9SRUncHZ5Kghb/zqfq7SuuroBBxh12v7L6cdpq7lhd/z5XnrjwsFJd/FHAisWSTffBz12dHr4Jvim4fvWzhvbNdX73nz/12LLmn5yj628du8/9MqvUUfCjvrt/'
        b'Gan8/ZM/RTLr2z9pLFtS4TIRtqX+3KU/h3HfEyTn/zK/vvijkT//unqJv9e69Z2bP/9o6J112x9XPag2jsv7TNP0YfOplIQ4aHHlb1+M/a7q2hrnT3/m+Q+bU7Hfu2j0'
        b'z5KaNc2V6y1uun74TvytSIvnO7o++/27H1WrfPYetrH+wSLb5RrPo+7apJjGJ3O7/T7zvuIgf/TT199IHv/SsHr74rHn15ktwb+w/iZxgdvuz2sCPzbKrnH0WCQNeG8g'
        b'0zX55tFNsgX1G9ourC751WPX/N+tdf7AP+/N6I68b76fuMAl729Sg2dkO9phf4mvxWJ/7wR/LiMER7j+4FTSMxcCBdd6+QYk+vlIAxCQaoR9frAO4REJPxd0Bz0j9Ysb'
        b'TqHJ6f6gLh3Wpwgz/Rjxci5shvX5z0g94WZBJGyAQ/Gwzsc/gIOY7+GGhsBrzzD40yAYcwchvWbEugZc8oV1m+g7LdX+PrA+kMsEgPsCBClPgAYiJ4rvlypgQ1xVql8i'
        b'bGYYYRjXdPWKZ7he5gyvwdPJdDSCri0p4CGoIbDCBtbwEHgB3VLxBNdbqsTu4TtdVPj1FIlkl+4zYbOgWFmxVV4uKaYvaAXguLhowoh4/jxMKLH+c/HYG0gLv9zFfJEh'
        b'YKztx+2cx63sOue1zWtfULvsfTPLcVuHTkWbon1jK+99Kxetx/nAnsABjzH3yBH3yEku32bOuNOcMSf/ESf/3qJRp9AB1c0tV7e8YflG5mhk4qhT4vhs70ke45zEeSJi'
        b'HGdrQ3sNxhyCRhyCxp0k79u5jru6ad200V0lrfHvm9mOO7qd9O/2PxrYaoBlWNy2WBs2ZuU9YuU9buc6yXC8MjifMxz7DM4HszwmBfjLpJCxdezMa8vTZo3Z+IzY+KCO'
        b'w54Ro3YR46gLj7GP/MDG4YV27cZRu2C2OeQDB5eTs7pn9dqNOQSPOARjqazsuuJ7F406z0XEl+9b2HR5dCm1nC7v3oBRxyi8PLaOXSFd0a0ltfHjZrZdilEzL3zX2qVr'
        b'/Yi155i134i1X2/WqHVIbez7Vng93zdzGLdzG7PzG7HDDXYhw+YhH1jbd1l0WbYmdG1Cg3qte2UDnF6HEeuQVs4jO+9ei1E73171iF3osHnol5OxHMbZc8wpfMQpHM3f'
        b'Zs4jLDz6+ZUK7/2bZnPiLJnvW5rHzeF934ODrvggkZEaT/DxPk/wENqZMGDxxQQfA4UJg7w8paY8L29CnJdXWCqXlWsq0Z1/rWLG6JKPPjo1U2LXRrSIXA7jPviQ8O+7'
        b'mOcKPofj+VcGXT40tWvYuEs8yRVwrB+JLRvmfsg3q0kdF5k9Ell9+UTACMx11Fcq8tKa0I+5JI7kIWeP3wdEUPteWjIyEthQBHvSYHN6ooAxreRFxcMG0gEecjJKTkmj'
        b'QJvDiFfD06COC/GbHvQtlvmgDbQiiL7ThUXoicaFujcr8YevwyQbMMzmUphNQDaDILYwjM9Ca16WHlAu5yNozdOD1vwZIJoXzSfQ+qW7+u+XyTZzMLQm70DqYWtlRZlE'
        b'pkPJM7HxTBxM3rX8dtitlFdpFEoK8irlSgS9yyjS1L2MGWCUroNp6IE+KxBnRZk8VqmsUPoQBjLUUjSNrLEsWBSKrl8UcAqSskLSXi9KrI+/40pl6yUKivALK5RKuaqy'
        b'orwIwU8Cw1UlFZrSIgxPKeokWF9Csf40EI1V4ClM41uUX8gkIf5qTSXCsCyiJTNHMNsb9/DDzKX/FpYK0jQLsfZpE1Fa/YqXGetSfJL8wIUs8l4jfg+zLj0lMZXDgItS'
        b'uBvUieeCnllZivhSLkeVhviczf1osLD7bXNw4U2GI31sbDzSmGEaE3RauvbmoeNv2wPHt36yi7O0K6ZrT3dKT8jZFGNjQaObX9Co5e7fWDR6pvgY9xj7GB/7lLn1K1HR'
        b'X9+Rcp+5Y+HaYJep2AepPaxbC6/DxlQNG5JmgUE+vLIs5JkEG8husBfWJgckoYAEmlDUwREH1HsyjmCIX14wTyr8N3YvnAotxOInxPS1XRpEZumCCH6rGAeROAPG2vWx'
        b'rfvw7KWjtjHD5jHjDrPHHAJHHAIHRLe83ggbdUioS6KBxc6pdeuwuRty9bXJn+N9oH7LYEKkU7UJA1aBlDi0KnEoVzrOlM6AeiUsIHVIs3SXMZ1D+ho5pI1CDscDhRCO'
        b'x3d1SIeFnsw5cTBPg2cYsQjWTtURNq/RVRL6YAeoAddAI9D68dYlh4HmKtAPzoH7RkwBPGgCj8OrZQRvJgrF4up18JQpguoofYAXy9kjRnghIUVcvRMcqsIttQhUWqdQ'
        b'ND4ITjur4A2zED4jBz1ceJBjC++pyCBjjqcqBNTCRiWX4VQw4GYw2EMHXd4Jz4urcV2vWoj47WPgkaWwg31ZaR64QTxisjnrEUVW5JQH9sTj+/olC09nns3rwTSb6MnJ'
        b'9U0Tw5OwmcNwQTMnBkGdzhmuVKSzIyUzXbFArlSQratZGCKXahQmmnKpwv+yS5XpVyuIH3mhVqHvgLCDwl1eXSP4lpQeD/hfzegLS8kjVXL1yzn8Cw/Hc6soLNQg31le'
        b'SIXQZfGxGdGSGBTYldifLkNxoFBdoUQ5eqWmoFShKkGDC7aQnqwfj0F5vlJWSngsRdYXoCeDDC+ghrz575MZk+Xjh34sW4Z/xKSvCEY/kRg+S0OWkoaYGB8/wkVPXlmp'
        b'quKVNQc8AbJWlbTSgDgVYXe+pRItCGbyHwW4KS4VlTSu4ZH/WWz7vy9pTMGHqdhhlhZHg0dfofO/ix3wOqidGT9w8PCBR0gyycnApQ8mKCigK9NL8DqtZvwzworBx6VB'
        b'i0oWO1cU0QzTch24BA/CPbgkgushcMiU5vk18Nx80ABqK5AvqEWu2opjCI/GE0bipaYMQlD2QSuTbCe3iRmU9+J3E5Xx8KRfOq4fBzPB4FacBtc0YiqLuPBGKJpjCBOy'
        b'fQkZX21ngUyQiQqKUKQtS5iNxxNP1gDvwD54Gp5leUhBM2kohG1rwGH8Li3y2RlMBvKQbYRRi4WYQR1EQSt/Igs238JkKSwvOQpUo6jpiz9kbm9LNd0TZL4vb402KyxA'
        b'87u8gt8IxvOfmf/JPvW1Nu/L6s8S710ZyihYciy1PfLX244rWp44vbWp97O3d82ffdlha0fEx3vbn71eJfQu/ZVhq/hnTicipJE3er1dvgjtk5/Q5vMOWp+/t3Ji/o03'
        b'DFf/ozL5uPHPPm2ffzd44d8i4w80R+QtnH0tOfxnbz/1HPisa1gaevETxeKxZbzbjxM+bnm+MjNg+Vx5Ucepc8u+FqriPeJ+sEIoefKXTdc6N/36Bxt/2/aXZOtf/OzS'
        b'wKV5c0wL6g72PeW91+WevylDKnpG3j3fBG/7BlnppbPLs2lY7wPnxCisn+KSyP5SWF8X+AwfpIHmTKj1TcPvvqbjzDYQdfHH3cEgOJ5swARDrTBxhR+FAPj9yHPi5C3g'
        b'DGyUTvGzAQf4IrQLd2iCfR3lt13J6aGwzh85+GpONFLLDpIgL4U1KKW1RoGvLjAdi7uD64NYXXyGyzHx4NxC2JAZrJfvvq56hivg4IYlGCgqSoZNyTgzJ1m5WRBv/TrQ'
        b'KjX8buktroVPZbcUhhjSVBZ5cqW/DoR8yoKQ1xEIscNJmaVNp7RN2u5bG4MAx/t2bo8dPYe94kYd44et4ye5PAu3cVfvMdeoEdeoW1ajrgtb458IEXzpKtSGjll5jVh5'
        b'jTu5n5zfPV+rOr+lZ8vpbWNOoSNOoSh3/MDKdczKY8TKQ5s5ZiUdsZKihz0ys2wNbdjcFdKwQztbK+vx7I057X+L99D4tvEb2WNRySNRyVgk1Cu4rrrLYdTMXVvY69ZT'
        b'PGA46jmXpIm2XaFdVVqLrijtpvPbe7af3jnqFEHz8S+fuTD27ij5s3B75CRByZ+F21cqCzTbIYuYAAYGGMXM58F5HHSlGEpMARN2ARM8FFJeBZ2+tY7wUo7nr7v8WR9S'
        b'5RhwOLOeIUg167tCqiNCH+aCOJwn5eje8z8v1Z2wyLbQE5bNKTN+K2jKzRYwNEsjvxXED+NO/fYP77/42z81Uu7WE0YraGz4lgSlmOQaBBnon2n8v8rKZgQh3ktBSMgm'
        b'MAPwKAL93ymDAf3VOAhVbaBV5ysrOGxRHtTvYEC9L7hJTkU3uoDm5HR/WJ+KkvP7kkxYm8K1jMW/mgDOgm70RcpkmBuAG0vhaUXzx69xVBloUJLF3sHCIygR6tUlQuqP'
        b'2VSIJELmOBFK6VEH8DJO2GQu6jIs5tab/LFyS7GHk/3eqOBUkWxXX4bsg58gNXzDMLHXXSp4hl/TL/SALfDIRjYZesllGlURTxUODgT7Ioe7FN7W+dzyoGfYKCJLtk4V'
        b'ENniYZkBPxdcLn1GagzdqtfFyS+4TtE2vmgb6CKeDl5aBtvQYlSA+2yNkVYYS+AuKVfPurCT0vkvg/VyNfFeETrvlcJ6rx2iF1Oo6YLcC3Wxx7aSYbfIUduoYfOocSuX'
        b'Mas5I1ZztEWjVr7Dxr5K7PupPxAo8QK8MoHCya9e+hShu9gj81OFoS9/QyKViTgcy+9g5p9jMz+I0P0psT/v3xoyP5v5XzLk9ciQtxplVpYq1Kopa6UnYcg8JfhusVK2'
        b'npxyIcvVWbxMEvbKGoKRd0x6dlrWihw/SUxCbExyZnaqnwRxS86LSV8W6yeJjiHteWnZqUtjV0j/vZES/HNpvQFjnPVbPiPJNzbfkMhoohjyosm+Avwbmr7g3k78O5N1'
        b'KcsTpnMzeFAK+oxA9xb0PxHUbWHAcaERqM1YSN7MzJKWkaHsOGSaxLe6wl6+MTgATrnBQwrIPcaosID/OPlHapPOb/2QGp9KpAqKCZotjnGN8Y4RtYdnlLlH8mLCQlPk'
        b'Qe3SrJ0+haJMb55vq81b9YoCUWjKOtdC79PCrDDBL/yKa3J6GqP/eOtXZ8Eb3cK4lcxXjeI/Z78m5RMDtFPP9Z0GPOBhtD8D7xMDSnfOwQYGd6e/AE8kbqSAD4/OBVrY'
        b'MI0xqmCnKTgGThN8YgduwPZkgoC8hYyhPZeH3wCNTJPyXxnj8PpPKfyEEcq7VGw1Y5HOFPOoKU7mGjLW9lO293Lhl9jf4lHbJcPmS76tAoz6aF1HbYOGzYPGrew7F7Qt'
        b'aF80bOz2f2Sdi3QXb33rTDX8btapjMRP5RBVATej4F0afKOAFkG8lkBQT12Y405+CegEF19tv8XYfvm6QIx/OXeqVPrftWGc19vgUql+PCZ1x3JZGclKXxGGcU6Kz7Ar'
        b'5egGCtcBRonUkktlajVKMQtlKL7OZESis6yIVmBfSqKNppLof5dD0/z5/w8YIErTLEDfw0XgwqtBwGI48K04AJcxryUSF5Xva08z0R1vKX+w2J4eoYMTHttVVemgVndk'
        b'D84JyStNnOpgHTJ4GRbwQCOLDGDzdsI83R35P4YxDxLGGkh91YzCqC6Tr6pALZvybWnd9MwLdVMCFi69Zc792CA0Jyc4yMMohPmrMDg0n6lJspHMr7XJ3Cc99I6c//Zg'
        b'4duhvzQIhSlLqpy81p4Q/KjMz7u8UJDTaaB0iDx3u8dY1Fl1jsP8RmUKZqulQnJOB9vA7m3z4PlvgxM5sJakYPAYuB68xl8vCUsnBxWwGbmyVAETmSbcsQ5cJq7PGnSW'
        b'gSvBeu7Pf70LOb3MALdgqz76qAQX2NPLY0XP8K8xwkbHpfrwA9bALtY9wsMuRGTQ7LgVnshMflmIWeAgHx4HLW7Iy3wr6sdeRq/Ca0ygCdJibBfKeJ1T3MGwJV6jF/AJ'
        b'znzmj5rN0oaMms0hR10hI3YhA/NH7RYPmy/+wFU65ho44ho46hrcKh63cx+z8x+x8+8tGrMLHbELfezoMTxn/qjjgmHrBY+c5mg3jjqFDASPOIW3igirgBG7gN7No3YY'
        b'4uj5TIMJMXbZeRVKAqL+ZX5Di8R6NWwyJ3KZx2EzGuRHn1chP+qAi8QO3zWjOST0YM6IA3lSXlpanJQTJ+WmxSkmFTK+6gBaujdPP9737oE1ljJng8nnptEfMDZeq6Mc'
        b'b2T4DgyEOR3KWfn0vu+P9/jF57SaDJZt+8u1+2O/fvQ8d+6Q9vxHWxZt+ss/vv/13W27TPNAR6XXUI3Xh8ctj8dG93RGin5lt7xmgXYoVRRsb9X9dcaf7h1tmiga6hj5'
        b'Q7e3UfHHXRbj/R0/MTMaOZnT8PhEs3mnt3H32Dut7qFF8YPVSwr7f3ph348vOK7Y8yhNmje4672LZ+5NviGeVX+kVDHintF48Ax3cZLC4W2FwEdhwx1yDFeb/v7nkg0K'
        b'lz8oeL8f+dtrS+xOtQWAgjv85E9DakqsjijEh71s/jy49Is1dUFN2o7LYINj+Ecl0PGO7Z+GeJ+VeL03ahJyx+JoifHRT23VI/2fnPtl0T+rnw27jHdnFfw+7e7wjzXO'
        b'2nnGd5y2lcz64ufbPzn/ddUuz9/+NvFv9wzkaubAJ7K5P5Xs/yQo7hML57Ono+JaZnc8kjZZrW350GPhvtFnxt//NCdlWBWVHviB+32PK4E//sTmUZXlqk/D156PrGx/'
        b'H5RtjX9w967yq23FZSnRzPMnjNkTUcsTfvqTSz9yyFxx5PL3xLHvWPzoWHLsqk7zjy6YF+6I+bvXoHu7Q8S7t3wjBwOdl5+/8vMN6R3mR3qtNpf3uh3YEn+lfuPt8P1H'
        b'/nFj4/6f/1CV/lx9Nrevc7LTonXW4txl4knobRkf8Xh/8SEHm/2Rf3zjxxuC/+CcfcmwXzWx6OJ7LX29JotzcmxXPvnDLJvmv49+eD183dt/jf9Z5OaGTZtbzI79ZvbX'
        b'34SsfdxzqL3DifP+14d2njz0yz/s+dnyOaGjdqGR60+BhyHhxTt+2tn9tCj0Yerz3xqfqOQ8+PhPnzlb/PX3v+xXmP/jiz+q7vR/fOxvq0pu/qJe9r3wp04mn7zn/2ED'
        b'cm/09x3h6cUh8DQK+hyGE4V/s/ssaKRvUjz0kjiDOy/lOnzRdnCNOpoe5P/EPmFw76t9I+j3eYZz+jk7C2EDQmtN/kIG7lkuzOXOBj3gBgF7YnAF3PVN8oe1iSlpAkRe'
        b'hbXWXOSkelY+wwc3CI+gXDMZhyvUBzYm4j5X8EEIF16I2ih1/m7vR4i+7fKd37J4pW/BCaJE91mCP7tmfKhLFeXllVbIivLylOk6d2ouRNgbYcw4DmNiM8k3MLTDfjSk'
        b'YVOXW8Pr3SptiFbWE350a+/yozuvegwob7ld1dxafnXzYMCby35oCRNGQ1Ie22NAKusOP2qoTRqxDxiwG7GPGl6QNmKXNrwiazh75ciKVaN2qzAAtWwvHzYnrzy8xpk0'
        b'YiytW6PbbGqXPhUKHY1qTSetGUuHcQv7cQunJwZ8B6Nak0nTVI6N0bix+bDlnEke/v6BsXlr4KQAf50UMiYWiDAghIgShoQwooSYEMaIGLb0njQhlCmhPCbNCGXOtlkQ'
        b'ypIOsyKENWnyn7QhlC2h5kzaEcqednQghCMlnAjhzPZzIZQrS80ilIR2dCOEO5XjyWxCedCmOYTwJE3SSS9CebNySAnlw4rvSyg/lvInVAA7LpBQQWxbMKFC6ANCCRFG'
        b'iXBCRLD9IgkVxUo8l1DzaMf5hFhAiYWEWMRKtZhQSzgsk2gOoZdyWDYxlF7G0k9jKR3HYUWNp3SCjk6kdJJufDKlUzj02amUTGPJdEpmsORySq5gyUxKZrFkNiVXsuQq'
        b'Sr7GkjmUXM2Sayi5VifXOkrnss15lMzXiSmjdIGOLqR0kW64nNLFumVYT+kSSgdPKii9gWW/kZKlulUto3Q521xByUqWrKKkkiVVlFTrnq2hdDXbvImSm1lyCyW36iTf'
        b'RunX2ebtlNzBYbd7J6WXcNnu0Vy631xW0hhKL9O1x1I6jqvbb0onsPSTREoncRkr93HLOeOWUnJ10/2b8zSH9Kg1nFzLZZw8TgZ2B77n6FuXVBszbj9nzN53xN73PXv/'
        b'Nn4rZ9ze5aRJt4lWNmrve1DwhMc4BHxgHTBgM2IdURs77jLr5Oru1b2CUZeA2sTWwoa0J4aMkx/yBkbmjwzNWwu7VL0xA0UjhvOfcxcahn3O4AuPMVqAL+aTfETiRSCd'
        b'u2ZrVQP8EcPw51wLQ3vcIYLthUhkvHYOnRvaNgy7ZY3aZteKPzA0ww/I1M7uXTZgM6C5tfKN2B/OGfbNGDFc/pzriRgwnpTLCg7LBtFYp1nJRgwd/8o1NvTDjU5sD0Qi'
        b'T6PfwdTQXb8DIpG7oeJmjhi6PedaGs7FbaSX+RM+Ir+cLBRxDBM5jyxnnTEe9o8blcSPWiYMGyd8RV6yqot2TnRhfuRilRjElvPNJ7gocvyHNfz/JGiZTwPimYGKhCdy'
        b'wdFetYhFxjEcDsf8OULG5k/x5bvC4xPCAOayeC5PETH3Nk/1PXSn0eykpvWnRnuWWO/7y9/7BBY2X8T3RTd88btruZKSDzev2mNeEx20x2z064iw+o7R0neMj217EPp8'
        b'6B3FO8p/8hM9jvXwa2qiPy66d/t7b5UktnqUj0k/PdDp2JQyb9XapXO4nyutk3NC/uj51vWVS63iDgf849cBFp+cqTsr/lr55Tc5d1dXHDnfF5psWzHYemqJwUJnNxj8'
        b'1a0lzb7GQQuMzwzWHDhfknRzYHfp+z+5W/n09eMPIjn1j76ZE5ss+vBa4Ac/XOqd8Jd/ch2euja8nyw1oflZjccs8hfZ0vHrp8mwF14yQIjlGhf2quEeAmlywQB4gHPi'
        b'q7gbPkOzgPd4oNUH4akH4Ahl0wHaXwMNoAW2JK+KQ8gKNIEWA8bUkucKW6oodNsLBmBTciLsXZXqk2rACPlcUYLjM7xxKyUZvkkChpMM99ozsAv/RZxn5E9P9MMh/Lcl'
        b'Zib/oDkw2T/X0AfdbYQtPCYeXDXAv/MNOsiBYQIcWDg9ZAnYT0cJGbtlfB84FELm5AsPmpCEE7EijPK3YFZO4CgfnLPxoK/WtiISlyKTYYNspwHD9+eAftAdRRisgo2g'
        b'ATZIEQsE7k6ixatLR/HGbDkvG/aB2wRv5lvFsD1a/LDQpKDJIX8lQgKvCxiwv5pU8N1W5Pim++E/j4GeleqC1h8+4MKbQtBOT0Br4LHX4SBsRIAy0KcKQ1aTJARaHTV8'
        b'NLn+JVL3bweM/xWY+F+8qNwJ4nwJaL7wmcKdinKFGnmPXB3ufJMh53efOzICq3ET6zET1xET12ObR028d8WN840OpOxOGbZwOxP1Lt/vl3wThPUcXYf5tpNcI8Fqzi9F'
        b'DgjiuXqPuYSOuISOuoQPixzHRaYt4jrxu9ae74q8xkWWYyKnEZFTV/S7ItdxM4cxM88RM88xM+8RM+9xY8uWtLq0YafX3jXOeS7cyBfMfc7g6xNynVxtyBhb70r/8lkV'
        b'+mL3OcMVBI3bONQasU8Ytg54T4QgKLpNDz/v8pcGMiDQJcaMB0056Eq95awJXqm8fIKPXyOZEJA6/gS/VKFST/CLFIXoWlGJmnkqtXJCULBFLVdN8AsqKkoneIpy9YSg'
        b'GOF09EMpK1+PRivKKzXqCV5hiXKCV6EsmhAWK0rVckSUySoneFsVlRMCmapQoZjglcg3oy6IvZFCpShXqWXlhfIJIakVFpL32OSVatWERVlF0dzIPHp2XaRYr1BPiFUl'
        b'imJ1nhzX9iZMNOWFJTJFubwoT765cMIwL08lV+OXcyeEmnKNSl40HQVU2Iby/9VHIqE+PVd3wX9ZUIWd+zfffINf07XgcEp42K3PvD4h1+/i5HHYelMkjLZn3rQXR8/m'
        b'fSXSvXc+YZ6Xx35nM6CvHItn/tFQSXmFWoLb5EVpUhF+N7moohDNGH2RlZayqos1GZej0H0jtLhKtWqTQl0yISytKJSVqiaM9Sukyu0MWyaiBSNqCQvoHyVdpNyHSFzS'
        b'JgdukzwU2p5w+Rw+SlfEJrsMngrj0IQnVxgxhhasKieNibxGRF7Dfove9ITeo35J4yLzR0a2w3aho0Zhw/ywR4x5q/0vGEfytP8BCYlV5A=='
    ))))
