
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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAlclOe19zs7MIiIGyqSMXEbBEREokajiCDIpuIeDQwwwCibs2A0roAOOwKyqijiBrIIKG6g7Tlp2rRpvzRtmlzuTdPcNM1tmrZJb9P25vam33meZ0BQ0uR+X3+/'
        b'e+E3M8z7bOc56/+c5335QBrxI6fXanpZVtBbirRTSpN2ylJkKfICaafcqNijTFHky7KfTlEaVfnSXrXF/wW5UZ2iypflyYwaozxfJpNS1PGSc4Fe80WqS+SakFhdZnaK'
        b'LcOoy07VWdONug0HrOnZWbpwU5bVmJyuyzEk7zWkGf1dXDanmyxDfVOMqaYso0WXastKtpqysyw6a7YuOd2YvFdnyErRJZuNBqtRx2a3+Lskezlof4peM+mlZfSn0Jtd'
        b'ssvscrvCrrSr7Gq7xu5kd7a72LV2V/s4u5t9vN3dPsHuYZ9on2SfbJ9in2r3tE+zT7fPsHulzuR7djo8s1DKlw57H1QfmpkvxUuHvPMlmXRk5hHv7cQd2meaXhGbPJJ5'
        b'k+k1kRGg5AyMl/QusRlO9Hees1yia+5pzomu2zKPSLbZdBHvmaAfS7AoLnojFmJZnBEG9FgWuWWDn1qaF6bEh/s8bUuoo58e7lG/cqxYQJ2xPCIGy7fSiJKFGyN8o7AU'
        b'SyOjsThSJeVCRSKecN4FZ/EBXzdonUZylaSlx30Tow2pmZJtN1v3PnSmYq/zuI0RNGtp5JYI6JiPhb7rY7Ay3gmLIrbQ3KMXmx8RjeWx0XFb5lND4UIicmPE+i3zF+z2'
        b'i4j0lUGbUrJC0eTg9dieLHPwQ0EvtyF+hH+NQFLdHCyXFcqJ5XJiuYyzXM5ZLjsiH4vlzvSKf4LlDYLlP7PwrbsHhM/LbA17TuIX3/HgcpACUvP831+5QVzUujtL7nQt'
        b'YErJnvjkPeKiPlQl0acuILdth/NquuhCF2dN9VT+0aMwyEV6f94f5H2LVk2LlTIYFUuketkNjZTTEp0Y+C/myRPjxeX/nPTv40+Pl0X8JOEXsi89ZyztlwYlmy8Xgddk'
        b'4j0JcP58LF4YsW6aHxZD6+b5JIMKX/9Iv/UxMilrvPNKbNPY2PbcD2GRxVUW+DyNrZegNhxKbZPYtvEktljMKuzQUUuJBIUr5bap1ACnD2OVxazBIuygljIJirEJL/G2'
        b'DCzGdgv2SdiM16nxlASlcGmXGHcDT8MVC5Qr4TqxD5slOAdXDbwtBC7iLWqSQz/0UNtFCZrgYo5tCht3ey2esuxT4b1Iaqmg5eAEFtiYRejXbLNgtxrLsICaaiQ4hb1L'
        b'+SB8ALWRFpuKaOulb5USlEDxeL7hHKhPs4xTH32Rrp+XoAGqI/iG8aRTmAV7lXtJHljH5sp7ljeoZkOzBUoluONNLWclaNztzmearcUui1a+jnpLeIGmWprCyYIWzWHL'
        b'fgXe8KHrtRKU4w04wUdkYOc8y3gJOsaJEfVHvQW5PVmzsHeckjiSR986JDifCh189SxfvKg1q6BsPTVcpyHRWMJXmR4ANVDiKgM73JNkThJ0rqVV2Gx7cWCFBXtk0AoX'
        b'aFCVBBWbwc6b4rFLwl6bAh7CbcHn09jvyxfyhjNwWYs3VIvTqKWLJGA2cqJ3YmO6Zb/cY7mYqxhurOIE4HU3OG7B28qYQ/SlQYLK/XCBj8A+bB1vGS+POyDWaMzMESy+'
        b'FgLnsddJvmEpfbkkwZmlkZysHXgLH1CD6gUVNVxl0n8AzbxJDZUzsdeqwnNQIpapgAIPoVFl47EHe13VcHONGHYOL2ORaOuGKvIovcSfG/vZyjSnhN28bRu0r8Ze7FZi'
        b'zcvU1EJajwN4WUjiFjQ6kwuT4d1E+tYpQTNURgqx3tg1mVpUWLdbMOgiluv4fg0rM6hBIdtO12+Q+FfDGT7C5wXoJm6rN68TulaJ3dDJl4nBnnUkcCIuTYy5CK14gTNJ'
        b'oZ9IxPXKSLbU1EZMCpnKx6yb6ssaNNi+QuhIE9RCAx/junsGSU4GDzBfEH1u4VpOGfTgPZ3WSfbyDCYVCS6rNGKbbeQkGrXYo5l4hG2aCIinuXhTA6l+lTZXtRWLxDoN'
        b'R6GFM05J6/dpsU+ZBjXU1M0suAHzOQlQNW8hNalj4S419ZIGy4I5EwxKPEkNKihwrNQM9U/bPLj8gg9arLIjW+l6oQQnAwSfJ2EzdGotSijFK4LR9U9N4rsxEWe0Lupt'
        b'jMq7ElxRQr2NhWa4jJfhJJQE4ym4BaUqCbqgWoEXZXFbsdY2g3U/tm4xlOSSByqDYmrvg8vKdBkchzZPmzdrvxA729EeyCfJ38zmcYYy+dSpPnqFbQKLBlirNR3BEgpA'
        b'2VL2UmzmV1NJdx5OtUaR90+SkrA+XuzNjmdIl2pXR6lZ9EhZr7LNY+ucNqRhNRbCdbKjumBoVRlioAwv7QmFlp0xUpBFBTUb8a7Nh03RQWSWid7B0Ik1eJr/GQTXsUYp'
        b'eUVS7C5TOuN1I++Ox7B8oWPuPrjGukdA53DvOLwIA0oFTXrMNp9Tcpjmc0zeMWLydt49Fh9ilVLtFm/Ts85n4SwZSXUEtBPNw50D2TLUGW5G+SnwTjCJg1NSinkRw3Sr'
        b'DFPwBm0S+vdodVgC17ZOlNbrNFq8iBW2hWyf16D78KhtRkCj+NaFZeyjja3iZ1bto+F1YkzHdIo/Q/SUKZLEAtCCjcRMKNkZg33QLUXgHTXeSozkqGhaJoW0kVu4q2IM'
        b'Um6SZmAveWt8SC73WTb52bTnRzCSk9ARSmJ+xKRrMWya9hh1Uoy0D7qc4O5ELY+/4RlBbI1OxxrE2QIsVJAvKsIaOJlKmtUoLcLzKiiPO8iZtRF6adMj5SCkxvfshdfh'
        b'DlPlfrxiE5KoxLuGsXSilfdXxqJdqcEOB2vxBLm3R73LHluDaQZenS4FvayCBgP22QIYtCJFahwa80jW1LlMbJ0NalojBWKFCi54HOVkUSCHotHKN8QpTldmFnYonaAg'
        b'zebHImrcqlELBD3vGNguSOQq6EeGaoGbcps/QylwH68NjWljYyYBuZLKA4yrcFIHF0mrYnBAE0hq3sIXicVqGBhehtsZaQjm75wfzIkig5AscN4JS3NJ7lypqqEocmjE'
        b'dbbIIuLeSEV0EFZLhJ0PsC1gYwawaXhMx7A1h+poddL0+IlSHDZp/MkkCvlGsOHpFY/0Fq6r8IRjrUe8U0r+cF+1Jw1vcJ/h8iwZuhjS9oQTgF68OE+B98MPcqteNQk7'
        b'R+q4kHMH6zoDb+IF7FMghaRcLmm4RzJ78Jh6tI5WDw/olIL2qYCgYQmnBgbgGE0xQsfZX0OeYM0WhQK7Ain+MWpm4p05Q9N3PaETBoodLUrNM9AtrK4O6uH0WNSwK3gV'
        b'moKV0OMaE7IWOuZKZqxxwlOU5tjm0tgoaGHuadjjCFmH6lRS0ETyeBdUcN4MNWLTJ13x+kgJjDYjZnabKeouxjMqqII+P9siNqiQRPDgkc6WDashv6IgusZRn549S2Qb'
        b'VZqlB6dw096RGBDF3QR1fEw/mLeXQ760Cco0s44EchvKdMX6ES4NO+BK0lB3cmjSYrhFbmMbVnE5BM4irPOYpAOF15iBpcTibhLEPB1nD9Z7rh7lMwgN5zl8nxfkkfqQ'
        b'6p/jXbWWpFGmOVK4WD0V7Aq8F55re4ZLtwiqR5JgXMd6y5k/vU1qBmfDRTgogma8+qRWdgpae+LwBpFKMbyPKw10T1zrUK+2oc5w00GCHu+Tgt0kcTfaAhkER8bcMdxh'
        b'56PIQTnJQ/K5jSpo8iR94ZbeifWxj4WcTq6Yw6Og8wVp0TYVYaETk7hnh0aCV6dHmzpTsiFTp6GN0oZozbJNUMVNfSe0TB2taB2P7eepNBLqQxVUYHs817NcyH9+1BB5'
        b'Ml8FW6B7T6g7LXQneAIULpHBmdUusbuxRcSEvhVw9YngPGRmUIcFegXehocOq78NZ/DEKCFTCLo80sk7/JxNlQOd0QK3nPUe/6QEuQua4UyR/K4Ce7LxvFB77KcVxooF'
        b'Dpd1yRMfKt2gK4lrHPSuNz6pyO1COS7twk4Fdj69XWCWyuzDT3j0YQEEe0obfDXPwn0/zhXPsBdGBYxRekSmx1T5IQvqtsVs6otY5zoW62FgH9lf706WZO7Blp2SeS9F'
        b'e8LrV0S+3bQDGkdpUvzcod2qPBzhvp0CZRi0cRGvppTl2Kh4Pw8rRmMNAXegWmWla/c4eTR1K1wZO+4/UvRjcJFWayZvd8Sh6FiSiscfseEJd9ep2rdkHnbKNjhpgqHf'
        b'XahTCdpTR1GYiwOce+2qJOJEjBQ4VQWlwRauGUv3R48KmQ42CxT5MiUTPUqlHykqk58tAgvH2gOPT15myg2LCSRUzuB6MRfb542h1EKHJhx6ToEDckLKTKXxEuQ9Ch2j'
        b'TWCYO7pg4k21Cs5Kzvponk4cwRMJlH9M40kTS0DM03kqs54C0wMLpZyF85j3Ik0J8uCZyaEJUGDBmzICz6K4Ue6Dp3mLE970trjKKD+64KijYNNEnjPFkq3lWaBUDpf2'
        b'MXUhdEmR7rhItY5Rzl1lMSs3Ez5FuwQFZIdtnDYr3NdZzCozlDmqL9NDOG1xFBA6LWZNoJ+j9jIbr/EB69PUlPNTFpxJDeUUrZ9Xi/LJFQJODRYXeTSpIietZh42iIT2'
        b'3uyNFihW7sY8kZ+e3Qy3RfZ8DYqgghVygrHRUcfBG+tFEt8aBtUWN/k0vElfGmmrEY5CTcWqaF7eKZ/sKO8gZahizE13fMjqO2nbHdUd5XOc6kWbFJZ9qrmca6y0g8cU'
        b'gjNNeCuS1XY27Riq7DAIzKk+tvEotWj27hLlgNPkbPIF1bexC0+yqs9V4rOo+ligWpQkisNmWMappQWOqg8W+Q0lwtcSWNkH77/sqPvsxWN8oTV79lpYup3PazLnmEzv'
        b'xjkKPFAYZ9HK/ZY5Cj9ox1aR9l1PlFn2y5+WHLWSDS8J1nQGwWnLfhWD1mI/ZVBiEFUUeyCcYlWU6FBHFcWE7bzlsCeyBpkFHoq60+nppBysxUaot9oyXg7Xgh0FFmxZ'
        b'zFtiKR52WMbLIC9LVFjOpkKh2GgfC7O9TnK8AhWO6kvQfC4dOVRYWfElRTtUfBlYwmcLOwyFrPYSrRmqvORjtc2TC/SgJyn7TRlWwHXBhFpshzzBngoff+x1Ve4nlZbw'
        b'Mi0ElclcCvIYidVrlnGLY/WabVsEcdVwT8eKNUqsdRRrrHBXsO7yM/NppR6NEarEbI1PYyWn238tQaBeNw2WxYs6QYv/ND4mCvrk2EvqRgnfHVZdIyt4br1Y6TL0bcTe'
        b'fXK4sEVwtQLvHuJ7gv7NeIua1CzaComfgnzo4rqFJ6Bmjiga3To6VDRqXiJILJiC91jNSA0nHDWjxZSncpVs8yaEzopGV3mVkFWNDkElZ9MEfODDykZkbPcdhaMDk/ko'
        b'HTSRuvfa1GDfO1Q5uocOQirIwXVQowy7wwTnqzLgPGdItA+epxaVgaTLLbDazdk2jZFRgxemEvW31OQZTwneN1DULxFTnoHmZOwdRy6KuxvawAXo8BT8asSzHqxSJePV'
        b'IF6pqkrk9HvPCaUGFTwYL2pBDIJf54OOwtUFooZ1FascRaxNaZzJq/EaXOJlrJVYNlzGwhOc/u0E1Rq0eEM91V00nZ0/URSXukM9WYFrYYyjvIUN+4WqXcyBeq2TOpbb'
        b'FWWEl9KxQFS+Wpfv0jrJNm10FL48SCLcEZx4NlFrVUYQC7g2VU8V1bXtFEK6WUEMyhMcFTG8s1uYaDtWmbUuanLXRY7Kk9oiuPNQs0ebq6StMyNoZXy+RRbCPUHvjKXa'
        b'XLWMyGdl27pNVqErVcTANm2uKspRxKNQAw0OMWzEYlZdW4vHhqprF/CMsLcC6IEeVl8jGDrgKLBh6RzhKKB+Ka+wXeNFd1ZiOyBaNhBzb2rdZC/x3faTX19HjopxVJsK'
        b'x7RuBOYp4uMD0lO4mSkIvAbtci12y1ygXbCuOR2uCQLrqLGM2hRZdF0i04KWZRTauSAuKJdpneW0GcdKV7E2Tfj+Gjg3X2tTaqFZ7LguZQVv8DiE57QW5WKuIqzKl4t2'
        b'MVdBDNZoLRq8s1psp4lSA07cbhg4CiWkIF5QSk0DJG+47mMLFireFkNt1VDoKPNBhwP5QSEvDCrxjCf0boaSLdK23WqylE7s1itt02nwLmhJwJLo9YQurmOpQlLgA4LY'
        b'ZCJ2rjOT4GRaFBZHqzeGS/IXZQt3QzuvO9Lkl6AzitXdyqBj2wI9O69ydVdMxhJKp/hWTkDhxAWxfrM3Rygl5WoZEXQqMjyZnRSxHzW92PEPP2diZ6N2iR9hseMsdoyl'
        b'sDunOjsOsJSFynzpsOqg+pCSH2Cp+AGW8ohqu5SiiJecU/XK9z+V03y6ET+h7HTTojNk8WNNXWq2WZdryDClmKwH/Ed1HPUlUhyq+uzNzrJm8wNSn6EjVZ2JZss1mDIM'
        b'SRlGXz7hOqM507GAhY0bNVWSIWuvLjk7xciPWNmsfD6LLXPo6NaQnJxty7LqsmyZSUazzmB2dDGm6AyWUXPtN2Zk+LuMurQ8x2A2ZOpMtMxy3eZ0cXrLjnWThmfxH2tA'
        b'kil5OdtmminXmOUrRjEC10SGjqLAlPXEjthPMjHG+JKVbcFoSE7XZVMn85gL8b2ZD4xczDpEJrHym69jZQfZjtn8dTE2i5XtkfE9Ps5v8aLgYF1I9IaIEF3gGJOkGMek'
        b'zWLMMXDCfNhfPjojqYbNYDXyc/HExM1mmzExcRS9T87toF9wnKuWYy+6eFNWWoZRF2YzZ+s2GA5kGrOsFl2I2Wh4jBaz0WozZ1mWD6+oy84aVlJfuhpuyLDwy4zJ+02W'
        b'xzYz6pzcU3r80FYXGy6c+PldUEZYk2zy4VGBNU/k8gPZgd3TJJZF3N6b6PXz3TZJhI9KbJkJJZKeQdMdlNPe9eOd/+Silch5bVjimeiK89aII92rh9wkL4pt055LdN33'
        b'9HoxwyyscCeMKEmGTI4R4c4aQci5p+CMZb9CkhZQas6OB6F4mwgZVw/ILRRMpZh1/HDQy48PkGGegh0OStLGAH40SAiuj7c8h7UarZm2lIZn+NkgZT2nRJQ7s5hiSQ4t'
        b'4vkUg1N14TY+Yg+lD23afXSdAEUFC+dnUmOEp3qwB2rZeaIkS9/GThMpb7zAne4m6MEW7LWoWQ1kN4MVVfvhpoA39dBHyQX2yFj1NIEfNYY4UCD2Rwexo0ZW4u4RJ42X'
        b'vQXeXAv57KCRxpwJ5ieNYYkinOZBKwVhxhtskLPY04SFB/lsvsG+2Mu2iuWEf86whOB+pogvdYrJlv2EUGVEcx3LQog7HDRcicB8AuOsStTJ0XisnDNntxTJED+Lbls5'
        b'4s9W8jVm0wQ97KRXkjR4k5/0Lp/MBexn5Uf+0neeSYyO254gBKxNPLQ4QMmYkAvVUhJ0wkn9eLGPi1A3nsuecq8rXPqZWCjW8IR2Lnw8cUAIvxuLxaCazXCeix/ak7n8'
        b'CeoV8ZUWhyYJBfDAAq4BEUv59bVYli3kb+bi307ZKI/hzdC/kks/CKu4+DGfoBlXjLaQF7n81fO59OFSHGfWfry2QEifAmMjk3+AmYs4EwdYEsCkTzjoJBf/YXwgxN9F'
        b'bOoQ4l9MeImJH/O9Hcf2O+YJ8WODSoj/JDQKVavBU8uEAsxZweUfAjcceRI2ZXP5wwCUCwVoWCua+uezyjXb7TICOkwDFHhJaFplNCWrTAVCfLkGwGWo1yuEdlREQgdX'
        b'AuzXCCVYIAbdT4wT00FpEJ8OKncKQXRAw8t8OuL2LT4hHl+td9z90Io9rAjA1AeuHOXqs4A0ng8swz7Ky7gCTY3m+uMEpabMFf8ms4wjFk18/1zMqW+vVy5yPVl95dyO'
        b'lYXz7D/+8bxPP5lYuG7hB3Mtb/zEu/ZbMKn21krn+7pJs14+Y3c/v+aQ+1PfvhowLu/NqC8Om77c8NmBby/N+4uzi1f/6oMTbkyffanGnLItoKOpa3Z07KGQz1955cGd'
        b'iF93Pjhy7GrH21++9t0Pbq69dvUP6945W/gn7eS627WhOz6y/OJXb32eo2ueVr0panbU3iW/3V24MOnMzz8+88OOzxZ/eP77mg+ferWrbL8qLSJhj3/y9bdu3/3Jx0Hb'
        b'dgc/3TF33Jqewq073v40aqXiz7aWv/2p4mcrv9Nwd9EHBQfr1/xX2cpPEl89lL0i/bub/tbc+upcpfpM1O6Bz70+7shfub4X8w55v+vk+oxXx1Hp3ubkeckf6DVWlplg'
        b'rRpaF/jNj/CTk9UUS4Rv5X4k9W6rFwfr+tkL/CN9ffT+WOHLMhBPKNypU75IeNPKz22v4C3oi4rzg6I4AmjkFbrVknajnLxEGeWQM3juAHewnt0N5ePnL3PB27RGnnwx'
        b'+f9iKytgqSGf8hjHbUn72W1JwXuxPNfPB4sXyiV/GFDhTVestzLpe02CW1gS4xuJ5aTwFZI6SO7mgtVWVg4PpkTvXJS4rYl0tyJ6PUOSk+Emeb8CBd7Bkul6+aB8vt7M'
        b'YpPemX9807dW6YvJK1LN2QeNWbpUcZObPwM9zw+68BCcwL6wAGjZzkLhUUmvlCllTvzlJpPLptCnO71cZOy6q0zN/5bTp5o+nejdlT7Zu5L6qWWevBfr7UbflKyX3Etm'
        b'JpuQYpnNSHr1oJKtOaggKDWocQCTQSVDEoOahASzLSshYVCbkJCcYTRk2XISEvTqv79FvdLM7mwyMzxsZk7XzO64MzOIzNetZbtzZ7s7Jn3iJVcz6vm7bRZzhV7QxZgP'
        b'x7BrtAA4811fJn/AtGHK7uwouo4lsVgehw0zI1WSW45iKTm5CnEjwCmogQtR0dSM+ZBPwH6BTNLulFMEsUOpMPPrszfxbAAv4kmeD2APnktWOGCIaiSmD5SGb09Tpiod'
        b'SF5RqCAkryQkr+BIXsmRvOKI0oHkCwjJvyN7HMnzuxNHQHlzdqbOMAS+R8Ps0ZD6Mci8+e8ge7Nxn81kFngux2gmdJ8pgOfQLZOjoVfcECIjQnw20YqmTGOY2Zxt9uGT'
        b'GaglZWzAzuhl5ArQ/vgmxkSrjk2JEY/vcKwlGMQPzzCk6Uwi0UjONpuNlpzsrBRCphzpW9KzbRkpDLkKEMpTDkeaMTZGDTOxLT+CxJT+GHSBflZbDkFdB/DlXCPEPp/1'
        b'8GUL6f8OYlU+gVhVsbbn6G93vE7p7Bg3ZxZF+6z3hbbN4j5NdkGzLC46MkYmwXUo0i57YedmU/trR2SWlTTLupLi3yT6/0pviDBkpGYkfZL4I3p9khhh2JNabmgzXjN+'
        b'ktj1ts+bbYZrhuhkl9RrBqfUX2TIpFm/1WbeeKiXc8+2GtrhstaHTAGLsDTG5nCNuVD4FPQqscuAlVZW8YQCCvHFUf7ryUESzmwkn+cwwulwU5m1mfCRfJS9j+UKVENG'
        b'P6gVN+Q+cm1uwrWlMKfmwV2befwjh6QadBrSqkGNQz+ER2HIzTyO9Rm5vMLM7t4xM48iunFPwyZ8e4Snue7xuKeZCvewbmiT66B91B7hJuEslsivx7qZT1QjWrEGWCGn'
        b'FC74KvDylt1RQVC+DzrgCgy4SElYNQ7P4dnZDjCxK0Sb6yZbhXbCZLXkdQhBVfKmLXA7Xpu7TwaXNlBToYRnSS7i1j9snYyVFuwbj/d8A5WSHKtkU3wFuIarUAf3LIFm'
        b'+UtukiybnQM2YavAQnWYp9fm5qrH59KEJyRsXAoDekclvucwNAt31xQivF0LnLWx6DwLuic7ih/HsWBE9aML74kl8/fAzQXkSmWZ0CPJoVwWCgNTx/aUy5mnVHBfKW7i'
        b'ldudUp2GPabyaz3mf31V7YOb+ujKx1f6C+ZbWPevryB8RWLPBv+P5/XJGZwsi9H6ZCb/GIGML9nJyTZyjVnJTxI6lMuHbQjRhVIkNzPXuZZCRLI120zZeY4tKcNkSaeJ'
        b'kg7wng5XHkrZvtmQ8cR8a8hC/UfQZmBCsfHb+H3iQzf7+NLH2rXsIzRu0yL6JPJ81gSu4Q2hoT6+T8w4Yk+GDEv2mBUJtknO5xxRh6BZU5gXP5DzGAPZzzeKj8MzZuc8'
        b'GRbZzzcLjaOE9w8rhLAb5bVPhBWP2HAbM7IdgZR/faOw8iiohHlol80ME/e0z/WUXlpokKTExF3fCjgoCiDPRXhIN8Mj6a/EQ4fCQySRetVnurF7dqUd5CDuSzsoKzsp'
        b'XMqNuU9DCRRCIbmIIrN8osx5Cx7nE/0xeLz0+sFVkhSQ6IuGVZKoixxPU7JD8EVLoEtaBKV4V5Ro6igxLV1MGwzcC5ekQNoXn6N7trsU4LJaknISXXcF2iQbc+UroSUA'
        b'ewlHbpgYJW3Ym8F7LnPSSl7evhRrE6OzlxulzZTksaDgCaXufMFgvEkLFkwSZJSQJy/m64XhXSlw3UxH9xTsX8i749U59NZ5SJDXCe0GsSSUzqS3O8+ZdoVWyy3d1Gi9'
        b'smRO+SI3CHAN++3smAs+RsOvX91xZ43G87nta9ZfcnPTeviujfiVfKVaofl1Q8TOAwf+dvTwb7SvjjOMz/P2OLTBd3zSv3528pLHg09/XvzZ+oD3J/4owNv1X6zX/qNg'
        b'Q2fQQt3O9juXXnrp2LNJh2t0Bq/ah7/INH1338YthjdDPpsdcUXRtvVP5Rmgfmnn26d+sGNGxl/TL6d2Lv59/ofvVembet8+9fJ1/+s9z6U3RYXf9+57e9Wszxefd/9n'
        b'vZOVRYqVWrwjsjWWqS3YKvfLxhorf+akHSpjngQJZjwlQALegQLrHOpowLJnWEygjM1rEUvcFlJHPzYoSkPcu6COxBsbeXIHA4S5a7RRWKofnm+892SwK53A/gKnB+qh'
        b'Gq5S/ieT8E66PFcWAo0TRWLZCnfxAkv7FsYxao9g2Ti5D/Rm8kSOHcdNGsrkKI3DIie526wp1pkiUN4Pj8KyqOGkc3wAnIBeRdrLeFUvE+jB6Runb48AjbNI1SjQcDgT'
        b'IODMUcKAjlyNvcsp43LjWZmbTClnGdhsenk6XuaJIwDPo3xpUEE+fwTO+bpUSzEi1Zo0jH3Y3L8bgX1OTx+JfXSMbUV4Hu8PJ7ks5VZLE9Aeu1JBoKZyp17GT6vC8ZqB'
        b'Hae8BCNOU6bDrVGP8AxHfnavFMV9eap8+FEd2Vc+qqPgj+oov/jRKNe3SbjOr4D5qRyl8yA98rDifzovGtN3sx/5E75bHWtbxdj/YBFJ4Jv7bujDAkdSAPfgvCi+FWFV'
        b'kgXOZrFSuKiDn7LwW5mUeAKukClhcQyWxmNhtNwjDFpJ8y9DQxi2BkCrXtrgroE+LdSbmmsMCo7ZPL0Hf5P412O+I1KM7yVlpP5bivRmtD76h6Xf2TPndf3ridNe9a11'
        b'O5n6aqL6R1OkFfNc53V9qVdxxwH3Id/5ScfBvUbtdOyCfjxr5WXjndlulkfOR+53EOzcYNljZ9C/YOvk0ZUinfJFK5SLHpewd5c2PX2UK+GORI93rewEcAYlL5VRcc8l'
        b'OipJjiqSEvKEscnHtGhNmtE6bM/uQ/Y8i9mxE6+rmKc8sleFqGqMnY3IRCO3QzbGk0zF4iHs8Jj0sdtIS+QPNDRjawKve0EtnB9BsS3s71iZ3C59YytLJytrG6Wk8TkZ'
        b'Jqtl2JTEmRDZi45dTTUb0vgZz2NmNWSaBl3QmGnyqM7zQ+O2xG7etMNXFxoRFhoVvyWG8ueQ2KiE0Li1Yb66kFDenhC7JWZN2Cb9VyfVijEsiEf8hB0a6fXdJHBdom9y'
        b'fKzE7zzOTjexxxUXsAcei6I3RvCUhqczWKWHVhdoOAAlnvQRCUUHJDindiHscjLUxqIZ3krfNXIwmQ0ch3aeEXrjNSVcXIxNpiluUTJLHHXPzTk7+bXucccCXJXfOnp1'
        b'demppmXb8ybvanDbtHyc+rWMmPTfV5381g8urfmPiDD7M91x333ztfPXPPrrQ32iq74d+9Hdcv3flnYog1//syb9gfsb9/5Jr7Qyfzsfz8kchgG3sVLUUO9hE9f9WMjH'
        b'h44gikWTRyr/PAsPhjBgw9bhYJgcy6qa2JLEw+hSLMPjUTxEz1dLzp5wCwrl0GzbMEp7x7YOF0pHLCPy90lDBrLISebKTcRNZPGe/w9Gwvc9ykgGRxkJe2yXsukLeG9B'
        b'hG/KTp9YKBvK1KfAfeVkE57Wi17QGzKHRSssJYRXsVAdAcXCnqYfVaYnxYxtTo7CHn/qdLiw93UmxdLU3Y8X9kbGLl4ByzJk8oRojJDF0iF2oJpjpAsU2kYHkUhhWBkG'
        b'q5Wym2QDxZ/Rk/JIZkgRtcMn8rpRcw3neF+X4omU7n9jKJWNGUqdRHXNhDe2fNNIirdWPaqu7drFHcndCZ45P5ESWRq0IjnIS+KJwIwkT4sIq5OfpsC6ZAl/RCQlyvpV'
        b'UVWEVDyF9yishkEpn/pLmyZxjsyT+ajo9EW+kunKM/kqy1ZqyXkv/jeJIyPtx4npqdGGE5nfT/Xd9HHi60nKz/KmLffsqW+ctjwkyOJiWZzcHeMc5aLdvnLx9pXXZ4f6'
        b'KTas3Dtu+2GX0ABFmlp6MHHS7S2n9WqOywlKF84XcbiagMMTsbgLa6DGyh9Mq4TLeNaB4fnRC6+ow51DWE5+JkYlPRtLePsElDncC17XLFiHt0aEbuiWHIHZBQbECY9n'
        b'1sjIDc14hh8BLYXuyQ7vBbW7R3qv6IWi6tiXpOWBMMQs6Bgi4imoUuK5g1gyhNm/ruDoyqM5qTMzFu6xpgx5rDDmp1xlLnIR1l1l5ukjfNaglvm4hGwzwwIjfNeYCxI1'
        b'M4a9GJtl+Sgv9r1RBUdWfn3WCeuiHrHZsT1LrmODhG3u6xWxseF6WbheHhtuwgQPleUvNOmbhbO2VJriJ4a4n0xLfXbW++pKfKE/rj9u84b+jRt/eizv4vPqmEmqi+p3'
        b'P0/88bthLS8dufEX5y8jXq6edPmtJfHv/v6tpw4GP7/EY7NmUVxL789+ufqnyYOnX9+6L2v+D9+ZMCXo0ocVn57d+cZ3Gid9NiUsbFtBkf/emNJfBjnHxf3m9PS9b/m0'
        b'XViUFnFw+RrNW9s/XL1sVunGyMlv/XRD1MzPg9743tON26MX+91881WP2p7SD9sT51zfHvPc3u0/WP6z3uNlGUmLX3jn+8F9P/m2W25PybufGBb+5zv/5/iPy9/4lc6+'
        b'NPqj/g99ynNOJ1t//MN9sW9gZOy+xsVnP/T66Ncf5gVMvbv2vLXu7ppV2y7ff9W2yfV7K743LivwlYDbd37otP+Vf57z7u6N7yl+V516WrNidmjtuhWp0S9urZ+3wnjW'
        b'+Z8CZ29/tvqXL71qefFUWnHdvw80v/Zn1dzkA23rxv3Zddq2+3Pf+921wDd9Cz8cLH/tnfIP32na98Oz3n+r3tRvju41x2yoK1oW/ruU1X/were14D/PbQrJPOX0cUnN'
        b'K/p3/vrpgkO/nfHw+12f/dZ69u3+Bv3Pv1Pml17d77f9r5OMWwY/Lf91z9Pemd/6d+u1L3/8o0+bxv9FWTWl+Pd1Xa/s0M9o+6+D3079j+1/sN/75b/Gh9T1ag81RU7q'
        b'XfDlB6U5CfUL9jVv+dWD2kNVey9nPvhs4JOYC19sMf9xYZ3szY+assmg+a3iayhZK4mWJbEK8lIJy9PhODe6GXBrETMpuBH9GBp+HiutOmaWBZs8noDk85c4HEHGTI46'
        b'sN0T72MJoYYyP7WEnanqF+XPQM2z3GwpiX7osWC9HxZCA1RGRseqJC10y/HcTqiysqgbwf5FQBRzwH5QBi3kaUsjWZ8uObZtgYr/5vmo3u2/1f2r51GZmeGP+cZ9hFNC'
        b'Qka2ISUhgfuHf2VW+4xcLpcFyXT8WNVD7qScIhO/Lio52bATf//f9+sk95CxXyfZJAUrOnitktMOJk10od14yrzmy2XTx9Nrglxm9hryk+Tq5AkJIzzcuP9/jsvMM4fd'
        b'IVuIuTxx1PPe3JGukFWEKHYkQQlU4C36rWCxmT2noJHcpilmui82/XFvqdxSx0J/40d+JfddYPWktR9lBcc94zIlL/2DqX9ZOOXVTXcK10Y2mwou7TT0HP1t5/eCFn8U'
        b'4FOsCXdNv/xs7LSH4dMuxfy0IEs5vePz8H2R732ebXwx9t/+NOXwka6mMl34+x90vfFK0S9Kf/dGYlWf9f2pB86He0dc/tN7qW5d+js7j5YnrvlBqdalbte+GBx3+192'
        b'f9Ro+lK/Yq7Xxp8/mBM2b5WvUj9OBL0H2OXP/z1LHFyJo32wypcWeuR47UiwuO/hngk6GWjoZp1Y/WoC9m8dr4DmbQHcQOHqJmhmnNiBZ7GCBQQyIsYID4U3lOMpK4tc'
        b'LtugICoyxidGI6mVU7Fb7gRX4I6V3waUBycSFqxXSUYolUWxBwTVVvbQLF51z3DAoozVw8AIyhdGkQ8op/BToZDWQbeGRFAdLFxF/dw1jhEqaB8eopamrlX6ZOBpbuxY'
        b'BpcTjszCXiwlj7DQZ5/D6Uy3KeGkchfPNOACdk9jqVQUlmgkpR/eXSmDDjVcsLJTtwnQtlQ3nYfBkbTMgDNKuIIdeIvzzYznsijeQ62C+gkFkUnjNyq2QNlkTu3BuQT1'
        b'9bzRl+2KJ20ySYe31mlUUvQewf0+HIC8BXG+WOyyhFNE4sEHcrydMXdUPjLzH+N0/oFvlD99hdcyZZmsDq/Fnq6SxjEkQ1mYQiljds8yMXeObhi+cVHMZqhnodl72PKf'
        b'GlRkGLMGlezQZFDFM/lBJSUG1kFliimZ3ikpyRpUWKzmQVXSAavRMqhMys7OGFSYsqyDqlRymvRhNmSl0WhTVo7NOqhITjcPKrLNKYPqVFMGpSyDikxDzqDioClnUGWw'
        b'JJtMg4p040vUhaZ3MVlMWRarISvZOKjmKUkyP+U15lgtgxMys1OWPZsgyqsppjSTdVBrSTelWhOMLFUYHEepRbrBlGVMSTC+lDzonJBgoaQrJyFhUG3LslEG8cijic3O'
        b'NLPSlpndV25mD+2Z2Y1CZsY3M6uUmZmPMrOKipk9MGdmyaCZQX0ze8rNHMTemNqbGT41s+fwzKzOYGaHBGZW8zIzWzOz/8BkZoDavJS9MRBuZrpuZppqXsbeWKpiDhj2'
        b'j0wcLsP+8S9rR/hH3vaF09DNQYPuCQmOvx0B64vpqaP/O5YuK9uqY23GlFi9E7tpJyU7mXhCfxgyMsjNeztUh8Fhuu5C7DdbLftN1vRBdUZ2siHDMug6MiUzrxxi4Ig3'
        b'oX8rxL/gep5d4oUypVypcGI6FjWJxSLZ/wXSv6dw'
    ))))
