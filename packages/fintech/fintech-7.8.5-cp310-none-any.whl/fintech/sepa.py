
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
SEPA module of the Python Fintech package.

This module defines functions and classes to work with SEPA.
"""

__all__ = ['Account', 'Amount', 'SEPATransaction', 'SEPACreditTransfer', 'SEPADirectDebit', 'CAMTDocument', 'Mandate', 'MandateManager']

class Account:
    """Account class"""

    def __init__(self, iban, name, country=None, city=None, postcode=None, street=None):
        """
        Initializes the account instance.

        :param iban: Either the IBAN or a 2-tuple in the form of
            either (IBAN, BIC) or (ACCOUNT_NUMBER, BANK_CODE).
            The latter will be converted to the corresponding
            IBAN automatically. An IBAN is checked for validity.
        :param name: The name of the account holder.
        :param country: The country (ISO-3166 ALPHA 2) of the account
            holder (optional).
        :param city: The city of the account holder (optional).
        :param postcode: The postcode of the account holder (optional).
        :param street: The street of the account holder (optional).
        """
        ...

    @property
    def iban(self):
        """The IBAN of this account (read-only)."""
        ...

    @property
    def bic(self):
        """The BIC of this account (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def country(self):
        """The country of the account holder (read-only)."""
        ...

    @property
    def city(self):
        """The city of the account holder (read-only)."""
        ...

    @property
    def postcode(self):
        """The postcode of the account holder (read-only)."""
        ...

    @property
    def street(self):
        """The street of the account holder (read-only)."""
        ...

    @property
    def address(self):
        """Tuple of unstructured address lines (read-only)."""
        ...

    def is_sepa(self):
        """
        Checks if this account seems to be valid
        within the Single Euro Payments Area.
        (added in v6.2.0)
        """
        ...

    def set_ultimate_name(self, name):
        """
        Sets the ultimate name used for SEPA transactions and by
        the :class:`MandateManager`.
        """
        ...

    @property
    def ultimate_name(self):
        """The ultimate name used for SEPA transactions."""
        ...

    def set_originator_id(self, cid=None, cuc=None):
        """
        Sets the originator id of the account holder (new in v6.1.1).

        :param cid: The SEPA creditor id. Required for direct debits
            and in some countries also for credit transfers.
        :param cuc: The CBI unique code (only required in Italy).
        """
        ...

    @property
    def cid(self):
        """The creditor id of the account holder (readonly)."""
        ...

    @property
    def cuc(self):
        """The CBI unique code (CUC) of the account holder (readonly)."""
        ...

    def set_mandate(self, mref, signed, recurrent=False):
        """
        Sets the SEPA mandate for this account.

        :param mref: The mandate reference.
        :param signed: The date of signature. Can be a date object
            or an ISO8601 formatted string.
        :param recurrent: Flag whether this is a recurrent mandate
            or not.
        :returns: A :class:`Mandate` object.
        """
        ...

    @property
    def mandate(self):
        """The assigned mandate (read-only)."""
        ...


class Amount:
    """
    The Amount class with an integrated currency converter.

    Arithmetic operations can be performed directly on this object.
    """

    default_currency = 'EUR'

    exchange_rates = {}

    implicit_conversion = False

    def __init__(self, value, currency=None):
        """
        Initializes the Amount instance.

        :param value: The amount value.
        :param currency: An ISO-4217 currency code. If not specified,
            it is set to the value of the class attribute
            :attr:`default_currency` which is initially set to EUR.
        """
        ...

    @property
    def value(self):
        """The amount value of type ``decimal.Decimal``."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code."""
        ...

    @property
    def decimals(self):
        """The number of decimal places (at least 2). Use the built-in ``round`` to adjust the decimal places."""
        ...

    @classmethod
    def update_exchange_rates(cls):
        """
        Updates the exchange rates based on the data provided by the
        European Central Bank and stores it in the class attribute
        :attr:`exchange_rates`. Usually it is not required to call
        this method directly, since it is called automatically by the
        method :func:`convert`.

        :returns: A boolean flag whether updated exchange rates
            were available or not.
        """
        ...

    def convert(self, currency):
        """
        Converts the amount to another currency on the bases of the
        current exchange rates provided by the European Central Bank.
        The exchange rates are automatically updated once a day and
        cached in memory for further usage.

        :param currency: The ISO-4217 code of the target currency.
        :returns: An :class:`Amount` object in the requested currency.
        """
        ...


class SEPATransaction:
    """
    The SEPATransaction class

    This class cannot be instantiated directly. An instance is returned
    by the method :func:`add_transaction` of a SEPA document instance
    or by the iterator of a :class:`CAMTDocument` instance.

    If it is a batch of other transactions, the instance can be treated
    as an iterable over all underlying transactions.
    """

    @property
    def bank_reference(self):
        """The bank reference, used to uniquely identify a transaction."""
        ...

    @property
    def iban(self):
        """The IBAN of the remote account (IBAN)."""
        ...

    @property
    def bic(self):
        """The BIC of the remote account (BIC)."""
        ...

    @property
    def name(self):
        """The name of the remote account holder."""
        ...

    @property
    def country(self):
        """The country of the remote account holder."""
        ...

    @property
    def address(self):
        """A tuple subclass which holds the address of the remote account holder. The tuple values represent the unstructured address. Structured fields can be accessed by the attributes *country*, *city*, *postcode* and *street*."""
        ...

    @property
    def ultimate_name(self):
        """The ultimate name of the remote account (ABWA/ABWE)."""
        ...

    @property
    def originator_id(self):
        """The creditor or debtor id of the remote account (CRED/DEBT)."""
        ...

    @property
    def amount(self):
        """The transaction amount of type :class:`Amount`. Debits are always signed negative."""
        ...

    @property
    def purpose(self):
        """A tuple of the transaction purpose (SVWZ)."""
        ...

    @property
    def date(self):
        """The booking date or appointed due date."""
        ...

    @property
    def valuta(self):
        """The value date."""
        ...

    @property
    def msgid(self):
        """The message id of the physical PAIN file."""
        ...

    @property
    def kref(self):
        """The id of the logical PAIN file (KREF)."""
        ...

    @property
    def eref(self):
        """The end-to-end reference (EREF)."""
        ...

    @property
    def mref(self):
        """The mandate reference (MREF)."""
        ...

    @property
    def purpose_code(self):
        """The external purpose code (PURP)."""
        ...

    @property
    def cheque(self):
        """The cheque number."""
        ...

    @property
    def info(self):
        """The transaction information (BOOKINGTEXT)."""
        ...

    @property
    def classification(self):
        """The transaction classification. For German banks it is a tuple in the form of (SWIFTCODE, GVC, PRIMANOTA, TEXTKEY), for French banks a tuple in the form of (DOMAINCODE, FAMILYCODE, SUBFAMILYCODE, TRANSACTIONCODE), otherwise a plain string."""
        ...

    @property
    def return_info(self):
        """A tuple of return code and reason."""
        ...

    @property
    def status(self):
        """The transaction status. A value of INFO, PDNG or BOOK."""
        ...

    @property
    def reversal(self):
        """The reversal indicator."""
        ...

    @property
    def batch(self):
        """Flag which indicates a batch transaction."""
        ...

    @property
    def camt_reference(self):
        """The reference to a CAMT file."""
        ...

    def get_account(self):
        """Returns an :class:`Account` instance of the remote account."""
        ...


class SEPACreditTransfer:
    """SEPACreditTransfer class"""

    def __init__(self, account, type='NORM', cutoff=14, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA credit transfer instance.

        Supported pain schemes:

        - pain.001.003.03 (DE)
        - pain.001.001.03
        - pain.001.001.09 (*since v7.6*)
        - pain.001.001.03.ch.02 (CH)
        - pain.001.001.09.ch.03 (CH, *since v7.6*)
        - CBIPaymentRequest.00.04.00 (IT)
        - CBIPaymentRequest.00.04.01 (IT)
        - CBICrossBorderPaymentRequestLogMsg.00.01.01 (IT, *since v7.6*)

        :param account: The local debtor account.
        :param type: The credit transfer priority type (*NORM*, *HIGH*,
            *URGP*, *INST* or *SDVA*). (new in v6.2.0: *INST*,
            new in v7.0.0: *URGP*, new in v7.6.0: *SDVA*)
        :param cutoff: The cut-off time of the debtor's bank.
        :param batch: Flag whether SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.001.001.03* for
            SEPA payments and *pain.001.001.09* for payments in
            currencies other than EUR.
            In Switzerland it is set to *pain.001.001.03.ch.02*,
            in Italy to *CBIPaymentRequest.00.04.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The credit transfer priority type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None, charges='SHAR'):
        """
        Adds a transaction to the SEPACreditTransfer document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote creditor account.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays and
            the given cut-off time). If it is a date object or an
            ISO8601 formatted string, this date is used without
            further validation.
        :param charges: Specifies which party will bear the charges
            associated with the processing of an international
            transaction. Not applicable for SEPA transactions.
            Can be a value of SHAR (SHA), DEBT (OUR) or CRED (BEN).
            *(new in v7.6)*

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPACreditTransfer document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class SEPADirectDebit:
    """SEPADirectDebit class"""

    def __init__(self, account, type='CORE', cutoff=36, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA direct debit instance.

        Supported pain schemes:

        - pain.008.003.02 (DE)
        - pain.008.001.02
        - pain.008.001.08 (*since v7.6*)
        - pain.008.001.02.ch.01 (CH)
        - CBISDDReqLogMsg.00.01.00 (IT)
        - CBISDDReqLogMsg.00.01.01 (IT)

        :param account: The local creditor account with an appointed
            creditor id.
        :param type: The direct debit type (*CORE* or *B2B*).
        :param cutoff: The cut-off time of the creditor's bank.
        :param batch: Flag if SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.008.001.02*.
            In Switzerland it is set to *pain.008.001.02.ch.01*,
            in Italy to *CBISDDReqLogMsg.00.01.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The direct debit type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None):
        """
        Adds a transaction to the SEPADirectDebit document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote debtor account with a valid mandate.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays, the
            lead time and the given cut-off time). If it is a date object
            or an ISO8601 formatted string, this date is used without
            further validation.

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPADirectDebit document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class CAMTDocument:
    """
    The CAMTDocument class is used to parse CAMT52, CAMT53 or CAMT54
    documents. An instance can be treated as an iterable over its
    transactions, each represented as an instance of type
    :class:`SEPATransaction`.

    Note: If orders were submitted in batch mode, there are three
    methods to resolve the underlying transactions. Either (A) directly
    within the CAMT52/CAMT53 document, (B) within a separate CAMT54
    document or (C) by a reference to the originally transfered PAIN
    message. The applied method depends on the bank (method B is most
    commonly used).
    """

    def __init__(self, xml, camt54=None):
        """
        Initializes the CAMTDocument instance.

        :param xml: The XML string of a CAMT document to be parsed
            (either CAMT52, CAMT53 or CAMT54).
        :param camt54: In case `xml` is a CAMT52 or CAMT53 document, an
            additional CAMT54 document or a sequence of such documents
            can be passed which are automatically merged with the
            corresponding batch transactions.
        """
        ...

    @property
    def type(self):
        """The CAMT type, eg. *camt.053.001.02* (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id (read-only)."""
        ...

    @property
    def created(self):
        """The date of creation (read-only)."""
        ...

    @property
    def reference_id(self):
        """A unique reference number (read-only)."""
        ...

    @property
    def sequence_id(self):
        """The statement sequence number (read-only)."""
        ...

    @property
    def info(self):
        """Some info text about the document (read-only)."""
        ...

    @property
    def iban(self):
        """The local IBAN (read-only)."""
        ...

    @property
    def bic(self):
        """The local BIC (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def currency(self):
        """The currency of the account (read-only)."""
        ...

    @property
    def date_from(self):
        """The start date (read-only)."""
        ...

    @property
    def date_to(self):
        """The end date (read-only)."""
        ...

    @property
    def balance_open(self):
        """The opening balance of type :class:`Amount` (read-only)."""
        ...

    @property
    def balance_close(self):
        """The closing balance of type :class:`Amount` (read-only)."""
        ...


class Mandate:
    """SEPA mandate class."""

    def __init__(self, path):
        """
        Initializes the SEPA mandate instance.

        :param path: The path to a SEPA PDF file.
        """
        ...

    @property
    def mref(self):
        """The mandate reference (read-only)."""
        ...

    @property
    def signed(self):
        """The date of signature (read-only)."""
        ...

    @property
    def b2b(self):
        """Flag if it is a B2B mandate (read-only)."""
        ...

    @property
    def cid(self):
        """The creditor id (read-only)."""
        ...

    @property
    def created(self):
        """The creation date (read-only)."""
        ...

    @property
    def modified(self):
        """The last modification date (read-only)."""
        ...

    @property
    def executed(self):
        """The last execution date (read-only)."""
        ...

    @property
    def closed(self):
        """Flag if the mandate is closed (read-only)."""
        ...

    @property
    def debtor(self):
        """The debtor account (read-only)."""
        ...

    @property
    def creditor(self):
        """The creditor account (read-only)."""
        ...

    @property
    def pdf_path(self):
        """The path to the PDF file (read-only)."""
        ...

    @property
    def recurrent(self):
        """Flag whether this mandate is recurrent or not."""
        ...

    def is_valid(self):
        """Checks if this SEPA mandate is still valid."""
        ...


class MandateManager:
    """
    A MandateManager manages all SEPA mandates that are required
    for SEPA direct debit transactions.

    It stores all mandates as PDF files in a given directory.

    .. warning::

        The MandateManager is still BETA. Don't use for production!
    """

    def __init__(self, path, account):
        """
        Initializes the mandate manager instance.

        :param path: The path to a directory where all mandates
            are stored. If it does not exist it will be created.
        :param account: The creditor account with the full address
            and an appointed creditor id.
        """
        ...

    @property
    def path(self):
        """The path where all mandates are stored (read-only)."""
        ...

    @property
    def account(self):
        """The creditor account (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def get_mandate(self, mref):
        """
        Get a stored SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Mandate` object.
        """
        ...

    def get_account(self, mref):
        """
        Get the debtor account of a SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Account` object.
        """
        ...

    def get_pdf(self, mref, save_as=None):
        """
        Get the PDF document of a SEPA mandate.

        All SEPA meta data is removed from the PDF.

        :param mref: The mandate reference.
        :param save_as: If given, it must be the destination path
            where the PDF file is saved.
        :returns: The raw PDF data.
        """
        ...

    def add_mandate(self, account, mref=None, signature=None, recurrent=True, b2b=False, lang=None):
        """
        Adds a new SEPA mandate and creates the corresponding PDF file.
        If :attr:`scl_check` is set to ``True``, it is verified that
        a direct debit transaction can be routed to the target bank.

        :param account: The debtor account with the full address.
        :param mref: The mandate reference. If not specified, a new
            reference number will be created.
        :param signature: The signature which must be the full name
            of the account holder. If given, the mandate is marked
            as signed. Otherwise the method :func:`sign_mandate`
            must be called before the mandate can be used for a
            direct debit.
        :param recurrent: Flag if it is a recurrent mandate or not.
        :param b2b: Flag if it is a B2B mandate or not.
        :param lang: ISO 639-1 language code of the mandate to create.
            Defaults to the language of the account holder's country.
        :returns: The created or passed mandate reference.
        """
        ...

    def sign_mandate(self, document, mref=None, signed=None):
        """
        Updates a SEPA mandate with a signed document.

        :param document: The path to the signed document, which can
            be an image or PDF file.
        :param mref: The mandate reference. If not specified and
            *document* points to an image, the image is scanned for
            a Code39 barcode which represents the mandate reference.
        :param signed: The date of signature. If not specified, the
            current date is used.
        :returns: The mandate reference.
        """
        ...

    def update_mandate(self, mref, executed=None, closed=None):
        """
        Updates the SEPA meta data of a mandate.

        :param mref: The mandate reference.
        :param executed: The last execution date. Can be a date
            object or an ISO8601 formatted string.
        :param closed: Flag if this mandate is closed.
        """
        ...

    def archive_mandates(self, zipfile):
        """
        Archives all closed SEPA mandates.

        Currently not implemented!

        :param zipfile: The path to a zip file.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJy0fQdAW8f5+BtaCCEwYIy3vJERAm/HK8YYDIhlwAsPIXgSyAaENcDYeNsRGOM94+14kcTbjmfi9K7N6EiTpitqf22TtE3adKZpm7pp8v/u3pMQILCd9m/M8e69e/fd'
        b'+O5b9933PmQ6/ePhdyb8uqZBIjAlTAVTwgqswG1hSjgrf1Im8KdYZ7Qgs8o3M3WMq89izqoQ5JvZTaxVaeU2sywjKIqYsC165cPl6qL0glRdtUPwVFl1DpvOXWnVFTS4'
        b'Kx01ugx7jdtaXqmrtZSvsFRYjWp1caXd5S8rWG32GqtLZ/PUlLvtjhqXzlIj6MqrLC4X3HU7dPUO5wpdvd1dqSMgjOryUUF9GA2/CfAbTvqxCRIv42W9nJf3yrxyr8Kr'
        b'9Kq8YV61N9yr8UZ4td5Ib5S3lzfaG+ON9fb2xnn7eOO9fb39vP29A7wDvYO8g7067xDvUO8w73DvCO9I7yhbAh0R1dqEJtlmZq1+dVhjwmZmAdOo38ywzLqEdfqioOt6'
        b'Mhp8XnnwMLPwOxZ+Y0gTZXSoixh9ZF6VCq5zeY4h93YNqNOUrU5kPCMhgw/koudwC27Oz5mL7hXgJtyar8etWfMKkhTMqHQZfoBu4Lt63jOAFsbb15hw04IsQ1YSbsbb'
        b'c+WMFm/j89CupZ5YAh+/ONMED+U16CVGJmPRiXmrPAPhAdqXl5dI38jNwq36LBnaPpyJxnt5dHdlvJ6jtaMLU+pNY8fBcxPekZ8lj8H7mcgh/FTcjG7SAgn4+EBSICuX'
        b'Ps/ELwP0S/wYfB4fhDr6kxbumIuaXaQAgMLbi/ArLKPO4tCVqWaxu7fQFnwsHF/De9DOSHzThZrxrVp8YyVqiYxgmAHDZEq8z6NnPf1Ig3bhY3LckpONt/NafJnhoTZ0'
        b'BG9D16AAwYxBc/A+0ygrupgAw7HNhLej5nzSNNSanJekVzBz0pWNKrxJqg5vnY7b8HVoWE4+uo7uyhl5I4vPqPE9KNCXFDiBLrgTs5MMuUlGGA2W0fTm1fhZdByek85l'
        b'2tGdxEzDaNycg7fL8D2WCce7OBgBtLWc7bTYxvmx4BBB1I5oyvy3iOpN8Oq9o72JXoM3yWv0JntTvGO8Y23jJPRlm8IAfTlAX5aiL0dRll3HFQVdA/pWdEZf0vD+XdB3'
        b'mYi+34MB1TDMqudHl2p+FjmIoTffzucJTs8coC7NWWvrLd4My1YxUQwTv7KytKq+mhVv3l8gY+Cv7mBWac6ixGSmjalSw+1+lX1ln0UzM/8S03fQG9xLYzSly5iqMHig'
        b'NxxmrygZXUrfHSN/6GTH/VS83Tro08h9kWzCX5gH3B8XtqQsZHyMJwkeOFLQNVhHLclzExLwtuRMQAjUVpyQnYt3GoxZaPPIpOxclqmJDJuO98d70sh075nEutzOupUe'
        b'F76Fr+AbgJUv4av4Jr4eqdKotWER4WgnakLbx6aMHztxzIRx6Ba6Ihs6kkGvLA7DF9FF1OYxQT1z0QW0y5STnZeVa8I7YQVvx9sA/5txK7SnbUFygmG0UZ+UiC5DuRcL'
        b'oZJr+CDejffjXbCe9+J9CximT0pENDqFdnVAIzIBSvjtQ2Zjsp/e8TZemmauCSZzLQ/TzNFp5unUcuv4oqBrmGZbKCol6zLNsjwnmX/77a2/Zl1PwVXlzDEmy5JX3/6G'
        b'9daVXVcPDJG/8bxl4au3o95Y/OqNXacOnNpsZ13K8gg865whbldmCl8RzmRvi5ic1qyXu+ly2pyND8MQbINB2c4z+IFZ9hSLrnKD3HHwtJezCN1emmiE8Wo2sIwC7eCS'
        b'lqbRR/hA7boF+GBiUkJmEgdPnuWSeuE7bkoSvPhZqPIMOpGYhFtzxsgZRQmLL/ZC992E/uF9evTSoDDckokuMgy3ls1oXKFnfVyCXs87SU+DEg6Sh72n2ZyO1dYanU1k'
        b'XEaXtdYyw8d77AJ57lJAok6LZqNZp8L/kl7mC6uxVFtdwOSsPpnFWeHyKc1mp6fGbPaFm83lVVZLjafWbNZz7eDgmqwCJ5lQp5wkpL7ZBAZpeNQrCo5jFSxJZaziS5JS'
        b'iu6YiZsShwOLaM1hGQ4dYtNWzMwo50KgCZ3NKQRNOIooMpssgCj810MUgg/qLogSk0dbhjamqVw56PBA6A1uY9D54ei2h5Ts9RQ+a8oRxskZVs9gLzqMj3notJ4G2v8i'
        b'vp6fgQ/CMzmDbmbiHZ4+lPKq0Sncko+24iZ4lM7A6mhGL9Pq8KmI6vBctDMLHvRi0D0ZcKPecH8kPoXOJ+bijegyPJnL4CNR+C59I8eVDni1AZ9QMOxiBp8vxOdpA9B+'
        b'4Dr38N6549BRyK5mctFZfNgTRahe3SC8F92eC5NiYAwj5+rDaE1oZy2+ONXejyPcA/434qu07zHohSFrkDef3D8L/4GL7aCNwlvnp6B7aC+6AjXhg/A/BT+gr+BTMfh5'
        b'fA/fayRPbsF/exp9pS8+OQVadRa/AMONj8F/tEmgT3i0exS8cQddJU9ehv+56BZ90kD4F7x0NC8SnpyE//jIOHG0TqMd6C5+Lgrt4YioFF5X5elF7rf2m1aEjuFTUNUo'
        b'ZlSpgjaqHFjsIby3BL8MGJTCpKDd+KYnHh4U4/v4NhCng3gT3qUkA8GYCfOks1WGz6Or+LrL9RS+XgdYiS+ww9HmhZR8dKBgXDChIcu3gmlklgKDamSbQMp0co3sbm4l'
        b'sKWwSrqyaNLG+Thjio8tb2PbFypdMj71tCq7y13uqK6dsZBUSZ7EM57p8KcGP1dskiQXyv4z8T50HYhwc34e3g5UgR8rjxmLWkxoD7Q8HL/IoPv4bji6AoVa7UN5H+dq'
        b'JtTv00MTWrNNU7UoJWp2/euKD6JmTDp57ldxd1JLPs4oSBs++jzX/L2BCX84smnzx7bjx22alye5Z434+OOnPjwaPl/z4i8tUWl7DMNyHP/ec+e7Uza1vm+MmTvR/MzT'
        b'n9TPjb52w/n8znj3zJWnM2I/Wp1ycMCCiRMu7V3/5qI77/9jUd+ShspFX62tizYOXuZMmPQdnZ+G7kYXlYlGdGGcHm8zMEAMX+TGwfCfdhOpDujgMfxCYjZ6jk3CTVk5'
        b'eXImHAgsYNANfNNNpko2HCawxbAAvQRiHUiUimXcsIX4vFtH6TPaZCQsswhdSsbbQFyDNfditpyJGc/jPcOeogQXH0Ab0GVCxYcCi6SEnFLxCRFdKKpe1pnEdpq+cGtN'
        b'uUOwmgmNpdR1KGlhpoxVwQ9Qvy9VvIxVw7WGVX0VxWvhbzzknFFBlJd1+dQ1DrMLdIZKq8tJRAInIVFdW8M5o8l1rwDBJdVk+Qlu9J0QBHcwPFiYg3d0RCQZ049bivfI'
        b'6oFhP/sI0ks5dAfS+z/l0WGiKHY5M5oZDlKXPbK00fl0lihgvaLNZHbBeviTozT7cE4pk0Hv1q+LYmCydbecpZo/xvBi0WhTOAODUHlrYGnVz0qqGJEGbwF0Oo9u43vj'
        b'UgAg2suUwdSfsX8uTORciwiA/yz+pPT3pZW2HMt3bQm//d2GK4evLdr2eeGhzX2nxMelGISPhY9LDXsU19Im9Z0a32dsnClNKFxYGF9yeHiq4ZnY+VGmo0RquKMQuMUT'
        b'i0BemMJEj+g95i7oH5R5o+uza4J4/rwBSZ5q9yDSspPoGjqeaMwyjNYbAQcP4EMGDKs1XidbFjVVzz4e9vUqr7SWrzCXO62C3e1wmiUOryU0pITgoBZQIB5wzhkThG98'
        b'uV3wKcsdnhq3s6FndCN9cPYOoBupZXEA3c6HQDei0KIDeOsYQLZMUJnQjnwjyKvN0LlkBFITcPzp6IjC1IjP9UeXuqgYAcyjsiELuNcuG7IU7x6tAnTBO9J0VRe8my3i'
        b'naqQ4h3zl6KGRsu89RKKFU+nKDb5V9PchqXy+UwxZTgO4Ojj8HNETRvDjLHjF2nZASNELWDXrDWGqfl9GFo0EZ+xjMNnJ8qI8jx2DT5Bi26ZSlULRqdtzPmeJ4WhfHoM'
        b'ao4HOXw0RzSscZbJtOQ3MiKADTAJBZOtOf+3yMR4yMJHW+ajF4BUlgO7Hc+Mj8YHxdu38IP8cUXoFozmBGYC2jKeVjFoTCyxLeiu9CtbMmuyQ2wX2p6xbtwMtBPGZCIz'
        b'0YWP0aKrVg9kYMQTNuTVDihaNUuEFh6Obo5DRxDh4ZOYSfhEIi0brtQRs8vkk5ENA370lF3sQxV+Pmuc4ILpm8xMxleVtORI2QgmExpQkFQ3q0A3ViyJzqwZiK6bQUFg'
        b'nmKeSllOS353cgJTANz6L4sbhz5TP50RpYs2tDMKhIINaBeM2RRmCj6ZQktvnpfEAK9MKM13z3pVUSTWy8ehrS68OR2KzmJmxZvFkbk4AT/nwkfx8zC4aUyaZzm9PQg0'
        b'nQsu9JxbQcTV2fj6UHob70/Hx12gzJyBgUxn0udEi2LGSfy80WXDh2DMMpiM+mlSP6aOdaHL8TA4c5g5rgpawxB8F59wDUSnYSAymcw5+KQoct3VFuHraM80Sq2z8G10'
        b'gxavEAbj64vwIWhzNpMNbGmP2I4rq4hckoxeglabGJMsTWzHLVcDSCuJ0OgcJqdcwr75MOigwkZtsK8xvDMjTZw6UPDPZ+DrHDoOPcllcudX0rK1YymNVJWOqKzakDNa'
        b'wog7c2Px9VXoBeheHpPXbyot2rxgFEBhon41fE3ZrbRxjCiInUtbhK/jlgHQ6XwmHx9Fl2jh96YkMsVQ78x0V5lpXa44fehl9AqIc9fxBXQChqOAKZgRTUuPi+8LchmT'
        b'8naZbZp35jqxFdPQg6nh6N4cuJzLzMVnx9Givy0PI1p3ypVFqw3v8DPEmbak9woHvn4GRq2QKZwTQUv+TB3JDACqV1tgr5q1tEGsFD+H9mrD0QY7jGMRU2QcL446Po73'
        b'hvfFt2Agi5niOnSA1nAssx8sKka1K6G08XVNslhD6nR0NFyJN8MwzmPm4Z3LaFGbbDADcxk/s8I6LdmTKxZdn4hOhE9Ex2AY5zPzl0kr6w+OoVQj2rV49ax3x9aJPcD3'
        b'0J3i8FIzDOMCZoG5gpZcmR8Hcjp0d6mj8Y8L1kgj3pqK74WjM/gADOFCZmER3kYLl+ckM0ugBVFc49D8vizjAZmZ6bN8EGqJI/R5EbMopY9ozDCOZyphDc5cbiscH8eJ'
        b'vLJlzViggcBsK+sL8yepxZvfiBvDlML6La12Dh0zZyJQf3EMTzesRy1MLYx2CVOCWxPFtXkO3XOjFpDM73GEJSzuhbZVff7VV1+5eTklhsyYmpxJybli1XsTJzFVBEcj'
        b'q51x5SMZOzNpCe8aAoP6yc5fT3/7zWw+NXbr+2teKMk92uo7d2zCW9czWq/3auT7DP34TxuaEstn7vv9vCjfsV0XW2a/MfVzZsah8yuGRAx2935aPmpM849jH1Ym9j2U'
        b'mBXL/btmqD2z6LhL9YPrz0z8TdpgWXXl5cQpu04tcv/AuNDXOsjXMsO3k30W6wailIgxs/72Smvj1N//bMwvd/y7Dt3aax925jv15xqn//GTvubvn575UUp+nyuZB6/k'
        b'LLiS/ZMreZOuZN066e4/9UbT0rvetSWInf7NXtNfy1q6eFvR0fe/+M6N8XFC2drE+a3mk0eNBe+a7nznl8/+9Js/7hs7q61xau4Zy7Hq0cZZ+qwX80/kHZvc/z9fnZ20'
        b'cldT+Gn3953Dl/zzo5IfrNX3iTjT7/6Xz5/5ZevT63f/4T+Dj4SXga4PMjMxU5aCnrcBhN48YqfbaUA7TCyIxS9w+JIqk9oXjOjmAEnQGIQvUfvCbLzRTaS/QvwCKJS7'
        b'lCABJuLW3KRsA6id0fg2j734IGqir4+srwd5eLspi9gYzEbFZK5vIzwiwuxUfAlUzGv4tAtdzMxLSiAWV7yTZ3rhXTy6AnU/o5eHFFNkoWSKIOFFKwkvnnIzEaGp5HID'
        b'Eo0gY6M4GZWfZSz31WP9ctyXoX9lHfM895/H+pVxX7T/yuBX9YVMwVHZPZbT8io2CiQfgCvTfEn+OuP8fdPzIF95ynsSq1hnH/8g0PfIUhQtJsdDSFREOJmRWhokT+VC'
        b'Qq3V6DQ6zujxBjmQuTmPkKWIsZYJkqXYr2dODS3DK0VZavBADRVaUup+/vTVeVZJltpRJHKdlLq7vf4+qURi7ofQfg0RykHb81LBPG+l3dDyHuciZsy//X3DJ6Ulr17Z'
        b'dWpv2+ZTmxNj2g6P2TrmyKmmUVv18W+YLHmWSuse2dX4wkOphpXPlDyjfa2f4uSUA1Un+70Vx7wVEXHlKYuedROlH99ArzSQhYGft/sNb6gJn/dL2D3gZz8RP11up6fc'
        b'7QER2+y02qxOUPhEXNWQ8Viv4jR+GTs+CAdkLijcMxL0DSABeZFs/rgINjAbo74KgQZkCwadyB8QwIPkFeieUT8616hPys5FzcnZuaakbFDyQGFGu9E2Nd6IN6geiRQd'
        b'BeyviRT+yjsihSJPNB+dUESEO3l0Ce+GzIsMOuzGrRQxpkZOYN5Y9zbwodLCy0tjmAx7+A+S5a5J8Gj+P6d/UrqEIsDVzSvZcvWHs14b+qX2nPY122ux58b+o+rA0G/E'
        b'/rb0Ga0i6ulDG8fxTPjD8LBvr5K0rgXhloGZwaZW/Mosd39KCk+jSwGliyhcujqqcpUPlCaue3SI76RrdUQGtYgMYXEsIVzOfsGoUP5IVOgfQAXyYnMQKnweAhXIPgy6'
        b'I18WUsUKwgN8Ce1hGlBbGG5C1/GWR6r5fCcL6+Op+SFJRFdsUOYV00nvo9UyUclTQagr1QwdkywKCAuXyJnPymMIJhh+9lS+eNNTDOJKLlllpTlmbgZjb8l4yLtAKGVe'
        b'/+6RD0Ev/0PpG2WVthetnqiPSy9YEsoNe/5UuvDV27uGbNUfYd+wZVsOlH4scD8w6GaMKpiXElWfcj5l0rht49xjY8c6z/HMtO9EHvr8KqAMWX7oELqCmtELObkGjpGh'
        b'B/iOiUXXSqdSDooOoDYbcF+8Izk/F7fmZaEXZUqO6VMomwhc+dDjausRNdZVbrPgsZoFi1tEm1iKNlykmo2VLEYyTvMV99A5IIBAMp+MFPeFVVktArzZ8AgLETGiOQcF'
        b'EIpUtLMdoaI/DYFQhM3j09GrcYsJXUxAzfn6XNSaT/ZcGXX2CHxNXoKfwYfL+aBJlgfjzwwRf2R0T1DuVdgUEg7x1EovAxziKQ7JKN7w62RFQdfdqeyKLjgkF9nM02Vj'
        b'mR/WfZsgxtiVqQNEbPlJppwZz/UiKFT1iyXRjP3OL4rkLgs8uZZ6duD2qxEbUjSyX9YVpqT6/jDb1HfuzD5nb7ww3tZyRR/3o9/9/byrZJWlwKDe89xPvrEjY2/kxIkr'
        b'5xpXzV7Z/O1ja+Z9+vNVhWHrh+dftTr/4thzcdU/vjoy98oZ++t16wx74392cSrIaGRwx6DTIA2R7ToVuqpkOHSandcrhRKkWRkr6Ba2sk7cwcY78A4q1xnQjUgTWbot'
        b'uDWfZVT4xCi8nUNbUBu+Q42deHfMQHjYlJzEleALjCyXRQ96oZfdhLIOTW3ELbnoRXTKwwC4Lewc/CC/J2FM0e2jzqiqqbB2wtR+IoHrqwIM1QKmqoHjcZyKi+ZAOlI4'
        b'BwfwVU7wFZCUoKBPUe5xO2zB1C/kIgE8HkKudR1xl1R6uB134z4OgbukdL0e3TQlrslP6oC6g9FpGT5iTO+eBxJ9PLCLzdjk/y0fjIDf3l2wdrCIte8t+zazD6Z415L1'
        b'YaPGxIlYezJ1CDWmbDAun/Za0Wjx5sWn6V5zSgpba6hhp0jUsEKUoq7k1RpKZdJW9d7VovFKN82yBNBOvHkrTDTmvO2oHpAGKj29+cZiUQ+sHVw29uKkMPGmayXd/o6q'
        b'TVylGTGgXLyJB+upLYapE8p+M2qYePP72hlMI+ibrw6uduYslok3DWunMasA0KuJjsIL1ljJDjtlKuMmarS8yvlRbp1487kR8VTlL+i1dlqjLE28eYYRzTi1fSvK9loS'
        b'xJvHB4uGt5lZqzTVjdPFm5/1n8lsgJsptrVjbxeulxrPiZrmq4OX5yxzDxFv9i0VJdCC4Z6cn5RJ3CVzhajZF1TVTHt3pNSkNx2STtqvKvoP7krx5qElc5mTAOjVSTY1'
        b'G2ESby4YJjBvAKCowbaMga5C8ebHugrmu+T1iAbF0tUK8WZboajC1yZXDbjt0oo3L5dpRcsEX2n4XX+neHNF6WrmM2hS7ew1dekN4eLNb4WLannBQGe0YHGJN7/rEg0I'
        b'tZbGoV/kj2Ls7k0gJBPd+XaTdd7u3DycErX19at/+/CbI3LDspZPVt/6uHcG1xbdUlw2YZm1vOadAdv52vDXXmv99mtf/uL+4b8WfTDuctxfz97/9IMY24dbF8yZvHFB'
        b'gmHyq5oRqZEJc2ZaN35/2u83td1I2Riz8D9/fr+fI336hr0Xsv4xc9OxZ28O3doqn5E77cjbudH1Bz6aU/vUjF39Njp/yy3OO/vlsrPbJ91I++nSMpN8/7u5C14c/aef'
        b'nFm5fv7fvuX9bPSFsLjf/X7n0PnDf3dyaP1Pk/YsT75aIht1YVh9+Efbvxzy+e5BV39+IX9c/qnkH1x55/b38hLene19fbxl0qTXDXdi/hTzxz8tW/OLpv+7tXlF4evh'
        b'FZOES1c+rZ/xnX95v5v017X/+TT3e/N2LdrKnKvaWuu9OuTBw2//M+yzfyc7di//J/OWnhdN7efQNqPIvVfi+wEGTtn3chvl/jXF+AG+Pc5kAD2hFVRrFajWDcloK6Xr'
        b'pWg3fh6fj0yECkazjMzD4uapS/QRjyCmj056INXBNn5CisssNSvMlY4qOyGtlB4vFOnxUyrQRVX8cCo/RLE6ur8URWWJaFbDqWVqkCnU/h++0196JftIM0AD72m+UgM9'
        b'V4Hm7RwaoOYgvjZYLc4gAt4Df2GdwwK0m1RxqZ12x74bgnbDWmF64QMGE6Xc2Xg7bkE7qLvJTtycA5NkUDDT8VUFvtYf38ZHjV2UDpn017UcEitx/2NKuDA2jBXC6eYB'
        b'B7oNJ/Bbwkp4q0yQCfItzGa2RA7XCulaAddK6VoJ1yrpWmWVEc5g44QwQb1FBXfCvACuRF1EpBWNT5kqCE6ry5VHbPGBfyomaKdhFuEuom9UwFfKppJ4jKJJBTxGCTxG'
        b'QXmMkvIVxTplUdA18JjKUP4LXRVweR41bSrRdXSmiGFGoBvMEGZIP9wm+r9MNb8oc7ngij1yaOC2MWQnWPbnH18d2Gd85g/djU3KtxeeadX85k7qtzeVnbB8tS/8ey/W'
        b'jT/itiz/lvB53jxL47GmuotT9q18ekHUv89+0Ny2dOdb7tJvP/jeH387MmXwn18uiJ8Rv/sbwunNLe/vVlXY3Jdy3iq7bfrXl8yx+YPeSa/Tq+kSW4juT4b1FY92Bi0x'
        b'fNlDH4bVFgacasLQfnE7djnISNTF4XZpTKIxsFfciI5y44qnUn0O3zb3oSLr5vIssVZ8jwMxfhe6Rrea0Ub8woJEY5KoCJ5Bz+ItXApqQw/oVnNKMfaiFrQT7zSpPUlo'
        b'J9qpZMLjOOzFZ9EGWn+daiRqIbYWfCgZtybq0fMyJjKMdwtoE233CPzKKFrAgNpkjEKVNZ7rix6g01S2G9IL7RttQC3JIL0Zs6jBhonGZ3m8MWMULTAS7R0Cj416tA9v'
        b'ys5NIr53LRy+BS261VWyVz02bWmnHUqzucZabzZTijGIUgzZWnE/Oo7uDaqBSiikHxm7OlLCaqP0nkgDVD6+vMpFtwFBmbW7G3yqWgfxWRCsPoXL7bRa3T6Np6bdUNKT'
        b'gqJwku0zJ3GcFDcWifurU0+S0QHiMQKSL9qJR7+tXYlHl7Z2EPNY6beIVEJWZCOznKG+vmxeG+tTmaXdT7iWuaxVtnZXDXHgVNOqLNVlgmVGBNTyN3JfwayO8kP0P3ws'
        b'kDYAqWd9cjMZOWdSAE4AmDMZEi286gQRiXmsOivFOsPM/nnott7IJ6q3QqxXaRZntdtao0LW2kG2nsiI9iWgoP8D6xLHdKZ4fJ597Rs2uYss8+vV1k9KPy79blmlTWP7'
        b'VQ7PxGD0Fw4Nn6FnRQ+7F+ai7e3rFLXivQoVrNSTMhHBuZCLJ8LuCjL+BVznmPXMenXc6t5+ZOhQSvT24Z1GUkv7KggGkBQYSZBJmWgYQFc8xXJmo/ZPIfA8NCCg+OSf'
        b'Phxw2Uw898xmn9psFp3S4VpjNq/0WKrEJ3Q9waJ1OmqtTkBCuu7oMmxffONpl4mnn8XlKrdWVflXf+cV3EbwTiwGRWhHiAryT0YyZ6gYTs6x0V9pelGhApTEeNEVeUYy'
        b'uuZKwntzsvTZSUYFo14OpBadxxu7zHa49Ne1i21n6wJbwu/j90Xui4LfiH2Rds7GwZX0I3CtijA+jBcMhO0HuSJHAcsljD8MWLjMKgfGr9zCAJsPa+WA+csFNc2H07wS'
        b'8hqaj6B5FeS1NB9J82GQj6L5XjSvhnw0zcfQfDjkY2m+N81rIB9H831oPgJapoYFES/03aIq0ZLeCETE6NfK0jZrQFzpLwyg4kYkvDuQvGuNFAbB23xJFO19pDC4lROS'
        b'JEMLL+iEIbRvvaD8UAprGIUVDfnhND+C5mPEt/cp96ls/D6ZMLKVF4xUMBHPGJDR0nojbWFCgqCnNcZCDaNpDYm0ht4CT0lEMgg/5ZR+Phyl1gX9k+6Khx86PNErfDI7'
        b'yLA+GUHIUPiXV64MQgCycrT+JZ9HKIkoRYWRAZQm1u97rrVpJQqjpDKVCiiMklIYFaUqynWqoqBrUaZ6/1+A2x2aSP5l1djddkuVfTU5uVFp1VmkDtmBt1lqysnRj86v'
        b'TKm1OC3VOtK5Kbp0O7zlpK9mzUrN0zmcOotubJLbU1tlhUroA5vDWa1z2LpURP5ZxfcTyMsG3aysND2pIiE1LS1/Xl6xOW9e7qz0QniQmmcyp+XPTtcbQ1ZTDGCqLG43'
        b'VFVvr6rSlVl15Y6aOlj6VoGcSCHNKHc4gajUOmoEe01FyFpoDywet6Pa4raXW6qqGoy61Brxtt2lo9ZwqA/6o6uDMROAu3VtjjQ8ZNan0HaRK//5Gv/wgl4DHKzblyVW'
        b'Lb4vZWCMivKTxo2ZOFGXmlOQmaobq+9Ua8g+iZB0CY5aclTHUhViAP1AoTsSRLgK3eLHqcfPoMW6/LmvX5/ImMXaxOuvUVcXc31XU6smz0OYRqEalN8W3GowktMvpgW4'
        b'yURP6AxGp0FIviVD96PRPtHIkrVDVstO5piU0po/zxrIeIi7vTYbnaAmygLcBAI63oi2mJJxM+Tyi8Sq5mWSXeXc3KxclkHb8Okw/BLaiI7TKtVFisIyYs7Rlea8be0r'
        b'nolAzX3xfrJXnWhCt5OIf2fO3EzQzCXxHO/RozamKFWJD+ITk0QzVSw3czVVy0o1gyasEc0qJ8pktW9yUcRcrDG43IyHiDX46Cp0UKxbrBgUhs24iRzWgeYmF2bibTkK'
        b'Zg4+q8BX8f0C6h/BP+1yrZQza/sxeCf0gB9nn52eJnO9BY8u/7R4xM6pNTglavbBX/8+7b1rMbrWqSeGpefteusie17HYW7J2/rfjKzKuBXleHbIu/flvzQoF07+XIiL'
        b'/Cp+3fBDwrqIux9sOjb+lXfu/L5q2g8Wrz62ZNoPJn1L2aAuScj47JcTN/zrvc/ZiD+mzt874pXnFiX98v9Sv6x+qeUXvVf/9tdPL116IP1O+qRxaxuv3Up++fo33zWM'
        b'WP/ttb+2xTRO/Gv49y4mLZlaOfEsf8T0dPib/d9gD/x8S9lL+8t/c8kZafnTq1PfPOU8kjM6Kdnz4YQ3sr74e+TOoXM+mPMjfTRVmjh0ThduIu7HzQtzPUmj8bZkjumN'
        b'vDIVutBA1RrQs24tbvdVIFrN3krqqzDb7CZmXnxwLrpvMmbnAhJtMWSBOLaTnodi+qEbshoBtVK1ryJTIW3hwSxcptt4Rfgl6pIAYsNli7j7dXky2QDzV9Abb+Hx7Tno'
        b'ENXezDHoAdnss0wMbPfRzb5ZeLubotJdfJ/onfB6YuZMTM5ZSVurJujXDtHNYQ66qkQ7U5KoIJnmWSLaKigihKPjqHUuh3fEo+0UYD06hvagFn9r0HaFHD/L4rvo9hCq'
        b'LvZFl9EWIoeSt3l8pG9fFu3og/bQh9OXo0PkXXGBzYyX47scm4z3iWN6hC+lAizBc7QfvxxQRYeWufUUddHRgUTXbNXTI3EG/BLeQ4dWrC8RXZfjrZPQcdoPZR0+R6vL'
        b'YaEdJ/AZ9AqLduGzuI1uOvRCV2EZtuQbc0kzX2Kxl0VH0gdTaxrag7egu6ShucRfZB06QWzt2gp+Cr6JvaJ/9Ua0Hz0D71NJD+8lwp42jc/InCIq7dsUeeR9Awx0XkIf'
        b'4oysRRf42Qr0wL+Tpv2vbWudhXmQku3A3SVVOFOS41VjZKJrNkdMZjJQiTVcHOToPaoeR8GvotMPx3L+6y/UClALRcpr9IMQ5eYwUQl4miQzGb+220nqblcRHlu91yvF'
        b'Snp3rJ3WaQxUTOVyYoEaHKxgjHw/hILRpf1PoknLzUT06VZRXOhXFNuh+JXnhyOKA3IS4WAgU/hZWILTahGSHDVVDXojwOAFR/ljq8VEozeX2cu7bdJif5MeDicNACmr'
        b'R/iPrePTwaDibXeQlwUgJ/YsCj15A4ji7kxk/OplCOCWAHBjsBz138BXS/CXs36TBAfrzCKqqyKSdtcawW9WUUmD0ZOU9eSN2UIb48wPLIzu2lFBRqWAjEry48hnT94S'
        b'W1BL9D21ZHmgJUmPlu2+Hn6KreiuAdUBBEkppgoLwA426umkidVV0fPu3bbhf2MFsun5h6e7CK5pROlw6eyd1qvLaq2mZ+1B06G6SJcXyfl7SQErAoUHepfucTp0BZaG'
        b'amuN26VLhd50lZMToMvQcXixbqJxrDFF37MkTf7Jma6m+WI9K57V24121CXS0zeymSw6ORg9j2977G3Tj8hcxL2rBV/4pPS7ZZmWBGtC9Melb5T9AXJc2W9jX4s9t+y3'
        b'2tdWKXQ7tVeGHNo4LoLBbNiIrRl6meifcgjfFIUHylP9HBWfi5qNtqHbbrIrk5eIrgUchoiEgs4CKw/ITPgaPiU6HFxbYZDOp9PD6csmoSMWdIWKZLl16JiJCi/cMhYd'
        b'RFuS0Un8fE82NCUxWvmPRok+Usx6dV0c8KDVkX6OIJURX5vQubJ2exk5M1DbwV62K6RduGO1IFPMhOKP8H4i1gTGy36dQ04PvV3QosjqFi0Iniq3HfRnidh7XJLCTINN'
        b'uJ2WGpclKGhEWUOXikgdU6g9ZUppLpSBquCPpcLqLH2EWkf+dbWaSh40heE7mJ/HTSPKWl62bbWorOED+HR2kLbWraaGt6PnAtoagzbYP7i/SEYdCst+fvuT0mzAX0P0'
        b'70s/Lr05ebntD8LvS2Xv6Le/Z0ifNUKjn1kXU3Bm81PHx2wV8XjkX8I90zV6jkqG6E61Ldw0Qg7aRUfVwpTmJmR8LbqQT2TcNnQ7IOd2kXEb0FHJcepRG6suq9vsnyDK'
        b'uSmWRklYCtKhKBuCBLi6rx+purzjh0VFL4JoPXtn0RLGAEqTM2irg1E6+pkQKN099McWDkA60XZqeHeM4JkAI6Cc6HFR2Og/LkaoSPe+YtTnhvrbEONjwOfmcT3FiO0O'
        b'lJautrvAknM47RX2Gosb2mgXumOgNdZ6iayPMY4JYSHp3iwkiLYX2n2/LygAMuoKrSs9dqc0OgJclbt1grXM7naFNEWRBQ8tcDmq/cKYHbiqpcrloBWIVYsDbLM6Xd0b'
        b'qjzlYovSZmUBv7av9JD6QIRJILxZ5/S3CmBluS2EWz+abnT13lTleYiTHz6GnxtqyiMb9TQqRV7S3MyA72khbsqZm8mD9newUI/asnTLypzOdfZlYcysishqdF3hIUg1'
        b'JTIy2MIS9DqzBrjYNbx/HjCy/exKfFO1YDY+Rn2II9AmUE6vaxylMPX4AoOOD8SHPES9wZfR/addWnS5j2d+JtljnYebDPOpB0ELaivONBA427Ny8DYWCNYZ/Sp0YDg+'
        b'V8wxeD+6pSnQou3UCyEWn0J7SbuW5vlbVqv111iwIGm+kilYT3aQN+Jn7ENjgGHXwlvfeeXtpO/eI56F6XPXo/zPxue8KtMgZvyBXQlhhpnPvh53RZ/w+vyTVw2Dl6Zt'
        b'1/5i9Zb9L9VVfPjNUWk1DR9HR30zfe8310WO3LXj2opLGbc+MOYO3rF5zeeGW+pfRr/+zp/ln/35i58tSV3744yYCd8JH35sMFJM1YeJ21nXe9cBnSbqN9G9w2vQncEc'
        b'PtIHHaScHl03DAofjU6h0+TAByGSflo6GF2X4cvY20d0jb+KdkQGeUnj1tIkUNyfFZX0q/h8f1O7XY3RRKEXNHzvmbhZNEjsxudqwk2F6i60ek0klRWmrcwCMQKdsAck'
        b'CXQk1kbfnYBPGhKN+HpykB82NczgzYViy67hFmruuD7Jb6Jg0a4lFaKAcrAyDJ71w3f95gl0BN+YIjkfPpZHDSGj7WTCf2p2aDvhj1GwIvHXSCxAzCm6sIIOtfibQMl7'
        b'gBT2xA/4oGLtTGEZJM2s3+dyI/mJ/cej2EKHljwJW5CZgah1ywxOBZjBGKqmtVO8nnSTJ1RN9LQVnu519jOBVkwNSerS5qV1tv+HaA9xZqp2Wm0+hcteUWMVfGFApD1O'
        b'J2gAGeWyoLYSc7jGTwOzRYbVHouL8YZLDj0am0ZiX7ImObAvObAvGWVfcsqyZOvkRUHXEvs63CP7EuOQiaIe5QTBmk73G1CkXyIf8L8bOJ/Q/V4CHQXxLfoKjCC5ZyH6'
        b'nlGXZqkhCpVFela2HDhaSFZGtrmAuxTlT56YMoZucJHNJ4HosKBrdQs+MPhTdBlVlgpdfaVV2j6DDpM+t5fwd6o78DUOdwgwTit0pMY1RZfaWYYulbrzGLywq0KnzvPM'
        b'FjnPfnSKxWc78kPcJBHmeZlwq1Dib+zYaLQXOMx1E76ezYzAZ7T4WXxWSeXuBAvaYjImjc4GUhv8eqDazOx5CdliMIxclsFnBy4J1+ALxRwV5T9vpCESSo9UlC7/dNxy'
        b'xkM28uebybZNKEk+KTu3KBNtdwTturQUheEHZQ2eqaRTN/GNqbiFlqJ28SzCPhMJQwWWncAE9lsyDdk5xqyk0QoGt+g1KwvRSQoYH0Dk50V0rAOTJ/0h8BOAnIO0btAn'
        b'ZcuZ1fh8GGrNNOt5UTs+gZ4tp6B5RjZDhp9h0QvyTBq5pahvXiLeEYWfJS/nEi+vw9wafGs0DQOHd+einYnZueIIwqwcS2SZmFE8PjIEtdl/kb1D7mqCYu+kewa+lRiN'
        b'UzSygjd/udD6jW+dPfWtl2dFRn0QVnto5KgLzau93L/P7c+Nu3/4/xZlyScvO3T1A+WI3viTN8oa5k0oennLtveO7/jzwe/UlERN/ezGFwV/e/forp8//37u6dtnC76V'
        b'nDtmdP6p3069sKs0fKD7k7Mvp6w5ueKHZcpFzi/ee/7pf1jvr0qb8uX0L0YbL/8QeDg9opRmMlHehs7jA1wZOwYfXEk3R0qRd0n46M6cWzZc5N2oSSNqStvRea1fBsBH'
        b'0VYqB4AQMG8x5aC6nKdMWehltCN3NIhWHKNCLRzamGig5oJJgIhn6R5OMOfGt9B+mSoP76FnC/Ce6gWieCGToVciyZmFB1rKf7lcvAcal099aBVV+HAeNxQdmi6GX2lD'
        b'bfgc9bXNB8zF23LRNsEA05HMg7zVkkLZfzo+WU1sFXX4ZkCGIfsHIONtEFmo5n9k9A8njFEiHZTFGwMsXjGeBMdQBRi8WvrV0EM4HLXyq/+jkK+OCWayUl1iKxUiyyYe'
        b'204rSWwduX3YkzkDy8SaaCXGQJ2UBVZCcr6jQDD0pyEEglBtfWxjvp64xfk72B0jfiPAiIcQrgE0lfKQANMJtgrqZcRDqY3Lg6oz9HFOYgt0ksN9TmIqIL6JgqPcbKa7'
        b'FE5CCOluho8nxvuZJBtiw8Sn9JuXiTGIqs++iI5qLZGegsSqSvpWh4nr9T/aXeoO75wkeFNfMl/rGGLhlnGxMgUr+4qDuRr0FTdRQQMDcfzX+6uVadTRLKcWwwupZbEs'
        b'F9exRLRMx3KDKQZ/KUWwRGf6uNAhtCEnTxTpWUa9msM7UoZ14Xdq6a/ry06+VwJXIhP4ErmdKVEIshIl/KoEeUmYoChRC8qS8H3yfap9UftYG78vSlC1ckI+SEnh3igb'
        b'T12oiUeRxhohhAsa6l+lbeVKtJCPpPkomo+EfC+aj6b5qH1aay8x+hBIX8TpJ9Lby6YSYoRY4iMFNUbv0wLcKKF3K3X3puV62YjXVR+pRAzUSfytiFN3LJQh/lf9hP5b'
        b'VCW9oW2sMEAYCNdxwiBh8BampA/1p2JK4oWhwjD421d6Y7gwAkr1E0YKo+Buf+ojxZQMEEYLifB3oFcBNRmEJCgzyMvAtVFIhuvBQoowBp7r6L2xwji4N0QYL0yAe0Ol'
        b'micKk+DuMGGy8BTcHS7dnSJMhbsjpNw0YTrkRkq5GcLTkBsl5WYKqZBLoBBmCWlwrafXs4V0uB5NrzOEOXCd6A2D60whC64NXhVcZwsmuE4SCiRjDC/kCnlbwkqMgoxK'
        b'5nN9itRq6uj1fAdBiSx98YHo6yWGtwUZkAQcrHBaiPAnSm7lDQHXo04OPh09x5xQQbXVbS/XERdFi2gTLRcFULhBZEqoU7SqVDXoHDWilBhKitNzPoW5zlLlsfrCzP5W'
        b'+Pj0eYV5D6dVut21U5KT6+vrjdbyMqPV43TUWuBPssttcbuSSd62CiTn9qskwWKvajCuqq7SK3x8Wk6Bj8+cl+Hjs2YX+vjsgkU+3lS4wMfPm7Mwo43zyUXAKj/cDnaw'
        b'DjsjjYT6ci45ocBruSa2kdvMCuwK3hXZyJ1kTzGu3m5O4Bq5OIYELG7iGgGZ17IC38jWMc6kRpY4NcJb7EmehDkWFH2hXDwTy0xi1rI1MniuJFdNDHmvkTHLoFb5KaD3'
        b'ZoWgospf2PvmUIpIZx84aZ7bXeA6v9CdeE9HQlQuLGId9E4PhixxyKZQL7Oi/KTxY8dMCkYjAXSSLBuR9XWuWmu53Wa3CoaQGoHdTfQHYIJ+bzcK2a8giigLKorTXubp'
        b'RqeYQh5PKRWsNgtwlwAalYKSYi+vJLXbxXECZJTgAIJ17dvvyJw/7G2vodtS7b0ZNcI1yscafWzK7wjb+N1X8O8hb0xJydMrfVGdwZJtFEtVbaXFp55PepLudDqcPrmr'
        b'tsrudpJjHT65pxaWidPNUKMCFR8I73GuZ3o81E557y9YyXNXplawsZK5Q8eqODVISKsjRQR4MucA0Y+cNq1bUeLvAdcAP4iAZ0BSZ6ShU9dQa9WVwpSUA7OvMs4W/5aW'
        b'Gp0ZzBO4t7exdJS6bdbnAQmnP/VPCI2IXcBxfnBREjiyhpdz4QETB08nxKeyuMzUH9Snsq6qddSActttU/7NSvEgtczDcuox4KkuAwUZBkMaBV1tlaWcbMZa3Loqq8Xl'
        b'1o3VG3XzXFaK6GUee5U7yV4Do+aEsRRKSwmeWoTlHihICnSspes2bsejTCwNFxGISx44ysRS0/1jbem+/6dQJGdeLZHNRHJjXVVeaampsOqc9FaZhew3OMSdWyhl0dU6'
        b'HXV2sitb1kBudqmM7OvWWoFzpJGhhc7NstSsoNZ2l9sBkiMlDjWPRQgkIuBvkpk2qZSMr4cufJHMEHoUsLLD+BJX2RD7eCRivNVd6WjnYgadyw4UVaqGvEY22YMdbrvr'
        b'o1TRFBJzfkqpxGBDbAj2aBIpczhIUF+dLdj24qFTIXSahpAkst7qhEVaB9zRUka8BbqxwnQQMAlCdT28ps0TvS/PN6IDiUmZoNA2E19Tst9owHfwjkzI5c9LyDZkJSmY'
        b'6mgVfgCK8B0x1CCoyKBLXsE35yZkJ5HAyzsTiXPZJXQTny5Mwuc4ZvwceQXe1leMvr4TXcIvuIy52Xh/vSK6Cl1mItFB3lgQT/cm8D58HgoEWS4S8vriU0mjTUmF/upN'
        b'cpBWVegePH+FHmtAzVHolCtBCl0vRzsX1LL4CjqZJwapP5zlKkKteN883Ir3z8tlmWL8nCqfxTfQleQMGqQSnUTPTiVtkjPoDrrLo0Ms2sBPppE7EyrwJhfeip/LFM0b'
        b'JnRJxvSCJqMX0UZ0jFpHpuFLuNmVQMM6ydfiM3gjiy/is6pi+z8+/JHc9S2GxDZr7N06vXCWRZO+988HXy+6urZ16ycbdvSu/OPbwg81D9l+b78z0n7mzbF7jj17+d7e'
        b'NX9qns/PmiOrfubZHW++c23zhvmJ++KnpXs1k2JLr2S/N3fXXz/51725d94fvPyltzI97PLjVb0/OfN/I5W5Xs/kijd/eLZxQ3HGvef2fzjoF8ef2XpOfkY/uyT5wzkf'
        b'Vf3z5wPunPj071tt+gGTahb/annkc6m3/zB5a33MN/+d6f3er2588x/v4Oh/LOo36dLTq/4z8JOBmg+cv/1U/e5HTz/4x/T6nBH6XnT3IzUZ5p/EqsItShI96JIsiUUX'
        b'0WW8gx75WzxsRWIS3oabkzNxK1+ITzOaDF6BmrNEu8luGLb7qCUZirAMeg4fkSWz6DryovPi5sLZ5ehgYnZuDsvY0CuyISwAOILa6I5GNLrsMWXljs5VMgoZjPluToXP'
        b'D6JAM/E2tMtEWwW1HsUHZX1YdDoX3XQTJ2r0LN6AblOjTi26FWJHBp3Dh2nfFE+j84lG/Wg/NmnwsUh8jW8oCBONMpercJNoMKlFZ2kkiZKBtAHFeDs6myi9ha4kyPJY'
        b'dAW694AafPBe/MJKYnLJMkxcZ0TNyWSRQSU6nQy/FFVJd40a7MNNsODoasOXhpryUWuyuOJG4/tyvAmdmy9ZnuRjxZ4S02Azi+8sZsIFDh9ZG0ENW0OK8H5TfhJLwutx'
        b'dWwq2odvi0O7ObtP8AFrvEnONVRXiFtWN5Kx15RrMuUa0fEi3Gww+YM4jEY75AhW+1pax7x8dAO35KGLBgWJKf2cbDaLXp5d8ATOk1/nFGVvkSqaOzICalCaSajaevFH'
        b'rY2STEnEqTSWOo7KqFMpMStpWdHVVLxL3E3JX26DjF09QJJ/QoLxH8KiBya/jrsoK75KpYp9kHxFpApihxMNSczGfiHCTfXcJqiTCJbdu9TQgDA04hhIC2xQQBiOfoXk'
        b'sdxq3v9xKFkhTWR20vkcUUQkQg3wHsK/AlKaJDIQ+cElCf5dWZO0udBJ5ugkYYSWKLoyuuKu0ouFcMgODN3PXx2E8ZOdlQYimnRtmaW8Utyzr7ZWO5wNdCPI5nGKPNpF'
        b'v0LzaGbfWa/qKM8GuTm6Lc4KUGL8JXvcSqkJ7KWIGOLfSvELVUQUsrqCLQCPkAlCH2hXiY5KarOGiZ+2RMEUlFbFJ08Wz26ENwxkJqu2MnBz2gcZi8Wb/Y0vjX+D+Qug'
        b'5MyVh/LPzaNR5nRTPK6IiAR0k2NYvIPBF9HVaA/Z0ENHZqGTAXonSRf+HRs/py0mG/8LgOm3JM8Fhr8ryJkAKNPqQVFTcGuSvc+v/yx3XYA6f5Kamdsqnq3/51vaKG7g'
        b'rNnTNg3defK5LNPWJe+/Nas4Ly1hh/nzdduq+91970cvzp+c+leL5Wr9pwOmXB029m+yMW8mjNymOv/zn2a2zV21Zci7s97/+PV/ni13YF1uif29l5STi/rvG3fkx+rR'
        b'Syf9SFnxctjBWb3y1R+9/tqEEX8c827L0Nc/KNw57Nr3f/RK2IJ/liz9ctyd141rdr/70jSV/qPeZcvemnZ67Xq2jpm47epgvZZuEcSAkLQ1EW3D14MCpaHN5dRGX4xe'
        b'WGEKEjkiodz9+XwVPoifo0cwxuTg80Hj52cWCSsldpGjoRxrfBhH97Dw/fVSRCTsTXaT86KF61GLSPGDyD1A2SqRfLwF76Fsd4VZSVke2ooPBqIn3aG8aARqsSVSlhAI'
        b'6hGOrnH4hV7icQ20Ce+rlqIn4Q34shg+CZ3HN0U3g40aYPYi01yPzzOUaeJbU+k+DGrClzMpz8TbnjZ0Zpq4db6buFvPgdbs0Q2nUmsWdKLDiHD4GtrGmpNV6AxuGSXG'
        b'A9895+lEh5buvcgZxXJuUDFLWfQ4fBid9u/J4P3ocpBHhRw/SycFH8MtaxMNuSCeSlHtIwfXor28E513hDpo/7j8TSlpEJSjjQ3iaKqJhJcppKMRcWw05VokboiWcjXR'
        b'Q0JLvCK0Er+QqurgFbe+I+vqIYAIJ5Ztd4U4AEkC14lhxf04BMPq1IAuCjohM1RBJ2oDUdDhl5jSIgTWzcE1v5mNgwICF5yj4TceciPsD2UjjGNt0CHSPp/GXOMwS8qz'
        b'y8dbylyitSWEIu+LMgc2xEWrZDYnHSTXcDCK3Oo+fgNLp3JdTIeBnWgSAq+Jfm9iM+cc1sjSvjAreKeO9MnZu5E9SfrAnGLXsjXhbl5gG2melLTxokERrmXkmxW0j1ze'
        b'w1EBzlltd0EzyispzxkBJJ/YqqgCTS5g9ugQxNira6vs5Xa3WRxwl91RQ2fLF1bcUCtaqOigSOYon5wyaJ9KtO86nN04DGvNtU7iC2w10/JzyWCRyCZq6n6jJeHxWAUI'
        b'LPRgvDRwHd4IOfF02GioVWIRhaEgNtHlrI2LE3e/YACixdoSSCcNYledawOTqu3YSpXZDDCdZvMSTjLRxAZbysRn3aNgNG2JHwmlVthIK5QEzWDUg0B3wielmUQBMNOD'
        b'TPQERVQ77kuPOshl5FrmBxxPcf8kYILAnuLW0kFoZFcEwLPT2jjnKUayHsI1XYknQjRDYTZXuc3mMtIKUj0RbFdHBNpBnj1xM1h/M7hp052EozrbuoFsNZttcMf5AtwI'
        b'hmoNATUw/8bgZdPLvyBWcI4oEf5ydgUxWdH75Ira7cSJIO3oBmGhOdaVZvNyTnJwV1MZn/tKzQU1jJTo0rCAyVBDh4MA1fjNhSKAbrpfA92s9U9/h2GvCTUAjxp2WWD2'
        b'Z/Q46hUwp64Qo17xdeZa7ic83Iye5xp0DnN9KKjWECss4PBOhtS/0gOH1YKIdNf1TMxhZvMaAukKE2SU9j/p0MMOMuvwkD3sQ3Z1GEp4uc1cYIgT2/j2BUZJqT9ayInA'
        b'3U6NgxVvEQSzeR2Zcso4aPDFoFVPH4dE/CD8Ig08FTQYd7sbdELcaI2bQwyGsyusxxiM+M6DQaeeTXLeJlDvhO60y1NmNj9D2nCPtCGIyJEH3XdXS5sQ3rHDzvs9dZfW'
        b'2OKn5ZoOtLwrNJ4JoipEuQ5QFaWboRQE8rFdu0x2AXzaPIc7C3inlRw8sgrteECHobtjNGZztQeQcAcnbWio6eHUDkhACzwREoAaj3oaFVrjvlBI0BVWBySYHDwmUV3R'
        b'oX9glPqHXiXJ7YjRzYiEm81up8cq2OvM5oNkYbTTXjWICKujA40NFPv67e0XaG+/kIjMJT+6wRpgWVUOh5M25QQZ1NfIoMYE2tn+9Os3NC7Q0LjODaVCDjvike1U0iBC'
        b'ZvP5QBODUMzRee3LglvXQS7tFdw6N2kf2cKGlrRfL+HWcmt5qZX8ZtJeXryy+YfWp4ARAbAgeVOq+R0mmHT6FQxCOn3y+kpHlZX49FZb7DWCtTsJU202i3WazZc5iVyo'
        b'qSITxRHVRvbV6l6BHvtLdi9VEllO5DThdOgDa7176ZFGZaswm2+TIT7XcYjpg8eBpm6HtuVR0GodLrP5Xgho9EH30GIpNLcIie1EyZzPdpiL7mCDcmQ2v+KXVqI7sK2y'
        b'UNC74+FULLrZAyR7DQgi3wiQq3Y49MFjw6noEU4YXagWqPCbAUhRwWuYPHJuZUJYRwPrhByBIitjBeNUuUHjpA4erMALMsI2+kAz1pIVQbQ4rok7Ja4RaWXQ6Zbn/Y5U'
        b'+nAo3da111Toah314sbwmBTRQcJTW+sg8X4ecilGHzsGVso2/3T5VCs9lhq3fbU1eBH5lFBThd0N+qx1Va1fdevWZgDjQIGbza/7JV8VjUBKvnAXNCJSoTbKbciw6JM7'
        b'OQI6q6T6XFUONwkpRrx1fdqOFmfI22zWcre9TgxJDeS0yuJym0V7qk9m9jirnCRUtPMYSdpdCgP46VMFFPZwasAUN1GpSZwqrs4jJKFU5jmSnCXJ8yS5SBISy9R5mSTX'
        b'SEI+VOJ8iSRUjnqZJA9I8ipJKFvFJCG7b843SELilTtJWBjn90nyNkneIcm7JPkhSX7uH2N99P8fF8VO3h8rIfku2Q4gHhEqRsbL5DJOxrb/RHGxLNe7G39EOccOYrlR'
        b'Kjae5XRqVqvQhKt4+JFpZSoF+auRaXiVnPxqeZVCy2tV5EcTpuHFnziebqDWrZ7owttxK/VLxNfRTUYVz3nQ+ZLuw73+tJNvoj/Aqk1Gw72qaKQ3Gu6VxHuTIr3R0K5C'
        b'GM0raeQ3OY38ppQivWloPoLmw2jkNzmN/KaUIr1F0Xwvmg+nkd/kNPKbUor0FkvzvWk+gkZ+k9PIb0rq6SgX4mm+L82T6G79aL4/zUdBfgDND6R5Es1tEM0PpnkSzU1H'
        b'80NoPoZGe5PTaG8kH0ujvclptDeS7w35kTQ/iubjIJ9A83qa70Nju8lpbDeSj4e8geaTaL4v5I00n0zz/SCfQvNjaL4/5MfS/DiaHwD58TQ/geYHQn4izU+iedErkvg4'
        b'Eq9I4t3IlOioXyNTMoR6NDIlQ4WZlPym+iLJIZji9rOl71/pvBXkP4IZVEgKO9epGPGsoG4e5ZYaQhjLrJIrm9tON2L8zhg0tpnfyY34Y4g7HtaOezPSjlBH/wuiEQUd'
        b'hC0lZNginuMRHOUeIucHau5Qm8Ppr9DuFo1i4qv+DZa01Nzi2VINpd144HXIZNkkZxKLroya8KA6cV8s+KCuQQTp76vkZel2WsmAdKjP4qJOnaRx1MWjDmqyVFXpPES8'
        b'qmogjKfDCeAOL3dguERtJSSHmLpdJSzhf04V4YF9mSbOwzo1fj7oprbLU+xaXgCeZxZTGU3lNFXQVElTFU3DaKoGqZP8Dac5DU0jaKoVeEgj6XUUTXvRNJqmMTSNpWlv'
        b'msbRtA9N42nal6b9aNqfpgNoOpCmg2g6GLg3b9YJLKRD6J2hjdzJYaeY2czSRJB0ZWvljbKTsEZPsa4tAlz3YdbKajT0nuIU69wlKIHDj2iUEXPgWpl7JHB82WbOdcQ9'
        b'SlA1ykSrrTuB3G2Ub+ZZZmVdE/RrubYJhEDX89nMJoBMxaSwPOePiHQwQUT8Lsuk54VA2UOGjzX7OLP5odw8wjXC9XBE50oqLcTxqd13SjSY6n2aQmD79mrJQ1Ehbg2K'
        b'4Ud5s13wyc0eq9tJosSIJxV8kWJo88BhNedswpjIJ22dRJ1wksO5YtySxVQs6HjOEcQ+cQ8Yaqz1OEGctQIIKhIoqRXdbfEpzNWuCgp6BTn7JzdbxT/0JGCE/zX6CTJ4'
        b'qbyS7F/SCLgWt8cFconTSszblioS6qjG5oAW03G12+zl1E8ZRBGRVgQeW6rd7R3yxZqrHOWWqo6H70kE4kqy6+qC9tG1CtXQv2JkYt8Ac6chBzEW1qFUVg7X1S6fGhrp'
        b'dLuI9zUVqnxKmBcyJz5tqn9mxJlQuqxu8kCvEL0BiA3Bp1hRTz70HhS6YB3z6LgJdDZ/SYS+EoZYn1UhImSputzp9ocjaZQUjl5LjRpayMvY1X06jcATBXqWPFD/yjDd'
        b'u3pGg6IjeqDGdwYVcEWdVky9CGpWtJ+nNIhBENwO6Qwq8QQUgETbbQ1AeIMI4hN4plIVLq2nxvb2N/bhyI5xs8iWe7XD3X7wlYYPfYLTt87MnuDGB+B2DJfVFSyJV/p4'
        b'UKl6bOoJav+OvQ0OldUJrBQ89PHh9hgla1AArj5ElKz/AjQd6OKeQA8JgP5Zqk4MGevylEnnK6jXOYEnOb5IoZh6bBcVksSK6IYikWlq4TUij9DYNCGCOxl1Re33bHYr'
        b'ASgJCFA7FGh3iwnQfpdutDROow1waXfTv/5QWqPp1uFoMZ7V6CcYrJKeBishMFjju8Yo6QY/U2ctSE2GJP0JsBRIyKc9tSMx0I5pHY7HkxAg1rKOB+U7tyetMH128uz0'
        b'WcWP2R7JZPu3ntpjDLSnkM5+EMuWnKX8nvSdvHiMutk0Vonos1RVb2lwSefDdTXWCgtRvJ/kPL/zs55aOTbQytF+VPd7IgU1WOLMuoSi+QtKnmzO/t4T9AkB6KMocXc4'
        b'VhBJVjzlDgJuba2DnGMCkcgjnot/oo7/oyfQkwOgI4sDx1IeH4TE1P7ZE4ipHSlYNaxZS4U1CA1rKxtcxBtNV5CalQdrvOoJgLexzs97Aj6j49C2A61yVHSEqUswFaZn'
        b'PBnm/6sn0KkB0KInXo2Q5HYkwZ92xq1LSH8ymNDdhz3BnB2AOTBk5AVdQu7jA5Qm9989AZwTADhEdDcEkbCGHOCQlooYDaNgXmHBk43sFz0BzQ4AjaY0jkrI0lmUJ0Kd'
        b'r3qCkttOEzpTLiJXE9cYcp0wKz/flJU3pzh94ePSTWlgybNuoRcEoP+5M/SO0r5RlwE0Yo4V2lND5UJXQOUOFeYdiNeCrIxiEqzdoJszP82gKyjMyk3Nyy9ONehIH0zp'
        b'i/QG6mqTQVCmUqqzu9pm5+fCChKry0jNzcpZJF4XzZsVnC0uTM0rSk0rzsqnZQECNQPU213E67S2ykIiT4nROZ6ErLI9DeH8wBAODSLqomokIqaFLkaLC0bxSSjqf3pC'
        b'm0UBqBM7T5yowRl1qe1nyLLyMvJhCmbnzSGUnqDSE7Xky55asiTQkj7FlNuLaiNMoUBwx/EEMiqsFXlPQ21up/FS5BR6KFEEZG03/wTrIk8yz1xPwMs6Er12YkfcsHXE'
        b'ZhWCqfhdQuj+x3wJoGsU9VfT0P1A6ghVqyXX4rFVst8Bv7LNkJpJeTn1b6MHZs00PamAVHkKsLJ9mh5OLRRdlYnlKiDjiCJXuw0ttEhm1KucfyHdrCZJp8DN1AZB4g04'
        b'HQzdPG2P7txpiyicfLBNqtLKSzuMCi6efmqJ6LgKdnX/zgpn0DvdzxSxogniHhWXVyyCDDVNZF/CwUtbbqBJd1FvA04t3R5jjJfmyKkk+7inGLJvW9HuTAP9V7Lkc1DE'
        b'KBHST00lGSzM5AtktOViTK1QjRELdt/v2KDGiHF1Bb/jIjV1+VsjF/WQbtzmqqw1ZnN9cGtCGxlouTz9sFD7VNT4QXeWfNpOhqunA5jTjjQ1fnzxRXS0Wykks5VS4tz0'
        b'q70+hWSykosWKxk1WMmIvYrGBvFpOhirFJKtSkbtTtpOVqnwYKOUQrJmqdqNWaIhSdvRWOU0sBL6OJPJ1RhWGsTHCqzm/A0k7xDL0I8ZcT8pOpwb+4RRLpTd3Jf9d1Ez'
        b'uv2reLxyGplKreI1cg+JR4L3ksNV4XURtRp9Nt6emJdjJF7keCePXo5kRlfK0RV8ELWGjKtI/rlWMcH7VwK3haEfKOQFWeADhXLpWkE/ViheKwWloIKyKi9nY8UPE5aE'
        b'iRE1StQ0fC1HImvA3XBaIlKIgmuN0EuIhhIRQgxdvbG+mE5In2MHXV0W1FBZMCkgUf8JOTZTRw0zS7aizVwFiSXACwGuIaOagS8s8NVguKx2CJYq8r24oZ2tmQSiOXjX'
        b'xOX35ZjM0r1afyUqfx2daRzZ4t3AS+xLtCWq2dUDQsB5sqPr1PbQvycG+EzAbBgS2hN9HE5iuLN7guf1w3sSUSW9pxqbuq0xMOnEKcLv+NEextxIas3otmp4sI1UfaXb'
        b'wemW1vfkjQHdaYfZkdlSCtUagNmZrUowKUX/37DVXQRWEtt9/yTG2tl5P+BTQ75m5XeScoW5AbDkjk9duFbwrn5wTR2i6DW5kq3gnYPccnGDDPKKk0rixcfSk1L0e3kP'
        b'k4IF32pyvr+sPWjCqE4tHdWxuOCwiqfYRbd/GsvFfzSOcgkQi44z0tIUPy8/h1xlkoR6lZDZAZZWWwvqtt/fPzwIBC3ajTsWbxGEvX4pSS0dKVFTV5IuzJkOMZTvHnvU'
        b'Eva0e/K0z2YnzEmBF4/ykssnyCV9QwELLZAFnCpj6SoRKXgjM5vZzEoSEp/XRfwNvEQ/bgPFlyrIAQwiz+zmVlK/KpHVcs7xZGTXiddkPfhYd2dcjITkpL/1sczqpFCt'
        b'dzvcliogSGT/yTUDLgidd1TXztCzPt7lqQ4pKcnpWycInv+ArKmQ40LL5Om1nWWkdscbiizteNIuTlDpIpeVZsBZEBAxeghTkgaF1vLS2KkYYMQKGpuV0/AqXssTlxIP'
        b'sevPxcfxyyH4MrqWgK/jZgPQr9n4ojIH7arqwpzjpL+ufWwH5gyTS3/4o/ISnjiVEJcS8gFBQU1YL/lUoKAlrFbodVRbQr4aLAc2HC3EAOuV0wOwKhK2yhvt7WtTCrFC'
        b'b7ivsCppiCrxS8NKIZ5cC32FftT1RCn0p/kBNK+G/ECaH0Tz4ZAfTPM6mtdAfgjND6X5CMgPo/nhNK+F/AiaH0nzkWKLbLwwSkiAtkTB86fsjDVqM3OG3cGWRMHzaOiB'
        b'XhgNT3tBb1ghUTDAdTS9ThKMcB0TlixMkUJzkYAg7R9c1EJvo2h/Y7yx3t7eOG8fb7ytNw2FFVYSu0+5L04Y28oKUwkcGBOeBsQi4cF6k48TChPFZwBpkjCZ3o8TxlFW'
        b'Oc2nIbjod4nwsQU+Nl8v93FzZvm4rHQfl14Ef4t9XFqmj581J8/HzzaZfPycWQU+PqsIrjILIUnLzPDxeflwVZADRQrzISlKJw9KTM5VlCTNySrQa33crDk+brbJWUyo'
        b'G5cFdWcW+ricLB+Xl+/jCnJ8XCH8LUp3LqQF0kqgwDxoTFaHpe8Pfk49H6RPDYjRtmSB0Oeyxw193vXDqF1DdcvyPGT7HETQvZFkKbhxc74Rt+bi1rH4aOLc9rCiNKan'
        b'MYueJswxZOXOzYQVkk3OY5KPpM7AmyLRjSx82v6Lf52Wu0jwvfcGLfuk9PelCdaEDxIsmZYqW1WZwbLk1R9+48auMYdMH20cxzMVLyh+99MGPU8/FTYJHcSbwlGbIZOG'
        b'OyiemMwxvfBdHl1ELwwRvxT1shFtwC35+MVYvA1Ak8AAR7hV6HCs+OX2Uw1oq/iFZnQg3xT8iWYdbvKfMXz0bjXnp9X+g43S8cbJNLZ/bDBSdfzysbx9t9xJvgQc+pOu'
        b'QLloiZGBYgHI13h/YOmNwT/Rb4Y4wRiyHeWqoMkmgDt+FlNFcUktfV5cXIBifJ72z2KqmsIAv8IAv1QUv8IoTqnWhRUFXYtn7jviF+lb1y8DDsjzEHqfo0enTf5wgoBL'
        b'SUlGEqiWRnlFbegEhmmfV1CPtmSiCzyDd9SG410l+JaHLAHknYDvt78MeJefNF88Z51JYrg2452mBQm4eYGqLrU4olZG4qJcDo9AJ+PpUe+lIxQkPHNUStzJwpWLZQwN'
        b'EY+O9ypxRURwyfXSUW98Dt2kxVcsD2OiGCYlZSTL31k+UPyMIL4cO6FjHPoOp76V8P59ZlGRsgGdQvdpmBV8K6vClJVrMuBWPcuENw7N4wDEQZOHTC/asgCfSMzE29Et'
        b'+uG4veNSUtCWUhMzFN3k0Svp6Bka4mZ2eEZiHjkg3Jo7L/hw+Qm8J8GYlICbkkeTkLwOvQpfn4G20fAwsBxvoDMm3JKVk6xpUDCKPpwWH7BTBKUF8tz4TCJZZUn4ciM8'
        b'R3e5iSZ81zOTtGv3sFn0GYBDVx0BiO3Q5ibQAOwFCWK70NZMnhmEtkagW+gsui32/Ca+OcFVh6/J0DPoRYZFhxm8swKf9BCHBXwGnSQnsNu/EVkLJYsTYBpbDIbceWII'
        b'fXKyHl1Chwoz2yNQ4jO8Bhb20YEecrhXwIeyTA58QQo5j7flJCmYmDk8PpYygyJcyvI17WOX1B7iP6grBAqHtnH4mekMuokehE/QVnoI9qI9+D6L985l0BnQ31czuTPn'
        b'eXTk/r2BNfg6OrgOX62vwzdQcz2+5lYwEf05dBjdRxc95Gs089El3gX355MvCyRkJwECAJmkwAoTNGhXe6MUDNqLb6sB+fp5xsCbqybjG4lkIGBgWpLxzqKEBCCETcl5'
        b'87LxK8HfFkAbUFsYs2yehxyfcuAHaEc4fgnfcOFbK1FrvVOzEr/E4HvoANNnHI+2qPFuDyWPF9Erq3BLHTpMvn+SZISxlTPRaD+PLuXgaxT3vTNlJOiSLmX+/SlTh9gY'
        b'DzlAkD3y/7H3HmBRXWsb6N57hmFg6AKCFbExdLD3AigdafZCVxRpA9gVVKR3VFAsiFJEEUVABTFZ34lJTmLaSTXN9N67Kd5VZoYBBkvOOf+9z31OjDjM3nuttVf96vuu'
        b'VKTobMN1UcrKdHQgHmbdESni8NbVcMMzPPhqouBm8tPrXY+NeuuTj219Dtvv+l702dgzZ6w/Wj7O7LypjnvAktO1fh5JP/B/zN/t3DYm9JkxL87e8eUv78wuaVo4P0qe'
        b'7moh9ftVIsgCP/047JTjxnXGct+DP0lDRuucHV0t/bFm9W/mpTfEPz7p+25Zkt+5rvVr8v44bne5drft6OsXnx31el3hR54750TFjvn+85dflGYY/PJJ7T4dqxdcvrRc'
        b'ckUxKWKOgVtq6hh5h8XEpW5PSFwD/2FwSU/RbB76q73x25szp+i+UfP7/u3P/fJTXdC+WXZ1l37ykTwxd9PHU+T/OFRUmJqcDB1lk8o2V43+wlAxM2f1h7Grvq8PfzXx'
        b't26/d9a+6GC+J6x9ysSXth+vOhUcfap1uaHr1Bl75j39heX6kkWb37cunKlTtyoiqeGTNSca/jXvroHdaxPDomaPfXprseim7Hsrl9/mZXQ3l4zISZqxtuJU6vYfZCfc'
        b'90x7fmLKH1/sVBS8v0L8zb23IvIyN4XLx7LzLcslToayFeojsveAzIIqRrdYjbId8UpS8TrJUA60ogsCnEHXUDE9Zm1QXhpBDkD5c/pRMaBDY+kdW/e4oYItRob6Zs6p'
        b'0K6AjjRDCWeeIgqFs+hIGlkgsTHQRVB7oiGfovZAkZQd0M0ol8AObLXw1+BxQFkokyEStE2ATEr1WSiHXNK8pFmoRYC63eg6o4k4jDI9UIFxBnQkQ3s6VMI5XLVsqLAh'
        b'Qo+iO0CWYhjloPCDYyoMiqYh7NXPoUZUiiUUdC20P1HE2Um02cvtocLPOUCCsnw4YRs/2wvVUmSHDZCNzkNBSjLk410Ct1s8g0cXdXUZitJ5qEaFlMcqSESYrFxQpl4a'
        b'CTT0wcKKIsMgJR06jVMIeAMqNJYa6kOrcQZehtCxJQU3PkAsQVeH7KKtR8V7JA5OUOTvljKO5yQreDi3GM6wF9s33gwKvNF5bg4UccIufhE0w2mKdgTdaL87obcoQOe8'
        b'odQvAOEDz5ngng9D7eItqBJdoMOGyvB2mEN5OgnFUYE/ln1WJc4X4NAYOES7dzbKFlHOUD/L3h3A0l9siFpm0FZsn2GM8M6L59du1KXDSSIE29noOAXP2LgE9uJryt1L'
        b'B8+sqxFBAhyEE1IK0CGWr1MyigWRAxmXjs9JCcox4kbDGTHeNY9DGR0nR1Qa08s9hlvfrmL0hOvoGIWnmrQBnaKgW0X+eFwu4a7yEYbiT8doTdCC9qMOSimKKzkJ5wP9'
        b'gygpLM8NgxpxCqqFU3Q2TlgNlYRWlB0hRqb4EDEKFQWIoZz2FxyFk1sIbakTFij8RJwMOuEUOQ4a0D4jWkAUnIKj+A5fRx8iIzR5ctLpQhReUFdYQ/anQZ3qMspldKvQ'
        b'MszBx0ng7O10IGvREIp+goXrs4SgJNAR5bko93QdPL7HcN906uigGuX6bltricXXptAgDSgVM3ycQIEJrmsaPVs3ozKyQDQFdQeUh0pcUP2UvlqsAz5fisbqoxPSOWlE'
        b'mkjUwYec9kebINdfLuH8oRO1cLroEqqHo/QZVI/OpCs5b7Uz3s4fouS8xdOzg6K6o9OoOpVMFVRvjW9WPSXBKrMIbkQJ2mXw/zyJK7UuUFk+eYAsrz9HSnlbxYIVxTAV'
        b'C5a8FW8giHmloYA34U3wdX38PUmdld4zEuErArlmJpIIEqE3ipX56Hp/Iz9H8dst+snnGmSvTfrKHCpVWLOYGN5Sx5BGLyDaoSw6Mk0doSxRRG+I3RzbHxdF9yE6o0ma'
        b'msorC01NIz9oIbSidPIrtaEreM0e69Sug0z4hxYdRPs7PgohrO465dsNCrCqNp/3reyR7OY0XnbL/Wzcd9VuajvKb6LKxGCts1FClvQBrH9UINnbsnXK8Kp192HQ+VPd'
        b'EEdtAVnxit62/S3a1yaeOa0Hq5+ocaz+UWE0EovEYf1tplvmsCCB8ulpSXFxg9YqUtdKiVXx3U74dhuSG9AbE0ZaQmOrH7kZdPzt7jf+EnUD7GmMRHycMihiMwlFwb0e'
        b'm0iSWmL+Hpkq7gKDdRpretBm6KmbQSO2SHzGegLopg5u/DsDkFp8vwE3UFc5cXAE474Va9RLN1g1kB8x6qrB4Zk5gSOJNrv47Xo7OWpO4KkJgdvNh2p83sL8EgMK1sYs'
        b'Nzh77GRaexz/iNyxhGSJbIZaYWv7UA31jf9Q2Cg2JKUnxFAa2dhUCjBuE7k+kkSNaC1LzdfkkRAbSaKpbDxpFg0ZYCUeLg1GVGKFK+OQ4rXj6SphxCMiwlLTYyMiGMlt'
        b'rI39pqTEtKRoQnxrb5MQH5UaiQsn8WYq5N1B2QXTBqx2gpivDENg6IIsjm2bRnjYg/HUIyIWRSYocAsH4vrRtC+u33/8gCEXBcYH1Z/iFEQY7053+iLiqZULo6Rxd7B8'
        b'K83jOyb1yHkKwQaXYR9WNqiM2lfqsDUhOrIJM9Lx/V1K4rj1sRTM7Aei7faVE7g9klHbx/U5eBTRCeto//Z6SkgBrEBiAGCeo14eWkKQaSJWgp30PVS5LIPPBx6rlC9q'
        b'gmR8X3OsA5TtQHkOmi8Hh1AblvXygohChTqwckOUMg5aodPQFWUN/y+R2Gq1LKt9apqWZZK6bgANkKUpQm6NIm0nFpk8f3tfR3Q2jBmZyBdB/pRjqhnlyWagS7rxHSXv'
        b'ihVkl7r93JQvIpzfJxTHdh87RvpTc/KXEZ9GHH0uMe7LiPz1vpFsSlQOkXKf68tFaWRLM4er6JJG3ZnWWiRYpfyKtccuhi67DzXCDTWp0saQfvC7c6CbsRddmh6unm3o'
        b'GL5XU85d6P9QBmc8+xTK2WepZfbpjyG8Qw8xAxXKGdgk1oDzH5xKUIXVtVs9S3PxLB022Cw1u6Nllnpx1FJ2fuSAeQrHFjxgnjoEknl6cbjhbFt0VS5Qw+RkyB7GJrDY'
        b'mEedkE+QF1E1Y/u6iKps2FPiSTxUWaM2O2iIz6v/WkS3/fyJrR/EbFh/Ntc72h9Pjo3vNepcetP6zeqXqkKrQpdn7rw57MCwm+avzvB/3KAmnrtZr7ehab/KfappmB8c'
        b'wEDd6VSjIFYDge8/WgYWJvr64u2W2keLjY9wn1HROJkL8XAYDzYcJl9okcUHqfW/QLb+kOsf79tHjW7xCqLRS7p3foEX67NRG+IMQvXoQh3ynQCucrx3E712F9q3tL9u'
        b'GruLaaeDaLXQBdkDhrBfqAcdK227ur7dAP8Jjfro3cUHIRUnpY4ZbFyM3ngIP83A6JL/hBAzQHwi/w08S8WBYfGd3rq8gnxt+v1Jv0gDPBgiTjyRXxRuV/Jur4A44Jyk'
        b'nvhBj0mxwwBlkIW2DH4ukvLGDXouagPt1F7Df7wvB3i2VAUPmN8hdr9xCmJLql30gkPkpxFPRa1+7HJpbfWON9woXfnYX0XfLcHLheHHFkHrDChwJNYhlIXaxfN51L4Y'
        b'nU8jC5Hf5qPdNqOa/ahgc78FMAf2U2vZRGixc/BDVwjYsDzAScJJoUtAZb52g4yjy/0WhpHzQKWexeUOOo6kvImDjuO/HsZsoI785QY4MEeo+n0jRx2YJHLAgOoYqtgB'
        b'IceUijJ9IghydHKsqWNzWM7wnBFxI9TOTdlDOTcHbHEGmvNKPQVmB9LTyXYKNFCPmxOccGEuN9Q4mbncbMjIl433l6USv5gxcdBQp5EJOi1AqxSuOcBVxqXZHB5K/Ube'
        b'eBiD0Lm+zqNrQ6n/SNN5BAe2ylA7dEKNXELdVoab9yiArCoo5TbAAVTol0R9nclYAmuHtnQJvnKCwzIMKotdRxsO9aGWMujQIYZFDmojUC2ecy3U64MKFgcpiMkIcrnI'
        b'TejAECsKkY1y/CfKSAfABQ5dh/2oaoGUVrIblcBJBYFehHJuIj6v81HxXOpU6l6p9L9KMg0qticxLyScgVNSaIOLpKg6XPdodAgyt7LDvloC3eo3QVd0UKE+ZKeTZTJ7'
        b'CMqlnYT7ZiPs0/StQWtaKlwO9XYgRnzmXStFVXq70CkxdUuiImuonwSlk1zFHD8iGfcEZMJldISRiRwKGdrHv6tCmAlesgwOTvIN1eXCUV0AVEmgXQYF6YS2B/f96aTV'
        b'kybhj26cW7AFHQOoWIAf7RYBCVJz4VygbXjCr/fu3XsjWId51iRP26+aM4ajztAhqABy/dRVQa435SIvcvENt4M83IZQOzmULPP2ITJUITo7OoDKTyHk5SSJhmuWwd70'
        b'BbickM0sSEN1J7mNTCMic7kEKftH5bKGDpRL3NZkBjWjLgO4tG1tegQuhfjhzxniZ8oMUaarVAcyw+G4BIrDDBeZDZPODkFdeMCPwwWv9Vv14oam6EO3ZIsU5esFGaDW'
        b'FWgf7IPTrnB9h3w05M5yhiMSdNhDjtrmToZqK1TFoe50YpvYjGrxfMMKQZYh5yYVodZwdGklHJSgPMhBB+3RfrgOJag4bHj8biyFZw5H1zfaDkedqBBlo46lW+J2wH6R'
        b'mx1uRtFouOg5JGA0nKT7Bp1p95KH85MFTtrq3LJtq3ckR/lysWRetFgbu60d2gsHVB5Wbw2G2xbolEWbRNMiX/CmfLmurjpjxhjLPLh0EkcxyUmfvEK1HmdjgD8sXbsJ'
        b'laNzcA1qeTdCPT9rEv58Go9IRQSeJOfgSPhEqFuJG51pEYb2xqLc9XASruhuQN0m2wKn0YkNPea22hopifJ28tUxsyBRNqhJjv/nUD406+Fln4Xqw+Q822CyOOgmMwAf'
        b'GFDs44h3CTy8Q6ViaBrqaocu0A0G5Y2a6NeHqhedQGW9dL3ayHrz5Qbx6Joo3Z1uUDuDtLmn0TmdwPCB7mlUloRbR/YMyI2FbKIQ8JywKQEV8x67EtOJ8dRkvZmDN+64'
        b'wgA2/V18fZxC7Gj8wYC4A2+sJyY7ozqy+JeEOC0VuG1hxtugAu+eJE8eVdmibkZA74NLQsXraXgI0z+WevsHUWJi52BpBnQEe/sGBDo6BYYzjmONUAS6M0NhiCk6g0p1'
        b'6QS4O0VEVWfXCUUBGYI7Pk8pR2Y8nlan/ZydKCI88R5JoVVAuXifbUoPxtcd0+aGBskDGFB9+LL+AS/4DfF4wFmUiQe2HApX22Cd9wo67T0G3fAeMwldEEMtukiY7bPM'
        b'UDU0wjHqwk90xuusDdqM9aRwyQL2GUNbWko6z5krREEz5jN6oGNwdGMo2bNEHL9yO5zj4By65pFOHJaoS+ztJ3eimncgbpZdv3QEbs1OyLKRor2oyYVibSXi2dwTiorC'
        b'hmNpu4jQEenY8+jInLV0y4c6MaqRZRjxHG8yDg7hCQJnktmIXzAigVr++Mp0LngxVgVPmjD2o87g6epIHh4ubedkKwVoGTmRbvwbFi3HDyk9x5nrqfN4uic7d0rdzakP'
        b'lhPwFCxZy7tY+bNtvQddSIYCP0plI4ZKlD2KR6eWTWVMpplQDef9lEEi6Kx42iTOwERkkYCPE5KZMQ0fYGfwnJZTVH8CyU88p7m4v0lpE1CmThw6C1doxAmcltjSvRpd'
        b'ghssJEUKVQI6iPbztOfFtnscVM69QLzjGawXGaMbMSzc6NomdFVJkAyXpxNagggz1iNNcHgOFDgFQskwuI57TLJGsMAbcxl97SHbXKCA+nrFUD5+Ko+aRq2gla03hEY/'
        b'Rn6N98nL+J3roAOK6UORqDFZxYy9aNxcHjXPH0u3Cd25KEfVRDwzyZLV4cZA/R5UoaO3GC6mE5vA1il6eIlTXR3luaj6RjZZ1TukZwJRli6UwkE82ckYGOIp3Org7LM0'
        b'xlGO9x29GQJeP+dhP5uQ2cZheM5eVkCbLidMM4HzvBOUSeNHn8wQKWqwvLBo5Cav0GcSh7iZt88p8Z9QPe7WpvKedd21PR/O32Z5sfEfHbM6WrvM3cpObQxJj/XLNX3p'
        b'1imLkC2t1WXLx/ZkThn9mGXT6BdK7mwtz7815+fvrj752mtTjc3K/MpP68eKu/KOfFlR90Se944nja7O9n6r56kPJ/ocL6valhe094/nN9oV7v3r3rMv+s4aO/Ht9dMu'
        b'mNu+/UrxoW/feC3ffuzBnheMdMb+Cp1nj1U77HC0e/ZD79O6dzZ9eeu3MTt8Sp/u9v1p4bDDtl+hZzZMM5bbj5vSWvfk5q9iy/8oO1pc+vbLXx/cJDScXhu3dVvMnBCR'
        b'1zMtz06RjfjBdotReP1LSW99fCUt9aVJn1r6ev2xyHrPMIXX79U1O3Xe7fjjys2e8IZ3Z0ydm17/3fLgJ3+9/Xzdwg+LFlqde9MtddNSvZrftgR/5vLrj773On46M/fK'
        b'u3feL29uGPrCq5/8MfrbfdbGDTMN478Lq70p+9Zv/Ogzh0eMnBYUs10vsbrut88kPl8U+K9q66oqMtM5lzJpRWu03e3LqfqJZraKV1Lb3rr45NvdHpuyK/d6fGjwYnPp'
        b'qupb73584KPipfEjjdbcnh7+r+QRh/Ijm15/b+4HixomtaxM3THi4zk/fuBrvTzj+8+vBB2Nbff7Nv+rTe/P7DbeUNDxld8dq5HfB3gta507/eInWwtWXrgVNP0ffxzz'
        b'GlI4XFEy5v2oCVdzRh7+dPuYSa+JP1qRVJgwfrRPlf2Olz/Nb5qWcfGT1EvCoksKu3nSa00On5QnXizY+uZScXf0DlG3bLXOO6IWfkvmF4/9/uWYuS/M/WPPhrf+HJMx'
        b'865e5Z3RqblXCoZNzSxJy/y16ovcoDSL7+SLc5//543Yt4//652rsysmiNuq/Ube+fO1NMM/7z7jq/vpWheFY0VSfKFsfHbLivNGa/XfbNi5atmXb3/2bXtjzz3d4d8a'
        b'vzF3jnw8C1ypgaMTNCMrJmLpVEZCK/aMoUQdUOy6nZquhABUQGis9sJVGnKyUB9lKfctW3QUb1vB06mvf4cbah/AqS7G25IUHyEtNPrAmoTbUDtaF2SyoAspahcy1ik5'
        b'3UvR4XW9eynKHc72Uji5mrGZFMAFIhKo9tMjfnQ/lQMLA0KH8UuV9YYKoWYo5mQ0VChsMQ18cY/3I0KBHFfUrmQf2ebPwnzqV6EGB3tndBnVyiEfHy16K/CShxZ7drkV'
        b'VWx1IPR3eagKqhzxnoaKBSyvV9LLNu5wVkUWA4dQESWMWSpK8PBMm0hPclSPRc0CGq9XEtQr0Uq40Yaowk+M5aiL6DILqClULHFwxk1I9sGNkKBzwiTonMICaq6u8iGR'
        b'QrDXR8VWA1kJ1CqMziXCFQUqkqYYwiUFqk4noXxaInegXYJ6oNmZ9pfxsOUOfR0LZnHQ7iNCJ83gBrMHV6Fzo/xUBuYgOuim6NgoyBGhQmuoYN1+bAh+Z8J17+JENlZ0'
        b'FWr8dDnjINGGrTPpXPOGyzKHIEesxRDWNF1DuMLJoEeATnREn/ZfUBQ6gfsP6rCIqSF6oPwM+uJbsCx6WHnUoG44R86aYTtZiFSHFA7L+oSPxRiwALJ96Bo1UgRBWRgL'
        b'vYHr6JC/MvSmZFsaORqWeO68bwAJlsaqOH8SQIIfP0k7ZUvSfFXoUsDQ8L6RS9COqijj3SZowp2nDqQxRqUslqY3kAbaJLRzgtFxXTzgvtQyDzXb8bw0hkxREtY2G+iq'
        b'WDmXRJgFEL453AMK1MbJEgU4is/Iw3RSY/XjUKLqcDSZRg5HOz9KFoeLOGarFiSsg4kYgapEbP23oBMOGmIEOgLVVJCAkiTqM4h0nd5fjEDXVvdKEVCeQoc/2GsEbp2T'
        b'c2/IkiUcwMVJzVbiFyCKgPFUvHy0dbKu/mCW0BTUwdiCqlfH+Pn74E0IHUPdIby9H2qkU8INHVvt52gX66pm0xO2xVrJDf6dOBv5iP8i5uy/EfVz27gfwCY1dYmJjbC/'
        b'qctdIkgpR4wJpSeS8MI9kkfG4nwIUp0RjQayJPRF+BsB/xHfk4pIWjq+U0Sojgi/DCM2Yn/Z7+RZUoaZQIj9jAi9h8hMZKm8S5/+ayYQ7HADgcUhGbHfRDTWSBCIyeye'
        b'WBD+EouEPyVi4Q+JjvC7RCLclegKv0mkwq9iPeEXc30hU/hZLBN+khgIP4oNhR/ERsL3YmPhO7GJ8K3UVPhGbCb+2sBSosyRM6BEfX1Mb/26ihkMWXASCxyiqWVTyI8Z'
        b'NC4pdmtvDENvtlavR8Pi/2zE5VKNFi5WtTC1VN2oKer4JmqlLMG/2g9mpVz4gjZOw/t1lZynKWuBD3CxEicrT4GGH83Ful8ueu8NQUtMwoK4NMJbGJmQQOFUNXiCcQPj'
        b'ScsiE/qgrDKErpgYBkEYaZMYu2VAoSzSxS4iYsnmNJ/EuIgIm6iEpOhNcmclIq4qyiFdERuXnkBCDbYlpdtsiWRkijHxhP9wIIexZiPiE+mNcRQ4QJknGqtgyaMMFtGG'
        b'ADzZxMcoHp6qkOAdzLTxodEGeEYq4gnqLK6HRB5E2kSnK9KSNrNi1a/mExMRISf4OIMGaOD+UfUH+RifaJMxzZnQZC/E3biFdGbahsg0dWt7Y0C0lqh8NwqFS4OZWKQF'
        b'LoAA4/bpIlUa7vrUpPRkipuntUT86mnx0ekJkakslkTJbc9gHBQ2diQN3hF3Aa6WoqxsS8a/xqZFO8vpIAwSS0I6NC1WNS7KcaexZon9OSmVox+TRJOAkwmIsrYy+wzA'
        b'AzgdeU4bp6N+INUf7aF9GUtnkXBhqInms3TCYWZdJ4sZlW3Agux+uDowCYIlQEDdjnR/esJPj1KaHm2kImLevJbiCpXDRnkPGZ+yCy6EoGx03gNVrlrok4bF4VrUKp0T'
        b'6DgSy8m1UOMJB0airtHb0VkTVzHKpbah3D0+1DjYah25MX+9L5dORIEVa9BBqrOHElrekmWQGxRGU5R0OduNYqzZF0XSh782ZbkWJjsSHF/duYaLT3z9FV6Rga98NP3j'
        b'8f+cZbTP1cTrxWnRP3zl87RQ2thmYjn/B8/3JpctaFoouhUz9OfAfZ5b0tMCROVLGldseWHXdwu+DNh3M/GnSsWPy37TDZzxj9afPw4pM/1nWOwfEbn71uzWLzhcAkvb'
        b'up//xbvquaKmxRtWzKmtWhW1sO0PfmXmsBcct8tlLAS/cY0F1XRM8XurwsiJpgNHt6YRx8DC2V5zfZiuQyL/i+Fg2nQqfASYDerBqiAyvBbJZRc6zkJ3CtBRyqXdoiB2'
        b'WCc7lUHKFEpFqNU9QsklvGGcKqcHS3nNSn0Ii3QnqSMMlUEPOssC7HkO60w0wn435DDJL3fPBji4gAXZ0wh71OZHZV5UgmrnOjBaS8j2YLrCdThAmRZFWB87PUBTg8Jp'
        b'YiluYhWL7z4/Fr+pSsxVC7nooC6L0K/NYMTOHZBn3TdeXI4yNcVc1B2v9Nc9MG5Ej+T70fVKBRxCU9hfwMEiznTKGyyIqThhJKIhzbxZ/2ABdVGqkBU1tMZ9ghXkAruj'
        b'94gtx7/WiZUkR/2PWC7LTJtLd5CGkJhRfNqsw8dNH2wEVXrsYNGGolzRQyXHkvP1V7GW8zU0NlEJmtoXkT1dwc7bWLrj4e3Za6GPR6gGyvpgh1RsVHy0Yl10QjwuhXHq'
        b'qmCm4ghsZPQGZ3qHsxf56UFvGwy8XaNUZd/MpPGJjuoARQIyrIilzUxKjSFf4O1f6/asBKMftA3Oi8L9IyjQXHpyQlJkjOrtVR2itVCCZKoGjiMnhzJ0V5Een8Yg4dWN'
        b'0n5oPLBVHh5hEY5/99Hwv/2oz5K/++iC5Sv/dq2enn//0YV/99HlXu5//9FJETaDiFYP8fDkQUJEfeIYRw0TdGJjHG3sldPfvk+cad9AWBoZp10yGSy8dVFqJMXr7p3D'
        b'jxLJuozIsmxXyJjk7NpntdAIXIaSy5YTrjAjPvLv9dTCsHAtTejl3CZ7DGsHW27xMQ8Qv8ScBlusWvwawii1TZ2V3vu4Fyb4j5rHUS93zJQFChlx9Z/kUKUrqoa9Y5lX'
        b'v20iPjjb0mWurq46nODDwXHUBteoc8cKOqPx6X0K8p2JheIQ74eI/4AYLkQJ0OIQuDXIV8AX9vLT8TF+lV5wWYvOOATi8/kItWrk8rPdYuRi6jdZgmpcoQ3qoATajOGS'
        b'Dicaxs+BA8CyoF1t3aFtPZY6WtOgE5/2cJAfswg1MbfVwZRYhTscG41POz6JQ51Ydmxk4RB79aAWX2qADmN8pAlQz9tbLGEerTq4vAX1oAMqxz66NoPGSRhFr1OHKris'
        b'RoWjhirDGaEbilZDG+oQaTTQS8KcPnWoEp2ANue5mg2E5iRaVwxqHqfw89RoRIoty0tucR+vcJ/upGo4yvWXi1jOdQux4eH+6FmqUdswT1pbABY6j+NrnVLN2lLQQfoC'
        b'XqjSSrbGK0MPD71Ij3dZ78f64gSqQFkydGqEIUGPETny86B5A32zudCEexc1oRtwWWbEcyIDfp4cytMJ3OEwyIvxI+JuKA3oJZ5iLAFzcAqV78TidSHsR9343WvC8C+V'
        b'uItOQzmWMytRN5yHKjMdOBilY4h/BKBsKJxtMwTLiWbGqNEQHYyfuFlPrHgPV3Hh8yfWPO+3Cc030f22+o1fvXeecTK/62Wfe+Lka1tfWWg9+x9mn760PUURb/Fqxfra'
        b'nFvTfhr9wZin1sbt+SFq9ieVbeXfL1jbOM7Fd15M6GL74TPyh876qbLgSNHF0KJvZ95+5Z095oWfzD57JebJn8N/r92357XvVka8P+NHe/uihhe2vO8/3tpi9K2wWS6H'
        b'cqM8v/nJYPibAR0x7y6x3tEyva7ZsHTNY+WHDCMdXj95MSrjFdNrN0wMv5qYWrdqTnZKs6LwuZEJL13S+5Lz+6bjeITxllXPtz55s+fE5PMu5xXFr35c/devhz/4U2dm'
        b'0NJTMblycyruwsUhVr32fU62EtVAGzHwX1hIDZZ2a9FhKBChZs1cW49gJsXXon3oiINGkLOBIypAjSJdyxlUisfLpiHSL4gfrpTjF/C0TCi0gDaHYHSNGImJAXk/D/sc'
        b'PZlDoQSqFVAAZy37pMmi9gDa3A1Q5+6gTg8lkjk6hg5kQD00s8cvzzZ1IDZ/Iu1KoUBA+agaZc3H+gOt+bT7HIVsGSqGdp7joYCDRvwSx9i1EnRmOypIToFjU/DUhxy8'
        b'2NaiE8xs2w2H0Rl8UWfLFAm+hudaWTC0M0fEGSxSX8bX0FV0egopNo/D8y0XWpg5/JQuHOtNRU2EKlUmKjoEtcyL0DIP7VVkoCxoJm5uVM/BUddQpjWcgYZtClSIjktQ'
        b'LmlVKQeXw9ARqmw4z4cbigwoQrVGOvixBg5qeH1qpHWeH4b3i9gVeE/lUQsHx/BVeiHcAp3HNRUlpJCKqvBQbF1I2+AEe1GWImM+NKfgatAhDnd/VjBjna/E22U/lQnl'
        b'GzKtCa/fpkFyLe8T6CxWYAmYqhQxWlUKkwhi7zRivF/3iCWU2E+JXVP4UyoWKL9H7x9CbEwp4AV9vu8fMVZFBHxdcm+7ad/IZVy/Ck6FZkkaaIrQqRV9tBIai4hf55Ba'
        b'E6lQJzMexJ8eH1wdMbmiRR0ZrCk8DTJKfZt8HtoPxeq2eF2QT+Bt2TqP8JAQr0APH69QhvupRre6LUuOjE9UZTqSXKPb+hqpgNSOqU7+1MjTLOyLgkVBsYgdk2pa9P1Y'
        b'64b9f8kAnxpM1ECRcgJJORNdfREBaJP8aSSx0hHmY330niD8PfhNE7GJiZFAyOAE8dR70m3mvHSkOQuBwsp1HaqWmaHSviYInhu2WBy/ZuGAgF4D5b8Kd74vOxwB72LA'
        b'XTViJXQX+0wAvPTwH/KZAHkRGC/2fe9nE4KeGTOEfjaPsVB/towZij9b0c/WMcNihseMqJER3rkcSRwfMzJm1H4pQe+s1K3kY2SVBpXSSjPyJ2Z0ka6erd7YGLccAg4m'
        b'wYruuJjxFOZKl3K2TdzPxdjFyAknHXm2UlYpxAn4ySH4r0mlWTz7zQyXaFapV6kfJ46xj3HAZY7Vc4xxJ+BjpNQcvRzDHLMc8zgphesipevRkFoJDbE1jZPEuMS47pcS'
        b'1FAxt1JGU0kn3TYji8WDclhQwLe42NS77n1EzYE3KGnXNG+664zl1pnxiqSZirQY+q+7q6u7+0wi/s7cqoiZSRaPs6urG/6LBetJctFtcWBQSMBtsbfPYu/b4vCQxUua'
        b'+NuCpxf+qUeqXBcU6L+iSZxKLAW3dai6eVuPgf3G4486cVhpVjxKtW6kWnHqcbLiTpAfJ8kaFvsEhjL8x0csawbe2vqWlXqWFhjquXTB3YUb0tKSZ7q4bNmyxVkRv9WJ'
        b'KAKpJO/VKVqZN+gcnbTZJSbWpV8LnbG64OrujOuTC73lNwkUcSw1noAq4g7yD/JY4L8O6wd3J5BGeyz0oS3E/y6J3Ea2vRBiO1ak4UKdXSfjn3jzI4U18anLGC7jadJW'
        b'g1CfwMX+XusWLgjz8H7IotzwTn28zyvfndbvQY/UJIViIVVc+pbhn7Q+QLGeluRGShJ6S8INvETKMu7XH3eHDf5Sdy20dp5c1qcUMt1S27WUPSO1k3zbr5AZtJBJqR3k'
        b'2uCVu911eIQ3va0bExsXmZ6QRrufjuX/e9kjTIG6AVmrWdwfHLKTcdAchZrid6fMYWklL5y5RdNKniWgIPFf8fbts++TVnJbSkhf0/CspkKHtiQ4ml+ymKG19t1NnFXP'
        b'Dp6d0INfYw7+pLDTKgVwWQZdWuSA+9XVpMtObIWWYztdfXaT2fkZaUtY4ICcBn1Vz5IgWJrTwKkoSRkcW5y+Ol9B/2HzFd7bq6vFnunDconjt8dqWDUZ7xBzP5E9+T5W'
        b'zFAVM7BNMmWBoCKMYubAG51s+q0bGztPL/n9byPr7oF3zLCxs1fEE19WxjTnqfYPUSRbyjZ2Ht4Pvlm5ZMnNjjYPqmfw7cTGzifskZ5wu88TD7szkCL6N3owg7HS6MWs'
        b'QyzNW8k4pWIzGOxJcnyyx/pPm+TU+KTU+LRtDDbYzp4cyoTLixzL9tptiPbksCb3kKPTnhiM7cmZZy937nW3TnV2d3adqbxFezG9nllXequy1N6vp9KvWdGDvRiDpFC+'
        b'mhbACdY/ExUUc2LQ7qHuipl9cQLoItMOH6HM8x+0Tb0YETPVrLUDYSAIJIPaOa/F907+w9co8SCx4VPbKQ0MiI1MIxNKoaJl00DVIK7pQcAGiP0Vl7MlMlUZR6DBhkF7'
        b'xyY0Npa8a3qCBtOb1qI8FoR5LQ4KWbGO0A4FhXqtI4wzobSVah8+458btJPYJsT6hzJEKUFaVOOmUt+UlmPtLu9eazL1ULASeo299v32FPtBgwboCCWzdapg7HX9thh7'
        b'9naqW+ITtSMhMLwNLKCqSHg3RCbaeIWHDGIVT7QJ3RKftj02NYEOXNp9Gs82xEHWEl4wPmmRCdvog4PvcPaDz1klUAgbkF78EDLzlUOixhJhDqpB3iiNxUBo4Ir3ebYP'
        b'DsyguxYtaYDHAHePUopSqKZvv3K1j4mS0LG3XkqkGRWbkJS4npT0AMs6kUr0BohRxoHULJsSDCegAi7DMT8ohlIRJ0Adb7cQVdGr0AaZqIIGPqB8dEqZVrgRdfYieUIX'
        b'tEgUhjooz1BQoZjmQWE6cVsbQgGUksR8VAid+E8byhNzG5MNYb8ABWucafI+hWXo8dOAMnUyIwbk+0N+Buj4CtwUtM8I9sN1VCYXmLn4oL0ttElRSa9JeAEUUHP25GDU'
        b'IhNDndqOjI57p4eQZ7JRKWigwmqAqqrzZZINDUMItKudU2C4nR3kQ6GLjQHkOxIkTwZU6kSsfoeH8KgVNS2ibXGGU8sVGRZwBC6JlfCjcHkM9Wa4J+sqcxG/n+q5RMKl'
        b'zyGmg6NwAZVpYpJ6O/sGQB5+aZcQyCU5USdRlygE5ZGEOriKzmwbz6EbYhlURXvHv/3qL2JFLS7GIbJmfNFFo73zDQ68OSp5hOvRX82eK064+catqiuTja6MPKBn+eKH'
        b'vzjdCfjqsxcmvPvaz9/sm2+3foXV3kzByHr296+0/RY4d6317pPyslXuFunN/gmVmzK2XHxl54dZ738dvKHM8Y+AqZN/qDB92fmDdyaMR+8Wvdw5bMnaPy8cvqn76/gN'
        b'7amz7Y9JXwr3XXkj9ujuVw8lT33tx6HPxIcsuu27Idli7bp2wfn6Ez/LDaltciW6PsPB2ck7ZRoNjD4tuELjShqsu8Y7lsEnk3RCR/y6legCgVA2ChG5wXHUyaIwmhXQ'
        b'qTT0Eg+OKiwdbtgzq2o2yoRrvcHy6OgOdQhJ5Q4WLX/KDI76BaEb0KA0P9vNpgZbA7g2VDUfN6MsVWT4fMii0bPbtqLWfqEYUKtDoCuToJhVng9lcKrXpotf5aLKqKvv'
        b'x4AKPaYNACpcC8X+EhVQYQm0s1Dtbut0B2cfTSxJ2IuO24jXmqMD1PZshquHAmMo0bTAj9hAuykBFROzNBSjw3QBXsbXA/hFqAguM5t22XKyvIshF1X5406I4t1QNhzt'
        b'g0eh/2/Z4dTwdwsH0anMdhJbnEREAl31CRgesdLdkwpinoWfEiA7I0EsDCMhrve060SasHapKbw223JGH3i5gPvpYqOaH1YX+xtQczrrKMreYDhYRfgTA5rTVqGa4dn5'
        b'ISTh/iBxxGIV6r0g5LaY8LfeFhMqV7mutghbFr9Kwllv6yoZv1Of4LWkxRurTpUlnDotnimRBko10pDheucYxxk/YvI7CY5p1KZMLoiJUfTlrFYdploMfWoxbKBOGmcz'
        b'kwiJMyPUKCURWjz5jkqhRo2tReImB4aZ9udfZPTDRFfvFVXTSE+mKQX5h1KRlMKtmqH3QVoSI+hiz2qh0Y1U2MQlJEUS84EN5YtVEmIOFkYTmdiHfK4/++5greijOmgj'
        b'x02L3crk4jQ1n+xmFvM5SBAnvic+hgh1vV3RS+HH3sHGjvLKk1ejQpttyCJnZ2db+SDiJguGoAHJkWQ2abBKq0tmtJlMDO69rrU89TO9LJjKKaAM1OrLiam1DLsQr0Ve'
        b'xHXjtS4wPGChV4ijjUo7YcShgwZ30QjkwQlkk5JZRPZ9StiqTeEbhKn1PsWR/9T6IOnh+6lrarw35azWWpqKFlybZmeDe8UrJHCB/0AtTnvQ8kNqdioeL9YVakJlMmGV'
        b'84asC6wMx1LO7IiIwKREslPcJ5p7a1pv7ZRul/RRZAKJoCYbhHrqxqUmbcZdFRM5SNh1QjozoK2Pz4hNVM18vDRjSFCPXXRSoiIedxcpCXdcPP0W9/KgDWPFaJod5Jqv'
        b'qaSXjtoYG53G9gPtik5o0PSprm42jPCWvQ9pg6MSKVT5vtQOQNYm3hS1lhOXnkrXGl3tjLh2UG2PnUozbUKV2pWKbp4Epm/DtSQk4MUXmcp0LHaz9r1FoUiKjqeDoNb1'
        b'klOTCGs86UXctcrBxguBTXvtnalBxmgTiLW+yOTkhPhoGm5I1G66njQD7bWvHQ8la30v+Ss5sG3s8E+5ow05tm3sgsJD5GQwyPFtY7fQK3CQdWivkTkwVW7/EPkM6tit'
        b'Beqtvh+N0v1iQvuonFKtKudoFksfYIryiUqZAT3+KqCaNtRBJSGqH8XOxfrREkMdzibCP2m4sZIr4+q8OMKVQXRMdDKREAmc3bWIqaBXUSnaTwOgpqF2CtdSiCoiWTa/'
        b'HspiCC87oI2AvKBD0K4bRtXTYOvI/sopVk2hUhdrpwrUQ8P1odQJkQxWxtsgxbeHKQEL/Jzsl3o7+oYPrqMy/JcLXpA/0xQVTNGn78H7RJJEdKafomxLfh4cmJ6+jOo0'
        b'Y7Co/mhV9fLhBNupQSzkEm6m32hXc2jFndTIeq8MHZ8iUyq/BuOw+nsYjqZvI1eyFhMuBoLr4+QbRDRgVpAOlEO2/nhr1KRPVM44qGJaJ1aDoAZfO2WGdazTYehkTDDK'
        b'W7gbHUF7UTP+U4f/PbBpKx6R+oVRa1H+wtT44OCNa1PHr0bVmzaYcFA8ZwSqWYLOsIi2vJggGXQkGwicAN3OybxLWFJ6OLnQgFpNB2sWbvwBfRLGnjcflUVhjUWzQdlw'
        b'CirJZxLrFWEMOTYcOhdsarUKXWKOoyNwAhpkylAzVGvOu8zZlk6mL2rCSmOd2hQgX6qE8UlOTw+D0mRDYygPU/Z7r5WAU4QR8wAZHiUbjBryBuuOjVJajxHkWpLYsnWU'
        b'4GSqAerUAFnqwRP63ACWDvJgWJ8xhXaUY7gYyjdRu0kkuoFa/TSJkYrQuSV01uBi/cgXZCpV6Ch8Ub436jHDEzwfKkKwbp3Pw40Uw8XOcIkCyaBurEA2DijKuxdBf2mf'
        b'ElG2DFWaj4d6C9SAzlhaiEjaRTKcM0Vn4PxuCrdpt3mZCiBJ451EEwRcUyWu5/JsPD578VrLZ3F3qDyKg5wQgxBXlJ9OlAk4jc7CAToUqGoxM8z4+8h9nZy1MZqoWmbY'
        b'd83gLjuWbobK4KwpDQuEnlhcuxJWIti71+Tzd0quhvwQX3Pcd51QzMIpc9F1qKeUM8Te4446SMjYSXSYRu2k00ipi1tNCeEOFKKC2f35dvAL1xMux3jPN+6KFFVY35K+'
        b'0hkQfD3xTVeTCfLgy05PFx87MdXnyVM7fpk7/xdubZGQU9/KDz1p5jLHKX3v6kMnS2w2j/pDvG1foLV73LdHnnxq8SL+Uukvf7713dd2Ih+v8wEHCxaGPWv67oFV0w5M'
        b'rn71ZX276obTdlenPnn21e9HWTd2uJ1btWZi+XMWZ2r+mOzw1Y3y8//6KHdKrOyDGxfHDE38PCtgRduKqpkHTz+98qfff980wcpv11KHjxoSmj/LruM//6X45ZX3Xsm9'
        b'W1l302XDvJMWZemvXI25dTK8M/G38dt9t1od1z8e+ePyYU5m93S3utz5aNzdm9++ffGnaXcmvnj42R8+N9pwY8c3m4d99E2Wfsjh20lvHLD6qePthOF3Xkqafr7jqTmf'
        b'psouHX7qg9ZbZl/v2JCzwGP9rK1bUnTz3n1i2T2POZ9vt7qrW1P3uelbOS0rI068P+dsxp15GTsvvFH3wdLf119M75icFrJ+aHTWpam3PL8dW+4XdPf96ZvWfPWPS0e/'
        b'2rKt4fxfDX/ud4r77bk/NiuyykIO3FpQcB52Wd1tCHLQ+Wiy/ySHD9IuPPtJa9GKx7/2/+nCWu5Q9WnPm7FySxbYd3CFQOxE6EaAiieB2IlQo4QRKRzGk6NLZYJaG6GR'
        b'xFQGR1gWE+qCBmUW06gV/IIVpjSFyHBKDNuEUCMcVIZdCtAyfAy9mgan5vcCKvTARTjPo6NwOojGXPqbhDLaFBVpCjq+iPGmRFvTVo+XEIsrNUzpGzJ2FgK3EKG0XaWh'
        b'q9BCzVtwFU73pWbhHZntrR0d30Jtb3gvyeuFhEC1jiwDqhQ1+TqoYzedUQcP+9B5yKIRi754RztN4IrQsaU+6JyYkyQIttA0jkYZJqKKpUqgirVwA7+YC15VV5khrEEX'
        b'1SptZiOhnDHLMMaOLtM0El23jiTEa6H/ICY1VI/qxdAWhvJpLwl4sakQefALN5F0eppKjy6zIUDlG+E4vsGR0MqJHQXo4NE1dAntY23JRKd3EascHDTrS/KyBg7QF5kA'
        b'XbyDs5OHu7fKvIkbVkObaQPNkO3n74PyJKjbpT/4kSu6InHZit95GOvJq2I6g7yhYqGjbxCWJ4w8RXN2jKCNhB5UBJ0k1QxLDHkk3YzmmgXvYUiPZ9CReFTgEoB3sKtO'
        b'ctyMOYINOiuXSx86u9n4vxObV6LCfqwksqIWmyC3R3+uAW8kmAhGvAH+KxFM8F+pyIw3MCEhn5J7+iIxTXSX8kKmvkA+kwR2Qfk9TakXzEU09R3/NREkytR4kntmoEOy'
        b'0cwEZnc0Ila+ewYkzV4gSerk2nZbLca3R0xT7zWipT7VN4ft4ftfM7v8KS0p5lqyy0t1VHl4WiybXJbdJ1psmw/xtoMH+8wlpj9i8mNRI1ycRB32I3qosJ/9ctHdiAHq'
        b'REhsItZkFQ+y61EjglJxIWprpMJmeYD/A7QTU/x31ADtxDEwnZiGZXhLLfLrDd0MVgPVKUHqCpbZ9YfAMEJZHNSg84YW0AHllFwPy/itnsqzvh2v/f6HffM8hktVjko8'
        b'FdNQfkavm8gaGmgRe+AGqibyRBoWgo44433YOQP/8CWh6+PW6kxLEDF59hrUw0ks2flRUMlReNcwFFPgsRCyBQC175fCQdSldO5BGdpH9azASQJJu5nvYxjheH39GI4m'
        b'caSiHmMKUIkl8CKsrsBxDkuaPUZMXM+Hc3AWKkQjIJchS55bQ9WslXDJSobln2I9LO3w0ES8gNmptH2b4TLe8OX2AVC9Hh8I23jIiphJq/JGJwhaPD5rAnU4CVxfYSkY'
        b'oFPQynx5V+HExlAoEnNo30R85nAI77LH0+nBWwtHZRRdDuWjDlIfxZe7ATcYShuWumRE13GAvczXp7ClEtoGOG1JxiUNOk3hhCrf5QLU0aGYvwJaKKwdXIKSIJa7shwK'
        b'GaBmty1TFYuMsNLA8fZe42gjt0/0Z8ocHED7mMNRB9ooUpt1DNSGoqK0CVAZjjfogwS3ThrEw2VjOEZ738mkhBvBc1sDp0U450esZapv8PyxnCfHLbfjImxXWpixL+es'
        b'pxneVhfiIjauW5zEDaBpVi9GG05J0yzDy487ye3kY7gYPluw5mpVhM37sYz5GfEHEN6bBTGp/vGJsU1KymZxAv6lP+c0MfKvkXDcDwJdNpQXYCQqtyT9sQC605iXUk8l'
        b'G0M5za/gQ6bOwEOYh/JmQHbG/EVxKT6puxNR1khup7sJuihBWfTVot0NOTwVXD8Ki3B8eZghe99kn6GcI8dFzLWJWL3TFev/ZLFO8IS9C+aqcQc1QQd90Ek6gmOg3Ykq'
        b'kwRziiqUvIsDlNCRUqDrKBNfTDEkJIxYcjLnZ8UOodXtc6fJZcv3TIjwLxdt45TOZFesPveQaQRXpylTj/ahbjod0uLdiP5oCtUsWwkd3UCn+sK1kANt+Jm0UbqcaAI/'
        b'By/0SjlPrw1B+6Yr4IwkkMiJgoy3QdWo9N8aScL8nvoMOQKeJT+e47kBfOFk7M7jsUt9gVe56wtsV8oyoMMYa0KtAmn9dGhBRbSJs6BCJsPrFwpX4/WEtTq82GvYUw1J'
        b'O6FtxmYD6NDFy60CX4YOdD2d7KRyUZiMQ1fQZTx7uWDIW0mfSMHdfElmZ+8wcTtc9MdT31dYOROdY5rSjbEiaHPxhU58QYeHUrx24BAqDY4f98QUkWIG3pNq3lgcG+5X'
        b'aB5uvuub8HtdDV2RJ9dvt7Ka+9WzmeusJJ7fzfv8V2vPx42fanzK4nJuaMCUyMi1m78M1q+rL8y7Vmc/4evJ31VYpT8eGP3+XsMdholpm6JWX/n2rVWvxEksO794S/F1'
        b'1zdbvvnCdajl3WvLZjZ7//LT0ZmOV2ZOjTEb2Wgw6zHRXN2Ecz/PfH9WZVDm+aamx2oFxSdhmYWJz70Zq3gn8OTsy7Mt9i1sbHr5tQVukyPcPtGJbb9hUt9m3lSzwb7D'
        b'wta3w7zy8NnafL/W1FNm7y03/GdkZKBX3Hcbl1w8eKW88eRGWce1ZTrZbeGu7fsnvZzw4quPWWyeMWph8cxzkQ6Jk16cv6nR9t32qm2vfxPa3uXf7rlqTeg7v9957cXS'
        b'8x1hN3caxM15ZXNA1c5vToVPeaXrqVk/7M55tbwx6U7Jkg8ui06/H/zdkYaiexZTutb9a5j1bx6W0d0nTP91oMjQ6t7ijWl7TrXnBV5Ohtxre3MNR3jBs8/MXlZb/MGy'
        b'J4a3fffBufEzth499/mf8SPvudzR+zJD0Z396sXbf64/o5vukDD8ZsZbw2N6imdZx3/DvS5vzry5/6jl6fe/alqc/+qN2Ns79UcoKlpniZt+vfmyh/8mr2fn2sW/dWvJ'
        b'ohCdt5w+qxkR/sGV7B8+P10fvNHlsOfVdKPOqg+H7Hv9zYhZkV2e1dY14kXHuK7hXzpOL35L9Oam9NN/TstMzPnK78kXrDZ7fxJ4MmOe6c9G/9j1WPOP7y748Jh84nbx'
        b'nnuPrbNHXQWvzf/M54c/fvP+Jer407+P+ufb+1Z5trjMiP5G5lA11fbNLSO+2uN3VLzsrR2ltfn5oy5ZhF1aa7B3e1Vb+i/v9NTrPZ1SfT16wgbxrTO2TScf7wnb8y8j'
        b'nznv6naN/pmrnDHjRd2sUchgz7f2H315T/KD657a5ybd7DYy/+Cri5/6/FX/tlyaPrsx4tc6h03T3XcXHCn7rDh55IWzb936xPX2iRiDXfkdMT/NKh7R9torjfuGTHpn'
        b'Z/3zz9S8djP5r8ULP5qbbzHv47nON9ou/zRnbEPitcUffl20peb5kZ8Lv17bwT37RcTxO9fi1iU2fT3qH07Dv1nTGuS7OSLm+ZVfvrDu41lBY5M/qX9mSuueO+u/2Gr/'
        b'TEZpl2dPxVM/r3p1/M3fV1+JX/TW+KbOs36FW3xeH1l4xS8kKfyw1TdDvzYLbvmsPO25c36FvzSnPT0V/7404+naBYdz3StekX8A3futfnOpbLj37q33/HdMSJ29O/LE'
        b'R8Mj5r35i6LDdMZfiSfHtta1fhL55IfjP3/qdclfeskTrN7lu7wrVuj2RAwvTBiif+Fjrzdj5qVee6vIJa9hSHf7MIvtH79UXbf1RMmQLa8/0zqkUSi36Dab+eePBr86'
        b'OV8OefZCshtMvLDj8bjkjCE7M74NrHUe+c2ko81PT5sz/ONlizssAmp7Rt7bfOTmsOf/9fOCC3UhI+955O22+OfivWs/OKz729yR387v3pHzy+vT/nimsza8qvPXhn/9'
        b'81DUtOCcsN9e3vPRc7OGVnvKN1EwDLgxcbSaPIVosbOxLt3LnoJy7Wn8gwVc96earOXkXj12SjRT8pp3oKNEyUuG0r5K3hCsyZEjfuIeaPODItSCzvqpbzB2Fa03gHP0'
        b'hl3rUCVRSFEFdKjZUKnOGjCWIrZtR83D+2us2UEqpRUrrFMnU618O+xHzZQ0EwqXo6OarJkb0QGqDMrQeY7BHRKoQzdURtAOoQIVMuy4uomwV4GP49yRvTlJhnBDNH+D'
        b'JdVKd+Iz84jCGYu0TqmBciM9cp630QgcyBNxk6FZEopO+dNOC8MK5Q0/VUaoZCEcXCfYL/NmQTV547f7TUS1/vZYhV/DT8OH3Dn6kOvwuXgsXLAYTYAY80ajEmH8WKhm'
        b'SYxV0IgK/BztvE3m9mLDeRiyBNRjqAGqZZDrBBd3hkOhn4jThctCEFwdQrMPY9AVOI8voy4owbfgG6ANHyuGKBef/7gXzlN93NdAQuFwCBeniBMTDFvo3kVrn4zaVrLi'
        b'xQZOPrhyfWEZlrwLacfbjkbXFPY+WILe58GIWUsCdTkT1CpKk6BM+mZpUDPXj5FzcjpovxiuC6JNKIc2PmK+OZkil4JkqMlOMnIppwedBJa2G1XS69EjUJ2CQEfq4UHR'
        b'MYJ9nD4UC1DggZ+nGbQ3UCkqwa0b7uOkJ8cCCXl9Q9QtGuK9gdkpWuGcA7W1mMAZVaos1EEjfXwEavEho+jgjI4Ok+vb2RNrhpmVCDIljvTdo6EyXeZM0NiPbpRDAX55'
        b'I2HVPLhOxzJhB8pRBPIcuoR6qDzQOGYrRaNJsMKSfhvplIt6BIWGgl/qcKaWIiwy1BjQKK7RcAXaYe9Kvz50o9xwtFeM6qFuJ+26MZNiFc47vH3QBQN8B8cZSUTzoM6Y'
        b'tn3KbgNohBqZr5N/CjrvjSemQs5z1mHixdsWs6zYs6gRnSBf2o7joIfwrZ9Hh5nd5MAO3O1yHm4osa918KqrFM2Odqa9PhbqVjk4R6BrSghHNX5j1wIam2Y4b7rCx14O'
        b'9T5YQEKVPCqCq7Esz/fKCHQG92iBDofOh/AyYjs/CBdoqdYLoL03U3oIlDKrHaqBctrX89AFPFoU2nEOysVjRbAdoX4ibfEqdHiIBrQjnGUQ0amohl5ePmKuzA53QYq/'
        b'HM9quIinyREBz/i962mDg1LSCB5lWkqAE8/puQmoygJlsdVThNXZRpmz3B5rgrV4eeCWS+OFeJK7S+bP6CFGDpAroIsuzj4MidkYFYmiFu5mJqR2VL8JV5yCZ4EOHPJE'
        b'DTyciET1zAx4IRp1y+QE+oCUquODy6/i8aAXDGEPd2ycyCxoWNSsI1Y0YkI7aUo7UnfYWDzv0VloxROCE0Eej+oi8KKgwualiVP8mElekuHAyXwFaMAqBr22OC1F4bMG'
        b'yuzlqf6BzniZu4ikcHYrRbldEoJO0rU/P4WDKxxqmW3A1kgxOonOY30hFS7jCdqN1WDUww/3n0+7diTWno8zeyocylCzRZ9F1xjx8knUA6WK5HVqud0Ruuj722H1pt3P'
        b'eQoc6OXJJfbf4dDArHOHE9AhMo9S/V141DGF058voCZ0ypEeULNHzidp7IWEyR26yBrCM5E03hzvt3A4A86y3OrDUVABx0cpoFiuj1ocoYNs3pfwfdYmYnsotKRNiUF1'
        b'eONvU13SgWMRS3nIxxvNPmpnnonyo/yW+isNq7zLOilt4XJ0CZqJnyYD2vD44HOqyJRfC82erNuyoMVSQWyqFJCeR8eJP6Mdz3Z6tQa1TcFCPOTZpUEOXidwHN9hjJVr'
        b'MvbLZ8B+3GQ73z2+W+wFThdVCDOgGerZwXp26mwS54oa7IKIWSWPGlmNBVHMSHSJLu1oHw81iDnU2FIQcysHuvdAh+uUSNSuCJTjEwrvqso90Qo1i90M4AAdUit86nSx'
        b'LZ30xnB8hBzFE3cZ1sZpEQ1T8VNtbN/C/YVqoRwvqHY8K/B+e5zOs6Uon9jucQ+epQCpwlLeSQrtdGuzn4VqFXjA9eAiVne2EGsRqWcIVIjQiXTUQzdPHmWhboKNPmup'
        b'iC71urTZbNu6ZorPpQKXAGqSRYXOcwSbJUZ0mIaiErks3VDPOhb35xh+gYc1O1OPJ0OTwhKVQiHxFJjzY1dvZB1ZCGdm01M6dxQWVFLodUNoEo3H05ZthNdRuRvj9vCL'
        b'10CLFy+lhz6cVEyliGEukB/gKIfiYJ8AvFvT4FYdbvpsCTo1Sjmi45fhASsISk2kzAwqQ7RidZo7HVGFL8VKVgO2F+PW9gO0J9tsOLRIXdA+dJq2PzoY5cnobVEOTil4'
        b'pRAm+csiPJnr8BFE95hiq22kgcehqheDgtBnj5hKO3NkLJThqUCX2GIjTt9LQGcl0xnSWtMsPXJpI9SSXfwQj4rtPOnY+qJLqxSBCxLkqj1kikgPCsZTdLRUfKidVoHo'
        b'ukFun9ZTEF0PqKONN4dWHdb4ROhwSsE1kdZ3iNBpdHgVA2SrhqNwuA/UPSKYzATunmDdD5lFm7MD99xlGb5rB7pGkN46edQ4GjGudPzi5zJkkI9nMtoLR+hUl3JCMKGK'
        b'px1AUKOP4e3dF6pNefzwZbwIJ9jSaY5a9viRDoCz8/Sx4NNGHzZH+0VYVmpE1bSTTPGJ1CGTYzkHHeSHcZANR/H8Ja+3Dh1DBYpAuOgCVTFYcqAeEpONIpSPju6g7Q4Z'
        b'jR9uc8QiY+s6sv6r8XG2AZ2lU3YsKocjMqiIIAh0gpwfhUpEbO01jQ2YMFqBd3fI06PvxZYvlIpnjoN8uo9bo0vJMif8TgT3edQoYUjyHtoZsXAZTlB+nMAoLOvZk8mM'
        b'F+0h1IBOsBOnG2XiRrvY46GJ95aTfadb8E6IT2PGv4tW0OYUyIwO+Cxu2sXDQZQ7hLWr2QWdpqDIQVDTFxfZDLVNZmdpFV7T9Qpn33S5HuTpzIMiTl8QsIRfosvKOIia'
        b'8eFM1mPXGEKxZWxHNjZDuCqaga7p0ib6uaMcPN40Fhudns3CsadhfYJO2WzoEvlNQPnOAXif3sbPxq0spv0phzNj/BYRBENllPYudIz5IHNR9zxqcBs+Ug1pkoWyUYHc'
        b'9L+DeCt5wHUlSAXNqpWkUis+9fWs1AJ+rPojtZdSeGACc0yQAcUUIVCMtzrijZFQwGMSG858OOSaFN9F/pjje0x44R4BNhbuWUlH8MIPBsYmFPJD+EssJn6dcfw4YRh+'
        b'El+7i78zJPTq5AnhD7FEjK9KhAn3hEwjXvhTuGciHUXK+0vyjP4sE4FQshMoZAKIbMJb4TtGSEx4cwI3IhpB6hMJv5npmdDfybdWhlYEypm3w5/xdzqD1y7cG6FjxZNy'
        b'KYQJBXM2xy2SSoTfjPQkP0tlwo/6Twi/6ofqU9BkAptswNvgnxN4Ujduy1+kvcKfkt+l5lJ+u7UWHw7rfQ02wQeMnUbC8ot4tEZI8LARxhbtriQuy/K2FmfS4A3B1dNs'
        b'+cd4ko8cGCgX4x80sLzJoB+aSWoCR5OyQz28vQK8Qil+CU2iZnAmCjUGCWlnKgE5Zu448/8TlJFZ6m46SiY18bgd4EjQm1gQJAKD6P5D0P3PfZI8K0wz4qXGUopaIvDm'
        b'94Q5DIvESmxE7vtLEAn8qHvcnlH6lFJmGGodQwlRnX0pcYKmgV7gZq+UUF7TnAHZ9vrKfxVm94cjEcVIlZ/1ND7r48+yGAP62RB/NlJ+b6zxWQlNUqOnhh0xj7HQgB0R'
        b'acCOWBbp6lnrDYuZoIYdGR4zQg07QuBKuJjRMTaPADsypkiiNwyXOFENOmIYpxNjGzNWK9wIATnRhBuJk9vdNqbYPJQx2zM2Kj7trssArBGNq/8G0Mh0lsHuLhduiz2C'
        b'Qrxuixa6L0ytJfO9jvw4wz884sd0loLp/kgwIcqHpj86FIiqOprx6UagQFJbWFIOAe1IvUChh0K8AoLCvCgEyLh+8Buhnp4hsSl988xdUy+SF36YW93UOBmqhty1GqxU'
        b'NXhG3zbL9fqUQcYh9V1NBA5V56S+R97oDrk0WB1uqdfJPf893IyHZMLVYQmfcBp1oUsKrEhmQbMa288cMd8ptE8yk2UQ8K8N4wiKWQ26tj7ePPElQUG00fc2f/lFxFNR'
        b'W096Rz4bZx8VFKkf9yn3/V7r6au4Gc7ip1+wl/NUKvHEIn67A1bOGuFEL4IbHEDXB2ED7VFFhBC5eTApgcaF2BDCg+1W/dbZQ0JwmOGuVrje50SjUBzvaznVBq/wBhnX'
        b'1wjOBsnr+z/B2VgvF703RvKwOBsxtNUESICE9f8nQTZUS+MBIBuqpfXAO6Y/NMhG39U6GMjGYIv+PqgXWhew9vsfAeSifwIXyzWITCRpAiQPa5CsIvVj2sBTBwBj9Bln'
        b'JRgGOTgYwAU+POwHTwB6EAqFqiWPgkMRH/c/CIr//0BQqFacFgQG8t/DAEH0XbQPCQShdQH/Dwbib8BAkP8G5uToBIbRiH10eVEYBR9YAVcG4A9AORT5Kwl8e+1w6Abk'
        b'yODM2NHxH34+WkdBuIS/eVpOGMg/vbMhbuVjrz/+8uNvPP7q4289/tLj7zx+rfRY2Zjsi/vGHm/aJy+4uvzU/vHZTdUX874wcsseU5U1aSSXGWI4oiRcrkOtSyNHQK0D'
        b'bgg64KQOoV2JLlDblIf3Cg2EgGVBlJiK4gOgM7OoqSgmg5G3UafrVrih9rsuhwvU1KLjgK5AGSHMVllU0uAsc+pKFtDwZ1SypW/080aoUsV8/kcS4rWTJWgkxi9iAaok'
        b'dFV8T4sE8shZ71YPI/6MeuuhxJ9HSX2Pk/OBqYhXiWNa0t4X4paxtPcBNalz3m0HOeQG5LlL7h+OG63bb0HIVIvCmwhouv1ENBkR0uJkShFNl4poUiyi6VIRTUrFMt3d'
        b'0lCNz8rs9V3aRLT7Z69rqo7/v0hd7wvvpZR7lPncm/FJQRJr/5fN/r9sdpv/ZbP/L5v9wdnsjoNKRwn4FNAkN3uk5Pb7bBn/l8nt/9WUbJFW8c+Mgal68ZDrAZdVDGck'
        b'JXs8s6WkE8P89qhdLEIi1BvygpyU4Fzeo+GULxRRWrFlBB6LJJ+KSUpDgR66Nsya5lijNsMlMri2bWCetQAF8WtppDVqFKBEldsNzSIOzs9AmenEigPHoBl1MQ+2dnQu'
        b'PzhNAboEDlXACT3odo2kNPPuznCmF9ULcr0dWfIG5Kp4Wbl1E6XoxsIF80akE7kEVa/S81OJvOiGvlLqJdmwjlAcwAK8QmS6UDQTDqeTtBcsUaKrap7X8CXLnCZZLl1G'
        b'knp9A/xRU5g3Ou8d4OzkE4ALcRHQJZk7KggJ5UahGqOEXcuUUeH1kKlwp1wa4XCG8IAcnplOfOpzF8+CAlQN2RrFL11GUlST3VNJXipNExdzEahAFx1EN9D+dCJJoapF'
        b'qDLUHK6p7laOVRh7Sv3uq+J00ZmVO6nRz3YtCY3P2pVqhHtRZMrPQaUraaIF6oYeBzxgZSgPOrcoSP7IDd4B8lEpDZyflCGO+lBkwnHzIxxvLnXg4mW79XQUN/GVe52l'
        b'4SVzzPbON8iuWHNoXfZzSPb6dmH7pk3Xnp3eFnLHOeTbxxeMDejWeevlL709Kro/3OEy6b3KsQdW/LZ3QVii1x6PJ71My1e+Ij439Preeb+YfmY9z/tFqeiKbLHlU7Pb'
        b'u6R5osjNt/aPvducUN5q/eLNFqPwxAlTLbe83VD51xvlT7999Nnq6d8PScjbe6eoxfCfU8pnLXG+umjnE+988maR/Wv6c7789MXrn74+w37iE/XDG+8e6Yn5cOdSvydW'
        b'9tya/vH+W42vfmj0xge6hiZeI7KPyU2oRjAJ7YfqXoA6GuUDDdCVAC0LWJTe+bBgDV5uKI9XJnrawEnqvt0SixqVaZ5GqJZfgM5CI6OryECVavbrCeiUKhvTCUqZS7kL'
        b'moP7gI1BNdrL9BEoWcKiQHKhepd6FsJpdFGH0Q3jj200rsQVdbmrFJ0V4bxbZDK10qbAFV69QlBPijLNFHXJafiC/rTVvRG06BTqVmlDLIQWKhxpNMxQvAg62TuQZZqH'
        b'azGCLhHW3C74oyuog4YpzEF7aXZ5xzrGeUwYj6P9qCYWvszLz92XLP0LW+EaRzeIUywstGgJdDoEh2iygOBSymnPjYNL6xxQvrtvABsYrI8OmSiCoz5wkIXZ5KC2lahz'
        b'A8GYU+mPQ5Mo9tp0b3OafqmZe7nXWiP9EqpiBhLNyf6DeY/+D1D99JNJ9iMh+SUZjBIJ8Q+bU8+3EfVEG9G/+A5lFuP20f21Jq3JinoPk6zYm6eoM7iTX3dw2lstOYle'
        b'D6N32lzQonc+6L3+i2mJ6+Wiu2semJaoTWH7WzmJxFsxMCdxbGD6AjKZ66HCzQ9VyB4tLVGZkxiMrlCKUrxmG1Ezy0kk+YioFfUkcFEec0QyzhbOiWB/1GR6KE1cOUqB'
        b'6jdqpCTCuVE0q4fwmLbilQ8n1bmG6DQ6R0+DHAeR7xWK/BJhMGlTEssmhCu7IXMtyqYZhapsQjjtT0mfJFC7SMlkBZ3zXVBePM2uGonOz1Tg3QhdG8rhMxflLdhDK/fD'
        b'DT4E2egaSSZUZhK6QQEVIab4ohJVJqEbypNYCgZwYDI93bbCGYHmESYksDTCdFRH24YaeSxVoCyaSajKIpwMnfSp8ZC31R4uyahIQzL+oMSWJlUmwT77UFSkzOqLWqvO'
        b'64tiVGUhm4v13+CmC5xrROC++XNZRlul+diMbD6X9E1UxIgI9qVioY/VJ5wNz0VEbFwyXOffS+t7yGSwa8TQQpPBCIbICNi7WcaYShzxRpriEwD5w1Y5QpmSIgnKURvB'
        b'MiFRfXLUIXLHAowfKoc2hQx3lgfkGofFL6LvIl9raP41h0d4SURC09Jk9oKRMUNn94iWc5xNxOxDyeM5SpECFyEHTijz+NDR2L6pfLqWLKe1CxWOS4AmmrDHkvX8w2mZ'
        b'0u2SncdIyqBNRMJHe6Zxcp4OF2HjbVMkeKujdCNR67/Vnxserj9FUlV/khkViWXfLtQFZTTDTpldVwtnWQ5dPToI7SS/Dl1Hx1iCHaqZRqdvxLbR0CZB3Rr5dSvhCKNb'
        b'yxuCWoiJKhhP3ehgqECMXA7diHQg+XXCVnV+HR6sdiq3mWOZ4JI6ww7VQrcOTbGzUMTPfq9QR5GJ15yZ+PX0sCcTzReYfPV1dcA7KY/dae14fIJVhduMxcMrFDerXrey'
        b'2vfkOT7l0/ce22tl5P2M8UnrcYHeI36V7ebyhkxsGWHqbfPd2e2W1iY5R1p+Obtx5stfFL9lt6qs4reuhc/k7xxXd84l+ky4rUfZXaOd8TEvPP36i86tL1W/kHd60eZP'
        b'F+mbdtqe0Bv7zKaxqw6/eNXzc38fm7HR7pEZ3VZ502XPjLeNLD4VOfWfRvlnh10d/rG/83MTbZ8d/uSHr+W9wDtzQws36T/W8vTN9MaGe1snfPLaRLO1+5774fXcFUf/'
        b'2ePsX/jZNfEXP3kmG/8xec3k35aWuRs/PnnT8+a5WfNGThW9euq7aXEr9d5bt1n+//D2HXBNXt3/T56EEEhkg4iKgIqEMFTABe4FhL3cIsoQZYfhlqUgG5ygoKiIgAtB'
        b'lKG259q9W7tobWtb22rt3tbxvyMJ4Ojb9n3/P/0AuXnG3eee9T0n6Tm/hvY75r8bbJr7YXVsRlDEp3yGbXKsl3Li0YxrZ6yjX/71y1FVz3U+nZXyU4nkI7dvn3H49I93'
        b'3p01cVrw6MWNkmnj3y0IviI9Ub7ure9+j/teWh0p2lJz42nnjp+CDCL+/KbJcnfXosCtB+K2vGCzoTLaZNvLDWdiztwYdrPR4y2DlvGruW7+tm/Krk79jt7nm51+gyXC'
        b'JWvX/iy7tjIuwKjWckXm8B8nDL3b6Ff9tfNzP/g/NXTNOi/d9sp3Di35Q/RNdeKbiV5JAQvON+x5JmPJ5I5BHdcyFcHxJ3Wnvl09LH3UfIOCZ573mLt1vtGBubd+Hbdt'
        b't5dN+vJtyxdOr3vL7mdJ26+3/Icr1oxJ4CYUPu9SFyP5KOnEHZ3TgW/cz3v3arL1yaT7V7nmu1OP93793Wff+S7bEPDl+RGZXKbRbdsHZ7bmP9jqPve5Yw5fTLo54enE'
        b'2bdFX/zBfTuqqXBsVuGaFNh58MICx0MfpBf9uXPei9Nv3h5z2bL3twW3sktTdLcE6a75ffrwSbWvZhWGvfTZ0pfdEjKkp8s7l//o3W3h/7aLXWbZtB+9L+OPrnazj64o'
        b'u9uwwrMxfOyPr7Zu9/RGw6qbr7t5DFId/fjbnHttx3vKn+/8uHvy/me3G68X/er1S1lK13fGn4WH/+HcIz1TfEZ55qW749PTThbsPSP98nju3hWnv6q+ee/CGq8I76l2'
        b'ydnnbBObm2vW6aa/srDBwlT+RrXnu9/JPjEf+vaQK6dQ0ozpE9frbPk87PaQ14tvHP3O9GJ40q3yez8d/vmz2703b2cnXRscPuars3Gzfn+tpOr1tpShYX8UfPts75Zb'
        b'dYsf1Cc2Lv3k9gfhcdByzePTvJDSgvndmauTzZ/JMlxWYQeey5/+yM/eOvBKarDlPR07uxszN3TLGTMKp+AEah0AVYNmm/5QtT3uzJW7GbK3sKgrxzCJ0aLVBntQftgX'
        b'nVg0ME6wKJxg1RbAbiYllKNsIyWm6uQ6HEZ1WrAaVLnRO8ZZuagRZhp4GTShbgIxgwoXypCnKdBhLcQMDgSKCcTMD5pZ0OOLE6BWpWZQoM6kD2GGmtCRdGLtQI0KBzXE'
        b'TO6LTxtH4v2LdqJKNcrME/LFmIbtgyMMB5KtgEItzsx6kTiSd4TSKdSbdy1+tEMLKJswX0zwZJADLbSh+uh0PIGTyWb2wclQLZQwl9lsq+EMHID2hvbDk+XG0mFA1SFB'
        b'6sslSjit2w9NFsvqRtmo0hZKoZYiytRoMmiBUtpqL1Tszp6XaOFkyzXIg7PQgEoonkwLJkvBLBHFk80S0bbr+ftp0GRYrN+hQ+Bk0KqexQR0hCTRlMzSYsrUiDJ0SBN7'
        b'unsddKmIIKaFlakxZSgXtVJxNQKf4HtJEwmibDDa1wcqWzeJIdpkBhQUNne0FhOG8tFe5qN8DPLWElSYNWphoDB0YTQVBLFIfChRDQvTYMLWQguDhcEZQwagqpuS5Y2Z'
        b'0P4ynS300FdvHLFSGuAsk3Ocn7MOHBGgU6jShnZKDvusiHGSwUVwRdVayEgsOseSt+/Fi/cUQ5tZw76HAWfFa5mkfopgJlQuFHEGJSu1oLNCvEQpbrTeHsop5oyw12iH'
        b'HO1YNJ1gzKxFIjwL+1EHe0+ZA6+UU3AZ5s1PaQFm6BzsYI77p+HEFILJwmvUgvisazBmaeggk09zvFGX2EZFcQMMnhAP29kQd82xV2PMdqNGCjKLYskv10RDjTIVdfbP'
        b'x0lycZZFM4H5FFTyGToMY6YBmO2FXfTZcSpXJVy278OYUYAZ2oP20MuZcG6ddANq0aDM1AgzODOEzds2EZST/ozapMWYof2ezO3++FCoIhAzZ1U/gNllB/pew3l2CjwT'
        b'BF2GTqICLcIs3pgNQ41PihpgZqvSofgyVLGMUjQjzAH1wctgb4AOg5edwwSHDNNyKdqX4dEXo0kAXV7ptEEq6MANyYcGCjHTwMvmTqGvVUAN2qHEm6FdDTFjADNMH2vp'
        b'w8HToIJBSqDFWgMPMYaL6kycmEZRigCdKQxkBqU+DB1wEXXhPjahCwxppkaZwUlUn65m/44nCt37Re4SwP4NLB0nVE/ZrIJOVKhlX5dYsJ1oPEOtePLK1ALMXAPptUjc'
        b'ki6VwXo1/IWBXxJc6amyEg7i3jN8WT9sGWxHVQxfhi4GM5BI8bTVamwZ7JrxELxMoKBTGAE7ZX3gsuWYmSTgMvzqA6zxpRGuygW4qEGXSdFFNVhy7TQtugyTqFaRsWB5'
        b'5Bi2VPfAkaUU09SHLUNNeJSHUAGwZC0+B4oZvEyDLUOnpjFMUDZ+uJSiy1AHtGnxZUkoh3UpF3b4kRnU944OIKHt/dE53G5LdEak0EU7GXrtAtQbE+45FJM/DfuMLuG9'
        b'QKO91CSEKTPitK4BqJDFVlujQg3S+XGal5JlqQ9VPJyAnc50eUBeBuHJ6aKbhlqwFGpngWpYjSegIFiBalC9ljQRVJvZAgbzq9GZpGJnoh7FtBVBOyXLwz1FUAkdY9lG'
        b'y1kYoYW1WbvqUFQb2hnCCP92VIsPKw8s5WuAbRpQ2w6UR3dMFuz3IuEfHbWQtoVQR+s3QS0bGKStD8+2FHIYpA3OQgF93lmGdtnAbiXT4RFMGypMoiMzQ4Ry2ErzSUW5'
        b'hn1ANMjbxE7V0/jmKrUev8SpHxQtEvalE5d1aJ1MIEdaMFp/JBoc1adgtEikjr/WjtpRcd+A4YPIiTNCucL0qdDBFsG5oHiyZpVyvckiVCT3UQONhkCOaL5iFF3X84aF'
        b'sVswmaunXdZFB/iZ6GQiI+HnUYUBbhAltrELtNAzdBkvIrIQTTcT7T/kopNarTrVu8JOQzpca0MFqH0zKu5TeU6GMrVGOcddJUetgdIAVK6Q8z5QwRmtF24i6bNp0zZA'
        b'oZsCrz+8KQrHKImGAVXzG6EHFdG59vOGKhWJC7qDsI2kZwIntI0zNhdung8n08eR1rejvRMHYvI0eDzCrDyMyUvPogObhufpMkO1MUgburxajWozZmj5cLiwSoWaxqhx'
        b'rQzUOgSf4JTG7YmMhiJ0WUWxfAw6DYcUbAPU4Fk7x/CwaNcqDXh3bBRFIkIZbusFRR9mEBV6PAS8QxdYXEUr2AFFmjaSiuAMalQDBzkHtp1KoBWVDUDeYaqpwd3pAIvR'
        b't8wmAS4HSSnynMHuoA4qaWMXDw1Wo+564IwWdQeNpqybeSgnBOWNkFKMGgPdzUANdARjoFVIiY8Wcof2uDDUncooncTLcQ7bSBB3DiiPIu5SXehzIXoGFG2nhtqhOtTF'
        b'4Hb4E0O1Qhvss8P7/TgF3WkQd5h9Zmh9KFaRTOkNzhrIHdpjyQajYNo0BrhDlyY8jLlDF+AUHQxzvEZOq1F3AVAhtuZNR8E2OhgLZhMjBVEtrh3dh7qbj47RBTEFnbCi'
        b'kDu8eyv7QHeJjFXukhNgshp1NxM6dAjobrZ6rFwNMBNBMHd9gLvhiRRyJ8H8Lnl52FQL1SovDeKOwe3QKaiie5zHx/wOdZAKH0PAZ28/vN2BtWzVEdPVKdtpGswdA9wt'
        b'g3o1LvrwarzCYjR4O26FJuREu4iqwPBBeakPVpeFzsgN/u9hdBTkRO0GEX+BoVMj6YYwJJ2RQCR8EoZO8hCGTkTtCfoEoXbXSCyiz9sIbHhL/Nfqb2DmJLoiNYpNpkay'
        b'8fcJwo1/IH5Pf8LDKDr+vonIiKLdRLRmYtcgb7GUWBC9P+/E3ovfIBL/l/i5q/zv+nP64+csn4yfs3jY0vBfgucKic2D2HH/yubB5Vh8/RirxxPagltAcAZpNzT4OSHB'
        b'z70pUCsl5ab/d7i3q7jS6wQemMT9r3Bv4vd4hYFAotMP4zamD+PGvrN8YD0zg8TNica7uuFhzbUTFoc4B7iskwjZ6Owjvq8G6r+q3EewbYtFu3R36e0yjeXJ710G6s9m'
        b'6r/67G+8MFYYLSzlox21hiWS8EZWMKjAoMCIpq6WEYwcxZLpxIijxdG6+RxJ3V3KL9bFZX1altKyBJdltDyIlvVw2YCWDWlZH5eNaNmYlqW4bELLprQsw2UzWjan5UG4'
        b'bEHLg2nZAJctaXkILRvishUtD6VlI1weRsvDadkYl61peQQtm+CyDS3b0rIpLtvR8khaNivQiRWoEXLm9DNJAy5ZbEFdJ4XU6CYpkOKxMcRjY0zHxiFaju8YHM3sFYpe'
        b'2eyZ/mGaPPfXO/iH3CWJv1L/OxiYTuttk55Msj2o2D0e453YXzeaG4F8ch/wMo1xTuViM7OfI6Dar43iAdTec/hqekwaTd2QnEny0qYPdOTrn8bBySYmatVqm7SYlLQY'
        b'VUxSv1f08zQkbqoD3vAkV56BJsIBhYBk4sHlE2tDE7KqbLJi0mJsVBkrE+OpT1J8Uj+YBXWSwpej8E/66rSYgZUnxqSvTo6mnue4zckJmTHUmJlBKEzCeuJsNSBPhc3c'
        b'eOq35DBTrna+TRjozUWcntT+gGwiXNXzoBlxJxuHWXLNbVE2qhjil5Ye81eTRObQYbacYDOi+vn+qb3uktPi4+KTohIISECNMMZDQAAQD3VUpYqKo/CQGJaPA9/Fem8T'
        b'HZOCSarKJpk1nDrwOaivzSIrLDFZNdCPa1VyYiJxMqZr7yFnwQA53ytcl5jQK14VlZju4b5K2I/s6KhJDzU8kXD7auCXboEmY5aUkhABJiJ8rIHaSi0sFOdxm0Ub9DYJ'
        b'qZVaRC3Twi2i0H6f1SmX7wj+BhRswEZ6ssvYk7wIce+YA+FCfz+1BxxNjkLf2zdveIaolyjelo93LXWIYcvpSXv2LyBKdGinEKTJqii861fgJq1gnnzsZdqX9F96T0hZ'
        b'ExUdHc/8PtX1Dlh6ZJGmZsSot68qA+8rLfl4PDRjgHcsy0RDdl9URnpyYlR6/Cq6WBNj0uL65Zl5AsgjDe/KlOSkaDLCbE//dd6YAefcIPWCG+hFMDxARdhtlaS27Y3f'
        b'FPLmdPkL8o5i+Ttnc56TqLj4zZIG4bKfyOMZREs/X0cGbagSnSdawnQsNsihA4rlaA+chRx0AVXSR6DBxIayqGHUlB+N6tE20zRowbVv4basgAvUWvvWJBphmBtrf3Zo'
        b'htMoLsMIF8Szwz1gO7Rheu/JefpLE35/8OBBZ4KI+A7YjJ1nG/rboM0c8z9rHqaikZPRUZLUw20sz+lMFgShg4FyPoMGsMmFCj8VKjJAO7KYYcEvwEXP0QGdQDUCbjza'
        b'JVagcybMjpq3Ho5LHVGj0EHA8f6CieHJ+CVE5zs7Cm3TvANVod3kPfrkl4Czm6JjNw0VURttMjroImVfw54UIeoSQNPSUPwO4uyC2mHHePwSdBi6+xrj44iFaNSq8FG6'
        b'EPtGBNonGYYl8mxqLB4O7VCL2jQXR9hIPPgkODRcLqR+BnNRFeyHxpUkL4czqnQb68Fzss38WpRnysamWrIKZaPCvutiTraFT5AF08sO0GiPdqGmvssCTraVT1w4NAML'
        b'n9yYAFOW7MM7DO2DfG9yV7B3n3uJgJtjqDsYdmygsXc3JQxmEmSwM+qAw8FUfjSFMiEcRK2bMgjqgmRKyVeiHZCr1LqoaHKloB1+SqUznzoVaoehi1Bkjs6is0ozKFJK'
        b'9dFZKPYNCeViYo0meprQRXMgUb0UYp1d0xINuIzFhOW0gdr+Ubn78t+UuvqGO6Ad3qgklHhFKsPRGYUcHRuhXrzUNwbL/iaj9dE2aNDRQZ1zR0OTnJubZYZqUasDHm8q'
        b'1DdjcXI/ajNMSRNw85U8uiCwRzl27Np5VATFUgnB0wxFOVhycSRWMHYtD6qwlN4mS8XPjYFcHp0QjJqpQ90YNmDRV5VClbrQ5iaUCVa4oVMsH0+5YpEqFZ2VCbj1UMqj'
        b'bMGoUaZ4LVFn3HDoUKEO8r6t0MRDj8BCKWc2/5JM2K2uCprRYVoXZ01x3RNW2mbAyYenG50NzCBRNUZBmbUmwws0TiNJXvydfQPDvbX3q0cUs85tHDqYIIXj0CKjaxuK'
        b'4fQEZcBo1NWXIYY+HOQcwR7iUBWmABcknBs6Gr/uo6G8ikgksa6NiVWeyaYzjZ7L+u6d33698c0V2xkSQ2HOJ6IU68xsfkdV7h4jzEsuUkbczV5z/npNxpdF+ke7c/kv'
        b'fgv+fsihY/O/13MY+UbQ+O5Lk0QOSclfTH/w/h/ffCSfb767dmHtYf0Q3swp/OXbW1pv1HwonvCy+a0gbycfUfB1F/P8JU2DAuY97Wxa4lVy9+ypceZpeyzOHnlP8GNu'
        b'ekfprVkVb3gvGCaxzbW7kpzgo+N/seTDMZ7Kcud4nyXv/R579vWfdIxlN3/1z7I5UZKZld+QNa3ZZ6XdK18EvenYPuLnWZbKrxSvWPosuNDz/KrblqZlsTc+s9//fJuP'
        b'9YjjXnXjd8ffWPWarNy0aJHeZ4t+7hm+YcVSM1/Rxd7Je3/bnfra+p833R05ffdriyzjG/8YssVi2cFAh+JnM5KOOv/w07zOsSEuNXdNLlyIyM87324/9fpN+ZuDL1Xf'
        b'FX78x5xLr7d7Flx8aWzUt099tuDMyD05aXOfOm1vZr8/YYan2fDQ3jfuN82at07n66/8v5rS+nxSw71lkyYlD/lu5fOppZFftt4XBi0b15x8dejIczWeC1I/2iOb+/y7'
        b'v/tvkX79lqtegGhuUPcrqy6CX/W+U1axX38l93D+2cvdyeP7iR5zBwW2jT90rXGS6+dDN+18Trjh+ytXhj7nfqfFcPXGIT9vDf86Ue7auMR/9awH9dUe7iPuK0Onz/yp'
        b'9/Wrqpopb4ZVfnFPryZr6xthqpqy+qbvvj5X/3PpA7j/jXt2Z8nKX5uydF+8c3/3kX2w/Oolhz0fveJ98NysIxsce9vSG/4Mb41rf80MveX0onew8eiweXZTPmrdWOj5'
        b'6tdDFl9r872y6YFkt9jxN6t1t36daFNeuOXul5cFiemSreO/lM+k+nuDGF2FC+yCSn+e4+G4QKnvTxVGAUZQTRYzIRqT0XFMTVARz0mhB+8jfVRL1Wh+lhYKH0O0x08X'
        b'P1oomIoJeznV5o5MEqpt38s8SAjTMt7ZLJbpmLbBPnQJil2pUdNBhxOv4O1QAWqiykJj2IW6SdIh10DnrKk8J97CO86AY+lkZ9miEybkuWp9Yi31c4EdgdT0C4Wu3k6O'
        b'FIWpy0Xiw/YkalFHXZxkZAs16zWG/D4j/nY4RavbhPYmEn0YKnVG++GsmBMv50f6jqE6vrAkXhno7CMZ7USMjlJo51HP5niqihsOddCm9R9AOVCqjXabtIqZd0maqk6t'
        b'L/II1NQHjYRmqKS1m0I15g+INpBoAleYUF3gmhA2TIdCoFKtC/SFUwKO6gIj4EC6OhHCITuFD5zEpzPkmYriBGj7IFTEAql12aHtRJc9QFVo5Y92owOiVDxDh9kr8qAe'
        b'nUtGFdTWxaxzqD2JvmILHNmMR9rXX+mMckKIai9A/ZpRaLeOpyMeXWqgL1dZqVDpIOjwITOiNAhwRu1KnrOeJ4KGBAHL63McmldtRB3E1F2up75h0FwedUIByqFhffE5'
        b'sh8qcH3xcCDA2cm/X3U240SoYRM6lc58CbOtSDwxKIPsfhpOOAEXqfpz1HrUuGEuFAe6+Po7+fgLOIPVwkmLYRvVB+t76LlCq1qzy1S6gzyEuhPhOBvu07OhhBoASpSo'
        b'eJ6XLifW42VToJDZmA9KA1Q0+h3eEvuFawWbUH0EveLOLdEYMBehPdSGKYum42s9JVpjkRuNLjOj3GqopT2x4GAnqYwYN0kgNSGngzkw1DUEDtGlNywQ7ZO6KF14EqZ1'
        b'uxA1C+DgxghqqxwCjejkAFsl5EzsFwoTmlAHbdnw2AkqzC4c9ddaDFWgtjR2DkYlalNj4lwRRwyNqCOSjuECyA8iZiVinYSKRUK0X4CHe6cH06nvRxV4YnCvyhU8hyrH'
        b'CFGbABrH4eVAz/ae0cTLw4aZoKklHvNk2XR8/eWEdWEWivEiHdzfLl5AFhzTxndkoNOqAL3BGoNuOOylK2yCjCPz2QcmQCeg0wROCfEANKnNQx7onC7FEzAbvz06JYEa'
        b'HnaQ+HdsfR11Q6VSR0t0oJ/bUD+foXC8Bkjfl0A7OoZZTGqQXG0pROdIC08volMWIhQFk75r2XwxZxAtnAtNUECJkw8U20BxFh6g9kzUPii1j/kieGtXVObt74yfCZ0r'
        b'MchAbBNbQQWqUCn0MQMsJx5Ca3U38+5OLNQwHJwjUynS2DJH9ct1Y/jxeO0dZzaKS+jIEtxlHxJuMVAxl1i6ULkOZ46aRcaY+p2js2WE91WVlLycvaQUVepCMz81kOWl'
        b'QocmyXRgt+Y1eKXqcgYBwhl+qJtZZ3sIukblq8Kkq0TACdB5gZH7bGbxPTVyOrSg7cQwQ60ynpHM0HiBMPb9DTPcFlRG7TLBY+iitLLEXHYtHCIuMcwfJh4TAXM6+Jds'
        b'VahkHSpXR+3EC7yAmjopZqoAtxNvFh9UgnvPyIOrNyoVciPRMZ2JeBe10k6lyc1VAXK1r5QSD2odOm00XBjsBczsg5pHS1XoHHFRYUGQF+HdQvfEWWhwV7GRWgX1Qtgm'
        b'2AAXVtBrwehM+Ir5Cl9npbNjACYrhnHCKEsootsxcdAcbcuUzHaGzy7iDXZAJF+ug3dMTVY6ESFioROTvOIszeIwzOi3PAIn4EPSE06JA6Yb0CoVcBmq1G4/cGos8/xJ'
        b'9qajPBm6hkjJJc0qRodQuTHqEmJ+1oDZYtu90FEFPXucxRxmYU9KUDePj5Od0EGJsjV0Tu1nSjrr3xe+ETX4ygf99wab/5Hh53GRAAD/+muzDrdVP8ZIYMDrC8SCYQIZ'
        b'M6TwVG1+z0hHQk0cYoE+NYfwf0p0yWcDgRX+GSYYJbAXmKhTYEkEltT0Y0QNJhb4Owv834A3Ib/xf4nAmphT7oglFo/5TozrMKBBGMkbxGpACgnAKPpFpLvBvL+OaWB4'
        b'ArkOg4TcJsaKbwbCTGT/1bQI2ev63q4dWh+JOqTWX1tguBz7psfYYB7fmf9RuIOTxGuchjsYWI021sE4je6bKo+dbGLiXGwciQbMZayHmyYSy6OhD/5+8zb8VfPOaJp3'
        b'Zyhph1qRahMfPaDGv1XZalxZk6BXErmKadifWGebtk5bilOm4NxYG/oYQdv/45rjcM1yQe+gSK3+ODL+ydV3aKu3n2mTkRSfmhHzGFD+P21DLGuDLFKjT/yrJnRqm+BI'
        b'RkCVjoeAaiS1ysh/2wwyCWl2fzXjPdq6XUKTSfyfpNhkGtjAJmplckb6gHBC/24q0kh4mCfWf3ngiusX3uZfjXma919VBtrKrPoqm+Uz+18OrPKv6npGU1eaP/c39yd9'
        b'adlfvfR5bQccwh4TlEgTbOPfbhl9Gi8gkqD3n9iElwZOGIX8s037bzeJhNWanvzEOl/V1jlEHR7iX9aYryENK6MSiBkkMjklJumJ1b6hrXYSqZbcy3TzCf0NfA/HE/nX'
        b'rTLQtmpVQrIq5onNujqwWeTm/6pZ/4tIlHGPi0Qp4B62RwgD4r8R9QhVhEv+ZsIgElJSEvtJguCZck5yTPBW8X11GMkNoehQPzlIYr6KiUG5CU8IIzlO4yhDGNn/xFFx'
        b'W8VxG8weOuYTYpI0EZUeF0SSVPAu4StIVIT/xFdwObKax3AWj63yfz4V+X9vKkQBYfE+L90UqKjebGqMMkoW+8nLHCd6PU8ucAy917fyHh3tDo6NdlqZ4BFOJjJyZXJy'
        b'wl8NJXm69x8M5d6/waSxOgeMJWkzqZnIUsz82hd5UxPsiZlgBQWDtOZXvlAHj7IQjzJPR1lIR5bfIgzt9zmL0K6HRpnYwkgqRbcBo2zDomxgOT2QKP3R0XkyLBISpb+D'
        b'Z8IfDx48mKEQcS/PZpEUns9kuv4yyIVWlUGaMarXI3cfFrig8mRqIbnsrMOZLR9Mbve7xyVzGYQOQNcULJwRFQrD4ZPIFSVK/CGAhHALCYLSeSHOETy3fIYu1KOcNRQT'
        b'DDsifJVEZ9MEZ7FYVUY1ZFQ9psM5rtKBFhN1/sSNuNm5qpSA0FiitCCmDNgGDdTU5B09XxugQ5CJLqsde1FjBsv21+NqR7Q7yqUk/Y0uJ3IWkGwswAwh69A5uKCQO44y'
        b'1kB64chIZuAqCYEyKqPGokbHACKyYzk1JhS2hTH47k73MCoSOvuIJqGznJ4uD2WocAsLKbIXcmYpfZwgL9EHv1ckgIPQNIPldYTcQKLplDuLBVDM6U3moWHyIvbU6bWQ'
        b'R1E9Cg2uZyLqpL1YgqXaRlTsDA1QFUCFS/Ey3hx2zWZ2yMOoSKREZT4jUaGTC3HcLabDzoIKKKbqEGVP0yMLU6pZmN59C3PgshRoI4/96yVJOqb3yJJ0CaBm194JxNYm'
        b'ydSdsUJ2bms4yxEZDidm9QFT0D4lHtcW2EevTcUTe7zPv3cjwT2hAwYstHA72j8azxjUBBPFgmbGhvuwwT2JDkAFUzoK1wocYNsmHrpYetWSFFStGrmFOBTzEsFwV3SZ'
        b'2dYq0X6oV6LdplpwAV5DFbQywcr4AViKs2g37Mezt4suDsk43/4wmHJUA4fRPiijK2tMEurGk2ULTQOwMHBgKLVo0yaRdGytocT4JeNsOVt0AS7Jdeirx8gW4Ien6Ax8'
        b'tnIT7eQ0dHB+P0hKrB90QV0INehae8EZAoVBDaYDci2JoYN2dl0k2qmAYoGL3LcPYlNgRQ2wKHcdHFWsCMJVusgd/V3kzr7+As4OtulMHoxqWVLc03BsndJvHjrbH9aC'
        b'TuDLdG56jEj8AOo1LYATIZxYwg+GVpRP1y8UoENeiv4ZW2APOjDA/XoNKssgGVIsJuPFTnz0/ahqmZgMS6HcFYroprBfoLMWCkMyqAt6xUx0ilg+HnZA1zqfL4U8HS4A'
        b'cnRJClA4RgmCCVQbqW2mmMqgEtMVUM/TjLruq6FaCYditLRGTWigAl2gTYMK2BlMqJmGkqng4ABihopQE6MtZ6AZaC4RpZokjSdKpdGwja27AtSDyvpwDuXoMhwxNqbT'
        b'v3gkHqw+n/486MTvrVcvO2hQEmSCM6UQKDuJEYltgxn5b3Ae0gcZROXzoWl8EEWvT9PFO6wYD59gDeyYxKEyODaKulUYp+oraKIgUZTA2hLl2PnSanhz1KVEmDaVeTs7'
        b'USDoHn4TdK6kEZfQrmUeCsh16e/9rvV9XzuerYZjsBddUjjAycD+aJQR/jR7ANT4wx5CzTSkzAfVP0TN0Ak4J+dZiIfjY+EyFOOT5yg6myniBOg4hxr1XNlI1kGpmQq1'
        b'iskmx+t5N56kibCfdm4ElMBptFOMV18y58Q5BY+mh5v3MH3OjHtexhmtkLm5jmWhBCKHEkeS47yMWyHrcLVmX56wJ8TLcrMhJl6X5ijYl9tFJKPwha2ioBWyO1YB7MsD'
        b'MglnxL03WLZihdPC6RMfDbVAuUbyY0WZkU3cMt3Ngk2CFN1oLgLT1lQ+WitbUmZInTBZkPkQa96r5xUXkxSzLiVtWoyemt7y2RbMhwEVToMc1UPKdFTJYpk6+ThDEf6w'
        b'd0DIBbRTiI/KnSYk6sJ22OdmtHICaoKm9dBkrjM3k4N9weaoLSadhqNClcTwVIyIzWens4sPBaX4Bgc5R3j3m0sykeuyyFRCG68vIBG2mmUrbB3p2gmbZ61QQruvs9yZ'
        b'eDyojUe63LBwEZxwmB0/6JPjItULuLeLpqfHhHYmfTDD6NqyIhP5rWkJb/22+Yv22iNGssHfhuiIc93nFTlFr9OxPJsvkoxdIgp42n57V/uoCnv/CrtIY5sRFdO9a12f'
        b'v+30yvOptj9cnJhcVjv647bj667M+zT6+KJdxYvAvdzrhY0rX981S3pz9ZdeBQ/4aqFfaq3QRWU71MXWNE/4fE7Ft6Ok1WlhAZ33Lg71td56KvPpUv3m19226OY/9WLY'
        b'K7Pj6g5cclz57U8P2md0vnfy9ajzXenJWTMb4yI6a4/vDhuyLDkk4tjxg3MVUwzXh48+915Uo9/ginfL3vMJ3/hJ1Be7ZZ9uAPHBQ0YTS6pSXnU5XFhdUlHfveP99W+H'
        b'nHJ6JnGO6b5f5ooL7Y037565YNSHV7/aulemf/buG+kt+4ZEm4v8kxrvjjv2ns/a94+W1bwYsCBQVdv64ceril5JPFTcFOTfUn1/xBy3Xt2tV3TXf797bZ3xRMmm92Xv'
        b'NxT27JkcWnw2NsO4aM2rv9/JCPugfsc5+YTAW04/6oWMCXJu1rk12Wdd5fdm10enfWdr+MLwqi6/W4If40MafZbV9wyBlvw4vdPGdUe+/XpNXlqgJDkkus5uyZRJHucs'
        b'KnTWLPnmuOfvz+4+lB+3Oe7niuuD9rzsv89z1GvLem6edYkL/vDDjE1XXN03fFt5pGqy48RhCyqTR+71+ublq5vPNbUE+X95d/sdu9rUVuRkveNpt5LpT02MvXky5uhz'
        b'hjfSIMM5rT7zhRu+hp6yLTOdk55/6ueh7xZMr7dfMC5u4jhzr+i1z//6bHWGJKpuOHpnyrse72yEO59uvvvm1zdPFtXrZmw8ssj1M0/3l6/eaTx6LfEyav8z6dkJs+yF'
        b'nw37dknm8OJNnfLz0z5xn7+wtGP7xsmGhzfd9U764OR7iaMMJn5g1iUY9Mu+DvkdV73PTn5tf3jM7wkzTbt7tltETM+zb+/if8r6XmSX1nVXlnW/OjL1mlj8zYLA+nu5'
        b'13/72jvz5bvfRv4eM+6ZgnT5ZGY72okOEuJd5grHRZTzq8Lsdw+0Qi61fnsRvlBKgGT4tDug54DZamcxZwyNQjgATWg3Q7tUw8lBUtgFOY5yzC5T2NBQPsJxKQWbTDZK'
        b'YYbpxAXUNO3NqdNYLlH2R4wumDx0GjQxI23FzEi1SVwUh1sUhbZHeTPj7rExwf3RkUlwFuqgGxqZVbNrBTl4+5gjI0yu96Mz0E4vD81Al0hXFNDlk+rnKhdzg/CN9u7Q'
        b'yYyLeficeRQ7aobaxMweWyplBr39dtCkQodm9odwXoBydrEeDi7WgD9Ry1Rmkt0/jvZLBj2oTRqHdlG8Dh8mmIaKtjATXQdUq9TW1gzoIgbXoUgN2z/lMUvqAHugZCBC'
        b'WTqRYSNPjYDsfnhfdHoiHEmGGvZssdhH5WcGp8i04GNMqcPpy3g4pFpObVNG89Bxild34tLgEieGE7wbqh7GkGBcqBKqoc7JwbtfLIETqIBedRmZqYUoJ6LtnBqiXD2J'
        b'timSW8OwzXAO5XMM3QzN6AhdcZboCGBWgYYBwNMkmiwIxsdoK2Z4GWA0ArpQh3QeysEMXx+sGg5GsSnOj8C89EJ0EhX5+KDzSp7TTeUdYRtqoT0agc/dE9Kp4Q6OCi28'
        b'dSz0MOx6pQ+0qfBpXOLunMrsvvoLMCcOlVCiySYJu6TQlEJgnKjRCLe8Bo8n5pn2MZNjIaocqnLHlWnyETrEsNk7hMq9pFh4EmPZoAvzbo5QacpAu+hy4jqVbgjxznRR'
        b'uugTHsgSzokmotYtzLukEtVI1WnhtEkdzeDiWswh4zMwnRr5pM5kdQxEqZo6jqcgVbdINTgYVazD03HelnjI9IE6t+CtwQbmAImMwwBpw4XMB8VcRNuAObnzcIoAbGMw'
        b'S/lwJuH9lqwjNckc2RfTZwwE2aK6TXSXb1wfT1I40gSOGyF3pvFkWu9krxkEsUx8RZYCXgtzBagUSpLosBGI3KU+GKKvDRyHQnc2oiegDS5R2/IQdJ6alxei4+zShRmo'
        b'TA02ni7lCNZ4MJxng3B4mIMUqtGRPrAfhS/2wAXamEwsF1T2gRdHoDyoM8PEgXAAM5WocyB+0QwTjjoKYNRH+cy5oXsGHJNCja8GaqhQZytdhS6rVJhAFj42v99YNdQQ'
        b'T0B3JoMaogMTOAI11Ecszy3mddrRJVXEYFRkgBcg7reukrfFzPF5RlUKphOqpIU/hq7GUt0RuMRS66FqdEYTnmQ5KmY+Wu4hbEj2zjUlQQrrZwdg0o25LQEnxTsZnTJK'
        b'Y+jpCwQWXezkh/YQxgsVepNQjKd4Gm9DbWnfNX6pYhM6jtllgj2sFwS5xDGscTbehtsUgfjAOOSE93MxdduSoks8Oj8VWlga2Rb8v0NqM9ERlQmJ+7F7DLAc4XAY0+4W'
        b'vPTRzvCBnjyWoWxrlA7F9xTDaUf87kLiO9DPbU0FZXKL/9+4r4dMrv99JMRefQKxiaTu7ZTz/pSyyf9ZY8tt1TcjVmcRBTWS3wa8PbV7OwkcBdbUDi6itm+ZgM+m+kJy'
        b'J7OM3xcJ+Xu8kBfr/2RvaCGwFxjxBgJLgZgnNnCWfNBCnYbQilrLZfi3CYUN6vOWxGaO77QUGEiIHd7gwTDeSmigBlLa4G9ED8jPMJ68UUYj91sI1GBMXszjNldukD9s'
        b'VCajEOniRU1QqmkufaPCpAxRr176uuiY9Kj4BFWvbmT6upVRqph+pvN/kYkASy6YOHFpEl6jiNXFn4REViGJ9/6zIpbLsfnmUVVshi89vbdyTxRv4qDiP0k4btwEVG3o'
        b'5I4uq32yMVkts1L6TohTZ1cnsXDQCb8M6jLUoYuylWp3SWYjcJ+uEHBWcEQExRaohfr2p8zGJ2GffMXcK0momsPcCE8R2mUnw1Isc62GDmelbwLq6leXGUMbwqF0vCkH'
        b'VBWFarV1oWwooiGHoXZTqIJo+k46ePu7+PgHp5DBoHkz8JnWTMIaCLgV5pJRHugIU0MciUE71S7bKMdY67XtF5DhQC7XoSpoUqJSZ8wohdGXjfMI9mZ9mIXOcVNGibn5'
        b'KIepf9swV9JBU3io83ew2h2oRheOQgFThCyFGokh2mnPQkKe0sXs6iPjAz1ZbHggG2qpLkeBSmxV/d5Hjt89cDkgXB1emGiECHsUu1WCidVlVE8XcPwHg89wqj344zC/'
        b'CzGh3UmmM81qq2vP/XZjgXXABL3X8ieO0kl88fU3cioqTDqHLFppN3mop03REL2FR5dZRQc3nhn91Vd/CL8KfWpw0LEZdqNz3bJK8+dc/+Wa6rWpv33o2ea66P3XEwpK'
        b'//go8CXZWwc+DX3ppd45ftXm29cGKp/57ZmUuTsmJrxebWtdkTE6RzT/0o+K9pfS7heNPBVffc1jZciCc/KJs97uWHSznXe+Fvp26J7iKuexn+cmip3mPLO5WdJkN8rd'
        b'amrY7U9ai1936x38/JXXi3KuTBHs+dxgrVH39Yrb2YeP7XlH+Jqq5HbnZ0dPLdm5z/ma2K3Rm0807n1DFWHV9GXlxvnLez9vKD1xVRr0c+n0A5Yjliy5cndE4VvVaQV5'
        b'71Y3pf9S9Zbu+Pne776z9MDZNxaEDv20ca/8u/tvbT1sXnR8gufM4XPvVQc8LQ1et83prp3T4cPBZw6/X361Z/G64e9N+WXZuZlDnrppdWvrrnq9tDrVUPim8/p3Z5Oi'
        b'X22LtA9Li+xd/Tpn8tVPd3I9d497za7Hdtbc6MPjRnykMm24YPj++PGDr91tG9JqDBMlB8cM83Q0FT5zaR3/7Mb7ez648OOKTz9qeFNxb9qCHXr+JyzKLw4ZOS7HZ8Ne'
        b'3SXmpq+KpnxnfXKnyWkvlPrbwjDzlL2yT+Jenr+o4Y/pus0HwkYnfVHVXfneU89+XrS4Lu1qbdSCBdfvb6vsiLJKcvnZK+/80axB96s+yjg0caz5jTv88684bn/1ZNzL'
        b'rcvCouRt/m9dPf9252XVd2cuDv8A5pz88Jc/RYPlmwc7b9b9LrIi/s0Tp76Li16wNNOouyfX+pqLYefOcdPvrja5OPn9mk8V15b0mnckeh478l7oBcvNC1qO+W8JCO6O'
        b'T3EsS0yxOH732SGJK0o3jCm3jCt4oz7stkD651aueNiDYdKg8F3ysekKvEx98Cbu58j2GC/HoGnUzzEilXIaocujiNtkBjrKpA3iVQkXgWWoj4IqsjnKXA1tNKJkjxvU'
        b'MTe2Zt2B3nxGw1FelDAY5aBKxhp1m8MxIvLZrWdCH9oOLYlMLDu42mZAmDjiKWeBqjXhmHNRJ4u0grm29Soto40KULmG2U5xpM6OsN0/iUSjRjkWHJ8pmJkObYxHOQHF'
        b'xGPRWQC7oYwy9nNZOCE3tAv1aDyNidIb0eg0tlDBDUe7RdDurxYdIDtwiRTLHGWodR7aS7soNeUxf3lyEHNKPI86xVIl7HNAJalyAaeThVnApETGVbbgpuep5AJvA7Ur'
        b'4zAlk3WqfC1U6nBpNt7Es1Q/i8d3NwUzRrhZuUkl14MCOEZ8HamjY+AG2lOhEpVjPleMCekRjl8g8LSeTXuavBUzqgECazis9tmEUlTB4solZak9YnnU0ucUG5bGxO4K'
        b'lB1EwreRaDZlHIvblTsDy0WEhzQzREc0keOioK6/9ICOWTMpdbc7Hps2ZwdOnYeaiB+oO5DykZ6oFU4OjIcxB0vVzInxYgJjkLsXkeSNau4Yi4s5lEMOh6NsfHOs50kd'
        b'UAuUMmdVIhVsVsc0yUS581UkWD8ctiN+pkJoEkD5dLxs6SDvIB74ROwvHRtPxHIhtAuwDNEjoROrh0qCpS7+aeQ6NKVjxtzYzD1KuAYap7KJz0cnYQcRGumgwQV0lJMM'
        b'4qMTYS9d+Vh00EdtNGod6hH1C1w3HrP2FGSEeXziof9kIIQEFamxEAedGedcCNtREVmwqXJoXdMnyRqhWjZd9dANB3GjQhOpLKsWZM0m00WgB3kOWFiFSolaXoVKp5Es'
        b'1z0cJyYeOAgFzM5AIg+iOj06y6IAVKwBkeDRLJvejxu3NKOzoAOV6CIqxnyADaol+zhQgLJtLNRqDLQPXSKOsLAX1Wtj4CWibrZ7z0xEewfEcUSN8RSGAS1Laf3B4in9'
        b'fP7Jbo9IwtvMMkZkF4TaaPsdIm2ICy9jdXo4TjKJXwmn8UTTI//McgJNCBzAzigEIbCbG2EpQs1wXC2LKSITmaCM+3tkIo2hpe/HQ0WwhMp6W+cRh23Cu8CO/lbjsYtR'
        b'i7/YNGUkC/l4Zpb/40kr8RBeD9uZkzAcXEq7r0SXHTXsyGg4SvlFXc5gsXBcDGqi1Sa4wj7CMRkufaheR1SoA+3DdBlG4/J0nrwnEAt7eJxPuqhThAkxzSoYTyfJWYYX'
        b'abHTDHSaYGUYTgbtsJOb/H+UnP5XwWP6B4dx1fi8fPI3ZShZoozKJWL6Y8Rb8MOw3GMlMMP/iQREpBwWaJ6EnyeyjITXp2nZJXetdSVpZpjxNxFYCcW8JZZ1TPAVGsjj'
        b'gYgloubF9yUkYAfxTn4gVn+nf18slBFx4QEWHB5IhBLeQCgT6lPpzIQ3ol7EpD6JjgH1TDbBsp0JTe0uyhYJyP1cDn9M9OBRt1wqQamlJeYFTMWb/5V7sVpachkw3Nf+'
        b'vtuK/a6/41vMOnGNVGj52Ezo5pEEc78qnQmHkQRgT3LP0mToNDc6zYheg3/16qo9bXtl/R1fe6X9XVC9yN3TyXOJ5NcM8msrqUdP6/nXq6t2x+uV9feS6x000DuNOERR'
        b'Vx46MGwezP/v9BF9zki3cPUTybxkcywijcjAibcX8CtZDBle+H/zVyaSCe2F1JYW6GygWpb6EOUTcEPQcVFMNDQ82eOLTAeNocJpMwTrar2/+H/n/UXOaBn3sPfXmoCM'
        b'QI7KrfpuY93HTxjn4Qbn4Ux6elpmaoYKU/4zmNE7S6IsWuLT5hxqM5TI9A30BkmhHB++JQQsHxqERde9ETrkYOuUSuEQnKDiObqMDsJhVDzGkVgkFQRgRTLWCDlTVCtE'
        b'XVvTaSgAO2gwdhtCDK/juHHoqB6Viq2Ey+i9+JcQctPwE6eF0sGoa9L6DBI/jYRoPe62dTbuxXhu/DhUQp0D0IWxUzU1qZ+qFdrMRF2obR3zMTmGLkxwg6PoLE98YdxQ'
        b'9mgWs91kkgKqfHD7yJMCzmw0bh6qX07bZ6I7xi2EpFp259zRcThDq1oCl0OomZVVZoKrKhYawS7UFRtJWyhfb+eG8iV4gj04D8yXFtLH7FGlJ+sXeYrnzEyFBrAD13UM'
        b'Hab28Ax0DArcoGk+XtATuAlzUS31G4HCcMhmtakfFAi9Z6MufahiHduPcnTcUMlMvIgmchMJTCyDYpd6cNX4QTivR5/WhXo8KtCJu2eWSiuUorxUN9QixStvEjcJZUMz'
        b'cw6o9QhhDdUdyZlBPbooIEPSMYg+NBqzRe3QlrYFf57MTR4LLbR3mzZO14wIHg07OmlwAtpRl2ApfQ6vImJQa1u6Ck/cFG5KWiTtnVMyOqBAlQls1mx49frA3FULnQFb'
        b'4QiVQowfmcXNgi50kFYmRZVraW34qZH4iRrowZWiLihGFXQGhqFtLirMn7XguZ7NzV6uoHWh/ROgTYFOz6eLUQj1XmQS8GNNaWwkq/Fyr1aNQ5V4xudwc7bAHjaSp4zG'
        b'swknHdRdSUcRtgejrlTIY8ElGoDILtA6mqQ74eaGQC5dymmYP6ukY0mfNCFz5zEddXmOziDZAyAncKNq7Bw83/O4ealzmF4rR2mIih3hEu0eG0+2b06TpuaraAfhRDBc'
        b'VsH2DXjS53Pzx3HUTSjSWUZvhlwSYQF6yHw3CtPH4Odq4RJ9MA2Ob1JBsReec2/OG+1ZSh/Egs1FX7bf2JNetL6IVNTFww764FroRN2obfAU/NmH8zG1pEPqst5YPRFk'
        b'uaykszc4Bc/fXjc6fYtDTVBb0jo8f76c7wy0jaWAqM+AbahYFqUZUlcNaSCTuHYyrW8eOj4DtTnBBTyFSk7pE0QHdDyqQbW0oXnoLO6eRwR9ZgK6TBcZdM3AwlZbTAie'
        b'QD/OT4V3LKlwOBQwzwhNF9UbYe94PDJtsJvO4SqoGo3asBR0AM+hP+e/HO1mlOVgeKZCvWLwo15kDuF0GOpSQDaL5XAYyqAGta1HjXgmA7gAzLV202E12wBF2oWjC4fZ'
        b'fODxrUJdki1s5ZyD/Vj2aUszxjMZyAXCYTO26+utrRRwzkG9dnRt1QtgM+xj26kNzmIa27aBJNcJ4oIWRzONYjvqmIf3fEcseWiWdj+tnkSfmoZq7KSb4BJH0kkE42Zc'
        b'YknajqF8yEHFWaiOrJ4csgZIW3fjJ8eibtbQXeg0OimdDJfxZIZwIavgAB0eRZBKgQ+NQjI89EEvdZXQlcp2VTd0z5ZCAxb3iNN7aDQqpgt9qSHai/vW4qZePmrCqF4F'
        b'qH00e3o37ucJqQ11IQrjwlC3KoMF6hagFlRsSHa+embVj1MKFwQ1dP2hzq2oWiqKxVMazoVv9GMeqWWZceycyEvjzFAuHCUEbj0cos5YaDvas06K93MOns0ILgJP7i46'
        b'thuh2wMVm81ij+akqWfEFlMq0tJwlB+NKSqqwxO5gFuA9kMD1Sx7QTZUMNot5MwiUfdE/JDxZvqMFI5AvRQdRufwLC7kFkJBEqU4s8bJ1aMiJJm32GkmMsfDko3Oq32J'
        b'Ma06gwleLpzFxUXcIrR7KX3nVHRuGhQHofMiYr1ejG9iNHHsmEX49kPz8Sws4ZYMRvtYb/Omw0W0EzUuwb114VxQBZTT14xEB13w97VoL03Q44oZGbYOulFtbCheeg2E'
        b'OnO209V+e6gTy1gn0E44KMM1KDgFiebLpjB3AVwMhVY4gmdhND5Azmxgb+qE8mi0MxBKcefHcmOx4E+/Nx8Ke/B7qlV4xp04J7QNdrLv4QBqCsULPw831R6fpx28XJ8O'
        b'lxVeCmfURw8ZLy9yikMtHqyuTYzAoXZoIj4RakaEHb/WmL/pQkehmm6CqdOC+ggEG3P8ti68HLpwvw7TJaDEcv92hSc6SU9iG4H6/OiESnp58ShdzRGIn11JKAXqwTTG'
        b'04Nts2LoSdUSS5TLiCw+FovxgsCkip5RTfG4xmJUOoE0BeXQzpDlaTKHkjLMHmASWKzQ8FMr2SrMgWbclUt4Uklv7WLVxwejHbPYjtyGqXyXHOoZfdlpsVxDmGbj62Uk'
        b'SAXZdwUb5QK6saHUCC4qoW0dTYhIkqhJ4DSP9/h+dPlLylRWpM2Q61P/unvGLM7TjJAkP/nkxczpzniJjCTqceCyNie8YavHvnw6nnjicWPH2m12+tV6JPvSea4JR3QT'
        b'Txms9hoxT8y+fBbzQSQM0Pcu0Qn7MjezL3UXGXK4cZbZw1Y7SSeEsC9fF4oJc2uUHZeVsC5K/c7XeSMOD9iksQ4rnV5YFMW+nG5FfAs5yetjN8vyLT3Yl6u3muNGcjY2'
        b'AVle+7cYsC//XMmCEH2yKcXPYcs69iVvyLppJIn1i/P25qgL9QsZFniZckZBqZuHLZ8+H8uMYfPohU1jWAdsFifLgkznsbs/itClbT20RiU7YzaM+7Kmmvx7YTqtQLyG'
        b'9YQLXpPwAWYgv3Sj/36aTrfYIrQPEafVPMjFezKZS8brMoeRuVphkGKhB95H67h1aI+VOjIXDXpigOofWXOYOJXiuW5CPbTa30ewLsxQJC79IWUe66wwxowOy4rxa5bq'
        b'xc9/1GdSG2iMsNFxap9Jlk6pLy2VGjvSqxOfFB2zLo14vD8uj5IhltVV5CsLLoOEGR2DiVKRIoA4DlMvRH+/QHwSDExGFS4fkI4Kb80a6czJE2jjA7Yu5M7gZWYzLXFK'
        b'T7gXnpSAgPhl3sCrmnAtv3/0dWnVCwFmwWbbvzt5q7XmWP1N4ytDjL/US31KcMU4bkbwjMN3JxibrBR6vrbM49mVUaOiWnwyZEvOf/vej+JLOYoRT5184CzpSg/++OJv'
        b'Bx6UyL+K+WXe0zndzcYzd5XYBthXjJp69Hnx0RfmRT9v775zUXvF5M9f4Iui9WLOmid+btC+07O1+MPSqZ8vv73k7RNtI4ZvGj5jzHqjZZ/bDrMv/8Rhvey5F0wn+dRB'
        b'/I+yrhfavrJ97brXesHgF5YvtXP9TH+9+ebo6acqhRcuNb/rnvSJfdL1Cd+uMMpKNfztB85w+sa1vQ7Tb3Vfqgv2iIt64d2cX691Lc/cnPXszF2Zg8unTbnuOf5by8Rh'
        b'Hw86nBGzdLqdgfX5ppoJxrJBx82njos+vOXAO9erqo7PSWs+OjZ3zK8RqtlzD+7wV5g2+r77c3aN9/78K3n7LpiY1oZWOTSfbV57svnjH9xLvnL3mbcuyP7Gc/f2XVnb'
        b'+4XhkW6/vCsN9Sf8Flf9NP2b4WhCXvwB1ahEq9HOTYuy7p93T6pdboTOvBKY3HxntlfJvKbnUsrTwk/rO+vfuoiGDXlB9EPX4QmzP2jz3z8iynDIr997xY1Jripxjyqp'
        b'ndjQcSTi51nzM1aNi8pYcuuHCW8f81NNylnwwYGL1dc2dmyMr7tx9KfN+xa+kfznD7B4Y3xT5qrx3kUL3rV/6dWpH7zU0aBzxH7MovimSS+f85376qtJaZbj/hiVcczm'
        b'fZtte6tOe9q7ri/JD//iy4+iXjf7Y8vcjB2NpS8qKy9lyFsvJ/gXvJgR6/r+MtV007ZXj40IDds7V2fQO4oYTzf7RfUOc2Xbm0+rvgmpsMvQuTWx5e78X7cFHli3ZtwP'
        b'M8Pds99V6slTvjvSAdlnPWc3HPJrMcttP3307ftjXv7p69MvZo1a8Jb5c9fr7t/bftvl6eQTXcH3Iu7l3nxwxXb3ibsC3yKpR/QZOQueEAwnVhFNL94FOpyOt+cmAT61'
        b'Li5k5o/KWB9UnBDLgkeIvAXQ5gBHqAY3BfITlTRNoJLE7Zai/UKom4VJeAJVE1vCPkzN23RRA3GYUulwQn3BOCEqZq42x9EudFBBFcRwwleHE0ULoGeKNzMWnIN8qCGx'
        b'hHycfEScNJPHtexD+z1M6LPTZkKzEh0xHugz18i8nVD7ktUK3huVueImiTIE1K28imrk7SVrFSRhDWYkDnI8tAki4FA4HYDwVUaY7l2w7ectB61By5nXZSHay6tjWehw'
        b'MjG/yAldJBkT6dVkVIV2Kf2hnLrl4BoHk6DpPbCdGoh0t6IOYgqLQweoKWw4KmdxP2rHoholXEx7OM4SuoDa5UP/bx1unqyd1P2HyuJefdWqqKTI+MSouBiqM57xHwOK'
        b'a/6L/Inqkmp52Q/P39f+CPl72h8Rf1f7o8P/qf0R83dEYtEd+leX/0P7I+F/1/7o8b9pf/T5X7U/Uv4X7Y9M9LNIxrx6JD/IjPVp6HLiq6MvsBOyIN8sKDgJLC7iiSaa'
        b'3EH0zEzvbSQwERBlnZnQSGBDn9WnwcGJVxFPP+nTv8TPyJ4mXiVlWrojktjh50cJRN/g/v3BX8d9nJJmwWs0n8JeYXxiXD/l89+coMFaZxzyrm7ijEPE7L/jjMPlWLY/'
        b'xh2HLuLqqBH9jlBBGiUfFstFEj+oeCRGrb7mNCeBJPpBJAVqNBofq6+NTSv6W7FpH1FCEgWkhHtYCWkd8GRVKNGF4zbwsfz/Av7KP1K3DsvZudsAkxSntWKSulTf1ZZj'
        b'3jdNsE+HMMgLHNSASgdvn1BvQkd8dLiJ6JjvRrEDVE6MP7shRqQifgTTFR99vcI76uVYh09vrlj61JmKnMr6/Eyfcduaqlt3tObZ7stxG84lPSV+bcUXcl4TOm47lCg1'
        b'IXbEXjz0bBm8EFVSW9csUws4BfsfsfqrTf5G4RosymMU4r3SVatjVq2NpGwX3es0Ae/f2uvcVokD87LbMCKSxGuOJPEg+tzU+r1Zs+4F8f1WPT9gcQ/RLm5L/MmcMHpe'
        b'f3txczkG7z9medOkuPsnoVIoJpmzoUSNVCG+ZVEGA7zLlMSFA5WJoQga4GgEHvOLllIs1pZbUvVvDH62VulEcvqUiLhFvNiK14djcJxJqJfi7BSoKgCdi+c53ljATZtM'
        b'10utKZYDzC7T9bIXc9lYYqJn5nan5cR1QukXEEAQeJJAXgUNqJE+88cgKWe2oltAYE23Jas4FZHJ4xq97dpDB6WkCkk6Hq7ZgsoI4TpEcPie52askLkv3cglkKGNDBIR'
        b'aYoLMjKUvW/5zZy3OBXR6Nyo2R0anvFLlpAb9odQRzC69Rtam40DFl+ClDr4FQk/S904FeG5JR4XPsNTEPenlJP+8RW9z38WFjgcknnM5vt9vS6C3Vd8cspneMLahAac'
        b'gdOnKsKfXzNcfuX2Zzd4InhbfvyCiqgOnt3nFBo+iF+aOSglDIsuzoJd80apyBH/6bOf1uVTI3aTA3ERNm0Vfm6VTY8hijN3Sa1c6/iW4QtOL+CNpCvgx3/yA633XsnI'
        b't/CfwW1yTn7qdhj97tPrrm/hhXSu05FzFD1Lv9q5lyvGFGOa8zJu2cV62jzVDPP09OI3yP3ctvHH6XfPeEcGby9+Az/8Gbe9w5IK6AIzi8EEaudD0WxueIygmPfFzMKx'
        b'+ONDHXRULfi9b359aW7IK0lXZ8g64j6Ntu++tuego3zq97JhFZPCeuYobL89xkcsnsml/nCA731feLi8okd3QV3+gk+ebfg1erT7m781X7nzxU9fvlb2W5Lh+bLKa+cr'
        b'sm2j7Le7Tlr6RWyun5u1w1v5t5VhMVbfFHfeWJM+/cHovZ9tHJP0o9vY+KWp99AImxaLiR9f00l57871bdxzxsE/7Ij1vq96ZVTdB9bz9jqO67m+O6xt6Lhgse3y3zbs'
        b'n9Xc8MXOk0M/Mtv01ojI4jtN1zdFTDKc4l0q91nlK/de0QsVgzfHeN3+ZOHsj0Nedr+9t8dv+LDV5ysr8txHNoc4LJq5Rm80eu/y1Zmfh0w+N/k991G+X9UXtIdkmrm2'
        b'GMR+veto+LIgwxcvjz+ZKb7aubp2KBpd82p7zXX0XVbRF3cMCty2HH2wIvXPdalL7hR+8OLyV4wP7h+5fHB571ynaZ07j3+4cFjv7aIpv025d9lzvN8fP3x28MFuU/2A'
        b'tZc+Ub2y5NMxHw7/zPTSgdZJ7+/7esGt7jfdNuQv2yTO+v3mzQXfvPnq2jNJb1/76Xb5nzNrLif4udW6LBm1emPDib1ThvRkvFujGvTDN1NrV+3/WZUiN6Lc4Ww44quU'
        b'EzdJMQdH4Yw4jndEO62Yx01BHOTErVVSnywCg5RABZ+cFsRYx8q0EZiTPUL0Lf5YABaNE2CROg8do04EKdCEDqB8dFlJaT4qJUg4CdTzW9AROMji1p2KhdOq9MzMQQZQ'
        b'ZmiIzspSMeN8Hp+yqE4ItbNnqMOtNdpg2fWooj8rPYb5isw3hy5U7A8njOACcSvPF8wneFp2DbUqFL5qxhWqVohDeLMEOMaafh4VoJMb0R7lAMY2N4tdPTh+pJElZorV'
        b'NepJediJW13PfFDOwyF0CD8odyZeTFFQJF7Bj0RnoZ1y6CsFq9VoGC4aDlM0zDzYyVxu9g+BXILwLoZmVOhDkoRKoZXH5HRPJq14UTIBgWCK6uOvHu5lfAwcxOw2RYM2'
        b'2FlpD7tpUIjPu8HQYq+WY0JJnkZMuf3kYs5RIPbkzVIm/pfm+3/jID2AX+47/ugZWvcPzlCDMSIamY1xpxY05pqEptohfKeI8qKEu2SJc/hsGeZTRZQ/NaD3igVmJG0P'
        b'5W+NKG8qw3cTTpS/K9ORUT5VX2B9VezMatGnJ3aalZYb1ekVpUSlr+4VRUelR/XqxcWkR6bHpyfE/FP+VJg2jLxzOPk1VHuYk3rM/ulhbt37mMPcBj/vjLZBZ99hjreP'
        b'Gnlq4S8yg9YZq/h+fBxplZZFJE4S1FYuiBVqQyXw/y5UgublD8dIwec7TUNKFMpYXCRYdqITxcvbBM6jczpClLtpWvw7tq4iFdGtjn4u4esVX624tcIv6naMPolsww09'
        b'FewkTHF9uV88FeETnRl6B5G5GrjyHP/BypOtTrPWrgIRm7PhA71i+rNo/MNTSx4O/6dTa1T9mKml0XsvR/Js0Ppzaroc7B45erZOGFSZ/3+Z3NWPm1zhI5MrDIifpZco'
        b'pAkSRkmfWzuDzVxC7Mpo7yhJ7Cd+utyIXqHPyT1/c+ZU/9XMGaxNG/HwzA37q5kbNnDmyMML//HM7XnMzNF4CtWoHroUAY/OnTc6Ohod1FkBBdZPnjwiwhaQ6RMUiGJF'
        b'/+3eJFP3aGoL/QBqY+PhvEjLxIutpkMHrz8GdVMW97n0EfwmzNrrpFzf+rtNr4h+OdhCSBt7aFiU095FtkzjfTNMQPT7686oNkfuHrqIo0r3ZQ7ofCic5DgndJpD+QSU'
        b'UeZJb48Zo1bWZ8Yl1I7V5Zht8QQmXbmhzmgPyYjQ5u0j5MSLeME6+/gedIBXZeFbfg1YOrzE0wDGGs2Je+ePQumcTyVLdRe/aF4ZUrWre/f+huuyCWNK/SduCEyepe84'
        b'zUQmD4uInWIw7nj0G+nbVm176/tL925W3JAbDF7lM6XGySEv4Nzu/KhIqxGK3m+3lH3RvaOzvt3/g2EL4+/+UJb84HPh3nf1Bj1rPavWUS5hif7gbKDC2YHYc8RQY4ku'
        b'8c6oZjzjGjqDrRijBPmoSMssSdcwF17IgwIlIXzFW4AkYybxN0owxxKPdjBWa/tKBcm6PXpoP63fduii755kjjqhhTIzaIeAE29BBSN4OzhsyMJD683QaPAgbytR4qGL'
        b'SWpgbxHaN0LhTTVwxM4umkhiGHcx3R9cRNVQ34ei9VhPNYNOMx/Zo3g3/aUDWa+M0NyU6NhIcmYy5dg/2LiSJAOBAU8z2vH4SL9HXCDJ0U48WrTbOZrUI3oIw/VIQ/k0'
        b'W/JMtKZl9BVL/ummNtn5mE1NwUxHMVuLucb9MyhN9vbBpy4b3REoX4SOmUHTI2RTT/1XZfVQ6rRdwl2yXbqxfDRfKqC6Ir4vdlGsJFoYLcqX5AkWi2J0onWixflctG60'
        b'pJRfLMZlPVrWp2VdXJbSsoyWJbg8iJYNaFkPlw1p2YiW9XHZmJZNaFmKy6a0bEbLMlw2p2ULWh6Ey4Np2ZKWDXB5CC1b0bIhLg+l5WG0bETSu+FeDY+2zpcsNsZX7eK5'
        b'GOM87qigTLDYGF8lujE9TNRGRNvgO0yibWkAv5G9uv5RScRx8o7zgEQ9JNOXTSK7xNKYDUzkg5lOQsQfoaV6GoI3h1MHiKL+gHSIyaGop6Wqor9LVe/k/cdcUQNa25cr'
        b'6kmZmciGYcmhyCeSAyqKvSJozjyb2PiEx6SZGrDCyCJ/nFowg+jUoBXLR4V0/6OGDSSXTKBzhBp0BidJtC0BN1+gO3Es6mAwuDOwD1qkKamh+JrmxjAJ0VGQpM3qPL2r'
        b'0B4fG4ksBO1iUWouEyc0bVAfggZugfN2zCDfvdRdgc5hsY6k49Xm4kX74RKLu9RqiKoUvv4uI+NoUHeFgDMdI0T7Rw2lKqTNUeuV4335pcmcgJwf5+HyehYN6wA6JFSS'
        b'FNOoETXQNNOOkKMOzoO2JylRF8rXhP2XJvOoOmwkteeuQKeB2O1LiW87KvYjWQHQQSHsQMdnJaIW2p+tNmFKOOnt7+JMnjYcKbT3XbgeFVIlVRy0eyltOCaFkd7AeX4j'
        b'1PiwzjaIaIylWT7+jvg6T/Uj1K2nnLkX5WPJL1uJafSA5OmoaTI7/M7B5WEDonJdSof9aJcNdTWBk45wTkkieY1eRmN52cA5NvyN6ET/cF12yXB4OZRmMBtWnY8Sj8iZ'
        b'hxLXp0ZQVVnZelHIaI4GzpPtCwvnqJeTDqqDfBJeE5/rqM52Baqn53VEgo7+cwJ6b4KNcg7R2hGuL2ulnWJAXC24pMdCa6FalpCowEXIrxaSTyv8fpTOZAc9qp4Jlf1C'
        b'fY2BbXilVqLzdCCXQ6ejJu+9JtIXdJqtRKVZDG7auBGaFcaDBwT76hFQUOYYqCVuiupoWY5wysnnoVTISSJaiW4QNCvxGqHCCJ4sA7ykZqP9y6DKJ35blligwkc0N+vK'
        b'ic1VU5PQWNk2n+odJmPi75sqdKb84jh1pmHF3NU5suEHbHb2XJW6mX1lfLuz8Wap77hbhq9PkN4LKLf2v3XT7eUre/wTXzyQqGMd8Gs8qh3u/nzHMzvDEw9/lGxQ/ZzV'
        b'wUq3Do8IoxVbN9okr3TNfm1YSvIH10+tTgs6MumN0l9qJ9yqu3Xq1qU1LVO+/Cns9NxrQ0Z9HLhl36a6u97XZmSd3vTysLVx763cJngpa7r+uvwfS20PXU5rLRvuZbk+'
        b'4Kr/jczqb+tHTP7eTfeVK6/dO+yxO8rv2g1pxPvrp0R/ED82NeCq31Xft738667ZPV/d/UOmPPL7WWevnntnVsvO7vTPln2a1Fb16rMzix2WbuhdrCcd3WMxS//nohu1'
        b'Y980nnPN2yLeosHpTac7h53mPJjrM93hpt3oe4edTG5cfiHk3cXSkwd3zf3Q3PfOsQ9vbKi7u/XHj9ZfKLj/me6O9Xsi3i2UW6kVLHDUV82VEI6kEeXCKTiC9lIFiy/U'
        b'oO14vqDCz9GF3SRN4NHRqeHMfHpoMkXqHozELCszJ5AEw5uTExngv8YaTrBEK3AWTmmU/jTTCtqJqyBSlZsl2vuIYQCOpmjggD0soAq6YExyH5dT0ia24v8fb98Bl+V5'
        b'Lf4NNggICCgouNkIuFBQXOwpQ3CxpwjKkKEoiOwhS7bsIXtPQZJzmjTtTdOR29w0TXLTdOT2Jm3a2yZt0vbmf573/T4ExcTY23/9NX5+3/s+4zxnn/Oco39FCSujuFUE'
        b'YZ8qlBywtlxmbMrJImzUgAK+JUIfdqez2Kg/jHOx0bhMTg3cYcJaF1gSw0sVSBkemesyh3BGhXsx3IFZ8l7E9ATieOHRgIBUAQ+yPlMo48q5urO6E61CD1yACh2Y5NQ8'
        b'Hc4/tarTyXXHgycTOIhEpktamRDTuw0dy4xP44AY2n3gDh+zzeVuJBHfs4EGCevTuC5mCe2wwMM9T6wNJVbbvZaZn7IP7ViJlsClRPVDIbstjvPXvaT8T3mnCNvCNnMb'
        b'0D9uJS0vwdWWgDboMccqHOfgohMBD5aL1XJsSk1R7IH3U1Sgi1dk72zYxD3AcQw5BZHgzEZowzzO15iZYUdAJYbhAM1SnqGB3WLMwUa4zXvt+qBLA0pO2lhKmIYy4QzO'
        b'yEEOt7oQe9aDyEvKl1VPiC/jbUcjnOOaNcBdGBTwltzTZfhkBZCPFQ6p8us3+3NjhdvacO12pOJSNVrsq3EIxy/w9S6qYCyeO6oL0LvMfDQOimEBGqCMb6TTZMG6BpJ6'
        b'iZ3Ys6xiaqiKoScE64xln+1uUnzRKyDsNgynuM8yreI5FXfBLSUlVkdChYsOK3B+Oa5+hJhvo83+qJAWrcT9IhKp8jUl/qElryrxurG/l7/n/3yprqDAvSO38rdvfIf9'
        b'kqku0SCfaKAgudykt9oZoPDcXk0R/6rFKmhdYVYFKx33vFaFIEf/H2tcaHpqzc9fqX3L15Wl/wGtj++TsDzDcouEbVxrAomS+rhU/4v1RIjha2/LByfHRid8TZeCH0kX'
        b'xE8v7VLA3gpNSU168ernMsFh1mHPnPbN5WmNHONDow1jowxjU/jep8etjy9D4cUK8wcLvuYE3lqeWZ+rMp4UGRGbkpj0Qr0gWIHzpP/5uvP+2fJsWySz8c0f/qky74rB'
        b'lxMjYqNiv+ZY312edzfXESA0OcWQfyn8/2QBkemR4alf1/3iP5cXsGN5AfxLLz77Mk5zN/WePfeHy3ObSJErZQVpEZbxA7zw/uWDIyLDCGmeuYJfL6/AgKMq7ukXb2MQ'
        b'IwW7FFufOfF/LU+8dRV2v/DUUdKppY6kZ0798fLUO1dazgzyUrN59fQrZuek3JM5MsLlHBlBoSBXkCXMVLwh4JwBQs4BILgp9F3xeS0XKxv2aQ+5wtfk57x4n4AvA9fs'
        b'f8xhYFpMJNckOiWGdeJ+jIdJkXyrC65Jc0JiytN+had8C9LDesrp/0ZJmizXgGB24y9ZA4Lw81wLAq4BQUKNMd/qL0HVkld1Vyi6UA7lpOwuYfUzyuLnSy9kM1n7/GqI'
        b'4JacfKaBVMwtb/Vx1k1UdGTKs8vps1k/VZJ6LZ9bnAtyVNYQ6Fw5WZgms38UJyRaIN4zTYtaBgVWPlHEyY2ZCgJYlFOGRdJUh///xXSezuqi4739aYkMF9P5wRvDLKIT'
        b'F7U5/pOQ0mgupvO6QLBtVty787d0zIZsp3XYD7WsEWcpDK4+bTrpPuVvivokFb7okasqf/2RJ0uPvFj4RKIXy4B5PPnnL3Ly6p+vcfIs+d5SPX7lsSdi7decOxkV7NxN'
        b'lOnrGpGkhfEeYz0eIbAC22XUmH1cvonze63LwiL+nXPYK2MjhAlWKyQ2ZuArYbI1/X7m71+98tdfRsREO4e7h7qHxv3igez4zze+WX+63jcw2+7VTfmbXtV6y9b9ZZXm'
        b'WMG4rML7zZ89lQS3dkJcUpQEVzimJRJ+m2NSEanKK4ky1z91VPzwZU8ezupJf/8ih6P6v2vo2U8v4NmsmYu+8S0FBMvRt2/DoD2e4q4nWN5fMq8gEDte7SZONkxOiY2P'
        b'N7wWGh8b8Q0eX6FgLUEj5+nnyPnbsi5kbssQqhMUDa/ppm2IjZUfb5JJZnrqTzW9Pw55I8woyiNUJeq/6JPZh3JV7qcWjN1DjiSPGVVEGJ8M18j7nyClLof+uI2H6uN0'
        b'D+k2NRT7xelqj1pECIr3mIWce80bDV+ueKUFmn9wukvtJ2LrOpvNgrE/6ZRqWBkr8EVYcrAD7pmuCI2oYju0w7TY6chhzhbfj01YZLrKI4yLUdcPI98N1RgqmDtzpYsV'
        b'bkP59ZtQLWkreRjmTVdwGs3dYijHbmyCuuMSY98WF1f6cM9j+3ZxYKik62MGdl/lTXPW2mLIBlqz+CwaU2w6Z0rk6QKDMgK5+C14W7TthiKXXX80Ctrc6HszOYGMvtAO'
        b'RmD89CWJ+PrG6JhCbHIwd7IcBZ38tpJNU4YrzMj9X8QVFhHKrDIcpcM/FnDPWNJjiXeIHv3bi5CWxh+/zoSVrkRS6F1zrXocKwpvcGG6SAYiMbPg2OEkKYsYxKRWxzsK'
        b'UvX/HTlek35Hjldx31GQapzvKCwrjFHSvfHz//OdK1dwo2308RIDGZuEFclQEesLRef+NaUwVGXUlbVFnIsdB7DBGSdgdMOyS0mJOdAesgITTwl0DcnfycVPRhvlanRr'
        b'BBGiMhZ/ky9YV6BRoBkl+/xRRv4t0jqUI1TuKHBRxh2xgkgFSVxPgY0fsa5MyOW+K9PYMhGqEWrc2IrLv8mStqsesZ77VolbkW6ERpkoYif3jgb3llbEhjuK9Lsy/S5g'
        b'T9TI0x/dCO0yOUVNRc2IXVx5D1lJj5d1BaoF6gXrCzQLdKNUIjZGbOLeVeHHpj8KNYq0Zr0yccRuLsIqy4X/WMsi1QI1NmOBVsGGAu0CHXpfPUI/YjP3/jrJ+9zbNfIR'
        b'W7j3ZSVvqnFvadMbilwMk72hyu1xK9sj7UIUsS1iO7dLtQhNzqoyekdVQiT0V2h0ZNIv9tIBreL0xwxXP8HEA/2dbBhKkmGlvGCBxtAUw9Ak5ru5mhpLdLBqoCjS8Lnn'
        b'I+in8BRmE8amGKYkhSYkh4Yzozj5iXikSwrJn8QkyVTLs4QmL5tTJLgSDEMNo2OvRSZIhk1MynhiGAsLw7TQJNbg7dChpwOezFJ7YoPLcu/4Kb9jFoYnExN2pximJkdy'
        b'O7iSlBiRyi136+pwr8Qbl0Twe+oixuo6MMs1YNjRL9eBEReKn+sKBsnxX5x98pA4cD0R8pWK8cvSbb1Q1HcZqsyEo6NdeRRr2mrs/Llji7AwdOGcWhGJtCKy7Qwj02OT'
        b'U9g3aQy6YRJvUOQaqoVkQRKjnV/TU6Z8WixbJP0SlUrDhUZEEKo8Y00JEfR/w9ArVxJjE2jClU6vb9BrxIK1ItnrPFPt6fM2XDyxsjyr83LkDquwzJ2roXra2Z1UaU9p'
        b'xztYwgJl7N4LD1OZZWGGk1zJeG4Iu/OrB6FXJa7/a1igmGWiwcUZY/2hwiQdq0njdpYRyO4WYj3p6Q18CYkOHHM2haID/LVhGHLgY8BFdjDl6wQT5thDFmC3tUBsIVCz'
        b'E+2IdeKywlwFZ1Z2GbPcbsR0JG9vrrnYAWNZqNyCFdyt5HhccjA9BZ0i1lsl+aglf1Vcmc+8+oN1RPzczjhBKteSc84f6t0sXPEuzEn3g4VcC7MyMyz34Gvy+iTKYzY0'
        b'QRdnY5wzx6Xkq7IsEmuGdwVQDM0wEBtp8V/C5Lfo53a/4ciKpTixlcqrR7/w+r3F5epLohw7x7bkniMOW0/89t9fibiyNe9QhcqjnTNGF/5H6fOmgM/9FI4fb91xUyMs'
        b'/c5vnMsd59VxYI9md7/1xd24/82fvvXueOqhAaG/h+vuhXEXj+8pDG5v3vjTIQOj03H3N2wJMFpMO6g75qOp+ju50OtVcWNqf0S3ndd8orDpE53PlT7Lh/g7cw+Ki1+P'
        b'dcxUv/X6ld9typ3/5ZdfvTt+tN/yH8naUWcyane3eq3XiD7/YXPRvU+XbkV+bmv+7t5/2931KOXt9p9/Jbyw8ZjnMXdjLS7GdunsdpalNQ+V7kIud2CvF5+fPY2V5nzo'
        b'MEFrVeDQ0YTLwNbHPHU3dxez2BXRezWo5BTE6zjqwIc0PWy4oOawIw7zdUsXoAUn3dxN9OHRyngmtCLfYIGAP5e4nIblHMRf0GTBKy6elKq1w41P1sBaXDCWEyhqiUif'
        b'7uT7trtv34YlUOZOuoEnO3wTOYEqTIp9rLCDD5zVXIN66BGbWmIxUx3k4IHIDBa3ckN7yu7EEj6MutVHGkhFVsOQK82SD/cCSdF2FxpilUBmqxDubzvIAcJhN+bTYxPS'
        b'THcuzd3Jj/cHzBrDrCTUl5jCzF0iNXM5gQ5My5AaY8Wp4FuM9zpvWzYQ5DRF68R7+fDY3dOHWWVEN7i7UdtLEt9dD3ViuMsumvD1CcdhBhqgJBR6vNyXyV3VV+xBJH47'
        b'hZEE3oFRVo6TXd/FIhcW+uQuMkG5pZs5VxKTVTtxgjF5GrfPj9uUfDyUSdIv4iz5BIwmGE/nK9wXuGAOdymH1K665UutrLTkXqzkS0vu2s1SsGmOIofDkunkBNo00BJO'
        b'BzydqfY82eNrxedYL6RvZT7YKnDdxlW4uu6sxruGUP8rljGvwmXW63+lJFKQxNH0hZk6q0X02p3Il+Xvimja1wQlxfyza8TQ9JRfwATR/fEaJsiz1v1tevfKfr3X2U5Z'
        b'4nV+arLluJrNskh/WoavkNcvGGjjYkBZXxcDOipdYtI+lhG3UryucntzbkQu5XDZjfi8ju+nLof+f3N8xxAi5Qmf2JYUXk83yX1fjvdRG2x75eOf+0nb5HI+6rf2SpyX'
        b'66DzjJRqH9MsMZhpRrdZ8t/gpU4qYM1bdz2BDcnh8cHcLc9v434+8SKUoNK3hhOStcOEFp24x17IKfbB3cscq0xX7hRreXckjEDZE65o3S2q9tgBVd+Qn875xwqE3zo/'
        b'/Tld0TKenEc1BXqhcZmZSxbPshOL3E1czaDfj09UZF94ubt4CE+aCGAAipRtRcGxe/UtxcmMMuKaTT8Osfjwk5DXw4x+YxbqHhofFR/2SchnAf8VkhD1SUhxtKvEuV2j'
        b'pSDcd8hYzBVWTvdnF8y4mbfj4vLka4mRaKziSo2rYhu2rUouguazKy4eK8Ash3ohLtt4zMNZbFiJfQzzoOKaNHPh68WC1HmeVPS8mLjaK/6UX361a9zjRbBSo3UNrHSi'
        b'Mbx1ceT5sbIbip9wlOseV3Xxxw5jEZ8E2g5dKRJH+UNo4Rzlblu5ZMm4Q3skrvXbXpyb3ABbYtNvD8hyrMcs5/e8j/zn31/hJf95w0/qfZmf/MZKP7m54NXvKOZPRz7t'
        b'J/+aiEap8MWd5QHqSkoymbrPOsgVPvNvWMDxFzk69f41ROszF0OMkXnwns0kWM49ywYnJiFLbEJ2mU2In4tNkKj5sucpo9EpMoWsZYkgXekWeba5fTkpMoo3bZ/KeVnD'
        b'Ik6KTElNSkg+ZHhsuQG8BAIhholhcWSkf4Mlu7ZElPVMZV2EoZP08UUskZCBv/cZ84Aza2ZmQ3bQ3r2KcYkJnP16DAqD3J6weldbePRdxWlleSyLxpLY4gsvi5JZfdrt'
        b'wzc/Dvkk5L9DvhcWE9Ufyfz+gS+VvheIoxVjgQ/uGMsabX/1R6+//Z23X/YWd13aeEl3oj4nLmi8fqKhRMst0LfeYXxfKRHCRkHZ6+sdTT40luPvjgzCbciR5nBiAX+x'
        b'JBtL+RQ4pzipXeECpTAlsSyux3KacgAs7ePNLN7IImhUSgwtqL/Bt4u6k2Z7/RaX4c1ZaNgGfOM3vLcly819hY0Pj5TPinD4HI5ymZ1e6QlQBAXPqvqQjmWriPjZSuvK'
        b'YhDscosEcURS2fetiPqKCnddVZUvC7HpCXpaMTw3a58kXY3zjj9WsNcUBX0i/rHHarUzDeH3IrSvVb8G7X/NWp9N9k8lVXwLveDLqTUJPuXp1JbEKOlViX89/R/j53xO'
        b'+l87Qkc66ZainwqSmZkrr7Lp45DzL/3oZSLC2vb8rSUBmlb1OROyAsv/lKnPHzUWcRfkse0UZHO3P1k66RzrGcj7/zfhfZlMqPXmo1292HbGzcXBfNWtA5jE+9L41NrR'
        b'VTOplLL+lugsuMVyM9dEDcnZ8LO4iKSqrqto5aQRL4KdqoXPiZ2SJRjzhPGOfHLotcjg0GTPZ7uKWb6GREbJcSaR3Ld0FBPa/iJsLUexFHOZFz1CUrL+ufD22LLHPzIl'
        b'lKWwhfIpPJcTr5HQYyXmpeP+XyE9/44EWIeYP5nz9ZsxJ/Ll1OQU5kTmiTA5JTaBT+xjhu6aXmDe+F2VjsVc/TT4Wh7oZXpja00KTePBRXv+BjJj+Py0w1jJk+u5Fa5l'
        b'9TwyVhgM2SRjz0MOd+FIuAfHTAlbsRLahM4kbXQ8uKIrTWUGvv7rrq27IiN4479kGoQpD17nax9Fs0KXP5djt2I6rHcI/JI+FTKPHf0UCLVxpl401Giq8LQAG3EARmLf'
        b'PTwkSG6nX/3vePn/wEpJdExF9ketEW/5qysrv6J8W//t67XmJ3/kePsVbe3hkOpY/TspF0N/0/PGWePWLucPjhZUH7DXcJr982sRRnvNPh381eTxjt22ejWaSx9Vlo5r'
        b'nXz/xPq4KvXhNzfn/y5XIVw1tTTZ+8fef32tsrP+V45Nx31SqnYHHC3WSdxzsdTjrakf4+8+Sb10rvuVM3Flbpf/MVV62O93fx5Jrb9wpP73xlOLh4wVOEFsl7iPCfmH'
        b'y3c1hnW2ct4ytzNqyyJeVuB+mhPwnhd5j+fda5krBbxIIMQyTr7rbeE8i9vgLjaauqrjkgcJeM6zqJLA6xVdJsqmJtKLArKYrXhYBK2QyzcZxeG9MCnxLT72LIpgiXMu'
        b'+p2S1MlwYzXbi8+7rSh3F76PG94A5rBS6grFXkXOG4qNULa2dDWWe17/3DvykhuwHEf1/tYcVUWd752oJNT/Sl3M9QsRyvDffCUjUv9fGVGm9hrMjiZc5ZjjdAF30Tfr'
        b'DWQ9PH72sfLgSf9MZOz5+Ldkz4Ic7b+vwaCfsWaCK+cR5Di04nICOB++P8wSAGTiQxOi/RzD5VfQO9uShpTeAxjTZnc5mRdLiQvLslCwqECtQL1AXLBeEvnTiNKQMHP5'
        b'QkVi5grEzOU5Zq7AMXD5mwq+Kz5LmPlNmTWY+bGICJYznhCZtjp5h4W8+PAaHw0MT0xKiky+kpgQEZsQ/TXXOInFHgpNSUk6FLJsUIVwbJIJjUTDkBC/pNTIkBAzSbb6'
        b'tcgkLiOCi/0+NVjoM2O9huGhCYx5JyWyLAppmmxKaBKdhWFYaMKlZ0uQVUHBJ7SvNUOCz5QrXyeLGCBYzDL5SmQ4t0MzHsprSpbHdxUSUi+HRSY9d4BzGcn4ZTy+dJAW'
        b'Exses0rEcTtKCL0cueYKEvkMbykcYhLjIwixVwjMJ/K/L4cmXXoiPr98aMmG/JUJC0MvlrObFpvMr4CkfkxihOGhqNSEcEIPekaqdIesOZB09eGh8fF0xmGRUYkS+bt8'
        b'bZpHglSWis6C66FrjrMSh54JyeX0uUOGT96neJxjLJ33WbnGkrHCrMOeHmXlrYxveJ9xCVJWfL0M99vYmltx/04lTkNEGBEpPSrpWIT6PJasnfp8MjIqNDU+JVlKIstj'
        b'rXniu5MNeVU345s0Gglmsq1cIWOCPj2HPrZK0VGTML3Vio6RJxfJzdwCk2QGLyZbkyQQJgpgBm7f4h1kbRFAcvKh8rWrpOhgoQCbTSHXWMipJz6RWGXoyTxvZGFDufAE'
        b'3vdIZf4qnDoNk/SKD68pGVmYG2GhpYmLBylN/X5XcDwlwPt0xjUWr4YaE8WDuAS1XAPXQ1Af9zhED3WH3M448zcBH0fXwy8qQLs5znDK0wFnFSUD4R6BwDtEJeyyFV84'
        b'Eu9CUSTTKqQhcqGsEZ8qaGZs7iorsDeVI10qT46/FN27HZdMscp+u5xAuF4ALceBH7rihPxJYBX/DEPM+tdJKpRoZcjsLxFxV5jNNPbsl5Qqtxfv2CLiriermDjE8Heg'
        b'oUaJjC0WelcWQOkJ5SRbrqwV90J1gEKAi4i0kZAQlaqUIEEqc3Jhe9ZB7go8dkCLrzPnMHah9ZeaMoVzeS/0g7OZq7uFi7mJnABLjFWuQqlDKjOXcR7nMPspjbXU2NXD'
        b'Hfr8cAL6JTqrsZwAcnBOETrdlR2NFbiTPoODKVjirpH4+O54U+hp/q70nBAXYQoXuLvj3M1x2loOf3V8XFWPddqbOCG9PA4dmH+YL3F/9zxMu0kvZM7CQ+ndcUNZDu1i'
        b'cWIj/bx3v/QKN8yH2fH5au3Yip3S+9sbME96hTsM78Vx817CKew35S5i2u2S3N8+DvNcgsROrGRNX9g1y5sbn7hoyV3fJvweM1bmtq2diGMEdT2okNQegAEtHOAumB91'
        b'2ynNMIUlHJLWHSg6y1fnL4LmgFUppMcwh9Ud8MEKbmQ6ijbsxkJPVn5AUnzgjD0PtBqowyJYkHnsnWJKJf9b035fN+4SrnewtPIAjjlzYNmN01aPKw9gAcxIqw8cTwvn'
        b'Qd6rjtOStFV9nJFUHwiEfJji9hQdnyhNi8XbVtLiA91YzoN9MRKzJQ5C6DVavtN+ASqgnq8/UAXV2OHG06TdCamnIBKG+MUvQs15X3PsOU06tThSeBi7D7tBD39ffwHm'
        b'zvqS9VTh7+2Ai6zjn7kQWtyDuDoCv98sc7NCQlgmmWkCbjhFnMFZXEIWP6n2khGIVAS4ZJ5srMQ36hk1uJ6smpSKYyo4Rvg8rQbFOJNCJxEndsFOqEzdJWD1Re8ncE8N'
        b'wQT3JPdUMk6mMh9IjxjvYz92cXiD+YkOywPSY2nYeDPlqmLSOlU5gZFYBm9DAXZyhchOw20RTqTiZPJVor9sOShTS0oVCzT1xQeyiJWxsFzgNchPvpqqRCMZYC0Uq+GU'
        b'IqHaZCq9UCZdwNGLcrKsnQNXWEIYIJC8AMX7YVD6jGak+Bh20BK5JrRNJ7E4+SoM4LzkyTTpCrfAsMwuIxzkFuh+HO4sD6Z+lsCShJO0wFPiQ3gniO/IcUfrxPIjacST'
        b'L0OlnEBdToTDWpJt4rAOdijjdAqtRUVxHen36zB7y00RTBBBlHPVLPTksuhMvb299fXoRGVxTgiVxKim+a5Gwxkavh5Y6YtleA8X3X2hjFX8bBTidAbe58jIHkaxf/UU'
        b'0CnPpriRyjGJG94wn4zTe6FDjX4UYY/Q5IwVJ2Wgh9BtCEuISbpZerh7+bMMqNMS49zM7aAPY54u7lhMvANu+ysmK+IC33JlMAuq3bBs3RaxQHiIUWOLPN/WKgBzccKZ'
        b'OIebOZGYp4xgfVoqNIuh1jiGY9y/u7pJ/T1hjECgHqK//8Z1npt/oWG647rgAfvyuJ7RJQHfm0Pw16OSD0YOxjLcvKo47w4D9CFDwNqNZ+AANnIuA3EaCbsBksqZAqyH'
        b'0UwcM+e+D8RcGDTlssMOQkE6CekHfOLY/dgkLGEcVLAFR2Ox/SLf7Vvp56/KJrOPWzy0Lp/+XsK/O6gPTdv/MuvVhh02Vz+/Z1852/EH+XfVDX+/U0Z106kWB8GU7XdE'
        b'qao5X2Trv1t4+O8at3/4wUsffy6jqBjkP9z/l/nMvt4vZe/NJSkJP9UpL6o593mg/l9+FvoXaPjVbovrPUe6zjYrnnw/QnOq/AfWPWc67Lwrvx/38nvbTdSyv9B2y/b5'
        b'wkfxp5aH9P/9jY/+tsElbr5xk4F2TP+d4q4P9jh9+n2fZJPZ7x/c9PKB9pTJPVMnJqw/DFQO7aiv3lV5vCSoJU6j6yc9BbMj3/NrVa8uGLkmW5b7cG9GcnH/FzI6LXBw'
        b'38e2H74vv1v+Kzufov9+0KXtlGD7yuYvP1e94Pe3UwGH7w38ZNul33QNnPpCNr2n6mcl6T8QHPjjS69/P/Enl35zdUbW47v/2eDnNRe4FKji4zT0mbtd9MD2j/M+c3vr'
        b'o7cszy2F/aP/s0t2syp/+Hz74a3y8b17ks/lD70UEFqLf6q7+tPYwwHvXbv8RZPOO87XWm1PHLefnis485eMsfeCvrR7/Xsf7Dq044r+vym89FKC9V9L5LUTP/3pVPUf'
        b'9v3m8ht7Nnz3bxN/Mg/a8aMP//vdl37/x0Lfi/Ol/d6Rvj5HPtBPHH/j30Iip9NeM/0vj33+lUkvp38n6r3wi0NhG7bd6oOoE29mPIBqj40f/XlTesadosG+0fuvpYdc'
        b'+45pQdT0V6FLH332p6DhtmmTyiKfri90zi38RdT7V5Mjir/ymTDXfP8DD8+pM93WJtfaPjb/e1rGpZMLPzi8cP3HOXKdUV49+h8FXH9tuC9C+0Jir9W/JbxWXjTYmLBp'
        b'n7+93n9W2ZdNeNxc/FP7L3++y2bTFjW7Q3M2GxJvTb/zj4K//VLl7JYS3zfT/vPPoha7rj98YfDDdV9Gp88aW3BxmZBoeGS6OhVCA5t9XMTQdg2HOcdNDJTgXHr4Y12C'
        b'WHUbn5Q1udnBTRod9+J+Xw89YVgghlKfDdwj2rB0baVbyAfvS8M+LTDOZavJHIhw43RFMfZIM+xgBAt4d/gdyIZ7kuywx7lht2kNLD8sIYVb4qEImDV1vQWzy66lazDL'
        b'O8qXcMRqZcoai+jbwF1Y4EJHkGMFE084l+LwrjRz7R5tlI0SgNVnV9ViE4mxYhtU4QA/PdyJJyB2bfTAMjmBzF4h9InFfAmPIZpqdmUeHlTZmh2WNAwmaVnMusEVQ7/r'
        b'Cr8VdIZyV1M0IrWXS87KhYgyoHA73gvjM/wW4C7OuZnCMK2YBHOGyADydigEc644Vxz3eFyBVwvbJEV4YR6H+KbXtZgTZep8fPdjDx/MQTu34pueWZLMQ2MS0bmSzENi'
        b'zdySrJywhTgcK/JuKU82RIfQH8uT+MIpDdCIA24uQYekt2xaceEAX9uC3dS5hyVmSFhSQsDwMGNC39dSzHp5a3HznoMh4vGSKF9SOOlnXIwvLYmDsM1uUpWnoXZFdLDr'
        b'DPeeHfPkkR68fcMKPRgnsIWDkxCHNzBtd07psbZLim0dH1csoV0v67syVlJtlzQ6DkxymBPDkkZ7rB7ru0pwl3v3ArT5SdXdazD3WN2t5V2lmKN3mtd2cSBKou7uhPIU'
        b'ztypx2YclNQrqoA7a2m8mAdN3ES7cCmDDcQim/fluQfUMFucCLNx3ETHIceDFQG29GL1CUkO554wcYRObiJoddom1XpwGnNJkVG7ilPrcFRoDbeFZtghqwh92McNtEkc'
        b'4CY5nMhdTHduFEHxhk18fmcN6VwTbnx7EijKwCVLFxgyEgr0HGXg/kYfPqW1D5YCuZrR+2Aa79rLCOSxXaRA5idfHqfgDD6QCE24nZQJ2b6847gxHaokhVYkNWI1zQ9s'
        b'F2P5qQBuctf9OMb/buEBDUZYTDo8zYz1MtAMFdjN8ZlzOKTKPeRlRpoAHQwjKpFAZ5/MUSxI5vp4W2XCKPcIGSpPVOfkS3NmYyefE9wjD71c3cZiOhE36PRgRZvLRNge'
        b'7c6husjsIOcHLzIjkHuK8GGYPg5d5o7L6pIhZ9CxvFziW3nLubnx7vxNuWm8H4oTatcYN8QuISnsitgnYj3aYYzHysVreIcOwtzYyBwrWQs4xWgRjJONXGqs9s/fbXrs'
        b'Df4X9u1eGUgPjYhYFUj/kqlY385Pvl9XqMrls2otV4RWEW7hqjwr0P/1v9BQUBEpCHlvOqs5o8F12ObzW7lPIrmVlWOEMn+VUWbX6Vb8+avcJwoGCtzIrB+KNufTVuBq'
        b'SMtwfnnW00TuczkVbdYDnFsNy60VfaUhVhXy3VBY5ZtNXKUaVS7nVpXeUOX+cH28v1ISrxG+XAEe3quvyLvml33lSV7MXb/sJU/yXu3p/+fKfcvz8zwemJuRm8xieW4u'
        b'SuBHn4pfLEpg8YvnCOOugIOx+B0FaeT08XVB1gV3+X9yghXesUCBgL/0w4cGFCWhASEXHGChAVHB+gKNAnGBZpSmJDAgUyiXK8iSzVRkMd0zghuyXDBA5qas74rPfDbS'
        b'L3xFawQG/K9I8ntXxwU4D3moxMO7HP59trdd+sTqe0EpEmf1iiHMJD7r8NCENR2ZYSwmYcj1KWJOx2dHIF7EOc/CHWvOaiJdnokhd/eH86NK18F7xfklsRAHLT2B90Sv'
        b'7Rg3PJEYEWljaxgWmsR5cvkNJ0VeSYpMjuTG/nZhbQ6AkjjGk2WH1gpA0PBrl8eQuLelzn3mT/8m/++39fau3ejHwJOzm4+IcdTtcUd0nycj28reK/LHyo0VcWSLTypL'
        b'8CDtcMpvpV/VmbkZsdDLl7lXEzOXHayZ2KsIZXowwlmrftAtDIY5FhPn4uFZsZzZ7C1SFtTEGzGz2Szh6l6+H8uWz3MqNz/ux7L/i9RTAq6maAPkmMIDplQX4l1f5hD1'
        b'cOfk7ZmnknjJ9l9h+Yv9ozLWYc/x07y3N9eAlP0JlpZK8rpA4IFzUfydd2fzLwXqIoHuqHW804RSpj1vvL/d4ODH/Rxne1bwrkCwx2Hfu1tbz7+1h//ZscOB+9VkzyXh'
        b'J/7DsgLDkHObzqsLuH6vHk6YZ0PAt94BkwJrqDBKZbwu2BkerLyFhoXM5VvN/LqkN7pIXOZclyM3H2dXM1e+Fh3p9nfTlNa5huAgd4hn5NKfkZsAC9j7RA7gXsU4rMMi'
        b'SRV9oW/Kqhr6mI9DrI6+GG9bYgXnq0uERWzknZ8W0LJcc9VXl3M0k3rfT2rm2o7mQVI1+/yMlq/mQw48UsxyhHIOUPtsxYIre1gTypB4Q4GNxFfiEMeD8b5BgGBSIDB0'
        b'sI/P/NL+9+pJGkxeMLe5Me8xxlyYYWWs6WOGBnYKMqAEirmrbi6nUnhlEJvkBZmGCtwJ7LUJ4rwnMIV9gnSsU+IezXBkfY/pQ2yaoiBWbT3nON0C96HyODQz3Zewp4Ts'
        b'rv1CGKGNdvHu3m4ouP5ErU9rKBRfgLx0SU9jKKTPmSvKqJJt0IKjselvhoqSOwjlGjaP2PscTvi5g/r9n124GdB1pCbicPF7Parv9r4he15GeF5Vw0F0vkL07uv7Q4t9'
        b'tu6QvzI2mFTc/HLdH45Zu9m8mv3SJwszif9p5zpVUPih3Cf/3bn1dxbt3zUw8phZr/k7Qe9vXnYzLhu8/ub7zuYed3ujmgPv36jYNf+dn/zptaOzn3eaNPhE7iqv+ezS'
        b'xuytUV2fel/bI1wS5Lz53+ZwIkP5vY+cTjp/5n/01QT1T35fbvvrTtVXt2Wo5HuY9aX/7vP/fV9GT//e1nC3i8FHXF8uj4ofCR24bvSb3G7Xq05THx7dMLM3+sAvauN+'
        b'vcPu0g/7hw78LMvGJfjGX3Ykv2X/+x98r6D5T5+7bNxg/v4Ns93vG7yXtu/LP4+9ZbYQ8WHkWMH7d46/eifIPu3Wvf8obNV4Y66t+K3oznM1Lye7NG2e/OH3f/boauNB'
        b'A8OtrXurPz8VcHWr55TKbbO5D8a97i+Jc7aIrF/9xds7L3Rt2ntmXsWmZeznx7+/3e/8j3/68j9efesnD1PCBgp3tZu9O/J21/Xvj8Q4ffrDjC+Vx0KPfvD20K9vzfgc'
        b'/Y/DbU2b3avN63zTKj+/kfqrpa/ERhP3UoM+NtbmzEMV7DDDGpUV5UWHD0XwhnLvzkzent1gbCG9R4etprz/ohUrvZe9E37RK6qGlkE/Z156YyeUPq4PQSZjdrxoG7Sq'
        b'87flanGG0DrmcWWJ1owA3top3KZxZTN3kY53SOw8mcK5rCd8cHLNTFUi0BwZHIFOKOLt6e5AORlLYgyP21RipRNvaS1hkcnqPpUbwsRkLe/mO1HO7MWH9GdyVfucPZbc'
        b'j05ZMMK1uVH1etzoxhOa+UycXGgNNKUVueCQO9uS4mYRVAjInGQr8iUTvUFaCX+TAjSKzKHJmjOZ3GBaZ7V9L58u0GT2vfcJ3spbOrKHWdrwwF3ixFHbDzVi8XmYteR8'
        b'BLuvBPDG2V2vsx5mnDvEVE6gB00yrC32IW7tSjDKVXLm23rKQXusvkjGG2o5y2o7dBisMiPFmgJNZkbSCeZzUwTiIJnd3CNOFyw8VhuSxZ78pb86H2xYYUjWZJEtyduR'
        b'MdDLXfYI20ynt7LFAzQrrLQjsX0D7915GECTM0MOGwRG5hI7Duqg7Z9U2jX/hYbbE9abyso8BM58G2b8/1uZb2TAWahwBhTfOpJv48NKhep/JSPiy4cqiZWEMiIFrm2P'
        b'jFD6t4yQNaOUvCviG0zyRp665BPffFJGTe5PqtLP9F9tbi4N7r9kaug9eZdhxZ54m0uOt3b8ly0gZnCsMLLU/69BbCyzYjKL5Rk5S+ssszdUpEVjvpWlJcjZ88EattbX'
        b'AUCaFGbPlnNEtIadxXRTTi91FXAp3rJkWfEl9UWcrSVm1laUyrJlJfPcltWxtfJnpZbV47r6y+mwXBbt/3HiN/+OtOAM/94a1SQtDE/w2TTcUp6RJcTliTPzix518fU6'
        b'uH+PFTN3LoemsFyQ5JSk2IToZy6Br3TzODPmyVp+/O8vdAtFgbcjWLdHhW9OkCWNtFOihFroOnK6kgfOYz3kp62ukR+o4MCpWllkZ4wsR6n7YFoSpsZFmOZ0tR34YJ+7'
        b'5dMl+I8n74/9sslMmJxND/04wcO8eKsG7NE6mXbrJ8eP5bz0oY+zzMwHShtPym7zrmt81WzGOcG1vu+drD+1NGeu2z7+gx9FnQw9/uu//XXM4bPdERY1Xpejv3/bo/Cj'
        b'7O988Pv0zRF/7PfsyZpO/3FA7Rf7gq6mXr6TXfTHnqN/e9XsUdhnF355Ic5S79xfXvpDg/jvQuvfblfe7Gksy4v0ge1xW/at1CSMgW/wbHfSdTn7dSf2Su63HL7A+wxr'
        b'vbesjHMEw6hElZD15h4IhnxBhvGTPnAmITOiednbT6dwG3KCVznXH0Dpqssr/5TkWMHYVVM5MlvF2j1fgLUTc9/Ee934rsBS9q7AdWXL3PwE51k96yrmu5oLrWC+3668'
        b'NXFW7n371eyV46zn6bsMFUnH3m/LWQU52/6wBm/9+h2yYq6ZsVeYK+Zf1ZDty76ns1aTwmNir0kq+0hq0a6qJbQG8zzBezniMzi3SOzlK/GRzLETGbH1mYxWsrEna9rQ'
        b'18/TxESwJquS8eSakmC3PbbyMayn0qKKMP9xWlSYjkIsdGrFmpy1l01mGWn6Qz/4eOZ2yGthgS+9/fJkxVhh7x1j2dc0wmOi4sPMQhOiYsJ+FS8U5H0m//38bGMZXl/u'
        b'wy4YXCZ5bIRSInvBZe5HMUwlSwNip6FAYkEkK/G++iGdTSup3uOUhOi3W3FXiS+ROTqGE4zex7DUHAtdVOJ4J46Lx1WJ6u8GA/IwisXw8Bt7pamH8gcrxa5kkRR9XoBs'
        b'bVXYhR6DJ92wT8ywqpb6hdWEubqC5OMnOFoLpk8NL05r6j9ag9aea7FJ77H1yHp6+jl6Jl0ScNrb11eke1zZgt2h5S7TcXeWuMx4zvHN6WQc++D2xQNl479aDX9OXp50'
        b'nD6qSu9XsSJ1SsraQpHB6uJy6jLq6goiLaGCmqpQSUlbqLBJjgUlCLy7vtK4aSHUSDAUKhho8Q1VsNoXZp6+tS0iU6pfYLRb9poztKf+D02bpnGdzLMq+0Rs2qMO+TiD'
        b'Dzcc2A/Z4Tgid4gUiUqoUiCb7j7eNlgHFZgHbTAI1SdPQocyVEGxUA8f0USP1kHDIZyEchgPZa4fv3Vky0IujtjbwSMYdYZHTvTUXSzOgBnog0GLG9DpDsN2N3ARe+Vx'
        b'lKisH+b3QTd0Yk/0Veud2GCF2dieAC14B/twHJtu2EMJ9GARjOk4XbXz0oaS7Zh9IivOBstITZmJtcP8S06bDEI3OR5ykw2yvm7hBZ1B+uZQjVN2MIe9ZJ9XJJCIrqRh'
        b'pp1h2vayCd61DsbSddgTgaOapP20QRV20J+HWBtyAhu9beKgLByH5KAFpjE/kRhBJbb44hCMpl0mhvMoi5WV8YPKjdhx6RzWQteBDTjsDA/3QCntvRLK15+EEV/I3e1G'
        b'C5jGxoMwkoUDPtAgxB5oxNtYQ2ZrI96NgQfEsjrStoiVoQYmsdXaDDtxOuagkh1OQUG4PmQ7XYY7ETRsnQcsGIc7Jho4YnksPsImV7wXhOXQoQtD6cdwFsbpqEbt5aDe'
        b'x9if9l7CQphKu/xwQhfbWYlPmPGAAmgOJIDcgzoznDl4ZKf9Di1NHA+gL5qv7z5nig3Yr66JBVgBU37J9G2lqtI2XKI3+nEMRmhJowKss4k8jA3nockaFjSwVTXMA8qj'
        b'U45g9mms2wIlwfsVcAlm9TVhNh6W9CA/ml4fvEKsv95KHzsitgWctbfEasKFWehJDiW0q8VGP5WN5zMTDl/HSf0Lm6HREzo2nsMRglEdPlCgzUwSTjVihwOWKkDBKZzf'
        b'Q0dZCwO2tMtBWt8M5AbSKdw1P0ooUZwO4zp6WEwweohtqjfFuIBFTjswXym1TMQ8LHAnGu6fPgblhPgqsIATG2440An3noI2e8jeAs1Yb66yF4fpmMagRXwKesJDtxtD'
        b'RYwMlBjesoTug6mZMWp4jzCyAx8QcEuvhJyBxQ2B0OgAjTAGXZAbis0mWGe6C2dxHmbEMKqINXo4HSp7Be/DpH9Q2lFsyvKNhwFsIlgsGtFGCE1wKMHtMA3Rog9NmOMd'
        b'SGNXBULdAaiHgjCivxyRrQdWwag5PTNO+mV/1rksTfXAW2F7naKxeX3G3vU4RLstIXzOJdK4vY9oq8jJwH1Hxi7CuLvQgINWLPOFMHQWC0OxKh4WaE+n8CEUyWP3Eay6'
        b'Dq2pbsdicWg3FhiRUrt044DFLci/qOgLs7pbWCk07F1/UCYRl0JwXIQV6dqhp/AOTChB6U1nqMccfScoD4JszItQg1Z44OXrbx2usWsj9h1zUtLSsNgjq2fjT3R03x0L'
        b'femE67FfFwqJsWSHYs9+OsqHcBvzxFjlCZU4ZojNnlgciP0wIbOesK9YBzpoG4w35QVbM8hCIQ7CZFr6RijbQvMNEVI9SCd8KMhcr0D0MBGFNTh3w1oLqgmGd+hsRol3'
        b'TSlEq7pi60ayfdrOBuAAkV4ezhhcgEUPN1iCXsUdUJVMXKEH8m0jceIyFgXCosUm5vU77wUzeoRzA1h2GqrcXNefT8Mpmq+HEKHlHOQQBS3RtnKscUBzt++ODV6QQwCf'
        b'CsLueALdAy8YN8ZZWagP2wHtOByY+hbDyNt0WkWEkvZwl6EkrXvOFCZTbbH5vAyN24Z3EkKh7aoyEWbdPm8z6FEPcYO+I1CK0wStBazTIzx6BMW0tXEYcYH8c0Svedtw'
        b'0fnIEXusd4XOCHUlzGM1OgijCP+3Q6PhNULgOtERWMgQ7LdwwepLKaZ0bBPQQwpTMcwT7VQR0TWFnbuQQNyjwwyb4gjcD1kGZzFhaj90Qi3WnD9FnHHJVOdMyoWL0OZB'
        b'K+zCCpw0IsqoPLrNOh1LtRRhbiW+EnXUem+kdUylYa654i2YTOCYZo1qBjQQt+w55r4/c2s4jHpev6EtvugEJTqQE0UbW6IBeogz5e4/QthbL38ZyqA3GKrX0RH3Ga6D'
        b'6oPY4AxtKfRIDrKdtHL163shW02EufbEQ7o3yMPMQZzX3UXIMA7z1vhIKw07EzZkyMTEYzbcI2rNxxo1AlQXba8HF2DCm06zYz0WB22OIVzLxTEH6CKQL5zfTcJpOChd'
        b'n3C3/bI9VoSQCKszhr40IodSCzr0ReyGjmPWxOiKCDNJfJ7fe2kfVhrF4YOs46qZLEMLsgmbO2DCytAoIhQmiOHMqGhhNVnsuSpY6Agt1n6EE9CeQYsowrtGMAXtMAB3'
        b'M7FDXm8HAfohdjkGWcIjbFZyNKFN5xOXbCPZ3XQSJpyiT9NhTsDt5CA60gaSiq3wMBNLrkH9BflIrLWPcrLg5PpdtxQSOvmpxBUq6JlaOyedQKyDpktQLLqmC82E4QRF'
        b'wnBoORtHq1wi839noqsjFiWsw8rIM/KbL+LQJqhj2GVJFN3huN4aHqb+u4g1uiqmIyBmm8ApGQs4YorTwlNbQqBNHhtOKwlhjCURlxPZ1ENFCowLiNvu2IDZVgTjev3r'
        b'OCwP89AV6WQEjSdgQJPkQeNGerxcFZvlL+vHEd40qhE51lsb4yN/C2do8rmONfpQ6rrlAImCGSUCzSMskfeGvhBGLqHCK+eZSnQ/AUfw4YUzxDAY/x0kTkBaSOJ+aNJ0'
        b'MD2tgSNBUBlyEm6fgnl1bHO6dY7g0nbguiaU+roHQd9OnLy1+UQIcY5+Oo6BywSUAWg6lyHEWkcbmPPbc131BOZAE9QfCSfJfJvOuEN3PQE7H7vEsLQeq/x11DexFEIt'
        b'qLjgHupHYFq08TkUT1RcHQjVFpDrrmWphQ/iYdCBqK8wDmp24e0TQsyW9Yb5iONwzzEWJo54wkMoPG574tTNTdhA6E98sZvmKxBcJgnQgWNy0EZ0UKRN9DJOoLqLzdaw'
        b'CKUbiUybd8LDLJy+eoTQtp7kXDnW2l3FjmPEUrIjfNIh3ymRSKAtCypsoDZrA+HVVEQG9kXrcjU124lVFB/GsjPr92MdKwDe5UT6EaF0t+EBWsZ9+tTpcCDdSZ3E4slN'
        b'MOFLeDgDkxl7ie4Xsf8ElhLk8kjotR7YwvSyJCiNMtzNcBErtY5y/KCDVpoNLbFQG7Y+85oHsnyxSaKtOqiKpdX0kVaQK4LyVIJ96cbrtMMmkqADJDiTA6HdAluwS9dr'
        b'nS/Jit44bWyPxHsudMQ9+PA83A+hJQ4fgWGi5EJbuIOM1Bex1p+GKLgYc41JIcy5vBEnrhCLGce8HY5nlXBUz8rRZzP0iVPvEmJrewQQWtMGlpUIU5wVXsbyU5Btf9AU'
        b'ZvbA6DXl3bbySaTF1jsGYNVx2gi0HaMTXqR5J5LYJQrGhAK3Qb4N5lqFwn2auBhGr1y3V9niBos4Eoat9Mww8Y66WwaQbRpAxz0rc5A4YS3Mmew/igMXSEe7h3ORpGOW'
        b'kxTrJwE9hcTXcm+ZY40GIW3h8QvQ5oq1px1IslZEOkCDvwmpHF3wkHX1KCdlpA0W1Ii070O7OvY5Q7lVOlapehhEXyZmlyNP5NFyXSkYRnceOumua7+OMGwQ7qmab5Yh'
        b'iN1X0rDFSYNdCmJHvL2VgJi9k7C+e70eCfhyGnPoPOZegJpjQGzpCHFE4kykIOB8MDZjy+GrxK3uQS/Jki4WuqUzEnqbB0DJzgQS000w6IW5Z7Hj/CEodjfzILDlQtGJ'
        b'OD0vJx+mwhRfuAk9YcZ4OxyyNa8bYh1Jq8pzOJ1EeFPrgwMhWGi+B+pEhGSt7lhwjFBridj6UPQFskoqiHUXbdQlEE+GYPVhLIDWxIME+gfWkH+EMKYLK62CSAnTitpv'
        b'6xUGXSE4m3ie2HLbYTWlnTYHtDbaGBNPn1TBIs2TnrtJHC7thGZ/GrhqHWHWo8tQfDqANRM/D227oEcrAscSaM4m2un9i0QI3eciNxD7qYIhCxhRJngWY100FBnA+IUr'
        b'F3WOQn88PTQEDVHEIBrEcbSwbF/C90kbuGsPi7tJ4M7hnVta+EgQj02mpD73iFL/g3AS+32JlggrcxI4pFwkpEzHgUh8kKFAek+u5nWCYc6uzaTgTurv0cBqddIkz5zO'
        b'dIaKWwY7r6dCfqiud7DKaRLhnewP5O4jzl9LjIRes2d60w31dTCYTmc7j60BR5VJXE7DkloIdmNDHInbXlnMTsV7fpGweD2BfmoKu0C6zDCnPgCpDw9hMZawfyJMF/OS'
        b'DLDbiBCjg2hnwC8BK28YEm9oZtpuDC2g8OKhy7rK9EYl8Y1agkaJRxBpev1ZvllnYtK3qXgiKayd2L2NOHfv+SPpqgTcEmCEWwGzCVeOaMC0WgqRSU4SqRQVgZ42ijtw'
        b'NMwTb0OtLz0yDXfksX9dJBb6sHao7LbRFWhUI0vlDrSk43gw4eqopYqpKwG0IVbdMS7jCNlOHZuJRkeI1ZToGckQLO/tIXWzQkcLahIMDU4RsQ5uxjkn4lplZJ5Mkjie'
        b'T2DZ+Vh1dSf2bCcDtx/vZEGjkTkxv1l5miwXe2ycIm3St56PIjLPIXLITSVKaFSCKissv2SDTe47iRgmNNcnhxHzW8D+s9h/geimayu7EneAdJYZGyjA2SsJ0JlCVngh'
        b'Wcs6e7SIWdYdJSY/cXg7LbsiBspIYZDFB/4kKgsJT6uPXMIp/42YJwM1OBJJ894nXGsUbE+zv3I2WdubzndsmwnTSaEyIgWaj6RD8XYskj2PJXHQYEfPjsMk6Zx1WBRA'
        b'UqKEtJJmLXdVaHXddcuL8HMQhzOD4qFCj12+8z1y6gCzzgZsoftYksl5mCGsuusBY9djtaKICTWoEYZPmmOnzw0nrHY0IaQY1tmGOZbucf5YricwltwdbYX2424usgKh'
        b'peA4CYBia6zl8lSsSbPtd2OBdu5+kSbWbIYyLhnq8CEjN1ORQOggCNxIGsYC3uW+Fl8+yMpQCI8KCF0KsWF9AjcObWKGZVyVCAVCV8FxWZIGtae4qRVFXAa8kKVU6ROW'
        b'thzCoVRnsUDgAKMkaO+TKCojomh0UCGYj9xUMjinCLWHT6uFarISxRaECh0EpXtMW9+Fd1wcPSA/7oi2MXGaGezemElyqR1aXNSPnSPmXQHNYSxfmNjrBLbuZy4XMrwr'
        b'0y1ST0C/NlPwsqA7MhQLlKE9KZQWUw1LRyD7jA/e86RzpN+JEPNO0ccu6BUQey3w1yDtrcmSjuu+9dkdhHU5mwliYyZBNO5dgRfNmRdJHHWEZG81nTPZN7E3IN+CpSz4'
        b'QcUu2vo4YcNZ0l0qdxF7G4IqWzKS8lKCPeCRG6F6F8mIEkKqcX0ymHLJKCu0Nb4BBTakuM0ThxglYdAGo1tJD34ADQcjD14T4135SDWsd74EfftxNsnUAOcu4sBZlw3Q'
        b'J38jNdIjKZi4ZyV0KTKnAdTrb8QcAuwAMaIc4ow958/SWKUEz9ogrTgi2DlaQsU+2mqP/SalMyrYEh7CWV2NYsy1Jhsmm6AyhMRDl+CuyBpKxTgaZOJFaBNIPK39MI7u'
        b'IrrptTEFVtK5DyoOkzp0l2WLJOmkypBoqkimbXTB4slzpEtWQ7EJtMjjYCxWOMO9o9jmTxZVKZkui/IbsCRka7jxCT0cVIB7IXAviehk0Vg1FfvCk5JYPWSsylpHKy7a'
        b'HxBIJuQQceJKGxw/4XRjfVQETBmtg2lVbHUmurp9AIcsXYi0+yAfmWenSI2s90nI2QTNwcQGoPao81nPc0lnzuoQLRSSHJ/TOYg1SZY2xCfGr4mB1WMcNNeGpdQYHDhA'
        b'hkCFiSY26jAuTvKuYM8tItKpfaQsFjF/lLFnFMlTmLGEphTCqQKYOQcFCSTCu6D/JNHukNstGAomg6+FTnXI9RDnflkQk4hpPRdNxlQ33D2go3fTlKhh0pPZEFgZBQ+x'
        b'Yw/9ZwkXDbWhNjLZLEWXlK2BIzh7cR3mrMMFIbRcvHVOAStSe0XsUvQcDf6EY4aY6PARQwe1azioLbcpDdsjiDhywogtj3mfw2JXLe1jZLQsQV0SwTJfWUv2bLD7aeI6'
        b'FTabCHVqYWQj9ljpum21g4nrZAsUBOp6mYcfkyeJNusTwLlnxr0MaJJGqN5PEFlQoh2MJxBD6iCBshiD06kwbQwjUGJnSqTRg80J9I+71/ZCI0k0Yu4VDFU7YcwEhvck'
        b'kqJPrGE84hxBOd8jQIepmUhcuvuMkLS9BSLqHH2inzEnEnAtMvrYa0p8dwI7NQPgwTZiquXQ5JDkTgp2SzSpnbkOjLeOQU5WPCn3eg6kJnRuVGN+LXfszdQ4oQT9ly8Q'
        b'Gy7lfQDJ4UQBFZd20rLY3dn2m8QJ5vSJEO6TiQu9HhcFcVhwPJ5YTvPF49EkFiawOZJWWJVCMjiX3iB1HO+HR8BIvPcBnNRRh0fbzxIm1Gth9zELBhET7NOJxLlYQhqm'
        b'4PezJt5JuHhR1k4dG/SssMrrCrG0Uk3s0CDbq/o66VHZsHSVFJ3Jo9C33svoqM0OkrxteC9IAdudEgnoTUa7U7cYx2p7O2msxzbNW6mH1kH+cZEnd1H4AeFmz01iBO3Y'
        b'YJ8a4Awl54jT3jaFWa1IIssFoovprDOXSVYmQLkYx+jfLCFyLvQa8dtm+xuB2B1kToypEQeM4eHxizBksNOF+EI1O2M6h0fE2hqIPwytp50s4tJNb3catGsfVF3e4ORF'
        b'08/rEUgenoDZY8SEC4Jltx1NuSXPq1qTzFUD932xZNmyPUOzl0HdXgNm3AadVhbClAYWesKInDkMnZPThj6yIbBnK0zuI1wYsQ3ARSi2iLUlLK3kvCb928yJlzEvXcN6'
        b'M8gj1kZomg+jZB3gozQvc2M6tAFcOHIM+vShQU1/Ex1BKUxGEMF2HrUTQN9GYi39O6HBFrO3Escbh8FAbPWHJusg4jwFLtAcEURyYSSAqSgd2B6UtFtWHGOHtZbYnY5F'
        b'FjC+3Q9zE/ZAV9xxkg1dtOle0lubHYnnwJw7FpsFkfRoMiGKvmO+9UwMdh/YcDYJH3kSytWS/Mjbq6UArXEJJBTriFF04KinPFHC0hUvMtsrCWtKoSuTNk0SaxP2WMK9'
        b'VJIpdZ5xhFNkudSZrUuAPCVDkq22sVjvqn0ZFqAvFZtsYf5YEtYR+O7iaMAWWPITHMQ76xRwSUyrzPfYAHOyzDPSaQs90drOJLT1NtmS1VVMW8Khw8TIFwgrRogSZggV'
        b'Fq+S7TmoSUBvCAtn1BMVY0SnWSY6fyz6qgpMncOeOC/P2KiLpKiOq9ISGknmDijhuBuUhENdgKkOkJFxG8viVEJx0A/uajqEXLiOLa4em62wcg+ObY45j+U2Iqa4Eh/K'
        b'IzO6FRfc02+wpt5h6iS/2vHRFpmdUKt5GvPDA50uHvdwJCovtcd7yQcjcG4b8aRhOtISMg3lgolBDCoH6XNMhjHuGgJkffheGMOpbcZEvfXYmUFEVw6jRmQBlayXJxHZ'
        b'fyVwA01aEoGL3lfpbMqQNIQKRZjWOGxBXK0lQ/OW2m6isAZiOY/MsDAYWg5chmkvaEo9QUoNVGzevAqzybSdFot08AFWOqglQZeWXNxuYrr3aS9jxBJrrYSufi7MfArH'
        b'2XCcWEeENUVbbzc7rIoV+mc3yxB+N5IALyUFfjCTgH1vr5+iPwzvx8ZAQu1G4tzzyswahwF9f4J2Ces6qY15vo5M99GkwYaCDaDbGodOmSApNK6bCUAl26DVwoDo854d'
        b'NG0gyDQlk9TpjYSxQH1C8kbR6b160LnRFrLDoMiSdF97YogG/sZ6xCeqYjBXEcYik26R4MqFyaD9JFQmIhkXL5FP8WbuQxvoUzlAUL6LDbrBBKc5DeyI3oDDCkaZx+yu'
        b'6sD9AzDifoPwqpukXxc2bMTpFFfs0yB15y4J0ocxJBAylU4k0TG20CBV2w6mQNdhGSscOroDHhxRwuYUHFSPuqALPevVr0L1Bix1i6aBcqDGTN7ag46UVA0CzayMoccV'
        b'hwOn43B4G7GGPqKi5pBtuORI/KsO7rscsxcQaRQTXZIKTtyrCqaVo7BgH0loQtKSEzC6SVFIvGAm+Dxxvm46llkaNW/9hjMka8ugUwHuxEC+LfaZkxQovHkNqg6eR+Yn'
        b'7xDAxMXDesRR5iE/djdRWq8uKwUzQprOAlmTedgcorhxHz7UgTq/g25XnEiIPoAHOCRDr9yGCUMtW7I6OqHnGPTL6hMxNcPSzg0bSZ8tM8GKG1jBQFOUBuPiK7sO07eV'
        b'dtCxm1QAkpZYu36H3Q5sOQj1kYGEO4VYm0TSaTH9HI7stfOH3PgUYow1FoL90BOarhUWRlCPj8GHUBYGo1dJg64kBa6MoDV2iPhq3g5bUvPnsCDpkFuUPfGBQiy+bk7A'
        b'HVcREvb1qzDtmA6yISI5PQtmveifndDoTgZ6K4xcccbhM5xsnMSHdueOQJ0RyU2yfp3scdKVFLgR5Qgr0uTqg4g6luTDSF3L3nZAnCokOroOD4IYHeUQOjNCWsSHpsSH'
        b'6wk7p21xUpeU3UCsVoo9AQM7sOmEJVSKSby1rWNP2KvHkrm4cD3a2ZnUgVxXf1tDzM9MJAV7EXuP0dmPQ6siLuyXjyehMyDEdl+c35kF2WT43dvlqKbsi7URXGRtiHn5'
        b'b12HGphnzqxOmDtNGyQy6WGuIhJi3dDjrI0NGad3n7Wkrd3DfjvMuYXlOKVPorHwPLT6k7I1ZS4Xk2itC6POSkT3g/RgmTVBNT+e8H9RDdsuQB5RzSjJlXIrrNCTpz12'
        b'K5rj8I0YUgDzw9LhDitPXw5tYhzXVcSmAF1HXUKWQSNZ9c04e9QfKlQdFIhlzmO2E6kzA4yh7cNhAUnve3h3j2qkN+SdczM6mBKnhIvqZzJ3E3cnnfzIZW+4ewWrrX3J'
        b'omZa6IRtzA3CjaLdMLr+kBvRb7sOu/c7HZgRb4IPdhLXmiGxnXcR59OVMP+UL9FEHpklD4jnVJLJspWAXbcF76soiaN0sORsXOyFYBtsdFMVntKm94agUg6q1usQrVXD'
        b'TJyKi6klTm9hXk+S2dmwsAlmWOCuV38zmXylYUftIX/XXmzZS9Boh+HN5glQ6b6daKKcbJ/kVGjYS6eQ74JTdsqkvz8kpaD5VKYOdqjclKU9VDlCo6biDSK3KvpXJSyZ'
        b'JoRkQMtWMilzNQ56wZQuNKsfsFdJw9uumKcfLI+9flAVAy0wQGhUfjqI+UqxN5X5u+jkHxLzHSURkYtdFlh4M3gryWhSgQLo2fuetJ3bZ3A604JUM+gmYqkmMV2oHBSW'
        b'epbIsRWYKCGNtGs/7W4pC2q2YFUkKd1TVwlfhtJ0Ca0GsrDgFhQRIye143Yg1F3D9tT3SVNyw+Hjy1TgwJxSd8+QBCbuFXfU8LTaDqwgCjiz4zr93LwxOlxRF7s2HoXb'
        b'B3fQCS/hcDQMyjuH0DTTpCB1i/bjtB4sYe+BOGXaUx62pQCLAOectYMqGajVJW6+kIYNbtAhpo89MB9J4ubBTWb6Ez3VkC1VqbQFO12JkQ4Q8Eux6gZZhQ/ttLBoPzw0'
        b'x44dHlgSz+JcLsxRFeFN4MnbRSylSEUG+yM3EepPZhgSlc9ZeSWy+yqa1rS2qj3aWLvdwBibdp0ifYHI4wQhxKJWDE6pYOPhrdi9juzGvPOQewLnHGBAMZ24SzUpP/eI'
        b'M3cKCOvn5eC+vjPUKZON0L1HDdqPWUGDDakKebp+G/DB9r1ycljocwKLlPH2CW8yix9akH5VYItjaldwylLFzRo6bLD62CEHAsoENMoQ4XcRq8/PDDFUZ1e55ogXzEGO'
        b'IaH7kJC0slvXrAjfqk9DnjKHFnPBxL2XLu0ijtCMBYkEtR7GCab2kOZRHRUDnQcJpZn7vRqLdXBiPxk2ldFQKAcdMYbwQAZGjhzCaWagY7YPMbBJ9zQS6I9s5Eiv7oRS'
        b'I8w1I8CMaENHFtStJ7ws3MYiybI35PZH+9HINXaqWEu6g1waU4ByNfclkL1H+vxtYhKV0KOJDSd10llmhS9BrhHmL17bCf3msOAIncay0LCVlKumQOi7RDbPEHSaB5P6'
        b'QzJ7/6HEvTDvuvsqduyEelfoMd1zCidkSaDUuWwlq/Y+jluReOtjNNLgq3HShtTrAQtc8t9BvK3udIhqcJbfpiBCnELM3udOc9RvtzdwyBKQcll4CftwPlXS2kAecoOT'
        b'cVotSRZzNvB1c2DGhisrk37MNhnnjz0u9vZos7GY+wWq1M65MafSQYGvDq2mBXv4CmBkKPq7scIRwj0CgsAskQtxar7mU6cLu0+FRTIC4Ql2l2SQzrVThr+vVW2LORIH'
        b'GakJVVisR4YP36KYJEM7dLh50SKsBdhhTNraWCo/Wx0pwQ+xxJ3esxWQBtKGd9Uxn/+tmpj93LJrreIW1rDyUDQmV9mn3F6d/kHveQkUiHF2+OM476l7KENyrsSDd7HN'
        b'Mt/uBs7x5o+FBhKHXPBlUj8LhMZC7gdLvC/r5kojmQpgNAMLNXdwYD2ECy7LDjl5Yh1Ml80xFjpy7X+4W2ya50QsITPmmkyIyuu79QXGYu7rXFvua91XxCEqF92U+dpB'
        b'ezfyX/5DEGI2rJol8DQWedJQ3J232N4fXRUlDxLD+mOefVb1GS+9Y1p50Wnvae/56atvOxi96qfn/unif2hVVXTYBR6ydq3YtvOPvjKWQV0Pm3r/LrgZ/0b5mV2/2Tq+'
        b'8P71N/4R9YbWV1u+DErReXcw/KXZsZvrkn71j7T62Ffe+clnsVOOr/3Hu753Nr93xmfqkfPxrY2nCy9/selvCYOfvlIs/LnVzY1n/nvgstFXv2zxd997MH8kIMiyxNFr'
        b'TsnD+Nf75n2DB08X/vCKMURPalU3n6/x+M6Pbxj8af6PAZv6muvMJzt+9/7n71x9JfNYwIPJzlzXCaPg0PsOVe6XfvDpyeJUvY/3/y5t6w/mZT99kPKa1T2VedvjOu/7'
        b'GjvrTKln/sjN/I9BGcb9GS7fU/lsT0v73ZTvtmtUf6n725sq7353zwctB2uj5w+/o/imXq1VbG3AuGxsXWxDZMupn9WcsDWeCVUPOh303RSVH15Je9c/qfbPr2WryMUf'
        b'K26ecDX/XuMn1XYmM+EKtlW2rTsuXTAdMf5g3RvxLtWvW3+0x/HtfRopP3tn5h8/rk/XCv/zq39+d13jx5W678m98W7XRwm/uOifvLv+71Z5npbv2TWpvGr1ss8u/TdL'
        b'fuuvd+jWyMnbf//iHaXf7F0c+llJkihDy1n73fpwq2Nd5eX/e9ciLUTDN6JXtH/TJzM7t/7GYPDXBnXfm//3c+O9X+wort91dOg/tlQd+Uol9433krRs6n/9254/Hvvy'
        b't6WvPXj9zaAem4KM9wsOJoZ5frjQoBwY8d5GP7fAXXUvO72lOf6y/cWXTf4RMbr/T62sI95HP//DX8b1v7vprYboCx8pyr/3w/qBpWsF/R9V7PgsXePjRi83R9WDrpv0'
        b'3v6VUdP/GqUpnXv7VdVrYwVZ+nYnrxRu1/+lTO/BNz/7Ijdo/Oqj3iO/e3/j7AeJf39j8O0Zua8+/uGb/V9euzTc9/+au9bgJq4rvC/LkmXZwuFhHIMxkIAsv8ABAgZi'
        b'KBBkWeIVl1fDIstre2NZkrUr2zhgMGATP2SbUCYMEF4GJ8HgOOBgnk65N9NmJj+YTmmT7I9kSKfpY/iTIc0U0pbec1cCprQ/2umMOxp9Wt29e3Xv7t2959jn+85L3wzn'
        b'b7l9P+/4XxzXz94jH/OvD9z7auG3v78/50TuwR1/m3Dr1+6W2QFbAo17r7MRD6CjhD5KiNHdgrsWoyuUEvXKGtQcC3LNRPueSJFH3KCLlFm1ZsF6c6Ht3+RfKJxOZTzy'
        b'idd5xByymCxkde9IDoVBkmSYZ/KmpjcKxowttKF5RQ3mhgWxSvX4Un2txcCkFvFAZUa9VMfjxRC+odQlvlReG8bDyagddSYbLQl4MLkujrElCeRx1lVKo2/xqU1ogNR8'
        b'qh6KRFvG7WsZl2BAV9LxWT0UuCOw2Vyx8lF7RvwOl4eOjacJ5uKBTqegiLGW9E4hy1vbUw2ivUHGhT80oBHeqYKaHWorLngsPPek/Mo0dCWqwHKo9OlMcQWjG1w66mBL'
        b'p4/U/xfQU3qLoi/gKRdFGnZ9mwBn57gX2CmgD/LQwCWyRk7gjayBN3AGLolPiUtJsZqsk63xKYaxCcIzY7lUBzf1BZbZyRVw7Is0R5DAQwjuZCizp7LLnoMyTlwYzR/E'
        b'eRfQLW59rCTVkLbRuoS0zXPWbDhq2rJY3WlcFmcjbztnY5qFflpm4LJpCXmRsjMQWW24HwsBN1qNbCr75Ft4KNwPbX0U4cyH/giDfxzxPXv0J8aoTUhWPxk04hpOkR0m'
        b'AZgqwc/+Reorynk9m7YMdbhVYg93Q5oy1Ia645mkifyk3C3yxI51vDKOJWbH17+aE3G4cZF1ef+iW7W+GbUpRmPmLJO1N7XrJvfB8Cd9hXbnmDF3e5r+NP5On5rWu+m6'
        b'2Pjna8/+sud03oPTkarzGTe/XfDl55EzF59794tN+9b96K0fWidPOHzpu4O3RhI+X5f51je/2b+//YtSU+Gr8373Sf5vPx78BY+P2l3rvy+9ebr47z98euBgWrDqwvv3'
        b'evgl/Y3j/rCoZ1rpRet3xR23T9b9ddaEoUn3js0NDFk/PR+J1BQ6H674qmWwK3Sq7+gR9/T627mVr+78+SJra+qSE60ts3wl+S38hIK7nozJ29On/Cxzafqd1BlvBNsL'
        b'Pl4Z7DL/5OsEm7/nzvj6yy8nz3/QUNSc0t2ACrISv3z/yGXHCH/ps+/NLffEOa9vvrq135ahs3H7cPtqMFVXraLaESnoRjxjRhc44miMWPQqEAC327kqhyxGpNqqHK7Q'
        b'x4zB13l0sgjdoIuKi9RuJv4ncYC7dZEt+MsOuRIp/GTUXUy5zWhgEeoBmVRXkTueMQickZjslyiVe2dTI+6w8nnEFF1HjGe8C5+j5A80uAQP2hUOd80EpnAny5hyOeI8'
        b'jOBeyv/dQLy6PfqCGEcs4j2M4GbRILqGztHdyzNynXPRGUe2I0evwyThdt6Ne9Noh+aiK1sprdyIjkfV1E7iI5TpPGPTJL1ZlwNHbA6hEbczKfgAj64W4UO6+tgBfBXt'
        b'dUolxdnuOQUsWbne5AzeDEpEqyEu2Gnn7AJyLBXrIq7PUiY5ky9sQsfpuDzGtbDb4dL3DqE9pGcD/Cx8oEpv/CgayMcdkAqvmxc3MMIaFl0rnKjT7Q+g9yYA0c+VDdsf'
        b'McIsFp1zqTqj/dQMNGzPwZESdjo+ygg1LLpcu4BeIhWfQYftIFdXAr/qIgMXpqJ9zLM7BLRbXU37VYffXOuEXpGR404OnWMZs43DPWPxT/Xr0V+fqTzavwG9yzIJDg4N'
        b'GvF5aje8Rpw6M74wEQ8l4w8V1IaHg3iolpgiFoZJnyYQ34DMF2ioAV1eSrlHdmgtayZDptxhDhO3M6Iz9Vrx24nRrLGof1JMc66jWM2CUXait71ODNE352eSawsaYlRd'
        b'cZUDRfLcOTYD8/Ly+O2L8Rmdy38Mf4TPm/EgHmKJzXONYfF+hrg+3dt03vxe3E88pouU845HgHYYt50lfvkFdJaeuY2vkEMvUnJRXlaUU7RlLZMWFlArap1OB9SIOvFx'
        b'u4LeyYF/aOC2Eo4xPc+hDtxSrVs9fT7cay/OyXbl5Lr9LJM4jk8gjvN1XbHsg42bneTSOHPJoeT+sRlScB/zTAGPj/14g97HE/hctX1ldhaQOzvJHXINJAl6ODywrZLe'
        b'QU1Uc60JHwb3zMngQxZHLE3RzNF/sv+P1ofxo2CSPM4QXEfAmJQQ5V6CUpo1uqVrmiVSHbTo1kNhF+ilcQ8hH7CR9fP/OX0s9hLydSIVtReyNN4n+UMKWdW0ODUc9Ema'
        b'4JMVVRPKZS/BQFDya7yihrS4sm2qpGhCWSDg03jZr2pxFcS2Ih8hj79S0uJkfzCsary3KqTxgVC5ZqiQfapEvtR4ghrfKAe1OI/ilWWNr5IaSBXSfIKsyH5F9fi9kmYI'
        b'hst8sldLXK7TGF2eanJwYjAkqapcsU1sqPFpxpKAt3qFTDppKiuYK/lBdEqzyEpAVOUaiTRUE9SEFauXrdAsQU9IkUSyCyjd2piaQPn8eXr2DrFcrpRVLd7j9UpBVdEs'
        b'dGCiGiCmor9S4ze4SjSzUiVXqKIUCgVCmiXs91Z5ZL9ULkoNXs0kiopETpUoakn+gBgoqwgrXpppSTPFvpDhhP2gOvXYEtPP98xQPdhq2wG2ATQD7AXYSTltAI0AVQCV'
        b'ALsAaig5FiAA8BoAkAlDPgAZIAzwOoAHANiroSBAE0ALQCuACgD84ZAfYAdAA0AdQDXAbipgB1BGfwiodXtgax9A7SPKIEwkU8yq2nT/aauK1nhgrCDzRfJW5WpWUYxu'
        b'Rw3zB2nR71OCHm81CI8BmRX2SeVum5ES/7R4UfT4fKKoT1xKDTTBjDXo6VJDd6GkLWYE/1PGZc24kFz9sE9aDAnfFMi7KzCCwcj997fQ2FKOkqb/AZAS4rk='
    ))))
