
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
        b'eJzsvQdYVFfaOH7vncIAQxFRQUXH2Bhghl4EG1Y6KvYGA3OB0WHAKSjYFQUERAV7771iiT05J9/3JbtJdpNsdhOSbNpmEzWb3Ww22aybjb/3nDszzDAzxux/v+f5/Z/n'
        b'J3K5p7f3vO2877mfMt3+ieB3LPyaRsJDy8xlypi5rJbVcnXMXI4XHRJrRYdZY5BWzEvWM9WMqc88jpdqJevZdSzvxXPrWZbRSgsY73Kl1+OVPhPSp0+cqaio1Fr0vKKy'
        b'VGEu5xVTaszllQbFJJ3BzJeUK6o0JYs1Zbzax2d6uc5ky6vlS3UG3qQotRhKzLpKg0mhMWgVJXqNycSbfMyVihIjrzHzCqEBrcasUfDLSso1hjJeUarT8ya1T0l/h2EN'
        b'hN8w+PUlQ9PDo56pZ+u5elG9uF5SL633qpfVe9f71PvWy+v96v3rA+oD63vUB9X3rA+u71Xfu75PfUh9aH3f+n71/UvD6HTIVoY1MOuZlQNqvVeErWdmMSsGrGdYZlXY'
        b'qgEFDu9LGe86pSivxHGOOfjtC789SWfEdJ4LGKVvnl4G7/+zQsSQuEOFhpyJCyYxlqEQ6DERbcVNuDE/ZypuwC35StySOWOKSsqg63jL8IlifD8atylZSz/Ia8jLMGXm'
        b'4s24ORc3s4xPJrpVy6FLaC26ouQsfSAH3oDaLdmZUZkSBu3El8ViFh3ELfMsZILQLXRqAElT4UZSw1ncJmH88SZRHjpUDeVJnmS8bihqwpuiqqBPzVCLD+pAFzgOXR2P'
        b'zlkGk1q2rELnIcsVOWpYugR16C24Y4l8iYVl+uBWEWpejS5Ab4eQvrTiO0bU1BfvRK3R2aoI0m/cippQqxfTb4gYrdfgthK2G4D2s01eOVlJYR2Zn7eSpf2sq8g2ACCv'
        b'5GAVWbqKHF05dhVX4PC+lAB0t1UkHentsooDhVXsNUjKrJgFUKcoynnHsIChkddKRMy+af7wVhS1pmSwEPmXJTLm16kwaUVF8hEL5ELkGxYJ02wKgq1YFJUsXcacZvQ+'
        b'EF23JEQcwn8FEPHx8L9y12ODZkGCNyRIy3azl7wYRUyoYdnbcf2KegvRJwq+CWgPYMP/wtyf8tHs48a/M52MJRoSNAnoEqxdU/TU8HC8KTpDhTeh09PDs3Jxa5Q6U5WV'
        b'yzKGAG9YhROjAAJOuCyAr23cGcICOG8jhkx/qa99grlnmuBSd9tE6jLB8jwj6YElhADPITNaW4B24DXTVDM5hhMxeD/A+R5LD5K4L1xUwDG4AbUwg5nB4xdagknPcTM6'
        b'X7AE1U+D6suZiagdXaHZJ6JjcbgNaqgfw0Qz0T4jLUFkHfEudA63sQzebWFUjGplsNBwM2ycwwVoc3LuVNwiYbjlbH90Bx2wDIfEEXhDItkYkWn4djZAc2PO1HB0OiqD'
        b'blg1Pi1B6/AlfIK2mjB7POqAbXwTr2FGMiOj4nSxY3zEpp0ERnKGLHgt1h/FyDdo3svsrNv/+zWiSx0vSgIjZVLf0jNXjvvOGRD08Ea5IYsLmrZ75Io/73wDDV/1j7UP'
        b'P3jjwYr2rZM2n/vboVWn5QN145e2Dosbt23V8aCa4sRFHeYE06wVLYEjXkvzvZV1+U+/y/rT1Vfi3qv6ehQ3f8EP33LfPIj+rKN87+rUkG9n/+bI0Zfyfxsz5/tXvXxu'
        b'JG+ZlbT2G7lSYh4AvZsXRAbXEolbclVoT2UWQSZB+HkRrseb0WYzQW/9cvAWwFZtkVkq3JCZkydhfNFlDu8PWWSmmObmMLwzUq3shTdnRVJkI2EC8BpRJTqOTtIcZrwx'
        b'z5fMnEW1GO2MAEDlmB74lgidl6G7ZoIE0B68eSrM9XG0AW8CVNIMuHMEiy7jzRIl18mFK40EbpS+9M+/8SAg+Lj3yFJjZS1vAMJCSZYayA1fPbrTz8gbtLyx0MiXVBq1'
        b'JKtJAQ/Z6EBWxvrAT2/49Ycf8jcI/gaygZwPa5TaalaKOqVC4U6vwkKjxVBY2OlbWFii5zUGS1Vh4b/dbyVr9CLvEvIgzY0hnSPgr8BSjmOlLHmKWemP5GkhvcY3ymMj'
        b's3BLdqYKbYoGRLA5OotlZuEbQ9FlSeGsvk47k/wTW/9SHMwTJgEYBC07VwS/Yh0zVwJ/pVpurpfWv54pZbViraTOe66Mvku1XnWyud70Xab1hncfgR6XirQ+Wl8I+0IY'
        b'kAqE5Vo/CMu1bAGhpAGd0ml0xvLoDD74ETBTicihW2TIXjakkcLYCD1UJGAjUYMIsJEYsJGIYiMxxUCiVeICh3dP2Ejkgo3EArq/lyphAI1XeI0tyjkaG83oHg7xk5im'
        b'QErp0IGPil4t/qJom7ZB87Couewc/wWE574wH1/aErth6r7DO3q8lK85pdFLzrBnin4hvvft1qgw+cSIsGbf2WlrHoaETgtZ9+KuDglzZVCPuC8TlFIz4Wsi0DbUEWmn'
        b'l5FSJjA/AJ0Q1Q7A94WdcSxLT9N3zxGyiBh5lMgLt6Pt5lCy3pfQntJs3JQDnIRyzAIpI0ObuGXeaJ2Z4rcN4oiMxQSJZWei84CGU7hQYCFaaFExOoWeR6dWo6Z84BPE'
        b'jATvY/EtvElpJsyFMmdBpCoDEtB5LUwKvsqhunh0Qsk5gKfI3T6j0NopKyzUGXTmwkK6nwitDJwL+wZAVgw7SPykNkBYf7Utn7CTJJ1iE68v7RQTVrDTq5o3moBrNJK1'
        b'MRJKeJq1tUyqNPqRR4B9i8gJQrNtkcCTrlvEpdUSrttWsMNckhXmSjkrxHGU/okA4jgKcSIKZdwqUYHDO0BcWXeIYzxAnEUJ7+b0Il/cAiu0Gag4bh2FThZkCKs5dQol'
        b'hmPwYWkP1DRdV38uTGyKgSKvLz3+qIgAX3hJ1CdqTY7my6LAkvJSfXHBi+JNsaqir4pmvxzy6gu7/ZmD8TLzL2KUYrrc09HJaBugSP3xHQFS8J6B5udo6ja0Dm0YijsA'
        b'hbfiVrWqSiVg6r6rxGjDFLyL0gJg76572wEG3cJ7KNCg06vMZM6zAOefyM5XsahxBsNVs+lody9hYTm3UAJYsow368x8hRVQCJLzKZazcrY2yL5U9ixCVWK67J1ig6aC'
        b'74IMY6DQTJAdLihIEOJcYgMJ/4NuQMJNO/8rmMiF8fQIF1HwLkN7ljsCBoEK1IqOdIcMIMx1utpXCkSmOCh1/GaUe9D4sojbFGdJyI95J+ZYjDi+qpRhzr0pm7v5slJE'
        b'd7sWnxxhBw4CGYNDuGX6YjNl7U8BA3kad6CN6I5b4EB3Jwu46Bi+j1oAOpZUOyCUUNRkpZKesQXAgckVDsrkgCoc1sfkDAcSYZnJgndKqjV6iws0iBygIdgOEmS+y+1Y'
        b'Ys9TQcLepGdEkSqABGGd2VLxz0QWLuSJtVbvDBSSPMru4/2hY4hMNx03qFT4aJR6akbWDNyQXyDwpRnAoqpZYLfuekvxbtxhiSBlnkfN6Ep3UKJgNCzQAZC0lbqvLN+x'
        b'pjwoc6K076OihwBI+tKIP0ZpMjR6CkJVmobPzvOnNF8Ubc19vTiqJGpbuCZLc0YTWMK80tsomri7zyVzTJRWq83QyEo/epVhYmMD1o/MA06TkDq1iAMmUI0aCB/oyARW'
        b'WolVzlh0A2AwX9UFhdyy/ngPxU/o7owsB9yEWvycIPAkOkfhGK8vDCToaZa0CwDn4wu0/qiJ6Eikahw6lkFFZoGkzUMHlFaaIvbIOgpAKrVUEY7RTtB89DLKIMpZ7kkg'
        b'V+tnBRohlyOqEmiVHTZdNgJgrS5qRkG0FzwqbCAatN0NiDq35iLYOSMsKlfbERbbwD6TIOdCyMRuYVOUp3tBdZQzZUHEb578mK3JKPsSQOcXxeWlwZpTksshfWJUWgI6'
        b'TZoz/Dmee0VVdOHMHs38l2f/cj6ejqdgPZ7y8nsvzhb9pgclWuJeATPGDLESLbwFnUDNy5KdcBO3zJhrRTjocIT/c84MDBCyizQVbUX3i9F5vAM3RWXiFhDapAu5weie'
        b'r8Aa7YlG29GpRGfmqDTMPRg8DXkBz28yG62Ii4j3geYgAAofAI5a/y5MQrLQUqdFwkp7BgjgcrpggegmLHZ01eIGFro1ouTyjESwV/oRLoxQSZBHfAoLBZUcvMsLC5dY'
        b'NHohRcCfshKAorJKY02nzMpzmShf1Skt1fF6rYmyVpSYUvRJAZT2zIaKnyp6CQMhU1NABkLKyRgxJ2aFH39OLpNLAiXBMgtZt1l6vMfXJrnI5Ogk3sMVoTPoec+yi5rp'
        b'Jrtwc8VaEZFV9nFzJe2MVnoIZJXD7HoW5BhZAYFt707pRAMg95rHwRP4Yp25EqTA6GwjrxVeHwjsxAPSxOOgmbyx1lJmqtJYTCXlGj2viIckMqjH8hzeXGvmFZOMOpP5'
        b'NEcn/sF/w6C/3Q0Tm11pMFem5cFEK8LTtUbeZIJpNphrqhQzQAQ1GvjyCt6gTHMImMr4MniaNQat23IGjRnfMerViimwTJVQdmal0fAs+dxVtpjXGXhFuqFMU8wr05zS'
        b'0rItxtpivpbXlZQbLIaytIkzVDmkU/B3RoFZlQmSmzot3QATxqdNBxqpj05frNGqFZONGi1UxetNhHLqabsGU3WlEWqutbVhNKcVmI0afJBPm1JpMpdqSsrpi57XmWs1'
        b'5fq0fMhBm4OZN8HfWotDcVugeCnpHRHeFdaOQJRaMddigob1Dp1XxHpMiUvL5g2GWrUiu9IIdVdVQm2GWg1th7e2xysm4zt6s65MUV1pcIkr1pnSpvN6vhTSxvHAki4m'
        b'9YZbo5S2NMVkHmAHHys1m8goyZS65lZMzlGmTVTlanR6x1QhRpmWKcCJ2THNFqdMm6RZ5pgAQWVaAWxk6CTvmGCLU6aN0xgW26Yc5ogEnWeNxCwmMKzKs1RABRCVg48R'
        b'bcliMmvC9ENk5rj0PJLG88ZSQBfwWjArc9J01fhKWBvr5NO9oDOUA6yReqzTnqGxVJlVpB3AO8Vqa5vWd6d5dxdP5t5pEHEug4hzHUScu0HECYOI6xpEnOMg4twMIs7T'
        b'IOIcOhvnYRBxngcR7zKIeNdBxLsbRLwwiPiuQcQ7DiLezSDiPQ0i3qGz8R4GEe95EAkug0hwHUSCu0EkCINI6BpEguMgEtwMIsHTIBIcOpvgYRAJngeR6DKIRNdBJLob'
        b'RKIwiMSuQSQ6DiLRzSASPQ0i0aGziR4Gkeg0iK6NCPvJqONLNQJ+nGy04IOllcYKQMzZFoLqDHQMgI15EJ9sgSojIGTAfgZTlZEvKa8CfG2AeMDFZiNvJjkgvZjXGIth'
        b'oiA4QUeYBl4lkLt0i4kQlFpgHNJm4WPlRpg3k4k2QLCeQGP1ugqdWRFuJb3KtLkw3SRfMSQayki+SfiYXq8rAxplVugMiukaoIsOBQroGpCUKVSr61hZFxlXzYVeAMII'
        b'J8WdEqzlIWmoa4E4zwXi3BaIV4wzWsyQ7FqOpid4rjDBbYWJngsk0gK5GoEu0zkHvgT4Expn5peZ7S+Aieyv8Y5ZTfZswkKM44EclzlEDE2bqzPAapD1p+2QpFqIIqQX'
        b'sLRTMM45COhHYzIDtTPqSs0Eako15dB/yGTQaqAzhmIAW/uKm434WBkAUaZBq6tWKyYJ9MMxFOcUincKJTiFEp1CSU6hZKdQilNohHPrMc5B597EOncn1rk/sc4dik10'
        b'w6YowqdZZ9VkZTSUXYyRu0Qrr+QuycY+eUqzozI36fnuWyN8l7t4J1bM8xieku6JO/s5meM8t+zEpz1LNkCV7rI5kYAkFxKQ5EoCktyRgCSBBCR1YeMkRxKQ5IYEJHki'
        b'AUkOqD7JAwlI8kzHkl0Gkew6iGR3g0gWBpHcNYhkx0EkuxlEsqdBJDt0NtnDIJI9DyLFZRAproNIcTeIFGEQKV2DSHEcRIqbQaR4GkSKQ2dTPAwixfMgRrgMYoTrIEa4'
        b'G8QIYRAjugYxwnEQI9wMYoSnQYxw6OwID4MY4XkQgCBdZIUYN8JCjFtpIcYqLsQ4sCkxTgJDjDuJIcajyBDjKBvEeBIaYpzGY+3iJCNfoTXVAJapALxtqtRXAyeRVjBx'
        b'SrqKUiuzyciXAhE0EJrnNjrOfXS8++gE99GJ7qOT3Ecnu49OcR89wsNwYghCX2zAd6pKzbxJkT8lv8DKwBFibqriQR4WmMkuYu4QayPfDlGT+WJ8h1D6bmxDmRBv5Rps'
        b'oTinUHzaFKtyxaGwi9ol1jUqzjUKxBw9EYo1ZsKXKgosUJ2mggcyqjFbTIStFUajqNAYLEBeFGW8AKZADt2pAZQORXSEuOu0tNhPZnZTvxui5L5u14xUxdQ1OwpgvhVW'
        b'lpdOZSlJt06y8B7n8E5kwi5N1WM2Le+0zEjUbUZyrmckZ83CaQnR1RuJ2UanxFSl15mNA+xqvEBnhR4xxltp00wKCj1OxLHSf3ESjpPGyl6j6jx8Gu3kTcTEpDEKnRYz'
        b'sqTZQdyqSejcf1CdV6f07vRJLymptBjMID50+o+DNRfEDk0Vr3/QS1DmEa34474TAAoqgLUgKlOFIPgADOsA80AWoo/tFBMWyDgMXr+9AxEzKgSOprLcwCsKKvX66AxA'
        b'SQZVdi1RsHQFu5Bc2qzsuQqhGFGkEfRp0pksQgRJcwwLm24y0fsJDL7Q0LgZqoKScj2+A4uvB6bEMZg2jtfzZVoyEOHVqnXpeo+zCkhptpmgDD/hCHnr3rZJbQqBK7LK'
        b'fl1aKqvUR3l1Iu9BZthdZioXWGugzel1kIG+6QyllQqVIt1otnXFGpNpICW7RZJsce6yxblki3eXLd4lW4K7bAku2RLdZUt0yZbkLluSS7Zkd9mSXbKluMsGTEZ+wfRY'
        b'iMgWFoYwuzyNjHOJhIAilweEaVPFKixqRZcqFiIFWLbpRtUKwrDbxG5B59q1jIqcyJy0SRbDYmqVyxvLAEPVEqxC4sfNUCSMEOhsqS0L0Qm7i7fCjZDkpsK0uVQeIAM3'
        b'VmhIoh1E3KXYQcVTsbinFXOfKIDQU4q5TxRA6inF3CcKIPaUYu4TBZB7SjH3iQIIPqWY+0QBJJ9SzH0iKTbiacXcJ9LljnnqertPpQWfDiieISX2qaDiIZUWfCqweEil'
        b'BZ8KLh5SacGnAoyHVFrwqSDjIZUWfCrQeEilBZ8KNh5SacGnAo6HVLrjnwo5kFpgxndKFgPpWgrE10w506W8zsSnTQIS34X9AB1qDHoNUS6aFmnKjVBrGQ85DDzhirq0'
        b'jVbKSRBeuqWU6MXsSM5GSyGJYN4ugqwITzfUChwxOdADZJyrMwNp5LXAgWjM3ZK74WHXwl2YvHuaUY+vm6xsglNKBj3eKTUDV2KXqyglUVF+x60QYB2plZoD6QdKQ3jo'
        b'Uso9VxACb+Z1MC1mu6I4E1hds65Ut1jjiP3nUjnQrkB2ZDME6dHhINGRTZrEC6IFrysmSTmwauRkzCRwNp4ZNUflMPQbWtboLRWL+XKbJpsSQcrFESO7PGOEJx6W2Frd'
        b'8cjDhso+o54S+BbelWLKycObo3FLjRc1c872YnoVi+V9jC58rNzGx5pZZz62Xdru2+6r5dp7tvcU+NkWL2+pt482ql5S71ffs1Sk9dXK67yBrxXzEq2f1r+O0QZoA1u4'
        b'uVII96DhIBr2gnBPGg6mYRmEe9Fwbxr2hnAfGg6hYR8Ih9JwXxr2hXA/Gu5Pw3LSg1JOG6YdUCeb60d72rPbj7d2YIuPt8xbplXVc9Yei7UK7SDaY39hdO0+7WwpGaEX'
        b'fdpKPtfiDeXU1HZOQl06AqG0l3awdggtHaCNhjRJvYw6fATRtKHaYXXecwMhtgf0bLg2HHrWA1rpqVW22HwV/OsDSiXaCG1knQxqCbJKAzGdsgnEuHt8wczH0T4Kh3+2'
        b'aIWASgRXJKccpyVGYnBkJKZvD6iNNzG9ekCtNYhIoJQ/INY2D6jdMrG16cpuTLZlNxK7G2MsyULMHh5QswACF0qvTh+Nthqwk7FQp+30LgEcYTCTV3+NIL8U6oHJM5d3'
        b'ykossH0MJTWdMmKrqtPorSYZvqU64OsKK2DrltO2O0UTZ0wTbD6MI+BRInMARh/rLzXamcR085jyrpfW+9R7lfpYbYNkDbL1zErvWu8VMmob5E3tgWSrvAsc3gW7tW/b'
        b'YPBOM0f+ZQpd1dXyJuolZp9vHTVqKOHVLkVcIlJB9NBUKLqmKdXqHwbohaiCrA5o1vnSGMwuNZB/4eMAK5htOEmpVqST8oA/ShTUWFBhqVIAFk1WaHVlOrPJtV/WbthX'
        b'yH0vhGT3PbAfePxEHxJ/qg/OoJGqyKF/SRcmR+fYUq0dM7nvC6E5BNsDrVArppcD/ocdwCtMlmI9ry2D8TxTLYI1iSCoQk0KDVQBYaH/Cn0l0CKjWpFpVlRYQFwp5t3W'
        b'orEOvpg3L+XJga8iXMuXaix6s5K6B6Z4XgvrlkhVjLe+KUqIxjDcfs7ooGlUeqrFtp1SbdBqsi8m8UasNCrCBauVxfiOsRaEb08VWU2lUqmkRbgSqEaAESt2CefL1IrE'
        b'2JgoRXJsjMdqHPZzqmISCShogFRXqjPAroE+Kmp4DXQswsAvJYee1UnqBHVshNJ1qp7BxlgueDuIinswCoaJmVdbJI+cF85YiHuJEm3CV3BTLjo3BTdk4pbsaNw4hdiY'
        b'ZuQocVNUngrSW3OmZqDzGXm5uTJ8LDOXZfBWdEheidrxKVpxtJ8fE8IwgW9MKcqZbTQzljSITPatclst3owbc3BLJGqEeifhNlvVtN66GjmTOZhWWjbZmwHirThmKJJH'
        b'1M5kqNvhhHETqYuW1T8rQ60aMDKCuL+gC2Imab7UhO/x1M+MVlE024sQ5/K90UX6nb0mMZbREKn2RxvddQw34Ga0Ce2CQZMONitnOnQM3TT6oite+Ipuf9I1zrQK6nmh'
        b'oF/Yq7/0XhMTOPGNnFVtX7zuH5V+SZR9iUl+91S/HpFT+hRsrH5oko38x1Hp60O3bRg+uG5o47Y69Z1xZz/ci3svfyOz+HDe22dSy32/PfPV1xfTe0z5S9BHGstyr9aH'
        b'mke+Y6b2++3GN4b8EHvolc4fdrxU8s0PH243LHi1/K//YktWhf/zyWilnLqL+E+chJq6/C9Fk4qZgKGiUrQXbzArCCNzqGARasrPQetnOKwmy/TF68W1HD5H/bXwrir8'
        b'vC9MqTLXZqnbCx0pRvViWbaOeo2FoE0LoBqnpWOZ3sO9Bol9xwaaibqtEO+ZgE9lRKrCM1QcI0V7ONWKMbT6sQt9oKxaNRvX2ZcqCF0Q4Sa0K5habg4F/uomOoTORaqV'
        b'eBOwaFJ0josvQ3eEMeyOVaEm4iUGJRrwDuvySJmgahG6K+1lDodMknG4gQxUYNloD62Ly+Db6BwTgzdI1X3xcWrhjjZ4x5LhNEVFqElO3IJbgcdj0CW0k1GYJH74WABt'
        b'Gh3BLbUkZ0sk3jQQN5KmVdAw2inCG3C7v3kQgf5qvJs0PQHttLZuZRf7oufFqCnYahvs82/6sXW5ulCDU9J/ZrV0hZQl7mrCk7iryajLGsRwUoj1YWt72EhxN5cbH8HW'
        b'lOx941jySCePceQxnrG510xgnm7BLBNKdVUyzl6KVuLGUecBYzUFZdYO2OXGqtW1v05Wzqz1l1qUkp6tYBZBADgTNk/JdvoWdrEPxhD73Dk4KI3UayqKtZrRPaCWbwQf'
        b'VYc2bamPrQjdWpuN+IcDodCqKg36GuVptlOkrSz5OZ3zKbQzFe76ZiTeuMFQ3pgJL48HCj0QirjpwDO1XCe0HFDozEp4bL6PvXnlU5mNn90R6xR4F9pouccu9LV3IXSc'
        b'xsTbif/PbrLc1qSdj/bUZJi9ycEeWYN/b7yyQpsvm6e2FV1te2Qn/r225YWOEoOn9gd3rfhP8CAeeuHkd0Dd57h6xu4+96xeBy4eMbaqXbwO3mjaKaKeusuqyx8VeX9F'
        b'/J7KS79k3mh+rfkT+YvyfaHM6KPi94B/4wS6UY8v9rcib4K50Z3ULuSNjocJfibnJEsc6AZuTB3kgLvxerThaf5sXoVkXzn4MDGrmdXBw2sDHXAZzSCU6dO9phD7isyB'
        b'xzCYXROJYtYya/073eBIl3qVPp1e1h0qGPZLTWYjz5s7ZVWVJjPhlTvFJTpzTaeXkKemU1qtoeKnbwlw7JUVglgqMmvKOiWVAPfGEl+HdSBo3N+2FsRTqN7XLk762e8O'
        b'8Beubij1ty69b4Mcll4OS+9Ll15Ol9t3lbzA4d0qVH4gcSNUpmu1JpAaCOur5YvJLoT/JVbDOAVPzfifQa6kUg8VWTSKcksZ7yDJweyYdCAJKQR3ByKUmXizWpEPUO5S'
        b'D0EHFeQ4RldRVWkkAqitWInGAFINKQoSkZEvMetrFMU1pIBLJZpqjU6vIU1SIYCYVZrUZKQ6oliDvWat0ipIkTpd6oCqLSadoYz2yF6NIoIuXMQzzMgk62jLiSbEte8u'
        b'+cPNGmMZtKG14SVSXkFUhSYilJiWWMjsFhs1JYt5s0mZ+uyyvgCzqYp0J/KimEcPRxd4KkZaTlVQ14Z5P+ng4LEWYYukKgroX8U8q7mdx/y2rZSqIIpOWCoqg85zNLfz'
        b'WJZsPpBe4amYl280e84nbE/IKrzQNqIUmQX5qvjYpCTFPKLc9Fha2NMgl6ZPV2VOUMyznhguiJzn6L7hufEuVEAkbSGgIBU5Gg17LA7IAyazHLYGbFdTiVFXZbZSMwKn'
        b'xLOb7q10vakS4JfXulUSADiR3IT26OlVQHSx1YoJgqaAbtHnCsyaigriAGd4zqPOgG4GACzoQJV1a2l19DIiDUzrUh3QOH4ZrLh1w7nWQ/7lVZp5YZvQzc+byyu1gEnK'
        b'LBUAaNAXzWLYgLBpeJidEl5RCcTebT3CkMimoSoQkzBMncmhS2rFJEBqNoTkthbHbUcUJgDq5KqlEj0MWLhlycS7L1lkvWipsoT2XDhLGVluNleZUqOjly5dKlyKodby'
        b'0VqDnl9WWREt8J3RmqqqaB0s/jJ1ublCPzjaVkV0bExMfFxcbPSE2JSY2ISEmISU+ITYmMTk+BGjiwp/Qj1BqKCrR2FQnoXIUWgtutzDhI/PzFFmqdR5xIcvEp0GaXBI'
        b'gaQc3cGt9OYVdHkqSLSF8fAay8Si9QlU0v97GLnIgVHEVFtWzgssYyxELzpAgq9m2yj7VNxALj3JUk0jTrDT8DHUGk7cS2eB3A9/gOQTR0JvvB2fjqV3xYzE12twB4i8'
        b'RDT0YiR4d80YTs4EWIhSGB/GrUNxh5pcvEFcbaFqcqMK3oZPcMxAdFyMb6HW/lTfgNahQ9G4A8Tr3Bl4S5Xz4Kbghjwo2pw9owoe+VHzcrLwdjGDN6F1vtDFZp2FeuEf'
        b'jyn0VSuz0B10kMHNPox3FocP4n14rYUIVAkJxbgjE8qzzGDULkI7WbRGJKHXgxRxJl/cEK3GjdBgFDqdBUJ0gyiNZRSTJWJ0Jt9CVgJvmt4Pd0RHJOMtLMNlsEkzl9NJ'
        b'DcyVEvVJYEz1SytHzOkr3N0zOHCyyQ9m6VrVXKFJ2Xxucj+03UK4KeCr9peQZD8/Nd6Kr+Xgy5EwJzclIqZPjQidi66wEHUCuoKer/VVQ3mYtEwyF/lqEdML3xQHLMcX'
        b'dI+P/sCadhNmKvsXqtdzfVBMoOSj5MzHH56JPJ7954/DxHfRoUP9vC2/M0Sh/kfvno5WdHy/7OPYnut7zRwVc9t78PTa8N83pFmU+4t2vz0svl41dfUL8S99+lHCri9j'
        b'fzk5551X35EnnByhKh+f/VA3MXvuW1dvHl4wct7JX3/36LH5dnZlZ8SPNfj9e+pb+9+suF839au9TbM/2NYye+L3v4o8815AwIGIxuVZSim9HaFwfFo03umkgKHql5AZ'
        b'ZnL7F9rl42WDv6X+TjoJJjJeglvxPdxK9SvD8F2LowIG7TQTHUy9WIYu4z2Um1WijeionZvt76SJQIdxC1W1DEWbkiLzVJmZudlRuEWJTuJ6lumN74jj8JFCwQ22dRk+'
        b'mx0VngEdwWd9YfnQWa4mO9/png//f/feHY8+sz4arbZQYNworzzMyivLM+SsjO3Nkqfjj5hcugN/Q9jannaet6sOgSf3E9QMcxmbKRu5C8Q4nzwWkMdC8igkjyLy0JBH'
        b'MeOk2HDv/Osr1NlVSZG9iWJ7E372FjX2digrryVVOLLyw37nhpV3Nyyld6dcSyz8rOxRp5/A9NqCUk0F/UtuS+E7va3HuiV8py9hUYAxJEZfQk/sgy3xccC/RA8TaMO/'
        b'0wg/7+PE0fsDTx9g5eoDCVdfGmjl6X0oT+8LPL0P5el9KR/vs8q3wOFdcCL/ttXr6Ty9xm64pxCuUXoGznUi8XkQciuAfMKcAVMKLIHG8SpBwjZEKcqMlZYqSAVuWeNK'
        b'jiorinUGjY1BiQDeJYJSVoGwEsHfbuRJOmiXhV1qIrLx/xNC/v8shDhutVSyUEKMXeX1E8KI094UygtRtgrccmTzfsLw02Nzwt4X2rFud2ucwNQaKokKx0jZVoN7ZnRp'
        b'JeEadRUavQe2d95TTF9BmHBv/OqxxwRLCf0trqxcTPpLYtSKXCt0aWhYUVm8CBYeRHz3h4cGIgSlJMXEWrViBBBAgiPVzesyi/XYCTuSTFXMMFk0ej3dGQA41ZW6Evtu'
        b'nOdgVftUOdCKZJ2XgfrbzXO0vP1JSY0U7yatOdl3/l8gbI3jl/JlVuuc/ydw/V8gcMUnxcSlpMTExyfEJ8YnJSXGuhW4yL+nS2ESt1KYQjgkXlYgZmTTr0qZsUV6A3D8'
        b'lgTCyd6cg69kZ+biTVGZdoEqNoRKUt2kqNXorncCuom3UWeAzESzgwy1IAGkKE6O1uBTFmIwg+8txxuy1Vm5wNF21UtqRZvR2u41oybc5I1OylCHhRw+haP1gDLzc/Ot'
        b'Vx2RJmbRmytbcQPIUz4ghaCT+VArRN0smI/2oT3oqDeDzuIdvnn48nRBFNk1F100ZeGWzNz8bHJJEqobEiNmQsaJcHN/LwtxecAtNeiMKSLXR4E3hxP+XZ2JzoezzMAy'
        b'iQStn0LlLHQaHyn2xTfQ5mky3KLKA1GLA+Z8A+qIF6HDK4ZSoRFdTGdgNmyn1yvRuqn0wr1r08gNo7GoSbIMXykUZOGt6Mgsa7cyo5TkrtJgvB+kzqMifBvV4Ut0rf7m'
        b'L2LEE970IpeO/pOrYCzkxK13Fd7mK2WYnEXTmek+gy1EM4/r0fOjfckkwVxuxTcyQMxswW34GhE+m9BZCOXgzSATiJj5eBvaECqbjE5l05tUUYcKncAd8JYSmMlkjseb'
        b'aHQIWt+XyOCp6CYRwy+gO1SURA3oIjRATIUm5UQz0aPwUf33T548+WUiQFVOpIRcjDufHy4cz3tLQL4UF4oYRZH+rYAAxjIWIhfPmEKmp8Uqs2dEzSQ3J0dnzQBoyMDN'
        b'BeFKgIkM+0XJSnSdzp4+QmrwW4B2rBR8UA6o0K4CvD0+S8Sw+OBwfI7B52D5j1lGURkI75vqa12maV0gI7NNUB+8y2GO0AW8Tcyg+hnec9AWjYU4q+BGtBbvFORgIgVP'
        b'DcfbC2SOMq+IGdNLGtffH19C6ygUTVw03pSlys+NJhCUR4VeEaMcm4x3SdBV00x6BbQGtaOrkcJVOEop44vuc+ga9K8jJpjeC1xqzuNekjLLqlbre743+4PyHMGiAR0f'
        b'hHfgDqt6QzCyAADDjdH5uVPDrdU5WjPg/Yl4Lzoph6qPRNIJQzfm4OOR6syoCEi9im5KUSsXjW/ivRZytl8zFl3OJgJjG1rLMpyRTcnC7UoRvZQaZMyb1daSqKUPLYhu'
        b'T6KX9qajuyZa7hpqFMrFLrEQfyN0ysvoPE58AO2GvXEAH9bl1o8Tm1JAgHpFHrZgy6g8Ubp8w59CK5P25mZ8n33lh/fXDD52YtKREx1js4bU7WhYdEITnvOiJDDjFdUX'
        b'pz/OufOaYWL8n9/95vt//q3mvyf99sbH27Y1aW+2RGXvCwmbeeCNrIfvdp7u0Gc1Hnz3ytiHfSrefJK9UKH84+1jk+PGX6n77pCo3D9MvXfv6Pm/emnSK2/vnLlryKpe'
        b'bf8TGeNzaerS/um1a66+ZZz4bYv/1Nbe5uhbv0s9tuCTli+W/XKrJej7xoflNR/lnmhTPVol2Tbgow09/oZ/vfV3o0pGxf1ueuOLqdLF8++/G7LKJ/qXI1P3vbbK59VV'
        b'AXk1eV/8adSKh+duBnz128kDRwaJcv5VkfD9piNF975YkXxzLv/t7279pu2rMUdO9lr79w9qf+BvmcpmdPzXwd8enVc8xji59sePB9eqlqerlq4fpd+d+WDPpp1jgvSG'
        b'0vSHSj/BrOOMDwC9s3JCHD9UVIpv4xaqoMD3ysKy3ZlMMJHP4UtEQ5GEtguX/p7He0u6m4jcHUY0FPmrqQ1HWVFutlplN/AIYND9mSI9vulDU8vxKVVkhNW6w3sFaprD'
        b'oeOA5NYL93rtTcP3I9UE00exTFovKdrMqfBafN1M1VNXDdOzcyIU+LyU4RawyahlBVVlJOOzAKpnc3KjOEYMG6A9m0VXotFGqppBJ9EdP6ALVssOpic+IV3BDe8NdQ6m'
        b'KKAGn6cmIKU13YxAqAGIEu+hth1xKYA1HI8HcXPUbPvxIGpdRNU3k6ZNNJHdpSIUi050D7wOH8RbROjSnNnCRZoXlzNWtQvLAInADUTvgg6gPU+5TEsZ+B9SxLhTyfgT'
        b'vUOXKE7VMjMJe7CaKmY4QSnTpZrxoTecialahoRknD87AFKDIY6YnZB8gTQXySHnfGhJbg15C2Jr+zjpO7raFVQ5ckGdwpNHKXmUkQe5tdGoI49FdhWLOy2O17Pcrewj'
        b'1Flqr5i317TI3o6fvYkufQ757MBcR31OxAk3+hxP4yuROHBe5Ljc+Q52Sb1XPUPPT9l6H6qF8a0X2+9glzRI1zMrpbXeKyRU6yKlmhbJKmmBw7u7q/tIQ653sPsLLF7r'
        b'ImAbqlJh4ov0uF8NM124CzlLwsjEVYREyzfMsgjaXrSRwRtMqEW2BB/De0WMyJ9NwZfwQcrPyFPxuQLUMh23zMidiq9Nwddm+CXFxDBMGDqN7vYRkU8XoCuCQf25SREF'
        b'uGV6InAiR2LwpgTgsWRLWHwI7QeiTEnCRbQRtuRltMZWJctIIljYfruDKGuxGu9SkjvXGXQuayQzEu1AFyhxwjsMwG4excc5Bu9ZzgxjQiLRZkqaZhfMAkLdmq2OSYhL'
        b'5BjpKhb225GVlNSibXp/1Ibvdr/kfBVu0p3LeI41fQmZ/vvquxWt6Vni2MCJZ7flpT6YOjl9QsBHuSPXXlgwJ+XXgzeJ1HW/+O/qqe/dSzcyfy4fOqq5Qf3XR59//nWm'
        b'd2n4lrGpS+pmKWJ2f3CzrkfPM3u0Lw/5Z/+QRUfm9szY0fK3ox+gr/Zs/XLokPcZ/68s8YvmXrO0fPXRDy9++zBqvP8ffPJSBr/456N+lx9Myfzr/LsrE/pM0X17NvTd'
        b'eyMbth9S/evNI6+0Dfvj8K2H35j8pz+16Pf++eol3Zgx7Sk//rP+yeuqYwbRK5d/OfyTm3svKcbdnfryo39Vnzx+/BPDR6OHffjOy6s0hffD/5j46Pf/aJbO7WXy+vqb'
        b'fg+Ti46OOasMEi7UrFuE1tFPDHgxXJ8IdISdgS+gVopwURu6VUQRLq7HZwHpEoSLdmcJOPxeP+Dr7Qh3NL7OEIQ7USKYWaxBhyfYTO6WsS74NlxEESkw0AeIHR/QrDDU'
        b'6KRTD8NXKSKdVqnLJscnNwJycWs0OiNm/NE9UaEMXaPdeI4w+7iJnLagBpOEEQ9g0RGoRbg9G13Ca8v0AyMdSCK5XTu9gN5YOgpvTY5UK7PwHXzb6WZ7fF1CrS3TxeOz'
        b'c5zsKHXa3ui8uN+yJDPh8Qry8fVsJyPJAYTxCVokQufE6ISZnhxtwzvmUKI7DjW70l1CdMfiDkp0k4AhIlPaDC0ORQ02s8eAAaKFFcF0MqrRjihCddHGkXbCC1QX7c+k'
        b'yStx/XJ8AtV3ER5KdDagNjobkwPQHqieXsA/RW+7gv8COiRQ0ItoCxuONne7ihPv96VzgW/MGQs9u0f5u8355IJVtIWrxPfwkWfDx/+fLve3md8IV/lT2nXMTrtk0f4E'
        b'O1MMTe4fJ3SLIz9PxBz3o0zE/Usm5n6QSbh/yqXcY86L+wcn477nvLm/cz7cd2Jf7luxnPtboB/3jdif+2tgAPd1YCD3F64H92dxEPeVtCf3J2kw96W0F/dI1pt7yPXh'
        b'HnAh3BdcKPc515f7I9eP+4zrz/2BC+M+5QZwn3ADpR+LB/lzvaGRQEIJHYx4hO4LJNCri/h0egmablOnxGTWGM2dIsj3c+mdxFhF3g12slZpp22UrJH7Zs8TstbXStaY'
        b'tYo3n25zJHT3f8EIDOjX489clBaCo5fZ5lliVf7qrToZI2+2GA00rUKhIWcLDiqeZ9LLKxbzNSaop8rIm4ippaA7sirDTPYDAasiyZ0+vftZgV7QwJHuFNeYeTe6Licq'
        b'LXWcPAdrfXqRcxi+iHYb8BnUhHegVtQIW3MbujILMO5ldHYqapCADL5GtDwIKCw50qmZv5x88ocZnKBm1CNQC1UjmNGlakq9UdMs1Jinwjuy1WoRE4waRUCiT+IjlPK/'
        b'mwh7X5EkJWoE3jxdsLRXZy2wlcSn0U2V9Dm8vRjdBTbgSBwTkShJwc096ekzvo+3zbMKgF4rBPnvziQqVabiur6O1HwuugwEfRi+QQuGA8NPsAcLKOo8lQ4B8dZRyt0P'
        b'0OvdAqHYaLyJQy1sf9RWo/vF5AkS03rIUBk8KvfVQf5obOCGj/9eWq28yxwbgMO2vM/4Gqa9mfpD88VP5Le9vfjxMz9a9c1qX67frOCZ879O+f3QkCuHG954aU7ib37z'
        b'7Zpft0zcr57R/0KfOxurT6w68N7u55ZfSRhU/o8P/6K/7T30vSnv1j55dNn41Ved7+/2Hbn6+9Lf5W/u9983t33eR/3F0M2bWpVSKiGQDzIAE9OEto61Wxo6nMxuMwjH'
        b'rpfQzlj7vcSz8R56NXGr2UwmQoyu4ucj1bkc6ohgOHSKBYSKGoXPQRzBu/FtIIjCJz44xhefG8tz+FBGX8GS/Rq0/LxdQtmxvLv1OdqmoqQJiOI21ECp2zW0xZm6bcc3'
        b'ldKfwCYe7B81pkKy6ygCfs6OgMX6IBGxRQ9ig0QE9crpj/RfIRIx54BPrIV/0jbSCI8/OGMq/71PxVTWmk+zneIqjbnc82XuoxnrddnkzJN8/UFqv9Bd/Kxff/hYxLo5'
        b'7+xCXgSPmDTV5E2vd0Rjz+4aRwaRqsgsVUSQtwgF4GGToFknCIpfRrxviaI5Ql2rq4qIog1ZMaXRvZ7aRK4Y1Nq14xpjSbmumlcr8okyf6nOxNuxIa2DDoBm1yhKK/VA'
        b'BX4CtZGF83ZBbTIBtWX0QPWRGVHE8WYD3p8BXE1Wbg46PT0DnccNUWpgNTLwRq+qmeikoG07ge9XZ8POysrFdbhdjRuB75sOjF5T9FTga1Th5JqZbHzdC+3AN6Ip5glc'
        b'jHbhcyCEt6GzVOcg0rPA1x6LpnopdBDdEEcCECxDe9EdZhmIIZupcZF3yZzIfI5hp+Ej/UCaKMjTfbdmjMh0A5KyL/calRvrw6XLc64sr11a+91vv1sXfenylUuXA9Nv'
        b'S9InpORferfi/WH7C1/+8Tdf+sSJt+1+Vb43UnYl9/vyg3+I+aTfCNOJKlNS8eq9Z6b/JuuMmH3nF+Frm/dPtby25+Oo8QnsqIz9RaLPv5uwdt3X4S3DK4MG/S37bqdY'
        b'5v/dlD3DRqx+Z9FbCZWy1U8++bws4uDXq8Pm5TfO7/XgLcmj868mFDwJ2MP3ekPx/qNe8hs7r4RO3r9q5949v+zzmjSl1+J8ZQBFMcWAJBqNeAOdddgDySy6wMVSrhc4'
        b'7hN4P+AmtG58nvXDcDLcxK0cgi/TDKv7o83AiV5dqkJnlgm6H290kkNH8YEKKjP0H4wuEK+p7bPyYJFA0Mrj+uMTOQIXuSu4J/kCXpRaVJBJU33xJQ7fSY+hLOgAHu3K'
        b'jkKb8xfLhI8Z+I7l8C50qFQQRnYuTyOFOXw7Op94Fa3iIvBhP1qxaSw+SaiHUo1b6ZgCYnoPEJXF4YN0wD0CoqFLq9C1rpvg8fo4YcB1crQ2MpqcZajUSg6Q4MG5eSK0'
        b'AabhKu2UCdXjtZSPR1sA1kA2lI7k+szBlwRVWAM6hPdnA6i2AAgK4OodzKHDwNmvF+SktavQdSIKLRpmnZBxXEgCukcrL15S2R9yNjl/92o92iFIUTej8Z3IaLS3knQP'
        b'GkanuCgg1euepiX6CdztgK/FZBtTZB1lR9bMark30fPIqAuRnA2kT6K1CaTan/5PuDXiJ7V+duRK6hAutrd+7sDMOGljPPf0NCfk7brsvhoeTwhq729H7cza3k/cfQDB'
        b'qX2l1Wl7IkO8/e2e0IBgrP+UEuEPB789u917Rcz2tZUlhYXUL6lTVmWsrOKN5ppn8YkidvrUwoeqhSgTTekTHYnAyAf/x5V2T11UIzmg+5SxftGLXGngIwap5wkHsxf8'
        b'hBsqBQIMcyj6eX/9xXKRj7WW3k/k0YHkXdT/Sd+p/smyfn1ZapdoQevxLRP56KTJ31/E+IWtRnc5fDgcrxW+TVaXGOKLTpkJUvElJzZTxqOb5LCmf5wYduPA/4WPMbl8'
        b's9NWtTMd8sqjh1jB+MpM4kMziMFt+MygbHSQDisTn0KHstXoUgzaj+8mQgX4OrsEwXanmqpodBPfj8yCDXzKWXckwe20/Ipp6BhuyowiTFZ8P3xWDKJxE5e1BDXrZppe'
        b'lJgI0H7wOOBR0fwXLm053Ba7YQlb4vUpd2KD3Dc0LT3qj8Engv+4IacoKdvHd3b74YwL62M3HF4/9s7h7Znb2CE9X31ht5Qpl/QYqZiklFB8k4rP8dRzEm1daXOexJdx'
        b'nSCnX8WX59vQTTrwe1aMcx0dEDDOYdTsK+jee6GGKJahyvelUJqkrliMt9ok/Hi81yrkT0WXKZINHFZBDoUhDTDaUUhcwPEBeU9zmJGDrAUsDV9IjCQoIurtgIhkQ/w5'
        b'8iENMaAdMWtcbt9S4k4xKdAptXqxuXwFilxLZ1xh3xKk5CCuG1rx/8DNN/QIbzwJX8fbIsOzVBlRWaglOhNt9aIHvAq8QxI8NNoFngKtf01EhWq/72MkuekCAJbTiuq8'
        b'54p4Mf10HkM+mtfCzZVAWEbD3jQshbAPDfvSsBeE5TTsR8MyCPvTcAANe0M4kIZ70LAPtOYFrQVpe5LP7mlHwWZhtb20vaFtuTWtjzaE3O2hHU3T+mr7QZo/CQGvS/x1'
        b'xNr+2jCIC9COgTgxlBioVZAbONp92rl2UamoXdwuIT/a0FIO4shfkf2vECs8xUIOh6e4+7t20L4AHaN9rl3SxmoHt/vAc4itLngfKuSFt2H2t+H2t3CtEp4R9nCk/S3K'
        b'/qayv6ntb9H2txj7W6z9Lc7+Fm97cxyDNmEfd5zVJu7j5vbgg/ge2qRQ5lDPw8x6loaSbSGaI5jaUAoeUTKYWy9tinYEzH4val3pRedbok3VpkFcb20o/STJ2E7vQqBq'
        b'mknAZVOndZezAmc5RbDTlNIPLErtJwSSZzoheMavkfkIJwSfyqk5fWD85CL9F2lFwnH9nfJmJoRlyoNmF/l/kDhPiMwYu5L9nmNmx8Rqln84KI+xkC/WoTv4epyTn77j'
        b'AVp2DrCcrbjJiykokwWC9LmF1pRVMJgBEhv+UFb0XKRff+ZzWy+/IQ+duaQXayKnNY/b8sKaX/RbEyMX7U84fonN+GAT+/2Ev3xxMYbtNe2dPe2/2q+akxT3btGLxY8a'
        b'Rx5+I+Az3/XTXhxx+2bGa19NGfdan7MJt1756FHRuV9//5c395aX/TDii49y9mz+MTViZs4/vdpUobLOT5XeAht3dXIxuozuCZ8bUokY2XTOPB5foagPtaxE60G8vlgx'
        b'iR5ASodzPaSTBAZxvzmZHpXiuzqH09J6sWw1bqRS+4Q+od0OFbOFCRkaik+gbZJy1OhFjb5Xgfx/X/B9jxwiD1cJWSFjn/7ikYvRNuEs8xY+jS8JvQQiRRTrzeQEcu1U'
        b'vFeEDgON3k518An4ANrYlS0XnQM2GR9Hp/B2EToK7PwVQeXQiO/ji3Ea1BQNzG8m+Ra1jKhg6hbHm8nlSl7ocD/UtBRqoYR9FO6A6lBrPlCYxny8WS1lRmRL0Y7iWAF1'
        b'PzNz2uXiPsCBJEjjfFiZJIS6utu0uuRjgfaN0827XdCidkqolVWnmBjpdsq7TuMMlZ3eOkOVxUzvFuviWR2t3yVGomEyriWPOsbGrq5z6md0d+LS+1fuvivn2suf48As'
        b'KSTd9+jAmw5B6sDr2I7dj71/1/WoLm68amM2wTY/w6XYr9BxDj12aYKtS48HODTv6sKufqa2y2ze810r5qnhyfaGwzJtmW1Woj+7XbvLOgGiwgqdZx/uLHuzvYl4oig1'
        b'Vlb8/PbqnNvTLPPYXq69vWDaHrEh/rmtWYFLWmiuNGv0HpuaYm8qdDrJaLM19tjef+wkwJVOcYzrBxIpzRiznGO01UQ6K5K/MnShQJJWZUmBa6LfcJd3LO3H6NZtRmIT'
        b'QV2/j8ogH/XN0LRrw0vzNfLSL4q+YP66N7Rg10uh60JTtpa9xRQ9J/lE/Z2SNRMBGQFC2+qA67ohOnQ3QMB1+A7e+hSulwqN9s8I2jCbz0zyZdzaHo444tl9xQtcuNuz'
        b'7u7UcKn8wRP4978geLl143cVvKzrJs6SMIFjJ0gZZo1+18jxU+jE/NeVcYt3l1CoZYPTdLmBjRITudrl/udY+BTzFu3sF3ahXejqltOiV2fuu6Gh353M8WIW3ZWuSzyq'
        b'5MyRdNGmoyOeFw1WLAtth0VLwicpmc9HB0YRJVOESg3Cj0SE1nHxaAuue5oYE1BITad1tXxhsb6yZLH9U4C2xe0/vzbUYe6dczt91lZCbX5dJZo2xklRsg0es13W3J0h'
        b'iud2nbarbdkJnNk+cyuChRf9J75o6u5Qiy581cS/s1+KmPBLASOYB6yCoVrX+enR6fgcAjmZqWVq8RUJjU1cNigQNaOzMOjlzPI+6D49lqrBJwLx/oFOzCX5Qmp4nopl'
        b'ElCj1N93CrU41RI7ZuIRWjoozCt7NEMNKNen5VMDyjWKJT3fCzEoFghXVaGbaB/RyQmXQjnZUVrBxm49iXenkOugDuPdPngP3rnCuAbKU6m/z8gAu9CPtvlbhX50Fp3W'
        b'zbyazpk2Qp7i/cqhr93tgWKCRUUP3s17mat6pff04ClI/BvzRTRjVdZbQ4IH4N8H7zXfartX8FLYxf/xYk1pWdoXJh2/8U2sIn2oaQD3m2Xxfr5vG+aHhn6mevj4ygf/'
        b'5f12zu86gz8Xf7hs9+tNb3x3f4c2vmHRtrfG//HA2yP+9llyYie/sKgKh28afuvPAZaPBh35xySlF5XtR68MDcNnu+lQRWWacdQUww+dxjetFn9D8E5HNjYLbaQ7zYL2'
        b'4s0La5+612CjAWdZTxnVJHR7sm+EleO1csb41BTiMNshxhfRTXyW1ruawzdQUxY1FyH8LqwyOgeSua1iKRODzkj7o4v4Jt3BCnQS77faOESim1Yzh+jJguHdmhxBUUzV'
        b'FPV4n1WHMU6qtH9b3KO+VFq41KizfgJW4bC9ZYVilmMHAFfa12ofJ4c38Xe1gQ6bjxZ1/oS1xlhm8sB1csbtzju+neyM7js+8Ii7c6/ujeaViB02pNMps/XrxdThz/71'
        b'YjE97JLAXhfTvS6h+1u8SlLg8O4JyUtc9ro0j56y4M3oKr6KiC34QAZvCh6IDxZQMZee/qKGodGlsyOnqmaqiNmKVw9uwHh0V/fl7VkiE7lH89C9AURBtgXhfu+8+P6L'
        b'l7bcbLu5/uautA3KXYM23Fx/ev2IlszmQbvWxocxZ3NkU9fWAs2mlvPnDeNAdMnEdxei8+GEglPzFZbpVy5GDfjyWNuKPF1TLi2kPiB05QMdVt5fL6bqKadJp1kFlbjU'
        b'wYSQfoKaaqacsftpsRDbLSdd9R3w0HVfdbdfBHbpgOdFH8tQS0OmXkp1EWTpvf4TS++qP5DkCStMtqXXatRYgPeg02SJd7CMCN9mc7PRBl3PrfdEJqJc7/zTwkdF2Zpw'
        b'Prw4W+DGih4V6Uoj/vjnsDeLHhQtLv1S+6iI2xSTFG+5cjzGcqn60vHYxlhxfNV1hlnyph838eUuzvWZjGKcPkFONIoOqxzsuL+NgtUQsWGt7eUw0V1lhKp2eoalXfY1'
        b'Ja7sld3XNKTVzZq6b+oBOW/wvLojhS0tsW5qyc9cWbcct+umtq0sxalr8b2pBaqZeHt8hoiRJKMLXixah7biet3HbT+KTcQxZN2/fnhUlGlf2wxepHlYpNZ8UfQlrPCX'
        b'RYGa8tKckqAS4cPhJ9u8vsN62MHEoJPQzK3ZORHoIFojWHzjQ6HP/t3hTv9C652rDovryHjLasXErzzEYa6dCtj0Fs7bs1NaqikxVxo9oG+xcZ+nLb0XHku7L39wvZvl'
        b'99glZYBgstxlwUyMlzv9uoTyxXxNp191paWknDfSIrHOwbhO3xJyjQ1PPh8b6xiI65RpdSbh/hliCN0pqdaYyVXFvMUMoii5UpfuVTm/rKRcQy58JVFzaU5iKBXb6WO7'
        b'P0andfC+n0dzmHVmPa+U0dM5IyE+RsJwubtCOa9TRr49Qqrs9CVvNq93Gk2vsqLtxRmPkpq9iPNlceUy6qDfKakqrzTwnaJSzbJOCV9Bvp7LdYp1ULJTVKwrgYBX+vjx'
        b'+TPypneKx+dPm2gkDk3Gq0w3LQhZSrK+RA9GMZT12mQptdJm62Wlsp/JHrvoXUXW6p13V4nAHgdaVobquL9ImBjNvN21FkbwsNmM67wrxprw9QAAKA6fYCPwPryOnkVF'
        b'4aP4qMlcDWn4mi8wprvRPS+8h/Pvh27QO1DQJby/JJLYhp4Pz8hVZ+ZOxQ156HwUbo3OmpoRlRUNzC5wZDY3qshK3DZPPl6Mr1IeXD0tHLdNZZjSAcCZ54bjBkrYB8Tg'
        b'Q/HEgpsdjtclMqgNH+5Ds5einQvjAdLjGXQGN8b71VIDbXQV3R0E+TmGDcdn8VkGtRf7UzwiLo+1u5+wDL5R5TuXwxfwBnRMYBEOoFZ0F0pKGVaJr6ENDNredyEtia7j'
        b'vRZi5numFFjJRPIt+MssdBU30nmc6xUhC+ROwYQWce8P9RM4jpp01AyVgXQZgVvxFgY40wN4p+C+d9CAz2SrVeoImM9G3JqrwptyWKYPOiYei46ii7TSgvmK5+pEa0CI'
        b'KVrB1ogZeoRomqyAOkUMG7UI3WbQLnWeYM3eShw8IsnVK5l4c3FPYh8bgFpExWp0mFa2dH4f+Sui2URJsWJ+TDxDJzYrCW2B2rwYVtUDryGLuTVdMMPfDzNxS28GJpZ+'
        b'U0kcxaJbPdBeWtXnkaNTFom+Z5iYommN+RVWoDmwuG98AroE8pgaX0DrGLQHb8VHaG2DgCu7R0zBUAfekAtyk3csh3YZx9HaPirMHpsjCmdh6hb5JvRkqO29CV8tILXB'
        b'kkfL0hi0N1wkEIK6THQJ2Pk5+ArID9ReYSM3GN+yLsP8cAlzkAOWZ2xRVJ88jqHg0BtdrohPSIKORU1FsArb0QZcR30x8dZQdDubXFHThDdnL0bnqY2aP6oTjcanh9Ia'
        b'b5WkLJrOfcQwRUVBr6yUCTVyqL4GauTIUBvQNgbtROdHU/tHHW4NsVa4NjOvC9T6onYx2jQJr6Hl/fEZHZQHKIsuxM/DIoJk0SJ4h97Gx9FRoQbiSHoIbSIr6V8lSkE7'
        b'TLRHNTlB8yUiojEr6j9yXpHQI7R/ED4aH0cANwrfHkZA7egMOmMB+M58gFt0EjUTwOUAcK+wuF2G1tFlwx2QtSE+MQamJw49P4uUbEAHBSDYim5OA6H32kBiYsgyUh0X'
        b'CqTyoNDinsDs+GRSLAUEt5MwCBlupKZQIHBNswLiJnSRYXi8Uz5SFFgxUXDv3MyIoRzMXeoIP6hleDx1j8Bn8CXcmC3Ml5JY2VegNfJAUa/kMXTUK6Te/ktZBVmHnLdC'
        b'qgTwRbeXKeOTE6APqfiwD4BvOjpBRzV8khx6MB+3EU/LbICSEq4fWh8qmI9uxQdFUApAKw0d0hM47YBiNKkBhPIN2dnkoIKrHIjOsGPRltGC0wdggxFQCvo9Et/qAxCJ'
        b'TsuEWdqG2kaAvLcEHcuFZWuGeerJeecKqsGFs5YPG8F9QYA7qTIsVVgsE26vRR0xCRKGHeeLbwEywBciBK/Izai+PHAwSBBZ5EhFhO+x0NAtZPW+lUx+7u/kRExRFKEb'
        b'wFnFmjbcoSK1AUoYX7aMQYdg9x2k0xOehs9lA14BnmbhUHyAjcbHS2lF35eGTFjDFZHJXPFj30BhAweheyBMN8VkZxI7ILGYBXboFCBgsmjylQupra+a6YG2qtENdIGa'
        b'1QWrocPEPWNaBsjJqpmChRxuyI0CHMRU4H3M5CCvfngjaqSg6D9jvM3TtobuChnexaHtuE7UdYN2g0yUNZ+jd2nr68b7C/qaebPRMdwGPGgUg7asiBpTIlyJtQ3GujG7'
        b'26kW0BoxyHq9hqIzEksqOk1nPKkU38NNU4t6JcbgTYDNgtgFybl0xjlATZezp+MWAAe8GybgFgOAeANfo9s5Em/J6e4uDnSjbfDQfIkOPY92C3LnEdzeF+/1hcW4x6Bm'
        b'Ft1T+AlO1Qd98NVImJNcvDlDlSUIhrFiRl8xbLokDp/pQYf8RVrfuO9F5YR2zN82xiIMech0f7wXOG50n8ksRfe9ouh1V0CFDga5VMjBoucOmyGJH4ovUpgQp6CL2VOB'
        b'urL4HFozgcF30RbcJKDpcwvQEbwfXysAwtwC1H0521+NNwmgdGRBZPYMYSqO4x2LiWPu1dEWeuR3HF0e1c0fn2UGoia0cZYYX0fH0V060ePRIdSE9/qRI1kGXeTRHXxy'
        b'ruDUfhxf9SX7Ww3Zd2XmQQWZqjgx0w/tEetlPC09SjaE+Hwx6C4B4zXoLt6PmmnpfjJiug2F5+PNtrIclN0rrsB78D0Bs5xbkoObCBJm0OHJOtSkplAXORjdIracpNeh'
        b'SbTfAT1Fi8zAcZBSw9CasVaVAWo1DgxBO4UBnwHsd4aiMSAfFLaiBS/8/uiaGBDbuVRhzk4AZt1IDFUAGzHzAU3ctgCNp67pLZlhuAm4k8XEqrp1MT4bKZDqM4X4dLZK'
        b'lYnOhWfBXgMW5Xmm51gRbu+ZSqdhGLowGO+VE0aGrPhW4GfqeDqWkWH+Vp9XfCrL7n0Di3OeAuLwvnityc8PcBTerMhn8Hm0N5CC2NG+vitWMOEExKKOjo8TOIlA1L4C'
        b'N8HIK5k81F7phVopCeo/bALwbhnEO785O19Fesgo+qG2yWJ86blkqtUcmDmEfaH2KIDnWMMHy+74VQkV5uJ7sPyCVhXtV9fGGHQvNX4qMf0dON7HvssXvDmn8q2xgV5/'
        b'edfy5ZCKtucP193qf/j9v789bu2OHePmfdXx/qxl32dnvJId/NkbNYMUf+r5cPJfVkXekw5kGr9etnjOyAmv/DAy7cCXzd63xG+/tT7OfJ+rnDCe/2HCvL6RPc13dz23'
        b'5/jWTW8fGhV1WDzm6xJ+RtPB1bNi079598NhGdyP7T0O6a/9cCakYsX0wa+b4l78Wjth15UDLyWuypdYzv66KmhTTkfC/i977Na8++jY0Cut/G8zh8T9z5UPX2G3ro+q'
        b'33d1on+fiF819deMePiHXS8v2fGBf37Dvijzsqw/mA+/Hrq1I+rzffv63JxyyjT1D9PS1U3zNXOqroQbt3+2p23o1kdRyefKyoLXXn9l2Yqm5MFxn10e8EOsNsv4qyhF'
        b'wuqHDS/EbovYcb7vo8L2xz58/u2eI1975UDy92n7UFZq2ubFaYumWL5Nedjjf7794PmCkrMdr34W+u3Cxk+rD0xNvhP5/PbXl7W/nvLCok++WTr4t7PbFvnO/v3Uf018'
        b'f3NiZfrj1b89X/zhS2EPlo8a9d4nr/7Ye+aSWfrB8Rd6Fhe8rv867P22ed5LCv+QPmzZrm+35Xw69VbbsqheB4IjRm7/oewf+8aP7FOzNVsUPfF6xfXTgxZm/pD64a3A'
        b'yh/fq5P+ftOdX/7qzs7vRaPntuSrP+94p8/otz9eeH+V74h5yq/OTvig9NzOjIKTu/OuPf504JcPHo9RfKnsKfh9n0aHic+COxMEvMUwNFRSHu5rpiR9I25BLZFEuc6h'
        b'PTXT2dwxNYJDw9qx+PxYoOhNRJqQMuIJLLorwWup7risL7qJmgKq5MkzjIC0WgKq/bylTDA6KKrE+/rRLMDbH2R80emoDKuFhAXvYnrgWyJ0Hp1nBGe9UzlyfGpCN1PZ'
        b'CHRTMFPo6FOMmqKjYe8348tR1Gj5KIeafPA2Qe97ZCVHNcg5MIYOqgGU5XLagfh5OrB+uAltgv0E46oOwY1suhYdoa3K0G7cHqnOSbR6o1NzOLQP3aYWyWiHBO9eiFtt'
        b'bufEA7IXXifo04FinyQmIfgEvmk3CkHtCsEb/3oBOieYhewKcTYLmZUraC534Wbg55ztOHiggD2oHUfwOGq9bGIXONtwDPaHDMSCY1g+/RICIOoOtGbYKmI2EkkvpdyU'
        b'gzbb1aCRIySAxLahq9QmxB94ZXKBIeDS3ninq7q03os2io+hO2IiMQCkmIF2231HFuKrgs3LOViH9YLJyDi0xcFqJAQddvf5gJ9t5top0mgFXc4yeNh0OczqIHVvVswG'
        b'Udd04mhOXOzsP1wQ6/IDcbKH/mFDrPcL+tBfosTvyylYf5pOTKBJ3kBSngtkg+GdY2VfBvWu9etS0UB/HLX7RqKQ+7lOepxQqkvrfw0eZzibEcxa20/ft9yZRDv1xfNh'
        b'PFUQCh/QYuoldgUhS1UY/8aRPGlIwXRXYQzP05MWF/cWMeXziEV2kfz4QkFnSNmBQ7PLEGFaBwwJZAYAb3dbYNbWAMOwH5HTzlC8ZQ4TygPrQvPfwBvGx0PtcSNAeo0r'
        b'R4KvWojEm1mT/RzhlaPaQ/sy9KwvKsKb+WHhEBIp56qLBdb1kmkFW97/O6pLERUOF3h9kA9v4VPxIG2A4ElYy50lZasoe1AKgsiJ+ATiX74TsNt4fvBCWo2Xvxczsqw/'
        b'tSbI9J8m1H09NJD5nplEVAE5e7xMQi/eXBnIvD9vMonU562aIeQ8K/Fj7kyIY5gpRVFP+BAh5y2lnBGnJdNIJt/a32/FPsylKMoU5PSPqBZyvj/Xh/nLShopX1fsLURe'
        b'myZlXs7pS7oUNWkFiOihFKFdWUiZyBmE45ZUsyDso1sz8X5h3GsM4+JjYoAVv4BOs0OIlHQ0lTb7i57PMUOCNpH1eq5flViQ99GFYfigwDrgvfggU5vB0/hheE0Z3utD'
        b'OF9Nf3ig1nlW6TMCbcZ7yeTdCIiHB9qGT9JlxHsHAJFoA5BRLRnNqPCNGNrqO0PFTLmxB9UMLIyoFdTKaG8JrEgb3o63j0zE20EewxsZdA1fmEYbH4qOVSBSUxgg2e1M'
        b'WBzaRBm4IHzHYD95FY5d0QV8KAuo3BXKZEcMwfcL6CkT4LoNLN7KBuENwG/Ske6dX0k9gfB93AHPm+gyja/EB0DUOwtvNeh4ATzaI+h4ZqXPE46k0VkNPNrxMXoCTNel'
        b'USxhfs0Hk0HpfxXgL2id5QvmU5uG7MMMm7dQ96th81kTuR007NtvKrbm5uGYwA2jqt/8P81dCVxTx7o/OQkhhLApKALWuICAIIiyiNYCAsqOQtVqLQQSIBoWswDu4oaA'
        b'iCguiLiLIlZR3BVtZ6q397Wvvfb2tprui21vF2utVa/11jfLSUggodje93uP/JicczJnZs6cWb5v5vt/f5+U5e+EJdjdOnvLvaR6F3PvQGJr1LQRs171j/kvu+z5Q+xm'
        b'POvY/9ABl5zct3/9vnHh/czM1k1RE14o3+g5rTW54L2Ns2NerXgjVrGh9PrY1ZNeu5j83Zxnyyc8f/TTr+dL/JXFv7g0TF8skrzwg+a9jR3xhVv/S/jmtTd9bL9693Ri'
        b'jkdSREhzaUG23/vg+7T3F29Yu2j1+b2PeSdv1XnVOj1uhbtdbgUd9dzWf/V73g9yhznPcZtz8OSdw/Wn3Ca1v/7cAnZg6y8tJ/2e7HhF+cN3y9d6v7VRtW3tPcnXa9eP'
        b'WFaxa5UktN5Fu+TvuxJW27+Um2eXFuuade7NKwuenz+8/4LXa0o+ennFlmNLf/5nU/Mz3xy7+f6Vxf732PBSn6NFV9tuiJb/yn9wd9ntH6/6uWuxcsvCamJ22B/U9rrZ'
        b'vO8lOiGtAA1hxEogNdAfz0WnWXAStqEIbfAsNXy/5EgcFiDhYrHGKF7kwzoqfOwF20Wmlp/wEmzUxsEOMm3CM3OwXSiagLEuin0/IwnhQjKP6RfNRz1sJ1hDbe/XIumn'
        b'E7vXwiD+Kh4GMHnCTcNKQBu13NwEapeYiWEzppvYgiIpjEeErfh8Iq0lwHbQMQqvQxzjIYWsbS4taS1cBVZ3WbCAleyE8rFwu4jKWSucMnEO1GsBWdUcMEsAO+I8kQa4'
        b'jz7MaqQPdZrQO8EqsE6OH8abj+b1SkARVbBGMhRLNwbJxh9scokfSiSXcHCRUCAZBRd3JAQRG1QsuMD2KbQ2WuGuKUSIACsiTAGoccuo/LMXtPibyDZIMe2gNqrEPrW+'
        b'iLzYeI0zEjOmBoweDeuCYBNYk4gKClv5aNxoVBKj2YmTF3Ems+YGs0gsOz0RbqV+kLPhbh2JtQF0+CTZMAKWB3bBk8FUdmyBxxPMHRu8CE8Vy8BR0hRBZ3yawTghAbUq'
        b'K/YJDnA9eW6BBzhMJVWDlIoXNECNFDUovHAyAcnC+6m0tnWwFYFtuReRw2TwEm4JZoa5sK4cvf76xUQ+zVGDrV1+ll5gB4Ad4KBnqcHUoU/7ZwJs4UckrTwzSUuiFvAk'
        b'LHGkgCQiLGe5os8A9HFHH3zuiEKW/LNEYupH3S6gj+CW0EvwpXiwiBXzxKwrT/REzMdGEyIWQ8+QLOPYJcvg7E1s4Hopc5dJ3BkU3O4pNrla2mTtlhWqGyykoK968pWK'
        b'jnbgo4HdYGPE8Fe9CAfEGJhYCWMDYb3IYChqOMK7UNS8kuDFsPEWsecg2/tkP5jsCuolWenR06NTsjJfSI/L0PM1Cq1egJ0S6O25HzLiMjOITEiekIqbf95xhhrz1wXg'
        b'6jrH4A0vZz7r8rTwMEcb9O/gKnQWiWzpOxYSQxhht4/gJ9ZFwLneEJu43hAJ2UcCW/ZfIhH7UGTHPhCJ2fsie/YXkYS9J3JgfxY5sndFTuxPImf2jsiF/VHYD6X2g/C2'
        b'o78jyt/dxj2WOBaKLhxkan9kgzr8GcY5kz8brgSXe2xrG7htNFHdmXoFDU6EwdbJ8C1njUf8Wls7gXwEEqAxjsMpTyC3lYuMrL12cjFB8Ug41l4Hcu5IzjFrrxM5dybn'
        b'IsLqKyasvhKOtbc/OXcl52LC6ismrL4SjrV3IDl3J+eSBoHcG5dLPmgn2yDEOJ15DnKPQcweR4xE4c49DecD0f8B3gae3IfDuNsST1P2lU6Vznl2hPuXcPGi3+wIs66A'
        b'IIBEs51xfciH1vIqqeIgqXRAasMw+XDCuusi9yJ2xCM51t2k1LhHW83g4JkGJlj0E6XclfpiuhTMiSUrkuNOouxO2Gl24p+JUekcDRY6Ks7RFKswbzcG02NPx5R6FHta'
        b'VpRoqbNvgqzv5oBajQ1a/Wz1dhyfGyY+4g7JRrOIOl/FFEjyvFI9f34RulaokCt1heiaqASVvKxYLVd38f5aJNw19+ll8KduhxQuMbd7bG/06dVXyt0CP/5nP/WZchdX'
        b'9B+m3P19xt0e7LoWnQr8QcZdkxdiLAf2yN5LKdDP1spQJJWpSgpkgZaKMl6aW4CyzCV+z3snAO6d/9cC1+9T1Mjv8v+itkhdRMfGz5CqZDmYcB4dmnrd9hvdzZ81pa+z'
        b'WArzopO69Q0xqQoLhecKgvrD77APW2Matux1whr7cB+Zhi0m2sU+/CeYhg19nlY7PZMq5dwLG/t7L8wwUHB+wbkzqVqRr9SgGkYDFBrHSHMKkOq416Yrwv65/xChrxM1'
        b'Fxk9y4WRaj+yZUqyA7bE2VDWG+VsUGWVzxfsy6ZqgBnr7pooibNtCkkSOLsxvgEu2P2z15HxSxniMFcADmuZ0N5IgmE14bcxTXR3iQQeEIANJNlwXwnjXrBQyKRnJw8a'
        b'UEaThS3pOlgTDBp7YQkmBt4mPLznwDp7sHckvESSfUZoy0hmBeKVEFWhzyxGF4ouOmih5QpIGJXBJVUIq0hqK2CdHdgCT8P9JLkGbzvGeVaiEO9qu4yxY3R45QyemjEO'
        b'1iwbbokx2Kj+dS/kGXuwHx4Tk1SbZogZV68VZLfnAjuE0WEzKO+0KUhg2QcP90zWl1NuEs3SvADa7OG6HFClvDHaXaBZj4tb6xn45kUHNloSN23xby+tO7zCw7ei8KUB'
        b'IlH4iVOzX3d2C656Y0XqwtyUguZfVTXe+99qTplxMufuKwcfJx//e1Oo9rd2B/uic6HgrfYvw+7Lbu8Pd0mJ10RnXKr65N7w8tK374ivgKbFa92eZH596Fvv0W4NZQ01'
        b'2wqXzbs96zve5Vfr4APZPu3wm79t+y7st5RWPzHRzha4wY0m6uZxsNGgcnouD6fr4KdmxRkdyWqf7VoFBxvAQS11k42UoWpTpTWJ6IqgDh4ZArdjS/GDsI06XzoNriAl'
        b'0aC6ViI9lDQZTnflFxOlKHwcXGNgFi6G9QQf7wCb6D7Gy2BvJDhYgvVOo2oNtmopAnR1PNwFWxKpomjQEheMpupqJ2zG/nXpIoAObqMNgVsDKAMXicYmAednUH114CDy'
        b'Ug3aqjeo0hKsbD08BzYSGRa08xICYQc8oyErG0ioTSZCbaCQSQGrbUEzbAZb/mM6gBFuif1HdGl5zHLHGEcObmngFBZzzMKmZ0aGYSR5WGYYfgUHr+IA4ADi4DUcXMXB'
        b'NYb5fSIeUV8ScTB7JD++wVa/ousjtbR83rP4T8fpaxSerGLonkdloQjNrrxMiIbxpV6Ihp8apCnJMpGkrBZqlqFQj57pVgIiF/xRrl2D1GQ13znGfIfQfP8cwTEHDhVk'
        b'IVnJap4vGfP0pHmayFN/jFBZkIVEIqv5yYz5+XYJTbLuSNinJ1E21rJBTLFaArmxBB54lcNEkvmDD2yXZVSCrOWZb5YnqmWj/GOSpx9LwdRk1cRofZuayzcpCjZrx32Y'
        b'mN8mooDsWGF3FSynuoqJg2RJnsRo5G7TVyP3X2z69ZmWSoEpOPvKSkUiPw0plSkJVY8kMSmVEe/sHyD1NwVeo3OC5UaRTCl1iGxLi4GZSvqu/xkzipRmFBdiLYKq3NiX'
        b'HIeeluUU67Qc15MGyavW6gb/YV4VBa4SuTKPsO5oOXnc/KG4+ibuMlG15XOe8iyIwvgvwcgSJetNtRsTZqLQSH0NVDTWVRvTeqVie4+OKvWNzlErcguKMAsOp+cRf3kW'
        b'C9rVDjQaZX4RaQqUa6YH4ZlGqjR9KiVSefKtENoYVJkx5CWHjTdqNDinMX4BeJHEwJKMYxhpknOtKWGkVSrJ/Zh3C9ddxPi+83blmT8QfmqlQvOfY93yxSxThB/LT+rv'
        b'X4jVbPQ4C/39/zAPl9SXcG4FUuqqp0m6F86tPt3/tAxYUivMXdYYsEb3rRhmuJBeebB8jTxYY/ykc8aEWOexMsWWcK9Rp6CPoywiBSV09rEpKS+8gJ/Mkvtc/FciW1hI'
        b'nO8q1HiaCiAkd0bt2KRAIb0XqFdyLvO1Etpbggw9xWKxqDBkSumFsh8bbJ2dzRSJY1g5Mukm6CrqkUUaJS1UcZ5lsjP5PNQySH3gG4gHYlk5Pu4jzxP+izZLREMWzZS5'
        b'BVolIfPSdFHN9eyzVtMMlI7BfNkKHRpcjQmgFqyUclWERqhC1OPing/MlGlzFHgh0jL1WKAUNRfqHFWlK5yvKLBc/4HSsd2ikdxkurxFOq0CzRzYE7V0RrFaQwplJY1x'
        b'kdJoXV6BIkeHux66IVqnLcbz23wrN4RGShOK5MpSJWrMKhW6gRLiabo9uZW7wywV+ekrKNxSMkqTYhU+XbEiLKX3dPUynlRkV9X/Ts1bvJhJWzJeMexW7qduiaaPn6dG'
        b'T+OL69ZYJlnOIl2+n/XmZ3q7NNzbegM0izhmvLWYqJkVBfXkGqU/hnZPJsxaMmG9JYMahfH5ekkjwjSa1Ucbb5aYheeyOqFxSEE0wnFHRB5AMikaWw1DuW8GnWOtTthd'
        b'QETMd4+mQnqGZBzfJHSqKEL/qJlL8RwUYZ1/swvCaJ5MSLdkQnpNhqAdzQgZfQkLYyyeb0Kt3mZER9Jb454nIzW+IPVFnZxr4ui1W68GnRoTU6LZYjJ3FCA1ke3inp8u'
        b'9Z0JDxSoUSdFZRlnvSgmwMyuxIyXuUIZktLM16k1PQvVm7hnTbwkomTfJT+jiBZttvjfNxmGQE0jpan4SzonJHhu328LobeFkNusvw0DhpUTIblzrDr31g4IwBXdgr9Q'
        b'xJ7xrI9iUxVqdVFQvFqmQ4FqdFC8Ekl31kctEt36WIXTsT4+4QysD1C95YxGpbgCJIShsd/60ETKhmQ2ueViWKs8JMUqFFosWeBvJGCF9Srf5RSXR0rxPjKSn/Kw1Iou'
        b'oDq3/lLxTRg5TO+SqaT4pNc7cpVa3CFR2Ku4R+HSOCY9IAkHYDk9cOyYsDDU0qyXCSOVUYHwV68tMk+GnjYeDSq9RSJYZ/SG8Jd0Tpj1iNwwZ+Cc7aVFG1DYkdIYdEQl'
        b'4Tkh4b3GN3Ztcov55l6v9W3AdnN30vdjfbDGiG4kosVEp6LXY31EzFHmogQTJqOsLfTIHnhsvIVvcYPtlRg+kykn8Lfkb4dHUEtbsNXBx0hRyWNEpUsIbq4wl9xSnShg'
        b'slOoZWtTgjM1O1bBnYkEyFeYSqF88AQ4TaIPix3ISOPmEBzw+8t9qa00vGQPL1CEX0EWM1oOqihn1T6wA+xOSs4C+4yYL4KYXiYgaT3KXMJrd7+LLZ49CxJFjA4705k/'
        b'D1wchaJitsU0bFkIjiamUJ9JDCpFzXSmHF4sG2eXL1hCwESe49LY15ZdlTAlsv4fzIqSraR7daAabAabLblIsgXHcWJT6VaFGc1kLWiU+JWA/WS9UHl1xE1Go0dHwfxP'
        b'dRveTgXZzq/l3/9VPz0q99JPzM6IRSGf+d351F71mG+3SR+lmu0U5vPGwW1n3mau2eqS3v64tGzZ2AnX5qY/05pzcsqJ4MtpoV7K1qprg1QfJo45mz08aW1NzObixs8E'
        b'KW+rDk5enpWT/r6qvfMf328q/VFZFnn3VMmmn/dcDSn4+G5N6PoBu2Pgjq3Hv9h19a2Ty+a1flHr2hZyPSFtxkzhG7ubf/1M/NvbjTuSJuYs7j+tZUhx7PBYt8LpST+m'
        b'f/LcrVf4R76ruJ/XmJrVeStowjud1bYvfvjRk9uPbzl1LIz5bKSbn4jsG00Z5UI8Krf7dEFI4GmORQte9oAtFD8C20ETxZAEwUbq8X5Vf4yxSPOG5xPAUQEjVLHDlGAX'
        b'2UqaGQSr6M5ZWoIZfgReFBN3dQ5D0TsixlDmu0jTYEu3jaRYX2r5Wckb290hE8sMsQG7qEOmNcuIQSU4NRDsg0fDe3AcYn7DF+FpLW6z8kmipOQEHsPCdQXTef7gcHpP'
        b'2IfkP+TxHBvEka2reNyDl5t+RGkYCII9640goA7qrYeYHZJtK5bnQb5FK9gnLOtlPF4kMe7QGHEdnAuQrmVrbM9tsmdl91Tl9xOYJELSNEd9zLO0cTVsk4WNK7OiWod9'
        b'EFdP2A6JqRQYXT311Q/javT2FqAEzMZK/BhDeoyV3nSsnBCKfQZ/k8mLylZ9JJhJx8pMiSO4BI9rdNNCgzGSFbUq3lK4GjRTYAiG1qphzTB7PgMb4lB5ZnrAsxQLsAOs'
        b'huszQh3A+WAKgb2IXZnXccPm4XDsdniqn12wbPGe6cncsLnuufCBMw0YDkUZ6KCXty1h548zYD5y4bFAksSG4UJGwkRki6XZKg87BQVhdEhdGCmTXWRbkp3sEO9C7foF'
        b'4fjiRiG/JFvyyovONObtcAmDurONbXp2wPIoBxrzvAO+6J7qlJ6dPHLsLBrzhkDMuDLp4zGGIymtjMasnG+PLj6czqKL47Ofpxc9JLhIf5toI81ODkkto4hyWBsBLmak'
        b'w5ol6ekMw4tlQEU6rKDo4U0ysGNscC6owKyLPHiAgRXg5WzqSeAw2LQEdrhmpDMYu9eCnfY0gyPUbUN7CDw+FGwxw4uAC2CLhOL4j4DVvj5gLwGMELDIzCkULNHpBGoy'
        b'0P3rUUUOZYbCI1GEe0oHdmGojgTsZUKYkBcdSWQ0uFWCDgz9cEbXA5nAxQV0FqsDa6ZglEcS3I+hHgaYB9gqIwUv04JG9Li1YL8UY4873IRg72zQRu/d7QI2TkRPYg73'
        b'SIyBZykMg3ROvh3jzHyaLM7OlswPS6dVO5HBF1/3FWZnJw9arKYwFzVc5wjWJWXgikVDLyNLjSUpzJ3tyvgyIiE/KttLsVTBedTY/CzYiArWDDvBHj+GiVxqD/cu8SDv'
        b'yGFgocYBHgH7xqIaY0EbAzsjQbXyRl2uQOONOmh4+OrC+iQM9libv/NAyqPk2Tveuev//WeCgPO8+aXPxboOPShb82V71Ua1ZM7nBV4HvjgQG+Cf9N7j3d//6+ufEr0V'
        b'meqXz8hvvMN/9t8NR3xe9v9tXVl9bOaY8oSDh7ZMmzGu4f70CyP/+9qq/CUPRV7X53nuedBSPefezxNWn35DPznT7+9T5M3ilNUVCkn0J/PiYoQx8THXbD8/H+Bm3yxq'
        b'/m0/XJv4zGuBPzzeVf9l0Hbdo8E/X3IODcndOev2w0N3gqZt3pp7PTPi6oFW9+i//cum8Gs/WYVr0vhDp0cW5zTyKpq/G7PSrd/RjtOKzZ++eVLRMne15ov5VUnvZT6+'
        b'kPDXK433Soambit0OhcZ4jbzH15NLUdq75xq/vGzy2+B54YELq5f+uHro7+p36dyqohZwLpX+rlqMduP/VJYaT6LwTZny+YQ++FFAoGYDOrDYMviUWRyRD+jGZEF9fCS'
        b'jFpxnISXwY5RifCCKiWZxwiG8kAzWAGPU1P//eASeBlJN1XmJIkLlpL5WKyYiCEiA+1NEKglsJmgN8DmGHh+IjjV3eUBhhtI42zsZsPNBDhR5OcGatJ8YG2XgQmspoKC'
        b'PTyxhENugH1BFLwxFnS8QKfds/A8dj9rsIMBHWCV0ZoGNBRQfp1Kb9TNDAgT0DmDgEyGwRolNZC5iMF1ZtgObKFSDhqwfcxcUEE8boE1E1FvbUueNM0Iah0+k8Jojpek'
        b'Jpn5FX8GnHcEq/gxcONsGqNJB7Zx0FBqprMqgtKKXYGUw2whPCNMMnU6Do4FOC7lx/aDxzhw6XTY3IXpwBYy4RpiIzOoiIJu66dHEhOc/S91WeEsW0xePR/sTRoFNndj'
        b'oQTH/aiNzhqwZZwZTgc/PTgTSWA6nfAyEYOCwNGoweBsT4sjam20GFZYMU/5HSeChBiGyCmlPeQUQYmAk0ckPGdWRCZ5Zw68iiEVzgRUwRJGZdb46YJXEFDFV0JP4S2x'
        b'F5JxWAq3cCZm+NhEX/BQZCd6IBBzpGhEWOhBt2a5/N2I1/gGarcK00+/bVYJ2Ezz0mARwqq34T/NvpaHpBRddynFMvWYLaUeS4AXwU64bSalH7NKPTYSTTi4HhL94csG'
        b'DjHYxNGIgSo1FSxenpY3yhach5cZppwpnwqr6fTZDHaFjoIrwCpCJcbAHZOGKW++xrAabPGwPfqbZ1M6xSBKkqpuPfMPseOkiqamjraIc5Hr9nww9HPpu+LRZTVn5T+7'
        b'3f743Rft77o83LTkuZzbztMiZOHb3vT7+euY5HH8xSeurhjSMGyA3UTRX6atjDhz4JPaw+97VGRPjFynWLmkPfDFb8cuvHtNdtRr/GbR3rn/nDEyqr1kxWXlO2dvn1Lu'
        b'GAQ+ueL1OKbzmEtpw+vqPcVf3FywU9nybd2Oq9XZzs/c8rjwwZzjg0Y2l+5uOvKdk+OZMI/d5/2cqDOATVEJlEDMdwmlEGN8SCf0As0iNCXbBpjxh9mBNjrEVgyDx5De'
        b'WQXOB3QRhIFNHJA/DBwsoQxhmB+sHDYbKML855Pf3WU+lH0MaydC9AvHPgaq06kjgJ3w6AjCIYYZxGAbOMKxiA30IqOHDejUoNxPg0ZYZWQR0wRQKrBDCeCyqQdcsB0e'
        b'IV5wS0rJzSJ4BHbCmpGwJaCLSCz1WfJcgxcKuljEUlAjcIK7MY3YgRlUlVsJdhcmwTWBeOg1kIi5L6dVchnNOUeSJkwytjrKIFYroNDEJngeu4iBaxfC2i4KMb4Hudkb'
        b'nIO7jV4RwNkUOi0Fg20cbQXc0n+UcHiQCYMYBj7+RxjECM0VGdKCewxpzPJhgX0iEcMDhJFETF3G9A7yKjfLewi6phnRYzhiKgZ8YJU0zJAfGu/McRz0lPPzjY9T/fp1'
        b'B30tZBhT5NcrOOjdHvECQ9x6axWFGgrd6sYP5vKntOA+vCM0HDFD8bA9i6GEYM5CCaHvGvCE9ftjdGASAZ5cBE8ET6T8fmWiCR48gr4CV8DBMI1RVLNhHDzAVnCWRUPm'
        b'NmygpzzjIBRoBiIJuHrl0rgNE4pWRSEJeGD7qzfcg51yv/+Uf+COyzu3GD91Rda4rdNHZE77UF4vVH/7Zk5DQVNz8W9/eXx0UtDkSYL46LnNdVN+rTw2NS9/R9OvkvdP'
        b'7q3I95k7ZfmFuPhrdbO2Cp78NeT63OYHSYekjZ98u+VjNu6+w9epuYqGg2U/ut9ZOXlD+RtjDl36Yr39pAV/Xys6cfvf1xf73BwJNPdnO3nGdta9/o3nX7/a+/yNYQP6'
        b'La9fEB/aIWht1+aMezcmYZFr0M1tp/773a1vLh3/4/nP+UNufpHRJKtMvtR4Pf4j17uyuX87vODLdLV9w9LgC5sOeX/95KudSaVXB+fUJX645fr+sb/o4/NvJ+cVDp33'
        b'gZ/jpLN2joevZqTVetyLiX5iz+rkY2Ij/fiUTWaND1ZqkHCCSXBBE4PGjIvziHxVBLcu5OylfcAJs2WflgAivkjhSrXZKg5YAVrpSg5ZxkkJ7rkS4/m/0wafOkAjD9/Y'
        b'ES0FBJEqyspSFcvkWVlk5MFKAuvBsuN4UrzA80TI4gUeqYeHq6u/63PsyEgeWQia6Mj3sWeWs6URPPUNY+fj69msLJM1HI//B3XAU9809l1cUkJviSfcqG8sMJZJGTyl'
        b'gnM8UAPq0BRQlZaMptY6eAwgvcNxEH8w3F6ofHzvHE9Th2Juubh+cNV4RxDsavPkwW3nqKmq6qic8f1mtsfkljUkVN57eFYU7n1ux6CUz2Mb4z0KPt/26O7r/LTIQqb1'
        b'plvGo6zhl99J3N7aMeqlw5M2T67KSXKe+cFXLQGxW2acO/PGGyf7QQE7OXo42BNtb18ZGnYjp/JZx4h9q/5ily94seSqw4PLSZPWlDn/+7pT9dtDRBm+N+/zkCSB5113'
        b'cCoQz/lpeEUakxXbg5OlE1h4GG6WU61iZf+ypLRAeAIDqg/FpeF52wVewmjyXYOpdtQCm0bRKsDCOl7rRLNiG6qCfvxnZoPtdC5sB+3TkhJS/FPgRtBoywgFrAhcgatI'
        b'p8sFjQDNo0FCZjas5WVgVXAXPEoUIrhpOLw4KtGGmQ+38JIYuB1uB5dJyXNBdSjhvEN5YgS2vZ8tWMui1GvBKiKOZIN9UzUmEcQJ4ATcyIL2IC3HPgovlCWRIRN310J4'
        b'yYZxhNX8VNhSRIoVizST/dTrH4q7nWwXeIrJvUuQllZNhNGpnKAl6b8E7GDhKZkjqbYYcBTUYfREQAkXQQw6hsNaFmmpDNGIooIGot9PSsC6sgXxcJMOdiyQLNDxmIGw'
        b'jg/Wg43LaPXvjAR7koj7BPwoSFHFHj7qWLjvBaS0YeVXAdvmgpqXQAuoC0pCo9IGvCaMX4ct4zlCAFa5wSYz/8iD/+/7WfduZ/c7Q4+FkagLNIGBKiIHsdH7P9bdJLxJ'
        b'/O4ikWAEFR7I4DNEz1cpivQCbKSrt9HqSlQKvUCl1Gj1Aqwt6QXFJehnvkar1tsQ/ni9IKe4WKXnK4u0eps8NAaiLzXe08e0ISU6rZ6fW6DW84vVcr0wT6nSKtBJoaxE'
        b'z1+kLNHbyDS5SqWeX6AoR1FQ8mKlxgAR1QtLdDkqZa7eliJoNXp7TYEyT5ulUKuL1XqHEplao8hSaoqx2aHeQVeUWyBTFinkWYryXL1dVpZGgUqflaUXUjM9Ewf3LH3b'
        b'v+Djn3DwPQ4+x8FnOMC0buqPcfBPHHyJgx9w8BUOMI+p+kcc4I0i9Uc4+BYHt3HwCQ6+wQHmhFPfwcEtHNzFwac4+BAHH+DgHg7u4+A7s9cnNoyusQ97jq4kxiNRHrbI'
        b'zS0YrXfOyuKOuRnokQd3Li2R5c6X5Ss4NLJMrpCn+omIuIj5ZWUqFccvSwRKvRjVu1qrwZzdeqGqOFem0ugl07FxYKEiDte5+qGh9rqZ2OtFEwuL5TqVYhJe6ScODgSM'
        b'wFbEdm9qruEsaYr/Aw1dCkU='
    ))))
