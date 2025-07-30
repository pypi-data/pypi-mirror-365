
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
        b'eJzsvQdcVFf6MHzvncLQERW7jp2BmaEjSmJBVGBoCpagBgZmgNGhOAWVGEVBQboKNjT2ghXFHtTknOyuu/9kk91kdxOS3WySLTF9k23//DfJ95xz7wwzzgwx++77fe/3'
        b'+70il3t6e87TzvOc+wHzyD8R/M6FX/MT8NAxeUwJk8fqWB1Xx+RxetFRsU50jDVN0Yn1klqmijGrV3J6qU5Sy25j9V56rpZlGZ00h/EuUXh9/axP8rzcBcvkZRU6q1Ev'
        b'ryiWW0r18uyNltKKcvlCQ7lFX1Qqr9QWrdWW6NU+PrmlBrMtr05fbCjXm+XF1vIii6Gi3CzXluvkRUat2aw3+1gq5EUmvdail/MN6LQWrVy/oahUW16ilxcbjHqz2qdo'
        b'rMOwJsDvOPj1JUOrhEc9U8/Wc/WienG9pF5a71Uvq/eu96n3rfer968PqA+sD6ofUh9cP7R+WP3w+pD6EfUj60fVj64fUz+2eBydDtmz4xqYWubZ8dXBm8bVMsuZTeNr'
        b'GZbZPG7z+ByH90iYRJiOOoUos8hxnjn4HQ2/Q0mHxHSucxiFb6ZRBu+x+RxD4r5ILVPeKlvLWKdCALUsQvtxE96Zlb4YN+CWLAVuSV2arZImzGamLxDj+3gbPqhgrWSY'
        b'uBHvm2JORWfQiQzcipszcDPL+KRyqAe3TFZw1uFkOtB+1KlJVaZKMlYxYjGLjqDLS63jSUt1uAa1atDeoZCqwjuhvIQJwI2iTHwWNUBx0sSYp/AJ1IQbhzylrIReNadK'
        b'GB/Uy6FruBcds06GHE9A83chy1U/1LAeX9Sts+LedX7rrCwzAreJUDO+sQ66O4U0eGIjbkZNqC1Cowoj/cVtJOTFjJmPbk0Ro9ocVF/EPgKlY2yzZyTLyS8m88OWs3iM'
        b'sJRsA0DzsxwsJUuXkqPLx27mchzePS0l6UyIy1JO4JfyxjNSxq8yUMTIC9L/O3ozQyNr5sD6zj0LbwXGwMjpfOTnsd5M0Ni1IqagID1gyVg+8otAMSMbqYM9WaC8/ZSa'
        b'6WaMPhD9I7+R4r8GM3O/EMWGfsndiPp08iuM0RsSRi3az/Z4ZU+SzS2Ifid6ka6aj05P/iqwI/CKxDf79+y3K4JnH2H6GauKAEq3UQKr1xSxODQUN0akqExBuBF154am'
        b'ZeA2pTpVlZbBMuWB3k+iO3i/yxL42kadzi+B825iyAIU+9qnmHvsKS5xt1ukLlPsl2kivaDQnIoPbspZolrGMZyIwZfG48N460xrMKRsxI1P5XC4DtUzzGRmMrqjpdGo'
        b'E59ckrOEQzX5DFPKLNicx0cfwBfx83iPaHEBw0QwEXM46xAS3TjvCbyHXY1aGEbFqExJVrLiq6ehvpyMxbhFwnDPsP748Fh8B9dYp5MCHYVoN9kX4RoA553pi0NxWyrq'
        b'VqaQHcuocbcEbcO3QmmbuElajnqlaBu6AruGecIgN/Re8WPNXZDWaB66+pWogG1zg7a/d2Dr9tXhYQHvjVJeNJZdjxpaLavSfDDtDxt9f72nMnZERvqv1zR+/s2oN3q2'
        b'Hqk6+en4h3ee1h3f+WT4bw1vhuPqWdnvHv3Sb4QuoXvD0yt8VSeuddxO3Vz71dgvL4mtu42H3vo271zLssVX/advefFFY9P9p7M3fR33bMjFD7J+kqSqWvmLJb/3+kfL'
        b'nVN1LZum/eYu+1Fbwl/2/lQhsRBEgK5W4zsa3BKOWzJUacrUaHRYwgTjWyJc/0wxzYGP407cGp6Gt4pUuCE1PVPC+KIrHD6MWlGXhexj3DZnS7hakRbOIxtfdIkJxDWi'
        b'CtSUaKEYaSvuwXt8yfxZAUM0RoxE9zhmCL4jQhdjZlpGEKKlwM/BfDfiNtwsYsQz2UkJ6Mq6NAXXz4UqTARmFL70z7/xIOD3dcgTxaaKan050BdKudRAdfRVs/v9Tfpy'
        b'nd6Ub9IXVZh0JKtZTmB2towNYmWsD/yEwG8A/JC/wfA3iAtmTVJbzQpRv5Qv3O+Vn2+ylufn9/vm5xcZ9dpya2V+/r/dbwVr8iLvEvIgzc0hnaNkEcs5KcuxUvrk/sVx'
        b'sAFZ5lsSsk4ke2oCqoUFa9GkqlBjBCCD1og0lkH30Z2p6Iokf6XVaXuSf2Lhr7kUHnrCNADDoGPzRPArNjB5Evgr1XF5XrqAeqaY1Yl1kjrvPBl9l+q86mR53vRdpvOG'
        b'dx+ePheLdD46Xwj7QhiwC4T9dP4Q9tOxFE8E9kuX0KnLpFP58FtAUUUih26RsXvZMAfhaewV82hJ1CACtCQGtCSiaElMUZFoszjH4V1AS8Xu0JLIBS2Jecy/aIOEgb+R'
        b'25MKjEGFqxjDvo+aOHMWpHz6UdbHBS8XfliwW9eg/aigueSC/kMI572wCve0R21ffOjY3iEvZWnPao2Sc+y5gp+JdynH+S1Qj2v2/XvUisSaj0aOWjJy26iE19nKB0Gb'
        b'J/1EIbUQ9gafxTvR3XA7BQ2X4hOTmUB0WlSN2vFJfp9tw/sUA1lEjJ8SX/ITefni63QTVaEjCRrclA6chUIaOYWRoUZuw7iJNA31bp5IENoMfFaTii4CQk7gRk3LshAu'
        b'Bu1LUKCmLHwGtQPLIGYk+BCL76BG3GMZBcnLUQfaGa5KIcyGGXczMnyNQ3VP4OcUnAO0itxtOwq8/bL8fEO5wZKfT7eXH5n7vCCW/EhZMVsdyMOA2paL31aSfrFZbyzu'
        b'FxP2sN+rSm8yAydpImtjIkSxm7W1G0Ci/Mkj0L5fSCMr7fvlTJDH/eLSehH3yLaww98sAf6KOQH6OEoURQB9HIU+EYU4brMox+FdgL7SR6GP8QB91nCy0u1oa7ovboEV'
        b'awXyjttyUoDB28mv7eJsSinn4GPSIbOfNQxhI8TmSCjU++6hjwsIKIYWKYPDtenaTwqCikqLjYXixihVwWcFKx6MfPmFA2dGS5mjK2WbJx9TiOnyrgC28owdbABoziwi'
        b'cOMzwTKJwMauwlnAE96ExncCcm5TqyopCueY0ZvFaDvuzaGV5ODrqB64vtaCLEcQuphlGUaGcxffRns0Wao4BctwVew8H9TOrzLnFmAAf5boLQaLvkyAGYL+mEIf1o+t'
        b'Dravlz0LX5WYwkC/uFxbph8AE1MQ30ywHUgofBCuoMgOH0cCPMOHm/b+30NRHoGEcn/H1ajVGUhcAAQYovohqAafNOQ/beXM0VCs4IOLj4DJkQMCoHxSwDVGWyPfjDwZ'
        b'KY6pPM0ylwJlRZ9/pRDxaKJNmucIJ40cOsxuwOfwOYucLA8+Ng/34p0TNO7g5JiewgmIFFd9ANfYgSQLHQau6/J4gZZ6RiIAE2ZXmCh5BCbMzjAh4ZecLH6/pEprtLpA'
        b'hsgBMobZwYPMd6kdPA4Ogj7cNO0Zg8zmwYMw2myx+D+BRVihCWcAkWRaI+i2m5hERMRcEDiPovsqlXpxStpS3JCVE0p52RTgbNUsY8F3vaWLcZc1DMooUc2iQWAq2kjR'
        b'DrqFLxnSp1RLzJlQJvqtjz8u+Ahgylh854WwkDBtitZIoalS29B5Tn9W+2HBzwuVFNrStOe0QUXMT0Ma2QUHRvRYIpU6nS5FKyv+fboXEz8m8NhbzwNjSpjGzSm4zYFl'
        b'5PlFfARo0UW0ZxUFyE14F9oxAJGZqIdSPLwzxEK4oFnoJt6Fe9dEuMVc6OZMCpFr8SHAbgMQiZ8TA+YKQ7U8vN7x5gTSB8JFFk/60C50TCGQH7FHlpMHW6m1knCaA5TP'
        b'6ANspYyylNX+AvDweRzRGE/U7LDqsjEAow2QPQqyRIwqs4NsZ7BnkHVu1UUsdEZmVC63IzO2gX1sMdAFmYndwqoo01C9N5Y1p0HE2fUfarQpJZ8AKP2ssLR4mPas5MrI'
        b'EZEqHQGkndpz+gt67qeqgkvaVQ9W/NcqnIuzsRFnh/7qxRWiN4YAbQv4Sxsj/XFgZVcV0DbCMY1He9Y7oSx0G/cBhLTi85aRZHmvytD92CBHhARU6+BYfu3btfg0upeI'
        b'm5SpuAXkPunT3GSgcSdoUZMJN8jRXsJTDTBU6PJa9xAxGGYDscFsMQlYjegHGEsQCBp+ACPVAQPohWShpbpF/LJ7hg7gjQYAg4i6VjtgtAyCyx5pTMFlmoiOQOFPODhC'
        b'VkG08cnP55V88O6Xn7/OqjXyKTySlRUBSJVUmDb2ywSOzUy5sn5psUFv1JkpY0apL8WxFGppD234elApjh8QmaIcMiCCr2WcmBV+uACZn8RPEiSzUmb5OGz6A7424Ufm'
        b'xwEW3F+A2vAuz9KPmnlE+uHyxDoRkXYOcXmSDkYnPQrSzjG2lgVJSEZlGO9+6YJywPwbvx6WrC80WCpAoIzQmPQ6/vUhz388JE18HbxMb6q2lpgrtVZzUanWqJfHQBIZ'
        b'1Nd+6XpLtUUvX2gymC3dHJ34hz+GQf/tAEyspqLcUpGYCRMtD52nM+nNZpjmcsvGSvlSkGZN5frSMn25ItEhYC7Rl8DToi3XuS1XrrXgPpNRLc+GZaqAsssqTOWPk89d'
        b'ZWv1hnK9fF55ibZQr0h0SkvUWE3VhfpqvaGotNxaXpK4YKkqnXQK/i7NsahSQfZTJ84rhwnTJ+YCATVGzFur1anli0xaHVSlN5oJWTXSdsvNVRUmqLna1obJkphjMWnx'
        b'EX1idoXZUqwtKqUvRr3BUq0tNSZmQQ7aHMy8Gf5WWx2K2wKF60nviB5ALnQEotTyPKsZGjY6dF4e5TElOlGjLy+vVss1FSaou7ICaiuv1tJ29EJ7evki3Ge0GErkVRXl'
        b'LnGFBnNirt6oL4a0JD3wsGtJvaFClMKWJl+kB9jBJ4stZjJKMqWuueWL0hWJC1QZWoPRMZWPUSSm8nBicUyzxSkSF2o3OCZAUJGYAxsZOql3TLDFKRKTtOVrbVMOc0SC'
        b'zrNGYtYSGFZlWsugAohKxyeJ4mUtmTV++iEyNWleJknT603FgC7gNWd56sJc1fwKWBth8uleMJSXAqyReoRpT9FaKy0q0g7gnUK10Kbw7jTv7uLJ3DsNItplENGug4h2'
        b'N4hofhDRA4OIdhxEtJtBRHsaRLRDZ6M9DCLa8yBiXAYR4zqIGHeDiOEHETMwiBjHQcS4GUSMp0HEOHQ2xsMgYjwPItZlELGug4h1N4hYfhCxA4OIdRxErJtBxHoaRKxD'
        b'Z2M9DCLW8yDiXAYR5zqIOHeDiOMHETcwiDjHQcS5GUScp0HEOXQ2zsMg4pwGMbARYT+ZDPpiLY8fF5ms+EhxhakMELPGSlBdOR0DYGM9yFi2QKUJEDJgv3JzpUlfVFoJ'
        b'+Loc4gEXW0x6C8kB6YV6rakQJgqCyQbCNOhVPLmbZzUTglINjEPicnyy1ATzZjbTBgjW42ms0VBmsMhDBdKrSMyD6Sb5CiGxvITkW4hPGo2GEqBRFrmhXJ6rBbroUCCH'
        b'rgFJyaYKYsfKBsi4Kg96AQgjlBR3ShDKQ9JU1wLRngtEuy0QI08yWS2Q7FqOpsd6rjDWbYVxngvE0QIZWp4u0zkHvgT4Expn0W+w2F8AE9lfYxyzmu3Z+IVI0gM5LnGI'
        b'mJqYZyiH1SDrT9shSdUQRUgvYGmnYLRzENCP1mwBamcyFFsI1BRrS6H/kKlcp4XOlBcC2NpX3GLCJ0sAiFLLdYYqtXwhTz8cQ9FOoRinUKxTKM4pFO8UmuEUSnAKzXRu'
        b'PdI56NybKOfuRDn3J8q5Q1FxbtgUeegSYVbNAqOhGGCM3CUKvJK7JBv75CnNjsrcpGe5b43wXe7inVgxz2MYJN0Td/ZDMkd7btmJT3ucbIAq3WVzIgHxLiQg3pUExLsj'
        b'AfE8CYgfwMbxjiQg3g0JiPdEAuIdUH28BxIQ75mOzXAZxAzXQcxwN4gZ/CBmDAxihuMgZrgZxAxPg5jh0NkZHgYxw/MgElwGkeA6iAR3g0jgB5EwMIgEx0EkuBlEgqdB'
        b'JDh0NsHDIBI8D2KmyyBmug5iprtBzOQHMXNgEDMdBzHTzSBmehrETIfOzvQwiJmeBwEI0kVWiHQjLES6lRYiBXEh0oFNiXQSGCLdSQyRHkWGSEfZINKT0BDpNB6hiwtN'
        b'+jKdeSNgmTLA2+YKYxVwEok5C7LnqSi1sphN+mIgguWE5rmNjnYfHeM+OtZ9dJz76Hj30TPcRye4j57pYTiRBKGvLcd9lcUWvVmelZ2VIzBwhJibK/UgD/PM5AAxd4i1'
        b'kW+HqEX6QtxHKP0jbEMJHy9wDbZQtFMoJjFbUK44FHZRu0S5RkW7RoGYYyRCsdZC+FJ5jhWq05bpgYxqLVYzYWv50cjLtOVWIC/yEj0PpkAO3akBFA5FDIS4G3S02Pdm'
        b'dlO/G6Lkvm7XjFTFNDA7cmC+5QLLS6eymKQLk8y/Rzu8E5lwQFP1NZuY2S0zEXWpiajkTUT1xh+pEHWjiRiQ9EvMlUaDxTTersYLclbokfPvZ50UeiKO5b6RSjiO+5aL'
        b'4V6xUnXsMXw82kwsVXYqUbeYkcVzkVs24/a5/2F1ns+8oqIKa7kFxIf+gCRYc17s0FbqjQ+H88o8oiL/enQyQEEZsBZEZSrnBR+AYQNgHshC9LL9YsICmabB69/6IGJp'
        b'Gc/RVJSW6+U5FUZjRAqgpHKVppooWAaCA0gucbkmT84XI4o0gj7NBrOVjyBpjmF+0y0iej+ewecbSlqqyikqNeI+WHwjMCWOwcQkvVFfoiMD4V8FrcvAe7QgICXaZoIy'
        b'/IQj1At72ya1yXmuSJD9BrRUgtRHeXUi70Fm2F0WKhcINdDmjAbIQN8M5cUVcpV8nsli64oQk1pOSj4SSbJFu8sW7ZItxl22GJdsse6yxbpki3OXLc4lW7y7bPEu2Wa4'
        b'yzbDJVuCu2zAZGTl5EZBhIZfGMLs6mlktEskBOQZekCYNlWs3KqWD6hiIZKHZZtuVC0nDLtN7OZ1rgPLKE8PT09caC1fS+189aYSwFDVBKuQ+KSl8tiZPJ0ttmUhOmF3'
        b'8QLc8EluKkzMo/IAGbipTEsS7SDiLsUOKp6KRQ9WzH0iD0KDFHOfyIPUIMXcJ/IgNkgx94k8yA1SzH0iD4KDFHOfyIPkIMXcJ5JiMwcr5j6RLnfkoOvtPpUWHBxQPENK'
        b'1KCg4iGVFhwUWDyk0oKDgouHVFpwUIDxkEoLDgoyHlJpwUGBxkMqLTgo2HhIpQUHBRwPqXTHDwo5kJpjwX1Fa4F0rQfia6Gc6Xq9waxPXAgkfgD7ATrUlhu1RLloXqMt'
        b'NUGtJXrIUa4nXNGAtlGgnAThzbMWE72YHcnZaCkkEcw7QJDlofPKq3mOmBzoATLOMFiANOp1wIFoLY8kP4KHXQsPYPJH00xGfMMssAlOKSn0eKfYAlyJXa6ilERF+R23'
        b'QoAwUoGaA+kHSkN46GLKPZcRAm/RG2BaLHZFcSqwuhZDsWGt1hH751E50K5AdmQzeOnR4SDRkU1aqOdFC72hkCSlw6qRkzEzz9l4ZtQclcPQb2hZa7SWrdWX2jTZlAhS'
        b'Lk4BXFymKcwTD6uER59HHnYM90cr4XLHou3+5vRM3BoBfKwcXyEG0xovZnih2A9tw4ddOFk/Gye7hnXmZDukHb4dvjquY2jHUJ6jbfHSKesl9f71Q4tFOl+dX503cLVi'
        b'vUTnrwuoY3SBuqAWLk8K4SE0HEzDXhAeSsPDaFgG4eE0HELD3hAeQcMjadgHwqNoeDQN+0J4DA2PpWE/0oNiTjdON75OludPezn0kR9v3YQWH52qnhN6K9bJdRNpbwP4'
        b'UXX4dLDFZGRe9GkrNanFW6emxnUS6hcSBGW9dJN1U2jZQF0EpEnqZdRrJJimTdVNq/POC4LYIdCn6bpQ6NMQaGOoTtFic3cIqA8slujCdOF1MqglmEoBpYrIflkysQ+f'
        b'n7Ps6wgfucM/W7ScRyG8U5NTjm6JiRhOmohrzENqJk5ssR5Saw0iCij8HhKTm4fU4pkY3AxkN82wZTclkEcUyULMHR5ScwACDQqvfh+trgqwkinfoOv3LgLcUG4hrwFa'
        b'Xm7JNwJzZyntlxVZYduUF23slxHLVoPWKJhi+BYbgJ/LL4MtW0rb7hctWLqEt/UwzYRHkcwBBH2EX2q1Q4x0nHyvvOul9T71XsU+goGQrEFWyzzrXR28SUYNhLypUZBs'
        b's3eOw3skoxNRYUv8tz0wAU6zR/6l8t01VOvN1OfMPucGatBQpFe7FHGJmAVih7ZMPjBVswRvM0AtRA0kuLMJc6Ytt7jUQP6FJgFGsNjwkUItn0fKA+4oklNrQrm1Ug4Y'
        b'dIZcZygxWMyu/RK6YV8l973gk933wH7Y8T19iPu+PjiDxyx5Ov1LurAoIt2WKnTM7L4vhN4QTA90Qi3PLQXcD7tALzdbC416XQmM57Fq4S1JeCEVapJroQoI8/2XGyuA'
        b'DpnU8lSLvMwKokqh3m0tWmHwhXrLej057JWH6vTFWqvRoqDOhgme10LYFrPk84U3eRHRFobazxgdtIwKT7XYttQsG7Sa7YtJfBsrTPJQ3mJlLe4zVYPg7akiwUxqFpWy'
        b'CEcC1fAwImCYUH2JWh4XFamUz4iK9FiNw56eJV9IAnIaINUVG8ph10Af5Rv1WuhYWLl+PTnwrIpXx6qjwhSuU/UYRsh+vJ/EBlUQI2eYhMhxBekP/HwY6zyIxCdRDb6P'
        b'mzLQhWzckIpbNBF4ZzYxPE1JV+AmZaYKNeK29MUp6GJKZkYGasItqRksg3eho34V6DDeSqses8yPGckwoUGK0nR52jrG+iSpuhXV6tzWnJaMW/HOdCCsaKdD5bTiuo1+'
        b'TCTupNV+mCVjgHhH/t68VvnmxA2MlSBlETrq7ejvlaJWhREHGnRJzMSvkiZPNuM7aC91WKOVyDdLCXEOyp5kUZ6IsjBW4pyTi27gO+76hvejc7gBam5Skh42K5Y5dA7d'
        b'NvmiqwzuNUSsKmXN1VDRT15rHPfy2941kX7b3zt989qdHXtubRPJlnzx90nvi312R1ly2o5VyjbN6VS+M2aiMrWj/eUplveG533zu7E33mzKDPa1nlv2q3krzy63tm3x'
        b'b6zZto8JPP+214bcwLdz/7mzvye+edp7bWMyfv2nm1PGd/35u0uWjwtn7flJ4NEwxe03dir8LERvV4b7QlAT2oMuRDi4mwROFRVPiKHG3lPxoWdRUxZdzRHopLCgLDMa'
        b'14qrjaie+rSgFnwqyBdmVJFhM+IdjurFk9EJGepAd2lFT+BzEcT3xHHpWCZkotgb7/SNQPup8wquxT354arQFBXHSNFBDp+YqEKHh9EKfHEN3gk1qFV4f6p9zYLRJRFu'
        b'QpfRLd7O87B6frhagRuBTZOiC9x8fCsGXcc91E54Ir5aDSDYRtanFF0XlkjKBFeJ0F10DfVaQhlibHwPnSMuszOzbAwc6aywzABPeLtUvQXvshDnWV9vfBk1pQ/PgukJ'
        b'U5N8uAW3hZN8crPEH13DN6mRc6kxiQweqjoPWXaSplXQMNonwtvXymlV5bgHYL6JbxSd96UKUMo1jka3xGTr5PK2kz7/pmvcgMMMNUAlfAizhdkkZaXUA04q+MEFwJN4'
        b'wck4kiJlq4fYyLLddSbT1hFqfEp2hGkueRCUYEoij/mMzUsnmRncvlnGlxqoJMleilbixt/nIek+mVWmhjkw3rOZq2vHnWygWeGXmpiSHm5i1vD2zGymgu33zR/gKUwj'
        b'7ZPo4O30hFFbVqjTzh4CtXxFanRo0Zb2tYDjhbps/EAo0A6dqqLcuFHRzfaLdBVFj9W1Er5rPvl2PsNdz0wp8BgG5U2p8PL1BL4HfBE3HfghkxKY78xdeGx+hL15xaD8'
        b'x7/bEe98G3n32IXR9i6MStKa9XZ+4N9v0s5ee2pynL3JyR65hR/YeCnfuCzf5hjnqW35QNseOYwf2LYAbn75joKEp/YnD6z497AlHnrh5JNAffC4esbug/e/5JFgq97F'
        b'I6G251UJ9QP+ZJiFd5YqLf6E+UXzK83v+73od6hzyShm9gnx29eWKThKQnBT9SYekQtIHF/F122IHCT7Jt6Xrl40wYbJeTT+fL4jJj8pG8wpziufbC5H56ct8DO9OsgB'
        b'ndEMfJkRj9Y00r4sT8FjGmvzdK6Bn3cGcYBzqV/h0+8lbFfe6F9qtpj0eku/rLLCbCG8dL+4yGDZ2O/F59nYL63SUhHVtwg4+ooyXnQVWbQl/ZIK2ASmIl+HBSGYPcC2'
        b'KEvIevvaRU5/+xUFAfwdEcUBAhz4NvgBHPgBHPhSOPCja++72S/H4V0QPOtA8PytxI3gOU+nM4NkQdhjnb6QbEv4XyQYzsn11Mz/MWRPKhlRsUYrL7WW6B2kPZghswGk'
        b'JTnvDkEEN7PeopZnAdi71EPwQxk5rjGUVVaYiJBqK1akLQfJhxQFqcmkL7IYN8oLN5ICLpVoq7QGo5Y0SQUFYnZpVpORGojiDTafUKUgbJE6XeqAqq1mQ3kJ7ZG9GnkY'
        b'Xbywx5iRhcJoS4nGxLXvLvlDLVpTCbShsyEqUl5OVIlmIriY11nJ7BaatEVr9RazYtbj6wN4uJ0ln+dEb+Qr6eHpak/FSMuz5NT1YeX3OkB4rIXfJrPkOfSvfKVgjucx'
        b'v207zZITRSgsFZVTVzqa43ksSzYgSLjwlK/MMlk85+O3KGTlX2gbSnlqTpYqJio+Xr6SKD89lub3Nciu83JVqcnylcKJ4urwlY7uHZ4bH0AHRBrnA3JSkaNRscfigEBg'
        b'Mktha8B2NReZDJUWgbwROCV+43RvzTOaKwB+9Tq3igQAJ5KbECMjvXyILrZansxrE+gWnZRj0ZaVEW+58kke9Qp0MwBgQQcqha2lM9Drj7QwresNQPT0G2DFhQ3nWg/5'
        b'l1lh0fPbhG5+vaW0QgeYpMRaBoAGfdGuhQ0Im0YPs1Okl1cA9XdbDz8ksmmomsTMD9NgduiSWr4QkJoNIbmtxXHbEaUKgDq53KnICAPm73Uy692XLBCudqoooj3nz1qe'
        b'KLVYKs2zIiLWr1/P37+h1ukjdOVG/YaKsgieEY3QVlZGGGDxN6hLLWXGyRG2KiKiIiNjoqOjIpKjEiKjYmMjYxNiYqMi42bEzJxdkP89KgxCEV1dD4Mz6W0ZuAHV4Fpz'
        b'uiJNpc4krn7hqHsirgdRcUqOpBTt1tA7ZLaghsQY+BvFcLgzajS+QPUA9+LEhQeIOmFuQXrgmqcYazxEBuFus8ZG5RfjBnK3SppKo1hCfGiXhBJ31OW4gfwB2o92o8ve'
        b'uNNg4q9+qsHb8HXcC/IwERe9GAk+AOJtJ+eH7q2gF0lxUWgH7lWTyz2Im244uoVvw0tLBsjGE9ApMb6Djq2j6oh1uCsT94L4nbEUt1c6DU+ZjU+jZtyQCSWbNUsr4ZGV'
        b'noY7xQxuRNt88Um0L5X3ousFvuS6r1qRhvrQER8GdVm90zh8BJ3JsFLB+s5o3IV7U6ECkNpjRGgfC5PZuZR2FdqoL/DFDRFqvBPaVZLrr1B3GsjZDSwjXyQRg9R730rW'
        b'JHL9k7g3IoxluBQ2Eu2JT8fn6PQeeNprRSVRAskL/ObEr2Non1DdSnTf7I878XXSbjY+xDKyVdyiLHzdSjiaUcWTSKq/vxrvgrk8sSUdXwnHu0XMiI0idGF2EX9L1iEY'
        b'jq8aKoCpS1Xi1iTooYgZjm+LA0OmGd586Vf8DT6XP56q+rnGB80NEr/20U//EPPfH2b+9Oe1t770efrY4tdaxL2a+ICkI0nBXxz9dc1f3188/xdPSsNV7wT9ttk77Mlh'
        b'k3fU3ulo7XlnzZ4HWk3s2x98Vv/6690z3pr4M036my+/9ddrRyUqw/zwg7+YG573+rXbx377xZXMY5++/bff/Oxh1b7fXVv6r6923H52kzXxzNtvvT/9dqFVM1s7/L05'
        b'r8r2TUi7Fr5y2gHh5hDUgJ+DBWkSNDW3YF7s2pqJ+KSF3j7WhbvQKY1bxQWbEh4jwW05IfS2n6GofYJdZeM12660kaET+C7VWTyDTi5z4nWl0IVsntX1NvKXCl1fIw7P'
        b'VKWmZmiU6DS6jFsUAB24TxyN90ylvrX4wkj0vEYZmgK9YBl8B/fJ0HluY1a1050iAf/ulT8efW19tDpdPs/IUT56mo2PTvFj/VgZG0Kfjj9ielGJjK0eaueDB+oQNB7+'
        b'vDoij7HZvpGrR0yryGM1eTxNHvnkUUAeWvIoZJwUIO69hn35OgcqKbA3UWhvwt/eotbeDuXzdaQKJz7/rWme+Xx341N49/vpiGmgwDf1+/PcsC0o1ZbRv+SSFn2/t3Ae'
        b'XKTv9yW8C3CMxFqM75F90EU+DoiZ6G2CbIh5GWH2fZzY/QBg+AMFlj+IsPzFQQLD70MZfl9g+H0ow+9LmXyfzb45Du8ODH+b1+AMv9Zu9Sfnr3N6DLZ2AXGY4HPLgbbC'
        b'vAHHCvyC1vFmQ8JTKOUlpgprJaQCK611pVUVZYWGcq2NewkDxiaMkl2e6hI1gd1ClHTQLjm71EQk6f8rofz/WUJx3G6zyELxMXYF2fdIKk77ky/PR9kqcMuurfweq1GP'
        b'zfH7n29H2PJCHM/xllcQhY+J8rTl7jnV9RWEpTSUaY0eeOKVg9jNgqTh3nLWY48JpuL7W1hRsZb0l8So5RkCdGlpWF5RuAYWHuR/96eP5URCSoiPjBJ0aAQQQLwj1a0c'
        b'sKn12Ak7opwlX2q2ao1GujMAcKoqDEX23bjSwSR3UCFRQLTOy0Cd9VY6mu1+rxhHij8iyjkZh/4fIIkl6dfrSwTTnv8rjf0fII3FxEdGJyRExsTExsTFxMfHRbmVxsi/'
        b'wUU0iVsRTc6fMn+so7fxySMX9hR+8UwYY40lPOT+Uahbk5qBG5WpdmnLQcRCh1bZpawt6K537Ci00zqaCnz4wCxBxhoWKEhZnJ8SXbISsxu8s3q0Rp2WAeyt23r5SvEh'
        b'dIyIb024yRudQZ3oJBW6tqAbC8xZ8bMysoRLlIgYtxy3Q6E23ACilg9IJlAphG/nrAIp5CA64c2AILTXNxOdmEIFGOC315nTyJl4loZcvRQpxifxBWZkkgg3o3voGM30'
        b'FKrDh8xhBfkZuDWU8PLqVHQxlGUmlEgk+DA6SzNNwNuCffFN1LpEhlsYdF+VqUTdHBMMgtox1AhdJvzvs9CXTpiO5nBNMTounH+nKlPR9SXkttMo1CTZML2A2q/hvtyV'
        b'Qs/QVXQ/Vakgt6cOwydE+PkidISuVbNKRBcyMl4aHzztCYZekrrBNBfdx8d9pQyTy+Sia/gKlZQLQES84ktmCaZ0F76ZAkJoC96DrxPB9Ew8bkLnISIdt6YQ4WzVKNki'
        b'dArfpSJjAj4lwq2bcS+8pzKp+DBu569jvYfubzDhe7ysHoVqvfibYc/iy94MtEQsjiKYiM1Djf/87rvvbq0SAEs6aXHo6FX84X64nj/cj5RuKQiJD2Ws5NgRHcF9uJGY'
        b'B7QIYn2Kchm5yTkibSnARQpuzglVAHSkpNrubFagGzCB6BAjZaTl/quLYE2IUn6iH6rPwZ0xaSJmDO5gYWHxhRB8lVo3pKO7qMcXt9B1WjIANTI3U4Qurd+Cd4sZVL/U'
        b'+ynUjp+nl8Kho/hE4YBwvBjtWh6KO3NkvDBsk4TnDJcGJOBmetEzvodbjOY0VVZGRHQgAaTMVCWVhRV4vwRdQ0dRDRX1oys14fxtOgop3hnK+KL7HO4dOYNeUXxAksm9'
        b'JGU29Bj+NPztkQvjtzNWctkZPjzbD/fy+g9S1RJqqUFADO+MyMpYHCpU6GgPAcB7xg+3T8K99JbeKpBuW8PVqcqpuCuMZaSojYuYpadJIMb2QYdxy2R0F6RIzsQm4O15'
        b'ChGdZnx8OKLl5qKLtnKoNoNeN4wOcLgGyuGTfkI5f3yWogZ0Ae9VDAyzNkIYZuoKw95vPmPMc0Cc+uVfV69ufzJTFBW0vcRYEd+15dvdyrrw7JyTvw+IHVsgDg2feC1Z'
        b'0X7zxVfki5PfGNa1d3L2uku5fS03j//l5We+erjROPXTjwoWvJh7sjsgznvsyADfV89W/vFX/Q2/0DWNTdv67oqhWYX7dl377kFie2aZJq/d+8HsNV7X6w8eD1j2ysmm'
        b'Sycy61/smHCw2/dfn71x940HD9r9f/unhNeefG3h15LOOdE149UPu8NPvLk1fuva6R+MW64c+uqYsH8crL409MAnK1pNU34aFf/O5G9euvnTj1uvHjpnyC3QHZ64tu+P'
        b'pmNFZxUdK091vvjWv7KXBRX/5neyV70/K/2vV2dErx1Z8VmZ/q7kV2/HvrH+9Y1dOX/sqd/z39ravpTIZ1b/4499zx7Y03Qo4PaRxe+tfn3+zZrPf//dwuHPWgOn7Mu/'
        b'sW1ExYol6Zf/Ep5YHHzn1Cd/Cfz7YlOPZLnCn5qY4PuoFW9bs96uuBhQWsynOgujD95u01gAej3hrLWgOousbP5+4V58Bh0WtBZF+ICDrYmstIC/OrUWn6vGB2UaB7ue'
        b'wGUiI7o1y0JBqSYtPjzMUCHYiHg/xaFTGfP4a8B2os6EcDXF+nfQYSWBpVZONb/KQkBpDWrI0aTjTtQWJmW41ewMyH6WGq0UoFYROp+eoeSIiqZbrGHR1QR0lN5cp0T7'
        b'8TYgD8QoBLV7kwFJN3HT8SGRhWBk9DxsgudQU9Ym1OHeggTvxXeoeQiuzUN3nA8VmzVe6Aw+K5wqbozhtURn0eFCM9llKkLF6GRXlwzB7SLUswzzl909jXfgoxrlotGC'
        b'WoaqZPBRfGCQe7kUQf8hHY07bU0A0UQMCOZUY5NLmIUt9IfzE/Q1A1obcl8zr7OhIY7YrIyH1GGslFquECsW/mq1YAgHULsWH45etTbCSf8x0Kqg4/Hj9Sx68igmjxLy'
        b'IJdEmgzkscaue3Gn3vF6nAufffg6i+0V6+01rbG3429vYkDRQ+7Qz3NS9JwN86zo8TTQIokDO0ZO3J0viJfUe9Uz9NSVrfeh6hnferH9gnhJg7SWeVZaHbxJQtUxUqqC'
        b'kWyW5ji8ezqHJ41NYB7l/QJ43i9hIf2cwgoTV2AMeLKCyaWxuIgS7g2lWQXKpOrVDCUIuA91K8yoRbZOxIgCvPANNqEE76JMDr4yHnXloJZc3LI0YzG+no2vL/WPj4xk'
        b'otERZtwIEdqKtgGhI9tAHr00B7ckT8qNi8SNsZFiRraOxUcT8EUrwVuoE7DAbb6mzWjnUqBYkjAWHcTbUAvlNBLxEXSYXAi/K4beB58+k/Ir6PrykfgEPsUxxlJmGjMS'
        b'7X2WktXk5JEadWQsPor6ouM4RrqZhZ2/D9/hfV7rIrPC04Rr1+OqhIvX0/Atw0t7/1tk/jNkUV2vWZB1F6iR340PNJ+dmdtUl/329k4vkIeLey/9cmnY8d6Y376/a1FK'
        b'/PitXh++9NKDD36/6nLS3jl//p8v38ocNlTXcLSz+sf+oc2f/fPsKzVD/FdbPpk0bhm3IErpkxx85m9zn0mY7Rt9ceKk5T8+fPrlHOmc30T+Ji9VHvdJTOuDyoCvbu49'
        b'HOz1YvTl9f+I3Pt60oef5qSO+bhb0/aXiA8+Q9djftPZPX0arlC3HvHe8umfvr76wZyv61d8Kq/+y8OFtbmTi5NDm7uuHXr39s/2nPvW++nPC/f3Xazr/Yfo3ZvvnD71'
        b'ZsQvVev7Hnwm6f828Ogvs3/ywQRFMG/Id3QGQYm4KcILdaPnGA4dZ5dOxbspxn0ad+FuAeWKNUpcDxh3Gn6eEgBUA4isTUC5PL4dii9y09HtakptYFFrcQfRazcpQ1Ct'
        b'O6O9pmRa04iVMqBZeWj7I2QL7d3Ek5rmFdWaTHR3qhI4wbYIdE7MBKB7ovwqdES4AjcLGLsmDf0uh3j8etTOAtfdhmr4S3Z34fPjHO74RncqGT+lyGvkBn4YFzb7AS1q'
        b'Q0fs1+3zd+3reDSPD81BHRpilhmPryrtZpkh6KJ4DK4bT8llcsRmzSP2lsFr0L14EbqAzq6jsxGI90MPB44L0jc9SnpBlqJkfBM6TQWd5rQiu3WrlAkcL3raGEoHFJyI'
        b'+jTqlPXOdBf3oEZKeEMW55JjAP9xAxQnCnfzU3GlcJTjNwHwc7DPrqDbArVC57ega/zlnjp0xXYl8YZAhhbGl1BTmIZwh63AZ/RkpQK6QO1cxeyAx8PF/0tfG7AZ7PDf'
        b'FqBkq3iAbEUQokSNKKkppZiQLI6DvzwJ8yMYm/6IKSHjDyBIiDe8lNnT7T/viSeKuQAuhCPEzdFgh+8AT8C8BkhHvxevtDb3S8wWrcnSL4J8P5RaSUzkSzymcjtRqrBT'
        b'JkqUyGW0FwlRmmQjSjXMrzx/uMC12/8brMBE1HJO/PUfXXQRvPOXxeZxIuh0jYKqxaS3WE3lNK1MriVHBg6am8dSt8vX6jeaoZ5Kk95M7C15lZCg4zLb9fyCfsidmvzR'
        b'IwAjr1gj3SncaNG7UWE50Vip4wQ6WPHT++ZByDuC61ET3ovagIG9goiouRtdXQ5S/hV0fjFqkADFqhE9UzDBShzcpHg/SJx7YJ3VDNqDe9SofbKVrDN+TouuUgqMmpar'
        b'8F6NWi1ihqGdWWinCBD2frSbUu+OjaLZDSx5K/DzHy/Y4ON6CbaVRdvwieUq6STcWYju4pP4eDQTFidJ0OPTVIAbNRvfAtlu6malTbSbgw7yB9Zn8QnUl4OujhJovUCe'
        b'h+DrtKQe3cP3NBTZcKYxhEPAB+bQFHwXd2Xm0CKTw4GwtLBjp7KGZwu3SMx1kFzd927GyxMDOJD63vtHcV6B/25dxIve7bLYFZV7/J8PmPPB8nU74t87GnuS+0fXd11D'
        b'Vtw+2vN+80/+on6xffiC5mk/P3fs9CWvukvKjyzd71c++d71ipKP/nz9sOLqdM3kbXu/83/1xqjFV8vCV36++cnczN+uPpi4bsefA9/95OuDyT9ah7/4F5c5furXvW0K'
        b'KW9t2IhvgzTtdAaLrm6wmRueWE1JJa7HV/EBcnkx6oiz31/8zHr+Rv69uehSuDqDg4GenT6E1YjRDorPVwNt6gT6hrfiOv4LIhzjq+eAeHaNsBDb8A3oEtruInAQYQN1'
        b'4/vEjPHwCloT2q2odvgqDCVTafhABa5BlxXS70EuHkwgteZ8svEoRp00gFGNYlEwz9rDX4IfyWGu3zdSyUjOAa0IhTO/1z7SBI8/PIK5nnssC0mhiW62X1yptZR6vgk+'
        b'iRHu1iZHm+SbElL7bfDix7oNXnCge0/EujnWHEBmBK+YtVXkzWh0RGuP70JHBjJLnlosDyNvYXLAzWZegU4Qln4D8dAl+uQwdbWhMkxJGxIwp8m9OtpMriHU2ZXgWlNR'
        b'qaFKr5ZnEZ39eoNZb8eOtA46AJpdKy+uMAJl+B5URxbR2wXVyTLpBfe4qQwdDU+BXZOdArxKWkY66h5SlJuCLuIGpRq4iBS8w6sSX8C1PGbctmSRBjZZWoYa7wRmjtyl'
        b'34RvbYlYDDKyKpRcRKPBN7zQ3ggL5diBh7xVgveg89LlVJMgMrKAy87hw1birJApXxHuBZi0k9nAbIhdTeUF+SS0LTzLiPcBSC1h8MHlYsPoH30hNt+AtG/fOv9kS2IA'
        b'ivTbsSVRkf10zvRM9hC7jpXW5d6QTZFOCS26+tqPxgRPzjEpfl77etqDpm/mzG66Ld/9ZvI/PnqxNa96t+4VS39e+rVvTqvXlw9pqmOurGsPqv/52Y8X3Gwd9XOfvKEP'
        b'JrcGxycsi/MK+HGO8sln9uyvPP+30dODLp357NUpr3fd/PbAn1q+qKj4nxuV+7p2/u3Qm8NV90NerB7z57Q3/jU+YNmZuLTvLry2aV/aq+a5y8ZWhb46ZwE762l5syKQ'
        b'snZla/DJ8JRpqFtJuEbxDBZdkuJtvPKnBajLIcBNqDElU/j+nAw3cc8uwrt4lc42fBdY9l58Lw1fWy8odLzRGQ6dQNfiKLfvH0YMq5WZqGsirA9ITpncWLR7DI972oxV'
        b'uCkA3YQUdSpN9sU9HO4LQrco85iAWjUadChJiVqz+K8g+M7l8P5NEVSpMz5mDrFVipi9Kot4HG3mwibgYzxzvw9fSiXkQwFMOB1X6NrASFEJ2jmV1yNdRs8FEpy7OsSO'
        b'ciOXUI40Cp0bFR5BDitUagXHWCSB+IgIbVfgk7TNyckRlCuXoF0RmRJG+gQ3YvYEWnCRBR/XoIvoPK4TQNR7GIeOadAF2qXp+AoiHHhLJr5Gek2mIokbCaj/oqC/mhFH'
        b'2OhNRMoQvq6FrqxHvXQWNbgW7SDdmqEk3ziQorOcchQ6OJjG53twtwO+FpOd62xnQ368eZ2NjHoU+QFza9PBBEFstb8dm5LSPLbuFr6KYGGctCqeO9nN8XkHrsGvgsd3'
        b'jyD12pBBvpLg1A2F4NS9gGziAU9pQCrCP4WE/8PB79BH7sMipvu6iqL8fOqm1C+rNFVU6k2WjY/jIkVs9akhD1XyUKaa0ic6Hp6xH/Yf18ANuqomcvb2ASPINDJOLPZh'
        b'pd+Jydx9N2wqzCbLfSsV/cC/4gARAIBQS0gEAMV3YhHz3djFo2cEjJGxVPMC2KANXTGTr1qaAwJEjD+wKs+P4/Cx1egKPZ3ywYc4X3TWQhDK0jW+5CAmm5xgjY0WT0bX'
        b'xP+bvuzk1qvE9STTK5M/nmq0LERn8WniUzORmZiGanmycTobHdGoUU9kHMMsxvfEwJmuw6dQM8/U7kMN6UQP1IevO32CL1pMS08yVuKmVCVhtGLEDLqYKkNNXBreqjBU'
        b'vvGh2EyAtvSw6uOCVS/0tB/bE7V9HVvk9QF3eruf76jEeco/DTs97E/b0wviNT6+KzqOPThd++LFqO3Hao91pu5mpwx9+YUDUmbNnCF5hfEKCf8tsVsrFti8KZfjTuJQ'
        b'GZOKOik2YnEXukE4VMeP+aEreAdq5eXyw2gfus+r05Usgzo2UG06Oh9OmVYVrsngpXYisVtjqMyO7wdR5KpAO+aR816apt8sW83prfjiYD4zfiBuARejzyfmDxQRhTgi'
        b'oilEBUwQjxiepmfsO0rcLyYF+qWCN5vL16TIbXWmTfYdQUpO5GzOkzXCz3ueWUYKrsPwVXQ4PDRNleKNdynTUEsEf4Irx3slw0KyXWBquPDX/KXjZSDh5EIMAFxOJ6rz'
        b'zhPpxfTbfAz5Kl8LlyeBsIyGvWlYCmEfGvalYS8I+9GwPw3LIBxAw4E07A3hIBoeQsM+0JoXtBasG0q+66dTwqZhdcN1IdC2n5A2QjeSXP6hU9G00boxkBagU0OqlLrs'
        b'iHVjdeMgjlzZwdaLocQEnZxc1NHh08F1iIpFHeIOCfnRjSrmII78Fdn/8rH8U8zncHiKH33XTTwUCHX5DNTzaBndJNe4f++pm3xoqG7KIS5viD5YP0Q3dRRzdOgxppal'
        b'oWm2EM0xjFo48s5MMpgTL+F6kuHU9tGLzpNEp9CFQVyIbpRwKYl3PhAl7UJgjKknuovC3lm84K0opfTLi1K7ml7y2Gp6l0/lkn+u7nI+vJr+uZli/iR92tnoduZJ/iQ9'
        b'aU0zM5JlQiNLXphflDibj0yMf5b9J8es6MlQiqPUVYyVfLzOGIx6nBzwbSd/N9AtXsYk2lsvJqdEFoR2o3pa00tLJjGESkZGndY0jh/O/NnWS+pwaGi23JWYyQiGf3lg'
        b'XPMV/5pIP/G7rfMLxDeOvjzeb27RvF3qSJTCDtn91uj6P32WX31310+lviErs/7g3fL0yA6fn//olQVrquqD19xbceoXGdJ8r6LtP67/8++SEz94dZ5XyS8tf/3N4iuF'
        b'/XPOHh61QrNM4c0L3V3WxWgHvsZ/UUglYmS5nAV36WkiOxvtR03ocjq6hPcSJbV0OjcEXzdTlnVsBb7l7CsfPYKeYCaiA1TwBnb47qRHBW9+UqaOkuNbktKcWKoeQG2o'
        b'SXBoDw9V8dkgk6lixFjxE/g2bqfOiF4j0fO4F6aX9hQ4SKLtBnQ9BHcR45CtuJ4y4gWSjFHxA3ky0AUGsnSK0Al8FtXy1t47gDk9iQ9OIWqDnRGp5GvVMtzIoTq8q8JC'
        b'hKhUdDMBOtSFrq2Heih9htpQWxbQiJ1ZuFUtZWZqpGgvOhDGI+DHZjEH/NbHOyL2aCnrI5GxI6n/uqBsZauD7dvnkW9N8qrRfgm1guoXEyPafr+Bg7Hyin5vQ3ml1UIv'
        b'DhtgPx1N1SWmbeS9hjxqGRvnudWpnxEuJOL1QRhQN719LO/cOt47V5JPhuHRLXceJ+wSx3bs3uljB+5AdXHOVZs0BPf8gK745zvOpccuJdu69PV4h+ZdHdPVP6Rtn/yB'
        b'lfPU8CJ7w+NSbZlt1pw/uF27VzgBpvwyg2fP7DR7syFE1pAXmyrKfnh7pc7taTd4bC/D3t4w2h6x9f03W5PmWyosWqPHprLtTY3KJRltNsEe2/vPOXm7fH2c/OMY108k'
        b'Ugpyc65oWYGIKqLTt/lyPIESZUg363ivI+W55CcYw8l1L0rM5AK47APx5Nu/KdoOXeifNFq/4g8LDl/6kPmya1TO/pdGbRuVEMMU3JR83McqWIr4/NAu3IeaKNYbiU97'
        b'RHx4+5JB2FgqBFIkR/yi7UhuGeFbq4c4oonH9//OccFFlwfRcLo28vA7+Pf/rUQlLOFwg4QJmnsImq4x7vcvnUIn6cVf/xZqCHqHjOGru4ZTi8ZLzOQWl839cv7jze26'
        b'FS/sR/tHI3StvVv08k0t/xFKEbOmT7r1r6yCo+uHev0ILUfP4XODU66kIfzxbAeqAcrYBES3E58PU6nJ6cQ2LgbdnDSYmBKYT42eDdX6/EJjRdHagS8B2tZ6VfUohyVw'
        b'zu30+VsJtdZ1lVh2M07akF3wWOECAucGAQHP7TttZBsUEPCzfQ5XBHAg+jfgwGUrs4z7MywKByWmv7OfiJjSc08V5A+Zs4yhB1Xolho/h86LR6HrQOqYaliYWt4cowWd'
        b'xzfReS52PsM8wzyDevysBEDQCXQY2DPKiaJtswasYXNDM1UsE4t2SgPwZdxCrUfLIijPy4QkFRjHPxPLUFPID9WZ3EthoTKmUjv07ZHPR/QxVnKt3zBuqO1qKN4eUrCF'
        b'bByKt/Kg5HQp1DF8wAcfrPamWJQaigzdlGvUO4j5VMZfiS4ZQn90SGRugBxLfjNm6itEWzxSVJDYljRi2RuJkcsKtX+Qvqz88MiDN04W+mj+K2hd4x9OT7H06raY0PB/'
        b'fD5myHuRB15q6EwqQYpJ83O1IycnJ376kwOFy9Tp6R91vxRgfX7n5IN/ufzr3Hdn/nFC797fbrl4VSE/+NNlf9++MmRt1BvvvpOav2HHuz/7sWTPkHde27L53QuTzv6j'
        b'XuFFRf3p/qgJZHlUVz6gLSW6UukIyjY+PR312BneIZEDJnv4Aq6zkPs0Ud9GWKJtsCRNg+8+3B5LjeFScA/e7hsmMMeJ+Iqdl56AesX4cipqo9s6BF8mnHgW/XgnWWJ0'
        b'Ia20ELXY6pUykeicdCw6ig7ySovjuAadwi0au8ciNVRAR3hbA9SAG7PxjfIBxQWvtjisU9g/Uu5RRyrNX28yCB+IdeJh84kdG8eOBx52tGDf5sdWBzlsQ1rQ+ePXWlOJ'
        b'2QOHypk6nHHAHniscsEBpwf5QKhL45lFYoft6XTELHzrmDry2b91LKanWxLY/WK6+yV0x4s3S3Ic3gcTPyUuu1/K69Xi0KFgRGy7JzAgSB6ZYFZREZnunDJUlx2+WLVM'
        b'hS4tx4fEjNcQbjxuxUcM29bukpjJJZstL4cQ7Vg7WrjmzRffebGn/fae27W3Vyi3K/ZP3H67trt2Zktq88T9W2PGMRfGyVYNHwb0ncxaNbqN2kHsIYobBJBDvzQLu/cm'
        b'ujamVIwaUCOqty3Q4KpyaT5176BgEOQIBsYAagfiNPc0K68YlzoYBNLvV1PVlDP67xbzsY/kpEDQCQ+DCxAcGOTzwS4d8QwDRDavlwAUSKlSg0CC178BCS5fvSb/XBUR'
        b'kkx+yamKchtqysxRLTP5qdBelhHh59mMSfi2gWts5qh25ExI3McFGm2oPvT91P9JoJzchwUfFxiKw/Z+XPCwYG3xJ7qPC7jGyPgY69VTkdaeqp5TUTujxDGVNxjG8rb/'
        b'iOJfDPC9j2Uv4/Qpc6JddFjwYY4LbpLxJkHEJnW4w1wPlOGr2usZrPbZl3c/PCpclnfPSM/L677Jh+QIwvNCz+U3u0TY7pL/1CK7bnfbIlNu6yqw1BdyVLh79jLcGZMi'
        b'YiRe5LT1Er5uuGG9ITYTH5Cj2d0fF8w4ncovNSx0ivajArX2w4JPYLE/KQjSlhanFwUX8czfWY3X1+98B5ubGoScQMfReU067okSbLuLcfvjf6e4PyBfuKfVYaWdGPhq'
        b'stLVIx0m3KmATRXivG37pcXaIkuFyQOWF5u6PG31g/BY7wILTcM8w4LHrikCeQPlAXtlYqrc7z8g56/Vb+z3r6qwFpXqTbRIlHMwut+3iFxvoyefnY1yDET3y3QGM38v'
        b'DTF77pdUaS3kqmO91QLSLbmOl2zgfj/9hqJSLbksFqIUMnoeZyJyhymRPNxcqkxO5vJojcToKqrfx3b/jEHn4Ky/kuawGCxGfb+MfLWEZO73JW82t3caTS+6ojVFm46T'
        b'Ml7E87KwYgP11O+XVJZWlOv7RcXaDf0SfZnWYOwXG6Bcv6jQUKTg+r3mzZ+ftTQzt188P2vJAtNV0jTxZXLhpulVqAR2FpJNJrLfgEVoq6xY9p+Qr0RCE85brYjnq+Pi'
        b'N1F1beX0LWOC5xt4kooOLkK78fPojBnfCATw4vBpNkyNd/P+dVfwFdRltlRBGr7uyzJe+CBXtDFgyFArWZ+cwuXhxBT0YmhKhjo1YzFuyEQXlbgtIm1xijKN6Hwv4ZoM'
        b'YOJ4Byopg/es9JsPbPxRnnM/q0SX8Z7FDJOXAyx9Br76NG/8fQvdL4hZi7YTk212OrFL60N7aZEk1IfOx+A9aBeAfwwTg69U8qNoA9muPgZ1okuxkQD4oUSAa0WX6VUs'
        b'qA41L7HbwLKMbx4HNbTiS8CPtvBuRNfxLWVMDt4WGyllWAWDOpX4CH9UeRPVoivEyLceHcXNGXHk2/JXWLwH35lEJ3VpYRiTC2v7wqqNSXNzixi+vgvoeehO5orYSNiD'
        b'YQzai4740NtK5qB76zRqlZo4HmaocGM68BiHt4xAJ8VzxyD+WtveKjkDaDghO2HzpoDhEn6ZcA/ahxtj8E1cExspYlglA3xvHWriTxVPhI8OJ7ezpBKm1QddkDCBqEVU'
        b'iNsDaY2VT4cwwIYHVXpVjV25MJ6hUzlvSlQM1FkfG+nFsCoGHQhm+TW/DVO3E56dwALT7zOJlSy6s1To3XsVs5lNDDOyfXm16SPxeH68iwGB98UswpdiUQ8Id2qAKm0g'
        b'7XdUCDpJbMdQB96RAWKXdxQHHa/X0rp8J2sYYGVl8rn6sDtlE3jTf3SJxWdj0O4YqAuWP4JBXYvQDt6I/jzeugQkAtFCEEGojcMObjKszwlaW+By/twiO8yQvjZ+Mt8z'
        b'fGYZuhATia7HxjN01jqhVnpoF4DuwrKSO2yacCux4cZnsyUQWyeajfehDlplyKYEppJhIiufMgQ/IZXwkugT+P6iGHwuLDaeo0Pdp0GHqP/dfFid63yNmQK04T7cAxA3'
        b'GnWIUeNG1EVHuAntQs/FoGPoRGy8lI5wP+ry4kG1GfdMFqogawl75RZ0qlKUgE8Np13SBg5lCDJ8YXbREy0Jcn4tiwv8YnJQTTSBXhjj3skA+byROT6Bu2CYa1II7HIA'
        b'u1dZ3AGQX8PPzk0QhnbEoDOL4yJheqKhaKyMZ7uaYdddCNdUIWqWyDJSAzdqWAidgNVATetjRm2eQcokkN635tP1mVqJegU4bESXGcbvCVHe0CB/dJ5WWYifw5dicAc6'
        b'PINs0VkAJCDwNVOgm26wavjtqSBm9n5BItQ7fjg+hI7zF0iH8Dc9t4cXpg99ag6/DkOA898aU4oaZ8QytLoD5Qt4178G1DEZ+oG70U3id6kBSCnixqDtHO9PeBDdhfnH'
        b't0fMiAUASyT9OCKYo65Ow9s103GdhpyOcBXsXHQGH+SnasdcZQzkuzojFjr/BEAlaphIR10KyKSd+CD2xGfAwjXDXA3lvNGlCv5a7aeqmb8SGJ+oDbH6egnuLYfR+TTU'
        b'uzEoMlbCsEkMOgI1X6GdHwZwcSwB3QEJJI2c4ojwPRZ1QYF2Wl3y4oVMM2zlL0aa0kblP8EDeQDeoUe9DLofGQuoYT6Djo7EtXyve0rxKc3MtYBogPF5mo1A94Tdcl00'
        b'iokkUyoyjW1/MprvVyTguL5xMZpUYkEkFrPQrwZ0ioIY7g4HbLHHFx+itsLqdNxArfCC0A7cQF01lqSAyK0inrRNEUAKMpSAjRh8AN9iFgV7jZEsocMbuxY9z7vezoyi'
        b'yFiG93OoE+/lBq7kfjmc9zvukVYqG3NYYSO3AoY/DFNdh+uAY1UySrRzPe/22os7ynj0XiwaOE4DUiRmpqJzEuu4kbRpCyDtc7hpMTqAm4hDECC2YHY1uoYOC26muKNA'
        b'gzq8c3ELgAU+QHDutiH8xWJ7ZqDbvCc5vjFqwJmcZaZmSQxP4jZhGRr1uCsN3/cFGLwH/9FBfM5KT/xuorY54TAvxKP4OLqZokrjJcwoMTMtVxKNr6JGOvTqp0YzAM2y'
        b'o08VPnEjci4P6KlAya7hLk0IcOnoPvxPBOIkJ/hzKtplq/WccqBSjpm2VBKzZC2PT8/hk3i3Zi2qXwwUmHop3xVPsgq3cR8LWoRP5ADpbgHS/ww7Ft0G0k8Q9wLciY9q'
        b'8LaJS/npOMXga/gCJJKGU72HObrrzyJHjjAZE1CTGN94FnXTbo+Zkwe4pzPLn+h/4D9ss/uUpiYrZ5PNrk7NhFKpKrw1OVrMjEEHxcbstTys1UwpxF2z54mIjw38x+1r'
        b'Kcpegvo0jiVL8eloDkp2ictATNxBb3dbjvYPw02zEeHADIyheCwlu0C9+9KJ9aftyLUOX2KZwKGiNbgGn6EFvVA9Oon2RK2nqocJG+J5M/imNag5nL/5DMCK6Afw6eRQ'
        b'lhmLrotx41x0QMAOaWSJ8PYICXH6hP+o6SmqztiEthInoSVoD3Asa5m1eSkUGAstsRqVKhVdCE2DvbYKujt0rghwY+8SOgOBeEcx7hpT5Ae1XWPILePVPDtyBtVNGXB9'
        b'xfsCBe/Xc+ga7cgKvF1pluG7/v6Apcj+u6hCVylobdT5MLAssrmT1xl3MBm8N/9E3FqGm1IQIBqmgqnAx0dTeJ+O9+J64OtSiL9+syYLIKt1GMEJ8jFi3DMe36T6UUnu'
        b'FPY1KChfn2n6asOVyZsZOpEsAEodOr9aLaaK2py1BuOlhxLz/wA7bFizevUv3yp/PTtI+vuZP2l9/VrG+zuCC6t+du/zYf3BoR3Pnvlk5a2R3op5S4f98Ze3J8oPh+v+'
        b'Ip59+QX8hewJr/vTz+z90YKOl/8884OfHoqat2/F3/569Md3JlydcfxY9KnclaPDh1ru7p+05hcpP1rz2vivPzErVD/62blpz23Jibry2cNk/zHvbO6S+3+hML+gP//H'
        b'33T84vRLnbIDmaeHvJr8Uu+v99xqnJGx7pWwS4neC/4k95++MvlPE1cejl1wY15e5qRdn7aPy6xq/GTbJ1VXF+kqjn05e5fkwebpXskBSfGJT0wx3XrtvSG7Tmyf9ZPk'
        b'1vmZCTMVpnPZf7724MC2Q8Nnes38/A/bHix4MHV606R9E5dfKPnz8KlrPmj7S+SPTjWkbzyU8e3liR/810lt+jv/PDY5LbzP+KsV3518eXnpl9cSW8Ycfrhx5/jXKvcu'
        b'vzqmLnfIzVUZyU8m9fWMWn+uZ7RO8erZv216ae3Gha8UFP1zTdWrJz55TlR+Zuqm3xS98puT/cufzrRsqb38k9Fd7d+cWXr+997vtv98eW9vhu7vW9Z1VTRezPCzJt2b'
        b'WlJeFLBeFz3x3eG3Zwy5N+fh1MMfeL1V/OX87i/OZr935Q9zfvr5rD+cmfSqqfsr8y5r4lu/bs9P+Vf0u33t+d/c9LduVn05bc5Xy95f/6/frfn296bZjbDpA6q/+dfU'
        b'5BtLPvyvM+WTf910svv1grwzP/vHljDVN02KUMVQqmfD2xZsFEwfCkJdjB8kpegQauT9Gs7hrZvCY7cQXT2HDrIZ6CJve2FA+zfhPanAIIGsIWXEySwh57idfkMANaKL'
        b'RtQUWOlnwtdQS2CVP96GD3lLgaweEVVEh1IDjblhQb6oW5kiqJTRc+g6MBN3ROhiqpoe/pTj+6W4CRggZ9M3wOK9tAumRSmoKSICNwZYldTe+QSHmkJxDX8h3rXgHKqR'
        b'Tl+3kOoQZRmcDjfDsMjGNuHzqFvz5LIsMqwqdt4YtI8v1YVP+Yer0cEkwZ6OGtOpUBedjCVReJ8mx+4QyaKrT3G0J37hMPgmdLkQHUy326GcRtepNrsgSOlshxK8kKrl'
        b'/XW880k9vqF4xGgE9RgEuxGQ/ajZCD4fEuZsNZK2TLAbWYHPUif3OOBnj+OzU4mlCjkRIWINscYWdKjhMyXoRvxm2mZ5MVABZy2rz1TIw+tYD+KtvFF5H0hmbQMuJ+hU'
        b'rOAcudqXV+MfKSBqf2Kksm6dg5nKlM3uvj/wgw1j+0VaHa/l2QAPu5ZnC6MOZkNYMRtMDQ2J53kQ/Ao/XDDr8kPiPpKNC2KnEC91diSUIb9+rIwbzcrZAFqGWE2TvEE0'
        b'fxA7DELcJ7KQav8BpQ30x/F4wET0dT/UzY/jSw0cG1yDxznOZtNdY/95c/QgxtROffJ88j8XHvX8p7mYeoldj8hS5cbjnf+76BFJY3LmUeXGdF65UZMhYuay5Ki1IP1/'
        b'KpcxvHKRGuqe1E1HxMNtPJBpZnwsMK4kWrYKNiU5ORnlByzqKHx0Kp+7GWSXzhioPhptL2Ki/fNo9XleMubB3OlQe4Ey7tlhDD01PLLEm9k0dyqJND7wX8dzr9uXPss+'
        b'CPqrhInUJqblqXkBbQEIHdvKx8WAwAEiKFNUgc9Tcl2KrheiM6gxJhZ4WrSPATYe76DV7Ld6MWe3jCWmC+lR69L4uhM0Q5gXSpNAoi/wG5YUxvdCHBTEKJOTSaSR1cr4'
        b'nAeK/Jk3kmMYJrvA77+HR/I5/7bcn4nNiCSRxgXFKUKdM32Y3DKiHihQVvpl8Dk/Ffsy7ySrSGQ6emYOH5lokTJHI8ZQa4qbI3MZ3t75vgZ3UAZyKWG4JyRJqlh0p0DQ'
        b'12zCh6bERBI1zhRm+mgQ6jF/tdBQn8lMtqyVrNakduVEfqFGAW+1D50nbIMaPcdUB8TROZICXmjDXbC06IYcA/97A+1dSTkNXy4Xd5GJu1m5EB5r8nm1Ujdg9E68B8BF'
        b'FTabUeFtk2mbRUGwJuah5IZf4++MRXz3J8eCVLAHeF34kTD55SyACLr+JOqhLCzeHw4iMqlp3CR0jhmHb2Fe41K6Cl13NNTes4Ye4qKjaBuvj6rF19GNHBXxkmbxLhZf'
        b'fjIYHcPHrOQUB6TziHDYKRvWo1vMBlEhHYsUhJuz6Dxh1NixzMaMXP6yo4bCEHSeI3e1notgnhHhXnqMTJcjqkLM3IoPIeNRrl+wjFdJa9v/h+wZdsvnDLvSYkjIrBGb'
        b'Y6H/geufLtuVmInnBu0oqfp0ys9fTx1bH/S7SibZf9z73G0U0X7oxyb/zu1/iF705qdDvI4mz5S8L26YH/n09BeTYhO/2vL8V/2KW6/NrN0X5nssJPfDuubS0BNH33tx'
        b'xPGhr/6zdMXCoX+9UPzH89I8zeHfTkr5/DV1xzO/Sp6+/PT2Vv0Z0c6P0nIrRpzac6PnXs+LOzbqLx3aviOp/v9p7krgmjrW/ckChBBWEUVUogUlQATBBXHDBRRZRAEX'
        b'xEJIAkTDYkIUtYoiIqC44YILCBW11A3XutvOaH3etve1tb3W3Ku92qqtVnuttdfa3vpmOQlJSBDavt97RibnnMyZmTNnlu+b+f7ff7B+XopG9uO+B2eLZ1+DX2jOlOuf'
        b'uD554fPbzK8yKj4t+CR1K6/sUFxz/7LQeXPubEoEGdXFO2SXb/jvDUo83OLgG359V+LYq+U/aMv+c/Sdl973IqJ+DX1HHRNxXN31A89s0cn0hVtq56TeKouO2KjtO2jL'
        b'+fUfd+sZ92j6zk0fvl075BP3xIcLC7P/4vj1T1cfub+RfOPpwboN2+6AvAmfDR75aWnpL74PBq3IHpki6U72mKN1SD0z2bdGTWWdtb1rLiwjs1cmmg4biN1BojSQg/21'
        b'NArgCS7YMpGFw8OL0ya2ihZINakh4kUhEhHIUl+ZEKwwmp3CRi9sedoH1JHpWArPo+TRRJuAvZphd9HxHEbh5TGGBw4FaCiy6awMHsPutlbjDXEORj2BHfBQ376gnPAf'
        b'wfWomSL9BIWbrdugIjFsHzhALPXtndDDorIglXxWbx5SmkDDQLCFgAeGuoZj+xijbUxoYjhoAZXEJCA/kXi9YTnC4hiy0Ok1g++DnrqZyhXLk5aY0EWRNabELh7+PHAA'
        b'7utKKkII6pA4iM1sWdEG1E1xdwDNRJLomwerLS1e5eA8FV5gJdhH6mJJUZoFchVuKOYV4IU6SuRRD/eOsjCKRbW7jQo4YBXcSJ0xrBJi+9qQicEDBuDlbQ7jCWs9YDMP'
        b'1mC2D1KgZCFS001tdbPgEWKui411wTpAPVskLw4jkdbG2TFwjxufywH1eeAQbRcNqNqPtNoegKZEYn7gxS3CJmshafCIwdQh2441dmhj6jAZtJAn90WNtpJKqVhGhfuK'
        b'qZg6HZ6hnokqJLDJhsSWACqJ0KZJoeLYLngGP6jRJngJ2EXlLbkrBaadBmvhjqBAFkkyVE28LhWC4wariQ7tsvGxSaGliwWyjyri8LkGZwqeRObyRB8v9OmOPvjchThW'
        b'8CQxPNg/8rlr35P7tX0v7D9IxEXS10sBD+/IirgCglxb5NIqz+DsTSzu2ilzqwHeCRQ8tiJCbWpnL84iS1RHWFRBX+vJVyL5r9mGT7pZ4M+I8bEGE8tRg2RiqYyNlPUC'
        b'g5Gq4QhvVlHTTgI8w2ZixE6E2AmQ3WSyjagXZSSNmTomISNlZlJ0sp6nVRbp+djDgd6J/SE5OiWZiIrkYakU+sd9amiWoiAY1xy2ZxPw3Nw7jTOzc+G7OLvYewrcHAye'
        b'NOyJcY29+ecJ3wP/ZrjOtfzd8HnEf2wf6MJx+c3ervt46sO/PiyVjvygHO4oYuGtbim8NGe4os0Wt4H6RjvKkuKXv8mVUOC6Gr4VXOMRr9pB4YfkZIwUcc3mKxwUAiPh'
        b'r6NCSPA9Ipbw15mcu5BzTPjrSs7dyLmAEAILCSGwiCX87ULOPcm5kBACCwkhsIgl/O1GzruTc9EmfjaDS6Xw3sndZI8RPHOcFT28mQYXjHVhz30M593QXxNnLUfhz4Lf'
        b'HYhDKadVrqvcsh0JbTAh80W/ORJqXj7BBgnS3HBtKPpUc1ZR/UC0yhlpB30VrxHaXndFT2Iw1I+l7Y1LjH6xxQwjnmKgkUU/Uc5ecQDmUcHsWbJ8BW78Kku2T7OTwBQM'
        b'VWcJs9BRQZa2QI0JvzHCHns5pryl2MuysrCIOvomcHsL59Ma7PZS4qB3ZJnfMCsSe0j2mQXU8SrmR1Jkz9fz5uaja3lKhUqXh64JClHJFxRoFJpW4mCrjL3mrrsM/tQd'
        b'kV4lZLePnYyuuzrD2Zst4d9+0mHOXlzZv5uz99WUvW3oea16G/idlL0mL8VYDuyRvZ1SoJ9tlSFfLFMX5sqk1ooyTCzPRVnKid/z9hmE2ycQtkIW3IkaeSWBMGqP1EX0'
        b'+JhpYrUsC7PVo0NTr9uSARb+rCnZndVSmBed1G1AmElVWCk8WxDUJ15BX2yLqti6Owpb9MUdpCq2mmgrffEfoCo29Hta7fRMrFKwLyz8VS/MMFiwfsHZM7FGmaPSohpG'
        b'gxQay0hzChbr2Nemy8f+uX8XI7ArXVI5Ncodr7eIjy/OVJ+U2zPE5gO8A+vt21DjlvYz5QRG0qQZae/KKJFbhjdV/Od7MkgJCT0Sn9lzs2A2pdtFcv4eUAtXR3WzzTNM'
        b'PPYmpJomu6tQhETYpj4k4fPDnTHQo/jjtEz1owmp1Gttf7ycbJVjuFXvCB9uVlhwClQ4IQ2iDK4l6Z5d7IBdCM+44pepTslTUIfVdvDAJKvJxgYlG9LCHoVxesvgOkew'
        b'maFVemQO2chmVmVmBpcnjaWPLwYb06ySDVcYlTxwAWywLOZJJ6ShbAJ7ScI3PcjuzoytvTPV3lkpjA6bToHKHmCltZQDWEUGVMKqSWbJnsHEtBU+g1QL3xnB1a7B4m2V'
        b'WPrhWXfuQFH0lKsl0k1j+vzYYrc+IHPrmkZufENYA+fa8EmN/eoHuwy+P+pG1tW3tDk1TjMH3pgn+fLT//yY6Vy3Sw1LffKrW8KDT1cvqf3lm4TxNZ8EbL+T8MY+1/eO'
        b'LS6f/tzp1j/CDzzfFzk6NWRec8Ovb6afUz9N1l5Jc/2X768Rb/j0mxR09Zmr3eoIudMZiZBol9i8YEeregmrgsAFVr905xKFrT9cCcpMFr/BKnDMaJV+pA/dijjVJdY0'
        b'EerHzxcuB2/CWj48jHTD40RVTZrg0aqpwg0FVFklquoQsJmodaPgCmdTWmK4LjS8F9xCVGhP2WiwelwY0aGpBg32I72SLp6BE+lgtS6Y1QiJOghPg2q6mVGqHWFU9cE2'
        b'uJlV94my74sEUqJHbwVnUZGpbhqK0iHqKdVNnecUYWs5sLIH9gSF5VgpPAZPasnqBarEwODYeCLUSu2RzlfmAOqQ3rrpTxPxjYhO3GVM9LkSZizhH+bYt3IRU15i4tfV'
        b'eGYg+EXChw1m4os4eBcH7+EA4ADi4BIOLjPMq4l5BB1JxNnsmSRoxCQYJBOFbxlzox2PeG2fozMYPWGGUZCyidNLRWWiKNDWvEwoivGldiiKOw4ENTLGmkhVNgs1w1Co'
        b'F70tSkBkhN9HVuuYYZCgbOY7y5ivL833j1EjsxnzM5DcZDPP1415+tA8TWSr35sfEo9s5icz5hfQKkDJLNG2nadfNtayQWSxWQKFsQQ98IKGiVTT2TzLDHkalSJbeeaY'
        b'5Ylq2SgLmeQp4VLgNlkdMZrjJsp5JkXBRu+4LxN73EQUkI0q7NiCy6qyQuIXWZQtMprA23XIBJ71TPnMzqPDNFVKzNfZUZYqErkzJFWmpFRtksQkVUZcdWCwONAU4I3O'
        b'CWYcRTKl2CGyLi0GZi7puD5ozChSnFyQh7UKqoZjp3MsSluWVaArYrmftEh+tVU3+B/mWVHiKlGosgkLTxErn5s/FFvfxM8mqrYc1qWeFdEY/4s1skbJ2lP1Bg4xUXDE'
        b'AQZqGtuqjmm9UjG+TWcVB4zJ0ijlufmYFYfV+4hjPasFbW0HWq0qJ580Bco904YATStWmT6VCqlAOTYIbgyqzUDykocMM2o4OKeBkmC8cGKgVMYxjJzKcltKGWmVKnI/'
        b'5uHCdRcxrOM8XtnmD4SfWqXU/nksXAGYdYrwZUnEgYF5WO1Gj7MwMPB383KJAwgHl5RSWXUm6XY4uDp0f2cZscQ2mLxsMWIN6FgxzMAi7fJiBRh5sQZKxLMGhtnmtTIF'
        b'nLCvUaekj6PKJwXFvX78+ISEmTPxk1nzu4v/FcoW5hGvvUoNnqqCCemdUVs2KVBY+wVql6zLfO2E9pYQQ0+xWiwqEJlSfKHsw0Nts7WZwnMMK0km3QRdRT0yX6uihSrI'
        b'tk5+ppiDWgapD3wDcV0sK8bHHeR9wv/GmCWiJYtoKnlukYqQe2lbqefa9lmbaUrFAzG5tlKHBldjAqgFq8RsFaERKg/1uOhUaYqsKEuJFyatU5FJxai5UC+qal3eXGWu'
        b'9fqXisMtopHcZLrsRboiJZo5sBtr8bQCjZYUykYagyLFY3TZucosHe566IYxuqICPL/NtXHD4EhxbL5CNV+FGrNajW6gBHlaiye3cfcQa0XufAUNtZaMyqRYeZ0rVoS1'
        b'9DpXL8NIRbZW/Stq3urFFNqS8QqiRbk73RJNHz9bg54mANetsUyyrEW6HInt5md6u3iov+0GaBZx4DBbMVEzyw9pyz1KfxxsmcwQW8kMaS8Z1CiMz9dOGhGm0Ww+2jCz'
        b'xKw8l80JjYUPohGOPSLyAJJJ0dhqGMoDkukca3PCbkUnRorHYY5TeoZknIA4dKrMR3+omYvxHBRhm4+zFddonkyYRTJh7SZDIJBmBI0BhJVxPJ5vBtu8zQiZpLdGp5KR'
        b'Gl8QB6BOzjZx9NptV4NOg4kq0Wwxjj0KFpvIdtGpU8UB02FTrgZ1UlSWQbaLYoLWbE3MeJktlCEp7VydRtu2UO2Je7bESyJKdlzyM4poY8w2AzomwxBcaaQ4EX+JZ4WF'
        b'zu74bWH0tjBym+23YQCssiIke47V5/baAUGzolvwF4rYNp7tUWyiUqPJD4nRyHQoUA8IiVEh6c72qEWi2x6rcDq2xyecge0Bqr2c0agUnYuEMDT22x6aSNmQzKawXgxb'
        b'lYekWKWyCEsW+BsJWEPale+yCoojxXhvGclP2VhqRRdQndt+qfgmDCamd8nUYnzS7h1yVRHukChsV9yjGGockx6QhIOxnC4NHzhkCGpptsuEwcuoQPir3RaZLUNPG4MG'
        b'lfYiEfgzekP4SzxriO2I7DBn4KBtp0UbgNmR4rHoiErCs8KGthvf2LXJLeabfe3WtwHuzd5J34/twRrDvJGINnZMIno9tkfELJUcJRg7DmVtpUe2AWjjbX2rBFm3GQJ8'
        b'S1IJMoNb5uazBra7U1yNZJV9uhkQc0OHkVtSpAT0GrEpOjP+wZxeLPy4Gp5KiIvtCrcbcXwjYqlDtAkECSy+J87seTkgiNrdzoFVnrDGDu4KIcg+cDSfooo3Z4AG0Axq'
        b'LKDTh2LyKVathHj/zBSOkPmUK5MY3QB808nJcG8QphpaCbdj9sXJ2KgQHJiUQH0vMdiGbSpTPMgxB75TTGBE1/wmU8bJkoIuf+/uPGMP3byCK/KWwv0YTdjW1xJOaSLd'
        b'uTAjnKwG20QSvzBV5NYsO8Kp5Q8XV6+9OIknc7uU89NvGWlO8jxvv5XK+nenvpd5MX1i2bgLPZeXDXdylV3j+/bZMKLuudvSjMd2B+bf2Pbzo+4P+V9OvVsf2M/nVM5X'
        b'L9J2j5QO/qRYFLR4nqvXzPyrhVNyf5DIezZ+W3m+p9vjcNGDql4PZn00YNB91eZ79V697g7KXdhF9cnTFdI1XtOnXNky7cAd55uHlbKHzXf3n9LWfBMQsWCofZDXrX9/'
        b'NOF5ya1rmvJhD2LX9Lv5m1ud29kgnxMeHtpzz+vrzsXNdtFWSUbc3/ij9Jgw7svnH/K8IxYsf3r50X9eTqzq77l69P3USeL+OyUCsgsVzVlq9MeM8SNgHyiV2uWRXail'
        b'8BysBfvjveYbMSTgrIrsQvmBWnAyCFZOjgUH+Iy9Gr1isKWvHJaRzbZx/WC9KYyED7exG2kzYTMxkE0H60b4TWm7wdRmd0k0m268HcKUiUbvTmy6gekG506wBVwge1tq'
        b'sE1iwXToDs5kEarDqekET6PLAgfj4mPB2ZkchjuVEwjqFreFgIj+JH/p2AqObGjhvWWzDa0SZrKA0BXyOS4cP+LkCR9jM0Mhu5nF5fQgFIb4242zSGTcppEpFIlmHkJa'
        b'F6+xRbfJDpZjpwou4Zsk0urJ1Pgkc6xuY9X2tb2NZVZm29gP4jAKWykxq/hGh1GdIXbKQUWfhxIxGznxI7WlFvSnI+cCfzwMTuwujMqMvyONoq6DipaM0+pAGXfK4FCM'
        b'YUUti7ME7LU3QYa0gNMjnXgMQA0OlWl6oJwa72+EawcnD4ZNoCaUgl/PMvC4G/VZcL8/caLRWxgqW7w8gUsTEncB21gIByiPYZTjMih84CzYMIjFfORJGTk8Cw+TROxm'
        b'Y6OCYilXnBnfK1VCgRhl87G5RZQ7pzAzOLhkAjXyv/gavvgW1x5dHBjE+l125mNbhxlviJIyg+cU+tGYX/mJ0MXu/g5JmfGLsobQmMfcnBhPJkIqcssMfimIpDFj3PHF'
        b'd9MF6GLLNB29uCcMF2liX544M7gLbyLFgyeCVarkpEjQnJTEMJzxDFgOT4D1FMJeJQTLw0O72YdiLwCwiYHLe8GTFHHcABsHJiehdzoX7OWCvegncGISdS6xFjaAC8kJ'
        b'mrkGwAiBi4B1rqTC/JcGErQIPAhbOH7oRSwBTfRNXeRJksl++UGmD9NnIjhNkBTxAlgVzmc0sI4JY8K6T6D4j8O9EzD6AxydyUgZKTgAlpO8/cCRMAz14IM9FO1BsR7O'
        b'4BApdU4M2J6cNAm8Lcaw42Nd7UHjMLCXulE4hAZOuDqWKTRz2YeaDQvHwFV9WeHIuDFJ6fzMTHWN3yJaq40e2N4jNI+TmRmsmZrDNrt1aXHJuEZTp6JZjpENjyMJNKV0'
        b'ZQIYsYoblZmePTyR9YaxInJqchJ8E24FDRKGiVziBBt5HNpMq8GOqVrnGHAyHFUZF+zHxFdVoEl14es7PC2arJmsK6PyNozEoI+VOX9zrHzquyrC79eVO1dsLK33eqve'
        b'U5DAfXTm6Pp0TdnNX8SJUR85vuVe8MhtyvigmcN3nXt669zCTfFbNqpk0+589sHmc9/e1GULX79+pN/1rZf73U7QrEz0W31g3vvHyo9MCdya9Xl0Rbrz4M94R7JTr7xX'
        b's/BCtHzJumz3F73Ff62eK/6pcc6Z7tLDueNe/yhlYppfr42Pt4xvjDvUNPLT30brB0h+yUz6pO7W8PKHrn5nX3TZ/azb/rUP73z8cG1JzcuWB6k9v/pU5nv+U9nH+6fX'
        b'7CsdODW+eG1VxUtR7fKoFQ9GlUrKa6U5r990u/L6+bfVHjtPbb87MvmD9G83znyiBJLEZt20hOVPR57mZ7z2YVyG9ofjk4p/OT9jyMtNwUNhdfAp59Mbnt/u1m1a0e0f'
        b'ZBJPYiqB2RsjXjWTgQupDpgYFNYSmMKEeXZBcX3D8AyJfhfAs1ywAY0dByiM9U1wYUnQpODUhHgOw+/DAXU+cyn/5flBIXHBaESoMHVEOHIJtQs5rBiHESLBg0yZF46A'
        b'WoI0cPUHO+KsADcmg53iaDvHGfNJGnlwOziH7VZOgwMmpict02j2ZfDM0lb4BtwxDXs3dUsnhidwI1wDNpvaxhDrGlgJ6vg+DrCRoBVGwvMppigTWA62LeX2nQeqiAXO'
        b'WHjYCaWwAJN+m0A8KMCjnPXLta7IA/eshjijTLIwitxdCOrg9jgzcAds6ucCVvDGwnpwkMIlmieITMEdcHsPghGdQskxYU00vBBnCuxAfehtlyW88bAG7KFRNiTDfWB1'
        b'SMGYVmAHi+ooBdX0Tez3oTCJ15FcYjTRKQDLSC32heeFcbDaPcfUWySo6E9eUy6swxAVVP6tYIspXIfY78BzY0ksYe74tkZIqG2d9CVGSD0X27BbeYUbQkItQ2SVRW1l'
        b'lUI+S6zMRRKKG1dAbOLdWDArhlW4EWAFF30LTdgp3dg/8rln78O9K+gpRJICn4VcuLG29dzn9o7cf3PRn0DIUqoRmaEta5v1h7Dgb8NiSqClmLKMqW/Ps6FlphotFids'
        b'Ojkey/w5JG4anaXUYp3BzCFRhxE9Q8D5bhYEZhb0ZVxYWwg3DCKKYI/5qOfUgP1oWFgA3jIQku2FB+mkUv46WO4NjhJgIVMMd84hM2oW2O0QNBkTknHgTuz65iRYqTp0'
        b'bwBfi9Ecc0qejaweLuSOEZW/VGR//ix15sy0tG97XXLy3BFQ0XCzIbPPN/nDrp1KaHEf8d6HK0fUbOvq99HWr0sqCDHZ5/Fh2nu/pMcPGv32wd3lvf2igz24l95PHPtd'
        b'5N8KpA90MR/XRvU+srUFzNP88933iqv25BR4dMmfdfOFY9nD5kfex+smP/LO7vvrzYe7Zp36vPrSosTv1PCwquXW+0f6vb3UwWH/te4JJSFTlnhtr89Z98a8LxpGlHBK'
        b'L0VMaAqVuBJlB24ICyOVBw+AMywrGdwrpX5cV8JKHu5RrYxkGbCcu4RXQDp1L7BrKtyJSbZQDCPj2GGwiig8cBkSSJoJARdhHPPqauAcAxeG0nFjI6gbhqYHls8MNoOT'
        b'Bk4zJI8Q+FXAOFAaZ+Ak04A9LC0ZPADXktKPR6rtsXFdCTmZgZpsKThMcfuRaJQeasZNhr3tOqEphThjnh0ED8/D1GRGYjKAJn5Kl3aOCy7agzMm9GSUnAxs9yU3j4Xr'
        b'hxfDUkJQZmAnywenqc/rg7PAoThj+3P0hCfgMS5oHIA0QTLgbgKrZyK18STlKDPyk50Tk1pNgKf8DbDGYFhhmLX2FhH9c2EUbIgE1UEsHo3Qk0nm/SnsZIRBi4x1gW3H'
        b'uhJG2rd9gjI8TLQSlGkWMO2Dv4rNsvVF17TBbUenZcxXr6QkM2SMxg1zEAgFhFGPSIkSD0sQ2EKGMUWCdcB+8TRDHIoXKfO0FMplQTzm/ocU5A68ofMo6IMH8mkMYRqz'
        b'd+OICC+Yl+T38oyJ8Izzko9SES/wGM4yi42DK0Gl1ii92THOeeB4Dy6s8QFHJJxE1QT5BL62FxKNo657Rq8dng8wHvp6918Zuc/o0PJ33TVlRcOiqvx6XQ4J8vCIvhMo'
        b'TPBSfbcz8tj7k45/9NehL+VLS/9bvnXBhSlJ/e9/dfm3xqCNN7zv/Sfv/UtH812vi85s+a3o2prQIMdbK5RvDh/2/ZVpY8Iufh5ed73qu4cuB2MyN+05XOTy+ErZrfuS'
        b'VT2fbJQnLrzs3e3cV0u69L3064Nnj1+7Osq9/tjfT80Qn1lUsebCevXjHiv9s/o86ea9b/prceuFcQ4xs6WbmiY8WTMydpYo7+oXW59uD7r1ry2zbw32nvZfl3Z4530W'
        b'3ef7e3bPesxy8X8nauGzXyq/Vn0nvvrzxWH3N/a/43Ikxv/xX7655b0ob3f4/H67T7qdeOTp4Lud7/PZneZVMc6L+r581M17drbj07sSHhHP0EhwfhpcjSQWTgTjNwzz'
        b'b4NmOszskGcZ1oQmgZrAVpffmSIi1Xg4xhvWd5anGZd4DAs8oH5h20Uan/+dNtjpQEIXCGwHBKwqyMhQF8gUGRlk3MErn0wPLpfLGcTp/ZKLRhh7jgdX0EPs2SPQc7Rn'
        b'fy4nEo9EIwQ8F6d+Jcx8Lkdz3dj5eHpuRobJKk+P/wd1wNF8Yey7uKR48NHiN898E2WbC43wfVaA9TORTJ0K1qGJoHJyPKgE6xwYF29er1Fwr6r/is0c7ToU73LTmV6V'
        b'sUIQ5Wn38vvT8hR+/9JSuOHc2C7pRd+n9xt+++eCfZvdC+Z8l5o6pbKLsoeqoTLjwQevuY74til7evy3JdXPJwXJ9v71UHHji3gX/yrpmPS8HTuOuqWm3dYPCPlgkqiL'
        b'QGRXLVhhLw3u+bcvMlf3+ininxUuvfvvdC98r+vQf/wy4GfPW2N+nDA6YFSJICVAv/4uEirw3L+AR2d+TG43GS9dY0ZkJ3CUC9/y7U9iZMHm2LjJUngEaUP1sZMn48nb'
        b'HZ7DoPP6AUR7egNsxOb24BTSFFEdYIkea5GoDjx4vUfAt0jf6joTaROxCYEJDkjFgAfs+VxBP3/a6zaDC5gGNMSe4SQz3OlwN9zak6x1wibYWBw0yY7hxDExXrA2CSwn'
        b'87ZYCDbExcLlcCt2BLcmAUO0nSRcuD5BRKWhNQKIBsWUiNafhbFc0OKaQxlaN8C31XFIESon4yZVplxgFS8RiTMbyOQNy+BReJi4BQTbp9EdhTRXMhRIQsA2LJNiFELw'
        b'RFbeEnXhwuNaKVHlwLIpsBRgueAkOBlcyMYQAiRZHB8Hm0mVFcZ4oRhHRaBiwWyXeTp4bJ5ono7DdIPreGBNLqggCfnDHaAxDq4GJ7An1iBMH8igd7Odi3TsE3AZWVrm'
        b'IW33TVT360Li0IizFq8Z4zMHxmcB3OXHByuGwzNmXpZ7/d93Nsu+5/iK8cfKcNQKtSA4dGcBdTJEiAawXifijbKUivyoBEFGIF89T63M1/OxNa/erkhXqFbq+WqVtkjP'
        b'x8qTnl9QiH7maYs0ejvCUK/nZxUUqPU8VX6R3i4bDYToS4M3/zFrSaGuSM+T52r0vAKNQm+frVIXKdFJnqxQz1ukKtTbybRylUrPy1UWoygoeaFKa8CW6u0LdVlqlVzv'
        b'QOG3Wr2TNleVXZSh1GgKNHrnQplGq8xQaQuwfaLeWZcvz5Wp8pWKDGWxXO+YkaFVotJnZOjtqT2fift8Ln3bP+Ljf+HgIQ5u4+CfOLiHg5s4+AYHmBZV8x0O7uLgDg4e'
        b'4+AGDv6Bg29x8AgHt3CAt5s0P+Dgexx8jYMnOPgSB3/HgR4HT3HwDAcPzF6f0DjEPh9vc4glMV8IsrEJrzx3gN4tI4M9ZqejFz3Yc3GhTD5XlqNkIc0yhVKRKBEQ2RGz'
        b'2MrUapbFlkiXeiGqf02RFrOB6+3VBXKZWqsXTcXWhHnKaFz3mn8batHCLl8vGJFXoNCplRj2Tp+A74CGM8sGN9STgPD/B1VbDTQ='
    ))))
