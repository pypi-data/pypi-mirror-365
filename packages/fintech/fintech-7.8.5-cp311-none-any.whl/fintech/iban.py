
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
        b'eJzVvAlclMm1Nl69QTfNvi+CjcrSyA4q7gIuIJsozrizNtKCgN00iLuOSrMjiKKCIm6IoAju61iVTGayNoZEwsxkTDI3uf9MFr7EJGaSm/xPVXUjoGa5v7n3+31t+3af'
        b't9731KntOc859TY/Q2NeIuPn7w/D4TjKQevQZrROkCM4iNYJVaJ2MXrDK0d4UYDQFYFJ1ljmiIRIJbkI36+MXlWKtJbrhXDeLEc8/voDAjhrrpqgRYByJKuQ7KDS7Mtc'
        b'i/iY6GTF1qIcXYFKUZSrKMlTKVaUl+QVFSqWqgtLVNl5iuLM7PzMzapgC4u0PLXWdG2OKlddqNIqcnWF2SXqokKtoqRIkZ2nys5XZBbmKLI1qswSlYJq1wZbZE8a0yhP'
        b'+C+nPfE5HCpQhaBCWCGqEFdIKswqzCukFbIKiwp5hWWFVYV1hU2FbYVdhX2FQ4VjhVOFc4VLhWuFW4V7hUfFpONI76F30dvrpXpzvZVerLfRW+gd9JZ6md5Jj/Qiva3e'
        b'Ve+ol+it9c56ud5Nb6YX6gV6d/0kvV2uJ/S7dLenEFV6jO/L3V4yJES7PMefhTNe488I0B7PPV6r0NS3lpWh7aK1qEwA/SxMzh47qlbw34F2gJlxKqxCSllygRSkQhch'
        b'stRYw7eMxE1Oy5HOB74m4V5SS6pJZUpiKtGT2hQlqY1fvSLIDPktEWvIFfIYX09kt/9QaoYaYt0RUmQURBe4I91GOLmoBN8l/TKr1DjQURO/Og73+BN94PIkcmSVlFTG'
        b'rQaddaR+OugndXFJpO4d/7hEUpecmLLaHwr0IVAb6UpMjVu+2j8oLj5QgLvEqARXOs0kB2brZkING9aQNtA9XglorQ5JjQtMIDW4A4Sa+ERSFS9BpbhetgHfJA3ZgjF9'
        b'Ym3qkwY4NFtVQL+wQRTDAJrBAEthWC1gGC1hqK31NrnWbABheleKJwygkA2g4LUBFL42SII9QuMAvrFsdABzJw6g/A0D2MUHMNjPHH1tvgcdAcv4yDzETjZGi9AaWxs6'
        b'qoE/nGPDT34SI0XdK/3gXEaBQj6Zn9wVJEYZYXYwaBmJTqF70GVUYAGnnbNdxS82qRQI/cTvd8JbYefXrBcUyGjPx7SIbokybOD68E/CO70IYqefFv0uROPpP1m44rng'
        b'b2vk27+JhpEuGArS4mEuVdOB8fcnVSFxQaQKX07zh7lQHxgcH7Q8SRCGb6NCG9l8fByfVoboHOEmfALhO1pLAcLHZiDSAh/IhRVsCCIntRoJIo8sEKlGWD8b9+rsocAO'
        b'3yzWasyRix8itQhXpWxn1y9WCbTkFkIzSCsiDQjXkNtinTOt4RA5gBu1uE6Mtu1E5CzCbaQmkd0zD1fgZigRopmzEelA+LRtns4JCtwEW7XbJAgfIfcQqYdKcCM5yErI'
        b'YW2ullw3Q6R9LSLNCDeQ8746F1rPJVy1QasDiztJOyJHEK4mp/BtVpFTCunRWsFNnZsROQONzifHmXHkSlCalvSLEakgXYgcB30ZpIf3TBU5b6HFNQh5pCFoFD6ZmMQq'
        b'IvW4C1do5UKkxE1gB6jDelzD9Z3Fl6HfykRodw4ixxCuA7M6uX2HSAe+pLWhbSBV7L6W5bietQp3zSeVpN9KjOz8EelB+IyM1PGSc7iJnJDDQLwbCNbCPbjdjtt3NDEU'
        b'V9ORu0iuCKQIX12k07lSG/RQa6uW9AnAbBhf0ohwvQ/hNfnFiEi/ToRgbtSyLj9aih/ymq4W2clJL/RfjxyRazAY8fgsL2nGF321ZUIkwL1MWxVuduclZ3eTBi2MNMKV'
        b'5YjAXDrimcSsI1enpmhthIj07mTVnLTGp/mYbyTvkX6pEKmDETmP8Klw8piP7G3ZKiiA+tsjEbkE9S8k1axByaQB3yD9JTAh+mGIaDX15AI5ynu8F98m9aTf0gylF7L7'
        b'2kjzIlbVSn/8AAoEyAnDnOwEjWU7de70nptgwwnST67DwF8j9xE5BxMflPP27lrrCJgKvXcGn4OGQCvJQXc+hnpci9uhEKw8H8x6qWMu6WJW4iZ8GJ+BMhEM0m6wi45d'
        b'I+lkKleSbgJArTNDobDI6BQ8YiVjKr1A+1EYehjHO2AGva1jE6nk1R1Qk2NgZr8AJeADCGYoPkUeWercaBvuRuFaWmaOyCF8g82a07gTn2D1haeRPhhMaENHGmtCmxc+'
        b'rKO4hmvEYrlUgLRTESxXfIHUbGP9KJ2GD8tJnznCPeQB9BCYMYM0MmXzoI9vyUslaB0+yuo5EQJtZmu7Gh+CSXNLjGT4AiLXaeffCmM36cj+vVBihlSbEOmHGQ1VnWYW'
        b'5BQIoECCwmazas7iI4F8ytwhDxy1JQIUT6A5eoQP+8n5LKvE10mDXCtGubGsz1tIRzafM82lYLWFGZriDB0CKwHfx7d0lJDgg/hMMK6eCVPnJq6RIBHe50M6BCm4Hjfp'
        b'POgFZ8hdML+6lByFMa2SILHlzjwB3k8e++q8oHx6lNhYGG7SIYMLK5YJXdLxEaWIr8GH+fg+qQb+V4QPp6IicOU3dHa04PLSBQlA+7KwPhFlbTD2PXlMziUkgGPJwW34'
        b'MRwbMzmitOJeO9pycgV386aTywAN4EDQZNIMCNAEi/rKTHxZkpkEo35+Syw+ty4JmRVFaiW4meyDRrO10O6Jr2hhnWThy4hUIoDXgzABlVAkwj2waIxqrpJmmHP6uX4g'
        b'ROIrpFmMJpFasYw0kiNMkQvpwQ+15AZYdLOEwXkdfhjCFEG/7YdlxTThW7iTqorDl0T46qgq/FAsCk1jziIvZAN1LqRjN3cuQjVT4kTOkkcma3q4NaSXXGX2dHN7GsVm'
        b'662YNd4AsPcBiYXoHZh95DTCreS0lPUOWNILupricDf0Dle0ey+oCaeWgZogEbmz6h0+WD0LY7UagKp9PgD3MEPE5CKzJgmAuXq0b6CLgdWchLF+sEWuINW48x0HtFxh'
        b'LrcN4nOultRYM8/YgB9y12g1XRdEaUMYVD++i8sDqXCN1NKPLmpRkEayjdwj+7lJV9xsqC8l93y5M8Xnd+hCoGA2OUUejjarVpSVxOzB58hJGH1cDYO/E1+KI3fMAMuu'
        b'bGHKdu1ZBKBPB68PkTrq/h556KZCwQow4JIZ9POYboqD8RKvRB6kX0R6p+Swfl6MH6dpLYQIPwIYpcPVDDc262ZB0YzFGWOGvHbMsLEh60yiiruTzLKSPNagbfiaFGgp'
        b'eCreYffxxUgtrhIjn40M+mC2mzPGgnuW76JGXQWjysCNMYUiAM1KmPSHc2HVnURh5IwE15E7wD7oEtqbWsJohpk5ZxliXKXzh/OxuGvBuAkVh3snsTnZxedkk4g8IN0O'
        b'rKF5UtyrtQbn9BjXIXKSYn8T6WN6FknlE4awgJxjbbzMp2WF2JzUGVE2ZzdpYsRGhys5s1mJW9lUIGedJ73SUzvGqtFlUobPRO6U4BNhoRwDHoFHqmBkiNwVcjY0FT9g'
        b's2HlTstRBBjtddBSyzufagO8ux1O6iW4vWwXh+Yq3OZLSZSCPOYcCpzFSd10WtU5XG8xfgXD8ru57pW2SaRHLCUn8CMjg8MdUYx04dZUTrrwg4W6UETxrRbrJ9oGboAq'
        b'7ubtZss5CBBWG2HkExp3sh/UmcPsa2De/Cg568k7oQ13wNBQEndvlZHDHSctugB6V/DoAHfRiih3xUfK6UzBhxW4A1ZpEnloHq7ZY3QaimhK+fDDEk75CEA7n3WXCl+t'
        b'U46osLTIe+v8Z/LWu5EWLT4jBRToIqe4ss6ydxhNBLTfx2niinI20Dukq0yqrvDmB+O+MWve2PpjEm0gOAEG0vUqUqdlfnvffGgxzL6lMM7MAz7C9baUWJIDyzmx3OzH'
        b'2u7jCHzHNLtHfUCsgjQxdCJ31CnktHnwXnyAw0qv4zuUr7nh+5yvmQGhoMMF7uwCPv0KV0Df5k0mw02zQYyC8X3JFnycHOaRwEpyR1smQYXr2djXQpRxgOFmCLlODhmV'
        b'dRl1PCLnxzgVPxEs/voVnJbeA1dfycliexkni0DrjnAcv/3ulnHwFK9jK6WHqvEgt0RQVbeJLDfPwmdAjwCl43rGzI+i7bzkchrup6xTCYYy1okrQ9kwTcOdMRPW4+UJ'
        b'6zF5SuQ2CVCLJhVrtZsCv6e1AdfVB/6YEtXWtYHMVFByQ2RCLaaD1PmBYPI4IhG5FoPvGklQ2zJGdhWFnOyCRQ8YzqSZQ/8aDbrG+04MLnrMCjwnNteA86ZdZwfe4Czn'
        b'xtV0SCk5htXZrYtk/VouflPT2Bkx7rNMil6Me3yRhjRLyY2tpCEVbqQTMYs0L2esWoHvclINcSGPl1JCpgJagPuXLGLz8Nh2CL98GHvcKB/rKaco2eKJVUhQJG6XADkA'
        b'dsyaPisGnwfyLUbLMYzFBcpc6wRsLOxDV46bgSagZY1naJ1mG0FOSXDjStzCPUh7zkLG8COoY6IU35PcZhMan92LH7/Cn9pRdGBnRNB6qy0zBLh/U6rEPAr3L2Ctc1lJ'
        b'ulhcgM/t4XHBwkRdIBSUQisTmCcDFRMWGyNcG/HNlbjW3Js8XsLn9HvkIkBnP+XN5Pos1s6TayEyocuD1HnGmBqKbzgbvTjTRf13BL5JHdsZcp4ZtWUrOMB+a3P4xjju'
        b'OdIZwWYKOSUqHbc0tOQ4m25dfG1ch/kGSLifA+hxXJNO+qkXAd2wOvqAFG9RsrHbTk5Zi8jBce7NSAMm4QOwUoGeVrP+Xkgq40n/NtBxJZItMKqIGYNPR2SNg/u4SNcx'
        b'cx9XiIDbUKLPjDmFz4WDHgDhgxAbUKhrWIErdb60rB/UVJAK4AkTWImQspLbsOAnA/jSTl5GbuFbPFjD7+FbpmAtkE3ijeQWMEAareGLOTxY8zC6mfm4OZuFalIdj9QA'
        b'QfbxuKoPvt7joVqbGQ/VtGQfX96XbMPGm9S7nIHEVd7dvXR5m4Lz6+Cu9rGwTpLMo7p5ct50CCn2QAHgR6MFW0KNuJJcYn2oAFWnjQDSxQHkDjARkG68gpAbpek8qjwH'
        b'bT4AmiTQD7cZyWgiJ/EZxgu8SmHBjWcrbBFdHcM38TGPMHJSgk/HLDTOkFKg+f3kphnSILaYTsAY3OWs5Y5q1WvTI9JE+Jg6y+1h70rA/zfxEFs6cyfErkIEzpJ1fvtC'
        b'omceK8odHxvvsShMjHqsDHxhRaL5bHLAGMVPx+0wR1gUfAj0sCg4ZKEujPbANeitC+MRY5RLmboMcPVKBH4swfVpS/jQ9OIaCOb6rSSoJJlFpudcFzP3v9pWM06ZMNto'
        b'nC3YdmemHdYDYJxaZLEZn0yOjuCD0Jco4GE4xFDnjXF4LVA9tszPC4vGByBA5K6NQXKliNwmbYRTxnnzwNuwqD1fxmP2ZHyIgY9jiPUEIuUJy2OU5xmZhE5S7ED4WheE'
        b'4W6I8WF1teF+pquVXIflRY3SkONzx81iQLwbr3ydB7krAsd2HDfzAGsjPsuzBRfIezxdQLp2c654H+bf5Ylk0RYipjGh42OxNXm0lalyhPXQI5eawYj2s/D+PH4IU4LO'
        b'++gAmFTjbDpIHjLw6OY2XRWRq9G4j00sLT6aQNMUuDnfmKc4lMq0eAIWXH+Nvb2aWcFbVgSaz1qynnOtanwSzCkRoymwOik6N5GGxXwdHMZXN7OEB2mgKRma8CCH7dgg'
        b'rUvDN2hWgVSF87QCgEwrj+CbbIvlpWIIpy8icplSEXvWTeA59fHj6Gkcvlkwdk1TaHxMWgBlaH5gTqybvNQMwhiW0zteKNdFMGY6bwI7G52cuH8dBJ4Ht5Bz65AmXwrL'
        b'BlZtJ3zQzpqTR6pofuZdUMbyM7hmGQMIcoUcoZ1uXNJAOerGwMQVib0xxOqGuAE3LeaT/Tzg7QOW1NlMk040qYO7cBdbjFvzyeMJcTs+QlrHxoU8ysVNkhJYB4843l4j'
        b'vfYsGYSPTeLZIFJPetgQFeG2NJYOIl34Dk8IAdllw7AziNTKrWEOHKV5pwfAwlfi48wMJwjBGt6EfJfH2ECqcGMYOQukZL4Hgzcb0rXy1Ri9Rj2uSrbNEESpV0jNQajj'
        b'a7uD1NqOtle9fBR2uiVZMCJJKNxFgmvIzeXMp9nGbB8XC8ThqgA+BXhKA/eJxY4arrgBmMuEBojIfmZHD19UVWJpHLnGPLc6CY1HmF3WY5bfXBF5SA6KdeG0px+TTq/X'
        b'Y8XxGJ6N74GLkwBcNOLLSinra8myIrm1iA7CTQhDEAz4WXKPk69b5aRBTq4LUOJ0thTP4ksOPMy4SNpEUCJCcwFi7wDEakI4+J7OKpHLhGgraWLjdokcwLWsJCGd3JTr'
        b'AK/7jZB1vAjaSDNFa5dsoRm+gkCe4cslN3jtlbh5k1wLq/R8OJsdp3eBM6QTZzU5XwDhIcW/c3aIPKRQ0x7M1lF68U6a0MF6Y3IP90DLceMc2h9Yz3KCYtyfhqtXo3c3'
        b'mpEz+PIepZhN/p35sGSqE5eTGhGaig+LyCPwBeuMeeFk0jI/gVQlmiHhJgE5HxACvX2FJZTtQgoTSF0IqZ2upBtoluC1L9mKnMzxQ441zVtJ/fTkoDgxsseN4kUCGId+'
        b'fG1p9tiNYbq3wzaeauDQbGbaPD2O9AK2RybUI7ZPJtLLc2Vsh0wsRJVmE3bIJGyHTPzaDpnktV0w8R6JcYfsjWWjO2SblcKfjAgRslCMecXSzWCtIrOQ7QIrcos0itLM'
        b'AnWOuqQ8eNyF44R4vgcdkF9UWFLE9pMDTDvQCjVoK81UF2RmFagCmcJlKs1WYwVaet84VVmZhfmK7KIcFduRplqZPq1uq2mnOzM7u0hXWKIo1G3NUmkUmRrjJaocRaZ2'
        b'nK4yVUFBsMW4U3OKMzWZWxVqqGaOIi2Pb3bTXfCsUS3Bb7ohS509hzZzs7pUVRjI76IGxsTHjrNAXfhai+grGzpGtb2ENkGVmZ2nKIKLNG+siLVNUz62shKTmdCV/3o9'
        b'JXTf36gtWJGk05bQNtJ+X5USFBE2c6YiOnFFXLQi/A1KclRvtE2rKs5khgXQbwEKFUwNXWaJij1GkJGRptGpMjLG2fu6bqP9vMfZ1DK2RbFKXbi5QKVYotMUKVZklm9V'
        b'FZZoFdEaVeYEWzSqEp2mUDtntEZFUeHoJA2Es0szC7TsNO3kMrV2QmPG7QpL0Ou7wnbJSzlEdZPHZVqsz94mQcbdygdqtuP7bJMrgijVNnZzxqR5SQ5IZwsnA3ZtxdVo'
        b'GjiMtWgtvprHrpy+3gIBpIYWeGRYblqv5hvGhak2aBLEC3mRGYn5PmaI54j0myO00aRGLkQ8RaTCrUobDrsnVuBebcTc0SJyG/eym5IADHu1u3BPmQjxbcmVexmIRpEW'
        b'fFsLvrSV7mCzPUklvs+dNuUONGnY6GsFOMV2Jcn1cM6r7uDjsXII9do0tM10W1KN+Z4VUKVb5KIcCHJvMa0Mwuvj0ca0ggCfK5Q7rd9Gz/dSDt2OqxmtckmzBMB+EA0x'
        b'OdvJxH1u7IY9uCqK9OeEac0QC30ayakiVrDKlxzUxs+he5x8f5PcUHKrj2E9OLZ+3E4u62g9dItTw7e4yHULfEZO2qbQXU6+xWkL0TftumiIzhrk+H4S66BbNL9yO8q4'
        b'B0eaImi8hN9jbT0FQWwcruFssM86VLtWUmaOWE6wnnQmMl+GO5ZEaoMnlwm5cVUJ4cb9Ild8QaUt3jpaADT6Mk8k3CJtNADClatHa8F3Tds6p8gFXKfF3eWjNeEOJbtv'
        b'KTmBO7TgwQ7T7CTPTJKLpEIpZM2aG0H02ij/V2XgDTt4hX3QsGPaVFxHd7j5/jZ+hPezifdTf3NkCcHdiCIj8Sd7rBBrVO76ogjz8lAx3elEWXgf7lf/yCNFqJ0MQ5Ci'
        b'661d+TCZhNouSN9VujHv6wdsHUQPBEXvy0ND23/j551a+aTZP+bX+udDdvkXA8vjWxvm6L6Iu+649u5vf/HdM7/5xn8daHFa8ou+HdIy2d1Vh67V7f1sqWGvRd1PO9b8'
        b'3XXX6rpvrTm0wzNs7y8WFVTOvtpy1ONLl7XfO6BzmvTL/+wrKH+0+yff+oHuP0e6y4astvdkCKxuHb6dJcg/pDjUvuKXT30WX7mscDhl8+BX6fExf0vIS5sS2XJ4fhyx'
        b'+D+fr9Y1fWbzyw1LZ9Xe+zj60/ilZe46l9h7DYkdXzRu+7E0/rM/Bab9PMt1+60zq78X9cHJSUuWbZD/YU38j9Za38qSn/p03g/PVGwMz077deDXGr4d/9ugps2Jf/nD'
        b'xXtbS3P6Ui/Lv3f85W9/fvpvyMk1p2FxntL8Bevzw+SqYnqQf1yQEOE7+LYZPikMWo2PvKD7kW7xpGF6cHxggDKY1AcqyCNSCfNFId60QPiCUozF5D18ISElCFemMAoi'
        b'L12XKqSc4+ILOkd838miTxEFBAULkA5fNcMHhBFx5i+UPDbZR67BFObP8JTxZ3hKgwJIVYjQRYCC8UMJuUGasl7QfeXgeHKSVCcFxpM6uouPT5tFCq0hrtz/wptGRvG7'
        b'E/j9NL2UuBzXrKVUyYkcFJE7EFK9p5QPC/2VGro6/q2Dlj53o1DsM72+dJqXqynaoSpU5PJH1YKpL14wbME8QzoVdoz5LqQq1sPx5T40skKCHF1HkMDKc8hlUoNuyMHl'
        b'+JzGOUfmHZ2nXzxkYz+C5FZ+Q85ux9WN6iP5R/MbREMOniPI3M67fdqlkI6Q3mkDU2YNTpnFTo0IxU4+Qx4+zzyCnnoEdeYMeEQMekT0am+X95W/b//+qoFZ8YOz4p96'
        b'xBs84oem+rfPGBGhScsFL597+Ax6zAAjnHxeHYYmT2vRtehGRPD95cuXz92mtLi1R3SaD7iFDrqFwiV23kMeipYZQy5eVPAb8vJu926Pbp/amtewbMjGeQTZQZvcvc8E'
        b'nQw6EdIa0mBO27awcWF75ICD/6CDPzQNVLC7/VYI4OhqOj6nVY9I2Akz5Ox+PL0xvT1twClg0CmANRTuMvjONLjQN7MTGuI667mT2/grxezK9nyDSxi8Ry8Mf+7meWby'
        b'ycmdLgNuYYNuYWPa4uDChJZlnQsMk2bDm51+OWTnxIaoZVqLpl3Qomn17ww2uEfBmw+as3tLeEt0S/jRPD1teovaYOMHb17o6NmyedDR95lj4FPHwM60AcfwQcdw/ZIh'
        b'h7HDbuMG5lpFDrl4P3MJfOpCr3MJH3QJN9iGP3d0bbFrsW+xPxrXUjbg6Nvp2JnZK+jM7nYDVQ2CIRd/g4t/p92Ay/RBl+mdJU9dIgy2EVqKgk+kQdFR6EmURYyZCEsE'
        b'cNQAJiOl5bCYzsNhETDAYXMjnxoWUwI0bJ6ertEVpqcPy9PTswtUmYW6Yjjzj5cDwC/KgJdpSWio+9BQTB877Y/RS4/A4SV9wdRXiwUCX+iD//bhubWLXl2ZX5O/Tz4i'
        b'lAgch+T2+lmVs2tmPxfb7EvYn3QwaV/SkNRmSOqgl78ckSCJ7fiz+1L4Py0NZ07LItEN62ihCNwfe+aiYxFpT4DgilQnk7qUeAmyLs5xF0VtIAf4QxtteF9QQmIyD6UE'
        b'SA5eqn2dEFDoJM/2khvg3i6PxmBa0hqSQM5mm56/pS+xianto2GUkIdRLIhCEEKZ5YpZ6CSC0GlC2LNbzEIn0Wuhk/i18Ei0R2wMnd5YNvbp0J8MCSaGTuzp2TGxk6Zo'
        b'qyLTFO2Mj2vGxzATYpS0fxBKaVTbdGoNJ9DFKg2EU1s50zc90jue66aYKDAYErASalRvVS3RaIo0AUxZJpTkvDlCovZSc3mUNLERbwwPjI3id0xs4ZuqoDHV0oLMzQo1'
        b'j+yyizQaoFFFhTkQCrDQSptXpCvIoaECZ/0sxjPGdW8OCpaoaZNfxSAQb2YqwoNKdMUQWxgjDdZrECL50ysCaUXKfzNEkCTr5oHkQe5r3vQMbWViwPJA3JXGH6elJ1IS'
        b'45MElHrXh+BK+WzSXJCmdm/9OdKmUtcsdp1x7dQ3w9vONt1seXzwiMB6petxQfmVn0xJqmnrljd8btfedLdJeUjtFrFiRkRi4OHK/WePnT12vemC/sLhs4fDapUtZw97'
        b't+yPsEI/fmEdU3FfKXxB00ukEajmGXkArDlSSWqSdEANWsBaoAdoMu4Xk2uRuP7FZLpAe/CdaQnBy5PwzbjAeFxLKQD1/+74hrgwd63S7J+gmtmok2d4Niznj5Jzdz5W'
        b'YP58BeL+fKk5cqQuzWqx4FPnKYapMQPOsYPOsQbb2CG3qc/cQp66hfRK7/i9HzngFjfoFle5XL+4YRpz9AKrKUMuHi1pDTsMtt7gifQJv6dDxSHbfFhqmr3D5sZ5qKGU'
        b'X0P5lsZjvOnmHJCp9RyLKR0aZ/MzelmZEYzB7HwzgWAaBdV/cvjKIJdS9xZZMLpqPU+km08H9vgG5WuJsMukGR/EffihE67B7YGijQmRuG4bjOxF/NACZZFGK9IGAcVt'
        b'ngy+hw/gdnmpNQRmNG5sVJAruBJfYIVrQPcFeek2WqanDy+0kVYIgh6wuGkhvkYea8ktm3Axwo/mCEmjwBlXalkYFLKKXNKGa4RIUITAniv49vxy40MbjuSBvLTUDDQe'
        b'QnHkAjk5KwGcBys7Qo6GjUI/+IG+kCQv7lZOlJOecfm3DFJnK3LKw2dYdWGyTdPBpwiQENcJSGVCLLmxYpzPkJqWrh69Sr2Bz5DoTck3GfgOi1zpqO+YmHb7n/Ed//W2'
        b'tBsDvfFJt7ciJ0VZevk/T169JadEb/6/nlLKLmBmaVUlryeRJhhI+6UoO1sHTqIw+3VDTWmkJSuiFbHAxjTUiSwGZ5ldUqQpD1QU67IK1No8UJRVzq40OrVYFbQns+A1'
        b'fTGAIcFjbMukg6JjP7gJWBWbFhAIH4sX04/YlJVh8AnmBcSEx7CC2NiAwNc0jmlTZoG26I3JMNpI1s/FPAUGWnOoPysvntCB9PUvMYVRjUXFrxME+vrXSMK4wftKc3Cj'
        b'zG6Mg7VJXsqRrh/fF73FxeIeh7d4Wepi1+MOlvP4bKcbzdWFrgjWzhMWWvAM3HmocBp8Pg8q3/V4chJPhGROA+CsJucp1K9Fa0PxNcZN1+MHgJbVWI8BRYTktMxBIJuS'
        b'xtR4uljTRJ6rYkFmYKnZVqQU8lTeOayfFIEf45sUpFAYbsed/BntY1mkKQJ3k1PQ5nAUjg/OKqD+5yNzW6RAKGpRWLHlrpWghSWh9gNLPhGB95PjXE1GAdfe6QrY2o87'
        b'k+HWFWgFacf3mTU6Fcs1SkeEWst7hatQmrqkzEGg/QSKGhouHkq9bn0g1PbhJqUkMiz5g9Ub/+rl+8eP41yrUs031lj/onDD3Osvm95ZtOjp13yTtGXXfvvw0YIOv9Bj'
        b'cVN0lySfdX2yR/cDz7WnDqye/fFHXrFrZBX2n305JStDNfCNb0z9lVvVn91LM+uH9snEOSPbdPvOffu5wjYq4zup/xGV7nntR6ffN9vktPUHf3/21zlqre3MF59O+kuh'
        b'4bvvRp1u+HZ+Re534p70ZSt+8EeX4Pxff39bXrvhC2m8zZqO+Ucrv/j6e5v6zL+fcWHt3R8dfGH1l9kJXzR5XDjybOHwiCHy0MsvzWaUzcbPP1RKWRIGPybV+IgNOW1M'
        b'xLAkzApy+cUUWngrbNkoD8rBNxgVekWD8CXzF/QZkfAg0kg9Cq5MoQmZELgkiN6RQE7MN0dhpN0sHjxozQsa04SQO/iSPIHUKBM9R9U54QqxVOz7go3fPcuQhJQg8E7x'
        b'pL1UEK0hzSwRgw/n4V7S4UnTOiEp1NI9wgDw23UvqHvVkoNzwU9fG03V0DRNuRNLJcGMat2bQGoTWCoJDDsbgZBNqGizq7VS9u9lZWgUN5qU4ZxNxsNP8C07Xn1lfC1R'
        b'wPnaLuBrLmMCcXun48pG5ZHpR6frYxktk1n5QFRO0wJxgk/dfQ1+Swfclw26LzM4LhsRiuy8h7z8n3lFPfWKuuMw4DV/0Gt+w7KGZS8/5beMObBMQsuMERF8p/kUB8+G'
        b'OS3Z7REDDn6DDn4jSGjnM+Qx5czck3PbtZfKO8rP7jy/kydwXqVjnjt4PXOY9tRhWvuqAQfloINybAbBXq9tiKjcXrO9Jbxqj35P+9T2zPO+nbEdQe1Bd0SPLe9Zvr96'
        b'ICphMCqhPch0R0NYTWmLm8FmCrzbszu9z+f2ygy+s+FtvMKZpz0iWra127VoW6Payy7t7th9du/5vU89Zho8ZppyVg2RWvqkwFWnaDF6IraIthc9sRPAkZNXOWeqdEYP'
        b'i8A7vomzvjXP9lpegT5KN2Y0f0MvrH7FZNeaCwSTKVf9bxy+0oRCqywc9VlHI5FSwPZd8TV8J9+0X4uvyfh+LWkkt8f9AHHUc2xHPCfAfoAozhWO/tBwAnP7H/ihYZ5S'
        b'+OV3xzm3ldw5viWkzWURKaNhY3dC/2/nAN7qnUVv8M5mybpFdJQukXrcP9Y7k0u4958HwdQ9435czdzZjnzSoGU7bE34Bttls9/IHr3x2UkOAX6SqiTSaUVqVhF9otB+'
        b'Cb6MD+EL+AR8UaIVtub4Fr7tpf71755IWCj9+6CQU9+MXP9dCKWvvxZKW9JQOsPN9trh399z3ffLlt7LCZkxM+zyJs9tDIw4vLtGvqb3xPc/2tcVzkLpFV52w4G2Sgl3'
        b'IJ1R6UYHgu+lGmPpVw5kHdn/gsYyqeSY1uR/SjZTD7SLcHdB9nmrXm0DsD0Aa/JAId6UT46zEHwutL6Z+ZNX3oQcWkkdCr5N7jAlC/B9cmnMXkEROSOnmwXAW24ohWPA'
        b'gMK2CdfNN6tKGKqbvjBMz0Ic0/dI3xqDj0uvT8xHC6xmf+qsMHjPGnCOGnSOMthGDTl4PnPweerg054z4DB90GG6wXK6hvYdBzaJhpKpN4bgNMOS8SoAn0NnhclYV1jv'
        b'2nwGWWDtVqlAQMP/Nx++Kkj6PWVTR2UBqMs6SvRPAUesR//rgNM1br2uKi5Ql2hHUYXvvQN0KOjZXE3mZraXPgFhTCiVqYh8Y3Zs3MX+sSmrk9NWrg1UxMYtiU1YtTop'
        b'UAG1JKTHpixeEqiIjmXl6cmrk2KWrFT+u2DC2OtumM+WKDSM/gg7020d0kXByXJ8bvZUcoP+Bn46LA3AlNS4V/kA0qjEly3wiXL4H09/qIrbzCywPpGcZD+PIkfCdfzO'
        b'uXJ+L0AI8yhepFOMO3CPvXrf9lqhNg8uNv/shwAcABvlAtHMXkv9u6R847fbvq20VNb0JDYWX1932P1w8sXwD6b8zT734CPHi6qaRW01oXscsv1WWYlingl9C27pnL4I'
        b'P/fLLlV3ZuDSGcfdPv3E/QPJty3XoK5vvecWFYFGzjrnYJ1SzGieTQi5bwSKbHyMcVXcix8zmkfOTJucbTYBCigOCPPZluD2XFI1Sg93W1KCWIY7OLdsxXW6BMpb8SNS'
        b'FeRvhmSuQnw2ASnFbyQNdD6PLrxhC4jJtcak3ZjvDC9KjXixSYYcXcfgwlu2cxg2LBxwXjTovMhgu+ifbOyEweXtXgPOoYPOoQbbUDh7fF7jvCMLji4wWHr/tzAklmLI'
        b'mDb4j4ORJNn/Boxo5lKbBTpqP+meDaFlB+njpAa+14fgKo7i7nvFeeY5b8aZXRRnxCZiQ/+ugnGj438Ha+gzYhsnbnSM5TdsR6AwcytLi7yB1tCkCH2ip1gFJ4D+jCca'
        b'8RxxCjJLSlQaRXYmcJTxShnbyczheymvZXfG6RrN9PyzRA9P7Py/RLekfLcBd5MbWWPZ1uYV/xrXAiBhEHsrnqdCQjdlqOa4eCGW3tiNG8hpLblQPvqUE1TQxJ5c34S7'
        b'kxPwIdLIWdjbKVgU4RmI30RRDEe2ob5SrWd8CFJHx9uKtMVQ8vefz+IbHJcXDE3kZYmWbd9uy+tQJv4oo/RInt/3hdM+le67OtXVv2+f7NQ3VYseuH/3iyxxV/YHF4MP'
        b'uf1gcfv92Udy1vbeOSUhn3Y3FnveXPQ4JOPruQDD9z6e/X30uxuTcmcHKs1eKGiXPZycMX7/A8BUvt3I2hZ5vWC/feknPak07A+QGgP/FLaVSeoAgpMkaFay2R6QKl6w'
        b'7EtHTBYAd3zIaI4hwpGhdp501nSi146neMDvtpP+F/Sv55A6BemS+5OHr+O69TuMY+Z74wcJr1VvIwNrG8WkDdeJAADfGv9RAByzA2PJ+BPMdLqOdoyTGJ5fMOL5Uou3'
        b'8j8WJc8dsJk8aDO5PfypjY/Bxodtuoc/dQnvnTvgsnDQZaHBduFzL+Uzr5CnXiEDXmGDXmEN8iGXKc9cgp660McqXCIGXWhUbjf/U/dpBp+5A+7zBt3nGRznDXn4tMxp'
        b'zx/wCB/0CO8NG/SY0SBl2oOfugR3bh9wiRp0obRyDPybD8splqcXaSgz/MeRMd/XGbMnpUmiLmFcR8yhTkFncgrbwCm4UQfwTw5f6bbOMVkg6raeI1KKkpOXKgVLlcLk'
        b'pWrH6nlC7VkYJjtv19rGX7zrkGr79c8KLX4UuUP29cOSnb8dup4t8rAI2GE1pcoiNdTXuSbXoffnCudBve+euL/FFR2z7bPrONX/ePdvv/PJ3YjZRYNuaQd+2B6UZzPn'
        b'g68Vn52SYxdgM/tnjbayR002571if/nxZ7PdDv3qpEVla2LsnP4TJ37wZaLr5lUXNJlPz1z4InJ7uF/M57qZO5Ny9s+6eWu7T9Dcb23r25R+9huhG22qHn3QcP7z7Qfb'
        b'Hur+ELNct+ZnYSplzw5VYVt07CnXhnviAoeVQ4K5k4o7ij957vKpcIl/XZx/tHLtYU2fsDnHaUPOjC0frhs8og093lrx58+Fg03y6/oNNT45omON3+pt3bC/+fOAbt9n'
        b'GVsXd3xvTs+PdxQoZmU53HVb/2HP5ahbmXN/pPf8PPlXU8qybe6+W/2bWIe7k80/fC9qsdcHdr/rPPZZTfbn21r1cdePfj++9aePJD2fq1u9v/fTSeVeWz+XbJj28UD0'
        b'pqdzHnd/Z+eS6tKfBpQnfWF2J/newJIfL5pV7jD/86BPkuf+4afWfyrbVv+r2IX/35PdvxOYfRg9b9rD7Yu/vHEzvXrBDwMWPFn1O7fDH/5C2hAy0mi55Ru1f2/r0k1e'
        b'rs623yDNdp26/dCz7e/d3j6rsDI+c/2Hzt+5t/D7Ka1FU/rz7T2Dft1nu+ejkL98bW/AlshDT4pefJT6s0SLM08210T4eae0vfyPI+se/OmjTdotnl1VJ3MHP/ryY7e+'
        b'P59fumfZutjmB8++7n38j9Pjl/70RVLOA7tV1WlXtqz61qDFD34yMzuy/T/v//C3f73YvcPnI5tt32378Nt1UVea76pq/utcVfmt2SOpC5et+eiPxG/XBy41P7vycetf'
        b'j/3sv9av/s9N34z/5moXvz+fflzRq+vShHf9KfF7I1MzPpobG+31sPbLyr9+2Tv/3N//fHvh5t77tS//UO8VaNsTI/ur4P29QSsbbQFm6WLzDlYBrxGgLeS0IAqQzhbC'
        b'YbatvB+fwvcYk/UlD8aDXiq+/oKm4IH2HsPnxoB0Aj42LrZOAOSljirtnYWkGkhvbZAZMiMHCzcJp+7FF9kzdDtwGz44fXkQ0ccnJkuQfMFufF0IiHl36Qv6Jz/AhdXh'
        b'xwnUcQaxP2oFl5ST4/iakHStVSon/XtPtUnfdvi3n417I27ROH+UGiyir33jXhzepenpBUWZOenpO0a/MVi/ZG58ZohhuwBZOY2IzWUuHMvDK8tqylq8q3bpd7VoW7Tt'
        b'4e2Z52ec2NG6ozP15N6Wvb3T4J/mjvcN3Z3UG9uvB98Ifn/x+4s/tH8S97W4p+GJhvDET10p289snXFC1iprXz7gGtzrMuAaZZiXPOCSbFiZZlj9zuDKd5+6vGtweZdS'
        b'evsjhUcLDbbT6JNkawQjFsjesSH6qJM+Rh/zcsRcIIsXDNlPbgi6YGkIWjqgWDaoWDZgHzdoH2ewjIMWjFiYuVuMINNBbz3iiOzdhuxch+w8RszFbnAaDnqrEeskgZPF'
        b'kKWtwd5nRES/P7e0hXUpoV9HzJCVHQjmTJByQcYECy7ImWAJgsHef8SKSdZMmjZiwyRbY5kdk+z5bQ5McGRFQSNOTHJmks+IC5Nc+YVuTHDnggcTJhmv82SSl1GazCQF'
        b'v9CbCVOMdkxlEmLHafwCHyb4sguUI35M8jdao2RSgPHm6UwKNEpBTAo23hfCpFBjWRiTwnkFEUyI5MIMJsw0XjeLSVFGu2czaQ6/cC4T5nFhPhMWGK1ayKRFAqOSaAGT'
        b'YwRGNbFcXmySlwjGNJoflwqMZi/jZXEmOZ7Ly033JnA5UcDtSOJislFM4eIKo5jKxZVGcRUX04ziai6+YxTf5eIao7iWi+uM4noubjDZtZHLm4zF6VzMMJmZyeUsk5zN'
        b'5RzT7Sou55rKN7/eJXm8LGxEzcu2GKvK52KBqbe3crnQWFzExWKjuI2LGqOo5WKJyQ4dl0uNxWVc3G4Uy7m4w2TlTi7vMhbv5uIegXEa7OXyIqHx8mghnwdCo6WxXF5s'
        b'Kl/C5aVC09hzOc4kxwvHdMdyIXKYMmTvM2SvZEdv09tnZK1wYufpZSMbhMhj2pmQkyED7tMH3acDoshC2KFyuT62wWnI1eeZ6/SnrtMHXIMGXYMoTw5khyPiBkFD2JCr'
        b'5xmrk1btmZ12A67TB12nN0gaJEOOwb1OA44z9UuGPCefWXdyXadkwDN40DNYH9+QXZmsTwZIsrAdktnqXRqyW7Sdsb05BtncAdncQdncEeF8WeQI+jcO/0eELObBnfTT'
        b'tsZ5REwLoK+NNbRMbdf2ig2yGQOyGYOyGSNCO5nrCHrLgeqYCVeN6qIFvsjF7fiWxi0G77QB59WDzqv18ucyG27+qvapnYt7nXp1d955f8mHPobpKwyy1AFZ6qAsdUTo'
        b'S7X+Gwda60oB3DpaPS1ZIXjVWQaZ+4DMfVDmPiK0lME4vH6gt3rABaMqaMGkN2qwlk0ZQa8fXtNACxSj3bnKIPMekHkPyrxHhPay2SPoHx2ojilw6aiucaXsUeDK6IUx'
        b'9gjbu8cEGjcAbYeF6en/6q7fv0IobF8FQuNJhGY1pU6j/GEq4w+maChWIBDY0njnKz98pRuH7bKZ6JZ1tFikDsnuQdrvwKnP8SFdQ4L8wCLHQ799kFjrLIlZUr8kemFn'
        b'c0JmZ9Id/yfO9+QPvrtg+J7mZ2cKFi0/+sX770+K+sX9X3x35/qRGMffiU6q70Rbu6VZ6ps+/M3G9ct+X/YfgdnN7eEn/7Tyk4svU66XdkSujD2viH3wzuylRztOruge'
        b'/vHPr01Rbb6Xk7K320/0rT9+ePpA8ZdH+z/7qd2Q86pG/4qvvSzZl/Oj2XXF6R8vRFM/mDmw5UOp9zHlvCVSZWydhWfJtjqhi+tzC5/C4oq/fCtxbsizkcYzT+7vEbi7'
        b'hj1plCqt2MYPvhrpSqptcQepTEkh9aQmwRzJcZ+QdCZksOyCjNyW0c2y6/jANnoNfa7AjjwQ4bOk0ZL9woPcAqZ9A1fjelJPU+l1KfQX6PXmyNpe5IV7yF22gYUfWW5N'
        b'iE8KSDJHZuKgfKGUnMWHWMkM0kUeT18uQYIEhJvJKdJCrux5QX+Mji8V7R63CXiVdPFfkoQkAJOvg8rqRWgZvm6O61eT68ya9R5+E5/qMUMui8WkCd8PIO/hO3zXrYHc'
        b'TWQpkbGahKTKA58S44v4QBDPel8l3dCCavqgRrU5EgcJ5pAe3LM3nbF/UrMcTitBCanHt0knzY0JkE2qaDXI117QaR+G294xXRKI63T4bgjfbRAgBbkpQfbkMOtl3GYH'
        b'fWCDz6QE0hQ8HwbySEhu4wOLmSZ8OprcJv2kBgKNkIBtxkAGX8Dd7joxPkw68FXllLcHE19JCPEVHrRTWDTyWhAy4TUak6gL1SU8JuHfWEyiFow+cOCOJA77kum/ISvH'
        b'Z1ZeT6282rYPWPkPWvnvWzoktqhIPJBosPO+EDUgDhwUBxrEgUNiq33x9B94TXcvg9h5RGghWScYkroZTG8g8l7+zzwjnnpGDHjOGPScYZC6D0mt6+VV8h84+g5I/Qal'
        b'fgap35DU/pnU46nUoyV6QOo1KPUySL2GbNye2fg+tfEdsPEftKHbmjLQbWlfn1yVbPBYM2C5dtByrcFy7cuXf7BDli4jSCgJfXUYcnLTWxhrMjgGD0hDBqUhBtN7RAKX'
        b'0DDGOV8sAcj/Hz6ukyFLR0BF9mMWiThmJsIzvWPdRcRNAEfuWyYPiwpUhcNi+jThsITt+g2LC9TakmFxjjobjkXFUCzSlmiGJVnlJSrtsDirqKhgWKQuLBmW5IKfgA9N'
        b'ZuFmuFtdWKwrGRZl52mGRUWanGGzXHVBiQqErZnFw6Id6uJhSaY2W60eFuWptsMloN5CrVUXaksyC7NVw2YsS5/NHtBWFZdoh+22FuXMnpXOn1XJUW9WlwzLtXnq3JJ0'
        b'Fc2eD1vpCrPzMtWFqpx01fbsYVl6ulZVQn9wM2ymK9RpVTmvfKaW5h4y/tFLoeAeMMd0oH+wWRskMAXPb3nBDLYTCPJE1I/9v3z8ylwwpTBPLGTRCvREYR0dLPpSavpV'
        b'37Bterrxu5FffOmeO/6P0ysKi0oUtEyVk6yU0l9T5RRlw3jCl8yCAiBBOUZUoblaOG8BU0dToi1Tl+QNmxUUZWcWaIctx+6waN5DxlQxTxrTIf5SOo//8fsFGvrgE91k'
        b'0+6Gw4gICM6IUCwQA92HgyWSW+0zHzFbCt0xgsYcV1ogmZ0ROJZzMIHFL5hhCFzwvu/7vk/8v+ZvCFwO7yGp7ZCFsz7Q4BIxYBE5aBFpEEcOIVsDsm1wHUDug8jdYHoz'
        b'8/5/1CKuvg=='
    ))))
