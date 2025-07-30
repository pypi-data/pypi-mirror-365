
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
        b'eJzsvQdYW9f5OHzu1UCAGMbGe8gbARJ7GTs2eAFiGq/gAQIJkC0krGFjvCfYgLEN3ntPbGy8V5Jz0mY0TdOk+TUhSbPaJk7S/Lqbpk37vedcSUhGEKf/fs/z/57nY1zp'
        b'7PG+513nPed+itx+RPA/Bf6tE+GhQ0WoAhVxOk7Hb0ZFvF50XKwTneAsY3RivWQTWiq1qhfweqlOsonbyOl99PwmjkM6aSHyrVD6fLvGb1ra7OlzFVVmnd2oV5jLFbZK'
        b'vSJ/pa3SbFLMMJhs+rJKRbW2bKm2Qq/285tdabA68+r05QaT3qoot5vKbAazyarQmnSKMqPWatVb/WxmRZlFr7XpFUIDOq1Nq9DXlFVqTRV6RbnBqLeq/cqGOoY0Av6H'
        b'wb8/HZYOHnWojqvj60R14jpJnbTOp05W51vnV+dfJ68LqAusC6oLrutTF1LXt65fXWhd/7oBdQPrBtUNrhtSN7R8GJsK2Zph9WgTWjO8Vrp62CZUiFYP34Q4tHbY2uHz'
        b'YdJg+JuVotwy55zy8D8Y/vvSDojZvBYipX+uUQbf3+8vQjSuWlNlHD1qCrKPhsB0WyppINvysgtIPWnKU5KmGNKROSdfJUXjp4vJc6RhtZKz00HJzeSWNTOH7CCNOaSR'
        b'Q2QbvuaXyeN2vJkcU/L2fpCnz8J40kw2aDIjMyVILObwscDh9iGQEFGdRyNVZBuUnol3SlAg2S7KJYfJSSg6HHKQ9ni8HTeQ7ZHV0KFGKI/3k91+uIPHNybZ7KMgC940'
        b'Jw1yXJfj+hXL7KRjmXyZfTHZx6EBpFmEGwvJI+gqzZhdJcYNuDlKowqn3SXNNOSTiO+hIWPEeBNuTCvj3LBwiHPGSijIBIChHway8iEOcHH1gK1reAAXx8DFM3Bxa3lv'
        b'4KKN9+8GrhECuKJ8pEiOUPDO9Ar55pEaxCJnlfAMhs9bq42aFEdk6DoZCkYo+nm92dhSqRQil3NiBJ+K4LhlRj/ROHQBGf0gep//ILF47udjEfp4/B/5WzEDBik4oy8k'
        b'HCs8wLX7IEV+wbLY92Pb515BLHpOwp+CWoO4sJ2qj7h/DfS3/A51InskJChW4U0AqIaogrAwsj2K1I3KUJHt+MLssKwc0hypzlRl5XDIFOQ7yTrMY7b9nQOeIsy25+JA'
        b'dK7L/V2zyfc6m+VPIr+022zKcy20VTud5zRyC28pnKWayyNeRM70Q+TIAHzTDnOHDHm1hQHkHtQxGo32J3fttBa8BZClrXAWxFaOm4Gmz8DH7CE0vi3fTlrIdSvUHIWi'
        b'5pGrrI6JvrNIywT8EEarQqpnNfZQiJwxHdcV5hSQJgniV4XO4IaSa/iRfTyt5TlYXjsoskdoAEm3ZReE4QuRGbD2siOkSE0uSPBGvG+gvQ9D/bFkPe5IV8IAJ6KJhcWG'
        b'1xe+zVtPQJL4J8cX/XRkIJ4SvOXjA4bbH0yf++d+Q7ltL46M7Rv90biE84mh9W3an37a/4PNm4Lj60r9fV/5ZNzff3UsLWDIN+VRV3ftXao591LBuIPvdLz5buBS/fy8'
        b'IV8MmX30443y1NCfxS09oW/dG5v0Sujr1pfvh/wiM3a16u0Zl8Le3dry4ccle39UHBX2zHdxa/q3fZr3Urpqrubnsz6K+NtPN/zip2ONv5509+uA1TMnnG5+Ximx0QUu'
        b'wsfJOQ1piiBb8X3SlKPKokQihNwRkbrQgTZKtshzz+COiCwVqc/MzpUgf3yNNBl4ckQbb6NrVIp3R0WolVkRjIrgK2kSFETWi8xZeBdLFw8N8ocZHIU3Z9hh5W+P4lEf'
        b'ck+E27JWsXRyAhB0N0z4diBSjUAMU8jdDA5fw+vHKflOPkxpoVij9Gcf/8GDIuC3/SeWW8y1ehMwB8Z21MAy9Muf6Qyw6E06vaXYoi8zW3Q0q1VBsfYZGRfCyTg/+O0P'
        b'/4HwSz9D4DOY78dZpM6alaJOqVC406e42GI3FRd3+hcXlxn1WpO9urj4P+63krP40O8S+qDNTaadC6SdIwpeyvGclD0Zv8BN+CBpicgiTZpMFd4elZWDH8J87ojK4tBY'
        b'fE1SrK52LUj6I3Z8WivhoaccHri7jisSwb/YgIok8CnV8UU+usA6VM7pxDrJZt8iGfsu1flslhX5su8ynS989xMYarlI56fzh7A/hIF+QFiuC4CwXMcxqhDUKZ3FpiqX'
        b'Td3jf8GSLBM5ukLH6eOkE9HIyaWhEoHoiOpFQHTEQHREjOiIGdERrRX3xHFF3YiOWCDht80SoMHtWbIpJZH/TI1Ehvf2+/DWPEg5GjD+y5LXSj8v2a2r135R0lhxWf85'
        b'hIueX0jad8ZsKTh8Ym+fF/O057VGyUXuYsmr4l2Rw+TT1cMa/eenrv/i7oKBg2YN3Dgo+S2u+uXgtdltSilbP/hezPwIjUob52B7QEaC8FlR7bR1tkGQnFPuF+FiiSIk'
        b'jyR7SIvIZ1EYSyV7poRpSEM2acoEKiPD23myA1+omdKPVR2Qj/fie7iNkitNJm6D1ZjMD8Kb8VXbQFr4kYqcxOf64oY8YPNiJCGHOXKv3GgbQBNPmmwRqgwmFMjIDX4J'
        b'3oc3xy5S8m44KPK2mBhKdsqKiw0mg624mC0aOZ31omCO/ko5MVcbJEBa7cwlLBZJp9iqN5Z3iqnE1umzXG+xgnBnoVCx+ApI72iXIrolgD6CXKuANrLAtQrOBbutgm7t'
        b'lfFuqO7CK7UDr8p5B1bxjJWJAKt4hlUihlX8WpE3VoZ6wCrGeQEIm8g2f9IEsAD2EUWaCzMY3FYnZRbkM+42mZyQ9iG3SbMh/qvTHENy4vPclyUUx14uj/pKFxKhzdZ+'
        b'VRJcVlluLBVvj1GVfF0y/+WBrz1/IBAde15WW3ZAKWZYgbfYySW8f44nZtRk9LGNpKlXgaPeJh1AkJtJs1pVzcguB5AavFaMt1RHCmR9IzkEuONEjfGZDDnIfvzIRoVG'
        b'vDcG12vyVAvIFQ7xy7m0QHJTACLvFR+A6FXobQabvsqBEpRmoVI/Ts7VhriA48oiVCVmIO4Um7RV+u5YwFv6uLCAIQBl52UuBDgW6I4AXtr4r9GWiqfCggj4PgWfyvHE'
        b'AbyVHBCg5I4Fo3G7IaXqC4k1Fgq9cvwxRYJj/2Ro4IEEX5Xw22Pt0e9En44Wx1Wf5VCbQbY4olIpcoJwB2lxQ4IUfJjigWiCjSo96RUznkQCQIHiaIoEZL1YoAK7Rhuc'
        b'OEA2DBQohNnfwdt6Xv4Abmt3cFc8AW6rJ7glAiwpVDsly7VGuxegi9yA3tcFeSrfVbogfzDYO+RdzXlf/bEC5Kloy5WLn5ICeMCec1TpCXuJQAGCs0dp1lTCTM4m9SqV'
        b'uiAjaw6pzysUxMcMkCTVHLKRh75SfHA8K0CuxivckYUcxrccRMMDWfBpctwwICCQtxZAqV2LRn1Z8gXgi7E8vH+4NkNrBDy5/G6f/C9KqrX1ey7qz2s/L3m99LXyqN1h'
        b'2iztRW1wGXplQNbmTS8eGNBui47U6XQZWln5R0YOrVkdfCXtbZAEKbaQgzMzqKBGpTR8GZC2S1IDIfeajarTIGW048suhCN3EgTCA/LbERvV8WbiFvKAdCxf1Q3tGNLt'
        b'I+sFrtYxCR8CxXKvJ2ca+wxjWynL8V4HZwpcxngTcLTz+LgTRcQ9ynkCbkrt1VS862JMRj+HLBfM1QY4sEXI406GBJ7ThZBPYj/Qoy6uxLCS0skqF1buCXHHSs92PHQt'
        b'T1LE9FoXKeLquafXVMVe0VGUa5CseYljEs3A0Gc12oyKrwBdXi2tLO+nPa8//wZ/fdCAaJWOYss27UX9ZT3/irrkinbhy/N/gvYtJLNJPjGS/LC+r7/xwnzRL0KB/XAo'
        b'5x/Bxv5DgP1QujOEbCDH3MhOHH6OYkEYaWc0xY5v9nEDLNmxFmCbPpSlDSQbbKQhMpM0qaRIuphsHcqP9iFXBa52ipzDze6yDDlq4gdNzfEO8d7IE8jiVpvFQZqoho1s'
        b'wVw/IE5AngK76AXN4iR1Ad8Dfc4N8FSFtLsA3+RBjp6oXsnnWqhyrQygIhNldKAh+BUXC4Yu+C4vLl5m1xqFFIE2ysoAZSrMlpWdMoeIZGViUKe03KA36qxMEmLckBFG'
        b'hoesT04y26syJAyBTkohHQItLOPFnOOXD5TJJXJJsMxOl+Kz+AC57Z+VQ1UJhB9xSCbnS1LwLu/aBBWvPLQJvkisE1Ht4TBfJGlFOulx0B5OcJs40CxkTLzy7ZRONwHV'
        b'Xvltv2n6UoPNDApZlMai1wlfHwezhfeYNvFtyFy9pdZeYa3W2q1llVqjXhEHSXQ038qz9bZam14xw2Kw2iCSqhaPfwyj/csBmCGN2WQzp+bCDCvC0nQWvdUK82uyraxW'
        b'zAFt0GLSV1bpTcpUt4C1Ql8BT5vWpPNazqS1kQcWo1qRD/AxQ9m5ZovpafJ5q2yp3mDSK9JMFdpSvTLVIy1VY7fUlupr9YaySpPdVJE6fY4qm3YKPucU2lSZoEupU9NM'
        b'MGH61NnA/IxRaUu1OrVipkWrg6r0RitliUbWrsm63GyBmmudbVhsqYU2i5Yc06fmm622cm1ZJfti1BtstdpKY2oe5GDNwcxb4bPW7lbcGShdQXtH9WiFoyMQpVYU2a3Q'
        b'sNGt84qYHlNiUzV6k6lWrdCYLVB3tRlqM9VqWTt6R3t6xUzywGgzVCiWm03d4koN1tTZeqO+HNLS9SBOLqX1hjmilM40xUw94A45XW6z0lHSKe2eWzEzW5k6XZWjNRjd'
        b'U4UYZWqmgCc29zRnnDJ1hrbGPQGCytRCWMHQSb17gjNOmZquNS11TjnMEQ16zhqNWUpxWJVrr4IKICqbnKaGi6V01oTph8jM9LRcmqbXW8qBTsDXwnmZM2arppoBNo7J'
        b'Z2vBYKoEXKP1OKY9Q2uvtqloO0BwStWONh3fPebdWzyde49BxHYbRGz3QcR6G0SsMIjYrkHEug8i1ssgYnsaRKxbZ2N7GERsz4OI6zaIuO6DiPM2iDhhEHFdg4hzH0Sc'
        b'l0HE9TSIOLfOxvUwiLieBxHfbRDx3QcR720Q8cIg4rsGEe8+iHgvg4jvaRDxbp2N72EQ8T0PIqHbIBK6DyLB2yAShEEkdA0iwX0QCV4GkdDTIBLcOpvQwyASPAbRtRBh'
        b'PVkM+nKtQB9nWuzkWLnZUgWEWWOnpM7ExgDUWA86kTNQbQGCDNTPZK226Msqq4FemyAeaLHNorfRHJBeqtdaSmGiIDjNQKUFvUpgd2l2K2UotSAxpM4jpystMG9WK2uA'
        b'Uj2BxxoNVQabIszBepWpRTDdNF8pJJoqaL4Z5LTRaKgAHmVTGEyK2Vrgi24FChkMaEo+M7C6V9bFxlVF0AsgGGG0uEeCozwkje1eILbnArFeC8Qp0i12GyR3L8fS43uu'
        b'MN5rhQk9F0hgBXK0Al9mcw5yCcgnLM6mr7G5vgAlcn2Nc89qdWUTAJGuB3Zc4RYxNrXIYAJoUPizdmhSLURR1gtU2iMY6xkE8qO12oDbWQzlNoo15dpK6D9kMum00BlT'
        b'KaCtC+I2CzldAUiUadIZlqsVMwT+4R6K9QjFeYTiPUIJHqFEj1CSRyjZI5Ti2Xq0Z9CzNzGe3Ynx7E+MZ4diEryIKYqwWY5ZtToEDWWXYOQt0SEreUtyik89pblImZf0'
        b'PO+tUbnLW7yHKNbzGHpJ70k6+yGZY3tu2UNOe5psQCq9ZfNgAYndWEBidxaQ6I0FJAosILGLGie6s4BELywgsScWkOhG6hN7YAGJPfOxpG6DSOo+iCRvg0gSBpHUNYgk'
        b'90EkeRlEUk+DSHLrbFIPg0jqeRDJ3QaR3H0Qyd4GkSwMIrlrEMnug0j2MojkngaR7NbZ5B4GkdzzIFK6DSKl+yBSvA0iRRhEStcgUtwHkeJlECk9DSLFrbMpPQwipedB'
        b'AIHspitEe1EWor1qC9EOdSHaTUyJ9lAYor1pDNE9qgzR7rpBdE9KQ7THeBxdnGHRV+msK4HKVAHdtpqNy0GSSC2cnp+mYtzKZrXoy4EJmijP8xod6z06znt0vPfoBO/R'
        b'id6jk7xHJ3uPTulhONGUoC81kQfV5Ta9VZGXn1foEOAoM7dW60EfFoTJLmbuFutk325RM/Wl5AHl9E+IDRVCvENqcIZiPUJxqfkO44pb4W5ml5juUbHdo0DNMVKlWGuj'
        b'cqmi0A7Vaav0wEa1NruVirXCaBRVWpMd2IuiQi+gKbBDb2YApVsRA2XuBh0r9r2ZvdTvhSl5r7t7RmZi6podBQjfCofIy6aynKY7Jln4Huv2neqEXZaqb7nUXKXMQr1g'
        b'LNQ6aqE2N2EDhBpELdTY2imxVhsNNssQl32Pe9KWR03za5zmSGbLE/GcjOd5cQzz88IbcB25ZKVeHtsi8QW8lewUI1kiv3ZQ9n/JkFep9O30SysrM9tNNlAcOgPTAdqC'
        b'wqGt1hsfhwpmPGr5/nbwNIB/FQgV1EqqEFQewF4D0BzIQo2vnWIq/HiY8R5A/JwqQaQxV5r0ikKz0RiVATTJpNLUUgtLV7CLyqXO0xQphGLUkkbpp9VgtQsRNM09LKy6'
        b'mdTwJ0j4QkPpc1SFZZVG8gCgbwSpxD2Ymq436it0dDzCV4fZpet7rENDSnVOCJP4qUiodyxup9qmEMQih/LXZaZyqH1MWKcKH2SG5WVjioGjBtac0QAZ2DeDqdysUCnS'
        b'LDZnVxwxmSZa8olImi3WW7bYbtnivGWL65Yt3lu2+G7ZErxlS+iWLdFbtsRu2ZK8ZUvqli3ZWzaQMvIKZ8dAhEYADJV29SwytlskBBQ5eqCYTluswq5WdNliIVJAaadx'
        b'VK2gErtT7xaMrl1gVGRHZKfOsJuWMi9XvaUCSFQtJSs0Pn2OIj5FYLTlzizUKOwt3oE3QpKXClOLmEJAB26p0tJEF4p4S3GhSk/FYnsr5j1RQKFeinlPFFCql2LeEwUU'
        b'66WY90QB5Xop5j1RQMFeinlPFFCyl2LeE2mxlN6KeU9k4I7uFd7eU1nB3hGlZ0yJ6RVVekhlBXtFlh5SWcFe0aWHVFawV4TpIZUV7BVlekhlBXtFmh5SWcFe0aaHVFaw'
        b'V8TpIZWt+F4xB1ILbeRB2VJgXSuA+dqYaLpCb7DqU2cAp++ifkAOtSajlloXrUu0lRaotUIPOUx6KhZ1mRsdnJMSvDR7OTWMuYick5dCEqW8XQxZEZZmqhVEYrqjB8Q4'
        b'x2AD1qjXgSCitT2R/AQd7l64i5I/mWYxkltWh5jgkZLB9nfKbSCVuBQrxklUTOzxqgU4Rurg5sD6gdNQIbqcic9VlMHb9AaYFpvLUpwJsq7NUG5YqnWn/kVMEXRZkN3F'
        b'DEF9dNtJdBeTZugF3UJvKKVJ2QA1ujVmFSSbnuU1d+sw9Bta1hrtVUv1lU5TNmOClElaxoFc972yroV6YPcm6YbB44FXSXeQnbm+bcV78V1rdi7ZEcXEXdKo8UGhpYPw'
        b'abGcNJImD3lX7pR3l3Ce8m6rtNW/1V/Ht/Zt7SvIvU0+usg6SV1AXd9ykc5fJ9/sC7KvWC/RBegCNyNdkC64iS+SQrgPC4ewsA+E+7JwPxaWQTiUhfuzsC+EB7DwQBb2'
        b'g/AgFh7Mwv4QHsLCQ1lYTntQzuuG6YZvlhUFsF72feLXVzeiyU+nquMdvRXrFLqRrLeBwqha/Vq5cjoyH/Z0lhrV5KtTM784CTtUEQxlfXSjdWNY2SBdFKRJ6mTsyEUI'
        b'SxurG7fZtygYYvtAn8brwqBPfaCNvjplk/MAQWBdULlEF66L2CyDWkIcm/7RnbJp1P96auHcb6P8FG4/zmiFQGGEEz8eOZQSC/VWslBoP2Zu2NTv7rFMUDBcCoNS/pi6'
        b'3DxmjsbU6aarlCXeWcqSQB8qmoW6QzymfhqPKVIofTr9tLrlQLssxQZdp28ZUBCTjX4N1ApKTrERREBbZaeszA6Ly1S2slNGHU8NWqPDVcO/3ABSX3EVLOxK1nanaPqc'
        b'Wbmsh5ZkCJfJHNjn5/hnXjzPoCfOJ/nWSev86nzK/RwOQrJ62Sa0xrdWulrGHIR8mYOQbK3vfKQTMQch8V9aYMAek0Z/MoXuGWr1VnYOyzXVBubnUKZXdyvSLWICKCPa'
        b'KkXX1ExwnMACgkOtQ44jXo450pps3WqgP2HpQCdsTiqlVCvSaHmgKGUK5hSosFcrgK4mKXSGCoPN2r1fjm64oOK9F0Ky9x649kC+pw8J39cHT3SYoMhmn7QLM6OynamO'
        b'jlm994VyIUr/gXuoFbMrgSMA8usVVnupUa+rgPE8VS2Cg4mgukJNCi1UAWGh/wqjGbiTRa3ItCmq7KDAlOq91qJ1DL5Ub1uhp3vAijCdvlxrN9qU7ABecs+wcCyDCYqp'
        b'jm+KMmpEDHNtPboZH5U91eJcQhOc2Gp1AZOe9zNbFGGCI8tS8sBSC+p4TxU53KYmMN2LyilQjYAjDsISpq9QKxJioiMVSTHRPVbjtoYnKGbQgIIFaHXlBhOsGuijYqVe'
        b'Cx0LN+lX0H3Q5YnqeHVMuLL7VH2PC7FcOJ6gEwXXXuKmIFRdIn8v3Izs9OCHPAXfJA05+HI+qc8kTZoosi2fOpdmZJMWvEVJGiJzVXg7ac4uyMBtGbk5OZk5HCK78HG5'
        b'Ge8hu1jFKD6gJpGLRii/xNiunIPsqbR5sr7CS8WxUwszyA6yLRuYKN72ZL2bV8rRzHWs0ps+vkOviBQIlUBvB5Ui4QzVOeDCp9zPUGWQ/QFqVTg9oIKviFHiQql13kB2'
        b'BIzVErNQOnA7BwKBoiTyNWMssk+CyERym5zr1rejFXTcpB7qbYikHWxUznXrG75r8cfXQ3INKS/8L2etpXasz4qGvfae7/po+ZaPz96+cW9ry52NItmsF3/SUN83LOPH'
        b'b+RM2opH/v672derzZvbxxTsfmPLvMq/rLK+Uxo1ITPyFxeK5vhUnVj89qR/JYTxfov5iZdNIz4qmGQs/Hj8EtIZfXDzZFP8s4c+3F0TFGY8+u/7b7Y1PM4ePvm4Unmn'
        b'Rq6UswNOeN+sStwQ5XbGI2isaKm83Er2Mp/Z8AC8HzfkZbtBkUODSRNAfJO4lhwhR230pGemzs8fZlOZw05RaXFHFI9CcZ1YRq6SLayiqfgouQE1uQMO38H7oLr+I8X+'
        b'Etxuo9JXMD5NtkSowjJUPJLig36FvAofGyT4AK/Hh4ughi5Q4Qa8EYXgKyLSIJ3PitszJ0SolWR7JD36dXkpPsfHkTthQvEOcmIlbqDnuFzAkY4IQyHLRfih1Gyj0luC'
        b'gR06cEpotI8Utkb8EMCLUDTZIlWTK+SObSxkLiJtZDt04QS5lwc1hqtpdtJEmiNoXoVVEoCP+LDZWT0JH6NDZyZOaFkl7SuHfu8TkS1D49mpiGfG441uDTtEw8EpofgO'
        b'jJJciBVETr//8IhZ1xEV5nM6hi64dWi1lJNywZzM8aQnyWTsNJmMpylSrraPkw+7jq7kOjvC/E2pQGChJMAyhT7S6CMdOc/FTEW9O63KhFJdlaS5SrFKvJyweUy7T90u'
        b'0Xp0YLi7Z2v3rrrcmjnHP/Mopf1ZjZYI52e4XCXX6V/cJTI4HWl5j5nrlE00aqtKddpn+kA9f6J1urXnTPvWQcQdtTkZfhgwB53KbDKuVEJjIp257Gk75lfsEiK898uS'
        b'AY9+VGbLhC/fjhDaFwp5af57260Q2g0q9hQceml8gKtxZa/CxQ/qxmahG77FTr7dSwcGuzowKF1r1btY/Q9qsNzZoJPF99LgMFeDo3sUA35407Jih1DQS8uKrpZ7FBx+'
        b'OLDlxW5yRC+tj+6C9PfIGl764HGwgJ1z4+uQ65zbDzpW4Kyu27GCcUcec+x87DNJ/xCOrVWWf/WrD9HPG3/a+In8Bfnhx+iZk+LO3b9V8owfgDa+a7gHVU7DN6QOspw4'
        b'jTGtdLJ/EiPLE3GzJ2VmdNmXHOjt1JlPMV1A7keQ1sHv+NpgN1LFMvTg5c/34OA/Hx7jYGqt1L8eCOF69L7HabNu9Sv9On0cC1Lw4ZdabRa93tYpqzZbbVQU7hSXGWwr'
        b'O32EPCs7pcu1TKP0LwOB3FwlaJoim7aiU2IGVLeU+TtAQXsV6ATHDApZf5eGGOA6ph8oXIlQHuiAuH+9HCAuB4j7M4jLGcT918odemIF6IkfSLzoiWk6nRUUASrN6vSl'
        b'dLHBX5nD/U2hZ876T6EqMkWGaSFaRaW9Qu+mnMGMWA2g3CiE0wxUz7LqbWpFHiB0t3roqq+iey6GqmqzheqUzmJlWhMoKrQoKDkWfZnNuFJRupIW6FaJdrnWYNTSJplc'
        b'T50nrWo6UgO1nsGyclTp0I1ond3qgKrtVoOpgvXIVY0inAEr/ClmZIZjtJXUrtG9793yh9m0lgpoQ+ckQLS8gtoDrVTPsC6z09kttWjLluptVuWEp1ffBTydoEjz4CCK'
        b'BWwHdFFPxWjLExTsAMOC7z3G0GMtwrKYoChkn4oFDqe6HvM7l88EBbVmAqiYWrnA3amux7J0wYFCCk/FgjyLred8wpKErMIX1kakIrMwTxUXk5ioWEAtmD2WFtYxqJpp'
        b's1WZ0xQLHNuCiyIWuB/S6LnxruVPlWchoKAVubsG91gcCAZMZiUsDViu1jKLodrmYFsUT+k5a7a20oxWM+CvXudV7wd0orkpmzGy+3MYsNWKaYLyz5boqEKbtqqKHmYz'
        b'jerRDMAWAyAWdKDasbR0BnaDjxamdYUB2Jm+BiDuWHDd66E/uWabXlgmbPHrbZVmHVCSCjto/rQv2qWwAGHR6GF2yvQKM/B1r/UIQ6KLhlk1rMIwDVa3LqkVM4CoOQmS'
        b'11rclx21gQCq0/uJyowwYOFqIqvee8kSx+1E5jLWc2HDZGKlzVZtnRAVtWLFCuEWCrVOH6UzGfU15qooQbCM0lZXRxkA+DXqSluVcXSUs4qomOjouNjYmKhpMcnRMfHx'
        b'0fHJcfEx0QlJcSnPlBT3YnGg3K/7ScGQXHaHUEnSQmu2MkulzqXn8iLU5Dl8AbS7MYWSysEJ7KKT1aRlatxSeiVUDIoht/AjprXvmSJcZrNebpIvWbYG2alZE3TQA0ka'
        b'h5Y1aEREAamPIE05WapZ9ETrrDB6MHQeqO/wAUwe78ZXfckevPEZO3Vi8V2G14MSuYMpeD5IQg7gY6SNl5Nd5ICdKoSmVHyedKipbto0K5OenYXK6bUlPBqBz4jJPVAu'
        b'm5nFRE+2kJOkYw4+Akpzzhyys9ptiDC+fFKfC0UbNXOq4ZGXnUX2iBEomxv9yWlyO4GdfsMHOdLhr1Zm4Qf4mB/yzZo+mCfHBtba6YZFkBxfImdB+e7IhAo4JML7OLwe'
        b'N0vZjRyBZG+kP6mPUpM75BDZBo1G4gtZoBfXc0gxUyJWk33s0ho7bk4jHVHhXJkV8RlcYt9iNrXTRT7smqHfT14ZmR+0ArHZMeJHC63kMDkXQPaQm0KrsoX8TNxKWoSr'
        b'mK6M0lkhMQC3TQ5Qw6TdzCbXIshuERqwUoQvk0NSO5XecB1uhHGqM+mGSE4mnRERCiV3/eeIg8g58sCgfn+wyHoQcr4Q9aKq8uPXc/xwdLDkoyTDtx92HnnziM+y34Q+'
        b'wOtLk2YtPDtkU/S5nf0nno9SdHxT83FM30175n7Y54ONaE+f7RcONn8xa8ILlqXZo+pUP/9q/Ss/++xcofn6zNZ9+9sPdDw2pPkXvbl3bvyphLbKqW/9du9f//RS7Zbl'
        b'5qSz762pfSv3Dz9L/e3Xf3hbm3m7422fu6XWpcPbt/3+2IBf3B6ROTdiQUiyUsrUfnwO7yAP3a0rBXJmXynHl9JtdM+J7MPbyFmNh70hVSZYkxCKiJOQ5gr8UDjdvCdK'
        b'7WZiEewr8UliGX5uFZNVyXlyDCbPw8ywhOxzCLS4nRwWzCBncP3yiFxVZmaOJpI0KTnUnzwgj8gRcSyg5ANmReEXJ2giwzKgHwBDfGkpz6/MJi0e8mjgf3rjTY+nYv20'
        b'Ol2xIMExgXmcU2DOoAdjZVx/9nT/FbMbPWRcbV+XwNtVh8NQESDIzc8i53ZeEX3QizosC+ljEX0spo9i+iihD62nGO79fK+/UGdXJcWuJrSuJgJcLZa42mEifBmT6d1F'
        b'+HfHuYvw3kak9O2U66gvn0NE6gwQBF9nUKqtYp/0/hJ9p69j/7ZM3+lPxRQQDql3l9AH1zDL/Bw0mBpXgp00OIvK8X4eknwgyPJBDmk+mErz5cEOWd6PyfL+IMv7MVne'
        b'n8nyfmv93WT5Zp/eZXmtyzlPIdxX9BQS63R6okHIrQC2CfMEwiiIAlr3e/eouBCpqLCY7dWQClKytjsbMleVGkxap2ASDjJLOOOoAkOler3LhZN20KXudquJqr//v/Lx'
        b'/2Xlw315TaCAEmJc1qzvUUI81qNQXohyVuBVElvwPV6dPTYnrHehHccSd8QJwqzJTK00FiaumrwLoSvMVFo0VGmNPYi7C3rxawUlwrtna489ppRJ6G+p2byU9pfGqBU5'
        b'DuzSsrDCXLoEAA+qvfd9QBNVfpITo2McZi+KCKC50eoWdPm89tgJF2GcoJhjtWuNRrYyAHGWmw1lrtW4wM1ltlf9z0FYPcHATtMtcHer/V4NjRZ/QkvzcN78v0DJStev'
        b'0Fc4XG/+f0Xr/wJFKy4xOjY5OTouLj4uIS4xMSHGq6JFf3rWviRetS+FsN/b2FfCtKhoqWnAmbVqZKfXFI3ANzM1mVF4Yw7ZHpnpFF4LvKlQ6/BD3/iB8UwnCVVM8FSf'
        b'0skmXp6ILwuqWQdpTtSos3JAdu29TtxAGnLIQV98jlwgt+x00wjvxE2rrXk5eY4Li2gTQ3HdPLITSjWTetCj/EDzgFohfLdwIT6MD+JTvgiUpL3+ubghlKkww/yDrVmS'
        b'LNKUmZOnodccRYvRwHQRCO63BzLdhJwiHcus4TlkRxiV0dWZq1bhtjAOjaiQSMhDcodlyk4jdf7kNt6GW/GOWSDMq3JBu+JRSJwIn6jCZ+10o3E4JD6C2ejagwZNB9+c'
        b'RS/RjYEBnu8vqSHHSaugEp0w4cvWLLxrLetaZqSSXg3aj5wSkfvkJrnEIPX2ROGq3ugZkYMKVichphqTK7GT8R5y31+K0Gw0e81ABj/SmK/wp7MEE7qL3M4A9bKJtJCb'
        b'oHJGLycN+BKEs8mODKp5LRwkm2kazbTBCfnTcRN+SDrgeybKNELv+gh6R5OV3NPGCQr4NDO71pc04ufwSQDGQ9IiXHlaWmT85t///vcIrQOjEm3+w32qhC32L3OFi2uj'
        b'x02vlqufRQyo2qhZdHKaGCKQ+ozIufS+4aisOYAPGaSxMEwJWJHhul5YiW/Fk11sBqWmgEVk1yJ2gWuQPz5WSPbEZYkQRy6PwJcQuawuZ+4FpCE00d8Bn1ldqCLzMjX4'
        b'CtktBt10Dmla7PustFq4IuuIDt+1uvTdgjCyp1DmrtquIQ9EaHKoNHDVVKZ3++EGvNuapcrLiaL4k+vQbpVkP2n3keAbhbiFqfY5S8ZECNfaKDUmKfLHz/GAK80j2fW6'
        b'clku/6IU1bRn5vR7cWDwJJnghAF63Q4/0uEwZzD3C4pZZFtUXk4B2dE/zFGhuz8COYLPyWHgrfg51i45WFkVoc6MDOeQFDeTdnyWjwLVcRu72ZbsXLpMg09mMq2Qt3DJ'
        b'88YoRWxhk034OCy5roJ3SRsfhVvmM7RZUxqt8a1xlcLbRrDFhi/jR3i/c5jUEOEcaNRcw8nGNpH1GdCPmod/vmjnpFwyJXhLxfJfLj+87l+7B+LQ88pZ1T6DA6P9ZkWO'
        b'1M06YSeJm6b1KShMVs08/snCCzWv3zv57oG//fat996d8+bRwKR+2TkHH2e0PL/h4/bfH86a94GxaWBOeb9vmhL+MGZ5aOY/mlejx79YflpyYP3Q42fPr/mF3H7HMH6S'
        b'7cKEYZLCNZVX1L+/X/i3NxWjZyba9n065W9pQwa1zv7u5eDaGyfPHW0s8+kUmw5n/3VhR/akfQb7G69ZW162/cyyp2OWIjP32sfc44pHml+dfdVy5eycDbvsGy6/suPS'
        b'mdzj5fmmlrelFf+YujJz/we1ox8o7nw6bPKHrzzQP3j2vc5a/4vFZ48/eu/19zYuqZt0OHLHkH76je9+uVyx74OfHF4Yanvtu0a//z047P7Y1T7/Trr4+aVVY+7+63rC'
        b'gxqyvbR2U/G7cS1vTPrNl5O/vmo5nfaFMoBdo4vvkTpyITKnm59HOeDjNWaIiJxJzmmedHtwGCHwddwhIc14Z5xgiHgYQu76a6JSnrBFiGU1leyGtBVTR8fg+xo3j5qg'
        b'uSKjKIklDsCtBRHhDhcN32cBax/w+MyUPHb/1gjcIo9QU0IfSRFpB9mUzKtCNbZQgaDcJR0afCo3O1yK+EVcUhZuEW4JvFm5AF/KzonkkVgzHddz+DrZhpuE+3ub8Xpy'
        b'GMiQ0y0DtNT5/Hhch0/bqBcE2YtPJFCbibv/BrlS5HLhyMA7hYwX8Q58F3KWDHzSSUNw0biMt9gYsT4I3NFK15iK8i021X3IzvRwEW7Hz5F7rMuhI/FxDwsLucevnCfu'
        b'5XIsZfB/yeDizfQSSI0MXTo4M7/MprLBOvbLyx3Gly4TDL2vTjDAsBBP/UaGQ2o/Tsq8R6gnSQiE6a3EMj6Q+Zb48TRcO8DDtNHVqsNgIxeMJjr60NNHOX1U0Ae9Y9Fi'
        b'cBlSXEYMN1uNz9NcXuwn1Kl3Vaxz1WRwtRPgaqLLarMUHkUeVpvz4e5Wm56GViZxyFp0D9zzMnNJnU8dYrujXJ0fs7X414ldl5lL6qWb0BpprXS1hNlWpMy2Ilkr9Xb/'
        b'I618BHpSkAsUBLkP49gt8GEvSUqMP1sVgWaz2ALEmHHy2KySyIfBemSnyDkeGFozuUQ2WnGTbJkIiQKBat+czoy4GaqKQtw0mzTNAaZyM5/cnBOQGB2N1kxAwwaI8IZ4'
        b'cp6d6UxKri0kTfjOjNkJ0WR7PMhRsmUcOY634H2MY8DS3rPaWRGHJOF5+CqHD85OZRyDNOmScIcUH5vHbi6vwbvZtejT59eAAHaG7APugtA4NBD4zFXGt0bgzeSMRh0d'
        b'H5vAI+lacryKw0fJsWg7ddsvIJtlrgvCcV0cvSOcJ0fIoSUGv18/4q2/oxX8tG163sNcUYz81qear89NaZg9cmf4tT/u+1CRfVmebfyfkcNC6nOHHX7cv3li+vU/yCai'
        b'voUvPRP4+l/CdX+3Poo69rtpMWlbZUUXKh5wW35e9b83BkWfPNGwY9Hp23umFMgb+F0vGia9EWEcIT5wZeSoeWdfK5RO/mX0L4syFQlfxe14uVr+p9t7j4T4vBB7dcW8'
        b'6L1vpX/+nSZzyJcXNM1/MH/69Ys343554MLk7K3PLRz6D9+g5da1nX8Y8V3V5cWK2j88Tt80e3T5tLDGQzcOf3j31ZZ7751/ru4zu7zl/p5q27pPXvqt750czbVjpzVf'
        b'1+z6YPSN70Z8Flpw4+5cZYhw//JBoGlH2H38PlPwTcTjk9wccmGsQFNbyHaY3l12F2EFqoqihSujH5JW3kVSyR3cQckqP37tbMZK8H2yhb4+gdJUfAxv9+IXN5ecZowp'
        b'FKC5C7gSOYTbnuBM5EwFI+Arn8EbNLnPkl2RIOg1R+GLYhSIH4mK8XP9makab5FI4vFB0kA3UiRIPJzDJ6cNZTc2LiDHYtwur7YXInmkyGcotE3ZGDlJTk2IUIvwOeft'
        b'8I6r4XH7QoGQnyUtYo274yO5vpBD/XGbeAjeSm6zTOX6tRoPV1QOb8b1KGQJ3dG4TPYxR0ENCMEnPLlrMGnzsPKP0wu8db95JfVMHTivy0URBQ0XLca7C9ncL1iBb2jU'
        b'5ECJJ3M140aWrCX1Wne+Ar8X+JXkBt7IQF5dWgRQv+J+nT2Hr5l4NtMGfJG0edzZDAx3C19DjqrYdFb44h2gFcFw8+il3HhnNX7Im/vibU9HdP+Prsh3+tMIF+Iz/qTr'
        b'4k9RlPswj0XmtyimvInn4VPgVXIgzcKvmHEsYduAhgQvR5kr3fkr5cV8IN+f9wN+5u5NIzQv8CmfLg7R6SOYoa2dEqtNa7F1iiDfD2VKEouZfq9y8R6TiwEx3mOERxvn'
        b'uBKT8Z716G1FD24/Qkf/C+5XInZ8Xvztb7rZD4QDVTbneQ2HHdboMI9Y9Da7xcTSqhRaauZ3s7Y8lYlcsVS/0gr1VFv0VurOKJhxHHYpq8s277DpeDNtP2m2NwrGMNqd'
        b'0pU2vRezk4uVSt0nzM0H3h5OF2kHrPFHIPLtxc3aAtDzr5Hd+Po8EJOv4UsFuF6CBuL1olXl5ALTj0eRM+GkBWCojid3kFoWIuyG1inxHcZgccO8+eSBiuzVqNUi1A9v'
        b'E+ELIE1eZQw6vlSE/jyU+sCWGIfrRyI7lUUTSAc+4iyrko4ie0qBJp8mJ6emxqLwBEnyKHyK6b7kymjc2KWXpaSDVnYihHHFOUCat7pz4BgOGDBUc47x2gi8H7fS1c7p'
        b'VjO1DYTyraxOfC8T3y2kpVJjQaPDTdzQEnLXcPZdK2cFaob++llgzmsjAwn1aK9IfXduYvyFfe/4+jVopFkTyqcXvTt/w083LZcXb/312Yaz66+Nn/Tdh/47yl69cSr/'
        b'R42frSkb/1kjznp1xpyFs7NN1a/MfvHlO9df0OF/3PvknaJhtQ9vTKi5cVy7ueXH6146eXRG6/nPsqqK164633rvYVLqzc+mLiqeO3D4wDcHjN4+fkznEKVUuG/+Em6G'
        b'gbFt0RHAmxw7o85t0SuRAr/b1E/kdvNvOD7Aj44jl1kavg3qxN4IdQ6PH+BLMOTznIZsF4jmTECG9cDBhJdb8NGkHfnreZB0Lg1mm7JVpMPi9Ov2BSX3Sa3huVLhNQsJ'
        b'mV1vKWF8CO9Xi8wBg5TS7yEbPXgeaq3FdMF1vTNEoJRGsagfk837wSele3RrNQQonRvxcBTN/YFOicvg8esn6NPRHtwSHU0ouU5xtdZW6f1C9ETkuH+abjrS1yJIXZei'
        b'i3u8FN2x4fixiPOy4dhFsij1sGqX029GozvxevpjZrTjExSZ5Ypw+i1cARTXKpi2KVnS19CzrdTSG66uNVSHR7KGHPTR4t1QbKU3+Olc5mmtpazSsFyvVuRRa/oKg1Xv'
        b'ooGsDjYAll2rKDcbgd73QtAoiFzH+FwETZZrV1IE3zmpICID1kV+BjWjPdBk5WTjC7MzcBupj1SDLJBBtvpU49Z57C0C5ZXjNbCKsnLUZFvURPIAX5wNxKEhqgCkDlUY'
        b'viAGeeeWD95LTkuYOpGblUha8CUQOVpWgc4vMnJ4Y43jbUnktgzXRfjgDWQjQjWoRorPM+thrRS3RUwhJ/N4xM2ikuotfMKwy9DEW6nxcV5OyqSm1EA+Rj7tpdz+89ee'
        b'fEdULQ2c8iMJ8g1bH37y+JRPCo27Muqr3v95QWrS2GfH3PvDa9807Y9r1V97cca9OUHLf/FGw5hVZ/9SXvqLf83OupvjrxrFv7hkfPr910//Wbnt48vHYzZ8caHur6P6'
        b'J89eFTi0cbxq0qq+B6onmXZ9vVb88XXDbenKj/+VuYBclv3ln3n7v5PhKuuY/7Hq5sX/86j4y7YdfRPWGD9uf9EvdWHClwmvvjXg0uKUPf0/UAYJMvc2UkeOwFynLaGi'
        b'nziJw1fIIbJbeGHC7ZlUHo/MdbzMTLbMQhr4NeS+mcmGNny2iHSQGyuYyYVcI1d55IvP8fhUTQmrPAymcT9pWDsRatgGMrs0lx8Kwt4uJmqTBnwe6E8DpKgz4bF0Eo/8'
        b'STtPHpCT+DRrf9RiX00k3pFHXwaA72k55D+FJ/vxXXyZ0aiVwGEeQAXHQbXaFpVHz+es5cPJQYng63ICb8AnKcdQqkkz4BIy4QsoKFpUQXbNF0jsg3Qqeq6a5KKy/OjV'
        b'pJmR0QiQlU9ERNHtBJVayY8bDSTwmAjUxQtZbGjBeCPZptGR61TWjsqVIOlEfsB8cl24mf25/gEaF6764g5ytx+PTyj7CNpKG9k3CrpdV0maHPOSzg8Err1LuOz/ZAHZ'
        b'JQjEYwpcIjE+MF7QLq6RoyhifDLrGbSKz/OR65b1Zqb5HnrtRqPFdP16errQX1/B0CJjR3GAOIOoKhhOQiC2NsBFQ2npXI83BFg8CXUvneSFvF3E2waPfz9BvDf193hj'
        b'gEfDznPO0+j6tkynX+keDhAUx49SInzw8N/3iWP11C9eZy4rLmYnejpl1RZztd5iW/k0p4mo6ztznmG2GCYUM87DRiDMRr//uqGsVzha6I7Kp8jhNSMTi3lqG0NcvzG8'
        b'Q7f43icfKJIDsBHXXy3n+vFD8wcnBQ5hdpKpKRlW+g5Ea2AgOYt3i1DAMJ6cILckwr7QDVB8T/nj8zZKMfzpTkh+vkrmL0VDY8Wjoxb9l14z1O0FM913C31yhZfftYfj'
        b'zYX4EN4LgZFoJNkwgtlndCCwNmrUuD06AUpXxZBb3DJ8nVxiY0wn93PcXuBG9ouZfWbpaOF2sBPkoIw0ZEZS0ShOjHeS86B7NvBZdh/DPvsbvJUiX9Paz74sWfh8+84T'
        b'LTFblnFlPp/yZ7fI/QelpkX+tt/Zfr/dkl2SqPHzn9964uWzm2K2nNh0ojFtT+Zubkzf154/IEVLJvcpeu+6UsLIVB5wmxOuM4Tzp+LLfNwsxzsgZttBq2e0wgpkxUks'
        b'yA2LICe2qaq7rNfk2Di8g1ctXSfQ9rMKUufSnskxvI1q0Lw5pFooemBpoIbCDxK51Ui2iNeDYLmlt8MlclCMQBLRF1PnAkZG+ruTkTHU6krJhhielhWu1SHuFNMCnVLh'
        b'aJe39xqtpFE1LvymZUfyzvrXO34/dhft7MyxcDduw3cjwrJUGZFZuCkqE7eFlazhkILslfQrmOeBQaGOT+sf3e+2iKD3OwBa8jrRZt8ikV7MXu2G6EvdmvgiCYRlLOzL'
        b'wlII+7GwPwv7QFjOwgEsLINwIAsHsbAvhINZuA8L+0FrPtBaiK4vfS2cLhKWBKcL1fWHtuWOtAG6gfQuC52KpQ3WDYG0QJ0aUqXsPItYN1Q3DOLoDRRcnRhKjNAp6L0T'
        b'rX6tfKuoXNQqbpXQX92gch7i6KfI9SnECk+xkMPtKX7yu27k4SCoy6+rnifL6EZ1j/vPnrrRh/vqxhzmi/roQ/R9dGMHoeN9T6BNHAuNc4ZYjn7MR1A46SODOfFx3LYR'
        b'yrwHfdg8SXRKXTjE9dcNYue5ojt9i4GhaGeAMMsOWntYyD1VAMEHUcpe2id12cUlvdrFn+LNaH6CXfx5DgSt+L8gNKVEnjJ0lLAdfQw1oYHT9/Iov8T0dXqyELllzhru'
        b'm5DnfVC0dtWbUQORPQoip9nNHifJs/Ej0uq+P0SaSYMPKqyQBVPZjFVUqxqNpk35PWB+Sfq76YXoM2cn2fE6Q+Pkl0XMuiWaPGlY4wsB66PlmsmiI/FnovkFv/9quPz5'
        b'8SEZ34WOO57ut6Dlj3c7xv5kxrghkfONk3aNj6/V5ocnD0gacOHdYVnn/166Z0bSoNXDGkMHjzi6qu/vGif7DDuc+davimf+aPvjb9D5Y4OKfpap9GXkqQy6fYW9FYc0'
        b'kcuZKhGSzeZtIG4dEcSg7SsKcAO+ykzB0vH8+Kl9yNlMwYx65hmy3tMvOTuZ7QZOiWIbZ9lUdHvyaLMwK2MHScj51Mq5K5miTu6Y8B3hfHZEmErIBpnIhewBQ8UTs8kD'
        b'wcv5QN8lkGk/fkRf4YObmGW5kW6xHRKBDHoAH2F2WbJ9Pj4FXb45wJktB19GkGuPCOIfhApn3+vIlfHU/LwtagT1N+eQDPR6vDkK37ZRTYccnBWFG1bgrWQfVMKYLFSF'
        b'm/OAA2zLIzvUUpSikeK9sWSbQFyfWvjrOoo93J1ox0o5P4mMG8iOZDtMmlxtiGupPPHCQsEE2Slh/kOdYup+2inv2nUymTt9DaZqu41dieVdg5dY1tLvq+ljHXLKhGs8'
        b'+hnVjfi/5SEaeunf0x7xlRTTTvdy6jSNdywL91ZcB66Hdl3q2e3sqRpq1VDU/r6uVApdCSh2n7leujTN2aVvh7s13/20tfppJ8Gv2AWlXpqd6Wp2WKYzu9Pr8T9p1beY'
        b'ok1xlaG3I8dZrkb7U/lfUW4xV/0ftaat6aW1HFdr/Vhr1B/2h7TlONEsLbaZbVpjLw3luxoaNJtmdXrNem3tv3x2mUfd39DH2MKPjcJ7un8/Qmv0C/YTmE64XDhq85G+'
        b'XD5xyjhkME8cLLZSo81oyev0dbAZ2lZd2G81Wnn55yWfoz8eGlS4/8VB7DWvJZOUtyRf/Hq3krPR/BV+mUDLPOkYbiRbn6BlCyJ7ETqZ+sXIFnu1mJNszaVSZm0fdzLw'
        b'nx5rLuxGa6562BC7N/L43/Dz/9YLVbtrOg5g5SVKUHQM9elab3xHPrSATcg/t4wtQxnrKHJyix8ZtqKHnJU6+53Oeg9AFdNR+nnJTt385/fj/fjGzgui125rne86XNIp'
        b'PeYXo+TZJSSDls/vBikPKIFSspecK2aWEdBI8AFq1gkfFKBSUzP/Rj5uMN7dm+oQVMzcfA21+uJSo7lsadd76JwQXVg7yG2iPXN7vBxVwvxTvWkRO5CHhaEJHvO7Afei'
        b'B3B7btO1GJ3wpUqT82WpIoCw6CkhXPnkCzO97fIwCB9d/VfuHVunD8iAk8cW5Qr+lPhgUgW+BFlrY8WoltwqYdZKfJe04Z34EgxvVUoVWkVu4E1so2a1IsJDOqSv3wzL'
        b'VXEoHm+LxkelgWtxK3OKPD9IjL4JD2FS6G9MlYg5+u2fwhz9oluXa/u+N/CbIVJkT4LocTPXOu8dGqTwcPdz4IjHjUMnyAE/chDfGsroneB51xAIC9+lUlN1mlwr5rPw'
        b'MbLX8PVpJW9lwHogHftTVQiO7if+aE3U5Py6slpfXUyGaf2Uj3+lqF8yq2DX4CWxGbk732/dfO/Iu9+Vf2bG19JCm3+2sb56YNXJ+j2bDweeq5d/nK6tD/5N64hxIQ/f'
        b'PBQydu21/Y9MScumxa015fzlf67ty3zl6+d+e9lf9lPd6H+kL+hf9sYvPzSeibBtxZJTD6dWT/3bP7lXL4z+x482KX0EW97JiWSTu40RBUWPiBZViHIFWXTbnKBuR+QW'
        b'jxPL5pELNrZzdx/X4x10cSUM7lWgS2Cy5gB8fIx/OMisczPZxoyz1hG4Q0yukmNkI6s1vWo883agAivAGV8G7ddZI4APXyzFt6RDyQayT9D1T6YVuu/Rk3PT+ZVjR7LV'
        b'PBZfLfPYY19ay5v9yeau98/2aE6UFq+wGBzvFfUQKospdea54SBUDnb4b8m52mC3tcYKer7zWGupsPZAsnnLTs+l3QyPhd2W9lmP9052ay63TOxYhR57rY634LJTZ663'
        b'4IrZho8EFrWYLWoJW9TitRJvi5r+SLotamku8yxaKcnA1B15BCLnSOsIcrKSaZ+C8+tpcmZoRIFqrop6Vfj0icEt/HByfaxhxzd7eGsM5Kj6aj81M+3E77zw/gvtO++2'
        b'3N10d37kFuX+kVvubrqwKaUps3Hk/lOPN3RI0OUJspX5j4H1UsuIOCAZtAxqD8GAE8zBgkNDyClDpRjXryh1znzv5mJpMTuCwOAb7A5fYyDza/CYYpbVqZN0ebKxVxYz'
        b'8043gi0W4p/Iy+C7Cx6GbvA9ENITfFnj3sFLjcR1EgCwlJkGKJB9nhLIT6HSS3LdoLlrPLlQSIG5l0Micr8PPsDlpOA7ho9+ksJZqVV5zT9WfVmi0b7827BPMgXxqeTL'
        b'EkN5+N4vSx6XLC3/SvdlCb89OjHO/u7Pr5+Jtrcvbz8Tsy1GHFd9CyGbOSD03R93iZZP5eLh8YJqaoRzg2g/d4haZIIPC/WWDHWb2K4yTwda7wdXe4H0bniYu0G6ZaA7'
        b'pL136DE1WHiHebywpCWORS15Snh3E5y7L2onvClVnYj38ABuf7KT7InLECGJD4c3hisMcfM/5Kz0aMKbZ2DxZrrAnaH9okSt/bzkKwD5VyXB2sry7LKQMpDGsn34x+g8'
        b'8vn7x0GwfCnR0PnO1GSH43v9Bbdj/Gje07/JtjOw2HFzpxuwPYTnWgrs2oFus+pRwDukO6Xl2jKb2dIDiRZb9vQE4lZ4rOgG4oZ+7iDusTPKIMFftst9loK9M6BLc16q'
        b'X9kZsNxsL6vUW1iRGM9gbKd/Gb0zRU/fSBrjHojtlOkMVuGyE+qFS9/BbqPX2+rtNm0Nu5KVbgh1yvU1ZZVaemEoRCllbN/JkkIfE+jDy0W6dAfqWVYjdR2K6fRzXmpi'
        b'0LkdBC9iOWwGm1HfKaPvs6CZO/3pN+cBaxbNbktiNcVaDtMyPvTMX6m5hp0C75RUV5pN+k5RubamU6Kv0hqMnWIDlOsUlRrKlHynT9rUqXlzcmd3iqfmzZpuuUybbkNu'
        b'ZgoKQApVaqCy0iE5rtqVMkdhrk5WLvtPZF2Ro0rPFVQmyLr30GruGx5V+03Qrtq9Zi5ijj5pz+LdVnKzgNwKAtThyVkuHF8vZHdykF2knpy22paTW8NxfRC56c8hH3KQ'
        b'D8Sb8Xo7BQY5h/D6COqh2BaWkaPOzCkg9bm4LZI0R2UVZERmRYHcCoJVzSolvsWO7JCWBfKp+PxgJlDnkvPkImkpQEsAyWpRDjmKjwvOR/vxhUrcTC7EUZ9ibjzCLeR8'
        b'FWPt+MZEciKOnwVji0Nx5AjezqqaFboQvl+G/DziwhBu1eITzAEqDe8ju5hTZjk5Tw2THPIv4smVAgsrp0kDqXhTOJSTIk6J8J4kfJZtSJEjICicEPxNE8Tk+hgkIdc4'
        b'0lJJGgXNcEE4mo1Q/v8MKhll9vNHzJ1qznR8kTQVQG2gGoYjvJeermG7JnK8Q61Rq0APf6Sm59tyVGR7Ngei52nxFHInklUpG6VAUxAqwWtKJgZPH4SEA1ZHyF5NUCpU'
        b'KUJcJMxMPjnIgIOvkZbMCHq7RyYTI/EtUoeCcJOoNBHvE1SbOf1RJELJmcqShZcSi4Uukk0++EAFPgkV+iBOhUCrvGllpBXvUj6rwS0+ZEck9e4QR3L43jR8i1W1ffgz'
        b'aDVC0YUJJbG+4xYJmLOKHAglreRMXDxuBy1LDWoT2fMMa0UWWhyhVhauzsoBLcg3hsf7yZbVrKazI7IQEKd81YiS8Pe5QMcgD5r4kBpaD0A7CuFDvrjeLjgj3Bwh3HKR'
        b'KSEbQkDt3cqPxs85LpP9YAa7+6VkV05Jdp2fHjEECSxOSwJ9Jz4Rsfnak2kXpuv0DLxbQy8/aSA7mBNx9CoEiCx6JhHfYLV9l5WCqhEKrtKWzFrrv0yYLg4fWEdOGqA6'
        b'no1wH94FCKKAlD64pUSoL9dp81au49Bg3CrG28mmIlZ8KrlJduKbuA0qkLKh7Z87nWlnZIsRtzrKC5uFu3AbCqwWJS+eybozNKYvAuUyAwWWTDyR6yN0Zw1ZTx6O7B8X'
        b'S9E1kiLYabKBzZRhLt7lwFZeSe4Btl7nADi3JjKFdtmkJaqKuATQpLlYKDW/jwDxR0nSCA11lOPIcRmSGvhB5CHuENLukeuwOPeRlrgkWiyZLsoTY4S+3yfbhjHUw7vn'
        b'ZJLt+Cog+ERRMDlKLgqa8lVdEW6fBiVh1iYAXkwjDWxVha7EZzVssoaT1ggldfOWB4tC8WncwgY9doYvvZ6iRFxeEinXL3Fgxy18eR2+nR+XBLSeVndg8XC2tvEmfCsD'
        b'+kFP9GkksKxuIWkZP2QKNMbcIptxQ6EJP4BygFap9MjOMYff43RyEnfgenJTo6H7BbyZm5JSLayPkzJ8D1+Lg0LQ94mAizVkMxM1x1fN1VBy1kgaOXyStCBpX94XH1rL'
        b'Ol5VU4v+jFBYxfCSucOD5gkLhJyKxQcH4au4Izpegrh0hI+lk0ZWWQm+aSINsbg9O4tua4jIIw4fwseFyv5imIEaARMjxpVkXZozDQk+VBfX9VFX06qAEExF+LjByBop'
        b'JZthdR3DDzRAUUB0WczB7C5j9bw5dBAC2CW/XlqycPlKo4PeDyFXNP3w9kzq6SIWczAnjfgSm+hppANvJS0ScgrfRkiN1KRBxFxhJ8GUXGVHBGZlgL6roic0z0LWhiig'
        b'9zmRQIAQmhniM2TWSAaXxIrZ7EQn2TBUoLgysp/He6xkf9dty2WjmRk0/6e+JdkiPkpYu+Q8PoAPkxapwo6AdEUqU5h9hTRGZmi6NpbKl7CtJeAzYtCkL0rs+DngAnRW'
        b'J+TB+mgooIdRxM8CORSHcIvII3KDQbbvzFHkQB/NbNIE2EAOINIeiesYccbNC+e5jiSTe6MdLXFobJ7EoBrD5mZZMq4jh/zJsYV03cBfIn7A3vYway4+EgEzkUN2ZKiy'
        b'cItM0PxixGjcbEnss45rqubOHYwAe8O29CmZ+IWSFxAbn1ZPJYd8yJFw6t0EfwZ8l3kNk5bkEW51HsQdjkp5NG6OJG4CwIvhalsuuZyJr2kKgLNy5DIiD1GR49KoMLyv'
        b'kNzHN4AjNwFbX8UNBageZhhgwdss+Da5pZkjTMUZRG4ETGdEbeCIudQ/wXHcOxRfF+ZhBG4Qk1vzgKXSZmEirpaRQwHkYhIEHsBfEN7EJjIV1mA7Xd/qzFwomKmKnUcO'
        b'idEQfFBsjIOlR2E8ZiRpIYdEoybREybwF5bMiqbUkkseJfFunoeSh8RVwPx3MCqWVguTAtQHtwC9Q4ZZUkZTVmrJbeqp6IQakNzLKKivaMmiZ1gpiz+IKy2iPlHUHjBi'
        b'BrnOpjiUXCWbGQ1jW5BMbVfQi7GG4ptisr0EHxPGuh4fNpBDkgqQdBC+D39akFFotelDKO3m59OlshQttVSxzljIjbEalSoTXw4jZ/ClLLrI+k4RkdYVvEASnksn98gh'
        b'Ob62lMoy1LfnFLnMVg05MDTV7TQleRTDznzg0zMZQSabyaEifGSdNSAACBOsONJGLuLtDLvC5H4IECq/bliJ/MsFAQLBqAmXwvolp/FB0PaQGbeRJsElvRGfIBtBYsug'
        b'Z78bNXmqBHyQdVQxREzap4P0QDWNjxLHcm/AclWsMK3+xkyGTBI4EL5Nlyi+JCYH8QkqtdXinbWGT0+/zVv/AbLt+z65i9581/RWfrD0o5SXtr11I+eTrSGly1999L/9'
        b'OkPCWtec+2rBnW/OZMVcPBm27/WAPm/eTe+f99Gf/CbKm5+3Rh89XNR/QEHssc8ax1t//M2kjdv/fDzwg6CPmirPZ6e8vffHr34zKerszs74WdcG27aObc3P/cm16xd/'
        b'9LPnLu0/PvrI+RfMn557Zl347wuuFa3NGVT16vmthx/rDn56YGf00knblv7zrPIXbekkUxH70pu26zm6o/r7LXtfDtx7qyVfN/4n6vH3p/+1/Sv79TzduhN/5HZJ9m7K'
        b'Ddw2tPzdL35f//LP0+temrZjwBeHg1Nesbz6imFX3JYJFdNfD/31g5clexty1dsWlt/9RFfw6/CfJHz57srp2zr/WTbx6CezMs7Gvj7u37/cqXzl9LtTKv/1xsgzcyIX'
        b'JPzPZOWfQg9O/F3On5pen7b4pE/84R9lLd8UmbDjvdghV8bN7LPsQXvoiqVG+94zE08N35O8+CdxX2xNkv6yY9Vw/d++OtWy9+/3+yx9f+eSD9sPf/6vcaYfH0wa+Y+8'
        b'S3Ovjb8z9sjV8ooFh9/995ZAU0NbTuOX4jujK77+49CvX9Hx7w9YGd1n4uE/737944JbB2oiQ4/2C5+4558Vf1/kU6P+46h90sXbL7/3yi1pzdg/fLn6T/yDv5uHDK6J'
        b'+KN68p8WfxL0TWXCM3cP/6y0+JvZ+1Z9d69P9a1Z78/bVvvT+VG7z5r63sh9u2ldePB3pmeXKPuyU1B4Q1GUux/AHrzB0xegsj+5zI76zogBVLxdGkEt5Tw+yOUAK7rD'
        b'HBEmRwK2NviTU1SXkCLxNA4/nFfFHFw5Db1jPahaDisNNwUtD/AdgfdKUT98TGSeWMXsw2lh4/3xhcgMuwr6IJhy+5B7IqjysOCGHwBd2kMaxuOdHgekUD9WvJxsxG24'
        b'ISoKXwY2zxxCZeQUjxuG4TbmTzB/Ej7JLMF4Oz4rWPlkObyObCI7bcw97oAvacVNKbCyYGDLubShE5jVN2Mhued0HMvAx+nJZ16F22ayyciYLMKXhpKTXcfw8NFlzJCc'
        b'XUUv1Be8MmrwAeqY0acImqJ9NXBp1BI+gWx+4ow2vr+O2bbxtoULmMMHdY64iO97+lGQ3eQqM12GZQOcHNnwlSQPN4p5pMFGX6hAdqSton4bdC+Cai/UhRiCuFWYgogU'
        b'UEFm4OOC+8YD6fInbaHR5DkODaG2UHIItwueGZu5ZLcDEfhIkHA2jzTPE451b8Ub6WnsKLJtSmCUm+vG3IHerpn/wU6dnSKtTrDVUL9Sl61mHVJTL1wxF8Ic6/yYd26I'
        b'85cP4br9Qtxgn2BuDD0GzQ2EEvRfzsn4wZyCC2QlgrlAljOY5Q7m+tHa+dqALiMM9MXD0Zea1n7o8TJeKNVltb8Cj4vUEEQx0GUIWo/eGezh9uvRC+974szAJ7xTCdVJ'
        b'XAY+jpknet4Zr3hyK06BnjRPjBfME5ljmEg4j0cl8pap4Uiw+jHZ9wR5SNbjFglaC+x2OBo+R8JkiegR5DgVBsgFfAoNQoOm+9mpzdxehh/GiVH2LBSLYsmFfgKPDJSB'
        b'avE8Jyopke8YpkNsQ+7NxTQyeYp/SYmxWWkQRNPsKmomqezrG61N/UQ+TOB7/ADSHBcvJvW0PbwHlQHm32SCQN5wcjEuXloyir5lA+mDk1klLYPpVSfRC3lFSfZqTinU'
        b'rBvZB4afrwioLpH/xbZG6MOibBr5TUFQdUn2zMpZQs4mtRwNRO+M4/JLIueH+wo5/62jkWER4vyS7A99Fgs5f7WM8v71c7ngksh83ibknCr1h8g75RKIbNJMEiK/SKFO'
        b'Bu3R0KXId2unIkGHaozF1wuplDgH5OmKGCRZDno/rsMbBFffjprpcdHUCDOG7PdFeLc2gLWqHT4KTUM7qwJQCZ+5vFpQLUDOuo+v0I1TmKYmKhuA6tbIpJdl5Dg5TA75'
        b'AXEEUOFb8AeCz0HBBkPODaHXguADk0G8oBLGlgI2s1NShpAWDgT1IqRCKrJ3tHADTiU9zN7Oi6aUGAOidYipvzPKyX6QK/fQX1C1yFaQrPzwzcAa1kIVEJFbGKrCW9LR'
        b'MDQMcrUImuxVsn2Jm9vxI7JPcDsm+30EEf2BbGYh2yniyK4lK7gQfHOeMDFXgHtsjPBBw0AbqEE1uDlOkMkPkgN4D74E3w6BkrESrcTtUgGJ15PrlXT3OBbQZBVahW8I'
        b'm7UMNqSamjLC1vpT/8QFAwXj8fuf/RVWzi/mUkeDP//ScGrKULE1HpbQolO/qtqVSm9L2Vqx/HdjXn8rc2hd8K+q0bSAYZ/wd3HUhsM/tgTs2fLr2Jnv/K6Pz/FpKZJP'
        b'xPVToxePfyE9PvVP6+7/qVN5542UTfvC/U/0n/355sbKsFPHP35hwMm+P/umcv6Mvn++XP6bS9IizZEPRmX87xvq1lVvTxs/7+yWt7/doT8n2vZF1mzzgDMtt9oftb+w'
        b'daX+yuEtW9PrEjqXzbZo/3zui/s1i94i71jube38Q9Afvh3yr2c/La5/0/zzOftEm69oLozfHL3s/2nvyuOauvL9zQIECBAR2bQaFywIKIIgalVQoMgmiktFKwkkQDRs'
        b'CXFFXFBxY1EQd8F9R9xQEe28c9rpNtNtnE5NO6112k5nutrOTK1T23d+59yEBJIUO32f9/54Rk5yk3vPds/9nd/vnN/39110rzED5dQs26d84U7Q8dCM820ug6L+1Jyx'
        b'8Rv9+kcXr/4U8ElsXMXkq9qk2Mvafq/65EvbFyxv2r1o9vvrE2N36IeMabpZ/4bfgNQv5u5v/N3p3TFv9sn4bHlp/iuuH/3r5S/6VGTd+fbcge177qGip29HT3xr3brq'
        b'QX+PqSp8vi7En7rHeJKpvRNtXdp/oENXvwHlVFGY0Hcg3djPCB8hKMU7yeRzRYiaUA0DnuNTI/VWGGu8YzC64IVvMAzQCWI7VLFJNZyo4czXcmI0A53XpqHTMJmmp6Om'
        b'PrDAVYNr0gScd7wItcagK8yZvH68aA4xyc+kQCXwZgEgcYYQ82EN9bhEJ5+lzpw9PS77xFE9ayraR2tCytmOD0FNQmGloVUgLkMt6ORkVsgWvK4/2pJLfUvMniXoNO6k'
        b'eJ8Jbpgy5eBDAoaQp8uWvs+I++PNKfSMShVstVO+n1n6NFoPaEiQCJ310bPyL6yIJOVftHQt7TME7abuoP3Q/kzmkXoNb+jh6JmCNjBF4PBq1AqagsgaxI9PKBn68xba'
        b'm02zQUdRbXdHUHfUTnXHlZkQOHdUchhe4zFyJKxRk4riUyLcgE7gdlNG1wfz7EFXhls6qIJ3Kj78JG1R4EDwdSUn1aY6cWIhEQ0B6CCuLWDeC80GMEhNGIDTAxkEAF0O'
        b'ot6mfeYv7eFGgDajy1auBM4DiJa0nt2gjdNHgDZKNVF8mEgbpo2WBlGtjMjcTny2h15m1snwDV/UvoK/1+cTC5gfLKhSQmdemcLNWUwb60S1vqagPegqXsu5zhOiY0Ry'
        b'XjZtH/dqL0wM7nVUq1JYa1U6qUAsNMH0fahO5UNevuTlT15w7Ekh+z70DG/+D16m8DNSoZtALoRNU6lQQhFUKzy7dBco2I43mgOYlKVz2nmSfGlDXWq02jnrViTJQcQy'
        b'2kbfMuh/XQMc+HUnGwVXW90SSKj7LfXLBZdco8TkqGn6BFtL1MWRwaHAW4c6YdCderqJS7f5jNKczPiZ8ek5s+ZlJmYZRXp1uVEMqHqjO/9DVuKsLKoI0uaxDvrP4zTo'
        b'gNgsDPoK2iARyfr0CgPl5Cn29PB09pHIXEwRGZzp7XW2ermJ2G1nR8Juv5peMidPgY/IP4FO5vno1Djeo24B3sWjK2WzRNm4Ksdqi9lEakJDj1lRroobvSglqZfpXSU0'
        b'fxLVuKiGEfUXoA5e+WKVi0piJmB1VblRgIqUJ2D1oMee9BgIWL3osYweSyhBqxslaJXyBKx96bEPPXajBK1ulKBVyhOw+tFjf3osbRTnc1ArVcB+YaMzQFAWeagCA7gW'
        b'TwBr8Mf9Tcd+5G+XsFagCuJR1i40DJF7tVe1LN+V0rhSclXymyulShVTcIskWwa9oRpcI6hmar+02oMo/UNUQymNah/VALp7P5ynUU3NSHzYZAVMnmXi9yQ/MQ5VeTAw'
        b'ZgADkrJYBWNc052G0epgxCzAR/OUR+RTSa6+RAv8zADrhqC3jFASgu6qS8tZ3GeK8e4Wi9iSrbUb72qIi9GV5/ECFhz+I90SlrDonMCHo8pfYhQtLibfFalVGkMR+U5S'
        b'StqztESn0nXxuvYgVLUOAWUKsu1KDCg3fqfX3RwC6ucoVfNDxB/e7zWlKnT5L6ZU/XlG1R7sqTaB7r+QUdXiJpjrAWG6HdSC/GyvDsVypba0UBluqyrj5HmFpMg8Ggzb'
        b'McGrY35XG1yuj9EjP8vvSsYfixuckDRHrlXmAsU4+WgZijlkZLcgx4yyzGYtrKtO+zY40qIrbFSerwh5Bn6GXdYek6ztSAj22GV7ySRrM9Mudtn/gEnW9JyzbmdHco2K'
        b'v2FRP3fDTMKBDxbNH8l16gKNnvQwEVVEotHhFCY38LfNUAxBmx+bsNWLrZ0MnS+DhRXFsEqFdLLHOI56Z0xG+yx5VT39LShbzdq8FanqhjipbCy6QrP8kNizwRwX/PVU'
        b'RcWpJ104QxxTN6/MsU0Ca8qRUp10ZYp2jeFwc6kUH0XNeAMjgQ3z4IguVLh9oUL7SnQEH9j0xAJ80WbOpsBb1LfanC/ejtZx6Bra5I4OheN6mvFrMyiMYllLkEI6JzqZ'
        b'M4BHWOqCp7pnizaV0ZynhWZZOlGvwXWuaKc/aqGZ/WElrA1xydWLFGnvDfRlVLXOw8Js1RFvSk83WXEWdVw6BmrY7o6O4DoNzfTjObAww8na/BXSgfMqGMksPknUlZu2'
        b'8g1ODmOGikWmxNLYzqEOdMYdb0K7Zmm2vp8k1oPiWRI4Kfx3N/oIR0sTZ7y8OrwxfvA/2pzqgxW7th0SprVEtghSDg0/GO0Z/ddJd3JfPqkvaHCfN/pOWcgHbz36h8Lj'
        b'QLOWGILFNW1RYddrVu3+96fpCQ1vBu+9l15xwuu/Lq3cOPeB+/vvRZ19cGL85Nmjyk61/HB4Qaf22yz9i9leXw/6IfatNyv6D08JffmfXk5bY/N2pIa40XXlAfg02tTF'
        b'KwvGox+uo/YjOoQPUauMWMDhVu7c6ATaya9iX6soB/DFCGK3XbTMhvRWI4sENwjvFuPzo6XUrE5Ga7NxkxX/bJc1itYEMpTjraBJxJTsrzHRxxJz91whi12xfS4NaUcM'
        b'ZbQjlNrKqGUoW4aXLMTbTDYf2lEKZh86+GQ8baYc3yhb4szs+W7GPN6CLrDIHMdw3aIIvJcaoNbW51x8uhxALGJyTgfTYMPxJdyuh6WJWNwOSwhpVJ8Ndybdtd4FHcDb'
        b'Jv9qerwZpAi6kYW5tpqbQlliBc5djLGMPZZG/jQfmUhZidJhhz/2OiQdkNyApBOSm5DcguQ5jvt5d1ZJbzLxsGpTCJGWerB7Ley4Ndwdq2BqPWvee9ZWs7rkAII2m9SB'
        b'ARu7SrIgkoWvHBLJ9g7bmG/i+LTQnRxU6hlTpR4O7FYDqgs8BrlooZnCldeSHJQ631zqIFbqLyew5dGG4hyiGTkocaG5xP6sRAv96fEZVMU5RP1xUJrSXFpwl4qk7A4d'
        b'fTyK3AJT/5oUEgflq8zlB8LqhIXW8otKNGktDkossCqR9K9Z07Ecw0KGOKYLHWY/2Iw8EV8RcCKHp5U6woLDPt1fgsgLQt5UdaPRcqX5UrNLuZNdl3IRHR3ifzp595qJ'
        b'SA1si70lIqInPw4PkSXvUI8sgYfIDAoeESYfYYlNJscU7ExOsmRRoZorqwaQU/TeujMXNF6eVVIENgIzrSF6GQ8wVuaWGMp5eh890Ubt9Q38AyoNNXSJSpNPiVbKeW3b'
        b'ulF8f9OwjKTbCvjYbDYUXfg3zUwMpHRkuI2OsTBX5MEm9hH7hotlvzKlvMeDKQ+Oz9Wp8wqLgfiEt+JohDabFe0aB3q9pqCYDgVGL9KD40ov11i2SkMMmgI7HCYmQ2U0'
        b'vckx48z2CpQ0OiQMFkNMhLhwhpkRN8+eiUVHpYZeD1RL0Hex43pP1ZRv3SBotUat//WIloKBWIhSIoXIR4woAiOaNGf5iBG/mHpJHkxplsIZW9HjZO2AZqlX1z8u6ZHc'
        b'DlmTPdKjkb2rhhUqwyH1UbCZ+mh0iHz+6Ej71EWWyA7+NhrUrDmaYlpRSlGekJ4+bx60zFaYVvhXqlxeRIO8qnUwMYVRXjOz7WtRoUjHFXLIx2S9EsKellGmJ8VmtZja'
        b'Y8niRIqPirBPyGWJgzGtC1k8JuRb8kQW6zWsUiX5tvmtVIvIyKD9ARfQSLfKZfC5l9Q+8C/eKhM9XRLT5BWWayh/k76LXaznM2s3z3D5aKBGVhuIcDVnQEawRs53EZFQ'
        b'ReSJS5wdPktZnquGZUbbbFPhcjJcWDhOraFosbrQdv+Hy6O6nUZLUxryVxjK1WTmgCjH8jklOj2tlJ08xoyXxxvyC9W5Bnj0yAXxhvISmN8W27kgerx8WrFKs0RDBrNW'
        b'Sy5gHGj6bi23c3WMrSo/fgeNtZWNxqJaRY9XrVhb+T1ev4yjHdnV9T/T8za/nMVGMqwHdqv3Y49Ey+bn60hrgqFvzXVS5q4wFITYH36Wl8vHBtkfgFYnjh5n70wyzIpH'
        b'9aSXZD9Gd88mxl42MY6yIYPC3D4HecRanma3aeOsMrPRLrsTGo/TIxKO/0T1AaKTEtlqEuXBWWyOtTthd8EAgdqcTIXsiOg4wankUF1M/sgwl8McFOuAHd0MILTOJrJb'
        b'NpEOs6FYQysOvmBKvJcA80203cvM2ER2aeJsKqnhC3kwecj5IU5uu/1uMOiAixDo3flPYXIL3S5x9kx58Fx8tFBHHlJSlzH2q2IBi+zKzPw1XylTVvrFBp2+Z6UcqXv2'
        b'1EuqSvZe8zOraPFWS/u902EogHO8PAPe5PMjI57t/WWR7LJIepn9u2FChvIqpInxnhjLjsYBhY2SS+CNnNjzPPtSLFmt0xWPStIpDSTRjhyVpCHanX2pRU+3L6sgH/vy'
        b'CQqwL6AclUykUmIhUcKI7LcvmmjdiM6msl0Ne51HtFi1uhw0C3gnClaMQ/0ut2TZeDnsFxP9KR+0VvIF6XP7NxUuAtQuu0qplcOBwyvyNOXwQJLUobrHwMpwJvtAMw4D'
        b'PT08anRMDBlp9usEKGFSIXhzOCLzlaS1SUSoODqJ4ozJHYI3+fwY+yfyYs5EM+pgRJsQ0OPlU8gnpgnPjxzr8Hzzo00vsd66c9jfJlw1fyW7P/aFNeCpiYo2JT6D3B77'
        b'EjFXk0cynDaVFG3jibRCRvcMjc7TJsVlAKui/0wXTqFdPNqfY5DRDnzM00xNSFFsSnxeiHai66iKgdgM4Ioq83aPU2ifCVbwCNs9o6JTp+FjM8wAu1jEtqdihwMg952Z'
        b'Ermi4ocMPx5Qsw12h4A5AnXirYC6Q/V6Br/ejY/hVnQI3zSD33jwcghqphleeoZ6Kpd5RSj7V7kpOUM4XNZI6rc5lJwNpHvTwSMQnU1JZ2GJuGQlvoC2zuSWjXEt8EJn'
        b'KdTniK+JarDI547/7+a2se3DZ2aWmPakuuIPheD2LJpTMtuQsOIZrEF7pCERAzTF32wU6O+SLAYPfWlDbXqKaIZs/ZmHv1+9IPXi0n5PTcm4OyeioyR/+9r4g5c2/+5a'
        b'qc/4fXddhwleHz4Qf1fhUvqHMbP/mLPr/oXMgSdz3+r342sPLs9a2tJv+N5zit+H/fjb/bObnkw89P2Ns6XrfAte0yXcHpv8ZW3fh6HhPxVOeiP7nPD3Bz7a37moNPv1'
        b'io8lR9Tn9sXeGP3W3599e+ePL75y7fe3j/f9Kfqjjk0vP3pLYeiva74/P3nbe4qtlQeUwR2/Xd23Qfa6X7t/0EJt3qstN1+aOPCN6uvPpS09pLyzsfXpSO/Wvh9WVT6a'
        b'PLVs68Mv/O7/MdnN9zchErqlNNHlmdB5Yy0Y7YTh+EAm/ckP75iOzqQV4TVmYAc+n0p3lOKD0JFQdL0cb54+DZ0Vc85a4RBvfJzuKKFdeD/e0SPKEVrrLJagvU7lcKPR'
        b'QXwt2WtG9w0jW7tFZ5IoLCMLrYuhkY5McY7QyWSLUEfZuINuo63Eu1GHmduuFJ0109sBuV1jEEW5LEzGTal4l0/aNAEnnCkYMQXv7onJkP5KwbfBeY1uUUHscKstqtXc'
        b'dAmlqBMLPAXDaOAj+AzegW789pSQ+hYGkndfgbdghdS8EaNUqTKsAm90LVSD+7XFnpTrY1U8RGyRSVe4TXNLFtncmNo9xHJjyqqWtgEZNIgSeBRx1WJzEKX/Z/npIfnh'
        b'lvQkzAtikr9ZDo73Co1TnCLM3V/FsWjkO5aiU3rDjOgIVAObuWKOPB2CVUQUH2WgFApW3jJX4i7ihqImbi43Fz2HLlOkgy++4Z81Hx+MjmDo2hscvozbV9LCbnisIvK6'
        b'NM0pQjlhQdyTPAr4GG5ziwqdMMaZAUhwC6pjE0mLCG+Nwhdcx4h5yMlpfE0Lt/83YvBzeGmgp1wR5svCBewZDSgS/0JhqULarPNlqIJZS+HLtiinUoX2u7ipDDCyfB54'
        b'X0j0gkxF2tfug9mZBxYAtKRQ6kK+rFiZzs7M0YCzwt3xYplC+k2aNzvzt9nwZdwEJ5lCe9CgZF/eXgkVOtnfVa7Q9quMYnCQTLxGkJWCrmdmZnKcIIGjqLszFJ88HZ1A'
        b'zVFoDRcRAcEF8FEOr0U7+B7Ee2eia1mZuB3XcoAMPE5+xBeWs0j54fgwQ6so8BoAgFO4Cj68jPVYfWpWVMQAvJMCVshtREfxUQoJQkeUaGcWx7nncoO5wauHU3yJNAVd'
        b'iBJzKXMpTqgRX2L3Y3Ml7gTcCTrel+JO6vFmOioSifxtxQ05C6xgJldQFaqnAI+C1SOzlpRlykUAm+nnjA5FTaV+qU8SqbzWBDLBe3A1C8YnTInFBxkCBDr7v5aAu8mn'
        b'C10UirQbQctZv34QDV/G5bgpFNp694lswGSjmz5ZmR54TSY0uQrY4IJpFg/6gsfOgz4ucYoB/xqznNcvbk1IyhLgi5moJYTjxq9yx4eS/Fg/V3nP0uMz6LJHFOkvIVAm'
        b'38xB2zQhLcvF+lgicgyDZhVtB1beWTrZhoK3X6v79qvdscN+cHLLiJ+WmLp2/fr1bzRID5VNmXqhNWzYrnHoyxrZPe72gLVb5k14xmd70KtfvfvPzj1jpzfOmBJQ8uCf'
        b'7Zmpkdq/7YipWLrz1LrLr3z/cUW/V/0+lh6c+YlG3djP49jN3SOTL92/GzBoUmBt4RVty/dn3/6u8JhXoV+YYZ9Ep86WnM0q6tuSF/DsG/v2bq+vrT9Y/2PTstaU16a4'
        b'TKn+qfDq0ZkuR7a8XfmV5A9e2xY/2hD8yPePUas+n9f6vddhjxO3Po03rJt25y+yqotP//Wdk/l1rn2f3/3KpZxluoJhIbJ3vv9yyO7Bzz+1Z37MYM+w+fnZL4xdP/Uv'
        b'i2cELH55yaO/fbNj9YuRL2+/9sTchruqp2NaL0m2Xry04etrKcv/PSnduHphdvvQ+eMaat6Idqp77rZ+Sf71qyE+1J0Dnw/Ap2zNzmPR2W4TNLo8gbrgj4olKgGd9NEl'
        b'vCUcPPRvCNF2cvVNxo5b77U4FG1QpqSnCTjxYAGZ2luWMHaUowl4N4s3WIFOsZCDwuX90XNUC8kdK8Rb1S5WcFeXIOpbg3ZVzkrthiFZjXYA5EGe6ORKSrjE8Cx7IsvR'
        b'Vnw+0AwjQS24Ddex0utxlQtASIgO29YFIykbSCEi/iloo6X3zuwpJgxJM+qk15f4Am4sJWamFdLlHDpBQRlJuBat7e7To8ZrmVtPLT5JK1iBmvFhdAbvwsctQbTTqT41'
        b'GF1AW1KnhaEbuRYgE09UJZqCD+F1zEPnBLpWDJQQt/CRbjCTI+gcCz15Gu+MItksRle6QCaeq0QJlTw2eEW+k5WDzwoNc/EpQlsZFmYH2jsAbQ1Eu7vQI+hgjpihXOqJ'
        b'XKnhoSP4SB6LDSksccZNvHvTOnSqu5cRbhhGHY3i8C7GYNyGz+A2y+4m40mYZnaVQvvRDrsh4xxrYWUmLay4pxZWCloXTzYmlAmZu7+Mx80CwkNGtDDQwWREK+uiYJTx'
        b'f8zZH4gsnIViHvkh493+wfWIZxWj+pBj4jLbTetBYQYq2IDuKtga7qB1uMPuhZJ8gFLnV2YyK/x/JrMeSpttJjMXRs2I69HREaHJ2QEmMjObTGbEitlPlYbVI9EJxk0G'
        b'xGSoJhG4yYjVfYFqAfjM3NGhLqjNk1KT4aoEOpmPn4wPhw5HW0zUZMvwNk38+tOcvo38OPmzGmAmQxGyhII/ecoqD9/lNu3YIcpsP14miEsJbtGvDa4X+oR8vnHM/PhU'
        b'zQc+E7Z/+v6igvc3daCGT+Pqjg375PnvdgafH79i0VSPm8mRzU6xm/51k/tg7IDnrjzfOmNd0rjTfr6VsrYXllfmvpgx75vr6jPCvqcPJ3RWC9bPf7O4xvjnpe8FPjnk'
        b'9r7nlH8OWP/uRwmXP/5N0tgf9owrutKctFjbGPGOsm7o6ZJ7om9e9RJ2jq3vzAnxorMHOleGOykDHBm5hhJgJVMMY5Jn/1A/InqPoCNdtGRASoaqVlOxpUHn8ckivIHS'
        b'lplJx27NpBfPQzeB9MJEOSZcNZOnHBMMorIXn8MtWV2UZkIi9Y/zlGZ4L77IKrC3FDWaackEaFMAT0t2xo0xgxHJex1tiIViukjJWsIors0ZrcE3LeMFh8soJVlCfzY5'
        b'HVahBnwm3YL4UTiUaNnHmUjfSRTwji5SMslKEynZ/mh2eS2qc/FG9amWpGREFWxiaL+9qB2vh8BQXdRkQEs2vpLWW47XofVxEqBR7mIli8KHGQ3wMXTAyQJBijbiaso0'
        b'1Iy30Gnb2zcXtc4LtaQlS8VrfxVeMsqkRYX5iJ7CfDUXPsQxNRnIxF+dmmyQ2BTUeE23119skJSZqkAKt8bgMDCekL5lhHh3B+AZOM4ShdcLt1IgIzQ6acrVRXoGo+tG'
        b'RdbnP1rl6MW9ukqSwSJ++UPiLBaSiVXoG9x75jG4i/4C+VLvCdT88lrqrzdrpUukTpxHoBA3jBWFCDI0xfWVAn0gmY1+c9MtsfZ6cRWgzP3axlVwn0RMWjco6NmB8sT9'
        b'r70wKjB1pPfe5LKGxMCXsgqaWhLe/bzi20HfPlG54GGn17Z1HeO/Kvh3dWtyfsH+zz4IaFWv8nh9W0fTj+WXtkWMcv3xiPrwjfElu+bERz532/3P7Vs+/2z6uaTCxmPn'
        b'y91fz0Kyr7cNXXh/b17GchzgV/FRx2aZ8s3vq75LuDh9/V8/jx7Y9Ixh0pykD6bFeNWgwAv1Dxq2RZ3cHJS84djQI5WjGo8+fX//qmnza4tevr3r26bQ9++vnTgpJiDm'
        b'pef3BRTdfnbwV35OHoEutcOuxt1xqgpdnq37seS166q57/VpP/n8swETY/POF5Uff031lu/zZw+3H7h3N6tBUX1z2b/yjjhPzHrjEZfwYX5axZ4QEROnVTpiD24lOpgg'
        b'thITK7UWn3qCrd41zkNbeyzeZeODYglRT9dQvRvfFKAbVotx5DxOYlqLQ1vQpp7raf3/Z0baYydEzohMT5rNhAKBJTk52hKlKieHyhngPOAChUKhYIxATuSKs8BbKAmU'
        b'+wSO8Jns8+RTIHUmSkSe7sNXc0t0fzA/XCKjMCfHQqgE/h9ovUB32/xsQk1hImDhfj+Ns+RLo1bFIXU22orqiIzfPD0NbUZ16FyuC+cZIHoCHU/SfHnxJ7EeUL1BX3zy'
        b'xOZxRKfwcfrpuy9lccnaLXG547zntk3JW9o4rfofD65KxgZd2xuQfi9hT1Jg4b1dt1sefvOSaPr4U3f6ZT3MGXrrrZTdpy6FLjw5qWHq5txU2dx3PzkelrBzzrX2V1+9'
        b'6I3FwqnxQ1FLvLt7dXTMO7nVEz1jD1e96FogXlD6gsd3t1InbVgqe/Sm15bXB0mygu8sqyAqA9Q+Dm3KhDl3OuwjAKFxPL7qji4K8Um0D+9l8ZJQZ06RNHV6OL4A58Hk'
        b'3Ad3AktTIwvZhK+RNp9lfQCgDTCDF8eSLvAWDazMY5iMmtGa1GnpI9JduCn4ABFwEmI5byynyzENhbAxMsqZE2QJ+3BERzkZRn/ArfKRoSlOnCB1CmqFzZIb+ALjKK3D'
        b'HRpKs0cKg5hBweiye4iQWFfN+DjTNjaVr9BbnIDWoJ1u04Sobfoq+vtCvAd3plIJCc/mZLUT54m3iDJwx0RaXXJhG+5QJadaBlEU0cZqFxGNADTNZF6PQrfwBmlfIb6M'
        b'2tBV2mGrAgHlQU4p5U/BG4Ld0CUhupw9lYoGL9SEt5AzLkrRpqVlBnypTFpm8IoXcH64ToS2kbJP0YauCEA7U2mACmgLUPP5uaO9QmIFH8TMck6OyIB+H5VKpEstrOLD'
        b'kQtujOL6DxOjqqSVVvGkn/jff7S6P2muPyNnbIidLjwLJVz1kLBQTNS8BINUKprUXdsZxvQBKm8GGUVadbFRDM7VRqdyQ6lWbRRrNfpyoxgsQKO4pJT8LNKX64xOdOXZ'
        b'KM4tKdEaRZricqNTPhF45E0HvhjAmlJqKDeK8gp1RlGJTmV0JrZQuZocFClLjSJiZhmdlPo8jcYoKlQvI6eQ7N00ehNw1+hcasjVavKMLgzhrDe66ws1+eU5ap2uRGf0'
        b'IGadXp2j0ZeAu6jRw1CcV6jUFKtVOepleUbXnBy9mtQ+J8fozNwru2Qoa+gTuq/h8+eQADed7s+QvAfJPUjuQPIRJB9A8ikkH0LyPiR/h+SPkLwDyceQ/A0SIyRAlKr7'
        b'EpLPILkLyReQvAvJnyB5G5KvILkPySdWt8/NLFAfJFgIVPrbQ0k++FDnFY40ynJy+M/8RPMwkD8m1m7eYmWBmseJK1VqVUaIhOp+wEtLbFuel5Zqh0Y30uO6cj1Yw0Zn'
        b'bUmeUqs3SmeCO2eROhF6W/etqd+6ASGMkqeKSlQGrXoSABnokoJYSORX9yE21oeucPw3Lsu0LA=='
    ))))
