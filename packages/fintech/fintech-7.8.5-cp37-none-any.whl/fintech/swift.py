
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
        b'eJzVfAlYU1fa8L03YQurKIgrwQUJEFBBUNxQCwJhFRRcIYQgkRAgNxFF3HBB9lVBcUfcQGXHBcWed7rMdJ9pq6Xt1E5nbKfjtDPtdNFu/znnBgWX/t/83/99z/eZJzG8'
        b'Z3v39z3nvDefMEP+ifA7GL/5efgjjVnFrGdWsWlsGrebWcWpRcfFaaITrH5KmlhttovJNOd9VnNq8zSzXWwhq7ZQc7tYlkkzj2esMmQWD9SS+MTw0ARpVnaaUauWZqdL'
        b'DRlqaexmQ0a2Thqq0RnUqgxpjlKVqVyv9pFIEjI0/GDfNHW6RqfmpelGncqgydbxUkM27qrn1VLTnGqex8N4H4lqggl1KX5PxG9rgn46/ihiitgirkhUJC4yKzIvsiiy'
        b'LLIqkhRZF9kU2RbZFdkXORSNKHIsGlk0qsipyLlodJFL0ZiisUXjisYXTUifSIm23DpxH7OL2eqab14wcRcTzxS47mJYZtvEba5JmD2Y0HSZKFo1yD0Wv0fg90iCgphy'
        b'MJ6RWUZrLQlekziGwKY7vxFzUZnBGKfgP9BF1Ia6oRSKYyLjYB+Ux8igPHx5rHxFpDkzLUQM/cwsGWsch7tyqCKKD4+CCiizhdooKGMZSTiH2gywS8UOEZ/jIALRhAcs'
        b'5sL/hQfpjiZa2X0iTCuHaWUprRylld3GmWjNeJxWtydoDRZofc7enLHBIpnhkRL5qiaEocD6AhFhgMtIsxStNHKTANS4WDIODJNTrU7x3uLvJAD3rxEz+P8kXXiKTZvP'
        b'VuYco5VgcEiQyyR7q8+mMszH077iembYeLzLaK1ww3uBDWyBPM2eCU6Z+YF+uYwVwKrUr+zfzvdw5WLvsD8nfel2iRlgjHLcEAMdcNx8JGZ7qW+chweU+IbJoQSdS/CI'
        b'iIJKb59weUQUy+jsreZDGzeMuRaDFE8nzCWMZdJFD9nH/ir71j/OPosn2GctsO9Siv22fnY21pUU71/SZALSFhGoEmNc5qWAMiiOdEGn48LCvcOXMzMV8U6oLgGVov3M'
        b'ejMLOAbtvNGZiAdVoMt+6AJWsl68BDrH5IrQHuMo3LQpcJ0fOoWuoS7ScITJhF49bbCCE+ic3yh0dSbRzgOMagJcMhKdRldDY6HWjGF8mGhU7KM1UExn2knmfcp5MIxD'
        b'inaEcqMgPosNjnYiLgx/S5n3VdAyRqP84g7DK/HfVXve+lvKZykb0iOVr6b71Hgow5SfpziqMtK1qfdSIpSvp8uWhStlsQrlBfVZ9vzI9Z+lRShXMzWqMGW2ukZc0tx2'
        b'ZvrilWWy8dIVQV8vfjH6tF3o3TVVV563OSxnEjKcfrYVyTgD8QFrXXhraIb9mFWyKKPcE0uYY5xQkdgS9cFBAzEnOImKczE/S6ASyrBizmHRQShD7dBoJ2MHOA+ZTKQn'
        b'chnyweGPB87z0vXZ+WqdNF3wYD58nibdsGBAQt1TcprSoCb9eBsi5Uk2rA3rwFqyHqzefHAKmWjAbKNSa1QPWCQn64265OQB6+RklVat1BlzkpOfWFfG6omm6M3IB5ll'
        b'Mpnfjsz/kQNnznKsOf00EsqxbtTAXq8wb89oVB6D9cOMcYadYnQsegz0zwxVcSb9Ez9FmbG3eKjMHPUFIqzMHFVmEVVmbpvoaX5vcMLhymwebSS+CIqxolVCLdZ4uZsb'
        b'I3eKo+BYtAc7vlpsVL6beMZXjs5SNYNrcIwR9GzbGMbHOVdj/N19Ee+Dm3Jtzv4tZdXNKtTg8gXqqjpXe25Xe9ikPVd2hR9mX04nWmWTfifSgqkvt5w87qKMNYwl8x3i'
        b'oMYrQg77wiOj4cpkM8YatXNwRLLcJIunCZmyesBakGi6NltpoCIlus142rBiLFC95KE4xVQ8A2Zp6lSNQU866Yn3kXFDRMjpSVgaIkcy3OuhHG8Nk6OUeFCohd2DYoR2'
        b'dITGCG+WGZclRtV+s6iBL0Sl6bwhYLoYB4ej6FgqA6fhqC9lr/fqJNLCMlyGRs3AOfv51LyXjkSXCVzEcF4B6xlo8YNSOhWqkTO8IZBMBXsW6Bg4D43QbyQSTYTrEtLE'
        b'MZxiYjYesynfOBrD58NhjoeuWWQR2LMd7WKg0xX7FxeqhttgB200Y7houIB2M9C1FDVRJND5wG28no5bCpV4xla3fOMY0lAyERVCp3EGpWg3OoI9GnSORq0UxTHR6Bht'
        b'xIjYjca+CbomoU4B+y5/d573o9i3o9LtDFyEhlCKJRwIw6wjwzDNGQw6xMBlOGpHh/mhq5tokwUeVxiLGhm44pBudMJNdulQB528jYQj+J+CbtbfbTltgdoNGms9Zbqj'
        b'GJ1moBc1uglL7YX2DGton0XaLPBfZawIeqLoqAIPtMtaMlPg1Tw4wFqhMytoS47LAmvooSTDBbgKe1h2QRRFD0p8UBEPnXl2GAlJDpxgvaAohrIwMXMlb2ULbXg6r03Q'
        b'zwasQT0Uh3nohIN1rhF6SMJwPgDa2anoNNRSQaK6BeN5a70BD7LyhAZ24ma5sE4hKkvkDdBrTbA7KoFy1isyRGBsN1xDTbydLeaDCF1NMWPnb0NdFAXoVsfjBjsWNxxO'
        b'tWKD0WUxHSPFbnQvbsnFFE2Fo3CZ9fFAOykG455ztbbNQWViRhQkm8wGw06WDuFGoG6iEVhZ0M6ROQxmxDE4QAlCNRPQFayy/uYYt+OoPx0rMyq1Fhi+IyCTiJ0MO4i9'
        b'DNbADgfUIOhSEfbwnTy0Q6c9Zh+LleAi6w+7ecr0RROm8dAjNLmK4DzrB1dWy6Q0fG1zdRzJMRliJvZm1u3A35tTYKt+1IjNbI6YmY6Bc7XuFOjDOm+x5TaJmZybWUmW'
        b'YQkUGB/jMqJZtAOb/c2tt9cs2EaBY0aPW5vL7BMzwTe3JvksEoCXbCes/khUJWakGOh+OpECK+dNFL3FNIiZlJtbXWYft6DA97a7Zf3EHBczDnjOzMo4Cjyhn+RbzZ4l'
        b'eG518fRaSoEHcqdYJTNtBM+tSQvWjaXAfs9pmQGiywRPvPrIYAp831lmLxbdJHjytycE5lJgnJ9niIF7GQOf55O2NQdQ4DcrvOfXMG8S5PmGcasjKDCA9w2ZxdzGwOf5'
        b'hpDXNlLg3e3TXZ8T3SEU8Q2zbs2lwC84P0Uq+xkG4jk3WiVR4Mn4Wa5G0T8ImbzLXGd/Cly2KnDuAvZ7DHyev73ypRAK9I2avT2IYcww7XzS/LX2FPiy39zkUZwlBuI5'
        b'I7/2EsQxbv6iWJGDGWYI72L5cT4FtkcvjP+Fc8FA0vPIDAoMsg+edomVmmEu8bcXB4dS4MhNS1wLWA8MxD3njMygwFXykPhGBmtYDqYo8fQ4CtTrQ6d6c7Mx8HneZczW'
        b'IAo8khhuXcwGY+9+M7Mh5v4GCvxwVtTKP4hizTDrMpOcXxKSppGbYzbni5Iw8PlMF8NbrhT4y7LY5QuZFDPMukwX76V+FPjq6mVjprEZGPh85u3Uxcup4cV5j+CtJdTu'
        b'rkKvDRsshsuCHTe5PGett7PFpgpnoWwEOx/1wgXqj21QKbRBJ/Tm8dgNitBu7DO8eLhBzcgBVczHbga7a2z/OCeshjp2El8gEwt0rXxJZSWabYGJzXOJiLWhwHlxv7X6'
        b'UBSM49nN7Aa32PGC7s36nZWWCcPA57Nvrwo1o0D3la8lThHFWmAOZDek3xk3LJ22GkwayHbTtFt7tE9h0q0eptbi/3hq7WB6D89GFkQbXfF3HY83XKUxeBdVCcXhaC86'
        b'E+UDxTg7dE4RT/NfTFGeP53s1JJ8bZgUG0udpZDU3gigGxWVRUqKTdDUSIY6GRxsunmF73jUoYCKGJxrWcJubvNqaBCC4F6LUagTdZEkm13JQI0FasVRoVDwa4eWLPXy'
        b'wKnpPt9oM8ZmPerjRfabI4QkaNe05ahTzGi2MkFMENqr1hNmUTRqtuBFmNnb8FbH5qN1uQLwZjzZbllOt5OmeC+In8YIGYAdNPtNpx4UeoyM0t6d7jiXokMaBc16K8lW'
        b'UoFTsw7U5BuOLniwjNRgZge7Jwv+fTccDvbzp3EjEB1jUtGeSTTFzIbL67zwpgnKouZgH1qGN1HhYmakTARldugK9fMpUCLyE3YQXjgUqdCOeGHOFiMq8UMdZNNxbFEU'
        b'o0XNejoAdkHxCD8/MuIo1PDM+rjtwoASdB32+fnhtBed2LKA2WAHHdSBo51wAir8AsjXBlSvZNLSYZ9xLM0urNEpRQTBK1oQivM4uxzR7JgsOuOIFNTgF0AQOAjNqJlR'
        b'Q5MrHQd9DqhbgZPECl8o92IZ61WpEzmcR5yKkXFCLDyHDqB+vwCOCA92oiYmfQUcFTKa+mkxfgEEyUYFlDPr4ZApMdFA+aapGNdSvBOJMmPEE1l00imIyge1ZQX5BWBr'
        b'QIfzJzMZa6FYQOPwWisvIg0ojkYXxIzNfChMFNm7oRt0Qh+cSx33Qz1kguOoxgazsBRzdRxd6wxUw0F0CUojI8ieRgQ3WNQIu9BlIzkLgJoJ9nxkeHgUOWgY3EbGefjI'
        b'PKN8ZHJOgprVOFU4jU55eKBzzl4yVAenvEahOmcnODUaneFwejbKAcpRKzqO46j2+19++WXNFKKNn1mIg1MiGyfMZ6hoovAc7fFZXtHyMDEjDmbRedQwTjaKar0cnUvE'
        b'mlPD2+qNIpJssJNRBc4zCWme8XBl6WTotBOaelgZNs+DtGlC2GgLuAGdplE3cCJUjlMKKpWmnEmwB07xeBhJX+pYV9QVS6XiFoG6rbz4XKOE+jVWivbZCHlD70zJDFSM'
        b'M4A86MLJA07U3ELhKjVaC9Tvgm7AcZx2QZctmbGdnYkqOKqmeVugLnettZ01qsROdhW7OtNC0MZdY+BSgjtvkOSRzPU6Ox6umwk+eQ/sSMLJTCFpI0vtZKXLxwjuodky'
        b'BjVhF91p0EMXpgvdYMcZUJkw7sRM2MtDh8GcYdFRJoGFSnReLNjE6dnZdnDe2tIWbyJEgWwY6oimWHi5TUL7t+CENteG4H2InQYHNwr49UxLhoZMazsb7HFFc9lwuIz6'
        b'KBIibEbNcAZHkk57Pc4zRXZsIFShw7QRXXMDcjzVhBuhg8SVSewiaJonNHbDDiiGwk18Ll0P9bATcfraKzSeQCVibDztvEQQWQ3m/hHUQrEZga26Jw91WNM2kSM7PRML'
        b'k+4Vq/PJptAc07iQ8Wa8py0R3GwZqvdDpdxUe0nuRpbBE7OoHDVDJeWHxSp/2BPxiDZ0FurpOla2I8Z5DdUnOIWOCQpQiYrhIFyaNQS9megq5bwIm2uF+YyhyoY6N9Bh'
        b'U9ARI/aXLUN0DVpx4k1xPO2HLgWj8mHShGq8H6LibEnd8kiaaB86A5UrJxnHk6az6LoBG3Eh1rpeHION2E2gqyzaiXZHCDajmoNKFwXkQY8NKsYWBftYdNA+i5LogCnp'
        b'iB41RCN94RxdcTG20wprODxE71C5cMaTvwiddUFnhmjruFkyYUc0G8eE6kR02lpiBR1YNkHs0hA4JOhQKerbhPpseBM/D7BuiSNpixbVon446jPEqMdG0pYE6CyAw+iE'
        b'tSWVtIT1QY0LBeWvzYXylTgedtoIgy5ibS3BnoAgKMlzj8Pep9NooydNzew0ZrkQNI+aJzuhXt4OesguBo6xU1AX9sG0rR4VMtOgDFu1NdYEDjrYgCVQIwjn0mrogxao'
        b'tNZDN3SLqVh9UIk9XW4GznnwziL4kUWNmUC5EeaPt8Ed6KA1dFvlmjOiaeycOXCcUmbjDycD4SRtwZmYBxuEt0+UMt53ChTCaR6V59BdGKZMhs1rl4BkKZyLggYJRjLH'
        b'nuxoiln3cXDFSM430A44pcEdalHlRqjDCl6CLgSgc7Af6qEWDiSyDN6S75+8TuyEt/nXhbBZ4osaoNaCQRdTmOnMdFThZ4wlU+2B/tV4UD3Uo31ksiuoceiEdbilCi/U'
        b'gf+vwwlRL4ZV4b5FVpjgeqyRLRkbsL+/go5b4Y1VzVKK+3Z0HW+qCkcMZTBU+VB2iFBR1gzFMO6KHHHcpP6qH3WnzZMPYaLnVIr98nRUvyh0CAuXuhtjSIJhCLOGcgWO'
        b'gWFRPjRcYXcfFSFfBvti4j18oiJwgIPycNkKvLP3XYbz2i4+keGdyAnoBdS+etTgYagD2u9o47KAIijOR3u3pAxluxPsxAiOFxjfjo4pfOSeEWTZi2Jm1Vz7FSIt9m+H'
        b'aGQVYS94A8fL7UugXEgOLKGBQ/s94JKQcuCcGVXjFDDMOyJGbs5YKxznYTOYilM9okayjQgL/cQQw4Fe1C8c1zVglnZ7RUQp5NlQTJbHyaAjOipCbWugXpNeNYfjP8MJ'
        b'x+u+J9YmzI0ftcjhi80ffPjHXPsQsd0IV+nR78Wux48WhwQHp+x/fkzw/kWj644al/c6rJm+RJrUvVOdNWbkvbEuST9zotTUJZNFS7bv/uhVnzqHV7Vv3Prwo39lBry7'
        b'61hcW2T7uoVdaftCaltzPlqfJn7FvT3tGzY5Jj7l6t+/c59a9/t3rX3+3NDp2yNzvu57ZV2OzOnj6NePN8wTRU9r7Z0TdmrEuZvlhU66F2VxoacLXzlY6dTu0jp2p+UL'
        b'D/gWm8uX/zRrrH5q77LQr2MT9/aXcVu6o37KDt4Q/HP+qaOTy3Vuzm6Lgv5g9vW7lqc6Jzbu9L83PWyf/ZwdC50mfT331v43vTdfrD78t76XVswPOKRSfTipzVb6yRmX'
        b'Q3/Mn7bY/NpFbuSVl8wqt3/rXTvm7nnrey1QtjEpIUxS8NZncfqC0LHzQ0PLr/RtbW37+Uj4vOXShFXymklvbPSst7ueO7/vbfcbWuvIntl3Xk0/+G7yezWyqSE3akpm'
        b'qbv336lvt0ks++pagNmfP32joumvTX4DzltGvvjxO+PlD1wiVtq030uc+8Xrxe4h6IftZc9t/DbezP7GwOk/LtZNvv7aotPhEfOOlCTpJjz3Vd0b/vrjUbl96W0Xla+l'
        b'rn1pwz9tj37S2Dh25JKCzPjNLe/fnvrRP3+o/vTDn4I2fJz+VuIkp/CqGtuTy5bd3eIepnb5R59V7Jc7RmvHbHqhboLOq+H1mNN/OsO/cSvyPbf4sIjPvBuUceVd576Q'
        b'rPab5ZNnbAXlZ180/c3zR13CyZtrPvnd7OaZx76Q/bJiVIzbD25HP9V7rj2z5Y2Pv7v5w4SJP+z36/+jt8E+LtDp5526z3ZfrFn5yX7Zb/50+tK7y30q9n0/4se71YGn'
        b'VUsqfn9xk+/PX/79zocb3wmpfG/TdfesDwMiRUcvTLZufRC3MFLU+eYd50lvf/x+31L5pRfWfOd+ovHrqx80fnrobNUWWcOID7ONH7Ss+ZfzwqqtP98qLqn6+peXLt5p'
        b'3nqr6aU7/PKCP7VUR30S33b254iiB4ssftoW/pfr23/8ve8fqppktgZynxeITm+CUu9onKBCpTfOxVFLDjqIXSneTl2nPXAafHmSl0+4t6dMhPp9cC8oZhgXqXhdJtpH'
        b'D/jlcB3OZ2J3N+yMvx1KUZeBWGXMAkcv8wIfnAsX4xXMcYonh3YrAwkX6VASo/CGy9DqEYZNEps7auE2o7PhdOBK2BusQIXQGh7lGWXBmIs5S9RTQO8dYAeqDyGntlCM'
        b'zuZilHCOXSliRs4VQePUTANxemEroF8RI8fRayO7HJ1d5IvOGGhAPJqCqrygBVX5yKDEm8EYtXJ+xhgDTTymJ0NpONoT5R0OFbjJn7ODS+iCgeYPR5ZEKsjFkCKcZPSY'
        b'WWnoVAoHjf6ohDJiDN4gdXt5QhdqHaTWai6Hjk1Bu+kEBV5j8aaFuNhxUCePIFcGjnBZBEVTUKHM4fHz8f/sh8zq3xvz6DzeUTiPN+iVOl4pXAvTY/nXGZLu2LGWrDk7'
        b'irXhLFkb1o7D33C+Yck6snYsuYWxZCX0PQq/HPD/gy/8nbMTvnMSC3OWjJawzpwjZ8mJzcR4tAPrjGHm+DUWz+tMIaPEYnboi8wtpn3wd86RrifGn6NYO7qqhHNgJ9IW'
        b'/OYkGCrGmNngv81ZF9yO4eR/3DIWv/U2g5TLRAM2Qwkecr3w7/FRxuptBzlJp1/CDF4+9I8fevlALiWM5PTfdPngOw8uyPB20is60kfQZy9zZilqtUB1eGveIWNpjJ+Q'
        b'NEsR7h2Os1N0EWpxktuYEjvspIcsTg9knmPoSQ+5kWaevJNOt3144sM988RHRO+fxN9k4Ukl0iH/YomC8FLl8CIBWnmwOUctjUqY4z9dmq2nX2b6DBs67I9wg1SvNhj1'
        b'OjKXVsMbyBSpSl2mVKlSZRt1BilvUBrUWWqdgZfmZWhUGVKlXo3H5OjVPAaq04ZNp+SlRt6o1ErTNFSKSr1GzftIF2n5bKlSq5XGh8QukqZr1No0ns6j3oRFrsKzkD7a'
        b'YVPRe0Ohlypbt1Gtx71IbYRRp1Flp6kxXnqNbj3/K7QteoTFZmkGRo0UZaRna7XZeXgkmcCowqSrg549hRzzME2tT9ar09V6tU6lDjKtK/VYZEzHuK/neVNbvuyxkU+O'
        b'wfJISYnO1qlTUqQei9X5xvXPHExEQMh8tN5iDNGqNYZ8ZYb28d4mWT3qrMjWGbJ1xqwstf7xvhiaqtYPpYMniDy9c6pSq8QUJGfnqHVBlJ14gC5diRnPK7Vp2cP7m5DJ'
        b'EnB5Tq3SZGFVwJQSRj2tq8qoJxza/AibRDiVoTfqntqbXDgH0U88p1GVgbvx+C9j1rOwVmmzefUg2iG6tP8FKKdmZ2eq00w4D9OXFdgeDGodpUG6Xp2KZzP8z6ZFl234'
        b'D5CyMVu/HvsXfeb/UGp4Y1aySq9O0xj4p9EST+xGutRo4FUZek06JkvqK3hdabZOu/m/lSaTE9DoqJUSRyE1kabWPY0seo3/K1QtVmuVvIEO/99B1ND8IehhOBsaix76'
        b'u5xs3vD4BCbNUPMqvSaHDHmW5yayVmtSn4ExiVwG5aByJeLIhZfSap+hYaZFH6nj8LWerZr/Nt/1ahxFsdEFSbGXwT2XQZ8qM1VY4Gn9iS/CxCdnqoeIahAhzAIt9PG8'
        b'WvtrQw04wD+DiaZ5SI+nI/tExFUYdWlq3dMjpmlZHCOfEquHL4z7/Noc6zcOj7tLibThVLqBx54qHScxpPlpA3P0WADY5ymfvm6sqVmtk0frfZ6F/bC1n8D76fHfpAiP'
        b'5QDDBj8zHxDGavDSTx8YvnhR9LPVLjlbr1mv0RGVetKHxJjaUqlCYgOWhurVWWl5z7T1oTP/BxRa6P5vOpMMJY42T3V5S9Wp0IfN+ik+4b8BMWIG1M6InxuGVwJu+XVj'
        b'0ymz1I+8nSkvlnpEY/BT9dSoz6F50RMjVqj1eWpdGjHL/Dy1KvNpo3l1jjJoaGKNJxiS1T9lxGqdbm2QdLkuU5edp3uUdacN3Qco09IwIE9jyCBJukZPslS1XqOSatJ+'
        b'LcMPwvtkZRZxmxinhIzHSqaHDwwy7XOC8L7gaZFheO+HV+xky+fMPH7FHi1Ur/bY0jpfRjq9wLvWSy5cUa+dQUt6pTclRu8D21MZes+dZUCHUWfMVLzTncvMDYCTtGvE'
        b'Elo87BAbr4s8lzabEWqX2qB3Dr1SXg5HSV3qRjsjKT9GhXp0yYtuUKEPLg/dpLq5mo0NDpXZGEm9JNqrmAGlvhHhclTiG4EubopSyE3HrTOg3NwLqr3ogewy2AdX6Xns'
        b'kMNYKIEKjMBJBT0NHrtsrCIXqobeMJP7ZXQWNQqnwYcWBT68R0YdLLlKJkdXFduEC96WpaOglJ5oo8ZoOcdYwhUOlUCjhXESGd2JClPJ9XU4lD23XYF34FDpGwblIsbV'
        b'UQwNqC+E0mOLjjjSXqgCdkOZgpYJVkAxKSaY4mU2bxRcMU4l0x3c4meajfaJg3bh8j86imVkqM8MHVoszJgIpahQ6HoiUeiN+5X6huOOU1LMglejDlqZiI6uWOflA+V4'
        b'Mp+IKCj2lpkzcMh8HDSKURNcGE3ZmIzOJ5g6hUdBCekzGnXInMTTUS/aR+eBxrXuJsG1Bz0uNzhiI4i9Q4eO+M3E6jR1K6pn0lDZQioDL7QT+h8X0+RU1JbsLxTpFcN+'
        b'VOk30wx/PaVGjUwG6o2lV4zb0VkLqLWEHRYMvTFpnyncwh0Yjw4r0AF08XG5plgKHUrh+qaHYoU96IJJrnBxg4wTFr06DfX5oY4ccwadTWMjGXQxf5RwSV0MlQ64hXy9'
        b'GoiOMplwAvopJagRjow26UMGtDzUB9SokpnTsxUeXcv188sRMbGol1Uw6IIZnKfrea519/ODNjOiMzvZZQzqQseEGkV0HFVDoZ+fXsQsgmY2hkGX9Hqh5ZI7asKjOswY'
        b'mQO7gkE96HA2ZfUmFTT7+bEMYwcl6CSTicpnU4atTfPw88N8RKehCDUxWt+pQs1JoDPjja20ykZdUJ6zRjDoeejIfN4CevEsIUxIKHTQrj84jiBPZ8w+vnWjti7bi5GJ'
        b'6KXc/PlOpAaB3KigrvEPL1UWSihfJqND7gqoRfuGXMvQS5liofZPBv3oiIIWOIvFrCM6hl/XoG5QFDvQeUvKtBnYAgnT4HKgwIB66LES2BaPTlOuhWRSA4AauDxoeahi'
        b'0AKG2N7o9abZ0Z5EdJlyFzWJKXdRYRiVlSWqWi1wNyOKcheq1lA/5Zo0mU49BavCk9aKDppTXi9RwWkqA4knFUHvRGrEZtP0Q204r+BxE0b9IFygbymYSIWlxjzFskLn'
        b'nSlpK+ag/XSGKDj3FNOGg9BLdUC0Nt7PDxsbtErRMSYDOqBGKHiLs2OwEbi8KTfYfOBmz8hGUROWrdmkCJdH+2AD9xg860ZV8nGoSIyaZXBRcIfVcBVbDCnFl6NG1Bcu'
        b'ZqwsOFSRqBNKZzo32j0U4+h4LMWD4dSFOGLmNT9UkL2o6aGGkIpb4RL5mgeP3b59hFwh94wmT8TYrxepN0wXPH7PmNGPFTpV0ooatMt/XKQY1aQG035B6DzceNhxpoJ2'
        b'HVoPVbeSKiRcs8963ON4jMRhoXoKLayCQ6gbtQqFR6jCF/eEJulgZ0+VGWqRuAiX0edRRazCl1SMYcI6BqvG3LbTArVErKAdpvKqIbVVqMgPytKg3kguP1AZ2guHFKgF'
        b'Wh73VqI4imxiKhx55Kz60R6TswrFekJwGIHH9g2rEzqVjoVzdB09/0U7w2HnIOu9iPMiwc0XSiLJRYqCMHomqjcPR5U5AkWVa6Fk8PpzMrpKbkA5OLrKlypAGB50/FFJ'
        b'05JcUtQkso9E3YIQW9H+rKEFUsewfE9OmSjclx/b4jtYJacJJHVyInuoMaOcmpcy8VEl32AVH1bZ/hTxNGiwodolQ83MQ+0ST0LHkuGA4HaPRME+k1JWwqVBpYRWuEE9'
        b'Wf5K2G/tmoUzk3gmHq5BBx3lhCrcvLC+HByucagDDmPX4Ejzh/3QyMOVHMEFToBSCl6hmmlNnt3YiNOLcww64CYX7u/341cf1EJJNHk8gpFPFQnBpgyVwp5BCYQoH6o+'
        b'akujBvnSaFqNOL1ts86mMM+KMU4jNBU5ErE9TeUPoSqq8+jcYH1RE/YZe0mJgAVJjpaiSiZ5oZdgOE3b3YapcYNhmBpvxTpEvWDX1rWoc7qIVDLNQmeZbLQDXROq3sal'
        b'Q629HXTDfgvCeAdJAjSyxgSaj0AH2mm63kfXYbdwxU/cR2U0lMfDvnDc5gvFseSyP0y46Y+LRR3T45eFeZPKNeI/l8dCOaaq1dYhZhF0US2LhFOeCjtU91i4CEWnKMOc'
        b'LCQka7W8Y5GrXRuwjknAQYgq2FnU6qwYrPkzT+ZCVJ6bYRedcj50bFJ4wIHHpmSgThDSHsXIQRFBkdUjGd2A60Jdwf5Q/8eTIOjJx0mQ1xKKVPZsGwabgMeObdrIrM2x'
        b'DFXrEeic4+P5VcxYU3q1x8O4ghpoFtGyoczBnCEPs/nIPbCteIZDb6hQ5xdPWLvPe0UYMRRqhXFP8LF/ywhUvnI9Lem7PdOMJup3gjO9H6RvZqgvnp2Z+aSpoe4V2NLQ'
        b'OS9TVNShZlSMOv1x+gPlG9k4HHSjPagVOqJzSaSBZRYsIRH3YjK6YKSlm/tRMxwgUT4cqvGXA3Ad6oSKFVO1ykUz1JG6zJCKumexmNnmK/Wm5AftVMcIc6K2OXRSL6x9'
        b'1Kj2OrsLaGxLoVj4GmVC5ZztQje/gFwRA2fy2Ag8Ai7guEfMc9PKbX7+2DxZrML1OHieF9E1ZuPsqMbPfyNLHku6ygYz6FzeAsFptcMRtAevAm0kw1xGYn0HlCSarsOm'
        b'oT3bcOMMjOaptWwozplnhhkXMaRo5pgEKz9OJiuwuKAyHtpsUbv/jNiHmr5MvuKRoputNokI2+IxCRyKcaToboUDTqglDJVilAuYAqgPFLLMoxJs4S0BqJ1jUEMk54xD'
        b'TcxWI6mFHj29AHv88gScGmxjtnHp1M3HzrHm6bNxeaplHuTSmviMxGGqkSi3QPvdUK9xDvFtqJq1jo6CcvkKk7ZBcWJYxPLwyWEJAh3oHDbbKLlPdGQMzkrPQJsE7dHQ'
        b'OhsqmMp0OAu1bqn0KUIfdBHtFmzw+GjUi5XgAsky2zfBQQa1cNCNR1FP3Q1HXBSpGY/ngU3YSknwMaA60aAZJkkepZHjaGu2N+whpZw9tJSzl4VLsN8fbqAao4xY+IZx'
        b'w8NcB+p5Msw5mB5FmQB7Fw6pIIJq1OjuBlfpOhwqhOODITDcwxQBHVEr3dRhT3g1+8lUaTecEXKlOYG0wlvzWoxBzF/DX/MnxRsTXtOND3H4ov/ge0eOdOddf/H1vSkB'
        b'O39TfN9iyeKkmzusUk6u0YcVHlYkoKLq0HveJWVvb1Xu8T9u+fdqkLwWNn629DeiPzdMC963/uWdFsHjHZJvtU5QzNjwmuGbW+8sf2d5cuIJRVxx9jdHcwp3134/KvzM'
        b'mY+3Nb35furYD36+dXBS2+mqkfuTPetmjfxr2azmVnF61Ibls7Ne+34gg0movvjnt/+cJ838fZpnd8vaO4tHv1dVmPCX/pUHtyf7XzjV5uu+TOIVoVL/pXnfbz5RxcT6'
        b'Kw4f/vze6NsZN18Ujfu4gPfY8RPjbf5tYLe2bu/95IDCT1dMzXMy1Jy42T9/1Mpdb3Tdt/n41cVjo9U3bn42qenWjo0ucuuM+PrfBJ7/sqlm6yLFuUMeL8//PL9rn9Tr'
        b'882bJ2k2n76/N+Yf9+dqjWbrfEWr1fd8VNN2HBG9G+PU9qXLXCut1e3am5E3Xrkte+5Uxw/Bx7jzXzudnx+xqnHLPPf4pfxdi/nzV2/82T1za5y5k/fdaXdXvPpjeuY3'
        b'WSuUbwVkTB/1tvG1VtF9/28z016bNSJ+5JzZtZ4pb0jPRC387voLE2bGf/PC8ruL7n2jvSf/fafms9gR41y/n/hR9z9PrFjz6btuzvX3splwu2+2nU80OAd+VxD+fcLM'
        b'5U1/2vuPd4586ZWjuNJTGnuhJyuqQPvp3jW+qz79YdZn8y7dysxWh42+aW07/oNc64bABteUSbNv/2P84d/dk3T8PH79T/YtVdtt/7rgR8/8iR+8e/+ShQ1fGpIxOq50'
        b'4t8KVljmP/+505+/ylzpci3sxcTfJU5464bl6/47rovv/6X4ZGL62LmX7MwyL7o23R9768q774uXOt7e/tPNbT3LXorKvnPt5X8uXfBza/C/6s873Jxdm+18YebJwJ1e'
        b't3bWR78X/PqUHzf9NsFxXV/XuvDDV+7d//v1GZUfpfropo8OtE+2P/na66q8l7/t7Yiv+ij9/oZ3Fxm+vP3m528sn3DC9sjimOBAl19ePfLx2i9svpMGalpqPmEVX77j'
        b'4W9211X5l59gvOTBzTdudL4Z8MP9n75/PffNa30L+62P2Veuyq/z6rN4Idvz5V8+Phu79OXtiyuuR3rO+tr4yqVXdvukrPi6JO8711Ezwt++XjrQYJX/579v0f21pbYn'
        b's/7m7B/nr/5hsdUt/i3bvo2Tb2jPzNA6L/s+bkrlpK/bP3Q8eHXz7u4Pttwt21Npv17i9Ne3nCrGzBNnLvxTxVtNlWPeT7830lCW0mVbub5tYJFd4T+XPHj7lSW/OG7k'
        b'nlO/FnLihVhpTMmciXdfud1yX1XgvnRX0+Zxtv/405Sunp/PqEr/dvLKd645P1TXVdyW2RnIhg8aUDU5AiEFN9jgiUuVk0OQ486oRxwGV2JpLZGtI+flSQp+UJ8M76at'
        b'VnKoefNoWuE0BrVCv1Dh9LC8CXW5S8XrzNBB+mwr3nZetvcaWsGE07sd8jQ4SIuGLBbASYU3qWAKg9rBIqaIdbTmZ3wu9D4qsIKTQbTGCm8QDKjQQLIQ7Ccv2QiVTEPL'
        b'mNbj2NUYjxoMJDwutk7zio7yjijgSFGSJbrC5c2ZRJfO1KIynMSV+MoZxjyP06KTPjg16KFLoxJo1ytsSDhSPKTMfrpo/WhUJVRC1aN2ODY0J0MX5nrOmEpnhsNB27yG'
        b'VEiNRBV+6EqgUH21D2+tGh4+7HsDKgef9sWZyQlKVg4q9oROUiuFLuQ8fC78eP48sYgcGchG/f8ud3pqLY7tf36eJx5TzjLM8Z9O66GeI3U32/HL0fJhfZIdrVCypFVJ'
        b'HGvDOnJCfZKE49invYQqKtLfhSP1UKQnqVMaxUnYoS9hBjth1DPmEl6WnB0rZc058vi0A+sicmDt6BpidiIeT+qkHDgprYPCs5oqpCzpas4i4VMs4MDZcDYUL1qxRdfH'
        b'b45QQ0qYJuG/zWkNF8WOVGVxEloBJmHHsy6sM24fizEQs6QOa5AeB06oFSPfyLPYhC69PeZj9GAZlpicpw8pv/rPy1DG6h0GpUjXeoVIj4CYHUzvlMefCM+AHrTLVJQF'
        b'lePRbjlJHBlmbI4IruAN07Cn8YkKBJPpSLqoJr/hwqzi0thVojROeHh/wIHeCtCKKX2IXp+tf+Aq3BNQddKbCqDUaVKlTqom7T7RMvGAZXIyuVhJTh6QJCcLP9aCv9sk'
        b'J+calVpTi0Vyclq2KjlZ0NFHH5ROsrcewNjR0j1LTthw7twabG0HvQZrK0KeXG8yTF84Zo5OhpvB2VkyNlTzhrGf413x2Ddcls+vvBINwaNC1muntXdWvVY88t22L3+w'
        b'W3TyE5GH5dqSyfHPRbA6j4y25jGT/2lxP+lF9sStvi3Gf32xNfmLH2ITjW4HXq7+KeDlja0Xpw8c/fzbSy/+dt6H7qNjroT9yG9OjrUUf7H17hhdWr/d5OLRr8Tcn/Li'
        b'BFnHW4vS4srUdxeU5ub+I89N7hGzfPn8Lllc9Adv343+y/7Rq16Njep7+0ToEfOoglVdVp+9qT4w5+7KlOqp+d6dyDOztfN599XaTvDZco+/6ba0dp3nnLu741+ffWz2'
        b'uebdNb+b+Vun2rXxFV8tqbT2idoWHWiI6zX81v/ygwN7/5UQvt92jirp/bY57yTckBwtRZJbH0zRffuHojfLLZ6X//Tcm5X3bleoPR0q0Zb7rPeDpMakfTIxDS1wfAVO'
        b'MEsjWYadzaCyaJzd70RXaWhBXeOyrJ/4bQyc/B629M81UJFUwk44aO1JTo+KyUnUyazBrq6oUwyXssbQmVbloB08uhAWjbedxQalECdGQJUItU0OwgpO9dzxv9CVmtPE'
        b'+dkf1EVirdVmK9OSk6l/DCIG4ky8lT/2SKSyk9R6Olg6WAzzbWYmvyUav52xwn2JR3WwYfWjBxUaGxGHtfyRSxjxX0Miq3d5aD5kcSJcoXLzns9QJ0Him8NS1AQ9ZqiU'
        b'HP2QHxXCYbfSgrEbI5qA9sNJzYZdLSyvxh39xoROeHGGXWGww963tqfn2RpSm/feOdGHfrPh797Nk+/fXn0zalbf53v2nE/f2v3eS3mZNx4cQL/kxSedOvRR818vf35u'
        b'atLW3dUyw78Oj7l8Z82V3GkzZv5zk211k/fazneOfl7v+sI9l7eVV2QWVEnWbUHV9OcrYqDSGQ7i6GuB43IHB2cD4Szt4QTXfRUxcryrbvEg/WLkHNaiPhE6ARcLDMT7'
        b'yRdCJ7qKt9yUMnJYiMopZY6iieg6umwg2+4YvE6VwlSWHbxGjMWaRHOO+agoQiH8dpIveQAH7+ysZRxUwSlUT1OpNOtk028rBaGmR7+tBNWJBuKxYjZFeUX4ojozhlXg'
        b'zC5fPajaE/878oX/B50R/6oxaHQag8kYCNsYW0tWCJGWIu/tNHVQ6Mc8VHPpgEir1g2ISQ3tgJnBmKNVD4jJZTGOiRoV/iR1kAMi3qAfMEvdbFDzA2JSSjMg0ugMA2b0'
        b'51MGzPRK3Xo8WqPLMRoGRKoM/YAoW582YJ6u0RrU+I8sZc6AKF+TM2Cm5FUazYAoQ70Jd8HTSzS8RscbSPHcgHmOMVWrUQ1YKFUqdY6BH7ChC84ULusHbIVUSMNnzw6Y'
        b'PmPAms/QpBuSafQasDXqVBlKDY5oyepNqgGr5GQeR7gcHK/MjTojr057ZMgC2RP15IRKP4N8eJMPspHXk9ReT66h9eTEVU/STj05SdCTKwA9+Z0mvTv5IE5U70s+iHrp'
        b'iZLrPckHedJLT0xV70E+yCPPevKUtp5c9OjJ49Z6ou96orZ6cv6hn0U+AsmH10M/QKRj9dAP3A8d4gdo2wPLwZ8nGnBITjZ9NznBB2PTh//4mlSXbZCSNnVatMxST/wL'
        b'CeJKrRa7N6oH5PRmQIKFoDfwpB5hwFybrVJqMf+XGXUGTZaaZhD6OYPMeyzqD1jOE3KFBeQvmpOIOWydgq6tHkXcLPt/AOJ/NG4='
    ))))
