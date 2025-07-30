
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
        b'eJzFfAlcVEe29729sTT7vjTQ7DQNzdKAiKAgi+yLbK4sQrMEaKAXdyNxV0RBXBpRafdGRRtwAY2KVZnESZyETsfQkMSYZJLMmy0YzWSbSb6qe0HFZN438/3me69/WlRX'
        b'nao6deqcU6du/W9/Rjz3YU79fbwaJQeIfEJGhBAyMp90IWSMZcyFJsQvPvmMSJLOBUyVlHNRKXMZ24uInCqZg/5XoraJjGUcLyKfNd1CQi4z8iKWPe2BT1SzTaoFnB8k'
        b'pvnFaSkF/IbGSmW9hN9YxVfUSPi5axQ1jVJ+Sq1UIamo4TeVV9SVV0tEpqYFNbXyadpKSVWtVCLnVymlFYraRqmcr2hEpDK5hD/Vp0QuR83kItMKt+fm4Y7+c/HU30VJ'
        b'CVFCljBKmCWsEnYJp8SoxLjEpMS0hFtiVmJeYlFiWWJVYl1iU2JbYldiX+JQ4ljiVOJc4lLiWsIrcTtAFPIKHQttCo0LjQqdCs0LWYWWhaaFtoVmhSaF9oVEIbPQqtCu'
        b'kF1oUehc6FDILXQp5BQyCslC10K3QusIdyzsl4yl7gW8ZwKUergThe7Pvhd6PMvziQT3BA8fwvNXSquIOKYHUUUioTKyK55fNmv03xZPl0WtdDUhMMquN0b5cysZBMvs'
        b'AMqV1R/OSSOU/igLLoHrYCtshTtzMvPgDtiWI4Cb5sC2tMLcYA7hn8yCt+Et0C0glS6YelhiAU7mydOy4B64OwvuJgnTNAbQLg6uIJ9jwWaahU0omWtdgthAsiGQvNhI'
        b'IkZIfiZIblwkN3MkK0skNWskVdsImykJkQXPqZiUgSREPichxgxZkAkMSkK/KP13JJRJSyhVbGQWynRCPZSZPZrNJ6jCrCLGwmYC58rMXBkL6EIVz9ihAA1ElJUFGeau'
        b'pQv7mthVSUwrgogvMxu1TiF6iXpTVJxe5MR6YkPET9quIb0EV8NCi2OJemxvSeldpNaI4Ic6S2d7ErXFH9PFj72+ttxvSQZMEhuDFGX/CL9DTBDKECz9K+AsWqJW2BqS'
        b'FxAAd80Be0NSg+Eu0FsQkJ4F9waJ0oLTs0hCamkSx4XDM5aENT3nSrwkTGpJ8HIQEcynQmf+B4Ve9aLQjX4hdC4t9IFES4JHEE6hDu7r8mRiQhmKCuGAO2xBM90tzIC7'
        b'4c7MvNS0oLRCIjwj3x7sL4B7wQnQClAvbCPYAwfAbqUDapSHBHRbDK6hEUAvKj9LNMOzKUo73N+J4EYxuIxrji6DrxJ1cnCVqnCA5+BOcTiW7kFwsoComAuvKbH+lq1a'
        b'BLahsTvZBCEiRAvhWYrbzipTArUzDnX42uxtIwt64W802RI+6G+ohUn2huzZRG3JkIgh34hKvs/jDVYce9MKaF6zAvVv3iU4d3YXfW5mtnO9mZku11rtlG88KHJlMjOz'
        b'AiuM5aGDhVzm5uCTnIIsL1vmZkZiKHe+D9sLHH7DyjSi1DFg31u8ew6v3WshW84AThhrcLCl5m9lKaG/c7p3B6gtVxWK5Ma2A8JCp+ilxLYqa2/ThQLGEw/ERTaayVEu'
        b'kqQgSxkcCHeFMAh7sB3ehLtZxvD64ifYtM1BvxIJfBfcC3czCXDVijWbBP1QBS4KWBOMAIHMHBE9S+R4GfktLS0TDrFVssa1Eim/ivbeIvmq2irF3AlTyjWXVpYrJDJL'
        b'RMzArZpQ8l0L8SiJJKxs2yNb16ryWjd+6MAf9YwZKtR5ztc7JI5aJRocXFWVHfVjDkK1YsxBrFHsWGCwc1VJOnJ2JBvsHA+ldqSqJOr56jxVrcZe06y11rhoC4fChvK0'
        b'S0bd4vV2CTuSx235anu9rf+omf9jrH4yrH8CzgR7ZXm9UjJhVFoqU0pLSye4paUV9ZJyqbIJlbwwRQ5WAz6epMwCF1pOJ964NgIvbwvxbSJJkrafWDi21rVwJxls0m6c'
        b'a9M6+xOW5ZYsg7HluLHtd4/YBNtq+tsPckqNON7ESa6IWcH4NRutwjbKwFsVZaXkc1bKmOEame4zbLCQOcMeGQlMykp/UfrPXeNTFp5aKSebNqADXHATdpIV4AZBBBPB'
        b'oAvsUmJKqIE3M2EnE15aSqCQIgS0plLla+fDTmQ88Pwcyn6QuV6utQz5K0OOQ4Y/FZ2gzcLutbst5CbnzV2ZXfw/LztjlZLGMdes9hLm7pm9Jc3R6201671G0/uXwEiX'
        b'BWGSz2nv+FBAUurq6OkkTA+GO9Iys9kEFx5tAv0MeBScBi0C5ovriGOf6UWc4NJqWVXfWK6QOU7rZRCtl5MFJGHvciirI0vtrZbr7YQ7kh9Y2hmckO51cdvZ47YuqsjO'
        b'uaNmnjKrZzolw/vJBLtSsqJWIcOuQ2b7K3pEKRKtR47TiXBaj35AepSP9Mjl39Wj/Rwf4hQ3hEm5ofu5NmTEku8IInekwaCAodTCgQ54s1muiKq0D2URjBUEPLO6gaJ2'
        b'zbcno1dOMInQkYZFTd8kUC40Ep6Ew4gabSpbQ0mCISFgb8gSil4X6kDGLtzFIppGGpz8f46j6MEWcNAL0YNL8NVQJsGoJuD5eEuKvtXeiYwvQtpCjGxQrcwpoOiRTpxO'
        b'lCtmmeVibqQE8r43wWWK/k+RLmSSdDWLiB/ZsKjqZ3ulPe7/DLzii+hJqA5lEIxG1H3dIoq8PcONTGU8IQk+6n5RHVeJBWpjBA/L4eXINKDC3IPNBBxshrupBmsE7mSm'
        b'1+85RBnqf02LF8XPyjWgBzfwloSyEf0WAl6WgV0U/Y6FfDLXj80krNAA1vdCKa3mLE6QyyKTQ3HviJkLcGcjRXzX3osseGkfC4l+g4p/tZbiJiUKtsFBZVgV2IVni/Yr'
        b'OAhbvagGrwl9yUVLktGeMbLBKZ+Yq3TC0umOga/iFqCFni84iBhi2lEtLNb6kcuilmP5bzAQb9VQq+tZBAbkcvFaSI2wkYAXX/ajqB+nB5BlUX7IjEfkTibbsymG6lAw'
        b'R3EEzlbi1QKHCThU50I12JkgJCvT3VHMcEe+qLJ6GSWeVHBmCaaHZ+NDjRB9NwGHM6QU/ZysYLLGj8dEyyVflPJDOjWBEriZAQflZuAavGCK+IdXyAjYCzVUC9OmELJe'
        b'hDiKvyN3yn1lDbXA6+BlR64sqklGSegMAa/Vwn6KfEgYSjbNL8MLLHcilhRQAwD1MtDDhf2R4Ay4jJugEJQJruZQLSLEYlJhcxZ5OTRAnGkDtWLgunUj1zTc1BovGTxI'
        b'mmSkUbJYCy/CFi68GgYv86iOtpIk6HCgR9kP9tvJ4eAqcAjstMDzOE4KX0YOD1fmgh25chNzuAVchVrc520yCmwH+6lewa55UMVtVspQ5HAV+RbYT/ougq20LncXzJJz'
        b'ZfBKlAI3U5HucEBBifkl2O8kV8BrZeA6F1e1kUJ4wZ02sPMrkEAtzKWgDQmUySbj4DZwmJpZDVrLW6iqPtyCJJgmZHxEAaUT7lXgFVTsYNKMpzVEiuC5RVRfzfDcUq55'
        b'EzgSDnazCKY3GQ+2gRtUGwW4KkWKPbcEm0ETAfuAVk5NyAncAluQgbuDlggOgeI72At2wRO0mHrhhUakfShoOEeZDzK3gflgO63L58DuFDnsh4NsqLLEMrxIRgTCIbry'
        b'1BoXObyKzOEySdWdI1F0BnYLaNex0ymCXC36loFMVe4UtHIeVfg6I4pcn/4WiyhDCro0bgVVeNYxmmwpyWAjI5U7pWnpwhDLGHJLtg2HsLojV2W+k0EVinmx5A7OPWyh'
        b'8kVJKpIq9BPOJXe/fJND5KI+ldYFVGGceQLZvnIbNk25wej1hVShvcN8cn8Vh0WEIsrFN2mFy9+QRKo4Yg4ySblTw/tWVOE/ZCnkkSK0kTQhLVz3twqqMHJJGqlO+RJt'
        b'GCN1Ku/CQKpw7fosUuOwFZtQncHF0YEqTBfmkBdEhxjISuoWzX6ZRRUu8MwlteEqFrKFOsOCJ7Oowq68heTllI+xutctKrm/klpI34Vwm5xrah2HdcKMjIfnYT+9DwwV'
        b'NXJlFijK3WyOFMmajFvvTlXMD56P1uHaKq8ctFFibRZuWEct0kqwH7YgK5DDa8grXcaKuZ/04jUKaJ5S8t4gj2w8wEDzXOUk2SyhCrWSu6TauwY7/cZFYQ8YVOFnlW+R'
        b'p+ruom34TuOiVcW5VGGd4h6pkS9H3gBRrrtvOuO0YjIdhuB4ca7J1AESn1eeHR6JCJOnJxfOf/DksuXFmMiKeDEmmpet5GMtvgLPNoHWHHQW3gt3pmWJ4M4QRjQ8SDiU'
        b'sfzXgxPUPH8Tx0RRVYC3ETp1W9gm0AeGo/NNULctBSZlZZmqRQkEJW+fIjiUEZIB9+SksQljuIWxFqjXIFdK29rVQDAEBpGRqHLwOYZcTIALUFVFm9OBBnBOWBQTgIL7'
        b'HSEoIDKrZlqag5vUQQZeBqfQGX+QRdRvJGKIGNPVMswCxcdCZxY62RrqjOPLMsfLI+nC1SwjwoyILmLwy4KeLHQhqF7AodWl4lDCBe5D+X1E+UKe0psauTg4gzo07MVP'
        b'BDLQiTQN9PmC6wHIbyvYFvngMuX7OOA2HBBHoP0ftGL/SqwAQ4uVnriHo+hQ2y1Ex1nqgQI626axiI2g01bARN/OgDO09l6Be8AVdE6L8cQnNaICnlhFOcE8eNxbDAZY'
        b'8AA6gIEeoj7dmXa2h23RWVBMrIG30ZdjRDVS4s3UTDzB7mSxmAPOilDFceIlyWqquLB5tTiKcId7UamKqIQ3TJX4wRHykCcKM9LhbtAKN8PWbHp1LJqY0VALjlMt01e+'
        b'JI5i4SMWIu8iJGSs0hUVV4MeeDuDAXozUaMQ2CYkCe4S5AVNQL+AQcfUhwphhziKUW6J+SWq4D54cirYrpSIozjgKLyCtw3E/E1nOnzaV5IFW+M80FEui02w3El0Du4M'
        b'o+PwThdwTRxF2sMzqM0RoqZBocRPwVAnr4ADQjSBi2hlAuDObNDHIszimJamcCfl4uE1tM1tEoOryHun4C2WqIfX4XnqgQ9ar+FS2AqOgFuZ6fhgyIS3SNANt69T5uLO'
        b'zwSCTnlmWloWfnb09LAeIBIEZokEwQxTcFoC+lDrM2glTwUEgF4HoQC5lVNCO7DfwR6ecgRnGWjTtLMCasTG6frvfv755x2pbKyUK0ziy+qbTdIJOvBqjBCyYG92cCqL'
        b'YMWT4JzfOoEdJZMQ2A6OyyvhdnOZEjuwY6Q3PBk2tc2g3Wo/8m63CQu68iopKEcBDbVVH4FnwU44uBRcmWp5ixRasak+08vBBTk8VIla0W7PA6jANnoJOirgdjk8Ytms'
        b'NMUh5g2SDzalK51xj8NwE7wglzjCq6vgZTYVnHjCE3CAGq9hFdiMWLlCojpzkgoNwuFpD1pbT1izuB5wiwUX7EXOeQm5FJzIpua9ISVKDvZxFKarcHx0k+TlmNJsnC73'
        b'kqPhdqEaPNIrJF8Bu+iJHUyEaF75HIUMBY+o1S3SVQpoJkB7ATwthwPwsoeCQ5DIMODeGNBOa50KDIRy4ckcY3NTgmDOIlM3ONONenngMhxcAV9VNpthzg+T/nBfNMV5'
        b'oik4xGXBIQsz5LOZc8g0NN8rVI3tUiaa7q4GSxmKoJgW5Cx4Fh6meDeBGi4cBGeKLeEA3ou8yARj5KwoXexHVC1yAexupoYCV0l3Z3iJ6tBlvUwO1eC6Kb1a+0g+PFNC'
        b'B0kHueAilws2U1VMGzIURXAnqEkFgINwCHZyCHipgQgigtAhdgftbcHmItBqa2Zp2rySJFgoOgFt4CJig+rwANzqhPqErzydFwOcparmylB/gzWo5qlGgRsW1FjBWWCr'
        b'PA9se8ZgM71YznAoAk34YvQzRYsAx6gqHOp3yOFmu2eqFgSuCVi04A+7g1NIiJrS55ZyjoCqM1KgCGoAxaBbny4kOItiL2dqYwIHHUGruTO8hg43SuQpwHUSvJLpTrWc'
        b'L8oBrQ5Zq+BVM7ATWRPcQYKuglQBMzubYknErebCM3DPc8p4ErbRBnXBFdk7suW2Z2qHXNAArcRXAl+Ww67Zz3TVHewRWNAC3QSOFHPhuTpTEziAliiGXFAJu+k+98P2'
        b'KjnYDDZPSfQgMpqT4BQlUl4M2CNft/aZac+BvfRg50E7uMFVLjamltyUFNWiFcdDJYBNhVjYcIcZ3eoi6V+TSc28mYf80yA8Do8pzWS46jRS5L7FVIfiBXHy2I0W8CoV'
        b'nPeQPrAHbJ3iPbpODnvnwKtcExzSD5BRCniOtvizYABc4sLdmSish1dY1NqK5iCFpQyqf+kq7gbQ+tSe8kEXNRa3pgA/TdkJr5g0cwimPzkb3k6l9X+3zQouUtnjuApF'
        b'cAFkDHJgW2lBXQH9CnkW2pHamujDxUVSsALso7qEVy1M5KAvDV5tskRxOtxJ+jkkKvFjDaAFW5H4W5Er37sS7kdavgv0RaHY/QA8hI7jB4tJIrnAu4RlD09nU/sZmnoH'
        b'7DQiQEcIEUqECqBKmUMZTIsE0R+Ch8COF/rZj0rbUf8D6O9+NN41VNaO6LaDG3CvCTrjH4IacL7mJeTqh4HaBHTBq/R5EQ5zwDE5OKV4TrbIL9N+LM0tHEkp+3nJorPP'
        b'LbR54gl7QS2HC7ZUPZOhKdJ+LHY/i1Iu7BE9kyA8naVcgCokSOI3uLAtA+2DqVkiatMSwras9OCFcEdOfoAoKx22ZsK2NEFRKopDFoIu0Ae18LK8mJDbo0gg22ou2goH'
        b'qUE4ieASGFw41yKXQZC2xAawA/TS4datZmk+A5n8ecKb8AavIEXGSqSAp6RIK1/Ne86SBS5UoEBGgMOg1R12z7RW0Aa30V7gGNgDBuVWc55bW2PYh+RA7dA3wXBIhigY'
        b'7tsYmI7ndpFFWBYx65nL6O3/OjgOL+J9uY2OQYyhirE+Hjk4NWihhm9EsdWZDHB7PtyTGpSeE8whuBnI1EAnuE5xvhhx14U2PHj5mX3Onkc1XT3bUZielRGMx0VRpxhe'
        b'sAHHmEALb7JrM1YVkfJsFPObOq9tK1zcqI+3enDlKBzWX05bmr703U7vBUvf3bQutoX/yZ0tawcCGJ55vTzLu+cKPH9izCN8fF4m5n/qP/max6dds6reeNCmdyrIuLqq'
        b'+svudVV7//xOfejS8uXni6vvVW8ic0KXNQ8PdD0suxvnVLbk6/cmRo7+PePcG+Ov6U1+7v7k54jWP2yZb5HRvv9n0Ve37y+8lyZo/+Nk82x/SdTA66wq3V833fNOXbcz'
        b'rXaTsPYPjkadsRGsbxeGvbrtU/bSlzqMd1t+9bl1hel7Zs6nlgy9OTosCLobk3g5dOfVy57+Dc1f5u1jf298M/6J8oTj0R7Sbcz3jTsBn9cs9/uB0XfW5x+n0nXZC4/8'
        b'2akuS/KXcLnRlvNJiuzOtw8l9ewcPZ+0ccGTibn6tVUhp7/0/uSLVPcUSW7vgrfz3oxN+zl9WbHXEscdP2W9G5I/m0zP/Wjodu47uw8dTbpTWB7ZLq/8uOlKgsNbIVX+'
        b'u48djIncFRDk7rK9IO9u27Ej3V8W5P21560FN9/6yKZi8bIrvlVpn5aP5xCPO9NTtn7jfjJY0PH112Huy/LffVDhf+SjxG7zhoasl/Rz3otYH//9mwuTDt39m9o/eN5/'
        b'rTBOXrjq2CvHeB3+ZOnCdd0uj/+WVnb73pFYt/1piXkX7YLvpMjUorx/XP2ix+unNuvtxbsfyT5fsaDHwSeqCJomd1wZern40XK4yu3jNofGMEPswY//9Mad783/7tLU'
        b'ectUfn7xSOxrOVtCxW/6XYr97ck/6nIsXyrxff3kttRVu7lzyzk3tv3oltPtlWWv2naw8eSWrjQTGGL6VXXStjP3BrWmf/1xcceOVu+/2f1wpnn4znxhxMrS7HeuvXp3'
        b'81/Wg/V/5z+I+ubjgxdODNVuL/rCU39XfS19RehnDs23DmtTxy/85pORoh3qd37Ym/uBQ+35n4q74y72fRz/4dVjCVWvXnVa9n1pjCIoc9fvasI/P2qpkTifv1hQrfW+'
        b'wCwpa3I93G9/ovm1++Npmn8I5z5Y886XESlfknN+8qyy6Yv7MXhXhdviHQqfjzaesOrbkHdKKgIXD1+6LlyZeKtsj9R27NjvvYazt8hzXl76tUWP74MSwycOH3r2RhRu'
        b'mrMh90CYqbRgw+OPGlx2KDctva/s3fe3tM60/WcjNliAx46vPLn4+UX2+Vn3Xv6Ho3bPvcoklsCcevzt1rAKthYpg7JRuA33BqGjBTiP9gNwwPQJDx9Z0VnxkFCUFhQo'
        b'EKFquJPIXUc48VklruDSE+x4hfWxsBVqzKfve6jLngJ48gm1qx1cVi6EfeYiFNPvRH1zwB5GMNgE6abrwabkjKCAVGTzyJvgYfsK18yDx55gt7gYHo/LgK/Ep2UFZhkR'
        b'HBbDOITxBPshu3l1wtSgQNQfcsK74V4mAXY6285hwm4HOPQEP0EHnb6JGTnNzcFo/11JJmzkPaGc3z64Sy4MIkQCuCsInyMvMMTgqBFVtwAeWgpbLeDJrKA0uAdVRjAs'
        b'wPUcajwPeBJuRWfpfHyJmJGGzyVISJUM5GV3VlOzLIC9sEcYOD1JkzkMe290ZDtn9gSf++BgNTMDOUy0PQSnB6EjH4q1L9vAISbcngGuC5xfuGP4n03kmH/+C5+W6Q99'
        b'z2FD33MoZOVSeTmNl5BhHAd13fGQRV13PElCG5VvO8vg6KrK1DkKUM7OScUbtfMzePqqy487aqw1YWpeO6t9UYcFJkrteHnMMVjnGDzmGKJzDHnoG9iepHLqyDb4Baqc'
        b'O3MM9s6qgI6SMXuRzl6kkY/Zi3X24ofuXuqwrmp1uXqFqg6RW3csmCKf5BA8955ZXbPUEd1x7UkGF3dVc5d/e6LB1aMnpitGXdE9TxOmCR91FbUnfejpq2Ib+L7qFepm'
        b'tQmdRT1SWVe+Oqk7ziCOVrvreaEGNy91ZfdyQ2ik2lXPCza4e6sV3Q1a9pDdoLnBR6ApOJmllQwpBhsMPL7auStnjBeu44VrI9/nzZ5uGhKhdtHzgqa/isRq5+4c/K1e'
        b'7xaOmzl0ZY7xQnS8EC37fV7UFN0nojCt7/mXVEnT1LitMFTt0J2JvvUs71reU9pV+jAwRG3fnTFpQbh592R2ZU4SZGACaUhMfcQkA9PIJwTplk4+9PE/nqH11fnMUiUb'
        b'PLzVaT0bDXwf9eLjllqGni/WKnX82Pt88UO6bIwfpeNHaZVj/LhHaSTh5TeZSRJ8L7RsRR1mkwy2i007Z9KM8PZvt6TmfCQHCTsg6JJFr4VWrg+Yo7PzbU9Wsx84uhxT'
        b'auzPe6AJq4q6zNSFOiehITDksOXHzgEqD4MTjyot1TtFDtnpnOLuO0U+MifcgtBUkNaYdMwb9YvR28Y8DIofsRupveOhC8pDy+3Qkal2fNdOgHVD0FE6GjBXbz8XrbCa'
        b'0xU75irUuQo1KWOuYp2r2BCSPFJ5d/adRl1IkYpFjVWkcwqaNCbcvVQpBjfPp4m3KvWFZIIXN4GXnq5WF6iyn/6ZbvbIzZISBJ9wdevx7/JX+6jXHA/Ru4SPuUTrXKL1'
        b'LjHtRgZb+0PRHdGjPJHWaMw2+j3baIO7p3pBV0P7AoP7ApS4efQs6VqiMdK7zW5P+VAY1mWpYqvLDT6BZ9OPp2uUWoW2Su8TpzIZDxBq0s5bqMwNrgGaML1rkMHDR8Pp'
        b'3vgwIPgSt5erTRxyu2utm52uD8hQsw0BwZoKjUxjqi0cCu9fPBaZrItMHqm4G6aPzNIFZB1nGzz9NH4nPX6lMVU3Ghij94zBtWa9Ztr8oeC7nrqYDH1A5nH20yb6gGg1'
        b'e9zDSx3ZvVazXO8RM+EX9UFy+t3Ed1J/mzpauOTtnEkmGb2cfEyQ/iUkUkrPEvLhc3rwe2GEdvH7wnldGaqEjz38VasNs+OGqoZ5IxLd7My7ebrZOWqWuui4mWYRUkWD'
        b't1CzUu8daRDPGuL0x45wdOIF6iSNw8lMg2+w1vG+b7QhInrIoT9zxFEXkTYqTqcrkTYFxZNInXie6pTueQ+DwrSe2gRN+nhgJLLYhKH52lp9YPwjNjPEHRvZkRysGt7q'
        b'qmOllLG/xwt+kkwSQeFfL2Ait/bcFa3ZhNkMP/grl7T/itc1I6bxAM85WsqpUkkipplNTKECGCTp8g3x/3Cl28UREL3cCKaApI+Yx8At0J2RFgQ3gxtp6LiODvvd6NSl'
        b'nfHAHPNHPaPG8L655lMPzDHaivgl3irC/OmDc9Z/9sG5Mg2ddE1z8c4j55fPhOVRWL81TRJ+VsHsiFB+o4zKhItMTdMUfJlEoZRJcZv6WrkCk64ol9bxyysqGpVSBV+u'
        b'KFdIGiRShZy/qqa2ooZfLpOgNk0yiRwVSipNy+V8pVxZXs+vrKXWuFxWK5GL+An18kZ+eX09Pz85N4FfVSupr5RTbSWrkUJUoJaYpt6UAoXQNRWN0pUSGarB6EKltLai'
        b'sVKCxpfVSqvliNeEZyOs4degYTF8saqxvr5xFaLAhMoKNBVJjKlpMJpjpURWKpNUSWQSaYUkZqoffkCCsgqNXy2XT9WtFSDqX9IhGZWVZTdKJWVl/ID5krXK6hkNsIgw'
        b'e8/6nY9K6iW1irXlNfWYYkp+zwgyGqWKRqmyoUEiw/Uot0Iie54vOR7kGcGK8vpyxFFpY5NEGkNNHRFJq8qRMOTl9ZWNAlMceqCBGuhxkiQVtQ1oGRC3eILT1RVKGZ7Z'
        b'mmcjFcNTNTKl9CkFhgnFUClqq6yoQVVy9E3Z8DwXFfWNcsk0G8nSyv8FFlY0NtZJKqd4mLE+RUiHFBIpxRO/WrIC9aD4n+VN2qj4F1hb2SirRrYkq/sf4k6ubCitkEkq'
        b'axXyX+MtH+saf4FSIa+okdVWITb5IbRn4DdK69f8x3icMoRaKaXB2ED4U6xKpNNsUhCe/4bL+ZL6crmCavK/w+Tzu1jMU1f5vM97asNNjXIFbjS1QhJ5hay2CZP9M++C'
        b'5S+pXfEcN9grKsqnF7YYeUXUZX39c6v7i+Wf2edMVfiXZCSTIO+LFDWGjywN1S6Er1bUraA7mqbBNogmUFoneU6U04OhadTDV+VySf2L5Ark9P/J5KfaYopnjPzCa2co'
        b'pZUS6TMPPNU98rm/4uNnDoBoXmxXvXKm716AVwCeqlLIkYVWoU0LV08TN8mQsJB9l/96/7lT1RJpcLZM9DxnM8b4BU/P9oqpxXlhv5jRYMbeQdPXoiF+nThtfkL2zCUv'
        b'bZTVVtdK8dL+0r5ypupWUMqADICfIpM0VK6aYR//ggL9y4ZWU4684K+a+gLJCvgqMgXpf3xQrF6UzmL7njFmAar5peJKyxskz6x8KgbhB2Sj4qd6oZQ1UXviL6iKJLJV'
        b'EmklVuu1qyQVddMt5JKm8pjngxjU6LnoaIpqqVS6PIZfKK2TNq6SPotqKp+PocorK1HBqlpFDQ6CamU4mpDIaiv4tZU4UoppKpeVN2C3gMYrqHnhJQ2RacxUzBfDT/hV'
        b'TyYynYHCsCBeRGHk0/hxZ28Ghq2uXm9UFpQfYTcFbPDHd8gEf9eCssy8sAZCiZ8wzQHbcsEgAxxYhl9cmZPiQZFmJnIIFNlHWwWWma0IXUVfN/uCYV+MCoctsIXCG9Q7'
        b'UJAPoAY3ioWCdLhbmJ0pwo+yUuE+uFfIITw92C7rGgVmSgwE97cGR2FrSHpaMNgV8uwJ+RL4KhEG2zhC0AuGaXjBdbAVaPBDdHBdOP0cnX6IDtqUSvwsDx6Fp4wy0qF6'
        b'KUZHPAdAANfTqRuA5orCjMzseWBgBswAaOEW6gYAXoEHwAnYih9lzQOD6cEMwhgOM8AusAsepLgFZ8PBKYxxSIO7M7JBG9wbAnZlpsI2JuFhw4IqMAwOUWiPl2fBjmm6'
        b'ZnAGkWLsy06MOPERsmNBC9xFvVRSBodAG0UYCXvpPnNokEh2FkkIwKtscBhqlim9EG0IaAUt053Ck+7U+BgFgih9ytjxTTkUTATcBmfmCEWwDbSVwZ4cUXoW3Bkk4BCu'
        b'sJsFTsJr1dRcc9B6HaepnImctCy4C9M42rNCM8E5GrOzc+WSGesH8LXV9AIWW9Jok5M+ieJwFgGuQQ0BDhGVfHCLWosceNYZL1YV3DNzserBbRomc1hCisPZREQlxm3U'
        b'gBYP+lKoa14M7DSC5+BWAt+pWdhR9yem4Bw4lJEOLi17YWk96ZshKyTdfWhtYX/0jLVdAnqmICQL4StgSGy3AQw0cQgykwAXg5bT+IAb8Di8LAYDiKcLL2EETB3cFUvp'
        b'izu8aEKrA7gW90wdimCbgENP/wbQuoiNrcRNTILMIEBfADhN3bktgYNeYnggTwy1bIJcSIDLcqQZ2LRiFMvFc73FMtQghwCXLGsoKyousRC7lYvhAKIuIsBV2LaQKs+A'
        b'Z9zFYpKAl2IJcIKomw+2UP0Hg22gXyxmI7OzQYtA1MNWcJsy0g4jRyII2bOvb9n6M7nGtD3LwZm5chL2ZBFEMpHsBy5QpG/xrPCLOYuONZfVXy/wJARMaulAF9zsQd+D'
        b'gRP2T6/CwAEGPENds+UsyMgQGUuDZ9yilSynJCKZBfegI3jaKtjOJlgsEvTErp26h0SGOgDaxI3w4lNxyYgp6GYoPCEGr9Y+E1ceOEkpPVQXxc40OKhJfGZw8Egq6h1P'
        b'McXNW5wQ9FSu0Tb0jeANeBJuEYNBuPOZcKXmVNdgPzgAb093bit80UiJ2TQstr0pBC/B6rXUCoCDoIcy3WJ/eIhq7Ias+Z9Y7kXYSkOOjoBeEi/XhmR6tfp4lD+Bm0DL'
        b'smkOgMbtRZNG7HRRZiFClrtdLGYRq0swdqsmJYlyMzawH+7NSAvODgC7RciEA6avDFzBdhY4DfaAzfSjkQ6wNwRjjgSge1lwGoswMWKAPbCNRh1GzLLA7xWl7ospM7vp'
        b'u57G2MHtoA3swEsJjsDDU2vJBTtpFRmGQytpFREiAT9TEdCznrJHFhxCriK9EFwKzggOzMavv1lWMyXIQ2qVvgSFpDpbOQWHM6ueAsQh0WHElWsmC+wDl8F2apVWSIt/'
        b'AZs7tRRZGg2bA6oNtGc+bA01WJKwFWpngT3P7SVEYAUbnIfbV1FaGOgRR0EHA+ZNgwfXCBNofJ0GHgU7aHwd3Af2PcXYUQC7AnBtGjFysQq2YowXsv4j0zgv58XKQFQb'
        b'CXbDrqd3yGAn1tddmfjmCBWS4EIsEQ4OcdLgNfpK2gbcTkW8pBaC3c9fKHeDfnpDuwEPg73CNNAXCM4+D0hjIw/EpBQ8Hp6Kgq0Y5eYHN00D3V4JoVgtA32wUxgQDE8m'
        b'PYd2LAIaeoM+iFbjyhQo0xionuIyKVBmnTVlVaYCeJrLSIXnCSKfyIcX4qaszQpcgbvkZAaXciiJkAZ8g21I/45xZRwCieEIAXvxIK9Mvf6SlIh2+k5yPdxGvRYDt4Gr'
        b'lPbl+GGEJxG/t6LMbCjFkqDciLcbOIshFEZEdgEB9hKlmbCd6iVuCeJ5MJRJcI0IoCEaQ+AhSuHgsVKk0J2WFngTNyJYSONPsMgC5En3UPg7eQG4+TygIR/szMPWsjcb'
        b'tuXDHWmoKgTuzMXohlQa2pCXCwZC8xemBmHAHjKrjMJc2IZ2ugvmVjkpFbQZHJyDdh0RmuKWmc6wHO6k3+xYyMXvwOWqHcsymfOMiAK0apSgLhaDixnTOxWHDY6VMgIt'
        b'YB81FXC8BLagXgfAxZm9+s6i6w8QvlMqdrTsedt7JUeJ32GDl8Et0EPv7WiZemfs7jbxFGPmbuYEYiSenV8WxHKNJ6iYINA/jG6VkfBi2CCKVBbjbS0FXpLPEA9+yzIk'
        b'L0AUHIA0LDAtKw/0V2OAYz4W7o6golSsXViDA/J+Icnb66yRvxuAuykw47KlGGFLBGxIKQv6S4EbQQczl+Hl/CkdBa+iEGmGkjqD7VO7ezjsLUJO/nBABN7d89DWMmcu'
        b'vekcLINaVLM5PKKJpLaWi+EJSjGqqQO3/WEnQEvfAQ/C/VNQnWrQQ6N1LrLBwIqFihXgSiSJpM1ZPAtpIN6s2GAQxbaDyCSe9gi0phQXZqGLUeUuePwpF4qlAhbFRw7S'
        b'xBtiERiIakY7VDpq1AAP0zFEa6y9OIKDoldbHEFJ4KUpVQdHbZaJa6wiVqJR4gnQGwn7KZOvQEI7jsY5GhwBtQS1pQ3YwBMCkt7xLopBC6o9BYcjwlBtCopobME2ZQKq'
        b'W+nTjGwAecg9aNHg3nyoNQf9EWG5tMZnOaJFXRhc9AuVR7FFjyk8DLui6M2sFwzYg/OcDQCNvp5YDw8XU4KpXw/OgvNIfoeiQD+DYDgQ8FyIDY252g36kVKeZyPndABF'
        b'x8TL4HowhbkyBS1VcupNy4UB+Nb7FSbl5otnMFAcbAQOeC5VxuKubvHXcbOzYBt+se520ZT+wZ3FqemFqQX0jEAvMuSsYFF2Zg4bxexQa4rODv0AA4GoGHOTnxXsZBuB'
        b'69QLd/BgNDWvFWQa0oc+NhHGRWEoCko4KagBZeedPqAPWWQXPDTTItNRUIf9eEVh8pRF7nw+YIJXl9Pmvhv2Id0dXAWvmovhFgybu0ZGlIfSlS1os9ktx5ClBHBqCrUE'
        b'B6Ip7HltRNtclrwCndqefHC3ryin0TXZbuONOT999V7z1Z2dEVfc/COO/2Zl/qfvXle+dfvT+DqHv3yQfDC6wEE6O35BciG77+EIuZNrYxT/4XeE8V/XE9lHopsfzpl0'
        b'Xv049saDtau6N+04cG3O7TU//vS77o/vXTn91cj5Yc5rP639Yc2l99kmxu+qN9qa166JdN3WdbKRODUZteQht/FK9duXv/2muDO25dqZL9ZOXLW71dSnmBfReHy8qPFg'
        b'CGNO/sCc66zKN3732u1kodb9D5Z9v9174WjGuynWr33f7jX888V73y++9+QNu688N0i26BrznpwVrGUOvtnw8LTJ3KGtQ5KPd9T83urT26Kyi/kHXx+VSfe9E/vjPcbu'
        b'ea8D9zf+ssz/1bvRW1/xnbcqecGnX9oMCthzPQ4HMoK+avYZOvWX+3dXTpb4fuBveHCvOvkzZ3DIeZXgs76Du27t4r+nz+36LP3nHV+PFXq/9/o54iu7usM1rdqo1QMV'
        b'zXHF3i+/b9j7X39PWB286VLd32eBWV5XDO99d2lLz4plobdOP+oxmdc3eTxs2KjJXbun6YORbXvujnwR6wWurbn6G9n2z0VvfbnIYdGx8uE3ZD2Srs9t3vpy8THJmj2f'
        b'c9NXJvxD+1G/1Ck851j3uSVSwa3shI3bbxYyjU/aL/uvM+dq57xb/bL7tcLXFx1gn009meK3K0pS/vcdxWdPFm2fdNu6d+OI21aLLzbUn9uTFLbgjLjy6ju7Plvwch6x'
        b'8v6bd9/97tHgF6G+ybedlqy5EJOycO5A7E9/7mqwSrx3+dH60W9eXvzB3x1XFuw5+cOm4K1/OfsXXl/ttmXx7/y48dxfPX62X7nWfemrPe8FuhlHPrj/GfNA3w27a62O'
        b'wK22n/1g/GvWzaO6dZ3jPh0JX8s5zi5vS/742HF2Z2nN26eO/bzlwe0vdu9bPdnUYeTv4faO68CnDQs9ioBb/aDjueFVA2zD476VKx90rjJrXF57cke41+eX377/qsZH'
        b'nMouXfH7hbkZr37Yn3rp0kvqBh6v7rP0gsSlQ+eCouc1Kzb/5g+b/vhp5MGxfOHR7uKJ7/f98UPJ38Mfv+v29YdNQpNv1m69Ndp1V7Jn43if3x+6Xvko9FLlzcmk32d2'
        b'Ki3muy5eH/nmyDmbewOXmldVqtyqlbWjrmOG8VPfj80WDnxqiLhuvefNZTdnvf6Vx2HuN2+ly2vaftpzbLP+g17/r0Lfb17+/hVbxV4H5dm63uuNr//53RKXXXk9t1QV'
        b'CXtv2f8pb+uD3ZW+kw5f3nr8cc6Th39NzFs/9+PflIt6+2PHOxTpqsHBuq/XvVSY0f/n29Uf3T/7XyfGfz4YcbvsdxP6iI/atoxzIy7d+JPTLc1a5Zv6svc12x4k53z8'
        b'x/roE4X7hMrD3xR/99qJL3frhhmza43Wn/vK5d7p46fz3jj14Oqjv0ymTAqOFbrF/bE92NVt6+O2Sa93jn42fJ7w/c3hLl1w1Uc/2J5PZK5fcPzeyBOeitlZYdvw6aTR'
        b'+8zOrxy6dNvvXRa/39cvjdm+w3hpdUrpaWXLrj9tvF4IRPVwXfedZRZ+QtNvD/clffzY6a9g5KWR5Scn78x7mRf0U1+5wOIJDgxTzeBRIQX2iTPCGCTsh1Fo6giuslLR'
        b'meI4hW0Ke7lAGCgS1MNXKLSRyWIGqjoBdj2hIhStHzyMQVWxwqewKgpU5eP+BO8UYrgtRPgUM7WkAKOmfOxpRNWVcHCbBk0VPcVNrQmA2yms0Ro4qIStQdlQA7a+gOfq'
        b'h9cp7hvhEDhKAaiGVz+HoaIAVCii7KO43wCP+gqzs4KW26VjOJQxGGasgtdhJ8UdUMOOFSga3BUSTBCcjY2rGCIrcIueWH8dOvTBNiPQk/F0YpahzGrWPLppS1njs7DO'
        b'jkRRHRzeQMOz9jAqhdPYLBRy3Mb4rDgp3e3mpiTqHW3E4tR72vRL2vt8qWkvL2yCgxicBXrqQF/T9A8TxLKYqMlmgef/KsTqXwYF4HjuRSjWDDhWy4uvnjcoZkeEymKI'
        b'KSzWMSP61fMyY8LO6dC8jnl6W58dSQZ7xx0pBjunHckGZ7cd6QYHxx0LPnTitbPGbd1UlerkMdtAnW3guKu/hqV3DW5PMji6HlrXsa5zQzvL4OKpTugSths9cHQdt+MZ'
        b'bB1xr2rxmK3/u7b+Br/Asy8df0lrqy3X+0V35LQnqCQPHXlqVueGB678cZ5Io9SW6EKS3uMlG3hePVldWRrf93ihD0MiDIJgQ0CQwV+IujAEhRqCwwyicJwKQwyBIkOQ'
        b'6JGzuafLYfYkj3DxUPt0uxmCw1V1eqdAg7M79dXVXe3bHWuYv+AN4R3h3Qr9/IU63jxVsjpQxwtGoy7Wh8xDw6gFGHqFmgTrnVHHIaqabkv0ddQrXe+c/olfmNZ3iDHE'
        b'1AYOSUYShmvueg836v2yMYSmXMvQcMd98ATytM2atXqfmEdGLE8XFXvSFENKsvWu4YaI2WqRnheG4VlSvVuEITJGHaLnhU/DtaLmjHqF63ni6e+4WscL/56awhG3SYYD'
        b'38XAE2giJpko95DngyRpr20esta66P1iJ9mocJJDuHmrkyaNcN6YcPNVV06a4Lwp4YZWa5KL8xaEWyDqxBLnrQg3oSZp0hrnbQi3AI3dpC3O2xFuwZrKSXucd6D7ccR5'
        b'J5rGGedd6D5dcZ5HuPmpFZNuOO9O8+CB83zCTaRRTHrivBdN443zPnTeF+f9CF9/g7/AEBj0tRB9V7EmRVhk1l3RNEZrzDVY5xo8LqSBOOXal0Yi71rfDR+Zo4vK1gtz'
        b'VEkYEmfw8etKfigM0Rr3zp0u8VUlG4LCejOHEnVB81Qs1RKdU4DB3VuTrvOfNeYfN5Qw5j9/xFrnnqhiIsF5+mkSR/mh2gwdf56KbfDw6Vo75hGm8wgb8xDrPMQPvXw1'
        b'5HF/VSJG/1WquYjE3UPFRP11vTTmHqpzDx1zD9e5h2sl/S+NJOqjFhimG0wyCdTZMyL9NNH9qAXTGKnk/vQRUh8wv8tcxRkXRGiL9IJExPGiLguDSKxN0JZrXkJfl+uc'
        b'hA+j5tBwpLGoNF1U2l0ffVTOIybpHKGyU9XpnAM1iQYef9QzDGmOwclNJdU5BY85ReicIrQF7zvFPDUHX40dsl00yzGPEJ1HiNZozCNa5xH9UCC65Nrrqs3XC2arOePe'
        b'fuqVJ+doPfXe4vHAmEmCjM0mDbnFaLzYRRiuJVyM4Vq+i8lHHEIUpnUYIvudz5cYQiO1jbrQlJG1utCF46LZQ34j1sOCkQK9KB0ZxSwvNVtdr+OLH5n9X9voRUmoRTRu'
        b'0fAuPwK18J+FBozOIg05RYiL6GIKNLaIAo2hFKm/l1qk44VpvXS8SG29jpc4xkvX8dLvRt7n5eHJi/TOoQ957j1pXWmjfvEjvnpeqor8xDdAY33JsddRa33e5WSpIUBw'
        b'yajXSEueNx1HNu95zb/ff8hzEFu9cliq98uaYdrJ3XMx/DP4XeSowmepg97lhVAuI07vHPfQiYcHDdA7B6LsJ+4ixGdojCFu/mhsJmI/NAuz75GN2XfOJh96+nWmf+Hs'
        b'jv3pxo6NavmYo1DnKNTaXXPrdxtSjoUl68KS79q94/Zbt9HiJWNpS3VpSz914j9wdBt3F42GpNx11IXk6t3zRp3yxl0CR4WZepesUbssjH5cqrcPGLfzUys1JTr/2Pfs'
        b'4gx29E+N+L5nF4AUpj3Z4Onbmf7Qla92H3MN/UV/GOfqrnMN1droXCOwx/dUF+gdBRgtO69rnkY85hqicw3RJl1L708fkg/mjJTrIxYYfAIoaKL8ZM6Yzxydz5yhpBFv'
        b'vU/KmE+mzifzbr7eJ0+VPO4bqAnrrcDo1SHP931j1eQki+WZSRrCZyHNCBhKHvEcKb/jO5yp8UVOxZQIi9KWD5FaU6wjviPkCGOI0hI2U4C0BPk8nwBN1Mm5hrmJo4IY'
        b'vc8cg69AU3S6BDlXjfNJDM/2i0NOCRGZj3lHGaKi1Sz1cqSLGJvqpueFaCN0vFnv4xX0Viv0zkIMPF2mcwoccwrTOYVpfcacZn3yomweKdmEs9vfVrMJK/txKy91pMZd'
        b'5x39ntVsg5XDIfMOc5XkPSufh7bOO7K+exJGBIQ/JhhofuOBs3TRqYaAeSP+uoC0x0xydgZlUZmURaGUial+oIB/7wnNix1YYw684nAjGlVoNcHCl5v/j2jCXw0mMGSx'
        b'7NdiBypcoJK3MN1cgkYZ5nNI0uZbAiWPcPLvQg2PcoKJPm40c8ZF6zSs8DF+BHCAWIZ/JZCQMfJJGTOfIWPlM2XsapZJtYA9YUXd6FJoP1myTNYoq51AjX/woC96qWBH'
        b'NoXsk1Tyy6V8CSYSUdLLFnAmjEtL8RV3aemEaWkp/SN/KG9WWtqsLK+fqrEsLa2qlckV9bVSibQRFRiVllY2VqCMfWkphgXWVpSWKxSy2hVKhUReWkp1TkM/KbnFTSeY'
        b'NTkbZbYRvzcLoyioR+zZYG8W1wJeU3BNUHidHSwLXgRO06FoCOzhsOEW0CUgU2qP/riSIa9HnRz2CJN0LM4BuVZbv1x5cv+GBQVR37KTggMCdnBF75z9duep118L9vnm'
        b'fumnPysnct9b7XHrg2H52z7ymDevg8Jl9+8v+yjyVg2vb19naJd0X8VKNttoxWTak9jj38+xO1rquDzyD38bWvrDf83/se/RnFEYOFq888zjwz+9E7Fkmde7X9/+3UFj'
        b'uztJH/9oV3HJZa21+fKQE9dVv+96d19t15XC1wIjxHHmluFewUsTPrxUDfRztrD27WUITnU5V3bN/n0X267Ld39Xhib0UD9YlnxgceLR8fjO4W3KLzhRXUsNVX8tOzS8'
        b'fUMVt+ELMib6Nes95Sdb3bObds3lRMPZ25yu5Nt+IhgacTo0BJRLHxcITnkVPvD87dLKUyLuSrtZd/y2dcpXHFHodj6O6rxV1uf7WfidCbvzkUWu4SHcgXr/pj+tu/74'
        b'Avhx85FlXd/1fFho/G2+972B8z/dX/Npm0uB/9kPT/XeSv3Q1PbntJc17/+hMOnj22R3Tv4bibYCFvVWSQo8JICtmSQFfW2PJuCetQHUey7RMbDjhd81E0SD7SxjuN/6'
        b'Cb5KWgRawC1uIH6RAx2ZEBVsdaQJPcAgC16KhV3UL6SBbaZwQA76Up3A9ezgpxdO1rCdCbTylOn3PYz/2+T/8/se8dSn5Rcf+nCBjKm+sbwSWUDa9MmCjdKf0MkiiDC3'
        b'n2QZmTiOW9q0h7euUnm2ru+Sq8PV5ccxGjyve2O/j1Y25NmvHMrrXz0oupN01wam6sMzP3RyUYWryrsiu03U6TonkdZR5xQ9Gputc8weXVgwWlikW1isdyz+0IGvtumU'
        b'jlr5oDDLCYUApoSNXXtCh/2O+d+yOCYB31qxTLwmCZyYGfNNDWaW7Q6TTJxz5qmq6JyfQBNF58RRQxw6F584UkTlHlIt2DhHtaByVAsqR7WgclQLnENRiLkVamNE513c'
        b'UKupvH8gajeVj5iFWk7lE8gkErWmvhnTrU3oPNV6Kh8UPsQZKTJYO6qqNFG/lv3aEhGOGvNQmG7jhErof4+4HC9U6v6tVQrDJOobAqeTuSzC1GrcxKpdropsr9OZeH3L'
        b'SGeZuHxL4HSSSh8zCVNvnFhNsqjSJcYo/4RBmoQfWYO2KpNwqvIRLvhucp05aZJGjtt4nDIbDU7R8xfobVJHzVLpDWxXAi/JinjNyjbJm0lvYHYTDKQu/7nt61dV1+5X'
        b'trRn21radIKfM8jjprY1AUla4V3N6m84+Xd3tROccGKAG8esfcUIMuUvo5JTVc2StjjTzfFOSbfnRb7tdSZfaN8ZLNty6nfkZfnRQK3S6v0PVn9sdTB+pPaB3d6uL32b'
        b'2tV3Vn7959oTbfGD73qG/HjFyD9luUK058yhecU2H61a7u86eFcU97luxKrybt6nu00jXQKWKP5Q7tS09Ubxg5glOXkOw3nf/4QvPy4k8gRG1OOOXHgtBKiXUD+1mkPd'
        b'nRoRXDDAgBrYAc/SL50NAG1JRk4w7HcGvZgsJ5iBfNCrTHDcEW55Ql3nHgT7wFHQiu+V8f0oaAN7jQgLeMrEhukOh+BN6omNEdjqlEG9gwe64DD1Hh4cqKNejIMHG8At'
        b'uBmeyHjuR1y5AgZsB61eFAXoCIE34HUw/IufeQWd7k8olMvASgthdH46G+MdoKoJtAi8/7mD/F9/RvOreuk97VJ/6VB/1bnWSmsVyFoWTjtX/EL531twlMS2NZjbjZm7'
        b'68zdj6zWmwe0pBhYptszX8kctfY8Ff0eK+gjlscHLPNvOSlG7PBvCZx+Q6WTuRaEmV1LznNvqvAnmPUS6QQLvygxwVYom+olEyyMjkOxZm0FSjEQf4IpV8gm2CvWoIhn'
        b'goVxshPMWqligk39qOEEW1YurUata6VNSsUEs6JGNsFslFVOcKpq6xUS9KWhvGmCuba2aYJdLq+orZ1g1khWIxLUvWmtvFaKoipphWSC06RcUV9bMWFUXlEhaVLIJ8yo'
        b'AcNphOGEOf0wq1beGB0VGjbBldfUVilKqQhvwlwpragpRxFbZalkdcWECYrUUBTYhII2jlKqlEsqnzkdOR/7h//2w+fTvmLhdIJ/HUqOf5Lg559//gdyF5Ykik2xv5iZ'
        b'fk2l/473wG7yjiknwYW448JN8GX+YDz9m6YTVjgOpfJT2+wPLlUzf62aL21U8HGdpDJbYCzDbwPhYLW8vn5KbWTzcJEpEq9MIcewyQlOfWNFeT2S7EKlVFHbIKGCaJls'
        b'WhuehbETxrF0fDxXhl/wwSG6PBMlk0ySJB8xWCRr0ozgmrcYfc0qNCLtJpssCBPrMWNXnbGrKn3M2F9n7D8aNPeOHwzQB6UbjK3GTR1GHcV604hRVsQ4YdXudJ9woUb7'
        b'P9yQ5Ys='
    ))))
