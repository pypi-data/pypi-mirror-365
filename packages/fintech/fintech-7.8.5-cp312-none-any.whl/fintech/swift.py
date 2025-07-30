
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
        b'eJzVfAdcVMfe6DnbKEvvZYGls/TeURBBOihFxUJdii4L7rL2gpVVREBUFiws1lVQF7Fg15nkxnw3hRWNKzEJ6Tc35WJienLzZs4BBTX3++77fe9773Fvxjkz85/5z7/P'
        b'mf/Zj4lJf8zxf79bgooOopwoJCqJQrKc3EIUMoTMJXrEC3/ljF6Srkn0ypkMQsjuHe9ZTkj1FjBQC6ecNTFmE4medYRPYUhiFVuvSsD5RaifOzc1OY9fU1suEwn5tRX8'
        b'+iohP2dVfVWtmJ9cLa4XllXx60rKlpZUCv319fOqqqUTY8uFFdVioZRfIROX1VfXiqX8+lo0VCIV8sfnFEqlCEzqr1/mMAlzR/QfF292CBWNRCPZyGhkNrIa2Y2cRp1G'
        b'3Ua9Rv1GbqNBo2GjUaNxo0mjaaNZo3mjRaNlo1WjdaNNo22jXaN9I6/RoYOQ8+TWcjO5rlxHbiM3lLPkxnJ9ubncQK4nt5QTcqbcRG4hZ8uN5LZyKzlXbifnyBlyUm4v'
        b'd5CbVjgi8uquc2QQ23kTpFvnpEcwiLWOE8+o7jRRJ4n1juudcgnXl7SuIFYy5xMrSERSRlbZZDaZov/M8WZZFGdXEQKdLJEuqpcWMwjcxuQW+y4Q2hAyD/QALxmCq7AJ'
        b'bs/OmA3lsBnegJeyBbA5NT/Hj0N4JrHgTbg3RkDK7DFypeCGVKibmgl3wZ2ZcCdJ6KcygBr971wZOQkFswkUGlCx17QRoYEoQyBqsRE9dBD19BDVuIhqhohSxohmpoim'
        b'5hVmFH2Q4Gx/KlrrGBR9yEn0YUyiBLmeMU6f51qf0qfiP6dPBk2fj4N1CAOCqJsdUJxxM86CoBrJHCYmGv8rZrHvYHwa3fhphR5hgikpLhYZ5XPpxq83sAn0r5coqzjD'
        b'2KCQOEmI9FHzrSob1hMzIn4s93Hst4yLQY1mDwkR1q4BBwU55FFhTMQXBz8KXhYTRDdP0//WuHydtxMjZ5T8p83J4hFihJD5o46kMtiNGNUUMNvLC+4ISPGDO8DJPK+0'
        b'TNgCe+F1X/9Uv7RMkhAb68UBxcop/GBNbLkU84NJ8QPzgqhgPqU48/8cxXVeoDiXpvjdCCOCRxDz7COKDdQWBfQ+mbCDh/a5E56C233S0b/bM2anpPqm5hPB6bmWYE8e'
        b'aAJ7iUq2Duy2hWqZFQIBPXAf3BYCLqEFwEmCu3gZOAQGZJaoyxVsgWdCwHncc5CA7ZlLwaUZMiyg4Ohsv5BgXNlHLCovA/vm083H5hjCdnY4RLLrT/hbgkMUqoH+XMIC'
        b'/XPSpFi0xSqAZvl1KzPCjSBs3mMXr+WsW0dU6wSMMqUrUU+b/+/7/yP24MbtPe397avCXJk2RwMr9ocEWjzeG/9zvOnxrM+8wzkcxQ4P5d8tPhNZc7bp/0VZ6+KRvM1i'
        b'n/5fSk3eLPxrDiTyuHnDrx4A+159o4FsiLadoz0WH7pG31VRkfFha2lK47sfvGpQb2wO4m4bHLAljByt777CEDCe8PAmWkrAeS4iniBT5hfo743khUFYgkaWrt6KJ9Zo'
        b'QGFVEGxaA1rhDiQ9O5GIR5Gg33WWgDXC8BJIDNGIZ4UUs43f0NDwi1VshaR2tVDMr6DNtL90RXVF/bQRfcoGF5WX1AtXT6ozMHAdKn5qIB7PJAkT89awptWK2Ts2PLLi'
        b'DzlHD+ZrnGcMWyUOmSRqrewV5W2iu1Y+yvq7ViGqevksrYW9QtiWLU/SWlh3pLSlKITKGcrZimqVpWqZ2lRlp84fDBqcrS4ccogftkiQJz005ysth809hww8v8NSJ8Fi'
        b'J+CMsJeXiGTCEZ2iIolMXFQ0wi0qKhMJS8SyOtTy3E45qCjm471KjHCjMSom78gVDwpFxc8NxA+JJEmaf2hk3bS0gTvGYJMWD7lmTVEfsoy3ZGp1jR/qmv/0mE2wTSae'
        b'fpFikdnNcSEOc/2YZYyX6Wc51k8G9lCUhpJPNZQxxSYy9aboH6ozJ+kiYz1zXEOfa32qoVue19CnCDzVUE6WDDfA8/CyFWwngTyQIPwIvypwnW5vgSfhddjOTIkkiAAi'
        b'QAd2ybBhzYW71iHtCYXHKO0xmlm99vMOphQNIv5+2x6rRE+7oKmNZB4NPB54umKT+qoi2rZpXq4ipvPUrViPbVnKMz9o7+csQiL9BZGzVU/1y3sC8oktFukz8IKzT5of'
        b'lKdmZJHL2QQX9DPgQZ0CAfN5LuLYZoKFI1yaexWi2pL61ZMfKOn0paVzLI8kLO06Mtsyla5K6bCFDxInYwutDZLATm4r+6G5nSKsfdqQgbPE5JlkSfCGR9jlwtLqegk2'
        b'HRLzl0gTJU60NGHFm4KCz4Q4/YLEKReJk92/K07tHFfiCNefSZmjxkhzMpRBeI2Gi1gFLu5LZDaYbpvgNdAhrQ8PZGH/vY1FwOPIOp6hIMqEFmQkg7AZDd+5CpiHz6B4'
        b'GyyyxsNJgiF0ADsIeDLFgBpcnGJNxjKIyNHwjADtXK84yr7CPn0dPJpJMCrBXthEwN64Umr4bwtsyHhE5NFpfYVd5n/1piy1EQO2SesjMC5ieA4cI5CVv7aBGp+20J6c'
        b'ySD4o9N852bGTtOVWeDp5c4GeDyDYNT62qLJ54Nz1OjPKnhkCoMwGZ2WkZXE/30lFZ/AE6AZ7JDC82EYe7AZ9oLdBBwAjeAGBaSa60RmMIjA0Wmismliy0UUgWbBK5CG'
        b'YSOYLSZmSOhBO2ygIHLznckcBqGLIPQD9FLD6D0fAWpnqYRapLaoHNGgDu6ihs9yciXzMAemGcyf5VpULMOSC3fqoiUGZEF412BvDOjFOO0GGymQVbZu5DzMgmkGGTHE'
        b'o0hqhdLicgoAbRvsK83AatjoSg13rfIkF2ImTHvDrpfFkdEIbTMxkkpD8Pwb7GAnAc+AA7XU8B90vMhizISor3IbuUe5MiyDM22R4cfTI6aBLjN4loCDoKeKArjD9ybL'
        b'GUT8aJQoYzT/dT+KaxtWJlLjddD4/fAwPE7AywszqfF/qfEjqzDXovqYj/juJLUAbK1ZBwekBvoIf3gB3gAtZCjYRQPo1AeQIgZRPBqVIf1Q9EU+7cD7wSZ7roSSUXAc'
        b'HilEcWllADX+YEYgWYcZHdVX/mThzCCKZ3C7ELZxYX8YBoA7QQu8RjIdYCMFMRgTQiLtzhmN8nVpSv6PCIpEoWAvuMrVD8Y8Q8FCaySp51hLs2c3VGZx4UWKPXArbAOn'
        b'SBJuAmcpZai115XCgRVGeCc9Kx1Jn0A+vcXda0qleoZQjee7CbankeHIIsqptcCpqBDuMhm8iEwz7J8JT5DuuRxqnytmghYpV1KPgRQUXRxrwAkKDXAJHoL7pPXwEhf3'
        b'NoMueJ30gaccqKgkg1siNTJE9GSyl5WQcXCrC6Ue4BrcDY6gHiOSYOrFuJDxEd70pnpBH7yGOpbhTQ2CA7CX9AcnwRkKzMpcl2tYB3ayCKarAewi48ERJ2pXIqAAe7Fk'
        b'I1WoQ1ZiIwFPg85Z1K6Mi2Aj0vRQDsGoKEbRETzpCa5R05mvXI+lj02p3JFIAp6zyKKxOAAVrlLYDweMMf3OCMF1JAibEBgmRlkQSwovjvedyoJHyRDQrCcwppnICSVX'
        b'YlWN6vNcldFGx4sBhRHkWgZRNxr1RoJOdhot4v3RUWQDVtGor/yXVGSspRoFqTHkFgaRMhq1c/HSxcsyaPV3iSPlWDujdqb4JLzpRTXGG0wndzKIKjSn6Wy2Sx7VSPgm'
        b'kK1YKaP6amxFm0xpgyadQe5hEPOQ5Bb2xfW403hOTyIVWB+jRBFi/RJvqnGH3yzyAINYiSRw3QHZF7ZU44WZKaQSq2KYiK9bQqynGi1sMkgVVp+wvgCbbIYb1Vi3Oovs'
        b'wyoSJvJ2JBfSq1vUzibVWA/CRKJfpwXkUI2ro+eQ57Goh4kqjBKqV9HW4DJi+HEpVx8LhQG4PIuMF4dQFF8Dz8CNXImRIZIjU3AedCFJGlxDcR4cWAHb4QC8tAK5TyzR'
        b'CjfSJ8KfAitmhiIdQCYSC+YeYSHpAi+AQwIWhcKTWa+RB5horzEG/DfyzeqoxpXTXyeVyA2PRnyVuGiJlE018gr+Sh5lItMSsbOgMG6vBdV4xOYNUsVEBIjwrTscw1w+'
        b'5dyiNxGWiFGxV2/8HIlPLs/OkESF3tMzDOe/7QzzwqnahHg+QpqeJXNC9emwrQ40ZXvALnQoboHbUzP94XYUbVsVszzhVktqk6Ze1CGSCKw4Yx27IoI+PFRNow6RgYEV'
        b'85Jlc90JSmNmIevXlx6QBs+mw13ZqehECbcwVsGrAtqXD8CmPDCAOIfOM6ALbCPnE6DPZi7t/C5Ugy0+Xn7eUB6QBa+DHjZhUMk0Rtaxm3brcbDTGQENIEyiiWhwCm6R'
        b'YDwoZPJcWfjwyg9MrtUh/cPoxow06kBsEmi1pNiQkUHQxu2sk01IIDgPO/DDbqIEufF+mQt6WAjV89OpA0ULfj+QDloCUsFpL5KYA/fz69lG8fEUHuAU2McJCdXFoRfY'
        b'Q5SCqzIZfkEDm6uNfNDJlnqzgI65VrapLMJcwEQP1+B5KrqcscAkJBg2ZRDUoa1siSdlG/lgEFmOc85L8BmvmxCVOFLNHHikICSEi4+84BBRCbfMpoyVJRhghISAjQs4'
        b'+NxILAEq0EPhlRjuEBIOGmE3BlAQ5YGwWYZfIqGmLaAbHoSd6WkYsSyaMUZ1zMjFrtSUoWFQFRK+GCowAp2EEMjhIYqbG/JhR3oGAgiAzT6JHJLgFiIrCK+nCRh0dLMR'
        b'XkgKCV8BupBdAF1EhSHyIJRdPwA2Lg0Jh5dBA0ZzP1FZVyizwxAHwR54CTaho10mm2A5ghawnQSHYXsgHZZ31rLQJvrBXhJPQlRZT6fAnHQ8fTAv4PYscBrNcINFGMQh'
        b'2TjmSy2XkAZOhICLXKjCaysJ0QZwidoAOkcvRPROw0dEJvZXcAsJ9lsBtQzzIDwZ3pRmpKZm4jdHOyfO6l7+Au9Mf4EfQx8cE4I9kUiij4OjXl7gpJWPAK191McC7LGy'
        b'hEetwQkGAXZYmACl2WLRT3/88Udd8bgUFvjUf5QiJCjrwwIXbXyy/FJYBCsebCwmkeBegwcEFlRnCtiJTJ2hRIaN1iErcJx0Bd2eFC3m+8yDA0Z0z0XT5aTAOpLarDE8'
        b'xYAD4yA3NgSSPhIebQI3ecKzUgRBmTmoAHLSCR6h3T3ogVfhGekymT4OLK9WhpF8LJeUVjLBbifkyFbA82wqGNkB1KQzHFxLUdAdtiLLMIA6DfG0/WAPOE8G10IFbaov'
        b'wENAwTXighZkkgvX1JEL5odQWNaBDndpvf4KHBBdZ8ObJK88jA48js6xwR14rY3gLNoxH5yEG+mw6CJabTscqJfA8zi2u5HqStqDzaH0FlqBIlYKz9VzUHRQSSKdgC3l'
        b'8AKNxy5wJYGra6iPdhMB9kaSKd6gizY55+B+pJMDsmUGGP8ucHEZ6ckajyPywWm4g2tkgOw0MwZcciNTo9fSa22DSkSyAWMJCpyYRmBzGhmRArdTfWaVEPfAc9gLuYAt'
        b'SIAT4FEZvYET9rBTuoxaC1xE0UQb6Qg2gh00KnvhVhTd69Oc240i6Bto71fiaVVSu4BeLtXHNIPyHDJwxmzKDGTDnfYbUPzdjhTJl/CtgyfpyS7ElIImj2XG+suWkwQL'
        b'niHR0WET7KNgzFxdJnYliCNT4UEGjd2+VaDhmUwlofUF4AS4SYewDQvhkWfIbQOXSf6ieVQX7DbFxJgQOdCwnPSZZUt1BbOB4qnIISuzh3RaD88KWBSldGwlk3gJB2Ez'
        b'4mZbCW2GD4aB3TQ3zWxpZgaupHQdkWmvB2iytYaXkMuWISsBrpBgI9w1nXITxeBSMWgCx8HuFfCiAdiO1ArKSdAJDwoFzKwsaqOJoB9efyqVsAfsIxegiPgypVfleTOf'
        b'yd/FQpLvXEBhmwyvgoanImsOB0keEpxegRHNn9bVWVx9PXgO8Sc6JZWclYniXtxRWjdXOk7RfboojHfOgK20oCvB7pKnqo2O/ztI1zq4nyb2cdgVwNWluK2PdkL6Y7Gn'
        b'uorWzoIDBjTUGXANHCQ9QUsqtVSBZzAaZCDBXcdmO5Ge2XAXRcwZusiQGcGLVFzeHQC3kW65Mmq2ENi3FOk2Vw+H8ucSwUUyHKjMKSJl2MMtXAnS4AssiqvbwADpvxyM'
        b'Iy/3gSeeKtR2NGMKiqSbaNbtSF3NhRf0lnEIpie4wSCjJMhf4B5rM9hL9aDAzasGXCWjjZFzwovZCeFhKWiuo88UZ5BjOEcKbMbB4pIqEY51xigyR2S4mUB6TEd08sNL'
        b'yUGXHmiC7aBlOZIvdDgGp8ORudgLO1C0tw+Z0t1zScJ1MctyFeigXOxieMAjfh1s10GRCREIdqXIcvB2+sEFWwTRATuAfOpMQeAoMpYdyPC0I1vRgfrU6CizFz13gEY9'
        b'dLzvgCrQW7UEmfrLQKmHBO0oaKHQ1vcCfc9oy16OTlBNBdRuKwqAcjJpb5ahw0sHUCK3iYnrZgAVTwmIjtIXyCg0qI9imIVf8FMKwm6gIqOhEnbIErHgJjpxYXM6coMp'
        b'mf6U0/KBzZlpfnOgPDvXyz8zDXk62JwqKEhB0cccqAZbkac9L51LSC2RQcsymZboRTtZhY4UDMzJYRDW60lzYh3oF1Okg7tWwIM1SbnIl7sSrgGwl0IoAXbMnaTFjvNI'
        b'e3gkWobf0krAIUS0JnA65TlV3QqVtBndDK7MecbaAn3SAynZJkQG6iWvGukkMmzL0v39vNPwzs6wCOMCpkgfHqMGIMIfNkReWWYBm3EEQqJoUsFA9uE8OEcbwX4LXRRn'
        b'pvimZfvNBMc4BDcdqZqlgNpmNti0/qlmujqRzoI8Ok5TgEag9EnLTPfDi8LNJllswgwcYgI1F2yp/shhHVPqi2J/m/fjm/PTsy0STL7pPLTujRvbFs3TLpKZjpFnDv9E'
        b'JA0pRj8efY+78Gj7/Yflxk3O8jjr2vY3NjZ9yF+cEmv6x7btN8Efxb+R6xcNvHd18EhJ+xenz5w6u3jR/d9fjysvqdnsMHb6HzvZGcEl92290md/mVEICtaUcN/PmVNp'
        b'GPP92cEbryav9/z9j4ObUmzXCf1Oq5i9vz5S/uxVWJ71S/gay4/3c99RpiSL3pT3ddtdcPGrYa+atyk3+eL53zI2nTkt29r7m9crnHd/YbM6xnwlo1FKidund01/fiv2'
        b'o/T0XSn63rtVHPEy+QKXb3iDiyvNH1mo+rOY+a9v9DY/S546vPL6qf+Qe3/k8cprsrVWTYsZIdM+qdz02zXGpehXDrp9s7TuxPKyLy+EzP+DmHnwKwuR1S7jcvUQf79p'
        b'6FuGq6KzHyV+8dtZ89JFqQdN1nF716/Pm7uw9a31djbmzedv9+jet6tbdGTx/NzDlyv/Mbsx/sQdbfgHx422rz90+dBNhx8KhBGn6z4qbTXzTVkaeqXY4VBI8MfW5i6H'
        b'NMvDNa9tNNfKNcn11z5PnXU85+fY+1VdLjs/v6V3d3b68RV9VZqUux5Nb5z0dYzJW+Gu91f1Z1uF18++VjljZVDv+avc5EuM9+b7fX99y53P6z+JOabeXSXd9ffbI/t+'
        b'9v/w6s5/6N/orel985Xf+gutd5X9HNZ3sUpzKuhBS5qq6tstPyztc3381yPRVzZsEkV+2uL5ybLEiuyv1nv8sNGhpimp85j49R37N3Lzwm4PLPwyJp4d1Qnfq6yJCztx'
        b'Z/O1DPd8w4MtBwzmZN7Z4qtYc9yrCXwtUk6/OeM7qzfv7P4kNcLosO+OR+uNbJcsfZw5/Irfa0ntb9V463kubJZXHv7V4Ma+Ow8+2bD28ol1sgXx773fHLR9vVngpxse'
        b'RliO5rXdPjj7qz7+GY/Bso921U9b8NGZeRlfsTdvfOt6gOD6r1W/x03/x985Zd4tgq1V5m2cY7faHSv+6qCs8jP88eKTKrO4ft4H9cc/7/i18PHBdzb9ZcfdhuvuRwYO'
        b'v3Nx9cYlR7+/M3vdsqLu+N/SXMqShnuF7+/TmRWe0/v4quVpxvetfe9q43piH/xyztpo8cd/a4Tvh/z4ptP3ujZvbz0mMHyCXTd7LTo6NflmoTAatviKqtCBAfQicz8v'
        b'geoGW5L4Pv4Rc1J9vQX+aADcjrSMz1q8soa+9NkP9sFe2PTsTgfcBL0k6NeFm59Q6n58hpvPetDqj8L17b4kwQG7GH5FsInq5MHNYGO6b3qOVwrSamQq0MqrFoEj1HUR'
        b'UFeD/vRSoEzN9M7UITgsBvKY4OQTfACGAyGg3yfF1xvNidzPTrDJArYwCfMYJoocD7s+oa8LnGLSs/1Igg27GcvJBNDGoOaFG9NifNzRaQHuQMdBDuhjhIAjcB+F0DzY'
        b'By7AJtAXm+mbCneh7lCG0TKgeoIPZchEbjRIx9eE6an42AF36iBilTPQkpvXPsFxDuhOAw0+3hJ4dWK7ejEM0A1QiEzNAI66JKUjo4hcgF+arwy2ozOdGRxkwkZvcFNg'
        b'+9ydwv9sIcUnB/5zfw0Tf/S9hhl9j1AvKRFLS+hsiNUvaaNuOcZY1C3Hk5kMwta9laW1tldkaKwFqGZho+ANWXhond2VJT3WKlNVkJLXymqd12aEB6W0rX9g7aex9rtn'
        b'HTDq7t06U2HTlqX1wBXb9mytpa3Cq23xA0t/jaW/SnrPMmTU0UUZ1FmpLFGWKpaiQaZts56OHuMQPMfuiM4IZej+uNaZWjtHxbJOz9ZErb1Td3RntLJs/3RVkCp4yN6/'
        b'dea7zu4KtpbvrixVLlPq0VU0J1W15ytndsVpQyIVM5WOd3mBWgcXZXnXIm1gGGqwv8vz0zq6Kuu7atTsQYtzhlo3gSrvcKZaOFh/rkbL4yttO7Mf8II1vGB12H1e1ARw'
        b'QCgCtrvL851o8A9BDbZd2fhZpHEIxqBWnRkPeAEaXoCafZ8XPj7yQ/8gtXvvkmejMbRPIHq26spAz92LOhcdKBr1DkAtll3pY0aEg2t3RmfGGEF6J5DaxJTHTNI7lXxC'
        b'kA5p5Kibp8q9J13trnGLUCRpnVyVqV0btHw35fweYzVjmB+ilmn4sff4IaN02wN+uIYfrpbd58eNpZKEi8dYBknwXRADC9oMxhhsO7NWzpgB4erZakzt/UA2IryX71mj'
        b'k0Zq6bBXjMbCvTVJEaJkP7S265SpLNUeJ53w1lmKgk4DZb7GxkfrHdBpPGLrpbXhUW1FwzZhgxYam7h7NmFjhoSDL9oQkiG9tulDHtEa8+hR3/hbFreqbztpfGcjvlu1'
        b'ZSit71oIsKgI2oqGvKZpLKchjis5nbEP7H009j6q5Hv2IdqApFvld6Ju12oCCsYXL9DY+I7pEo4uimStg/PTwlWR8lwxwosbwVJAdyvzFFlP/5kAe+xgTFGCT9g7dHt2'
        b'eirdlKt6Aobtgh/YRWrsIoftolt1tOaWHZFtkUM8f7XOO+aRWkdn5azOmtZZWsdZqHBw6i7sLFTpqK2HHaJakx/5BHUaK9gKmbJE6+Z9Iq0nTSVT16srht3iFHoPvXxU'
        b'qb1GCkOtvZcq6K69r9bJTcXp2jDq5XeWe5KrThx0uGOqiUob9kpXsrVefqoylUSlr84fDO6f/yAsSROWdKvsTtBwWKbGK7OHrXX2UHkcdnoJMNU35B2tcY7GvQYnDdS5'
        b'g353nDXR6cNeGT3spyDDXpGIw04uyrD9q1WL7jpFj3iEjySl3Ul8O+X1lKH8wjezx5hk5CLyO4L0XEwiwXReTI5OkYJPfELV89/xmd6ZrkhQrBxx8tRGxQ1WXObdEmqi'
        b'Mu7M1kRlK1nKgh4D1TwkjlpXH9Xyu65h2pCIQU5/7C2OJmSWcqbK6nCG1t0PEdA9UhsaOWjVn3HLWhOaOhSSRnciafKNJ5E48ZyVyV3TR32D1M7qBFXaQ+8wpL0JgzPU'
        b'1cPe8Y/ZzABHrGz7s7F0uCorDhSNq/4wz+/bJJLwDX48i4nM3KSbWoMRg8km8WV3tf8Vo2xATCQHTLLDEi9UvMzw4hOHNIqgUgV+TGSQpB3S8X//glfB8SJU3BCmgKRf'
        b'DB7MsElP9U1Fp3Yi2Z0E+6vAvimvzDGm1Hvq5ajYazj+yhynXREvJl5VGD59dc76b3t1XilgfF+D0NCf7LxyMH2k/JKpeXpU8t+qOiE/My8qNJBfK6Eqwf5TQKc8pNbz'
        b'JcJ6mUSM5xJVS+vxFKUl4qX8krKyWpm4ni+tL6kX1gjF9VL+iqrqsip+iUSIYOokQilqFJZPma5EypdJZSUifnk1xbUSSbVQ6s9PEElr+SUiET83KSeBX1EtFJVLqXmE'
        b'KxGLy9AseIxoylRUlgk9qqxWvFwoQaNweqJMXF1WWy5EeEmqxZXSf7G3hGdYrOJXIdRwXmRFrUhUuwJB4glkZWjrwug/n8IP0bBcKCmSCCuEEqG4TBg9vi7fK0FWgXCv'
        b'lErH+1YLnoN8EQbxo7g4q1YsLC7me80QrpZV/ikwZgHe5rP1ZqAWkbC6fnVJlej50eO8ejY4vVZcXyuW1dQIJc+PRa2lQsnkfUgxIi8fXFoiKkE7KKqtE4qjKXIiAHFF'
        b'CSK8tERUXjt1/DgyNTQuM4Vl1TVIFNBOMaFeNrRMJsEUWvUMm7nwaJVEJn7paJwwFE2VaE5ZWRUaJkVPspo/w7pMVCsVTqCdJC7//wDl0trapcLycZynyEsB0od6oZja'
        b'A79SWIpmq/9/ey/i2vr/wlaW10oqkX2RLP1/dDdSWU1RmURYXl0vfdlecrHe8GfJ6qVlVZLqCrQtfgBtdfm1YtGq/9E9jRuBajGlpdhQ8Me3JhS/bFtUptW/2NUMoahE'
        b'Wk+B//+xqcnxQvRTdzbZFz21d3W10vrnJxiXDKG0TFJdh0H+zHJjXgurS/8EY+y56ksmhGsu8lxoKZHoTyRsfNFn4jh1rT8XzX+b7hIh8qJI6aL5yMqgkXPgtbKlpfQC'
        b'LxuPbRHafNFS4SRWTSCESCCC16RSoehfgdYjB/8nRByfB494ObIveNx0mbhcKH65xxxfFvnIl/jqqQujMf9qjsrlU/3uLMxteLSiXoosVQUKYnD3ywDrJIgByOaVvHzd'
        b'nPFuodgvS+L/Z9hPWfsFvF/u/8cF4bkYYArwn8YDNGw1WvrlgKkzErL+XOyKaiXVldViLFIv2pDs8b5SSiCRAvOTJcKa8hV/quuTZ/4vCDQ9/N80JlUlyNu81OTNEpbC'
        b'a0itX2IT/gcQw2pA6Rm2c1PwykM9/1rZxCU1wmfWbjwu5ntloeaXyqlMUkfFRS9AFAglK4TicqyWq1cIy5a+DFoqrCuJnhxYowkmRfUvgVggFi+K5ueLl4prV4ifRd3l'
        b'k88BJeXlqGFFdX0VDtKrJThKFUqqy/jV5f8qwo9Gx8SSGmw2EU55Vc99tTQVMHr8nBONzgUv8wxTR0/JVTIins9Vyh3/3sIJfwEkT+YSxQYxeVZ0ls+1lTjpItKIGV9s'
        b'wDctJagb8KpEPTDAIMAFNhFDxMBjYBudHSriEAaElmfMLzbwCE0gqDNpCdwEr+MvKdbCPiovBwyWyvioY3qwjo8gDe70ycrA97M7YYtPCWjkEM5ObDtwBBwTGFDDopLW'
        b'waaANEfjVD+wI2DiXimLTQTBZo7PemvqLitrcfbTK6cssAc0T9w5OUMFde1tbwzOTknQqYIqnKOTaEN1h8C9sROpOPAg2OcznoxD5NB3aWfhnkJXuBU20XeCDEIXXmaA'
        b'HaAXNslw1j84Cffl4flT4U6EQDNsCUiBzeDcNCbhZMaCCnBkFZUElQ63MCcNy4a74PYAtBc3FmzzYceC3aUy/MYAKEED7KUGzrCdGEqlTmVlkoQAXGODLrgFbqLmXA8P'
        b'gRNT1kb0SkXj3PjVxex4sDVc5oyGcUzBYR9/hFRztn9aDbyaCbf7CjiEPdzPAkdwajSVzrQuDh6nR8GboDc7NRPuwKOsLVmBixMofviuBzee5xsi2UGacUZ8SkBs4TF+'
        b'SDCLCAgkQAdRDjtyqctBIdwcMIlPR2DrBJ/gIDhFZ0v5wHMhwWwCXoNXcWpTFewMk+GXNeWw0QVfPFcH4avntUL6DrM7AMqn8FUIWjFfwSYnKsGmbB3YNsFYcN1ogq9m'
        b'gQIGdf9aDW7mhYBzdfA0uM4hyAz8IcF+EYVJbgDYj7rQIuc24ByxpfWI4FTe6tkIBzOcbDdVGJizBHQarxvcC/eEhNSBffiehUwnwGnQsoaii94ag5AQqObrsglyDgHO'
        b'Vwro9zbdlbNDQiTgSigan43FrYGeyhFehVcQxDkh1jWygAAXwY1o6n48EMlce0gIiZN59xLgMLEU9kVRV7NWQD09JIRNxMHLBDiC07WuUeqp3GBF+BKj0/T4xTxvcRoh'
        b'w9+vmIMbq6QkUetBJBFJTD9qoGKaKcEnAvOYdcWifR4MQsCklCS8ADbMN8V5XFPui1dAJUWW2mqwafJdc1Iwvm0OAb0UutPg5TD8agpc8WcTLBYJusFOh3EmwLNQBZoR'
        b'xerBxXGCbQBNdN5zI7gBDmKaIaKcHacaOAW7KJkOr6a5P1XrBizHtc7ZDi1gScndbiam7zHYO07gRLiRTm06B67BbkzhorBxArPCKLUqBN1Q+VJdjQHNSFeN59K4n4ZH'
        b'4QXMB3AdDFJ8AF0LqY8nwRmvLGqCFeDqnylxWyXFsnzYAQcwz5YvplgGFbTSZgfBgZeqtqgIqXYgPE2nHAy4FoWEsAiogrtwjmPVoiWUqi5bBfenp/pl+SMlhr3GXrS2'
        b'Mgl70MgCx+pJegP9sTq6+Tg9T+CXyiL0dBhgl7suJQdnvfAHeKNrDAKLMy6WuND2HFyZF4MZmW4/zscU0E6JR5bUrXDRC9IBz4NGKpvAHSg8fdL80v28s/CnoaC7xLiS'
        b'Kcy3lLnRbFCDvZPTQyMcAKYUOM0i7DNYYHeJmDK01t7w6EuySHE6O0ngNFJLZ5k7nvAI3FxKG4YyuBPsmuw4vMvYoBdcBVeoLIq8GXBjcV16wJSM2lMFlDWMB1fzJyed'
        b'poZOJJ36jKdAgh0pPnQKJDgAmqg0SBLsB6eDZPjrnSLYgHDEJAHnhZgqYDuSUbgjA1/BpmMyBIMOTioytWpqtuD1oHs842IW2Ok3nnFRAHtoL9SzAnROJGpuAD2YNjhP'
        b'EwlqB1JR6g53ixAcHc//BI04BZQEhwthN7XTOKheNJ4BrAuVWXQC8FIbOm3jqMAeNGEZb1lcPjVN2QYeoxNYetxlXAZRAJqJXCIXXqlAymVKmZvuAGRBQKceNiHw8Fo6'
        b'o2tbmDVXwiFAE/5M4CTy/KXJlAmE+8LhDdhOEiao1Y/wS42jjRML5zt7mRHFxaLFubMJOk+qEWxEet8OO3QIuFlIgBaiyAHsp4ReD3bpgoFAJlEeQgAVUWuN2qlrcCXy'
        b'RlfgZngGthsbwQtwrw6W07z1+bI5lMcAHb5TEn28YBs4jFSjJQs250J5KuoLgNtzcNpPCp3zMzsHnAvMnZPiizNZkQ6l5+fAZhYB+gxNsnNFtCNqQKQ7P9n8rTfA5g/0'
        b'gfPU/grX6eMvRBcbmBRnpM50IvIQx6hcNWU4bBSVp9NZwCTBKWJ4z5VSuXjRUAFvTp6STeXvwOPjMU3sqvpM3gsKB7aCrRR4qYUd7clTZk3x41bj0VqmlSFhQ4wuYeQg'
        b'is80JyiDA88COdj+NE7QNZ4SJiCHKCugd3s2TzqFOIgy+Ntjfz8vJF7e40m/udjkyH0LUrBcUZI7+wUi3gQ9+mtMQbOXMZXkGxyEv5NWlBHxxRn609k0VnVICM6Miye8'
        b'jqKFqXn0103HHckq2BgHBkLrQEMacuazkR9BznETLUo9i1AYhvrgPrCZpPzIGXgyUBaO+gzAJWRs2gHifRvcB/dMSmKDfUAVDs6wwbnSOfWl4EIYiQjOmY8Cvx7aeu4D'
        b'x+dT025ZPj6rG+ykXIstksKduGvNtHFkauD28dxN0I6Ctq0h4cuQycYuKQ3BgWNxlD6t4MCGkFAOURKBYyfhokhaTgbCy0NCl4NrYACtE48jToQ0nXi6CVsctBJUB4Kj'
        b'BOXFzqEASkDSaYPwSBjqDGIVo65kFMkg93ldloTn3If+dw4pA2xClG0KgC25UG0I+kODcp5K/hy/ghcEHzaBbn0h2AK7PMAFCmc+uCkDvUjbL0USa4m1i9xonLutdEAv'
        b'TjjvgOcYBMOKgKdygmkr0IxM/lbQyyZyk4n1xHpONPV1dx0KBbZK/fAXyXO8cNIIsvFwa1L63Cnrz/XTAXtzYIcsFi9yFGwDrdysTNjsVzAuhXD73JS0/JQ8ejfgJFLm'
        b'TD//rIxsNgFOQHXGHH2wFV6Bl5HYYGTs4L41sJ1NeOTir1IR08fz6y7NKUBScZqN05wPEbCTQGw/bI2AqA8qet3gicnaCTaVYfUMBm2URSiCHckoetn6goJaIK9NhZHt'
        b'yPBsxcnfFw3h9oU4ufQSGZoH99OLd7uDg1RyHx9eo/L7SA/n8W8yquvnp5LSaHR++6Al4ljBm7X2SRbdnQ5rrv9TVRaz/cuaaTzP88fc95yPF7DS0n/y/jQ9JSXl65PZ'
        b'hqKjSYVH7u2oMKpLSJ42b8atVz3d7iWyNhAbMmp5g8u+3Bvx9tWP3Rc/0C399Ouv9n9wo+WDGz9WbFD99sovbzYMnLz58U+/LJJ2V3MypL9Z37owXPtNf8k3Z95W7Nv0'
        b'/YK0Hzp2vWrjYJkz0PfJMtHsdHdm5UXZoxXxvM69R8o7jC+adu//y+b2ebxoTYd82UAgvz3yG2X2weFVX5+K/cTorbLyDouWgsAr+a86fxAc9IpVVK7v2PGvBYdmDN46'
        b'vuFXg0ez53/XYy5WdjN+Xra3yfHaoh1hC2esa3vyufLoo0Sr014RIb/M+ejrXYE3eq6lB8Vv9d0+FnBu/6Pfty/PdvB4/1T/D6ZLrHN+Dfps+3ol542Ifml7wL1Mnl6i'
        b'qib+zUp57OalpOEHwYwm10bFgnOO+8qMbx6+WH3hRNnXb6tqjp37sez3FtX0sieJpobVle7vf/HxW95fj/1tOMCmj/z1EFzNM2z8wc3uXu2QuPETj9f9lsh2Z7c9STnk'
        b'vmrXJ6t2C3db7s5uvxb/rcvrlTsfVX6m867r59ZnuH+7XKPQTxv+h+dJraq6bM8rNe+qV+455ZnfYNjufu+8tdVj8fW971y80Jix8knyoTCD0bc8ri99u2/njddcb9ve'
        b'cfxH15eD03d8Jsh/Yrswutxuaarl56+OvHmy9O9fHD7JaW77Mvj9vZ9PW5SSM8a7/u4u79fe+ef970ydzmfNG92ctfz7BQfUDjvnLtL450uS9ores1Imijoj1B/v//X0'
        b'T+tf+8Q67/hpKHx3gdF85Tf3TtTJwr8J7tLtzFUGdjISHcVl7y3uWejovdFyreXcD0qz5od8+fMnr/+tePHbX3p/9kXvqa9vceb79yw3XZzz1uz1c4o+qLt3qCC/9QtB'
        b'xZU2m7WalNLT+nNTv5sDHBbaR8nXrFqxMzB8+WcjK92b5X5f2XE/TNzxzf12jbsILHU7+3b5OwcD7dc3X7uxS/rp+g1xqopAGVOzzGr1xtIi3SW2kW3a81HCj7/SS5pf'
        b'Uba8rzn2UcbbWZDx5msRKrNvQx/+5UDf3S4bo/1yLTywct5r9/efP2VSWXvymuSbJvNrn16wid78gcU/3u9apn+jxmcJ17TZ4JUYvcML9m9c+WAk8P1/5qTufe8/VOeS'
        b'VgZYdm95V5H4+c1DPa9HvJJjNPL6d+/Z3vhjfmJk56s/nZev776982u32Mpy9RM3lnxz3CuCV8K6t3ALba923M46HOWwCL7xTkNu0YO+2lW8DYZf91/Vfnjlm6D8XFm0'
        b'81j0obN7BnrtX9/ZlC3tqn3n7q+uG8O0DcYiQ6vRTSdjftu25FZjctMHuXNTNrQ9eeCW+I3Th7/bLeve3PJGlwd/8ZrDnl5Gq7aEPDkkzR6a76fT0vb74zcWJD/6av2+'
        b'k6md9vcGPugr/+PLmJ3rQPjDuevPXXr1cHTEb+cHrmVem1Yc93nIDw1ruv8wHPDY1/noLYHRE3xEqEpm+FAZcKArFufnYSOL4k5rdAxKgZ3wBpUsh6xwOzgIe+B+H+/x'
        b'ZDy9+QxwbDXsolILjavheR//VN/VsHlq6qE+PEAl65WY6QrARp8pmYXgBjxGdepvyHUG19J9J2cWgotwG7W0IxjweZrzCHvm+U4kPTJ1qfRCcHElbJiUXghbQH/meHoh'
        b'GDCl0gjXmVfAbW4+WZm+aThRUBdcZqxYB7qfUC5qC/L9nUvqUci3I8CPIDgrGP5LA6h8StiVl5COUHq6I1PQYRzIrLRi05CnqtihUVPiNnhqEbVgjBgFoaf1fCYnLq4B'
        b'jXQa5vU5YN/4DxXAzaAna+KnCmBLLJ15eKmsHg7gzEVwtAycrvMb/3mOWBZzgYvA+f9q5uF/ORkGB20vvkaelB3T8PwvMNTUR4UGrp78QOUmntGhf4GhWJewsOmY3jZ9'
        b'2NxNPlNraS1P1lrYyJO0tg7yNK2VtXzWIxteK+uhuYOiXJl0z9z7ob2nijVs79c6U2tt37GmbU37ulaW1s5ZmdDp06rz0Npea8HTmlvjKZUh9809tR7eJ5b0LFGbq0uG'
        b'PSLbslsTWmUK4ag1T8nave6hPf8hz18lUy/WBMy8x0vS8ly6MzszVe73eIGjAaFagZ/Wy1fr6YMm0foGav2CtP7BuPQJ0Hr7a339H9saOtt1scd4hJ2T0q3LQesXrGAr'
        b'lg7beGttHakGe0ele2esdsas13xu+9wpG54xR8ObrkhSemt4fmjd+cMB09FCqEEwzPPFQH4aWzR5AJqmar8xahhySdPYpn3oEaR2H2QMMtXeg8JbCZer7rherh32yMKJ'
        b'ZCVqhor70A1vY7Z6mWr1sFv0Yx2Ws52CPaaP06qyNPbB2tAotIb/MC8IJyuKNQ6h2rBo1BIwzAueSF8Mj1EkDbkED/NCqJb9iyYNwbvZ7zDGsOLbaXkCVegYE9VGeW6I'
        b'sJbqZYOmarthj9gxNmoc4xAOrsqZYzq4rks4uCvLx/RwXZ9wQJwb4+K6EeHgjSYxxnUTwsFHNXPMFNfNCAcvlcWYOa5bEA5+qvIxS1y3ouexxnUbeowtrtvRc9rjOo9w'
        b'8FDWjznguiONgxOu8wkHf1X9mDOuu9BjXHHdja6747oH4e6p9RRovX2/9UHPCtaYP6acaWckna54z97voQ+dkFaiXnIr7I7pneBbMZrwrGGfbJzz2ZmhdfPoTBr1CVDr'
        b'npw20eKuSNL6Ir6dzBhM1PhOV7AUhRobLypRVZWm8Yy46xk3mHDXc8YtU41jooKJKOfsoRSqEof4ger0If50BVvr5KbM7Vz9wClI4xR0zylk1MVdRfZ4KhJxamyZslzJ'
        b'RWMcnRRMPGli55IHjoEax8B7jsEI1cT+JbcS74bP0k7AjDEJNN3TUfefjRoOnzWRNpg06Nqfdosc9prRaajgKNkPBaHqgsH8YUEiQn9ep5HWP0SdoC5RLUGPizQ2PqPh'
        b'MXSW3oPwVE146h234fDsx0zSNlRhoViqsfVWJWp5/CHnIA0SIhsHhVhj4/fAJlRjE6rOe8cm+qmWuKss7tr7oe0+cArQOAWode45RY4K/M/an7RX5w4LopSch64eyuVH'
        b'YtTOd11DHnpHjxFkbBapzZmLFoudh5MYfebjJEb3+eRjDuEfpLYaJPttexdrA8PUtZrA5FurNYFzHvpHDXrcMr0suJU37J+GlCTCRclWijT8kMcG/ynMsP9MBBGJIWru'
        b'8kMRhGcEWjAyk9RmFyAsIudSqZTzqFRKVCI9cFH6a3hBahcNL0wt0vASH/DSNLy0O2H3ebPxzv01toGjPMfu1M7UIY/4W+7DvBQF+aG7l8r0rPVJa7Vpr92RIq2X4KzO'
        b'SR012av/ENkA50ue/Z6DzgPYCsgui4c9MqeoelLXNJwinaT0u4sMWHAEqvne5QVQZiROYxs3asPDC3shxqDqh47+CNfAaG3cjFuzhmIz0CYCM/EmnLLwJmyzyFFnj91p'
        b'H9o6YlO7oW2DUnrP2kdtccmh32FQdi8o6Y7F2w6vOwzNLbyXuuBDG/5Da4eHjv5DAcl3rDUBOcOOs4dsZj+08x7yyRi2yxyyyMTpwAs0ll4PLTyUMtVijWfsPYs4rQX9'
        b'Azzu9yy8kKi0Jmmd3XenjdrzlY537QNfmA8ngjtq7APVZhr7UOwDnJV5d60FOJ18eud0Vcg9+wD1zEtp/WmD0oHsWyV3Q2dp3byoVF3pkewHbjEat5jBmbdch92SH7hl'
        b'aNwy7uQOu81WJD1091YFnSzDOd2Dzu+4xyrJMRbLOYPUBkcgmfAaTLrlfKvktvvlDJU7siv6RFC4umSQVOtj6XC/Rd5iDFLywWYKkHwgs+fmpQo/PE07LVE5c0gQfdct'
        b'RusuUBUcWYyMrHKmyvZw9rcOhEccsk1ooOFd13BteKSSpVyEJBFnbDsM8wLUoRpexH3MO2Qu7tr64FTshRob7wc2QRqbILXbOzYRHz5PnDEZm7B1eLySTZhYPjRxUYap'
        b'HDWukfdMorQmVh2GbYYK4T0Tt1FzW3nmT0+CCK/gbwkG2uND7whNZIrWa/otT41X6ndMMiqd0qcMSp9QycSjfqESYYcZhvl2rPt29vlhOnSWrckIC19s/m9m1740yMC3'
        b'QsUviykkMcSzn1KiYom/4vHTCDrdNpdDkmY/EqgYw8W/m3N7gONL9HEjmFMuVSeSbL/D++sghPjHMolCRjlZyFzF0KsUMEdMqNtcKtNVkiSR1Ep+caLvdyk0JeOJq8Jy'
        b'fomYL8T9/lkC1ohuURG+EC8qGtEvKqJ/5xLVDYqKlslKROM9OkVF5bVlRUUUoenEZooKeL+rX1h2BKEqZaOuLcRHBkHUcPoKc988sI1rBC/Vu3hy9VBEneUnGY89A2A3'
        b'hw2UMwRkcvXf+AyGtA7NkXDsB2HbrGwYb7FlxXulJ35kbLFaHbBxKN1rY/etdeV6y5jp8W7+d3Y/+Exu0rEwaqvT6wPbmbpO0/7xzf5VV2N+3ScbdI06dyTy1JHrA9aw'
        b'2Ew6fOb9T31/ulVrt/O9sJtznfOrThe1by48uOSYmvPpJXA23rBy45Ul31fs/P3LExfyS49+3fJ9uLFFwvQPVtkPfDKk5/okVnrkg9eGk/KOJr2zx3RAln37mFyuEjiL'
        b'7Q+tfrM1/tu9rltDgzb7BjXG9je49G8J7t9EfsTfJs83MJ8VmMaDkf3b9D5yOy4fVji/VborsoX9kcs++V/n3fZ+R70rOly9nXNR3ezwVanxr5F/Ozpt0PNDk1mRyeae'
        b'Dq+2s613t37xJDV6Q7LqcLFd5LGYKvGu4J2XkyLEad2VH55OdbJc1sZft4OnHxXaZs2eHW4eeel7ccCJsT9e+W2a37Z9b9aVVJfsWvTz2bc+bun7y+AfYmH61yccDH/8'
        b'PfX3hBulPz4CgsCbhGXMsld3yQUs+lupfWGwP5UFmzJI5FTQ0cxfSh0bjLmgeeIn/bzhoPWz3/TLgeonOB4PsXLkeuNPmtAxiRqERziBAdA5jwXPFoLj1IGqGpzzl4LT'
        b'KVl+T6+LTGErHDBiAjU4Zjbx6ZPuvyz+D3/6FE/9NbzwRx8okMqIakvKi4pWP61RR4lfkND+Ex0lfAlDyzGWjp71Q2Oz1uCmFQrnHWs7pcpgZUkP/gRidteGfje1ZNC5'
        b'XzY4u3/lgP/tmXfMYMrd4IxHNnaKYEVJZ9h+PWWaxsZfba2xiRyKzdJYZw3NyRvKL9DMmXvXeu4jK77SrF08ZOKGIikb5OH1CTOL1oQ2S/mMH1gcPa8fTFh6LmMGunx9'
        b'rYFxq9UYE9dseYoKuuYhUIXTtZDwQQ5di0+8VUDVRikINq5REFSNgqBqFARVoyBwDcUXhiYIRoeu2zkgqPG6pzeCG6+HRiDI8XoCOZNE0NSTLg2tR9cp6PG6b/Ag51aB'
        b'1tRaUaEKf1n1W2M0cEiXhyJxMxvUQv//MZfjglodfzRJZuiFPyFwOZbDIvRNHuqZtEoVYa1L7+m5/MhIY+nZ/Ujg8jsmoe+KC5MxFn4eK9RF9ScMUi/4wCrkgPSCqc7H'
        b'uOGnsTWGpF4q+dDM6ajBkF/yMH/WsFnKkEEK7ZZ2JNjM1Cde0Tef6cCk3ZLFCAMZzv8+p/RSobV4iaN65qxSsJl+Kqr41YI0btxTCUjSBDsqk+9x8e86qh5OENHPjWVW'
        b'v1Y0h5SuRS2PY+YJm+P0N8fbzLw5PWykMy91aKXnWbWNyfCxjOiS177e3Di22yU9vq4r4tWyz+au+eGj++9m7HIwfHLM+Pu0xmtff2C1yyC6utsh0zNmrsuqBQ9uL04t'
        b'3pVdHRjI0pvziVfOR6+a7eRazH1U19gDmJlzo+2zEzyqBRvOvH/e/lD0OoEO9f7DPh7egE3cZXB7djZ1C6pDcME5Bv4YfQH9/qPLEVxJz84Ecj/Yj0dl+zGQCbrGBD1e'
        b'85/gu8oyT9gHmvD1ML7nBM2gRQfuKCSMzJiO5eDUE3znsRDsAYfTqc9RhTzqg9Sl8CL1Vsc4EwykG4Erk36lmCtgwFYjKf1daC9s8JDWrXn+R4xjwGZqYl14vdYnjU0l'
        b'KajAeagAm0GHwPXPjeL/9XcxL5VI1wkz+qIRfalBrRZX19MGla5RBnUWKn5rIL6zI9jmWkOLB4aOGkPHAyuHDb0akrUs/caMjRlDps5HI++xfN9jOb3LMvyRk6zDDv6R'
        b'wOUTqhzLMSIMLBqyJ32OxR9hioTiERb+8meEXS+rEwlHWDjFDQWQ1WWoxF9vjDCl9ZIRdumqeqF0hIUTgEeY1eL6ETb1w5kjbEmJuBJBV4vrZPUjzLIqyQizVlI+wqmo'
        b'FtUL0UNNSd0Ic3V13Qi7RFpWXT3CrBKuREPQ9PrV0mqxtB6n/I9w6mSlouqyEZ2SsjJhXb10xIBaMJhOMRwxpAPMamltZHhg0AhXWlVdUV9ExW4jhjJxWVVJNYrnioQr'
        b'y0b0ioqkKL6rQ9EaRyaWSYXlz2yOlI/Nw7/84/NpUzF7osA/fSbNRsUff/zxOzIUxiQpYWJLMbV8TJX/jt3AVvK2HifBlrhty01wY/6iO/FjviMmRUXj9XFT9YtdxdTf'
        b'Y+eLa+v5uE9YniXQleBv3HBwWiISIRtL4R6Pm/QReSX1UpwfOcIR1ZaViBBl58jE9dU1QipElSybkIZn0eyIbiwd/k6TrCDoeFuaiooxJkmSjxkskjVmQHANG3S+ZeXr'
        b'kBZjdUaEnukDXXuNrr0i7Z6u55DvtNse0Evjm6bVNXmobzVkHTKsHzrECn1ImLTa3CfsqKX+F9wmR6E='
    ))))
