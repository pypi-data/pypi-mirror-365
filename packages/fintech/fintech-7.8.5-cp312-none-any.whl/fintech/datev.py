
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
        b'eJzsvQlcVNfZMH5nZd+HffEi6wAz7LsbiMgOCm6ogYEZYHQYcBZU3OM2igtIjOASIBoFlwQ1Km6JOadtkr5JCmLqSJI2adqv9W2bamKSNn3b/s85d2aYgcHEtu/7fv/f'
        b'7yPxzrnPWe5zznnOs53tc8rsj2P4/WoVehyhpFQlVU9VsqSsHVQlW8ZZZUdN+pOyz7GYkMpOymFTMt45Q0wLpbZbzkYQvpRrTPM8C73byEx5WNR6nl29kP/dJvucrIp5'
        b'i+nGJqlWIaOb6mhNg4wuW69paFLSuXKlRlbbQDdLaldL6mVie/uKBrnamFYqq5MrZWq6Tqus1ciblGpaopTStQqJWi1T22ua6FqVTKKR0cwHpBKNhJatq22QKOtldJ1c'
        b'IVOL7WsDzGoUiP454EZ4Dz12U7tZu9m7Obu5u3m7+bttdtvuttttv9tht+Nup93Ou112u+522+2+22O3YLfnbq/d3rt9dvvu9tvtvzvgCKXz13nr3HW2Ohudk46rc9HZ'
        b'6zx0jjo7naeO0nF0rjqBjqdz1vnqvHQOOh8dX8fWsXR+ugCdW10ganLbTYFsao+/sTk3BdlRbGpjoPEdhYOMYRa1OXBzUDkVYgW6llrHWUatZaFmZpfUmnedH/rngSvK'
        b'Jb29nhLalyhsUbhnLYfCsLiWuqSTSi6lDUMv7mAneBW2wT2lRQugDu4vFcL9+YvKRHwqYh4X7K+Ab9qBl4UsLS4V3Ia7Zqvzi+EBuK8Y7stWsyj7fDYYlC0TsrUClCB6'
        b'GdxemB+Tz6O4XJZzKuhxg8e0uOHhIXABvICjRHAP3KfNLuZRznAvpwS+CU6jzEEoDQ+86Aba4N6YZoTOvnxwEJziUfbgMhu8Dg9FaUMwAsdgNw+lueQIdGvXaOHlNY5r'
        b'tCzKG5wNhQc5YB/YkYNQxSlXZcwDbeBgbKEoSg06McLwIAbYUP6hXLAd3gKv17LMGs3f2GiH0OOw327UcKgvuagnKdSDNqi37VA/O6B+dkJ964J62Q3RgAfqa0/Uz96o'
        b'n31RH/vrAur8SR+jAbHHxtTHbNLHLLM+Zpv1Jmsz29DHE6CmPm6Y2Mfek/o4kOnjozl8ypGas4hLVzsuz2qmmI6vxB1/p9GZqnY8xq9hgDPqbClXKq6YVV2t+H3ORgb4'
        b'KzcuZUutq7KdU13UuDyFGqAU9njMu/lwn7hTZX6szyK+ZF+N/+vaIpYCc417Ud2sQX9PJ2pOdcLHqiflP6MI+HblVy4vrF44jV32KevvSwNbC6gxShuLO/A4OBCOurct'
        b'dkFkJNwbmyeCe8FARWRBMTwYI84XFRSzKCU8luViNxM8D7ZadJGDsc4q3EUOhi7iWXQPhTuozsHUBdz/vi6wmdQFjiUq3IZkJICTa+H+8tnVC0WL2RSbQ8ETc5q07ijC'
        b'Fp4B58rZcBs4TKEvhmxZqsWlzAAdsKd8IRvcmk5RDdS8jfC81g3B+Z5usJMDO+EZioqlYlM1pBB4XAP3w04WvJRAUSJKFFGl9cEffRO+CN4sRz/7ihfA/TyKvYEVwIbt'
        b'2nAUqVhF43E1E5yOLkSjYU/RgkgwEJNHhroYDvBQe78Gzmg9cfEvoyG3F1zmg10NCDWE3GvgTfnce5c56vfxQP3zhmM/nXli256+zsudq5NDOD6aNYfnLHN0tF3gvUt/'
        b'wtExvsjR8YrjlX3J+5wUwn0nViQ7psy5HjSr1y4ged+Jj89102fbQsu7Vvlc7vKNm2OvtncoWuTp/w6/35dflqj/rO4RNW9otY9EvPWcZudZ6e+lBbXPn3sxa9H+D5U/'
        b'F6R0tQ7J08tGuz4Lt9tWxK5p2SH3UTbs/s+ah9J5qu2Rwz87v/QPsreH37y1I1D8H6ykNhuJd+QGfkX1H8JzvXYJPogpKUp0i/d4784DNnXtk8wLWrGQ9wQzH7jXZ0Eh'
        b'3B8N9xeLCjADg6fAHnc4xIG7wWDwE9y6WzTwQnSBCOryi4rrS3iUA7jIhieKa54QBveqDOiixcKCaMzfinnwsIhygVs5TaglTz6ZhjvnANwGTzrgNteKohDts6lg2OsG'
        b'b3AQa3wx9IkvSpMRCW/Bthi4F/13EO5DozadBS6CN1RCpzF2pFDlitL8kw+1E3rQ9Nbxv++8ZtSpmlplSiQuiSAWIyEqa5k15qSSKaUyVZVKVtukkrZavrJxWV+jx5+3'
        b'Uo83sigvv67wzhW63I8Dwnrrfh4g6rBtZ7Un6z182mfq6entuV3xh/IfeE7r5fWq73lG6+nwfs/XAgcCB9VDOaPCrBE6a2KSB3RI77yT9mbgfl7/2uGI1HueaYa4+3TC'
        b'CJ0wmDjEGaVnmOfX3POMQWn65vbzThacdDEvg9vfwJShp8POOPc597eM0ilMgl/7hQyHJl/nDi266TASOnfUL2dYkPMokAoUPwqiBN5H0jrSunJHPUKGHUO+wiNfhYe+'
        b'0HmMz7TImE1VlUqrrKoac6iqqlXIJEptM4L8k93kjB7VFv2kwnxAhYf9hK6YjdOno8dftlLfbmCxWIJvKPT4zNm7bfVWh0dsHkvwwMG9Lf0zrsuOYr2tywNbjz8/5lE8'
        b'V+Pbd2oiMvhR1FmHZI4FdzOpjNWY2fKOUDKsMCJ1Ucqq5KB/XDlVyUO/fCm70kZqq6PqWFLODrtKJsTdYVtpR0I8FLJHbJmlY9dxpHz05kC0JC56s0FvjuuxBmM3xl9I'
        b'qlRC2raWY4YJ18hn6zAmLEZzO4JLpEiZmNUjBXWPSUHdxCWsnmPG6rlmTJ2zmWtg9ROgU2tUnEmsnstI2ydCru0ZDuo3JC4vTauk5Avi97HVK1HM8Q0tx34640RfZ3ob'
        b'y0MT8h+X8tjv+oTTbekvuYVXOix8//mBjLbA8vO7JMkVVfa1nnmxIS23hY7J+xbSy7uqp3fTQStkEeUdrmURqV6pCW8pqqX93OwPvKhfz3Db4ccW8p9gzdY1CLRFIwWH'
        b'0W6i+ZQLOM0B51e2gl3aJ1ih8ZWA2+MJOKArm3KM4djA1+DrJL4B6BDTaytCGh/YBvYI+ZQt2MteB6+DQcLxEBca2oKFBjy3uTAfXEDiKI3tG7ua8KpWeKsOtJWCY+BN'
        b'pNZxKR48zoI34E3qCVZOIsHz9tGivPyYOngFcVNb+Dob7IhZL+RNTfk8I4MiBD9mW1UlV8o1VVWtLgxtiI0AwoKqGRb0SMOmYuJemzkwc8h7JDprxDWynfuCY9cqvcDn'
        b'SGFH4X1B2IggrHfVqCB+MGtEkNzO0gdN71ndvbp/en98VxNK66APnIZ+7B94eBvy9HI/FIQ94lACH5WHabTzx7hqmaJujIsNjTGbFplKjWwSFZaWKi9TFfh48Fbj4csM'
        b'2mDcThPRX45TJqHHX7dS36jZLFbwM4zYrzDZvcAPpU45xHJq2dbGSY1pnDCjpI5NxgjbQh3i2FkoO+bjBY0G9maOYYxMgJrGyI6JY8T0ebMxoo3CRNS2GvQ7IHWlDZFh'
        b'Wyw8WJ6HgvszMNUtKCP60WzYx3dzs5O7J/lz1LNQnmMf7T720yQ0evo649H4eSHe6/HhOLgO6RKOi/xaFI6O53yD/ys8t1fsVbRy2R+6ak40r3zL8bgvdUFt7/vbmUIu'
        b'oV7w2np420DeDGlXNLDXRcx5QqNICTi6GF5GsvogPCgWNRsEst9mNwcu2AlPrmPovwN0YxrPp3zGKXwTPPaE6GDb4Lm4wlIRS5xEsVtYWeEZQrYZNeOuMZIykgv1Mo1c'
        b'I2tE1OxuIgcTjBB0ioGgczDldWl6NnRvGPGI+tgvbDg8Y6hiJDxr1C97WJCt9/Y/0trRemRzx+Ze6ah39LBrtBmZ8lTT8Qe5SkmjbCJx8ghxmmgzBtOmFWRqjeT53Vbq'
        b'67kcFsvnWcnzEH869bKDiPO/zMYnaexTk+hheA3cmkijJgINtDWQKOUid48fpAiJvnv/BsPgrZCokUD3v/uTkvDeWV5Fm04gDfjSoW2XedTf++z5u5cKOYQBwytqeNFI'
        b'or7gqJEBX4O6J8Te3Q5PwF0mOk2JNKNUTKcXYT/htqmzefNcMaGOkynohy8JORN5LIdQ5ThZqq2QpdqCLOMNZFnyPWQZghjvEfsO+66ku660OeMkFKkS4Q/yWiQK7SS6'
        b'nMg0kywJ04ROA2XGN4sRYU57BsJUYV+HdX5JCJJj4pfYoKTquP8TPJM3iSB5JVrcUvBVnwzsLKmAOpFIvCCvYBHUlZaDTjFjsuUh603MojTwth1/Ok1IGBxNsncAL8Fj'
        b'UxGxgYSLNsj39IxRainKc2PJkWM/TSB23PXOi53yZA/OJZ2PQH0kLmFOlv3nqyJv7rnYObIzePGBbX0v9u3q6wxr28PiIEpP/Mb28CDQJn4YV3ExPo5+r5r1UArvdf94'
        b'j/DndteOdfQd2pYYSP31r26rLjkYzCtwGpyHt4nxU7nUaP4wtg+8HP4EO5dKN4BzhXGIzs0YNnsdaAPXCcNewtUYxwG4USaeMBBeySI6SRM8CbvQOHCqNx8JL8IdTzC5'
        b'pYkDoqPgMayVmFSSeL/vVUlMOvgYX9uMTaRWJwNxMq9kmCxhhsnjpRzKZ3pvaD/3nrfoY2xXzB71mzMsmPNRAN2eg3h3b9KZzL7Mu97ij4OEw1Gz7ghGouaNBuUO++Q+'
        b'4lGBwY/4lJsnHkb3XYNHXIN7Qz90jTAbTDbMYMKsYcIoMkPahjLweaPpMBMPKEucG6lxJv/tkmdk8sxYMnfNWOoeHOKaIb4zA2PHrhjOv80VM0k/n8zYOSXyskdaDiHz'
        b'b91fxZw6eGfwiQ5E6q90ihC/Pl+3Y3jReeymmJNc1LXq0tKLv9t+V+x48ayjY/yclVf2fffwSpH+j+/UvC04J9nxYMV/rIAVsAwqONJv+y/HUZ/8tJKzdkkcp96P2qd1'
        b'W/7RB0jlwDSMNOVrsnGVA97aTIi4GV4k+kRDBNuMScfDXqww3wAnmbw7wRV4CFn/+XC/iE/xn4Md8CA7hAcuEdKG5+EucAor40ZN3EHO9l0G2hBR/ACzEhMFTZup18ho'
        b'VWtUiPE7j3Na/G6hXDdwKP9pXV59Ib3SM6v7Vo9OTxjxTWjn60MizmT0ZdwPSRwJSfx5SHJHYXtOV5jeJ6DHodvhvo9wxEfYHzrqE9uehYxtxsZG1B2a8phP+YT1Lh71'
        b'jhl2jZksI6akaCIhzAg6BxP0BLy1RopGxvA39Yii3Z+FosUYDXbJw78jqhY6YdsDa1DIpLevqmLmI1DYsapqjVaiYGIYiWZbiwZTfZNq/ZitwSRQq0IJq6iTyxRSNbEA'
        b'iKpFxBoZigT97+M6ZpY/ppxWg31cjuOTce/soD718NZhlqLL03v7ooeXn26+3tNbl/s1l+8U/sSV4xTzxJ7jJPzGnu8U+a0rz0lEmlyLqQkpFtfhVYeCYnggtgAeK2NR'
        b'to7sarh9zST5hP++WoiHNWuCE4BdyZVypFwp7zi7ksemllCDlJS/yoma9Ce1Mc4LGX8rbdbbMmb/PCWS7uu/E+TIauSaJpVMGVuokkmZ4ENX0isP8aj+zn2xTNWqrVc3'
        b'S7Tq2gaJQkYnoiiM4XeORTJNq0ZG56rkas0AWzUPAR/+BBHy191IUS9sUmqaMktQp9GRWVKVTK1GXabUrG+mFyk1MpVS1tAoUwozzV7U9bJ69NRIlFKr+ZQSDbylUojp'
        b'MtTlTSjv4iaV8oeks1bYaplcKaOzlPWSGpkw0yIus1Craq2RtcrktQ1KrbI+c94iURFGCv0uKteI8qUlKnFmlhI1mCyzAilJitis1RKpmJ6vkkhRUTKFGqtOCvJdpbql'
        b'SYVKbjV+Q6XJLNeoJLBHllnWpNbUSWobSEAhk2taJQ2KzFKUgnwOtbwa/bZqzbIbX2rWYuywV4o2IIJAYrpSq0YfVpghT8dPGZOQWShTKlvFdGGTCpXd3IRKU7ZKyHdk'
        b'hu/J6PnwlkIjr6dbmpSTYDVydWaFTCGrQ3HZMmT6rMblRhpAQmMcPV+GaAeeqtOocS1xk05OTc8vEmbOExVL5ArzWAYizMxn6ERjHmeECTNzJevMI9CrMLMcMQWEpMw8'
        b'wggTZmZLlKuNTY7aCL9athqGrMY0LCrRNqICEKgInsJuwNW41ZjmR8D87KwSHCeTqeoQ60HB8iX5uRWiuU2obwyNT8aCXNmAaA2XY2j2PIm2WSPC30E8rEZs+KYhbNHu'
        b'1uC47S0qkTCpEgmTK5FgrRIJTCUSxiuRYF6JBCuVSJiqEglmyCZMUYmEqSuROKkSiZMrkWitEolMJRLHK5FoXolEK5VInKoSiWbIJk5RicSpK5E0qRJJkyuRZK0SSUwl'
        b'ksYrkWReiSQrlUiaqhJJZsgmTVGJpKkrkTypEsmTK5FsrRLJTCWSxyuRbF6JZCuVSJ6qEslmyCZPUYlki0qMD0Q0nlRyWZ2E4Y/zVVrYU9ekakSMuVCLWZ2S1AFxYxky'
        b'jo0vzSrEkBH3U6qbVbLahmbEr5UIjnixRiXT4BQovkYmUdWghkKvOXKsgMhEjLjL0qqxQGlFSkjmEniqQYXaTa0mH8Bcj5GxCnmjXENHGkSvMLMSNTdOV4MilfU4XS48'
        b'pVDI65GM0tByJV0hQXLRLEM56QMcU0YmkswLGxfjokqEBWIYkTi7RYQhP4oKm5whYeoMCVYzJNLZKq0GRU/OR+KTpi4wyWqByVNnSCYZiiWMXCZtjvQSpJ8QmEa2TmMK'
        b'IE5kCiaaJ1WbkjEdkS1D4rjeDBCWWSlXot7A/U++g6NaEQiLXsSlLV4TLF8R+5GoNUjaqeR1Gkw1dZIGhD9KpJRKEDLKGkS2ph7XqOCpekRE+UqpvEVM5zLyw/wtweIt'
        b'0eItyeIt2eItxeIt1eItzeIt3fLrcZavltjEW6ITb4lPvCVC8clW1BQ6cqGhVdUGRUM4rhhZizToStaijOrTVHEmVmYlvtT617DeZQ1uoYpNXYenxE+lnT1L4oSpv2yh'
        b'p/2QZIhVWktmIQJSJomAlMkiIMWaCEhhREDKODdOMRcBKVZEQMpUIiDFjNWnTCECUqaWY6mTKpE6uRKp1iqRylQidbwSqeaVSLVSidSpKpFqhmzqFJVInboSaZMqkTa5'
        b'EmnWKpHGVCJtvBJp5pVIs1KJtKkqkWaGbNoUlUibuhLpkyqRPrkS6dYqkc5UIn28EunmlUi3Uon0qSqRboZs+hSVSJ+6EohBTrIV4qwYC3FWrYU4g7kQZ6amxFkYDHHW'
        b'LIa4KU2GOHPbIG4qoyHOoj4GFHNVskapej3iMo2Ib6ubFC1Ik8gsn1eWJSLSSqNWyeqQEFRimWcVnGAdnGgdnGQdnGwdnGIdnGodnGYdnD5FdeIwQ1+thLea6zQyNV1a'
        b'VlpuUOCwMFc3y5A9zCiT48LcDGoU32ag+bIaeAtL+glqQz0DN2gNxrcEi7fEzDKDc8Us8yS3S/xkUMJkEDJzFNgolmiwXkqXa1FxkkYZEqMSjVaN1VqmNnSjRKlF4oWu'
        b'lzFkisShNTeA0CyLHAt3uZRk+97EVsq3IpSslz05IXExjbcOjZRv2qDykqasw/GGRmbCCWZhbBOOe6rGWJklA7aqXOzjm48feZRhokyVjx8F2I/IUzcr5BpVIfaEsRj3'
        b'IPahGVyDxcQ1yPjQNuG4TKNrUIhdg766vEd8yitW7xn52Ibr46zL+9Ke8vJ/xI1zm8v6toZFuQj2yNrntq36qp6V6OW3J3fcQbhJBDrVeD3cnhgwAF+N5VK2KezNMnj8'
        b'f9BB2CC0G7PPqq1t0qIKKuvHnLMRFTGGjKRZpnjoybgHsQv5O78cRFeNSFnBLmGaMaXQqJAjXoaS4DWpY1ysVKkqUPDrWwiwqJHRkZoalDK6vEmhiM1DTE4pKmzFLpvx'
        b'13G2mbmksJJmsmHXHGbIarlaywBwnPk7M4znY08iYzIwH8peJCqvbVDAW4icFEjNMX/NzJYpZPVSXBEmaPDjjIcTDCZXprEliAmBdUyZgVsY7UCa0bMM1uS438tgRxLt'
        b'H1uQKDEarxpiaRhKIJ9TyFECEpIr65poEZ2l0hhRMUDylTjnBCBOlmAtWcKkZInWkiVOSpZkLVnSpGTJ1pIlT0qWYi1ZyqRkqdaSpU5KlmYtGVJbSssr4hGgkOkYrD7L'
        b'CDBhEhC90MUyxIKNzl1aK6bHnbsIyNCy0dsqprEJYDTkGS/ueDfSRdFFmbla5WqyYUKmqkc8rxXzKQzPXkQnpTOSu86YBHuZrcENdMNEWSkws5JYGLjiqkYJjjSRiLUY'
        b'E6lMlS3hadmsRzIk9JRs1iMZknpKNuuRDIk9JZv1SIbknpLNeiRDgk/JZj2SIcmnZLMeibOlPy2b9UjS3XFP7W/rsSTj0wllakqJfyqpTBFLMj6VWKaIJRmfSi5TxJKM'
        b'TyWYKWJJxqeSzBSxJONTiWaKWJLxqWQzRSzJ+FTCmSKWjPinUg6KLdfAW7Wrkehai4Svhui6a2VytSwzF4n4ce6H2KFEqZBgd6V6laRBhUqtl6EUShnWs8b9lwbJiRle'
        b'lrYOe9pMTM4oS1EU5rzjApmOzFK2Mjo2niJEzLhYrkGiUSZFGohEMyF6Ah+enHmck0+MUyngVbVBTbCIySMTRnUapJWYLDUiSURE37FqVhhqapDmSPQjSYO18jqijzdi'
        b'Aa+RyVGzaEyu53ykPGvkdfLVEnPuX0ksS5NL2lzNYOxRs6lJczUpV8YYKzJ5DY4qQr2G59rUjGYztaJm7m5GeKMvSxTaxtWyBqNvnAhBosXh5TYlqqXWtWK8wLbVTHG8'
        b'hePTjJpxiJlmnKr3pC01Yx+3Gd8mjOvFqf7jajGeyoeXwOtwm7qoBB6IhfvBDgHZ7lFoQ3nWcB3BHnDbQj12NKrHfDZSjwWW6jFRiPnonwP+J2Wjpwf+h1Xm87xzNkxW'
        b'O/SflNbxdE46D7Jk3s64KKaSi3dlSm13UFK78/bnDEvbKvkE6oCgjmZQGwJ1QlBnM6gtgbogqKsZ1I5A3RDU3QxqT6AeCCowgzoQqCeCeplBHTG+dWyp9w7bSieLenp8'
        b'zz+78z7n7M1qHqxjG+rOlfqa1d3ZsvXQP3v0j1VnbEUbU8iydL9zdsbSpdN1zHI/vKXPFX3BRupv9gUXaQiK5+lsyaY/dxIfsMOu0hXB3FDdAlHd3ExYeJwPMpouhm2D'
        b'zjqXOp502g5bU4nu6/l2O4ShY7Y5eJvN3PLF38Xa02Z/RjDN8ENmq6tFigGeqgwTOLa2HuJFMarncAivuSV2jdDxIUbiIe6Hh3ip53hyVb0xuQqvo1RV4yS4pR/ibXUP'
        b'MaUKbcbsJdIWxGJVVXLpmF0tYnRKDQ46S5ixVKVAmqqmYcy2Vot4gLJ2/ZgtXtIulygMq14c6uRIOa1qRPynoaTW1mwo4E+RJVqbKeNqS/P9t2QrHwt1NldngxqP2cjH'
        b'r7Mnq8cQme6xN60esyOrx2zNVo/Zma0Ts91sZ1g9NgFqvgrz607UOBYti//ymarIW2VqskvZ1B9yshakViaelGUSIAPZV5JGerwZMwz7kxEPxR40wwZoQ3tKlJpJJeC/'
        b'yGzE+jRGxisU01k4P2KStTRZQUtrm2kkKlJpqbxerlFPxsuAhqkHrWPBRFvHwDRP9D04JH8fDpakk0EXkV+MwvzYImOsATG1dVywYMUiDQlEMV3RgIQcGiEyWq2tUcik'
        b'9ag+P6gUZhEOY42jkmgJKgK9M/jTiiYkcFViOl9DN2qRTVYjs1qKxFD5GplmrQzPk9ORUlmdRKvQCMn29LSp+8IwZDLouYYQXYsdrZGm6VkzB61wqlKMwy3DSK1qU2fi'
        b'3fBNKjqSWeyzGt5StcoUUxZkWK2WQcxJrHqhYhgaMXCfSFm9mE6Oj4uhU+PjpizGbLxn0Ln4hSYvuLg6uRKNGoQjvV4mQYhFKWVr8VxxS4o4SRwfJZzcVN+zONqR2XR1'
        b'luMa18qZQ1HN1TG3Ed/T4kV1W+Ah0AnbisH5MqjLh/sLYzduhnvK8LLpvCIhbIspEYG98GDRgjxwIa+kuDi/mIW3d/Q6NsGz1aTYKjsnxV9YcRRVVq1Yl+VBabMQEG7H'
        b'C5TNygXnwZuFscaS4QG4pwjujwZ7Jha9Y70jXtF5lRT97Rq7or+xaLwsV5FEIYwjEBCcAIeT8XpO43bcPLEoqgBhHg13gVe5VMoKvnoOOEK2FJNSTtfYlIWyfCiKro65'
        b'3lLC1Ps5+Ao4aVFvA25QV++Hym2LwRjuEy42Qw5cVzmAS/D0cvn6A1VsdS8q5sqCzE0H451BnOO8P54a6KxoDhTfmXlDulXD4S99sJH6UXBrvrvdkr7cK4J5s3/599jN'
        b'P05trvbL2nsxUiDb+lfVjM//a1Nn5mca7pBjasTtd3Xf5qSE/fis4OTC8wUPjwqOcfqP/uZMkrj88J0XPu9RBv9jxfWHg9O/dnr3k8erXN1/80l4x+If/Y0/cu6T7Lnn'
        b'5c8FfLG3smXmkti/92fd44CHnE9BTODYW0JHsuMtApyBF0Fb7PieNsoljBMmr4NvxpJNtuKcJNBWWgSvwoNmnc6i/OB2bmvQMmar76FVTg6ozYXFZCF6Irgcy6Y8wW6u'
        b'LbgIL5PF5mGFC1Ex5r2bAQdRMV7BXAd4HLzB7C+6Bm7Da9GiyDz3ChGb4oOjbBG4DAYJIiGgYx7enoGKMXQr7lN38CoHtpWBl8mujYpl4Hq0WAj3wjdaYihUwHl2InxN'
        b'QjCgS+Ab8Bg8ANrwRmBTN/Ip9xYOuL0i4wkhoUPxTri6WBtdD24aUDVQAUXFwZ18MbjAeoK3f4PBfES7qFJtMVFinAzuhwejcTIaqbTX1TwnsAucIN+Gp1NQ0oMinJp4'
        b'gNG3RejL4AgH7oTnNzJbUy6kR+FvrwUXGWXYqAn7gSEuwnoHPC60/yf2v2JFYeLeV7KNzs0ojy33AY5QzFLlFhsqGO/9c9KHiNq591zpBx5eHequjM4tox4R/cF3PaI/'
        b'9gsdDssb9csfFuTrp0ejtC5MmvTOzaMe4f1ud/G+FpRm/qhf3rAgTx8sPBPUFzQaHI+SOqOk7Rq86wonNRWXOuqXNixI00+PelncX3M/OHUkOHU0OH1SBlPZuaN+84cF'
        b'8z+NSMZIhupDY/FvsD44BOfRh4S1cz+02D/jxKyNbsKPZvxYgx/4CASVGj+w3qXSUE9bPo097tWGP7NV1FO06kOcZQZ6/AM167elNixWLetrCj+fdWNxLz8O6eaZHIut'
        b'AiwjWw8gbH0jtYqa/FdOITWNVSJkjTlUjetSyNTDbUFMPdqwSXSGQtJYI5XMMquIEeTGMpIT1VVxP1B0N5BZAP2dQdAZCjYqRZFIgEpFTUrFeuEAa4wjbar9p/CuZ/C2'
        b'rzIpX5PRVu2ybHojxgKUhOygwxj3VB2tYvCdxuDLFGgF3X+lfV2qLBW0H46st2Xzxt8NjGfQFT5VxfuXEW9gELerMmpUPxxlP4v2fe7ocwzCvtkStcykoP3LCNYZETQq'
        b'az8cwUCURNWJExDEQqZU8v49bWhbZVADfziGNO51UxOuPLrSgOmUauS/B1PHKjNN84djG4I7fJxGxXcDxQYa/R5ddQqsTRuNqtHjMNuwz8m4w/rfu8vpB2xf5ZTIf/lq'
        b'AFuNNwBWnd6Jt0zjzXzMjlS8w6nMs2hoUQVrTRynnk8l2Xt+wv/xRxuEbHJiyRZwsdFMwidEjsv4hYuf4Aae9xy8hXf4n3Qrsirid3Kn3PFsU4X5SVVVq6uZfCEQIrTx'
        b'BjK8W67AjvLx70rqmdU9a9Q7aqB8UHA/PmskPmtUlD3inT3smj1pa7M1KcfsbMaSjSGGk5gYJn04nDW+QejrfLtn2yBEuEYHP5jqc4jhCO3HbAxcjdkFxFdrVDKZZsy2'
        b'uUmtwVbdGLdWrlk/ZsOkWT/Gb5EQR4pDLbItmxoZBwtHI6kf4zWhca2qdTDrZ2djP+/DRMa1flQZIjwnw2ZVW52Ljq2zx4Soc9VxdHY6mzpnQpAOiCCdTQTpSAjSwYwg'
        b'Hc1Iz2Gzo4EgJ0DNt919/QnPiuMkSypVI8sYm3dSWQ3mT+j/WsOaWVpGVif8AN8JseyJWS6hG7T1MjNvBWpXtRxZ+zSzqwo7HtQyjZguRSN0UjmYUTbieVV5Y3OTCjtZ'
        b'jNlqJUpkueOsyOpXyWo1ivV0zXqcYVIhkhaJXCHBnySGLl5xrRbjmsqxhxzxCUORBmcBLnNSGahorVqurCcYmYqho0iXR/2AFsk11LYBewMn4z4pfaRGoqpH35AaeTDO'
        b'T2Ofvxob3uo1Wty6NSpJ7WqZRi3M+OH+LIbaM+gsC2FOLyerHFZOlQ1/OYMmu56Wf+/epylLYQZXBl1OfunlhpW4U6Y3DsIMGs9YoK4ifpbl5itxp8yLh20GPRc96eWl'
        b'Ks3U6ZiBjZIyAfKNGDq/vFSUGJ+SQi/HsxRT5ma4QQa9OKtClJ9DLzdM/a+MXm6+s2vqj48zEexNYl5oXJD5foIpsyO2gxqzAQ0NNFzVtSp5s8YguTGd4vNNyNjKUqib'
        b'EP3KpFYdYYiccGosNxXkuEXS2WI6h/GGkSE6vVwjaWzE242V06f0i5HBgAgLIdBsGFpSOTnwUYKada0cyWfZOtTjhgE3uRz8V9KkkTHDhAx+maahSYo4Sb22EREawkWy'
        b'Gg1ANGhkqHVqZXQTUnuslsNUCQ8a4uZTM9WUq81QEtO5iKkZGZLVUsyHHXYKIlLHx1nWKlCFmZMs1TLrOasNh1k21RLMmUnRGQ0aTbM6IzZ27dq1zBFdYqksVqpUyNY1'
        b'NcYyVkGspLk5Vo46f524QdOoCIk1FhEbHxeXmJAQH5sTnxYXn5QUl5SWmBQfl5yamD6ruuqZXXDuJVqawgdBJq5XFwkLROISvF05GgzEUPACbKdCy3kNbuAGc0jduUx4'
        b'LRGn7lTGU/HwtQzixlLE8ijbgFf51JxqxbaiKkqLZ+bAG0rPQpOWcaZ2AdTho9gKRAvx2QULI/HG/yVQh3+Q/gEOgdfs4OHp4HlmM+trnnPgZXgAdlQSl4YNxYPdbEee'
        b'Czngcjm8CTrgZTHcX5iPD0eYB86govE5b2xqGniFC29Egz7iS5Otgxfh5UK4r3gRbG9G1UsKMqtgGdSVoHz7Chc1o0dpUQE8zKXgXvC8AzwF+nPJAZnwMOypcADXfcXC'
        b'AnAL9NhTdgVs2AN2ZhJE1ynhQXg5H2VnURzQDfvBERbYCvurmLnFDg4YcIC6WDHcg745WxQDBgrgPqhjUfR8HjfPXYudRuAwfAV2w8uxUSyKnQfOwkFWCkKZNO3caTaU'
        b'48Y/2lB0tWLhyuUUg9P5aaBb7YRQu8J82TY9ewV7fg7cS74KdqbBXhzt5CSGHdPK4ZUieDEaHuJQ3us54HyMjRZr6O40bHMQo/yo3fJxi3AoT3E0vM51cXaXb3r7Dks9'
        b'hFJlpSxtHH7f+fk4R+rTltrtrOeXbPI6OKvAw+kXw9vd8/Zdm7X1cfC6/MLgdV2FVzf9/u83bp9z8amG29r4v0o4en1arw048buH7xTN0snqo65IM391afPD3yR59ORe'
        b'7fxGxW04d2z5SbuPPvjHN2+0X/j409P++rZbUR6vnN0fWZ6+oOw3L684rLNf9Inyenivarbsze7aCvffDd1do337XFZv65x3H7ydnhp84Ot1lVtOC//+3mtNWes8fzEn'
        b'bQvrTx9FCwt9hHyyA99DuXKCb3FpehinrgTuId42+AJ4pdhEpBaetmi4C76eyEO9e62OKNfgBDy0wczJiD2Mc8TYx4golDjZXKEuzEz9hr2g3czJ1scjGM1vEkaXiPLz'
        b'iwtj4H4hi/JKWwlvcRM2gHbmyIDXwe3iQjAEL8VE5iFcUN+Cc+z10fC80PVfOSvQqmMOPyzOpTMdJWAvkUqrGDWv1cOkdo8Dicr/O4PKX2RP+dG9vF7NmU19m0Z9k9v5'
        b'eg/frtgRj6hhjwS9OL49t2v2iCCa8cyldm4c9Qjt1dyPyBiJyBhaMBIx667HLOJIm3unfiSseNSvZFhQop8ubOe3r+1w0QuTUGDziGu4flZ2O3/YO2PENVMfGoWA60ew'
        b'ly0ShVo6nPXCeGM6OhSFtB1ODzx89ZHiftUgqx+fPZg+IgjTixIHswaz+yvR+6wRQZTey/eul7BrRTtH7yo44tzhfN9VOOIq7A/pV426Jtx3TR9xTR8K/9A1y8xqcWOs'
        b'llco49Le0/hxBj/68WMAP87iB9a6Vefx48IUdo5ZZ+B2rx7/o8cPKVFdw9aPtW4QYgMoG8X+46/YsWeHXXrfEsfe42d27+FZ9DP8VOqaQxabI7Qbc5TiRdAGNXHMiVH+'
        b'ja98SSP5xWenycbsDOtUamVjDlhVQwoyXsXKNIKp/rX2ZnLI1SiHDmCLyMaaRXSEnPyKrB88hcwiB/Ta6dyQdYQP8CWHNde5EpvI3sImciA2kb2ZTeRgZv3Yb3Yw2EQT'
        b'oBaTyQdtnm4TSUwLUWjm3MYfoPnPw9vJmNQ0Uj9QJyKlHqlUEvPjrrHaFUPXq5q0zSgWWRuSyeK8qbFGrpQYFbwopPtFEc2EUUywS8m0fh4jaPKDTCoJ+0X+nxH3/2cj'
        b'znyIZuCOYiAmB+33GHMWY5rJz4CMBVjVaJd/zwr4KT/H8AzmOwY2YYAxRoGyCbvvVETtV1pX5tc2Ya1b3ihRTGE2LH/KHgBkjFnfBTAlxpi7MfjWNDWtxvhiiJguNlCX'
        b'hLzTTTWrUMfTTdYtEEQgyIhMS4mLN3hQMSEgCxgXt3x8f8CUSJiYawa9SK2VKBRkZCDCaWmS15pG43Kz7QVPtaMNzNmyG8hW5uXmWxC+19LF2SdYuxYL3f8vMFazZWtl'
        b'9YZliv/PYP2/wGBNTIlLSEuLS0xMSkxOTElJjrdqsOK/p1ux/ElWLM0sJOE8hw+7p+jhwGbH10rXU9oUolPDl2BbYX4x3BuTX1QCrgIdo/AvsGaJbgG37ZLg0fmMpXU2'
        b'Htlj2BDFVmhygtEOBeeIjQtfnA2uFooLipHCn280I1Cp8NIGKyZuG2yzA2eQzbFVi895Ll3rpS4tLoU3wA7DCX/4G0tgO8pxEOqQUWqPTDhUKHq/Xr4CHAdHwUk7CpyD'
        b'LzqUeNQQq70QPg964cEmdQHcn19cWoiPBozjUj7ZHLgPvAqvk0SzQZ9AHYWveOhXRGL7RpwPLkSyqGn1PB7YBQ+TqxqC18PrDvAaOLDQFu4XlQDdGmSrsin3RA7oy7Qj'
        b'x82DbUL4KmqM8eUtyG4EVxaWiYrgTT4VD9p467LXMt6EXTbgrAGp/BhUbI8QH14vgCc58Ca8vZl0VoYjc3lF9XJ1UeicUIqcmp8CLsGtDmvAG6iPK6gKeALu0eLTsVKQ'
        b'aX3TATcSas4OeC2vKA++WICPzIdXsBHfBs6htyJ4IA9bsit8beeDw7GkRDVqiB6E9gm8njKfyp8FrpNz+MWoJ15IrAa7UTieinerI6nhC27wOOy0BXs45Hj+JfCc4s//'
        b'+Mc/fpbFUNacJVpF5epEZv1OW7MNXhHsOqdS5vhehB2lxbp4wCZ8Ri0yqwkxQF1ezGJ8C0dswUxwaxGiiTy4rzxSiCgjz3TthhBcXYgP7ecrnVZuAG9osZEArrrBi+Xw'
        b'8NqcxAIOxYLnkdkfEqXF0/igE2z3dsDdhPpo4TjB2OLmiQA3jS1kaB5U/0NcCuxeZLesKEBLTi5zgUOM/wCcqcQuhAWR8HC5LXYXjDsLZnvynZPgfuJSiNzAUxeISotj'
        b'MfmU5McIlhKHgRB28cDr8DZ8mThD4uQO0fj8MQXsiC0Q8ikH8CYbXgYvl5EbJDqWlrB/xKfmVK6VeHzkc1r7DUWGAbhEg23wssE3xKzBQtQF98SWFi+IZI4zM6112gA6'
        b'yVqsE+CMI6r3EUS8eN2OHbiJ193kx0TB3eAKi+KDg+xYcGkDubcBvgzPLy7EtnSQE8VWsdLgYR8hh3hepGvAUZKtDL5qyAW3g0FCCCVu4AzJBbdlkmzSjYQlpIDXmkkt'
        b'S6LNK/kmfFOu23SJo16LbLKMa7teWTizFMa5XjlRGtF49LQwTBCe+/fst//umOtwKqcmL4R7+DL9Yu38mP/a/vf8D0oCxjKKcgo2vrH22y/+kt7z0FvCndEFboV+o67+'
        b'ZOzsWbs3fHNsxmr/tvfEe18INAd/uaow70TSL9plrn/82y9/kWrfEQoeVM8osv1H8ls7HymydR4zklkL920MfD/OPiXwWpM6xO+bozWftvtO+0/XRLtm+Pe3tv3py5MP'
        b'V/RU3/nZC82/3v/k3pwfeap+/kZXtfKsqvSlvKLzy9ijy77sGP2Z49jCjoLviv4z8ze9p2QzFp44uio+9sArlcc9u3/zy+y75R++f6/6nT+1BTxf+/H5/o0DpS/eD/r1'
        b'0M3hzOfCrx59UTLrylfrvLtPfDhr/aHPNs2/sfZx9tp97hf96o/84S154EN6ufLk70ZbAjoOqE5rr7S9OjTj8UD/FwvmfXye3/NqyRcfev4eNHx98/Ybo8sDq1YXpd/+'
        b'4hu/5b/q+fG0PUN/aalccmPLwMIruaXL9lU4RgnXh/3X32zKtapDXX8UOpFzFdX8WHOnT72QLCmrqxA9CSPksEo+yeWTB7YzXh/s8QHb1jDXO7wavWnc4XMOXmScPmRZ'
        b'2QDsY/w17YlLCk3LwfLAWS7lspijSAf7mOhBcKU5OkosBFsDkfRBlLqMDV6Bp8AFEg1uIK62K1qMZURMdg4mwQNsEbwOTz3BzoIGcAReKyyK4oPnwWmKvZKVCl/1JQvV'
        b'ZsHToAOcK4oArxfHsCluIQtcAjfAVlJ/52wlPo6biBPQ1YrE5UZ2BNCB55lVXr2wR8isGoN7N09cOKbmOeUlP8ErkEB3KNgJj4GdxuVoEyeLBbCHuL3Azqj5ajw8RYi5'
        b'ocqdZzxtbrCdAwZngT0EJz84gERwTGQeOFAx7tZqBbuEnv9ut9bU/i7cpkSZ2LrVmtPLGTtWxk37Vm8Lj8t4BHF+zWQzzq/NDpRfaO+8/iR8YP2ob3o7n/FzzRj1jhz1'
        b'EPbn3I+ZPRIz+07wSMzcux5ziaMr607RSFjZqN+CYcEC/XQx4+hiss0c9RaOekT1V9wXzRkRzbkTPyLKueuRQ7Jl31k5ErZw1K98WFCun5GPnWFpI67p+kjs+do04hpm'
        b'5iuLiMbOOPS2ccQ19IFHYJe0d+49j8gH/pH9glF/cXvOA29/Zrnb9ZAh6U3hSJjhkgyU05ALO/GyDmXoUzPac4f9E+8Kkj41BEcESQ8C6V6vY8vvB8aOBMYOckYDk9rt'
        b'9R5eXVEjHqEDHv2V90UzR0Qzh2pHRdl3EkZEuaPC+e8E3xUWkm8WvdM6ErZs1K9yWFD5cVrm9fl3ct9Z/Fbp6IyK0bRFuFpJI67J2HuXnIm/Fz8iSPg0OOyMb59vu7Pe'
        b'w/tIRkdGL/c+HT9Cx9/1iNeHJQ5KRsJS20v03n53vcXDQeJB7jW7i3ZDs4a9Cto5GK3Q+35RI+h/jyh90PT7QeKRIHG/eiQosX3+A2+/rtTe9BF/0ai3eDDsrnfqx0ER'
        b'w5FFo0HFwz7Fn3r7d9X31qPkqGB9dGyXTa/NXZ9IvW9gr00/r8/5rq9YLxQhKO+o86eRMYMVd2pGgvLb5+tjEttz7gtCRwShveUjAqHe1bvLbsR1usG9GP6ha7yZR9GD'
        b'8Shif7vqOn7cwI+b+IE3OqluU0aP4g90Jk4kfPypia5Fk3fxA/SYktYrTR5GfKzwGnsWS048jHLWV+T5rB7Gfn4aNeSQxeHUGg8awH+me6AQs7LwBh6hdDY6Ox2X3ATF'
        b'1jmSi0acdCzDfVA8NrXHtG1kE594/nhmnj++mY+Pt5lv8PxNgE59mPdkM8OZMTMG+JxZ/iwcqnacb7eIqiBQ2yzewhIWuTrEkZ/dRBE1rgZp6J1qsN92DYfiOMMhcJ6V'
        b'tjqLTGNlhYOD5fg+tv2LihfAK2XwyiKnlLg4igr05syBHWAbGISXyVwN2L8JHCuH+yuS4+DePNiThHR82zUs2GsLLhLNyxbuSkNFgVfBACmORfGiWODoumaiAfmCo8ng'
        b'Mh/f+wT6waUZ8Bw4Q/QfpAHeQmrUSfgKkjBHEUcLp3yckU5FpuB6wA7QXSiGnfK4pIRkNsXfzAIv5QIGI8TpX0Qyg7k7qcQeXjFentQEr8inU64cNTIwqJIZb+8vLyxB'
        b'etCJNe6pb/L3uvYstj313E7/wbrUl9/Ji7mUfXgTVai4MSdg+q8OFAVfKKhb6Pbupa/qfnHstxf/tmBT9nuBz//5xmbnanrxxfBb/+fNtIfvxf5C/Ks9iYe82x9XvOXU'
        b'3X7rg5m/i/mJ1mvHj27GH9OnRZ+MPX+vLki47Mjy/Z5lN7I+eF8m/vxvQSvWJ1VO259S+UJmxaV/dO9b8POvb3/yvv+pt6rfrF/1/k9OHFwU8vsFf3q3c9lHcNVxbd/A'
        b'n3/t9FHhxy8p3404vb4n709blv54y7I133z++ap7u7N6f129/6c3cqv3Xz8d/4f+lDcUeUtcE3qu+w+89dfu7zS/C8j62emPPynQbJn/hbQo6u3vgoLSZ+oXzD/zi4Jf'
        b'/HU6L+r17zZvuf/xwscrFl7ZcNOlbMYWTtpz0nhRlND9Ce4nj2YvcpEashW3+7DBy6xFmgpyzDmyGofikLhnZD3YmoDE/UIV0QTKYK+XSdpTiyqJsN8MXyQrxJF+3waO'
        b'WV0iDnawsLCHx8Fpsg5/I9KctxvVJhs300r8OnA1jZn/2ukJjheWxCCj5SC4jlJiXccZvMGp2giGiLoyu6QZyXh8VRbFDcpqYYGXQfdGcimCbTU8MH5rDTJfLnDItTWt'
        b'YBujJl0um2O4acvNnRRALtqaAQ6QT5dJnAqLquA1i/X/XuAC1z8X3iYbABzgufhC88X9sEeF0riv4oDzwlRmZX0bPIPQsz7Zlwjb3LHmt9+faH7lq8EL5JIcZpH+dnCa'
        b'LNR3CeI8h8zwflKnme6oNEbzgwfAG2QzAFb94FEHovFsrAOHC2Pmg6Pm83hoUF0msYGgA/ajT5guBQtdzgIXka3JnAz+AjhgX4iiLy81Pzl/tYZ0eb7bTGSYgON1qMal'
        b'+Nh70M5uWg/OCd3/G3Und6PuNPkiqzGbKuYSK/MVegyEqErHGVXp0VInynvaEUWHolPZzsE6SX2vpHtVf9Q9j2S9P92T0Z3RnqMPCO4p7C5sn6f3C+qY+6l/UE9adxoG'
        b'T+vJ784n4Pa5eg+frqT7/jEj/jF3PWL0/tN6g3GiR2zaz10v8HvEQb+fCnyOFHcUP+Kh8CM+5RnQldVRcF8QMSKIeGSDYbYG2JHSjtJHdhhib0oVPiIIf+SAYI8dKU+f'
        b'Lk6PY7fjcFjKqE/qqCDtkRNO7Ex5+j5ywSFXHHLDIXcc8sAhAQ554pAXCpFPeOM3H/xW0lHyyBcX7ocLt++VYiVx5kjMzOGwWSM+s0YFsx/548QBKLEB40D8HoSS3xWk'
        b'd8/t5ZHrztaN0mmjAemPpuFImkSmokjOGcc+x/6lo3TKaEDqo2AcOR1FPgrBoVCMAG6XMPwWjuCH8ruyHkXgt0jjmxC/RRnfovFbDCle2JXTU9xd/EiEQWJcx1gcisOh'
        b'eBxKwKFEHErCoWQcSsGhVBxKw6F0HMrAoUwcmoFDM3FoFgo9no1C7fxH2SzK17+d96mr5xHHDsfulf0po4EJ91wTDYCu8p6l3Ut76/slfavuh6eOhKeOBqbdc03/PCis'
        b'PVcv8D1S1FHU59G7+KT/hwLRIw41LfxT78AjGzo29CYj/fq+d9yId9ygz1D6qPe8Ydd5ZpqYM6OJnSdUzUzWqcd4ao1EpRnjIIp+NrXL2ah2TdC4PqcsV7MyY+UCy3D3'
        b'29/wBQ5OLFYMvvst5lmXtL7EF1OvOqRz/jdXOX/3m0n+W2bzv8a4EdcwD6YwuKdVMo1WpSRxjbQET7Oaebt/0BQlvVq2Xo3KaVbJ1HhPBeNGN8wLqE1zowafurWpxYnT'
        b'pgpmMgKjU7NeI7Pi9rdQFm2tKIvMVUSD8A0sMOGL4CDYg5j8IXhgDri0BFnsF8G5BUDHo3zAVs6G4Brid6qHgxtgJ9KOxeCUGD1uwhvMWqLX4FG4l2iSoG2JCL7xHHyx'
        b'UCzmUAKwhwMGkrMZn+o6JEyWfoGIubror4khhqsBboJXlIacNhTXsxG8wgJH1HD/GIu5ZdQevC4hfjAWxYc6pB5iR9h10EscXjPA1UVYt3w91ly1BNfhJYKvJy3F0ug2'
        b'uICEHPaTrcsgiq8XEpoXkc66Mh3nYYP9rADYwyFRsMdlDuwsxJdj4ApwslgbwI418nD3YI76Im69axcOt8+0Z8e75taHb7n5hd2tXUsrWznLeR0SiZrbHVCd9YcfZf/h'
        b'D6p8D12llFecOHdd560msWYni73vg7mbbp39U83Aar2Iusp1jRtuuD2wLDf8raXP2e093H/y/ZXf/exDhyO3estO3d3ev+jsmVc+aHn/ly1/rTmz3e391pec2t+PPZ0q'
        b'jd618qXHn3A/ydnYsWf1m6rLLm9/8gl/XnrbiYJffE7VBK37ydovt5cs18/5aDbr4I4o58v7hXyipwQERSNdSwA7J++xCw4iopsPX8A3+RgvBJHB7ufYIUJ4kehP4AK8'
        b'7RMtBv05xWzUYP2sQtAdxehHV+HJ1UjlKoDn6/GiNxGbcpCxYW+EG3HpNKlh57iXBlwFJy09NSKwi7mb6qAbOIj1LPslhjtNGT0L7igX2v5gTcDWpAmY5L9EXYXHqxlP'
        b'M0CI/P+UYuT/QhfC1JE0DhOeKekruR+aNhKa9vPQjI6i9rld3vppwT0t3S3D4SlDnKHy0WlZ7Xn6aTH960ampaJQeNQZRZ9iMHHIZjR8Tvu8rshDpY9sqLDMR46otPuh'
        b'SSOhSfdDM0ZCM34eOsNQnl9gl6Q7HGkRPn49/G7+8LTYQY/B2g99MvQ+03ptRnwi7/vEj/jED0be88nEIF63832f2BGf2EH+hz6pj2y4tFd7HtIKIhJ7pczHR8KzhyLQ'
        b'w/B9FypsJhL6PoHtjv/UroYvLeWAoc1+bb6rYZ7LM157cgplHGCNcZslmgaLy7FMxizelnOYZ7gcC59rge9axpcK8k0XZJks5H/5giwkDD7jsKysphmXB5g1qyUtOKRQ'
        b'mEuGH344A65sBp1fR0fhUBSN5KmambfFPF+2Dh9yg6cxo8St8uaoGPIhg/BRWZ8FVeOzwaWmuVeJqrZB3iIT06V4qnitXC0zCRhSBqkASS6h65oUSJp/j7SYfNW0bYk2'
        b'GjOBIVfYFp2HmEdZHjI6CoqLkEmfh1iDLkYs5CNjfReVB3fZNMNzc8hUzsq1YHshYjYFxWK4B9lkFYh/t8UuQDaHKBIMcBvXUoXwqg14EfTC1wiv9ytARkgnG3GMc8Qj'
        b'zVGwwPNwm7PWBUVmsebE5UQj5NZR67bAN5gZscEl4Gh0KZvi+bMWUvDoctghP75XxVb/FpNv3cP9Cy7agzjX24V3Vwk6pk+fd+K/2DZb5mhavDQOzmkf+l7ozb4xxFvx'
        b'44O/K23V/8Q+flXCr9d9+8Unn/yH6I3tjaseHfw/s+pk22SvN02bvjtK8zsep3L/a5UhZw9tWVvb9EnljT/e9/zwWOfzX+z46sbvfyvY8vWKhMGLhwv0/f233hnZWgL2'
        b'OuidqZR9XTG/5Wt/9lu/unVv/dTns6P29HOzz+9pdv7b8J23V/3s0o6zd5scd/R89N7vG9/Zn1t94LMz4l3XRYt+/bLvr4HtzG/+sut++cBvN33VEPzOdruiYBgyd6lH'
        b'7u/+80f3m3Oub6DSP08/3H1X6MLsD78CTsK+QHCKdBBSq1JZ4FVwpphw11awA7yBLVRy1z2PagSHbGEbexO86EWkgwxeAD08iA8feH2tYQWpHTjDBicbkA1OpgOuwldc'
        b'4E7E7XEpe5Cxzy9hB8BX4A5ilcJboXA7PAF2og/siRHnkxQOcJANb6HePULMeHgWbIcDK5YXxoADpcydcg5z2LALnoM7mQswryNdRCdR4TJiS/Em983sKLB34xODV+eW'
        b'oBjcxvNeQjE8SCrpEsephz3MhdmIZo4LIhebXWnFDoG34QDJDQbgizkc+HJ0LJ5oF4mFbCReejhgJxgoIGYtaOduBLfhSWKpx5bwKP4MtjfohIbJkB7Q4VJopHQKXoOD'
        b'dgI26HMMIFvr/ZBGcQPsxr4OQ9tks31o5pI4ODR7Htwz3dyeRtb0CnCFxOaibukXgnMMXuiroJ8dg+z/I0KHf9YadqAsZhIYMcjFTKDVycTP8SsRgHwWIwALXCmB15HU'
        b'jtQjszpm9Ybe84j42C94eLpxx7mHJ4mb2TGzV3DPI7w/4bWMgYxB6b3oTItkPgHYHD3m3M4z+MI7Z9z3iBzxiOz3uucR98AvuDe0n9O/YtQvA1nK4dH4lq/Tjd32Xdwu'
        b'qd7HH+ftrehP+tAnDhlGEUmfCryP5HfkHy781D+wJ7U7FW/c6w+95x+rR1LTttu2V3DceUIpDwKDe6efieiLOBPTF9OvGawYnZ4xlHMvMOvOQn1AUE9ed15vxfGSbzlU'
        b'UDZrODDrMf7MLwOzUPA7NT6V6Edp7vM8eT/25M0LsmNEph0jMp9MITcntj52JJuMKkaU2rDwhXgWTf8Poz2FPdcbkBz1wYtin/nq0xf54dRph3iOkDmpaYwzb9HCEnIh'
        b'lUqOcbctMfwJecwPG/3zmHAGMN49KW2qraoiW/THbJtVTc0ylWb9DzkEAO99JEuAiaeeGI9EcyB1Fgr+R2bOsHdy4qTZeOPjK/laTWdgYQTVjSxyNttjLtvJ9Utbytmz'
        b'jzOgvpM5smzFg6Dg/vTh7OeecFjO1axP5+XqFyz8hhPiFP4VDwMecVHwcQGL8pv+wFWkF6Q84bH90nQFj/mUb/AD1xi9IBlBfFN1+QgSFP7ANV4vmI0gQVksXQm+jY5+'
        b'4BqtF8QikE+8Lm8cko4hmQTiPe2BaxQD8c7UzUcQ/5AHrmKmIH9UUOHXtiynuawv+Qjx7vI+9cXEtzzeTXwQSA94XA95K/FdKUa+gvXpgkX6pSu+5YicslkY+wqEPQ5/'
        b'+RwL1zjkYvlbYe/a3Jn2wD+oW9MVdZGDSikfWbxsRCLDBdSzkCpchZdsc0pZTglfUviJy0ERXBz+toad7JTL+orCz6+VLF+nwC9TMEoh95yCvmV7OUV/xaGcpz3GofFz'
        b'nhtcwH51PmLAamdnDpVW6hTIhn2wA55jVgwVz3QA/RosoxxgG+jAa1DK8NqTgARuyFp49X/xAuofsD3apoRZ0nETCYut+OY8eDojmAqGt8Fxotxw4dGoQjEYjEvG4avg'
        b'MnidtQYMTNdiAQ1eh1clZMoCXFidX1RinLIIAj1aLKCRSjQIdsG2fLx5Yx84CK8kcilb0MYuEIPn5X/Zsomnxhzgk//cy9xkHd/WweKc33V35T7hvmXvdX05Z+V5GDSk'
        b'vVC34yH/bO3bFUfAC+DWUbt8pwiv5Ji803GCiy0Jp+M0CXnbPrRJbD7NoRqr3BxDcoU8RjieBvvgBXJ4DHNyDNjlzE4E/a6MhDvh1wrb1oMOCwnHA9dIbDY4h3QSZhkB'
        b'WUSwENxmi9yQ2YdjY+HzQIdFOjxQCvrXGz3GWxyZ725DNmkvXh2HFIZX4QEcvZItS3WZcie4Y7NKhvRuWRVeJ9pq8UbE3WKKEXdz3CiBDyOgdDmfengdSetI68rpKegu'
        b'OFY0So4zR/IrsyOza22/3ahHwvj7ulGPSF3OAxdPvbd/1/yuxe2b2rkoTldobmWNcfEHx/jMIRffczO2BxYPFpgGs83uxN7iymL5Pevlkhak6mr4/eoX+FxIB7NzIWPx'
        b'nm4yXuzwCZEyrpS9g5JyznNNZyvyCJSHoHwzKJ9AbRDU1gxqQ6B2CGpvBrUlUOaESK7FqY9cwwmR41B7hI8Nwsdlh22lgzROx6pjSV0Rbo4GuBs+4VEaT+AeCO6Mwzq+'
        b'zk5nX8eVChDERZqAIFyU1hOfnmg4qRGfzsip46AnF/3jGf9J3cm5jfaGMGdC2Bhv/OUa00/4nQgn71Kv4y5ySuqN83eypD44Hv36mn8DvfsZ86Gwv1k4wCwcKA1Cz2lm'
        b'ENosHGwWnm4WDjELh5qFw8zC4WbhCLNw5Hh4Yn2lwuPsV1jSqONsfB6lzF3mJo3GQ3VVBDXpz8hLjWdVGtLH/ND05CsCw0GNzNkD9nU2UhGiAk9ymqYN6XmeVIwgXuvd'
        b'EZdOHLOrQsJekousX4tpfJOLASs02MtsNo2Pz4LkosLx1fB80+S9zb9t8r5uovDgUBOFhz0zeT84E3E4wctkt+oLSzczKznXpeyjfJJfYVFl1c6JSLsjwNdFm1h/XpXF'
        b'ouIkmXXzFlLkIu918NIsizPeLBZH4cuubajIwvJ6W1dwvIgU04e025yKnyA8qtl7EsTUb40oEnYmz9l3mqPGCx8K5DuO/TQFCZaLnWEvsfhdPhndmcuWJGavm+ObK/Dl'
        b'dxV5z42Ya1+b4sGZG+/d/uMX/gjulIVS0vj6Y5xlH4edj9v0+KowJm5m8b4TtEe3JOFEkdBReH4hHe81tMr1oOfOt/m/vcha/4fmoA0Z7/wmIG5zGL7ruKvWrzxuSGjH'
        b'WHcn4XH4OnOfsYhDga0RthVsTbg3iXQHui2gDbyGJ6HhbthB8SPYbvPhq8T0a+LNJCvl4KX147sjyd7IQ+nMqrtT4Ca4OHEpGW6tGviyDRXmy2uYkUiWk9nCdvgyc0Za'
        b'dCPcHSliUqJW9Q7gzpjny6w5O0eBC3he+6gHXoO8n0xs78OLzo5xQB+VTQzunLhylMTD35CiGJynUILDHHBSAm+SFLagD/3XFous0Xy4j0Xhtce2cC8b7IDnNz3B7hXY'
        b'BXTwBmhbiwohShMqChwsRVJ4Dz5M7oRazKfSC/ngRRpsFfK/R4vG42PSIWjuprFkeQraeoqRoivcqGmh7dwXHPCSK8GxZSho/9ieokN6Z4xOi2t31HtM6w2+6xHS7zio'
        b'uhuZPqR4p/burAVknVXmqN+MYcEMfVg8PpFsun56dP/c/oW9YnxOmj44jBxPZvgJovEn9MGhvbx27mEnM0HL2GZjPLLqf4yLN42NOY4vEFI2jdnJlc1aDTn025rTk7HW'
        b'DLNgT694LNtsCmy5G4uVhk22tGc12br5QmrAIelfOqWMV4VrOtW5RGa4Gw8mymKbH6NUebSSOZYoYPzQ6kkHEYlVOmrCtevPiKVTlXlPPAO2OWyLo75i7wbGMvgGmeE7'
        b'+Vwy8b+CrH2ViVCeAdP5CFMVPjeHwS8w31iGcQ/Vvws9uypM4lWN8inPzrKCXQHGbvx4Ly9sBNN1qqbGfx2tOku0JOueAa1iS7QEBC28X+9fRcpweBe/StOkkSieAaMy'
        b'i+Gx/Ohyw0FtFbgc4zbAKdH7n5y//gGaBI/RJLxLkR1m+y6ebI0RbVrAKA2JATaUo8CXh890TdIUUvJiTy1LHYdifvv76UbDkeVxKq6A/W7NTwpyw3eVBKxanJj9YcIi'
        b'1l9a3q3mf+BIzfiLzXOvnRGynuAZAXhkLbJG2+BghXUhZJRAsN1nKpONOT/LzZzhjp/cJaQYQSN1p3wCjmzq2NS74K53hN4/AC+NTeqZ2Y3XJPdnjXiLhl1F//zpXZO/'
        b'Xs42m+iqdf8nJrr+F50V9d/vrDBQybYMLjYPfX7ruFWhz5o/nSwLOXHuMc4d8TyLYl36Rt4mXMkjNPLXsDcNNHLgXUQlmoQ89rsxdUXdgp8ITn9YVLYo7ckY9W4B/wMN'
        b'pXa2KXopXsgmNAJeCgbd1rWU0o3jJAJuGGYa4Fl4FBzBcwCLQF+USIydBs+zE1fAa1Na/S5VZLOlvFVWVaNoql3d6mvWoZZRhKyiDGTV7E5FxuDF6IOLRiIy70dkjURk'
        b'3Qm5s3Y0orSde8Spw6lLdtc1dBJdjfHIVsLvseuzsV0/NSJLzY38RkRhvs9s5E/kQngq4ivs8GTsmyPMhQNUHed/gsYmzxoaDtCOKfhm5a/Yehtkvmx5gpce4+V6YKAg'
        b'HZxDSVupTHiyFZydzYCPLoU9APsDNlDwYuuGRRuYw6svrwB9FoYNIqaKyBIRiwqHHUlgD98Z7AIvks1wS5bykqo5ZKVzUdOqNRTZ3/WcvETwK77OiWqWeHy09PNYd+Yc'
        b'oE2gPdd4mvX4Ji94pK48z8jALE6y7oPd9vCoezDj0MR+uxXggtLolUvk4qOCXiJeucXwurz5yDIWWTNyv3f5sZ/OQANnZGdwSwRnrmiu09z4Whd/j7kR5U5wVS4/Lk/y'
        b'XoukOtLrnOSd5/fS2wXhXTdqtvntEvwfhZq/a/oX7nVDMxyK3tjjJlVGqL0cvMqXhm0LLQo7+7dFzamC9OyirTf3ib74y3KOwj/z44CWHY1zjqXFN1Y6veLrO3gztM2/'
        b'7fdp1ad/dfcwqHyr4i3ul5y4F9ZdfEcNNnFeKK4rqbvEurSh5XJcRULzaRb1dm1E9V1foQ0ZiTWwg2+cboMvy0wzbtIIZk7tpaU5gpoJx85gw0oFX3mCOTe8oSqxMvDB'
        b'SzUWwsG1mqwUgS8i20rnEGUwwIq18aDbUOo0cJkLX2ta8wQP3EQvuIcsG8amF6IGcL4A7DcKHD4VB87y2bAvwAFcI3NzW56DrxYaD6zx9iVLXeHF58i0KLgBh1oM3sd8'
        b'HgUOwp3E/Qg7/IRcq2YSJm7TmcZI1Virkmtkra5mo5xACJcZZLjMVy3uVGBwe84D/2l6H5oIrs71vYmHtvRrXts0sGmo/F5s1h3pO7Vg9cdBkcPCzNGgGcM+M0wCrt99'
        b'xD9m1Ft0kTOYc9luxDt9aO5d79kP/IO6NMfS+3l3/UUfTxcPx5aMTi8dDijV+wTc94kZ8Ym55yPGs3FO3U7Me3/5PZ94PbPwtHf6qCCsX/Ca/4D/4NJR4awRwax7grDH'
        b'nghNM17HZ3gdV6KqV1uVpHwjvzNeD4kZ3qSmWGHG577Ruv8Ts1yd/BDqpIOYU1LLtSbTyJoRltGhQ9w5mPGx67iE7XEt1ozwCNvjmrE9nhmD427mGdjeBOjU8wCTDy2z'
        b'KSFLE8pgex3AN39MA1vBy9Q0G3CCHK6vxW2nAKfrolFzaaPAYUqrXUFy+MLb4CrDFOG+CPQ4zJWPNJxmrtl8+7PaYz9NONEnvc/49k/FtSSsTThft+vRja7M7jbf6O6F'
        b'6LeOI6tLPD34nsyu7tMiGyrxhr2+ayvS1XBPpoKbrqAtNh/qNoILkQCNlja8gJtF+TdwgQ70g9efQvNbzWie7N+36GgCITQfx9D8ozIPyjfwvk/kiE9kv9eg5xB/1Gd2'
        b'O++Bd4DeP/ARh/IJ/Cwk/Cxv2Fs87Co2ozmb8TWuKryzWuXJmqTGqW0oxmg3SdryiYRH8JEbCe+/8PlDHixW+LMIWFtUpgW9meQbcSByzejNBlEcdh7aEaqz+W+gukm7'
        b'f6wpdAx14QYBPbK5oBPJq+dpKpAK5NXJFZQXT42veV3U+e6xn85CoujCtv+vue+Ai+rY4p5t9L4LrNSls7D0Kja6wNIE7InSFlhFQBaw94ZiwQ7WxQpiASu2SGaSF1Pe'
        b'C+uaUJK8+GJenskrwRZN8pJ8M3MXWBCMvve+7/cZcvfeuTPnnpl77sw5M3P+p3XH9o3ff9vAv/1d/vQ/vgN03rWLNN+TevmTzWbLrW1rP+Zmva2XqXr30/cj9rfunBea'
        b'Z6B+45tsotxNcjZ5sHJx3/t6hQVaXdC/QMuIkCFd5dDIkaXWextIpsIUrhGmN/hAMKp2HBadbmsnpVsj/661T7edo5K3P6k2rlvoqpzcGK8WBmH5cvM85dZh7d9h5q8l'
        b'VAavIFRDeTYYkLH+KbEpRMyGZ7e0b3KIyNpMImuPwGsKnOdQgevvWYqB9ow17eB0NV0c7/+FsL2o2fUJG90as2NeZabPFHgTrUW7gxI4gKfLgqvhGXhOHvSRDkcRgfNc'
        b'u9+w/4MILHXHV7WyK3YErGvaeXXtdpZBnTBi1JjpU2J+PGg0+bSRkf8sm0xLW04MVjEMQepC/dx2Ee67yKM90Q14TprsFcXTob7GeugS1sVHlDhen8RpnGdna2IJaURO'
        b'qPUOB92hUifRSF1xv9R1WTsqg05zmuJa3JqT20JVkii1Z3SHc4zKOqbDLEZL0vSGSFqPTkFOXkVp+bDDp56WiDECRhwaR2ZugbaMzSUy1vuaMkYfuVfHA5w0DOSITRkv'
        b'TurPST07iY9nj/HApN1c2aIe46rSyrwiWTnlIGDwZWCPYR4Bv5WVVMjKA7QvAnv08uUKBrWWOIj28KpyKkiQL1llRc5CGmyK7CbpMZItzCvKIaGQSNJxmpPsiQ/oMehD'
        b'nZXna8HXnaA5KuQVxTLc1mSLSzkZ/cvnkgNZ/x4SfCy1R4+EHiYkewzJWR9GHE2m0Nn0eYHluSyyEYZADuWWLqQweT28sqLSElkPpyBnYQ9PNi9HXixm93DluGQPJ1ee'
        b'hy90o2Ji0ianZvVwY9Iy4srLSbdC5psGGWakzYmu+bgE9PmP7gV0NYvsbSVjBqg2KND7f7FnwfaFDzmPMdFcxctYz9kLk9j+OWMuOY1hvENhE6ybokCXTcuxZrwnl41O'
        b'sLxW2NNtHJOC4G5FRRW+hy7BbRJDFtBF+9gmvkWV5GuHzfCirzcBHTjjmZDim5gyCVWnwjMStM0vaVKCJMkPW1pYySfAIqMnk+0daOdMoxhsHBysJN8JOocaOGjnJLJ1'
        b'DtVjAzFFii4zWyt2oHqbIOJgyvJwWUagRo5lMtivJ+J8g9gAboV7QBAImg8vMZQa4J5UnJ8NWJ6oDW4EcNfEYGq2octwFdzQ53A3fRTWxQxnsNHZNLSTOp+OQSvhJlxS'
        b'B7DEsAbtBXA35q+WVt4wP5xxJQzhAh5qZaFj6AraaYWu0qbMifECWeC2jo5ZdrRPkQtgGD8bD5WYHAuwvPQluDVNMS2yyKMbHSv19fElKDwpPmhTMlnmKbKGx7iR9ugG'
        b'pbeE7QQiQbq5Tlm2XU7iGAaIxjeUg6lxAEsCr3sAWAfrRzPVuhCMGrwJpmsiY9FMgG2mcAsnt2QcJeZnYA0kwJPLEWW/4Zk7RsPcXli/GJPTBSyfwgUA1s+HjbSi5eg6'
        b'vIZNIwls4gK0n8OVsOA1eAAqKS173QlgKVjJMvXPztgQiGnRHZytQnQoKBhi04flC+vRVmzRozXoPL0Jb8GmULLFH9ZNSMGmu34AG9aloAuUnHxCEtgF2ufzzLLnfF6x'
        b'QCOCjWFwKyGH37hfAFwH4H54KZUh1pStyzgy0F2T69noBmp0malPidllE0Cctjj9yOziaYVmDDG0SuESFByKOZMQPwfySi+iW9RjGFup0VICfluDtjJOolPnmcC1nPEK'
        b'dIwStPIMB2Wg0ZabnR34rqsFM4dhgXbaY4JYunzjZwK4N9Wjktqxu+CFUYlwB0MwtW9RkQVs4C4u3IQOwRYqnc5oqyEujkXMD+5C1fg1CrFUkNdoAI+UaEozr7EIXTMp'
        b'44SHwQbKTVwpH7gCPa4JyB77mb0boOTg8TC0MSiQiKwkFjVjIYuFR2hTcWZYawSWjQX2PAtVz0S7YuEx5u0fk80PCsFqOyvQCF7GpVA9l759PmyFp72lxFOEBXTkbHQL'
        b'NoxCjWgPLVYE2/yDwkix8MXwFhHBTREMKtURtHqJRgQ32cFt8BwARmM5ZnMSmZdQB6t1cEHcaBEy1EbE4wxay3QqTjwp01RidKaMePAamXEs0WZ35jvw1QdmYJqtXna2'
        b'UfWkyYzoToE70fGgMKzksyL04FksuwtCaZVXoDoHzAQBH5Ji8chjo01wly2/kL43vQLYgAthmRpjEII5iNJloI434s6sWSolS7HsUnQN7mZFwnUVTE+yD9bCbbgQ5nss'
        b'ul6BBVFRQJ+kQEczpaRD20wWaXX4bKwIXdNnh1KmG22WgCegy93ALDvUOiyGeVFTzOEheME/mAdY0WJ0lOwtPhhF264cHofXsFWWRJaLcXu3cNBbLLi/DO2h1CZmxIPN'
        b'4HmRnig7qa3KgmmCyNmwnlDDnUGMFe7+oDJ0Oe0jJgTNkOIeBetLs4LSsYidR9uYD225EPiDlhij7Gy709YrmO8WXkenYbU0kWxBtoUHuVwWPIzfdQOllGhgR5y+oBIe'
        b'BcTr6xCsobNyfgtRM3X8zkhAG9N8pjC7+1F1igT3Pvjz8J5ooWs7ikVFeg68mc0ATznCU/Rr0EN1bPwJbhg3EHJuSQEB3erINgLZyfFTvZm+Dq6xxJzs1AHJqAV3XhK4'
        b'2auSYsBcEThJh6zYY6bP45GGC9zgKV5loZCK3LJA4s08icATcAHXgmWGrr1p602rPRttQiulWWgLlgVUn4MOEYe4XehAJVHjMLl9aPtgBLXmJZR3tzSeHB4Wafr2HNiM'
        b'9huCaaYAvoX/ZKiOOsWJx8Ot3rhFUtDWBJ8kamzDGysSA7jAPYsXCOucaZ0/mGoDgkF7hb5Z9tKjunlMnYMkb6D9ukARB8i3dQtWoy10g2RFxPghFMXjEgPYwH0yLwg1'
        b'4W6WdgSr8qylk/CwykKn3VEjQDfhymhGws+gC6xMPBxv4QFUDQ+zl7Ds4OVpzL0j8GawdDLTFMdhE6oF6GJwCa1Jdhpq64eo6+vNHPG4eCGFiy6jm0w7o0voELqO9huD'
        b'tDIAb+A/uAY2UwC3pTOT0TlIptlwt5CKiyf6BHKxoO3jFqPry2gzQiXag1/ffg6I4wN4E//ZxTJwbVvmwHWoFq0bVJqNS+/nzoOrrBkFYKUQbsF9OihfAuRADldPZLAp'
        b'DtiUEgeUfqZxLdeY8jlzxBoHQQVsmkomaWBtKnAEjqgBvzvy7nVxa26H+9F5bwYgHUuXHwNMZwcvcdEmU1PKdOBMdBPtx/0z3Iw/IfIV1YYxtXnLmnj0Y5Xk6hQwF8zF'
        b'bXWdGaHXo+2zpGhtvI9PIjztmUQ+OH4kB+3K8KcvbwnWuo6j/UYgH2GSF8m+0LYUWtIP7UX7pVrR/ULhRurTvy2M6aLWTEG1CmNj3EOhrXNtADqTjjZQEeMtMAQCYBas'
        b'Z5Yt+cVFxMwRCKUuqIYDxGNBKSjFHd812tgCS7Qeq20JBKpuszTNh/InsnVy46IWPEjto5PpC+a5stIVx7DFE1nyRfhBdo5Gj2hFzegMmb+Kwx37YrAY7lsiL1bFcxVk'
        b'0SVHdH/3nukKiyiz9wrXR07zd3US8vh5RnNulB51d4+/v+zLK9P+mnV8zqKZi0R3H+24sqx1aeu/zZYmLrmfGhPwRf1ur7pTh3797dqSqsv7v/xxgvOjpTkrLhb7Gqj2'
        b'rNoR3Xz53+bn6s8WyTZP3PXswuWzhVPqFy5a/qcfDOIsl4/hOV0L3PV28YeozSXi79b664LfST2b9uUep3zrwp+kvM/M5n40ZXXlgUa/kxOXzJm67YbFpNAP5p6LSN8W'
        b'kwl+y/3HuWdPAq8v3vr2jykWP+zYeOw9+7X66/03rj2/xv9dM6+Err+LkoPWLkvo+l6UNSraWF/Xbu2o9f41a9eYQLuY8F0/uf5tFMxxlYTrVa4v4+qfta3c5WQnXXbU'
        b'ahR8ePdvZaudDsRCse5fgmPCd/5k96fAtYomfVyA5/pGhZlvwNoPE9q+EkkC1jYntBXo3fzg1uRNPqxx3rrjHiz+fM2R1d9OibL/x6jnWytK/lVx8eCbxmkX3P8tdv7D'
        b'o7IrP4tzP0n6KPnu8nc/jXJTX750lfuw5ozXnak/fWErCJlpvquVXX5Lfzpv3VtpnOvjn38cvvCd5Yq86qmBY8pyXbJvBYSzrm06FLR4976Z98YUzow53vmV144frx34'
        b'qHN/A/wxesIvlTt5nlJl2+6PGp++bXRfv95s6tN/vpOX18UJ3O/h/HmO85fvLllQeu+bjLU/G/1lVUqH6cPxPmabJq758bv3Et3SMqY82vX+/VHdO8VQsb53tavZx9Nv'
        b'5eudq/6Nn6VzbtQvtuXRmWuv/BZi2Wjz54C1z8Rzn7c/mPBdWnzThDHlz6H/W7mWxjcyvwz18L+Qv7t9nvRWCT/6k1ULfrw+Z9cWmXTh/hUs0+CnOfxiMZ+ChGWL8bc0'
        b'ZFOXCTrN7IIjm7p00F4GweSqGdzgTRaT2KTHL2alwGq49QnTY6aTfoVYLzrALogby8LDe42AujyFo6PSxARYY1pmVI4uwi2mVcb6OkAAD3NKyX4yiv2RAFvCDNF6Hdgk'
        b'SehbIjFH1zi4Jz4Bm5k9zi1C/oBzkCm6TndPo+OxdAlGjGqmwxo/P6y/bB9NPkY9dJQNcc+/kVmCOYwOwhN0NSQZbc2j07l6Kex8eBqupn67uCvHGfCXjCtXNQE2saLg'
        b'uUDG4fYWqsEDlNbGbDYuVeuDmvJp1WPxOL1eg+uCDuYxMG6bUyhVk+Tyvu12ZKsdqp1ubpJGK2yMjk8bvCIEd45iYOmq0UU6D41HggsSWJOEdqUNsz8O7kV7aPNOd0Zr'
        b'YU0gVKa9uEduHFI+8STVP4FOpJP9eGTxjthPxLFMM6uNx/GT3qN58PJotO8JGcVmzYStFkZkBnyY6W90DF6mLZpkEqtBe6F2AFbmVzN+yErUzKwZvRVszWzLW4wa6M48'
        b'ZlceXDvrv/bZGgxdwsnJz19sPDAdhC/pBNVbXI3PsiVwcNagnAWp7EPv2Ee14UNq+/Rag88F1nU6hw3rDfcbqwXujYJO8WiVeHSbl0ocpxLE1bK6+YLPbVw6XONvCz4e'
        b'9f6ojsysD+1UrpPVNlM6BFO6+PZKKzXfgywXSbdLyToSpqSMawxSC/36r5qCGqta5Cq/SLV3lFoYPZArtMWjaUJbtFo4QSuN+osVq71j2jPUwoShN+ZgGu2BamH80BsF'
        b'au9xbeWDydMbRWrvCe0WamHs0BuFau/x7Sxc4t6rPmOe2ju2PVctTByWqwC1MG7YZ7DVwphXviFXe0e2Ow9Dit5wGqkew5GSqb3HtmF2o0YsMbTmIzZiP6mnPraWVg8j'
        b'gNBZ6d5o1eDb4nLXOrRb7NOkaAlq02mrumrSrrjN7giXdoZPUoVP6siYrA6fovab2iGeVqdTV1Vv0mVtX1ewfXmntZfK2qsx/9ycpjl3rMPpguZ4tcOEDiwLto6Hx+8b'
        b'3zilJb5pVlv+rZKrJXd8krvEfi06TQ513AMmv5uh295ZGdroqXIJIpB+8RrpVLJP6jbo3iPrnt4qoXdjfMukpqQ7kvFtQXckce0u7VVqYWqX0OGwQb2BcoJaGHRHOKtN'
        b'922X9oLbs1Xxb6qjZ6nCZ90R5nfk5ncJ7Rs4yvjGCSrXMWrRWJVwLKWqWcOyumLTatOWpg5Ivo1bbFLXy27ZK3WUVQ0mnaIwlSisTUctmqAiHwNDfrzKNUItGqMijv1D'
        b'aaSoA5JuR1GOR7w1UNUYza0kdcBE5qMargz+ENNerMhEdUC/0A8hJ1UHJPTdGFQm6TZPHZDakT5JLcx4sViqOkB6e6paOLlLaNsrthRbPQaWTtZPgKWlkED0jNor3SFV'
        b'hqoE4j3avjKGzJQ5USBfD8CGdJkvoNdspK6Wg7rMU33T5sTVcpIli2VD0AFfx6OGTpvX6XiCRsOgwft2+5doCgCDW0AXZ8jcLqjW1SzOsAbN6f63GwBf2HYjAkPndD2Y'
        b'Od077sSYFsVwQbZkGaccDCwPcmA9PAWxRZ85DzgAh4KZzKLhGZAIdxJs1UQwCozK06GG1XLUYB7EBWidDwgEgbANHqLE5+iT2RhRLCc7W+LA9wF0542ePUksy+FlZxu5'
        b'L3dibPrOmWRqOdxaxz9niWi2DzNzliKF54OCMcdow0S4G+RZ59HkWHNeULAOAPPREbgXyOzRJUrCfY4OMAK99rqibKO08HiGrkMlfj6INDIsy05unmPKcDB/rjlObEvU'
        b'wYmGFQVMTuckYyAEtyXG6dnFhnb+TE6RN0ks8wLp2ZK/LJjF5DROMcCGUq2Zrll2sWlMEJNz3mSSWFSFrSejDzynM4nXgwhL/vqEpY9lXsxeoBC4A9VlYq1qMzGxJ5N5'
        b'CF4VmTLdxqEWWho2xYOK4UV/MoHtSvYK3cIWFXlw4gIXEAvai/C7yk135TKTACysFh0i5hQ8gNsI21MCIYN5oBT5oP0GYAwmcRn/GaGrjM1Zv6gU7dcBy9AqAK+QePFt'
        b'yYxleAYrdofRThYohkeADyBeC6foc2tNsEIJyhJ1I7ONZtj6auZwt0Xoo51oN/mPB1jTRqP1AF7yCGSMvM1Yr2qhi8vXk8jiMrzOZxwUa7FtvRablLClfzcU3QmFjcIm'
        b'WtQE7nbIhDXLfIjxykLbWRYrSplNX9tQU5m3LkjQI9AOaB86SZPnoxOjYTORkUws1ovQqRwqp2ifdDrZISaDrWAJWJI9lXYm9K202JJp33ZjI1wdvtyeAbma2rkIfzAP'
        b'xPhLYn1wQ34pYyJHQVZq4uavvbQ7KhVGCtZ/mSxeLWKz2XGxdxtV7xy3fXMR91yvRcr1ZtvgxcAke2ys37cX60fN/cl0VN4/jqT8+bePO5/dqr/o+BePxBkfVvrws96Q'
        b'7FAcybrROCP5E2+TUyFWkvtmdzln5zeGV7bLV84w9P/u8gWfE2LxDNs2m/eNVUnHMszCplr/+avRK0qa81fd/6d9e5Eso3lc43fj7d55q/DQ5T9eOPpY1NO+89PWi18c'
        b'OGGxYWH0H3TFb0q/3e15dHbGP9a2fd+auf22/f1TLlvbT41Dny7xvvngwoojfzu06mFJuEzR/qBkrKzKw+DUvb/EP+vdcN3KT/leTbvLto9+jnhcF3PoQebqcr/mkJ8d'
        b'vvp216/X9rkcevgg4PzfHgoqlmdnBa36KvkA66R/6l6Xozv+dSBj8bm7hso/Tf7l/Iypn3jfTXH+5zumT9+x7pq74+antwqznlRfC3+U9r70ybj3VnBjli14IPnXGx+0'
        b'zqxvXLLUeNfOOwuEZ29Mfha2WPmN2vrp9WX3HoaKhU+Ik1IM3IS2juS1QvaEoRvwJN00fASepa4wZO1mGc56BjajzdhQ8yI69yU2ztECdzD4DGdM0AktiIXpcA2xouAV'
        b'BogSnZXEYoOlIVfjPURch9BxdJ2aLLPQJQ9iQ6SQeT60JaQMbSHwjFEceLYQnqPljUrJxpwk/IAGa7LljEWQKZyz/amdWTyZIGilJRujTS96WxE7czlicKahEp3PIR5M'
        b'3hzcB2/AzJ5lQSVs9qbPCJmL26UGbfRyRuv7N706waOUR9wF7CXhk5OxPYhOwz2SVGa1yGoa19bFkUEEv+oONxFLUIM0iY7r0al7CzcOPO2eSJ/Bwcbgfmq5wXOJGuPN'
        b'vBSdZ+yyw6glj3GwYowyuHuQYXa4gsHheMsW7cAmkt3UpMFATftRLeV1DDxTMUBm7Aotuw3VmFBeveF2ObahEiS+ZGfhcXTLLwkzipo4aCfuQw9RdlJxR3BG42vlia7D'
        b'NYOdrYzhaWq8jzWcSTNtlfIA1xidYbPgIX82rW0Rz106C7fzFm0synx4hEohOomNx9oX9hGiY2j74L2EdhWQMfxwx7ePzH1L5/tpwDoYWzwF7qcgnt5on9EItqg3bLEm'
        b'pihaibYytA6g1RNgTdCCfvcujRFZF0qN73IreMwbnbP10rhcU2j2gumv5MWlBT3RwyVOC4tNBhQick2NSD0OgxE+wxoIrGsrdo5WsnaM77K1v2cmIBufO81cVWauykmN'
        b'7HO6TbpdAhv6Z63RuTsFYqzHdQr8VAK/FpZaENgS2BLUIQjDtxmAykYXlcDnjiC0xfWOYHyba7dApBSctG2w7XQKUDkFtASoBSGdgjEqwZi2KLVgfD9VL5XAq1PgrxL4'
        b't5irBUEt0S0xBFXk5Q/txqYut1PopRJ6qQXenYIAlSCgxUktCG7JaMnsEIym94n6vzONIdGIb0oaMxrxzYChHGe2uF7xbfXtDExUBSbe9lQHZt4RTO+YOv0/zRfW4nZH'
        b'MK4tUKsFQlVOoW2Y/4hOQaRKENmOaxpDbts1luNKdQrCVYLwNgu1YCxTxrHBscV5oL2i1YIJzIsY9JzwFvc7gui2eHrLmqkytvQYBV6N6+zcGNAh8Pmde/3vuTfMLsDi'
        b'MbAT85+FA4HN9tA6TzXf5cloO3O33ghgbtknHnfNPLDAMFd3zdy7+NadfDcV362Rf4cvuacx0HiN3E7PMSrPMX3mZ0696R2hX2PMHWEoNi+5twyvGj7msMRxJDKgUxzr'
        b'CWBZxhP8CXPLvYbbDeti7pqJurSfYm2zd+H2hUruSeMGY7W1by1XA6iqdOoQuPbvce0QuHW5ep5MaUhpcVa5hnS6jlW5jm2bqnaN0+ztzyUxGq1taw1f3MHzCkAvdPvO'
        b'IJyXY8T4GPKt/avP+vgRWx/TrVksC7Jp57WcSYiLqphF1Xcx61us5vxG/Zy+JRv9xdZDwFyo+2K5IdmJ4kYOJAx9uQfZ3KLX50HWd0a2tVBPKQbFhbgr0C28dDsl3exG'
        b'NyT1GM1Oj8qISpmdNT09LrOHo5BV9HAJoGWPoeZGZlxWJrW8aAv8d5NgL+C3WJNGHfDplpD2rGRTAJcfdEyN3R86A4Fdt5lHlyDwCY8tCK6OfagD7Fy7zfy6BME4xS60'
        b'OnkAnyWI4LOEUHwWDfSKhECv+GqDsXiRFAlNsbTvNvNkAFssA6rjnupxjH2fGrCN01lP9QyNJzy14Rr7PTPSMQ7oBfjwgxnHOJb10AQ4ODUIGoo67Py6HVy63Ty7XT26'
        b'3cWNrsoZ+KfJpTFfOWvgxNWjkauM6PtxcldWKI36rhyclK51M7qdyZVdt5OrMktp0O3m1RisTH7oaGZn0essGGXRJbCvV/Ry8Nk9gW19Zi8PnxFQYaeGoAYFzurbq0tS'
        b'9IClYwOfUOjVJ9cGwBLnVgrqknoNybURrmy9QhlcN6fXmFybAEu7DvuAXlNyYTZQ2JxcWwBL54YYwmMvn1wLBu5bkmsrXLg+jzDfa02uhQPXo8i1DbB0aOAoY+sW99qS'
        b'a7uBa3ty7TCQ35Fci4ClTX2MklsX0etErp0H7rvg64euuMlJVcimUJzpkQdJdPOwM8HvPosF7BzrljYmqhxDOx3HqBzHqB3HqW3Hdwtt65IbrVR2/p12ISq7ELVdmFoY'
        b'/pDHsTWplj4ziGYZez0C5Pgsge1vbPcQ4APj90FV0kOwNQoeDNHWY3nALIszA+2yGGSgG2p+HzsT9A1zLfQNFsHc0GBSmOL/dSnKgungq3z24OvTnGZdhqA+yLejW0H1'
        b'q00LuPnctfp9cwYzuNg84mlQO3QHoXbw8vVwqr5Wqi5NNcCphlqpejTVCKcaa6Xq01QTnGqqlWpAU81wqrlWqiFNtcCpfK1UI6bG+fZ9tcoXHGDTNB16pGgdc2zAC//y'
        b'LSlqhP2Ld15EmXgpHatXpbNY6/wYaysr36GaTWd3mH17hiTqa4F+vlCr3U3xff1qE/o+Rq3Vm2E28H5P2/TRolt3OSR+bAEv33Ztf4yIGeaLrPWLxI49DFqVNDXupz2D'
        b'gBoJknDfLVFecY5CIfJML1VUVMnKFTkl+aRXl8tKxIPKDLrwyiJ4kUygRxLntTRXUVosq2Cis5IIl8WlZC8mibApK6tggrxSzMshgUfLyXSXWLdHPye/Sq4gezR7DDWn'
        b'dKulHhN0Dydz8guqejhzS3DaPFm+vHIeTtMrw5wvKC3Pz9PTav3+MBsrgfb2+r6gu9SXjTQ/Fzc8DzeeDt0DbawJtoHFdWN/WN1l+nSSTU9rkk1fazpNb7m+ZpJtSOog'
        b'YNCHnGGAQRNL5BVy6sOngYruexvyEkVFTkme7NVhQfubLkIDKzoQuZZQ1mxUJYFoPaOZ7bE4wzxZuXj4mIRRIs1eYQZFWlRZRlyqw0T58kJ5xTBopYO5IG+tnw8Srvcl'
        b'XODbI/FQIsopLivK8RmOldGivCL8yDwaFHfEoK8auRm+TZi7Is8ULK6YJVnJf9AiIb/XIlhgmfihsfFTRMU5ubJikSc+1Q7JKvYdEuyUCoViWC4Gs07b1jNQqymGYV7D'
        b'CP5oIkTJFECKUJnol9wfOpdpFvz1Z+bkFZFgt5QnGgsZf9wjgMZW5hbL8jVf92Aq6fhYWsKEzcWUKGYsvmZaStMnDN/GiRX9wYxzNM2cK6tYIJOViIJFnvlMvFMx7V7C'
        b'R6xoX8fANDtzJZLna15Y0O+9sL7eRBM0VnMlKpcVyhW4hXEvhjs7Kk4SUaXmtVWWkOCtvwOD+6Jnlykzs24yzhy4jo0DoCw7+cziWaCS+Geh3RmSPldSTeyOdBowMDkd'
        b'NTDBQdCm5Ela3qRoXaSRGYG0oUTbp1uCiz7pxG117P0FIlA5DifCm2iN2/BU+0iSfZ2Ttagm+KDDZUbomN9sBgagygg8sQ0AID3bqNMlkCGrh07kD0uVmTtqm03nsAYx'
        b'C9tgtSFsmAZrKdnufF1w4E07AETZRnsUi0BlIGmCSy5gWLKJ3plapBZ6wJVomz7c7Z1Eae300QciGzeympN8ccViQMNITsWlhyGFqsksnTXcIkFb0JahHF42hEdhcwil'
        b'emaRIXge6QmAWXbypYI8UEmMMM6SYRn0TJD4BqGVvswGdS2S12CzIapGJxVyu5UxHAXxQXj7m7x1H0tN2E5GOvcencjevOGRw4X6/K/agko+v3Yf/CFmYaIqYUP66hS9'
        b'GvjbpW3Pufrir4/yb3CXNn+u7+G5e3ZX2BtrvXu9zhXOH89+46vJu/8kkX7vu+O2/Hyiek3wu3ee7IkP+vBPHz25f7JrVW5dbnP9J5sO3orcIT/mX2u3c6lb/YF4xZ2q'
        b'sxcOzv3ol/bYgvUfPFlx+fGWCmHC9sTrKRHL7ty+xvIttV01JmTtbrEBswEFNcOVmonDvknDMCmZNoQn4FWaZS5sRM2D92zI4FW6Z8MGXaNzcVVolzslQgJ4DsgdDzii'
        b'Oi46B/dwGBDgDaihENbMnzkwCdk/A2kFLzI4TleloA9IEJ0x1IGn2UFwO6yjk3mmqC1NM0FqG8Ch06Nz0VU6eZpvAk/1T/Sh5ulcMtEHq9EFWgfU4Ae3wJp0p/5p3IFJ'
        b'3Fn5NEsh2o0uYwpHRJp5x4E5R9Q8hZkTPFWB3mI0ep+58Di6gC4r6OQ0TkimKr6PDkiBa3XhweSl/2M7l8IOmfcpFIPhlqwZjN6HC0cBF/eGvEbx0RK1cwhBSurmW9VW'
        b'7F2xfYWa79HodIfvTbGVJqptEjoECV2ufgRbyYlm6rT2VDFR/6Lu8H1otkS1TVKHIAkblg2ZjcKjb6qdggjeEkNz+fblar57o/kdvhfNHK+2mdghmKgJdrNfinPqMzkX'
        b'bV+0c7wSU3VjAgiqbaI7BNH37Bxpltci7iQ+6dDgoHYK+P2sLm613E/MRC/GR2klExHnyeECOVwkh0vkcJkcrvy+619/ZJQh7n8jvCExVhQVpMv67TnxMx3FYmWwSHCU'
        b'jNeKP0ex2HQCQKvh2P8MGqqoD8eoX7EcCQBnoAp9+DeTcRW0YIwYtbZPNxwGaek/h4YqZLg0mq2leL46n9MInwf7+XQYwidVrga4/O+AjfpU0VfnbibhbgDXyJHhrk/z'
        b'e6ER/xv2uLOxmvrqnM3CnD3uxzeavm86w6Etw6GWovtfclfYxx3WXV+duxzSbh2svnbzHNB5c4bCfSn+axaL+t5vn9b56nzmD36/NmRKUktd/W8560f66lNhX52zwhc5'
        b'w++1XxXW4kzMppPBzLRwv79iah5HixcCg04dFmnAS30tv2MdaoGTgBz6NOglCXlpXG1SYNTvhaz7v/RCfsqzGMYGj8rPJzGYSmQLtOUDf2OvFI0pDltMTGYyAZKTn4/t'
        b'A2xl5GgMThpUiUTOkIgKy0sry5g5kBxRXum8XHlJDon69AJJLKhe/eBxXhKRlzbsHb6myHo4U25p6VzCKpmnoSYRw0bForLXmDbof1CEKLN0HjE+mekcEkFEgzmXk1ta'
        b'ycSYIhIgyx+pbci/+NJykYw0Sb68oAAbS7inYsy4wZXStDeNO4WbrVATH2UYC4r8w1ZhXk4JNQpfNiMQEKplB4s8S8toTK3ikS1i7XZlrL0XOgiRZ1RuuSyvqKSypFCh'
        b'mR6gUVKGZXRADhQKeWEJFQVf2iZahDWR1kRy7VrJsaWMreJhqfZZwAH0JYeO7jeEyZMCxBIyASfKl+VWkOfgHHnYRpWTi7yRbHcqlXJaXiGroG0XPvoVZCaeeGnTCb+h'
        b'n4pcpoh4ZZnDvMorNASYdqcp/RMJnpmlxcVk8qBULPLymkdmZ3B1Fnl5jTjNQ2s8iCKTNEByIm7eEh+/BDwulbwOaQasTzMXUKqgFdYA+L1SefJxMqW1P1dfUUr/NAf9'
        b'fEtz58jyKkT0DQ7/DWSmhYf6B2gmW8lcKvN1+r4aG4O87iOGTDdVlcrzZP0CHy0rlhUWkHxi0cyAwDdfhWSg5jVWypjqyEsoo+Srj41NSZk+ndRsuDh05F9ZzqJ5NIqd'
        b'rJwMfBLRPNzO/ZMqWgwFvpwhzeshIBqD3xdJGTzFxnwtfn1fyrBsMepfNK4k+fYJDfz4IP8RHz8I56BvwlHrM8Gp+IssUcgZpkoLhn1qTv4cLBm0PUgBGsovZyE5H75v'
        b'HH6qchARBZ1rlecVVcgLSVUUeUXF6AbuyYvFL36zI9L0EWG5yayQVeLOtZ8AlmC5SNNEuIeah7+4uMk+WTkVuTIyf50/AiUsLkxIrOLKeXNlRcO3v48oaEg2+rScyoLF'
        b'lRUyPHKQOJKiKaXlCsrUCDSCI0RRlQVFstxK8unhAlGVFaVkfJs7QoGQCFFiSb68So6FubgYF5g8T5FTsVgxpOYjlA4djuXXb6Cw4cjItdia93pshQ9H7/XaZTRtyIGm'
        b'/52WHzYxi5FkMtE8hO/XlkTt6heU49p4krbt5yknd3FloXhk8dMuLgpzG1kAB2UMGD1STixmJX45I4vUYDKhI5EJfRkZLBT99XsJjXDtbCNWbfQgYsPUa8QBTYPDgns4'
        b'zRnVB7BOivvWvq7cM5MZY0ccsAdgXiJEMfhCxFxhHcdTii9lJfh/LOYiMgaFj9jlagHEDCYTOIRM4EvJUCwZZsiYEpXlkxgr8pycWYF/yXgTMmKxfuwZpmjcZNpTkwSR'
        b'J/7INSKOX/vIzVBZjlXkPDxaxGjOJCIt3S5ucobIcyo6VlSOP1LMS/DIrGjB3gwQ60/WMNVHSjG3slzxIlMvU/dGUi+pKvnqml+/ihY1aM3o1XQYCuQTIUolP6KZgf5v'
        b'vnqxQKZYIC028tvoQwjSqJCaa2KMv0wOKHwQLkJ+cMYX843ciyXIystL/OLLcyrxodjXL16OtbuRey2afeS+itAZuX8iDxi5g3rZk3GvFFeElTDc94/cNVHesM6WPzwb'
        b'IzUe1mJlsgqiWZBfrGCFvlS/yy1dGCEiexSw/lRAtFacgNt85JdKChFcJqZUTrGIXLy0RJ68gnyQ+PhSdY8BoyI5mRNKWEL0dJ+ggNBQLGkj80RwoDBD5OelElmQg2sb'
        b'jzuVl2WiSFL4DZEf0czQkTNqujlNF/cyie7DuIoQReMzRhOeGRj20vz9nzYtMnhN+KXt3YecpSnJvJ+RO2uCl4VVtOioVPx6Ru4Rc+V5mGBiDH70MF/k7wSz1qzL7ljA'
        b'doji0H2ZxcJFyYxTDjqyjGwA34y2uC/z0wIemQ+v0ULRmVwvC8DABZ8y1WEgWtBmK7SNQUPhpqF1BA1l1gJm7ZdvZTWaNY0sfNpNM7VjPHUS4DFUw8TFBrYOvnArvMIE'
        b'9WpF54OkyWgLux+AgqJMTYQ7KLFb8cvkk1m9POCfs2TepAgmhgtsDYU7vXHmJBr1ahuqgaeTUhjEY4BaYU0GWOhTGqxfCC/AwxSPISgqjf2OAdBnwI33GXzELKGGo/XR'
        b'L4IbZybAfXaEVgKzoKWNb4y2wHojMVwDm+iKivx7r+lsBZsFwPrGwN3p11NRpNmBcYdnj/YYFyzesXrTnvU7DitnP/S3WJf3btR58YNP4yJitz2Q/Lr98ft7BXsFpysi'
        b'5IWFVVXja/yq/6yKN69b/Mekr3xOjVHZvjvpnKXr3rqnPFBvanD21KV/evww6v2xH9x7buHm5Jm6vunvPy7ZfPqzSYrcvV5fVy68+c3dH6dHTJh+zk18v6y87tcgrxOp'
        b'prPKv//rmhlLrh4znTTRJ3FSgdMC6ScmB7fcLK+yeZo0dsnV8/V1PXaX6+7vsZvitOMrVcmPJ75858/LM84cDzANW6azYLRP9Nqawv33Tf+5sXe95XfQZW7W49Tp78Y1'
        b'b90qPLh4qnFIV9yzoge/bf73t6ZZZ2LHBbmL9ejq5ZhIuHaQyzxqg00+o2IZsIDm8DKNwzwXrkbnqMf8jUq6sumXSxwDNqYlwtNcoFPMNol1DkY3mVXTY7Da50UUZbgX'
        b'nteLhNueEKhv/K5XpmtWJgctS8JbtkNWJu1hNXVLcYc70FktNOU+KOVx8CJFU4Zr0SEar2YGXA1vKYgU+HiSrGgbcfnYmYJqObAFnU2gAIy4Jo350uREFmDHo5MZLK83'
        b'k8Sm/8sojiTCr2jAA36IS6dR/5x3nxN8oiZuaboDEEnuOPo3zifhZmzrKlR8l25bjy4PzzojghbqqqxqkLRw7loHd3t4N2W28Fvy20Jbi9uD2qM7Qid2hqaoQlNu56lD'
        b'M9Q+mR0eWXXcuin1Rl22jkqd+rGdthKVrWR7bJelg9JVZelO6XrVkduHI+oj9vdn+JqsTE5Q20R2CCJJXLg3Gkd3WIXUcrr4VnX5nQ6+KvzH96WQzp223ipbb7W1pIV3'
        b'xzrkcwevDu9UtUNahzCtl82xDOj2H93m2uEf186/4x9H3BqoAy5fJfTp1eGY+3QJfGpjOwWuKoGrMpN6Q/ioyF9IC1ctCHn+RBfYuT0CLEzHwbsxRu3g3yH0/7mXgxN+'
        b'fqIHhE74nrlPt41HI0dtI+kQSMg9c5+fKGwvDLSKEQOk7xjLBkisHzOBgwL1YiI4KIKHz99h68cKOe8Y6sXyOe/weficWXU1ZVZdB1YVCATaa3nyDhGCgWXXlwrBHI4W'
        b'GuYkWxYr4BnAh9fZWE9iXQ0fyYNi6HM1kTx41aBaRwMm/T+P5lH+LRgSrc/xheHNjRneFloSZ817i1iR2cWlhiuYgJq6y1CdopKAW23hAvxVowOohbUM7hYx7r7UvXIl'
        b'PAtvGXIAPMYDU8HUpTMZyK82uCY2kynIQtfRCReALsJdbvRZR72J1256vK5/ju2cMW8wAD9idEYWFAyb0UYdXHwvkKHWVPqE4nAuTj8kwBwTb154voLx23XSBUagzURf'
        b'lG1ktDCN8bH9Wyrx230wR68s2+ir8ZaM46bYmyS257Fwol5FApPzL5ZGQAge2JmkZ0t8PUqYnDFGJLE6Tw8n8gKqmJzNRsRFV+hlapZtpB6jYHKeNSSoR11WxmbZEruJ'
        b'oUziKSvCUrsXYUkvsgIw0Ffn4a7QzPT0dPyCYmEr3AngqgrYQO+h62PQ1iB/f4J0h44p0GqAVsErGVRLcEX7kjPTAYGNOQFrJfhOCGpmMHHPTcjK1HICRlediR/wKnia'
        b'tlfVonlBjBNwqh1xAz42ifFsPRoMz2QSRzw34ASc5vNo6jK0D90I4oIyC+qBvXoqA7a1E15FzcSnF96CN4hTL9Y66ijLEwOytNx30fr5bgBeCmHcd/FgFZGZLuKQEcXS'
        b'YKkObBiTRlUVL1hHUNK0XXd5cCM7CR2ewvjX0mghznpYU2pzMMnOLq62N2OalG9NvL6fy9k40cN7kQa4cSXcbZpJWhSgNfA4vAJy0MEgSuSGvQB4gnuTjSOzx1Y6ypn8'
        b'YYtRXWY6VIoBiFgGT0YaoobR6BKtzhvhaJvCOAg3FxuL3mm4CaCb6FSlPNquhKsgq5d6AeEHs95PRf5m9mMSw67dWbdjT4aV0/jVLiva6z+rNlDM9Zv812rFcYc20fgj'
        b'K9bfXZF94A86XzckJRyfZn/rWeDPS56zPq5tN7Jo9RX3Olo+vzyv6s9o/8J/cxOOra1s/OuUf/zTsFV+zKrFSuC92GPVHq+fZqZxkuxPJ4EF3xxOlznWrDoV+KnZ0XE7'
        b'30rP+5fU7wqQBuxlt9wQGCqm3H6v+sjZoOffTSl4eKXrM4lv7pVflnwiCw/ZW+Oytst/yej6yveKhe6L3vzm6MXwKce/zZoxIUuHN/mNr7tCvUaf/+L988sOcD5z+0eC'
        b'8JOGbVku67+48Ksgw9F68nvLP/Xm63wytsv7y0Xblqdt/HbKP+6DtAdhwU9Fwom/NJ279zw4LkAQ9ZW4yv/Qu2ePTN28wmXJ3LSozJvd61bmldy52NIWW1RX+nyR629n'
        b'l3l/NqnwT3/f+K3n2N9+S5aFXMupVa8J2RdxkBV/7luH1p+5fgW7l/6o/nbrUfuq+hK/hSu/U1sbP6/4zK5JLKD7peA+rCA0YrXEM/oFxWSIVhKaTv0eV6B1cLU31XXw'
        b'LT10fRk6yybbv9AJqiYlw7XwHNZ8k1mA64Q2Y8X7IDwaSF18A9A+2NofyEEPNsOrcCV7EQdd1wShnZWuHWMdKzhnWbB1chDdwFYKN8BVQ9ECiSupKA6tD+DpJ8gYP+GL'
        b'uP/c3+eii85OmciCSn14nNm5duQNtIN66Pr4Cqw0DrorIBNf3g8eXozLJRhpb7Qj2+z0sZZFaj4J9zIbGR9i4mt6mMf4EKMzqJmJGqiER9Atbf9dZuuchycHnoZ1YbR5'
        b'nOFb8Eafiimtglexhjk9kvpIl5Sj49JBeEqj0FUTuIYTPRNeZOLq3LARa0MbrUDHqeOuLYdWLzd3kVQbaUksMVnGifU31uyvgyfG93vsanbOoQ1wKwftlNhS7ddoEjo8'
        b'4InLDgxmwUNoz0LGPXsdujpWqu2Iuww2skvRoXFM3beiYxItF2zN3j2rcg48i/bCc0x4kJUTdbQ3MvZvQDREZ4g6uwbdFOu9sqahx6ibWtu7SNjyxWYDKoZidr48jwka'
        b'3MTWAC45glG2tTwSkNCwS+TaKfJXifwZkJdO0ejaBBKUY+GBcSTKh71Iabl/RqNT/aza+Ht+YSTQR/OK2rg6T+UUlY23SiC5J3BkHDiV5ScXNCzoEtp2CR2UVvWmuHSn'
        b'0AcrfC1Y6wu+IxzXJrgjjGsXEJz7rJPTG6a3sNTCwE5huEoY3maupigyh03rTZlCjTlqoX+LRQu/QxhCbpjUm2jif0xSC/1a2C2cDmEwcX1K6LQLUNkFDCbVFt0W0yGM'
        b'pPcPp9SnqIVenUJ/lZC44woZd1xh+FAGI9us7wiT2uOHTS9qT+iMnayKndwZO0sVO6tjdqE6tuh1ctoz9Z7VMKsF1yCsUzhOhZsE1zISt1cDXzntqL2KhDqxpy2o+SMV'
        b'iKX7FE2U5Y2sDqHXSImYSJeQxGXpDbH1t3oMbD2tn4UCocP2qroitbXHD2G2luJeU+AU0RvPAo7Oh4vqi5RL1A5BtYbdfOE9V/eTExsmjtjOlPIIL4dWq9MtVOVGnIGF'
        b'EZ3CSJWQOAMTwKcBWegTiV5zfR/Mnr6b9TOLAfYavR/y9d1CsVy5b0/pxSqQfa3Ri9E0Xr7dkUbT+P0P4WvOQEC0Z3GOr+nDmkYsg8dgSFS0/pi8NIQLTwONztW4WJHo'
        b'aDr9sOgD8Q3+B7Do5T8M1bpfjHGgm1pJYhjB9b7wqncC1ovSE/CwhYcm2IT2umclwDOoWuIr1gEJaL1umUM2o/jdgBvQaqycNcPj4+geZ04xC66ugpsYVfysCTrnrUuA'
        b'reH+hWCh2XiqlfnhDnCDdxobsDLgRbQLoH0pCfI/9YziKL7Bd1v39a6b1GoA/c1uSnPnWpqbbz+SetbX5NeVD/7xRodPeH5Wg8H7X1mVWU44MuHbHFvL3DmBXy989ucv'
        b'bn44bvHKeV69274aX7CT/eGDcMNGm8pTqC5rvs/RZUl2XqqGqRd9PvmhMu6pzSllxF9ufPfT6Pf/PK7TqDif//68o41v2N5VLv7LJu8uY9blzXUflW059b0iRH0jW7a5'
        b'TMozKzU7u7FM/5d3O95769cjE09d3Hp3w6rezj8+ur/+srnuN8JfvjtSrxCvq7HKXms156vHco/vm77++/J/FrkV6WbWIXPF+lrz+AfffBR0O6B7AktvSdiJu2qxKTNI'
        b'3YS70BHvBLQWbafxprhhLGy+nIVH6ShqZo9HyRoJ1gCPpmp8LvVQDXtZELrJQGycD8Aj+O48MkbgoYQNdFLZdnhI20DHSBfcuqvJCC7xTaR3DUvhatTCRjfgzQgGZ2Mv'
        b'asVv8AK6uEAzX6LvhxXYk2x4lK8ZRufP50klBNthY7IvCxiiQzqRbFSHrsPLdIhG22egy6I88hS/NB82GeS9bAOYQXQX2gFX04Ba8FYBHkf7A2phlaCFDsJh8IYAXkCr'
        b'MP+JaAtWkXRmsV0A3MMwdwnL3CVvAj6BdeREH18xG5iiwxy4Dl5C55iB9uw8rMM0wiYpUSP8UnlAZyzbGp9v0GBNolN8KTyzNFcju/oCNmwIhdfoCD4pG12BO8ox61s0'
        b'jRfNFlpUMoSPhEEl0a+Cjfs0LIJSuRnuZHSj1hy0PwKrdhpkDB08vEvQ1qn/NSJi30wA0zXpUniv/q5JkVPFRNr6ETADdJITEFjtDdsetnf89vFK17t8j8bocxObJp5L'
        b'aUppc70rmdAe/V7S20m3K+7GZn1u49ThHKa2CScIE7iXNqo32m+CB3e+9d6I7RE7x3byPVV8z0aru3z/bhsnpWsjp/ENtU1EbUyXu/fJuQ1zT8yrN6jj1uXj3pqUVWY1'
        b'Bn8i9O/lAI/gewLrvYnbE3dL79naHw6rDzs8vn58o+tdW78uoc1hvXo9peCAyRAq3fZOSueTHg0eJyUNksaKliy1c0Rb7F37qPaMLjuHwwn1CcqsA6nPOMAhmtVhH/WQ'
        b'POZL+yh8+pOCbNh8x8cizoD3rgEvjq+vHRu5/MnvjgBMezORkAfhGQzT2o5cLTC1JSIWS0iCIL9ORC8aWEnMpdMTTMgOGsZDr3/QYtPzVLHFUGQDAxbQhjd4hX3+p1g0'
        b'VmOFbJ6CwSd41Fctsfn/cO5SqxVJu60c+o9pzXOkNftde53IcPomi+IYPORyjc0eGQETywZOQ0zdota8tzPf57cndo+yU3pf5V/NbNN/P+YJh2UyiYBijI9kPeN4GLs/'
        b'5tEELj59mMHqAzgIJQAH4RTgwNal28yXAUGwDa2WDgAchBCAgzAKcMC37TZz7xIE4BR+UHXMQMp4khLJokmaYv6kWKA2UkJfyiM9zHsvYJuksOoVrfyH9KzH2nZfbMOo'
        b'TqcwlVNYm77KKbrTKUHllKB2SlLbSXscnBtGd7qMVrmMbnNXuUR1ukxUuUxUuySqHZIeclj2UtZjwBImsx5yCK1nOpUsY58ngBwf65KUXpryrIQz2tj+URULP7/e5a6x'
        b'wzO2wNj7MQeYOD4kZwNxGv2zwxT9NioP4B6xxdiGjQfqNYZiVqr8DzlpLEUcfh3xyw/Ltn+cuibS7A+Fq9Ydf7JCbnjmk563Vm9c4Dd+zTN9hxty/u6uGjlcWXg/pneH'
        b'yWdv9hyz0xvz5dJbP1Y9f9Oq5C+W53trlDuS0lf0qg3fXhUovn4J/KJceFV34ZLwKarEq5/OOfvpv6Z9Ns345uOt8VHytGtLLgV5rDQ8dFi6XHfR4zPlDWOCz81/K35M'
        b'Z0TAxUOl5pcPnJI6PZXH5u3r2FUQfHLXpxffd95scirDZCz77wGd/Iz6d/4VlXOuauuxcUW/hPK7/vbTPcM5QecezZDd/uBB8vwP5565Orb7qEncR47f/diaWNux42xR'
        b'XNixooPvhhfAd/50+o/LfmDfL6/9OXlXm3J82j4H6NVR/P5H6i0WM9Lbj+kVJu+bmfHX/a4pOl8eq97iIkvbuXrZxT/G17UE3bx9bym0in388eUx3SXX8sKW9Tzf8DP3'
        b'e+elv+ref3vOh3JrMecJUWvs4TV4GtVgW44VLgsjbf5WATOQrYTnIzUrHrCFpR06Eh6No9ZeRAw82b94gYf7wwMLGMzqxZmlYtehn6DeSw//Nz74/6CLcGUGtkj674W+'
        b'Ykiv0aM3e3ZxaU7+7NmL+8/oiDcOy+qveMQLBsaWvVxdfetuU4vawJoFdU6bltYrlIHKnIaQ/YsbJ+1b0eraUt7m1FrZNql14QXft2NvW6CEO4HJnwtt6gLrcupD9usr'
        b'k7AF1WKNjcCOsakq69SOjKyOyVNUGVPvWE/93EqktNhZ0mHmSqL2TWP1GgALQW3Udsvq6GfB5vquPwB8eObpoe/zDODDD1mssfo2tVOeAPzzw3KWq75NndUTgH96U1nA'
        b'wOwZu5yr7/0MDByf0iP+ZA3MeunN3gp9IHRvNFRZB1UbPdXR0xc+syrn6Nvh7Pj4lB575+hSYhmUzMDxET1SYg/pzee9UUKWfiKr28LxmFGHT7xaNFFtkdBhlMCMmpui'
        b'hLF64B09fqytZjnDvoc9e/Z/uHzxf0deiOKaPXhhbLjhxZxNhpc+GSEqmyIaMNZaAItlRhZHmAPxTTN7Hdc0ohmc0okA1wyjeBz5b93tPAUJcDa14w+yzYkGMF245sux'
        b'd2eYva2vWxa+faqn819vHvzwGv/X59+/G7Mw8Xic2UffSBNu58VtCh51/uvbmcqEdzPvnrdKfCPO28bn14qA2c92jDt3fveW32Z/+l1h8+IPfv2i7B9FV5+ne+wd13w2'
        b'SPz17fG6Jm9ebrrNCb2a/4Vs7/qruR48QbCRRKfMc9Lb3093yV4b4F6Xu3601TTn3C3GBsWtyGGD+sgPV9p/KNnmfOjL4xt9P7iWj40L0ozwKDxBJuA2ppF19c3SCHhV'
        b'FxjC82zUGCmlM1HoAlyP9knTfFAryZXmA6+hkwSy/QYHNqDLgJIpNyNAe3Ab2kbmoOCWCLgDbtMFJhYch+l6FB89IAtdkSameKXoAh0rdJzL1guH254QCzDGNxTV+OkA'
        b'VibILkBHYc1MmhwY5uqdxAMsKSiBzahuArrOAB8ecIV1JPLGVvwgtDkAncAWh5iNauExdJGp0iW4Eo9o/Vms4Hb8nSWyYcs81EZNpuAQuFVKhz7Sk55EdSk8YII2cVJn'
        b'FVJe5QJ4RLPVgcsqh7XwMFo3V4P0h05HY3Y2SZi9At7jeMCIz8YGRq2AMWg2wxvoCMRWgaSM5kCHcnjAAF5gw4uJoXQVGjVbwSs4x3kjWL1gfiW6MN9ofiULWBvgx2zj'
        b'wM1oDdqoqYg8Q0pDPNO6XEZtAL+afWxMfxWXkoLrM+Fp0u5+Uh+v8WgTqTHaRhJ0ga0rF65ZAteIPV95OPj/cnTQ+u496TgR2ffvJSPFIAdVvUGewzPw4TfcBzy2ATx+'
        b'l7Gg09hBZexwYKHa2HNlfBfXYEPyquQOc6dj4Xe5ks+4xvjvC67jl1yPL7k+X3BdnunMMOPhrnXg+JQeexeKgJFgZZrWVJNjD6dYVtLDJd5MPbyKyrJiWQ+3WK6o6OGS'
        b'2aMebmkZvs1RVJT38HIXVcgUPdzc0tLiHo68pKKHV4B7LfxTTjY/kuDqZZUVPZy8ovIeTml5fo9Ogby4QoYv5uWU9XAWy8t6eDmKPLm8h1MkW4izYPIGckUfBEuPTlll'
        b'brE8r0eXgbFR9BgqiuQFFbNl5eWl5T3GZTnlCtlsuaKU+Gf0GFeW5BXlyEtk+bNlC/N69GfPVsgw97Nn9+gw/gwDY4GCrMxmv+yfSDTwIuiBRBFVpJF38NtvZJ3anMXK'
        b'55BeePCxlx5fp08mg9fbujpR1uBta8MoZ85PegXEJSmvyLfHbPZszblmLPjJRnMtKsvJm5tTKNNA/eTky/JTxXrUrurRnT07p7gYD32Ud2J59Rjg9iyvUCyQVxT16BSX'
        b'5uUUK3qMMoh3xDxZHGnL8ki25vUzgsAoLGPnleZXFsvGl8ezGedHGne2l8NisR7iqnF7TYCh8UrdR9xiM5agd5YT0Dfv1LNV6dnWJd3V8+iQjH/bHXmqJEldembdBlYd'
        b'1kFqg+AObnA3MKsVfgJs6KP+D/VL0+A='
    ))))
