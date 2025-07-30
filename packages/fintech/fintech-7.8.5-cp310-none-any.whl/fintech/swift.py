
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzVfAlYVEe2cN3bC9DNJrKIgLa40TTNLpsrKsqOCuIuNE0DHdsGexFBXBHZBRUUFRVUEBSQTRA3MlWaZSaZ7BtJJk6SWTJxRk0yiYlJfFV1WwUl+Wfe+9/73tOvL91V'
        b'darOfk5Vne7PwFP/ePg1D7/0s/AjHawGmWA1k86ks3vAalbFa+Cn8xoZnV06XyUoBJuB3mkNqxKmCwqZ3YzKTMUWMgxIFyYCiz1Ssx9UosQVUYuSJBuz040alSQ7Q2LI'
        b'UkmW5BmysrWSRWqtQaXMkuQolBsUmSpvkSgpS61/NDZdlaHWqvSSDKNWaVBna/USQzYeqtOrJKY5VXo9BtN7i5Ruw9CX4NcE/BITErT4UQyKmWK2mFfMLxYUC4vNis2L'
        b'LYpFxeJiy2KrYutim2Lb4jHFdsVji+2LHYodi52KxxU7F48vdil2LXbLmEAJN982oQQUgm0T8y0KJhSCFaBgYiFgwPYJ2ycmDnufCywypbx45XBuMvg1Br/GEnT4lKOJ'
        b'QGoerzHH75P0LDAXEUxTNX9yDAPGafitAHahI6gclSbELkUlqDJBiioD0eGo5UvkQjA9go8GUTXaL2WMhGrYj87AXfqoOLQPVcShCgaItsGOKBZ2jkddSuYpsdo9QiSZ'
        b'8IXBnPl/8CXDzkQ/U8LD9LOYfobSz1Kame1s4rD3uUTo/xL9Szn6j/oLgWS8MxZaqmW5mRbQRrkNC35ca0WYYvlxkjfXeGKKOfBKmIzbUjVFsQFc45YCAcixdcTqmhrb'
        b'EJIPWoFGhJsjec78b+zAvLtjQ8U32T6/w7N2MhoL3HFmRx3TOfFVER7v/5H/mgV2gDabrfvKpmbDLDd2yS3m55XF6xRgCBi9CXN3WztjQZT7LPXwQGU+kXJUBluTPAyo'
        b'PDoOVXl5R8mj4xigtbGYDa/CZ7lt9ojsEMJtwmmQwXvMT+Zf4mfGaPx8PPFjfoo5fppNtAauAIzznTYn+HczpnNUCFEtPI7JqJDFbEA7UQUqjV0aGeUVtRz4xyQ6wJok'
        b'WA5rQabADJ1E9auMThgENcGTiwJgP54fNqHrsBVsQr2w3UgWTfNcGwB7SU/hdngcbEBX8o32BKYb9XsF+ON3i1EjPASU6EIS7VgGG2E72gN70EEBAN7AG5bJKLYHnMQA'
        b'DzD3zXhvwqlNKzmZOtqMBVPwX9/4wRULDdZAXbR3DU+vwC2T9xi/TP1r6nMZsYpXMrw/lSoiFX9LtVNmZWjSbqdGK36fIQV77aIVUtt4RbuqhTk3NvOv6dGKNeCAMlKR'
        b'rTrAL2vqPOs7f1WF1FWSHPb1/Bfim60XVQ/8xrJeDhbdc3hVMEnKGlwJE2HpbHEMqpDGwcMWRrknljwLHGAx39wr1DAeD3BFteggKs9EnagMVaEKHuCHMrAL7l8mZYZY'
        b'D6mUpyOCGfZg8eMHx1kZuux8lVaSwfk9b32uOsMwZ0hEnVpKusKgIuP0lvhh6W7J2DLmjAd+6YSPppDyhgSbFRqjasgsJUVn1KakDIlTUpQalUJrzElJeWZdKaMjqqIT'
        b'kAeZZTKZn8jE9hMhyzJChjz5jPBn8uT8yUW0f4Ys0sszHlYmRKlgrVeUADiiXXxnNLBwkZIdpon8UVQcO5XHKs5Sl8HDKs5SFedRtWa38xKHvR/NZTyafKSKC+Op+q1B'
        b'fXA/OojNQA7g+eVyeMjPSNwaLGbXoIPY7HwAPML3WYm6aHOYm86kdvAS2umNaiPUJ/3f5emJYcxFB79MXf18NXQdVwd7q1sPthZ2lUwvGiiMqmdeyiCaZplxK5YHDrWY'
        b'O56dIWUMzmSdU6lSWbQclUTFzg+IFwAx7GLRcdiTY5LQaKKnAhgSc3LO0GQrDFTQRN0tPflYxFjIosdC5lOhDQnSVWlqg44M0hEvJWWHCZbVkaAxTLoEXPZYuu+NIl0S'
        b'E+fCMtj/SLqbk2mQ8WKAy0Y+3D83ktrfXd1YJpAFHreC2qat9k9iOdsugxdm6Q1BvnzApq2dBlCzejYdPdvGnglhwbhbQa94uC68wDdiZwwKUDk8RUYzgFXBvgKAWiei'
        b'Ejo+KtKJmcWCkFtBFTNXBmwWGB1w48Ix8AIZzgNsJtw7H6Dz62ElHT4U7czMw0y5NcdyRnBmzgw6PbqajGr0hmCCjNYV9gF0LgwW0fHHF41nFrJAgscnRYgWmZzZIKqD'
        b'+wkAC9hsVP8cXsAcHqcAEVo3JpIFthjAc9GaqRspwHoVPKhHvTMI/rDQF14HqMcIWzgC5k1kYlngiwEmKxfniIxEJ1ArPAIrKIgAg+yB+1wA6nVHZyhIuUHCLMFxHoPE'
        b'P+9xdAIlIh/Woi69jq6RjZpRBUBtE9bR8aVKdyaJSGDOK3bWBQXeFCd4YU4mxsKPEA1rsT89gJHavJQChLNTmZVECHNuBwn1QwLjONwoR1dVFAATDQ/BvagBo4RwICQQ'
        b'n02czqwlYpjTtoxvez2eW2IQNY3X6wPIEjtgBcJkd9jAoxTgTqSUSSWCCLWUi6f6u9ElFkZjmyJLYMHBo9gBdgN0CR4UU4j5E2TYDYB5t0Ir5j+/OsjeSDwnPIpNpZXC'
        b'mGGYY4tgJ0ADqAQe4mCEciaLiC9UwxznvRTGia8Xda9BPXpLEaYEXUQ1BUygC2qmAF+H+DAaFqRigMhAq7uAqhO66JYo1lFdhc2oVg5QvySKDq+18mVyiLRDvfRFUfWJ'
        b'VLe165Ri1DWDDEcVAbCE4bGedHRDqD+DDXXJrdA2/zOuL3vTyWG/wVcs8idiQ4cWo2bGwgD7qUTtPHzEqI8KCBUFwAMMgy7AEo6EK6jNW496cq0JCY2wENUysmhrru9c'
        b'uLfewgp1khkHZbCMCcI+uIJOCUtQh1G8yYj6AO7sypEwU13hNYrHSnR5pV6sMxCoOnhQx0xwgC3chDVec/UG1C8mXZXosDsjg5dhE8eabkt4RW9thVnJE7irmNnwGtrH'
        b'WXjbDDvcYc0AnsVKrCbztqED3HR98Kgb7tlE6LpUgFoYb3gMlXNAu2OkYqscWMEHvMnh5sy8FHidagbWi+N6ot3YHHJwBlEDUDtqQmWcteyGNegiNvhAIWAz0GU0QAzo'
        b'GhqkKGYucCU6SOyoMAAewShPQxdMdjx3qR51oR4bwsWOrAVMIKqEJiyPoBPWetRn6jwXgk4xAdsnSW04nzYlkNlCjDZU4/dC+Hxz2uikDGYKWJCDFTTNINeP4xJyHMl3'
        b'ElsN9ZIr3I4LaWOBRRizhwWReOSkv8R/lEcbN3vMYkqIlYZajnl5iV7A+au1c5kKFmTdCo0dFzHejGssDpjHVBPzDI1dkDdBy2VqbzsvYGpYsBI3qtPFRgNtXKmKYOqI'
        b'WYZaxoxzn2JGG8Wpi5l6Fmy5FXrb57o02JY2SldGMQ3EHmdYqpon/2MGbfyzJpZpIeYzQxPrn1/jRxtdlAlMGzGRGbFWXbOnedHG5duXMp3EEGbcdi7hfTWRNorYRKaX'
        b'6PsMzfzCmF0WnAruwblgs14sIpphOSOQmYc/76aSCpuJ2sQ6ayusS2PQbtSLtemMgJPwsRB0GPWg/lw9j2i1EyrCSngI7eFkVQ1L4GFsDthhEh2tMZ/PuAenS/kUiw8V'
        b'LzD1PEzuTEunIzafz6KNnaKXmQYc228Fa5xXbuzYQhsB77fMGR72MMEau9dSgmNp403Zq0wLD/Mg+BWXeQ6XMp9Jyi0eJRYLAXi0MXyy/QEZFo8TdP5/LkG3Nb1GZi+z'
        b'440TCQbo9CpYnoA3a1WoNCrOG5X6oKMQi9cxlT99LJcWTxzPgjNB5F2q5mjQEi4tnqCwAObbp5L9j6VZ/ExA+QwvT4QtMT4xaF8CztLM0Z4cuJfNQ81Tud4z2O/vhz2w'
        b'F6fr2/wBswrANtgJ62jvZNiC9sk8cHpb4oPTGEt4bXYmzwYOeHDZVDfqxjGtB+MfZuMCwlyzdYR5FBX3uQJwdYkt2XVp4uau5RrvYWO219GdnNc6KQvoLLFLMgN8p6vJ'
        b'fAeAAuNxwUhSe9Q5Ce2PoblzVVQE2bjGwCqfKNjuwQCJQWAN69AA9S9WaC9qCgicAdvJFDUgDe1V0TxGDUuiZHhLRre8eH8WxU9HRWCslIcqNOgY55tKcCQK8EcNCQQW'
        b'b0dgpZTzgWXolCoAdsP+ArKJOQk0qCqIgmxahfYGBMCKuQTiBMjE+/BqmnOGLY8NCECXsnAKDRvBc+ggPGcke1p0Ps02IMiNCBnWgfTIYKMrlUrqtphoglc8JxjrHNSB'
        b'SnghOYjbQbnDndYBQclJZPkjQAWr4BUaHdfZoH0xsRjIB1XKGCBGhzesxo7OAZZJWcrPSRGoNCAIHbRnSSgFGZE8incUSc9w+2UbguAxkJkDe6ilxWGNsI9C5XgzEycA'
        b'/AkMPIU3qkcp7sst3DDI7hnYPmA9yJqz3uhCfewsVCsjokCl8bCdDyzHo4bZPBsJbDQFEFg7JgD2wV5KaQNmXsN66vJR5XLnLAUqj40mGyIeus7gMNEEy4zxpLMD50/6'
        b'2KioOHKigTei3C7Uw1vqGectlbMi2KTCsboZnvHwgMWoC7Y6yqQ4SpyR2cMaRwd0xgmeZQEss7eFDVlTNfcfPnzoahSAPRFjqRZarcg3hf4jsN1f6CSLl0fyAX8eA8+h'
        b'1glSe8r1PBBsj/borXRG4pNOMJPnhnCx6jwqHT8PO7Aea66rj5GiBpyjEPdnFrEENUpRjwnqOiPDCcx+upbSIxuWzNVjIOrEmIlwAJ3ksGiGu9XPWek3GUUkg7zCSOAR'
        b'U4p1Ae5Dx9zjcaTKRb0CknEwk5ZG0L6AJJzpnE7DWQLqtSJTdjH+sEFDZ7Rw3jwZHRNbi2EV9rarmTXYNk9SBB3g/pXwAqrTG0S5JOG5xriGolba5YmNAR5yIT1kpV2M'
        b'BLvkbrqWo3gzNrJq1GPQoV6SvV1nXFClkHMbR7CnbtGjboMQFcF+wGBTQFUSrFKEi+tX+8yF+8TmVnjDwQtmImETj0vKT2zJzycJ5yZLgvtRZjpqxOpO2XEGb5TrzHRi'
        b'a0vsfHkzmagw1MgBteQmo8s4N+2x0eHUiGfNBMOy5RRoFU4nm8ak4x7UTSKMOxO+OYMCJQbDa3PRUf0muhLsYyZgQvZwKw1mJWK6SvUiTlwHGImTges56rcFnUdVYtrD'
        b's2N84U7OpnRwdww6iA3HaxUcAF7oeB61RdSCM+BBWG4j2rSZQf3YgfBRBwMrp3py3qUau62BafInNC2cxMXLQ15YCMrhyjQV1VLWrUpxgYcjhuFmq6QKKMBZTAnc7ztc'
        b'y2CRyfXMQR1LhT7DtMzXRsrnwuh+2DsuTTlChrBoG6fTnR5wNyfCk/C0SYRjsQiJgIWoDMcg1I/Dr1EQngX48DIDd03GOSc5AECH4Xm4D5bnoj5LWMqH9YGY8hIGHkHX'
        b'4EUc6+LpAh7wOBbrBVQ9TCcxy6o4HuyHTSGocfkwzWPRbtq1fh6mrChsmLbixK9eyqXC8Dqsgw3TUIdYZIG6sZjCmMWoyIwyHIO1hs3n6U1sPcRM8s7nEvK9kXOxAdQM'
        b'M+y8UMo6dH6stVYoNqcSFzHe6Hw+56lO+6JDeCPcjHosOZgOZjqA+7jU5STeYpRiU76CddlSR3qbmOm+WBoE1Bq2e+NUs0pvjfpo6n2SmQILYSmljbWDVZNhL7ZtsQXJ'
        b'17uZIHRKx1HWHIPOs6hErMOzX+RTGXtP3sYZQTvqcoKnnYbZ1FVsppS2TmHCIlgnRhctNgkBbzoTOh2ephN6wGPLYCnaR7twZubBhGH2N1EkNwZboE54TQ8rc7iNQwd2'
        b'aKfgIO30x6Rdhi3wHEYzB8cLFpUy0/jokJEcHiSmLcKKcRBWbUY1sBKzqD0I79ZqcS53EB1awYDJ62E93Mt3yENXaAzRzcXkHDQDwBddWgZ8lyYbabA9iHbZYYjDWJVK'
        b'npqpBrdW4xW68d8anIv047ZqPK7YYttSdA43tsDzWc9hVz8AGyywJzoAL3IMbIVVUzERfcO5WxBKRbYdVuegVnRhBHNRO473LCfvXfAa5lU1tv4njMyAbRz3O1HvpGWw'
        b'Zzgj9y00LsVdC6ckilFlDI6FkXHeNHLJUGVctHwZKklI9PCOi8bBDlVGSZMjcQayjEykXwH0DuQ4td3edKyKquYAW1hrZwlrIOfzctC5dJXVCKsNhO1c4nAWnd/+2DKx'
        b'Jl4w2eZcbD3U5Cu2s5vI2cQT0cGd8BSmk/Bh3ZbVMd5yz2iCcwcf2CTno0KeBu0SUYe22BleJ2G3kksuzFHdzDwWI9iSQYFnwcvuOI+M9IpOkAtx6tEYH4NtCVZHchY9'
        b'sDwSwx4fZn7oZBDnL3odUJ8sOi5GThaOF8ALKmAHT/Ag9vnPqfMPvSPQX8HpyvZvfdclzU5wCLe/FtDz4A8ffld66vlTDSUeZe4eJRNfe+H1Bj/Hvtc/nvfKtLrvfN9/'
        b'5caNs5uU//QcO7ZsnZ3MZY1y6vHB539/cl646osjH+zyuPnK7Xr9ax8/uHgs+VCrz3sTnN+84T5t8u3vd/amOo+NSb6Tw4qHtFXS0/V9zSHf1F30uaj+ujhTcFj/xrU7'
        b'/yx7+YtND178VrzCvzXC+27Qb0TZN+WJq/+8+/R8xRHV6gdZNXttOsK8nte/83W02dqY9Nx1si3t/a1f20fyXhIXB85+Mxr+Q1bPK30/v/Jr/j/ubDoRy4+/UVj3x2Cn'
        b'U50T9xRf/zrnt1tDrD4/uGDvLP+rcR+/dqnK9a0XOn886v7piVcNb685yfzw6hevOZa0p+a+5h7WGTk+Y1LVF6klbdPlRt/Y1VYfuq4r+PiTmy9/Nqnx0HOl9qEJL57a'
        b'oZ1p6Igr+MOe2Oakuy2fVki/1CV/Wrq2zXPsOIvXun0u81YPzH79j0EOuV9O2rzpi+drwswu8wteOT31u5+7dzxUr9n1ql9zUsjf13qWXTnmuPJrgSHs26A3P2izj03+'
        b'88trv7n5brRnlXramNkbS04bx2wQfWn37p+susJnXdvwneyKYIfDlc+d+yc+1/H3wP2Dx30P7/Dujo5vPnCop+TCl9HeD7of7Mk0Chw67lqN3dX6t5f8m8+db3nvxPkD'
        b'/jPcMlQG2/W/eeetee9thYGGwtNT5s15cOvPdmtevrNaJZrjstatce0PrW65PRe2uIa+t+XQ6bVDHdr4ecF3DHOrDEsbP3Tl5761/EunS0M71q5c+dmVpSU341dN7nL7'
        b'KKE0Ozy4vN5P/KWuJP/Tyvv9x3y+DNr8edCgZ9xbvQbx8ro5n3cdLZ79uvyb6zfFpe1vtdz53W6l3+C2N77nbX6ja/1r5X6e6YNmr5kVfHjPZv+Vh4Vnps56MBiecPfN'
        b'fX//vVvmQ+bb3OM/KZ3uXWP/3nD6NY/8B07nzk/8mzpSamUgqfFmshsp94rHiSuq8sLp+SScDGOn3jEumPaLgmG1zDvKy1PqjftR6SwctsZJ+OthkzU9ON6hQ+XoUA5+'
        b'DL80kOMgTSN23VzYJ/PG2XGpF4MabIAQ7mPl3usNNF1L2Rrj5RGJ7QsbLg7P9dPZPHgs3EAPW6PyYqLiPOPM0Cm0Ewj5rDn2oZcMZLOZYo0xivTyxFOiUmy+VbwNqBmM'
        b'nclDx8iOwUDjahPa/VxMgpzB6VorYDcz4esdKUJ+sASdlXlLUZkXwAn5LoxQGxsQEkU7lbZSVB7nFYX2ATxzIRAGstboEtxNGWG3MTGGXDfFRJEsHzMKng5OZ9GxQFRP'
        b'GSHdAjtlniZSgcVM1I3OsPDkXDW9fTGG+sdgD4U9rTzaK0oATxqAHbrEQ8WJsFBq+/Tp+n/1IbX492CenObbcaf5Bp1Cq1dwF9T0UP8WUYX55oyQsWcsGXNWxFgz9vgp'
        b'4pkzdow5bsOtjIi+bOn/R5/M6Xtr1vSZFZqxjPChJf7syNiy5iyf4QvJrZAjnkFI52d3WjOOrDVus2f4fNz/+D/pf/TEf7+ys7XGc/IxpDVjTVfDq7MT8NOOpS88C+kl'
        b'69myQmYc7rEnvQx/Jx6Le61/FvExVTvBLv4POstHvJDyhiyHs2DYdcW/x1kpo7N6xFs6/QJgusxwHRzlMkNG87vFmWgXVlLuPsNHineesvhYb07XZUKwGLaZ4bh7BvZK'
        b'GZoRwsK1DjFRXlF4bwiituINqrnVM+dDBAt6dBML6PkQuR4Hz16QZ1g9Pidi/6Vzokwp758b8eQiybB/S4gO6SWKkRUNtEwiL0cliUsKDfSVZOvoG3/vEaAjPkQZJDqV'
        b'wajTkrk0ar2BTJGm0G6QKJTKbKPWINEbFAbVRpXWoJfkZqmVWRKFToVhcnQqPW5UpY+YTqGXGPVGhUaSrqZiVejUKr23JFyjz5YoNBpJYsSScEmGWqVJ19N5VFuwDijx'
        b'LGSMZsRU9LqSG6XM1m5W6fAoUshh1KqV2ekqjJdOrc3U/wpt4U+wyJNkYdRIBUlGtkaTnYshyQRGJSZdFfbLU8gxD9NVuhSdKkOlU2mVqjDTuhKPcGMGxj1Trzf15Uuf'
        b'gnwWBssjNTU+W6tKTZV4zFflGzN/EZiIgJD5ZL35uEWjUhvyFVmap0ebZPVkcEy21pCtNW7cqNI9PRa3pql0w+nQE0RGH5ym0CgwBSnZOSptGGUnBtBmKDDj9QpNevbI'
        b'8SZkNnK4LFQp1RuxKmBKCaNGG6o06giH8p5gswKdydIZtaOOJvfcYfSJ5zQqs/AwPf5k3PhLWCs12XrVI7QjtOn/B1BOy87eoEo34TxCX5KxPRhUWkqDJFOVhmcz/O+m'
        b'RZtt+BdI2Zyty8T+Rbfhfyk1euPGFKVOla426EejJZHYjWSx0aBXZunUGZgsiQ/ndSXZWk3e/yhNJieg1lIrJY5CYiJNpR2NLFon8CtUzVdpFHoDBf+/QdTwhCLscTgb'
        b'Hose+7ucbL3h6QlMmqHSK3XqHALyS56byFqlTvsFjEnkMigeKdcKHLnwUhrNL2iYadEn6jhyrV9WzX+b7zoVjqLY6MIk2MvgkcvQVeWGNG6B0cYTX4SJT9mgGiaqRwhh'
        b'FmjQVb1epfk1UAMO8L/ARNM8ZMToyD4TcWOM2nSVdvSIaVoWx8hRYvXIhfGYX5sjc/PIuLuYSBudyTDosafKwEkM6R4NMEeHBYB9nmL0dZeYulVaebzO+5ewH7H2M3iP'
        b'Hv9NivBUDjAC+BfzAQ5WjZceHTBqfnj8L6tdSrZOnanWEpV61ockmPrSqEJiA5Ys0qk2puf+oq0Pn/lfUGhu+L/pTLIUONqM6vIWq9LQVWzWo/iE/wHEiBlQOyN+bgRe'
        b'Sbjn141Nq9ioeuLtTHmxxCMeN4+qp0ZdDs2LnoFIVulyVdp0Ypb5uSrlhtGg9aocRdjwxBpPMCyrHwVijVa7LkyyXLtBm52rfZJ1pw/fByjS03FDrtqQRZJ0tY5kqSqd'
        b'WilRp/9ahh+Gt9KKjcRtYpySsp6q7x4JGGba54ThfcFokWHk6BEX82QzaQ2evphP5OoxZq/mgefzadGxV2xMOHepnefPB1nT7Wh9sX3kdMBtIq9Ptoc9ePM7E1XCQ/hZ'
        b'tpYO/oZvBj73mUhrmb8OdAL02kJBrjtJUSzau4TeQvuhFqMEdzg4jZORDStqhMdHbFonTRSMHwNrpZb0qjwd1SWicp/oKDks83lyyAr88NqVsFcoQ2eN9Bh2zEbYKUPF'
        b'84eN4U5h4WV4gDuorcf/9z11MR2Pqngh6JKWO3++BI+iJnoDvR0eNl1CkxtoRzhAD4ndklAXKidnMzPF0XIWmKMBFpbBvlDjJNwbkmlBZo8SbUAVMXhDjqp8IlElD0y0'
        b'46M6WAIv0QqIKcvm01HcmAS0L38cKiUVCFNkglnTZ9EKeAnszB4xiJYKxMcxAHXMlMKrAoxng9FIqlnRPljtN2wsHlgOj8E2nyg8ekqqYF7+LMrvDSl2Mm/MtN0FeD7v'
        b'6DhU6iUVAhd0jA9P4zkuUhZtQ8dQNx1WmRAVh8rIEHjNysmB77vQk04DjznbU7kFLXtGaqgVnaMa4rDeLwBrjg6eA/AwSId16BrlLzobmSiD+9CuZ4QUuYRTrZPJiwP8'
        b'BSAJNZB7/CzYLqL3LBud4CB3zxLqCXyVaA890Y+DfcFPiVMNL/JCJBO41XpQITpDpRmGdg2TJjyzRcrSY/2FqH1pAOzOEaJGJWBiAexALaieO/E/kwPLcR9+V44uknKI'
        b'DfDANFojEI46URGnBvB03hM9QM0TpEJ6bzUTnoUXAgJyeLArHDAxALbDq1u4a7xB1CAOCECdAv18wCwDsNcxhIK4bEeDAQE6HuzNBUwCgBdQs6nkgI/2wx4M0i2wmQ2Y'
        b'ZAD7VsAyyq4oWLgtIIABSaEAnsL4lcAS7uKvzU0fECAA6IAdgKeBxmCqDr0pcQQNO1KIhc7awDoDroajDZ5L1TMARPhZgYhlaDcdet7RFtzNjgAgJ9Xyu2R/IOVx1dEH'
        b'4CVaToEqfbai8kc3KaQic+94roCiCRXpRl7DoLM7eJpZiKvbc/NFV8gRlABshef5fAaeRBXJUq7KVqZH/YRrqNbJxLUGHgUyQwOwj3ItBFZxbAvNNroDWp1XNYeqv6pg'
        b'FKsrgJ0mUVuhC7CNMBjtR7s5DsMzaXTZxegKPEcZHJ7IMVhkQQ06IggeH2mr7i5PbDUMtlJuCycvIkKAlVoqBXQFHadGbLkD9Y9uxCtRA2fEkaiNYpCjnEbkBbvxBERg'
        b'qBYWUXPzmQpbnjLuePPHpu3kzol7cPuqgAA+Kew5Sep5svwEFP3FmfBkTJTcTRPvjU3Zw3QEDlxgMR82YYlV0tvBZTx4ntSjSOEJD3kUH1iYsdhEr3OluBUCG5A6eRY2'
        b'vFTL5/VRnE8PnQG7ORFOg0eoCL2WcRZX4wD3PLpjmzhcOcoTuNKK3gKRLFoeI/eMJ9/UscmExzfzVOGojPr6pbBzKq2K4odiQrmqKMwwUoXjEsvHqtcDT1OfF+u82FQ9'
        b'BQ/CwlHqp4oXUAk4YkM9xXkIuG949IAdcLenUgDPo72wiSt3KIFX0BFaSmaJjpiqydg8eMGcix2tsmjZDGZExRVXbmWNujm974DXYfWj8p+FsJurAIIVqNDoSfqxE1z8'
        b'+P4RlmI1RWWx5CIkhrDCHx5GF/KFUc5oJ5XKBKdl9DYSVm/kLiTJbaQWRzIapyr5SVyNUgXqfVSnNJtng6rhIDZUeo1/DR3EvsxU+YTK4FVa/ZS7hM4uRRWraelbHUaE'
        b'K3/L5NnYe9MAZcuDe54q0WMBdqVtpEQvfSstGkHH1Gi/GOcAiagI7gKJS0OwmdmQeM0uo77EHh4HETP8Oa9+IB0P1glB9iLMSJwFxAup5xk3E/ZzX2RwnQHk0xFXYF41'
        b'Fz8LppBCv1ifyT5cXZPLVqz8B9FhM7AKngHYB6QsgVe5i/GdsG4e7PHlARzqKwBsAdmwFLZRMoPQtQJ00MY6Ejuti6jWDGBlTYID6+ntNmq2CRlxvU0MpCoeVSaikijc'
        b'7oNKl5CL7kjulnvpEtjtm7gs0gt1TSY1XNiYYpYvQZV8ANusbBNWoFZODS46o9Mj3Z8KXeBpUCVXs/nRLDG4OsMLczk11i9jGUh6JK8W7Agbsch94EXYRU1HmMJ65uqo'
        b'djr6eo6cMxzu5WlgA7pMF10P98PDnG7pEoeZHWrx5Youd8CSp6N6CzxPwjr2gjspYmOCLUFBoh8AS1I1DUnTAPUgqG5MPgVshUXPpg2wxcxIvkeHOmHPdv1wNknilmEW'
        b'ka+Necs9sIJ5mureEgmPS7ySI4lyUQ1eGun1FDcHt47Bsq4dR4vc5m8TAC+tAy1y83EOB9QpzsFW3/qMhsJrjkRBYbsCqyItFtiJ3ehp2BOIw/tOD8AsxQHFCe7nontj'
        b'uIr0MJjv12lA6RBhtx2Au5LQIWzlByFWgv34bc3wEo6J7rBDALvTlhnS4MUZDGa5cBXqjqNTJmFfUsHNOejHTTkGHaTauy4TB3OChyCVQwMdRvulfNM3S+blBwRt4q21'
        b'AEw0SUCqsfLSCtSOtQkBgUKwBTaRLEol2E7H28KKWQGBmxnYBgcBMw/AVjsxZwgVmfAMXgV1AtjkSeNYNzqYIWW4Mo/zGIW9uBujhidkFuGMxltmJDXA6Hi2EhsCjub7'
        b'sMhQVSLqtIJdgX5LHmv+MnkyLI1f9rSosFc9KUJH0RkcSWgc2qf3hueF2HrhwXxQgHu6OEH0h6BeeD6IfFGoA+8BWEeAzo3XUh8g27oAnhcAsF2GLoPt02Cz0ZcGElJU'
        b'pKdfPVvmQW5wiY+Xwc4VIxBYITfDseUCOmCcSRk2HtaK4+NQpTzZpH2odEVk9PLIJI4i2IoNOk7uHZ+7LTZBQKpNOkWwCO1GJEegBNQu9eO+LIV2oWrgDatklHlqbCUd'
        b'WCXaBSAN9gJ0BMDzeX4YaDxNLAZgxUjrtOZj4zw2nxp2trUdZ5lL0LlhpulioL2rUDHcRSoe+6wYLNoiFvUzgdh3F1LGJcMTsNxU7BICG7h6l8rZtBJZ7Wr3G1Z/E7/N'
        b'u2i9LSmmyiXCtmP7+wF9L36b79a9aeer2m6L6j3P7128JWTWoY9tJfwpZyQL3Td5dElieBPQV3+77lsWmOO/+3SRZsqZ+pBNt16xulEkdor/6L6g/vvLL1yxcC9dlJj4'
        b'U5zxneDlnxgUzYGnfV4Jykv7StSf8ac4RZBa09GWtyapXp7U0VNYtDloxR/CZi4PgG91rnfPrndzc+vb+VxQwIx3P3C5a+XSF7Dtg/tlF354afmA/+sfTD3b3X7qz/Yr'
        b'ttbIIvY1v9u66q5788OUD2+8MeXeS0ftdDdeuneovHPw3bNd0Q+ZZLNvnYPX9i74oNh7/p9eiF33bknUD/wPa14aTF/xxcPSdfKFKQ5t8vfvPO+486fkG6lvKi6f27rr'
        b'4N/G+FgbOv6YOzD2dffdFwZcflx773rp/jtXeFd2VFc8mPrZjNQebczz2+1u70z9hP1y153XdrvZ33ZJzWUfLO+8wn9g9/7HvNnJH1TdsfMJ2NZ+v/rt5VeXvSvo9ryv'
        b'6Fp8o6N0tmfftG/r3t964w+yoDEf2m89+f5naQkls51vBxWV3zlZd6fW5qeVX7zR68/ruf15fdHx7zKbbr9sN26gbsWDG24pMcr7xXevL0wusPokecH0BKvAzsl1MfJZ'
        b'Wyd95vhhV/7D+qzWCZ+unZ3+udnml5TnOq6v2fpN8/k7Ee/8ziIv557Fuy+vf7tz7b3CNwc/mtr9lyA/xYwZ+oULeoaCt/HdAtdNtimw+S7C4qr3J65fH217L0b4lufJ'
        b'vX+wzMl6s//urGmXC2Hj30OyZv5k/XWB+UVD318Dp224tXzp8q/RVy++3qHddqXlclDSOxEVv/3Zo2Tipoy5lx8MeLZt6LHqscln31vceHPc+873q/50dOLJcVfzTiXY'
        b'DWw/+NL0iC7V2sGEL6Z+PvfKscHPX0n44/bVlxbDbWM/OvnBpM6PPMa/VXJS0PET+5xXrPKbmMbou7djGxfdfTdTtDUIpox97uVP7tUX/LTqjS0tH421WfvWti1XpN+/'
        b'dlZ+f82nKbHKnJl/Off7q+1/+fHc+s/qwwcXxccf+0tT7p3fXLj3/a2qZfdSPDbd2Bs7cfJr5VtnT9kepVt1XWK8fvl7de9Wx735f5TrErSv6K+tuD+398fz09Y4JNe5'
        b'/xj0Y/7dVTa3Cz42/1INz957++u83LIw2StXCwfedz37j9q4wfvqt4wfufcKXd7+cHL7tvcWX0i8nPpF4Z9X7viq/1SOw8vG5F3vLQ72WB7fPRC9/6c/lb4w5XLB0kvC'
        b'ay8WuJ6tnPAz+41D+NjwhJq/+mblOX+iXWR2/51b3xX+cFh267Pbzv5vT7+RtbTv5fg/rmt1cQkL0fzUn1Ly/qWbLydcWPr34zuYWbGNZuECqbWBbGdgfw6sMVXBYEdH'
        b'XB1O/vDW5agT7ONHGuAA/QIuPJyHmmWe3tIodIDUpwCLVSxO6RvREVpCkgR7nIZX4hDPlkZKcVCfKy1fQQNpaA9ZBh5dR4tQaLHN9qm0PCU4HTaTapuVeJNrKrjBiXAV'
        b'rKRzoyO+6BhXBoSackyVQLQMaNYcA/lqAtrDh3tlOqsRdTemopsqBV1eDHthkSw+zoufHI32AbzCAJs7D5XTeh50BNUacPZVhhqTfOR4e5XLeltF0bVhuQhdisFIPabL'
        b'xtcDFfEydfAI993UBngYXiNZFDoGLz/OoizDaS+6bolaSEXPCZw5Ea7Rih54LYJW7WwV29KvtaLjsC0q9vEXW9F1zHOSRI3F2X076iFlPbA9x/StaFinc5jF58Eya6n9'
        b'/+/SnFGrRKz+6/M884XcjYbQQF9au1NBikF2gB3mdo/qaES0Fsec1s6wjCWp4GFJnYyIYVmWGe2/6Btza0sKMZ4htTvk/ThaBST8yVxgyXAt3AhSW0PKWdiHtiz7M5/H'
        b'/sTnsz/yBewDvhn7Pd+cvc+3YL/ji9hv+WL2n3xL9hu+Ffs135r9im/D3uPbsnf5Y9g7fDv2H+xYsrb5l9ZOEkaI1+Uztsw4xpZnjfG1xCu44tVcH9rTWiFbVvRQiP8S'
        b'2iwZrvKHVBqJePTzTyIh7fmJLySt40grSyixwxSIBKQaiFBPXnxWiEcIWSE7BX8SmiqbCHdI7ZGItaTvXTEm9rh/PGPN1SQ9ZB+K+JgfP4v4lpS//J3sVyJbsgKpibLE'
        b'89E5WJ3NI4FJeUN8cj48rL7ov64KUkZn+0gZ6FK/I0pAjBDsmtI3StURPXFp2QLrTSVHeANei3rlJFsEYHwOD6dCJbD4me+yE62aR6Ymea2K/JgKWM2mM6t56Wwi/QLZ'
        b'kC098abVQLoInS5b98NE7gycaqjOVNyjSpcotBIV6feOl/KHzFNSyKVBSsqQKCWF+9UU/N4yJWWTUaEx9ZilpKRnK1NSOLV/8qA0kwx0iDGdhpsDc5aeQwSNQ5fE1qjf'
        b'ILYgZMp1ck/YjHcTxOB90EmhQAqbpMwidST/EKuPwODZY4/Mfv3leORrL1gyM/7DS4lhZ6xUJ15kVScaK1SeLo4/Pr/c9twNtnt+2gL3D8LTbvat+fngYfdJMYu3J7xX'
        b'/mXCl+2NG4+LQrYsvvruZzMrxp9e9c2f//aJZcAfvvC0C/f5S8/DtW8qIgcskwP+sLRj8vrxc4ot75vtSH3tQM/9rPeCq623XP1pq0tTTVKfZz7rnL5AZncpMWrqbF7e'
        b'+40Vr0zfy5Z94jq1JsrMoVt0+PaCytsvgtCSSbpxkz/3eOGlTbHVB+vcz/ot+H3avvoX2VUvug/sUXXvctA5bFj5ojCoq2jj7VSnre+/yFhv2jNt35VvbapC4nPK1vkG'
        b'1H92asOivWllssLxn7csCD/y23tTVl86M8Fi3ZvqdW84P6f7502pdPkilfTI2bYGzfza2tNrfYo3fLQn+UfZndjDqy37s4otN6bw3W+N4V3J/Oqe05W3Ne1Xp0r5BgfT'
        b'ZhIemJSB9x4MYELwpgJ1MgZyBuOJ+mEb97sURiyRmvFPfpfCWkijJ7rkjFrEnqR6EoedqfK4Rz9eMRH28HEQbU+innxNNKzWw/ZIWIxOx8sfn4uNQdU82Ckxx1ZBjcPu'
        b'v9GNC2kO/8sP6p6xemuyFekpKdQ378YP1pFlAxkJ8RgPiY8wZ21ZW3NWSDzoMy/iUZ9+EQ/79It4XPwS8kXUb5l/j50d9eTCB67mYAdrYcl4MCQqsDaOjM5pmEdisVk9'
        b'8Udj/ntYxejGPbZXWgsMTHWR3rdH8VD01KKTHBXBcnJ6SH5ECJbCKjNg7QxgD88NnkPF6o6HtwX6DDz0eMSnbi/4We+eZ7v3jR0ZuVaGtKa9txqvwhsr2443GaZN3Cq+'
        b'1HpjxbXOJe+0VSVvfZDxqlNK4v3twUUR5/rzvl9+9OcVs3v3+PoX7TsxmTe9PsCpY8qiadqqSbqa7Pc0XVd++IvNzdfHXfqoRGpGFdgvBfbQX5xIoMd+ZkA8HnXBbha1'
        b'xKNzXHK1KzQgJkGOusigBDkLT7hhtbzKg41BG2hyBY+iKhVHGTnZg5WUMju5Hd7T7bOl+RM8YA9ruYpoIHSDjXzWPASdoikOqs2CJTHDfipJnG2QsqganpBTBG1RC+of'
        b'8VNKy+Au8lNKsBQnZ8RZJnjKZNECwMQsn0NONC/JHxnLhP+J7Oc/oT38XzUvtVZtMJkX0ShzK5GpPNmLRxQe7ODHkK/0mhReMsTTqLRDfFKaOiQwGHM0qiE+uYPFoVmt'
        b'xE9SXjjE0xt0Q4K0PINKP8QnFSpDPLXWMCSgP3syJNAptJkYWq3NMRqGeMos3RAvW5c+JMxQawwq/GGjImeIl6/OGRIo9Eq1eoiXpdqCh+DpRWq9Wqs3kJq0IWGOMU2j'
        b'Vg6ZKZRKVY5BP2RJF/Tn7sCHrLjETq3PDgny9RsS67PUGYYUGjiHrIxaZZZCjYNpimqLcsgiJUWPg2sODpVCo9aoV6U/MWmO7Am6IPLejzy8yIO4Wh0xNB35sSPddPIg'
        b'yqmTkgeJoDo5eZAjeB05r9f5kAfZuOiImunIebiO/ACNjrhjnQd5kKM3HTn70U0lj0DykJAHsQsd0V7dDPIIJg/ZY49ApGPxSH6Lvn/WI9ARP5g/+smhIduUFNN7k3P9'
        b'YXzGyJ9hk2izDRLSp0qPl5rriE2RLEKh0WB3R7WBnBUNibAodAY9uewfEmqylQoNlsIyo9ag3qiiKYwu9BELn0o7hsxnccnKHOYR5nzAF5qznM7Zr2FpgvwfvV4x7Q=='
    ))))
