
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
        b'eJzNfAdYnNeV9p1KGVGEuqwyshpDk0DF6gUVg2jq1RYMMIixEANTULMKIAGiCwQCJCEhVChCEgKhhiT7HCdrO84mWWd3tSQbJ07WiWM/iZOsvf/Gyfo/994ZioRs5//3'
        b'eXbRM8Pw3fvde+6557znvOd+o1+yp35U9FpGL9siektm29kutl2RrEhWHmPblSbVBXWyqkFhnZKsNmlyWRazhexQmrTJmlxFjsLkZlLmKhQsWbuBeRwzuP05xTMyfHms'
        b'fo8l2ZFm0ltS9PZUk37tfnuqJV2/2pxuNyWl6jOMSbuNu0whnp4bU802V99kU4o53WTTpzjSk+xmS7pNb7fok1JNSbv1xvRkfZLVZLSb9Hx0W4hn0rh+8k+k13h66fga'
        b'Mugtn+Ur8pX5qnx1viZfm++W757vke+Zr8sfku+V753vk++bPzTfL39Y/vD8Efkj80flj84fkz82/4X8cSnjxbrdD40vYLns0IQDfq+Pz2Vb2OsTcpmCHR5/eMKGfp9n'
        b'krZo3SkGVWxSf4Uq6eVFr2FcILVQ6gZm8IxNc6fPJ5coWdpWT/qUEO0Yt4w5ptJHqISqYCzCE3HR67AAS+IMWAKtfpGb1gZr2fRVanwMp0Y75lJPzN6E96hnKZYFUncs'
        b'jYjB0s10T9GMdRFBUVhM/zrgemQ0FkZqWBaUebyyDnPEzJVb3dinq0hb+oTojMlG5niFLk7Hi2nY4eG1LoIGLY7cFAFt/lgQtCYGT25wxxMRm2jogXP5R0RjaWx03CZ/'
        b'aiiYgSWR6yLWbPIPjpg+MTJIAS1qZocTI+Zuw8dJiqeszNullPXfsEsp3s59UBQoaR+UtA8KsQ9KoXvFYeWGfp+d+7Dr6X3woFfMM/uQJvehzlO7vpmN5tpI2xk9mYmL'
        b'P/FW6n/K+KeEoDWxU+XFLes9vDcyPV1LSPt4e7q8eG25OmIb8yXPSYiuUatZM0vjezrFZ4z63/3Yss+GzU9GZVfoaXU5S+NynN9Rq7jpxvQzx6SPWTAiTNcmL+uW/9Hn'
        b'lI/C/zN2JHrYkfenfcp6mCOI7/OJHeG0I7Sr/v5YOCMiGAuheaM/7UtZUEhk8JoYBUv38YC7psV6Zpjh4EtctgUf2oYo2AI9wxoG1YHY7BhO1zdj/jqbVcNC4STDIgYF'
        b'SXDVMYI3QBt226xubDZkMyxhUIjZwQ4/akkKs9iwi7GgrQzLGRRPj3OM4UI1knU9skGpmkEVXmfYwOAcXoJjjlHciC9jNRylViVTYzfDiwzq4eZB2ZaNdQdtmRoGNVDJ'
        b'sIzPdRqKZFsDNBlt2K5lk+AhwyoG5dCMZUKQl1aH2RwaFoZnGZ5kUJRyWCz1JSzdaPPS0rVpDM8zqH15tmM0H6oWu6DChh0k4A1oZHiaBtNBsZznHDRggw2K+cdFjIaE'
        b'Orw9R+gIT66DCzadkkGJN8MLNNBOrZgpamu6ba+K9ObJsJpBKTw+IK4nvcpsPjTQQ0/RvQZr5jlG8kla1+7HDi81s0AzwzYG57EZLotbXsDyCB3tA3uFYSvdsgerxDZA'
        b'3ksKKKKNwxosUrgzuA4Pk4VUPpFaG96ihqM6hhUMyjRwRtyydhWWYIeD5KqAS0LTpyxG0bJ9LVTp8CYpuppWdYO2YAI2iRYsTYBjtr1K2sV5YrTCA/BAKAbPhUCRDe+o'
        b'SZfbGNYyOAlNeFUqrQmP4T2bj5JNgTwxUx0U4xnZVj8Cr2GHu5LNghqGlxicIYsqEbMFBCipRcP88BTDq9QVG+GGaBlKI9zCDruGDfcRk5VBta/chPrDcAY7hmiZt0Xc'
        b'dM7wothWvAg146hBwaCCdgGb+HjX8ZKQQonnp2IHtpP0rbQZjbRyssRseeNxfATdhG90512+IdfJ2rBaLabzGxVILaSp9kChqYtbIEfuYfcYJDk8VAyO06g3GTRi5S7R'
        b'ZIKGyaR4LYNb0C1M7+QIuCNt7xZ0QgvtPc2VT1bM77uILXrZWIT5SKvGDgVbsZphC9dVDp6U8xW9lsSb3NgwrBNGU4/HlwhlOSBnAW0nmUA5N2cS/9w2d3ET1tLWdOrc'
        b'abZi0lYXud9QaBA3KbZgkQ5vubFNhAN4m8SAm/7CnbDUd4suS8OS3MQ0tQ6zFID7dbEOu9TsIG0jttM06zzkNGenYSG10IrvGhl2kEFvgU7RlJxyiBpIf8VQIaZpIGt8'
        b'KJomQAE22uwkWzbZIRaQjY+H46IpHe766Gzc1KBNqL0GL2GXkHsZHIUmnSdNVbqJ4T0GV9ZihQCeGJMZiuaSDlpHw20o1jAVXlTE4bEA0WoMS4CiLDwFJ1KgBAo1TJ2q'
        b'gOxNcNah5yvg5vBQdigJw/LNZAliDA8oUY7ynm5QCWuAy7R5d7GI4pSFTV1mgTu0Fu62eHkdNEZR+Ehk0+FhItzBQsdQur4Az9uitDyo4MkFyXjJ5phOV9VYGYmVWACt'
        b'c7EIWqFZY4yBErz02gpo3B7DZts0hJytIY5pPEcYtt3ZdX44XMcqPCX+mA2tWKVm47BE7RGJpxwBXLoCuAmPZW/oIpdsot2nGyLgem9/eKhWjWRCiqk+NKcceuII8sm+'
        b'oa/JoSvU2lFQ5/DnQzfDsVCsjIBrc2cK5HV1DuNTUOdgFenl8VxHoHSoSzSGHBqui8VB92s6PcWqU/AQmjYPY2v0brqN5CQ8jPkOxSu9vXtHhhs8vZnrvo5UTjMEWzWZ'
        b'cHONY4bAIjgN7VIckqVElShn2MGNtI70CEWkxgi8q8XbeDpa6BHroXADv6UZ2uVtTs2o1xPodqjwJnDDnM8Xe92y2KVFWh6XYoB6mmL4ANditIkxLBNuuCcTWN0jQLnu'
        b'mMknuos3Kemp5GPzWVbDKX6nilDpBFZBXgoZVh0LxfMaChTX4JyM5BfhCgGB0ybu4W05ody5FrlzlSrs5sHJYeDBzZtyLtndhzyqv2E0y93LV7thK5Q6QvnwV7HdZRlc'
        b'x31L6mcbs+HBjoMaio6NeE+sBI7i+QOum/q2nHqXSD3wu8Jm0VZTzLmQOlVY1by1y1y6Wxsv7c+lNilXm9p9MqEyFwuO48k+sXpnIK1fE1MchAvSFoPJYW1QNcoRLCIK'
        b'nhvpuqmF30QAu5+rFvL0eNwXLpJ9xeBDtzA4v0g4xl6Pnb2TuKwRc7f7z5Uy2XQZcN6d0O3ufrnuYjw52nVD69MGSZnIUZdU1STVtRQxx6FwLHfd09brzyv0WCnsPQ5z'
        b'U7DeLSQQaoQJwyl4MKLPggfMRL57HI9J2ULggeY1t9fEFGTCZ2lPxE14jcyo5Rk4mK7CB9jpI/hCmq/a2bdC12fus/m+q8nku1TY7jnXEUI97dAx+SnjaH7aOPDqwUwN'
        b'1IyFcuFOUAvdwdLIl5P99XZ34YFKhTdeXO+CpTsBruFvYSfp8RmjaFS7rcVax0vUPZaWeW4wacQVNdwaEkNp7unlK6FtGrNilTsh/k24K5acDvfDe72iuA96Vug1ZN4X'
        b'NHBegSek6Z2CSuweuAH9nUj43KwACtJnNOS59bsl8Jzx2NdnriW9BiiuqEg0r9fmKNZp3IId8/A4PBLmqiC7rI4SiEFde+2D9N8P8tdDiduk6dAqfBs7Qim16BUNT08S'
        b'ACc6c2CbBbcJO7BBJxwOspdT7BK9Sd5+G9Ei97mddmI8dDleFMg8TninY1fvep0QOA5yyHRmT5ICnKLMu9a5UA+y4Ge2F/JVeD9whmMKF6CLclKy/Qit5wBgVXJgvUNW'
        b'BtnLRBDxpb0/71xXGSXa/WzsupT1Jsk6JVIsazve42bAm0dslloWiNrZZ2Cdi7HeEUZ9V+MD9bMBZLbLeoQiQsl3arBOQ3SjGUvFbmZs74+JvbI09b8L27B2i4aMHjuF'
        b'aqKxLWWgm3Pz6nXztRQci6Pd5s8PFUiSQlD+aKCRtT29kln6OHisIYXU4HEZQB5iTtKAm5RJznl8aZq7kD9m7lAomKOAM8s8Yy07pJM1UgKX7fT3Kvrc/IyTGVR4B0oy'
        b'hcfjDWgLfC60Y/14J8I5NBn4KECsPJSiqnP8EgqhTwPEC3hPRclrFT4SOYACG8htnIHAB88OiATO1OWx2pvSwkopf9U0ijty+AsUT/tZ3DU5/HUVZfPH4YQQJmklT7ef'
        b'gvR+2zB2d5DbS2RB18XgR7DRlURRzG0exJq4PT+GjvHCnGLwMp4ffAOgYzs55E2sx2Ov0aDMutsd7h1YK5Y8Pu5wP2vaSoP0rlfj5wz61yhQYplS7vP5Nb0hvy+/6Es5'
        b'HiU5Mx+o1NjjsU7Y7K79Wwez9Ob+NjsUW7GBsG4zIZCINVeW4o2+gNkf6wzYJj1FkzlHsdbdba4/nhOLgWNYQ/vUJ93wUKfKrmkSSQsxLGyUhnavGo/KBPECnFvq7L5s'
        b'uIxlTg3LbBJuqdV4VCF2zwO7sN2V7NzyGrCSNmkbhWr3l6BColEe0ZhTcj8O7R1g2NKQFqp46o7HJLCfm/76s4b9lFdDVTRWauAstV0xREt+m0s4dl/QkUK9ZCNwEqtF'
        b'dh8MLctsxEVjiRefIOIWANWCKSmCvG3YqWCvDBMVkNL0oYK9xNAsosgCVXBVlln2UdommNLtKdBig2Ilg5yJFNAZnN2FlwWxCVpAFNpKnKf8MMN8vgH52CpJeSNFqsu8'
        b'OhMEp2V1hsVLoTu2QAEvzhBfeCyrM2RSpwVXMW7Ciza8xTnnFOJ0RCB3jpVE7vJG6LZ5KtkBTslquJT3IFtWGR7g9Sk2KFSztDRBXM9mEd0VtLsjHM6Kck94miz3LLTL'
        b'W+q3Trd503q69jEipmQQtdgk5hmPTQedZSBocpaBatPFTfPVKlECmkx6liWgk2R3goxXEGs5JYpAN/GYLALBeQqMQvLzk/aJGtBy6HTWgC7BYyFf+MYkanFju3jlqJaH'
        b'9/oYKd9xMsHjvD6kwWxZH1q6U7SYlmIdrw/BfeiQBSK86itaPKB1uqgPDYXHsjwUg7lC4a9DNzbbOAunpOc4ERFacAzRBi7CHi0+4NWh5KGyOIQdTnIIeeEBvKYSgmdk'
        b'TcUvQopWkYLttr0almoRqykhAC8XQ+kXxIhSy6opzkpLLSVHvMHTDxqoRcFjqShOnQpaKcssVcQl7vISDF47JEswWEa8UJRZ8AyU2XzIHs/EiwrMWazzlwptg+IDojjj'
        b'scZZm6mCK6JpN94lU+LVmYz5zuJMAYVBUViLorDGazOhi2RtJmi1tEbaDuLpHdwl8IZWaKH6RZXY14lQSa7dMYSs4QFUEV+mufA+ebjwirJo4ka8poMVGmdRh2Tnc03a'
        b'N1fWdO6MlCWd14NlWTJtPU10y40ZoF6MVudBOSBvMWDTFuzwJp9oM4vaQSMWHxElAGhPIpjo4IYHedjMyDngCqFLu1BtJC8edGTSNpmEZsv8nSXB0UTOzlILSXf2ZbHl'
        b'5QSn56UCL8LpFc7CUvNBWVjSWcV4Q6FqvSgqjRwnS0oO1z0FpKjToqo0K1YWleCeXlrE4xEvi5rSKix01pQeS0+HO1B4QBSVsGOnrCkRtLWItkxCilPUJmpKxULtFXgp'
        b'WkCUJmU4tWjYIi/hgZWHZjvLqdhEpLsDb2vZvFeEymuVIEuNsXh3H3Z4KZknxweS/IIPyCoatnpBmSheUaQvcxavLs1zFW/v8BG9NLwA2iXqQ42zp4kVT7cEyKoWZcjO'
        b'stZtaBaTHaJsv0vWtZYukGWtxVrRsoN4Q5kOb2rJuUXD2QzIE1OthCIoEQUvAq4aWfBagzXSlDrJ3S/r3ElPDQ5RcLoEDUFyQOyO4KWw3dz+eCmMtr5eAmwF3PTT2ck2'
        b'b0UIY6rExlC54kLC8seiTobZh2WdbC05qRNZ7keKSlR1vKxEEeGUYFm7N1iXRSZRspjMgoNz7hbZ8Mhvmi5Ly2JeFtXd0xSfimT9qHJLKq+5YWGcLLplbhHXt3uOFhW3'
        b'mTGy4KaCWmlD9dC6Q1bc7nvLittkyBVNlBquEiU3M8dPUXHLJngX03dDfpLOm7bvsgf9waDpyAaptXuYAwU6bxXhEMH4I8aDVKt09mnTddhOtzRGCq01jF0oblkJuXiD'
        b'WuiWErjC8C5t99AMUfTys0fpPJQseLyY4+rEEUJdw70wR+cgHZ/mwElrJMdxqusmnhTlPuiURdaaSYdlIdUb63Q2N17+uy2WUk82dlpuTBNcGk/eTOYRH0ApM9/nQqxy'
        b'zOYIsJu8hXJVKBDlPAogbU6eBgVzR1jI+26roWMjFG1iW17V4nlKLjoNascLdOsmojLnsSh6DbHHNsxWMRU+ojwbT0K7VFQFpbJ5wcOisDBay5Q7FTMoJb0oJDpoNEaZ'
        b'4rF0BpYEGvgJ1xBf1YigVLldZ/ywLTA2OGL5OjVTL1NACxHh/NVJ/LzJ9aNl8jBKHERFMHH2xc+8+PkXP/dS5XukeDhPvNQF6lx2SHPA73W1OPHSiFMu9WHNhn6fZ7Jk'
        b'lTjxUv/iMyWFDn2/nxX8zNSmN6aLw1J9isWqzzKmmZPN9v0hAzoO+CNSHtUG7Lak2y3i2DXAdVCrN9NoWUZzmjExzRQkBnzZZN3jnMDG7xswVKIxfbc+yZJsEge3fFQx'
        b'ns2xx3UgbExKsjjS7fp0x55Ek1VvtDq7mJL1RtuAsfaa0tJCPAdcWpBhtBr36M00zQL9xlR5JswPixN7RwkZ7IZEc9ICvsxd5ixTepC8iwsYHrligATm9GdWxH+SSDGm'
        b'fXa+BJMxKVVvoU7WQScSa7Pu7z+Z3SUmqfLbz2Pnx+PO0UL0MQ6bna+R631DXPCs0Llz9cuj10Ys14cNMkiyaVDZbKYMoxAsgH8K0JvINBxGu0mctickbLQ6TAkJA+R9'
        b'dmyn/FLjwrSca9FvMKfvSjPpVzmsFv1a4/49pnS7Tb/cajI+JYvVZHdY020LemfUW9J7jTSIrq42ptnEZa7kvWbbU4t55rTdnT19yjs0drWApkVTocaWSZSkTcNkynkA'
        b'r4gT3OzdoxlxNfdLxoRX/nX9HibxqhBPc8ZBXW2MbWPblkKzPAR+WceoQ6qbb0L0yCwveQjc6u3DxjE2M3VewpD7uyYyGTuq4XasTQfdY0kykS1CjtngI9PFY8FLbDoK'
        b'8K6m0Tpx3csSaNtrxTsqJk8Zgwl4+FgLidbX2nyGhjPmPGY8SrxFxORbBDQ8JkPXUFq0OGmEqrkSyW4cJnC1boZ2vmZ+1EgMyEVSJqTqMrAKjvKpmnicuojyNBiyLdCu'
        b'y6QMqIG3UQJwxuuQjGCtW2KhaMjYAAUTx5NY7TzUuk34S+mijYJPDWEcz0IqXsX7QpPBr2whipIK9xRMnl3Cvc1S8uOUYuVQ5gLdO/hE/PASijOkeNcykyn6e8ItjfP0'
        b'Eo6izCb84dQ23d5UeMzv6eItZa5z52x4jOeww/oS1PLbzvAsriVWnurkDkuw7cXLG9yYyPbLoHCUWFPGtFS6XgkXlFK8wjEBBpXUw1G8H2HbO3yJqwXLQCbbnqojNMtB'
        b'bHfNQnn5WTHNcsqNb9j2QqPaNU/GTiHbZkrbyolUEPkvUcum8i1w3qCUCjwNV7dTK4W+HFcrsdl7QhdqUi0/rR5P+QeTp9Vwaq6wu23L3dgQxva1TElI2zfnNafd1fGj'
        b'qVkz4d4aNX+ihCViXoT5xSf7NDbK6tjKs+mLy0PXrFjum7crK+uDqB93wzT1+q3btu1TBuq+nK5eWKR4c9kbh3zXVnxXH31/3C/2/DJ0Ud70z9zf7Kk9eWxPyqMjX/1n'
        b'/sknXqN3lD9Zkb1n+Nu/V+7MvfTeuydXvPmeZVTFn/XtF3771lvtx+b/24MxNUe0M+a3/HL+oyUvPjmYcdiraPWPJ3V6vPrFlN/Ozh62ZaJRucPv3cfh9RGvQ/3m3T1X'
        b'fX2qa4681343c8nG/7r8l1+9PePc+YCvNh/O+lVJZkPOuf9Y/+uH5U+6H36yoXlvzQ+mhn32dtfM77/91VTvH2dV/vzdqsDlqcpDt164ZtQs/DT93PS/Zt745+boP3ic'
        b'ePPX//Dk/tDpn3z35urmzXeXp3/UoMkbmRd35Ce6lCWTfmNws3OVhWNlemCwf0TweDyvZFqoUwaHz7XzZ4vCV8GFwBAPvBcZFGAIwbIgPEFsQa/eCXW+ogNR2Dysi4oL'
        b'5tYBJ+JE0qBbp8TSNbF2vvOe2DWcP9ETEBzy0hoFDZ6jnDUNy+y8ADph0yzadPlYzV7+WA0v/JRmBQdg4QwiKfBQQ1kL5trFMxd3sHYYFsUERdINXfiAsonZSu9lUGnn'
        b'Vd/tZNFnoqjl6Ab+cA7QmDzBUbEReEyFdxPxokHZo/Q38McOmMFD/PrWbxxZ/zxiUYrVcsCUrk+Rj2+F8MC7pMdThIF4/gfvZtvMofgIM6gVaoW7eHkrlIqRCk/67Un/'
        b'+PUh4rqnwl2p5e+KvnfeplWMFr/5X970l5q3KMcprG6cuAhhDNoeNZ+xR0XBvMfNGRp71DyW9bjFx1sd6fHxPbr4+KQ0kzHdkREfb9B+/RoNaitPzKz82R0rdy0rf4rM'
        b'yhM2MW81X9sEvraj7NNxJLdSoRXvyr8olZSMKdh/8b8ck6iHPXh1FN/MiVj/7E5gK7QRwHDTmXh4ShS1YFEs7ds9OBMXqWHeGap51OWigAUrdHpHmT2iY2XGqWC67Uq8'
        b'flApWF8KXFs/Zm5fkrpoTZKqXzTki3JzRcMlrPcxK3WK2plgqgpUlGCqKcFUiQRTLZJK1WH1hn6fnQlmKiWYTxRPJ5jiUbx+GabVskdvdOWEA7O/gZneU5ncxq9JOK2m'
        b'TIfZKtOMDJOVks49Mh9yPR84MCOIcyUKJEjAeprRvMe0ymq1WAPEYEZqSR48j+TycnFlLvn0IgZNopyLknc8vcLBpuCZ5+o04y69Wea/SRar1WTLsKQnU8IkElBbqsWR'
        b'lswTKpkbiUzYmf0OnjqtMvMl92VqlJUb9WHBdkcGZWDOfExojRJJf94jiE9k+IZESvNMIqWJdSzkeNdO3Hqw5w5PRAesCYKWjfIRRH4hLjoyRjE7jVHMO6Gbv33tRvOQ'
        b'SSFq22IaRTF6zCcJIR8ZjBHGtJS0xE8Tdr7x5M0nb/793HLoLJ+f11zdUN2e2xzRmteQF1piqGnIm1STPcuLBbnpGrdWGpR28axkGz6A+7qAxbwyTrJgcYzDiZwToUON'
        b'NygfyLNPlvlJNZZFhawh8IQS7o9EmE9ynxwLnep0bIB2g3IAFjwPBQUg9OjkQ6h9oOctQS+Zw5qfADerTx9YaXrcXcbV4+Y0E4k2Q/gbf0J0wPQqK2fYVl/+5tGLQnzA'
        b'f+6HQq1+z0ch3iXRIzgqJAUr+xbdt+CC/Q7+jC/Uj4L7z7DoZqxKIr5/jDLLYrgQpHo1ajaUZkIbXOEPuSVihReee3WuzJLzRuBRDzddljfNzR/Iak0+KHIWM3bNiIDT'
        b'uqxM3lBAWQsUwDXJ6qvw4mYbdvmEwdEENVNihWIkVPnJIk3RCCLxDfttYaQ5hYVXxDqDZUJYtAcuHRihy8rS0oDHGdaRhZ13Zmp4GR/sx5aX+8AQqg84xvKWctXaKGwn'
        b'9j+Qs0+IFTeOhbroeXA9kABWwZRQqlgxDgufgdFeUrGaw6hKAKl8UlWZ757i3gun6m8Np5yv//V5fF3gwEC2/lww4cDDu38z630OGeU3/49z0aQ0IZbNZH+WfT4lINeL'
        b'JSnJQbiZnvSsoC7+uWrtcv0Kiv1WjqsrKX4k2S1WYpQZjsQ0sy2VBkrcL3o6cX4FMVSrMe2Z8cLJb0P6yWbkm+IQD7QHbFixMSCIfq1cyX+tiFsfSr9JvIDwsHDRsGJF'
        b'QNAzI/ZbE3Fby6Asmi9S6DlDcmcaNZlD/P6MpxTIf75V8Owd0ZLxbMzkP98ubg7YvP9W8q5gg5F3HyLvPFwEicPGIiOx8m8bd5xRJx4eC6b0ppsg+TMzVh9aVPpygKTt'
        b'Zzb4Mf50w8+328b9LMXKRF51wN0GRWsgmwnaTzysRkDFfsxeBEWrXyIcK6AQOUzhgYWShA1fIcj/aH3WriGJM9YTlkuyfCwW82cthGb6HMpCsR1bxfhzoCVyFnYqaZFh'
        b'LAzb4JEY5f5aX/5o+bwfrrMENakz+CjyQc3kl2fBZaLAYpQpIA8ydIehg5hDPZZRjreWrSXacF8K4+vJyxPuvlnJQaqFZrbRPE2Tp7bdpibHg+yppaHeOct8V30V9D3l'
        b'a9fSfrMoZ9dnnsO/W5roOcyv8NXEiz9anRj2xbiEj4MXuedbR4V9/8s//TruUfn3agPc9xf/n/LRO4qyvizd+vm/X/xyc+eW8MmLM8MfvP+bip+c9P11cc2iZX6hFZ+/'
        b'+08++4K/e3Xyauvnfxn1s7c6d++q8vz8rcjGT/Vv3Vdf1X1ZHHN3bHXIWc30x3BINSp7y5YnH3xqWHj8X+s67gTkFradeSv2R7+McT95/MM/ur35xZzKzUkGdzvPhIfh'
        b'A28iaPAQL0cEOxkaxfQ6O8+3JwZDoy6gXw7An5zpSwNmxdn56TVexxt4LBDaIZ/gnphaXDCcmEH9gvltUW60RRe0kctm2PnXSKALcqJ0UVhsiHFAJd5y5hUjIF/tDrlr'
        b'BGmMo9iZHbUHu+KCKXhkKZZT+DwuKB82HqAxifPNgLz5cVzew8qAF0PFShx4Amo4jcNaPElUTtK44XF2/s0VbMGr2ByFJVFOrhlEGYLPTNUuopbHDQqZHrj/TbxNZiwe'
        b'kqVRzBD5ykyZrxxhzEXT+LuS6NYQQcy8FWolp18v0mu082Ud1i+j6SNLPSqC736JzDfxLFU/njW8N7nhY/+uX3JzauzXJzevpk+LkhAApZxyU4hv0rKhmK+C4mnhBoUM'
        b'/o+gEx7LSv+0va46P23n0We+kNLLlBYwwZSUKcreL54ovtUXT1Tii0/qP//9AIxbLzHyOcl+isjVRTTuX0n/n2ZHzwVpl7YGgrRWEgO8OXfe1/GChSMHR2gsXiDPT6rg'
        b'6mT+UACzQbd8JqAVWuWDKiVQruQllsIYLN6ABdFKv1XQDMfhMtTSBwNbq/LydSOfveVrPn4iU2Hj8mys/tknCUH9KMbWN+6WN1QqImZdnhmcHLR5wtlAY6xR+72ZIQkf'
        b'J2x9e/R7b9Qq2IbpXm4vfmDQSNpAAAMtA5DFCSvNSQJZvCLtssxq8OTVI6yBYy5w2uUrHBoqKIVtCwyJDAqI2DSgfmTGB6KHBm8zCTRZux39YYbgvdjOz6uwbriDFj8J'
        b'Hw8oL+FxvCy9UTmoy7vtMtl7Hd7X5fCTuKOL2ovCOrLXoZtVsuYxKB9pVshG4aj8ntHkPTa9dNSj7Lfez3dVXuXAO1COuVER0MQBt98CUqDrG/xQmc/+n/wwlfywZYAZ'
        b'b8hIM9ttvc4mjzTIo/T8aorVuEscUTzleC7nNepnD0qnB3T2XxG3KXbj+m1B+hURq1ZEbdgUQzx7eWxU/Iq4lauC9MtXiPb42E0x4avWG76efA/mYyK6b07WsiFs5ste'
        b'+oToBXPWMwdXExbAJV/+pb1A/q2/E9HrIpxkh4z2GBEerDBAsyfU7qdXJJzYz+Cc1hMK8Mo+56Od8yg09rud/EtQxddmTMAmNVzEB5PMv7v5K40tjnp/h0WNeKd96FG9'
        b'76o3v9LfUlv1CZ/c9NhxQeko1i8/N//BvAUj3n8V//HzxGRTffnGTckL/uWj3HEhY+dOeSf3R83DvzBF/+Xqz9t3/6P9SPHsoT/64opBLYIidk2HelGApej40BXfTwTa'
        b'OdbDY+LvRc5g3Och0BShdvceZedIT5h+28NVGz0L52VQxQtwTcTjGWHromZATggP9v5a5jFaCQ0BUDiAdA/uRJ7EUGz9iP5wlx+FuotQyaubgu6P7fUl66inhxvd6z28'
        b'l/8A7+n5Gu/hiUhyFDQHRgQFYAMUx/bR+JHwQD0CWr0p0vHqr4N26SQFOrwey0+1i7BsBhRKVxt7RJ26Eouf72nO2qD4AmZvbfBv9LZfvPp0bbB/4BNFtHTjHkGbBol3'
        b'nDTxo8IME12guDgwAkVKn0sz2u3EgZKMFLwGDirCoDFZlh+fYX8Dxuplgt9EBCXx+98ahxWDYoR7rOBKUA13tV9foJsaN1gghvtYK1CmZtWYrM9YAv+e6+v3/ELkgShU'
        b'R0KnCM8pcfJrm13R8qnekolw7JngPDGzf3jmwdmyRAyuS3V7rVYlvm475KhlBDOf++wtpW0btZgawgcG7N8mpKZEG99NCVr/24RX3njy5s3y0JqGXKPi/fC8WN/vn4Xu'
        b'8vaa8U+uHJt6XHOtfsy1+k0VDdWKpvrb2mtLjvN6oYr9+wcj3YZ6G7TiiARaY2P6gjlehHsDy4Wr/cSZzEFytROBfRQhjjzqYBhXKCFQjIa9FKs9DEURIvKv8sFjmKcW'
        b'yOVELRvWyshf7QOFIvD3hf3hM/nBUQNeESdHi0buewrUovE0j/zpeF3kH1osw+tRLhkS4E6fEBOhQo3njrzo4gTfVLEcIpIBsmnuMQLJRrqQbBXHryEKT6XMCoYorON6'
        b'scyg6tFx7Iu3WHkq0S8/GHRCkmZ8L9bxURYMwLq3v6ZiKSLR5SV4FGuCepf89HoNUGRQxcauNihWG5Sxq81TfnZXaeukOSaENW4q3xY3bN3wv/v9w1mvXgn+YXjwzx/9'
        b'3rPwwdaWD0tHr9IM7/ztD5aHh1/84p33urdW1IaaP3T7ecPnlQeuzJpUV3nm7FcHKr4M/LJxTDVE72h86drvo/5QOmZLTtuS61NGL/wIPD8s/s/qnj+YWgt/2vTiBwXz'
        b'/7Bn6wd1wSXv/9PSzy/2jHs/oD7jrsm/0/FeSOv3IbnH1/RPw7+zdMEtQ+gb+hU/qb7hv8FYM7Tl04vf9U8q7jiz+FPTxC/nv7F8nXdmzeRb4/9t9N/Nn/STyNjMulk5'
        b'P7CW/il65juakLDvTH2n9O2sbT/dcvfdOddtuWeibUULZs2+G3wj5N3xvwv73uJ7YZNeqfpy0c8nle17b9hH++4vHlX7Q3tbfd2m1pIRv9z9wb6A78x5s9py8Mrug9W7'
        b'/qPYcviTG3967+CVK68P83bMqv/44x/GDdt3YPuJ9T5u+PrW35VhR+n3t5fr7Ak5iTN9n6RX/7r7ifXD+D/NWrgz/3jpd0ZljnwVo3ZeLk376Q8+qS/98dKfrare+pGX'
        b'5fKeVdZPsiuSl4ecyrmV0dod9ceTseu7f/+bzgfv5Le9/njhf5xPWfnl21dXFl3bOPmdyBv/1vP6d2M69v84x/rTxz0Xr3yaEkheKQ7tr1F6eIxil4I/nn1FMY9h6Rps'
        b'kT50zr5WuMh4bIkZkBwfhBbh00di4OhSuDJYjs5dGq9mirNTOI05RCqKgiInH8KSYC3T7lROJvy7IBwRK4MhNxCu4PU1wVgQGR2rYTpoV+I5KPURcvjDg7CopTQAYSr1'
        b'wOJI3uOGElt8ofhvPEw1eP9tZ6/PHUdj5SFg0Dfh8u7x8WkWY3J8vHD3j7gTTlYqlYrZiglfKZX8mNVP6a5y91RyZ/yr1l38/t/3r1Mb66vg/9wVfipeoRi3VEkgNXyY'
        b'J61ltGKcv5K3eIt3X/5uneCCPkIvZXx8P9Dy+v/XusI6sRfh+EQcp23iPyH5YNrz0Y0b0eJdeAmKoIxAncIunIAyN+Y9BspDVOM3W81ffP+E0naaurVQ0Cla7AnLhh/7'
        b'9Z65R8auu+m78s3JvwrJSTQsWh859n3/yOmxX4z8lzP3/zrnheS62t8nbRzuM+Q3oZG7uof8w/dONXn8q/vs7Z8Uf1j/qHW/KfZ6atzIV//rvnvi8JBHnjHd7umpn4xt'
        b'jL7sc+PtB7P/uGzka1/t+fgPf9Fu+fhT92md7929koHBe2f/9E9vJHX8Q/Sf4n4x88PiW/+peKPDEH5ggsFLuMoLwPNsWgDlALxoNuQFcoRbSmzCvMXCVTaSq7XzbKAd'
        b'TwzZHBfHq19DsVsFDXAvyM5DwRyo3iD1wKGdqD3Xgx+UQblqAhzFfIkK5/DW5qjIGDiDVQExbkyrVrrbod7OS6IrsBtvBK7RMEVUWBzDGmOqnX/daQfwL+M8lfdA6Yyo'
        b'YDhuDqDLxVimYi9DuxuUTbUKUeCmObDfHaco+oi7tGzUSnXAXpXs1Og+mXNxcvwZAZkSXtKxho11qCEvgnCIy2tPxeY5+zmLisIiN6YOVkDbBmgV5clgeCgSJDhBsrgE'
        b'gew1pMwzariybLvEutYNM7DIQL2kgSiYzzpKsupVm/CcLEcsPoiXqAfUbhCdgvjaBGNTMD3e1rA0fChrl0eJ9l0OjAvCQiGQG17dw3T4SElM/CoeHcB6xv/3gNF/45tB'
        b'9Tw0M6eb7U40499OZV48YSESplIrOCLwh0p8RRLD0xhP1RSe3Myw6nvRYGKPKs2U3qPmxyg9GkHoe9REAuw96mRzEr0TAUnvUdns1h5N4n67ydajTrRY0npU5nR7jyaF'
        b'wJR+WY3pu+huc3qGw96jSkq19qgs1uQebYo5jehJj2qPMaNHdcCc0aMx2pLM5h5VqmkfdaHhPc02c7rNbkxPMvVoBf1IEqfBpgy7rWfoHkvy/JfiZZU22bzLbO/R2VLN'
        b'KfZ4E6cFPV5EI1KN5nRTcrxpX1KPR3y8jQhWRnx8j9aR7iC20IdycrHjrfyA1zqPv83ib/xbVlZeB7dyZ7HyA3QrLwNbeYHNyh+ptvJvslp5Sm/l/8GQlduuledlVv6d'
        b'Kyv/1rx1Dn/j2rfyL51Z+Xd5rfy77VZeiLDy9NnKTdXKY7OVV+GsnJJYw3oxk2+HZy9m/p+Vz8VM0fPP7q6HjXp84+Odn51h7c9jUwb+P1L6dItdz9tMybEGd/4YULIl'
        b'iTREH4xpaRQI9E5D4jkwXfekzbDabXvN9tQebZolyZhm6xnSn4xZl7rU2e9NWuMi+Z9VLeFMTBTX1Fq1yp1bXNRwBY9C/xepeDbD'
    ))))
