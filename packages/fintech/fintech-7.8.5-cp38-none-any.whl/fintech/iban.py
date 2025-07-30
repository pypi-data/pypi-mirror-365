
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
        b'eJzNfAdc1Nm1/28qZSiKDfvYGaSj2CuoIF2wYYFhGGQUB5yCba0oQwdFsCAIKCpFpNrLes6+ZEt2N2VfdkP6SzZtU142eS95+16S/7n3NyAjbHbz+efzeQ8/MwO/e++5'
        b'5557zveUe8efCK/8yOi1ml7m5fSWIaQIe4QUSYYkQ3pGSJHqZQ3yDFmjxDQ7Q65X5Av7lOaAHVK9MkORLzkt0TvppfkSiZChTBJcsjROn2W6Rq1dE6fen5NhzdarczLV'
        b'liy9OuGwJSvHqF5vMFr0uix1rla3T7tHH+DqmpxlMA/0zdBnGox6szrTatRZDDlGs9qSo9Zl6XX71Fpjhlpn0mstejWjbg5w1U0Zwv90ek2ll4qtIYvebIJNYpPaZDa5'
        b'TWFT2pxszjYXm6tNZXOzuds8bJ62UbbRNi/bGNtY2zjbeNsEm7dtom2SbbJtSuZUvm7nY1MLhXzh2LQjrq9NzRe2Ck3SJOG1afmCRDg+9fi0bSQlvl5ZnG6oIKX0cqfX'
        b'GMaInAszSdC4xmU7s98tMoGeBf2nW1rMewFJgnUOPYRH8AzOYAkWxcdsgIJELMSyeA2WRW1O8FcK89bJ8fk+d2so69meNIX6lWPFfOqM5ZGxWL6FupcELoauxEi/aCzF'
        b'0qgYLI5SCHlQ4bLz4FE+7aEIJ8FNEHJ7Z6a5fU21ULDupIee6/ZpoBl7XNwTI4loadTmSLjjg4V+G2PxXJIzFkVuJtKOc/lExmB5XEz8Zh9qKAwkHhMjN2728Y+M8pNA'
        b'q1ywQNG4MGwy6SSvqJbHgEQ2fsHWZHrYhS8plJLwpSR8yaDwpVz4kuNSu/D3vCp8F3rFDhP+FVH4T4OdhI+cJwuCOi1mSXSWwB9ON8qELCVjLy27ackJ8eEPUlyEmPS5'
        b'9Cwt5rOju8WH9TsUQtqECWQmadlrtuuEFiHblR53z54o/6NXgptM+PG8T6X3gl8EhkiyGR8JLpePjZKmeVL/kO+FfJB5SOCPncZ/uu6NqT7TpQk/kvx125QxXxH6BWsA'
        b'NZzAbqihjSgJTPTxweLASLTBY38shpZkH9qSCr+AKP+NsRLB6OmyQiazjmf60DEabWY3ErYrVOIlAWqgEwt40w44jefNJoUg4AVowRIBCpdhs3UsG3V9jJ/Z5MR+icMy'
        b'AYo3Q751Amuoj4WLZrxHv2KtCisFKIVqLLV60YOJUaFmKGci9cJGAeomuvDHByNW0WPS+XhvbCICG8dax7HhDXByrvkAzQ4n8RxW0CRLx/A5dkKVzIxdSmo5RW3VAjHe'
        b'gefEUWcSsdlspVF6sodzApTE4knOshHP+JvdadDRELwmwGXoxQq+TKzF9qNm7CHGNKStF4kcPF4oNt04DMVmKGULa4ZzeFWAK/MkfCJowKfQalYR3xtdsIERPOXCJ5q+'
        b'C5vMB0ljsXE81ghQDg0KK9OmQ2u2mj3pc9pK1v8S7c1FPmBzPFZgjzvNP9UP7whwDa6kiHM8OA43VWwDoBbqsI0GLUjkQ7Dl8BoooV2TjIJ6Z9pEPXZxjvdEwB0zdtN2'
        b'QjUJ/rwAFXgmRNzpIrQ5Y4+VOIPT8UzUF7B1l9WbNRVjMZarsJPtdSv24F3ah0yo5eOO40U4bT5IC8X7ROM86/3AhzctgHw/M94nzrWkd5cFEhGpH19sMNSmmD1pkEco'
        b'm+rKOigVRXpNmoo9ztQwEa7hDVoZTf1UbLqHHbuojZgISsRbxALp3XNREpWraL96LNS0fRebqOIAlHNlkEA5NmKPG9OGK1o2qg7r8RYfNRNsEdREwoggFblNBLX4RKRX'
        b'g5cO0jq7iPWMULxODwRPTs8rEgsI0CSMUyjEDgEaoQzr+Ki9JrhNbUxIt8KZjJoC8Q4fhc9D8RE1kWwPkGZ0kl3gE2jgyzpCWkptVuJwL9xkunduGto4wX0n8AztPJus'
        b'NpeNatJhh3UiI9gzHx8Qgz1sJ59jEbYySdVCl2hld4nJh6yZTPBwAlOa+gA8xVUjEctW0U6ycTZvxn/dZK3dNFbIVc5srosky3tMo28IfEg4NsF9FXYTMZft2EdsrPMT'
        b'hzTjnTxVHi044zU2yWWgLeItCg+oUeE9Et960okumsWIZZxYzuxQaqDFLocm7GHaXDBG1L/2dKikJqK2AJ+waRol0Cbq3z0i3G22MKaf4gUsFKAAH8Ep3oj5tPxzKobF'
        b'cBoeMrlfItu268zDiXBS5cp2//wSfCiQgG1YY53MiF7AruNQEoaV0AelChJ7jgybJPELMF+c9OSaPVCSRzpWBsUKYWWyPEsCp47LrWoufzwJT+zNISnOA0RcoEw6IRav'
        b'aGTW0dRNDU1aLKFdz8n2FnK2YZ+Ijp3QDW3RxHC6F5QL6XAbrnCogxt4YW00MZuBdWH01qy2zmWTXU4NxKpAKMVCaAuDFoU2lnTuxt5wuJ4SKywwK8iSaydYfTjwYqUF'
        b'q8SOHVjNhEW/LoA2vB6I1XJhCpbJXWZMt/qxzufoX6vYm0R8m3WPhA7Wm1iq593hqVxGUNHCqW/A2tEDxO8MId4OF2JE4uflSjOcs85j1J/CqfFYFQntxPJg5xC4vTOT'
        b'9/WX4YNsqBfZbjRPHuRaoQUbNtES4clelRpL4PaWMcJGtZNqk9nqz8RROG+9wxIl5JL4X3exjH20Mvr+JsWBHVjL/d7ESdTDzokUbmGZLF0kT+K6QoKEEpJjJD5QYt8a'
        b'qLPOpiFjZ9AWD2GeyUUOjxSbhMnYI8NOaq2wLqaOW5buHCJBPv8dKA0YIp3bsYxKe6wyPZas/64zPKRgrE3cgftYM5dN00HTzBsnDpLBedLoaijIJJ26IgTjNQWUb5/J'
        b'VUG7K8dhA8Ttao07LG5WlYxg5aSVyzQ2YNlIitCCZ8lI+GbZ5E4K7OYSysUzy1/2LnOkTz6E9IeGLDiqgMv41NMawpQB+jIHhrzcX+pYxue5BjeYRsmFEKxQEObdwbtW'
        b'XxoWOJtg00HlBsS0gfpwvu7InclACjhjeHpciOMsNxfaB7eLfLbz3SYTNZs2iEJtW4AtA2Na+ZiCOFL2w0ymUEA2SfoUi0+dQnwCuELBqTDCk6qh1kW6gfkpPmH4PE5c'
        b'hRmuOWPperwvcnVtd/bAgDY2A9zc7KCCdqZqFGa4lGudT0OiR8HFwa0btOBwNVaFwAWu4vFY7xQAJfiIM5W7nS3CroBEUzfOPtVL0cmFAHis2DuHHAnbcPLMxeH2Ia1D'
        b'TX89UycS7DwZPk6hQIh1DiDTb3tVwRfAHWfyHNR3Mt6TYdcyaORbTajZTYw56seQUR1w0a4gBxQUuJyGx1xZx82lwMyu3AOdyf6VWMfZkcnwrjf0WDWM96twL2BggrtD'
        b'tYKiibOiWlyXO1l01kWsdxE0eo3EDn8ih2632DUU6MwVTFjtTBbRjJV4hSJQBktYDvnYNQRsxN0Oz8NTagVFLA0KUt2TntYgzpWzZugeOFgSc5EcaUKxVkEm+wBvW4O5'
        b'bkCp6qXKlr3UQvZERpr9wM3Nfe9CSaLCaTF52i4uAN+ja6M5TGC14sirWsJxfhOUOc0wzBHFVXM0YoAxuKC2AxrvyqAsFPoIMiiuqOdL3ndw86s7HQKtOynq4DvdRftA'
        b'vfv4nkHVDKhywA0R+R5C/iYCmNOkQtgxUwTt+3Be4mCb9g0OCBPRyCbDRwkUyrAMNJn8SfmrXEixRssA9T7pGhn/JXGDbkKtbLhmdqSLejAZO4nfqDGchR1QN9WuYa0D'
        b'XaGXlOYkBUV2Hes9gk3WQEb40uQhGz9Ex0QNCg0VtzMYryig/pCKGzrkj00aJo0FdqCflGYfsVVB8WMzeQ7GU5zx5Sx3BtWLGfraE9zOE2KclkDlSk5/DFwY7ahhd16u'
        b'Y+V20cpD4bkCKuCigSvlDmwnDR46RqqzTzIKq+BB2GgoXCiB2tWuvlgXNyleVBgb+dSuYd6Y2Vf9Ti4pjQzvR1L05i/Gj9V5Dju7SzsU3e3wZlXkbqKQRiNmCHcoehm2'
        b'axRIqMVdeyjD7olQyH3AKihfOaIPaFuNd0Vjfy73IFfTLTL/mELF1uEq3I537cQ7ZNgBhZkc/kk8tyjReBXO+Q7geTvWJvg5LYIzBo7MSW54y8FdDGgRPsdng5r8HK6Q'
        b'0+aoUDJhy8jyh54ULMMze/F6imDa55xpILOp9hQVqQif7RzUJGcHjGtTeNk9fTvzlIWUTgRxU1QddIy2rtKnQ6QhRjpQpbDA7TARfW55u4zs9tkAPG0YUPJGhnNNUCVu'
        b'eG/WS3xv9Y0aBnYElAcWShKcncKyU/gWUgzRlj7IXSiFUQOCa1ekkxxihZAJCkruH1s4rCyBux4ODtMu43byo1zC3XJ51i7RjTWZsWmkJdyJB9GPYbHc2TJGZINF4c0j'
        b'6HUb9BHesN7LZPh0BzzgIpX6443hMcuAPXvsGhBOlQKukjqXaWLEFKMKCuEBzz+wnmI2nn/coICG59ql22ebWeYZjLexiLKqaPJpPAvrzMJGM/ayUXVKVusox3y4zNPf'
        b'ZCyFIl5WidfzqkruCk7sYNxoM5RS9pu3HusFYqLDnlAZ8MZis0nOMkEPtAmU4JzEh+L8BclyXoU5tpDXYMhV1/OGo9iTzYswweQaWBEGbidxxmLxFlSZsZsNPkdZRbkA'
        b'JaHQzBnL3jDb7Mpy+YtYwhir3jZLTKTuEnyUmaGYWPA6zLLUq2pKpPg6C6A8yF7TacdSXtQJpkyUJ9LPJkCX2YMIBpEDuMLKRx2jxFE1tIb7YsGH9vUGL/nMW80n20IR'
        b'wl2x6BNJUROr+sB9Kyc4MRnP8KoP+YsOXvWB3g3iJj3Hmmli3Yf82SWx7tOA9r1owTodNTpxfDjJSgQXsO24mHjexKtYwItC+Pg4LwqtxZtiglsF+WpeFYL8MbwsFIti'
        b'xWEVNEeIRaGdFDHxolCnUhzTCrbdZp56o20x1tFK414TqwDV0OfBS0IEOOViUeiSfbOgd8Z0XkQJoGXxGkqbim8ItEdAu/kgMaeJZmsq26DnA3zw8UKxtrKQdobVVsLm'
        b'irNcw85Z1MKS5atYy4pSF+B5mNjWCFVQzesuBDRneeUFy4yc4PzdcMHsSaMMB1jd5SrJ7ooon0JsXijWZLB2vFiTubZI1Iqri2jDeUmGEKCeF2Ui54tqeT2b0JOXZA76'
        b'85JMxmHrJEauBCtoO3q4YZD/sTFBkFrAE3tNbSvZUY8bU4t7O7CZZlOSQTHJ5sIzVnxhtZyD+JDXckIm88R5pnS2WMgZ48LrOKn25RY4k6R7eOUCez0YsStQncT5M/hu'
        b'wR4PVqKsP8JqBtfhsos46NQEUr8ern34NI/MhBSkaaG4SwUZfthzgFrGTmaCrcB7Gs7awlgKdXsOMEW5SZKlTa/cvlok16Fdbq8kkTnX8FqSk73YBVVharGYRHJoEYtJ'
        b'pYGiGO5DmV4sJunxOi8mQfkMsenccrAXkxbm8VoSDRPrTLsp9m4Ua0nQQ/6TFZPgSa7IyH2ywOfUSNOlULxKUj8PXdu5/BQmKzWwwtp8ZodVE5L5qmS7txLrfcyi7sED'
        b'JvDL4WJZeEMG4U+PO9OjFgljvIEy7NNcYQ3J1JUXrYK9ec1q6hJxsX3LWHnMnenKk2RWE7qO1Wu5WE9gaZa9mHUimZeyvCJEnvsoXL5mL2TB7WW8kpUyRdyLutVjVdhJ'
        b'zB0iZaWGq8p1oq03k9s9Kda4cmkrWY3LA6o5c4fdDquc2XoalrAK040owmOurc+gdj+vfvku5rWvidgmWnMlntuhsrBCFp5hClQFlyeKvHXjjZViVQyeHuBlMRJvOR91'
        b'8CDc51UnZkS87DQa7fXN5wvwhiqPaUMX3MMWQli8uEJsak2CYlUejZKR82oTKKl6SFE55+Ixnl/OC23ReJNX2vD8QhEeHi2IEAttbj68zrZzlgi8NoWrWGfDU568zuZH'
        b'YbCID1AyQayzQTctjxXaZsJDPsoPL0GFyoPEEO6CT0jiFDd28nlc4GSoyoNUbg424zPKfDbu5NTIiGgEdjEnd3MyE10jwVGTyEMzPoSH1EjDJmbiA9rxGSfsFbAVGpUL'
        b'0556yk1polt57uI+3ITSKSorLSeRjJ0WejFdbFi4zJ+X+LCEbIiV+Hzgniia81CepDKzXSjfyhZTf8LuMldg6RECG6Yh09PwKauuFWXxQ67jpuMs3IFCe3UP7tgjPygM'
        b'w0o3bII+OfQkQ8lmYesuJV5bgJc0cg5eG+HcCXKMLdAWsxFLZYIMn0kYHFJyyewoYH1wNBbHKAXpbkkaNAXK14mlxkrydY3RhPmtAYFYNl/DDrLcRsnGhawRd75vOTTO'
        b'J3CN84+UC/LVEmhdD8/W69hZyMCPUhDPnvi502qBH3Gxoy12zMWOt2Q2l0wX+8GWvFCeLxxTHHF9TT54sKXgB1vy44ptQoaMnyrKf/zvtAOu6iE/4ewc1KzWGvkBqDoz'
        b'x6TO02YbMgyWwwEOHR3+iBKPX3335RgtOfwo1Xfg8FVtIGp5WkO2Nj1b78cJbtCb9tsnMLNxDqTStcZ9al1Ohp4fxjKqnJ7Zun/gkFer0+VYjRa10bo/XW9Sa032LvoM'
        b'tdbsQOugPjs7wNXh0dJcrUm7X22gaZaqk7PEc152AJw+SCVgpAHpBt1Stsw9hjy90U8cxRhcGxXuwIHBOGxF7EdHgtEfsrAl6LW6LHUOdTKNOBFfm+nw0MksA2ySKL/8'
        b'PBZ25G2nFqCOtZotbI1M7knx/qHBYWHqNTEJkWvUISMQydCPyJtZn6vljPmy33zVelINq9ai5yfoaWnJJqs+Lc2B3+G07fyLEueqZV+LOslg3JOtV6+zmnLUCdrD+/VG'
        b'i1m9xqTXvsKLSW+xmozmpYMzqnOMg0rqR0/Xa7PN/DET8kGD+ZXFDDtJdxZePcwdHbeeY94svDU3BW+J4SYLNX28+THt3yZ4C73Ttezs9rXuyBSBd8bSWHLEJfTbdsxf'
        b'KGyH6ym8s0riKiyeQonpqLSYLQdGiwe9B8Z4CO3LVpK/TfOLT0sWOF6tnDwTWCDKA8QG8QjymcaTA0vgktmj0162uOA9ES6vjRobQqEyP05kZ4nbUQzjZTux80AgP04U'
        b'DxM7XMQguYxQsJ0CikviiaJ4nnhNDNkmUFBVsQEv8CNFfpwYmMPxySkZTlGc16HKZfPcZp7pNpzhE01btYOWqjrAGjrZOWTfNk5r6p5YM62An0GyA0hKZG5wh5GAjRQH'
        b'l2Zjj5k5J4o2zmMxOQxG7NgCH4u/eDwpHk0+jxLxsWsHlkTuEg8n+ckk2AbCxRJ4tB7vT7IfTrKDSWwOF91P9wwi8Xi/ikvnHksizsaJR7DGxWjbjT18nbUMnlv8OQM5'
        b'8/08mDhZvHiRMdAwjz8fjwUaPBcunnKy6Dw0TyPjk+yC2lgKtVpeNkF+tBg8wfk1cF09dJbew/aMLRJ7V2teTgMVy0RfdmE0FMHpUWJiwbOKQ4kaqXi4SKlaxaqdQ5qg'
        b'z5e3HIEWTyRVEQ+i+SG0XxBXsx+lK4VOjynsOoJbfWKaIB7K4iO8TEurCg1iUUiVkE6RSJfh0M8NcjOL2tS/+e8VlcFxsjVu637z+68Zvd7cEpk4uzj5wpRTXt+4G9Gw'
        b'bovrluI3slt9Wrxm33pndN6y8hfBiyUbCn26ygpvdv3w2u9ytqcvS2tfk+60YkrT6h+oDrlfSz3/6dolpl8EB347NGpX5UfXf/XGG12e7h/bllw64ZHTdrv8w49KP1Wd'
        b'frpna33a9qIjZ/Iadx0e33flRVHJn4LOylw+nj7j/dnvz1/4u/BCp9jLz9/temJemfzXltcsP1v0XuCFE5rny//w9oOEijt/2vSzqsqPnlR98uGmacGpURk/6tqvvXLu'
        b'+Y7/Sfpu7On59zvkjRrLWx2dZ92ndD09WP/Hr17/wa2gf5k3W3kteswnX7naXvv6+OaPfuTxcO9ad7eFbn96/taLzL/dfKFxsjCl1eLNPfP9fSL9pRRhUaIHV6T+O+GG'
        b'ZRoTeA25/4L5AVF+vpoAJJVZ5YdFguCtlu+GmrUWZnVBEdboeH8oiuexgetKVaIUy13wCqc9GdqXsZs5vv4BEmFupBJOS0N98LSF1UI8dmVS8CtekDkoXpDJ8/fF4kCp'
        b'EABPaVS3AnuT8B6fRZNJhlQS6xdFCb0wCVqUC6QeUAq1FnZxybI+NlokAEQuBrvn8PhlHJ6R4QOfuRppv9RHwzRV0Ljwjy/9xjD0s3HLM005R/RGdaZ4+SqAudiV/a4c'
        b'8FPZH6ybeQsD3ROCRi6RS5z5y0MilYyXuEpG0ctVwp678eeuEmepkr1LXr6zNqXEm3+yvzzoLzlrkU6RsDqHEMeZ0Sj75WzGfhm57X4nuxPslzOv1e+UmmqyGlNT+1Wp'
        b'qbpsvdZozU1N1Sj//ho1chMLvUzsMo6JGZaJ3QEzsZCMz1vD1jaKre2k8OspxLeUeGLv1pn0bB+chNtDhW+XfNUMLvwkbCAsYYf68VIhmtqwJG4zBdnl8VEKwSNXttgv'
        b'iIeeWKqCjugY7PCKw3IWRUoEVYoUO0b5if7nevzKwdhzwqzAQ/hMJxvi6tg6nAZcXZgweEVKnim3R42yQhlFjXKKGmWDUaOcR42y43J71JhJUeNHklejRn5nbkjYaMrZ'
        b'r9YOBHqOIZ1j+PZKeJb8d6JIk/6A1WASY4dcvYkiyf1ikDNwkc/RzccPeH9ixHcTzWjYr19nMuWYfDkxLbVkjBwcMn4Zu2KA+OoiRoyM7IsSR7y6wpGmYOHk+mztHrVB'
        b'DGp1OSaT3pybY8ygKIhHleasHGt2BouSxICHh7f2kHbkeGidgS35ZfhFobZWHeJvseZSWGUPsrjUKDr0YT382ESaL4iOFMOiI0WcdQXzrr1b2U2y4TcFi2J8N/pBazK/'
        b'NMhuGhbFw1M4GxMVKxGgDYpUSyxzkg3b33CTmxmd6B/O/yQt4GcabeT7adrszOz0X6ftfv2jFx+9IHdZuaSgpaaxpiu/JbKtoLEguExzqbFgxqVToVMFP2fVjf63NVIL'
        b'O6ynSe7iQ5UvGQWlk6Wx2YesdpScDj1yajsHpy0zWMebOqiLDthIIAlldktcBncILXvlRrBhu0bqYPWfh3fc9PtV4mXRl/DmIcJbBgMwLw5jJs+XsKTodx7QrX4nu5aI'
        b'uOLG3tiNTofpZSZ2hcTEcEXsxvGGEfxwCN60eQ3FGwb1+BwK1Y6LdN0ss6/xqpN1OQ/1SrB3WA7cQpHZGegmp9HgJ8Niy67oBVB+AO7ATXjqKqTjeXesC9skBldd0LpX'
        b'ledB4R0FnnlqbIMqMSLCDqLQo8o7wJoKBf/jeFU7d+AC1xO4ZE634j3PELkgxfOS8Xsn8ZDoNahZZA4hOUlyhIWL4T5U2W+XBWKFRJWXpyRaZ4UpcBKvwB18QoDJlDJy'
        b'me8g5HlCYaBAQSnPt6uPSAlw4T7WOqTbeE0sPyx2h8L5hKISQQrlErNn+BpoHwaWg3nBSgaWMg6X4l1Sqc0503kQNOVfCJpnCDT/8nmpNrd2x0T7cyGDwQvr/sUJ6+fk'
        b'kWzw/3oaqcvmbJn1luGJ4ysMMrnk6HRWQkejbjijA6njuoQ16nBy5iaGnhHkJXSWHBMlg7nW9GyDOYsIpR/mPe1oHk7JpUmbPYzeWjLPgCG8admmWPn9ct+k8GRfP/qI'
        b'iGAf4fGbgumT2PNdG7KWN4SH+/oNozhkTZSW5oyYALNFcjnnimkvUc1gQH449xUBsp8v5SIHKebkDveM7OfLeUeHzfun5t0SYaS825Py7mX0x2ws3/AlPcvio0P8yip8'
        b'ytOeYBdv4c9bM1h+vnyi3wQx5VZM8xL8tOxueNoU701W8WYjdOMpeCBm7XAbS4TtEXkcdozSmVAChVBIXhCeeo6RuMAteMgJXc31FD5auJjl7jGJmj2E2fyqnwY6oY8V'
        b'F4OdsUAIXnaCPz0x71gorS+Ecj4hBMrhLifxYjO16dcIQm5azEdbpw+QWIT3czkFLDUIwcnwmD9Nga7tvP6dQOgmJJiXcRLJYSrhzxv9WVnBb7nrAiHZENLorzD3UlNv'
        b'ffSc8mAPCKIEbnZs/2nvc48OeP/xPePXJdvml8zxWht1y3W872zzqffeUngvjnw/4ptvv/Pff/3rt/f8cY5WVSqZ+Vpl3yfb/iu8Yvb6137cqRsn170x7+qP7m39evSO'
        b'x7PW1qt++uuJ27ozQ10/XKH2+XZj4ahvHHxnj/PSn//lWKLiJ4Wz7+SOmdWivL1tifc3f7k35buVUXGGvr/N7fD6cMvjH/6by6Jb3y/42o4FUR//YMujJUd79zc++qtk'
        b'VWzYot/Ea5wtzHck4l2JmGflzBV4ljWVMqFZbPso468f9PCB2BDr6OJ1eI5nTCRDLGHYTtkWS7kCqY8/XpSzUdFOJNoGZRRcwyYL+2bHfuNUVbQBOrFUM0huHNjkztCw'
        b'z8Kr64WkZR2Uu5GnSBidJ1kTs4znbMZtO1jKFhjvL4UO7BOUx6W+Y+Eyb8vZCNcH0jDyki0Cy8NyIizMMYXBo1XRWBbNEkWeJXoGYfEB2Z6ZeE4jEb2+8z+UeImBiIuY'
        b'ZpGP4GFIkBiGnBCEgTyLvUspX/LgmZWHRC5l+dNMennbX6YxQwKVl9lOv4zgekh88kWJkmxIojR2MGZhtH87JGa5MGlYzHIqBdsGcyQxT4ay9NFok0Hp/i0aCU+QoCQc'
        b'GrEEzjsNrb4HQeewL4MMZjrs+hq5bmmmdPBLH5K/+6UPu8P+7D0H9Nokot/nBOuZPNbmfnZoeft/O7v5XPgdkJIj/CrjOPpCfRI++nLw670wfgj8zhvNgzJv7NzNS6Ze'
        b'WMyrpmty+VUNvC45SpaExbH4+BCWJmFhjNRrHbTAWWiGy/SLRkgY5QT3JlsN+tVvyM2Ml8pv+n2S5seSA3tqsO31B5WNVZJPfhsZ2hzkn+G3Zb42Tqt8Jygg7Zdp2970'
        b'/trr35EKSeHus/7Up1Fw3MDTUqi248YJbKTkwBE3EqGYWy3ciNHZKzyEO1Aok/pjK9y2sC98jYImaOAFnnBoGzRdVuDZjzd4j9yJ/qpohiLQscURSGh5nP4yxdiXJaC9'
        b'ewVeAsqSiAYnHdGqnfboLYM2PWrApmcwW+b1EYlp/KDNtsjEusSImUSLRGzktsjGeJO5mL1EWzwp/MpjqDWyUsNuaDgeHZ8M1wZrVpxdqJB9gaFJbcI/ZGhZZGitDnqa'
        b'lJttsJgHrUk8SCCTUbOnmSbtHn4w8IplDVinVr1gxHzXobNPePzmuORN2/3U4ZHrwqOTNsdSIrwmLjo1PD5inZ96TThvT43bHLt23SbN38+ORzIi7p6PuToZIyTevPL6'
        b'fmKgwK+KH8NWE/sanBRvzWffoyuKSYwUSzksQ8HzGmhxhcuH6RUFRYcFqFO6QqErPuEX0uEutoxmoweGkv3gxfUcB6fhbTk0LZ9sgLIPBHMi9a7W5X2StvP1TjKWrvzg'
        b'szPO/n5VV3XU+caaxoLG/Bm1TyObzwSfbbncVdQl85n5VufJlvwDM3T+Ondd19SEgomzk/DBycMzwoNke5YKJTNG3w1coZFbGJ4vX71WtBJVkOifx0End6XR8ByvqaLj'
        b'kof50g3RFqZzhiV7B73iLbzKvaJ1p4XD+iMsOBjNPbWPUnDxhofYKIXGOSaHdHhkI3GlpMI8JAUfO2Anwc4SN24pHmIiPmnQVkwTXiXnPWgdrJePg3X0O1gHK/gmmvH2'
        b'/Eg/37jBEoIwPiIFHsvHkXMqJ1elpk4hll1YwhrZdZdAKGZmtA3LlMKkE/IsvDju8w3JXpvjX14crM19SWP68a5Xa3NDHRcvYhm1+3lCM4K/YukMO3/L1dMD8muOHiRK'
        b'NKlsrcVC2YlOS87HkSh3Y9oMsfw3LC9zoDWYo31RiiamZP9X/ahkRAhwFv3oJriAdX/HjxrXDk1khvjR7QYOIf+e4C0EZc1jWcyUdZFrxDPCzdA3hjvXOCgSb78VD1zh'
        b'7IZeCqFEBzuyd8ULUMo8bPYKPkGdQSm4WTrk7Muqo2ZOEgz/uuymYN5OLVNmGBzd7q/SsjJjHs7Qvp3pt+lXhCsfveisDL7UmK+VfGttQdyod6/Ck8quj26emXNW0V4/'
        b'sb1+MyGN5HZ9n7J95VlWr3MX/vj98Yon0zVK7pS186DsZbXO6g+Ni4f6ZEq1Tlv4reIOsGEzj+YLlfaAPp5XyLGcUDBWISyKUx5PgyqePIyVwV0CJ2zR27241H/pEe6e'
        b'8YYT1HIHvg6eODjwTKzg8DXuEJwVPfgEsDnA1+g5YonxBl5OiR7KgBmLRR6mw3k51h3BsoEQ/ovqhm7csZNiM7PhqDV+ALXWMaxyI7QRPbybxDRlELc0sn4Vw7nUHBML'
        b'C4b4+hEnJG6mDuIao7LUAdfedKgbsl2Bm1ieED1cxnx9vVOwbtcijSwubr1Gsl4jjVtvqBuVIjN/SkTffm3n5nMfJo1JHGv73dPHLpoL8uCTTw/+y+5EWfpXi119sj54'
        b'v0GZqA773tTqiIMTytL/dMr203dXfevxWx7XzT9772rqCs+Dc5dXH/jk+wlrZpq/8tOTz6/3n/3K+nHz9nl/6+ffm93/yz8cDv6d6r7zr1IU53rfN6S+d+nNn875xumr'
        b'NX9Jb491PfG9nz2ZuaVy5TKfr6TL1uRPmBm3wn3BNyNOz37Xr+Hs2RtZzWV547suzfHTT3xn+4uNW7quLGzXT/3kO6+vD+u67J+tnzw1e4/Tsu/8i/E/Oy8e+/XPX4+0'
        b'7TFVhltMh97rVGxYvPFKwKMl6z2/uuRFVNyBK6FXmy+ar374tiLAFJVz8Zc/cd36H3llx5XeH/x56SLv9Eu135uJ+3/7i+yLP/jt3kXfm/WO858Ovx5uKv20MHjaJ4ta'
        b'q+eVhr648Syk/aHx0+UfT3z/8Ivom4cWfviJZmt1WfEvRuMvZ+ijd2yf+bqmzP27vcnf6XV7p91nx7tv/37VtpqNLjsexn5c2ez7zc01vx6b8l+/CXs0elFinU/eWz+1'
        b'Jf08csOSA7deBPdod//hpvd//A093j16/Yn/xP+ZNueD9w5tCY6dkXvmL8eLx/2y6MST3x2qyC+59d1My28vzrKE3Az8YJnLu8d+pPP/3VspxZuilN+/9uedpcmPP/nr'
        b'ty58O/O/Nn1r+ayvP/u26dGHb1557SdHK8vUn0X0/nnCH+99K/S73yE75gXdBqiAq+TnJIIETuKzxQKWH3Pmme6RXftFexo0JqwLZvYU5C/aU9ExrB6KAS8BAOoJye5C'
        b'b4KFXxe9ARexD0socijzVwpYtkG5WzoLr2ENnwfPsstX8zf6LfLHwqiYOIWggi4p1kHDRm7YWDwbiyixTJqCFdQDS6NYj7tSbDV4/YMnnRqPf+xg9HPpKEzMaYz4xvHB'
        b'OTU1O0ebkZrKsSGCeZlZUqlUskAy7W9SKTsD9ZI6y6XCCP8k/6Sn/y13pd8k0r8onfnn/71/vcq4URL2z1niJWO1jSmrpISXY8e4kqS8JVN8pKzFg7+PYu+maQMoTEAq'
        b'TU0dgp/u//97KjFNHwRbNhEDVPE86IdzhwItg2Q/39VQAhUp8AwrmOuHIqhwEjwmyqZi4wLD6z+8LzFfpm4f98z3L1nhCqvHnvn5/rDn68f6yb/xlTGHJqh0muW9CZuy'
        b'fMtDo5Zqu++/+YMPdp0zZD6rSExcHtTw1dl1vw+JDExqmmuZ9fWsO6HF0Z91nJhvNq19fP8Xnx79j2x5sOuEE2fn7pbv6bUpr8c0ez5/8/GCT1f79v0t7A+Hyl7862dm'
        b'+ZiUzJ0JD35avG+S8cHHv136Ycwf4n8c9G+Fn/6nYtpWzQ/DV2vcuVeF4rBc/l+KsP+foHQHVEY7kWl1S/E2nE8Vr0ZcgGp8xGKSLtYtntzyaHwiw9O50DjDl99LCMWL'
        b'1IukkQkNWMEcDpRxaXjJpq2Cdg4zcDcJSqOjYn1jk6HbSVDKpc7QIeMFOrfQ0CB8PH+jQpBEC3gJK/GqhUVDftoch9ALzqzllaXAaAKacvJuFTJhA3Q5EX5dP2FR04hY'
        b'J+gKZJU7x4BNKUyIkPuOgbtiNeEqDSjCHixlWHIBnwX6HrAj1ySrHArwTDLPaGLx8XqWq0VjCbTDXSdB7i+BO7ugxcIuBITgJSjhjhZrvIdyNBlq5XBzKrRxIt7O47BE'
        b'cyKP9eN6IhE8E2Wb3WdwAIVLS/EBtfNWP1rZaigUM0OJoMY+9lXGyyICFkDDwfnxfuxyCLXfWM22CZ9J8f7StQ4J1tR/Drz9E980ss/DR4PRYLHjI/t6keDO4iXK92Ry'
        b'CUMBlvON4jEUi6JcZbNZbBVoUg8iwPR+Wbbe2C9nhyz9Cl4z6JdTImLpl2cYdPROSZCxX2a2mPoV6YctenO/PD0nJ7tfZjBa+hWZBM/0YdIa99BogzHXaumX6bJM/bIc'
        b'U0a/MtOQTSlSv2y/NrdfdsSQ26/QmnUGQ78sS3+IuhB5V4PZYDRbtEadvl/JUyAdPxLW51rM/aP352QsWZQq1nQzDHsMln6VOcuQaUnVs9Sk351SmSytwajPSNUf0vW7'
        b'pKaaKcnLTU3tV1qNVspYXiKbuNipJnbka2IlCBM7XzCx2NrEquUm9tU00xz2xorGJvZ1ONMC9saMyMTKdiaWj5rY4bmJqZ2JfcnMtIS9LWRvTPom9u1KE/tirol9Ac+0'
        b'lL2xr3KamM2YmMqbWEZkYuf9ppBBnGTb4TqIk3+OGIKTvO0z54HbRP2jUlPtv9td42eTMh3/mye1MceiZm36jDiNM7vnk5GjI5nQL9rsbIJ7tV11WNBNz11J/CaL+aDB'
        b'ktWvzM7RabPN/W5DU0DTqgEBDnkT9W+5+H9JrWSemVfm5Eq5zJnpWPRYCfM1/w9+F+Di'
    ))))
