
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
        b'eJzEvQlck0f+Pz5PLhJuSLivICAEQjhVxBMRuUEUPPAggQSJImACKhStVyWARxCtILWCJ3jirbWtdmbb7bVdEFuRdfdr3e5uu9vdamu3rdvd/mfmSTAIttru/v55wZN5'
        b'5pln5jMzn/nM+/OZz0z+CCw+XNP3V0vxZTdQg3ywBOQzamYTyOdouEtFYNhHzTnGsCGdSM3lAA3/mOnJSqAXLeDgGIGaZ06zgcH3VprBdxhQzRcVywQPl1rPTpqZIF1e'
        b'rq4q1UjLi6WVJRrpzOrKkvIy6QxtWaWmqERaoSpaplqiUVhb55Zo9ea0ak2xtkyjlxZXlRVVasvL9FJVmVpaVKrS63FsZbl0VblumXSVtrJESopQWBcFW5Afgv9tSI2/'
        b'xZc6UMfUceq4dbw6fp2gzqpOWCeqs66zqbOts6uzr3Ooc6xzqnOuE9dJ6lzqXOvc6tzrPOo867zqvOt86nzr/Oqkdf51o+oC6gLrgupG1wXvBgY3g7fBw+BvCDT4GZwN'
        b'ngahwcogNdgZeAYHg7VBbLA1iAwuBi8DMHANjgZfQ5BhtEFi4BvsDT4Gd4OrwcYwyiAwcAyMIcAQbHAqDsF9IVwTwgH1geZ2XiMTAQ6oDTHf47DMHGbA2pC1stkgYITY'
        b'VWA1dz5YxeD252QVWfZpNP4Xk0bhUTaoBjL7rFIhDtvncWc+xyUhZcZfPSJAVRAOwivoCDyHGlF9tmxWRg4yoK3ZMrQ1NW9muAAEJ/HQVV+0S8at8sZpUVsQOpSeKk8N'
        b'R/VoSyYf2KMG7lq0Pgtulle5ksxeQHvQNpxidXAqH/B4DNwH90mr/PAju+fcwuhbmaloqwxdhPtSecAZNXPhK7ATHpZxqnxIBq+iZs/06BicJh1ty4YvoZdxRg7+3Aki'
        b'9HqVF04hStKR56mZ+HEBPJpKiDjJjYJ1sAvnQVLMgxtC9OQ5LgxtYWB7LbBO5cDu6ehwVSApoxlthOds0Jm48Q7ovB7Wo4sV6NwK2OhgB4B3AM8K1tfImCpPknRrGDyN'
        b'GjPS4N4QtIULuOh1BrbBi+gsTkAYERn5zunwRAhukYZ0tAXWZ6Nthd7ZqXBrRFa4TACSk6xq0askOw9CGdqA2tFZtCEWk5aRzQf8WgYdhNuc8HPSfDG1sWFp4fLMcAVT'
        b'gDqBrQvXejI6jR+SasHNQTlhKfJQVJ+Ba4U6VgEbZOSgkyvgxiLGovtjzN0P8WVXdB1mAcydPMyVAsy9QsyxAPOuDeZdO8ynDphvnTBvizHfumCOdcN864E53Qtzvg/m'
        b'aD/M7/6YiwPwGCDcHWwIMcgMoYYwg9wQblAYIgyRhihDtCHGEFscQ7kby4h6m0Hu5lDuZiy4m2PBx8xajom7H4t9Mnd7D+PubJa7DT4CYAuAY4BCKc+I9gM0cvUiLiAJ'
        b'HzooSz+pzWAjmWQRcMS9kVmmtF2syGYjn/PnA/J9cZpS7rB2GegCpdb4NsnPg/dgbCTmm4+Dv+RciMrhfQdKiSBN924tauMqHcBUZfRt3ULbEjZ6TuZXz3O8Q/w4M+8w'
        b'/3E/YqsBA6AqnHTfi/x5eJQ1RuSEhKCGiBTMMLArNyQtE22XK1JXoe3haZkMKHMQTYIHJ1VNx2+4wfXwgr5St3JFlR5dRN3oHDqDLqDT6Dw66yC0tbYX2dnEC+B2aIBb'
        b'oiNjo8dGjYmBF2E3D8DXF4jQCXgA7qpKI0Ub4Da4Jz0jLSs1Mx1tx0N8C2rAw6MebcX0hMhDFbLwtQvC4Ck8EI/PwlmcQbtRE9qFjOhF1Ix2zsW0RNo5C+FLQxiNtKsb'
        b'6Qk1YTQOEb+Y1RjMXvxiLmUFPH3U8wZZgSsa0tE4zLXodM5arokVHosdZIWSx1mBN4wVeFk60ofa0ZuMPH0KDv0l4MW2dyfu9X8hqrGJ4VZGn9zc8NHdmTnI+OYW2Sue'
        b'MxKr1Kfvzpn9Xs87L7257c2yw56bP8yY+W/vli+/fd+2+M77ACiuvnHNbsHSTBn/AR2D62BHDe7FBtyKWBzwxqPzExh4Gp6A6x6QppiwEJ4I84ddCtzG9XIGCOA2TjiT'
        b'/MCdiIqX4eshYbAFXQwPSQnn4Gd7OOFuqPsBGfkOdlPCvGaFo60ZUXwgyGdw7xngVvooBzXJUWMKLqMJXsbNtoaZEQp3yngDnBCZDrMxeHTRk4aQrlu37qHLxGJdeY2m'
        b'TFrMzr4KvaZCNXmAW6VV15ALh6SeiS/frgP3ZnCAxHX3uKZxLbHNkwzT+8Uu7M2++Nb4tol94pCbYkWvWNEnjiQP3XbHN8W3aDslfWLFTXF0rzj6pjiuVxzXJ47vsY3/'
        b'inSMzgpfZIIBUZlquUaPJ37NAE+lW6IfsCoo0FWVFRQM2BQUFJVqVGVVFTjmEf0CfFEqpbgKOicS6YwvlF4yHvSxZCCvA/9M4jCMz8f2bo3L1tnc4/AZyS0b58bxH/Mc'
        b'NmX2Cx1uCcXf3sei1dF89/ArwhPNggBwwEbBLeKMxEHFhIW5JhbmUSYWFPMGmZj/X2PiYfLMehgTO2VVuRBe24Xn0p36DD5mnS4QinbAI8lr6DSxEDXBV9PxA0YGoBG1'
        b'oDosBPbSlzDf7YKvoLN4bmH4mF3j4fl5Y6sk+EnsHHgYNZL4JABPj8Gj++UV9AFsC4R1NngyZ5yAP+ayK+7oBfbBAXQ1Oow8yAGwAV5FbW4hVYRUK7Q1PkwhAMwCYI1n'
        b'syOT4VEa7xs8EzXnkC4D6HXYlLkANlSRHqyFR55HzQvxdAjkQI5nyVaZqIr0b8YieG6CYg7uEfQC/lv+PE3uDs/InkMHHEj0Ifzn4kvJmWFVAq/A86gZZ4N24z94KY02'
        b'xyS4Fa1HV+B+eJQ8uoj/4Av2lCKvSRp4xbMCA2O0F//hSu9hm+mEzh5dQeeTyZPX8B+WhjvYVt85ER6DVxaibQ74UTv+Q7uDKFlz4JVQdKAYz7kEc9oUwk20DlhUGqxm'
        b'L7bGOQWDYCfYRQuG3ROyUTOGFgfwUIgEkfD0DEorOpgHO7FM3Y2j4XbgAi8UoGNjKTiogIfgFnTWGXXr0dmVDOCgTiYQ5/ACK9LKvwzj61/DIY+8L9YYo+xhpG3S3wMz'
        b'vfLnhf3jWlTNxpOVRw+leSwQvfgJmLHLkVv4seC1QCeOS+86N4cfvvvX7+ZWcT/aqFz0/SKuv2jHwRD/TJlGXVI1bvKnrqqcvmP7YoP/rfhg5uSP2/Zv+Jp5GG2Mnua6'
        b'3qVAvu0Qt+37PyxKmM35HL2UHHH3A/u9LXt/fYKTtdwztbv4303Kot/sUC16Y/6F/RvnxCZ8cz11jpV7xfsvvWqImptwX/f6wx+++OvUP+rvCg8/B7auizjsm4blKGmG'
        b'RLTRLUwhQw1yEDEfS8LjnJjR6OgDijHrUBd8HcMgZEiFO2szsvjABp7moL3Pw/1UxurgJm/UKMcIMVzglgYEizkB6FW48wGBdriDN8IOOs2iBgz+UD08nobHwUvoJXEs'
        b'Fw+heriNFeTtKXg6bVyEjj6S5ViQIwPcIxM+JlWfeNGTjpFKibgyCawBG01ZUblaU0DEbY3lDRW4fazAvT8TC1yXfjd3o7Dfx79T0p17TfIo4O13n89x8zck3xMAJ+fd'
        b'Vk1WzSJDwi0Hj36Jy+7kpuSWxOYMI9Pv6tmiatL2u3vsE7WK2gM7uX3ucmPCPS5w82pR7dDil32D9i1qXfRyQZPIyDMWkbdTm1Jb1O2JfZKQJgan9A2/4+h10zGo1zGo'
        b'vbhT1ecYaUjod6RFdiT0uY/vSGhZ0enUufSo3x6n9oRe9/F9jvE4hVhCpofm8T223t99yQUe8Xpb0qJeokQghEE8fGXlv9UAox+wLisv0GNtrkSj15Ge17mN0I5Wg2Lf'
        b'JPelRIhYNl+qhfz/JhvLf69nlf87BYHgoE3E08h/AmL4Q+T/fw/EDJP/w0GMiMWz1QnOgPB0hbaw9i9TuaCUtFJ1SgowYolinKdK+9dzM2jCa887AdxgcXey1Lab3WUs'
        b'nN05wxpgqSkEc2psvx+XCFixdxIPj66YSFxUAOqAzaAQHRJpt6ZEMnpiMvDZurTt3ei96+s7mi83rxgTwHU/GFkcExUp0R+oj9ZciYyURM3hvHmmvfBt5Zid/yj8XH31'
        b'/VBnzlHVW7l97/BiTriXZlmnW2+UcI3FKapdhZ2chpsbbsNZCFzcFb5g43r/lvUxPiC50+XcPK6M84CIPLgOA8yLYeGJ6PQjSIR2ohYqCfwmo9fCFKnyUJkCY2RUj2cG'
        b'Ddoq5S2GVz1l/CePSj5gQZBpSDoVlWiKlhUU6TRqbWW5rgAjoOFRdHgqTcOzkgMcxcaYxtUt/g21rfr2mLbVnaP2rOl38+53dtkta5I1hxkSbzm4tuj3rW1d27nkht9Y'
        b'8gy/k2CcZrRqCWgpbFnREtzr6I/HrTiwPadPHNwZ2yuO6LGN0JG+No8PbpFWPWBVVF5VVqmrfobhQcweI1RigeUg0eNB4vkMg0QXgF8chu8pZxaaBgdVJB+he2bIwPil'
        b'it4wdM8fNjCmswNjXr4z+Dw1izTKxA+yJIAdBRsVTkASlYDHi7K0Z1QOyK0ibTfGX0X04ShbdAZE6dCLNOmkJXwgScZz+lRl6XbfGMDO2BfU8EIMLit6JboKojGAaaWJ'
        b'N0s44NUUe1KarUG4iE28Bm5DHTGYaWLQC+gEiPGHr9PEH9rYgYwiXOJMZWmitIZNvAS9hAcdhiax8Eg6vuxAbRTQBMEOuDcGt/gYdBWeAGNgHTxBc/luogs4XjGb0LfQ'
        b'sXgKoDWxqqqNwU0yFu3wx5d2L5ryWxdvsEm+kpTnzUnzMtVkvw08GIPxyDh0KhpfmtArbAutloJ1SetICy28P3kioKgGXahE62Iwh8XBF7ggrhydo2nz84LA2yt2EBI4'
        b'fivTWBLKZsCX4VkcGB8ZAsaXPUdTnkmQgfZR7YRDOSL3PECrFmqLlc+zuDHjcUNdxNd6uJ2m3jYtHEyUniMEj8qIq2BpcESbUBfRXaahU9Pw5YUiWg+EAR28osetnJgI'
        b'12PM0D6ejd+NzmmJqjDdGZ0C0zHkbaHkuWgUetyaSUoGJKHL6CDbGF2p6AQRCTPQYXgBzIBbAmi8O9qMzulxIyVHYgKTcQ9sZUHvtlr4IhlxKQQL0Osx+kIlPAO3I1L7'
        b'VK4/SIUX0Tn6AmaAllGI1DWtAnaCNEzzGfZBB3wNvozOYvrTU11AOlbgD7GIsQWdfg6dxRXIsC4GGQtn0pZJmyAAISlYUZQq5f+aFmwS2PVohw6dxbXKhMeQEV+PoCM0'
        b'uTLPBmSMw4LAUSlf5h7N9jy6ZDcJncWVzUKXFuJLF9pIE//9+dHgdnAbyXva6bRsNrEed+ZL6Cxugmy41w5f2m3ZmSMjDNwQdpGcOats+IDSvDAP7kNncbPMnMADM/Vo'
        b'P026z9MD5OaqSd8vzJ0kZfMtxwL8IDHK5nDQSZADX4A7aOL3q0VAGhFAEsv/I8xj852IthfZ4LabBQ/CbWCW8zKa9B/uDuDS2ol4nlPK/7Q638TWV+FmkQ1uzdkTMWSf'
        b'jbqx1oExOvAKQGdtcGPmrpyMiUmlGeSEe4HKsjJSh4WLHf0ATVjqgvbY4KbMq8gHeTy2pES1H7gzv4aUVHtu/iKWKNgJ19njmoM5aH0hmFOxliY9tToACKc3kLYfdWXl'
        b'AnZIoBdS/G1wE84dh2fTueVJNKXeww20iBeS5l74rrM7y+TwOHphto0VMU8eQS+CeZOFNK3PAgXoj3mdEDDNKdvUj7ANvl4AG3FofhqWDPML4as0cZnfGKAc9xEZlbqa'
        b'VDU707+jjAHG8vcJXTr/aDkbeU0TCXoK3iJjnbMDR8o4LINcfB7zZyNu8HzYCo+A/KKxlLiSJVLYiJt2AcYHR8AC2Da29NsffvhhSwkfRI52IeXZrpiwis36OHcc+Jz3'
        b'B1I752mqpUCr/O4ffP0U3LDF90RVve9kcRIcBXeOfta6PmdFAVhlNe5Xa97wyagVOb/2b6s3vXbcMb5s5f7Hre4Ri8ff3+Fql5ixZc238Z+dvDph0b+7Xn97f4jTZZ/R'
        b'MdcikvZ7Ws35ZEP7mdy/f/G9797/fP/uep/LeV8//+aVf2VU3LngLgpMcki8G7kzbsPOuIaoFd7iu4GHf6V933C2Rdw3ui3q1vF3Pmj7fMM7rzko9nw+a1zYN/K2Bw2p'
        b'p/Y88KyNqqtawW2763rhzYkrf8VZ+eakzxutlPcdk+9GZf1q9kv1SS81ul2SnKr4/d2xfxRcDFmzYLm96B3jpKMT7l/JvPnu/IZ/VWdvr95v1Rhybtqh8G8z5z5s+8h7'
        b'/Ie/+r/XtWO+rb9SpokJSv3PvTHLbr3XozykbP7z4syS5G0XYl773Xu/H/+fxO2c3x2piZ48KXnMm7kd15b2tB2dufG1I355a1Wqm//EuhExgYfbYg2xETXAV+RZxNa7'
        b'Xc5gDegYHkzwtaAHRCosH7MsjLUhoSNwMwVN/BwKmQKfi0tHW8MWrUVbM8PT5Kl84IwucVEdPIkOUiNUIdyFVZ5GtCU9FTMWKIcXBXEcj4lTH0gJ2+1Kh6/p4YkUeEWa'
        b'FR5CrPVoOxc4ISMXdsNXFT9DMxrELAP2JrhSVVRAUH3NY/cUgM3lsAAshWsGYFENBHbdEbsadS2McdzuKU1TbogD+928LJAYRjce9gR95dzjkpC7V4spJA1oN4VCwjpN'
        b'ociYblMobsKlWWwoYfq1QjaUlvm2jg3NntMzL58NLizoURXR4B1aCp+EaCk0REuhIVoKDdFSaIiWQkOklPs0REuhIbYUGmRLIUGi+ElwOVZs2MO7ZTDsH9g+yxwODe8s'
        b'NIdjxnbrzOGJU64x5vB0Jpl5e/Aug8lmemYOZpbLzGVI8abbRYySISTQWyEhYdY9ERv29GkpNIcDRrfrzGF5RDfnvikcP/HaqC9J2JB6zxa4uBqS7nFs7Xxu+4V0ijtn'
        b'dxZ2un/kF92UjDFyJVZ9W6J2VN1x92n3uukf3esf3R3b5x93CYcm9bpPauWTWvu2e3TGdvj1ukfiezsgjblnD3xGtU9rTTOK+sW+LdW9Ylnn7G7nrrnXxbH9XlKs0ErG'
        b'YDok7t8+wPjO50vA2PnccvO+x8XfD/VUrgYm2CRGAxQtSpzMRZMYfDWbKrmYEZ+MwKld0gKAkyW2xzmYWMEp+v6OmCi5DOP0rCrqDsEosN8mnPuTKJws5gALFM793y23'
        b'DFdPrVgUvircdvIiJpJC3VU8gQmFVyhtag4yFJbY/oPvx6JBPOU0wXVY7YRb8snyGyjMnqedEHse6GeT3GUHiIm+o3n8917ESH988/VF72fY7t2y9/1jHUtnuZ9tdXdv'
        b'cA9rjW+d3TLb/eC6h7PdZ7Uccj+67sx526kfZoyxrfhQfsvT1vYN25c8wK822Ueu2CBjqJWpBJ2Cx02SMggZqaDM1Mt4I0oss+mclVaebN/qK3VVRZVVWMUq0GmKNTpN'
        b'WZGm5keeUSmWBFiz+jQe5kViLG+eaJh+y8HZGNtYbRJo/Y54fBtnGYUtse2cdqeWuF7HgB/VFQUDPD0u5ek5NI5w6I9QusGSWxN4DOP8LLoiefEpuHSorvjf49JNj3Mp'
        b'dxiXCrJYRY0PW2x0XLgb8yE6DmDrzOdZMOoTC0pwh0eKto456TIazNDqLw0weqw+go3RYpYfo8zcuGVqdXHGd5K3Ppx561eLkm5j3szYW7HWevYFm5k7T+/wCPlgnaND'
        b'8Z0MLlixwDb0lELGodw3MROdocyXCl83mTaCYPMDX/wIXZbDvWGKVLS/0NK6QUwbG9BZGffxziXVG2RN98f0/keM+cQnlC3HmNhypiVbkuUcPKe2x94Qh3QldvOOpV7i'
        b'HM3CHHpLHN6p7hPH9NjGDGXDomdiw8mEDZ9IV70lE2b/LCZ8Gmse38D8j6x5T7EkKWDF5d1Ee6CcEEdwfunVShOU/ngaH1yaTPF16caJpWxkTjAHpIipwSEjcZ4d0M4Z'
        b'58ToF+N7u4s6ap9rJha6LsyfjPh48aae81hWvnR6jK1mS5L11Kr3591I+EzyVuloweZRf8j6s+RwqEKwWVEsbfSQv/W+KDbA3bD+wumDkW9knOTcVbzlG/xBJai67uwc'
        b'fgyzLVU5t45Lg8cyMuU5izmAl85gtbd11gPiwWHrSfxE5GhbRHZmFTyItmalwuM84DaLNxatg5uewSRnV6ZZXVmgrtIUqFWVmpqht5RZ803MupAHxG63vOSduafmd83v'
        b'8xpnFGKWbVndi6Xk9FPZXdl98knXmOvyhH6prDOhw86Y2u8mbY/asabf3eeO2M2QjlGBu3ertpNpK+11CzXyMJIQuw0xwvFIoQOiUo1KjcuvfhYzNVmVfIz67cDCBreA'
        b'92wLlawNzuzGRT4CMz+VEpbmsS5OmKk5BgE1U1sZhMUCytjcIcuUPNEQtsVhngULc9fyTIz9WOwgYy95nLFFwxibzzJ2lXcMUAvLMNHK6FUpESwPf5fCA8KUZQxm7Izg'
        b'VdFAu3pMAKMnc07py/1t747F0jXcJF3P246xnf/+6k88JsxvfJA2T3V373HZlmOt0s/dpYvey33v9js5KJf/yaoV4DeFKPbY5vETNq/vMFzZ3ISHQNgL2jE3JuUpv0qP'
        b'U/113ZmXxmzZ6x351Ru1r57ktt58Z1up7xbPA3YxB148tDmoZX2MHdjo4p3RLjYtQcHNBbCLrBSVo4YIK8CB+5m89GK6wgTPoK1oN/FzikAvmtyYeGgj1bDgRtSA6tJR'
        b'vRy/uzWbAYViIdrCgZuWwh3Upj3fFg+NRmSICEcHiPGHl8nAq2gXaqGlKhjUhhoz0+A6eBx3C9zEJKOzsTKbp1WsHmdJYmcx61mDw8t2icZidA25o4Nro2lwVeDB5bVb'
        b'3iRvVhgS+8Wuu+Oa4prjDdM/dnC57ebTUtxe2Ocma+IZGWNUv3dQJ9OaSZA3TdayYsekfi+/DjzoDsh7vRTG6Z+4eX7s6NOibk/tc1SQUNG+ktaStqVd47tzj03p9Y3v'
        b'c5zwlYjvbm9IweqBxNuQbTEKRWQU4qE3g5AvKKqqLC9+8iTD1lxEB6PSYvFNR0zCQ6vbSlKOx5d/4dFYjkdj0H2AL88KzHcLgsERm+ihwHzQPk1nG/4gMCdeVqCY//8C'
        b'9rgOG5R+7KCMK3gP7GTAvM89ldra1OnsoFw0zx9MxTDjwAql99bZq9nIMZnUF6pklVop/3qpCxt5JYQuHlXM81FmhMoy2UhPiZisR81UipS1B5aa7Exv5HsDAjVrc5Te'
        b'36dYsZHlMyi4Wn0zU+msXyxkIzPyrIh71uoxo5Sl90us2cgl3BAwE4CQZI1y2nUbho0UJU0GtXhObJ6idFYELmAjf2MzCazGJL25UKkbpfRnI2ut40ElHgBiX6XzyzXj'
        b'2cjADA+A1ZLVO5coJ4JyU+RzUXIwD2slW/OUo64rU9nID5Lpwplw2lplxrfBC9kVtug1U8E6nLJAr3R+QUfT1YRS17CpL89Qyn+dnMy+fNjDFrjj6fwfc5TyqROc2Mjt'
        b'5V6ACP8ML6X3JmUSG7k+bRzA4tuxOELp/JtiPRsZFpID2nF9flujTBvtOIONPJ+pAW8DMK86QVk838P0+leJxeB9HOmgUAq2jF7MRv4qyw3IMUlfKpTeBmU0G5k+14G4'
        b'x1X8YZwy433vYDZydMxz4AH+fsVH6frronA2sgBrsFhflTY4KJ1HO5pqtFQ9CuAZrWSfnXLanMRUoJ1k9U+OHos4UHrsza3N6Vloqu3mvRmjv1hSfX7djaJu1Tt2Nfz0'
        b'9jmFvfzGt8dfk14wJH6yo78vNT8oYdT8LX85+8P/xWz78sTz16xmtx7+5trkfVu1Gd8xycvT+kpbPr8W++n5yVOtPj0wqmQMOPqi3l14sWnlxHNX3v5y5xjftxo93/nu'
        b'85fO+Sdbi2fNSnz5RGq4Xci1jKPVv/n9Hruls+b1z9uX1aOVy4yGc7+ve/ubu/Z/9Hjn4h92rf7df5zmSGYF3udvbX3zI/8O3t+QzbXTn8hc7gZNP1pTtWfu7tePKI6E'
        b'jJ/962993EXHonxHL//CGB//QcHD+L//9XjVJ9YHPC6//O3/LYwfv/LKtX+4xp/MuV6R+b3X7Yzvv3Cr9Px3fdnWrzdJbC5WtzTlfP3KX8/kfBf3wZgjtV88LJj82oIc'
        b'n5e/XbZcti/76335XyxLv7X4N38L8bs98Y71vy82f/KnL6pd8y5s/OTvbk0nNwRciZNxqaFv3vREM5waxFJF6AqGU6PQqQfU/fQoarRJR9vQMXlICtqazgAhPMap1iDW'
        b'EwIdgqdRV5gf2okzCWUAr4pB9epYmfPPnE2eZsJxNk845o/FvONERG+hqmxZQUl5qZYI9JrhUXQGmmcy9FXwgcTNWNk83jD9ngBgpXhNr0Ngv1tgey4Gaz2OocQS5tLC'
        b'bbKhjglGVYt/k4a4PbQn9LoQt4VOp86cLpdu5y7PS5zekPhe6p/g6GTMaXFqymvJaZrfHtUrCex1DCTREqOuSYQDTmKjqskVZ+XZoqNrtOSNWU1WLVHtnNZx7Tmdozrm'
        b'9nrJu526C0+79XqO73UcP+Qtw7R+J2ejuiW3Pad1fq/r6E6nXtfQTlWvS0SvUwT7sLAlumlJu1PTol6nUTjGmRQdjAMOTsZpDatueZB5MqFd1zmtY1WfR0ST4GNzTJ9H'
        b'qFFwX4hrbcxtiWpR9TlK+x1dWz3ao9q8cX1x2PL2Fq6TORkbjm7R9TmOsgyTJnTDb0S3+fQ6jmbfHh42v7Giz9H/vmB48ZapoloKcaqRyrN8ewRKYjzJ7H8/zjIBblln'
        b'MYtB2hOuOwf1S1xaRe3+bba434zESUUsMT/tcw66YyvZnl2f3ZJww9aXhDPrM7dk3xkVashsCey19esXew2BFcIBXrVGpftxJPHIYK205GbdXCL5h/PvSTOkwDrrN/P5'
        b'WGe9B55RcaUo33Ie55m+vyKrS6z1REM2boB8DBlEQG1FHRI51JYiyifbNHhqziZg3oaRz6cxXIsYAY3hWcRY0Ri+RYxQw8N6BLeYoxZsEpohR77IAFYz+dazAYYbwgGr'
        b'BLVap9HriwQW5ArNsGMlMOvZ5n0XGAMRD3MOVU6o13mxkCIhTFC99SASsqJISGCBhKwsMI9grZUJCT0W+2T1ZLizAD+LruV5oT2l6JWVxNDoD/wnwEbWm85mSz9fvw2H'
        b'/nxf2/Zu1F7/vR0vdjSfTene7E8dhXUnNzdER1fqJDFVZ1znH4osjirKeSfnjXnv/+ptIyeXW3Qo6o3Km9GF465ujmp0mV05ZsuM/t9o/shf6T/B9bnLjkfT4u7sf39v'
        b'6Wt3p+45sVk1RnzDLmPv52My7pdWjDk+1ff2r7LspQ4d+8Rv/3HTlR0yrJtwwZzFfhcKrGTW1DvNH+sYr6bLQ+Ar6KSF3EdX4GE6L9ijF2CLhRuyP9pPvdf2L6aLPHBL'
        b'EjoVpkDn0AbqYsc62KVPou9mofppZMcC2gs7Utm80RUOrJfzWLVoI6ovwe++aB3OeuQc5ERaO1DVx3VBCKpfDhvhdrQ9PRxuh9utgI0rB9VVwfM0gQoet4aN2XgyQlvD'
        b'ZHr4KjzKAw4ibmUOPMr6+2wJQHUkxYu1aJscdvGAQMjxCEfN1L4A24RwE2yMwLqTIhVtyyarV6XoRXSIi9bHocuUevRabkIRNOJUCllaZjgDbFAjB13MRNt+sQ61bp2l'
        b'DmVVUFCmWVVQUONgGgEKUwSdv4iWTzSo1VbAy8dodUvs0S/x2p3VlNU+9oYk9JbYq7Wy38t3X1xrXPu8/Yu7nbtzz+RfmtUTOLXPK8E43Zw29kh8R/yBiTckkbfEfuZI'
        b'cnvbzbtlbntRr1t0d8wlqz63qUZevzTYyNtp1+/jj7+s+/1l+Mu+3y8If9n2u3kZbSzEns0At6hUrwsl9eAVaSurB4QV5fpKskgxINBX6jSaygHbqrJHZuEnmzxI2yjp'
        b'x8LssYRIxsfb5XuSfAK+/AfLxSorhpnKfAXI9RkkI5XCLwnk4LjNuKHKFmMe3950fNeCpWD4B8usYhmT1cUMCAtMTlUyZoCn15QWE8cQIGW7VjixVLW8UK2aXONoroM5'
        b'xo4xTQXrQOf0U5lHM2mr/ixKNmFKcOn8AtIBMkZXQdrnERW6FaQRhxFgj1N8ZSJAcsrzqOcvJkBUYO77pybCwYKI3FOLjy7++USUsERYFbBs99QkOFp0ROypiUcnDidh'
        b'0NSqBOz2E3bJAU9n/78sOHCztDNeRFz9KBxxra2+7d1Y6khJlhGYAQdqqKUrVMvX8nyXOsgYKhDlpeg1LA8jUYeFPERb4UEZx2IQEpEzaDrV6i3Wc2pczA03JJrKKGLM'
        b'JRi7RAjcvVum70trTetzC+5xDLaQFHzaHSMNf2qytdiJsYZ008ilOTOPrPhfq4TPBoYonzUJ/EGHjZyLJ23ywQJMiKWKarmmoGDAuqCA3SqKw7YFBSuqVKXsEyqGsGTT'
        b'lVdodJXVVNzptORCeFG3zEz1gB3Za6LCGEZTWlpQIOPhIcFGWG49ebQIOHVQzhEjdI0ZAX1Dns8itdwE7lmDqcx0pj967DdcBzvv+6OAm1+v3/g+13hDMhb+vd4xfeJY'
        b'w/RbOFY6oc9toiHllotPr++4Ppc4w4w7di4POFy7kK+4wN6VhmiH0P2GQWi9nT4jVZYWrhAA66UctBG+gOrQS6h1CPfZmL6/isU9vcvpEVpUMwQdzgXdXPzvgP8dTd92'
        b'5FvLKeaY7of8H+ccM8E7ijaDCNbEIM68SdARQzjeJtEgQuSRbcIESaoFx62OmRZgKOLkq4U4VmQRa0VjrXGsjUWskMba4lg7i1gRjbXHsQ4WsdY01hHHOlnE2tBYZxwr'
        b'toi1pbESHOtiEWuHa2ONxYLrJmG+/aPWUWPke9zNjIZpjW0xwna3wMIOND+PTUDjoPbEOZos8/mOQ9rY4biXuSz1aJwPcR3nqr0tWsyJ5uOD6fK1oMuZxvrhWKlFrHho'
        b'3vjfCv8Li0kM77i/mQZ1MAbYHNOGTtJP9gaHYpF6lEWpEpp/AM4/0CJ/l2ouFmchGNkX0TnyYbC1pTpvimV3YA95Qhb/tFgVGuCR8TfScMsqsrJgUrKCRUXkJnzZJRy6'
        b'OxvLahGW1lxMOjO4E5U0HTAIMMPZUxluNURnEIqGaAQ4LLSQ1lZrhSYZ/lispQz/+DvcCkMqRT6pZdpKrapUW0M2nJdopCpTE2gxQlKVFZEd64+/El+h0qmWS0lzxEuT'
        b'tPgtHX01dVpClrRcJ1VJo8MrqypKNTgT+qC4XLdcWl48LCPy0bDvh5CX5dJpqYkykkVIQmJidl5WbkFWXua0pFn4QUJWekFi9vQkmWLEbHJxMaWqykqc1Sptaam0UCMt'
        b'Ki9biWWjRk020hMyisp1WJZVlJeptWVLRsyF1kBVVVm+XFWpLVKVllYrpAllbLRWL6UruTg/XB/pStxmagxuhpNjah7CJ/GULhIyHwtgbl6sUKs1uie+bAJw7PumG9xG'
        b's7PDY6LGjpUmZMxMSZBGyx7LdcQ6sSVJQ8oryAkDqtIRGtBcKK6OqUQcGpnip8nHDLnYvMx3Pz8/Fj2xubHhn5HXkClkUIcfBDC2WVXEMKF1RIfJ0pZcgbYFwatoS/pc'
        b'ZEinu/394H4efHWSnlqLr6/eDrz5CgZEKrM2FM8EVcQmEg0bA1BjJjw+ExmIchmB6mfCK/AUMmTPZnPJS4EnUrIyM1MzGQAb0H4RuoCOwcs0y7NrrIDtvH8KgFRZ+mVq'
        b'JKjCqiuYH+tN/BXDyO76w2gzqs/ISTFpmFi9RDtksAvMTrBCuxPhSZqLYjXWiKd6Ccj6eVryWta2/ZexPCBcfVhAFiTfWh0FqiKJvEK7sQJtypxkjBXsNmTISENbMLUR'
        b's1JQQ4YAJKNDAnQaXUSvUY+STG2wfgUGRx6oHm3HVchBW7RBbWv5ehGeSa4e+fOaHZPKNkU6vmC18buoKV57UiSXYdqCP3HGv5UWO8faeOHe4Xpe5s7iTw9M4u2+/Yby'
        b'rH1g2ee//er77wVfzb69jhGEzHB44M5rWPbwtOO6Bxl/ei9A82po0LL/AzcOfFRw/tNjS05cfC66pOD5z747ursnO3XUJ/OUX34wY+zcG6LLtmH5YyaXvnXp/aOw++Pf'
        b'xe/derT6I9+3qu64bfv+/cN52R+Ofvi75+58svfz6lUf/fa7wvsDeVZHP78z5RtfRfIrU34fqi6svWET9PYFazd13vX/qCJax4//evN8n7Y0q+kX3CTT4Y5stf7t1Nbx'
        b'Oyfkxqln93hd/93fnm9oleyZVadLLOq+/fKH2duKtJ+Kd3wx4cy21LKDf5c5s44u28UhNrhxZZnwMjxVFR6KGiI4wAXW8YTwmC01GvDkpA8GXV2T883Orkb02gN/nACe'
        b'mwD3wq7EdEVapjwVbkXbSQdxgSc8xyuDB1AXu2bbMK8CNqKuMIvN1WGo6QFhaQyoG5LS0baUTLQNrkdX4TZzHi5oExddQt1Z1CCvjIdn6IYjdATuG+qWc2DFgwiS00X4'
        b'CmzHLINzCEP1kqRsU67bItJx5baxDrPJ8LQV3I5O5JuM+GOc0rPDydEQmJ30SmCTw8Epd8Ej1NaDDq+GHchgg4k3EcVHexj0ynx0kFbMxQ42EpNJA7oyD3MjF7UxcFtc'
        b'NFtpQ+TocC15kx2gfPQKh0kqoMXO5Ts/ssVQQ8xsuEnErQyUPBgNyP6Hg6iZGFu2yuipHGzL4mwSpuKMwuBZPnohfSm7cf1VJ0+aVSG8lMFgCvYx0AibqlmTzkl4Ohc/'
        b'VaAdtpmEvAsMHkMH4FlaObl9GKEuk/gbE29k+9Wobgk3Hl2CdWzbXMD98SJ+3Yx57RfCnYncGb5ZlH2WoKsYAeMM5LiBs8JTeMAeN0Yr7OROT4PrZA7/zYUNskNg0AZk'
        b'aQnCqogWI4SCAqylssJWYY6hetZshtWzFouAe0B7bJ9biJF3y83rtmdg++I+z9geSewtsStZ42jR7Zj8iWdgT9C0Ps/EHkniLbFnq759XFtt54rrfpG3yZMJfZ4TeyQT'
        b'+109jdxbYrImkNcZ255xQxx1x82rJaFp1e7nm56/4RbS7xd40y+y1y+yW9KtOu12KfDSisvBfX7TWnl3AkNaRS28lqJ+N6/dNU01zbVGXr+b90234F634E5eZ9ENt2ha'
        b'VHyf54QeyQRMW7+nzz5Zq6wtrCmx38Vjd0FTQXvuDZfQzqqbEcnXI5L7Pf32hbeGd/L6PMONiWYDlLcf/hKZ70zGqdGhRt4Nx4B+byl9aPqSBpKHt6TB/RKvWxK/dl6f'
        b'JIh8C/skMvIt6JMEfyXi+zuTZPdsgX+QkbfLzkJLdWK1VAO5EJexEVW9n7bxP97jpHeVFsYtC9v/PkCNEo91tx9RdIlH2w/rwDfPYUV3yjcAX4hLwZRntXIdEMSAszaT'
        b'f56Vawlr5eIXEAD6ZJuKiXyzTWXeI7NOS+6+/D35tIkfBuUOAlcCKTDIM2OKEJ1GpQ4vLyutlilwcVx1edEvIZdXUKgtempqFwyhdv6e+Sy1gYRajJF/lNifbaqijUrA'
        b'6lOTuRin0B0gzyl5YT+Odn85lcSqpyvD4aemUDWkIRftWcRSqrDE1T+X2MgfIXYpZ3ic2SLIwVJVxdpV6Dh+6sqoyRC0H6xM66KbPhHXfSIsGv/HgPv/oj7UzMrRnQMm'
        b'afTUVVkyvCox131Yb9uHEU+jN/wvqrPEojrLnqU6S4dXJ+q6TxRbnfCfVlz+O8OXEv7UNC8ng/c0MA/eyFyqsmMCLRdHpCZGlZbSg+qeSOj/S3t0iYzzcP8wBS+RKOd6'
        b'qfYxyajXaJbTo/QKNazOPuxFcryeyVAxW1u2BLdBUpWuXDpTVb1cU1aplybgOg/XJ0Nww+DmwS+uHKuIVkTKflzjHGmJNlfGsKeuXIaNeWEY4UlW8LDyxsCj6JC/9sGE'
        b'/Tw98S47bVVD7OnUli6O/XRltDqqqIGbd1bpokGSTNVCdG6Px+FRvvPHuHpt9IhbAA5d9nK0HtujkPEoygyZ6jkERIbI7AmElKMddN1xujCdKgfTwwmQH6oazEZGFmlv'
        b'dnIh58BhJbSzynwOXKGIekwvEHmkU02RsxjthyeYCLgZvv5EA74VsZ2T00EczNxoiqBgkiygkYXFEhvipD+paVKPOKQ/UHYzMLY3MLY79+L80/Ov8X4tfEP4dmVPYGxf'
        b'YK5x+s5MAvXWNK3pcQz8Wab9XwG6nDeUmgpLo/4im2f0cFjLjkIC1p7CQ5/4TDJ4pPwvPPSX4JFSN4wxZ2sqWVtfVWmldrmq0jRnV+lNpi16mmWlTlWmV1mcSllYPSwj'
        b'kkc8tZXGKzNxGpwV/lIt0eiUP2GAGb6CZHKoNtpss4/kxHGIYcU+UwqqyMaN2X7oxOOGlUGjio14JLNK0SjtjcUMTz+FdGL2ErJzoKO5K2dbfYc45VSxGmxUjL6wX7rP'
        b'6Y1s1fsrVcqQu4r1X64fVXF5dPsrWX9efSkjiLvEEywNtS1uWyrj0IGCTjihBqrOo0Nwc+ZQdf5qxAMZTuMNzzw3klqJlUo8LHawiiVsgId+ZBuWhUeZXlNZYO4jCsxq'
        b'PMyMOuzRkF0utWQA9YgDbnmNbq/s85Ibp99y82yJba5uj96x9rZvSI9sRp9vco97MlVaPnQMsNwTwA6d+ieMnydsBniXDKMnU1djHlBkY8AKPKDcf9HhHM+Ive2HEvPU'
        b'M+RmAh7JEWVkVr/pE3ndJ9JiRn/a0aPA0pAwh46cxTFkf8PgpLAUPHIl2g2oEzVZ3zA7Uv93dzeQpYAMZoSlgEG5UK7TLtGWqSpxbbTqJ0GWMs0q0+wXpYgaweD6ZCuz'
        b'mjXl0oYyb4vCBSmkszQrqrQ6UzuqcaioUqrWFGor9SNatolUwhToy5ebsbwWQxRVqb6cZsBmzXZFsUanf7Ldu6qIpShxWioGP9oVVSQ/jDxDCNCR6sxU4bJSK1UE+vy4'
        b'cBu+DUqYVUU0Z19iGkrPQltMR2FmheekKNIyUT3shFvkqD5iFjJk5KRwZ8lgV6p0caFOt1a7WASmLXFYjq5OqyI2OAU8PcnSaMu+Lw/NJW+TvRu78vBsv4tZgc4L545d'
        b'yx67diUd7UZnbXGfo050xQbAl2HLhCqy3Q92OqBGvX3VnBTicpSHDPI5yEBMkrArN0VOytiSmoEaGCxVD8pWwxcD0eFcDkC74EW/LNuZOGd6uic6Cy/hFJis0eiKmbKK'
        b'wVxnzg2fYwVmPi+AB8PhOe3iqDienpgzjlYfa3s3nsjl3gPNQRjcSFbsjkT9si3HPPyPj34r67B8TsaHxzoq3cTixOCe3PbW0nm5UQmfFr7unHXpVoaofW9G3tTzKWMj'
        b'xz0EX+tVf/3t3Tcl6arNn8n/PCN6F//WxFcVxYJX3DsFZdZnfjdvQmvvbcGD+RMnZLze7PH2H9fdD/WI62PKrKQNHj/IRNSY5w5fnIZnGWKtm4AbIpUPbMo4qC1l1APi'
        b'1YApz7IJXQGPo63sSb7mCcAPnuWhU3BjKutB9rqvK2uFLYGtpiOdtvjS/NFB4dh01iQJDztSq6StI9dlUTiFaSnZ1ayt2GJiWRvJEy4RUzNk2PQ1LAKj8Asjxt3kKN59'
        b'WvpuoA3nsaOipLA1i7dYl8raGV/Lm0VNmKz9EjbCzQw0YrjXTukSoTPwNDFishZMeA5twHlHw2M/tadt3WNT1SOxQY6ZGjIZDHlEp6q9pqlKaUucoKcQFFe7o/a2b2hP'
        b'2Jw+37k97nMHLXPGRLIHbnZ34EX5afkNryl0Aku8VtQrS+3zTetxT+sXu+IcvPz2jW8df9Mrotcropt3w2sMTZfV55vd4549JDNZZ8ANLwV9PPVaTO/gZGgy65GvXSJL'
        b'T1p2ShwU4k+eF6kj7ZCJ8fawiXFIW9QzFnt0sm0Zxps41Ho/qw/Ji4LR4LBN1C8yqPEKsGh+6rmxg2iPR4FZe4yi1odHwvzHFN1faACSUVKrnt6YdnAoqRNGFPWJeYmP'
        b'L6eOQLSMO8BbrtMUDwj02iVlGvWACE9SVTodVhSLeBak2prrU4Mvu0Tm5X86twsHvUsYgx09U4xjsC+2pTM9D8/0g4v8a/iiIfM4DvMt5nTeWr5ppn8s1lJR/rj1R2d6'
        b'9uB6FrrTSdNSd37y0j9pAnbKNL87uKv5yau4tMHYt+gruLFJnIrYGRTSRFUZUdFVpmeFS/HkP+KsTxwM8EQ8OztubGQUdS0gy/5qYmDB2vsTix/sp3jpjFLVEumqEo3J'
        b'cQFXmNT5UQpzpZ5UfFl55QjF6DS4ImX6eGnC4zqR0lSdn4ANg7tdB2GDdRadpFdnpBPQ4A3PP8INyGBaVspLwVGzTDCAiXaGzbAZnU1HZ9NAEDpoj/YsRE0UfOAp+jK6'
        b'lK4ID03DM5BlBoOAJCUtL4QePZqRlTkBnWQAOuRjiyHDHrSHXaIupucvpvCKlNYP4n1B1VgcuaAW7afKGbyCGoYpaOFpmbMttbPG2SJ0FZ10qiK6Pnwdnp+IGmkauqiY'
        b'SgBHGIEgjwAO2pYiT8tQpIaHLoAnBQA1ymxXJJdUkUNI4D70Mp6QLeEQqRApOQRtS/DIwMqXXBaexgc16IgIbgUrZVx62iw86knewwWjdWg/F/AmM/AYvIQ204P+YT2s'
        b'Q/vC8HyJ38/MhU3ES7yV8xzcCw/Rw+j1aDc3LC3T1JSoC51mgDiYi9rSRVrPmMl8PTGJuya/3fZuDEY3MY8jmxntS13lR11ONy457RTZKlJFY3izLNhryz740t85c94T'
        b'zX1vwyfWY9uXFm/6a6k+9vzxkD+fqdRV6TaXnireMPBbRqL64pMNXZ/e3XBUueGY46efvHv3rcrvlgpa7NuXviVffDs08vYHm+/6bs4a2273/aWvV+kOdv8Wo6LPPtny'
        b'l3Vd13w/oH6YEYXhnDduyFgTDlynWIOBSUY+PM4ATiEThTajdRT0zFxZbhM6FPBYwVODmGcrNFKAMaYWbpDAqybwNIicMDykACMI7oKX01MzQzFG9ZZxgBA2cuB6dIlP'
        b'lzlhKwe9Ygl9bFGTSa1Gh9we0CNU6tGJEJKxr8q0IXm6jD1lAh5CRkxd9twouoNMUMoZpZ3IZrttHlpPd5hls+fhyqXoVdxNEVy0a4oNXZ+Vod0riWksd8GjJdol3Hh4'
        b'FJ2X2f6i5VQi/oevpdqQ2d8kW2rElpDAFEmB0QBggVGhHTGCxe2Iu+05uid4Zp9nTo8kh5xYMXHHxPbpRzI6Mm4GjrseOI4+Tu/zzOiRZFistd62WGvFb7VOoIaA62I5'
        b'fZDc55nSI0khq6zF7UU3xKG3fEI7x/b5RBtnsHElN8QR/T4B+xa0LmhbZJzRL/ZgnWjbMq6LQ2gWU/s8E3okCWRl01va7xt401fR66vo843s9w+9b8WTOX8FeP5iuqpp'
        b'Ddy9d9c21fYMMTQ4sKjqT+TyZ3L5C/g5K5mPFrCHrmWa8BfZ/TliYx8xI6/vMfJKt2OYMLKeGfasyOtlgQKctBn/85CXCc4IzTQ9NaR5e6jt3p9MqnjKoVPs4JxsaayX'
        b'8YhvcRcnC5c3Q+aqe568u45c1gN2w4e6vKiggK796shRBXTBeYBbqC164qrzgJV5FYsYUakJaMBuiKWFol8L3PyAvmWurNP/ZpOm02ODz4IZNgPq08w2pgdhgGbiv7AJ'
        b'3Odx7By/FAJ7l9aYDn5HUVdgl77HL6bHM/ZyzDvcW54+XdzTiQ+4jP34OzHj+uMnf8ONtQv6CpALH0fe4+HQ/VIGSLxvOQb3SyY84HMkkwzT7wuA2OuW4+h+STyOEU80'
        b'JOIYU5oEkiaRoYnc/G45hvZLpuMotxmMIdmUKmJoKnfpLceYfkkSjnJPZgwpOMrV95ZjVL8kEUe5JjGGGY/ymkHySsF5fS0U2gV9KaFVa+e1hN2wG/01R2QXRjywg++R'
        b'0H0J8Am65RjZE53IZuWDs8pkW0PcEYBf+CfHxU5qegGH7svN1Uom1UplaL1MUTkkajaOYjMI6NB3xZ4W9owe/0buDbu0bzi+doEPAL6Q7NKZe+T+/mQz1eMI1ePrk1mn'
        b'cDJ5zEyBr+kzsli9mQHWNZzg59C21cgw7HcEAB1wxCfceahPuJqTz1Nz8/lakC9Q8/Kt8L9Qzc8XqQX51mor4k09F3TziZ+xyWecof7GjseFg57NERir2xgci7lqkYWP'
        b'MfG4tjP5d9sO+hjb01g7HGtvEetAYx1wrKNFLCnNXuNk2i5oRZ2BHQxOxUK10yNP7MHynEnqQWodjzsP+m8THYK871TMV4tHeFOMy5ZsenQvIT+DU8xRu2wS5rvgejHU'
        b'P9xV7bYJ5Lup3fHVnXh+53uY0nnip55qLxzjpfbGV2/iz53vYxDgN33xM18DwCE/HPJTS/ETKb33x/f+6lH4fpQpnwAcE6AOxDGBppggHBNkCo/G4dGmcDAOB5vCITgc'
        b'QnOU4ZCMhkJxKJSGwnAozCDCITkOyQ1CHArHoXB1JN2ISXaOKjaJ8hXVPKwRRQ0IEpZT1++jQ+A4kaDsA9b7m/3VLaxpkJ8QWaJTERWD1Q+Kqgddix9z4B3qS67DGSzX'
        b'VGqLpGSPhopdSSli1RwcQTQXnCdr5iytlpaXsbrISLqCjDMgKFipKq3SDIgKzFQMcJPyZmU9nFhSWVkRHxGxatUqhaaoUKGp0pVXqPBXhL5SVamPIPfFq7F+9igUrlZp'
        b'S6sVq5eXkrP/EjNmDnBT8mYMcFOnzxrgps2cP8BNnzV3gJuXPG9GF2eAzxYsNJc7xIQ96EkbyBATNp7rOHrbkec7dm2rdvD309TMsnFYAjvWcpZyh6c2s6revpJvjlNz'
        b'ajk1WE2y/EW2en4tY75fw6i5tcxKoAusZdQ8NZ+Wxyy1AsM+au4gFQIiZcx3NViQ1PDJuUYktzKct9qKDZMV7Ecl1YKCQXUf028Dhn3M9OOUg7uHq4WiYpno44KRVPLH'
        b'/fBNvPjIDf/xF56k6NLeYtVsFZsHjfkR6zfbrfHU0312dnhsdNQ4S1ZXY+08tZhovVJ9haZIW6zVqOUj6sbaSqJJY4xl9rinJZutKuywwsq6TltY9QTtOp48jleqNcUq'
        b'DCQGWV2J1XVtUQnJXcu2Ex4wpnLwIBhet88IRz100ZbRJf9HtQkO0gcPMIoBJvIzIoI/+wF/HnIVkZFZMqsBx8eLJcvVqtKKEtWA9RxSkySdrlw3wNdXlGordRzciwP8'
        b'qgo8lHVchhwPx+JZsotSR3YyPo5LCBtILSyD1M3Oge3nQS+7PxBQshOwTpUSPOX3+wXc9Ivt9Ys1phB0v7p5UnvCdXFQ57yb4ZN6wyfdCJ9C0fjES6t7B1G9u1dLUpu1'
        b'kd8vdm0JaprYL/Fomd2e0MXtTDqV3pV+idsnn3hpVq98al9IQm9gQq/PtF7JtKakOzhZXlOWMemWb1C7pq0MQ3ebfn/ZEd8O3z7/KCNvl/0v3QlJ2+xJGNfcEmaI+/UQ'
        b'z60FexZYLL1ZMjZlr+oKjVSJ2aYIY89SxXT2W6lU6A79Eoq7GLZnn5Lib4dQvHgPu3P0oRd1MRx5YA0hjWMmLetHSPsxWbmUN/yZzaBfE5ey5oBQpS+gu3MGhJrVFeVl'
        b'mrInbkx9vIL/IszpyVZQvW9p69KbvlG9vlF9vjE3fSf24j8fdqfqwyLqCFi1vFCjI91j6hdpRamqiDgRqSqlpRqVvlIaLVNI8/QaKh4Kq7SlleHaMtyPOlyqGutyeHSr'
        b'1EurcEKSYGguQ5tucBqiJ8UJB3/2Dwz+7J+16SgGZsha6n/BFenjf4wkzvMqiIrDinLN6qISVdkSjVRHowpVZKm4nPU4wqlU0gpd+Uot8SYqrCaRwzIj/kgVGowcEnFn'
        b'6XATTFOVLaPLn/rKcqyAUcFb9lRC1iRgzSQVUJKUpBeqqFBlRTiR9YPLnrgXyFaoEbw/yA+ZaipLyh+hGLlUr8WzlSkb8hpxIbPcUPWkOpoyiic/hRqvNAGsEdxIftTw'
        b'WlheTn5XTVpsaeGtol2hfqwbRpx+Vml0WLisxOhIVUh84Z5g6/0Jzy77LLpU6wI3ou6w8JRUOTGfpc9NmQQb4Qliz8R32XkhafLUcAFY7ixEV5EBvUx/UbN4eQ5sRN3o'
        b'fE5IWjj5Hb3thQvDsuB5tH9WODrMAbHJ/CUJ8AK1QqJjxXCvXpGZhnatEjgDB2REp+FuriIC1lcpyPNt6DI8Ra2jYviiyUAakhUemh4+y5x7Oh/rI0J4JcqfKltocy48'
        b'oqdnn2fOQxf5gA+3M6jbfg4tMHg1ZzbcinbOTMxDW9GuvEwGCLMZdA7uSp5RRf3EroTBVkIRH55bAriwhYHr7GED/QVUdDmfmHjhRX0KazdNhyd5wAkTDI8nwzbqCLdc'
        b'ytWTZsmbgUteQ34GsAttydWWh77H01vhUTbe+ddrZr6Xxoty/PwDdXRz6xqpDRxlvfYFNxeH/6xfcit96mevXb7bpb/v2nLsW6d/NR++menoPG534KK8RYv+/eHziS3i'
        b'aSu8/7E9b1N3+2H1pvWV8zND/xraf/+fd7VhLzeoTu04tkE5/puvrk0tSupTC6L/8dY31TOklyqnTY7ack5+fsvJRTZ9gXPjJ0Sdt07P//f2OlXM1LV91e882Pq3V9cy'
        b'/xd9/ZUdh7LFU+BX/y4fteSFTzNvz/B7fuP3urvbvF7p/CS6/o3f/1NwJ/Ny77JtpWMvzlr+2Zc7rVU1PddCD18Kra7bNqcn8w9dD7aLP7g78eahUcs/zX6lVV2I/m71'
        b'j4q/as5cSdytddr7tbj/pl/85cnCvb+TOVGvvMXkh8HIYfao0WqmE+CFM/BEOnyJPajxGDqA6sLCUQOqj0hBW7nA1hu1zuAK4tBL1CYbC+voQSI4BeODTgJeBAPPwp34'
        b'KemIVXA9OhGWlpnBxEkAz5+Be+HuKGqK9fNBbcSUmzmZawUEPI6wGLE24Ep4FG5Kp/Qw8AjcAHhuDNwPT8I9dB+TcI4fsSQHodMjrZ5XoGZ2O9DF6XZhCtka2B4aYvqR'
        b'XQd0hlu9EJ2h9l6XXHSAGmphQ5TpB3ZfhRdoazyXFczmzIfHuYCXxcBuXJ2r7NH+zStGEUNv6mg/uQLWR5AxmcoHUikPXUCvo1eorXupNzSkPxqfcGsEHaA+ViAUvcpH'
        b'GyQu7C+0nVGXstUkixX15AyWy2iDmoPaHGc8IOeDhT4PG9Kzw9f4MoCzkklA2+dQ0tdUwYvp8pBJthZH2rgL6e+2wRfhLrg+PTM9PVOB6uXpcGs2oQ9tcgWhcBsfj+HO'
        b'QJrH5Ey0DzVmwRNywXgvwJvOwNc48LLM8b9uQiMXs7AbasN2YaVpwdAJpMbbhBRGfErN2insRqF7uY7AyW23TZNNj/eYG45j+119dpc3lbcXHSnpKOlzjbjpGtvrGtvn'
        b'OtbI7Xd03W3bZNvjE92deMMx7parR0tAcwmOd/PcvbppdbtNn5vctNlodE/wlD7PqT2Sqf3egTe9w3u9wzvV3eO6ll/K7/NOuemd2eud2eedbRT1BwQfGd8x/sAEI/eG'
        b'o7Tf3eume2iveyiGyh6+RkG/p7fRqt9bui+jNaPT9SPvSON0DL/b03v9IjH69hrVHttp1TGpzysKx7t5765uqm5373ML7VRfd4vu9w9qERB3uqSWkKZs83k2cR9K5Pfs'
        b'gE/UPXsg8Wnn3pRG90qjr4uj+2XRxsQbktFkD9GMW9LA9rwj+R35BxZ+JI02pvS7+bWvuu6m6Pf2bw9pycZZtwruWQH/mHtC4O5rtNwdZKMrAT/Has6ebfP4zp+JuJN+'
        b'vC9/MFvNyQFgzzkwjBM55+ZZDvvXkd/IxIiTqEhD3GMH1z+pNxx/8OdI+fSkXzB41i8xIwj+ay6yBMF9NBKCS2QhiGlXPKtwEECKEQFBFYM43gTkCKrTm1Td4YDBtLD8'
        b'GBJ8DPeNjPOGw4/c4ZhSRXDLEJhlRj3lBI6RVfVqAhiHU6YqKmFd25ZrlpfrqqkTQHGVjkVOevqT9T8NwR63JAzVeCw2cVSqdEuw2m5O+aPL6GWD6+gsQ5qX0c1QlwBU'
        b'jd7SLvcz/PLYU0L55DTTTg/rmcqMo1Gm40gZHTnctSJSOFNZm5LHYSM7ii+A1Ux/gA2YuqK/yHkehS1hqNNLb2fHgdvgBcCgbQCd8JRWkR9gLkCb0NX0x0CfecXejIJy'
        b'Z5bAU3PD58zFgIwswj9yu8NzVI2vY7wmSqsOvc/R/xHnWLHnN1VNV61hpONbEdq+OY1J/DenRNz59HBbY7bS79ohaeACx7odirK/KCZPX6EtuL6shJ+6I8j4xTdrVl1+'
        b'Lthvqr9H3JG/f7F76vquTxQdK8GeonzOZ6ePjVtXn4HesYtpP/XJbxa+Fdlat7fhlV63wtGqw4UvxjvlXcp988PWG5OKda4ftP/hzyfzt7/jN/+HnYak/t++sunQsXG3'
        b'p/SGzrFKm/Qwj+tweO43X2+3//xQVufGtQeyiy8xU27yP7z89xkPdo0LKd1191TDvUDrv7nu/V3F5aq+f0/59aU/Ids4pbrzn/dmwU//yV/2t/iJiTdk9qwn3Tl71Gba'
        b'0JxURD3pYHcc+/ul+8WF6RYoEtbDBoc53FK0PZlO5bIV8AUJGGEyN03lZTKKclzCldTvwWoh3MIegR0Mu+j+YIw792D0fg6eHTYrm6ZkeBh1s3sj2uAl1LESrWMXkFlQ'
        b'snMO3VKNNqxBG8LMB5y6o108YAPPcNAx1IY66dthYehI+Sj2xGzzadmH0H52c3ETPA3PoH3JJlzDgpos2E0xTYAPOkwxjdwR7Xoc1KTBsw/CSBbH56MdVAVJxeST9jij'
        b'etQkHHQGNjAFEUJ4sFJK2xztQIfnhtG1eD4IcBMs5fiiXcvYzexb0FYnukwPL8Y/5v1+aBFb3c228FyYPBMrHKafnkVG2O0Am7m6ZEeZ6NkgiAhYnEtn2jxi0gpr7E0z'
        b'lOme4otQE75QOwHvwH2TWyf3eYWR4/K9Wir3rWldc10s7/fyM6b3u3vfdA/rdQ/DU76r7+7SptLmMiP3lpv34IPOolMlXSXHll53j+v39tuX3preltmZcN07vDvgYsjp'
        b'kEuzzoQTiJDamtqW3hl4M3RCL/7znnCp6Lp3Qr/E/aZE0StR3JBE4gz3WbdSK5wb2cvSnnRdLDNtVulM6nWLov6H83oWFNxcUNKL/2Qlfb7aHnctmfWTOgNPhXeF9wbG'
        b'9XrHGZNINaquk59+8muv6nWTm18t6pUV9fmqe9zV7EshHdm93jE4vbvPPvtW+/bKIzUdNd2T+twTjPxbbj4tmvZ5fW6KHkeF5enjrNmSWiyf4qhQ9uTxIWeFZhHU8Fif'
        b'hHBMOIE4/Gc6MYz3/Wf0a9T9HjzpzLOd4Mn2sdoR9/atBDp3NfNoJQGnEgxPNbgKICAmQDXn2dKLNsm4WQ85QdqHvCBFdLGMR9t0wLagrLzAZLvSD3BVhXpqhxtucxtw'
        b'LBj0ZmMXe2rczNbhxx6kkdaNB8QQd8fEXdNvBo7pxX/iMZjPDwa0q48s7Vh6IKLXK6pHEnXHy/9gYifvlHWX9YHsXq+YHgm703LIUs7gjxwIyVIOZzdgl0/quebVSt3K'
        b'WuYJTT5CLFnc0eWM3B06b5wTf3j8yDk9Wt4pk1UOLuaomVpOG6PmjPxOG10KesIT3l6rR0tIOJVweKo1OJ5agflZNa6DWG+5Vo+7oaiEoqQabrw0uMYqmBriggeYYBmf'
        b'7XGxdnlFqbZIW1nADga9tryMDpIBUW51BbuKwPIAu01tgE8h5YCQXSfED4f6WUsHd6sN2BdU6DQYbWkK6Cs1LmYGGRKdQ9iD1B0LROLOo2mfcwPLP6yyrG1a2yk55dPl'
        b'c91tLOaTm14x171i+gNlRzI7MrsDL4afDu8LnNqa9KdRYQMR4y5Jrvpc8Xmb/1v79+zvcZnweeRMy4D5zD3A+Mxn7nj7E+GIhY2bt9F2+NLAoF0sA192YSivJqZX5se7'
        b'2NShI7AM6dC9fHrIJS+rRsjWOyS4hhcsx73ACZbpyP4GGYeVZoMbD6WPzrHALaSjR5qaV1zYiIUck1H72/XgVkR0d+zF+NPxJ56/xvu1HbLrccvqccwaXrnB/WtkEJKq'
        b'PYswKuaYBAb5vbGHVkRYSIP0LP3DpYJVATltEBNuP0g4vS/gDBrjya++TD+S1pHWzbtod9quJ2Byr9vkHsfJLN0jbkGcAUwilBlGHqhl1Ix5zK9hRq5DLbOMY1on4WQN'
        b'MBO7ODpyZgHL1qZOmM+YO8FUFUFBQSk5SsRusCbkthAn+SqArcjgJJzUHdPnPg5PnuxBHu14wpT1OMr+tzXyNIlx3CuciZN0RT9VF83QuuDb4pHrEtvnHveoLnns8e4/'
        b'UpeXwaAExlKsnjMogWOfwGcjSrplIQArKzoP5gl8iN8aIZa8NftJkyvDPmUPYqAMy3vUPo9tZHwktXBbaVYMaStySwrXEy1pqJTy8d+X35rfOebUhK4JvT5jv8TCZhrT'
        b'7x90xKfDpzvoouK0otd/KhZHLonMnZ9q0MEVNUIUYQ62ArbmNTEWAf1IF5cN7WJyW8ExuRviLvbyax/TOqnHLaTHMeR/y5rTBwXGADP5JzlzydBRRm5JEp2GMXkM/s/o'
        b'XGjaUUKG0OSfHkJLhrYvuV1FCNUOEjqi1CXOiGRK+ekJZXB7yxDJNNL0QNaOhkwPbMRzHNPvPhAudfMadpTsyC1ZZiLwl7Ql2TpCjV3cWjInjrC2a85jkDPCuriPxDAF'
        b'I0PGpx0zdHyaa4+nGJVaPWSKofdriTSLZes+gmhmFRw8+ogBlVUvco8s6ljU5xbT4xgzvHX+P+a+AyCKLFu7qhOxAcmZJglNaEDAgKKC5NAgwayAdIMoAnYQMcyoYwAx'
        b'oOgIoiMYwYg5juHe3UlvdrcRZ0Fm9o2+t7uzbyPj6Mys+3b2v/dWdYLGUZz9/99QXXXr1q1T56Zz7v3OObrqwyr2yLwxqDrGobVi9ctaEZ7ZGeoNZnaS8A4mn6BBKWJe'
        b'tntte3Lvjw29P0nNWb52zYUr6l6jtpTqxcYCAb7egjvOGpM9XMf5YJbzVj/OezI+rvsxzjOUGHCeJOBo2iTmLOK8m1cLHzvualf3uoRr7MJfwnu8lG1S8RCodJnzR5zM'
        b'MG7rNbiOEREDNtJqVTqS1uXY1YdcZtBv+KZqwqRMjupjubrSqD7I9U7MBGymYjS/feEh1jiK/y/0HQZbrtj6YzXI0G5QgyRhL25Mb798ujCQUoyry/eNOo/VSyvZ6rW7'
        b'VgTTtV69Qq2KilQKtVxWsRIxxl7HGF3afjyuZFNDBRdPUZ9nRI9nRDe/W9nrORkpRh4+h+Na4zr5PR7hGsfwx54iPHd0OvV4SpqSH3n4tgcyulivxwSN44T/+4zmvJTR'
        b'nNdg9BIy30e8NqetkcRcWV2tYFjtoGO1PvEw7kQv5bWq13OKntdOPR4SjaNEy+tAlOf/C14LXsprwWs36sDXZbUZ8SRvPErh65O4o+8w2dF1Gvzv9TzhI57wdDwJfhWe'
        b'qHSLTKa/bS2t/7pXz7uAtE/iGoNHuGZqfY7NS/JwX56njKNVZgWo4SHWoLmYiFL7jOUpgZ7jA/zaJdWVcmwDvLykokomN1y4YdGeOv5bFhUx5aIqGKOrAm3SedzMsU3N'
        b'iM18Va/n9KbkL1BLDjgZ0hHSKe/1wN41fxsU3ik7v7Rr6fXA3qDpOGxUcsukR55+7bHMCnKv50R8NQllWt61HHUVpDl5Th2kaKepLwkqkUj9mHxtNUJjNmio5TodcSSp'
        b'm4SZKTdqk+T6Oh5g3VluoLlRdXh16+qWZZ0x5+O74ntdJmnsJr0R8Wf5P0p82asQX1OtNCKeXN/CHarNpP6i61B5BiSqdDlGIEoHOf/RQZiAPPON2+tLyC9ZbEw+ub6D'
        b'W6KnjvcHS5n21lbdqTq/rmtdr0u8xi7+p1TNFOofIbOiSmVEJrm+z2EtvQiZ7i0xePRvfltjN/anom3Tj9JmQSaqEsY5rsHUhVN+ZqQ2emKXo63zekdYKNC1i3aKNaJA'
        b'AyheX1NY6VuHjKNfs8YDsYwr4zFC72oDwteNsHxqcrWd0yDQDdPcVxkkCVv40v/B5y/8CEy3oqpcVFNdywB9oyIZMwF1TU019rz/ghMpGaCj0FDqrm2VA+Yr1CVVqorV'
        b'cqZ9Mu6mBsxQSeUVKuUAV76qZshUpnc5xQyoevYTCozYz6Z8iNmfy7C/38G9ZeaeyQQmn97rnqFxzHjkjL0Ll3amdizv8Y7pdY5t4rISOavjzuj26nWdNpJk3kUkaydM'
        b'fsQQS0rFC5Y0ZWW1CsdYccXfbGMMokHXZWXyUlXFSiZQL5KDKkuUqiIGszHAK1IrKhV5mAez8UFvk6nr1gPmuh0lKwKSYOCzBMBDthoUBfhAJrCF+FCMD9h/qGIJPizD'
        b'B+IAEru6U+D1ZsVKfMCqtuItfNiID5vwAasQCuyoRLEdH5rwAdtNKlrw4QA+HCJ04kMHPhzFhzOYP//uaJzDDD3ZPUmM81/NWnp9itWeapox9BTwhHaDlpRbZH36Y58A'
        b'jbVnv5dPvbTfyxcdPHzqs/odZtYn9XskozO/II21z38JHVuTO/w7yjUekhsOD4Xx33IchOOw8eLUQXz2dQjl5PXILpixnHRKpuuTWVPN0H7HKGyqGU0sNXHKlEEO7ZxL'
        b'P+NzXfOw/aYlZePSL3T9jhMo9H5KoQMu1g0fXAZ56PJrVJM2LgOIgtKHQj9sOhmBb/qzOdDl4HSUw/lrDk8YQyLqDOKz59YWQq9nzrQwh34qoIXTngo4wpCn5hxh6HNz'
        b'njD0qTUtFOvTnpnTwuBnAq4w5qkljS61Z5LniFUxOHPoc4FAOPG5nf5gJpz6zJ4Wxj0TsIep+BCED+LvBHxhzCCFDowRJ/ZetNobNCsxgoAx4jR35cQvVCvgTdNxIPEi'
        b'+j6+sQ0n8YfGreeV4diP5mwUHu4mSsY7wx8ShUeAUs0MUs0MYvPoU80NYvPoUy0MYvPoUy0NYvPoU60MYvPoU60NYvPoU4UGsXn0qTYk1RmluhikMnF3XFGqm0GqHUl1'
        b'R6keBqlMbB1PlOplkMrE1vFGqT4GqQ4kVYRSfQ1SmTg5fijV3yDViaQGoNRAg1RnkjoWpQYZpLqQ1GCUKjZIdSWpISg11CDVjaSGodRwg1R3kipBqREGqR4kNRKlRhmk'
        b'epLUcSg12iDVi6TGoNRYg1TGKnU8sUqdgK1SZRPR0Vc2CVuk1sUhIW/ygC12gVOgd9f3pJseAgbU+qozyMQGCBqSDVs8EPOL0pIqPA0ulrPme6oKAsXTGkmQmDJawz5s'
        b'J8Fg3uTG6DwWE2hsF4HXNQ18CxbjSbeE8eIjqy5V41UsXclGpVUrtAVWqJhNZuZRLcRuRkJ2QRJbQvEIVodGF+llrJFHiWgx2RJHxTHISEPfh2HMK7Xfylq/qhRyzBCj'
        b'8kqUxNgWE0dML1aikkoqK0VqrFdV1mExw8ipotHDRuIell+wxcE305Hgt4+HpSmFGZaoMKiqwVxNjyRVqXRyk2lsgk7G4sqotdwinapKrnhGV3yjK4HRlZnRlbnRlYXR'
        b'ldaqnTJEvKJ0K6Nc1kZXQqMrG90VF13ZGt2zM7oaY3Rlb3TlYHTlaHTlZHTlbHTlYnTlanTlZnTlbnTlYXTlaXTlZXTlbXTlo7tCkmyRSHdFoytfo5x+2qu1nKWp1LA/'
        b'Wl4nUQvl7FIDbx1/LW9p+vC8Mr62XSgFMpSHbNvwqvxGyC3Q5laMkWE1NGN4njZ6La+NPsRdx1Nl6+jkrtUtuyhtVDm68szQG41MolUzDZ9Zy9fGTKOp7eU83JIs1nKX'
        b'6niq/9Ogi5Km5GRgXAyXiYIsVRxHZb+IZYa2YQPhy4c6ssGaMkAXDXCKil4EDn16SQm2NdObqxH7XLF4wDoPiW0Vy1mDWwGD+2VCHnKLKmQD/CK1XKXAbvQZVx4DtkyY'
        b'ap0XMsURzOEufMAhqxXV+EDcuv+CIjAaIyd8SMtkAN6oxBq1AqnxcvQKIoubEcCVqmRAULRcWU5evQz7f+MXyZkf4g1OqH2siISZNSsqXYLBySTyZ4lKrUQKgUKOkUAl'
        b'lThuRVVZNaKYMLSirKKUuAZAOgAzDehulyxX6T9owLGosrq0pNLYky0O9boEQ6qViD4yDKNiyC8TAnbAs2gIy5H6jIZYNi8fnS9XDlgiIhUqJXZ4QLSZATNUL7hOBmwS'
        b'tDXD1ISZUq7CN8SWjNkB7vwDgmW1iASlgdtgE+obI7HjAY0ZsfWSOomn6zKETG1c3S+xHvcerdt9VbUntNZqJFN7fKYSq49Fve5FGseiL1y8MLSpvbTXJaSJh4GevL3m'
        b'uvAsJAJLf1AoDs8SoAvhIjIK4aKN0nLUwiiWi/bXx5+EGhb5GYYhZhO9/YilNJto/BMoxs/7abOyPzjGy14bbR4tYQHB+NdXdx0WiX/FLG2Pvf3JawICmVza3P7ik1M6'
        b'ppyYujuzKaklEC+DT2ud1hn90COi38evvaB1dSuv383rsE+rT6fjZ26S/pDw82Gnwm7wND7xLbwviE2LI3GGGaYJL9DMnt8TPr/Xe4HGdcEXjh4tSe0BnfzPHCWDtlTA'
        b'uK/tKFe/9oCTYR1h3YKHLhM0dhM0LhP04ZdH7XsS6dKAHtnM2nVo29CaI9tzjdwz6wMuTCkgBhlVy/RuCcMYB82qatbrIzZ1lSFZp6KsDkkwBpLFG5qMKzqoUXyJE5cy'
        b'jKMy1jgoDTZ1WF6t0vulJMES3yBShKJzNES6YiL1bjSNY9EMpxGHcnyDKC9nR0Oihwk+GsajGUIjG4Rx9Hx8WSiaEYn0xkTqfXeJTYSi+QnpJAvZt0ZDp68xnZ8niJig'
        b'nkr1YtZDDvHJgYljjaTYUCEv/QiiTjEFESgz1n5q0GNYcyExCUwEH5GI8vVpZRVy/EJWlUClowx6EyqdKKEUhbBMDQlDpxUq8qsNKhNCQLshTFCWkNFxlixefzoazgZj'
        b'zv5Sx9mY4d7kR+hTCYmzEyLQIfkNOj+iFo5mtA01JnqKkcNf7K9dvtjY9e9Q4mfkJSdFJCUnFoyS+DKG+J+NhngJ19A1x4IDC5iPyCON0UAgZe38tC5FhhigSURJxBs9'
        b'Y25XWVtSp2Td2oqq5OUleD33TdwaK34+mk8bZ9xNQ7TdVGtxZ/B1rJAqCs6fNXvemzWhD0ZDaqzx8BxEpunq6mVYuWfc/iKdv6amGrvcQjqEmnEU/EZ0fjgaOidiOr/W'
        b'buG9sC3QuTIaPT1s6/1oNPRMxvR400YzxnI07JWUyw36W82SOiU2/hTlJqRL0TBZ+QaNsYtWfDwaSqeaqGE9hZXV5cYEioIz85JT3sgXuOKT0dCZYEwnY1JbJQtXVYej'
        b'H73YKApOfjMCESP/YzQEJhkT6GXS17YoOHv01LGS96ejoS7VWPLWB6HzZWyTkYpZhT31sOMN42E9tzAv982G/l+MhtYM485sT+Ytop6zHoreqHI1oyEp27hyQ4bOQngF'
        b'ANt74fPgxJyczHRpakHynDecOHtGQ2ouJvWxjnt/G0qq8SKGRJSChvBUOSK+iihgSt0isamA8Ggimp2eUoDDuoeJUmfNCBPl5qVnJ0hzChLCRPiDM5PnisOIsVUKbvBL'
        b'2DJHKi0pJxuNLExxKQnZ6VlzmfP8wkTDy4K8BGl+woyC9BySF72BLFzXViixpXxNZQkOKsN4k3+TgenBaPg9y7hnSR54MbaaL/wM5nVmoYjpViVkuCpRojLeZJ785WiI'
        b'nWvctcYPbRzM4pdElKD31JYuTclB1ZwkTcWTPW7bb0T2r0ZD9gJMtp+ObJcCIqwyy3OoTclwY65+A3ULDQu/Hg1dRUOmeTZOAXF8yFAl12+3GC5ZvMmo0DsaShcbjwpe'
        b'DAe1sxL2kiHCG0omhBAd1GUtrcPZm6BPedQ0jGUVjQEVI2ADRzC2W0UrrUd6hriD46ylTcNeUKoJ01Dtgvpaqsgwp+XwnAoP0+mmv7mI//L7S4XD01BOm+Gp2s0A+qX9'
        b'58XkPMbXBt5402k6jLam3wI0rc1JxOaK+7j+/4E/c0hsarLOjr2BK/6JDmKuQQBrsgqM+aezZrAql6u0y/irPYY2OIObcvSYEi9Pf7+ewoZf6/asw6udE1snPvCI73Q8'
        b'79bl1p10Le1CmiY4/oFHxj3HD93uuzUlPQoI7UzqDrgmviC+XnB3wY0FvQEZurCRqIio2GteF7xaeIeFrcKHrpJ+R9f92buz+xyjexyju5P6YlJ6YlIeOqYOiTJp1Kbx'
        b'H9KmcRPaT9XRBKNbwBiXDe9aGGczvGtp7Y2q8QRAoitho5WXgNnyqJG7t8LONDBXu69lCLQtp4YY3Ig5in6UMsDDOwUmDFLN2T2EIlMfwdxR4LpizSAdXPocArDvAmxu'
        b'HNbjEdZLENpfuHi0JDavarJ9ydpxxss+0fl1IvuydUK2srTfxyfNyrTFbaW8Cn2fiV0JcqMWf55ohM/r8xjX4zFO4ziu38WVfJtU7G8KJEY2Pgisa8BmyOYV6SqkZ+k7'
        b'1f9SbH8aEBrvXQnYrSszVtpWJONMAnbbis/sWvHIphUP71mRgAsD1kYbVgJ2v4pH9p5shuxMWRluTAnYHS1z/YYWs5lkY7xhpfDgsG1dIcJn/hwCVx8RzGUcUExxFXeS'
        b'odiMHrwbhP3CEiCXhdDuO2eJ0PNrGU15jyV+8POe8TneBXS9VO9mfwp2oD/15a74DfKwfuinYT/0CYwnfpI0yOE5RTzjC1wiUZoN4y+/3zEDO8vPouuzUTY2CZPgVcAk'
        b'Ye/84kEO7TTpGZ/rHFef8rW59gXT8QsS9a7+ERXxmIpphAryYL9jIHbrH0S8+rMYM0yXUwKDMRv+GJsyHqdMNEyJximxJMUzgMQVwI72PSfVZ+lfFoxfFkJexj6FaXRM'
        b'ZGIPEAYPcrhOM+lnfL53HuaxNeXh/8gODZkTUUaPuPpMfWFZuDApE5CAxcKFYyxcBMHCmfgYtgIxod6x9dJnTNACWuj5VMAVir6x5ArdGDgZdpgXNhsctVoJzq4T1liL'
        b'M+D2UGmWBPvIgbu4VMgSPuieCtqGhZvFf77BoXkxwFYPLdtEzeNyKDmGlekGwnl8ksI1SBGQFJ5BipmMj541r+eU0TLBJvN5FjIzdG2JXc6XcWTmKMWK3LNAZ9YYaDZP'
        b'WGeFtG7rAYchzTqrQmkcPYyjHQCnMgMgbSRqcNCVbrjEiN0i3ZBXjoUS3chex6oiPLKWM2BRJFOzeFMLbPtRUlmhqhvwG7pDjKkpMgQZKbVWiSEcAjzVFmKuLUNrnygy'
        b'8GvtaaJUnZPr9Xj89GHGT3YT1FdMtkTZn7HB+qi0o1+b/9+XiLYm6dPFfcXiLTY5HD0BrA44kTNKErZiEmrfiAR2gWfSaEmoH5kEnRAiISS8qgmDli8chQ+eEuJMU4an'
        b'ixHbDxEvtnF15qVYjEhijGR6XSI1dpE/FfyfVTAJjSMYAJA5bZjMylJKBIUdmFCMl9JaKfR5SHo8JL0uERq7iFcRJDf9qCA5AqMYYbIJV6EXR1uFht5+dOYyP1CmDd6U'
        b'hig5Wo8vMu01wnTFkwAPwegJ0+qaCZWLPGFLDLpMqF7Ep5CVSo9/M0DvoSeshz+x1HZ4mt5MlsZjZBl22xRuuG6xHLscX6z3LB80hMdBxtll1XLGZTbjG4gEDtF6fCSy'
        b'EVKW5tDsAErEM8VkfDYFH4hhBG5lSJCrqZFXybROgawMXsFkHdG2j1sikw0TVklDQDeacRvEgZtIG/RtD+18+6HLtC/c/TUB+b3uBRrHgn4H7z4H/x4H/3bVybqOugcO'
        b'kf0eY/s8Qns8QhmjnwceU/o98N11Heg8hlhSFPS6F2ocC/vtHPvs/Hvs/PvsQnrsQjonf2Y34SVdEOMD9V1wqCWQoTeOYZ3ND3c2N1MfSeT4g/gzhZS+qzXXaexEw0nR'
        b'eRnFACbjoSuJ2kWXcsqpUs5CV8YDlElLGhNteTdnuzsPPbfOwAC7lEOTlFqdsTlXqV6uGItr0sAXxQCtMjLJ5quqVSWVpj+U3DqMPxT7CseDn/uFpF6PSReSOle0JBxO'
        b'a007LG2Tdif1eEzqdYnT2MX9/YHHJDI7b/OSmEvFNkP1EL1lCWma+lapE9kZCT6Nw1aAIptDNPohwjuuX53oPh5XlCkZZx2mHGMikfj+VMATipEE6ejZ4xnd6xBTn/TI'
        b'xadHNLnXZUp9msHpUx4tjMJ2BZHYlMHzucBMOBGbHvh+gy4nMyIhji8WUR5qtXKYOAgvwQZPcDpMQlNJ8KxZ1lJw3Egu1MJVv/kvvBrlbigXor8c8pd7kD+Pi6PJyAQy'
        b'M5m5zEJmKbOSWcuE6MxGZiuzk405aDOPV8+p5yO5zx5Je3wkA/LrzXEgp3r7ercyMxySiUiQZiQIk1aCNCcpTpsomfMZFyMTBDMW/u9iZIJgxsL/XYxMEMxY+L+LkQmC'
        b'GQv/dzEyQTBj4f8uRiYIZiz8X59qy9BfxpUFIMrtSB5JBeq1cjvtEsIxeic9zw7ls2eDOI1B30+TEE725AwHcHKwYEJncYkbX4Eu8K2w3gZxx47wx6Hesd6p3rnepd61'
        b'zEkWvMkCmyTMprrN0H/nM2JdnJ5I/C7ETa4s1CAEl5Mur/mZMMO8JAiUPp9zXQgaY6IGrHG71ALdB+jcATpHzB/gpCYOcNKTBzjJ+ei3YIAzI22Am5gqHeAmZWYOcFMT'
        b'cwe46fnoLC0PHWakpQxwpTnoLDcLZcnLQYf8ZHxjXqYC+6lHT6Tnim0GOImpA5ykTEUeHt456ajstLwBTlb6AEeaM8DJzRrg5KHf/GTFLJJhxjyUoRARkz7MsJXg2Rn3'
        b'GEws4f0U8YtMIRWDR7wic428IvMsjHweG0YRpqm3uG/xWK/IQ1J1XpHxYskwDYoMmzrfuTypOhOdg13gFjiI+54KNuRI4I5sHF2WiSkL3qnEHm1JOFdJOnELmhWWnj0z'
        b'DTaEZWCvqqCLR02FG23BZdANTlfEfhJEK2NRofxfTWn7ZByODN/csbej/tam3bRlnuvsGY+ytwfOeDsrsidslsBa8zEv3+3Te602VJOvuc+5ZjGXOEbNA1vheivQFZbG'
        b'OimFh+Emagy8yQVn4XpwnQmJfhE0wxOw0R+sz4HbEC3YI3sbZ5UDxbjPv74o3d0GNIJdcFdmOPrEXWaUlTMHbgWdSUgbMrV+gfkyBNTqaNjWtIhW3MWUeMQiMT69KEeX'
        b'lrAeh7FkPs7pdc/VOOYaolm1zmqYudFMD7tV4EhBphx2EkNJNhLmjxFzEY/I2MEPjj5e4kXTPq8b/nKfIJA6bhXJLTWU1my0jQXHW9xnpo1+vZW3lb9VsNUMtV1L1HZ5'
        b'aCDg15uhwYEZDgQkip1dmQ1pz2hwbLDStWcL0p7NDdqzhUHLNX/Lgm3PQ1J17bl8aHvWBYzRtWcfKQlnPAvcTs7UxhtETTc8XILjIpOYwrhRwT0phbm1YFMa6ORScGeN'
        b'FWxaALeqsatT2J1bp38UNfKc8FnEpzPsVKMy4A40Ke3KnB0MG2abo/7Co8ANcN5KmLeauJZ+lmaGw4an9YQXh1XIqyjiWho2+ycqhWAPXI+Gb8a1tGQZyf7lSnMKVXeN'
        b'Z3mx9bUcAaUm/n6vhdcZhUM2cDI9OzwdvjvLjJqbb1YHdliTeB/RcD3cmpmenRkGd4jfltKUlZQDT8wGR9S4J8H34HnQFpqG3VHD5ujINZaRYFNxJuUHrnDBnewJ6kj8'
        b'yi2wwTVUir0K78guzNX6sU4DbREzgyXhwbA+IgRHfq4Wm6PZeIMV+ax1gYFwIzyWCRvTsyIElMCFYzOniDRxcjvRDu6dHRSK2R2O7oKbnPHe9uSOBWhYQ9ILc80o8xUc'
        b'c7WlUq6egOnYALrn57M+tPUvnhkMd4XBhtxgKTwCT2qpNKPAQdBsOdvbWY0tXdZNqsk3A0fBTooKpoLhOXCdCWeyEbZNVK6EzebwIo+iQSsFd4HuZDV2MAAvT4tHnN4R'
        b'JoE7cXCXmpXwYkEwquLGsLDswjS4M0fr51sfuxIeA++D21xrVMoBuFlNvCqfgU0JmUwGMdyWBbfC3eiTHVK58JB3EYm6goaqc0k6Bo+FRynKKpMD3p0CjhPJR7AInszH'
        b'sVzQeNtVECyA7+k/nlBAUTl2ZjXUEvKpy8HdRNiMTURWo9pvyg6MINFZwHlE+npUQRdqV8LLoKEWXnQapxJQQg8OaBUISM+ALXAf2K2EF1WoVYfNCs4IR60GjePMWxCD'
        b'd05MYdiLvgANr9ctKWtwngTqht3540MxcxCzUHfYlR8cjMbm+gi4J1nKMgu3HFQt60GXBWK8vRpb6MykYKsVvAovK+G1FWBHrcJ6BdyYDa9SlEs0F2wCm21JvG4uPB8F'
        b'G1GTzw6XpGVVx0v5lD3YxwXn4OVo0lemhPBwhzd/Pr3YemutlGlk4Eauo3IF0qTgLgqczgPbUL03VGxttqSVeFf5l+bifQXx1SDS7ooDJ8pH+v3Y6fMfdi1silNXv23e'
        b'ePxUyh+bRA9nlXTd9FzzGf211ffN7+dW7ok7BmbsKf/yN2tqv/rC5V9jnTfETcwdqH48V3b3yMDGPdBeVfv9D+2P09pcl6Ve3n/0/TN7XRqr7jfLe/PHKW0nnfr9ORHw'
        b'tu9wOue2tIrKDwOtXx7l+LRUOgb/VrxZXvy3TvHx5tRd95Iq3prxUagwPiM39lc9eRZpi8fM3WteqwZ//OKLxUeU/12e9NuMf237IKbZh/veLyJO1I1JKnzo+M0nnKLx'
        b'2R6Fd6/YvpWVHP/x2+lw1raz9A9bLG08D//nr9NnF15VzlknH/PthRCvXj9l24F/lfU8UHeXTr4deubyjoGgrj/85f0/7vzDJ3f+x+HzkKdbqjJTvY64zM+0t9ld0XR0'
        b'6m8afvhSut7j23sLrffx/5j+ue29Xww0Fv8qdvOJ25E3Cmp/e7xu1sPswbI7A2u66q13io/8fkxDyeCfevLWPPZ/cIh/+1L0b36+7kyV4PlleYnNkq4169++HxN09JtL'
        b'D/953+2rX3B2nKpX2bZvX3IsdpfdjuetjWmnP3DL//Sk09SgP2R0nORlO4K/F244sDbS/8mf3XocLvl9V+R+uu3If36kPCv90vwf/0v/ZdL2sX4DYn/ionzpW3Z60QBu'
        b'gNciOKxoAHYtJTlS0sAx1InBzghpeBq8A/dgn+3nOfA4vAt3M5HFz6GBsV0bsTwH3DRwhW5RQ7LkFMIjoLHWRghugj2WCnhFCa+qhALKcQU3v2z6gF2E0ikzRyIIZ0LE'
        b'rCt4hm3j7KZGwsasDLCpBm7nokZ9hwZtcBPcS8iaAK6i4asxDMlVYlifBu9aYLrOceBRuDmK5BBI4C3QaLsSXq2BV9RCAbpqoKxcOEtgO3iHOJv3CR4HroIW1qc+8agP'
        b'68FtQvEMsLEIyWhhIWIJGtGvkEGTolxFvEWo/zUxYeI3gKvRmRL4flm2gOLU0VPgXvgukaZ4cAtoRZ17GxqE7kzH1PMm0eACvCAiEXG48OKETLhNEZSFnltER9StexaO'
        b'y2v0TVKutF6hhtdswTaw3dZcaAm7bVeijg6v1q4QCjxdqWyeANxAX3KYfIBXNGz2gM2h4XBHVhRNCebS8IwVfI8EJnKEh8bhaadpJTiLBIR1dMoCKZEHl08GLaAxB42O'
        b'Z8Yr0rIBmoMlGdlcyh1c4dUGgf1E4JuT+xbOsxPNz6gO4DF4EQl80znw3Siwg3AXvM8D+7G/fWaYQUMuGtj5lHMWT2hRQIiLnowqa7cPaIzADYxPCYo5fjXgIil+OVwv'
        b'QjfYQRzsAPv5lFUOB42n62eSEEBj4WV7XDpqdzlYSsCvaAAt4YhjPvA4D15Kh5cIqxW5oI3NiBsoT15G2SBJJCmilIlGcMtxZTESyHFgpx1ZiEXpHBcbsIcwIhkcgmfx'
        b's9nhieA9iTQrB+yAu1Amd3iQtyI4jPHhvwk1Oswv3bQFN82lbPK52d5gFwlLkDpWiG5LwpF4k1k5g4ta4TYOaprr48ndpWWIAzkZYelIVqHMJ3LAIXBwMWoWB8lnlr+V'
        b'gu+GgqM4A6jPYd6RjppjSDAf9cdT8CKhdY0StKKc0jDQEMFOFevTEL994DU+H+6teEYmrY2COYQURsa5BE/iYBD24BwXTzTRzyYSgeGGD+4VBurJNrAfvRM0gF0RxqsF'
        b'oWja2uFvCQ7T8PgzvLK9Igoc1z0MT6m16g15FnTB+iyxgMqizMBFNHM2kkYNjy8E7WSe24W0HfR9adnoQ3dGZKKP2MnsUKWCC2Z0GtgVM4VExoJHV8LTTOMA+IF0sB4/'
        b'I6CcUce5mwK6/u0+NLT2eEN9aJCNHKchegOzg0O0mMscJkxppRc2DAvqnPDQJZroMWwc0scu3tjx40OXYLJimNLrnqpxTH3i4kNimkb0+ET0+UT3+ER3p17LupB1z/6e'
        b'ryYm6Z681yfr1WOdPnHx6vcJ6ozt8Yl84C3tll1bfmH5vfSe8dIH3qWavNKmVOxPeGHrwj4vSY+XpLP2/NqutdcTr8/UREy759Lrld6U8tjN67BXq1efW0iPW0jn+F63'
        b'cU2CRy5e5E3T743v0fqM6fcJxG6oOoO6x/X6jG+yZp0PN69t4vU7uLSsbC9vfbvHQfIb94AH+bMfzC3SBBb3updoHEseO7j1OQT0OAS0Fz50CEUfm3kxk5Se0eueqXHM'
        b'fOzph33Vta/p9Yxusnjk4NnuctKzw7NzcecKjW/Udbce30RU6EBgaGfB+bldc7vrHoYnDHLpsTOwO3aPJOyO3Qkd0ezi045USUl37bU1F9eQNyTdW9kTmN3rLtU4Sp84'
        b'eLdPfjg+q8c/i/22yT2B0l73HI1jzmMH3/YFPQ5RqJDgMBwz4ujavqAJPUET+oLie4Lie4OmNSV95hjwOCi0Kekh+vUJJHaMfsGdHj1+sejcVmcTydzRWieytpeMT+e2'
        b'BSSLf9DJuI64k1M7pvb5T+jxn9DrPwlnFvWLgkhmtgjW3nFsEGOBGRDBlGgQkJbdKCT2mfjt1o/8xrar+4Km9QRNexBUci/1w6z7WX1J83uS5msWFPcmlfT6LW7i7bM1'
        b'UKjHsN6HtHbEPLzer8COgxTReE3GqrREpTMJFihLl8iXy181VIZBL8PdqZj9o+trP9rJrmHtHCsb/0K97LtlSD3Pob+j8PFrcnwNXV2JxeBjghjqstU07hvgnbFFM2HC'
        b'SDuKxl+ii4xrBBQdvR3b4ZfsZZp+8wtjiGowRirqPGUwnyJiQzSIghXyEll4dVVlnfgNrEAZd9MDVkWshUZRhez1SP6nMQQ4/IEX4zP3RZgpu48Kpf57DD/gDWgnyL7X'
        b'oxkvUhoYIXkXEGsPbOuhM/96U9oYvCq2rVerqsvKXo8+Ls+oGUQQIwC1KhwVJMKOBvQWKphmYjr8xgQTM1an126xAkyqHgUcQlDAFWUs7Hc5xnyjOpdXYTcpsp+GSsRW'
        b'6yKDke71CLbABNtoN5kZExCMVS7H4eR0Jmc/RdNU+L52w7TGxOmx3kEjx+I2JtHw7bqt8mKKQQ+xrqi4ZKES72Xqwg+uo8lCJWWwUEkbLElSb9HsQuWQ1NdZeBdITfu9'
        b'XISpo0noa+z2SBvsWrcJ8JMEu8YOEU2GTk4xDLlsDBZWipRLqtWVMryljsbairIKbNpbXoIhxibLUrEel0QzKuUl2A5DlET8ieAGxcZkJhZbeJqsQP2VsS6oMB3TWSkn'
        b'cRuLiwsUajmafiuYnh6yrLpKVY0mgNJlIaLKisWKElQ4tlTRRn82WRi2tlANG9vQY1pMJhNLkbGAqTMwLDFZGmMboyMwpaRSiSgcHsWQuDgybBS6TqNrFFxpxV+/oLhK'
        b'vGLYsulo2ycTD3U087f4NtIOvOiaMoqa/Bnnd5fjxDRRr2C3P1Iv9TqHTuGoRCpHEDiH+pidto+xGANeWblctTrAqJMpSyuLCAdRd8MMUU6V4FxEOcDP4y2OShHlKcI+'
        b'KTSOhjsZLKTMWIoimyjFWmi4AntSfbU32vHYfYy/r6eeLRTRtP3r7mM0CURUu1Uo17RT6DLS8dmIpHyyU0Gz+27YbbNuF+2niEb6CvtuGBYILvmDPUMVTbzd0JAlg4dC'
        b'MsLAqQJmMRyn5WThNXhwGjRYTQK7we2KzP+5wCPx2aydopmtthtpt6M8mqNQg3FU7o+E/eLtp918z4xNGbtF2i5xvdssfs/ixKk9G6KF1Jl8i3ngczH3WRSm48g8eJah'
        b'A2nWV16m9IJd8CLcRSI0TgLN8DgOCK2NBu1jZxgP2gvuIboxaAOb3x7aTqWVjGoMTsA7r7IZh5qu8pWarpJtusFM0/1aIaJcvdoL+wLjHwTGf+EdognN6PXO1LhmPhob'
        b'0hl7dFlT0r4co8050qSFL9MO2M05vRdTBXi1Ro5oc9c2chxSbwVq5G6vE00Po/HFHGZf4wjYAZozM3PCaYpXaGFLg5PwGDxLVsWnWU7ODJXiG+AdsDUaBwV/p6ziq6oz'
        b'PLIxq/4qou2TKYc2NHe8I3b6eEfU5gubjzp/9Mfivxanl0pLOE9dl7kudc1v+SqSH11zlaL6ploMLixn2PMj2G9Dx646Bqx2Ns0YUk3eTDX188yfzROZjwn91pE7Ztyg'
        b'OeUb2Cnr0Ttr1b59xCoxfrsC4goZ4b222ipA7/12PqoCi9epAgw+Nj11F1PMzj6Jd0yVcf4Nk/crCBZoDkkFUzhK3EG/XxLf9knMoQ0NHc0dCblkWDhTtklz3/rg/1DL'
        b'1/G8fnEJTSV4gQ2ud4Y3h6ywMStkoEM90gIb2D9JzDGoAg7prwagyqG71QRNSWrdhe2c030pVw8TgEptdZuYXvTVbbA5PvLrfA0mledvv+ak8pLK/rfLaZuGVjU1rKp5'
        b'0oKKL+qseErc5381YWXbJwu3Iolhz240vFu2c1wKG7Sg0yFyAAM6HbpewaBNSf1YMPUzmILqx/M1J/yXlB1gOMMn+75mZdzm/D+rjGEz+vAo1KjfFVR9QBNUSPG637V9'
        b'4vAM1QXGvMS5XWxxjZzuHHqif6mr8DOPT++1CqgvFvFFHyjR9EvG8jvg4nzYGIaX0HnT0Wy7gQZXLBY/w1viCliPNwuMu2ad00uXvuFVCdmMyl8KzocImFDA4QLKHN7i'
        b'gN3pcL2JFkHw2sNWsAhQm7QIEdMinmXhFqEFa/d5ju/xHN/rOdHAnf+rN5SXvDLIsKFkjqqhGEJZPLW1hR0K7nMyCWXBiDYb4qBYi2kT1DsQxJsO2VbvVu9eb1bvgfRG'
        b'qt6z3qveu8xTB3MR/mQwl2GD/HCYyxSpGrM2F243y4SNfHBRh8CogicYCAaWvMaCs+CylQJegVds8dY7vKgSuIJjlB04xoE3x8AGBvGyo3oyAQSkoXaSA86YRAXoMAFw'
        b'yyoPcNEKXFk2WSwg0sbY2WFKeBWpI2i0hE0U2A53gy2MjHIBbPGBl9QCMXgH3TtMgd3wNLhD7sH1dvOs4FU+OAgb0dUVCnSAG7CNlGgelapU0fAA3I3u1FNgC9gLWtV4'
        b'gzAMSTkdVkoe2ISmLXieAi2rBeRGPNgOziprOVxPHACbAtvAcVsCG/h+MUHk2EWm7C//mVhOMYS9B7rmYaAEbzbYjndvKPAuuLWWMBW2roA7yAdtg9fYL5ogJfCUVCtw'
        b'jnAKMQh92zVDJsFulQJezk8LxRuoDHqiCbRYrAMt45hXNo4B70fDpuhIHkVzwHuIG3B9dCGB37wFuwuMED+sl20R2BY6M3c23BedkW9GFcIWAbyCBP/TatybVtmC8+O9'
        b'otFZFBUVD5oIMgTUB4SBjZkQ48UjqAh4oq7y+3/961+Viwl2QhQ5a8WcS3kySp2A8zbDDY6ZWofeSMNIC8Oqx46IjMJg2IBoyA8Ww12z09KzsfyfjYOGX83DH/aWmaBK'
        b'uLBYxWBoTkajemvMgVtgo2Fe3JrQsNQQkcMyyBDGhNvRaXDLGl40gxfVxbiY7VPhYSF6YLcQrI8058P1hfA9AdxZIEyxdzefkgdugfcxlCm5fJVFmcsKS3hbUGsOtlnk'
        b'WINu+A48FgnfXyP2AUfgHVg/WQIPCMD+GWJwaWoMbHUFLdLx6nz8xR0T1+ANyg1CKsqcC7oLwcV5cJ8ANMCtYN9ysC8EbILvw11gZ4FHxVugE673AO8v9fMA11Dj2gyu'
        b'lq2Bm7hRwYiMHT7wQpJDdiC8ocBtjDQ063x3OoZDmXdL+0P21agpArcJds2CjdngTC6sT0ffHgEbcgkIjdkOlRamgbNp0uxspNcttsWYhGtWpXB7EClPkJpGNVFUZCT/'
        b'06J1XqspNd7QgJfAdXARf0OrhfNaSmSNTmctWgb2gDPwJuygo8BGeHxyNGpMzcXgCjwDDxQGwaPzEMnrnQrARjmoL4ft8LrZEnDbrg4cm0iaNTwYiWEJw8lMC8/g2zth'
        b'hCfoEqN/qFtFgn3wtAW8Zga7CsQ0gzDbElCKXtiI5iO4Mz0MjRXhgkC4kXIx50WCNvguGWTW5IDdmeEZ2flpRNlNx3C00FkEVIqaoLcX0+x3poVlZEnSw0NQ+9gmtq7w'
        b'hJcZ6NEJeGmOKezRUOARPLYAY4/SfRBteCSZCXetxrAregmH4oCd9AykvDaqcYhM0JSJ6EhDfNuezTT/iIz08DwMD+RbpRUOg6ClIVW8Bvf93LzwWRyqrsC2Dm5dQJpV'
        b'JnpvF4P/Sp/JPJjGqvJpWTnkSyUzzVfCqzPTMrKlYeHSFfMJFBF3Nh30DI/NqBfkjQHHnWAraQFxZRwiaEQ6/2l2VVkIEuTUBPZ6TlmcyWzdc+FmcALN690cUA835pAm'
        b'4kqBS/k54mywIyc9LL1wtjs8OhwAWUihRn8K0d0A9sDtC0TgNGpXx9J8wd0032hwnkchPm2wB60SsIPUcQhsgV1owLxka2EOL9rCS6oVappyVMZFc3PgBnCCABFhiw9o'
        b'ysejFZei4SG4CZ6h4JkocJjAGlPAAX6mOJwsbkgRYcFIeGkONLb7XCgyBxsdJpPSQhZNygc7CuCOwmw6Axyg+CE0OICoPshgKo/A1llWK21oeKcSvexdNJ6YZZM7QemT'
        b'YGMWDZrBVoqeSCH27gXXSYlo7thdk6mH8lnN4zhw4LnpiQz1t8zgcYzdIcAdcCubYHfWgPVkYJ3pPjsTbssSOMHbBP4yX8AUeWoN2MnA1vgU7y1425tGY9AVsF1N8CbH'
        b'YRdo1yIDwSkeZW0HNoKjXKc8NJ9hLMUM0CoEG+Bp1LbFZBElLB3jOZjyxoL1/LKyXFLp2T5gu26spifC46jWWzhg3/RQ8tET81ND2R7Bp6zLk6O5ttme5I4nH5zKRA0B'
        b'kQc2OfBoJB1un09mJCnYB07AxnCwJV1KICSChRwnL3NmElw/ZhpsJBAbHrjkM54GXXDbfHJrBjgAr+GujG7ZKtD3HoWX4XoSIYIHD6ORqZG5Vwbem0qD07AbnlbjdQt4'
        b'cTHYoyUSNU7cb/ngHdhA+YJmvgW4Dm8wWNT2iOmonzfkSOF20BAxhDHR4F3CGynYYAab4EVwhJEmrrtSGPkkDhfA5omUxSQOOA7WryLIQnge7Eez0yWMQLxkhoaBQ2iK'
        b'PkuHoyZ+qSLzys95Sgc0W76zcdvmWdk5n0+3+80Vrw/T0+otXCdP/77m+5DNeRlWZ09dTUwr/NX7igXH/3jik/sJjh3Pj197orE69cIf7Ppz/wWvybc6JlUerKsu+3L7'
        b'4b6/X3qxf/p+h79D9aQPgntTBr6PC9D8dsunbj/IboomBNSc/4+5721YM2fcd78MkCV92Hc3OHSzY13h5ncnbXYGn463iC2I8vhs89hnP7j53lf+9hf/cXvmUy/XRJeY'
        b'vPCYWX/9W8mxAFVZ8myYcq55m6bx1P1fm396Yan7//z32o1rU4R/Xix4eu3+77M3H9gE52/b+fu8mJg5C1071SLrO8eKf50/dtmqMXc3TV6ZJG488M//EO/4BrT8ddtk'
        b'hXz7TYXjvj832hfVZSjvC7PV6oqMZY+hzZnvxv2Knzoz6PFXcQ1/XR4++/NfPn9cVLJoyX/+o+Uz+7Jt1p9P+iGx5MPN6X9p57215OKv35+mmRMas7nrj5HPbYvadmwe'
        b'+33O7z548W7Q5A/vfrNQ8sF3oV/+Li9BXf7AQxnwV0WVX9W4hO8s7rR99eEnC34ff7V3jSh7beCH33HMbv9Juu03mo3/Met+m2Lu/uqPlBZv/e9Xc9/POzzlfuqcJ3c8'
        b'Z19a8bdznknvr1uQ+Q/Pv361t/Zh7Imbjx7fGrf17EnrjHsWIRfOe835xZS/lBwT/jLca+nebuHDKyc1V1qf/u3QhkMP+3+5dI7rI06Qsqk58t1xW4Q205r+VOatEjSm'
        b'/3Lx+A0Dz0t+/fNZ91fc6nyadu7E1Mb72au/mVu71nnjrp2xHy6Z4yw/szLsq984rru6cPAXDZ/a/vGPq5YIpeXLdub8t2Tavt2qaf0/e3To44mfp7v5+/8m/S8hVz3u'
        b'zgxLAZb9Z1bMBg2fc82+Uksu/X1ysu3u6j9Gfnn0S4vPHX5n9sm3HQ1/in7+6ZhJuWucd/9h4feLGjz9niY0ePo+TW+4TXn0lZb854N77UmPK/p6B3f+6Q+1d1PHrLGw'
        b'ORc0sc1Kvnk2AM8dFywoarQ8V30PPq/84C59Zafy2283/HCixOmSxGnutn9Fg0/+syt2psesFR8IS55Ed096ELTih7m7527+c8PP3lv2x/jNTjvm/qXqh+T7ETm/tJz5'
        b'z4yQL3+gc47bXFGsFQcStJo0nzKA1WFIXbA/B74Lrk4lwED47vIkvAoJ2yMIEJLKJUBDeNoSnCFD5jTwHhky34LvM4ivw4E1WuAlWS8GN9FQTZCX4BS8TBBoaEi5laDF'
        b'S/Phe3mUObjCWemQ8MyD9Pb4yUbjeDXcigZyJKMxGEm4pRLJUtqh3DafjOQrFjHYuAZ4DAl5WnAoAYY6w80ceDwCniNP28HNcH1oJhdJOohGPiVYyvFG4ukzPPgFOi4L'
        b'DZGI4bYwauFMymIuHmY2xxJlG24D25xCJWBfNJ7iwtBwCnZywitTCQ9nwSPCTFYAhlccMcTNdha3Ug1OkZV0S2U1xvRhGSpHL0ILwNVVlE8mD77Hm03eHgE2ZqE37Akl'
        b'BKAXnOFEx04l7LZJVYaGR4CdelToLHiJ4N/AnRmUEuwwXyGEF5XwcglGhg9DaVLZ8IoA3KmdwvCohVMUqluuj6XJxpJ9Ohe0g/cYnKpkVmqmdocgZx4SolA9U2PgVi7Y'
        b'PiaHoCVrxmPwXwSq33Ayu5/mZZpRtjncJbCpjIBV4YEIeCE0JwwNxkj1QTetkOx+BXRz4DVwWMK0govybK2kYwb2sIIOBdsIN96C18Fm7dTWkoSntklwC3l5gATe0kKE'
        b'PZH8s02HELbOJ3W8Dhy0wdRdtNFDLBejhzHD4A0r2GG84oImkBsmIYNWc0j9geYMVP0MPtUYnRoID/NqF4PrJFuMK5qwWGAlqE8rGIqcTBaR5m2ZADeHSsQZZFsFHgdX'
        b'USO0heu51XnRpDFFFSDdpBG1EObjraoWcTmwDVyA3YQvGYunaedg2A268CSMpBamY7xTYaaTVtBHHsDiSrE5w+yT4eHGoso8cJjrFGHxDM/eHuC8Dzw3YWQ5RRBEatUB'
        b'nkLaR3a4HpmaDbsoZ7iFZ++KGjsxQbhQXDNsrRm+O+ZlK1rL57NjzUplZlY6DS44Upw8OkSymHzWXNvSzLBgNFRk0mDbQjRUnObUVYKb4uB/H+by/+6B7GYZbiQPj5g2'
        b'BPc5YDskyhDjY0C30jbkLlnjs+Ezq74FvpQo4PDa1rUMvrPb7Lp9r88UDJb03r9mz5p+F//2tT0u0V94B2vEWR+pfrXm4zU94nm93vM1rvMfB2dpHAP7A4JPZnVk9QXE'
        b'9gTEdi/uXqEJmNSU3R8YdnJBx4Juv+4oTWBsk7TfJaDT5oHLeJxe1FH0MHD8dYkma2FP3ML+wHHdsgeBcdff0swsfDCtkLwq7aOpPeK5vd7zNK7zHju4taa2p7TlPHAI'
        b'ZeGkK3sCk3vdUzSOKY+8RO3OGH3Z6yXp84rt8YrtLu31imuy7HdwbgnpcQjo9xGzn8bt9YnpzuvxmdiUhu3NJzava1/xwCWYvC9Xk7+wR7yw13uRxnVRv4sXhsF2ju0L'
        b'ie9B/1zi7wV/KLkv0cwseJjI0CfVzJzdN7O4B/0TF/d6l2hcS544eLWUd/I7Ze1rHzrE4DdMaF6rfcMgh/ZKpr/hcnxS6EGK45aC4Z8R43scQ5uk7amPPGK7qx56JJOi'
        b'F/V6F2lci564oMp46DKxXxzZYtPvF9Bq9lgcis58I/p8Y3t8Y3t9J/T5xvf4xvf6Tmuy6Xf3PRzeGt4W0WT2yD2wvbzXXYLOHJybapuntPs/cAgkjNPyDKW/1eswttNe'
        b'y9G8Xvd8jWP+EwcX1hK/fdyetwg1Kb3eqRpX7E2tdU1nzPWkhz4JD1wSyK3MXu8sjWvWy2GqLvun7pnaXn6yuqP64dgJ/Wyr8gk4/Hbr252159d0rbnH+1B4X9jy9kMf'
        b'6Rd+YZrw+ZpF8r5FFT3oX3hFr99SjefSx67eh21abTRB8x+6LiAOijriOpdc5z70n/LIJ7Qz7VT2dfpewIeh90NRIbvTHjn5tJt3+j90kjzyCeucg8G/aThG75JO84cO'
        b'Uf0+QYfXta5rextldPNvT+uUPXRjUNDze90XaBwXPNFGJ22vPbm2Y213wYPYjOsL+z1821Nap3Wmdi/6hku7JtNNPPR1KOOU1ik9DkFMw+x1j9c4xj/GLsYQ0/2JizHs'
        b'lWF30hMPbyYqbld0p6ovIrEnIrE3dAZGQrv2ieN6xHHXJ/aKk1DJnil0UxLGBrvuj98d3578wEGMw6Mk9Xv5ty9unb875bGHH0Zn9HlE9HhENCU9cQ3qdwx4ynVws3/i'
        b'4jHIR7/Yt1XAoBk6GzSnUMPwPOA5aIGvLCk30WGrA1aDVvjKWntPiK9s0DOHcw7kDNriKzvKP6TPb8IDvwmDY3CJ9pSn36ADvuNIeYU+8EzrtrlnpolIe+A566PZH2V8'
        b'P+iEczlT7n6DLjiXK+XhczjiQMSgG053p9y9Bz3wmSc+88Jn3vjMB5+JKL/wQV/8lB8lDj9v3WXdF5z4IDhx0B/fDcBvDkRnTfzBMPRMn1tYj1tYn1tkj1tkt2Ov23gC'
        b'/n7khS66V91z7fXKaErpt3Peb7nbsiW2PfihXWh/2LgmHuPzoj2px07cb+e433q3tTYFR2xx8WyyNtjR8GF2NA5giBxx/xCED6EEXyxfpUPdGbhfeB1w8U80TWDxehhE'
        b'2ZRVwHOde56RZoQQvAWTRrG45Zm+NJ1PcMvGx9dBL2OHLxcFCRzqPscqQcgV08RfhfQVwDp0PfbGIPi3gHXKxJwnjzgm8HAJZSq5QlRaUllJwtZhjC4bxg9xqgKzqKTS'
        b'KJodE1BAJmMi1JSIquS1wwpl8J/BxcW5y1XpVWWolhZXVpcuE0vYyINahJ1aKS9TV2KYW121WlRbUkXQZbKKlRWy4Sg0IyIqqkjGMuLBj3VdI1cy/myYqDki7K5dVCFT'
        b'DseoDUuIqylRlCwXYceDcaJ0gnRDrVxZgaP7ofdg1FuJqFStVFUvZ4rVfVq6rLhYjL06jwgORPzR8gOfVlSJVk6QjEOsSERsrMXMVC0pUemo1eMPTZbIfhsJOUjAwAzK'
        b'DxWAAxAasUjrGahcUa2uIVFHTJaIPl1VUaquLFEwOEZljbxU509RKQrG/tPCEAvQa4nD3LoadClXlUrEpBJGwDFihqrk2nph653gv6sQzWrESFQ+bnV12tqXVRO/RDU4'
        b'WKWpMo0qYHid/si+taWU2Z7aaRuI1PvlcItuKxGcApeYvUS8UgkaLMHmoXa8rBHvzWVgEzwFd6mlKGMoaIfN7C6LyJyLN3JuroiEe9290xwCV4Bt9uvg+Tykqp+dAfbO'
        b'T0xXgdNIEek2j5eGecGDsAMeTAK3fFaDU3aR4BTcTRbC9wSkr7WiRTQa20Kqs6IYgtztgskKZX4wtrXDNuPYMN+MygMn/Jby4GnwLmCW0Z/O5K3+nIPGx+nFYfdLqqiK'
        b'jsBUrvIQuiP84CQDm5vUSDvIokq3HY88EXm2bGP3Mre8lmWun7hu+9/1L+ZGfuacvrcbPr9AfVZTfKprcWnxnF+Yl0yIWjnOeZnqomxF6an5QqWDrXPt0/+e9SU/5lLa'
        b'9gbs82JMWY7lsqtWGvUXgRtr+i743urYeKGlYbcv3zXk64ORToc+ddo+16/l22Pds78eFxkQfXHdz5X3k0LcJs6n8vd45/g1iq2IKjvfF9QbLr9wwbuMUSMXNBObSaRt'
        b'3oA3CA6Ms5KOmJ4A9qUSPQu8v9AT6Vk+gcNRPSOpWSXwAIGWCsFtcE4JzgbmpUnDg7Wr82NgExd0g3PwHaKmgnMieJtdo4HX4G6kCZJFmlWwgSyISOH16tBwcAZ0GFh6'
        b'roNXyHpFiDm4hS09GTNPeDE/BZ6az6yj3IRdiaHhcDc4ZGDiurGcWZnocoY3rcCOdMP1I2btSOlKdGxE7EkaHFxiUhvn1YLtnkSfBRvh/rf0urihJl4UhnVxt+QfBbvp'
        b'lS0L7IiDdOkhoDNdOlGwcLQArGAtCjStYPWzFlxIsu5zCXngEvJb76BBihZPp/sTU7Ao+zWXFkuxxZhPDrYYc8uhn3j4IMEQlYbEyLa1WoO82B6f2F6fCS08JL23zmjn'
        b'taV3cg5IkTzaXtTrHqtxjO33DzoypTOGMdki3r8eILlnRY9d8K9Zj41GcMiQl8kzw+GQfO4w9J2OEUcNAZAzAmna9bUBkPSAGZofi9AEadoZHpEdaJ2LHcbBDlfnYIf/'
        b'kznY2YRkh+95JmSHfHkVG07LOKqvWsnIEnIymqOpJzkxfUa+QaTekSZg+eKKUmVRaWUFKiWOwOa1vr7LcJyd0iUSkkOSjI8zSLaRAgAblMpyMY7g/sN0wH8cX08pJ2RW'
        b'K2Q4AU1tJqceNqDxiDRIUgqziknoB3VNZXWJTPv1WoaYLBRHotKFcsCzImvWo1RXqJiwwjqiTE+IP0rVjBkFxWGjfbRw1I+m54720YQ580b91qSk0T+aONpH5ySPG/2j'
        b'0cWiEcTGV3g4ZgTTi/QyIkWxQpxcFiYKYZt/iJH9hrGBCYFum5a6RjIbSVGUkFCV+jb8OhYis7GczowKK6MlkUa9hVi2MAHLmO6EXriyomR0nEosKDRBQhzjJVzJjDEM'
        b'HUx3q5D9iGg5HKXmJCXyV1SBGWW9qoZDiYqzDruvodQ4V7U72K60ivFEEwtsp0AruCgiW8jgIthJwUuRkZF8CkkI5zjpFHwPbCkiW8/gINgGL4dKJUiYoDngXToTboUX'
        b'CP4rFVygQ6UZHApeieeAjfRE0GFGXgSaFXNDpek0VWHFAfX0lPHgiphHRN4kuCOSQBrgRfSu1iiuOx0/ER5jxOFbJY7oXreKQMAuL+fAfbQvJ5pAAYLHBSvHKTjUQthO'
        b'V1Pg2lRP8sh8JFhdV8KrtgpU2mk5B56gQ8BuCzWeEV2TFxBIFjhvHUFFgMvxhGYBuJWJHpiHPZ4ywLmtUSy6H95Kgnt1xJXDTZi4oDICBbBFbDirIw40RxPiUOI58qgD'
        b'fBc0aulYD5oIIWkFhBmqIniU0D7NgZBeDm6LuQzf62H7DN0L4XUP/EJwJIqgHESOoEv/wtOgjbxxDThO+BEJDwVbrbRQ8qiCFVwLOiI1nSRzwWG5lVBhS1FZidwwelrI'
        b'PObLukEnPI53461saArcWcO1pqctq1Jjl5LgtDm4kYnl+Hxi8YKxPkiwp+ARsGctUhm2w01IMN0LDhagi73wNjwG9yCdYW8WPABu2yOy3wXd1nPgKSH5WLgjuDQfNoHD'
        b'lehiKZUOjqQTX0zwEt8eNmO7mu356KoDvscFDXQC2AyvVmwb+5hWYu9/DwePYBuJjuZYohqUINXgWGRG1MNxqoux3b9G5/JlkZGqC+qLTk4rL8ouFM/81cHlv7yXu3cv'
        b'4Gw6I64U/1k552J/1Gf0wnsbxDcPjEnsG/frSGlxWEbmk4/+64NT+83yL2+J2mFx7rBF5xafxr/n3nzX7Q+rE8LKIj+LPL9lS2Ik99O7yVkOrt84rp8ijYx4/sj71uf5'
        b'15E+wtvwe8tSZdSn8vsT174HhOM9jhXtDfvnlOJ/lm948fOPH/zKSvW+d66Uk2/z55AKzomLso/3yCN8vvjyqex/vtr6p9kBmdP8vtiHsnH7zm8rershbsEu6lvHKW1R'
        b'yXa3wqe7dbiLJu0Xli1y8C8XUOnq2Yf/IRU7kh2nxeu8DPZbwe4cq3l4v/UQPMtsHTUhpWC9dsM1MYhxeyNl93IX2ceEGhgRwU6FdRjXDBxXMurL7fngHNFe6uApvH+8'
        b'FuwjGoKFY2Io44QlwpYHNtHwnXhwnlDj7AC1jmrQ68ChWsZRzSnQSBQIv1zPUGkMPMFuHjNKCWgMIcSkrALNoRm2SBfKxMK+OWzkgA3wFthEts7glaVRSit4habgUR8a'
        b'NiJi4c2ZZI8pBENEG2ti0QjTDRtouBV9dSm4QB6LdUYcQPcE1BK4l8YNdjc45kiIAXdA/TJ8DxX5DjhKwwYK7gF3RUS3g20OctYPTC24zmxHE0cwoC2c2a+7C1rhDeVK'
        b'1FNWyWhwAj2B3v4eoye1+4E9SrAd1HOo5bCNRiMIvAxuryRcdV0HN6HH+FSAJQ1OUvDgVLCDkGpjDnaiwQENOZGgnQbnKHiIiz6ejHnnwYYQ5coVNDUd3KVBC4Xq6wZs'
        b'eYb70tw5EegOh/KBp2ikgMJtpZVEUQRnwZYFSgxi1KuJReAEoynWwPNIgXiFZUusQOD5RG/spUQC9OoxxvY7KIloUTjKFdaiqsbqtKjIHp/IbvtuX41PDNai3Jum9fuE'
        b'dqp6fKKbUp84uLesZX2UrHzgE98fGNKd3B8g7o5F2pRX3Jdx8Tf8r8vuVtyouCUZ5FJO7v/l4tnvP/bkxI6JnQXn53fNvx6oCZve65/QYt7v4394TeuatnUtPFQ+q7yZ'
        b'Xw/o9ZmmcZ3W7+TbXvDASfzI0VV7igPO1O2u0wTE9LjE6B/h9frEalxjcUhvt1a39rIHbmEj3pQ/cAsdftPJbf/c3XM1fnE9TnHaIDhDMz0e4an2sQ+cgvs9gljn0Em9'
        b'HlEax6g3vxn4wClo2M3fOfv0R0+4NvnS5Hu8Dy2gxaPoaYN8jm8CUmJx6IxBijMmkTZQOAWMLw9rQ4VHIeAOtyUQUFoHmYzOiQMym2gx97Xq5j/WU9++jdRN8euqm1ob'
        b'GizKKM5i23WXIR6YB3hFOenSAauiGYV5ecnSGenJ+UxcGJ1n5gGrmpKKKtbrhuIQ3jSw1HuWYDYVMHaT+CtRHMQH4p8EGntwJg6d8dI90bDJJ4vd/z/YncaD8o/sRyty'
        b'8I6DkePeo9gzymwmEMygDeXh3Z7fzb0efa+0xyGjHm93uXi2x3bzrxd+FNjv7DHs9GsznodNfeZza64w9DvLqcJS+imFj19P55CQJuJvuLRHaH3mExyoRNzvOBVHM5nO'
        b'RDNx93tkF97vmIiS3JPo+gx9zJgYHNJlPInowkZBScbPpdKGAVxwTBWnRCbmCRs9BYdi8ZhEoqewoVJwSBfXafVp35rbCmO+FlFuvj2uER2Tjk5GP/Xpz3m0MBK7xPbE'
        b'h7hBcyqBnkF/x62lhV7fUfrj1+T4VMGlbJxa/R8Kvb/leAjRp1E2PoP47GkcvlHwUOj3jDNZmEjjO/5fk1PGrzYepeWwwXqIc1+ack/l2cDbFfACvG4kx2v973+zCbvT'
        b'dsRWVXqH2vO42Jk240j7II91pc2cY4faFugvPseOtbFbbSZdf24nGyOzlzmQc0eZk+7cWeaCzl3JuZvMXeYh8zxoNY8n59cLymiZ1yadMQ12wM26iqZlVuhojZ1Go//2'
        b'2v9nvE+bMXkt0F9ZELt1xJX5GDiSNuNQcj7rRttP5zDbXF82+o9L55Rx2HId2F87/FuhT7dnacC/Fui/ZRlP5n8mwIiGYOxWHFNRb1EvrLevdywzlwUaUGNBXGsLiP/c'
        b'MWUC4n7bsp5aRc+zIj4zxAP2uN/MIHG6iTv2MrnixTgjdWx4Biaqp1GmFxKk28VVKKvjlCoZ+R0XGTluXBxWEeNWKWVxeJSSREZGof9I+YwWcwd40py87AFeWnpq2gCv'
        b'MC81t4se4CQlo6MFfmVRjjRrbhdPgWWOAT5ZkhmwYEK2V6BTflllSbnydV4bhV/LU5Dg6mJ8COHiATZdms9E0HjNsiaJ+UPKUsSQAvOTZiW8SFyiUtXERUTU1tZKlBWr'
        b'wrGyrMB+Y8JLWZ8VktLq5REyecQQCiVIpY4cJ0HvE3P05XdxiA9wRTlxFzNgkZUzIyGrCOnQL8ZiomckphMK0W9uSR0eAfPw3pFShQqVRMagI5plcGFdtKKQiViCI54P'
        b'WOenS1OzkosSEwpmpL1iUVFiLkOX7pNfTBjy4AxFtVKZSJR74zKyqsuzleWkpChcEkdfEiJwCi7Ldgg/XriP/FEvnEwyT2xlVApuboppJsqepMBhnocWMokUEq2Yju+N'
        b'/PKoF6Gv8aUDZjJ5WYm6UkXYT+ry/5G96TATQIoy4UGCaCzv0NOwGQSFhnjGDAIpFGcr7tc94hOz4GetKW2fTDx7B5sFX+JTlnc4sfuUI5gFD5gXKarVKtTsmXg4xuOJ'
        b'RHvTyEJ4tZhy9XpNw08czPmlb4jnG5h/1opHYf7ZZcYIVW0mJKtDWvHKyEbUUsthJrrYCDaiNLEIxe7OiaPzMkud/af1T2b/iXcVNpqZ2FVIZzzlVKyWG+wtlBIWMhvc'
        b'eNR/yV5CvrqmplqBlylrSHRkIo0q44ZnDBcN6Zmi4KRk8cuz4Z79ozkmiYJDlBV4t3zlBMn4kFcokhksRMEz0n48Mzso4Mxhoh97z8gDlig4veC1noh6yROvOvbgIoYS'
        b'PdK2Dbv0zKzRMk6MZPLFqmqFLrDrSE/iCZp5bGizqVFUVCsqVHVMrKTgEDzthyCC8MQfYnolPwSLAzgPnpxD8LZNCJ5VQ8QSPaBjvGScJDKOzWK6GD32I5JkZUvVJ48n'
        b'yUzRI30Y406O/TQTLuEY/gQpiVe4EdlDNijjjL1gkU5m2m0b68VqRJr0vtgYwpj+OtSpGnZbpoP/mED34D/onhpvF+KdNLKDQaBH8hIVblDoo+qG+r3D4JcRXGnhXRBU'
        b'Tm2JgkUqGQQGJtwR5cvl+FvVlXJRiQoJcovVKtNkzUgoSE7NyZtblFuYl5uTn1yEI7HnEyp1KCHi1ssE1IhlEjMIMfzJTUiXat05autNq8uz+zemQTX6PR2yT8iUoN9y'
        b'CRkypoSMCEsiNVTD9FMlYeKQZyeFMF+nzVJRZdrPF+OTDonAzDYQBiJViZIL80bYm6oS5ddWqFbLFZWk4lQvIZ4ZEEfoS6jDpKtKKuvIgyOPcCEjt1nWmR5TIXofe7jl'
        b's1Wi87fHbBOP8EUqBmVlEEzN6FkjT40jjlqkpGH7dog9rJym1DbfIeWarhOilRj2lPTEBKlosbyyuqocl/Qj+1sWw0QwOxY6dccXnIfNmXAnbAoq41IceJQOjgsk4lmx'
        b'iGbjY2TAqwRVBY8Cxi0L2QJySQdXlEImLIhiPAXPBoG7xFpyHuiADVhnB/tAPdgOr6G/l0ADjxLCTRzYCFvBJibmwylwFjZi0yK4oYA1r6coe3iEC7ZXwM1qLEUtyUzI'
        b'f0lIDca3AwX3YScMO+A1SwtbcELMYXbcmszBZWazZkUVTeG9mnXwMiEdXB4jwvs74EIqReENngi4SY1jUpSA3WCrQQgVvd2/zg65RijMwxFUlPBGcLi0MDgYboPbI+C2'
        b'MBz8gokMEi5APNnvQMfDxhSyCWUPdsP1ypVsFA+wCRsC7UI8eZ+JDrHAjOLNRPlExZUrJjhS6slYON7HlxvG90iTZGTDBvTZEXmwPmstPDQzjZsHGrCbAngDHK8LpMBd'
        b'nhVs8QDvVHww8yBP+SmWziJfLG/KtgSRdpvLlw7ENDgl7T5ituIv6V/wNl1fltnxoOqLHY/zFjjmaDIP5L3gfly5p/Vv7z+J8vn7Zs4HR9b/tu3z/buPtCRuS7P72/fT'
        b'x6S5C6Tvb0qxD4yJ37WgatPk3g2L1PcHqzUvjqXCv5av//MR6J75kTR53O6P/rZkptI+/Ic5W+FvG46pKn/Ttnl+0+r+g5dObFl7NPDj0MMx61x2HfrdfPuyrz7u/CDc'
        b'bda3VWV/61m/yOcfn3suKGs+/ut9NwMurJrd+LOPD17ZaPmzv9gebY+4+qv/FguZ/ZoDs+ClUEl4WjgH3IKHKAE4xokEV8AVBkF1FTSAO0zcJBwAKgwjxswomzz4HrzB'
        b'jQL705hC7sB3l+lM9PAuS9wyzspiVAgGao2hkg1Ra6jCLjOwNbgFbiVbFEVgPbzDwtYWeNEJ2EyLidt0DN4WZOpaDbaUK4Vt3EpE0Tuk7Dh4QMIaEBaDLkMMGDhYxRTR'
        b'Bm7kG3rYx9sqQXAPN2n59GeBKIOwEjQPc9XP+OmHbeAUD7Wrw4wxFtwTv4iJqZAPT0oMQioUMb7ywUawE3cuvPclzdeGfFgN95G71eAMhu+R7nt5ObiI7mfTKWPABcIC'
        b'K9AcgYaNLMSCxXBzLh0FTvmJrd9oKRav3hkivw38U5vUuAxdwXOYjZVnslBqjLPGObgzoMdu4nWXewEfCTS5hf2Tku6VfbTkGZceMwdbqrh7H/Zo9WgS9Lv5tI/XuImb'
        b'+Hh7xITVkIOL3mrBxa+9ssdl3G+8g/snTrkrvCW8v3KQS4fkEExbLsG05dKPXTw0qAyXCGwkQ9EhBP72NcqWSrKlkWxp9BMPUX9weAvvoLA/LKqF99BV/MTBtSWlzzO8'
        b'xzO8U/7QM+Yx3onx3L9g94J2v/YojVNgp+N5ty63Hqdx1yfcnXxzsqFH+0EuNSWV1jiNM1BmhQaY/5dqkiNj43AwSyNE/itWSDZWgadQLPx+dgh2Ff78dR2GE6eY7YJI'
        b'qttq8ugchrN+sPlFWC0YyWmvqe/Quu7dgb5DgXGPjOteySvoHkMdeONVyPy0hLwBXlJyYsEAb0ZecpLYzJQlhuJbbQDMAbPSJSWKcrnSSMe31X51PTrsMx/RDxT2AmVW'
        b'b4N0fKzt2xJ/T3b1Y8ps/w3enrC232lK20+QyZAIaohc10o7JtZ6dXLy8EWDMlEcluLjinUOEItNAJ7CWKlT59oXQ+eHWxqgtxsSVIqk2sVIe6hWq/S6hAozXsVqWq+k'
        b'w7LaB9MuXkGNLVmuf9aQHCZdVKIUlVVWl+CVJKSHVKCUKvXyxXLTIj9+XZVu1QQLkFpkZQIpzRRIiqHCSLczJEOr2ankqxjFBXOFcW+8nIH9j4DjR3kqZFjq1rNCISeG'
        b'HIgy5htEwYhQBfk0IlX75aVIJBI/8Qj6AIMZIzYpJbg1KVUKdalKjUrXlywRpWghlwb3TZane4a0THVNpVzbBFg8K1JA8MciHWk5YqXJMoLzklOS8TZpcpG0MDsxOS9M'
        b'pFUfC5LnFIhH5LecGKFgZsurZOGq6nD0Y8Cf4OoaxijnJSWsMqWRo1S5AhvzGGrkLy0O/9Ep7JjDL9Onde6m2VZtsrQl1ZUyNGqaVL1FiCvJedKErOFqtmm7lVdUvWX/'
        b'h733gIvqSh/+78zQu9L70Bl6VZpSpA+9ilhAqUoRhmLHLqggqEhRBEQEFKVKUVE8J4maojNMEjAxiSbZZNOMEaMxm6zvOecOCEZTfruf/b3/979md5g5995TntOfe57v'
        b'U5i6Atuw0KJAv9j4F2mwonaD+0VBajpqF6iBJCWF5ebgkeJ3DHrWFTxPHUeGY0E7LWxEgweI6aablp+bjUSVkvwKy5usQlrDmZ5ZlJoz1fJR10zBZx/NV+Xm8DKRuHBM'
        b'SHCZJBRJ+ZUZo6OZqRfizCwmndXclatTVxXQ48HLd6LR4S7z7OxJ40aVQ8qD82AlcuAgKi9R1OC+iQbFl8aTVphP+hrp7cSY6NXbcXoSc2NHi7a/PHZxRibaUWPbpPUo'
        b'laws1PmS8+lNMH3zy8cWHi93VSaphOnN+Nr8XNSRyYl0JFpRZaOOQDf7lwvz+Shnww5D2/LktWuzMleRU9lYL0L600xbq5f3nUX0mJEsGhRR6nh+Z5ujT44VG8/ybPPw'
        b'2CgOrgw827PNffzCXtEPLWYYj83jWPwJk7bpI67e00P9C36uf+/o/B/oBPTDaC7UWXBq3ZRnTNADt5Kt/1FYShaWZMd6RF8Cv2u36zVMClHzlhS5Ci1lWPDkYS+4Mu0q'
        b'VEXRn+y3l1OgexPcj8mEouOiGXrkGb1i2SU2BGYoIhnCDrgrhrz4zwY1zkSJMEOBoAcO0zoEcHQdcf7rBbo14T6R60ns0zTGnDYP4lpbxEm6BloFx/6O3oCQDrv85qBN'
        b'TvUicpQU7toCdk4f8DwMu7DWAPTbFsZjwXSCBrypfEVygeBQykvTe+5+ONJ8GtrGkaDc7FRgt64jOfCp7beYPnAK2vyxQgJWbipcj8IDYTOo5hKSpXVwONZJ0FGIw4Nw'
        b'l4yJJuiQea4E8ILb4DF04cRcsAucjAFNKZGgzGcLqEcbvTPovxb0d/casBeMrAOV4JTPyuVgr09+ZmTk6uX5JktB3ZoMJQpWLNABxwIliQpFDp6MloUDa+WYFGhSZcJL'
        b'DFtYySmMwcI4Aio9X5kxWKYJyrxA1Uqwa1aOdsET8DD+js/EJinCPWzKF54DnZFzNGAzfc5XMwxUiI7k2uEjuSGwpTAZhevDIWVuSH6RSDfDiRPhKtcWFsbAyrXyivBg'
        b'jEjgM9Q2WFuDW8EU2m6K6wi2gXYpkooCLFWDZxNgf6EnhTe9FxKngKLF8PhLmaL4uZhZNQnPgz3yAZnwIo3n22sCrnCJA2oR/r4cdEaQ5gKGnFDEXELaQ83okDgvGOyd'
        b'ixr3XngoCuwDexnwSp58AKwFhwpDUVQLQbfHb2KCndGBzzf+cbMiBLtkwWEVE3hKFbSBVjVVFgXqQueAVnAZHifYftegzCkM6IwyMWEzPAz3R8EG2O+Bqmc73ImEewwe'
        b'BpfAwZUU3BMlFwUHwBWiJIMX4Q5wYYaWLCSIE2xtE5cE6l7il3UqZ/KzuwsSWkPhXFAFLoCRwgQstX4wAC9P0dMiA5+7QK4BDVNJ/JX4o4JVwCU9lAoeaPzENHhF4JTV'
        b'c0e68KQlORdHaLMJoCvouZ9hOzQgdMzwNAx3WHGYYTGZEz9/KcZ7D20hU+a8VR7zVhi0U+pvSD968qujY0dklCQr775drn/3umRMoJpPR4z3ktMyrpJDw3MDXgv43Oz2'
        b'UGFg9z+um3x389tvO0eOfv9Acs5rR+98mRNcuS7NunRIKTMgcLPxmup7vq8bccsjQ8re5ip9frveI/7QnnZBgPQXHysc3rr8Rzt9ubZ1n4G7l8+5r1b3cviszGptVoSl'
        b'fVvo7o4Fw77mRZrNFT+lRqgr7Uv2731WJn2fGcv56FKNi4L9B3Gh5ov7AZ/5+ua0dzZM2gWc4Scse2fDHuGhzZtW3nVyfvP4gw0ye5d7C2w/39Wnvnyf24cNXeCrdfs2'
        b'sN8N/2fHuMzXDHmzwdFhy7s/jpzT9nmyPSEvcjDh+uSJc/Xx+QKL2MgbDysif5FaF/66Z05ta4BvQMsm09WjX5/prLXr+7x9Wf5JQev7iUX/OLU8PMb668J/ProrcSQi'
        b'2+CU/Wcjemt9Phpbr+Cs+5OS/neRrhaFrR9mNOQXyxavOL+8oz7N8oSjs/+B1LisB+yetp2PlTdusclbfu+7ro3rNj44v+YHt9wHlbc7+vyV90i+rTmY//heoeT6j9bU'
        b'/m3tl2ryd9d8eO+jvwenXg89vPqu6Sfxv3byDd4+fyh0zMXcrtBxMA2cPLBZc9VN1mmPZ8zkllr+3zM4auSEtjQ8Bau4NnLw9EwtHitrfRjth/NwLmqptHrQeP0UVQwr'
        b'B5vhEdpN6XlYAXq44eBUmMi/ahrcRasdOwyXkW4DhzZNYxzhuWwufSj6TDia/UQH0ZlwJ62Nyyki4LFo2K9PHLrGwdoX/LnC0+AC0Rwu3YSGJAIHs4G7pvhgTNiKXdvT'
        b'FqhXFEKm6WXg9OoZysdKR5JDb9gKtz1XjILBCHICPWMFyeFqeAaUig62LwAH6JPtHvAMOYLtlrsR+94IAp1iGD88IJHFNIQV3kRZCOvAGX0u3LskWuSBFQzPJRpKRjSm'
        b'SsEDcsYztZ0s3/lwgOg6ubmQ6DrR5NX6En2nGOyTADWk2mC1giONgAI9ylMUKJaqHhykD4jvQLJtRTdYgQ4xSkxVzIoBLhgUEbF4xcEuketZeCAOXJhWk6IJv0/09Hxw'
        b'kVY6o5FjNdE5w21Gj0zxtWPrwFZuiAPcEQTKXjBOZlF2YEjCdiNooa2Om2E59l2KplqCiw1H6w8FX9aCUHiZ1tdWgZ2gc8q7LDwB2ondMWwDJ4j8C8GuSLDPNtSag7JR'
        b'Aw5ILGCyUbMb4aj/b5ycxYKZWlm+GtRh+BIF28sATvhAMHarkGaNfXmatpu+q25/W9eoyb/dtyu0IxQzkPzvvlxJyzZuk2uWG2fbC9j2BNDEdq6UnzAwn+HEslLhrrH5'
        b'uLGTwNhp3NhFYOwypCs0DuArGUwoa9Z4Vnm2O/MdFvEtfAXKvncNzaq4E6qGTSljqhbtW0ZVxmz97hqaVnEfSFDG9t1hAiOfSi7mE9nW2Qq1LMe0ArslBhV7FEedBXaB'
        b'lZIP2FNuMHuK72gZP6AYpvOwvlh2WPYHFsPUl/jM9CM+M/0YNBfHtcq1SWJM2fS2tqFIa+xNlMU+RFnsw7inbSTyWdniUSd1d8Z59udPxJEn4skT8Yy76nrouogFNUW3'
        b'mvmcup7oOT/ynD95zp+BWTzu9e40QkqoF8nXiJxSgcfyrRbwjRcKlBeiTGvo1Gyu2sxXt+uOp3FHY86hd9nW3SpjbOch43E37pgbVxCRSPhHsULDOL5OHPZWip5pFxeo'
        b'W3dbjqqMe0cJvKPGHKJIYiI01j11veaN3ZuvK4zNj5uYkZcQoV4oXyN0QscII326JQfleuVEBfAhBVhECrCIcVeH3RhSFzKuYzemY9cdM7i0Z+m4s/+Ys/9L734gg8Xv'
        b'XuU+rswRKHPaTd5VtpvQN60KvKtvUBn4uaoWX9u6vUCg6jsafz2NH7eMv2LVhF8EP2oJf2nKJIuhlsaoZCJp6JtWMg/LYkFNR8W3cH9X2eO2gTlqvUEdQUNqY1aet/UN'
        b'm5zoWhTq21X6HA4kYCXsmLVdTqDsNGHuiJ2bmkyIJB4iQLkxtqz0PRx6V12zUnqGcn/uK4E+z9XI+Sm/tTz4M90a27/9lsPz13p0pfhMx6HLrBiMKALdiWI8JJ9/5T0A'
        b'3qe2SjhT52W9qdkvAiSmdrAZ6KNagpxppE8jS5ZKlVJpEtOnG8X/bacbd3KYPyf9ZmMdlZqTkprP+yMNN1GnibbwWIGTzGMvDg35g326HvXiPp0TRuj1aDbpBOe5z8/F'
        b'R77IJ98Xb/4bWAY8Bs6iTbqzqj+oJ0tfI7gVHp259t2JluTnpte+sub0QYFh0OxAv8FeHCBaQFeDg4X4petm39X4SoENWk/YFKGP4CDYhZZPTMp4ufh80ATK6Ch2gmo0'
        b'8R3CXgRAjzpDjwKVJrC+kJ69QR+sIwcRQJ0jrBSdRFgAe4i+YT12LkLdnSNBJcn5BrJpRwh24mAYOyXQAVvtUD3B4xS4AvtKyCbSFXaJY6tVW3CC+BI4AruIIsI/kScr'
        b'nc+ixOEJBuyg4NkAuIfsdJcmgXpLjgXcDesxX3I9A22lq62ITkAO9IFtXAywrlfihIlTEmpMOVgFj9C+GyTsomE92A3LxfDKjwIH1tDGwKuQWMswUBxUuhGmOOaJg6EN'
        b'JDVvUAf2o/0+3L5JkT6AgKplFymVjvN6Yq6ahwoziBoosY/tzyJxFmHwO7ZzBQNLsakrsXPdD08Sm1VbeKpYtkheNWatGIXSs1i+gcS3CJ5xJwoNeA6eUqCPQcBuNqFL'
        b'++coRINytMnrco+F5bA6NpRBSYUzYD/c5k/k/tXmCkqHMTpPxi5J4Y35EbTyZ1uWIeVLBWpKUknMQY0NdKBGOCb+D/lIJyVZ/GipRgfO3yRHaVCB86UjkqxS2CvpwMGF'
        b'6pQV9RNDjJ2k46UVTBXiBm5cFI42wXv0fwNpZ4WD3WtoK98rcDu8jLURsM5YjkkRbQQPXqHbViNswy458uAO2CbPolgqDHcleIQk6JmLvWj8fY40Oykk2rkEOyEjy/Sj'
        b'sM4L1YGZwVQVdINT5MpmWJ0vWyQNdjjzkCilGbaoLfSQK4qG4BLsk0VrOHASjcQsU8aCjGAOg7QEfXiRwQvDu4U4sI0py2CDemXSFv0oV9kiOKChoMjEsbmATjU6A5fN'
        b'M2WdYQdqjqhpYDvyXbCdPhi9M2QN7JODA5JU2CYGPIQuI/EQa2x4ebOcLGolYDcVSUWGwjbyAFteXdbcwhL2gBbPEFSHwcwlgXA30ea5oK7VC/tsg63AMTiILoqDHQx4'
        b'JHh5Zp3lpBjPD43UlmZuIwn/WKMTq3K5+PFI39HNn5+/vVg5WznRz7s/dF+peKKFYX+Et4pRoL/F/Ll50ave1Tz86Y7Ad0uP7C1tYq9s2a4yR7XK0ELmROndTwx/2pF+'
        b'/yb69/S+m/D9b20defefXp786NqdjTe/vf2La3JZeVn5+wMqPw+ublS4v3Ntyq0N/jn9h00mwv829E7PBvPwk16pPjH1i28rpQ7nLytKa+WkMZp4C5wMHKOG4vzWaZod'
        b'0Hx/Z03rEcNcg4Id/IQLcQW/ODwx+OJY9IOHTh+0hNnHLGv60t4nxsXwEedCL6/B5M6J5nRnfl+U4ncqp04sNRn8vDr+8ZDfe3fNeyuYunkLXhOk/vim9lmjlW8t9/B6'
        b'MrDmTJ7jB2eG1g8+DKm+/7DNDJYO1Acr9Xytduf0G2p3eut3v1ns/Y1c9wer1V47bJA2P7fwzarHrh+HOTreOtuvZ8XR2bjs3M/jwdcNLLd8WPvo9uNtGbFaHZt8o999'
        b'JnHX06dF+cdbkb4lfjL6g6uXHvomn1u0M22kalAico3WZuXSJYnL+ZuPjcvNh5HeQz8//Hht1tdXJ5wk+hX33X79/rh9LuP0vtUlK03Olx5c0nTydvTYRa3uFkZRnGVC'
        b'4OnXNMsnJT/bFPHkKTsg4sMf3d7I5myQXfdp3mCfwbXvtiYUXIPv7Pzhe2r5gNvbZ78Oy+G98ekPZSVLlquxMt1knFTfs89ptR+WfW346IeGkxVKT9Ye3XIg7ZGGruSG'
        b'XzQ9rEI3mSmtSO9Kc7/x4cE+F6CZ++Ta6qG9G/e0D9n2yIz6WJiutLjQ+cQsbTPVGzbQ8k2Svb127ZXLbr+a6tlVjC26U+R7aWFvSsNc7vufijWEG538W/L9v1XI3XxD'
        b'+/00S65Gbor79dUDZ7ttudSKmANe33BynDNKDn8o5y7oP96Yev2XCaUjWxT19ixppOI80xP5P8QZfBHUbpj87NgRx/fSRk5u/tLkM7muvMQvdy4/z1vyN2HZj9Sp0u0t'
        b'9d/dtrw64LAoRC/32po3Mvt47Msy+Vdv2l50l/jBQ7JQwT1ysrdk++Kr0u6ht7YoHJI93vX1F6YFTI/c+x8NLPjp2/eWHs2/eefTTwpWPFmjPnjuZu0PN21WRLZVjOid'
        b'dP7G+dIXwbDZ8rF0/kenEh1Tjtv6fPMW/wKjs/DHvQmeyct31Y4POV9P+oB18buFX23MNfj+bmiJ8kOWr4tZnVSJsDFyJDfmnfOK57dkv+lY7HTx0i/Hfvjaec7765sW'
        b'lLqweq83vP3dBsfPr8Bru1OO7Nl/+1n1+LuNO/oqn+p0v//eh3dOfxz0rfTNM+FpG81UP/nB8Ev9iUnzNy7e0ep9972Nl5yP3XvC0H87xl5R+/ULST/+vHVjM2+7SkH/'
        b'dsVmZoFFAK/ks+Gapd6f3znq2LDxq9ujF36WelD/hoafdpS8hlLNUnmNn6LiWDcS1jonjbZ1ShzsO9khIddZs1jeuNFzubxGt3u0/Ca5B5zTjB2Pxd4bLen8ZfKOf0vh'
        b'mePvhDdf+Px7g7sSpxfukLlw8bsvIxguF+0UJxJtqKwdn460fraZ8dlm6bMrvL+ZH6TqPm5XKP9T9i8fXB//bnfcU+sHH8h/Pfj91iMSk2t2X1LfVuJ4X3/TIavT3+/Z'
        b'8ORc9dX0INdnX3gm9KTm6r0pM9i5hdrMUfpH+NaR9i1fxL25ZMu996/vf/ZmYsfHGgdKGuZtge8objrkvHnY+rVLW3b8/OyW7ZL2/FMXOr77x7ObHxb88x8tz0r2fKxv'
        b'Gwy3qPyyiqEx9vWDb2zTw427GmV7v33qVN11c5fZ/upn+nf8I9/+Z0l+4jP34MH7wcqZ17Xry64E/fCL86aKBr2xFV2HcjqeKQyb/KjO110aPqZp/KPro5jPzz0CV0La'
        b'wu6Hb+TQRuU8GYbIq6j/HOJXdKZXUVDtQ7QsflGgSqRkSdSZtvI/BDtpDdMJ6axpdYQVqEmcVkccggO07f1wyVouVk2Ve3CmjnUp2rHS0UxO35CJZvM95IzYOrhvlmLF'
        b'kCLn5NLBceepM2SSOb/VqjDmkHgkVqEpZR/Nyra2CQxJW4zWP2ohYvL6sELEul8NTlvaoLVmc8pzcPwieJwAtXPgcbCfhx2yHgNnpo035eEVlhfYakUreOAVWMqzsaEU'
        b'YJl1fhhHGi1Y+8jJPVjGopzgGYnofGuaRlC7FpzEGh5H0E7ikVjBtPCGOwhc21odnOaGWGAXwsxljPngQCqdvXLfGFQVaGkEhtCyGGfvANMEDGXRCrfLRaCahm8HwlYu'
        b'g4Zv+znQupi62GhZWGoNe+B+tNI+wGVRkrCfGR4Gm0X0AGNQjm8AreA8vgmtzNDsKg9K0cIEtDJpJkPrRnzE1SY4XgwjzbErEtDvTuuChuAI6KBTsIbbtIJQ8jLMeFQV'
        b'NMYOlMFWLZ5FEKxYS2gRB0CDeJgkpQS6WQVoldpO66Uq3VK5wVYUOI7uo9CqdoTJAvvWkLJ7GCyGfVzYGy4LOswlKGk4yCzIAq0LV5HkY2Lgbh52BiCN6kWckoEVTIUE'
        b'uA+eBVtpwv1uWFaCc8eBLdIc2I3Kx8JoPZYy6EeJ4/VLCqxPwMpARfNA4qCFAXdEz6UfPgG6fXA1WtpwZMwtQH0SVrrN1WDBrRjYgHNnCPbMk7XhwgFOBDwP96HCKzAT'
        b'wTnQRJANS0AzqOWlzw1j0Eujdl4y0YIGwl0lsA+VFQscRQ7OuMG94tQcNRaoCwAttIuGAbTNOMaNWBBmBcpspx3LaIPtYuCUsg9d81sXwu08myBfB9Alh26hKAUJlqeq'
        b'Pp37brhHRpadGmwdkgfOBqJuweMwKM0YsQBQj6SD8ycOjhbzdEArB+fvMtocWbmTUsVErOdyQpU4tP8icdTlDrM8wIhIpimwEmsROWAr6KAB+VNwfFADT5EGYwpOFfGC'
        b'LOzBIActFsFhBijfAPfQTikuwcH5sM/KAO4TpxiyFLhUAGtJXYbGwJrZroFglSRa7h8GR0lprbXQih6T8+E2UIp3N8TRzzF3ojcFl1LwC8aZ7HwWOKenyvQjcWfAo/Nk'
        b'zZEM8kJQjmRgPXMLuIj+q4cj9BHSbfBAMQb+h6JW32PNoKTtmaAWVrjSfbYbVHjI2qB9VQ84noYzLpXJzPSNoMe5ygjQbIlqB8VxxCaI+NShFEE5a6UX2EFXU60ZCyUO'
        b'euzzwvDCtY0BG9FGtJ1cjM3VluWgjrFDCbU0FLM4rGXA8xFedLb2wGqIvRdZwSpQQVS+WOGrpi1yFwCOgzbU/JlGuMQsWMYALaANHKDdURQXcOnXTRKUbDBTfSFsK2LS'
        b'+vNGuDeAF8KBvbjyuKjbyDHRrvUSaLKf0vA3GsB+VIEanpz8EMx6krdlSaF1/UFSu5uNwWXYl0xOzVJwiELt/ZgIOOkItoMLaNeTDxq9YT/a/oLLDG04sJiWwx7NXPxi'
        b'AN1xmbgFIW8GDJg0hGYn2KFAbzz0QC/eeHDzSM0WgF35XBtr0BM66z3GArCdFtFlcNwNZRVl1JZByXgxwSAcBB2pUYQxKYk2tZ087N2C7seowH2gLgtlXAUNzLBGHcWC'
        b'h6kQBdjLy0WbyAqODDhnBQfwKN+LbtNUErOAXXPIMOUPLpmhaMpDkxLINfE4BtyrqkJjYrqQ6HuIsxUKNsEB/HbAGVYReW0CZw3xy0q4jVUE+1AdzmEs9zYmIvFHKdXw'
        b'iOMxLTDCAMcpNELWwKOkaHnwNDyB9jywzM7ZHPUjeBzdADpRk6VVGfCALA9WmAcXuzhYMClJcIjpmlhCJjwnm3n40H04qpm9WI9SRl4XKDJZKYylJEvqXhkznVWxwBE1'
        b'xYJVZOAppFbzUAkukkkMDbqiQVMDnBGz3wiGSJ1k2MEjZMxvSIU9ZDN2FLVp1IrP0RN7p226aNwkgpKB55mwVRJc9gDNtLRa4WHUevcRn1fe8DgzjmHtjtoeOfteDbev'
        b'46GaloZlxdhXS08AOIVuU4aHWGh/jKZout4bwF7QxrUORmU8hGcl7AYL7IbVpDXJyRjhNwwp8/A7Bvx+wRJcIr3CGhyGjbKF8uBwsTQSqQHDWxb2k8EwZakrD+5HXR9c'
        b'MGOqMIy8QC89jrahRtNBigOGwFGboDxylzzsYJkYbaYn2TZwsXjKNZjKajR40Z7BwKDpIzOsQADdsImmoV5ZYAv3hlpxgkLRqM6lvdu4eEiAE4moWslAdsgU9JAXc6vh'
        b'iRkvVwqsiWcUX8qFuKl5hW8uMhbHwnNSgUm2oEWa5M5pcbEsuc06L8gCntHlYEcs/SzQ4r+QSJJtvgqlF2JmPz30KkSzQuFJH1JVqVaglBfGEXUvP6ZMFDi9HvQTYWqy'
        b'UecK44Ad+mSYP8IAFb6rRAOXjS66Ag8ETg0gzixpWA+PEHmAWjBo+wo/JmiTj32ZoBGyhrSl5HBYO5X9MI51Ccn9AAuchEfzRSuYhE10WwbH5J+7NaNdms0HJ+jOcmgF'
        b'qJc1R62lHM2SLDjIAO3gUBbJazHYaSsL95Ilkj7qwyxKimJGssBp+sn+nM1o6AdHYH8wAz3Zj/vgNh3SVWB3OKjEwpFB8wZqIKAtFz2tAnayYGkiOEXPd/Vm8rLgItzB'
        b'oSiGFgV3oeo7Tk8cR4zAbl4Y7LFFiwuOSR4ew5VWs1Cz3gqOkNEhTQ7WoqnSBrSb2+D+X4cnvGHUT7AKJcQLnpDFUN0UdyaHoVe0+BFWg8rDraCBF+6KRn5YJi0qFe6+'
        b'sFLMDewHnaT7o6bZUyJrbYOmrB0cVCwJPaayzBrabqMSLUvaiCvUMGtwIMICN+bzTFT++ih6bjjrB9t4thawOxAeAT0cPPJcYgaaJZGrPLUM2GcdBlrhKVpNs5kBq8FZ'
        b'UEX3pbI0tPqf4ZsmyAXdQ1zTFIAOekHZFgIP82yCCzmo/6OpickELWgQP+wAT9BSO7k5gF5agwZ9qyBFczyyycNhlits0aRHn0vwMjggsvjYBQ7ieQibfKDFWDnp6bqw'
        b'2YhrEypBoRmtkrme4bHMnkjUN8WbNgUJYzFXMuxD19Kde6sEPGqJp54gsEP2ObCsGYlO838X+kN672//zfRBI5FPdPobNF/ytoO+RF5brpWlX1tusiPe4A+vv6NlyjcL'
        b'Fmpx+SpczMHSrtMe17QVaNry7byFmj6VEhNqWjVrqtaMq1kJ1KzaY4VqjpWsCQ2dRtk62XENG4GGDd/WU6jhVSk+oaE9phHUJNYm2yw7znYSsJ26Y4VsdxQ26jcqja/r'
        b'NRm3WTZb8jWs0S/6/dqYenB76phN0JDYuEuQwCWIzwmuFLurz66Uu61v2lR0tAR9UWE3qbTpN+sLVewrGfeU1W5radf6NnLruCLzk1VCHYdue4GOs1BrXuWiCbZRVdBd'
        b'Le1GizqLCQ3NcQ0LgYaFUMNqksXUVqtc9ECCMjBu8m6WqAz6XM+w0n/CiNPm0ezRsrAyZAIlFCJQsasMuWOE0sbOR1q2CI3mzbwyoWs6rmst0LVuT+7K6MhACTTK1Mk0'
        b'zWtzb3YXatji31J1Uk2qRxXxVySjJt+24ObgMWPX7nljxr5D8UINvwkd/VrJMQ2fJu+2oOag9pTupQIbb6GxjyjcVxSe1r1JYLNIaOx7V1N3TNOrKa5JC/3B3ku8BLZe'
        b'k5SCptZo8rXVV1dPGBjXxo/petAWN91pAo7HQ4qpqzdqgDnWE2zjNulm6fY4AdtxjL1wSGKMHThqiqSxiKGHhKFnOKbr0hTTltCc0G0qMHEhTw4lX8kYzphgG7SJNYvN'
        b'uDhmsmgobswkdLRIyA5DUXjqPVBCMTQm1CW0mwp07cZ0wruTB9f0rEFJG181Hi2CVsJ54ahGagPGdFa0i42buwjMXdDXocgrS4aXXGfcErshdj1mPHSZIHSZMHC5cMGK'
        b'SW2FAIbWAz1KU6tRvk6+qehESbfqQ4phxmVM5ScOezAaN1kgMFkwtFpoEiRkBz9kMc18GXf1TbBfm3H9+QL9+UMyQv1Fk+IsTa0HUjgyiTqJCR3dRt86X9SadJp1xg0c'
        b'BAYOQh3Hiel3sAIdu0lKUlevO3IwoSdhgm06xk5td+ry6PAYt1wosFyIfo7aX3O56nLd91bIjZDxkBWCkBX8pFX85FX8kBThotS7+JGMqUe8BJZe6Odo5LX4q/HXY24t'
        b'vbF0PHSlIHQlf1UaPyWNH5ou9MsgqQS323fN75jf7TTo0eMx7ugrcPQdjR5dyXcMEloG42JLNEs0FeAGOW7mLjBzF7I9JowtmmTG2Gn8yNjxyGWCyGXjkaljkalC2zRB'
        b'ZOp1lW7GoHSP9JDxEG+UOcR5z86XH5kqsE2blJecpzcpLoeEooWFgtquSCgvpOIiMHMRsl1RHevqkS6Da9CjndEl3iHentKV3ZEtNPeYlBZHEcnhiKTrpHFESI6otsfY'
        b'8ehO+Q551BjSe9KHUq5kDWeNLwwXLAznR0Tyo2L4C2OF8+KE5vGotRksZ9y1tKUl5j5m6f6ARVnYjXFCu70HA3oChnyvhAyHjHuECDxChE6hY5wMfmTUeGScIDKOH584'
        b'Hr9KEL9qPD5dEJ/+bmTGhLfPNbWraqJmhRpUotB76aSkmK7eJEsC5VSJ0tKr125SfkihVtFu0GXeYT6ha/C89er6d6f15o6Kj+lEXfdHbU7XF7U54xOK7WpjbJ/ueYOe'
        b'PZ6oQVlqTa5huNqqTVKueuqV/o+KGJS+SS0TexjKJ2h4z/bkMW3biXkug6t7Vgt0HGvDOgLuWtvXhk2Ymretbl7dPac5uzYAO1XCDTy5Lbs5G8suoC4AVwLuq4Zdph2m'
        b'QrY9/i3XLNce1RXfET9m7TckL2T7kxYT2O7Q5dLhgr4MMa5IDEsM5V9ZN7xO6BJIiovqRM94TDe43bddCv0ZUhl3DRa4BvOdgx9SUrp6qBLGI5YIIpZMGJi0aTZrtqcJ'
        b'DJxwVRgOGVyxHLbELsXQCNStJjCeP2bsM+Q/ZhwymobagrshbguGbVLNUhPGJm2+zb70mMOf58/n+I9xYq473XK94TrGWc5fvFxovAI9YkAeMRln2wnYdqhhoL61pGfJ'
        b'KOOa2FWx0Zhxv1iBX6zQK07oHD+pKBWJhqS5lC6bDEJNvvQBGHpEmnNFa1gLy0OmWQb1FqcOp26xcTsvgZ2X0NJbyPZBSbnhlqqr1+hX5zd1o0OXa4fruKWfwNLvugPO'
        b'2jh3mYC7rElGyF4+yZJBktKiDE1PaLcr83Wsx3QCug0GzXvMhxyuuA+7Cx0CJnT0xnUcURWO6axEcpYdlh31vuZ71ff63PGgJEFQktA3WeiyEt2FZ6PG8LrwhxSSPt33'
        b'RHU3YWJ5YkV74ZhxFJKt2bDZqCEelK/ZXrUVukWNGWfx4+LH4xIFcYn8pcvHl6YLlqaPL10jWLpGGJdFpDfJErPXeyCDy+Vf5z81BEa1JTYnjps4C0ychex5E2xDetJ1'
        b'RGM8GsFQPTKuSA9LozFizDi9PR+7+Rq39RbYeqOfaM7IuJpxPR+7khsPTxaEJ/NXpvJXpfLD04T+6XfxI6unHlkksF2EfqIOJXlDkh8RNR6RKIhIHI9IEUSk8FMz+GkZ'
        b'/IhMYeBqklBoe15XcUdxd/7gxp6N4/MDBPMDrrOuz+XPDxHahuLm4t/sjyrEvcOdHk2Fxp4T5jZNaG7M5MfGj8cmCWKTxmMzxmIzhI6ZgtiM6zFoCAjqCRpKGXUc9RnK'
        b'fM8pkB+bIXDMRIOYqyEaxEjtIbkE1wWL5PJCKu4CS3ehsceUHHWJHPXplYMzWi+M6aTRDR7JJOVqCmoh7jfcx7kpAm6K0D9V6JaGaxbV6phOKKpTiR6J7rzBgp6CIZ8r'
        b'4cPhQlQuu1DccQPrAifYNg8pWQPDbvvBeT3zcDZCmkMmzDldYh1iE1bWXdwO7oSd/aBYj1h3XJ8cypC1DWqr1u7jVn4CK7/RFKEVd8xqGemXcYIINLQtFUYsQ8MrxwJ1'
        b'ZY4FGXVzhOYLUB8xMUVdxMRqzNgf5Um+R34oXWjnP6kq62SIczDvgRplatYW3xzfHi80cZ7UlEeDXzEjiGGm9ZgKYmhqP5yDRqsH3kxK3+hBmhg1R2tciS1QYjfNQauO'
        b'wObACRXVmoCqALS+QuUWqljh30FVQXXZR3OFKjaiX7UpTUsFevZCFYepgLSmTQI9R6GKEw4IrgrGix+xOrHamMaldUvHdW0EujZkdaTTKFcnN67BEWhw2g3b7dFKsFtl'
        b'ULNHk6/h9pCS0dQbdR5aT76IZqXbbAO0ZuQ0c9p9u0I6QsatFgisFgytHMrjW3kLDH1GVwkMg8YM465njBkm85ckI5mamOIWIBJ9ezQaNKeOVfkJnP3GrBOuq9zSuaEz'
        b'HpQgCEoQmi+ZMLccM4/qFhuU65GjxxP0E03ZcVfjrvvBZWi8NzGdlJTEDUgaiVJSXlVtUlbZZO4jSnmO8g/m1Bzd2uh3lQwm1LVqNlRtOLSJr2T09OEiMcounfH0YRKT'
        b'clrNIIbiY8ba66RsvrbUXidvRx+Kkn4ZvuvVewB8rihp1po//z6Ge716wa8jgR5zpQja60mhHYMx9wfqL/K9CpiEE4uhdF8pYIVxWFgYRwx95CdjeJ7cC3TW/J8pgjaL'
        b'XhToF+oXTXisBEFG41mPTjNVcc7zd2ApqObv/E/tovAu3evV1FQTLM2X0B8pfDishIHEuJP6QYwpr4S6pGEUY0LXecIArR8sf5AWN8b++0jYggkDoxfD/EiY/nRYGgqz'
        b'njCwpu+zmL7vxbBgFGZK0nBDYbbTYc4vhCXSz6IwGxTmxcCBOtYTag4TatY/ZDKcNRRKAx/kMCgFtUkmQ14XY0vVHuBvD/Uw0DSebxkuWJx4W1u/I3pY+SrvEYuhEMK4'
        b'6x884e33mOUuH8iYFMchD8Tw9x82MCgVndtKZhMqvo/EmSr+jFLfh1Ikno7UHv/25VdX3XAWRMYIYhMES5bxg5fz/Vbc1tLtcBw2Gl511fjqOr5rxISuI3pUwRl1V38G'
        b'KlFQ+BNWAFNea5Iin5LkEv76JErMhyVv/COFP2nGKj7CDI8vkCaMVZoxIg0G4J4pQwom5bFEAu4FpSazTqXJiv5OpmDSqvIfkFZZKVKi79Izvsug77IpcuS7PPquIApX'
        b'nPFdRF09Jj1NVFV5BVGV9VKiquosmqnuNFFV7TdEVfWdVIpGp+a/m6jaqXVGYkYO9KZ5qvJp4inav0NS1ZlFUs3g6H+gSAjEmfmpqwp8U1dmFvxs+xuM6oyr/wJD1YVG'
        b'5zlwmB+ILQqP8vuA5ePgk2+Jxxhr/GHL+vMwUxea/eTwlwiooodc/jrldCo5gpqyx5TTfBcM/2QRHmm+K4aSykT5hYbH+BG6qfELZNFoX9+o1LzZgDu7fHdc4D9zq/00'
        b'AnQqIz9rvCrWaS7o7DxzpGfFgesh/58z4aJTwsnHUM/8Z/jSq9Kwzw/Apf6/DgnKpF480yoeRg75+cFeMEw7AIG73CjaEUkHKKfdb7SBFgdZDPlngGEn7KrgGDwPdmR+'
        b'ZKclzsPq8Q3S1UffdGloPmSwj6F80i5tjZ2din2cQ3KNYtrdEEnq3RyjYPGRPmsOg+hy58DOjbQxi4q26P01GI77LVqUZn5qvNC9ZiNFsVIbI0VTXGYe6J/QZk9R9JXY'
        b'/xPQ6CsTnSs5gzKa7PI/oIzmc1n/11JEMzjMewYSf5YimkLkgzGJ2Cb+34kQnep/f4AQneq/f3iHy59GiM4eEl6FEH3VyPI7TM+XjhIvv/8vIDxfpJ/QhvrJOdjGHkNM'
        b'XoHkmH7sZQ6afoP9nFXPItQnnp1ofCeaoSxeTc/4I8bmVE7+CmUzM+2/gM3/dwCbUz3uJXxJ/O/PYC5nd9o/ibl8aQf+L+Ty3wK5FA+LKcQcMjC8wunlLEV4EJaH0Hbk'
        b'gSF5ys/dRF2Be2RhK7jIzZwc/IbFw86Bixu+Pvqmc0PzToaEm6ab64bb25yizdLNEs14ZlyzjWbfrC4qtTJaJLPKLMBDealztFpUvDZLwvwLm3s7e6Jr4xx9Fofur5Y7'
        b'9hVVvEL+wqQZR5x+y30sW1ZkWOoeQ7MML1Dkle8cMLT6JSBDFmhxtncOos8j1QTpvUgKZIEKcMIXnltAH0A85gWbybtZSTBA4Zez8BRoIm97VfXVsC0wOAeqXvBGq+LK'
        b'kfkfqAPw+uGl8L7frmJmkvv86aXTo7Wu1By1ytymAoGSc3f6UMFo3PXYiXneo/Ouu2BuXyyD6L0rxQ7LT6jr1Ww8uPEFAp6G0X+OfvfKEmlIzkTfZbv8j9B3+UtZLyzV'
        b'/yzyLo3DCMtfTjs7eCnu7jcZn2Ld+aCMz2DdGb5iwv0N307i940QV0nOyKDsrAWm+OwFJlpeSosWmEwRvE4ew+vSZMkCU3LWAlOKLDAlZywwpWYsJSW3SIkWmC+Ezlpg'
        b'bn7ZAvP3wXUzd9f/T1DrZqPXRas2EcotG81zmKn1X5Ddf0F27P+C7P4LsvtjkJ3VK9d2WWjeoDdcUxXxF7h2vzNk/Ce5dv9hGttc2kkO2A1L3Wgam1KyBMGwgzP5NIXd'
        b'BV9vXCpPQ2MwFCrcOk5EugqG5dishxuPWeXghAvGT4lR4CDYJw0uyIBdhLEGGuE5wxcha5iwtnkRBjHJidz0gG1qPHmwhzXNdQP7Qgid3W453Dl1fBeciH8lMJ1JgUOw'
        b'URpe2ghqC/FpXHF4AWx7TpCCpYFWtME6LA1FK/QgsNUY20+sMJPyBttlyCPgcjY8yLXJB0dnL94xFMsKVoRaEROYKFlJWF4CzhPWVUyqBdxH4rMKio2It46LD4T7OSmg'
        b'PTg0BHTEBIKzgaE21kGhKA5bJuiVdQD7oqIpPXBMIYsBThGrXkMLPZ4D6AIt+ajs2O0wbHUptMdLqyWeL8QNS8EAHLSKW+uQj6FUBBInRiWBfZKgGlYwSCH0PUOi48FJ'
        b'WE3ut5qqrBj6GVF04lRimiRoVV5DzIQXgOPgrGy+gvxC0MekWHMYC8CING00fwBchi2wDw4W80ADuIyN5q8wLBNhA7F7/oeqmFIFhdayXklW31tEUpnH1vYzeM/QFb+Y'
        b'6IaDt/YCO6U30qO+e2ZxorT0yY+fv/fZwtcu+yw++XHUnKrHTYNzPPYqCmruRH64pLi3u/atnbaf5F4Oum5yYTtz73Wjtpi1K25Xqu6pNhYfXj3+VdG5z9d/UF3vf3b1'
        b'OSo/+tbY4OmEfmmtm5wfetxP3P+8W9zR5Na86vvnaqhT71wIP6K86IZK7Wfc+ifG+SGrgmp3Lfuy5u9B733ReUrHqe6f3C8i5r5zMWRJzOjHVY/uL3s8+I/y1i8fZI+/'
        b'I/nJSsNC3Y/Tc9qCVwR835Ze0vZ2Setrz0Lqgm8plPvwbyj0JX6nuveX1Z94Pj2a8F2LgsmX4edsnj2uZcrcuBWb8OtNW6k4z8jPAnarv8dRIidu1d3FRaR2S7h72jwC'
        b'NEuR7dFCsDUH7At3B4enQfBTEPhltN3F2cWglRsO9geKKE/wJIs+CHx2Qzq2X6sDI1P7MprD5AgayLYtJWzFNIWJ7LpgNbxMdl6wYTEdxQVQV4SaF6gFI1NtQjaHCY8q'
        b'gUMk8eVJpmhXlwFHCH8d7eqaQD05dJtkAfu5IbATHJtlD3QO1K4jx5yVgiNkLVaBU8RE8TcGir6wk6TPKvKjQVIom8vgWViGklGAF1khi8EBcrh7JTiIdtTWwaGrwHEW'
        b'JbaQAc7ANriDPiM9EhnEdQDl84LxcNFFwUG0x+yiL11YYUpU7rA+ZcpmzNye3svugE1qlsGhohphUMpmLHAiBB4F1YAGTKGvO3TJXhnWrGfS4P8MuPeRMd7jwD53bsir'
        b'AEy56bbw4mKOwr/pvTd+cc+exTyaQUfRf3GH9TLYUT5Nq//B1/2vwo4wfEe/pqSq5F11c7IBXiTU8uWr+N5V1iPQIfpU3WjqmCOXXPYRai3iqyx6IEdpG2JiUaUkZv/g'
        b'KwuEWgv5KgsnlLVq3A+6N83HJ267jQeteqzGHXwEDj5jRj7kLPPUfep64+pmAnWzd9U5JDySH5M4HpMkQP8zSxJqJfNVkklcVe58ZQvRFr2poG198/puvzEz1zt6FnxL'
        b'v+uSt+RuyAksY4R6sXyN2Ald48bE+sT2mK6EjoQhkzFrT3Kb/3V1fKZEYBkr1Ivja8Td1TYc17YSaFuNac/vVhvT9h6aVyl1V9uofkFTXqXU5+o6tSvaUwTqi0YDrsfx'
        b'Y5fyl6+c8A3nRybwE1dNshgaqRj3Myd1pqtehT8D0PnjkySkKcxm5fyFpuCHlQXY18ezrdSTADcGI4jxmMKf/5Ku4H+DioP20z8v+0Mqzsu2z/8mJA47jNA7bUB10u8A'
        b'cZKMXo3EUTUGXYRmExG56TkNB3RTKxctYMlShrCTpQRa4E7Yu4BGuKDlEQ9Ff6noOVIyahkNkR2MgP3wEBr16jDrhoBuQD2oJLPyGxtZVH8JpvknWbW5rKIIpAPuhpe1'
        b'McuGgGy2o1UGhtkYwrpC3MqKbaMwy4aydfCkbEF7IVmYoFVZlQwvDxsSVlAeiqDMCe4kGXNVhO2WHAts54niaSMkm2McspRY6QGqMciGYwUaRCCbJFN6jTcILsGu6CmK'
        b'TbI5OABHTGkccBNa1uzCJBuMsQEnnQjJxhQ00dDf7bDTS5asLVm2ORTDAnaANoJ0wVMSLCN8mVhYzkRFfM6XKeAQWWxRPUBpeLgyKbuknJVGOjQfRt3BkNrKLccCWvnR'
        b'Wl060Do7iBpKN2KgzibzfmESHahgJE8ZByCRRSRZndqYQQeOSqhRHksTsDMdnVsp62i8J6hf5kLAORguA0dg60zADDwNT9FC6IGX4ClMkcEEGS1wSYXhPteUxOodKUmt'
        b'ddHDsVqlrZGgOAy69PWbYQ8Pbksk5pfY9hIeLiHVs2ytHYa+YOSLabA0wwU2gMN0ImXwYLbsFPOlVA7UgZNouYrbTVIovEgsdC4T9AsNftkCLhC8DzzOssIKtEh40ZGK'
        b'BK3gBP1O/ArYaU6zX0IYcFidsF/MFAqJRVA3HIzH6Bc46A33TqNfUI2czoy/FynGa0W13R/z7sjif+y7E6Ny852QtLQvh4Uf3S5Kt7bMyDxjbv76Eu9N3RYye8e2b7c5'
        b'Ua6am1edcP7Mx+YLIyTUL6yM9bWyMH+vRyUyQqnKEP07wd5798qnNxqMD73zNOdSx9mnJjeKbz29WfzJlx+PW+a6nXM8pvnYHwhurf6s5+9v5W2a03JrX3L4BYWNJ6/Z'
        b'f1I+wmzbGs/5YW5wZ9nV7Xbr47cVu/5QtNnWPLLh1K/B26u/usLNcr5fN7EuWK7oQsVDuUht9mrnx49HnjrF+8Vu//rNXW8esr7vlyH59+tfG1TYr4nQfXzkWPnPvSe+'
        b'rz9949xt99ooE+cfVfzkg1NcD61KiE+NHT+SGlu9oJ1n6fslY8mhzUpc44Ufru9Ywa22fZj/9Z5J12AjqFrhed40DhYvuKf0TndW3M4s9a0Z8qtrgoOjP9gi2Z0b9U3M'
        b'vPeSzQYNC+b72krsP1tr+fr6srPzz7/RqiO+v4bxRv2lO99qn3+tesPl7+4VxRRV5bSOiPczj3e+H+l6b0LSecXrkeudr/0yL2PXmqb3v0H/8z5mUvH6txIHtF0HTOe9'
        b'lhQ5+NE7XuETveMyyp9Yl+Z2c/s+evOtbxM2Xfv+kVl2ddenAzqqxYvPUFYnV7q1rHz7wif1P1Ip3z0WfnY3bM08foly4YbdS5OzWi+6DHyuk61ToF+gcOEtXv8b8wLf'
        b'+uhOsPO8J2+cuf/zgMNTsfLI/oCKOydt3hr95NATn0cLK7T6P7llP6/xDcvXtt9vlGRPNuscCZLX275EkeX0NvX463WKixoDmmTe+vlp4i91C8+YfGduq7nxp8gK+Zzx'
        b'lqI9ccOrz0ratarcabqt56mdZbnvtYKdNZ/Zf3ar98e6rtPhzCvLT/+S+WHGTgml8++vyTiQ7nJk7MmRQZ2Ukm0tm7oqAnp6quuPPttx6nTk+19Y67d9H1e76syRTYLO'
        b'm43ul/a98a7TwIU9JyS/a+ob+/Gr8uwTWT0t9buz7qeWKhj8LOOVmP9RZ+OmCp9G+Qr/4Q+tEg1AQkl0mF5veO1kd19DQ8jXP2ol5dxYpVOduzhx+48PD53tqH5oPfr5'
        b'jUGDnxX2b9Dx3aye9D3PKvaJ4j+Vn+yh+t65u5BZFDTgaZH6beLDVTmNKefM1mvelLBXjN6TSHW+7jTGNfzYMzzDuq1JrV9ySYCmToTgWFTOxxUptzL6jFTT3SXdx9oq'
        b'5Z9YRR099KW2x02XW/MfqL49+V3C2uO5D2xrv/ywT+XGpHxnOvr2RP/WpPzlZ+HHn2k+sK38Urs/8fOnzxween6pcf59vY+OrvAqfDyptJYVu8JH/DPnf1q2U98+q5Xs'
        b'tF7B+mTe6+6nPtvM+qxh998HlX69GddzpbxjDXR/9+mNCwv+vrr6E9aZhS51v1L9/XXLzO79OmeiuPdx/8b9Z0vePF/xSfk7z7b3fvnjkzdv+m/+9XZvy+mH6RHqByZK'
        b'GN8e/6W65fDTX98QxBx4dpPL4X1ycOSo88d2Rxzm7/5pec+xnp9ZX3vWFMf+PSTErHJLxjMz242GOuFtu5JV995/e9sKwd/vPX19hdQtb4H19+sFQckbqy55Nxp+sd/s'
        b'6RUX/8i3H683e9Nu7P7KqvwvUjnuJRN1jv+89a2moU5r32mHOtfThs8kLrQ82fLB+p0fb644efmUwq+sn1rFPCQPcNYSC+cVoBtUyYbCSxYv374UmtEo2MOwB5RNU2wt'
        b'QC1NWJHTpw0hq7zmifgqYKfyDK9YaGisow0hj4JhuAMTVjg269B08ZywstaDvJsDXfPA4edgFNDoFhgiIqOA+mTa2rNMDXQTMkqZqfYUGAU0g60kBS2wO4dHL1RgRcFM'
        b'Lkpv4CNzPAvKOfJsbDAThRNskxdkkQz6sEGqiIviDnZKoIAOUE3MXVNhxQYa4QCP54nIKOj7ZZrBsM+AjRkoQbA1+TkCZdiDNpoeBudsaQQKl0AhaAYK7JlPX97JXToF'
        b'QeGyUP5oBko+3E3E4B8EG6cuLwflMwkocIgiO74MF3gGA1CwoTlshuUYgTLfn2RMCuyG3SIAShBDHBwnAJRl2vR2cBdstHuOP8neBA9M0U8MVpHHLUDLCm6wVRDcB89P'
        b'w08sYRXJ+IpI52n4SZ6uCH+CJs3jznQF18A9UVP4k504XzQCBe5bVEzfMARrs3HepDlp7rPoJ+UGJPWUyNU0vgTuw4Tei4RfEgzr6beu9ZagkTcFLzkMG0E7PG1AjK7h'
        b'ENjNmIEw0VLlTBNMwBXYS/MemlBzFXGWxWA/OE02yjmJZBs8Z2GRbJi1HGzQ5mAQSQsDnoMnQS8ttRbYUkAABnjNu91wBr+gUJJYXifAtkAuTUaBZbGz4Sj2U5b06Ntp'
        b'nk0Q6JLTha3TeBTQ4U9UCCx4GYlmO6zFgBS8wIZlHJqRoicmBnokJOmsnAmBJ7icUFAeDqrg8HMcCtronyc9RGsdOIbJIZZWkjNZKGviyIvxpfC8A7YQRwsoM3CcmMiL'
        b'OdPSPbnGlUZ+YArKMCgDlxJBLW3zngr6prSKcAQ0T2s/TsEB2rz+FOo0xwgMBS+Q5UElZqGAsxm0xfLOBNylaRZKevoUQxot0KpJmezBXtAnoqGgwH0iIgq4CC+DRlJz'
        b'ZrF0mUKtGaimm2gaioIIS+EEauBhmoaCcr9FhsBQwFEwQA9LB1F/aMc8FJsgeNRtBg4F9ITRmT8AK8FelH4euAyap4ko3hxy1XEurCFAlD4K7nkORGG40s8eBY2S0/hr'
        b'1GT2YB7KEjhEsu0BzoPDqD8QGgq4BE4TIkqJLD2A9FjCSpqIAnao01AU2LZBhrY678N+PaaQKLmFNBQFNMEqmh8DT4NauIdwEDA+ZJpo0I1kQq+g8cpcxENBO596cE4x'
        b'h7RzPXiFjYEohIYCa+FxTESRVyelyd78nJTOgq0xhIeCnt5Gx3kaNq/kgVqX6VV5DKDJAWgsb4R1ROung7LwHIoC+0ANLafjaNt2lOY2wB3eNLoBnNZJIE0fnvQMmgFF'
        b'WYfGjjKSexqKklBCgzjawQFwnCdCogRrvwBFaUSjJw20kmASKgrstQItU1iUrCgaIl8Ga4u58JQNAaNgKMocEV5+noIH5p4UhRpNIVFAmwtNXKjNwrit3UYEi0IzUUxB'
        b'ObkWbL2cAFEwDgUcVKGJKAPmpMybwVYpmodiwZQA9TQQBe0dL9E8pU6wexlhNYSBnXhDXRoKz6PcasBuMUvfzbTU6sPAwaldCOhaTnYhoAG00WUpBb1oW16TLnIXybCH'
        b'231prEEVPAv3yoaJYp1jjtutDDjIBJ1rYCddqCaz9ShmDhPswa0T7VkNUVsup0eCagk1EY1lqRPNY1F045Ka0mWDczy009lDT5/S0zgWXXcxUBUkGumyrcB+egYCu4iS'
        b'k+axgNIMehaoACOe0zwWDXERkQX1vgpVooYttliMVgEjCQTHglks8BKLFMwB9Jo8R7GEZnEJ7YUmsegZEKkooU64m2tNZsbUjRjCogK3kT7jE5FPJxoEr6jNgKbAJiuS'
        b'a+PYpKmXLpaMcAkRMwWNd8cJkD5IN5sgU17gpYB+eHKKmQJPzxeh5txLeLSEwA7QjqSE87WdVQC2o0Eac4CCQBs8glsplyMN96bDS5wgERhDE2wTC4CnwEWSJ1vYvIa+'
        b'DZfUMR4tFI4xvdGIRvtFhRdgTz6GpaCqBid1ZtBS9uSRG5igFHVO0QsVMAQOTmm8we5M0ls2opbSQVTOeCVRbo1VzqhhVZPUjRJTeCjhcNSSDsBLSpZoYFZaz9qUitoQ'
        b'flYbtsVYosaHBvdQRoEbElgdc2MQ2EHatwQaqE/ysCuXMryq7EnVQHlgUHNUWZtBFTj1yIH0aDfs9OH38DFwGLSLEDK24LQzES8D9gdPI1gCOZznCJZS0EFPta1gIIuG'
        b'MMEmeEAEYuqAexbQKu99oAMM4Ouo21LZhAcGDuTSYzbcLUmejANXplFTcIcOqTbQIgfOvwIUs1XczyUtdRG9kK2BI2unITdesM5iGnID+pxoTMw+UMmxzFshoh7NxsQU'
        b'omETN+ZAT0lZslBgSYEdBBIDh9NIEcLTvGWnaSpxHgQRA8+lkGueaD2/DU2ImA+ztpAmxBwGomHnUqSFiBCzGXbh/jBNiEEp7CU8khXgopasCA9zwQXuAu229DDfi7J/'
        b'dooQswlUcKYRMYudSMpOoBGcw4QYjIfZ4kkAMVngBP1ip9wDNMiWwA7c1DAhBjasJFnSQRPLCI8GxGhFvYCISTcjQ9JquBd0yVqjqfSklYgP4wwG6bWBNRgQ4WEsGNkB'
        b'IjqM5TJ6Hq2Ex+Aumg6DsWQXaDgMXtuRh/1AAzyEATFwUB0eneLDeLmQ8hoYOE+xYbzgQVzXU3CYJbCWDNCmLEqEhjkFzk/hYQ4HIFmTKj4IG9AiluYuBqFbemfSYUbs'
        b'SQ5i9OD5KW/AeNY95IzRMFf8aQcfrWAnfol2MgvjYTAaJlSRCNrLxIVGwFgzfWG5CAGjmclR+w8TXwgl+YV/vzH9VHtRYT8D9KInQ7+yifH410Av2mMa7r9hulSKP5Cg'
        b'2Ab/RkiLpUDDUqhh/VcgLS8P/HN8FpWjCv8+PosoEZEpeFNkW0xzTLtpy1JUYhyGZNDOINbI5LXRGUWhjouI99Dk3xbeHC7UcfpriJTn2A2FOoWmoraS5pJxM0+Bmeeo'
        b'jNCMK9QIwTn6L+/k//e8EwWcU9zc1YQa5rhNyNfJzyi+iOIxw1w+pmtpx9Jx6wUC6wVC84U4VLpDGvMLAjoCuv3PhCPxcCwmxcVNTCdZ0ybxLFlNrclIhhMmojgRIkrW'
        b'v0pEyWnO+StElElxFqo1qX8ZHBJcF9yUj98Aj5t5C8y8R/Ovrb+6fjwgQRCQUBss1Fki6s04MvlmeSy7wOZAlJXEjsRxay+Btde4tZ/A2k9o7I+vcZu53cxB2R7ZcbtF'
        b'ArtF43bBArvgcbtogV00P2a50G6F0Dhp6j5JobHLpKQ4Finqjw+UKF39PwMe0dVvTKxLbFxRt2JMd373om7Jh5Q4KnLklYThBJGk7lpaYxhGl+dpT9TSzKxP5HaLj5lE'
        b'D9lfmT88f9ThmvtV92ueVz2F7tFjJtn8+MXj8UsF8Uv5y1aML8sQLMsYX5YlWJb1bnz2hJf3NYmrEqN51wquFlwPFQYsEXolIsHjLIsvxMSZ/xJK/kso+Z8SShIYbhhQ'
        b'4jbFJylmYD7JFtb/bXyS/29jSQpZNJYk6jmW5KadNs/D5gtj7QKGzb8VS/KKtWmp5AwmSajHv8AkeYyZJPgsFWGSsDCT5AG2JFH5TwBFeHgT8TKWCC2BSSyBF/EH9zCO'
        b'JewlHBGrl3BErF7CEXkxLI0Os57Q9ZtmhgTOis/6VWEYD2KH8SCRDA7Bg8TReBCWvIEID4K+PZQhWI/2hVeNXgEHMZkBB8HffwibhoO4YDiI219ng+AEohh3/YIm3D2f'
        b'sDzl8WEo/ImTiULJ4O9PfJhZTIwFwZ80FgQrETLgiRDZIrAVnJdfWwDLrIJDbfKCQuFeKwZlDq6IZ8O6dbOO5SiI/k7+jJkgqi8SQZaITRM1MBtDmVAzpEU0DYVZoSqz'
        b'fsk8/5XJSmN1sqYYHSkmxFoI2wph2yG5UvlShVKl0rmlKmlyKWIz2BriTCpVIkV8J5Ui0Sk5TfiQJKFSKFR6RqgUCZVBobIzQqVJqBwKlZ8RKkNCFVCo4oxQWRKqhELn'
        b'zAiVI6FzUajyjFB5EqqCQlVnhCqQUDUUqj4jVJGEaqBQzRmhSiRUC4VqzwidQ0J1UKjujNC5JFQPherPCFUmoWwUajAjVKVUPI2RYrhTaokq+WaEvqmVUkjiLCRviVKp'
        b'Ulkkb0Uk7zlE3sbouvp6pnQGx/QDuUXeoTG+oiNe9waYL1haYVOHmXfQqJLpg/oFudhHPI++x9nBiv7rSDyq429OsyKbOknGs2F7z7AhEpnEEENokeENulqQmk8cvucW'
        b'peajX7NtgGY6f7dipyavymDnp67NT+Wl5syIYoaREraJmxXDq6wAZp9nm/UjLBcbfwSlodKRw3LFqfmpbF7hyuxMYs6QmTPDvpzYV6DLyej/BRn5qbMTz04tyMhNISa3'
        b'KM+5WUWp5ORdIZ4mstZjO41Z3u3ZfpnE5MHcmyOy9MuabQiC7SVEpkR0RdiK6mFK4lZscx/O1G3JbF4qNmkpSP29SsJ1aL6Ig43Sk2eYDYkMdnLzM9Mzc5KzsHW0CBaF'
        b'RIAtv18oKI+XnE7s4lMxYSALW8/RpWenpK5F8yKPnUtnnNj+mIuu+eAWlp3Lm20Csio3OxtbNJK294KdURiH+QFrXXbWBxKrkrMLnJ1WsV4Y7sgpxE3oo1qONmesoUjn'
        b'kEQDEpOYM9KDkiLqOEqljDQFcviSxaTKpk0TN4uRw5esGYcvxWYcs2RtERMdvnwhdKZLwnt4xP1DWsasLvdqu5RXmSohOdBWSotDQ0RmNrgTJJN4n9cwqktiioY68Mvt'
        b'18xT6Yb3qt79OxQHUglu2Bh/VTIaH5JQlpJocyE6sulIZjbS5JyXW/qlpGTSxmWidGc1Utyc8wpTRR2dV4h64PRA83Lr9VkmeMUZmegJ3E+TCwtys5MLMleRZp2dmp8u'
        b'MkX6HTv4fNR/1+bmpGAJ071/Vs/9/cOxktSLh2P1wnhYS8zuku8TPLHknC7g3OAM7Jvkc97v3cajMjdLtV7dTc/6lujD2A00gD5YBQexP5ACDizjgAGwD2zfxIFHQC+g'
        b'HwGtYHso8Z8eQ5zcBcJdaKFwRpyitoAT+uhjjyY5OHknhkn1K+KDi0lyP/PcKHIzGALdYdiahXIXBzWUuyLcn/XTs2fP2hXEqWMFc4jFilmWCkVOMUrATtBOPFPCw452'
        b'TApshYfEXRkRsNmfw6TxZVWwFLTw4F4FWFZMH5oJCYP7AmykLcwZlAM8LGEJj3BpJ4lgn4qshbm4MoNihjLmB8OTKA78zhachbvMZkYhgz8YlCE4AA66iRuqG5Ejmg4s'
        b'eEiWvqIKDrPgBQbogCdBHYoFyw5cWsablY8gi7wwDuyxDOKin2AY9rKoOFgrpZOZQ1vwdFL4NQR9GZ6F51mUlDMzxw0McFjkhiBwGVRxw+B+a1jlaOfMpOQ2w14z5ho5'
        b'SSIb2AU6bJ5flqDktoBGcIiZFShLnwAdgLuKnl9nUHIl8uuY2XAbaCy0xtdb4F7QDPfRRkiB+MZITGgPfH6GmkH5KkqqIxHXkDUhbIAjoJ1+CRIJLsJBazhAXoIogwrs'
        b'ZaISHizEFv34XcmRmUexzckpqggUcwiXa83MWwAadFBUe1VhL+zlqoC93KgEWRnsDTw4KppKTVOazwT7SBM6s0SM6pxHWkXWR8vCqcJEFJgKho1fEj02BoNl2rbBseaw'
        b'LBDuj8aGWNxY2D3dlonJVXiQ+FwTGdRkW8XF4bCfCejgUH7FKqhwJ+B+JHq8WbMLhpdhn+LafAZltYYJhximcAgM02d4T7CdZKXyixjYBGuIJcawQG1gP7kkBi+CM7BP'
        b'Lg89tnELE3YyUH+inUdGLYEVvLXkTEI63MuSYyRtgOXkoTmUNy8P9sqh+gGtTLiVYYySakVtirwD3KoID/LgAI5xCexhgksMNTAsSaKc7+ciSssMdJPEYP9Kcmp7uSU1'
        b'u95T4CAzGzSnF87HvXVTNL5KVzwsDbUODkftfDg2cPoRkUBRZ+ujYGOWLGgH1YHEZlDfo+DFZ2MpyigFNG0Ug4cX5xWKDJgumUeLKgXUwCtoXJJmwBF4Ae7LHHj9NQbP'
        b'DE2lgfzJd+LfyRF6KX1ceMcl505/zpZ6MQXrT8PZzTLNagwfHQsFHYvIPK/2CN8aZqJKs2mMyZJ9Mnl571l+GrFuuwc1/7UPH2iFhBR9u/raewPtc28YPE754mhu2uVl'
        b'b6l0XYm57LDn9feGdMPldY5sGlj9w/7P3/5JyubY0ALzX0Y+XFN82nWL+L20X6kSh5x99uX69q9/+oWWv4XpMmW/DWL5eXZ75y63vNW2c+E/+ZIOBhvuHDYxjL7dL2/3'
        b'aURB0ob7N//WFDb3zhvOg0mlS303Joit9Im5rGp4bkhu8qlVT5vl/rM+ZkZmFu0++X/zXzVy+nFMyPAF4bLLn7ydHD8/+03BtxeO5/dWC/8uSN7o9olhesNo6ohmZ26U'
        b'Ucmndt+dqnN/eNjsQ7Fbfafka5NzY/NO7kz4ZvG3Nm8cH9z30b2P1MJbbJakd361ZrG0fPvk3mUn72uynSr7zLoS+s62Zb1+WOubHR8veWqVZ7H4XqGh0Cr5YvI7GVX6'
        b'+puvjh04J3M24IsRv4n7SgMXi9ZbW5x/Z90tG6MYt7auA29f9J24n/jlaHV+SoXk++uGdu+ULK6JKpj4cgs4FxFlktjge/nhgebXEmoPPMv94OD80G++MPTwfGtkz8/L'
        b'd9Y1dBnHvy3V/kinW3/PSPOpN/5mJGQ1pguPcm8c//jNu/HRm9Rdvls7nGVoPJFSpPtRI+rBQWbdz97axRkNOZdmp+Xy4zXTg5t8Jkovt35JeV0bydp5/8sTnu6Mny8N'
        b'GH6vnib26Nn8R1c634xScp0n9eEars357+71f9E8IO1VUxTZ39au+DR9deL1n4qtnjrNs93h9k1Z8Mdzn/3j1698xUvltVY4/3rhrRv9bz7UrSp+q+KtDPExjcPvLAla'
        b'+9h8OETn68jvRy4zvyh8V7NZYkTv0fec06u+UHkvz/2zkrmFWcrP1hT+H+beAy6qo20bP7tLryIovddl2V1gpffeO4KACFLFggURe++gYl8UZRGVRUUWUSkWcCYFE5Ps'
        b'AXUXY6Km50meBNNMM/nPzFksSd7vffM8z/e9f3/+lnPmzJm5z9z39Ou+xs5X+mH/50+KznDqNjYEynb7waDVP7z26K6h9Fxamf3bt050HGRfWbv5bs4Az3Vh7uzgXejH'
        b'6o09LvtCH3295dgbbqdten2tgt80/WB8yoNNc+QfBc7xprp26iw97ZZ+43FenbBsRu/nA4Z9/lGltuNfV3/y09TwX3d/rt595XStcvzpYcEvVNHv39ra3jYxOnuLG8Hs'
        b'Sx/gwos8QYpHLptiAykryRdKGFSSGF4C21EX3cU0f2lwJ5uCUnhFF1xFjUKpBbNFuw1egSd4Ccn6TpoYbsEKmc0ACeAgx4UHNoFtBKw6AVX1m032s6eD0wWgfrq2kEEj'
        b'ahSzHSxgBwP66QVtMagZOIu6wB3CND6b0ljLdgfr/cl5O1MF8CqoF2KMZbIA7EjDSM3dYLsw3sOdkPDogXZNqggNJDphL7jMgCHOLC9nQLfPELexUziV4JQVeWwKN+Nz'
        b'zEAr2I7S2sXXoDRmsR1hJzjAvN0I6qOS0vgJHhhnUQYP6IKL+Ci+ax5kj9zE1I4B/cI9sFPwAuoXvddJYiyajvp2xi9T3elFPhzYA1pURyf5gquqPXrQnqA6wCUNNDFg'
        b'jT1Tl8OeKLAFb9JP7NAbLCHFGOkDB3kJoBONR1CPPqhWyYJbnfIIqiBuoTVGljw/2gW9agGbwTXQp7Z4mjfRna7hqgmQHOjh4jHDfm2C81hTXocKOTEliY832VNVrzvB'
        b'S6isDqoHgVPwANnhD8u1q4G7ErA2kgxS+fBiEmrvD7Ipm1g1cMpZBXvGbqF9GJu6R5tEYVP6MRkr2bAfHpjKANs6dFHDXi9M5XukPMuuEGxjUXZeavAU2DOTaIKHhhWt'
        b'z0+igVfdCdrAA25koA7HjOB5UJ8mSEzxSEhhUQZzwBHQzPHPAjsZyODW1BnMAEOFr9D3gVtmcDRBvznRQpafObL1ejiImZGSYL0mpaHN1oMSW4JEMXGGPTUEDwMbYzjz'
        b'WKvxud1EB8vBwaIJQGHIbHLAmgvcxii2S7NiAh4HD8PLzIlh8FIgAyfpB9vgVpTnICqKPQzqUB0eYaHO7GI5U4XOADFo0RUkCdD7e6048AwLjYUuL2KwOCfhhsrnqEFk'
        b'M4KXUIOaoINInm9ZiIF9s8HRCfAe3B9Nkk8B/YE1RmAzhv09A/2dhocYoPmhKiRgfRoBCoJGMw48ygK7Q2AD82XnYX8l/rQ9PCTahlAO7GGBdrAtlvHHPeEIjk5gacGB'
        b'eWgAC3bFMdUJjfXDQX0h2DiBHFKHA2wW3JxDLFKEvqoJnzpXl8JALMthI3O001WwMxRrl++eOAej1AjGcjI4z4H1dbCTaLiszIIc1IVhYKC1BB+8eYQNdoDDYANjZxcD'
        b'/HT/gPEHnU4TMH94nQGQC5BsYjR6JugeF9DPgZdY4PxsBniaqCFkHpFRnwZlUAbXg8OcGHVw8js89A1dDVGDUbcMXtRf/HwciVm2hHB3fAqfCw4HalBZMVoGoNuRKehN'
        b'cJ91DU8HDe65YD/Yz6I017CngfMxRJjMBfBKDW8JNnlwpVqd0ixne6NJUgcplHJLKEZfnICBWOAgN42HMe3q1BR4Rs3IDexjzP482ArP6OLUURoxWCea4Aw7RAN2MdUG'
        b'DUkm0kCWqkkZpMLzazjhNvACg3qtXw2u1yDj9ADHWRQL9rImLTAmMCkDeDWagUmFgM34IC2JJknRepW9CiOFWjX35xipZeAISVEIZWkqFDu45EuhWdh50EiOW52LRq74'
        b'zDdPLTSPMmE5aguIF7YlPDkTiYhkSEA1kzQPwni4i0M5zkKFd1rdrxgVPoEDds8FZ2tSuRh3eAI0knrOoiZZczLyU0kGa0w1apjDNVfAzRToXx7HgEEHwBnjGqZZYdlz'
        b'wBbWStSOnWYgTvAYOM9L5Cfx3VNRq2JYCTfCa5zZdWbk5DT0CfuLnsmWD7YlMUg21HOlqlPcWergKEp883fuOHN84NWEbagj8V4yjzRfNJ4OAuc1UrOZg96KF3mosPpg'
        b'H7ymIpK9zCCz9LNAry5+WMuHR+B1plMxggMc0JnmQ+wmckoAj3Q6fNjuhbGcV9hgryE4xoDgusH+SBW0CxyMSXsR2rUcnONa/r9FUf3X2zfYnF5akvirXRxCnTblxVWo'
        b'l5ngmtUZiNXcSNQ02ohLJT63jblKC6sWlyYXuX1IX81Q1KhF/N6ohxNBwX0lQ46jFrGNUWNTzcWO4qX7qxs5SluHRrUDekpru5bcptyWwqZCqWjUWihj0dbeCmt/2tq/'
        b'z3jUOqSvhLaOQBF18Ik1+U35DMoJRSRhxqYKYz5tzJcb+yh9AzHKQuGbQPsmDHNHfbPl3tmN0bdNBA/tgpR2AUq7qMeaauaTG9XHdSgH13bLVsvT1nsTGqPEJkoHl71J'
        b'6GLqfVMbcY0k6o6pm9LWESM4FLbTaNtpsqzbtgFKroc4ujnxvo2zpBRJaiMUc+7bu0mNpRWj9j5ijTEz63FDykGIqoWls9w5cNQiSG4SpDS3arFosmjUUIG2FI7TaMdp'
        b'jWq3J9kpnXnSiNa89pmtMxXOvrSzLw51UDq5S71aExROgbRToMIpjHYKG3HKH/Idtr8RoIiaTkdNV0Tl01H5OLL9mB1fWtFV3VGtEERgqJZdJKHds3bEyAiFtRdt7TVi'
        b'nS/L6YvozutbPVxBh2XTPtMVPvm0Tz5TpI6SiKa8lllNs5i9YIW1iLYWMaWP3uyLHfLqTxhM7U9VBKfQwSmK4Ew6OFMRPJ0Onq4IzqeDmVSsHCReTQktqU2pCishbSVU'
        b'WAXSVoEKq1DaKlRhFUVbRY1YLRpaNjz7xorX195Yq4jLp+PyFXHldFy5Im4eHTdPEbeIjluE0tJ+SSJP2trzRYlwZg/tXaWsVvN2m1Ybhb2Ithcp7P1pe/zIQGlji/7o'
        b'vmvt2BijtLRrCWwKbAlpCmmMxtvb2k3aGDQ2YhYkderidnC7PDo8FO5BtHvQkNrrOjd0RkwTCaXBjFGbPLlZntLepd3ipIVYfczSRlzbsrZp7ailQGY0aul930EgF84Z'
        b'daiSW1WNq1MOHuMa1BTzw0n7klpFktr2la0r28JoE+9DScgabJzGJ1H2rlgpYw5CmYZscbc2s6mt8IyjPeMUnsm0Z/Jw2ahDFopjSNQpy+yYqxCE0YIwhSCWFsQqBEm0'
        b'IGk4e9QuE6fz0NJeYt8U0BLSHNIYhXe5l+1dxvA9KEzdaVN3hamQNhXKRQkjpgljfJEsCoOrepO7k4ccX3e94TrsckM4ys8Uq902c1da2uDyUVjyaUs+pmvwU1rZKawE'
        b'I1YCmQNtNe2OlQDXgnVH1o0JgvqiBmP7YweT+pMYjNZI8Cx5ehaDiVCk59HpeYr0WXT6LHlx2aigHFWUNKZCWHHHJ1PuAlwPXT6ydGyNlk6VsTssumw6bEad/O9aBvwf'
        b'vkIWNmIaOSZA1a83tzsXowaGRK/73fAb9r0RNirIwh/B+y8+QjhiJZR501Y+d6yE+CPWHFkz5hHQ5zjo0u+CYSWKwEQ6MHEkcOZw6TsVNyveqbpZ9U71zWr5rJJRj1Ik'
        b'fYpK+kAkPU+IpXdVWmPz0hkzNldxhStMebQpT5p429Tvvo2r3C1l1CZVbpY6ZmovcZE63TYVKu1d261brdtsmzTGrF2lGjITWblM77Z1iNLBTWIm1njX1lnMGbNxV7Um'
        b'qEFsWd60XGHrTdt6ywJv24a+58AbNnnH/E1zeXauInvmSPZMuUfhqMMsudUspY+/WI1APEXtoa2hI2bej7UpOxcks4nFC/wZRgyo4ShmoG9W+5/DG/6bbgR3E8+pNP6n'
        b'nUeCFnoV0z/8sp56khbJYrFsn1DoByMhbP8GEqIGrza2aAipLt1Azr/Ev7n5v+PffPkDJsg3O1HGL5Bvek3sj5INRg+78kqBnTve+xB4+ogmaIr/zMX5L0k8B0t8kv13'
        b'JZZhiU+zJyS2xBKrtuXsqspeku1fLsgO1j2tolJm//bvSdeDpet+Vp72hFqP8MlV2JEEMUHkvy0jLjou655+0bN9zKKqvynoZSyo2rNidImwq62uWlxb/heMk/+JEkXS'
        b'6hVN7Gv9bWH7sbAGz4R1x6VasxQVK9kze7Zd9p8SmFim9t+2zKsv1yVB1kJM911dsZAwgdrNLllYu/Ql9vB/X9JKLGkr9XclHXxZUsvsl3mv/22xCBmw9G+LBbBYZ56J'
        b'ZfFcrMiEqP9QYXX+balefamwlnRR/2J7R7K3Z/3d7Idx9g6siUJxy/4LrvQJFt3/SBGhqqpDiEGLME3n3xP2Tdwf4r5sPSXObik6UvSCgRH2T6Yx/E81KVqMnEsX/j0p'
        b'3365kTZXccr+h2SrnGicS2bPxzCHooWLyqv/noD0y42zPxYQp8Lsys9/EQT0R7ri/1jnYvBM/tL5C2vK/94H3MYf8Db10gfgZP6tD/hfPDXoWdk9QzZwUquCtryhTpYf'
        b'hJqXnx/+oyZadJpFBY2yzz/9cF0+l0WcHWvgXjhIFh5hF9zD+KCqVh7b4am/OPjHEbO4mfxhzDm/vFq1XoHj4EN/5seyKDOrw6v2rpJPcvibx/z811kocC32oZgjfubF'
        b'sv6FM37+/6I46k+KU0vNrvrw6+/Z5AxBnW3ZRHP79or0f71G6UjYpnq7mSL8s06Wsf5iHlCycOF8lVJ0VEpZQpTyN7Xxf0j83ovqWPzvqwOjx7DZfruSmkCPIYWoqdBj'
        b'WttZKjp8Bj9GbTdUYcfYSFXPiO/XcLRfUsSLODKkFPZajkpVfwh9pqrKP6oKY9hFL6nKNpXAEApAa5EKpMCG6/1AK8sJSoGU4HYatNVKvlMxzdbWxVEMN1p/EjhcY7BE'
        b'G79wArZHsARGCwigY5WWmmCIRaLPD7JeSNV6UpjwYDGoJxsk2Jl6B+ivItS+DUlwR3IqZvvNTM/k57CpWeGaoBXssSVoFNAFt+kmJWI0Atj9fBtMnXIvBZ18dXB2kh2R'
        b'BZzhF6qgFxy9ONDEKoYndGrxAm1AIjj63Jkeu9KDrWAPGxwER0E/QVIkZgIJ3rwhO01qfCBZyAKd8AxsIDxvPFO4QcW2t2Il5oLZ4KBNkELg7MoAZjV6oVYq5t0xrOSU'
        b'54OObPK0NKuIrPryE9QobU2wEbSywW7YFs9IezShmOF8VVMDl73xVtKufIaL74QrXI+3Mbl8DUo7AAzOZoNT8CTYTFTkBbqKJ7h2fMERcJAFOsDmRJLmzNI1sJ6fSpaP'
        b'A0CHRiF7ynJPgp7yAAfMk+DuBHw4SjKsJ4XNUKfyQnRBmzpmKAKbX7Jd3QnbXYptV+cl233ZcieOb/jPWu2cP1qt7p+slp9KLDPWWJ3SSk7gIFPTezNhFUXKyRxuyiPU'
        b'MmAvbKM4hFsmB25nuBsb1LSIvz04BBrQM+Jxvxl0Mjo9vlSo2mEgGoWD85FSc/kExBMDLkMJ2XlEZruZwluPYNMSgjoDB+Gu6nSjmmQhqgtaLOtiAbEdcGR+mZ5x0jOG'
        b'D9gJrjP5HMPu3gy/CTyvgxl3WOBoqQGR3gQcAIMqBpvpqZQaJrARgg4GT7bNCkgIgU2fM+awmWCwyeITqB4B3+nBk7AnC0feCdrtKfsK0MZVV1lXtRF+Wc/gxXfhMV2S'
        b'rx04C1tUDDKO8CSlhglkRKakFoGOOLBPRV2j4q3pAxcwd402bCFpz0NGdQHTaDTALZgdh2HGKQWXavE+h4Ur2MhDmQpQTRJwwR54mJ+YgsF3W9QD4CEbUigaYMekpOSE'
        b'NWADN5E/wUJjCPuYD5fBM+AoQ2QAu0A9ykBDi20KOotr8cbUAijV+CMbghY4/4wQoaIKbKt1RhErjeFVwpyRTDaXcbsDdoIBuIFUHJdc9Xmgex1h8q71Rlqtf5kPYqH6'
        b'H8gWUsEGTdjIhdeIvqfVgZNMK7QEXKEwAKzWi8D0kitRq4UbIbAf7n3WEKFGKGYqaebS58Cev2jlFoL9qKFDrRxoiiQqCg0KnmipkK2r8XFDdR7KGOW2wSbYSPhGULvd'
        b'TOymDXSipgOLVhqrx3BrwPNshs45cylJsgYcd2EaDi1CkIIbDnjZlzwD10CbkGlwwI5w1Oag9mYd7CXtjTY4g9kO0BssfyrGFTUhDbCNAc9dmL6Gl8Lnsr3hRUptNqYn'
        b'bYKDJEHvKoMkTNp2ZhHfA5WeFjjEXg3OORI60WlJ5rznFBScjBdIKOzgCeYT+8HmOBQJCajitcKEMLBVl0GJdgeA83/Z0IHGfNTWqeP9vWsq0B2nGJyDvXNRj3RhmRrF'
        b'glJ8+OT5YvJp8xKBtAZ2a2D+GQoOWIHGIDBAqtaaDH24H4dfgkc8UMPaAltJhze7RpcyCXfVpCYVewhCPRmi0q+moWY6uVUTE8Ged1jOBN50U0PtlRELd43lgZFMYPY0'
        b'fcrMxI6NeU4/zFjEBGYlaFOTkvXVqeJivQdaBi8PLjgT7SHezkxCzSeeaRSiodEa1mrWclYNm0WVUYdYh1ksqkFPDbWXnRwCJEdzYzJWYt9jCzzvsZbV4CGVHTPTuKcd'
        b'XFleXb580ZLQlcF/XIddWr6kqAhNPPA6QU2ogNwT5PLzsGdvl2sjs8KV9jM8UJNHF9MziuRZ2UMZIG/YCeahu5/IsGzjpMms2nBs/nBQiOGGcM9SzILBFyQQlpjEjHR+'
        b'TvxfKBT0sHVYGKl6Rq8YXENmR4YKA1PAVdR4c/mo3cNMLtvUVH261XQ1pGxUE6o+bQng1CxDhbduxa07uQVpxhEmx8eqvz514H3JqQNvXNpo/4pZaXKUfNrc22al2zMc'
        b'5pZt9vQJnm8sLPtk12GXXY9ifuJcn/57W+XlHmdZ+1HujyW2A1dED54c+7o5RDT6W3yo/YHmfamdCaklQbqb40e4NYmrW45fT7zX4X3vjPEHm5uc+VP3tUZZXucv19EG'
        b'/LDcexu9r6jV/dPEbn4YqNIumOGxWu2JzuuOa/X22Jdq/67MvTer/ZVw4ZaG2f5OW/XqF1VubX8qqi6fbzQ5Xb8q4rJ5mEZzjMbbF+Jfudqke+zzj0tM3ioZOlrve/v7'
        b'wZVhDwM/6V/2ffukWWPKhTuOc80vDEX82rxpp62jowM4+9pK7VO9aWUmM3zCTiQso+xKHXyddOsnH/ro298CFi7orapLjf7JYbL1nS8/X7Nx31dbUzxGuO6H3QsW9ZWJ'
        b'czcr3mr0eDU34zd90fVcVvG5Xa8pe64mbzrTTkdHr9vzPbhnXf75WlPZ4tn6A0/nvjej1fT7W6u8a867dt+5uLuhcIFzqp77pJ9fn6JVeIKdp9B/5Gf0Gr/sS99/2H38'
        b'1ZXh5ob6vizTxR4DtgNZG3y8d7yzw//NjuSVP//6ZfYecP7B1R9Wae44OEl7renjhlx+8sFZNwpbFt0Z2GX0U8xbwoFf1R54fsgpzRT57jLPOrJ4XfQe5392n/zpLaOf'
        b'yt8SzvuNU/r66JHHw+IMuuH11xrMn35y3KGhssK9sWqXwejy6i9Pnjl2dfydNz66HnlrYLvTg8hpRQ6lXbdK3jwQH1CT+KDwqXLHQZ17Z99JPW///uWnpYuug37719lt'
        b'u2dXv9W8VLHg40/ekg9/PjT8+dmYrceq7o4+qdD4es9473bfEdclMxv2yDc9vZMzerbzrjz3+9WRxxSS799Pri/85ZzZUZujXzuIA4TCpg3z22NeW1XxLV9Ze8x87w33'
        b'N/dVHoxccVE3+fLD155+9umq75ddZl367MQPnHTDkAPt/fM6rsSuK8soFPbNWPJ7zbmNv2x6NLAErO5auO3Vzb3wF++c7tDv4n75TXBrgf5cowMfX4vgb3S/rCEt31KS'
        b'cOq9t1e8s+Fc8z/Kc8K2rvRZ895X3489SmwHBWunLHvv6hdXq7/Y8vM7X+3e+euVg3l7P26Z9Ba9bN5MuKj3UMBDW4uSbx0Ul6Pf37GzefjrvMZPd361pSO1ao9N+CeD'
        b'n9W5627cDq7cEBpn/JiQxnV27f7qQsr1vWGtwmlrfzX90tvn4lcsbgABJZmlYurG3UIgVYPr00i3cnUmw1cVaZkCL4NzunAnN0HbDXVIaBhsBNo5oDkc7GJgOGADuKzr'
        b'zoUXZsALBD2mZcnOMc5h+MLqwcXaZ2xzYJMOOJ8F9xOsyyq4oVoFDpsxkyLgMBsdFQHZXNDIYPecQT9FoHs58AKDrmoEF/1UwLHlcBPF4MacYL2K0weNHBonxnFbwaBq'
        b'IDcTbCJvx5pEkS9ZnCzkalD6mKy5geMCW3IJqhMcNZ//AtdcDmx9CTXGYw7404FHQauRZc0LlG/+QMWcdhz2RBOqOCeHCdRYCdxKIEHlvuawEx7XJTQ/7GxWqGEVAwjb'
        b'hcnhJsgVYdM0cBXsjiGYnXIgRiXvJgBbEzH/4TPuQ7AHbCD56S+CKg7BIoiGzoRCEJwREDSZPzywtiaZ6wHbGKLACZrA1GKitZmapnhsuBM2Q7EHHuqdY4vANnCVoXM9'
        b'4ws3JXm4LQY9hKaUoShFem4hjzXhFTDIEB+q2T3nPQQbFzAqOgD6ojFnYgZsfEaZCE/DPhWGNd4QlfFOPNrjgLPalFoAC3RngTYiVgJmStMVcB3AeYazkTA2uoSSh0vA'
        b'YXCtBu5M4HMTYG8Sm9JczHbPBYfIQyNwEl7XdXOHR6GMkOIRRrxFJQzrWo856MTwKdALBxYz8DSdXDYyll6wjcFHnQDHwVVd0LEINpTDDXws9xEW7ELD3A1Ef7pRpo7g'
        b'Ug3hhsMALLDLlNH5KUtwWjcxhacBdpP5ywAL7J2TxVCPXgHb4Rk8Q9EWJAmgBHTr4KmiGbik5oc6wBYSKQJsB9dVHFegI7pIxZpngsbycD+4lE5gSQLYE/Wc3a4ADStf'
        b'oLdbPpcpHt91hA8O7lpIKOEYQjg7BlVcJixnuKw8tCeAsmBnKVmk0wyCm55RzjKEsu5oLIk5ZYNRHbdmxp2dnqRWzIOXMDPfc16+Y7MZLNwF0JmgW6uvzS6GMopjz4qw'
        b'BGcZEF99LLiKyQ7hRdgBO5Da1GNYcJePAcOSCDozCI8ZmkPg2oyJzBaAViJzJuyDg89IXduzgBQeAycY5G8bPDIbkxRqwAPPSAovOBLz5NbBfkKAth20qvCsmAINdCYy'
        b'JJA71csIAxpsAT0oR8KBthUydKYicNxbxYFmaPESBRrfksDkpsBL9oE+uhNEZRGoYcFKLF8NDqh0iHPucH+RqAy2ZpAy0oMXbTFRGdyWryIq04IniEzLjMBe7MXkAJqR'
        b'BaIv1kxi28PO6eRbrVPRgJ0Qp4EeSyQwZk6DnYUMDFaMrKeJIT2uXTOBJK9kMyjaPSYA1SGP1BrsAwT3oMe6qCKjCUoDaCIxairwrNcjFY3jUdPNhdvJyTnn2bDNC+xm'
        b'SmuvB5SggjiE55qYNLCVlQ7Xo9pKyCQbS7i8NA+UyWVUofE8SJPShdfZqFbJ4HmCWnVa6gN3w6267nA3BzuATQMHE5g2Zu+6+S9jjr01fDia8Ew5A0iVwfXwiAphfwoe'
        b'f4ayZxD28Joa1/5/H4X3P0FY2FN/5kH7E2KPGe/rPB/Fr+T+jwf8ZBG2EM0ifiTD+++i41mUh49EU+nsgSFpbbMkbKWjq9T7RKCSL5LEKj28W2Meqq4kMUp3LwY9JdF8'
        b'6OgsmXsiVJbbO+vCLCXPW+bbF9sdRvOiFLxYmher4CXRvCQFL53mpY/wVsuzC+QzS+Tl8+iZ8+js+YrshXT2QkX2Ujp7qSK7js6uU2SvprNXS6KVrjzp0q4VHStGXP2V'
        b'/iF9y2TqUg2lh0jhEUx7BPflDJX3z6I9khUeubRHrsKjgPYoUHgU0x7F31AUv4AtL5unKFtKly2V164aRxMFVjT7MaoxzJ9yVgz7Cf6TztylM3c5zF0Oc1fA3BWwJWyJ'
        b'T6u2kj9NltNX0V1E82MU/HiaH6/gp9D8FAU/k+ZnjvDXynMK5bPK5JUL6FkL6JxqRc5iOmexImcZnbNMkbOCzlmhyFlL56xFqfm26pDUOoom2JOiaH4Uk+gIv3Q4Tp6d'
        b'fzNNkTyLTp6lSC6lk0tVL7l7yVw6hAr3CNo9AmnK049hSYmgPSNQjIBWfaW7Bwr3EHWlnUtDRejmgXmszhjKMhWuobRr6B3XcKWbsMugw0C2tHdF94o7bhHj6hQ/+LEG'
        b'5eWv9BBIV3SkKLmeXdYd1gpuEM0NQmJ2FXYUKvhhND9MyRN0+Xf4q1JQuAXRbkEjbhF9S/4cMq7O8XH5luJ4uD7RoNz4rbVtdd9ocjz8xjUokd+4HuUd8J2lgZcDI/S4'
        b'DeUX2lc5rEGHptK+aQrfLNo3S+GbQ/vmKHwLaN8CpFG/CLa8qEJeWS1fXEdX1tFFyxVFq+iiVUhTxawIrCn8B6UXRtuJlL4hSFELFb7xtG+8wjeNJJpN+2YrfHNp31yF'
        b'70zad+ZE3GB8GlH5jTQ6OFsRPIMOnqEILqCDCxTBxXQwtqWQGGxL8vk18mWr6Pmr6LLVirJ1dNm6J4wZqaxJwpY7+tN2AQ9R6dl22Cq4oTQ3VMGNpLmRI9yMocrX592Y'
        b'J9EYc+RKK7rmnZk3JgroIzi0oWXDFTfWjopy5HmFtKhQEilZ3pr80FWAydkkakq/IIatSeGXTPslj/iVydMz5VmldHoZzlBE201DGmK0o+BH0/zoEX7mMHvY96bOhJl5'
        b'dRVhM4ug+RHPgwhvFyY7UwUJvLvmdsztWtixcESQPDR5KO6GJXri16qLIz/T/wg/Zch7qOJGoOqtCTK3YJoXjIKmtWrh6HkdeV2zOmap4ghFXSs7Vnat61iHAvxb9R76'
        b'BGMcX29Rd5HCJ4H2SRjxKRvOZRjziuiUIkVKGZ2CPk4SStt5Y1O06bCRaCg9vRlTQQ0QIzxTYeJofpyCn0zzkyU6Y458pZOLZEVrisLJn3by77NQBCTQAQmjAUm3nZKV'
        b'Qh+GNyv2tjBWEvdyTNNBq34rRUASHZA0GpByxyl1nEN5xuFzrAXTumaem4mau5fiT8HMas9Sv+OUjOILAh95+shK+sy7F4x6RqukZeRXcENobgj6Cr8QXOl613avHfEr'
        b'HJ4sT55JJxQ+U6Sjs9zFd9TRr+8FlKU8vXAkuHB8EiX0kntF0IJIhSCeFsQPG48KUiRxj9z50sqzHn1GI+6BE/V6yW23wMcciidgnoy6ByJrki5uXalwDaBdA267Bg1p'
        b'DrNu6CjCM+nwzNvh2egrI1kJrGGjGxbDufLpOTfz5W6hUk0Zq0NHFtcX0Z04htKqOxvc5zXCC1aKAnuDuoN6QqTR6FIhiqFFMQpR4ogoURkSIWPLfLt1Hrm6S/3aVssW'
        b'o3a7P2vIFCd8pUienjESkoFarD5Wt47CM5L2jLztGT1sKs/IvGmhSCigEwpuJxQqvfz7jLot+paMeEUM5Q5n3MhXxOTSMbm3Y/LGwqJpsgI1Gl08GlYsZct5qKkJfugm'
        b'wJ8t9yvApfuc3UxVuN9xWNwirEied5egQ4DaRnevLl4HD98o3ENo95AR99wh09ctb1gqIjLpiExFRC4dkUviKdwDafdAhXsY7R4m0RxzdO+oVAaED7nK/RNRNV1DO/k8'
        b'cvOT+8fTbmnDkehHov7Q00+iflJf6cI7qfu4iIO6058IX9KmePViIWtYO9MC/bnnFKuL/qiON7unvXR5WfnS2VXza+5pFi1dXjK7pvzfwWiqDjp7cZTA7JgmqlPU3xgd'
        b'cPDaXyB68ef11JOoeBaLZYePPLP7G1up3+LVz6MaPOqsri+Hy2F8pPetAN3kMIjdFFUFN5CzINTVmYW/q6DROUnlfpg2cSiiBdgIW0GbGqiHnRFkjwAOooHtATTG24PG'
        b'pgl8sDNNlZ5tEBq7n1GDB6ySVavDaIi+W2ciO+08kttsOEiOmvKH253+nBsUw40kt+QQ4ngPr88BR3jYOarTLR4egWdTBAkpGYuwx0lGvIq6m0UVT9FyAlcW1DJOaPAA'
        b'vDDh070M7GTcutkLwGWwl1ngvu6It4V28dGkPpsk5eWTEa+SMtAJXs7VoMpEhKdgnQPeKNiFF05hA2x2SMplsnZ7YQt1JjiiZRi0hLAj6KoX/3XBXDBE5QK3wZNkDzdm'
        b'srDmD+lMV51wir8Jz90r1sGN8JQWmjNcgZ3EWKsqJGtYNVEcitrtdu9a7nvzRtNNBl1TBi6mhClq5+X2Br6yy97Bwd17q6G6prGtWkxZ20bFxjr5trJkaz+Jgzhx77XP'
        b'wn/47N3xvF9Lfy0KTqjpOXC/76zxE3lDzVdf111Pqw49+L7CV7sxyntmmdNPCmfNsQXbJh1eBC6aPDW+DRftNk94uvjHpT4GHkdvi0TcNllP5PZjrfe23St+arioaVK7'
        b'Y3VV76Sb+rW71wTX6X34+wP2Bx4+95MWnQnve+2NyYMXNu6dN+3K1rRdel8MF2Z8eKjlZFbKryEG87zP/dOSNdjvG3v7tw0P+sUP+ht7BR/L16evvpcSH+DYmft+l+kS'
        b'U9DcHDU/auOxrI96on0be8x+fvfnVaENZzlVVgt8DPyMXzkY8Fg/T18reP7uEP6W44J4s6A3jvva7Yq6m2HB35Zz2Gm77j7/ped76t94/+STbOe7WQeHNI91Sh8PaPh9'
        b'6e23KKvT5dKNL3OzzuVsmd7C4eeuM37qvOPLC9F3M7616LwTOW9yhd8XXzxNXbR2/NzTY5VjB0XKfW1dv5m+Nu+Nhsrhimn7Kx9+9sUJl/cv5j6puLrV74u3Vi1YSJ9d'
        b'cWzt8dRB0XsdB77qO36g3+Xt5bq//Hh6iZ7Lj79UHz96Qtj2263ZdQ8SS77UOb5wSWGzbm/87n8EFUZ/rGm54f2yeZNt7zp7v1qX1peXfOfbDKsVx3uLftl/1ynjTvKy'
        b'AnDC/yl9+4P3/Q9mLc7aYb25v+Bh1v0v572T8cOU0I0F4nOGNTXC797WNZlbsbVnjWTqO4/ZnbblkQ2vplR/f+K8+f2jHw3l/xR05tqqTzdzZTr7L7165m2rqtK33Vru'
        b'FjcdTU1SpsZJTD0fxdgvM57bfH+B7B1fp7x7yW98di7cev23ep9+UP3NrR8Nhmp7h+vPTAmhVlnXzPn+0Ba1b6u+d5jm/V5uaWbvmEIe+d0P6a/PvmzjcmrVK79xFVLR'
        b'L9e+PCQzTvwyIzPp3ROOV8p+0T3uoRkyfeqUxR/cOVb/3sw3v1y8760qtc8yzzkuXqXkee3+pMoq+0lI6grNB+G+ZiEPp767L/pB0huvPGHFbvvpHgjaV7D47NWfX5Pw'
        b'Z405GjTs/Gzb5l2aBeHVOzSzQvLvPH6zovhzp6kPVnuEfiGyYj80vfVZx1e/f/X5R1N+OrSC1f+bcOpNvR9mN3E9vxPipqDXC+z9L7wb0RT9LOPhyLg3wiPzVQcWgeuw'
        b'fcKdkgMvWbmxwHlwzI6ZeZ8GLbBftSxLqflGx7DAVU24jWGR3wCk4BLjz/fMl08PHOJkgEPgNLMwtcmxUuUArVYJj4F+FtyaDCXM7HpPjcEf3T2JryccyFaDXZagm1kU'
        b'22gI9kwsXzFLV/DcFLx6ZZbEnDMxCM4vTEojx/GCfaasCHgM5UCWNVvhddA0sVwG95ayHBPBIZJ5dBi8ODHzx58OLzLHRMCDi8E5NXBxVQxzWDBsX6vrzmOO7Uli57Mo'
        b'XWM23GTvTb7OHdaD69h3fDGXRXHATvU6FmzOLGPy7qsEO1XOjNPABbxLOQCaGR/bk2WeNWTxcU9qHdfNgEXp1LHBWQ7YwDj8d+XrqpwdOWBLwhLWyqQUsuwDNplM1RUg'
        b'/bFz5weyguDBfLIoCHqnVUz4a57MooA0woo5TbgXXmVPOMPqwtMqf1hOjDloZdZtujRAAzlsicJwCHhuDQtsLIbHiHKjwFaLZwtyQlQAzw95cgPrme9on4eso0fl9w4H'
        b'wHpmSa+Jwd2Bo3CTpsqLMcjxJSdG0JA24aZ8itDvTCw4ASlsYds71jDrazJ42BOvr2HLBH3TyPrafh5jtu2lYFcNPuocO5pyQAfsnc0CeyJLmSX49bB1AV5F34UXujng'
        b'IqoCB1igCezlE9Hs4DW4T1eQsoSJshTlbWSSD8ScuUACmTUn2AY21eGlWGahVksfXLRil2VnkyWr1aheND07acoN1a0NE2dNaU8jfsZz1qLa8Vc8CDaxKiaECRqEBhUN'
        b'wjJb0I9NdTFDvRSrWhyeA7rIBwcmRDELw8iW0Xilj1kZ5sMrTB3YzAXbyQIwXvxdGc8CezWKSSEG6jkmTYxHKuAlckbYADxMFgw9k8C2l/gj4AHbicUt9GQvybgUjZXO'
        b'oREGU4nTwkE3C65HlZQ5oADuhw0+E2dWISngbhbcNBc2M0tzG+FxsIPhX3ADXS/RL/RXkzVlUc3CFxbgyGInizJbCZrL1RxAmxv5hIxFxdiFlxl9aPmDbbXsEnjdiPge'
        b'g0Mr0BCrPu2PQy9bM9AAz6nBM1PhDtUZWUbgMGOs+OiwZHB8Dqp3yWzQaA4amKTO4HN9UFp4sAV2TCAujGA7Hhd55msYl+l+R+ietq2DG/66mZ3wEob9/hqpPqDxO9WR'
        b'qMfh6WcjqXk8sBPs0aQM8jlei0AnIQvAhEqNSS9nTABtcHukuTqy34urGc/gbUvIguSeNLgjWQDP6uNMUVIcjj28BA4ylWo9Gnb2kSMdMFvGNLgFE2a4g2P/Vxcrtf5v'
        b'L1b+gSaWmYfYsf/KPYzMQ8iKZBOap/xEViTHl8eyKBuHlsJjhY0xxB/zlIVYXWnvhkn922zEGtjHM6wpTGEppC2FMt8RywA0h26KVlo7PHd/leWMWAcpHZ2aoj/Cfptx'
        b'w87vCG8KFYmzaPRfOGvUoUhuVfRQ5M9w8StECbQoYURUNZzzTj6aCM+YM5pSJdaQ2wppM88xnpfMuZfbze0VdAuGnF/n3uAOx9KRWaO8bHluAc0rEGuIl9NmbkqugFk8'
        b'U3DDaW74CDdnKPb1xBuJw8tGo3NQnGVNBkqBCDPrjwii+paO8CuRUPybfEXiTDpxpry4gk6sQNFW0mbuYzy82GDZbzlo02+jCEimA7CzKC9rIicH13Z+K1/h4E07eCsc'
        b'/GgHvxGHzD6fwZD+EEVQCh2UogjKpIMyxZpjXF9Z3ZDaKDdmhJs3PFWePoNOyFPJwvPsCugIeL6UM8JLHVJ/XfuG9usGNwxUOT20c243aDVgaMyRErgCZmEjmOYGj3Az'
        b'hzSwC+2w72h4pipRFJ/QnnvSdp5i9TFbJ6m6zKTXttt2xC1c6eSOj56Q1o06+YljlO5C9E5dkyHSQm9od6hCFE+L4hWiVFqUqhBl0KIMhSiHFuVMqOEhsgRkAEj9tnjB'
        b'ZMTWrz/2oZ0Lzu65iEomgMmfCVLY+dN2/n94EEjbBSrswmi7MPxAr1Wv3bDVkDnvY8QuqU8dE9APGvQbKPyTaP+kcW11fxtxLF6vsZr2xGARy9zjewr/jpdxKGf39tTW'
        b'VIVTAO0UINYec+FKnbv4HXyFezDtHjzinnqDM5QADUZd0sS6Dy1tFZY+I5Y+Y648aUzbqhHXGNm8oYjuhU3xjzUoNw9pAkOsrfCIoj2iFB5xtEecwiOZ9kge8SiRY0/b'
        b'Qjq9UJFeQqeXjLqWiuMfWTo+FEyT5eL1u/wh89dtbtgoIqbTEdMVEfl0RL44VuLXlKbki2SxHbNG+AV9KwbX9q9VhOXQYTmKsAI6rADF8G1KHXN0lwbKVtCOSUOx6Ecc'
        b'Pcb1kOadtcFu72NOqFA9xzls5xClf/AwT8n3eqyObh76BJG/4phxLYrvK445ljJmbScxPzpLunjE2vMjJ7cOC6UdF73oHsUa8/KRlfdYKj380Dvo/mFQBHPxLcV2jmY1'
        b'xaDPd+A9chLJp0WPUyznXNbNaHlGzptJyvCkxxx8r0ybzlyg/DQovjfOj6nZow7xcqt4fDyLU8uKphUKWxFtK5Il3rENQ2GuHgoXP9rFb8QlvM9HHKe0dWlZ07RGYes1'
        b'auulFIok6if1lD7hEvXbdt4PA8IHbfttFQEpdEDKcN07a26uUXHx+5fgCD5KR/f2kNYQhaMP7ejTZ4LXAmnHKKW7oMu9w12W21vYXajwiaPRf/d4SZRSECgt7ZrfMZ8W'
        b'RPfl3BZES9ljQm+Z97m6+96h8rCsUe9suUf2uA7l6a0Qho8Iw/FT0dnlffZnVt/3jZRHFYz6zpR7zlTyhQp+KM0P7VtM8yOGsl8vulE0ws9Wekx7GBQ+GNofqghKo4PS'
        b'7gZldCRJo2XOSuE06ZohA3lmzkh4jjIu4fVVN1bJs3LpuBky9V6DbgPU8HhGj6tTwZksVOhcwbg9JYxhfedCCYPkQdNHBTlyt5yHNo7Nut/UIJ14POZQNryfCHP65jz9'
        b'fG3W2GQ/9MusYk1iEPvJ6n+C7f+rHcqkP61i/Q/6j/cm3IvxmlUdRv5bYvdiS+xebPl3fAC+xxl1Yt8zsyXr8PV6/LMB//yMfu5NKcKsqqVLmaWyIkyhWlVdSTyfl2zE'
        b'P0exM5IjB0XVVPnF3tN70fn0nu4Lzp1LBDj2dvzeL/hnB/5BUwzqnvYzv7J7mirXrXt6L/pJ3dN/yeuIOKkQ3whSTNwp/++2K/GQ9i9Y4Se01qSGtPYS2bQfVtYaJOqP'
        b'mBReT3/SuBXlzJXr2X+gb9Lk3MoRW3aUd0f1m/TX3sjqm3fTh87MpWcUyDNm0rNK6LIqeu4CeWm13H+hnL/otv7iJ+wiln7AEwr/Yh73JaxxEvI4mjPByx6HedkTWNuj'
        b'kblbOIxN4itNvFCQhWh7IgoxtR2b5K408UMhpgHb41CIldPYJKHSJBiFWIVuT0Yhlo5jkwRKk3AUYhnJ2p6EglRpR+O0Y5m0VUE4bRMRCTG2HJvkojTxRCHG3tujnseJ'
        b'wHGimNfM7MYm8ZQmoSjILJy1HXcE5vZjkzyYlMxF2xOeSynEUnq9KGUqljKdRcS0dh6b5MkEWaOglO+0WPqO32mw9K2eaBRw9J2eUPh3nPwybLJ4nBquA5tr/jA+ZlHm'
        b'UKpWWVkuDHgJtfqMuRb7xB3UJB5KmGucUrnEaFdoPvNWUvuPeSv9pQvMy95Klam1aejabHqxyHOat6+Xjwj0AtnSpUuWLa6tQdMIGbwIL8DLaOZyCfYYaunpGGjr64I9'
        b'aDbYAPfBg1npaG53CVOo5qhTEE0JdHUxApWUz7rF4PKUcIJuredhli40j63nUMbwGAcOxOnW4lpQls7CYF4veLSA8gJtRgQPvS4fbiKReRjBvHEJeqWLg2YtG+GAPbxY'
        b'i6sHmiBc44rQV3inRVHesGk2eRGcBTt1J7JTvYkyu4JmgwngMsPPexxcWy5CVV0EB6PwDzjLAKw7HZNRduRFe6Q6E2ckJJp1XSZeDgl6sEOkQVHTBPA6mmwcAjuY/MRA'
        b'Uvb8AzmTUX71HIDzA73u5APB+skrRMgSfMJMKJ9MMMBw18rADi/mC/FrbMrEmFODinrAZybJDorBtkki1Df4gs2hlG8ouE7WyTXRDHYvk5nqNRYH9EIJyq11HSkWsKNc'
        b'U4QaUT97uInyswFdjAtDA1hfqxJTE7TCzc6oYDCn2ADsj2Ey7AHX4AYRslL/ukWUfza4RlwPkJyb4TUiaFIOT9MRZ4gyOwylpCyRSdTDa6AHXQZkQDEVkFtH8vOHfZoT'
        b'ZYLKw4HRXx88CAccKhktdMAt4CDoQQoMTEyhAqsB40oBz5hTKqXbJeuxVbYCztsTKc3gASDG+OnINUBCRWaDg6Q0F4H13iQ7sLcKvetIlIC+bTc8Rgol3RuexWjvKNCH'
        b'f3YGEt3BZtABTvGIWXJQoRwFG4OxHtCLJ8E+kp8/2AIGUV9ORcMGeJyKzk8ndo1qxFXQxJQn/kjNElKaqLCuwgEDU8Y+m8CpQOzbFwM2p1Ax6XmM3i9U+ZDSJK9NxsWZ'
        b'C8QoxyNmjDPN4XTQW4P0HgulwVQsaCwnGfJsAjMhoTJWWSi+5DClOjBTjdHFBnu9GqT5ONgDpeh3ALaTPZswfGI8iY+qzwV4AVzFum/nwCZkSgMZ8CTxkTBGdbm5RhNz'
        b'XW8FHVQ8aIP1hBEXVZdLQMKohHk9mOQLOoLhgBAeYrR5BV4qg9gMEjjgDJUAGjnEDhKheKZKamx5JUSdQLoWDlTDS4w7WAdsh4MYwYki74NXqERweRXZlmGDRrgZ9Ks/'
        b'L2bhRPNBlNu5gMl6X5UJxGzbSXAj7KKSVsLDpKRZoNEKSw13AynYBC8smXhvkz/RjxE8swz2INUmg2PZVLJFHflaEarwl1QSkw9W1ZNmHcyHCI4wSuqGbeAU7EHKTbEw'
        b'oVI0PRl7OiuCZyfMCb0aTGrnNSTWgAg2klIuhlvgNdiD9JvqDs9SqfAQ3EEKqnRt5bPv1AQnGA2BPbhmawYzFXS/ISphpN80cHIelQYHZjE7Zw3g5OoJi9IE5+FVe5VZ'
        b'wA0LyYeKwqJgD1Jsegzsp9KBTJ0Uz0p4LZJ5J9IObATHn9W0NjPGmhoT4GXseZYBTjtRGfA00jTOj7eGeAYhY9qArQFuqsSyHiSVZhnJj5MBzusidWYGrKAyMacdsWDQ'
        b'D1vAflI0zIsH4N5gVZ7w5FKGvxzlsk8XqTLL1JrKAifBdoaV+7KxObxOjhetf1Z3sAsfo1BU585MOKJtAd26SKXZ4EA4lV1QSlRqZwRP+k15VrqqFl7V/EVMdArSSHBA'
        b'Fyl0uhfYRU0HW4GY+PNwddbh6Ha6HLBpCdP4WaD+gpTQgQB4XBepMgdsAhepHDd4gbBDw+Zq34n+Z4MnGFgyoY/zqInDHQLcqRunixSZC4+upXJnqjNecX1JsBOb+FXU'
        b'SO7hoBGYH+4jwxnpTsGTXrpIhzOApJqaAXdCxrMMDqYWq8qEA06Qio3r1yU1VCoD8Bzjh7fNQgPUo4s8ZHtb0e9W2Ez05B0ENoN6pKh8f3UqPwZuIVlVGIBzoB7poKAG'
        b'bqMKkLLaSOHGpGfC/eqYlvKQCyWAm+FpElxRGg/3o28RpsFjlBAMgnMklUnIpOqxG549PIn6IXsKRSfCNOLl7v0oeSQ0aEG/p7VrDdGDVeHTs1DpO6chEZ3trYiA81KW'
        b'w/3ooz19Z1GeYD/qOUk9OFUHdhFHJA/jZZQHOBtCgtVQN3QhSx0zJfYup1xKYANXp5ZZ4W9HjbzwWRkF444dSJA9Dmig+kwa5c2aqAGbGKEwnTE/AGlsy1KSxGQveOR5'
        b'i8AUM7K8C4vgQB68RtSXDa/ymJ7cDu5UYzHdCGgLZ/jCd8B+s4nOEL1Zgg3JMxMOlIGdJAIX9nKfNZJwo6qB3W+GDKCGqa0OUYwAcAMy9xa4LVjVEXdlM8OQZnDahzFu'
        b'8qElJAU+2Io+4ro/sRU/2GjyvP5oRjKmIkP3A6AbXGIEvQ6u5qlqSifcxtOMmqhjkgQui/TPofBgdhLc4QF3xPO9wWk2pQW62GBD3qRPyfCycUk4V4e4cL05jYM0Rw78'
        b'0ht0Wsb4dS2eo08tSvOlsLNXQa0LE7jWQovqS3LAk1cPnmsyE+ioaUyp6SXh160KDbOZwH8kqFObc6cQ3+orVTFM4PlQA+ozo2BkJ8V6v2cEMoG3CjSoPmsksF2x3ic5'
        b'6UxgR4kR9Vl6JBovFOttK/BlAj+P0qU8jYUUdl9bOGMxE5iQZkLJJ2fgjILrvYOZwJl1atQ5PxMcmDzDwZ8JvBHIphr9yGd6pE5Hr2PHXFtdU+qqeiHOPfidxCkUl50d'
        b'Sx40m6pTP0YTtn+9PnMdJnZ1oga1aLIZkbXau4j69EgT/nczjGRgNlWT+sjEljy9ZulFfSoi/74NY/zQr6GqeAT3itRC0AkOod92V6aetFhr8TQxMfD5WPQzCK4xXrK4'
        b'EZ8DTiX+2d76IpC1DDJe7GVmU9HIfAbOdbVeSQDzrfRCE2rYNJeUynJDDSbwemEedaCmgoW0F9i5yh99a2pq1cDHl9RqPJBQQ2/FbTlws8YyxuS1KwX7Ot86VLZiWv58'
        b'3tvs2Qkz2GrxwxutD/lrJ5Usij+g9t30mQ1nlzR2AOmsFv8dR9ynmr7qrGhuHtzOyz3zo+k3KXtiM+wjsn0GP//4Wtfg2vfaHlT+ni7PWXO2uPGeIt4x6u3iQ7cc4j7J'
        b'sKsXO36a4fCmtFFXuq9+fNhi9YXdGmPR9TOBd/9G3xVaZz+abTWmmPmp2+7uJ1bHXfd8qP5NzNXo6w3GHyVcjby+UzGsWLxzNWfhvoWPpv3k+779g1fNv/F43/GdR8Er'
        b'WKY3n3THnv9w5Prak49Zoa/E/Wh2uHsDr2/nvB/VWkJvhY3kWPrMsL6o+eaGI79ai3+8VvBo9dwla+Wh8sVftP8gsS5zcWyc/cmtj3788J3JCw43HWvoe2vFvPk7e7Zw'
        b'39668Ojp36P2gU/XxDpXz9dQKO4IT9ds/ad5rNXsV3atncVt2pvcEtrm6/s45n6Q2VdvfXzOs3JZwdi5N0U7Phn4h8diF9ex4uqRPSfLc5JPOveH/qL//e1dOY8S8x8l'
        b'nfni7Qe3h7OuUeX1tM5qgyTfHbsKd3euOP64Zt/B/nj67aTrh+tXNlieL0kybLhV4v/uvltJiz+9mHlt64GtnTHc5G93WqYd8+oxO76PffmHW8erXjEQj6bUvpX3A6iv'
        b'ejVP/U72ZY+PJd89qIy45O24MHYv3dF37GBc0C9vTA8MaN154NTGgvMlB0H6mtxtg2tyze8sPfCL8NS7dF7cnkKz6bLGW7vvvF1ziffKpf1brN+Xhrwnym/taa9re3Js'
        b'zt1/jn6q/Z7+mazUZSfnnz3X/mTdL+tOA4fL51yn511d+NnXwvbPX62sCpl/L3+3xd3Dcx+m/ePh8dv7ul67e3LrW3PiQqxt4NbOnt8vjVbJpvDunnz/Clc/t2XuBzc+'
        b'ntm2LXa14n5T3bLdNUt3lT7ou3X6M4lXueutfRX7beJC/5H5+tY37xru3imsPfx1Fndx1tc/ZYWYtK+UP8r/8UOl9fiKtstHgt9qKSjs6Rw4DXXePSSV+LxaxMt7lGu8'
        b'sir2XVprYM1vhmPOjzd9zG1KPPTa4Njxw+eSP+V94Pzhk5TDTyp+7T8PwkZ/vQDXxRufDzyedNZ2Upzy7hP33qdqzd1G/vcbuIYMGOFSTgTeIUzBzirJaeqU+moWPLmk'
        b'nNks3mxX7YP6CoZ5WC2eBXpgB7xCtoOzS2BzEprz7OEl8d1ZlC48yskG+9ioB2Y8H+DOQFg/B7SjxHsgnmRwdFheVnAnk+tJcARcWbqCh8bL5xLVKbUyFrgK9vmQXOuW'
        b'xmLu+QSPBDVKdxm7DLU6R+NBH+Nc0BMAB5M83LD3ElgPWlQeTDXgHNmy9QN7ptrNRqkKkUhqtSy4Aw6GkierweUwngDuUqfYS8Ap0MPKAftWMjvuF2eA9elkvsP4LjGO'
        b'S4VATKRhmcGdKqICdUpPgz0HjWUtQAtTPr1gt2EhPJhEXCRQjqYscGL2XII4iJwLdjEACnAochkLF/Jekp8u6AHbGd/yAXA9AXRSlIY/23wWbGK4q9vU4MY/UPeD/nxO'
        b'JdeW6/S/7/XwLyw84n3gv/aTeNldQuUqUVM6u7qoasHsyvKVL1yTnceP1RhCmqUpLGpKJGt7zDh7kpmBcpKlOGucg68c+NIa5mpa2JAxuXpInqrjK/KUXJGn+GpcgzKy'
        b'Qs81mWtHAYqhuvYJZ6FI5EaLiaTNXJNIqmsmErnRYSLpMtckkuqaiURu9JhI+sw1jvRYdc1EIjcGTCRD5pqkpLpmIpGbSUwkI+aaRFJdM5HIzWQmkjFzTSKprplI5MaE'
        b'iTSFuSaRVNdMJHIzlYlkylyTSKprJhK5MSORHpsz156iIWOltZ205uU/39hOwsd6PnZQEVO3B7UG3TYWKqdaHp67d67EeP/CRo5y8pTDvL08canUGW/ZNPJGJ/tsj1Ja'
        b'2eLjgnekbI9p9FVOMTtcsLdgf+H22EdGJo054rK9haNGjtsj71sIGzXwCrKteJlkdtNyqYZ0SYc2besl85KV9jl0VyjMQxojlBZWjVFj1g4Sn+MzxSylmSUhavWV2ktj'
        b'OlxlER082tH3jpnfOIeycf+I5y82VNo5iNWVjq5irTF7l9Yaqahtucy+dfVd+2niCKWDs2R2q4s46pGtQMkTSBfLjDpqOvxbtR7yBBItpa2DZM6RdTL/vuUjoji874pP'
        b'Cc84aYiioih2zpKSNm1pRqvBSe1xU8rBBxWdE7fDSOIv1lKa2eFjx5sNlY48aZQ0UxKCsrd1aBVJlreFyLxpR59RW1+xGn4ajfKMlUXLfOSOATiSq9LK6TsNCuXtdnRB'
        b'R43M/+yavhpaGEnbRIk5zCf4tK28a++NxHf1QNkvlzm2rh1xDelzHHGNHjIWx0jsj8Sj73cQPbS1b6lrqpPUHl2L8jKzVolk59Cu2aopVW8zQAXj4CTWVDpzUZop4mil'
        b'C1/Gap0njlM6OIqjlA4uSjd3ibrSxb29qrVKptuXNeoSIeEoHV2kRif8lE5cpau7RE3pxpOWdGjheFxpRGulhDPm4i6t7a7pm9azYkQYPpQ97CxPz7jpeqNQnpM3EpOn'
        b'dBfK7Du4kiglT4T3xvvU+qYPifoMhyeP8pIZ76SaE6uUbnylh5csuiNZEoMvIjsSJTGP9Sn09L9KezQmD1UjZ/59nmBYfbh0eMlNnVFh1k2dIS+ZOj40vS/iksGwDi1k'
        b'cAV5NC8PKdnRDZP8ypz7tLqFtx0jlTxPmbHMQRrYvbQvrmeNnBetcIqWO0WPu1KOrt9oUs7e34RRHgHfaFMWoeOalKXn+Eo0j7P7CT3yzGbhRUDqTSOzZLdJzP6dzj1O'
        b'1YLKv7V1R+i7il9uXZccwRjzF5rVKxMgcnzmcU0Ki8Uy+oZCP39nL+499PpLpznijMmqP+E00vzDaY5a5KBZhteIqtB5doqjxn/yFMeXtyH+fI6fVepfE7oVY4nZDKHb'
        b'drUK9v8FSrc/MS5x/iSdeiqZ7PzMYxPJHrqv1tOJjKZquRTeOAANUXjOnOtG2L2SM9ziE7Li8YACzVehuMBvlYYbkMCrVQXzCjk1+IiygHmxR9+Yhun8tngd3bGhNX5g'
        b'v1f9Xhbn3NaRBj3nlMhbnt0mp++kH0xpOKZ3Q6+5ikod1zKcieQkoEtjN+OkicMdNILZlnCLaR1Y/x2GyYMufLILxpuCbrj3T5hTfL7IRYi08YJR4n58oqvXLZ1TXjqv'
        b'qKq6rHz5StsifOhpEaaXfe7t8EIEMgBwo5gBwJx0VFmmNC7e56M6dP1Awn0LF7nrBKW/qVmj1gt8der3WFV/VXfw0jdTRZjacQLXjv9OkCk6z9nrvq9MR1XG8O/UlrXo'
        b'TWazYy/YBvcleaRi5KIapcGF2yzYOvAQOEDWAsEhNhrI7ktlU2wjDA7cR8HT8BSxi1oHxi48XXIdzfPmUVwWMzs/plORlBxtm5qKOZ200tg1lfAMeeHkdF0KjUm1PHOa'
        b'QizdVzN0i3c+Cc7SX7SYQ9W+w85hUV9/T5YHBiLUKPSKnafv5Yri3AXUfLzY0FGtnunOxm4JlN7YjKQpS6kaPOl/58iDrOm139dxKM5OX3WW8wd2JDfXOnUmidjtduf8'
        b'ahiHl6KvEhfkfcjG/GK60/5B4i0t18QbhJM8c14NVSYGMfFiG3mfvv+hOib1M5jzaw1erds8dPjDj/M00LsulFnB28Rf54ubl7Omv/eq/jL9Rdlo/MxnHRiPrMHFFpHz'
        b'C8FGdrhhVHNyuXE356Pqk2QxogYbxLsWb40aWky/6XET1RZNFtv7pBrJ13Ls4EWvUWwsFDe0iQR946pz12YUFbQ75a47RoK8f9YN+q0etRyFVGHTh0Q6G2l3Pe2oQFcf'
        b'UFtOvErCbn36Zj3tVYJe/ZDa+ttdspQVU2sE6xNYZoRYR4QKGdSzE/EKelVg8TfqNU9QooefimqzU9LeDZ90rPDdxz87Orlo20ZMN1wULj1sc6bo7vGVEU81m/v2NP4j'
        b'3krP3e1IiJ39wV3+08/87HjfdmwsxddLueyjTZXvX1/xbcWFdSNFPxUtH1t1c6HTzspTrAjdrOBCcQJX8r34xPvRuVu4b0h2hfdHxXt++In2bzZHOHpz+3evZvHfOtdw'
        b'z8PpzT7rzjW7GtM6lv1WlL3QpHPJfseHxQZmwuvs7EQ2y70rZv3NN88NbjT4atu7uyN1PPNON7/32d3W8tKtGXG/c7fYfHr28+GPTGZXBLgd2WQjp759NeALiyu3Fh3L'
        b'c5zx7fE3E6wCPlpeFfDBVytNvv5HVYwOVF83/dOnOk3dsgbrwJ+upiZnrPlm+q6o8zvfzSrRfOtAyZ7aI7dPJ9LTt2TXP1hStOR17SWHAy81XHkq2Xzgnw+uB5beTdCc'
        b'Fz524cZwjYdbbWLNV9ap547k/dLccvbh00+q59afLjP4eHbYDxn3E1hhX57+OndwccvvpmvWpr7/8+efSKY+WGEQduW9G5+/bX3r0MNraSvvv2LuXPDDKwF977t8xTK8'
        b'v7X+3Q31ga980fR1uu7kjxdrfmif2tuwRuzYfO1G89Li3b2jl35bPcfxyPvvtlRe7DkrWK4Z+3X1wfPuuwq2LDy9Z0H0/k2vZA2vsq/+aMrrXQ9NQuGx5Q+rZtVMZ3U9'
        b'sNk0b/mkm9+ue1rd3LpnPncSmaEuX70uiYtdjjQoDXB6SSXbHVxbSKaECbALnERTQldwOInh6tICjeyF8DrYQGbTNvCaHQZdp3jgRdW1al4scA5eAIMEubpUUx9NT0H3'
        b'HHxazy5M0qQFWtlrK90IWhlcnulTs3TZMn0DNJOFu6cYwgt6i9WpqfA4BxyDR1czDgdH80ImZupzCshcHQ7C5u+YFhXvyqaAc3gLbTOrAByNmwu7iFhe4DS4xEtUzY01'
        b'0mFnJtsEXEtksOad8Bi8ODFxngwvkbkz7Hdnpvk7wW5H9Or16XxVvtq6bLCfC7YTgWKWRaA3uXyMXdYAx8DBYrZjEThEBOKnwD2EAIWQn3ROxfwn1QXMTH8bOB/FS1wF'
        b'1vPh9oRk1J/pgm42PBYXSxSQWrUgKQFcjUpRlXEhu9xGlxF2ADRwn3eCsMU3mG0KDkFmFSB9DjhC6OuSuVh1XZlBbJMp4CDX9H8B+1tD6AX/GuGrml8/795WvnBNutdB'
        b'NtOrVaSz1PTN0cx1ivn2GKWhsdzQFh+osXLvSonTqKlroxq+W7V3lcRv1JTXqDZmaicx2b+uUe2RkbnYSaJ+28hF6qA0MTucsDdBXNJS1VR1dJ7US5at8ImlfWIbE0ZN'
        b'4hpZSmOTxszG2Y0+4rgRY8cxE1sJ+0Aa6rjxOSP7lzeq3Te3EmdI1CS1rXqj5vxGjbGp9hL7dtdWV6mbLHbUIWh0ajCaJ041FXPEEU3q4tLG+ejWeKrYeV+wJEJSKrVv'
        b'LZdGyVgdMZJUWfmIU5DSwr4xSmlhLdGhLdwbNZVm5i2aTZoSTenUUTPPRnWlsZnYa1/AmJWrlNWl2aEp48jm056RQ7GjbkmjVsmNMUoLWzRhNLXEs7l82lYoc6JtfZvU'
        b'HlrZt0ZJNduSaSvPxpgxCzQRbK9orZBmyZxHXfxHLQLQS8amSks0LxZni/0ao/FpNUuPBkg50vIOXdpyWmM0HsLE740XZ0uimwpum3CVdk6Spa26jRGN5Y0VjQnPRjhK'
        b'S9u90Q9RStMlInEwc5zKqKVwxNJH5o3SNbVjpqh29mRaxpFWdRj2TR21C0dhlnYS7yOBSifn9tjWWOk02ZRRJ78+e9opSByjdHBlpmgurkTwbJlo1MUPz86cJFlSo9bp'
        b'UpEkWOYz4uiPJ2oTU7NxbTSNQQbi7CJBxSxJRuk4cdtTWlNkLn1Oo05hf32f3JosMxt1CkR3k4wOa+7VPKD9JA/VftfH+SxqkskzO3rZvP5geoYm/x9z7wEX1ZX2j98p'
        b'9A5Db0Nn6E2RqggiMBQVUMTGUAURlCKKBRULgiKgyIyADNgGQUFRQbHlnPRNYYREMG5i3Gw2m2yymmY22bz7P+fcGRiKieZ1/+9PPwzDufeee+pznvJ9nmdIh4vKhMl1'
        b'OEj0qIFxFf9pDq5lSM/x52IttJBfoRb6R/uy3vJVig5WoVlAzfvsDYKStffZmYISwX21nKySNSW5Jfkv5slLwJWKSVVotvEyEaom9hJHXSZU4SQqWZhDtPsBCVV2L8Im'
        b'xqE6M5gKUsK4iJJJ0SIKCRSrhIQpKps1HhiW/d8LDDveAIXI04jzxNa+SFgTxE/AbhbEVoeIpz4HngX9LLgbNoNzuWXJgUpEDfinvujmt4Nbdx1oP9J+pPPIRq2/5Dkq'
        b'e6lmP3wHkd8g74Xsb1gl9Hyxpg49lpLGiZgWnr8JOjb5T0LKMJOIE6CtXUISoGVKckcM5gxpzlGQCpSLrmA4bP8zMLFEBk9TkA6u42me/KpkuSzw807qx5wlaKYtX2SS'
        b'Sfji/8cnmRWfm97VRU+fY1HDpOmbZcAy8fJJ8tlg9vkZBhX5Jjs77x/PNX3Fk6eveNr0yeLBPylA06dlXFciTPpA03b63F193rm7SeZu0ntSFOduPZ47k5czd9l47liy'
        b'uWPQoMts9n9h9qbpOZSmzZ56PAEMpOvAKr4d6B8XNrGkeQaeIXLYx+7WzM22P6tSGz6tGEj+lDaoVwSyYq1Z+Fta/r4terT11X4bAxMmdKdg7hKOriw4uTBtdSK2YlBw'
        b'j6MzDpW3Cx4kt99eobzyEZOYmvO7t2bREaNzrMMS3eEx16hoFqW8HF6DDUzGQrAv90f3j9nFLeiGr27aNb/t09p+ZJZMR7GqO1az1W3erHeEeUtMloWXgi9S9+kvFeZr'
        b'hf/yufpwnqMkJju6Nz8w3D1DK7yeV+1iJDxn4lh3PPWM2etum9yuXvzQK/mit1fmxvT6jPAyNbuhz2xft0oUL38wsF0lae+fPX6MX1q3SnV4Z/udY69VdvrU6CR2Hwlo'
        b'vbhvo95fUq+G1lWYVprO8aUudNqYvlHHU6XtPt2psMXVM8fdOQqnagbHme7gMGiVxZuDEngLG3DGWXVwBdxA7LqEQ7twtsOj8CxBNSCePQHHJz6YDVoR9wyOoDrwai5f'
        b'jwMmO4+H6LPPYG4JcSOvVt60HHTx5xKuGh5g4DzRtrDBj2ZT94FacFRurLIrweYqeBPuy6UbXQdEuq5RAeAUsSqx/bFL8vU88qQOFKdj+xfo2axgAgMNK3gqz3Ms4i0p'
        b's+PQG1wTU8kNmdlr8JlbPukvsr3PUDJDDqbOJk2B9YFHgqsixnQthZlt60TrJE7DVj7Dur5VYZ/pGtVtFDoM63LFelJdu6qwUQNDdKO+wWfGlkIB5hbq2XWMOu9RXU6T'
        b'Rr0G4qHCRCn3LNykFm6SxcMWniO6Xt+qUAacx6qUlt7h2AOxB+NHNXUP8w/whapiP5HOiKbzqIF1nU+Tf71/U3B9sJg9ZOAmLrlr4FYVQTgLBZqjUvRX3Df2bwYAIWMh'
        b'4xBo0vMmJj2ThmCFAuV5WvzClAej1CZtezXZ7++wX0GjVhOVRaUyMqlUZiYjlcWkllG9LPSjiX5UspndzC6Z5rOKIppYAgfH2ths1UzWHlU5rUllM6kspUz2HipTqVu5'
        b'S0bpUpVJqQoqVVUoVSGlaqhUXaFUlZRqoFJNhVI1UqqFSrUVStVJqQ4q1VUo1SCleqhUX6FUk5QaoFKOQqkWKTVEpUYKpdqk1BiVmiiU6pBSU1RqplCqi0YD63zN96im'
        b'6pE7rHIR/c3Sk4/JKUYtI1UP3YU12WqIplugO/W3WCJKbH1fJU5QgF1AfnZXVxTAEhcsCuOupy9xSWYYj0nXeQxylE06StTkdHwD+mhUVUgKMD5ZhCVQGz9UlF8mS/Bz'
        b'5aQW4n/RBbkluYL83PKsYpKgaVKvcguKS7CLi4f6tOcCNwiKBOu5eNUHcnHSHPyNW1LIFdBVLIqI5Gbn5md5THty2gqffLBZxZdiZbATvK3mGoUI2qIoJIC7L5WFSAHn'
        b'YZWbB4PKhy0LGSr+yaEkzjysCc/X2LAxEV2T35ikukkL3jTakASr4kgkbESxM7iqmu6giobpd4O9cJCO507BejBIArqDXXnkLMuOgf2uOGD24dz5/DhMyUXMrZkCGt12'
        b'eRvscgXN8FhMHE7gTZw1DJxYsNl9A0EtmhTN5/vEMP0FFAP2ULA/HQoJajHABxxHZ0csA1SCboqZzvDWNiBv28GHF/geMXGg0ooke9coZEKRRjx5W6iOAz5N4K0Q7MQM'
        b'a2JxMnjYxppvB07SSPdDEcV8cN7SPwq1Bj+tY8dKAbvgMaKLjgX7V9D6DVCpglM+q4J+5lZ4DN6k+3KaA/v40XEu8DZsRDcxifYSPX0AXKVD2wdo8mOjeTnw0kQ+AXDV'
        b'ldZz77YD3bLIvRQ84kkH7oWN4BTNPvR7wC6SuAGKw0juBj94jlTq4uAny82Ao4L2kOwMy8A1ginzhJUEfuKJ+nwctE2kWADH4XWiyC4tIFroeW9Gp2laR4dTNEx+cK5d'
        b'IrUcnqUoG8omDZwlfEqTN7nV6/X5abH6fF1KJtXA2s2giaRSgMd8STaFiUwK6WCAPNodTlTxKTGqaW4XF0VQdFj+QdYKWXYHCrRkkOwOhRZkJLXg9fWusMoAnFHI73CI'
        b'lQ5vQHGpTC92LtbVg4fh6efGkzsw4VWSUwHcUIdHpmZfkKdecIT7lLJBizk96l2pTL4HZRITR0QyNGXaUMxalQ0HcpPMl7CKW9Eh8M4vd08nD8ZDL84VA6f1x0+dXh+z'
        b'oq7OxNTlyazu5W7KOpbM+fOLTHRrBu1CO7bp+VqD0rygM5ua1X0+C3zjbz++9mB/wv0bTtbO82z1RF+sZ42sTLa/ZLb48lsflqXfqdt6cei1iKuvDX7gGCSuru20uvvG'
        b'iUjeh1+47vvmZ/euyJU+BlAz1XGh38q3W7bkuuwKVGqJWukrmPvhLxYX6z8yPORWcLvSfMWDU5Uf9Q1UfhJS/q/t7/aX/F3t+qsn/xQ/pBV8/UbGmZFH2loubZGWb3+Y'
        b'/M7GHxYU17Yt+oH56wKL4fbvNR9Fvf4LtTRH3dS/YN+ZvBUqwyu/kR640bcu4V2e+/dbV6ss4n14/H3R3x1HZm1OqY37Jq3JsPfA3lbX/C+/F5ep9xlUt6y6FtLoezP1'
        b'k5bZQa9eq9YwbHpX9Oo3op/WXWqsCTum8UvZ7rCt4r9cWz0r1DNW+fb7TZ9nqjl94P9T7MH3I96NeacbfVi0fRT4mU6oweH3P7MOPXIy9JPy+PWf/O29MZv3kldKBv7Z'
        b'F2BQEdfz/qs/iAw9/nmH83mFxi3TLddGEt533vILo5wS3X7dkGdGlJJG5UWEvlGUNdhD82w79QnPFg4uOfFjXTzgTniQvkMjnwlPGcXSbOgNtHtbcAhYRBcGs4hxUBXW'
        b'MLeDfSE0G1rDKsdhVnjesG7caGcI9rNVYTU8QYI3wAsW4DKJJgPaMLc5zbpnAek4GuCgjz12w0L7A57A25zIFzchjdnaAE8VgBpPRNLA2QVovWLSVcyEx4ND6dAsg/Bw'
        b'PkZKKYP9FBMjpfYspmMT16yBh9CDMXEC0DtOQo3gCXZgoCodD6YP7gZnQE0CoqNUhS4rn7EU9BnT0Uquwesk8ASmpFQejvTbxkCseA/opQO5DIJmnJk+wQEcQDSVEFTt'
        b'taw5cA84Q6JCwCv68DKo8cjG0VAmiKq+Pwu0A8lWupK9YNdWUBPsmADOy+mq/lYW6GeBc6Trqetc6SRpB8CxtZ6YsGosRj0HV8tohXQtuI0GLiE6DhywcCG7VMOBCcVe'
        b'+eTyLNAcRkcAdoP74E1ZDGBwDtIxfoMCYQeu/So8TkfoIERQR41VYi+DmgEJvB5JGoBoEWjgsnEmF1N4Dk0MXgJLss1BDWic66mQbUYfnmYhAa4KXCMzawWOOZKQK+Bi'
        b'Osk1o4HWEOxPzSH1F4IGJPfgJhQi6k9Iv3Y4KxL2Lv4em6qhGAygZsW7y5O6TKZZlvA0Na9URS82lXRngx3YhxcROIsWpPws1s5hBcIr8CSZEldYD3eiW+rhrQSPCcKm'
        b'P4cFboBmbRl8jusNarZu8oyKRu2m94W+NgucyeLxtF8SoA1bAhWBa5PyKuvK2MDxlMpE4FnEovUZeYm0OkocMWLAGzW3rouQaXUt2/xF/jhWhsRv2NwLF9MloaJQif2I'
        b'uecDK+chXuiw1dwhk7lj5s4SzrC5B1YmW5OU6JHDVguHTBaOWtqIHUUrSQ5sazdJUq9z5+ph62D0tyYGtzmddW53lgQN2/rjVOajFlyMphInNyeQtO6T/8SJzjN71nau'
        b'7d0yPJ62fszGQ1LSs7lz84D6sGf4sE0Ezuk+YyFO6L1ZtFmiOmztjV//0NoO/xo1tWwzEZmInYdNXeuUSZ5urjhSauzyqZMHzisfKVotWdq7oHPVkEUQzlk/WxSPfwVI'
        b'Ldy/U2E7mwnZLZqPtSmep2SL1DlgwFbqHHLPOVzqHH4n/E29YWe+UGvMlte7aSBX6h81YhstVBl19e7lSV2DhSojJs6jzrN609FzQpUWrVG3gAEbqRu5wBt18eo1lboE'
        b'DYRJXULRVZ1RL38hu01TpPmBifvvN03hz0CphQf+PQcJoN9pqcharIvTz8fWx97j+Eg5OPqyp9Q3ZoTDH3VDM40vjHB4D20cyMCZW7fNEc0Rxwybe9apjhmY4xGKkhq7'
        b'fcrzGrV0EGdLLd0lmweUOiuGLOaOWtiLl6I34d/LpRaeaIxc8BsxVJDnjbrkHDQwX+o8957zAqnzgjsZb3oPO8fRY7T5jprUP2bElo/HyLc3Wuoa+ntj5NMbIHUJGRBI'
        b'XeaRMfIJQGOkLdL+wMTzeRqn+Heq1MIL/05Bw4WGSdZoMkzx9fH3OH5Sjl9vykChdFb8CCcBB27gdfLQUKGLOM07HqpGbQXRXJMOb3DlD4U3kGn1J7bzb+3mDXLdPpbd'
        b'VyVi2f176sUEeJJPVqTMozo1/P5YbnSSeZfxG/mcx5stz1/6Lmq2QoJkW5JkXCa+TSTIfjl50GX5YlXWFOfmFDw73/i0Ng7hNj5hTGqjPNU4rkpQUlr0EtLZytLBstek'
        b'+6Q/d9uGcdsmMjk7R+YLcri52dzcEm5uMRJm5/vMHx/Pl5Ou+xPqBab3w8nNsyDpaYuyMnNLCoteShJ5kgD7c/YLNGkMN2kiJ7GVrEl0wviXmphYbc36wszc7NwXWGoP'
        b'cOMmclA7kcTcguISLl1Txsts5R55K7M2Z2WUlrxAKz+Z3Er78VbSNb28JmbLdyyJUfL8DXw0ece6yHdFiQJ1QduDrvWlzbfKmsysdLSwn7uZf53cTGtCWEgVLy/R+Pgs'
        b'y7fdc7fui8mzbDNp77609mXL2ydXQj93+76a3D4HRS0enmi5Cm9yGxVfPzldMkYCM6tYMmwtxaQOjCsrtzOI8pJSUF4yFNSU1A6GTHk5pfTZAUimY2uVn4H8/a+ncsaK'
        b'1ZRpak78j2ybsrVZaDSL0JCiHaOweYrQVi9Cx3MJFy2HgsKS6ZrSadrSGZN7fxK0iEWSe498bz45uTfrSRYVNML8bLYyj0HE2og0PhG7J8nc4EZCYDysmSGN9CCO92Qt'
        b'Xzbj7Z0Az2bnZJVMyvKdvoxBWZDIgEMclxfMK/1cb/unAkb3+xXL/lCG6eexy1NVjP+KXX5a2u/p6xhNab/OEFWM1YJpJpzm24XjlvncWXYskxKf133vzHNg5ShTmVL2'
        b'a1FPZZPrXbFcPrlRcKeCTgVczftts30R+N2hL5ZNtD4lE3fRRDu5SmadXFcX0ZgwyX5PZlqL8Zz2++d69Y+KFv1cPOumL2rR5zFpDe5hOGjHx5CWtiIGxdZhgLOBsJHo'
        b'q01VYTUf6zQGZqMrvgzQ5wMluUX/aWQU48hCevqvYaz9riPtlbxD3nsv7i3++qTRm1+mxWfECJiXTNeZ5JkkCv/mpYT2HYN6pUot4lsf+dqfSTTB0z0xCtjrvVxv2iiQ'
        b'Ibekh3yUrfp9yjIGW8/1B22Gns9Drr0kU2rsO6TrO2mfzTTmz/Wub+RjjN71w3I8xmr/q9ztk3cWm9BfOvs1JcNMvHwqHDeNhIZjeH8xzbogmjvZulXMLS7Jzc/nbhLk'
        b'52b+jqFqOn5GOT4pkpgKqn3KKVXUdd2gd2bNM3k/KldXqVmpuAgPZfR8GvHggCgyx3epDzNL6JVVvXnnI7eUV01dRTt98lPeeaRUXfxwZNeCM7svCvfXMwZ/vaJ5uCBW'
        b's/WdWZqtsV3tlxYwZ2kufyB0WQZLS3yynzw61iOQPEpPe/MRTKoHLV8zN+Y42OUEUobZJiGfLOSpElqwAXYGuY4rykA36KEobXCVtXA5vE0UfKbhsIE2cMFLWuMWLtAB'
        b'u2j94jVwCJyjDUcBoGXccBRsQgDALnYLXXMCppq/POfKdMZUEF+uNgVndGiLFLxZSCuFD7kvoDWAIeVsNk7bvjufxiIfyUlxhQcSokE3m1LOZ8LbWrbg9DryPndwGZzk'
        b'oytuyhQ8B66yLRjgEuhayFN6tuyPITMKwAXV3OI1ZJ4n+CB5CdllZfTKf1yOCJuJRdP2hu2j5gQbu7Vhqzjz7LqOdaPmGJzYtKNhh8S+x/2cO/r7IcekKa4+7i7HS5x0'
        b'dkX7ijrGmAFGL5iMGLhgHKqySLlZtS4MI2Zj6mOOxIq9pRz7ewYuUgMXSdJdA2+6yklIhBnOyRmBCAqgjCILZUX2Tt6tXxSOyqfFL3xU4nGXZTo2mCkSo0LIRYyeKPoc'
        b'jzILid5FWENcVKGEB10uv91XlctI95VpoeG+Ms2o31eVs8T3VeUcLCFRpFc8rf+9UhfjRmcIi/gnjN6Qm/bX4bEykkdEZGrpfqtMaRuKfEUlQpcRLYenzOUMLcdvKfyJ'
        b'Qxw6PiYFTzYx5eEE5+BwgoEkmqCR1Zgujy4xCqyKnAhCiOMLGsxjkCiEsiIfXORHSmTxBf1wfMHZJL6gLCxhCA5LOJdEJZSVBOKSYFIiexmOi2g0n0HeJiuahYv8SYns'
        b'MRxg0SRAsaIgXBJSFfWDqrqW3xMjytRGauLZHnAyCP2qin7K1tWyeEyhDzpUIbE+CUGTNuwbV+Org1omvJoCBsGFikn0Ul/2+7tQtL0aTWeAriijHxP0Q3Uz5UANgoPQ'
        b'qtKvMshW+uOQFboWxL6p7VGVQVVMCNxDdRLcQ3WiFd3q49AZfERpoPezMzUU3q82471KSJzQVLhLfVK/TLq15G3KNCW16pN6dfaojT+hMf4EJX8Kg3lkPybdul3K9J1q'
        b'6H+mWRWDxHqkcSJaVdpVulV6VQZVJtmamXoKtWpObofsRxX9qGWzuvW7ZC6dmeYEJqREkCcaVZqoPh3cxipOlWGVUZUxqlc300ChXq1p9crqxO3t5ijUqySrUYfUZoRq'
        b'Uss0VKhJW2E8jSbGE40PM9NYYUR1tmijg93ivrZsn6Jfgpysok/90COTzusw7uQ78CGPfhdzBeh8Vzz1McpFUMIVFGH16MbSXER8JlWUjYQxcn8mupRRgtUJuSXckiJB'
        b'QbEgA2tmiqeAYaJLEBdRWCR71fhbBMXj8jNiPwq4Am5O7qasAlm1hUVbplTj4cEtExQV5BbkBAZOR9tg0XxKB8e5l/kLksI8uBGFBU4l3NLiLNKDDUWFmaWkuTaTMUlM'
        b'WpV+nDnFs3fckbYAfTQqjXv2MuVhRQksSWXcp1fppfn0Ir7t09Sp00kGdgoySc62rZcPwB8CJ42PP5bL0SJQnLQZBXC8UsgEZ3pwo4leOLMQtQgJ7NyszbnFJbikDM9D'
        b'ukwNmjUDKylrkEzpQ7dpmiqoLBc3El3JLkXVCTIz0aJ6RpsKMtEPV7BhQ2FuAXqhokr4d/hYZWoqH6sVXxpKYYwvqIanJzJe8ZdFyU2x8KaTJ2yAh2JJiqolUbHx8sQR'
        b'4DbcrwFPM7QJDCvHNXPG5/EjMisyPAgaNsH9atvTDOl4dYdg+2x4BIld8BY3ik0pOTHQEXMsio49VQ9bnXDwqYrCzdRm2Aa6yBm0CcdvTXSHZ+AlT9AET/tQLA9KJ5hp'
        b'vxnUkiRf/r7gCEl9PO5H7bYS7IUHFi1a4r6USfnzlEC9nzcdEu9UKDjlinaDMdhfTBXDdtBGePpEJSbFtlikguNxOa+0p0hCMnCWAkf5E72CVbGLcTYQN1gbR+fbWFy4'
        b'QEUF7oSNsnCYkYXgbPFGJSJ3njSiQDWoDsv9WGszo1gfLXnlu9ea3w5F4kEAFg+Km7zgKO9gl6lNt2OkOM+IeU5Ul9SXc1Fw7r1Hr3K++mzn3798dKe9xrz5AufzD2J1'
        b'N7mztLff+CnfdRPzy0dvnN1dj1UE5/fZ7FXKPsLDkOmMY9wzFzhL/9G+XKnEGNzgeO0Rvf5m3b3d8K9AmD5rQ3H1v+pAy/kjrLFax0hJ85j0gVt17qM84fpHmz+z3/in'
        b'0xt22q8TDW3fG2L/pejSu6Ym1XXDGk5Lyj/94rOD+99YprVOm1X3hspfSn1YWx4LmT8fPn1kFp8xvE/9ddvc3q9jhEXLzwnTeSu9fhH4DVltfnOZj7OviQ/H95ivt08E'
        b'c/trbw4ZrHzF4q1F71XZrFbT+1s+g/oPP/LXPZ/wOAT+4QxawHkClcMwOSgMwx6HgwRMsBKKoJjAWxSxLRvWs1V1QDMtu7TCXRF8+YLTiAHd8AQTnoU3tOj89s0JfBnw'
        b'Rh1cJsAbeCmAllxqtlth4I0cdAOvZ+KwR/voxM3bYd26iVBCpYk0kvrmMvLSlYVgEAk9oAHcwABFnjKlxmGC9gTYTYN2BjaDY7AGsU3xsLsUrx8XxGCCy6zF7uakcgco'
        b'AgddPWG126YoxFYpAwnTDVV2nHYDtYSXYI2bS3y8LBgAwfsUBdIC1UE3cNo1Jg6NlZ4j24YBWlVoIQ2eg+1BxGFyXaw8Xzw8CSXEPdTUxVsOQDlAcs27Iw4UXIWd8AI7'
        b'Cuxn0TVcFoAmIkNqIDkNDYmyAVMLtPJpzAaogp04/wsf51eh25UBu/VAEwscXruRDOiKwFR0R2w8c7acYGgnsuLg8RySgAv0wCbQhx7FsaZwRp3aqDhYC2o9+e7weDzJ'
        b'+4MjbC4EF1XAYZYP7T86CDoWjmMOazD6B4MOwW0fGll0Ejb40yl0JvLnoLafZK9eQtF5a+pAJaxDnUI0DMjfiZhmCq2QWha8DS7D8zz1PyBm4NgY3Cn+Y8TSbDz54J4M'
        b'H1nMoMXOyOVI7LTGwuYDM/shh8hhs4VDnIWjxlZNFQ0VpGjusNm8Ic68UWPTprL6sqaK+gpxybCxWx1bDigJFgVL2JKcYfPZdaryu3bU7xBnjhgjVt+oiV/PF7NHOA5j'
        b'ppbCtRLWiKlbL3PUxKxNVaQ6ZOPTu6x/xcUVUpt5IyZhT1mUmfuQqdtDU/M2Y5Fxm5XISqI6YupN2jFnwE8qb8ynilVZcdtyRDnNuW2FosJhK897VoFSq8Bhq+CBxVKr'
        b'uUIWqfQh6hD2/8u4a8wjwJe5w1bzhkzmjVraYGzLqA2PQCW4TgSUYusoLr3nNFfqNPeuk+DOwjdiX4m9F7FCGrFiaGXacIRg2Da9jt2o89SUbu3PT9VlX4rJyWJhHanP'
        b'grO9Iq1Yr+srRZqrvG6lFOkk8xpUV8AVYGboOcAFdNiVcTjBc8ywuYaCu2BxCpLAbXAMFpsXhRQIlZ0piYbvH4MUyKziSr9pG5raA7mJKFhjErrAd5yXms48KTBKLxFu'
        b'UNT5G2CIZ7V6roaihbqIrTzFrWJyUBgWbbaqYssU/i/XcDXNlev/IcNVDhIHBphTBmdGG1Pnjz8xiI1p9tjqcRuThQ22Ml2lqKAnLIb6EI9BcgVGwUF4ehJ9VUGcGiGx'
        b'mLx2wd3PsjQ5TpnO4oz8NSQ8y28YnJak/i8NTs/50nANBbtTeOrLsztN8ikk2vEqxv8/PoXTFyI7vjQYfUcsj0hl6rGM/SoOxLrEuC2Hh8G5JNrLApclxGJwLOgCBzQC'
        b'YhNy05qgUnEAfn3c/ea3v3oda7+vRd044j2NxXXcFy/2MLl9hHdC7cy5hl19SlT3RrXNfwrlsb73pkgmgR6wC57eMCODMIU7QGLAJcLXbI2ydVo7Y55MNuyJBKcJ68IG'
        b'u8GpZWUzMAFohTpu/A2LzQThB8+7eOSWMx69Yp+koBVrYilOvucQctchhIA8Y4at+EMmfBwVbbpBTeW3DWrP8E17kebFaUxY154uS31R6xr2WpNZ10IFtnwSGhOeh7XE'
        b'uAYvgEE6QP/5JfAGNq8xqMIIYl1LAJdyX7X+mkle/bbEnjggj1vXiG3tm7TojHgB81uTCeta8wi2r93jqt1tfk8WA+p3bAATgwLxoJg8a1DILFlT48a2eakMVT3XHzks'
        b'PZ/HqpSNwwzmNqVnz8gLvXq+xoTt7cew1Be1veHIU4ioYjX8JCIz7jW8lqJNcDJvM+UqRpUKOlOUxsmM0ksjM9k85s9npqkgFmaVcAVy7kBRHfds5c36oqxsWlEyDc44'
        b'g36lKKuktKigOJAbxg0kvniBabLBTuMWpudlZcwAr/gd+55SfCmeEigBbeAMkd340W7r4NHo5EXL3Jcum9EtDez0U8vzhrVEHQJ6QuHuCXUBrUGBF5iTVQZLNFTgIVBV'
        b'nnt/fTGzGLNC8w78tfntQGLyv3bk9BF3RDm7s3cPXdFs7R79rE/o/VqeyVLf+SmvbXNYPNLtJeW8Hn/MZbbywEoDu6HVjnvup75u9rrb7Njhnd88upPuadQ49rmm5oIH'
        b'Dg82mIt0N33gpUyO7Jw3DK59dYGnTExverAhn4jEefCc3H+4EnYS2L0r7ELfaW+Tg9GwDp6WiZ87ttGeEqfK1yiK4zrwsMzbRJl25ViOJKo+LMuXgk4iznuDalmk4RRw'
        b'DTbzJ7RJGqlMsHcNIhm3lWg3lXpwDDRNpebwtoecoAORy4v4MSsEy9HAbruyhVVuNmVfKlwjRGGtjHSXYNJtL46Q2GPU8rCxHw5hMlnQIiLS/DtJUofoYbOYIU7MmJmN'
        b'2L7ZvU5l1MCsKag+SGx/1q3djU4bedfAhwS3Cxk2Cx3ihCJpr04R+6xKU35iXftti6DqBPmX0ZtkbBL8jX4lyUUTTPOzMMUxefyCaOeikmcyNekUzbnKAiVQMkjYy2Vo'
        b'EPf685UZKU3JdBhgYbbcMfW/T3jC6Hc+J+GZEQAU9Ua5EuEYdvxcQUd45OGYCSU+F/ZVf+gz4pXpLTj3TZJq9sNYFepDL6XK+nd5TMLaLK4Al0jAFngYESwWOnKJmc4M'
        b'trLL4allRCtjEF1GXD6xiw2sAu0yl89mr5lRQuPAEXPmM9aUbJDJXrGh98rjpBUMytz6npmL1MxF4jds5oV2ABL+0T4Z0nWYdIQ+a5HTMRwn2PXfe32mAhvzw4IVL+p8'
        b'74dbw6QjAagUCzZlrREUx0+ykYyrzvMp+XFKbCT0caqKhEgqW/m/YCFBC/3T9JksJPK1jg1NmbLcfs+10sPGjWJZJQIMNRbQgMT1hZvQ+YyTHsrrfVnbhH5GNqyB2JBC'
        b'zGFu2HqyvrS4BFtP6G1bXJJbQKO0saJhRvMHrXyYBFHF1jBU+Uyml/EdittaJCijhwv1+YUtJerxpXiVzAM3SGg82gY+mRsAl62mMwTgRi7J2JPAXKzm5RrDpBhRFGzU'
        b'SiBxK9/5vCAxWWvT6o+1NrAptohRMqpCLBDfxcridS79KGG+gQ6VRBvhscoXVqXAkwvAftcEVNUSnMKuak3uF3P3sYtfRVe3fheyPiFMHXjptvzZL7dGUtbziBX8k36C'
        b'0uFXwgtSw3hqu/t3Lnui9+upuHWc+/Z7tPr6+nw9f1CGOat/vptWnmp1rvL9xO12Z4QL+LBn9crMiFlbxpz/Xa7z5Y8uGu9ufEO71k0U/OmjFZbr9pg7qZbN/uvRnr3v'
        b'tRna/u2O4D0113fcXjkqPWyQKtpiG3f29EXQljNWfabsLzXfOZ56vPe9hbxjag61Zns2av/pl/85f3FB3DLHJMuYzScKOkDj65sfard++xNjv5/HX/da82RuoLezgmS6'
        b'erY/rIY1iDOxn0O7A7b64gxShC+5ZDehFYdtHDqD+fkgUDvOmBiBhgk32ARz4oDrA6+AelpxzraBfaYM0Lp0KW0HOGUZ5uriAauCwVHEuzEotSAmaCuGO0n2cXANdIJj'
        b'k7TneuCWTIHOjkJMi4hoz5eDanvF1AOa8BwDXHRXIhfLwYWtRN1PlP3VcD9W+KvA+v+N6pmrGA1QRRaXpNxoBoqJygmxltLE+knRij/A2BjikIDsEUMHib5MBd0cUBfx'
        b'lEUZOT5WxsnDV4hWSEx7w4YtZ9er17HrMjF6SkFtbWzWtLl+s5gtXixeIlYdNuaRgHDCzPqtdewxAzOsps4RlyiqqcWcFm2ZGtm8TqOupE7jqSF625Chw89PdeXFtPb3'
        b'FRW9cFUWcNEP57CgqlK4ngrkKIVbybS/agqHzgrl32WvSFqeyfxVDuavnjG0hYpq3xX4ILJ58oJq36LFFMHSEtU0OZLUxh2laHSUpTKOWJMvKMjJUFEgWvpyonUQn1Ga'
        b'9Bm1n7WfvV9pvzI6qzB0BEeu0iTwEZ0qXXR66VXpo7PLAAmGOJUoJ1ufnGEq6AzTGD/DVMkZpqJwhqkqnFYqO1RlZ9iU0kln2A72DGdYWGYmdrMqyCqbDM7EJm7anE5b'
        b'/zMKi4qyijcUFmTmFuT8RnQRdLIECkpKigLTxqXrNHI64LOykJuWllRUmpWW5iZz8NqUVUQAagQVMq0ywTNRINwMQQE+s4oKMahN7jFRIihCa4CbLihY9+yDcxIIYAqb'
        b'OiME4JnH6W8dwXggMEaheENWBumhGz3KMx6oE46CBaXr07OKnhvQML4o6WZMOPOVrc3NWDvpZCc9KhCsz5qxBYW0b5F8HNYW5meiDaXAJ0zxPFovKFo3BbkzPmnFXNo/'
        b'0YObgB0vynKL6RYgZmdtYSY3MLu0IAMtD3SPXBpKm7EieeszBPn5aI7Ts7ILZWzHeNQfehGUYicoDLsRzFiP4hp65kiO47ADuVNdECccReTvfZbDiKyudJ/06bUoOjL+'
        b'zvOYqiAeLTGBO9s3wN2b/F2KKBzahJlZ8qmS14WWPr1KZvZficjKFpTmlxTLt8h4XTPOuFMxl/yJ4VHTGjeJkZOtTNyVDUjqQt+egw2dxN8ZTOPvnOJpH4F9ebbFPuAg'
        b'uFmE+KtCCvQDMaihL52A/bBSY1NKzEYGxYBVFGzRgB08BmHLlqjAFtf4tVmwFucGqmWEg8v+hGEEx5zzNTZtXEwri5w93J1hladLdBxiE88lbYCXSsAe2LmUBqeAoy5q'
        b'c2CVBQGcwB54yWoSpIaW2ybwNDsSMlargnYwAKoJ13gkSIsyoXp1lBelxS5zSaNILKUdQGiE1TfjeBgC/Oa78dxj4GlwWYkKcVWGx828iKKW6wdPu8IGZQrsyWPo4byt'
        b'R0ELjYlh4LDuP21jctNiJUb+dORAwMds6p1S9ry02H9Y2dKFHH8cPIe7iE2l5T/YakURqI0ZOGgETzJxbIwzOFg82JVHYiGTJ3K2q1G61DyKkZam+ZHaKooYIqLggBKJ'
        b'0JQYRUwA0aj5B12xzm28K+hClFtMLKiFlR7R7i7KFKzhaW4EA4tKcX4E0OgDj8g4dbAPnJ3g1g/yEOMHOpNkjDoPdXcXvKYGToJ98HIkT5WAk+DBRfAoDTYQ6LAoGmqQ'
        b'C8/SS6FmGazlI/ZuDxDFKpP4RqHwGA1q2gcr19ERjixBvRJFAhyhykj8njmq8ATfCnYoRPbA4Y00YRtZREGaZXSEIUN0XJIAQ6vXkefMOKDNVSGeRwA8TgIMFbNIeKFC'
        b'WBWPowvhUB6gHjaT6EJQDK6S3Kfg0GpYNym8UIWTQoAhpWzuXJ4Gmf5ofZyyF4357ALEtOKYWJ6wlzTAHpyPo10GsL8AtrnQPgMXt5HLsD9Qw3WyS4AZ7ITN/EI65hO8'
        b'upKPN9VlLP+QuFiwGR4i72Th8OWo16bgYqxMRXhpDanUCJ6BjfxlQCyP5EJCY8FGeIXOV3kM3oB7SbTF8Tguq8EhEh+LwaLDJYl0c/gTQVygEFzF7ghscIie4q7ATFn8'
        b'b3R1awTxcogF1aR6FbQ7uvgKAUlgJbhBoi3Bq/CgLNeDhua4MgXUqtO6FDAIaasHPMCHFxJh3ZztyURmoQrMQD+JYvUVEe+8nNXmpbnZ6PhSdGv2g05/1J0jsHJhApti'
        b'alLwNrwGK3nqJG6VA+xfUKxdVAovasKLOkhq6MdRNkvQWOexoqMLCfYNHgKt8JjiXX4+sL8YXi7FWqAzLNgKxbCbxJzie1ko3ldWslGtSEsbjWmVMuXMYsPdaPkM0nm/'
        b'e6FIGfaVwsvFG9HuOqRTZL2tlEUZWLD8udGlBMtzEZwHN4o3lqqTunTgFTV4Eb1UE9yEtegJeRPmrlZWAq3eBMdX4Ro3/gC5nu+G7jDIYoUZqJHUzetBJ+zCt4D9fMUm'
        b'IukCXGA7roYHSGbeBCboV6iopAheCoSXUfMWsALBVTBAboI12xzHbypDNFcZpyndo6vMhBfgVdBJ+rkMHlbSgFdLUGs01bSKlCitHUzYBrpBH7gdRe6wgHucE+NgfSJa'
        b'so2J4BCbWrlRFRxnoCo6dhAyp4Q2cuIis9RF+KWVlAD0aJPehsTD29PqrrQEfUGwlkx+LjhsXQyv6hShCexSopjwDMMFLbhqcoTAy/BcGKxBFJDvyXWLi01IxsfFEpn5'
        b'wQ1Tw4PRsbAaEQawO1mtGDTBowRD6Z7L5+Mcf/wsRiAFj4KdBmQ4ktGE3YZ9UYgk8N3R3olnU3qghVWEenoM9oE6QpS/qDCj/CguQ0c3zcKsdC1Nqb3XulJJ1OM0Sjct'
        b'/S2GN0UnbKV+miv74jyPxyZvTkpOBV04FTnYiQ7XLbB5Pp1euXklvAW62GhkqqlyqrxsFtGNMNYGuapQ8DQ8RW2mNlcI6NzIB8Hu2bCGxDtqoXKpXGd3IsDl/uP6bmax'
        b'KYuiNO1iWpf+ed3IPN1P3t3ucO3BlWs7/uqxvrjcsLNK8tPiVztUlyw4FaXnfstj90f9Ky+etpds/2jJq8ZP2r9u/qno13v/tm45Fe3x9Xv7RlzvfZZd8d0v775T4Phd'
        b'33c1VQviPzv8nyWjK8P/0ZV+7F5mUK1R66ov1x31us7fL00OOn9Q/8HQWMGpOUtf+/Xpl3sOfjH2a6jSQY+Mfe9aJLjv//HWu3kRJXub7qds1/D7d/Cteji45j/MHfpf'
        b'Ct52iU34y62E+fq6Hzd4n/zsbSf1D/N/SI06uZn19kEP079Z5qV9Dcu+eaTu+7To9k9H37FY+/e8z35x9p5zXT+0MvNe7Ea/+e/YqNaU6e04/nPrd2UfBCyx/fxfTBAx'
        b'cPZHs76+nzz/rPHTn8Gjn+eL3rp/851/3jH0SNqQOtCZ9dWne494eYeq7WzR82ipDNVf3GGxlKuT2apT98CF1//Je7x49afgXyce3dN97TOzpTaOOifOLpBsbFyzzO5f'
        b'l8rdt2gfSNG1fPOxcsMrcfaVeXo5T1z+0XR+0XWHjzhR3f0P3/zodH0Z3+6fjZGhzodW8g5ts/8o5W8p+wuqPtD5J5ydamx+ftehz9edvDa21uqqS/bs0gea6/5a5tHd'
        b'1HPgn8fesFqcrfSDXfkSta8eX37KOfHmR45fvX3o27PqI2cqlZv//vpTp8YvQr987aLPz/F/SirZdjg9MuQNSZv36kcHLrgGlv8Yuaeg8hu7Et2acwmc9GTnv4vuOsQX'
        b'3b2dvbzmXcvmdpvg2xq/5hguLl2yQ2IUy9jYqvkh32Vu/Q/JiceXPOjlWVQsn/PvA+80/2w5B4ztOJ41fHDJv2N/bVy5v8241u8Vrmj+fr/yz+Ze9ru6gTu21+BXnfN3'
        b'XI6Hz+fb7dy8L6Lv+wPs1wt/bmXuf6vtT1V30mveyTi/eNaneYyCuNfVmn4Q/FWpQ3rY0XjT3lUhlgcbcvU/znOs2Cu5kuI794dXB+4J7we8Grjb+c9l73nfDEs/d0iv'
        b'OiCN9eTtz3f2nn9cXrP5SmKP4I2qkY8NBY+q5nJyw1/9Rtm0Ligzquzh5cLdexusP4BzBxvjLoWrZP6y/csrEdsSRIKN3SXWQp17m9407XryxDrfk3257GueB7EHRMPB'
        b'bNfJKAf9aIzDEQJxGWghCFJlfdiJGBlQvUzGx8Cr/gRMAXtc4VW+HHWRgEM5UnpwP04gUgsOZpgRRZsf7AZnJwNy4d5Qomiz96Q9+ypLw/mhShOIXCY8Oxfs/96GHImp'
        b'8PgUFCmGkMJBXXAYDoAbpIXqZfAM1tSZz8K6OgZo9QIdRIe3Js+VTgmikSZHuB7gkI7zgDhoGsIVHllDdHThG2gdYj1osQBdspDL6By4SIdddoViuuGHdMAV1/g4bJ/1'
        b'U6bYfgzQaQ0byLUYeGYHrcAD1eCEDLGbl0nXK4TnVshVf+D0NnnU5f3gvMzVkWstS3OSAveghqcx7eDhAhpz26VXwXcFF1CDwRW4X5lS3sK0h9cLSMXl6TF82g5L8r2A'
        b'neAAyfkCBozIcCDO42QgUZjOWS8z5JbnEtxsoBvBJ8t53QPwFsEno+OQblEVYqSO4uRjGqs8VZD00sFIhnVbiRI2hQWuY0V3OLyJWFnssgnaYbXM+Gs2H9a4IYYUHUOw'
        b'Os4NsSKerHh92BhVQl5bmoO4xc2gaZKNF14AXRtJe1eVwNuY+zoJxTLGzxqephskmg330ay3dpmc9a6IJEMUAZtLae7aDueSp7nry4BGWm9CzAAfngANU/hrxNnTKWbi'
        b'wc0KmsPeViTjsJH0tIuMrzE6mW4rMtmmUEiY7MIN5NngOHhunMneE0947GAwSBurz2aBvkkstlXBJBYbnlpFY8FrVeEpXAtt1EZsWZ4O3MkqBI3gKh3P+1Y07jtiKRPc'
        b'5xoz8ZJ0AT2B32OeTV0TyYQKjNhGeEUL9jJ8wG6GAN5ygx1KakGL6TiJl0DzEv74vCSD06rwOBMt1sNhdIKg62gar8sz7h7wjAbn8/jODMo8kg1awa5tZKjtM7eQaOez'
        b'0K6h7FRVYDtTFTaCW9+T03mPHryCT3JwnYVPcjVwjla9H4T9IbLggLKsEQZ2LCUjWLsddpPNCeqjougbPOJgdUzcGnDLA70ZCtmgBdZnk1oWw0Evck+CG2JQ0JwwcZMb'
        b'jWex586ikYYGizzpSuLdo8DBKCTAHca5d9HGcIBtSmkeoJYeCMR2XeczVuC2VNPzoQEOMWH7Umcy3FywW50YEg64gXNL0HDHMy3goCNpRCA4aU3D9mWYfbQgCGwfHIQX'
        b'SO0RsLMUMUyHQb/OJhn5U4OdTHBeVYf2RuhBwn0TmgZ3njNaNbZr1HKYaGquwws8m5cTtfC//EEsulP0KDun/ZOhKgSZmc9EVShcI8YHYyXaUrxjJQkVH9oQKs6R+VmT'
        b'cIn+PUGdQQOJ11fdSb4bkvhmlnDuiHkyAY1Hven/ftBbQVLe0mGrZUMmyxRh8nIshYHFkIFzZ2KvadfqAcFd97k0dn3YLGCIEzBqYFwXPGZqI7Y/69Hu0Ws/Yuo/4DNK'
        b'50Jt3tJWIaoYtva6Zx0ktQ4atg4Rssds7MVJEpv2ZScthMpjtg7tGRJ7ycZOp5P5vYuljrOHbf3v2YZIbUMGsodtFwjZwsUiFWyxwFmIGC3q48aLs6btphK/k9YjJt6y'
        b'somL+vjiSfMRE/enOpTZnMe6lIUVNqmI/SQMiY04YNjcvS7ioYGxKEhcMmzudtfAjXRo4bBZ1BAnaszYbrLxxsCQxL0PrQ8V248YOE0z3owaWTXl1+cfKahjPbTgjlo5'
        b'3bWaLwnvieqM6oq55zZP6jZv2G3+XauYO5mjNi6j5lY4eGGwKPieuavU3HXU2rZtu2h7c8Uo1+6sVrvWSZ1Rrv2old1Drj1OgHuP6y3leuM4kdtE2+5Ze0qtPUcnXbFz'
        b'OhvcHnzPzl9q5z/5ir0zziR0zz5Aah8wautII2VmSW1njfLceyw6Le7xwqW88Cd6ajZGj40oG2f86Ki1Y9tW0dZRrhP5y87l7Nz2ufK/7F3v2ftJ7f1GbXl4qkd5Xvd4'
        b'oVJeKKrC2ugJz8pEv479OJSycZhoRJ0WWh44Y8A9A/e7Bu6jXn79mhc173nFDHvFvBU3ZJ9aFzdm5yRh92h2at5zDpY6Bw/bhQzpckf95vTHXoy95xc17Bc1FJM6tGLV'
        b'3ZjVQ05r0DWxvlTXfszGAS3wwvbCYZvZddqjPgH9nn2ed0KHliTdDU8eclhapy0skuraPpQPj6/UznfUwWfU2a1HrVNtyGf+sHM4GrtRN997bmFSt7C7bovvLHtj5Ssr'
        b'cZ/RE/IsvNrDjnPlRajbru2ud21n9xqO2tg9MdQw0q9jPjGhOJajvrP7gy8G31H/wJf/1vIhx2V18+u21ieMGZkdya5jjRqbNWwXlt419pAoY2ucMV4AgaLA5uC6iFFj'
        b'8xE7v94kqV2g1DiQbMjINzlSXtywVfyQSfxDc1viisKU6A2Zu94z95aaew+b+059Dq0PIfuBsbOEI0UvKZHSNkeSD+rINvzVtq4Eu4pIjZ3FS9AHKjIxb9MR6UjYknUD'
        b'PgNFwybz65RGdQ2a1OvVhX5iH4lBj2GnYa9+p1lv8UBmnfqIbji+qlWvJcwSh4nWjug64b916nXE7BFdB/xdu15bWEKvUi+ptdeIrjcqvadrI9VFpAHfb2TSlFOf01RY'
        b'XyjOHDZyxeNCW0W3128XJ44Y8x4z2Ya2eA9riDTE4SMmzjijOIdu0oguDu5Qp/G0gol2tNTU/5fvNzEpC7tvKSZ6hqY2eB9JEkesvUctbJ6wKK7PYxa6+DOBoQLz+aHL'
        b'Qlj3TPVS1Kl7IUopKiqj6g4pPqxRbwb6pC2ZhrQlc9xOWLQWmzPHLYRFub9r3XzucwAzbGn0v8knAG0RbZ0JcaZA86uxVXQ+uvM/O6mni1cyGIz5jKcU/vyBfL6IUww2'
        b'yJ5V9qf6NcKYLB7rvqoc/TIRiiKDTU38G1f1V6GPRl25VZRgd1RkNlENmU2USayi2CZKEed1VpVhtgGxiLKZ1IFx++Z2JbVJmB30XUnB9sneoSSziE4pnWQRTWTOYBFN'
        b'3iDzp5lsECWmQYHMtDUO93m2mVF+x2QH6BKZlU6hCjeZsS5DUDCjBScdG2O5JKk0trY82/T6R6yS2M4741td5M1z4RInZ2JAkreDNgfSTcK2XdT0AtoEN7NFkBtemJnl'
        b'G8BNFxQRExbd4aKsDUVZxVmk7heDMZEBlBlwp8YxncnyiqqfObibzK4nt2piQ+LvGb5e1MylSk01c1nHl2IHDbAbnAUn+fBAggc8hGRc1yhYtfg3oM21PDXYA/YifheH'
        b'wwLNsBejoCZMMfBYRRTGQ8GqhEQFC5MSVQ7PqoFDsbNoIxk8sYaGQNmB/RRshA2giegV3zciqYypf1ukxep56dAuPvmqcXQqY+bSkE0Mak526UIsYFzXhlWuQIIl+yp4'
        b'OBEbhOJiCfe/TO6mMu6jEuXGXwpPK+hHWcla8Aw8D/fT6siDW5NhH2MT4nLjqDhwEFyigzqFhPxMBftz2ZRXWpYw4osKWrs5KpqXRMd8mpVKDYTfYFBpO/N+MtuTSF+O'
        b'7JhHroZ7r2OMMKkUB9u0FUPasXSKCnDSotCXDU4WU5QP5cOB1aULUOlsN3hR0cIHq3Cs/SPYsIXk12iZzZBkAeejX5WgNsYthhZOYT88rIUteJWlPqgmE9gEqomwopc2'
        b'HZg2HZW2fQWPQcwcG0GVBT/B3QbeVszzR5L8gdMLiW46KB+cltt+tqyRRYuCt+wJQj4uEe4i70XCZYfim+VGNucJq9EucEttOzgpy3f9SwaLgIaf6qTFdhaYy3TJ8/Lo'
        b'UfxVdxkVW5DLoObtLDexrTYvqsLemvgKT4nMnSdsQZJ+F6pVQGEV84JtZKAD0m2RVJq/g8JCKZRASSlJ52y50FUFHjelsH7Zk0cWoxOS95FsRtmAYxRWLwM0onSyjspy'
        b'FyyBo2VTo0yxZ4MroIcBepbNKsUynwsSz2v5HiZzpuTgyAW3afvfNXAuXJ7hhG0FbsGTDNDhZZv7cecQu1gVEf2riz46dCSucMRLd9/Xcz4ZO2z/Ucngn8+oJqvqOmk/'
        b'mPOtzpzkR3MePYyxaIhZ4LrC1cZj9caHu3/S+3u99ZtzVvyNtR9E3rc/kvPxlhCr/6T8ap/37oFf//JObefl9jfOlm/8SuS8qPGbbfPf6fdMaiw9YxTca3h8/y/t/z4a'
        b'ENEqWbJq9nveS/eaBCSelgYc1Xn1kt2S5G+/8E4+ZX1+63fayQ27ys6WHfogPln9naSt4fZ6e5yumg04atxoNt4TpR6xxvFIQ8j5is4trQ8OzH5v0KJiqC1gzf1z28tO'
        b'21mciBvRiowoMLAe2pV5d++i8t1hIxf832g8v0fjYlrQynff++qp+ltRPlF1mwSzxabv7F0n1cwWtuf2pLZXgk1c4Ya5gTcTkkeaJAN6q2K3BnPuGu9obH+9PL21pmJT'
        b'esA5rwfSkqG/7S78x4OCVPXvGzvntya8e3uMb/rv//xL95XP/nXH7C/f7Sot1ptX1Nbs8vWtvT76Nt2X/5onrPg2J/TE7q8/uXd61sdfBp2PKX2F35zEC/w62/DP+Qu4'
        b'ILSj+mlgoG91g/rbbaOBi77oEjjqxGe5PbrZlZP9yXvHYyOYX226kD5nuHBO5U8/zFkRlfg/Ix/+OSh12avCwWtzC7edPPx9Y1zNmyVnHE7Edfeb6L3v5Dd/9MtbcO//'
        b'WEs9z36h9yRvt2r5/LLvqm84zrpZ7HztdVWHT1oL/5WzKe6btd//4P/F35r/fHEXz4io2FZ4gu4JnGMfPMoAF+awaI/284hY7ZKr7oAIHJKFFoB9oIXWb9S6aU4LiFC2'
        b'g61qGUCr0nbBG2HYfS4bXJcHV7NVWkkUcHagJ4lGiLPZ8fAqDsdWu4ZcgTeLkuTgyCQwyACtGvAQregSglaw32n9s7zsQCfsJS9eE7AUUZ0obH1iR4EGKGSAPthXTNQi'
        b'xgWwjk+M+vxVTu4uOP1EM4uJ8+eRAYndBJvlianZmaAjkAFueBfSEQD2mIL9rjF0+mjYIc8gbQ9307rXW6AFAxiqPVG31oJGdNmSCergDXCC1BwFL8BLru7OoK5oPMUf'
        b'W4kMtb4NqCHaTNCQOkmhCRuX+tPqIHgcXCDN1vcEkliZvlpnNmsl6KCITgp2GNgSpRQ8HOcWAw7DdnwsuSpT5qCZDVrh7Twyuo7gxGr8dJyVd2yCEqVswWTPS6F17ufB'
        b'AKhEVcTB6skKNNSuFthGa8336MNbEwo0VSCOiZtQoO2Dx2gt24EyUDdFhWY8CzbAPvbcrWAPAbMmoJPhjIIWbZIKLSApbQ2QJRypxc44MjXWJrCfQRE9ljO8zrP+v9dR'
        b'PVtoweOgyBpN11zJExsq4sHKzad66ilcJMqr15i08io/jUGZmI0jZdeOGHsSZUv4nbVSh/hhs4QhTsKYseWopU1bqii1eWV95JihtVhZwhoxdBuzdJHMHrb0qYvEUQOz'
        b'0cMGnqOWdhg327yqLnLUwFQY0RYjimmOvWvgTGqdN2wWNsQJw9BbZ3HEiCFPskQGvRV7NwdKjKXmXnXhGIHr8qmx2Zg5l3iXLh62WjJksmTUzLrNReQiThk286gLf4xW'
        b'pFWbq8hVnDFs5lIXPmrvdDaqPao+rm6BcPZDS1v0emMLYUnDNqz7Wiop7S3t3C51CBm2CRUqj3LthUqjNg7om7GlmN2wfYxrJ14gSe5d2rlaah88zA2RX8YfuPdWNm15'
        b'ojyJQ6+yxGrYao6Q9am59ZizT69vl45IS8gW5oyZ247aOpx1aXeRJJ70FIY/NLNUaNyYsTnpPn/YLHaIE6ugJpim+Ppd1LKVqyRiIGLEKqxeo45dlzVqYCxUbQidriCz'
        b'cbpn4y218R628UX3pdRrjxkYjXLMmhLqE8RRkswRju8Yx0ZsL2GPcNwfW1EmFnUaT8wpc+tmRzSYHGNyX5h4o8RmhOM2iq6GjZqYCiNF6uJkqYkL+svYROjbUDZqwRUy'
        b'Ri0sxUqiaImy1MID/YUexunVM8SLJTaSjb1hA/Prokc4c3F5XH2c2GGE4yx/QQROKo6+x9fHi/0k6lI7395IqV3QCCcYld7jOEg5DmgYOK74npj6GGHJCMee1klsZKBF'
        b'IjXk/UxyZAAdwxg/1tt+SjGhMoS0Ea1XOKFMKYR3fDmKhBn3Ka55umZhQrswiLULv7Ur1VE/iudi+QGrF9IYDIYL1i64/Ig/XsiZlkWyHJNOW+Puc5WnaBPwiBGJqhx9'
        b'NKopaBNYVSpVTFkiR1qjQGGdQrbmuP5A+aXpD/bwmJ+GzeQVJNcfTGRzHHfyIb5BL9kBjn5GHt6Tfm6GXAYe3HAaLEua8gwQMPGXw0oGdGt0YsKc2V7eWKhfLyjBUM/i'
        b'kqLcgpxnNoGOKzoBfJ0ab52+/sJuwKrxtLzbUgF6FJx+OPDWb4tXUUmRRJRgl8FqvkfOBASNRMPdiUQFImgczVtO8GfqTp4T6RlPgg4ad3V+uxms0UNy9qEp2R/hfu/c'
        b'nndKWMU4AM2//0dzb623PvDSZGetiM9XvbH7U8PgN5T+shvMY/yFcyqofN/Cz46o7m6PMhlJKWt4b+u6bzaWn1Iz0v4u6i9f/vD4KnvurMPZ/8j68oOhr5tUVjwQP3zP'
        b'cHt2a0NF1z8Luu6EWfOSd11Sz7b7uEAr3nWs65UUzrHPXhXt+tNfG1+5eCLNM/iffl/U7DV6zTOr4z/bv3N6P9RgT8dbHepNHQb/+pr14et2dy99xVOizZoNmmGIyQX7'
        b'EEMrT1OcirgyPAzJ8Ko5tsGxIxUjXMFuf5LODAdUA1en8bjsMNirumkVuSUVNGKbOGbeLplOYd6SaT4YHgOHECOIWDxi4W50wEZuu9KXnDxsOmehXUo25DhvYTmFik2+'
        b'TLiLXor2y5mf+Qf8coztxUnDxi7YCmQuLJUa2I86udZFCM3ucuzHDC3HjG3EzpLwEWOvMTuvXpNhu0Ch6qiT5z2nAKlTwLBTEL5Tik4JA9MhA4dRB/ykSX38qJ0rtiec'
        b'DL1nF4QOmGG7EHQopkp1uSSzszjiA12egk+njoJ7zTgJ/YOHR7HO9JOBPhJexUfCbw/mFk2ZJw4+FAozxg+FFzkPfsA9YtxXKc/dgNWe/9fZA37unO5CU5SxNneTLACp'
        b'LCXLpJCnM5D6cFrzmL+FqCpz12/Iz8LK1qxMm2ceC7IBmBpQExU/T6Lf6YSVHU8jR/eagis0qoXWG1XAXTPhs9ONVXNhzeLcG54l7GKMDn+U0I5DhtDpLjK9M6pLfc5n'
        b'7+mt/ikmRdDBO9gam5yvqel1zfF1/U3CB3nKS/4kNMkJpP7Rqba5pIbHpsE2J8HJ9aAHnB8XvnE0wKsahCb5mJbRYncE3DUe0A+egHuIKLgdtoO9k0lSADxAYE9x3t/j'
        b'8A/R4Ko7kuURKboID7rDqmh4KM4SDCKhOTpuo+wRPuhSAb1AAtt+O0PDfV0BPcnylV08njNh3NQy5QZCSLxpQvJ4XhaD4hiN24SdRgxc6KByd5zGCccDI96wkeuQruv0'
        b'bA6vPWP/Tsvm8K6yQjaHZ7VMpKmQzaEwE+1K8xcNTE5aV3SegVWB8fFJkfFF/8LN1f2dQOUT4d5wPBYSJIG4lRN3PmLBIowmIS2kLzzT/1vx1ZSaErt8OmfsgId8Snxk'
        b'bWxrWyYPZ66mpfutEQ5nbtdeNqLl+ZRpqZXBwGHMvR6Tr09C5VHMo3EUcz6DhDGXxSPHQcONA6oW/qiqo+X3hDslRPgjLY7IbkTL6kemlpY1rtL6Mf72rRV5HbrwHVOV'
        b'DpmOLqBv33LodhSPaLk+ZZpoWeBLbo/xt2/98KVlnb7X7Mas7To5F8O/ZzG0Ax7OixgNnveUtY2hZfGUwp/fKaHix2z89dttLPxQRifrYuI1zrW1Q34LR7SinjITyM34'
        b'8zv6E90WzXhMyr9dSZ6x6zToTLroPOQc9ErEiFb0U6aRlsv3FPrA98age9HXb0PxnYkjWjbfM9W13PAV2yf4G+2KjfU9MaALXB+Ph740CV7BX2MT3JmUs5PSJtDIKf0W'
        b'LbAC0AcPg1bQEFIIm710EQ/UDwcN/WeDnRmwRzkQVoF60KAKDsBWuNtaC3Epe4EYdIMjERGgQwM0gGqGObwF+uEtLSAKhJcB4nIE4ArsTNLCaLpK2BMSDG6B3ihwayHW'
        b'YcPqLaAfdIJuj23gZCy4ELwN3oRnVWAvOIf+X58FToOT8EzORh8HKPJG3FV7AUB0DXbCS7B5WwioAYhDAxeNF24MTjACNXZwZ/j2PF/EX90E/bnBcN+6hWbWArPIQL7S'
        b'cp+tHgng5HILd3AEXgkG1+BZ0AfqCsA5WI+quRoFrgasd4GHfdbAg1rwTCbsNUDMrhg0wA70fxAeSwuHxxf55oFDGfC8MjgBrsJ9heAirIcnEuF50Fu2Hp4Ct7YjqtmU'
        b'BOpNYce6FYiNO+VvCC9EgUEvcBD1vR7U6kWAnkRQ6cRHDbgKj88BPdth12IgYsAz4DjcDY+CFvT78FpEaI+DjjIrlgY4Ci7DNh83eBJeXTtHPRheAfszLMDOhdbR68Ge'
        b'TFRxUxy4wcuILLSOhLW58BZsjoGNy03A+c1hcABcQhPVG6IMhIt5yajnNaAR7FV3TIJ9JrAddqC/+uPAftCSgoajETS5wf45oQ4h9hwDeGkpKmjZ6rTCFYrgOV0DuB/W'
        b'gStJxai0XlvdFt5GT5yDF5GocQX0UrDJNysIilaCZh9wQx+2aafHgdqcklC4cwlssgI1a2arwttgwMIADOSD2+ZgXw56vHsDPACF3hawI9N2aWqIJzyCVsIAOFMsQIvu'
        b'GDyepGm6srwgaCu8bLHKEhyPBx2mK2APGqEmKFFFnbmMVtRx2DEPHlQF+xfA615oIo+BrgDUy27Uvn5QmYLm4LD7XLQgqjeDS8bmsBqNzyAUa+9gwRvwwEJ7M3i89DBa'
        b'9qAa7J4DWpeEgVq07DXBDdhnuG0emt+zC8BOK9AChe6afvACmqGL4ARrATiTIbDjgbq1bFDDrfAEp+eUlq/VwYnpQQeUoJE9uCFtGbhpmAKOzwPHwUVwClQKYIsLbHJ1'
        b'hAPwOk7P3KsGj5rDqwKlDbAVXE5eXjYXNm9PzAddsBkNxE1n1AucVvl8AT8IVXHCAjTDXYtSUN0NKaDJHwjB/nS09XYxA+JgA+h1R/dcghJwbvuK7Qa6KRXpfgtzYIve'
        b'Fj89eB51tQYt5Uq0K3bPQtvqwELrWPstjmixHQYi2O2NFnkXWpwDsEoAG/LBDdSnBXAQHFCBp0Nhw1bQVsoPy4XnneB+ZyQ/3t7m71EB9q1WSwQDJlY4ejU8qzeHXQhv'
        b'p8FLTFi32UiwAO4Bferg4I4oIIS7LBaC2uVopsVgJ9ybqQPagCQhMdknQ9/RFHaGLVTn6Ht4KZn7JqNt1BoLqxLRFAvhORNQhejKTgE8MxvN5SDYDfeyYEM8qIcXubAl'
        b'HlanwHOgj42BndXGoAN1BZOmvWt88OiCKtgNLpdtNgWHrND7sKZashktiP3leqpoQ/Rlw6Pw2jYfDjiCxnEPmp9eRLquqOZox8A2U8RYiVOXwi608/bCfutV4GYcH9wG'
        b'Z9XsQUMxIgpnwL6ALNi3Hh5IATc9zLBhYWUC6DdHi64LHloCGvgxeivLkCjcj6iTBJ5YAXahLXQbdWuXD+wycEq0N0wAu9CgX1kOT+ej4ZMkgEs8OKAEhOn2oB21d1/p'
        b'XbQmE9F6O47WZAg4jNckavc1V3C5NAC2rGSjesVwT4EAiDdqoJ3ZNGuRGzijm8YHnaHgILyKRusGbDJHa+kWWtkN4BLoiQb7VqANu9cW3owKDQ2BwhhwMlNXHe5Fa/Y0'
        b'WlX9YI8dOM7dhBZxEzMU3NhCzfaIhkfWlbiiaesDZxCDWY0OkEHYgHZdc/qKVQWIfHS4weY8NNyD2GGnGq3Wc+AkOAaPrlyACONtV+NlJatWA3EcauEpWAcvO6PdUT/X'
        b'1mczPMhRA9cU1yzaIccWmaJ2XCmDle5qFeByAaGZR7W3ABEilmfCYmeX22SA3vit24xYqxeCGmOwKxt17Daq4AwiTZWzQ9EKFqqsR7Lz2TXgiBaa4k6uFjgyB4qigLgE'
        b'3bIL4p60wRPoVDoLduowYWUIIiKnDVVA/xx43cQRLYZL4LoPvMUpgycLDLew1+bDnUheH4D74FEdNFCnUPfOwBugbxGazQ49WL3cci1aa5Xw4jxwCg35jZVOODD18s0W'
        b'aO22rw+BdWnoBGvigc4ytCUOeqCp6AjzQVTuAJpldHKu9Fs3C9Y750HJ9vna5aiBlWAnWskdoM+b65wpwMnlYb8mBx6B12GlJqyK3FEITvgkoRUB2regJhyAh53BFbRm'
        b'usDhctihYm6PhnkQnopc7gluwRb1SBfU5X2ISIrRwd0cAfoW5ixBU9kHdhcvRxMqQkdiGxgshzWbgHCVShY8FpK90IMc6of5JejE2VeK6EIduudY8ELjFNgEmteBauYm'
        b'E9CC1jcaQ7S+wYnUPNTO27CN5VAYEwkPFGjB+qxlKpar4Xkz0ITXlifazx2ReqlupSNMguA/vByT2gLCYNwgvhuMBVZpQKwCRUvUGeAi9harRXtGCOpKwCUKkVt7Q7jT'
        b'Gw2w0GIrvKACroNTWQudwfFw0GWAToPjpuj2Wm3YorLeIg8tmuM6aC8KfXjwVrJHFGhevBUetQAHY6z80UHQr45G5hasUVkEOtPwXhEwNqzEzFBrAeyBg6uW5aMz5DzA'
        b'NLgbUQLEhBTOBs0G81yX6MOe5aA+LQLsXgCu60LxwooVaGTE/lsNwMHE2OWg0wFerrAMT0OU4xyakK71aFi6QPOKLQx4LNIXXEvy2qodDneBZiAMzUBH8240zx0memi4'
        b'98FTLHBbDzYkG+uaobOvmgPqVsUKktDevem7ODAf7eIjKeCIB6iM5XhyoCQfdM9Du68qDxx1hLvDGXCn0iJwPXM+aIzMBX2h8WAQVM0PCF+wwwyK0PJHdPE0et9+aj2i'
        b'wR3wojIQo31wwAjtl0totP6/8r4Eqqrr+vs+3nvMyDyDgAIyi6ACMgiCyIyiIqjwZHgIiIAPnqIigsiMyCAzIjMyz6Mgzd4Z2kzFmMGQpOk/HdI2X1OMSUzStP3ve7HJ'
        b'135p/+1a31r91vrQdd5995577j377P3bv33ePfvexDYnWIZKfTLTNgu4dwVnz3mR2jaRr6vCBo9z2OVDkJKfeCgHig9kkAl0XIGGK9qkVjOJF3HgtB42EQh2Ek6Uu+ON'
        b'Y+q7kTS+GnsOEDdiE6OautA93Katbm+XnANq5Bf9DGDqMKnhHExf3ElGv4yDvlhJYisir3fHZTPLySRQmWS6jVVFrNHay4FBF91mPrSnQEO8+qXzodhGV5kmw2qE2hS6'
        b'mwHiBIUyUCUlwVfqX6butZILHSLPmRUFnQ4UEffohascJkfRn6qDnWKsD6Tx7cN7J+H2KbrFUS8YJTMudYPryNr5MjYcpSZKYpPPsy4IC87q41Qm4cskFpn7H1fEccMd'
        b'/oeMofWUtE6GXbhJYibuHEEb37EIW5znncUqYhGerrYw5wjj55W2uclJiMQ2+Udi7T7qC3T40Agv06WnJCSlWRaEorZAsTMW7ohjf4ol5B3PvOypvDkYlnEsHu9QnVHC'
        b'j8arJpBvG0nDPS9wJSRsgAWb3XtxKIZIWj0uiIliVpEXGyQnPYOEa4VX7fGWBilt6b4Y6AjChghv8qzVYm9oPmpDtKMH7u2hq1URIemAJVUy7tvQqYYDAVC1IwdrN4Wa'
        b'nD5LYFcgR+bRfllRBOMWe/xC9DxVSMOGoX6TvbGAhHZbUcMNp00s5fn+eM2M5JhvQVrfq25IDr6K2hw5iYUxcMsHCJi8yA0SNhFJwEUR+5CM+znCq3roJ1/SQ1R/nIaJ'
        b'd9A+Eios0slNt8JwOBYex66Te6A8xC6UxFYIZb6phuEHDrE0pjwmD/rirfFaAuRrXjbFRvJWNSdwVkKq03AIh05hqb0jNMqQnt0JwRIf0q4VgvWR0zEUlFQTdJfp65GI'
        b'p09hnTuWwJ0MVxL9XSco9iKl6cGaHdFaSbvdwuOh5xTOZ5wkXO5wV1W0cHbR0ne2JlCfVsYyTb+wbeQLV7Am0ALajlLDtSqkXPfPQnlEJFnJ4knosIQ+rUScSKdrtlJP'
        b'b8eSLfSeEGsTAtXCiAOMKZE8y7HxNJSZwGRMZqzuXhhMo0oj0JxEANHMT6Ubyz9MKj/tDDc9YXkbOdwFvH5VC+8zaewjCQ3U9oL03Q29HCHzJ70sSOfUcpnUMgeHxHj3'
        b'ojwxn0LNyyTFAktjornTRo4aWKdGfPJYxKUAqL5qYnFZCsVxegdFyhHkxLvZf1C4i9C/gaCETvNkmVPuAZhVU4HhHBrgRbwTuVeJfOYsrKiewl5sTiWf2y/EfCnWHxHD'
        b'8uV0OtQaH0OEZpTjEEAc4h4sp5AJTMXrYZHEBHutSDu6yICGjqRjTa4pYUQbS3uT6R5KY/ec1VOiM2oIP1isrgiNJro3eOXwlWPJOVuUw5CYazf2biH47j/plbOJJFwB'
        b'rAFXw3x6ppcGzKpmk3wKJMQrqqPCnBXMcTw+DK9Bw2GqMgvX5XBQRYylh2zZ50auQUkmtKhSvHId2nNwUkQKO75d2TaIzZ+VouafetGLIqguYzLUMYKcCkMrAYmz3pE4'
        b'Z7WuFtxKNzXZTxY7bIwLBwi9blCQMk1eeTGdXeuItecssG8rBbmDeP0KtFjZEwjOy9HFCrHP+YDYOcfsZBLZegHZRKGUzKFFEWp3YNUZZ2wNsSCLmNJUz4onEFzCweM4'
        b'GEPG02NGitjmQsRlzhlKcD4zHbqzKRIvpYhZ11GLQLNxLyH9lPtWuu3qZLhBvEGId4+SyywlZa3zOoMzR/WxSAC3cExM171NCtfCbL3gmXk8S+cgje/EFhsymttQk5gN'
        b'bV45UL4Vy4QnsSIVmj2o7iRME/FsxLJIchUVRE7atEI2wZ0gy6vhpKTDOHopOo3oYuNhr/0ubIA25Aa9PhKbkzBHWnUzFCYup2glkf00q5KOT9tj96HcA1jnb0MaMaq7'
        b'BQu2h6QexapMGLGW5Z6iC7BzDQ4UeoQzvO0MnVFkzCU0CGbVg11Qjq3ZDLei3Bnucc/SpVBDN4NtZXCCDngzxDP6LTYyP0+exKpge1nqcS3D20tHoNCfW97t4RLK/hzD'
        b'23eU4QUx2BoI4xtnFIiRzTnLc4J8Lldeex5MSQP57HJR7CLfcZtc0g0yihZvZZL5WJ6iyQkFaHCPUI3TJNdU40Cq0EVSqmcpuyVeD/QPheJULx1rgps57NW/RP6pE9oD'
        b'1XxOEIJXQ1s8OZhKwtgpvLObnXah8Lsmx0HqC4M6LM+7Ar3iOCxRgtIr0CmJI6upgxUvyD92COvDaCipCtli0X7a7GHfEdSPJUc1iMe1bqcRu+103JwUr8CYYoIJm2hq'
        b'+iYTTpctEhOyjpEbrqOhpjgnJReKHcjF1hyBaksKFyZJIY4Th6mxJIGNQK0bBUtF2aJQuB9M2t5DvqKC9GrSiAKnQgrOSt2sc6HEmTjcIoHEODmFDhg3I058F5pdxa7n'
        b'+XhTTqyKTQFnYGA3zktsTXAhFoeOB2rDgFyuVBwqERGK1kCPAjt7AE1G+lhAsh0iOCoghOw7eZzaqiSRNkRrpZLNLtAtVO+irvZ5GigeU8b2hFNc9NXCx0InimXySSoj'
        b'SFi64gSVfByPtgl3wqIogrVOdxy3JLvpd7YFdo3sAFS7Eye6Sf3Jl+hKBeSfqrOoDz2w7HeCOGUdlNtAuxwOp2B1ANTvxY6jFFZVUvyyLKeNFafMEqx9DXFYHupPQb2E'
        b'7GTZepMUBxIkEuyjf7VXVOh2y3ZHRlEcOcKuL3TGSd8DuepJiTBjpQKzm/BOANnVNRcc2R5Ipj0AxcjO75SpUhg/DQUG0CYiGICGvQHHw05Ijh3XJVJUSs58QdcVb0m2'
        b'OxNOTJ7nEzz0wrC9DqxIk3HIheKBahtNbNFlgZycXonjVTLSmV3kMsrYOSnrsCRyqjC3HVqzSaFKYO4ElKSTH++BQT8y35HgqzAioqivnYZ0JGgPNwmzxCcvc+fEaYqo'
        b'euGmi65hni1xz+kwNpTAmiS4h12OVKzgsqkONIiz7LL1iHQNeeF8rAoWqOASD9pjiV9P+kn72fdqwLjj38/OEIaOepl6q57HYR1ZgwvYmUi2URBPqDxx8ASWB2np+FDo'
        b'sgKNEvZJMyUt4XFRSAThTrWzAfviLhjTx74desFmHjB1mUKCkii9cPsEHznyafOHIrlpmslwE7pIC9TtJoEsKVIHJtMJYLrInywn46wUZq1hDCo8bMks+rAtnb7cPL8T'
        b'WsihEbZXs2raDRM2MOqYQWS/fQ9OJp4gIReHRuqybBMJpHuP8dinHsmmC4zIdiYOkH9rFxhhvy2B0BR2a0bC3S2EqVXQ6i0JIZ7dfprYZ6E3C60TUHAljQi+oTdRhW59'
        b'VXZyKwT7L2n4KsLg2RhC4cqNeYCsBNL+6jMWdFvkzLAzj1BgwYiM4DaFudAfGsukYsm+NEKctth9p8krTGGbmO6wNptccCGdwSauuZ2QCGNpB11wWlcN7m89TorQpIW9'
        b'Pg6sRGzyCEUHdMW4kMIyDerSIIUPSxJcjhV6qGGz4Q6sDc8kUKvUxC4NisLqLhOdyoeVc8R3pvfCgHq41V5nc/K9HVgfLY+dBzJI7q1W26SbrVN0Dh7QUMcOzavSPSpQ'
        b'vE8mjFR+kPSvDPryCAc6pZEBUHGCgPaaLcxrickql8gsZq8cO0uuMh2q+DhB34eJ6y3EnSe4bfPMjcLeaHsCpRYcsoZ7+2JhxMQikDChjh1jGof7BGvNhA0j6tSNZVzJ'
        b'OxhCjfbsgtqz2gfC6dqLhiSSe74w70MYXCISbtmbDc2h0rdIVy2J8szB7cNY8V2Ae4yufgMad5qwMW50hBIPZjSwNAzGZO1h5ISsDvsgqhlM7yJFGHOLxGUod0hxIxWt'
        b'4aZNBrfYE4ixU3XN6nZQRJhGOloM4xQe4P0L4fbWNGJDuOTlAwNG0KxqZEDCr4TpRDLW7r0eDAzoE6wMWkCzG+abEdRNwnAU3jkKrU7RhDolgdCWGE0OYSySpSdd2Bkt'
        b'2SbkJ3tgw3bszcEyB5jcegQL0x2hJ3UfOYUe6nE/kcs2f8IbWAjBcrtochutNmTN1+3NjiVjr4v2cQneDyN9a2AXYuzUkoc7qekwTuDVTlcYD5MjM1jJDKfQvYb0pRJ6'
        b'LlGnyVUZYN92qJeSM2kMSyVtotCl0U4lHYoUTffgiFsKNgXpnIUlGJBiqxss+kiwkWR3E8cjN8PKEcYVr6vI4wqf7rI4VBsWhOzkSLcb9J3WCYCG/YYGbhR2lVOXcMSd'
        b'QHyJVGKMzGCO9GD5HMWfw5ok9Ob4BNZ0kpKtCFNvyJz0OX1OGWZOYF9qeFhKUiyR1MlNdAst5G+HFHEyGCoSoDHSVhcoyriGN1KV43D4CNzU9D4Vcxnbg0KNd2CNI04Y'
        b'JxO5cJZhWQmBUBHF0XdwKSQnl3pfEa9GjqsT728WWECDZgQWJ0QdiN0X6k8mXumJ9VmuiWZ+uLCFIGmUBrWCokNZEeHDsFK0EYcxLGzfIlE2JeyECZzZYk3G24TdF8ng'
        b'qmDcioKgCnU58o6DmVHadNmKRFw+eI5G5wYSOahWgFkNdwcCtfaLmldVt5F1NRPi3LfDUhG0u5wlntKrLPUlTpOAleZ/o9gU3c7yZXTxLtZ4q0qgR0s2dRth7m3qzQQh'
        b'YsMOXtCRQDaCSsD5BJxSIbuaoc532rlvwmqj48YC0vAW8t2VRN+HL5G463ceUTgKo7uxJYqUu4WAe1GJjclhyOgoyZviaqjSwaLD/izz0aTGRkQm0OuEI/ttkLhMkDEJ'
        b'qGIL3HEwIfOs94BWbZJMaxb5nH4xTEQZkZq3yETsNIRufTfIj4ey7cR8PQkPTY5aGxJM1CZjoQJMiCVXyW0VwnT0bvIpU2IWxCvksg86w4CyC0n4JjbridicVhrYdVob'
        b'R+WtLvl4nNOF2y4wFpJLWtVLfq8Hm/VxNjsIBzSI5dxk3wuYTL7gkqKvhIawnRqp3eKaDT3ugh04stcc7nopYls2DqslxehBn7raOajTxsrg09RQAdyyk3MKpeEkkkFi'
        b'mReYhmZ6u0Sk4ugWAoYBsqG2U1twxZ+gqxFuB/p4MtwSm36WfBNw1cKsUhKW7CLfTCpa4QvjBgo8QoI50UkCvV4aknlqtUhd+xi58BvQLQ/XkzmuOO+GA/bkBErzzkOt'
        b'60lkp8q7GJiKdTckTFmE4pRtZGv9etBpz77jgMxinELrtlMK+rvwni40HnENzjxAPvQu3MURAZ1yDaZMtdwo5uiGPh8YFBqRObXBioW2PrHZGzZYnYvVrHjKLsAkP9PS'
        b'nfbWeEDXtmO4QM4SG9TNPcyx3RWaxFGkO6XYICHntJxzAsd2ehyFwrRsgsZbDsxu6IvL0YqPJ8mnJeM9uBEP4+eIP9cQfbtBEpvYQ8haZO5GMeEClkj2BCd5EhKUYvll'
        b'exLwpDKPtG9QmSXGNJjNiVk5V2A+nF2EBi0hFKPfgbHMABw9xrnGabznccILGq3IbVLse8ATp4OIvo0pJe4gHtcUTdaxIhdPZC1/S0qeVIbPppk5QXIkQyogfWYtaRnv'
        b'2RIUN7GJNdxwWo+IbhTWKab4wpA5tvpuhxo+ubcOFbaGp1oKRYtLl08HBBAdKAw66maKxZcyiFwvY78PKcAk3FHApd1yaeR0hnjYeRgXLa5APsV99Zb+qkqHsSGR+3lt'
        b'hJ3pv3oZbsEiO6fVDQsR1EOykz52uohYbi/0Behg88WIbce3U9/qcdADC65iFc4YkWssPQl3jhLZmrGXTc5w0oPxAEUy/GGqeMOJxFqcRkawrIodMVBEdGCcXEvVDqw2'
        b'lKM+9irY42huMvG/4vgcuO5JPrkKOvg4qaeArZF6/nqkLcNWQjVjnN97FKo3ecsTai5i/gGiM0Msou3CUTYnWj3edNwkPghFJ4KtXLNTFXFZ7dilbQTwRMm9zh6Em5lY'
        b'53SYAmqWhE65JeeScpRtg3H1PcFkxJ26sKgIswesoi6m2eBdCwKuOYrYimJxMUcRi/cfJtMooqDkLsFODQUsZiTuxs14W1mRn6SLFcdTU2JEztgSvIm3X4fOG4EaWahV'
        b'1yWTq4O5VOVA2+04u5md/iTHnQ9LBjDH/oTXb2RMMV9l/F5PIu/tO0kanTBqbJ8ONSFbySiqKO7JkkLzThqF4kCc8VAi+n6PeEHb/ku62KWcJ6Q+1PpDi6ZCLtlbLX2r'
        b'gRXb9FMXod2MkLpQwzUcZvSgTc3FU/kCXgvCIiORHPYfgdpkaIchUqOqiGh2yhT7peycF438PULfcfIRhdjjgKV5IjNy00SBIqnu7TDqzLVjOHvJgXgZ9JK11JGnLlWK'
        b'jpceJ3u8A6wvIUbas5v6tnIFbm3GWjGR7plzpC8jF/RIrYauYMlVKCMkJ+ZxLQoaPSkO/5D9IeA2XXz6OzvwZiembh4jN0wglrrXNELVHKvJBo6ZX6bDbfqnExT0sEff'
        b'1RzZybXR0zAsF3CKrjLLvupFZjfOGsIK9rukKlGrRdiRDeyvwAXHPaBWAA16hOZLF7A5GLr4tNkHi2JyN3fzCBxvkjndosGoUdyM3UFsIj+SfSXW5uIK3PPQwrLdcM8e'
        b'u8xDsSKN/akrkJ2mSjxI0imyJEgpUxbgoNiANH/6oilZ+cKO8AxSuR5NJ3bJqKMONmw1scZWy/3EGMg6fEkblrWScUYZW9zNsFeFosaik1DoiwveMKSQQ+hSR/SnntC5'
        b'myGlX5SF20YB0KhEIUKvoyp0+uyAZmciC0V6R7Tx7tadsrJYesgXy5Twmu9BiojvORDDKnHDCdVMnNmuHOwEXc5Y57PHm4QyBS0CsvsegvviS6dM1diFqQsEBQtQYEq6'
        b'PsIjXnb1/A5St7oIKFLitGJBROi9csaSAKENSzJIan0sEMw4EvOoS0qGblfSZ3YSvg7LdXFqN8U1NaehVBa6kk3hrgDGvPawKQcpRs8/RPg1HXKBHPp9Z1mi1d1QaYWF'
        b'diSYMR3ougKN6qSWpVvYH5SFubK7Tx+hlm95bMIG4g6yF1gCVKi5K53CPaLz1wgjaqBPE5v9dHPYZysOk+RaYDH2vAUM2sOSP3RbC6HZjOhVq4xlFAycIXc2At32IiJA'
        b'5Ll378nYCYtB285hlwU0BUGfreN+nBKSS2kMNKOo9jZO7iAHN8AaSfNhDT9nothDDrhy1JzArTHi1CbRlSMG0aQ6pZi/K4Su0rTV08T7CkMEs/QMDuCiq7XMxisQZo5u'
        b'4pIlChkZXhSbKlHdd+OFzk2pJllOG4l7eTowJwd11nxutWikoTDYjoet7gzPlaHhKXHmWlKBgbxgrGKwxoHhObIpB/vcuYyl5MFS2TWgApLJIsPzZc+pwPyNy9+EmrTg'
        b'QCG0HNuYH5PDOroz7gZqSMmDw2VwegvDc6JDace5SS0KTomwVIQIo5UYnhvbQhFWbjQ2aIZL7Jyak+rGlFoesI2xk3Dhh7ZjhbVw8yGGF86QTC9vnDB3gGy1IlQWOs9x'
        b'M2o1zkYb6UansS8u2FaG7G5qYxIuBJaeZSfGlkMRwUFCeexneLYMCXgUq7lEtmZnuJfwVvCwNH1jHo7spMia58+9OJRbibvgyK3T9RYpnApxuxDBWPO53Rf2crvl31U8'
        b'lbZ8Zf9GfshiZmPnLeGpENfzHkyYtUwYNcWt203RLFllsj4llLqmNVZ05KX097y1TgaZWwRFbm9IDP50+anB09jar5p8N8lu1jJfsNj3kd7rFo7jNyvHfBz+zP9TYrFW'
        b'oHtDxSbB6Z+1/lfrB2/9ubnm7h6fgaDQ3zmZ4xvV6vr19k6Wv3Ayq3OyeOi0dcpp25PJozqJhxoSW9MaxdFf2+ap6m0xfdViamVU/uMDL38sNLufvitKUeu5r2c6Drfu'
        b'//3Msa1f5JXEmL3mG3Zh4ddbzFq+/TxY5aervX/afP9I26aXfhqZV/b2tfZa5fAnwTtyTYbudEWuKkdU/P7UC6/9Nnwx+ZvbQz/fenN9z1dfbc1tkvt62KDjkfTR4KrX'
        b'SwUfRhZqreweNjJm7B/b/lyQWV64Wzaoy/0X70R4R3cMHw7m9/5WzfWn236kb/Xeb+Rzat/70d1bwoffHIqyyNQ8+ZHbuMGvOl6Re/7+KZVvrW59/YnjTEu/9ILY7rX3'
        b'pZ98+aavx8vWr/8orjbL45UnTUnNc1+Vhg9Z23ifGJYzeHmx9e2I12KyXnu8ulB4eeGnXzT/Uj/kQWbUf0m98l85tyvUYn7aM/vxB5+rQtBXVTa/fsPtuSc/fmNTzNeB'
        b'MRVDyRMrpW3a2Rd2vmaQFePuWv66nmWo61TfxOs3Xh0JuOIyU9dm++g1DSlMvJI13fXp4kDY78J2v/+mZt6nwpcSXjrnOpQ0YPjNZuffjSztrXv8I+vP2g7v8l1e/+3l'
        b'57d99Iee1816Pnny8MbjN682z1788PHLh/YuybZEWj//wZcp53ZdfktN5SOjmYc7nuab/Fo9VrCimCff71Cm6fXjwLancR1df/SS2d8clv/iRc0/7ig//lz44AevuL6w'
        b'P/f0w9hPUitfdHyQ89AvTvRu0buXvp1aezQlY/Tp+bP4OPVjJxOYCNDMbMv9zVeHV7VCHyq/9obRaw9hJKxi2u+V6X1Dn7/83Jm5gqzCt88//8eM3xxLNs4QLglTU/5w'
        b'J6/X1eVR8Z9yfxwrjHy8ZD1wbfedI+nLHe/nRSw8uSZ5Gvirnz15uVXp6Ldqnvsm/vCRy67XPukuvVD4sw96dJ+78NG9+JN/4VsVRK+uSqwVuVWfPuQlxggCeDLYwYFQ'
        b'FbQ/W+U7IYZR9mliO+z52zUO8nkXuVW3WhTbVPyDJbe1qtRsOQxya0NFQpxUkqgoqBAvqFCVSJXJlc8Rh+nkM0aXBPIBeVwtazXI/67WBZy9cE5FltHz5itDOTmSOVj8'
        b'fBt7W8XspHPWeeVzUpxTpUOVqvIqijiuel7IWBtmbhKQ723E69zjzi4wp/VDNeHGs+ZZksSECmRhYSvWbKzVbcfpM0rftUjQxKZGK9+OdxO5F4S7+sF4FtyQP0d3mUUu'
        b'suz/aHOPAxOKM7IUwDXhMJcgTw+mt+GUNGDXD6XI4/LjYbWtdcTfP20r//9Q8R9fNfuffeY5guGW7Hr/k79/+Ej0P/7beIxeXiRKy4hLFIkufbfFPSf/CcWPf/nLX77N'
        b'Z9YjeYyK9rpATkH3XVWNaqeKC01m5bnNWR1OHXGdu1ov3T3UcnXCfFwybzYhnT80kTPl8JzfjzUw4A2nkPf1DJqcmuKad7UqdAQ90HMY132g57rqEfZAN2w14sjq0cgH'
        b'Ecfe0D32vo5ph0Zd+qqa+Tqf0YvirSsyGlrVPjXapfvWZRldz1KlR9qmq1uDHmgHlSrSHj2bd3RdHui6lCr/3Mz5HTO/B2Z+q/KbuW33B2butP2FLF/B/amimoLxU3M5'
        b'BccvNYwU9L70ENLWJoHCzqfK8gp6T7XUFIzWGbawZPQNS1WeCvx57B62fBohY6Jgtc5QUS3+nP1Y9+MximpPZTJkFNyeMt+Xn3HlEz4dXOcOricKafuRgu5TmTw+XYv5'
        b'vnyyUVJdvY0TBOz39X3yjNHmVXm9nyuocqedllHQ/5Jhy/+9Kvt9/Qi1rfdUZouC++cMFdzxdfbr0yDecaECmz/qBz4+3/hYv6TIdSFGTsH8KfN9+ZgrO4yecJ/PusJu'
        b'rnurcidECNmq35frXNmU9oT7fHYCdyB14wresmzV78svufJZRW63v/IxnoLpZwxbPpXI7FXQe8JQ8eU+GZ6C2xeyPIWtT2VVFPTWTbn2RDI0JAxbfsmVz1piN9f9hFyV'
        b'o7IKdk+Zvy8/48pn1dnNdW+VbXKC9SM8SyojeBvbVlRGPttD249TZGlcZNYD5K1pV9TfVPq78rFU1k8gL/M4WD5Y3lhmVV7/SZQao2FW6vOe9rZq3vs27vM+D2y85rMf'
        b'2Pi9qWbWYfZAzbzj0Btq20jPdax+oW32P9XZ8q/VMfpndR5THePHqnRbX637ZvN4CoG8dzVMepRX7f0fmh54qBGwqhywsei5w0cvRJF5VVEzxPhZMrVdknv/7C3L/x8V'
        b'3PKcUz+YLuFfwVnJI3ZRyncQa/tXWP86n3l6mMfjqbGr8H6wYJdrq/07qeDYkXxORtZHg3lOQ8nHmJ9St57IywqmcfxW1UVc/ZMgvo9a8eW32+2bE2ubnzdP9zNzuCvQ'
        b'PfkzKPzlZvOAp/tlHne4dP5ZK/aFknULY3eF0t965V59KJLqfuFmWpEm+bHFzdxarYMB6i/cOlg0eCvixu9uHSpsuXX4scWLb0dZPbaMfaFu69tvvxnTm3HGJ+zXP6k7'
        b'6fLSlybvxK4eX/pU8tbqL15d/dg/8ECgvdsqL9hY8nB+tDz71fthj068Hem6e1jyguOvYPzFi4Hhb0lfbEgfT8gV7ZK+XvOTyVeFJQ3yr8S089964+zsazF39yy+Iq3b'
        b'+tbD1jaHv7z3kYHd9GrxDRXX3/xov65nzvrEDeP/tW+Lt4nZl+px+XyjLS+qV9V0XNNsw48/UvY9cq5KS3f+ee3Uu1txl0HyR7Jz875VH51zrfqQf/7jT5d/U/HbzF0L'
        b'no/tGm/fWq56/iUMWXLdumPqz9ErT9RfbBquzPyML3RN9fv9krUJl7k48LIBGxCHh3NZQuRCKJRUgkkZvGsGoxyN1TNPCw63xwm2Tjg28exlGHVc4kMnxbr9XE4SHLfE'
        b'GaiAmxupkdlpYzlmkwbfAMo3Z0IDl6IlWwqLwTh7JDDUJlSOkRXIyMMQVHCJwOGWIYXRFdtlhZkM7zCD3Vgfz1HJC1gEE7ZYZcUmOqnkMQoOMtiWDC0+WM+1uQVGDDjm'
        b'bKPO5mQK48E4jidupDbp9UQuwbX9s3zMm7CcH6sSJmU40h4qy63tuXg58K/Zr2egbSNVS83ekA02HhrI5n3uxp5AAaOBdXxYhD7s45YYBmJzRnCQXdguZx4jh7UyUApj'
        b'slAo5C4tOJQT7ORMJ7NJlmOgi00mY8Z3h4nT3KJmWLbBJrZCYCgdh24cCmTvbpS/A25hMdevGFsvrLDBqih/vElx9yEe3AuFe9x651DoP8JmFgvFEqkdXWsHD4ZPwhx3'
        b'jI+tOrb2eMMRltgMP2d5MI8j0M11iwYOa2zZ1dQhbJ6xUJKMINqPMbwigGu4CMWcvM9tPRzM3hV1nsSNPXiHUbKWwWrsYTay9HQd18r6vgJcFzOKgTIwnqfHpZ1xwuJ4'
        b'JZwU4JAqzmRBGc5l4vQ5ildUGMZoq0AOxn034qLii9DFLQ61ZRtjsC6AVK5FBruwzPHzjQX00CnLJgo3FrGvWdxIFE5RxP3P2dfnsotD6oJhxIoGl839zKXBx76L4YFw'
        b'Y3uYvbUsc2C/XG4w9nBSsYF6vK6E4zjNvtyphjnMPt6SzNt4J2R+Aps5J4ZGuTKUzdkjzKVum8MIF06JBcg+Dsou89xu82xxJzRdZQykAihmn6DdyNSUH0MdsWd/K8Wy'
        b'EBlGwZIkJoGKYCzYuMa8LlTZBtnbhdo78PxwilHW5itiKZRvmM51J+wJpoEJdqDzyYCOwSh1QNOZj+0wlryRW3zMEIptA+xs2GwBJPb70MwoYbUMjspv28jZPRx20jZI'
        b'SDfVwvCCGWzaecB6738iBPqPu7j/S46STTnyD2KVf89lsqtUWZeZkp6S/SwqeYVho5I/5zNPjBih5iMVrXdUNj9Q2dyW81DFKt//kUCxJKQgZFXdrMf1TYHdewKV9wTq'
        b'7wlUPxQ4PRA4fSiwpe2//tf5UODwgcDiA4HNuoysUHtdhq+g/4Gy2ReKjNDkA4EZnftU9tAe4X7i0P/jxxcbH+tJ2TxGWSs//KvPL9KWmuFnDI9tVG+dT59//KWSDu0Q'
        b'aj9S0yoX0i6h9jdZNqyOK8n66jOor+JrzUdLGV87Bq147LY1n922U/Ldw0c3HpUbnMxmjZ8mTpe0kkDWhNnSzDTxmiAtJSt7TZCYkkBlRqY4fY2flS1ZE8ZfzBZnrQni'
        b'MzLS1vgp6dlrwiTiH/QhiUs/LV4TpqRnSrPX+AnJkjV+hiRxTTYpJS1bTF/OxmWu8S+lZK4J47ISUlLW+MniHKpCzSumZKWkZ2XHpSeI12QzpfFpKQlryvs31sqHxp2h'
        b'k5UzJeLs7JSki6Kcs2lr8iEZCWf8U+gmFeKdd4vT2WyjayopWRmi7JSzYmrobOaawP+gn/+aSmacJEssokNslpM19bMZiW4uG++rFCWmnE7JXpOLS0gQZ2ZnralwHRNl'
        b'ZxCdSj+9xo8KDVlTykpOScoWiSWSDMmaijQ9ITkuJV2cKBLnJKwpiERZYhKVSLS2KT1DlBGfJM1K4F6pvKbw1y/UHWk6m270e7bLDc+pf/HP1PR7reUKNiVvViSnsPRH'
        b'PE+Vx0sTspzuh8onXPlv8zxjWR975jl7JR9X/jfySTTE4oRkhzU1kejZ9jO++Y3Bs++mmXEJZ9gksWySA/aYODHMWp5bFb4mJxLFpaWJRBtd4NaNrxFrXJNNy0iIS8uS'
        b'LLOhgCnp4MZac25N/MYcggeNlTRN7CUxl2MzNFC/g6ggHefxHssIeIJ1ZUZJJV/uM4F0D09rPVNKbET9HXnDB/KGTUFvym9btfN6zhKtHtgFPZJXe1dRZ1XX+aHizlXB'
        b'zncZtWq9txgD7lr/DeK7rWY='
    ))))
