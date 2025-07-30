
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
        b'eJzVvQlck0feOD5PEu77DhAg3IQQrnCLggLKjYiCNyIERbnM4Vnvg3AJKmpA1HgjogZBRUWlM27rtt02semal1603avdbhe3tmvbbfc/8zygoLa//f0/++77e+FxmMzM'
        b'd+Y733ue5/vEz8CEH/bY36/34OIwKAMLwQqwkCqjdoGFLAlbzQEv+SljnaUAuECNf5ZalrFZQGJ0FtcvPB21FsgsF7Fwu3EZZ/L4HRRuNZE8NwsFyowKgNlKgfH3EvOC'
        b'ooyZc/lVNWWKSgm/ppwvXynhz94gX1lTzZ9ZUS2XlK7k15aUri5ZIQk1N5+7skI2PrZMUl5RLZHxyxXVpfKKmmoZX16Dh0plEv7YnBKZDIPJQs1LPSbsyRP/syCE+BMu'
        b'6kAdVceqY9dx6ozqjOtM6kzrzOrM6yzqLOus6qzrbOps6+zq7Osc6hzrnOqc61zquHWudW517nW8Oo/DQMlTuijtlaZKEyVXaaXkKG2U5koHpaXSTOmkBEq20lbpqDRS'
        b'Witdlc5KC6Wb0ljJUlJKd6WH0q7cE5PedLMnC9TzJpNzs5cZYIFXPCe34havyS0U2OK5xasA+P5s3zqwnr0ArKPMdglYuaUTGWuH/zkQIhiPSUMBEJjkVpriT0Uz2M7u'
        b'LFJblh0TYQEUvrg6xdoGNaL6vOx8pETNeQLUnDFvtsgY7vACgWkcdBf2rxBQCh4eaY00DrIMW3gmB+1FTTmoiQLmGSyoQXXwVik1AQX7cRRUuDhoV4fRwBQDmIpGmE4m'
        b'mKpmmJoWmJpWmII2mJZ2mNYO5fY03bBg1T8nhptZNN2oF+jGeoE21BbWGN1e2veUbuX/Ct1yGLopAk381lBcAPjLKgtNogHdODiNHSdhiGn5N/uFTGPMclNuDJuP25ZZ'
        b'1nHSmMZzUqOl9cAWgORlltPFxuA8qDTHzQXGrpzH9iB51GEDdWTzsQjhjAVUpRnu8LBRURoTwA+PfxjxQeSv7P4E6OaK3K9t2myooNHak9yf5pf5rQDDQCHCHejiJtSJ'
        b'edgYlh8UhBrC0kWogceG5+cGZeaglpDQDFFmDgWqbcymxsKWSYzijO95I2EUm2YUYRIoZz9lBfu/nRUrnmeFyUtYYcGwYlG1DcCyyA03/ilHkegDFKG4Ed6i4E3UyF2H'
        b'moRZqAnVZ+enZ4RkzAORWQVOsG0ubIQHwQojE3QcHUIdCjI1bMxGnWJ4HVMAngcrNqxxma5wJu0H4SEzMewn7UcBVKPdq1FrlIJIdBEfbRNHkjGHAOy1LhV70zOhS5s8'
        b'eGgbOmAEQCgIRW1oN43pzixz4AiAaXjAxvQe+0WMKLwW4QD88N/w6oStZgXxoCJvczhHtp5sLCj/yBuJR7fXnzjQe2CDqy8breLv2eb4WmW57RK/uSwXdkOkIrKoNyJc'
        b'3V3F+iK35O1y6sKKzBLBsuySi5KuEtBt1CCPOKcRJUeyqW03uXMMi9r99qUZCri6VG5BXGvaA93i4V9ZypMcbv6w0/W1lXHvAuF2tze2zhOwHhPdhs2LUZ0FJp4gRyEK'
        b'xkLEAk6wjhNRabopnB6Qju6ic1jIbsI9qAG1oCY24MRTsBcdhD0CzjArSCC1wsOeFTIiXPxt27Z975xYLq3ZKKnmlzNWP1S2rqJcPm3YnDbpxWUlcsnGCXUWAa7DxZNt'
        b'YDSVArYOSllrdP3Gpo2q/Iatyq0fOvO13gkD83TeM3TOKXrnFK1tisHZXVW2v1LrLFTLtc7iLrlylsHRXSXZl6dMMzi6HE7fn66SqGeo89UzOiu6nLrWaOy6ZD1umnkD'
        b'EQP5A+L+hVqPZJ3jdL3jdDzegd86Ve2kcwjUOwRqLQO/JiIpJTIpMB42WltSqZAMmxQXSxXVxcXDFsXFpZWSkmpFLW55jgBEepfxCQmk1qTRBhcTN0qsr6yWbJTsNIWi'
        b'KIdR8EvFiLWLsqJ+ddPqbRajLCPK0WBhr4ytj2+KH+HYbMvanrMrZ1uOwdTGYOqgtHgyagSMbCe3bstjfmVEFA+aCcEF63j2zFLWyyzCK2QIizhR2iZQT20C6yXmmW32'
        b'Ei3HLewX9J61hT1mE17a9/M24SliE2yCca7CichuN1RNQwcoeAsdBUAEROg22q8g9jzWBvWiA2x4Ox6AMBC2MZxuNXNdjrXVIYDWV3gR7q34tvlLSpaMu5a+oyBaeOJA'
        b'BcWOaYUq2N9Uv70k2iH7dOP5A73K6N03Dpw3f6t0+Z84Xyx9Lftz07nItMDhraF2azA8xSLk3c8FFKNNO1E/PCREu4MzRUiZkZ1rBCxgLwsdhXeTBezn5YTEb+NCMmzB'
        b'yEd5ZU2JfOPED7RaxI2pxVwKOLkdztmfo/ZVy3SOQr2jEAuujSMWEys/AxdLfrtFq5HBwa01VhW9b1rbNK2lt9T2mRxLCR2GjcokyyvkUmLcpA4vkV1aeBnZdSGyOxEd'
        b'IRm1hhZeglABll43IqQ/X/xbpfeQWQjosU5g01b1wwR7KooFgratf79q/rT3XWmpwNFME+qXyWPCOSA2mbUcoLORzvTwYo4jFccC3Nn2b1ZxV70bSRv+UKhJJYMpsATW'
        b'syQAnUc74AA9/q0kFyqRBeK2xeqr5mf2xtPjrbE9bCMAbLDGjLUCoAvoOuqmx3+R5kolY3bNDnlz8/ySt4sUjsSn5aJemTwWIwMyWNUAdcOWYHr0peluVCoLW8qce5tV'
        b'+Y9XM27oNDwWS4azwGa0m1WDp09EB+jxu0I8qHQWsFXbDG/mevjFKXBcAiLRWXRThvqjMf6O8BIL7gSoD52ppCHsTD2pbBYIH6q4v3m+2xcyhStZoXMxuktDGAF4mYDs'
        b'Aqgf3fGjQRzm8qnZLGA6kvzaZkPJH8QKwn90nYLHZFKyBrxkQ5DqwY6ggwb4O9eHmotZUOvx8WZu5YJXaAAWurMI9Ski8KbhwWUs7IRRXyq8QQN8l+pPzcdMANyPN6sC'
        b'v5vCrNCOjmbRECxg8QoLO1qsR+2FNECdRSC1GHNBHfXrzSree9YMk09ITWUyMVlAXcraip0xOh9GD0+3DKKWYSaMbn1VNn9VcDJNJlvYiXEm87MB3J3Lgh0ADcCGLTRE'
        b'd2QwVcYCyZrI38pU5lc30hDocB7qpiFMAKqvYMEjAN1YjE7SEBdyRdRKzDpNzrCMa/HIi2ZduhQv0iezNGeBhdYsdJWKQhrYSI+3iQ6jKllg2aiZXmaY+7qU3jM/hmch'
        b'JUIKT6JzLHgWkxnWoTomnJRFULWY1xpzvYybYZ9LAwjQoVwL1BuNQVBjHguH4WzYChmAbzeLKWwpZqv5v5LNz+5wpTHyQ3XonIV5JOZbZSALHaLMMKN3011oVxQ6ZYGu'
        b'ERYVwgsstJuiZMH0zjfjXcpQ3zprFoD74G4WOkEJUS9U0ThkwDp4V2ZmhTQUMEONLHSXioHd3nSfJWxHuyzWKNA1APLRaRbqpfyhZjkj1wfg5WKZhVROgcVkORXlCa+W'
        b'MV39qM1eJkfXLbB4bc9loWZKaMFnum68Ak/LrK0wSeF12MQ2oqaiGzJaABZsRi24x5oCSMNim1HJSA3rGK/QBk8G4a41mEx78XQDVGhFCiNlF2A9vGJhVQubOCAMnmD7'
        b'UsmhqJ6GSoC3ooiI42AOdbNqcWy9BO5nSNVpCy9hhY8yJqp1g1WOTQR7Dk0qPrxhSaTQCKBr6DatfFfgdtRJd5bK4AkZdkN9NiyAg6XLLHSJipoN99KTcpFqswwDkU4x'
        b'GmShbkrsVSywYYLFV6Kp9VhvR2XvygxzvBk1uFAZS73CArXLkt6TqVa8W0Q3npkXT23D6qq2/lhmKO2bRjf+ae4UahcLpIMZ78gM/oHmdONMx6mUkpjKWCRTlQ9b0o0W'
        b'G6ZRTSywMrzsvoxrroulGz8uT6ZasYK2zn4gUxUN1dCNrqkzqDYWmD+7UCdTeUsz6MY33dIoFdZMvo1eNn+j7XK60SCdSXWywHot6zWZyv8rim4c4aZTamIZXd5aPT8/'
        b'zolurPfKobqIAVwGVxvK2hiT/mhmLtWDVUUj+fVq7vpSMd34bvVsSkPUocCwer7pq7V0Y17SHKofi/zovNdWczMOLWZYfAntR60yC3MiGLud2ZZUMjyI6miGQCXci05Y'
        b'SK2tsDhdRBfYdtRUHOjfphnimQjvYvZeX4e9cq4PkWvsxR3GbLIHHysEtpkUcIY7WKiN8olLF3BoLD4vf53qZIP1rZuH1hlc8gR0Y0vafUqNvfsyyXs1BtEdH7rxU/s3'
        b'qNNskAxc3qmZL7IqoBt92W9RXWzAb3X6uEa14EPTSac0s/HQh9zfOWg2dpwm57RnR2lQbvb0xGb8nz8824IXo7OkXAUffypD/XmwMQ/txaZ8N/YX9Rk5WNnw+cJ5GSdw'
        b'BtzOeIMN+DgBBjw4YFnlrjg/5rB00dMUT3x/ujU+TC9yqAE09+YbwY6ssCy0Ny/DCJiiXawZsHmDG2pknNr2BaGwD/aT8xtsgdepBQD2YJtznQZ1QQeXCYNEKauDkTIM'
        b'h2SWK9g28Ag6SgeFc93QZdjHAWvtQAJIMEKHpQQFGg80Ba8Ekk1M8fk9vNyTaSx1NAGWIHkBm78sOwrHxLSTx7rtIg4HpbAJ47IflMDreHZ/MsUdAbyaRR+cWtBeeAru'
        b'QE1ZsCUsA14MogBfbmS9EB2hpcwbnYXd4iiA9qBeYsTActSBZZPc5pq9aKEQn+/pWy/4sJ/BAXnwtIOAjZoSUDO9flEsUuIjKpbqy/QxtbQc7aI7UBu8XiqGVzgBOOqF'
        b'x0ElPO7DnF53zy0TiwEfKw08BlbA23A7DYBt+BWWWGwsRYfwhxNg1UJMYoKfEAexGnEMQPtgC+5RgTI4gLbT+EWhZliflYmRa6lAjbkMi6xr2XGoB7YxNvkWbHAXx3AW'
        b'wYtkCSBBt+E++t7SAmySO7Oyc7Hra0N7w1CzkAIWCzE9C1CXgEWjGoAuscUxLNQjw7AdoHwGOkSfyzGHjweIY4zTM3D9CFjhk8mYgMP261AjtQafaXOMAMeTgidhMzrG'
        b'BGPYfbWKY6hQSOjUCVa6YSNPBGgpOoTOCTFXNqQGofpceJEDLKeybUQ8JtpojYH1YngNLISnMJwaVIajOwo30tO0EV5GjVCdlJ1JjsZsdIeCR+AA3KPIJuqTuVSWnZGR'
        b'Q26xPb1FERQqCM4JFYhY5vCMBJ7FfD+9UBwUBM87CwWwDZ0WOsI2Zyd02gWew4aqwdEWYteGblY++ec//5kvIyL5pJKdvCz73SQHMObnzxsLV8OLuaJ0DuAkU7AbNcCb'
        b'Akca97SV6IwsCh62kirYWE6PUb6zoIYGK8bG7zjqE8I91kzfNUogiKO7FmRjq9mHxWnfGNgdSrhsMWNF74SiZhnezy0MRQFiDb2waOxgoqY+eAZdkKGrDmsU5rgT3qL4'
        b'cBs8THcuz4PnZPAUOoeurUP9RoBEMN5bsEOkCXkaT4mdZTjqxp1WZOJeKhJj0MA44T5fOGgxFzVaW8AWFmAvpBah+gCa3+JAdEcGW9Ftufk6Dl7yNsWDu1ArA3Yr0F+G'
        b'dW4/7iMLbqf4Vdgb0GLS6ixHfbPhYbkU9eMtwjuUO7o0je6Lh+dgvQxdkWOXf7caB78AtShgA90Hbzujbgu0H94ytTIHgB1LpWMJ6KL7lsEba1FfNNqnWGNJdtBBBaJb'
        b'6DrNhyDYtNYCHUOHrC2xXWdPoTJQfS2zAXQR1mPfsw022khx1MW2pmLhhY00FLUF7sFdxyQ26Ap2W2wfajqvhlHUo+X4HDKds4ZeCl6jPF3y6Y6pPkmyBHjQnGHcfoqP'
        b'jubTxJCidnjGAp5bRXex7alwHHbvZFSpE13IQwfwdvcqQAgISVzO8LrDDEtno435mrXYne4L5uAQBja7RtGoeeVJLeA1eP3pfjCjT9I9rqvisSD0hTwTK1t0ieFHPT5a'
        b'd8hQZ/kz9ITTGC/bSwxKX+CMZxKHnTXTdWEO2iVLQT3PJA5uFwk4DD/21gpR3xR0YQIfo+BpRhwH0W7YzDASNhUzjIR3kmiVz0PqObARXcd+XWEE/K048CaFg7fuAroX'
        b'HclD52HjOnTNEtZzgFU6Bykp2M4RCNi5zN2HSBfYYhHu8EwgYSfsZ8QgA9XJcFjb/0zq4GnsEGhTcm2WBQ52704Q1rsBAuZQYx8Auy2MiszN0BXMnwRqFjoO6xm6NXvB'
        b'4zJ+0hhFD1HeWFe6ma7L6I6jTALPPVNwIVIyIt6HzxYWmOLtpjTHzbHduwu7GNb2bSDKDzXwuCUDeAkL6+BGGjA8DhOmD9uxuwpLKek7QwUWoRv0ektw3I4j1yJrdE1O'
        b'mHGc8oNneAwqJ+CVNNnyTeiahRnxiVfw2eBWLuOgzyUtsMA6fkKKrqKrHJq/oXAXvENvvAIdRgcsbFOfahQ6Da/SwlxcBdstgsrQVbM1xoAdSMXPxWcyApIbMdXCBftE'
        b'3EEBdhCVgD1KO8P0Trh3pmwGvAKba8lRhOxMIIIHGZI0w6s+MnR3IbpWa2OM++qpAKhOVpC7GmXYORzBGz8AW9Ziv9kMG+DFGHgeHSTYoUNFeLcLfZdynNCdfFppUufh'
        b'M+UBE2CN/Wo4CJ+H2hWzyVaP49/zGOIwOgyVz83Uhltb8QpX8N82tE2O6X8dN7fioXVm+MB5GHXBCytXYbt/A6rNYHspOjOmuw0+snQcEUwg7VkLRlJPkicxFj6oYRJt'
        b'BzjYfTInGxWW0QsWz2hohbbRxNgAL6FBC6yTe5+RcRpmyQzcJyqPsEDNWThMSc8JpR2YEDXnZLKhSjQHKfMKgkJzMlFjNmrOEBSm46BkDtKgflkRkDkBuCfXdpqnEaO6'
        b'+9AJdAb2zZnNAvlBlAPYjG3ODpp8HvBcdQHe6B54AYeevuhWIcOhO8a08O1ZPEGhJfPordYumv5MY1ET7GZ0VpLEiPQZtANtk8G9aycwNwbtxnSg7821YgJnhYpQZ0Zw'
        b'JtnaJQ6wKWRXYgSa6QGpnugwcdHNTBRiilQs7DpOkScDKbSPip4F8YC96ejA7JDMPJExsMjC+objzWZ6r9FZxGmcRUeeaakC9tIRkg+8gQmYmZMlIivjEDQ9yB4eY2PG'
        b'KdGZCl/TQpYsEZ8X2LYFRwtz8vTJ3GOf93/4lytemqEr/B1XPr3OV4+8vjH8k5P1gY+NAz8qiz4SkhGxa+StX91LOeD57YzEbRkpli6hP4Gwj6xmbW2pOSe5Ln7b7bOA'
        b'd6uOt/9xQ9Ifjl6f+njaAfWd3Jvf/jZvehyVkBG6Zcdr77xjem7ZN/mabZvfSPzM7Vb7T3/XKVVbzsW9vTHvVlrtxi8Nh9w/VlT88cLZtJyFrVPS/tET+8e8ii2R/Ibj'
        b'cT/UnfG4P+tQxtGCeR6y6dsl0tI1bhG+785pHzm/5V6mqubmVT/uLK8T6reGlU5Rxp/FWF49c/zOm67fFzf9aOOuPOw4GPIo7Z6wKvBXVdzqrJq1jeuT9n8qW1+cU7s1'
        b'4e30gI+vRYSefS0tY6DZ7VTDjxEVW00erTG6nPEP9qcOm+pvf7/VMGXGT2Xdi3rTw7svT/9QUPG5+6XB0+vDRY/++sHe7Nf638iOW1xY/kTIbeE5mITKfhhKu/SHwOu2'
        b'h+3uFb2q//J7xTeu5d9e/LHy6JWd9t7vV76fuSqq58ePv+LLfr+kc99/zTe5ZGqirJ13UXHlmxm/Wx8qbX60ZF507ILFxyFUhmxtEt99o+qrkS2HJHtWiCP8Vgw7Vw/c'
        b'W3L37G9uLrx3o/LeJ2+ud/mh71XThV0mvsHdj483xbz1K7ejZ8/mpzVLFJI28WsfzC796Khp9z9X3vD+Onthf+ylT1Svr/F4vdm5ym5gg31xzVG/r68/WvWqx4bbIx9M'
        b'Df0s1+qLzDe+On9sZvrZDQ4pF1fvswnweYf796nHktKOrJh6a8kX/9xmdOxwdGdd2ife15c9fuPdGyeHLK68nlbxm/CIex6y1x6dXv6B213luU1NLlc9F3/qPzp85acf'
        b'Zb/7MC/vieztt25zfwyb/gm4/dvHB96ecmrQi/tWWXfp/R6TY91tnaNvG2/sa9so/qaoJvFA7FGn34X91f8D6pCJ9HWT99/92+tlhd8cW7Aq61pSCw5bjvHy1wMLdvDs'
        b'0s+G64p5Tj+k/+bHkR/LZs56f9GXqZdjdSeDGs0vP7ks3/KHO4l/4vyt4csEp/k56052H9XO290+aNcxsKVq6PurP20W/rSqK+s19w8uzBKc2j7v1GabEufVylXFXsOx'
        b'r35WavHNsdMeP9k6HT/bsPetJeKj8Z8PfxLfavXp7R+tao+Ed2epBVaPSRrAsiKkQo0hudjQn8DBNmoJwecJcsfpEj6E1tFDYPt01CoMzUBtwpBgQSgeguoB4PI5S9EO'
        b'eO4x0fQ4rNT1qDEfK+jEZ17wGpfuxjb7JDojDMXaW4/nxzZg0BjuZYkqNz+mLfJudCg0KyQoHes6tiN49dncDegOOv6Y2OMt61BrVkZOcI4JKISXjDksUzt4h0bMDx1F'
        b'24XpIcF4VlRPjlNskBngMIWNjsC+3MfEaNpZCLPyRHjJnXLWWmo62mX6mA6CmjCeF4WhAtQQAsCaNGPYwxKnzqL7ZpSHosackAy0F5C7qr3GUSzrYnjqsQftluHAlizU'
        b'iJpmOWZlkOMJplYZCx3B/mgPs9XWdJYweHynZlNY2I11wuMr0WEa5XB80hjMwvYSOwdRZgg+92Ey77ZHA2xUN1MmcH3ukcd/tpARZvCf+9k2/sM8drFnHm3IpSXVshIm'
        b'6WTjS9rohzClxmPPJlnA1X8UpLGsYh7RZSvH4OKuyta7CHDNkaviaR0DDN7+6pLTLl12XRFdDqd5rZzW+fusybD0ti0PXUQPXEQ6lzC9S9goiLCbNuIf3Jqq4u7LNQSQ'
        b'iuu+vH15BidXVVDb0odOoQ+cQrtkOiex3kk8CkR4tKePOqJzhbpEvVy9vHM1BrDbN2sC5Kgx4Hkej+2IVUe1T+2c2ppqcPNUrekMbE0xuHsdT+hIUJe2J3UmYcQiuyL1'
        b'7qF4gDfej5/TtEekUBkZ+P546jXq5afNmA/0SvQHd746tWOqaqpBHKdKVXvqeOFaXrjBw0dd1rFEtcQQHo1b3XU8kZYnMnj6quUdVaoqjdGA4xUrjZXBT9A192SOOkcj'
        b'GZBfqdJUGXh8tWtn3kNe5ANepCZax4vX8+K19PVsyrAoPKWbjhei5YU8aw0V41bX9jxVHmmr1HpE4ovM59yZ/ZAX9oAXpjHS8WL0vBgtfT2FHAmN6CrV+J9f1bNq4gzM'
        b'rMJw3Obcnq3Kxm3Hl3QsaS/uLB4FNq7TRoLDcJdTe5Yqa9QaePgez+7IHgVU8HTKkJL+iE0FZ1CPAOWRST2my1G6HPEL7PI/kaXx1/nFqtIMXr7qjM6to4DtMc3A91Mv'
        b'OG2jYWn5Ynzp+WKNQsdPZD7p6GuEGfKQH/OAH0N6p+r5U7X8qbgy4uWN5alwn+Uoy8jNvtV41BL4BrbajJFzFBjbTaMLzNigkMvW3dYamS5oij5ois7RvzVNJVYbGVzc'
        b'RgEH81pB/+ly0gR0eXV5EbJyVIWdlup5Oq7QgPdso7IxuAbh7ThNM3B5dFexlhuNLz03esBRx53KfNJxo58YHFxUZm1J2oAErQO5RkKShxyHKu556UPysWw6t2WrXXSO'
        b'Aq2jgMi2oK1YGzRN60QuLJdq487Eh+7CB+7Crpk6d7HeXUwWLaIMYWlDZffj79XowwrHcCvUcUNGTYGnj2qmwcP7aeGrSn++4E3V0peBFlNaUpmh6rmq3Kd/xqcY9bBx'
        b's8fcpknKB+4exwM7AtV+6g2nw3RukXq3yIducQ/c4nRuCXq3hFYTg4PT4bj9cVpeqMZE5xCnd4h7BALsYgye3upZ7VWtswyes3Dh4XV8YQcOCDQuOo94vUd860yDMGIU'
        b'+Dhh24GLdhuVkUqhLjH4BZ/LPJnZpdDINeU6v6l6v6kqM0OQsIvdlXHeusdaZWVwD+qKeOAeonUPMXj5dRl3bFVtHQkSXbbottCkDHjct9PFZ+qCsvRBWZi9QaKu0i5p'
        b'V2mPuWbeQGT/gofRaQ+i04ZK70foonP00Tm6oBy1ER7nHdAVcNJL7fVzE9FDtMEJWm9ykVGW3ZaaggHRfW9dQpYuKFsflE1GPYXXBcXpg+IwmJePSqaObt/YubFryQOv'
        b'BK1XgiEgRktfhrTMoXlD8+6nvJP+Rrp23sJf572Vdx//jrKpuCVEjQKXEjXCJRYB76XUyCSp/L0wSrNAJ0zSC5OwkLtmUUyJNXO6ar3BK3AUGHlkUYb4qQPlg7whiT4+'
        b'+36+Pj5PzVEXnrbsmq/jxxh8hV1rH/hGa32jDeLYAeP+xCFjvXiWOrXL+US2OtvgL9K4PPCP0/rHGaLiBpz7s4dc9FEZWnEmM+IJMYIzO5JUSSMhERpvzXSNb0+mITi6'
        b'S4jt2vSBGQMz+it0wcn64ORRI3aYJ9b3ME/G1LTnEbH1VZd3FKuKn9nK774bzeIQP8L4lAnP6y2HLSd6oZc9sf9X/KAlGE9ImeD6pEG4eJmvSyEgOFgYS09h/R8f8P8H'
        b'H/8fMYsAvdZJbAHFHC9PzUensjJCMjjAErZxALn3qq6Z9BCFEIB+QkF2dNBq7CEKyUcEL2Yklls9fZjC+W9/mLJLwPqmCqNnPjE8mU3YIeOXTE54pbNoN9RK+Dlz46PC'
        b'+TVSuhIZOgl00ocMOV8qkSuk1WSuygqZnEyxvKR6Nb+ktLRGUS3ny+QlckmVpFou469bWVG6kl8ilWCYWqlEhhslZZOmK5HxFTJFSSW/rIIWkhJphUQWyp9eKavhl1RW'
        b'8gvSZk/nl1dIKstk9DyS9ViiSvEsZEzlpKnoRCpmVGlN9VqJFI8ieb6K6orSmjIJxktaUb1C9gt7m/4Miw38lRg1kmBcXlNZWbMOQ5IJFKV465KEn59ChGlYJpEWSyXl'
        b'EqmkulSSMLYuP2i6ohzjvkImG+vbKHgO8kUYzI9ly3JrqiXLlvGDZkg2Klb8LDBhAdnms/Vm4JZKSYV8Y8nKyudHj/Hq2eCsmmp5TbWiqkoifX4sbl0ukU7ch4wg8vLB'
        b'y0sqS/AOimtqJdUJNDkxQHV5CSa8rKSyrGby+DFkqhhcUiWlFVVYFPBOCaFeNrRUISUU2vAMmyJ0eqVUUf3S0SQnLoEu8ZyK0pV4mAx/UlT9HNallTUyyTjaadVl/wtQ'
        b'Xl5Ts1pSNobzJHkpxPogl1TTe+CvkCzHs8n/395LdY38X9jK2hrpCmxfpKv/H92NTFFVXCqVlFXIZS/bSwHRG/4shVxWulJaUY63xQ9jrC6/prpyw390T2NGoKKa1lJi'
        b'KPhjW5NUv2xbdHrfL+xqhqSyRCanwf93bGpieJLw1J1N9EVP7V1tjUz+/ARjkiGRlUoragnIz1luwmtJxfKfwZh4LnnJuHAVYc+Fl6qs/BkJG1v0mThOXuvnRfP/mu5S'
        b'CfaiWOkS+NjK4JFz0GDp6uXMAi8bT2wR3nzxaskEVo0jhElQiQZlMknlL4HKsYP/GSKOzUNGvBzZFzxulqK6TFL9co85tiz2kS/x1ZMXxmN+aY4Vayf73VmE2+h0uVyG'
        b'LVU5DmJI98sAa6WYAdjmlbx83dlj3ZJqUa409Oewn7T2C3i/3P+PCcJzMcAk4J+NBxjYCrz0ywEzZkzP/XmxK66RVqyoqCYi9aINyRvrW04LJFZg/kyppKps3c/q+sSZ'
        b'/wWBZob/XxqTlSXY27zU5M2SLEeDWK1fYhP+A4gRNaD1jNi5SXjNxT2/rGzVJVWSZ9ZuLC7mB+Xi5pfKqUJaS8dFL0AUSqTrJNVlRC03rpOUrn4ZtExSW5IwMbDGE0yI'
        b'6l8Csai6ekkCf1716uqaddXPou6yieeAkrIy3LCuQr6SBOkVUhKlSqQVpfyKsl+K8BPwqbSkiphNjNPclc+9/jcZMGHsnJOAzwUv8wyTR0/KXrMGL2avFTDvGx2YwqZf'
        b'PQiPcQt41X4sMc2XTbJvAD+8sDwbVtkD5o2i85awNR/ug30sAKaAKXDvOnqwxscY4IO3bfhaBTsifANgEqH2LYPt5GUieBHuojO10NEghQ+gE2BOwXqhIBM1CXNdnLND'
        b'mScAQmPg7WXkBlXotsBS4Uc/XYDHly2Dg6gxLDNDBBvCJjxWjEDNxkLUGUg/z6yyR3efPXOEDS5GgHnoCI8I6OeZi9E5q7VoL525NTFtK7aYftrKgiqLbHg4Kzt3UmJW'
        b'rZPCHfe6wpOobxZqQY30g2ERC5iiGyzYkIAO0plvUOkFj5OpM0jGmwZty4XNqCUsHTWzgZc9B6ngBVhH77wGXfQbH4gHwd4akjRYTzL1/IRGieh0sCKATHgbXgD0uFVG'
        b'zMg8Jq8uN4cCAjhoBDtQX5HCGw9dCA+ZTJzx7CsEz7AMPNBvmVFyhAc9Cp4Dc19BvcJQ1IznCs3MQfUhAmPgjo5w4Cl0Gu6jH93CQ9khzBC0fW1eRg5qIINcnDjh6OJi'
        b'OtERDsCdIWOMWxP2HOOWwtu0lNSgA/C2OJID0L5YALGsZVnQ0yfN3TyBR7th+ziTUA+spxMUK1zjxJFGoCqXJLmthO0pTP5eG7wFT8LBApKBQNIPUl0ZdJtR61K0DR17'
        b'gas+8AzN1gRUN40L9z7PVntqLF8gSy4Swyu1xoCCdbHZAF5CN+FBJplwZ+lm3EVeooO9JG1wtbMnLQuesN4T1cPDz8sCF90SGDM3au7AXahFLK5lA2oW3JGF5Z8Pm+gH'
        b'/s7oCEssRhojQKFm1DGHJITfRY00LiboFjwtFksxFGzYnAfg5Rx0g1Gk42unY6grBKoVNRcCeA3MYxKj7sAOeEIspkAtagPwJFidm0oTcmlavlhsBHzCADwFKu3QPlpN'
        b'9wqdQQhR09zyNU9SIxmdzsG62It6UauMAiANpKHzyUya/VI7gFkeF742seAkvwwI2LQipaA78PSGnOeTBw76FtEUd0eq+LmwPytUNCnxQGZK70QyB3aQW1jVm4wAh0PB'
        b'4+g8vIJ5QVP8Vsg41dDeZEI1F2eaniK8yhjR3NAlmma9SM0oXhPciY6Oiz/SwN7nNQ9dXIHnp5Mt2tA1uJchcBk6SQgMr0EmpzTKD50co7CdEaEvPGPOGKDG4tKJ2rWf'
        b'vCsxUWGV8BaD/U2ss3WEE2AGzQh0O5ZG0Qzu20zPsDX85zS5kc2wuQPuRvsJ2+BgMM03dEVEa2822hU/AYtwdG6Sjqck0UkmbFfYLBZzQAXsJ+mvK10i6Hef8XINaC9s'
        b'LMnKEOWGYpUOGn/e6g7rOPAMOlBG0ycxaTZqASRxUyDK4AAzExbci3aNvQe8dOyN1LUJcd8smj9m35V+LoSZsD1+jJtRqJW2xtlw13zUhdpeEBJ01JeWkmh4CbbmwFvC'
        b'TFGWKDiXvGVts4It2eRLE90Vk/LMVPHTVGI6jRhTjGSqumdz4P44eIfxI9cWz5o4KmZyujEX3aUpME+ayliIudgw7Z3oQ4JLjeAFtBMyaZLw6Aq0XUZNyrzeEEMpyMPf'
        b'nDjUPikxWQzVHEAnJiciJsd0zrIy1EhSY5c4jyfH1qAmRQjj8PbDVnSj+ClFYD0WU9SQTZ64Z5H9R8LDxhmwDfUwKaK9q7C07plKUnAm5N+gTg+awGl4sptom5hk8U7M'
        b'4YXX0W6spwSbykLYhRpJYjALtY7lBme7M1lUPSnoKlKvEQaJJmaJ9wtoE48N6g4uk8zegq7Nm5zLXgWZTHJ4F3VmLYC9FjgOKAAFFplYycit/PyIkEzUOWZJ0uE1Wjds'
        b'NpRYSI1JPtotgM5jLwOvhTESuxydCkeH0AGKfqUxEF6npc2abUaS7cPDjS959GTyx6StfTnW5gPosAmAt/wAbAHFccsZxe4vxarTR153ug13AtgFajBTB5lcvG7sOM6i'
        b'AzbWeMcHTQBHasqh5kZjxPLpOTmobVLqF9GNllzUXICUGbg9DNXPJhlg6Uz6V/5seCW8YE56SD5S5mBpxnqUNW82auYA2GNlmxftQHsI1IialwW5Pm8CsaG/TG/vbzEW'
        b'zEvTzssyjYvCwFzMMZLTZTTFOmvcTRnDPthczAqGJ9BtWv7QAGqFdzAJd74w70XURe/Vc5lLEep/QedSE2kbgvZhK39hzLufgscmuXe4C+6icfuzyBJgXILCCxvXxoX6'
        b'ABp0RSba6Ywuvzx4wKTuVhQRXwoPAtkkOiEl/bp+qCgIS1nwWGY4upNRQKisDClMJyJGi3A+TdKJ9Ly7yQ6b20bYTKeC77XnMMGocdLWYlMcX9KCWof3dGZMUhdLJwsq'
        b'OluBRZJ2x+fhDT7si6K9fCM6kI89i1DOJHGqsf2+QfooQLkLsWu5BE9yFWLcxSOvjB2AWAr2YQFtm5TceMkI3uLDK8vnyJfDq9EUprjxArQrgpb1BNi9fmzClXCQzDgn'
        b'kMnY24FuoBPjeKhsCBqoHe0XcGi4JZi+4pg1xPnfRQOZGC4rgHHxbfCgpzjKGJjiGA4HUxJ0I5qxVs3wCDoujlqLl8IB1NlkstOx7NSqUBz59kUhDcDz7YEd2KVdqd40'
        b'9iAJbQtDZ3FvBOkcqJ6JoxtUJ1ekATpn+WIOVggswnsx71BLAdJYwd6oiNnjGoBj/6uz54gK5zzPMdQIj5ujDnhzA6OuanhrDfZTOJDFB45XwCvoODpHE6IS9ZHWGNjL'
        b'wmH34BpngLrRDnSWtgjL4KUpYdgmGwGwBWzBqO+m7WeKYqOMfmN/ThBJGSK2vggpZ2Jz8AyBIpEJPAj3iBXk/WF0Zh3XIjcHNYsKq8Rjcojqi9Iz56XPZbYEz2PNzhGF'
        b'5mbnYYd7DmnM4W6H8PFYpAe2r0E7YNP4Nx7AS8400aNRTzYWi4sYpAVtB6gdYPnf7o7B6Fcvk3M5ps/rpx+ORWmzcAVb9Ksx3BcUdCOTGg9b/LF76VuHrlnB49NJuvF1'
        b'Kso+gWHZEXhrrYykegLPsWRPdGk+/fZOBecfr3Nki/D5TdDxzkWXN6t5aZpbK9Z6/qC5vXTKlnstOV9ylb9BFItKMVX9XWgf6Hckq2G+bQWnb2R+YawJpy6tsd9+RvpK'
        b'G9mrh2tN19nGWt941WaUWnxjzYmza8vX3VwXsObkl6ve/PCbr7ovdX/796te8zcFLN9w3PcfH3K/vNP+X6UNVAFvK2vgyrD4/Z4/f/lTT+Wrw7IH1XleZm2251PnT/+H'
        b'WYXXmnt/c7xQWTGr8/evyDfdX7E9rqnoUP+iQZnn71OP8ebf3H3JY4tysHBamOHm4Sn3z2W+kX9JrpY3j35i9GsU/XhLvrT2D3s8V62NOxBy5eue9Gnwc5b7j19F1G6a'
        b'96tba0dOKMJ6v8p0+cv3ix4t6BlJOt3m8EbC3NO33oFn5RZvF+lEf1UaLMvcu6r3Fc3Okv+U4fzgQ1F/+LXjwx55mru+a1m9K2/e3vbTw+2bRXt6ky29vlp25a8nPBf9'
        b'riJ5qnD3zVyfwmTfxvc27zl/LO2/VJ5P5D6PPpfde9tS02f2bem9tyt6j+QF3UqPb5+dmbogPejwviuGc/INT/48y/LQts2vl8Q/ak3pM6T8bkraB+fMLtku9l+/R51X'
        b'2zzC5nj5zfef7/vE9tU+zkOz6nu1Lb8qXj+w4sd7B+uORdUtTT0z2PlnhcMl69xl7t+t+uJGHC/+8OORuTyvLmFS1yfV8b7HH3S88Xr69+0fJD1o8ZX2aKd+/dl7rZ7m'
        b'mqRPMkSHSxcsePt7quUr8e6/Lzz0169OX9wfsqL/0Dc/nA9ndTc8+WLJquiykd7+b8uie9faLKwJ/ePq2zeWzv218d3wm86X5ubcmHskekHEF2/vfLet/olz5arrQzvf'
        b'23Xl/OtC6d8Gt8lmJvWmm3wTEL3nwtXTfWU3y6bnPX7rmOH3r16fv7sl8NGPs8x70hvSnrjP9L/7MOnEarOtidWBcz/jXtgQX/24Y+byNZbnC0ZP91t79AXf+V36kYOf'
        b'LXP5ZueAi0SqWPrndRZB383d833/MeGAtm/2T+0Xp62rXPH1sb8kLjIU/FB4bbnw1WL5b//4t3e6/2h/7J2esI8iXr/U/pm6znULNeVbl7/8/v5vDmzPCjqTlpozmxfg'
        b'E3a4+E8xTaZOGa6XbRuK7P569sS7212+PruIV9BREOYfazhh9m7LmgO/bXtvmeeGaxHGiarX3nuzv0PNG/TxqFjidGNDbdufho8W+9X8xfHOK0uju0vY8T8ufvuh/O3f'
        b'yr3/+Oc9bxsat0oWetc4Ft53HIyXGrt/BN+t/uCdw3O/Z/3lUIKL4ujF9zfOf+Xymjca3lqkzudWnTq1a6vviu/iOvmXdJ/DpNknpbz6ro43FdZNuVvf+qjo9fsh1Dnr'
        b'+bGv9LXMfr15+7Gqaz+c73jc3vPmr9/6YGjJ1u8lgT2rOCsKDSu+TnnzQkjn79coohtlJeV/SJii+WjFw+/+1J+59NhrpyP/sfVWoMbcfTT3rPnUOPeipX8M/vTj3wz+'
        b'M3F+4CsGRYLXSLVAtimzNv41bSK6a/Ipf0rsX5BbaVGPcMdHLbmzPjmaEfjQ528f34gd9v36nc9Tr9/t/ft3W22/9fz67vdeP1i/vje5UWD92AvbmtqVW5hE0IVQSbI2'
        b'ifHFoakLvMZJh+eXPObSFvyqLdwOO4TBYxmaZgtY8MzSZDrDUohOmAlDM0Jysycno1rPoGFhF3/d00xTY9iJ45S9LJG3K93JRS2FsBuHtBOTTTfkO9PJndNgnxyPP0Kn'
        b'w05KhfWH5+jsTXQKdZZOSjiFt1azAZ1x+orRY2JlFTMCPNnC3Bwcwu7F8Rm8wVqHbiQzmO3C0cZ1HA82hIkAMJag3nWsUDSQSu9qJRp0zZyZhZF6uimbcDaOmgbpaRe5'
        b'o3PPArsMNxzWoZup9LTY8+EAajyX1TgjhOSyhsCT9Bds4M7zc1BTlfC579dA19FNekubzGZjX9qUlQFvz4EXa8e/0iaRw0ZH4TmB9/9oQuq/nLBDIswXbj3zJ2TwbHv+'
        b'e0Oq5PFR4RsnfqBTVk3NmZTVZabAkXs4aX+SzsFP7+CnTDU4uShnGhy5yjSDq4cy0+Dsopxl4PJGwUaW1RzqEfOnlWNw8GhNUJWp03QOwXqH4FFA2YUa3ANViV0cnbtI'
        b'7y5qTTW4uB/etH/Tvs1tm/F4N2/19HZhqwluJYM9DI48g4MLWVktZr5Z5xGQsezmUIaA4HOrTq7SOGhKdAFx+oC4fXmt01sVKsmIC0/N2b+5dbPBnT8KWK4RBl6olhfa'
        b'pdAs1Yel6nhpel6alpdm4Pkcz+nI6fLX8cL1dG7fSFiUQSAyBIUYAoV4dkNIuEEUYQiNJKUwzBAcaggJHXW18nYbBbhQGbUbjfKAm5far8ND5WEQRaqMVKt13GB8GVw9'
        b'x1rdPdX+qkRVomHGrNeFUHi/VDdjjn7GHB0vSZWmDtbxRBitBbqwJHzh5XGbQMcLwReZQaR1DcMXyaI0Uq1st2m3wa1an0ytK7lGAiLUqzX+A6wB9gC7P3hAMjR9cOV9'
        b'35s1uoBcfUAuyeAr0bC6ynosDH6hapIYmK9Zoyno2ajzS9D7JYyacMhGOGQjo+aA563O1bpH4ssQFY/RCNXxIvBFMlurtR5R+DJEJ+D2MB0vEl/PMl5jpqjStD64TYyv'
        b'Z81PB383Rot2j1GWM9/NwBN0RY2ycW2E56depV6lcdKsGbDTyPrddAGJ+oDEUSPcN2oMPHzVqaMmpG4KPPzVZaNmpG4OPAK7OKMWpG4NPILxXDakbgs8hF2po3akbg88'
        b'grocRx1I3RF4iLrKRp1I3ZmZx4XUucwYV1J3Y+Z0J3Ue8AhQy0c9SN2TwcGL1PnAI7RLPupN6j7MGF9S92Pq/qQeAPwDDYECQ3DIqJB8BuOFijMaSghs1xnHJKgykj8K'
        b'jFwDDMLorgQ67a9kIKV/1VD0fbv7kfcd703RxeTqhHl6YR6TUGzwC1ClqdJGhGEa055p423+qjRDSITGvyd7IOVBSJKKo1qo4wbRedNdmfrAWG3g1IHp2sAZQ3Y6zxQV'
        b'G5PVO0At6UpRV+j54ZosLT9JZWTw8lMXdG586BXxwCtC5yXWe4mJ1gSP+Ph3UScCVSkkf7tUXaYuO22BR3t6qdhkgZTOVQ89wx94hus8I/WekVhXXYPxPsgeUh7EzNLG'
        b'zDKMTzDKBniN/zPAeA5o2oBvf+YQpQuaoQ+a0W6lMlYbGQRRXe6awoF5OkGKXpCCNzq/3doQKtZM15RoUnpW4YYlOq5wJGbKeALlw5iMBzEZ9/10MXn6mLxHbMo1SuWI'
        b'9dM1uCvFwONrvSOIGHM9VNV6rughN+oBN0ozV8dN0HMTtNwEXJmgw/5djg/cRVp3EabVQ6+wB15hGhOdV5zeK24U2HvMp0YEoZfdu901BTpBvF4QrzY2+Aaoxeq1J6ac'
        b'nqLxfuAr1vqKDcEJ2uAEvOvEXMowuwgjlDifpKoKF5BUVVziLn9cGoPQiK4CjfMA1e96fmnPUkN4tKZGHz5zaKM+fI4hNL5r9UDAkN2gYGiuLjRTH5qJ9TjWB+txrI/a'
        b'SF2p44tHLf/FGXShqfpQrGOcOAIfR+CrdPwoLT8KT4FlJyAGoxSXQxnyCjG2cUV0Yu18OrF2Pp1YO59gizU+VM+L0PjoedGaSj0v5SEv8wEv8360jpev5+Vr6YvQMlTr'
        b'Go6vEZ7n8YyODG1A8hC2vOl6XrqKGvEPUhd02V126XbR2J1363E7UXy62BAkuGzSbaKhzpv3mBtoY+d9PfBK4IB3bzBt7hQ3q3UBOfqAnBdNWVrHNNU08oZBmlrEvGEw'
        b'EhmLP2DLGqblhdFmdKrWlVwjXB7BLkjrGowv/GnEM1TrGYr3F55gmDpjaJY2MRtvPzyHbN8rl2wfl0R6c6kR74DWzH2ZI66eo0BAXBL2ZFv3b1XLdC5CvYsQq5GTt8bx'
        b'uscVjwGFLiJNH5FGN913fMfjDQ9t0UJdxiJ9xiK67RMu3+DiQTLW8TQ0BtqwmfdddGGzdZ75es98LTff4BasxZcwW+eWo3fL0TrmkCz4RVqnIHwZHAO0jgFqRddSfWCi'
        b'znGq3nGq1nGqwZH5ri9/nWOQ3jFI6xiERb81zeDtT+Ptzld76t3Df3nVsUEae717FHHW3uq5D1wEOhcBeRckqSOpS6xzD9O7h40CR9c4Ter1zCuZA7LevP68oZIHUbO0'
        b'UbMMfkF0ZrrsRN7pvId+Ux74TRlIHfLV+c3U+8186Jf9wC/7foHOL1/vl4/NmX+wel5XRFfp+DsWA946/0S9f+IosPZgCjU1yuF4Z1OGyFgs4kEDaUPeQyWv+g9md/mr'
        b'U9WpTz4MjMAkxQMmlobg2C6RNi4dX4agpKFAXVAG5mp8FuEnLokiZtOKmE0rIi7ZBOzJkyfY/0TEaEoGKE1pvzmjPv5D1BBriPVUhYzYAqxCuFAb4dF+QV0xJ6eppxmm'
        b'pahTtYIEnd8Urd8Ug7+gq/DkUvVS7DHVqV2uJ/KePPIgW+ITACu9L9E2j3hDTJyao16C9Zi8jOGhpeVVzwvTROl4scwnHX0ZXLGRf+Aq1LoKyXsVi/Xc4IfciAfcCI2f'
        b'jhur58ZqubG4MvJyro6Qb3xjWfkbbH20tj7q6C5PvW+czjZebxuvtY032DofttpvpZLobP30tn5aW78RB1dlDp0GbrBymO/NMXj7LGCbMDnmtsMc8pz9/2du+UvDV3LX'
        b'e9nLolXpFPDs6+ToKPVNMv4kGEs2LzCmKHuSNf7vLP5tCejk+3iOm0WDq9bT2exJiQTjCedfkxtlh4GEfAszWMgqoxayy1j09yKzh23pHAY6v1uaJpXWSL/3YrIaaGpI'
        b'x9K1JWX8kmq+hPSH5go4w6bFxSQNpLh42Ly4mPmaZFy3LC5eoyipHOsxKS4uqyktLqb5ybw9QBN7GiH2C8sOY2Rl5Ay27enviGWEdvyi4elHTrB1FtphYY2uyy3M8Bkx'
        b'VyS1zR07T4Wh48ZG6BDqEVAzK658+RVHtgfPKt/qv3nfr7NQMvdXKyIzOuaujr2gOL9oyRd3/vrDQqeaY4nmLdtMPfvVjoPp/APrHR99+t7SL7w+d7lwTbCKfzej/KNN'
        b'H8eK3zGrm9Lgy3tPx/tx99SOgAKVu6zZfkVPds3vqbuOP62XLV2w+8G3t+990fZp1oYZb/xWbf9FcWixhSju7wcPCP/xVvi3NZLbXXYpaf98P+hveYqcX2V+pOjnd28I'
        b'3+lq80HPhU9ci9pDPttS9/mOws8sTY5+E7/u06YPpa6HIto1HLdKVLAmJCWyUqA0nD23JDzK+/t7dimdquT9hibHXqOL96KGlX/5E3+tT8qXM2J7TW7fm1ZW/yOXb71c'
        b'qULhazin7kU0OQSGZ3TCqPLwxvi3SqnG+TCyUNMQ3VPKPnJZF/uVwABj1moabxe957A/K838izv137dk5ZwNcfih3+TDnAcZUQOi6lNnBr0460Q//hjzhumNk78r+PW5'
        b'N8vb91cId5zTDVa1pRdc+mjpyF+PfffrDXtSjnzSpS7Ku5n693nOd28lWq99I/sHdmjMxmGOjYDzmGixJ7qxADVmz7GlcBQA0F4zdJW+K7ApWmKRBQezn//GV1PYgc4/'
        b'Jo8G4V60M8giGO4MJO911qOmp+O8YB8HXabgafrOB6pbnCaDF9NzRU+fns5GbXaolaSYnKsaf/nT9BeL/+aXP5Ppn20v/DBnZ6xclTUlZcXFG5/W6FMzeRf/CfODjVII'
        b'sHIa5ZiYuRhs7JWy1sj6dU3rVN4NryhfUclUMnWkuuQ0855TPnklS+OHf6UD3v2Kgfz+9b2h/aFDqUOp9+1fTb+X/iAyWxuZ/SHXTRWpKumMbjfrNFNn6rihGhcdN06b'
        b'mKtzydXOmaudV6ifU/TApUjrUvShM19tv6+6rRobcRyHc3HMZg7sHVuntzkpZyhnPBk1ocwyKIO9V6vojKVWNFPHn6Xnz9LZp+vt07WW6bT/MzYLGgW/WNhyzEgM+UuF'
        b'pSnf3GBp0+o8yiY1V56qnKkFCLpimJo4ZsCYqSWnDBXStREawojUaAi6RkPQNRqCrtEQpIZDUitbDGPC1N08MNRYPTAYw43Vo2Ix5Fh9OpVKYWj6kykDbcbUaeixekjk'
        b'gPFQocHORVXeFfOy6qgNGQjGC60pDx8z7bm4j7lGLYx9cBcutKaeo7YzWWbY5f+bytkcYG5rMLNVurTKVNGtq7VmPjozHz2mOyuTY4aD4/+u8hEbmPvidchf2ybnUQ7d'
        b'tdAUfxplUWbkmPdCcXTDI/LnMSnG4SaPpSONhulJMxwAdHCbIWIzkYbjMAs7qX9fnPFStXd8SezxLP5IJy7xqbITLyi7OR58CCjKlgQM/5Hi3xqUnDZLADetp5uyKxxm'
        b'WrFlO3FTeVZQVfNU6x3J3NS7SaaG7Qe52ikbdjfHGBasmnUFfbvnUMOerIaI9HTVqoANYV9fStz06IuLvq/vXbVRd2Dj2ebEys9RatPW4JUXblfH5xYeyj70VuPdloXv'
        b'TzV/6+7f47jcHaYRc1bpvmz1ft2zgW3OKwlaA7/riF+9n39xcdDtzSBrg0fB394XmDBuopE8dyX/1YANbM/Lo5M7TIAFvMJCXbmwiRnTjgbRyVQ4mJUnQr2oPi8vT8QC'
        b'dmiQDU/EjH3VAOzZNBM2kqQXksABm2GLCbC2Z6N+eNYzZg791QqR6GTO2FcrGHNgvzfL1BLdYL7QoQDty8qQOT/7HwwsBCzUmoJ6mO9tPr4gWJaBWqH6uf/iAB52oGdG'
        b'DVCN1MJMoyR0ClBZAKnyUbvA9+c93P/4PeSXKofvuE980SO+1DtWVFfIGe/I1Gjv+D4Y845YZ9yAkcO2XPJrsHJ8aOX5wMrz6HqdVZDeKmjbTAPHvC57R7bWzvtMnI4T'
        b'oueEaDkhBo6XdvJl4FhtyyC/o8YzTYywBfkfKmdbA0vHbXkTXr/lD7MrJdXDHPLq5bCRXFFbKRnmkBxjfGSqKMUleX1umC2TS4eNlm+QS2TDHPIGxjC7olo+bER/Xfaw'
        b'kbSkegWGrqiuVciH2aUrpcPsGmnZsHF5RaVcgj9UldQOszdW1A4blchKKyqG2Ssl6/EQPL15hayiWiYn71wNG9cqlldWlA6blJSWSmrlsmFLesFIJsd72Io5UlXIauJi'
        b'wiOGLWQrK8rlxfQxYthKUV26sqQCHy2KJetLh82Ki2X4qFGLDw7GimqFTFL2zCTL+MR6/uIPn89Y0vzxghggWRT1NGL6mR8sLDYUJWUT6/e/v/y3mW/iKV+1NJvuA171'
        b'sZ4ezv7edPw/Sxi2LS4eq4+5q+/dyif/9zn86ho5n/RJynIFplLy4jY5DJZUVmI/SzMomTSZYxmSymUkC3/YuLKmtKQSi88cRbW8okpCHwmla8ZF/tnp8XvTROa4OU26'
        b'DjAnXNlmXIyyKYoaZXEoDg4McWEJLKy2mYxy5plQjqNgQllrDczsHpq6PzB1V2XqTAP1poGjgEVFa0OmDQUMBbwadC9IG5KJL4OprcHcWRmidRHrzKP05lFaTpQB2GqB'
        b'bStXB9z0wE07ftHo/X/p+Lvi'
    ))))
