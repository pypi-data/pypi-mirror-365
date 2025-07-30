
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
        b'eJzsvQlck0feAPzk5L5MkEvwQc4ACfftBShyo4JH1RYCCRANAXOgUrVelSAeiKioWFGpRUWLR1tqbWtnurvd7naXuOmaZdt33b579Xh3aWu33b777n4z8yQhIcG63e5+'
        b'+/1+XwiTeeZ6/jPzn/kfM/Of/6ZsPhzz7+d7kXOcklFrqEZqDUvG2kOtYcs5A1zKyUfGvsCiqMssy7PaU8ZhU3LeBeS/bE3VRmk817JROF/GtU+/i4VCXeRTSmFRMl4V'
        b'5dYk4n+9zX1RXvXilXRzi0ynlNMtDbS2SU4v3aJtalHRhQqVVl7fRLdK6zdIG+USd/fqJoXGklYmb1Co5Bq6Qaeq1ypaVBpaqpLR9UqpRiPXuGtb6Hq1XKqV08wLZFKt'
        b'lJZvrm+SqhrldINCKddI3Otn2dQ1FP174Ab6DXI6qA5WB7uD08Ht4HXwO1w6XDvcOtw7PDo8O7w6vDt8Onw7/DpmdAg6hB3+HTM7AjoCO4I6gjtCOmYdp/Qh+gD9DL2r'
        b'3kXvpefqffTueoHeU++m99dTeo7eVy/U8/Te+iD9TL2HPlDP17P1LH2wfpberyEUdYfrtlA21Rli38TbwtwoNrU11D4UhYTZh7Co7aHbw6qoiGnjNlGbOY9Rm1hue0Ts'
        b'inrbzg5G/wLcAHwzhlRRIvcKpSt68n2STXHXqdkUVVu2VqOhdJEoEJzyAidhF+ysLFsG9fBApQgeKF6xVMynYtRNi7nwdQ0cFrF0ISgp7Ctr0RSXw4NwP3gpqRzuZ1Hu'
        b'xWwwUgn6RWydP0qxFVxSlBYnFPMoLrwFh7gscGY9RfKu5VTgCDHshPvLeZT3U+B1uI9TAa6Ckygv7jW4OyIAdMF9Ca0ImithcD8qxR3cYIOb8Ey8LgKDuhschq+iNHsq'
        b'4HVPoN+0UQdvbPTcqGNRAfAQB+zPn48gJZXqCUkAXeAU6ASHEkvFcRhkeAiFHHKhQiK5YDc8FF/Psmm1EEurXULO0eAO1HKok7moiynUtS4IDdwQAnggBPBCne6Dut8P'
        b'IYcAIYE/QoAAhABBqPND9LMaQkjnoxHT6TKl89mk81kOnc926GDWdra5853GWTu/YWrnBzjp/FCm8zc/xac8EQ7cXyErOxO8gSKBGVUcCk8Z9Lony+545zGBj2vdKF+K'
        b'ShpgN5Z9qgpmAsOXcyn0S99hPeVZq4ijLlJKdxS8YWUg98EMauGEYAvrl6v3ueXLoiilG4rYwu5jjbhQdNJjE2nvpZxpu8UEfyX7zKfXhxU7Qd9n/y1QtuJTapzSSVBE'
        b'E3wWnEEd35W4LDYW7kssEsN94GJ1bEk5PJQgoVXF4pJyFqXycZsHLsBLdn3nYan0Ptx3Hua+49n1G4V7rsHD2jfcf3nfOAxMFyd941mhxo2rw/0GelGNn69aLl7JpnQ+'
        b'bA4FT4MrYIduBh4b+uilVWyE1uB59O4IeHm7DvUQtT0RDlUtR+O5CTX7Yt2TJK0EYfcgPMKhqv2pRCoRdKeRtB4LwQ14hEUpJZSYEi+u1GFYwPUVs6rKl8EDPMrHjf0k'
        b'a5asRReF37c/D76MemN/fCkaOJ1ly2LBxZzihCIyL0jgRR7YFSlhSjgMD8Oj4Aafgqe8qbnU3LIixc+PLedpjCiyv+Ivp96ed3pn59kjN45sCIrgwPX03h2SqzOyTu1k'
        b'Pf7zp8P/fHD/Fk8Bp0BcIK73quesda+PWeW122vphY6ApuAlXvUxX6YM/HV9dN/BOb8QXgj+Pq+oYc5Cd427x6WP4jK6Ty8VvDMQff38ibd8hL+/Kl2kC1q3iq4OWBtT'
        b'FSw4WSFX5mwcPZD+tNeKzPf2Rg95/bjpQumOMpe6Nm1I66g2yDjrWMVKz+MlbOj5k4KNAbneP/vJsZGIix9QJ9/Z/UfvpX84ty8t+UKrpPaNBp/2H7uktl7gUMPdRbFJ'
        b'fxXxHmB6Ay7B55SlBa3wQDw8UC4uwXPeDDjKgR0BaQ/wbLIEvCyKLxFDfXFZBQ+8mER5gGts1KU3QQ8pYGUmPBcvEZXEm2fE7fC0D9zBaYHD8LkHYbgP9sIrVR7wVgW4'
        b'mFCkQ3PYvkQ25QdvccAV2B3zAKOMzq8WddI+eAju51CsHG42C1ybBV8WeY2zY0Vq3Ovf0tF44UmB3jH5+Xrm3AZ1S7tchaguoecSRIvlbfPHvdRylUyurlHL61vUsnb7'
        b'RzYuqxEN1q92UBNbWdTM4O7qvujD63rX6QvfnxU10GCYJTbOEk9Q3l6LWYx72LWb1Z1uEgR2zzPRc7oL+5IPF3cXm/xnd68Z4A1oDP7xRv/4CcrDbzHLREcP+T8feil0'
        b'RDO6yCDKM4ryDHTetFncSJaIAc7A4rPug+5T0g3xhjaNxWQa/LOM/lkTlIt94nt0yl06ZSR1lGOg5xrpuVNfojX4Jxj9EyYonjVfwUDBEO9syWDJWZ9Bn6kv4w412byM'
        b'QzJFPed9znuozUBnGOkMS4bfBkeMRaaPctHfipc9bnsYIgsMwYuMwYvGhItMgpnHs3qy+goNggijIGLMM+JzPNGo8Uwj8h7nM30w7lJTo9apamrGPWpq6pVyqUrXikK+'
        b'JWJ4I6fWDjPUfjgSzzxTOn8BTt+HJ33c+0+yWCzhBPVdOPe9A/SKzg37N+zwmGDzWEKTxwx9Zmf2/uz7XJ8dpTvL95TvKDe5+phcBXqPryZ4FM/XPnRHJfOnwRTptFsq'
        b'dcM7j8Wxm6ytfHYdpim845Qcc9mIx5ax1nDQP1dBreGhX76MvcZF5qanGlgy7h63Na7Ex9vjuoYJ4yOfO6I+LD27gSNzQU8ehH3koidX9OQpYyEeulHkPs5fThqtgvTe'
        b'h39DY6aeYwMQ10I9tmOAWAxnexwXTJGiMWFDTH3nFKZ+G5cQNo4DYeM6EC/Odq6ZsDmNsxK2xqmEjeOEsHEZpkM5H3ENsnksamFtglfbGkqR+z8GStOAC23nn3p77umz'
        b'R7K7WPycxyJ//UlgNH0m+xm/7z/Puyjb9enMpNRaVrrnj3Z8tAp+MZi0cq3LTm3KnI/LpENSpTzfxLnJkRx3++DaHXnfvjdzTwSM1N24eMTt3ejCgZffqP3xL5C8sk2Y'
        b'WXtSxH+A+WHQFdkcb2UD4/mUj+tscIHTXrToQSCKXsGNmIzlUJ4JZWs5LkDfxuQ9Di41lMKuMsQWi/g8sI9yBfvYm8FhtwdBeJbugK/HauFFTCxLi8EViuJnsYPAmQBS'
        b'Mnh1Pnh+gSfoqkS8L5fiwX4WvBUIrpGS4RWwuzxeXIT5ZTT7U67wJhvsgQfgLRFv+gHIs8zMZNyNu9bUKFQKbU1Nuw+DQBJLAJl7dRQz92rZVELS8LzRAGN8nsE3tpvb'
        b'69m33iQM7C29J4y6K4waWG8QJhuFySN5BmF6N8sUNqd/w9CcoeShOf0tKLGHKXQ2+nE3CQLQCPSLRjmPl/aUDnANwiijMGrM8p3goEiSQi2wzkT8ca5GrmwY52Lpbdyl'
        b'Ta7WIEFPjeUF9UxrvTDy1NbiqYWZUObgCWVqndbilGoypZBJRcNmscLxnDC9811NFp9jfD7uJqaueOdy6tnOhma7dWgyA7OBTYYl2wm/yXFzwkE6DlQ09NjbOeZh6TTO'
        b'Oiybpg5LK1h2w1IXhzHvQOFMD4RoXQjluxLhoaqipXCAQfFlSwkDugCe5fvlgqcVnb6JLM0ilOfX/h+cejsNDdizR5LRkH07sGtPSd+v1+0Vfr9ib1wGf698v6fn5SDp'
        b'ufL9C+d9pi5L+i925BeuY50XYvp2pnpRXxk8TnTzRVxmzDz75GLriKJclySRAdUPrj+g8ZjpjJoJbyCu6BA8JBG3mhmfYLCXtZ0Lnt5KkyLAC3GwzzqsWpeSgQUuw+4H'
        b'uMr54AjYrwTnSyvFLIrdxspLyhGxbcYQ7j3LAEJEsVGuVWjlzWgMzbDimzWMDKNc8zBaxKGEgX3a/ifHBHHo+35w1Fh0zmi1ITrPEJxvDM4fE+abAkJ6249v79k+IDME'
        b'xBsD4sd8420GA0+NJdlxrkraLJ86BHhkCFhHgBiPACcQ4V7WKJlBgGAq4LBYgRjVnTrfKfofdYunLntnc/5DKZODOPyQIeAFd/nZDwEr/gfDQ9YhMB/cVgz9ZD0zBI7M'
        b'aGBo1jcOgdNlCx8vS9oes9urSPzHpwuSOI051CeJ7mP/96mIQ/DXF+wqYoYA2AX2kmGAB0GG6kE4xu7uNQLrEJgLz0+OAjwE4P7WBxhzErmhlhGwIp4hLb5iEWcqweAQ'
        b'ZJ/Edo0TbNfYYXu2GdsrHgHbIzAtce9LM/jSY+RrO/ETXFdj8X6c1yZV6hwwfuqkn26P8lawmij7eb8c4fxsjN/TO98V4quj0Wudz/cE4TnW+R5rHKgG7r9xzndgxXhO'
        b'EJ5XQRQs8OVVIVgDVw31YrFkWVHJCqivrIrFwuUKCtwuQlK+hEVp4atufHilUhePs5yGVwTTDBI8QsDttWSQcOELijcTN3E0CpSp8Q/Vp95OITL/y0euHVEECRipv+5v'
        b'Mwr5WUXSdfzfXNnblZbclnIr6c23f+65MsWYpL0ue+N7P8LDafXhB8nvJlVfS04a+PiPhzkf1e39NGAkqZZ1uqktJWUwiZvaiphH0Q7hwc++hwRxrDasj3H3IBIyB+63'
        b'E5JBN7zGkJt9yzZMkps5aoZ/ewacJuSGA3Z52pKbVHDEZqwVBhBWrREeAc+SwYaS7rVyclHwPGHzYBciSGZOjooDexlOrmnDN/JxVvlpnK9rxQJ1u5cZ+ZlHMhy3mYfj'
        b'ag4VOKe7fSByiGsIEBsDxJjRymO9jyXEBYbghcbghWPChaZZ9ATF9lvCYtzuRYggDaQN5o4FSND3/TDRWNz8O0JD3GJDWKExrHAssHAClZt431fY637PN/yub/hApME3'
        b'xugbM2b52gxpF2ZIYx3rlLFsUzUXykzHLMLhfDys7WvWjBO2URYituqhROy7J2fMqLbVItpzcRyiRST6XzMJw1pDzr9ca/hIXBynQjHvjQKeBs+Kq9/7ANOk8KfD+46e'
        b'PowG3bNHxIg2HUtOSRpu2PPppdVBgeuDdnzWephX5rn6Tgr9hNfvX05689Kb1Lvvpvw8JfzUqzuCTv1XcGF17oYTG/rWB67va97xSdiKgf9dvWFsnf+P75zgU8OBwqpf'
        b'SBHrRmSWfjgILppHUyZ41kK48lqJQmpFLRjBw2QZODcp71TXkjj4SvVW2JVQ7NUMD4j5FP8JdgR4HfF8GI0EpeFEgBJEWEUoQQJCtkdQSGBko2kbicgF0Q2tGpE370k6'
        b'gp/JWGoxj6UmDhUyu2/mQAT6kw1uMMxJMc5JMQSldPNNETGDOfciUu9GpBoi0o0R6XgcRRPncGn3or4oU+Csfo97gaK7gaKhSENgojEwsTvPREdZVTwBkd3bBlYaAhKM'
        b'AQljvgmOBHHagUPIoc24WYzHzZRqYIlO00qZtSqNaNzMwCNjeuc7GzKJuArsCjWeU0VeWPLETGxNzbh7TQ2zmof8njU1G3VSJRPDkH7XejTeG1vUW8ZdzbKfRh1F5rwG'
        b'hVwp0xBRj3C7hP6T2YJU/ZumTxv1E56F280qlCoc/ybT0Za/+4IAPZ4J9UWmgCDkzAzWLzH5B+gLJ7h8L9S70zm+HK+ECcqJ487xEmGfg+PO94rFeR/i+PK80Nz9aA7B'
        b'Hh1u8rVgH7jgUVIODyaCE+BkCYty9WTXwittDhwA/nxei6cx1hTFFXsNV8aRcWW8fvYaHpvqpWT8AT7l5CNzsV/stX9a4yJzJWort3H+YhXi0bZ8LVwkr1NoW9RyVWKp'
        b'Wi5jvB/6EpT5EE9iX89YKVe36xo1rVKdpr5JqpTTqSgKw/u1Z5lc266V04VqhUZ7kU0w7MPvowH7xYkZFFXaotK25FYgjKJj82RquUaD8Eml3dJKr1Bp5WqVvKlZrhLl'
        b'2jxoGuWNyNVKVTKn+VRSLbytVkropQgfW1DelS1q1aOkc1bYBrlCJafzVI3SOrko1y4ut1Snbq+Tt8sV9U0qnaoxd/EKcRkGCv2uqNKKi2UVaklungo1mDy3GrG6ysS8'
        b'DVKZhF6ilspQUXKlBjPASvJelaatRY1Kbre8Q63NrdKqpfCMPHdpi0bbIK1vIh6lXKFtlzYpcytRCvI61PIa9Nuus8lueajbhKHDelvaDAgKktBrdBr0YqUN8HTytDEp'
        b'uaVylapdQpe2qFHZrS2oNFW7lLxHbn6fnF4Cbyu1ika6rUXlEFan0ORWy5XyBhSXL0ei8QZcbqw5SGSJo5fIEe7AwQatBtcSN6ljanpJmSh3sbhcqlDaxjIhotxiBk+0'
        b'tnGWMFFuoXSzbQR6FOVWoRkLASm3jbCEiXLzpaoNliZHbYQf7VsNh2zAOCyu0DWjAlBQGRzEivINuNWY5keBxfl5FThOLlc3oHkReatWFRdWiwtaUN+YG5+MBYWqCeEa'
        b'Lsfc7EVSXatWjN+DJtg6ifmdZr9duzsLx21vV4kUh0qkOFYixVklUphKpExWIsW2EilOKpEyXSVSbIBNmaYSKdNXItWhEqmOlUh1VolUphKpk5VIta1EqpNKpE5XiVQb'
        b'YFOnqUTq9JVIc6hEmmMl0pxVIo2pRNpkJdJsK5HmpBJp01UizQbYtGkqkTZ9JdIdKpHuWIl0Z5VIZyqRPlmJdNtKpDupRPp0lUi3ATZ9mkqk21ViciCi8aRWyBukzPy4'
        b'RK2DZxpa1M1oYi7V4alOReqAZmO5Dk0j5odWNZqQ0eyn0rSq5fVNrWi+VqFwNBdr1XItToHi6+RSdR1qKPS4SIG5I7mYIXd5Og0mKO2IQ8pdBQeb1KjdNBryAjzrMTRW'
        b'qWhWaOlYM+kV5a5BzY3T1aFIVSNOVwgHlUpFI6JRWlqhoquliC7aZKgifYBjlpLFXdvCJsm4eA2CAk0YsTi7XYQ5P4qKcsyQMn2GFKcZUul8tU6Loh3zkfi06QtMc1pg'
        b'+vQZ0kmGcilDl0mbI74E8SckTCvfrLV60Exk9abaJtVYkzEdkS9H5LjRJiAqd41ChXoD9z95D45qR0GY9KJZ2u4xxf4RTT9SjRZRO7WiQYuxpkHahOBHiVQyKQJGVYfQ'
        b'1trjWjUcbERIVKySKdokdCFDP2yfUuyeUu2e0uye0u2eMuyeMu2esuyesu3fnmT/aA9Nsj04yfbwJNsDlJzuhE2hY5ebW1VjZjREk4yRs0gzr+QsysI+TRdnncqcxFc6'
        b'fxvmu5yF27Fi09fhIfHTcWf/SOKU6d9sx6c9SjI0VTpLZkcCMhxIQIYjCchwRgIyGBKQMTkbZ9iSgAwnJCBjOhKQYTPVZ0xDAjKmp2OZDpXIdKxEprNKZDKVyJysRKZt'
        b'JTKdVCJzukpk2gCbOU0lMqevRJZDJbIcK5HlrBJZTCWyJiuRZVuJLCeVyJquElk2wGZNU4ms6SuR7VCJbMdKZDurRDZTiezJSmTbViLbSSWyp6tEtg2w2dNUInv6SqAJ'
        b'0kFWSHIiLCQ5lRaSzOJCkg2bkmQnMCQ5kxiSphUZkmxlg6TphIYku/qYQSxUy5tlmi1olmlG87amRdmGOIncqsVL88SEWmk1ankDIoIqTPOcBqc4D051HpzmPDjdeXCG'
        b'8+BM58FZzoOzp6lOEp7QN6jg7dYGrVxDVy6trDIzcJiYa1rlSB5mmMlJYm4TaiHfNkFL5HXwNqb0U9iGRibczDVYnlLsnlJzl5qVKzaZHdQuyY5BKY5BSMxRYqFYqsV8'
        b'KV2lQ8VJm+WIjEq1Og1ma5na0M1SlQ6RF7pRzqApIofO1AAimywKTNwVMpLtGxM7Kd8JUXJetmNComKabB0aMd+0meUlTdmA482NzPhTbPxYJpzUVH3Nyq246KouxArI'
        b'JdgposzLnepi7JRgJSdP06pUaNWlWBPGYnSXWI9m1luWE70lo0PD6zyaFVP1liKstwzSF03wqZmJJv/YCRduoPcEhRwU5k7NDOleMcFN8itgfVnHonyE++TdBZ3r96//'
        b'tJGVOjP4AYUcfSH+m1Qk5mwFwxq8b7UzAZxOBhe5lGsGezs4Sv2/pkhsELmNu+fV17foUEOoGse98xG2MQKPtFWu/NCfUSNiHfrXwYsQ/jUjpgbrxGlG5EKjR4HmPJQE'
        b'7+gb52LmS12NvF/cRgErmhleqqVJJaerWpTKxCI0GarEpe1YtTP5ODm95q4qXUMz2bAKD0/cGoVGxwTgONtnZrgvwRpHRrRgXpS/QlxV36SEtxHaKRE7ZPuYmy9Xyhtl'
        b'uCKM16zvmfSnmEWzXEtLEFED86Jy86xikRdphh8zS52T+jGzvEmkBCxposRoXGuJRGIugbxOqUAJiE+hamihxXSeWmsBxRxSrMI5pwTiZCnOkqU4JEt1lizVIVmas2Rp'
        b'DsnSnSVLd0iW4SxZhkOyTGfJMh2SZTlLhtibyqrqZBRQynQMZrPlJDDFIRA90OVyNFVblMC0TkJPKoFRIIPLFq2shMaigkXgZ7S9k91Il8WX5RbqVBvImSm5uhHNje14'
        b'PsPh+SvotGyGwjdYkmBttLNwM94wUU4KzF1DJBFccXWzFEdaUcRZjBVVpsuW8rBsziMZFHpINueRDEo9JJvzSAbFHpLNeSSDcg/J5jySQcGHZHMeyaDkQ7I5j8TZsh+W'
        b'zXkk6e6kh/a381iS8eGIMj2mJD8UVaaJJRkfiizTxJKMD0WXaWJJxocizDSxJONDUWaaWJLxoUgzTSzJ+FC0mSaWZHwo4kwTS0b8QzEHxVZp4e36DYh0bULEV0t44k1y'
        b'hUaeW4hI/OTsh6ZDqUopxWpNzXppkxqV2ihHKVRyzI9N6jnNlBNPeHm6BqyRs05yFlqKovDMO0mQ6dg8VTvDi+OlRDQZlyu0iDTKZYgDkWqnRE+Zhx0zT87kU+PUSvii'
        b'xswm2MUUkYWlBi3iSqwSHaEkYsLvOBU/zDU1U3NE+hGlwdx7A+HbmzGB18oVqFm0VhV1MWKytYoGxQap7ey/hkigVtW1LZvByK02S5i2bFKhnBFq5Io6HFWGeg2vyWkY'
        b'zmZ6Rs1WLY3gRm+WKnXNG+RNFh06IYKEi1uFuLgK9Wrn3DPeDt5uwzjexvHLp3LQETYcdKbJn3bKQQf6zf0yxZZ/zgzB7HOIPfs8GzmPwUGwUwNegs+WVcCDiYSRhvtL'
        b'XSj/Oq5nqv1qvKeFiY5mIyZaaM9EI7aZ3+vR6yFj9wp6BZidHuZdQDzuZRdLdjf0J4vU8/ReekEDR+axx81+89AaLj7GLfPcQ8m8hr0voHdctm5UXMMncT4oztchzoXE'
        b'+aG4GQ5xriROgOKEDnFuJM4fxc10iHMncQEoLtAhzoPEBaG4YIc4T1y/BrYsZI/rGi9zmwim/LkNz7rgjnK527VMlJ5tbhuuLNShbbwt7dvr3stqwG3sQlxLiWEXkGxw'
        b'2W2yRFm0ntnGiQ/5+qJSXWSzHUr1kcWgVDy9KzkMPIOkove4rfFFYX6oFuGoFn7kzYLhOfbCjvlAsbfep4Eni9jjOqXkGeY9FbHjrovw0bqCqpVfJ7rTNh9LMM3Mo8wp'
        b'ebsUF3nqpXhg4DHwIZbH1E9gH967TeQhkeeHGJwPcet/iDcGTyZXN1qSq/G+MnUtToLb+0N8vvZDjMkil3F3qawNTc3qGoVs3K0eTZAqLfZ6S5kxWKNEHK62ady1Xofm'
        b'DlX9lnFXfHBDIVWat/x4NCgQU1vTjOatJvLucc7iFcuZPUVqvH203pWa/ODXk81vxyjLTlvb4/zknC8LIQFX74Ialjnly29wJ/v1EBp3uk/Zr+dG9uu5OuzXc3PYk+e6'
        b'3c28X89pnO0O3C+OoIa06wX8KWaqrWiXa4gxBGvfKci+lHq5xCGLQ0AOkuGkzfRkk+eYzSCgeRpr88x2FsxtL1VpHUrAn9h8NL1qLZO7SELn4fxoIq6nyZ5sWtdKI3KU'
        b'ScsUjQqtxhEuMxjW3nYOBRPtHALrmtU3wJD+TTDYo1kOXUZ+MQhLEssssWbANM5hwcQbk01EdCV0dRMipGg0yWmNrk4plzWi+jxSKcyGIEbiRyXRUlQEembgp5UtiKir'
        b'JXSxlm7WIbmvTu60FKm58nVy7SY5XrOnY2XyBqlOqRURKxhZ0/eFeXjl0AVmH12Plb6x1qViG2WxaLpSLEMzx4KtGmtnYqMbLWo6ltl4tAHeVrfLldMWZN7Wl0NEVsze'
        b'oWIYHDHPVLHyRgmdnpyUQGcmJ01bjM3ckEMX4geaPODiGhQqNGoQjPQWuRQBFqeSb8Lr1m0ZkjRJcpzIsam+cWO8J3NG8Z1qP2pW+CKKaq1VHpfPo3TzUGAIvAEOwK5y'
        b'MLwU6ovhgdJE2Il8YEdDZVVRmQh2JVSIwT54qGxZEbhSVFFeXlzOouBhMODZUppAit3r40XRVakUtbRW+fPtuZQOH4ddCm+CvY7FojLhQdhZBgfhMcRPgM6pBe/Z4kkt'
        b'gVdJwbvq3Sj9jHC8xTrBn0qgmBNdl8BFuN/2xH6RRBxXAg/Ak+BUKbjKpTLW8TVwJ+gnBgdIQWuW8ammpSEURdcmJK1fT+nwxkt4Be4B152BCPX4BQkYzP2ilTbQgZfV'
        b'BfEe4Ppj4AXF7/40zNIMoHKMf3A9cCjXnZ3su7Dxs5+u2ZzlM1K+UBviV1mb6eL7yysv/qI0R5TS41NH78l0+9Phew/4+37TGNvV7eYhon+Q66ua+0v5E1Xge7/5fPvW'
        b'1X55y7+4HNNT99If3/voubU+71/QfPzundrm21/+6U9/TTj2XsxT/qpbbYbdVz++9ee9P3z+j8+/2DIOynM9/z7rlba2Vzr4n4ZcWP2Hnj9d2Oddt0vw5ucusCI17Hv5'
        b'Ik9yegC8iBoHdCXaHP/0iYKvLuE0tIEXHuDduvAauJEJuiptOx31yD54PBju5rYjPDnGGAQ4DfoKPVDji8p1FRLzSQR/0MF1XelBDvVo4SuwAxXE9PSBJQ1MP7OomeFc'
        b'D7gL7CC7pH3hefhSvDgW7ogtErMpPjjJFmvgSWIRINKbnHljOpZ06gwangdXObALHFE/wDuKwzeA/fESUR7cCfclUCj7MDt1NvsB3mELDyP83Q26sLUAaz/yqRngIK+N'
        b'A151hecfxKBkpdGgB1fXzNtiGBEWwH54CmMCRSXBp/mSmX6kbR73J2lRaXEScFWC06Kkh+JxOlrD8wJ6BfPqXvg8uIlTEq0zerUYvbgJoeNxDnwaods5UhzKfwQesHm5'
        b'mbH2yQoGo1zQxYedIvdvcWYdsxFTz6uT46V+Fqpsf2jWy2ywoM2FCsfHm7xMEeJurtGXNglmdqd2a7o1fTmHn+p9yiCIMQpihsLvCuLHBPHvB0eORRUZgouNwcVjwmLT'
        b'nHiU1WcyS/bh7b3bDYJooyB6yO+u+UQVyrLEEFxkDC4aExaZwkXPhZ0LM4QnG8OTUWZvJrPWms32TZmG4CxjcNaYMMs0J25AMlR3LzzzbnimITzbGJ7tLLPtOwsNwUuM'
        b'wUvGhEvux6TjqkWaIhPxb7gpPIJkjogiNXY40+XFbGHH++jVeBe6eiN28NEstQY7mMtTa6mH7XLHtiVqzR+bze7T9MiHOMsQxRz9+sp8/qvShcWqZ+Ht7d+d+51aFTjv'
        b'lk297J3nwrE7Y8KyUKEZhAptpdZbo8gqCKtCxBr3qJlk+JDMi5ubyLw0aaavXecqpc11Mul8m7ayBPmhdOT1O6i+amOoeAdFeu5rMzE2l2th3GIRkZeJW1TKLaKLrHGO'
        b'rKX+HwB2DwOse42VLXSEVd1h36UWMIUoCTlPisHsr7FAOZuBkinQCZD/AHSNDHQ+NfYM46ODGGDfkskWGEUP5Ti/JbRNDLRuNRa27tHhDLZryicsYAblSzVyK5f4LcFq'
        b'sIBl4RMfHaxQlETdixMQcCKm5S//GcBca8x856PDReNutTbX45bmipiWb/1nsM+zxoahfXQYI3CXTqKexIp638ARTwOq9QDZZuQcZZvPtVlsE/x7TrU5nFOd5lTb4MJg'
        b'rgavn0sXB596O02fS46RMqetLSfaBq7vN8kv78jq23mDRxVfcpXcPSZiE/bIKxPsJzyGBpy3YTMIj5Ge+IDYtboCT2F+r7IMHgc77bkMhseAF5OnNRXgUoPnkZqadl8b'
        b'KkVCCNuA+XBMnErcqMAQRPDT+ucbAuKMAXFDVUNVI0Jjcp5BnG8U5xsC8sd88x1sAjgjmIxJAEwkGZQZxCjj8PZojNUbKPORsGK3f8dpMDLp9LrFUZe8szgi93EX81TI'
        b'HPnia7RquVw77traotFiyXScW6/Qbhl3YdJsGee3SYniyKMeycctzYxCiaOVNo7zWtAEoa73sMEWbwu24Oof5Tq36ojQ2st8CNtV76Nn690xmut99Ry9m96lwZuguwdC'
        b'd+8p6O5J0N3DAd09HVDaY7unGd2dxtkphd7nOVEK5clkGiT1Y9FVJq/DEyD61pv3JtNysgvkEfRCRGtBVA5SuknXKLfRxKD21ijqlNg2Jj5ah5UqGrlWQleiecGhHDwT'
        b'N+N1aUVza4saK5As2eqlKrpOjrPSMoVaXq9VbqHrtuAMDoVI26QKpRS/kgjxeGe7RoJrqsArDGh2MhdpVoTgMh3KQEXrNApVI4HIWgwdR1Ah7hFapNBc2yasFXWE3SF9'
        b'rFaqbkTvkFmme5yfxmsmGqxU0GzU4datU0vrN8i1GlHOo+vqmFGQQ+fZcQb0WrJL5PHpsuE359DkdNnabzxjNm0pzKDLoavIL73WvON52vSWwZlD4xUf1FVEh7TWdsfz'
        b'tHnxcM6hC5BLr61Ua6dPxwx4lJTxkHck0MVVleLU5IwMei1e5Zk2NzNL5NAr86rFxYvoteatE4/Hr7U9QTf9yycnF6wpYx5oXJDtuY1ps6PpCDVmExoaaLhq6tWKVq2Z'
        b'ScB4iq0ZkbGVp9S0IPyVy5wq+RA64dSYWiuJxVrS2RJ6EaPpI0N0TpVW2tyMj8Wr5kyr8yODASEWAqDVPLRkCmIzV4qadZMCcQXyzajHzQPOsRz8qWjRyplhQga/XNvU'
        b'IkMzSaOuGSEagkW6AQ1ANGjkqHXq5XQL4rCclsNUCQ8aosLUMNVUaGxAktCFaFKzTEhOS7EddljhiVAdWwSuV6IKM8aANXLnOWvN9oBb6gnkzKLy3CattlWTk5i4adMm'
        b'xjyhRCZPlKmU8s0tzYmMXJEobW1NVKDO3yxp0jYrIxItRSQmJyWlpqQkJy5KzkpKTktLSstKTUtOSs9MzZ5fW/Mt1IszKohZWznXTVMmKhFLKhKKsT7lYgJFRcLBNVW8'
        b'pu0CYkIT3noCXExFnuRWqKeS4SvweaKfi6niUjebhRS1sNbzzDoZpcvCzML8haUW9cgyqMfGJ0vEy7E9DnixZXkstmOxCurxD2JpsL1QN3gU7oO3dERH1eUOr8Ib8CDR'
        b'0bhQPHgCdsE9bM8s2KvDFhEWwmHQAW9I4IFSrPTpQsWjF4BRuFfMpmaDZ7nwVgS4qVuIoT6wwhPeKIX7y1fA7lZzDeELcIe5lkuhvgLl3l+6ohU5lWUl8CiXgvvALg84'
        b'CPrBLR02J6AAJ2CPh0RUAm6ngy5wxp1yK2HDM+B0OdmpiEDdswLeKEYFsNrBixQHHGeBHXAgiRj5hYfBzg0eUJ8ogZ3opQngYgncj6IPQD2LopfwuOB1BWNZ9RXwGnwG'
        b'3kgEl+DBOBbFLmJlwFMrSCMfSHGhhlYFYyVo2WOJlYyxYtjlN0cDzsLLXqjxXiCvp1zXsZfAmxvJm/3AS0CvQZFeXhJ4GL5QBq/Fwz3gCOzhUAFbOGC4HfSRtWJ4Eg7W'
        b'eYAr9RJUCGrJYowDHMofvsz1mQdOKjZuv8jWAJQwXLWneazUHSz05N+XhW1bcOf0M99bu/npHQMhoqslHou1hzn6X1699WnPhYjQjX9Y+KPM/4sJutv4BZsnjxrO+u1f'
        b'uT86KbyzVvxKWA793tfakcHfJT55zfj9z4TDMb3BD0L/1nb3l6e08X+6ceJ95dWfv8RLGf5l7PCr4RtefucnL22M3Nc/Y9kn1ftmxMSXnE5Z9jvZoper3v9kNHrgg7Pb'
        b'bxSt2V4V57prUF2sy7v0ZG/Qg54D/JUrO35w/6cH2r5YlxTOfoN1939dTgwkxdb+RcQnalB+RCijTkV9/PSkSpXTAPukDzCKwR3JUQwGb0bRVgUjo1yMT+XBQ/AVwFhA'
        b'zc2GRz3cwQCjVLVVqYIL4CJRqsLDueEWvSK8BXbbMf3wNagnWt4s+OqT8TLE8IuLi8tLE+ABEYuaCW9zU8AA3EEsuESCfaCjNCG2CB5YFIV7G1xmbwGdMSLff8aMqlNt'
        b'JHbsDGhaLVe4S2WyGoYLbBdYmfzJQDvlZJk7FUz3zRzgDWgHtxmC0o1B6d18kyCoL9GI9XwpJklyd2HfAoMwflIFmXl4a+9WgyDSKIgc0BpjckaXGWLm3xXMHxPMJ2rB'
        b'gjuNhqhyQ3CFMbhiTFhhmiPq5ndvOuxjEqUhz3aDb7Rpfn43fywgx+Cba4qMQ4FbDFhnGIt8bYe9TaJkSzo6Evl0h70QRNh2RpYpVjKkHmENqYex4dVsgzDKJE4dyRvJ'
        b'H8kfXoNC5huEcaaZQWMzRX3rujkmX2Gv9z1f0V1f0VDEkNrgm2L0Tbnnm33XN3s02uCbZ/TNG7N8bQQpP0aQwsw5sw37Oexg5aH6InawcW81ZtvVw9i5gp2r04heNj2G'
        b'O6d28kNPmu1Rj2KBzFlfibBMBikbtaVZc+n23Wsu/+UaTSyMXXLLo6g3KO88b47IbdxThvfMm7ndcS9GhrE88qXN5BcbfJSPu5m3K9XLxz0wx4n4fLyZmekHaxfUW7d2'
        b'oI+vhZzinjzq4kzgO04seiPhDq/+s4hFdje9HxL+sMV2Yra/wZeIfO5ORD4PIvK5O4h8Hg5inft2D7PI5zTOTuQ75PJwkU9q3adEMwZyH0GwWYxPJTKpacRdIfxCMgvi'
        b'GKW2FyJgrjKBblS36FpRLBKmpI7cSktznUIltfCvcYi1jSOMF8N3YZWc9RgGBtCqXHIoCSub/n8Z9f/LMqrt0M3BHcWEWJXZ3yCr2o11Jj8TZCnAKcO+9hsOSEz7OmYu'
        b'Yd5jnj7MYYzMo2rBOlE1kWpUzmWVTS1YqFA0S5XTSEVrH3JEBMmazg+JTAsxnvUYeOtaWjZgeHGIhC43Y5eUPNMtdetRx9MtzgUshCBIRs7KSEo266IxIiABHxe3dvL4'
        b'yLRAWCfdHHqFRidVKsnIQIjT1qKot47GtTanTx6qJjBP2vbdQE7Er7U9ofKNgjzOPkWYtzsH8R8gi+fLN8kbzbtY/395/D9AHk/NSErJykpKTU1LTU/NyEhPdiqP48/D'
        b'hXS+EyGdZvYAhSp5+HYT30Ultcrax1IpHTZEBq6DM+tLi8vhvoTisopULDcTqRsL21Ml7afAq25p4Ap8kciP25C8ecRGzi4At5GozfYE1zJ0GSg+zgfqSyUl5bATl2xT'
        b'LNSDsw5CfBfscgPPaXLJDiLYsdwbXvPSVJZXmg1z4lesgt0o/SFU6opWdySWojLR88tV65AUdhKcd6PAZXjMo6JNTVQS1eDZIk0JPFBcXlmKrXmmwaNJXCownwP3ewp0'
        b'NErhDk7GwNvwsCauHB6MxdKZpBhciWVRsxt5PDBaRopxcUnxgC+Bg8td4QFxRS04jyRwNjUjlQPOeiwh6gRwFvTD06ghJnclIQkYvLAcXyPiPicZdPE2L+ATSTkgD75k'
        b'hqk4Adz2EuE7SYTwPAe+goT6YdJLMJWNV46STlK1Cal0IUWuO0EiXA+86MGHFzmoZlR1fhVpYrAXDD7ugZsHNeNh+FJRGd4MdQS+gJUSXag5XstBAWXwYBEWyNcFuS5B'
        b'svqrOszUs9vAdXiDqgUdFFVMFUuSmPdcYsOTqRQ8VUFRyVSyHHYQ5U3KNnAVHkEiP7hO4etWaLBH+dXf//73pCiCUZv/a0lt2V/nxTI7rnpWkTt4lm4X1Xq2uYZRRJGy'
        b'ItwFN84Bs0anKGElvoYpAB5PLFmBUKEI7q+KFSGEKGJuXipHwjB4kbQgX+X1+OYndMQC6XVw48kqeHQ2uJBawqFYcJiCw3C4gmxm4yI888B9hDpo+SSmuFpaB3T62DQQ'
        b'qk8PlwIdK9weAzfBBR02+4dNz1Vr8EVRNywakWWx8GiVq43+o4dDLfDne8Nn4PPktqbV8OZyTYm4sjwR409FcQJ8FjxH1B8i2McDN4PANaLkyQXnCuNLQIcHtmxXIuJT'
        b'HuB1NryxOZFcGOSVU8F+k09tHiluTpDKl81xZzbS5ZYjzLph1n4xG+gQfsHOxMryZbElTEmWPWrovbvJLrrT4DlP2A1eAb2kzcAgeC00XlKcEMeiwuEwHxxiJ6IhfE4n'
        b'xA062hycGYuGRymLYqtZWfAZcFnEIZdcNae6mXPB0S0kVx28ymQ6C08ugk+3TmbTeZIJATy7bn58iQs4ZV9HMATOKIqOZnM125C4WCx5cGV5aQVM8v0is/NnNSdnloiU'
        b'WYXvrqVVSXHL48OFcTOP3pA2/lnv1XX11q97yvpzDuz+hVRkOPXpqV+FPCU7s8cv4p07+zPfPB0R8ZtT2ZeHA7f9VX0kTPRfY3t//1jf2TcWfvnVr/a5B/ylIuOiW9KR'
        b'P55XfRKSfjH6zir9qfU/XFAtiHZbWTpycvjSCc9lMoPrstuXNJofLK5Rf3SpsfeH25r3hX3dUfiXv/zq6LJEj+d95DEfTew6LRruG5fU/aH54zi/B4bcoduVM/Z6/7L/'
        b'2plf00X377zVeFSYUl5TfG3Y+PMH9O5lJ2bz/nuL5t7LP9z9UWWa1zujIf3Zqxfsutj51OdbPRpfG7lU5qG40PT4mtLmDxqi9678IOG9s+qvBs8ZPWtK1p840uh+ow38'
        b'/mbDhifU7yRLdPONvz/bvGH7M68LV2azVj21PuVXa8T7DKqf3/1NzshGVpdm5kufj7ds2t74aXlX1WXxhtd/K/sq592Inb9MfMJd/NfX4vf+6uOzlewlmxoGuG/NW/bx'
        b'7Nuu2z9bEinyIvZN5/u6gK7Eygq7/YCcBgXsJ8qrfLgPvFY6ZW9cKbwCBifVV2VsoghbuAic8LBortbD/knllWweMUucB07AM6WSrS2T2/l8VnKUlUuYmyNeidneDs7H'
        b'x0lEZCef22Ns8GwbGGQsGg9XwNPxEkwiElgUOAAP8cFBtnibH7F+D/a6VYGrS0vL4vgU+3FWJjywlGwtLAWjCOUul62oLE9AE2kpCxG4F8AoeZ2oqBoRE8vevTYVfys7'
        b'Bk0gZ8n2Pc4M8PxyN+tGv6m7/ODzYqKLaylsmrJ3rxjesC6sL4XDD/BEz4evpmjwwBRjOkda2C8sH3ZzwAhWNpO7k+A+eB4eAE8j+kdUchaFHHxdKvL/rhVy02vq8GAn'
        b'bMSOHc7Udd5Y2zMp1LcH2KmBJiOI2u5FNqO22+5BBUf2BQ8sHkobnmcIyjYGZWO1nUVDN9cQEGsMiDUIREaBaGiRMWHBnXBDQsFdQcGYoIDo6PLulBmilhqClxmDl40J'
        b'l5nmSMw6OmsZ8wwBImOAyCCIMwrihqqN4oV3kg3iRXcFi8YEi0gZ+XceN0QtNwRXGYOrxoRVprnFWKmXZfDNNsViDd42g2+Ujc4vJn5wG/JvNfhGmgSh3Tl9soECgyDW'
        b'KIjFFqgTTSGxffOGhIYQiTFEQuxN4+DFLGab4mgE+pO9LLotMkTZXF0UE28tMagvryenO8eUmdNdOBaSahCmjQnT7k8+mULpvqqBmSfW9q+9F5p4NzRxhGMITTOGpnW7'
        b'o0r3xY0JItF3SID+1twTz7srnjdaz+y0uJNiFBcaREuMoiVvhd8VlY6JSglQZW+1G6IeMwSvMQavGROueT8rd3TJ6JI7hW+tfKPSMLfaOLfakLXCmLUCt0qawTedKDFZ'
        b'fnNN6bkYqGSDMOV+eNRgULe3SRDQmzPANdLJdwXJY4JkU1TqiNQQldldYQoIxia3wyQj3Jtuo/PHZpZ0czC4kcbgOMaevilsjjFMMqQxhqV2L0HJsYJ2INsYIjYESIwB'
        b'kpGouwGZYwGZ74fFjMWWGcLKjWHlY4Hl9wNC+hoHGlHOu8Sityk+sc9lwMUQGDsWGGsKCh1wGeINet8NkowFSUwiMYrjnfD+6n5swkj1nbqxsGL0RW9LSO1eZBRGDlQZ'
        b'hCKTb0Cfm9F3jlnfGm3wTTb6Jo9Zvjb6VQGjX30ZO7ew8wp28Kk79avYeY2y6FcfUbU6dcThV01VtFp1rT9FzrSDbA3Wt/6EstO3ouG20Z3FUhB16L/X/U5Vr5fd8ljU'
        b'GyzvPB9OvcUsB/5YLz7soezVpMcpvYveTc8lVx+y9Z7kyikvPct8ASKPTXVOOQS1jU9UojwHlSjfQe3J2843q0Sdxk2/6cuZ/OXNyF87NMw9lEtTVZ6d2/KpahKalUN4'
        b'aHqgqiVBXrCIuSYRMe8712vAAdeNHIrjzQLHweks+EodWZfbDPvBUJVWDA5UwwMrypfBF5bCF1Z4ZSQlIREvgAN2bob7iegCzmwEvVXgFD5uUZ2eBPelIQHIdSMLDsD9'
        b'q8lSKSJd8NkqcA6+bi6MRfHiWEiYeg50EClBOG8+uAF2rEaVmUvNRVwB4QDBM7B3AzwfCS7BZ9GMH00FBmgYBv0w7IDHS1fBFyVJaSnpbIq/nQWeyY8ikU3Z8Jn4kkXR'
        b'5tsCzVcFakoV2fybLE04Qu2L8l+drnpFBZM8ByNLt3//0LWCHX+u+Zr3P+8dKKICinYe3PmAxb4lc73V/lnPmYSf/Xzfb0vC1u/wrbgdcei6VrLgjQbOntcOf/BBN8v7'
        b'xZv+13NfavzZYUFH5Vev3ij/af8uP3U2PByysSn9x0F7fueZlK9Z+2Xd+JP/dzE+vWBjwtV982rVdW8WR3uH/3RF4vkg/3cGX/J857GmwOtjJwZm/fD/vld+/7wALu7+'
        b'6daf3/ijx+s+ce/87vM/frXs/66U7P9s783Nv3zihRc7N5fdm5ez7W8LXv2f10JXPLH46wWvx3++cvGPy/+6Nf9TbvQvdh9e4617a/aWX/1B9o7oy4jdfTNvnHX7n0RV'
        b'QcjVVz6pu7xk88uZ67+nuPxu+4FDLj+Gzzz44KrX463n2KV/959f8Nr/su9+2RydOCqaQc4/NFHwMsKQbsS7dCW6UGxwjrWiuIiwPy1afENQmZn3KUeoch3sgScIwzEX'
        b'PIs4NCsDBG9GUZgDAkfAlQcYsULgKDwCusCOiml4oIVghBTkC3d6o3THChOncJApmYz9/J5lqtLH8V6AcngoEVziUt7gNU4N2JVN2DAJOI/ks65SciMkN4wFXoND4FzF'
        b'SlI2eAmeB91Ikr4aaXtZGcdlrg9zAmWEA56JDyqxuVSSuVHyMNhBWC94AbzYUmpzkAUMleLzJ+AKNyQGHiNLpQW+fqXkhMrsxy0nkVjUjPVYwN3ZSNqiODfRjgOGvYvt'
        b'12/Xgj2kKCHcA5+DXXSQ3XkTnzDOE+BQC8PnjcLnNpSCS20Sex4YDGaSLgMdueWl28AJOyZwZRzhgTeBC9mTl19ys1lw8AlwDe7UkIacD8+BHaXBqZO3TOFbCpoWM9d1'
        b'XIkNKV0ObmDW/WBlMZpkQDe7xWOOaMa/kJnEOgSzVsqBk3SpYS5OtN3ayYQQ3vFdM++42osKmH1c2aM8rOpVYW4C82KNA9L+9UNxBkG6UZCO762cbQqh+3MQHzYrvL+0'
        b'e7EpOKy7oLvgfkhYfxYOnN1fbA40CQL70owhCXcFCWOCBFPI7IHwEyjJBJsOnmESBk9w0O99YWBv+QQP+Sb4lP+svrzeEqMwZsIFB7iaA3orJ9zws7s1QfSEBw7wpPwD'
        b'uwv6OGc8T3qORWUYAjONgZkGYZZRmDXhhRN4U/5BEz7Y54t9ftg3A/sE2CfEPn/sm4l86C0B2B+I/RUTQdgfzLzAfUCGWeV5Y1HzDYHzDcIFRuGCiRCcYBZKjOENxQ9h'
        b'KPWYMLuvoK9ggEfu2txsoLOMdJZhVrZxVvbEbJyIJokySSLOc57nPIdWMxdyGmZlGmdlToTjRHNQookI7IvE0JRPRGF/NIamuC9vIgY/xVqeRPgpzvIUj58SyEtEfYv6'
        b'yyfEOECCq5qIfUnYl4x9KdiXin1p2JeOfRnYl4l9WdiXjX052JeLfXOxbx72zce+BdhHIaebP5HPooJCunn3ff2Pe/Z49j3e9/hQhiE0xRiaYvBNNfqmjvmmWuKqzqw+'
        b'uXqgcUg6uN4YnWkIzTKGYsnA6Js95pt9PywKc8IS4nQXmoRBx8t6ygYE6G/l2ZDBEINQbBSKx8jXFBB6/MmeJwfSGXnkXkDS3YCkkcDRbEPAYmPA4jHfxTaspTfDWl4h'
        b'w4FZ8NSM8zRaqVo7zkFD4R/jI70tfOQUFhJfCu84yK5g3rHfyjvi62i8WKwEzMn98853tuEaa8POumVSL3nn8Tj/iVv8v/6tg/6dse2htZyBN69jKs3LC2q5VqdWkbhm'
        b'WoqXyW1WKx5piZneIN+iQeW0quUafGiIWQYxr+torGvb5jURZ0vDU5e9lcxiEganbgsC/Bs2/rk65Wl1sZh43d4K9oEueAwcAp2IMvWA65vYqxDTcQ1cXgb0PCoQ7OA8'
        b'yVuom0lIEhiFJ+ERxN5L8GHeQxI4CHt0WK3iuh1cJvwu6Fq1BNwUw2OlEgmHEoJODrgI9eAy4ZUlT3AWfsLCvtqE97Z6Mpb+wM2EOeasLog1Bce44FnEMTfNG2fVEHY1'
        b'IiLKrMqU5hFNZgu4TRhk+AK8Ao9WWXlfcAQ+Q/hfxMU+S7Sg8LWUhFK8wQ++YNZ1gt2LSF3mgoOcfPB8FZOTDQ6wZsFb2xmV67488BqC+jw8QirByWM9iXcgKhKGB7ga'
        b'LFJu3fqzo4fn4XPDhY0pf9n4BfeJxeJXd15p2z26cvzt31AedTEz5wx2pz1ZfAM05LGvcwp63P7034ffe5ezfmJsNOKBv6+7f9VLf7m59/26y9Tc9ndNAyXciPg3ijrP'
        b'b/9dZ/Ef6l55/L/ZR7PyliVHvZi9YmHT0Z9/nLLlo8PPPPf8c38uTPt4y2ufvtWw/y+CX+yTZka+8hG3ShaTvOWFrNbOS39b/rOafY2JHxfrFhwJ5X65endf5n8lvf7D'
        b'x2o57/6as+NYUsSzISI+c9Z1F+iJtG5JGwKX7LekjYJdDA+ylwsu4OuQyGVI/jS5DmkPfJlch6QDt8GJeMkacKWcjRpwiFUKenIJ/zgD7IdPg65EzC0Vi9nUugwPORsO'
        b'KMFl5rDypc1wxKKEq0ZdOOV0CxgVMseeD60EN8y3j/PxqXErr3gVDolcH5mpcbUyNVZWRqqpwaPYZpY1hxBWxt+8e225D6FHiKmIEg1W3IvMuhuZZYjMMUbm4Nuw81iM'
        b'e7gMUfcA0+zwM20n28aiM0Y5o1WG2XnG2XndRabZCYh+z85Evui455TnlCOpoy6G6IXG6IXdi/tiD1d2V5LSjZFp9yJz7kbmGCLnGiPnYg6pgMW45uKDQ/uk/dGESQoM'
        b'PsM/yR+bnTgiGKk3BOYYA3PGyNcUOHvAxRgYey8w+W5g8kisITDXGJg7FpiLI3j93vcCE+8GJo7wGR5njHwnXLj0zG5sYigmdUA2iAAci85H39EY5tcC5v2AWd2e3+o4'
        b'0Of25Mzc0L+xOw602OffcjnUs+h9F1nj3FaptsnutkSr1L8LEyee+bZEbAjHRe9KbsnlW29MnKJQ+BfcmLhHxP41h+Vkn9YkpcJEQyNtwz6l0pZmPbrFFtwIOXRxAx2H'
        b'fXE04jI0zI4ATI3km7F1LbxAHidpV7TGJZAXmcmi2vn6ugZfXiCzrupL1fVNija5hK7EmxA2KTRyK+kjZZAKkORSuqFFiXicb6BjLk7omGuFToTxLUwZX4QmsaVFSH4r'
        b'KS8DF6uLwBWoT5CIYHcgnyqCe11akTQ9rMNXeEUWg1OlsDOhpFwCO5GAWw31SBJfhuQ3cSwmV/AQlyqFL7qAY4vgbbIHHB5F814vEq8vw30JdeAQRXGULLBrKTipwzjv'
        b'7QOOlsJb8QjCzdTmJT7MQttAPHg2vhK+DHrYFGs5BU9uilUEB8znaPCQ4DwlPr0s1xskeb5w5MGSv5SVjbzBCxxlZdbuKBmR19VSkYF3edcW1S0ePnHrNz2BgzOfXbT+'
        b'6fOeL55Z8Ke/+M3P+0Fu7Dv05rIY3veaj+Z6VryRGW945wnDh2+t1fV/ZNIvaLhx5hehgh0/cP/6xc/UH20ADf2dWwN/uCFXHPSHpTHL/zBAv/biB/3n2YLMnz52p+2m'
        b'dE9j9qqmGTVP1+0L2HNteD/93g/2/DHtyyXdI9rE019f+mj97A7tcVVIZP6GC5d7RBdnZud+8dcjQs2WH9354vfdHpQqquxXq65s3lb5ly26qC8/5Da0Chvbfh3U7xd+'
        b'PlZ0e3v88feemPm/RV9u9BD5EIG5FRyLIZ2lghcRX5jJAlfhDnCbmfM7QC84jmV/POEXx8AbSPCFXextiKQfIfoBxK6cBXjfws1NeLM1PAF3JbIpN/AcG5x3R6XgyWgz'
        b'vFFAyuhMYFP8p+BgBXtWXAbRP+SoyXGCzgRJMewEO8pQAg84woa3QUcCSYDPITxWmgAOVmJlwDVwSsKiPBayYR8Y2UTAXwlHxbiExEps+kIGd25nx8EOimRmIeiPwMs0'
        b'XlsVSeChBKxv8EniNMJBdwIZGG1ZZiWo/ORCRFDhTS5TsXPorx8OwGvxiXg3h1giYiN6d4YDngbPgeOEIHOi4DDRfCRW8Cg+OAiuzmUHgPNsoqgIgz3wVqkZ68H1MD7l'
        b'JmSDs/AsvMys1r0EboRh/ZG5XWQR+exAMLCQRAaCUZTTrKrIXUaUFeBas5BUeR64CXcwUKHXbokHQ+wEeEMj8vi2egYPym7RiqHKXDwftHtZKQV+JPT4upkel/hSwpm9'
        b'mcfn98wfiGTsWmARL/v94PCxOTamJgT+KNG8nnkDQsaqBEk0lPJ8zqWcEZkhPtcYn+s0X+AsrAQ44d3v3c0zCQKO5/TkHJ7bO/eeIPauIHZopkGQZBQkTVDufvGm4PC+'
        b'mIHIIc7QOkNwjjE4p7vAFB3/3IZzG842Dzajwv2TiXPCvY/bJzMFhuCCB6qH0gyBScbApDHyNQkDjhf3FB8u7S3tJn/3Q0L7M8/MPzl/KNIQkmgMScRlxJgQvXc96Tog'
        b'xID1edu9h+0fTxzze0LD+6oH5gzGPJdwLmFIO1JtmJNjnJMzusgQmmcMzUOlBcXfWW6aFXam6GTRQPWJiv6KvooJDgolUcT5FDsPKLswZw4SQZ0GT3AsMBFl0vciZxby'
        b'ed/ncwvd3b7vxUIuwz64MezDF9PwEFPxBYuVVjmZYStcWfi6Vjtk+TvmKXZQlutan/R5tOta/0X3kJ9wS6Se957HEZnN3eE7MW1syCHKZf6IeMwPG/0Lphhqx8e5ZS31'
        b'NTXE8si4a6u6pVWu1m55FNsm+CAy2ftPFqWIWoEwY6TpRMJ/y+o0poNTF6Yn+1CGnHarIcH/xhnKOHaGMSe4bC9fhE7IcaW8/fWrBjhDmju5Y4+tM4WFD2WP5T+B8Ne7'
        b'loXQFrkPiHt/caFp2fIJTgS+H/Nhzqe8yUwTXBxawqKC5/QFmnzFY75ikzBjgscOzvqUQs4D7OhLELceFN7navLFl6aahOkoQVAmShCU+QA7+mKUICy6b7WJrEqahAtQ'
        b'grA8BB52HxBXX4HSBNLdm02+8WO+8SZhIkoTmIySBCY/wA4xAmqbIBsnyMUJcnGCXJIgYHZ3k8k3bsw3jkkQgBME4AQBufolKEFIRF+syVcy5ithwAghYIQQMJCrL51w'
        b'ZXlhKeOhLp+0el/VgGYk9Y7grVRTKD0kGI24k/qWDLd8NWn5atKI1az7y1aYVq+b4Ii98lH+R3VxN1hKmOCS8CdYTGdHjFTdiXrL5c5sU0hYn7YvboSDYKgaW/nYmFSO'
        b'X99IXt9IMjdiYGvwuRJOJcsrZYL69i6GyFool4TXsdO9ChHA/7SrYgV5hU5Q0zkZTHtHjHmFGbzCjF5hE+yZXmhC/UbnUw7lPdsx/eSNCqAb3lJrVE8UI9ZC4+3NobxC'
        b'2Yg36GY2U4JrYL/OAwxpMd/lgXfxLV26EAwgLmVWCjeiudH55fLkGmqW9XJ5izbv33Ox/J5HMdjhUqHzQU9PwA5W8UJ86W44Fe63kjlxuRMOwYulEjCSlI4yl/Lgi6yN'
        b'LTrC78dsgTvjS8R4ZcZ2tRNxkiR6gxh0wq5ixN7B22lwfyqXcgVd7BLY6aUYOvY6T/M4SrP1ytFTb6edPntkI4uTMeKpXwW3PL5ftN8j8NpFzkeNc4afClr6p/Wjf5MU'
        b'DkgalLeW9y3vO856Z+07e84d411eM9OzKmjfaE5QVWBO0JoTkUHd5fFbXBvuo9mx7K/+9+aOiHhkfckLcZuX4s27r/jwEuJXh9mp8BkPZi1uTxA25MfwdPBSrpmpg6fg'
        b'8w+YTY2vYUNs5h1afHgtC2/QcgXnmP1bl2bzSsnqUzE4a12A2gCvMaqhU1LfUrLZ82lwlcQ+zpbDV5+a1i6JZ6tajgRPeQ3egt9u90SYPGycBlPthX6UMNDCeukX3RfM'
        b'PJ7Vk9W36EzJyZITZf1lzK4j/SLMoOX25PZtGnIzCFKMgpTJoM3Mvh8U4OOPp7EoU0BI35K+lX1Lerd1c1EqfamtJmOci4EY5zPml6awI4w2A7MeDMkSYLbDDvpwBL5G'
        b'SVm4jqd8WaxgzE04db7Te67tkN/X/Pv5fWzF2cPGinMKtjiCRiZ7jxu25yznyjh7KGLH2d7GMY/E8VGci0Mcn8S5ojg3hzgXEueO4jwc4lxJHGP7eWqcG4nzRnE+DnHu'
        b'CGYXBLPvHtc1HrJUPauBJZuB4Pc0hwuwHWZZGgn3R+He2K/n69307g1c2UwU4iNLRyFclDYQWz7ude9l93IaOL3cXh7+kwkb2CgM/3Ksv0wo43KZFDYud6pfFtTvo6Bk'
        b'wb28IyxZSK87cmdZykL+UCYt8oVZfbOtPloWjtw51ucIqy/S6ouy+qKtvhirL9bqE1l9cVZfvMVnWwdZQj/7WZZM3M/G9p/lM+R+MkmQFYUGBJSTj/0cbG8t2lxG4j9T'
        b'BoFGaDaRzFjGcW9wkSWhHvYntq5dSK/yZMkoZKZMSGyRZYy71SC+UVqoUMqJsVC7PUdWdZ6eYtaabPYcYWPMXPQOSs82K/XwTiOXf/lOIwdqxaEcqZU7s9OoS8Wj+hf6'
        b'Y6MKCSHeGmZfPj9uP7W6MZ1NLa31Fq5rZgLfCN7GSlrygEclSUMam5dQZCP8OrmbnZHVsgokv79kY0cK0YMuF6qq0dUX9sC9zK7/kjnU8OZDyFeb/5n7U9TvLWCSmVLx'
        b'/rF4lgYrRwtv/O3U2xmIql07EvXMRx+x+H2BOSdyHzvOGL7qZP02aNlvgpb+9hVEt5YH3njjk7ow+pToFO9NyQze9RM3Tryh/NuMlaNRnqKEoei05LZdSuneX77VC7rB'
        b'+NuRbvdYvfKdH/M/Xb1ss7I1LKT7B96/v/bc7q0/2Lk05Md3fsGmfnRn1uvar0Ru5rWJGnADdCWD45WYo+FQrtVsLdi9nERugyNgJ+gCz5OdNBHwBj+G7Qd3rmM0PMca'
        b'NnvYH9fPysB7nv1hN9k8IgTPlk5uEkZ808u2zRYVxGuqmPWAxiXtfwo+xxgrjY8VM2lQigB4UTmLO3f+XCbR0do6VBo+U3KAbMjZzwGnPSg/eIoDzoJrEpII3AIv4qIs'
        b'ycrBMFU/GyU6ygHnwYtCsq5SWAQ6QVdMXCLsTCyG+1mUK9zHBnt08OkH+CA50IPX4VXQtak4ATwPjhQTVg6VBg5VIhagsxIelPCp7FI+OAbOwF4R/xtEN4yWDsZIZ1hH'
        b'nb01UmxGD1O/dX7U7Mhubq8Hsx9WeOKx/sfQo/uEO0VH9GkG5hpmJxlnJ3V7mgSzB8LvCiLGBBFDniPqu7HZY7HZo8q36u/OXzY2fxnZAZtrCJ5rDJ47JpxrikrGlj7n'
        b'mObEDxUMLR8qGJQQu6XhUcQOqPknjCZvDo8c4GGDqN3oz4bOMyqHcR454zXOxUeExz0n92aqWsbdFKpWnZbcAOJsXYNRQpjX6x/eJomYJ9hN2SzWr/VjsbIwC/DIzne6'
        b'Jt/vlkJd986j/hFTn2YLgbwa3FTTmQa0qbzFNmAe29Z+4ZodZtOAsyavwHAwBihRd6Ik/7hlT68a2w78B2BcxLYznZloATLMBkhH456Sb2N71IpU/wB4SxB46gOW2ffr'
        b'0GJLGZbTtd8SKKu1TDwIapoV01qldAJTCYZp0lzmTKy2oRvULc3fFphGe2Ckm/8BYMrtgRESYPCp7X8KFH6NtkUrVf4DcCy1w/W1FjQKqsblWI6ATwvUf8KemEfiS3gM'
        b'X+IVwaa4s3Zz8f6N7IgtDAuiSHehPNN6eBRd6xlZxqIU9dL5bA0+3sj57EeMBIxNYy4PjLp35tef1F0Qfr+WH723Quj/o8CgwJWp4N3UFawf1vJ/oqUWa10LZvuIWA/i'
        b'KbztssWd0DJ7Ogau5diTslfgwelkTsYSpZ/t9DxpCDOZYiiWbAYVOKt328AyYwBZTQg1hczqS2ZOOqT1m4+pDOUZArBK8Nvbw3SEooptuwJeP+PftgL+4d/R5z9Qn9P0'
        b'KPocMyZu1vGIxFubfFxpKk52JZvpXglvxPmFv2dRrAV/V7S/GswjePjBYOUkHib15gRF/voT3n7P1Qvd691/lhLN3/tuWeu82K+bF64P3BWU9TNqX4Gr/IdeIvYDbCzV'
        b'g3YFr4HLTlDRHg9f9CY8WrUQ9ODVQXgCHosTS1gUH+xip4K9cMe0mhGfGnLWX9Eur6lTttRvaA+ywRX7KIK5iWbMbZ1BxSYMbhtZYYzJvReTdzcm707EnU2GmEpjTCXm'
        b'f/rkBt/IMfJ1wNtxHjnO/g3KjgKs7JgemtX2mo9mhML4CJJz57vVfEydRbE+7/OtlEXaO87ckUQ1cP6N+NswFX+d7Vcw3+ehLf8z6xMOFXsnUVbTNzuUIhsGmvFOdHAZ'
        b'DoObqE7tVDsYYTPG966sAhcRDvYJUIs/ST25GL6iw9cgwDPwGNBjnMQ7pWxOr1fHVohZVBro5HsvAD3krHdkAZecU7mf1qjMX7CKIgeXqdpKtkx40ItqlQp+GfiJl5yx'
        b'37eQH2y5XMP29HIbOGLBerurNc7CE+7wJDznzyibyab5nnzwGqMhDdZMKkhBB7isuHnlaa4Gr0sFf33w1Ntz0bg0PB3+50JxgVdBcr1PvKAgpsoLphSiYbnQkyXa/4sE'
        b'+tbqW3ulLE5GN9hz6fzqm3vDn84+FfSm5INEaeHyH+66dL3TT1Yfo5kpWMe7HLku/dIapepyvrrmsM+bCWn3bshT895/4+BvvNu0m7QpibVv/O4l+cLbwT+ply1s+5i9'
        b'cvjsG/9Pdd8BENWR//+20TuLLH1B2sIuvYtIl44C9oKURVYRkAXFXmJBsSCgLtZVUVdiwQ5WMpNivEuyS17ODRcTL5dLvUsw8ZL8LrnkPzNvgQXBmLvc/X5/WWf3vZk3'
        b'7zsz35n5znfm+/luWBTRcYT/B5NTJt6b3DYU3d/yDj8n7OjXIUGeoT6h71LeL7w7MTIfjwyh1CJJQOEZU5EhUa8WmJvr7fNPBu26rf4zcCdBhoPtYthCFpoJ4PYIaLhz'
        b'dWRwAScloB0PLfH+zxpcVsOt5OTczEgTUz/dIn4wQzdwGR4BO7nwAlrytpBsF8EXYStoZIGruThPwhjgbAbYOZCxARUEOgycDVcSTa8p2A9ewEasrqjNBk0YQPsMsvkf'
        b'ZFfEqIFBd82gGnh2pIg76qoRd8ZBdwlIoFpeI6uVrrTSG0PIHTKQsQdcWNhQLu54X30SCZqStU5ueOvbXSsQ6ibiPStaVyhDm9c1rVPVXljTsaYrXxOYQAcmNK3rKb1X'
        b'Ahb3LH7o6qsWTdC4xtKusWpB7OAErrKhncRo9qbtJZ0c9Jd80fiKscY+uiup136S2n4S3lkKVdS2RR+KVvF6nSRqJ8lDjwB1YI7GI5f2yFU752oFzg8E4l6BWCMIoAUB'
        b'akEAunPInLmnytcIgmlBsFoQrMVmCEoPNd8LfWi+l4p/wanDqXOmRhRHi+I0/DgmRkPCfruB4uqNzQbM2MwtqlkoH1WyMBgYn3UDdA4eoJ+q3Ll4XF46OC7X2fx3N773'
        b'GYupsxYxnJwS7miTOTlixxrQyRGNHB6t2WVcMlZzRzlixyNjNfepsZr31HjMXcvTjdWjxo1t9zcaOKphDjlEDM6C67AFYA9qoBFcdUM97pYjUToSG7vahfBFf9QO4JC4'
        b'jqoDG+sZJI6NcFs4eBGVerk9HsmvxMqcv2Ox5PEo7vPU3oP3Q3Q7Q01A+/p7r3fuaNtQFB6adbaxu6VbIdosUrhv7m6RRVx/MOWVilf5+7rFL5kdklDbPzazSf89kpCx'
        b'4mHhXHAKNAZizBNwA9wEqGMTQyIW5VTOBQ3gUOgz+uh6vT5KEHWGsRG5Q/oophcz0RRbysHlgcC3V+CrGtdp12WgEUyiBZOaeFp7Zyw2u2qdXBQh/Rz069F4b2Woiof/'
        b'sHGxVYAehxsOWVDUYNGsBp+1HSmFGFKMomVQDikYyeaEPhlm83pKp2TBsIW2LBY+7PNLwW8mihgjuoYx+eCMTxTPXD0mN0RsjpXOxoTVDf+LrP5c26S8nCGGLnZaDFrW'
        b'wBOocC6UC7w0RXatyItFXJa+bdh98H4c4txzG0SbgxUbth2zvfdl6axXX+7pdGxwVyqcfN/sff3aDmvf+0a2fyvmbA9hTQs93vFl8Relh9/Qvh5xMPj0N5tlAXI0S5pS'
        b's+qs4/7qP8AWz3GWxJAaPEvCcK4p2X/Tsa+dHnsM3SY8nK/j4bm2FN+haSLhVK29e9NKpZfKlpkaMAv7aJ3dsNVVW8ahjKYUrcBTYaacpkrVCEJpQShidC9fZb7KC/+p'
        b'7YPUVkF6bG3yHGw9sjgmQ1w+qGOdgRl99JJUYW7fqsftc56T2/9TzO+LaP0Mn+AZ1gMGx9FNlP7WCxnmDXUDPe9/k/tHE8oHuB+3lcWk6nzJdLg3NI1D8QxZoMMTbLTz'
        b'kR29+ypHjkF9PjvbePB+DOoCJ0kXcN98pqV70x6WhUIQ4zBh1j5WynSYMsGhY6aDYMorvYoOrQBLjnOoj26bPIj4auFtNHYzZ4NBu3wA/CQKnIwEl2rR0mxM3ucN8L4O'
        b'1aNQ55lSx/wCPZYZFkP4P1zH/xXD+N9NGXqOo0pRpXR6nck6m9UVoREnaHwTad9EtUeSxj5JbZWkx+FGIzi8z6CsqKS2qmZUMcVIj7UZxp6LGXtMKpdj3l6jx9uLfw1v'
        b'/2YwBpjsA8ZBVKdFHEdkyUBGEPAIAiOBASX6zIf0zYulK/rMl1XVlZRLa0gpgodfhvSZlmDfBdLKWmlNsP5FSJ9RqUzOOB3AaBR9vGVFtdhXrbSutqie+EHF5/n6zKT1'
        b'JeVF2EsnvnWKpMQ2Y8F9JgNOA2SlesjBp0mKWllthRS1Fz5kWIO1nDVYyTSaD92cPqPiosrFOMs+U/xrABuX3CYeUcj7QmpKWfgoIoZULK6qJwjFfbzq8qpKaR+nrKi+'
        b'jyddUiSrELH7uDL0ZB+nWFaCLgwTkpJyp+UU9HGTcvNSamrxkFjHGrF4x3WOF1PfbKEG4CH2U2QbGFte4NmSajApM/rfXMY7jTJilDDL+BLTNXNOUv1k+7V6XDozgpSb'
        b'gA45vOYEN1vW8Cg2PMXyA7f9yLKYA66Bs/JaV/4yeM0SXjVlUYbwANsCbIKX62IovIWHlmrr/bGV+TnftOyA9OypsCEHnJsEtonh7sCMqWnijEC0IkdrwAF8Ndgyxywp'
        b'y5tIqhGwGSphy1T0cyW8jhak2fNBM4mZB1vh0dBYcAFjSLB8KAwaUMYIqhvgLbA5FPXAUCrKNrQOniW6iOWwCe4KBW11YUFsiuVLgVZ2IMGcgNdAJ2zIzAJnwnX29SzK'
        b'dDYbnofNCxhx+UXQAW+EStCTBhRLRIG94MR4YlhnsSyVwAZMAtezw7kUD15kwRa4o5Jx9OnhH3abjZjZagG72CWPInk5w/UOoWB7TFgQi2L5UWAfuA2PECi+ReAw3JsZ'
        b'IAnAAITgpHW2BG7PYlH2oJ0bnwg3kixnlgv573HWY6epzmdj1jJQfA5rwJbQAP+wIA7FElNA4e5CWsYfXlvuj2H609FCdw+8jFe6lmAnp5iaRfL6PNh+Sh5rJobgdz6V'
        b'vYBR2MCbS8DO0Ah4NyzIkGJJKNAmcGB8AjSCPbl4yXzeWAzOcCmumAVuwKPwGJNX/KT5NPU9WlovsOmeLdVBhuxyNAlFAv2tMNCJeDKAAgdwTTK4HHfBrjxsCZctYVHG'
        b'wRZwMxso4NEZJLc5thkRxyg0G1stMEmQpDMVB1rk4Fxohg/KDLV3IAUOzgO7mJNt4MIq4nhqPeiG2/B5frAFW/WBzSS3d3y58VyWFT56kOWUEMNwNDwBboP9oXCXSxga'
        b'+3G17QWd5XVYyRE3CezKzCBeXXdlrgPHiJUeYmhOHNwKbpAs19ZHe67mPMJTQk3X5Aodgevhi0tD4Yn4sAg2Ke1+cKKyjtgm3oKNi5gsc7IGWczRER4ErVywXQjOE5pS'
        b'YAPYFgougDthEQakiAq4K58BTtkLusBlXRYYZNIWt6ZFNSfKE2wiJDUttqmezMEHrBfEnpoeTREtW7FlQihoBpdDMN+iMu6blE4aMw22TiN8O4+VHc5GbHuJhXqTAuwn'
        b'dOSCi5GhYBtoDQ9CVROCHkO1tZWptj3uUOGfKQ5bBbch3jSQsR3M4Xrm7OE+eF4eCq6AO5H4sShEPVrDbWJ62Lla2Ix4EQ0GHZgft4MLFGUWy7GC7WmE7YSmsDHUBB6P'
        b'xF0zBjGKDGwnbWtiY4etQ5SIj8kI0cGlzKw4dmCfHSn1jQyj1VdYQtwQFew5QQzfgS54Bl4IBefGRYZRJLs22A4VJL94cBceRZRgA94wuDsTMUsJ2wl2w8OMWrIxdWao'
        b'KbgZGYZ4bAKig11A6Fu3BG7JdAAXM8FZNBZXseKlsJlUiCe4Mi4UtMAXIsMQ5bGIK+FZcIchoyNgfiYa2SzBUdRsO1Bt2bKNrSYQup/kropqoT7FHB7xtVk8w5NxsBk3'
        b'1qz8oDAexUqk0HOHwF2mK62H+3zQWnimXQaG3eDAOyxwsGAxyWt61OQFKpaAhfpxRothJZNXCjhMgcuwOzYoDI0KSRRQoubYQcoI9s3OylxSiwYXJKrNZwWGASXJZ9pc'
        b'QelD9gJcl6v/6GHJMLUIdosy0+0jsJkMl8sCR1FdqkiVOILjiON1ltOX4YmAdbCDGK7BF+A1X4L4kpcGt+VidFVsigYbssVoJKKoyXy43sbQKSOWjFIruWDjIA4nPv+h'
        b'AGfASTbYu7ZuyGXyJz6csB6dlXWVJI4Z9mCLJdwIW9AUhjj7Flu8JIHgX64NAAczh3myhbvRfMOVwy7KC3Tw6uqtGfu3fWiW2Akbp4bDO+uC4HY0pNmw5sGT8DhT411Q'
        b'kZ85H24qgDsRL8A2Ch/AcScni+HuteKROLIsM3CV8srlyWbpphsnuMkXHjRF9X2HyrUBdxDT3yajgdX8HH9UIdlwV5okg9FvBHPBRXCZ8i7ghYBd8Bwp8604p9QgqhzP'
        b'HrHbS2uY4RnNQ01ACQ8iARbcpXzWgbv+qYzHk+PB9U/lyq70o7yn8ULdJ5OGz18N2zP9s6eiKZYAld42M2FMyjtMwJ387BV5UzH4K3sVy7kOdQdiX6WEx2FnJmhmTWNq'
        b'4SQFr3DARmIgX2AGWgZhelElrAT7SRO6gUYuvIaGF/LSuOIAeNAcm+VTReA8uJUIGsgom49GbdSz0WiQg55Kl4RwKadIN3CAWwH2wjbyqCe4Bi/Cg1hJdZtaZARuW44j'
        b'j5bA1jnDHmVTTvxkcJC7BG6GreRRG+zsBjaiXzIKHOLKwKXZTKNfZvGwmSRptE0uhF5LW86iVcFM17iOxI1Oohdzo4q83ELgaVJUuMl1kT/j8QbxUyCDyevMywFXuahZ'
        b'14MrTONchTvmwIM8jCJJgTNzwc1KDhNxEnajlmtEEsliCk2ItxcHxZNhPQ6cAFczJZJ0cNY3A7Ya4V5mG8+BrWAzeIG0jd/UVHjQDEMK4AePgCvwNnyR2Y/Y6ALuZDII'
        b'PuPChjB8umADeamXhZMcbnE2N0fjEup28JxUB+cLDEwW7eP4YsbKeiV/IUVOk9utjYCNqNhVFCutarUDKXUYvItaEZxLw2i9OzJzJRlCcBWTKHTiolpqmE82XLpZniw1'
        b'elK4PKCqJ0obKNf1zhMVoURZuJKCew1XRoFNsn0zi1ny9agSoqd/dPIPk6v+GMSnFjR/3XQo5lr+8vZVng8nPExvObXqQm2g/adJpvf2J/YfC/ooc4NrrWilaOU7r9v/'
        b'/Hqc1zXPkNXjjjkG2WTkurmJDuxe99e74uq5Ef+gqho/veATv/rPC/4+87XtVZd6LHhvr/7H9y6ekl0S10l/7rr46PJnUR1zis6+tubLN5YdSt7I5sPj5y2P/q7yevu3'
        b'T174wezl2T/dlVR5V4PmHPCF9GGdb0L37lzL5LJ2ycwpZhXVzY/vdQti7MIy93rbcCKeLD1vMP1j+bTVtte+fbP9kCFt9kqMKIK/9P6U99K2Z6e8V+pb6f2KZHvXO1MO'
        b'eb+yZHvXwynvJWyfYLd0/7Gug/zvPloduip96VGPLyP5C9OWTrfOnvE9Ky9WId/s5vEKjP7ksZHIddrLJVs+XJoXu0fumtv84ZlDH8ryYk80yLd8OCsv9nTDJ+avmLbX'
        b'T7UOfL347rZzH6tecei027JqjfF3n/3u9TiXgo/++fAgFJje/cs7HU3buXOzJ6X0WuRfDdj7zo9dnz9uTPk4kb5QenNvqet72zQ//+2di/VXc2zuLUg41/p9cvibd47t'
        b'CKi7cHvc1GnjZ79T8OQjgejOgwCrPOcN38zouTlDdaDPtiBla8o/21h/XnzjizvrT/7pHvf3f47+pCOwdXv2uaPSaJ8Lxg+2LNwg9fvq0/aNa8Tg70Uf7Vy6RyGf98dv'
        b'skNOz7l/4M7tL2cct/+q6cOHjz3ea/mgWKv2++7BbgtXs08eFZ2Prk8u+zHqcs1nr/i0fx+WT5+X1Kdu93dYmLxmy1vpX6V8HJ0ReOfH3X0dbt/4560+vPj3VWlfSW61'
        b'mNdXKf5s2PujaseNk2e/zS384r5v+7jX4u7Kly+iv02xX/7aW8ftCrd1NHzzF7f23wdWqfaJbInLdXALtEPlSL/n5EgkmtmOk2OR8HYdAXflw/2O/lJ4Cm9CssEBVraX'
        b'gFi/JhU7IIkM7JoFzokNKG4yC62LwHlyANIBL0kaLavNauAVsNNymbmxAcrmYCk4yqlCQsIZ5pRkE1pmbDAFZ8RpdRI/sNOdbIBZwxsccA7ehN2M1YMSXEkiVg8HqwZx'
        b't9CMsRVcIsc/JwWjRVhjoM6a1QieQJPoFTZoRDPpLbLh5R+yiMDIMrp0o2wZ2Mcuza54ghUZKyaXZtaBF3NxwZaxEsYtIxtormieP0EMKc5MYmwpsCEFvDaHlDqDArvQ'
        b'DA+uTx6EtLWGe0nU0ih86BNcyJoNr+BIfEx16kRCpg28EKU7pSoG5/Q3D83nkMqIMwQbhw6Mgsux5Gip7lwp3O7GuJ66448WTUOnT++I8MlS3blStJQ7QzzOLioLx6dY'
        b'ZbADb/filRQ2f9ZVgH80D00tW71Ifs7G4OTAnoPefsN4sBtvOayAl0l9RIgCdLgdC1z1YDtalpIG8uSCTpSH3iFWuDmcjdbAWyP+bYvi4ZBlnKLS0pXmQ1ondEkUYn/i'
        b'6QA+7ChXD9olsDO01yVC7ZLQhYKcnllNJg/59gqDo6YHTNvMD5lr+N4031vFp0XRXX60KEXDT2liaW35WGc8g/XQcbzaM/Ue/y2H+w7q/ILXnX/vrPGcpnGcTjtOV/On'
        b'a21dlON6bX00tj5avmB/ZnMmNjNGOStTVKEaQSAtCNS7gf6WdcrowHiNfwLtn6ARJNKCxKH4iE6fs5O6EpmtF73bxLK5QuOfRPsn9eRpBGm0IG1k9CImy54QjSCVFqSO'
        b'jC7T+E+k/Sd21Tz1ThJdrvGfRPtP6rHRCJJpQfLI6IUa/zjaP66HxTz96Ne9e4nGP5n2T+4p1gjSaUH6WJQHawQptCBlrHezNYIkWpD0K6NlGv942j++x2P0zAei3Z9d'
        b'7jEyl2r8Y2n/2C5UsARakPALT4+stV9okhGZP5Y42Y17QqGgf0QQQwk8mlYqvVXj2gM6x2vsI2j7CLy9PoulFUlUfJVcJe8M7TLoWnbLokd+j90jp6MyH0RN7Y2aqs6b'
        b'pomaTkdN1wTOoANnqEUzFQaKZW0WWnsXRVnrWuw1uvTsol77KLV9FNl/j9O4TqJdJ6kRdzq5HYrDb4lSTe9MPTu/q/RWZa8kSy3J0ooCOw3Ouiq4hyyeL5GLh2KaMkLl'
        b'S48P1UEqp+q6kpJ92vC44SO8P+/fK/BXpXZO7chQi+O6QtXilJ7xPcs0ghxakKMVuB41OWCinMRs5agF87sMUez4nrJ7hXTqPE3ifDpxviZqvlpQqi4u1QpclBz0l6qa'
        b'RHtO0AhjaWGsRhBL3qLb/hx33fGSY1euJjiLDs66hxpgKi2Yqv3lBC5KA+WydosHwsheYWSXgUY4iRYioiYNvTKO9ozRCCfQwgkaDNszMsdsTXAGHZxxL2GgYL+QYKhq'
        b'knQJMjTBk+ngyYNjxBjPozEmlxbkPl3oyZrgZDpYv6+OeEGmJjiNDk7Tix72fMY9niY4hw7OUU+ZqhHk0YK8p7PI0QRn0sGZ92ZoBNNowTStwKlfZCca95iyc7d/ggP0'
        b'y07wBAf9JBBTdg5Nma2ZyggNX9Skw1PQ27wwZTYvsKD/6yD68KzyFD5fI0EeGDardOANjO3UwImLqXbPsgF8dvCb7mYcNA6mLlpMGn7qf3CLbi3FgB2RzTmscqcaDHWb'
        b'c6xRVO2//dnjp1TtQuppVbsPo2r/KR/JTtwW3CDiebMjKGbHjqxDT4VmAKxaiYEXXClXeB0cZe43w5YCgJ9YOd+BckDy3SmyenP1XBKKllpLqkOokDnwGsndbYExZZVm'
        b'TVRj/t6JFDkyx12Fbi5IZaObWa1CY0a7cm/Batb3i3hY5T/ngwVrGQUSuAQuwIOh4DjcG8bFCkiqJABsZfQFCrAD7A2Fm8HuMFQqsJ+S2pWQnPbZGlBmRjJycJqXl8xk'
        b'n+9hRQnLIZeqXpC1MkTIEMIJRjfDsgzwTf+YBUzKdTnmlKA0mEtNWSCuNF7HpFQbopsFcRS6mVUamcCkFIWbUPzYYAO8huWXhjIpr/mhm/ybPHTTbE5mGnPzXV9EEn8/'
        b'G5Ekblkm0J3lOwpvgtb87Klw5zRwDuvtm+GLy1jgRnwCowXfm+EVGhTkDdu4FMsTV/vBSPLet6eMp5KzjiDeW+DxduBq5nTBTPPpZKULusHeldTKIEfSVvJAtFQ/aIIy'
        b'U0WCaxS4xvNm1IKHYRdUwYMGOAat6K9T4PpCnfrRFlX3BdjCws6J4V4JJanIJK89J+ZSRs77uNgl8Ws2QbpCnENPK2EL3Iv/eGiVv4VyWgCuOgIlQXCyF8UDnBXYVetC'
        b'uUhnMg91GgfqzLyZI4ybgQofY1wObhPq6sF+0JkvAefLcL2w4B6WDdwKDhIuc5iLlgSG2EChnqpn15Oyy8BuxAe4OyyesYJasUZOFv/zreE2gG1fZ1WtolbBS+AEGbpI'
        b'g8xYgJYoeBs3fkHFJ4HODGhoTDuNe82Ft1kUy/djWYKTLUdej2hf/5HbudbMvBfirbYsNEhLPPIRK3hb1cQtK7fNPZb54oKS7iu1n3kYdr53qRh6/e3loCzLbN6JAmv2'
        b'uu8i1y3PfeP0d16tWtXOg+nuNbfWBTRt64sr5KuuaruWujcUvKawT5typtjOcG5/0yN+YfGMy7ERJ6QrZC98P8X03PgXT17N+fCva/7xls2NmY1Jf1j0xb35W36q+Vvw'
        b'3zoXf/dp36a/uPU/vL7a0u9O5vTvqMXlF1NbN9etLHMrrzUP7VSU7Hv3B7u3P7fPcvz9om2FPxz4H/sJC7rz77/ybsfsP/QfnWlSNufcpa2pMSHlV7aejfuq3gakdru3'
        b'fPHqhmNuCRtUp96P/sMqtqv428uBi13tfxY3rz8Z/cHdUmCS475y9qwfKsD02tQT5faeX16uvf9x+oEZbm1/OmwauuszLafsLW3dm1ONo3nRUz/zfnfixW/stf+TmX/C'
        b'7va1v/70t0PfLC50mTN+7jcLr614P//bCZr499/+zumH24eWxyy8/cH0N+eM/8Fi3Qcvz/5+9we5i/fUJf4kEhCLBccUbHOoOyZuBfeMeVIcnmKwrg6D7YiBsaVmjsQP'
        b'n7psxK6N2GBfBdxK1lFAMd9zGHy0IAxchK2gk6xTY83hXWZph60fS+G1AnZtOtjOrJT3gitwF17UZWPFK3ZakpUPd7MomwQOOG9dRLK3wdaNL2bAffGYCLgNrVvXsj3A'
        b'ljJiBbkYNPsMLPfBnurhtqNktb8xl9ABm2Y6YTr8sar9PGsuvIiW4JtFDObU7kL0VCNi8Ca3oePwXo7kgGwMvFmHVr+tUJWrw/sme3jjZnKdjACD9L1sGlr8o8U4Bvsm'
        b'FGQt9kWF8OKAsz4xDPz2xemr8RIaNPtnDSyh88E5ZvW7z0o23PQSjWRXB9bIaCghR/ZXSE389eHI0yrIarUTniS4XNVgl9Uww0zQkTywggataYTMlf5+aEWbJg4IwLu0'
        b'sBnsQUTCMxzUnt1Z5OguaLTFJ33RWHr1KXNRZ24suAxaGOz1c6DZipiU7srkUVw2CxwOAEfgGR10+0zMDJlDmOBTUKZN7Cp4CtUX5kHQsAZcJNqLMY79rkREdxg4w6N2'
        b'JL+VU/CINqQMOYdY8gQbvX975BOCD3ukAG7A5AwpBsALYMdw5YAXuMIY1h6FL8zQX9mbgtvEQhW0ChhIiVPwzKwhb0H14Ah2GATPZj+XMaoe+lMfF5tUrbQYEsLwNVnb'
        b'z2EAhPpn21N8+6bQpto90a3RSlZzXFMcOfjyyIrfav7AyrPXylM5VcW+YNhhqOU7ko89PsGbSfNFD/iBvfzATpaGH0LzQzpDOkM7Q2l+JIrGioDxvRg5OqLTU82P6/LU'
        b'8oVNWUp+uxPtHtwZrOGH0/zwB/wJvfwJXQkafhzNj9Pl6veAH9TLD+q01vBRZqGdiZ1JnUk0P+oXX2rflKTg0gI/Dd+f5vs/4Af38oM73TX8MJof1pnXmd+ZT/OjdckO'
        b'mezJbc19wBf18kUqlEZM88WqPFW+CqUJHkZ/fqfnlYAHIem9Ien3fDUh+XRIvpo/Sz1j1r+QKrLTS82f2BWiVxcRXaggMTQ/5gE/vpcf34NKjQqbxKRwVtUwpXzAj+rl'
        b'R3XZaPixND924HG3To9h9ZjIoKUzDTT01qhObzU/sSuV3LcfqABTWuCLVgGoQlUeqmCVB82XPEesjgH6I52DbR5TziLbJzj4LoriOzZHKHw1tuNp2/GPo52tvVCEtVc/'
        b'CWIoa7sBTtJY+dBWPmorH8RfzD2NlTdt5a228tba2tO2XipbBsL+kW7pylNxH/hO6PXFq7xDpsqiA5ZqQaAqSS2IQItx7i3TxxyWKAVjEKHwMcVyJ6FdKr5jh8GESGiA'
        b'KNhv2myqSNJYCWkrodpKqH36/faO++ub65XcdnPGaU8TlyDmK93VfM+hQ+taT9/27E4P2jP8gWdsr2ds1wyNZwrtmUJMiYqxB3V7pybTp4+EPQd8G9mLHIbehiEgRnbf'
        b'L/EiClugkTXULPtnGcT9p+zjsP80EYusLdBXHAZKw5ahNTPxL/sR4GzE/LvGFJ9r8sKBNw588FEpowH72oFf+JAUsS1lUNmwYRU5vE+ONpNjn+SIXJ9Z4ZSEvITswoJZ'
        b'U1Ly+zhyaW0fF8OH95nqIvJTCvLJCpRU4b+nL30Kj80et8oQsIYYNwhaYAwDZDOwxOhpzww8KL5zU5SWdActP6Sfx+aHPaZQ8AQHDcmIbZ09FShBoNoqUMsPQwmcI1AC'
        b'54gnOGjIGoGyFopR1sIxylo4RlkLJyhr+gBpYgyQFoAB0gIwQFrAUwhqfjiBGCcQ4wRiksDOpSlNa+WrtvJlMNjsMAabHcZgswtuSOk34pgH9FNjBSZs8yksDEz3jNDI'
        b'1HxSPzVW4Mg1D+ynxgrMDMyD+6nnDKw45skYjfqXQwvK1V3JV5arnQO1ruO1Xr5aTx+tt0jlqZyNv8arSpXzh354+qi4ypiBL3dvZa3SbOAK5eOpmK31wFfOGHOhQGmi'
        b'9fJThSmz+t2snFG/xIEH38FGy3dRyPs56NcjvpMiv5+HfuHqd1eGKuUofUC/Ib5jRNm5KW1xNv3G+NqEsnPCEBKKjH5TfG2GGkwhV4YpFvWb42sLys5Z7RLcb4kvrIYe'
        b'tsbXNpSdhzIJE9pvi6/5Q/F2+HocdgNSgkvQb4+vBUPXDvjakbJzVXKUyYqV/U742nno2gVfuw6ld8PXQsrOUZGk5Cpi+t3xtcdQ/Hh87UnqXZGhdXYjiXzwTWow8PJx'
        b'tuinUIB4H40Izm6KUMVqVTrtFvHAbUKv2wSN20TabaLGKY52itMKnBQcRZZqHO0c9MA5vNc5nPH6oRFE0YKofh7HCWWFgobMfpNElrlfP/VvhGnsIHPnfurXBowhIJaM'
        b'C8G5CmZRBO6CE4yJG4+yKuDMXgEvDtP9mOq+v5mPAays9QCsWBi2qpXbatlqWMZGoe67lD3w6yznFJqRXjQcyMqYKnUj582NGyzLuKWGm4yHq6Fmc9mUlKeDszIZBeqK'
        b'V2qK4syeijMkceYozuKpOCMSZ4nirJ6KMyZx1ijO5qk4ExJni+L4T8WZkjg7FDfuqTgzXCelQlwHpfaH2OgKUY5hrhaZD6QpFegBM1lQo/x7NrjTiNwc/p3cVj51p521'
        b'i1Xq3sAmykfmtK9pg2WDVZlxqdNTLWaJUhk3WJD2dN5kNNuK4YizLsPzJBYGnAazBvMyXqnrphEO5GZblzoStAePPgZ1NDMn5R/7hoGOY38dA1HCkooiuVzoO6VKXrtM'
        b'WiMvqizFs7lMWika9sywC78CjH1eVlWzpKhWiH5VFcurKqS1UgLZXllVK6yowie6hUUlJdLqWmmpsHgFg9/uNxz9vKaMwoYxfcZFpctkcnzSu89U95Mc2DZiXJOj25zS'
        b'smV9nMWV6N4Saamsbgm6Z1SNKF9eVVNKRBnm8Dc+EF5ipNdcg675FJS+tdJW7lbeVoOthsSIGrcOF7ULD9WpAbHgMNc56EP8vs1khIrYmKiIjZ5SERs/pQY2WmusUxGP'
        b'GjcMC/8xZxQs/PRKWa2MGKPr/LYMNJqsUl5bVFkifX4k/MEajtEh6euQX6rKSM66U/FFGMkjkTmLjxIskdaIRnfwniDUGTcwLl2EddUYmSRSWCpbKKsdBaB/OBW4cQfp'
        b'QL+fRQWKHouGSmFRRXV5kWQ0UqKFJeXolSUoi7HJGWCv0euEiRX6ZiOuRiRJK/+FGgn/pRpBfB3DdMjU6cKKomJphdAX/ZRkotetlMpKylFHDBBOk9cVVVSsIGTJGKaQ'
        b'j0rFcNJJ3fqG6FXFKMTrCEF9K0aYReAhcS6TA7MGmkNXLWiQyC8qKV9chasC0YSIrpGiMWAMPwl1xRXSUt0gMDyXKSisqpRW6nIibhLQNVNTuqFj9DpOrxUuqZPXCosR'
        b'q+iquVhau1wqrRSGCX1LpWVFdRW1IjIKRY1Z0IHxg6l25kooK9U1WOgvNdjAoMM8PnAlrJEulMlRDaPBDo2JhJ3Ewjpds9VV1smlpb/g+WE061xLZl/ohqU13jaKip+5'
        b'LCvJnkfVRaObeeDc0gEEA53fvykEwmAOuDukapyqB2IAN8ebWTlYkizFQj7li0/610udn4R5M87cq8F+cB42OoCuUbIdzBM7RZymn+3RajPYDq/Wk4y3s8woAUX5PqIW'
        b'V5xcW0HVxVH4+CNowUdrR8lWT+2po3WOLQO50AUaTMExeMKa5LtrgQFlRlFW8YYrswoL0qm6MHRzPLhVMWqu6f75AxTOmIgzWw93G4O98Dy8TXKLrTPC2CpB1KrarFsx'
        b'Pkzx4Sm4p3a07GDDkIZZRyQ4DToHyLxmirWkLiTjH81NKT5FGcXPk4rXeLtRxOQFXs7yHC1f3wFt6kCmHQFMnjfAi6awAWx2kc3ad4Qrv4bZ4o3ynbuzTUCQ1Wafn9P9'
        b'66Ms1dlK1YTH3C9rqKVfdByc32v8zrHDZnRPU9zX/7iz4q2feI4ZW0tMs0wWvDrrzel7w36M+8LtTrvpvTfPnr/2/vU/P2ziXXr/hmuH7+9pcUvY78KKT/2ljU75qvZY'
        b'a+CDe2/+Nfl81Q3Fdd6fsqJCRR/FvOr1RlfCR69u+SLo7Qsh+78tOr1mwZzwFO67bS1dKQ8qrH+ucHPYH/bnbz2+6+n+5EDbpy45Ta9aXvl+8vzlP4lMiO7YGJ4B3VjR'
        b'PsBDUWCLTgu+dhJJAXebwOt6iIWOnIGjYHK4hXGptH95nH4WjG9ON6jgggvwOrwAr/KJLnt1Hdw6XJ2OWHSPnOjTQYOQ2XQ4BA+AJn/Q6jCAK4wxhd3hbqLQXwx2gs2g'
        b'MQHsHFT4AyVLt18Bd8PbqJs0wrNcPQX2kaQqoo0HHeBg9fAtCRZlBo6RLQl4E2whhQ2GSiM9XTqLcrPQadIbwcYnGPylHBzFfk7xmkICL8NrcrLLgq6yGACNk3CzxIDK'
        b'BpsMwWHY4Pkb60gI5J/1gLQxHAVxqQ7Qot6BGu+tHK8sUZaoRMcq2ys1HuG0RziBLCQe0Gtb1zH+K1Tuvbb+alt/gnc4WeOYRjumqflpWs9AjHforks95Gw9oddWoraV'
        b'kOTpGscM2jFDzc/Ay29bZb4yXyU4Nq99nsY9lHYPJZCIuretZRxhqKx7iVNv8niqxnEy7ThZzZ+MFqVH0w+kt2UeykQPGQ88tGJPXGucEr3RS23rxbh11zgm0o6Jan7i'
        b'I2c3kvTffLG76LTrcVeNezDtHvwrHhvvhWsHazvR52n/jBexegw7Dam5jIMrOLiKg2s4uP7LptmDnhlHmGeP0fYiJJ/KsR9xfafeuQ4sVh5xtP1bh7/ZCRF8IL3dOIa6'
        b'YZFg9GuAIcsGoA0HBeexEPOG6moAMG8aqis9ZENGbB+QfUeBXPy1wJDlDG1mhXri9PNTNxNTd2SQOtcR1BGRcYi2X0+WceGAWP38NOENLT2oQzeGpgEp9qkK+/UQldxC'
        b'JGg/Pz3zET3fDEIezlqvo8uJoUtPVP+XaCoboAnJ3M9PUxGuIzVroI58h2T1opF4nvJ/kbBBtMoBGfn5qSsd3oKOWL+uJ1z/m/QMiNnPT8/Cp+lBLTcoruvRI2KT/Qxm'
        b'Z2PQgDunhKNHJhI8GQvuZhTsNdZDfDAg2gPsP8+4waTBtMEMaw8aLMrMBvEfRsJu/0eAfv7OsxlFf5BQWoqduVZKl+vzCOpTz+XWNQWt9pjEWMdTVFqK1jZohVSkWywT'
        b'76zY0Z1YuLCmqq6aUfMUCUuqlhTLKouw+9inskTM6jeIFesnFvrpQ9uia4KZixIVV1UtxqRiVRRZzjFk1K6o/hUqj8EXxQjzq5bghTOjscIO/3QQs0XFVXWMs1rMGdLS'
        b'seoG/0utqhFKcZWUysrK0EIPjUzMEnR4oXT1TRzYompbqHNnOMrqD/9DK9qSokqyoH2WNiM4Qm8NL/StqibOeSvGXs3r1yuzUn1qkBD6JhTXSEvKK+sqF8p1qg3i1HBU'
        b'Qof4QC6XLawkrBBA6kQvY527aKFMv1QytMpHK/pRcx1YvQeTRo6IHlzE4zcFi8RYxygslRbX4vegFCVofS3DFyVj6R0IV8rI83JpLam7qOjn4JlUDGdBdJoju4pMKo95'
        b'bp5DtMpqdRkw9U7uDCpBfPOrKiqw4qNKJPTzW4I1S6g4K/z8xlRRkRIPy5G5NZTlZFS9lZLANDQjVf6arBnkXp0eo0pOCqxD832u53HnZJ7W764BwuxBFQ3pvlXFi6Ql'
        b'tULSgqP3gfzcqIigYJ0+GauLmd4Z8HxkDIMniRmhKltWJSuRDjJ8orRCurAMpxMJ5wSHzHueLEN0zVgnZYojqySE4l6fnJydPWsWLtloDq3xv+qiFUuIO2xpDZ4GxcIl'
        b'qJ4HFUJ6BIU8myBd82CkpOHthe8MVw8yvSVwoKeMShYj5CWiQuK+j/NArw8NGvP1wwBhBpSlet0E3UU9slIuY4iqKhv1rUWlixBnkPrADxCf4EX1+PfoY+PoatZhmciJ'
        b'nlhWUl4rW4iLIi8pr4C30EheIXq6z46Zp0SI+Ca/VlqHBtfBDBAHy4S6KkIj1BLU41KmSQqKaoulWPdeOkZOiF0YD7YVdUsWS8tHr3+JMHREMvK2orqylXW1UjRzVJYi'
        b'dp1eVSMnRI2RR1iMMKGurFxaXIe7Hnogoa62Cs9vi8d4IDxGmF5ZKlsmQ8xcUYEemLZEXlS7Uj6i5GM8HTEayb++giJHy0amR9aSX0dW1Gj5/bp6iSYVOVT1v1Dzo94s'
        b'YDgZK8lH0P2rOVG/+GU1qDS+uG4HaSoqXlm3UDQ2++k/Loz0GpsBhyUMjh4rJWKzysCisVlqeDYRY2UT8axsEFMMlu8ZeUTpJxuzaNHDMhulXGNOaDrAKjTC6X4ReQDJ'
        b'pGhsHRjKffOZOXbMCXsIDytGmIQuhMwVknF8M9GltBL9R2wuxHNQ1JhDrh6S1vBsQkZkE/LMbAjoFjNlTE8okKQnC32n5deibzzfhI/52CBIF/NoyjQyUuMbQl/UyXUs'
        b'jpp97Gqoq0EicgmaLZJ0v8RCPdkuZVqe0HcGbC+vQZ0U0RI2Nil6+GBDmQ3e1hE1kJV8cV2N/GminiXujSVeElHy+SW/QREtYdh+1/PJMATxLEaYg7+Ec0KC5j3/YyHM'
        b'YyHksbFbYwBKTSdC6q7x0vxZfEBw1tAj+AslfDrd2KNYmrSmpjIwtaaoDgUVAYGpMiTdjT1qkeRjj1U4n7HHJ/yCsQeoZ70ZjUop5UgIQ2P/2EMToQ3JbKWjkzFW5SEp'
        b'ViqtxZIF/kYCVsQz5bviqvoYIT6GgeSnMiy1ohuozsduVPwQBrBjniqqEOKLZz5RIqvFHRKFzxT3GNQ+nJL5QTIWYzldEhocEYE4bWyaMGAeIgh/PZMjy4pQaVPRoPKs'
        b'RARyD7UQ/hLOiRg7oW6Y0w1xz+LoATDAGGEi+sVIwnNCIp+ZfrBrk0eG72c/s74HIAZ1TzLtM/ZgjYEFkYiWmJCDmmfsEbFYVoIyTE9Crx6lRw7bUzaixtxTLqjjEJTc'
        b'oMWyrAY/T4qB5XoRborJxGYVZ/Twl9hgL2jikac6xQzC/pSopWbNyeEUAwp0EtyAx4rg8cz0IVSou2ADecI1cRwlpiirzkWLVifGTaWIJVqGMAe22MPTBCsqwD2NWKKB'
        b'C+DafALUBG8L9UD3ZoNdJKevClezvmdTM+PrZU6PrWdSddgYZFy9hz9KmpENd+Visx1wNiObcQ9AwYtwC8qzMY+qDzNeWGdCwGluVOeyXzag6jsdJlv/UdDo8heqbgK6'
        b'XceH+0dzB5Aungba0wvSyK6bRN8jANwJ2sxEC+Emsi0j2zdpC0duzqKo8rfvndxzMQfGm21Z8klzWLbyrMuCDR+y7OPPxvJcrG6mpOzp+LzBccsm1raXHG64/8HkmHhN'
        b'+iFl+/JpkeIV/Ye/+mHdD3GXA60uJ77aF5TeZbAq8OPNUSrzDZ42l9oS3Wp6rXp2/aPv/fLc9rb7974qfdT/wrd/H7eLN9ncz/KHvtNVSun71264rgp+MqPz1sdd8jWa'
        b'btd3Uo//Lb76hOY9l4VZX2sft35/5P2LtHn6j4KCmcdLTd/+4KzmzdpvL676+O5fHss/eSXna3pqmqWdzZQc4btz7e48Pn/4vaJ92i8XrFhrvOLa6bkbJr6Y9sHhfbX3'
        b'SlSf7jQRPwqvX//h7q+sDy+xuCz/tv3gTy+ZH//pA7OfjkX+zJO4ZXLOQZERgQApBi/EDPlgBbusndkSZ2sSFQCawUawYwmBB9Mhh8zPIFGiaQA7pctNB2e5lEFFzly2'
        b'RwVsZnaLr8Ht8KRuuzgwTh85ZEIW2UCFl+cFk/1TuB42j7qHOrh/ChTgNLEGA80LgMLUD7bC46M4IODCC8ZwM+Purhlu8pJjXpCEwTu+OCXcjU2umjigEyqtCPztMnAC'
        b'NmdmsULTWRQ7j+UHb8L1Isvf0vE4NsEUDuGBjLDeNhvUiQ9AglzUbd1OcaWEYrVbkGop9lHnpKhVEx91WifsHMhOpPXxVZgx2NGeymXt4k6Oxj6Mtg/DkdNYWh9/ZS02'
        b'tum07SztirhS0RPak9gTSkdMfhCR3RuRfa9EE5FHR+RpJPm0JF/tU6DgKqa3mWmd3JQGh2JpJ3FTclOy1s5V6am280Yf3Vv9tT5+CpzqaMyBmLbYwZR/wduikzSO8bRj'
        b'vJofj73czlVFq8eFN3G0tuMUpbRrgNoWf3TOEGgnf429mLYXd/J67cPV9uEPXf3U/jka11zaNVctyO1nc+yCtUHRncZdnuqglB5bFDAfbH/kq7LVCCRqgeT7h06emKzg'
        b'oUDr6q9YokrSuAbRrkFqQRDeA+3noAj8zeVYS7R8SVMyzfdU5tPY+kai5oejTyeX+R78fP/QXohhVSRDgdbRRyFRcTSOYtpRrOaLdVlbS9C3PAgzHNc6aRwFx5kkBXGg'
        b'0DTJnwP9efh3mCDZgnrZwiTZl/OywDR5POfl8Tz0m9kqtmS2iod2NzCT/ypwgBHMNrRX/ExmW4T3ipXUENTxVCcWC1fibxX8ZqYwn1Kj+NkhEybxs8PVeSvjNVANBjrf'
        b'Df8dj2ULReyaz6kR7o/dRpnNvZjZ/It8Zl4O8k70bAzJY+ZluMvKRO7PrpsaHoTB+tAAxloDt4FGBlYAt2q2K7wbMNUUtdcMagbYWEsM/b1cQ/KZJ1jwJoUGtOPwypy8'
        b'CsxSj0yZKbhz4lupT2YQC3UrCm4IJVb/W8CL2PJ/vh+DTLBl7upQDBTgDPZjrICpYC8DDCtgznEFpZpRAcHjGev9d0TMAbegcc0ezpJsxi48YvLAzSqH7MpiJuVbAnNy'
        b'vCyorEX4baA7k/KbGcyZsyDvPXVz+auZlOEiE3ISK2jcxgkxHC8m5Tpn5nhWUMQ0zhGfKuamzThDhqQys+TlE+t0WLVoVoKb8qdMmYIaJ5lKgXfABnjOgwE93QsueoQG'
        b'BWFYU9hOLYYdcIPQkHnsIGz1zAfb4NEpFAYGO4WqxxacIiCr8VAFzufD5rIhmAEMMWBZyZjIy7xDywOCgnQAA6bwIrGnXw1uw0sW9jq37rPgZQbfIXVhPtyHIR5CqBAj'
        b'C1Lj88AV2ATOGBO4AAklATsmk9eCG7PQJDgMFcCbC67a+xCCueAcPJc/RYhBFS/bGcBL4Aw45juPEQcb4JZQJFNtstPDB8A+4A/Cy4z9Pq7oCYbMWbqg6TUVr87V1am5'
        b'h+6mQbFfw9I1DFhlNTwMz+anzcF1SsEXqCJ4dQHJYncgcxoxKOfG1MfhLKYFsuF5VF1TgFJEUTFrTMevgsfAPriLAaPYIwIn5eahqLbY4EXUWKvg7fg4mbT7JZ68GhU/'
        b'9kDryYJuJIVZHZ73Qbezj+ejat6dF5onKU85FVkf8K3V3GhvaN1ooHGfUfljy47sW/fP/8Fz9/9suVqx+JN6+Vtb/2n8VlMiW/THLlNV7qs91TUrTVfc3Lr8p3t5bxaV'
        b'mB5pSXW/Ov/diLOfKnv3nPvs4OyNC3/s5LHubb66jPXlfaffiVssZrctaf/jpz+Wm96p9nxnzRnxhaiVmVviVnw25aPzHxlGPzb9bN7HDhc54QGJ/SdTF9Cflrd96nHr'
        b'8cyvjY/JqWOn3Z9M425/+Y+7C/ZW9jiXK45ZX/6jSf7vzC2m/X7LouSCnVM5Vbd2bHu7ZdkPqTd9Oh4WXjT4W2f1pS9apuQZTP77tiOFr4VJpLs/5J6uz3hrVpv8UtjZ'
        b'bkf2G+q1EX/8XckO6zeb26b/7t6nP3f7nXxfsGT9uc32H/+PbdbenLb178x4+0oed/xnjd0XAq7eO0/fAV/8nPun8/dLXj/qNu0v3VtizkXu/vEDz58Kv5Z0rElf1X+t'
        b'b30/9dLbkTavNczb6CbiM1LXKdiGPRaPdW4Ny1wOaHFAjq2dsyLW4OAWOAfa/GFLJRHnUBIjeJMN9iQsIlIg2AyOhyH5PotFcd1Z9uA6OGwGVOQoXj68m5gJj6aLfdP0'
        b'XDptBXdJvgvRUHdoGLJABNgGLoKDbuQ44WrwIuzOBLejn8b6o4QpPGN4p5R5/3pxgp7lP7htCpQRBsQs33VtATb7H7D5L4O72aHl4AaRUMPAPh/daUUBOKpv9m8BjhLq'
        b'HcKgEiMTDMISoFXWGbbHnGJyihHsK8VnEMkxRj/QOXiSkRxj9JxL3m8EO0DbkOAMN8MD4JK/P/N8lx9YnzmICgDOwwO4FizAC5xEsDGNcd6FRwTFIC6ACbw4CGO3Gd5l'
        b'zN1b88HNgWyyjZdhYD2LNZxkVJM3SR4TkbR8jZxlBHtg28B5RuY047x8cpySbwmv6Fv7w8PjwBFweR7T+tvhvkmZs/FJyQF7f2zsD45YMRgPDeAFF+Y8JbgkHDpSSc5T'
        b'gvOBpCnt4f5SgEap+NEOh8IL4CDcKjJ6bkEHj0dCof6RuG8o7JpnSMKRF5bKSmqJSG2ps8TPc6McnJp42D2zqVboSQuDGAAsjTCaFkb3Ux7Wosc4aEpjfHHVt008NHHQ'
        b'/xfxI23XNvvQbJV72/ym1EeBkdgB2Jl1Z9c1pSh8ldM1jv4avvgR3+0B37uX762sOb38+HKtwEkrcFWOa7NEedACSadtryBMLZjYxVcLUnr4jHOXgvZZnSyNIIQWhDwQ'
        b'RPUKorqsNYIJNAHeOmT5QCDpFUhURRpBEC0I6rRBMr0tLQjHcRY6319TGQC/Tjb2LEYLwhjTvDTaOXi0XLsSu5K6kmhBvC7ZoWyNwI8W+D0QBPUKMC4AQSfT4QIIooYR'
        b'Ht9lrxZk9KQ+fbO8J41OnvYgeX5v8nx14UJNcjmdXP7cyVwGamJ+JypMJC2IfCCY2IvqCRU7npDqqrRFfzOPubS7aLDnMxdStUMfVJLkQ+ltFocslDUqlrIGFejZEa5a'
        b'gRuirz/cKWjcY8rJ1/4JDr6LoASuzcsU5Rp7H9re53Gkk50Io9mJMIYd4g/8K4py8zhafqBcuUrjGkq7hiJ2shX0U6bWEY88vU9PPj752W3j9uxmJfVAe2HgAkEMLYh5'
        b'IIjvFWDgAh203xBDDfBVv7WxBBXB2AsVAQXf2Qwrgsr/sa2xVwRiUu892f18SuDSZPa0J6xnH0QlnrB+ubt9hBcVdZTOcj7F7b9sND8Fr5+eYIlc36msAaXv8I2n8+zB'
        b'1dn6YeeyBoNePUb6AfqPOJet+Y4asWgYzReQYQ7RnYELC1b6pyHJbkoamnnRFAvOFIDt4EoaEgkbxAEiAyoNbjGsBq3gGiNIKmYBBWxBEyc+Ms+pyILdLLBxDdzDONm4'
        b'Ao8vxGhQ9RRQ5tQDxTQilQZXgdP+uWyKlWcIN1JoFlLZyF6d8jZX/jWKjPzd8p1Tb1qAILMrLXeAvHij+bKXe9z6DV2UNhV7mgQCynhLaVHjy9tnhtZ9llvcNLvV5kxd'
        b'q/u3h/88YdIJe8VHlHQmN1ewJ/+OatEn3bBoSdTptnRx1Wbn+S9f8NOce19TW/HpFy1vSzr2n7oTsejVd7Vb95yNyL/fk5yaVgkOFfD32uw0qej98S2TZX+WRJ9sm9X3'
        b'scm5/mB+fqxP1tTo7f0Kqxtvv+eWkPj5l5e+KPnn32qSV312NcHjyvQbAXubF18Mzf/g55bi85UOXV95fRrPW/aopGXh1ei/fEcfjl12unO9vFoaeeQlO+uQ+83w4G55'
        b'8c8GhvtTUxz+IrJ8grvDJMsKUvNI/o7E+k4WOO+2msy4QtCJvYqKc3RmxEZI/t4AjrDXmCC5Ac/6nKjZOBpN4mg6ZFMGOWxnNL/vJ7MxaC2MwyKJOCAdR4IucIUyhZ1s'
        b'eAsqYAPJP9scTbmX4ZXljGYrBl6hjMFpNjjhC14kcDnTJwFVphiD427LCmCBW/AGZRrPhgoX0EDePw0JeZ34JYFmnrkSNsZT8luF4vCz1lHg0oC/ULAXbiIlxA5DPSPI'
        b's2IeYqBGcTrcsBzuRJKewXz2eLDZgIGK6gDHkDRCYHok4NDUABEbCSNHOUgM2ppOBIll0eAE9v2AZA+wPzCHRxnEsu1BWwhj0rFXDK5nDnKuMR+uL2WDY1FLGMihbnAX'
        b'nkVU78xJjmLqLZEtQNzI0A3ugFNgl76wWAN2sMDFaaCLvJk7CazHlME9y8XEnYiKLQYd8IV/G8t3QJvCjHxGBHVxcOSTFy1jnIge1ynuMtwp/rjWyP1xzXFKT8a4AuuP'
        b'olWJZydfyO7I7vLUiCfR4knkZk/iaxkg416tJrmATi4gtx46uqs9IjWOUbRjlJofhdFWzQ6Y4ekLiS629vtjmmP2xLbGPrD17bX1VY3T2AbRtkHYgae/1tFd4aP0VHFU'
        b'czWOMbRjTFOS1tv/9OLji48taV8ypCRrM1FwFaVoIsEZKwtUYcwUpCYfLd9+f3pz+h4deGVT5iMnl0ORR+MOxKk8NU6BtFMgzsNHK3A8anTASMnHhCkshr2HbedPAt17'
        b'XNwVBUqPdp/T4uNiVW1ngcYjhvaI6UrWuCTQLgkoNwf/njyts+vRtANpyoK2nEM5ipx+DrpLokjwGAdPqGH3RguwSm602/2cAZrkeBR8xW5cSiTvlUhuygTjV+JYKGSm'
        b'QmNmKvz7L86HDHvgrYpBXduYzOGG1v/y9dQAJOcq4S86Qf0P+UQlXiJF3BGG2MwlKT6b/M4R2YyElzFhUfoYM89h1tLBIq69a6VL5AxIzDcDtSOy/g2163qNgat//ch/'
        b'TKNcwI0yaGfvjmWUt9jDwWS4XHMrjHdi1W9GWdg1zFBylEmKFZ0lPfn3bHvStQ7OSv8u2678LuN7SYg1LaZiDCQUPiFhvwEVF8/q5/hg3JlfDB7z9J7k4rt5rGEoMxEY'
        b'ZSYKo8xEYZSZKIIy4zRe4au1wk5MGZwaJ4xT44RxapwiGjJHoMyEY5SZSIwyE4lRZiIJyoytUxPKgeAw8YNRAttQlMA29AkOGpJGJIjDCeJZOEU86wkJSRr9twTht4Tg'
        b't4Tgt4Q8BXYzSgIjUruoJ1pksxTyTlvmFxNiWKdaRbIiWelAu0d2GdPuiQ/c03rd0zTuGbR7hsY5k3bO1Lp6KEqV0fT46C5venzCg/GTe8dP1oxPp8ena1wzaNeMxxyW'
        b'SyZuHkEWrmQUos4/+I5+gzqWuaSf+m3Cx4Y4zyf6OVdyos1d+qlfDpaxSFUoxqvNXTXmrrS5az+bb44GqV8MHnMoC7en0zNQJ3genSmGt+TWYMegfodHmTuyYYuwQsTK'
        b'kV1cfYUrn426xJwL367Z/UbOC1OsNn9S010t+mfgkmN/P33N6YOXd06YEZDt3RW09Fh22MuVWbYGc50+WJ9d2Lshb/Yi8eu8kE8OVb35zyOvhkSU2M256PKF2/eLohfE'
        b'f+jzRhZV8X2FGz835Oc7cRXTwjYe5k4+cSBnVkzVu9EXJmh+DNy7auo7C70+WTkrm8qpvObxStWE+z/XeZp899Krkq9OXm5d5RpT9+rp6l3L2t/45Btew60/FZ+xaN65'
        b'8mvFNwFf/Sm7KWnJ51OPGoS1W+8UKR3eSLJ/eDXnKiuy58Zr8qO1qs7uP2jvm3k7TOg1MXkwzbfzjUWfcEK+vHvmy6YDe9+X3v5u8v7XU/7U9N4r7Qbdty7OCfv6fk5c'
        b'9mc73vysOeyNRMsffu9AzyldHfHOwxns2+22s7JmRB2L+Mr1/GE64Fvfj7/66ou3N1WcuhFV/HlXTva5S3Pev++3aoU04FHp+41vXzFa9ak8Lurd+/FdnE8e27+ZXbd+'
        b'12ERh3ifiBAFwsaF07NY2K8WEomOgW2MELVnIlhvOhFsGbKkHdgYNaCIR2V42ADsGeFhHey0GNzjdA4UeY4cBY2eGfwnxtx/YZT2ZCSqePLvqeF6xMDdZ1RYWFFVVFpY'
        b'uHLwFxG1/sAZNHFEY3cYZW7XzzU0ttda2jTIm0K2Ld+xXOG+fXXDaoVcIVeGKIvaw9tWHlqpmnpgnWJdpyf6q+lyv1LXNfVK/cWAKwE9yT3J92xeSns5rTckSx2S9VDg'
        b'qAhRFB0KbzM+ZKzM0AgCOu01gih1bI7GPkedV6CeNp3Om9FrP0NtP+PhOKHSZk9la6XayrOfQwlmsvpNKBt+U0KrXUNiQ+L3/YYs43SW1satSXLSTC1J1Qgn08LJGps0'
        b'2iZNbZaG5ZUoa2PPfuo3CXx9jNHI9GuDxzh4MnSvgBVr7NhPPStomv4Yfz0ZuruW5Yl/PitQjHuMv54M3c1hUSZW/ewarjEawv4vho9J+IT5zUHE7hinI7fWmBJ4q0w1'
        b'9qENZv0GRsZIVBsrGFfDMXZG+f1Hw8ckfKJ/f5Ehqd08Upr//fAxCZ8wvwfqcmQiOTbi254wKdGWAraOiRLdJrlLH7uw8F/cFP/PDGR4HF8w/FjHaKKnNRuLngODF56c'
        b'5Z9QOvVYMItlhQX8/3vBb2bYjRfQ54wTONRLHIsEa45MNLeDK7+Cbk6zmbhkZ7QJO8EqZVXhq7zkasibm/ORnUH2jVAYbPv5nG6FY1t9+lZru5cy1k78fNLnIeNTDpjN'
        b'qvlINKX9Q7+MWds9dx23iRT99PuXVn+3quPow/rVsyfPev3gT5+0fv5a3tWT73sWupm/5i2xr/v8o0sL33kvyyT60lsbkmCEXfcr3tdnRf41z2f5u+ksnjmncZxz36dg'
        b'vHJrnIGgeFOwt8KjeBfPRHwROB582P7kdM+3Fdc9vjzacz1o7Y/9IkuyabMQ3IZKrFrJxWfZOsEuuCPTkDIFl9hQBe+sIjP8Ekd4MzNXAi/iVIXgPFbBWMNb2B/S9Uzm'
        b'dNIe4+mgEezGIMo7svEGnCFlAS6BUzYcV3gEXmAArU+BDtCQmZ7tl21IGcAdnly2Eexaw8R1Awyr3bgI3g40oFj52DfqZrCXCB5gG2wu9y91yOBRrEwKKpbCNqJWYtmB'
        b'G9j3HyIZdK3LxtDIpiI29k0IOpmNnu6V9XImQVwBiTdJZ4NOeMubRHt7gfOZRKrcpnOvun413M7JsfNhMLYV8+Bl3fFCcBKewkcM4T7QQrQ35pHwAFFKpsFGE3iIqM3M'
        b'bNnwis86ohVbtQLuxnDP4mpUt2eySLwJuMwGV8ABeIwBFznvC++ARhtwHF4yAw3Ll9bBy0vNltaxKHu4mwN2wE4RI1+1gyOGmQTPHDvRvZ6N/VeaggNseLxESnIqAOfB'
        b'DtCY5w52B2Yi4WoXPhuGm8OQcvLkghdAs0zk+9yy1f9JUUtvrPIlQlf8wL9niF3D8CWMhkGKFLH0YCXw8OVI8WzX5+A/rTn/gblrr7nr4XqNuS9t7rs+Vcs12Zq1MUtt'
        b'7X4ySsMV01yxmivWcs3Xp+M/vR9u6uEfLddHPdpHy5WoR/touePVwz/9BrOteGg6+f8qrBdSZvz1uXrbMm59nAppZR8Xm1P38WrrqiukfdwKmby2j4t3Wvq4VdUomiOv'
        b'renjFa+olcr7uMVVVRV9HFllbR+vDE046KsGW1/08Yjhcx+npLymj1NVU9pnUCarqJWiiyVF1X2clbLqPl6RvEQm6+OUS+tREpS9iUw+gF/XZ1BdV1whK+kzZKAC5X2m'
        b'8nJZWW2htKamqqbPvLqoRi4tlMmrsIFon3ldZUl5kaxSWloorS/pMy4slEsR9YWFfQaMQeXQNC7Hw+mCZ/0TCof4kQQm+DHJMFYc5R/iTmsWq5SDJ7P/n8PfbB7GUtVL'
        b'JsYJQuoloUVCAOcfRmXY4rukPKDPqrBQ91snpPzDUXctrC4qWVy0UKoDiywqlZbmiIyIMrDPsLCwqKICyWSkZbC6sM8EcUtNrXy5rLa8z6CiqqSoQt5nloeNT5dIUzCn'
        b'1MSzdczNsDlu2X8YxS6pKq2rkMbVpLIZpAn5GhT0c1gsFi4zt5/CgQVlar7esJ9bYcXi91N64Xx3ytj6gZFTr5GTIkNj5EMb+fRTbFa4WhzX493j/ZLvy75qcQb6aI2s'
        b'tCbjGsRq+1CNSRhtEqbmhmkpKzVl1STQUI405age+BDy/h8GE3lj'
    ))))
