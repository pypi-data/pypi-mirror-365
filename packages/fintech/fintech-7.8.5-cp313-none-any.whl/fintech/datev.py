
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
        b'eJzsfXlck1e68JuVJSyBBAirLzsBEvbdDVBkBw1xFwgQIAoBs7hg3bWiuEDVCmoVlypWrVi0xa2157SdTqfTS0pbkPb2Ovt07sx81jp1pnNn+p1z3iQECbadmXvv98fH'
        b'T0/Ovj7n2c45z/sLyuaPY/79ah1yDlMKSkfFUTqWguVH6djLOQucqEl/CnYKi/FFmWNUAhTLWc4LoVLMMVnofx0qm8tezg+hFFxLCTVruUMItdxaA0018JzqpfxvNjrP'
        b'ya6Yu5BubqkzNqnplnra0Kimy9cbGlu0dJ5Ga1DXNtKtqtpVqga13Nm5olGjt+StU9drtGo9XW/U1ho0LVo9rdLW0bVNKr1erXc2tNC1OrXKoKaZBupUBhWtXlfbqNI2'
        b'qOl6TZNaL3euDbAZXyD6L8BT8gFyKqlKViW7klPJreRV8isdKh0rnSqdKwWVLpWulW6V7pXCSo9Kz0pRpbjSq9K70qdSUulb6VfpXxlwmFL6K32UnkpHpYPSVclVuiud'
        b'lSKli9JJ6aWklBylUClW8pRuSl+lt1KglCj5SraSpfRTBig9kgPxAqx01AZW+I9PqjYoiFIGjoeVQeN+msoOzA4Ko4LtxNZTMzjTqHqW0w4pu7TWdin90H8RHiqXrH4D'
        b'JXUubXLEVYs4FLe8CkFHdfGHbmGUMRxFwg64C14rVqLf3WXF82E73FcmhfsKlOUyPhU5lwvfAC87SFlGXKs3zdYXlMD9cG8J3Mui4EsOzgVs0A+2rZSyjT4oA9gBrsEe'
        b'cBKeLyqILeBRXC4LnAybZ/THDXX5ghdx9KpIGdyNquBRbnAPpxQcWIxKB6EcKzRwAHTAPbGtqDN7UXGwD3Q5gwE2qvTAUmMYypIBTjuiLK+4gPa1q41wYLULcrfBEyzK'
        b'Bx7ggL3gJXgFdRZnXbMSdb0DHgQXwYG4Ilk07jY8ADrAAQfKP4wLtifC27Usm3nzt8zbIeTM9KtEc4cWlIuWk0LL6ICW3AkttgAttitaYHe01B4IEERowb3QYvugxfZF'
        b'C+2vDEj2Ny80q8LBZqHZaKFZNgvNnrCkrGw2WehJsVMvtM+khQ5kFnrvHD7lQlHC+IVHEz7JZlEkcqUzm8IZ49cc9flAq2Yi42gnSoji4uvnlq9QrWYifyviUuiXjl+z'
        b'3KvENY+6QDU5o+jZtb7cR94/pSnqZ5EP2a8mpFcvpJoIKknuZvU7UIt/Wlad+JlueVosE10w/6H7IXeW48Ml91l/X7y01YUao4xxGEq6wQt8tMQdcfOjouCeuHwZ3AMu'
        b'VEQVlsADsfICWWEJi9K6g6vznGaAO7BnwiIJLGM24EUSmBeJN2GBKLxEyQLrInD/hYtQ/+QiOExaBJdSHZ5FoxcG+iPgZLkI7FIskC1kU2wOBV/QRRlx/lBwHpxWsCn4'
        b'LDhDhVKhbnAXKQHOgb0J4DA8rVjApqhGai4YhKeNYpzyBjjhDg9yKPCKA8LnceBV0Gn0QAkKsC8ZHmRRdSGUjJKBcxTJvtEJHiwErytK5sN9PIq9gRUwfyXZ8eAKDW7i'
        b'HRZTyS5Ce2J38fwocCE2n+x4ObzAA9taVpCK4cvrPcAAn2oLpqZT05eBQ5rOL/zY+k9Q0qd/+Li565YziJfsLPuwaCxvdVS64zZxtk9ax7GBjqI36uSKSI95b7597+1F'
        b'rY81z/Cn/eij1Kvd9d/8OOM3f3X/8fOzej9kR8c4vf6b48o/7Pigef+/+w8uuJ+TnJE42/OwJnbvq9N8GxbMFr1dNPbnI7KfxSeUvrTb8X6g77tD3yxafefyr5oDDqy/'
        b'fcq07vK9enn48uiFhpI7v3w0696n0ueulmQ+/GkX58DRtIq3b9Zd+XTYI8frTwZ/2Bjyuy/g9E8Efd3DopTfal/+D9MHkSBhe/Hc3+k3z8qa1/Yt9cavogqPNUt5j6ah'
        b'waXAQ4tBD+wvgvti4L4SWSHGZZ5wkINQ5R448MgXz82dHEFMoQy2FxSXLlnMowTgKhu+UAhPPcJ4xAc8mxsjlxbGmDEdOAOuu8MtnJbEGtICuAB3baoEFwR44o0IOe2J'
        b'Y1Me8CYHXEYNXyZ1wFvwVgN8DpxDa7UHHoB7EfbOYIGrcKuf1HWMHSXVoZ1L/YOO3hXDNr1l/G/Me3q9rqVNrUX0k1BmOaKq6jUzx1x1am2dWlelU9e26Op0nqggG9fA'
        b'Rvvyz1uoL59hUd5+3REHl7fnfRYQ3lv/SYCsy7GTNSqSdM0YpUM687oTDhbc85rWy+vVj3jFmLxiRumIPq8rgRcC+/WDc4al2SY6206ue3Ro79wzzjYpfby+tUORaSNe'
        b'6SavdHPyCJ1oohP7kwY5w/R021oMI16xJq9YlO1Ubh/vTOEZd9uauH2N1ppG6fDzbqfc+tYM06lMnl/6hQ6FpdzgDipvCUxhucN+c4bEc74MpALlD4Iosc+R9K707rxh'
        b'UeiQS+hXGAnoMBaQuo3xmTkac6iq0hm1VVVjgqqq2ia1SmtsRTH/4Eq5Iad6wlLp8OYkC0GcWThXBnL+soV6vIHFYokfU8j5mZtPx6otggdsHkt8T+DZkfEzrvuOklFH'
        b'93uOoj9/yaN4QkvoGz1GWMf4MdRFQSpnAnqzspIE3/IOU8sxI4nYSAVLx1GwdVz0nxdP6fjo10HB0TkqnJVUMkvBxbh3JUvnREI8HNIxKXzix1iapWQncxQOJOxCuCcu'
        b'CjuSsKvCSefWwEb4VjDGX0Bm9QsF6kIpmepajk0XuRYM3Ii7yGKYu8O4eoo0wJABToUNJ6vlIjLAsSED3AkIn5PNJWRgUuzUtJgziQxwGVr8t1WEmMZnzqkurqFdKc2y'
        b'gwKWXoVSDB7uA7Un3hOCgLe2OOUsXry1TirqfPs4dBT9lHOh/s2KwLf2S73fq3b+2Of9PsGHP2lf0RKfGxUqeNc7YjC1u53V7rDIF5xlqcOdty4XvbXv7evF8bfEkg+3'
        b'diYFUkv2uFzqVUv5jzALDK7qK2KsDFAMH+5IpNzBOU5bPdhJEA246QC6mBzgADyKc3Eol1iOQ0Q4g4h2Rqwugh3FiCuU8sF28CrlCPaw18EueO2RhKBC2FmKCUpRAbhM'
        b'Ufx0eRvbdw3oYCq/Ay/MBR1liPHjUjx4HLGHu1nwJngNdhE8Cq7DV+BAjCwfM4xg/wzKEV5jgx1CSsqbekvwLMiL7IQxx6oqjVZjQPvNnQEVuSWCIKpqiiCqBwY2FRt/'
        b'ZcaFGYM+pphskzCqk3vIpXvlqFhypKiraEQcbhKH964cFif0Z5vEKQiDBYWcXNWzqi+kL6G7BeUVjAZOQz/On4t8zGV6uR+Lwx9wKLFEJ7KiAf4YV69uqh/jYqlkzGGN'
        b'WqdHAowOE3edt3UIfLyrq/G+ZnZzCHZCkbMMpyYj569oNyMkywr+ARv5Kwxyh/nh1IuCeE4t294uqbPuEmaPJLPNO4Q9gVHiBE1gg2x3C9oL7GwO2SGTYqfeIdYO2OwQ'
        b'oxT5Y5DYIID7EADtRywhPKDIZ2BtfvyGcsI2zYKn+B5B8JpmTcmvuPocVMRvWtDAu061R9HmEQIJ2j6XfH0lnn+RSE73qELe3BvscrPJxeXcXuGm6NDySMG5D+g1xVeF'
        b'g3Iv/gcG6t2/8fVX9FLuIyzRwBttcCuCbXiqhAFvBrSF4MSjYAycZ2JL4QCi4QdAL6L9B+SyVjOt9tvEBTtXrH6EefBMd7jTBsJZOZvgzeXw+Ud4tMYIn6IyGYtir2Eh'
        b'yO/MBq+ypGwbSMZLZAFjRCwa1AaNQd2MINnTCsnWOALMqWZgnoOhrttwckPPhmFR9Gd+4UMRmYMVpojsYb+cIXHOqI//kbautiObujb11g37xAwJY2xAlKfDEtIYV6tq'
        b'Vj8JmDwCmFa4lGMHc+21Frj8Zgv1dS6HxZL8ULg8yA+lzgjknP917N3wvWAzGvkdwrImgWYxOI+h0wY2EQ5r1ygOj/EIcF5kb2Tw+neAZq2jqDxOcO5zId9I9yR5fHC3'
        b'h0UtbuafO7lCyiHAmekKXrbiXQKY8GbJOoQ5LzyiUfJqOFjAAKctYG5MYEAToV+MXpcjLvKwDXCmwQ6EfWHPcinnSaTKIaA4Dot6O7ConwCLCWZYLP0OWAxFmPaIc5dz'
        b'd/KHQtoWUxIw1MXjBnlrVE3GScD4JJZMw046hQUjGyxZgqBx2g+ARl0khme72JFAIceKHbFgSSVz/1sw5CQo5E2CQl6pEe8/GegJwpqTio1a2C6TyefnFyphe5mCEdvy'
        b'kQQnZ1EGeMeJD/rhi8YYVMQDtKvtIlUEtovhfivkHoVnNSxFCEvfggo9ruUO1PYgyL30FoJdUPfeWxTfT7gneOexrcFHPd5TOdYn73xF4Zsr2ek7XewreSjJ8c1ZvK1b'
        b'Er8lpbzZufyzReJGfsxnLufK+StS+fwdBZ+5ONOi0fgSx5+/JRZsvZW9NfiFrXRAEocS9gp+Tx9F0hbhT075rJ0kB8GLzuCy0o1B0u3e8JR5IyydbsHRcDvsfYQJJrwF'
        b'BhJF8MbkvUB2AjwI9jHVnJQ4gHY4aIuq0VboQ9UQRuQEfAXsIYxIVAaS9xg+ZBl84TsZEStLPsY3tmKhaczVvGGYINkrS5m98uViDiUJ6Q3r4474yEw+ss+wpDFr2G/2'
        b'kHj2pwF05xyEuHuTz2edyvrYR/5ZkHQoeuZdsSl67nBQ3pAkD4FxYPADPuXhhbfTiDDYJAzuDftYGGmzqRyYTYUl/Sd2k02/HSgzkrcIE9nYwdirmTILEwjNP16E0fwD'
        b'6ofhemZ32SptJvIeHKK0IXo1K35nVXD+O5U0k/E7p1SzsbeDrcc9+vrOQ4Kw3+/9Nwk4jUDfG6HtYt/ga/IYTm5Qvqvo3FF6Yew3vdfit+9y5uRKyxdtFa7x3zaa8HaO'
        b'r+rrXyfMi9qReJGz5PWVLi63vRDMuwRfKnQ51br2QnzrqxRVNF2wMN3DzG+A2+BWtA1Oh1vgHgzM2X6EkwgpyrBAJzicwgCozMxlgyM+4AbsiC2A+2R8qngDv5IdioB3'
        b'FwHe6hxwaZwDDwK9/HS2L+yB7QgcvoeIicGBpm04aiTA6g06hPrdxlE/DhNQXs6A8oNGDuU/rdv7VGhv3flVp1YNhySafBM7+aOhkeczT2WOhCaZQpM+CU3pKkJQLQk4'
        b'KegRjEikJom0L2xYEteZjcRuLGsj4AlL/ZJPScJ7Fw77xA4JYydTiCnhmNAHGzAuwE4hcoyUmT5gmbgBgbHnD4FgTNiknDFeFWHh+fUadVOdXheBY9mlX/wdwbbUHUsd'
        b'mH9Ck+RcVcUcWyC/S1XVaqOqyZziXlVVr9HpDU0arVrbUlXF0DrHWoQVGlp068cczdIBU7mumLJIAoTtSrPuTDyuMS+8CCqDprZKZTDoNDVGg1pfVfVd6MlGYyCxOFiS'
        b'1mfiZXyWui/yacdYpz1/1McXOd5+7fNGvXza8x5z+a4RfxJyXGP/5MxxlT525rtGPRbyXGUPKeSQRTLiNYlYDgYFhSVw/zPyuEIW5ejCrgbPsSdRNvz3FcaCM1l2tAgc'
        b'HU/BVfAUfDlbx/elllAhlMJhgTs16U/haDlmsvzqHBVOOqcGZ6dGrCuYq0UcyvovNqKEb8Rz1DUaQ4tOrY0r0qnrGO8XQrKMX2BU8I3nQrWuzdigb1UZ9bWNqiY1nYSS'
        b'cHe/cSlWG9oMajpPp9EbLrB1JSjyi3fQBvhTjyfa1S1aQ0tWKVplOiq7TqfW69GSag3rW2ml1qDWadWNzWqtNMsmoG9QNyDXoNLW2S2nVRngbV2TnC5HINGCyi5s0Wm/'
        b'Tz57la1SI4Cjs7UNqhq1NGtCWlaRUddWo25Ta2obtUZtQ9ZcpawYdwr9KhUGWUFdqU6ela1FE6bOqkDcXlNc9ipVnZyep1PVoarUTXrMAzaRdrX6NS06VHObpQ2dIUth'
        b'0KngSXVWeYveUK+qbSSeJrXG0KZqbMoqQzlIc2jm9ei3zWhT3BKoWYt7h9WOtLkjKEpOLzXqUcNNNp2nE6ZMScwqUmu1bXK6qEWH6m5tQbVp21SkHbW5PTU9D95uMmga'
        b'6DUt2klxNRp9VoW6SV2P0nLUSFJaheuNMkdJLWn0PDWCHXi23qDHo8RTOjk3Pa9YmjVXVqLSNNmmMjHSrAIGTgy2aZY4aVaeap1tAgpKsxQIaaBOqm0TLHHSrByVdpVl'
        b'ytEc4eDEWcMxqzAMy0qNzagCFFUMz2I97yo8a8z0o8iCnOxSnKZW6+oREkRexaKCvApZbgtaG/Pkk72g0TYiWMP1mKc9X2VsNchwOwjH1cjNbZr9E+bdXjye+wmDSJw0'
        b'iMTJg0i0N4hEZhCJ44NItB1Eop1BJE41iESbziZOMYjEqQeRNGkQSZMHkWRvEEnMIJLGB5FkO4gkO4NImmoQSTadTZpiEElTDyJ50iCSJw8i2d4gkplBJI8PItl2EMl2'
        b'BpE81SCSbTqbPMUgkqceRMqkQaRMHkSKvUGkMINIGR9Eiu0gUuwMImWqQaTYdDZlikGkTBjE+EZE+0mnUderGPw4T2eEJ+tbdM0IMRcZMarTkjEgbKxGYrUl0KpDCBlh'
        b'P62+VaeubWxF+FqL4hEuNujUBpwDpdeoVboaNFEoOEeDGRS1jCF32UY9JihtiB3KWgTPNurQvOn1pAGM9Rga26Rp1hjoKDPplWYtRdON89WgRG0DzpcHzzY1aRoQjTLQ'
        b'Gi1doUJ00aaAgqwBTikn51G2lY2TcdlS1AuEMKJw8QkJ5vIoKXxygcSpCyTaLZBE5+iMBpQ8uRxJT566wmS7FaZMXSCFFChRMXSZzDniSxB/QuIM6nUGqwdhIqs3yTar'
        b'3pqNWYgcNSLHDTYR4VlLNVq0Gnj9STs4qQ1FYdKLsPSEYOLEIEI/Kr0BUTudpt6AoaZe1Yj6jzJp61SoM9oaBLbWFTfo4NkGBEQF2jrNGjmdx9AP21DihFDShFDyhFDK'
        b'hFDqhFDahFD6hFDGxNbjJwYn9iZhYncSJvYnYWKHElLssCl01ALzrOrNjIZ0nDGyl2jmlewlWdinqdKsqMxOepn91jDfZS9+Ais29Riekj4Vd/ZDMidO3fIEPu37ZEOo'
        b'0l62CSQgdRIJSJ1MAlLtkYBUhgSkjmPjVFsSkGqHBKRORQJSbVB96hQkIHVqOpY2aRBpkweRZm8Qacwg0sYHkWY7iDQ7g0ibahBpNp1Nm2IQaVMPIn3SINInDyLd3iDS'
        b'mUGkjw8i3XYQ6XYGkT7VINJtOps+xSDSpx5ExqRBZEweRIa9QWQwg8gYH0SG7SAy7AwiY6pBZNh0NmOKQWRMPQiEICfJCvF2hIV4u9JCvFlciLdhU+InCAzx9iSG+ClF'
        b'hnhb2SB+KqEhfsJ4zF3M06mb6/TrEZZpRnhb39K0BnESWYq55dkyQq0Mep26HhFBLaZ5dqMT7Ucn2Y9Oth+dYj861X50mv3odPvRGVMMJx4j9FVaeLu13qDW02XlZQoz'
        b'A4eJub5VjeRhhpkcJ+Y2sRbybRM1T10Db2NK/wTb0MDEm7kGSyhxQigpq9ysXLEpPEntkjA5KnFyFBJzmrBQrDJgvpRWGFF1qmY1IqMqg1GP2VpmNHSzSmtE5IVuUDNg'
        b'isihPTWA1KaIBhN3TR0p9p2Z7dRvhyjZr3tyRqJiGp8dGjHftJnlJVNZj9PNk8z4E238WCYc11SNsbKI6rT0grOuFGvHyrBTjp35lPmwTbcAO1gJOMbTtzZpDIzisQIr'
        b'xliM5hDr1sxaw4UWB+vU9FkWraEUaw192/Mf8CnvuFGvqC8duBK39vyHzpS3/wNuvEcu63ENi3IX71Z35nas/KqBleTt15HHqA2xyrp2EbylxxfsdgvCY8EFLuWYyt4E'
        b'n4fP/S9oDndIBWPO2bW1LUatAQkpX9zGU+OWg8CLkXBUreqmL7wYvSGe3G/85iCAa0ZcDNaN04yMhbaLBiE5lAXffh3jYm5LV4m8f7qNIpTNDPPU0qhV04qWpqa4fIT9'
        b'tLKiNqzLGQ+O49OsRUVLaaYY1tlhTK3X6I1MBE6zDTP7ex5WMTKyBNNQjlKmqG1sgrcRnDUh/sc2mJWjblI31OGBMF6zgmfcn2iWxbIsM0FkC8x8qs1oxCIg0gwDZhYz'
        b'xxViZgGTiAVYtESZ0UY2EBHEXANprkmDMhCfRlvfQsvobJ3B0hVzTIEWl3wiEmdLtJctcVK2JHvZkiZlS7aXLXlSthR72VImZUu1ly11UrY0e9nSJmVLt5cN8TNliooE'
        b'FFHELAzmq9UkMnFSJArQJWqEmy1aX9oop8e1viiSgWWLGlZOY9nAIuEz6t3xZaSLY4qz8ozaVeSFhlrXgJBhG0ZgOD5HSSdnMCS93pIFq5/txZvhhkmyU2HWUiJ64IHr'
        b'mlU40Qoi9lKsoDJVscSnFbOfyIDQU4rZT2RA6inF7CcyIPaUYvYTGZB7SjH7iQwIPqWY/UQGJJ9SzH4iLpbxtGL2E8lyxz91ve2nkoJPB5SpISXhqaAyRSop+FRgmSKV'
        b'FHwquEyRSgo+FWCmSCUFnwoyU6SSgk8FmilSScGngs0UqaTgUwFnilSy458KOShVYYC3a1ch0rUWEV8DYYLXqjV6dVYeIvHj2A+hQ5W2SYX1mPqVqkYdqrVBjXJo1ZgB'
        b'G1dsmiknRnjZxnqsgrMiOQstRUkY844TZDoqW9vGMN/47BAh4xKNAZFGdR3iQFSGJ5KfwMOTC49j8ifTdE3wVb2ZTZiQkk9OkuoNiCuxinCEksgIv2NX3jCP1EzNEelH'
        b'lAaz6/WEUW/GBN6g1qBpMVh10gWIqzZo6jWrVLbYfykROa26als2gxFUbc4sbdmkPDUjxag1NTipGK0aPoTTM5zN1IyarR4a9Ru1rGoyNq9SN1qU5oQIEi4OX9dmuGpd'
        b'jX0mWW1xMOuoT7cwyaE2THLaqBc9kUmWeEx/nDjOIqf5j3PI+D0cuCEU6ItL4f44wiaD7Qq4t8iB8qrhuhjhtQlssquFTf456tNM8WQ2GTHG/BAKuQL8X8FBrgj/Z1jn'
        b'DIcgKohShCh5SlelyHIJfyXLcr9GxyMvPp38KIWzQpDB1jmQsAsKu5KwIwm7obA7CTuRsBCFPUjYmYQ9UVhEwgISFqOwFwm7kLA3CvuQsCvuSTJbISGPAdwm9F70Hf+d'
        b'FL4ZzmQ8oUq2eURchd8TI3KfOCPovzP6z0pmm2txsPom1u2f4YRqDlMytwPxW0Ahqt9BEfBE/UJFOMrDUzqSF4OeJE+g+VGEB4r3QKMLIqPztPZEpJiWwTK/OXRTuifz'
        b'FDTOYa1TpAjWiRsckLgSMeY4B7/OyVUs/OIXKKnNx9kSphn8xryVdb7A02HJSYfv7HyBb8voNNiHr+MS2UTq8gWG4i/wxZ4v8A3Q8ew6nSW7To+dVTgLfgj4BX6E94UL'
        b'Lu0w5qyqW4PQpK5KUzfmVIuQldaAvW4qRpqqakLcpqFxzLHWiPaxtnb9mCO+ma9RNTFXXsYE5H5MVTPCIY2ltY42MI2bIpe2tlCWO5m2j3bJwz8WWmGu0gHNF/Psj5/s'
        b'bL5R5ljhbHOjDK2Z0tHmRpnThLtjjtlO5EbZpFjb2+zGM2iOnAuYzmva1HrymNk66xpytaMWv2PORFKPqpken5hM8zNlhNmwwsv8Dto8QyqtwRnfvYrKQQjIYEF/Ujmd'
        b'jfMjVFVLk6uxtLGVRgg7ja7TNGgMermlGeuc22+FSWZasB7TfEcbKU+2MXExM+li8oubmBdXbEk1N6xn2sLkCRMGRFbkdEUjIhUILtW03ljTpK5rQP2zW4q508LIsKgk'
        b'rUJFUJjpD93UgsiUTk4XGOhmI5JkatSklMrc+Rq1Ya0aHzPTUXXqepWxySAlr8bTx+fKDISZdK7ZR9divWSU9TTTRp8ptZSyAGwmbV59vXVy8SP0Fh0dxdyFWQVv69qQ'
        b'nG0paL7clUmEKMxwoGLMGpn3aJS6QU6nJMTH0mkJ8dZiNjsik87DAZoEcPF6jRZBGeoDvV6tQg1Ha9Vr8VHpmlR5sjwhWip3/o4rxS7Ms6RLbCGCcUo4fV21S4rMkTLO'
        b'RJHw2qJw2FECLoCt4FI5bC+A+4ri4O5yfNc4v1gKO2JLZWAPPFA8Px9czi8tKSkoYVGwC/S6tKSBvaTeB5mulISi0n+3pLpYFj2bMk7H9Z7zX4nrtdYpACcs1cL9cHcx'
        b'om9g95P17ljvQm3IJLW+70SeKZcrVlY3PTdLSBkx6oAX2/zIM1bzI9Z8uQy+HhNdiBoAL3Op1OV8/TpwlrzFJZX8ZoMDfhVNKeTVLovcCinjbExjL2hgP+wA7eBqyaQx'
        b'w3ZUc0cs7uBe6UKbvoEbOgF4BRV8TbN97jS2/kVU03O+zw38Ar9I8UWDozjBe2cHhR7/0bm3hID11t5z5QmSwPcbU3ZuDe7Cl6m9zmV2O0Uce08CuMm7fGFAhIu++2o3'
        b'3FbnphdGcvjxO3t+coIzwnt1+4x2QcfK7hWXFv5KsuZq8L23V/6kj+VVpqqpLq92rHf/+dursrKO/uGZdU01//Wbuz9XlIZ9mv3r1Xd/Wst6eH9mGvXj1aceDKpuG/Cz'
        b'l0tF0z4X/lXqwly5fi0yCnSMv4rnqMFWyj2cU18FdpC3BfA0OFANOspsF53lmU75we3ctk3wEnnaVb4QdAjQ5Of4SEssd7e9wC6u47JmUslaeAycR5XA/W3wus0qsyjv'
        b'YK6gLIZceU1JhgfhDnAtRhaVL2NTfHCULQODJaQCL3AKdaSjTC4jq1qF6kML6wle5qB1Pwr3kQoqwKvwdfDCihi5FO6JpVANl9hJNU3kmW0YvBkHOvDbWcsygqsrpXzK'
        b'cw0H3Fk57xG2dQG35oIrqBGw3cfCa+FemuGAouLhTr4cge8jfBN1cwbArylQbdFwGzwnxznhPnggBuek9TzXaWhucNezwS54FefEnBtu2huel6GGwREO3NkGXiA31xF4'
        b'avEkW1k8zN+hznRTfmCQCzrAtQqp8z/wYhRTzidfi+JbpWMeFnI18YGciWIu9K5xoILxozjX0VBZJ/cjIX1P5N2l7848uHlYFNkXPCyK+cwvbCg8f9ivYEhcMBoSg/K6'
        b'M3kyDm4aFkX0eZD3HyjPvGG//CFx/miw9HzQqaDh4ASU1Q1l7TTgJ0k4q7W6tGG/9CFx+mhI9Hl5X81IcJopOG04OGNSAWvdecN+84bE8+5HpuBOho2GxeHf4NHgUFxm'
        b'NDS8k/vxhHcmrswt4jbsbMDOM9jB6mzdJuyQu7ebqaddNMYMdrX5z+a+Mbmrux+zQzgTxnXfool8XObAYtWyvqaw+0Of4Z7iJ1BXBdM5E27Qsyx4PIDgcSW1gJr8F0Y5'
        b'NUhZpVLWmKBqnPlAwgoePRFWaPN7yelNquaaOtVMG4CwRHmwLABEdVeMBMo+DGSu+n5jplzmii1cRhSigHWyFm3TeukF1hinrqX2n+m3c5WVm5ncbV0Xdp5DjhhFkhdl'
        b'uI8nq45WMT2cxvSQqcJOB/+ZnrlXTeSBntY9n4lTmPBhYALTQelT+aZ/VVedqixsztM66TdhDiuPVjJd9M1R6dVWPumf7lKjpUsWHuppXQpEkbqTOES6Ejolt/VPdqqe'
        b'6ZRjlZk/e1qfaLyW1mlacXSFuW9TcnT/mglzqbJhAp/Wv1C8jOOwJv8wUG6Gte9gHKfop/WlDNZzzGSbn+qMPxL+1z7U+R4PMTmlmm+P/Zynx68xz0OvAfLot/ct5m1l'
        b'sW+0Lji5gifSet2cfQngF5QfvMSd/SUtZRP67wZ3gV5bKoxIcAjcwlBhvxrm+dje+fDyJCrsBE+YifAmcGLKF7sOVRgdVFWNCW0IK4khdBW/wcJvvgqdKIl/d/LJmT0z'
        b'h32iLyj6xSMJ2aaE7GFZjsknZ0iYM+lprj1CxLzMxcSHgYEr2OlHTgRr/K3L1wVOP+ytC8EBz/FDqNMCGUfqPOZgxkrMSxW+3qBTqw1jjq0tegMWlca4tRrD+jEHJs/6'
        b'Mf4aFZH3BbVIIGtpZvQAHIOqYYzXgvasrlZgs7pultXFFHMm174ZLgRwruaXl45KdyTfO2MAVAqRtO+kdEh2MwOioMLNBhBdECAKbADRZQLICbJdCCBOirUFROMMBHPO'
        b'2XV1eiRQYqmqTl2DsQ36V2u+qUmryeMSYqoMCbREOlXRjcYGtY3QjWZKr0FCLs28GsLytF5tkNNlaK85YzTWjA/hNM2tLTos+1uy1aq0SIDFWZGwq1PXGprW0zXrMd5z'
        b'Vq1RaZpUuEoiH+J7unokutehPiEUhHa0uQqzTIzrcEZFjXqNtoEgTmsxOposSjQaQZ65d41YVTS5becog0rXgMrUWfAbzk9jha4ey5v61UY8+hqdqnaV2qCXZjo/oSvI'
        b'pLMnkDd6GTmiXmHJhmvKpMnblWXf+YLFWooBx0xaQX7pZeb7k9Z0C5hm0lh9jKaGiPfLbO9LWvNiQM6kc5FLLyvTGcbjGdBGSYyH1BFLFyjKZEkJqan0MqwStuZm4B+J'
        b'+NkVsoI59DLzueqKmGW272nGKx/fJlgJwQRoXND21rY1O9pIaLCNCFQQOOprdZpWg5nq4HXFr9MIbGU36VvQeqvriD4ELQ9OxRi/iRjDI5Mtp+cwShECkiEKg6q5Gb9O'
        b'1YZY1SMEONDCoQZazaBVpyHm91RoGtZqECVRr0MzbgY4OWmttMWgZsCIALfa0NhSh3ZGg7EZLSRqS7UKASACKjUaXa2abkFEl5RjuoiBimhv9Ey3NXqbJuV0Htp0lg1F'
        b'StmCIdbtIFDBxgJrm9AAGDuBejWTs9psGrCllvSEOfGZ3mgwtOoz4+LWrl3L2DeS16nj6rRN6nUtzXEM5xinam2N06DFWCdvNDQ3hcZZqohLiI9PSkxMiJuTkB6fkJwc'
        b'n5yelJwQn5KWlDGzuuo7NS+epUZsUyIIngGH9MXSQpkc7AH7SvGDzhhwAUmuYQpeIyI7xDyYEPSBXeAq2JeEAglUAuhfTZQYRwwW22w/a/k9bzllxG8En4EXnYss9Gs+'
        b'bMdGqwplC7CFggVR+FH0ItiOf4ocKPAcuAJfDXCCh4uKiE0/0JVVBwfgfiTDguPwGNztQPFgD9tl1VyiZAkBN8GLcECOpOEC/JwcVY0tYrEp2K6eBl7kwpuok3uJ9gjs'
        b'eAY8DweK4N4SJexsLVY44TFax1cO20tR4b1FylbklBUXwsNcCu4B2wTwLLgzzYjfJW5YM00gN4Cd0kJwG5x0ppwK2fBkAniWMSA4AA+CLjhQgIoXgossigOOsMAWcBoc'
        b'NGJCnpsJTwhge5wc7kZNxoILhUjsb2dR88EAPY/HRVOwjVhYqwSHwCAciItmUa2r2fmsVNgHbpPJNWY6MHbzvHeu+Sq1iWKaPRsID+ld4WF4HbfMWguuU47L2fOCwWtG'
        b'LP7BE+BWFU53dZXDLni9GF6Ngc9xKEcXn/UccEkDj5HDnPXyJIEcVYBmrwBPCYfygjfA1WiuO7wMj2jkJXye/i7K94ePLzV3Fnlui3d5dvh59q/mT2f/Ii9tb0zqB78N'
        b'blxyo+aZP6Tv+3zk5JbBvhc0X/2t4GDyjE/T1t8Ib3nm8/mDSzM+7WrT5Wx/Of348Y/c3ot8V9avjHl+79unT7j8Z8bH96e/3s4vMpguznr40u7N99b+zIsz2Nb4R4/t'
        b'NefEh+IP9x4q2O6i4L/XHVL+QcUfjrjB+gX7l3uUDBzSf+S1f/GyT74Oe/1xy7qNJS/78SJ2w4JM0TdtqxdvvvSTb98a+cvKtufWP0PFPh+0svEDKZ/ohlJdwUlDxAQd'
        b'E1EwgW2Oj4gRuiOrtUV29C2b4R6KikniwQPJYPsjbLWzGR4GO7CaaYKSqciD67gZ9BAub0182RM8HmbwwEl4B+70gTtILXBfLeiIKZUVFJQUxcJ9UhblDW+jnXicmzjL'
        b'wBgqOl4Mz6O07XAgKh91hkU5govs9eA82CYV/jOm1uyqaLAzwaaX9em1s6qurophNMZEVrZyPJJwlr81c5bFzpQf3cvrNZzfeGrjsG9KJ39U5NsdZxJFm0SJo/KEzrzu'
        b'WSZxDKOjSTv4zLAorNcwEplpiswcnG+KnDksmklUKrl3G0zhJcN+pUPi0tEQaSe/c22X+6g0GXk2mYQRozNzOvlDPpkmYdZoWDSKXG/C+pYo5FvT5TYqTbDko8OQz9jl'
        b'+rnIdzRK3qfrZ/VhA24ZJnH4qCypP7s/p28pCs80iaNHvX1HvKXdyzs5o0LxEbcutxGh1CSU9oX26YaFiSPCDJMwYzDiY2G2DXPswTDHr1CWi4wD2LmGnevYeRU7r2Fn'
        b'EDs3sHNzCnbaZjHwvFeP/9HjFh10EDtv4bYxk40NJHyLLY6UOWHVzmOi4Hn4g9U8+H5gHz+dGhRkczhSpzGXOnzZ08w4jbky7KYlyFc1k18usSzhZD52r1WPCTCzg1g8'
        b'fCmPGbR1vLXONpRIaKFEnZjrdrDHdR8mJjMRh41P01jEtqmT0gNx4Nj2KTF2myw0893OE/huAeK7bc7ZbHlwxGE7ZwsI3z0p1sp3NyK+u4U3ke9WWe9h0ow5PcStzsUP'
        b'YZgQjVgEtBsQY4rYGJWtAWDM6sTSDboWYytKRRywyrm2pblGo1VZmKZoxE9FE+6BYR6wUsF60xc3aJWSnbGU/P8Z/acx+rZAm4mP+JgYq1rrCYZ/AlQz+ZkoSwHCtS37'
        b'jius1uqYXcHUY94I5jiGUdW2YOWHjrCmWobhXNuCOUVNs6rJzLoue8qlXMTA27+Wa+0B3o9M+zUtLatw+zhGTpeYV0dFwnRLzUo00UiMZM4qtViQSE+NTzBrjPDEI6kG'
        b'F182fiHX2oh1u2fSSr1R1dREIAUtzJoWTa0VGpfZ3N+dIAuZ0cPEaSKPBpfZ3umdJM3g7E9INBNuiv4PCCg56rXqBvM9nv8vpPwDQkpSanxienp8UlJyUkpSampKAhFS'
        b'cKsTJRX+JEmFZs6IC+fwqHihmKJmVzfdiBBRxkQUuVpWVVRQAvfEFpi5N29wOWa+PVFjM7jjlBwLrhEu2hteBt1mOQPLGLngBhEz4HZnI74tBa6B3eBAkbywBDFxBVZZ'
        b'xl69lXAH6IAdTuA8PJhEDnE1ZeB5fVlJmdneFW5hEexEBQ7AdiRuOCPeHFWIwjcUy8FxcBSccaLARfg84ipPlMIrtBFziI3gcKS+EO4rKCkrItYHuZQkh5XDgXv9wBYj'
        b'jft4vhC+oY8ugfujMLMqLwCXo1jUtAYe6MzjaeBxI2ZGZ/qB1wXwNbB/gSPcJytFYggbHppPeSZxwCl4dSYRqsDOVLALTYbl6Bp2+8zH9i/B9QXYBnMC6OCtm6Vg7oDd'
        b'gZfAC+Z+FcRK4T5eYxslhmc48JZDIlmmJWEcypCFKX51sV9SLSM/gj2b4S0BWtoKOTxHVSBxaosRmw5MB1fAYQGeJDSbXfC1fCSH7YMH4XUsm3WAiyhU7AtPwf35WERZ'
        b'7us4D+6B/UbMQyzxBXshZrgKXIqpgvlLiJVpeB3skhIZFfTBl6gEuAX0ENvRYep52FY1FQdPwHYqjjer6c/ffvutYR2X6vP1wSDlEjzdhTmYP73KgWpvQ2tAV8e26VMo'
        b'I2azVEXgdTw7+8wybX7sQmybPq5QicAhH+5VREkRUOQz5ujBgVUlSEAAr5L542tdV7jCm4xF+m2LNirg4aRCDsWCB5bCSxS8FAr7yLUERRF8UWBepAXj8OJoZ3bAy/A5'
        b'LqVD0vMupdOScPCcUYZ3DhwIHJcM50fBwwpHsxCYDvvNcuAsL74b7EfCIhb+FwgS9IWyshI0qCp4qSiu1CwLSmE3D1zjw/1EJp/tDq/EYIs6YFtgXKGUTwnAG2w4AC7l'
        b'EMPqxYKydCO/3ZVqVYk+XXyhJMp8e+OUAhyDA2bhn7lcgaAL7o4rK5mPjavvR3UtzC9vs7lj8QI47wI7wS5wkqzmYq/AGHlBLJKMqXQ+OMCOg72pBJxy6uFLRUQoYutY'
        b'7IJ0cNFHyiHSdJGs1FwEnAkmZZrBHsaS+U14fr21EALkG+krQglQw63wAniJjBAeArtthohSbmtW7b/E0u9CfVC8r3txQUkZmC184Q+PvaNeFHvM8szJf0C3dQnyrgSV'
        b'3LwVWRq26fjvr7y5+RcH9GvGLj9/ObKg+rX/89P3N9z+ovYbpw+rtgS8O5/1dcMvKhqcXjmg9N30C9eLN755q/RHfxQ37XvjU87dmazRv7j+8d11gf9leCNxntA3RvjH'
        b'wrJEP9OslOm+gZo5fT87mLfntS3a3Ns7L65sqy6blxry6q79g+8Xey9KeeNAZ1Fyg2Hm4C+f3fjjZfvT/3bl3MN3A+dd7r6WY/q0Pt1/vWmeodfUUBX261J9zvCyB/sr'
        b'nn1W1pPvdWuk8spFg1dMW2DghS+Eoc031r+X+UpgzCdr3vCXlPIFwhsum7/69ZxvRQ9Ppv3lL984fSkC67tGPyh0+PKjd1bX9uxboEtXZvy5/q2PZmyq/mle62a9cFgb'
        b'/qvPbrx4cfnx45/Gqv8852bgJZ1x+ovznDb8/NrhnzX9deed7m+0K3/39pJVj0+kP97319mRpzzG/vrcH33eCvrdW47Ba7a1hL/BW73+F8+fePj3h+dW7btY88l807oX'
        b'YNaD11ou3CzftG2d1JWI0K7woINZoN8FTtsK9f7gJrkdEZO/ySrT14K+CdcoiEw/F77ESOPb4Ku+E2T6rDDm6kgNGCTWzlY3qYvwtY9mBEXMfR73hZymkEpy5SMUvozg'
        b'PNp84cNpCTt8HnhxVjMpGJTrFSPHtCIWgffpaD7Yz5aBXnjrEcFWx+EgOF5UHM2n2CtY4Jh7Gv+ZRxhWI9fCXnCxuCSWTXHXpxWxwCuN8Dpj3Pg82pwd1jsegqX8Z9iR'
        b'FWDHI3IFqRv0gLPmCyGTLoOAA+Cm61Kw/RFWExWjrTHplInya4FXyCkTPL6Z6DKawU74ih5c9lfll8ow4SOT7AE7OaBfC28SY29F8KW5RbE2Sgp4Ep5aLwK3pV7/aj3F'
        b'1AoMPGu02WacHS2GG1ZYjEtyYz4TNBnjCUSbkc1mtBmbBJRfWO/cvmRspHnYN6OTzygupg/7RA2LpH1zRmJnmWJn3Q02xeYOi3KJ5iL7brEpvHzYb/6QeP5oiJzRXDDF'
        b'Zgz7SIdF0X0VI7LZJtnsuwkm2Zxh0RxSLOfuClP4gmE/xZBYMTq9AGs30k3CjNEorMrYaBKG2yg/ImOwdgWFnjEJw+6JArvrenNHRFEmUdQ9/6g+8bC/vHPO5z7+zGWW'
        b'G6GDdbekpnCz0XhU2FwQK2ayD2aOpmV25g35J30oTr5v9prEyfcC6V7vY8tGAuNMgXH9nOHA5E7nUZF3d/SwKOyCqG/piGyGSTZjsHZYlnM30STLG5bOezd4WFpE2ix+'
        b't80UvmTYb+mQeOln6Vk35t3Ne3fhm2XD0yuG05V4ZMkmYQrWyKRk4fYSTOLE+8Hh531P+Xa6jYp8jmR2ZfZyR+gEE50wLEoYDU/qV5nC0zpLR338RnzkQ0Hyfu5rTled'
        b'BmcOeRd2cnC3wkb8ok1+qHPRo0EhI0FyU5C8T28KSuqcd8/HrzutN8PkLxv2kfeHD/ukfRYUORRVPBxUMiQpue/j393Q24Cyo9TRmLhuh16HDyVRo76BvQ59vFNuw77y'
        b'UakMxfJ63P58Pyq2v+JujSmooHPeaGxS55wRcZhJHNarMImlo0KfbieTMMSsM4r4WJhgoyYSMWqit7HzDnZ+hJ13sfNj7LxHWdRE31ND9CTw46ae1BdZVUZj2PkUOUut'
        b'KiNsS3O1M4ulISojDesRcX+oyugCP4O6Icjmcmotr2Lxn/WLKPhSk6165zCldFA6KbnkmyhsJWNh31XJsn4ZhVdhcyVayw+ilDZGlpX8CUobXjafqHImxU59lj9ZrnBj'
        b'5Iq16RyKSw2pXKnqpj97PENVkNiOOh7lSPUtRaxh8ckZ05iPmMSHLNGDfY6rORTHDfTMYaWD3dGEkXJJzlaAfRVwn7JkPrxejjguD6Vranw8RQX6cMDWGamEp9fCMw0K'
        b'uK8iJR7uSUYMPTgAdzquZsFefK2QsFrwPLi+hKkpc4ESsUS8aBYSEG7CQ4TvgTvgoAx/AgVsL8HfQHEELxObh7mb4Fl4Br7IpsAt+CoVQUnAVvA64TiF4GZskTw+Ge4q'
        b'TExhU/xNLHCiFWxjzhKuO8ELlq+GmL8Z0ovIxguFmzW3k9I5+kT8TY33xvZVIGEm3sX4Yep/+ux05TZu6eM7yIflFyOC3+wR1Ow5OO3uztq/u37rs/aa6KV/v1o4/6PH'
        b'v//Nb9LfW/Wlq/y68+iIYQO1KPbu4T7Pb/QH8779eVngt+tzf3vh4+XBUaCWNdKX+yjhMd3gIW/Ibr+95nDK8Y0nukSJv/XK+8lt5RLWO8vmmqQHIm7/549+7XDvIb1s'
        b'd9Pr1O+q38soPvrH43/deLG1/93/U1xx+fdvL05Jrvzx+Vc+KfrqNb+5KwqjZ7bN/+v6StZHQ7/78NFZecTtjq7/+v3oM2n/vv7W30eOaa8neM43ipf+8TPlGvnHfqW5'
        b'S/1FP/fa8Vbk1/tXDYqObpr++35+hp9iQ1zjo8cXfx2waM2vMr4V3J6f9ube9MzQec/+5s5/sMV/cFI/5/DGGxe/zn7wQq3pDc6Bzo1/o0bhnMMn/yL1JGzBprm55KtC'
        b'DmhlLlNscJqlROT+DeZzLedXwGctFL4IrXo7ovHgNXCMsf27E3EkWHjctyjRTL8xma/OJKQ7HBzPZWi8UjyZyruCU5XkUi2vEnRPPPDIBDfImcfJPIbr2Q5vryoqjUUy'
        b'y4E48BICx8twvxt4nVMlBCcJs9EI94BXYEcR+WYMNwicl7HAaRfQaf4MA7xQGmNTvUssBx5OdYBnq5hLvQeDa2y/OeML9pFPzoBLcCvz0Znr4Ba4WTThTi+1SY4EeK7/'
        b'WnCV5IEH2PBa0YRL2SzKcyXPj4OqOcCc3eQj4fW0zeFNA3zhSUYvTfuIMPp7veEgvqNtvUWNdtKVcvcgTqUWbiGjUhrhriLzBV/M5sGjcDdm9VrBfjIlC1Y3Y14HXF9q'
        b'cybTDRibuIXR4Jrt13H8vVjg6kbwErG125ADzjOmdufCF62m/eFxcIoxxfsKbN+IxRO4vyi4DBt8Bp3sFngIXpZ6/jfyTZ4WvmnyF13GHKqYT+3YXidiYgibdJJhkx4s'
        b'dqV8ph1p6mo6qO3kYH6koVfVs7IvekSUYhKljPrTJzN7MjvnjAYEnyzqKeqcO+oX1JV73z/oZHpPOo6edrKgp4BEd+aOiiTdySP+sSb/2GFR7Kj/tN5gnOkBm/bzHBX7'
        b'PeCg3/tiyZGSrpIHPOR/wKe8ArqzuwpHxJEmceQDBxznaI47UtZV9sAJxzhbc0WYxBEPBCjuSxfKS9LNOenS4zIUnjosSRsWpz9wxZndKC/fB+7YJ8Q+D+zzxD4R9omx'
        b'zwv7vJGPNOGDQxIcKu0qfeCLK/fDlTv31mEecYYpdsZQ+EyTZOaweNYDf5w5AGU29zgQh4NQ9hFxRk9uL498+mfdMJ0+HJDxYBpOpEliGkrknHc55dK3eJhOHQ5IexCM'
        b'E0NQ4oNQ7AvDHcDzEo5DESj+SEF39oNIHIqyhKQ4FG0JxeBQLKle2j3nZElPyQMZjpLjMcZhXzz2JWBfIvYlYV8y9qVgXyr2pWFfOvZlYF8m9mVh33Tsm4F9M5Hvy1nI'
        b'18l/kMOifP07efeFXkdculx6VvSlDgcmfiRMMkd0K04u7lnc29CnOrVyJCLNFJE2HJj+kTDjF0HhnXmjYt8jxV3Fp0S9C8/4fyKWfcmhpkXc9wk8sqFrQ28KYq9HfOJN'
        b'PvH9ksGMYZ+5Q8K5NkyYG8OE3SCAzRzd6Md4eoNKZxjjIKD+YRyXm4XjeoLZeoCdL5FzmWW2W/43bLfclcWKxaxW7A+9CXeSH0ddEWRy/hcvRe6Qsr857Mw8SDVYnpmZ'
        b'j2aazBplndpg1GlJWjOtwidnNgppcmpFr1Kv16N8rTq1Hl+HZjTZZlW73nr8ZVZr49OnJ0/Cmhj9Pa6+Zr2BfFHTlr1ztMPekW9mwD0xBUigfR6Jv7vBVfgceGURIrVX'
        b'wcX5oB1xTf08xCxt4WwARygjRoZJa8EFeBBxtP7gjpySZ8EDRI8aUVtDOD/QsUgGny+SyzkUPJMvBrs5KPvFJMIy8sMRMS+WOWDN538tmsvc1wCnwBZwxlzWgYrfyAUv'
        b'ssAReA5sGWNVEe5tFrjWaFZawZ0qorTSw15ilYblBF9H7KAGXCa8pYUf3JXJqLQuK8G2InyX4EVGq5UeBdpJlfAVcG65ginCBvtao1kBYGcOKRSfsRoeJAPgZIOz4AZr'
        b'Azy0QvP3597n6vFB9trpb+NLrdV3O38kBEFvbXHa1p3wdvEpbGyexcmViji5W8sdlwljzr1X/U71ufI8RZ/v+vfffP/U+zebaO+h1DXFf/LIOVdc7j2Q2fkopab6fn05'
        b'dWPf9rrXwrP//dd+73m+z9YtD6qNj0n44zXVL2sd6wVq13oHqevP3zl9Ah7yOOXd95zofKG87vCbn73TVP3GgOqlihpHdbJHtSqZOvpr0PiO4582O7/17SmXaJfjvtS/'
        b'XfeXzhyV8glxf2YjeN323sXmLOsDlxpwhXBkkfBOmdVkPQ/uwDbrwYuLyJdxEmLAoRjEfHSWsNGM9bGKpvkTupwIBoTwVCTipDBLUCBjUwI14pLh69mEGcsqIk+CntCj'
        b'LIRdfmY9ShBzm2OX5zOYGQKvL7PwQwwztGOl1PF7E2tHK7G2kmiVvgpvNRsSbY4hJPojiiHRC9wJ0kXUMlx6vvRU6UhYuiks/ZOwzK5iRHOnBZ9c07NmKCJ1kDOoGJ6W'
        b'3Zk/Oi22b51pWhryRUSfbzrV1J80HDG7c+7Bsi8dqPCsBy6onpGwZFNY8khYpiks85Ow6aQmv8BuVU8Eou4Sv5P8Hv7QtLh+UX/tJ5LMUcm0XgeTJGpEkmCSJPRHfSzJ'
        b'wlFIrh6RxJkkcf38TyRpDxy4tHdnPqLWkTHnm06jRk0ROYORyCEtu1PhMxAhlgR2uvxDF5TxpXcdCzm/tL2gPNf9Bxrjv4oKXmCNcVtVhsYJH22xCphNGC3zzB9twY+n'
        b'8bdA8aet+NYPt/D/hR9uqUcIesAGQWNcqletwb6mJltUPf4WGPc9ky6op6OxL5pG9E/PnFViJKxehy0d4KO/aHmbpjU6llRkxvY65qRQjy3F1lnPH1W62kbNGrWcLsPH'
        b'oWs1erUVw5MypEMku4qub2lCLOQT6Hvyd0sdmc9xlYHO2TH5aEOX5yN+vbCkGFyoyEeSSnusPB0eQGx0PnzWoZUNbxtjUW4feBDsKkIIoLBEDncjqaYCtuMPu+ajLR/V'
        b'Ak5gw15F8FUH8HxYEoOeb8JtkfirvIhr74RnUB2cJhbYBl8Apwk54IAr4GwM6t26zeBlal0lOM98SPUyktC6YsrYFAv0w1cWIDmBs0Bzfecalv5rlLy4I2Wg9th7QuBh'
        b'RqA56SW+wbGuffkhaZzc5Jjimd0eESffa4cVa04XK+uoG3sOuvjEB9/YEtPuP8xVRL3gkBzT7vPaM8JZ55bHJz37h5dnp12Vsn7qXO+kStn57JKg2qjcTlo7sNN3+lsS'
        b'SWGPRHI+3/lQru/2HQnKvKhjidmLnV1e93Rx+Wy2X98C8Ws9zi5fDNYsCFC4JAUouG+q5LvLZEOuO/7rV9yvFjne8pQ/zq8dCD3k9OtfVC+UdOwOPhB+KDzfW7ExKgmU'
        b'vFndLq6Udz4obCivG8r+s3vfzH0FW7ODojgVonfuVv8k9t8633n3HpvqoiPbav2l7kR5PQs+K0crBvZ4Y/mLm8YCL7uWESzoUAj7YMcmgOQ98yeVHWEHeyPsQ/ImERlf'
        b'BHvlcABeWyvbxGHu1jmB82xwBtxezYjNx8EOJBLh8ruR5MzXgUOl7AD4agShAPPawBb83ehYOcLPnQUkiwD2I9iALyMpi7SwAzwXVhQL9pcp4GnmQ0WC2WzYDW+Dw0SE'
        b'K4Znyddod8eV4eefhrJN7Gh4ExwipZvAABuLaFI5fBnegAdi8QDd4zkN8PAa80dRlrlaCQwftoM9+KsoLzPfLazQwDsxcfioGgyAOzK5lI1owEkO2JnsSCjNdHAWXiay'
        b'blwpD5V+EeyZzvYBx+E15ntBW6YHFYFb8AYD/AjyncRsxF1cCyC0DZxuJgcD5pnJD8phS5Akzcw7mrM7jGDqAs9bv9wKjoEtpNvTVoLnmZ6hdkEfGAR97FgJvC0V/KNi'
        b'pYCaoI5niBUXI4ExVyulwkFCptyZT7c+KBRSYu8jaV1pR2Z2zewNGxFFmkSRn/kFD4VYHmWKvEjyjK4ZveIRUYRJFNGXeCXzQmZ/3UhMlikma0JmSQCW7o65dfLMauWD'
        b'0xk9eZ/3iCjeJIq/5xfcG9bH6Vs+7JeJqFdEDP5uzLnmHudu7qjEHxfurfhEEo/EjMjk+2KfIwVdBYeL7vsHnkzrScOvZ/rCRvzjTP5xo4jcOfY49oqPu02o5F5gcG/I'
        b'+chTkedjT8X2GforhkMyB+d8FJh9d8FoQNDJ/J783orjpY85VFAOyxSY/RC38x+B2Z8EZn+jx0/D3xZ6zo3jvR3nPHemE0PtnBhqx2F9LxUxUdNaZRSGCnrjovhJ4LcW'
        b'CQVrgzcgKih5+AO/rEQklCP8SOq8IJGDunaMIl9qGz9N0eErfroj2DmB05yYO6MatV7XhyNPY+dFhopjOx9jnLnKBaXk0yY6/IFXRAPMf1Ie88NG/73sGZLEb5/qWmqr'
        b'qpiXxY6tupZWtc6w/vu8siUvl8jNSqIrf2BlFshcETOU4v+RQyysYn7y/Gp85VosDrawot/IIjZ9vuSyXYUPHSk3r1OcC/q7WaYly+8FBfdlDOVUfslhuVWz7s/NG52/'
        b'4DEn1DXiAYWcr3g49gEXeb8sZFF+IfeEslFx6pc8tl96e+GXfMo3+J4wdlScgmJ809oLUExQxD1hwqh4FooJyma1l+KvI9H3hDGj4jgUJUlozx+PycAxWSTGZ9o9YTQT'
        b'45PVPg/F+IfeE8qZivxRRUVfO7Jcc1kP+aj3PYpT+qtJb4p+nHQvkL4guhH6ZtKP6/AIKlj35ytHFy9/zJG55rC+pLCLx1CBxoD9DytZePChVxVvhv/Y4e60e/5BPYbu'
        b'6KscVJfCtHCJSaXG1TSwEPNbhS/JcspYromPKOzielACF/sf17BTXPNYf6Kw+7WW5esa+DAVdyzU5Br0mO3tGvOAQs5XHMpt2lc4OG46FL5eCs42a/UFsQUyvZsbh3IN'
        b'ZMNT/nAvORqAHaAzTwD6DMhzrhLuFeA7IuX4YkhAIjcUtMf/v/5dVIdSwgmBXeBIOTbSGkyBzuJgNtjCDP4qIhhni+SgPx41weWAa/BV1mqwfRNJdZzfNPF8AXRg5mrj'
        b'dJKa1pwDOwpisUCUxKUcQUcx6GYXgp61mvqfNvD0+E3qst+8zLyxlLz17hZW8SmDvDa+Vph0bnq5T4x2xbm98f8+2/j77t9t69nWU9LT+VFrzXy4rc55O78iucurbm18'
        b'riNHsPi8M6dBULiB+mm3oDQ8Wcoj9BIeA+fgi1YrDSv02E6DdPkjjFCrfKW5TU985jyrhnAgSNwXWw/0+VzYhQ/04XbwKknNmQGfZ3S4Zg3ufPAauyUJnCFkNgLfL8G3'
        b'1ZjUFTXubDXsh4enfM/p0qpTI4ZdXUXuVIezzF86x8ZvMbmc7UGJJQxda59zX+RNvgM+52RhT+Gx4mFiEBeRvayurO61fU7DosTx8LphUVT7nM/dvUZ9/LvndS/s3NjJ'
        b'RWntRbZy1RgXtzrGZx6Yf8dnWXHfiBPMtvks62Yhi+X3Qz90NgEahebfrz5H9c4UPGFILAE/zEQbg202ZMVdzguhFBw/CpsRy2Dr+CTMR2EHEnYgYUcUdiJhRxJ2RmEB'
        b'CTuRMGNGjEfMhPGsZsRwWIDac0DtCZlvhCsSlaxklsLD3LqrOdWTMRKmSCKpYnOqOw4r+UonpXMyV+FljhUqklEsF5XythjjMpv+wua+OMnYMBo2lsaz/FeIiCEwZ7Of'
        b'84Tfkm755VryP/H7ZDwJK3zk7vGUQoLLV7EUvjgd/frZtoHC/pZyyB9g4w+08QcppiGXtokJtvGH2PhDbfxhNv5wG3+EjT/Sxh9l45eO+58cryJazp7LUsTI2TrP5aIQ'
        b'armnIhbD7wIpNenPgiYtNpnN+WXfNz9pxctsCIx5NOyc7KCQE5jwJmbaHAgM8BRxJM5HEa+TNIicGqUpiD9CvLEqDwnNGsTDUxPO1a3aBWwGDSt9bc7VseExLmoJf6KY'
        b'bz1Nd/gXnqZ/jw/MOzOn6f9B43Pz8iDX2dUuDZuWMVcqd7rupSSsvhm88mq5U6GYicwu38j6M7t9sSBeldWuyKOIAF+VbpxgRKl4xmpb1RpCyB0OlKLBUQg6eKQWyieU'
        b'mkO9W+1GVbNnTvenfmPpIcFlmsJf+XD0mP0LKp3FiOQS8By2h/R+oUvwpXN7y4OK3EL3uHCKI3zedau/5llTnf8zFXW159K5+Pgw52333l/4q9mpjMy+Nl5Q3BBd6/ju'
        b'8vrBG8Vvurx5KZZO8B6Uua8UHvDa+SP+b66y1v++NejWzHf/FhC/KZPT4Ee9GSl2pP2kTgzF2YYozkH8Qc3NmFPgUI4VbEOelBEcr2Z4I9J4pbgEbg/F8lsk2wNsAWeZ'
        b'g9LXW8A22+tpnuAVs2kjVN8dctctAewER55QRIKdseYJC/flNXI0REg2pqkYE0QxUTJmSjsWgX0OlE8Ad/q0APKZcbhzPaJr5MOfYB85Xd6L73wd41SDa0jgvDPjEXNB'
        b'+WLteKYScIlCeQ5zliSCM4XPEHEZUdZQ0BEHX2pCIm0B3MtC4v4eNpLgb4Lrj/BXgdPhzbWgYy2qwkD0AWAfOFCGqO5uOAD2lcH9cj6VUcQHz4NjG6X87+Cd8f6YZGDI'
        b'07qhJloYWk8xFHS5BzUtrJN7SIAvPImPLUFe5y+dKTq0d/rwtPhOl1HRtN7gYVFon0u/bjgqY7Dp3drhmfPJLaesYb/pQ+Lpo+EJ2NpPyGhITF9u34JeObZBNBocTkz/'
        b'mH+CaNzEaHBYL6+Te9jVhsgy4twYj9yqH+PiRz5jLuPyk7ZlzEmjbTUaiJVYeypORsAzn0PZ2ABKRegojm1zBLXMg8VKxwJe+g8V8I7yo6mXBCn/lAEgXhUe2hSGQ2xX'
        b'yWL2B1/BG7dzsvToUsaKSMC4UfxJdkPkukPUEx/6/YFWTlyrbKd+KjMnM1HEHPYEkzpxHwbGMR0MsungZIs/8n/GPoxzlRUUnta1eahrum7KjP++CSywFLI86/mn+7PD'
        b'YkQHQ21Vs2ZKgzW4O4W4O+NGdLyx8oeu17U0//P9aJjYD9W6p/WjZGI/xKQf+FHXP9sLM+zwqwwtBlXT07pQPgGmlx1dZjZxVIELWh6LTdmf//FD3++i9zyG3l9ey6b2'
        b'1uDvW1Q3fVIrYEj7iU0O1JYFAfgJRfGCNimlOV30M44et/W7x7ss8twWp22+S7ae5R86At692/mBBPTuyL0uDa342t3noLyzQnW/mEP9PZmXpP+rlPUIn+TGrYmYQC12'
        b'b7QSDBtiAa/BKS3kEFXPmIctVRg3j4O5O0wU6jwpScCRjV0be+eP+ESO+gfgS6TJJ2f04Au8fdkmH9mQUPaPm8hZgF8SsG1OoGo9/4ETqP9VpUHjdysNzNBxayaPyHCz'
        b'vbkbJLNPzyYXJ/zvn62Nx5deWRSr/rwm430ZVx+Pgt/uLxqHjRzJ4q11SNAvXl0aXxt/UCqq8HK787vZiS9sHeBRjz/nBb+TKmU/wiwj7GiJsoUL+Bo8Yg8wwOvgNSKl'
        b'z4BvwLNYxx8tk0fD3UiOB9vYSflw15SCuHsVeRyoaVNX1TS11K4a87UBoYlJBJSizaDU6klFxeLb2v1KU2TWSGS2KTL7bujdtcORZZ3cI65drt3qD4Vhk2BpjEee0n2H'
        b'zL0Iy9yLkbPYVuZuRtDk+4Nl7icxDeZXv6qnLJLGYca8NJXM+W+Bp0l3dSefBprtxPLzv2Ylx/yHA1VePWv35lbmyoYseBm4iHK2wQsbkHMTniRPvlyb4RZwEc3NhnQH'
        b'agO8NNOIbwtuAFdCJkgYCG4qokplLCoZ7OaDi/CMmzaFeRwWwKXOJnrgx2Gx9RtbKfLY6UJFKfstP19H5rETXOxFGTGLBfdK1llMyk548cSAIGLtz8onWGw9BXuc4dFk'
        b'L0aLiPlpsEuCD2kKYuElcG1cJcYuBDfhXs0b2eUc/R2U7e1PHw7UnnhPWHIXRL1/f/VzW4MPBB/K3s5iL+iWSJ5ZL5HkdB/acvrcXqGpOu+idHaGL793sbDCxZeb9GYF'
        b'+KkH94Jr/avRDdX5v6yvbq9/9qJ664USNfeeJwh4a9vbcxYupJ0Uu3/nt2Kww/MFWhf8fuuRV5bMnd1ct+vY2/vrQvXCyHPN58qXsnat2jZ4dbCTUx8tX/HmpVeLXy2m'
        b'N1O5+3w6pkd+Nm/2vZpf10QY6U8fJ3M4aUPvG/gfJFMzfxLw+UGF1IGcR2XzYD9zjjaXZ3uK9jq8TmQUfNV0kokNLuye5QjvgG4iOjjCrtV2RYc0cMiWGJyBh8k9jXWb'
        b'4Q5BtFkwslY7raENDHDhFXgO3CTVwr5UcJJcrsWSEQIQcKkQiyJ76sFWspJ8Kh68xA8AA41EptPlFBTFRsFOcNPGRkd2HXOj8yrYD7vxOHPgy1aNILtloa+Ua1eEwcBu'
        b'teWJOIq1Oo1BPSa0QTUkhmCYAQbDfLXGkwoM7pzzuf+0exKaEKqD63uTDm7uM1zZeGHjoGIkLtsUl3237t1auOqzoKghadZw0PQhyXQrTevzxHctfWRXOf1zBpxMPhmD'
        b'ucM+s+75B3UbjmX08Yb9ZZ+FyIfiSodDyoYCykYlASOSWJMk9iOJHJ+vufa4MuE+xUeShFHmZmZvyLA4vE98xf+Cf//iYelMk3jmx+Lwh16opzaojs+gOq5K16C3Szz5'
        b'FnRnxncYSenqkLPcBt89Nnr+A4dWh/hh1FlBHKe0lmuPipELHCyLioUoWDACZCdzzeiPO+ECBw+hPxt0aKtoQYiOm80j6G9SrO0FjtLvMNZk0cFfcIFHAX7HGuA/jZqm'
        b'hP3EnjRBd/D52nkxaHYEK42UEfSDDlJC6bqR4MZZYKCNagMH4QuaV/Je5uizMSqsmD9Q2/OefLZZu77NN7c7V1LcE3x7+a+F9a7/t7n3gIvyyv6Hn6n0OgMMfeh16NJU'
        b'pEtXBDQ2YIABRhFwBhR7V6wBsYCNwTpYARuWqLk3xXQmk2SANJPNlmSTXYiuZrPZ9X/vfWaGAU022d3f+3mz7mXufe5z67nlnOec71HmmM5sjC8Ikxu3WXi5pxhHNptX'
        b'hlfmk3uZWZBRSN5ydC/D8gITcCvflYc4fWyBDNAqwUrOmQzKuZoNmsEGcPwX6H29Ab0TO/Vx9E5SCL2H0fQ+MpNHObpqBP4qgb/Svseun6sWTGvhfObgMujsOsKiBK5f'
        b'evme4ww4hAxYhxgQm9GY9qcM79cyv2e/oMqNKJqZ1p+wi3CmxSiQ6ljpnzDYCo/B8B1BrLTvbzlmBaiYcdSmP+OIQI9tQG1GiN6wMM+E0JzR/wnN/QqoS07eGHHl+oAd'
        b'oI3hv5CiXClXObwr7Y29xZbjD7GqN+5cLu9Et7YDb2uv8eyKbT3tEeHrN3A3l2V8UVpqLGa80RGRnCobOmKc3H5vkaN40QbP89G7VieGWzu+XfE2RsrkUkOfmHT7P9JN'
        b'16/4WmpE6b+W0hRkRr6TaMnIzoCMxpIJLU3W0tICHsV3bJ2KKGfIwUPho+RpHETodj/k4q7gHM5qSRsSeCuKlOlqQWQLZ9jH/5zPgEPYgHWYAVmZ/gqymths0zEq0wur'
        b'avFrdSioMyS0+ZjQHv5WQps8kdD0u0ktZSg5JtuakXZj4/yfENkzXOSz9zodkRGl1buLMwoqckSz4f7IDBbFMWKAjZGh0jhNOVMej57fSuq5XH4UUdpemtLe5gOV0MWi'
        b'IinR+ITtzNf4b1qJBySS0vWjOe0NQwJBoSBWzfgymgPbEYNONJPw3lmWDfaC3VqT2xg+UKA798+SGEdHYlor0hKtewotjQkMaGzcE0JmwVoyq9GT2aCDuyLyPKs7rcfn'
        b'XE5/tCo4Se2fPOCZonJIGbBOMaAr4wl0NcytFJc31Mmee04aGxAUTU5Y/CBrQMFyQ3JajMlp9DeSEym9netPKc0iWQFWtNUisV8klozYpnHYYkxstliyYthiWV1jebVE'
        b'RkYifHw0YtisHGNiSmobJLJww0jEsHGFVE6DXWLecJizTNyAnbhIGhvETcQVCdbdGDaXNJVXi7HjDZzUR3JiHfLwYVMdmKW0wgCD6zLJ0SBtqJGgYcVaJbJGHCzDwXOc'
        b'y+QNG2P3kLjIYTP8Swd8RZIJ5iypL0K2moHVTjCKTVldE8H6GubUV9fVSoZZleKmYY5kiVhaE8AcZkvRm8OsMmk5ihglpaTMKMorHGanzJiVJtuFZ2o3YwIHhscc35Mf'
        b'1lM6G8r9FPmahDVJ8bFAFZlGGf9/w9s7P7Nmy2lebHYD/n5DJSpjxas2hjApohjpCjY1yOE1KxmHYsLTDNjGDyxzp5EdO2si5A3L0DN41cxqKoMygoeYluh60NOIF7c/'
        b'2LwwCBtdXfDPyAXHYHtIZm4+bM4DF4Lhi6FZ+RnBWaGIsUI3eB2uBmybb56SCA8Sy0xTuHEubJsDj2BloJVULlTALvIg3mdGZBS8bRPGphh+FGgDL8FjxJbSD13690Qy'
        b'EXd1gaIiqUh4x4S84A7PrImMWg13hzEphj8F9sGeWlpVtH0BUOjtzBCbuY1Bmc1jwouyIBp7ZBu4Da9HRmU4h3EpRgAF9q9eQWAkPeEmeIE2o5vEpjiwd20VGpjZsWQU'
        b'W2KCqEKKElTalCY/cJpEjyLcmgKOREaB3rgwBsUIpBAjsyOQBmBZj8Yx23V2iCgE48/kiuCOHAblAE6yE51gHynxsYmQSqSosEf1pS7BjdNpHtkFHloXGeXtF8aiGMGo'
        b'K1PyGok+5A24BRwKwjCVmYRFmQdPUVZgN6ssdRUpbFKGPYU2slLoXzpl3XwO1ajVnXiRh5p3BK4PM6IYIgp0wJ2glzQ9ud45G+4hHnTZwYwAeAXctGOTov6xcBq1mqJi'
        b'w2JKZ5mxeXRPQ6NmoelpA0dBD0UxQihwKAfeJKdBqBj2YZX53CBwBHHnJuFM0F5rREo6Y5VF7aOo+p8EpYFzqmrpkoJhp09kVDra43vQVIdS4DA45kbUTISgDxygrQKI'
        b'guNWcMGb6QX3C0lh6iQCYVp6Kac052mujC7MDChBO+phc2w0RQZsP2iX0xOwHZFsZzYG89wJ9xDTyNXFlCXYzEqArZmkxDXBsRRaudZFpaWyH7ketOkwIsjNfpFR+ZOi'
        b'maSfBy3gVQLjw1snoUvLywG74Q4teTEoJ7CPDXaEJZD2BIF9TNQcJTwdzSWdawfN3mQG4UHYaqwtgMwgvNFIWdazYqdqXeCYmttS6DQRrLcoXfBaZAWNxzMLKlMiIzLg'
        b'JkyqqHsHZjfQ9sd93EItpTIRpfbBm2AvA+4Dp+fTBietc8DVyEnu4Cy6jzMiMF1emk9oHOyHJ8GmoGxsecGguFIuvMl0tIV76YP9Mup9e2QMvGKF34tFza8D14jUA14G'
        b'+0CHlgB3gEvgii9FmU9hWYPr8AipUx4BNkXGxILLeD3GIwJBa3g7mVcTcKYumx6uAHBWBA+yKXNrlp2Iptw3mMbESU95Wan5d+kLtVeMLnAM9EbGgLNJiIHExXXwwBHS'
        b'gyRwl4/agWF3shGVlBvPYjqDTfAumb1IoFiE3tqfGIVoazJqxBrYSa/Ugz7O2dlovzqIP4Ay6xiJcK8beSXlBXg1MoYFbkWhdk9B5DgHnNRuhA0N2Xgr24U/iXJ5cC84'
        b'yjSBraCZXnFTV1GPED3aC0rtV05NpOkR9MHdGWgIylyjOBQjGZXhgcaW6P1eDLNBDFcW/kbLgncYk5zAYbi/iRQ1Uz6d2oXWSb5v6aJjlRH04kXkfwT2oLKq4b4otBuk'
        b'UEABd1TQvdnJg0ez4Y4XzHLQ/aiYEQrPgZOkqD8sdKTQ3NXPkJYuuF/B09L0drBDlp2J1YbZbEZgMuj0tSTswmJweTVs4/ijVRBChUxBvCgWrsPN4KwrMXq2hmdmZcDt'
        b'M0SzafV82JwbjPYfippua+TsH0IT9l53sEUHudQI9wXhz8ftTLBfBs6OeVFSOmHjfUr4sXFpTu8UP3qzQ+06twS2ca2hEu0LVHDIjEbiLafaeGz7VsDbWo0CdMSwKR9w'
        b'ltO4GM02JgUhgwV35mMrfbSJ2YIu2MxYCHeDfnrzuwEvsrILZXAL3I2IAXZQaDQvuJC1XOblosMM48PmHP1a9pnBkYJT4CqhQcSb3wHX4GEz0DsDf9xH/+DtmWRzYXsW'
        b'BqHxyIV7MkTmwVk0Ix3OpnwLORHrSkmH35/tTCHSTVzlWLrgXlosTdYz0K7UDA8boek6jIq8i/5Fg5tE/RD0pa7UlwnWB+oKZVK+RRy09d6gl+/VpfBYdj7a2C+jk5WB'
        b'caleQquWPlu90uCBAnQY70Zn+ioGuFrqYj2PvOUCu8GZ7CJwGbbRY3GKgldWwFZScVgC6B0PzQYOlqCxcAc72fBaLdhPU9wB0LwQHrZwgOtRK26jf8HgFL3RbvWLxas7'
        b'JDPPEm1yu4MyRRFsyhkcYtcAhQfZxYQytAcfZi1kYmAyjE3WbUm/eiEU9YZ+F2x0o99loncPs5e4+JE+8dBZvQnupJrQ/ykpJYWnYDN9Im51BZewBYlu8sC1csqKx1oE'
        b'L8cT4uKuBOdBGwvcAB3oskC5i8X0OJ/izA2i4Z7hLtGS7FAajs0FXGXDHfA8bKP3H1QnHx7mwNYi9Mot9A9Rwm3SmRJ4DF6HO5nwaBpaQNRieDKW7HLz8yZli0SZ4Lx/'
        b'Fl5ovESWsSnc5wD2kvHzQlO+AR42h1fCMGod+pcGOmlwB+xrYreBLbv7MgJaBC65kqYIY8FWuQVaXxss0AaFFh+8EA6uExpzE5hSaJCETwWl5ttjiunFDlp48ATciVZG'
        b'LOJTqTp0AbpGiD7dqBzd2jIwRtuu7BmirGDYsxY1VOjMRgvjCOggcnNWnTdjgIXKrPIu/zR2tvQrWq4QDTp8wTl2EAtf2laCzRHS1j2+bHkNmtGWNOv9B+YXqGdavx4j'
        b'LTjkyRnesVHIOfvg1Jci5cv2+TeaNEdSVSvL07c5nA5N+OEvP9g8+sdKW1m047shfstOt3397tOnH3+qVn/6+Nw6jwbWQAn4fjlj5UdZP674nFu9qefy/esnMqTGm/bK'
        b'tnx4TzX32Mp53W9aBN4M3Dg4fIFhfsH/rclGYfW9Z/vqN+aDxQHLru/9/d9r0/rK1lmVvv7Z0/1fuaq7Z70UEZ/3qMTG69ia48ed4nf2lX8Rf+Mz82OHPnjxtZVL3ww6'
        b'qnRpq4rLfOXPgW2CGGtfAfC2deImt3lcaakfTmwvM65qqf8osb3SODIjtkr4dsTmOO8jMdZ/cEy+NZIZErY5zTvY0dh1az3D5LRzY6tHsMOd/CDzL2Z9Ie9/2/qi8Iuz'
        b'GwYkxhrTThiY0l/cXr/J45NUIGJ9EZ0y0tJTKfxEbLy8tX6Gze2PVJctjKxn7+34/euR/ue7pVvU17xO+HQLWuumf735p+K3rKO21/z59T9+Ni+5ZM/X3ZOrv04YUu9z'
        b'+9u6N02/anDP8Xq6NvqtU1XpT0p//06w14VHzrOK3jpnudQ54/UacXTXo6fV38b3vfXG9iffzy+rVt/KeNT9ne/Vhyuj+l7dWsebvHLhxyorT+cntmsWRxdJ4uZNHU3I'
        b'uf5J5Z1/Nb21aO6PX+afXbN6QdDkF4R9teEf1vzO9bM3/mnqD0JSmo7zXim43Zq9+Xdz7xSPTvnuq7SX84ojGm97/nFyWtM71p+1sL9MaF7vYfzlXZOipPs/eMk+Lth8'
        b'/elVsdLts/DNL22cervqJ/dXEuNenZ5i0Sl4rerbL80+6750jvfC3B9rsmvfM42P9+i79X3MU5hQo7zP6L/7lJGX0X3zjQ8DeESJCp5Fq2nLmBZVSrWh1hlWorKbQgsS'
        b'lEngZlDeWrhdhO1rDzFyg+EGoshlPgltLDsx18Kl2KmMItiCtqVN8BBR5FpdjK7vO63qzWXwygK4Fey2WmZhwqX4oBNbgvJoVI6esLVmoDs4Q/eNwgbeZIH1c8GFufAu'
        b'qWK1g+k43eQF8C7oBftDyKeVWLAR3Y92hmJrHnSt3kNsrE4wwc7KKbQV0T5vdOHaSctoF5tkokM1l1mBbwDECrYQXoFbs2eg8wB3bBkjyXUNbb+6GZxGR7Be8RnswTB9'
        b'TBHY50U0pmNAc6oezoQBji8AfatgK3nkBVoLaNU2otcGWnKYNrwwoiDmCo8tMQOHCp/51GNs7UX7/bsA+yOep4kmnoUV0TyI+Bltc/uIEe5EVTR41g6cAG3uBCUEnnSs'
        b'xIpv+OscZprAnmXggl5UHRTHAdeKZpPyWLDLQy/MbgI94+XZInCbzBO4mQo2GOCbsGAbbdKL5qaHfMUCL8JLNVj/DSu/9YKrBgpwR8GW/9q2ajxWB0tcUTFsMSaPQlEi'
        b'hHqZrbUAtqPcPLV4XpEq12iNa1I/CvLuzW0x/YTv0M7tNOswO2yh5vsq+ZqAOFVAXH+gKiBNxU9rYXzG43/i5DXgnX6f/57jG44DBYVvuai8i9ROswf4swd5rgr7D3h+'
        b'+NtPdms2/iiESlKkKSPVglB9rDtSuaxHqgpNVAclqQXJY7mie/y6p/UnqwXTDNKIRVeNOijl3iy1IGPig0WojHsRakH6xAeV6qCp/bLxxZMH1eqgafds1YLUiQ+q1EEJ'
        b'9xjojQe/to4l6qDUe2VqQeZzWxWuFqQ9tw6mWpDyqx9I1UGJ9zyfUxR54PFz/XheURJ10JR+1Nykn31jYs9/dhD1Rf1N5GxnPxpPCTwVvkr7rpAeL41DtMoheihA1C3v'
        b'iezn9i+7YXlPfp85EJutic1XxeYPzCpSx85Wh84ZCHihndu+rMNy0MG1vbJ1rcYhUOUQqKy4tKh7kdohlnygTFC7TRtA5ODs3pnQmaCc3ZPeXdxfcbf2Rq1alDMYENrD'
        b'7XZrZx+x/LcZhlw9FdFKf5VXJMavS9cSqIJ5xqjL6AH+jhmkEgQp03vyu7M0wQn9kZrgtHte95apBXmDArdO0w5TxTS1IFIjKO43etnrXuX9ElX6QnVysSq2WCOoGCir'
        b'GBS4drEU6cppKu/JauEUlWAKKVX7acr+ulOvU/8MdXjOfTRo+YO/9MhVwVUs67LUCGNUwph+rlo4TYXXA118gso7Xi2crMIW8xPLyFWHZ91PIi3+2UdjXU3RPspSh0+n'
        b'19Xz3kFrccazHZmuDtfT/YTistXhGboH497Jus9Rh+cNzMxXC2Y9+1qeOjz7/hy1oGhQ4DwSYBdg/5Cy83B4RNnZCTAmjePB7L3ZimgVP+CAoVmKGS0ZxxfS34bYgnfN'
        b'Z+BaTmDx60kUnNUJyvEn5Xw7BsMJY+L9FtsVIijv4AZQ3WZR43Vl9d9fqikaF4B8ecHSXKrISP/lhTFOivs/92QnpCZKcf1oKe4RxBixzbM5GLRkd0woRX+OwYxOhiu8'
        b'AjASSiq44Ua5zQeHaaZ/rxfsA23oVwg86kg5gk7ENROM5xfBRngnko3vMPBgBBWR60hq2L7EmLIO/icXDX9wZYw/RZRrilNMKGv/eBZKND8wNZlm5lO9VjN+mJfOoMLE'
        b'q+5UL9fyHdfgNd/IKHZtJpYyUeXgOthB8w5VKJmbkoXNrimJBThIyogqM6LMm2yMKGGpealbLF2wa5ANJaxupaj60uBjnDi6CSdCrFHiAy5KNLc1MqVzJrpZUIIp9zjU'
        b'zNIcH7NVdM4ec5x4hIkSzdfkBdI5L7iYUXxBuRFlXRrMXFtD5/yzBeKcEncyUaJ5YW0TnTjgiJqUo+JgQOmFxka00eAicAKuR1y1LQV3F2EJBGcZA9yMg71kLIsRP3o5'
        b'MgwLrW2We1Ngbx0t1DqR6EWlJn6OZyt5qqyRnqiF8Hgl+cifA3oQF2UPW2g5A2Ka58PDpph1Ww6uoYEEe+ExWo/g4koZPMxF/GsouE6B61OMabnJUXh5AWxDxMvwFlEi'
        b'uL+BVCqWokukcTAHK0IlpU+haD65MwMqEN+/H/+Pg+6DBxETuRWDuu0oJl2IhofzAC4LnEEsJ+UKds+gxei7wDkMk5YZXGxrqObkALoIRzs3uaFAhKHXGOAuXA9bGbZA'
        b'yaEJ7ALok2MsBrgDbGjCrHsdSefAy+AQOIc7cBdsWkGtmG9DoyVecQXHiQYYPAlvraJW1dEqAWRS/IxRvf4/kk4dnR5FQzoNbu/Bq+YfpQyK8eFtqdzqAEe+DHWhN2Dp'
        b'S0UY+Zm/+tYV440PNcbGzfZds3c5TTrS3/KnaSN9l3yLM3d9cvvH7J/u1mYvf/nb4K7w3uvvvn34ScfjuJ9OF/ru48qT/g7LRtOvfFAX1MHd8cn0ogW7ONl2zNuAsW34'
        b'jOnqRYjlf/Hshe/WBwxcPes780P7oON+S+ffDvXJz1nwufCvi78Ku1DxT7Bj3r3r4Qc5H2+oyT/8eq9Z2Afl6sdNhY+aP1m56ubV8x8v/Yu977FuR9cG6fyD7x54S3Fy'
        b'51Hr5dk1oW8uO3U1Zc45T+t1ZX2x/zjgE7nnX6LfzfuUNfovM1fW54/fNbs6/+2FnCfLz/7j7gcbdnRVhhq57TsEuyO3eWxbPXuB66G0L8uiY0ZXJK7b/Yfm6VPa0x7f'
        b'uZQU47B1UsEbl/7E9d+S/yNfPvzl6Fd3Ht0u/v7SO64PXne6u3zp7gTFSnvbb8Vffuvx2ujpz1//plLWe6nvrX+u+iP7n5kjd+/3r13ZZN/oLv99Vd+jRdz2rz/SuKVX'
        b'7n7p/X3fuE9bZDT/jT+cDhAQtV9wmrfiGVWv1eD4BPXOFeAgbXVyGewHu4mK31J4Ok8UiG/dV5nggAU4RwMXKmF/kp6DgofBFtrCM0wLARECz4O7mJ2Ad+ApvaHOzPm0'
        b'bUxzI2wFZ5owK5GLBX3YARnGJExigYuI0ntp1a8eFjiP0esx1uB2Bti4gOKuZXouBHtpH98YjmqCk88ueHAcpwm7wQ0aDPJCDFq5qDlBLHDXFXEnFxmIXbsGjpHGisLA'
        b'Ha0qK1p+02hVVhE8T/jN2WAHuIGrQWztARpmkXwusn+B7ewMj5I8dfDY5FwecYtOgywSAb6tD+7ATthLY0vs4dvpWLg6oCDWSTZwC819bQcHrWAHvPU8Ng10MZk07sZl'
        b'xC82G8JBWjUkYW5pOTxAM0s35poUkzGZyMWBExmppIw6eEYEW+WIo8oIDgnBHwVRO2E3YrzmpNPc4p4QHm3blAavj5k30bZN4EQTGbCYF7gkz55sDuxHBwebyQDHFoOL'
        b'NL7IRlN4AmvsFZUaKOyBqzFEORBsdfF9nm6gTjEQnkUEcJbrAo9OJQ32AYqlmBUHvbCdBtegWXHEGF5+5IcyWIItE3hSHa8JjnjTPClivI8RkqpInUZ4SXDQ39CWCiir'
        b'6CnaEAOPBQWGrHbQo5CDUzYFv8psygAeYpiN7Q+GLccYSRwnnKQxi0bFnudA8R1aGtriFIy2hEFn1wfWfKzJrLH2Vll7K/KVzEtG3UaDfCfyz0F769bwA9BNTsMPVfFD'
        b'exhqfkRPRE/kAD8GPaYxGZVeKr5Iw4/u8dbwE/q9h/hCBf+Mc5ezxiNc5RHeE67mT9LwJ6v4k/uT1PwEfamBKn6ghh+m4of12Kj5kT3JPSkY+eOXKx1C/C5bIwhUCQLV'
        b'/CANP1zFD+/xUPOjemb1FAzw48hzzAC0zaCLUKKHwcpZSvQwfGKLC3q8r4f0hmgiMlURmff91REFGv7cgTlz/9N8MT0+Gv7U/giDEYhWeUT3o/bHa/iJKn7iPdTTFPzY'
        b'RSlDndLwY1X82H5bNX8K/Y57l3uP59h4Jav50+iJGFdPbI+vhp/cn04eOdBdRuwefYVXoz57KsMH+KJ/80w/zyMxLuG2DymXAN6TWIrv1Brd7q/meT2Kc7HxGYmnbOx0'
        b'5PGBtR8iGDr2gbXvIM9Bw/NR8XyUPDUv+IGWReMo2Rr/ySr/yToeVNxhpRGEKlM0gmjEYLLvmt0we8hiBKQxRimGRxrGr7ZLxwAPNnYHzVrN2lM+sBYOGtbi4HSwqbVJ'
        b'wT5j0WWhdghpYWsxRBUeA3xvvdbqAN9n0Nv/TG5Xbo+nynuSxnuKyntK/xy1d5pWWb8Mu5lzcG4xe1ZV51eAsRA9nXFYLHcx+3EPBX/RsR9/R+zHXAcGwxbr6fwmoxA/'
        b'0phh4xLaDEEuS8KFZ+FgOoOoVxIjQ1kqTsnFwVQGdiNH7vsBjK/RlegpMWX6GhuRBDg+D2SFti0kftFjcRCHg3hcurHOFkz3CyvAEIso2uiF2CoQBV6iU0n03bCW0rB5'
        b'ycykWUm5JYVzZ6YVDLPkkoZhNoaKHDbTPihIKyyg+bS7ejSW/0p09gyuCnalRwJscy1fzyS4Kk+4VhgwBQWjnhTfZcjab5AfMcph8qOaU0e5lIv3kHXoID8KpbhEN+eM'
        b'waZEYtiUSQQ2RYuIEowRUUIMMVICcUowSbFzHbL2p3FU7MKb0x4bsyxCnpgyLWYyHhubWUx74sS2CH1izrUI/55CwRNrlkUqY4TC4agl5ebRxe+qHnAJHXLzGvLxH/L2'
        b'G/INUHor5qE/3V7KCkXx2A9vPyVbEa/74+GraFCY62JuHgrv9nlDnjjmMuThrShUmA75BCqjFDmj7tYutiOefEfbQb5rh3yEhX494Dt3FIxw0C+MvuvRFdklR1lDRoxw'
        b'ijFl597FwyWMmOC4KWWHciv47VkjZjhujrrcIVdEtS8ascBxS8rOZcA1fMQKR6zHXrbBcVvKzrMrBbdxhIfj/LHndjhuj17uKMeNH3HAccFY3BHHnSg7ty6WIrV95Ygz'
        b'jruMxV1x3G0svzuOCyk7p44UBbs9fsQDxz3Hnnuh+Kg3GnLcFawhijJ974cTffxcLBEFFDIoF/f21cpMlXu0xn2yyn2y2n2q2jlhSODcnqO0V7mEaVwmqVwmqV1i1ILY'
        b'UQ7L2bI5+4lpMsMi8CGFwycZzDALl0cUCmijEHKZ7QabTMjlF2zx0t5/OZR1IWueOGQcf6/za/4QQ4Qk2EwAymDKMIgE25NCoRX6vxEBR7AaHytgTYiz44zcqAI3oiZq'
        b'UmQVxS7g0CAVOqGDjLOAqwfYMCYAGzhuguKmJG5M4mYobk7iJiRugeKWJG5K4lYobk3iZiRug+K2JG5O4jwU55O4Bd2LAnddSwvsQnBbuaRnpiRkYrvDif8V2BMAB/dn'
        b'n0wEcPg35Tj82nJEBr9TGdGMAmERk4h9aBU+M+zVMsqkwHHCiNJ+5S3JaDsRgAibsZkrcI5jEIVdFvaPGcUpcME59O/aFrjKeFUCk6oAj2FjgrKWnZcm9cDfVisJBq8u'
        b'TVheI5bLhf7YD/kyiUwurq3Au7ZUUhtgahpYiAEdaW+A2LllXZm8rkbSQLuoxG4Ma+qw9iV2kyipb6A9WxKQycAQU9lSCmtvD5uIK5ZJ5VgTc9hM+5MoVBrT3uJQMqui'
        b'ctkwa3EtSlsiqZA2LkFpxvWoVcvrZBXlxhMom0iuNlKGevI6f6HENA2PLBuNKQeNC5coNVvo3UoYFxp4BK01caOKDNxMFJmME6EZJ5kQwdozqYaCNfEoWmKmmbXSBimx'
        b'+9NCIuvGVlorbxDXlkvG0Db1gxGvReMcc9qJ39QqmGKfnP7JtFor7XY9gHaPlyTU6hbT6MjCxnpsuBwjrJBWSRvkIRNqoR3Za+vBnkV/oRb0WFdHrVBcU18tFj2vqjhh'
        b'eTWqopz4/9T7z9TO5PP7RD8V+uciokFV6hzJ/2KPJk3sESIR2vVjavpsYY24TFIj9Ec/Db1fBoRM8ENJJkVOahnfFDIW/hEGXQnQV4TIMF6YQ3CO8FvTQ3P0XkPpbqG1'
        b'UiAur8Z+QEmdxA0rWiJaLNTGshpJhXZNjH9rJgrramkPouhNAoWK4nRPtSuJHpPMBr0fVbF2WMokDcslklphlNC/gnZFGUAWYay+4bqlQw8THRNKK7QDGjlxQHXrS+t/'
        b'UxsTyiRVUjkaEbSW0ZIn0xksbNQOa2Mt9pP5b73JW9HS5ClZNpTwhUtsqr4057vVHKoR21pAZW6UzjgSXoJ3tb4ZZhILyRy9XCLfwD4Sbkk0t4bbafmjYxWf8q/+ABti'
        b'rs62YVDEyeJysG2drtDnF0g8v9NlwsvwNl1uZ705PAm3wxZS8u1Yc0rQsJLCgt30qhdox3We4CDsem7RBiISw8aCfnB9DWg2A11wPa2k9dUsLmUedp9FCUtrZtU5UsTX'
        b'IdwLzqCin1dwOTyTGVRgWOR6+KIJ2A+3WpLyYlYYU9apfhyqtLQmK8iSIv4CrcAW2P284mDzmGRqfDtrmsA1M3CCNZmUKlxhRvFji7lYWP1gciJF9LDDGuufV6a/TuYy'
        b'rsCb4BbsB+fM0LyeipL+9egClvwsKsM6oGHLe1Mtkz3MjUa+z31Z8N4DkwULXKa8sqomzzJ923KXly5VB9vWLOKBmT88HS5fm5g53/+a22BQk8OnHAdF4J0790zW7ix+'
        b'75t6o9iq9W1dn53vXpWf9uGUqV/N9XgvbMW1t07cmBS5/B+jS28/iH1t9Gi5b8XagoSQ2p69pZzXdhz9/aLiw1eXCNotIGuf4iLHznFS46KfLotdzu8ulbw2b82FT4Mu'
        b'Sefc+5h3lwoYHUHnHfmYz4V34WksKBsvJAspd14HmkmOOmt49jkmqW1LjeGGImJhujgLvGRYBBYRtYAbuRzKHbaz4SVJMg3mcxQcs50oboP7AojErdCcVtK4CHbD80Eh'
        b'oB1e0uLTYXS6cthNNCqKp60EO8vBFiwS1MoD+eAILSzcAPfCG2DnNHtaxEWLt8C5elp4uc0HEeEEySU4akoLL2/CS1rNBi7cOk7KBjcuogVtucaPsCEeOAeOTqVFsiK0'
        b'tLbBG/CanIhlUUoOuaSKuFQu2GyEensRXvsfM2wE2sdGd+COR/ZxoKFkR5scKS/frnJlwIlateckDMozxLNvaTi4rnWdmuen9FDzggiMz3S1U8YAP2PQOxTD+HiQTBoH'
        b'fxXt4S1JzRORbJlqp6wBfhZijroKlIITC9UekRjahy5zbetaNc9XaaPmBZLM6Wqn6QP86VrPJoezUU4TOueK1hVtCQpUqg/tLE7tlDzAT37g4k6y/KbCPQLOuHW5qT3C'
        b'/31WL58W9ofWwmedYbyLOd/3cDCAAxUO3seBGgcf/HtbNr0bjAn2bERO8AWWL6DLpxxvVk9/wJaTjgzGLOJzbNZv8jZGvLJyI6g+s6n/FQyRaYn+KvZzWERjZKWDIipC'
        b'XTAA1KEverrb1nNAfv5zGCIt0I95icFV7ucAZTCG/Qu4Zd36lrlNaBm58Iy1679pkkmJ7rr3S+2Zj9szhrHjTrdHd/96ZqD+G/Ahdgm6HP5SW4pRWx7qwXbmHppLt8mZ'
        b'bpPBhfK/bE+1rj3oDvlL7RHjsfkLQzc2/mO3TfFExCj5f90oPTKS7n74Sy2rGD9rTljyb3CV/J+1RXfd/KW2VD3bFjRb+ouqQVsCmETwSIsg9VZ0eeUsg9oxhDYxoyOu'
        b'CE0MDF+5hGPEThlMiDtC7IzQosgyylxvBmv0vzWDbSxCjTFNqqjAvnFqJcsNZx2tDuIlJw1xGHQEs93iigp0H0e3eLGWwSLOb7BDhWBhlayusZ7mvMXC8rolZdJa4qrd'
        b'FJFToB4lLDBYGGgIaIbiBDMNZSqrq1uMq8ZcP2Ep6GqxY/gxtlVfULywoG4JZq5ooQB2DKHFEhOX1TXSvnzwHEkqdH3BDA12Qy/BXaqQVlYi5gLtATRbM76R2vEg/n1Q'
        b't6u0biwq9FxRubiWMEW/xKGGRxvwdUL/unrie6hmjMMzHAea+3lm2Qn9k8pkkvLq2sbaKrmWXSXOLUhDxuZFLpdW1ZKpCSF9NChI61ZKKDVstRRxfojLI6XoOLpwMujR'
        b'cXrGDpccHhCMxS7CCklZAy4X5ShHPJkUR8p1vCahAinJL5c0kL7HxqE5S8fWtURsM5G0pBJ5vH5OUdnSBm0GehxIip5x9S+oq6nBzGpdgDAwcAnm3lH1KwID9Ww/adG4'
        b'EuiksSKmo+7WikIz0P5a+0tF0YhnWl60Tk4arEVBe25+TKx0bkPyDRHm6tlmQs51ZYsk5Q1CMoI0DRXMiI0OC9eKtLDEiqbekOdXM856OX6CeGFZnbRcoieYZEmNpKoS'
        b'5wsQzg+PWPi8IiK0w9wooZsnrSUNwasgNTU3d+5c3FLs7wo3tV68YgnxjiWR4c03WLgEjYueCTeoMGJ8hdrhwzgH48cTp4wXkdDUFaqjLFItfVVIRo3GtI/fQcVHhi18'
        b'dvUslqzQCXwMyAylIgqtlUvpSusqSaniikVoZkh/cAbi4kvchH/Ta5sWBY3LJCeyKWl5dYO0CjdFXl5dA2+jnaUmIH7sHZEQzUtBg6QRLXZ9BkQBUqG2C2iFLUEUmVYk'
        b'KhQ3lEmwPK5C+yaaDtpTTk3jksWSapk2OXJCMilN3Fi5srFBgnYm7PNQOLtOJieVat+JihcmNVZWS8oaMSmiDEmNDXV4f1yszTApXphZWyFdJkWTX1ODMhQtkYsbVson'
        b'tFybO/p5Tfj3HYp53mtSg2qX/HK1sc97/5f7FUc6PjY0E0aGBIX0TGPB2YR6n5lJw+ZVylDt/riv+jLFZSsbqwLGps8wuzDGZ2wCxz0Ij/MZm6baUPHYlIzPFu0zNvxj'
        b'2dCg6us3yBNrmKyvOm5cZlSvfsPS4hmgFaP9RfZndAajtahb6v4F9B6p32DH4BHihSkoIqRj6Mzwz0ZRSS36P5pWId5zYhc++1rE+NciJrwWMe41grFAbxmzkwpFmalC'
        b'/6KCBvQX7y+T9Nn0GAx01rQispJxgtAfEaV2itGwjnWjUYaO/HK0W6RofwULDc66tKJZQv858GS1DBEZqitqrCoDeIexl/XJ2kp1r8oXN8rkAeOOv587PsnROXYS6o+w'
        b'pHEy2+efCQRgIl6Yh/8I50eELfz5bBF0tgiSbWw0dMgU2iNTG8cXbMNxJjAVKAv+gx4sNB1bJRkSmaw2NF0mbkRBTUhouhSdZmOrgjweWws43xj94xfGFoDhm4jq06rR'
        b'oYLW8hjpk7LQmVNBF6NrHDo1JZIGvPPiv+iAiB53/pTVNcUL8RcltP9X4lMSJaA+hI3LhPEz6FziGiGOjMtRLm3ABIPCcccPDQqCn9A/yIvB+FwXRYZHR6ORHqsD42+g'
        b'CvCfcTNQKUatS0dEa5hIEDrQCOA/wvnRYROXhXZJGM6QDhskXpiMftEn5/yImHHP9aRFsoz/JjCuvzpEEW1OejzGFifGDUFHSHJSHhqOsRVSJi1HL2SmoKIQhfwbJ5ha'
        b'ufx1PjGTpuqrmoJ/EpTRrimXxsHr2XAX2FtPbKz1BtZG4Dh5aVYQhnKnhGFTlwfHRa7RWqIfF0XoTL7BHj8G6ITbKkn201MIVIR1mEiy4LHnMtrAc/mitbAtAnRyiCW4'
        b'H+ylP2tvQdW+lA0OCcZspAmUhqPWCF5Rshpji7xQ6rjcOTA9i2rEn1Pl1jZBKGsWdqCBFSXB+axcgt8IjsOeQuyJZOcsqinKpApsgXuI1alq9QzBeqNmCxqt0d+fTcu4'
        b'J0nXPQesMQaeJ2CQGbQA0xCuEe4GHeYBoO0FIj6TPp7hz5IbIX6z8pTr0ZlvZcFE/tTlESsa31+bPD8lafnNsPxgu80X7eR+wgq7gT+d/qfzU83haLVpebSlOeuPje99'
        b'8vq3zrPr/mT6+sOL633alx3ab6HZeOU961frjm06ek1q6dxnybmsTnade2bRnI3px8NkvDPl9cp8m9swP1wR0j3lZMnjrzfdmnWn7sWDG3/X9cc3/9yR8Z7SdE1J+G2v'
        b'jtPbZ7wzS/PtpkVvXB9d0nPmUM1snzvLRcOPi1fmfPX5usAFTjPcPktdvP61I5UdD8/H1QxULXjr/JybO99svX3oR9d3pg/BP1QmtG267Dz03YGseV/yHKojXn+1+kyf'
        b'kaQqblHjX17ZOLV7T3zNRk48V/rji37//JHhMzcsY+fxAGOiWjkHbpPA3bMNrQSZIrg/lwit6/3W6Q0EE8BhBuiD/fAyeW9pdgzsBsoguH1GJjjPprg1TE9wHh6kPYDv'
        b'LAXtWsk7uFVkaCQIj0AaDLIQnl4+Jo7Wi6JZAROF0Vm+RFF0ZSTTAAsS7nPTwUESMMjacFJxJtwG1ssxDYj8ccZJ4Ab2cm4DW1igJ8qW2IECRHJm2TmZDIo5iwHblgaC'
        b'DfBmgNX/0icURlY2sPYbb7sybK4XV+oM/rIYWqA8N0oYrHEPUy7FMPbO7Q1qntdnzn6Dfv7t5hjuzFuxrCu4h6VxiFI5RA35BXUX9PB6Kvqje2vuRd5LHoieronOVUXn'
        b'3i9XR89SiwoG/Arb2e2zO8yxT25uxxTaR3dr6qCdm8JbbedLig5sx4+xu+/D+gxfYUn0NLVT4gA/EbubWaCMG7Cf1MIa5Nm3V2jcQlRuIWpeCIGj1DgHqZyD1A7BPRy1'
        b'w6RP3AIHgvLUbjMGBDNGmCy78KGwuH7vgbC0e7z3w9KwAicxNuKpBKIRLstGRBQcvVV8b0UB0foUvc8XqfiTethq/qQfHhlRLj4PKQYqxS1ImaJ2CxsQhP1jhIUS/vHI'
        b'mBJ4oGc2oiEnPyVL7RQ8wA/Gz2xEPxLcQWhhn8qmoLd7qhv1Cts01Zn1iqVxqj3rFXsO/u1mmjqJ9Yq/cWoY65UwDvpNy9itaBn7mJQKW6H+JpulCVQwzt30OAsmFpr5'
        b'RVjSjj9fYqivfGcGIxzL2cMxTmH4b9Ej/Bv1HDhgcqYQOGC2FnicU0QVcfV4mP9b8PGqAKbsCTXBE5D7M0ebD320fZXCib/DsMZfh2tGQ4ppkJPw5ebyxvxJYaANbsPQ'
        b'FGhZM9YIEseMm2CnK7hohsZsDrUAds2BB+NocI/rs6mCSWHoFaDgUwx4i4JXZoLNpKLFK9fE3WGOcKgwsXNGkSUNpFO91Dkyiot2gh2gA5shrYXN9DGpKAO9kVFsjEwB'
        b'DxC7pStc2hbJ3Ki4hyHA2Og1rR5VWl8os61jGYxEbKBkzq2W0CYqvbE2fC5FJ45SYXTOr5rMZy5khOFP1jlveObROattLapzWHSiaN1iOqecMnPiU/7oRC6tOd0QSOd0'
        b'8jFbFEgn5mimedKJyjAjpzks0qQct+I4GlPEER6CJwpmzpyJ0Z1OUoxUCmxIcaBH6WQmsU4KQ1v+DjRKJym4oQkcJs8mwU6HgpkUNos/TcHj4BrcAI6AIzS60NUm0E6Q'
        b'RIrWgs16oyfY7UvmZN5MV9rkyZuChxvA3pAYGth0Z8oq2u9Y+RQPeBYeIqmNklXY1CyCAj3MCHABnqRNhHrWhRADJhEGqbor8oWXaGulM95QqbdWghvhDZ21Uk86PV93'
        b'oAK1W8iiCospcNmOC7oWltM4Gn05TTovZeCaWGeuBPtBP21NhMd6yM9ElsYQ4kVq/l5mDj2s9wuNPZ9SdOLy2kyaMrngMtiDhhWXvAk1EnaKQQu4SUoxTrWz3ULNxKS8'
        b'4BMxQwtZtF4ILhbMBIoAqgwco+LXmMGunEWk0Wx4wFJuERnGNluAhvscBV8KBO3SJY5qjhyD0x3I+NepwuwZINH62KfXbv9ezFhhctX2b8kj4NXUS7Iv+uBrkSajgyVf'
        b'fvj0zzUfLwy7Ze00fPLFjr/fOfpk21OzSy33bG2viUx6Qr8Y6iv6l+UXbZe2USaf/xiecaes4ycfzV/j7vmyM64qrt63f5Qz5Y20+kPzmbKvRVnUe9+8uL1vyc5jyviT'
        b'CVzHvXnKuEenrk+6N1ld/Jf7bxn3rG75NjJT4vxK4lxpbOzZoGNrth8oOPx61p+uXXDoYhVE/r3b6wfToZesh8LuH+bP3TMj9eJ3R4Jz4fvxZV87VIS3ls/v5Z9NfP3s'
        b'vSUeq5s2uweZdBlFz9vlumvhd08+9Mvbcaz5pdvvnbY894ehhMkfBP8wbcPZf/RuW3P7xCrFosyfWt8pHYnan8DvfcVjWf3sRVdcOmqbGn6I+WjeP/dUl9f4pzTuf2n7'
        b'4pU+6msmbZVt367Ny528YvL1U+9+djsmPKeo7stvd3z9duDjr3p2vTs7OGLKGvM774tOXbdLCA46KCk47bwvuuLIX9LbU/72D6sXhvJPN5YF8B+FYLLaAw77PudqYnAx'
        b'WQDO0h/KNywmn/AxsoEiiFx4eJ4ogzG8xQStFWA9uXEkRsxGF+AcBrgONlFsDwY4ugp2kltUSpRVdrB/BrqqNmfokKjhQbCLtr85Do5gpRad0dOuOK0L2E3wGNFeSMgC'
        b'B7JznnW1JEzjoIv2FpOoabSBTDd8CZzSWiO1m2u1DxLhS7TZ02nmMp0xEgXPwfPEGgnegZtpy6zN5cKJShZ5QPEC2zlVW/pBE96Y1RTaOedhq6l48CJtabQNbC3RaU6A'
        b'Tu9xtkroLniBDNAquCGMvmiCDnsCRtFXUEPfJI+BXaAve5yRkiXYxCqBe5MLQRdthtQtA/3jzJTgehY8A0/WoVk5TvdiE9w/VgwxU7JcwwrOTYWthbSGR0ciPEnrT4Dt'
        b'cPs4SyXYPZfu6an5fnozpGMLaTUN2AVu0fofVxYkad0IgjugT2eHtABuINdXB3ARXtapcSCqujnOCI2qeOSFMmWG8SZoo+g0UfrQzFyCF+CW/8Dz/NjFA38A1HqdJ9dP'
        b'A6/z2OKSYE64E6/z2P+R2aDQWyMMUwnDaCN3jTCuJQODjDdhDHIMXe4qVNgdnqf06ChuSX8QGoPRy8+ta0lr91fMVjkFqfjBD/jutAGLQnZmedfyQYHzoMBNYd9hNSgQ'
        b'agQidA3sQXfBKI1gaj9fI0i7x8fwvYVn5nbN7WGoBREaQaxKENtvoyZ29J1W2KIEv6QUqwVhPbY9vAHBJPzAErukJ4jm+WpBaA+zhzUgiMJK3Bkal3CVS/j4ovqT+1MG'
        b'BInkeWduR65aEKgRhKkE2BxJQJsjCWInNjCx30EjyLqX/tz06nsZmtQiVWqRJrVYlVo8UFKlTq3+LTld6X4XdxX3oB7EoPFQoSFBvUxE49XFU7xwwlWFwdtdyQhq/+EO'
        b'pBJtFUuFTMkYEAT+XCIqZFDgjho0Msk5zP4h5ezv8CSaEri1LmuvVjv4PYlxtgsYtaI84kfSGZS7Z2d1R7VildotssXsM57ggbfvmeld0392nEnJPzM5pFsan2iVDzaG'
        b'EsSjUVAJsDEURr0YowUdSYzYmIhQ80x8HJ7YjjVPGTTKM/GJRnTl25o7wqcEri3mz8KE/7LSC4EJn7gUZE6I6L9iGZjxpLkzGLYjv9WMpxKXxWRMcPCid/5HkOk5WkBY'
        b'tlabHDt64erBYLn/QzDYzegmzmFMuIk/C+JslNdI7CNvot3qclBGcGUC3D4zA51g6KQC3YUZeo/lGXCrUT04B/tp0Lle3mrYhqI72KArmKJYNQywEZ6mzcdBixHYEMSG'
        b'F1B12NZ7FzxIW7WfAZvig2YwKcYsCrSi3e8QPAT6pH8VBTLlj9DzwI1f0X7+bLCDofbwV5Njcx09gi2UGTscWSH/PP/Kn2YUsv9c5Zclwl79/HIS2m18O98UALtXdks3'
        b'Bux7l3XI7pWd8xOa3QtC2k3gsjmKw4P71ldyIrf1HEpO8XsxfJ9HhvX1IWDuVmZufirH3JzzZpegblcSaA/02pfbIQzmcEtMuNxaoUVhwI6PczhbGxaIQ/YEbPV5l/2y'
        b'OGT7DNGAxeaffs9+OMf4lm3Ik4zyy177TP7wu1J7wc7tHi/67PPJsC9Y4x8Jcl8ubeYXh7SMZFXNrBhI+sFKmbA7c0OSmz+rkPfavdK3gt9ree3+EJOKKvQt/LN3gBU5'
        b'+sxtlqDBnw+uYoca7BgGuAhuFNLH/yXYjf6PjgLagmQhOIruFTuZa1LAVWI+WgI64VH8PByeoB3I5zFdVnmQMzEK3qrHp3pwSCa4BK6Tx2awhwlvwxa4nhxYLuBOKZqK'
        b'K8tFgUH+RJRiAs4wwYn52cTi2h9sAbuzg7F56/Z88FIOuh2YJTJhO+xypT0jHosAfbiKUAocnSFiYmPpQD8xKbo4Ct7MBmdWEXchBs5CCqNIn2cuq0DNzqxHjN5udFni'
        b'FjO9bCkasuoy7AQngmwExLG9KCSAiQ7zThbYMj+XvqxshQfgyWx8m0As2pbQPA7FncJ0gAeLyXUKHoQXS7J1lBthTJnwmaArMph+uF02BbV3dx7YDHvo8UpmCnIC6IIP'
        b'VhVob1rnEPepcyAMuhpJZ8OXgO4g1CZ4Be4PJni0Smawpdd/jQelEw2MuXkfttAfz3LxMtpvCFMrHsryoPj2B2NaYw4mtCYovDU8PxXPT5l8aXr39Eu53bn93prgaarg'
        b'afeSX896Oet+gya1UJVa+ImTx4BnjNopFtvYon3avMP8sCU64HkOtBdiDc9fxfNX2mt4YSpe2JCTh8JbyVIuUDvFt6QM+gadWdy1+PSSDtN2Ntqw8cuKwo8EYaPY6/0D'
        b'vsPBzNbM/dkPnF07YzpiOhM6EpTeGudQlXPooMCp07jDWME/YjmukCFXD4XnGb8uvzPBXcHKhp5CtWd8f+oHrkn3Zg26uHVmdGQoCo/kPWFRbskMlWvS97iez12TPnJN'
        b'+lGOVYNe5dimeXNe9TZNizQxdMcoY/1bxUd64Gnni+MsOonHeGxH6M42AJRZJWQwBNj54m9xVEI8RgQYD5uVYMtNMVaQkct+h8v/Iw6+wcF3OBjFwSMcPMFvsImQg4Y2'
        b'J3DnxvrjjUl+5wXwn2vc6cKgDC08f4Vy6H0G8VXVIFkipwVR5CS019tp2vwPBaEG445Hev3E/+jxf4ehDbDVk7yGQWw5R9lsC+vvzbGbeFZXSvuK3vKXC97g3csccnRR'
        b'BN3g3SjoN3kjBTuJz8c2xAmJjCcsPwvfUQoF2EM8SmXj+CyGzsgzGht5xhIjT61Le2wI6hzdnD1m5DkJG3nGECNPnvOQte8gPxyl8CKbU8ZSEnBKIoMkaV8Lw69FGFqL'
        b'6lK+N0YdGKGYlrmMDnkvb5T8GnZwPpTa5ajxiFF5xPSbqDySNR4ZKo8MtUeW2iV72M2zK07jFafyiuv3VXklabymq7ymq70y1W5ZqL+u2YyHFEOQwxhl4bKecBsZFqLH'
        b'FA4fGuGUEZLypJYVZ+E6QqHg+2UM1IgOL5WF2xMm3yJohELBQ8RGuT/EUdpuEe+B4a6J6aBdrmd7OZSFExO2+YJTAYw8abPJI448BU2OlblUkv9O7cZE62N29jN/crC7'
        b'mvZqZMyfujIPF//IhkdyMg5diQ5/eXHnyb9+PPT1Rl/ZcMdflx/U5P6+sPZU0KXvzz1w+Ixrsm+pqeTuTKH72T+6r39vec+qb6s/u6b0+hPvxNd2aU8OlFt/8I73T+wH'
        b'1VX9Tx5FuKneezvu/r6wV1TV05I/it9tf2v3N9k+Fwo+PRNiIU0uOKQ6Yn/lpN13/u+kmGvqLb8RbuW324TbFrQs/vbwVMsd7979mLO59z07S46jDT/66rL5NcGDX3Hl'
        b'b6bO3Obc/8GJloLX3vfqyy0bHmBNff8Ac/j3Nnmvln/k7fC40mFLftybUx5/0OrXf9rjzDsWD88vKrGNmlzyVwf1odWPzZZ6rH3rtUuPa7zUr15e4nlubu+bV8Q+rt+b'
        b'vHZ84aeNX6+Gbstmus2K/ebxd6ve+bjk6cs7L29p++bYv6hvf8j6q8gqgEV/iTgId8TDA4iJ3IkYQUYsBff4agElN4G7sXrTBW90Xuk/oLjMJ7CX4CDosqU/iCgRJz3O'
        b'QRb5IgLOxQR4T1yKxr8Y/F8s/P9gq/Cmz8ZE8t8ze8aE3QMbz9fUiStKSmQRaAsn52UyotJ/ofMyirKwG2EbmTgMWdm2ROxc3u6xc3WHXBGhEHdNOrxSmX94Xa93j6zf'
        b'o7exP7+36XLIy6n3bWGGOiLnE4FTe0S7uGPSYRNFFmK8ehwQ7zgwJU/lkDcwq3CgaLZq1hy1w5xP7IUK27baAWtv7MXoBcaIKWXLb0lqtWtOfhJlY+L9hMKBv5+J6AmF'
        b'ghEcPClkTDFxapn9iEJ/nqxleJs4tds/otCfkTwGZWr9hCljmwQ9ocbCxyREC9bUeoQ8HGkwoQS+SjOVQ2Sz+ROusYngib2MZeKCsqPwMQlHFhmRwmaRYsbCh3SICxsl'
        b'D38YSRIwTDIZQ7buJ80HROlq4XS1bcaAeQZ93u5Ickm1o16x46X6az+RuA4z0Vj/Z59E/m/oBS+Y0vFf2553zGDyIIEToRGK5vjCGQxr/NHFIPgtVg74OnGOO5m6ZZbE'
        b'ZUnZmg6W/AJKWjp7v2RXpilI5KeuW/kXb1PPWLafS61ivtXAS5EfZf2w2ObO9dE7WRuFLxyek2bXWNxX9s5W0eTHLrGyvx+/Vh2gbkt0yF13s+PSZLupnZwdO5+WXPum'
        b'6tzK2h+Xe/We2P99ytGF3x+/+e5XLcd/4Hs3DP0hoqhslujmWyFW78/8ZKtCIS7Nf7nrNWs3hteu8Jf5kW+rSjc0233k3/uq5SqXPbl/dl7J7p1zK+zamaZ1rP6vPGck'
        b'XkWcCMExB8dBP77Qz8Af6ndlG1ECcNkM9DGhEt5toCVtF8F2cD01PHuGCPbijPjebwNvs0BXOrhJexgXGhOwnBezTYECbUpYdmpEWdqy3OC2ReSjsrwObMzOzA3MNQLd'
        b'lhSXzTTGSEqPCEzdKbh3CdwZiljnQEYBBU80wq3kgRW8KwrK4lCwfR0jG4WI89hD2z21wxugE0OW70GVYYgdMVhvFsBEXM4uHs1G3Q5eKjd4DvaDPtNMJugBm2U0tNS1'
        b'INRbdOotqhRpBYiWcAcrbxk8Q+MGn8oHN/PAXj1mPug0W0qKdofX4QbMCgdnaI38PTLNeUzEJGy3IxnmOmJQKvS8XvvcZ5YpuMwEV2bC/fQu3lwNd6EcfeagefnSRnh5'
        b'qTkKu8EVBuUAX2SBXeD2NNLPjJnwbDbBx8JdIXLRvWbgEBMedwddpCirStCNSuqCfeDF0Gx0FKAOwxfxXBhRzt5ssIkHFAH+v/os+P/l0WCw6P3JIZGo++8Xjolx9k04'
        b'IGcEvmo/RRvAQyeKwxu04Gss3NAF6UiT2sJ/ffog23RbzoacARuPk7EfsIM/Zlugf5+y3T9n+33OFn3K9nrCnWfNQVvqWPiYhCNNQsqcv36GgXjKfZhVI6kdZmM9/WFO'
        b'Q2N9jWSYXSOVNwyzsfB1mF1Xjx6z5A2yYU7ZigaJfJhdVldXM8yS1jYMcyrR2Yb+yLAaHfYwW9/YMMwqr5YNs+pkFcNcxGA0SFBkibh+mLVSWj/MEcvLpdJhVrWkCWVB'
        b'xZtK5Trj9mFufWNZjbR82IiGAZAPm8mrpZUNJRKZrE42bFEvlsklJVJ5Hda8HrZorC2vFktrJRUlkqbyYZOSErkEtb6kZJhLazaPnQFyLEEv/aX/hMIJc4AdqskxL/P0'
        b'6VP88duGwahg4d13fDhKwt+yIeND62VjbpKAellgluTF+tG4Eivzl1eHDFuXlGh/a28MPzpp48J6cflicZVEC5UgrpBU5AUYE+Zq2KikRFxTg4480nbMgw2bovGUNciX'
        b'Sxuqh7k1deXiGvmw+SysV71EkobHUiZmaqefJgT6ojJlSV1FY40kQVbFpE1x5DkoGGExGIxR1DX2iCVlZrHe6Ht2jTWDP1LsQZnYaIydVcbO7VkaYz+Vsd9AcMLLvtBf'
        b'HZw1aGw9ZGo/4BCpNo0aYEcNUdYtgg8pJ1Lb/wNXIVCi'
    ))))
