
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
        b'eJzcvXdck0n+APy0FCAUERGxRUUlkACCYi9rBQJBsWMhgSQQwIApCBoURQhVsPeCFTvY+7ozW9y97e12c7t77t3e3vZ+zbvf7TszTxISwLbvvf+88OHhKVO+M/Pt852Z'
        b'P1MeP77obwr6M1egi5bKpLR0Jq1lDjE6Vsfp6Eqmhc4U5FKZQi2r5TZSGpFWoBWi/+KyAIvIIq6kKmmaWkgZJ3GUzqfA11RKU5m+NLVaqhXpfLP8tGJ0lZB7f3IN0Plu'
        b'oBdSWpFWlOm7xHcRtZgyMovQ81zKRy/zedDPd16eTjq7zJJXZJTONBgtupw8abEmp0CTq/OVsV+KEJhfivFFgC4OOiaHdraERX8i53+zHF3slJ7WorZsFJfTNVQlVc6s'
        b'FtroSmouZWMqKZpaS6/FNaNnn1wZq8pxdYkQ/Y1Gfz1xQRzplrmUTKpyUD/jz/MKcfWThwgo8fQUmpqill+W9ab+yuf9YfJJqgtEpKA4DBFjp+ysnnVDRT8Sqo2eULkK'
        b'9IaKU1lxwbAa1oNrcxVwB2yeB2vkC2ANrI+dkzQvKQo2wgYZrIUNbPIcavp8ITwPKilDwomvBOZolPO/R7iv1V+pC/XfqO99Lt8SpUnSfKN+NTskJ09fyFzY0GfMO/tq'
        b'qA2TRfOPjJAxliEoR2gp3OKHio3GhaZZFVGwLpYBrfAiNRBc5OD5MHDeMgDDtAW0rgP1oAk2KVFC0AiaRL5+VEAwOwDcWGPyQUlkrIOJlJkwDvIX/PJB0AS9qWi1zijV'
        b'88M/yRGgMZt1JktWttVQaDEYGdwFeJSoPhI6gDZJXFlReZzeasxxiLKyTFZjVpbDLysrp1CnMVqLs7JkrEdN+CKjTf743g9fcCHhuOAAXPAXQYyQZmghuVqH4ebcHgCP'
        b'K+UxKkUUqE1H7QcNsMXVtZQ8QQBPWkFFIQZD0vMe/aqAGnN/Srnka1tK0WmKoMysfhZm44xvgij1+uwDiQcCnChzfzL5ClcX0O8OQ/BI1X3jpoTxWSauZCiuHwZLLVfk'
        b'L+Jf5ucLKclsuQillBRRUZRVgV4ycD047wda5QieGtg0Ny6DR4HIGEUkrJkJzsVGJafR1NIl4tTRQ2S0dRCucjs8A274oRYpFb6RqiJYB86DVo4KB7c5sAdWS639USpw'
        b'SJeIhzEWtMfjZqNbEeWXzsAtI+E560CUIg/eAaedI60DNa7BJkNdBPbIWGsYru0YrAS1SlibqZClpAko4VwmFBwGFdZ+uJJz8OwqJS5+2xDYkJysYCg/sIuBrfAsQ+qY'
        b'Aq5mJCyC9emwLiUtBtamgtMcFQwqWVgBjsBtqI6+KNUa0D5KmSxPBnusCoKeAioA1rGqCNhoDUXfl8O6TLivL04ioDiOBgfhOdhEmgk3D+k/qpRH6rRk2ChLRuXDrSy4'
        b'Ae2RqMMwlOPhbnASbhytjE9AKZRwUzoqJnAQO34BvI6SYAjmlcGNSlCDUySn8QkC4Dl2RB5Yj1JgukiyLfZLQsNUDOvhZglsUOLGhsB9LDwOTvRHDcHDnQq2FMJ6uQpc'
        b'HAI3JctjhKg7LjLwYlY6AVYmRx1+CT4bDTelok6XyxQpAqrnABZuHQzWWwfjDr2A8LNama5IjkYcoDZZnsLAo7ExSWlCSk4J4O7CLNIiuBVeQSNWDxuiZ85FX2Noyg8e'
        b'ZuBVeLXYKkMJCnoVKsnn5LSx8CDcNDtSiSh+E2xAODZbIaSmcUI0AufBNYJRubPgEZS6Nj11TmRSKtykSk2fj1PJAxaPE8wQgUY3O2M8mewuwq3tNOKPrJ2zC+xCu8gu'
        b'tvvYfe1+dond3x5gD7QH2XvYg+097SH2XvZQe297mL2PPdze197P3t8+wD7QLrUPsg+2D7FH2Ifah9mH2yPtMnuUPdoutyvsMfZYe5x9hD3enmAfaR9lT9SPdvJgqoZD'
        b'PJhGPJgiPJgmPBhx4e4kQ6CTR3jz4CqVFfPFZfFwr1K+Ftg7WIQ3e1gjJOMPdi2YQehJpZApYqeAGkwqwWoWkcBucNvaGyfZujoK1iMUYylmHawCNfQUeB3WEzKKgjfA'
        b'tmiEhk06eRJCYrCRhpVpYJu1D87YBvaB89EyBaxJBrfBRURl4BQTrTHxFFijHYhHJwhckaOB5pJpcBueAtetuD2TBugRbQ6lU/EXHxocmzCLkEw8VYT4yDNwYxIGh0ui'
        b'wUXQPJl8QmR/BmyIjpExFAOuINlzjs4cKORbcA7U5SvBKXmyYhi8JKSEhUwkbEoi38yzU5WwbrUAIn6B6hpCg7PwDDzGg3gN3gSbCcLRqNBN4HoAnQq3zyMZB4JtC5QE'
        b'veQWeISmhIlMb9CwjM9YD6vgmegURE/p4EgeavgUJgDcshJAn/FHVIzLjFTMg6dRxlJmxORe1l4Y0BtrDIiQI1ETjPmgiZ4EKxAjx1+s8DqLWp6C4dgF1sM79MzeckKc'
        b'veJHEJqQYcoVg2fBfriTAXawK42ACY8iXtwM69OQEsLYEFVfpifD+ln8t5pi0AxOwzr8DVwsjKXnwUvgMmlCHqhFvEOuItRVBw5xlDCc8S1YaA1BH0sDUK76JHAW5SsP'
        b'T6dnwq0TybhZiuWIK8ZgKOsQs6VnlfIMExxbNBhxEFxYdEwy6haVgOqdh/r3FBcPTuYTZgXbQscpozHbT8GD6yM0wQ0M2A43gls5jBPnuS5KDFJh7LRbiWFqkNpSziIC'
        b'YggBsYSAmLVsdwTUvRLDqgzi4e2MeRJ6MfnA/a/fW6p+JfsLdU3uF+g/93bDlD0+SQm0QS/1f36x3G/R+gk7qhoaJP2n/EvfPO5KQLVa+LqFeueLgLUpJpmIqCgFYDfY'
        b'wgsk2Jgug43JpaCWl0mhQzkWHgDbLaSPTsNmcAonTEry0FKI4JoNL1qI3L8kh9cIvcrT0LjUklT7dHzCgWAzBzeDyhmkuPFwA9iDk6YjFEW42yRKBDcpX9iMRtoKKy1E'
        b'0B3tK8NJIlaiRKkxCCxcH8sOksMqC8YCDdhtiFYkJWfCs1hIieElBmxcAmssg4lONY4isMBNYNMyF+vnYRkaJUgfneTUgzppOuQt0XMc3AqNuYBxKzprxTT/G0D70qYe'
        b'bk2Kc7Bas8XBmk05JpzQhHmfjPFQnhhTML7v6dagcOZ17oIrvTQowhNOrQxAVAHvwAqElkKKkyPKL/LrXl2O4TGN0TNPqCzndcYzrjs8WzbyAmPGPal4P/1r9dK7bz7X'
        b'/MIHz320rPnFS82be9wL0N9/FekaY7n//HEsUncxG4icmaMct0oeidifkkbUfpopG9ebKLjgzsAVaDBqwS0vHZdgT/pyvhuZ7sfAajEUdmix6yhxEG0KoTq0WLYoO/8h'
        b'3U6berl7HGepwcUE4WIqqAcBXfr82ozx0QpQCfdhQYS4rYkGzw4Xufucdv7NdQFj4w0PWsWD4qzNxxv+AGNRVlG23mrO0VgMRcYGnJnwC4aoyiPgFiPij/VjwGXcM+kp'
        b'0QqVCiumSGlgqWgkluCevGmPgUH/GBh8XADomj2qx8pRCCLqa4gnkmqRjn4C01EwrGTBbV9x99gWj7GNxviGzDPuCTFO74lxNNUdZxN0JHDx0YHu+ggftXPu+h7HSTd2'
        b'rs+3OwyfcOv3rDkFvTjX45nTn32l/kb9hfqrHIlerYnU3Ps86oJa26pDf8FfqM9p8vRndK2avGxJLhLrmdXjqsXVSdUTjoulsbvWJ/hTNy+Ajf6a2jsymuA7NxOeNoPr'
        b'KnA2SYWMCudw9oDNLGhbZ0LDRPCT68x6OuG+ICtHU8gjv4RH/lAGsZ4gxIJWh5vzDHpLls5kKjLFTCgsQinNk2JIBhdX4jSmXLNDWLAK//cgkS62HWPCCpEp3E0smLnu'
        b'8CCWb4I9iSURvYPb8pEKgSRmTWo0UuCIZYus2IuoqbXpKiTvkZKzFdSLpgzNGEuBusk+8Cqwmw3ft7zOmLGu/OGg0QW5ebmFuaoclSZVk3/mb5+26r5Qn9J8gexrX/39'
        b'QprSvSb83a8tLrx+og7z8+gUT57RK0ho6tvBM3hT9hEd4mns4nzbPPriO6++kKJ3KaBN0KkrGMpf3xfc4EDraLihezrq4nZ5SgcH0wWjOdU8w6+fHBKYI9Ab/3NQqcGK'
        b'QZKG29Igkyb23KX9Ti3W308VUbmi6x8I1+14ScYRSdkTmT/EJk1XyRUqnjH3QObkCXCJBZvQv0YLFjGwFanJ24lIRYZyZIoiBmxKR81uik4GZyOJdIYH1lKLssR60JxJ'
        b'FAIz2IVEPpHyXukoUCMOh9s5sAGpkI0ECIkYEn0gVpaSqkpLSYWVPbHgxokjhgj6M+C2JyZ4jLm/1ZiTpzEYddosXWmOJ7EMFNL8r6lfx9g7WJTKY+xp14j3d484Tn3A'
        b'Y8Q/k3iOOO5cJMYOa6OJWZsEGxaDNqQzpqGxR+QupIauFqSDy9HuwXKNem8PbkaMt9/GPTmqO3ktVhXiVrO5YrF2JiXVrUst2Wv+cOny3ETFxxohRQTcOOuKaLiRViQj'
        b'yrxMIcv2MA0uazXED7Ns7c+B2wKfC2Vm36f/G5YUtJf3n9yfh/CMo0rb0scuf1cZzb8cNyuYwr0QF1A0YY7/FMowdsNtzlyG3ry76JRSo9W06lp1Z/K+UBdras626r5C'
        b'VP2V2qiPyjitybzbDC4194h6URxS3yo+qWFObT2pO6f5qe6MJlT0Ffe2ZLB6XNWHdFLvPVUJIT/N/+LduF6Xqb/syljUL6ztJPtKmyPh3fheM9e/a094N06YUHwcKeLD'
        b'Br1efwWxXczChoFtvZS8tyEc1mGVEDQzRT1hZfec47H8hMvTmPMISkl5lBouRvzX9UtUQYQUEnKH1JIBHiymjzeL6b5+mk9GsA5nPu6BdR958RlitzX3wP6HJFU00gkR'
        b'EvRClici3WuPcKLSnZyozJPrhbjZPl3wTKIiJtZEeAzshlflcCuqM5aKhefgRoIbpatRp1OUNG5mW/mwgok8wnzZlyEoGzfMN3TM2lzKhNlydxcHnWWIl/7EmmvRw9dB'
        b'dxSvjggAcUHT39p9ef/zstaXBWN8eyfR/V/zPTr9sNjYvK/uxT+F/D1t5fRLL0SX/PJHe0RtT+GZa/fLLoklpp3Xs1TPl9T1WDg9Va/TXknZPjhfGPGqfmzRr5nF1+ec'
        b'Ppc0fdTlD1esuvna83tP31x3bH7WPx+8n7+zXDuox4Oae883ab5t/KFp4MKPhqR9fFDmZyEuwJYJ2ZhDLUOmkMtW6jCU1sFdJFWPyWCvWY4sWbtMButSoxTJTrcvFbVE'
        b'AJ4dP5iYNnD7jD6wqhheRBqCxSUxYAU7UgL2EQUiIBbuGguud/IJE315JNhtwaIa3IS3YE10DKyBtXKaygfnhGATo4gHWyyRuIrabHC+szGGCoFHwHa3NXYNHiFlwdvB'
        b'SITtn5uCvSGpyPz1A+0M3J8N9xBww4fBG6ii1pJkeZQsBjYhBZWiwqTccnA7gXBvsBNs6o8qOwEuYmaPquP5PDHoroDTSIRgDM5MgleVvH2gBs1OE6EfMveIvd8Mtyuj'
        b'9WkqRbJcJmOQRGDFE+BNL43+EcaasNiaXWjgBUAET63jGGSqBRMREEJz6Mqbb77ozhdRrYQ2ST0otpc3xXajFHRYEzjfdQ9ifdnLgiPG60VwMC06Mg3WIdtViGzTNtAI'
        b'KxlQAdriSI05QiehYdNQ7CK0GBbr9Da6D1UurBHZhDVUJVMusonMqrIAG3uIsglb6HLxQsoYwlEWusDXNIam8O9iyhi6COnBNjHOaRPiMiZQWhrnbaZNnE1QnGmgygWl'
        b'h22CQ0wLNZ1atmMpU+5T7otrsflUMiY9qY9Dd+dswkNsCyqnVI/uOJI6pNyvhkUp/WyMnrX5bqJpauU2BMd0kkuCoJTU+NiElTTKFVHjWyPG95U0ySkmOcUeOV9fSNkk'
        b'pp9qJHwOF7yzqZX6hVQzY4wgpfpVMgh2eQ1dQxUI8R2CRqBlWmg+dTNt/A9JR1uEeoakXVDj50y7oIbBZbtTvk1SCkkqW43AmQrdeaU6o2UPibScVrARGYvTqUoa9ba/'
        b'VnhIZPM/JNaKtOIWBr+x+aO8bVofm38oVe5vF9n9kCbHan1RPrGNxfnKA1APBFTSWnEBrvETW4DWD41MgHGw+z2H3v9HK8E12gJa6FD8ldP6lwfYmGbGNBPBSxN4GVOE'
        b'NsCGcvRGHFvPoHSBRqmNtjEFLPo2QRuI753vxdogG3832CO/WtuDz+9Og2sLtAVqg0fj//4ozSZbALkGanvaAmz+uDz8zRhgC8RfinfZ/PGzhR/jINSKINSKENQKxvTA'
        b'FoRbp+2F+pQxvcI/oTyfoTux+/2f+Cf8HrWyhzYUPVPa3lVMH8rWg8AfhGoPq/HHNeT72oJcMNjYZtYktdC2wEp6A20UW/z4O6du1Ec174GoEFnXRsWIB4xc6haHjFMk'
        b'EmMZS61cRFrLfMtpG51PbWZWctjl5tQqHeKsLKNmhS4rS8Y4mJg4B23pZEU/8J1QaDBbcopWFE/6J+U0o4XU6n45ebqcAmRidVhhHQkfsNIi0wNa/iVNSijSSy1lxTrp'
        b'ULMXkAIX9UtdQIbiaVgblteMmatBAFfSToDzOsBCnDGCCM2SR/BFE9bD/9MB75e40geBGmmJptCqkyKIIoeaZUT6Pggz61ZadcYcndRg0a2QDjXgz8OHmoc/6EFe4Fv3'
        b'K45ce3qkdOV+4CNdYTVbpNk66YNAncGSpzOhFqOOQNcvgwjgD+jhD+jBD3yGmpfExMQsQ++x9vqgh1yaW2Rx9dE49CeTOAQGo1ZX6vBdgAGegU079ArVanZwOUXFZQ6u'
        b'QFeGzFxUc5FW5/DJLrPoNCaTBn3ILzIYHUKTubjQYHFwJl2xyYRdng6feagCUpIs2OGTU2S0YPvB5GBRSQ4Oo4FDSLrH7BBgWMwOsdmazd8JyAf8wmDRZBfqHLTBwaJP'
        b'DqGZT0AXOMQGc5bFWow+chazxeTgSvCVXWHORdkxGA7BSmuRRSfz71b/fJoLkkrJbhEodqHia5QzSoFisLjjaCwIA2ghi8UfLwiDnSpsAB3K+JJnLCKJeGRC0VM4UmhD'
        b'6SBhCBGgYnSPvZ4BdBCD80tI/gAGi9EABudCb5gAUl4Y3Q+VFYqFLMO7zq8iFWDfzAhsLaXBTSp5ClJkstixfvCY23UupvhgAkIGX6ELElZM6Sc26hBFxM/bSFix5ZyN'
        b'NfdbGWBB6iv+MyABt48tF9gENsbGTkAEY8pAIpAuEKL/SFD0oQ4xiDmyfagWJHSQEOIQ4+ewqDDrbVwuXc6VLrJxqPTZSNiyWJAg4XcAER4WCQItLlGg5VApLH5C/5Eo'
        b'xCWtLOSFi+mUlis+o8UCWmATkdqE/PeFFBIsBAJSEjOBf+acz9wEamUAEoEMMewFKkS/SXgUyVBihxT/mOJ6JxOYJuABZs06i4PVaLUOobVYq7HoTHgeQCZ2iDDurdAU'
        b'O8RanV5jLbQglMWvtIYci2mWq0CHWFdarMux6LQmJX43E2cWPgbLPFyZOKZAm+UqdwBiYeZhBMk4hA4YyYJ4RMCoRtBLQocxQeg5CCGEdShKOSoPblFGwS298YRfMqiN'
        b'BSflCCdq8UxaNLgqgDvGw41eJgiuGSMRqanLtCeFJz71fi77xka7ZlE8TSK3cqVFlxo8ynQtEu/5VHEQwjKUyTQS4YU/ekNjoVlJ+yFbh4glhA9I2NE1bI0fvq/FMSkc'
        b'AgJX7YtAkejFboekj43B+NPZVYORGvcj8WV+gwHgbFg/oMpaS5ejaln8RPQkVTmDimAxYJV0AWVKxHc2BEY5awwhwAkRYifhO/SGmY20PfImrAbrL4gA9OgZIzvRsMIW'
        b'UqVTbbjcceWsjZSK0tbVCBGSskiH4YwSfI/ekycbZyrGcgaRDyrHxpEyihficKUYpGlyFoGeQdrmJzTSIWlqtQR1lADL4IWoq7To3VqBKzwJkQbquE200y+N8AvbuA5R'
        b'icZE/JFsLsJhxEVNBatM4zFuTeexsMMFmYYvBGmXE6TXmUwy8RNzxQ58lWQRfliMKl5hfsaNrQhHGQbjqAQzQIZBz2EMwVZGgrA4DOFqOL06TpOToyu2mDukulaXU2TS'
        b'WLzdrR0VIGm8FFeN2+FyMZIXGOtkfr+Vv7MOEe42RLZ8kcvczfNxAzSGds0ksTy7H4BYb3if1eEPb4NLgViCi9Pje9/fJHyWuMEROSsbRTv9BRQrHUJm2uPgmRJlqgo0'
        b'gFaVIlImpPxiGHgU1sZ7+TPFzv/mBeiiozKRepfJEHIXuhwYmew2Me/SQBTooxeQODtxJZ3Jud9j1iBCLIGPvcPfBHaKozKFBB1Fjh7OOLmZhkJdapFGqzN1P3tL/HQM'
        b'Kg7xHI9ZB/aRsw76JwpCG4Hu9VPgDl942AzORialxSSnzcFGfHpqsiID1qTPjcRckQSDgA2w1WdxCbxuuPujgCWzvgeuBX2t/kb9lTpPH7UjksSg3eNj0LK/Ub+enXn3'
        b'o+e2vXCpefNmurV67IGhVYN2rU/oT+VZEs775f44WCYg06+wOgnUwouwAdn7sVErnR6IcCvXywSqpwXx/o7L4MxQeBye7c4JAZ8F1/nQtWqwb2IqOOScy/Wcpp0GjhKr'
        b'H2wDF5b5gBN4qrZjnrZ/rGUa+qjWFYH6Vc6wGbgJR/o0JMPLfG+AOlxzLKxLhU2wAUGAgG6i/YaBPRg8uNsftsCDCc75jsdwA6TgG4wGS1aWp4t4HZWH1ZgAenV4F8SI'
        b'cWVwz6eYdYV6h7CQfH30fEoBvs931W0yoEsupgts61MV6Hevp3fvUZV3j56JPHqyCNuxUBTqhW4U5Z48xKD7iTiRio+9OQMOg/1K98jAZpYKAKdmzWWDwJWZVkwgaFDs'
        b'8CCeviTxk+6ksxE2O/1jlzMoamlkjEEEtyF8aibxd7B+KrzG54qMRIiXpIB14OS8yJQ02CSP8QU7kxUpaTRlDPSZOHS8FfuywB64rcdcxQK4BVxKgg2ylLRUlMFJMyjp'
        b'SLBDGJELThleLP2GNWN77/ndIV+rX85u1bVqFt3dBa41ty86vlFWdbL6mX0tu9tr2ytPLmLv5QrbC8LGLbr4YV1hhW1HuHBEm83HLJomMie8w+wI2FE1p7DhOck+BfXj'
        b'5z2FRe8i0sEBMj16SWC9EuyaT0LmuAE0OKwD6y1E0b0+jomOwT6yyWCTp5ts/hJCdevARWMXoouNRmQHqkFdX55YqpbClugYeAJWKZIUDCUER5k4uGcGcbOlIrVphzIm'
        b'JU2eDBqxExLuhTdIRwuoobMEmVPHuOYznlyr888x6ZAmmbWiSGst1BHiCHERx0riKGN4u0BCrx7YFU+9crsoEWM+IhcstDrIRPBwOcLwtLLCTTCF6GL0IphtoZ4E8zhA'
        b'vKjG7cWe4KIalwKJaUes9/kttIMLdtvtbtoJUBHnX3khjt70ohxDAjiFKKdFRigHtMLK4scTDjgOTkVi0rlCW/EU3EBEko0PpRxENol+TsIBW8C5h0cNaDtFLjhofeeY'
        b'AfGEQs2KbK1mUhXKacKMx4oFM9zJ9TM/hFsj1R6cTUoDm9zucbjda0aYjQ82g60ZweAoaudZxGFgdQ9QAfZpyTQqOACr5c5IpAZYL3cKEri5IIMd4QP3uJsjoDzCAwgn'
        b'5LVyBo+qmxOyRFhzaDRZMpocGU12LfewEAG3meDJCcei+yJQAQ8q8XRfDD+TPzcpGtbBJnBn1XxEyQoZ3JSaPN89dAIcBuwL74zNJJMfY2XOGRG9vfxNQTxFBhJcnADO'
        b'exXJhyAj6c9HgCRbQS0ayhXrfMK4QSRuPXGhSYkkIOrvtDmRsHYhz/3mdGDMOWifj3AGtovgedDIGaxFb9FmLIh+PlRz2vIliRN7WR8TLNOkagqJtiA3faV+LfuV7Nez'
        b'kzVbtPeyz+q+mPKn9+Ko+ePp+QmV8+wJn8na4ra16cy9jsXFV0hnVx+rDA+dsY+O6Pty80sh9LsfP/fmcx+9FPbq3d009d64sDM5c2QiPvaqaQrY6Q4qg4eg3XuyxEoT'
        b'DWMFbAVXujDEYDHPEM/DK3xhNwalo27as7KD7XmwPGgHlYS5zk6DF51TzekomQ6cxrX5wwtsGGgF1ywYxZLAzXgl3ASawDG4g5+TjkH6aPBaFnXsQXiB5+I3Z+WhRIVw'
        b'j7MwAeU3moGNg+B+C54kLo0cgfS2JBm43SW0ozTr6flvAA7ZyCo2FVmIZU4YcLiLAa+jghnipuHoIGSzSMh8xupRXbmfrlSX4+R9Hdq+d8k8rQt4M6LD2nrcHKVzKtPf'
        b'nYEw6GJ0aaJdsqKC/P7syaKt2PaB14LXPRG3AM+O6I5h4JjyLWNhu2AGvD4FXB4KTsqowXB7SL4V7i3E0L07uA/3SzA15YeeH4b9wFwZ8d0amubns+W76TYRoro+xj4b'
        b'jSMlBynyesF4PM1NR/5ArUs9MvU/yr6U4bm/fE2ZW9C3Tflbhjbc9gdxQVXff6gqHL4tyRBWMeKD9fTUlaa21zTjtsQbiyMG+idE7P1TzVf/9+Wa7CHlSXlszkuW3b2i'
        b'W9bHf9JccuP9M4FvVO/d/vym1YnMysUrGj/o3/rxtPr6FR9/k3Wk78SBjonfRsd9fPKLt0OiYsKufLNgZ1Svf2985e9+CnHQkEl/rj/6+dZLfb554/mPpyT/flnyzbzv'
        b'ikLmLTj057fsA5uk0cfe5mT+BP+G9PHpopGXgGtYKW8aSFLAGnBoRDQD9sd0nq+D69N5/b8FNIZ2orwcC7EAQLU+zxKF0uTFm3l62glb3WMIatBwofHjmXOiVrgMnBJY'
        b'MBJkTtFHxyhC1riVFlA3m9Q1QS7oLBfy4SEB1XcUB+q16ZYZFI7vPQ1PeNkBE/hKH2cKuO2APvAkiWcdHZYL6hGcewnzcWcVUb3gehZeghvBs3xE4kl4bQIfzIJBI70I'
        b'DoLm+Wwk3Gklk6LzkeGyhw/RJ9HLsHYuOMaUFsBTpF1R8BC42tnsge3wPDJ9EuEmwnCQ6G7u21WmrQI7kEwDB4JJ2CTYs04E68GpoFSaosdQCPjNwP4QavR5WgNd6GY0'
        b'fh48gnCZSBeXWetW8xgcXcZhpzG645jgQCG6BjFB9Or+j+Q5Xoqf0Pmug7OIngRWxmSivKymleiyxksJtPfzVAIfDRKqlDj7fbOcL7KyHJKsrJVWTSE/0UOsMqJpkpoc'
        b'/nj9k8ZsztEhruk0+n6TU8Th4ywJlUIakocuOtqpe4mZIFGYvxWHf8E74BzY78Ege8M9XkjPUOPAbSHYPd/DKYp/XFPHZkynLl+JjtXyWhBFAjMZLbvRB/tGiP9DQPRX'
        b'gdv/MVtjQf1mRH2myuE8SnVbmGPQxaknO92uepFTs+JqREizEiDNiiOalYBoVhx2AXavWXXVkwUqEn46Hm5djfXky8u9jUw2aDg8JmPIWhFwEZwM9FSmkWyGtRwF7OBo'
        b'+HQuKQMcIetpQAM4U+CZLjoqSYgjwA+Fm7n5WWCH4cKWQwIzdqdbi7/6Wr34bjM2C++d2the2V55fbeBnitSijY1FIj+MPXzzOrw6sEXA3aEHC8skfp/phsxOuH9uOcT'
        b'fh/HJRylRuSGU2N+HzS77zcyjveB7AQ72egYcAqe78JwawYSGk/vuzg6Jga2dth0YNtYElsROQPsImArQS3mRaVRSCHRsUg53hdJ2NCYjMkuJgSvgJt4GQXiQuAk2O5S'
        b'Np6EvDzDgfVo4LOwdUbYQLCLDayj5L6SEJpjxQyy9fp2wZQYdz6eOIQONqfQ7BDrrYWEpBxcMUrrEFo0plyd5bGKBWfCIWOm1fiyBl9sbsovRZeTnbSLD8M8af9R0MkY'
        b'FXY7Y+QxmfHFQtgfIckVOktekZZUYLK6uqW7WI8SNzCr0OWEy6mJ/cVWTHVgT05sB+WKkWS56Fqpxi9TGy8VghNIrO0mVgA7huVDoGYOKAz36UF5zXF4E53XLIeb6CgS'
        b'I/iEi69ckw7eRNeHXwC7XIZMl92wzozk/yW/lVayqu0qbLeUwMt+JaAxsFgC23GI13EBbAM7R1mx2WwBW2mUvjZVBRujVeDgqvnEak1G/2rTFa41tOAsrJHHgPYM4ru8'
        b'BG74wmfLUh65yJclkRO/cd1Ct4yFrFZpAxUZ0aA11T1CiEorbD3nsbB+NWwk9ma6jcF05WzRqTS4PRqcjKSpcLCZM8XCFgNbdpI148mI0FWff61+5a9fqTPvtjW3bD1Z'
        b'efLeycoR9Svp5svNPe6J2neP35URNndXaHzlZ+PDLnxY/824sNC2ih8N8+LiLXGChKOIaxTrKertpcFbmnUyAYl2WrEY7kTGB1ndJARnGHg7N0EELpJvKT7wUjQyh7ck'
        b'ET7CjabBuZXgOtHtxqxFmgv2AMA6BfkMds2nAsF6Nl8MdxF+kQ0ODkHqxIV+2EbFK+q4sTRoh7fBRhIjCU8qEMPxXKShATvL+oI9j10O46cpLtYhGsNU7u0nWkfNwVMn'
        b'EjIB6EuvjkL0n1VoyNEZzbosvaloRZbe4GmYeBTkqpVwgEdGX61xU+RadHmjE3u46BWBpULvVeCaWpmuALWFUqwJOse5MZ233ZFZSiRtZ4PD2TOIF/OdrwUHglbA40v5'
        b'NYMtsDoyGpW2Nxo2JCQylAAeoMEljYmsI0XltsC9iEraV5XASysl4uKVkpUcFYqXwrayuYvhITIHGpsIW82IX7T7+Jf4+8N9vgFieGEVJsaVAioimCsHt8AOUt3kmfC2'
        b'EkmUkmx+IMWgjQHVcLOOkGQZqIRb4OFpiMdsRfRbmxqVIkciaNsqeST2DaS6lpHMFZN1zbFRNAWOgot+02BzthVzmrgeWU+UE6BEJPeOQl9YNUhJFrvCY7B1PqgvXgma'
        b'VsEr8GriGsRPLEjRvQrb4FUraslcDqwHZwP5rjmlRRo5BnQnFt/IdKlPFcHtcDcVCDezGQNgBfHzTlkN13uUCS8M4QtdBdslvkIqIpkDdcjKP0O0WrKkD4nB44WjEbpf'
        b'RBg5HikU61da+QkOeBw2w+vIFtiarkiGO8D5pGQRJZnIwAPlaCDwJEwUsNtANTjlp8Ar/5QL+bZjLHEyN3CZMLJlcL0I3IKH0q142dYAcBNcDgHn5iIYIqiIGSWEv7/C'
        b'iqkg1KVxem0PRdlyZ6C0CdVIUUFxoTUZS+MYpOKS1z1GOMNhhSfWvhSYy6e9m+dMKzRMemXGYIq4CafZ/LCRFo39PrXE11ML69nuYCwCFeJyCdxjGPnsHpZMdrboJGnN'
        b'N1PYZ8Kq3pi8Jjlx9Pf0GuWPdMT8IOWPGWcaP25az4VeSFzy6oaIqS++8u6ChMaqwOxPE/4pf25d4t7m/Nc/tZl3JQy5BZ/PWZRtmjd1yLOh5wsPfVp+bNr5LOGwSz2i'
        b'G++Mmfp+fFv7uV+mKtpqDrIBY2wFO7ThfxbO6rn9jZHvfdt+5Hrzkj8u+rf8/AfH27LmHy/cutX/d2frrn/4Sf73l0ovXPz7C4v3r7r+121ppW+81evAuAv2kRNG/J+y'
        b'/I93fj9k26nSUUGHP1i267x2/XFNfWCiX9pn36/95ZUpoivfzq6Wha269tKQOmV/x6af+/fWHR3yh+1LXx/6l2krJ06yROzZObJ//tBfQ/418/uMj7JvpGiYs58/P6vn'
        b'0I9OLLDZfPeOKR01JbH1563J8n8Vrbzzl2NDf/1xf8ONn8fPeH/E8+W//jT2taTToogj64I/Xi1rfEYWSNxBw+BhcGUxDiuPxmtE67C3xw9eYJniCKLZMeGISNMVNMWU'
        b'gB3wMP0MuAIaiCt/JtgFjveG66M92DiogDWESy+FVUokXvcoU6Ni+O9+hQw8qgSt5HNfRTFe0w7r48ARNMp40qyeKQcH4VEC1Fh0d2fJhOh0DBDWOEQIpjsMvDrPRiTI'
        b'2nnwAOZkZdqOpXjLYBsp2hY7DV6dEg1rkuXJRI4IqMAJrB4cH0YETAmwByjxvCTiCDtQyTKFCmkzvVO5KT3hGTIDMnbKtOiY3gOdccck6HgAOEPKjoN1YDto8yEwwXoR'
        b'xSlocBZsgHbe0j22mh4jjU5JQ5YuN4gG+8F5ZEwPIfSKOu8gH8yMuqUecyDEg5QItXuDK1wSaJaQho1Ghv+z0THLYUWH6EyImEMgBwdjyvD0C2JARzuFKV8qfJxH7sls'
        b'VE97ule3Qo4IxowOwTgLi0WORBsHMb5MkC/6Y4JpfPVlg9C7cLx+ANneJJQKXXFkgpjE0wQhaRZAIhWC6GBGwpjWueQxspWfzrj2iAfEhbzQSXje9tStiYPayIF2Ijwf'
        b'LjoF1HLLAFoMtpelyFh+BeXJGVPx3NhVxC3dk2NjtMTUC4WXEC+uV4GzPtGpTq8quMzAY+ACuEBWnof0Am3RCrwhwG1YL0Qje4hJiE/IYT10vVCXvoenIrrsf0C5d0Cg'
        b'vfZAYOy99KHuWQHBQ2cFWDKFz30agcbQV+rxk6HLNZgtOpNZasnTdd5pJ8bXK22yRWowS026lVaDSaeVWoqk2AuLMqK3eL8VvAhUWoRjLLN1+iKTTqoxlknN1mzeR+FV'
        b'VI7GiGMoDSuKi0wWnTZGutCAjBerRUqCNw1aqRP5CFSustEHSxkCwaskk85sMRmwE7gTtONI7IoUW2/jpHg3IXyHYzlxkc7iUQu7yVKgK8Pxlnwu50OnjFppCeozBFO3'
        b'BVjN6COf3Z1+xtTkaXPJF6lBa5ZGztMZCo26vBU6kyJ5ulnmXY6zt12hphopbqMxF8eZaqQ4AheD4yorRqoqQh1XXIzqwmGbXUoy6EkuvkPRWGVrMEBorNDYmHNMhmJL'
        b'l4Z4+TgCupgifior3rWjOAdcmRvrmqHLWJiENM25SSmCjLFjwUmZL7xeBpD2MRZsnzJ4bC+8CKJV0mcNqPPC+yBX4SneeE85MZ92Yz5jD9QH/ZYZMMwguu7XoVChNIR5'
        b'qLq34tyBCE5XkXv67alXBHdd0ybgayYs1xC57C3GjK35gXfPfa1WfJ6kkei/UH+pXqH/Rp2s4TZ/KXmtwZD6YeGMzP4Nnw6Q/qh6f8KVgPct0mWad5579zkquEBv0dS8'
        b'd1Lw9RlNs5b6Wp+vf/VzeR2zVxy67G5b0KsXNJGX/EQXQuNitGrtF2rh7qBX737IUP9JGth/xmkZQ+Q50ilrfaIVkbwLZw8Dr4FdCrBeRgTTSiFWEDbFRsWDGiTcrDQS'
        b'X9fBnqefDxJkrTJpiokYGdAhRtZRQzkSnOaLeDQfqxuClwHLTE7e5BGU5sRijze4RJehRSI/O6TH48QizWcgomM9ugxGkJlDO0RHBXXfa9pnMkUCfnatiXahfDfLgpEQ'
        b'39whWGYEy2JT5Fhfag00rIb2R0RkscQ78uTrwL28IgKqO4+BSGXFcbBzwW7YnIAE14m4kfGJI0YlICnWZrGYSlZazcSmuQQvIJukHV6GFwPFEt8AH38/0ARqQAODzCp4'
        b'1QeeBacl/E5Uw5V4xbD4zSHW/MCSAl6/fz8qmWpGCtJdoynfJhE5sXqiUEebNegu1rep10stwVNmBwneXPOPFW+9dn9hxDNvnm4XVP1dz9VGfHN8+K037qdvfn1f0ku+'
        b'fx37WfPQhOSmY/tfeGFadfK2iIOfXt1w2iDZO+DjE+/+WgbVjvuD2nf2PPzJyEn95iyNjbjT60BVf4TDWHEE2+EdcE0JL4NnvfZpgAdGEBxni7EHq8NxAK+A26A9MfVR'
        b'0RuPj7wyFVmysrG9jDo+zBOpEziCyCEkwCSYXi1/InR2FueadHDHMj86Jouk6EDmDegS1wWZ3/ZadTkFfVlLKR+Jyp5oDOtiQW16fGKmgkV6dH1QDFJpyOgrk4jJl7ea'
        b'Uaee1C5z2q5nYfsSuFUA1+dRVAwVAzalksSgN28K/lGqlm8O6snjj08GH0ZQPE0tnzMvh8cf8mXxQB8sIIrnrlCn/iEynH/pv4jgYNKvoeqU5+Jo/mXWoCBKisq4YFKn'
        b'1ocnUCTOaxXYDY7MhY1w23x4G14chVR4jhJm0OAMalo9yXdrRF9qJEWpfxeitn1qm8wXdsbQTlfkvoAI6v6qsBg/fr8iPwHcPBc09QekuEYBxarpSdpQ4m4A1+BJcMDl'
        b'coN1a7ENiwwNWCNPwR5EbHSQcAbYFI0Vd1Ab7SubCuxk4jZttJDqh0Bv69FT8mFYxdpmiqx39o0dLhZPjI2j1alKU45idPHs1xMvLF/FEUs9JwOcgBfpaRNRdioNbhAS'
        b'uPtPGUdZUEmSger4PwtH8o35w6DJ1MZ57wqp2RWmXQX6FeTle3mTKRtCkgUJ6mD7qgl8yn9nymn1JBtHSSvMHwT9tT95udfnffpSYF+aClpfFGZcv5y8nBozi94WHoKG'
        b'fX3BrlV7Y8nLClsIHafHM08V5bsCJifxtWdYqR8i+yEpWFHywdrbq8nLlOXz6FaGCuoTrimQJQznaz8/azMdOStAQKkrchcJ/ETk5Qc9F1HXCkuFCKTVYaqSqeRleMYQ'
        b'OjX8VyFVXFG+aElLHHkZNm4ANb3UgZtp+8A308LDmZlKH0rZQaPsBbvmbOfLHOfbm5Yz1GytVN2/ebiz7bKoN+lDLCVelq2J/TYjhH+51vg8hSSe9M1kdfJGhOTk5S/q'
        b'cuqfqL6Js9Wht3oy/MuMQR9T12hqiiVDvZiTL+RfnpVKKMQSgnYsVssF0UL+5Q+Li6kK2RCkadzPDhlxL8vwl79NYM1HUQcxvWzz59zc9O6UoG/KHJ/c/luMqPTHn9Z+'
        b'9GONWOzjc2/0mCnN2/ctyqwd9dyg16ZP+uz6Z5/V/KD9NfAgFL355xlJ90wLV10/fmNNvwv6XpJnyy5u+CBj1v5vtxg/6W+tf2Xq1GVHJ124sWSBb3h1wVv130/uX3Wm'
        b'187F99TKG69ee/366338j/gM+4kd1OdEflDSrE91r878qW7Opoh7tZVbchJfuHR01OX4C0U+F9dv31pZAmaUBDwYpFxwv3X7N73L3lf/OPD8vqk3WsL8tnz0xtd3b2T+'
        b'4/Di9uXvhlyUqgvK7o0JbVv+7aQhfzX/zl9zeVPA7zY0nz25RfDvMSUffF/Z75ekyuf8P3l5zF9SLR+u8/1SvXKC7ye/+8+3V/beyZjQ62MozzuwI/f5tI/yt1995tNE'
        b'3zMrRUMTr9WvudYkKq2ZVdowvPSVvRPNwcNt75yY8Jr5xI+Ho6atVZy/N3zljZ8OfN679EKCY3/+gx3vJnz3tyWzbR+secv3YNwd7aWBhuGT3/zXsFd/PNXr+y+U371z'
        b'aGnwqNv/Scn97Iwy/73fff63bW89m/oP06/CSxMjIxZ+/691P6TNz1dufiPmv5Tqg6a2vjkyMXE0G8AOUTQ4Bs7GeHoKkuBG4kRI6Qfbo2FNLGg24On/Fno2krKbnBkP'
        b'DItOUSAhBa8rolQCSiJkEGvaoyaKlp9+vIeESgNnsXe7ZxD5Bs77yaJzFiEGnQzOcHgntcGgAd4i3oFypJXciI6RpfD7FgrA5iVUIKxgi+BOeJrMxE1PLiAOFdAMt3o5'
        b'VcCGhWTGX8NAu7nTli4RqAIc+qMErU87OR/09JPLT6xFil1ik8jcpZ4yd5CE5pjQgCBfjvbc0Ar/H4D+h6HfYDoCicB+tJB88cXqJhtMhxJJLSR7HYjJgrIAlAN7LlaH'
        b'P1xuu8KO8IIOh8hpKToExPzzENj/g6VwrGkjvicrR6rccr4S8/wucv4vUZ5yfhz6AqtGwuOPkvTgwNgOYS/A889I6bslBjvJXD6JbuF3h3R7a1XgrNPVEQufBefAJQHe'
        b'RBTW8lNUtXGgymNKDQd8BsHD4bCKHWABdwgfnFGGUFycKcB7mv67/0yeOY6agzQBCWCoKerCbYZS/iUcjHSG6UdYvNHp0BEJlGFr/VzWfBB9ifz+vf4NEwNAnGTmt8NW'
        b'vHPpL6PFK4cnLjgasyDwzXiGPan9a2ixQFXz8g8R//755+FrvzJOCfux6sKnG/yXnLv2efWS70pfKPjkxwOlAwJz0gW7X5hhq/jl58X7grfFg/eOTroe8t3qHsMH7fns'
        b'oHTtAMG9zz//rnHeKwsmzB9eU7ox8LDjnYX7tsx9ruXNdf0aSu6rj713679/uLF93M1v5nG983YM/G5g7OoT910Rg7cmD/HcKbcXvMNHA/Ib5a6Bx/h9Ck4sQuPidi6O'
        b'A7eIf/E02EC8iGALqGI8dTIcLpiKp/QOwH0hXBG4lU/CcsCzo8AJz3RpeNernXBLFAtap8NzhGGsWwLP4TQdoxjQG5wC59jpsFFBlOWifjJQH6tQKWBdqkxIBU619WOz'
        b'UuAZHpbTS/xAfbpTwXFv6dUXWT77+nDgCGhZ5jIOQ//njOCJ2YSLbr0DgvBvPxwOFDlLQlyXDF4byoQy/OYJmC2YqlFalSdx89RHCK+DrHv+f9yWhxA9Bk7Uhej/nehJ'
        b'9GRCb0vqVH9Q4SZ7hgpMZPVwZ1KXaWb8Y5bQHeE2WjqT1TKZnJbNFGi5TCH6E6E/cS6V6YP++25jt3FaQSO/Uxqeyee0Qq2ILEny00m0Yq3PRkrrq/VrZDL90bOEPPuT'
        b'5wD0HECeA8lzIHoOIs89yHMQKpE4PVGZwdqeG8WZPdy10e7aQrS9SG3B6JsY/2pDG/EuanifwN7aMPKtZzff+mjDybcQ53NfbT9UQy/nU3/tAPQUquWIA2mgIyCVZ/Np'
        b'GqMmV2f6VNTZeYodfN5ppCQSwyvR43IYzNiTR9yp2jKjZoUBO1XLpBqtFrv7TLoVRSU6D++hd+EoE0qEPfRO7yTvGnR7HUmOGOnsQp3GrJMaiyzYo6qxkMRWM95M3ctR'
        b'aMZJpDojdiNqpdllUueS2xin71eTYzGUaCy44OIiI3EF63CNxsIyb//hfDPvUkZVaUweXlDiK16lKSNvS3Qmg96A3uJGWnSo0ahMnSYn7yEOXmcvOGuNIZ1pMWmMZr0O'
        b'+6O1GosGA1loWGGw8B2KmundQKO+yLSC7FYoXZVnyMnr7NC2Gg2ocASJQaszWgz6MmdPIenvVdCD/nkWS7F5XGysptgQk19UZDSYY7S6WOde5Q+GuT7r0WBma3IKuqaJ'
        b'yck1qPDuDMUIY1YVmbTd+4aQccqv1iPLofSCJ1iv53T2P6jq6lM2GiwGTaFhtQ6NZRdENJotGmNOZ68//nH6tV2Q8q5t9GDINaJ+e2Z2svtTVz/2Y3bjFKqssVj6YR3j'
        b'tHP9B7yQ2e0SEOcCkB5gB4k2GDeU9VRKIpPkMTGwKTaFhje1VCLYKVyjB+dkNL+vd/PEZUq/FJQuXYHXJTSm01Qw2MfC9fDUIoMsOIU1z0bJposS8dqqyPJTf/oS/ZeH'
        b'fqlOcq4oiFkQqUnRMBf79I5bFRerXXr3QnPL1uuVsvrLldcrR9Qrqq7vPFk59MBEsirRn9qwrMf+S8OQvYBVAB94RTiNzBJ1I765Inh4MAm2W4a0eJdYBufBQadoJnL5'
        b'WDI/EXgMNA31Qy2W8XvuB49FikQvYOfE4BbD7zXUOhLrGtWL4aakkRzFwpu0cRiS+8RFtgGcmaEEVeAy3xE02UUMrAeHFvIrtGrAJaS51SsVIni5FO+8TCvBFtjGf7T7'
        b'ro5OgDtwufGjWEq0moZ75oHtvPZybnoCaV5NWqqwqC+F1EEaXgfPgtMuOfoE83fYd0CkdaintF5HhUjIMgGsmK/u7Y217sWEKs84XVO9t6juPkqP4ZPle9Vfx7gceRXu'
        b'33+GeMbnPQyC7tckYQ3WRuXzMV60ioTQumafkJKU7+6Bjm4oQpfdCAyyNKlLda7FSw/6PHRSC1XCaotyHgtQLg+QOMtpujwCnn0ueB6EeExruWbHYp68KsxLDVrzI6o6'
        b'6K5KjqtyqXHdzKHlFBoQl1aYEbOWPR4EZ/f7ZelKiw0mIgQeAcVhNxRDMBQdebCc6dzlHZW7eHdvN+927u9qF3jw7kd79vWd96rr6tkX8nvVRcLdqrmwEb0Gl6k+a0BT'
        b'FniW+Acj1BGgGh4FpxFc5VT5Qht/LsJIsB/WJxOFPYHTgSZE/vVMCuK9pwzrfv8n1oyXvP/3wd/717/sXxEnaT/BrdpffJQOP1IlPvru/Vv3P43fpxpR9m3epZyXj376'
        b'6WsBVe/E3Tt49O0LJ9bn7Ik6MKoVtv7YtP3KP8e9efIXRd3t488tfud3vzyzc1/k96KghD5S32UyX7I2SjFQ0JkTIuum2sUNg1fxW2TvQnAdwZ5TfMgCnQLbKTG8yYBa'
        b'eDuEuFmWrmVcsX7LlLyrXwX5ZdlWGhyIRuxnl/P0B05FgzZwaQnxwYQUwWOwXgvPewURBsMGUq0YbIUHXJxsOqwTulhZHbjGO2Iq5oPjSnkw3BSLT8ngEmlwC2yaxE+j'
        b'bYWX4CXnYvBxE53LwReJ+cVXe8HOXKXrwAh4B9TzezjGgHN8qPWeLHAJ+5BXJ4GzSS4GHQxOs7B6ULTXXnFPwk0RremMOaayYgthqf28WapMQuIxfElQI9l1twtbc+b2'
        b'4qtPtPWjc8/dDr6K99s91g1f/fjRfNUJwP9UL9rYrV40LU9jzNXxMRAuTcZF4p20JKTsPKmCZNStehK9qPvdKDnEq0gsLzwILoUo8VEntfBqF+XlRj9D7dpprHkRSpmx'
        b'NcD/lejQCumRxhDuzT6l/92zZG5lot9Ld8Oli188ZKRLTo3Oap9y56efLkz915+iohK4xb8M/+OIhBGZgM2ecXdjn76fZf/8/ZWpDcvuf6tdM7BNPWZS66iQ/fNelPkQ'
        b'erMOhNuikfBfAbe79AqwZQ5Pq0dgDUBUU7wkHa/7BKfkkTQVABtZ3cxVBLenK8AOcm6B8plOmI040kmednaGgpPY57AM1sA6muJiabyUtIGPodpfkMvvSKtMB42xLk0P'
        b'iREqDh4SjoXnJQTGUbB9FlFfKAbeQD2H9ZerYwnZz54ITyndag9sX0U0H3grgQ8dvpRqinZrNnAD2I21m9VI9SGk2wLbS+Bt3mlCVBwnV+jT7+npMjCHYFuWCzU6xxvj'
        b'33G+ZBOXEHr1gE5U0Snz/0LtweeutHVDnm97kedjAJGxDmFekdli0Dp8EDFYjFjMO4S8uO9+HQ4hYc69BkfgXoMjeOgaHJbIce7TqXQnUxz/PKPVYrMGk52HpsCbgW5J'
        b'/VDa5YHnKTcJ3SdPd3GAbI2xoCv9ukne2VY+52z+EWWOVFqNyIhUJE/vJrjHI1DIlRObzDibV2CQrDt4TTqL1WQ0j5Oq55msOjWO7+F3CNDKpeqZmkIz/05TiF5qy5Dq'
        b'gvUno+WpWRCrMoxe0kNA9hb4Yl/g1+rld9987oPn3n3uQvP1HS2VLZVj69t3tx88saO9ekT9yeqWpkG7BjUPqhm0oUfAIMG9P6WyVKK/n/EcUmd402Vjj7GgHjEIeD3S'
        b'i0fAZniYiFblIH/MAGAb2OvmABlI7A7HJHgS3gRnlKnJODob1KanwbrUGLAploRwykCDAJxFEr3h6ckxQKPVZumyDTlmopsSagzypkYlpsXV/TsRgHc+JyEKebrajS97'
        b'8GWvN0l6gsd5JMt3pyUkuR9dbndDki94keSjIfqfEh0OHpzVHdFlEAcVojsjj2g4TM2D+jxcU///oz+cLXluupR3Kll4HxSxDfQGo6ZQqtUV6rrG1j0Z5ZUdmMESyvv0'
        b'X3cfT3nRW120hynvVYpKDPQrtr/hpLy14CaimXoimyfmeVAeaIdXidwE20uXgPr4sYj4XIQ3HW4hhAdOz4RN0SmIbBtjlaAxPa0M7vGkvclgkyh4fvDTE14P3rf5GNrL'
        b'JLTXSQuL6ZL1f0t+eHLp1W7I74oX+T0WqEecaUPbKY8zbR6+dzlLbGfuQXY3hEewkFCI0boiGxEbQjwPR3GH+zXHajIhAVBY5mFM/xac/O4fIQISFvnh8JH42Jy25haC'
        b'jSPqh2Z3LwmIHBBRX37v83KkAGEjVhZjwLH+PDImglYvOdCUTsRAgBTWyf2IJHAhI8I+XgyA5pF4s81YZDiC2mC40VMORAkRMl4XSeGuWZ2OKOoW/XKKrEaLx2iZu0O/'
        b'bHF36Nclq8oVgpj/cHyjPVQuvCnDH7pBsBMBj0KwLtX+DxHM+FAE64g4fmLkkkZGYS3MYJSWJMaMjOqGAT8e2ZJya1mCbKsyXnEi28XXnej2WGTL/QwhG/F4HvPB06He'
        b'ZolIxerS5hOrYxpijfvBRr0XthWBs/yhX1vgyeXYIpfHeGgcK8J4XBsD7EJwMWvNE+BaEO7Bx6FaPr8PVacx75zzaTHtCLr8uRtMO+iFaY+rVda785pjUVaWtignK8vB'
        b'ZVlNhQ5/fM1yzXY4/NyrRwxaUyPOhI9nMm3BF3ziDHG1OsTFpqJinclS5hC7fJdkytMhcnoJHb4dfjfiRSC2CtGOCI8mdESa+Jv3NPBw+9nRxco4I7/FfhyDIzjdv0y/'
        b'AIZEiHS5MsF+/fz7BfYLDBCTZf0KeGsojn6wFPAOLng5DdmtyPBkqEiwXrAOnIn0mhTBRDyFci5X956D5eN8HT2dCzOco0T2d34gnVGKd6XELskcvOrCZMS6l4eupUIi'
        b'znvUTEfdLe7k8jyDLl8z7pXgHM1vZ7cpNaBjJThsc7nsXOc+pMAj4JqvCDTBetBkxbudzoOXSxOeKMw4KaTbQOPbcK8XV/Nz8QbcQ85wfMr7bNCOTXKfJjAfF97VsSpR'
        b'yVgSdTLcx4+KzMOnlkgLdyV8qiahmtcySajmGPksSvLhoh+Z5VQhXkS9vWii4Muw67m/zugru14wO+vUwNaCG4s2RO5RvThm5OJG+f70s+OPjVvW/52ow9n/J3+Qts7/'
        b'877+5bfmt0VunDYq5a+qsmc+HSAM9+330aKpmX+edHPYvozJ82r7b4u6NXDJ1NjkjNLfB7YXfTvSwW6OyiiO73ds1OfT/649ML/ab6T8OjOlh3nweMHfxo4fs035zeD3'
        b'ZjQIP163Lgs1TKgedY4hB1XCXSHY7wurzS7XL+/3DeHjNnfEsyl+NL5TF94Im80H3Xyxrmf8LxTeWVk9QSQ08C9PDgzNm0MvwocTL92+PJ+yjiKlo8L3wPo0RQw+5zUS'
        b'1oIjwE5WnMImpQhuBifLYO0MsF0wFJmAw3xgCzgUyIdCzhakfIHje6eoJT/lBfN1HKJF4olsGK5DnhuRyW/+mmq/kEMI5WMfunaAobH5TcqMqbV808WhjTf92RGSabKX'
        b'/7EydMuLY/ouHjZeK6Blb/fPcKR9FLnkg70zXxw1eICsOaXXlV0fnP1xd+q4baL/e37q+pTq6vHh8y+8d3TOoGXBn3xqsyX9fmbWqnMRz1zd+MqLVX2XKa6sOvFl4Di1'
        b'6e4aw9qbM3tmfRD/n+/6pH30B/37Lyz8kzo3de3gO/893TRs6/U4Gcd7iWpADdyo9J/kPhSY+HdBC9xrwbvZD4cbQUOXM7PhNXjZGQoE12fyR6g8mwUqoxX4FFPciepZ'
        b'AsoP3sDRegcTiYa0EG4ZHw3ronqA9dibhdeTjc0Hh7qGhv/WvXk9l8abzBovT/Jgb7Fl40gcXRD2IjNBtJQR0yH4xKBzbq7MOjg8N+8hrH7zlsG06bybZeEK/t6NZGuQ'
        b'eobCkP1TmmFrv+goFWjw0APAsZl9wX4OnB4M6r04Tnd7KnpwHPeeik/FbbqfxvF1cZvrZX6qX5nZhNssKvzUn3CbtTYRCQynZhZKvpx5LegOz23icv8/5DY+RdOPFZ8f'
        b'mJ31B8Ml0eD5R9W6MSkFr/p8mzwx2r933iKToGLw59NLfL8ylxRH9v5wxim/Pv431v2KuM0XYSqeqqP0LMWFLRHhwL6fQobyVP3hjGAqIulzHO3X79W8/vzMGvlybiQi'
        b'k9TXhIgJyGePT+FfBlqFlES7n0FMoPAfGi3FT+GfR8Swk8xfncJL+zsYGWwaZPg+keLMRpSsf9IFxe/a/WGchLt7YvmFfT02XvrwXnRQ8ebX5/veDGZsV9pG+wuuDXru'
        b'2RN/oJ/55u9HXvlg/IRRYw6WmteULT9k+be8ekf1rrnTcrXvrJj/S1vRf0rGy/d8HrZwUahu4oqBP278fcHFub9cv9/+X3qUqv+uF8tlNCHIIHBlkDI5rQgechL+MkYH'
        b'T9BeWtnThdB2pkCtroMCI7wpcB0ViCfHQ8juViGECiWEJk1tHTTIE04HCT71blsdhIdLFbOuvfwqPH4feG5iRQZt1lK4jae85DQn4ZX79FVzoAUcDfRaoYf/yLaXeYgY'
        b'awT8TvI2+hCFya2FKWfIPavl0D3bTJdGWmicZjrVTC8LX8qUc+V4x3lBDWVh8DEISKsMsAkOsVpBC10uWEgZB+C93gt8TcX8qULkGz5xSMDv7W581YZPs5lCysD5b9hY'
        b'UzNKJWjBZwudQ3dCclwDrktYLqqhbSK8M71W1Ihy2IQTqJV7UC3VJL+gEp8cw5rexEcjoHYISo0IWgHZCx/nF3fJL0b5HSj/TJKfP8tnijt3pDt3v4flbqbxvvg1Qj4H'
        b'eocYMypTvtC5K7/ztJ5sG6X16YPZFc+ifFWIOet0xTNNE1Hfz3sgsFr0ijHuQ2cQArfjIccfTXhvDBMOCJaJTHhhl8NHZ7Su0JnwYQ1T8LMQ78Gu1Tkk840GfEP0VD7v'
        b'BB7nOvZm7CiW7IlPFi9h/meKxiXR+U+785MEH45ijucXyoZj7BxHGLqYBHniIz74g0KCyfkNHFmTFeZxJ3H+F5O16mKaLCDqaenBn16eGIX3syFx89IBaeAOB9vF3sfn'
        b'ujebxtLIRpnFWnouhY93Ip3PkNMTsEQgHWga6SZM2kGbH2I1+pMmZVmKsgqLjLnjWdehnyy2R0gEFKgTjuABBJvAhZWxSPciWwNixYsaBqoEZeBCrNd5PO4ArJEETC1d'
        b'QJsk2M7QsjZ8hhKt5Q5R+HweBLQglGqhbXRvCos6/IZMvgidTSCxEczQUrJa60uGb4tgtd5QWChjHLTRQec9rF24ObhZpH1Tcbt8nWPFkeNYyEGUxSnwDLa9UVtAUyw4'
        b'Cxtx69JJa4XUsAGCsqyCRyzcpbtduPvoQwK77O7mLtJjSWXH6rRDA4opdf6LNFWsFi5ImM+//I/gBeoHXSiL5Jlhj2Qe/9KQJ6SOKolSm1qjyKYMp5Rvc+Zc9OXUsfyv'
        b'1cvI3kuXwdnKk5WXd79VNej9UztaqlsqB+29nXSi0krn+E/z/fPU4yrDrPentoRXC1L9+tRVSQ/3l/d/dZTktQZZavCU4MOD+0W8Io4fXrVYEnmjYmyVblBOHJsrpK5t'
        b'D28SrkUaKgnhqoabQCu/zhdeDiVLfRULQDNRXy3w5MBoj1PytswlB+WBw/A2v/Xm7mRwguzcUZsKm+Q00kl3BoDTDDxXCM8QKRiv9AGnU7C9CGvpSXJKuJYZPAq0PP1C'
        b'4R4rirRjR/NHUGRpDbkGS+e9Y51bM4lp/mAeMd2PNj3nJqr/V0uBcTHKbsXbVa/lwMRAPjYN7kUNbkwH7SPJnrrgCD71ZRM+P9bZTWPACeFa0AjPd88vsBeI5xJY1LXw'
        b'x7wwKodAY84xGBBklym3/O16RKwoT1daaNCXzWedx2BRLL9J0J5Jq8iEOzxAtqSuTQWnOTRiVXhevGpW96BglodPXCHyLwQfUIQBKneCRxgYozIBHpDJHmA9YmctH6vR'
        b'CWJmBwPDygkBcxa4ZIlGlE0gRVCuKiVw4s3M9oON9BP32EYPwB7ZXz7ZiSP547Q0Hj1Gzpzcle6njE9IJsZbJLyI1bjAQez4TOlv7Ky839BZCDpehuo7dRaJsriRCo5g'
        b'ELEzxgbbSHAoPMeOAAfneQWguU+GwyJQSyOmjtSn0sE2yhRlwUyfrWSQGkGVs/wJUjYGsXhmpS8+tak40Ubjs5z4PTVVjoi4EfEJI0cljh4z9pmp06bPmDkrKTlFmZqm'
        b'Sp89J2PuvPkLFi5anMmLAMy0efWARpqAoQTRsIxzCPm5CYcgJ09jMjuEePOJhERe6Pt0bn1CIj82K1jXORZE1gnJPjFEn6ThGXBAGZ/Ix1Eh5D5Cxqk3Ow7sye5+oCRO'
        b'dNHyRxiRYbnnZhW06ZWHIEpCIj8UqzwQBQ+DPBJswxAQl1idgR+Fo2wcvAl2kgQZsCY0WpWWCbeR/cDwqTAAWe9tcAvc8giPPePlsX+K7QIfdui8jOYR+05PX97joIhZ'
        b'V56UJqQCF7JLwHqwhSzVLpPBU8iIoqgl1GDQtgQegNUGxytrGTOebjkeOeFr9SJ+oqd6UH175Yiq9p0jqpL34SDnoz/7U0uiBF9O0sgYEkSTCXYMiVasgmeSUcPrY0WU'
        b'TwIDWmDDZH7D4GfBZXgLbzSFeCPenCkNXAxG/LFnLAu3+8OLLjHxEKXBYC7KshhW6MwWzYrizrt7un5ZsdD0hntsWYeY5PA+rMHbU/6mqwaSz9Yt36/29JUTFy+8DY+B'
        b'dtIWpJzA2mKWdG8ybEBSYZhJsI4aONMrbs3bjck649Y8nJh22u3GfKr4UGIudxn8Hiqy75CpxF+J5PUm2MChLqaE4YyvCpwjKknc2N6UHG/KVrS2XwkVTpFjmPMCohLi'
        b'QXt8HDWY6g12iVQ02Is0y6uE9EATuBWCPl+JB5e5wRQ4DfaLwE4aXEEawmErHgzEtY/DreG+ArLmH9aDQ6Sq5LwwKg7VOHuAaWmoaCqvEvmWyyik78dVlFqn5meMoEjY'
        b'KjyuLAEXA+Exfse78GEkaS8rvwHdmyHZctnQGXz+wZM4smkApS4ovDNiLBpK0uKgcFRGMjgjh+dKhRTXjwYX4KHZJMdQ0RQ0ltSY+yZT/IDiAL6Y2MmT8EL4sCCxKeOP'
        b'2Qn8yw+ihGSXgtmhZZI9eaMpw915e1nzH9CXu8/XzWh+LuX5KZLqX7XH9ycuSB9Q8sLFWQfvXv3h8P0RrYUt9q9m3Fsqn/r3Q/8Uf7t33AvWoRHcf23/KhRMW7o8/AXF'
        b'LdPK1AnLb7w6OzMvdsCLBb2rfhIVte9siQ43vHmteM7W0QN+/dvuy5l5f6qNv1WyO+n6X3/8UPZO8V/2vRxnHzK/YNzs12IvB316tj3+b/O/qy1tvG17p/SZRXC2zbG9'
        b'VLzbfO+tlxct2S4rPbn6p+S+35xaasgd+rdfml/6rv13l98LnZf4weDh9TseLOr3umL7t7mj//nz2pcmCu/ABzv//qXo6NtTDwaZZEJeRdyIzz8izA1zNgpuw74MsfH/'
        b'ae9LwKMqr4bvNvtkshCysIQQIJKQBNlElH0JhECCbAFExyR3EoYkk3BnAgFvXACdGVZBxd2CuFQB2V1wa++11Va/9rN+1TrVLtYNtaV1qS11+c85772zQLC0f//v7/8/'
        b'H3mYe9/3vvty3nPOexZ2m3aoRt8xLMWTsvZ0s36PfnQe0z04rm261nTbnFXA1KL7i0xD4KC2CQCnKc/LqQVMnLdghaH78Ngk/Y68JNWGhGKD9gwJKeTrO7Uj1aT+3Kk/'
        b'IazkJ+n7tL3n7z/tX8ENTeuAU8znBWB08UUXjiAwNP5sMJQm8YwrKvEe0Q24qRuAh8QX8QJpGGeRI0m3oZmsvBIHWMzgR8zZ1K40+rzkBTEBt/4Zg92C8jOOSzYNgnXd'
        b'KJrywNel/H2Zwjgl39c3X1o3bFZZKcpo3zMErc4BMLhw1IUSN5iXtFsH6092IjKm75s+qV8dYhwDuYFjtesaTa3CFMkjNBUe4dHpZRQIMXRVGEGK06JKSplqgf8SnNKW'
        b'PC4bUuVCGlXYzZNsr3EoRkRZNPNtEJkHY0glKg0RaTfEq+IeAUpmeKpUk0L2xv1v4lIjN7TZjKhVobBc8ohoOKFN8hZjOKElXKXnU4k80O4z8QMrt66wobUdSBYmENST'
        b'11yGIIkxS2dHh09RpuB0S0QzW2NSyNcVAsQDiwj61/lijqAP5ZRC6BZ2jV8OrVD+C9OLsu9st7jQwNfw/efxpepObste0TwwiSOCqxDWo4DW+xgn4Tjs9Gr06F3LiBc6'
        b'oOF0HgA41k3aTkk/ZpmagmTGhxTnFZFMQoY5QIbziFOH3qRhnnfjIKMnRREHmfh4gtIAcyvIEqQQVRH9caP70W4R55BKWAax5A0bv0NqcQEnMzPv1prTQ8cvn9TV1lox'
        b'bBIhi/5A84TLiy64YujlV8LvsBJ8ryidtHzSREK+T2JjiXVl8LaAFkRsPGYN+uqVxhUxS7PS3tkRsyDnCB6t7WtgXoiGkGIi1BOzdaBslxKIWWAcIYPdrPbbMPkMtKAI'
        b'ub1m4sOieVMhSqbhATKMyMCExHci4wtIyeeKyTihdhDtxWjRWnaZRBYjL9d32TjogHab9qQaRy9SLjJvp8kAHF7I5hCrZ9SI0oU6MMpg/N3N7wGEUxVkwPpVzovaMYIy'
        b'EX/py3RVgFihq4+KzM6sbqJxoDwxFyaG51bNrmM5OuI5drIcgT4qr+ykb1vO/GYYrJJqYrzztFBYSPMBw0eL9Te0B0L1/la8KfK1+tpgFnyrfa3fsvFi7g7FF0IFTRzk'
        b'7yfGli1tvI6ykoIDXkplM5xN2z9y6bChs8tLiBjWtrAR5rmBgL8cusIyVH9ics+q0egSO3EtD6CIWyb6JPLQyKEXxlvEldaVtmV2iEPPjBhn89lWOmSbGULPjQDGUDHa'
        b'vswpFxm4vkt2b3Qsc8mDjHCa7IGw2/B0IIXtTRY5Xc6APGkpcZlyFsR54jGS3EvOhpj0lFS95RyIyyCFaG5Zpjw4LDbxpPLsWJYlD6FQgTwAQr3kYshjhRYUygMhnE1+'
        b'FXoTnXFBzDUDpsQXCE0Fyi2+6Exe4gITqCY49eROmJMl852KAVKS76ZpP/kN/DvNXwK491Qu4SCtOj6/SZvIS5uSvJcHO+obfa/FSTFhXb+kZlWcmfAsSpDaiWcpEuqw'
        b'PE1GC18DDfgTQdVQfXPP+mAxR0drvT/ghQSxpAb0Tm5APEVKzYJZcxbH1NDaPeYWNBXShJjFi3CftsE59NFwm/w2QYWuy0iuGTOnTEu8UjdNC+5xOaH/pnz27YNOlb2X'
        b'6GYKFRPnHnfEZxyhfNcSYnTzhrffWXhXw7z7qqIstAjKRTKyGoTx3Ko8iJFarME82aKK+ARIz+M9DMTYWK4czkxbB+Wjm2uDxWOvOc0Pj/Glp4WK4dADMleLm1T5I04S'
        b'f/Vpy9Wl3UOCeLoyv+hOoBWVUHCNH07OKVxCTYLMrc+lTB3nIje9AGDg8PWRJfcPRVNci4CKnbzJ9AHAsi4/ZRUm56mJm7kUk0euwFyDNHIhdkEgkDNv2C+mZ2FR+Qpb'
        b'YQl2ApaACEJANkW+sPExZ3yln+PyQPkGfv4sGjQhNjt11WCJ/2QDNyYaqHyNjbFhYfWAwiS1UMH1f46m8fDpdErTep3ZNCjtLFAT55REYDFFJEQ0IrS+V8Iy2SpQW3mz'
        b'reirXDVZlngxEQi21XdACwXebLaVmeo39kLM5mNtOD9VZRGK+Vo0FEw55j6eX5eV3A9WfM+DfCHrhhDvhhDvhpDcDRxynjlTZx2h9qd2w4+WiELm4CPLT5H481W5tkBK'
        b'SUrpR9YZ/WDlp0xHnNuEtE8E2hkRoR+lJkRQChEBYY7Gu6EviAPiHg4JxmISjT2NbKzT/GSGDkjK37BF9fF15fJ6AYvyh3xtXq8JsSq5v2+VUbGhooJkXisZ7tphmeWm'
        b'bNZE4T3P0ZXJS63i2/rGZilQGp/RSmNG4fyjGRWNGZXMtAYfR6pRrLyBnppza2HDgAp9SbMMYxGMj4WYGAsC4ec31XYoLFMyjkFzVDyCk7TqU0cmXtW3+Nk0N9dCk4/a'
        b'08lp93ob2ttbvd6+UuLgzE6tjCUwsPOF8bkwaQzkOxC1Sj7juSZEbnlEX++G0+U2YZu5jiphWN7l4qjhWgDG/kAolo5IuOxrbK03Vb5j9lA7uyY2zwPMpqABHLqaPpsX'
        b'bFV86IZngBSHWe4z9ghLUHlW42khFcYbL9NikYWtEhE+PBNnoIEEBElqHDE6gHp0zJNPzOHramztDPpX+2JpeIZ5gYLEGoOfYtMKoWOB4ISiIrqJhf2RxiMUgxOoFY4F'
        b's2uZ2Kss/Hm7p64p6fBpkGTeNRBHIvWgwDbF9z5mjpMaSG76gcToWonHBclGXMm6RUeHBGse6PI9eP3N53PLhW5Lt1W1qEKLVZFpf1jy0fOPEFzI3pt5fI43vgCMsCIQ'
        b'X+VRrSx+laeO6yqDXSWhTAbUVgBl2rrtULtVtUGNNtWOg6vacjlIrRKhYut2qA7lWZUPHlJRpsMBKcTxXEBSHYilBH+sCsEfy9ALSAu5/bxBqLA7btycpy2DEMUqccTc'
        b'sCeAYvS3yjDdMVuo3Sv7G0Mk2kDnAZwoIVhXDTEHJsQNFCTUkpE5n3LEw6GzxtnYHggyrbwYL+PdCBQa4xuVT/Cr0Cgzo0/VZuZzHKS5UOlQybRuhcwmoiuZAbsMwc1n'
        b'C4wSYm7vJLKikXrYGp0g1BBRYScUubBEqKws4StLcs4UH6befNfsjfL7eOc+4xhFjYQywwwQ/6CTnoaGzhmCywSGFAf+eHhjAVJHknxWnT9HL9mZFbbmVdHYb3bRLrkt'
        b'dsFt8Uged4aUIWVbs61ZtmynXYIYC4l3LNBuLQuia86tc/Wtw1bNLquxcCtG5U+WKrW9+uGFJXwn3oH0XavfntB/QocP5F6VZSqxciNl60J9m1zCLulyyrT11egR9ukM'
        b'loLnXNcI+j79di2aIg2IoILknTxx8KDy2+JUCR9ztdW3+EykREiIzvRwCWzM6MwEkKX+6Td4teeog7uzzMY4tXsFfbN2QAunELsm4Aou5JKI3QxytYeS6EDaAhEpAZnK'
        b'M1tfy5h7dqFJNMhaK1r8gjQ22S2nwdMue+T0jWgxjPUpM+ae3tnWttZo69noMR0tKLvBaBY4cPkkgpJPEJSMowC/InEXJNm8rVT+wBmHqXKKM+gCOBtxUxGtyVbtz2nI'
        b'vIioB+JoE208K4s7kyJCXYXaBI5k5Qvg/7reyb05fyMwTYwKG8Sf88x0AF7CGrIoPp/8upyU6uJJekbLjCtPQjoMys/kaFKNM3tcRgzfQhjm9S5JqjrvjJ7GE/Vc+USa'
        b'QpkHus+NUmaEHwKcVwZHaBCQ+sZmwQQLyONTRuIEJjV3Y1xMysqQXZpAHDFCjVJQwXOz4AjaXJ7Ad+zEb/MQt62nLp0XwkOXx2VmPeeYQJvX2+oLeL1y0hhmn1EhJeiZ'
        b'V4DdCHHNpsQFwQIJT5Rz41j4FTqRVN9Zq5NSnAc6V/ktPSOwvfJbamGoHDbZeebRgZtIGYJzWBw/Ci4g3Dd+Hjj+zoQWQaI55oTaRafVLrrFDAeAepF42PoT2k792WAJ'
        b'gmrtQCgO2HmuQHtyUpek36btyO0Z6qHkoQn1bhFXiiulZRYfExtDBp7kk1baAFkzQmG+iSeIaF9mZyw3gIIMKjqIdeakwbTHsmobVvoaQ2Tlzhilf4A/1MSOZDxb/x53'
        b'KBSfFHFd7tmVnj+TqPn8mURrE6fNeUGhpvOCQrQ8upPWWEEP3TkXDIr7uUfXt2szQpxBdxn0pwQUaItTuZBJABM0ElW6e8AGwlcLfJUN+WB+t5XovWWQwpag+bCcRKeS'
        b'xDGSKDk70Wy0xmPOKqAMupgk7CfmHoh5phCm2BkyZGTjlO8/Atyuk+JcKQHQPA/9R/7UucfMICBdZ+7OUj4Zk2Mo3oDUzXqeLkWxpIBJe9slhoG5RTIkXKE9pT2sH63V'
        b'N82eW4HicZvnzF2VtE2nag9pty6yDdIe13f3vE/7JO1TwkXoZhDwE8NGQayv2XMTKk1Dg5xz2ttbOjvi15IWY7n0im8947iKwGQakqAA56U4ULIwtF0Kre3wKdvx1RFn'
        b'wJ3jMLW2Up3bEjQjUFZF39K6CpahB6W9C+PtOGuzlMOnzeZmATCIzggK9YP6/UmjrO1LgMK8tlX6tqqyCv0xFKzVt1eUo+7/Kqd+Z/G0lAulOBcE+UlwgnPE1+hH+4lH'
        b'amk30Gl7SEJfKYsgzcdFrEjKRjh6t5i8zNNfTSPbJKhH3NgZDLW3+df55MJWoF4L6S5dKRzqCyk+HxoybU8s25JzG1Gl5JegqQey74KKyP7mQLsCdSTYooX1AbkQqWa0'
        b'TFEvy37mQaqw1KB4hpaUFjI6O1U5OakJqVXUt7a2rwmSORmlHr0/oT3VQLlpXaXQwNSDqcXBfqbbRnHJ3DmwcZAIj7mS6iDewz/q52wkzPptkikiZ2dGvOgqF8UkZO2B'
        b'1dpm/ZB+HOCYfnjqJE4/ck2I5Hv0G/SnFqLPdu2+sSyBGOAvmzmwZw/cVyZtNjlxA2VtstDdl2OZSIJMVjj88N7LDgejRDddomyT7UgiyA7ZCSSANem+y77MRkekncCm'
        b'J+Y2dsJcIHaUmsoUoyXxRYhqqzLnh8Ul83eL3VKcLTcY6ADejxKOXDNP1w5IOQjKljgrbqIqGF8A2czngHqQkAGgisEAvlFYyofSkfEA/WCMPaGrnypMRykBC+S0mKmI'
        b'DRGq40wW7UqhCb5s4+MMPStyxofjfiXWXSH+ELqYiGNXnzGnlzjSXlhW7LRABMm0X0EJEUOIuToUX5O/y4tik0QCxoRA8PytaT4qmQp7goDCJwKuFbRyLZG16wxyxecm'
        b'rkH8PotmIkHQmFDBxiXJchzBCcEzERZCs4R3+sgB4gFr7Ra7dqp4C7SJcYDwPj94MXGFJOLnFHQFQoIq4a0/uy6VbVtxqBebHKLdkmyHc1elPLiEaEoABlk3wFRTGTUQ'
        b'7wSAfQumYV+MeIJEqI+zQWAxdVBjHacyw1GumphlAd4JxcQZATkm1aBrb8vi+tZOX894GbsxRP6VLLRYDa9LTIZDUMbhLF2aBJx7EGolW5I/RREEMuZZnjrGje0BgCQh'
        b'AkjBZHERZuITiiQebxyzMHlRFuTzEQwyGE9BcqPHWFF/YxCFTiwx6FsVs7Qrsk9BLmawszVEtERbgsH0bVIMntQW6pLBXeF4t0FPOWFFCQKK6GbDez9UPnPm8ev6fks/'
        b'U24U40zS2RwK5sDGm0ir56JuEbAskvchba4KXGHEbRf3sLl2qiIc2gA5UZYEYzGuLumuRECWcMwK4+WDubZ7m1pRjiNAI2ayRyfhyE7Bn6n8tyNcM+D72wlqUjKuSsgm'
        b'7Rk7x6jorPOUVlSES74rR9FsFXuRh5dVxPKAPbUHxbPhG7tDgK8hehPhbVYIAJEq5MApvJ4nMQsAWXt4wmRhl8CekJGbGcgwYzAN3qbKFvYGMTCiOSa4YnengtfL1lfO'
        b'okBLoH1NIHGQFhYNCRadtl49JIhXq1YlGwfrNGayMgimjKFtwJkIrJhA7pWx/FkbIpbmDaBEEhqhhgI+wiHNSVpSGcbFRA5vFTL4dX1ShzY5awpkwvElbprMJV9f0opB'
        b'PAUxFoG9+YG86CpmckeGPh7CHcxDuoKqVZUI0JcBoJfYjdVKOAaaoKR7BQT35mW6VZnNG0tDmYY/tP/ovgaIcrTjDri2LYnBZDe5x0oeblsH4xdDX5K2Y8+s3mpI/9cE'
        b'vg9jJCJDN4vG6izQbVQt1sAWcPRIiU+LN5y6UJ2K4Z+nw9gE1j8a8j+SwPpzemcMAMLcw2Slb9T3ZCbYrPrhufoWNBxVkKs/oz0jaU8tmn2WjXD8R65m4/hHOhHdJt7B'
        b'DPabWAd+ORPjQOLAwDdIrgYZkmziMmL2Oe2NLZX+Vl/N+6yq30yK4x0pYg4IlCJEkONyCmaHBJmnjccIZoG+0WVmDvIjJRXISa+FuJJW4lDaUK3Oa4/LP53uhY50C+V2'
        b'n2FqH7HH07YhwQqU1cPJout9qz+I6WhXxWz1DUEUKIjZSZ5P9isxG4q1t3eGYhZvG7mcIf+8MZsXUwDunCTnEJMwhbKI74l8wKXgssRXlZuQgyxCEKz8ukxzmM7mbiJI'
        b'c5qjtIUzBTuRtYfqgl2r12ZEcMMBEELAXMcFFhvqt6t5AE88t+5iFTYVAHBRmbge81mVWcQGZOXwLZKyPGSTBRxtiLPLRjkyh+AN9SCWcqsygPyW2FgvgFCdSbtZak5m'
        b'EjRrbO9slWmg6xvJyH8hDtD7d96B/x6etLDEATQdDCUNT8zS1gKDqyyke7TaBUSZxyw+RQGoswQj3fM7A5jc+BJs9fk6DHgXs8EhQ0U1nnMTxySsvbfFlL4lnVSBLCc4'
        b'yZKMRDOAOtTr0uJjj3l6Vmwp4xjTSCmWaT3CauTNMVeKYfwlc/wN7BRPRAt1hS0Niz8Y77BFaYN3g8XUAznbGcCGFFuS2OColrMuPd5QluLb8CiGIybzmZrPzQZHA0M+'
        b'gGJllgQvKCNpRdLHngemNKk2XJIG51lgnGe6OICBMXSgSZxFQrYPpyw2h0apSzSsB90grxeALTJUh1viUgZ2wqdh6rKSGmkkS5FFxv912MzB5vzlmEw/HBwmk4kXp7y5'
        b'nknepo5mqbG1HZC+Zj7OKYpJXl9XYw88YQAtsGMvSp4w55m7mqVBXkctT/rZPR0VNDJYo4Ka+Yoff1rPh19bA4lsFoNMtUsepyfTjTxbG12U+VcXa09ciXaSavVtqw23'
        b'22krRecSfX3KeWAznnS0x5k/KBouAaUZZwChNOYySc4IM7c0YtgatjdZiS3rgHMhk9Gm5FgGL6gccEYwG2l4TZVKlWbFpMp50ytToF0cwUArRyHOQAvoPh/pP3PG4Alt'
        b'iggrJVSeprBFFkJWFjLOBFOJ57Rr3lqsaGTh6iHB02kQMPxvQ9BkIvppOtGyZ0d9sy/mDvpC3g6lXe5sBJTejbm9i2fMX1BVWxNz4TeyBAvQyeX1Gi6qvV4mSO5F7ycm'
        b'epa4TfyWCcS6pyRWeBbJ1sKeT8Nqz6YQz8VXNi5OTmcugFYUttUHyEommoRBENCZWMvMxsSZ+CL2Kt7+WXFoIKzLomakfK6JNwZ5fHFLLpGkOcN9hmbCVYExslYKypUR'
        b'IEfxDQXOgZwUgQSFM30DE0+n924REHUxl0M5aIqFU363lclvEHrJK+sjgCTKlg3C9oxuCQhcmyqYZ9Zl3HxuCSNNUISdBNM/JS2oIUMWzJg3pfBT7CoTV+wCgt9J2HhM'
        b'WNNgLIOYFU77js4QjVbMIne2dQSJsURyjXS5GbOsQZkDg1fJoBiNJ2URmlacv/61cjXetFhMoWrSr7aSXQTENrPonMrm17lo/FnDYo5ZvtbVvpC/sV5BJiSTzsRN02jy'
        b'k9KTZ6SDZ2TQHhSi4mlOEAUn+WoYb9HYSTS+9A5ED6DlIn6J8CELEH+WbA4FTtEYBgv3ZWG7bO12yLZuJ2MMdLtu4rq+hvl2kXDqJ91uQPDd+Vx3mupQXjTTqmkwm8h2'
        b'uFt2dKcFCijshPAJ2QVfzfrtWP+qUGp7VLcKmGYe18Ipv8GyZXcul891vA0leVQPGvKQ01RPiw3fVA+rB96LVDf8evB6wYAcUKbsUW1Ypix2O6AVHtYKygnfURqc1Ynf'
        b'UWRFtqkWNU11wtnvWIm/rpVuOXOrFcpzKiFMhfwq1crgWs1JtDN+Emdi4Umc8/fDOW/85IsFn0+qJKbGaXHChAk0dTHRC3CDX8jIQr4wxk+N2aa1dyp+ADt8FYotB3xr'
        b'vF3ssbYkjYnxO0nwttUf8AUZOGqrV5r9gWCsFwbqO0PtBMa8DQClWmJ2jGxqDwAeq7R3BmR2DYJLIyY1+lpbY9KSee3BmDRnRuXCmLSU3mtmLFlYks7WON3kS1SARAoz'
        b'lmBoLeDBLmyAd4XP37wCimatcWICbys0x2e8A/EKVVgUH7QiZm1gTBJHoLPNSzmYgLCE7xDr6wpR9N/1CO1iYp8k043eDYmG4AxXlG66pMkgfQ/mapIZF3QaRknISInQ'
        b'j3hyVsrBtp1kbDsUzqJNl1TJWewUOqUULnV/0VVWP7pyR0pmtixEOdR9ColEKeHpaUfGywbD8Ec+ao/wslXlc5iYoyTbEJqFLAbn0xoniEXif9oJtjlO95lar6DWdOGo'
        b'9qZxjAFPZhyCnW3Kn3EtDTsfjfLyisLBw4cNScGb4oJnCJRIh8vTDT1gpH6K9hacKnhtYepv9e+R9kHVrYh5mli5dQNoYLHpo8b1pLl1EvVzTkulQ4KltFdqgEp+lTP4'
        b'bagUJJOgeUyEnsY8tLL9QIU3tre2KwYMZ4Wb1NnPU8/hVLXkl+LtRBcu6y0m4wktPJEmIbL8DQhsFEto7LWImKUC4HOgdWt4A9Are3mjmiQOwD9sHirBC2iDkiZY4ryA'
        b'DJtdyvNkD+3sDcGl+sNFQdfIvI5VIifod/ID9fXacRS3ix/6JIcm1tSg9jqKfg72648Mq5k7Xr8tVZm+v34YRdRE0hvW7tI2d/n0E4YKYksHZme+xVtF2hgXLn5g0ksz'
        b'G6Gllf4rN37OB+8ApO6Dj/4yd+Ff63o1Z9/zo43ykcOnLv+e5XigbMrkHZHo9JtWLHE/9tCEtwIv3PnasstXHrjn2PEfjTv1ru1r25e1V7//u0vb0sMvvdz9xe/br9v3'
        b'+oa8hktmfnZs+paPMg9Xf/T8xl3RqvKM7reKHzxWOeej8SP2jo0sLc8Knpj68Wulh2eOjTxzYvLHr/ZveO5XRZ4PclbN+05m+LM+q5a8Hh10+qaLH7nr+RFXuBp++sIl'
        b'a++4+QJ1wAvTf3lqy5/Kf/p41ZzjXz3Y65LbK5/9/bE3H3zp/fyX73x/yQfzxhYvuD4cvPjXf7480DzybSE3t+OVp2tPDh7z6ZGS44Xbxi0f+XHGotwfnXr105GPTl/+'
        b'quuKL2t8Bz+rnrL4/lnf2XnLA6VjHn7pspv0RctbHvrgrVrf0AkL39r7YNnnhdd/9ER964Q9vU4cmzEi0PebEZW372ye0mfsiAG++0qv/nj0mzUPvj1r6sj9ewtbtowu'
        b'uvnIT599dcn3Gn75wn1Ny668oH7hxKc+ObRR+Ov6ewed+ujKQas/rF/6VfqI13cM/t0t71zf+tKgN1w7n7ihd43C1TQP/mz0vjGfLni/fWnL8Ia7//BhNFz81fzPvpyV'
        b'45t84y86o5235Dff1ll77+c/+dB26MZfXha+e+H4z0ove/bTz15SGta88+iceWtf/PGpq+7p/ejjDR+P7H2yI7dvm63vC3/aNbMi2hD+2+jLT+6auPRQsMD386fevMz6'
        b'xSH/Q6PrO8e998HRR/q/kTb/ie0/u+PBN3zv9W87cNUXi5pP+cYfGrFua/eS++56a+oPjnTfWP6j0W+Ef/HYx0MPFp34btHejw/tklb/8cU3K7UPDv7x0dWXHf+wXr9i'
        b'zG3v/nbEvUuuif3xtocP1P9UeevGp+Tjf7v4kFrx9qrIQ69MGFX7sw82fXbgdy+u/uDTt7+5alH1/s8b1azf776j6IuHnvxoxtLTX8x//J2SsX8smTjqzmPRr3LLF427'
        b'6rWf/umGt7w//EnrgoKbv8nyvrHSuvWFq9dtGfX669+749lRBSfeXDNn/NKvT91lV9UN1z3lCT35im/1R38quf79v/z5+d+//MHL/p2nnl3XtertazreGvq++9KW31z6'
        b'adoP5ywc+8i9i9Ttt235/Gdvbm0p9z/8n5+IV77yyexhW29Zd+Di3/sba0e9tr1r7i9b3qua2Xv00W/2XbW4ufbm+sfevf3Ny5qvPfr1lNXzfnvgJy+WnXrngi9bm3e6'
        b'guv4Fz6q9J/Yetfm0ple7tbnfpM26plX7to655booucPjDz9K8/S9w92Vf/gl98Vf/jRY69VXPnXp/cfeelvd7/52MK1zzz32/63ngod33F8QcHhv/y67tMv7woHf3N/'
        b'7BvO//ljX32/oSTN8Jw73o23lWjSqnZOVbm2Sdtu43rr13u1x0X9mE/fQP6k9Dtd+h2YrpbuttW+2jZMl6k9LWo3609rN5OHa6AwD2lhtFNapW0ZPmva/DI9ynFZ2o2i'
        b'dkx7ooFZ8Dw2s4zM3daUl6KTmONrta2CtkvfqZ8gJfVsfasr7iVb21ppOMomL9nuiyiJVbtbv/5MoVL96ESUKrXPI0NKeXpEv4Hd0DpmlZVK+g5kh6Zrz4ne5pIQ2VR9'
        b'VjtaDI0g9U+jJHzH7pE3Zrq81x/Xb8YLfPUSp6TdNz00CtE6bbt2IKn6qrnVZfpW/enLS86++L+22slN0p8MIYo3scr97YIZTu0B26BG/bYQSmhq+/WHewcryBnR9s5E'
        b'bSlV6PdpT2A1a/Q7HdpjLfoRNqf7Fy3pkRl8iX5Y0p7SN1Uyb0DX6/v0vUGX9oS2M35YzNe+A6jfP3Iw/Z1ja+y/sLD/X35Kihjq8P/Ej8nsam2vl71eMseAIhZcvZXM'
        b'GJz/n1P0ODySG/6ynRn2nF7Z2QI/dJ7A98kR+MHlVqF4al6+x5I3WRIEPo+/qHXoajdvt2OoOFPgi+B/QaHAZ1vhv72PU+CzJIHPsSaeHgd7z4JnUT9k++a44X86vmVn'
        b'FPDOdjfi/0KGpU9RNu/ul8E7bW7eLeL3Ao8dnv149+XwO0bgC3l3jbI/zoETkmxE/M+C7uEngfPjoF3Fmbj0fV3J9i4KIUZ76hr9VvPE0TfoB2rnaFE8Szz5Yv+h2iH/'
        b'jS+388EiWGfvfXhV+c6qwC8nZ8x4alzkzgNrd5VfvrN56b0rmmPvuN/o6p/db2PR2G237czdcf2vj7+UeX9fecfedyaXrHYLX11Zd3jTz9OuWXT/oLUXjx548vh7rj2D'
        b'ylxX1E/5wBGe6v1FdtPGx4u/fHTjmF7XVK+96bWZfp/ji6ED1VDJ7o9bdn16y+++J93yzf7vzqt7e1qv/Z/PvuOqh3P+sP3Xuz7ceu+Fy2fPHLX8nZ/l9X61X++5h/54'
        b'79fzohtyZwyZf/il4Kjt40s7e9+a+5NXf938ndWvnX7osTdenn3Xl/NnfjJk4pFdvX+Z+d5fXv7Dp0cG2F1v3nT8xV5Lq9XmoO9H7+6vmvmHpfsi/Wefmr187sr9x4+8'
        b'cmL6F/vHPL/twJgf1Bw4/vyfDxx/93nPov9QXx3Yvm/vH4r03z9wdPHHeeGVV/zg0XueeuGCXd3P5rz2uykj31l35KUfyNsfumTC2kEFQwY9Wvy35VWev1R+89zWEd6l'
        b'NU/4xr27492B37m8YNXrn9z+N61J3Xn3kfaWy99u/viZz8d5nxx5sO9/yJ9sOe46vP+d2J/GPyn7fv3R83U/GnOqeOz46sCTg9aM2Dz1w4o3vT95VSy5940r1wxrP9n2'
        b'h8fnD1Kb3zzw3uH89l8tOPVX/bUdj/zpvUGfD7n39PjTz9827z87fvPjSe98f6aVP/LiwO3CpqGNtt4LL5vWP230K1P79g+9Mm2A6D68ecKWQ9vFLSO+nx2+WBtR07Fp'
        b'1N2NN7peXhUdtvx31sftq77oqhX7PNtU9/XPvC/dMnxix+SHh5d+8Zf0jZ+/fv8Xu0omMOTkPu0pu7GktuibtA365jJjTc0XR+RrD7JT8YFV2vXaddMTWEwyDqM9ru9g'
        b'hsFvWKbdp+9DF70pziv1p/SDzADP09rTM7Ud+hPDtEfLrHBqXs9ftUY7QT70oAkPV2j7GodVl5eiSSh9O3mz21Ktb7ZxAxdYsga3M197e/TdVdoJ/eBZpsoNM+UZ9dSY'
        b'gdrG2dWQRN9Sqt9VgumGWbn0sWKLtmMU85R5j/5cv06Hvnn4LH0rtHQWrx3V7lkTQh6Uvk27vlnNQFN7AicE+InaAwVk5IdvcqMfPrR9XmvhrJMFD2BaR5lfGH3TQH2z'
        b'T9sHNQ0t5zlrlzACaiDrQpdqx1urEXUrqSq/Rl8vcHbtOQHQvSOLmX+jrX0v1Q7q9wH6B7S7oPKTYAwfpU8dHdoWGL/tUOwm/KYd5Rc2+8me2dX6d/R7qgV9t2FDiwxo'
        b'6ev1zSGkZfXrGzz6sTlkuxDydfOV+tEiNgu7te8u69Ie0TfXVvBQ4iZ+pn6d/jAZgZ+vP6Q9C3VF9K0lMA2Zs/RdaMgOcC5EtIaMtkzPq6WFU6yt1/e6ABGtLncO1a67'
        b'BNbOQXQ42gfvzO906DfQJBRcVEFWyGBIKiYMr4JRA3Qzd4U0slV/JITcEl/twmv1vTAHs7Elt/OV41ZQ/DD9plEDa4fpkeE2iP8uX3dRb5qYZm3voHQAfZurcM6Ea/nJ'
        b'+ZMJa63Tb11TjXBxhn5/LUwPUeLXC/oDiMkyB6b3KVZA0QGA1taWVw2bTa5Xsy4VtX3aEe0xKmS8fr+2u5p5fwUk98naGirIc404PVOi+pf11Z6E1lo5foH+aBEHTd8+'
        b'nGZYe6hRP6bv0A4OS3bqqu/W76e5WjRAv/0imOLN2sPMrIfUwGvPLteeZkvxiTX6oWr9kY7yktmQ1bpAyNEf0m8kpH/51Dxaxt+FvbmlqgqQUZd2uwDB41fQ3tQ2wMDv'
        b'0+7VdsJ8JoRqJaAdNogwrw+5qQF1/QPVVWVVHRnlRvtguYo1l8E8ET57IzT+yXL9LkwDbZd47Tv6g/rtNCpThPl12rOsX3Nh3EuqoHD9ZlE74dGizMHm4/pG/dCwKu3A'
        b'0A74Pnw2rNR0fa+oXXfxclqMrVq0pkB7pnrYrCrYaX14bc9V2noat5Xa/dp67T7tuL4Ztz3QK9JlvPaUtt8dQtFnSb9//LDZFo6v1m6VOf32K4awCu9qHg4ru6yuH+RB'
        b'86EwKqqg363dpG1gdsLu0e/U9g5ZAHuO/GFKGbx2p/aIlW2Aw+2l1UD5jBmlH+/NczZ9p2DVH8ii9tTX6rdY9W1xU5umnc0r3IwEu047oZ3oq5p2LuNGLse5KPv8wV3V'
        b'ZIl5SYO5Kz3abnHaQB8Dt8f1jZcyc6KPAoGVavgUaKPHKZVXe0i/HSFzsu3RhOXRJd2hEZCquwM+AEgph01SCpMDexSWwNw5NCJbqsu1R6Tl2mZurrbPpl8PpMsNZOZQ'
        b'26vtW+yaBdRlh765qBoS4pLK1u9G43gPaEfY8N6gPT2dKE1th/Zoxay5FWhO9z5BfzxwLa2mCy9bjqZ2+3fTYYBb7aigH9UfUFn2Y5ap+gE/AMo5+vbqspJymMBeBaJ+'
        b's1vbSB0Ui/RwNW5CtJpcVTZb31k1vAJNP5ZxFv0OffsQgvQNedpx42jaWlsCb3eh4uJWPHhyhkiivlV7klluDMNptAuNMdeGtBtq6dCwQZOOwC7RD2o7qcrKHG0vzDk0'
        b'aTUuM+2uAQCP59i4fP2otFQ/oB8jGIHL6enFHmibfhiKq0WnOJk6HHJ79D1AqNPieXDUmJnNODh0MknlvHZAe7BviMxUPTdVP4JNHm4eYrdh8zHGxvUdLGkb/NoxBp0f'
        b'yVlXrd8/vGpu6VwbZ5UE+2ggXrEJ82GqbmU2e+/UtpRAl8thfPUHYIEsQWj0d8gj3iQd/+9TP/92P/FbY6LEdsMP5xIEO3/mnxPoHCbsgobwJB7TeNgX4y7EoMqYMKDg'
        b'NN4gn4AOl+zk7iA7pUw3lYdp8HLSTTrPdrqwdAtWseta7uy/cVae8cINa6EOsnzQ2eH1Jkgq80LhAJ/cP3xhRMQX7iQigr7FhRfSOLSDycQHgs/DbwMn8yvhL7o4shgF'
        b'yaIXwFOApwBPEZ458JTguSiy2M/B0xlZjHqA0QGYfiWm5MN8eLEp+tbNodhbq9gmRdPbLN18m7VbaLN14/WgTXa02tsc3RK9O1udba5uC727Wt1tad1Wene3etrSu214'
        b'+RjKgNJ7wzMTnr3gmQXPAnj2gifqJlvhOVDlIunwTFfJ2k/UpaJpWj6aAemy4ZkFz97w9MAzB55DUBYbnjZVihbJtmiuLEbz5LRovuyJ9pXTo/3kjGh/ObPbLmd1O+Re'
        b'0T6qKHORfJT3jg6Ss6Mlcu9ohZwTrZVzo3PlvOg8OT86U+4TrZL7RkvlftEyuX90mFwQHSoPiFbKhdGR8sDoJXJRdKI8KDpJHhy9WB4SHS0XR8fIF0QnyEOjk+WS6EVy'
        b'aXS8PCw6Vi6LXiqXR8fJFdFR8vDoCPnCaLU8IjpcHhmdLY+KLpBHR2fJY6Iz5IuiU+Sx0XL54uhl8rjofPmSaE3EuYGLDpYvjU4N5cJbpjw+OkeeEJ0mT4wulCdFL5T5'
        b'6HTVBl8KI4JqVx1NOErZYU84NzwgPLdJkifLU2D+nKoz6iZxlYQlWE84PZwdzoGUeeH8cJ9w33AB5BkYviBcER4evjA8JTwjXBmeFZ4drg4vCC8ML4L1MFCeGi/PHvFE'
        b'7JGSDULUEWYe0lm5bio5I5wZzgr3NkrvD2UXhYeEi8Ml4dJwWXhkeFR4dHhM+KLw2PDF4XHhS8KXhseHJ4QnhieFJ4enhqdDzVXhOeFaqLNCnhav0wJ1WqhOK9THasLy'
        b'i8PDIMfMcFWTS54eT50WFskwfxqkywr3MlpTGB4MLbkAWjINaqgJz2vqJc8w83S7Ih7VRTUUU14X1JJG45kHI9QPcg+i/EMh/7BweXgEtLeSyrksPL8pX66M1y5CW0Uq'
        b'SbrGifPY7Y4MibgjpRG36o5UbRA2oIgBxpRRTBmLucatukgYaybzAEDy/EzXHCFEz4JoeHgylakI1+JQ+oTQAgi3kjfFtw2N4tO9hwSHlhT6mUxofWFDp7815A+UCEo9'
        b'Qp1BScfOuaxVeZsCxARDabP7LHF7Hnh5rBw0tVBKJABxzb5Qk4J6D3ZfVyMJzZDGOV6JtzfF3KbQEAkL8WiLpA1gIrw50Rp2W4fiCwYhJLa2N6NeMgqTKU9D2Sex0yfJ'
        b'EDi262QX/tyNP6THgvLQ7bIPICuZg0Ap8pjY0d4Rc0Lpsq+pHjUT7E1edu/KjAAlzEXEoXHM2kTlxFyN7d56pZk8YqIrT2/LmvZA69p4lBOiAqywmBveg6F6w6imHUJN'
        b'rfXNwZgN3qgwB70EgqEgfSXZd6phdb2SCKCILYYoH714KFYJksBDoJ3KaYUprG9gGRSfbzUaPccAyjNQwNLY6qtXYlbysDIiJjb4m0luHM3SMI8YMSd6TWbvTMjnuDHJ'
        b'IaW+0YcOFr1eSN7gZRNpgzcUUIhJXsXXFPN4ZX+wvqHV522sb1zBpIJhYcjMVhpehZwWhpak+MHDG1JEvcgrCGr7bTAM2aNdJ7S42s135ZBBSA+ZlOQB6gPBu6pfHTOy'
        b'tTGu2nuWbujfs9WEi/PLuIwZ4QFOc9HG24jCZFazjc/Dl4gNYJwbtlU+tkPlAfoITagpUSCTbxvSnxAjhSTkJalSxNliV9ZH3N0WVYi4WgRlFrxbA0MpxClXRtwurtsS'
        b'4ZhQWMQZyYIvHui7OxfHwhqxQbj/BkG1RnpDjUJgvyooOyGuIJLThBZtdqFwF9TTC+p5lFLnQe5+WFrgOogfEMmkdB9GMgHi2LoKSb0sr9sOaW2RbEgrwTkBo70B9Vh+'
        b'COMqwfnBU5nWFvtNvFIRsUJOR1cFld4XUpo2cJxQipFbdcCbE9/II5AdynEs4Ng4RHgq50bInR5JcxmKbqoYyaCvaXlojReIPJlTXfhNFQDipuVyTP+KjIk6mKuAuPAc'
        b'jSuU+SDMhzPSB+oXcHxUSzbqoOSx8YDvz1Kbc80RUVPVwd3/W9cVA/8NOMz/EBMaV7YVVnOwhkC0h+GqhK2ihI9VsJPsTxZaLxWZnJCbcOE8wmetfA7fh5dEj+ARMvh+'
        b'mE90QhzsGiG+YTKNE4g2zH8JxobxwDSXGBsmO3nDwFcRJy4iwSl1YcoWwokbBnkkesPFb1Gl4MfkLt4awb8cmHAR5fBUm7JetZE6jV2F2tjCgS3TZzwXWBHpGxkUKYaN'
        b'kN9kgWX8ouqA5Tuv2xlBCTYnlOtSnZG+sDV/Acsu3cXl48EswrsH31U3bT4oSXUBiphuLF8XpmDfVOd4btWuOi4QiAyOpEX6ynxkEPwvhv8DIkOb+Egm1hQZgFssG5BM'
        b'iO8T4SMZkQxEzvw22uQWXMSwnTJVO/QoDRY8PFXYGhFPHtftiWQBSoAxnlwOtk0aoQouyFVGDru6qAR4b4Jeb+O7LYGPIcYaKYUy09X0SB59B8AA7U2PFFKo0AgNptBg'
        b'IzSEQkOMUAGFCoxQH7OdFOpLob5GaBCFBhmhYgoVG6F+FOpnhIooVGSE+lOovxEaSKGBRmhAfNwwlE+hfAw1pcMhUY4IvsptQ/CJQAD6GrkgkgY9zlAzbhKCj6gS/drw'
        b'l9ZLLq4XKAPGvgmNeRu9yeVQ0Q/GsxeuMyhVJBMNEo48AnGKH6ZKGK9Kpo5+XG6oJPP/yL4tqfg3gB3//fBpEsKn9Qn4hDKIgt2wVW0VPcxtmiTw7M9KTmpQuzgbUmZb'
        b'TZfJaOM6Q0KdY7S/5RayRCdALQ9/rr8swS1m8FkiOlbuI7pFpOnjMM3UzCKYxgxPAtQCcjliN2CaNcIlwTQxYqHDHJCViAMQfYBlTKI75fDpET/5F3gKoGE8YDWV9Nkw'
        b'ijgQKR1ymB1CkxsRCTYFYh0CgOEs1okNJMCpFKNweSQDrWxSvKRSSuheWgT9hOBGSgeglIZgGkMoph5xbi/msVRXJAs3HQ4UASzRAiA14hgLyN/4JAF1AG4AJgGY49bD'
        b'9wzIQQLX6CiI8nLnMXi9/nvX6tPWJIUqSUCtJMnm5PuJqI/DVpEzsYqcyYOOaiyAOiJTA9ZJfNAlY9CH0qD3BsRLDJbRFwznYJjM2E+HleVGpVz65tzeh4YNldVteaQl'
        b'gKGUAQakLWKDcwtQUjgvmlQxuMlEp3ksXQL0EM7PrkrVosTQ/SNCSziZLHCKwBR229Y6ka1AGnXZEhfiWpzKy8xgDXNjSXnysAw8C4nQ9gDR3yucHc5tshkOZuyJmgBt'
        b'hF0CbekTScM4Mz872QBncMCOorZ2jVct8JTjNTiQsUF5F0NeiIMvjnjeeDsADS2tM5W+xJqzlGri9nDjThOR7oAuwyCTiwY044A+cdByZHsZ4p6kib8xYaxKjAmhBkVD'
        b'SvEl/h82pxHz+IPe9oYm7xoFxaoVuy2u8SKR5LWTUSNAgiM5/k/54cj/dwLub1oNNSZzw2TAr5vAPIqbZwEYt0oSqfajYAzqJiJJZnV4xDwbxmbZPAarNosvyWP8BZL/'
        b'RWWUmBhcG1QOYdxh/DmCP0fJSkEj2s8JKsdIwH9dq79BOU6vbfWhFcpjpBENL7569JegPE5qK35ZKaBCgfaOifUNQLWvqA+i3nTMZtiAitmC5ktza3sDUPwlaf+aISup'
        b'+zfgqf/Pzz9zCYFr8mZkK8RwnQuCdOYFhMeSR1cGeD1w9gUF+5N6+HP3GPvP/1mN//Gw1S1m2SRxzhjYgWLTSvwtdEvihf3wbfw03JeC3UrkoSBQP2tQIQZN5MQyEkp/'
        b'yL/zeo0d2VbfAdsypCghnmnWkn0AdvdxkPbdjK5GXweaSFLwQhpvQhrrO4M+rzeW7fUGOzuI74dMMlQ5gViXNxFQXk8185Ckhjq+rV3ubPVNpCsQlByVBMAIBUCEerqP'
        b'uZbrZcQXCWTB1pTO+18hCwab'
    ))))
