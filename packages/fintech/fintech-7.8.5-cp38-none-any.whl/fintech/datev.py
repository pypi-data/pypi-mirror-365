
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
        b'eJzsvQdYm9f1MH7fVwMBYntPeSNAQgwDNnZiPAExbOO9kEACFIthDYzxNrbBBgw2eO9tvLexje303rRN2iRt03SEpG1Gk9ZJ2qYjv7Rum3zn3lcSkiU5SX/9P8/3f57P'
        b'GKG7xzn3rPec+36Anvongt9J8GudAB8GtAiVokWcgTPwm9Ei3ig6JjaIjnOWkQaxUVKHlkut6sW8UWqQ1HGbOGOAka/jOGSQFqDAEmXAk7VBUzPmTJunKK802M1GRWWJ'
        b'wlZmVMxcZSurrFBMN1XYjMVliip98XJ9qVEdFDSnzGR11jUYS0wVRquixF5RbDNVVlgV+gqDotist1qN1iBbpaLYYtTbjAphAIPeplcYa4rL9BWlRkWJyWy0qoOKB7kt'
        b'ayj8DobfYLq0MvioR/VcPV8vqhfXS+ql9QH1svrA+qD64Hp5fUh9aH1YfXh9RH1kfVR9r/re9X3q+9b3q+9fP6B+YP2gksFsO2RrBzegOrR2SG3QmsF1aD46wRegNUPq'
        b'EIfWDV43ZAFsHtsGUV6x+/7y8DsAfqPoRMRsjwuQMjjPLIPv45NFCPJkGqSLG5AxAdlHQiZ+0A9vII1kW37OLNJAmvOVpDlr7kyVFI2ZR65ME5NHKqTk7LRTmZLstmZl'
        b'kAe5ZAdpyiVNHArK4vHVyBglb+8FFeKKDNqsuCwJEpMr5JyYw0dTltkHQoEad0loiYpsg4aSOUtRKNkuyiNt5AQ0pTupwU063Ei2k4M1cVUwnSboJQjf4PHNFTPZPMOh'
        b'y4tQ47ocN6xcYSc3VuBt5JZ8hZ1DfUmLCDfh22kwzxFQNRY3BuFG3BKvVcWQHXj/RNJEWmhGABo4UozrJuJbxdxTSDnQuWkGCj0BdujbQa9koANyXAMg71oeIMe5IMcz'
        b'yHHreAfkNj8NOTqJPl6QGypAbmmWFInXwBwVOvOkoDTEMsPH8+jcJIpyOvMH9gohc32BDJ2KHwV5urjvj58jZBoVYvRODEBoks7886p5qAOZgyB7SnY/8d8i0aTPolaJ'
        b'v+BvJ/wiLZozB0JBfuZ+7moAUnxWWZb4jgX1hm5odqfpr2HtYVz0sSV/5L5cEBEjRd3IHgsFpGNhLcCsMX5WdDTZHp+pIttxx5zo7JUrc0lLnDpLlZ3LoYqwwIlLZnht'
        b'fLBzzVOFjfc8Mohue0mwa2P5r93YUl9HQuq1sfI8Cx3dTrd87hy8rWC2ah6PeBEiVyeTw+QUPmePgKJkfIpsIRfDCqCXEWhEioblTszDxwti1LMhswxNW0U22Gnn+CTC'
        b'm+xkF2mDnuNRPGnMsfem+YCnpDMFXyJtsHgVUpGzuIuV8EWSgtxZpFmC+NUcnMK9gxbig3YAHhqynuykpyBWC7i7LSd+/axo3BGXyc6lmnRI8CZyMoudOXKfNHOw39fx'
        b'DVjlBDSBPKgybay+LLIegtLGsOylryWEYo18i/7trEX1HQVh3+nfb/+ChfqMPvKcS+PPBO+MsTZubftb2UjFsN2vkC/WLVz+YUP+kGPvTDy0N6pZUzRpY/oXizM+ROm/'
        b'H3CJP9/y5tDN/OvR080n+sz74/XCNwOaPnk9Zony7b/dWpLeEXkpZd+/Ty9buvBfn5/66Kfx/0jKOrxufD/9r9pjt5zY0hD26YA/35ibVyNev1r0WJz22ZDjSoltCEzx'
        b'BXwWP9SS5ljSjG/g87mqbEpBIkmniNSPRDZ6MEvg+G6U4SOx2SrSkJWTJ0HB+BoPYGoZYKPEQwe0YUOsWpkdS+nLzNJcCQojG0SVuItsZmOQPaQzKpju4Ax8zw5UYXs8'
        b'jyLIPRG+hDdNt/WHKoH4MtlIKAVqIU1AJ8dxI6bja/juc0q+m49WWijmKIPZn//ggyLhkz4TSiyVtcYKYCGMOamBsRirn+sOsRgrDEZLocVYXGkx0KpWBcXc52RcOCfj'
        b'guCnD/yGwg/9Gwl/w/lIziJ19qwUdUuFxt0BhYUWe0VhYXdwYWGx2aivsFcVFv7H81ZylgD6XUI/6HDP08mF0skRBS/leC6IfdqHUapB9tpjs0mzNkuFt8dnA5OIz9bi'
        b'jRwaha9JCkmdxuNY0n9ix1/GMo1UEgApwMAtEsGv2IQWSeCv1MAvCjCE1qMSziA2SDYHLpKx71JDwGbZokD2XWYIhO9BAtMtERmCDMGQDoY0UBNIyw0hkJYbOEZ4w7ql'
        b's9lm5bHNe/wlnMpikdu06GoDnBQjGTm5OXQkkCFRgwjIkBjIkMhFhsSMDInWiR1kqMwXGRJ5kSGxQN9/WSNGMvQiJdDyYUuykGn54VCxNR9KIscFf6J7tej3ul2GBv3H'
        b'uqbSi8bfQ3rRi0vI1daEjalbZh06vifipXz9Ob1Zcp47r/uBeGfcYPk09eCm4AXpGz7u1392v039037KVb0cvq6mRSll5+F5sl0Zy7gjZY2xUhSGD+Pd+IyoFj8gt9mZ'
        b'G0W6BruqnM0HFovkcaIAfAZft1FhgNyOnasFEkfOkbMgMSilSIa38zWkzsyOE74ROIMSMG0WvgT0Nw2fIzv4/nFkg60vlJoK8B7cmA8SgRhJyCF8OZIj99JUrAw/moBv'
        b'x6oyJ/JMlJCRmzzePFGk5N3QUuTrfDEs7ZYVFpoqTLbCQnaO5HTrF4Vz9EfKibnaMAH0amct4fxIusVWo7mkW0xFve6AaqPFClKhhYLGQjlfB+ccl+K+JYR+hLkOBh1k'
        b'setgnA13Oxhe4xXzT+G/C9ESHYhWwjvQjGfcTgRoxrvQTMTQjF8n8icAIj9oxvh0OO7ArcGkGQCzA7g1aSnIpBBszpo1E2/BexgLfJ4cl0aUrDf97kfTRFYNNBrTfvQT'
        b'HcW5l0viI2P1OfpPdeHFZSXmIvH2X/wtQaX7o27By/1efXG/FB19JFv1w9tKsa0fNFsnXUfRowbfdcMOfE9vo6SCdJEd+QNM5AbQ6xbSolZVOWjygHVivGU2OSig2BHc'
        b'VEHRhBwk+xyoAniCW0y2SFp8VRWhzVdxiJeR1mouY8gSAZi8T7wAelhqtJlsxnIHalByhoqCODlXG+kCkquK0JWYgbpbXKEvN/ZggyVcGCbShQsMDahkUOxCg6Oh7mjg'
        b'Y4T/OsnxEin94kIMPWaXY/F9d1wonNiDDT2YQC7OMeW/8meeoWdmfoZvVPhU9E8dvz3Rrvml5pRGnFR1hkOXTLJl8Z8oRYyY4Nv4PrmrFbpXSuPwTgc+7JDYqO6ET8VO'
        b'8kYG5SCGDiutNiqlZUQF4sZl+KqLagAqxM9y8D//9ADgbvWGe+lTcLd6wl0igJUCuFtSrTfbvaAvcoN+LxcK0J0uc6HAgXDfKOAazD8xSBFQgArDXIn4f0MQOEfXnkgg'
        b'EQhCrwkjqFo2hzSoVOpZwTWZ2XNJQ36BIGtmguCp5pCNPAiUTilm9fEdLT7hk4AEkyPuWLN7mennSSKxNQ8arRq07xPdx4A35pKYPjH6TL2ZYoyuquC+vmH3eeM5/e91'
        b'rxe9yjAqW39eH16MXumznZu2v+9VmybOYDBk6mUl7+YEoLH6sEOhcx1S4zpyvBwEOryD3IrLfEqi22JlSEdap04DlMOHcGuOO4fagFttCrorIyfhdnLCDxEarmVkrDS0'
        b'j5NR4fORAtaR/bhJKMQtwAZVM/CJTDdeFWVWOtiF2K8sKOCm1F5FRcAeTmUOAnlPxmS92hAHvgh13OmRwIRcCOmF/UCaetgUw0uqbJS78HJ3pDteeo7jpZ95UiWmFruo'
        b'EtfAfXtFV+wTIUV5pmsF+yTWbMj45LZCq88s/RRQ5gdFZSW99Ock1/r11agMVYAw2/TnjReN/Cv7/6zSXdYveXnBD5eQOWQmMZOZ0T/7zgLRmxGMF0m/G1b54XjgRVQY'
        b'mRqJt7uID2DBvecY8dk9gJWSXfjuCgZkvGW1i7SQs88zGE/DTTmkMS6LNKfg7aB9SZfxI4AxbROknPNkC0hMgpxzsEAQdfj+w3jfoH8WnQLB3WqzOGgU1c6RLRxEfTkg'
        b'Q21oD+mgVVirDpEAX/9oAEJLDwZQCmp3YUCzB2V6qnsln2ehWrkyhApTlPWBOhFUWCjYzuC7vLBwhV1vFkoEIikrBtwprbSs6pY5hCcrE5C6pSUmo9lgZTIS45CMRjKE'
        b'ZHNy0ttnak7CEuimFNAlUHor48Wc44cPlcklckm4zM7Ex4vJEcGgfFweQvUPDsnkvI60TfSve6jRU7oHv0hsEFFd4xC/SNKODNJjoGsc5+o40ENkDKMDu6XTKoCGr3rS'
        b'a6qxyGSrBAUuXmsxGoSvjwX54DEd4knkPKOl1l5qrdLbrcVlerNRkQRFdEFP5DlGW63NqJhuMVltHTzb9MffgwV/vh82VVtZYatMz4NNVkRnGCxGqxW2uMK2qkoxF7RH'
        b'S4WxrNxYoUx3S1hLjaXwadNXGHy2q9DbSJfFrFbMBBBVQtt5lZaKb1LPV2fLjaYKoyKjolRfZFSme5Sla+2W2iJjrdFUXFZhryhNnzZXlUMnBX/nFthUWaB5qdMzKmDD'
        b'jOlzgBWa4zOW6w1qxQyL3gBdGc1WyiDNbNwKa3WlBXqudY5hsaUX2Cx6ctSYPrPSaivRF5exL2ajyVarLzOn50MNNhzsvBX+1trdmjsTRSvp7KjerXBMBLLUikV2Kwxs'
        b'dpu8IsFvSWK61lhRUatWaCst0HdVJfRWUatn4xgd4xkVM0iX2WYqVVRXVnjlFZms6XOMZmMJlE02goy5nPYb7chSOssUM4yAO+RUic1KV0m31Lu2YkaOMn2aKldvMruX'
        b'CjnK9CwBT2zuZc48Zfp0fY17ASSV6QVwiGGSRvcCZ54yfbK+Yrlzy2GPaNJz12jOcorDqjx7OXQAWTnkFDV0LKe7Jmw/ZGZNzsijZUajpQRIBXwtmJ81fY5qSiXAxrH5'
        b'7CyYKsoA12g/jm3P1NurbCo6DtCcIrVjTMd3j333lU/33mMRiV6LSPReRKKvRSQKi0jsWUSi+yISfSwi0d8iEt0mm+hnEYn+F5HktYgk70Uk+VpEkrCIpJ5FJLkvIsnH'
        b'IpL8LSLJbbJJfhaR5H8RyV6LSPZeRLKvRSQLi0juWUSy+yKSfSwi2d8ikt0mm+xnEcn+FzHWaxFjvRcx1tcixgqLGNuziLHuixjrYxFj/S1irNtkx/pZxFiPRfQcRDhP'
        b'FpOxRC/QxxkWOzlaUmkpB8KstVNSV8HWANTYCPqRM1FlAYIM1K/CWmUxFpdVAb2ugHygxTaL0UZrQHmRUW8pgo2C5FQTFRiMKoHdZditlKHUgtCQPp+cKrPAvlmtbABK'
        b'9QQeazaVm2yKaAfrVaYvgu2m9YqgsKKU1ptOTpnNplLgUTaFqUIxRw980a1BAYMBLZnJDLLunfWwcdUimAUQjGja3KPA0R6KRnk3SPTfINFngyTFZIvdBsXe7Vh5sv8O'
        b'k312ONZ/g7GsQa5e4Mtsz0EuAfmE5dmMNTbXF6BErq9J7lWtrmoCICYbgR2XumWMSl9kqgBoUPizcWhRLWRR1gtU2iOZ6JkE8qO32oDbWUwlNoo1JfoymD9UqjDoYTIV'
        b'RYC2LojbLORUKSBRVoXBVK1WTBf4h3sq0SOV5JFK9kiN9UileKRSPVJpHqlxnqNrPJOes0nwnE6C53wSPCeUMNaHmKKInu3YVatD0FD2CEa+Ch2ykq8ip/jkr8xFynyU'
        b'5/sejcpdvvI9RDH/a3hGuT/p7NtUTvQ/soec9k2qAan0Vc2DBaR4sYAUbxaQ4osFpAgsIKWHGqe4s4AUHywgxR8LSHEj9Sl+WECKfz6W6rWIVO9FpPpaRKqwiNSeRaS6'
        b'LyLVxyJS/S0i1W2yqX4Wkep/EWlei0jzXkSar0WkCYtI61lEmvsi0nwsIs3fItLcJpvmZxFp/hcxzmsR47wXMc7XIsYJixjXs4hx7osY52MR4/wtYpzbZMf5WcQ4/4sA'
        b'AumlK2h8KAsan9qCxqEuaNzEFI2HwqDxpTFo/KoMGnfdQONPadB4rMcxxekWY7nBugqoTDnQbWuluRokifSCaTMzVIxb2awWYwkwwQrK83xmJ/rOTvKdnew7e6zv7BTf'
        b'2am+s9N8Z4/zsxwNJejLK0hXVYnNaFXkz8wvcAhwlJlbq4ygDwvCZA8zd8t1sm+3rBnGItJFOf1TYkOpkO+QGpypRI9UUvpMh3HFrbGX2SXBOyvROwvUHDNVivU2Kpcq'
        b'CuzQnb7cCGxUb7NbqVgrrEZRrq+wA3tRlBoFNAV26MsMoHRrYqLM3WRgzb62so/+fTAl3317V2Qmpp7dUYDwrXCIvGwrS2i5Y5OF74lu36lO2GOpesKl53XILNT+aaGP'
        b'6SzU2C48DqHOGBbqCNctsVaZTTbLEJcJL9zTmEef+qz1MOaJeI7/t1TC8/yXfBL/GvMKw4fUZIOVNMfindQPJg53iJEshV+H9+Gu/6JFr0QZ2B2UUVxcaa+wgQbRHToZ'
        b'wC5oHvoqo/lxb8GeR03hTwZMBUQoB+mCWkwVgu4DaGwC4gNVqCG2W0ylIMto+Pp5F2TMLReEmsqyCqOioNJsjs8EqlSh0tZSG0tPsofOpc/XLlIIzagtjVJQq8lqFzJo'
        b'mXtaOHczqOlPkPGFgSbPVRUUl5lJF8DfDHKJezJ9stFsLDXQhQhfHYaXnu+JDh0p3bkTTOanQqHRcbydiptCEIwc6l+Pocqh+DFxnap8UBkOmI2pBo4e2HBmE1Rg30wV'
        b'JZUKlSLDYnNOxZGTVUFbPpVJqyX6qpboVS3JV7Ukr2rJvqole1Ub66vaWK9qKb6qpXhVS/VVLdWrWpqvaiBn5BfMSYAMrQAYKu8aWWaiVyYkFLlGoJlOa6zCrlb0WGMh'
        b'U8Blp3lUraAyu1PzFsyuPWBU5MTmpE+3Vyxn3rNGSykQqVpKWGj+5LmK5HECqy1xVqFmYV/5DrwRinx0mL6IqQR04ZZyPS10oYivEheq+GuW+KxmvgsFFHpGM9+FAko9'
        b'o5nvQgHFntHMd6GAcs9o5rtQQMFnNPNdKKDkM5r5LqTNxj2rme9CBm7NM+Htu5Q1fDai+MeUhGeiip9S1vCZyOKnlDV8Jrr4KWUNn4kwfkpZw2eijJ9S1vCZSOOnlDV8'
        b'Jtr4KWUNn4k4fkrZiX8m5kBpgY10FS8H1rUSmK+NCacrjSarMX06sPge6gfkUF9h1lP7ovUFfZkFei01Qo0KIxWMegyODs5JCV6GvYSaxlxEzslLoYhS3h6GrIjOqKgV'
        b'hGL6TA+Ica7JBqzRaAAJRG97qvgpOuzduIeSP11mMZPbVoeY4FGSyZ7wlNhAKnGpVoyTqJi841MPcKzUwc2B9QOnoWJ0CROgyymDtxlNsC02l604C6Rdm6nEtFzvTv0X'
        b'MVXQZUN2FzMEBdLtWaK7mDTdKGgXRlMRLcoBqNGHY1ZBsvEvqLnbh2HeMLLebC9fbixzGrMZE2RSnBKkuDxLjD8xNg4+uvyKsQP5D+3M/fgy7qyw5uSRHfHUz3kbadIG'
        b'oN5FYnxurnxcuJcgK3cKsi9wnoJsu7Q9uD3YwLdHtUcJAm1zgCGuXlIfUh9VIjIEG+SbA0GoFRslhhBD6GZkCDOEN/OLpJCOYOlIlg6AdBRL92JpGaR7s3Qflg6EdF+W'
        b'7sfSQZDuz9IDWDoY0gNZehBLy+kMSnjDYMOQzbJFIWyWUU/9BBqGNgcZVPW8Y7Zig8IwjM02VFhVe1A7V0JXFsA+na2GNwca1MwZTsKiL8KhbYBhhGEkaxtmiIcySb2M'
        b'xWZEsrJRhtGbAxeFQ24EzGmMIRrmFAFjRBmUzc7wgtD6sBKJIcYQu1kGvUQyJaBMqemWTaUe2VMK5j2JD1K4/XNmKwQKIkQKedTokFiGU4SgoSqPmWN2PP3GvDOoJqCU'
        b'P6aeNY+ZxzH1q+mpbkl1Vrek0Y8EWoU6OzxmDgEUG5QB3UF6QzUQJUuhydAdWAykocJGv4bqBbWl0Ayyna2sW1Zsh1NTUbyqW0YdTk16s8MRI7jEBOJcYTmc2DI2drdo'
        b'2tzZgqeHZRx8FMvcUDDI8cucdCajpwKaAuul9UH1ASVBDj8gWYOsDq0NrA1aI3P5AQUyPyDZusAFyCBi2yv+nAZGeOwa/ZclTNNUa7SyAC7XXpuYK0OxUe3VxCtjPGgb'
        b'+nJFzxaNd4RuAUWhBiBHbJhjr/QVNq8e6L/oyUAIbE4ypFQrMmh7IBnFCuYDqLBXKYBwpioMplKTzeo9L8c0XNDxPQuh2PcMXI85vmYOY79uDp5oMV6Rw/7SKcyIz3GW'
        b'OiZm9T0XymYogQf2oFbMKQOSD9hvVFjtRWajoRTW8416EXxIBN0UelLooQtIC/NXmCuB/VjUiiybotwOGkqR0Wcvesfii4y2lUb6mFcRbTCW6O1mm5JF7qX5h4XjOIxX'
        b'THF8UxRTO2G06+mim31R6a8X51Ea78RWqwuYNFCw0qKIFnxVlpMuSy3o2/46cjhHjWfKFRVEoBsBRxyUJdpYqlaMTdDEKVITNH67cTvL4xXTaULBErS7ElMFnBqYo2KV'
        b'UQ8Ti6kwrqSPOqtT1MnqhBil91Z9A6dhuRCnUFUWjuQDZsAXXc6EtSHIPhEybYFS0piLL84kDVmkWRtPts2kTqSZOUrSGJenwttJS86sTFxHWvGlzLzc3KxcDpGd+Ji8'
        b'EtfNY92+Gy5Hn01JQWimTl6ZkI/sNMxkPm4mj3x2THaQbTnUKLQNeiatpB567+l58yo5wnsKWMeFU2UoRzuaRsPlfNkvF9nHQOY8cghvcguumpWpVhnHxdDIFXxZjFKW'
        b'SK3kKHnA4sNYL0c0UmTT9mfRd5/rJwjTG4BP4XvC9PAWg+cMSQN03BhHZ9mknOc2OXzXEoyvk53krGnxoRixdTV0lD5s1uBX3w7coJFvee/MnZv3trZ1bhLJ3giIjx+e'
        b'd2x4/ympn/cLqn/xh+YvCl7BDyLwrqlZk8csO/7dytcqGic+VlybefaFuYNvbqmd+8Xff3FMFl0T+tnVzvINMz6/umPL0XMhy0lZ5JedPzGUr9O+f23Vkz9l31GfSfrH'
        b'E3RshvLn6TeVchY+RXbk4UO4kYZLpgcJISEiFDZKVELOlDJ3/RXkCIcb8wGgzSk9MOXQAFInrsXn8FnBibvFlBAMW6rMdfjjkj14K+qN68UychBvYj0NJbvJKejKA4Rc'
        b'MK5HfYaJg8m2pSwEhNRFk+0Ga6wqOlPFIyk+wKsAIkdt1LI4GV+bCR2oVQxgoekUZJH4sggAepVnTpnBZAu+soI8jFUryXYQ0KT4Ip+E28klG2V7eCvZjVtwIw3zcsIo'
        b'QqWUoshqEX4A1XbYKJLE46u96ZJBZism7fGOqTqAjJCGbJGqRbjTxkJoD+aQ7XRRjXExuHOamtYkzaQlltZUWCUhdnyHeRzjh7gTH6A1qRRIx8Zn56hgaLxXRLag51hv'
        b'5O4icoUNXYkfeUiMA3CnGDfik/iC4DUZ9B8GovVErTBnUzooWo/WSDkpizeTOqLOQuGTxpzJeFoi5WojnKzZFc2S55wIczSlx8IyiX5k0A8qNlimIGeoDI3vfJbTskxo'
        b'1dPJZFcr1omPoJvHdPpUIkcb0P4h7i6t3lP1cGzmHL/MnZTOaQ16QfCe5/KUXHdwYY8kYenn2ja3IKMJZn15kUH/XAT08lfao9uIzrInDsru6MspBUQDxzCoKivMq5Qd'
        b'XLfIUFn8baYWVOiSLnzNzJIJH72gvSULvjwZKsxAaOJjAt9m5LBCT5nC7/B9XcMrnyl1/KcTCSx0MnW/UxjgmkL/yXqr0SUFfOshNzuHdAnT/oYc7BpyhF8Z4T8bXFbo'
        b'jEfzN7aiZ2y/csW3HLtUGFte6K42+Bt/RA/Ev0YY8TMLj0ADFgjH1yNXINw3CTP4hoFwojyTcd1VjsXXrhzUJkQzlZV8+v2T6CdNrzW9L/+O/JAKPfdI/EWkXcmzSJP4'
        b'ArzXnWQ76PXCOLKFHJgq8JQjCwY4mIUbucanyAWBZKsinhWZFlBIT5R7dNJ6+BlTG+5Gw1gFoU3fp3vq54LFQvgYDftqpQ/jgCZuQO94RKF59agM6g5wnErBj19qtVmM'
        b'Rlu3rKrSaqOCcre42GRb1R0g1FnVLa3WM70zuBjE9cpyQR8V2fSl3ZJKwHVLcbDb/lOSHeqEAY3sqA926ZEhrjj/UOF6hZJQB7iDG+QAbjmAO9gFbjkDd/A6uZs2+SuJ'
        b'D20yw2CwgrpAZV6DsYieOvhf7PCDUxiZ1/43UCiZusN0Fb2izF5qdFPhYGesJlCBFEJkA9XGrEabWpEPWO3VDz3+5fTRi6m8qtJCNU9ns2J9BagztCmoQhZjsc28SlG0'
        b'ijbw6kRfrTeZ9XRIJv1TL0qrmq7URI1ocLYcXTo0KNqnVx/Qtd1qqihlM3J1o4hhQIv5Bjsy3bHaMmr+8J67V/1om95SCmMYnHSItldQs6CVaiPWFXa6u0UWffFyo82q'
        b'HP/NlXwBX8crMjzYiWIxexC61F8zOvJ4BYtkWPy18Qx+exGOx3hFAfurWOzwrvNb33mMxiuoURNAxZTPxe7edX7b0oMHait8KhbnW2z+6wlHE6oKX9gYcYqsgnxVUkJK'
        b'imIxNWT6bS2cZ1BIM+aosqYqFjueDi6NXewereF/8B4yQFVsIaGgHbn7CPttDoQDNrMMjgYcV2uxxVRlc3Aviqc0GpudrQyztRLw12jwaR0AdKK1Ka8xs+t5GLDViqmC'
        b'iYAd0eEFNn15OY1wqxju11jADgMgFkygynG0DCZ2QZAetnWlCXiasQYg7jhw3v3Qf3mVNqNwTNjhN9rKKg1ASUrt5YBoMBf9cjiAcGiMsDvFRkUlMHef/QhLooeG2T6s'
        b'wjJNVrcpqRXTgag5CZLPXtyPHbWUAKrT64+KzbBg4eYjq9F3S53j8qPKYjZz4bnJhDKbrco6Pj5+5cqVwvUVaoMx3lBhNtZUlscLcma8vqoq3gTAr1GX2crNI+KdXcQn'
        b'aDRJiYkJ8VMT0jQJycma5LSk5ATN2NSkcc/pCr/GLkF5n3fYYGQeM7DjrnVya44yW6XOo5F6sbgjZy5ofiMLJGX5+KadsjbcFoWvJSGU1gcloARQJ28y3T52Or15oXVh'
        b'wCSduXLdcmSnptC182doncx8FmmIJc252arZNL51djQNFp0PCv42fIGcIi2Uz+/CVwJBr63Dx9g1SRnkCjlGboCKSzXAgDiyFUnIfl6+KJ5d7RJKjgaQG2p6TwYNpIXO'
        b'oXtQc4fi0+RRhpjcwx3kLjOsPFeJ95AboFHnziWtVR7Li5tJGvKgZZO2EG+YWwV/83OyyW4xAkV0UzA5tUDMpmLBXaQ+WK3MTluDu/DRIBSYzZOjuInstFOpYemKRHIj'
        b'K4A8hPYcEuG99BKaHfiinQk1RzNyg0lDvJpsgzHjcEc2KMwNHFLMIHefl4jJ8TFCvN1B0oXPkBvxMRziM3HLLC6F3MT72Ob+fJ4UyVHDiBCFLu5kWRlicxo5crk1BLbr'
        b'VhYbVbaEX0xOzyAX8DZ2edMk3IYP0QohIWqyk9zKIddiyS4R6rtq6RARvogfkAN2agcgO6aNC1ZDHzw+DhuYRTdGhHqTu+KwuLmm9o5OznoAqo0K0qhezw3CmnDJu6lZ'
        b'T37z+7zHr9d1/iVomX7S1YFK9du5FzRnW/tMOBevuPH3mvcSoup6z/vVtc7AEXPGRz+xpHVoH8t/eDFlYZp525MRT3a9o1lyJK/uFa7x1SJc8r2SY+NeM2UMXDQ7P3bR'
        b'GwfOvBbSTL5/YvLbdz554w/7fn1z7r/+uuPu2jX250+/vS7k5DtX744deG3bZ0fnz7kyNMsSu/LNVUqpEBp/cDXZKhhfnKYX62BqfJmRa6PospjsDXUho9MGMULGrBCx'
        b'SRLSQjrxZSao6u0jmfkFn8P3nCYYh/mlnWxhJprKAWSfmywrI/dzXOYHfEQj3JWzQT8yNk+VBbPZnJWrjSPNSg71IV3iRHpnhxD22mwWa+OiM8lmfB1mA0DEF/hVY8h+'
        b'j0s6Qv/Ty3L8xsgG6Q2GQkGGY8LyaKewnCnn5JyM68M+3X/E7OYPGVcb5RJ9e/pwWC9CBNPCIuT0YqN3eViW0I+l9GMZ/SikHzr6oacfRcjDmOE72jdY6LOnE51riCLX'
        b'ECGuEfWucZgwTy8iU3oI82+Ndhfmfa1IGdgtN1C3PoeQ1B0iiL7OpFRfzv7Se06M3YGOB7nFxu5gKqiAeEjdvIQ5uJZZHORGhanVJdxJhWlwP7sWrUemDwWpPswh14dT'
        b'ub4k3CHVBzGpPhik+iCXVB/MpPqgdcFuUn1LwLOler3LTU8hXHn0DWTXaTTIQaitAAYK+wViKQgFevcL/qjgEKcotVTaq6AU5GW9N0OqLC8yVeidIkoMSC8xjLcKrJWq'
        b'+i6vTjpBl/br1RPVhv+fGvL/ZzXE/ZiNp4ASclxGrq9RRzzOpdBeyHJ24FMmW/w1bp5+hxPOvTCO46g78gSxtqKSGm0sTHCt8C2OrqykcqOpXG/2I/gufoajK6gTvl1d'
        b'/c6YUihhvkWVlcvpfGmOWpHrwC49Sysqi14AwIOS7/u5YQVVg9JSNAkOOxhFBNDhaHeLe5xg/U7CRSDHK+Za7XqzmZ0MQJzqSlOx6zQudvOhfaYm6CCwnmBgAXaL3f1s'
        b'v1ZXo82f0tc8vDn/L1C3JhtXGksdvjj/T+X6v0DlSkrRJKalaZKSkpPGJqWkjE3wqXLRf8/WwyQ+9TCF8Hw4Z6kEtCmk0Iy+snTbtBeQPYlKi7uHGLVZuWR7XJZLqXpK'
        b'l2J61Hr8IBC3kK3JQ+xMUcAbxsc71KiialCkBC0KlKuDdno90jiedGnV2bkgybr1i2/iBz76xo2kMRCfDY6wT4KmK8bgemt+Lm5KzHfcZUQ1tfmkFeq3kAbt3Kog0D+g'
        b'T0jfLViCD+ED+GQgAo1vT3DebLyP6Zy98T3cZc0mjStJc1ZuvpbegqQRo36TRaQpwSb4fd2urbHG5HJLyI5o+uRQnYUvRXNoaKlEgtsWs0sTyYbaiGByB++YLSPNqjxQ'
        b's3gUmSQCUXsvPo73453skbUC1CNQBd0eWYO+g2/NnlmMN4AAn4AbJTUTQG+jihG+Oxw3wbzopLLilPR20V7kpGjFbHK/poxBqV9/noFQM/1HKQfi5yM7lejwAZuq+vlg'
        b'KUJz0JxsfMo+lvVlIweD6f7APu4kdzLJZSPomc2kjdyi6mcjvgCpHLIjkypfS/rLZswGdZv6woFS/BDUwg1DyQ1IZaEsKd4o3JK6G7eTrhXkLEUNqokfQkw/X44PkwtR'
        b'Cc7LU1V4t/nvX331VWyaE6Oulc3ghwsP5D/NoHolCtf0EZultSOQnT4q1JHtw+juNDu09sy4efQ+4/jsuYALmaSpIFoJGJGZ5by8WIlvz6bXqUordOReyNIl+KSgz7aO'
        b'LS0gu5OyRYizkV3kIiIXs8kdO72wOmkxuRLsANPsHmyRQY9nZa49cm4Qvkx2iRGunxu4MI7Usfuz1s9d2qP7zoomuwtknlru872lC8mVUHJgEFOGteRwgTVblZ8bT60E'
        b'eIc2Ps+h6CrJPgm+OZM8Yop82UpjrHDhplKKgvEjHh/rQ26k9mHX9t4dkMe/JEU1P+6zOurtBdcipYLbhn0sPkduOGwb5DzeLfhWAHqRbfH5ubOiHR26+y+Qw/isnLQa'
        b'qhgoFw7OjVVnxS2LBdVfilv4eFMSy38O9mMDnAft4AIO8RYuLTdTKWIX3i5cNoK2yMaHnU1qcYdwSW4HvgsnFRqNiREarYY9o8qmuIZc8FxcDb5GbkwZZTr66cu89TlQ'
        b'kVZ3j1raOjGPTArfUlr9i+pD67/c1Q/3PqecXRUwIFQTNDtumGH2cTtJqZsaMasgTTXj2PtLOmpev3firf0dIV989NO335r7xpHQ1F45uQceZ7a9uPG9q58dyp7/K3Nz'
        b'v9ySXn9vHvvnkdW9s/7ZsgY9frP6lGT/hkHHzpxb+6bc3mkaM9HWMX6wpGBt2WX1Z/cLvnhDMWJGim3vB5O+yBjYv33Ov18Or7154uyRpuKAbnHFoZz/WXIjZ+Jek/3H'
        b'r1rbXrb9yDJbkZV37T3ucelD7a/P/MBy+czcjTvtGy++suPC6bxjJTMr2n4mLf3nlFVZ+35VO6JL0fnB4Od/80qXsWvh2921wecLzxx7+Pbrb296oX7iobgdA3sZN731'
        b'SbVi769+eGhJb9ur/24K+tOBwfdHrQn4KvX87y+sHnn3y+tju2rI9qLausK3ktp+PPHDT57/4xXLqZdeV4YwvR+fr8SdboaIdnLN6QeCd6UwW8TojNgeU8RecsbDJYIZ'
        b'I3CrlLmUWHAjvuzhDMIsEavny/qUMTcO3BZPOrQOLw58A1+mfhxh80Rm0oDPsIu38MPVuCU2Ro3bCgU/jsCFPD49cAmzQEzBN4fGqpkZ7iG5GkeRaQevGkRu29idyPtK'
        b'cYs2J8ZMWqWIX8ql4iOxNoplq22z8YWc3DigfymkXcvh63HkGrtrckEWuQicgHpt4IfP0fVI1/BjyH2ylzllTMQHyUPm4kGOvhAX4+3iUUK2MgcXfBEfXggVx1Q+9TRQ'
        b'eBI4IUW4//Isvh9tpedKRRkVs/pE2PBF0irCV8lVcl64/7IN3yEXtXHR/YIye8wseAPsqv8Ls5Th/yWziy8DTCg1NfRo4MwIM4dKBevZDy93mGB6DDH08mLBDMNSPHUp'
        b'GQKlvTgpcyyhTibCLWeRkA5lbidBPLv1rK+HgaNnVIfZRi6YToz0o4R+lNIPevuixUQ/XnCZU3xZbAK+ye3HQUKfJa6Oja6eXnCNE+Iaosd2Y4aPRR62m3Mx7rYbf0sr'
        b'lrhJWvSBuOft6JL6gHrEnpZy9UHM4hJcL3bdji5pkNahtdLaoDUSl4VFyiwsknVSf9cS00GGoqfFuVBBnMtIgYMSfZEyV/PLNUPQHJY7dJ4YyeQ/FtPLiv+amo4Y/U6Z'
        b'ha9YcbNshQjh42tEoVwafjiCyS64C5hLQwFunkOa5+bOIrdmkltzQ1I0GoQGkw14Z18R3kg2LRaMus3kANlQQJrnjK2J0JDtySBQyVZw5Bi+QjoZN8jtX+LsilwdxyFJ'
        b'DIcPgEx4nHEeIFq7cBe7Cd1A6iegCUNyBKa+BbhLIzlJTsNcTgH6jEb9yDER6xFfAlnlslatSU4cizdaeSRdx+EjxeQAK10/NM3t1vHZwKboxePLSIfp/PFyzvoRVDk0'
        b'9pVp+el54gR50vlbH2R9dONFdeTkSVN+mHGurOPxRUlIZMOlP7wwYO+gYY/T+IBjJ078Ni3txo3Je47+ddmRP7ykmcJJlsclLtv0nV7VqT9vPvf7fslVM2vfks357rWY'
        b'YyO/073ziH7lmJdt3PZ3Oq/n9P9g9k9nLx6x8Z0VcWnDyHPv/GZ16PRD4k+6ytPqO47Mm3xl6PSfr8pfvPrQ+vFhARV193cs+XeR5V8fffz3/X/+ReWOsPQvi1dfem1E'
        b'Wfu+/LisJH3G5h90/vCTDw8fTLzQp/K993J++ukfRv3hwZ/+Xv3dtcsavxp+9C8vXoj84/H1T0TH3pz5yssNykh2C2s67pSxq/6NMwMQj09wc4Fq3RIIdgc5Rk456Cve'
        b'nCSm9NVM7gm07Iq1Cp/CTQ4a6ySwMbhDcHqDTHLP4UPnTl3XyAT6WoGPsX4G5KwSeBS+F+PuqjhpuuDKeC2U3NPSpyQnq3NJSzw+L0ah+KGoUE9a2fxJy2gg6o30oYoE'
        b'5aaIh3D4RKVKsMQfx814S6ybIV4+uSpOFLAO32dDzxuZTu+YL8BHY4XXWDgumb8fy2zrpEGPb2ndnV7JQ3KIQ33wJfHAtFBWJ2kGvYjS6ft47XnB/RFFviDCFwOBebGt'
        b'OBw/x8llZbgx1pvJ9pUJLPSmmL0pAwZMXST4mkpR2BDRMnwab2IQiagMoyw2iDQ4nVsph01HArgOAq9qYGb8Zm1NooO7zJIw/jo6o3fPXfj4MG4Xj+PwNR15wJrKFVXO'
        b'6zTJ9SrHvap63Maa5pENy6kcR3bkZ4HGtA/kd9zKV87O+mY09391xb7ToUa4UJ+xp5Ie9hRPmQ/zZWQejWLKmnge/gqsSg6UWfgRM4YlPDugKcH/UeYqd/28Jx4m5kP5'
        b'PjxlYu7uNcIEBEYV0MMiugMEK7S1W2K16S22bhHU+7ZcSWKpot8rXMyn0sWBGPOhF71e4hwxSYz5bEA/U/jxAxIm+l90xhIxZyzxkw+9zAhCoJXNGebhMMeaHVYSi9Fm'
        b't1SwsnKFnlr73Ywu38hSrlhuXGWFfqosRit1dxSsOQ7zlNVloneYdnxZuJ+23psFmxidTtEqm9GH9cmDl0rdN87NdZ7dt01AGc7DjWQP3p6PW/A20GF24evz8XV8DV+Y'
        b'hRskqB/eIFqdR04LnKyO3M4lbQBQcq5GjdT4ymhmLxiDN45ifJYcwE24cb6K7NGq1SLUC28T4Y5a0slY9FdpIiSegynjljcPMiKmTIYmGllL2ko6nOwuwg/IKXIiEcWM'
        b'lQARr0tbN5Qpk/gsuVFC1TSmo7XhHVRPSyTHGD8ke4Em7HWyYK6oSuDAZbww6/0TA7VMVOUt5MBiLs0wnfFf0gH97CpgTYBrNHM63DYovsA0Y04Jb90EFb5n0+a+Oix0'
        b'ckL45vf2/6pPjTTrL+rvBLbKekmDK/4aeYT8afzU3qVlldlTYqracr7807ZJ723/wdakId+/L54SdL5f7qHcKblLw2Sqix/bTO8/v6pq4nu3/mQc8OGtvcrrY7RJm/Z8'
        b'FfKj2/tn3Sgf+M9f//t/3uyUr/zDH984Gla/ZsU7mgePbm4dJd7RqpQyVz6Q8reAdC48Iz0R7uHyR7bgG+QyYyNVq0mXcCswtSCQjqJl/AhlJlM+ShThsepcHpZJ34xw'
        b'jNMuJW2Mv9TgzeQIMC+gxQVmbZaKR8FGHljmVVB46JNMUJnqyUHBj/AhPuZDewCF4CGjsdkxC12vO6F8aJKEcqKxZI9S+jXEw48Lot5aSI8bo5jDeyimWSyKFER0+Evp'
        b'H33OKv+3VNKLdyMijsZ5X+ufaIGP3z5FmY748VB0dNrBdYur9LYy/1elj0eOe6npU0f6/gSp67p08TOvS3c8cXxPxPl44thDrCjdsOqr6Tez2Z1sffO4NLqA8YqsEkUM'
        b'/RajAJprFWzblCAZa2i0KzX1xqhrTVUxcWwgB2W0+LYUW+mtfgaXfVpvKS4zVRvVinxqTl9pshpd1I/1wRbAqusVJZVmoPhfQ8oouFzxfy5SJhNujcePJobHZsLBAIzs'
        b'nJkJckd2bg7umJOJL5GGODVIIZlka0AVCP637fQNEvgIjfnQwlnKBmLSkKsm20AwmwPae2P8LJA+VNH0XhctuR2A95Bd5KxAhc6kFQO+X2Cqv8jMwZEAsaZ6jUBnjoOe'
        b'0BlbQk4DGtSgGtJawl7MNHuNLjafR9xspIkiB0x4m+no+HSR9RwUvXKwcWLuuFCsCT+0NH1S59Sde6e+H7Bmw8xJEeO1mb0yuez7w16rzmyf88nR99Mif/XOiI+CRl3b'
        b'+ceftQ3+/G/D+ye33VrU1B0xau+NxWURZz6LUMwbEzHePvrusje23tj0a/FffrzwpdDfnf/wxe/UvPHGjdSdgUsP/nLCpqrlf/lR0YL1a974kWXS5vX3h7yNx92J/GTc'
        b'9djadZWbPp/3C1PChy2/LGqRjrEV1ot+8MOwN1anzm99TxkmuFhcw7eT2SYDuqdycNDv4cv4DG5npbELYf0gZ8b3drwqDWRyfm0sPiVYcpqCyCFyg9xcSc4scVhfAvFZ'
        b'Hp8EprFNkHWBjOM7tAuACqg8eTzuJA8G4fvkDpMtSfvCQvpSuDi8Ce9UZ7FKweQqT7qmkO2sh9JC3KaNA3geJjvzhTcFBE/iyT7yaAmjkAbcSBWFbfH5NIRnHU8ezIkR'
        b'LWCCNN6WNF27OBX4hFJNWtgSwzSi0oVkP5MuNaQO1D0XcV3Gkzvk/ohaA2sbjBvDYgPx9nj6OEGlVvIghB8V4S39lrNRR+Iz5BSTsONBX5NO4IuW9I2JEq55b9SLtRRD'
        b'h9F3kgGSBvbiQeQ/miHM6S7eNIoqJ44Nmcwvx239yCEQalnxVjM57PF2qEWkCWB0LUCQpXfVkF2xbE4wKj7H4xv4WtzqWc+y03wNpXajzmJ6ej0dXuhPoGBpkbEwHTmI'
        b'qk7LSTjk1oa4KCltLdDmDsf7A2zIwxbif5IdvFC35x75aipdPEXC6/p4vE/AY2ClIy56GqJx9K5gYyAljn9KifCHh9+opy6Voq7xhsriwkIW7dMtq7JUVhkttlXfJNKI'
        b'+sIzHxpmjGFCMeM/bAWCYN7rv24peyYcLfQNCh9QMO5C7LIAcRAHYgLivxLzyCmAf9VrFA+6Bv+lVPQt/4pDRXKhv6f7hF77xMs5KXIr7Xn5zFeDZg1IDR0o45h8V4Vv'
        b'TrfSNzWCLnzHGhoqQiGDeXI8ar1dAaXTcSfeEozP2VaHUMITTB+mzKQPUQYlikcE483/5bcbeVmrnN16sqWAPPYES0J2reyzkAayDEPDcP1MxkbmA6E8oSV3pWp8VTMW'
        b'WpPb3ArcmcEWuwCftjmsO0vJYddr5WzT2Esr8SF830oas+LwSeBLIGkliUGVbeSzx4eZfiH/icRKcTpb9fknuiWvpL14tfV4W8KWFVxxwAf8mS3y4P7pGXEf9TrT66Mt'
        b'OboUbVDwgvbjL5+pS9hyvO747qxd3MioV1/cz6EXMiKWHC1UCko3h+/gnbGjyWmPwMWHuF6woHSQY8mkcSm56UaFgAR1pbPiSHwCb4rFR/FBZhZ3msQXkwuseNJCfIVK'
        b'5lJylyrmDqUcWPRWgb6dIxvxBm1WbjCpd5Qv5Y14A7n5rMgVOahaIOEYC6nXAiNQlAa7CNRIatClBEkMn5bVrnMn7hbTBt1SRyCZ14uV6MVwljWuc0NbDuOdvW9w/Lzn'
        b'Ljgy7FyOH+H22OjsyfiCKhNkjeZ44XmrguyR9FqGr3mhUm/HX+tf3C/aiKWXTQCe8gbR5sBFIqOYvXcO0TfONfOLJJCWsXQgS0shHcTSwSwdAGk5S4ewtAzSoSwdxtKB'
        b'kA5n6QiWDoLRAmC0SEMUfWedIQ7OCGfobegDY8sdZX0N/ejFGgYVKxtgGAhloQY1lEpZ5IzYMMgwGPLodRhcvRhaDDUo6CUY7UHtfLuoRNQubpfQH0P/Eh7y6F+R66+Q'
        b'K3yKhRpun+KnvxuGHQqDvoJ6+nm6jWG4d95/9mkYcSjKMPIQvyjCGGmMMIzqj45FHUd1HEuNdqZYjV7MB1GIKZLBngQ4rv7ozbwTA9g+SQxKQwzk9TH0Z+F1mu7AQuBW'
        b'+ukgJ7Nwby/7u6eWIfg5StlbBaUuq7vk21vd6T/v4LQgwep+NlW8zEa9LCfpzKNKA4VH3heym9TRvIZHM3XqQMNYIdMgX7u4hvtMgjT6xfNnTUGCtL2N3FjmEd7u8SQK'
        b'SEdjACooJZ19ZOHkPj7OelKsGDHnS64Bvul4+bps9DvnLFlYn+nIu1eRla4g/a2Dg5uuhWzQyMW/2TFFJ7597NUh8knFGTs/n6/WcBG73hpQ/9EfC2sf7HxFGtxncf5v'
        b'A5uX9WsPev27r017obo+8oWHC07/JFdaGFC85Xv1v/v11PQPfpQRUPqG7W+/mHWtqPv5c4f7L5g+XRkoiFRXB8Ls2KuXVItwnQjJ5vC2qeS+Q95aRm6DvnwlJzeOHJCA'
        b'vDaGj9CQTib+pgbiTV6PHofiVrEM38ZbmY21FxDLxqcj9tjOROONaFR/SZlcJZgDTpGtGiFYPDZaJVSD7es7SIIPiCfAVl8TAruvLCmhc12Fr8Rl4WZmvQYCHUEOivBx'
        b'cqdUqNRJbufSWpPyhUq5+CKCOrtFIJgfJTuYATtZTgPE40F+zSJNeeQmB6L9dh5vJu34hI3akVKfT8WNK2FXbEz0Bzbdkg8MYVs+2aGWonFaKT4xC9jVBnxHILbfWMzs'
        b'CQgf4k7EE6VckETG9WOB4Q7zKVcb6To3T71JUTB2dkuYo1K3mPq5dst7HnBVVHYHmiqq7DZ2GVePCOruNy6xUIuQZQP9qENO6XOjxzzjvdjBTz2EUB/z+zZhr5JCOnG/'
        b'8a4ZvONguI/jCvse1HOTqFfUq9qipWTmm0ylTJhKSKH77vmd0lTnlJ4McRveO+Jb/e2CzXtg5W/gGa6BB2c5KztdLL/1uK5wa4o+heUm/yHP2a5h+1B9Q1FiqSz/j9fp'
        b'HE9f43e8XNd4vdh41AH3P1ydtNBWadOb/Q410zVU/zm0otNR1+94/x9FT/PI+62BjFn8e4BI8B/rs728jEsXeNG6LIdP1ugfWX4wcxAyJd5IE1vp9WnHjO/8aD59iW2m'
        b'vt0Q/ZFWLy/5ve736C8H+xfse6k/ezmt7rbk44/nKzmbYCnHt6dQGocfcc8gc3ska54hmzL9j1Ez9sIzJzWbR4XR2gh36vDNQ6sLvIjOFQ/jpXe3j7+Cf/9lpcjrBefO'
        b'bn3Cqs8UcW0br6BzNu+zTprNtiNk/ulidDCNYimX+7Gp7wmj2BoN+Z9OfFN42XCrQbRrwYv78D58s7VD9OodPXsH46sIvfBQWvfbRiVvoxffTe1HdrvxInzeD6CATZ5k'
        b'Cs4KcpicoUahGJUa9BOyF5/Bm/ikifpnKRlhhczT2FRrLCwyVxYv73lBnhOoS2r7u+28Z22P97hKmIust75B9XE3G8dO+FjgBevzHrD2P6LH0XSCm2KW872uIgC46H+j'
        b'BXPI93MmBvABi/6H+1QUXSCeqStsnDJScK4EKQjknQtihDfPQrWotvcQll3Vaya+wNO38e5Gq9FqslVvp9JRPt6f6yFA0leEFj8XnafiUDLeJg3NwQeYc2ZWPg2e7BcV'
        b'NEmXgwNCEHM31CXkM3fDRTZ91Nv9zihKkJ1ea4evVY9i1yVVkbszXTGVgs+hA108bko6TvYHkQOr+jJKKFwG3kF24tNUIReU8WB8WNDHyc0Fpi+2vclbt0GtVY9HjXot'
        b'PRRr+ol06S2T+857M10zr0j/W+mrcb8fGr7/wJycx5P3NhSMTB11/OCof7ZFXe5c33fqZmKIHDEv6HDg2Qb5rC36pvA/3Bxaun3hP/RFs+NHVZ97O3fQT5rW3znz5HXl'
        b'V/tuffrl8t253E9y1nTfvh7/zvUFjce//CjvCU5KVu9renfrl/8Q/aZ1eJNthDKA2UkHkIa+VPHGnes9rJ34olhwG+gCyNx2yqt4I+8Rt9fLRg3u63AraXum1DdovZTa'
        b'zvEN5qdHrpLbC4JjHIKtUwzGoOGjofiGmFzBDfgc63kQ3lUouLU1MWDji6A249vPOzuXIg0+Lx2Et5ArTPBeEUf2OlwGOFxP7gpOA8ZVDiPCDLzX+ehfMptcE4wMtaRN'
        b'6Xp/tl8jp7RwpcXkeBeqhwBaSN3HeG4ICKADHG5lcq423O38sYaeL2zWW0qtfsRL3tLuedzb4GOJ13E/4/GKTK/h8orFbifS48mv4929LCTO9e5eMXsYJYGDLnYddAk7'
        b'6OJ1kme9wFniddCleYKH9X7LSNwmAkXiIXXhGgpainBnmfCctpGcjo2dpZqnom4fuNMYEMEPIfvxbtNnC96VWOkdk2VfPPpEN+a5JS+24l9+553vXG2923a37u6CuC3K'
        b'fcO23K3rqBvXnNU0bN/GJBG6OES2tOML4M8sMPgWaZsKOgo1rmBAEuYIwgHSJQ4sE+MGsk3lhMWzzdrSQhYpwSAe7g5xcyjzwPDYdFZVMGJL3Vzu2KuXmbnIk6h3iIXc'
        b'p2oyeO+GD5MXvPdH+oM3G9o/uKljeL0EAC5ldgYK9IBvAXSf7NzbNiDJE2BL52xT40sFqgg9wHYPh0TkPpeLD082XY7bzbG7Ok/uVX2i0+pf/ij6/SxB2NJ9ojOVxOz5'
        b'RPdYt7zkU8MnOn67JiXp9b7266c19qvVV08nbEsQJ1Xdhr4rQ3onzewRS7+RS4rH67apac8Nsr3cIWuRCV431L2zt9sW97QRutrjH3/2uuC4Dz4qveDY1s8djr4HeUyf'
        b'C/iHaJpwgCWOIyz5FtD0KUh7H2EnNClJHT8DtxWo5pHdSZkiJBk8NoDDm/ApfMOUcOuHvJVGSTxZLf5ElyXA8wkCiGbqP9ap9b/XfQpQ/VQXri8rySmOLAYJzcyhc4Nl'
        b'fdLGwlGlI04lDWGJY7Q5MYIbNDmIu775C3e7QwsdV4+6gdNDmq6l4Kzt57bHHg2cBgjPQ9gtLdEX2yotfsiz2HLQ38Gl8fwrvQDe2Msd4H4nowwTXHh7PHqpM293SI92'
        b'vdy4qjukutJeXGa0sCYJnsnE7uBiep2Lkb41NcE9kdgtM5iswj0s1DGYvjPeRu/pNdptoFPSO2XpueyWG2uKy/T0xlPIUsrYkzALtSxa0ukHe1BGBbCeG4HpM7FFrEfq'
        b'xJTQHeS8b8VkcItQX8xq2Ew2s7FbRt+4QSt3B9Nvzshvls0udGI9JVpO0DYBNAixqLKGhad3S6rKKiuM3aISfU23xFiuN5m7xSZo1y0qMhUr+e6AjClT8ufmzekWT8mf'
        b'Pc1ynQ5No3u8JF4KWSr7WJ+jJ0nkuumJMkVZiex/o+yIHF17nqdiQfbdpVnL/Z1H0b9I06c/0pYiwffoCrlmtFrJTnI7DPCIJ2e4mMX4Ojt75GSJ0WqrJrfXLAsjt4I5'
        b'FEAO8KHRvewUKGW4FZ+MpaLbpejMXHVW7izSkIcvxZGW+OxZmXHZ8SDCgojliCPKxScRaVssn1JEbjKPaHIfb59P2mYh3ArKUi3KxR14J+Pc2WQ73pqUrBGTfRMRNwbh'
        b'NuMUITbqzjp8IInPxecRSkJJwK5PCKx+94g5UJ/PAoGLi0a4PZjcZY+oyBbcNIE5i64lG6khk0PBi3hyGbdMYh3a+pBWaChdgjciTgn9RM5i0sHscmDizAmWbKkdS195'
        b'fo0jbWT7araNwaNi0ByE0t4dqiva0bcGsa7SQ/Bm6IrDO4sQF4PwnrLFdia/XicNmVq1Sk0j7XJVZHsONxnkzL74lHhSEd7EOpxmUaBJoG68vV43obxyLWKLGhNKGqBD'
        b'USxuQ1wcwvv64M2OuL+qF2LpxSNZTI4cbEVhuFlURLrSWGd2bR8EG5qmHaFbEpSnEdzPNfgh2Qa9BQyjvalAOCKbUwQQ3yEbp2gzyWayg70+SBzH4XtDSbNw+8u459Aa'
        b'hCa9mK6LTEpy9LU+KC4pGV9F5AC5iTg1wgfIAymbWToAbjd1vMpVcfgSvo4CE3i8j+wlJ1hvv1mmRSBbVv29ly5mfOgQYZn4gGIG7U6cDVDl4hE+uHgwg8HwJLxfuIYD'
        b'XxjI3Aa28iPwWXyH9dWJqGqFyuqn6+RFCcnCzPANsgFfTEpOQSnD2J7txocDGBTwI1CEtPSGlkaygzk3kzP4AArFm0XPTSIXWZcv1aShKoTCY8y6xLfWTBe6JA9y4qFD'
        b'Ht8nu9hi9+Jz44T7X24Olgs95uXk4UekUzCVc2gAbhfj7S+QTUwYIQfwdXIYupDijRK2wH34ehXbrtyhZKejBwZJ/GgECq0SpRmK2HxMMZEIqF2NLEi3JDY4WNguXW/A'
        b'2ESNdDV+xFa4Zz45wo7xgliNgLHRxWN5QNjrHGkvxk3CET+IL5CDSWM1iGzEtxCXCO3wwVS2wFCyIz1WS1XG+uk5HJKa+P5rNMJutixZmpSqQflkC+LS6Ly3kFaGM/bB'
        b'ixkCLhqcBRC/gpB8gig8CR8Wduw0uTsf2vG4az3ixgOAg/FFBtG5onwt2ySybR2QhfNiJA8X9SY7lrLljouR0Yc6uiKdLicjYqmwXHJlCDmUlJqM8Pko1tl+RaSAtqdX'
        b'qGEONMQQb1ylBfQo5gfijUo2hZi+PLQRw0xg5ukwA1xHOgVonMfH12q1+CKi4YiIr+Qm4QtLhHk34Csx0IzH9bgLcRMAE8sUwlj1o0m7llKzJgk+SJpgl6L4wOlRbNq9'
        b'AmvR3xCaub6fbt7msHRBAg0hD3E7vqFJlkyajLjJCB8l+4iDpN5H1Cv9zuKcbPoIREQectDnCV646HnJDNQEezAoTpf9m0iTYw9uLa+mfYnKgxA3BeFji8k5NuNwUqfU'
        b'AkGR4uNkD+KXcfHkpJb1s35Cf6RBKHpQmW6JUpkmoHL/GqTFV8m2LOqEIxZz+CiPjzE7R/+cMtImwbdAM1MjNbmAz9ipuYt0kfMGFq8wOxO0XdU8wSONNORmDIgD4oPQ'
        b'jMiAgXFiRmoXgnZ9yxVfypXGIxnZx+PdpG5Gz03RRetZZG3mRbkuLi4pFDGnNLynHHTzNqlchYBwxaXOEMJituGb5Lb2qSdQwF/E0OdGNAqfl9inkGa23Ra8YQJpnDVW'
        b'k8GR7UDCIrmlwaRd2O4GfBpaziHN4ilrEUf2U+X/Jj7K4o8Lp5Q8HSHNka3PoVH5ElP4UEbW9cn4PDkYjJtn0og7+D92FfMzHphPrsfCbuSSHZmqbEHHS4BjH4xGz5Ek'
        b'4ktj2HpfnTsAJQNy/LqXbk1dVYAAz/7kLlDjgwHp+DQlTPC/X5kQ67yTXM3x6pRfOwuNnitJwiemshVNAeG3QTtLJSVnyUVYEaDyA3IatzEYh+F7YQW91gErbgZWvpob'
        b'hOtwo7ARx8md0dq5sA/4Pt4H7U4j2Ic7KuYZYC8gnU+FoHOTV1KdWQwwILsFPNyXD5QkBHfF0KAlGre0NUi4XewiKqAHW52VR5rxMdIUm6VKFKOB+IDYPHgim9f8QWQH'
        b'OSgimzBol/gB/MdX+rGQJl6zwtU2ALfQpjw0PSguJ9vKBWfGI9PJJdKIyGFSB1QRmeTzGcaNssylPpPO+eIufAeFRYlewHVWwahXh4YLBoDjzACgymNrJdfHSGKFe7sA'
        b'MZ4PcjhBDMK3xEDMmlIErnQCb44iByVGvAUS9+H/LBnrNKQUbyaN/HAKu+Vo+Vp8h5HyheTKc9oB+IpKlYUvRmfTExY1SUTaC8cJBLg1CG8nB+X4MjlPOQf8J2dB2mEy'
        b'ygN8Yb4r0vOyGJ8lR1gcytBANpVQCW8NCeGHk2sAtB0ItmJnDkOugN5BiFawRenk/XXzBDGkFGj9XtIoIsdgx1AlqiyOFrjVBlJHjoColkmD0Zu0+So6ScVkpBgohhNx'
        b'krQy4+TPZ47ifixCujVhkyp+VSPR6xzB700D5+AL4rQhVFCrFQWZtDfe4K3/BLl2ya3Pl77xSkVURrj03Y+PfHdF5NtRUU31h6/+KX3jyH68/jeB/ywJHbXR3GvhnpYP'
        b'gvvMPtr63aicR3wYGfHZoH8V/LFp+qC4+w87Livn7w1Mf+n8hX/O/fmDhgfDQtoDZ5ebTuX88s+R2zuypuw+t275uzd+lDFg5A/OS4+snx947Y8fX/v4qxT9gPcL3m/V'
        b'zvvhFeXJ3Bc/7Lc/70zEj1566cbP2zo3peau+FnM5XHbpn6ksI9ZPPWjYYsPJ0+9nXEgr2jnH1oH51Vv/3TTp9XXZxgqj//luZ2Sl9eNCZgaOjklfcJIS+eP34vYeXLL'
        b'+O9P3TElL22c0nJ+5u9uvrx/06He4wLG/em3m16e9vKoMY3D9w6bf7H0d72bf/a9oR/ot2sT9r8RffBfhVO+tzeL7Ov8csr32/eseuv8zi+z9l/58W9NpQNSx//08+/d'
        b'y69buOyVivDZGe/YxkbYA/+MS965/OL51tMTTnZ/HnHlw/5z65rfu/DWxLAbq0Pv7pb+/fKoA1eyblV2Tfj5g5CHR8rMk//n6LxLm1r+sdX28MDhcsWNLxoXrykwlxed'
        b'i/qzalzqVetAa+eItm1/v/zyg22f/Tsr/vGg519OaRuavWXGlqCWUV9lrftFxPO9V+3RNh9tvPj2K7en/2vy+3v/8dG0f338qPzcn5fvTP3H/juRjz74Yt5fA/b+ddan'
        b'UXm3fvLJ7+Ijru+eXPic/eNty0bm/mH8T8fvfvSlKCbi35V/qVRG2WjYhJJsInt9+gpUzWOuAtbBzO+/DHfVxuaBYHh6KuLxAS7XTpqZT+rq2gjSaMCUtsdJkXgqB8Sh'
        b'2SIYf3cA/8GNYVVyCxCr5mWkOaw6JFCKeuGjoko5Yq64EfgWPhm8ohh3xGU6HRoiyD0RvjQLH2Um5oHAb++Sxkx8yMMzjNwmVwVn3oukFbhXY7zgoAp09QAwr5M8biQb'
        b'ytiF+3h7bA0zAzNTXvV8JMvlDTU5bF2pIFMcg/PEJQFt46u5DHxccMXNJdfxWSEImxzH150eZzbSxdrNl+Ir+ELWMCHcmsYCFoQLIXibzRmC7wbZFxMn+G5UBTDvB7x/'
        b'brGH60ZOhGAJL8LbmQ+FcekCmPU9I3UL8fKzOI7vs0oBwDDu4sZU3OKs5u5psdfALvivqiaPqGMHfRBBtRa8g1rB9+EuwZoZO06Cb+OGPGbxrAYd8oKbxfPibKfRk1k8'
        b'B+JNbPbPg3TQ5RaXAaA9KMQIakYyQGQDf+hweXdwIAJcd7h34FOlvm7E/9Y+pt0ivUEw1NQg1GOoWY/UkVwfTsxFMm88GmwdDr+OHz6S8/qheR/LBodzI2lgNtcP2tBf'
        b'OSfjB3AKLpS1oS7HtG44qx/O9YIU/6msT21IjxUG5uNumrdQK9u3jXjjhVY9Jvub8HGeWoIo53dZgjagXw7w8ET2mIX/R+bM3ie8GgrVS1z2Po7ZJ5794NzLPkEHUaCn'
        b'7RNjBPvExUgqHk5ShCGdOU07GQlGQMp2M3OicJsEvYAvoSFoCG4FxZ+Jjq14YyhotGj+aNQf9a9aLFxlWr+WXEsSo2oQ2BJRImkRsd5XlwWCglETGqrTxWmVyYg9oruT'
        b'QDM3jAjU6eQ/7F0iiKlWRO0kvzQEavSra8t5YQoDx5CTSclcgZjaG1BxBL4u2CSulihAf723QkqjBpBxBDnH+tg7IwDJkS5IptDJL66dJHQcFRcBq/9skKRKZ+6UmoQp'
        b'jC8Kh8x3MwMgM2fMBKHm4Rg56oc0lrCZOnPp8wOFmk3mEMi8miOGzL/MWC3U7KoOZmIAH67LmWMcKdT8M09lg+ih8nBdnGSUUsiMyKdT2hcRrNCZP5FNF64bJefHJBRQ'
        b'eXEuiNZIUk1uLeTwPaCBR5n0MUCWkBSF72o0YsSNpLfWnCDX2bApcPKnIk2eFOmGZ5ZMFUTbdHIQqOEFMRBufISKClrcyiR0EPC3kzPkYBAqotLfbfiP701iRQtIOwER'
        b'W0rFWBCG78D/eSC8RzDSWq8ibRyIbClIhVTDqtjIZdT7FkXLZJN08n/3yURMipqAH+WRNrKb/oCaTbaSG1RcvwWkm4GpJg5IKu3qNIw/GA2eQg6xh6ajQcm52/PMlD4w'
        b'JefwbT4bHxjOGk6dP6sgqQ97SsSRnVwkPlIuSJf3gLzvig1AZH82DbHJk7LsDHJwJL4AJBG3o1VoVR7pYNnlIJ1eos+S5evok+QgcpY9t2Vg+dBMTRnHDGJYz64h/QUb'
        b'8tV1H8K5ud+fuiDcO2v6uLiYsybD4RmwoKR8Zzq9ymVrafUHXYfq/2rRvBcSMOnNHw9Tt8b+a/bIs9eWTDEOu/tqRPXql7joiLMNadz74U2/yLsa/trr//rNH7uqLa/b'
        b'v/furWzRuVEfjh89YsAPoo8VlSW/G/iTFaSmbNH04L9dPPH+3Kg/3Mr700+yhvz4td2rf7bpqPKnWyvferxj6ucjzz9qeWPF/F9O+uXVoubh8783WfR/mrsSuKaurP+y'
        b'AAECBAS1ipoiKmFTRFGxVlBQkcUFXFArBBIgGhYT4r6ACihW3HDBBUFRwQ0VtW5o5952nJm2Tuu005rundqx7XSbOl1wpnz33PuyQYLYzvf7PiM3ecl79553333nnvPu'
        b'+Z9//dE+/+q3e0Hv9qa28IV/fhhx/uDqmK9+nn0j9uXxi//t/pdP5xffuy8r/XLmF65Pv3pw/5hjf/tozsD31O8Urdz6c/muvv4vTvy07S/fTVlbVTT34Q/jsXCyZI77'
        b'KznPZ78y+3yScnDmK8dyNzfNvp/8ju8Q3Z2N5Rd6+bStT236T2XL+nS/mX7jXl4xzis8KaL0vWevjlv/zdRVV1u8a8acfW9p3Pt3B4Y1tbQJvhi5IfdKoKJ3McTZ+I5Z'
        b'hTYGPCY4cE88KmFT7SZUhk/RZf6UsGAIM7xEHAIhGchXAhgCqRmVDbWGvKATKmJVZIyjC8F+6DiZvlh4JsRmFhEXv/hpXEPNGvdifAbm1mRwPSFzEWDcY3FVrgidjUMN'
        b'DIG0YzJuhvRRgGDfDLbDHnRxLXE8WtfQNWyvKHzcjtX1QhDEX4LZRWbXc9Se6I9OjQVJQuBpw9n4CAGq06CTVMoA3DzAEm+yAJdDuEkmP11PL0IvMFYjQOyDCbB5rIDr'
        b'OVfcd+5glsullbxOW7EVkZKcyKBQonHR6eXkZGk/AVqpig9GBeQQXk8MmmK8k3aFQov3sG6yMVdi0BVisfj7M/vsnEe0NZwTb0FXqdmAm9BOFjq6NxrtsFRjMmfwftxC'
        b'TJrAZNqUXxAm+wydEhoeDo+oiaTk+PWoWUT0xkW8j3E0tfSI6BjOOjoEAlrFz+AXUmmn4RPZYD6RnaoSnTixcI2zANVGoAP0bNMH4X3mJX5Y30fX8S1hYfxaGk6AWoKG'
        b'dAonWI03dAgnIDqpng2CTWNhpPCGKRilUlRC7NJgtIFCYtP8ICVRByPNZKDNSyEmGt6NNrNO3I4al1psK7CrcLMHmFZ16AILGq6fNzYkONyUTAi1rBGiY0n4pCk4oVtr'
        b'YmIIwqMGVp6tgaWTCsRCUwoBX2pe+ZJXT/LqTV6w7UnTCfjSPXz4P/q67+wv/NS5H2THkQrdBL6cuF0igmVSqVBCMV4rPS2mDAhgFa7WhdSW6LVLpPjajr1UbbN21qER'
        b'0i9gn5C37fQthf7X1cBGrw5ILRqUq1sJBQ3UpRG8ELxrlJhCOU2fYHGJBUBSiBYEW9EQDLouTxd16UKfUZoxPXZmbHJGWvr0+FSjSK8uNooB4W90539IjU9LpZYgPT1m'
        b'ZP727BG6taQIFZpQWiKZ9xPjsJw8xZ4ens6+EpmLKWeEM41bcbZ9fSf2gd9M3ws7/m56fSX+2jnYU+D5i7NT7zgGTboVlmqt6J04mU9EmmgeOri00+qziZCFZkqzYZMV'
        b'V3tRtlUv07tKaP4k2uqiCiQmMQAnvHLEKheVxMwt66pyo3AXKc8t60G3Pek2cMt60W0Z3ZZQ7lk3yj0r5blle9BtX7rtRrln3Sj3rJTnlu1Ft3vTbWm1OIcDqVRPHRRW'
        b'OwOgZZGHqs9TXJ0nQD/47b6m7V7kb6+wSqAaxEPCXWi6JPcKrwpZjitlqKW8seQ3V8oCK6ZQGck8GfSG6umtggrmCkgrPIgjEKAaSBlivVX+dHF/MM8Qm5gS37bHBkGd'
        b'ZmIuJT8xelh5ELB8AHWTskAFQ1/TkWDSZiM4DYDcPFsT+VSYpS/UArU04M8hPS+jyoT0wOqiYpahmoLRO2RN1kH4kcLF6MrTjgFXD/+RrgpLWMZQYO1R5Sw1ihYXkO/y'
        b'1SqNIZ98Jykiki8r1Kl0Fo5au+SwtompTAnAXYkL5cYv9rqbE1N1hx42RyH++Ltu08NCJ/9qetjHs8N2YoK1i8H/leywVhfDLAekEO9CCvKzIxkK5EptUZ4yzJ4oY+TZ'
        b'eaTJbJqou2uy2q65au3w0j5BjzyWq5aMQ5bTOG7SbLlWmQV86OSjdZpoRXiHBMyMYc2uFLai074NGm7VFXaE5wUh98JjmHIdseLaT9LgiCm3m6y4diu1MOX+BlZc0/3O'
        b'up1tyTUq/oJFPu6CmZQEn8ia35Lr1LkaPelhopyIDqPDKVRu4C+boQASSv8q8lkv9vRk+jR4jjAswK0oM3TN3HSOBmmsHgiPYolBLEPPOyCgJXajDUFsWYxUhpqXskQ5'
        b'i/y4IG70ZJeYTP+rc1xYZlTgD51pwzzL9ehUJ6Vlsa72cJEUN0RH0WqHjaFPN7ydpmeG/jEhmTHGosOZxF5l1TbnOuC0pfHWVmHQV9Amd1RPnLVWWrExCR5xyGKc5Zna'
        b'j/L68qHVR9BBWEEinkijHbrchJBU6xpL8DZXtJs4V5cYmGM1LEu/WCzNzNSGTsvnDBCzgzaGxfLctodRS0dyW4tb10HUy+7oaBA6QettWU0f28R6yTKlgWnT2dVCtbgm'
        b'jFUcrLOtNsjkt9jUeQ2dcseb0EEXTexhsUD/PKnjmGxZ2KvX21Z7oxhp/AxN+/Dq2KcffiScUp2ZK/U755nmPCJG8eZL818r368/rD2vevNqyx+3nt6nvVL948Mrz6RP'
        b'/Huvd899VD5/4D/cEguyB3z27Moeb6hGVB5f3uPDzyd++4/aj/3WvnhgVblfe9rfT3wxKNyvOqN6y978tYu+nvul6y8bDld8WLH57lTdvwVOJ0av291P4Ua9qiXowCDi'
        b'plxErVbeJHMl0XnMvM2okW7ufqi1U0pUSRY6xcJqX5hA3NghaN80mzHmxA3A+8S4Gd+Yyzy4ynXzeJcUHXWy8kqJSzoF3aSezlrchPfiBlxpQ4FbaKDP+p/tv9LiLUMQ'
        b'dyWqew5fpt7dMlw7ysrzE6ArxIWsDSQuu5yjqZsPSZlfn6mw9uyJW0+8rRImXwVuDKNuKK5Gp61cUeKGDsN7iyGqDdWPQhcQjNcjYMOG4RZ8WU8fVpCtJGrRhjlzyWij'
        b'CzqEtiX910x7M8IRkBhWvts6bgIluhU4W0hvGQEuzVBq3jLxyhLzwwEF7i0oXoTid1BABi4dhuIlKF7muMezxki6U4mHzTkpiM7Ugy9m5dqVcPdscr51lvzJkIBm48kh'
        b'bm0WkYKhIi1tWXHhwlddcOE+MTBSmmFlSTkUaq5JqLb+HSSgdsGvY0V1zTBZTQ7bnW9udwBr97dx8PINizOIreSwzYXmNvuyNq3sqV9HtSvOICaRw/aU5vaCLEaTsiP6'
        b'9Ml5fs29bDJTHEqgMkvQBx5dWFkyT9pmnqlNswPkqM1cmzZJL5vtH6s2FUIGXabPQcyBsinZIitRIOYc7l4aKTuJFHT9CXI6CHm31Y1m+JXmSM0R6E5dRqCbOJScfLrN'
        b'oaQGxsjuUijRnZ+EQcmaMalTlcCgZMYXB4fKg62BzmSbYqfJTtb8L9SuZWIArUb3fT9zQ9Hy1MJ88CCYqw1p13i0sjKLzJA8MZGe2KqO+gb+AQmIGrpEpcmhFDHFvC1u'
        b'e1J8f9NMkqTbcvmkcnbMYPiXYKY0Unbl1kVEWTkz8iATb4pjt8a6X5nJ3ukmlQfFZunU2XkFQNnC+3g0tZxdQS3jQK/X5BbQocCIUTqxc+nlGuuz0hB3J9cB+4rJjYmg'
        b'FzlqjNmbgZYiFKHwcMRE6gt7mFl9sx05YHRUaujxQBIFfTd6TPdJpnJsTwjOWqPW//coooKAEomSOSnkwcH54GKT01kRHPyrSaPkQZQgKozxLD1J1V0QRHXr+Cela5I7'
        b'oJlyRNcU3j0xbOAbXZI2BZlJmyIU8vkRwx2TLllDQPjLaFCz09EUUEEp23pccnJ6OpyZvcyy8K9IuSKf5qVV62CKCqWMbGbP2Eqg4V0L1CWTlO1zEna3DDXdKXbFYoaQ'
        b'Nf8UaT5ymGMqMWvAjOmpkdVtQr4ld2SBXsOEKsyxz8ylWkRGBu0POIAm51Uuh8/dJCWCf7E2lejpAzNNdl6xhjJP6S28aJ3vWYd1hskjgN5ZbSDK1VwBGcEaOd9FREPl'
        b'kzsuflZYmrI4Sw0PIe3zZIXJyXBheUS1hvzF6jz7/R8mj+ywG21NachZaShWk5kDEjTLZxfq9FQoB3WMiJbHGnLy1FkGuPXIAbGG4kKY3xY7OGBktDyhQKVZqiGDWasl'
        b'BzD2Nn2HM3dwdJQ9kZ+8g0bZq0ZjJVb+k4k12l59T9YvY2hHWrr+MT1v98s0NpLhaWEHuZ94JFqffo6OnE0Q9K1ZJmXWSkOuwvHwsz5cPmqQ4wFos2PEGEd7kmFWMLQz'
        b'MSb7cWTHaqIcVRPVVTVkUJjPr4s6Rlvv5vDUxthUZue8HE5oPKCPaDj+E7UHiE1KdKtJlQelsjnW4YRtwQsCPTuZCtkWsXGCEsmmuoD8kWEuhzlodBcM72akoW01wztU'
        b'M7zLaigo0YY9MIhSBsbBfDPS4WFmECM7NH4W1dTwhTyI3OT8ECeX3XE3GHTAoggU9fynULmVbRc/a6Y8aA5uyNORm5TIMsKxKFb4SUtl5q95oUxV6RcbdPrOQnVl7jky'
        b'L6kp2X3Lz2yixdo8+O+eDUORntHyFHiTzx8+7LnuHzacHTacHub4apggpLwJyW+D29zVOKD4UnIIvJEdO+/nWItNUet0BUMn6ZQGUmjDh07SEOvOsdaiuzvWVVCPY/0E'
        b'DThWUF21TLRSfB4xwojud6yaqGzEZlPZF8NR5xErVq0uBssC3omBFdWlfZdVuDxaDuvHxH7KAauVfEH63PFFhYMA3suOUmrlsNHlEdmaYrghSdmlucdQzbAn+0ArDgU7'
        b'PSwyIiqKjDTHMgGcmAgEb12OyBwlOdtJRKl0tRMFJJMrBG/y+VGOd+TVnIkgtYsRbYJKR8snkE/MEp4/fFSX+5tvbXqI7cJel/1tAmDzR7Lr41hZA/CamGgTYlPI5XGs'
        b'EbM02aTChImkaTt3ZCfodOec7jzVk+9yPqdX4TrpLZ9kFnSKynDZbFiEmMyj3kyYtwOxDIpbTEGq8qLJxaFvjpjKsIFCfKPnMHQg0QLDw8+jQ3T/8qJeAN2VTQ8pWr1o'
        b'3nAWdzwE7cC38C5lPyeKzkNHYxls6IWJ6CiDx42BhQYTtPlZtJ3W9VkfivWeKxcZ5p9In80ZwjmAJDTg5hCyM/AFTsPb8Bl0EW9Bp6cmsyRGHD6Ptszklo9wzZ2HL1NE'
        b'0EtzUvLSxZs8uCJlj3fnjsr8nDMAGB+X4ZZ00xpgmrd1uiKoaApbpLDhRtyKaqQKdESh2b/1tEgPiZ4Xxf2hrGrcIuAl/PDVqacGnPBcevhPVwx/79Hg8VLCeK2ydFjf'
        b'WRN0Su/eowYPkUT9pB18+w8FPwxZx2nKlR+s+vCZY61+0TvO6bL/c+ru7QWvbn4zOPFyyV97PModOW9Rbbjwj+NXlLq/tFDzSeQnazY0fJ0X9yjw5QGvuezfNfz1V8ua'
        b'E0LGDnwrbnKfuoaayIEeDW+FL3ZrPxr/3uCd15TrvtTVxOeOn5N3f/03Y9e6V5VGvXPkuZwH2tRHY5WqCe11LaXZWVsMD8b8s/TDb6uiXv0l4v4EjMrO5h6ZMncQ6vXz'
        b'/Xbp79yDf3R/v33y9gOHFRKW+qcVbZocwmceRltSGBQEN+NGGqIZIByLSvBNE/cegEFycQmflh3VA/nl5mkJ6LR4HdrNOWuFAXNQJV01m4tO97cGhESgPfyy2eqc4jCy'
        b'wzp0KJtFQtlZRcIVqNGykhQeQfE86GwarrBKjuQ5ml+N41MjvYCq6UKWJAvvZhR9A/AxC0sfpeiLQA00vwZujUxLTEoQcMKZgl6oPhhdj+oM45D+l9KHQ6gbXb2CFVqb'
        b'1at13DQJZdkTCzwFgTRJEnyG6EE3fuVKSGMQ+5D3nkBVJDWv0ChVqhSbRB2W59YQp221XOX6RIIrxFaVWNJ4ms9kkd01q30B1mtWNlI6xm/QhEsQfsRViM0Jl7rDU5RH'
        b'hFxCDrZRkyB8Z0a8QUxNbulBNd6wS9Myk1yWyJiaxKfwObxNbxiODs4YOQxvFXNkHAnWoFv4LEN4QKy/Fu/D591FfVdxRJo5+HIkBU7Gp+AzqewYdMVbgK9z+GIMukjb'
        b'Sp+9GjRc5g8jlPNDpmj5dALleagxcgQFYyi1nBrdwDUUgZqB6ydEjqDgDdJwDZeNS3ETrYdbDjEDXJ57aKZUH7yIoSoWFUEwBRd0aWlmknJSEYvU/5OMfhlj1GWGrnZ1'
        b'YnvWjQFQBsc9Nysz6acVT7E9l+ZBgAMXs396ZtKWZflsz5rxdMlf9k6vzKST0QvZnrvmURSnXOGfmVTuls++HOpJRVo+9+nM0H2ekWziIMrjCC5LnT59Osf1XiqI41Ap'
        b'qmX8fQN74xORw4AyEFWiKgFu4HDpPFxOeyTbB11NnU4uLNrdQ4iOk19GjqOXZYA3qkhNxnvRaQv6Q4CuoVJ8leF9qyL8IgH4sQbtptgPCWplgNySyag8lUPr0SGaS34h'
        b'3s+gMBvwMeC1w9fwLQ6QN2EJ7JpcxI1L8C4BqljIAY4Dn8AlDHtyAh2daUFtpHsJcDmkz2oV0eN80LGeqdPlZIisSEAtfs6o3i+GHXdIiM7gLQn4kibUOvH8pESGqqBQ'
        b'82yaTkD+46JMaU5SEOvXZ5LolzH9szOltcOj2ASbldA/Ffp0ProEmGFlGAP2l3IQ+sJxBxIzV382YjK7BhmL0c7U6ahOwXHjUW30Gndcj47xl+dqjzy9RyTpL1w5RYhO'
        b'AbC3Zp7m9288EOrJ5My1pWXl7+BJeP/quvn7ATMaK0YH/rvs4Iad62t7Ntb6SpKFX127sH2BbuP7j+QpMa+5NnoXfiWbEReSPvbwje8/uLGiOmnPTo1y9idvvrL7xufv'
        b'G3Lczg9+e+/Lgz9O1pWlBG45veT3LeXnZwTvzXorftMCj5Fvis7nzLr9u10rbsZnr9mW493WX35n62L5D/WLrvUOa86buPC1tCnzAvvt/HpPXH3i2YZxd38ZbwxXPMqc'
        b'/sahD8aWf+kVeL2tx9F/9TpV9eUnr39ZtW5X+7kvZvn/7a5yQOtd5eun5uw6sT5iZtLyqspN7dJ9pTEbvnh2vaJ8X1juwvdltxe2ntT6HLyy//641FcWfL4z/Ts1UqQ0'
        b'GWYnl34/7qo4Y+CriRn6f16cuvxR69yo9urQUXhr6BWPqzt++rhXr9nFH8suKXzp3IWrZ0VYzV0BlEHTfhDE2dV0siyUyEMSyfBqgBmR/CrB14Vox2KelAofx4cTiOmT'
        b'JAA8UqP4aQE6lDmD/rR0oiExNCoxyIpHFu/0ZrwCrehgpAXnMd7AwKPr0V6WAfvUzKCOWQoAgoGPozPyeCfXWC/KrIs2Di7kw0pCF9DAkjqRjoXd16Bjyy0gjDjUACCM'
        b'jMl0kh2SiM6YMBi4Ee20jpy5gRuYbdG0BO23RorgzQFrhQHpaA8TsArtxyUdURp4N6qlMTFoaxAVMNc9kjc/8EHcRE2Q+AiaL5wc3FSYmOCL661BGp5og2gC2hBHzRA/'
        b'fGsUsW524Uor0i2K0DjCsLBrPASJCbhqmRU+w3ONiJxrKqOlrI8Ps4FmyPqwiBh8ZAIDkRybMNMceINrh0HsTS0+hzawHmjRo2uJRK5qyFZgoW9wE7EeOIj2qDvibYA2'
        b'kkXm3MQ7GLHkCTBRrREvLL5oDW5kIUbousxBTMpjUvlRYhVqmqzsbJoUiXn6XyExSGRCCY1zl/H4U4BHyChAQkje3ay4FWX8H3195txXeF/i7yZwFop56ISMj5cX/uTs'
        b'KvxRSP4kbjx9GDUYOnOS2T+JDuxkYJX4d7RKSrha2+yAHZvR6WEicpjn97dSlOkMHY0U+/xcLikGAIIl4fJESh1ll5tLgTZQei4P/Dzjv92FziwwM20NQvtEWshAV+7O'
        b'5rZW/HxRiAux3ndSpi10FZXSybDfRHQTuLZw7TrBTMgCVJKqefjmzwL9SfLjaw9vj9sKSVhlcblve8rWHvlIXF095b0Sd9n2upI7s9waYqZef9o3pE9gyrmbipSAN1rf'
        b'uPOud+qEBG3D7anzPtvzzeKIRStPnjlaXhu467uaHG9BlkFWP/H25/MSdYe8RwzeXlEVsPRK+FD/0b2n7V/1w+Dh9dHHR1TJ36ssyL2bf/Mvdy4OQh9+8PBy0dsHNv/L'
        b'/9698vFbMlvfWtG2r22I9vzk0siTzVjw85cuY34/Mr/0sMKL6sep4QN5si10aLB4lACdRZdQPQMWnUFlkHIiNAVvmY3OWei2yNeV7OY9F48rQIGdQK1mPi1/J7ydsXFt'
        b'xSWgMgGvtTnUhktrKdrBdiGaTYVbilAzvrjMlrCrGu2nWjRhsXci3j4nFBBQFrKtMBnzoQ4NIjYfUbFo92wT31YwrsOtVHuE4p1oF9Ee8lW2fFuTnWk8YNba2UR21ICP'
        b'mQm3Bk5GR5ne2j0U3wwZGijtwLaFjuFm2m+odHRPopHC15gJt3qhEi8qsRMuC6B8W6H9J1votmp60UaD8YZAYNsaj6rMhFu957syXttSYk7vtaKfvUjMY0p1U4uO01YH'
        b'rhgdMjR3hoVuKxRtQ+v/K2RblB6KqrLgzqpsHRcW0DXfFugEC9+WbhnXNUJruU2zA8Sm3LclHV5/s8OwZWqKqAdbrAZDbQnpW4rCpyNSawXHWcO1uhFseJWjubOL1fl6'
        b'hrfqwKPl/Zsc3G5ck1ZSPA2aOYujxFnOMkp05WxNZNXeU/FribOkMJ20i0ld8mU+YyUC6j04jYyjPFh4e0/6YMGJ8+gjJBP2VnxJIUjReFUNEOv7ErN3bd2S+KqrDLD8'
        b'9tJPBlZ89dMm/UfPuPXziol9MPPfF7YHHOPmbBqhbTi/YlHOVr+Lr90Z1R4x/uO/N71y/cWgxpbvl1xc96BStbT86i8HPp7317e+fbVu8ednD6g2ahK+HRDW4/17K8Zf'
        b'ctv585mFDy7MVmUsyxs54WjommOJy/17tJUM8f9u/V5//Z9C7lz5aNzbyRslLQc+XDUt8FHc8jsL/6asevm12+hByB8/q58xN6Cnz7odS1aOvCBuOlec+WZ+2c6HQbUX'
        b'hmq+rw976pFuof7lvh+cv/1oMHarWR559KW/bL0W/On7p+sWZt/e8WnPoMLYb6bW7jnYfkAffs9v2caRwUvmTPrxzuuL+x46H/nUpbLG/BOjf3o98J3MkNqvXm+M/bPv'
        b'jf8IJz2XE3E7XCGiiUDw5XQh3kJMEsFoDh+YQey1kzlU7TkNx9s7EbWIyVTUIsHVg5nN8gLekAgPa1AjOmGTzZp/XNMTNXR+4tL3f2dAPnFB1I7IdEPaLSikVJKRoS1U'
        b'qjIyqNqBx5hcH6FQKBgh6N8uJArGWeAjlPSR+/YJ9h3vO0QoiAZF9IxE5Ok+eB23VCjQvW2+E0VGYUaG1SObPv8P+kCge8d8I4OkoIlYGtkHMdYMXnS+OZbTE21B2yB5'
        b'3bQktBltc5nZj/N8StTPp4fGcDdHpN9G9qrzz+i3Gag8fZ3af/xaFjNFWxmTNcZnzrkJ2cuqEyoe/vSCZNSgK/ufSv4krmZSn7xP9rb98w+iadFN9/xS2zIG3rw7dV9T'
        b'S8jCxmd3TdyclSib8+5nx0Pjds++cvmVVy74YLFwYuxAVBfr7l4xMuqdrIpxnsTKOLLhtmuueEHRyx4/3kx8tmyZ7D9veFX+eYAkNeheEDB2MkD9lCUwB8eppsGTZ2Dt'
        b'dUcXhLhxDrpAh/tEdJDMw9PC8HlyctNgmvaeTk71hohMi5XeLMJ+MzqF9rIeAOMc3EGXOHya8/QR9V+Fq/n8OQNRTWJCcnCyC5n8KmLFQgk+GkGfR0YkEV9oy1BnToAO'
        b'z0vl8NHoQewWLEE7RoVMdeIE40ISObyP3E38BN+cjusSE1CLIhlI75MBOe2uEOLt6JYrO6v63rhJn7AiwvK7W4IQ0uzhUxTCrcDXUHki1ZTUL+o3g/PElaKU5/A2lv0I'
        b'X4Lca3QxYAE+SdcDjk+lE306sRqrwe5MQMdDp/BAVmkPIb6IdxbTLtOgpiJiHFUOxaWhRfwObqhFSEyCCryPgvRHixPJHhekaNOyJQbcsmQ1apYuMQi4XgDSfz4N76EV'
        b'LcMn0f5EvAXtngPp25IhuZ872i/ER/BFtJ4mHEDV+Crr+6GJRMVUzYyGJ76w7cL1DRSjDcQmvGqTqrjf//3d1fFmc32MwrGjfyyoCMou6iFhaX5omn1w06SiZztaQYHM'
        b'fqAqZ4BRpFUXGMUQjmt0KjYUadVGsVajLzaKwTMyiguLyM8ifbHO6ERJ1I3irMJCrVGkKSg2OuUQzUfedLB6D/QcRYZioyg7T2cUFepURuccjbZYTTbylUVG0UpNkdFJ'
        b'qc/WaIyiPPVysgup3k2jNwFBjc5FhiytJtvowjCyeqO7Pk+TU5yh1ukKdUaPIqVOr87Q6AshwNDoYSjIzlNqCtSqDPXybKNrRoZeTaTPyDA6s4A8q4zyQna1H8Lnb6H4'
        b'EoqPofgIis+geB+KB1DA0o/uH1Dch+ITKL6G4h4U70HxORRfQfEBFEC3pvsnFN9A8SkU30HxIRTvQmGE4nso/gXFFzaXz82sU3+Ks9Kp9Lc2SQ5E3WbnhRtlGRn8Z37G'
        b'aevDb8uLlNmLlblqHmmsVKlVKQoJtRWBhFWp1fIkrNSaNLqRHtcV64HC2uisLcxWavVG6UwIAMxXx0Nv63409VuHEHqj5Jn8QpVBqwY0OnO1xS5Eg3UcYqN8KTL+fwCT'
        b'fWR6'
    ))))
