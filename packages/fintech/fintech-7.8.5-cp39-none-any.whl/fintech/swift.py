
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
        b'eJzVfAdYVFfa8Ll3hgGGKiJiw7EzdBnsomgsdFBQ7DAMA4wOMzh3RuyogEPHDlZEwYpKExFRk/OmbjZl0zYhPdlssl82m7rZJJvE/5xzBwTF/Lv/93/f833yzPXeU9/+'
        b'vuec996P0QP/JOQXQX7CbHLJQKtQFlrFZXAZfCFaxWslp6UZkjrOND5DqrUrQJuQELSa18oy7Aq4PZzWXssXcBzKkCUhx0Kl/U9aeVJK1KJkRY4xw6LXKoyZCnO2VpG4'
        b'xZxtNCgW6QxmrSZbkavWbFBnaYPk8uRsndDTNkObqTNoBUWmxaAx64wGQWE2kqYmQauwjakVBNJNCJJrRvUBX0F+PuTnRFEwkYsVWTkrb5VYpVY7q8xqb3WwOlrlVier'
        b's9XF6mp1s7pbB1k9rIOtntYhVi/rUKu3dZh1uHWEdaR1VKYPQ9xhh08xKkA7Rm/12O5TgFLQ9tEFiEM7fXaOTupzH0LIRRDPUkriNX0pypHfIPIbTEGSMqomIaVDvN6B'
        b'3D9plKALO+TkLi3AWzMZWcaR22mboALKoGSOf0LsEiiGigQlVEQtSwyUoUkLpXDXAxcqOcsI0tIA9bBfiIqDSiiPg3IOLbfIo3jcBFfSNdwDXPXogWEVJQtHCPN/IUum'
        b'hw19rlhC0OcJ+hxDn2coczv5pD73NvQLB0J/zEPoR4jo/xxqj5wRcg/x+kQdHhOKWOEXyyWINgzJ/GLcGEWeWPhnH0fkTspCFh0ZbW8/1FY42w6R/xUhy5fO+ChjEbqI'
        b'9JSUs1YOk37ngSK+GryFW+356eTl87OR3pFUjJxVwzXZk/bDDMO6c790/KdY/IriW7dDbpzvVyjf+WnpXcmnqBtZAkmFO9RAcUgw4UVZ8BJfXygNjgyEUnwx2Tc6DqoC'
        b'gqICo+M4ZHBzDA+DtocIbt+DNVUlRmyUKeklKfcvkzRzIJL2Dt5LUieRpC52bmgketYoC0lzTstKFBGBoytDw+AmQaTcPwbKoSR2SWRUQNQyFBqTNAQfSsZl+DDKsrOH'
        b'WoTPWTxJD3wbH0lW4RtShO+MR/gi2pi1xTKUVhzBZdCqwm1SBEegEuGTaANcSbEMoXXnoSZcFUrmOwV7SUukWQoFFsI2pIaK1XDQDkVMR0EoKGkzAzVhrhx5on0auXta'
        b'bPT6DSJPZ8oGo/EohCCYNnL03ACke+eVpVJBTWpaIjM+T/ssbX1mrPr3mUEHfNWR6v9I89BkZ+rT/5oWrX4xU7k0Sq1M3BUYo76ivcBdGpz1WUa0ejU6oIlUG7UHpKUN'
        b'TedD5q8sV45ULJ/57fyn48+5Ltp38wnnEzqUHD3kg5JQJW8eScmaYXQiRFLGWQL9CMt5ZMbXh2Cr1AFKHMzepIEUaqGN0LIUqqBcghI56QwON6emK7lu3leplJgoT/pc'
        b'eHL5yWt2psm4VWtQZIqGL0jI02Wa53TLmVVLzVCbtbSd4Ew5PNaZc+bcOQfOlzPJeoZQSrrtNqn1Fm23fWqqyWJITe12Sk3V6LVqgyU3NfWheZWciUqJyY5e6CjUtggU'
        b'Q/S+Oy/jeE7GrvzPPE9kikO/0icLNacSvB+s/pH5cDLALx5XJBBZsUNesFs6DN9ZtkjD9xFG6QCSTsxLr6TzzHhIiKTzTNIlTLr5nZKkPvePMh49E/SXdFk8E9E12AqX'
        b'4SCH8G7cjAJRYAwus1BLi634XDAclKDMiSgYBc/NtVDbF5ajoBIIhfgKlcHhuE73xLPedkIQ1aiPXvo8bdXj+3ANbtt38eDFgubIsUU3C6JOcM9mUol7dbpz5gd6DlVf'
        b'cogITFByZmp8523Cbf7RgaFQAsVRsfF2yAk383ASE1ts49dAgsDY0e0kcj1Tb1SbGdup6CM/Z05KmG6S97JcyljYbZehTdeZTbSRiVosJd+HzbyJers+vKbd/Xt5/cff'
        b'4DV1lbgjZZ5/pMhnKBuVCCUJARwakSPF+6fiDosXNR9noWaqYF6HL00NkSI+HcG5hbjC4m0zB/iwYMZFc6aGcIjXIriIO3A5swdKeRqpOY3vTg2RID4LwWUDHBWtyJ1w'
        b'fEUw28OZaXREA4JLsAfaxCGL8QFcLpjhQMq0EB7xRtIP9mErq4ST/vi8AG1z8a0pdD5cgKB1FD7IRk2We5AqXB87JcSOVBUi8lANIg747OppgolobCPrRwZtzINbrCpz'
        b'rhZaLaudJ1NQiCGEVnwU72fTLcVXYT+p9IATkyksxKYR1S+IYeitgya8SxDWLlfRjvkIruLO4azbYLwH7yPdli6YTDHHxxB0wB1cw6CEZtw6jVTiK8smh9iT2uMIbtqp'
        b'2JBQhSzQKuAj05zlZDq4zoXFJzMgdxilTqY50MY4gM8huAFHcZE44N6RcNIJmt1mTaGVJA6QwEG4xgacpZzkJI+AI6EUaTjCOeJKvJvVyGbvcIJ2J9zI0IYijsM3lCID'
        b'iibDbgFadfh6niuFoo7zJ1zcw+AY7gkXBUc9vu4CTXTIu9xU6JjHqlI2JDptxIcIVNCOSFUzNyEcbjMQBQJsgeCE271NZtqrhvOBLtzCuoUQebklmCNwG9xwopUVnL9y'
        b'msi0Q/gOviC4QqHChdBDYseF+4HVQs2BG96PGwXXKSNdXDkkceQiIicwqzAlcZrgittwp8tGilYHFySVMnwd8R2Crgu+qcjF5VIkGcdFKCxsKCEwhEjG1U1ManIRXPEx'
        b'i8zYDcWCYOaWTA2TIT6TSDYUBrNJ1s6fLgjrclRMzIgEtgyCRlFT7kCZtwDNmnHQ6kZJd5ULG69iVF2wGO4K0I5bHG1VlzgVPozvKBXM7z1v9uDCeOTrburOWSFXSVnh'
        b'xvWe3HQeeeeuxDk1iZ+ILatXenGzeTQ9Leh3OW/a/TWVFb6R6c1FUJOx4dUdNQuxi9h91XBuAY8UH4x9Z4d3QIM/K1xhP4qL5JG7e8jzO1ZkvunICg/N8eFieRTy1Y5X'
        b'd3ivXJzPCteuV3CJPHJ43O35HW/Odglkhe6uY7lkAmfTMNixYuU/nVnhkWHjuRUEzrQJb++oUYwQZ1+1eSK3hsCJ/PCOmiVOsaywUKLk0gicadnPCTWbfhjJCj3X+hFn'
        b'gSISw94TamaOGM0KcycGcNkE+JenvCOscH5pHiucZQ7i9DxKe3z1a8KbslMmVhgghHC5BKMP/J8VatRpMla4eqyKI6Y1ESU/J6yYcHMJKyySh3GbCZqKKX8QvH3qMljh'
        b'dPtp3HYe5YbYPS6syPhJLPR1m87tIrjnWn4vrNAZh7DC9pWzuEIeRZ4mY3qvaBjECl+ThHPFhCD71E+Rlru8WKH/kjlcOY+y983pFryn7rRjhXcfi+D2ESq9vPFl4c2Q'
        b'sxNY4euTH+MO8WhFWsLbwgpz4GpWWLVtAVdDSPfysD8IK3b4rWGFO70XcSd4tBnNJwRZUijyXT8ykjtN6Tno/Q0rNn6ayQrnJMRxFwjpHrd7fIO346w8VmidFM81EtLt'
        b'm/bKhjfndIqk44cs4ZoI6RTorQ1vql+XsMKrk5O4NkK6D9xe3rBC4hTKlGErbiGGyQmO41tyqnHOXAQ3hSkDFBpxi5PJMNTVhajoIC4cH9vIlMET9sZCK9zQ2+UJEmYq'
        b'/MdBmWjGi6Eoj5gYv2RisKnOH+LGwkF8VSnK/d2Ep7kTErT55eQ38ryFRTGscHP2c9xpGlgvfMu4IjR7vCjiiue5egmK2LXgNaP3zqLhokD4/J67ICFyH/SG0XtR8uiH'
        b'QnPHnpgiEqGeBeL9dRDKdOwN06X/cpj+0MLP3fbrH7yEx1sUjAD4xjpclkBWblVQEhUXBJ0LoIQEm15p0kmhuJjhsZBoH+2YNnar3rJ2gRggfzLNga2EHleonbcmbUEi'
        b'PUulLsPgXExwDFQmkFjNAQr5Lan4DDO+oakkrrlhwa3ELJKwnVuJcGM2vsbq1k6Hm/6+JNAtHoKrg0kQ45wlcQsTIya4houDcKs8lsAwE83UwAETJZ5I90gpW3q9nGYI'
        b'WLbWiPQ0/JjrIS7n3J2Nzs+vYrY1Be+PxyVQqAqh5vwAUqdsskygt7fcoGIt7ophUXQVXcDG4KrgKHzFl0MKs50rcbzn2Ag78VloWbBTFcb8AUqHMytZjDrNfbY/WZKx'
        b'hS9Zn0VJ0WAodVNKyFPdOlEwL0L9TGhYTVckbDWCm1OYYKrwNbgK5YNUuIWghmuRHleTeIbGjhPwrsgJMSoV7XEKZW1MYZSYSYKTGq90lYqE0bgOrd8wRFzvHFhH3OkV'
        b'fEg1lT7VoAxolbGF+YRJcC0mmgIWTxnis9YOueZKpuMqW4ga6gDN5vWqqXT6o0gbF2kZTlFVxcbEkg7BcBYXQIU/h5xWEReC21OUPMNIA2eDSGBRp5pKVJ5EFZl6Ehax'
        b'4BZKJ+3YpppK4TuOsqA6RfTku/FJuAJlMXG4lhDKDkl9OHxmfYDo3q5AI1yZREcj+oFPoGw4F2WhMSOcwZdxuT9lBpQ44Yp4fEWKnMMlbrjTUaRs67wMH4sKt9M5ThPy'
        b'VeFKyzBaUZRjgrLY9XAjmi6NJHCHw8ehkwhbLKnN9N4mxEZFxdFNjd6FqG+Q0i8UauOClIG8HDdo8Tk4h+t9ffFFL38lPgT1/p74kNcQqB+Kz/MIl3q6k1ikxln/w717'
        b'97rGiVKYuyHfeYNHKmIiPZ1EoJX+8VCNzwcSKZVGcPjSGNyl9BR5dlniKrjgArzPZKFG6RQ3btRYRqw4XLgUWl3xdVwkVrVzSmKTKsUYq1OSBa0uxGGfEyvvcP6zsRjM'
        b'wvlBuIgEKafhlskiGrPRWbiZUcpxFlwQNs6ebZHTYPUWp4Dd4WIEfCobnyTxAHRuz4M2Oxa2jRmVLGrz3tF0kZ3nDQXQ5sKxUCoU12wSETiumOjkCmd9nXAVsberuNU6'
        b'EseybqfwARKcmXEJbpHn0TDxNjcSjsYxQHx10CSYNy2Q59G5dnMK3BbCxss3RkKreQOJgNpoqHqHGwFNyxiI0wibruATYwRoMcsQR/QBqnCrQYSCRGZw3skheocLWW5I'
        b'pnGRUDGY1aS5zqLB7XF8dKMzBf0YNynIS4zmOmBvipMr7oR6Z2KBJbO4KDiVKg53EG74kLgIlyITCTklrty07TmiCLe54CO0xorroIV6mLHcPFyxniE1k8fNwsa4cWwm'
        b'3M75mKFGlO3WuHWCHDduE5l1gKDb7s7MyUSn1U7yQHyKVkg8uBCoDWTlBNNye8Lui/ZEhwJQANxYwXSScLwWDuMyN/kwaN64iSOr/6scrkjD1QyCISolwegIFPVglAfn'
        b'Rf7uw5egk8gTnIruFacojs3lIF8tyOMm9cLmji8xXP1IlFxGpawRKnqlDEomiSQ6Z5ciuCbDqV4ZgzMmpZRRdnHaOsLD+XCuDxMvSljVbLjrDZdIqNyHibnjmZHyJM65'
        b'iEx4Q5gOXWTxRcwD7uTw7nzCv2HMoG2EFlyWB+3GQGdcQlQJijl8dMYk4uniRSRrsFVL8G/O6hVGXASnxLoK6CTRM1yAw70yB10qBpQCGqKInJ4LuC+mu7FV6SpyfD++'
        b'6ukkJwucTkdoIVyayS2G83CM9VyDC+Gy4LpqgkifI9wYtgyi/XzwCbgluEA9butVbbKSbGIkJ6vUliVODp4Kxnc5FyTZIFL1ItFdaHUevUjsc5WbNH00m4kjytRGJbl+'
        b'grOJVjVwkwbPZVU8vriM6HtNBrSz1UwtNx5uuItYH4VSLVHrueFOjnQN1MJNxRX4omgcy4lmtjqZMvFuuA7XpYy/QQvgMoNk5EJc4OSAy+f0KlQzmZ0tKg4NGeZEejRD'
        b'g+NGGZJM4masICtsUaVwF7SQSuMYx40kKvPlZrpiUQDJqixGIHPXQmOuuB67yim3OTFSbcFNDtT23MTFuW5kbQMl3ER8EFexzcIwb+JyyogqVG2CQ2SAUnxlKr4Ih6Ga'
        b'rCqPpBC9v8ShceukQ/AF3MW8zzA4C/vgYAScIlFACAox5FsSKARN+DRZQx0kHatx8QODHSKlpA+JKqtJRRO+Qcr2kXZWxyR8Bi6R0gv4cvZ6YvFv4tOO+OgCb6aOcBuf'
        b'xNcp7C34Wi+J4TghFUO6ODLcyaSBE30I7IbriPtkzC5VjyS0ClzWQ0bcBHdsnvwxXEGq0NAeMkLJY5aldMSbS3CHE1TEEGcYGRfEnJc/VMRFBy6F4oQk36C4aOLwoCJK'
        b'uTyShCFLoQnahBQkDKGbqleI64LGLeL+qjs+7OGM6wYxDoyaEE80ltCt6L7KkgCtjCkmkQ9rNlPMRCjro5hwXWbby4CaFEKDQCjqZZ/GnSDJnHcBnFoUExToF02BvuoI'
        b'1VLktlyihzbczhrgMoWRkLyM+t+KYBZmOEANjw+vJ26aTX8D18AhEklGBkTjDp+EQBlyiiHqBCfC2fTxRGOuC67+br06SOT6NNtMmkzgPegfHRcTSGcn4aRHFFTiUxJC'
        b'6N24WNcx9Qte+B2JXR5/dfLa5FnGwfPcT+048cWsu4oIj+PuPru/muruwe/fn3hoY0zombq6yPGlgwaFtvwpZsHuTRMK53V+s6Bk6TsNi34cc8jzZ36n5Mz87bfyKiNL'
        b'3337lztHjVlZmcEXcxIv3bi7MvTJM48t7/gyKXSP1rqi5afy4JB3/yFYQ3+nyztY4CF8f3hOQ/oP1/9EzOmgu8FDPA+mPP63mr+vvqp9pXjNBwuekE/SVCvHCU+oP/zY'
        b'e8Gk9tqV2tOwf/GUN5bo6sr//FPE03PL95jOJpyVKOIUd2e/4rf/e0Vx/sfb1iuWNo9QW7a614/9W/qUT0Ia3YedsW4NWvChJVPxxHddr7y19C8nnnkjfOradNWX7tou'
        b'u4zvC+c/s/rLCcX5f/3be4HhL26b/bWfYPfnb+T699WLZgU4tuwK9g6Pi38p8mzWsxeG5W0Y7d+Y7+V/ys1hxvLL9c9ePtnx/IiUW2U7PoqZmtZyeM/7p7+obl9/aWVR'
        b'8KfpMStzJrRp/T6ecvbnxrhdt368nfTZD8+Wtx9W/zE599f3Pa788O3lp3686D2j6+26BZuNB4vTv5zl+P32hgRoeGXR1uOw57lLXfvKkv/mM/Gbwpf4j86P2hh2NX0N'
        b'rHiy4864TcXGkR0//nneE+/jgB/bayfNyft+9bO7Pp9du3tNxvUT+sCLmWPen3J9zdPHtp3bO/KPP5xy2b14ormjIvZP274ueOlgi2VwxrJkj0tpI0qmVjQ3xb36p9zT'
        b'SUPucXmjly3/eujZULvXJy5uPfR8S/Wnv1xOnF016483n1EHrdVaP/9q2we/uFb9jLGxw8Hg+NbSr/Ny/65Zk7zi43Dlkx91XpmRGFRZ+MOYn7d2qDo/vH7iXPMPvr9e'
        b'+3QdPFVp2Hx9Qs7z7XGzXt+owZq2iVNCcpLvvvB8ccIzLz3fGbDNa+3sE5IbH9185XjKzGertg39TB6+XlG5+NTi6oRfA6PsPv8meLJXV+eX67/1Xp/UtPMj1ZKux6dk'
        b'X1hiLDxx9/RXr85Vf+zrdOhTpYt5NNW66s2YRPsB8SSkxXugBKoCSPSOL9PwfR8+baa2a0bmfP+gqAA/ZRBUbcW1AVCCkLdCuo4faqbuYR3xZOfpsUJIiniwwI4VcIHA'
        b'Dh1iScRV6h8ExbJYKCFjy3AlH4gPurGuuGPj6CxoiQnwJWFYDNFnMvEWouO7zFRfw3AD7oyJisP1oX5x9kgm5R1wnaOZbf42x2ylm79kSAJzOVRJ0GDcEDlLQizq7p1m'
        b'atwfG4vPLc2JSQgknm4TN88ed5qppeXhWoB/kHIN1EBpACLgNPKqPNzCwIG786AIyuICwOpA9J/UhvGuZEVzyUwXbjMM0BBDj6JioqDYQhcBhFIZPJmxDRcwgDeMnbvQ'
        b'6O9HkGWoOs7ice2URAYw7EnAHTHEaBETHBhNjyU8iI/fAx0SsIY4K90f3HL/z16Ujv9en/tb/B7iFr/ZpDYIavEQm+30v0MuaL6cc+BknCfnzDtwzpwrT+4ktMyDk3P0'
        b'8MeBk7OfBye7J6U/3p089fyRe95VvOfl9jKOvyfjncmTF+9OxpPKpOz4yItcZeTPm4zvxbmSEk+plOv7R2t7rtJvZO4ebGaxtyubX07m9SFXD/rj5aSU1NLZSDkdWc4g'
        b'9qJwcK6/OkvlnMm5hw5KSbdzX/T7nF/8e1RVciaXHrqy4R9DPacbd0c++nTDl9Rvn49rbKcbwUqyJvWPjw0SJd1/rUSGFuNGe3woAR9TciycH/vYjpioCHwoIIpEuyQE'
        b'PC4H60O7RxQWtqmTiNjuET1FRw+fo2e69O4i8f/SLpKEHfZK/55DJpAr+vxLpJIkKNT9cx9YQsWWXK0iLnlGWIjCaGI3oUH9uvZ7iDIrTFqzxWSgY+l1gpkOka42bFCo'
        b'NRqjxWBWCGa1WZujNZgFRV62TpOtUJu0pE+uSSuQQm1Gv+HUgsIiWNR6RYaOMVht0mmFIMU8vWBUqPV6RdLCxHmKTJ1WnyGwcbSbiTRoyCi0jb7fUOxcU2ylMRo2aU2k'
        b'FU35sBh0GmOGlsBl0hmyhN/Abd59KLYosgloNNck06jXG/NITzqARUNQ18589BCBhIYZWlOqSZupNWkNGu1M27wK33mWTAJ7liDY6rYqH+j5cB/Cj7S0eKNBm5am8J2v'
        b'3WrJemRnygKK5v355pMSvVZn3qrO1j/Y2sar+41jjAaz0WDJydGaHmxLStO1pr54CBSQgRunq/VqgkGqMVdrmMnISToYMtWE8IJan2Hs394GTI4IywKtRpdDRIFgSgk1'
        b'UFONxUQptOU+NClQn22yGAZsTQ/EZ7IrGdOiySbNBPJkyXkU1Bq9UdD2gL3QkPG/AOR0o3GDNsMGcz95WU70waw1MBwUWdp0Mpr5fzYuBqP5X0Blk9GUReyLacP/UGwE'
        b'S06qxqTN0JmFgXBJonqjWGwxC5psky6ToKUIFq2uwmjQb/lvxclmBHQGpqXUUChsqGkNA6HFUgh+A6v5Wr1aMLPu/zuQ6htazOx1Z319Ua+9yzUK5gcHsEmGVtCYdLm0'
        b'y6MsN+W1Vpf+CIip5zKre4QrhXguMpVe/wgJs016Xxz7z/Vo0fy36W7SEi9KlG6mglgZ0nIpdGk2pIsTDNSe2iKCfOoGbR9W9QBESKCHLkHQ6n+rq5k4+EcQ0TYObTEw'
        b'sA953BiLIUNrGNhj2qYlPnIAX91/YtLmt8bI2tTf7y6m3Ib6TLNALFUmCWJo9UAdc02EAcTmqQeeN9FWrTUExpuCHgV9v7kfgntg/28ThAdigH6dHxkPiH11ZOqBO0bN'
        b'nxf/aLFLNZp0WToDFamHbUiCrS6dCSRRYMUikzYnI++Rut535H9BoMXm/6YxyVYTbzOgyVusTYcuotYD2IT/BsCoGjA9o3auH1zJpOa3lc2gztHet3a2uFjhG0+KB5RT'
        b'iymXxUUP9ViuNeVpDRlULbfmaTUbBuotaHPVM/sG1mSAPlH9AD1WGwxrZyqWGTYYjHmG+1F3Rt91gDojgxTk6czZNEjXmWiUqjXpNApdxm9F+DPJglqdQ80mgSk5+4FM'
        b'8P4dZ9rWOTPJumAgz9C/db9je7oM9EIPHtvHi9m1e8fxqDCN3qXF5s02i2fh01zt0IJxQxGKSIt9Wh6A2IHDWn98CreSZfCscfgKmgW78FnW2GGKDH0W6oOQIi3Wa8Y8'
        b'xJadJnwXV6tCPaEZiSfVgXDaMpbcJ0PBOv8H1q24ACplaMxou+G4He9XOlvG041XfIZuP0dHBeLSYHH/9RQ+Ie7BToYKmT8UTBHT/YrCcSs+79Rvk5bt0OJjcFfcID6J'
        b'd0v6nF7Ts2v7oZLpcAHvEw8aL3mtFQ+qZ8feP6aeP1zcfz4JtVAMZeImOdwaxiMHuMnj0hSoYOnt+KLjCDp6FJTHkGU5VAVHQgXUkTnRaA8p1OD6mSxFQpMv0GbLYJet'
        b'JU2WKKE5CuP97WYvj2Xre3wOH8LWPsMlQOk8OEVzCuLjOKTEXXYEr9upjEh4Pz6Lm2nj6fa9s9PcAdJyfJpdBK7Hxyw0WX12AHT5B0EFGS4oOg5KApQyOACFaAQcl+Kz'
        b'PFyw0D0/M67F52zNouKgNECJK0bL0NAh0hBshUNspEFwGR97kINwerKNgbs5W7a1d6oqdB2cpPkA1SgDF8NBNgUcxK1Qji9kDsCuo3BYPIzvhILtqtCpsNeOnf5n4wsj'
        b'xUONalwK9XCQHsrAPriDQnDFbJHDnTPw6Qc4DKXDJdOx1Z0dVU2fCwW2VIQK830Wr5hjO0kR8EF8RoVbcuOGyRAXi/BVOOErolIAB2NJDW5Zi1gOxYbkLHZy4wvXoaNH'
        b'LCbLeqRiIj6lFE814DC+qFSpcvGBeRLExSB8hZSIyX7DpsSqVNA02WCHuKUIty3CdeJBSDE0alQqE+yHCtInAeFrOttZKu6EQmgnvVrgIr5N+i1HuB1qXFk6unmLSaVa'
        b'60DTHs6gDc4aNonrBlyoUmGrCyXjWaTHtyKZxn4t8UIOs1dTjV0TnTIesSMvM741QSD9F+J9RrQQmnANa7tg7iDUuHYhQrlpzgsmb0RKCaO3Fl/e2XvcAnvx8Z4jFzg/'
        b'Vzxl3pu9+P6ZDT2wIXSskuhXrRKPtUqhfCcUz4xhidhSKUck7yZuJ8xgVDhD8L9IKJeNz9goZ4aLjBvblsJVSrnVUG8j3VALMyz5uCrhISXE50b06OBhPxunpXgPtlIS'
        b'l+JLNhJvSxI5XWWnZPRt22ojrzSQyfzQQfgAHXsDPj6Q5q5zEQ/cL+BzdirVXE8bF6B2pKjRlQlwob9Ca4hF6afQ+DicZDBk4QJcT4Cw4nIb12IXMPzgKtRAGR1mfuZA'
        b'qq4cxtgYtdhVpfLDjWIaUDbU8oyNd6a7oZ+TphO9SXN2mTQUKT3FpK1bcME/JiowPogou69tw1yXj0ZgqxQ3DE0XTyiJ8ZlGk1uUgVFGfE6KHO15XImr8E3Rdh6CW7gM'
        b'Goh+3WcmWE3s5A0O7xx/X04OLO8RkxGkM5WDrcMH+UcHxgT6xdOXfdyyhu6UaD3glmjcjvJwqn86FSEZviLdnIxGxErxAWjSifa30h6fHCDvKoDIM8u82r1MBKbENI1L'
        b'G8DwVHqxceAEnNSIRgRXMp+TP93W0E9jhy/DUYWYRrB/IbIlphEgKm3JaW5wnAkL3MSXcUMgPvFgMhfL5KqHm4yoO+YRkPvbKwdol0yfNYOBOgNOGWzmar/0vrmCLnyB'
        b'0c0nfQ5UjYWy2D5ZSXq4zOTN225yL8lxCVEEKI2looK7CGkomUNxtSxq5xI2UEK4v3gumhfbeyyaAcUi41twxURb0pQSH+5NmvLXiWRoggZ8kgBVB/TotScZy2UC67yM'
        b'UGG3mIiXDMU9iXjExl9iVJLBcbyrX7pgSTAR8LtivuBgqBeTDzrUm4iPq+9rJm5BiSh3FXAaH7DJpYfOJpZrQ8Q3Jq5ODXYisUrSMtyAkvxxMaNqDi4lMPWVNwSVEi1R'
        b'xkZiHAYxEcFnE0QzWOuFFgYMYpo9BC7mOpkC7GQ0BY+EM3DMjbUebIFj9H0NFGgHx1HgyI3MNsYlQel9ma/M7pF5wosTTBkrIx1QOX15JS0toDAzHFkmUoKYoX0gYce3'
        b'8TGbuO+Gfcw8roTidJaEUIBv21OzhVKjcCcTYUUKvtRPgper+kowwf+w6JqOweFNuDUEn1sgISNcQEZid8oYWz3t4TAcdHMl3u2wPbGW1RFSLhnXk1AqCbHsoWtg7Zc+'
        b'4EsiiWP0gDAeKpKgOIrUBUNJIk0miBQzCZYk4paQpKWRATRPjhiZmGWJUCFFuNHFPWFxuHhEfwTaU/s7DGj0kOjD4Bij2bNSOWqyJ+LtnharzklFycQRMT+zX4DrMcyt'
        b'EyWRQTGuSuX9SKh4iglJmkdo/0FzF0n0UO8mRo4tg/G5+6pyHI71erFi6GK8zIRGqO8XEc0PEAOiZWJm7kp7F5S2UoVQYlpAg3okYraaEPpy3gPhFrbi3bZwC1/LsSyj'
        b'RznhvgIh0GxCvV4a0UAzeIlvUKAvURo/W2ZhEjXNxQHLI6m2MIVc8hAt724bRDzC7mCWRvjYZilyGO9JA3jn+XZmxFQOF8GBkAdV7jAuE1UOrk21ed+5uBwfxa1huZlw'
        b'jMRCS2jccmcb8065LjtpxdYZHPO9V4nlP2OZQiqWwlk4TWI7wv39cAQO9cmOgTNrpuKrdrglfak5HV+fwhGKy1YSre4UfX0prlhCBw3Fl2yjetlSo0jfPcTRkLqwmTZA'
        b'cP1apfj2A74ExXNVUzdG4JPEi0eTbkPxVTFVrhQfW6MKw3W4S8aiTy2+FsnAX0kGaFSFbZpERIWLIHH7bHyEzbQ6YTOZBpqIeW5BzPW3bMTXlZwIhhVXOJLqydBmIJWL'
        b'SAwIZ5ZaFjILCXfwIdg/3om94FpJeAdVSdDkgpvDJif2Sv/SwOUPCT/R0Fo5HMNFU5gp8YXjcABfJgBvXxODtudYxKkvLZqBL0/FzVC/nke8F32rqG6GmMt8Mng1vkxi'
        b'hJ2z4RDamYFLLAE0VKFWWWDv+S31pefgxJasSo9J6Td3SqA9PpyfaZlBOmzGNzOc4uOgInC5TfagJCUyellksogGvkg0OS4wKD42wY6+D9kkHw9HcBGfSaSF5aHVmgmf'
        b'DhJAgvBNOQqaYiPpShIV1hKJuIIPhNvRFzaJVkRREaNqqcO7w/rr5bjVEv3ESNEU1ETghvtqeSenRyul3qJTKIqLx8X4JrTmQTtLJr3BhWmjLH6kLgIfFgZwfsP6+z44'
        b'B7eZqITm44ZVcECA9t60o2wHZgW9yFrzjC1jqNCt1zVODGJxkzc+aX4wbIJGd1vcNHMdSyvXHdtvthOayG3SzO2W5DjjyIXuV36tOfpLzfW8209nQvrj4zfynLO3x+/n'
        b'/xAysWbEvPklHk/WHRq5fPiHKzMcX9vxHD/c1C35qG3+rKGF7vauI6ebFhSnPl4yzr7yR67r6spZR0KGv/Dd5398d9nry4yXQlR+f/EXjs+evKUopfWbcyGzwkoM733b'
        b'Xnwi8LUVn64u2rSpscuy6Vw0zl5x7cC0Fyu///6faVOOL43T7xz1ZpN69X+MeHrxnO9LymYM/4+fF5//5tbCd5WV28KWl458oTFJG+H4an7t208+F/b39ektX6rPykbc'
        b'7ZR++rmE/8eUDlnHtnfMz3Gf5N+Snjre0FnXPGmU+50rnHbKjFcPqEZ/+HvMxSW/575pyZvhTTnq83abBOtfnN51WnLR5+tXEqum5FbP2h3okfbCu7ueKa0+v8jww64T'
        b'9xIbrz7++dSOZR+aLj31oY80z2uN8cITO5TvKHNjPvDhs779R9Hn48ae/IX/Xt00MfWD35396PrNZwaHWmZnffjh4nPPz3kn48ri1guFT23fYnjqRWP78nczh3itrRg9'
        b'yj1ve/gGydy9fy9d+a3lyeTFrm9Yh7/z8bO68PLbaRurv1iQv32h2b1lZV5F2v6E0fsWL1zz8cv/8M2rOLu2wu+GT/MPnt9+l/3HG6+Xv/TBezPvPdFgmnjys19m1bV8'
        b'u8xlre79bxz9Xje9sLH4879GrH9qhOnG8NqDPy76ROf17ZZsvMtq+Jl/etKCEYljvktx+un4Bf3QYflLQ3+1vvrsbe6nYTunpO66Gvfru3WdP6cPurXwtTr/be/5F9ea'
        b'Mu22dJ2Vf+711l6/otJx3efrqod3ZO2a9syx2pPDG2dPU7x1cyN+8dOGp1+/E/jZuKJfhrp+keW/7J2fx75X5pHv8dFL8gX5jutbfyw6MyPmhwlfdd/4sCH88pgs+U6+'
        b'pWFP9a6p0UWqt+e9/cTx7B+0f/iw87Pczz97aV7bWzMaXZ/8taHR7efSD042Vny2ztKsumEeUld2e9HciEneL9T7rzly9asZuSdT/V+/EPzZ30ufejHt0xErtnzsa33S'
        b'uHeyech7g+berX1niuu25V8NXf7ht9c+PvK3T+X39hy5p/zdvf0XEhd/8P6uEVyrT/ePXcP+3HroJc1r35bmlcr8k28X/O7NyZ0fv3Br519ak65+fOT0tO0FS7fVP5e3'
        b'4xtOez5wxyvHFtTOXPih8pV/LinquLrk3LQq5fKtL6658tVXbySfHb72vcOb8+e7rP+53VwalDrIsLoj72XlmV++0I/a7HajalH+N7c4Nzy3aeiYsVnBB+q4MY+tem3U'
        b'p5Pf8PvkzX3wy69fl0d98tH2b/M7w9Y2/HQln3u2vOyw5x+Urmbmxu/g5mH+YtIOUXJqPwNx1Rbi/8nKMBJXQjVLZCIxbcc8f78gJTEGcHIjQo4redyQaWbvXuMbo6Gu'
        b'N0mKDIOvDBGTpNKyWQ6Vlqydbvn3ZAbJSHi7lyZCITjCMo9coNrJlgWF63GhLRMK145ib+wuycUdthwtnnjj+ylaSsFM7dRa2C0hfvjugxlRLB2qFO6wxKdhxjn+8XEB'
        b'0VApwHlEJrjJ5+F98Sxxafz0USSYKw0OpBH7ZejK44OgcCVD222FYwyByoYWeQ4JXS/JmmESaXIMrOPuh2X45GgSlSXhO6xSi4uD/Rm56Kh1JIxv5FUkCmcoQcOyGSRE'
        b'J3EkvoSv3n8LORjvYslWcGt+KLTSXCt8JZf5uaF4D4+GzJZKVGFKz//f6VIDZu+4/OfHeejN6RzzjLAQlk+1jqbn5JM/D4fevCY5y55yYLlMxGdwHryY1STneW7Av+/k'
        b'rg4s98mB82aZVLQtzW5y/UVmJ+f6/omjuIr9HjWe+Pe5bKgrp+BobpaUc+e8Je6cK8v3knIjydWT5mTx7vfknIxlUZGxbRlW/D2ZhD3/IpexWX9xltFSBwmBiXfmKaQe'
        b'ImS8nMFDfjzNE5PxNBVqLCmRUUhFeGmOFy/mlcnJzN6cJ6kfzmaS3aN5Z66/yqQidq58TxaaO+/KszF4kxuhcHxPSpeUbsD3SeX6z3NXyZnce/jL5nqe8pUuOdAudGP8'
        b'oxO8qM4Gk6Cy2ZbhBVWB+AZZ5pFoEqHhuRK4udDtoe8JUHGJoBPQsFBLv26DVvEZ3CpJBi9+bKPbnR0ssKQr00KTyWj6abR41MBEz2TLodJmKNQGhZbWB8Urpd0Oqan0'
        b'bCY1tVuemip+xobcO6embrSo9bYa+9TUDKMmNVWU5/sXhjmNa7sJdCxN0IEX91hIRNnp5Ao3zE6OFMdA00583vZZimColdk5blFyi3TfLPqSE3xIX1WLNLzqZjxEeC7M'
        b'0k9qbg2OP9G0d4e1yTjvzMcS311BT+0/Hql8fIiHS3uYZvyvitHPT1d8dyzvWuV7t798fsfovxwLetJjRvv7p1pHXZ5U3p7V+e3ljaEJec8+pQryuLfmvaGe/O5ttVv2'
        b'jnj72tnIj576JmlOSVRKqd7svtJTc/RmcPrSkT+vjXT6XdKU1x1yog8Nnnb9ZtKWT4q8lq0vqZ75mu7l+qKE467c2q2/n/wSXxbQHFs7ZPlKzUmXqW+lH0/6etSmtzS1'
        b'EtcZ6SFfnD+giZ/+Sfm3Fw+uiva9GHBwzeS3LJ/4zv2u44NX/vSpOWmoZXV1bMFloy4y4XDyW/uWQffeFy4e+WaZ+/KOP0/c2Fo7p9Awx8EwbOIedcYzmwKSdm/2XPeN'
        b'xPEvK/af+rtSaqZhrD2+gEvJYgNXzyeyNB1BpRmKxezS3WmE3DFQT5YQfT4Awr7+EaJgXi4dn06E0sec/OhuBXEQvY1G41YpXDPgvWa2rXV1Gu4S8JXI+MCeiBcNwo0O'
        b'sI/uoNVACxF6Jvse/4WGV8YC60dfmEElcqs3qjNSU5k1nU9VxIvatTDO5x7P0wxSYj15dwd3+75WUPqjzNlm5f4pcxiZjxypnfWldtiN50xDe0SbqBNP5P2+uRj0X4Mq'
        b'Z/LuVSQ6OfXGYoboX4N++1snc1PUuIxuH0FJQiwuwVX2yHUY7oSDklGzEnSmRJ4TMkmzNFn4qKcnu+6JcN/7h/zMPBdzesPeD+q68JMrGk82mCeO3ubUcfHJlNtNia83'
        b'Vi3f9s/MF4amJv2wc1rRwks/Ljv2a0p4W2FIaFHlqXGSSSdeVKmGXh2/aKKhaozpkPGP+uZbP33q9tTL3h2vHFTaM6+tio6mH4BKSKCJ4DH2CB9c5YRbeLiAz2Mra4FL'
        b'3SJjEuKhOBCaacOEQB4Ngi4JWcZXBLAWMa5GES+62YgrGF4eAtRIfOCo2UzX9+ZJGTQr/IJjT1Y4tC1gajAfH8CVMX0+KwUHoNNJycM+3AZdLA57zB4f6/vhKVyawL48'
        b'5ZBjpsvccdAV5h+Nq8fa0fMIqIF2U4/A+/x3xBz/DxIk/U0V0Rl0ZpuKUNIhF4eeRG1JQD4LP2JMw3qFXtEt0WsN3VKantttZ7bk6rXdUnoOTbynTkOuNMWyWyKYTd12'
        b'6VvMWqFbSrN0uiU6g7nbjn0VptvOpDZkkd46Q67F3C3RZJPVrdGU0S3L1OnNWvKQo87tlmzV5XbbqQWNTtctydZuJk3I8HKdoDMIZpqX1y3LtaTrdZpue7VGo801C93O'
        b'bMJQMQ+g20UMp3SCcfrUkMndTkK2LtOcyrxat4vFoMlW64inS9Vu1nQ7pqYKxPPlEj8msxgsgjbjvlqLaPuY6HvQpsn0QndXTNRgmqg5NNFXsE2T6IUKmElJL/TUwkTf'
        b'ODPRHV0T9XemYHqhAmaiMmyimxQm+oUeEz0NNdH9ehN9N9tEXyc30RfJTfS9cJOCXqi6m2hQbKJ7bKZp9OLfaxUodxx7rcKPix5pFVjLnxx6vtPU7Z6aaru3Gcqfhmf2'
        b'/3idwmA0K2idNiNe6WCitoe6erVeT0wfkwqqE91ywhKTWaCJD90yvVGj1hNuLLUYzLocLYszTDN6SPlAbNDtMFuMKObQ6IVFLlKqsKLkrfYkUDtw/wdGG5Yo'
    ))))
