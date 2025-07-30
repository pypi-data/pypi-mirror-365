
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
DATEV module of the Python Fintech package.

This module defines functions and classes
to create DATEV data exchange files.
"""

__all__ = ['DatevCSV', 'DatevKNE']

class DatevCSV:
    """DatevCSV format class"""

    def __init__(self, adviser_id, client_id, account_length=4, currency='EUR', initials=None, version=510, first_month=1):
        """
        Initializes the DatevCSV instance.

        :param adviser_id: DATEV number of the accountant
            (Beraternummer). A numeric value up to 7 digits.
        :param client_id: DATEV number of the client
            (Mandantennummer). A numeric value up to 5 digits.
        :param account_length: Length of G/L account numbers
            (Sachkonten). Therefore subledger account numbers
            (Personenkonten) are one digit longer. It must be
            a value between 4 (default) and 8.
        :param currency: Currency code (Währungskennzeichen)
        :param initials: Initials of the creator (Namenskürzel)
        :param version: Version of DATEV format (eg. 510, 710)
        :param first_month: First month of financial year (*new in v6.4.1*).
        """
        ...

    @property
    def adviser_id(self):
        """DATEV adviser number (read-only)"""
        ...

    @property
    def client_id(self):
        """DATEV client number (read-only)"""
        ...

    @property
    def account_length(self):
        """Length of G/L account numbers (read-only)"""
        ...

    @property
    def currency(self):
        """Base currency (read-only)"""
        ...

    @property
    def initials(self):
        """Initials of the creator (read-only)"""
        ...

    @property
    def version(self):
        """Version of DATEV format (read-only)"""
        ...

    @property
    def first_month(self):
        """First month of financial year (read-only)"""
        ...

    def add_entity(self, account, name, street=None, postcode=None, city=None, country=None, vat_id=None, customer_id=None, tag=None, other=None):
        """
        Adds a new debtor or creditor entity.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param account: Account number [Konto]
        :param name: Name [Name (Adressatentyp keine Angabe)]
        :param street: Street [Straße]
        :param postcode: Postal code [Postleitzahl]
        :param city: City [Ort]
        :param country: Country code, ISO-3166 [Land]
        :param vat_id: VAT-ID [EU-Land]+[EU-USt-IdNr.]
        :param customer_id: Customer ID [Kundennummer]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Stammdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D18014404834105739>`_.
        """
        ...

    def add_accounting(self, debitaccount, creditaccount, amount, date, reference=None, postingtext=None, vat_id=None, tag=None, other=None):
        """
        Adds a new accounting record.

        Each record is added to a DATEV data file, grouped by a
        combination of *tag* name and the corresponding financial
        year.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param debitaccount: The debit account [Konto]
        :param creditaccount: The credit account
            [Gegenkonto (ohne BU-Schlüssel)]
        :param amount: The posting amount with not more than
            two decimals.
            [Umsatz (ohne Soll/Haben-Kz)]+[Soll/Haben-Kennzeichen]
        :param date: The booking date. Must be a date object or
            an ISO8601 formatted string [Belegdatum]
        :param reference: Usually the invoice number [Belegfeld 1]
        :param postingtext: The posting text [Buchungstext]
        :param vat_id: The VAT-ID [EU-Land u. USt-IdNr.]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Bewegungsdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D36028803343536651>`_.
    
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...


class DatevKNE:
    """
    The DatevKNE class (Postversanddateien)

    *This format is obsolete and not longer accepted by DATEV*.
    """

    def __init__(self, adviserid, advisername, clientid, dfv='', kne=4, mediumid=1, password=''):
        """
        Initializes the DatevKNE instance.

        :param adviserid: DATEV number of the accountant (Beraternummer).
            A numeric value up to 7 digits.
        :param advisername: DATEV name of the accountant (Beratername).
            An alpha-numeric value up to 9 characters.
        :param clientid: DATEV number of the client (Mandantennummer).
            A numeric value up to 5 digits.
        :param dfv: The DFV label (DFV-Kennzeichen). Usually the initials
            of the client name (2 characters).
        :param kne: Length of G/L account numbers (Sachkonten). Therefore
            subledger account numbers (Personenkonten) are one digit longer.
            It must be a value between 4 (default) and 8.
        :param mediumid: The medium id up to 3 digits.
        :param password: The password registered at DATEV, usually unused.
        """
        ...

    @property
    def adviserid(self):
        """Datev adviser number (read-only)"""
        ...

    @property
    def advisername(self):
        """Datev adviser name (read-only)"""
        ...

    @property
    def clientid(self):
        """Datev client number (read-only)"""
        ...

    @property
    def dfv(self):
        """Datev DFV label (read-only)"""
        ...

    @property
    def kne(self):
        """Length of accounting numbers (read-only)"""
        ...

    @property
    def mediumid(self):
        """Data medium id (read-only)"""
        ...

    @property
    def password(self):
        """Datev password (read-only)"""
        ...

    def add(self, inputinfo='', accountingno=None, **data):
        """
        Adds a new accounting entry.

        Each entry is added to a DATEV data file, grouped by a combination
        of *inputinfo*, *accountingno*, year of booking date and entry type.

        :param inputinfo: Some information string about the passed entry.
            For each different value of *inputinfo* a new file is generated.
            It can be an alpha-numeric value up to 16 characters (optional).
        :param accountingno: The accounting number (Abrechnungsnummer) this
            entry is assigned to. For accounting records it can be an integer
            between 1 and 69 (default is 1), for debtor and creditor core
            data it is set to 189.

        Fields for accounting entries:

        :param debitaccount: The debit account (Sollkonto) **mandatory**
        :param creditaccount: The credit account (Gegen-/Habenkonto) **mandatory**
        :param amount: The posting amount **mandatory**
        :param date: The booking date. Must be a date object or an
            ISO8601 formatted string. **mandatory**
        :param voucherfield1: Usually the invoice number (Belegfeld1) [12]
        :param voucherfield2: The due date in form of DDMMYY or the
            payment term id, mostly unused (Belegfeld2) [12]
        :param postingtext: The posting text. Usually the debtor/creditor
            name (Buchungstext) [30]
        :param accountingkey: DATEV accounting key consisting of
            adjustment key and tax key.
    
            Adjustment keys (Berichtigungsschlüssel):
    
            - 1: Steuerschlüssel bei Buchungen mit EU-Tatbestand
            - 2: Generalumkehr
            - 3: Generalumkehr bei aufzuteilender Vorsteuer
            - 4: Aufhebung der Automatik
            - 5: Individueller Umsatzsteuerschlüssel
            - 6: Generalumkehr bei Buchungen mit EU-Tatbestand
            - 7: Generalumkehr bei individuellem Umsatzsteuerschlüssel
            - 8: Generalumkehr bei Aufhebung der Automatik
            - 9: Aufzuteilende Vorsteuer
    
            Tax keys (Steuerschlüssel):
    
            - 1: Umsatzsteuerfrei (mit Vorsteuerabzug)
            - 2: Umsatzsteuer 7%
            - 3: Umsatzsteuer 19%
            - 4: n/a
            - 5: Umsatzsteuer 16%
            - 6: n/a
            - 7: Vorsteuer 16%
            - 8: Vorsteuer 7%
            - 9: Vorsteuer 19%

        :param discount: Discount for early payment (Skonto)
        :param costcenter1: Cost center 1 (Kostenstelle 1) [8]
        :param costcenter2: Cost center 2 (Kostenstelle 2) [8]
        :param vatid: The VAT-ID (USt-ID) [15]
        :param eutaxrate: The EU tax rate (EU-Steuersatz)
        :param currency: Currency, default is EUR (Währung) [4]
        :param exchangerate: Currency exchange rate (Währungskurs)

        Fields for debtor and creditor core data:

        :param account: Account number **mandatory**
        :param name1: Name1 [20] **mandatory**
        :param name2: Name2 [20]
        :param customerid: The customer id [15]
        :param title: Title [1]

            - 1: Herrn/Frau/Frl./Firma
            - 2: Herrn
            - 3: Frau
            - 4: Frl.
            - 5: Firma
            - 6: Eheleute
            - 7: Herrn und Frau

        :param street: Street [36]
        :param postbox: Post office box [10]
        :param postcode: Postal code [10]
        :param city: City [30]
        :param country: Country code, ISO-3166 [2]
        :param phone: Phone [20]
        :param fax: Fax [20]
        :param email: Email [60]
        :param vatid: VAT-ID [15]
        :param bankname: Bank name [27]
        :param bankaccount: Bank account number [10]
        :param bankcode: Bank code [8]
        :param iban: IBAN [34]
        :param bic: BIC [11]
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzsfXlcG9e18MxoQYBYjME2XuUdARL77hXbmB3b4A3bAYFGICME1mIM3o1tdrxgO953x/u+7829fa9Jmybta1/akPQlbZMmTty0TfLaNE2b79w7IyEZQZz8+sf3/X6f'
        b'ZUaau997zj3bnHPn94zLPw7+psGfdRJc9EwxU8EUs3pWz21mijleslyqlzSyNWP0Ul7WyFTJrdolHC/XyxrZTSzvxXONLMvo5YWM92a111drfWZOL5q1QFVdo7ebeFWN'
        b'QWWr5FVz6m2VNWZVhtFs48srVbW68ipdBa/18SmqNFodZfW8wWjmrSqD3VxuM9aYrSqdWa8qN+msVt7qY6tRlVt4nY1XCR3odTadil9VXqkzV/Aqg9HEW7U+5cPFKY2C'
        b'vxHw50umpYdLE9PENnFNkiZpk6xJ3uTVpGjybvJp8m1SNvk1+TcFNAU2DWgKahrYFNwU0jSoaXDTkKbQpqFNw5qGG0bQpVCsHdHMNDJrRzbI14xoZAqZNSMbGZZZN2Ld'
        b'yEWwaDD9CrUkv9x1TYfC30AyACld10JG7ZtvUsDvwGqOka75VM4wpZGRowcx9gmQiDeg9lW4DbcU5M7FzbijQI07subP0ciZibNewNek+DF6CR1Ws/ZhUNiIT6Zas/Jw'
        b'JzqejtvzcDvL+GRx6EoNvqrm7IOgBHqMDy/LyYrMkjFS6cyxLDqCL6HDtHJYAE8y0AH8UINboLqM8cetknx0QA6VybJVeUHLbbg1sla1AIbUDo34oOscuoFu4jb7ONL8'
        b'FXwD74Qy15SouW6FDh2x4+srlCvsLDMYb5OgdrS1GMY6FoquVaBr6PBM1Ia2ReVownEnbsfbyJ0XM2ycFDXitpXlrLhsEvgb5li2UgI3AWrMd4ObYZgIM7YZUHYtBzBj'
        b'Kcw4CjN2HSfCzOAKM9L58F4wGynAbGSNnFHOnCJlVKWmWfZMhiZ+nSdhpCoEFUuV9WVmIXFphYIJlCZ4MaWlubO0LwiJ+YlSRhHmK2WmleaaB0GiDyRO0gyRfhHETPvz'
        b'wHr27UXvNgTl/i9r8oaMvw/fy17x+vUc/2mlse9YHsXMYmgyo/48YFfAE6PXnPfYfw25bT7OdDN2DaTHoYPoLACqLWpuWBhujcrU4NZCfBadLQrLzsPbIrVZmuw8ljEH'
        b'eE/OmOW22L6O+U4TFtt9gzBkqQ2+zsXk+l3Mzc9uAFmvxVTmW0iGPQQuRevRncJ5mgUc3lHLcBIGH8rHV+ykPD6Fj6A9hag1GgqPZcaa0Sb7AEhn8cHawhrrPEitZGah'
        b'FzPswZAajs4AsnfVow6YUBQThdtRJ+0AX1iNTuIufA8/gilrGA0g9QO6OfDNsPWFeXNxhwwWbSfDrWaHo71Gu5pkHULX8XZIvoMP4PaIHEDWlty5YehsZCbdjFp8VoY2'
        b'oZOr7QFQ2s+0GF33KoadPImZFLTWuDH8C8Z6BDJe3fvysjdi/FG0covubWP35qszCl4+3zZgSOhbQxaVXp8WXnjeX/kkfc+PJicryv4wZ1z00SuLv/r6J7FD77ySVFef'
        b't+t0woiRq/cZ//CD7Iok7e7fchcrK+d6bd0Way7i/nYh43zYiBBzV8Sa9xatDPko7NU/3yxacvFEcNrBr/0DDiT9q2Hj3794w7b4xt+f6H+p29HWOaakvrLu5KPLnyUt'
        b'+ex0UtCilPmF59Uy20gCJK/iHNwRgTvyNNlAKdAjfIAJwnckuAkfxS/ZQqHIwlHaiGwNbp6K9mXl5ssYX3SVw4cy0AUb2Spr0ANLBNqcqVVnR4ikJABvkNTgM+gaLYDv'
        b'RqFdvmT17LD1W6O48VXMAHxPgi5m2sQC6Apqh/VuxdtwuwR14L2MNIVFV5fhm2qumwtTWwieqn3p13e/nGW+GjTJYKlp4M3AJSj/0QLv4FdO6faz8GY9bymx8OU1Fj3B'
        b'S6uKoO4UBRvEKlgf+AyCP3/4kO8g+A7kglmLnLRNUFot6ZYLlbu9SkosdnNJSbdvSUm5ideZ7bUlJd970GrW4kV+kw1Eu5tKBudPBodVnJzlWDm92scQUnwW39NFZOOO'
        b'nCwNakW3TVGw5zujsllmPLoqK5Ghh85NSf5JxW9rJVx4wumBy+vZYgn8SY1MsQy+5Qam2Evv18QYWL1EL93sXaygv2V6+WZFsTf97aVXwG8fgbEaJHpvvQ/c+8I90BC4'
        b'99Ur4V6pZyll8O+Wz6Mrlf/kX7AZyyXiKMgMfRxkIppxMGqoL9AcSbMEaI4UaI6E0hwppTmSdVKR5lQ+S3MkvWiOVCDgUn8p87UOdv+0UlOjcSpjDH81QmrNh5x5b3p/'
        b'Uvpa2UelO/XNuo9L2ysu8B/B/Y/LLukqDbm6YLS14gwv/UvhkOVDlmxcviF8b+z0cTleM3b4ztl6U3Kmc8foLaP3bowbwSypDHjzR1gttxEWuh7tRNsinPwuQs4EAP++'
        b'lSppwC0rbITHoX14PzrcU0QSgx4wykiJl2qOjYgOi/EpWw5sjH2RuSAJqOWMArVyq9AOdNw2BLJfwBvHE96ck4UuMswgdF6ezIXi5jl01+Jz2sGorQC4vJRBp3CLDB9k'
        b'8b2h6AZtGd3B1+sjNLgrPpMKCAp8g0ObUROCHeeChJJnUVPqwMluRUmJ0Wy0lZTQXaMki18cyJKPnJWyDQECrLWOUsJukXVLrbzJ0C0lslu310reYgUxz0KAY/EWsF7s'
        b'l2C6xY9cApzbgHSyxLkNTge6bINe/ZVzLsjuRC+tiF4GTkQujjI0CSAXR5FLQpGLWyfxhFxMH8hlnwi/zYZZvrgDt6lSAZZtUXhbYSZuI2CbO4dwOGYqPiYfEL7e+MmH'
        b'O1g6DtPr9z4pJVj2iiEqKEKXq3taGlheaTCVSVtj+Jg65q2XlQdH/egJc/DPigk6tVpKQY47s5IAI3Kn4bMuGDHS10bIAD6Cr8YvQjvwdSDE2/A2raZWoLjM0HVStMWC'
        b'rlLMQO3KfAEz0LlMKSMgBnqM7tgo5z2KWyw5BRqW4WrQ9pXs9HidADvOIxoAsavgbUYbXy1iAqFVTJkPq2QbgpwwcRYRmpJSyHZLzbpqvjfwOcsAJ/Ap3APhUu6E+xF/'
        b'V7h76OPfRlkMzwX8CPhdsg7vo9D3DHsQlQ9R+AfgrUbp73ex1lio9M3oSRQB9AW9UOBpKdcaa4/+dfTJaGlcrYFhLlYpSpc1qSUUCYYMSM0R2gcE0KKHFAd8cCtFgkWz'
        b'8IYeBMCN6JQbEixGXQJ5uCGZ6CAPgAFou4wgwX58WWRrfW98gLi1N8QrnoG41R3iMgGcBLDdspU6k90D3CUucB/oBH4QQ0Q9B/D3B3oGvrM7z/s+VgA+EW1Zg/Q5976b'
        b'NseKTbqDX5ZvJ1t5fEY0UaeKcLNGo8Vb0dm5mdnzcXNBoSA0ZoL8qGUZG37oLV+JmqmQWYsuJ/XCGLSv4RmCkZVlLJdFcNYCqDJnUOonpR8DxpgM4YPCdZk6E2DKhTkf'
        b'l9bqmnef48/oPip9vey1Kf8wRO0M02XrzukCy5lXB2dvbvzhvuuLUjesydgavLVU/vogpn5pYPFqOwiAhEvhR942V+lMkM22ApO5OCVRoDnXylFTD8IRbMstXDVCZhtP'
        b'MrcA03jcm+LgPaiVIhzqRKdsg6FkQfQckersHeWgOstBiCTYuHom2hih6WFF4fg6cKNb6KIDN6QeBaUepJTba4lI18OLTD6i/BbINviJaCKUcSVBApvpwcRn0R5oUQ8j'
        b'ouhI1I1qJzruDnJFR/d+3JQsdzJE9VknGWKb2edXqqQe8VCSb9ye+ISlssx2uTJHl1nxFBDlx2WVhmDdGf7Mz7hrodf37g9dOqTsZ5/wZXuXh1btm3Zt8WsJ7T9tv/la'
        b'Qm6CMuG1ROWW2N8qR7QnTFsGnEfDJMQFvNfwN+A7RFKJBn29MQAdcEeDVWg3OiDIE22x6IQLPWHRA1Dh7uHT6yh8q9DZNbgtMgt3gP4kf4GDPbJpLHoEGgKpjDcaBvbI'
        b'MSDE4B2oMxRdRu2e4d4fdQIp3GqziJSJrDpjC2SDgTYBdfLvIRekiIPS+X0LDrAu4CdKpd0J/g43avRM82ou30J0a7UfkZUIqwPdwKekRLB1wW9lSckKu84k5AikUVEO'
        b'iFNRY6nvVoiykZXKP91yg5E36a1UBKL8kNJFio10TA4q26dO4VwhC1mUQjIFUlnBSVnxw/krlDKlLFBhJ7u1eDHjS5UIvK0B9AiFkisFvbirFzsk/6g446ZHcMVSIv3r'
        b'vQ5yxbJdjF6xXK73bmQbWdApfChK+3XLZ5mBZtd/FTyTLzPaakATi8qx8Hrh5xMyxydk0F8FLeAtDfYKa63Obi2v1Jl4VdwTMpGvlLm8rcHGqzIsRqtNzVGt4sl/AuD/'
        b'dx8sTk6N2VaTlg+LqwqbrrfwVissrdlWX6uaDyqgxcxXVvNmdZrLjbWCr4CrTWfWe6xn1tnwA4tJq5oDoKmBugtqLObnKeepsSreaOZV080VujJeneaWl5ZjtzSU8Q28'
        b'sbzSbDdXpM2ar8klg4Lv+YU2TZY+36JNm26GxeLTioDtmaKmV+n0WtVsi04PTfEmK2GGJtqv2bqyxgItNzj6sNjSCm0WHT7Cp82psdoMuvJK+sPEG20NukpTWgGUoN3B'
        b'ulvhu8HuUt1xU1ZHRkeUZ5U4EEjSqortVujY5DJ4VUyfObFpObzZ3KBV5dRYoO3aGmjN3KCj/fBif7xqNn5gshkrVCtrzL3SyozWtCLexBsgL50HWbKKtBsmJqkdearZ'
        b'PGAOPmmwWcksyZL2Lq2anatOm6XJ0xlNrrlCijotS8ATm2ueI02dlqFb5ZoBt+q0Qti8MEjeNcORpk5L15mrHEsOa0Ru3VeNpFQRHNbk26uhAUjKxSeJtaKKrJqw/JCY'
        b'lT49n+TxvMUAJAJ+Fi7MyijSzKgB2IiLT/eC0VwJuEbaEZc9U2evtWlIP0BryrRin+Jvt3X3lE7W3m0Ssb0mEdt7ErGeJhErTCK2ZxKxrpOI9TCJ2L4mEesy2Ng+JhHb'
        b'9yTiek0irvck4jxNIk6YRFzPJOJcJxHnYRJxfU0izmWwcX1MIq7vScT3mkR870nEe5pEvDCJ+J5JxLtOIt7DJOL7mkS8y2Dj+5hEfN+TSOg1iYTek0jwNIkEYRIJPZNI'
        b'cJ1EgodJJPQ1iQSXwSb0MYkEt0n0bETYTxYjb9AJ9HG2xY6PGGos1UCYc+yE1JnpHIAa86ANOW5qLUCQgfqZrbUWvryyFui1GdKBFtssvI2UgPwyXmcpg4WC25lGIijw'
        b'GoHdTbdbCUNpAGEhbSE+WWmBdbNaaQeE6gn81WSsNtpUYSLbVacVw3KTcmWQaa4g5TLwSZPJWAE8yqYymlVFOuCLLhUKKQxIzhxqVXVtrIeFa4phFEAwwkh1twyxPmSN'
        b'710htu8KsR4rxKnSLXYbZPeuR/Pj+24w3mODCX1XSKAV8nQCX6ZrDlIJSCc0zcavsjl/ACVy/oxzLWp1FhMAkc4DO65wSRifVmw0AzQI/Gk/JKsBkgjrBSrtdhvrfgvk'
        b'R2e1AbezGA02gjUGXSWMHwqZ9ToYjLkM0NYJcZsFn6wAJMoy640rtaoMgX+43sW63cW53cW73SW43SW63SW53SW73aW49x7tfus+mhj34cS4jyfGfUAxCR7EFFXYPHFV'
        b'raKgoe4RjDxlirKSpyyH+NRXnpOUecgv8Nwbkbs8pbuJYn3PoZ/8vqSz71I4tu+e3eS05ykGpNJTMTcWkNiLBST2ZgGJnlhAosACEnuocaIrC0j0wAIS+2IBiS6kPrEP'
        b'FpDYNx9L6jWJpN6TSPI0iSRhEkk9k0hynUSSh0kk9TWJJJfBJvUxiaS+J5HcaxLJvSeR7GkSycIkknsmkew6iWQPk0juaxLJLoNN7mMSyX1PIqXXJFJ6TyLF0yRShEmk'
        b'9EwixXUSKR4mkdLXJFJcBpvSxyRS+p4EEMheukK0B2Uh2qO2EC2qC9EuYkq0m8IQ7UljiO5TZYh21Q2i+1Iaot3mIw4xw8JX6631QGWqgW5ba0wrQZJIK5w1Z7qGciub'
        b'1cIbgAmaCc/zmBzrOTnOc3K85+QEz8mJnpOTPCcne05O6WM60YSgV5nxg1qDjbeqCuYUFIoCHGHm1loe9GFBmOxh5i6pDvbtkjSbL8MPCKd/RmyoENJFqcFxF+t2F5c2'
        b'RzStuFTuZXSJ6Z0U2zsJ1BwTUYp1NiKXqgrt0Jyumgc2qrPZrUSsFWajqtaZ7cBeVBW8gKbADj2ZAdQuVYyEuRv1tNq3FvbQvgem5Lnt3gWpialndVQgfKtEkZcupYHk'
        b'i4ss/I51+U10wh5L1VdsWr6asxD/NItKsDGPJr/Jwxu1wkKcUyzEAmchtnfhkQgxoVqIpbRbZq01GW2WYU6TH/useY94VKx1WCipeU/CsQqO46QxdtJEQR46YiUeHy2R'
        b'+LQXOitlFIncOvwQn/832vZ8ppeX19jNNtAnuv3TAQkEPURXy5ueEHPlE+Lb8NXQmYAU1SBpEKupStCDAKWNQIieEFNst5TIQ26WvQeQPr9akHJqKs28qrDGZIrKBDJl'
        b'1uQ0EKNLz20P4UtbmFOsEqoR4xohqVaj1S4kkDzXe2Ejzia2QEHoFzpKn68pLK804QeAECYQVFxv09J5E1+hJ7MRfoqWmJ7fsaLSlOZYDKoEECmRF/e7Q5NTCZKSqA/2'
        b'WK5ETZDK70QHhMKw42xUVxBboN2ZjFCA/jKaDTUqjWq6xeYYipiSZSY1n0kkxWI9FYvtVSzOU7G4XsXiPRWL71UswVOxhF7FEj0VS+xVLMlTsaRexZI9FQPBo6CwKAYS'
        b'cgTAEAGYp4mxvRLhRpXHAxF1mGdVdq2qxzwLiQJCO+ylWhUR4h2quGCH7QGjKjciNy3Dbq6ibq+8pQKoVgOhNCQ9fb4qPkXgvQZHEWIn9pQu4o2Q5aHBtGKqI5CJW6p1'
        b'JNOJIp5ynKjSV7XY/qp5zhRQqJ9qnjMFlOqnmudMAcX6qeY5U0C5fqp5zhRQsJ9qnjMFlOynmudMUi2lv2qeMym4o/uFt+dcWrF/ROkbU2L6RZU+cmnFfpGlj1xasV90'
        b'6SOXVuwXYfrIpRX7RZk+cmnFfpGmj1xasV+06SOXVuwXcfrIpTu+X8yB3EIbflBeBayrDpivjUqrdbzRyqdlAJ/voX5ADnVmk44YHK3LdZUWaLWChxJmnkhKPRZIkXMS'
        b'gjfdbiC2MieRc/BSyCKUt4chq8KmmxsEKZk85ANinGe0AWvk9SCE6GzPZD9Dh3tX7qHkz+ZZTPiWVRQT3HIy6SMfgw2kEqeuRTmJhgo9HhUDcaYiNwfWD5yGyNUGKlFX'
        b'EwZv442wLDan8TgLxF+b0WCs0rlS/2KqGzqNyq5ihqBRujxcdBWTMnhB3eCNZSQrF6BGnpZZBcmmb2nN1WAM44aedSZ7dRVf6bBuUyZImKSFxDkQ8Zd4TVkiBfGX+K9b'
        b'tM8h/lqIo11/wm8YXB54FH5DaVSDnMXbrbn5uDMqMJTKwLg9x4sJKZMqo/AeN/l3oEP+Xc66y7+75Lt8d/nq43cN3DVQn6BP1Ad2eOmTmmRNfk0DDRL9QH3wZpCGi6W8'
        b'TB+iH7SZ0Q/WD+ngiuVwH0rvh9J7L7gfRu+H03sF3I+g9yPpvTfcj6L3KnrvA/ej6f0Yeu8L92Pp/Th6ryQjMHD68foJmxXFfnSUA5/5eOsndvjok5s4cbRSfZheTUfr'
        b'L8xql88u1sBBSS96ddQK7/DWp1DfORkNugiEul76CH0krRugT4U8WZOChmQE0TyNXrvZuzgQUgfAmKL00TCmAdDHQH1MhyPCwL8pwCDTx+rjNiuglSB9EHW5SutWzCS+'
        b'2TMKF3wV5aNy+edIVglURwgLcish6FREmXpCHbQJjj0hjh09CsQT4pTzhDiHPKGoQ1DvCfGIeEJcNZ4Q9wq1V7ePTr8SCJalxKjv9i4HsmG2kZ/+OkGrKTGB3Ger7FaU'
        b'22FHmcvruxXE6dSoM4neGr4GI4h6JdWwmyu7JbPmz8svV4j45MO4OANNYZ4JS/Jukjf5NHkZfETXIEWzopFZ690gX6OgrkHe1DVIsc57EaOXUPdU6f92wUTcloH8yxLG'
        b'Y2zgrTT8yrl4RurgUM5re1XplZAKKoeuWtWzFqli4BWQFWIWEiO7xEXRmW29WiD/wtKBGtgctEitVU0n9YFulKuoH6DKXqsC6pmk0hsrjDZr73GJw3CCwfMohGzPI3A+'
        b'/PiWMSR82xjc4Z+qyqXfZAizo3IdueLArJ7HQngNofLAI7Sqokqg+4DOvMpqLzPx+gqYz3O1IniWCAoqtKTSQRNwL4xfZaoBHmTRqrJsqmo7qCllvMdWdOLky3hbHU8e'
        b'/qrC9LxBZzfZ1DTuLrlvWIh4n6qaIf5SlRPrYZjzmaOL1VHdVyuOPZPqwFarE5gkzK/GogoTPFiq8ANLAyjdfTUkukqlUg2LSCPQjIAjIqkI4yu0qoSY6EhVUkx0n824'
        b'bNpUVQa5UdEb0pzBaIZdA2NU1fM6GFi4ma8jD0BXJmrjtTHh6t5L9S2Ow0ohJKE+PLAhj53GMLWlyg9mLWXsJMzjBbybxB/loQtzcHMW7siJwi1ziDtpZi6Lj6txW2S+'
        b'BrXibblzM9HFzPy8vKw8lsE70FFlDX6Mz9CG3w5VZkuZaIaZU6rsbljN2AmtQRuH4G0eG8aduCUXOCJqcWsWNa6CljfXK5lCsd3QRQpthUTFMKWlkS+MS2LsxAkUXZVj'
        b'EsDjDJbK1GrCYyeTgBR0ScokLpVbxxTSsC/axurRXkMWscDfVaWRfxjWwNgnkzYe4kMp7mPbViUODzeT5iPJENvVC1wmje5afNG1GVbjZysGs9ZV0EzZib+MeO2P3hui'
        b'lbN+/lKJ0e43cYXMK/Dk0TenjskvnR57640E85xV0tdP7dxSMXbz+Jadm4e+cAyX4Oq26i+2LzpTePOcf2r6w3PnH4UGs7JfMQFN9wetKgr4cMGdjOpFwzK6/vyjtglV'
        b'ny8J2vbTf6yvu7c2puvVT7yqLeoBq56qlTbCfcx4N9qK2sQoxyP4BA3rYALGSwzoLu6iZYzFs1FbQS7AER9PcoCSZYbiRmmDAt2nXrkhRrTNlywmzFyd53DNDUFNUkXJ'
        b'GBuJqURtVnwD2sGX0Fk36LHMoNFSX+JyTr13ebRjeAQ6gfdrwjI1HCNH+zkN3ok32YjtER8ux5ehEa0GbcZHwh0AC0KXJLjNC98T4gU2FaNHEegG2qVV41aQ2eToAheH'
        b'LlhthNWW5KG7qI1EbsF8NuCzIpTkTNBKCcC0OdhGhDLciF8aT2ZNZC9xpATIaEst4CDxL90i16K2dOrCnoTvhZOZtUWGa0lB3AF/x5QRpKDKKvObwdF1xMdHFpBiHREp'
        b'gPYtpGMNdItelOAt6C5DVwnvQyfxLrFjVXpUj9A3FN2RorYydEsQJX2+R5xWj9xJ5AbqcUoCY5n1zBo5K2cDWYV4JRFkChpFpuBIjpxtGODgyM6IlXzHQKi3KdmuFkIM'
        b'LNPIZTq5pDOOcJgZTP8uqwqhVk8j0521aCMeAmuekOETr0tmA7NvpKtfa++hOl2bWfGP+pOS8axhlgthM2y+mu32LekRHhxutFK3letWTDLpqsv0uikDoB0radOlP0fe'
        b'VyI5F1tzsP4wYBN6TY3ZVK+GziT6mvLnHZhPiVOc8Dwuy2y4BDuG9NUooX+hkofuv7Vfg9BvQIm7CNFP54Odnav7FTO+zzC8SxwcvJ8BDHUOIDRdZ+WdTP87dVjh6NDB'
        b'7PvpcISzw7F9CgTfoWsR1IoSUTzop2dVT899ihDfoefNQs/KEheJop/ex/ZA+lukDg9jcAsuoOFtXBPjDG/7TqEFjuZ6hRaYXpsmpXGxO8f/EKUJQWuVhqfMz9t/2v47'
        b'5cvKg0ZmyjHpWyF+ao7GFM+cjrYIhBm3SMa50+U9dso1howf4eAGFaZniTLag3f2F3PmVUK2j2v00Xr4TGwIdCFUtEAfHv5cH879C+AygQCD+NYDGdzAvOMWa9arfbVP'
        b't5e4HQX/fbnVZuF5W7eitsZqIyJxt7TcaKvv9hLK1HfLV+qoKulbDoJ5TbWgYkpsuopuWQ0guqXcVwQEGZW/AxgZBK6+Tk3Rzxmh7y8chmDwF+Ht26wEeCsB3r4U3koK'
        b'b991SlFfrAB98TcyD/ridL3eCgoBkWr1fBnZavC/XPR/U/HUU/85VEaq0FBtRKeqtFfwLkoarIjVCEqOSohkIPqWlbdpVQWAzr3aIXu+mjxhMVbX1liIbumoVq4zg8JC'
        b'qoKyY+HLbaZ6VVk9qdCrEd1KndGkI11S+Z54T1q1ZKZGYiuDTSU2KepIpM1ebUDTdqvRXEFH5GxGFU6BFf4cK5IhzraSWCx6j71X+TCbzlIBfegd5IfUVxHrn5XoG9YV'
        b'drK6ZRZdeRVvs6pTn1+NF/A0VTXdjX+oltDnncv6qkZ6TlXRCIYl3xrH0GcrwrZIVRXSb9US0auuz/KO7ZOqIrZLABVVL5e4etX1WZdsOFBM4apaUmCx9V1O2JJQVPhB'
        b'+4hUZRUWaOJiEhNVS4i9ss/awj4GlXN6kSZrpmqJ+BBwWcQS1yiNvjvv2f5EiRZuVKQhV9/gPqsDwYDFrIStAdvVWm4x1tpEpkXwlARX07013WStAfzl9R71f0AnUpow'
        b'GRM9PocCW6uaKRgB6BYdU2jTVVeTcDbzmD7NAXQzAGLBAGrFraU30gN8dLCsdUZgZvwqgLi44Xq3Q/7l19h4YZvQzc/bKmv0QEkq7NWAaDAWXRVsQNg0PKxOOa+qAa7u'
        b'sR1hSmTTUOuGVZim0eoyJK0qA4iagyB5bMV12xFbCKA6OZ6o3AQTFk4msvKea5aKhxPVlNORC49HJlXabLXW1Kiouro64ewJrZ6P0ptN/Kqa6ihBrIzS1dZGGQH4q7SV'
        b'tmrT2ChHE1Ex0dFxsbExUTNjkqNj4uOj45Pj4mOiE5LiUqaUlvRjefB8GEJQvp1oTwPjiClcna3R5pO4vAh0NhK0pXpmXKGsciU6byeqwKrY8DjgkfgOE8PErERXqfb+'
        b'UoqMUTB3arynlUZ2FpgYeyokomZ8Bj/IycVHB4ga3lzcTE4VydbMI+Gs88JIgOhCUGfhCxg92okue4Ou3JRoJw4raC++gm7g66DIbgNZAG2u82JkeB+nRLdHCRaGzkUk'
        b'X0uOuCBRs9A0ObKEY8aiw6PQKSm+p8DX7NOg5ELcirvwddCd8+bj7bXuM5yDtozBzflQuT1nfi1cCnKz8W4pg1vRJl98El/D+6iTDO5YiLp8teps9AAd8WHQcb13NoeP'
        b'VOE9NDguQIvP4etZUD/PyjIS9CKLNrBoh3AWx6Oh43xxc5QWt0CnkehsNtHiWWYy2qKaLZOq8EV6Ms0iKWkiKpxl8J0gLpNNxDvwY7q+JYlejJJRhPqoSpXJg4oZYYF2'
        b'o1Nmqx/ejW+SbvFdkM4VS7nZqBMfoEcsoU1B6Cwp4OenhaZu5uKrEXinhMGbRg6ul6ALaFe6nchmIYW4zVcLbcDyZUXOwCdhkBImBN+VBqAtk4yKr8ok1v1QLvvvr2le'
        b'n0xOr5GVpk2t7p5wZeO9FYETLv0gJHL0Td/WIb/YsuH9wugVc15Is47b9duui6cnRRgv4/T/NhVlrppwLOH9rr2Jh7Iedv44JEA9aPXJ//7gJ7i5cMqcDyZGjH2yw3al'
        b'ccTT30olN2o3sJ1X/jnp5V1T928e9+in79wrfDsr+Ks30l77y792//PNe3/8nc+7tR/+zrchtO4F46p/MlNeD39jjlktF7T/VrQNP3KaWqiZBbXjE8TUgi8X2+gRVTeX'
        b'T80hQiZ+xLtaHajJISJOhrdlW+gRNIPQnlpibqGmlpy8HmMLbkqg8iraiI5aHTKtq0T7cBXegvehe8JJNodnTYjI12Rl5eVEou0gxnaoWWYQfiCNHZIohMleW4fu5kSG'
        b'ZcIgWAZdLVeg81w93o663IRS/+95aEzfYbE+Or2+RBDjqNQ8wSE1Z5LIWAU7iF5dP1J6loeCbRjolHp72hBtFX6C8LyQcTypW0Qui8mlmFzIYR2WpeSyjFxeIJcSd1nc'
        b'c4Cvr9BmTyPLnF2UOLvwc/b4grMfKsfrqGDvKse/NcFVjvc0I7V3t1JPPPpEOanbT5B+HbdyXTX9JieX8N3e4iPbcr7bl8gqICEShy5hDM5plvuIhJjYVwIdhDibCPM+'
        b'buK8Pwj0AaJIH0hEekOgKND7UIHeFwR6HyrQ+1KB3medr8sDoG1e/Qv0Oqcvnko4qug5xNZZJK5BKK0C3gnrBBIpyAM617P3iMwQqaqw1NhrIRdEZV1vXlRTXWY06xzS'
        b'STgILuGUrQpclaj2TkdOMkCnxturJaIB/38N5P9lDcR1e6USQAkpToPWt2gibvtRqC8kORrwKI4t+RZHzj67E/a70I+4xcU0QaI11xBDjYXKrGbPkmhdDREZjdU6Ux8y'
        b'75J+XFlBk/DszNrniAllEsZbVlNTRcZLUrSqPBG7dPReVVO2HAAP+r3nh4JmogElJ0bHiJYvggigvpHmlvS4ufY5CCdhTFXNt9p1JhPdGYA4K2uM5c7duMTFS7ZfJVAk'
        b'rO5goDF1S1w9ab9VTSPVn1HV3Pw1/y/QtNL5Or5C9Lb5/9rW/wXaVlxidGxycnRcXHxcQlxiYkKMR22L/OtbBSPySO/jWlTCw99ZibL4P0kCyXl0ym1SOWMnxxTNRY/Q'
        b'kZwskEEjsxxPy+a6qFCxJU4laj166B3vW09PdJ2SA+Iw0Z/2gthJdChRgbKgE4KCth/dxy052uw8kF+dDeMT+PJcj/pZG27zRqfxGXTUTp4d1UTh+9aCvALxxCLSwUK8'
        b'HYpvw82gSfmA3kHE7GZ8t3ApOgidnfBm0Hm8Bx0N8c2HNs9TLWaZAZ2zZs+Zgjuy8gpyyFFH0VJmSLoEtw9mqFI6YB7aZQ3Pw51hRErXZqGLYSwzqgJ3MDIZejyWlhlf'
        b'gR754tuoc54Cd3B4kyYflCyOCYqToGOL8SF6GBvaga6sgOVoTzA6H0mTk4duziMHeMagNtkq3IRuCArbadyFDlqz6aBQE27MilTjDhkTjE9I8H10CV2nwDq+iJv0kCW/'
        b'SpVnImIYOxEuNeiYylfOMEVMKt5bBKt1055AdUDcgRp9yULB3Hfg2/MXZoKi2QGK6U2ifLah83CXizszifK1NFQxexnaTE8ylQehffg6/MhiUAvam4UOwCiJ6DhuvB5U'
        b'cdDD0d6SGHxCSU9JRQ/RKRUmDkBRDDpii8LHfehYAxbL5QOFB+y5b0dpGQrCtVEKshQdonKeGbmAnDEclT0/DO0IwS2ZuL0wTA04kEkOFaYnCqvRLbpecrPfMtCEqGaM'
        b'tsC4jhTi3XHZEobFF1DjcgZfwMfwJTs5O3o9amJ8cQeFybweBMHnrIqe1XCuBbqEd0oZ1DTfe/EydJeepIY3SQJ79Ny5YXh3ocJdo50aopsu90cH11Do4VPp46zZmoK8'
        b'KIIx+VmRVJ9VwzbYjjbL0A3beLo96tB91BkhnIqpljO+6DG6vZjD11V4Fz1XN3NCAfdg8DY/plY38O1FhVwiY08j2nIA9HxdtGMIjhKATLglqiBvbpjYmqs/Aj6ETnM2'
        b'Jd6+PIxq+ZmAkBFavLcgKxI0fTnaxkVlZNActC8dP8yhaiBnQV2ok02O0Kgldnrg1nZ0LzJCi44X9VRDD9BGCvNZq2Y7qz1Ap9nk1RUUMLwCtbhNcFgKzA8fwl2mL7/5'
        b'5ht5irRsPSvQmvVJ8xnjX031Eutk0JJu3P3Fsu2T8/G0wC0VK3+08uCooH/tHIJCzqjn1XoN9Y/22akZrZ93zI4TG2cOmFs4xyoNf31364e/Dvnp6w+SjvzP65d2+JmW'
        b'zrP5LTYMzBkzeyv+se+5k4/+J9W+5zX1ZxFLgjL/eW/sP6d+9tfYkSf3/ikrIJZNSc+b23Qm9OM7pokS29mWvOPn39UktXw9YcIbJa+8ssPvNx8qPhpdefpE68ejRswo'
        b'ePOL5J+duCT545gXj//iFb9PImt3v7n6J9yLLa+P+WT+xnGT/3Pr6pNHNk+pPzD0k7N3F8zKeDP02ktplxYmbklt2hlbNfz1vzZ91hp93zu/Pqt228qvbec/3+Nt/v2w'
        b'UZPO6HZv+sp8/z3f5dLVzVr/YZHnpddf/GNm27/444NlIyxTU7fU/TTgN+PXbPzm7bOvJ9Wrlq39Sv5CHd5/74ugx0H7sp50fvbTURm5K079bbTajyr+8zNhTztMEZcN'
        b'PU4fA9Fp4Zi0/TbcmfOs94Noh5iMT8jwtuhR9OEZUKAWdE80RpjReVfXjxeWUitCKbCI5hythvhr4KO11GUjYIHENNlX8NfYuAjtiQgXnTW8F6M7+DCHTqWtEg7b2g87'
        b'oytCG99AiH0kQa9OToM6USc9/jF8dERObric4Zah23Y2CYjjIRvB1/K69eh8bl4kx0hz0OYJLLqG7yQKRo+90ORFYAsd+NJSyhmAjK3hJuIX8R7BU+UhvjrtWX8O0ZlD'
        b'g7bI/BZkCeXO4YveUC4VSKODP7k9FnxopStkwhsVVrLnNIRp0aUegLfr0C4JuhIYKizBMSCNnU5DiwKdR6dTufoRmn6OyFIH/pusLp7sL/7E0tCjiFMbTJHDBrOe4ZSi'
        b'BabHDkPOrhOsMPSOI/4jIyE3mJVTLxLiURIE9+RUYgXnT31MfDhy3zDYzb7R06totVEKlpMyciGCioWcjm/hycVALhVOa4ong43X8xxe7CO0We5suMzZUoWzHz8Pphsj'
        b'XIrdTDdnwl1NN31NrVwmClwksND9RHNZk1cTQ5+Tsk0+1ODi2yR1nmgua5Y3MmvlDfI1MmpgkVMDi2yd3NMTctL4qF7SnL8gzW1byVFRb8M8o9I2cjVTRFMPqKUMfKs2'
        b'ZFtMf5zygnDueaUF77aiDsUKCSOpxDf82eQF+BY14w4cX12IOopwx/y8ucAfL9jm4Jvz/RKjoxlmxGAJ2og31An24BfxVpC1ZsPe7ihKiMat8SBJKVaw+GjOQDvdAfd8'
        b'ghwtsYwsnB2GL6H9JnyQMhEObVCi62g3ahPOLefwfeG89GvouhSEwlOAoBNg2xweUoMvUJ4E+6lpZI42Oj42gWPk61i8cSQ6jDYEC6M5gPbZ6RnhWegaauw5JFyF9hhL'
        b'YkokVuJdFJ68fVbB/fwZMcqbvz/wzuxjmqB01fyyD2bsXRS6997ii8HjAg8NeapWjvx7+7r0qRtaWna88fKThyHXLAeta54mbw31CVtUvuMvcmX2r3+z+MW5P4+pfO/o'
        b'F9eCz7SWz5+WtenmvsO6v6lesfm1vnMnNu/VFT82/vjijr+tHO47SD8E//PhkZebu0oP3fZeOOfj6glf3Ev6zC/VXLXt88bPa393EiXe+eS1/46a8KOaS51Hxv6r4YOv'
        b'v/jP9Sbzzbc2ZbTUm7P2p8qOxX76WVm3NeXcnyLa/nbl0S9ttr/tzPjnwHcXFPxg7QvN34wr+fMPrgeNPPbNlxJbcn7r8N+rg2wkjCEqBp2iJ/J7EQnpAYeOs/MzKig1'
        b'DRrBOqgpkLBTOUBOY9fRUzIzVw8DVnJW5qSRhJSuTxDM2TfwHZANBErqk/QsLZX5oY2zqfcgOuKTA/Ry4wJX4zj1QbyILwqnft5Fl0Jz5qHt+ZEg7m2LQuekjD96JCnB'
        b'd/FhSkKXoyv4Cm7LoSe6S6Hi+ZEsOo72eAmG7I6kNPHc6kflQvvk3Gq8azYl0fgA7kQXI0AsfND7XHieFhlVMDkn18WXlWUGoYtStBmfHVaJtlHvRNBk7s/IwZ1B5HhR'
        b'F//GoOXkgUZruo1YsSOt+KaTsabgq71t/HgX2iqw1oP46nJyzny+izupnAkYKXnBgo7Rcy7xS3gHupQTgToE9urkrYu0wrxbcBPjylc4fBRdrZ+Nmqmz5eQVi53n2MOi'
        b'7Z9HjrFXwXTolryCH7PuB2iiTeZV/tFCzxeA728ioh3uLCDHoKLtHHo8sAadsj0fzf2+J827OdYI5+FT9qTvYU9RhPlQx0XqviglrInj4FtgVUqgzMJHShmW8OiA3AnO'
        b'jgpnvuMj56ScPzeI8wF25upWI3QvsCmvHgbR7SWYoq3dMqtNZ7F1S6Dcd+VJMgs5t9VS5WQ9Jif/oaxnOVwusuK5mJT1bGD+W9WH/48w0H+DF5aEeuVJv/qglw1BiKOy'
        b'OQI4RFusSTSRWHib3WKmedUqHTH1u1hcnstMrqri663QTq2FtxKvRsGUI9qmrE77vGjX8WTeftZ0bxIMYmQ4ZfU23oPpyclJ5eLfs07x9nCyFZpQB3m0h/egbaBtXsU7'
        b'0bWFwFiuovNzUfPcqTJmCNogWY3PVFKdGbdC8Rsh+CLuAkBqGS3auMROH9p1pqOzoNwfp7wWtS3U4D05Wq2ECUYtEnRWHkw59EY/gW9HL1BazdEahhoQ8Dm0A9111pOP'
        b'wbvLQI49iLfgk/h4LBOeIEsuQCfoq0TI6wEGoGsRWhdt7SJLs/LTSgUmPLtSZMNo/+rBAqu9n4C7qCY3A18AZY5NtoAKTNW/OyDf3y/EHWifP6nFoQ52OL6dZwx+/U3O'
        b'ugVK3No5Ja/9mH/jtMCZFXV/yl4xP+/LlnXstaGFG4+ZZ/zCam9eZpf/R1LdjMA7r7724G9byp8sDA8r+ssP/xFztevzVpT944z5S4tyP61tOTIkdGHi3i++/E1GZOGN'
        b'J0ebjnZV5OxPTTZOWR35yakZr3YXta75jXWJccrdDxdx/5GY+hQrsO8fPwzIzRz31sZDajl9MhqNNgDR7Xkyih/gXT3+frhZSwnjutnoAj6Cz7geAjxWh+/aCABD8dGq'
        b'CG0etxw/hsmeYXMW4XZaaznaNBzUKuHFFhyTG+fLA731nUg7LvVCh7zxBRencjdtITWQEt11S9B91aSIZ7lQ7UK1/FvoRR++hzprCdlpPe8KEUikSSoJpjJ5MHwTgkee'
        b'qwYBiXOhGmLV/O/ollgDl/efIUyH+3BMFLtQs93SWp2t0vNp6ImMeAY1eeJI3oYgd56ILu3zRHQJFYalv5WwHp429tAqQjasupXkl8nkSrWeP+CMDDxVlWVQhZNf4Sog'
        b'tVbBrk3oEb+KxLISM2+4tsFYGx5JOxIJo8WzldhKDvHTO23TOkt5pXElr1UVEFN6ndHKO4kfbYNOgBbXqQw1JiD0/VAyt5cMOCmZQngvAEhB1+dGZMK2mJMJskY27krL'
        b'y0VnizJBnmqO1IIUkIm3etWCvPCIHiSPT4PkdDcHNlJ2nha3gFhWijqLQFFvi5oLIocmjJzXkoNveaE9q9BBQTDvHAbKQBc6D9r+YBDtJCYWbVqA79LXJc1LRnsiQGtZ'
        b'xcTgY6sU+DGV/pfEzYso4JgodJqdx+D9QOuOGdcMPCizXoXMjNcDJ3dQx48tRw4Fh60v+4hNnhHwgx/KmJZYplC+iz37g5+N3hH4wrWrMdainUVl/3hasT4qzDdnuu9v'
        b'znkNC2qYm5m2u86u/01hbsrpLRrpyOlvb/yBf0frk7iZTT9nj0+y53ilBV1Yca7z6VsRs2/Znu6KPjY5qfnzRdPufGr91biEd6buON2i+M3HNWdW53864701Kb7dV6+o'
        b'N7/re/nQrc8rO0b5KRN//bsNfz2wqumzzyR16+K/mX5KHUBFanR0rJSuNH4RZD1pEosuTSwRLB678PYiImjitpBI+iYzBW7j1qLHsYKw/MhMjpsnxP1GnWht8UanOXQC'
        b'P4ijgvz0WSNo9ZacCJDY5fnccHQOPxbk6KMzskHiux0LINNmwYVjfPEVDj9Am0Fwo7rRZvTi4BxY48ORqLNAeBOA7zQO70UnqimFqsQb0UvkrW9RBehSJQnRWceFo0bU'
        b'RsVCM7qUSbiEWou3jcQ7IolUGxAtqViBtlB9wYDvSQSi6hMqklV8AKRR2vW5oYURUeRBggY0tD1aNQfE74gEbcHnpgkvgXiAzpEz3Tuhc7x5Oqht8kncYLxhqiDrdvng'
        b'nTkUU434IEFW72AOHcMn11LijG7irbOI2YfY9zfIyMqkc0MqJgt1702jr9CiojDw8dMS4ZVOWXoHSHZn0qGhB2gXQESOznCR6Da62Z+B5lsotguVlpId7O7oQj7egolF'
        b'QYNxgDyDlCqYTIIgtcHPSUVJ7Xy39wTUupPqfgbJCWV7yLcFLt88Q74bB7m9N8CtY2jcGcdsiScXGiufIDROaLcliaFmnGTyO4VcyBOePmsJ8fXEnG0hJnrLZGEGtPhM'
        b'IqQIjZLWgG6J/9Qy4YuDv4HPROUTB3x9TXlJCQ0c6lbUWmpqeYut/nmCloiPPXXQoaYeKnRTBkeXSVjy4H+7Ha5fZLGQp26/Z0TPHIVUyhHTG8MGj+NE3eVbr5y/RAkY'
        b'xbCDtEo2mBs+Z2iS/zD63AE3o4fh1izYgVZ/fwnjB/vt1AgOH0M3pwki6pZKdMkXnbGR6MmpeJMvefgyhzx0GR4rHYsf5v6b3mP0HK+y8cqnj7TqklA7CWgZzeCzqH30'
        b'ONxFJdniieE5WtB1L6Er0YBUUnyLXZGeQZ88BEfh/RHZMXgjsf/02H5CcAvNjkWt8bgti1Dm9jgp6LVt9XVcNizBBuPQJ5kSK0HBkg+vf0KDSj7S5+peK3t66iDcLTdU'
        b'Gp5Kr+4t3Dtv74F9PzDtCR50JWzGjjyvcp8ZXjMiusZJMifs3Xhdxgz/bcAv3/qrWkYJYiLqQDcjtOvGusYqnhgpUiV8D6ifSJaKvUSipMedAkW7jh96R2jRPi9X0zgb'
        b'LGQeVAS4aeeDTFzNDNwlvCJle6GOPLMV8pah+1M4Hu/sP4pFCYoXCDx8CXFgoLRqkCutGkeMuoQ2SeFqsTt3h7RbSip0y4UIMk+vT6ojSSud+E3qjuYc7W8QP791lSCp'
        b'a6ipdlJEWLYmE8AYmY06ooSnryq8RxYsxVvcsCdE/LZ+5no6RjQ5IQJQktNLNnsXS3ipXqqXbWb0cr1XB1csg3sFvfem93K496H3vvTeC+6V9N6P3ivg3p/eB9B7b7gP'
        b'pPcD6L0P9OYFvQXpB5K3zuljYTuw9MwN72KlmDdYP4SchqGPo3lD9cMgz18fD7lyGjcj1Q/Xj4C0AH0CpEmhxii9ipxcsctnF7dLYpDsku6SkY8+1MBBGvmWOL+FVOEq'
        b'FUq4XKXP/taPPhgAbfn0tPNsHX1i77Tvd9WHHRyoVx/kigfwQfwAfXgos3xgI9PI0rsIxx0tEUzdEIWIIgWsiZc+Uq+BVQuhDopedJ1keq0+CtIG6UOp02FSt3cJMC1d'
        b'BojM1FrkZn93VzQEN0c5fSeg3Gl1l/VrdX8OcuUjWN1v1sqofZ1ZuzzXf/BUIcA8cVUHM4RlwqZNWZV/prReSMyzrWG/5JhFgTWr096NT2fsMWTjHkCXQOh2DV130yaB'
        b'TuzAm3CbF1NYoQhcik/Spn63ZixDyFY0pxuzojCf+dAxzM/JxdgYlCSh5rPNnVUj2l/22xCtlByKPxXNLfnz05HKH0wMyvxnyISj6T5Luoxdn929Pv4nGROGRS4yTd4x'
        b'Mb5BNyc8eXDS4LNvjcg+8/ey3RlJoWtGtIcMHXV49cA/tk/1GnEw6xf/UzL7P1qffMmcORJavGGq2ptSoKVD5eT1OyBYdQGzkTCKIs7mjAGX4otAdtHlZHSMGp3lE7kB'
        b'6Cy+IThS71bi7eR5oxc++0yoOTqI99LHl2hPCL6URSLbC55dHlia8aGyylLRxhpiI+8BIuTVb3hEmEYoBWUGD5dOyl9Kw7tXoCPouvgqqA5qwW4nT/Ae4yP4gAQdQxuV'
        b'Qmz6RnRxZk+xPHSBYQao0T68W4JOLMNHhTcoXpodjtqicMsCdDsqi7wEWYFbObQ5H+2yEVNS7BoMknQd2ojOQDuUy0JraFsBsICWAtyplTMpOXK0x3uIQF2fW8TsCfke'
        b'6Uq1Y+Wsj0zBDqGh36LNlG0Icm6WZ96HKNg4u2XUSalbSnxcu5U9T7XMNd3eRnOt3UaP2vJsKZBZyGmfltXkso5xSJ5r3MYZ1Yv6/8JNAPUwvucNJZaVkEH3E906nXPE'
        b'dbv04gzsHt5zUGivGFcttJpFaMtzDsWvxHXl+hnSTMeQvhrp0n3vqG7t8/bsU+KEUj/dznZ2OyLLUdzhWvmdenUGVRO0Kak29hfanO3sdBDRMlQGS031d+tts3tvulX9'
        b'9Jbn7C2Y9kacbr9HX/ISW41NZ+qnoznOjkKLSFGHa67H3r6/db7XawDJP47p/RpAyhZelUqImD4tUFGqHJEiE9jOewPk1P8/Z0ypMixsOGMMP/lfUit5BWDYz9OI0Jup'
        b'26UP+0OOrvY1peGj0o+Yzw6EFu79Yeim0ORfMKU3ZU9+V6VmKS17YawKSBm+GdIvJcOX8fZ+xE6qgFG6Rd9g5qBbC4ic2TDAlQ583wjqwl7E5rKbsdJDJ0T1/DcpOr2g'
        b'1VtyEKFVsFrKBK4hA91g2jtkfR1dkJY/dZe/8r8UO1nzL4xrh61lreR5QMofjgkvCN6uf6UsV5erW274mPm8esi8IQCnOEb/q5BUedSnpWqOQsqGDixHbYnoWl2/oApG'
        b'7VRlSQkPJ/afcI0Wb6ggWscmUFnO5PanPASUUGdiYwNfUmaqKa/qed2dA6JLG0JdFtq9tNtbWGXUC9aTHtHOuBky2uCyqBdwz7kBt+8+nbvRAV8yc8dbWSUAYcn3UWVJ'
        b'o72fI4keGb/1+ys7JPotL2ZO6fof1oPERywwK3LQI3QeijaA7HeMaUA70DbqYYkOhbDoPMxv9fRqZnX4EDt55B6H9+B7gnhY6eJIWhSWr2GZeNQi958VQPuKK5Exk4YN'
        b'pO+W3jxoGEO9Cj8LzOd+mJ3gTb0Kh3xh2MfYCarjQ16pjpOOlDSWsce9UMQQt0OOjuF9Pni/hbU0QGVq9A2pqXWq1LPzqVLNZafhDurq99OBUqZ0VQgdysQ8IEMksZOX'
        b'MdunBtPEV4YVM8ahpRdl1k6CrF9+Pb7jmD8XEziz4vZDxHKzP42qPTjtMy9FsHlG5vlLdZu2ly0q3Ph+ozEl6dUHSZ9/aThY+88H26PNXi+qp2eF/XrFkfdGX7gx/enA'
        b'H0oH/qPlh+EP1YWGN6597DM5La0oYkpV4aCl76060B75r/jV51WK5qIfJV0r2n/9wjDbB2+lGXf7RyeX1Q5WvF75p6mHa8f8HKWqvajpciI6hRoddk/R6GkdLalATWiP'
        b'YLU9WoVPOEP2QGRF94pEqTXDRDdhzeAYIJfEIfQmutj3JpyKLgjeZ9dBcL3kGy6KthNinKLwKOITcxnfTKUnGaHrMQrqgkEEW0AIdAF0ZWjUupg2K2ei0Tn58JwGKnjb'
        b'0ekw0VsA7y0WHAbq0f58wR/gsRxfdZgUrFbhkX/NEHS+54W4fRo45SV1FqP4vlM3AbSEEHKOVYEAOlT0JVOyDYEu25JWdH8Ps85SYe2DunOWTncq0AGXpb2owEtub8Ls'
        b'1V1+uVTcsHKm92t5aRic87W8UvoQSgb7X0r3v4zuf+k6WV9nlvT2r5fniw+G16LHiLhHj2Im4A2j0E58h2qrwoOTPWhbYcRczQIN8fHAR8K9BnAj8e3Vxtdu3ZZYiXL4'
        b'52tjBQb9tPTT0krDp/pPS7WDcnSqv/oYMnWfln5cml8eVK4wvPcawxz7g8J70g5g1CqoN2LkAtBJiPkEAUpQfw98BL3EMsMqpahZGeRY/P5t2PISGhZBQRzoCmKTP/Wz'
        b'cFtlWtShwvQ41tHXKFNzUC/yLhXSnylLQbwNLsZeIN4X1BeIaeeeIUzIXZMMYCyntgQCZ6/nhPNzcXIBnMQclY8vzymUBBJw7mEZCb7P5q2wGT8a3MVaiQl6T+WET0pz'
        b'dK/8Iex3WToqaJV+Umo0hO/5pPRJaZXhqf6TUq41OjHOfu1UtP3KyiunYlpihFdvX7ltK1T+Hd/sEUOfy9/E7Y3ZxGLnAs5gV3BaFIJDDfHcDHFZ1Z46zwdXz5G0/YB5'
        b'O1xqeoG5a4grmD0P6AkxbngGeLywpWXippZ9X2DL+gQ23bstDVmFmgV4t2VhXKaEkXmxaBPaie4Yf/ZovdRKAiU+GPbZJ6VZTnhn6j4ufcdXq/uo9ClA/WlpoK7SkCvs'
        b'3lwJc/obry/r/w67lyBSPH6Arzh8oM+MZpPQi+j2879ft9u/RDxb1AXgbrJ2AwF4wxCXlXWr4Bna3XKDrtxWY+mDTEstXX2BeSdc6nqBuS3YFcx9DkYdIPjv9rjzEk/e'
        b'br8eTbuKr+/2W1ljL6/kLbRKjPttbLdvOTnNhScvS41xvYntVuiNVuEYFuIVTF4MbyMn7vJ2m24VPTSWPEHqVvKryit15EhTktTv8y71QBo43i0jPkwx3T6OY1aMepeo'
        b'9EW0hM1oM/HdCvI+DVK425f8ckR702R6fhNtKdZCjkTo9iIBiGU1q2hIerestrLGzHdLDLpV3TK+Wmc0dUuNUK9bUmYsV3PdXtNnzCiYn1/ULZ1RMG+W5Rzp+jzjYs5w'
        b'CMLEjmUlMxIPAZZTh2W2SWFQfB+RmODDkF67p1wQiTcErh2fwv1ZxkTrhv08YhRDj7MYhg7gA1Z8K8CCtuADMobDL7Hh86qpay9+iG/i/XnosNW2Ekrgm74s44X3c/74'
        b'bBkNLCMBPuhhBHGVvBiWmafNypuLm/PRxUi8LSp7bmZkdhTuQM2+eSBXOeKJcNcS5YyMdOqLYEKn8Uu4ay5DBPLzo5i8AYUC776NDs6Mi0+aGS1l2IkM6kL3pdSlYSy6'
        b'ODgO0DmOQTulcdV4O6X+Rvxialw83oBaozmGDWPQLnxmPHWExrvT0YNVOU4XUZbxLebwpbR6+lgL38H3QqDiqbpoOcOqyTkbR9BxYebn8QV8WPCATSAvNb/Ko/0s7sKX'
        b'kHBQx82p4cwd7gzDBJZyA/IGM0J4zhK0Ky4+EDVFgwYZDkLGmgj6cAUfw6d8crSg4rXgbXZjnga35rLMYHRSOg0fH03bixijim+QbCBnwQ5fZA5ihAFuzcSPYIAb+WgJ'
        b'w0YyaC/qxLeFUKzmzNoIctJIFu4cN4o8eQpAHZKyGLRfiC60DV4lAQxhVKXDN02JF7Qf9GggOhcXb58b7cWwGgbti8F3aT8r0EYvEEQj0dnh6JqUkUay6F5aIm3oaMjU'
        b'5T/gvmSY6NKgv60sFXAGXcHN+FZcPLo8CV0BPUzLoP1JuE3wPT+bh89GaNFDvE2dnQeKkncMh/ZWo+20ua/HZS8IkoSxsGzZT5dPFMYVj46h5rj4RUvRFYB3FIMOLIul'
        b'bVWjgyMExzLqJbAVH0rlxqJN+BhtK2WMVD5ViKCMPLRyuiAJhMQhMrCj6FIiQ5ds9xp0hT6NzUI3l+Rk05NKO3NWa6k7mD/aLJnC+9HmJialVF7m3iOH21qCRlUJMX4D'
        b'h42Ji8+fm8jRSb7ojVvsKkiulyloU3vkuC2/B7mGol1S1BqJm+hQ5uE2styoMTRRTqcF0BNew2Ragw8JQ4GqWegoAZ9/rSS5IsNEHqE0GIP0l9lM+FU66eWVdInWoJum'
        b'uNhMtJ1gaiQRX++FCKB4Kc4koikHaHptvZ7Fu/w0wjZ6GIXa4hLwDRJBwMZCrQEGOrIJ+PLSiBziA80ycuPUei4U6tAc9UjcEpeEDqCXSJVkcjbPXh9hR2xdjA6jQ2ij'
        b'iHWt6DLDKCdJAtG5HCGo7aWJ+FBcEj7WQHZhKqAEvu5Pq1qWootAZUBlouukJv7mykBJCNqMNtClD17kbTvNqsjS5x5ZoRSwYi6+ge7CWB5qgcKT9vZ551L+PxcdxJdh'
        b'FCS+MAfwonxmDDcsFx0Qtsx2dB+fgWE0rY4HZEojw9izTED/RrR/dE5OxhjyMIGrYafh5kGCN+b+4fhkXFJ6RjwMfBIJaLiIN1IEHBeAiSKaB6Bqh6UaCDpkI+cNmhsd'
        b'9q98VqtGSj4iyJx4V7pYoAEhijR0PTouM17GsOkMOoKvJFJA+ZNowrZcgPpcQDqQUR+x6ACvEsJLmYzYIskQFnbr8swqm7D50fUstA+aGjU2Hjb/DFB68R70iA7YApRq'
        b'aw5utc3LBUHlBTYKXUWbaEsXo4YktjClZCWXHmdHii014f22HFCGq+0yRiplgcptxY10tDo/WC7Bcxa1xGjxY3xI8MLdh9oZGqWAt4fPywTtVrNA8ETDzXmgVYNeODvI'
        b'axg6axI8HfZFlwMOossZQogpeRKzl4NRdkp6Tn4+lSIpniihQbS5XyzMFDYYoBvajrtAjIxkotDGyNIIO/HaqdSgFpFqn8Ev9jxxAt4iZcajczI70Od2urChUUG4bS4J'
        b'gwHKFYQ26thleC9qpQu1nC3KKcK3JuAOwAW8j8FX0M0YGkiMGxdNEgKi0Wm2JyaaZcYXyIwNeiHCdv9kBh/wJYSTWVSCHpXjW9RvIyYR7Y+AtSChsrsXZGqyBTUvRspM'
        b'KJLFouYxdLpD4oea7jGVhENMGqsTKXosOqjHB7yI/s+gNnQSVNSz+JzgDbKjbLnYKtDDXT3NcsyE+bK4pSMFXD2bjF7MmWupBFbK4guwx1HzWNp0FbR3vRAYcEcoOgV8'
        b'fDU7fBg+JiDAyRULcuajw6HCOpxi8I3J+AGNOTIDc72bk4UexroFnbPMKNQmxbfwVXSd9rtyOW7EB0DERA8YX3QXPSAyN2VuZnxnNd3ZDxZos/KhbpYmVgpixX6paSa6'
        b'44gsOoDu4gMSEkrEjC8C5tBkppXR1YA6UtmCdzgrc0QmkVaz+L6IIesBR4n90cjMQS8Zx+goDU1ZgfYRX0ky4CUgR5AxBwyULJ8VJNC+dry7SFT/8TbUNEqKT9BllqBz'
        b'+CihYeXorJZilejrMBzdlOJW5ToK+sGxIJiANMSg+4whF91fhh8Jg2nUwTq0AU5XMZO9qgahh5TCrY9YkaPRZKELYdmRQMsHTpOgZtSId6FjeK9AHDfIp+MDShLGQ9zL'
        b'z6Eb+HyysHW2of1LxHjOBeioM+ZEjS8JsHsRnRlq9VuIH/gBdYKNhy+iDUqKYWUJvpZRkjCCYZEvcUkC/SER+KdwG0y8hkFbQ2vww0rKslbje1NASrOjG5kk9Lw9p0BD'
        b'x6oaJoVd0ZxAbZYfeI1jfwZVVV6zTL9J9soNEdpEW+ehTsFuygzCLzbUoYfG/0x6V2L9O4izrwX/bNl/vWX+xZxA+XspP8o5kLjinTnpy95Mf+tvN6flHJ1z9GnOW7dr'
        b'Y4Je2TNHb3nyTu3m9yPe9/1h45+TJzFvvPynV8/yKwaM/7zeEHvYapk6YUFLvuTNxu2HBvjN//Q/urfPvTsqLXRW/Oyxu8/eSLK9xUf9NZYvGvzG47Ptiybem/Ok5v2v'
        b'vsy98sbAjJ9cfnXphyOTxuiL96VPGjEgqWPsCt9v4l/dOPedW0Gtr01LXXCr+bX0W8VPWk2Nry1umfmH0W9ffBr4lvdbPH/7lcPFH8p2PNy+dsGgWX+dkThxkspyJfG3'
        b'o3fgm1Nmz+xM71ycorUcf/PDk6+c3X9wUIokpeqDg6/UvyKLyBkzePSL7eWGkJCPf3LknZcHRc3eVf7Gr79+96BlYaJf+e9erxsx9533PrB8MvXMFyFDp3ac/pk9dYXP'
        b'of+68mrEB97pxXnhX/yq/u2QFZuSl73T/g/NIlXKw/CJmUvfv7AwZXrnErzwx/dOXR+5u+KP1qi//vk3r8eX7F4neUH7heqDqn3/WR32btV/h31Z8Ej7i8t7bi7T+69b'
        b'sa2m+WKH39r0R+qE21fa3r52aPuvZn3avuVP3XUHf7ua93v3Rf+A5SNGZv/rxMcPZqyL/OzkzsSpIW9dSUp8vyJo6mVzyStR/7o/oHqd+rNz5+o1fxm2rir+8fWUP/3H'
        b'lKPnti2eus5nx8XgP1jUn+obWuL/Ny132C+//Dpg3ISP2Ek/Vw+kMVjoEj4WKPoGrMAnPLgHgLj4IvX1R5tGoZci8hejdg2JbNjP5qmGUidbTboaZCHQG9bhk3JGOpNF'
        b'DyPxSeqhkF2HT6G2gFq0d73SAiJBR8BKP285E4yOSGom4ovUtUu2xOCLzkZmOoy2A/A9iY5HFytm0Ox1c9FOpzvqSXRO9PxCh2bSJzDGWTxqixpgp86yxD/4BIfabOmC'
        b'r2qzDWSoAtjNZwVqDJwtj9Oj3RNtRB/JzkddOQUhc8l0VrLT9SOoEWFW5IQIbY8XWd1ITrM+wSYoW2dGUq6K9kpJMDWLroGycp+ai/PQfbSfOGqIXhpL0HZuwAB8R4ip'
        b'u4TOrREt3kvQblc/jVx8Tzil7n703N6OFQckwE4eAh1qKxJPzlMWPutXgXdLpgAfPIF2TRfO629Ft0DWaCPBhR1UWSHOy3T66Cq+wjIRKTLQ5iKoQ8dIdB3dohbPo/DL'
        b'xeopWjxT1HQha8ckOeIwXirvCcVYjrcL0Xk3oOV24sxxejxucXXmgIHt9XTG/Xd29eyW6PSCQcbGMD0GmfWMljgAS9kg6m7nQx2DgxwfLojt9YG0oV6B7DgSe80OhRrk'
        b'T8kquKGsivWnNQJZf1oykJYOZINJ61yDX4+lBcbi5mNM5P7vGtTGCbV6zPMATOYcsfYQfHJaezYwvx7q5nHsNgrPD8qpJU94WRPTJHNa8lhqi+j7cXmvx3MjmWdtEWrB'
        b'FvFVpUQIvJqwMXbNSjkjmPeoDyq+vABtGYqIVDqSGbkCX6aqPzBkP3kCIpauUCZ0AejppDC6gw/VpCTGQVOxIFw9EM9rOa1UkDP3oqMH/X522pBZgvyZsUDwAbtS/ULt'
        b'RwuCBH0xCdh0W1y8FG1A+8hJm0x5pHhIJ95TgZvi4uX4LjpI2DDDr0E7aUOHfOlT/cBow8983p8oepgF+A1ggM8mR688vzZzXbaQ+M8JSmKOCYse9H7a1tLhQuIDiQ8D'
        b'1FARvWBydU5CgWDUxLfWF1HhbT6RcGUr2alr0D18fgnlv2s0PnHRxBYyjsH3gEjstBfSltSjxwiuaDEtmpqYiSKz3r0aH8WP80R+3YAfC+rPoCgpuow34QMAZHQL/uPD'
        b'xbSCbDBumlOMD4AMjm7Df7wxk67tpAS814qP4S4ApIbR4GPjaKe/9BeC2qMzCof/1XcVQ6WxIeg82oC78G68G91ai3eD8oO3MujmwHmChQZBFnoE1I00NoIZARJuF9Ww'
        b'oqcGuvsHc+hYfjbqCKeyPT5Xh64V0mc0LN7BrsGbgvAR8VAcCe/H4ktCgMsq3JkuyGd38Z0xDWWI2NrqmXolOkSnKAU6e2U8iKz0ES+zGu0y0Oep1DZ7/Os3/utOOUVY'
        b'9vI6+sB0wmgRfwxxRbekJuEp6o1UEcJy7/KRiyOFxKXTRQgnflV3f8QgIfG4wleA8KDx5cO1yULiy4u9BKxJjGzQJZQKiT8aIngwRk/oUPqsmCskdi0REwe9rIgbHiEk'
        b'vr9WXPYFB9ccmz2KMRa+G8hagfEw//zkWPWOrHxJTOCs809fK6+YsLm+eOybV2YsVS38MmjndSPvF9H4y58Ml65g9jQXqvI3JEvfzR9Y3Lzlj1+9kXAu9qcXFn6EIgfu'
        b'vat/s+XE1hXyQeN3ZV2IuBsb/sXbTZP2G/987ui9Kz+p+uV/Dftl3MCH5ypX/X75g4SPU0/sb0/99cyWDxf/SlW1Y8QfLgRb6sdXd40MqYyb9wf0lyPnLt8ovtTR+asv'
        b'/Az4/7T3JWBNHW3bJwshQFiLiuASFJUdQUBwQXZBFlGkLqgYSIBo2BLibhGXiiLiBi4ooKCiL7ivuNWZ9n1r91pta2rVVm1ttdrFfrW+Xb5ZTkICScS+/a//u67vMzLJ'
        b'Sc6ZmTNnzpz7mXnu574lVyv/mHC74f7erKsP/M+2OrdLRztFOWU41agvH4p/PASO2/L1/UPB519jZKKcso9/vj/QZeXNP/Jccpbd/G7tpidH7l1zs00XNc78pLZXTXRN'
        b'L01M8oLq+f+8Ubk+QlJ3oiHQ5p26I3c/jHno/NOsT1ZaPV3U/xfh+WkXh/y6aESP4Zdm3lh3++HER1L/n1cVOfMX95kxzculFM8V28AVvniBGOvymHWoOZlNlqTjxsBX'
        b'iSdAqp83fjKd4KKn9V70+y5wmKznRoKNyKohIGOSEyGAY4gxg1XRiYO74Sn62KXumUPh3lK4Hl4gS4YhJaAdP21TcHguHNsYYZNaTHWP4oGDYJ8VpeucAqcCceioSrzw'
        b'zMFEoTRQN4A3i/ponlaA+s4OmmVoBNGBsGD4KoFa/i59ia9oi9gHz0Ic5IDGAnCMFrEtC5SzzijUEwXdpo3DApNJE0jQnYVLAIf9KHOfTGL2nMJ3sw0gz/Bh4ADWNtLq'
        b'EcHV4n74JAbxQGsW2EIwThHcDxv1MA4XrrFwhLvtCJJASOgIXKYPYcCxIVoUg2qyzI3UYwo84a6jdMJWsFqLJcCGTNKcJaAhUx/irIcXtTAHNAnhOgqoGsFSOcIbCb7+'
        b'/rA6AFmo7eNQZeF+HtyUP57kMxSe5FJvVrCnoLM7Kw+0EUTn7+5L9lmXAauSLBg+lwPqy+AJcrYOMtjUidN/zK5IEEs8FMDOEIQqjfgSoP6XCOp1zgTThTRCwKpMHP0h'
        b'QA+korY8CCoX+VEUftzaiyA2sBqWd0ZtLGKTBREoFggODCFus3owa3MeWDHRndTaHu6L0QsgxAUrx4A9oGGYdu24W+tgfOyKR8DWLEOwpRRx+FxtzABnArWc0asnermg'
        b'F962I/EDnMkeTuwffmlD4Yi41hwxFy+airhCwulaaNcBaXDBJhzXzBC39P3Y2lDyyAiK2mywatapSJQDEZZEI/Wf6PNBkmkq+a/cwBDE+nzGVqpXr84aqNh7UIkBK/Xq'
        b'Je6+2NNXI9T6f2o/4ZUo4jlJaVZ4woT4a5AVfbLeS1YDNaKstKiJUSlZk6amxaVreCpZqYaPowFobNgf0uMmpRMoSVqCtuV/Hl9CiQXafHGz4uoLeQ6O3eJWWdjx7Wzt'
        b'BM5CB0ttJAkB6QkCg5c1j/YQusXt9Kv25WBhx3HmucTSCe3VyLBsQQ8B+5d1jnoWjMMk3rSQCIPVaK0qiyqisxosf7M9UUu1175Lh+g+WVZZSj0RgMYcCvtczHax0WnD'
        b'iqS2KxipndSe1YZ1INuOZBtrwzqR7ZfINtaGdSbbPcg21obtSbZ7kW2sDetCtnuTbawN60q23ci2aDM/l8G1kvbZwd0swNyW2bbSvr2Z2XaYBcJu99Nu90J/W7jrOFIv'
        b'liRuSaIn2ayyX+WQayUVS92p7iv6zYqouPKlA6QDVwinOeDWkHpUcVZRw0G0yhaZDUSRFu3vKO1PvHe8WYXXpNS4Z7UGvOpJWqFS9BOVdxV7YskPLOAkKZTiPi7vrCdp'
        b'sOE9CdO7WcUm9KkoW1WkwHLSmJWOA/ZSZUwcMFhWXEpjVhOKeqc4yqYJmJYaK1aEDIv4sB/J+rGQxhXFcj7S3Lka3pxC9F2BTCpXF6DvhMXobOYVKaVkiKAOr/qSsIYh'
        b'q7SRwa2Q7WXNrgjb6EJWdUMU9osfeN0VhcVt/ZdFYZ+vCdtF/9UoQf8vasLqtb+uHji2uJlaoJ9N1aFQLFEU50v8jFUlXJyTj4rMIRG8zUvUmleoNaJG+wIt8lyFWtT1'
        b'aLDj2PiXxQpJNpZCRx/140d7+XeKzEyl1ozWwrDqpG09g/Sawkjl2Yqg7v8cfVxTWrjGIziY0sftphau0Uw79HHFf10LV3uL02anW2K5lL1gw553wbTjAhvhmt0SK2V5'
        b'chVqYTRGoaGMdCdfsZq9bOpCHGn6hSVn7em0i1WBAyP2rOZgydkxjnNpoFPYCE+CZuOaszqory83O0EMV0aKHMAqBcnU39WZ8Yz05jORs/rk+hUzJBhsf9DoZz5LhHqn'
        b'hqRk6EdQbSgWweapC0mu9/oiyzotm8ukzVKkTrdkiMALrBoKD5oVsUVAuop4auv5UJ8GFTbIgFgK20jOZ/oJGNH0fZY4Qu5tt1iGhO2dy4NnjGacCLeAPT7p+vkthdVW'
        b'oAZW04ruLrZiHBy2WmBV3MVqOatouwmunWEsP1jBmnkT4mBV52qetAFNfLiVZKuytWGchSN4jMOs5IvRUuo93nv8K8Yy9aRmDKgahN1u9LJsB/+wgRWeyfLvj2RyVGtQ'
        b'Ds42v/q987ZtdKAo9sOwMpsPx3guj75fzv10SvSouRXWQpvJMV5XX5du3qN+9Onw9/u9Kio5Lzh0cKT/prGv1M/MLnkzc/G05i9O8kfCoIJHdzRDQq1SonLyveuOf+14'
        b'e+XM27Z/lM9bWJ7xyuwH6Tmr33a+1+veP48eGr9z3Ym+t8c8LXm2ZPu00/zzv3OuuA1vPxvpZU3mrWEb3AXbwQUS3C65k2kJmkANcfmergZr4Olkfadvdv5bBg8T8zF+'
        b'YAmeqW96Sb+DIduwP9yKPbh3w3IaV+4AaO5hYKZSIxVWC0BrBNhP+d7HwYF5cFOZj4Ho7YU08uNYsM0Z25c+ZXCr1oQGyGYnxtUCL7CRGoRJsBVuZy1CeBw0kun30XC9'
        b'k4GpT8189Pt6cHDETHKqfSAOYaS1TFmrdCxYCzcJkQ3vS5rMEZyg/u1+8Bg8qSJTF4m+Lw1PTCY41k/ApIAVlmDnZMHfht91nEeMivQsujImmojbcgQdQrdU9JYEKtVt'
        b'abVkEeYwIXt7GidncNKOk7M4OYeT8zi5wDDP93gVdicTW4Nz8kIHqvCl0zP1ljLXDYK/da1599mBOrRkhtGWwTPUv8Ul6enf4q/M6t92jyqZr5Um1YNOZio1RVupZ/06'
        b'1YBAgRdXY7XK0oIkM6Vm6krtT0v9j3V3+VkIGJkpcaauRDdaoh58enHhV34WQj9mSpPoSvPsQEiSzkzUF1P21XFCtXjETPlSXfmueAJDD7T8pSuqBS1mSswzKBG1rw7o'
        b'6PdhLiUwkwkOnbtsag6PrQj2M8d3K/GXxT79ZGUKh3LgsiaqNQnuK8oV6bzOLUx6nbPxzH62cOq2epIMy0R2VzyJ7Pwi2kn6WkldssTaSTqOsbev2Fuf6oy2CXca7aSv'
        b'/EKAK60GFtTovnGnK2iEOL2oAJsI1KTGQddYvrIku0hdykoSqRAYNdU2+B+W/5DhJpHKc4k4TCkLtg1Pim1vEkYSNVseG1LOCM7F/xJ1YkYSc3ZbYKietSL21CqmmLZb'
        b'9NuVYvIuN6bYMypbKcvJL8RiLawRRwLLGa1oRz9QqeR5haQrUEmULrpcKrFc/6zkyJ7JM6G7orVTAslFDg3XmSu4pEAvXzwJolXyxXvopHxzTFlYpFfKyfFYHgq3XVh4'
        b'9+Wlcg1PCJ+1XKb6+8ShPLEYEpFx8hJ7exdgGxqdzgJv778sFyX2JNJQflRh6UWyNiMN1a3jX1SoSWxCYMqUUJN/96phQNowK9fkqZNrCvQSZwYGmZZb0id+sJdRLaOn'
        b'Iy8kFSXK6rEpKVOn4jMzFlYW/yuWLCggQWllSvxg8iVabDrTV69CQeYrZFZDynAihN4tAdo7xWi1KOzRV55CxQ8balpETJ8mo50W0rtN0LfojixUyWmlinKNa3JJZ6Oe'
        b'QdoDH0Ai80rm48/dlCPC/6IMMlGRGTF5Tn6pnGhOqToU0bresybz9BMHYk1nmRoNrroMUA+Wi9kmQiNUAbrj4jL8JklKs2V4ltG4QpafGHUXGkVUoS6YI8s33v5+4mGd'
        b'diOlSdS5C9WlMvTkwFGZxS8XKVWkUibyCB4hjlLn5suy1fjWQwdEqUuL8PNtjokDQkaIEwul8rly1JkVCnQA1W1TdTpzE0eHGqvyizfQcGPZyPWqVfBi1Qozlt+LtUs4'
        b'aciOpn9Oyxv9chLtyXg6sFO9X7gn6p9+rhKdjSduW12dJNkL1Xlepruf/uHi4YNMd0CDHQPDTe2JullhQFdJTPpjSOdsQk1lE2ouG9QpdOdnJo8w/d1Mnlq4QWZGzsvk'
        b'A42l8aERjv1E8ADCpGhs1Q7lnun0GWvygd3BEsSa7OhRSLcQxvFMQpuyQvSHurkYP4PCzMi66/iFhtkEdcomyGw2hIpooBvoScQCY/HzJsTkYTrqIj00LoOM1PgLsSe6'
        b'ydkuji676WZQK7F+ItalZz/5ivWwXVzGRLHnZNicr0Q3KapLsOmq6LEmOzLTfc1WSpuVao5aqepaKXNwzxS8JFCy+8hPB9GiDGb2u4dhCM9zhDgVv4kzg4bO6P5hQfSw'
        b'IHKY6auhJZCyEJLdxsayuX5A2KXoEPyGduy6n+lRLEGmVBYGxCslapQo/APi5QjdmR61yO6mxyqcj+nxCRdgeoAyVzIaleLyEQhDY7/poYnUDWE2qfFqmGo8hGJlslKM'
        b'LPA7AlihZvFddtH8EWK8TozwUy5GregL1OamLyo+CJN76VEShRhvmD0iR16Kb0iUmoV7lMuM96QfSMa+GKf7DQsMDUU9zXSdMJkYVQi/me2RuRJ0tvFoUDG3E6EjoyuE'
        b'38SZoaZ3ZIc5rTSqmR6tJUqPEEejTxQJZwYNN7u/7tYmhxiu3Jltby39mj2SXh/TgzWmXSOIFh2Vii6P6RExW56DMkyMQUUbuSMNCNRdnZbZmELeY7gMX/GjJcPMUsz0'
        b'5zJqPF1fCJfDvVpxxVhY3UF+uwApvVG2mM8I+a9xsPxeb/fR1PEYto+Zijl5hJEH28By0DCQRhN6c1EvxjcyDC9P9XlrVi7dfTGoghWEqQfWgcNY56IBbiGut/BUFnjV'
        b'kOE8xRcedGEZt5d8lnCeDijmMEMlmTP8PRk1XkDoD89yfdDeWDJwPPYRBK3jUmhwIwYeAU1poHIiMz/YKg9UKAkxaGhqKvd1ATP/8IKclz5zuVM6ha4czoFHedr1KP1I'
        b'RjijBLoSYaCQWAW2icLhJq90sF8u+6aco/oCZXJ996SV60YXgkiHlV+/q3nQv3mz45P9DmNv8+UDLe6P9VdcXhNaWKGwrk2IWa5cNmmHbYlo7jHLhMAr988Pv3U1cNQb'
        b'q3rscG+9MfWXg093VIbHtB2V2lzRHFuU0bTnq0THjb/V9bq6cYr9+73WPNu+8bPs3X/ErRmz3eZ4/FuRw/z+fbdm+Ya37lRscN4ekguEbZpWnxszKk8vSPj8yFm7M+9k'
        b'K8dMvnLA6sytp34e8a3ymN+Dmi7NPXG2fLBgyehvFHfnH9k142Hvq7yi/fbHylLn7ZJ8uOJgL7HTy6u/5536rcH9Sfy1bzgzZWNz36nzElIuST1YKu0ghowAZ4j43nJw'
        b'iCwrlcLdsEEns8dBrbcMy55MJK6ZAaASbPUhroGtfEYA6uB6BXcAqHKmzoG1fcvoylhCgsHa2Ox+pTiIWhgHKxR2WS4yXCwqBe1gJ2gG1WxEpH6RunhIdMEN1sIGXUQk'
        b'cCCBhmI6EZzfVY+P5xYNDkf0JGwYuAJsLklKBjWFiRyGO5HjjXVnuzI6RH9TQG/suEaWqXA8coNlqjJmvJCo6vE5dhwPEh8Jf8ZOhNbsEhWXuCC6oveeHCfOQpFuMUYi'
        b'laYaxObomKzGLuR661JWL1RxL75eJh0RPHVnMtvo4tTWAfqLUwa1NE7nILGWsFMRs4qvi7X0PGWivP99ykR8o6M/S1npUcxnRiX0IvEG1sSHMTTCxM7wLJUa04+r+Awf'
        b'nAdL4SHOErBtICW0YOYKL9LFBl2NyWAD2MZMToC1VB1oIGxMJ4dxvBgOPMvA45lgJSnI2m0JZ37WExKnY8qoGZTWAattQNOwYAHD9InBZBQRPE4ZD62gdtSwYFTZWZMx'
        b'fUWWR/J4I0TA3J/kigNAiCyiVZR58laCA7NiQgwOMpEsEMTTL4PtbJkdocEMkzZL9DCqjH5ZYWXDbI70wtRSxWwPJT2RBSEzSXB4sB3sQGnVYPJkGjUQHBo2dOhQxgvu'
        b'RCfSzMBy9SCSyQBrO+ZNt1E4doQoabgFbbDUaSxLmRJdwG7QMpcD2mOE5GzGg3Ln3gu1ZBewMUtBuB7eU8FywvEZNJgJAu29SIuMFKVRbgp61FagdAtYS0NjHCDCyJiL'
        b'Amss4MXhLBfFkcZ5OOKrYA67HOeg882dGlxEH+JobF4JWvSZKCK4C8fVAw3gBKGKkMgMokIr5nuxGNPrRaExJLuLOT2Y74sn414xPTV2Fm2+a9JLTP4oSx5q6MAxcRns'
        b'E3+7+1SV7bCh/DEqhgv+wcDzXLiFcDsG2DsyayWR+Lr4lgUvoYSPOS/ZMgmew/B1Sb45Moh+WWGP7mlXH0L5VQyeSL98jydgfrPqSxSf/5zszsYOOd8nID0tLY1xh1UM'
        b'J5YB5eA4bKJk5JbEANg+Jz2NwSzMvfiCgQbKt2kDK8LhOU+9n+AFuI4c5ZoBK0iGg+FyNsPKl0n577taMcKBg0n4hocunvRswRGw2gZcWIwOwRkvZyROoJHs3lvqwMwq'
        b'iSK9sGeULyPPaJzEUY1EV/KrXREFG86kwkjnuFtu/7re981lMeDCPR/PXxkPa+9m4QzHwODUfM+Hs1fcvdLw6lMm9t3hacVDUnc7v3nlzV/eqZt3q6XyR99t73h8FH1r'
        b'75kj2dcuVzk/K67bNn3inSfqoOpfh6Tuirm87OqUOy2SK+LaOYnXBEKFRY8V9d9HxP78hu/elkHVLV+/dS4jeMeRkPqZ1wp4KV+NXHGubsP64MRpHmN9vpwRva+54Mod'
        b'P820iV9dSkwc/kr/sJSID6/fL9oxaMykAjfJJ99s73X06RsLdiXWNKff3HW2Vbmq8MK4x71rP//XMv8BT57+/NPSwIhpjTd/HbOM4+9ycfj661tr5jqOVB8Iqn5sEZOZ'
        b'uD8oJfyLN7Y0uN765dP3I1TTa3+/PXtO9KaMry+0R8S//W383QnhD671liRffKYJuFd/uoH3KP5R8w9PLH9KVTJpW7ycS/1I34fLQsw/6osziWdIb1BJkEUQ3A12+hDw'
        b'gH4VTgKbEDYEG6TzqbBOXQnch2BiMic7iuG7c8DOILiPBt+uQYh0Y4caItyInY24C4LgYUKMGPiyl04NcUQApcMowEHiqiN1gi1J+lQVuA9sZAnD4jgLK7sJhKoC98IW'
        b'CfG04Ym1jjazfAiWigBtoF5LVYHtYCkNnFoALhCOSBLYilnDxJ0oIF7foShwEcViO+D5cR1sGjS0YkLNABk4Qbm02wAWfz8QZ8RRCLT6wgPkFOEmsCaHIjbQClson3es'
        b'E+XZbgK74aEkQkIRQh0h1w4s50X3BxcpJ9YHtBEmizVcpa9P5tSbtHB/L3iGZjAOrmS5unZLeLFgPRX6HARXwLW2qi6uQqjohjBSQQmoE7POSBbW2dQVKQ4cIdfdezjW'
        b'mtKRU2ALenat5xbNm0MbYEcK2JOB+SVdfJVQu5yF28l15IJadJSe19ZMsErf6apvhsnAdOZBXJEWxBV2BXHFGLSxMmtcBy5lCjiwpF3MI3FAIK4P+tYBgboO1UkH9o/L'
        b'yrNZYx1Kll/iwDIGsI4Lq6dG4JR5yTbjp9ZFvA0juD6dEdxSpt4womLnQlE+WErob9Zwy/8/DbcumM+4hptlKjGU0Wi4DDbqibh1UnAD++AmouKWDw7SeExHLQWsIBsa'
        b'WyOJIBtcPYEwcAWwBpzxscQej4cwaRUcBycoi3lP6gzQkIp12Ygom3KJfEr4NZ4KWwA2iqbR7xJJNovbeUMs3mpwCWOypXeZ5OnMek+eoneaoJkbs0p6qXLIlHD/RJ8j'
        b'S+rH1v5ef23+/Ik+T6bMDs27Nfny3o8+GuG0cEPPCw6xLT+PLn88MvWz+PSPe6/cmvDugNfs+ZnTv8pb1ydFnCWwi9+a1t+neYGn+Ma67w5N+PcvO0e9NyC4rgyBhbTC'
        b'gCGzeTYjfX7bFufW2rD3480ttw/DfkOu3nrIe+uB/Ydzgp7Km7zsybCDgG7bFNJmmNcMTxI9trA4KkvWBE4kUj02eAYs71Bkc2ZlH8EWuBMhlUpf2MhPJZpqWHMtOpYM'
        b'Wgs9+HjQZ9XWRiSzemsyGRkQk+G5PPTQ0wq5Ieu5ghVzWwj3Url6NAjDhiSdGFs6rKd6bAvgUdbxU+aAS4DVoDFgvFaPbdkwGqRgKw9UGsQlRg+9Y1iQDV3jFvpIaAgZ'
        b'jeu+N7hD6RI2j6aF74JrprGSbFiOzRdspYpsPeAxWnitcwoaj0ETGthXB7CCbKCRqqaBanACPTVJzwPb03SKbB5FpOABfqjPVcKqyCy20aK5LuCsB2k1gSvc1qFMbA+O'
        b'k4dxCnpW4iO91XALqtU+uJRSC4kaW7jH36LFRoS9yEDu3XUgL2P8BpiXY8Pj4d8ux9afrw2bvLTT644RYTZtFcwJs/Epr4f8Tkh+XFo4fkv1cupM6cO+cHq8vm44rB5l'
        b'SKj2UlmBihLzOommOf5HcyfduIwnUeLOYydVhAI+Fz1vuT09u6+Rhi+wC0c8z2kkMdHyPeF2lQ6jWjC2izNcuchkO4IZk/KaPwM4Kjf0mHIvezdu3Vk8MxiX90no0/JA'
        b'wcWlDk83l/661Nm97xvXQhOcV9cl7Lo8oGrnofdacxzbpN/t2LmouuzLTY3vp0+euyEjLe/xnfuPPpiz8brbV7/fEt06Ulh098H8pF/ON4qTZ4MnlwOvj1z0eN/L7se/'
        b'zTx/Zc+Eu6nz8kNev3PfbcaXdz79YOyoL1Z8veOHZVvOfbnM5+YPNz0qNtwAEfMHL3h/5ZY+W5lhzacc9l+bvHHL2KahYwd7/HvAg59nS23ugh/LJ5zqMe7LCaPupWmu'
        b'XKqtvrDRbeZPr/YPu73T6/Dr4476/KOt3dv589bdM3PeXv2ktqVwwuOkhtr6P8v8z+RmXbGaHbyxsPXR+UsP1t68/86/Ph93cme60+Kh4R9/mpA7zCXk/soBP9n41uTa'
        b'3Uj04hGIDPaAcwmwEiEzDgJrJ8Kw6OiWUjozt7S0gE4KghqRwaygAJ4lrvAR0jB2ig9skGtn+XQzfOmCrpN0bv9vOtoLJ2gE4mpvNKMJISELs7IURRJpVhYZgXBkG8aV'
        b'y+VygjliNOIIOE5coavY2dXbeYzzkFF4PBot5NnZDC5j5iqv6O4tnoablaU33Lj+Dzh7jvIj3a2Ja4pvKRpm+H5kZ2E3eModPbVANRr8V8MdIeOTwWpQbcnY9eb1hW1+'
        b'8oNjDnCIEoDATdN39WVrdK9ZnM1rcOlxqarx9o+Jf4D1MVvPLEhOFdT//sk/73DCM3rUhE3Yuzre9WlbxKgf3lyeOrvkjc1/fFJx6LhTz28frul14P27abs/dXr92skz'
        b'Xj4T9vQ4+N2P7YrXh5a/lvZBxdD8DwCQVPb9r7DbFS+9d/92yaUenOE3fnjt2OON4yV2uy8+iyv5g9N0zTM1+zBCEqQPvwqWO+Ln8fjxIQgsVBOJZxtwlAtbFhdTHv96'
        b'rDOdNN4vH6yAR/CO+KntCM/xwC7bGVSm9eBMZKySJkgqzET9HNvEqAWceP1mjyJWbgmyv+qTElO8UyxHODBoeBP2g+tLyazbRjWyEQMEDCddAtsZ2DTZjU5qH7QBFT7j'
        b'LBhOEjgMyxm4FSzLJ6VFwQuwhsgBgs0OqDBMsbfx4qJ6ngM7CQ7oOwisUtEdwHp2D+tELjg8C2wjht+SaLiNGH6bVX6sXWgH1/BSwTo1xVfH4Vpf7doRqAMbOaBhKthE'
        b'jnV0DyLgM6EwiGU0i17iwuOgAl6gdmmDdAEy6tb4FoM6eJHdxRoc4yIwWg/LS7HuBQK9e0ejnY6KQMW8ElTHVjU8ViIqUXOYXrCaB9ZGwTUU0dTB02VJJC5GNoPPCMFV'
        b'sJ0Ld8NzvYiBOB+2ecCTfrjxA5LQ6LIOrxDgLUvGzYMPlvd0Nghk3ff//73V+Vazes5AY2Tc6WDKEP1ZWyEND0XEGLCdKuJFdAZCHhQPkAGnv4ankBVq+NhtW2NRqi5W'
        b'yDR8hVxVquFjw1DDLypGP/NUpUqNBZnP1vCzi4oUGp68sFRjkYtGPPSmxF4eWN2lWF2q4eXkKzW8IqVUI0AmUqkMbRRIijU8ZH1pLCSqHLlcw8uXzUe7oOyt5SotI1gj'
        b'KFZnK+Q5GkvKmVZpbFT58tzSLJlSWaTU2CJrTyXLkquKsCOqxlZdmJMvkRfKpFmy+Tkaq6wslQzVPitLI6COmx2DKD3RvsrH+PMDnHyFkxs4+QwneFlQ+SlO7uDkJk6w'
        b'zp7yNk4+x8k3OLmKk09wchcn93FyHSdf4uQ7nHyLk1s4eYgTDU4+xsk1nDzCyfc4uWdw+ax1I+rTWL0Rlfz2TJiLvbNz8v01DllZ7Gf2SfPMld1GRnDOHEmejGWeS6Qy'
        b'aaqXkGA/rKCLTF5WQZegQ401anFlqQobyRqBoihHolBpRBOxo2iBLA63tvJHbbt1olhohKMKiqRqhSwCUyTITAOfi0awzl1suDMJkPDf9mPJPA=='
    ))))
