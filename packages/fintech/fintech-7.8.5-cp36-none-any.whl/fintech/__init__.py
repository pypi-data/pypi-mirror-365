
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


"""The Python Fintech package"""

__version__ = '7.8.5'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcvQdclEcaODxv2QIsRUQURF2NhYVdwK5oFDt1sUaDGnZhd2FhWWCLgoKiqEsXe++iYMde42UmxeTMJZdcSbgk5yW5xKi5krtLMXfJf2be3WUXsN133//7/T748fKW'
        b'Kc/MPH2emfkMePwE4b8E/GetwBcdyAA6vwxGx+exek7P65lKtpLJEOWADLFOpBOvAVqJTqKT4v/S0gCbxCatBJUMA+YD8wQe6H3yfS0lDMjwZcCyATofvW+mn84XX2X0'
        b'3p9eA/S+q5n54EWg89H5ZPgu9F0AzOwC/DQH+BgUsocRvnNz9fKZpbbcQrN8utFs02fnyou02fnaHL3vVxIM5FdSchHhSxsTk80428HhP1/nf6sSXxzAwOgYHbtGWs5U'
        b'gUpQzi4TlzGVYA4oYysBA1YwK0i9+NknV8Gps10dIsZ/o/Ffd1IQTztlDlD0U7eBf5DPc02kevsiHkiBpswvQSMbuGIy+FLI+7eJneChxcQReFgHcHAGzg0T8/QwuQr0'
        b'holX21X4Pg41TJtTkKxCW1HjXFSlfAFVodrYWYlzE6NQPapToGpUx4Gp88TotCneGLd6gMgajbOlRRbc19zTmAwPNLe+UG6M0iZqH2huZ4Vk5xpM7NnVKfKwMQvB6sUS'
        b'a5tawdqewzmeR2vgGT9caDQpMs2uispFN1FNLAv6wXM8Oo0OvmTri9PB4/wUWAvXo/UpaO0QnBLWw/USEBDM9ZXAfS1AwbWxkQoL6R3h4oMvD4PGGyyFy/RmuUEY9Alt'
        b'AVqrVW+xZWbZjSab0cySxpPRAWEyJoCxyFxZcXm8wW7ObpNkZlrs5szMNr/MzGyTXmu2F2VmKjiPmshFwVj8yb0fuZBCwknBAaTgu0GsmGEZMb3aB+M3qAbtRAdTlDFq'
        b'VRSsTo+CtYUenaocLkIt6Mw8EwHjlQFvMrdFIHHvsl8wP/bKyPwJUFT5q9nO2qSgKKFbjPaTjCM9nKhyZyL9OprLY37DVvTwlWvGfbLCJGTJCGIBD+708QOa1JkxRcLL'
        b'qdliIAMJcUCuUQYGvwjsBMlnRsb7wWYlhqYKrZ8TN1sY+sgYVeRI8i42KimNAYsWSlPhriQFY5fjLDPganjADzcnReUrj41ENfA0bOZBOLzBw53w8Hx7BE7ErniOjGAs'
        b'HmzyXwL8QuTpLNoIj6Bmez+Cjfj1VWGQ0RF9itcgw9MDFZy9B05l68mkqBTJabBlmQiI57Ch8DS6ZO+Nv2hWoKMpFD+TklQs8EMVsApuZ1Fz8kxaPrwOzw9CtemoJnlm'
        b'YFoMqk7FWAWCYSWHKtDFdFw+ARNVyOG1lCQlOqFNUlGkFIEAVMOpg+EmeyhJcAVezMcJkkSA5xkNvAH3waYQ2g9oC1oN1wqonATr05JQvSIJV4E2cfAqOiPD3UWrODVF'
        b'kjJseBJcBWtRfQpqSMdlBfbnxqHrL7mS7EItRSQNupaelCakCECnuKErMKIInT4P1i/yw5h0ORGPVRGqRXUppNkhaDeHjqBtfXF7SK/Ix8BtqFapRg1Jyhgx8Auww3Ms'
        b'OofWoYv2Pvh71EIuGjWkovXwIDyeolSokkWge18ObUJNcJt9AIHlDHKEp6SrkqJx31bjnqlEh5NjYxLTxEAJRGiHyGSnJLoebYKbCRzR+FsMA/xwh+9BB1l0Ca1JtUfi'
        b'JJlo7cKUiYE0DWnVzMgUVRRqQHUY0WaqxGAKL0YVs1GlnbCGNHhKi1NWp6fOikxMRQ1qdAhtSk2fRxIq40XTAKpzMzPWk8Fup5zawWDuyDl4h8ghdkgcUoePw9fh55A5'
        b'/B0BjkBHkKObI9jR3RHi6OEIdfR09HKEOcIdvR0Rjj6Ovo5+Drmjv2OA4znHQMcgx2DHEEekQ+GIckQ7lA6VI8YR64hzDHUMcwx3jHCMdIwyjHZyYFDFYw7MYA4MKAdm'
        b'KAfGPNjJgdd4cuBAJ5/w5sCVavtASgyV6EQ7j/BkEOgY5RFzpbTbJ6CzqJkSllqlUGGMxxQTXIoaNRw8ZeknYOx6dBynqsXoyMBGDrArmYQlL9h7kk+r4ZY50bBFmYix'
        b'Ge4zwzUMqpxWTL/B44q50QpUF6BCVRj9xPAYGw3PdaNF9hMHk7FR4mHm0Q54PImBN3IiaTb7PFiRgomLfJoM9/kwsAkz+ev0Wzd40o65SSKq5wDfDV5KZOA5H9REi4RX'
        b'0HZYHR2jGA0Ps4CFF5mMceg0zTZ4OrqWAo9xqEaZhEdfbGIj0QF4yE56D14qh9tTME/FbAPXqIQ3n2PgSXQBXrT3Ip+3wUvdKcLJURWDi21gUtE1dMoehj9Og0fhzRRU'
        b'C3ejExjRlAwQj2J72mArBSjXCquik2FTH0xZ6bj9CWwAvDKblopOGeAOUipqQrujI1U4Ywk7tLS/nYzlDCVag4k6MkuHm2FmJsBWnpYXIIKrceOTUXM2AWQ7Mx3DfJAS'
        b'KaotQ5tTSIEKQsNSzNHgTRY64KpwYQSPo1UDUW2aErOMeozuZcxEVL9EGKXtKngGHsddA3fBdfgbPMfMLR4rjO6+sHkpSnQKHVATKuOBOJz1neMndPd6PKqoNhGeFGFq'
        b'Y8sxNDfgespi4a4FOZhPxkztQeCsYWbArVBg0Znwkj9mJqSw6Jgk3C/oWIpaBHrm8sMwgztIO3VeVFBKNBEByWSUfWClQszCLVloczbrRHy+kx6DtRgH49Zj2CqsuZRz'
        b'mIpYSkUcpSJ2BdcVFbnI35uKOLXxufhczvo8fnFm0tIeb73iD+QyNqH5t6/+EPGLo0m//xv64NPKRdJIX7juYK4RrStQ7fxdy4m/bN225voff+4N4fjA2yEBUe8mKiQ2'
        b'wgNHo7oip2iqhVWoPl2B6pME8RQ6iOfQ6fk2wkyj0+Fhl5riFF/iyYIAuxBio8L/ZulKSq3KNIw91e1Srh/cwMPz8BLa8Dy8YSOdXbQMbcFJd6HLcH06Rk/YQNL5okY8'
        b'xMgxiaZBa9AGf1JeOqE4WI1ToFZUDwI4rj9aJbJRZD0Lr0dEqxKpyJKi86x6IVyDHC/ZCJ+BlXhwT1CIqBSgEkCAaCJsGRQlSlcPcWpEHXQe+pZqPG18gdaaz7pVnhVS'
        b'RvgNYHwZSze3TsW3cTqrrY2zWrItJKGFcEAF66FGsZZgct/dVTLNvNJdcKWXLkXaNt2A1QdMF6hBjBnRXoOS0H492tG1zhwj4BprYJ9SY855ssaMMc0v5CPG2h+/6FUx'
        b'6D7Wd+9qbuUfyXqgSczOM+j4s5VhY95n4n/DH50bgrVewrPQ1gi0L0UZiQVkE+aFKQyQwuNsKVodLAzqiYXohCca+cFNLkVoNjoqdCbb9UjYbUZTu1a7EkiDGEsIaNdq'
        b'ucKsvEd0PmPp4e53kqWKFENsOVABHgZ49jzlLddRfV401ZAw21VpLAy8CS+Xuzuecf7NcQFTBqg5xqgFUJy1+XjDH2AuzCzMMtit2VqbsdBcRzJTtsHaFQRbD6OGfMwm'
        b'ad+kJ0er1GqiqGL9gQPRlOufE6GdcXDXE8DIfQIYPi4Y9I0eEBDFrA88PQvzRqFqTE/B/bB6VcnBG2PRta6RbhhBOoagHTbV+P8G8ZguEU/UnsDFUPu566MM1cG763sm'
        b'lkrqC+oK0YvvXxFZk/GLvNgvjn9+T/NAc1dzL1tm0GgjtbfuvvpF1FmNrlmP/4LvaU5pcw0n9M3a3CxZTpUOC/qMdfHrpOvGH5HKx21fNZwDMMRfv2O6gqEoDxtRldgK'
        b'TyaqVZGuAe2GGhNCOYi1TwYPE0VRviMP6oD+osxsrUnAf5mA/6Es5kFBmBctC7fmGg22TL3FUmiJGW8qxCmtE2JoBhd74rWWHGubOH8p+e9BJZ3MPdZCJJ0l3E0vhBdt'
        b'9aCXB8Ge9DKK0Ms6dMmANW1UlRodMRHrdFjzrYnF5s853N7qdDUW/fAi1qBrJbPHAlgz0QddSoNNxivWP4msBPWZjyfn5+Q+HJljylFnq7Wp2rw/Nevvao5p72J729dw'
        b'J5UD+tPik79d6MLrp+owP49O8WQbPYLElt7tbEOwbh/TIZ72L8m32aMv/uLVF0S1xxJtN2pydoarK1hYKwe94VUeNsPTS7umpU5OmGd0eHRWFHj1XKNu6su8lQjD6O/i'
        b'U3B/VuUkah9u5jfWKeSjum/X/UUjNdy5DUDOh+KKtmEK3iYnCLsLbaL2LOZGx9LVSpVaEJrd4HkONmQl26JwohJrIZWs2HaOTFbFwIZ0uG8YbvX66CR4MpJKa7AgU2qI'
        b'NFJniAFuiRRkOU4imemRKBxt4bGNfX0cTeeLzTdqQ8cqklPVacnYOBJ0g4HPieAOW59QeMgTCTyG299uzs7VGs16Xaa+JNuTTvqJGeHXEtE+7G0cTuUx7IxrsPu4B5uk'
        b'3usx2J/LPAd7EOmp9fDqsGhq58JrKxIxbdelpOFBx8QuBoOWidKx+bLNPUqu4e7pwcqoHfffsU7e+ec96FK1iTT7Z7mPVDcdyPWBDQW7rB8ueilnVP8bESwQVPwDCcZo'
        b'VRKmyAvArxzbuQcZeAFeVVG/TFvOPwI3BzKRfws64fNTr3Crj+BPmfEiIF6WkjOFp3XjUiKFlxXLugOCXHF9bRL7EgUwWq8eE1lL8JsPNz+XotVpm/XN+oVxJ3Lvaoq0'
        b'VSeb9fcwUd/TmA1Rs49r38pK1OYZ1tQMZV8bEDU5b3vFPV3ejvxe+dtfWxW/akSldLtauwS8t9bwJ9nash7xI1OnqRLGHgkJlYhN9yqGnfhWdiF17Sz5v/4kG1n3imy3'
        b'Cnw+tf+29Z9gnkuNjhOwYWiK2wEhhY0sixoL0W5Y0zXfeCI34XO11lyKVXIBq4ZIMfd1/VKNEOOFjN5hvaSvB4MJ82YwXdfPCMko4pHMRzwQ7yMvLkMtw2OoCrZiEwdr'
        b'hxgLYHVGD2KLHkcHH+NRZTp4VNnH4pqX2CQNl3XCNZnaTnRadMGObqJNuMJI5IgFsctUFDn2DOKBdOY/GJCgMU0vmSJgjN9YjEUlV3BajexovB5YCFPu6tLGZBr9C3/L'
        b'WbHdB+o+vqy6PTQAxgVN/fWOC3teVTS/KRqTHNPIxu/sMblhareP5GO39K6dk12bWzv/wd2V6mm+3OAHlz+1X6yq+6bR/lHM1HGvre4dvPrDHb1OzB5Uu9NHdPzDL749'
        b'LeoZf+He2bnX0E9FuYv2hn6y+OP/RN94ePu7Sy847nQfXj1m8MBQA2pbeGffxDe+6c8Ghir8qL2E9sMNZU6DyctYGgsvY3sJtswRxP6WfnFWpUKBajJiUqNUSXZBEoCo'
        b'hSJ4U5lB0bT/PCwiz6nhSZvzo/8EdAlVcCPiIqhreHwG2tDB5gIBQegkVpbRpsG0CLgVbccWKzqLbsagKlRNDH3YwKpgVRE1ymajrc95GGUStMfbLsMVHEH7bITXwSPw'
        b'clx0sgoexIVWJaVi69cPtrJoDzqbRhO8oEaHsW2sjFLEoPVYOcVWAfGCyfmXQoKo5EAX0HkZZfMDUQ2pTmDx1K67uAKdsxEch3v90NWUMHhQGellIOhtxHZ/EZ1bFq1W'
        b'FRcl4b5jgUzKSf3gdS9l/jHWmrjInmUyCtx/oECn8Sy21YIp/w9heHwV7DdffOeL6VXGWOQetNrDm1a7UAbaDQmS74oHmb7pZcKRpi5FW8qiI9NwX1SnioE0OQudYWFF'
        b'CWzNFjsJi9BPgIuwYjiiw5cxYaBcXCUpE1eBSrZcUiaxqksDyrg8UCauZMql84E5hAc2Jt/XMoYB5PdFYA5dgBXfMinJWSYmZYwHOobkbWQsfJmoKMMIykUlB8tEeZjO'
        b'p4LFWxex5T7lvqSWMp9K1mKg9fH47lSZOA+r0OXiEgO+42nqkHK/Kg6n9CtjDVyZbwPDgOLNGI6pNJcMQymr8qHQiUsGVvlWScl9JUNzSmlOqUfOX80HZTLLN1UyIYcL'
        b'3pmg2DAfNLLmgbRUv0oWw66sYqpAvpjcYWhEOraSEVI3MuZ/03SMTWxgadoXqvycaV+oYknZ7pTv0ZRimqqsSuRMhe+8Up3QcXkSHa8TrcH24VRAWlDurxPnScr886Rk'
        b'Ho/M7pX7l/njvGd0PmX+oaDc3yFx+GG1jdP54nzSMo7kKw/APRBQyeik+aTGT8oCdH54ZALMA9zvefz+3zoZqZG8CSVfeZ1/eUAZ28hapmN4GQovaxmoCyjDOXpiDm1g'
        b'cbpAs7yMKWPzOfxtvC6Q3DvfS3VBZcLdAI/8Gl03Ib87DaktsCxQFzya/PfHaRrKAug1UNe9LKDMn5RHvpkDygLJl6LtZf7k2SaMcRBuRRBuRQhuBWt5WBZEWqcLx33K'
        b'Wt4SnnCez/Edxkddb/r+U+GJvMet7KbriZ+BrtdaNgyUdaPwB+Haw6r8SQ15vmVBLhjKuEbOIrcxZYGVzGrGLLX5CXdOJThCPfehxIQNarNq6ENWKXeLP9YpAqlxTEz+'
        b'HExai33LmTImD2xgi3miTjlVyTZpZqZZW6DPzFSwbWxMXBtj62A1P/QdbzJabdmFBUUTvgdOs1kMlkVk5+qz87FJ1W51tSd8yMkLLQ8Z5VcMLaHQILeVFunlg6xeQIpc'
        b'1C93ARlKZmDLiHxmrXwVBriS8QLY5SQZSMXkksfwQwuRAP9uh/crUunDQK18idZk18sxRJGDrAoqbx/2suqL7Xpztl5utOkL5IOM5POQQdYhD7vRF+TW/Yqn1+4eKV25'
        b'H/rIC+xWmzxLL38YqDfacvUW3GLcEfj6FWGUD5khD5kBD30GWRfGxMQsxm+JYvGwm1KeU2hz9VA8/sMtHEnaMEpobfu9rE1kNOv0JW2+L5BmTCMGHn6FYbG28dmFRaVt'
        b'fL6+FBu7GJ5Cnb7NJ6vUptdaLFr8Ia/QaG4TW6xFJqOtjbfoiywWYna0+czFFdOSFMFtPtmFZhsxJSxtHC6pjSfI0SamnWZtExEYrW1Sqz1LuBPRD+SF0abNMunbGGMb'
        b'hz+1ia1CAia/TWq0ZtrsRfgjb7PaLG38EnLlCqw5ODsBo01UbC+06RX+Xeqhz3LBMirJLRClLgR9GziDFgBLhB/PELEYwIg5IgwFsRjsVGUDmFDWlz4TgUmFJRuKn8Kx'
        b'YhvKBIlDqDiV4nviBA1ggliSX0bzB7BEqAawJBd+wwbQ8noxEbisUCJyWTopEJ2INmLdPDENNaiV8CS6lIwVm0xurA+qc7vSpZ7EcQ9fsAhjSz4pA3mACqX3sAjjyvky'
        b'zhpRHGDDSiz5M2Kxt5srF5WJytgybjwmI8tsLBiZfDH+j8VHGMhjMcvkwmggBhZNPBYHPBEgVkMZn8OU8yULynhc+kwsgjkiXrBI3FtFRS/OT0oU6XhcCkee8H9eCOko'
        b'Ngkix3JMxxed0BGxLSqT0NrEwvf5AIsbCgEtiR0vPPPOZ348KA7AgpGlbE2kxlSdSEaRDiXxSwmPya53CpFlPBlgzqq3tXFana5NbC/SaW16ywTyVdomIbhXoC1qk+r0'
        b'Bq3dZMMoS17pjNk2ywxXgW1SfUmRPtum11lSyLvpJLP4CVjm4dMkwQa6TFe5fTFjsw6mSMZjdCBIFiQgAkE1il4yphcbhJ+DMELYh+CUcB1swEqpMLkNq2PJhF2aMMcW'
        b'LYWb4SUR2oqqGS9ThNRN0IjW1Wk2FJD5UIOfy84pY6hzFlsznqaR1IVZOnypIuPMVGOxnweKgjCe4UyWERgz/PEbhgjTSsYP2zxUXNEgH8yiuSo/cl9NAlV4DASp2heD'
        b'IjNI3Z5JnzKWYFBH050wXOL+p07NBwQAvozoDaC0ueQlXC1XBpz6k7qcxUVwBLBKJh8zQHJXhsEo58whFDgxRu1EcoffsDOxFkjf9Koieg0mAQN+JuhONa9e80HJ5DJS'
        b'bnw5V0ZLxWlrqsQYTTlcP2+WkXv8nj6V8ZYiIn8wAeFyynhaRtF8Er8UgzVQ3iYysFgL/YTBuiUDlgXgjhIR2UzjlfBvuWiFSIhXwsSBO66BoXYlo8YYRtTjNskSrYX6'
        b'JbkcjMWYj1ryl1rGEeyaKuBhuysyjVwo2r5E0V5vsSikT80X2zFWlkk5YhGuuMA6yY2vGEtZlmCpjLBAlsXPvViKr6wM43EvjK3hzLI4bXa2vshmbZf2On12oUVr83a7'
        b'tleA5dYiUjVph8vVSF8QrFP4/bccnmuTkG7DhCsUudjdPB83QGMY19QSJzD8vpj5hoctC390G1yKxUJSnIHc+/5X4mehGxyJs7KRjNNvADj5c4IP6hpsRQdTUtVqVWT/'
        b'oQox8Ith0eEgmZdPU+r8b30BX/QgA2t9GSyldrHLj5HBbZYKng1MgD4GzJR1/BppJZPBu98TziDBHEFCY/LIN5ED8CBDTFmtpK2bM25uutGkTy3U6vSWrqdzqcuOxcVh'
        b'luMx+8A924Rul4FpQ0mP3IjQWeHJyMS0mKS0WcSWT09NUs1GVelzIglTTAmm8SFwNWr2eREdQweNPccPYK2E3TcWzLuveaC5p8k1RG2NpKFpt4TQtKzBwx5ofpX1VtZf'
        b'NG9l5Rl0OnBM25CTpJUa7pgYoEr0i5v8hkJEjXcddCBHb3QNnUN1KhIMVex0SoTbebjOP4bOAmcOlnRySMBKdCmY6xsWTp0E6GLYcO9ZWxBgRJc4rn+pH7X/TXDVMs8p'
        b'W3QGXoZrYP0IGyF6tHPWi7B2qTuOhkb/JKELQm/AGlJ3LKpJRevRxkIyS18Hq9F6zJ2J82GHPzoA9690znk8gRNgpd9oNtoyMz19xStBLlFiAphl4Z2wIsaVwT2nYtWb'
        b'DG1iE/36+DmVfHKf56rbYsSXHEITxP4HFfh3l6eP73GVd42bowTc5DCqE4EoNojd+Mk/Fj9znzwbJ1HTaJzn0MtwbQrcEuIeG9TI4dE/xgXloBp7LE4Cd6LWAahWluuM'
        b'qGyPhkLuwIILswFYFClBm+eOp/GYyZnwGpn2jJ0VGYnRLVGFamDL3MjkNLReGZOkSo6GW9MYYA70eT4b1lKvuy0eHZ6jeiER1SmS01LlY3ByJ7XghCPgVvFAVDvWmPaJ'
        b'UmQl1l/49v33NW9mNeubtbeyUrUmg3KrQpusPaYNyiEE8kAT9TvwzY5JD8LXBfzOdHFAb/m+pnWTZMpM+NEr777y0e3Nr733ynu3e93+xXepOxjwwbLgye+FYoqhXtgm'
        b'eHA0qsU4iJWXxjQR4Psy8CA6CzdQ7x0DD9NYEi9/WQ3cIedfGgi3CrGfZ5UJHvSWleFBcb2X0RCHnqjFHh2jSlSxQAwPw1VoIxsHT6Fd1BdpXliQEpOcpkyC9S5vJKpB'
        b'ezFlDZohykAH4WXXxMbT63T+2RY91iMzCwp1dpOeEkeIiziKqdOMFawCGbOsX2c89crtokSC+ZhciMBqJxPRo2UIK9BKgZtgTKSxXgSzOdSTYJ4ESNdUM95FNS7lkdCO'
        b'1ODzlLSzpuN0jNtccdNOgEA7i+ejTSledAOvwUOUdqajk3YiWdBu2DhdIITHUA48hByUeuC+UZR8XnoJHexEPmjjeA8KcpLPc2jLo0MHdB0iGNoYQ8fAAel4k7YgS6ed'
        b'sJaMAynFPhdfYuHLJVY3uDxq9ObY2M6DJxPTsI7v8pajLV7zwtywYCvcNDsYnQTwBFrXDVY8P4IGZKEr6KLR6WevQ7VK53RhUMBsbii8FOBuiwh4RAhQPijo4ywZUzcf'
        b'5Kic5vFYcnQseTqW3Ar+UVECfl3xwbH4fkwuPJZCJv1iiuFNYUJ/TmI0idKbh6lYpUANqUnz3KMmAnC/3hezzrNT6QSIPFkE/p0XBECCRtY9dwCgfFMPD5mEIp3lCYHJ'
        b'WPSTYAws64+olYS5Faz06aWE5+xkOqfPElidQlhPHdYWIlH1fIEHznLWvGMFrnweZrWoVYJOK1Cz8VrVrzgrkUOzjFnHbV9hfeCu5k1DTLBCS5giYYRKyz3N21hX+FVW'
        b'knaj7lbWSf3dhE9/GwfmjWPmDa+c6xj+ueJM3OYzemuPprhhuV9VyGeua6qctpsZ2PvNxjdCmN98TBjmG5hV7hCD347pdWzeRoWERmLNQi1oa+cpE7QDbhZizNZifian'
        b'Yz4ZrXExxAlp3irICrSfloZ5XCVWQLz53k5MBvUuvndjuDAFcxydHeacdU5Hh6OcEzX+6CzXS4HOCjXWojNoB5nAFeamo9GOiTFYHQ1ewWHVYkOuME9ThGqcSZqThSlF'
        b'v9EshqNeRCsKMcNj7ggPWInrdUV5cPBMydJn58EBJHQjs8hSaKO2OWXC4S4mvBIEs9RRwzNB2GaR0fmNZSM7c0B9iT7byf/atX3vkgVyFwlmRLu19aTZSuekpr87A2XS'
        b'RfiynnHJiwr6+w9PNm0nto8hFdZYH6HfeXCL5Vgd7ZJhkIjzjWNRq2gaupIALwyCLQowAG0JyYuHW0wEuoVTe/H/DAYJf+teyuzKWTv0/ek/MnRqGw7fwdyO0Adi2hv2'
        b'0bBPAncB+vqnsn8E6vqp+rEz7zA/9fpL7hhgrLKNEVnJ3P+ndVcG1Y2jM49LTW/sWxOs8Jfc6fXRKm5N1p+hbaD+ozuJL4X/qk517If6WV/VX57aLzhZE3JiW1pr8M6W'
        b'O/6t9y/oP36+d9+A4Et335a+2nOLuFiU+/GU2vSLBX85/WbsqmsN6d/VpC49djVgy7H16/r8iL6c3qQ41Pq+etyAVxMjvx9w/OuBFyvQjpLdivsXo1uvffHV9Fk9RPfW'
        b'9/8JRDdH/efv/1T420hsHrzeB27pqJajRriDRmfWoz0UifuMk7uVEWx93RAUEqyMcOMpEvPhKe2qCDwT5Ul66HyijayCMWfAFoGgXOMHq3Bp1egA2peeKnDoUTrx4hmw'
        b'xUbCHEr6os3RcDc85VZg2Dh0RUGhxgRbN8BDOCSjVU6O2XskD2sLl9umkVRNmLTXPKVF0G4OoPolbougrxCCkgQ3+jh5kJDzeijJLAE90CoOncc61QbaT6a5cJ8Q2kIg'
        b'Iwn6hAfM4yIHwUohwvEabFosRO+nwAs0phk2sSXd4UZqIfkPgTs72D+J/WjMagM6JEwgV2C5cbOTZHsR1VDRdgNV2ggBpfWAm+AaEapNZQAzBmBVAB5/BDn6PKuFLnZz'
        b'Gj8PJkHZTKSLzaxw63osCTPjid8Y3/FscKAYX4PYIGZZn8cyHS/tT+x8185aJE8DK2uxAC/TqRhflntpgo4IT03w8SDhSqm/3zfT+SIzs02WmVls15qEGSBqmlF1k9bU'
        b'5k/WRmmt1mw9ZptOy++/8oq0+ThLwqXQhuQSwc849S8pGyTp5W8nNIZWwZuwIQ9tfhSTZEE8vCGGO3LzvRwLrillaxRod5boOZ2gCwEaocnquDU+xDlCHSAi6pcUuR0g'
        b'M7U23G1m3GXqbN6jVLe+PAZfnLqy0+1qkDj1K75KgvUrEdaveKpfiah+xRMHoFO37KBfdQ5dwvoVIaDI8gJvVTkAHcGWDFaVObSXaoYZQ+Y5UwxAzTQRFs6omgfhU/lE'
        b'Zaiwsmc1OoXOOZNhQ2wXTRcdlSgG4VZ+Hrr6vIKla41sdncyE7zSsbTl8XbKYQ/FY23LWdj+yA5l3YC7jWjqOZGVOOarJGHE3EwkhubZKO0DzQON2fBW1j3NV5qvNfmG'
        b'U9gMjVyxYNh9TZL2TYPkvYSXQq3Ds/2njLf6T4mb4htkvYhNvucCb1UfVfDUn5IIz2dhvj1jsqcZibk2vIHNTMInAoah60uLoz04bJma5hyJmpdSmFNgtbCmKVi2VM/B'
        b'E8Ngs2C/1qGDmZSTgRdS3YwMGyI7XBrL05CoZ2yxAWNPJjHzKCsJdrGSlUDpKwtheE7KYqOxdyd0i3HnEwhM3MZlm6xtUoPdRMmyjS/CadvENq0lR297onbCW0rJ/TJy'
        b'WU4uZW7uQWLTWjqoKB/28uQfj4NOwaqJ75pwEAuxgCw2ykIpWRfobbmFOlqBxe7qlq4CSJa4gVmKL0ddnlHidKZrKCN8BxpC22lf6r0GbpxcDI+iS0OpMRG8lKN0FCf+'
        b'o6Z/9yzgNUniTbVe0yRuqgU04PDRi7oMHWctOltF4YL3Ep6D+9AJK9YgzvsV29FFrBdcQq22JeiC35KhqArWBxbJUCtZFXtEhM6kwNV2sn4F7h0JicOxOlX9wmJUH62e'
        b'Ry3fJPyvOl3lWpoLT6IqZQxsnU39n+fhVV8sPs8mPXbxMEeDMp4urNLQ0UfbmTeJBDveAlv8omFzqnt0QL8xoPtcjsbtH6Kr29LRLrSXEFWqmjQIbYnGYvxl2BLJgHC4'
        b'gbdg8lpr7ClfwFpTceofY5fd17z15T1sjeUa7uruaaKwDXY76zYbM+fszrBVZUG7rlQq1g5d27IjbOAfX2l8+yXd719pfI2d/cqtd18Jud0Ig6ixtfNit4QvbC6v1Gas'
        b'DO6OjlGgGiUeNHRWBE+ww9EhtJv6kxLgFnQ6miAVgOtnAH40A0/hV/uoP6q/Em6i3gRUo0pUxsFmwm0C4SouDxs7h4XQyu2wFrO/WrosrY6DB+F+wI9lYGv6AqryYSa1'
        b'K8UZ2hU5TgjuSkUvP3GhjZ+2qEiP6YxQurfTaSWYReZgZHQu0ZdZFoV5QKbJmK03W/WZBkthQabB6GnheBTkqpVygceGdS13U+UKfHmnA4s45xXaNZt0ww7YOiElXUXU'
        b'TddYw/p06gfA/wWB3dFwSVHCSrSa9g1myXQMgA7uDSrAautqIbBzB1alsRGKu3b4KBb0gVdEaC8Dzw9eTiXfRLRpASaX1qVL0PlimbQIbuxfLCvmQeg4LicCNlH+Abdj'
        b'/fWMFZ1HrT7+S/x9A6To7FJCl8UiMHACOhbMl2fCa7S2wfDo8ynYJKAjCaSoBZurLFyXCRsodQ4na6mwMbsJk3J1alSyEh5Dm5cqI4mnIdW1OmWONAZbvdhmYAA8DFt1'
        b'8JzfFHgEbrCTeTy4Xge3P33+rX3RDpMvWot18S10Ucw0bFTUFhXD9UvRRXQJcxcbVpovYYv9kh03hoPn5vBwFX6sE9Yot8aPoeBuIxIc20K1qRIQ6I9OoA3c7AR4U1ii'
        b'flZT1KnMpahV5isGA+GV5Uk8rFk5jWrINLp1NGxZDs+xRO+XjQPj8jCZEy0FWwYt6WhTuioJbYWnE5MkQBaOXn6eRXvL4HHq0OuJXkbn/FRkQWHKfKHJHhwOXqDcbDHu'
        b'gma0SgKvo9qhdjInvBhTb80cXH0h2j0Qt3El5fQw0QcELfiLGGg0sm8H5DjXuJvEQGZTiIFcIzucniy8XDKaBfzMzTyJsDVPXQLsw/HLOQOXE9sumviLqqmPqEtoCqED'
        b'm0QV0vIwuFnB0uJOlWIRM3UqKc60ZWKMUMfQ+bi5oBePK049NiEHGDfM7MlbJ2OiufyLgWmNN9QoLmTtO/afdo5S3YzKytHdYYa9UFe1r7/SNF9laUpM2yYLmFLfvOPW'
        b'c3FD/yGXjQfvzNYOMf72zS+/L5tw9ffDr6M1wRu3j5g3M/LUyZ7vzSl6+dcvv//L33w/THMg7mJD43f+uubwG6H5J1DLG31/PH2jJnXgcwFfHFyguNc2Ja3hox+a/1X6'
        b'6zPP/3LFyB2NzzdcUn7X+wvDd3lnfv/prcP/+vO0bYGlh9fW/ZDwPp9e/bGjzafnyh33x9mWrUveXCjeWvLhH89Mb20d9+0PudcO+Xz0nzeav9k8RPJuQviWfauKHcvH'
        b'H0zdEtv964xTxxJEllzr8sHNxrGtK1594+Kmmi93hnYf9CBTdOr9K7JLza0f6OL2Bu/8Xhej/KGF37d3yuvh6qZb78dM3OUY9bMqdun1rxUrFkUfyv/PrxqHrCv5SH1z'
        b'wKC+Qek/M3arrameVQRSM7I/PPlSCsKMxBFNVqXWEH+SHzrLsfACPGUjQahj4U60B15FNZgLMYBdwkxC52PpF50fOiNweMD7phAGj7bF07k3FVonTUldAPdHxQjf/Uws'
        b'OtwHnhWm7lrhyzxdUE9wgszO7YWXUS1bPgjeECKE69AWS3T6YDMBiGgkEgzTyyy6BG8k0vJ1WNI3pbgDe9He0TS293y0IDqOoIbu0agqSZlERYwIBKKWqeM5w4yBtM0s'
        b'2t8/BZs/B8gsKC5doVJjjadnKp8wHu4XSqhA58zRrkBnuAtep8HO2DLaLMQWb47PpIChWgng0aosFQNPYoI6SvsFtszNi05Ow/Y0L0MV/Rm4JwTWUJMcc/Fm3GfwbF+h'
        b'bMK1cSmYJHrCi3wivJJMg5NhC6wQuSRrcncxEaylQbRrFsFVy6NhZX/v6R6spy+GdU9y/D2dJexptffoUgRSsTm7XWzOIEKTp0HOQawvG+SL/9hghlx9uSD8LpwsWMAW'
        b'vi+NBfOlYTpSGvWFRS0bQAMigphgVsZaVrqkNbbIn82E9whHJIW81kG03vDUvimzQttU6OoTRCvci7aKwEs2KR7cC/CogqPyDLXAurF0Qo5MxmG96zSZkMNpTwk8ews3'
        b'F9Wq4clU1JCO5dIG4seFF1jUxGCBQpSXRLZ7tAo2w/1qVZQYG1P7seJUBddmc07FkMw1hLqUQxKU0GkbBuDeiIHx2oqBdfQwhLrnIkSPnIvgqD7K/2kgHkxfucfPbH2O'
        b'0WrTW6xyW66+41Y/Mb5eaZNscqNVbtEX240WvU5uK5QTry/OiN+SrV/I+lN5IYn1zNIbCi16udZcKrfaswSXiFdR2VozieU0FhQVWmx6XYx8vhHbOXabnAaRGnVyJxZS'
        b'qFxl4w+2UgyCV0kWvdVmMRKncwdo42msjJwYevFysp0RuSMxpaRIZ/G4hV1kydeXkghPIZfzoUNGnXwJ7jMMU5cF2K34o5DdnX7a5KQpc+gXuVFnlUfO1RtNZn1ugd6i'
        b'SppqVXiX4+xtV8irVk7aaM4h8a5aOYkEJuC4yoqRqwtxxxUV4bpIoGinkowGmkvoUDxWWVoCEB4rPDbWbIuxyNapIV4+FfdKArfd4qe2j6ac9ejSObFkRhBeQSfJrODs'
        b'+YlYK52TmCyaPXYsbFH4oiulY+GWhAFjewDUiJplYTro8MJ797LZZG+8B07MZ9yYzzoCDUFPOe/mFRdHOIW8UxuU6q4tPXfMg9Mj5Z7re+YVyJ3tPV5Nua1xYd8U1krm'
        b'NT577eZ9jeqLxGyp4a7mK02B4YEmKRts+CphWL1i18nE45XdBn7y5s43fvfKzoDD0ab47fG9Ep5rzHq7LkbWGn9Bs2ekbKOmXJHwa9OvDkaeqdb8WrnOEPfLdQfejYm4'
        b'9VaWyaDR3dWIdxBjjgFf3+67cHiGgqXWFGyILohWRVLXDqpKhzuxsKuCG6k0Qi0TFkajhtj+C7DuzNsZLLKOwQPPPtkkylxq0RZR4dG3XXisBIN4GvnmizmzEAocQtYa'
        b'KyxORuQR8eZEWY83pESX8UUDS9tlxpOEISNkoAJjFb4MwJBZQ9sFRgW44zWnRCyVtAFB0a757i7WHbfLEXS5fFqwIjYZy+/psDnQiHWopsdEe3HUb/L0a829omlEoKuI'
        b'AInaTuOc1o5H64bHjRg2aujI4fASPGOzWZYU263UujmPzmLbpBWrNecCpTLfAB9/tNXuB9fDKljHkp0CLvmgk7LpVBcPTUoGm4vKxSBIE5W0MlZQ0OcsTwSNqV9z2FzI'
        b'q4iOEZbUGTM+KGCsmfjuu10+Pd7oH1ARF8T/4uP7YeN9/tYjhF01Q/OLkf0ZkW/x0byHpoyROxLf8Pny0ueNg4a/WZf90WuvTVmXtHngazO/vpMXjk7+de7ml/f2lB3h'
        b'gqvzNEc/DvrXwaHF06w/hW0I+fCduRh3aYgfNq7OpChH9vRc55WJrgqa3B54cJHbi4C/1VEnAlqHdj8uMOTJQV2WQltmFrGdcaf38kTn4TxF4RAauxLMLFM+FSI7i3NN'
        b'ZbiDpB8f7kVTtKPxanyJ64TG73kt65wMqOu/JvzpENmWi/EY1cTC6vRhoziwBNYGxaBWMR3995exYHMfAqAm9dOwxYBu3TNEhQ6iTRgfY7DKtBXEZKOTNHH6TAl4EISH'
        b'RK5RMsEjBfwJmssDzdjuJErB9OOSMAF/6JeEQh8gl2JDWqMx/WHSMuHlu+NTQERpNENwMMPfLLzsM7Yb0PXHPVGkUfZbrBSWHuv6l8+ZMwXVo83zRsahGh6IZzPwRA8T'
        b'zbF1fjg471+Iq9eURYaOdS487t3KfB4CJADcWfrBdCihO/z4waPGOZCUgupFIGISp2EmpARQUQcdsei42/+GbjDYxsX2BKpSJhOHYgq+pzESxMtSTTT/aF+FGV6jM8H5'
        b'L0pAZOzzZItH2YcLFvh+Behi6qGyIVLpiyDuyKArxVt7j4nMCRw96qfh1YydqLFmMSbYc1iKpGHzZjVIg4fQdgq4RRYP1gz+irTGYpzTX2jNqIiJoGSMDwNmVli295nQ'
        b'h75ckT8ByKQ/YxzRWP4TNNXZ7ggV888Fr2Mbu8K6YBbXn74cmf17BsTkSUDQqsIFo7eI6Ms2/QzmsFiFh3ZV/oKxweH05d1ePZjv5+sw26ko7yVL1tCXvWfZwK3uf8LA'
        b'VizZvtzeg778OWIec7jfPBEI0qYsTV8s1D4zuJFJNc4SA01FzoKlYb2El88tALZRRQwGadn2DHk6fXkncwCTGLaHB0UV5R9E7xtFX27u0RcUFdXgLBVlH5TunUJf7l6Y'
        b'xtyZNkmEs+d/kHI6h77s378nkxC3kLgSni9ODxRqH93/XaaXaYYEaLSFG1Y4kWy436uALw3mME4q+nYbIrzsG1oObjN/x/2peaFv6STh5WzNx2B8vyIOv3zxB4Nzl8DV'
        b's2WgeSnWGWZqlK8stAsvo3sXgak9iFpxJytk8lDOuM46ibU24w6avzpx3uxXzL+JC+qz/usxH358JKH/H5QzI9+d/VPFlPVlYHagyCfmrsIxNeOVmGP7LeqYmuUtls9f'
        b'nf/3sRG9/vpCYuTZnC/+/Oe3d33Q+v346hdeuHIqwf/N93JGvNvob94ecE579M39v5hfum/m8AejwsOn54089teJz782oPn+gNAzIxf3nL1t9rbgk1N7F8CFky+ezBD1'
        b'nPuOwu83+dURiRvmLzzy4AfD0pFvK4omp/tMO174r7r5Ew50fzfw1NpVRs2vUy4Xxf0Y+PuXkCry6x6t/7yfFvJSzvQLn/R8+V6kftYrS66/bVh9IkCz/Ma/K/r8cHZR'
        b'0JIvkw6dkP6wO/zU1DdrX783zJLPXghdqou6f+GPd09MeO3620WjI3f84v7tT7699sH1tHvbkp5XH+x289Pg7870tO2bVv9jSYWv9cGh19nAv0vXF1cMKamZMn7Th3uX'
        b'v+73w+9nfPrFB72vm+4t+OnT3vcWf3PuJ//iJepfZk/JXDx6w0srQ5pmnM/59N2k8Ru23zg66Oahwtoxrx3f/8m7b5x959C3X5k+upX5jfWbHUv39C39z7JNv755u+56'
        b'vGhPQZjytwvHbnjvvs0a/NKIlcz+/Ab9304qpILhvw6dlLgdA8iB1lPHQPJQqikp4GlTNKqKJVuIHQhDV5mZmEWsE2bzL6Hq7tHwnE+yKkUVpRYBmZhFN+AGuJ6KqYnQ'
        b'MahdSqFdqFEQUxthLS05Hu4owHwkPQme4AE6M1dsYgeoXqQg9Yctc6NjFMnRzp0WA1GFfzhXOGEQLVgDV82LDn4hvaMnJQvdoHFJL6ELcIsVNqGrnXaO4eCZpdOfdc4/'
        b'6NnnrJ9agZS65CYVuos8hW5/GVk8FhDkyzOeO2eR/33x/174N5gZjGVgBCOmX3yJpskFM6FUVIvpbgpS6p4IwDmIq2JZ+KMFtyuciSwUaZM4LcI2ETXzPCT2/2CRHWdZ'
        b'Q+7pipS1bkFfSeReJ0H/5yhPQU9iCPPRnvFPJ+dFWKDBK0aINb7raIOd7jUJ18DquXQKyu3PdTo1kobAOhGIhedF6IQ9VJi6roUn0AG4GR4X5tmoN4WEkgahtVzfl+Bm'
        b'yghVKpaqv0EKS+o9o5OP2skODlgxOGPLVs4fMFF4mV9INlYFQRWLi2X9ZTnA+LwolLUewF8y3v1FHxIrlSCb+rVpwq40OFpaHKZOmFG72bBlQI/kyFWr6z//8H7R5NSa'
        b'IR9+9uWq3vclpQH/1poGdnuu5fPZiYotvzm78cIDXazj5b9Xjz7n/+8BI74bfuI9dU/dKvPgUb9+/duWngvOvzL1u8GXWyQ/2IynJN+GXSyaMHHWnUMwb33mAn3SK4sP'
        b'/vxR2Nd3YqY1lf79kv2XtpXXLtZuWn519tifwat/iOWD31BIaCAQdJSMI/vywgZY496b12Nj3rHwmMAaTqBKtMrlToQNzwOeuBNHwVPC9nLNcNsY11DB89mCmwqtTyUT'
        b'fXv5QrgRXqZuzdR8bLYt9xxUzA2CozjYjA5kObcAxurwZVirQk1ovWsoRSAAnuKmLh9ClWm/WSV4JPdZY1VqFapJVYhBYASXOWwuZRY9e/nC2nSq5QxcqEx27xvWm2y8'
        b'd8iQ6bIJQ//nTOCpWYSLZr1jjMhvBIkwipwho35Klqw4ZUNZYYMGwhIsZAMQtSdhC5RHia6dpLv/v9yWRxA8AU7SieB/HNVxwxa0bTK87qJ42LQIk1vgKM4AD5V4TTyL'
        b'nP+tMqY9hkfHZHA6NoPXcRkiHZ8hxn8S/CfNARk++L/vZm4zrxPVC/uwkdl9XifWSehCJz+9TCfV+awBOl+dXz2b4Y+fZfTZnz4H4OcA+hxInwPxcxB97kafg3CJ1LOJ'
        b'ywzWdV8jzejmro1x1xai60FrC8bfpORXF1pP9mgjmxH21PWi37p38S1MF06/hTife+sicA09nE99dH3xU6iOpx7Rfm0BqQKPT9OatTl6y58kHT2kxIvnnUZOIzO8Ej0p'
        b'h9FK3HXUZ6orNWsLjMRzWirX6nTEp2fRFxQu0Xu4CL0Lx5lwIuKPd7ogBf+f27VIc8TIZ5r0Wqtebi60Ebep1kYT261ky3Yvb6CVJJHrzcRXqJNnlcqdK3ljnA5ebbbN'
        b'uERrIwUXFZqpv1dPajSbSr2dhPOsgt8YV6W1eLg6qUN4qbaUvl2itxgNRvyWNNKmx43GZeq12bmP8OI6e8FZawztTJtFa7Ya9MTprNPatARIk7HAaBM6FDfTu4FmQ6Gl'
        b'gO6GKF+aa8zO7ei1tpuNuHAMiVGnN9uMhlJnT2HR71XQwz65NluRNT42VltkjMkrLDQbrTE6faxzb/SHg12fDXgws7TZ+Z3TxGTnGNVkK4gijDFLCy26rr1CI4BzDSBd'
        b'Z2UQPcUqQKdH/+Hazo5js9Fm1JqMy/R4LDshotlq05qzO7r2yY/Tee2CVPBf4wdjjhn326SZSe5PnZ3VT4hzEavtZCdReLZ4gXNVCdoAN3S5MMu5rGQsdNB59fL0fLpr'
        b'8Dq016WWRCYqY2LQ+thkBoyC28TLpajeucE32uGfSzZSTleRFQ/16QwIxqJvFdzN4ctVVGv83a5okVWNU352ohsJp7v15T18VYZ+pUl0LlaIeSFSm6xlz4Wd2z5u+66w'
        b'cwt2hsXvGLf97IJx21dlmRS3b6S+2KOP8u8PFLJXZLvDgOm5oG96+WJrgWoAu9DOlZ4CGdavQLvbRbcSXaKSOxzVwYMknUsmw43jnGI5bQiV3CQMBN30ww1WpNlzxjn1'
        b'iB7QwUs1aJvgwj0KW+CJaNQAL3ZLHMEDDl1jzJMNVMV4sQ9a7ewHP3SCoRuVwVVoO9pEhT48PRpeQbUpKglg0WV0HDYwKVjt2Es/jkOncnCpiSOGjYRNIg5IljFoZzLc'
        b'L+RsGBpHAB+vQ1VpqWKA9UEGXUkY5pKjTzFZRwJhqbQO9ZTWK0GIjC49IEr5sp7eSOtepKj2DP211HqL6q6D9lghWZ5X/TWsy4tX4f79PsQzXO9REHS91IkosGQDCedi'
        b'JxqV65phwkpSnrsH2ruhEF92sM4VT52qc62Jehj2yIkrXAmnK8x+IkC5AkDSTKfZ8hh4drvgeRjiMXXlmgGLeWJVOa6qCCs16qyPqWqfuyolqcqlxnUxT5ZtMmImrbJi'
        b'Xq14ahD8MvUlRUYLlQGPgeKgG4rnCBTteYiY6djl7ZW7WHdPN+t2bh7rEHmw7mdw6bt2FerENCmhX/WDL89BG1ALqsff4AUA169AL9MoooWYqx2BxzFg5XDrKFCeMIlu'
        b'EDYd7ZiIapOowj4cG1vwwAhYyyb3XWr8ux0C63yc5PLfzql++Uv/ijhZ5Z/GqNbH/CLrxMx3c3u8Ofzw0UXDRh349PP0rT9FHgh5o1IxeOrhvyeNO3j28qL7X72V16JY'
        b'tXJL76XbfLj1yl+9FHFc/IeHc6YUGj8T1X0SmhW3QOFroztY7kHbyIbMHqywqZenFYOOwVXUneGzaDrxnSY5IzsOowZ0jYXVygjKb5bDy0Pb4z7gaXSYOPtXClEncAd8'
        b'GR50+UH4+NFqBp5Ba+B5yh/7RgS2e1h4uH0ZcbCwE2mxxT1SKGyEh6Ez2U42prHTjKWpQ1NQQyw5joOH63uOYuB1/LtfYLq1Y/XuReYcvIDOs3BN3CQhzOU4aoKtnrtD'
        b'HkUOzHgL58Krwpqwc4vhWrp/fKLAm7F4gtewLDjOYfF2Vuy1G93T8FJMaXpztqW0yEYZaoQ3Q1XIaOiFL41upPv5dmJqztxeXPWptpV07ubbzlXJTr5NXXDVjx/PVZ0A'
        b'/F9Qiqbkas05eiHKwaXGuAi8g4qENZ2n1Y7M+qVPoxS5NpfpOBmM1RYSfllQilF506wOmgvVWtAheMLYb9QRnoaFzPvFBf+3ooPJBNuvdwz8d8R8jh+TesPMX8hJ/M3O'
        b'SWD+4LOZF3Jn2j6Z9WZz7it/OhGUMfrnL96anCKKreoT5vdCxMwzpz6+MeV8/3/4JH+5vVV7dUWGpHv6B0jhI5DTBXSWKhRYmyBrQgSNYgE8S3UWdBpez4G16WQ1KTym'
        b'jGQKpoMAVM/pYTPaTXWW9CR1DKbfDvhNcfsArKTk4zu5BNbGYo2PGYauAz6WgedgFXyZsoxseBo6yOZN5OwIWB+bGINa3HpeHNovHgtb4in1lsJKrAg2kAXKVIWh6ksL'
        b'OiqEos1QkH6E1WgnhcCp+rQ+R79G+aNdpIXosD/Wb5zKDVqNVR+66eVOzGP3E87Qd4ynfoPWD3522gzMphiX6UKPjsHH5Dfel24NE8Is69uBMjpk/l8oPuSQlzNdkOh7'
        b'XiT6BEAUXJs4t9BqM+rafDBB2MxE0LeJBYHf9eoeSsa8e2WPyL2yR/TIlT2uaCUS+tmJqibpdMSuIaTnoSsIdqBbVj+SfgXgBepNxPdJU11cIEtrzu9Mw26yd7ZVyDlT'
        b'eMSZI1PsZmxFqpKmdhHC4xEO5MpJbGaSzSv8R9EVvBa9zW4xW+PlmrkWu15DoniEvQd0SrlmutZkFd5pTfilrhQrL0SDMtuewIZ8OrEhTm2Uit7mrCSw+l/v2+5rfpV1'
        b'V/NAc/HHexqj4ZT+ruYufmMyPPiyRX9CezvrmPZuttQg1UmzqjSJzNkxC0Ek5zdmdS8FR02PfNiSP1HkySgENmGPEgyIc3bOyQIAJuF1lAfMhGspC5CimhEpqUmwOj0N'
        b'1aTGwIZYGqmJDqEmBawTwZPwFDz+7JQYoNXpMvVZxmwrVUwpIQZ5E2IKIcNlfTrgvnc+Jw2KBZLaQS47yWWXNzV6gsd7JMtzp6XUuAdfbnRBja95UePjIfqf09uMruht'
        b'NnVOYZIzCzhG4tA8CM/DLfX/P9Ij2ZLmpMsFh5JN8D9Rw8BgNGtNcp3epO8cPPd0RPf11bssJbqhQUNcRHdvxoxnILotakx0RDib0Jo4J8mhE+ioB9mhixIqeYOxkKt0'
        b'ER4/IZiQ3QSsKUcRmryERXRldDLZeCA2BdZ7UB96Ge7BFDgRNkiC4dWCZ6e9boJr8wnkl0HJr4MeFtMp6/+WAvfhy+0uKPCiFwU+EajHnJvDOIDHuTmP3hedo4Yr/zCr'
        b'C9qjiEiJxGwvyML0hnHPw0/c7n3NtlssmP2bSj2M6f8GLTfu+RhYya6or9b/nRzNk2topuh4uxM6NtxvR8jh4GOZz5Lv45wIGY8OkJOYvIUA2jgfI2R1JEVItE0PVwsI'
        b'iXavYARlMCLZRuZw5tlziQWGzUZy6ME6uMpDHESJMTZekchRK7zc4SCkLvEvu9ButnkMl7Ur/MuSdoV/nbKqXaGHeY9GOMZD4yKzl3/oAsOOBjwOwzpV+z/CsDUYw8yP'
        b'xLD2sOKnxi55ZBRRwoxm+ZJRMSOiumDCT8a2y1oRT7HtQvdJj8e2Qf082d/HkT4bE+wY24jRO2VYZEdcg2fhFmybHOkmhAy2dIf7MmCNmwESZEOXAN3KHtahaynC0Xwe'
        b'mkfsRAHZxkCHGJ7rG/YUuBZEevBJqJYnbHDVYcw75nxWTDuEL591gWn7vDDtSbUqenZcgyzJzNQVZmdmtvGZdoupzZ9cM12zHW1+7rUiRp2lnmQiZz9ZNpILOc6G+lrb'
        b'pEWWwiK9xVbaJnU5L+mcZ5vE6SZs8213vFFHAjVVqIZEmTSlI9rE/3qfBA+/nwNf7Kwzzlvqx7MkftP9y0YEsDQ8pNOVDfaL8I8IjAgMkAoL/hzoKLrZHvyALqRhyxWb'
        b'vSyIRBvhPrhKtLLXSK95EULHCcC5gt17GlZYLtzW3bkAwzlQdOfoh/JpJWS3S+KWzCarKyxmooJ5qFxqLOa8B85y2N3oDm7PE/hyn3UvDucZeoKtBd3o0b42HJ1xNYpE'
        b'MJxGu+nsQ7KvBK73RRvsU3CGYLh6zGPCjOFGRYdI445hxrE+XmzN7R0h/eOMvgfeB5G2b737hDh8rz23SOGdo6UD1TToZEqcL4gEzUYxkJs+yJq9hEZrno6SgAhQpGNI'
        b'tGav4hglMJFdYheVPi/6qteVnJ+n9VZcyZ+Zeaxfc/7VBasjd6pfHzPixXrlnvST45riF/d5P+pg1n+UD9NW+n/R27/8+rwzkWumjEz+Ul066U99xeG+ptvDLg9dO+KN'
        b'8iVpYwatjOw+LnJeycSLfGZwU9HpflmZfzCelwyYd1ijH5Ocf9vn66Tno/175i6wiCoGfDF1ie8965KiyJ4fTjvmF+Z/deXPWPGPK5vFU5cvqhs6xcPlO98sJR5fWFNK'
        b'G/r2CBKH8+4kGdCkvthXJ4TcbFCTY3ZKJpMjtIsxnxRCQfuHAiU4E8fJNeMHcz2EdZ590tF1VJumilGnps9zbQqG1qdI0AbYUoqqp6E6uB1uEQ0CcM1gH3QAboqlhR1f'
        b'JgJScFklS9DIPjNrhBou9yeRPo1TAuUa097BScJust0/TcdDdrCAHDxRdlHB0ZQpwWR4iob54uHplZYwnQ6Pfi4ZnuZxATSY9pJqnzA8E23j/xfDM3XZ/3R4ZlriOeMD'
        b'2VGGnjfz5ev6QfXjAlCcbIrilz+M+bpv7xupf303OjfyI9Xd3NjfHvwkftjZqpLDCW/dQIOz/zAi4sPLRV9NPvjePtWoW3Pl/+CS95hGvZA3MOX1IX3fiX3z2D+tXyYP'
        b'G6j/p+aAqOn4a7+7N6Ksqc/r465ve/1S/rBv1869szR65pLCsBf1mVeMRa/f6fnej/ycsEH6GxMUPHWFWeGZ0e3O6kGolnjKCpVwFZ3KTEdr4XWvU8YpD1gITwrBTLBB'
        b'QRW9F43oeDRqEquSSTgTxgkR8ENXyQHGF7B1IZzcGEt8bjVRxBsnhvvRVriKHYsOo4rOEe7/7c7Fnuv9LVatl1d8gLf8LeNpNGAQXYoYxMhZsjAxiLGccosXro0nQQYe'
        b'Uve/3lCZsZx2M15SwbddiOg6uWdQD101egi+DLdHR6lhXbtSAx1wJ+gN9/DweP6UrjVCj20nPVine9vJZ2KbXkdIuNmmv8A2D+RjuizJx98xXXIPp1K6nFcsxnRZMUtG'
        b'6fLvvt8LdGlS/k/oMuKjBZMzPptwbfDu2RPnVvfZHHW938LJsUmzS34f2Fr49Yg2bkPU7KJhEU0jv5j6rW7vvHV+I5RXBvxV+ii63D//ViBtyrGFHOA150RkHXpl6UCB'
        b'Qy0LDAYDR9wX45cRD9h4YJEA5zKF1ELM0DT1IpCgUb7fZ57wstZO1ssfE5H18nlFRiBEZlVkB7v4MToGV9NpOMyRIwY4mVu3CX4gcvxuMenE7cMvTaKdeDufMLczPTja'
        b'iUNELUInPj/u/7NOzPo04lGd+ME4eaCxfNfvRVaiiBpE11VvUebGzXzr9js3Vv36wui3eowYtOuo7M3PQzWFi5v+NmBy2T/fEE0yfdv0+rj072fe+az7uPu/PNoj+eOe'
        b'Q20xVddCRkwfbd81LfDHw3e/Prtg52c/QfGs381+/t/xr/rv/Xn5qVt/7Td2Z5+Ss79RMNSCNKCG2Sn0pHfUDG+SCbfFrL57mpeO/GzRzB3ZiE7fzkYGerORlSCQF9Y0'
        b'UwZCWImMMhbLmXZGIlB/Ox955v3U2rkHKVXKubZrrPD4fei5TRmdTsL8Yw+sEPhHUprAPtAGK+it4eEBrd1rWSRZh0J3OM3FLKVKJBwXQM6yIUyjki1n6T2n4/E918iU'
        b'RNoYkmYqaGQWhy9iy/lycqyAqArYWHLaBdbyA8pEeZxOhMsRzQfmvmRD/3xfS5FwpBT9Rg77Eb1IN/A33y4jRxkl0DJI/qtlnKURp6K+ypJT+E5MT+UgdYnLJVVMmYQc'
        b'P6CT1OMcZeLxoHgnrmUdzS+qJMcGcZZ3yQkYpI4SM4ZWRA88IPmlnfJLcf42nH86zS8c5JTgzh3pzh3xqNyNDDn8oEos5MDvsHzBZSrnO49ecB7VlFUGdD5hhOkKU/++'
        b'aixj9Pqi6RayynDuQ5HdZlCNcZ84hFG4lQw6+Wgh+5VYiI6ukFi0BDV99GZ7gd5CzuRIIM9istG+Tt8mm2c2khtqNAh5xwtY174BZ3ux9OADupRsJrmQHeLamLxn3ZlL'
        b'Rs7AsQ4TVieHE/yMp2JJSqNuyUkuwnkwwfSYDp6ukOvlcSdz/pfS7UalDA0tR62wAZ1LwXibmZOkGhVFNkagSxnkfXnUmoYuekWBuOMmiFwtA1apjpkDyPFetP/ZStYZ'
        b'bEH70DLCTZ1MG2N9hCHvT1uVaSvMNBWac8Zxzs30AEdMRLobUxJabyEAJs0YqoINsaha2P+RqMRgMFwrKu0Pj3Y6M8rtncfYwOQzFhkx+3RcGTlCi9HxeYAcz4RhFoWS'
        b's1uYnoCIbPKGugfFzhYQWfSQHVRC1859xQpNES0zGE0mBdvGmNuY3Ec1i7SGtIo2bzJplq9ztHh67g49aTYBrisg3hDcloGLyRnnuG3ppKkqMRjcV1QKrwx/zLpppst1'
        b'048/ErLTumkx6Ly6tX2p4DJtEbgDwJiZy0oNn2uszlWBMa/hQQfyMzOLfF4fnCK8ZP0ldE0BiMxOzShZAIzSL7/jrOQEinfivrmveZvujXWy6L7mnqbAYNNWXTimb9be'
        b'1dwyxL73Ff56QkuCAu/pVCHHtLey8gyRoaurlpyxxf0+bsTwI3FJIKmqpqgx8rlbu0MMQ/fnhlp9U4Znx3E5fmDRgbCx/5Hcr8SaNt3eY9tEeDpalRYprLcmi61h7XBh'
        b'55O9aFVydLLKdS4iOgU30LMRh0OHEMJ/HR2cS/dOqU5F65UM8MtC9fA4SxKindS51YPXw+PJc6fRMMlqrGOvYAegvejks6/Y7lZQqBs7WjhoJFNnzDHaOu4Q7Nw3S8oI'
        b'BzBJmQjG8oqbpP4frckmxaR0KeEuea3LJruTw8v5sLocnsBNrk+HrSPoJsvk1CfYkO7qqDHwqHgFavU4upQBHscZE7ecwCOIrKsUjpBh1W0irTXbaMSQXQBuEdz5VGBJ'
        b'rr7EZDSUzuOch6ABjm7ktkgFa2gEBN0KaSbW44/zeFTXsujqULS/a75F8pFjdaj8CyFxbASecid0TrgsUIBjogdUj9n1zMdudkKY0c69iHoirN05hirRumhU3w4qgbP7'
        b'1MVzObRnHtz21F1m8ADtsR3mkzVqhHBumtajy6i2UgP3wzUpw4YnuY3RQHgeNffnxqFT6Mj/xT7DIAqi1NChz0hsiB9sgKsIlFTjJKtoBmFq5YYmexxizwOPwwGJINQx'
        b'mLFjJapkQBmwRNkI4+cqWaxMgHJOOC6sjMVsni32JUd0FY0qY8jBXbRfReq2gXFDhw0fMXLU6DFjJ02eMnXa9BmJSckpqWnq9JmzZs+ZO++F+QtezBDEAJFJgpLAYH3A'
        b'uAQTsoJvEwtTRm2i7FytxdomJvt+DB8liH6fjo0fPkoYnwLOdWwJFXdiulcP3edmBjqATqcMG9XuNQhEG0N6cvHoJDrX9TjJnCijc51WhUfllptfMJa3HoEsw0cJI7HU'
        b'A1lojN0GuMWfgOAeBdS6Eh3m4krgJuoG06PqzGh1Gt2nTRdCzv+BV1l0xtbtMZMorNckyjPs6dj1uSYiEtZF9yJYFZEruE9UdJvUQLgbOuZzC2HFKLp0/jnYQnY9xM1b'
        b'gi4uBAtHoBZj+pY1nJWcX7Zpkea+5hadDyEHjDzQpAbGaB/oU7XBOcIhO3MOi84d3aRgqTMHNQwQRauSStFxsodirAT4DGfhAbRWZ3MeedBkI9t9NaCT3dPpHllpmEN2'
        b'j+XQFtTIugTFI7QGo7Uw02Ys0Ftt2oKijhuwun45qdjyjntguTYpzeF9MIf35MW7rhpovrIuOf+6gI6+kRGoCa2jTYHrX8yMdfZuEqrDYmGwRbRy7sTpXsGE3n5lzhlM'
        b'6OFVdjBuv/IzhezSfVI7jX03Nd2OgFuEgVwnSsFiuwHV8UAczvpiUA8KW9/NIx5WIP8pShPxb7WvsIEBPAHX9ho+DLYOiwMDJiiBRM3AXQGojiISbBgDq/HHi8PgBX4A'
        b'rIPrgARuY+DFMS8KJ2U3hWehTaLx8AYAMSBmEjxHKzKkhoE4AHIlJs34t4pzBZ3oxKRIgDX+oJB8DftAshLQzQGH9LPAcywWlriAcWDcpHk06bUUH7I7T+J1vUbGxk8W'
        b'8rf0pYs3ex2boZH5YxsH4zrdA+3GSnNKEjzBjleKAR/BwLPwWAbN0DM1AY8kkH9v0QR/nS4WSjk6bQLmCiBhX7zGci+lt/Dy135UXdP8oNTIiicUAeOXn5sY6wf4S9/v'
        b'Bk5rbE3mJ8nW/awzLF3yWZ6+eMj8hQ/5l9fWr9bP/HCt6oXe/d8fE/G572szloS+s6kx6Pt//DmwuPTrkKV/e/21WSUfXqmbGWULCvxlfe3k0ncWRuj6HpsePiL0VN43'
        b'v/rs5oSzo9b69nzrb79ravzm1V/Wzjnyw/9p70vgoyqvR+82+2SyELIBISzB7ICyrwKCQCCorII6JrkTyDYT7kwgxIkLIDNDWKyALK5AEURBVldQe6+t2lVrre1U2+q/'
        b'1mIXrVqXUPWdc757Z4Gg2Nf3f33v9yc/5t7v3u9++znfOec7S3T0lmrnJQdfC3z3KffBtLdOHx/zj/nvR9o6N53YEnxVmbpIu6qja1ubc6f/xVdeWnTTtoxTC8af/W7K'
        b'DwaNHLNo9viJf3zopjyl8ZBpW8pjL760Z1/xglBlZevZ75d/eWriB7fufP/ol/tu+ZKvTL387OO3FZuZ5uUD2lZ1j4HTWoeSJAM4ii1MgPpgen2MRFym7dajZ49V72Rn'
        b'mzszZ2un7aVJYbq1tSup5Px+6uGYenXJtZyVlKtN2kkS3g4bpG3XbUzKtdOJRibz1QPkBFo7PWVWpXawlezQhQZ+Yq568uLj4/075LkpLbB1edyAhEaNGDKU0M+489FP'
        b'isQzua7Eu0QnUKVOQBoS358XyNI7g0KFOnULceWVGKJinlei9jqfUutxU5zLOL76V/yxC8rPOS7RRwvWtU40tLNvTfr7Z5Lol/Tm71FPqveUTi8rmartJLNfxHSPD7ls'
        b'iMQN5CV1m3ZK3U8gqz2qfmd5ubYJaY1+XL+rm2oNI08zl8BBoTf4MI+hTSPAhmE4yjCym6agpJQFTfBfgu3ZlMNlQq5syBOESSZta31DDIuyaHy3RmTRqyGXqNSEpQZ4'
        b'DkhSgJIZiypVJfG8sUYgtUYhiDMZRxuEwrIp6qUegDghKJAegJiIlO53JIo+/LBBGJi59oKaJh8wLExHq7uIyYwyEqOm1pYWj6JMwimXiGE2R6WApy0AFAcW4a9v90Rt'
        b'fg+qjgUw+O/KejmwTPkF5hdlz/khkaGBv8T712LL1ZnYlr2isVmSQARXIqxJAV0n0mzDXrZNqcQw7nnq43MY92Jszn21+yTtxAqtM4m6jInkcV6RuiQimAMiOIcEdSyE'
        b'KMwhDDLGyhRxkEmMJyg1MLeCLEEOMShiLPYGCkOFc0glLIanFAkd30NucS4nm2jbM1d1FY27bmJbc1NF6USiEuu9S8cv6X/J9UVLboDf0mK8ryiZeN3ECUR0n8HGkuRK'
        b'F20BJ4hUeNTs91QrtcuipqWKr7UlakLBEVyafCthXoiBkKIi1BO1tKC6neKNmmAc4QOrUe3XUfBp6L4SvnYbmY+KxnmLKBlOIChYLEMVEt9aAu8aVl5GbiHVR9GBjxqZ'
        b'w+hb4MQpDlOlhYP2q9vVh6wx0iLpVPkAzQXQ7kImh9Q8Y0KUtciWODl/EV4bgJx0csqlQUEGij/IudFgSYC30/Cqv50VFOCN0JYXRJFnRgexOFCumA3zw3PLr1lofBVM'
        b'+GoP+8qbH+Thnr2/5/z3+hmPVBXl7V1CQQFND4wmrd3fE0gEquub8PjL0+RphknxrPA0fQ0cRp0tiieA5rM45t+LD7WTBON28rNhJx9vViGHkW/a9mXao6VFM+sxoBVy'
        b'nUDM0KjzXD91j6nosgnd261jcPS4wgQgJm6x6JEoKCeHgTe3ig3mBstiKzzDYJz4zOKxNNhki5HCYJ2A1NBq3brYLvfXqX6H7FxrW+yQB+jpFNkFaace20IKWetMcqqc'
        b'Bt+kJD1LlzPgmSv2RJJ7yJnwJDUpV085C56lkbU6tzhdHhgS63iyR7ctzpALKZUv94VUD3kQfGOGFhTI/SCdSZE0ehL4XRJ1TIUZ8XgDk4GBi63BpFD0iGLjYnsKJY1i'
        b'e7w35XI6FEf5DgaU/JgzX8E/5QOOSPHJXDw2XmVsjhPgyk1wSsHs/S3VtZ5fxtgyob13Qtsqzs14niCBGotbLAJFEMGCN6z2BOXvhGgD1Uu7N9mL2lqaquu9bsgQTWhA'
        b'z8QGxHJ0bymYodfscxlAaZhsClGTG7cCAoULmAwiqLwV50jb0xJrxo+T5ibWXSfNDcJ8LBweVPDx1w86VfbHeDeTuJqYgXVLbNoR8bctIrk3rwd5no6nNyyocxCWQqOg'
        b'jJBR7CCM45bnwBNbo7mlSjYHRbwC8udlyxrenyNb2VdZnJF3IZSP8c31ubJXdfGDo3xJl1AxmDkPRjhV3scp4m/qMt1U0lGIovXYK9x6/S1N9YGoHZhIJeBfWQ/bKm7D'
        b'hkULucmfTQW0XIgPdQO6gZ3ZQx743xMN1TpCMVaKJpQnZPLtuUnrMfGbqpjfUZE7R5ZEq5HGMMBODgSK585OD2jCROULbIXJ3wokBFIPXtlQz8PGR+2xNX+BUwXlK/j5'
        b'RNS5RWx28vrBEv/FBi6LN1D5EhtjwcKqgb5JaKGCUHCBpvHwqiupaT3ObRqUlrS6Y0sQRShhWFZhCamQMK10XJAbBWorb7QVw9VTzPRlxQKa6Jq8/ubqFmgh7Gx6s80s'
        b'xIIOFVGLh7Xh4uzKRSjmS1G3BubI93Qa356R2A9WfNIgx7oxhHVDiHVDiHVDSOwGDjl0RNBljADI2P7kbtSjy6iAMfgoCFQk/mLt402QU5KS+pFxTj9Y+edtBDElkDC0'
        b'MwyEuVJi4AalAMkTFmm+AydIP1cKCPpiEoOGQFcE6L6cEQeSchZbVB1bVw63G0is+oCn2e02cNc07pv9ZyoWNCyRjAMnIr+QCGvPTgLWeOHdz9ENiUut4uv6xmbJWxKb'
        b'0Wn6jAqySDMq6jMqGXl1CQ866OV12tWYWxMbhkX4E59lGAt/bCzE+FgQMr+4qbZCYemSviEao+IS7OQCIXlkYlV9TaxVA7jmGdLV7vZQq9td4/M1ud29pPgWmplcGcug'
        b'k+7zYnOB84AVoUiK2Nkw7eF1SPrySNjeA/vMdmETrysTTYNheYeLEYqrABnXewPRVKTQZU9tU7Vhnx+1BnzsCNnYD/AzBZ0V0bH1+RJis+LBEEp9pRjOcp4DIyzDtPMa'
        b'TwupINZ4mRaLLGyUiCvimaoDdcBUFZVqhw7zoskji8IUtXnaapta/fUrPNEU3MPcwF5ijf6PyMU0dMzrH9+/P53RAnyk8IjFYAdqgm3B6Fo69ioDf97urmtKKrwaIBkH'
        b'ECSySN4osE0x2MePY4xIFH7qgQFpa0DcRXoTN7Bu0dYhwZoHpn0Nnovzudx1Qoepwxw0BYVGsyITfACpCKy+4J/H7pfyeB2nvwEcYUYkvtwVNLPny10LubYyqEtCfQ2o'
        b'LR/KtHRY4Yk5CLREhyVoxcENWrI5yB0k9sXSYQvalGeCvP9IEPU9bJBDHMd5paAN6RVgWH4aFPBXhp5Afiihnjdgk07AEUC7TAOQ4Cq2RZ0AF8BS1jfJMOVRS8Dnlutr'
        b'A6T6QHsC7CoBWFs1URtmRCDyE6HJGJ+POBL00H5jr/V5/cyIMsrLeGoChUb5WuVDfCvUysxLV6Xx8QU202yotEgy3JGhRIp4IeZtME1w8pkU+NCshz5kwRSSN1y9E0Qo'
        b'ImFshyLnFQvTphXz04qzztX1pt4cMHqj/DXWuY85xnIjJ82oA6RBaLenoaG9hnAzoSLFhj8uXl+E1JGEmGMXL/ZLDEaGrXlV1GHOKlolp8kqOE0uyeVMk9KkTHOmOcOS'
        b'abdK8MTEAjQ/O1y7x48BWjfO1jaWLp9ZVmXSNmvHuNzLpWmj58wrZvHMqoeVa7fPTLBa0yjcJ35SbOYulc3z1KfUtcXs6Ep9pgXDnrAitf3qrlKec9wsaA9ru7XD57nh'
        b'IIUoVwxHBPlNfNyzi6O5utFjUCZCXLemm0NifUqvjGPaVmattyahg8Il0Ba7ep+gdaqdCY3h9MbgPz9GxI7xv2kUbxHNBoDbBb5SAs6VZ77ZFpuY3WedqHO6ZvTQBnks'
        b'slNOgatVdsmpa9HDG6Pl06POK1qbm1fpTT2fRKbtBVU7GAcDmy6fwGPycR6TyRjgVyR5gyQbXKfyN07fUIlFIKaTcZ4mgixiP9nSfY2GzY0UuzdGPxH0mdmzc5kkNDCZ'
        b'EyeWzHw+/G/vmdilb+u6RxnAX3DztAGBwhoyPzanfHtWUnWxLN3TZ/qJKFEfSbHRdXLqym6XEiO8EJG53YsSqs45p6exTN1XPoHmUeaBFXSiKhoRioDwlYHhOEMuYMA+'
        b'IJQEIK0uxVlMaG5ckcrMqF6aQBwxopGSaMILC+oI5SyJEz5WnsWKQZlcd126KMqHTvzLjHouMIEWt7vJ43W75YQxzDynQsrQveACuxHglnJrEvCBhNvKhYktfAudSKjv'
        b'vNVJOb6hd6hoMe1reka4u+FramE0HTbZfu7+gUCkFOIcDortB5cQERzbFGzfMKH9IdMsY0Ktot1sFZ1img3wvUiS7lztoNlfrG1MVXdrG9VDgRh257l89UlJ266e0u7r'
        b'HvWheqKB+raKDWKDtNjkYaplKNiTPFKDBbEQS4V4QIWIFq2LrUwUB6iQoUYbidTshPas0Yw5NQ2e2gC5JtRH6VuLjGiD/SaBUSA2KWJ79vmVXrzcaOnFy41WxXeci8JC'
        b'yy4KC9Hy6EhYY/nddOdCOCh2EI8xkFelBTidAdMZUQlY0Ua7MoSpCRM2EoN0QoENhLcmeCvrSsR8g5kYv8VITsaZPywn3qkEq4YEls5KzBut8ah9BrAIbUxd9kMDBqKu'
        b'SUQutgZ0RdoYC/xtkNutUkw8JQCt56L/KKi68JjpnKTjXOgs4RPJOUbn9U0G1ouMC4sleQ0m3CoxMswpUnToa4dre7Xjc7T1M2dXoAZdp/aUeues2csTAHWyut8yoFW7'
        b'u3swzUsAU6JH6PgQaBSR0e7RXkbHDaQ0BZ2ozvL5GltbYmeXJi5B34wgT9+twjCX+nwCmpdiOMnESHcpsKrFo2zGW1tMEHeBvdTcRHVuivOOwGH1/5rWVbAPurGyHBJr'
        b'x3mwUg6vOg1YASyIUiD1Ke10esIoqw/HEeFybdOMsgrtMVS8zcUQZRXlGFlsuV3bVa4dTzp4ikExlglbOEcSjt4EUDzxTKi3RHr8SlkYuT8OddsROOjeZMB81xdTyKEM'
        b'Wn/XtvoDvub6do9c0AR8bAEduysFRZ6A4vGg+1lffN0WX9j1LWUfg046yCkPmo/XL/X6FKgjLiAtqPbKBcg/o0+RalmuZ8G9Ckp0vqeouKSAcdzJJuUJTUiuorqpybfS'
        b'Tz6AlGoMzIVecL3lhkucAp1c9ycXBwBNh5LiotmzAHKQHY86EuogKcS3jUV3Kcz7dslQobMy72t04kt6Wqu1Pf2BzD+inRw/AnCZdpTTjqk7tGdICUjbYld3q53qZnzP'
        b'c6J2T9DLX70ko/t47DckQJwcP50y15noXMy2WCR9JzNsgHgmZoXNUaJTMFG2yFbkFWSbbAdewJxwFmZdbKFt0kqg5oo6dXCYDUyPUjUtyeNMTC6HxsYyVw/rS+bvETuk'
        b'mIxuIDAEfD0qQXJLeTqNQBZCUDbE5HITgoL+BgjOXA7YCAmlAUHR78U7SgOjIXMohYB+MCmf0NY7KFyB+gQm+NJk5CKZRGAhF5fX1sGbTTxvoA4ziskHI9CSHK8Af4hk'
        b'jD9jp6JRu5vE025YWWzHQCLJ8DxCGZFCiDpaFE9dfZsbNSuJFYwKXv/F+0E9LBkGioKAqioCLhf0Ty6Rn/I0ipjoJPFB7JiLZiLO1BiIwcIlyLeO4YTgvggLYamEp/8o'
        b'DuKBcu0Q2+4M4uHQeiYOwpN//ygSEUkk3Mlv8waEoIT6AewoVbZsxKFeYIiLGiTZCntvkL7BJURTAmjIvAammsqogud2wNpbMQ97oz8nZISGO2sE9mQh1LiQCzIPKI6q'
        b'qGkuHhBFxaleOSpVYYx204LqplbPeeqlCQeJKMySpUazrjfLZnQ0ztFYduQRuzdwdTcasOQP9Gc4H1hLe3nyaNf6vIBWAoSd/IkqJsxNKxRJot8YnWGIp0wo/iOEpMui'
        b'/BTukEmnzjL0QhuY6Pcsj5p8iuxRULjpb20KEGfRHJc5fZ3mgyu5hZqkC1w43qlzV3ZYW4KA+ryZcN8bLdbsOXx7r6/pZ9KRY0zIOJNDZR4AwQm0jkZ0iEBzkY4QGYBV'
        b'4FojIbyoz7qdDh8BjaL+CT7FZwvZEcoyEhMLKCqOmmHAPDDtVnddEyp/eGnIDLHpRBzaSfgzmf96+msqvH87zlxK+hEKORY+B4j0is7bXWlxhbnEI3VU5A7y0I0cPMQi'
        b'MYigK3PDO3a2AG8DdCfC3fQA4KSggLY8q3lSxwDstYYnwhYABsBDRgmnN814gnnwvFU2sTt4AkOaxRnWP3S+KrjdbIFlzfc2en0rvfFttaB/ob9/l/mmQj8ev5qVTBys'
        b'LvzIzJCZMpzggDPoWTFO6ysj+fMgIpri9qIaEzoShwL+jEOalbCm0vQDiyzeLKTx7XnJQ5v4aRKSwsVEAjaZSzzWpCUj6PSLwO7qgdtoG8SUlXQbPkRB+A2ztzMHJcL5'
        b'ZYDzJf0kC3aEOijpPgExP2F9YJvMykxeXxrKFPwhAKRzHODR0Rc/kN6WBHmT1ZAoKzkItzYmQ4a+JMBj9+LfSsj/eZz8hzESUcibQWN1HhbXqxarqjD0TneM+ZRYw6kL'
        b'lckE/0WG+I0zAcPg+4NxJiCrZ1pf4NNdZPo1Rt2gHUbBZKl6N6NK0dxuA/rgy8+W1KfnafvO8/OO/yg4cIwUSSUe3CBBWNAFgwDBN+cSH8gs6KQHqd+gkJJNXFrUOstX'
        b'2zitvslT9S6r6vcTYySIYW0Rw0ph4s9xOfkzAwJyiKt5nX8W6B0dcmahjFIKAnfpNpGk0kxSSwsa4rmtOqctVXX1wNDHBbLPo4dLQFqyy1Lor0AFP5wsOvY31/sxH0FV'
        b'1FJd40dFg6iVlADleiVqQT14X2sganI3U8wgiqgctbgxB1DSCfoPUQlzKPP57tgJXAoOU2xVOYlOyCBawcy3pxvDdL6wE0coFmJ1A2dogyK4oYFh24pVaWEEOBgdxMwL'
        b'Oe8C3WR3BQ/oiefaxwQRdfGNojJhNX5nVqaTVJCVwzdKynUBC0oLVwPZ1WCV9XKuRf1DKAFNJ5anATcusbGeC6mFhkTDVHUmnbBZra+1SaaBrq6lQA0FOEDv7tqJ/x6a'
        b'OK/YBjweDCUNT9TU3AiDq8yj87U5c4lRj5o8igJYZxE+dF7T6sXs+ht/k8fTouO7qAU2GSqq9oJAHJWw9p4mQ22X7FgFchphJ29AEs0AWl63p8TGHr/p3nKqTEd1yiCZ'
        b'1iMyYsaYK4MgJRnjr48L7ogm6gpbGqZ6f6zDJqUZ7nWJUzfsbasXGzLIlCAVRyOe9tRYQ1mO7sVdhm4WkouJ6kpLLywVRydRHsBiZaa4aCgtYUXSy+7tg0oSasMlqQui'
        b'BSaIpsMEGJiY3TSPPLiMo7LAGBplYbxh3VgSud2AbFG+OtgU0z6wEmkNU5eR0Eg9W5ICM/5HX+lk/E/zl2XIAHFwDC3O2FCtZXo4C2mWapt8QPUt5WOCo6jk9rTVdiMi'
        b'BtQCEDsiccLs50I1y4Oyjzk82XR3t1XQyGCNClrzK/X403Qx4tsqyGQx6UyrVXLZXelOFOFayKhRjaj3+9DR1Rxt0wqyMr27coaJS2kQ7cvVp5J2BIt+pc09Jg5CjXIJ'
        b'2M6YSAjVNhdLclqIBRcSQ+aQtc5Mclob7AzpjFGl8EB4bGWDXYJ5usPDq2QWNSMqTbvqimlJ+C52hncFh/J6nTCgk35kBo05w6Ulo7a0hEQapU2yEDCzlL4rGEZfXY6r'
        b'VmFFlxasKPR3pUBCD5UOSUOqWE8Tij5aW6qXeqJOvyfgblF8cmstUPVO/Nq9YOo1c2fMqYo68B258wX85HC79WjibjfTP3djDBuDQIsfMX7NFGLdk+JrPIO0zQHqU7Da'
        b'89nFCwma9bOGrvS50IqC5mov+TtFfziIBFrjq5n5pjiXYsRexdo/PYYPhPYMakbS66pYY5C3sBkoIZw0Z2iMh8ICgzBUbghLJBkmPXXgLUXgR0nhkRQd6L4D+I2gmM2h'
        b'3jQ9hX2+wcw0O6gcXlkdBjJRNq0RNqd1SMDtWoIC27Vk7mruGm6RwZ2YmRHpRwiX9sLCuVOvmlTwEXaVKTK2AfdvJ3o8Kqys0ZdB1Az7fUtrgEYrapJbm1v8JGgijUc6'
        b'7YyaVqImgi69ZHiMxpM+EeqWXbzRtnITHr2YDOVrMso2kzcFpDczaKfK5NsdNP6sYVHbdE/TCk+gvrZaGYVFkKImklO1hnApNXFGEIUEabcHMp2nOTGTKhWyQPwaUYck'
        b'Gl+6B7YHCHMR34T5gAn4P1MmWY6gCw2W7sXSVtncYZMtHXYmJehwtP0TZttB6qsfdDiBwHfmch0pQZvyAyNnMAXmEiUQu2RbR4o3n9J2SD8hO+CtUbsVa1+uJLcm6AwC'
        b'pZnDNXLKb7Fs2ZnN5XItv4eSXEGX7y9yStDVaLmDV8YFXawWuM8POuEXS7boWANKlF1BC5Yoix02aIOLtYG+hPeoMs5qxPeoxCJbgqZgStAOe72tAX8dDU45faMZyrMr'
        b'CuZargBPbKZVl1F1Bo2vzuAszDuD8/1uKOvXP/107j8mTiPpRpc4fvx4mrao6Aacwc/T9boLovzkqGWKr1WpB5TDz0C1Zq9npbuNXVYVpzBVfzup4zbVez1+hoqaq5Wl'
        b'9V5/tAcmqlsDPkJh7hrAUI1RKz6s83mBilV8rV6ZnYm04FqVaj1NTVFp0VU+f1SaNXXavKh0Ld1XTV00rziVrW861peoAIlsbEz+wCqggh3YAPcyT/3SZVA0a40dM7ib'
        b'oDke/R5YV6jCpHigFVFzDZOR2LytzW76gqkNS3gPTz1tAXr8jRG9HUwZlHS+F5t0DoLTI4k66cQmjUxEmJ8D5h7SrrsxIbcmQm/KaaYcDOQkHeRQZYsALqGSJGmK2dih'
        b'FC4ZthB/+fLo/B35mJmyEOHQXCogEp+EO6cV5S5rdEchuWhxwsvmIJ/FlB8lVOLmuYBJF4GaY+ywSIJQKyF4W1fe5GoFLawLLvPVjWbCePL74G9tVj7BtVR6Mdbn5RUF'
        b'AweXFiZRTTGxMCIkMvtydfBhndFPMviCHQWPMAyTrz7dcj6o6xM2dhIz196XBhabftno7oy9zuBxVpdUUugvIVipAh75VU4Xt6EdkUzq51ERehp10cquBx681tfkU3T8'
        b'zQo3eLPXkvfgZCvmH8XaiUF4VpsMsRN6hSIDRBT/69hXL5aI2FuQLEtGvhcg6lbyOpJX9vJ6NQn8/7d2KRWXBDRDSeNNMUlAmsUq5bgyi8icd5h6qMbvaFkucsLMWm0X'
        b'3097RLuTqNuqqipdp0o7oX2nzbC1h8QTMWt79f4GVFQTmXHy4dwU9Yl23U5Re1pbiyWQwW9mEYsOO2TEiYaec/KhedPqI0+pJv9OoOBsb/SZPe/zuT2uTbtvwMAtnWft'
        b'Usa4DxZsKii48fkr+k8f1ntaWfnmN1e8/Pc3rr/u9Tdf+tuCwvlvfiR+dfx3N526pnTb4I+e+bKr/c0ex95Z//4dA169fGHJczvGCStm9MjZXjKkX+EDl9z93HeH3Vq8'
        b'k3/wnZIhAzw3Lsi67c1rLJ+8OPvGR38snJUdvxr8+m3iMb73VvH3d1xndv2opOWKvwlXevrs2OL53egfTzXd90fLqM2vtL3QqYzq2fLDV694ofHa3VO3zPvTouanPf/1'
        b'5PS5Xb+2lf9JGffW04H1VStPPdbnnZ7v/iaw7qfvfbT2D7t3vtXq/Wzorgf9u/qsfq/ss+vb7tvvWN/45O7Zd21OHWLefMPf3s0YrOQ+0/Owcm+vN/5w5c13Vfx8X1XG'
        b'1V1v/X3kp5e3OnaVjPxi1PUPlkZ/2WPx7pS71y+fcvbdtOrVqf/MvH5fY8mAeTsHlB7ZG/jJ26P2Xz0nsj29fu1Hpzq/nDtsyvE+m+sK31yx94kFq/70032jd1kmDt7/'
        b'3E3Heoy6rbLw79FNzcuF5SXB0MjP89//zLb4gT8/8Qp/bM93Xt62YdjH+yO++Xm+3m98+PbRyq+eG2z7Wee4F8Rxaw+XHti7ftRvDoy95edjD/Z9oHDxgj5v/6Bm95K5'
        b'n1dpg9f0WvLW8PyQ0nfb7x7oOe+Jn6942XPNmWXbfjkm61Cf70crnpDe3DBk4fh7vX/7r2v9P9t7oL3X8Zlzd3p3Lskb+VSZ8nHua1m+szMW7//NJbsWbH/GN/zknTsX'
        b'9ji98EBDzccNZ4c8/ObpKb3W/fXVrH5Nt1/yvV/+6XD1lUf7NBz/YfjY7YvfPjFjSfuVby++hT/buvmxje2L/Ns/XvfkvP1n193/i3+uWtb3Kq3lzV1jl54Ye6Lxs0fe'
        b'rt/8yWs3DJgz+c8//KBj+uxXd4d+knr1a+Maxj/wQoP50MAn7vrt+6Pv++qZh3r9M61H2+Q5Jwftq/3KUXnvp3f8I3f8yI8q7x675N2zv3e/XDn3Jw988llqfu2L/3B8'
        b'0b5n8w8m9/poxa/eub3v+2vfT3+l9Mdd28qk69sfq7jv7T+8+tbRPj335Qxs+eT5fa+/EK55+J6pgU/WCV9UjBlz8NDBK3v6zvSpOf3qTbW9Ktc3Hjm1P/VI8I7Fd2Q+'
        b'3mfN+H1/LX6+a/r9N55dO654/qTSj+aa5l7ac6A66zc/f3L+0q/2fjkpcJV2OGuV/aYPe33h/dvAXnXvOL84enDbU7/Z8dsDB9vFB8bt+dmLH1972FS/zTb/+Q3XnPad'
        b'PfDRnC7h+9mv8W+39mrMfiy4bvvL7zS/8cag14+evuWVhUXP/vCaO4Ye/WBwmemfWS9Gj98Z+h03+sRjd6/9qDiFPIRqz96sHqTDys3AGc6aUa6uV7erh9TNFq6ndpuo'
        b'nbAHA/0g3/WjtScx2xw64FY3YYZ0bZP6sHpKVLfw6lYyRR+rPa2gh9kZ6obB08u0CMdl9G5X14nqifHaabJzH+1X95OH4qryEp6zXuLQTgrqXYsC5OFihqXGf15A88so'
        b'prn6uLaZqvCn9j9Hq7QjlXRK1Y1qJzlbsmhPaSfZ6axtelkJyj1Ts9RT6rOiW3vEHrgUslxZYocGkI2oXhLes54xD2Ds5D6oPZw9xi6pz5gC6PFLPayFeyXUPmN2ZZm2'
        b'sXg5jENnY+zcn316S6WdU+9V1wdw99I61ZPaE0maGUvVjd0oZjSrjwfQj3pf9Sn1UX8FhZHa3NqtegGrZuUg7YC2y6Y+pm6+JsBsM/toB7GNDdbuhL/qSYW8WVWrj6j3'
        b'6HuDutWDm8PV2mog9b7NRvQN29TIf2Nh/7/8FPdnpML/Ez+GaKvJVy273eS1AdUruGozeTu4+D+76LK5JCf8ZdrTrFk9MjMFfshVAp+XJfADy83CoMk5uS5TzuWSIPA5'
        b'/IimohVO3mrF1KB0ge8P//MLBD7TDP+teXaBz5AEPsscv7ps7D4Drv17o5A3ywn/U/EuMy2ft/tQO98lpJny+mfyzt5pvN3i5J0ivs93WeHam3cugd/hAl/AO6uUR2Ly'
        b'NiHBlcT/LOhufuI0Pg7ajZxBO+9pO8+j6Z1Dx7CtRr1H3YnbjRrBfcSVK/ZZoJ2qnzTxPcHfC5ZZ6tyfl9/5gvc3l6etW3ntFfMfXvlSg/e97z9474qXLvvD2/4jV6Wt'
        b'PzVqwswJa81f3rskvzA0bmZ+kbZx0o3P+paO0n5tetZeKN784uvP3Hn0uz1frblvaHPdpjNDzs7afu3rX94w5P0TX42vnnr2dxmbtnQVPFT2e9702U1L9m39dNeDj8zc'
        b'sn/8ts/L5j1W8quz0c53Zix7v8j1yebfrXt7o+vVicqVb06U79zxw8LR21797fdWde398A+nrdsW9j9Rf+j12/Z+2LzbbvnzmfePP/zTms/n7mp6b2DrJ0XilxnX96o8'
        b'3nNn7q67O+76dHzdpoZTfzyz+nXhzbt7f7p7w9H+S15YFPnr+puyNWVev+LbIwtGjxmyoPbpoQuW3p3beGTjhuGfP39Xyd+fP/SHCWs+6Tf1J3t7Oo6d2PfD5kmP7Xx6'
        b'ylyt4q87th3J/sdDeffOnZD38r5ZVTekhF6544evhGe+ssP7zle/2fHyLz9Ynbdu+7Bhp/bc/tbwkym+Az965PZXl007/NCh4z97adW4a/98fNSvxz3ap2zVh1uP9lyy'
        b'y7+xpU/z9B2f7nprRPSVVYHKH/1p0+Jg9o+eW3hozRc/am+ft/quB1//4qXRY7435cfDf7xyzOf3D2rPOLXwr++mHv3+/C2/3/tey7i/t34QGZF2x5EbP5r4h+em2vN/'
        b'/mJBZ+8PR01JL9x69aSew3/xyuU9yk+8Mil7/MfLN/Hrcqo32CpaIqXX/Zd57o+HvCBUPnLkB+Ylf2npHPvZE7+beODwe6cfnPO3V2Y/GFy+7bP+l5695RdvvfZyvyHF'
        b'44lSUO8t68uW0mL1MSAVOsv0pXSNODRde4h2QvU7JdpWnWZR92gn4nQL0SywfzLHPA/Dnv9MQpDR0bx6m1M9WpXKItwcKVO3lKqHy8xQ0V2coN3G35ipnQggr6uu09aU'
        b'lVaWl6B/KFjVGIx0Q6XWaREruX5zTRnaNvUZakqFtl05zw27dtcITnfDvvcyom1gF9+k3l0JGYf00TYUY+ZSM5c6UmxUb19EjVXXqfept2mdg6drG6Gp09FD02b1uLpn'
        b'JWvsGvW2uZXapiL0LLmHE7z8BPVZdS29G6WGppSif/c52lPqd0yc+XLBpd41MYCMYrl6pJWosqLyJe08Z24Thrpd5Hpo8eXXVdZqz+LL4hlARFjVZwU1VKodIypCu0fb'
        b'1x8IvjJ0grKGE4L8xJvVh6jISdraherD2np4tXEy0BjH+Xk3LSYSUNYOa1t1p1pquIL51VJPTaXPrnKOIHeGnLZFPckJHfy0aeoRerOAB0qnc04Fn68+BeWt569U77cG'
        b'0Mka+llX74DKwkCMlUzX7oIRQBrrBFSElFXhMNMVI4E4LKCF4ytzAO1ZWW7vrd1fpK1XH8UQsXnqaUndpe4aQBRkjfZsAfT4rlnoa21DKTomq6wycdnLpEu1tbNoNOcP'
        b'hb53Dp7Ja6u1W6E5O/hpUP0dNCpN/vGlWniwBSZzC7w6wC8EvnsLfdYBQ3mf1gnknAhr7hgn3MJfru1LpzV9lfqkdqKS6HCYJmLD74epuk3Q9gFRvpfFttys7vOpnXPm'
        b'lLeXz8DZnG3iMsaK6sOVQ2gFlWvflSkornpgJpRTReW4bhavUMPaSRb7dssi7RjRo+HBZo6fi3H5blV30rsF2v6CWCDeKr5ZW6ceuVqL0KxNX6xtg88eYm4+pBo+b6b6'
        b'TLH2JDmYUh9vu7GyvHjm7Ot7wcKaK2TlaUepvdoe9VAJLmhtwwxcPo5FA9UdgnbAqW5n1Or91bi4kC5W96gbdH1aictQ14jQrJB6jDlY3aNt8lXOKJutHZpRrjfQpa0X'
        b'q1ZptwdQSqVtH5hVSfF8JYn3jlXvL7Gx6X6mn3aEdUk74poN4148A0rXtohAYO9VV+tBUbWwurF0hnpoZnVR8eCZQLGnantF9VZ1H8Av9m/BtZWVpdNnAMTl8YK2U92t'
        b'PSjSqABzo53WOhEBALciXc3Xj1Wf1va2U6PatR0jgLHoP9PE8ZWctmOR1kn1TR46DNY4ri302QmDon1XfSQowIJ6CPgoLFbQ9msPwAqk6KVSGq/uHq7umg/Li7RP99/S'
        b'D4M0bAHmZ/hlPPA7dwpm7Tb1PhoqF6CpTvRwqa4tint4RDecR1ppcXvU+9W9lOFW9ZG4A8bD4lDkUaiBC2/UwujQaMP1PWLO71zqA+IU9bB6iDm0vc9tSnY76pjZnxyk'
        b'wtbeydDvQW2X9gRzTzpPPZnooRT9kwIiDqC1fon6GDoq3lAO67EEegVweydglFk0Ohsqy9WDEjdbfdgCvNej2m3VPIHKRJN63OHRDiGP2YJfV+LiytTuEbUHtc6RNBBe'
        b'7UH1UUJqFdNnV/CcY/4IbY+gPa6e0LYSLm27djK55EWWCoBNO1mL3vOOZ2vHWRfv1/bzpdqmWdpmDvFVcTnMY498UduirQYuDZli7Ultz/LKOQCJ0MvIjLJ+6t0zB5OT'
        b'yDLOpO0cdT1b4xH18ZVqZ8ZoYrI3zikG5gyYVdiIsgolUV2tHaL2rrpmKTpsnjOHNhEL54CtRj0GsDIPFgU2KDAwt3ImrJpZK2A/286huK5zloXL1Y5L1xYX0cQt0O7S'
        b'ItAg7ehIdS2WhXGM0jXY7nYP9DKAfHS6toNGDLYpTirntbvVx2FutqpPUPBOn7Y6H/fMwWxXuw0gj3Y2bG6vgZK6Rn0SYKIngZz25PDKGbNLZs/LtnBmSbAWqduoFUXD'
        b'MYCw3tNyxGOrJ2v7YG1ALfsuwpuwzjz+3+d//uN+YmfExIs9AD+wTAQrf+6fHTgdptyCHvMkHvO42Bv99EPny5jyn2DX7+A7AYNkWcn3U2ZSmU4qD/PgUaST7J6tdDzp'
        b'FMxi2y3c+X+jzTyTfuvuRG3kAaG1xe2OM1XGEcIhPrF/eMPYiE+dCWwEvYupKqRw6CiTKQr4n4ffGvRwA3+RBeEFePASuQSuAlwFuIpwzQovqOPgOj+8oB6v9vACNAOM'
        b'9MX8eBgd4UN8aEGdwIzPOjhUZmgSm6VIarOpg282dwjNlg48EDTL1iZrs61Dontbk73Z0WGie3uTszmlw0z3jiZXc2qHBY8bA2lQek+4psO1B1wz4JoP1x5wRfNkM1z7'
        b'BblwKlxTg3TMEnEEyQYkkgb5MuGaAdeecHXBNQuuhUHSoYxYglKkv2yOZMtiJEd2RnLllEgv2RXpLadG+shpHVY5vcMmZ0TygqLMhXNR1TsyQO4RKZYzIxVyz8gcOSsy'
        b'W86OXCXnRK6UcyMz5LxIidwrUib3jpTKfSJFcn5kmtw3cqlcEBkj94tMkPtHJsoDIqPkgZFhcmFkuDwoMl6+JHK5XBQZIRdHxsklkZFyaWSsXBYZLZdHLpMrIkPlwZFK'
        b'eUhksDw0MlO+NDJXviwyXR4WmSoPj0ySR0TK5ZGRq+VRkWvk0ZGqsH0NFxkoj4lMDmTDXbo8NjJLHheZIo+PzJMnRIbIfOSKoAXeFISFoDVoq8NRygy5QtmhvqHZdZI8'
        b'Ub4c5s8etEecpJwS9xXrCqWGMkNZkDMnlBvKC/UK5cM3/UKXhCpCg0NDQpNCU0PTQtNDM0OVobmheaH5sB76yZNi5VnDrrA1XLxGiNhCLLA9K9dJJaeF0kMZoZ566X2g'
        b'7P6hwtCgUHGoJFQWujR0WWhYaHhoRGhkaFRodGhMaGxoXGh8aEJoYujy0OTQFVDzjNCs0Byos0KeHKvTBHWaqE4z1MdqwvIHhUrhiytDM+oc8pRY7pSQSL77UyBfRqiH'
        b'3pqC0EBoySXQkilQQ1Xoqroe8hXGNx2OsCvooBoG0bcOqCWFxjMHRqg3fD2Avi+C70tD5aGh0N5pVM7VoWvqcuWpsdpFaKtIJUk323EeO5zhwrAzXBJ2Bp3hGWsEUijA'
        b'J2X0pIw9udkZdNCh5jQWJIC8b9B5ePc6Z0jdMVupMNdoU/IC6ASEa+ANTW3di0pXz0J/UXFBPVP/rC6oaa1vCtR7iwWlGhHOgIQd50IOq9x1XpKAoWLZHlPMpQeeFCuP'
        b'GrYnxRJgt6WeQJ2C1g5WT1staceQrTmef/vqok5DO4i0gnh0R9IM6BDu7Ogmu7lF8fj9kBKbfEvRIhn1xpRTUPYZ7PQZ8hCO7TrThj/34A9Zr6Dqs0/2AFIlbxCoMB4V'
        b'W3wtUTuULnvqqtEKwVrnZoeszA9Q3FtEDBFHzXVUTtRR63NXK0spgClGXnU3rvR5m1bFHtnhkZcVFnXCvT9QrTvdtEKqrql6qT9qgTsqzEY3Xn/AT29JzZ1qWFGtxBOo'
        b'TYsp+o5uXPRU8ZN2g9dH5TTBFFbXsA8Uj2cFekPHBCovUMJU2+SpVqJmCsAyNCrW1C8lFXH0TMPCZUTtGOia3TNtnpP6JAeU6loPxsN0uyF7jZtNpAXuUBshKrkVT13U'
        b'5Zbr/dU1TR53bXXtMqYADAtDZq7TkDLtEoqKk6IW4sko8lYUMgTN/AwH9+jaKcwcvmWRp0gX+ZwkR0Yd/PLeC5mfrbhrgfOsQr/JXRMuzn/GlMmIBLAbizbWRtQaMxtt'
        b'/AG8CVsAvTkBrHKxHUEeEI9Qh0YR+TKFviFTCTFcQNpcUlAK2xutyuqws8MUFMKORkGZDvdmbxGlOOWGsNPBdZjCzJhRCNvDGfDGBX13ZuNYmMMWSPdZIwTN4Z7o49R7'
        b'GB3H+LfC0/xwVh26tdmBelxQUw+o6Qjlz4Hve2N53lvhed9wOuX7Szgd0I2lrYDMynI6rJDXEs6EvBJsEqJurfQijKyEjm2oTHOj9Q5eGRI2w5e2tgoqvRfkNBzh2KEU'
        b'/eugDe7seEchg9D6xTaXYyMR5qmcMHydGk5x6AZuQTGcRm9TctBfryOIvjUc+C4oALpNyeaY3RX5G7WxKAIxPTkaWSjzAMyIPZwH9Qs4QkFTJhqc5LDxgPfPUZuzjREJ'
        b'CrqVOVs1zv+t04p+/wEC5m8lg8a1bYb17K8iJO1ihCqRqqjQYxaspOqTgX+iROqVTiKEc4iYNfNZfB4viS7BJaTxvfE70Q7PAG6EGMik63sQgcwvBB1kXDDNxTrIZCaC'
        b'DLwVceLCEuxTQ5KACCeuFL6R6A6Xvyko+f8SxrhZ5jD+Za0hY6sOWMjK6qCFbGesQaiNLRwAmrxxnHdZuFd4QHgQAEJunQmW8YtBGyzfqzrsYVRYs0O5jqA93AuA81ew'
        b'7FIdXC7uyiLcu/A+6CTwg5KCDqAPU/Xl68Ac7F3QPo5bftdCzusNDwynhHvVceEB8H8Q/O8bLqrjw+lYU7gvglgmUJjwPC/Mh9PCaUiZ1VsIzE24iAGc0oNW6FEKLHi4'
        b'BgE0wq4crsMVzgB6AJ+4sjkAmxSiExzwVRlF9GqjEuC+Dnq9ie8wef8CT8zhEigzNZgazqH3gBigvanhAkoV6KmBlBqopwopVain8imVr6fyjHZSqheleumpAZQaoKcG'
        b'UWqQnupNqd56qj+l+uupPpTqo6f6UaqfnuobGzdM5VIqF1N1qbBNlCN1H+Q2IQJFJAB9DV8SToEepwXT7hBaVgcl+rXcIfgP0nrJxvUCZcDY16G7b7032Vwd+ccL98B1'
        b'BqWK5J5BwpEnn2L4vDQokXqllORLIv3/CMgWV/wHoI3/ftQ0EVHT6jhqQm1Dwao7sjaLLhZSTRJ49memyDVoUJwJOTPNRnhrdICdJqGZMfrecgoZoh0Qlou/0F+G4BTT'
        b'AOFhEOw80SkiLx9DZ4YrWkJnzPEkICwJFo9VR2fmMJeAzsSwiXZyoFTCNiDwAY0xve2kZdMtcfJvCCVAw3jIbJjms2EUcSCSOuQwOnQQOyQBPCDJIQAGzmCdYKqa6Ngb'
        b'lcjDaWsEpYzeSEHKCx1MCWMMEYSiVMBIKWELS6E6eti+eRCP5TrCGQhxOFSErUQT4NOwbSTQfuMSFNEBswGO1JWp8T4tbGWK1UFyvo/QeBHD1+O/d7WeMieYTkkCmbJb'
        b'7HxvEe/YOrLH1xEWkGEMuxcpSaD6wqlI5caGXWLD7htEg94TqC7Rz4Yd01mYRgqGPKoDhQhrbia9tW/Oo4FDG3VLDtkDYCppiIFmC1tg2wKaFLaLZUHRv8Ggp3ksXwLq'
        b'ELbPtmlBk/IGhodEZAkbkwk2EZjEDssqe5B0w2Gby5S4ANdoV37KfNWwMJf0TQ6WsXzHQo6YbBcw/D1CmaHsOosefsYarwmoRhNpk/cOp+Az43u2sQHJYAOoora2jQua'
        b'4FoXq8GGQg36dhF8C8/gjS32bawdQIWWxazwxKok85kkn7ixiIrIeECXYZgphgN6b8CIOeg90leGpCcZ4C+N+6kSo0KgRlGRVfwR/60daURd9X63r6bOvVJBJWrFaonZ'
        b'tkikZ21n7Ajw4MiP/0vBOnL/kxD8G2bdYCkBZASmVI7K5RmAys2SRHb8qBaDdojIk5ltLjHHgk8zLC5dTJvBF+cwAQNp+6LZSVT0r/IrR/DZUfw5hj/HySVBLfrO8Ssn'
        b'SJ2/vam+RjlJt83VgWXKY2T9DDeeagyooDxOBir1spJPhQLzHRWra4BtX1btRxvpqEV3/xS1+I2bpU2+GmD5i1P+PUNWvPA/QJ7+Pz//ygEErsktJt1TLScI0rmHDy5T'
        b'Dh0X4NHA+YcT7E/q5s/Z7dN//c+s/4+lzU4xwyKJs4YDBIp1Dfhb4JTEIb3xbtwUhEvBaibuUBCon1Xz0Ck49hpxKtPwT1XQVU40LW7vhxI9t1sH0ebqFoDTgKIEeGZW'
        b'S84B2EHIowSIU9tqPS3oLUnB4zI8FqmtbvV73O5optvtb20hSSCKzdDiBJ463PGE8nqyj4cEG9RxzT65tckzgc5D0NmnJACZKAB11N3hzC1cD/15f4Fc2hrKev8L4zCO'
        b'iA=='
    ))))
