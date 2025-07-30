
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
        b'eJzNfAlYVEe2/+3bt5ulkc0NN2w1GpodROMWowIKsrlr3KCBBlqxgV5wS9xAG9ndWURERQVRUQRXNDknk8yeZWYyGbJNJjPvJXGSmZdkZjLOZPJO1W2QLS+Z7/++7/2b'
        b'r7db956qOlXnd36/qtt8KPR7KOk5j56WOfSSLqwVMoW1inRFulgorBUNytNSurJBYfZOlwyqAiFfsIxcJxrU6aoCxT6FwckgFigUQrp6ueCSqXN6lOEau2B+onZLTrot'
        b'26DNydBaswzaJdutWTkm7UKjyWpIy9Lm6tM26zMNwa6uK7KMlu5z0w0ZRpPBos2wmdKsxhyTRWvN0aZlGdI2a/WmdG2a2aC3GrTMuiXYNW1sr/aPp+c4empYH7LpxS7Y'
        b'FXbRrrRLdpVdbXeyO9td7K52jd3NPsTubvewe9q97N72ofZh9uH2EfaRdh/7KPto+xj72IxxvN/Oz48rEgqE5313uDw3rkBYLTznWyAohF3jdvku7/V5q+CSoVMmpvV2'
        b'pkjPIfQcyhojcYcuF3SuidnO9Nn2jChIQutUSUjJbnFOEmxT6CB24u0lWIIHk+KXYhGWJUH1Bh2Wxa5cEqQWnoyW8AEewSbbNDp1Fl6ECjq1HCsC6Hwsj0nA8lV0UUnI'
        b'0pjAOGgTsRRLY+OxOFYl5EOFy/qJWM1rNm1RC26CX7qrNiU7doFZsK1jNV9Vz8U2lyFLY8hmaezKGLjs578eiwIXJ+Ch5c54MGYl2e5bmV9MPJYnxiet9KOCohBq59KY'
        b'xSv9gmJiAxXQLAlWODh8empCmqLfBHPv9knidwxQhrtjCBRFIg2BSEOg4EMgcrcrdonLe32mISjsPwQu9HQdMASt8hAoo5zIEUJofnBKdu0ob4Ef/Gs2GxdBGy+mxD/0'
        b'nyEfrPJ1FjwpMl7LSgkcHrRbPhj1nCTQ+5oti1Ky/YdPF5qEbFaVYZePlGv4aLIgfPDk52JHWE3KU4ps1o6LnlWKVidBGzrKtH3DDOPqOwI//I7/5x5HPRR+fxZ2Z3fs'
        b'+IOhVegSbMFUMAPOAQ0nG1A/PywOgUvBMUFYDE0r/GhQKgKDY4MWJygEk4fL07uwURdiG8nGsQ5OY6fFTYGnZ9K3KgGOQwuW2YaxsmN4LcliVo3B/fSlRICiwCk2byrY'
        b'tn6mxey0FerocJkAxYmbbcPZ+R1QbrJghzAdLtG3SgFK/b15LRLch0sWKJfgATRTUYMAdTFQbRtBZWHQvoOKRGylwwKeEeDUELDzy+AE3sILljwVFmIblVVQXXBwLr9s'
        b'JOxPs+A1NTZhOWuqAJW4z4m3YyHsz7HYVFi6hgoOCVAC+/G+jQ1pBu4fZhmiTsfDVFIvQPXT67gxvKCFdgu2SWlwgL6dIGNwehY3BueezLdAqTAljgpOClADp+Ewdw/U'
        b'zcA9Fo0I14xUdJqszV7BL1lF7d5v2arEe5uo4LgA5WSf1z8e6qHU4iHkD5WvqJqil+vfh+ehBtuGSK4Uq3hZgPokPM5r2YSH12rMKtgDR6jkEl2jMsvV11okKHFTwN3V'
        b'gsJZgCsZcI8XhDwPhy14XbEhnC44LECFHvbwWqKgdCe22ZQ26JAdfRTasVn29H4ogDsabFV5sX5epUHAOjzKu+MOpUDdEbGY5gC3WOw2nNcUaR1twZuSJ7Dj1QIcwuNh'
        b'srkOfAAFFg8RD0KrXFdNHlzkrVgAjVTc5iziKT4XzlFPVsbzy3birUgqUeFpKGODQq0gh7XzVqjWGLDNqsKrUCFXVgHnXWVHdGBNMra5qf3myBfVZT/NvT0f6jfRccWm'
        b'3XT8IhmLiZNbdwZuYxW24TVJR6bxLE16I7TKw31ho4ZwTYH3CGzwigANHnhaHqPyUTRDXFR49gnZQ2fguMNDWKTXUZESbs2mL60CnF2M7bwJM4fiSXK5epNJnnCH5o3i'
        b'xuDAarDTeCs2JchXnKHzGm0+zAnQgBXUuDZFAJ+MzeQfPAy1/Lod3mtZkVMKFsrz5BRcgTK5fa0x0EEjqMDybXLT67AiRm5fMQGzxlmxDewsSgVoxKLN3BWhWIM07Ned'
        b'sJ58KmA7a8k5b+5XbzwAlzT5qpEauapqPBLKzSXAOaUGO6TtflRwjdVzgfrIuhuhCaUCtQXvU0kbzeJtYXJEekI9FaigeYtcSUMOXpFbXYtHR1qsCjyONcyR5Jl1IHsV'
        b'ji6AExqLlO2YkTRiVCKHa7K3xlWNLXCMvtwW4Dy2wlXbKFZ0wM8XSqZjJbRDqUpQ4hkvjSJpOHbaRlNpPLX0CpTk41Eog2KVIGU5zVXAXmibbmNMAG+6bnaUhjssQPNY'
        b'wQXKxJHxBJlK7pfRhAF7sURpw5uCkCPkwD48KE/ExlF4IU5CO1QJQqqQCkegwubJCu7oxsSp4VIAyyfpGfPk7t3cvZQ6DtcJouSOx+M922TWjJaZCylvF8Gl6dCk0idA'
        b'GZ7bFAln1yYIERaVhM1wLHCyjNAnoGSoxapa9xR9PiiAPQsLbf6s4AiU4LVuI1cIyY/yjxFYEAuX8JgkjMUyycUH98oRcUc7zYI3FHAYzsnIXQ5N0GHTUdnE5JGyHeiA'
        b'i8xQDFyZHgGFeMFhCDolJRTBCdnSBTOWUTqBTrjSnU9O4QkbTRUhkOhIR3ebLj9u084VlHJ4kw5Lam84zg1p8DShK5SKFCcXyNIpAU5iUSanPcpVmXgkBlrIPT1WwsfB'
        b'PdY+MhOkpLRRulAOtDtQlGcxS9G4h4zYBSiEy1DPmwP7Mnf0eEh2854IuLdJo8USuLhqqLBY66SBfVt5ylufBacpFW6Z4MiEvlt5zp2cP3qAkwnf6OtVLGNvzaxFQWZV'
        b'HrbQHGRj5k8J9zqlzxFY4UifvjNsQRzQ1wXzbsHddaxnZcpUahM1CM5SlJ7bBCU0AWLwlhrbx8XwcFu6YRMBvbCbpZlyynPYrrBNouPRIa69/cMGTFo2HeuEMdimpDx7'
        b'mIKF40Ib1ME+i6to2iWP1bFQbLXNoJIVUBXaa9R5VxoX9x40uJjAKmhJUKcmCHlw1Zkw9VYe76EhESstUCwFuMigd9IXS2whrL49T9BoHmHt6R45JTwg64fxIB6DAxkU'
        b'cjVCGNarKGXW6nkfn/dLY5QCi6wOSrFltzx6ZTlwoM9k4vMy0lN2+Vg4QvlXReSXdTQKb+6yuIuU1RlXqKFJ6YS3uJlRBOeDhIl6B2sgm5J2yYlmZ5U8uW/Q5DnFeMw2'
        b'aHPQmGiosoWxvlUTTDc+NlXWt108VjRwVIjYqSIkvUQhwRqWZ5M49zmT5qA+lPrsNkrcwjKsmNADAj0NIzNlsvfJHHmrTAjHChVRklK8JA/pBWiGakaZrsU6GNMcVxkS'
        b'7GlL+gayYyDv0J8cOHhZcsbCITK0nAwdwflVdayDXvnq+SD6r8XqAQ3DxnVktUXuNQ/mIMJXixYPyVF4gyZ9AZlz8oSTcvo+GrJYbvDNrdjO2No9ngAYXYvK4/HwhCdR'
        b'IkdFzawiSp+UdIu2s6kCB7RwhmI0ATudwidS6uSQWh+Dh4jfJXo56B0ls/28854LM/oiKoUVFqz1m857rvcQLFDvjKWjoUBOMI3L8Dbjg8ad3XTwOFbyiB8FN3O7TV3q'
        b'Cfl7eL4n5B3dP66yhMp8A89BxQ6y5rSMT786hol7sYjXFEnX7CUSSaB+xMEi4a6TLYD1psSPWEr3DO/JA5FaAneCp6V4REjCU07BUOHmoJ0NhFFbxQnY5KBpWrjD25wI'
        b'dXN6AIG38dJkPNfT+A55+IPhrmqTP5TwdmUTnX5g2aoaC9fk4S+jRlfzkMGbeCvRYa758TwagVWOhPCkEu8Og4OyJ4uwAW8xljh3poMkxuNdOYJvDaXSfjgVsZlSz2Vm'
        b'Zgx2KPFaIhTLdq4SCpaTHcWMTJmIH4XL4+WoLCbyvIfIpponCsY18Q7e4D3HBkppd/tFZVPfqNwZIkTkqaDK+VkOOGOfRrvFQxGzW+amJ7Fzqe1JZuoy2a3qjV7sUzgc'
        b'C3NEj1KJVzWJcvDUwoFFjOM+k+hguGNG8sy1a2h+d2Ou9krK9Wu7I/Cs5LQ5Ue7WA3gwgbFhqILzDjaMl5NsETzLWqf179QwaO2xKMF1t4T5UXB5imDGY87EZa6O5m6M'
        b'xksrOY2uDutm0bexQ/Zw2W48ROSSWMABrTwVjyeGyISkDesj+6ZKih8v2BOpVQkRcFoF9Znb+Rz0dg0jxi3B5UksiBhzLYIWDhvj4PbwvnOwF9xyzJ4dIUzFWhUlg06s'
        b'5UPx7AIb4/VDZnTzepJxzJa3ew8yZDzRbe7xVFRS74dsmqZYqnKagXco23N33p5CuEVqIJLjDJMDNDXKbIFU9gy0hMRRy5xGseDtH3CceC2DMqcJVNUFPr5zF8Adcsp1'
        b'px2ecj9r1nnIsXEC70553E3K4EF41mGGpe+p0E65bdoa7qxYOOmMbe5OeBEaZIp7dscEzrl8KbWV9g+NcDifKie3MXiN5hqVXJdh7/CqaZTKy8VouEh2rhMfzh7GpxvU'
        b'uUJbn/QmcwFi3aWUIvdRoGqhWYbok7BXj2154rb5cnxVQD2BJ2sNHKPZWdMH83l7VuU5Zi3YlRRxR56RHX0PjtIpbXlq3zgZ7SopJd21TaSyXLyX0r9b4rJpSurRTQp2'
        b'El1cAuExUtZcn2Eh3HUoNCjY7Ggodi7hEq3oSYdEwzsZfFjixkUxhRYBZxwKTYt1vMA2dSXTZ1YuK5k+y4Xr8niVzMfrAzBoJpxj3mKObmWOLozkfhbdyJkk5nw4l2Rq'
        b'bhOJdFayZgmWU4nCNEIOnMOwDy7wxAPXnyN8kkGjubsCuEEKz/4YNm7QnO+Qh9JuASamVHgqWSYYR+YN53xgA0FZ4yBMpTv+2cRYRKkqDGtUBBRXsUH2VvFoLnXb1Ynr'
        b'5Ciqxqs2jo1wDc85D5gcEd10jxl8itGx1Sqo3L6D+zEpfgiJVtGdc3vy/Gm4Gy9PkVMb8G7fXEUI0ZOrtvsIS+KdZuaQU1gvl2DhGiZ+sWWEQ/3CoQTepuzZlGj7oMTl'
        b'x06TSc8dZ4qiByqoMJp4D72z55EtFbltnyxHzzJz3GfQjnsm9TFHFHBbmqNxntS2W9O9oGiaAmrnuSZCATmeLzWEYiUX4FGqbv19bb2cA46YyLP9pUcEHnJ3DKZOiTcn'
        b'WvgknkpoeoGLdejAVodaz8ObHHFMicJADtVi7uZ3Dg5hU+V6E3yyXu5aADdI3KuhcZds6iQJtCLeqC1YTxK0/xzOiJKz8Ri8rWRT3F+OrJub8SRfJNjPGSxbJaCAOisz'
        b'xGMz/QZjiF7QLfXwgeROxmQ3BZFCq9c4q7ECmmRVf84liLdo17C4AeCFjZwg8hZdUeKVhSQv2ZRKhrsGjbNi04zulYkzlPE5/blOovLqANbWM6egHm4JSwKdnorK58nC'
        b'iKeyNFZJvUlG5CN4MoVXsHHyJr7AcYIEsrzAETOMFxhXYLHGVR3BEYYtIqwgDs0RrA2bdmryJbzLyWoTASCF9z0+0Xfvzu3DSR3hfAg7emHhg7ngyKlXNsMhTb4a7nOx'
        b'd0mAE1A52zZVJjTVS/rNzbvQ1D05oW0tlmHhJjy7VjBvJnEFtyfJAX1rBDZp8lVEKm851mW0UMnTIlQ44fEBEEFxeZgxHZW3Q121kF4g29dkc/bheJct5iRR3pBXcybi'
        b'QR6Lz+BZwwC1nkBo3tEbIojpHlFZVZP4lEihHM0WgKCUr8ywFaBRi3g9ziHQwFaAcD/ecCwB4eFRMllqgBJ4oHFXbKMUgfcEuJilsYWyOCQcvTUY5D3O+BLUjacuNRAD'
        b'SZrFdRip74voEIYRsJ+dNYBtXFHlTVMscXaaTjPpKB9WbJ6J+/qrye1wjCJRlUpjkSCEj1RBqSafz+/wjJV9JIA8CWYTJZXXMeC6JGkpOXPLnVAaPkgnCPxknjsWiyXn'
        b'NdDOLa+itF82EGASoNARgbOV2GnI4j3VRdK8HKAQ++A3lvmSd46oKMQvY4HOmQ9S6kK8onFXEkdly6/3BcrOd2ThvngVFGnwmiJeJwdjA5Z68dELCsIODSMd+7CFim4R'
        b'yA4njOXBshev79K4iMT+O+Thu0BTpF1eEDur8tDYJNgLDvw7MUZmPsPhXorGIuFJdBCfqkxs5iWWXDiusTjBnU3yLDlF+eAch66ZUOsDJQwCaznN6SS8wQ6082haR6md'
        b'Co9AkWNtDy47AhSK+GKgBG0r9LlQslJYvUGN9diQq5N413YOW4ol8YuxVCko8b7iebwGtZOflaP3LNzaCienxWFxvFoQNypCSE9eso3han8zVsVheQiWBehIfLey/Ss3'
        b'T+XwZQpZ8lWuhhMBiUExkiDNU1A/m8jLByYvTGN7St0PtSBvOPHNpiiB722xPS22v8X2tZR2lwwXx46WVCQVCM+rdrg8J/EdLRXfxZJ2qZb3+izvaH3wZ1EQXLW9HpFs'
        b'K9Si1Zv4Hqg2I8eszddnG9ON1u3BfU7s8yVW3oH135xjsubw3VT/7v1XrZGs5euN2frUbEMgN7jIYN7iqMDCrutjKlVv2qxNy0k38P1YZpXbs9i2dO/z6tPScmwmq9Zk'
        b'25JqMGv1ZscphnSt3tLH1lZDdnawa59Ds3L1Zv0WrZGqmaVdkSVv9bI94NQeK8GDXZBqTJvFuplpzDeYAuWrWAMXxEb2aYHRNKBH7JFGjjFss7IuGPRpWdocOsk8aEW8'
        b'b+btvSuzdjeTXPn967GyXW+HtWBtgs1iZX1kfl+eFDQ1bPp07fz4JTHzteGDGEk3DNo2iyFXzxvmzz75aw00NWx6q4FvoqekrDDbDCkpfdo70Laj/bLH+dRy9EW73GjK'
        b'zDZoo23mHO0S/fYtBpPVop1vNuj7tcVssNrMJsusnhq1OaaeSRpIRxfqsy38MHPyVqOlX2cGbKQ7C/13cb0SF3KiADeDEyx5Kp3KsT4Grav5/uzGxFFCqN9kSUhJmfNg'
        b'uFrg674roT6ZbW8JcyY9KzxLrOsMP/fn4zXCMClHJXimBIKkkzd4QzXuwtj0nzsJoSlur3iGyQbSN6ZbNOJwpWNxJxmO6zzkha9mEga1VGbycZSFYZlc0oDl/mz/cA9f'
        b'yWEbiEHyNXEp0GrxICidIF9SBQ1wjGOVZRbbHxkiYe1UGWrrifY3ymIVzo7WmFV4ZoFMQap8SY1xkDqFJVipyVUSTp6XNfEJOGGQhchJaINCTZ5yu02m6LVwfwR3X9QC'
        b'ylwlborEdHnbEY/Pl9GymFLUPmyzqHfwHVnSLodnDpFZZynugya2Jwm31shrUxUkeusdG6xTZrBdSSh4Ul69OYp1Wx3bVr4ebEtSwe2xPUn/7g23PYT8lRpyUclWOVWd'
        b'8s7knX0O27XYZlaZR7FVGNKeSXiSF2zIibNspbyilRf0Kkgwy/uRjM5sYdub97HOsW4GrSN1Sj56prBhrOhaiKPkKR+5/uuebK3ErNqtcFSzCi9y7+CJiZFUj5XvgLN6'
        b'vDfK3rltxBa2ophBKdKxpHhogk7ktRhXP8+KlBpHSc50Xsu2zN1s5xnuQ7vg2Hve78xnmvtUteAWuEQUtClu193nC3LVjaa5U0Ol8Gjq0xEhFS9hkTHO9qxkoewgVOX7'
        b'THvt2mLlfE/1b6vr3p199mDRiAnHyjxSZsUlz18ulawZUuQivaP6w4JlxCzbR5pedLJlRHXc/joj81+dx9ZM/NDtib8u+cBH9Xnnnt0F5+asXOQ+/AurZUKTh3fAprqq'
        b'GW+2nnluqtPDenwUvumV8Pybzh2n3nlm3pf3Xpt7dParDWe+mJn3xagpuU803PP6fM7nLavafPd/9ftxXxTYWq6+6/TJq//5zScXPtH8LeBvU//S+GjJ17/qnDayec17'
        b'c679rK7yrXs/fxh5rCBK7fubcffMX+0s2N22M3bJN2aPBUM/OvL1P9w7ltzfsPxfr480xnc+FfbVnNFvm176UX7aWw0R696ZVH8V3NQhD5q3bDgz8RWdk5VN+QQ4qw4I'
        b'8ovZiAeCREENNWIQHoYmK8/pt/JSA4JjA/11wVgRSGrh6XjBRyttdIdy61hePgUOxCUFwcEkRgi2Q7WgWSqyW1nwnJVNc6gaOYfdjOMfhNVwLlhB9veJUyf6WRmzmzUj'
        b'i8SgfEPMVvmGmPwgfywOEYVgpQ46VXiD5OJ52dDxqWYsSQiMxdskiGjyqyNEd388YGVrKFQZtsbJFoDsce6CDyg+hmOhEm8NXa0Tu0Q/nVnFOKILf/veLww5Hw2fk2HO'
        b'2WEwaTPku66CWWKd2+XKYT6ZfWGnWVIZ1O6WdJLCWcGe7gpRMUKhVkjfuItqhfiNqyjRcTde5srOEcV/uSrZuays+10+Q9wzjJ/LjrorJP7nqhgruinMTt3t0qm7JFZ5'
        b'l5LydpeTIwt2SSxtdTklJ5ttpuTkLk1yclq2QW+y5SYn69T/c3d1kpnxLzO7DcfM4srM7gMzM17Gqz3OusmiV9g79qFaFKlz7FVSqP/FXvmSVsp6OM1GA0/B3t4j4hiN'
        b'aKgnKGHTBy7lwY04KsKSRCxPilXhrfGCe65yxmis45vTbsTg78XFJ3JWmRwboBA0a0UkZVEro3U7lNNsuAPNvfho0bA0Za/Exzrl1J34Zgk9d0tJGZKDRyqLlMQjJeKR'
        b'Ss4jJc4dlbuk5b0+yzenffCWoj+P5DfS9SKS5pwtWn039etL8voSun6EbcX/wCvNhjyb0SyziVyDmbjlFpn2dN/d1zfxJ3XzAWqI/zKq0bjFEG0255j9uTE9laQPThdZ'
        b'e1lzZcrYvxODciVHp+Qr+vdwsCoYwVyYrc/UGmWam5ZjNhssuTmmdOJFnGdasnJs2emMN8kUiBNeB8kdnCFFG1mXHxMyIt96bXiQ1ZZLRMtBu7jXiC/6sTMCWUW67+BL'
        b'qgF8SZVoY1PIyzkSS+JI5g24c/BgvP/iQGheId9EyA4kxccmKGimw0HNzG3RK4yNXk+qLE+TkUkrqh6mBGcE6GMqm/XZGdmpf0zZ+MJbL771YiXcqJx5oOl4w/FrBU0x'
        b'Nw40HAgr01U1HJhQtXeqUtC9oCk+OU0nWtmuNlzYtFTjT4ILD2JpQiZesTnwczy0SXx/qMHqy6I6SIgLXpwQSJIwFsq6w3E03JBM3lihE/vE/7eBIAeBLo186+hjzHOX'
        b'MS/dWeGtkHHP7NGDT6ou5+451eXkmB0ywLixF3ZrZ5/alWYv9pndISKfxoGH2fv1Y+Dxbh4EeFg3h0/24N183Ee4CTVyP8Mm2mbTKZlJYO+lipd6yLq4CY9BIVyHUjgd'
        b'qNwQFwHleXAZzkOnK7GGw0OwDktXcc7kmYKdq5do8t0VgoJoKF6ahwWcmczBZjOUajT5eaykiMgJlDvL+4amFRbs8AiXBBEPK+A01ozA5u3yOs/hSROmeFjCyVmKHGLh'
        b'xMHqZAZ4PjcCWhM0+flqsrZfwBoj7CPUZPZMWEbtrJz8GPOIuD3gDoASsGNRjwg/Cqe7RTicgxIZMxuxGVsisTqAUFUhiFCuiNRh5QDM7BELCxhmKjlqyneXinbnDOce'
        b'7JS+F3YyDf71t2lwHvR9Ffi3IgdDGXb6dyvZbxGY7OL/c32Zls2bZTFYByrKfg1kfslJS7MRSJrSBja0W1NGL5mvjaQkb2YgGkXJIs2aYyaVmGtLzTZasshQ6nZ+pgPU'
        b'I0l1mvXZA+wtoGgN7tU2PRsUG7/33H955Ar/QHqLimJvkUnLwuidmue/IHwBL4iM9A8cYLFXn0iv5gyqjFknuZ9zZT1MVtMZnm/P7edA9vhembLHYk7uwATJHt8vSfYZ'
        b'vP9VQa4QBhPkHiTI5wl807SN37n8b2QYYu3tLMtgNd7mkihjuY8QGvOiE6n3saOEhbIir4kbKjyxhuFqypw53gmyIn8erjIFS592QQWJ+mWCLFIP4gUCkRIogiJKiUMV'
        b'gdNdSImf5obum0jauz0lkrTPvu06QnAINzMehANs/dGIe8OEsCw8Y2OQHojFuVOpm9A0MVwIx5ZR3MYHz3oJWs/1KiE3JTB8WCizwbB+JxyPYib0NrKwea68RFFPIr/N'
        b'iW3JjF8iLIF9cIqbKAx3FYateUtJyOz2+bMxwgrj+b1fKi1XWFd/NW9yeac7hLoVvlqbaax5DV7oOvTURy/Ptl5+6VWTremlyhXR2jUXK3+67lzO4jd+/JOtc+ttCzZO'
        b'bfd0rfqvSWFXRnz6N+W1mo8ikwJm+TVUvzfjw1Wb3H7z4bwYS/Ti9yZU+1w7Yv6LZn6Jy99Lq5/r/Gd0qO7TipIf75/yu5bVV7xSN+z94liBYejVmnbN2x9lL/xq+e8n'
        b'mmfChhFJt4M/68h+0Fzs3/7Z1F9PrtgaVPyZx/szwi2/P6Fz5nJslheUkRyDfVga063HFsEe6wQqCw8c+jjb27D5ub7ZvinRyna4N2IhljN0J1XGpFkInbPSFsQuinMS'
        b'wvC0OhbubLay33g8j20umjgs1SXYaGQc1oaDXXKeAletXNaXxswggUeJIl9BYq1lPlRiCW9oxMS1TNmFEHvvSGIt3SX6480dVnbLKbRSWj3K9JoKTsV2y7XNuM/KWH3I'
        b'Vr84LIvTjU5xqErBI1SZCcX4QKeQaYDzv6XOZGLiImsxyhKcloTKtGS3TEnYq0gyyk0hyzAmqJjQmkjvPo4nEZehj4nLYxnUpSS87sVXvktBKXspqGE9HIaZ/uwxhxl9'
        b'ZBAOo6WSyXBvSI+UZaqaYKBILXihXUlZv9SgU3BlRGFI7KT3Mr0nUZhaqF8z4LciPepnusDVj5gh9vwmRPG9fhNCyufRz/tA2TIZCr+FwGdw/s2Tbu9F8P9rxfOtWNzt'
        b'qb5YrE60MZ4Oe8Zj7SBI7Ist30H3x0IRJ3Pz8RDct+SpoH589/rqnuf49vJw1SYKLn8fLE7A0uVYFC96R0MT7IdGqKYPOmGJpxN0wHG8b4yMDVNaGIP9y4ZdD1MCR6cx'
        b'5eDQDWteuFXZcEQRM7UxNCg9cESwPlGv/klocMrHKWt+6PPTF34jCktqhri2ntSprOzeJejQ4SEGJITudx1g0gdJsAYPWvlCYPUKbGWLQ0GjVzmwaDje5EtDUJc+KyA4'
        b'dgLcf7w6xNeGQnda+Y3j9cSAWxm4uEKrrqcCDi5QHsphwrRuInUfT+JZxwKSvHokBcgxKA4a506ZBmtPlHvyKKc4n+DsWFJxVZhHdF/QpJSXMAbVGk0KuZBHJ7vEhwLH'
        b'4sOjU9jr/tEg8ckCD2pd4Hb3khe2zu1udPzK7wg80S7824FHtPlRc595uzw322i19ESXvP1AIaRlRzPM+ky+ndAv0rqjVa+NGFQT9znZLzJpZeKKZc8GaiNjoiPjlq9M'
        b'ILE8PzEuOTIpKjpQOz+SlycnrkxYEL1M9z8r6MGCimft9RvUwhNjyZ/alEDfZH+B32GNdmzUsd/OBdCsodhaGtMtZJolPKyDJleo3k5PBV6OhYPbaQqqXaFo7grbEyyp'
        b'pMFd+Vo4nyBfTvHE0dEXL0pwZgsWGKvS31JYkujsA58eGP6jMPc9Ws/oF785fb397O+WbNz70sayX72RFf/muhcSfpD/svGTHXnFrkkxlbbm8NuJHX8/XVirGX/4l/t+'
        b'0eSz03foN2Fr/7g24vL4A6e9CqpH6SQeLlFDcQ/L3QeDe1I3NO7mChw6h8BVR6oN8l+EFY+jAU+M51cHYOk4ljLz4UhPylw9hgdbDFTDvTiWyAkd7gb5qQUXHxEaCGZa'
        b'+8jnwSPGlVSHpZdiH+YIGucwtrrozFcX2bt5dM91I/tb8+kJFXaSX59QeetbUtkIPLUlICYQTkKdf+LjZYcRcFcajvfxCKUy/mPT3eFyHiNdXhECxRwJMpcIo3dLWbPg'
        b'9reHlWM1j//ysWc17/uGVhYp0g39V/N6pzW+7GXSb+HaZ5BsxpQP28PLNdABynp980usHGDZequVhEyanlJTX6M8yenT5QXDARKuj60eOfddak5Wb/+/ZlnFoIDgLGfZ'
        b'1bPx/L8hd6B6oyPJYiXWckhZljdKINI3IzItZawyKVngayWu2KzEw3iasm936q2Fozz3+jolsuTjyLx4ZvngyVeNFdz8CFf+S1e/+7oUt4TRIwWjj8s4pWUllRS9BZSQ'
        b'e6XjT1KyMuL1P84I9P5jStbJ9S+89WJrZVhVQ4Fe8YsFBxI9f3YS7lVeW3OlcPJ+VcupUS2nVh5uOK64eKpd3XJqqlI48tnwMS/9Wqe2MlSjoHgwuRfnd2RRvI0n5VSd'
        b'Bxes7J6aqDn4oBfnh9N4O4kvrGM5gU6CSngqUb2LeMxJvptigeMePK0zlKrFBxypLhOxZ6vyc73G9uz5EPWw92R2vO3MTxgGRc/1QJktpReS7RvHW72WEnqhnCP7tMEH'
        b'Do6HwxLW+UBxN9X/rvVGN57uaV6zqOHwNaI750c7E5+nnC+yvM8+mcd2X6tTdmkY3iXnmBlX6MUABq2PGjOuB+CYkVm9Ac775W/Z6JhuWtenl1PxjtxRuZc2aNMpExMX'
        b'6hQLdWLiQuMvyjxESzQ17/zNV1e+4bR86Hwf9W/f7YybZPV6qbiz4UzqougfvBf9A/HNX2vP+HmOee/ZDTdjvvzsNb+aa2enZP3xX4vefzvdp652+3/cv7Oz2k3lNPqd'
        b'1KcqKyvfXbi78xv3lQE+Y2Zd+eEroV+fXKfIf/T3Wz4PNatcCjdJ8LNd5c+/uzA5cv3Ew5UF1xO+jDr35/E3w68sOVq5a/ozD1WzVGfOvjF1aan30TPZL7VGn5g30/8N'
        b'72M+iy6Fnlp19kDivKC6olhr+PnXmqoWPgyt+/kL8bM0bR+P/WnjF6H1wS8sWFsRbQ07/po6MCHuVFv8n9aVL7wjBnzs33J+8z9nvZk6bgvsuKMYY5w6/fWf3bmjCrIG'
        b'dLz+6Vvzt6aOfPfyP/6WEvKu/Wtj9RdJs/YUlHo0HPN92WvHsC1f+pT/YuiM2Ldfn5/0cW39m+/vXLj61d+NffpqjnL96TDrGyUfnTnxWkLIh4s/OOe73vDckM4bHl9H'
        b'lD/8Um16Y92tBKdc+9pH7775q7s7Pnz6nQseoTFDY96wb4sa9/Xbtx/99dQztUcu/sDT90OXZduKM31e/uJQbuKOH68cNSlgbdSiDXevN14OXFp0tnTI2zdWvHzD7Sc/'
        b'9V835CfvLbzXuqK99di64y5r/AM2GH405cXFnes+OfCu+euoysTqr/5QOPZjvyc/OTojI7DoxLZjpV998+Ts0DfHvPjw6N73/1j68rD3frulYdJHf3rlbsuXLz3T+aew'
        b'fR5fFSW9c/yDd8Yvyr1e9OSw2X/4qSGspv5v6btc65dfb/2Hxvyj1vfGPbp6fs0/inP+XpM5bNP7X1je2fxS/D9feBWyfc6sjDq8W7HvBa/lL9YSQrBEHrMeT1P6VMBZ'
        b'vCgoZghYvnsUj1Jon/oEi1I4HNiPfidF89WEdamBvZElG2701gATieezAEiHCriKJYGxWBakFtQbx6eKk/AUHOVKPovQ8mLA4iAsio0PFhJVggauiViXARVcA6zHm3gq'
        b'joE6nUEhUmGKZadcFbEZS+Dgv7kTq3P/9zZuv9WOyszS0KAvHHKck5Ozc/TpyckcbnIJCsRJohih0LKlhG/UIrEm0VkpuooKQoWvRSe2a8t2ciWl+LUkif+UVOI/JLX4'
        b'SHIS/y45i19JLuLfJFfxr5JG/IvkJn4pDRG/kNzFzyUP8b8kT/HPkpf0J8lb/EwaKn4qDRP/KA0XH0ojxE+kkeLHko/4kTRK/E9ptPgf0hjxD9JY8ffSOPFDyVf8nTRe'
        b'/EDSir+VJojvSxPV70mTxHelJ8R3pMni29IUsUt6UvyN5Ce+JenEX0v+4ptSgPgrKVD8pRQk/kIKFt+QQsTXpVDxNSlMfFUKF38uTVX/TIoQfypNE38iTRd/LD0l/kia'
        b'If5Qmim+Is0SX5Zmiz+Q5ogvSU+LKM0VQXpGfFGaJ74gzRcfSAvE+1Kk2ClFSffEaOaZx3/ONzwTPRWeCrZDJCrdFWMV4jNuimEK16Gi6MO++fESd/7q6awYrTD79gJy'
        b'MTm5F34P+X8ff4V5fA/Ys4rYThonxVPeHwToWWLAs9O9oAQqiLYT/6D0WuEkGIe4j1KOW4NFxviYJoWlmk4r+OFvg0oSXCF0WOF/Nhq7HhWoRhZ/5DLnwKLcCcH77bcq'
        b'TYFFb3xWaDS9/s4vo9KnT33/lYt+n330uv7omz8ZJ33ceCRs+dC7XlnX3xzzg8m7775v3piYtamkY9unKp1r/cbGjPlSZsTDJ9WjLnkmH7y5/XeH4n/5r7cjfptXZDr/'
        b'zKLQs40f7oOauCtZtz44fvfh+roR9W+kveD1q081jdF+f/Jr0Q2Rb9d4kDed/2uUJOoIWwzUsG3M6yJejB3J1wM3zMGjLKPtScNr7DS2rueF95TQQODCdYwnnl8je4Jl'
        b'OihjnlgQ4e6t9MUT0MIXBqEG70FjXGzCIiz3T3AS1JLovBD3Wdnq8NzYqIDFKmHBQkWcgFVQjyes7HeN88LX9Cd/UB4ykSoh3CpnyKEUFsE1J6jIwkarlnXl2mYo7H+N'
        b'WsicPTJK8sdb3vy+EB8sG49tWEroE+KfJ0MglOIJYbRNggNwg9gQW4aIgHLcw7RjHJY4CVIQXvVVwGWoG89hEgpHbeBZPuRxY9KhTRgDtRKch7IY7hcsgpqpWKKj8+RJ'
        b'oiC6iUUeS5UrN2I1Z0UeYVCzljSO46RA6qGscxWCFttV7Jb6g/JdN62W4QFJgeyfS8ij5JuK90W8uQKv9FF74/538PB/8UWn/DZANZqMVgegsh8ZOQ9xlW9tUYr07sZv'
        b'cRH/5Sy5OtZwnlByhhdi1vYAwfguZbbB1CWxTaEuFV/G6JJIDVm7pHRjGr2SEjN1KS1Wc5cqdbvVYOmSUnNysruURpO1S5VBiE5vZr0pk642mnJt1i5lWpa5S5ljTu9S'
        b'ZxizSad1Kbfoc7uUO4y5XSq9Jc1o7FJmGbbRKWTe1WgxmixWvSnN0KXmOiyN72gbcq2WLq8tOekzn0qWV6DTjZlGa5fGkmXMsCYbmD7qGkJ6KktvNBnSkw3b0rpckpMt'
        b'pDRzk5O71DaTjWTTY4CTOzvOzP57lJmtipjZToiZcXwz85yZ/Q7BzJbxzGyJ28x+F2JmP4A0s0AyM2VjZutNZjZ3zWzemdmd8eaZ7IX91yMz2yMwsx9HmJ9iL+y3N2Ym'
        b'pc3sniwzA0MzCx4zW2w0M21mDu+BSzYcrt1wGfXVQLjkZzxy7r5NqsszOdnx2ZFTH43O6PuPq7SmHKuWlRnSE3XO7K6l9Jw08gx90GdnE/ZrHVOICQA67kqDYLZathqt'
        b'WV3q7Jw0fbaly623GjU/0+3GXi/yPJwj/3esuUyKWhgeSYKkduZzbVicyFXEfwOL23gx'
    ))))
