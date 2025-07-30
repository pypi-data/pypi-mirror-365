
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
        b'eJzVfAlcVEfW7+29odm3ZlFsVJBmF3DfRRRkVdG4QwONtCJgL+4LrjSygwugCLiCiqKI4p5UJTOZfJkMBCcik8yXTObNJLPkYeKMSSaZeaeqLtComZm837zf93s9k8s9'
        b't+49dapOnXP+59S9fspZ/ET836/Ww+E4l8mt5NZxKwWZggPcSqFWtN6Ke+mXKbwkYGd6q0yRkNNKLvEtmzmD1SohXJFmigfu2ScAWqYdfEbAbZNYHVBLv82yjp07J1G1'
        b'MS/TlKNV5WWpjNlaVfI2Y3Zermq+LteozchW5WsyNmjWaUOsrVOydYaBezO1WbpcrUGVZcrNMOrycg0qY54qI1ubsUGlyc1UZei1GqNWRbgbQqwzRliIPhL+U5DRvguH'
        b'Qq5QUCgsFBWKCyWF0kJZobzQqtC6UFFoU2hbaFdoX+hQ6FjoVOhc6FLoWuhWqCx0L/Qo9Cz0KhxxnDN7mZVmJ7PcLDPbmsVme7O12dlsY7Yyu5o5s8jsYHY3u5glZjuz'
        b'm1lh9jBLzUKzwOxpHmF2zBoJcyvfNVLIFXkNzNsubytOyO0cOUDDuffAuYDbPXK39xJuzCuubuG2ilZwWwRW69TCxAxLHdnCf85koGKq1m2c2ioxRw7nD2aLuN+G2MFZ'
        b'WvxCoR9nGgen+CE+mIOLcVFS/CJsxqVJalwai0pR29LkYCk3LloMN1zA1ZSB9RYZ91upJ8ep0nJWpCzlTGsIg9vj0TXcbmW7KAbYlMQujUGt/tgctDABVy6R46KYpcC2'
        b'DJcHQhe4LCYBly3zj4nHZYnxSUv9ocEcCh0uilm41D84JjZIgC6K0ZVpnBEVuU5MczdNgB5Qi3w+sB7OA5/D9cC4OHRRTFAcLoGO4/HhWAm3GZVbrUZF6zMEFlNiNzAl'
        b'W+Fw1LYQpoXqSgx6koIe5aA9a9CWDWjUzmyfZUf1BKu3SDyoJyHVk8BCT0ILjQh2C3k9vXB1UE/ZL+pJ8ZKeWpie7ifK5L8VuZNptlmUsZ6jF6fbCKdeF8qp8gyxy9jF'
        b'RTr5WJ1IBdfS4pNcprGLaq1E5Sxy4LjZaTnfJaziWrgca7gcs9BD/MyJ87eSfzLuS+HN8SdcfQQ5xMTXza8RtMk4VZhH7oqWuSWZr3H0ctiSL+2P2Av8+7k9QX4upRlK'
        b'ro8zBUJDuI0baAMm3t8fHw6NCcaHUUuKP6i7PCgkNnhhgoBLR+Zce6sZDrPUoSZXskRK8eEp6N4Egw0oBddw6JgWHTe5kZYDU/EddEdg0EuAKOaQGZ1FZbTJ3wrfRcdw'
        b'i0EvIxw4BN3gDpM7kRgUfx9dQmUGfJMwqeBQCb6KLjOWN1AzOrUdXTegMphZ3MSh+q3ZtClmnBcIWw4NQmg4zaFTqAxfYiIeQKULfP0Nm4gc5dAZ3o/O0hZ0YySs7+bl'
        b'BnxNCm1HOVSx24W2TBiDG/DtCQYTeaaSQ8XoMjKbXIihGLPwTVxpsCVPNHCoFp0ZRyVAB9Gdtfge6jTgdiLcceCWHE65TUZ71+CC1QZUQsQ5yaG6eaiZtihQGy52R5cN'
        b'CiJ2I7DDZZlM6lv4BGoIlRi2gC/HxzhUthadZy1NclBS7W6DPceeqXFD19j83MIVK1ZB/7ZEgFYONaAa9JCKjZpdJy7zUFBdXIJH0AN8nXE7M5JDRyehYlCgQM6hK7gJ'
        b'n6Mt49A1Hb6hMODrRLVVHCpHHfOokvAZdFmLTuGjuN0kYtN9BK49YAzNs3FbdoQCt5G+roIm8IMUKl4i7sTHcCtqMWwRMo6H1fgofWh8xHgd3mfAt4jgtRyqxFX4FpvW'
        b'ZnT8NXxqvsGeV2wdqsfVJiUdO67W41O4GbfLSeNZDp0Yh9sow13p6DJuQTXQRMS4AGJEZ7CnzuILzvg0PNdulLDeyvEZIW1DFbgMXY9GwNFGyh6r16JK9tyV9BH4NMxP'
        b'O13qzWSJVYAaqZC3XXAnuuCJ2/E1MoIzYAchOYzlOXzFD1fHghslj13hUBPah/bTNgf8EJqPREIbP1en8XncwHR5MgWVoHsSaCNT3MahMwFgBnSG2+JRS0gcTD6/Bivx'
        b'vgz2UAO+h6/mToAVIGAPnd6J99EmVSi+Eo1KQcJ20nQR5kqGypmIl3CjxBWdJG0ytnBOrcUFbGQtJIYccQJ18uLXh8HKYQaOytBeXDhBISdNN2GoqG2Eifg9467FPqhT'
        b'ga8Tdh0gxXxreh2Vz47NtVNslrBealHVeMrqNXQeHw1HFxX4Jpm+a9DLRlxhcoKmucHbnMVwnQy1HVZ0yEQ6B/bhqB3tw2ehRcL6aPIOpH3oQWsaN4ORyGTm0CHckkCf'
        b'cMWlu9F9dEthELO5rsnAF+kTM+LwvegkhTXp4jYHopzNNHlS52OzCBVPxBWoA5VI0L1lnAifFiQl4RLaLMN1cah4Mz4CIfWwxAsd4cTZApiQNplpFDTPwx3gkVh7OK5w'
        b'XkS5cFaoVKiU4VNqEZuRQnzHFheDivM4Jb6bFw4GQa8Xg/GeigNR07k1run4LKoyOcL1bFS2LQ4EzeSSjZmwcO/SsY3xRndxbbTFoM+AkH6Ez8OdYIDV2IwuTUQtEk0C'
        b'LIGz66NiYCWfWZnARRok6KjvTjrTvvh0+nwvAzWKIhBsZCxFEYvSXAeevwIWfwSMo5OSkbBujoq5EbhUbJW+hq3MFtSKbu/xMeAbAua8yxbupFzUkTsYF3QTGBA2d3BN'
        b'DLoyyAXdF4v0UuqrFKh20VpcOBRSpoKZESao4LW1A7K0Eibr03hJLjNJqsTSFRBICJNR6mmoSAMul3iGUxw66QpOkjCJw3VgdNUx6DJMCJVk3wzKJZwIBlyCRbgzJ5Ja'
        b'xnIQ7iEqRPUGPVk0hRw6AH6jksbKPbgODGZgZiSApI6Q2UX31itUuBg1L3PmFqpkCjCrg3R6U3JttqZZBMN6rSmETFnNugCL+VWhDnyEUVdxKflzkQgVrJdsQtcgbFFf'
        b'Xisy+AksgucpfMcURnidghBbvQtfGRxeqSidyYTOgLhn16NiUHoM7pTiDgU8RHVW6LzTxwu8PDkvIwvvOj5iGktWMLoopZzwflzFTxZRmXgx54XbRbgtBrMoZg3OATej'
        b'/QZrIdPYUfzAzjQRWubbTLJQe+mg4ni1NScQMS8nSNMTwNmu24SuytHtafZ0lHMdtqLODAM6LGZO7iQqG2MKJULeQftsiVxXqEzozEzCT4SqcBFQh7LAzuq48bhBAgig'
        b'At9mkf6AIBAf1FiAiqkwSDVz6xHD1hRuw5fZwrzIFma1CJzqJS0Vag+qyhPiEoMdGWgdLE1cOpmymQD3nB5uJw2z+FG2sMVZKJYloxLmcdthUZ1RonYLIIOPK03B0KZB'
        b'5UuGGA1NWcxqdGfIXiJ3SFCtTzD1nsmTUcFSQExD2Ac3oTN0rvQi30HjH5x34FCaBAqhGiDMwnG5BDXaoRPMrzcCRDpgRGcsEFPxayZ/6k3Q/m3D7Tg4ZECXbJStYnny'
        b'ejpXaaEjjNEW0ArdxqfYMq23xQcsxApHN5hkwPMyGzG152BwqwY5Ps8C0SlAhvWOQcBQxqL2ERUqpk0b16GDkEJcG0JrAC/3U+uSokPQA98V6BNfTsBHIGBuIysFHVKh'
        b'02CmCfi+LBwCbwGzhxtbk8GCmocQHr6YQZmheitcONyXgmUBmrwpXOk/kU2AATXIIWWpxHVM6mNbRPgkPmGBCUdBYCOqAeXWzh/gBjqVx75g+PwcHJMYYO5OM9mO49ZV'
        b'2kADi9P1wB4d3EPjhTe6n5HsbwEj7ztQL4ULBfjq4Poe9P+R6HiUCldTL5WET8lConEtU34pOirEh9DDIYwWgcuo2rLQdZjZQc+CmuB5Jvqg9ugUhKC7kvXorJpJ3Iru'
        b'z8MPswxbJGwZlKJqCVtLBWoI4Iwd0cyRdRC2LOPKOBG+iy/xwObebvCphydYIMQ4VMD4VOH2YEt/jut2MfttJWy88E0RvoZOiemajFuZhVtcgIuAAfEj9rDoSYNyHYh/'
        b'b6cFytzrS5UeDbZa9oI9Mk+oQW0W9rhJgmpW89D9Bi7A5onJBnsBQ6UnnXAVjca2kyDlHvRcIGrnVkIMRB6RCHR1NZAymYiKtua6WCBbQI2nqavxxntBkOqBtUJczQ2A'
        b'y8Os8IxYptlBB4b3+64LcbeAwbgomrpmfBtVZrxqYPSKGF23ScCdkXPmoVY/wFRH5eBLm1AnW9VF250B27RbIuhrsxhKPgr3HVqbCaGRQgBYi8fW4BN09OtWQwwaDJga'
        b'gCwlzISiVBIuEjVKAPJUL6A9rMZ3slChErA2Ufc5GD7412pTOOm8DT+IsliGA/4W3EMHKqCTQB13BD4hgbVxG91gOUtpLuDTk4Dwh6A9zFqLKYLiUpjEliGXBFxBiXX8'
        b'wqRXRTAhtusnCBZJZJNxPbhXoqT8kdDWKLRICfSQJhIvHonLd+txfRyNb8DkBfuj4GsxKpX5AJi6S4c8AgZ2eClAk3YGm2HQdSkmtsSPo6rQoSHnhtKoTvmQeB6BOkis'
        b'q1/HYkvxIjDN/W643U7GgO4ZmJqTVANGdFhgaSrJ6DxbfxeZqVyDBejiR9dNlmqrmmRWLKhcB1i8ebPJl2YE0STxIiNKxJX85POwYATaB0YbhVrYMjnthM96RuH2TUJm'
        b'beUwtnN0DetQy/Lhgel8oKUloEIRvgPdtFFZfJUQIcGntm+SMrdXke9KEQr4/SvoOB1RlqsFQhEShHIL7H4iKIpoP2UVoIJGyD4tEjTAyAf59LxkWuYoywTtJLg8WgbA'
        b'zU4Q/Y5ZJGg7t7JZPo7bYC0V+FnkZ5NQB6u73bCLG+aQ2vE+5pGusGlug2mea6Bz5AOg5WogqrNI5iIxyw5hxZ/zwffQWWjjTakKHfZjXRTPwId5T0LXqJuEnt8Y8iQ3'
        b'0H4dHYSvABeMRZ3ARcKgRvVsdMo0nqoSVsrRYaiFdyNXUMNmC/g5HtdJ0KnlK5gvbprlGYMfwKg6eEOqxbXr6aqfN2HUMG5s1M24HJyCBbfXJKhioowKF+IDsbYC10PG'
        b'KmSz37g93RQALZMEQyChdSDYRi3E9YOBKzleNgVfxA+ohn3wVXIHSesHc19YQidprN282364x2CIygpdtJi0CPRQgsphSe2niy5hVbwePQRuEpaRnkEHFlNnYQSAdHAY'
        b'O2EGL50DSNYJPvniREdkniBAJ2ZbJ4JFH2X6rI9BB1WwcCxS8FR0lRpmWgwoyGLJLAXRLR26WoRvbVvGLwt0ZwO+6W2ZrS8BH0Lmf8ladMTCrNC+CAvIN4QpTJL8LD73'
        b'h7HcwqdnojpI8KWM20l0NI0uMl/t0mHLuBoVWGRsXvi2CF8P41ETMoehi/Go1qJOkC2jegS4XrBoOGb0SR6eQD4U2+FyVMuSm32oNX0kalPIpSyvP5tsolMkHhM5LGu7'
        b'5MMcxmUmzBURLKQjYSwdBkx2SoFvDhUmcPschvarpwO+fxHCRUVtH1pUQbJJ+Og2Fsj3gxqK9ei0wsiHoerpPlTKHTJNBr5hUeCYB4kGwWExuCQbX00fKibsHMOGdR09'
        b'QA1O4xSbCacWSJHSdlKAho7kQ/i2QKiQgOQPs2XiCx+iInBWhJEzPg/J44EMxWbSwyVwRDodhWfo1oL4V69K1L4Sl+LWhfjAenxmJaffAElWlI7Z8jHIhiCxbBiqybig'
        b'W6YgAkCs11ra8lV0YdA7XJI48UnWZcgbcAOrCoLX3A9i3plrUcVBJfghjdpjIfSftsizIKA/tICNFpku4EMjLAK+sFaHjqDT03UWBSB034ut3KvoFPyvaqlFCQgfcWDD'
        b'ugyr+hou9lfYkRVwj1QRG3ZSVyBEVyEgvsLltVh7DvN4TQBHJqQxs1qRjNrshpRU+pK7lGyaIEiWyyaia68x2F2jTrbMKtsBalBviC5L0kEfCVy4UgKT04TraYTXrIV4'
        b'NJQL4CO6AX/OKhvouliMLwIAJDdLN0FAH5ZqtifygrQygzosluOaOGrEseC4jg4znIM+w6xvmgjfz0qjSsLHtOCLX8oXwQmhkx7DJqdaAtq+hC6r5QxktruiC9kKhR0J'
        b'hQ84dPE1xLK2ragtAB9PVuBrvCU2gVdmdeJA3BSG90+GJvJQJ3GwHW70oSTo9QousFZYCZnyLuAL4MhJESUm2gvXblWY+Pr28VUb6eW4dcrtaO9QZS/WhhpjbNYU6PCO'
        b'wsBb6an4mbTrdAU6r/aFZIa6vPvgY1BDnikSWnJ8wH9DkoPMm6cCAqSlPdTKGyYy01qgGLWnoOKl3GtrpLgB79+qFtPln62GdKU4HnW6LsQlIk6EH4D/R4Xb2QTtSxud'
        b'iEvj8OF4KSdcKwjF59xNXnTmRPhsHC4LxaWOgIHU6KKYs3EQwXSOZSv5zmhcEJiI2jYGx4g58WwBuqhHNzPIvtLAj+zo0M0mIxyOSgf2P49zZgHd/xKaOboHJjIrsqzo'
        b'7pdYyBVJB3e/JHT3S2yx+yWx2OcS75bwu18vXLXcpfykHzRlrbL4RZF9W4NKk0s3bFVZeXrVZk2OLlNn3BYy7MZhRCzbLg7YkJdrzKNbvwEDm8UqHXDbrNHlaNJztEGU'
        b'4QKtfiPfgYE8N4xVuiZ3gyojL1NLN48JV8rPYNo4sCmtycjIM+UaVbmmjelavUqj52/RZqo0hmG8tmhzckKsh12amq/RazaqdNDNVFVKNtuXJhvW6YNcQl71QLouYyoZ'
        b'5jrdZm1uEHuKCDg3NmqYBLrcl0ZEfhkwMdqtRjIErSYjW5UHN+lf2REdm36bZWfGATFhKv/9foxki57nFqJKMBmMZIxk3pckBUeMnzhRNSc+OWaOKvwVTDK1r5TNoM3X'
        b'UMECyFmASgtLw6QxaumOf1pait6kTUsbJu/LvHn52YzTpcWPRbVEl7suR6uKNunzVMmabRu1uUaDao5eq3lBFr3WaNLnGqYO9qjKyx1cpEFwdb4mx0Avk0neojO8MJhh'
        b'O74S7sUdX8fE+SzyX0YnZxk2SVBnFF9Nc9tBN3O/WOnOPdJqyA7vzlvzp3HUZTmSshAqhrMV+Jg1HArW0Jv/sETB+ScBhHFIs7GOFrDt4O9j7Dlz9jSOC0sLmrF8E+OQ'
        b'hk6GGxTCNc58JSgK3VCziipuNORCCz6yfKBIdDCFNZybFm/YIsIdkzm21eiNqpn3uQKx45bBHoJ5FnumBh8Lou5uJj4ADNptxagY3WfeuAGSAlZT3r4TVyn0gKZJVZnu'
        b'Ny7GjSygN+EO3KrIF0FcYinz8cW4hKGtIpiqQ4pNInwiiwH4EzNHs1B/DRdAPlNsIyBZL9umDEZHqOxbHSERajdI0fVMlt1UrWZ7ETGoFrWSzUv0cAarZJUL/dioypFZ'
        b'T7Yu0/EtVu05sn6gwHZ/+Qiyc4nP+bNQcgrVBdBpxfULAPBtEU1yZoHsVJacMpsLsRjyWhjsGXDE+AQpdJZEsH7OQv5w0LBFNnoCq/2VQwhne6uTvGmFbTS6wBfZ8Bl0'
        b'Ry1igifYQxPA8Fq+DRWg/ZThLFy8gHZ1H5cM9FU9c2C7uMkGutqEWvm+UIuUZaqNkFoUkAIkfrCDr0EKkVktZPqoyd1N2pLQZb4N30RNTPxiEP802bTGjVksga9bNoou'
        b'vF9OkXK9GSPJawxBAau8OCbCA3QwICJMnItrgG81l47P4RJd+/4HHC2EKVcv3FV5PxGHOfz0F5vfK/Oae7CmznXsx1Zpn/rUBHxwwqnojaPZxX2l/+vOGO/RoT97Kzbg'
        b'4s6tT7/54vf/2PX916lpdxfteOtmSthk05aGoD/2v7f9WPefUPFnNT5Rd77YfUhm/6eFI8Jzdsz/stPRNiq2ddXd7W6+Ld9mNO213fCTmU473rC97jd21etWHlFvTV41'
        b'JTHlz+8tLbY+1xBw7yexpdf+vm+N/G+RP8tS/ulo260ll43n/276Ha6q9PpL0IPFN8VHlA67NpX/+e7nJ6rfOx52ZV7Tu/Of/WLJLPT3UU0//wSV5vg3ZPz3m8e+2ffb'
        b't666N51sK/jJzIAnsduTZ8Q9/mXGV59eebJjasr9wjSXy5qrN9siNvQG/ON7maRlUW7JCbXsGZ3/qnmoLTDYPyZ4mUrISVGdMFiOTj4jbzRBHnnCLTAkdh2uCwpQh+Dy'
        b'IFzEce4q8drt+MEzukFZjzo845KCUdGWlUkUWigWCXGZHFU/84DmxXNxEXn9JyA4xBtdFAD3fcIIyGmOPiMoMngRoM92/tUb3ILrtrDXbzYHB+DDoUIuBN2X4BvjQykr'
        b'tB8dgluLE4JicRmqAsQmjRTa4Qfxz8hWpys6wAGGiRmjgecRcIynEMgVHxDhTntXtaJP6K/W083ZH3MwkNdoVKqCgd+3rtOz9HnbtbmqLPYiWQgJvzP7rGkwSCXEdotz'
        b'IWFRCSvv6wLuabKEc3HvVY7odVYen1o5tXq6ed4Te6deN4/jukpd9YYK0RPnkY1jL4Q2hbaNfTR6Ur9Q7Orb6+X72Cu42yu4ObPHK6LNcGvbtW2vO72+pGdS7Ptesb1j'
        b'/PtF3IiFgqdyznNMY0Sz7JFHWK+X6onSu9fbp9GncU5NdsWCJ/ZuvZ4+DcG1wSdCK2Sk91mVsxojHzn79yq9+znBuGTBU07gniz4eNTYXleP46mVqY0pj1wDoLXLb2K3'
        b'cmLvS9cbN3Qrx5PLHiMbRtWOalY+8hhP+nVW1ixontk9YgohHF1rxtboGwU1/s0h3Z6TycjdPGvCa+ZUZJsX9Nq71ei67ceRqy4ja9Z1u/g9dgnqdglqTulxCTdHP3Em'
        b'U/XE3qNX6fNYGdStJA3K8C6H8I9d3Gsca5wqYmq2wEPNLs2aNkGzR7dLeIXgidK/2bFHGdhs7FZGdDlEfN0PYWqE32OvCd1eE77kBK6+T0aN7RfB328NZCf77th5E7k3'
        b'J9pHy0VvyQRwJPuZnNqmT0yU1ycCpNQn43FHn5gAhT5ZaqrelJua2qdITc3I0WpyTflw5Z+vIRsSEuE3sI70JGjoaZCyWCvHyK1T4PBdAfdcJxYI/J5xcPjETlm8oUDR'
        b'L5QIXJ4onIqnfCK2P5DQK7d/Inf++qmEkzgMUN8aiF88IQ3kLikmisCTE3CPmp3w/TiwBVyciMts8YWkWAlnly+anB/FwP8ZcM7lcfHQiC/thhQgUMApVgrxlR0zaVrj'
        b'p8Y1MbuGkoYFMRkDL3aSn3gAc2QT4C9kwJ/Cfg5AvzRLTMG+CMD+IHTfJaZgX2QB9sUWsF60W8yD/ReuWr7q9kmv4EWwT1/NtED7+ryNKs0APh+OxIej7hdQdco/Af96'
        b'7SaTTs8gX75WDwnARoZNB94XHY7OkgZAGwgSsBh61G3URuv1efoAykwDLZmvxvREXiIuw/UvDuKVgJYfFHvixRG+qguSBczP0axT6VgukpGn12sN+Xm5mQBeaTJgyM4z'
        b'5WQScMtwKs1K+Ezk1TA2WkeGPISaIUPSqMKDjaZ8QMM8NqazBqDen9wRRDpS/yhQK0k0zaQLdw55QZMPHqgOdwy+u2nGRfEBC4PQxRT2Cie5kBQfmyDg0CVUpJgiQBUp'
        b'OsFnrWLDQmD0bP5nJ94Jr2+q7qjZduTugUqB9WL316KeJJTUX17xro17Y/XtavVB3YQUv0NFe5uONR27Vn3OfO5Q06HxpeqapkM+NXsjRnKh22zuHv6pWviM7gjsx2fn'
        b'KQLAlCColSSYSDDDx6Mhno1CgICuYjMyP/MmQzi9xCcuJAHXL4SYBrCSj1me6IY4d7xBLf0XbkU6GJqoQ+lTsNeTWRCyJGgUmsWxKDRfxrl4f+g2umvM3B63qC6HqF6P'
        b'MY89Qrs9QtvkneNej+zxiClaaJ5XMZbEJqVXTUrF9i4HH4ga5riviEKYi5T1yQfWaJ+MX216AvX0BBTovYZLKmMOkAjLfJ8P8X2WIj4mt5Hqx9/A+W2QCgRjf6zfOyr1'
        b'5c4pwkSmqUDYOGv5EspQ/YQUow+g66gENQaJ1sRFojIAqug8um/NpSdPx1W2uB4XT2P5UospbzI6pthsJ+AEpD55KSWIIfBOh2UGkWLzJnLdDHh0wTYGYQmj/QZ8c4e3'
        b'fbiYE+IqgduUFFaVvo07nXDhbEO4XsgJ8jh0KxnxxfhW3D4ClecoNm+WAruDHK7D11AxD8FxK6p0RfW4bsj3LvGmL32ha7n2rFwTic8MlWtwWTyVccUUY8iYQPDnAk6I'
        b'ygRR3qh2mMuWD1hUPjdUqwGXLTEPVGuswHVbZ8kHXbf0P+a6D4Dr/v6H6jTU5wyv0vyg4yJOjtz+r6sdP1CEIA//j9cgMnKoWAat8eWqwwsCknnJy8gwgY/OzXhZ0IG6'
        b'Q3TyHFUUwBI98eHzIFZlGPP024JU+ab0HJ0hGxilb6N38jElSgvj0eS8xG8uGHeIhWwaohQT/ZgiYElUSkAQ/Jk3j/yJSlo8Hv6CeAFzw+fShqiogKCXOFqMSZNjyHtl'
        b'9YQMks5zPquZANdMEk625b8wgeT3bwXqQY55+S/HZ/L792L0MOX9R4s2gwBqML7ZJ86nAW4PeoA7BgMcrkGd/3aAi0a1NEf+ZJE7tzqYlndGBK9fwyo2oiBnrsaQSFzy'
        b'6syMAM7kAKfJ6/A+VvKxcuZWrJpM6ytBqM4DFSMIVxy6gfZxQmeBFchRQtnMcbHnRthPJoWfnM3WsRwk8wRSW+GT+CLZohy/aR03HpXNpew1+CYui4AhhmdmcuE2cykH'
        b'4VgHbnbsPI7LT4v/r017CAfyOnnkYh/6/Bx0lxu/VURRKLjK2yF0rzHZG5dyySN2Ug5/lyu4gg2BpCKVc8jBhkvR1effFxp+Ck3/680Ru5LH26EwG+PJ8zp/eZGk28pK'
        b'uvt15ddzn9v4f/T+xXNOQTlZC6afbhhrGyx3/YPvnWkNv3g6YzuneW/9/Gx3m4uf/9qr6obMadvq/rU9vcaywCWzkbmp4dczlLMbC8ZG2z5wvztz/6JZ099/8x+TPv/9'
        b'N/W1taXamzNCJnwXVrdu2vGTDn9I+2X6J0/R97tnnjyLr0Y+en/HaSf95xVfZi/et3Fp7vGyju7ijviCr3uD22dsXTDjo9mOf/2DW9C6irk/D5j81CXgfFnS0W9Cvnvz'
        b'A7X8GdGEaic6RjJ0yJHbg/kcHbWglmejyeS070SXX8AboUL00I7HGznKZ2QXRoEvyEhYQEVJJF0PhZuCyQNxMm48bsRX0E1pbDaupXl/iiuuVcThEvUAN851C4TPQrHc'
        b'Bd98xnYTcLMt5P2C7Qs44WbBHHwB3X5G4las1zKS8IcmqdBNIupuYcDGXXQQ6FACaqf5O7oLUbGMJfCaBc/Id1S4Cu/HjXG4NE4dssLIFxrsw0TrcMNItdWPy9nJbsRg'
        b'ys6wkRXLsyB2bB86pbjoIx4X7QRcpCTZqJPrcXWlujrQHAUI6InS50NPv65x83s8F3S5LOgXihx9er39H3tP7vae3Onc4z2jYsFTKSCqmozGiEfO43q9RjdMq53WaLiw'
        b'rWnbmR2PvCIgS/7Y2fux89hu57GNSx45q2la61QRUby1Jvzw7sYxjZomv+ao08Gdooc2t21eX/pochwRA24ZX7S5xqPbfnRjRrNPU1abVbffFPqwW01EzaZGx5rJjVsu'
        b'7GradWbP+14TWV3ha9Ce+2jIdB19nnipINN19GGZ7jnHubM4NMsqSiHC1gI4MhinYJiNaKdPBOHoVejtB8siL2W0ZAvYYnq/4PiElmC6FTKBYNRXkNCO+rHArlaq5loU'
        b'kSK1gL1EdQx3ZuLi+NypFntcHLo+7IusQa+axrG0lH6RJc4SDn55JfqPfXmVpRZ++94wB7+YBYgfyKqyaFJEoYjl9tH/dBr6gxFK9FKEkiaapnH0DeIzO4Z9OSew/bfC'
        b'03I7inBH6vADAz6Brgy+4xuI6+i+Pz4L2VBxnHhnUjA+nIBLlmBzvNApGjzeQXQO1cKJmkt2kCEIKm469bULIprInT+48sQ7kZDIXasZlsbZkDQubcKRL9InZ3DvtKe/'
        b'cyHsjXiu7r/slNr54cfHFzsvSR0nio8GX6Pgzvzczs0hWi1hjvVMtP4lv4r37eH96lJUR+unASJSHU+kFVTeN+PWVFY/LcWXtwaGxPLFUxmqHqifitF1WrfMQFUjLDwt'
        b'Oo5aibclrhaXojPPaA3n6A50ndZYk/DhHXjvQJEVV+arhRZGSfzZgMOTrdMaqbsbOKHOLpZ3drvlLyaBQzVJywLhh26qLp9JPW6Tuxwm9zqPfOzs2+3s25jZ4xzYZROo'
        b'J3PE/IhETybilbkfSeDThjI/kp0NyuQu4LO+bwq4v2yUCwROP8I5fEWcQ6XUh2tSBIn+pfWLzdz/E+uHjObbi8OMZ0l+js5oGDRxtnsIdqwiV7P0mnV0N/AFcx9wGRpV'
        b'5CurJcNu9o9KWpqYsnhFkCoqJjoqbsnShCAV9BKXGpU0LzpINSeKtqcmLk2YG71Y/eMsm+Iqt7lSzgaQ3Z7gtPhfWW3hTMSLq1HjTPIJbiD5HrYoB1XFL4qhWShNQXGV'
        b'GrVYo9pt8F8sKtrGoXqpNUDHQlzLXtksROVL+ceLrQkH8kEwK3h442YxOu2F23TSX5+VGMhnv7bpvcyWL++dUlwpEF0+9P6ad+vfVduoSxbbdNhMsKmP15ZEf+j7bthS'
        b'dfylpu0n3KfVrncfu/dy0LL4nqm1mj+s99jgXlyZkDa/JhnXvFX2K983bE56cB+86fg3U7ZaTO0WV6PLGma16IErM9yxUykamYRrpvFWqXIYQEDEJtG9NXQzAjfZoBv8'
        b'XgSHa5MolEGtqIwinQX4+OY4CrD8pZyVOzo9U4iaPPF5tfiVwZRM/6CF9FlDcmjgqzgW59R+U5n99q+14lzcBw325ao6tdtZPW6zuxxm/1B5He5p9O5xC+tyCOt1dj8+'
        b'vXJ69cwuG5//K6uOIlZtIay/pWEnWP04w9aT4ALRnhSJ1ngaIdYvhBCPS1AxLg9Fh9kuk+cecTYqQxWvNvxMYvjigbBPPsPmK9H/WeMnleg1L1aiLaM/LdnmajbSxPkV'
        b'QZ+kzeQlgXwtXABwMDwMxzIXkKMxGiELztBABB/OlGIBTSYrdr+U/w/jNVgL+FelAJb6//8DRuSJphnEv9zHZXYvf8Y/HIqgttCX0chsfIE6vX0AgwHBhoWt9QvZ4BXO'
        b'0cRzgXsO/wkS7gwHhOI3jX2GczUU34z7p+gElaPLBKF0oEOU/Zp0GfGpDmF+t/OX7LbndFk1W4UG8m9jfPGHXFaAbhmGW+Jt6t+tz99tveSmyz5bUVRl2rglbhEi6exm'
        b'hfR6+/LxS4lLLJm9bXP8Ny5ZNVazn+ej6BXJH+J9v/VeFqtaoTDucZt0XjfBRv48P4vjXHrcTFNnqaW0QA2p/imOAht0ZLQlthkoUD/ApTRlRI34nJ1FzphE95FwGXjG'
        b'BAk3KXGNRLobV02neV82OotbhjCQ5yxhsCyMOtOFsWsYBNqFH1huIQPbBloHHzMBl/LeNgYftnS35FNkBsUejrahCGhmzHAhRqEqMa7H+6eCt/rBbIV4K4tCuQ2FH7DM'
        b'iRFtH0ZRL7uD40vl1i+gJJK3TeuxH9UY/r69L92YDO9WhrdN61HO6nKY9bG3+rF3aLd3aI/3+ApFr3L0Y2VwtzK4OfORMuJDz7FdvtN6PKd3uUx/4uXbuKHHK7xtfLfX'
        b'hAo55RPSrQxp3tqjJEDLwgPL+hTEnabm6Qlc+ufZGauyW2wI6BOIVx42vKkWfvn5JvDLHj82G6uWjuHOKEJEalFi4ny1YL5amDhft7zjodBAvnINWPTbg4+eL+lJc5f1'
        b'T/q8Udd3fcGc1Z3PZ2+ynxf94SqXk6nFLuNS9vZNddi4OH/Zm3sVrQ9v7Dn73w8iO7b8uf7zj8Zt+6rkeWzocavU+OLbGdvfdf4q8fC1xQnN6PLEXWk/U0e/LVqYWuwg'
        b'ao3Y0vTttlBl+8+WR2T8ZZnNX78riRfbbfBt94p6ctRB8v1JjSzYat2VNZrorLd3176ze0Zme0DTigljDh/7o/Pzv8g/61n4ocL+Xn+T8R031/tCrX+Sf/Ns39a5E1rn'
        b'BLfub/jgzN735o6pL51iDPld9zfZpxVtFSEo/Y447vPwoAuBbVVX0Po70g3O1s9XjPtb64KIjwpKb0hOfPa7+BGr2o7m4s13RNM+D/nT+dbwO7KNxtC/dn+ffUHWNcf+'
        b'ne+iJseXf5w9NzZr89RDn65ueD12u/WFzz1Onvt9V+wvPhX+ee6k+/7jHo5teH69ZO0bS7cnJIpWXxA86/L67NycZ90nOo9+9PnEL/J3KZ9nz5Jmy59/LrJ538emJ8z7'
        b'ffO9snc+G/Pk6fhTXRfcm34RtrDhU0npz/7xXkXPidq+s8JZv3HHk9f+xnXtp7a/TrxdtXD1pL+kFflPXvzEcOKzXOXpONfRF+f90vx1Uu7GiY/dOhY8alxW43Ut+k9q'
        b'0++mXiz725+F/3v0+t7aFbWmOfdjDq6/X3Tee9HNp9N/rVFmBf/3d/qe0D2un89759SuvD1e2kO/6ioNOPOTfunJrbMurvhqxe+bx1y9M3pG5TsP/hJz/WZA42+iKj3X'
        b'Pf08TJegfPzl3d+MmflJxIO0gI/j9/z8z/0/7epc4Hvh0sTvTn6x6pPETbd+Oe77j/5QX//HnzZfSrtSdfrJ1PY9blk/nXH7T59/9+uTP3Fu+/S1yr9f0XSPPfLulvM+'
        b'v317RsevLv79+VH366bDc6L/+I3i+05l87uF4OzoLst5dAhVobPoFgAJASeYzEGMuKiljifZAwLAYPK1P9LC8VzCNc/oLpXnLly89qUskPeU6Nx21smJeTJcDGCwNFjK'
        b'7eKka4Vj8H18mkJFGa56LXBhMDZbSWLjEyWcAl0Tgscq8XqmIk/eQnfR3TgSt4LRHQgzZlwSS266KsQXceNq9Ygf99KK/IcOP/rVl1f6GOLPByPzbPIrGPZjDlaempqT'
        b'p8lMTd0+eEYdq5uU474H+DpfwNm69otlVkriUcOLt9T4HN5Za2gMb9Q0TTixvXlR3Z5rY9v0nT7XTJ2Lrm1tD3lj3ttOOOb98PgP3QnW1dROOGHVuLDbPaRN2e0+uWt6'
        b'YrcysWtxStfSZd2LX3tf+RrBtk7VuV0OY/tFnPtyQb815+RSMafS1Tz3S6nU09ps1+/COXn0Orr3Ono9lYk9rM22/XYJAlfrXhuHLifffhE5/9jGoSK0X0JO+6WcrSMQ'
        b'MkrIGWFFCWtGKChhA0SXk3+/LaXsKDW2355SDnybI6Wc2GPOlHChTcH9rpRyo5Rvv5JS7uxGD0p4MsKLEiP4+0ZSypunRlFKxW70ocRoJsfTMZQay5p8KeFHm9T94yjl'
        b'z8uhplQAL34gpYJ4KphSIfxzoZQK49vGUyqcdRBBiUhGTKDERP6+SZSazEs8hVJT2Y3TKDGdETMoMZOXahalZgt4JnMElJ4r4NlEMXoeT38Zzej5Al7UBYyOGaBjGb1w'
        b'4Pk4RscLWN8JjEzkySRGJvPkIkYu5skljEzhyaWMXMaTrzFyOU+uYORKnlzFyNUDcq1h9Fq+OZWRaQNiahidPkBnMDpz4HEto7MGpmEdo7MZPb5fx+j1PPsNjMwZmNWN'
        b'jM7lm/MYmc+Tmxip50kDI40DfZsYvZlv3sLIrTy5jZHbByTfweidfPMuRu4W8Orew+jZQv72OUKmbyEvaRSj5w20RzN6vnBA34yO4emnsYxeKOScR/c6+fY6qenRZ+D/'
        b'vl+uoHeYrfpXCzmvsQ2htaEfeAYWLTRHVbj2uvs+dg/sdg/8wD24UlwhqBjf6z6ywbbWtlHT7NjjHlgpAU/jEfKxS0iba7fLRHN078hRDStrVzZLekaGmGMrMg4n9ltx'
        b'XkHgE6wdnlg5VGTUGJqj2jIfWU17LpxhFfmUg8NXIs56Ojk49IuBJFNBb64Z02hoEz+ymvAXoaOVO7lhIn8XkGDCSo/j6yvXd/mk9LgtNSs+trInHSxpHNM8r821zdS5'
        b'7PXot327ApMfWS16LvSzcn/K+TEuiwU8G6DJyuYle2Tl+UxoYxVEGr34O4AEf2N5g53VaMsbgASnw8Rd8sjK569CJ6sppI3e5fBUDOTX/RlygVWs4InTqLM2XcHze1QL'
        b'epxiumxivqXvyBXNcY/14X7m4xwbye9POPQJU1P/3U2Jfyd+OQxh5OExS7+UBPvBcDWG3DyTB8pRAoHA4TkHh6fk8GMhc700mGtVTBbp7hZMEhjehCtXvvrJiYBfvfdI'
        b'bf3eh++F1/scHH/Qp7DpWNMhn+JagehI2+vLL3n4GIMzbDPcpp1/x8VvbEe8Q51j+tQ4ZZx11OjAcQd++sFbH/7s5FvlOrTev/5t6xtzHIpXdXZ9hN7mImPdi1fVLEox'
        b'/+bmpeXy7OOT3ZyXO/jlhxvDTG2b20z5RvnmsC1yk3lzzOY249vGt01vX3h6vq0j3zjeFC6J8I84EvP6s0thLkWCXb/oeqvko1D1ZflXYzy22/yXR0DNGI93PKb0cD4l'
        b'Ae+Pjlfb0uRuCfkonv4Df0kAXshmosI1FF0X4ubMGRRjoTO4Sk1S5WvkniTIDj18HfE9EWpCdbiV3rIc349ExagclwMWC0Ud5JvBchln5yTyNqAOBrAaBeh6XGxCQBq+'
        b'nyDjpGKhHNegm8/ov1PUnqsPXChR6jhBHAdXH+I7z8hndmGoA594sSSAyvBJdCA0DmBcGeSR5SJuAbomQ+WCjTTPXIILvV98RIruo8Occp44AN1DRSwdPbAK36P5qCUn'
        b'rzTcgk6IyTtF22iF0WNuIC7eNBmmBRfLOHGwALXiY/PovJF//CwcF6uBBcxb0ShSkxBw9otESxcksrfILqC7uH3gjow1QagslFZe4TYV7pBwqFDI3iJrRRX+gUlB+DAp'
        b'rxIF4APZ+IEQkGUrLmTi7sVXEPlaugRgaGjAJh7DeuKWpSYxOoSLR6hH/zCG/I8gx//gwTCagtCXsOcLv0EoqsvVGRkUZWcUij7g6L7kV56cxLnX1uWxrXe3rffJrT22'
        b'/gXze8XWhfF747scfc5OfiQO+pXYFuCfp3eX2K1faC1ZKfiV3ANQn7f/45ER3SMjekZO6JJ79srtyhVFikcufo/k43rlTo/lXt1yr5o5j+TevfYej+39uu39Htn799o4'
        b'lScWJXZ5Lf+lzYrn0g1iyZTnHDn2s+NKK87GpSDp62eb4ET5JSeUhPW6epitefZdLiEfyAGSwmX+DWbx3AAOBYyIshJhuQCOzG+O6hPlaHP7xOTNmT4J3VDoE+foDMY+'
        b'caYuA455+dAsMhj1fZL0bUatoU+cnpeX0yfS5Rr7JFngA+GPXpO7Dp7W5eabjH2ijGx9nyhPn9knzdLlGLVAbNTk94m26/L7JBpDhk7XJ8rWboVbgL21zqDLNRg1uRna'
        b'PimtN2bQtwS1+UZDn+PGvMwpk1LZNnGmbp3O2KcwZOuyjKlaUgfsszXlZmRrdLnazFTt1ow+q9RUg9ZI3rLuk5pyTQZt5lA8MJAdtLR/9lOpmHfPHDiQf6vSkASHf/zj'
        b'H+RFa0eBIFtEfPvwYz89/hhPTwLYGzLpHCX3hlIxZ7ToW/nAFwJ9Dqmp/DkfXb71zBr+z9CqcvOMKtKmzUxUy8lL5pl5GTBiONHk5EAIzOTXMiniwHVrmFy90bBFZ8zu'
        b'k+bkZWhyDH02ltVU/X6OryGxahKzhensn7mdqSdv+pDCOd0Q7BdBfHsqFAvEkL4obAtkX0rnw4D7F1tzVo78Ol4Iq7oraOYbfti/O2hhr9zhibVblzKixzqySxz5hHOo'
        b'cP8l50m7+j+pwxWr'
    ))))
