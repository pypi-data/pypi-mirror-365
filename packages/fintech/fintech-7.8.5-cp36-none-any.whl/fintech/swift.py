
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
        b'eJzVfAdYVGfW8L0zw1CGJiJiw7EzdBlEQY1YUDoKFqwwMAOMDDM4BayxgAIiIKKC2MCuICIoiN33ZNck65ribmLIJtlN3yS7STZ9k43/ed87NKP5v/2///ue75NnrjPn'
        b'baef89733Pse1+efCD8R+DFNw4uaW8Zlcct4Na8WFXHLRBrxaolaXMgbRqslGptCLkdqClgu0kjVNoX8Nl5jqxEV8jynliZz9kUK239qHJKXRM9dKM81qC06jdyQKTdn'
        b'a+Tz15mzDXr5XK3erMnIluepMnJUWZoAB4eF2VpTd1+1JlOr15jkmRZ9hllr0JvkZgN2NZo0cuucGpMJh5kCHDJGWFGX48cLPzKKfiZeirlivlhULC6WFNsUS4tti+2K'
        b'7YsdimXFjsVOxc7FLsWuxQOK3YoHFrsXDyr2KB5c7Fk8pHho8bDi4cUjMr0Y0XabvEq4Qm7TyPXSjV6FXDK3cWQhx3PPej07MgXZg4RmKsQJGd3c4/EzAD8DKQoSxsFk'
        b'TmGXoLPD71vmiDgJt1Ztz6XFvTvClrOMQyCcGk6uQRmUJsaRG+sXQAmUJyqgPHrRfH8pNyFSArdIm0nBWyhhcJYcIWWm6JFwLB4qYFc87OI5h2gRaYFtpC2DtyIhxo9b'
        b'NxIJlA88cuL/wodMNyu9fIkY6RUhvTyjV8To5Z8VPY3eCb+gd4ZAr4Kz5Rw5zjVo/PPD7FFKDBg8jjKB44LypxnvBWcKQPNCe84VYUEeq7K9xjsLwO0ZEg7/lwdlPu++'
        b'fthMTueAwKs6T8nXblzEFwPX8XGy9onFfoWczh4blvjU8i222HuIPmz7iA7NLAG8LfUfLntdeO8vuM1+n486tzqP6+Is/tigXUvakO1lgQu8vWFnYJQ/7CRnF3rHxEOl'
        b'X0C0fwyUkqp4ntO72E9XT+vHWodueoMoaylbuUxxD/P4X2Ve0ePMk/6CeTKBeZkTndP+KJ6CTEmLMypjOEsgVYAySRAivcs3FnZBadyCqGi/6EVccGzyILIX9pKOhaSM'
        b'7OOybGzhKKmEaxY686BR5LKSdOD85OyQ6dwaclxscUd4iHiQklyi4MPkJOzgcnKhiQ2AI8NlymD8QvaPJNe4DHsoZQPgggs0QLUNxwVwpIQ0BsDOfIbqlQ0OC78VeaOk'
        b'0+IC7eIE6V0a6eaZIo7Cb2nTWgvmc9q3P5DxJhX+/v38xk/TPk5bnRmnupcZsMdbFaX6JM0tIztTl/5ZWozqX5PvZyqSolWK+bGq85oz/LmBWR+rY1S/E70w8URLR3C0'
        b'6DdJD5M9G/x+6+7s6nu488DF6rOFA9T6IHGWlIsqGVTxQb5CZKYugZyBNtgvQ1Yp4i3+PihkETeIFM9cJLEbP9s8hDI+jhxAdu6EStgl5iRhQ514chHOQpGC7xJ5KxRi'
        b'I5V37+Us90+PaZlGw3qNXp4puK8AU4E20/xMlwPzTalqlVlDPajJkQp4tCPvyLvydrw3b6SCNlIhK8RdNvkqnUXTZZuaarToU1O7ZKmpGTqNSm/JS039xaIK3mhLv9vQ'
        b'C51lDJ3fmc7/jqtIyot4KbtahiHEUxnnG+Xnk0DKyX5xImqHDecBWyVDyInYuRkiq95JnqDE6CN6lFjEPIAYlVjElFjMlFj0rPhJHqDbKvorsTSBqVISNEMTVPO+cI7j'
        b'/Dl/UjSWwXVkN7kC1eI1Fo4L5ALJLrLfQj0WnCe7l6KKFcyiShYAW5ZqHUOuiU3UYN+Tbvw07cX0KFWcanXmJ+pP0vz2RKn+nuaWxbUOCa+tG1L4zjNDpii5cmL78l/R'
        b'YZopO8jx9VDqG+OPXvXKkOi4BBtORi6K4PB40mKVxWPMZlDG6i6ZINFMnUFlZiKlWs35OPISFKjRoUecEiaeLhu1Jl1rNtJORup4FKI+IhQZaUzqI0c63LdHjq/3k+No'
        b'yohLmXADiqDCKs1EFiH8eG5YroRUwUU0SU9K33VSFWoyQwlpDg2ScKJ0DCdwnFy3DMLG6dBCzprMI+FEaBDPiTQYPvL9LR7MkiPJNZPZhZwNDRJzoiwOGrPhhtBUg3Pe'
        b'MplXSibTCfUcnIN6s9BUS1psTOYMaJwcJOJEBhw1h9QxPGBvNtlpgktkW/QkuhYp5KAtgly0DKYKsTIcm6ADzkwKssG2IqQOTknYnJGwm9w0GZcksGE4ZRMS3WqhxklO'
        b'kkPkKrRZbFdNpKigY0N7LiEXBMpLJ8FlbJwHjRMpNmQ/nbV6PpuVnMyaYTLBPjinpCM3c9A8HXaxJqNyAY6CW3BuIiWd1HFwZdxEy1A66hKpRX+AredJxcQgW2w9yEEn'
        b'KdrMRqaR2qXQZiK1ZkcHXBAu8yFQZWRNa+DaWJkxHA4zIZBTHHS4wH6BMw2kWiqDizpyZRJtxIgthi3kEjODjJEjZA6kOCSYEg/7efuQdczTLvEeLIN2VSKjG7bz/Eyo'
        b'ZCJdk2IxQRupMhY4UxQaeN+hcIFxC25pYIvJHvODXU7QQqe7xYfCbjjBREAOwTYb2ZoIUmuBdszx4CI/DqqS2ZykSQlbTbK40UYzHVbLe4mgUGBjzXI4YjIPhhPQIaNt'
        b'5bwvn8YwJA0pMpMzaYCzTsgMsQ0/ndcJSlJHdkCNyXk5KXVy5jmxPR+xFLYJ1EL9KJOzY7TTGkrVFT5geKqA3Da4iQs4wbbIPLJLwonH8BE6ckpArihmhsloWcE0Jw/9'
        b'AxyA82yhceuSUPHPkFuhIVJOlInKjawuYcjZD4g1mcJylUzbUBNbC6CRreQpzzfBRTEUQ5sL5V8zH0I64ZjAwItwyMcE7dCBzBKaz/FK2Mcr5CyefbNyIL9ivEHCzb+d'
        b'+3DJVBUDOkwaxIdEoh8Iup1bOxyeYcCizR78lMgNEi7vdq6n7l42A8YuG8JvHF+IHuP2ppTBtk4MeHfMMN5dUyLhIhA48ZGRAf8wbDi/YmyNhJMj0DtTwYBfp3rxl2bV'
        b'Sri025se5rlFMKB9lpzfIj8t4Vxvb/K0vySgNFw2mr+ddIHiuclz8qz5DKjPGcfHyS9TPDelhB9dyIAJC8bzEcHXKZ6bUkKmBTFggYeC/2nYbyieppTZ4TMZ8B03H/7P'
        b'insIvGPylHTNZsCXHP34l7MeUORNtfnFwQz4N9tAPsLmDQRizxE/pTHgg4IgflrUu5QiU+2Ev4sYMDk6mHef8DkC75geTvSezICnLCG8PPsLSqbp4XK9FwPOXDSZX7vu'
        b'ZwTeMaUs2K9lQGnwFP52oMQGaTd5zk5KZED3+Kn82oXOCLxjql1/JlJAacI0/p5pgA0yxORpnOvOgD/GzuAj3IciEPEcNyiGAYs3zeR/ihhjg1wypfCFmxnw1Rmz+bWR'
        b'3gjEOUP/LmXAD4Iiece8YBtknSklRS2I+LD7PL5eNgOBlCKdKwM289H8dbdIdPq3cx4aAp0Z8GRMHGpIkg2yLueh/XtrGfD0rES+fkkqAu/keGrPDGXAM+L5fHakygZZ'
        b'l1ObLzYxYGNcMu+XqEXgnZyUCcflguF1wK0xJhnZMcuB2p0jH0GKoFNI6CpsfGTGiPHOTmiqA/jpsJcXvMlsdGjQoUgvMImZw/BdDjuZoSxJhcPoaEJIK3puavl7+dHk'
        b'uJNCwtb/zOkuv3bTNFsktKB2Up6OAce5vcCfWToLQ9xtg+fisVEMqNzwIr97WRQC7xg8B0wyMOAjyT3+zOBkW6Te4Dmh1u3JyTXdflp3b717Fi7TvifRlvzHdym4teAG'
        b'/SJHSUiwjMTvmdA4hpQl4n6qEkqj4wOgNFCUBm2cR5pkAmmNZyhf9MX0kAuy8Fya36Lpg4UMd+Iaumn5foVDWlpc54YwTohLx0jjstjA2LH2UJGI2ZcdFInWwa1JjK0F'
        b'5CyUkzYMNJh38wOgdSl637AkIfq0jIATvt6Yp5YEJsA5UmjDOWaJXaAu1kI3lKTVU0PaJJisy7lwLty1wEhzEoHz83AZrmSZQ0Sa4/tpvgLQMJ3uvf4slsjT4oLil3CC'
        b'Bx4NJ5RBHNkCtTjjHk7lM9cyFuEbCjxiWRZcSXeVsaQyMJqc9+Y5OfryXWYbZ9IKuxkWef5yZQi3nJzE4Xu59DErGAfJOXdyyRd3UWxHiluqaGglOyTcQIUYdiUvEjK7'
        b'KlKThbuKmEy6r+AylqiYqzbAxZFK0iohRycj/Cin88JIxwLMbszEbyiVHCn0w19HuKxNzsIupHo13FQqpXNIAw1D3OpAOMpwg/OrPZWhXOIGBNdy6jFjLcOZWZjJsdgY'
        b'2EVOwVUoSxCk4pwnniLLYfPZQsVSZagEyibhuAOchlSQG2zkqJnQFBuHAwKh3JdcgiM8J1uGMQM6oZZxc54jXFOGYlSEchxax2V6rRLMrZA0xStDpdCeivCDXFbIOCEV'
        b'2EJukRNQhhuSeBtO4sXDhWBybOMCxp9B80i9MpSfSm7RaM1lL3NgSJBqcgTKfKk4oDSBnB8XL+Ecp6Na7IRTbJzKdoWStHOzlmHfek4XTA6ytWYP9oWyuBi6rRHDTT6G'
        b'HCUHyXUosixg8qJ3HExx0dHx9H5Dz27SO0DhEx+g8Bc5kJMa5NcpcsLbm5z18FXg7vKErzvZ6zEINeIknBhMTos4stPdldTDIbgsSOyM3sE3wT9Kwkki+LlJ5NwIKGFa'
        b'70W12eRktFAnc4TPgoNjaJoipBjX4Ogz0OYsNLbzpHySwnsVa9LR1LPNOuwmj9lnre9mI3Ncw9aQGyYcI3gmcm71SNKhEHhcRy5gzrLG4kCz0Gt8CrksJ8dgH5vRM3Ua'
        b'BvgCuGTD8jA0xopRjguY9eG4y6jlbdjoxLP8iDRCZ3A+2SJY9UlodZY5y0gletBlPKknV5fDHlLIsAkgR+eZzA4FNPW7wc+FluEoY0Y57MBcopO20RW38ilQL1+ByZWQ'
        b'b5DGUdBmNsIlmofe5FHjrw0jV+YIdBxDlreYoNUs5Xg5bEcDgMos0s4WhBZUpaMyOyd0luLJvJTURG2YzxYcj1lQC2awaxwpEXU8bu0vTEgpYJqycoqnzNkRtybiqTw5'
        b'4RI9eyRjytwU5L+LEfNJsTNP9pOOyajQx9lsS10Iptgu0ErjxmieHBo/Ew6TVsEMmyfNNK1h65B2HhqyvXRD2HzJUCMzOQhS28Mnkf1yTLc62JgNmI9WyVib2I1Xk51B'
        b'y9MZajTDvAnVUm7tHM6P84OGqQLXD+NepoSUuTisyec5CTQP06GCjNUy/nlmh5Ay6MD4ZEFjIldnUU3YGgNbmDwHGzFNLiuAdkdSigoJJRNIEU8ODCZtCmdBNJ0F5IDM'
        b'wR5aEZlwKtEd86bCGaHtPKkjjSarUu7nSfWIUZguMxryp23uVWWyY9UYOKpmVr+Q7AmX2THaHHhSMSAgz5XxQ7wEiWtzFIY086QpawI0ZAlCPokmWYXicjTSxpM8OTZ2'
        b'ghNsZ0J2jCSnTc7QzpLyo6is4rFhYaxFTbZMRD2W2dNEvpVPlYbC1gFCDKmHrfEyI26MLksEoykhxwJQ/w8LyXQFNI7uURs/2Bq1hghUDXt2swwu26+RcuIJ/AiyJYwc'
        b'CBHssxm3g1tZGyYV3jxp0IcvnskEMCWblJtIeZ6woWjm0S9sUaACXWA8XABb4BJimeeC2TmUotxI3fh5BezWG7mymkoHqknlWjiZD3uxcSc5H4oGuQ9qoBr2L+G5Mask'
        b'1Nk0MN/ubiH7oNqWm+PMBXFBydBuSaTzNK0fib1rcM9a8tgsexG6Gxdoxf/3khbSgbDd2K/YHp1KDW4bGrNXo9GR8xzpJPX2uO276SrI5Ca6yvI+7IUDK0LdUfiUqHUb'
        b'E/pyl1SbAnCNBsEoy8mxYb1MJDVLwyYLqkbK7eBSLwuhKD8cKsk2y3xsGzp/hAzKY9G9R8UHRJOTmdQj+0J5fIx/EpQkJnsHxMegI4fyaMXiKIysSWjel0xLONMgeqvv'
        b'PLpk4ZafK9nn5khuyIWd81Wyux/zV5LW8ejNtyhEQlA5CaUTYgP8DVDiE0NXb5ZwLovFOnSdl4QOxaR+Aw0K5asiafTjMY2pxQ04XCA7BHfZDntDYqEiyi8m0R9q7aSc'
        b'LBYNwomcYLyYB0eQNz32I3MYhcRY6D053JuSGt+Y+Fh/unDCKLkN50aOiFFCbeQsokctyZHU5GBcJSV5QlglVZkMngpVw2hYPb9WCKvhUK77/tGjR75Daf7TssE2Ik33'
        b'SD+NU7gLbMft4KpeW0XPWDUGagT3SqqwtblP3JkGZQpSMYSxzwf2QFOfyINdj/mSbeSwYBHF5GhMb/CBI9A40nM0s6JlsCOkN/SMJs3yFQMFpdpKdpCqfrFnu2qU1ChI'
        b'qwO2RfWNPHAK9gRDwyjBZjt80P56Ig/sGL3cJ5ghYgMHcaPdE3c8ycnh5EQMG7QWOmJ7ow7Upcrh9DzBtZWTcijqG3ZU0mHjFwmUXST1y60hRzuLRZxJpFrw9odJbUqP'
        b'55gTHbUaSoX5mlHVjvaJOBPJgQmjM4RB58eRQz0hZx0XTS4LN5Iw/CDuPUEn2DIZbqE9sKi4h9SQ6r5Bp4bsnpkM9YJIb+GeZmdv2BkDRV5QPF5o60wku3sDD5xwlMMN'
        b'0sgwWUwaBvbEHVyrMChaxlSneRNLnfMdI9LiPIaLOAZcOZwCnx/tjPo0dbaYQ7X0ELznxYBeA4fL+jBS52Pl3IKIPj6ylJwKnwql2mEvnONN72Kevv6L91cunJrovsD9'
        b'5oU3Dm/yHX1ly9CRC54r2uYtDygd7eOzvfQ3yyLS14jWvKZrFf/G47ukKXVxqnvP1b1IyPcyvzNn/c/7+f1rwLPf3YvY++7bnd9N/WijyeuduMwdM17NW6TO/Ople9+o'
        b'9u3VP3f6NY39o8eJqFt3B9b+9Yu3PaqinrtvcnC492NN+Ojqf720fWVSWNWXq+7URweJ9Y/WfZ7kqfAdWDo55tW1Sn1Vu0/VwhcyDt17P++tGLX35CWH2v98zGe54/0/'
        b'ktjlsy8f2bl5mdO36+c53hRpuR8gqi1i2Q159cXbf13ocm/q8SmHMz/zSRjjBfY/NEi/mJD04Zqs9Q77Iz8c6n/lfnD7/YcpW6d/sm9LLq89mlab9vmNhRscv31hdPrO'
        b'LxPvGZ+5u7Fg66Yvayd5xRZ618te22Wf9KeXsvZNeo98siZ18kcOn6f+UOplKzr8mmyWLHPqgtgl179VXn844NKHIrfmkBN/ylqku2nWLK+IMftWDesacvr2heBBF5b+'
        b'/tpF/pP3rn2Ubcp/7UrSZrL++qr6cfcbDn20++zMG5++E/aGx9n3v3c5e+/zJp85L/+t4uOXBj2zc5OzMXbhqTfmZK7+SL5oQnrmgsKH++9+6vba8Nc0Tb4pSnP1h1rV'
        b'mxETtzUbcr69unXlKyGfz6sq+zH+a5JTNbXqee+4ItkD48KGqaFxC4e/usfplc93//2qwxfnzq/906KG+5XtL36y8e70B82ZhWd2vbBtiNc3f3gY7v52i9O5r+My3x3w'
        b'MLz2asWtpSO0QZPPrE8Ye27+dwN/XhwyPfKbScuOxRz76cSPviXLP7wC712J8Xr9lvRN5dfxd2+pGv+V1fjh28/PPN0kfvNj7dF5Ph97vbt//uSX/T/44zeLf5765l8O'
        b'vnX1Ja+utZcbVjy4rJNVPZjnlfL74+seelx6+dgQdfa7Z2pfcVze8OnP7rqvdL7HtDfLnX8ItBk6sfCvzY98Pm+7W7Aw9SfLq273f/NIvHn7vk0zjtv++auVKz7Qv796'
        b'o53H9JRPd858+JvrqSUvvpZ6eYrP9o6zCiczDRxiDKlNUOaXgNsJqPRbhPGTk5FGTA9kg9gN+VhS4uUbEO3nowjAdijlhsN2zlMuWZW90swcc4ltTt8TGX4TbiUv6tJZ'
        b'46RJ0OgbgDuWUj+ek5KKOFIv8h9DjrGzHFILB0fG+nlrQ6MwsmDEwmXXkRI4YGYWehADUWx0vE+8LSeVWOCEyA59qZnuXnF3UgP76H12nBdKMepVku3OYm7gVDEc9Jpu'
        b'pg51Bibc52MT/amP6yCn8/mZfuQ6wwkKl5DjvgEK2InbVClpiiHbRcqxpNZMfVLKMLIHyuL9oqECG0PIPlIqcnazZ5zwIVVwLpYe5sVG0+2XbhOySi2Cg6EubOLIxe6+'
        b'PgFwOdVKr/1UETkaRDoZn6E5Al08RmbMFPxj/KIT52MchStiKA56RuH6+JnGf/aisP/3xvSeobgJZyhmo0pvUgnn+Owo5Q944WY583a8lHfnHVEYjryzCL9h7mzHu/HO'
        b'PD05s+Md2Mcd/1zx/+4//C5yFr6LHGylPB3twHuI3ER2Io6nfxKRBOdw5T2wRYp/Q3F2DwZxl0j4vn90BQnrg99FbmxVCV7deWe2toPIlfdiLfgROSBUgvg54m8p74nt'
        b'CKf/Y8tQ/Bgdu+lXiLsc+5Ld52Do3+Omgjc6dfOTTT+b6z42ujW877GRgu7YMLidsB4ZxSQFKmJwc58QFyBota+Um0eabMlesj1dwbPAFQvHoCI2muwa7ReN2ySMzAen'
        b'w8l+N+To4uy+2RyO3ZCjRQTcL8sIMp16bsyJnnpjTpzM2WcpJN/k4qQO8j7/5lM1MclV/Ws7WMHIujyNPH5hWEiQ3GBkX4ID+g3t9yPaLDdqzBajns6l05rMdIp0lT5H'
        b'rsrIMFj0ZrnJrDJrcjV6s0lekK3NyJarjBock2fUmBCoUfebTmWSW0wWlU6u1jIpqoxajSlAPlNnMshVOp08OXL+THmmVqNTm9g8mrUo8gychfbR9ZuKnfgKvTIM+nyN'
        b'EXvRkhaLXpthUGsQL6NWn2X6Fdpm9mKxTp6NqNFamkyDTmcowJF0AksGkq4Jf/oU/shDtcaYatRkaowafYYm3Lqu3HumJRNxzzKZrG3rFY+N/OUYlEdaWoJBr0lLk3vP'
        b'0qy3ZD11MBUBJbN3vVkI0Wm05vWqbN3jva2y6u0ca9CbDXpLbq7G+HhfhKZrjH3pMFFEntw5XaVTIQWphjyNPpyxEwfoM1XIeJNKpzb0729FJlfAZY4mQ5uLqoCUUkY9'
        b'qWuGxUg5tK4XG9z7Zxst+if2pqUC4eyKc1oysrGbCX9Zcp+GdYbOYNJ0ox2pV/8vQDndYMjRqK0499OXxWgPZo2e0SDP0qTjbOb/2bToDeb/ACn5BmMW+hdjzv9QakyW'
        b'3NQMo0atNZueREsytRv5PIvZlJFt1GYiWfJAwevKDXrduv9WmqxOQKtnVkodhdxKmkb/JLJYAcavUDVLo1OZzGz4/w6i+uYP4T3hrG8s6vF3eQaT+fEJrJqhMWUYtXl0'
        b'yNM8N5W1Rpv+FIxp5DKrupVrCUYuXEqne4qGWRftVcf+az1dNf9tvhs1GEXR6MLl6GWwZxJcz8hJFxZ4Un/qi5D41BxNH1F1I4Qs0MF1k0mj+7WhZgzwT2GidR7a48nI'
        b'/iLixlr0ao3+yRHTuizGyCfE6v4LY59fmyMrv3/cnUelDScyzSb0VJmYxNDmJw3MM6IA0OepnrzufGuzRu+fYAx4Gvb91v4F3k+O/1ZFeCwH6Df4qfmAMFaLSz95YPSs'
        b'mQlPV7tUg1GbpdVTlfqlD0m0tqUzhUQDls81anLVBU+19b4z/wcUWuj+bzqTbBVGmye6vHmadLiOZv0En/DfgBg1A2Zn1M/1w2shtvy6selVuZpeb2fNi+XeCQh+op5a'
        b'jHksL/rFiMUaY4FGr6Zmub5Ak5HzpNEmTZ4qvG9ijRP0yeqfMGK5Xr8yXL5In6M3FOh7s251332ASq1GQIHWnE2TdK2RZqkaozZDrlX/WoYfjrtlVS51m4jTwuzHKt37'
        b'Dwy37nPCcV/wpMjQv3dPJQS9G+rBPV4JsVIoOfYOpVUOnN0Bx7S4A8tkQiHBGhd6N5TL+2Bmmp82I44TTvMbScdA0iYiTaEcN5WbGjCI9W11kbKC7zp5mm7/ZHuO3Xwt'
        b'cMxVQg2pESqKuQy4Rm5Y5PTHDiiU+vbuUaeTfdZt6qiRNkND7RWOlvHCvecichPKAmOi/cnOwJh4qIZD1vMDG24ilEt988kZdm7xTAQp7D1cIPuHdJ8uLCW72fEDnIct'
        b'cJyWA3SXAkDJQFYNIIfDwsnG0YFLe079R0C99dB/ELkgTNAxHc5AmXBCI+LsoAGKoFNEdpI6st1CK3PhwExSS1eIhl2IQzlUyuBsYBSUi7mRbhKoJWcMrOYCmkgp7O3T'
        b'kVaglJITaYFI1Vhfm2l2UMEeEJgynFT07UZ2Rwm1GgnxPKcg121IXVAcKxolNbG5/VZGpmnIxWjsNzbNJiKXbGF83zwaDvoG0JOAxADkZukUuOmnkHLD4KCEHJ9LyoW6'
        b'iZZNidZO0fGw088+EbsMHiQJyoB6YbG9OP/lPuKD1vQ+4vMAoaLX4gTHlCGWYFpnXsOpoWUtq1NeTS4P75XUpqBuQU0jR9hZD2nWQbtSGRFsw856sqFTZ6FVPLqxDlBt'
        b'6xvE0XNAOJIhHFcd9nTtK9NZZAuTKVxCmdB7aWki2x6ZDvewinQ4tLDDEg3UwjHYO0VJWvOkHB+Hay8MFk6J9sINuKXESyNp5VgVSg65CkXsvCForqiPHkSMZFpgTmS3'
        b'VbRQxc4ly5XKPDHHx3LkvBMIBY1wKSxmGJxTKqHFhuOTOHJpEuwSSL5qnCTNUSqNOCKRIxcmo86yG5uNUE0Ow2moxUGtOGgxR9rJUdguWGKrH6lRjo5U8rT2iMsJGsPA'
        b'QU7OSnJzlJKy7zin8yRXmYFGpHtwfmjo9QFpG30G+XMWFwQumpRm4ifSkqBILnK+UDDIebnSx2nSDqxNizs+roBTiNkDKBGkhLSzg0HrsSC5hIJnR4PbSRkzIA1pGRcb'
        b'4N99sLgBWoWzxfNCfehkUgx7YllhukTCLyU7kJItSmYRC0gT1PfTX9JK9vQxnXXQYBmFHV2GkB2PG44B9nUbzsZEC30kJRz2QF3fbiPQ9h8znDyyi80IN4LMj1tOBGnv'
        b'tpxMg3CgVWPvqXSEXUoJq1XKRsnssT6+4syhItp5zUhztIzzoieQ1NDMo2Wx0f4JAWg+3lC6HudF+xBzw0ixhJyERotVvFF2tABH4R8t4ey9yRZbEamAZtIqHP8Vpi7t'
        b'4ZaeHCFHV5PrwrNALbCbFPWTRQmpZbKIgyamormGMb4x/rH+Pgn0xLF1CueSJdbkZDCK1SkD+5d8QeXQUQnkvIQbFiche5aFMQoGDQ5+rDAsdrq1NMxs42yKFzC5LILq'
        b'XmNeROp7DnVL0FjYQ07tZLuDYKKkAl14LGyHw90u3CfDhjTGkgNCCUM7OtTDsYGx1vI50oEKUyRaN2atIKgr+LOzf63ZOWiy1prNIPuYd3FNhpN9HcJmqGYOQUvqWDtp'
        b'gQPoLLtdghwarD5BOVk41dwDF2R966ccbMnBYYnsFusCUkxKetiOPrwyMG4K7IyjJxax9HmsYFIjjSb1RiGcdEY69pyTbyNF1oNycsaHeZhB4XCjt7hLHykUd60azLBI'
        b'hoNZfarFVsJ1Wly4nLWFp4V31wqKg4RKQXId/Ts90NjwDOnsX9AIHTMDRaygEa6tZnol3oREdOsVOUBOkaMmHUOJzxrQq46oUBepPmaRSqEKsYlcDJGJyF70G8lc8iph'
        b'yKRI0tSraLBTxhTNbQIzmphgclyWI6JPrsBZTADIGbgp1OtVwYGJUM2vfJY9GhKjZr5cA9td+il1J6omVWotXGG25mm2o/Wc2bLVaX71dnqOBSNDxJzHtZkUDemjzjmC'
        b'NR1Il0C1HFWoxhZ/VXKpcGUk8z2uXtDYTz+ryLZ++kn2pjEvbYAmb9JG9ucGiWnJG2eYN4vxICIGDkG1izNchn22nG4DsnUhXCBtrMpjZIa6T5VH/AIUN3ohKE+GkmiE'
        b'B0LpfFrsESVUeiyYT1qDkpOi/GhxXimSMwOuLpoP5RJkv5NrIuyUC5Zy0xcTjV5PG7WcOVpoTGd8qrSX0WxvyvdD0xxPRY7nFqILZ8Pq4BhpihU0n+dQF89KU0U+rnCV'
        b'mQaGwt0j+8w6LUqYdTtsY+1jlsL+vvKBQ25MPBGkhiVIAyPgfN+8gRwkF62Zw7KNDDHH2Y4c5dhXS1GAihiO6Wx6IJzom5OQ6rDenMRrrmUJx6rpitaa+vEIGUQf4Avw'
        b'90ZL8LGWMyZT9u4bDiV+i6OoETADW9DLTisvb20YQMpXY5Cl62enJfc3GZ7UW00GdX6XUOC4c/CSdAxJbSE0T1iAQX36AKH0er8zGl8lFNMmnkX15kSVRcm8+0AewzeK'
        b'uQr2w95+dUrNNqQ1PWm8wZxOLk/ikanSpZhOnhY09Vwu2eFMripD12A6EIMTDsS8S3giAq6HKdHpFYZIWU6lgbow4YE+XONYzAJlSD7iEMGRs0usBZgR5KoH2YZqGwIt'
        b'HMsfWsktKBaIah4YHJONTROxZS6mOApyxUKPeqCIbCdVqLZQhmwpC4TKZGhxQvOfOB/1VKMRpJDkvzjpcc6iDR11gDoPqBMylC0Y6kij1BvR3chtnE12MKa5502AowgP'
        b'JRdFnMiDFntWk3PMxqaTZkz5G22gZgHHPcs9uwEus7oxOApbFSb2JF+SNz2vpba+xLq2CmqE5Zf425J9NhmWcByxEjOlKllCPJT7L7bqCpQuiYpZFLVQIIacRcuL9w9I'
        b'iEu04chpDVyDFgeyfaFKQL14MdpDtc0Ed+FxtJvjGerOcNIWkb0Gx8l5G5rxUzG7dxdXoQeBG30siJRvYCY0E3YLFtYmgu19TSgwW8igdkUKAu6cMpSWA7WzcqAO3jcs'
        b'xDDR4o0t46bp+wee0RioHo88cH2gYOfXyF5yrW8F3ilycTwpRIVnzSUrR/cEpvIQa1yCc2S/sIu59SyU9EleyA1MZ/tkLwo4xwrQrbUxqCMHlpIyvk8OrSDbGDmh+XBF'
        b'SaqgvieFziIHFFLWRuuKS8iFsN40WQonBbVsiQs0zuqTJZOr4UKZT2UOTa5JY2+ijL/OMixcMBstCYSGvnlyxzA23/B1UKeEU2Rfd55MjkayhlQ4CFeVq1d1Z8qkBo4j'
        b'USxVP+W1GDowO+3BjmwdKySCTavmJWf2wQ7OZlkHIYNvJiBORb34rdUwzEWYDbXCdUUf7JASuhiLhuULnEy8jw1Lwuk+kC0ULKbbx0Pre6InnHRnNUpfuLNno9NemJMW'
        b'lxKu5bpR3rppmCS1j4eCo+SiIKFyb3IYM7KKPj4q000hsVI6BOrDSXuvtyHN45gpThTBISW5MKnH1zS5MsRkQ1SesKPX1WCatlVInS5A82Kode7nbIqCrOfNcN5SgCjs'
        b'7+NvhpOj3axrhC2kA80N2qiuoMEtRCdFWzxJvR9Ua9b1mttE0sj4EGwR7k5ATJrfKxOVnDZs5k6J6RrG5pvTf29ZGGsYHun699en5eeHrnrzzkF7PvQvg6Zet4+222B3'
        b'Z05M0IcDbke/v+KYW1X+iQFTy0aPsaR67pa6N4QZU0Y5D58if87l+Ym3uFHPznb+iXuO/9Ly+64UcmbSgz+mLlmyaMmmlZe9ymI2njTIJkRNKU2sMl+1L3h32YWy8Vd+'
        b'6FBa0uL9fRcdadw3aZ/5t3UXmySZ8avlh9ozr4YNES064ftG7T881PF1cSfbL8tWfDx6WNLuxn8M9v2d4ZOKfe6Zx/YkpUwMXdzqXvX951f8vetOJoRe/d4+NP3hFcOY'
        b'Q5/vkrQYto67/fOJ5vJ/tPwEc7/40/n327clhLt9/93cYyU/xFW+5Hr/+sHicj+XiV1Z5oEfb9j1bOrsg9KxNxceqIzJ3Fbx/rmk3cqhay9VyH1fvL4iOjz8wUb47oef'
        b'/Nv/GXT9iG3+votTd40Qf+veUmy0+Sznt158u0RnU6voGLLBfcDZd71evrvlE+P2ZZV7dpgqbdWrN9//qf69Nrj/jrq2dM38O+nr1Prf3DOE6gzKLZHDHpRW1W/91H3T'
        b'85UZtyJ3NBfWhj9/Z2Cn6Nuxxq4vTR/6rxr14ExiaK1t6ettpR1RI99vmB2pa/10w/q74zcsiz64vDhlxdU26di3HvzYsPKVB1c6P4p98fSrc+M/8f9L49R35k1v3/dp'
        b'p90fP3lD/0HG1LB317/i807gqUmrLrS//dtRh0WBIXl5d0eQnxy/EsdJbDNeujPXo2b3N1lhn95auv2nnKjv/rzkFdOf2wM2v62pXX5m9rUty9RNpuMeX1//o+/zH3zU'
        b'Gpq/ddeFvRc0L4Uf28QfKt16w+6HkzGv/E5ZfvjBmDt1jbbZN4lF/839LWMUnx1963Jq06U1D4q/v7/mp6rKW2cG/Gte2iFF4utvrZlzgV/S7BL4rzW7Dv3l5MWiAsfA'
        b'Vcts3F5d95Lh8/J1P/mY1pR3rs38/Bt517tj8zse/rz9Xc/3c/wM7pvmfHfV6fzPKZcHdL2s+FpiLvxr5Z+GBBizrsg6ZxsWGsPV2huRDYqgzba+hr9/MP/lcTN+vD/r'
        b'9TdeumBbUPHW2x/864eV329seefVaUsm375Sm3Ourv6nsuOzRox65Bz2ZfDZP917feUtr9Nmh7a6JRvXfPTs4d1z3hrckOPz9fMHC956NWve346tFL33xXe63xe56d+I'
        b'XL72b3M3dv1u4MOmk18cT3hUfu9u/kr3T7qeec34+QGlxzMBL7n7tMYtmZL5hWvTprKpvw3ODWq///DNjz3vqEd4JaZdLh0ueWD7dUXNvJ/H6aQlL9a1zSqrijjibprm'
        b'55Jx4YPKLw8ccvzuo9zg58qqX776xYwRy1cMOhz4M/+lzc5dl8cqnFlh1oAwuGQt98IIT2P8UA9/TCVJuyQKt8es6gtzwlPkvK+PtQDLntyKWioiJ1dtZG8AwFyrflpv'
        b'udnMNCjlWLUZnII2VqE1yVLQU1GGu6s2KakQ+ecksbnDoIJcjPXzttaTxaFXbBStcyV7GXakntTD9d5aN1KysLvWDWpJk5nujJfwsLV/YdmZNGthGRyfIhBQTfbN902I'
        b'94uhNWJ2cIvUkk5RgaOIoRcJ13jcHuwM9Gc3DKukBaIA0rmBFZDJYM/qWEStu5IOrqzgXILEWcvJbjazOAuu96b5e+AUTfNJCdnFZoZtxvjusjXc/12RkiaRcloCm9kL'
        b'2gezh+ajcYd8ltzofmo+B5lGN+FDcCe6C9po5Ro5n0fzMSiEffTtCtMkYsx/zinc/3+XoD2xMsrpPz/PLx73zzWHhQSxGrU5tApqM/652fVUizmzejE7ViMm4h15N5FQ'
        b'LeYgEvFP+hMq22h/TxGtUaM9adWYu8iB7/snzOAsjHrKXMKfnciZl/NSEX0NgSvvKXblndkaEt4Lx9OqNVeRnFWl4azWejU7tpqHWLhKBBxEjiJHhheromPr40dEqaEF'
        b'ZaPxt5TV1THsaI2cyIFV5Tnww3lP3gPbhyIGEp5WxXXT4yoS6vfoN/pOA0qXkd5jTOguipPQ040+xXD/eRkqeKNrtxTZWr+j0qMgbgvXMbZviRzzCXUj/DdnWWvkoNKf'
        b'7mg4bmieGDrto/q91YLKP4LORbcCGvoWJG6ZSM0vE6tFrI5N3OXKDmhY8Zox0mg0GP85UjiyYbpktNaiadRylV6uoe0BCQpJl11qKj3jSk3tckhNFV53hN8dU1PXWFQ6'
        b'a4ttaqrakJGaKiho74URSfPFLsSO1VLaiYSEvViRKXMOwE1mh1lmT6nzN1rfeRIIR6U2yXBawc/Vfjs2hjd54djc7KDplZ0JEOG6o+BGQvqE9585lLfjx5uGWTPviue7'
        b'XnU/GjdAYXOlof7O/vzy54a9r1oqnjWm/MNH32h/PpD4ea763CnX2PdTbji3DTk9oWnxjKtfNa5RvmSe9aZyhtujFc3jnrfdRlZ+uFTftGpu1XNlHxRvdK9udl96QG78'
        b'IuNAZ2J60vCfc6NkXa8vWukyKDKmtMZHb1n1Y8PsAzHvng5YtPoP2pdPRB505leuvxd8d5rMr3XO0cXHNItTNOWW0Ifqstz8h5rKTc5TDn2b/MKAu4fyXnzjD/Ej/C/9'
        b'oSI+4M3P6vItvl+HfUQ+/CgO3OPf3PuZTU3qq3tuBvx1SOxiv0a/gw/i33p1ZsqHOz997nfPrh98ak3gFdVuO2nVzkV+yVvXuv781WTbl1LS/nlfITGzJzk7J5HDUBaH'
        b'Se6URV4cVCwIE94sc2hCrvW9MqR4Vu+rZSR2sHWxmb2/o80bTq8jJ2Q+tEgXfX/PG2hGkjYJXIjIMss5WjBcOt1Ezkcl+HsLAULMDSAH0bXuFpMWaFKjbjMVd/sv9KJS'
        b'tpF7+oV5R9RZnUGlTk1lrpFurTkP6qhC0BnREltaeutq52rbz63ZWF2WePhmzh77Umfq6sgbB3erM5qQCHW81xsM+K8hkTd69hgPXZxuRYQS2s8C+voHKhI4D8fSMIjR'
        b'e4n0nVylpNKWc4OdzkPEI0gDHNdOWxpsY9Jgz7F/9hvx24kOBE3olc2ZBeP+umvRXleXDwZJt7fk7z+V9H1rR+j35wZ7nFv2zWvpgY9Svvp9jfvNd+JVVauf3X/q0SIX'
        b'/1G74hqOr03/6Pnb9lnv39v+3HP3vnlmTsU//laXm5/86Hu+UunpUrNTYcsUxR7qMN0oQyW5AA2JiWzLb4thuVUEZ+AoXGFqqcgEWqRO3w6TmJjoTxqTRdwAuC4mDeSA'
        b'l5C0nCU3BwjE0fvKpJwS57DM2U3sBXthD8sMyJXFcKCnVF5EGjZjVgLnWd35CHSZ+2OjxXC29/1jMoUIdvvAccEyjpCt0GSKhnZof+wVZT5jzHTnOACOTfSNseHITajE'
        b'TTXUroaqbjX3+u9IG/4f9Efyq4ah1WvNVsOgBHJOdrwQKe3EfptZBhFrHNKj8vIusU6j75LQwuYuG7MlT6fpktATfAyN2gy80uLULrHJbOyySV9n1pi6JLS+qUus1Zu7'
        b'bNjbiLpsjCp9Fo7W6vMs5i5xRraxS2wwqrukmVqdWYM/clV5XeL12rwuG5UpQ6vtEmdr1mIXnN5Ba9LqTWZa0dglzbOk67QZXbaqjAxNntnU5cgWDBYqKLqchIxIazJM'
        b'CQ2a2CUzZWszzaksjnU5WfQZ2SotxrZUzdqMLvvUVBPGujyMXFKL3mLSqHuNWiDbyxhKv0+kFz96oV7SSLNJIy0MMNITOyPNmY30kMVI78kb6T0/Iy0BMNIIZ6QvQDPS'
        b'e1dGqmlGH3oJoBeq2UZ6g8xIb7ka6RutjPTUyRhCL9R8jFR5jTS3NU6il8n04tvjE6h07Ht8wg9z+/gE1vZPu+63fXW5pqZav1sd4j+HZvZ/kaFcbzDLaZtGnaCwM1Jf'
        b'Q8O5SqdDV8f0gIaWLgcUgtFsokUiXVKdIUOlQ/4nWfRmba6G5RLGsG7mPRb/u+ymCVnDM/QXy04kIonITtC15e7U5fL/B75ykDk='
    ))))
