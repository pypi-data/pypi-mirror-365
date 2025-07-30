
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
        b'eJzNfAdYXNeV/5vKwFDUexl1hiZAxeoWQsggqqolWRIMwyBGos6bQagjgTR0EAhEUUMdBKIj1O1z8sVWmmM72XjJJl7HdrKJnY2T/+7G62y8/3Pvm0GAcOz9//f7duGb'
        b'wrv3nnvuuaf8zrnv8ZEw6EdBr7X0ElfRW5KwS9gn7JIlyZLk+cIuuUlxRZmkaJRZ5iYpTao84YBaDHhNblInqfJkp2QmF5M8TyYTktRbBNcUvcuXyW4R60JidGkZSbZU'
        b'ky4jWWdNMeniDllTMtJ1G8zpVpMxRZdpMB4w7DMFuLltTTGLzr5JpmRzuknUJdvSjVZzRrqos2bojCkm4wGdIT1JZ7SYDFaTjlEXA9yM0xy8z6TXdHppGf9J9GYX7DK7'
        b'3K6wK+0qu9ruYtfYXe1udq3d3e5h97R72UfZR9vH2Mfax9nH2yfYJ9on2Sfbp9in2qclT+dr1hybXiDkCcdmHFYfnZ4nbBGOzsgTZMLx6cdn7CDp0Drz9YoYo1N4cnp5'
        b'0GssY0DJBbhF0LvFpGro+w8NcoFdyx1rc//RPrNgm0d/QK87nMViLDw6PjZqExZgaaweSyO2xfmrhQVhSnxKbWdsS6mnBZ/AFfqrDMt9sTAWy8KjsWw7jSheuCncLxJL'
        b'sCQiCm5AGRZFqIRsKHfdjVc9+cw+qS6CuyCM+rFnlvuUY36CbQ9d3BWJtdjl6rEpnIiWRGwLh1ZvLPDbGI1nt2iwMHwbkR46l3d4FJbFRMVu86aGgoXE5qbwjdu8/cMj'
        b'/GTQjE8nKwUrFI5fegTKjbJB6uTplMiGb9iSZE+H0GUFchK6nIQu40KXc6HLjstHErorvaJfEHq9JHStwkUQXposCLqE1MvuuwV+MXCeQvgHmRd9S4haljRTuqhb6iqM'
        b'O0R7kpAQ9U58lnTRPF0lKPdOJJNI8AtRTRWahFQ3unx70yTlx5pPqfOHC/4k7w0KVGqEVMbHX7LrZO0ugi5wcuT8f7CUzm+XLn9H9yevc14y78+FP2i+2rFg43eEfsG2'
        b'kBrwATyFJ7QBtIne3li0MNwfi6BpqzdtQ7lfQIR//LqN0TIh3ct1Ndjhhm0iU5k8KMazojvk4x0SM9YKUIPl02zjGL0uaIF80TJ9vor+KBag4OBB23jWcGMVVokW3UES'
        b'B5YKUITVeNc2gVqmLYY2EXvhPF2mtgoBSvDREmlQtU0nQtkMvEVixUYBLuKtMbxlFNZOopYNWtJ4vCrAJTgLRRIHJaMixCw8j5WMg3KayT+Bs409k/GOiB3QAffVjLYA'
        b'Fcuwhw/yX5Yh2ki/T7IxZwUotkGJRO3+dmLbY9sKNuKyAHUH4a5tEjUYoBSaROzCk5DHmDtP1JCUny9p3FFoFWkZV7GB0bggQD10HuNN8Bh7FohaklMbY/0KkYS7C/hc'
        b'UAG3BPHgwnTSWawRoAyKXDnni6ASGkQvuIH1gjSmFq5jsSSiIqyfhl0exnGMi1YBLr+EbRLrNdAOuVrLCgNb1B0atCHcuUdX8SkUux99WSbINALcjc+UeMuDx3BOxM6t'
        b'SravlQKUQ91hPs2uA3AXu2zYelAhCfzcAey1jaGWgHE6LbbPTmCTtNFGJPlzWngjDXPFg3gaC+QSrSJ3aJI24tFUUhG8h/lLGc91Au3dWaji8yyGnr2iF17Gi46NrccC'
        b'K2+BNs187NJATyRruS5AA+RJupCG1w+ylrw1jIdbxMMhPClp6mM5XMAuK3ZjiUqaqnwenpIEV581G7vcj8AjtTTqIhR7SDNdjiK2u9yD8CkTw20iuMBom8xauvEMaX0X'
        b'duBNfMCYv0a6vw3v83GZWcfIn9F+PmTD7grQqMBCiWL7gjRqytzrENJVEuZNzuEM0sYKaloAZ5hg2wW4BvexiY9aA9dnksyh0exQvrN4YzTfQUVOMG05nj4sk8ZcVcJt'
        b'LvWXoHkvsdcFJVDJ2ppJTLM9pM3Nh5oo1hYhd5E05RLY93FygWERtIXQCDccjF9UB0saeVkHzVrNKDjJGnoFuBG5UBLeg3S4rsXO2e6MVg9xoMGrvGXKPuzTZtNuqqRJ'
        b'6vAUtktq14u3D2qxN2wlE1wHzbJyAh/y2lZsoOsTsYWts4tmXYR3eEsYtGEnNS2JVUnTNE6Ghw5iwfNFK3RgI+OsQIAzu+ZJLLdBJ5zUivuylJKsa1cJEsv3l0Gh1i0T'
        b'z7JZ7gtw0xs6bVNZS95sOA/FS7ECeoD0RIFXfVfKYrEFr9imsPABBdgDxdl4jmy+iPxxileoDE5uhGs2FuyDjmc6GoOdFFyhNHmUfCKUHNAruJFg+cvRWEw7nIGNkCdk'
        b'GKNto+nyssNpkcRmIg2+ICTugys2FkN24l24F0lcJkHFfnorh1LbAi50PyzEKiwII+u9sxSaVIZoKMXr+0Ph2q5oYbGogmq8s8KmZ31PHcIe1pd1vEu+9hz/uhjuYLVS'
        b'mIa107FU6ZqDdbz3MtKXVqk39MJt1j0c7j7v3XsUHisVcC7J5s0dqec0J+nWQaRbeOeZh7BSqYZL5IV8WOcGaCUjrgqHFuJ4oHcwm4V6b4MmfwX2YRve4t1pR1sPDfDN'
        b'FwiP9mt1WAy3t48VNuqmQJ2LFh9hrS2AxUwo2/XiKklrStlHM5vC30Kq/USVBfe1tkCuB2HTGDsdtFbOUqkiUZoFrmE9SROKSZjh2KcmAZZCs20uDyq+hIQGFjGZwA6X'
        b'kHKzMBW7FDTDtb22Fazj6QA4M0iSpcOFdDua0WiJpov56sRoIYv8GtzfCj02fzY89yUlm+Yum6YEO6WBCqikja+GM8mkXvVCEF5WQdmknXzroCQJrw/ZDWnn+NqnLYUu'
        b'qFKQuK4s4VsHeV7zR9KKJmmfqz3QrnTB/F1cuNkucO55Z8dKcuHUMPVYfEQFdeIoWxANcQmFy84hA5sdCNVLqWuptH42JBjLVYQly/A8X4NiLZ4Zqn1OYXG2dBTMW5Ua'
        b'A5byOfDWNJLH8EloZIvEI1dDfyiiIPlUJU6E+xzoJFGIqXeOamajyJ8eYkKFMzq4SroVjY8Ju3a5BEMV1PPdWIrXyaKcM3Fl3IudpCmYt8t7qcSdCJc1tFO39kjK9YBA'
        b'xFPnkDsvaKSDtxo4t0klgt1bMpGKjSsHdlCy6XK8z+w6VIdVXO9j8ZJLwGhPPse8l7BuQBVLh8wjiU8pBMBDAljnVPsxF4skmy2ARxT1pWHNL/gD6AlZoMCHh0XeOQMv'
        b'zhtssdJmt7KeU3eTP+9VEIqqhHt8O2TUo3mYmjSBna4OU5MsFdTSci7xtGMV3p85oOiOjk6fsBIeKBTY5r5Fkk4lPDE66be9oByZNPk10tlSbLAtpu775fOHMzMwRgmd'
        b'7tEh6wnzNkPrfEpoqjVYcQJzJQndg+pXXvA8oTqVsJiQVDlcUcFlqIYabhrWLfBo6B7chYpJg5jj5rcIG1RQaTvAt81MfrD0udqWDughv6Ig1jz2L5FtEiarXJbRmqts'
        b'fiw0+mNXJCHqJwFcd4boiNPvb4ZSl1lwPpCvwm8RNDoZM2ODw7nxvsytLYIech1T8J7kDRonkOsdttHBEu9TjT7YQbuAldR5DpPP4/lpg1xHFgnA6QKnwSlSnkkxUuSx'
        b'047cG2KfgzdXg2fBrsAHKdHcsW5lofM5Bx14S+ouZ471HunZIbjAFSYAL055USfvclbHzcR2YnVzOF/VcfKVfQ7danZ2hW7H/ATcekm7us3zubqQVp8nqx/uEgmKX+Hk'
        b'n8eRIKxXUVQ7DycdXgjvwM0hA2keaBzLNXPQsFdVRKyN4hXbT3hCY9qHGXsZ4fRHg4w9Lspl+WSyEzbNukWUBQ9RtFYaf234shaRqyMdLaZRzNkZsTptyCi50aHOo2iO'
        b'vqWj4UE2FCyRQcNat5ioDVIg6YQi5Qtx2mlmhMhP6RW0rzdt3ADmU3C89YITdrp5h5+zHcXzqkyo8pEmKMXeBS9uIXcOUzcT2rqvIOd6A/JsviyRxnzoHTEoODBJHSna'
        b'U6XnFoKK3E3coFBnf1GZOSdTaWgL3lXg3dfwLMdSweq9Qx37ZKwfugl+Li9pNZwViq/1z8PaiypFH/eZTj+1HuOWvuNY4MjCh65d5Kfy9+OVULy2S7AcoMgP9Sd4rEnH'
        b'B2Ofa1MbXhi8YtUYR+BvobAZTktgmwy1Y8jAh+Ow56hDQj9Q5YY9KmvMCj5mPaVALyh7Nt7jEGCwrjeSt7Pt5VuNlCd4sUFLEqUOpcPRw11V1hJZnMZl6Rq8zLdaTiZY'
        b'OMCaIWBAZC2qRBJCtBA8UQUlR7DcNp/1NoYMiZgO4UpwEh8vgE6lUj9X2uWHUPbaSACmVercgZewSKmBsiDJF9VSl54RlNqhQy1we6WCHFsmt7WASDz5Iq7oE4dbNFap'
        b'KKsshDp9FE859h6DDtFqgafOVAQeSAm9Qj9FtO7Fuyx5KRTATpt4gedih6HKU8TuGXBNJlU8ysiZ5PFMweq/SnQ3wEBhRbNcyneuwfX5IpQEpbHs95IAFwKzeP99ahfR'
        b'gk2LWbZjpyRvjpn3V2IeFIqW7OXOMgx2KXlyQYS6ZouWo6ucdRjXMD6AomYWZf4JLqxPmQDFiVgj5Y2NpKSNohteSZBLPFVD9RqevO7BkhkiAY0OPKeUMtQL5PsreH2E'
        b'tu82nhYp6bsLN511Hcg/xpleudkmeqbuZPTqaY1wc4+UonVTfporQpnfEme9RxkgVRNuo308NagNznoPbXShJJl8KIR7YpZin7Peo5JJjHfsCBWxYw2WOKs95CHv8aYI'
        b'8l33qC0BT7pIZQFKwGZy+SQkU4ttrsZZCMKaZH79RLxR9CDrveQsBM3YJJUYcikZaxNZyo3nnYWg1BwpF+1KSaIWzUw2yUVaqDeckxbaqofTopZw0ilnEcgU4SibYPMW'
        b'8SDWxjurJnCFBjFqVkIoXeJBwzKVtJzSHMIWbIwrnFouUmMR5DrrKbPwkVRC2OPBWpony6Qy1DmCYPmc2kZsVIheeOmgs87CigFcbKfj4LrotR1qZFKd5QIUkG5y5irx'
        b'CtlAl2bGRmcNZi3WSznr6AC6bsVSZwlmyyzOgDybcH6XNcXqLL/QTl7mxPzdttNud4/CdpkkghoKX7f5IHe4EYhd7hPHs+XcoFkImfdKhZSGtWSaXe7YvMhZtUnT8vX4'
        b'YfE4avDFk86ajUXNFRHvkve+S1N1rsNeF4lg/VFslRZ7bcl+7PLE/AwXqVpwDU9DOW9aMSuENrWMHH8uW2ynADehU8ebDhDMr8OurDVwRS7JtRzqx0oEz6W8Si2kFQ1q'
        b'adMroHUuLx5Rkt9Jbr0LOzLA7qwd4W2o4yvbPAMeY5crnjvsLB5hyWpJw85CzzZWWKqB+876UQSBVjbdqAjKjbpcfaF8oHp0AVskTi7OMbKKXZvMWT2i0FDE59q+eA+r'
        b'K+VFOSRfSRZcwaXosYL2mJoq16skA6zSTpMEXymuI9Z7EnIccq/DMj9JKdrJ+V7GLg/tIbnE+RU8tZdTU8MDpN3yOCE661SZLzvqOo3M1j1eTVdJpaBr8DSLt5jwhicr'
        b'UuGdvc761fKdUtWwCm9CHmsLc3MWsPD2Sj7R0pnQqMX2VDe11HDBBpKS6Sh4XWW1rVwocNa24mZINlgWM1qrIURTr5ZqS9fhvqtUrLmzT6fVGOc7a14HQ/iA2QI2aK1T'
        b'4LZDK6vwCeZx5R+fFK/FTh+46iyGHY+QhHYOyr21bnDW7Cw5+UOutKedBCoeaLMTsY9RayKnSpzckxxaJ17J0Waf4Pt2R4DzwfCAT5O+G05qs92gwFlam+2Ypm0f0vJ7'
        b'x2Cus7J2NMvhG92OUcP41c7C2hgsk4Z0QzteoaaEXc7K2vgAztkyQl2PtJ4U/K6z9T8SKPbdI5/BylWTdvtpPbPmMlV7IkDz+LXSJKfC92ixQw3XHQJr1MbzSWy74AY1'
        b'gD2QjehjxmU3cwmboG2e1tVLJZdmuHV8iiSVfHLmzVob2zRHNZu0W4pP3nj7Va2IJ/c6y3qHCYqyWZTLWLkPbsc4hH+J1LFJsoBC2Xpy4O1428rW/5i2GM968rOstaRJ'
        b'lwiQnqf2KihwlPag1QHvoIAXA5XQRfnJNuHVPWq8DAVKvZIbclwE3sHiKLg7eiOWKAQFPiEgTUHyrOT082gZhZFYNGZ1lFqQ75UtXDmHlxm3QYP7RmiKxLKFWOqrh2al'
        b'4D5KMZ4mLuerX0PpQ65vDNwa4x+uFJRr2ZFWDZzdYGRHSuxHLUhnTfyciZ2O2gV+hMWOs9gxlsLumuzqOMBSFijzhGOqw+qjSn6ApeIHWMrjqh1CkmKL4JqsV374OYnf'
        b'TTfoJ5Sdb4o6Qzo/2NQlZ1h02YZUc5LZeihgSMchf0RIx6o+BzLSrRn8iNTHeaiqMxO1bIM51ZCYavLjBF8xWdIcE4hs3BBSiYb0AzpjRpKJH7IyqpyeaEtzHt4ajMYM'
        b'W7pVl25LSzRZdAaLo4spSWcQh9A6aEpNDXAbcmlFpsFiSNOZaZoVuq0p0vktO9hNHKASMNKARLNxBVvmPnO2Kd1PGsUYXBcROoQDc/oLK2I/RhKMKcfKlmAyGFN0GdTJ'
        b'MuJEfG2WQ4MnszrZJFF++3ms7CjbQS1AF20TrWyNTO5bYv0XBS1dqguJigsP0QWPQCTJNCJvoinTwBnzYd98dCZSDZvBauIn4wkJWy02U0LCEH5fpO3gX5I4Vy3HWnRb'
        b'zOn7Uk26MJslQxdnOJRmSreKuhCLyTCMF4vJarOkiysGZtRlpA8oqR9d3WBIFfllJuSDZnHYYoaclGuE4Ye2o2M2SMGmGnvhvph1GOqcqJJi1F1+JDs5YdLGPCGBndNO'
        b'W5LlLnDXiD2HD0AxA0ICtO7a+VoQ79o/1W1xh+BNcToh1WP5YelI9/deXnv/qFgmCIEJqT/fPlWQfNV1gqR1BAkfTnUiQiOc0ntJjU9eggJRixdCnW1Y7kSSbZlwSTx4'
        b'NMV5ZogV2C21lK+dTgCvHZoEaVAt1qdJi6vHAh+KvuvgtPPMEC84zlUIhBSu0lrk451nhlnQxRsscM1XmxnnrZDQ1XkKCxKYwIdHoESbtRwKHBCkAU66SbRqts2BYneo'
        b'3Og4ZjQQ9ON+vukEZWVd4gK4rpZgRiVcdSA84wlspTyEckDnEWQyFEpAo2+uP2ETf8x3HkFCNxZwgjHToI5F+Sv40HkMSVFUkgOxetKgPRiNLQopPF0KghoeT+VYnYNd'
        b'ln06NqaBkFrmPn59rFcEIfC2JS4Smi/X4iUppbmJxVgpHoSHUDmAzpvgrF7BJ4qFk+HiwaXQ4GwjVNXBOZfBVbZeSzR2OqfS4TU+F9TM2k4U7XOck23U8+u7xs6izGF7'
        b'0sDR8qkQvZxLNQpv+FKT36iBpvbFUhzuUW2jDHEvNAsSKK2fJmnhuvXqDV3ySewWhKjdU+IEPkEMXktdFIiP3IgMVAmJ2KYzzy76lVL0ILl/37hrdUXIxtAQ9zNVz35w'
        b'JK3H6+ANXcCeHM3EgFW5GY2+E+f1fR7S9H+2r9OuG/3unvLP1avOvPm5ckZjjlBVYFpa9YfYr15en/hyYmrIrwRV9ibdU9cvZs795LTl47jAhXsXzvUISQz5aWGh0XX6'
        b'J681PLGf3/aTr37zfvSf5pxa/ZFXe+r6v5zubYw/5Pmvv3u78M6fA+3TXT+ZOevtOW83L/k0tOCVPRefpiUe+v3Rlv/Y8u8fv7Xw4mXv/9x8/PDHpVmNpx7/bPNv8ipq'
        b'P3jjX8Wm3277c+3bc4M//0lv4A/f+mD6V02/n/9Gte+rp3487UzSxPdfn/Jv73+wLLY/69a9pqgs+3f+8cnirv3fe9Y8OTWueUn62YaA7td/DF/8duKmjaaf3L6id7Fy'
        b'pW32gNO+/t7h/nDuNTlh23q5P9YEWFloT4Hu474Bi6Amws9HH4DlfpTuC5N0yr0bx/F2ZAdgkbH+UBiLRVHqNDgpaDfJsQwfpFt5anB/2yF2D46Pf4CGUAsRPyVfhE1Q'
        b'ZmVVDHe8Sf6oy3EzzMFYk3Q7TLa/DxYtlAsB8FiF3dCFjZzWEkIiDVgc7ReBZVBMbka9WO5JqKjRyqq4lAMUjiYIMgE4DfIX5VEcxYwns8I+OAW39fJ+ubfeQpoq6F35'
        b'x7d+Y071y/Grki0Zh03pumTpDqsAFm/X9Ltx7x/P/mDdxO3MC58Q9EqZUqbhL0+ZXDaBPkfRy03Grrvz624yjVzN3mXP31mbWjaJf7K/POkvJWuRT5NZWA0jhjOjV/cr'
        b'2Yz9Corh/S6OiNivZCGs3yU+3mJLj4/v18bHG1NNhnRbZny8Xv2316hXWhgGs7C7cCzMuizsZi8Lw2Z83hq2tlFsbbnCZ9OIb7lMzd9tOrrm74mXI3GI6GV7ncLfgzfJ'
        b'lbAjZWiEii2R1IjFMVgWG6ESPDMJPfcqlsHNJY5k8hVranRkVIyEJmWCdpecMt2biVKRp0+zlRDocqZsHILqZxkVjsDHFuHiDHzBwsANUcpkpQM7KgoUhB2VhB0VHDsq'
        b'OXZUHFc6sOM+wo7vy4ZjR35H3CDwaMlI0xmccG8osBsK4oaBtK1/A0taTFk2s0VCEJkmC+HJNAnqOG/TGxrsY50YgBjx2UwzmtNMYRZLhsWHEzNQS9LIEJHxy9iVYOLw'
        b'RYyIjxyLkkYMX+FIUzBQuSHVsE9nlqCtMcNiMYmZGelJhIU4thRTMmypSQwrSbCHg1wHsB0ZFYWZ2ZKfgzAC3AZdsL/VlkngygG1uNQII3qzHn5sIv3fwEiqFzCSKsbG'
        b'kg+s3ZMz0t2AhVE+G/2geat0YyC7EBsVES0T4A4UkpPq0S7fsGyrOTUjQSGuJjI3Rr/3aULAr/WGcENqcmrim9c+S9j7+vtvvP9GBXRXLD/TVNNY05HXFH7nTOOZoFJ9'
        b'beOZWbUnFykEP1ftjWuL9HLu1OYkjtL6kBVgIZZE27hbxBoskQszoUuJbdgFBdZZjOUmaA2ODNhIvpGdsXLHRx0bhSnQrUyHyxq9fIihf52L49ber5VuAn3u0Twlj5bE'
        b'fNYY7rksXs89kapf49SqfheHfkiuxJ29sbs2h0yvsDBcaWGuROrGXQwj+LNBLubOmMEuZjZdm0lJbYNjkbWUTzsX6lhkHz7g27eA9qPshey3CashHzqhhKBUxUY/xZ7I'
        b'xVCWBa1wEx67EUio9MCLqnUS7rud46HNnuXrSeCOkCelxHccRUewR+/VZsMjWRZrKiAscoJaGBAyYOl6VhJumekVrCT8VSmbgKckWINt0xViMBSkkbRkGQLcWwvnecMr'
        b'8/CcNjtyc7aaiJ2mUAoXXnYgrpU2fEpuzgvuOdwcnMUSfssOxbt275VrXsi1a1USknsIj7CWcu0KzMcymSCHMlkotIUNcZID2QG7r4OSa+YmpTtG5XZNsmbAWSq/0Vn+'
        b'9esSbW7lQ9Psr3UVzK2w7t+crn5NFskG/48nkcZUzpZosr6YNg5jkMklw2i0kVdMN77IqDNxDIsL0YVS9LYwr7meooPRmmGhVDDTlphqFlOIUOIh3tPhxUMptbQYUl+g'
        b't46MM2AQbwa2KTZ+17jPltCtPn70sX49+wiN3RxEn8Sez7rgdbwhNNTH7wWKg9ZESWnGiOkvWySXc6aU9BLVJObAD2UOEyD7+VahcYBiRuaLEZH9fLuoOGTz/tuybpkw'
        b'UtbtRVn3ag578D75rG8VVPDcvOdxRbtcZ+apzl89JwuB3n0sN1+1UJkjJdxLdWOFuYvr6FvCqo+2bhSk5LRnIubxjJ2ode8UdmKPdP6BjYZFUAwFUEABELrh3FiZ624r'
        b'J1S6y0uYFp6uoszd/b2EfeSvpdy/bxU8WMS88/wgIQjurOBXpy5buIjlVlegN1gIhuaJnMTP9owSdIvvq4TMBL81gcmMBPPkR7B+FKOwfgNRwNxNkku840cOusuFnclg'
        b'ZZwQtwjyOJG6I1ph3KpetTAqwW/l1GRhqzm3+TWZ2EFNkcKzeWVBnhDoHvb7udH9p2p3PMiacPfHsu+6/3K2LfyB7o11IcFHvCo+c5923T7b/Mknx06c+HTRw4ln6ttd'
        b'vqtxXfNW/2vbP1w8u9D1cs7K9qJTQR8qAgKnjS95t+erkribc9ter1zSEJFzxH57x5s+IZDws6ejbBF2w7bxH+XPvfj5ojlNnrf7l01599/3//JBxbOY31u/SE4Pvhfz'
        b'lw9+5/r041+U/eA1687qv4v58kZO9x8aD/1V9vGKJR8e/oFeY2UeORRuYTfPrqTUClrD/bERO60spEVpfAfi+yK86AjxA+E9H1qt7BwZiuZCnS8hYkqzWK61kDr5szGR'
        b'LkKQIQGvqCNWQK2VPaQBvTPhKnn/h9pILNEPEBwPdqUmB59YWZE6B+p3Us5G0QHzvLJlIWMm8Tww2BMqWa62MJaxelyuhhaflXCat604ttWRefG0C875ekIb5llnsCkv'
        b'U+hqisTSSP1yyhsdSaJXoGIfnINqvUyK+pr/Uq4lARFXKbOiKMFhSKAEQ04IgjO1Yu9ySpE8eerkKVPKWco0m16THC/L2EFA5XmC068ghz0In3xTbqQYlBuNG8AsjPY/'
        b'D8Is56YMxixMNulQmUqxOjFJSox4kiyMRrsCSqxwXS/jRZ7t06ETi6OS0gZV3dfi5SFPegwkNuzGBYrY8mT5wBMdsq99osMRp7/80RCntVlyel+DzZM5tObhdXBN+386'
        b'mRnR6zqlM9TrqmMkp3vtFWz5dj5Xv2Kwy8Wn0M09phZasUzMYqWtWjJjViwNg3Z+7wg0e2IjGREWRWPJFiyIko8JgyY4DTegjr7ohTjogN5RLtAL1XjefOOIt1xcyTQp'
        b'Tv9pgt9AVvBZwo7X+yoaq2Thi24E+if5bY/r8TXEGNTfDwxI+G3Cjrcm/eD1v5cLW0I95lS66FVSoSM/fjtzGqRPjwcnBk6vAX2vcccD9yD3mK8/do8d8D3+YIcH3Gax'
        b'lqDxed+ACD8fuIqnhpR2Mm1W9tiXLue45EMgd9kQNwK9q6wMiialBbPKz1k45aj+OEo/pUckc5OPaNMu+0zWAYse5bToWcySeUFEZpnw3GIVUiFi5DxCJjVyS2RjJpG9'
        b'iGMkS8wVfuc52BZZZWH7q1iEeSnPq1USv0Ls3zA0uV341oaWTIbWPERPt2Smmq3igDVJpwdkMjp2Ndli2MdPA4ZZltM6DbrFI6a3Qzp7h8Zui9m6eaefLjQ8LDRyy7Zo'
        b'yntDYiLjQ2PXh/npQkJ5e3zMtuh1YZv1X58Mj2REPCK7y9SzVTJeYnX/ODRbsC1jqnV7oY092ubLno0rjNoU/jwbeQVuYKUemtyg7hC9IqDwEHvqwg0KAuERv99xDJb6'
        b'7IGSwePJfLjrm4G3lRS9qrHeXNF0SxA3UfdPP57xacLu19vJSDrygk7POt1RHVHZWNN4pjFvVsPj8Bv5bv5Bp5vqOgo7FN6zn7XnNuVlzTL6Gz2MHdPjzkyeuwX7cg/N'
        b'CqVgpBaKZ49uv5urV1qZtiyBRxTFBuLykR1y/xRs4jEU7fR7DcooPXsxiO6PsLIMbc7EI4MCIt58We65K0Cyu3qrwWttJI/R3mrBdZKc0F8e3h+iuyPbhhvlEuKgvHuc'
        b'0zyCNDJ3biCeUvY96f/BRNgY7yEm0u85PFy5LIO7vuF+PjHO5FoJFQphAjxUjsc8BYUr5oAWQDfJp5g1E4orp9S6fCEUSRY15YQyJQYvjmxRjpocf0RxoCb3TVaVQmnm'
        b'nuE1ucERjBev0g1pPKEZIXCxdIadvmWa6AIFuKGhJEKyrVSD1UrZidFAUWgoUR7PDElS2e+FvGwIrYEc7ZtSNCkl+98YUGUj+gKNFFBXQwee+xsBNXX2iLUxCqjn4T73'
        b'Jg1HKIvRUEBNSDhaOFYhHdh4Y5fC9YgUZlmIzYZifo/jS6vnfE2AjQyRQiwPr40vcdJPZ7sI7qnLZeSo/Lo3awTzP0ZYVeJOaok/JEgh948qZ9D9XUJKcpThe8l+m39H'
        b'vuX9N9orgmob8wyy99adiRn1wwvwqKLj/Zv5806rWi5Nbrm0jfyN7PalHnXLmtOsSOch/MsvJqhCH+jVPCBjHzzFviF1uinmQQF5FZyxMse3DvviB4H4WF4FxzJyMdHL'
        b'F6qEl2LUx8e/yn0TXsFbSu6bsr2ckbsxy8oL6J3wYDJc8uWhe0jYzsHTVh31mI2P2fOeIzovqMFrnBeg1HB05FA2KrCaWFER15VKvIj2WU7o/k31Qnce0kmlmcFwxzXB'
        b'6bjCmLtyl7nJpdjuLrNMGeS6+rXM1cVnWBggGOTCRpyQuJk64MwYlRVDnNlbQ+qFbF9ixkBfZCy2QN8waTuX6LZcr4iJ2aCXbdDLYzaYf+fzPaX4FyJa+/CP287+bMvY'
        b'TePsf3j80NV1dcG4h+/7/lvR5pLp48M8vFN+8vaVU5t0+3/8i00R1oPveP/bZLv941+8/O7DZ57XxF//6EL8aq+DAauqrAd+ERcz+83S38468UqPtrQ0uGxb4M237wd1'
        b'v/ebRYnvTEyfsLXHbfbqNbeOffTdrcFzCn/9cUtUgbVh3L1/+aovenKYLebLz9rDX/VSeewtmLK/6dol9ZTCd74zpn7nRm1r9zs/Cq7pOlXdkrjkwI5Il093vK1e2ln4'
        b'w1SD78/f/5Fn9rvPArK77I8/M77ssuytWZ7ltsPzX1m2ceKbE9xfy7yQfvifbpSP/c7yZ/oY8UzXhY9W/XX3P17dHhD0uunxHkPFnd3v/dw2xj2o5Y8e6cHgfa8vunLl'
        b'P/z07/c+/sV76X2xRUEzPq94pWTRG8Z3V72Tsc43ti6pyHzMtFU8lpTzXXFvhenM+Ue7/unPW7Nf3xZ2be6vEhevuZpqvpNqnye/GbboTNqu5pRdZ0w151p//cnHl/Nf'
        b'79xa3F798zj3nc1z95ieBTT2fOD64d89HH2vY9Wmz04987r1vbNllv0XVrwZdfrQDxuO/uQ/J67s/qfSP/UmfL5l5YHNRTstJ+d8Fq+Lr7z0xZt/Kfvzsr6cB2kxvzm+'
        b'fN2CO/96etetTeLML3Y8O9JZeTWuIuTPC9b8Zs4n/9z8n4tv9Bx6snXx25rutuoL/7xk8/wPvpiRNKcgZHT0X1Xrg34aYKgik+YGeG7tCXYjVDF7cFS2TCCjbcNmKdt9'
        b'ADehY7Bt7d/psK5gwg/cIZRj8RGtD9SCfWjt3ukR4idwAE1ovGwZFhOIKPVXC+q9hDjOy+dgK/Tws1Wowt5Idzzvu9EfCyKiYlSUj3TIyTLzY6VUvxSu7MY+bIlkHpn6'
        b'YEkE69Mmx+Zj+PS/eMSp9/yvnYh+LR2VhQWQEd+4t9DEx6dmGJLi47mn+BWz3zlyuVy2WKbjR59j5BrlBJn066aSkzVr+Pv/vl+NfIyM/Wpk4xSsCjHtZTmtYNxYN1rN'
        b'JNk0b7lsihe9RstllmlOj0lOTx4fP8jXefz/S1xmmT7gGNlETAelM5sP5g8/p8X8bLhOel1OSkoxGgqhHBqgxkXwnKyYjidXmA8/KZeLrKRYXvGef/FqN1g7Lv83aUuf'
        b'bhjnp3znu2NzJmqN+lXdcZtTpsz6bf6zqrd/OfvIloNhN+v+fc2GsD++njujyvrd7+seRxXW/7h07bWeH3kH/PbhV60/eOb6+19e/f4ffto1+jveu/9jfH3O6AvvzJhS'
        b'Ely95j9m/+HdtxRNP/nq5z/4aIn61U/fHh2VUpcV8mGl711z34c1Dz/dveiHL5/Ggjnf+/nE6W/rf5leqPeQIuETwxgshq6ttI5YWg0rhmmhU463of6olOR2LT/BEEQH'
        b'6zEG7rG61mh8pIBGynkvciKvzIiWhMHiArthEevwDAljjGLGqu3cFcDJo3ApMiLaJ9pFUCuhWC7XxGG1lUHz0TMSfDfCFWxRCbJIllJ3QKeV/++JR9nYPRwozYZcKFsY'
        b'SY6gjEJRuUJ4BTpcoDwRq/gRXjrUUZYwbAycnKsWJq5X+sRhOw/uM+AJ+ZMuLCFzX+iT5fAqU2zYZVPCGdMRfqMEtEDVCZZfYe/WSCx2EZT+MmjFhy9zEli+JoxH/sG8'
        b'TIWGBZinhJtRqdz35GSuwmI9dXKoSS5hOa9Nim1QnyYVIQr2ZTg6XJxCIIStjOdyhL+wRyUsh1Jpk+p1cNaX8FF1rB9l38XSLuETOd6zZQ9JVab/97if/8Y3Sq2+xn+Z'
        b'081Wh/9i5VnBg6EbStAUShnzACxJG8URD8M8boq5DAkttMwY8AEz+xWppvR+JTsM6VfxJL9fSQmDtV+ZZDbSOyUr6f0K0WrpVyUesprEfmViRkZqv8Kcbu1XJZP7pA+L'
        b'IX0fjTanZ9qs/QpjiqVfkWFJ6lcnm1MplelXpBky+xWHzZn9KoNoNJv7FSmmHOpC5N3MojldtBrSjaZ+NU9VjPzg1pRpFftHp2UkLX8pXqq8Jpn3ma39WjHFnGyNN7EU'
        b'ot+DUo4UgzndlBRvyjH2u8bHi5SMZcbH96tt6TbKLJ77Nmmx0y3smNHC/9EOexjJwp5SszC5WdiDgxamThZWbLEw0G9hSaKFPZxmYY88WtijjBYW7SysXm5h1mV5ib3x'
        b'Ywn2oKWFPWRmWcLe2INUFlagsDCMa2FmZWEqb1nO3lj5zRI44CnZdrgNeMov1g/ylLztS43zNp/+UfHxju+O0PXllOSh/2RJl55h1bE2U1KMXsNuwEnKMJJM6IshNZUc'
        b'/gyH6jCITNfdSPwWq3jQbE3pV6dmGA2pYr/74FTNstopwEFvkv6tkv6TE/ufIFIFTSlXKjRMxyLHsagk+79qWRLG'
    ))))
