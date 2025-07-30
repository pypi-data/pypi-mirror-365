
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
        b'eJzMvQlAk0f6Pz5vLm4IJNxXEBACJJwqAh6IBzei4K0QSJAogiZExaseKEFRA6IExYrWAxUVb6vVdme63V7bJW5as+y6tbvd7bH73aVbd9vt9rv9z8ybIJet7be7vz/G'
        b'yWRm3plnjmfm8zzzzLy/B4P+uNbvz3dhpw0owSKwHCxilEw9WMRRcTt5YJQ/Jec0A8B5xvZb46zkcoCKfxr7zw+kWgu0zos5OFyg5A1Nv53BoXaqYbkwQMmfCxyWSwVf'
        b'rXCcO2N2umRVjVJXpZLUVEhqK1WS2XW1lTXVkpnq6lpVeaVktaJ8pWK5Su7oWFSp1trSKlUV6mqVVlKhqy6vVddUayWKaqWkvEqh1eLQ2hrJuhrNSsk6dW2lhBQhdyyP'
        b'GFSxSPzfibSGEFPVABqYBk4Dt4HXwG8QNNg12Dc4NDg2ODU4N7g0uDa4NQgb3Bs8GkQN4gbPBq8G7wafBt8Gvwb/hoCGwIaghuAGSUNIw5iG0IawhvCGsQ0RbUDvrQ/Q'
        b'++pD9GH6YL2H3k9vr7fTS/Quep7eTe+oF+md9Q56T72/Hui5eqE+SB+uH6sX6/l6V32g3kfvpXfSj9EL9Bw9ow/VR+jdKyJxP9lvjuSAxrChbb9Z6gA4YFPk0FAcIh0a'
        b'woAtkVukc0HoU+PWgfXchWAd41Ah5eSXDx4FCfi/iDSWwDp05gKpa36VPf7177UcwAMf89xAaUxnehHQkYaFh+BVuBftQY0FuYVIj/YWoBZ4Sor2ZhXPlglAxAweehk+'
        b'D7dKubpAnBw1oXvwZk5WTJYMNaKmPD6Ax7WuaDc3H+1I1fmQFMcV8BJJwAc8HtyODjHwGGxFRl0AiTSAvGjyoMItLy8L7ZVm8YAHOsCFtxeWSzm6YJKkBTXDozkJieg6'
        b'2oeT5KB9BTgvtxBuKqxHnTQbeCEP3sBJ4K1xWVl5bAJXdJEbz0FGnA0hdB6qR01aEompRE0MOj4GOGZxYA/ahXp0Y3CKxNJoJ3TFDV3XwkZ0czW6tgYegCfgHjcXAAJC'
        b'eXYCeynD1ugcbJuD9uRmoyYu4KJ7m1EXA4/IF+FoMkyTYZtXDrwQiVtkdw5qgo0FmCBPeCUL7o3Nl0kFYNYMu02qMmtmCngeXUBXMVG5BXzA37QedjDoZNA0azQ8l+oS'
        b'nS2LyZPJGXQL3QTOnlxHMbqDo2nzX4E7JdGZMVGoMZdU6uwm4IQMHHQRbYUvlTODxkGibRz0YedgQgMeC3j48vCwFeDhbY+HNMCD2wkPbhc8kN3wwHbHg1+EB7YnHtLe'
        b'eGD7Ylbwx6wRiId8MGaIEDzMQzGTkOEfoY/US/VR+mh9jF6ml+tj9XH6eH2CPlGfVJFIhz+eTBqdhg1/Dh3+zIjhzxkxxJktHOvwHzXu6cM/YJThP5sd/iVFgplvMLiR'
        b'JaXOeQnLAQ3sUHGrwgDxlcZ8/ZwfG7hujoNGCSQ4rDT33cQwNnAXn79WxBUCMLU0d56nPzgLqhxxcHSkD++xB5jaL6pjfr3gn0sOengzVQ44Yv/CdqbHDkjifPM1KOEX'
        b'ZX2ABr+15G9urW5MZD94jv8nn8s8e9AHdLE4oggPnaOYD/fEFkZGot2xmTLUhvaj3fBsUWR2HtofI8+SZecxoNrNYZIW3tZNJ6PlRB3s1tZq1q7RadFN1IOuoSvoBrqM'
        b'Dq/B3HPVzd7Z0dXBxQnuh3rYlBCXlDA+flwivAl7eADeW+yALoyB53VZOKNwPAWcysnNzs+CZ6fm5eBy9ZjTd2PmaUR4coiNjImSS2XR8BLsgt1zcA5XMHHN6CAyoEPo'
        b'AGqdD4B3nIvHqpAhY5AsU96kMzaRMcghUzcehQweefwKLh0leCFq5A0bJVyHUfodh3BHjATOFq51lIwaNzBKKoePEt4oo4SXryHdrH4lz46rLcS+ZZ9NP/Jm2tGQnWsY'
        b'7vjeN241NW9TjAttKtkzV+WCODOrfvfW1vXjtjeU9XHGwpQVvint3nHlOv+5LugvjQmdDuc/OK28bCjTxHGXp4BjNR61tQVS/mNfnK9XEerC/bwbN3JTAZ8LeBMZeBnt'
        b'RNsfkwmgJhmejZbj5m+MYdA9NyCA+zgytC3vsReORHeyYVu0LDJTxon3xlGHcdThEjaqJbYyWob25sbzndFFIFjEoAsT1I89cZQznhxwiZnwghbdxk25mZmZ6iLl9XEi'
        b'pRo8nsETR0saRrJ169avPNMqNDUbVNWSCnZhl2tVqxWT+7g6tXIDcTgk9VLsfLkV9M/kALFX24SWCcak5kmtk/TTLSJP9uexlMMp7WkdaSZRpFkU+UAkvy+Sm0RxZlEc'
        b'SeTdltKSYlR3iU0iuZl8Eh6Iku+Lkk2iFLMopdc55XPSWRo77EgFfQ7VilUqLQYYqj6eQrNc22dXUqLRVZeU9DmVlJRXqRTVutU45EllSOeWlkpwfTTuJNADO5R4wjra'
        b'NYT4Lwn5MzgME9gPvs155OqtVzeubFq51amfw2fEFicP/YTGiU0TH/HctuZsy6vP25pnsXez2Iv0Tl/243ldODR0awH773MyxA45xIBu1xTuzHLOaGNyC2EWrpVZeJRd'
        b'BBW8AXbh/8fZZflwdnEchV088nVk2MGmSei0NpePB+BZeBp2AHgGtfN0JLXqucocHMFIYWsoQA3wAmrVickjV+bFo6t48WP48KAQwOvQYEcfEAWQYUoiZkxQAjy5tAh1'
        b'pM/WoztCJ4w0GHd0eCaAd/yzaXIniJFCNAkvDIInATritJImRy9mLYmWCwCzOMIVoDPwTo6OcAHqRB2wCR0grL0BL9kgTwrP0JgSdBgvygcEALbAYyAGxKCjqFnqQDOL'
        b'mihP5QDUuh6gnfiD9qbRstFOP3RlIwdI3AE6hT/weipbSH0hugbvCIAPvApQG/6MQ2fZWp9BN2YiHJMTA/Cyjm7K4U2aFdwqRkfgHS4Q+gF0FH/Wz6dZeUXi1sDBaGsU'
        b'QHfxB2fcRGPgTowMDsE7bkDIw9XCH3g6ny3kOryJjqEXOGAj7MaY2ckOnWEjjuM6bp3LBZNgD4gAEcgAL7EVuYgObkYH7EAtegnEgTjYJGYxTwdeR67hqb0Ncx/cL4YX'
        b'QAlsR8dop8+F52LQVS26upYB5ckcDIfCQtEFOn2OmP/puAkiQxoP5+VgE1iKscEmppGzFlwSbGKaOU0ORLygTM5yOrePI4/rY8pZJiaiEGZhysFfOaZVqbW15TWrVk/e'
        b'EKyqLq9RqkrIxCRPq6opV1RpJ8ufJFhAng5iZ6hen4nsx7imy71rRVdwV7DRnbhdwRpCoPrf0Zd42m7sm/CzgCNvJhw9fuC68eyBccaQnfE7pTsn7gzfOW6nbOeknaE7'
        b'E3eudF0um70Frwk9zvr5qG5p99GYGa/dMp9eHVvOO1cxvSv/g0+UsvLIFs6npa+e22HX1eCAP0sXFP5CcNZvFz/X8rjz9us7Q+alCLouHrp8yKFNNq5pXO7HNx6/XntF'
        b'Vvrap2N/mz/PecJnstKfnL6xY+Le+J0v73zhwLv8ny/9OCR9yZeCxNUVuF6RsX+oCMTrCe2qUwuU0XIp2h0D8JLQvQ6e4iSiW/DSYwoYz2XAS2gHPIVBJdJn5ebzMd9c'
        b'5uARvg22swtHW2AR2hODkTaG+4JlAQs5oRgVPA6hLAPP+VNIgnZjDI0aYXc2H8wTiJK4GKWfRBdo+fAM3M+3LWhcUCegC1pmuNRu2OoymqO1o/1L1hy2j/ucBvXrhsE/'
        b'6JLztXXJmY2XHE88Nbv4Wrx9DPaWwJAucU/RK+InnoDgfj7HO6QfYEc/q18A3D3a7Frsmh1aHfTpFjfffsB1kVnEnm2zWmYZM5pzW3MNjMXLz6gwqA1qi4/vMYfDDp1h'
        b'XVyTT4zZJ8aQ3s8F3v5sLM4sKPzY0sNL20s6SggRUuo0Oxh4hnKSZVZLllHZmWESR5rFkQYGZyz0fyAMvy8M76zoUpiEcWZhHCZCSCkaGJz405mOHZPPRDN2hSlmYQpO'
        b'JRKTtbR5YuvEXucAOlxZPrHrY7R9jtU1JVosR1eqtBrSmxrvp7QxuxBaV8IwMgcObluCAbVrgW1FLMAroj9Z+L7D+VGXxTYHGbjgmsp9hlWRgEj+kFXxPw8iR4gao4FI'
        b'B1bUSJR7gLCpzrgipZuuTZ7CChB/dswEhqr9DO6KqIlbVoKZNPSn64VAUvRLDlhd6tzolcUm7axwBOL1b+M1oTQ3LNQfsGtLUxC6mBiHp/zmDQAeAGUYJB5Vv3rMArS1'
        b'OLqu+xCZubY1Hj/w4oE1vqFctEKya6v4taq4pW/vLz4kPcKf7h1/Ks4usTZBXvqK4BDz2YrkS3suHzibGdB1yP1IX/7YIv/dx8ee6TkZdy0ha4w5/nTcnU9P9ozZU8Ss'
        b'kb3uFjPOufKi8q0Kjuknzh2+4OBYvz1/ipVyHpPxtgXenc+iUopJHaBRhrHAjsf+OE7shxGrPCvGXxAllWMpBjUC4CPhLUO3kqT8p08LfMACUeuk4F5eqSpfWVKuUSnV'
        b'tTWaEoxCRwbRCaLROkHUcoBQpNcaEhvXN603huzepN9k1Bq1nYnt6zvWd405vNm42eIdYNBZPDzbpC3S5ujWaH2Gxc2LcHKgUXtsy+EtXctNwePNweNpEJtYKDKkG6YZ'
        b'prXaGUONZcY1xrKOCJMwhHBpWK8orLPQJIowiyK6ku6LYnudY4dwK7dcreyzK6/RVddq6r4Hs8YQZh1Z28VDWVaLWdaPMOV3OD8Wy2qI6mP01X6DlVWpxuGJrMeMwqb/'
        b'BY0AfxQ2nc6yabBKBMhUGLfl9SXCKSusHPnlCnci+yfHjX1uwteKMaDICpS84TYROk30KvEgHvNePZuHnEfUB5K4eVOrfrlhHmATt8IuPrzplcgjCrkEtBPupoldF3Jo'
        b'M8WNzY6fHJYIdKTHobF2Rhm8nsghSpvERRtpSvMEF4AX18i4sX/hXtuSBigYlcBtaF8hOpSIq5IEktDFhToyQuCOWStC0IlE3BnjwDgndIjm8MkKT6I5lcRN5rh+FOsE'
        b'aFLUPjZ1FTqaiBtlPBi/DHbSpD+vCATJpLDJxknm+VK2MHi7Lhq+sDIRA7AJYAIW92+wU5tPCJhKWsc1bK1c7Mxm61yJ9E5LE/HQTQbJ8DZsokk/WBoOMgkFhQ/jPsrJ'
        b'ZGu7UFGjccPgGICJYCK6GkxTvrYqEszGzRJXWBX+oautEbfHY9jaiiWHq7jNUkDKWH+aWFcXAxYQagvXL3lbqQMU4GI8cmMiPACvExF2GpiGRewTLPI9GA7PoW1olxa3'
        b'bwbIgK2wkdKcNQYeQA0JREqcDqbDThbvw5M49RVYv1GLW3MGmFExiW3ibnSmKiGETEszwcxQeILWBV0IrHYuJRB1FpilRrdYss/CPRiDd8HbhJUzQWb5EhquK4JEWXIW'
        b'kbpngSx4YhXNOsd1GtyBAT2pZDbIXpXE0nE0a+ZcXPmrmOockIOe19HgDGcOukASY6pzQS58Poc2yYd5AuAMgDBubeZU6axUtv3gQbgtJlyIruKa5IE82GQdhHPFeHEB'
        b'wD5uXl71p54ctrc3zmJIenQV1zAf5MNjkTTt125jcTk4Y0VA/HiPpWzG4Rr0AryNTqCruOYFoMATddPEeepoUEQyLnxn7PaQcLa/l1ctTPJEV3FTzAaz0YHVNOWpcF8s'
        b'bOD+lp/bVByktQ64ZthqD3fB80TXXwgKAxbTtE5BDkBI0o4t5mfWprC51sEba9dPccJNNgfMQeeyaMqLPFei//OJW5sdmhUvAjo3HDgJtdaFTHTCzTgXzJ0xmzZ5JDq9'
        b'MBXdcMKNWASKpKiBPg6n+GOuwuRX30/fFJZtHYTH0HlndBq2OeFWLAbF09BL7IitCgZppKygL8N+nzaPZYMFsGUJurnYCbfhPDAPnnSgSSMyxgCicYhjgmK/iljIVkC8'
        b'dnlauhNuv/lgPh4XPSzTL/DC4idu7aCvlZXqWrZZZsOdbqin2Am34AJcwh54j6Z11sSCJYQAhXP5u0opS8AijOKXIT3cQxgNLHSfzGouc8aBSsKHvr2zg8IzWYhRlZqA'
        b'50JMVV2/d4zGGrhgRTwoJcyd/slUF6U9kHLYkfQ8PAr3outb4B7c4ovAooxSdjbZM6VctxruwY27GCyehrZVffnNN9+4VVlnxJnua/vlIjbnf9ZMAFWkar7Lxtxx9wBq'
        b'5/xirrYQN+qHzbN2tmQVwNnCny3/7Uqnrq5bL9zafiv20b3y303on37i5jc/Na6f6uGsrtnQ9dnMJm+3JY9gW+1Xs/e89mrbSyXwq89TPv/TtcTN79acfH3/l/kHGhdd'
        b'+bXTpvM7VmalL23569bOY0V/i87VfbVynOrmvYIvHOc9eu+f3/xm+Ue7StHZ+DF6x/KPPdZmOG0Uev/jRIFlf/1qsAOGODvNiosKSKy+f+v3rx2Nq37z1oHXjjouOZu4'
        b'6s++5b/w2+iqVgg+hzFe9XsWeMjLZ9zaPe6DlPH1R0oVrnUfeN3YmWrx/IuiZP3WjA/c9638TWnHI/Hyv577SVDIp2ua3lz75f+ePrPznef/3fEKf+lHF8XNZ9L+J+rk'
        b'+X25oX+4UvPg7yX/W/v3Sw7P280cJy941Nb91kVl/fXJf/1oafVHdYdq7szzabsZXX/mnec+kDef1iR1Hzne8tOik5J5x+2WnnS00+6ftAXcrV1+1/s9LBZKSKddgy+h'
        b'K1iyyyd7BftjGOCEtqML8DzZLbgCr1PkhvRz4UkM3eCxxTb0JouCt6joGF4G7+WgvdFob54sm2zneOCJ5/RKLmpAd+KoJnMlnkFfwJJfU042PJ8FL2D5M5nji/aEsgQc'
        b'xpF3tfBCZr4skuz5oP1c4I4MqCWHC3sKU6X2zyAfspiIjCCJRPIEFPW5WvGQrryECDEbhv2mULCLw0LBTO5gKBi/e7OehX6PRF4GjZExaFontE1pmWIShZlFYQTsBVi8'
        b'/Q21Q5Ahxkq+rgT+FfZzic/H32j1SUI7rb7I6C6rLy6xx+pLTr01h/WlT3+ljPVl572uYX1z5/UuWMR6l5T0Ksqp9xEthU98tBTqo6VQHy2F+mgp1EdLoT5aCvH1A/KT'
        b'FkUj2KKoly2KJsJSsRgXZsf6fQOMA/6QsM45Nn+UrKvM5k8c36Ox+dOmvMLY/NOZWczrA79ymQKmd/ZAZkXMfIYUb/25lCllCAn0pz0hYU6/A+v3CzSW2fyhYzs1Nn9M'
        b'bA+H9QM2ICXtlTGDAoijz+p3Bp5e+hn9HGeXwIfBkV2irrldZV1zu31MwQnm4IR+IHCPp07zLIzjay3ePsb4Zh1+2DP+kU9gp/+DkIT7IQk9SaaQZHNI8q0EU8gkk88k'
        b'I9/IJ60T1OnblXQy2OQTR0IsASGd09qzDQ4WUZCxziySds3t8eief1+U1CtKsvhLjOP6uUA87ss/iAKoAPHEoYPPoOvnYj8G749E3oYkLZ1nJ6RLpvuBV/0cp0dyX41g'
        b'sGtTfnPxyH66zEA13YNEhvHYGc4SZLLXrib4luq8uQzjTgSCpzs/qnB/0CEanHedyP1OiYHsUIJBEgP3vy8xjCbY27ESw2/dnSfP4GDoMrs0Zl50tFVi8FQ5Cu4SsC0s'
        b'jVk2sZpFDs4zkR5L6/AE3AuouK5j1E6zt3O1RHC7kt1M9paOH6h7okd8O9f5aNPRt9/y2XaiKc5EBfdXW6HYOYkoII8fzPK46BQJDbApZg7/1evOU68aV/j0vl32BiuR'
        b'y0DSN+6BNcaAvVKGzuxwWyy8zArlqCfMuld06zkpb9QJ1rbvw06ufuzI0dZqdOW1OixylmhUFSqNqrpcteFb4uikuxCwk+40HhD7kP2d5rTWNP10i5sHnoGTGuua6gbN'
        b'wBYhnn0McwxzWu2NSZ2cTvdOTkeySRj6DPK0oI+nxSU/O0+kEZ74Fuq3D+GPdB7DeBA2eLrzo0nSWPT6bkmaN0yS/s/zRf1wvuCOwhcC68bDTXgnx0mDU6BugNrWwPYp'
        b'zpQ1zhUmgZPl98muuWaZah6Yqf7o06+Blugbf3NQwfLAmic80DRV12Qxn4qTc3df2vWW52cTNybG1yboTjSejlNd3apqn2Pc4bs1yqe3mJe4+jQXiP7kltD9UynnsR+h'
        b'4TC8iMXURnRxkC5KBhtRw2OyDcBHrXFEEUXUUBexYPlEFQUPwS4pd/j4IbUd4AifYeqXJ/zw1BjKDXlWbpg9jBtE3gRxdCax+6J0VejK6Mro4Z3N6s66xTmX35XPMohI'
        b'1iuSdSlNokSzKLHXOXEoB5R/Lw6YRjjgqfQ2Dhn/Bf/t8f8sSl++nvn/o9LXLr+IjvXnC9yw/Pmlo31cae6/8mpYwef0ZCIN3VIJppZWPb85nQ2878DFOWV6MKC0apV7'
        b'GVB3CF8FWjWO+cc7x6kW9wDR4549EL+HERyKT4jrrqj/bIVviu9Knzd99hSl+Hq/0v3FjOafJEiWuXx0Kk6145Mxz+f/UfzHKLlgl7xCsocf9abxZ++/YX+tOXyn77vP'
        b'R0n+UvbnNX9VOlc8qmLARyvFpmU7MdOwtk3oGqyH53PzYjiAlwNvwysMvOIgoiyzBm7fhAUItC+2IA/tzc+C3TyAXi7znsMbPw8e+R7qW5dq1fraEqVOVaJU1Ko2DP1J'
        b'GWWVlVGW8AQu0Rb/mF7/mK6i7oUm/wlm/wkGe8wwxvW9ogj86Zp+qeBcgSlmkjlm0ivM/Zj03ph0i0TalX7cxZBl8ZZ0xrdsNmy2+GCY5W9UG9VdTHtVR5XJO8rA63fB'
        b'mfe7YlbU5wxRzfIIHX0OVSqFEpNU9322UjIJUw2t0H4wRDO7mPed5gU/qo0Bq5m1mZCSP4Ft0NYTfuKxJpSYozh6Ad1KsdPbVwgoV3FHMTDgOYzCJziEN4JzuFt4Vq4a'
        b'Ne7pXOUwClfxWcRl75GIf0fi5a3Uo2eFB8s/n27kY6bqHMefWpqbpJ0K1FunrWG0ROuxambTkTfH40Vl1cCict15nLOTT+Psn1neWKRcAHcb/qrMUyx5jVeEeKJG5sqK'
        b'9hXtqRNXGM9t/Vq+z29XTIWxykU7fsE69xKXUFFGxHzHXyZ03j3/wdr521ZJP5huAUU/XYgsb2xb4bSgNXLCjqpPlD+7xi+e9jrv3ceLDvkdKhW8kwS2TR5TO+V9LIdT'
        b'C4ku2DCfbqLagTX+HHiCKZ4AG6lhjjZsk81QMhftZOAxdA0do7smYytRaw5qjMHP7S1gANoqsEdNHFhfhQ5RyRvtQ7vgPhyrj8ULHS+PgUcY+LID6qRFbkZNcDfakwe7'
        b'AUhegR9jZsEdgVKnZ5W3hw96opCzid8DPO28XDWIpYf8YqVvK0ev5gGRf1tMS0yzvFWuz7CIvNqSW5KbU1pT9NMfuXn2A55L7EPvQGNFZ5nJW2r2ljbzDIwh3hIQjjk3'
        b'j4hXXq3JxjUtkwyTLP7BndJOwuoxJ2NM/nLD9D94+z0SBhpcjMrOLJNQbhbK2Z/lxyoPV7av6FjRNbFrYk/R2SndU0xBKSZhqlmY+pkD38f1McCOPhMLjOIAfcGgycCB'
        b'TAZ4BsgmdRSU62prKp6+xLLN40DnhNJBm9iaOWRWGNIm7STlNnZSIM1Sg2eFcML3z+z8qPLYYYc40OM6eag8NrBVQtdd/oA8RixGQQX//yX29BplhghmZ4ibEW8BkB1D'
        b'NkvVf1TGsDNE/HgJaJ2L23t1acApeR4beGu1A+hZEk7tOj8O8mYD7613AqXxMiK85W73WcEGlnmLQKsLQW+lm26PS2ID/y0JACeZNUT421RXHM8GzhAmAV71AwJwPfav'
        b'8GIDb8rswOPiYGJqGpOxwbro3/OQgvWcM6R0jlA9lg2cFzIZFK37BoC4Uk2PayQb+AvnSaBq/d9IQR7yaXw2sHxaKrC4/w+hc45rmRMb+NlsH2DvoyR5ps3k1rKBW7xl'
        b'4FH8TfI4Z8pGazWlCe4gLHAqaZDcz1Ks1axbNxXos3kMDpzzR0+BdfNZxge3IrxIjWL+pVpvrZGjC1gfn0jyzLX3s9rJlmb4AfvcVYSktAiRIxv4TvZ4cGvtr0ndNUaZ'
        b'NdCttBCEec0kBWV311Swge3LVSBzs4HBBY2tXa9iAwNLl4OO8UcY/LjgtDqYDfyN2gt8mF1C8tykjpGwgbwEV/AqP400XW5sehob+G7lRpAZ/TGDSVpbvmIeG5jqmwCM'
        b'QW8Sij0OJERYjXwXjgGb5GTNKJ3WU6oE6mx5M1e7BPODh8f2g3NTq1Gc86nwt56LKPwqp++diTNqmqOFldtAYEJt3Mfcro2mcZY35x6KmVSWNcPBb/7MQt/tXV+8Pmt3'
        b'/ZS3IyJXz13+hcMr275Yc3fx8ocfutzYeST5TtpPegTL4z8RT3Xrmi2qFQDdzwJOb9/4Fi/t85u/+b3nz8IWTC+vn9u9ZK3vYr+c+7/LaPzibNrhObuvr//8V/VXJ884'
        b'8Np7v/7jgvSa1dPOLlB+PSljS+jy5AeZb64smPHrj36xJtv3D2XfTHV6zfHS7DmNV/OilloW/WVh9Irtje8v037x+GzO5r/3Cdzy/mBwcn6uzdkhEf1O4/FvXfEjwdyW'
        b'29v7NnV59Ue/Pav/T5X/OPK+L0eb+uZv9s67PjXw59VrfH++Zco55ewZB72S9/zufyqnBM3s3/bO5y9d+sWi/Tt8x5v/LLnxj5fcPvL/dO/+X13s8j3y/nPX780r+muL'
        b'ccq4tk8des58tXjh1x/GPuexd4PLH96acPDXB0Jl16VcqluGR0NkQ5Hlgk08QIAlOltG9Reu8Aq8mxMTmYn25jDAHp5P43Hq1AUsaN0HD0yPxg9HMYCng3fgXQaLfVfn'
        b'ST1+4Ar3LIsg3YAd/DdoLXQnM32ZonplSWVNlZqsHxtGBtFV8VdWnfRqPhB7GxINtcSuRz+9XwCEYsPmXrcw/LF4h3UWmb2jeoVRREHraeQ2O1FrIYPCGNKsMiqa1Z3p'
        b'Js9wkzC8y72r8Kxnj8dZv1scUyRe4IjBkNDdUGh0by42FjYv7Iw3icNMwjASLDZomontk7vIoGj2wln5GTWs8QJ+Yk6znTG+k9M+obOwa8zx+Sb/mB73nrLL3ia/iSbh'
        b'xCFP6adZ3D0MSmNRZ2H7QpPX2C53k1dUl8LkGWtyj2Ujy4wJzcs73ZuXmtzH4BAPUnQE9ri5G6btXqdfZ/ENNIrxop3eqemadnydyTfW7BtrEBgEj55EmHyjzL5RBgHR'
        b'EHsaeIYiY7xRYRJKzEKJRehl9DX6dsa3B3QE4GbAv0cGiYc/wwYkkEqPMQvHjAggje1NM0loD+wINAnH2jJ9+m9bFmtwQ5qFIbS/Rqd1+DPxxjL2mW8hbESu30J8oh8F'
        b'NMkjkuK+8xDZAFhn+n2P8F6PcIvY0+hgdOgMaXfucMZDxMD0c4FIPDzZI2fx/oLdBcZ0k3OQ2Tmo1zmIhOTtzmssaCrQFzwaE6XPM4aZnIMtIv8hMMq+j1enUmi+HTk9'
        b'2dwpHcxOGqIhHYWBLpLUG4BVQ7GQ/50aiv+AroLKVoOBie0o3ucE77K6OhU5qgcWYVTkAJT21ICbU8FVcuodFpEDeTwltx4MPWS3iE/DeSPCBTScPyLcjoYLRoTbq3hY'
        b'quNWcJR29fZDEdYiBz1YzyxynAscKjHKtUtXKjUqrTa/XDCoNqQvKMzaB2yaF9thO4wFyakhDpUY6UmiCnuKCDGNjY7DEKEdRYSCEYjQbgTqE2yxsyLCUeO+nyaGn89u'
        b'2u/ixM7F3yEAnUB3Q1AD6mLPdmjHXALaQ9gXIbmh2xfvCuOcZ6yaz8vIOvqXJfro1eDQ7ovFilzXR1zJe7kLNVlLwnIX83MuP2755vNvDpTEpXMc3pJO2/VeZqT97M/e'
        b'sofrPG52zHrbUtvf9ELUe5tfuJv6wcsd+vZFX8wo+F/T5bf61b8dt9F51t9Dq5alfjZDdP5UxYOvfzrL8iePrOBPPs37oHVD6LyyFzqVZ5vlwtMTqnjhLr/cKHWk4ttG'
        b'eAPglW/WioG1j1O3wJ3KhegFeAZeeGJsy5vIoJdD4WVneJTVgb6MjhYNMgbmQD16IREdgM+zy+49dK+MnFVDt+GdLDZ3dIcDG9E5eJOKpMvh9fRouYxVn57khKLzceOD'
        b'H5NzeXVoZyncA/ej/TkyuB/utwNO6Cg0eHFw87ahgzTNKnQKHYZ7CvDSjPZGS+E5HnBz4KJ6eKkWXkONVHSFh0XoEk0TA8/ygMCeA1+Gl3zDsmkO5CDSXrgnFgu28ixy'
        b'sM8FPk92nk9x0bbN8GVaSQ16AZ3BaeTS7DwZA5wi4WW0h4NuFhb9n0XcrVsHi7h2JSXVqnUlJRvcrMwitwbQpfw1wC7l6+2Af6DBziLyxVONe7RF7N+W35LfOd4kjjKL'
        b'o3rFUXhu7Acc93hjLf2y+AcdSz6c3Lmgc1mPR09Rz6Jbc3rDppr8083+6YbptseTzqScSDmedjLNJI4zi+N6xXEWUTApIN6W4knMQ+8A4/zOcpN3FEYND7wT7nsn9CTe'
        b'sjN5TzV7TzXwLJIIA6/VxRIYgr8cLSFS/OVqCQ7HX85kp9tp0Lzt1Mctr9Jq5KT6vHJ1bV2f/eoaYlGvVPUJtLUalaq2z1lX/WQD5emqMtKkpfRvkLpsJXZGNCcx6tYe'
        b'BqxszIrHOjuGmcqQufv/5v5YEz8V8o85jAPXXdO5Q6VmxjYRedCJaBNYMRBF51om/yzTZ19iNfyUMn08raqqgtiXAQl7rME+rUqxqkypmLxBaGsZW4gLY10ht4Ku6d15'
        b'WwHtq+9Rfj0uH5fJLyGdKWU0xFR4UNkaHemQEcW64hSfW4sVd/v94GIdSmyj55mLdhtUdFH3sh9ctF0JO1yfuWDhoKZO6k4breCBNWc9YA80shtzeLn9f7hdPdq2HDdf'
        b'fex/N3G0Y3GQW9T9I28mUcPw43RDQb/WtqWw3Tf5l6DmVzxU/LmUoWtPZNmWwXMzOljD8Y0ulHIG8TWZ/AYU+2rtoM3UDZ62Nh0STGdLIrcRxq60Bz4Bhlrj9I5sk3eE'
        b'2TuiVxgxaP7h084abVKhewqDTvMRXdpTCvQgPUlmGjqVKOz/G8iQDtlWhyhwzjWZi4EI+cOzqT2e4hSrVCUlfY4lJextCNjvXFKyRqeoYmPonIinWU3NapWmto7OvRqy'
        b'H6KpJk6NrbJ9LuSYo0KrLVdVVZWUSHmYu9iAwacen+znTx2YdJeRprIBvi9I/OvWxrH963cEU5npjCVhfD/XzSWgH3y3MwZ4Bxsqe4Mn4o/JK8XslaKfhVc6Q3JvQCL+'
        b'mERJZlGSfroFp1rfK0nFH5N3mtk7TZ9p8Qw0LOgNmoA/Js9ks2eyfuYjF89+DtclkhzKGe58xgWuXk0LnhpPR4+OasV3oGvztLlL0PYsabZMLgCOKzA6gXvshvCLk/X7'
        b'8+14YB50f4LXlQzB563cVrdWIf7v0uqm5lRwsM/6r5tzGrPY+QG8TPH9WILuMS62naUXYlTMq3cYhr155CIOguOVgm6707jc8wP7nRTj85X2OM5hRJwdjXPEcU4j4uxp'
        b'nDOOcxkR50DjXHGc24g4RxonxHHuI+KcaJwHjhONiHOmcWIc5zkizgW3gSOeBr3q7Re5sm2oxFJIt/dQ+YS2lDOWhXxGSCduNHffeqByU/rh/PGsdn5gD2uR0Novbt3+'
        b'Q0tWRuA8yVEgrjJgRKu70zwDMcVBIyj2oHHBOE4yIk5kK63VrtW+gtvK6w4ZSo8yEstAHOs9CqTfXfVuFQ7K0BEUiGkpYbiU8BGleCq5dLWSYlmsnKKDryIcByuYrKHs'
        b'PSlDYsjevxrLxn08MoWMNmPkl9uBJ3+uwLpEdGDnoP3QO1TwGuaAVzEurggzcB0EaVSgF+Dh7ErXNrtRhDx7h1HENhxiP2L9sttib13bRo0bvLZ98E/cQkMqS/6yqtW1'
        b'akWVegO5LqZSJVFYm0aNkaiiupzcNzP8kZTVCo1ilYQ0U4pkhho/paGPZk1Lz5fUaCQKSYKsVre6SoUzoREVNZpVkpqKERmRPxX7fCR5OEYyLStDSrKITM/IKCjOLyrJ'
        b'L86bNmMOjkjPzynJKJg+QyofNZsiXEyVorYWZ7VOXVUlKVNJymuq1+JpX6Uk1+AQMsprNHiaXl1TrVRXLx81F1oDha62ZpWiVl2uqKqqk0vSq9lgtVZCDTxwfrg+krW4'
        b'zZQY+I0kx9o8ZPykULqIz3apj615K2uqlHh4Pe1hK6Rln7f+wG00t0CWGD9+vCQ9d3ZmuiRBOizXUevEliSJrFlN7gdSVI3SgLZCcXWsJWLf6BQ/Sz42YMrmZfv1w/Nj'
        b'0SabG+v/AXkNWagGlDGDgJ1zvo5gOngBdqHdZHc4Rk5uuMmZj/Q57HU8jUwwPMGDL6Fdq+g+h2/NPhDAgMrqKaXyQ1UVQDcBB6LztdF0g3g20hM9QCxqxL6CuWwuxZnE'
        b'aDsvLwv2JOYxAO5GJxzQDY716MPCRfSwSenu0FLnHRJnoIsitMJzc4gleHQOOSecW7jcKfOJEgC1SOFZMDfdDrWtG8du/XjSg1CVq5jSmIfZWnZH5mE4nz04kFMac26a'
        b'hL0WBV5DZ+1IzuhsuC1zpCd38WBiY+dkot25AjALnRKgy3AP6mYvJbiNtsHT89BF7RpyMcF+UoNGJ7V9yh2e1gcvRpUHyva20A2eXeo3/paR1VH7urDz4xbRh453pz3g'
        b'LKx3djCkf1IZ+/Djux9/+sae2IVv7vScKzTYC/+8/8MCjzHPnSsRbpV+Opnx+fjfx+a9cO/Cy2lcY/2sTREno6cddW8zb5Y9eHP2nvv39n71Svn9PU0fm0XFXRN6b93T'
        b'Fi1Q1Hnclbxs/PofgQffWLvs/Z9rHhYUrOtXfmHUjfGa9eLfHnZUtNc9nLfU81zBB//22/3nD39/+8KJ2+qXqgM/dBs7p/7SnB0P3+vPfVdw0e7Tgp+OyXvj8775b7/T'
        b'fkb29yM/+9cfUr7g3ErzEj2YWvRVZd7JSVkndv71lRly3ws+xU3viUwzeyv2/itmfewLq9wvX7h14UyW8xa/1o0o6u5vPuG++cvgrxzmi4J/IfWgZj/wAmqBR51wY0vz'
        b'dLIouwq0O5YDPGEDz34tuvaYXLETCXeE06MF3SEDpwvoyYIatJXmgTtg14oceV1Bdl5MFtyL9rO3J/nBa7xqgTdroboH3lIQUz1/1DZgrWcY8ziUPH4JthXloH2ZeWgf'
        b'3IefRi970ww8UT0X3UIdyEj1YfAmbM+xWfXtL6wcsOmbJXtMzk2uz3bDYwdnEI3ItUyZcNdzNMfYHFkU4RtyJGEWvGwH9y9YTbVT2Qszcwpk8PBCco0TGVpOhRy0zw9d'
        b'pMUlruHiQUbq8gJsJOTw0WEG3YaXYRPdmAqelY6lJ3gHvkif5aIjDKa+bSzNei5s8yNP43b1nIo5lY9ucxi4Gx6mSq05aEcWfjZrzFDdWW2a5DFleMM0V6IW2yul126x'
        b'bZqj9qY8Hw2v8tFOdGQ6zQntsIPNRIg7DU+hfbkMJuMYAw2oxYs9rn8AboVUAXcuTZ5HiLzBwCNVz9F+VcFr5YRGtBVey8PTCrVOcV3OTUH1i2kl1DhuD364NC7XirFd'
        b'M7gzATpEez0Dbif6P2JbeSUGt3K+LJMHXGEXdzqm6JrU7cfcjyOHuwb0dYO1dljkUmO4UFKCRXx25pXbQqgk+jbDSqLLHIBPqGFjZ5LJO9LsHWngWbzJqXb3cQ/9wjqX'
        b'mfySzH5JveIki8jLtk9n1LRMNkz+g19Yb/g0k1+G2S+jV5xhEZGDte6T6OniCe2bOjZ1rbkfHNcbHPeQJEw1+aWZ/dJ6xWkWLz8D1yIKNKQYlZ3FXUmduSZRvFkU3w/4'
        b'7tJH3v7G9NZ1bc+1PMeSg0UbT6klOOxBcBzOrUfco7jmfSvs1pqXIkzB08zB04w8I+9RWGS7A/aUY8rbNrRsaN7UuolUI+CBd8R974guXle5yTvB7J1ACEyj5KSY/FLN'
        b'fqm94lRcL1yGu9ziF3hMeljaHt0RbcgwZFg8fdtKWko6i0yeUWbPKPKkvEtnjp1FfRa/4GOyw7IunslPZvaT4eRWpWJAMP5ysP2yKhzHRhl4ZmGoJUBCI61fkjAaKYno'
        b'tLOI/S3iYENOJ88kDjeLw9kf9iax1CyWsj8EJnGEWRzxmQM/xOMxwA55uN8ZhBD1pYsB/xukPXBntQdNxNlLnNFk6e/ekho+1MiwKh2kyhy0VfUCoKqkYeMsmCggLoAB'
        b'hSYZbhvtGWYKUTn86M6PquM87ZAGXnJNd/w+Os56VsfJLyFg++n6Nmsj2fRtC54o+oxFHYus+ravwosGQDqBTxjQ2vBTpEalUMpqqqvqpHJcHFdZU/79FbG8kjJ1+TPT'
        b'uHgIjQttNIYRGrEU8K0kfn/a+FRX9MzELcMpNGdIPCUq+ttR/A+lrQLTptEQ7npWuhRDGm2prdHkg6WEH0piwAgSVzCDiCUNKeXgJUDBKrso7z8z4UrGum3BEm4OjN06'
        b'uG2/Td74vxK+nBKuuQWsU9Uz07x8OM2JNppjn0Wu+b/SXT+I7prvQ/eK4XTH2+iWfbcE9cNGMjtNUVqfmcxVhMeuAxuPxRVRjQEma/AemMQ62iRV9Jbbp5L3/4ftg0op'
        b'56sTI+TODKIz0ErUw6YzrUq1it7PW6ZiVQkjHiR39lr1J3PV1ctx28zQaWoksxV1q1TVtVpJOm6LkWJuJG4w3Gz4wbXj5QnyOOm3C8KjXeHBzy+SMnS3vyhhTDQFmtNQ'
        b'F28qA8+lydS7xqbytamko3/7Odn8YDc+/Mypvl5xCaXM1OLczKoKn9Sda1x+mSCpeX/7uMRp44MWencEvv1KuyvoSHP8U2qRlMduud90iqKQ1oZnxwewiPZ0BXtJ1s6K'
        b'KQOSStIKm6TDCipwG7zLbszfhXuLbHfIFsITXHQPo27Ughofk7Hq6Alv5qDd3vOx1MBZxsQ6uT91y8WObHWQu7HcbGPVGkDBLTn5SbdZnIDYp3VSryjSEiZ9EJZ0Pyyp'
        b'p+jawld4r9q/XtsblmQKKzKHFRmmt+Zh7Ni6uVcY9oM2Ycg+wghCVg/Zflnq9F8xzNnOcjVBfc9wlojYNDOY8/7LZ4m+ahgx0OeqalmVpq6qVr1KUWtdwnVaqwaPXrld'
        b'q1FUaxWDrs4uqxuREckjhaqKU0rzcBqcFf5SLFdpSr9DzzTaBqL19MVP1PuJ8kiYk1RaPU02A+gmAiq437YfXXsEm9GRIRqkJ+qjhfCyuvqFNYyW3IXRNvs37DV7ZwsP'
        b'NB4XZcaWK0sXuLwq7P0pT6ya7p2neLuCMc34Onx1fGfk4XNjO+/l/3F9vXwXPV1haIqrca38/JaUQ0XWgBqfAVWFTVGBBft6nr1CSkXnibDHHovO4qhhwvMg0XkBOv0t'
        b'B2MH2XlqVbUlto6iYG2Dr23wj4ii/Jhl5cdNhB97RaEW/7HG1M5ak3+M2T/GMN3i7WfQGpOa61rrOhNathi2PAyK7JXONAXNMgfN6vWZZROheuln8JkllkX3PoVPn3JY'
        b'6R3Crk+neAMz5ODSGsy5PoRLv8P5z10p9Uyo2XVoJZ55ad9FYCoReQgCMQfGDcEfz8qNcjxPy0gZRKs65NDVwKK1HTwxpWsD9DAF2TyyHaj47xy5wsv+B7nMKDsrA/NP'
        b'jUa9XF2tqMW1VCufBryqVeusq3a8PH4U/fXTlfZKVjNOG9B2+BQXJJfMUa3RqTXW9lViX3mtRKkqU9dqR90oILMfpkBbs8omTKgx5FJUaWtoBmzWbBdVqDTap28j6MpZ'
        b'ijKmZWEwp16jI/lhoBxJgJtEY6MKl5VVqyBQ7tsn0dHMEe3zdZPJfHkeNcDLOfl4VtqD9qyDLbGFkfmywkx5dh454tUYOwfpcwszuXOk8GyWZFmZRrNFvcwBTFvutgo9'
        b'X6SLI1nsXG4/WL1On23XWB8H8Ao6WIxBykFmDbpuP3+iM3uH6wF0IRRddcZT8FZ4F6AuAJ9HN+F1HTkIjK6kwBNaV928TGJlV4z0MfOQnir3zhZlxpBimrJy0W4Gz94n'
        b'pevhoTB0uogDCIg5CG86z0b7inVEwQrPwB4JoQweENiIWz2Q6+z5snl2YPZzAnjyObhX3eGay9e24afu9DgeeTOFTP+mmwfCMTLb/WWO8YOAXeLXVE3Ozud9FV+PfS3/'
        b'ND/XecEr9IirLj4+vpbzc8Fh5wmrfGe/v+LWb8uOe+SHbTSmtJ+zbF3Ru6q8uolz+CeOooWv7Pr5X8TLz1YUbf7p15EVV0sPZ7cGG7dtAedmJPq/+7D76NsLHro8rktL'
        b'bXr/DecP17zy9zgevVD1ne0R81/WSR2ojtPT1wuvblbtZwk6DJyqOeiIMzpN8R68kLbUKWpLFrkZh6wmtmUnGF7loUuoZT17sY5xWSE9ho6uoqNW5TbRwBIsGIp2uuY8'
        b'UfPCNnQNOAu5nk7ZVInqXscfuqCh2/AFqn1HPegFSuEq+AJ63oYmvb2sYPIcaqA2lHAHPF87oBSnKnHUgK7Qo+630CmqBU6HjegQtfTBs8LEWayKOAy+yBqBpjnjKKIc'
        b'9oUvs/rh7BXfddx367Bl8sl8Qm5rHLLoDImiy6TJukyWOpNjEVMIJt2E1xbPBczDoKje6HmmoPnmoPm9PvOHaCut54Tn9oRdizH5TzH7E32YZw5DF9GMV8pN0ixTULY5'
        b'KLvXJ5uocadY/IM7Jj7wj73vH9vDM/mPM/uPI0/MZp/INwUVmIMKen0KhpUiNU7uCjX5y83+cpI8k00+9ZVE0+Cl2qoCZb8M+N9gc3h2uR5YKZ6+ZlNr+CGL9qMRi/aQ'
        b'9mski/YmMHCwsMCZYciNM8/k/KjWT+0OseCS66QfoDnkleAF4pkX7uNEJieHAdj1Op7qZp4sKd+mNPhBmjkpJVD37FrDk0MJTB11mckozhi+Mz4KqVJuH2+VRlXRJ9Cq'
        b'l1erlH0OeIHUaTRYuJ5ZPvg1QM62arQActuOzcSDAg77AfskRu9C7+Tk6F0rnCn84GH4McyEYzPfYRRAgUP4IyAGbwvfCj9GjRsCP9q/FX6wrxZi5Ra6kg9WRDzdvIO0'
        b'DbuO254duNDi6Tv1tCXZp+gjuBdImIIoc+SSDEU10XcorHFlKzAiGRWKECMSjA7mFiSPj4un5iPEtENJdFfq6uVPLX6gA1MkM6sUyyXrKlVW4xRcYVLnJylslXpa8dU1'
        b'taMUo1HhilRrUyTpwwXCUmt1vgPLDNwXMAjLOOazsKHDcaMNyRAYg17iyAqR3rpaFmfi0DlWYMMkeMAD8AC6moOuZoNwdNIVHYYn5+jIRTxwWwy8myOXRWXjRfDJ81Mm'
        b'FGcOZJ6ZXRxpvbQcS5HoVKAz6kI70QkqmH5RkZUUzpGQy5Qd0brnrFYNrQTmjCqYyrLzlKhx7mCxdM9cB/QybId7KEUYGDWidrQHJ5ybSXeMswgGiiao6AnsQvsy3bJi'
        b'snPlWbIoAS5K6rwGninXxeMMJsHWmUMgGmkPUngkXmOxuBkjnQ9PyLL5YAM64wD3LqyWcq2vDMgOocVycwsBbzIDz0N9mo4sDfl2rtH42SiAn84jJzXaORtR9yQd0UrN'
        b'yhoXgBqjs/OsbcgAUQQXHYF34XH1BM96Dj0stajafmfzJHLKZefR5Cl5u1+F75WvAYecux4KI0oTU8seLlR83Hqq7dWMXyeFdB2K+el7/3p+1R9067kvBh26FfjXW17C'
        b'6WJwYMGnDaUXllx/eOPTz/Y3xEwKM4w9sI7ruqLi4a7iKZ+7/HLBfe68BUvbz78+17/uI+lSk+b9ll+8WzDlvOr45ObgcUVjNPmG9RU/rfzHwXfv5GHhAV39n3uh436y'
        b'JW6dZJ36fur/9vn+5u9OwQnj7ffHYfRFVkU52s3PIU22Ex5iAKeMiceYtIVVtXX5oENOWI6fkzAa9vK3p/CKU4ZRDovfHILI/jWFb+QtVxQ7zcQ4uTUnKw8eHh+FwTMH'
        b'2MM9HLgt2Z5qE+zQ0Qgb+oJX+VFPTB8il7LArgmdLabIEJ1RAx6P3NrwIrzNKvn24xHYSkwN6FUpJeiAoIozBifYRoFdSgm8oEbb6LnXAvZS/Rjcb7FcdHADriE5oOML'
        b'b+D+34P2D958Rx1FKRhg48H2f9owJyvEyN1yJwIorNPMBtFglGENpPhMZt0zL3MhasVkshc8h3noN7Y3YrbJr9DsV9grLrSIvFvTSEwe0zn9ZK45bAL7gybLMfnlmv1y'
        b'e8W5I/bTHw7fT/c2pj7RkdwXxfSKYmiaWSa/TLNfZq84k91Fr+gsN4mizCK6SZ1oCYwyLu0abwpMMAcmGGbaklSaRLFmUSx7NCcw9Njiw4vbl3YsJQl8jdOPZR/Obs/t'
        b'yL0viuwVRdJSppr80s1+6b3idHaLOkBiCQp7ECS/HyQ3BcWZg+IsIVH9djypRz/AzmeAFyJ6TBy6L+0IfAJaNw1V1bix2O8T4nxKnD+BH7IL/cTqYeg+tBUlfkmQyGj9'
        b'd4bgw05g3YvGfZjjwjDRBP39SM6PhiGJLua4wwRw0zWd/31BpJQcsbHW+Jlx2utDN3dCCCDAyyWFBwN4YvBujpRHzPrPcvJxeTOlXpod5FlyqY5mJ2DPiylryktKqFWA'
        b'hry7kZoi9HHL1OVPtUfos7PtVRJlOlXR9bkM0WhRCWCQ7PAlfcpWWff/zHF392GzxaChthvQ4wRsY/qS4VXMpdPDwGkCHsdF2A+IYw9cPfXzjYmd/M7yrrAubW9wYq9f'
        b'0q3E17lYxuri9mT0cxnXiZ8B7DwmzqPECZaUyf3cJJfwfvCDnM/4trz6eSSsigHiAEOyRUhOmljEqf18jnjSZwA7j4lDz96L/A2RFuHYXuFYizgFJxCl4QSitMfE0Wfg'
        b'BINzSCc5ZDAkiwzmMXVpJuQ4hEVITu1bxNPJu0dmkjTYfUxd+g4SNp/YXmHs0/PxkRjWW4SJvcJEi3gGTuMzi6TB7mPq6jNxGq8gwwKLML5XGG8RZ+A0XjNIGuw+pq5+'
        b'5jB6ZhJ6Mik9mZSeTEKPvT1ps6c5YlvX8YzRvS5jTS5jzS5j+zkOLpjtn+KQoxoRA6nEIDDcmGkRxvXiT0IGS2kgpTSQUopdfZ5tiIg6QweV4uki6Qff5jwpioTEDOnC'
        b'WaQLs0g52H1MXdqLg9MUkjRzaZq5NM1cksZKS2intiupx7537MRXinpdsk0u2WaX7H5OkEtYP/jhDiE5hxnIafKQHppAemgi6aCJpH8m6meRf+zZFmrpeBc2w4va3DL0'
        b'cj6rO2KA4wYO2hcRNeJdXeTv83xyusVj6OkWJWcRT8ldxFeDRQIlb5Ed/m+v5C9yUAoWOSrtyOmPVn6rfauwlangtgq77YedtYjD8qOTXljBVTqMOOlAToe4WE+qOA87'
        b'6eBK41xwnOuIODca54bjhCPihK2uKnfraXM7ejTBTe9eYa90H356ZBgtHq2utCbCbo9h50+I5Evycq/gK0XfkYsI0yWuHx4qJu/NrOAoPevtF3nitmDomRcvpXc9WOSt'
        b'9MGuDznFssjXms4Px/op/XGIvzIAuwHkPMqiQL0APxmE44L0APuCsS9YKcExEvo7BP8OUY7Bv8dY8wnFIaHkJMmiMGtIOA4Jt/rHYv9Yqz8C+yOs/kjsj6Q5SrFPSn1R'
        b'2BdFfdHYF613wL4Y7IvR22OfDPtkynh6yp/cWhBb77BIruRRQ6CEPkH6KnpQ5dwQAZKsm2wEe1aFfZMvlo3JuwOXaxREKGYl2vK6gQMPw44VDD35osEZrFLVqssl5FCc'
        b'gt34LGcFcxxAZG2cJ7tbUFUnqalmpefRpFspp09QslZRpVP1OZTYqOjjziiek/9VWmVt7eqU2Nh169bJVeVlcpVOU7Nagb9itbWKWm0s+V2xXqOqeOKTKRXqqjr5+lVV'
        b'5FbmjNzZfdzM4pl93Kzpc/q42bMX9nFz5szv4xbPWjDzLKePzxZsbyt3yA7RgH0/uXToIBfjGo7WbjC2YTemNw17I7OSWUlz0Yo3cToHo6SnDGStRy3/SZySs4mzAcv1'
        b'I9/93MjfxAwN3cwouZuYtRi2bGKUPCWfUsN0Dq7Dk3y5w6gU+D6hZ0jMBjxFbeCTWxNJCdW4VKUd6ycGMMNp2ARKBtRcuL6DavK0+uInBo7oKe0pPnT4oGQ05dPwU0XW'
        b'MfzkUNHwB56m0qG9zCqUFGweNORbNp/Y4ZBCz+3MLZAlJcRPGMwiSpVcklVB9DsS7WpVubpCrVLGjKoFUtcSnRHG+7bzQ7Rkm2KRZUdFba1GXaZ7ih4phUSnlCpVFQoM'
        b'OwdYpFSyrlJdXklyV7PthBnNWg5mnpF1+4SMi6881dXUUuhJbSLCtRFfMfI+Ju4TMrV/8g3++4orj4vLl9r1CYcXS+xbFFWrKxV9jvNITWZoNDWaPr52dZW6ViPAvdjH'
        b'163GU4DGjiF34LKylTsB8uTU73AUSwaCZJAunZrrurH9PGCt+1sCYX8CWAlXjPEXtQK3BIeag5MMmay8up682LQz/b4ovFcU3rXggWzSfdkkk2yKWTYFB1DBMe3WetNg'
        b'GdXH38g1zmh37HA08HEmxnBDmiHNIvY1zu1M7+LifzMu5ZzLucU1xaSZY9JuzTHHTDVFppsj001h6abAaSbxNMMMw4xH+IHi5nzDDEtQuHF5p6q9uqMai5pOlhDpmaAT'
        b'QaaQeHNIPLnQwYD/fd+j8hVUcqLN+jShydZYNpnp70OMOxcP2TQfPPbpCKxbrZKU4pFVjoWZKvl09ru0VK45+/3oZHf62S5/Rjq/HEKn7RqBr/ypdfHoHDeEII6NoGkj'
        b'CHqWSXfFAIpxGjDv5NJx2mev0JbQg4d99qr1q2uqVdVPvaNgeKX+RUaqH1spZceKB0Hx94PiTUGJZvJJ6w20XVrwVTm1BdatKlNpSEdYe0CyukpRTgwUFbWSKpVCWytJ'
        b'kMolxVoVnSvKdOqqWpm6GveYBpeqLC0lrK5QrtDhhCTB0FyGNtfAWkavmLUfeN04GHjduKP1uiBmFHuH/8gtCR/8ZbQ5v3g1kZrZ+V61vrxSUb1cJdHQoDIFMfOoYa0Z'
        b'cSqFZLWmZq2aWCqW1ZHAEZkRW8fVKgxLMnAnanDTTFNUr6QmCtraGizT09m5+plmYussbCOphJJUSnpHR2dedp4nC8KAaQLuHXL6cxRLMJwSo6fKmicQKUaiVeMlzZoN'
        b'eYyYrQ4+Q/q0OlozSqnQVZenlFrR2ygmZd+6D1FWU0Ne0CypGLzhoaNdoRzWDaOuUetUGjy9rMXQS1FG7G+fsvXxnVajrvk6ooKBx+BptD9alvmcKiuGaJJz5pOdAbQv'
        b'E3sLiiOzY7JkArDKwx69DO8l6yLxI4I1lXAP6kHXCyOzZeT93Puj8+F1dGKODGGpJWkWHxpR5/IaNRXW0D1yGb1WnpeNDq4ToAtlHsANtnHlq9EpeqgxFRrGDt4riMwn'
        b'L3s/E5Ujm2PLPYePJSJ7eAcehLvo5QYbA3Va+hqdPHQPHeADPtzPoJ4qeFFH3/O6fZPHXLgXtRajvehgMdkuiIN3Chh0DTUIZtJTkUHwaroWNi7BVPEBFxoZuDUA7tMR'
        b'zbQjPI92aTPZvYQceJEHsje7Y4JhN2qHp+jTGQnwZS1pGHgAncSlb2bQhQWOReoIZT5PS16OdfDMrr2Fl/NRnHjTLy4fTc7yn/dv/vjJ4NWm2wvOFd3Ybnzee3zOUvc/'
        b'HbnyYcTlaI8HP/G4rnxj8sOjfz368uGafv9d968kj3ml/vPAn9T45uS+H/TqpnfGLTn4Zbnllxpt/LaYsUJe+ernvdbxmN/2fuppx+ve7fru7oRrjfU16F9/3B6ifS3i'
        b'q31/avE+Xnwz68znyt8siT/bzz3yTd29h9c/2fSx12bVyogvHolDvggP/vWHv0x75a3yjl8dbv3NJ70KUc94xflDK859eeKFa5kf5Z4r+cWUTeIb2pbt+x4vfdWz5pIp'
        b'tOP5zHrfBt9//j3R/aGsstbt7L8Mfzr94ZEvvjiz4x31/ZOT+7vK4L+uvn824p/OFd9wf//PrI7fz5G6052M2YmT0R7fbDyk0B47wJMx8EIE2smeW7wrWREtQ7tRY2wm'
        b'2hsIj3CB80yuADajbmqe4ZWIuug5PGMsTsUAXiwDr8LdaY/JyxaW5k6LhhfRi9l5uTgmhIFHq6bTAt3QFVlOVl5UHroYawcEPI49HhHt7KHAg+gq3JfDgafo+5rwc94M'
        b'PIFH0kV63hLecEInyc7KKPsqNzLRJbivim6P4EHenRctl0axI5GPizzojq5w6+CZyMeE2bJg87ycSXbWW60ZeGwmu22SA4+Mi4ZHXKyP8fIZ2LMBsds6cGeaN6lsVowc'
        b'NsbKMunDEgmvCl5FN5AeGh6TlzSiAzOLc54wKdwbm42Z+ATl1Cj0Eh9tj1nKXnJ2B14ck0OrmUVfWrwXXWCAk5KDjkTwqX3LJnQd4ixkDOCsZXDJZ9Iz4Iu0BT3GlAy+'
        b'c5RTWlwXDm+wm09X4HW/nLycnDw5aozJgXsLxEWU0ii4jw8vTYxibzfbuh436x7Yg7blwwsxAsCbzsC78PxKqfBHV9ESxzbzDd3U8WSn1pKhq8mGACucGDWW7vMctO7z'
        b'FAmBu3ebU4tTb8A4k3C8WTi+Vzje4hXYVtNS01l+stLkFWv2in3glXTfK8nkNd7sNd7AtQi92pxbnHsDE3oyTMJkszC5V5hs8fI1lBtDmytbK3EKb7+29S3rO51M3jFm'
        b'75iBE5fp7B7RFJPfVLPf1F7xVEtA2IMA2f0AWZeyZ0L3qluLTAGZ5oDMBwF59wPyTAEF5oACg4MlNOLMxBMTj6eeTDVwyUWbPv5mnyiMtX2DDAKLX4CB7N0cyz2c2+Vl'
        b'CogzB8SRNz/JqGOYjtF9Z445OA7je/8xxgmdSV12JyeZ/OPN/vHEKjegra6lrtOHvVGtS3nfO6HXO8ESEm4UEIvcGcbI5gLbNWzJJnGMWRzTSz8WUUAn1yxJuC9K6BUl'
        b'WKQJhgyzeCw5FjnTIgnr5HUWn1l0YtHxJSeXmCQJOB05gTmWOpgQ7+DOdb3ecvwh75aKNBbQAr+0eAcOOeTopKkCP2QDib2QbfgBxqm4x799YHzD2F6rS48xun3ni6Oe'
        b'6vxohsLFgAoCROIbYuw/YLhAbW75VmN/Hn1xiB3GorbXHBC9yrDLKf8DBv/E6OW90TBoBguirFeZsEITgdoY0xBcNCCVWKEowaVaq0Q/EvJYLUWGYdlhyHV0pDoSQBWN'
        b'RMUKgryGAEUbbqshgJKYydQRyDuSMkV5JWtAu0q1qkZTR616KnQaFvtpFcu/h4LlicJkqPw26GRbrUKzXFU7kPJb7WKqBwxj2IFvs4uxgXUCsVXawWrLH2T9Sy1V9kS6'
        b'AEl2Ark5veqPa6rYqy4cRQEgoKaWBAaUip5jA9/LuQnW60gWU9cYXbWR1DzEO2yM1mUW3ObCAQzaB9AF9DJ6SZdLFqQjsBUeyxmGW20mODYoB19CLxURO9z5GFUSq5on'
        b'tr147doQJExB5+EFteygnqMlu9NvyN/bOecOsRmp/c3tP4R41df7/JMrWDt5+7aDx8s6F9f7nKtVJKaW/dx8akqjf/N4yewx4bsL7qX++m+hGzkHdpacaf71P0xHjclT'
        b'ooPbLHf9Jr6/49HHn/klX81acmme4HGh8eyspivijw7+5V27N9753a92bvjor00pH03afUr77uKgXxUumXEu4F/PjXPf8rc/xibfPJBconOcG/yuzzuXM3MmyO46FHLn'
        b'n2pre7dzwabcl1t+69/YF/SidIcAdmxbknc0+u/LVo79KO4bTefLt8VdhWcqet/Zogta+6Y6dKPJ9c42+w6fsx+K3kdfpq94zNnx26m9t2dLXemSjwHGmZpBb4zaME2G'
        b'diXQxdx53nhqo1SKW4yFxW7zuFXwspAFJHdQ98xhiIRFI3PQOQpINixn3wDyPHyxgtg0hadgWEbfAOIOz9I87KbBk0MwBYsoMD55kaIKdBJjJDKwnqsps74qZLOCwCrY'
        b'zdqrLMaA6nR0wXS0b+ANPU7wCgedD8CIht6y8fzGqQPvCdFl5THwZXQYHaZx853grmgbIsPt0EBQmXwCfXtnRknwUEy2AXaxsAzdgA3w9ONoMgdnwYPRFLBh0oe0hG4B'
        b'BwOm3UxJrD3EdUBnKfCyc5JHU+MaPhCs4GhRY9BMdIEW54U60cVh53hQD9xGLG/gUXiAomaByDM6Jg+LTdV4VDfCbizHuMEDXE0c2iF1+H7YyQEMuu/VerDOKttucLWu'
        b'htbfFBjlW4GR0h0EhB2bfHiyyT/a7B9N3kzkb6zt2MyaqVj8gw05Fp8As080xiFeQW1VLVXN1a3VBPoE9AOeezwb2VV+qfJc5dkV3Svu+yT3+iRbAoKP5RzOac/ryOtK'
        b'x7CnN0DWE3ot8tacK7IeGUExWYez2nM6crrCzFGppoDUW+X3A9J7A9ItYp8HYvl9sfzJJbE+Aay+0bt1UueM+yJpr0hKT/h1zej1jscfarq8oHdxiXlxpUlaaQpSm4PU'
        b'vT5qAjlmdIV1y8xhyaaAZMMMUjHdffoaPoJMdL3eMfhje7zcJC03BSnNQcpeHyX7bOTJAlNAIn7QJ/CY62HXztqTG3ommXzSzT7pmCAMYtYaVZ0LTN5yM8Y4Qvngd66w'
        b'WlyqwH2GC8PZ960MuTF8DkExw/otEnecdiv4/6h7E4CornMP/N6ZYdh3cIBhX4RhR8QFF2TfBxVwV0AGEEXAGcZ91yiKCyoaVIzjEkVFxd0YY8w5aZsmaTpD51XCaxrS'
        b'vrykfWlLWtt/6ntt/+c7d3YGF17a//sLHu6959xzv/Od7TvnfN/301szFbu/gl7096ocLf+CGcmP6EbGcnNxo4l99WrCCRlrenpDYg2nLxanKkLYKZXxXiW1fZ2EL33G'
        b'i6h/JoiIH1crEdAqGHCqaGyq0G32KQb4VUsVdONy+CblgFuFQeuVO2JbL9LvrVtEFEBlANDbVmaQts0sbXiK2hN+Sad5M0wlO7/8TML5BCKCq72SBsUhb2Z2C3oczpSQ'
        b'RiVOVntxwHdmx2cG0KgBBqypX2e446k9fPNTZPmijawZew3X3DGaPNuU5XLxRlZlKlJafdPymKwxrMXE3Z6M3cg7ycp4pm+cpEdpZveCU7aWh3AkheGwaxO5o1v0NtL1'
        b'Ywwi4cp6BWFr9TIqTK3npwZHrreNpDuOkc/YSIkNV4Oe9SubG+qr61squL6gqG9qpH1kwL5sXTN3psLVKWfqO2BDJc8BO+60lUSa23YEGyx+B1wqmuU1RCirqaCvrPfW'
        b'V7jZ41lQ3bsZOmZymng1qjkaz1itZ+wQY+seRYbDjs3dXj0BfaIJatEE0gS04mQyQPrOZ/vDJReLzxb3ht+O04TP0IbP6MzuzP4yNEYl6U+Y2L22e+19r4cB98nPBzYf'
        b'u3xAfob4bNw89luGDZvPPqUh6b0B89lB/5CuQjIcifzbnYYfjBh2B8FC6yhZJshgY5oduZZ1NWp6zz9lQw8nBNL1dhwboiLXCyJjSaXwIiVycCgs4XFjm8GMO9jopYgw'
        b'TE6di+uPo7gHi4B34YxOo6o/YVy3onf87dRLW3q2dJOfx4L3nR+TH7VIqnaTDi+YwZoXbF+hWCONLrU83SgAYEvPbGEECI5QcFQP7+q2FeBgl5DrYiCX3oNPJQUM2oRU'
        b'UbAq63xBr+C2szpsukY0Xe02naPPqkF2DsONfSrG2r+NrIw178ibWFPqN7Ir6F9aAYR+duolnhxOebl2rWP7YlbPdl0xhBUVDeAaytlQCrhdSpL8KZwrhI//E5+YPjJH'
        b'Z/cma3wman0mwuwl7lhPplORRO0m+WcWidUVqQ6KxJs6TV73osLUmBeG3NZaL8x4jc8krc8kfWHK+yjAzHMKA9/UDatk6NrDsxhWg83alcnQtoKmaXI1L5rxmosvNZ/1'
        b'WP1TetbHNUKBsdgWFtnG4YiwoGaVGQvgFk7f9KbXw4Yfnnsm2x8Q0rWgO6VnSl/ABBgtMtj+kIjzAb0Rt+P7QmaQEcU7kx18Pp8MB4T6E0t9GZwMXnOocPOcyms0rzy4'
        b'bebplHwJ4eIgVcqJaWpRlNot6p/Z6AQ6ztNGx05/YZurM+9AcAtJ5PWsTpP2n0SnjSmdvOkv7hx15vyF2zVA6EoDoSMOnDAjPH8+MB5Lu79gnIfDL7NxnnuwAaoaVkXQ'
        b'SEViaz7RrTNymY6+0bMSQHToJhh/I8xphnTmb9FmDE0i5hLfOLRSCcOsb7qz5n1TX3QyZVTJZGZTBr3fDAPUJF3BrQ63sIhRlWvobq5u4VB2frFGlKwVgV7scN4Y6g5O'
        b'957HmWF1WMvV4ebnNSWYq7mSmMzV9MEOKAqcydAqfH3j4Y2qbG7T+Plj6/dQhQ4vWYVcr46Tb3qFalMol5rP9HC/C7rOFqt93MD+RB37HV++Auh4v+1F7OcoMmE/fdBm'
        b'Inz4BnTagPtElVIjitOK4tRucc+pgKXMc9cMti0mL5UyFqy3eUnWU+NR/oCLtKklnwjkNeASqUZm0otsrFWHVbGbVMpKZYNZpdD7A8CBaYz1mY51j/5MLFF7Sf6VHaqO'
        b'0ylqe1GNcsUxqVH6oAMa2Y7nTyQdz6+74P9Fp3K0UtuOL1nbVIxmE7iO9vI161hR0SJX1sjqVxN2eBjYYXj2Ogwx80eoYRv3Sf3+wU/8E/r8E3ptehUa/yla/ylk0SMO'
        b'6krtttGI49RecYP+wV0F3d4a/3iICOmcoIqApReHra32mvj/Dat5VljNe5UxjZfwyrx2ItJxQ1OTnGO2p4HZxoenoT+9JLdbNP5Ttf5T9dz21ojj1V7xHLcjNP4J/5e4'
        b'LbTCbeErzSARr8psWwp4Yj5kwf1F6OKHrHZxw6L8ayMnbAgnBBaciHkVTrSYbBqZlnMja1nSl025iLZT6rlHQHln3GUzS0fj+SPH1/J0w8aAkDQ+whwyP1M567i5sCU0'
        b'8nzAZs2ypoYacAOwsqq+UVZjulWj03Y11IBDRQWXL6kEd0Ml6B9dN+yPWmnqQvfppk19rcZ/htZ/Rnv2Z+IQVfj56O4ajXi8Vgz+kb+MjOuW9Sy/H6GJnKGNnAFYktmd'
        b'k/v9QztzVCmwoazxn6T1n8Q9mEySruS6DVlk+U8HdxrTn4OzNJ6xLoo7mrVlKy1Wv4YcSSyn0G51Zo2T3t+H0VasYwqdKVu61neu6B7fM00jmqwVTVa7TR4FvQ7Pp3fn'
        b'y9Db3KQwo5fevw2d6bTV9YyhMxWZENViksKMJLNp/AXDAdVlnWveRp9DeNVSc8Lp/SNofUEmjD5VDQ3reFNXU3dLzyaNaJpWNE3tNu37WqfJ172AyvrGFjMq6f17QKWn'
        b'nkrqq60r9dCWji1qt7HfB2W1L6TMns5OVZw7c5P5Cp68b7aC9G9Xgh9lzn24fstADvaZ1sfYy4zO6oSMmdxemtzVtHnIeNZsRGR8mYATgdcPK9Amsw3SEbbReXuEFiM0'
        b'/0XjpG4bHCyomWehVDm5vrEuuLlpDafenJTIWUoom5ubAErlGS8xfoBNIqNpoL6RDtitUlY1ttSvr+GaK+c/b8CW5FRX36IY4NesbbaYz4w+9Lgx1VghlAKzCtE9+RFU'
        b'yBJdhXj6dc46PKV9CjUOyNf4FWj9CtReBf1jAtrrOmWq6u7cMys1geM1Y1K0Y1La+VRG162FM3sDND5pWp+054jrl6iYDdUrSbAwRJb/XUeooqGpBdDB/IEDLuZqPeS+'
        b'tramuqV+dU0F6HMQ4aihStFSwWl3DAgqlPIG+RzgCDjBNjFpNvT5ATvDIZEjVafgVIWpShE9bZCDi29uRquCAPwry5dB0ABBEwSrIIBmJ18DAbggpItx+XYIwEefvBUC'
        b'WE/I90PQDkEHBK9D0AXBGxCcoXRC8CYEYPgu7wX+/LNhwYfZSetOJQUsnLRxjQRQBxSRAnM7aaEA7KQhcGB8E1vzB4PC1U7+/QFBrdL+gBASiINai/o9Z7Vm9YuzyVVo'
        b'pNopaNDZq3VuZ7YqTFWnFsff91Q7T9M4T9M6TxvieTqPG2KeF4AJ6nRD0mjGO6A9r98NRgvOOtebWud6U+tcErZmG+yRY9RuMf1eSWCPnAzmyMlgjZxMjZG5BFPVblOH'
        b'eOyYmeyQDd9nNskHwqc0JMkcGBdRv7PPEC/COXCIedUA6PbdtxD+iPbNHxLAcylLswRmVKudQzXOoVrnUDCtTQBr2xcEkFMYSW/IESJIw3UZM8QTOI+HShlvAJ6DB072'
        b'zgFg42w9GMM6l8Cxk/VQyDqDZzJ9IOQ5R4N1vC6w44H1tCGwE8DVSIET6yyBXHTBC7JiASLPSiDkQxGtBA4svGsInpcOXKHpA6GeZVYDJ4tMhc6TiIA5QuD2v4m1dSYS'
        b'5UiBB+ucChQMC4TPiQAJdXhAIiLhalggNK8ek4qyAW68QmBENdyMHjEK0ECiRt/oAn6DsfPhKYPSrOOQ/50Hqo/mdt/U4Si/VVArkPF22unQCPk7GZmgx8YqGqGQxNkO'
        b'i7M1QSq0jLMzQSq0jLM3QSq0jHMwQSq0jHM0QSq0jHMyQSq0jHM2QSq0jHOhcWNInGhYHIdB6EPifIfFudE4PxInHhbH4Qz6k7iAYXEczmAgiQsaFudJ44JJXMiwOA45'
        b'MJTEhQ2L8zZBFbSMG0PjxpK4yGFxIhoXReIkw+J8aFw0iYsZFudL42JJXNywOD8aF0/iEobFiWlcIolLGhbnT+PGkbjkYXEBNG48iUsZFsfZy0+g9vITwV5eNomEIbLJ'
        b'YCsvS6XS/pQBV3AnV2b00/sFyAHDbNYtEumAFi2SgbkUtd2qrmoEKXNpjc5AuKWeasHqLawoBp/edBiMrDh10xpzxVidOq65URUcJZg4Fa4EmbaK84gna6pWwraxIWez'
        b'3Jrk+gzrWzjFDe5VvXZrZnpxWZYuh8oR7JrNbvJrdRZiVcFLqZoJyY5TSjZ1ehzLfVJfVp1dfou8Bhhill+VgroBAOKo3dZqklNVQ0OwEnYuGtaBFG/mTdnsZbO1Fext'
        b'wHLxTxvJIuGoAJYtcgdYuhjNzPfYKdkXLWFaTBYlI+n5WCxq+DJmI7/CiP0JdwKzOxuzO6HZna3ZnZ3Znb3Znd5zBzNcOZ3EOpqldTK7cza7czHc8cmdq1mcm9mdu9md'
        b'h9mdp9mdl9mdt9ndGLM7kdmdj9mdr9mdn9md2OzO3+wuwOwu0OwuyHBHlpAVwYY7ltyFmKUM1d9t5KnCGCv/zHmexSxuoRt9gk02GwWqcGtvyGzM24pCKCNp6emqoDFk'
        b'xLeE5m/JnchbzPII/f1JdqPgJHuKv0nQUmx8iyyQLbZBFR4tJSa52pIvW3Hs0DLLPI+NNuZYtiyzT0lanP1G/nJDy9ljgVWr4BWAdhqfjq52Uvklkv+zFG5YHDaIPn+Y'
        b'pEoROQNsxQCvouJZhOXby6rAyNVoJ0u9B0gkA06zyRqqfqXOHYCQU9fnkLP5FfWyAZsKZU2LHIB/OLdUA64VS6saV1QYvIHKoXblgMklvwmBAgIKWwO+hwdczJ3qDthW'
        b'cHYZJMdmpby5SVFDPkEXxrZUobGlakBYsVJRRz+9Ahy02lTUcH+ou1Zn/WsVYKNAXqpeBjYFFJW+qkWpIKtzeQ1o5lU1AG5WY20ToZgytL62vpo6PCELcm4KMURXrWwx'
        b'FmjAq6Khqbqqwdz7PaGXLPLldWR9L6ygQzjJhv6t4PjiX2HB8ooKGJ51aW3I9UrFgAMhUt6iADcudGthwJbUC9TJgEu6vma4mrBV1LRAhMSBs0qCoWFAuGINIUFhAlFg'
        b'ZWeFWz7DoMeN9sZlM9TqepEFmXSDdk1FxeewxfJbVq81AYeclWxniyq9a406fro6CH6pNdkSjV+F1q9C7VXxmSjg9c2HN6uquZP5dgGoaQs67AxodRwgXWQMQC2EGxDt'
        b'gs0Q7YygdWfsz9ubwdvp/waFkcdO/cGhNFb3ou5hYCh12qB7aP4nQgLvh+qT6v5QgDsXfRo9ceFR8DfEcB+bCH8lOvoGA8PoZ8IjuFT61GGSi1PPTj0z/TwshdwTaHCo'
        b'sD2rM4Kw4nTaibTuZI04QStOANTB6f1Boaqy4+sBYbDfN+B00Imgbi+Nb7zWl3q/5vbs+6PjemK7Y+8L7gvUQdM6BZ+JQ1XjSTKDk+zF7GeBseq4MvXchZq4hZrARdrA'
        b'RWqfRZ95iTuzVOHdNhqveK0XnJeR335RSPt6Vfj52F6hRjRRK5qodqO/oomgF+M4Sq8WP2RH9hbhY9m69B4WPPhmoBAGUKqpZdQQq3GF0b9wLAcL0dKk8+sMRvoyImjV'
        b'164j4pOJWPPK7i7orvCbzCjI9+YzppBwY82x9MCwaWVTi9HfNMWzfnU0uJ7RkOYDpBmdYptD6A2nDDC2XxXcS35jNISJrfDMFEbPgjIdJvb3iaA3ImmBQJrRQaXECoLe'
        b'/5o6ejjy7mioCzGn7t/Tgzk8dYVyqc4NGHUgBCTpTB11MGnPJZ2uzLiMqOUALKSayWuwCKI4SVaA1+KDS43Pautr4IO6VQnJnSQwGkIaJAtFcLSOldGx5LK+hf7V4+VF'
        b'U536aA6GLvqVa1s9Gn5GAT/7DPwcPxyHZoS+kp4xNz2BBNmv3JUJjT8azTAZY07qVDMX/IDjUrPU3Bm/JcmZs7OzErKyM8peuZMTWj8YDcnxfFOHQIv0A/ts2txMJFCd'
        b'Pa7efZGFoWh8cBbFpuHMYhvWVK1T6PzJBzfW1FXBacqrFEinLPXj0RRonHn3i9Z3P709rEmZdLJocFTpnLkLRsPxD0dDYIr5wBpJp9CmphWw6ud868uDq5qbm8BLIFkg'
        b'KDlv/KNg30ejoW4SUPdn/cn5M9cyg++0V6VCx6OPR0PFFKAilDUb4VeSAauqrsak9zQvW6cA4+vgmen5UjLANbwyly6x8p+Mhr7pVurQSFdDU505WcFRhbOzc0bTwj4Z'
        b'DXXp5tRx5uuNsriWpjjyxyiqBUdlvypZOqb9dDRkZZmTFWAVniI4qng0NBFi1KOhKddcsDUg24ZwJv9kCdgIrr10AwUHUTKzfPbM0RCoGQ2BBeb90YNOKXTRrHNk9qpz'
        b'G6k97WgIKTavvWjLCQJW42DbCNdRGSUlhfnS3LLsea82k+km338bDYEzgcD/MHDqD5YEmm8jxAfnkHE2t4aQ3EhXMArDFi83X+h8HkChoF9Hlc7NzynLLMnKjg3OnZMZ'
        b'Gzxzdn5xurSkLD02GIpZmD1fEkvND3OgHS/T5TlSblklxWRw4LLLSS/OL5rPXZeWZ5jels1Ol5amZ5bll9C05At023lNvQJcTDQ3VAHmG4er8urt8eej4fIc8w4Tr+8w'
        b'oSbzLLc/w/WWKjrgVClIFq9OYd9oKJxv3mMmWLYDbqcpPjjd6JExX5pTQmo0S5oLky803lEQ+7PRELsIiB1rIFZURoVCbgeMNBoZtNamV+rjOjjngdFQU2Ex7eqAeKi/'
        b'U46WGuMZiOlS/pWho+RPRkPfUvMuHsBxSz9zgK+YYDjbsSIKGNS7gDrOxMRIlaLJzNbZxUzJ1cw0tFloGkedNvI2sqYqWuTacApivqO8kalgTFIZTkfk7qZ3pnRVWH2q'
        b'MpykmP4jKQxnKuZ73ayV9vpsymzO6wucQxlkeW4VYjwRs75KiZfYyX8AdfAPIB6QHExAHOjWMYA1yFmoYD632UkT0Y1N4IbBpMaxrqZFvzO9XmxZ6SaRNeQ1BZwffLeV'
        b'AfvDTaB0nseCgvkktXhat1ePb2/W7Tx11DS1uOCx1/u+7Vn94TGq3O6s3vDbkvtlDxdpwgu04QUGYGfYikvrT0q5HdAp6HLW+sT3e/l0FD/xSu7zSu7N0o7P0Xjlar1y'
        b'1V65ZjjQ1ps5rJ7AolhnGFbGGTgOb9ugxDW8bevt3ppgYIU3dWZvz9GjnMdY9iu510iq3+anN+bK3HXWNS8lPPkvyLMBAeyAW7F5ttPtjVdYKwwXI4cKi+YK4ynSeobD'
        b'hnQCqa8n4tg+cSy3H6r2iv9MJO7MOLS2Y22763MYrDe2MSmvk+ndcpMS0GoA02d6GqMvig1tRtbttxtqGklRrGys04g1UJJAi5IkU8v8WK14nNprXL/Ip30VpV4qCbOm'
        b'ckh37qmS4ICLxekL7Ri0Hxm7EJSb9p4BZ/PDF6Hu7MVWJ47KwZR3QKg7d7Hhjl0E9NRFAIcuFFtnwMnsxEWoO3AR0MMTF4ujFUfTkxWh7kjGzngiw52GuJifuMiDeLrG'
        b'LQ+Hq0getYcYUTXQHBVT/gB6haViggaOM76xgE8R2oNaIARj4p39h5gXBzKWCRzbaYAEmT1kwwssA1U+Ej6lYavUAsZkKsCPTAf0kekAPjL91YFQrOZgimmRBpgW6RR1'
        b'JJ2ijqRzKCjGNEM8gXfCkI1QlPgtQ4KnEJAkLibIIf1eBQAbUkRhQ4oobEgRwIYIzdJAiQNoiQNoiUlI03BAKWC2P8RjvScP2fDHpH7LkOApBK05Q3ZmFM8AijMoxRmU'
        b'4gxT3Bau2NOg2GlQ7DQodhottvE7/V4RAMgSCXgskQDHEknRWEw1LYEv3pQv3pQvJKSali/8immCCZBgEiSYBAkmDUuQDAlSIEEKJEihCfzDOw0ANAA54g+QI/4AOeI/'
        b'ubXIoiBRUJBoKEg0FCSaFsT0E8AuL8ouL8ouEtKvGNviEI/vPYsdsrEJBI1QCJ/SkDRHJ0Yc1klaGzgD6veaRLISk6ohwVMIWgstiCkCYqQU5kZKYW6kHMyNqXpqHKin'
        b'JoB6agKopyZQ9dSX4bxp5wG+BQLfAoFvgSmE1BGBcrxY6IGGQMgHdBpD4MB39oUry4DT7QN9hOXOaY6rnZudJAV4X4y0KB7vmYvO4n34IJ+JXmaDehd4min56ac0DuST'
        b'b6rkt5NZwOcxNaDgZzHZLbChz/nDngvpc8Gw57YyG5KbXSuvlpUJd9otsJfZknsHgASp5cnsyBNHGmdPrpxA5W+Bs8yRTkZOA54W41tRvaLFDKeUp5/rZnBzHWsmLfLI'
        b'nYEQMAmoMMigdSBXmmjh6CVsAd3YGrCvkCl1iuz2YGdW1VDfsm4g1PK0G+ipMFW2UuhtouN5VKNdn4mdPg+9dXSwCYKAv5VcDXACW2EijeAmUt3pbYiEnuXq/oylp7Jh'
        b'avr7qoeb9JwLuDjSmsIqbQbMe1hXrGUYK+ZCL7X0mzraD++GD28YxYd124PTRvvh1pE/bBAzY+mHX840Sk8STx4GMsB063SBfDBiK6GC416+zrJoKwOyYZbWP0EjStSK'
        b'YDr7PiyLdHyj9I1gW0QFmGHLER2VVCbcz9fZ1xvNn4g4qxElaEUwhbzcUmHZC5cKIzCKWy60QwWG8PQVaOoBzGB2Z2IuasVwVmGuE8ha8bplHHNMKl4HsyMm8aarZL5F'
        b'vCM1ARWYP5W7thg09qzpIZI3DKtblYnvMOM/S9N6lhvzqMu2ONNtnpWAz7DUCLgRacHNSPPksqYaDkeA8yNGoZr0TmSp2EtWvQBIRAdEKnnL0+BqBgTUngraFJHRm5tr'
        b'GmV6B2KOJp/gko5oF8yvksmGrUJolZOII3wTo1SqFhLTvUUjStOKwHjCvZz9zC9MHV6q8SvT+pWpvcr6PQO1nmGqlvPr+jwT1Z6J/eKxWnEMWBD2iaeqxVP7xRBJbsar'
        b'xeOpJVaZxq9c61eu9irvd/Miw/ATt+g+t+juKRq3iVo3veaJ28Tn9EFQTjT2Qas9z8z1z7B+Nxb6na81DtDVWxdfh79o7HWH1nWsU7sFP8fydAJjOYaBTLCRybJYGFsx'
        b'juRJrZczimYJ8+5iF/BGZ20deoi3zxVW0/oCR0PV6xziAJ8G2BZTzw9yWGCuj7NW9JamlqoGMmyDTptiOrkAyaFpZfN0wJtSQF5bGbV4MvfbvaozvSuvS2p4QDkjYQf4'
        b'CuVKK6tfG5q7dZ7TqNN8nTkqDMd+XJ69WSTQiCdrSShK1YpS1W6puuWvi+Xy12geR7uNsccYVorcwrGIp6t/+Wwe3TayWDMC8w0rxlRoJ9Ykqk1A7S+YYcZkEjC40QVO'
        b'VFJX+yeTX43neK3n+NasfrLWWasOnkJ+NaKpWtHU1jwrj4YErHMSCLS6QMg6J8LVsEBoIf3agiHOSIEH6xwC6YYFJJcpcGUZcFKyhAQT0spMpGR0Dj8ASRnEZHwL74mN'
        b'Z5ksfNW2KN7cIkavl/wnaJNH/UyFZfLDoz/8LpsFfIA2kwlltjI7mb3MQeYoc5I5kysXmavMTebe5bJA0MprtSGirwcReG2IGGzTagdIhK0erb61toAjSEVpW4oWaC5K'
        b'29Hn3jsZ2ZgekRWrGFudtYllnAON46xNLOMcaRxnbWIZ50TjOGsTyzhnGsdZm1jGudA4ztrEMs6VK28tXxZOSupGUybUk9Gvxs18aDnPHmAXuJHUHjp0QnfCNZZiE3rQ'
        b'K0Am9LTncCT51C27EICBWh0ptqML4akb5apnq1erd+uYVlGrT623TLLTHqxhOmw7xvREW4DMJcHXSC3wZbHDECm96Tt2PXHD3yG0xA9LP0YWQ4fDcQNO0OX0dhMD7MwB'
        b'tkRiM8DLzRjg5WcP8LJLyd+yAV5m3gA/I1c6wM8qLBzg52bMHODnl5KrvNkkyMzLGeBLS8jVzCKSZHYJCUqzIWJBoRzwUsgb+TMlLgO8jNwBXlahfC7Mqrx8knfe7AFe'
        b'Uf4AT1oywJtZNMCbTf6WZssX0gSZC0iCckJM/rB5gJpHbGVAFALP97uJQEQ93zNktSagfu/5VvzeC+yteLInTwTDfNvzNwt0fu+txpliL0mHLVvpjGLiHV0gVRYwACiC'
        b'tqNz0Ltb8J6SeLy/GO8XzImZlScl3bsNHJbjVtLp4/NJgPcUxeYXz8ojXb4AHGajSwJmOt7uim7j0/hGfeRhBZ+6mHVunnvyw5Al406dOXLpyJmOM63v7jzEusz2eZ1d'
        b'd+WL0OJ9EUV2n9rkNQi+lmX8m+fHjz/lMSk99u/d/x8Jn8K0T8RH0SNHdCl2Bj6Wp3dG7Y4f8NHViegMh6ayrawUt5XgvbhjKiEFsEJO8tbinejkU6gE1I0P4AOoDR3E'
        b'Bwvj0EF00JZxHOMUwMO78WtoH1lxWtsuhCq0UIL2Mm2Ieg1o6JmKcYwOkD2A8RJ1xqo9x5JfKhuVaPxmav1mqr1mWug96z2ScVO1rVFfW/4rmJmsOF6mxu86sPEXUXUT'
        b'pqQ1DAczTgirCmDZIHCj/ILge0MPhxVHp308c81lKr/aYGdD/rnoW98b0DVsua6xm79bsNtmt3C3LekkDqSTCMgYZNNqS8YlbiQSUqxYt1oX2nHIOL7H0aLj2NOOYzes'
        b'49gP6xx2m+11HcdqnClghHnHMaCqmXScIKkyhdyF4q6awiIdFPCsjTm4NS4uflZeQTluLSmNIq03r3zmGrQzD3XzGXyg2RG3L8PdyqnkTQ90Bt8wvkq6U0ncHB04QAHe'
        b'TybWg4Vzo/CeuXakVwoYdHMMegtdd3RGN7GK4hSMDxAyTgzjNjR2TdGpxjyG4kOhAwK+wlmHUoCuO+Or6BbaQ9PHLrdjSHNKdItc2/COIJxRguv4enx3oikElhGxgKIV'
        b'2DLzS23RW6vWydAxJVgRBYzFbxTmFxfG4v0SfDGKZRylPHyhwpHiVxXL0ZmYPMA1wEeSExNblGhnZSETiu7w0aN1M5TglQ6fa8A9MVLwUL+/uNwIiIAOoH2zouLjonBr'
        b'QnR+Mcs0SezwLacy+tEGAb5QiNvyixKEjBAkDhHPBT1Ax2kXoilQqyNhIrA7jiRBx+3RA94EtE2mhJ60eXF0DFcTtgxuQ2/YreI54KNZtP5yo9GhUh0mQ1T8LHRHT8Gs'
        b'KHwwFu+ZGWWg1ZZBXeiIw9zEdCXYYeHjaGtgKT6D9xAqopgo/Dq6Qj8nwG+i/YrV+KaAYdFxBu3Mxwc34jeVM0jcmk2rCLf3x8aTkWlfIT6UObeZJCyLIvXdFhtbXJ6H'
        b'D5TosSOKDADT+DzfCR9Ed/B1CmtW5xZfyEVJ8N4itLOAlNkzl49PpW6mlspoux9qN/K4mWEcC3noWGKEEk7I8BFHdKEUsM0ILy6VGXk+i34WnSNNv8TNtjmwiCvmDv8Z'
        b'6B5+HR8BA6b1TDHaWagMgYiH6FwpEfxurFmNb6M9a/BNdKOwRcg4i3noOFbhy5S/0bgzUoFvtpCWHTsnCp+zLYgjTYdMHNzXjNwlZUBH8H0HBneUK2EVhd7CZ/HtGOAM'
        b'YVZbAj5YGhVFpoHWBCk6gg7oWMU1UrQVXbJn8En8hpLCaB2vxVsd8V18W4HvrUL716xBbXKnVfguw4iS+WhnDu5V0gniykRn3EZafnFcfF4RPon2S21IvzzKR9fQVbSb'
        b'9po/2Amg/wfPDN0Yu7ZxC0OZko1ahfikh2IVWVPjgwzai65V10e9/gueAnSuPol1OdoxrQkluu363c4ZH+d6PLJX/3TPnerdf9/7963xxy4LL13lLe1Gs+/gG3MD3GaP'
        b'HfN3mevlRb8anPPebPW0b//6+00rdyd8ddLX6beV6fUrEu/ir9Z8/IvJdePDPw/93dc/mWIb88nHF6vbfnrA7sq849E/nOWddHKruPPHJ++fv2I/Z0Z5+JH/vPjFxRTF'
        b'g7m8v42f0X3qfMq0p53KGe9/yXuwcO/vx7VOXKQ8/8vjn21rf/M3Zzb0z4j0XlCan/JIXp8wf/VfWk67f/TXFgetouwHhYHfdiWzBz6Z//6fvWvKf14WUMh/2P/zLy9P'
        b'efDHx233ey4eGDP1G8kCv8Grb7U8fq9iTXXAH1bH3j4xNSX5my+mz/H88LPHtVUXr/7il8cP+f7y7xsyxqaeiPpswDYh4NP9e/9rxYPAQ5f+Mu9PxZLrJX8JrX4vI2jK'
        b'kx8fWb9r0998twccePyG68+KtBev+W+9ulDyt8yfipf98ID03vqb205mZf+eve+6xCNt7nnknrv8QvjuzasXty11vVS8swJl7p76u+S3Hf4cdas9aJGm5Ndbf3Vkk0vU'
        b'3fYPHMoOfV2m2jc+9J2w80k/+TSvLuts5ed/Ct888LPsjIMbHhTZ/SMiZqbjNY/N395a898HE1b2/NLraO+zlJqbG8ZO38w4uakGEoMkYVSewO+koR0gkXDiCNqBDhtE'
        b'khB8gmKVLIxaT3oyOpAgjcvDvYEAA3Kdh9+sW8lJJBfwhXgDvAbah9o4iA2A11iMDlIIjhoitnSitjUuzg5oK74hx3cU+G6Ls5DxWsUvTUJ7KYIHvjwT9eqh0/Ab+EE6'
        b'6vKlKCfTYr1wWxFZofEZPn6EDyey6GRFCUVkY/FFBOMMkekkuDUPH5UCedd4+Bza5Uqp34SPbEZtrqvx3WZ8R+nss0HIOIp4yxoVHKjaJfKlh3qMFnwmFp3gxaGHRNqi'
        b'mHQ7lqILREKMjZbEk7HlWCUZPRnGJ1iwJKXwKewp++OjroXxxUKGt47dJJ2KXs/nMPguOClJF99L3iE0Cybja/g4i26gHnSOFrUOvdVQSMY58t4SFl1EbQm+JIbCR17D'
        b'O8YqVjutUuJ7rmgv7k1C+1ztnB1wr+tq0unx3TWrCNuKBUIylBzwo1ArLfgK3hUTh/cXJbGMcC4+OZ/FPYulHALNOfwuOoHb8tBVIkBsYtEFJmfi8qdwPrQ+GvUiImi2'
        b'oZ480tlPFyMyO8cXFPMZP3RHsKYEv0sZzJ+E7kKyA2TqJpWAH60hAucMHj6G76LLXGFv+0cAnotuzEn1KSIjzpgigbNXKKXBYQp+QEoIbcyGEQaGVvJC8Y1plL94hxhy'
        b'T9CNmESgsGEcS3j4qALdeQr70WTI2of3Q+6k/ZWA/FCMry+LIxI64V0QflOAb8XgO5TQUnR5mS4hbaid6DUB40KyzEpCVzm8ml34Thn5GrCKcIrJzOeJ8F5X2kIh/UN4'
        b'nRRBhs5Li0pIszpIkvnhLsGqpmgO/u8cfiggzNDPYmTufMQyLqX8Yrw9hQr4+DTpKiRFfBwRfQpRB3rIJ81xLw9fxDdwLxXwk8lXdpMkBbH5RJwhq4x9dpN4S8l0s/Up'
        b'nOyQSrm+Uh+NWktW4h7uY/mkgUZH2eBtm3AnJdkR368jCaWxaE9CVNw0rKLziA1hyz0bm0J8ivbOQvfllBwqAOFuvAughjzQNT5M2XjXU5iVlm4Mgg7CrZOIKHaIWyvF'
        b'oD3oYILx+BA2RWLIjLY/zAGdTol+CmijZH65hS8Z3zZ9k3St1iIym7sImSLGFt30x8eeUnHpoQthBkyAB8m6qwSqvhd1FpPSHkgoJIPQAe6QMhfdsEUH6/Bl2lrRCXST'
        b'5VoK4t7pxO+Sd4TMGDImvFuD9v/TXTHpLUktXTHRYztvi4ULd15H11OVnArGUEMA4xPavl4V2T2Rc7cFu8753K6zEdt7UBQIroY5V2uQIo+le8s5Gr9crR9oUw2KYHnj'
        b'XsxSGPGEJ0HJfUHJvbm3ix57PA557KEdn/W4RhNUpA0qGj3C+KAoALzZF5BvRHan9AUlqgOlvbLbKx/naydI1YHV6tnV7bng6X7xk4D4voD47jU9G+9n3J91P0ObkPZY'
        b'pAnI1wbkt+cM+gZ0BTzxje7zje6eoPEdp/Ud1y7sh7xZ90KuXDMeT9CYujALiji9/sT67sjecZqgCdqgCe1OgyLx6+sPrz+0sWNju6DfU9S5WlXXtUXtGU9+SRad0erS'
        b'ubrf+RW634hKjV+V1q9K7VU16On7xDO8zzNcVa7xjNF6gqsg9yKWMKyQu6JkFGj8CrV+hWqvwkH/0NMFJwpUGzT+yVr/5Hb7fk9/4EUWqxKd9+9e2r2qe6k2JOm+rzok'
        b'g/xSCvojYlRzVHO6y67Pvzy/d50mLl0bl66OSx/is2MzAT9EnAX4ISQEpTkSkpkvSBXLlaF3ze0NXFHUEVmPV2siijV+Uq2fVO0lHfQMBBpnsqop/zahSB0GvzquTdFE'
        b'SDV+JVq/ErVXyaBniGqR2jOJ/JKso2Ivrj+7/szG8xu1kROfRE7ri5ymiUzTRqa1Z2m9wtVe4YORMfRyMCiC2gOHRnWLtaEp5NrVYFvMxeitfHU2ygEhpxecWHB8Udci'
        b'migs8nzq+elPwib2hU3UhE3Whk2G1MH9wZE0tS4PneHw2EjOlDk8gcvSEmRef3bdHxTCETVWFa5SEqrVkVWPc98vepK1sC9roXpRpSarSptVpQldqg1dCiS3u+oU37jd'
        b'B3ed+z29tb4ATq7kZRA/Eba5HKurWgyG90JF9bKalTUviw9lMiJA16/U/TOMCy8cEO7BVsZjhtvK+E63n7EigGWpQ69/Qfh97YlQpKyL9tOYd1zSHfmvrFoNzgoo50c6'
        b'eDdnn/7E/TsztfRXtUQ9/5yDfuvfe2auBh8FutIGtzlcAYJ1GEjBUfKaKllcU2PDOskrW2VzFkEDjhU6+6yKetmrEfo3c4uCuK06imOtGX3VK4yFMKX61Y1gfvAcBXTr'
        b'hMJusollYWAZNfUCQy+D/eboKOKUEsAbhrKlqbb21ajiC8zqOYEaCClb4khGweAaxGiUBpRSW/3/BZly31duiEIg0GhUEE2NCuprdVYEK8FIhNRqTSO4QpKNljZOEWfA'
        b'qcJkhHw1Mu2BTA+9QgVnAAYGD3WA0WqwFB19k5NHvHKDcwKSjMYhkeYgr3rsM84ozZQwE7qMJ+Gg3gS6cTqXd3y6gQuH9RbYvptYuoHLDNvAZYdt0jKbWd0GrtW4kTdw'
        b'rZ18CKXWT/BXA93sbpKMujgDqsHswuJkZhPP3godw5GLCWXsZp6OaqtxZjjFStYKTjH801nG1FAnYOb2EYpgxbImZYMMlE/IAFtfWw8W+XVVYFVhNa8Wnc+14MyGmiqw'
        b'5QrOol6BoOE1yUEphbP+h2m4nvRhzmypXmE1M0UNBU2urCyTK2vI9F7P9f7oFU2NLU1k1K9eER3cUL9UXkUyB2u31VX1DdDzrGYGxlstw0Y58ppeMZ0DMuas6NaZGKdZ'
        b'zY2zrzMQmFPVoCAUDocQhn9mzcXQuUyaC19an7sriKeAZek/fiA6+eEC+0mnzhwJaWOF230n/Ywdu5f3H1cHJSxdbpI13aPZJiswtC0pz7gAW5tIuqWbvlvq1HEEtXU1'
        b'LevDzfqlorqhgrLQqI8BqehKCY5T6EopmPEP7kpTe5meKul0Kc2FNHqyVak3hpE/Bq2Gl/qeG3lRUcvokMcXB7OsBwhIlsH3eoR0xF7CXHKZyLeO0LAZ+ihfhytuQw+J'
        b'WN3ZKiApWJyL/hMwxete8mwVIGE2NaB7Zkt40hLgoGdPUXRBLLpcxh0+wIOSIjj5QFfQHkd39OZkdAdfqe90iRUo0kg2OXMDTn4Ih6lv5fUcSSLNbu9fCzu/8N/l9cOa'
        b'fU5OV3yr/mdszthdUlVgmUZ6Ye3Y+y67Kmc+E34yholc6Gj7j3oJn25C8LAKvWtJjX4zwQs9Mt1PwHfKnsJ2+izU6eUYjfdzGMX6o9ggdAvtw9cE+Pp61Mbtbt5rTDbd'
        b'dshYbGzzW9CdlzlvJd1A8VLdQKHrBlN13UAezPjAUtm7iFWVayOmcZefBUarYwo0gYXawEK1T2H/2GiVrDvlzIrzK9qzOkrayY/ZUSztNO7PW97ojmKNfsjlP3q5bkTo'
        b'9YNutJrRA+GuIv3IFzrOC4LvDf42EgrJo0dUtfgqvoH34+uFdA9Z4Aobq6pJ3FHartmkdfSirsIYKcQls6SiD6H79Z2JU1gFnOlkVC86+eHUU9uOnNkh2Z/02o3Xzo35'
        b'4LeVv6/Mr5ZW8Ur/548+K3yW+5R2fpVok9xMho0nofbaE6s4Hr/ATMfUv7uBi+vHWOcurf9Srv77BXZDC4Lt3GOGGCuBF9993BDz3MCOCYnolqlFyWqja3c9ySM2BnOS'
        b'5R9AUxiBWFeo/CZdY11Iqt4eKnfk4Hur9e3MSKqKVEDjUUFHQEQd3r9Q1Nn5MsMnmXHviF6zUcDe9qreGyc/HH9q254zR87Qwe9Y0rjEntqd38LcyzR9mnVGgNU+ZPYF'
        b'xZMmdHKayTbrdHT2xXu05KdbwjOpWx4dlkwUtC3VLahmNm2DvrpqnRHC+IitKmfrW5KVWdnYkkz0O0b+YAi0oxWMbi7eMtJc/L1OyM9pQ/+fCcvDlJusyWwCaVn9vbMZ'
        b'NgrgNpv1s5MfTjoV8lpSuaxzW7Iz4/KIV55ko9eIt5DHOI14y40pThWeVrqjrtJzSKX766xnX174ek7u4WbSVnbIP7tyAVvl/3rlGkgyHx5aP4+wUcBJoN+es1C3Z0DB'
        b'LNX35uBDmyKneY/HBS/ZH6oeZMuv7/ovu9rBIj4T0i88rVpIRCE60V3F74Titlg4LMJXUwQzWCJwPUR3n8Ic1+CaZxxCmtH2lzjm4W2hZ1bOrnhvDD3iBZUGFT5nh9/m'
        b'oUNF+KCVVkYNVIZtf1LLFNrKwrhW9uciaGXUOuWJ/4Q+/wkcmJM5FNLLt77nfDXSrPUV/ktanxwEfjNdMX99fT+AJuhtVVcMtFVdqEd9vb6qsNWTarMatFZbfVv9Wm1b'
        b'xa18skDwbw1oDaz1N+iROf/T9ciGLRKs6ZFNlVKNkka0l+FUnCQOQkYo4rl4TuPUm6hkvR2fy3eU4zv4jivos+CbVZNbhIwbOs/DD5Ytpvpk6AS+j9+gujZ5pPWVoJ7Y'
        b'OVHWtW3wVXSCatzgXWsd0Z0JPhKhkmoV7EI7QhR4Tw1oyjC4nUH7JspojHtDLL6FOlCnUggHtww6hLfWUMJDfL0d8dVEfBdUYe4w6MwqfI1THGovz1IsdQFTCNwK58kn'
        b'8QGaV/T8OEe8D7VDo8TXGdSJL+GdVCzFF9FROM/eh94FgGB8mEF7HfFWqoeztFro8yVL+m1wZcOexRsYTrML3Sdv3ML7luMbkNs5Bh2bhLjvS/DpGkXRCmNR8FvrqEpS'
        b'XiU6S9kUVRCKuswYhHtb5Ph2aV4MqCNwOkntqNN+U044R98x/I5bMjqwALcnJwoYljACb23xVsIQ1IC3bzFTpNNDRcxag/bMnIuPJheU2jLluFOI7wQuUcK2XRjh4sVk'
        b'cpHEFOOzSXjHOPoYH5tnj8EAJ4FBpzckpKGLDd/94x//mLnMZulaUOCbURnr657JKLOg0o9msoX6L6HbeCdZR+bFwupyf0JBeRTeQ8gojZLgg3Pz8ovhtLiYNA10dzYU'
        b'TdjovBgfxW3KTJJRIBnMToOmr2lCaEjk+Z6EEh1/8uLj0IEVBgVBaEFX0NtO+CZ+F/UoAXFJXr7GmbxyyBltTUxFJ+xs8NZy/IYQHyhzzvHws5s6G72N3sFv4OvZdWvt'
        b'a0WrHPBD4Ro7tNe+xAn14h34fCJ+Z4MkCLdOiccnhOj1TAm6NX08Pu6DOpvxcSUcTSWhm/iIDb66AW/D25yZJDs+6i1HNxfgo0K0B+9GR6PRTvwOPogOlInrN6NuvFWM'
        b'3lkeKkb3SMN6Dd2t3YB38pOiCBH7g/CNLM9i1OVLhyDazsIb/cLu8pYJGLfKTT717oxyMrD53YUluK0Y9czErfmk8Al4z0yq4KlTSCvPQ1fzpMXFdPl+DZ/Bd/E9x+pi'
        b'1Eaz/PO8fDs/NpglC8fon5bJGCW4C8cX0MNJNqQIx+2ZYCdyMWfJCnQY9eAH+AybRDr8m1OSxbmkRo5UkmmpB58oj8TnFhCit3qXoe01qLUOq/B922Xoodu6CHSVtuyG'
        b'XPJhK2TmxRXYeHiDpja6JMGXpCQkPQtfscf3PAPKJCwdY/DdghnQAMgEhw/kx5KRYg6+RmpYZCdInIKucGPMI/xaQmFcQXFpHt1ByAddz5g5VDfc0O4P5MUWVKLzRfH5'
        b'cdGkgeyVONWjHnRWCbrSuE00x6pKn1GdD10IMGj0oVMbCHXQm91Ki0CjkWV4m1AnOsBm8vFeZTaJ8MK3p8TgM/55hHX7YIomPSChID9uNqd8q9fsNCo5ostlzdD7Z86O'
        b'm8Nj1pW5rhMFKMuhcJfJQLSN06zMn6XTxNVt1+QVldCixs+yW43vzsorKJbGxkmpki/0NdzRoFPpnAt5k1Lvm+2O3sStEbQBTBPwNr7Lg6vKon2NIUTc5PQ0b+Aj+GIh'
        b'p//CZ+wal+NeHmpdUqKcCQM/utVUWiIpRvtL8mPzy+fqNIvxm/GmysUMafKX0VZSt4fxvkXB6AoZEc/nhaB380KS0XUBQ7rmNg90HG3PUQYD/6+Wkk52C99ytbdDPZPx'
        b'TVd8q2WVkmW8FPwSfGcGHebigtDR0hw7GLL4ZJDrYXAPuovu02EOn0C3wwolcXT/SkroiqLSEH4NnTZIRHxmcbAd2i7FJ2h20km5pWh/Gd5fTnqHTcWqaJZMVXf8uc2G'
        b'6wK01XG1C8uwZDC8jY/BgKLCh+lE4buKsLAN30G7ikj8JAYfGItvKKmuWTu6jk5Q5WlS7lZOS9ZxAQ9fC6yi+a7FZ+PJq0fHGzThWHQSX8ujbWmuCO/VaZRJcMcSNgGp'
        b'nOkHV6I7dritIhu0s2wYQSBLJoooqnJrNxn0RKFl8PH5GAm6LGCc3Pje6AQ6qgRNpHh83TEGVKJhhyw2n0w2V0EnistoLNpqUxuC2jnS38Sn0E3DmA02CzticCcPHRWt'
        b'oK2ieBk6EAO9Yj+ZbqiSklMd39UTqSgz09AZfL8QPUJdpFEQGgUsOo07FnHt6XAwaVJtcVJ8sAjfR20sI1zM80YPpJQlZGTcjnaQ/n1RQDXXBBNYdAmrqmnJFUjlUuiF'
        b'jsTRGFLwcxJ0hH5wxaSN5J1u1M1FTWdJE9uHu2hrqvHE22L0Orn7S6AH2zAh+F4BOmJjvwBtpS3GE10MwW2rQ0gjl5Jpf0+CCZsMLJKibba4fS46SJXYJwQvAkVCCRl9'
        b'7Avw6ck89Ca6lMI1mK1Z+By+VY8fgXLvLVuGh6+ycWPG1/8mZAtfEU5mzb+U/Hj/nMKmgRluS9IS/3N/iI+nnX1S/rO8Z0U/y7n8LPLyL9cvCvlB3hxZqIvmmcel3V+o'
        b'C8v+/FtP0R/DprDffBMv9i789JuPP5mY/Dm52bJ+i70T//DmPTleQf/WPf2J/fyvL40dO9N1XD3qfu+DjqzfnZy6e5zm1vGCe2NCFE8ffRD6i/rxohXLjhSmbDtaZX9n'
        b'829OfTy3p/rhV3OdLyRXN0z95Jxjd+SiMSWf+/9jzHGv4x9X+v3nL+pSf3Lw9UWhbb7aJT+JdN5WuM03Wjj4teDD21G//dEVu7O7PSZFu7am8SJ7b8W+9udf1p9XLc34'
        b'6Gx5Q59D8qGPOo7nz9rT3Wq34MvLr2P/Z7GR8+dVl7539odFyoDts6O/eNj1SdLF0mOF0f/e2/7g4if/vfGCfMMgTvrm4Pnf73s0bRxvyw7N5czlGf51O9r+4TntBz//'
        b'ODehuHbPf3m6f9auqeLPcp68uoOfdneZ4j93p6784Zhb2hT3DeMv/f3zsXcff/7DJ4eLF36y4tJnPdpP1v8h+1rcD1yefvls5tw9K5vKPl34h8P3vH/57+8n/HXt7T/1'
        b'xvz+kfz1t8XfSbWvfVL8jx/XXs5/55c7Dtx8sjt92tGzV+KaTgb9zybfxRkTV5VF/dLh1+P7/orf+GBV6BtHpx8s/dL/7mBw/eXQvk2aOWGDOV9++an8TOSpK2N+u+a9'
        b'd37+NVt770jNRLff1Tb2L9kw6fDUjplb7K5pX/v9wIOIH/En1l+6eWz9vzu/vcJ1yuxTyyfW+T/JzLY9HXxk9eUvKnyH2i+W7L6yQbzxm5b/efeDn/966kdhPy/88tIv'
        b'FLl7P/nxtc8++M83+11++uWiYwk4sf8nkxx/Wbn1zm8uL888mP3R5DcuZv/F5UcTPp/7VPa3P37a8b5N87I/j6n49XHPYzc83tFG93+ktvn4Mu/OodXZXzsee/fJ14Xd'
        b'v/5u73X/D6//9UDWX72+nB55+szDn/64aeb0wf+4Nzj43YH530l/7Tyx77rSP0X7jq3oR64fLH386RbZhANfDX7x3R7v5odbXQ6cfu1z0cadCU//uOS/r/4g+/akoj//'
        b'9vO0j4/98t89Yoqj5+2JvnXjK6Hi4aoxwndPfFeQlt0u3Zszb8/Bn35zXbbuj7euFewqKFn3V+3NX62Z7fM3/p/mJKi+uyaJoBqYRKDfP0GnsFqDXgedVb3C6i58/ymM'
        b'lU2oFd3lFI2jZ6xm0/Fx9IDTQH40EV3QjaLN6AEZRSfjrVyu58PQA4OSM94bmKFXcSbSyyG69HaU4gt6AwUbxq6iGd3hrS7Eu6iO7BJ0N4kb2g+hfSZDex3q5dSQj6M3'
        b'0BEiqW4wHdxn4itU79QbH8zlNLBxK+qUxuXpVbDRLdTNrfuv1OJL3AqdzIWv2zDC5bxAdH46jcS30WvzYqLjJXhvLMPYK2vmk8GnAt/jIi9Votdi4mHui10fRoZXdIAX'
        b'V4DPcPq5Jzbj1kKD+YyAcZ3Dr8EPGlAbOvkUAGjQQ3E4aM2CiFViFLKFTFBSTaGA8GYb2k51b0n+59G2GEpDEpFMhKiHlyxwo4Unq6idc6gKNj6E3uCRONDBPowfUo3o'
        b'xSnuCrTfbpUzvqkAowzQhg7FJywUovEdIXpkj87TQ5up+IZHjOGcsgfv4A4qPfL5SCUmlFNTjy6yTrhWqD8swg+rS2jFu+PdfCJTX8minLfDD9AORKS6vQlxMMAX2jKu'
        b'JXy8e+6yKHSbpliNe2bGlMTivUTUOgGLJZLEET/i4XtT8TnK4XLvJUZ5SE6mQBCIonA7bXLF+CHeU+gjM858aH8gx/ujM1foFPPjx5taCuKLAZxu9+HkLJ02M7pQSWou'
        b'nyeS8SjP6vFhpBpJK9effLK1SKLTysVvz6EHYkSoOk8+rlcIV+GrFgrhm8O4Gr8wyZPU+JFIg4ayhXoyuj6ZNvnpGWgvqe8C7oTNhnHFW/mo1acpnzRZ2FOqzBhL5HrC'
        b'L/KZm7T4jo080hTuLeKUtd+tJjdt+LV64yQdiO/Qks8L4OG2sUhlItPgE640VxciLdzhpBp0drxRqhkfQLWrV6CzqNtEqJlBBG9zmSYJX6PH3fhSozOhLy5epwpOxNrX'
        b'icg2Bu8SeJCe2vUU8LirFoisc9liO008Tb+hVsdSu4Fa50WFRfksHF16zWaj8aUCrie0oYf4VGFsFBlECokYtdgLXeGtw2dqJFH/POXmf22gANcPploKwxFuLRSsB1wt'
        b'QOw4py6GbT6LWLrHuEXI7WSXhTDB4V0bnwQl9AUl9Nre99AETdUGTQWl4sCODUOMg/tCtl8UptrInZJ9FhillhR90PLxBo1kgSZwoTZwodpn4WBUkdoroj886nyRNjyl'
        b'd2nvqt6l2vDJ7cX9EbHnF/WG9ib1hmojUtql/aLwbpc+0QS1aAKJulhxtkITMUEbMWGIz/hM7E/NUxctVqfCb3/EuF5ZX0SqOiL1/mb1rPK+tHJ1Wjn9et4H0zWS+ZrA'
        b'BdrABWqfBYOevp25nbmqnOMlXSV9njFqzxidvvZqTUS2xi9H65ej9srpDwjuLFWNOe+vCYjXBsQ/CUjpC0jprdYEpGoDUtsd+j3HdEarPcPJb3+QRMcNviZovDZofO9s'
        b'bdCk9jzOG8ikQ5s6NqlW9Ymi1KIoSs9MdelijWSxJnCJNnCJ2mdJvyigY0v3WG30NLUIfh9H/SgexatnlWkyyrUZ5eQJfU2qnjVXO6tSI6nUBFZpA6vUPlWDngHtqZ11'
        b'3TbdMtVGzm3EEOPsHst9eSLod5t8eYjHBmSz3/J5QTngTY2EQwzPNwdUpxMmaLxi2qWq3H5xilqc0tuoEWdrxdlwPF7J0q8v0QRWaAMr1D4VQ3x4CL7cEtUi0gI0okla'
        b'0aQhRuAd2y9J7HTpDw3vtO20HZTEkOuQhCchKX0hKZqQidqQiU9CpvWFTNOEpGlD0tpd+v1CTsediDue0JXQbtvvF9EZo6rT+MVr/eLJLdWyX3NoasdUVRinZU8ryaR+'
        b'aIrNGs+xWs+x3R4mFTlb41eq9StVe5UOeooIXaDXb3TMohp3eHP7ZlqmHE1grjYwV+0D7lQ7N3Ru6B5/P0sdlK4JStcGpfeJ0tWidJqwUBNYpA0sUvsUvbz6uKhjOriD'
        b'Xcyq6i42nW3SjJ2oHTuRe9LP9RSBN7kMCj+95cSW7jU9Gx4L3nfu3KIJkmqDpOQbvivYz0Jj1XEL1UtqtEvqNXH1mtDl2tDlav/lpAZILKkB36DTLidc1JELNT6LtD6A'
        b'2ERd7MFZ9URVqiq1e9l9viZsqjZsKn3UHxTTubE7r7v4Pvs4/P0YdZCU+1p7Hmms3kHtC1R23WEa73itN4BCQfrYzk3d83RWA3n9tLUt67bTeCZpPZMgSyhA5OlNJzYd'
        b'39K1hWbjG9bpp8rrlml8k7W+1B5jMWePsVDjt0jrt0jttWiQq4yuVNWa8xt7y9QpBfcX94tDSIdM687tXfItn/UBSGsI2wWEkSTpVLVnJPnl+qnGb5rWb5raa9ogeD4N'
        b'gxrOYanr05j2rPasQXFgZ3JnS9f67mTy06JNyNDEZGpjMsHuwueJJLVPknp/kkaSpZVkkU/5Q1+AsJ16ZPTpmKbK7vOUqD0lgDuW1R8Qplp6fGF7TnvOoDi0K00rTiBf'
        b'8InsdO33Ch/ie/p6DDH6YBD84w7ZwK2QCQjvzB2yhWs7xi+ky7/Tf8ge7hwY3+Aux07HIUe4c9LHOcOdC3mrq6SzZMgV7tyYsGht6ER16MQhd7j3YPxDOycMecK1FxMQ'
        b'o/bP63V5bKtOyFP7z/lg7gcF3w15Q9wYxi+002dIBNc+jDioK6EzYcgX7vwYv8BOryExXPtz1wFwHchdB8F1MBMapxIPhcB1KCOJ63HSRmWoozKGwuBJOEdDBLlutxmK'
        b'Je9pfWOf+Cb2+Sb2eml8J2h9J5hYo/QHJKoDSETv2sc+moACbUBBe06/25jXHQ47dKaoojRuMVrOFWTsOGqnoMrSuEn63bw6nJ64hfXp7rWcR0mRf7uTyflVEHd+dRrO'
        b'hagXoxgIEqg1Qs1ag66tiWufVzFF+J7mZRCchxk0WLN3emZwQDfSFBwNB25erLmVw6wQli2lVgj//wy/N8sJOGW/Y5/uyLzn6JLuy5ew1K+T9CW0AtlWcBEk/JdqBYIG'
        b'76c8Kxq86bUtNfLg6qqGBgq1C1YFOuhh0hrqoRlUNZgh8HK4RjIZB2xXFdxYs2ZYppw+e1Rl5cyVLfmNtaQlLm1oql4hidehJet1gpWKmlplAyjmrmtSBq+paqT6sLL6'
        b'1fWy4XqzZkTUN9KEtdTxss4tXY2C81XHge0FA85McL1MMVyrdtiD1OYqedXKYPAXnRqcT3VzSU9W1AMiMfkO6OlWBVcrFS1NK7lsDUXLl1VWSgDLYkR1ZsIfPT/gsr4x'
        b'ePXE+HGEFRmEjWuAmS3LqloM1Bo1pq3mqCsbhUmmJg2cXjLJAECTzVik9/pXJ29SNlN4M6s5kqK31FcrG6rknOa1ormm2uAGWxEcBb5OYwkLyGcpssC6ZnJb01IdL6GV'
        b'MILmNTC0pUZfL7p6pxYrjYRmJWEkyR9a3Tp97cuaqM/BZgDYtpanWQUMr9MXKmU4SDkvJJcClhTitvIizmUHuOs4j85y59nUQcOJHLTL1EFDYpCpfwayon6kBMxd/Do+'
        b'NRnWyddQJ5z1Bdvx4TzxwapE3OEXmOcZsWoTvj4bvYauZqKOhRn5LegKPoN67aZJYwNwFz6Du7LQ20Hr0WW3xKpCehSzgJfHtDNMc0d95fKQMleG7t7XyfAu3EaW76VR'
        b'YDYN7kDA+wq+hh7ZMqHLBfgK3p1HX//vJTZwir92X25lg4N8EVN/u6GRrzhLYrqqtJx67uQ2VjgmcVwlK9knKfqo08dnTvJ7Wct9Z3eu8PnQZ+/DbQ++OJv4RfavIr7J'
        b'ezBvqzw2cYm3mI/HqX5z5YsJ45NWjxuzYs3N2Mof1H41LniJ81c1N95b/IF0nlKk/o/QyWN3SS9Ic8qmlM679V589K8S3LPkEvGFjxx8SreGeP7U3vO/ZNcqP/7V9v+q'
        b'vP6rmsq82r25rYmC5GbC1LwjoWmqzySOdBOmAF8fS/f8luITnJ26bs8P3UfclgE+loxvGZwLdOOD6aT2rlLVOnwSHVWSZTy+gY6/eCmvX8hXyOjGYDU6NVEBB6VxUfqD'
        b'ouQ8d9zOR734eB1nH39wPD5l3BnEt9F+O9gbRHc96JYFeoAeoXsxceicj86GHwz40XG0h9uUPIvbvI0W/OEOOejABBqThC77x8TFoCOc8wLYNatNo/wQp7vSzUp8NMGg'
        b'20x3K9FN3fYXKyzQ7/Xo9nnwfif9Vg/eiffS7RIv/DY+a2KMbtzqwQ/wObrdo/B7oQKscSVvD/6caNe20Ck1PKer948ZbvW+JGKE1Xu/0d6VLIa0omgAly1hvwyMJHO1'
        b'ZAbbn5HzfgyRlyXg1JsNKgGpOYiaQPqWsIPiIEg+ici9weFgbHx8Y9dGakid0heUogmaqA2a2CmgqzHWfUJnZmemSnA8vyu/m3dC2iklUr2qQuOXovVLUXul9IdFqqZ2'
        b'j+fMXt281G5hIBmu0oBP8DBzR8xmCtnxzxPyhitkO/CHaeEaOHbOXAU7M4JlfUBieUHw/apgswO2ZEquIHOydS+6VIxhDa7jOMdxfIPjOJt/uuO4nUSM+U5gRYwprWnU'
        b'QYjSScxgGKlUcGJNDZ1YyCyYnZGfWWqAdYl3GEkWqFlaX62oqG6oJ7mkUpsjPTZMLaARVi+LpynisyHMpMkqTbIdIVcdd1Op0VSswWoKEIIVNZTMJrkMHpBZ1uosmFqr'
        b'bKx+Dg3xOeVFlRR7S9nc0FQl05dezxCrmQIipwFLCyZonZ2kQlnfAgZRJkRZn5tfSFVmZlll7GhfLR/1q/kzR/tq+rwFo/5qVtboX80Y7avzsseN/tXkyuARJNiXeHn8'
        b'CHZr+bVUoNPJkzWy2OBoXfOPNjN+M7fOo2Yp1gXAkWzucuRVFGzb2IZfxbxuLiwZuFFhdXJ8ollvoWaBHIQr153IB1fXV42OUxll5VZISOVwZhTcGMPRwXW3etkLpFxr'
        b'OpveUioMTsyzpQ74EieEyO23pDNKSDc/JFURiA45gv6iCs4qL46nIvEKgRe+lZiYaINv45sML5/Bb6BTnNolul2QEoM78XZpPBG50DG2EKty6Ev4KrqBO2Kc0dvSAh6J'
        b'2s5OUuI79KU0/CApxgF3S+FkBLWyU9F9fEUioDob6MCSXKrkg2/aFKPjDN+PnTYb76ZKIng7PpBKIntb8D0GvZHB8PBRNgR3+XGk9CSj3YqkjHFyHsM2MegeEX07qOIF'
        b'+Jo5ocB3XeU2+BF6jbx2gY1OwQeUMAuXznPAb6TolBYTnGZwxB9HuzYr8DVfowomurFWwuP0OM7ivZP1NKI9tZRG0PADGtPJV98x0LgDH+WIDJlEaUyMmMbRUYeuc2Ss'
        b'QHc5/cxtuHWdAnegGwb60SH8poTPfbJjIdqt/2Qifod+cgY+qATBslmIj+m/iLejN7kvoi70Jv1mEr5V4rjaXiHAu9YwfHs2gaxJ9nMce33MUkdnuSuD9+I3GX4sm4aO'
        b'CjiFm7tEWr5LMr3t6MLiU/YM34lN24DvKgsh8gqDthfCMqOU2v6BOhxZdxAJFh3eSBY0+/BO9BB1oK4yctOBH+Lz+DBZ0XSghx5ELD6Gep3gbh6+jw5Qnaal+CruLc3C'
        b'FwmfGWY5k4+OO9KCoXZ0Fx3ER8DMcF8pw2Qs46M9bLo3OlUf8rN7fIUPyzB7/P4GBl1njqSQtctNn6oer11eP5wzNv9+UVxm5EL+QudMh9IJnq2f/+DnP55T1vfjwz8Q'
        b'PHmv6ydOZ9vGlc7b2p7yWtxrm1w+4tUKY5llkY773nFa9tXy++/c2ZeyL7tR4u84b9XX1TturPD5Waf66TjlzfjKH11o8nW7nvPda28dqWFtJyhTilI+/mjr9AXO/095'
        b'Ihb8cKpy57ttnVs3rgs+7fnhwdy/FDrM9c08FKVukX5zLVfZlFgw6XxzZrHgN1+FZqa5Ht7c+KunX/0uI2mb6Ostf1ifqbJzLRI0jEk41Fg1/3Hurit/bV/0k5JdmzeH'
        b'/40n+zrXRZk+7mnY7gduq54Vat1vSngf1K+fUL03+OZvZjya6dze9dGu5TmeYXVCRhGw9GLQjyRenCurHrwzupC0pFtGl4xUIwG9ia7TZYkH2kuqiHO7hve36PXNbqET'
        b'XAaPfNGhGLQXtZn4bHKK5duiHnTsKYwa6KS7tHCdv27NlY7PoXfpebg97omjvittkGoNI0A7WbwDvYvv6xQhZsQZPKehN9BJRjCZRTcmOdNXF6Ar0TFxDkYtC1hHLUBd'
        b'9FU3fCogBu/eALoKsESxw208tK0WvcUtAN8snKcoDHTEd1iGxW0MWQO+hXZwKhAPfMtRG7qKrjSngJPR3aRjo0f4HaosEhy3GrVFoR3NKUISRRrzoZnO3LrsmHIFavMv'
        b'bU6BDPcwpC1v20wXfOlNuNXoiay+LE/nh8wRHeKOti+I0bsKvBW/xikJXgANiDsJNC5/LHpLsSmLDCutQEo7WS5iFbpBi4COxy9TkLXZ9tUuNuS1i6DDsG0Ffa2pxVOB'
        b'L6LX8V0yeLPoGoNPoS78gHvtXXwebVXg0/zVq+BznQzeNyOBlgFtiyhU4DOxq1eRj6Fj0N+3xXN2rw9C7CzWtfgYwy1sK8nK0vZltpRhHQOTj9ESVkGk7fXu5uaE5BFd'
        b'9UXxuFVf41i66tMGJfZ69Ib0emiDxsOKz689rT8oprulLyi5PXfQ02+I8Xcf10mSJfeu7guapg6a1h8R3ZvdHy7pTRniswGpZJkTkPp56rQHYfdlD+vfin8YP8RnvP0G'
        b'Rf6w/COLxLCxFyedndRd1rPwfoQ6doYmLF0blt5p1x8UdnrDiQ3HN3Vt6hSQT+qWn3b3wzVBadqgNLVP2re2kMGQHTMmVFXW5y1Re0s+9fLp9w7R3wHi4Tp1+Hi1CH6N'
        b'mQg0QSnaoBS1T0q/b0CXr6q2zzdW7Rs7coKaPt8YtW+MtQSkNH6xg96+HfPVoalqb/jV4TLyvSdYe2HQ2lfgfdXYPu8otXdUvzjyiTimTxzTnaURJ2nFSWqvpO8rQUSf'
        b'd6TaO9Jagi/HBLXX9ydPvD2ll/w8Frxv/5j89Cen9QIMXEi6GWYauOLKYE1W1ELO35OT6bpL7sgfbi8kZPQep7lFdRgsqoe3xfdgPS1nDN6mt5AFtQSWzCMH3+taWm+8'
        b'B9KY/Ab4OxFZIEIMCCpK8qUDjhWZ5bNnZ0sz87NLOXhEA1LEgGNzVX2jzsWS/CwcNDkYXQtxB1EGj1jyMxBQD1gfmCNKUIAJOO6hGxCUYRK//wMqJDA9vUBpRF4Gp1Rm'
        b'3vbPge+ttRZ4iC6MOFBV2su/n/y4Wu1ZQH45qEF/VUqvzf3yDyL6x4iHXQ7ZCsQuQwwJWguHnPjOMQC9Zj1wmO5cTdrs/yKcwdOB2cHJ4rd8VhwDnuRiWgsHvQOMEHbT'
        b'AcJuBoWwm0Eh7GZwEHZwutrvFqd2i+v3yiBp/LIgjR+4o4OwtcACV3E8oBROgA43AfrbBApRaIqVlw0fyqUfyqUfymWHgRACdp83xe7zpt2WhBQKzxSUDxACxYAQKAaE'
        b'QPFkCspnCrgHKIU+gFLoAyiFPmmteUN2rs7jh5jnBsGMb0inndongfyqJqsmn5lyfgp315oP4CPW0UasQY6YgI+wzjCZDA/smHQ2kx3ir2GdA4aY/5OhnM+4eLfO7QxT'
        b'OwdqnAO1zoFDPDHguDwv+Ja8FGRImsrlUKZ2DtU4h2qdQ4d4U5xhILYewsthVlNxqCtU+fJtdJ+sJ2fhR+Yb7izjlyuoD0d3zJarTrq/f9pIBqWjXmC8a8RbWcAHrBUO'
        b'Z6VLoENa4a4Bb8We/MA14K4A6gr33HjtJnOXecg86bWXzNtwPUYmItc+9NpX5icTy/y7HBcIamxahbWsLGCnhU0loLR02HawMscOpw67Dg/46Qm8QIbyKwYELnvyI4vV'
        b'HeHyZWHDUEJseUyNjSx8JyOL6BlrgZRix+Xf4djBq+WR3D3Jf7cOj3ruzoN81aPDvsOhViCL7Imy8t04wJmBL7fatzq3erR61drJoodRYE+xU4QUpcC9ViiL2WkH4Ixr'
        b'2QWO1HdZ/IAHjKiZ8hpZfQsFDqqtkT8bZ7bbMDxBMN3/NEv0LF4pb0ytVzSlKlpk9O+4xMRx41JhByR1rUKWCvNXfGJiEvmfHJ+YLOEPCKQls4sHBHn5uXkDgvLZuTMv'
        b'sQO8rGwS2sMnK0qkRfMvCeQgsw/Y0B3HAXu67yOvJ5c2tQ1VdYpX+WwSfFYgj4OZLx6CBD5MvfnSUg5x7hXzmiyxschLPplmWJo1J/1ZxrKWlubUhIQ1a9bEK+rXxsFe'
        b'kBz8zMVV6/xZxVc3rUyQ1SRYUBhfvSw+cVw8+Z6EZ8z/Eo9CusgbqKO5Afuiksz0ooqM/MxnY4HozIx8SiH5O7NqHcyNs+GUVtFCMo1PHP//svcecFEd68P/2UIvgvS+'
        b'IG2Bpfci0ntvKihIxwK6gIq9YAEEUVERURFRVkVFEEUskJnkRhNvsktOIslNMcm9yU3ySwI35qYn/5k5u7AopPxubt77vv+b7GdYd86ZM+WZ58w8M/N9UIjGHzix8yzh'
        b'YsbLnwfOq3paTGJUfERuaEh6WPSvTMqNz2HyNVnkb32euDFMWFFZGUpsV9PTiK8oSagsISm54ZTYUymhDIbgtOY8UR/fGs9eqG/1Zqw8vtq0VLC4CcNnSNtPGIl/fSIR'
        b'P5KIhzACx83+cLdvHX9DSd9QKiwqXla9sopUP2nL/zCcwVPnwGdmVRDzIRAllTDn4dAU0t4KXnSoLrtXPkARhEX+/BekCIvWLPH2fgVK8012pf/VWRAWbyjnCiuqq1B/'
        b'YJxLTlc0zrLIaTSLDXzK0Ky5+jfyBJI4MgeWszwjSEGeKrCO/0dQBc4rMWP3jhkG8J2To3jcST7CLLX0xGkEAlVZEx2hZJuKZiAQsAhvAHurIX5qilUn6QLqfwRd4N0d'
        b'SjOs0sUw2L6yDUVya3UFpGGYvSv4NfMza3Np1atXVwix2R/3Xim6tdL/6QsFvCdUAc8+PIL/85dhVfKLV/jx7B0qy/BGmLU+zt4OvyJJRjvx7MOif/liqRbCFzvxfuk5'
        b's2tInn1M+m+6w+1n7vi1yg4n8WSmZ1sGlS7lMGseDFGxsCi/qkIoi5l1ARWPCJjbnhSb1cKyCmFZVQ3j4tTeAY8zHFCG8EjDYeaVMQc8/sDX4NGAA14GdcCvcQe+89Re'
        b'LW9nd2dXf+klMyczta3LlVwqTXXqZ2/yM5P0bAVjeLfSos3ArGXqx66SYGtnrR6ylcB/OpKTdLKZCbNSpOaseZoCyDIZY/rrkyRYTF2d3Nk3w8Y9/B+Kq8bL73hlmqwI'
        b'kl2FRcuqsEChQtU8CebF+9pm4XriVUWUzrplQukmRHyrFDxKaoeXVlSEy1q9soi3rAqNHPOrq2bOVlhIekRUUuqi3OSM1OSktIjcsKTwiDSSy8kNgIQxOsMuQmklMUqI'
        b'qZ/kkJhEGVBa1m4yo5R0PXTm/XJTa6Rk3Z1JYWoJ0+EJneIw645D0kKrmX5aSSrxiXv9HJjSyS4pK58ZOsogddGYm1lWxXsMy3kRGamzrPWW89LWlVVtKBKuJA1X9TOZ'
        b'ZxTiLH0JdZiYqmUra8iNs2s4h9llVsoCZhpkChGMJV/aJJO4YGbbxSwlqmI2UMr5QJ527zSU9Kxai6T01Do4qh7pwLBSJr5PpDtzm5BpkHxPiQkNSeTlF62sKC/BKf3C'
        b'erHKDGM7rUSyPGlXXQYPxcEm2MyhwP5kNjzDsoe1i5gl27NgQHvKx9lp2G3A1uSymC2TeJ4G+larTDp2y4KH4KWs+cQ+AOq3gkvYcyPYB2+g//tBHZdShzs0YC0bNpTC'
        b'g8Q1mzbYqzN1ODWduO/aOxd2csC+fHCcONyC58PgibRJYMYG0DibKzT00EZ4Q1UFHAadUqJkNjgNRdK1TgqeAb14sTM+nSyRFoILzmSJlAL94BheIjUHJwgERcmrROYB'
        b'zw60Ocp7n5t0pLdaQyMVu8GzFyRm2NvDerjPBdY7Yc9ljE83AV5rOqrDcoU7Ixl8BeiEZ6b8r8GDRnB/LjxCluyHV0mX7PVLkg5YK1IE0LoG7ALNcm7ZsqKdYxNgHSqy'
        b'Syrci5EmO2EfJxXUYRYOvAnO1thQYJirBlvBrZKy+YtOcCpfR8m8feHuquRbqsBV907MqZgLHR0d77xv8TXLed2FbD2lMgPJu0MNYdr+1R8lbciOLo3lbH+zPeql+1Fb'
        b'33UYEdxtOdiVrSKO2fjKPrG2i3UYP0L3UGdXwsIDC+Opj9786B1VhfMm6T+sepQD/bJaDL++krUj4wCEXzxKNnV1eE6j/odqt9TnC8oFrpYZDbljwp0vDaxXdm/tW/tp'
        b'md6xjequfzuyelGn7Wbhp7v5Azrvm6Q2tq0q2HQj1Mr0mw+Fnxpuez3us/YdX5hs/KA2+4PitXd7bt9uKBt9+9Y7H3+jtMfauyJZia/BLMU1wiHs4UnA7KBszAVdbNdF'
        b'tswJ4SF4FPasALWMt03sNNQJ7whVojRTOW4esINZsGx2SXdMjIe3p61JQlEJWSWF2xehyp1yn4S3pYJDUXhnapOQycEdeBb2yHamgp2wPQTckvkC3RMdawSHnjiAvRJ2'
        b'2jHeqRpy7OXOpDN7PMExb66ygi+5oBrehKfBwEY5t0jSpcgVax7jtQb0pMvg0DT3SuAQPDbNvxKoVyRF2VQFjk66wpL6wQJH4B3uUgHoJlVhikRU5qcLXod10hXj9tWk'
        b'oPz8XPQg3JuvoeiD5pwEViSo8ydLxcsWhyAdEo+qIJ8VBevdwEkeX/1fWiLANkP5UyxynjlmnNTJO+xJYjGAukJHSltfrG8vspZoudBaLg+1fEe1fAcNRqzvKYqTM8b8'
        b'wkeK75VOcFjaC/EGUxSOM6EiZWzebtKsOGZk0eEtNuI3K4xZzJvxFKqOgdwRLgOrjpViA3f0ecvcvnX5mG/gbY1B9P/I2pG14xyWQxLZzJpMNrMmk82syaxHBiZiCxex'
        b'Af7gU5MUy4Fsf0W5cogi10eT66PJ9dGsRya8cYqt5z5mL2jltmuMObm1cmlD/iMdQ3wyLZrVGvnQVDBqKhAVSUw9aVNP5tdHuobN4WN6pi05HVYdbh1WtJ6NSLfHSKzn'
        b'jj6DPrcD0J8nvBSNcyh9D+YC9JGbfGvIHYb6+XnsrPtjNagnjir9ytZNwFN2ETX9XFKWw3+ulxXi0uOMih91UzNE6bd4WZE6FFHIxXOa2RwmzFRVMrcJjaiqhN34UuI2'
        b'wflXTJye9H+CbbZp0SGpb3DDI0LT3+CGpUaE85VmOgUn/E7m2P4NpYLSZcKSokphCecJfuIcWYE7UHBYeVZ+IqYnKu3V3KtI7BhzCCdRa6928Zw/kJKIdxuLZrJjhBQW'
        b'osG1/HEb2ThuBrP55AzgaXNIMc8fz0/88yZhzHkzbI10ko6nJz0o4PM+Tx+PQk+Xz1ABGq/no3lRRXXV1CypCrdKlXQO+atm59J5FSM0v2KCvmzV1L3y2WF+5y2r5BWv'
        b'rFiGLW9ohlWGfimvXpVfNPNkBj+ufNIehIfGsj3YISS1mbZTMrmYNmuVz4ZszlpVtJ6ZkuFaYbxIrGLOKs1y+AhdU1aI5xNTVSEsIqfPUM6YMvDsUUaFpGhkvmCVGuns'
        b'7GzFn2Wmw+wuJQfplmFpqqwSVhdUVaPUp1J25kXKNmfLxc+Y3uQ9RDKrV68skomAdOc7mlrhwqLZ3ypUlTOmYZ8aERmB9yJE5CZmJIRGpDrxZBPj9IiF6fxZ67uInJzD'
        b'lV1UXiioqhCgP3L1Y1+xmjlJ+DMprJ/J1oB+LRLiE4jytoafTQ7/N2mKwDX8c5aCSa8eUqmeMbXSipWFSKXOaFTgoVqJSE0MiX/agDDzYbtfaVQorC7KxQfvmKpA/+Lh'
        b'fxGBlcoN7hdVRSVILpCA5OUlVpRjTfEzpxDXV009HSeGU0FzSHzyDyuISdEtFlasQlVVuGyW44IrqxnbbUnZ2qJymeSjrlmId0nbF1SUV5ah6sIpoYorI7+iWp41Y0wy'
        b'8hYvvnwxmaxW5C8vKqhi9MHMc+y0JF9vVzci3KhxSHlwHpykfrKk5SUmKNw3kVKcMZ3iaiHpa6S3kxOQsxsamDecPy9NOrGv5K0rLSsoJQcqa9BTVq5EnW+ZkJneMxfP'
        b'rFsqKysKykgjTJoZVgsrUEcmZ1dQ1UobG3UERuxnrswpLefMS6xAqnb16pVlBeT8Brb4kP4kf0B05r4TxuiMZVKliJ6OX/48exTynXh4CMCzT8pI5ePGwEMBnn1oROIs'
        b'/dBB7sSrN9/hV5zDndwMHzKp6nG+06ey/XOHbH7R2mEhPQPatSwYtiRP2jTwIdBTIWRcS6bimRxFKs/WDAN9nTYuSZO6rz9qCls2mE8aOuAlNFlsjSQWkDx4Pr0SXqfS'
        b'wBXpdnKBMbmpEO6IwY7IuXMWSRnA6KZt6Yx15BLocZpuHdmyhUsxxhE4CA4w50wb+JgoJnWJrowuT2e4lolxAofMaKfYDDmC6BPWEHhhK0MKvhKhjSZtR1WYzd/NsHWh'
        b'zB7CUWfBYdAbDPbxqjNRpDfoXjH1NCVw61c9kFBWnWNQkGI/STvlK1L+rrqw1xDcZcxEomzQzBhbOE6s0PBgeCWqeh2KsIOX7eMIBFoQm4QxqUwaCvAg3KVqYwTOq07Z'
        b'NxbA7bAdRXTW2MwFu0BXOugoTAF1oVtAG9gBLqL/z6C/u1esB83gXGj+UlAfKixLSVm+VGiTA46tKNWiYFOQKWgHV5izD+5qAjV4fbU6m2LD2yy43d8FXAd3CMwXXvGC'
        b'w7PmC9YZgboF4EA+2MVkyB8MSXO0C3bCFvwdb5fPmwP38CjQk6JtCC8ZkIqIz4OHyI59vF1/61IX2AkGqrHswn1gOzgiMzs58jOltOfV1dXpsHm1xhx4MF1a45PmqMYA'
        b'cDkdG6Jwy8jIsDI0MkpOpEyepAn36sNLWwurQ9BztsBbsIPBcXuDllmI3Pi+9GmtCQfAHo0o0ApqGcBzgz3cFZeIDSpSL0GNoCeZSCjKQdwSHwKqxcgthcpYUD8X2yDg'
        b'oVTQAOqRzK1BKe3yr45FCfnAy5ump1OSiVKKJoYMYsTAtOe4yeTALjXQomsDz+mBbnBWX49DgWMJ2uDsMntiM3P0gXukEG35ArHhaYjKCq8FopbZgc/GwvaqOfjYAjiY'
        b'T8E9qeqp/qCT2P7AKTa8NtkMKdHxMfxYgXMm3OuUqQ8OPVFPslxpTO8pqLpOVM8FB8rBEEH4ptoVo+sIaBQl+ETS4LYrSf3XJp0aqwtuw4sBxKjIh4cM4GUwLGdX3A+b'
        b'C8nOU2ab1l54MNIRS8U+eMjD1RXU5sUhddBMWYEBDrgbN4fPTkwvazA4ya18A00u1398ZVf6rUToqlvdvu6Q52ZrgWAvSzEv9L2soau6lg2nD+9oOaJ5z2iBa6vZ1eIX'
        b'Rk/99XpMu++a7LgDwtwPTXNzv3v4U5jhVVblscPLaq+P/23Fq0rDCj/mpQw1t070N/DPHhZu3ay9K++qQ0jy2SOvhb5/bK/onfXAUWeXX1SnYfLj999Mv7/grSOO8ekf'
        b'ZG60NM7IHY+sy+i0W6ybusvwxaDElWnxD97LtdEP17iQ3L5xbqPfecv3X3z0F+EnA/P69F71v8p/o2N96Jevrv/0of+r280Wnf1SU73z2ySF97xfXqu6+ca299V8yy++'
        b'lKvQc3xt4oofJ+ZZ9a5XeDGh4exf8if2Dr95aoVT8T/bjkl2jkiu+Bof3qm/p3917MXTJfYfZer9+WXj5zzGh85+9X7Tx9W3krcuOsXdu7Eo8E/pK3oV52Y2RT320U06'
        b'n/l881r7lZ0Lbpza/klZcHXNc+8fuLPfevPHwldtF/64/YWr4VurfRzVs5a/Nm4RGnCoY6IucWN0373wnrqMD2wia+97ur32MMN85yGtdw5U8WCB5u2FYa8VbP4gbZ7H'
        b'aeBUUHc/cPlLewK/ujb0xe6hja0pURvCLj8aUH/dXqPQ9z2BjltIysK0Z+125Yzcbrv10bGNA4N/2Qu5L7+lumL3/1zZapHdzT56lK9P7JFrwaUEYoxMT5U3R96GfeQs'
        b'fDxSCYdlxs4q2CqH3uwC/cTQp56jBwdgQ9zkoZDtHswZ+Svwymam47iCk3KnUfoCiWnRjA37ZKZFbFZESQ6A4/C0KjmsoBFViJUD6FynqaEqhAPojVqloUjpruGkgQPg'
        b'HHPKvnFJOcPQTIR9jlMIzVRFqZ+vTaBumjF1K9wlPTN/EkhNvbciGcTn5gVypl4wsJicItFwBiLmWAs50wJ60etyZxDoY06fDCqYe2zF3sliQA+XUlzJtoLXkskBkzDY'
        b'plUAWqXYUUxuvhhBDK4R5rBOZrnlwKtTxltwAYqIhdrO12qa7Vbgv1zechtgyViRh0rwsSyiNzaBo5NIxCJLKX3Tk4VincB5LsV1YsEb4BoYAo1gmGRiEbgFzkwz+85B'
        b'/d+Qx10Kt20ldt3VYHAVOKw2aUPvYruCQbDvMXZxJETt2hkXHwPqpjAKLfGyAyXoOkUXsI9PJEBdG+lnLDvRTvA4em2i0YdmOCcIHIQtjJ18m3Al2OntKJBjJLjD/eQY'
        b'Sw4QwYEl6qDBJUHAR3kIYvPmOfEN/k9sTcdZlY0qZ6cnWc1geZsJY/ih1HV8sYBxHW8rspUYuNEGbtjQHDBmNq81syNSFN6TIAX9RT6axc7Ms+5Sp3luUlYhz6tZY8zS'
        b'Xs6bebPmI2t72trzobXvqLXvoJnEOoq2jhJrWY7pGLUEi7zE7mFih3CxDv48srJrjmuOG9Oz6igc1XMQ6zmItozojrpEiF0iHlnZ4rhxRcrarTdxdF4ous7Y8pRLm4vE'
        b'2JE2dhQbR/cqXpsz4jXqGt2sNM6b5gadcYKOimbrjW3fahMclm048Z5OCGsoxIi/CBaDPvPrUBzVsRXr2I6ZWI2TPeZS+3cIMXuHErN3KDF7h7IemczD97qOzbPr9u/0'
        b'Px3YFdiq/PWj6UdXSDJZsmQySTJZJJkskkwW65GBObp8Co44xYjEiEc+3ipvLJeigTlOMVKWYgRJkSDcCM6QZRTJwpy2AJy1VIZcmCwxT6HNU8SGKczaQIbYKUhsPV+s'
        b'gz94h7xpy2axgWtvFgbwjXoliL0SHvEEvbqjPC8xz2vQmvaPQ3/FydkoJES+DIlVJm2VKTbNfIQPB4kUxAYC9Ol1HNGlQ1JH3VPF7qnkyXLMSZxvZe0wVsdG5m/v5nua'
        b'oz6ZYp/MMVl2E5nsxkvME2jzBLFhwpjpvPYkXFx0udI1deabtOChpOBhpOBhpOBhrEemvPZ42tRVekv6tRzaK/IX7xpXxU0f8FCHP6rDF9lIdFxpHVfM9rMas7DFSL9H'
        b'FpbN0X/TMxabCERVEj1PWs/zoV74qF74SNa9YnHmEnFuwVhEsjh1sTinEMmXfjFOHoXNbFS5KAl2ixqueOkTxA4BEp1AWicQnzpyQ11mnIP/Orn2xAzqjzoFi52Cxyys'
        b'Wis7PGVSJbFwpS1cm0Nbognvz1qkLtbxRJ8xe4/mcFrXZoy0arxYxxV9xqwdm8NbEh4ZGDWryK2QzJ0VFzdlKBcuf/qE06/RT3i14GnK229TTc14GeVP1PRllCVOLFYq'
        b'Wf74o8LfdZFFpDKfuqsZoj59kUVRZgrYhoLDimSfLbNDXmmv8l6qWHFyx+2TBJN/y47bb/OeslykFpUXFgkrf2kJgdgrpTYSbCFbVslbmBD/C4YQc+ppQ4hjYvUC/DZu'
        b'sUEv9qmDGylP+k5pyLJ3Tn0KnQTbwSUNvSx4lbhaWAebQNv06UWyY5x0cmEI+5jz73c58BSZoQjMZHOUQXCBILfgjThwrXItuAUvoWmbMxq1Oa9FQSw+/Wu9VMFnC7hO'
        b'Nmt4+PngB3CdwQmKZY6Pj3ejiTMZFd6MgF3wUFwY7Gb2sJANLKAddhF7zmdcDsX1PaWInZw0ZUVT0nvgDrjHAzaDM2DAwxU1FDxJgeFo0Eq4AbAxZjGhBoT7uFAuc2OZ'
        b'rTDdYLe1moqQA0+C6+iG8xS8VABPM3HNAnACTZPBeQdMs65hwe1gG+gmOddNXhaHB6WJCpSifiBoZKvDM4XE/sCH3eBEGmws8uOiJAYosB/NSIcZKMBZY3g1DR7eAndN'
        b'eTtZAw4RG0ImKulVNQ1Y7yq1pwRblxF3IKnoofsxLgD2gBaMDJBSFNpQZTPDSHAHDmHWQDzsxbgBwhpAv/QyRprmYHBNbW2lo8ZqLoUe6gDalzNwhhPwKryLzUawTSi1'
        b'HAXDWnCS8QJ2ATakpYFG2JJhAPpgIzyMPaooJ7HQ5e1gH2mFLeZNlKlGNxow5iX+NF+ZMbXBFVZU+Oo1SBXlWTVZb2B+3GcbTTVbf6OAVNzyVa750zfNK8nEOR53ZtZR'
        b'qoTaRC2x2MyqY3dQM/23iVVIFbJ2sY0mfzmH0rs4meYB9j4ecUzPTvwoksKnJd5QCikUxpeVF/E5QrwB4w3uSvQPRvNiLtLk7nLctTYIZlC1QtKfp5zsBq4sq6wqqFi1'
        b'ev4SJIVfCCgyIBS7FDOfe7q9rBsqfSqD1oOVI+zBytt8iWs47Ro+eQF5rZC6ifHXoAzt01lUcl78Z+s8mB+9HQ0oJ9PlXIqXl5OePo+Z9kf5YJIFOCr1qfOEQ50joIlB'
        b'YewMBnvU4HUK7pBZwVxUjIhEFxiBO5iEdxJ2rdFAEzZdVgD2sEKeeNNNiVJfvVgB+zxTy92EvfeSMwI9bvlqGmZgUCaVYQ6MWLWFuaqthZ2ZUquXC7zqQXqGC5pkHIP9'
        b'arA2VwO9Njm2rKCla/gsxufbniDYU5mIJqjgQDnFVmPx4C7OHyILpUgWhHX41VyPD6kwUiDcx5G9fv9VIbgkLwQeZcznXnpvyI2YvpjBwhGPkdARj9tlEs9o2jN68gLm'
        b'4B2xRe9AHfYUqtBdufD6HDauUd81WxnFAC7EqgnhRYhzjlQGUrXKRJ3YgLNgF+xXh9eVFtojbXIIxcJz4Bxx7Aa2a4MGfNICHIBHUqiUkKWMqbjDzE7N3sERXo1HvTkW'
        b'XtZkL4Yd8Aijn65mgAHY7xILb6BYBbDT2BZN6MPmlH2sfZdV+RPSZz9ofXpn4aKKv0RqLU2dy09Rssmtz38+SjOg7ESX34azUaOvJXzuccfkqzf/pKHRukP369ML7+ry'
        b'F+vV3IsTZ7EUuLofx23//viPtT/WNelWPrfkz80tb6Vve/fd/9n0js+tv76kWfPytzf/aeKxqOR62udG+7589/Nnrnz69kHvgjeTo7Z6+lcnLa1O2P394Pl89hH2IYlr'
        b'WVWf8Z90dw93PHK3d+5+b1Naq41+4aDec5/18dQeLjLK0Fq0VeuAWtC2+2sCevP0utcvffE5xc89w7NPR5n9NGC77zX/Z+mWTas839lR/7e1YU1lF2oOzFENKAkYKDcv'
        b'YG9lffHVoysW0ChDXfXEt4q3Pll5WaFp9VCie26y7hH7H5MVXxzKsIhgDXmu8bZZ1jDa/KL+rvJjrUW7xm+15vou1cvihGuErS5xKlfN6Nn4yum33Guulo0frNeNrPum'
        b'euTlDv+ihT5xL8fmF6fEK7xWYnpoRQD75Nh1s807fti6rUizwGh5T1jP7dw33zL/zHarguueva83dV78ywdv91x0/eSNhd4RjRsNP83lfqYYtuVRcLvoo9gEA8/u9IRP'
        b'myLWvLLx4xUd7sF1/qeaXjG8/K5C8mLloN7Ogc8OqHxoJ1mzOEiUtnnRxW2rtAt0elbVx3/iuc/l9PtNN0zfeEvPacfLzxZJVpq2sNwD6k+PbFX/8uGd909/eoLne8bt'
        b'4um//aTRvsKwO+/HGoXK1PxMVqWD2xyjl41O/XC/68KXrS/Nq3/pTJ2/u/na56o+yK9W3PRJ3abueZuq2+YMvmQtvF/9WqURfTl3uY/6lr+vXRrSrnFJ4wfutg2vHvW6'
        b'qLRxwOU71r2/uXkeXfyV6bvBp1q/UwhcV7jOZ9vnVs985ftM54c/cQ98eKjVYmh3nOs/dbfXtN1TOGZSMQ4fB732z+rsdwd1F19y3DFwZMFXx8KX1ElaDVg//M8WScDO'
        b'+h9M620/Cz61/1Lnmq8CHpo/Plqy7Zsaq3cmDt0zzszRSezadW6ecPyn6Fd2GNccS3YCGdoWai+A7Xcdb9R4iNS/XZsycfnRgU1rku4YNt7UvDuicSHAec9PEu2zty7W'
        b'u7+ecWfB17nW37ss25L89sgXis++yH1veSm8OT84860jlu8dHt8waJdrs76w5fpn4tcf/+0W2/VtA7+xt7aef+vuT0qvCoJ65n+04C3xqPOK11PmjLvYPQ7/Kaq78/LA'
        b'u7kZVS6HVnzf+w9J1vdeoX+rfjDnZdrk9Kd36jb8zW/8w/rF33357ajnX4/tyDTM29wwknn7RtjG9R++bfnBtn8mp1StVOhZ//kLi+7X/08F6/ONteZbdgf9PfR+Jedh'
        b'zMbyrhC7QNbnOv2nMyu6oqo6YuNf0Ex/puvvCya+/iv6chZ/+WFdh+o7rIDkTSfuaz7++6e3d4xVKG3QeLFoVDP9vnWGkvEX+zZrLf7RT/xd871539QcCVR5wSLmTsiX'
        b'37SKwz6p0j3R6xIcMlH+yfx9m2NLt0R+HWz3/UO7+ycsGpYYHP26vCbnux99Od8fL/1rXe26PS6uLavfT+70p7+bG5H5fvOfWZ9dTPf98gI3y2bTg21N/3zpn0s+fImf'
        b'8vctjWsqTdKHn4kc+Unw8ZWNplmcZ9cZsr/96NjglSa3dz7smahY5Zb7wUrPbxXdbv30QcPzf2+c87Z6p5de5/XQjUe/CTqw64WvAzJu/PNuRkWEmO8ZqZ97+MRnxlWd'
        b'dnabK3f6vHOw85vNpV4N9T8Vl370+Sc/ujftf33rscEftB7+uazA7cM9bgtf9zvw8Ktd99YFOdl96XfnT6rZP7EjvsjmZvL5K4h5D1xTzVJzQKPrdKS2sb8S2TZPC9DP'
        b'hVdWlxDzHj8y2VEeiINe0JfYa9EY8jQxysLjsK9A3oAXCHopxoB3GRwgKSjDwdA42BjHDwyUbe2c48opgbeXEhNg9lx4R2pmhB05cptIQSs8+tgKXZFamiG9ADSvTZpa'
        b'fZEZIsvzGCdK1+FAKb4Qu1sROEfHJyatU6D047kacA+8TbLiWgrvSp0REVdEcA84yhaA26CJbGidowp2VJJZx5CB7MS4BhzmLNAHA4+xYxFQa4GucEYPFwgT+SpoAtJP'
        b'9u1C9E72RO+23lzFNDAoNSl6guOZcTL4kWIu3LmF7RAEDhIHLTEb/OLiHRTh0UCKvYTlAxoTiZHXgof92bigeQ7O3n700tvPtpkPDjNOmOr5iVO+W8BFeD2WXQM7q0nk'
        b'onILNbhXgMbC++I4lBK8Blp02Unh9qRmSqDIVhrbArrQFWiQjUoG9qJRVWgCk/jhSNAPG5zhbrh9ytVd5xJiw80Fe+Yw9wti0KNVwV1wjp0FeqOJbRv2rIJXKx1iYNNq'
        b'vCroyIL7E5UoLdDLqYIHQDdjJB4IhpfjCOeVohRQg1+BZ9kceAJVPJYBuxp0Z38c7EtSA+ftFbFX20Mq8AZxYpdMirAONsN9ldi/kwqaEypQKAs7VGETGzag2dQeRhQb'
        b'4FUXnE0VsN2GjyYauCY0wG2ODpKMW4ybqBOwb6EjOA/2qckM6XDnygqGONUMb8MW3KCOznxV+4xYB2yynmvIgdvSMhgKEhwqV3OOg9f5sAFVg6adDTs7CLQTM7sl7Lau'
        b'TAzWZjGDGxGoh9eYXrYPNqK26kclx43j6JwEr6BSKFDa+hxwDFzyJu6ANsAmDtgOB+MSnUCdi9Q/oAJlAnZwwTlwW4E0wwZQH1rpHAOuzOero0soSlOREwyvwE4m/1fA'
        b'nfnghqlarCB+DbgUjYS0ks+ijNK5URXaJI9IQDviKvmrI3Am76KJpgGSLBMSgWroWBx2nKkHDycRb0maoIUTyE1ktpm3wn5wCXtbgiJleYdLFbB5A2M+R10zvTIGCVet'
        b'Ax+N+0ALCzT6cxgK1DVwcCmq1wY3bQWKpUah7nZZm1k02ZUKzsRNEcLgLneyLJMyn1k66ITDHtiJpAickXPF1OLKiNRBHWNp9yJrDuC2D152sAEtzJLPgEmcmj2qhDXx'
        b'KEM+8LIqbGODW0jV3WFEQQTPm+MiJQhYlIpbyVw2aAV3Q8mDc+BOAzVnvgNqsAak9MowQpldVgOGiZbYiqYe/Y6ogZzngpMxjAfHOaCRkw/2rWJydgQehsPo4WsS8fiz'
        b'exNoY8FTsANcZDxvHYJX3dT4EM+GUfIKsDURDLDgAGgBbSRri9DcAx96WR8sWzUBQwLQzywSdQTGVzrD8/AkKTQH1rHAGdCH9BPuxa7V8Gwcs3SrSIGLrmqxbNSVLicw'
        b'1VkXDHZVxjjwM+cJ4zE3UcOFg3Qz3M8Ix6AnaqT4IC0sHIMUuOwN68nakk4a6mH9VblwtxBvrWeDuywTLS55nI0Kmu03xIOGBXJe5azBHaLi+EXaZI5UA0+QOdLGRUSW'
        b'zJGoncerfKiv3Zx27OAM3EbyGZ8NbuFsCuNdWBQ4BRtVF7CRLuqqIcxo9MRzoK4Su0Jj+ioSx/74BHgDzR/xmYCj4ADYway5nVi2Za5rJWziq4LLTqjRkEbvQ3rPSIvr'
        b'AHb4MqtqYFckSkYao5CZA0+xYL0gmwiuENyCO8nCWYQhs3R2BDQyrYBeguAaXsxfC/tRC2nzclhL4SnQTGos2gg04TjFrXAPxQInKbi/VLbGtxf1hr1ocrJyHayzRx0F'
        b'nkQXKMJLjOCcK4c3UIbtY9c5sCklcEgV1LL94EFwlxGcY4ZcfOYmKSYU3MV7KYh4zGFzCrW1GSXeZAeuOE5qD+212A1qJGxnquMybIy3AoOV5MWF9KxUQxqCi1y3mEBG'
        b'EdwCp+Yymp5MnY6DRngAyW4IOMUoghugsUqqIkmNgX5QrwoHkFCobGDE6Hg4HMYv4XhWAJdiZ7IEqTnMcZf+paC5ErW3Cqxbh/6gJ8Bzy1mUDjzEQY28M5hU3bpEcDJO'
        b'AA6BlkmvqqAxmLSGzhq/qRU412w2D9VAN7lpbTK8o1YNL4BGDRVUpZasEDQLPc5AAreDXiQC+wSsRE2Krcual2vIvCv2IEVwiimJskLMGnwFetWf59iAO7BR6pwQvXL6'
        b'5b3OwlZ10MQGh1VyyOpjXCW4QyDnLrA+wYkfk4A0N1nhVaB8A83cFJGqwqBz0rDdmUXM6mMw7HaaXH20hlcfu+DoXaBxDfFz+HMOX1U1M+BlZZeqYMaBXJMO6FAj1wnW'
        b'4KvuYsWrjbooUpaX4HZpGYSwFT04PtEiSKZkNdM4CWAPejKWmPmwFlxGEiHtbM0bVSPY4EJYHgMubHQEFysT4R02n+j0Iyyk5htgDyPJQ2A/PIZvTXOVqhMvjgoPiIgb'
        b'P7jdAx51nKEURUi3EEd4PkpE4laVgB5ZKRJ94/ikDNc5oEsnjIz91qDS7CEiPcSb7jMXO8xFInyQWQBvcACH1exLk/BrkYOUARBlgj1M3TfDC+ZqqFNLx0bKFDjkwU4p'
        b'BNelbg4LLNScI/T5sSx04zXUG5EE1JIqRiO5IVNcQtXYBCwqcaiBjnEoXVDLgXsr4D7mPXIa7oJXkTofgnspimWMG/O2dLjJLUFjAjQoUbV3gKIyorC1lnNAfYgrU79t'
        b'YWhA0u/kD284O2NdcAy93sDuQKI+wZ6aaDXUCcwSKTafZT5H2osXVYLbq7dWIh0P61SmCmUIm7n+oG0jU6S7FnBATeCMi6RoXgI62Tqp4DgjENdAbQnWnY6JAgcs0gNg'
        b'GzzCBkfgMSHJ0wqOdqWLA+yN5mMFdBsN7+vY0erwOolcAi+Ew35BImNY2Qx2wh0seHhFMSOQ9ULQIe/SMB7sM5d5NByQ8jedg+HRSufYaj7SAgroFi9VNhu0wFZNplfu'
        b'98fvVmZIfQNejpljjzWcBrzJ8eNnkiz4qqIiNGB/yU3MUS9yzuu2HuntLHgc3IhzTlAM9aTYNaxApMgYRGU/PAd7yREwNJA5gY+BuTlVkwxZe8FzjnJIzwIbNtIZXaCV'
        b'b/jvWcZX/sVLKnE5n9qzukDeZaEiY8LbYDSrdY+s7/urS/Ehm1wpQxOZ0ze8uB/PesvYVmwXKzGOo43jxLpxGAdp8tDIZdTIRewaIjEKpY1CmxXH9I1bVjzUdxrVdxJl'
        b'SPQ9aH2PZs6YoWm72kND51FDZ7FLsMRwAW24oFlhzNBEbBjTwe1Se8jzHOV59mZIeAE0LwD9OBIxooIvMO+w7nIUGwrQd7xWLDaIFRWJnWMGubRvjJgf28x9ZMFrVh+z'
        b'sG1d17GWOFFTH9PlNcd36HZZSHTdaF23ZtYjHf1xSknbbszYpNWyNbw9TnqerEBi6k6buve60aZeEmNv2ti7OWyMN685pjnmkbHJKYc2hzFDo4eGDqOGDhJDJ9rQaYLD'
        b'NtHHaDj95rBxRcrSuiOkSxFdbG41TqWwtU0mSNgcOTaP3x3YGXh6ftf85niUnY54ia5rc/xb82w71nZv6tx0ekvXFsk8b3qet3z0mJntQzPBqJlAtOxK6YVS9OxTqm2q'
        b'Hd5dARJDF9rQBf+g3KbcoXdsTvsc/A+1NrWO8K5YsbVfr7fYOnwwS2IYQRtGjJlatCqJDUM7QrpjOmNEhb05EucQiXUobR0qjQqXRhX3bpI4h0msw2nr8EdGZmKjBR2Z'
        b'HcboD/b6tmCc0jQyHln2/HKwfMzSujVLbBaIT9j1Fo/y8eKzmfmI5fOOwHGMZ92lIsoc5XmIefMHFcW86BFbVFFhLHNUUyhEFWVuJTbz7UjvWtRrO2rjS+4dXDZcOlQ6'
        b'xrPs5nZyJ6PENmGDmWKbhJG1El4izUtE6QTjZILNx7VQKu2LRLajZq5i06TeZTdW9K1AGbAG1iNrn3F61kninUR7J6Hma40Sm+aKuLS9L/o7mDK8eGjxPdbL3Be499Lp'
        b'hCWS6KV09FJJUC4dlDthohnFMn5M4XDcnDIyPqXRptGxtmNrrx6Sd7s4lix7mV25D22CRm2CBpdLbGJomxgJL5bmxY5z2HbhrEcWNu1bH1r4jFr4DKpKLMJoi7AJBY4R'
        b'ShcF48o4WcU2xTFTs1PhbeFILE1pS3eJqQdt6jE2ud9Aycy8N+XGor5FYzxbMa9I5NkTSDvOR99G3J73Bb73wh/E0/G54rwC8bICFNLxhZKwIjqs6BG+vJS5fAH6NpLy'
        b'fBbIupf+IIdOyBcXFIsLi1FIJ5RIIkrpiFKSeqzI7YrPBZ9ez2uBtEf4SNpI/kga7REjcYylHWNxiRU7FTuqujbRdgESXiDNCxyzduhQFfOKJxdw8Cclg05ZQqcUoe8S'
        b'l2LapXhCQ8kbNRUKJhTUcelRMG6MS4+EWFr6aan7Snh+NM8PNbEZbmIzc9KjcOsFilhXFC4oiAp7VknsA2n7wAkVBZwiCsbVcYoqbSo4xfi2eNTeYl4Wul7jggaSiZK+'
        b'ksHC2yvp+Uni5BRxaro4OZ2enyHxzqS9MyX2WbR9FhI+y6WsR44uuMoCxjks/hKWSF/MT+gNuRHVFzUYfjueDoyXeCbQnglifqk4JfVhSuZoSqY4K5vOKqCzSiQppXRK'
        b'6ddjIaHP6wN9qWQhscqmo7MlITl0SM6EEheXCAUTHEWcbxQg8TU2bzXp0BnHUiGyvGJ/wX7MzFIm0GaRvcW9FSMKYtPUe5EYEhyOZM+6Yw7KGS+01/taMJIoRyxRjsYT'
        b'K1h+LkgJoWCC8jM3eIyD5sjxtSzKwgapIZYeVkMobGUzjhyF7RuOBbcHi5aNmriITVzGvH2vLUfy15ooihJFPRK4tSaO2dp3Le/V7lrVGvXI0Jx0gmXdqzpX4TqOaovC'
        b'rabSqSKy6rGV8Nxonhv+Qb1TXZTakyUWRAxqSHiRNC+SCFe0yL3HF/0ZZA0rDikOCm+vl/hG077RU3WCWtDcWmwWKwoXKaM/g7q0X6zYK3acUjYzR432MHnxaPLiMUub'
        b'LiNR8ailJ24vq0HLYcchR+ztNqZXf9TaR2wdOhgpto4fKUbSE2CFpCfACkuPVbdyp/KYtU13eGc4OQzsHSnmo0/6Pc8HfmL+UvHCpRLrXNo6F91miW+zJLfZ0DxXJEWo'
        b'By7uWzzCep4LuCPpdESGZEEmvSBT4pVFe2VNzFFOwRoNh+NzKTMe0WIdSHN6MvpMe9h4yBjXjGqnKuphnhc8e7m06wKJYwjtGCLhhdK8UPRUfyzq/ljUzcxPRbRFyG5w'
        b'7/GjHSPuuT/wo+OWdKhKeEtp3tIJjiquNBSgjmRl22Ei0hGbCsSmUb2WN+z77AfdbwdI3KNo96gxU3OkTsSm+aja1YbURkKeDwfh9+bSMXmS8GV0+DKJbz7tm4+uao/D'
        b'G6JQKzBLtNKGHLNx7MgVVYutU1FF2w3ZjVg96/isi8Q/lfZPFVuvFGdmPczMHs3MFucspXNK6JwVksyVdObKqUqc4HDdcOu6mY+r4oJFtkXKVGdqVzZt4yXhedM87zGe'
        b'VZcazfNA+g61KWtYZUgF6RaxdYlI2LORdglB39DrphSU3hM+2EgnLRPnF4kLilBIJxVLIkvoyJJH+PLlzOVh6BvqfkovKImTU+nkbDq5UFxUKi4uRSGdXCaJXk5HLyfp'
        b'J4jWXFl3YV2v8NpG2ifqHufe3Hsc2ide4pJAuyRgcYnsjEQtEIBUrsQ6mLYOHrN37kCv1bLJ1Ur8yciiM/LojFL0XeJRRnuUIY3nh8qPAqTxcEOpk4ZC5Y9ti5WWf1rq'
        b'ARLrQNo6cFq9yXoFqjeL9jg0EBGbFjPijqqiEBQikQig4wolkUV0ZJHEv5j2L8btmCQ2TUBtqNin2LvmRlVf1WDo7SSJTzwulWsC7ZqAu250W/QYz3mcUrO06nW74d3n'
        b'jTMT3xk/Zs+/wr3AHXMSXIm7EDfm6naD28ftzbyqfk0dZU3gjLImcEYSKgh46BQx6hQxUihxiqOd4sROS0gHzRxNRuowR5K8hE5eglQz3wGpZr4D6th8B6K3yyX2QbR9'
        b'EOoyNraox9jYog5j4yS2jkQ51ujTGCyRuEbSrpETemqeqB5QgPPoPa5P2dp1Z3VmibIkNl5IaCaMNHDtoGBiHSuGZYf0Hw4nUGhk8piE4yRkfpnQxlpvvBhNBo0favFG'
        b'tXgd2micE90ZPaardzTqYBQa+SVJdJ1oXSf8Q8zBmNZVrauOVbRXSHSdaV1n2Y+FHTkSczeJrjut6y77rbhjk8TcQ6LrSet64t9iD8biARi3jdua3p5DmznLRmim7eq0'
        b'IV9kJXITWdGGgl7da0ZiQ/9xStXIfMRrsIZ8mXoZdrDQ6JYvCu+Jp52CBvMH1wzm004htFXoSMGoVYzYKvNeqdhqmXjxMtQaNrZYkKRtJ0pDipfZoBghFiy6p/vAlI5Z'
        b'JLFfTNsvHrN3FNun9nKvqSP1g76hMUEmyLwX8cySZ5eg1whuEhRMKClhIVTCQqiCqxkFE0oaeujNgoIJNR2buY8pFExQOto6j3EwTgJ7StusWb01TaJlSWtZ4t24BsZH'
        b'NxzcgF1lT3crpjIT0XD2CQze8Ta5/Y/ZjPAd5h3OPl0xVcRe1SnpdKXadRba4azB74ZBrGET5jsBgaZwMOMwMZHPRQEhBpxXf4KVLvyRItTItLDoiISINEJHJ2xHBpbe'
        b'MUk4x+UX7sF1qSfc+++YV87UDthstmB2hrkDbpMZiLsU3oB5gc00xiTKnMvW0EKvRxSoU1aprDEzrzFLNO5xHFdRsEaNgANNJiJozHLejBERJMJiekQxihCMWQqYOxxw'
        b'hMPkHTNGxKIIW/JwfxThgiNcJiO8ZorIZpJCEc4oYgEWGhJqUqaCMX33MX3BeBnLy1BznELB3ujxchalqT/OJpzraQGmT+vvW8hEmTPk6iyxY5J4YfaYiYUobVBnpBIN'
        b'RDXj8eZiFD4m4aPI2LGQiHFOgEY0YVX/UjihMHXvOJf8voFF6Zo2+45p2Ym17MZ0w8cV2LqRGIGuS/zXo3BvOJqgMBkSFfVGipaOFNzzEqekizMWiRcvEccuFUfkjhmb'
        b'iTwG5w0WjFiPrBf7JY+ZeaCENL1QOppej3GAtFMkC9VjTNI4J4qtYTxO/avhhNJU2uTXVG4oR8N6nPo9Q2YLkj2xpcLj8DI+vlrFIKlUZOfT2PAcaKcCFyvCerDXddpW'
        b'VDXp3y9yMAJc5xcQ4JxCZel3Fbnvqui7WqE6+a6BvmtKf58j912KA29XmUR9686K+ubIob71ZkBuW06ivo1nQX2b1FKFpj1m/1vUd4/5OaSVLypOe6rVJOhbo1ih0OIX'
        b'Ed+8aYjvEv68N+YQpwllwqKCqvCi/LKqb12e4nvLxf4LcG9fBrHqzme/wQ1LSo14gxPqHip0xYrYHQeenF9P2fZlGIHuvwnNLb3J97fjt2WPI0hCN4zfFgYxG/4wKFs4'
        b'H9OyVVMjEpLSIwh22/oJ5HVaeHhq0ZrpIFRX4QJc4F9zqdskm1qWkW8NZ0t1Elg9Pc98lWlp4HYQqnLlqNeyyhGqo1+Fajhqtme4CeNxqf+vYVWzqac3tiswJ/xhvTes'
        b'S7FnnLExntjANj+yQbIo31Vt7Rpw2Z3FOIJqh6KYsoOfJbMqCUpNfynmWJ8+ZNnAUkw17D+2oEo7Ta1RNc21Pt6VU6JIHQcKD+8q8lnS02ywPiYiR+68INy5Aux/GnjN'
        b'cKgNn+h000HXPIo5JVbo+8S5KF6rF+OISIv3v6Ffz/rUuUry6Otlvn8E+lqYjEWMjbL5EV6/+r8ObV3KZ79rqfhr0daFpNYxuxfjTH5PrrWss/8C11qmLH7xCt9fzbWe'
        b'rn9m41rPpsZ+BjQ9o0qa+frfwJV+ElzFMFaWlWM8CuZPzUJTmrxtJi+cT7Gop7WzlD+NX4UMUxq9Dh1mBx/9EvhZlpPfgn4uK/4v9fn/HeqzrMfNAD3G//0a9vL0Tvsr'
        b'2cszduD/kpd/J/KyQmJ6dSD6p7FD1syAX3gQNsYzIBAZMATsq3ZkYU+Qe9Tg2VA4WBZTVsapzEWpHLr15vEXvE6crj3A0vQ38vc74ubm+nBnT/GOOqcFByNSn6fvv37/'
        b'tftv3h+9//b9oX1mop1mts/fawZj97Vfrk0+/px6gcEXR1dbxccsW6zoudnrzd22f9Ldnaf4kic1d7XWlReS+ApkV0A0uAbvMIgAuMtFSgnYCS+QLSRwL7gFm2ai7OaA'
        b'7W6wG+4mmw/UwX7Q/RTKFvSBnnAgCiObm1Z6cGUcWXgDHma5OYMeZu/DMOypkMM7gMuwluHlcpXhbdDFV/1fWG/woGNGwuzTAyd5vGwZM1z7crUfpa3fXNFRJdFyorWc'
        b'Hmp5jWp59ZYMVo1k3ssY8w4Z8b7ni+GyGQQum0HgshkssobSzG3RGDMwb9mIf4tmPYVexT8yUX8ceHXWQhsqzUBdXeX7n0tdFeZznpjD/DxstZbPShQWMk6JZgStPlU1'
        b'MspqKKoaOcqq1SxDgqfIqoo/fzi8QEku72rThsYK04fGaGCsIh0as6XEVA1MTC1WI0NjpRmGxspkaKz01NBY+anhr9IWZenQeMa4yaFxMRoab55paPzztFR5I8T/E6jU'
        b'6Z5MpONNKT90FXpDY5Djf+mp/6Wn8v5LT/0vPfWX6alOs45KV6L3CTNVlDXEb4Cp/ozK+CNhqn84AnQu4/AEDKpGTPI/dcE+A7YmbIXbGKcm/viC2nw02CWssrRoWJck'
        b'yGTgimiM2xYdCxvx8bi4LOz9AxMPuRQ4CBpUwNBCeIph7vWFgPN4dQS2Rst7P2HonirgDrFFwhsRa2VAUW/QRcFLG1WrPfHT62BDyeSe+Cedj8RWytyPsClwCJ5Sgbdh'
        b'47xqJ3Sjsh3cOUUuhHvRw12dGJIH3JuAJhjk0FGunXJItR65gc+1i5uccoADesysA0MYnWBTAnOQLFVNCTaqg2vVwegGmyXgGGyQJpWRnCXIzIpGA/LYhHhwPj0aXIpO'
        b'cBbEJKTAnQlwrwsb9Km5g4bUNMoctGuuhLX2pNw2G2B7pbsQlbsiL4ACN8B10FzthiPiLZm0YbPVZPKYjLjaXYhxiIRLyqXyQIMSOAxqwc1qvK8f3HUQppErL/nji6UY'
        b'zHTmpslSZxcrgbOwfyFzhP4qvAvOqQk1NZzhLTbF0WYF5cJucrA9CuwEfbAf3lhXCYY3YZjIMMvREOwg4AN2gAKlTI2nUgvyVsawlKky5z9BNFREY8XupesOHwxSW1UJ'
        b'XLV2u5Qd35Ldzn0m4vuIbw3co5d06Smd31n+ofPlE0OPkzZssU5YrhCk/OeNdzZ+ZnPf6y5LaZ8kqvtdSnApq6XghYCWpMrD7Fvv/ePr51suVL+tft/6xq2mbZ1rdy83'
        b'WXwps+i6mkbTK+KuzKQAj48ye/fk12/5MGnDcbubvRsjhg0iPisL7sm/s2jL8N38m8kXFrbWJ45kfed8cck+jeXjMZcaz+e+vCw/JbTNnF/dUcdZWnA2MS5Nr1J4vDT1'
        b'8dqyL97f+nXRqXtKe+/PeTZ941/d33L38xeq//34kh1v9RScbjj/Q9vH6opshTt/4YbtcxWtD/OhP85eHDJ4l/OP2MRvV1J8Leb8021Hlryvk2JVfOwI3MknR1uqiuBu'
        b'eU8qKaBDChc8D6QnpBoWg0tStCCa4rWzQmwNGUcpZ0FPpRT+h+aN+nOl7D/0+3EytSwoB91PeVJBnagH0/+2kKMCluCW76T0KjiCU5RaORse14KNZGd7JejdIJt6gk4T'
        b'ltva9WTiG+6/aer83AbQwGANN+WTIzcBC1nkfO+Th3uRLuDCKxnwNDmBUaEUx+Qdd+s69ARekia8xYmHp7aSczfwdJYybBCgrniniENx57PAxVxFssrgiCb8R+LcY7Ga'
        b'uBIOGvHxoNNgG9lyH2rmQVYf0IS6TbYCYbGMVJc+uAnqHWMTnMH2cNIajixKx44Dj8MhS+ZcxEW8iCsj/sFecAfP500o5mRJk1ehPPIvGvbJCEBS5J+yL1/zd9pAgb1c'
        b'8qaR9uRQVhZPTrtmQuwNMc5exsMD/jXEHmazWRzdenCrxMCeNsAAM+0IZmIeJjEOp43Dxbrhj3TMJ2l33teCR4pGPeLEHnHkqlCJcRhtHCbWDRtXp0ys2l2alQg/jqUd'
        b'TOKDJMbzaeP5Yt35YzrGLQEkosOnK6DX+poT7R46Oi9UPC+UnBmQu9LA/KGB3aiBncSATxvw8T35zLmCFHF6Np2eJ7HLkxgvo42XiXWXkWTFOg5SuwJHL4vVUdVV0xsx'
        b'aucntvN7y9xB7BhxT+mBusQxXWKeQZtniA0zxsys27MxDy6LJUrvWTRoMyoIFguCycWR9wwemEocMyTmmbR5ptgw85GJFW3iJDbx6dUXm4QMejcrPzKZ1xrUsaZZ+W8G'
        b'pq25okKJgQdt4PHQIGzUIGwk6l6mOCNHvDR/LDxJnLJInF0wwWEZFmFrCApxYYrkzRuav4aa9ssbpIhITQek/QaRisC2jkvUlK0DSVaUP4sVQ0wUv3f47zN4/CeBz2r5'
        b'7G+X/CL4bCZrwO9GPbNKJPhr0An681Rh0y+Az2bBnoFtRgy1bAc4bucIL62fJJ+BXio/LIijRlnBHg6sdUhlyGf9SFnvk8GZO5cQ9pnuAkI4KoG1aESCmWYUy6wEI83g'
        b'YT0yzHhlORsvuRu2qOapX9qUQDGD1qPgLkGWEVyZSS4BlnnzCcEnK6wMn/Dcg8a8LpQLPAJ6pSNMbmnlGnzWuInCYNs6Y9jE0HuO+4CdjnzCKgMdcIjwympBHbnLGPav'
        b'i1CcQpax1ecxi+fF5S5psJFBlYXBk2A/FAUzpKBD6P1xJA0eJqiyhZsIrAxerWYyUQsGeGpkmMwxXkmxHDD9iUcR32xnYRPDDZNCw+Ap0MeAw4xBP6kKPYcmypRFrX45'
        b'OM/5R/+tDPHqsIYVhSHkP2rksRUMFzA/7gyPoZopan3G8jyH/oSlfww37Lezohye1D6zg6KGsGWxkSO1LJJCZulpUKjGfdOz8pyiCxczPw5bGFBoNL/gXee8QJdAF6oa'
        b'G+SL4E247Un6F7gE6wkBDFxFo2eyV6J1rq8avE4QX6CvBlO+9kOG8nVigSL2Sbh6EQ9JYawTxWcxNK/u5KXkzDnFTt6CsVz1cM8fxmj7t9U1B5VYuF9W16RqSlex1NYy'
        b'hC14HQyosHzhLXiaRKXCITCsJmQgW/AcOACOLZSBsQbhSSeGtIV6/CCXoLZq4Mlq7PuKZxSpRsG9FRSVQqV4+xC2XjHsgjfU7B3AKbBPxtpiL06EB0hyW0AvvOGgK0/a'
        b'wh7Y15S5fPSpQuV61BnvOpXfWbgo7f1IrSOFLyodLNKsbH3F70iC8i3uvRhN5RcPrqg8GNB7vCB0bohrUWpNdOPS1K653esfFTnOqUnJuPD9e4GfDZ/+R+71TztC5q3b'
        b'b52qkuH8RtAPm9/yeC1+65lbN3Pb3/EKW6Hp7ShY8sob4998+Lno+zu9Xo0f/ePvSRv636uvuHvacuuDZreTR6hDdXlVlx9enOu8870+7fZn4l04Xzj05xRaq729Je+B'
        b'onnN9z57Pmms2bumq8e2zcul4NgivYIDPbY+d958JvSViUpDna+/aB1WOHV9h0e75EUvR5M3ytZ8+ODFL27n7v3wC9VAqBZ8ZOQFqrOVSvnroqX/Y9UX+OFX2pVXlYcb'
        b'v6l5W/CuB7d2p+XC03aX9xX3DP6w/S3XhRPJJZvdD35yPdNC4Xuq7fkdr96PuDi3NUS3AH77OI+3QfmSeMKxdqthkcv920GLIkd7n/l233vxQbcLDM233HRo+vtlifv4'
        b'fqWT3wb2xnf1JHZkvDqQZ3fjuXLF6zGdr50f+Wf3VeUPnu15Rj1lc6Pox+0jay2sfaHbHIXMH9R9LSI/7Hj1qPUDve3HFB6sXGlmdbKs5/v+kBOZQTWXY2vM6/487z3L'
        b'pGH3pD2fSxbevan1DvVnpZz9zwnrqpteG3391WH/W/4mgc7Re78ZeWPvyefFem90elzrODMQkbVz8eXTA74/VoNhrezv3l//6b23L7LfsXrmRnhv+Ce5th9vYn8R9jBn'
        b'+1U7lQdp4YJ7b45pXRQPX/3+0/FPXKLfW+/fa7wiZ8WDBW+X5H+hGl9bYyx+ean+5tV6Ykf7tq9/eL33H/vSTsW/fHrfvKA1L3efV/7eRevHdI9Dr33y3MjH51cdfpQD'
        b'v/94vn3wff5reo9j/vKn52/PP6lUXfTZg5rMKJfKFzer7C88s/GtNzUcTfs15r/8z1ilIsWf4LyDux0n5qdmXNL50aR2K+eLsA+Or39r25i1louSt73o75UOl7xEXyac'
        b'/+SKQ8vLW88odlZu2NX6ysXtn97dveE5/jcPF758/2v/lG8E4CfFFHjc6i/ZYMPx9vsB/IVva/TELT8h0NVLeVkw2DDw3Gan0V1OX90Z+Wz58FdukbFBuyQvLDU4ece3'
        b'Yb/7W+ZfK/VuXVD43EbDF15b+OEbB57RGDr1aLDrB2uVb7d+Zmcx99jyq1/qxGbVx4iqbOLZZxuef95xicrRBR+9N3E0a2juO8PpQ1/7H4q9sSGnWetoxpDFsoGujKFU'
        b'm7qWy+8Zfefb+3FD8+c6nU2LV5rtsLP9otsq98Oev9j+4/QJwb6m148G2L9d/ubOq38Jfymg9icP8FNN2xuvDwqXrHxP8E6tadYV6ieD0r8WPjD7W5z6c6vORvKrv3DT'
        b'NXr18Nx/9O78zkE78cfiZ3zULF4JSTv54JR+0o8f+G01eL/YtvAHYxPWTz6i4fe2NJRwahssF0g0RW97ObzdXCS+sYS+ddXJ+E7Ug8u7v33l7qKbg4t2eM85dV5rwGIs'
        b'uPTL4PM6n3y/anyL8tFtP4D8tA992DsTdu44GfOXF98tXxXnN6zWE+Z4/1PV9BqN5x3XLo0c0GnxcaqJl/g9fukFzTUeQ/MGP7LI87qf9PcjmYF35zxutKlOfsCvYKaK'
        b'17Lg9RlmwFxwnBCu0Ft+J7Ndrt6vDEOuCoLkwPtZAWRi7htr9aRbUu7i6qXr4ACZPefAwzwCt5JGw0HYTvBWmkuYA/cHssOnMakIkcqhTAMOsUn6VsvhOaSme+SxVGwB'
        b'OAabGajVti3gVOXUgJAFDiQwTCp4Bhx6zCe5hwcyK71BO8Ol4sc6r4nB6BoZmCoA1CqCfniXWSpPtgHnQ0CnHJiK7YCe1kIi+XrwWhk4KM+gYtuA/cEMXaTVYmWck305'
        b'vDaJoGLX5Euds1bDZhUMDhEETSGo2EmRqIJxKRwUMKtCiqfC8KkEcFXKnwIX5zNn9A8n5MMGZ4L9AD2wG/On8kpI85hlRuGbUxJl/Cl2FhryHiVmmwXea6bQUwx4Cl7N'
        b'weypJVJAgw04SOmCdjn4FJsDztUwhhmwDeXgEuyUh08x4CktcJA0MCcF9hV5yZGnGOoU3AlPMliVOjQyvE6wU1LmFMrJcYY7NQf2MPLVZpau5hwHbrtOsqPY2SuDiVUp'
        b's4xTmchQo+Al0AdEoHUjyZuWEU+OGsUgo+A1Qo2ChxNJnbGj0FBZusczFDQSI4tHNokqh9dzQKuCWqJAHcmIAjjDgpcjGafB88GRDQxGRsaQAX25BCOTiKoMG45UwVlw'
        b'dDqKCvSZSGlUaOB2WuqP9xaX4KgIjAo0LGR4VL2hZEuEOzwPDhMWFZ7BwDo+g6My57pzueCqZxXpHeXgBKgj3CkCnUKDdREDnoL1QaT2/cFuSwxpkkKnKsF1hju1EOxh'
        b'ZHIXvAxbMKMDA0quoo6NISWrSxnw1MFU1PUIZImlRtlbgtugg2FHgX41nRXwnBx6itjN1sJWBqDRvHQR5k4R5pRSCqZOqYFhcqfz/Gp410OeO4WhU6ANiSMu0KpwcApe'
        b'hDenyFMMdgpeg70kw3ZwAHShEq3ylYKnMHbqCKxjDF9nYd86NWc+T28SPcUuWwX6SdIl8CZFqFMMcgqeM2KoU1AEjknZQmhKdwbuBvVT6Ck0bQnbwqB9rjtXqIKL07hT'
        b'LDgA94FOpia7wTlwYtJTh6UTpk6BEwFM5JF4cBT1AQY5dSeJUKfK4RHmuUcVwMXEJZPcKQY61QH7SV0GrN/K8GUSnVlGawgkpgyeYvo1Upb9BEVHiFOXwElweRU8TrpF'
        b'/HoFNC9giFPlpZg55TmHwbmchC2ge9JZiy/Smpg6pQ62k8dVrYUHpVMAVOtn0SQAzap7yZ3ZKXPkzL+wT5lgp8AOcJ4p456gOPeKSRYOAeEg9bDzMZ5UC9Ej9z4JnWKI'
        b'U9lwDzxaDM8y2mBfts1TxCl1F8KcgmfXkfoSgo4FgeCGPHaKhXTGzQhGDw4uh3ul3lpswEVMnWqE+8mN2UhTdVFwlxx3irUUHkGPJvnfAW+C3YQ7RbGSkFLC3Ckw6EO6'
        b'gmI+mjq7MMgpzlYGOlVKEs1DpdyFmVPw6iYZdortB05tIOUpBwdyCQEHdRS8YjEQz4L7SihD2Mt1tAfHGandVgF2ollCovnUHAHchifIg1lwLzgrtVzD6zX5LLc1SNgJ'
        b'NrAJ7FiNpi2X1GRpY6lUBQfZoAdcdyYS4oQbD1x2QKkT2UMzfqty1JNw3PrF4NJarynaFWZdgRM6RHem2bIrmfegyiTnykwtJ4ALDmyBd4g0RMDtWkh31MnTrlBvUQZH'
        b'SO64oJZgKS/I064Y0hW4DmqZBYELWvMY1BWab1ZnsgRgRwTRn4Go926fzrpiQFewOQ/NpQaMyO2cTHacgHnf7YfDGHXF8WPGDA0xSHbJcxkylUUcw6aCoo0k7xXgBIss'
        b'ws3zm0RTscFheHgF43b9Aryk/QSZCp4xmIJTKYJOPmhkkDtdqOMfnqos9N7JBVfgDk4VuAk7yf45w3lgNxbWOL4KrOfHMO93W9hJGYHt3ChwBOwgYpDkH0Gu2uTEJ+VV'
        b'gu3sEHihhKHxHVyDFB8GUUkVLms9A6I6XsjE7wP7Q2Cn7dQSCLP+Aeu1mV5xzNaVLEKg2hLCWrwI4QwvMYrt6OKSSvTIJCRH+x2RxtWCd6prOJvgqSoSrwVEGY5IAAHe'
        b'lbc/DuPf4TH2RlRJ28nrcHU+GKjEvuTq8EARF45FaS+eo8fZDBosHrvihx8qZRClT+G5EnTlAV0EzwUvp5Bk85Bi2TNJtiJcK6WVhGwFu3SYDtuD3umrwJ1J1h3h3AmW'
        b'MJFDgXAYx6AOm4BeXJinCLZJiaqZSDivMrchrQrrwBmG5de/hox7wdVFAkewP3UmiBhhb8Gbq5jG77GHJyYZYoQflgAuMgix/jRyiVm0payLTaG3NMFRTN9SKCcdMQWK'
        b'4DE1e4a8dZBL4Ftwhw0jFCbrCHrr6LxJ+hY7xRF0MP2neWOJGqFUceYKCHrLfzXpAIIyBXnsFoPcooKQKqlzIsthbqgyjqnxCW+LA2vhrgUZzErcIdhdKUNuMbytNHtM'
        b'3AJHk0h+5oFzJbDfieC2QFclQ9zaA3eQVJX58C5GbiFNtX0Tn2WeAruILohcjnTuE8SteasY5tZ8uJfouezFEbAXHJqkbrF1wG1romCN9PGiOerMHnC7DLrFBkeChaQp'
        b'rdGgpb7SxSEV7p6EbrGjYR+8TOQ+aUM6OJEox9xiwcOeoYz+vKEHhqfxthjYFgd2zwW7ikjqOWCg2ArsmyJuEdwWat39TPtfKURal+FtMawtcCODwW0lAgbYtRSJ8VkM'
        b'3JLStuBVrQRWJLzpz3TLQ2xYi4Fb6G07CLswcqsJvcBJtzzvAxowWQucB3dkdC022D4HDYH1/jiWFm6b6dZ4eZAWcyxdf2ZbHFm/+0FVegwpPfB3RWiZiA0DnoZlNSuM'
        b'K1I8y38zBMtx1NBRYiigDQU/B8HazMIQLBzOCsGa7edfCb/SPabZrvm7w6+kj5NSMzpSutM700W2p3O6cpjawRFxbXEiFoEvpPcsOj+nZ47E1Jc29ZVCcjoiu5Ikpp60'
        b'qedvQ1A9QTbSbNPsWNu19aFd8Khd8IiqxC6OtouTGMbThvE4j/8FSf3/HiSlifONe4K+xNCeNrTHYqHRpiFXMVIGkhwtJL0nhxYESezn0/bz8W8qF1Qw/SXqQlRv5Pmk'
        b'niRUdRjigoIJBQUMCEHBBGcGQAhHDWcDBRMpLE9MofLEFCpPTKHyJBSqlQyFKpRQqEL/dQpVeWf5b6NQTShwcGZRMK78+1CaYttiO4RdNbRdyIjw2Ro6alFrrMR0MW26'
        b'WKoUcGoanRq4yqM7o1F2smnBAloQIbGOpK0j8c9xnXG97GtqtGsY7Rr70DVt1DVNnL5U4ppLu+ZKrPNo6zzZVUoSa1/a2ndCSQHXvQKueyVcHBSMa1FmFr+G8mRm0Z7d'
        b'nis28+kN61UapxRQqVOGFw0tktbXI0dBT0BPMBJYmxxWR3FHRa+C2CZt0G3YZ8hnxP3ZgGeDJQFpdECa2GaVOGvhw6yc0awc8ZJcekkpvWSlJGsVnbXq67EFIc8rAsWR'
        b'Nc9Xgap7CZKoxXTUYsmCbHpBNqp/nHUOzrrCfJR1FKC+9l8o1H+hUL83FGoRyx8zofwxEsofE6H8MRDKH/OgcKCN1c949H8qDuq/FKjfQoGaZbi9V0keAZUQ+H8aAYVZ'
        b'AEIdrhQBxcEIqO/x4r7uH8FvqsTz45nQTUw9/oTr8UmQyruYobXkF7FNTrNhm5xmwzbNGFHMRAjGzCKm05mipz1DgCMEPxuBEUyuGMGUwuJjBBP//2PuOwCiOtb9z+6y'
        b'dBABBaR3li30DgLSexUEEaQqiiIsYO+KYMW+IuqCqEtRV0FFQSUzJpLEm+ya8+LGNNPLTSK5mp6b/GfmLAjqfe/67n3v/WWdPXumzzfznTkzv+83hIIph6Fg4hjYj1KT'
        b'nHEKJnxDd4zxaOaw4z9BwORMKJb+a3cyARO5nzqZgCkQEzAFY/6lYEy/FPzfYV/C5cwk5cwkeWWyHsQkqELQ8zzcACMQX8zFZR5LZ1SD3J/FrmJjhqR/p8uAUPCaOJDA'
        b'TndCtASbBYkpopqEFDiIF7UELMoN3OQuyZ09CflmqP5+FIH66MFpT1Ms5WsQYiKdAyYVbOweMFRfm6q/dZnvSk4Fp5czmdSozJlYGGL7QmxvqN9k0GTYZNRk3GRaoV+m'
        b'8QxJEZdNlWuWcbdQZZq9Wk/RI2kRP23kp/OMnzbx00V+es/46RA/feRn8IyfLvEzRH5TnvHTI35GyG/qM376xM8Y+Zk842dA/EyR37Rn/AyJ33TkZ/aM3xTiZ478LJ7x'
        b'MyJ+M5Cf5TN+U4mfFfKzfsbPmPjZID/bZ/xMiJ8d8rN/xs+0iVvBKnPYop0/jVw5oqvpTRSSJQdJUrNJu0kPSXIKkuRUIkkn5G9WxiY2sS739aMiU7Kj1VjMjy6zn7Lw'
        b'xCZWE0MwTFLjBkJ11XbLimvFTBg/bwHz7YNNjciV76TExiCfYpFd5ATbRbUpHqGOUBv8Id+68lpMaGFX3VBei35Ntj2cgOYVC+zKi0sX2tWWL6stF5cvnZDEBONIbKM7'
        b'KYV/ZH00GXg66UdqNTY6S6hAtSOo1uXlteV24vqSJZXEjKpy6QRGDmLXhbyL0f+6hbXlkzNfUl63sLqMkBSgMldXNZQTiGw9foJXrcT2YRMrKLKLqSSmVm6RPLXlcdVk'
        b'AzRsp6U2YWQE4aGWw1iLC+zcZvHGghXbicuxKV1d+X8mJCxDtygepvEonmCuqDYUrK6tXFC5tLgK80moCQ9RE2CujKcqKhYXLyBMIuWYk6UKW+0ytbcrK1+Gpixiu2qm'
        b'4MTm0E3tNwv3sCXV4smmZ6XVS5ZgC2vS956yb0zlse9zViypuq9ZWrykzs+3lPOU0iSIxQPIOajPmFcfpsjw0ELKjk3MqxmFNwUNHaMmVoUhQU9z2FTzU4bRazUIeprz'
        b'DHpa4xmENGedhho9/Vy/ieRXH/3K+id4hyYNxX9sJ/ePTCdR+zBWk3NSktVmf3hwFJN0n0geyZiYxqKB/Xx7WrdypkP+o1H/n/DhEOEEY1qT0mKkN+ajIs1nzBeZxMYT'
        b'mdh5i5c+3/K4rKySMXZV5zup8+JuXlNfrlYA4no0MscV0PN5QCaZBC9fWIli4PFbXF9XvaS4rrKUdPcl5bUL1KaR/wmjSC0a18uql5bhFma0wqQR/Z+j28cBthPQ7Tap'
        b'YrwhdtE0uk/5E5/XXcd7lXd5B+/ti7fiN4qpyrXap/atYGYVIuTAs2CnFuiDe+EVjK+o48FmHrgMdvDgIXARnAZywEQCp+Bh2Ee2ALIZ8K8cXgFb4J560MOlqHXUujWg'
        b'kcFpZ3MIS5xng2TO8djpFBP6AEpgyzI/0IeeGyFUCNgKDlX9/Oeff7pbaVAolp1ng4vVuvpIikBdZ8HNXuQMcXjAxx1c8GRT3CBWusZqHrvemSnzIdgphtsNYfNyBoWV'
        b'nCrScYfbktxYlDc8oMm3iSXnEMMLuf5gJzin54482CmsgOBVKA28Z2ynrTcxAV3ssCiHYHAJnuY6gC3JBN3rGbtej/HhwGt470oCusRRKAl8aC88ARph76RiJLjXpPLg'
        b'BX6C1qokEQaD5UCJthXoAlcY4H433BAJ+/gJIdaMt7Yfe+kUbR6HHNmNt5gPJaXCnUK418cTHgR7/diU/lr2YsNccmS3zzTBuK8tvOSnSemvY1eBK/AUiY6mgq1LnkRv'
        b'jPJjUfrr2UvADY96jFuDV6diRAWxiIzHwTLiJ+DcqOgpWvCEg1k+kqgdRU6R2wgvM9twGUJ4mewLmoDdHL3Z4EQaaK6PwUnenGE10XrCjYDy0lG6yUlJQnZNGDhmBa+D'
        b'7dam0+BFeDHJFGxP0tOFF8GOxMwsqrzCKMAaDpJOEzVP3Q0q3uTPKQqm6vOxpgRHxc9JHhuleiTOdoPN8XBnFrYGTZoN5Xwu6BvrwMRyIy2Ba+ysC7eCU1wuvBrjDLp4'
        b'VMxyU3gMymJRi+Odqjx4vRj2TVlWi9ESA6zVDi5gv8OYqcI1Sk+7tgFJXoMFb3i5m8QSEfrCm/AI7NOvIXF6WXlgr1MRPMGIt3U2OC9eRuAwHH0WkuCW+QJwiPGTZIDj'
        b'4hp4UR/H28ACZzScloCTqCuR499zMJTkMkkUDLHAwTnTp8NdxGumr92E7OA2OOgE5K6kQ6SBIbBlXOJrXdUChwP69QHI2yMa3sS+jNBhU4owMW12fKottoUkMfzULQo2'
        b'wD7Um6v0gAxcXFFP9rSlcFPMM5EpynG1ITykAQ/AQbiBlAHctAZbs1A60eAqFg7SSTosJPO92pUP165mi1no6eoY/+2lnLmLTSJNj7+fcvFq1f6quwWt3bsO5wzN9biU'
        b'GfPSH6ypj1/+evPml3kH9kXv9dZ7+Qov8kS0XHfla0m2f998vPe7d468k3CFO29OoM+jYw/XiN94551f8v+IrXL4usOxu/RoS9SKP0OvX164q+mr9umXYhZ8Q91v/vzH'
        b'kHfPdq3YVrFvRVP+VOvW2Sc1t5go1y2JKU01P7fLqmTFwqX6X0Y9ln5nlfD9yGKbrSpOyYKSo+1hr7VKXhm1SX30l5gfC3OLa3e1bu92qQaN+v3RYcFRr4e3DX/8ttuJ'
        b'c+XHqqqGttzhNjxY5trvHdmQvuf7ttGdOd+7bn+jg6d7ZfaxtYff/duNPbuNvvzrqh/E0985Z1hkkJ9Z4b7oVtr0x1u22YiWv5PsW/LZCDtl2s79+1dvmr1r4Xrda4ei'
        b'H/484/TxW9QnVWVRZwIiyx2bM5drzkzJ/uhijvHNt9Id33J/87tZh+Pzy7jf8lbPynot5rbR2dX6N1fCtt6Psrsb31p4LHLxR9GLkvXnnWzt61r0Rnv9ByPL7A8WK7+8'
        b'YvoOvVX5soR7g34z8vgXKe8Y6A7N702e9nmW95uej+Z+xFP16B/vKJj191u5Bxcc7pi6MF9/u+JK39CIKK7vflfeu6+Zr/hr8MNlCf3h+frLrS4mXsj+XbTm9epvAsOh'
        b'R6jWL9ccVgZculMU89d8b9ePp/z6J3fg3OICruO9XaU17++sSnmrtizS5aaWc2HJlWXf+ucv1/eqCG/5wMbtKOvE4Kv1Kw/5f9ykU87fdzssqu3znKbvZsOv7VqnNywu'
        b'5uaUiBot/uqxLYh/YXbZ0IlPG787MLUn4VbG7I3hEetWRBwM0//gk1jX2YsXzoZVPdc7d6cWNL8d3n2r9dO9hTrRpc5vo+h//9GWv9GrM1HauHy/khP92/Ui6dfFvv4f'
        b'Wiyce1ajzXxjf/CZE+YfraXN/L5tuGv0x5d7m4uu//LNb+/+UdTYKFm9uEewNu7no2/f8Fjz5TazjVoj3j9lczfevr7/u66b0m+6HBd8NtzxyPuTjT/47A9cGzY6PMT+'
        b'taYszWXbm7yVsS7VxY8C7n5jdW/Bm7xIBiC5ew04FIaZs1LYaJzLWEngerUawTQEboId4DzWbUjjwW4gg9vZlB4YQqMeHGNQZfAcB1zRz+MnJGuh6E2sMNgFdhPYwNIM'
        b'eJpBNINLK8dAzfAa6CMojKDVYAPY4QG6BPAwaI/nUprz2Q5gwI+Bk8lMFqFB3uyRBgdjsQHwOrY7aIaD5KQ8MYooRVExHjZZBJrTCKoXNHnEC9zBINxHuMq0qCI0Pzgr'
        b'BDsZUEhXNMZgqTHaouqxA4jBDtjCHOF2YGoARkDAXRHwglCT0ixkO66Fu5nSXIoC15LShAkCXmA2DzdAPxsO2TI4FXAyEJx4Bh1eBi4XrpxCQEAlsHPFM4bfGqZgj3ao'
        b'Gg/qNkUg9nBHc5HuCfCPxWrwBdyJORoI+CPAYgz+gc/gYyBCG8HROfwEcBZNJTQWsMApcAM2gm3BBB1SWC3CiKVJ6BDQkT0DtmnUcMEgEZ+fl9UT9OWlEnAO9sIjBO4I'
        b't3FjUCsnpiQJMVwyVZ2AE8q9H27lhgD5FAIgscyAN8RwVwIWR5JhqvcKIexPYlM2sRrgVLgZaaOFoMMN45j36KQizwrYifwNYtjwajW4SeBlYEssmozt8EgVClJwXrAD'
        b'XFHnZ+elAU+lRpK24BSFMzCWetgxjmSBO9Q4YLh1bRrYkSZKTBEk8KpSWJThQk4g6LElKJipsa7MvAFDdxxgDz4W2I+jVQIPM2Dgo/qo32J4184ksI8Ld2hRmjpsfdBj'
        b'Qw7iS4dtlmJywCFnMWtB5prsdQT64u0Bdo8jVMENFuiJs/SOYKAvA2iq0jKOt4THWfDETHAcbAK9DIT1OncmwQ0mgg5djGLlwlYWGhwnGcwU6IE3U/VESeRIwG4W2GYA'
        b'TsBGeIy0VjEHPbWfi0MFA+AiPBybxSDOT6BpQZctc0appvoQ0gZm1EbHhBAEKWgVjYFI5wUzOR8LB/sxcBCjTznwKGsJ3Al2c6cRAbiAPnJyKdzDxwXrY8GjbHAGbF5P'
        b'sFxGM4vHkdZId1wFQzamJFoF2OemNoCAe8QpGHd8jc2qUcOmwDnQBTeAltlqzK4ey45dxcCbtgv1sETHALtBoFODMgbnOKjyu8F25sjjGyhlOWFtAGfgQTUWErSyQXPy'
        b'XKLHasAF34kWIFyTiUece4LjTO/ZxwNoDsVX45svsYCsHpybn8lk0gF7wBDjiydzi8FVniZlWMaJCQQtj/G8uxQ0Y322vAH2G9Q8mR5imkEPuDveAu5NEaIoWTHahiF+'
        b'DMD8uoaLmK9bkIEm6jwWpbWW7VsINzNo6iE4FCvm1yahuRiBbGmVs73Rm81mpjAbKnCrJGBIXxof2zxwqWmwW2NN/tTVDKow3Q0e0EPJgvZcdXzQzQ5byhy+Wwf3gF1j'
        b'8ZH+hWdgsxZlmMqJWIsGA5ZjXQHYshoOiBOx+QcLXmEZ1S5gwHqXkXbYrsbcuaeiaexpXeZM2LNw0/wJmLuV8Jj6mEsuPMSgxE7DFnBqzMqh2hs9Sq4BCaN6z4D+XHAV'
        b'dpEzWskJrbAVbiEwxpWWoAmVFZUkAY1MooM84uEuDuUIT8Peam4AOBFJxlNxVb44lac2ekkC3YtZlJE1JwM0WTON3YZeSTqx8QE+9ToJ7kf5DbKIV1DEOjHTShywlVUK'
        b'G1ehpJtJyUpXhPAThUlC91TQBrYgjTJlAac4QcycQXxOLJxUMkwb0oxByLxCrqk/OIqP+X3sTp5X7eDg87sGvKKd5o9myCHgnGaqYQPTHBfS9SeQdq8G7XAzvG7NoIJb'
        b'ZhXqYT/mUQIua+KjUq9xwNlKDjN6B32N+WiYVfnwUtBTTBsOssFeKHchwykJvVIffg5aEA3AFuOFdjzL/40DSf6ZjS+sQCetLzxv/4swQk6buKQ0mQPzTS7DurFoFtKN'
        b'Ni3BklKpn9KER5vwRinO1DiWaobVCZdWF4V92IB4OEo5I56eEd8S1RL1YOx+6EDJsKNyRiw9I7YlSjXdoqVU4iip27v0wNIWjsrWoUXjgL7K2q4t98S81nkyH6W1B23t'
        b'IWfR1t73rAPvWgcOmCitw2jrsIES2joSBdbF58PlM6A4JjC5aWJGmwgVJn4q/+D+Rff8E+76J4zwlP7ZtH+2wju7JZo2FT2wC1HZBansoka1NCyMRynktHBHdSkH1zOW'
        b'HZbt1p3Wo5TO1FDi7E1oiZKYqhxc9iahi+nvm9lIxNKoMcIQ7jQbla1j26p7tr53bX3lWUrbINo2aJRiWQhVPIEkui3xfRtnaSmqjY0HbeMh4bxv7yYzkVUo7f1oez+J'
        b'psrcWsId1UPJ/GBIWTornIOVM0LoGSEK0xCVhVXbjBZNlSOvM5R29G3RoI3sVM58WWRnXmcB7eyPbzionNxlXp0JtFMw7RSucMof9h+xvxVER82mo/JxAHuVnVBqIKvo'
        b'XUqL1PAdwkNq7dhWRFt7Kazz5TkDkf15A2tGKpTh2bTfbNovn2lbR2lkW15bIW0toq19aOtAFHYgdthrKGEolQ5NoUMz6dDZdCgT2MpB6tWW0JZKW3nQVsG01UzaKkph'
        b'tWy4YaT41spb62iMfymn4xbTcctQeJ0JiXsyieNUHti7ylidFp02tL0PbY9vGapsbNGXHgqPoZk+xGmJUVnatQW3hbVEY/yATpuhwjxE5tTL6xXQ7iHDGrd075olKswS'
        b'CZ/JHKVNHm2TpzDPU9m7dM4YpdjTFrEYV8JVEeBVfds6paWIthTJp9619FZYer/vIFJ4LFQ6VNIOlQqrylEOZeXzwNS8JelAktQH/dV3rmoP7wxXmnrjWy1JKjsX0qYO'
        b'HlKhXFNe069De0bQnnG0Z/JImdIhi3bIQv5T1JKQZ/YuokXhtCiWFiWNZCvtMmm7TBz/gaW91L4tqC0MdzsRcdAoMZtxoIE2c6XN3GkzD4VPgsIMf1RCH1mOPKo/rj95'
        b'2PGW64jLLQ+lMJMWZko0aHN3VK+2MNpSKJ9+1zJAYRmgsrJTWIloK5HcQWnly1ziXrse99MKlkoUIlsyEDUUO5REhyYrQgsV6Vl0eg6dnkenFyrmlylF5bSoHKNBmN5q'
        b'QJknskaNKHcRHkwun1k6SqOl0bLpcnbvjF4bBqCltAyiLYNwJTyI83RN5OEKs1nooxL5oibJ6s/tLxj2uRUw4n8rXCnKokVZuCL851YE9TAPubcSY37wJa7IWlyRMpZK'
        b'ECRLGXAcchni08GJiuCCkdI7FXcq7yxVFJYoBaW0oBRVImW8ElG4EnwPXAlXlbUtozwsRim9qUHkBIZ7Zvy7ZnxZotIsgDYLwIQ5aaz3bVwVbilKm1TaJlVhnqoysyf0'
        b'Q05KMw9UK8zA466ydz1j3WHdbttpK9FEI9zaVZIv05Sbysvl+owCw0m5qxzcpObIG6MBNaYFEUfCUdm4S6qeaAukFdtW3LP1vmvrLQ9W2s6kbWfiqhax3nfgS3kjpncs'
        b'RtCfIjuXzi5QoI9gntKhkHYoVFgVqvwCJRptulKfzplKc2+FufeoGaoYqd2o4ViGE3AoUxkcigwDNLo0/nlEyn/x5MFPliesPP/s8yZBGx+WRTGUPOiRkzaLxWLZYkTK'
        b'v935dyFcCDKnQyeQGjCM1OS8ABNxxX/FRDy5icZoiM9iAosnNMReYzuzZGtTYFe+QGTnjndXRJ5+PmOU8s+yEr9AORfgcnaxX7ScclxOvD3NlNMSl1O9DWhXWTapRC9Y'
        b'mC7Wfe2iUmaX+MXK1IfLdGm87ewJcShhy6ywIwli+tt/oWQ81n2DovE90qLKFyzeZVw87fEmc4m0q19aWVNf/hwW3f9eGRcyZdQvGtsRe+EiXsVFNB4vojtuQXEdakKy'
        b'2za+0favFZP0OIMX7nFDk0eGKKsaH7SwtKKaMBnbFZdU19dNOrfhv1s+wiF+inrR8t2cXD7L7MnnDPw3C0PUSO8LFwbgwpwbL8yMJ4WZlRD1r/Sv2gsvXJaXJzVMbR/1'
        b'4ozuzqwXzXQEZ+rCGmsAt+znnD4xxu79L4gGDTddQlNchEmDX6yIr+OnId4/20BJstuKNkzsOISLmFFe/5oy0GZKV1f9YmV7Y7IqtVDzWv87SmRQVFJchQENRdXLype+'
        b'WLGUk1VoIC4WToXZf6+aCAN6mij9Xyy14XipS6uqxeUvVmwaF/suNanYOJl/qdj/94e5LXz6MLfxlpyAaOCkVlaH1bPEePGp7pOCJwezbbIIfIvlsj3zMPvTg6/xWGQ1'
        b'2By0wX1kjfLJ+uSCRaAZbsh7znlsrpgG0vSpmWZV+VL1wgZm6sKzzKpYFmVudWC1wsjhBY9e+8cZ3MNjdwGlBmAvjmX9b5y79v+Z+J85y+954tdIza6sMAlgiXEbP477'
        b'Fcvffqsp10uy0ceAMrzBnv1ZGCOQZ+W7ivWcN4mS6uoqtYD11QKuJQJuqXtB6f4nyd+fJN6a/wPxYiwbHhGP9lFjWDYkYA01lk27iaU+LIRBs1FNU9RINjYS/VMHgqzl'
        b'6DxHmM9i25B42es4atE/12/iMSGTRY9F4fOU6G2ZYxyL4uB1cQ3mIxyDTzjZAAnBDwWmcintNc1szMM9MnUqw9cHN6faig0Xgqu1Ojh4B0sEe0E/AZoU5GpQ2qFTOCh8'
        b'cnyKBVVPGAc2zVlANniSYBfYS3iZMfX5ziR0kYoJ0TPTM4U5bKowQgu0w9PJBI9da2ealIgBEmD32M6dPTyXhMrjXsoFPXAn6CHIj7Vz4X7xMtAFJWPAkPngBrxOMDss'
        b'2M5m6N2jUYwn1BKloJ9UxB0OluLdp5jMJLxPpiFkgbNzzMaIywfhWT4PHg8n5J2YuDPfm0ECDYJW2IOX02FHmtA9Fe8tTFnAKY+GG7NJ3EXpenjlmucOW4UJGpSOFhvs'
        b'pnIIJKYI7oK7kxIyYAcmhdDQYIETOWpqz+vgpgDvvoIWMU+oSekEscEpKHci1IXwAop3E+4QYS4pQhuBCaVmwSsEJCLEp2vCHcJUZl+0D2zRnMeeBi+AHfUuuLwn4Tmr'
        b'JLg7AR9+lQx3kDaHR+YzJNP8MC7cBS4JJ/VtvbG+vRP3bd1JfXtyzx47/OZ/p1c/o9B0n9Orhamk63at5oZ+y0FaBXXF97KrKdL+M43hbnEqb81ywrCE2ZX8YS/T/mfm'
        b'w33iBHfUk2TEE3NUwJ01pP0T4YVS9f6JWtrwGOwqNzJnxkMj2ALbxcmpcFc6s7G6BrSYEqBTCgdcFmM2DB2wl63NsgZdYJDxsAJnGV4cQ3CYXcjyqAbHiTCRLG+wMCFQ'
        b'EbhJOIEIIRA4C/YxXJklsYTLKTMH90rM5QT7YQ+JmR4LdqmpnPTh5idsTtIAgiusxypVRwCHstC3PQXPL7MH+2N5XAZndKIE9qsjw8Nx45Fr4skgWw/2wauYTQlejCaE'
        b'SphOaRGnnsAGDoMrCyZQOREepwwwULIK7GGGUn9BDWa9UjNEZYVjU4ul9XgfZxZo8eOjLEU8f7DbPUXEEyamsCgHsJUbBK6Cq0QwkaB7FmFjMpw6zscEu2A3QwK6D55x'
        b'ZTg/QHcsykBTm20Gr+gwQMZLCTr859CGgMvwJEMdogP3kpAeoAlsJwQzyWTjnJzSsB0PJ3AIHKVccrmLjWMJoDPVH1zBeI40duxk8pSJtCSpYKMWbJkPN5A+Nx00Arl4'
        b'WerqmWMKSht21pP9z6twDzg0fgAFo56qwUlwEFyLZuiPB+HeAKwHwSGniapwXA96Tydt7B0cixVZkhPSc2OazGwd0/xnhTNxnPZ6rDcwMQ/cAG4yHXcj3CDARDT4/AY1'
        b'G/5iAWnYNHAabmJ0SjTYi9QKVilecHu9mtmreT2mtwNDoH1MG4EhPVJdDSBJRP2XRbECKbg9AO5G4hpkOJp74DWwj58ihKfhOTTGNIqRUvWOIkWZbmGG+le8UEAICw+x'
        b'c4rXFEMZg5XshvtEDG1LYNxE4hbM2gJaF5EObIv6SwsTCKnuvjEKJQdwg5yjjvcL87AOhOdB9yQ9+EQJwhZcKqaCN5aAAbADXmzQQANyBgvKkH6AZ0oZdubl8JgYXkAa'
        b'Bx6kptmAltnwCKk5mgUfQ3Xcj3wEFNwHTwvA5gLyWLzqo9vwFxYqiNH85NqADIZN2MmCXViH6XCp+YLSacuYm9cF3OlXGK2lvww9R8nN4VADje846FGaPl/whbs2c/OW'
        b'nk5+GMsOr/JWxYWETp6csMf0Im7AJKRG8VvTPDTvXMNaxiqjcqjDLBa1U6dsfLWHzMnYhOn3PqtBjOPbMa9Nv+qELihfWr5iWe3MVaFPLxrXldcWFT2h+SW/Ccx6AvXv'
        b'WOxyHTRlw4xOX6K/DZQiej7+ZGUPZwznjTipf074MCjqMORUeuPHNMa07BemV4oSCKlSYka6MCf+6ccaEifoY+uyKCSKbv35SJkRkmZwAwzxkAbnCeF2NTgGjRPvOspq'
        b'tgboRSrsWqVW5Am2OJeDZPeh7HpuUtq7EUaFIc3Wt1fetNu4ZVT7/KGZ7csivt4a5bz7YMuqiLA6ve696Z/Fh0nft9yWf0p4WLfrjFV3wd2o9SW3m6//GGwil2U7jX5z'
        b'J+DR2pCQD1psP7fPGDGoCdb6ND/kj9ea3/rG5JsF1M2oCx9vf+v0a0e+vt+wvbvglM7xwDRQNC1HJ1YQM39/cvurjSPffmU0++8H/77d+Uhiltl8LXO+fW+nPPPGDxfW'
        b'xu1u/DnaP+3Cgbcu1q3/9luHV431D4in0af+bi5fOHV61ByL7Lz3qsTelr92Phx888/3pj5I+W2o/Zteea12KW9TrGf6vYivP1+7Y3Fyn+7Cwlf+EuJcoBWt/Mm25ZN5'
        b'xyu+atHd2vp348h1n668dDT54WGvgoH7VEWD2+c59rmr3Wu+PtcaEfZll912v57gr069s87gM7r3V6f77+tFV4yONLv37OhbPOKY/Ocxy4hTxQODv3zfpWBnOZqIfzuS'
        b'q7T6/dMdI69q9QXwewdd+pz6Xb5r92vdvFi4J7DJeUNO1hxxR8crs/hLPWFhcWz67aUv9d/ZEnZHenDDauqnO+nvrU79zcHv43Or3nvUUdtY3jv9oqO14pLCCbz2+pK0'
        b'yHvOdWu3vDFHb+GUiqGFWrveWKV8mXfcOdmgueuj9sOnpUeNr33Vfjjj8yCPa5tiv7i+0GzX5aE/erd/OaND5mb/tjJxyfm7jQ8/+bzrr0Xmv6QszioLM3obvpoY+vrF'
        b'Hw8dNaub/9r1A7seNcZVCxJePVT90vWrfxFfmCPe+PZvo0XfbtgUZ1w9c3r1H0UrP3p/bsuRsp2B/JKwH9e+lPeIzZf2fZS6OK717Tdu/KQ/dG/7303+diL587deTlv6'
        b'eMfOh+EvN8QfLnt5SHt1a2nMO0mH34xNG1i9fYVHl8W3byyp/yPC+prx3R/1eyx+8V07Jej99DcemQdtq91959fU+nu/la6/t7ajNff6n/9xTf7Tt4NBK3VuWq7m5fzt'
        b'IeRdt3i0xiYOJp6xW71X9MpXI0fjzT6p+8P5015uEG316KfWi+E5Zxt/e0PxQ9KXv7x09uHh8B++WPzGmvVaPckBo78c/mIddWI06nve+ZbRn6jCivK/bpVt+PCtYo3a'
        b'tEe6dg1T1x+cvcq9535wj/zrZt1u/+t9J+pnuL6mpfgl6ZfTozMce39sSJOdt95rGbOxOjb3Q97KlJ2v3/zdL/DBjtW8IAIKKeGC7XiiAS5ygEyDPDqGwPk6Bg+0szRJ'
        b'D7Oy6bihVwN4HvahifBUcIYD2kzSGWzTEDwVpufOgxcZ/i1LNks/B543YfAmF8Exl3EMIDxRBc6Bs3AH8StfiEFmdbXgdN0Yxs2yAQwSv2i4KQQjD0H3egZ8CBvhITWH'
        b'LAroTLBvWl5q9Bs4DjvAQaY0g/X5eKoWArc9map5wFaGBG5rGTxDalOT7MHTpAxQkLXwjEswPM+AuaA0bwL2LRGcnwB/g4eXMqfSwM2xtgzqrQzcZIBv6GWgTU1hC08n'
        b'EvCb6bIx7Bs4DhiYUjR6J9ugh1mwULPOZGezZoL98CABP8XA5qxxeFsWmmwMzXRhoHzo2blOTfZp/oTuE/R4PVZPTXvhICaP3YemNARchpkz4Rkz4u2JHsbiZCyaZi6a'
        b'Re9M4lK6+mwgLUhlanINdoKjhPt1jYGAojRBL9vHfQmpiaFzaZLA7QkRL9gNh1aagCGCIZuXVsXwfNaBxidUn+HwGiODA6bgFKYIRcKWjdOExpQw8LN+eAC9Uu7A0DKj'
        b'cCwjjSAWuBDPVBd028CzeiLeE3rSRHCyEk22LzJ41csLwE0x3J6QAK8ksSmtGjZsDHSHzdOZ6my3Bof13NzHWSJhe0B+zgoS0wgcdcUQsBoeOGgHm5HwdXPZ4JqpHwOo'
        b'3F0OzuqBrmVI9E0FQlzkVhael6jJQnO5eH6BAWRQkk8wZAN1ampSIIfdeokpU+BWviZ6RbnGAnuRJPYQRJU73GuMkZ06oiSRLnpHrAUDlDm4pBEAGq2YY30b7cBhNfMb'
        b'6DKYp2aSNEXTdbjfDnYwgQ5EgkNPyB7B2XVP+B7Bich1pCC28KgFw6E4zo1oDQ9FcopJs66HUsyri3G+cAu4Oo70PWZDckiGbeDMJPpkwp2sCzZCNJtEQ5IMniMCDzVX'
        b'JbgZP4GuUnMeaSNwCciy9OoNDJ100Ki0Z6FCO5GIBmiedpYQgPaDLaADyY0bw0L1OAIa1cNiKE3PTQhvWBKCvysEHNlNvJyWouYZIy8+CM4DGTwEBtTkhuGYFBDpnTPg'
        b'+hh1p0iNa0aaA+7WG+fSw6SAxuB4Rm0QSTVgvi3qYmhquBUzAxJeQLhtBVF31pqr1MSAugwzp5obEDZVgF4GprgPtHkTEj/P5WweywappT6iPOJtQP/TJH5w9zKGxQ+1'
        b'4m4SnQ/PmWMOP7atmsUPnmfUqL8L7MeWVagTogprJbEj4HF70CIkJY5fXoFJBbPgUYLZJaSCe2YR0SbAg6sZIDwS4tVxem85UkjkVfBy5AK4Q5CKlDfo0YV7UAA9NJrh'
        b'OXhoHqPg2xuQesAhdvK8dGBTvAYKcI4NT6KXqhMEQuszAxzDL5OYiBX2skE7K91gIQOhPQc2G/DTBGgs74CXwEUCjdeDN9iom20DzQw2s6kGHNJzh7s5qI9uYqewfEEf'
        b'OM8or03RAU9w0wxomirSgtuLSK9MykGvV+MWAmAPPJg2wUKgfyXP/v8eTfjPwD6I8d1z/z0NA7mv+2S2vor3T0/sybpuAnpd+JmZxo9Gx7Mogd8oVc2yFnxPXKmWyllw'
        b'pqCjoL2ws1DKVjm6yrw7gqXBKqGPNFYl8JbGSGMejF+r3L1o9xCp1gNHZ+mizpmjaDjHsuS5/YXMlYrvLfcfiL0QTvOjaH4szU+i+ekK/hpF9lxFQYmifLGyYDGdXUVn'
        b'V9PZdXT2cjp7jTRa5cqX1fWuvOsaqHANVAWGDTTIuTJNlcCHFoQO5AyXXy2kBcm0IJcWzKUF80cpSjiXrShbTJfVKepXo5/rWdHs7ymqAX09RnMHVgzzlc585TBfc9lS'
        b'ttSvXUcl9JXnDFRcKKKFMbQwnham0MJMhXCdImeeorBMsWCJsnAJnbOUzqmhcxronJV0zjoU0b9dl0TsLSKkXFEopkJYOhKnyM6/k0YnF9LJpepQ7l5yl14P2j0Statn'
        b'AKbNiUQ+Qe0GKnfc1AKf3jRM+TaLxbio9m6CXh3ZFHnmPdeZd11nKl0jaNeIUYrlPIulcvM4b9htKK/rX6l0i6TdIhVukT+jVOUoHZFsZW+KiufZa03zQlDZeufRwnAV'
        b'X3Q+sDsQxes1pN1CUPCB2kk/RrkcP5fvKY7A9TF2ftKk3IQd9e3LO5ePanEEAaOalE/AqD7lHTRqaejl8D2FnMfYYaowakMFzBxYMKKpnJlK+6fR/lk0ZrKbi2QQEMlW'
        b'FFUoFixV1CxXLlhOF62gi1ajhp/PisQNH66081H5hw1U9FfT/vEkbjbtn0v7F4x5huJT0cpfSqNDs+nQOXToXDoUizosBotaUSVWNKxWVq2my9bQZevVUpayFY6YtO8B'
        b'agVbmjeT5s1S8DKGF9xaLMV4UNSG9oUsWUXvYuZK5ROE+qbLEH+4YaTi1jqlTw7tk6PIm6f0mSedJV3RnvzAVdS5RqqhCgihA+LogGRFQJkiPVORVUqnl+G8fJR2vqil'
        b'UTvTwmiFMHOEPeJ/R3esd3jhvhH55NdcWhim/iXy7l3UW60QJQ8bD8fdskR3A9r1cBgsM4UwZdh7uOJWsDowwwQYin75tmvjQHm9hWovD5/eVb3r0Y/Adv0HfqH9Bf1F'
        b'tF+Cwq9sJBcTLBbRKaic0plKO2/cMWxQK3h6M5JDAxgXCPXbOFqYLNVVOQpxo6SwVE4u0pWdKfecAu86BQ7MuBeUcDcoQRmURAclKZ2SaadkhVOyysMPc6LF4hjkQHrk'
        b'SuMmxzQbsroXlHQXxQpKoYNSlE6ptFOqgnxw3gVMboyLtMikuNOGnp8vztrTT86VlwxY9C9RekbTntHq6uDq0bwwVMOAsP6V/esUAfNGjBXJBXTCvHFJOTorXPxpx4Dv'
        b'KUv7ItaAGreZPk8ROk8ZOm/UiPLwUnhF0qJZ90Txd0XxIyZKUQotSpHGPXAXyhxlC7oEvYKBqXfdgxXuwWMjsVbpFky7BSvcgkc5FF/0dDDUg2Q1navuuQbddQ1SuobQ'
        b'riGjlBYaycNaI6xbuvciMu9GZCojsumIbOY+GnCzWAmskam3ZozkKmbn3MlXuM2UaclZXbryuIHIC4loRMt8ZMu7QntDB7zu8kMV/FCVT/CVkIshF8L6w2TR6AftE0P7'
        b'JKKmFSKNERYpZ8v9L+g+cHWXimUB7Ws618hrGM06kDWQNWyGs7paNFSkSM+4G5ahCMtA+mSA1a97z3PWXc9ZTCOjus3MZKkS0hUZmXdm3EuYezdhrjJhHmpcxueBV+DA'
        b'1P4ZA7V3vSJREw7njmTcyr8Xk3s3JlcZk0fH5KGbqvDogXr16tCcIuQqo+fTyA2fT4fPl7EV/BClW6jCLfSBmwi3rCJgLhYl4dBTC/J7DotXhEmFkDvKuJoU37tXhNSo'
        b'u1cvv1dEu4cp3HOHzW5Z0pGZdGQu8aDdg2n3cHTp6I67WxJLtoD5VgVFDLsqAhPRYF+rdPJ74BYgm6IIjFe4paHPyCzmW8p94Bkg5XYaqFz4Uj381643WsTBD0rmoTnx'
        b'WMb7OnUrysrriiurxPe1iupWlBSLy/8VQKj6gMaJT39mazWHS1Ev8NTn4LW7VorgQtEzPyqexWLZ4Q3Wf935d+3QPsI40OM6vlS/YSSbw+MwC7kDzuDw2GEpsJdHzkup'
        b'hFuYRcF+llOS2uRyHNAwA5zUgHvzwQ44ALqIsTY8DrYUoLnhHjShTRCC7WmJAtAKD5MkbUM04IEyvGPEbEd0O8Hr49lJhSS7PLiVrOVnwgtzn5sdets9gPI7BzsZ4oNG'
        b'sBtc5GM7sbMusNMtPkWUkJKxDBvdZMSrWfBZ1Pxp2k7wgi2zBXMNHICtxFQdbEkhtueMrboGHCRViBNbJsFdQjfLhaArm6Tk5ZcRry5nsJMmFQWPMGc8n4f7jPBxKgIR'
        b'aOMR+9NcJme3CTsPBaBVewpshD2kGYPhafR6Nal9PLKftI433EiSTsgAR8RPJTVbfYY0rtVgLXn9r1ivDTpg12IyICqtdh7miG04FDW0IfpYTkr1WxFG79db3S5qNgmo'
        b'bHVZkn+jXfHHRht+zYOmLVui/0P3bGY9f+tI1yrZ21pGxobd6VOkhatGWDVf2X7UGOj4h57J7cEfXzlqJzctXx768C93jua9W+Ru+/sC7ZN8368zb50Pq+t6+Kfu1CjT'
        b'pMu29jZnd/p1Dtx46WHsN7N2Fec/COl+NO0lV69gN6NvT3744ZFPZhsVBq+oTz3ma8jr9vpC81PqnQ+adn5YPOr7t+Obg996xXm2wa0WC0nsznk/31PIDAsqjvMXO5/K'
        b'6db8dL1j3YxfvnhZ8pf3jpX0rn/ttdfKy51D/a8Y+G36YEVeUmzK6m6XB22drX6jpq2ZuRtrPtOl5qaWHDL7SHP2qyf3/aStV/M7qNoSWWnsONuo4aBTh+uc7u1Nuz9t'
        b'XzBauOl88+CNkVkLgudlyv/ycJbfva2L7px/61rHaw58TUM+6Fq0bK73WxqZu65OXVS7RUcruuuz7jnTe07P4R1g9Z6Yz3XwdXk7+7OPFldobLsj5esdufjT3D8/utr9'
        b'uECyNjRBL2xV8HnP/O1fZzjm727NCPk6+v2RPf6r/PNWVTc6J1y9rHhpC69g6wf1pnuXDNyrOP3eriMfzFG843dDb01Ev0T0m/72Ow6/JtyxvP/3s6rbnX91KMntNU2b'
        b'LlmcVX7iVVjRsMz3yL7+M9K2hACNTK9jJd3zG7/42PTM5jdDsy++kXjnm8rb83/bHv6RIqPylbbNKTcaf9uV0bet+XXB5y2/1ttHXrtT9t1Lwu/uhWd7bdz91lvi3x53'
        b'xZsHfiKQJ65V3Kg5m1J6Z+HnP145ElTwicXfDQwsSnhRaatshW/eqJ/v/d3o+z+LMgs6eaWi7+Uc8aq0OrZPmKDvYvfyw4GeEVE/PVjXyv/GpmnekZl3TtIFYQYte6b/'
        b'FuE3d83axk0P37k+Y29q9pyNhrO/LM1Yvu3N123u/2m1quZMWN6O9t7vEr879p3SFVyx9Mmu7TP+wngk+Wze6XU+r8c89q3+qst6/WKNnz92Fn/lf2X38paP993cKH1l'
        b'V67npWK/3gv35x7rvfj1O5/+8vBUqED8x8XfBTMXmB1d0XD/flDYe2Zf6pb+HDz4s87NDzXC4t5W2s6Zb1i3aSvP8zHenPQA56P/seVmCrwADo6ZboLN0czKxlWtWNjH'
        b'R6P2ibnoOWMwyHhuT09LwsaAsNPjyWJtvwdzltc52AIk46aKfTHkrAlsqgg3w9PMKs1WwRp+QqbfmFE3bDT2YKykd0wFHZPPMtu1ZIIpa40+WcxJgYPBE5e0yHoWVRtQ'
        b'A8+QIw7gFUP7JAf0qk5OMWdFgr3M6tDUMqRqssDlcStMEewjRphcF9A4tgiALWBhPz4sizlQBR7UAP2wx4k5S2AzOAh26bkvh0185tAqVDc9EzaqWgvcyazG3QDXwT5s'
        b'D1/Dw+scl7nLWbCtAXYSO+ugxTnYRrMInMVmmuDqEhFZAImHl+BhMdwOd8Kt5IQvbDCru5wNesB2PVKnZQZcMU9Te9yMc9Uy5mSttARwQw/uB1tFSILsXFbIUigjKyam'
        b'C4vwqhU4D87hlSsgg5fASWahcfMapM+Jqa/eYsLcwlj6cuAxxpR0q5ArdndKJLqaoCE2+YJDzDLgvnyBeo2uDaUxYZ0ODoE9oIW0gL85WaJnDnMogZfIMh/qZKdIEyIF'
        b'j7X7JBvNWtiHzTSNzZjF7TlgYySzDOVko16IsjcEjMUqbIeyJWMn5TjAXXjFDQwwp9jxwOZCMWwG1+BV1Ii78ImqXSxUrOaZjGSueIAbYriDvRCf14A6NXrQoyfUOT/G'
        b'8vRGsImeKKUWP+VAVzLsrEM5TzXlLDKDR0nqGAh1CK/P8uAxcIy0mrYBu0wTXCbe83TxQU9JK9Y+dcSa87zHAuRd6Bj3Dxgd4O56cOQJoQPoT2CWOo+BrbFiuBPIFwtr'
        b'eE9Wi0vBFtIQlYGzmcVi1Jez2cxasQ1oI7L3hxd19BLXz0kZXw52h23qs4a6ME5EPcvg6OOD8eCOHIYP4TzYB7fi1S7MvjDGifFktasHHFBvb8DzJTiVXtDNDOE0Ftwg'
        b'ZAzoTdFgGUQPFdRDNo1Z+MLNS+ApZiXwIBLN5slkEkH55nYahXV1ZDXPMQ+cm7AcRwYhizIv16B8HULgdVKHmYHgBDZMFngtJF1UO5BdYgP3kw5aop9NvMZnUyGotLiq'
        b'tuYasNsxkIy2tKX+qH/C6+AGXovegc97onST2aAFYrIMZm5XBE6ihDAVz8l0IWieCLDwzNc0gccNH/NxhS5YwCOMbtUCA0+r1yemz2C3AamfLThpoZ4TgX1gB54XgT1a'
        b'lGE+xwueA5dI5iXgBjzCzNrG8xWCYwTbAZu4oL8AdDDaaAe4EoBTS4PNMWG4X5G0OBx7NDaPM33+VAbsZWg/hJp4k2g75v3QBBv+Rxcu/+sjS/7FhcunSIOZdxcn9vPs'
        b'18i7C1mdNNbE7ynq5ckVsSzKxqFt3iiVz5nq9D1xW2LURql5nGnoFnYlXJW92xmrDqt2m04biSa2dA2nLT3k/nctgxSWQejVXxItiVZZOxDzXXnOXesQhXWIytEJ3/4M'
        b'G67GjTjf8aATC5UehUqHItqhSGFV9MAnkPaJpn0SFD6VIzlv5r+Wr5izUJlSSadUSjQVth5Kc08V30vmL3fu5/WLhp1v8UZi6VlZSn42zc9W5M5V8udKNCUrlOZuKp6I'
        b'5oXQvAgFL2c49nYiSBxpUEbn0NE5KEDDEUOVyKd3iUIUNVCnEC5AJRHSiQWK+RV3EyuQ/yqlubuKHygLG5g2ZDlkQwdh+1h+Fs3PGkvdwbVTSDt40w4BCofMAb+hMDok'
        b'hQ7JlGipeP4ya/nyYQ0lL4bmxSh4eSPTFelz6IQ8db58z94gsryk4KcOc2/p3DJUp/nAzrnTkLbzQS3LE+G1lVAFL3NY87Yu0B3xV0Zk0hGZ6iRQQD3azhMFtHXCVpaB'
        b'Mq7ctN/2rluEwi1C5eR+JrEjUbZc6RRAOwVIYlTuHije8iNTUOP2z6R94mmfVNong/bJGWvSB0i4VsTCEy/X2AaMUpoWNgOx5OuBnUunHimXCl+hbNElbRf45FcwbReO'
        b'f+l3TqHtfBV2SQPcIb0hQzowaVSHG2gjicWLQVa+o4bLWBboDf7f6pZxKGf3zlTaKUiio3LhSUtlzr1C2j1U4Z46zEF/CS8Z3jJUuqTRLmkSvQeWtrSlHzaiL2OpXPnS'
        b'OllM++rO1QrXGPni4ciL1ZJ4SfyoJuUmQD4JtCCMFkTRgjhakKwQlCiwjfE8Or1E6VpKu5ZK4h9YOo5SZhYJrAciX3kuXlrMH7a4ZUNHzqYj8yWx0oAjaSqhjzy2t1Ah'
        b'nDuwcmgdHZ5Dh89FPv5HUlWO7tIAWbB8pcIxCX2GY5lvNF54ApmJLK/LptcGm+SrnHykaSo7z1EO2zlMFRg6wlcJvUa56McohZwHfiFPfkhiRrUpob8kpi1FkqKytpNk'
        b'SS2OFLYVymruWnsqrD0/c3KTzZDNUNnxUGruUSyVlx829b1g2W+pEgSgdNA9lBByH4RETvz5PUo9mvWYuJIYlI0m5cAfpbRw3XH5FL7ReK08lzUSPRKtyMh5NelOkioi'
        b'CR9LkctifFRpsyf+JGkIvZmiMrpA6RBPO8QrrLAA7JzaVt6z9blr6yNPVNqG07bh31M2Frl47clVQLsEKFwiBvwkcSpbl7a1tK3X99QMa5SFh4+U26mv8ouQcmk77wdB'
        b'EUO2dFDKyPI7a/FRE4El+LYfavjOMNrRb8B0aIbCMQp9VO6iXnd5bv882i+Odo+XRqlEwbLS3iqFKBp9BnKY71HKhJQeuzK2ysNbJpZ7dy3vXY5XxWaz3veeqQjPUnpn'
        b'097ZCkH2qC7l6U17RKCuxvNjAvt0rehdMWDfvUa25n3/WYqouUr/Atq/QOFZMMqhPEMfCD1o4cyBGloYOZx9q+iuMFshzFYJfB+ERAzNvBeSdjckTRmSQYdkIJHw8liM'
        b'25Uki5Y7qzx8ZWuHDRWZOYoI/FHFJdxarcjKpePmyLn9hgN1Ss/on1VuQhn3B03KI0QRMlspyqFFOQq3nAc2jhI9/HdE73uxJtbqoxys7hnVP2GZzYixPZjDfcYA4b/7'
        b'9DJ6Zpntn3hYvY9tGLrGF9WWYyMGS7wm9m93/m1WEL/gKl3Atn7mtZvx9RbsbMXOH8i5P60Is9mW1jGrhkWYurZy6QJicV7biB0pNg1z46CgWmoL4vv6Ew127+tNMI2t'
        b'9cahMQa99k/s7MKOMcr9vs64Rd99LbX53H39iVZr9w0mWYMRQyFiT0IE8m87s+2f6Bp4nv6cow/G+sdpDdQ/JpF/B+Bugd5IqUkHH+jjgw+wY0U58xT69g8MTJtyJc5S'
        b'jsRSVi6PGjAdqB/OGlg84qfIzFXMmavIKFAUlijKKhWLlihKlyoCqxXCZQqDGqVBDW1QM8ouYhkEjVL/Uy4+1aCW9SSjaM6k4wbi8HEDCVgTI/cxcZuikTqc4SAxVxkJ'
        b'FUZClSl+LszwQUFm+DzGTlMiCmBm27JQZeSuMHJXmWIdbxaEApgFPcZOUxwKYOUkQbl4KIw8VKahKIDVTBTAauZj7DQlowCWjhI3lZFIYSRSmUagAJazcDGQ+5i4TUko'
        b'zMSiRuOixpKixpKixjJFnRgGF9UUF9UUF9XUhwQwsWxBGbkojFxUpp4ogIk3CmDi/Rg7TVFPpYAfUKbk0YTcx8QliZjbtaxQGfEVRnyV6UwUxjwCh0HuY+I24ceLhb1E'
        b'W2UkUBgJmJJY4JJY4JJY+DQlPNVoHrjRvHCjeeFG83qm0VJxo6XjXJD7mLik3aydJfEqI0+FkScTxpqEsSZhkNuUMqrNMkBTiOc4miwDK3z1jKM5l4PPYfjfcBksMYGR'
        b'yNk14mT9p9bIWJQFlGmU5ydOQlGP8z9vQs5BLWLBh7n8KbWJl06F1rg1n8b/uDXfc026nrbmq0ytT0W/VsDT4EwhaPHx9PX29/LzAVeAvK6utqGmXozehOWwH16El9Gb'
        b'9yXYN0VbX9dQx0AP7AFNYCfcBw9mpcO98HAOl4Ln4FU9PYPpZPuiAcrnEhT2Dr4HPAIPwD189Jq5g0OZwGMceA1I4X5CCg0OwUOgeS2UY/y5F+UF+u0ZYwf5khwSAzkc'
        b'sKmWMlm0DJ5HMeEQOFGPVWVVMLymC5p9kEb0przdyoi81oFNYK86V3U8sAVcJ3m6gQ4SkZUDpTWwyYeNQe8+86uJRQAL9sDrKK+l8BqJyqJMnVGcWLiXxBGArmDOLB/U'
        b'dL6ULziYSTIDh0rQG/WO8eyMUWbn0lAlSf0aiQlN/bq5YMDTB/UTP8oPdIGTZAsGXjMBe5nq4YhsyjR3tgmOth0eqscLgqDRHe6Khid90KTDn/KvBe3EmCwcnmhgslNH'
        b'48LrLBRPD24m0RaAI0LYAw75oOdBABUQCRg26nJ4LBBHS8tHUbVAO26Vq7gt+80YZm4J3AKPgEOmPqgPB1KBUDaXmGBogl2pfAdnUk4tR8oUZwU32ZA4KaAvFR4HcoDt'
        b'/4OoILibRfJKiNMbaxDUEg6UiROXkduAiDF7OLYEXAIt4AzoQ5ILpoJRD9vF2DKdh/2hqFHmWWHB2bHVXUUbtRmuGzxa6Qh2gVPY6nMWNYsDmpjdLMkquBvuMCGZokZx'
        b'RNGwBGA7CoAlUCAAA2bwGjZSiKKi4sF1YqO1DmxZiMW9kvSv9lDKlLT/4UoSB/Vu+RzYoyNGAo+moo0j6ska9ia4FW5jBI5rqFVCmRSBo6QpDZNJP6kOBNvXw1PY6jWG'
        b'iplOMUXcCPaBDUTcJJoxZQpuFuLGtClmpN3soI3a8rwYSTuWigX9scyOYyPoK1DXiw+ugX0eTBJ4EOEmrQ1g6LFbwUXUxa+BLjESexwVB3stiSlMnRu4RsKjgl+EF8EQ'
        b'lrsMXgZncPvIS0lVI0vAEJAFiZHk46l40GxAosJt4CjTNOqooZTJenCWZAvOopYlY3cv2AjP21hC3AUSqAR4wIC0ExxagTyYcuOeg5oJnAC7iTTz9Blh7jZyiYRnMQ6Z'
        b'SqQS/eEBQgQPu6aDi+MNDI7FeXiMaQ0sU5vZTHc9Bm/Afn4JxPz1SVQSPBHEtPNZOAi7+bAlFhd8M7xYq44HOhOYvnc9Ax4D/eAc7EOCTaaS4UFwkdR3CTytO9aDcJVx'
        b'Sw3BU8wo6YZHmfoeBVsouMsc9iHxplApRajj4r7ELcfddiwq6kqLIrFwHZ2YvtQTarQKFbgPCTeVSq2aTnQHB+wqHq+oFujAGR7yJZIBF8AgE3Mf3CGwnQP7kFjTqLSC'
        b'KFLLOKTgcGcCnTFMZHt1d4CNXqRtuWBvmiY+IACJNJ1KtwUyUkowCFun4xjJU/las8aHV9ZiEkkjCjZ6w63YlDODygDtcB/JrAp0V+M4JSIOEulFpmEOEgWXwTTpPtiP'
        b'dPgVsF8PiTKTyoRXwV7SC7igEZ5G5cwFbeq4oeos4S7Yywiyv24J0uen9diYmiEL9gEp6fjo3iAS0lgPCnBT60m1OGegwuH2STIBZxzhTj0ky2wqGw44kz5kFgcHxlt2'
        b'DexDkmHiqlWeHxmoQdba4JKrHhLkbHx2eSWz/388JYUPDjWQZ8fmWkbhgcNeJAbogVeqgjz1kBhzqBzTJMa69/Ry1E9QVz3oTCJtrFULo0qtWXcIWWAbUtBIhLlULjwB'
        b'rxPNusw+lZ8ALhA1jma7AWRYqXX/WnAVKa/NoEsPCXAONSfFmhmS7fCMp7pFOKCDjGaIxh/TpJcbSH6uSBb7py0FO9B1HpUHWsF20lQLwZl4Aer5O5CQ8qn8hjgSeirY'
        b'Cg4vgZvBDiSAudRccDOZlCBxKQ8J4Cjcj+oqokRgbwZpgelZ9vCCLtyP6uJBeawVMbqrH1wOjWYzZqL24DDYwfTdg3DQBs0C9qOU+RRfN009cm3hSXgG9mWhhnemnA3R'
        b'4xWHdtSA+0LXwv2owp6UJzzbQJJeibTa5roCtYmcAJ7XJMWYIloKN+dkobK5UC5wqIiny8wYuuBGcED93MHtgwbiNDCIn+LLtZgQO+HFaKYr8ZnHpw+UErV/EOkf0sbH'
        b'piClNK4FmDa+imcUKFQg6p3kOdVoAfpQIltQr0ap2LGYZwc8aEG6BErgyoKxByCKWIKy0cUdKTeQmTW0AQk8NK4c4SY8LM7oMqp12wLGwPZauT0OcS4P5YCqheuCkzA1'
        b'Y4rZKEI9aQd/bFKFFexh0KF+zoJDZPzZgYHxEYQzmoU1TDHpLemAMQUHx6iFyHPDVCZElHp8LYM3eCxGZ0jBGc0k2LxmlQA2x+NzzMF5NtgYb/IFmVK21EbwdIl5oXsC'
        b'mzlnJLbAYtWyAsbm0D1Zn0LDys0z9gHvIj+WuXkvSYdCUvT0rKCchhdVMzcfuRlTeI/Dc50y+ayJDnPzRJb6GIrYLXGfR61gbsYHTaGQYjL39N9ukVVtzdwU6mri6a2R'
        b'p8uC6LWrg5mbJ+2NKNRYgZ7+P+a9YmHF3Hx/jS6Fnpnang17NBIXqg0mN6+dRrnhjFI7EwR2Qubm53lcJvecwdRPOc7MTXst9XEqFV/whhe7U8R0fIqXGeqeKPd1n+T8'
        b'Ge1J8djZscTjtbnqJGJPLv/WvIAJHTtFXdbpqsh1HnbUF61H8L9Xw0kGW9CYJ77+v1lJqkqoL3zIv0fhzJN+AHTNRrPwffiRSFVT1fCYgAyJwFC4Aey34aPxs4Jakc5R'
        b'Hw1DJi1N4DTewprY3ZaqHxjSQpLp8ozpTAUK7xYrjAKZqlp5qBvF8IrJz6Y+kw1G0dhj3iVCKUxWcphagA1GzdaymtlS6nn/0KsNit8znsZe9k5zTAalpgq5z61cWla+'
        b'gschJqW1eLAyyyH4OKhxgg9cnVU24tLipUWVS/D5VE+sRqsqxXWl1UuWzZyii2LhF5CfN1AKjyzmM+wl517Ru6g3EHnBsN9w/DZ5zSOV7Z2fR8lxp7T+I50yyUAiTE2t'
        b'3PT6KbYYLz6d+D5lV/a7S7PiTI9Z3K5ZU3W7+ZPFbZLVr58S/vSb9d3p2tz7TkZuIvdCjchObQublktfGGjExkZvN/IIlWj9raTlV87veutnHd5Tevt2kN1u39cXVPxY'
        b'uPgv36z9Pfix4M/YyJsjH2Z5agsqH9vHfxPXFLjBUxm5xTxmZ2BTYI02vKUR25TQ2VRZ1pT3adPJEZPbnqmC+dY1Yf5GASVv7Tv9RkXVR99o/R7/3vYlt75VRf6uE26y'
        b'/qXUj0XfuHz3UuHHM79xtRmO/NjeysXmpYyPvaxcjw8nfMxrczn+Ut7HGuvm3X3otw4+DNz2aGBDQsEt24Etrw/87e2V5896d1+7kS/b/X7utwvecfsPz2/fgdn1vecO'
        b'vpklFIivK99ZnSGb/vUrHsaRf9O63zdl/apprSt/+u1+39GCK/dn1HL/PnAoaMaxIwaKP4O9fu4x/uj47T3fQnpLvu/LjQbeixxPnubvzjQ+cEP36tGHkpf+4+2qI3/M'
        b'sN6z9IOkd9fnvtNytOf6eybdA68axss+ePhFBvuux7VX3TnT3hD3fBcmyP8P/09ae/xKIV0rrersun0hctYHXx76zW+m6B3ZFqdr3cWlxqLBxXdGZe++xHX0CnHzar4z'
        b'uEBoViZ/dHza7T9DJd/9kHIo/tstgZK1VTZHC3LLnE9n89K9bwf2zKvYsmnV/WnFnxif3/Z79tDBU7FtV+9dv/qXRYPLTR5ePWq51OD6D7b7Bqhk/Y+qrxhG7fUT2Xx9'
        b'/0wc7Pn1etuN4ICja9+2ahjIcr1t2Xd6Fi9n5KtzLfpvDt4s3/wxZ9f61sHv1p6q6bH5cfBoocHR+WfbHl59+WGF1Uu9KYmzYj/XD8k0s17kNNe6bL/kQpfn1ap84x+a'
        b'bG3/OHjgp8HLvITiis86V33k47KkkX9l3iuCD/Pf47164PV99dXeH/3Qv29uR09Vz2+DwWcDH7ofPHM1t/ZIbcfXGR/2eRfVvv/D7bM25y1enV+7NcPjm5b+soI3fN95'
        b'd7fP7/k3PvP5Q3jiz5R7H9Qvf/fR722ax/XjW+fNfPfbJR1nGsOsV5wB1fTuxGs2j0IW+3mcLPrtJm/P+dmfrHzF+atdR32cT87+SZJ5yWPHtenzfC8ttjofOLNkaeLW'
        b'h39M+dDMCRzw5hkSIACacJqhqZwENMGdKclpXIq7hgU7l/oyO8998JKeJmyFOxg+c414Frp1Chxl0BYHVptiCNEefpLQnUXpoUdwIzzKYaPENjLRL8NTq9Gr+kU0r+uD'
        b'V9ALE0eX5QWH1CZvW/yy0GO5jw93g95ELqVRxkKzs5Nq27+p8+fiwywSBAkaKOVG0NPAhkfhtUzGFmhPUWKSIEQ8waxwpacpc57AkfgcKAdoLrvbAxVKo54Fm8GhLAYU'
        b'c5wHO/gi2IuRJVyKDfpYOXMZXIkR3D7fCLQx5oTjxoTwrNqsT+bOsMII3TH5AD4yQZMNr6MXzFMkU/e5YLsdlCURngaUqRkLdKSBy8zBAUfQ+/OhpDQfMKCGMsFtZozF'
        b'VC/sh7tyQdP4kR/jB350WvAc/+8tjl4ICED0+PPNkyZt96sNlJ48GFZNuCZ7/FqaauqnuhQWNW0WqylmlG1kbqgyspRkjXLwlYNQJmaufMOHTcjVA+LLxVfEl1wRX3w1'
        b'qklNtUL+Wsy1owiFUF/7RbBQIPJDmwmkw1yTQOprJhD5ocsE0mOuSSD1NROI/NBnAhkw1yQQuaaYG0xIcseQCTmFuSYh1ddMIPLDiAk0lbkmgdTXTCDyw5gJZMJck0Dq'
        b'ayYQ+WHKBJrGXJNA6msmEPkxnQlkxlyTQOprJhD5Yc4Eshivljnl6TNsorK2k4knf43ajofBTlP8qMM4131niNLEgzbxwKvGLqrplocX7VskNdlbfaC6haMynnaYv48v'
        b'wTvl7i18pbEfbezXFKWysm2Lb05pimnxV00zPzx339y98w7Ma4p9MNW0xaQlR1K2d55yqiM91bFplmoGSjjUIIb1PXFbNPFGhK1kmqRBWnxkhUxTVtulo7T1knvJSwcc'
        b'LlQoLcJoi7BRKmgqjoHdlkjVDKuWKJW1g2S21O9IQRs2TZkWSBwJS2VueUK3VVfqL7OXxXS5yiO7+LSjv9I8gDYPUJCPio/C+k3DyWFXMkVl5yDhqhxdJdoqexfpNKlY'
        b'Kpb5tK/oXCG3b1+jtPel7X1HKT0LD+JIIlUOztLiThdJ1ANb0SjFsfbAFh418qld4t5AqbZU+wFfJNVW2TpIF7aul6yXBw6suOsTp/CJU9k5n9Hv0JdltE/pnCKdosLB'
        b'UGg7Z2mJVEeq06mDfAzxVTv6r3J0k03Ff52BqFjmdicMWg2OTGmbgkrryJdFyTJlUZ1hEpyNREzI2le0h3WGyb2Vjn5KW3/a1l+igQNGo2LFyqPlfrJk2jEIh3fFiA9n'
        b'lZXTD5oUKqPbkSVtS2RimVge2LW2d+2AWOkxS2kTJeE8aQq/9lWdq5T23rS9N44bw2Jc1BCuAlkGaiXHjnUK17ABR4Vr9LCJJEZqfyReEq+ytT+xvHW5tP7IurZ1qDDm'
        b'1hOqYOdwRqtDS8ZtN+w0RE3v4CTRUjnzZH7SlFFqugWWDHYl0SoXoZzVvlgSp3JwlESNsk2sY1gqN3cpV+Xifqayo1KuN5CldImkXSKlHJWji2xqR4A0QOXEU7m6SzVU'
        b'bnxZSZc2DsyTRbYvQEFc3EcpbXuhrF4ulosHfC+s7F951yNC4RExnD3irEjPeNX11jxFTt7dmDxFTJ7K3UNu38WTRqn4PudDu0MHNAZmD/sM5A1NGTFW8pNpfjJj+Cju'
        b'WC1drXITqgRe8uiuZGkMvpjVlSiNGTWgXPkvkCPSHc7C9/mi8fk1+oxwR0pHakdK7+iiH0qPLNpjHK6Up+T/P+reAyCqY/sfv1voHZbels7Sm6KAFEHaUlTAgo2OqwjI'
        b'ggV7RxFdEHVBkEVRV0XFjrFmJhrTzK7Z6Ma8JKa9xFRMTH/v5Tczd3dZiol5z+97/7+sF/bO3Llz5045cz7nfM5M1NM8fI/EHojt8+rXPxcs95io8JiIvWVQQ/mH9Fn1'
        b'ufdZ9Ub11fbV9qecXnVulcw/Seb51M+AD27hx/qUl99jM/Ii4shAMcDjbqAW7dO5ohgtYN/wAUuwqPwvYfpCTCE2iNzT+5Ij2DtGa8m5jN1fMMpNlhxhJoPBsMDA+l87'
        b'PDcU/kNUkyFxdQ3VuzfC16Y3LK6uPgknTnO2UWWGmni6uv/n8XRHQFajRVR1zhqdNnMZfhYmTZvZwC5j/i+JM1mj1Fsni+w0jWeyPKspmsYpzp5D0dFAm5PhRqyDmQ66'
        b'4C5fPk166JualpOK5b80HSpyha5vBTwg2PXtBaYQb7prfg/d92oEpl7dFLqPwd7WGm1vG1LAem3tsjEdL9+eDLaL+IX5t/RbSzc+3mcXbf+vjzE9K/UJx2AvL4XHpBkr'
        b'zoPeXGKwHwzOgz4khurGMG29YRNt63oansvARvfgIhZ91Yb3g1b3U+A1HlNrZGBBSy2LGRXPLy1eOI9s6utd5+HA1fMwtffgjl0rA5HQQima+3P+ZDRMrUWLW8aIxig5'
        b'1ntTWlKa01rTRGnvOXjLfLTCrtjaifS1xrLOA4ZgtJGMIRV6wNJj9RQeq39WI2usRKigVAO4fDIawGZ4TI56eG7jFMPGNPPZusTl/IAs7E/FpqrgSV0HpqERPET07TXg'
        b'Kjg61tIftmQxKaYFgwLNsInmAluq0k3Z6Ns28XQoHoNQpc2JreJnZGVhMjx9sBZuzmYKwYU55ApelhGtDBvLX9VsLaCjQPy2tCoHGJhUL2ZRzGkM6vuviNaKuUqtDYtP'
        b'5jrHUhXYfY4bxsb6PYpKrjB+fUKzHo8SYrXtfbSs5dX9gKqz6QhLh+EV2kruNjZFXcQvIetiY2lnw+Q9ayfofMzEHJJGv3uTfCvXqFRgyTLjjqn5dD6QJ/z5y491MI+q'
        b'aVQdoQKe7Xbw4+KxnzKxGtguaakQK8i+eGSSk2fywHKJSXUuRekGMlqta4W4FfbfOUDMy4+2pPpi1xCr06xPHhSTjYgQd6Lb006/ZfZKwCtoqOn5f8xghrGOkvv+tOL3'
        b'uMlv4baieJ+PzSXnfm/r/Oe/3kJN7Uf5/ZBBTrVNuafzSSOal+ZQc3r/Rqr3cujfGp+skaO/PqI2FYrIuc/feKkxZoMcXfoxtfkdJ6KDFcLd2No8jdCRhbMpfdjiBhqZ'
        b'6Y7TBO88vEsJMTZy2/32ptzTle+GmHvxXnH3emeH5cuLXlhS2Wj8/q+2j1r+aS4ZU8BJX8u5tVhfdKBbPubzY680hn+W8+uECXenFafnBiSsra1f+u037zm7np130/XH'
        b'kHrfk+yBFUftQ97IXB4Z7jPGaIXLnMOzhbfGXvll7u7Dvcv1DQ40cV53qvvnK1EROQ331n914PSbYpu/n7P5WvrjxCkpbr+173/DaE1F1vWbb9zPOePd9caa63mFhgUh'
        b'P/PuzI25e+m3eZ+ud2M9Kn+1jffFJyGndlRuXuH3kt26/LKN333x1ulPJQ0CX/cSu9+Wxdl2iplWtxfNzvhxoYzlFB+6dPXbiu7NsxQ2X78d/eBD9vbOD+R3k1N/OwPO'
        b'de7e4+u2//JPX7y10HrKk7vJcZNtb771auvuijOhdxbmBcVKetLaCr5Y0b/90x0zN7dNufaq4JdroqmGMXW1Zb88+H6b4aG35bFRPlnWn2wPmbdEPH99+uuz83QeJVd0'
        b'vbeic1PRzzk3BeFpm67fs3p79f661crfon9fEPlDf/3m4gff/sulc2P9Jy8EfFa599jLsZ2Fd+/Zf+e1sP5Y/W+snNzA2E9fON1ZeWrasrPvTr5mN25j4u//UuZNEn5S'
        b'Z/HJCqNdNvPifjQ+zPgqpGHV/Xb/49/7bvxqyb33Y83KG/8xIbr8/uMTP1vMOTPrzjteM782zgtvf33xgKdp+b3xWx/Vum4RvSe+/W1Re/5qr6DPv9XJ+el3asrS/gLB'
        b'HZ450Ttw0eTdyOdhL01dagXs0i1n+kW6EDWHAJ6zw9t/mvZQP3oaEDGrpoGNKoKqc0AMG1OiYVNmAFo9QxmgF3ZCCdEeLAKnwRGicUiDTZgYUh9054Nu5mp4Ap4hfhTB'
        b'48EuYe2SJSamYIeZWQILnjFerEPZwP0s0AmOwEPkHlOmwEv+aAk7r62FiQHHSOJysB3sg0fgFdiYCXpxhTYyUuAuWpsyfxk85Z+uUnnAa8t1pzI5s5aqvEvmgg6+3xxt'
        b'fQjYpiJyqTex9E8PVN3OYHWhERPsmphL9Chj4CXQh56JF4h9QhzydQuYHmCLHa0uaivFXic8uA01RSI8SDim4AHQQhP1wINZqNSCNbAhLQMtjkbgNBN2ZsIrtLPbtVUh'
        b'/LRMVSODXiCZwyzNAxJy00DQGcNXh8WbDnvwugqadGhPpX2YJgpzgmbwdKnqpbrRTM5CsJZn+z9wrSAk3k9xoFApVQZXynqtv8mS/SJLtUCWTWawTewHqKcdDClr+4ZJ'
        b'SjMrmZmr0tZxb31LvcRTjmNM+YjY+MSKlhWSSLmtv8LWH5/gipZLOM1rWteI2A8t7EV2Yk+JjtzCW2HhPUAFmDhI3ZUcu71pLWnioi5Bu6BtYcdCaWhfrmJMsihNzklR'
        b'cFJEDKUVRzRVVCia2jpGnHLXykNm5aHkuIr4EmZzdmu2KBuJD3uXtCxpXta6TMR+z95JPEXCltR1G8vtAxX2gSJdpY2baKHE7YjPAR+pb1+y3D1a4R4tt4lR2MSIWEob'
        b'WzFLnNCmIy4WG7RWoBNWNmKvlhhRjCRBUix16y6VJvYxjk6SLOzJ6iu96xkt84xWOrihTb+Ds8RQ7uAn0lPa2XfptetJ9KQ2crsQhV2ISEdpZScObRkvGq908hHzpYxT'
        b'esf0+lh9FfKQiTeS5b58hS9f7pShcMoQTVI6uOJIXdha1zoS79Xz5a7BfZ5yvG/++aGTmyRRkijV687oyZA7heDsXmJ/SeGRsgNl0pw+L7n3OIX3OLnDeIXDeFSMle0A'
        b'ZWsRrXR0EueIc8W5HZGiJDrkWm3b+I7xUpa09KiR3DECnUXyWGpLqjhXktQ2S87hKTg8GYen5HpKaruNRAmiUlGZqKw5bYjYpnR0FSWJkh6i0vMk4eKZHTH3HQPvOgbK'
        b'HYMVjsEyxzF9YahgW+4AZWodTasyuG5ke82SCo6a9dvIufEKbjyOAseVhLVHiaOUnl5Hkg8kSyP6rGknj343uWe0eJLS3QdvstnOQUpvH/KsuX3hcu9IhXck3l57SnKk'
        b'Ft150nDJzJ6YvjF3PcbJPMbhzbZ6ez1ggC5FfdXLW4Len0TQk4HK9OQdyTyQ2efd7yn3jFN4xj31VMaBjD47OY7vF4VOmFvs1WvRazZoNRAZDMxkoE5Lei45PMaHJ9SQ'
        b'c6Mdfv7551HT8hmUOWeAYpn4Dhkpo4yj4SPNjCMz46LT4jwRDp6A3nwDn0g/L5qmjeGbsV4zY/Ot9F6zYaAjLVUbP2BXF9bOf8AuKawtfGBQXlo7r1ZQW/HXSCYIr792'
        b'cDFaEn+R7JoH5xQOFrr3UJpgYqVY7MZGof/Z4bmJ5zNRfYuZWrs8zdZzJUVvPQntuQ7aPlNlLA3N+XBLz+dPcz4ibIemYkPiNqD9ADY/qIP7kvnZ2IcQbkUyJ1q9UsAO'
        b'S3CRBdfDPigWxC+6SPPuNu9fX7Zr36sxneu2du/q3nV012KTj8O8dTe/HW/MeNG4I5CqXq5z5ubndEdhDX/neAusWUVMcMcZXEiGfiVrCQZ/yPZvqipoaYlUILMaJ7ca'
        b'p7AaJzMep7XT060B2BPjpae4Y2CTPZVzBd3PXsb9bOgt83BXq6HUrhTlU1FPc8a95emH59aNsPDw/99uxMoSpHxXpCPEWoszn48b0j3srVhwAXczlbyZs3l6a4HuHRuq'
        b'Ol1nwcMvn6mLCId2EeGILuKq6iKVqIuY2Daki2rFuXJjd4Wxu0z9GdlL4LP2kldJLxly1xlDe8ki3EvscGd4+uG/0EtW417CUvUSBm1eXsb+X/YTjTGIVj8xzKIjUVwG'
        b'zcEqVQa8tJBNYVUG2AIvkJ3+xykuTDu/X/Wp6g/X9Bdw68jJxy6siFkqBZmJXQVtn+FgwPD2QvsRqrrQdU7yUoo2x5TOsc8BJ/BtNibHUGB/lAfJbFCnqxvEQC3ILQho'
        b'D6qmiGkfpxDsyAnEXuhwj39qGovSnclkTAcnBBfGz2IK8QPPPW+0anK0IQzhvLXiXxtdui++Yv/gV3C++IbodK3fj4y/dc96tCBq2SstHj+WNmzYMGvDi2d6fto499em'
        b'+Zb5Pq91GtbbJSsOHNqzRBLwe86HCzjV4fvuFT98HQgXH/cYeyKRu3Ph9e8/fyD8cJKjMmfqG0m3vn+PmRY587fg4FeuXdr7yuFPT6yw+PoUe04Ef/0/Kx7Jdyy5WXzx'
        b'2oGaTx4l+sTs1f18+4bfmAeO+Kx2juPpq2LcV4Kt/oG+qYFwaymT0gXtzEABeIFsXNYkgctoAwh2LFfvAfEOcCI4RAPPPXPH8eFWeJEfgDkNsnEYge1oFxYPd9HMlydB'
        b'DxDxA/KhRBsLj4E0byw4A7bDK+A42aWhYq7D/QxKdzXTHYrN6E1VQxTcpga282opYwxro93heXrbtAX0rPRPBQ2gi0DT7EgGOJkLd9AKyUNuzhguTwBntRBzQ3iUp/cs'
        b'YgYe9yrmSnpOMcaTfnVJ2Twsw9QP+UZmFIVqRqnFi47d3qiWqOaY1piGJKW5s8hEXNK1sH2h1EfuEqZwCZObhyvMwxsSPjW3ES0We8nNuQpzrsRCYe7RkKC0skbXWFph'
        b'mSz0U1tncSEtkzWzRQxRqNKcs9eoxQgJzQltM+47Bdx1CpBOkZOYuHLzEAVxkhnQo6yISBc6oE+ZWOzM2JaxNWt7VkOW0th8J38bX6wviWgzkxv7Kox9Zca+SitXUVhr'
        b'ZGuMhC2zCpDUogP9QdXAMp3WNKhX8wi3BPsPmcFIy6nkM3o2fBvPhkMabBaeDJdqJkPhM0yGz3dGxCLJkGnHQPX7+1sMNCOa7KVKqXxGCZXPLGHks5hUK6vVuFWvjNnL'
        b'HGp51kARfIM45GCMo0y/hLVRf+iMl89mUqU6JeyNVIlOr+5h1FmOa+bifF2SpofS9Eek6ZE0A5RmOCJNn6QZoTTjEWkGJM0EpZmOSDMkaWYozXxEmhFJs0BpliPSjEma'
        b'FUrjjEgzIWnWKM1mRJopSbNFaXYj0sxImj1KcxiRZo5aFeMujhv18y1IPhcBWk1KLYa2bQ9jByPfAuXFaJMBWrmcUH7LEmcSWsL1gV5mYSV20fw10FBbMZEzaXICdxGd'
        b'xCUR9YKGpPMYZL0fsmTiDkLWpQZ02K2vFZZI8/KJkGWgWTyHQ1zPf/HcyGP+umFIzfG/tEpBraCwQlBfKiSBLIc8raBSWItdU4MMR1wXVV1YU7iIi8dnFBcHIcR/cWur'
        b'uIV0EZOTkrllgorSoBFXjhhJwxdwlyyCTBXCbUL/VDRVT06FW7MDp6kZ2PYGgBOwISCIQaUw9CLB2UyaD05alWhUvTgHpahz5k6GW/WxOh42ZJJAHGg9KubqG4P9YBsN'
        b'dkg9ZuGgMpkscB4coqPKmMG1tCn1dXAJLdc4YMdOfiYDbrNCi1Ubc0U0vEK8E2ahxWqvf3pmUKBfOnbLC4HbKSsfFrbqiiUGs3WwF7Txw9KZFAOeQpMCvBi3mJYdGm0r'
        b'0OqYwaCYRfxARijo55HaMKfCfrdiflB6ZkBaJoMyqmLCNldwiZiPw7MlEbAxHvaiVRMHHGjMQDlMYRdrIuivJrp8XdgGLvDXgE3gRCqqFC7BzIM1A67l0ubW6+E1eFql'
        b'GESPsykTra0XmSt8JtNOYe3wGHiBn5bph9KZsM8WpTYywTp4El6jDc/XTwGHwUm4lgQ40oQ3MoFdtE9BajgOL4AWzhxnVXQBeBYeJbCRF7wCz9IRpJhzZ8NLOILUdVpE'
        b'O1RGk//gUEeHwDFVmKh182j/hvOusCMVyQM0N5Am0pMxvEJwIRhJ22jfWCI0HkirogUzuBmeBttzwJVsijgFxMLdRDB7cwWNAA0k1VT8WOeCESr83MGGcAsd1skvs8hX'
        b'O6pTLYdcd8uARra4ZsXGt6LHULRpejN6+WIcZQocZbNhEx1lCm4LJk3lBK/O9U8wGRZnqmgy3EQuXgkvTlMFmULtuxkHmgJiJHPsJiHQ7OBx3OvUoZrAVT+taE0kEhR6'
        b'DRdJ3Wut4Qt8sB0cQD2G7KeDmahLSFhzYMcawSnOdh3hMbTyNDmVnMidUAVCzCdEm5pXO1wzOPFr8a+Ov7LOzDA2Nj73RcmeyrIvpta9kaT3q8eKc9u+5utvzQ9we+/7'
        b'XyZ84Pzm8p2xazds3R7xHktv3EffLl2U6LFUUhAc2fboVOOi2/YdM5Ndqn+fL1yRNu6KyWe85d+80FsU8durfXfmtp1lrfpoksvOvcsdcvtqL96aOeMl6bgbvdUzX715'
        b'ttP9nmjF28t/2mSddar5raPVB5KzLoJHb8UuWDbh1eNS4/yjSSZ+Z3anX0/wCvoof1PCJmGx0Kc1wq/V+aWIFcXv5t5sv3rjR6svzcbkRN6xarDcMs3psagkZf8a5hW+'
        b'wvTKF5bfzv7qztHTjd9/+E6Uz4L0eZ/sKF7kfOz7Mf51VrL6WlFTxev/nBUa/mOYsKVNkZuZnTmn4qPzX0fss5b//cM1byWd4/p6zX/0hvMHj+TX8tZ8s7r0F6c7Abkv'
        b'nPiNGfLJrvdtJj35+IJigeLS1yef/K4fKFv00+djC9/zvr0ySRC7/vWU2bWzvui8vOPdpA3vvpT3nnf+5TeW5C9+t+vI1vkJk9NlXhcPBS3Z/XZ/5uwl7z5Y/Xba3srp'
        b'H62aFv+iR9Lxqi9LT1n/402eAwEUTECXO5n2qLlQRAupcI8pbaK6FzbDA2Az3MPP8AsieSijCibsmQwu0QEorOARQlpPkHtTCk1ZjcxVgWAnTc60Ce6qxjRwPA2cbg22'
        b'sMHeUn1wrJLQ3fn6wyODbHdw4+ShuHsqOEwDCU3lsAtHJ/I3xrMn2VrBdeWkkvVgNzgGO9B80hisnj0pIyETtuvF0+auOF7BWj5NhYcerpeRAEUhBAUqW4X5OYMHZ1WM'
        b'77DBhoQob3CUNnptDUbXN2ajedUA7KFYFYxpC1ASqZQkhUHivWYwmPAymoW6GEDkuJTsLKrAziBMSwU2Z6vnV9P5rHE58DhpmbkR4DgJtjQ4u8KNSyjLSBbodi4jVYNX'
        b'4QkoRuVr5ldzeJ2yXMECF2Oz6bezFu4BmwJnkTrQ0yxlNAU9N9i1kOZP6070S8UcW9mqeZYy8mJCCTgDj9Lbl61gPcs/KAf24LgF6pgFVaCVXJ0N+4pBYzo/W2s6NDNg'
        b'1YKN9fS2bP34RFS0ThA9LeH4cvbgtB5d+cN6Zfh1aKYkT3CQsoSHWHCdTZIqjIU/3INue4RQwpEIeEao78CLpbNJA4aD/hDUgJvAuWz1AmCayEq2hAcJ6Zgp2lwd9M8K'
        b'fEqYuXjQgZZNPQvQCreT4tI956P27gmAOzUrs2k5KyoS7qYZG9eCfYboYQZntsgCynIcC1yBJ0A3naWdCdE7C05Nwwc8FOAha8rSlAUOl8ItPNPnxImBEXYitQwjw8A8'
        b'IfXmKoER86QgMUpF6vU1TYgxsCBHrU+UJMmteAor3gBlYJHKILCEBptw7ojsimuPk0bIHUMUjiE4BZ+KbY+VetJABUZa4hnvufjKeLFylziFS5zMLk7p6CueIOXIHYMU'
        b'jkGkOJwtFWXzk/kny11SFC4pMrsUpbObxLtjtojdaqh0DRCvkub2+fbOlbvGKFxj0EljbD3sc8T3gK80Wu4eqXCPRCfNlE7crtT2VEleW3ZHNjphMPIEN1BiIi05Nf/Y'
        b'/L7l8qAERVCCnDtRwZ2IEk2UbkESZ2ntqWXHlvUbyoMTFcGJcrckhVsSSjT940RXj65l7cuk+nLXUIVrKK7gQ1cP/Etp79xl124n8ZXb+yvs/UW6Siv7x5SjRajSlitJ'
        b'ltn6oc9DnyDJUqWzhyS5Y650Wt+k3jkyp2ilk7tkbEcW/jVe4RT4WI/t6/CEQgcxu8N4wJTiBUuXK3zH97srfCfc902865t4I/G2BQ15iU2U7jyJT9+SfoEiMlXmniZ3'
        b'T1O4p4n1lP6hfTyFf4xYT2Hnq/Qd01eEihDrdZgoA8b3uykCSAJP6RfSZ6/wi+5PUPjFolQzZUgkvqvCLlBmF/gstdX6GqVwCsK/xymcAh6b6OGH0FM9hDllbd+acZ8T'
        b'dpeDA1AEK8LT5Ry+gsOXcfjKANSjWjMUHN5DNy/SxI6uXePax0nS6b4l0ldaOeKGjMANmSqzDUCfh7wQqa3S2UtSpnAOlC7r1+ldI3OKUzp5Sqahu+PfMxVOwagp/XBT'
        b'+uFaYAtvXih6XN/o/okK37j7vpPu+k66UXw7VO6bqfDNVDflshsGish0mTtf7s5XuPNxU4b3pSn8Y/+sKcP6xiv8JvQXKvziSVOGjcd3VdgFy+yCn62+2t/zFU4h+PcM'
        b'1KqoNfFz6Kmeg7Rm1n1OxF1ORN+M/irFmCw5J1vByZZxsjFlFQ+1Z5aC46Ok21OEfrR0HsY0XxP4t/iaVGDV4FzzR1NNNVaKiCi1UmROzjMqRf7PtSVCvKXrMAijzpgm'
        b'UKwhBpOaoN6WZLO3klqgSUJb8Pk4uqMOk4Tvxq1IwnfTkR1r6oa0QUxF4aKiksLYNwyxBSxOx6X+6o63oeqtq4aqaUjU+xpMYvUX6rQR1YnHeKA3TygorywteeaayXDN'
        b'fmAMqRmpVlUZFxdVWFtXM7Rmf71S7HlFYUXPXKO3cI1OatrKN7misJwrKOMKarkCIdq0TwybqGm7f7Ne5AV+TP2FF3hvaKWccDMV15SWCGqrariCkn+3ImW4It+z/0JF'
        b'3sEVOa+piIuqIoW1gqpK7n/SJqp3ZTBvUVWJoEzwF7rQ33CVvDVdyAdXqaJQWMulSyr+z+s2X1230mWlxXW1f6FuHwytm6embnRJz6liejQj2rNX66Oho85P3cdrteYF'
        b'1NnpUv+TzkUqV1JahLrpM1fu06GVcyVTAimCW1hcXFVXWfvv1qhc/R7VQ+eZ6/T50PfoNmT8Pa9aqdX4z1yrL4fWyktbu4hfpVq1OLRmWhUbRCyXUBjX3ks1MBtYKrt8'
        b'ikltHaZWXcUgylZqhLKVMUKhSq1mqJSto6b9Nbt83af4E5BaM2h/gjLGf9GboIzH/HXGCIUt/keG0tL5paj9a9BLQKNIa0DVoEFfgxbbWi7qNpVVtSN1viP0vpq+MxTg'
        b'N57hxhTiDeLXopJ9r47DPgaNDF3sP3DJi/Leyvz4m+08BqGtxrRG04fqClbCfVhdEAWbwT7U2czVnU0lR93A/Jau6s6mqfOgFX5ZeWkt2cFhe2ksVBVNZ1BO3I44GcdP'
        b'S8Zj0zLeUPEOM0MRW/+/cK9vsQhXTqksGWdNRxKcJRbFhh+eG471IvMZ7T+oBsZ/1f5j47OMFtQ9lm/KZAqxvuHWzZuD9h8Cew9i/bE269Yyu11um9zE68JZVMvhHe46'
        b'x+a/gfoLlyLO35fBPq0OA7rBUZWCKQrsCfhjG5Gal//0hQpVncdB1XkWoM7j4y8pkY7pXtizEO0askXoZ4iZCOlHFoxnNSZ6lir8ONRwRIA7lT3uRU8/PFfDER6TRlb2'
        b'YR4lPj8b7F8ZyKDYZgxwBB4PotM2wUZXvn9WNezFSeHYCb8RnhFsMTXVEWIqvjPFZ7B/0bpd3Rt4TaGbTm86aHP7i4Ks4vRC5hn7hXYL7HJOK8WfheiEVx9mUC82GCT9'
        b'lKYemaPtqoj6XtOKX6JDvcWIViSvLpN+dUq2/sCM6Qy2hf8ANcrBlGGB3TlHPzzkekpLZLbh+GMePmTWGO0dP1PdvsHvdKGqW83Eb9QAv7hRD893rhh1dSJzBZusTmyC'
        b'pFIqG6D/3hqVOWKBScQeVEJa2EMr0lAUU8gV1goqKrhLCisEJX8CSI5meaablZtM0KAnZfWUPmoU8+ivOJ84NtYL5hd+whLiYRxwddq+V8PQeuWF1qttbVPtNiS4bw9p'
        b'dl/C3WlwB/fc18JhXTVzeYDdd9XNzLElby2wF9tFtS1MNUDHPYw3ZjeFTO/ZXMjwZ9n0GTdMD+c+WRoWVODRe3Jz97bGdW6NzreyC++UJfSbfZJyx4aKP+doUH6Zp0+b'
        b'xYjBRtjpTytC1xgRVMAUXGClsKGENrtpMomCR8BlDZhJI5lohKqir5wGu5zgNXhNAw/S2CDYmEjrhncW+mkhnZTVfHAGI51gA18VbTsYHOTTenGwBVxXY4+lq4jKfjma'
        b'ac/x08DpFVjNy2YzQNd0lUcG6BsDWv3h1uw00MumdCvWwG1Md9DhSLtdtMOjoJWf5gDWg94AXYrtxABnoNicp/N0DQq2B9OywtEXCOeRlz4oZKrPkAHfrhpU9WiutnNq'
        b'XYWHMFfp6CqOUNo6tq7AX90kJT0LyR9KR654DD6/mnyVevYGDp5/yLFrzZRxQiS5PbOwC4CzKEpcKLGTW/kprPzobHb2Xbrtum36HfqiBOxFkN6S3pzRmiEJlXM8USZp'
        b'7l2rUJlVqPo2otohtjSjyByjmtJoGSHV8HS1xWv1k/+Gp5MllNpF+Klix/+VFILfbRb9WFajUXNrcXBjA6KaL/CbZBWFFdXgmHM1jTr4xaq30w/01ZvXB7r0vu6BLr2r'
        b'eqCv3sk80FdvQcgMS5qFZ/KfYwMm1DC+bLrVldiASW1LshA3dj5zGEU2E1Nk44MuZWrdMB37O4j9ZCZechMvhYnXAHMmw8R7gPr3j5jV2nuwpCXMIRzO4zCHcxSmcI7C'
        b'DM5RhMDZxkU0Q2nOk5nz6Aw2OIMNzmAT1ZA8jCYaMzxbEYZnK8LwjI6EKVo7TxjOE4GzROAcESSDNsNzBGZ4HosZnsdihuexhOFZm0d6AuaRjsM00nGYRTqOkEhrZ4jC'
        b'GWJwhhicIYZk0H4QzJttQ3izbQhvNjqSZ9HOMwbnicRZInGOSJJB+y6YvtsO03fbYfpuu/EjqoFjQdhNwBkm4AwTUAZ9Q5OIAeppBxtChS0jymvJeMn47uieaPpbQ9oA'
        b'2xyzTv+FA80YjSfiIA68BM9mwq0L1KCaIdjBBJeDI4YscZaq399jqWe3/QjrNd1Wu1aqlznUxoqYLpk0WDZYlek8T6s1uly02zDYqK+yU3Mgtlv6o9hu6dO16zUcZleH'
        b'5RAjVDN2idGImhk85RodtLM2HpHbUPX8dr0mQ2ta4kjuYUnuYrbRYNh1RuQ6Cl/Zqod+7HrND6Np5riuOocB+ilxamAQWm7aAMykwbTBvMGiwarBrsy4xGpEmcbquqAf'
        b'/VaDMlYv5zDalBzX8CmUOBN7Qh1iUmbUYIzKM8M1bOA0WDfYNNiics1LrEeUa6Ipl5TaqtdrM6JcHVWJZqQ0G1SSQYntiJJMVW1rN7xtUSsxS+xHtK5ZiSlR77k8MFXN'
        b'j+hXYXlpzYcR6OIhglkCd2gOLM2h30JuIRLktMU7bLZWWMstrME6/8V1AjTpDymorKqGzl+Ckoprsc5NUMutrSmsFBYWY1WlcJh1W1otEheralS30tylUKhRPCE5s5Jb'
        b'yC0XLCmtVBVbVbN8WDFBQdylhTWVgsryqKiR5nNYpzXsATVi6sRJuQlB3KSqSp9abp2wlDxBdU1VSR2prttQ40MmDTZ1MYcRbWj4K/BCultHQ7TBVDPCE/tDPQ3Fhs7/'
        b'OcXGfB7zw/zhr5k0+DATRLXcvkjdMP+WFaLmvWC1Feoc2i9zVP0U7kHkxZcEcdMIMFJShWpUWYXV2gJhLT6zFL+fIhU2UDrKXkJVIZXulK7TCI3qUgGuJEopq0PFFZaU'
        b'oM72lDpVlqD/3MLq6ipBJbqhNjryJxsZXWrkRsYkqy4efVsKLsNmOnYuHTg3VWNoAVtgUwYJczs1NSML7ggGvXArkfrBdbjFCB4CEnieGFzC1jWga2ghCavUxaCLVVYi'
        b'S+AWg1XTwVWa5HgPOMCHu8BpF/+swFQ2pePDgGJ4Mp4Q8cKzS4NpFlG98GWgC2yjrQB7nYE0JxAehmfgoTB9LsUKosximJ5LQEMdtsueAzYuAntX47B8/hryEmw0Onlq'
        b'4DQmFcnTAc2J4AqhKoVN9un+aKAIKQsL4XjQS/Z0hcbMJb0M4vRhvMy8kqrDsRHBjsJQvqZRwEGwYypsyJiCIxAGwB2ZdDjiKVV6cG3UQtru8NLUOcLFMVVoLMKdFNhW'
        b'Aw8K/M57s4XmqMcLDDfvnno6C4ZwrpT7nH6LuSms7u9Gdj9b6iq23ixK9RLpT7VI31NZltLb5t7zD89s6wu/OnisP5ga+9k37122XSPOXjbHrbf+8QGPtQf3r13HfN9C'
        b'+Hbw7DEftfut/jbMc8/Fqd9XbvLOXtjxzaUtbj/KJ0q38bJ+6IzsbAOevj8fWPdaz5cm+QukZ486BMV1PHJcWjv7ra9dZzYPjLsOxnxRcXzuDw6z3Ht/aX3zehIIu3z6'
        b'03ecliv4j5caVr286qvPffalle07tLJ+9ZaGF35h33nlA6fy6Ys/OPZ75mfV95oefJUT99rlmTu+OfzDp/8U5K6Tz4yfG57Pfsnq1ZVzO/X+ca7oeqN4Udurfy+7m+1+'
        b'crV9W/+kXwZMqg1yzjld43EIl2AYOArP8bE1L20MywgF61KIvVJxBUvbTg1JNZdpWzV9KJlI9pxBsAE0qW1RdWETbY6KgzySveNCcAUeXwCP0IZ0Kiu680BC7KxsS0o1'
        b'9nNBQESb0IGjoJmUDE6FgfZceH0YeeJkVcmpvh582v4YbSMMOEJfJtreXoXtxChpkgAego2ZcHsW6jngAOosfkjCB+dYU8AJsJfe8q6f4OkPJOB8MNyGJTRdIGUGgC1G'
        b'tAVYRxxj0H4PW+/5WDFXLYN7aAuvPcJa2AT60V4ctRfbjQE6QQ88SdvFHeXX+4P+OSpGAUIn4JBJaz7PgxNT/YOITRkay1vRWA1kLkKyOLjATq2Dm0i1LME6bHrnBrfQ'
        b'xlSUrhXTJATQISxhYxY4gGNP8nFgR1K3mXALZQH2ssBO2BZE2m1RLhNlIXMGPJBMpgzTHFamNTz7hMQK3xXkhy7F/Jo4hicO8rvDAlwFO4L56B1jH62dLCoFnNYDOycZ'
        b'0y45/eDYtFLQpDIsVpsVN1rS9l/oPOzUjtsJT4MeisKRO4UJT0iQxrHEnA3VCKjvCE5EI+kfFXUdzWMtPMN/Y9eHGay4w/yJiYmG7dD1fKhRWAK9BRxInsmg7Fxp1UIq'
        b'4z0HT5lXstwhReGQIuOkKG1dWtfglAQ6JU7uEK9wiJdx4pW29q1L965pWSOpldsGKGwDRGzaTiymPUbKlpbLHccqHMeK9Ol8q1tWS0poX2y04UClKTk2e/ktfAlbzvFS'
        b'cLxkHC+lvbOYI54vZcntAxQ4qh/DeiKjj6m0c+jSb9eXuYX1TT83S+4WL7dLUNglyOwSBlg4B52PPj4mxyfU8PNPOxKn8qckPbR37LDtcml3kerL7UMV9qEDlK66Fcb1'
        b'R8i1muLhyJrH45q7cLvK28vbBB2Crqr2KrlLsMIl+L5L1F2XKLlLjMIlpn+KwiVOzMLPEc+gr6KPj8nxCTX8/NOOqucYLekheoErJMV3bXkyWx6x2IuTu8QrXOJldvFK'
        b'ZzdihufGI3ZYXB9iK+fuLfGU1Cl84mQ+hTdSXsq4nzTrbtIs2ewCeVKhIqlQ7l6kcC/CRnki9CPE5FjAxSVRnwX12YnGetCMgY4vGcdNsmXdtGVPctS76cJARxXHnJYx'
        b'EpYPn8EiieaY09ggPUPvdjRCV22hNK7zwhkMBsMNa4z+2uG5mR/hlXyfQSh12jTur1gfqWB9nT+Eqoc3ghqxjjEaYogUrpFER4qeWmLmf2yZVHPyD6ylnlbXOCNtU5ca'
        b'C91hvm1DWe1YNHbewFbhgf8d9PyZ8MD/z6Hn5WgzdpU5rDmfAnT3CyexCVR4X/rlEKA7nFrj7N3I/PSN3SrgshrsZmuvYqAZXEQrmWoZs0p6GtLtPez9C4sr5hGeuT8A'
        b'vKfm/0eA9zPeMtFIG/dOzP8f4t5DPNoJltXA+N96tI/W09lZdXEUJk2E20lgDS0hygkJqTuww9vWDL/0AHAsl/Z9wyeyMzAQA46DrUbj0aX9gtSr31BCXND8hbdosOpS'
        b'au+uUAxY/VLyNV/8odNmzq3S7cbGx+0L/+Gd7L05S+KSK886vMy733Rzge4dY8onzvBLhjmP9SSEIn4cdKibITKdWqAbg239B2U6IdhEqB1xeDewb9DFBAv4mxhaLiYx'
        b'4Boddt0A7tTu9qX+g52eDdb9AdY7uHC9/KydUo3dT1CNgxloHNhh8g3rDIYkT4ED/eI/iXF9utyFr3Dhy+z4Sm+/P4D39f4Y3n+K9/NfqXKm0RC/6On5f471P1/AH++/'
        b'ecw6msMenF5WAU/wiV8Pwfv14D4a79+mB0/AnkI+2vOr8f5ToF8wVniNIRyDu7wFixhzDMX7v0ltKUgrzipkfmdHMH8a8S9DM6a7geLlCSrqzT+BAgcb9jZuWLunNSx5'
        b'+7mUBv6Pz2foY7x/lAOHhaH+PzzoU25eo1sB6Dy9K/yl+k7Er75a1VsT8v/QJOD52gVgplC05GBkbsiUqmHiWEvR5gEqj2fdBkaDHlqIdTST6nBN4/OfVNFC/OvhEdqx'
        b'lNJabqFa9NLWID9dr7ioprSM1uGNMCsfRfVXU1pbV1MpjOImcKOIn3hUger9FXCrihaUFo9iGPentgc6WXUR+Amn6RHFAoZ18iZPD5w2PRXNn5dh26BjtNorGqyNMFgA'
        b'j8H2OrzvBocsYT9/mH5PrccC5/xoVdZUIz3YtNxesO5cEFNYiS7jf/3TvlejiIHVpV2HdgWiRWJPaGhIb9n6xwvso2Za1BjZ2Zsb9a112Fwa//jt6ktF3ZbTNlYYFvvw'
        b'rR1Z7e3eyZI3Mj6PWmi/0O6suDBGcnxGQcXG+WPFeS/NA00lelYvPBqz/UXjDgFVf8fmvfnpPF2ixNAzAFvVGhvrPKyzAf1gLW2DcCFrorZmxBVuwK6N4AJoJEYQrMpZ'
        b'RotDRvg26sPN4PQT7I4NusEeuA/7XVcV0comS2vaK7IdHgcn+FhxAbaArmCiuTDKZ8KTYDfY/wTHgQBXrIrwkjUHto/GRgwOQ+lfoQnR4jg0wjwXqr5V7zBstGulkflp'
        b'mWq81+LVyVO0UpIk9ezlyW0jFLYRmHNtxNafYcGnt9ATb+TKvdLkDukKh3QZJ13p4Cb2kXi2BXYEivSUVg6t0RLPngCFe9hdqzCZVRihO54gd4hVOMTKOLFKW5chPi76'
        b'9MJGsPk/NkjQH1zdVLNaEbZI+IPnzMXz2krNklaa/1e8Wp7bHLf8qfJiPUXvLVQMSJTKpvi/Iyviae38qNNa7Uhb8qoyNRPD//0sl0Df8xlnuafYdp6eVMwWYt37Nafb'
        b'NL24gMEaK3ulP+Tx9uZ1hWM8ts97bTIU6XxG2/397Z7unPRXeExaxbnRxJQQy6n8SUErOIKVqw6wk10/EZ4kKs4QA7CNP3my2veWJjgwhxdGt/zUGOW5Mp/SZVUtTYam'
        b'u2po5s5iUI6u9x387jr4SSPkDiEKhxA0xGxdWlfLzL2GCAJPG0Q0a/jgzurP7l+Ch8wizZCZNOsPh8xzGyPj8FMwaYofPWHhktJ5hcKsIQikBoDC5j20REAQSFoi0G9g'
        b'ouGj+1/EH9Hw+bBoNPxRPYIwvFuiCm3/TOMnQQNFl9YWYo+XQtoaflHVEiRilNVULVKX+7wGH32NqrmjMExJQOgAjE0uqhPWYmySngyEtYJK2kUIK6JGBRdp5dQQjwqM'
        b'QaPCRwM2NeMe17WmcCndXOiZ/w0c0jCrDgv+a2AfPKwl1qCFeItKtHmKWAMuVRJylXlwE9jpn87MhccpRioFd8PmakInutZnZ06eibBmiUk1m2K3MWpvWBKUb08BJgv5'
        b'nKLiCzLEKxdTubTVDJEMtntm+GczwXbUY6biiMZIdBK8O2k2W/g6HlU2wbsnh5qCEOOY6MwH25qa2mxDQgZMD6dvt2CxWJP8jrXobHUzi+9te+HJrp7URbv9jC6EKfde'
        b'3vXtidiC/tfTps8NmfZy/Jsfl3z4nf33G5Psaws/yJ5x9dpr9m9/UnK87+fvex72Gke8vHrFjLBPJr16xOhU16lo79ccEl9eCerO3zStuzeQmDu/YfKmwBf73px6LP/z'
        b'gHvjHksqN1nM9bYPu3bT8MSVdG+rc2PmXmmrmhFi4ij/18nFN78OKfnIsNMn/JVdpk7+lv/K/LThu3/oGDwZew/e5OnTWNE5eG7RIDLmUw9OwiZHNcNEL0Z1kaB1dcYg'
        b'CoUELZEhDbscBqezhnBIlOWoJK0m8AKB9XLhvomDENV5JugEUhPaonO/oNLfLwhuplQEBwbRTNDl7UQ2/IlMeH4YSqU7N5RGqXThKVIAuyJhCCwHLy0Hp8GJSFpE3ASP'
        b'w63+g7gabACdzADYDHb/J0APV5uTWk/FS1ZvM8qEjM6TxWA9g14Mamb9p3Katb0oV+wpYcutvRTWXjijl9RS6ejcFdkeiQmSRUkDLHSOJJDDY3x4Qg05N9qBxjBGpulS'
        b'Lu5ds9pnSe37EuTOYxXOY5sNRWxRCSb0HYo+2TrsXdayTMKWTJFMlUzt0Zfb8hS2PEL9Ky5pXoH+sHIYoJgWPjTSVI4u1eA1PhqgScJpM+0wFZtiVMaHJJEDhmR8nlBD'
        b'zo12UEExw08/tHUUGRGw5EUj64QA1osB7IQQvRfDGegIrW0SI1kwkp0YrQdjGehIL8gGWgvyfN0/FW0NKC2chF6oa7Fs+5R+UYUX6fWUBiWZNesvoyTPbeXOo4jzCUGE'
        b'yPJtoPFIpu1j/XQxbV9FYWV5bnKxntZUbqmeynvwim5Mr+hbWFvYW3S26KKVHZu1YVpQY2LaZtZgjtZ6iwZLtNJbNbAbqAZWA6fMkqz4emjFNxq24uuTFV9vxIqvP2JV'
        b'11utr1rxR03TdhX4cDV7lBU/oaQE+zxXli4d6imAzW1o0x7aEqm4qqamVFhdVVkiqCz/A0oztA5HFdbW1kQVaDQ0BWQtxZJFFbegILemrrSgIEDlbb2ktIYYLxPLtRGF'
        b'FT7VUo1bXFiJV/iaKmzwrHaHrC2sQb2MW1RYufDpYsYQg6RhW4VRzZGeKnz8kcCCGwLbSwmrS4vJEwbQrTyq+DHooV9Zt6iotOaZjas03ZWuxqA//dL5guL5Q+Qg8kSV'
        b'hYtKR61BFe0arG6H+VUVJWjIaklVwxyHFxXWLBxmXah5aUIuTREQxM3GPpJLBUK6Bkg0nF9Vwo0qq6ssRt0D5VHvdQtGLUhd++LCigr0jotKy6pUQpqGgpDuBHXYhxmb'
        b'BhaOWo52H3pqS2pcjKK4w/kABn061fd9mm+nqqyisKKRpWizCvzJ9Xi+QRJtTjZ3bPj4wFDyvQ7NoWgQlpSqX5W6LNT16V4yuqtpUmlZYV1FrVA9RDRljfrGfYRc8hWb'
        b'cI6o3BCxV9Uz8aNUo50v+usZhPYh0rDVKNKwTxYdzf4qY4UwrCbOn0kxqihwcYU7oc8Dh43gJqMli+enMygGbKBgRwbczWOQtLlj4AX/LLjDGJ5hUEywg5EITgbVYR+6'
        b'WCAGG9BVU2gp2jco0Bc2BPulZSKB+pjpnNxqeKZ2Gm0iB1r9DMZlwba6ICyidYMmsHbQrM+0mj89ld4yD9r0Fc/VB92wH2wmonV/obGTDxVCUZMLKn5y8aDqfNHJBfwI'
        b'wtK7R09jlUd7HwXwAtN1qAn+OA7vIdBDxxYXV632hy26SAQx9KfAfrAF0kWzxusW6VKETjnjYFwtTchc76tTSbHMsSgf8NisgD550p9ZYcsiCqeK+YYMirTobNiWDQ+S'
        b'CE9gKzxqFDaLBCshF7yUrh8xicXFq3hGWl4GVYexH9AFLq0kjJBgL2zKSSXQVhqq/3Z/vB3RWBiihNSA9IygtEC0VsJGnvFicKiabGnCOGDzCEXtdl56ZjnclgGO5qZq'
        b'bMfAOnjJAByE18DxZJ4+zYe4Nx2eBpeQfD7E5GlKOmmllUudMYsiuAAvYSZFRjA8WUusKifBhhAoBQ0qJkWaRZEB1hP7ST1wtnQIgyJsjTJnWcM9YC1BZ3TBMdDiv1pF'
        b'ZqhiMlzLoVkhT8IzS/xVrGHgcq2GyxBunEr63yqwyZ/mMpyzlEEzGc5yJzyG4BTYCrppIsNJ4MAwPjCayLBvGc+IBo8u2Avnok0IoeKkaTir4FpCfAn6wBXYqfZcgyKw'
        b'Xu29th82kkabJSwHW4qG+Kdh5zTPCPJ4E2AbWM8PS4frUgkRJwUvwiPwJG2zeSJzGVYIwwPRtEbYwpa4UQTDs7BzkIcT7gVHMBcnuBRCWiXI1oOwVxOmuEp4XkPFGQtP'
        b'keuTUGdrV/nDxYK1GirOCyWkwnVZ4Iza0w5uBntV3nZFLPK+ytPANrW6/pJQi9TxTCx5oGXgoEDF0zkxU63Fcg6n2/EMaLPMgaI8cBiuxQ/YSVVO0idkmf75bG4vgx40'
        b'fWvKKZIfXoBNTPQsu7LLctkU05iC1+GRFTzDOqzOgmvRg4uFpjV18LQxPG0GtsGLtahxF7DA/plp4CJoqfPC2U6hXnICZ0uuH8wohOfqsPrtMAt2jgWddSSqX/cy2KJd'
        b'3tLaxQY1JqZoBF2e7Mtiw/Wr62iy0yPBdfBsHTwnXIwGVpNZTR2LsnJimS2LhLtC6rD7N9yUzxQurjMkxZjB8wa54ThmYB3Orr553FxdnaVgd50bmWDgLnhZc4U6i1Up'
        b'ywpeSQCNqSSXoQDs0eRBlYtn0dVzASfZ3mgz2VuHd8A1OhO1CqqtgedQ7SaxwBF+FJq069CMQhmBBnBFlQmuhwdRaWi61aXMdZmosQ750095NYODtrkvGMELtahCxgYm'
        b'NTqUyWomOGuChi7OEQR63HIyYXMObIK7BWE5oImN3nc7A722E3zSg93hvkU5kydPgNdxgRuowpRqcuUqNLmK4AXLkWWXgyNk5EaWR6O+t04IL5ihJCY8zPArqagLw51I'
        b'BI47wkY06/GDMzOy8/AiMZVeRdZEpAbgGXB7WgbchuYCsD7PQJjMpvvSBthkzMdh1RlRaB/eScHWOCgmtTHRhxd5xvBsKpoN+IFo2GSxKQvQwQJ7TMBxMhk3U466Mxnz'
        b'Kcq8YKXAczk9Q5tP8/PuZ0rxSXezlGTqM3oF/TlO9YdvPI9Npnm4wwNeAngXsJwKKloOt0ym19OOMrgFHEfyfz1VDFrqrZyJEXh+FeylzcwXwbXLjPToRXZXElp0GtFf'
        b'AgpcBq0CcB0cJxtDweGogyyhLYuiUhZdPTGNX/VWvPn7dU4vn/Ks+7Vh1mfysYdi/Ey5DMuJ+o9t+2W/pTfkHvO7uGBKKX/yVvjj2n6uaeBdl8lBj3aWdNz94WS4d+xD'
        b'360T/vX3fS/fufPVzjvZQK+4ZunNU8tDDn/3SGeelW5CkPXN6NMvfm5ReitzEfPzo4px3+yPkE2tcS47lv+ZjZvVsvb0V3Q2/XRYsWjhCz+M/2rgtRvclZ1mP0S+HtX/'
        b'w5z7Va8/Svng0Wd7b/SxH9/3unPPY1ny1BbzwsLx4htL/bqSDjJvzd2eJrDJm9h2dr9HxAc5LPN9A1//y+jm374f31Yd8tvW7oNh96a/E2cRtLl8/44j9ncTm68NTGnM'
        b'LY//uV28fz8vfVn2ucmr3R80/tA47Z2vDp6K89ryfkOM28t/b3t89EL2HV+v37g6tWcDxv79zL3pByvmBHm4vPjgxEDqXlfFmQ8mvn2hMc+o/XjM+m1zWr5qvy5o+um7'
        b'pe7xE3of9S5OOXvpJY/aqqBG01vTpHOtrjjeuryVt8f24M1Xi4yfWIPfrrBCT73/yq2FYTZnDVPGcHpXS2Y+ev89wdRt6Ym5L+xIj5ws2Ji+QnoueNU3s9+VjRFmv33N'
        b'yXeuzrbgdR8lSJQmnIXrKjcEzlshcN457nz1Bx9Re+dN+bvPPet/5vEDpZ+ZmHj9tqb7szEDV5j30+8WHP+l8rVl4Wn3Xiz7KoF35ERZ6a2SN0PfuZjh9Xb57iX94Mq6'
        b'Od0lT2779TZdCf70rNFKr4Wml0ubxsz86UGms3LLKuk/GLdenthpdmBLWlSjstBxjfB+0FeLpmf96vvDMru4z7rtir564f3S23BXZHrA3P0f5+R/HjvBpei9zwaOOoR+'
        b'lZvydd/vLxpt+CGY/8H3Idez//nSqbAvcz7gbo17vyX225WeW7/ft/rgjYfbFm13e/zOWpOZQqZ19O68fWMZcWAgpmjf1uj3m8eOPdv25gXlj2/MZ5a3H425fyOj7uYE'
        b'Rdmu5aVnFxw+3zgrWfTTFM8H4eZf60mX/uA+dV+V2ZROsJI/q/2OR+6RQ186Xa8789bNudYBHRY/Jn/yyaodSrfHkoeCMcefMLNst/zd/tKEhfHTXKZvNa+Y9G3D9x+a'
        b'JTS47/guhRdEFIOmYL0BPAjP+mubW+tSlmksIMmfTfSOlbSIguUgsIkWYUA/j1ydAo+BTt9CvtqGKJvQRVvALSyw3dSYqCYd4ZUUleJxEtytjfGGm9LaxTZ43nOQnhpK'
        b'l2KXgHTaXDwzA5xelDDUhl1twH4xl+gtg8D1VCBZpWVdHwb7SMlhYJ9AHasPtCNBFVvXV4O9BHsyQwLUcY3iMslGpbqkFZfglCrcXx9TVxO4gkGNh+dw3ApwpJYY9lvA'
        b'E2DnbE9/JA806VLsCAY4CteCS7Rz/Sa4GU1YKq0m7IIdxGPADR4gyeNAH+zms4Y5KyDZi3YZQHP8uRJNCEIgjccxCCfW0GlXx+nw/ZHYtZ2vS80BEt3lTE8+7CaNXQg7'
        b'wcbBcIxx4ByJyMhcDY4vIY1lmw47pxlpu1dMBvvJo06vB6fVHhLcCuwjwUSbhX3gPLluCQN2Y6OxYHDGVg9tWQ4w8mwWk97hCzfCK1mYhFxDE2AGNxDVcC24EAvPrICN'
        b'ARD1jEbUFpkBSBIJZsHdsB/uJw1hBg/E8WnvAwLgw60eGMPPg3ueENL1ZmYVlvUs4TZa1isJol/MOrRUNlIrh0rcNmA7qe10t5h5ZkPEaiDSp5XNB+H66iFyNViH5Wqw'
        b'wYI8zYISDhSXDZOquTQZ7xW4q14tVbOAdFCq7odrycUTlnjSUjW4NEYlVo+Fl4j9nCk84ElL1QVRowrVHahbEtl9h3suLsQfbrVFLYszmMG1rCokF1ylh8sxeBS04GiQ'
        b'wdmBTGp1LeqRfuPQbfD2rQxeBevVMhjqdJexHLYYnjeBfYwwJIMHwAM6BgtBC2l6L7RlucBXvZcxK7GA3s4E2+aBy+Ttwd7AhfwAEtAFbA1OAyd8GZRjMhuIBKBzJmil'
        b'X8NeKJ1CQsaMARdC7dmUHuxm6oN+7hOywG+HDVWqlRw2ltQXxtJYxDZ4KJqqUtEOqyKKWXmw0ASyB+ym793hDdvoDEGZcBvaJKB7QzHbLwh0eMCNtAFIF2jNJXmyA+CR'
        b'IiSgoHfDpGzHsONWghOk1UNh20qSA66DJ4KzAlPBdjza+DhQqRfs0ikIBt30u90DLxfzcV220S/FCO5CO3EkZXfbJtFeLfvBPmy7EpCFcqHN90nQp5vFdFo+llwPNkfl'
        b'ahyI0OBdr3Eg8oDXad6rdtCP5oSzZktUU6ABmjrPwKNMcAJsATvoztkJNxSg9xHI8w1EG/r9qA+VM9HmoBsc4Lk9H2Lk/+ODkPjvDP23dsQ/lQ1NYUnJU21otNIINuOt'
        b'S2Mzq2fjuDutsRiimMGQlGOOD/yX0pFL6Jgje6P7c/rn3MiTTci5XSqOkzvmKRzzMLowg6ZiTr0d+Xq0nDdN7jJd4TJdZjdd47wTR6AcLfsZKyeZla80R5rTZ390bu/c'
        b'/sK7gXGyQDqbKhamjDNeaWXbHKO0dxPbSTx7gvo85faRCvvIAUrPOqg/TOnq1rW0fWnb8o7lXWva18hdQxSuIfddo++6RstdJyhcJ4jZSjdPiZUkV+rWM73bqcdJrKt0'
        b'95J4SIolxVJP6eJen+6Knoq+KXLvsTTR8333CXfdJ/SXyd0nKdwnidniKW16GJTBkUEZbYYdhmJDDUZzxP6AvTSi27XHVW4XqrALldmFqtKGZrTEGbsdexzldoE0y/GA'
        b'Gao+eQZyeIwPT6gh50Y7EFxnlDRzyskFY1+SCClD6iZl9YyXOwYqHANFSQ+tbMXR4mhJrdwxQOEYcJfEJCItnCJ3SFU4pMo4qUpbjxFgnJV1a+Te2JZYiafcykdh5fMH'
        b'YJyNy96KlormytZKEeuhE1fp4iNzmShNPJV6LPVoem/6/YD4uwHx8oCJioCJMpf0GyVKNz+lo4vS0bUjRuHor3R171rVvqptTccaJdfjiMkBk26zHjMl11Pp4vGQ69lj'
        b'rOCGKl09OlYqXIOV6u8ePj0xCo9IzXdP354Mhed4pbs3Ntcao+QF9jopeIkDFgZuNgMUPthQbr49xkpX744VSq4P+svDryeO/svTX+EZoXTn9QQpeSEKXiy6yhVfhQ48'
        b'FzvLAQodROyBWMrNi9xNZIK6ZGuMworQ3MxiKEMizhkrQtJl5HM783amzDNflIkqiV4Hu9dY4Rsj95ig8JggM+cqI8ady1BEpMroT3q+bNYcRfpcGfr4zEPpEku5uafS'
        b'zUvCQUOvSu42VuE2VmSqDBt/LrgP/dyIlU3NVSTmydDHa5rIVFwjN3d/SLdGuNIrTOkbcMrgmIEsbKLcN1Hhm4jqoAwIVwQkyAKm3Jj+0mz81DFKb78jggOCPlO5d5zC'
        b'O44+hx7fX+Y+ts9a6eYxYG1kgx4bHUTMATuKgw2+8RQQPvZizJmYG4bycL4inC8jn9szb8+UeU8XTRStaM5W2jiISprLWstELKWtg2iVuE5mGyTVxd3JFnVUC0/Msh3V'
        b'HtUW0xGDI8w6vu0R0Zer8IiS2eIPmT+Sb3PkvEy5S5bCJUtmlzXAouyiB3QpJ4+OGClTaiFloj5z3zH0rmOo3DFc4Rg+Sjmou4jZ79n6SjkKdPtaFbpMIq82r2xdib+4'
        b'i2pbV8hsfdFHMpX+jU7bOXaZtZtJ2dKF/WH9NXK7iQq7iSIdpbnVXsMWQ3GEJExq1WvdZ3nUoU/YXyIylJsnKswTZeaJOIdJi4m4VJLQMV9u7qOgCWXQWbMWMwlbbu6l'
        b'MPeSmXvhM6YtpuJa3JtD5OahCvNQmXkoOn3f3O2uuRsabJqLbexay/dWtVRJSuQ2/gobf9ykGCBf1bJKkkODygOUjoX7AJNt7Y4nGqN2I0mi3M5XYecrI5+f33N0R5O3'
        b'tdYBTZcdS/Fwk+bQVPLozdq7K53cBljoN/kywEL58DyDthkc+rnpyGq49xL8GGu3gEXimGRL1i1LdrKN3i17BjreM7We5knd8/Sabsy6b8RARxpAtqYBZA2sWlOHUWQN'
        b'oFqz5E9B5WdeHLFoWkD/G7os0kD0sdGMLLUWwm0YjFZSNBitAqSnzGYwGMQd8394fG4+gOgBqWMGCRT1ImWaYMrisR7oqw27BjmlitnU4D8NLiNBh93mamibmKvpqYBt'
        b'IxWwzSTQNga2KcKOwmqwLrMisDabSW0dBkmv0jEYxTQNndEZAV2zV+uoYO1R04bA2jnMUWDtvGqVi+FQVJvgu4UqfFJj4fZ0rFidYyijRq0KatUqIkCFuBYXVo4KwxVh'
        b'RJ0rWESQt5o/wM//HWgZg/Wj3tVPXT0/LmHNICiguh40pktXCQP0qOqVNI46OqzLTawqKQ0fzy0qrCE4JP3ANaXVNaXCUlL2X7PcIw2oQuGH88GPBp+j4kcn01WBs2po'
        b'GqPBf4Ze/lWsUp8aiVW6ZtVF4nnxMrgON6CNTnYQbMpEe+Apap+E7NRxI033dvAM4KlScJZAk7AbbiP0CoNwGsbKYEN2jm9ZgjZKWA+PGIAm8IIJrc/dk1Puj8OppVJJ'
        b'DLjbB2whauKFrkYUx7iERZkXZMRUT6OEeA40+Sojx6R6MYtiVuRPY1B7Pq1LRWdXoB3SRn8gxQZmDXBnDob0MjPITm76MBc60AgPoCcYou5m5ZnAw+i595LqTId7TOFZ'
        b'BtZ8T8mkMsuhhOaIjEj6dWUCxWVTIQWlYr0xDrS2WtkWn0uSD83MD7vM6GdQBWsXjAvRL6CTkw/Ek9Q1QQsZitj9uhS3IDp1TYoq2Ow6uA5cD0fTFTjGDKPCQL9t3SR0'
        b'Pgw2TdYmYIENgemZcBdGJ4NhU9oUdcA8KbyGW5s/JTU9IJ2OSAYvwp0m6fA47CPeJe5gM8o1wr9kVCNMsC/NYIEASHkMgnWAy0Zgiyaodx7YT3bhqqDeW8E1Gtg8Abcw'
        b'NfST4JoTjeFNp31b0BZ1Czg8KmqKIVNfDW0lWAeusUsNVoFuf9JaN9ksir1stw6mbhFk1agQgvgFdFu+Xz096l3mfAYVv7ZenMfUq2nFjvA4hadDAFXHKtBHYAPQC/qW'
        b'U8uhFPQTiMAvJY5oG9zZ9VR9GuikUYZjkfAABg7g4fnLqGV24Dw57Wg8heAGs+BaASVA+/+rBAOMgO1FWLeCuk+jLsVeAfaMZYBTcB9soZFVSR48z9cO3OYLD2OYLwMe'
        b'ITBfPbgAmjWaJ3DdDyufdH0E1zdX6wht0OSvW/dmU+vVyndDzF9Om3LmWgX/9BvjPunLOhCU4CpJvHht0hHK2WxSM2Xfg4OSPEr+dtL0rPyOyEf3fL6Y0heYc+3cngLl'
        b'J+/9vvTljzvX3FkTenZlwW8v1yTHHK5YvGZF35izn0kvMiM/rX9J/O33G/Yday5boDOp4vHZCb1j334rrKCs0O/7kyYyy68C63b8Nv3wd+/sW/DZHOMri9/c/NlLiV/P'
        b'bJuw5NwLA3ccjbO3vTO73XJj1xsph9uKfkxd/pL+Kt2knZ1ZwoJvfkjrmPDp0q9YC8Heh5f7y4M7zq7426cZj/++sy3i5vefNEyIurR1a9PRgM0/HWNZKze+Hhn7w8rU'
        b'n44Hi4/aRG1MSkmPf+F4+0svvJ6n32b5ZcfpuoivLHJ78uN3HDO/tT/9RtKmKil7+5RHuVOuvrQ93K/YK/fnMXZli0q+d/nFf0xfv1VFj8vRKYHN4l1jxPvnnFjf8OVP'
        b'k5fXpNzdwbsnEc6pC9oecf+fr/969cDHv795dtvv49+8feTv9h5v5hr/8uXrO5XvrT6Qs/vGyjqJIlaYEL547s6on07kRH/n89MbX0YLFx5pBa3Ljr2oKLgV6TftlVci'
        b'/pn8mnJn96WPLkhuc99796PrN6c9Me5XtL3al+Jxf+HJnLqTNTO+eWHcBv+LyY1nl3Zu/9ff9uSyrfv1U18r/KH+vaLOCwdjLY8FpeZ9Mf3s9x3N55s3ftZR4l391gdu'
        b'f/vxugFY722+v+XJ9i37k1eXPbp4Xcf/4qK6Lp4NUSAWg8Ngt1o5mxVL2G+kC2m22HPgfIqGwQaeA/tVGtqzQEKrzK5zYefIKHFM2KwPm2Ebra67BC7Cs1rErQucme5g'
        b'PewkutbV2ZRKiQsv6mE9bqoD0abCqzNNVdp1KHXCCnYhPPuEiNnH0Hw7zCsY3Ri0g8NqH6sL40kZejXgKpqRUjHQyB6Tl8oAZ4XOtDbwBdgFtvKJyQY/0I9BwaNgixHc'
        b'x2KCfniNVDsRfUWzEOhNx3VrBAdLGOAKFIPjtGZulz7Y7J8eSGdIyqUMjJhgF7gST+vh93rD6/6oVvjJ0Dg+TBk4M4EI9E0iLZ6WCM6RmNgkIHY9bGIGghPmpGLZaLE7'
        b'paW7NoWXNOrrBRXkpQRHx2FdMpBmqJAJM3i0aCxrNjgOdxAqGx+4z9ahiFZB7sxEszhas/x1KUewjw06US4xUekuAZvscQGZGdk6lK4TeiFnmCh9Mk3i0+uK5i+1rhR0'
        b'gR4tfel1uI1++S0V4LrZslE0pqCDj14v0XFuhkfTVfpSLWUpOF4ZF1pLbmVVXkCXMExTGuWHdaVTcmmepSbYv1KlpGTA/fA8raTMgWd4rv97BeTTN1+4mbRFppFqSXUI'
        b'cG1jv3rH4a68WolEM/mFKmxcRQGDsnNQmYjPl9sGK2xxCDiLybRWKvHGfLlXltwhW+FAQlLZOmOf43Cls1tXfnt+2+yO2aJkUbLS2lWUL9GVsuTWAQprbHSNs/iJ50jH'
        b'yp3DFM5hKAvhKC5Dt7AKVliRW/grnT2w9XfbnI45OIO9OKkrvT29LaMj466Vr8zKl9QgXu6QoHBIkHESaPt0X0mS3JqnsObhIsKkU1X26ZLQtqiOKKntXccQUSI2U9di'
        b'Scdm6mFPnsahPnhQmamPIFm3dRigHFB1HblYI5tDO+ZPkbtMVbhMldlNVTq4dvm1+0lmyB2CFA5BIsw86+jS5d/uLymWO/gpHPxEiUpPn57U5kzRJPHYh87u6GltncS1'
        b'LStFK2k96jRpXV/d0VVyrwlyt1iFW6xYV8n1FOso3bzQX7bOEnbLKtEqJddDwpJMkub1TTs6V+4ZI+dOUHAnqHOpsuIajle6uHUtaF8g9erTlbrIXcYpXMaJWQ9x0D6W'
        b'dZjSN0xq2Bd+1KzXrM1EzBaXKx2JjiJM6e51xO+AnzSnO7gnWJz40MF52DPYOuL2yKR7Bl/ukKFwyJBxMoYpgUZqPf+CC4KLv3iRNKk/SeaSIHdJULgkNBuJ2KJSpZWt'
        b'WB+rz596oZvPfbfQu26hcrdwhVs4umZGs6nSymaAMrfwUnIc9ma3ZEtSpSVyTriCEy7jhCs5bqJMiaeULecEKjiBMvJ56OAi9mzz7vBGD8uxJdckSBZL3eScAAUnQMYJ'
        b'UNo5iRKUdvbi5DZDSZ7czg99s7UTh7csFS1VOnHFDKWTs0SnLU2qK3cKQt9QIWktaeJiyRSpm3RxX0L/RFGanBOn4MTJOHE4NbMlU+Il5/gqOL4yjq/6pklyDk/B4ck4'
        b'PHwmqyVLEiE1VHiE9yUrPKLlnBgFJ0bGiUFp9zledzleqF05/gqOv4zjj/Ont6SLazHLN8dTxvGktUtkRxPskGjNgtbsRHs96MRAR1qVZEOrkjB57KC64vnojkad0nDJ'
        b'I5VJgwql/9fee8DFlR35wt10k2mCyEEECYmMCBICEQRC5CQBkgAFsggiiSABghEIkRE5Z5GDEIgMAjGu8nrHa3uNZrUzMrtjj8e7/uz9rdfI1vOzx7ver85thdFEr9+8'
        b'tb/vPbp/h9vd5557Tp2qf1Wde27VO2xB6csATE6BWvkm78WKEltOiuHz+Szu+X9j8bU9IHGbkNhMIKa8JZsDK6lPrRaxRH2cZ9xMRZvsJ1aLBFXSVRIvUryLV4x4bM3o'
        b'ssKr9aFPJ3r/+teH2IOOHp/3oOPL9aHXed5fPbfIPe74NT8pLD7nZXx28XmfkyXM2tBTvKOd68oX7NTnHixmi0hU1S8sxNHBxpYt2qTH5rL92Dm52SkZSV/YBXFg+Ne7'
        b'0z+dv0j8+58QnEEmOM+BWUT1sHD2s+4z2chVX/Qc4ziseHOeIDzEqdCXyRM68Par3aJjuJYn3tgwCN3Y5vTp5AwN18T+9yMyol/vR8U5qHydG74BKlJ6w97i5zBeeV8/'
        b'/U6wreItd+Ve598oC3UN4opKtnblNeXl5Z98y93og6e658113H6eejL79smjP4i7fC3pp/3HYzz++vYP9P9jUeNnaQ3mNnsXvxUT57/4N014PfoXqy5rHv+j4tsHvvWz'
        b'MYduvYbjFp7PflO37zemdxoc/mbve61xo+/by2nGPtwX9law7MWMEylDk2MzGUef/8F4+9LemX0FwxNNP9q6+fHDjuFr3w3wir0uaLB69wPVse9Y5Cu5mElyMRuUjkHT'
        b'Cy9GTp7bZHLTmLvBncK2c0fA1JuxMiWKTbBCbOu2x2Lnmz4Mmcl93G4heED2PmfHTl26/sosD8XpT+wqMTzO7ZBRxGa8xe1WOQztL3arSMPY15xc+LOWo2IeJ6ivbMe9'
        b'n4LeN3/mrMdf8cTW44mE/9VnDjWNG4sHwx9rmj/RNGd3tHQ787ZVjen91MSi8WSnzmOxElPn7E6Xp5pGjYWDphOejzVtnmjaMGPH+el+m0HXOa3H+4892X+sU+apyaH3'
        b'TZzeNXF6bOL8xMT5RRtkXW6rHnh6gLWp1RT8dL/FuMuQy123Ebf39zu/S0qVu5VIZkPUY2XDp8p7G0VcHmVlsydc3H7x+xMP1Ct94vm9V6D9J+pMLh7apxSiWBM+Zprw'
        b'y6ejgOnCu5/QhZnxX7Mu/NoU3e8Y4fg70oUpWWxd/i8yNRhL9zP52Qf4suOTU669CNH+Ip/jG0HhP0eHeYqXzNMKuDX2lPSstER2lyAxwegL9d0Lwnw6tDh9/QU3Mr5S'
        b'YwiDueDZHkkwRT4xrJHjW/eZFc/XD4nEacqkYNe1lLcPKQpzTtCJ8b17WawscbhADRu7GH5f4HdKPpr+cbbXiQP3ZN6/+wO1bwWPmTtISYUfCao78K8yR75Tkn9EcKLe'
        b'XsB7L0x+NKLcTCh+CLwrINfC93Tc6w18cAsrOXS9hm2w8jrIMX1a5ZaIoITPrVYcgQfYo6b82TUiGXWn5+whoqtGuMSU0iF8gHVWWOUnvkfgF3TVyhwa8Q53QgBMS8Pc'
        b'Phj48sxrO8qx4rl+KV85r3Kgvbq1+akKHCC6vQBE90Q+T03jxSYPk9f5eF6g3/G3TT6Jfh9omIlvQ28rW3w2Vdu7XwApn0nVtiP1iVRtX9TNLoU3UrVlJhBMMH/uS4qv'
        b'NQcPN7TsB3y2Hh4cHO4dnP0fbKzKX5GT53U4WRaijIvow8Uo4Z5/5u49c/4CB5UcIcy0/7wLNtq8T6Xp+ayDY8fm61MpKRTZXfI2wacy98iyzD2s0BBn7tk/eH1bdOix'
        b'6NAT0aFdib2ieP4u748tWZYem9fnub2RpMePJekJYKlrqHzOlVyenk9m0GGZaTRZZhpNlplG06nKZ1dGiSWZ+dLC8Euyz3woUmOD2hbpPxbpPxHp70qIRAa7vC8r2CgM'
        b'XlXVf0GWT7Qgw7ISvVG8PoV9o/aSkjnbIovHIosnIotdCS2W3OYrC9aQ5av6h8UNnZuwX93/1GD/hNocW3dSJAJR8ZwVH7qffOriviso4rMG/neVzyRfXm9XyH1bJBD3'
        b'LH5CMBe2qraavH3YZ1vk+1jk+0TkuysRwp35310y2vnxX3fgwotO7p9QnQifM902dX775LbI77HI74nIb1dCQ0Sw+acX7Gr+/FctuYmvFbYtMnosMnoiMtqVkBNZsuxI'
        b'ny7Yifs+W0EcvoUFZ8MN0lRNLO0R533hEjsIDLGSUDjGMzWRvIYt6nm/JnyCKoPz5AQ0u2Zij40yVOAKPlQ/6gAl8TgrdQyroAmaZciv6MNbBiLSUuUwCPeg5eRJGJKH'
        b'Zqjh6+Ij8ugeiaDrGC5CPczHwhJOhotYpLgynHV1gUcw5wuPfKhWA9YUwApMwj3rIhgOhPsuRbiJ49Lknk3Ra/0IjMIwjiVdtTuAXbZYgnczoB9v4yTOY0+RK9TCGPmP'
        b'DzR9rrqEaEDtfizxLE61J825CSspLlhxxUfHIFbH+1iAZKTdDesQGI7Us4IWXHIhi2IcFqAxg5yjJmpm2ReWndLNscEuGutEOJaAc6rkSA5CMw7R6yG2x3hi9yn71GNk'
        b'jdyJxxkp6IdlrMgkHd+E/WE4A3PX03EEHhWTp9oRDk3aOHTlPLbDyFF1vO8LD22gjobfBPUqJ2E2DMpMAth2cOx2hNlinD4NXXwcIwf2FrZCL/1vSIYJ7Iah6/oCeWiF'
        b'RRyws8RhXE52lHPBJaiM14MSn3S4nUDNdgTBhlm8d6aBN9an4CPs8ce2SC2YyffAVZinmZpzlYLO02ZnaOi10AblcgfDcUEL7+IQfVoJgkrojSB6tEGHJa44uh1wNVZT'
        b'xfmz9EXvDZPzFtiFU8qqWImNsBSeQ982KcrtY89AEvEewCx1Z46HHfaJzth1AXrsYGMPDijGBUF9Uq4bloRihz7URjvI4Bas6qnCahps6UJFEp1+LwursdNWD4cS9p2N'
        b'cj2ELcQKqzCWE0tc147d4QraFwoznG/got7FvdAdDEPa53GW7d3HCRkazCKxVDcOuWOdDFR64boNzWQ7TDvRKO9R/1agLIJmoMHqOLOl8mFeUxdriD4PcVDxLQFuYLWP'
        b'MZRAY1498b06jXIA+kI9oB57iJFbbBRgAxfUi9xpise9oEQferHTSuEw3qdJegD9Ai8Yi4/dbwaNyUKoNbx5CEYd8wqTlbCNy2kxQeSty4o5B5vqEdDtDt3kUI9AWSz2'
        b'mmOHxUFcxXVYEcCcLLbq4nKsZBb2weKZyOvHsac4LA2msYeosWlKQyEmwZmMAGdqol8PerD0VAS13RwBHUehEyrjSABLJZyCsBnmrKjOPE7AVPH5YlXliJtxh32SsFel'
        b'4LAKztB4a4mhy9gjC0dIuKp9DAKNCw4SvzVAF96zJVafJv5cxapYdntrg8bkhQ+hWhpH3bD5BgzkBXik4IwJVppiFW4VHbW+CRWXZMNgVUufpZXBcRVHYSZuxeC8BDbm'
        b'a8R64W1YkIO6t3yhE0v1fKA+EkqwPEEJBmAiJOyMXfyeg9o46eEjp7bH2kZS1/4MSVFfIFaF0Rx34pQWVBGylMTimANN5kOyu8sF2BwMTfjAEHuDsSYCp2BBqEL8V6MJ'
        b'QzQMBk7l0XaMslCF92Dxer423NGn680QW03kE0dUFqrIkEQsXMZWXCuyUwP23MFtmps5mvMlmSRFfxzQhvs4GHUWp0nwynHF4CJsBgXAFozLGkNzDsHCGFQ4JeJCOlZH'
        b'wKa1DrsXeyEEVnSJ66bxTig0B/irXLhOxv0Ki3mJ/eehlLhri4ZVaofTqiZhxuohUEoEX4rE0TQi3UQIzJvhqiR0xhnD3WicyntPgj2XjOs0mX2hrtBAYKxAn9csYDHP'
        b'CXsvCKndQbydEQuDV+VJNDuOnLKEMeWYAJh0gzpcJmptYIcu8dEjqKGhzcOsH1ScJ4kt34ebvm5urtjpD8MJynJYTvw6Shy1Arf3Q7chuTXYIeEGGwU8B2s/bLmSa0HT'
        b'tgBjpD9qYJ2kp5nErifu/MUMwo8hS+xJJXI/5BEj1RCnTsEwtGPrBS/CxS0LzXO5Fy/BYBD1cAQbcdGUJKPp+D67fKxTk4W1T/IrSUf7KW3qx9J1LLOSvQmLGRxktioW'
        b'QBdh5ZhHoEOhUTzMBd8o0hBc8iFZb4FSTSi9TIPbokbGCJ/KHNyIgzul0+EOjEdDi4imedJQBC2O2OULg7lUpRTZaAawn3TTOJQoSWCZKyHJqLo0rDjiutZBYoh5WLfD'
        b'R2rXcThDvUCYnIYlwB6hqsBWJSLWCA1xjPTpwima0SEVrIncm0z8VoYP3GGEyL5xwYQ01P3IfD3i37vprtgYQ3qswwwmr5NI1FnTdAx52BHUVRNnkv68cPjKEWwyTcWJ'
        b'4hOKhdTBMkKlBuLoBVtD04RYWCDAWVFQwxZihzIFrPKGfrtw4gm4W0AdqMYGU1git3MaGgpxSFrXmAj9EEe8Iw/BI+yV8zanAVcQTg6S8u45CQs+SaE0mQtwKyeSprSL'
        b'1OIAPCzE2mvQeVE6EdtdL/tYc4q9ISCXVE5FHqFCI9Vpd/HRjMAO6LkCNRLXtKCXOJwoSBwO/VGp1MstHBAcyPT3xuoMETYlnpPeewlndKCDcdchkughbxVolsj7O2Jt'
        b'Vbyvx8A2gzMyNnDWApf5XvoxMCiNXaFyfHjAnqWuJ6nphMZcmOcR2BqrY4ktkbdT7wbel4Z1GEn0MYVuT5hWJYXQrU3V6xWxVzpdL5XYpluJpLHTzgwfnbH2hZ7TN7BV'
        b'D+r89Y+SLliRI8o8wlrpUzAZw6Qllp91gVlEfRk4iw8vniO8YPB7j4CArJBMB+hRdbcI3YOzkdAUcxJuecG6Mg763DxPZBk8ekMV6sICI2HyAC7e3OsZQ8AxRbMxnU40'
        b'mYae8wV8bPe2h7VwmxuKnlgKPdDpFk+q+RZN8ZCWCtG6AkcEsKWCzWc0lXVI99WoQePFwNhwEt1N+9PH0kiIWyKgxRrKAtUOqeFEGtxzJ+GrSoXWg3jLk48lkqdgPeEE'
        b'tHmnwIJbMDyEqhNOnl5v6WCXYzoL7tBEk7AKlbx0UgFD+EAKBkkIqjVIWOaJWA3YawebUKdNctp7AB4W4/JVN+LZTlJ09djuchWHPAhTShJO50OFTybx/2AxtBerE1ct'
        b'JRTgZJIWdhIK3iWgqHHGO+dUHJDYvRFHfMg2IoYeNTxKfeijo2H3o/k+yqQUT+rAQhhx4QosFhwmqd/EKU+sI8KVk8obOKrPzLJsqLtsaMI4EZvUjnNoMETdLIH+FGiP'
        b'Uym8FoS9dJVFkqoOaE4Blgm5BcskoD6PSF+nfYOG10P6c5rUZk4E3LXGfhzRChGFkaYYT9XAu4nY5kczPIYPL0BfDHXxvhvcJxmucoLbyIR8E9vPUBOVl5KvMR2Epena'
        b'uJBF4DKP5cbeUXI4p2vrfXovzOF4XjOznuu8CAf7QmkM9QyymQlhgav8dKwnE8LV0QJWbGDumryJk3Q22bGd3mex+QSNBQY9aI436dIL2USlZYZAEfugwh7LbGOhj65d'
        b'A3NZN1wV9ANgE2fjcIDq3Cfw6LhpACUWZ2nCV4WOBIPtsGbucBynL5KZ1oZriWRi1pMamyINvYQEamU3rbB1D7Ft1YmLMOiP7aHupFobE92h64w52Rwj8PAYXa2erJFB'
        b'2FBi6gfuKkNdFk76Qr1tPjYrBhkkpRPYlUqTjPTfkIuGuQPHTgZquYqIye5Bm6LVXiHRrU9ujxMuGhyUEXjjLSMWaeMAsf6oii4p+XpqduYCll2EVg8gaHIjVUjoREYC'
        b'rkdjL/Y7XyXEaoNx0icjZPDP0UzxT1mdhdoDGaSqe+BeCJZF4dCFY1ATaBlElCuDas9U3RCf08yMqbn4FozFmeGteChRvWGIHaSxms7jcjZxT/tpnI7BKisb6JAgVhsI'
        b'xEoPYrAtgvWZpIvkmjQSdFdraxGVF2OwxRkrYSDTkag/YQcVbsQ3I9hkG6l22cEpJA5GYnA18wLh8qCzktwB+6Nq2vZmBOqLClitejLYhPTh1gHoPUOtNouIuR6lQ03o'
        b'WZKS9QsweBDG1BLwQQZdsIeG2XeJZGH0fKI6AVAzzFjDrDwRswY7kqDaAOYvZl3SPA5TaVRpBrouE0R0CVKpVyVhxPKL9tDgCpsmpHHX8PZNNXzES2M7uNrpt4m8HWZJ'
        b'9OBqGGPL0gyOKzeJK/NxOhEnCmTI8ilTvUEULD24l0zcRT2bPdiiTLbkudBCX2i8aXDgRh5UxGqdilYIJSU+zF5QdoSwv52QhE5zZZZTkbII7uXTzK7jwNnj8qQsl2FL'
        b'KQZHsSuVlO24JJbkYVt4ImzeyKCfeuIukjVznzMggAyIh7CZQuy/EKeF5dkGOGpKbDHEktOFZ2BTkSHhQy+zd5OpA1WXjqVrydMZTYQd7USO2qBIsvWmisOKzyXn71MI'
        b'RjJZh3F0H4H3+AW3fEX25DIw4W2E1Ywstz2wrJRLclKaTUZFY0SwvawxzsUF4y1oD6Mqy3CbuZ8ER6JErDptwfba3YLKLOhWIo/lNvTn43w0cevcIQULfwKprhRl79QC'
        b'N/KhhvaSoM6yzCO6pkKiZ5sNGZ2NmmrQmmFo4EUSe28vrvkQet0h02WRlPJ6BosBgM1XD+DYfvJzp/B2MXSbWhEIrkrTxcpwzN4n0T7f6MJlkvVSEoiyPJKFbjlotsX6'
        b'K/bYE3iAxGFBVSUnjkBwA6eicOoiSc6IEXFh71GyWlbsoRJXszJgOJec8SpymjVt1Ag0O44T0i8476duNybDHTIbJHHiDGnMKmLWFrcruHRGG8uF0Mr2o7fRuFawm7f/'
        b'umtWVI7GKZrjB/vMSWL6oCkhF3rd8qFmP1ZLXsDaVOhyobrzsEiWZwdWnyVVUUu2Sa9aoCIM+B+8GUJMeg/vF0amEU52hLl5HWUu2rQTjHpkm1+AFWKrhiB4cCNF7TLB'
        b'UJcS8fiiFQ6fLvLBFm9z4or7mvuw9FBg6hlk5ludmRS399sf6r0C/CT3nOHxD/HonGnY4gKWyKhhM4u2AvOKPP4xslGJGSrF4Wy7yM7rCrCQcD7K47uzqAjdB8TbyHtM'
        b'XAKspK7l8/jH6WtisiHuew+7s+weJx82A3h8fxKpQ6e578/z2J5wS376IS7Ebj/0Oub5C7h8gvNSRKIWvENi0e2uQBSfJfu59i05g/Oy0O4cqhSrSsqpyZqYYYjo1Mas'
        b'9oN42887CCpS3TTMCG1WcFS7kDTUXej3U/Y4TxjeCL1x2EBGC8kwDjiwtRdywZvyrfM8YUqDGXrFMJoYi5XycDc7lgSnBbbcoOTcaWwLppmk30kcy73ocATGeQSxlWf2'
        b'ECF7DtGE9dlFGRPfle4ln+CBeSS128ALoWuWJxKqzpIWbqGZJj8npQgqrEnDNoVD40FyF+aJH6LIiGk6SPSagWYncpbKc6OD4FEAMfsIy0ZIbDWvR45TGTlnVU5mRVBp'
        b'TxbcOuHEHCmEQZgzInt4ArocEx2vCbBBOlEJO32vwKQDrmZbGODaJZyO8lOHSemivMSg7GgC0SYYkWXLB9Cpp42lRNxpgqNSAsixC1HUVh3Rsz1SLZVEdo260HiEhjrm'
        b'qiN3TgH742M476tbgGV25MuUEFVmkKB0yw7qBDgXaR5ih+URBGt3nXHuIInNuL0FsNARk9DoTCZRA42nJFszT0i6qTGHxjACmyfPk0XZAjXm0C+N91Kw0RfajrP96yvU'
        b'lS7YlFbH2hijeDNPXbwnA20x0JZNYrJpppiHk/HZ2ThGr+ZiEXW32uFsBPmRMwTGTfY47+lTpHI5AZZMRbCsiAO+JFa3juLMIT+S7EmoQLbAU61ELvwilOpALzmPUdB+'
        b'3Dcq+Hz2uShNsomqSJevaTpia/Yhe4KJ+WsCQodRuGelQUKSjNNHyRtoNFfFbk0G5KTwKm1ukowuHSGDsZotSZkFXyaFCiuHoCeXGKoSVs5DZQbp8BGYOknSOxNwE2ai'
        b'yevrpymd8T/GrcJsCAhDB84nkZSNQsNRTd23LMj0XAxmjgQ2XYaHOGRDxRZuGmpAe2KOZa4W2VzTbrh6SYSlItzgQ/+lm+fZgk3eOKkwHxXbl6szL1dmCELvuxm6K13D'
        b'expSOtfxbgIJRik1vxBHwPzgFJ3sr6bhQc7LFnRkEzkr5NUko6IDQwl6Gu11iHXaYVYbx2y1AoxcYOEGOQWVEVohVvEe0qTXVk+f5ZZp5kMM6ELd0OJARNmQo0HMZxDC'
        b'DBGSbCbjch4sm7EUTy4WJBpj2JtBHxquHYZu0msEUY2MVYfhgTnct8kki7//GM4nnCdCVwSd1WQGJxJOj57jk9G3QUJdqkfy88CH1Fy/UA/HLQh5F3BY9SxM7CNYrYce'
        b'9+xAMrX7k8gALXNn6PoASovTyMrXdSdrYVhbiREsEMcL93jKwVT6RQLiOvFaQE48SUDjlQPULdJnePctQoI1PaJXH7m5MB50iZeKlSfSCHJ6L51IIsWwgL2J1MPmXNLE'
        b'ZXRGOcskGp8As2mnjuKipjI82h9FzNCphqMe1owi5jipmYhrKcQ3zNSfIvdhIxs3L0m6KGOXri02h2QRpNWp4tAecsJabpAtVQJbV8neWTwOkyohpsftjUn/DmJbpAze'
        b'9ckkoveYmuTpm6VonPLZo4KDqjfzjomg4oREMPH8FDFgNYy9RUBwN++sL9SeJ6i9ZQGraokklhskF8vF59JJVWZAvQAf0Od7ZOitxV4jsO11LYrA0UgrQqVunDaDhycu'
        b'wYzBAT8ChRY2wTQJjwjXuggcZlRoGJu49dapQGp05Ag0p6v7hNC113WJHg89YdWDELgyWnLf8Vwcsc17Qrx61sIf+sJY1LsX3u05uvYd6DhswBzcyFB5PiztwapgmJWy'
        b'gpnzUhowiQSAi0eIB2adzuIm1FinOBF3NnGrJlP7rAjD2Cpdl4ollBOkEXtWwBw5B/joeoiVGU3WNG64ecCkHnQp6ekQ6etgMYFkdfi4Cw8mtQlVpg5AlxOWGBHSzcO9'
        b'CBw4Az12kQQ6lX7QmxBJ+mD2LDNOhvBuZLaJpCDZBdsP4Wg+VlvD/P5wLMuwgZHUE6QTRmi842S29noT3MBaINZYRpLW6DEnYb5tZXQuGUePqkdl46NgYrV20hvlh9Vk'
        b'YCA1g7ykDsKIIZwLliYJ2MoKIb+9ibilDkYKadCkqXRw7BC05ZEu6QhOJV4ix6XDUpQB5XKGx3DGKQU7/TXSYQMm87DHCdY9srGDaNeAc2f1YSuc54i3RTK4JaBeVgSp'
        b'w5okWxkZdoKxJA1faPfS1XEip6uGhoQzzoThG8QQsyQBK8QFm1fJ+7ynSkTviotnUnM52ZQg9Y7EBY+kqwqwdB7HUkOCUy5fIjN1XpG60E26dloO5wOgNh46zlpoAjkY'
        b't/BOqoLAJhbvhUODqnvMxRvY7x+01xabbPDB3uQLWG8vwQxXQqBy8qMHcCMwv4jGXxunTJrrLj7SFx6AdtVQrIiP8Ll0Isib5LvOFdtyHBNwbR+h0X0WF4h8Q6logoZ7'
        b'8pF6HLww1G4lUnbGH4YHuLTPjOS2E4cLSNzqYc6U/J9aFWlSjlNZEeosbn0Cbp66SrNzB8k2aJSF5T3O1oRn/QWqN5VMSLa6CGweWWJVNPQfTScbpQE38k4ym6aZDPqp'
        b'N3ib3NtlgYQm2UBN7krZMOJ5WE0q1YQwt48G9IAQsd2W7x/uxzyoeFyNxwURidYSjf+upbMiNupF7RUSm5NVhnVkxd8rJJq3HQ6XPQP3HbA7gji8m4B7XZ655TCtd4aI'
        b'Tq411GtgeZg3M31UqbGZaAMYtcMZL3Mke8Z/L1Gpdh8MWBuQhLa5QI86kacnhxTDeCI8iNAjXu+WCD2sC8PaTlASB9WHyPh1JTw0OGOmS0jRnIxlsvAgMfsmqa4yWIx0'
        b'IL2ykMhAvFY695Q9TCocJTI3YJdWNBFqbQ8OJanjfRnTQg+Xq5rQdxRmA4uItUZJ941glzYu5/rj5B6ydBpIjT5MJl1QKOeZTfPYT40073PMhRFnoS3OHDeGCTc57M3F'
        b'e8qXL2rBmIryVWhRx7qAJGqoFFotpe2CaE7J0CCyrAoNg7Lcj4am4v19hA6TJEi9Mftwy5sl0YY+Pw9XHklHDYkm2d+EXc2wLH8ZK4+Qfmbb9TxhTkeWT3CwEn2Bm9dW'
        b'cl26oVxF/Ryp8TswLAO3k6HCCSetSAFUvXUNmh0vIFsqH+LBwiVnXQKVdahIMSFhG9eCu1Yk6V0kF3PkVvfGyGofwYea0BHuGJDlQ/pzAiZwRkin3IIFQzUncjmGYcwD'
        b'piT1SJ56YeuAujaZsnfMsbEIGxlpqq/DvCDroDN92+QCQybncI0UJbarGLsYY78jdCZGEN9UYXs2KabN/PM4e9jlDJSl5RI2tlrzHGAsNl8tLo6onpaMD+FOHMxdJeO5'
        b'icy3OywL3zGC1nJjJ3IL17Ay+1jAZVeCgiqsuWFFxJ1X4BPnTSkww5gmsishJ78YVkPo4zB0B5KLPgCzWb54/xynFhfxoct5N+gwJZVJ7q+PKy76k/k2K59gS3ZcZyTJ'
        b'xpZ0HBlrJfuIyfKEJEg4d30PE6NS4mUmR5v40IKwuJNYc9kJF7XI0I3AFrkUT5g2xh7PQ9AkIO02KGI1XJVTyFncuJHk60umQJn/GSdDrCjMJON6E8c9aPLnYUAWNxyk'
        b'00jrTPPxbhiuHyiGEnL72g56K8mHYXsCd39thq3037wBrbDOlrSGYS2URkgyMsZWi8jKHYUxXw3sKgg1iTpEY2vDKRcsvYn1uKRHmrHqAgycIUNryUoqOdNOC+Z85Ujo'
        b'71HFO3ZE1oo0EoBNJRy8COVkDcyRbqm3xUZdaRrjqKwV3i9KJvuvIi4fbruSSq6HQQHOa8liz1ktby3ilnumksp7cfX4GWhUdJch0FzHEh8yZaYZpB3B+zxS3m3YYKOY'
        b'eArKzweYOuamyuGm8rlCE0J4Msnd0k9BQxa22IWRP82M0AWn5CJijmoTmFM5FkACfFcT1uVgOaIgzRwnDhBkrWAPlF/C9Xw5rPAKI6EoJ5dkggCnidwVIyJ2hz72KcgJ'
        b'LmtibVRqysVoe+wOUOR7adB5M9AkBc0qmiRsLbCSquBncQiX9dnaJ+ntEtjQgRV2825cby+5e3Vxx13JdO8/TLS4C/f3WmVAU+B+Eol68npy8qDrMM1BhR8uuciT8f6Q'
        b'zIJer0JNHFJ4S5JG0OwN3aqyRSRtzWRzdtA3TbBlkRFTAP1GBNZlexxDYEkLepWPuipcx1v+WK4XLY3j4dCcDP3kGrdgfWgkWzPF8Ty24kVz/5Cwd47URBmOWGPVW9FG'
        b'pKnJBjpLdfuCaUC3zuFyoTUZZjBK8tJCyrpKPjIuL4okcgCYOiF7dMSBxrdVDK362JxIJvfSVeKYmetaxFjTxVh5E7gorvNwK4LgqRY28z4gU+mShcIrOXBnC1MN50gP'
        b'E4ClHjcMVTLGRpKBc8Y36Ode7aR4WS0c0XY05h6Mv58E96R9Y+gay2QjjUo44LIubOH40VR5GlA5DuYCuw1cGuUCzUJo1yIk37iOXQEwJKDDMVhPJFUz8RYBYwOJUytN'
        b'R5OcPg77E5BOE/XrsLkIt+ChixpWO8BDKxwyDsLaNHary4+tVCWcItqUHyRIqVYQ4lSiDnH+YoEhSfmabUgmsdyIqh31rdlGA9v3G5hhz0EvMhlIOjyJHzbVknFJAbud'
        b'jXBURF5j+QUo88Q1d5iWzSd0aSH7p42QeZg9rbkuBX16vtAhT+7BqI0S3PWwhS57shXKtcLVcWL/YSkprDrtidXyeMvzFMt2aE0mVqUTPlDKwqVDCgF2MGSPLR7H3Iko'
        b'C9AtZFlGCeorCmMMldlD/msEBWtQakjcPsMnw+zmNVtiuJZQKJfneGItmtB768pBAoRerMwkqo0xIFiyIdOj5XIyDDsSR7M1+Bas0cQFB/JpmpKgSgqGkg1hQgizbsdw'
        b'mfnmWHKa8Gsx8Dop80f2UmRVD0OdKZZZEmFmNUgGYagYOlSIL6v2sfvJkkVSDknh1HiriyK2k+kgdZ0ZQWWqRzLI4yOD/hbBRBOMqWLXSc18trsijIjXDeuXrh2AKSvY'
        b'8IZhM0noMiIDqycCJq+QxzMDw1bRZAKR2nY4lnkY1v1NruLQAej0hzELGy9ckCSd0uFnRG5tH87bkoabZDLSFbbnpD0Z2dPWuHXGmNCtIzRGMbo4XCeSeKcKS44E0jU6'
        b'97sauBfzyMSsuoKT2GRtJiHO7NqXu18cQZislzJxFGG4K+SWodTMYnPYlhK77Bfh7OGemZlAHO593S0jwJJPTk4Zj+/Iox4NeHGLWnlQ4hCA9bxwqODxbVjYv1qsFke2'
        b'3orfwz4IiXlaeHxPdtL9Au6kFFLiqwF+kjSIyheLZN0G1EFuyWsAS1MDQiTwdhSPb0c/2bmLv7+ncRlrAyWxxIDHd+JhQ0481zMFpta4ZbUqbfGy2pFr1BS7jC+xWBXW'
        b'mkmSXhzh8UN4OBTmIF5wa40NxtogKWy35FbWmrAyStzphWMwG2AhQT0aEC/FkZa+b8bPY3sOvZIiA/wlcfIgj2/BI7pqcRQlaO5ggYjZclxXgXg5DiZizPjeXHp6cbz9'
        b'SwK9cj4X6j4wfZ8iz0zAfW3lIIj4SIL7WqHDPkwcQ/lxlEBxRVw3rSNdyAs2kwimprgoCCm6Z3iCnD8QVu0L/25b619nqp5W/tbA9Q8c6n+iv+L4PbPgX27+T8WTvY5Z'
        b'c4ftJIwVY2TVDmiq/fx71mv7jN9x6vj3lqKHl97zqgmyTP/dT7/372MbK39wMjnz83b9n7e5/byjO62F/wPrsnnPioQI74TwbyVcOJgwHvg3rYHfqfvu31h3tXyw9c2G'
        b'2CDTE9GPK/UvnHD5aOrf3/kfp48MRNe0nQl99z/bT5aNp97ox197bZqsDdTYFX87LHPBqXw+XmUo5fIv26Sv/6jtd/+2lR35wyPaFhvfvzsf9c9NZ7//2397Vydby3Mg'
        b'u+DHdhZFkb95cnL5730csh9NZn7znKakwplzkx/c+/bPtpOOO67VZphWnnt+4nd6//z/SES3q8n98OM7Gcd+qvizcwfaTqx0Nw2qTqj/sETR0yfiyJFw4Q9tk6zk1Ctr'
        b'zl+xnTDtO3H9V065ek2Rx8r6f2ppmeH/dnPRoTqFtLDeH0tGuD6pXg320pP9zdtu9e/808xA6Md/JThWkLtu6/Jx6S8S33ODn+j9WMvx73o/LLh0Mmh64zvjRadrTunc'
        b'/m7Zrfy/6tK//9f/8t0PPi59lPJs4x9R4JJsP16gmHcm+crGX/21YX/bUKvkg2ntB6W/LDapa2zBO1Obeh95Pe8RTP5ee+Raz+OMs+U/f274aCUl08M5SUlaWf1kktH0'
        b'ium1KbtZ44Nnf/Fut871n7gkTCg9/0PhusqcyS+XL//9d7pdp82SogI0Un700YX2j1qlE92VnvwyxrMtSrA0o72kNuxhUxll8w+99h8lGhQa5BYOfNi1Xv8/f/vORweT'
        b'tf7xxN8VfLz6I5eua/8e+22f/Y4LF3P/tuCpT0FdR2x0ZbGaiUvd7OTbsUXn40+l/L5YT8VpvaT7n/b+60fC90Jvavyt0OXI5vezdAquffeimWTKnr8POjLzt7889fGp'
        b'pB/+7pi5c5/EzPr7/6CxUptTJFHYPeYxkOK9pXI4IOdwiPyib8Bi0S9H1aNGj0SNi3YWn7+3Gfok+Ur0xn8U/2Qo3eXXR/2d/sXwm0vTP/3PgvGP/9D6/aX5+t9/wPvF'
        b'cswvXMuWfnQrb1fhvVj59x7/58K//aEx32rxH7a+q5hxaeN9MzlxgtiG4FTCBH4wdnKoVH8U17jt7uo5im9sdSc/cUa83d01gYsOivdPw5o8tF7/dPyCl7ELHmIbl0fW'
        b'Epcz5LNFsiIyFmqVsvMUSMOvCFgI/Va9QqEMIW0D9xR+7A0zedhSfVnzOi5fvyqS4mm5C0jB9BtzIRMC0o7mXFO4mocrSmQr1SnJwHK+SA7nlK5J8swUhaSQS7Ca243v'
        b'gWPyb1YV14M7LxsOEkqxDROwhiuWXCiEdLIvBuVlCiVftiiD4xKHcFr6uS2DLlIN8zlwR+YqdS+H1Gb15zSJS1LQ5gPs3u/Ec5YoHEoV2f6k12H9xeFktbD/dUTZcGwy'
        b'C/30Jm6Zv6Dizx5+4M+7lT6Ux8U+cP+Svy/caf/Ff+LnPGSio9MyYxOiowtfHXEPcgzIvw5U97l/Jbzds3yeSH1XKC2r+VRpT1VOo1319brrnUY1RVVFnTmdOYN2g7Ej'
        b'R7oKewsnTnff7Lw5Z0yv7FWjxbzV04v5D6wXrd8++fbJd/Z8w/ebvu/aBW7bBX6gpdNp1xnbe6RLtld20P+xlvWc5mMtx22X4Meawduh4dtnzj4JPfeu5rltzXMfaBgO'
        b'7mFhQbeVjVkYxwj+rhxvj1qjR6t61YmqE7/dlebL+vGf7jFotBpV2Lbyfmzo88TQ5/Ee3yd7fLcVfFmMAzmepmuV/FN1w+39/o/V/avkdknazZ9oHq1S+JA9Pn9yW0af'
        b'O3Cmg10pgazzLu+LCjll2b27vK8ujKVlbXZ5X13s0ZPV2uV9aeEiySp/aaEolD28y/vSQkGGtffVhZqyrB4bwh9VHORp61aJdoXefPbNf7EMlTCQNd3l/XFFY+Iz9u/5'
        b'629P8nlyyrsSmRKyTru8P3/5jCufi48F1LU6jRedS5CkT09lNXcl3hKw2fhLKZ9x5XPxMfVYq07/ZceFXK0TMjw9/W0ZrQ9llbjuJ0nIau/y/vTyGVc+Fx9/6oJcrXCi'
        b'lNauxD4mbH9c8YwVz7kjcYPis/35UZKyLO7l/0//PRP/e/7mb4VynERclJY13uX9JZaDes+4/8+58pWUcBXclbjOh0qyyn9ZZWfaM+7/c6581W2uQqqY5u5SrPJfbvmM'
        b'K5+Lj18OgPvZW+EcX9Zwl/e/UGZLHGfa408rTkjwGYR+aSHFl93Pjj6/kBKxtr66MORmKlqCKaD/vvIZVz4XH7+kPPfzSUmuQ2ekZC13ef/fK59x5XPx8cuBcT+7i0yk'
        b'hbvh/INUhvLFx6ZUnn3xDTtOkSIVI8EpIoldXxkz+irijaqfLvOkTgpl6ASuDJAJkNlLH1i5LaO9G6HM22PE7Bcvvris8njKZSsWsS9Y2cj/wNx51eOJudtq7hPzk3+v'
        b'bDRo9ETZePD0Y/EToepG/xtr6/0Xau8KuKpKr8eSw+LhDHocP2HGAzMdT8GLiNhHsrf4n//A9P9pRQ5LDRnzubHi/hjfKPuf2fPJr9wilgEvJ4YlGWe+Txifz1dmT4f/'
        b'3+Jl8bXFEWd8/Q1JWQ9d3jd0FT3MBCn/JHDk55wm0sc7WqbX+4VIeCiXP0z6UUmslgZ/ZVDW+rTnhY9+dcjlqknvmJOWqsvPvjein3f0klPBs5CdZVOjd/N+e2n0R9NT'
        b'K25+8+8crLzwq3fGS07UmI7d9g8fkxsNH61LbQ3r0/llnLHPkPKhjyK/Oxrxa/2+0T9s13//fcfjmiYLCRmz36m719Y6GvZepslNh2MXHHKd7J+vjqVoPvqV0yn+783/'
        b'6R/z+/aF2t4wj73eZHU1LeKnzbHluhVm7x/5YGjKrn3qW8vPbnjd/xc97V9c+eDDUzWnOv6tbGgyKs3P9ts3Pro6t1EQ4vLb2vSPb5oe/Ntwlx942ra1/OvAr39v/eBf'
        b'3v32XPK04rnvtU78bCrovuXBjKty1Qej5ub4uumOPxuU19RfflB28bcy255VxSd/9hNeZdXV2/HGpj8WjjsiL7F3+Jb8hY/kzKbeybqjk/2PH2pcnxi21a/76P2Svq6c'
        b'Q/BMczcqTarkuZkBF5TnRi6PrfOHhHBRI6XhHrbz5GFeAieScJQLp3nGC0dYvOFZdXzAKrLkRSq4IYC7MPgy60+bQjzUQoM4MxK7LS7N88NuxT0CfWzEZnH2q3XoL2KJ'
        b'NIOkeVJCaDklIQOzeIdbCjTBXmDhK6R4+7CFH8bDYaGEOAhoiZKVF8xYYL0pi3xZx+fJWktAdyBMcDE1nC9fFK//SfKEwTAM83yYc7cRn9kj58weT7Z68bsBbCpijSA4'
        b'N5DrTST27X+Z+ArbsZ4PA7iA/eJgRmOR0MK1i3exLyjID++Y+Ql5e7BFAOvYoSAOXnpHDlcL4FGAv2XwEXs+TxqbJaRgAGa5iB6S2H0lwM4+z5nODRBHgFYyEjjjKK6I'
        b'0w51wW0PqgBV2OznFySuoYj3BbZqMMZ1ENrCMrDWnEVXFfCEp6HpHB8eWlwRk7IM+4NYCKogSx5PaAs1Eny4d9WbC0maivVQZ2GFd1jU1/STMMOHVWzGTS6qKdyHBRsL'
        b'lmAskF0yiAgg5OkWC6EUHsAtFSgRk67lrGoA6xQRjkh+NJsnbyaBjTAcxi3PFhRjRc7rn3EamnlyfhIwdx67nrNEptKm0CyP80q4lAPVuJKFi1e9NKBWScTj6e0XSsfg'
        b'DNeOVHEcl/DMgrXFw2lcI8brlsAhnL3MkVgaymDrE3nCwnGFDz038e5zM9bLBWcoD4AZU5pilvuJy4EXwrYU+MGdQ8FWZlI8Hy/pIrV9HIdJaebL4xwu6l9iSZ2baI51'
        b'FMR07nLbyx465UK4ShaZnuPjiAtMihmhD3pD2I9WLJXz1RdrzDp5QixXh4qA6xzBT/pKpNLMWLHdYFgdKMGTPSgBtV6G3I8RqjoW/laWQVbWfGzFRZ6CukAOe0hqWPNw'
        b'C0uxK4DmIzkswJrOJvmhXqvaC7Af21A8GdBhy7K+mbNgY3X8qyY8eWyUwPueOM6F/vWBTlyy8JfkxUM1P4CHnaH+Zsf/HMu4f3aV/zUZDsep+IL11v+aCcECuDATIiUj'
        b'JffFyqqe4AtXVsmu0ONJqpYEs9dTkdr7Iv13Rfp9+Y9Fpk9EpiXeT4VylYG3ArdVjEYdHwstnwgtt4WWT4WiEj/2eipUKQlir6dM37LXU6Hd9he/nwottj/v/YnTP3ug'
        b'sf3y/VRovf1576fCA9tvvp8KzbfffO9KSEmq70oIZLWfKhhtf+b92w+UdJgPp/26eKqgVRX48kW2sKw2R7F/ltegn6mtV8VTZbUqSfaiSpLqVOVDof72m++nQqPtN9+v'
        b'aLgrdfqYJDOw/++//+5/l3P5PAU1Mv9sGOCpS53Q44Eu/4QtD/QUT1gJwFyCHVvy2bGVgB3bKnjyBHCcT6XY9THfEaQlZmQPkpztSObmZaUl7gjTUnJyd4QJKfFUZmYl'
        b'ZuwIcnKzdyTjCnITc3aEcZmZaTuClIzcHcnLZObTv+zYjKTEHcmUjKy83B1BfHL2jiAzO2FH6nJKWm4ifUiPzdoRFKZk7UjG5sSnpOwIkhPzqQo1L5eSk5KRkxubEZ+4'
        b'I5WVF5eWEr+j4CUOdxYUe4VOVsjKTszNTblcEJ2fnrYjE5gZf8U7hTopG2fvkJjBMp3siFJyMqNzU9ITqaH0rB2h96mT3juirNjsnMRo+olF4NxRSc9McDoaHZ+cGH8l'
        b'OiElKSV3Rzo2Pj4xKzdnR8QNLDo3k7yWjKQdQURQ4I58TnLK5dzoxOzszOwdUV5GfHJsSkZiQnRifvyObHR0TiKRKjp6RzEjMzoz7nJeTnwsixK6I/vyAw0nL4OlOnnt'
        b'VOaY814lQ/rKP0PD12DIFbKshUL+V9xhehMYlfj8NEnmZ/yfXX69TpahrIcD7xsOiieEgo9lLpMYJMYnW+8oR0e/OH7h+n6s8+KzYVZs/BWWxIfF8mO/JSYEm8lwscp2'
        b'pKOjY9PSoqPF08xFM/shTfGOVFpmfGxaTvY32KqEFcmpOAIaF+aNscXHMi7Ez3lpiW7ZttIsECHxxltUEH7z+bsSQr5wl8cKBZ68qER6V5h3jK+2y/tEmZVHDoHK+zK6'
        b'78rodvo/ljF5ImOyy5PgH9m2dHv74NsHv2H6TdNtS396P5VRfiqnUWW5rWn/WO7wE7nD28LDT3nK2zzlRq3HPJ0nPJ3tl2+uf/8v9otz8g=='
    ))))
