
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
        b'eJzVfAlcU1e6+L03IUBYRUDcIO4EkggGUFARrQu7C+6iEEKASAxwk4jiLiI7qICKG+4LAsoiuKB2ztdqF7tNp+2U8bV2mbZa2860nbG775xzA4JL/2/e+7/3e0+a2+Ss'
        b'376c8yWfMI/9E+FXBH6ZJuFHKrOUSWeWsqlsKreNWcrpRIfFqaIjLD8yVayzyWcyJSbVMk4nSbXJZ7eyOlsdl8+yTKokgbHfJrf9SSdNWBQ1c75sVVaqxaCTZaXJzBk6'
        b'2Zy15owso2ym3mjWaTNk2RptpiZdp5JK52foTd1jU3VpeqPOJEuzGLVmfZbRJDNn4aG8SSezrqkzmfA0k0qqHdoLfBl+eeOXA0FhJX4UMoVsIVcoKhQX2hRKCm0L7Qrt'
        b'C6WFDoWOhU6FzoUuha6F/QrdCvsXuhd6FHoWDij0KhxYOKhwcOGQwqFp3hRxuw3eRUw+s8EnT7reO59ZxBzlEpj1PvkMy2z03uizGJMJI5wmF8Vre1OSxa9++NWfgCKm'
        b'1Exg5HbxBjv8XrpWxIiZOxOdmGSDq5MNYxmJG+EyqoerUArFs2PnQhGUz5ZDedSCOUoJMyY9ZoYYrmsy5axlCB6qR8Vw1BQVBxVQFgdlLCONMqGrHDpvjw5o2cf46dYN'
        b'xTxCEBaT5P9BkDQ3K+JskQgjzmHE2R7EOYo4u5H7PcSHPYF4hID4r1rbcTtYL8ypZMcaXzuGNh6dzs08wpF3yQbD2FCh8a7KLmgGYWhycuxz7BKhcZSNTV4n64plNNnw'
        b'VZ4Xc4YxSHHz+hQv8fduizHXPxrzLdceyCz+ljHY444GU61DHJfsgsePu82vHpkiNJ+1/Xa261BfH27OHfY3r9yh6UwXY1ERFuxYDOcxB0rHzvX1hZKxkUooQWfm+0bD'
        b'LtQYB5UKVZQyOo5ljC72k9d5PEFp2260gwilCZWZNFEPLdn/HC17Fu2hpYNAy2JvZ+aF5aEME5Cs+FISzFgUuBG1T87DCJT5x0AZFMfOjYxSRC1gxsUkeCgkqHo+KkU1'
        b'TLqNLdQxqNxCllVNhnNq1IEXR2eYXFXOajhuccftAUvRNTVqI+0HGVS8IHM87LcQgcZ6oR5HdtrNROi1PNpDh0O7Au2FKhu8IOyAaka1GnZRKBOTHBj30XKGcU2OVbDz'
        b'BD5O1bsxhpAowvH1K0dGMvrP/z5AZNLgz19d9Pgy+YvklWmxmltpql2+mkjNvWQ3bUaaIeV+crTm9TT5vCiNfE6MplF3mq3vn/5FarRmGbNLG6nJ0u0Sl5w4fypGFTBt'
        b'SZl8iGxh2HfTbsSfdJ6549IfHA8MZObHeny89UU5Zx6M95nm7O+ASSSPsyhDA/0wqznGAxWK7eBUgNmL4FOxdAimYwlUWrCulWF1DWVRM5ckZ7s4X7lcxBNu9Hpw+PGT'
        b'56Q0PitPZ5SlCdZNZcrVp5nDu6TUdCWlasw6Ms7kSHg73JF1ZF1ZO9aX5SXdS8hFXTarNQaLrss2KYm3GJOSuhySkrQGncZoyU5KemJfOcsT+eBtyIOsMoKs70zW/9CV'
        b'k7AcK6VPyyDC0hUu/pEKv3hUPjtq+EhFlA3jCVvEA+HUyJlarpfUiZ8iythw9IgyR82CCIsy1yPKIirK3EaRVZTTHxfl7oX7irIknsqUbQRUQxWWduUAOMIoLQ601QiV'
        b'K6AKK9bYoc8xY2VIEEzYmgvHrJJWCzsZlRfao08/sNXGRDT4cPzBL5OXPr83Zgfai9p2nKk6k98cObzgUn7UAfalNCJYjml3DCyzp94uYoBSzpoJYdDpFXDcP1oJRehU'
        b'dFRsvA3jgHkNB9cEWJnyNG5Tmnc5CKxNM2RpzJS3RLwZP0dWjDnLS3v4KqZ86rJJ1aXozTwZxBNLJOd68ZLjid/qxVAy3b+Hoe/1YSgxsagF9kNzN0+p51CsQNtZZvAq'
        b'MdoZjC5bBuBRCmhD11AdajWZQwLEDJfCwEmoj7d44r6x46B4FLpIeliG0zFwBve1CHQ+Gw8H+/uRLhHDpePPqwfROejYFHR9OTpsMo8nyxkZqJ8Key0DSddVOA6b4TCq'
        b'JJ0cw2Xhadge1FmIzqHNqBwOoQuo0QRtwWRDlM9AKx5+kC6cOxqu5qITtNMGd25joG0ZQ7ugZjzsHDLQxNNpeNUGOILOU6nGbvMCnFqGGqDVEkgAwhYOWlERdArdW+Ea'
        b'akWXFtNuDBK2W9AGe1GDsPAhuLxSA80mk5rM3cRAEzq2SMDzAtq/NkJH52EKoH0MXFyziJIUtjsEDcPbki5b3LWfgUtGOECnzd2ItoRhW9hqcpTi7eACG4T2TKfT0GWj'
        b'LbRAuQNPGYFOMtCxEHUI0zZZoErsAM3BpAv7dBFcRDXURI/zTRorc5COI6jDbtZeAVUWD9w+ZbAjlGY6QDtFGwpYFu0dTBfzQJcXw0G4YILWXGcCxBHWf0os7VqQDAc1'
        b'c0z2TnCeLHedDYFy2CeAtw9dTIc9gxxyLNDO4M5mdhQ6kyXQ6Yod7FyAakwOvJnM28t6w/kxFIx+xjQFbDeZocOB9JSz/uhCGBUhObo6HhV5mJydMCVENuxk1GimU4LX'
        b'wjEsC1dxjzPLiOzZiAlwVqBsFVzLDEGncU8OQeoiq0Kb4SKlg8PCNKib6eCUjcrEjGgEG5HkKDCqZTU6A/vRQSIeWHCyGWiMWC2AXRgRGYG2YiEOkjBcGpHvfLTVQi38'
        b'OdQBV/zQWcJ6G0EWW2DnQgogHDSOlw8zQTO0uhD6NbFBGYJUjEvyUKBCE7Rbe+pZNSq0yGXUr12c5cYGcYzvnZCy5LicLzNpo0O6BzuBY7zuhMQuuzl58lDaGJjpyU7i'
        b'mAl3Qu67fxi7ahBtfMXixUZgc3En/L7f2on1Ftqolw5ip3OM7E547JrhPp8PpI1TRg9hIznG9U74rdWK2Uvn0saNqT5sLMcE3AlXeLt4hITSxgdpMnYOx9jhkREP53r7'
        b'CP43Zjg7n8AZXuZ4YEyMO23cJx/FLiZwht96zmGo82ja2H/waDaRwBkeK3thaoM9bXxngi+bTOAMVfCZ02bE0sYfvfyxe2Ai7oQaXH0mSSJp44cjlWwGAT401iHRcbIX'
        b'bWyRjWUNHJOMG1e4z7ifTRtHrAxgswlGoYbEE/JD/WnjoOVqFpvVObhRtXH5Z960UeQUxK4haIbeV383/I6cNqqCQtj1HJN9J7TM23vI1mjaeHjDBHYzwT20LOJgbLVG'
        b'QDN1IruNYyLx7q5nXD3W0MZhXpPZIkKQUMdw16DBa2mjZ+AUtoxjMu6ENqz8Z+QggZ6jYiPYHYRKoQ2jIjJGJtPGhpzn2GqOWYxB4m56skG0ceDgGexeQrpQx8yfDEkG'
        b'2vjpiJnsAY5Zg0FaF55jEfj+pUcUe5jQMzjWY19Wu42A0bI49jQhXXBsbFLyMJ42Th8fzzYQ0gXfH1TtPkBLG22Vc9jzhHTBini7CSsm0Mb4dfPYNkK6YMVsVcZPU6hY'
        b'o8MLUCN0oOMmBylRPEcsbkaqqoOhLg+2wEkH3tkJ62o/drIlWFDI01AwPQ4b9lboyDWJqMnwz3MRVOj0EqhHW1KxmcFGmyh/NTscFa6XiwUxWXqTPSDCuE68vywj6s0M'
        b'2nhkwUvsYezT74w3jLwx5A0pbdyQ+Sp7XIRlZ/z9KJeQ15S0cUnALfa0CBNgfKzTfvFd4xPhtn13OBHBMN153qOkhkmz7wm9xf966O1qffWNV8LjqeNVG9FpVDobp1+V'
        b'UByF6qA+TgXFOIb0TBaPwW1FFIHO1RzjaEvzGse7XhOE0Ld5mj3zvGY0yWscZ5vTGeo3h6WgppixMVAxGwdldrBNha5za1ErXKdkRjvRQVSEWv3noTYSkeNsCHu782Kh'
        b'8zSqMPinM75KPygai0MXx3SRC6qOFsxYE5zagFox+GHYD1/Hz3NwnSe0o7AMl9owDSKaTil8BgRYAZxvy1xUe5MUTfE3qZ6hoZjOO04dQHbb5TeA0axE54SMtTkGjsSQ'
        b'IBn/4VQ0BlWOjbJ1R42+LCMz2zhjI1lEpQvV+8MBNQklUXXyYCYFO+A6msiiinmJ/jjTomksTruixEx/eeASEZSFRlCbj5rhFNppTTi4EEa71FUQy5ND0Sk1aiH5SR0q'
        b'hQOMAWrQRUHKd0EzOqJWk7eHYGsYk47altHVwuA6tKrVOFDG/XCCWZmiEXZpQMWB6hDybu9iqGRS/RJoxKJE13Nioglk8QJvnLMXwVXRBA3sofPgSraNOoTAUAuHceSq'
        b'S1tJ56lgb25MEOyOxdPGQrk/yzgsxU4E6lCBnBNg3IZw3KIO4YjbhZooJg12hFhIqg47psnUIQTE/fHQyqQvCxR0bQccx56wFCctcTaM2Fu1jkVH4chyOmeyGo6pQ7B+'
        b'oAPzsB/LGDOBzkmzWexv6xWF+QHF8ahRzDhOFrnEwE4B9q2eaWrUTq0C+c+QPotOipmATkNpbDRJekRwLRkaWLR/HXaacZQd9iNNsVFRceSAoifJ9FXJ/eJUciUnRSd0'
        b'6CScXIi2oOO+vuiMp78cVePY2h1Ve3rA8QHoFMegEndXdHgUajX88PDhw0RfMWOe5ElT+ueeW8RQ2PyGoGr/eGWkmBFHTFzEovoxE+TuVJL8JKjA5MRbiCE6lOPFjkBX'
        b'TAJ9aqE6FVqdha526MTxkFwHzUJkc2YJOgKt1nnXUH4o6w/VU6hDHwW7cQCM51H7hZrdWR8oUQqBxVkttJhyLFISql7Jg32sDLV4Uo2FUgWU4SggF9psSLiWhcrYYagQ'
        b'1dL9Uo1YJFtxnxNZtNnThx2H2mG7sGj5zGgHZwdUic0szrFhF7sMCsdQ5Lzi5pjM0lwSGl5FJ9zYIaiqvxDGbN4YR3rIVltgjxuGowOdEPDe7IcDuFYzD20kSL0G5XPY'
        b'wQaosMapi2CfafU8aDFLGBYdYrCeXodLdLNIDZxzsHPCOYZoPDo5nI10RtsFi7IDnUSXcGyb40ig37cItbNj0KHhVG6HoNJNDs6O2PSKJppRCRtF5N5KLKzGGGsXHkec'
        b'Iue8BHZ8fxyDkxXjMYl34B5oIb5lONq1lp2K5bmdwuFuMZpy6Faofe5I1hsdwJgR4IPjYLNJKrBsF2pC5RjrRqviLYxa4kC7RG4u6BIbAOVLaXsk1MA2qMLao8j0ZRTo'
        b'HNop4NSJzmtQqYs0ZzWLw3CZGEd0qJwLF6SjDVWgbd1YQRGLsTqPdlCs7FFVTi+pKoRiVm47kQIey0zsAW86dLIynMEKLNmHtmJD2yNucHY8FreLGkpA2TS065G0taJd'
        b'rM/4AAHGGrQHCnqxMg1dZQdnWeg0lSecNTnCgV6c9PQTTGiREhuTUujALthigy0eOiRGl1msgQWTaAY01AUTrzQX2h1RsRhr+lgxRhEbrPZcikboOs9H4rgX5xfLkhwo'
        b'6kYtutwjdHaICH+tNcfBG17IeSSq++EYO2RCsNyZdva3RY0OUntowdwJQ3XL2VnY8u2ge0lWbTBZabnbES6zwwajMxS9CDir7FHrQJyujICWpbRnJOpwd7CjrJbipKGe'
        b'VUG74NxQPlzaCK2OwqymmGR2zKhsCsFz6EQill9HnnScwM5zLzvGSUh/MrGOtpqwZ6JZTN0kLNsj7cQCUuehfB1WaQd7kvu0oPx+bEjIKiGvLcDWutKBhwtwQUwtyGkD'
        b'q4qDSip0Spym9GjSXjs2cqoDbZ+vwFIFF+xzJIxoTPQmNtRrPAU8x3MAbcYBmO8KOMqGYWNVTEEQ62aaUHm2kH01DYFaVm6EAkE6zizFKTe0Z7vgRAaK8Ud2NBagWgs5'
        b'IJiL2qAdy0AVqlyNG8tRCWoMwTlRDezBCdXuRSwzYsVg1Cz2yJkv+JitE3ASacswAdNx7hoAZQ6WeNw8aAm6jMfvgT2o6LF1qnHrDrx+C/5/NTqPU6ca/HkPKrSHetjT'
        b'bwicRmczVmLjfgkdtsdyUgCHBV3IRwdiexG1EGd0IRFYKwcKWnl6Qi+q4hiimVWNghqrk/R3gS09BIRL0MGGhiZSleVw9tbSQ0SscNvYMFQdZiFH3KgSDg5xgPIY7Pci'
        b'41TUV/lDeVy0ct4iOAJFsxN8VXHR2MVBeZR8YSSOOubBeWgzLWJMHuSAtNG9+6DUFdW4OYbBBbqlaKq5F/l3oEOY/pdQPQaVePwcPOF0jErpF002bhIzLgtNK0QGdBHl'
        b'C8cQ59agfOIuy4V4wA72ag0cqjFPE9xJCToVHgOnXaAiUhE9WylhHGKwJqiWCWHcGT2q71EcVKJihwVNtpCLDthtD53+0XExSrIvjv7c0KEoVCLCslyLqvWjdy8Tm17D'
        b'Mca9kzOXz3813n2qe+OiN2If3Aookd4q+iGi39y5rjNyYh01d+MHqGQ5OZ+80FabOmjhSb/A+Ni892O0i83fsYoyn5TEH2w25sd8cuYvTv08Fyzf8PrVU1+fnbjKUHzr'
        b'/noTku5a/tHxTeH9F+66J513fMon9re+X/tNSaJ7ygMbG4/PvsrcsPPlj94r2TN/bOq3R+a9OXIxmzWm4cOEEYsWerqNj/7jxYFZl9rrd7jvDj801cx/fultzzD3wJXZ'
        b'FX4Oq5yCtTW/tA16pfGa11BGL/rxtZemF5g/lv2Y/3nt4jR+PLprGJI67u5HQXcDD7gOPFqYN0x316JamLx7yd31J8xbmuNunPQzhDW1NbJ/kYwzRR959d118o99fr69'
        b'rubmjBsJC2uVgUmLkn/2br2h1e+wNb+8T/7RPxpa0pYunvxV62eLNb+enfRWomyO9qqqLflCwqXO765euT3A/KLNyMTGTzteeD1zUcc/OmcucrjUeDBH2uWX8PL2dzoH'
        b'D5aN3/hAurzi1qBFg//Z8MaPWQXv/vBb3tpNo2d5f2OZ4ff+X062rP88auvk5V+WfrRSd+zPn51P/TbstQHjEq4Ungn7q7ryhxcjvM99uXj8ec/zxhTlH5VLj/5FlB/V'
        b'z5x++P17qtUzXu30WfvBX+oihv7yS85Qae146UeD9JNd7l5b5e4X2JYy+LQ5f+Fyu0ktR24uTx1x6KXKROVX+0Je+vKLMfP/0D5Pu0x7t6s9TmMYV/6TV97mFV9+WvrO'
        b'pe0r9x8dOPf0yqOf//CXN4MKb+1vm6Y5sn5T4f6/LdNe/+bmRs3d8YnMA9fgt192yX6tf+L8pZ+c/WPRi28kTnw3vGL+myN+aJSl33phWfCoG99W/XL97Dqlz8S0j19r'
        b'5/s3aSfWRo2uXNNQfCz+z85ph58rLXpj5Ln6rxXjSpd4v751WUrTtydPqO59ct351vaBccMrLJ+57Fj7j8KozAmLHpY0H7/587Xxsw9/1jj+olvmkK8SMr54q8sueJMc'
        b'/WGKwzZ5cuJYuRM9ws9cw0PpdFSliMcxKFQqcJCNzmKzOQbtoqe6XKTMXxWl8JNDaZQK90MxjrBk4hWj7M1E5TbhaPyMcMQvnO8PxoFmM+ycQc//YyWwx1+Fg9xivK4c'
        b'GiSoglPCLh+z1R2cgOMxCt9IrHRYl9HZZGjh1s4cbiZG3Md+SExUnF+cLU57YLdEzNnBVnTQ7EPcHGpEheS8Fi8LxdgaVIqY/hNtYY8I9sMZhZl4jZSZkTHQgCpmK7GH'
        b'Ws1OdUWdwiF1PTqMavxVcihRkLAPlUlQA4dToASzEOoF2EFpnCIKKvCHo2pJEOeMLg4ye1NPiTr6xyzDoWMpTtKiSNCOiZXK4U0vo0aKL9qtDvb360bYfiLUpnGozttg'
        b'JiGG77AZMdhqYRuqjCbXBm5wcRQqFuFo6Phwuevjh+P/1Yfc/l+b8+gw3k04jDfzGqNJI1wc0zP52/jBTJOydqyEdWcdOTvWkXXm8DsRaXNjpSy5i7FjpfTlxkoeismL'
        b'c8Wfuv/we85ZeM9JbSUs91DCOeJPnpwrXk8sEdPbHE/8lOA/L7y+J+uMW9zFYrb3H9lDTMfgT99KXN3ozsJsZ7q/FO/rjZ9u5MVJcSvuJbvhdrKylELsSeBgnX9zFEtZ'
        b'3rGbDnJRl2Nv9HvdNPxrVJWzvFM3XenyzzHd9xDXh/S+h5CTEBJVz7beQoyVJ6MGnDv6x8eqBAn3lzCzUIMtqnaGWjkrpCXH4Jo/9rnFMVEKnPGLcUC7HzW7PnHAQyCg'
        b'5y+RDD3gIbfWzJP31mlOPQc93O8e9IhoZYL4H6vwwlJZr39ziNyYZJq+1QW0ZGFttk4WNz80KECWxdM341R9pvb5EGWW8TqzhTeStQx6k5kskaIxZso0Wm2WxWiWmcwa'
        b's26Vzmg2yXIz9NoMmYbX4TnZvM6EG3WpfZbTmGQWk0VjkKXqKTs1vF5nUsmmGkxZMo3BIEuYMWeqLE2vM6Sa6Dq6NZj3WrwKGWPosxS9VBRGabOMq3U8HkWKKixGvTYr'
        b'VYfh4vXGdNPv4Db1ERRrZRkYNFLNkZZlMGTl4plkAYsWo64Le/YSSkzDVB2fxOvSdLzOqNWFWfeV+U61pGHY000ma1+e/LGZT87B/EhOjs8y6pKTZb7TdHmW9GdOJiwg'
        b'aD7abxpuMej05jxNhuHx0VZePRock2U0Zxktq1bp+MfH4tYUHd8bDxMB5OmDUzQGDcYgKStbZwyj5MQTjGkaTHiTxpCa1Xe8FZhVAizTdVr9KiwKGFNCqKcN1Vp4QqG1'
        b'j6BZBMczeIvxqaPJbXQYfeI1LdoMPMyEP1lWPQtqrSHLpOsGe4Yx9f8AyClZWZm6VCvMfeRlIdYHs85IcZCl61Lwaub/3bgYs8z/AVRWZ/Hp2L7wmf9LsTFZViVpeV2q'
        b'3mx6Gi4JRG9ksyxmkzaD16dhtGRjBasryzIa1v6P4mQ1Anoj1VJiKGRW1HTGp6FFr/Z/B6tpOoPGZKbT/28g1TuQCOtxZ719UY+9y84ymR9fwCoZOpOW12eTKc+y3ITX'
        b'On3KMyAmnsus6RauRdhz4a0MhmdImHXTR+LYd69ni+a/THdeh70oVrowGbYyeOQ86NRmpggbPG08sUUY+aRMXS9WdQOESWCATpNJZ/i9qWbs4J9BROs6ZMTTgX3C48ZY'
        b'jKk649M9pnVb7COf4qv7bozH/N4a6av7+t1ZhNtwPM1swpYqDQcxpPtpE7N5zABs8zRP33eOtVtnVMbzqmdB32fvJ+B+uv+3CsJjMUCfyc+MB4S5erz10ydGTZsa/2yx'
        b'S8ri9el6IxGpJ23IbGtfChVIrMCymbxuVWruM3W998r/AYEWhv+LxiRDg73NU03eLF0KdGK1fopN+B8AjKgB1TNi5/rANR/3/L6yGTWrdI+snTUulvnG4+anyqmFz6Zx'
        b'0RMzFur4XJ0xlahlXq5Om/m02SZdtiasd2CNF+gV1T9lxjKjcXmYbIEx05iVa3wUdaf2zgM0qam4IVdvziBBup4nUaqO12tl+tTfi/DDcPqsWUXMJoZpfsZjtdZ9J4ZZ'
        b'85wwnBc8zTP0Hd3nZp1cBHgyj9+sxwtFrY7pIkbsFYUzwWRFwrpM4Uq6n60NYzfEnWMikmOr0jlGqE+7CLthN2rFaW8WKp7ITEQlfnR0RoaEcXSM5MgF9uywZIaeeLvn'
        b'xQSgS92Fq1p0YoKFHMgkeKJ9/vJe+arBkWasw3xsBg2HCrmjhRRUToE2lA+lY6OjZhmUqGRsr/PWQCiX+EPHBnoVE4fOoerHTmPtJOQwtnmxZagAcyNsE26U0cXknktl'
        b'0YQ1cIqel+cuNsT0ujV2FJF746nQTA+ZoUQHtVBKDmIiVNFKjrGDSxwqQTtQAYWTXAhPJqtHQVkMTsahcmw/2BYJ5SLGx00Me+fAWTrOAE2ottc4UshQTGoHRvrboCuD'
        b'JqGtsZbRZL39cI3vNW4DHJ8t3PbHx7GMHHXaoH2RG4Stz0FHeJ+tyW0+HjUy2QZK0MWI/gspwWMzc/1VUI73VEXHQbFCDsdRsYQZDPvF6NgUXqBS4TCVdVBUHJQsmaqQ'
        b'S5gBHuIAqEMHLDLCYgXs6sO2BHSoh2+eIFQ2w3lu02DYqR5H7uf3MKmwxZNScaPE+zEeTUCVmEnocDatdVg2YnQ25KvH2RACMBlRSbS1/xgJvTGBOlUAEwA70inH4TI6'
        b'M0LgJ1yFjl4MjVpKNxtrwvzuxVB0LYJwFF1Gh+WccPvYmgsH1FApQy3ZEoaNZVATqkA7rVdcaK9qtUmNWsiHQ0wmOol2WK+DxqwSJCFN/kgSNiXKJXTicnQC6tXQlqbO'
        b'FjFsDIMaUe1ka2lgO1xR95Op4bwNw84jl58nUQkl2Aw4plXD2VlqHs+ZjVk6czldzC4BtanzQtXQgmcsZFA7qkVVAomPoQrYn7larSa1B0eZTPt4qm0j4NiMuXZqNSHh'
        b'McYgRZeFiqh+nowi+QeimZMOO20Q9HgaVq7LJpaUkKPaGRiIk3CCjjZkuzIy5mcRk53s2DY3lpGLKEWXo/LlwkWKF999lcKhGqhF26n0YMxrUAm5ilkLzY9uY0QGVI62'
        b'WYtJN0EdOXqyYcRiaJ/OorrlkI/ZQe/gA6BTnePbQzfYiU5TPi13R51qrMp7elFuP5RQ6Z8I+wb11TtUjc4+UjxX1IaXJ3vrsDJUq1dBRw+RIR9qaVcY2o4uqgeh+keE'
        b'hnY7Wm+kX42uPUNfOXRg0iqB6qhgiYPeq4cXfqiIns7NgM2wv9dsdBhan1BjLJBNwmUmqkhzgvYe3vWDExTFOWi/8Rn67Q91EagZNdD5eqy3+6DeUa2mpTlMhr+KcjNi'
        b'vAszxPyRhAlIjr1uHs7I3emyIiztl2KilPEqKFH4CieG6DraK2IGo0IxOjEOnaEXZO5wAdpIvYk8AV1URokZe1sOy96FTcIF2ZUxQ7sZis6txAxlsaUg0hKXjvYK0uKG'
        b'TvUWlwpBmqAJtof6RytjPOGY0i+efJfGJV2kwwQpsIzC/WlZqKpvhROmGmqcSm4sB8eK0S5UBofoSHQFFaDKx6uhUMPynnIodHC5IKFbFjo9ZoHQ0QhigXbCPkqVJHQV'
        b'iqxuogK7G1S1oGe0n9YGnV0yjFoBZ1Q2lNaNLYZaa+kYtzYR1QnV4dexaB17oroKVaLTIigzolp6MYl2ZK23GrCTgb3sl9JE6bMSFc3tbb+w6SogBswDXReucBtzdb2q'
        b'hTAmTSzar8O6OAb3SocMsN55NgXg+agYawaUxJIblxhC6nFojyTKzl5Y6VzwxJhH158LppELUNiH7R3lU61F5t+7kgm1hU0WuaAGaKISMAgdDn1UHDUgmUVHx2RQGiVi'
        b'+1bh/6g8brlHusgFGrLp/Sm6iLaMfVTJF6fqn91TxzciXJCtgrlMt2zlqbFooT1QKVzaFqImOEqF0ol/JJPtM6k2RmFvdcqBI+bGIYFJSEbHBI9RCvvmEYHDGrOrl8Th'
        b'9nKrCdoAW1EntYin0XVsEbGKnKIWQgSH0BbYC1scyHc94AwOZVC5rVBhd418GYx8hQLOQo2SUerQSbrfOKizEXiwAI71UgDUCruFWmCDPeNqmMcxycmKzkki4bto6ITS'
        b'6SliH5zZLfUt2PLRoontCxXDMReqYI8tuXpnkqAaq6wQZZz26SXDE9CBvjKM9msE0DvWJMIhBWoNEJFyRhzN7Z9G17ZJM0GVizPW/BpbTPyUMHb+EmizzKVWpgYK+tzx'
        b'E9tRGQ/lCVAUhdvHQvEcctUfKdzzz52DWgIS5kUqSN0aNjIxC3IGzYFyMYManFxno+J+whcUzmK6VBPX4Yrye7sOT6Fs+p3npIy7622OcU129PWey8zHLom4huGwNTim'
        b'W0UkSQtRIeeH6qYKF//tE+eRFR1hV58VweqtNmNx2i8waJhHb/5cwWGMTAjCDuf1CofgMLT0BETN6BSF7ANbR8Yr9a8iZk6yQus7iKGxlngJHOwbbCWgbd2xVsxIywLi'
        b'j3wnmfqQCNOHfPtNpfTF+uJnLfRLINQtUiyMJHrijwryiCbO7UVNgZbX1/XD7qUpjhb2rZslZuxSQySkuPQb75ECSB5Qtrq3uvHYx3XrWx66ZA2JbENRB5bPCtQZREKi'
        b'uSR8OYGarcWdsagBd7ZGB2Wz1A03pUktahp0dMABqEKY/ztxalDdp4alyQa1pMwzo87xKehCMIsJLlniKpTjTJBhq9WaN75nPbxGPYXDBl2AC6jVFVU/gqMdtsvFgmEo'
        b'8yNfnbvgH5KDXXk0njgPCSVtU6AmER2H7eogCQ09dXDOVihogYMBarTdLWg13ioCB3GoGEd6NCY5A8V+qHUmlAbBeYZ6/xb/oXKWrrdkAtaOVehcUCDumUlKvArXWKYz'
        b'QtlpFFYDbDwqMNugMgHOO2HDciEiKHBOj+jPUy6c9zivsFLWSWHfWnSURrf+6GQ2OouhXTl5PbMe7fCmpnM91KNOrBQlU0NQM8dwngxuuGL99gl0QjPsQGdJnLAdVW1k'
        b'NuZh9Om3KI9jmp8yKcnX6ub5kttuYkIWde8/Gu2lICxS2qKamRstE/EUV+hAZx3i46BcudAqgVC8KDJ6QeR8ilEQJtWeFKzRcUpVfOxsGwY78/NSVAAtflhmCAYDQ+AI'
        b'/VZY2EQVo9KgGsFEd6AjUAcHsGetQo02xI9gLU+hwTfV+HIcbDQR/fSFyt76GTVb6D+9zNvqwWqn99HO/kJ5U3vKTFLo2U4LPTvsIZ8Nwraw0uJLOs/6xgqTjYHP9H7J'
        b'UENlzQFL1tleBUZ7h7GjocVIhWN2ONPLMy7xJp7Rub9lONlj+8DBj4VPcAJ2dodP0DKFlnvr7WZftzE14re5ReWW+TFZQ2a4fv3epNz3PvjHoP1Opawoh/vIw9E+TTap'
        b'zP4zSeSkapnzKN5Lvy099IjR+f3Nkhc0LkVvS19LPGqXM23IBL7iB3v8/HjbhO8sr3U1b3sro+P6b5ev1F++92W9WTno7zXXRh+QfTRyY8nxt2s+8Gi9c2/K6/O3BNcc'
        b'qOevzHs39oT63T+19PMKPmP5qC246tf8wMUzLu9UJ2xkGqKq9H/y+IobcPml7e6f1v/y1ivffunXvAvt3BstbzhdXlM+q1/xw43viWd811SlXn57a7lXyMYL/V4fU8s8'
        b'UF50v/3hn5rneu/e1GV3aGJ559Hzp/bb//Jg3NwX1p+8mR6Oak9MOvDyON3q2vc3nN+Q9rnH6rc3vzBg5afHdo2Y6n9pn9+dYU6Tls14vmS79+xRja8Hf/g3VfjDYcuW'
        b'5783NPvLWzW3/s3p66CLc5ue3/DybXm2/52v2fRXcvcOHjG8VbHgF+6fK85fTjz67rHj5QU3+4+zTEr/7djPn519/cNU7ch7h7e8yFs0LyqM7W99kDbUc1Xsg/StEpX8'
        b'p+ddkq/qQhK37nX7NFm96I739Pj+Uyo6X5w8Tv2Pl3XvbnkjLSUha6f3K88Vlvz5+zcfHG+7+1ZT22uNzymaStc+yHjvwVdl3jeuLvgx/6tva7+OHZr4oGZ5g98X0ZcO'
        b'lc45c+ir2A2Jp9RNHqv+/m8pYfBd47sJQ/+4JGNafqHxttuNWYsHzxn2/YB1v76W2lxYNuWVgQ9f8/t0hehXx+slr09973Ln2tOqjsSC1QMtXt8e6vCbWrnk6vZJK/bU'
        b'NL+aur5m/Yv9vvrkzRjHr+3vjDlVcmhfZsOBN8Tf3A7TfP524ierPwz5/q2CX9OdvxqQuer294qNAyb89tLNpPlFvw3/U9orpgWnKr4I/dsr//joRNLNl2q3+VTGjvjo'
        b'xWONMz++VfFe+4MbgzYeslx8Oex2eF5oUfuE/HfKvkpS3Hh+bMAHyp+Kvp4xeOmvzStHtB1J+ML2C3HVvito1NfS8Zv7553ZWRV4bM8yz4k2N75J/mvNsSHSvHcqr519'
        b'U/XzpQ38exPuL/mgLqngjSkVyy5X+XfavPiN3Pfhx6fnzLrzl+fP3DzOt+7N/aXz6z8uKVs59+9Ta3ZNf8f2dFnt0Ykrfr3RuH71K873pd9v33TuTzvnIKfl36s+uNSv'
        b'7p/funtO2YM2LXgQnxje8mDGkQ8mnlzydZjDVXQz01SQ56ivHPGb/YKiu5avPZ67fOu2synr8CKx7cQXR/8t/Guf2I2nxk9+/Rf/P7u4VgUP2OZZG1Hh/uVEhbbhQldg'
        b'eKntJ5+EftJV8NcfH959++NVO2//MGDBc2XKw3PkzmYSyWea4Iq1GAmrOFZydAodjMG2YABqF0cORUW0hGcuDl38/VTyKdBIS4Tsl3DYAJwPpCU86LqCFaqhVMRCJPdU'
        b'Q8GVgbS8yAauQ1VPxZMEx7FHZnNK7J9qaMlTGNqPk2qFb2QmNrrWoiduLaqYSQuMSJgObVDauxRruw2txkLHZ9PSJ7zwbjjzRO1TsoyUPu0LozDAcbzIYf/4OEUKKowm'
        b'hUx26BKXi3aF08IqIGFnJw7tSsYqGUaS62PhVOsTKXo4MG6KisGAyXH63l3s5RIgSu8PtZQ4k+AIqugVo22Ek5zfWBAoh87CKWjvLq2SoAb1Bk69FBppYdUQewv9arDw'
        b'veDccPrN4LUqyhg4CaUmaCVFVagxW+mH9mJXR79LPkksQpehSe7+/7s66qnFOk7/9XWe+ErzKnNoUAAtn1pB6nI24T83u15lTKSQyY6WLnGsI+vGCUVMUo5jn/r3vdTZ'
        b'jpY62bFetHCKjCXFTM6/SmykbO8/YRVnYd6z1hP+vpQMcGZlLCnFErOurJfIlXWm5V1idgh+upMSLM71oZSV0KIpvLa1oIp7KBHRz79KJXTXXx0lpNVOhGHiHDkCqZsA'
        b'GSel8OAXR8rCJBz+Y4fjFgmBVICXlHRxQhmZFO/sxbrj/kEYIjKDlJk5/yYRC9g5c91FZ66cM0fX4HgXTOH47gouMTmB71W59V/nrpzlXbv5S/d6lfCVNDGbmY6Rveu5'
        b'qK5e8h1kreeCSiWOvgKz0CmcY2eL4BI65vTE9/qJfESQFUneqyO/GMMs5VLZpaJULoGxz8AoudKrBFpmxc/g+Sz+Jx/hcoHKGm+tmtKlyjRGmY70q+Ll4i67pCRyG5OU'
        b'1CVNShJ+Gga/d0xKyrFoDNYe26Sk1CxtUpIgwI8eFFUSGHZh6GgZoB0nnFRfSR7t4AwdZgd7gqKSVwo//5CqGgt1EhtspTrl7Ex9UQwjNvnguZ8XnJxc+XI8RLhOTzeM'
        b'aW7d8Vpx/3fPf/Oz89SPb9hmy27za1p2DP8rEz4s5w+708pe8PlUO9B2209/XJB3r/43/sPCy/UOzdMr7ndMbddaCt765/yOTcHxn90NubTmlRkf173689Zpsuxv1G9k'
        b'j/jZ4hXVuXjjK2MCv47cWe48vDRFoX6wpKw0/7qDfura+vp7R+KK+Y9PhuT6net8M2X7yo9POAffC8r4+O2jcRHf8YWq1luBb3Clire0tR4Ll2gPOoW8n7J/6Or3tXUi'
        b'59B93897OXDMAf7Gjy9EKUdVz98d1bT3/j6+2icvMVv/renykdLLJ2JO/uGdjqDjp6LrDS8NhK7tr505+e0C14UXPxud01oXvs04yc54d8zWjak3VysStqxx/+BVF9Xy'
        b'xQfLWuRiM+H6wBXoYuYknHHgxGYCAxVOs6hdnh4OV7p/Z8PP0dDrdzbaZ5gJN8I2QLmDHykuxS4hzrIAGqzs8EGtYjiHrqISs4yIZOlArQk1RsYrF6N9vt3+ox/sIMdm'
        b'F2AzlnAq6G7/jVZWQkPpZz+o9cQya8jSpCYlUdNpJurhSYxYEOv9kONIdSg2lZyrnastTqiEP/Y/9e5HiaPVCP4ssRuyibEnZtiXmGkXjuUHdCsCVj4Oa8cja9Lvv4c4'
        b'LO/Vo3Zkc+KwhXrR+6re9oWECxM34byrlJwpwdYY8nNHOMyotGWcB4qGTkXH9XETp7ImHR73Vq5h6I1A560Rrtvf2pSW62ROObH9zpFO9MLKrxQnRvz452XPxwV33iso'
        b'qE/bcOH9m7mZ137ajR7mJiw+vu/DE3cv3jszattOufn7AwMv3km8lDMmcNzf1zjtPKZY3vrOoXt7fF48fvK+15/u7ZHbCvHJRZx+05/QmE0TNFscwrQMhuMcOYSDs4K7'
        b'r4BqVBozW4kzXzwO7UKts5UclsJOEU4zj6BTgqi2o525AnqoPZocSWJsCXpuIm/ctMVMjzEawhKsVeISuDyGFIlf20CDoNB1E2N6/bKTg3xoMAc74BjaS6ve4VTwwL6/'
        b'/DSPXP2cH4Au0YVhO966zD/ahmGhbkwMA3vR0U3d2uH9PxGN/CeER/y7+qQ36s1WfSKnIYyTXXfFtkixiQYmMfzAHnmXdYkMOmOXmFTudtmYLdkGXZeYXFFjv6rX4iep'
        b'vuwSmcx8l03KWrPO1CUmBTxdIr3R3GVDf8ily4bXGNPxbL0x22LuEmkz+C5RFp/aJUnTG8w6/GGVJrtLlKfP7rLRmLR6fZcoQ7cGD8HLS/UmvdFkJiV7XZJsS4pBr+2y'
        b'1Wi1umyzqcuRbjhOKBHochICLb0pa0JIQGCXgylDn2ZOou6vy8li1GZo9NglJunWaLvsk5JM2EVmY4cnsRgtJl3qI40W0PbmydeX+UDyID8ExZPTAZ5ILU8uvXlyHM8T'
        b'5ePJnRBPDnl5JXmQi16emGJ+LHkQEeTJySTvRx7kPIcn+sGTEw2enLPx5IvgPLny4Mk3unki8zwx9jyRTz6YPMaTh3+PQSDcse8xCD/O7GUQaN9Pdt2/mNTlmpRkfW+1'
        b'oz8NSuv7W3EyY5ZZRvp0qfFyO54YGhIFaAwGbOeoHJB7qC4pZgJvNpEqiC6JIUurMWD6z7MYzfpVOhqC8KHdxHssbOiymyQEG+EksKFBjZh8jUOQtWXuGGo79t8BveN+'
        b'pQ=='
    ))))
