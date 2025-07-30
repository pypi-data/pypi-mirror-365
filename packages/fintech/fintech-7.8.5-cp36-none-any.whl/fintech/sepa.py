
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
        b'eJy0vQdAVEf+OD7vbQWWBREQ+yoWFpal2GvEgnSQYkHjsvAWWF1Y3KJi7KiAiBrFXqLG2DV2jSVeZpJc7i53yd0lVza5knxzuSSXu0suuebdN/l/Zt7bZZcWkt/3LzK8'
        b'mffefKZ85tPmM5/3P8jvHw+/M+DXORUSAZWiKlTKCZzAb0GlvEW2TC7IGjj7cEFuUTSg5UqncTFvUQqKBm4zZ1FZ+AaOQ4KyCAVV61WPlwUXzSlI09XYBbfNorNX6lzV'
        b'Fl1BvavaXqtLt9a6LBXVujpzxXJzlcUYHFxcbXV6nxUsldZai1NX6a6tcFnttU6duVbQVdjMTieUuuy6VXbHct0qq6taR0EYgytGS+2Ph984+A2hfVgDSSNq5Br5Rlmj'
        b'vFHRqGxUNaobgxqDG0MaNY2hjdrGsMbwxj6NEY19GyMboxqjG/s1xjT2bxzQOLBxUOPgxiGNQxt1jcMahzfGNo5oHNk4qnF0ZRwbDfW6uCZ5A1qnX6NcG9eAitBafQPi'
        b'0Pq49fqFMG4wAlV6WV6Fd1g5aVj70mbJ2dAWIX1Ynk0N1+oyGZK7lkNxme2NuGzkjoXCxfg23kxaSHN+zjzSRFrz9aQ1s6QgMThfiUbPkZNHUbF6mXsAPDnejG9nZxoy'
        b'ybmIRNJMduQqkJZsl+VFh7mj4TZ5gVyJZvePlSuQXM7hZ3CD4NbRW5vIHnI0gb2E76bmZpJWfaYcRZC9MnyPPJij592D4LEKvBXvzU4dk0m2LSWt2WRnfqYChQ2TTcH7'
        b'1e7BtJ6HarKfPjCDPJ2ZK97XkiuyFHKdbIJK+sMzI/Hecc71yfQ2QCM7OBScyeOrvMk9Au5OJofJ1Vn4Wgi5HkZuOXEzuVNHbq7ALWGhCA2KlavGkdt6jlVEXnQnkpac'
        b'LLKDbCEPZEhGXuTwEdw8DO7r6f3DseR+Nr4cl5lItmeTHbg5n7YItyblJeqVaO4c/OIc1VpyZhY8HwPP4xcnRJIb0KacfEUyPoEUazlyuh9plsCVk0dpCXgfvp+VaMhN'
        b'NHJIEyULhgm5Bvfp4JCtZnwsoQTvyjDEk+Yc2rEQspsnV/B+awUnTb8Mfsd4p383xcpAnET/r1jZGNeob4xvTGg0NCY2GhuTGpMbUxpTK8dIuMo1BQGu8oCrHMNVnuEq'
        b't56XcLXSH1dpY4d1wlWriKsFfVRIg1DGY11ZziuulYgVRq8GBEZoYoW8LOdcyGix8Iu4IBSOUHhSbZnmbZNLLCyPUCD4q74wqyxn6ejZyBYMhetdMfIvl5kAI98b/Tf+'
        b'dsrPnf9GtiC4Ybcc5K6qkC45ui71Xccfx/1OLD7a74uwtjAuTjfqS+6rhdUlryIPcifAjYj0cbBiWpLmxcWR7Uml4RmAAfh8cVxWLtllMGYmZuVyqDYsaBp+usA9h87d'
        b'rUEbnC7HyhVuJ7lDrpKbgK+3yTVyi9wIU2uCtUGhIXgXbsI7UpPHpuL95Oj4lHFj8B18VQ5YsziIXAZc3ufOgpqm28n17JysPHKG7MzMzSa7AEN2kO1wv5m0QoviDPFG'
        b'fWICfh6fw5cKoYrr5AB5muwju8l+spe0LUCoX3JoxHx804czdOTp6PSj05DspWSySpk0p3wTzOI6Gcwpz+ZUxuaUXy/rjv7IOs2pPM9B6b3V9dUHvHMiXC0c+0W2+fXy'
        b'j8qqKy9ZMrjry2KuxxzZ9MBwpnJb6TbtGcOH2lcHbKs883SsIXp3RrKsKgRFvx8yw5qmV7goJUrAB8k5GK/LMAvbYQx2AFpM4vC1BevZbXJuLj6QYIShgSElzQYOKfFO'
        b'HmgWckXB7er+eGdCYpw2LyORhzuH4c75lS7afXJxFrmfkEhaK2blpCiQspQjl/GVWPaWS4VPkJYMfHk1fgbY1zoufR3Zr+c8fJxeL3PQPrcn59HjqKmVDvsaS62uUmRA'
        b'RqelzjzdI3NbBToUTiUdrVnBXATnoJcOOlZ6uSeo1lxjcQKzsnjkZkeV06MymRzuWpPJE2IyVdgs5lp3ncmk59thwTVFeIeKJgqa0PpmUxhaCuPFcF7J8ZySpW7aE3nu'
        b'sATSmkNu460c4vFBbhbea0+v4DvgA5vCVIoPPMMIeaXchxGyHjGiuuMq91Xnw4i+eW5asB7fGe7MgVaT8+TFMITPpqa5I6F80lh8JhvKOT25W4RII7mOD7AXykbjLeRG'
        b'PtxRGPFGhG+VrWN9IreGUC5Gb8zJJ5cR2YcP9ndHwJ3ls/DDEGBVXB9tLcL3yUaOQcAtw/HdBFo+D+8LRuQIOVUm3tiPz45KMCoRtxifVCByFm9fw0DjaxPGkb3z4GrN'
        b'UNKEcvG+BLH8vmst2askDx0IGZCBvIB36oPYnbzFqVN48iw+SKk3/CcbC1h59Oy1T/FkK4wMeQ7+47ukiTV1onUAvq9cPxbKD8D/Sfiu2Lf9E9eT+0q8Gb8AmTvwfxo5'
        b'yNpKNuFtG/B9WTgIIOQY/Ce3EXtlEWlZTO7L8P0wyjThP9kG7IzewcfISRjN+2GpT8GtE/A/CN9mrRqCD+Am8iy/Hm+iYk0IvjWTtQq3km0JRTK8dQpCo9FoLXnkDqew'
        b'z5dkkL0qE0x0MkqeUMxqH+0E2raXHABkxLvI/XHIlEa2M+EBv4jPLyQ3nOTGSg4B6dvOk3PcCHITn2ekwUeNeAkDGbrQF6vQWvRk+DpuLdcEcqBDvpZ7ml8hp3SHrRlx'
        b'4fAe3pjs4Sr0nLgw5N7F8Dh4qs3qdFXYa+qmL6RV0vqVyD2NrhG835ItyRmMa2eQNnwDCGlzvgE/zCM79Pi2LDUVt2TjPdDyEHIJ4QfkXgi+Sg7EWPd/mMU726CaL1/+'
        b'bOTOh9rNBZENb+iblrzyzEsv/fT7v/n1Z9zB1iBZ808vP/3B5OYQWc4vXyZT/nWVr6354rnL7+0bEHwyYkeM89UtzjOuJWufHK1MSltz8Bd/nOfsf3PujarK1SP+bn2t'
        b'7de7T33/i4VZzupXYjOMd34TdWxlTPP8xTkvPxfZsvblfbnHlw/d8MGVd+v+M2T9BxGuT79+Pvr9C0OTNaP2NxUBnaQiB7mDm+YkGPVkuwF6jS/htqX8mPWk0TWQErSF'
        b'5BB092xCViJpyszJU8CUX+PJMXxiMHtZDstuC2kBea41UYmUS6dN52PxbrzZBfwT1eKrNsYCyXaQsfpaSDO+lKVAfcfKyB4gzIddVKTBD2Pr2yl0KNnEiPRa/EwngqmX'
        b'dyjoMI2eEEtthV2wmCgVZfRzCEWWDDkn59TSj5wLhp9wPoIL5zRcDOfQ+tFVzukJrrWbnCDZV1ucDsrdHZQqdW4J76DY7QjzkVNaTaaPnL4Q4U9OqfiCN5Kz5FE22bg+'
        b'AJfkaADZI1+FL1X2QFkZpw2grD3z2uqOvNa3VHyUNUiUn7SqvuUqWQYlmYPiQheKUtGwvMwMJdJxqKwsKzp6JUpnpVGT+sRPo1pDXZnBtMooPvogP3jNn2Sg4YSX2bRz'
        b'UxAjBbkp+PQYvNuaDNDwXlTet8h6Mn+h3LkY7j28//c/lX0CDD3H/Hpl3P6PNl49dH3RdqHwYEP/ycDdD/efDH9bDBttr2pf1Z2qTB+ybXhI05Lg7OBZCXtHNL2yGweX'
        b'N495K9WV/MuNr5f9qDK48vevIzRgbOTH7yTreRdVMPBVIPG3gzOAd/s4d81i11C4ZcIH8dYEvJ1sM2Ya4vVGEMOA26MYnXwpOU6OSGThG7GsT0W1pWK5qcJhEawuu8Mk'
        b'8Wo28aUxDNfCIQXc6uOHW7IKq+BRVdjdtS5Hfc+oRQfR0deHWrSWxT4IZwNQi6oYU2anA0ZlgCqDd+YbQbpsFiZAx5Kgo7tyODQNH1GCIHiJ3AhQAHwoxoQ5DpCsXZjj'
        b'GIJ1L6Bv8Ucw2saRnRAsVkSwn2r6okF9cimCLfkiTSHh0vOFfdCJ4tkMl673d6FiVjqiXoE+C4NqZpTlbIqqFzHsw3oZihFCaQUaTfRIsXBFXCiqrgEOWFCmmTZ8plgY'
        b'81QU+jSokL4+NXKKhKAf5AxGI8avok+ufcTFi4VP6nXorRnbKPi1i4eMEwt/MHMEylHspq/zd1dJqsS7YXokuE8C8LKZY/oMEgsf6hLRjjE3aZ38R4vGiIV/KlKiaivQ'
        b'G12ZgY83iYX780PQbEsCXR6GNbNWi4XPrx+FTuQepE/O/N8YCXp8fQJ6OeMKfZLvk7VeLFw/Jga9Zq2k0JeMLtWKhb8ZHIQmpo+ghYbY6f3FwjfNYcgVDjJzcpnmz9HV'
        b'YmFV0QD0uryW1rnkq7m8WNiYPgTJB2ygTy6ZpJCGzrQqFmlcO+kgl+96UiUWTl4bjXQrF9J2To1ThIiFk1KT0IOaR/R1XqfuJxbqI8aiEdPfpEMXcT5yqaSF9U1FMQve'
        b'oHUWaucMEAtTs1NQTAGmIz98XtAYpB/hpiS0Nm4I1UdTFixGKWTfZFaGd6G4MYBOqfoElCoMEmWczcA3jo2B5TYGHwcBewzeix8xsYScB4Xo+TEg1I4l9w0IGMx9RovI'
        b'PdBsDo8BxB+HH8xG4yIdrFiF75FtYwBzx8fI0HhKMtx0lRWSqxvGwOKYUFuBJpDduFUU3c5EkaYxIKxMVIDkNJGcwc+KIs/5lePwDTooZHMEmpSPDzORZxK+NwPfgJZP'
        b'FoLRZFc8e3Z8fApdGzPxHnwX0r34iihGXoLazlFxYxbZPxkS0NPEuveSU3gnlf9nP0GuoNlutVi8i1yd6YTezAGJ8wCaM6BKbGETuTvICd1JB/3tKkrHLfWsP6QVP1A6'
        b'oUNz+81Gc2vJfrH0AbmAnNCfjBX1KIMjL4ilzynTCe1N5iIdAu5UxgBWh4QT2pcskEsvoSx8aDwrrsfPAKQb0O7stSAIZlvnioI62a0mN6DROXhLFMohz4E+ypp9ehEV'
        b'yKHduTH4Jsqdnin2/gZunEhuQLvzqvBxlAdyxl2xP8/HYdB6oeH55OR4SDbNYG2cOw/ExhvQ8gJysw4VFEWxp+PwebKJWtjm6clxNA/05TYR6p2FkSFyOquHAJkK8fZY'
        b'Nj+xpBHvCoGmF1k1qGioXsSfgzPxuRBoefEAsgkVU0sRgxg5Z2YINLuEnE2E5CYWx+pJcsoWAs2ePyMCzcet+DgrxY/sQSHQ5gX4An4RLchdwUqj8YGRIdDkhWuHoYXk'
        b'BHkgwtsBs3AAt8DlouX4NloUPJE9HRuRj1ugzaXk/GxUWorPihL8KSfZjFugzYtjyUm0GG/BR9h6aukzAS2c76FrNOK4VkC2f3399dePodMvD4+gy9HwSnSYWPi3Wjmq'
        b'zgmnhZrvP6FE1taEz2TOt6GOhX85X7MrJY9Pi9n6uyfGbLwfvPmjT05sfGXI93aG1MmCN1gMp5/6qZCZsVCvO3R+/KhZcy9NU6n+FlOc+vKeB598/dX7D5PO6fYVfHjP'
        b'VpQbvuXEV4XRivi1H459OqrQnHDp2k+U45IOJv9h5PO/mvqj0geVRwb/9uqPFgf/9eDnx8Nufvr50/mffv3BkEtP/frB899PcH8y6NWfZL168OED/fMPVm6/rPnDbzNn'
        b'nDw2/cogIealH/3tneaGn//j68P42PrfyidWPEtuvPLTjyYMyL32mmZ+5fG/FAyRpzz9aPi9kUM3vPnJ5El/jAbRlprDFi4AvaTFkFePn6XWsF2g5Ifgizy5Qh7VMF1e'
        b'Nh4/C5ICacF7fdICvjDTRQVHfHsWOQGiP6jBuYlZi8oMmQoUQe7KAH/ukXtMdiU7SRtU1kJ2ZOOGiZn4MgjQE/n+YflM3hgTM8CJL2fkQf3NZDdphUnfJUN9yG4ZvpqK'
        b'7+gVXQoasq6kAj/xQyuJH+4KExV2mexB7cxI0HBynkoeaj6Soz8RvBxkhAE0LwtnUgn9VXKOSJ9cIgO5xF3RkzjCOaJ8kkgk4+5eSeR4gM2AigAwFEfrfLIIfmZcvjEX'
        b'ZBLRBKsnGxV4b5S+BymEGiGRnxTC9SiF9ELMVYlSyK8maRAoK9U7Css0faLTJSnka0swgh7NODaozJYyRYvYwlSqSOuYGWSvV3gFJcU6L/ZVzjmLLtWUs38q+2F5deVH'
        b'widlH5UtE6XYPRnmYOXfCg8WxZQeGpFm2BZZGZ599OT+kw3XLszYxp3bOXLguW1jQtGDDaFZ5fv1nCilHptQSyXUenzQi3ZLyS2vBNrD7A8QZ9/pcrgrXG4QQU0OS6XF'
        b'AYqPiAkaOhgbEK8G7YbJoNF+cy13wsM9T3Y/32TTFzf7JntjwGSn0NHGF+b55jrJqI/PNeoTs3Jxc5J+RVZudmIWKDqgLuKn8fZgsolcyO1x4gPFz28x8fQf32nilXki'
        b'h3l+xdwQUFhp76hifmgZ3srm/sW+41A1+mxi0Iyy1A2aqSjd+vTyO7xzAty6/cboP5W9zib5U/ibY7ZVfhA72Bw3/6OyT9D1woOgrxSL+sqM/5YpfzIWff128G6ZGtQP'
        b'OnZzx5fhk+SCv/aBD5GbTJde6jYkgJ57qZP2saZImqHu5z2mg9IROOvB4qwHqTmqfzhi/Oe84hvnvL9vzumLzbTCcDbn6N8Bs06VUXytZnX7Ct+D94sah6hvJPnNez0+'
        b'H0SaBuKbPSq2sg4mw54V28pvNiIrxRW/Uq9FgwxblSCn2kLqJ4jS5/g5cqSecYADHmhTVuvFwrFDZEgePkJGFYzQ9aORdfageQpnDtwJ+qvzYt1HZZ+WvVZODdAflZ0z'
        b'v1aZlMr/rf+R/oUxN/pvtJ2JHBW0LW+U7sea91WoxJ18NnncqqFjto9xpUambpX9+yXN0f5ox5fhb3z4A0k5nYFfzMIXc/qRa7kGHsmzOXw9luxz0V2raAKyHfAqsjMp'
        b'T5afS1rzMvElOepXKB8f6eytahpaa1ntMglui0kwu0TUiBBRI4zngoElUBMID0zAMcCHInKPnD7sCbJZzAK8V/8Nhg+KyY5BPpShFe3yQ5kvAvRTunfYty++QFqy8WWQ'
        b'dc/G4eZ8fS5uzc+k7HQkua4oHYUbKmTSpCr8cWS8iCNytj2laFRWKiU8kTHTshzwRMbwRM7wRLZe3hWBoFUqO+GJQsST38wZg84lMS0l9dWsNSJK/DNWgWz6aKaIRozK'
        b'R9bM4wq50wR3+uueGbxDr/1eska+bsSJpNdW/a3xZ/jcCcu8E605tx9diRpb+ufq74UpJvWfdlR489PsGQ2zjCtWbD089vHY0HHr/vTpq+dmbV78+OKJD36x+4PaM0En'
        b'yjc8rUianzf5L0P/GRMztPYMSC1sj3SHHJ9ldjMV4slJPT7FlRQUi3sPG0GVP0v3TxXkmRRx/9SFzzIMIkfxNtKQTRdjC2nN55C6HMT0HTxIi/fEPQ09vh0M95qSEvnQ'
        b'aUiey+FHJotoA9xPbk0hLbn4ElBTch2W9hZu7lPkTE8yirLbWx3RUlNl6YCVMSJW9gd8BCFFC1gZzGl4nlfz0bxjsA83FRQ3ASEpunmUFW6XvdKflnW5HABnqfDlGBKI'
        b'p7TSQ354+nG0P57qoCxpGt6ZnZ/oh6BT8EEFGopPyckRsqOga/41FkmCC909RZWKXvKwAFJGzRtRnVB0qIiiO/J+iNpSrnGgxltlAyXDxBujdGjG6mfloEgvKRuaLRZa'
        b'h6lReHEMNdwZfpeYJxb+KzYERQ6yUCtAzhH7cLHQUtUXjciZBR0qmzon3yoW5hkGo4m6JzlUUDa1FKgiK5z2FDDK6nkqqttfsi0WCy8sUyJNxjtKauwIcpaIhWcNelSA'
        b'EpQAnf93foFYODH3CbRW97YK6HDEczrp9TtoKlptG6ECQKn7FkwSC9eUTUYu2894aGfh7tWzxcLb+v4oWT5BTi0gN1YMFQsvVhrQQtspJbw+/N2KWLFwqbkP0tX9g1oW'
        b'bKGlT4qF+XNnoI22fioodCytiRALs2YpkHrqFdojzYcZ0WLhy4NCUYytSg51Go4MlIuFdesHorE5MbRJSxbJJSZyIWU8slVX0r5HTBqUIBZW8vPQidUxFHr84iK31PfZ'
        b'FvSa6zUKSFk1NkssLFtVhV43PFLA66Neii0TC7NHRCODLZvWOehsXwlQrSwMDRr0NkdZ2HljuFj4Vfka9GVxjgKatHJbVoVYeLcoFQmCjnpsRPzPRItYOGtBLJrtSofV'
        b'VjY8bWERspYO/oR3xsGU99v9r5Knc/NIcvjW71/74q97zmz55cFXxxkmqu98dKpfzKa3MjKEV8of/O3VT9dE5uGUiaqKvelX+294w17537Ythrik6cUFaTmv2DarP0Fz'
        b'1cFbFaqDJ0fEoD+ozxnqfrzXeDArRHn0e59sCPvd5/Mv/fP3I34xQqV7KY+UPo1/wS84tmzg/cz3X/3bf9XG7w8sjC34yZKy759/668X2z7fVjt01YFfzUt77oVPtpe8'
        b'8r/j3r577K3/Di5fE7WPS3ryiws/bz09+cLL0/6xtLDviPlL6zaPWvHXSVV/W/XTfFfLH7JIqrPffyL+vGDALxc1OA599PnVnF+9/eOUxUsa3tk6fsPS+6bm3xw4tvzA'
        b'TtVPrvxuaOYzL31x4PgHc143nX7+/LEXm+680bfgqejTD8OfTg37fMfXXza/EfvWG098NcZ6ake5XsbI6vSF+IjIl71ceTXeJDLmDbGMeC5/kjRlG+IyQPABoosvkvsV'
        b'fD25n8dobiR+oYK8OCkB3o/nkNzNkebIHH3oN9DOb056oMz+tmpKecvNtctN1XabldJSRn6LRfI7SS0DAgy/I5hoEM7p2J5IOBMTIniNnO6V8GzHBH5kHf6yK61MA89H'
        b'cMFAutWcQ+cj3SB51lvMDj9q3QMr4RzDfISaVnHFj1C/FelPqA10Rqxki0ioqdtNC95JHRxK1kPanAPTY1CiaeSaktzF5/CRAD1BIf11VlIaSF3JUCkvhDDrNw/qBy/I'
        b'tgSVyixyQS4otqAGrlQB10rpWgnXKulaBddq6VptkVMGUMkLQULwFjWUBDWCsFsazCQRjUeVJggOi9OZV6GU4Kv9GchkykBEtxufG06lWmIjyiY1sBEVsBElYyMqxkaU'
        b'61VdWeJlqCuJWJHHLEv9MuOKgJzjNjQMDSN7yU3R2SJ2zisKpxOuzodMHbw9RcunaOR//vHI90qzlsUPeSnko9Uo9+XM83mbfnb+3U9vfP7T15fNvXGf+0Hk/hXjP752'
        b'Jf71Z0JS/pJ7P/Wvv1SWPxr34L3Jf/8oZ8qSr2oG70pu/vvq323FH3x06Acvp7z0ymfxs6+mqvINL739WZv7P9ykO4OnrxurD2ZGFDe+R27A+qkkD3xLiK+vwUfZ4ppH'
        b'bmfAHG+yBPhw5IaL4tBJsiVd3LqcpWebl/wYNb7MqrUqcTN1vMKHIjLFasl9Hje741m1S6rInQRjYkYiOY/PUEXtNJ+Mz5BNzGxknRWKW/Ausiub7NmQiHfhXSoUEs2T'
        b'xgFkD9Pk4ovH4JZ8spMc6JNEWhP0+IIchQXJXHJykcFW4mtx7AEDPo9PE7irVPP9N5A7jKLgBhePW5JADjNmLk4WrSMR5DkZ2VRKWphvCm6NAACgVIeSW1m5idSJq4Un'
        b'dyLI/c4SubrXZKOdLKhMplrLKpOpfZN0A8jTbHNUzUWDPEavIjil9LMmTEJho/SeuMTVHlmFzcl2qkDNtLrqPeo6O91GFywepdPlsFhcHo27tt1W0ZNioXRQC5KDut+J'
        b'e1+jaEIdKR1xPtpA1Yn/+tGGbQP8aEOnVvoENk76LaKv0sW3Fi0TVw+Xp+c8apO0LQfXcqfFVtnuMyAOl3qqzVxTLpinh0ItdLGgNeFeWN5b3wisUgSmMNGRAooX74Ph'
        b'A+SgbmNaL4xvrLFKrDHI5B31HmoN63Wt0qCoTOIM9lBneKc6AyRjIxItO0AYeycTb/lmu44sz/rEM2Gcky6y9z+f9qeyj5ipRlP5exvXpwpFavnfq+P0HFvieIcp07sI'
        b'6QKcOo/vT54jVyVnkK4VaKvTz7bW7oO1AX6i10R5Jz3gKa/thg1TO4bzAfwt3jdySZBEcF7NfCP8fKb1x+KugQAZp//0IYCtJur+ZTJ5gk0m0UMZrjUm0wq32SbeYesE'
        b'FqPDXmdxuOrF9TQycFElse5SdzGz01lhsdm8q7qzgQgwTHwMHmFdGA7JP5FkGlQrEBcRruHYD8+cfCucOSH4gTMnU5+VaFSi4GVAOsMTA6Y2RPrr3MH5sWKuVNYmawtr'
        b'C4ff0LYwK1/Jw5X0I/CtSsFAWbWfd2o4sErKrIOA7cotCmDWqi0IWHNQKw8MWyEEs3wIy6sgr2H5UJZXQ17L8mEsHwT5cJbvw/LBkI9g+b4sHwL5SJaPYnkN5KNZvh/L'
        b'h0LLggHbY4T+W9SlWtoTgYoFA1o51mYNiBgDhUFMRAiDdwfTdy1hwhB4W1YaznoeJgxt5YVEyeAhE3TCMNa3PvD8cAYrlsGKgPwIlh/J8n3Ft9tUbepKWZtcGNUqE4xM'
        b'oBB9zOloaRvDKoOEOEHPaoyEGuJZDQmshihBxtZgEggsFYwgPh4drPP7J5WKju8Bd/RKj9wKUqZHTvGvK3TLq1BJE04XiNa7rtMpiRAlnyA6eNKkel2RtZVaiXSomByk'
        b'BtKhYqRDzUiHar0aSIeMkUL5e/+G5RrQLPovs9bqsppt1jXUU7/aojNLnbACWzLXVlBX/46vTK4zO8w1Otqhybo5VnjLwV7NnJmWp7M7dGZdaqLLXWezQCXsRqXdUaOz'
        b'V3aqiP6ziO/H0ZcNupmZs/S0iri0WbPyS/KKTXkluTPnFMKNtLxs06z82XP0xi6rKQYwNrPLBVWtstpsunKLrsJeuxJWt0WgJxBoMyrsDqAbdfZawVpb1WUtrAdmt8te'
        b'Y3ZZK8w2W71Rl1YrFludOmZihvqgP7qVMGYCMKrOzZGGh870ZNYueuU9T+EdXtA2BIuj25clfiu+L2VgjIryE8ekjB+vS8spyEjTpeo71Npln0RIujh7HT2aYbZ1MYBe'
        b'oNAdCSJcdd3i3tTj5bZiXd7cd69P5LNibeL1d6grwCze2dypyWOm2IplIEW3kFaDkZ57yF4AeivZkavPFa1c+EEpfoYZD5rH70SDOBRzYmCl9sT0YchNN0bwdXI0l9kI'
        b'C0gTFamTSDNc5ReJtZRk4MuzEzPycnMzczmEt5NTQeT2OtzEKizawBz1w3WzLTnnC+KQm/JDzZMFCmbo3JEAFYDyNi8DtGRJniZ79Pg8KkpTkQNPJLE6XlrNsz2EN3Pq'
        b'c37Sb6xo5rhObfoI6d5MrbOVr8hGbsrXyCYOlEKol5xa5a2aNNFDGtDWpMIMsj1HieaS55TkGm4jW5m3wKQJayZEOVdQL+Nd0Hp8a5C17s4NmfN1uFc8YfzIXdm1fEr4'
        b'7HdWvrErH+kHOvidLw3+VfoPX51ZvbvSvPBw6MPzL6Tl7XbWjf3hTz5ctP5J4wt9kg8eUWnuvHF/dtVfPn4zqt//lvx8k7H4jz9/+rc//9O407Hrita2NZ7YWt761ac/'
        b'Pqtp/fPS9Ko9f6lOf+OpOwc2LF//i/ON67/4YMrghh9cytGPda75j8VuWnPj9COD5avdH7f8YNTf8j9+xbb412k/3qc1bHhsGLFK1++zD1Kjb1xYsmB9ca3uqKou3zGv'
        b'8NcvpFY9Z1nc937c6P5G+8llc99tUuoj2N40aayBoW/QhsDw6HPdifFkexKPonCjXE0e4tNMT+HJJryPbp/77Z2TRxN5cuVJvJc5eJLdw2OzybYgY1auIRO3kl10jGVo'
        b'AL4pr8W3yC3RnH1+fr7ffti6jEQY3lPs/TXk7DzcXObbUPJWEEW2yMjdOcOZNqbHx8w1EQmdffbOkMMuun24cg6+jJ+FbAtg9a4EQo/YSNuS2dCxneK++1x8TUV1Orxf'
        b'VLEeKXGraEVg6BAyj+xczJOdqaFMwyOba/EZ3OJtkIIc5sjtCeTeBrKXvZ6I2zJAuMQHSRN7XUaOAM7hQ+Qhux2NN1H3DqpB0hNQCnKPz8O7uWn4quhacGZSKRNNJWwn'
        b'N8kWUYPEN8h9F1V4xuvwMaokturZgShxeLPJQfKI1ZiAbyjIVnJuiuhDe53sw1ehxjJ8jOzM4aA5z3B4tyxZPOlwE79A/UfyyXP4pDGXNvY2h4+QvTPFfYODMFRbaWNz'
        b'gSZkAqQt+IQCaatkkxcoWPWr8JU18Looz60n25VIO0uW3hfvYvNDNi0R6NsGGO+8xAx8Ee+TIy0+J5s9WO/duNL+P9u7OkrqIAZbgbdLOmy6V0hPUTMHTA0vujvIOS2v'
        b'4aJ5atDSSO6/4fCr7PDDU/kbfjQ8aHYi1TV6AeSJcnGQKMPTgymOScirpXaQqtvF/16r5XqVWEnfwNpZnfG+ipncPQWSoQGqw/+M8lcdOjX9G5W9aq9SSqWdHlS9hX6K'
        b'rwTDq/g+HlnsE44o2wJBwsu34hwWs5Bor7XV640ARSbYK3qrJstN5daKHhq02NugxyMoeBCseoTe+4Gg0kwPcJf64Cb0LPt8O/CiKu+g7rw9ADf7gBv9BafvCj9Ygr+M'
        b'86r9PCwrs6h+MqTsoS1C4ED0JFJ9u4awmeAds72LoIc2VPnakNQbUey7DIjYjtE9t2OZrx2J3yzEfRu0EBcDa0MP4Gt84JOLmV4CkP3NbjppSnU2doy5yxZ8d8uNqDXK'
        b'H5/qJJPOovqEU2ftsC6dFksNOzYNSgxTMzq9SI9SS7pVEegy0KM5boddV2Cur7HUupy6NOhBZxE4DroJnYUXV443phqT9d0LyfSfAnW2lBfrOfGU8kN8l9xLoNzsyiw5'
        b'ks/g8IWBUdbwHQ/lzHMlq24x9RHKML/2YVzhR2WvlVNPIb78w8hXI88s/VD76upPP1Hqdg07uGnMYPTymaCxrni9nIkVpqRwH6vEL4ykB0AYp0zGl0SB6mQyvhBb3Y1A'
        b'5BjBBCpjGBKPHC+2eA8ck+dzXbQzVaSNbMmmEkmcgPilXBJv6sncpaI2Ju9hGcmJaANaGcxFU2uqROilZ/K+pZ2LHkStC2BWe7SB1trA+uFlyvh6cBeiZgHUyPXKXUjG'
        b'KIn8cWMnJCiyuERTgNvmsoIiLBFxt1PSfFmUAJfDXOs0+532L6/vVBGtYzIzhkwuy4VnoCr4Y66yOMp60M/ov852Tckd5d0pVO+KmapNLtO+wg9FbuoCs57HV5nahW8P'
        b'6lbz6qB3JQdbf/lqgYIdow363uA/lWUBqhoKPy7bd5n6LX4qfFIm/6l+x68Nc+JHavQzVvYtON0w6XjKVkDZGyBcBofc0o/T8+JuxYFgfMGrJpDL8/00Ba3TRSn0jLnk'
        b'FBNVZw4JFFb9BNVnwyVvo2/asHRaXCbvzDBmzHAz3IubGxDnleXW9PdiUKd38rzAGDpOCkTYLnya2BPtqEu9v9YEoG6Tv1dTD4B7a7PXBr7WA3HfFshbeou0Ru85IroH'
        b'3bV7FfNcYV4r1E7o81zpyblKWlXvgYbR2dTmW1h2h7XKWmt2QbusQndssNaySiLVKcaULgwa3VtxBNFUwrrs9YcEQEZdoWWF2+qQRkSAqwqXTrCUW13OLi1HdFlDC5z2'
        b'Gq8oZQXuaLY57awCsWpxUCstDmf3diV3hdiiWTMzge9aV7hpfSCGxFEeq3N4WwWwMl1mynV7pg6dt3DVeewoKj44EW/NzqN73iysQF7ivAyf92UhacqZlyEr1OPzmbql'
        b'5Q7HeuvSIHUmmlkVVoN34/3MZ9ewFJ/zs7fMxqf8a2BqZAnwp33cCnJLvQBfTGM+0dnmxeSGhouooYfmET5eQ/a5Z0B5SX2qU+uen0F3MEtIk2E+6MK7SAs+X5xhoAB2'
        b'ZOaQ7RzePmUUOa1fjfePIGeKeXro+o6mgLxAHrIoCUVAHJ72twHVad2jyEOp1oIFifNVqGCDEp/OjbD+J+qR3LkcXhrx2fTEHfdDNyaHz/pr3/UhQpuGl725ZNPmNv7g'
        b'xrGVy/M2vXr9v19qUjxnY4cJk99/5dV99m3C+S/V6vdnXzz6cfCo3Rmty29sv3F2kPGfZ/a98ev6fy10Rv12bdKLq9783Rd33BvX7EwPyX0npN+bQ48sbdMHMcY9iZwl'
        b'+4EKkx34VBnzv0MhtTw5gvcOcdHtkHHL14fE07MClP4xcwpw4sNAKIfiG3LyPD4kE/ekWshxp2QMwac0on9wM94jKtIX8Q18G3h/Ej4W6t1W1oTLoibgZ5nZAMBdxvsC'
        b'TDYl0yWjzZl1DMB0chU/K0oHIBsEzRTDkewdx0h5PtmLGwIMKVq8X7SlPFjIXk+dFMzsEsyE0EyeZWYEfEd0Wo9LoVYA0YBwZKpoQ3gYJHnq9cobhdLLdurgPTk5vJ24'
        b'91WDEi4SeI1E5sWcsgPVDaglz9sGRkR9ZK8nmi/ze6yd8BdA0kwJbqSX8G9E/47slvQHNKK3pF9uAhLWA8E/6SP4KUyxaqdwPWkU307NldPjIz204bSvDVO6JGyzSmZ1'
        b'NM530RrqA1TjsFR6lE5rVa1F8AQBSXY7HCDDp1fIpZZSW7XGS/FmiiypPTASagyRvGI0lRqJQcmbFMCgFMCg5IxBKRiDkq9X+DGoQz0yKDEQlCiyMVrvr590vyNE+yJS'
        b'eu+7Pi/87o37rOfiW+wVGDVaZqaamVE3y1xL1SCzdK98GfCsLpkV3XcC/lGUP3F8cgrbcaK7QQLVNUFD6ha8b8An69Jt5irdqmqLtJ8FHaZ9bn/C26nuwNfaXV2AcVig'
        b'I7XOybq0jrJwmdSdb+B2ndWw4Dw3xQP8Ar6GWwLZHWmSTJQlGVBUKPKumhkGLjUC78V7yY1sciMLjSSnteRw1VA3da3C12pCs42J8VlAUP3f99WbkVUSJwU3APnZhQ+S'
        b'5wZryLnROiaR8yUZaDdCycklv5TZ4oyiRE4OkCuo406IZZ4okSdm5Rb5C+QtRUHkET5LNrmn0/rIc+QSaWEPMWt1JmWUCZR17sAv4s1+OyEZhqwcY2ZivBJA6TUryBZ8'
        b'n+1uDByXFbBnQrtDmuZPzi+KA8INcrdBn5iloLb1INw6Va+XsbOzJXOh1RSuDOG7S+XTOXwxaroYcuqyW58gvknbe2C6mhzinxpSxwJK4TbcQBoSsnKlIeSQfkDf0UD/'
        b'K/EWa3H9KblzGzzVdPOzwT+5H8qnaeQFTz26k35qe8Lm4a+9NmzRk7/P3u2OKuN/TqJaVu0NOj722Wuv6n4pmxK//s0BqkVzHW1vj8v58fzIp97d++7Ot35+s3zFR0P+'
        b'8Jf9Z0fG3q/efbYk9pWhuUFGe+xPgo3Ca3NeuvPibxNuqF5MXxJl+/jvOz55YumPnpSv/nzj7f/lbP+Iz7gbAayaHfq5PRRfzWY8LHEdX86lDMZnXNSaBUrJdbK/A5sG'
        b'Fk1ukxdENk2ulDCLeRGISbcZt/ex+lg3OeIke5g9fOQKciI7MzcehCZ4u43sVeMWHm+aECwqTIfN5EXGpAevDtxZeYJcZIy0pJBcEyvGO/Bx5sRfQe4wBjyU3AT+vRPf'
        b'otsY7ASI0sYPNzsY/1fG48PMFTVfjKlh4NBifLZvkgxkqv1PifsW+1bGCeP8jPmiIR/fxU+LTFLzf2R/D6EMUCIZjIsb2rn4WMrDtRL/1jDnfvFXw46f8KKhva8/K5Vq'
        b'kji5UuRMJTSZT5MFgew86Nu5ysrFmhb4mP18H7dbBMnZDhz/neH+HL+rZvbes0x6oQde+5qP1w6jTAJIKGMZPh4TYESXMycgHn65dH20g+5+Oahg76AGEurWJ9grTCa2'
        b'UeCgR+rZhoJHVm6t6HbPwqPyWnypxYbpvp7QAO2UiUV+8tIi9pbUPnHC+vwf7e90h24OSnb705FaChdquZyPBIRC3JBxPBMYe53y2uAhITwVKvlgLjLa/04EpxtKr9xs'
        b'HZ0gBwYklzlz8sRNOg4Fr+GBYO8lWwPYV7D01/lVBz8moaRULshLFVZUqhQUpSr4VQvK0iBhfmmwEFoa0qZoU7eFt3GVsrZwQdvKCwtA0AlpDK+UCWFCOPPQ0VhChT5C'
        b'BPM/imzlS7WQj2L5aJYPg3w/lo9h+fA2raWPGCsGBCjqSBPW2KdSLfQXBlCfI6gxok0LcMOFga3M5Zk91wc0/0HCYOmJvlDnEGEoc2yOhGeoPxP1QVKXRkHbOGG4EAvX'
        b'0cIIYeQWVNpPGCWMhr8xzKsIlfaX3ogXEuCpAYJBSITSgYJRSIK/g4RkIQX+Dm5UQk2pwhh4Zkgjguuxwji4HiqMFybAfR0rmyhMgjLQ34QpUDZcqnmqMA1KY4XpwhNQ'
        b'OkIqnSGkQelIKTdTmAW5UVJutjAHcqOlXLowF3JxDEKGkAnXenadJWTDdTy7zhFy4TqhMQiu84R8uDY0quG6QJgH14nCQsliIhOKhOItQaVGQcHEzkUeZVoNc5y6ECDz'
        b'0GUt3hB9p8RQoSDO0aBvVQ4zleNEIayi3ufW08F5JtATywEV1Fhc1god9fAzi2bKClGWhAIqHkKdognEVq+z14oCX1cCmUdpWmm2uS2eIJO3DR7ZnJLCvMdTq12uuslJ'
        b'SatWrTJaKsqNFrfDXmeGP0lOl9nlTKL5ytUgArdfJQpmq63euLrG5pHNyinwyDJK0j2yzNmFHllWwSKPLLtwgUdWMndhup73KESwai9Un5GK/vV5sKynNJV3BlO6uo5v'
        b'4tbyDZzALZc5dWv5ZVwDqA4Og4sX+LV8NKJhX5v4tYDG6zhBtpZbrnQsWctR90B4j1smo8FihaD+8FwMikQT0DquVg33VfSqCdH31iKTHOoFjQKulIKaaW3B75m60iY6'
        b'epZJM9zuWNbxhe5kdDYOooZgFutgJT3Ym8QBm8x8t4ryE8empkzwRyABFIvMSiqw65x1lgprpdUiGLoU660uqgQAY/P6kDHIXs1ORFbQMxzWcnc3isFkentymWCpNAPP'
        b'8KFQGWga1opqWrtVHCdAQwkOIFfnvn1MZ/1xlLWW7Qi192b0SOdoD2f0cMkfUynjY8psH8uMycl5H38N//QqT3hH2HRXw2yrqzZ7gufT7sxxOOwOj8JZZ7O6HJR4exTu'
        b'OlglDhrKwLufUUOTWtTjIWzGVn/rExaC5cAsoiUbhY6nEs6aMBELer8BL+3w0Wb1ICP83bf97gXg231P7Ig3bPbq6yy6MpiVCuDiNuNs8W9ZmRFgUC2kl3YCcYS6b9a/'
        b'fKLLQOYD0DUudg0sHHn3WhvQMj7EZyCRsanwqM1OE3Oy9Kgtq+vstaCg9tCQ//gaUsF25d015aDkwkBII6Crs5kr6Nan2aWzWcxOly5Vb9SVOC0Mz8vdVpsr0VoLI+aA'
        b'cRTKyiiamoVlbniQPhBYSzebpuwcD8dCGfiCO/vO8XDMqN79Bir1X/1LV1SmpI4KWSKFsayuqDbXVll0DlZUbqbWf7u4TwpPmXV1DvtKK90DLa+nhZ0qo7uodRZgE7Ng'
        b'OB3QoZnm2uXMDu502UEEZPSgtldrX1r33iaZWJPK6Ji62VoXKQslQT77N4wp9TntYh+Nhtq2uKrt7SzLoHNagYhK1dDX6Da2v+dqd32UKppMg3VPLpO4aRcbcj2aMsrt'
        b'dhpFVVfpbzNxs6kQOkxDl1RxlcUBi3IlMENzOd2P78Z64pMk6crrHL1Em8eOu4WMejIhEbR8qrNmLzDhHdS6QHZmQC6/JC7LkJmoRDURavKInMpnJnVyDb8QBirgVXJr'
        b'XlxWIg1xuyshj+wfim+RU4WJ5AyPxs5VVOE9+CKTdcfiZ8g9pzE3C9TIQ9GrlBEoDB+QGclx3MoaYAQV95DX5JCZS40OcXmJ8dmJhd7asxVICFfj+xMMLAI33oKfx1uc'
        b'cVL8bwW+Q67jXRy5ineTh27mAHepYFER6ONtJaRVgfeQfSW5HFLnc6D93sMH0sVN+Htrh9JWKZAMH+RI21q8EV+tdVPvxbnUEdGZYUwcgC9Ss0Q2viJHfaDR+BLehPeL'
        b'r5/GZ2OddHygBWWj1nHkMmkoKLb+JqVR7vwJPHBsjmtw67TCmWnhW576xwFVfPr8hyGrg19rygjdYdijvzxg+Jsby8av2DOt+Y+fy49uXXTq48N/+epeFbe3z8l+J4eM'
        b'iMkcO/ZLQ3MD3vzUBwcGRO6ZdG/4c3/9Tf57wpfZ07JK3p/a0KJYtHrKl/F7TzaSnx26GP3C7S+37k96amT977f+VDv0yEvvWdMTBl/Z/8XC8wP+MK/l6V9UTP0676PP'
        b'L4z8+zP7Q8f+6Od16tHrGpVVz0/74om3zNP2HPjl8Qdf2+4mPbh5as4X144/33D1ldeOXvltrv3gdPvd89Oej39b34fZDxbmOlk4ItKiQvJEzoyP4svkBL4q+jyeDR6d'
        b'kEi2k+YkcjE+g7TKkCZdpqzEO8TNicN2cg63JMETHJIncSayEd8YQ06wc6y4pRSfSMjKzYFbw7jYhfjYJHKO+RyM61dOjSG5KqScVyjn1fhACbOSTCKH8dls1hp4px9H'
        b'bpDd+NQc0uCih7zIRrJ3WbstJoNc95pKJFPMI3yYWTSeAFy6nWDUx8fNqZQQKoxcl9XXka3MmDJmKD4gGjrkco60QpufMZN97Hggfpa04rsJ0lvyPG78eHx1mpV5WuC9'
        b'+A4+Sw0lmQYjbk4q0tI1BrXodHJyO83NGomvpJZmt6823LoBX0kSV1w8eaAgm/FRJ2sk3h/qEruauS6d2uU4FCLw5Eg+OczGyDga38rOT+QQv3I8PsqlFZIX2JCn4bOD'
        b'snGLye/0MF9PLk90UW9tfMu+Njs3OzvXSJoN2dDgF71xM+LxTgV+nlxKYN3sR14cQlry8GWDEslnc2QTrOyHoX2/hQvidzlDGCXSQ1MgC2CmICpiSKagDUgbzEKtUvGI'
        b'emZGMu9LetYwnBmEtKxUK5VGcOIG0JpBkpzTJRCfKwo7LfhdfC458VUmQDRA8nUHE1BDwMHCHhsDdVG5sWu/FRbChIW1ApGA8wthwrPvNXTvu7IFBIJfdCUQzBI5mnSa'
        b'RZT7qLQCDIYyKZ/oJckFVEhwSgJ9Z/4jWf47CBYdxIiuxYbO3Ky4s4hipmwwgGt7maidcne67VFP5Y/OLTNXVItb5jWWGrujnu3SVLodIiN2sm90fDNH76gvBQqpfp6C'
        b'LrOjCpQT75M97nPU+jY6RKzw7nN4JScq71ic/jp9D4xfhrre72d7D4c5DbqUPo4GGrUlm6WIGtO5QSiuoo4WLvnnOinIx5XM2+uzuc8ABWesOBj+lI4xQNxEbuBGZ2go'
        b'j/DWGo7sROSyarKbRvslZ9aVZ3eQIrxbKokSQy2me+8LgLvTPRJxP794CN3RB/qzZkj4ZNxGtlhXuVQy5xmocU7K27mtKVqcHC7/50+0w8InR/b5/NLajXirZdW2n1nv'
        b'fvjRai7sPe5ByDunThx58sfL9snkYfPnD4xzHH7LGPd6wlvy2IX6ipf/Xjj5iN61uemDkBr5zvXvTtk5vv7PeP4naya+dOgXv7rat+DP/1j+n7rxh7+80NbnP18+aL1y'
        b'0br5zWOpf/zkZzvGbH/jx1/FTfjnb5Z8Nab+1WurD5GT0+OCDkQ5FgUnxfy339wV4/8evfvLe3qtyOiuAkt8WtyGD8bbxTBdU8gN0Vv+YshYccNoY50kWYTNl9nI5nBG'
        b'lEPIrqAAliDyg3q8UWIJa0YwfjkW3ymWYvjUked5GsPH2p+5CqxbiA/7kXWRpOODNRJVV0E7aAXODUbG1nTkovSdlNvksuiwfwhvI8cSaDiKRYPEMFEh+DpPLuJTWOSJ'
        b'peNGSHF+8C18XYz0M8Yh9v0ouT9dYolQ43OULeKroWNY08hZsge4jMgU4/Bm4Iv+XHE6aXZRgRCkuYZSJpNmQvPbB0PAD2A8aPyg7ZwpSY1PF+OdrD3JCnI2gbktKFLJ'
        b'XaRcxg8hRzm2pxGBT5FnvC4NK1b57Zbg4/gM84soqZ+VYMgF8RMadleKIR6G98oc/ciurg6S95aDqSTtgPGsVH+eNV7kVkrGjbSg5It8iQa90LKNDdFBQcut0UqsQaoq'
        b'0PGsNpA99RAAgxefbfdE2ApJHDTMGd3OlDYij3/Qoo6wA/RsWivTs6kvL9Wz4ZcaxAYInIuHa1kDFw0PCHxAzvuljsf8SOtj+UhjaiV0hbbMozHV2k2SHuz0yMzlTqan'
        b'd62Te8JNvh1q0bqYxXtPUvMwbPyafl47SYfnAoyAvq1huifRxGL7N/CO9LUc6w1aLnPMoL1yxEMJ7QWihr/aaJdM4NayPH2yUiYaBuFaTr8PwHrI5z0e7eOUNVYnNKGi'
        b'mvGYkUDiqc2JacX0AmaNDUBfa02dzVphdZnE4XZa7bVsljxBxfV1opFJHBLRouRRMIbsUYsWWrujGxdcranOYQFGZTGx5+fxXm9HGhGLYh8vZ5EY1kR5hyzg+U6TzgaM'
        b'Io1AbZpsUOggVfLRol0Huh4h1hRHu2cQOwmNa7eAiXPa6SsJ9MgNgHaYTEt46RsJyN/iJd7rGgsjWIO8eCg1hs2DimIZDHsXLeiIVSoTPRBvYkd+vOC1PvDslk8K4/2h'
        b'x3jXACdwDfw6NiBrueXiRh20gZsK0OmHkMQJ5EXoO7togtJksrlMpnJeYtcI5mhNqK8N9N63agLnbQI/ddq3aYPFZKrsrg2WLtrgc+v3LaPh3gWynLfrxNYAgeCLpFbS'
        b'K9Eg5z8vfq3qBp2hcZYVJtMyXrInimgc0EB6P6CBvHeQNGyQKHCN1x7o9V7vaTRqocd1fjjRDqq2q7HoaT7kPpSY/i2mowqm3dnNdFR9W5RQ+FBi+rdBCVBHTKu6a4Ol'
        b'w7r0OaDTEfeSiXZrtB9l75IKUPOYyfRUl1RAvOfrcYCAO6LLHvejGzuIUWy+gfcSKS4BCKmv817TfPsI1HTZOCARZkEwmdb7+A2MRLA/mWC3e0K/ZWwnqH0wTn7D2FOq'
        b'yCpt6JoqBgLsxXjEdD0eid9xPJzucpNpW7fjwW53PR5a1ryQ9hHZ0vsRYdW2dD0igSADRoR6JfhIlNaFGDmCfGTnMaF7BR5tnt2VCYzZQg8GWYSexqabEzAmU40bEHan'
        b'P8GSBw4Re6BXKCNtm5ztxQCxStu6HqBAgAEDNNV/gHSdkWegb8gGdhgywcdyuaReoFLXwxViMrkcbotgXWkyHeC9h4YYjQ/mYdAifJ3wPfbd+jHA148B3faDT/ruHdEA'
        b'A7XZ7Q7WxGe66ElfX0/an/tuXYn2dSW6q66Iq3vkd+6JikUBMpnOdtEJPxy2+1MhOfLbbyhAncUCsf0u2gO6oQ5tbb9ewq/j18mkfsgaaI9k4lWl//R4lDBmABY0CNax'
        b'5wN7J2/vnUexqtpus1D34BqztVawdCcrB5tMYp0m0/O8tPokAYOnp7rX9PH11/tc1/IxFUdFthfCpqahS2mnOw7IoqdVmUx3u5RD2a1vAhv83cDW2Z0m0/0uwbJbXYON'
        b'ZGBdIkjOR0K3iNutzYHz0gN0UPpMphe7hM5u9UrEqOqFiKGi2+cgN73UJSx2q1ewqnsBK4gtcDNU+bIftHD/1U9vOlyog43Xt37o+qcrZjlyhLtAo2ZuKJwgE+SUb/Wj'
        b'WildKVRHpScWxbUjrRg2IIq8j2mlj4ez3WdrbZWuzr5K3L9OSRbdONx1dXYa6+cxn2z0cCmwetZ4p82jXuE217qsayz+C8ujgpqqrC7Q1S2r67yKabemEBgFBtxk+n47'
        b'GVGzmKBa/9GQHgJ8pSZM0T9A6aii19U0sdJkGU3oMR2HjQ05nQM6fPqkDg6LjiUSbKfN7qLRxVbTvDbQvg75ykpLhcu6UowfDaTbZna6TKIl2SM3uR02RxOtbQdN2l0f'
        b'fTjtUfsMFyHMdCvuETPDP1PhHdtpwqjUHprQD/Y59tPkIE1o2GjHYZocpclxmjxDEyoIOU7R5DRNnqMJ5f2OczS5QJNLNKHhTB3XaUI/sOO4SZNbNLlNkzs0eeSdD33E'
        b'/z+ulB1cWcyQvE43PWgoVLVKzsl5Oef3A/Q0MqqT96SM53Rx8DtMo9KGaGRqmVqulmuV4l+NTKNQs19aolWznyAolX7YB4wjyeF5TrKDtFKnSvxgAIfUMbwbb5wW4FXp'
        b'PRzi/FUHr0pviNRKOQvWqmYx31iwVhr5TYr5xgKzCkEsr2Ix4BQsBpxKivmmYflQlg9iMeAULAacSor5Fs7yfVg+hMWAUzAfTJUU8y2S5aNYPpTFgFOwGHAq5qOpEGJY'
        b'vj/L0zhvA1h+IMuHW6i3Jc0PZnka120Iyw9leRrXTcfyw1i+L4v7pmBx32g+ksV9U7C4bzQfBflRLD+a5aMhH8fyepbvx6K8KViUN5qPgbyB5RNZvj/kjSyfxPIDIJ/M'
        b'8iksPxDyqSw/huUHQX4sy49j+cGQH8/yE1h+iJ/v5lDJd1PHvDZR6TDJa3O4MIPRvTRPGD2JU9x+bPW9qx23vLwnPf0ekgLQdXiMuokwn5UKcy0lmeUWyRXPZWUbTl7P'
        b'EhbxzOukR51LxJ0dS+AelLTzFehMQjU5vzO2ZZRAm8XDRIK9wk1VEF/NAbXZHd4KrS7RGCi+6t1ImpWWWzxbqqGsGw/CgExmpeQZY9aVM9MlVCfu//mfATaIIL19lfxD'
        b'XQ4LHZCA+sxO5o5KG8f8VVZCTWabTeemwpitnrKkgMPFAS/7WDHVLylxoR4azmqOckUNCD2UN/ZHTfzyIMcAL390MYstcEaZALzQJKZylipYqmSpiqVqlgaxNBikVPo3'
        b'hOU0LA1lqbaSpmHsOpylfVgawdK+LI1kaRRLo1naj6UxLO3P0gEsHcjSQSwdzNIhLB0qyCDVCRykw1jJ8NXVa/llsQ1oNnpyCcjG8nWKtfJlIwR5A7ebc2pBCpD3Q+vk'
        b'tQNYqYKWOuIEJfD/kWvl1BK6Tu4aBfKAvIGH52e4YB2vlYs2a1ccLV+raJBxaMVnC1ATwF6mbeLYk+Uu/WZoBRPk1HmOu1SCGCcugU4Lpuclke7hTB7eZHqsMI10jnQ+'
        b'Htnx/WozdeVq9wYTbcbxHk0hSAXWGsnDUinug4rBR2Umq+BRmNwWl4PGlBGPUHjCxFjkvmNzDio7OZ6gSRpNaPwbMeJKLpMEAk9YglwobnhDjXVuB0i8FgDBpAAV2z5w'
        b'mT1KU42zioFeTk8eKkwW8Q87hxjqfY19OQteqqimm7Us1q3Z5XaCKOKwUNu+2UZDItVW2qHFbEitldYK5mYN0odIMHy3zTWu9g55Ik02e4XZFni8n0YYrqZbzE5oH1uw'
        b'UA37K0Ye9gwydRhykHJhMUrPKuC6xukJhkY6XE7qPM7kKI8K5oXOiUeb5p0ZcSZUTotLuuF0Why0QnYDRDXm9kDtHB7l8lX02+F+IRJq0DcHaGCz+zsqI5YyGTGCOXZ0'
        b'DKel7lTSzQ8v/o1gVim6oUZtxTSe/Jp+HUbkWwZ1dvwc9ei6GiHzetTGdATkc62dWswcKGqXt5/zNIghF1x26Tws9XQUgGpbK+uBFvvRyF572krNndpzc6O8zX08KjDa'
        b'FvU3qLG72o/hskijvQ8t9ETPcGN8cAPDbHUGS0Ob9vb8MVvsPUAdGNhb/yBbHcBKcUb/j+JrDfHB1XcRX+s7gt7SqxhOw3yg30nTidFlne5y6bgIc6Wn8CSvHymcU4/t'
        b'YpKTWBHbWaWCTh28RoUUFv2miwBRRl1Re1ml1UIBSlID1A4PtPsE+XiBUxcvjVO8AS6tLvbXG4ornu2jxosRseJ7PU+5PQ9WnG+wxnaOidINfqbNXJCWBMmc3mPpWz23'
        b'IsHXiqkBB/Vp8BFLeeCR/Y6tmVU4Z3bS7Dkzi3vRGgmB3u65NUZfawrZzPuxb8lLzHsuoIP7klE3m8VIEZ21bKvM9U7p1Lqu1lJlpnp3r0fsFz23MdXXxngvknsdsPya'
        b'K/FoXVzR/AWlvR+fX/YMe5wP9mhG1u325VSsFc/dg7RbV2enx7FAKnKLJ/V73elf9Qx4og9wWLHvhE3vAEg0+tc9A5gSSLVqYJ2aqyx+yFdXXe+k7ne6grTMPFjXtt6D'
        b'9vQMenrgoLaDtNmrAiHq4rIL56T3fu290zPgNB9g0e2wVkh02RPhTzur1sXN6R1Eiea82zPE2T6Ig7uMAKGLy/1W4H7TM7i5PnDDRL9KEAdr6REUaXGIcTgKSgoLej+m'
        b'v+0ZZJYPZASjZ0w2ls7S9HoVvtczjNx2CtCRSlF5mvoC0eu4mfn52Zl5c4vnLOwNhZT6937PsAt8sP/aEXagjG/UpQNFmGuB1tQy+c/p07a7ivsOhGpBZnoxjd5u0M2d'
        b'P8ugKyjMzE3Lyy9OM+hoD7LnLNIbmHdROkWVaqnO7mqbnZ8Lq0asLj0tNzNnkXhdVDLTP1tcmJZXlDarODOfPQsQmAVgldVJHWvrbGYa20qMDtJbnPyfngdwvm8Ah/uR'
        b'b1EdEhHSzBag2Qlj2FuYv+sZ5iIfzPEdJ03U2Yy6tPZzb5l56fkw/LPz5lKaTpGo18jz+57bscTXjn7FjJ+LaiJMnkCxxt57GfSPPQMytVNzKWILO0cpgrG0W3z8dY3e'
        b'gv6gZ9DlgSSunbRR/3IdNVJ1YB50O8S3DTJfAufMY055MWy7kDl71Q2i1+IZW7rtAb/yBkhN9HkFc+JT0DdNLF1GTSOqBo7zoyyPpxSK/tfUTOWTX0Rhqt1g1rWwZdSr'
        b'HT+jXXySJh3CNzNbA3UvdNDPe3r37CeirnaKQui31KRKLTLJPwKBBhvDHPSoa+iagR2VSb93up4lajQTvG5gxeIWQNdTRLcc7LL2PapOiqvP+abj3liAu5FDy/bHEN3S'
        b'rfLbJ+MddBfKI6eGh24c8NSSWcJEh0ZyJ2GnNbpoivhg132ODGgKjbbrGwFmx/K2RcHGrXtvQJul1mRa1aEtXRgO2HN5+tiutp+YQYNtGHm0HYxTE31Y044wS7244gkN'
        b'tE0pJdOUSuLQ7Du5HqVkllKIVik5M0rJqU2KhSTxaAIMUkrJHiVntiVtB8tTiL/hSSlZrNTtBivRWKQNNEg5QjgJdRz041UO+h2o3kdsc3wfkp9Saw/d5VJr5HxEai+C'
        b'bCg6h934lmE6OqfynsN6aILVMrXCTc1b08kDfCNkZWidRp9FdiSk4Ot5OUbq8E6/AhBfrcBX5XMDdpu8PsdOuv3Yvtsk8FsQ+xigTJD7PgaokK6V7MOA4rVKUAlqeFbd'
        b'yFdy4kcAS4OEEEEDZcEsYi0vhApaKA1hT9D4HupSjRjbozRU6MtwP9LTtwPm5lhBifZuhcn91zJ1nKe01MScMEwc3U428VU0aoFM8DE1ORPfPUG+T+/CZY1dMNvop9qG'
        b'dzQ5Umgm//0Np9dHI5pje6jeStTeOjoSKLr1ulHm86OSvh03qAs43/p8/DfoIdt81rwuofX6G22SEDuc6xFaoxdab2WL2J7ra+qyvgAfM6/zRntccg1dyCO6r5iu9u1+'
        b'3KK7aehMpr/Bc8MPZiceychLqx/UjvxQgsoI8v8FP9z9zT2UeKJ3kQe4buWhdtcnZ4QLAEtHBZjr1nKZc6x0tEDGrumVfLnMMdWlELexIK9cpqLOf1z7J+weJ/pLqTU0'
        b'iEB5e1SG0R1aOTrwccFuEY/Ni0cSWKQY7zE9RuBBmmn1LkrxW+wj6dUomjCfEDo/wI3q6kAb9p5FCPEDwR7txsFKZhaEvT7RRgrZpWF/O/FVNrzwfNe4Eyzhjg9l/Wey'
        b'M97Qjx4e9ZvL/l0B6yxF+XypI9kaEWn2WjQbNXASysryAqRV3wv0hASll09q6KEQKoQ8za+g3t+VXo9z+o0+r98d/Vqdh3N1WmOQnPC2WonWJHbVapfdZbYBCaLbQs7p'
        b'cEGpur2mbjr9IobTXdONeKNg7z3zTWPCnsrTazuKNu1uMAxR2nGkXQpgQkECJ42+w+iTDHqIgDIMHlonkwYcOK5S/OqfWkadQaizBwtAoMSX8aF2Duxjv+QGaTYAHLxN'
        b'PptcVuXgq4MDGHG09Ne5kwtgxDCt7Ed2VFEqo+4e1NmDfuRPCKZsln7OT9BStir0OaotpV/jVQDLjRD6AptVsKO3ahoKqzGisX+lSogUoqBcaVEJ0UI/6Qu+KiGGXtNQ'
        b'WcwpRCUMZPlBLB8M+cEsP4TlQyA/lOV1LK+B/DCWH87yoZCPZfkRLK+F/EiWH8XyYWKLKmXCaCEO2hJuUVUiS3gD2smVhsO9CGi9XoiHO32gJ5yQIBjgOoJdJwpGuO4r'
        b'TJICfdFII+2fQ9RCP8NZT/s2RjZGNUY39muMqYxigbeCSiPbVG3RQmorJ0ymUGA0ZCz0Fg02FkU/HSiMh3tTGJwJwkRWHi2MYQtpqkdD8c/rpuDhCjxcvl7h4efO9PCZ'
        b'czz8nCL4W+zhZ2V4ZDPn5nlks7OzPbK5Mws8sswiuMoohGRWRrpHlpcPVwU58EhhPiRFc+iN0mzmQQZvZBbotR5+5lwPPzvbkUqpGZ8JdWcUevicTA+fl+/hC3I8fCH8'
        b'LZrjGM8emFUKD5RAYzJ9y90b65x5I0jfDxDjdsl9kc7l3UY6F7n3N36PVJ4nnqfdTZoHUYR3keZ8I2nNpcFG20OM0uCeCcZMSEhzjiEzd14GrIOsXKN6LWmm3yadTjaH'
        b'4Zvr8G5rxe0fck66S/X75176U9knZa99GBcRZ84w2ypt5Qbz6+WflC2r1Gx6u/L3OSpkyVIenv4PvYwdo7TjfboQfN6QgbeRVm8khT7kngxfduE2Fo/BibfJSEs+2Q6Q'
        b'OfJCJVLjI/zqdPw8O1S6OAjvkz56vJCc8v/osYJcFOlCb7aGeS819p2lFH8mUmfCNZH+KBT4MWFF+9a04zOadP2FCZn4xAjfYz7I1ylZosdF0caAnzcDQvd32YIKtTTB'
        b'FFzgxynVDGeCpQ9zi4tMDO7T/nFKdVMQ4FEQ4JGa4VEQwyP1+qCuvmsrR13FvB2Yxz6xNxgf6ZPtDTkIaJOYSPbg/UYao5YGl42jE1xSsApvycDnZIjsrAshu/Gt5W5K'
        b'7ck5cg6fb38bcCw/cb50fjuLtAIJ3pW9II40L1ADoiYDbPwCfj4kFDdPZ2fI7aUqpFm7U4l0ZbY+o3KQeIb8fv5sZ2gouYD38kg8Qo7wFfb8H1RqFB5u4FFZma3E0R+J'
        b'sWrwJUBAGioG3w7xBqgNPFKuQouKVPX4xGAWfDZmZEx2Zm62gbTqObwR30AheTw5k7rYrYOb6/DhlQkZ9OQ52TsG7ycXkpPxlrJsNBzfkuEXU/Tix/4a3XhfQh49gtya'
        b'W+J3aD3OmBhHmpLiM3PXL+SQXa8G9tOS7aYRM1bl4pvZpCUzJ0mJlP3IDXyc17rxaeahSI4vx9B8GOlEuInv4UZymh8/gbzAYt4X4/t9E8Rp6ADpNjkiQpsXx2KrF8SJ'
        b'bcJbM2RoCN4aiu8I5K6bro0BVQnOleQ6aVkpRxw+hMiuGXPddE+cbMLNZJP/Fxrr4LniOJi9FoMht0QMii8e1PdFphyBHyJyWqYhu/otYsF1+uGzumzp23LkWbyJbM+B'
        b'rvSdKyPH8LbVbmrWCHORs+1jltgeub990OZRMDzenmDmEb6FH4WMi8fb2afki9W5ZO88uFhTg8+h3IgYNln4GDk3AIb42qqV5CZ043TVKnLdpUShA3l8KIPcctPvTZDn'
        b'RvJOKJ5PPxcQl5VoWAVPtgItZNAK49qbpER4L7kbjBQ17MsFfcPlCXQUYFRaksiuorg4oHFNSXkl7d8JIA2FKgQ4dD4I4fM17HuX6fjoxBCYmZtOcmcFbl3l0KyA3GV8'
        b'FgZpjAxvycabWJTjaeSKFXCD7MhNNJJ702BsFSgC75PhK0GRDNlPVcmReu1zPJpRljNKlofYNOIXSEuG9MnItDT66ZWjc62jXP+DnLXAhH7WfKGkMDOPzAj/9H+P97c3'
        b'/3n3Vpv2qd9+71D+7qcm3uR3jIz4dZ/3f78kZph7hLZP2HuZUzep6k59aig0jvv5b0re/k1Fdm7b7rfrqzIvXVqz4NSO6227Dhx2Rz3172OzX00xxg/pO2Xo5GErLy99'
        b'qrDfG/H/KBz9TFPV2uwUS1jB4/f/fr6w8d8HVn96ZvJTW7O/lzazZcKVy+d27JwW8vo17ap/v3lhX3zxV6F37m1ZfGdm/wOk/+qExGvnF5V+P6Lf9me3/Ez3H67ftS1j'
        b'Hv619pN3ry77qmW6OWfgD7/63qRJq8f99BX90dYf1u4ateJnJ17f9M6e3e+Mih908R9X3tW7Pnl2+qZR2xJqy47/5Wxkv0Nb7/4o/Q/X/z/23gMsyjNrH3/fmWEoQxMR'
        b'Gyp2ho69oYiidJRijUoZUBRpw2AvKEhHRVBRsCJiowo21OSclN2s6d0km03vfbNJzEb/T5kZBhjQZPf7rt/1vz6RmWHe9316Oec859y37yXXb8Lefjtp1pnYMLfKxGu5'
        b'c195veiF15Y6xwye/tOBcd/EHF9jkRpzJe6fLl+l/nTV6ru43btfWBC0bcTMtFGDNj4dE/LCUyYr/+G6ftOhF0av9Dm40b1U9kni6U9P/9Dvu8Q5RTvECu9XfF47fl8c'
        b'Pb3gnXuOypGcIaEUqrCJbYQad3dTw20Q8/lOSXa2s2ROF2npCmVYi9lk3WqQ4JkYvMZv2Qcnt2gxCaLhiiGEszfUsVvWwSU3KNpgbWWRga1Y7qDGtkwruWCfLo3E+jQG'
        b'4IB5uAsLgsPdTXEvBf4RZ2/HJg4xUbUlTMfRALfxtpbD6RqeYVtxBJasYbSbxUrMD5DNh2ukfPUSPE1G7i0OMX0S8vEmFNlkYdswPJlGZhfJXNFfsmYYVDAQbLy0IrKD'
        b'dNNksMQ9TWRIRQvlVpwBYjhc6cSmeSU9k07u/gtCgj1CsWyTXJBsEmco5rCnNuAFvE5mXyFZJkihPaBCNlWEJqjEKwzgwTwIT1DaKbwFVXJGPAXNUJ/J0MhKRrmosyzT'
        b'NXjFBgqh2MbMygIbbbLIdBxrjm0b0knJQ2VyuOYZywEq8rFyuqs7loR4i4J8KZzH6yJenGzNoI4WYrMHmXREv7gJZ4i0sU2cR1boAwy8Qgb7p1LyiiK4GBAKBXAWb+Je'
        b'Dwp4PghaZRvw6FaOnnGRNHk1Y7mgHEVFIabzfQSFrwQPQlUKu2Mbtq7TcXe6Yznu92ALgkOIzGpyOCsjZjvCcSjypOPMRJDHYKWHZAQWDOedc3FxArmmXcpMsALbBEW4'
        b'hLw3wDXG7QlX8CDe0BKBhdONma47BSFQBSflwjA8I6OaEuaz5Ghlc7T3LoEGNmY5aRgeSGGNEo63lQy2qySEtFjgtiWS/lBPxuNwWtL9OyCfwYG7e4SFhM0MZyytojAI'
        b'q2Tp0ILlDGEDdsFFH8rwGTYPD+kAj60jpaFSvMFhxQ/F4QFK/uFOpIpgaR8sI0OyUIJn3bayBkkbCOXkcpBbIJmBx9cR3XCKJG4yETypoEb6ocpDd9VuNeRriU8DyeB0'
        b'cTYhm97+dDapto1ZQG4Lc4MCT+3y7pdgQtrjiolJGpQx3lofuDWOlcMliAJgaQFa7KCeiLbQmpxJLfVQEEC5W2108jiZzqe5TE5GxV7PzjqpK9loSkZawHG8Jc30YK1Z'
        b'H9zxMFk39nkYPAznMD9EKRdCBFNoxsboTHfyiAecnttBPjtucc/0s5DXh6GP+U0YwYcIFISvh5v8ATlRgKV4G4/gOeOy9n+fRpXZCZjMntJdZvexEM0oc6pEJg6gQKfk'
        b'3UEcILEUZVzpp66aEnuGpD2IYneRzzQOz1JiISUyt0Ru4BhKD8fkBn8xy3C/LrI4NwlzdcBCG8Wk8xyWUeNZBh0BGZQB9a4iPjZT7wQsV8evSVif0BVvxfTRoM/CRW2i'
        b'GQvpC0uEZRRB/2S2mQWiYXtd6UHT+FsnMlbjtXtU/lPTVbxOvaGv6o3enbN6ZGu31rYe2bt1+p7+VNiZkZjoIh14+Zy0UChduF7/CMrsXcUqrc/Sql6JcX7XF8TNmJ9T'
        b'krqjbH+IZFNr9KdnxL3kThU3nvvQKObgRN2b/hOqWdNV8ZrM1MTEXvKU6vNk/KbkfnfygBN1ue9wtKLlYE7Kf6bSD3FGkOsL4MKcEZIStd4H66m3B2nxhBQaMKL6M2S3'
        b'dy1XGczhXgphri8Ec4WibhCrKSSc3k/wT9Rb1Xu9LfVZju0Z2Lhzxtp82WKqh/+jRlk9WDw3Fgg0gGWbuFm+lZ3BUzxgUdgubBeNGZ06wbfojQVmHTZtqWFubiy3RPER'
        b'SVsp5rBGNAIxSP91Ygvq7FChdlKvSdUkqxh/a0IGgxd3il0dS90wjKalp1yak5wQSx2SnOayyBPaiVpoXObFp0UK17rzJBmH1tWCiMfERGVoEmJiOLtsgpPLutSUzNR4'
        b'yjjr4pScFJcRSxKnLls6EN4eKQAzu81mipSvPdvnGITcFWyTgYfVw9HUY2LmxSarSQm7o/+xoCnB4J/YrYulYUnW37UKasbeuG7olzF/iTNLFGv+ESIVzPLF1muPK0Um'
        b'3g2AXdv1gkSHFIG38BiRJEzwhu7YpctBjyxxdQLHPWMUlzu6/AzdPKrTlqKOT17F2rbjHIMm0BMlrKgD2ezAM6MQ+rYy7dF1l31zp/CDpcHOqaGGNzydmEENqsPxpIFN'
        b'Ffe7GlaViOxUTi4Ip6oStOGBYIaxio14xcqL6Edt/yUyWR0s2sONwTSMwx+rSAn04iAv6iLMlw8lIr5LkBucj+JmI/JaEB7CSKIuQIFiKtxyT/r95seimho8Xs4+82WM'
        b'h93nMXfi/hHrbKeMDWFG4K9iPotJSfwqpnB1UKzZ4lhmCD56w2x4ZJhSmkmXG8zbTomeOufeVRTNx51MHMXDrgzUEMu9oZiC8VIE6M7kSByN130Dpye+PXFM9+E2AU9Q'
        b'uXUuVD+SnZgMPrV28DkYG3zDGbnrwwcgSUSXXweEf680rx23sTEZQ8bkoB7H5GeGdmONP639/vkz6JhcC01/ZEy6htEx2TTYagZcxBalhNmOdsD+GcHBgTvoeJXZiERZ'
        b'bVrATJNEN9zrHeyaDgfoY7LxIrQQ9a0haRE+zylbRw9xXrc6ID6EDIi179clrFm9ZnXy6qD4sNh2u7BY8YeB6wasHRC55FMvk/FpiYLwlJt5bORI3ZmmoR29x+4x1zd2'
        b'z33kYGlhK9vsYLyPdLn13BeGgeikE2x67IQfbQ1F6h7y+y+QmD/iDCfLsmX+WIma2olf+DDuSzIZ78StSbRM/MedZUQR7PuD5ElfB7I0036asGzCDj8DLfThGqgyuls/'
        b'dXGt6HnFdu52ssF8LHpYoHvi7KZ5DO+xM9637u0kpbNPx58VTLqdl9B/3fdHWVhU0rMVjqKafv3Vzfzg2MGFtBfISq8UXT4t6hDquvsaHBd6a0jXboobdyB59K2Opj+q'
        b'x0b8u2VvSmIXB87/pBUf4fSSDOfaMYtN1NTMdP13M9dYSmV/J25tYqInG9TJojDcQnpjWTnZW5hFs22NOxa5UbvNUAuZrwitqyE3k2JcTwvc8AeG+ko4C8fdoIiZjmIW'
        b'wjXX4B2W1NrqLhfM8IYE9kPduh56z6rXaeDRXe3mDquP3Hs0/bE99t7bvfaeNi9avE5Hio66lo8T2JEiPa+3ZHqB7sRekteHSSSdzu3zTPIGsqPGQXmD8xwTHfXHjYpe'
        b'jxs7rWPUh8u+W8ePC2OckBsXbNedgrnjLXl/iTWUmrAjJI+MOQpq2G61occm2JwJuevlgi3USPD6DLmGWtkc4UQKO8oJgLII0nnhcJEf6fR0noN7NiqgNSiZcUpPM/NR'
        b'Y5svUswW3CdAsZOMFWm6w1xs0cAxOCQnF44LZCjkzuVHkfX2NgpsM4Fj9MClldnAoZ1tpvPgtpU6E/KDSd9hvgB7oDaCpQbn3aBFocYLUE3qjg0CHF6/juUvCXZXb3DF'
        b'o6SvsEyAQtgpsoOer0Q5bbM0P88YN19JIj8FxfMTNfRkC3bDGZrOaQEOOvXjVKA5eBErWDvwug+w0NceGzMz8HJkgCs1m/MjrX1w2Hyb+xh29Il7NluMx33jvbAR2mSC'
        b'SGqLO7E4REPFOPExyKHnqIOwqIMSVAubsnDBYqwYHxRpKkTjYTm2kjbKYQdz1pusxwtQivWC4C14T8MD/JjqIpxwwQNSLFstCJ6CJ9TAKVbX2aEyyjziu3J+jKVZQryg'
        b'mUu+HIrXISdYnxXmBzBeb/JXAV4MinbGAlKOSGcl7l0cEEjlneJQJuhE0PrJU6xWwE4/lhDshWtwlDpAGN64GIoX0YoQCckzXNtOhgfEdJxcgBuW2IynoVATK1BvoqN4'
        b'2Yp6SszC/Vaw08vMBHdG4zE5lkZZzbMbZDYjAm7ATTyGDf6rN5on9k+3wHb5BjMoNA+3hEbcjTVEGdiiHIb50z3wiBwOzVFCy8wJWDkADpO092oiaHELB7mZYDZmW+E+'
        b'peBtJoXGaGhehhVyKMA8qHAh/XET90Jp1OCk7VCHOwfDzbUjBsMVKIZcaEvcgjlSb2dSiJJh2DS3b+iIMWwdYA2dqxwsTpAIXmsGxAzZbt1PYPNn0GNQiUWhY0grGdLI'
        b'snN+/eGmAY9sPV5RxMMtbGZJ7hvNeGljmpJj1v40OFDQhJMvvfEQXKKVqDQXnCzJh0Ur10EZkTqv40nRG49nwS48M3086ZMDMdBKBu6R6LF4ehkp9M5+UbArAfJX4wm8'
        b'aroG2m03jYpiJ8VzoQlyu3LdYj4cSg6PDHAPMrHrR3sGzinJf3oEesEcr8A+0jVKkVG1JAwif5FBQPYCLA10I+uB+0w4Khf6m8m8oN6RE9vfgmzcHWycFPcy7jFOiluo'
        b'tEzCwkUaqs6l4TUyUboeEMeTrut8Rqw7IJ5JFn0+Oeo2RbiGpYVgqShIoFScI8IFDSXCxFy8QUT7ANJ6xXgKzoby2eAZFOgewf0wunoZLAwgml0aXQkWRLgvkgibomw2'
        b'4W3MZsNrh3NkMCnarr5kVgUu1HplaFXDgJBwVl+PhWZZ2LYwICg0zM09LJrTCRu4ArDjdCyO6ANn+kIDGwY7wqVUt3XyNYlxSxrvRmtFj2sGQ/uwYA8sw2P8vIbsqo0S'
        b'ovWdw2MaCvfnvg3zI8OVoRx8Pnox9TShXiYzdxj4mQik9c7DTtK9ZVj8mBPRUa9CTcBwuB0wfDw0yAQyRbPtoJIsJ8eYA0D6DDhOVskWG3MzbLbBlsx0jSjY42G4qpaG'
        b'47VlfEU+67Mhkq5eipVSsuRdFPCihUpDD1FWwrVFwUrSPQ3uVDEOCSMFc+4sPkiFFU5msGsambLsGLUWayiL0Dw4GYUllEHIxEWEIxtgP8sKm2OWKLLw0ghrkeR0kKwr'
        b'WJHJdCyTgVGkoJfV2LLUylSQ4CXRnSi+Jco+vIhlJpT8NwTbncmDUwQsTcJazmu0B1uCtR42uXCAnZIplkmwngzvQpbyJGzP4ie7LjKpwM914ZQ9L8/OadgWjIUi7gnh'
        b'Z6TYvIDtBEvgAtlrmf+BK+wxEWRDRTjlh62sL2FfzCKtNwe5qVYJ52WCpa203wA4ysIdJpOiFJChr2RqO0Xk5yeXJsKY0VNhp0kinB/LSr8Y9+IxcgWuQzNf3UUyLg5L'
        b'oGI1nmINCpeTyLds8emLxZ5hJoLlaqkNlsNeVjkpHII2ykmAdXDBhJMSSPEI350PuSzFIvcwdriIZ1bKV0j6WQ3ju+dxOBuNRZSruz2EDNdJIpwLtdPu6RNW02m/iiTE'
        b'an0azmAec8MJJwvXYUZYTTa0dnKVMlZDA5xjY20uHOnn6rwaDvGFkoxjOsVNhOFwwMR8IOkuOqLMJs8j6wHRxL1JhYuhwNNYI4VBtinuc1vBahhGFvbzrh64f32gm5Js'
        b'ReZTJXBmVZpSzlXzG1gLRURsgYPjdWKLCg7xzr0AZUOI5GKFdTrBZWEyq+MCsgaUE8FlKpzUCS7OeI23TC1ZctSZeAuzdZLLItitoZKthf1khTp9kU5qscGD7OsRU2LU'
        b'G9ym6qWW29bJvzx48MAlnu3kA7z9YtzEScMF9uVjcSZse18eEuMWmeEjJLkcDJKqN5NnT334g3/ktdK+s22//mbqjKF731jZ8HXTz7euHnQdOeLN/GE7hZOvzRs98qeA'
        b'xIlZb87xHXzOcUnGzvz8Pu/5/mXDV2O/E3PaU17we/GV6IaVN784/837+x2WlVWZXXB54uSiFhPlyMKr7YdN7b8LyJsT+/HYwHBXc8+Xvc2DZl1oqrP/5cHNx5372s++'
        b'JtxtHNG3pcC8OOdlcF7b7wt8R2bv4NL3Y8ndSvNJzzo2nWiryHW+Lb73Qd3Tzzh+/mTQuzWlFdEBK/o6fL/s4ElzTdAK188HfjHvnfF9vrps9rflH/0csvHsheVLllb3'
        b'/bztlfRJS6Z7LPuxbeqnK/5e6XzBdttTPs/fXCm8EHry26W/Vpz/IOF5q77TK96aOELav7J0StbAmNsfthcmXb1zdrjVhTefvL4+9+/NpyT41l9Sp3r8K7Si3Wz/lT2v'
        b'/2Xx51M1g7b8c/qLK/Ymfpeyf//vRb/7Jaf23R0377fMxoj7T6bI82a+vOfnvLd/DHspzeG7kSlv+OzN3HDp2b89t+K1g3B/1/TNb78V88/PNpokZxXc6Zu3PuOs8uef'
        b'rKuXKU3ODmxeneqF5TdeV675+weZl1LqP7cctG3aqnMJ077e8vSb42f+sC/yjtNPS16JXzXlNemdT0srp2T+K35mzZb77VtefPbdLej26nPh18Nt3pn+vuOPhRf2JDnN'
        b'hFDX9x7g9We8//1eSkPZ50dtt1/yfrp/5MeiyzcvjXRdv2T0rbeL/C7t/qF87msf5R/7+alxR8bUXWuw2RlgvWD0P1en/Wj+0/DX+7zuPX/MvE+W715+zPfDTyxuzO0/'
        b'cluc3fMhB96+/97U2mf+qXrtwmMfRQXvfmNFa8i6IXduNUvGf5xt5XjqheKWCvvaj6+O2aR8LO/eOxPeeSf03rIJ7z0wmTdEMqF1t3I0d7DJIfKD3gXj2grqhaH1wSDL'
        b'Jecbu21PKUVwN+S6c+8ZsmUyLi0oJ6oHWUez+mmX0cXzuHGSLNobdUwi1HhJ0srVcYlUwQnmerMRdke7hpGd7LjWPUMwg1ZJ1lysYo4QU7AGm/gKv5lISB0LfCveYk60'
        b'sKsv7OUr/IAV+hV+F9zgrh/1eDlO61pEpKb91FWDuxbBgRGckqwxBHZqqVDIjuBAqVCgMoGlHU4EzJuuLkTR8VBiIVH3zZeS5QeuDmBXHWcluVKyvQI3ssDuwXI5lErc'
        b'yRZYysu1x0NDdvxbGe56PjzKWuPlwZjvR00lMmoRWf/rTagkFt4hj8uFYcEyIgC2wHFWPrIPXod9rtoCpA+Uw0XJeM8Edi0Qr5LdmDsVkXX0KqPNMVnKzM7BeDVaTVbV'
        b'arhllm6FzWrqA2jg6qNz9MFWOZFhW924c0ol7B7t2tmabBcoJY1dAyeI0FXI+3XXVFmwzo4djoWk1/tgnpRIHuVQjGcE7tVzLZ08VOQJ14jgVujpzsgSTQWbcOka/wh+'
        b'R/0QG9dwN6KLFW2EFnZVgbckRFqtw1zuebRvYjppw6PDOglNaj82Hn3hYDLd+4bCXu3WB6fXsYQ3Q2OG1uOsw98Mb8XDJbwexzqHyF0NE/QeOkOwWR6oddGhNp10bAs3'
        b'bjyhzibLo/TuJr54hTk6peN5PGfg6aTzcsLiFObodMOaud3E4mkifOmccjqcbuQhWrebjVDC5kQS7Jzr6jEPDyuDXPUMezulqRvmsjlB9v8z1Fk1lLLbkVLfpHxAihQJ'
        b'Hp2zgTl/DYZbM9hOHYm7tBs11k9kl8heeT6NSzYLorWCTeZElqvGz18n1pRDtl6swcqZbMgS9e8AVhmXayLIKCWCTcQO3rEHN0eQ0lH/Ju7dtIryFzrgHpnd/A2ZlJYV'
        b'j23Di49qn7pBFgdmjoVL0JxJN10sSl0SHLLBO5CsQxGiCzRHs+GyGvd4BLtlwU1D7j5rvKa0/E98c5SO/4P4r/+Bp9Bdmy7wl8wI96IgdDfCjaN2YjPGXGPL2JLsKMCb'
        b'hEO7WWhB3gaR6/QqNaZRCDmKVy4jn2VaQmVr/iuRa1MwY55FdoxB0FZiIbXXUi9z4DgzcsWavVN/JWuSNvVSspDQwGP+04FtKyEpSNg7/6HBxZRpx1KbFg8k1Jv1ulTb'
        b'0D2Juw6xQLG+9KU/80xK2Kj3ajCIu+owOvb7X+s9nXOTnT4EjJaQcQbxQvXVezgx22cc+dOlR9vnm36dOBF7aySlyMLOwno5f6UnsCID8n34+auOEPEtiRFvhdmJmZT3'
        b'MDY5mcGUGpAJk0Il0dLEJndCL+VAVyoVx/GLdUpJ2NAtUe7l4hwTs2B9ZmBKYkyMU1xyavw6pYcWaVbn/6BRJyRqkqkTwqZUjdOGWE7GqEqi/IndiY4NC5GUwm5MZHH6'
        b'2tjOBDUP+OTYgk4UMckpSaV+dKpDCi8wzSmQ+SGQ8adOomiuJB/qkxDrFK9RZ6au58nqqxaoiolRUvCZHl03SPvo2oN+TEpxyprsQfmz/UgzbqCNmbkmNlNf2g7vEKMp'
        b'auvGIGaZIxP3wSAJUMDZTk2kC51dnZGqSWPQc0ZTJFXPTIrXJMdmcC8TLec9R01QOznToHU30gQkWwZmsimN/JmQGe+hZJ3Qg5cJbdDMBF2/aPud+ZildOW01Pa+KpUF'
        b'7qZRcGJjaXbqgF44IXWBrZ1N9uZhTAedjYfxKjPa482hLHpFYo1FPhq6ZUIzkfJK9PEOuAvrdTEP2niHsVCgCSZ3DhsXxW2dgpOZlBpTr6cTFWTQ0IC+o9O3YUMESefS'
        b'HChf7heYSfbyk9Bo5hO2Y7zbEKzCk1g1F24M2wznbb2wAGqYGapPeiC1Rpo5r4txaQ2bL2gojwtc8heJ2g+XsYaIBpQMei+Nl6FhSKbCiLUyojJfxmPs+S+Tmaq6IGtu'
        b'TPKTPjZCkptPvVSdQa7cmPXN6GebrHJ8LU1eSv222dHet8+iXyf4+vW3XeEXN6Qs8EU/M/OwkDecVkzaPGh1btmLNk+PzbFxU/78/LPX3t2dcyVOerrIcfm3sxW7x7hb'
        b'TXbc9M83SkZ5eO/9bX7hg2vbTZ6P/NjxZGuNdfE5B8u6T0ynfDGo2veBUsGliiY4BXWQPdzQU5zrKDtCmB4yX6Lj9CUqOtFPZmB7JrWYYn4S7DMqbSzBCz16Hx8ZwEXi'
        b'QqzG62pq93V31lm9+qwgfblPCo2ToZRJ4suiBooSXfyOVoUhYgoXueqhKYP5z0+IZR70Il5M3sxKHDI5iDnPU8f50dR1fp/AlZLDeBSPUMke99vyiAGJ+/ZR3Ccbc6DQ'
        b'UKuSCAOxlilVoXiel/n6WNjZRR6F0lk6x3sXWyaO2sLxLd2k0fHYqPcCx/apugO5h3mQmNOwPTY1mRTibEwK2SFMoZIDlSiIZCGl0gaVM7o4EegT6szc6NB5yzbiS+LQ'
        b'eetMIH+eplunk7Gtc6fwnl3Pjgz6MlCvULKjrCJbih6vQBfG2pM/oTRf2mMQq5QdA8ve/0VmZN+MTEjR4ol2RjDXqPk+msBWMrLs+vsFzok0QCXvafNJiEuKV6+KT04i'
        b'qXCuXR1SUyJFVoxf48Hu8PCnr3PYbT2BnRukqm2Pacwj0U3vkkgReNUJrJipGSr6BVnWjS67WvD2HsvgMS86JIahs2nSklNjVbra6xrEaKIU5lOPtkZ3BK07rlqTlMkh'
        b'1PWFMr4ZPLRUc+ZExbj92Uej//SjgQv+7KOzlyz707nOnfvnH/X7s48u8R/35x8dH+PUg8j0CA9P6MEpNDCRs71wASZB5ebkoh3+Lp08Szu7vjKHOOMSR08OrfMyYhmY'
        b'dccY/iO+q4upjMpXhazxHl6dZgvzueUgsnw6kQyzkmL/XEv5RUUbKUIHFzddY3g5+HRLUvUiVskEY4HXDpxqWz7LdN4dgWj1TjFue7ZE8vjOBGzCErViuh81t58QoBLP'
        b'KJjdXt0PD2CLF57FRi8vE0ESKOCxUf2YX8EIbJ/vGuYhkq1vpwQOisEJsfx8IHv0WNewIImA7WYS2CVOgUJsZbkosQLaXcMCRSEmSwL54gwocVLKuIdAE5YG0SO1+ctt'
        b'sNlEkA4SfeAC3GQHJLaz8RK51oiFSzLxCtnSsUIcDvuhip9r7t4+Vz0uQyLA6QgxlXoVFo1gAqQznMV2NbZtgV02ZOuSYK3oAnUL2EO4E3eTWlIEGE+yq9PTTgtWehke'
        b'WUaewSrIEbQHH/7b+ZFRPl6EnbSMyzG/o5C3oJIVkvlC5tNiOkNBRzFnebB27K+Moak2u+hLQqp0lhVl1UzYzctf5sjKvxWqWQPDuemTFFm439GcdKLUXPRctIjVC0u9'
        b'8IiCugnszLAhArSbOAuboYIl5u28iJ734SFzhbUoSC3FWcvjNBS/HsrxkCaYiqSRzB2Xnh0TGVXAU1C2lQjBxUT4aYdyqIoif5RjO9ZgGZGBy6HdzgQr4kysyEso5GJx'
        b'AtbOcOpLZDk7Gyo0wk2lhB8ZnYaGTbR1Rth3NE7TXNY2Y2LoeSI2wq1+Bh3YjuVKKev9vhl0lJGfE1Cjfzgdani7V5PSnKSPz8C8jsdx33x+sFY3zYK0UgXW6ZoJW3Ff'
        b'0g+vnBbV35Pr/s9A9Is+Yehlb/rdz8demZB9sPZSzpNPP6m86u9g/V3UqBs/xHh7TRmydnhlSfZ+aZrZk0/euSNOMen7YNSQZZs23b/p+Val+9JFEdvLXL9wLiq7AJpR'
        b'/ca+UDb6l5BFr07p2+4wpa+75t6iJQfeciiYXurYtuwt828SPip5XPb9hIWrX1y+5p/+BWMCg+9vqRo09Pf+pwa9tHrWnMX1lg11F8ePTUlqHNj8bWPLyKM4M+bT07++'
        b'e2Jd5oMRR3KHffRJ3ubm/nnnb5xc+/5HuTBsa/qEpuyMNSee+zzlM6vMTdeHbFasKLnX+HrCg09mDk4iyt33Q3e8FbHtgc1du6V71/VT2vPI21Okvc9yA79jbId9330y'
        b'v1yBe+AQkfQT8AyLzuX2/TlwnV2Gcyq84co8qec6c9Hc0k1qCiXTmZ1wHOZCLdMI1snogYWpE5eua+biRVc41wcraLSoDHJE3G01k1mG+9sR0b8IC1dBMY+sZWG1PpjL'
        b'8ouBIjzoGuZN1gpDSV+Fu/lpw3k8DnmuQWRkN2BJMBWkzbBIAtlYBpVMF9hKSnRBrcBWUYCrItHGBKybmcwN/Red4BIUpU2UCOQJEfPItIb8dGbZNCFD7iS9JifaBB4T'
        b'6YzYPxjzmRKxZYMXvSQKW+1ELBCwLJIrTHFwjEea8tOPVoU+TnUuNnPNpMktU51FZiC5q06EWgGPQrE9a4eZJMd9aiiGfLJC7k0QyRJDatVE1B26/EwYiYXkQRNhKZ4Q'
        b'4axApuDVySxJnx0KsoJYCsJjUCFCvUCUp3w4zyKglcHL1FnpJLOd20Q4LGDxfCjnxageMYJckQimWCzCQaJywSU8zizrcJ6sXA1E+yLDYFcnDYypX2R57SEwsxd3apma'
        b'CNpMTVlkXE2JoYoJNVpSom9qMuXGTwlTV3Q/lixo0kKiM1Lqf4l6YyZu7tPZM5rkGKaDVWFxlJaGwnlGYmftRtTVIUmv0yTqAx4pj88TvSg2T3Ty0O5eDpK6RNCywIUp'
        b'+3fBqborWxUeGHZXsWpOdESEf9icQP9IDsipx6+6q0iLTUrRRkOykMy7Fh3hgtrgTXpzlwjO2M44Vwz2ito3mabGasUbaND/S0b2DE+qRkq1yHRmprZS2vfWUmuTAb4S'
        b'8umR0TIltraWEmtKuyabtNFMtB9iJjK/zvht0NQFpwgPDyLSynxZ0hTLTu7Cltp3tYvYmYNNJVF5qDxVXiqzKpnKXOWdKKjGsc8K1fhEgfxFP1tRYCnVJO33kykjGPvc'
        b'h3KCqWawz/YqH8oIxj73U/mqZqv82GcHVX/VANXAKgVld8uTJ4qqQarBOWYUdbPctFxUzSm3LDcrt6M/KscSU9XcPAryJScqsZNqOAOtMmWsaSMZANdoyvpGnytXlEsS'
        b'JeSpvuTXttwuif9lR1KzKzcvt0iUqfxVSpLePAogRlPMM8+zyrPLs080U7moXFnK5sxNV87cdvskylVuKvccM4ryKROWKZi6Pf+uHZ0EcxgdBINrS0zIuDeuk2Da/QYt'
        b'qZnhTfc8iJQ7LUmdOk2dqWLv47y8xo2bRoXlaRvVqml0Ynh4eXmTXyKGj78rCwuPCL0rCwicH3BXFh0xf8FdyVz/u+Y0s1XhYSFLydplKjBoOaqW3jXnvB1J5KNJIlGu'
        b'1X8kQ2+WYWBYZNQffGrqXVnk3EWz7/mtycxMm+bpuWHDBg910kZ3qgRk0DhW93htlKBHfOp6T1WCZ5dcPYiq4DXOg6TMsL8y5tMlwTwkfM7skFVEF7g3hhZnjl8gy5u8'
        b'L4jdRBejCGr/VWeSRDy8JpDXjIn0OcvIwLD5If6r/GZHzQl4xEe9703uct+cjFS12o/pIJ0fCUldHapezR70pg/adKnLvUE9F/BeP6MVVyo6pUI7vnuyXb6Y2kNaXb+e'
        b'yr7uvVQ9X/O+5/oH2uKuqSohMVaTnMk6gnXlfyXsoVsUj7HgESYji3gCzyqIPDIMrmsdBIdhfVKi9RgpCyt5b/q94FgeBSHzX/aqOC/j017CSu6aUXLUTDJue46aoj/z'
        b'OSZq59nvoXv20eMU9pJ6+ZBP6hHG9+WdwlOdYhV6y1VpyvfRBUY20wjdjvo5BUaLCusU2KDvJBruzwIbBB1DJ0dJS7TQBy1Y9Bi0IGVYBLL3d5kaMVMG8qDgpM0JBsZK'
        b'zrXDT4vo4tmLcTJSR53rlMYYEZgcoZ7W/UZ3py7Tysl5rr+y99voVHroHVOdnF3USfToKWuyxySXR0iSz04n5zkBD79ZO2fpzW5OD8un53nt5BwY9Yee8O7liUddA2gS'
        b'XQvdkx1Ya8viRh8er61lWdLh/Pf0JN3t+GNdh01aRlJqRlLmJo7M6+xC90/KXkV3UBfjpkEXuq/Se+jW50LtwC50O3NRenScjk7yGOfhNU17i/FkOg5Svdit2lQ7vp7E'
        b'vuZJ91Qxjh+hrZoRbAjePmPVDB6ix+ZhJw/TOgf8s0lmHOlBG7DfY5k6IB2m6clbu2M2UPwE/Vm6kaNy+o9cY2R71DTPTKLsHD8hNpMOKLWOiMwAAIOeJPeAGkDNqiSd'
        b'DbEZ2mN/A54I1jpOkQkJtK6aZANuM6NJzZkd5T8/PGLpKkq+Ex7pv4qyr0SyUuqP3DnjWo+NxBch3j6MIUmLpaLrN53+pDUIGz+h7jASs4MHnkKHDdely5ri0uMZP+uh'
        b'ND5P1ZyvrcsS48Jrp7slKcU4pAEHxyDypI6Ldk1sipN/dEQPxu4Up8gNSZmbEzKSWcdl9lJ4viD2MJfIhAnMjE3exB7seYVz6XnMalE9eId0gH3Qka/tEj3wBz936qFG'
        b'mdxlwQC6u9OznSBbely1WErdDgJI82jlJbVu+HZJ13ifaCkMO/Jl1JFxCcmpKatpSr0YzKkcY9ZNeLIN44bdWjyI+XiABrXskwoSPJ2BZaKz7zxmuoRGX9hFvRTgNF4O'
        b'0bkpXJrKjMljYQ8eUFtZSUbjeS2mqJUX8+qPhFOQS9VTKMYr5KcFCmSCFeZY404JFo0cpPEjN1ljhUewYcTYIsyHQqFLLE5nDM5QkyCJMBF2W2POEshhduSZ8iRqE+YG'
        b'4WnTxVnpO5itePlq2K+w4iZkaNsozgrGYhbBgw0R3gboqh0l0AXPYBVmR6dZWUVQjFVn97BoZ2csxGJPLHSjwJocNNRdTqp8qK+IB7B2Hj8ZODBHQtFAZevdtWCgWC5h'
        b'hxI/mcklb0vYoURIwfYVAouVwgKoG2+IEBpAAysKYD/uIxX2jMD8kIUB0ggooCF2eA3ObBotwG2ZAg/LsFhrlU7DBmjvqD2WQrU4K2kJq/9kuCrX1R8bl4mzvLE0yc/t'
        b'aRM15b3P7392dMlNC/C1zdnwbdlvgXGub/42r23Xc2UfSEasftbsiTkDpg8bY/PZsUmK9ybf+SrEKSfODp3giVPZ85fPuBD+yde574/9uU4VOTKxJm7oxVcLq5NXnlm6'
        b'MePXGdOTLuQOe+7YkAEWswYuzDryzgTz/B1XXtxWkZ/2/e3B5ZN/sT/jWjXrjZEhX+TU7Kic8/ub63ZETrYsn/zuwC/2vFjwwS8mlvs8LR9IlVbMwBfgC6ddPdwXwRUO'
        b'f1gj8cKTI5g3g2KtBQc5ptDMbtBuSd0yTAXrCKm3IxxnRlcPN7NOnhVQDeclWdCCN5mZUwYNsMvQJwSarbhbCBb0Z4bHtXAqmVqB++Ap5rcOx/AgdwO+tm6IduRitave'
        b'RzsrgvvEXyZjokARHIC3DZ0tmKfFdgsGfkcKmwuH9DZWbIMqvZEVbg3MZF43tSakxPyWCXjNAF1QhywIp3Sofxft8Cj1KY+jeJCGYJCZE5iNeN1gqNPhVErxlgWcE+Go'
        b'uJrZiDduhL0kGzpNL5OroXhghjgPzqzjJtYcPA9XyNoQIkoxW5DEid7T4Ewn2AGL/8hOpoetm9aTnrXVTrTQuqFS+gIZs6nK2C/lHbaWSETHHrQiLVRbWHdXz14VpN78'
        b'Rf4Eylxor8pd69CHKnePijjHIbHumqyiUnAvoFglJjq8OWPZ6VmTPR5B0u6OFXdXFhkwO+KujHKi3pVRelSdUtrZvZY7r1Jf1rumWk7tThqpjW7DChD0ofZcJ7XUaqVW'
        b'HL07zybR5hEC6nW6aZ0x3XS2SsVo/Az4O7R7sxEDn16q667iJjpNozLntBg9pEmMkfN+N62MpMfcol6T3Z1Mu1Ibcv5equl3SL6ZtOEytXrBI2lcWllZT3L7MKWLs2Hx'
        b'Z41w0caqnRKTU2Op8cGJEa9qeSZ7craJTenE8taVwranUnTSRIxxzGYmbORidqaemnU99/jswYWT3JOkojJiR1N08OTxOjg5M6J2WjUmA46ImOfh4TFC2YP0yl0mmDty'
        b'LB1NBrTM+pQ5IyWXqjuuG01P/0wHwaR2CGjduTrTTRpNwznCf54/PY7xXxUWHernH+HmpFN2OCNnjy5gzP+4Z0bW1DTuj91LChuN6Y890J/2khz9p1cvaQv3pv3pceC0'
        b'o9poajpebWOKohNpFf+IsNkh3ZVC4y7Lj6go6ji3eFPomYnpgNWOGzoviG6dwGinY2LCUlPoStGLL/fGzI7cGYMtbaPYZOo/TRcI/dBNzEhdT5pKFduD03WyhtvjVidl'
        b'JaToRj6Zmirq+uMcn5qiTiLNRVMiDZfEviWt3GPBeDKGVgylYTW1PM1xaxPiM/l6YFxvigyfMsnL24kzyfL60DK4afFBtfVlZgU6N8miaDSdRE0Gm2tstnNO2B6VR74J'
        b'TXOK1CprOr526pa+ieSSnEwmX2wGV9n4zcbXFrU6NT6JdYJedUzLSKW067QVSdNqO5tMBD7sjTemAfOhUxhRImPT0pKT4plTItXi2XwydLM3PnfmaGnfO7hV6f7s5Exe'
        b'lW5OdJd2cg6PjlDSzqC7tZOzn39YD/PQxSBuYJLS5RGiGfQeXrP1S30X8qPePEf1GqyZUQ12GDf/b4ZbRH3Swt8shGtURR08kCledi7yxE9FrnhtGZDCvcGwEKpj/VdS'
        b'xVWrtTqGzmMpzYOWpTQq/CLkCVrvKGiI4B5c5UTdKGPYMQfhoA47Zt78KA11nIZDeNm1s76LZaZM5SX67kTIY876NmPdsUhLz0CpO6K0qAjB7i6LAtyCojtrvZaehnov'
        b'R51p8O9DRPUarOK+Qfn+i7jyR8rWxv2hhk7RLGY6yAQaRavLDNpHPjQ/NwYHouO3WejMADPoubJSLkzzsqdYjHHcI+3oGneqWI6bo/XOugkHNZRxEU9KhWCGFuQeFE51'
        b'a56GCZZhrsXogXDOokOZ9cVsomaX4Sk7ognVRMEJ1UIo8NsOR4hOdoH8nCbve9ZthH1Q6xe3Egr9MpIWQg0cXrh2Zcbox6By3RpbAUt9HKFqhpS7jeUJQKPz0ywTAiSC'
        b'BNtFTzgFhzVUSIZcbFrLSvbYNmNlw4KBUOAL++PIjYaFykWiYdHP1IcsxgbznIiqtbDPADc8zZ3CKkl/5yqyzNW4H8q5e9Y2qNDQcYs1CTP1VgblIi12UJpGE4X70qxs'
        b'sCxK2+YGBghqc6Ado0MV0aHrQDbUmWVRBzBrMtJuYr4DXlqDLcyKAlWT4QiHb8ILpJOM4zfRp6M6dSm2Qp7VfKyEFs18WtyjcAJvBBsyHZXAxQVsmJKCBDOkEzKcDpio'
        b'g6DQjozwQjwQQcbdUQ0Uing7naR1Cpo11N0B9wbB7c5JDcJdJLWADh12UadEIVcB5fajaTjCWTjj0E9Kmja0D5yBeqjSUK0Cdw1cbIDNpKuXBE8mw2EsJ1ldnkH6aRfR'
        b'Vwu5Xx+UxZExEWEZMReLWalUcB32G9h9QgKVQe4eev4Sg8aipYJTqbRgVp2nDWm2ao0d7J/moKGsryvhxnwOTIHFCwN6TdotxiBxoylHBNlDO95O4qO5OM0TrsFlZk/S'
        b'WpOiMJt54DA0noFWUKdn1GFsOk7hOj4d3DWbUi7S36S7HpNN1CeJlmWXVR260Gfvq162rUOmh2UduPntx9a2Ez84++KI6vrl5iX1aTU3ozNMnqp5wuk5za+jf5bW9Zl4'
        b'/Xja6Kfuy55smew06IU7W1KP+cQvze/X77lGh9yL5n8ZFvHqE/tu+U90ifJvrPnL1omL1776w46Ex6/HLJnv4xC3+9SuouWv/Hp/5FsvpbzXOOaNyvt9B7tEjrK5HPdc'
        b'7fjTuYsHvvZu5meyD+riXqv4feSNeT/t/fnY2ncWXIp+9fjE5iMOaZviJm81vXKnbtj2oIEOC31++Vrz+oTqyqgHg8+vWtC69OM1r/U78M17kqlBf/nXiteHzlGUD3k+'
        b'OG3s0hU5H9fk1fhUp96fvtT83Zzrw1977S8bvoqouLkhL2nstvmP37V/C1abHm956+zwt6P/uvuVY2+/Mzl7VvjWI4N+Ova14yvHyuJm3f5scHn/HxWLv3uQvVH2b/Nf'
        b'Nt96//EZn7qlb0nzTKy3eCZz4E+qzSNT3K4crH/6h/tzH/fvG2aywzn4XI3DCwn/PN2/cvcz29WTNty6Uz3514rEjQ9S33i8piJ6yt5fxn7m+bLqnxY3xm0LUKfcnfHr'
        b'l8Vpd9+sjX0w+7VV94W/eTWclz+jdOAEDTvxcKzWuOSLOXrjUhQeY9ehaVtwp0gmKdYyq5X1dma0WuFHVs4mqOYBTdRqdY3zheApKezWj38KVZvKPCZn4hXuE9kKZxdw'
        b'IxEchet6SISGKE7IQqZuFtl8CrK0XCkGRCkTbJlZbAae9OygYxGGhXDEhEQ7Fv0PFzAPLhsGIOH5/lqzGJkUN7nf5jU8C4d0ZrutmVpHyTg8wGxVm0gS9Yy1CVrxhs4F'
        b'09+PZS+F+vEUKTcQLspIM8J5ebJkBFZBO7Nkkc3jLJ4l69aZYIY8QPEmNsUz89larNV0+DsWQ7veFmfbn6Pqlq5dnazpTvOhM8StgjxuFywPj9LxNdEweLxqTyPhx7qy'
        b'EiRNNyUX3eAc1nvLBJmbCNfxojVv3CN20MLZXLj1bgWe5wY8uI1XWdXlWDjT1cOdGkJhH+5kxlAikJSwGHvY+9ia4JBAKPBUroH8LlBLXnBV7pkCF1gRJ3gnsNFDthnY'
        b'FRBOhArruVIfbAjkvqRXnfvqGFugVmQhZxaYx64thvY1UOQZ6q6UCC5YI/eROMFOPK00e+QgZpv/GVe7OB2QZH5PJsQdwkwL0VLC4tQlliKNareVyKVmop2tNYsupxHr'
        b'lB3DgkWbUx4M+kmujUK3lQ6QDCDv9HcQi2m3JZ/sRTMTaxqVJmEGSom1aM9Sp/HncsnmEUZMa12Cq43YJXuykWUc6uzp+eiNbhg5fshI+LiRyPF91D44qieD5U7hB2dD'
        b'k+UjVNS4PxBFXWQGPe5iIiTK9Z5B0l7x7hOVsnsx3ZSFiIQUoqeqH2a1YyYCrVpCldJYtdOS0JBedA+Kx+jQTfdwD2PSFzab4dFgQ67ILrB3RYuduwWKDoMGsixdsuqH'
        b'5+E6282nzumn38xtsaoTO94yOMXp7G7EYhuRB/LwaodMQJaHfA3Hj2+fToWFTA+ysHpkkZcg6kY+aiW2BZtMDoYSJrortidQAj6yNnqRFIaSlSR0B0/89jQiGxocApIl'
        b'WXTGyk1MjRrtyMDplribx7g1rFVzLE35QmxgqJfUAesYXNlEkX7iGbgV7pygxgPSxyg9m6fgGQi72QHZJCJQlyrMpzpkUMS4c0TxGgznuSZziWx2rkqXULKkb5oEDSJm'
        b'W2MJu7QjYQk0wKFgum+EmQhyB4klNM3kqFsn4OrkSCyRsc2rSkaRKivsWFbLJ0IBQ6dj2HRJgwW8uDyKHRfiVTNH3bHYEI04C26tZy0wZDjsplEYuhAMaHARh+NBOMuy'
        b'CpB6MEQ8Hr0hw32izyQ4wBJMwrppVPUj4r8Q2kd0ySIiMdMYL08lOo7+bA4a4QDJLVfOOhxr5SmRUMLA58qjKVw7Rb0zCxfxMtE/c1irz0orFRzJzEnxjgnLcBvJESi/'
        b'VI4Q5pLuXm4TI2leYMu/nDubYUgOUCXHuJz0VgmdmJLlurFLN2HGlOxAZpiwVtgqqgSVmCsZKOzWcSZTqu7PKWo/DWCdrcoISUpJ0LEmy5LpH91hfKnMIddTJzPE0G1W'
        b'UMSck9mJppu5TsrFMleq6YgRk6aSjb4ACqZibpbvvMT0QDLuCjO2p0D2EGHrOFtoeiyJVWx6oiWN5dp4dkmM5dBBkby2bykdBDfSJXc9YxxzNyi4POxIFPParqCFy2Cf'
        b'YK+Whme5MaHaD446MQ2R6YdQE0xUxGyy99MBMw6bp5Jr6VZE7rGHs+nidMwewrI77caAZM2qXGJC3h7hrwWSPRoxQpHFQ3KIzppHUroKu1hKjlgtYAsZYkQ0G7MGj4o+'
        b'9tCsFDkiYRvRg86pw0yZWCdRiE7JcPtP91Yi6a2MIyLzJzwq6vmtM6pEo3jL5OWSQUfRapgNh2ZFFrbZSGg9KiXiFDiPDWxYz0/GCgVNAy9CaR+ij6Vm8al6KgFqsMXS'
        b'dz62mZLJdYDcsH4en1oleAXrFBRuslgQFgoLN1voot9aJymcMTfJxRWbQsg4D5IssyCaFPM/uIaVMxeNxhbPILxCrpnAbhEPrgGKr0/zW0PmQ7n+HL82ncyhs3Bbi+84'
        b'Z7y+Ey7DXtFzPBxNmvTuSzL1fFLvg6+1JEQHq+2j7W9dOf7js3d8wddplMQ7p8+wAX1M/J/Kz29wXrN1VJ+fzDZHVgzdvGTB6+sLg063HVz0064K/6Xlsx5/FnLXLTqo'
        b'6H9f/sbBhIUej/1a/YrP8Oyg6s/Vt779Up36nvr50E8SZp//7evgwszzizUOA9Y7ZkRU17284X2bNJtb8ZrMoLhD/7a/pRnkkq6MSZ4asO+ljX2Wet4zO2bz/Fkv83Gh'
        b'/dqHJFovuPhra/O0+zNdF5mfO7LWYn4/+37LnUYEnnetDqm0uHjk4ICWwIk2Hh+WLK34rejBmInLx7dGjdYMfvNenwrZoS98B/0wD/e0iW6Xo8fnzAhdokie/tp3bQtC'
        b'jy1vupdW/+GY19Tvrosc+dqiyVH1p5WNIyeovhzSWjrEpK3kSNvww8e/vF8Vfeefn/4SfPKXwYVh51aatFUv+1v9L89+te/qza9ibrq++vTmxUnBlZ9uPmfS/3fLr52T'
        b'Px3idr9g2YsNL71uH223dcnl23OuFLVOuBNy7YdVC4r/Gln5bkKt9yeRNi9djb72yuLXn6veKPteFvbxzJa8eUv2T7/5fYn3Lzcbt/3FK+mbQ61jn4v6Zu5t8d0XKmue'
        b'PZC4bEaCtX0f5d1/5eJP9s8d2pX1VOQn2SN21bbMVve9Mzt2qKzlZsxOn6iLfz0v/3L770HVb1zePa8hOmfTRofrr4YPWTMse8guH5c7d+5VTnlp/Ym9oo9lccVeLF1S'
        b'fcN7x3t9G8cWbVgz9muX159Ounpz9Oy9fnnLPvxZVv6MxcWPKjattW1IO+Tz3JYTH7S3vvrG1w3fBb20N6a0YfFrJern33zwdGH4jf1fj7nw4eAJHtufm7HbUpP544Jv'
        b'Vv4r2Wrbt273D00Y/8Kk51oOHzb/64+m8xVhLwfddQ2NCCyKrzzUNqTsmx3WT0/fMfTOxaovFN+FfbLyhQ+r44atnGD9kf/2XT5PzXw9K/fXJ+IKf116p2XjZz/+dP9f'
        b'NT9suPd20aEX31v5rePPP9emfONhGtPQaHPf5Wvlb5ssp6a888olj7DnilIq/u2+9McUq093mGcNmr79rfYRt/OSvt1QWtX+xm+RX3wb+Pve3dv6bXyl/eBvC6V/+fKd'
        b'tx2DzxxJtK741+lXfN/bd/9xn1e+jYv49+HVD5ac9H33978H1v/m5PHz94mV60vH+h+L/EvWjSr7WfcWNSb9a2NE4ZpXan556ciJFbrP47aY5l5bF1E48W+B35/eoYr4'
        b'1/c1Zi3pEc9bjvE/XNm8+K1ZR00X9r+z/MtV6raP/i7HFRNe6PePq//+ZkOyq80vHpO/hb/vvmmzfN+WpIi/r39/h+nzsm93WGfur31W+Viz+7+SB9/RPDnszUnPbHrx'
        b'w6VTx+4PS3ddF/LsU62bNN8f2pQ7+Pc5Fk+o39hWHOb01lNjK486fPr4z1kvKrfeasCXZ+14IXTS7h+P/uPHOZnizYHzLryOb+VmxA8rexDWf5Lr/H5fz9+b9735kefx'
        b'725DBtyZcX1icf+5vysPf7Dy38WpTh+1SB2HHt/5t/cKZt3397/87Nbl7397uV98hGZedMPvNjbLR35V4a1cxyLK3KF0oMLFKZUG2nSnVSEL+zmunpcQlbmVKLAFeLRT'
        b'rN+yGRyDLTvUlyt6Ejxu6KkxXYtL6GUvC8aSgLHBej8OGy/pasybypK3HJ/O4P8a7fVqNncaOT6DYXPYwHklu+EGHDKuq0au5CGH1XjbV8+NGTO2gxkTKzKYvjcFK/By'
        b'Py89VCGDKbTi3jcBkAPtarKDX8UzOtFXFKzwttR3BlxiKmnmwAQbqFF7kLzdM8KUVAZoYb46WCAVJuAFeeRyvMZqnAXteDUVm4N1lgn5KokL3IZsDhLZNiEoOAQO+bgQ'
        b'nX2FOBmveLHibYVmODd/C+kMTyJt0+LtlYxOHc5aiQjYRM13w0JoNIR0g3zYw3TplU4rFaRW+xLcydZUHCwVTPGyJFy1lvnmjIFD8eQqVMEVfhlbyLZkBflEZtiM+SyO'
        b'cTYR2y4zJFwKg7tGKsK58XIO33hmOFQoqIX2JnnaPZBkbSFZLOABjoBYiaehVu1C5J00RsG6l/RDQ5ipYAuN0syRmRy98KbdQjhhGcwAVmgM502JFHficdbyYTZkXLUE'
        b'Y3O4As45ywUix9Sb4xUKL1kK51jXzoDz0KCmwI/mpGtMiBqRb4GlEiyC45jLzQ03sAaO0EoWwB53cyU1G5NWsIJ2ad/ggaweC+fBFVfOiiojnV2Pp0TcjbfxEBvFc5L7'
        b'0t509VBaOLsQMbwJzskEuwGkmD6zWR3srEkreAyD3GBsU2IRaQVryXIl5HJE0GNYsEAdRpFyL+KJMQLULcR9rGCmUGqBLVQabGKpD4BbWGgi9HGQQuW6idy7qmj6tGBD'
        b'ZlGTlUOFwbBLBrU74Cy3dBWR0VOp9sCzSwKhwZLcJwjWcumstdDIGmganoEaRZB7SDpcCiDjU60UJy0XBkbJ5sOlRZwfYyfm4gHyPfl4yxSKiZQyeDZvl4V+wUpLzNMi'
        b'bpuQ6VcunQH12rDj60sh19Vj2fwuAIyO65kFKBXyx6kDydQXpFAOh4NFKImAi2yYD9wyg7KamwiiAi7OFKB95nyWYizejDc02l0M4zCmdaHcYJOPzeM5LCMFZVwD9SKc'
        b'ch7Jp3gl6ed2Q3sUnJ3NkBmP4iXuN3YGj45XOJMmSA9RUoQBuGyBRyRwA2rn8foUYXaWqwcUw0VlUKi7KJh7S+Aw1kE1D4jel6lUeGDjAqUL6TBSeLMkSdIoW9YJc2YM'
        b'cSWla8MGT49AjulsAyXSuEgs5Pa487a27sNI5ulhVOg7K+JxONSfPaoKHgwnoFChJBOEtYkJHhaxlTToYVaq4XABjnNTGrWjwVHcRW1ppM9YylsGq8jop/WVkuVzlgin'
        b'8QC2sQJbr5kRzI3zcgGu0EEgwbPrhrMhG4D7Q9WB5Nt9LsqMEIr8YOUpNfMdzayqMjgwgK0DRH8MhGYB6q1WsKeki6g0TOkhiNoMt4gO0iYOxtuTWEkCg/obeN2ps6g5'
        b'tc2LsTMvcPRXhwWk6dSAJRnaDoG8jcEeeMauM/or1MNxvrzchquBdAhlhHiKRAu08JXAOSjHo5kcQbxouZqSTbDJSUpTR40OtNj2ZNXFQ+SbcxzoqXZVuhpLlRZQ70a6'
        b'iKzfzSEinl4gDLSVuRCdqJGbM+un4iHNcJIYv0EwWSSSVetsMGsSu8XhwWSFvQKXtNbUQVDMmsQbWmA/HJpGz2uysIV0UR9xJd4MYU0S7qwg38NNsl3KBRGOCbjXBfew'
        b'7OKg0oSoAVjgTOYHHoPyZHKddHU7S1UCZVCqpuAQJ52DNrhIyFpxQDLVN4gN9QHQMIK60oZCXji1vRSwoWEjkapmYjsfyQehFrSQ6BQPHWvWUUh0uBnKFv35eB1vqNk2'
        b'RdZVvh5G9iHpXpB5W+AVNngkk6M3RpFF053pMCZwlAxZrLTic+0qnIrSLomsqci6ftACW8mQmDafz9TC+MV0vyXFuEauSxaJ7mQL4dsC0YpJ1UqCzbFgA/mylnxkefTF'
        b'A1I4vlXg5mOi4tRRjHUKsI4H3ci4NsUmtlzF4yGJeYbOOMssszdSGZKB19gohcbKnDTocNlccXYIHmF95zsNzqixmKjA9JDAXhw5kLQyXV0TKM4A26j34F4ip6RjsTvd'
        b'2M9JR0ORBW/Jq5A3niw4fcM7Y8+vWMjdVvPsFk9dyEDEPLEw1E0ZGErWai1O8pQZcjiF+/AiR2bLIRIEJaPGY1jGTNId9uiRmTSqXE4ZVZg8w87YekB+J3P/cjTWm3la'
        b'YB2bRkGemxTsRvf0QBc6d5QUy/eyFE57mvIdot0UCknGKjzasbZSmuxoJz7NmmD/EDIc+DQbhYct/CVwPl5r5ie7Yf1sepWu4wdJ4ctFKMVs5DRIUEWW51vqsJFblbp1'
        b'ZKLUPHo9m6GOcAN34UHBOBwuxcI1lfDTkiK8hKd1tQhT4knYz2rRJiULzu5wNmrxHJwZ6Oq8bKQx8HwvXzY2kofhbgXbAqV4BUoni1A3IYh1ZBpWQ50CC9fDTZ0cZCZI'
        b'Fu6AcjZgRw7GvQoPZZBIHrwMh/vSyXgUrvDSXYLy1bQFLILw+KpQOmDI0/aQIyVLfivZhpkVsGbaUoVSEMRB3lghYO6kWaztRzr7qsOwyZNIDsq54XSZtl0rhUIyrC5x'
        b'cGqoGYItbh4edBWoxMszyI6GhX3YqhkzapUiSGpGpoBEKQ6diGWsNKqpWKsmyzoWmGOhtioJpsIA3CebRnaFI2z6jCHLXz3uXqZwZ3WSD5X0xbrFfPJWJGA1WzbPQbZr'
        b'mLsLHdJk6h7EPGhmPW6ChyaoPeEsNrpgY4CSLj7tkoChUMl7vMkqg2yRtdjiHsZtGNtErBhmz8Zi/61ztZjGuGeNjrSdYRp7jmDtkUC6tlXtEaRRkulvQgZbm4VEQsSD'
        b'02STZbPkkqsPbWDIJmOnyC3QxpmubVZ4TTq1fzg/uauAk2T3NPDhngLXxHkhWmGVyG1n4GiwB0mgKJQs1ZvEGXPcuCCWsxErqc23PYEuSXGiNx5bwqqUCVc3ugYtCeqE'
        b'RuJGJlKf/xl8W/lDrnPsCR6fK89gln525GNGbWfGj3x2CC5mDFaY/jiIFqIdQ9igOBv2HExQQrE6+D1mDKPDjNxnL9pLBlGadImD6Gg6SBwhsRXtGWW6pWgtjpKMEgeR'
        b'T04mFIDYWmIvoe+jJL4yW3GoOEBmzcCNWdr0YEm0FQdJHcmrA/luqGSQxI6VwsFyAMmBHj25SY2la0ueGcCe50DHFhIHiQVZpgfJdBginLrdibyOISk4imPkZuLmgUZO'
        b'Ynhb9cTv+vBm7zgZqiZN7Ujth3SV7+FkaKfwiYPh2VDPJSJlSacnTxn0Rc0Nlpn8jVIZK2VdLmdsNrhoYuxixlZuAtVfIp/1uALkye2PcFlkl8nbRH4DzS1jp8iaLr1r'
        b'UbrdI+m4R3dZ5Fd6KbCcX9on0pjssDCSUTn9u4K+HGQtQb5l3yktu2CuZDwmsHD1yDkB/qH+kQxlhYWTc9CVBXqkFNp1GZTKkg8D+/8NLBTaAvqxk0KnKT1VTCTvZjKZ'
        b'TAvYLf1P3s2ktrZ07gqi/QyOlULnlJz8PXSHYM6AdF3jNMbOIaAOWiXCjGVyLJTgrU4gAxbad7VFd7CUsSpnlVJlWiVTmalcEgWVK/tsrnIjn93ZZwstoAr9bKPyVo1T'
        b'jWef+2hBVOhnO1Vflb2qX5W5HhTFQdXfABRlsgEoyoASU9UUPSiKo2qIHhRlqGpYjkBhUv4AKMqIErlqqh4SxSrRRDVSNcooGMpo1ZguYCjT7towRCDG9z03IS4p855n'
        b'NyQUg6v/AQzKFB62P+6ubE54hP9dqd84P7Y06BYGCn2SkUW/2EBfNpKXP5K0N8XL+GP3T/njICe6nFjAq3dnkBO21ty1iPAPDY/yZ1Ano7rgkETOnRuRkN45yJ4DnTzS'
        b'rR34JPoKD+gpVT10SOcSK807pUH7o3uiNl2byXhavWTe0xXvjFLaUP9dRJFudLTdiVRNODj3DCLqZauxTQtnCMWDRZdJeIYf/e1d66CgeGQUTY1oETewqh/eSorzL5Ko'
        b'qW7tXfo9ZXkPiL2T6PJBcKxF4mfCD7sGTlnw9ivC1HWy5j4DlCK3JBHVZ5+Bie0WnqUmtmrnHvhS9+rcXFgoWU8yD/1xonLD5gFdZuSfhCaxM6XIUb1t+fTnu04QJT1m'
        b'/Wj4JFRR+h/DJ6H0A8Plj4pPomKVoAAMNH7hvwlOoptVDwEn0c2kh94x5ZHBSTpPzp7ASXqasr2ghRidyMbv/wPgIF0j1XhQRWwKjYegAWc9hE/pHzOGJdsNUKRTP2tB'
        b'ROjuw4FByA7k0nOk08PQO3Ql+SP4HUmJ/wfd8f8f6A7djDOCXEH/PQqARudJ+4gAGkYn8P/BZ/xB+Az6r3vwkUlYFINxSMaSDd1RHCiCA5ZhScjC7XCWcyMbHOLcxjwF'
        b'nsFzqUlvxbXI1NSRMOnf/U2eaOq308nS/6V/75S8fbVI+uZHS14EWe2m+C3fTio+NjN3/BRl1KD5k5bm358y82/Xs6zCz/5zm8WN9e2zMrMt3wuVKE14xP6tidO1fsJy'
        b'vJXIMBNqNjCrP+ye268DNAHPQ45bB2oCHIEcfji4TwGVOndoqMLmjlNmLBjGDqsWJvhQSACbQK3RqAiLuKnqZJ8RBg7ecBx264APorbonF3/K2gBYx4mA83jqAFyY8LI'
        b'/xuwAAMeSbD6YmjvgtWjYgMkMmyAjDKxQ8QzggzgZ6pDBuiWkx4WYEQP+2V3KAClvHen5nhTbaFpwyp0M8yXSnimXWQ8BZXyEhVaGc+UyXhmRMYzZTKeGZPxTLebGcT5'
        b'bzMm4/Ue52+ovv7/Isi/M66aVnDSRr6vJ1sNDUH+v7j//4v7d/q/uP//i/t/eNy/W4/iVTJZ+w1J4P4QDEAvS8b/JgzA/1jwutSo/NiHB68TaazVmwWvQ6lEi682LF5D'
        b'0ZAgD0/ifu5AEjk+OQALwt0XaUODKfIU5V9bTCHKzFj0AZRBkTlch9OQq6EmIryyGE7oYtLhrMwAhk1CJLY2OM6cqEePwcOwM8QgGj4K6zX0sCACGtnJND/mNwBKGx+j'
        b'h0qjMGkSAQ7gcXNsh/JBGnpCgXmecK4j0hbzA9x4KAzmM+pZ6ja1aqwZXMXc2XAJ92o86EOlcB72BHeRnmnssBuWhnJXuIjp4QpTLFkLtZpZ5BE3rJuoZbN1C4xesNh9'
        b'0eIALIacWGVQaAiciwqASwGhHu6BoSQZTwk0K8ZBUUSkMBSqrJM9IIeDAVzyGdUHDzKGEkZPAjeWazzJhUGrHbukTcN508ZlRGD+UrjFI+tllNnBFCqmOmroqQw0ESn6'
        b'WKTuZm1fReE5KOcP6qu/PNEUziwzZW7zcjwGtYrh3hnWpCmlfUQfgdOGmPTDfUhdaVrxygY1jcq5LbpOgSYWlVDiZiLfK7UVBN8YS7OogUKS9PoLgvoOuZJ/ol/0Xh9r'
        b'8LLMra4JPHq/yVtt9vxLuQqvJZbncs5fjr9uK2/JODb0zPi4j8ymRIx+smzG7Z9/DazdNW6X8zM+4oWXm7bXrJpS8AG8YllTVeg19Kxlgv3kbBf3cN/UrfMrpXc2fzw9'
        b'LDPo8KstZnEzWuLL+uaMn1lzaLp69WHryOxfDy79ZtsPjzV6/Nx4rZ9f6u9HyldtbJj3ty0K9cd7bwyNWLl71WS/exUFXzSc+97zYt7kSS2jfLY2bvvs3OjZCeUp8ws9'
        b'21TOY4eo7oTHfLuqf3JgwJffKXlgqbla2gEUyDyioGl1MlZt5y63h1cs7MztFzSTMZBf78tOuX1wN1Fz9sNtfUisBqvZk/FQs8EgYFUBJ2EfC1m1jWf+FRnjiKJGZgAc'
        b'wvwuQG64B09xV5J8KPXTjxQTQYFVppRSWQqnmatNQiBcjZzKENS4stQE51ml+m1fZ+DYp8A8OE49+5b3ZSGnUlKS/QqXDm9jOIhHDT2Op/lpI0fxAFTzStC5WkCyscYb'
        b'Ult1CJ5ZzhwqxjnHkrHagAXcd4iyOsMpPM29kqqgBbLJqG0PHhdEF4AGsm4smsvdXC7jLdjpOj1db6MWSUuSxYS7qt2KNXENItPLJRrzg1gd+o6V4lG8AMe5V0Qx1GEz'
        b'VUUdoE4H3wdlAdxL6DY0mWojVomaeMBYyKpkQXc9S/FfDBcNepgOmcaCRqVmjJTYTC5nqHP2WlJjerZvK9qJ1hJrCb2+eVhXjcl4tKf5o0R7dmiaJj0fsJr2zAlsJKjT'
        b'/5HUzZtOhurmw6r0X47rXKOU3Vvx0LhOY1raHw7qpBDo3YM6R/KgzkS8OtZ4TOcZqOglrpMHdZKJekpDjzDGuOClDogGaCTbJNTFzfGRKoQReFGKOT7QzuOjKqW4hwZv'
        b'xlFkGW1gZzNJhdlzCsgecJWl0JykDdo0t2F7wHA3CSND85qUOilQMUDgiK253rY0LBP3QCMPzaSTrTWY73alZB0sx6MyLTWY53Co5pgup32j1emiBCvoTRSf8rqSZR9B'
        b'1tFWV6VL+koWmyliNhzHXezSHLwdx8IysX6DNjJzGRbxQl9wh3M0MhOvx9DgTCLmrMNCjpmSP3cIjcwkjXGeR2cKeHG0nOPvBEEhkVjgPJaxcErRBY/jbQ3z0cpZvo0G'
        b'TGqDJdfO0YVLksrdYq1RFcXCJQd4rQbvO7PieazgBLORNFxS8BqeMiBOHsK/PLiDkdx6eU0MWz5ym++fD5dc84cD8K6bdgTgUdiVBNg1S0vj4kYW0/TAUCx0w/2u3PEK'
        b'yxjtGvN9VAJlbauVjiNCTDBFIlIrSNPNwXybKOVGVi2PTCsaLOnslZU/7uy64byuTjv602BJW6+VIQmTTMcIjDxminx551BJvNBfI7JQSdg9QostFOxH4yGhxIKFRIrT'
        b'yTaxlyV5v68pDYi09ZJnz1jm70RqqtFuJZewVB0G9ViNddyt2Q32/C82rtSso3Hpxm9GpuJFGt4IbZYswlGcYj2BRyoWDjQnW8kK3E9jEASonOzGZ+Ju6nGMLZbYhnXW'
        b'uvDG4QtYVDOUBC0iKdFCLBQWQiVc5QGMBVudFc4ueA12dUQ3kl2VX/WDy9E8thGLh+vDG7HJLem0VaVMvY9U4/aYI5qoQHW/ybYHJ/xtywupyXfi4o8+99Wo4U96F2WP'
        b'GiW2qNRQNkXmKHEO2/fEjwPU382O9B9eZxm1/8iqx7P73s551vsp5VPKTx2nqD/68uDQhDkfv3j6/r0vhwZeCj//gYsm4+SDgy++/NfpzUElE4Jcxwb3+bfZrcvjZj0+'
        b'5WXvxpcDB0ZHnG4rdjWRv/QbPPvB5o+/tHs3LWIsSgYWhD6bub3RbkzuxMfy+yyv1TQfjv68pu7AwOhJyTih2vnopObnzBfOe9z9HwdL1iumtJ37/IlZdxstH2s48N29'
        b'zAPP9Dt87fYv869Me0GzF4+M33/bd+uZlLc/OfHd/mWfWDRFT2txL3xildVy6eAXfxk2f80l6S9v392Z5/XGd1/eU3qNnGHR4qEqXVBblP36yA2736r7ze/rMW86j5t0'
        b'1D3sh6uti6Z+HXf0zG2fT97M+lfOW+/vd9j8lI//ux9WnXV896/HvG7M8At7UFa144l2vHMjZtFmedPP/64qz33tQvuveYcrNles3Hblr3e+Cfzo2pMLF/897+vsbY/f'
        b'GfD1zp8v/rAtf3v+Z1Piyq/1b3vh2WX9Fv/j67wh303cXDL0O/X0xur5jtW+K0uiz39gPc7m3pJ/5E599akft/nmJVlt3vfb59N/2b/ybx8+E6s5ntly9Rsz9XGY+eOn'
        b'n0bVPXei5dgy95lNVp8FPzfD5e3o5Lc/UTur14S9tnB/n+t1z178qvrbV06p7lz/qtXn4uXTjfGNgV7PbKrt+13Y6ws/NWtYeNJ04cz/j7fvgIvq2P6/9+4ubWnSxA4o'
        b'ytJEEUGKXemgiNgVpInSF8QuKB0BKSoCKlKkKCBNBESTM2mmmy4vPSaaaHox5cX8p+wuYExekvf+v/gJMPfOnXpm5pw553vOc/k1N87H9Fk3fWbUctVhyzdpG/UW1E8+'
        b'IPll/A86tas+2fDtpOjTuneeN9A5Zenh9vbSxNsOL23J3R/Yb/F841Inw9Tur6pfsnkxLePXjJeecUyalfvAUzqz9dB79au+0g4w/yK2btWdD3+bl/Wpw3tGn1Y83Vpx'
        b'e93LSdUTiuJmFKfcuzF70tM/nZn4jvfkT9+qi3Qt+nZGfXjUuy93nHG84/Lib1GTio8WnVzX8tGUAdeoqOe/zPj129TSV784uGew6tuMAS7K6EZBys5MdDU6NmTGkxZX'
        b'zoSdCL32mP23ezuKdjheKb174+lpjbvb7+h8ULSxZ5xN/Vg//oLdp6te97499+X2N873fF5/94VM14QHznbx8ytMdn0QlSo8cH7ry5dfdtqc1Wxx+5eF7euMNtvvefLD'
        b'918a/P7FI2cPLnltQc1decypT87OzDwRrS0dHONsYZf93TnXz4/cudGmVvNlt+ntexNCdXd+OfHJbx3fcXEf2v1Eb+DXY2eYL8tKO/1DtKHjl0+su1G5X1J/46m7e+Jk'
        b'CZQDh/7FUEw4cFRo/SjIHzq2isHXUJ86cVhzAAZHwP3QaQllk91Q31riUa0AGh9yzew6l8oPGu5Ovnizp6+A2CArEH+ToI8x+OdgUJcC9cxQE8HqjUDq9e6iTPxSaNjA'
        b'YHpwPEiJ1AtYwcSTInV9uYqXsbRUwvRQzY6UGfh9mjsqVYD0ZD4ToAYfQQTLowTquUGmGnTZGjGOvgZ1ujI8kQHUKYB6q7Gcw0IqQmYIRePBRScVIA/1QAZrRxbxCWZr'
        b'Ba1wdgQkD+WgMoaLvABteLhRrt1aNDgSlQctOxh0rhX6idosVwnKW5ukguXh0T1HWxiOd/wGgstbjM5SaB4Pzeg0GmRwlkOQjo6QEjZB8TA2L5lTuOTWWSO39sayVJkK'
        b'nKcE5kGDEy0e1cLllQSXBxcMVdA8P2hlyq8cuAJYYPe1wPu7Ep7HoHnrvOkQJcXDGbl92hgVMk8By8v3Z0NQDR2JpHkMkCdHuUpMnvsK2gEtaIQcqb3vPKgagapDmYlU'
        b'KWePx1sewNvGsSOtaQc6z7R+teioOwXVhRL3hQyiogTVYVarkAmCF8eGE2MklA5ZKmFvh0iBd5DDeWmAnTZUQLkMdxvqeNQ2GXqZ9Xxz8naiAFUAb9CVOCX2ZhOcoEMr'
        b'oGtTR0L2djtjAmaQPWiAAkofMagGTsntGV4PDqF+BWYPnTSk8FtUuAUdl/rYQc96vyTCj6M8GUXucZPFYuhAdSG0mJRINOArY+A8SIcrSoDeAjhGG5uCySgHDwCD56FM'
        b'6FBC9NARDXpbEInaAHMxMudNDN7BQ1HcZPpmty0wPBpmQ+s5XsrBFRc9OrHbloX7+mGe7PiwOE9EeVvUTcdWBKcsKUYPcpwoTI+HWmjWpJPujccAvyqCfmhT4fQISO8A'
        b'VLHbjex41Ca1CoJCJUyPQfSSoI3qe931Jbg/Vuj4MD5vKeTSep195FI8103QPQKeNyeJFduNsqDbBs8GReeJ9ivxeRIFCPUY5EInged5blMB9AhKiBJElQhlMHje9PBh'
        b'gJ6rLa32gMcCCs7LhlMMoMeTzin8yXfvDZDby8bgxc7weTzUzXCjhY6BSlTi67cWnVUA9Cg4D8on0EKlaaiVAXIC4mwUmBrUOYFesSxFOfMIyk0b6gg8CdPrgUha25zA'
        b'SIrNq4tRwPP4CVAcT8tzSookN6vRUDYcHdYJ5TNYxBE4ZEEYWRGqZXwsXGUrcB7eAeqVV1GRC5TwvMgZDBlVB8ehSR4QhfIVyCEKG1oF6XQHC9m3lILz7G0YUGwUNG8+'
        b'qqCr9QCUQtlD0LxAVInzUWjeYRmdnR3QiE4qcHmaHkpkXvQSOhzQZoYHEuX7mcIAQ+Zx61j7cqEcGiksz4PMnQKZN4Ca6ZDsRIcmk5c+UKSE5kGlAjEN561J9OeZ+CRB'
        b'nQyfh3O4RLOroJN417iAG22FOiF3GJyHie4agwu146OrkOKF8Aoh16A9nu641abootgGriXS6lN90DHMR0NRwDAbjZr0GdC0AzLhLLlEQ82og12kQcYWWvhBvJjOSAPw'
        b'4HcryiYUqQWlAlzAw32OFdDvNR0XLrOFQUJ4WFYleMEM1re2JUtsrFbBgBIbSICBWrjjFCnZucdfjiX9RqgjR6OmEhzITXITQ4knXqSkCBnqWMqOJhEMqsCBy1LYvn4V'
        b'mhPIlK82U6IDGTLQDl2hE6YfgOkGn/B+XtEKYGBtMO1adCpQXKAh9FNo4ChYIORNYvCey4aBvnZ4Q6ukyEC8oCBjJa3YFl3cz0iN4PimoiYVlK96ASXnTU7u9H5/luVI'
        b'IF8KOkSxauus1zwKxhcIPUokX5AlrccIn/KH8SAtRl2KMcJ9QodEKejaeHYE9aI80hLM5mjiteFNTiGnJDyI4yBD7AmXdOmWdBCu4oON5IJ0PRntqTqqFhZJFbvOks2r'
        b'cXsUV6bQrK+A7LmGslHuQ8fILudvtEl1FUvuYaEa2uko74AGLVRg52Nup7wF3bOPfrlzG9TIcX1Y2s4KxIRUbIM3Wf3don3Qmsb2yiZ0GY7bYOqLRaWYESNXD+iksJes'
        b'RsqiFaLmCDnmzYwxg5FHrmwJh8JzY4xF+xdtTiHahDWo3/0PcIzo9J5hCCCFMTrPpu1agCocCADQAfoYBlCF/4uRM5brUjA6KvdWgyYFHpiigfFAXFQEhka90CD3tjZF'
        b'JQxyzkOhUzLjhS6uX89gxAHjUbEC64xXThVzJ9gT4TcaodhKwlqPQCmi4hmMa+qjHq5I3gyoZ4BLFdiSn0GPbmN0FI7Y4FO9f/IjYIpYbj5FN2sfaBRLca5c1M3Aijw0'
        b'aWsoIKcHp0lRvp0pZu+GgYoEYktXwIQZ5vic248OM6wi3phQ93I6MymY3czB+w70TJJp+YzGKe6wYzj02jAok8o4uADlHD8eM6qAc9F5j0PFOwhU0SKaghVVUMUQPMB0'
        b'4zibuocgFbehwwysSJCKmSibkpsJ1M2X+vhDDTQwtCJUu9Dh2Iw30sbRcEWUDdm4XRSwmKTYsQzw7ltMwIoakKPEKxbDebbhVo0PIieJDd7hckfiFduw0EBaFgSDO+Uz'
        b'rafBtRFwRdSqSUuOR8eCGVQRVToo0Yo6EXQ+V6DOOAJXtEPN9gF+o+CK6CgqobXvgi5Il9sT5K4StMgQiychjzJZCdC5UuHsg6AV+9eqAItwWJuN3KVVmPeigEV+BYMs'
        b'8suXQwUduc2oP87X3h+6dRlYETVisqRkgLl2J3I1BocOjIAlBkCuTPf/HodIUVVUkSD8GQiR/RunhCLqi/4IhKihAiEa4H9GNNCNPk4TAOJ/AB+KNBRAQTEFBppqPAxD'
        b'NKDAQyOag/ip1Bab8ia8WFj+X8EPTUfDD00e1hb8b7GHueoKxMefKjDSuZ9HIRD/oFEyIbmW6Ejqfo88HP3mrzwaCSQUMTwgQfgkN/7+W6c/LPWP3qixv7tU+EDy45FI'
        b'wOTTJONfBQEa/l/i/87guj8g2FESf+2f4v80RPpqCrzfdCXezwCnTBemkvsaaSQ0DF+lY7FNcZvOc1ZwTRKHDsOxUSa9uorf8kO/Q/qtF5erl2uWG0YJ5Ge5ruJvI8Vv'
        b'LfY7RhQlihAVChHWKm0XCVKknaOTo5ujT8ONa0eIIyQUYSeJVItQi1DP5CI0IjQLhfXqOK1F01Ka1sBpbZrWoWlNnNalaT2a1sJpfZoeQ9NSnDagaUOa1sZpI5o2pmkd'
        b'nDah6bE0rYvTpjQ9jqb1cHo8TU+gaX2cnkjTk2h6DE5PpukpNG2A02Y0bU7ThjhtQdNTadooRxLFkyDtmRrrjenf0yNm4L9NqBGniGoCNXKkeGz08NiMoWNjFSHDOcZG'
        b'CBSWYzOkvWSRf/BShUrvg0vCQwacxIJqZA4GMVTZ/6QkkEgdcpbHabYt++1I41qQv+aMKkypOZTbmy0aYZqosLSjEAeFPR9+mxKZTMNuJOwkIYpTRpsWjgzBYWsWGRa+'
        b'zSw5MjE5Uh4ZP6KIEbaPxFx2VAl/ZFw0Wn85KhGQQGzKvKPMaGxeuVlaZHKkmTx1a1wMtZKKiR+BHKFmW/h1GP4/ZVty5OjK4yJTtiVEUGN63OaE2J2RVNOaSnbJ2N3E'
        b'/GtUjBGzZTHUkspqkUxhBBw72r6MmGEpLBTZRMxUzINyxG3NrBbLlNnCzOSRxFIuJfLPJonModUSGYGbhI2wRlTYASYkx0THxIfFEtyDAmSOh4BgOh7qqFweFk0RL5Es'
        b'lgrOxXpvFhGZiI8FuVkCazg1KbRSvFtMKCwuQT7asiw8IS6OGDtT2nvIfDFAJgyJdsXFDqmFh8WlOM0JFym2Goli26EqMOJmVYFfU89RRjiT0u2DxxuIEKWrUJuLctUO'
        b'c/vFe9T2iajaXEzV5qID4mG1+Qc/838B0TZq8fyx4dof2TLiHjEzxrX+fgo7PBrMhpY7PFd4VqitKl6KjzZwtYpkJPRH6/RPkFZ0OF0JYCY8DK/0UNykUGZPyApTFTKS'
        b'3P4gxFBYREQMsz5V1DuK3AhhJqVGKpasPBWvJdWW8WiEySgbXRY5iKy4sNSUhLiwlJhwSqBxkcnRI+IC/QFWJRmvxMSE+Agywmwd/3mcH9W5pqMgstFmDTYBcsKWT/n6'
        b'YNeN+zaylhTZddmlAtkbnRlyLma/hstQw/e935LPqeEbakf1qAQLQSWol1xHpmBBRUa88MjQcegE9g0cRk3QAOdQI2WIg5l1wQDU+8B5CbnFakdd3AEZtFKN8cE4gTNN'
        b'IX+F+r0u38Up1Klem6ALf+2GJRzOzQ6aaV7RQjGXkmZADNtsfw7hmVHDVhFUozJH//kODqjc0UHgJPP4FUGojR787oFr5ChfF+WlMT2GX4C9prUVz81G5Wrj4IwNdByg'
        b'zVuFBe8WqbUblOKXgj/vjCqNqKUknIPuwJFFjEWXtMhvnrNwlVjAOVeq4LZEA6hOyp6LUD+PBhZBs8+SVFs6aBaoZFQrvK2J154OG29fezVUSnQpIahCYyIMWDKtcS1k'
        b'okuoi7wfKyavNZyE+LHQIxOlUtn+CGpaR2Ko2KGSxdDh6OAkcNr7hR17nVPpbUcl6kxRvDaBGvxajdM+IMTiImtS6Z3FVXR1qyIDbncPzsFz2geFuF1WqQTpsQvVhrLw'
        b'LF7BXiRUy1V0zG6l17DVC88t1VMfi6XxVupfOQCOaDOhFQt6+SvtcEVElDaEIhGcMZ+WSqI0jo8ingmH7WaUAW5Qnp+vr52Q5AHtWB4/NRENQr4x6kSdvkaQ7yvVQp1Y'
        b'kgxaxUVG6TvDMXQmlXCzKCME9T6iNGIROtNntRXK80JHVsGJaPyg2Hc1uqiiVWqeE+gtMbDUwsJ8g0SC+pZZQrOMW5ZmhE5BOgwye4XLJGBOl15iMqYGdJmHTu/pLlCn'
        b'sF+B7qVSDeJlAMs30ICyrdHh3fSzWGKt06WdRL+6wKNK6JgGOYnU4GAd8cwpTwwg98IibT4U5YS6u7LpPAT5UCVPQp3a5Lt0HmWhxmnoDKqihRodgCY5ukQLhSu8Prpm'
        b'guqhlU11E2pG5YqphDMLVTM5Ew6lulFSgSI4OTLejr+dT+BqL/YFzq4YOkjHaxKdiZWiHvxBE86cnmpHKriyGrp+9/kKuxD2WZweh0q5CHRZg4PSfbE//vbbb3GzJdw2'
        b'S0OyRmPddJZjgYUaPAnTnP9wIdqiehsSy4JtFCd2E9XqXqhUrsRDTrgMquepSPIYWYg/Khq5FA9BHx2wCVJ0aORSrMQ01bx5ES6E9qgXDkPpHy3HWahLtRxR3Tq6wdjE'
        b'ony2GFHGcuVqNIcjtLsOm8Sc+w4Tamu7+4AGFvIokewPwZvSMP2gcjg03dWbmVN1oNqoYfqpNbOODqEvxgSLRxDP7JnT5Og0raPKRczdCxtLh9TTw42jDys0xJzp3jG0'
        b'4jMrnDhF1GeomI5OjCAXdBFVmqiF0EZZo/apI2qAfHR4mr4mLW1OmoS7E0JNhmObkidyMd8fMxbLC/EOHOQZF1c2EG+4yCj79iffD22ekOzokvm2Yc4GDecZj6tZlOdb'
        b'GxjEL4xZzhc1PLN5YO3Zk9mLtr2y9BfOyF0iqX2fb2pq0i9eeLLUsaxQ80TUvhcPPnC8XXWyRyf2ZjL60HuD2KI54lLsj4t2X/tQbv9kUvzKE/PQnJVPHN/ZbPFY+nOP'
        b'rTjZPubI4iNR29umx2qKbz3vPdHrFc2P1mx+4bnasyXnxckhL17fPe+boh2V7iuNFi+5dL0rJ/BkVKVN0bXFt9Uky8oXXn3t/lhjx+7fvGf13vf2N5wyrz8057tX5o4r'
        b'v9V0tn1SZP231nqRTaFPjzPeNdQ1f8L1zpVN9d1upyPDr86Nl77lxBsvmXV+674XBy4VbUr2+7hF/M6Le+ffvfDB1bJ3e9J8+o76V43fPjZsfNSVL7/Si3vjl0+yh9xt'
        b'd0UmNdn+tG/dJ0mtM/K0vrra7xp8tqpe2nL0hd+KVs4de87VveHrlx7Pn5jmXHqh5heDH/zv1v4494XzFhufSrNJEe8petnxA3fZ55N6vi4UZ7jueTnhjmtYRG/RsZfi'
        b'aoXqg5KEOxV3rTcezv9l7opN3392aE273us9t+I+GcwoC98UZHlZs/f9ua4mboue/fAtg9e+WPhka2fI1KvtGTdd90x30/aY4rFyiX2c63G103FOkb9OcekQT7iYNyP6'
        b'nYT57/74QteSoDcK/rW0P6GtZKLuF0P6645PKjib/QCt8pw8ueu3b+YEfv3VjyW3Y541funVpad7yu8PNO7adf/JLe47nkF7bT+KuZqy47n84Cfq3jqol5/87Iq3f/n1'
        b'/atX7rwLaiFr7y37/LDxV48dFXVs+X77tjqPT6x/nRni3qhucfOS8NKrr5Q0WM8O9rQe/4XsZ/H96p2rqvufbnnityUWweubYnsm3lzj+UOF0bv/Fnpu6Zv0R8oWMY1N'
        b'M9Rr2dhDFrrkL2Ayb+J9oQLa6C2lPWpFmCGBdksoJOcB0UrlC5wUrmCaX2tBL4XH2EKJjTfe5rL81PHnubwHagijl4/+fqhklFfj3SjLDp31YHeMR1yhAwpmMptntVAB'
        b'75plFnjzrKetSnEhOgYSlI1YNB8QJKjeOghKUxzoHo9qoBJ/S/TrfvaQF0g9+ELuTC9bawIOhgzU7qvObcHsU+tUhUIa8BFgqDAAKZOM9PjcrPTC2TEVHSZXqajQTo1T'
        b'2yzgk7NnKpznaGeWzNrjGzgReuy8bYl+QArdArpiD8wP4jh89ndSb9OLUcEo4xPLZFZ7CT+BAXahfP8o+/YgaGQ6hk40GCmfSdzeQSVqVt4lQ4YOa9y5lVA70u/dPmhE'
        b'x9DFvfRuPQB1WuA5aMW7vDia18ZDmQ3Nq6lqKyYaXSAKEeoZj90zQ2scz41H1eIkyDWiN8F4w29lXldXxVO9bhTUMWuAY4noEB5pH39fO6KKVTcIUFxVT0PHJG4y1Mr0'
        b'Tid0CVdW6E1mxFc3wA51Q7Orr8BNXi7G3OtFL8Vt+lZXYh9RrBkwDdXgPDiDzjIB9TmhCqoIg+NwGl3F1QXY2WJWxJfWhXK0cXVms8SoATKA+e5GVcm75fbmkDvqXhwd'
        b'nkXVCePhMlyEgkACcTmx39bbn+d0t4lc0CDqYaTX5TmDsVgE9sL0HDpOIvX1S2jh01xSqAaJhLpU59Q0BWKKr22ILtOhckbZW+TU26RoB6+3bx/m1TuYFmjQBtPesIda'
        b'Ptl/QqTCcSGZkYwRLlf5DVAGp511mT1LOqrDzBLRS1IPthJUyWOmvw/1o6MJdHodUqBBau9LdR8tPBzShzNQIWVq0xzv8SpPtAfUH1J2p6BuprqsdN4gR527UY7KGezi'
        b'abTVi9Flu5H+Y+ej+s1w2oPtDI0riSKQRvESoSp+Fm500b5kNoYkCsgl0qViG9KsLh7loJPQ6LaVVmiF8qco3CzD2aXEggOqFAqxfE9TpTt0Ys/QL+iiDt4ZWul3GphY'
        b'++UBOHuF0mOvwUrmgvMo7nQ3mdVhfIoBtInmuKECTxhgSrJBMsoUokI0lzlwgehaoVKAPDyf+czaLMMKLo7EexD8fOYclbUZj9cjaWdSOF7TXTYK98Y9PBzH3FybDZ5Q'
        b'amVViGW3a+x9incE4YbVON0I0bIU6xTKGHVD00YoSNuJunWShnlr4gVgJiry8rdDl8fiL1Yt09BNsKeDHY4u6spttDAf5Y7aZTynvl+YMxV66PxPnuQjt0mWaW7BexUm'
        b'dvVIYTZkRjGNfxEqGoN77I23rTJPKAyk4S8lnDFqEY+B4yFssg5BqZ4UFy3TxJJBDS0DWgQP77n0dawV1LAi3PDKKcRUqs7pBogWOmvSOdlvB31yLG5GEWMzHvXy+uEo'
        b'j6n0GqBrHvU8imfmDFHpocN4+CgzXY6yMe+k9D+qUOm5HIT8qCCmmSrGU5zNnJP3QDG1pMLyUyY1sYqfsUSOSfrQZoXX3Kkol+pL8Y53KhY3Fa8Tb7w+8f6AGWw8tzO9'
        b'UKGIm4rOSZyT1WifAja6ywNkChs7X57TnySaDX14D91JK7BGLaup13HtBHSVKFcH9zLqLEQXoUHONhURZPFwDfL2wLGZzBznpKGNjY+dr10KyrQOwNuKXrQoDI5i6qNQ'
        b'myqomzaqcYstCFgqj5g6yDZL8Pts1J+Ch4vzTZUpiAPSpzxEH4FzsdjhBm1qAahiE1tMrh7D7qv4tCX4lLqwnpLheji9WUpeKY+UMahftHE3tMYG0PcCaoE8G3ruoHSo'
        b'xceaBhoQoCQK8umC8V8G55nT1KmobbQWkngfl+n899qJ/5HC8FG+Kbrxj/+gDjzIRWrx+gJBEanxE3ltgiYSqI6DII2oik2NqtrUBA36ly7OpctP5qfzVryBoE+faeBn'
        b'RB+ij9+Mx09MeBOBIJJMcJqoFCfj0tSojmTUE57806VfEgwTK4koBfcYj7wgfNhNhoSp4/qJFmlgNEZJ+7+aCRErbrh01Wh6E3t+gg39Dxq/dK5v+kid36P78R9dZGz7'
        b'Sy4yWjWULjJGV6PyjzFLqaegF/22ZpHR9mbW5ObS3sHJUekI6FHuMv5jA6NZA1f/eQMvKhv48wTSEsW1t1lMxKg6/2JlQxpbwpku5E9q7FLVaE5R7hTaHWVGPyS+Gv5W'
        b'vcxRyZDOFtU9/5aYP6v8kqry6YvMUuNjklIjH+HQ4e+0gNHBkPYW5Q3wnzegT9UAa9J7eQruPr1FVl0g/5NGKPy1fMD96VxfUdVtvyqBuJ6Kj0qgLjHMwrYmpKaM8mT1'
        b'9+rPZPW7/3n910bT2gjPSv+kswv+vDJQVTZ+uLLF3kv+yewmL/rzup5U1WVD6ooPG/YMpvSmwtxJ/KNRjfjzyp9RVW4V/Ai/WcoG/JNlpUW9UWwhviH+pAHPjZ5W6lKC'
        b'Let/0Fu8hdA6UxL+pMYXVTWOUzgf+Qf1RSu3jq1hsUS1tSUhMTL+Tyq9oarUhVRKcjONS+xIVe3Dvmr+UZt0VW0Kj02QR/5Jo14b3SiS/R83ahQs9286S4162Fkqzz2s'
        b'VxIFxAQPxUnkhBms+wQRr6caUe/7iThduUYu31N5ScZTpns3lpuOK8UfLPqMh2aF9NO06w+cneopbauI/P0fmamDXPQeo4cO/djI+C1b/rqrU1Lhm2ToyU3Of+Q30rnz'
        b'oxyePrLy/8k0bPvP0yAOCI6p3RkskZPH+WM0fcO08SzkzVDnxFa87E2DYSr7/Tif4f7eOG//HXO1NSEh9u8MNKlx6G8MdJP2n7F2rHbVSJNWEAU7ETKYgn3YRazSqRhT'
        b'svM5OioFu5ArwXMgwnMg0DkQ0TkQDogetRSI6lIb/+84ag6mBKSyuGBnIHNYy7PaiZ+2ehNVa/57lpg4gVkx6Btq+1XkZBZ+Ey5iwTRDrpusSbLX7lrK28PZ8dSVCLqA'
        b'qubRsA81kGXDPDuQa6EjvviPAOIgJWhFkF2IwG1eqA5noUSNqkLno35LXx+iyYEi1eUYFvOsw6ETLkngvIsXrdgTsuG0SlGFOlL5UGuUSdVN/upQonL6Qk3C4SjKF+DY'
        b'KmhmmsVBKDYgVzv0Hkpsh65BIQ+tqA4qadmhqC5eGcoXLhEcUQak61LFRcw+qLPx0d2KRVXrACK2Y0E1UjAMZtjbI75zqUxo5y3mNNUDUIkARXYoiynkri6BdmbVLRZD'
        b'JzrMw5kUY6bHOy3bRe44ZViM1JyHLvgJ0ICq7ehncw7iIVaGaYOKtQQOViplCtgsOIlaUIFdABUu1VDBtE2CMRTqpRKheZUFGvBFRd7Eq6MfKqAjzlxT2HigNqiQoEIj'
        b'dG4U3UmVdLd0mO5GUx2vcmCnpDgtRnFrMBH9jupGrXwarPV3VOcQQGnLf4OEvDRzMDk81WvcYkWE2jNRUQRxgS64KHFMO9EgcxGQp4muEevvVFSntAuHHjjBNJXFYVvH'
        b'oQx6nzA8SZgKzzOSPQQZY8lFIxxCWfSycd801EtB1dC/GB2XEzt0LLQGoKpJQSb0k1lY2i/zpdd1wmYe1UlnouOoiFaGBqFoAfNwhOohSwnEQSUbGUmUrYXjLLoZHDdW'
        b'IKfGQSn7Nn/G+pHBzbT1cZM6RMZhftQkgarbDkA2pr48VEyOZXPOHLWiEzIJI+NSOLTioe+PQoXIWG8ObXXqXlTBYozNgIsKFJPhSlqzKxyNQOcSVeApJXTK1IYNb76L'
        b'pY19ONSNDJlWgfqoHwOrsXDEBldpj1eIPRq0lNn5+POcBWRJ5hnPpaW7QC9UqaKUSX1QM1QLqBEdW0fJ3YffpYgKhIlWQzCCirEoHcppuANvYdzDgYUgF68Gldk+VEML'
        b'zYlOwrV5FNrhR6+UyYYC+agTddDVMH2NZAfnSjeivXhUCY4mLzAACuDSHwZhCoAMdXQUevWYirIS7wjpdIfBxXYzdfj03cyVw4AWgbwdwZN/fnQIKV3UygwyOtLm/H4b'
        b'G4M6yE6GdzHj5aySJkdXxUaEynTJXoT3Ia9ldCc2nA/dJFiWz14FKAbVoQo6PcugFi4TIIg/9Jsq/eH0QTp96eCFaob3hE0CXEHNxqh8MSWJNaT7dDvxR3UKdGmsPqV9'
        b'r9kkgpCfr8BzvAuHilBLGG3GDrisYeNvJwuQC5w4jGyFjaiZ7T/Hx7lh+kpAVV52thQ1fFzYh0k1J9WMHGKxUK4MVgaFGtA3CjJRmcCWR5do/HBEM+3ofahepIf6l1Jl'
        b'fJTPpEdtYImYxPEehvcvdHQZ7RWPGjZCAercKcZ/NnE7J6JGaPZhe0h5sJ8cdUBmmhq55OTInSIqZir8BtQA50QGqAy/suWII9lOuhnlj9PicAYNh+n1MQZTdjMvFFmh'
        b'Ck8lUSWuBWkm7OHiTQp/FXMfX5S8QIs9vL5bg9Mnvjmi6k1n77Ib7ZuDcirkf9L7fdwm3f38Pj5RO4ILwVtnkhChZLgZN6KIW87vfIjN/lnTPToyPnJXYvL8SE2Fxwgx'
        b'l7qekiaUBshVt+PQDCXsBhSVMMe5tt52kI//ODHaMUeZCHVBmYEvlDrqb52LV2zzbmg2lizbyUHFSmPUpTcxdSEZtMuocAKxssBrrszO3psClTAX4LNyhV2I1yNmC7oE'
        b'LZ7DpNWiHQonY+ni2Iy34Ct4e5bZoXxMTb0jlEITV4vhwjYbpu1foDgUQkST/f0iie0AIbsDKHPOiNmGy9CD95ZBdImtqBp0CKrIlF/yUk456l0W82HBTUH+Dh6oyM+7'
        b'I4OppcCpk+/0pA0e2Pt5xKkZeWUuL4o0ApfZ/8p7edXn15ha3nDKn9jY8bJf5tr8uIUbVjScq1m8z1NL62p6vvWWdKvL8jdnacqu7H2x7/b8T158Ns+x86ONxZY/PEh4'
        b'YeuEtU/M+e5A8aa+m2PRJaP1Xr4bnrafL5ntO+v9oZCNQ+Zun5sbIsdIG/NTMpPZFx9Ti05MWXL9/ZduFCV/aBvxy1MJMvOKgPN9d54/+urhiZ8ceBD47eOPx9+0H3j9'
        b'418+t7+TsmrG9t1WNXeTn9cy+n76jdoXm7TLvV5IvWn+6s0bc60/nvyvhJg1fe9P23dx2v6mpbYfoIWRZ7e/liu/NePxyQUnr+uMi3r9YoCakBgx+bPc8eW/+vyc26hx'
        b'7fiDjNxd6+O+Wj772LEsvXN7bzw/zdfnZe9t21P29Z1r6Doxo2uDg8e8hMjquHeeeZDq79t1/k64/mLDKIcH6l8f+aH8RG6Y7+6Kw19WTKh3XyddN22rs8NtqVVCyO1g'
        b'3U+OJFws2O4xp8P1yU+892dfWbRd9PpE2xVvyqAgs1HzPfP74745+rZ5s2/9gcXvTuvx/mz2xy/ox485bXll8a6i/nYY//EDs7fPPeO+7I2eg9u225l9e1Y04WLee2Gb'
        b'PzbcUeHo+sW5lm8+Wf78qaKQ6z1Z9997Lct7Ym/ax1628rt1Jj9fur66+nK+88aBH+N2xdh++JGm6dtZl+ybDV7YofNu7VWv6E33Oo1m/PDVhKe+/GBN9+sv6U+d9MVz'
        b'H+fe/Wbb/J3B8z7sfP1peyRdnd3y3dMe176Ytfq4zZ138/wadGcX3Xs89bireHDgk+sDsRvlPTODprg/cTD92R83f/5qUUt9muuncftuZ59c/1t50v3u9366/MuLma1Z'
        b'fj8/tftn+8g1HW+VxfU9mNz4aZjT0Nj4W5fHRL9fcq/+F6/7+uvevrfyTksLhA/VeVw2O3K/bUfu6ffdVjjd+2aVZO2vQa8HJ5o5HBQFmm29y909eKu/raLl2r6Wz2aa'
        b'Rs/4YnLZvXnfFj0QjHbPvVV5XzaPqaXOptDwojOhCZ2BK2K60V/BW3MhlWY9oEdNSlCMmlaYFcdM5xhoFG0LhuqDkMP0k+k2qVJrdCpChs9TClabIISkuFMFj+aKLajL'
        b'bz7xE00V2ih3DFU7OXuhY0xJixfzSSVWOc+CuR1oMvOnanRcXilVpaNszCQ005dzMT9eyHS46Gq8Epm7dSvT3p+GXm3GX21Fp1Ts1VnEAuXKvKAa5UEG7U6S30yZGqeD'
        b'joimo2Y1pvg+i0/xWjnxHqejCCr6UEDRwmVU42YFFWuIupZpcfExh7eu2vH01VaUCzUjVbla4ZvVnRjOugD/65PSeHZCMD9/1XxDaGFQ5GnoKtHTonTUIGFQe3xmX2Dq'
        b'+strdYZj1mqhSlQNtSRm7XEoYSq8aztIQD3M1MGFOUqQeQoqYVjOKwdRg9yPTA3eYX0lnJb2fGOBhJs1pc09gHIF6iABy+lqcEFAl/UdRRxVs+2Dq1swo9QKp0YGlUal'
        b'ixnVZCePGx2xFoqDUM8kVM00sw2Yw24YEe4WqqAfk1cbHGczlQkli3GHid+JI2bQj9mLeTx0zEEn6YB4RqFqqb0V6hkZaXe9I9OVQ2u4HOX7hnt7o15fgVNPEqxXYCJm'
        b'FglpcIaMMFRbD8OqF0AbG8pidJwAt4/YJTFVsdaaA1oC9EMfOsJalQXtYVJoTqRhQCVQyW/BB3879Imo0QE+OU7tlNN3ghGPji2fqi6hTXLbS2Lr+ttAF2SqYQmjn4eS'
        b'lZBNMZmekOlLBAhNe3Qay3T2WkQ6M4UesTNmvWqYr4+LEybK/dCJORQkqYJcG2EmG/MbUESVhGPCdOSocDI65vsIbPRVBfS6QB+3sQszOxdCfUdAijEfPMhopQ+uwamR'
        b'BizGe9GxqDD6tddUI+haPsLliMrhiJMGzRBAvDKOCPqqhXo84CRZu7iNhMJdUZszib+agDJICFZ+EZSiZjoxjhPQSYqYJ9YmkmVYLEKHUGE4qmIa7Cp0QY9E7YwNUkJh'
        b'd8IlOubBPDotx/ypB6/w8+GF6yJjnozZgUtShVJbzURY5maBF8WAIiI2KnLBq1yK+keG+sRyWB5tp8j+AAn1CR2pSgStExymsxXmRLxh4NZly36HoJ0+gfl0OIm3mUNS'
        b'HxaVE6qjJyPMJTIzkGKUOV2BdcWSyHFVeE6GdXXfw0xU2pKhazguJxavDPGsnKATFBgsyMmigHpdTIZ47aj7CubbUS6teTOq8qahQtfGKvG3cGkOm9h0qICuUWZe2pp2'
        b'e1NZDPFazALhdWobgHdwzNTxnBTOu6UKWLI/j7dVGhzVL56+PyJDudQ1aJurRMDDcFgRZSEdc079RAIkkYnP8jxqWbF+nsIfSniKTaAtbjQRTdQ5KboK+XoCZtQGoYYe'
        b'AiZoYDE+IIpExPYVTnBzAncxi5sCvBxLNqPzbMRGmAAtwLNBF0YRDIYRw7fRVm9YxKoR0AWtIJnJ/2dU3//eH+eQFoFXbaEwB8rfP0u4/f98E3mQM2K4WTHF0ZKfuvx0'
        b'qjS35a35yVSJTlCqBE0r8EztzVCrgpq2YMWb8FaCAa/LmwpUda4IE8p+awvjKcCQqOFJnvH4r/G8vkAChDJ0rT4/UTSeqtG1cD4zfiL+R0rSp6VRrK9Abi73yB5WRpPe'
        b'brF3p+or+Xz74d4zqUU8pJmyKyIyJSwmVj6kviVl19YweeSIK9V/EEADS0JvEsX6Gyrt+uv4LxGRfQh49C9cwqZzvzHHoFr0Z6ofRyNqF2rJH7Ik+utyErnhHJyLTurZ'
        b'ToZqGfN4nAgtKM/Xhzl7liTg9TAoiEKgmd5t4lRHCn4Jh+EQNascoU+oE+Nqy5fRfDy0Q5OiFShjHmlIoKLIKW5iVK4LJ5V21NfQJXRFVV+SKanOO4FKWctQy0xSWSk0'
        b'PaqyJdBLYRRQHLHEBhVC8R5fzJ95+dt7+69MJGOy0kvhOIPnQo01pkHrQSp+oYHt0OYbsNZCaZvPTPl9p6da4beWcA6fB6jQDh/YwbQYPIADs5xWeina6DpNDZ/JPtTI'
        b'3QROOhO/S3irbFYGn2FVW424+d0IlRp6M1fTPoXtwEPDBibF8nfjggetmF09X4GrqEX+UFGrFd6sSbcI8xN1EApSNKAWXVtJ5U0vBypvmkb6hmqnc6u5mFcAOHknXtJw'
        b'zyVylUfCqwtND3y5LyD26Z+2v9od8Nyanx5o5Y5JvZerb2BQom/+nAxJJG9+evSDK6GZLwTtDm+uWOEZlV2kfeonnV81c/lZX709T2RQ8OvPu0/f77s96HZi602byvwf'
        b'mo3CZz4p9640Qr2OD0521p7btVz2pt88H6+5H10P7/u25JMBmyf4b5Ymm51asiZf6/NVT7076zUnyw+dK8/3pzie60u53+Sw+fRsn8A3LJ7dtchDWPPe1ND5rvP/pfvS'
        b'zl0mOiZbLAd/jbK+8OlLLhXcZh0zHWNhR4SatLU/5uiPb4fYWQapuz5t9eGW5YYnX68MuRkyydLHpDfWLr3X9t3VO5pfXty6Yee2b7vjTs/ddXZPYmrPhKDrJi91F0x6'
        b'u+LrUsuZrZ1ls9Did9b1ff/6uXWaXm9a/Nod9VnukSXfbHqzpXGo0xoLJc1ql4Y2Rnosu9baaHOt+mP3tOSSgb4z6rsdG6846dyq3Hjwy4bUgQc7PzOenPzl2pwFWe0d'
        b'A16fTv0pq3SG27JNBUeOub/7ytVbjiVq3/IOgZuCTzwfk7E7c2bwHa2U9NMzo67mPuYukd+8d3371nulTzaabOl1+aFVw2lio0vj1ONzW7T7Z/UFuWS5RXae3f/O0cFw'
        b'z28Dl4/ZHphT9s5Pd33ygieef+ByZfumtcdMY5yLdr+eEfHBv8/+4HP1x027H7Rn2HS1TY7f8d7bQfcec0rdFL91T4fGxQ3OPjMmbyuZm/rq88H50xZeSkw2/Amu29X0'
        b'zir52MHXpW/V61/1uZ0f19NsbVvb3eN+wy41wSfqs/3jpzTEPX94INi1QO+Zi5G/lV/qL/7S0MHOrdnq1C2j2Ii3dr/3ValnxJcnwy+/Mi/3xF7X4CXfm6H33CZf/TBm'
        b'xueftdWfVG+Xz3v5nvakW0mljil6TgHPNjm9qD4YPXVP1Ltf51589tIL+lfNlqsfHjNJPLX0u+p/f7plYo9eJ6qWOaSQxe2/gHuUreTqYXNJha2k/XpmhzcATQtHGGd6'
        b'EI4EM/jMSx/mRy7RaNtYriQy5ex1WKqcc5Cd/NWoce5DhoEh6LJoJRZTTjBOcjKcUplS2+7CEqAFOkOFtKidUMUMR7ug4xF+CuE0qmeMyREvKMOcN2rcj5nvkYy3P+pL'
        b'UcBW6lAjcZPuN546SkenElKYv1TxXsrnz15NDR/18FZML2ovWaI2wq0EEbmwg/QcS7DUPRI6JobucYuYnHECatBpqbWNOWrGGxXrodRQQIctdVis+dmojdihJ8kwD34Q'
        b'ZabxeER6HBkv3AgZKFsug0q4RnheYhfpI2flHjJdR7lD1BCNigPS8NdaaQLm4TIxF0dGTW8DHBu2mkSH3Pk9npNpJPnESB3M8appolxOWMO7JXqwuurwhtaA+d16ayV7'
        b'jS4toSy0eSIx4rVxQI1KnBmzrF2C8unke6NaKJFb0/1UhGXRHkseDqHLcIxynAFw1h8LEhMg53eyRCg6Tcdg/oaJw3LI7K3EKQtqRywGfOw6aEQF/jAwwlxeYRC5gvmR'
        b'gww8yB0E8qRkk1EHnBLMsVDAPHi5EjZdJR6gKgsTwQJK0GUm53WgTJGcRJQgBqsiaJ6VjMVXKMRyInmths7CUTk9bLCoLoJuD2J5fBK3g3GlJ7Hk1iG1909mWVJw/WOM'
        b'UAXqEG2HTFRJ61+P2d8cIkqyodPQiRSECHTMklawP2wMgQ52Towe5TcxBaqo2TKcD8Yj+TCwYgeqHMZWKHEVOpvobCzETHcfoVjtuSrRFgu2AWb07QpoVh+WammUhUoe'
        b'tUd5MXGkzwoKiPRKJVfcWyy8LodT7N1lVG/rq+QF1CA9dYtgPcaazvFW9UDGmsOl9Q9hUvZBI5NK6rZABSrwZes40GobjwWJZrw+6TVPhmz5sEFtLHSRcLAtWOwjFJAM'
        b'ZVuxNJN+wPshN6IoG7VTedhjNjqGl6LnAaXoQGU1Hp/IYovd6Bib5xzUtpnYArNzX8MlGTUJW7F43cfuew6ja/70NQygi6P5nimmYtyYCo5RW7OzOiHWRbi7vXjSe4jw'
        b'6yfAUR0scFJmLQeP1GlcFAEhQt4IXbSnG+ewXs3QZEWKLZ3ZxVA+epNF1yDrEUbHVf5MdOszRKWEiYGTu1Vspjqnu140Cx3dy3pRGIUO+f6uYs4a5WqgKxLohtwptBd6'
        b'UIeqSVkeSwKxIGivCIYnEpnLeAV2YjmqH4be7JVsFqbCidkyg/+PEtX/ypPRSE9FOkprmst/TbaKI/KNBjVCxv8L+oIJlm5MsARkhP9hCQjLQaY0FAKRfQywSGAgaFDJ'
        b'a6JocjKWkXDKSDSeGh+b0lAJAjExFsj/1BsRLlObpAUNka5ImxpBq2FZjBgyG5AyJSzAggEvFliNGiIN4fdmvVSSUkhNzMLkzf+lYbJCarIeNYzv/A3TlYY/t0qmzSfm'
        b'YaaP8uYzZLyF+FgIT2HC4RbiUIEEb6ZefaiTH+raJw7/GFJX2OgOaY80mh2SjjBgTR5PcruQ7zaRH/PIDxKkcEhTZRE4pK4w1BvSHmlBN6QzynaNmkpRMx46IGz8jf/v'
        b'7h2GjZcu4+qdyXxsxSkNXbEgFmz56VupbyD+f/pT0BZpi6hids2mGQ/LvLtRLs+NQ03iSHNU8mijLzLu1A0Op4pXra4yABP+uh0eYUTsuIcNwIICUgM54r8zA2odHebM'
        b'njvLyRF64WJKSvLOpFQ53qEvYq6sEwu7HZMIeBB16Wloa+lq6kjxNpoLR1ApOrZqBSpBJ0IkHGpDfVJpGMqnThr2QlMIFtXb4BzHzeJmzUD19LFMfa6jGPJRF8fN5mZD'
        b'FxSlEqYKHV6FqhwFOcokliqOs2bTzFPgArQ6qk2EGo6bw80ZB/nMB/8R1ITqHXlrwCeRE+eEaiKYX4iaxVDsKEFZazluLjd3LWqlZU+HetTuKFofjeecc4aTB1khXbPR'
        b'oKM6OgX9HOfCuaCqWKqe3oW53gvQxaG8NI6bx82DMtRGP/D2xHxklxiuYPbVldzPooup+qSj21C6XLwKqjluMbc4nrU8CvVGyEmwrAGOW8ItWQQ1tClQNvWgXA1dwzOx'
        b'lFu6Cp2kmdEhzHMUy3l/uMpxy7hl/gfYmBSiEle5BDITOG45t9x4HK3OHdo95aKYuRznyXmaQiHrTAsxLZKrY86tjeO8OK+w7bTkGXBqDYHul+Hp9+a8zRHLDj0h0I1w'
        b'Xy7iMfHhfKToGCumhjhRQF0CVGEi9OV8Y2TUFoFAZ5xQlxq6RFrox/lhwjjKhrwv0BZ18ZhX68FSD+cfFcUeZ0EV7lWXJB6zJwFcwIwpdGxnY77rFOoSwUk0yHGBXOAa'
        b'yKUVH9hCWGR1yNyOWSxuBWqAs2xkjkLjeiknoAoWOeGsOzMh6ETXUKdUDOkon+OCuCArdIblvwAn90uFGSiD2NOuQv1jWHNyIcdGqhYPRzkumAuGS7PYAGejNj0pvwvv'
        b'iau51VAoo5ntUKVYKkFXfDguhAuBLnSKZa6Bxi1S0Xi8B67h1sBxJ1bhIFzUkapDjiXHreXWQtVG9jjfbToUcPGYENcR3w5Qwcb9KiauWigQ79+J2VpuvRxdUBAuFEqh'
        b'QBDt47gN3IZdKJtW6QAXsFRVJrHZwHH2nP2kQDoZqNABtZL7sENwmEZiwcV3U9KAdLHFKg6dTaYWS4ttadnJcBj6UJlgOofjbDibRFRC866D/sWreKjBNVpylpLlNK/V'
        b'TLxUytQ98a7owDngCroZWbQtgDOoTO0AyqEWGwshg3WnZRE6vUpCDFPwKuOmh2I+1JaakGDWKof6icD/bAiikgQ9E3GG6NRM1ClC/XAZdVLnIFjIOId66Wv8QwSHknGm'
        b'dtyjNpxLPpvmmY2HbUBZkiLLKXQManCWAFCYgxVMk9mgM1gaKaa5eM7IEr9GFTtYNdcwb9033B6RAS6jAO90p3CmCWnUuGg9qkTHWEtIDoEzMsTiwSXS2vzp1PDLCaoD'
        b'WAmKDLwereQkZubZLTyc2YcKDBX1qAOeCUPoIyXUrqCXeL5wYjWrQn0qni501Ignb6s8aCvhhOUBZQvxcFnQoahDh0iWY5BHOzp2L25koBYbCDOBDAV5nY03I6quSd9H'
        b'Av+x0ZzKmUAvbg3JUDCGvjfH4jSejQwnOicivKBwN0kfcqIU3mEOYpm5QDlS6ltJB9QlOMcUN1q/x0Gopj2grw3wGGiZkPJrzJgTjoYVVPtK6mfdYPPejsk+Hefbsome'
        b'hXhvyLWl77Ck24k64QoZqUZUi1pwpuh4NpzZgh8jCpbFnZTjPYu09nQEzTEWNQcqKiNDupUSRtcCnCMeNdKKJiFyd6Lqz0wlHRZ4+ONcCbHsavVKohat6DDqTOb2TWFD'
        b'xmHqJ7PinIyrL1DSJ8mBhwSd1SC9bsf7Dhk2gVzD2CjGFOfBo8qjQlecJVxG27EbZUKtqh3qUEv7G4IaSW+q4Tgzb7vkjsW4Xrw7svFVNyc9JvUUQxMzPUyfC1hqgiNL'
        b'yOvFw/PfZUvfO0+djAoWBpNxzSCDRmo5RqqoDKPvV6XBaRvLNNJK+t5d8X0qaqbTpwUtVqoBVSwEMlp4vo6QYoriaDYnC6hUdUax4sioQCddL6huKSPGBswfNLBVeziZ'
        b'w+zDYUbvvRGUlhzVoBUVWLixHBnJit6awAC903eHYn221ET42K42ciZFt+ETg8zKFAcSu47tK1BL6QedCkdNJE8uXivUu3LHdNzdmao8eFYsURstpgEKaBPmQjU6p9qj'
        b'6KLfvhhnOLCHzojUVT488aySAtS6D2eQYF6E3vvUpPjb7NtJNwQzni2miYvYntS7a6xyMeMWbMU0sdkHv16pTUcn0piEn1CQLjpEqXvdRvxefyoj/17IxhJ+wXqUR1qA'
        b'WTTSATp+h+MpUUEn3ttZGWwgyAJol0IJyXMBFdBMxFCja3hG1RfTRXIWyELDvE06W/ZXZeSaiOVYgiduPVsDqBuyZDztjbkD5PsugqM0xiaJEa8B7QJkzIKa25TBPJq8'
        b'kJrhaSdRg73EMGmo7YZpPsw2L3iZNjHY08jbHOrXZ7OcPRy7SJMY7IW+ExfqV+Cuzx6+uMmQwyeI1b91Qyf6aWqzhx+bUxN408xFodqRU43Ywxtj9DjcdodfHUJjZVYi'
        b'9nBRJI0wFaptHWrrJklmD3+LH8PhoTBV2x8aOz/Nmz381x5qbajvNyHUduKKUPbwsf3GnBVu/OrA0H1aETPZw+n7TUggrG0tFqETj0xJ4YKX3648Sf67vuC2I/3v2wX0'
        b'+JzuD7lk2I4s57gELuEgNNDH6qgyBc9wDrqGuUtuVywqZGbGEyn9Vag/TATonCceeufIUQaMYiXvTlZGtMKEkcW/UsW9ilJANYYkMfERkbuUYa+0uT8Ke6WnNRz2yoOQ'
        b'Qb80zCaAuBmnloH+foH4mB2phnsohhje/zBrgSqli1C9HR2rS5PWcRcJBxoXOr5r/25OpkUfP4WFGkIUCZqhsU8sO8jG9WltasWp/2BzqO3jC+3ZQ+ONlCisgsJCba8t'
        b'T2EPff0NCFE4zFIPdd88x5M9lMymaiOHNM9Q7R0eCpra5K1LiMJU3TlUe9qYJezhjz6UKLwMp4Zq98WJ2cPeRZQoVgTsDPVzcFQQmrVcSohiocb40NgyHUWTtq43IkSh'
        b'n7ks1L3BaQ1zsJS3jBHFZfPQfVM37cUyf/By+qJUlzZL/65vaOwic12Wu26mGm3BVLtQvx/X72UPb66jOV0OeYVq2wdK2MOB/ZTUrX7xDLW1cNnIHrbsoDk1flkWGhs0'
        b'wwxXFhAQEzfpR0GegmfvYFSYR5B/oNEi/dYvbr5z88tJx2/e3GRy7SupkbHf3Gk+RklPJkz74GJeSSaSVpib2ydWLPk+Zo6uelle9Ec36r5+etc3t67/KHIZpxeil43q'
        b'B1re3bv6+z01uprjdZOfqePGLitfsVyy+rUVnqLJT738hMu+bv2aQt3+ioV6ZS5Zr7oc7nLJkVU/Ldn4hOXGp+ZEXQlIlKyZVbDj8oOYN1aUBlYvzTK6+6tXwDGXDtcU'
        b'gxnlbQZul79eFJ30xbG5z27r+zh8dkBpeGHf5CefvRU0aT9CfMOejwqu+343L6lh6Ev92/Nur8pxKPb8wcRtXL5/WNWRCf7SgCe3L5xQdu6Z+LWhOdIL+z7cWtVf22rV'
        b'cOPLs4m1xu4vXi44N+3t2c8E177zhL/Wvaee/eHZlM2V1gMbPy9tTpKt3rtj7uL3Wk7+HF+049yLTm33XIIKLh9ItsmRfBe3YFHwTg/7j7w3u9yZeXRJQXnLjbePTvOt'
        b'SVvfPf5tjXcqxO8dffvVjzaWlsWMn/3CpPd+/jDpsIftM3M3f5x5rOXXKbWfTDKy+2bBg/jiPRFP1VbdnP/xj2+VyW42xKZ90DHp5r6Xng5qeU98Obrrpt/BnMyPL0aM'
        b'OydzK/986YyTSe6OB1pqBefd+3wLPpyy6Kc3dD4Kf7e7dsvaubwz0vpCbvPGuSftno8e3FXoED5k8J5JimfAc9uXtffZvT71i2eqX1gb+dbUG1++NVb/2vGd3yVN6hW/'
        b'F6l1/tKzmwYWHG/wrPpXxfUVC97MFcVL7fX3vTHj9briH3o8q9SfvN/d4PDY4d5luk98dDskbOEbEy6II6a7aOzQ/Drz18ClcY5LWtcH194sfv345pfKZw++fvb75ya8'
        b'cmdg35Yne8feDR56oG75/NvPm6+R6VKth3wsFgy66E4h4VZslOzjUT2/kt5J74c6qvf1wkxdNtENiL146Nqzn90ml+5c6EtjY/oSH/RSVAXnnEWCPfSzy+7mrXhb6cL/'
        b'euHsFrmEE2nxs6BxMvu2GxpQpQ0qgguzocxHwokjeHwK1qEj7IL5MDoBF30D7by9bb3FnHQnNEKmgKpQFipihTe64ZNsIXTbjjTG2x5H720d0Vly3BbNxPJrJW6ZOJVH'
        b'eYs2MTVcA7qASm1QQxoNwSRAFx8CPWmsUcd3oaPMCM/Xjfi8oTZ4qBx10TqnQj86qwDGSDhttXUmAhpMg2I6iLG8hy91eFMciVsjHstD7VzUwdzcFEMe6veFjA3KAMTW'
        b'iKmFMGdwimBjFPG/UB4Hl+OY+6d0aJVN+L+15vnjq1D1v3njPKQlDw+L3xITFxYdSS+er5IT8K8Y9Rzk/MUKHxWP/qclML8VWtQ8R1c0nbq0J94xiBGQCfVwoUvd6xPv'
        b'GcSch/nIMCDmPyIj/NuCerwgzu31qfmQQM2CtOhvYlBkpbjaZpfWYpxfn7fnk2+pLjtFQ6KYuOgR98x/cXg+VtnfkLIGiP0N8cf+l+xv0rmnTUfcJlOmUIaXVqNNgBlc'
        b'HnnYSziTzWINzNoXjvI7rLqLJK4mRoAieQVATYjSUvkbFv+hv2EG6x5xI6mt+H/0jeTkgEffgxJnHrhOIUr4pyhk4Xd1SRgILt2PcKw1+zQw2/jvBfM4alAzB6/1c4Qf'
        b'XmOlgFBaeXmv8kJHaPgMbwnnvFfNCspcYlb+6CGRE53/1449d0O9wp6Psiq9E/r81m1RoRFWYX5h26Nit94L1Yh6f1NvLM/FnFKrlz6QCXThp6ZG4k1QhgV26lFHzV0Y'
        b'aw6VVD2+HpUZPOTTacGa4QCCRyBXiVR5xPX2kDR8W2T4ji2UC6SLyOGvL6KDnBWLJ7FnyhbiYXsL8QwxbHQ2omQlSfMxIwhaGEW3t1V0+wn+y1hLEeP5L9JtOve57kjK'
        b'XUL2vXPbsXxHHKp5kcAyDML1sK2YLzGxQEVqkI9yEqEB6kMI+NRUigWf8+gsteDaBpejfG0DUJEn0QGLObXxghYc0aEM+yYYWOoo2KDSAIETxvAcH0zp5Ln1VLJZe0ct'
        b'VHtmxAoSvZbs0aGGFiQaezsMBBDYnUagIJ/GkLvfzqQixgqPCaHay3w0ODm51GtveHmVTuK1rCQRCdjELQ+lWTcYMw6veWmo7RvxK7hYMqJ7nSSEQea45bHaSXH/WujD'
        b'yUnzWlwdV61O/f4pWZqIE0l4S6fX5QS5PNuy6iPBeTaBk0q199JSnZZQttNsvEVo7PiUhRzNV/FK9UeSn1sI3FnX+zu5Hn50/8nKjz4WyB3eBk3T6ylycsc6/4nBVat1'
        b'duokBuOip6rZ8eULZsgJ1dZOO2Rj7333lq11sxWxAzHsEN0qCaE7OMWRJ+kMvKp3/bTU9jpeJeq8MHu3O6134o/TXuUu/YrpgpMN/EYfbRvc/KrYwg7z3Zz1N5/QR7Mi'
        b'ggr4j73xJHCbvoymrXvlfkDBDfz7Q+5xPqv9efrsMfdJBTfwZHzE9a3JPt3OhNhByN6NCrxtV2OGAy8bR8xJQ4HgQ5BYlI12dae8tUPx0lA/E715jLeOH88Y7mrPUD+N'
        b'/eu4mPsu9by8BpPrzPbwZaW+AbcWamd/3hIcdOzc7uc5zeIlZiYXXMTFEjl3vsG7fsxSjY5Eby9J7Z6MOxL1D8xsXZ6/EJV13mBW1TM/x/324N5rXXuysyymfb/NQ3/X'
        b'keyaNOR9wTV3+vuvLH3V/NOJxmWHXjnccc6iyfjqg2+t+wM6PkvhZhuMDb56x3JpUt1n3p/zNzfriUSfqy+94Wb42N1/lWrvaNmg8ezY6u/yo2zb+MG8x7I32rx3631f'
        b'+5jWNcjzjdufl7/wxV3vxsKNXTfT20sN11y/vuFSxJ61H1x0Czha2ap2Tlb6vf3465OLB2/MuTjnoO7N5c+tXpjU1fdS8vW59498rwcfWL10P7X7U+t7b116+dAZ78Hw'
        b'F7rUvrmavSNJzbzk51dvhagv7Cvy2xPoOnDr1RcOJW6+9quJx3Ebp4k39H6aMPXbl0rmfSl/eaysqmmb28qS56o7n/s1KSTtLe/W5458mn3zzM69drcOvtRpPSk+y/nM'
        b'mq/OPDY1vHe5TpzvfdPebscn5UNlnxu+tKf2msED+eX0LZ1nXl7x2nsJkfMHj7X8y9Tpqe9q6z8LiM+Qpso8TrxvsiWro+KjvkGZvgLEUAh5vjJUaGcKrVZqnFq0YB0K'
        b'LdRcw9wV6gmP5OnKQJAacFRIQP2Yh6KMF2pbSOxO/DfDeSzLiWfxcIFjnh1RGxQvp1zZClTsjQoJRk4DzgoHIH8587pXAKVwWZ6yc6eOLhTp6WE+OAt1aifhMxSdFsEp'
        b'SGf2SZFQtYbyquErVKzqUXRNEX/NQLxdm1jnXCC24Jm8ZzRcYTzqlQmCjQ9lCk9CK+YK1YIEI8hhjvXwDtcKObRxYUuVHOOUKMqHToc8OIcZzQDUQyrFVWpKBShbhpht'
        b'OlzF7c7Cn8rslsEAMeRQCxWmQh+UMNv0GnQ1gGJYTOIUKBbHuIksUtlVzEdfwyWjXG8SRZZ4epdCh4C50MPQRttlCp1w1tfb3w1OKEZ7kxBpsZShSRrQFd6X+o7Dy/GU'
        b'4rTbhHLoQBwcO53ihP0ku2R4At1wX496/Jc6+H9i7TyKDx0+/ejWVvF3jtAZuhIarInymrqYt9SnRyoJy6TPm1FukfCNJKwS4Tm1qTc15o+N5CTcpxrlMgm/SvhMYmAu'
        b'4LfUxJwZQijKJxxp8h0VhykZEieGpWwbEkeEpYQNaUZHpmxJiUmJjfy7PKco+TNS5l3y41PVKU7qMfrbp/gXkx/mP/ES7Cem1jNRs+7Ik1ydM/EXG81aGi4omDbSJxUP'
        b'SLgYqgnno0QqdwjCnzrgiH6YC1Tdo6m4QHEAPsgJ5GQPHINKLDgSmHqeLSbwCygPU7EB9BJdWydkx8yzP83Lyd3t4xfm3A29E/pZqF/YvUitqPcxZzdBe0KbKPHpf43w'
        b'mSL6QwOEIR0yMaMJzPrvENi25HuqKRezCbo72oJlJCMmPDyP5OPVf3seW/VHziPZBVFWFJzGQ4Y6F+FRGz2TlkskwVvRhf/ZVP7On43od1MpCoiZ1fWRiMaskMv+zaYo'
        b'NmprhFcYZsDrv/BT56YMibyrnf7iJMn/u0nakfz5w5P02Z9N0mejJ4l8vPZvT1LLqEmahr+EVoT/2QTYHdzx+0lCZyShXqjt0bNETIpyyDzxOeIo8V+cp1GCl+iR86QV'
        b'wHQn7VyEr60kOmCYBUfNjB+eKZ4s7BNzu75asG/+h1Nlc5mDgBWi+VMFGgxE+5bdQnY7m7Oa26OP2W4uMWzKLtODChcmLagzCNXvXQWtJJXJwWlUxUr+IkY98QUeH7Jm'
        b'oX5LpllzVAOojbrRxVV26LgNNK318hZxausEHmVCZYzL2wUieRrO8t7+eZOODOgIK7XFb/7yxdTxC2uzbNQFg8V3j1ZnaGjceybP2ypj/e60odjlXcuWfIhKa/N8fpBs'
        b'TrEqGwrQeHvMN5snvvTtizm3CjNqCpwmnfJ8q+bVEK3JzxmfKtZ8/Ivbnx1wfD22s+9i/nPF7z34NFlP6/GwX0UVmhMvJEpkGsyesBCuJdvYLbewIqoXNagU7FAe9LFD'
        b'/fCCFMLk4AO/By6p2JxdqJW+lqFeXV+yoRW4YSalMJC4zDiCuY1N09nJ3I/qBV9bKy+oxByB6j7MUouVXR++Es772BBFFBGDeeK63IJWTZvVvGzTiGstAa4kosEFyxmb'
        b'cg43+ryNF7U3FTujYiMe2tw4VmwtOi9TYlbJZZk1HOKhYzm0/2494pXzp7ZcQ9pkK02MiNpCzj26SOf/nUUaT65qdBUoMFN6SBvwyV+MWLirSS3ih8BUv2umkPwl+Wa1'
        b'sl20iA1/e/k2Gjx8VqovmcwOJS9vfGCS4dwQynFTUKYYnUPX0JVRe6Km4rfc5KHQdOWicu1y9SghQijk6d2NMOxeKEojQhQhztQ4zK8XR0oiJBFqmVyEeoRGobBeDac1'
        b'aVqLptVxWkrT2jStgdM6NK1L05o4rUfT+jSthdNjaNqApqU4bUjTRjStjdPGNG1C0zo4PZamTWlaF6fH0fR4mtbD6Qk0PZGm9Un4PNyrSRGTMzXWj4mURHGRYw5zRfz6'
        b'MfgNuafSxBvXlAgz/NYgwpzeQVkMqfuHxRODxZ/tRgVEIlHUzOLYKxYibnTAJMwfkt350Xsl8XdJfTdRIz06tOR001TtmuI/3DUVobh+Pvwf43CNauFwHK4/inpFVgQL'
        b'vEX+IvG1wlgRK5YuN4uKiX1ECC8VNREa1vjdzm0ekEqOQHRmhg5d2SRET6BdCMr1gB4K8sKHTa6tPc958urOWNrIY4GhmrE8VSBNTFqFX4Yo4GDBGjt1EqFSEkwibyvi'
        b'LoebaWh7mtMtXM0YsqivHRF3ALqorx1zOM7sNYrGozISVFkVURk1mwt7Z/nQawDnBHTIRgt1+Pgzx+o2PGc4Q4SqUDk6xqzZzvj6+8JR3dk+Asejdg71omIbFnylCp3G'
        b'Ukp2NC6bhQqPnU5rDIcGGPS19/GnvvelzrEJAhbMatA1Zl1UAFViIkiiUlRO7MFRgR9x0Y/OiBZD0XSqPo+fluaLxyYHjnnhdpFS9KaK1kIlOsvuLi6gfMhlAhLxw60B'
        b'vVCOd/G9qFfMLD/a4Lw6Fq6scQaiey9A1zQFyIB+VE5b6IjOoLph308oO8KHuH66as78/fRD+RTmzUHEbYDDzJvDNFNqxjVmyn5fOwOll62ZcB6K6DglzV/PPGhJuOjZ'
        b'1IEWHPFmlg150Ok5ygPWBDivLzIOcKZH7Imp9DJr7UuLQ7VPJYWzoF1ToRqdX8VtJ1pwc84cSq0w201GD8u8KFPl2EpmZy9R+bWCXHSclnh/HNUfmz0rCY19Sm7BDm0j'
        b'lKF0tCUmQKEe6mnLBlXTAVuTBm02KPfgxtGetqAL6hmE80r0bFylwtEWtEO5ABWrgyhbax1mYAN5UY9yVkWdYSVBDm3B5P2Lfe13uvj4U6MIPC+6qEa0CXJ305slY296'
        b's8Tt9Q3VluyYy66bbJPp2CSeXxTqN9fagT08M4bmNHvHO9Tv8/AQ9vD6HppzW7pPqK3VDn0u5lz+TYl8Jd6A5i9aur/ULQg56Gf3fPNUcnXah9NM2lfd4sq/S5kTvzOo'
        b'YpzWjIa3318uC03WevH69qlmS9Qqv7+/Y9rnB8bv/e6puwHOWc6tFqkOMye8d361zrspiQ7g+lV8V6CG6y7Jmcy3rRt36u2dNumN6tonrM+s9jgzu271pMStbTrfZzp+'
        b'EHx5Zmym/ODQsVSz3fryBZ+EPb/7+aneog9mZZ02XDfuG7/339d4Qb1wonujX+DmeTUdOqlbXw/5Ns065inD6ckm2yKMN21YHRiz6NuA3qElG+3erfEPGNgU9EL1uQln'
        b'570atG1M2umgD358cU+Q3U/Gv336vMtLqZapdj231r3i4OuyoX3Xk9n3RTvL/vXG1nX5HxtvqEV18e/eNLgZ5Hz/bWnD2Kc2Ww1+9a/OCN1V7z7ofMLR173rysDFJ6TP'
        b'zV7/4ObJuz6frf/sROS4FzstH6x9o+/tE99eq1h9/LW6zxIW8JefLJvi1ysbT29dDNBFvHUwhgXLe4fEzphjWQkX2O3GnhBfP2t79lZqYhQroHoxushuizrxzvH/eHsP'
        b'uCrvq3H8DvbeQ1FRQWSq4AIRRRSQqSIqTi4bZHNBRFGGbEQ2MmXL3qKASHNO3zbtm650Js37Nm3SJG3TpuPtSv9t/uf7PPdeQdEk9n1/5dMI9z7Pd5zv2ed8zynlbv3z'
        b'wQE1rEiIEOXiFA5y3pM4KMcyvl1KphkWLW+Xkolt/IW4Rci7ssLlD4/Ml13Gk4Rzy4jzgUIWsGGMEVrOcUqzKVbxdwFLaQPMOa5gjZqQF5AhwpZ46JMyIryKRVf8tT3k'
        b'wUQPrOYuAHnhIixwTVGcHA/hExnXNMEOJTcyg6e4G36REh2oCGY8ExuzxInCUxm4wOly1kS/LVyNVuKZpIMWifGeEKpx6ir3tRTmU+hbHeyQs0/WugQ6CaxczuM83gqF'
        b'Cksxu0D2lHca7BFDF8zacuAVQ8822nMZPAqGUTn7NLgmhocesbw6+eiUPrcCGffUTM45TrveCRWy4GwYtLN+EDLuqRmDT6xF2JkYzmnA9ngLm+X1HrA7hiv54AjTqdzt'
        b'vUuhfvTqTWLuT9mdrrpYikMevP5cgBVZ3OSMD+3SZaX1zFmdSb7dzCzWQT9UwC2s27as6p8B9omJfc1DHl8CZsZiPXdLjWNHmi4pWMHKPtTDHb70TDsUqbI5+vCOnMXr'
        b'eIm93aGIa9SQHmKdTtwuyPEFFfYOZqrqB2/kcGStEt5n+AMzWKAQuzqxYjcowUkei+qj2T2pnS5cuxkZYzPYK4bHNtDFPXF8gxft6D40PFVJiXh0xNDvh3dslV/sVFJ/'
        b'1fsaig4JE19Gtb8p0NDgFHstLparJuR9cuziENdQnfthpRY0uOgw86+pCLWUjLgrRBpc7wT5p/yPlkiPixJ/mec1hDl6MnXz2cYIsqtHv1rpE1D7wu5KEf+q3QowpX5p'
        b'k6PWYvllo+cW+0VLk78jeGlp8m9pyLsfKGZQND7YxLUbkKm1T0vwv3qng7dVL2XExya/tPfAd+UL4qeX9x5g70mkmemvVrFc6VKEc8RLJv2+YtKt3omSWMv4GMt4Kd+H'
        b'9pDzIQUMXqU0/PGXw/9HipktuOrg6dFR8dKU9Ffs7pD+lZe3knhLMdt62Wx8Q4cvvztZ+Xn1S0kpUfEx8S890ncUs9pwdf4lGVJL/rXIV53+lnz66OzoyMyXd7P4mWJ6'
        b'K8X0/GuvNrcCl7nbcy+b+ReKme3kaCVdRlKEX/wQrwR61UtR0RGEKi+Z/5eK+TdwtMQ9/2+1G1C/JMfQl0z7kWLajStw+pUmVpy03Jf0kol/o5jYerl1zWAuN61XTi6b'
        b'mxNiz+a0CBU5LYJSQaEgV5ijcl3AOQmEnJNAcEO4Wv4MG+p516raC/JnvkTxeDF3Ckqfnlm1xzSHX1fiorlG3NI41uH8KZalR/MtJ7hG2Mkp0uf9Cyt8DPLjeM6LX/Jg'
        b'u4hrDhBbX8s1B1j/l5h3A1QFamXC2aOGtkJOdbzMGlDxSqsdzmDnMq0VauDRC+rWX5LfaObaA31xVeKmQDVng1xyKfb5NDEmJjZaGvTFi9mzZXyiIbvg+YVFdZ6gbnlR'
        b'+0zmdDLDwjicluly2GCv8HtwrbjLID92eWYMK9FBtoaKJizq4ND/XZzt+WwrOta5wyMiLjjz98IxFpxJiPk4vDLW9w9bWHjmDYFg0yPx/b+zK/T8bRioOig/X9rPOWOF'
        b'TVLn+3mxm/TwVz5mzZcfc0a0dIX2lrTyqFdGdJ4+oVjUX17h0CtXxHRYpj5Uu+Pjl5z6LqhZfupkGrBTt9PEsnAsthVx/h0lzD/H48M2mFLSFcJ9LBPxgZlyXejjX8KJ'
        b'HCUXIUxrQnP8/ENrZS4mtNHE+XKsb2QAS2/7+UB0XOyFvrjYgEg/SZBE+Eezy2YJZiFnPtyu7JIaIxBMtKv9+LOc57LVVs9cSz8tQx2+vNiXOTaxlqqOKEf/uaOTz7zq'
        b'ET0z8+9e4Wzql6eorTL/6uyYi6zxlf4Fisja5zHlW8SUA5/jqF4sIy+DF/nEgle6iDMsM6TxiYmWWZLE+KiXeHuFgtWEiUrQSW/O//ZPk2tGHUI9OhnLLLO95wLiv/O9'
        b'X4gy2Nvfmgv7Tfi3I7Z+4CfRivmIfntfsrVR8GbAEWfbgHD9mPXFm/ZbfutEr6qxxHZCMDgS/VG49uYhyUfhiTF2fxyUvB6RFCMo3x41ucvlB9t96d/722Onjazz/yfv'
        b'jQ+I3b971PT1n5y2VeOMYPO1B+2X2Zs6MCuGSmUfbMZZPvG7Epagb4VbWBSGt6/BExznrehFLDm4wsUqgoZz15h5zjOc+47QbL/SbQxT0I6tWLydN9MboSHJ/6kPQnez'
        b'GKfg9pnjh6V8PfTHeEveakJ4hCzke6zsCfMSGOMSjNsTSR6FESUBuyakkijaBMP2fPmnUayHh/70nYOKQMlCiKXqMIW9OCCXHJ8XA1OLz7jEHTFHO4e/LO0YqnCp0Nz/'
        b'uSRpNVZBY5ktKB/+RQJu1fWtkHdqtLJ/vAJ5lRisapwqFmRruFoJjGW1LriA3CkGJDGZZunclei3WOkLNblB8baaXLd/W4VXk99W4TXYt9XkKuXbanKtkGMU3HZ4WPz7'
        b'HSWXMaHf08IuMyixMolqhERbz//7FSh0NLVE/H3MMXcplGGHQm4oCzSgSgQLVjkrZLeB7N+MgmeDiCr1ZvWCKNFtFlpTLdEuMSgxjFH+4sFD/i1SKjSjtG6pseBhjCBa'
        b'jQvXqbGxo7RvC7n0ck0aVylKJ0qXG1dd8Z0yKbB6UfrcpxrcasyiDG6Loqy4dwy4t4yijG+p0/ea9L2APVGvSj9mUSa3VaKsuVIayrKuKtolOiV6JfolhiVmMVpR5lFr'
        b'uPe0+HHpR61enda69rY4agsXMFXmonqsB5BOiS6brcSoxLjEpMSU3teLsohax72vLXufe7teNWo9vW/Dzcne1OXeMqE31LmwJHtDh9vfRrY/2oEoalPUZm6HulGGHNff'
        b'+raODO/pH0lsdPrPd9LBrGDmnpYrn2ASgP7NsJQQ818uElgcUSK1lKQzR0taZjzh94qBYkhx556Poq8ipcyUi5daStMlyRmSSGbHZjwTbjwqJRGTki6bSjGLJENhCZFs'
        b'SraUWMbGZ0Uny4ZNSb/6zDBOTpZXJOmsi5qb2/PxTGZkPbNBhWg7dOSkp5Pl4ZRkG6llZkY0t4PU9JSoTG65G1dGcGUus2AWxhXL0HzFHQeu3oqi1go7dkW9FXGp+IW3'
        b'G2Ti+ednnz0YDkTPRHHl0jlJvpVXCuQqIMmsMTrO5eBf1exiZ84dVZST5VHO7xSVQisiM80yOjs+Q8o+ucIgGiFz2ESvojHIFiSzsPk1PWd3X4lni6RvYjJpOElUFKHH'
        b'C9aUHEX/t5SkpqbEJ9OEy/1SL1FXVuhSCnVFOyiT+QixNDqCRWPlpU19mR97zp93ZWMt3g7gapGe8A0IkpcogyUs0cQ+GMNCLmC98YgR/dX63CjcEPSizAefhSXquVux'
        b'l4+xLpicxTpSmn2VBMo2wsOkDNzFGZjlS2WMb4J6e5g5pcrdAcYOaOMiqUL7ayGO2I9T2OfMFRrsdhLouous9lhk2rAxW6DImqsTrriEwoLuXP8uHDMV7LFVhpq1Fly1'
        b'ECmW2NnfhPsi5prIgMFETnNb2MNFTgXVyZcDaq6nCDK52mkzcDvYX7Ehu8QTWMr1CLvtgFWBfIW34ymqrFS1DhcYT16/MyONFRxRZnfSyD4IhfH4lk2D4oyv0LeB0W8d'
        b'ueOqA9v1jny2N223ZeIJKz2fnxvkKUl3jlUaWR361c67EXHvXrQodtme5bWj57PYq3/Z7jD/qXex+3+VSUIfGtzv9k+KCPlRR4dbwrfetrr451InzfbfbXHTLf9KWeHR'
        b'xZw9+12nir4HXoXf3feV8ELHqri/pi1IT3xy8Y+NqfBG+9uZVu8fOuN96JcSVQMv3RCH7w4fsK5ud7P58R29b/7t3Lfein/fcu6D6tdavx4w8vH7f2x4a7C9+Zv/efvE'
        b'vbUfH/O4IXFyL/uw0daIy0I+DyU4bont/oro/05c4jXDqa36sugdF7pLwhJZ9A7nbGTd469AlTz8DsM4LdBk8fcofMINfTZc8+xGRSoUK+25AEWc6rfFNEARVoR6rBRo'
        b'ssAijLhy326IgycbdZcnSglhkgzjMT67HR+6+/MJF7YnsEhFoG4kgi4YvsjfEGxyYhUDSdQHsXO2s8I2FdKaZ8THSU9+wqeZ1x4Pt9+G5UwTUIEBEZZhg8M1WOJGN4rE'
        b'LkVI058Paopy3XGSLzk4SSuqhUUYJI2ZwKW0UUiacu15Po98wktvRSuE/ngXL95pYwCNUCQLtrE7O0RajiE+KgJTmFXy9dLkXnfNOqVQ81UMRVierY13tnCv48J5HIRb'
        b'Gaw+oD/cCZbFW/WhSQx3/BL5jffjABbRE3L6hnJoFgp0QsSBl7FSyhUqnoZxH1banlVOKAvmrwtB1TZ/R64kJG1tCCfFAh+YVIU7UAutXOw1TQenJevlaRR8DgU81OEm'
        b'9UyDfNZLTl5iEUbwMV9mESogn4/wdsG8Bbu6RFMp5uyEOyoCExpsCZtin88q+yK52qvFyU5+WRPAlemLKlxeug6XYa7FdRdnuenrOYOAj2jlmK4Uwy/o9a0QsstshJfE'
        b'BcX8s6tEs9Zq0mbcvpzJkCf4cPmFxxcu+Yu6opU/zxvsrikPbT07lSLC5aKQ3c8L62WC+ZVCXrIeyG8KXhqROaD5JXzlcjm7wl29nVeNmEok/oIO67j/Zw7rOFK+MldT'
        b'vtj/Vvis06OTUqSKXsikRcalZCZGMaUnKzqdMwgtJbESppOtOpYiDc8rMVqSzhrsHlYoYjKnN6cUxfNKH/O8ZDJHzKqDZURLmTIXHn4yPTM6PFwet7G7nJIsTeGuWtpZ'
        b'JsZHpEtocBYkzJLEJ0oiEqNfqEtJFe2t5edKr6Wkx8fGJzN9jmniPtHphHlXHSxTGDiuxGesPhofllQs0FuSmEErfFWH/g+sDHmH/ntvfYs59I/nq3G3JtT6hd/f62wr'
        b'5JMlSrEAq3kOaQmVCiYpY5AwYPW/7tO/lLPlGZLNiEy8xEH+33Lte70S31pa4dz3YSCZVMVHT/28D9gvAcGOWGu/XIpg47MXYDm37s1Qs/U6+0kbqXhJej/ngiwRfuH0'
        b'/ueuYTzv6VcKymS8G9tTdzIZqwuLy8Usy/8sC7Dzc4Chk3wqKPsgOIA51GAYyjRdrd3jg1M/E2YwSV11+NFvwp0MfhX+RsS78amSrQa2kgBJInen+qPw5JiPw8tj/WTR'
        b'g9bHaptSxmzFUsaodpIEr3qBhL+Ho7yUl0t4U6jkL/XVQw2MLU/COqO8vCA69q3hEfUJNJAStVKUc1gKvTiDSzHH5CGCl4trRZDiS3u7I1hCyxfC3c+JV6ySx75K0CLw'
        b'ldD5wYpcdtZUGTrXp7wCNvORiMVrZod0jq7BRVsRZ1NFaghk4ax7Blz4wnMdf/mjYD8s8e+sh2ouegG9p+IP/3pExFVNKJnauzJ6ERebGOsXGcRFL8yXRS/6xQLfP/+H'
        b'vXr4Ucfn4xcviT1JXvlYT2tp6CnlmL3oWJ+PZXzOKg690rl9ZXm46cWrIabHnKur8xYO0CKOtygTd1FWcBfxS9PgWYij/zkZ40NSSCJXkZZ7s17sMUlKj47hvRPP5RWt'
        b'4tRIj5ZmpidnuFl6Wrpxif9u4bJdh1umRCSQeH+JM2J1vUY5KHMXgw4MsjoSMpQPPXba8dRpec68ImEeGnCAJc1D3k71hCQY4bq0ZEC761MbnfdbyEx0mMEOmZl+QlMV'
        b'b5NyIM3wFWYE0ms2k76/Cf84/Nfh34iIixmK/ii8veDbEa9HjEjiYhxO2Ur8hN8sFb4VWLlOy3Ly7NfWfM0hpvNso8MHiR9sum/wI6Mt1YnakdvFsSqC/CP61nd9bFU4'
        b'g8yBpPIkZ75qxcoMWBz240MXk4GsBB0zE3VM5Lmvotw9UVxMRgWbz3GGc9AGRW8Jzm4+STYRcyyY4qym/y4oVJjcljLbNikB2v0DgtywWO6j0TwrwjHXC3x3sLtwz3hF'
        b'sqx2xjI+vS9qBam+2PJYXjODXSOS4QpHvG5flnhT+bRCNa63U86aZ8hm2fAr0/9CVzLk1UMpIv6xp0qGGa3x5CtR95jRcup+yTJXJ+znklZepjDIU0kerErS0udThVJi'
        b'LCX/ryjck5/zC1C4cFU1h9TanF/UKWcwv0Tz+PHfhNfueiPio/C4mJHoAcnrEVqcgmtvqnTY4oe2Iq7dxRHojOXucuEdYghYKOSDMGuwXSkHakHWOXHcFx77H8UWaHx6'
        b'20ME+Wo75Mrm6gFszVeWOjcFLEt1NUyQHctLEVb4Agxl64l6JQzt0Pk8DJWtSzbp26oZkqzoS5KMoNV9+iwbViaJVDjzVeVLePQjVjMq5djLQhxRssL8Xwh3PRXhmGip'
        b'hKUESvi0qaSULBJtrJS+fNz/LcTn35EByI05/rlAjAMz8JIyM6TM8OUJMUPKjESWqsgcFasaerzzYkWaGzMSafDVQgUKmmNrTZdc4cFFe34JqTFE03uO1DR4YepPgmLw'
        b'84SpTJCSvVihnmCGt7nbR7syoNHeT6R5VSD0FWAD9kdytWqqf3ScL3Kj5HhKoNQslKr+mvOaF4r4CznfPZgcsOHKPsHJ9EVCA96T3+i21j6Y6NFEIDwhYIXo8uLXvlOp'
        b'lFFEX7o/iAm8HVbZpXPouJbXwu/2X9yupPzan7zyBPnn9ery3tnlYJWR/aRRU+P7O/f/yrb+Bx/57q53Oy+yffjb9i3Ww/+94YSWWd34kTq9Hx9+T7943V/2bvyocFD7'
        b'Gy5rW4s/jYv0C2n9u4PbDve5166oF4/9Y6H4Nws5b/9g9D/vZWr0q/1rUfWNbRsmz1nZHCu0VeM7EnU5ONsfP7Pc6TyK/by3uiZW4+ltFZzZzAttvG/DOVkTj+PUcne3'
        b'CPJwWubvrpIVrcPbeA+q7DOh46n718KNdw3Xq6Ta28nuU5xbK1DfJ4J7aTDLje2BHVD+jP9X5aYJ7//N3sHJ/otwm7Wq1TZb4fa+CAX88FVeULzMa42NOCdyOGH4Asmp'
        b'8kWdp2+ryi4Sc0zU98szUT0tWXkOAy7t34C7cKAlNBLmmKzCwmiilT5Tjn2uEX0BZUC87Nmn/NaC/kx5JX5bZ7Kc375gsQTIYPkF57fVFVnyfDqEuohdkU6UJMee9I5U'
        b'lZEy24aBnJSDGA9m12KZA1GDC4Wz8LuoRLdEr0Rcoi+LuBrEGMh4s2qpOvFmNeLNqhxvVuN4s+oNtadqxc9vKK3Cmz2jolg6fXL0lZW5UMw9xoc1+ShsZEp6enRGakpy'
        b'FHPivfhGLHFMN4lUmu4WrrB8wle4xnjfnYPMY6ZwIrI4+3ODSV4YV7eMlCQzXpyewjJR5NnEUkk6wd8yQpJ8+cUCYUUw9hmFatVQ7AvFxMtECwMEixVnpEZHcjt04KG8'
        b'qqB4eokjOTMpIjr9CweWFYjFL+PpbYwrcfGRcSskFrejZEnS6v7LFN6VKodDXEpiFCHzMvn3TIJ8kiT98jO5EIpDy7Dkb5M4WQbLfab869HSuJQoS7eYzORIQg96Rq47'
        b'h686kHz1kZLExGjmco5JkYlTxa1zHgkyWa4+S2SQrDrOchx6ISQVGYhuls9eNXmapi2f90Xp2rKxIpwjnh9l+YWVz3mfcQbSPUKCLXe7uDru4P7OJO5CRBgVLT8q+ViE'
        b'+jyWrO5sPhwdI8lMlGbISUQx1qonbpNhyf3JEk6eW9wKBUWGmWwrqWQf0G9fQL1S6C2sKN2a5/QWuyBO+zDaEZLhnJ6OYyKBMEUAD9X0+Ivoj25gq2ZWmiRHKBBiKevl'
        b'2LvWVshnE9RAEVZxfrFezCPbGKqEXlhziNODgnAA+unF47zas9XJcSuWbrM7Gkga0NDJVJySnmLdN7g0AQHU26nvhVonLrEBGnHenE9rgHockKU28Bcjn+Y1RF5Ugy7s'
        b'xUW+prettsDsYJGS4Fh4ouDcDgFXAQCGTLGP6Q+KzAQ+8dLB1tFPGfthSrDfXgVbsDKU88lZX4MFrIMKe6xVEQj1WT2WJzjODW8uURFoHQ4RCizDtd7Us+CrujjpkAIm'
        b'DVAWHAzXyo/L5j/cY0eqgKWxkNV/wXAtQSYD+gGXo9hD4ueGj6ZAU/U6V8GLe9okV02gl/rfqoLw8IDgvdsFmUwu4ui+9VxVgRBfzjV8lBZfac/UR8VG6AuCoq+DX4DT'
        b'UUc7FQFW2Gql2d3I3MnpVMlHl+mfKniXV0ErbUkLgsGTMgXUVkUA+TinDj2B0Oltq8ad6FHogvYz8SvDx1awwLdYGTax8cfyAJN4/hI+tp/nbphDB9SvZy1G5DfxuXv4'
        b'2LWHyx65BLccnl7DhzpjJYGWntgYBs7zV9zn8GF4HLTI78hz9+PX23CvrhHksB7kTmpQt/x6PA6c4l69Dk/CBDj59IK8CO7G4XSmNRu2Fmo22svumWJp5vP34+Og2FaT'
        b'R+MCGMRKWGKVVLlaDlwhh23XuXzE83jbEWtJHVyRs3sN67CO74fRh70wiYPa9s/Vcrinzg/fiw9wxt/ZD6p2KIo5DEADl7QSBM2eLJdDip28bykD73BANcROmJRVc8BC'
        b'daFAk5VzwClVvmvEE3xgwkgkGMsOGa+o5VAPhXwBimF4lMblAasoPS3mcBkbONDCQkQULsL8ylTja6yLDHdZfP4UzLDZNxGNLa8bEIf3uNH1ofuSB/YuL/ZA5oYD9HFM'
        b'Q0xAYylDJxxVBOLofWrCfW44yJeIWISpIyFkC1WHHnOECihWEag4CqHjLAzxfvFSuEvYi3XBnqyPrEhLgEtid1sNvvdMCzzApgwdk3XpmTiphZO6UI4PpQTvBPFRX2f+'
        b'4FuMjTN02PdYESt/JANnMpkLo1+M7QT8R1wBBXN4HMY/yT92RZqmnq6toyLYKs4JVsICvBXIwVrC2mJOZ4aQoj+TkaaVBrd10zPFAkML8R4x1mcyXxM2OeF8RlqmBjeQ'
        b'Lj5Qp+lnMtmz/OQ4Bx3KggMXVZQJxbi9ZB3Akoy0VLgte0m+SMNosSdOaPCNap6Y4gK2wJJiaMUa18OY0hY7MYeCEsfwjDQhVChGkqbjDC3wiNgt1Iov/jGHnSpPB1El'
        b'pjolVRHoqYhwDOtiZI1ItmIP6ySlibNSWo2Wujbp7No3RPTZwxQOK45BPw7T4R07Rmd3F6pUBMo4J4QamIEa7oEL8ORMSCDWhFifINurIQRus/KmLUKcTTbii3JMu5yJ'
        b'2f78DBdz+dO/hQ0wtutUBs7q0lci7BfarffmxAmtbYporYKYof+2wIDgUAPoZ7LjhMyqdmCcsfJoAJYTm4CCUPUMvOXIs61mIopkdX9W313oRpaf/QEem+rSnLGP5UH5'
        b'Ep/wdyS+GqREiN0mhkYfHOb4c0boWsHOgznKAr1w96+uMeWZ9npXO8HJgxEEv3DRNa1AAd9bRPC3A7Jfth60VeJbZtVg8TUYZr+1ia4Kru5ew30cbBMEw0qsARnm5why'
        b'/IgVcP24GrHd0F6VNRQ7ki3Ihs6tXMpcmpcPVrAhxrfEC+JD4T5XeOOHXgRZpU4RyZ6AfOcIvhqHsy59mGilRB86hDht5D/c6assUHO/qso+9DDaw39ocIY+1LonoA8T'
        b'bdzVBPFbdzSIMlhlqub400kn9iWv3aG3Lv30mzf6/hw8lRj2r5/+fbe3n6nroV8olYofWQx0CjzPLKh/JSlAqVNzn1tehWWJr/77Wq5+5Sdt//T6hUzbrKz/fvz1n6fG'
        b'JAYfvxrTZzCxzro9tjD9qxEeMd94bfGxx4L6XukfPMzT7N8t+vG4/uWrJ7cHvvfHb26Z3V7w0xC78a9kujflV3xz6dRPOhLSot5vunqk5eRPq3/9boVWKGw5m+p++Hd+'
        b'bxuvddS3EZ8xvhx/q6J9oU79vrfah31tgwGam9e0rTWIyvhh0c9c3u/eUPorxwvftU773Uxb6l+npXOfOLe+1fityrsqmsezjqd95/Q73o/va2weFsxpPOgWb+7MVj4i'
        b'me4Xd5098suNM8qPNNcN7Xoc81/fPfTGz1zeGtOujvb682uWZ89tufiH7+U/hJ8GppT8d/LVhd/+9vWfrruYW/ndT/ILvn6v/NbZQ/Zd9d89OhA1+vMHX59J+KH5cFau'
        b'ScM/P/jz2z/+bdnHhnd/8J7e4u9+75378He//161he4nf2vrrLmo75n/D+lXbbQ3/MH2b59GJ/3s5hvmFw4aa7re/P7JR79qfr00+pfvGv3V9cPXIk/8x0fNDhuyDS+Y'
        b'/0lvCD6suqo5p54bmCj4j9NZHz75Q1bD22Z/a7r9w7GuhZ98bc81t3VvzhR+tOGN6Kj3cpymN1/Z/KnFgu1nwd/ad0V79ieTdt9v/qnXZz+711msKjxwXNXtvR2fpCeD'
        b'narHV7d88vObX70m/kWux7v4D5NZp+Nfd/tQ+tFD7Y++mlT/16DfhO38qCzZ9TspPwh5eDz0x//4jtT0p8bnP/v/3v99Rsk7P/p20KH5qzsCTTz/7lXd+cH7J/75z0aP'
        b'NwMuzr+x7cLu37+1r9zmM0Hg9/7wVamRrRPnagnCIqwLwV77lVFqg6Ni6ISGcM6NYwZPoJwpHsTEZJrHIoxK+XKY49iFeVjuLw+eB3M1gvSxRAyVUKrM14XNgzJoUHiL'
        b'AtWexnjgXggfIprXxruy3Egc2qPCp0bC1Hkut/KwMNn8wqrpfEYwwSVPRhIXbDwpXJZn6IOL3DfbNl5blmZofV3kghUJ3N6tVcUrnExmqf6OsiRD0rJv8V6wJ/v3wrDf'
        b'08J2rKataFMa8NV5ocQeijPt7IMC8baKQGmnEAZjPXkP1GKq3jIHVBi0ixwIWM18OeIMMfbtfyZlM12FrxXSAPdYI/cKW0e+9i7rvC3anJXGDzuLFan+9jBGbJhE91Vj'
        b'HBFZnYd+7vKScC80QPUarurv8nrEm2SpnCRTZ3FaG1uWZ5mugw5u3kicW7MN+/wV2imXKIpj0XyhvknW5ZAUtG0wAZ2qZGp0C0MFu/kSxf0xPti0XXGpidZfEsVnWQ6d'
        b'SHEh4VfhQOojvYvlgQ6kLWwT0yYXdLk1J0MhPvKXZ2GShjUji+KJJFzwby8UujAFLR1meQUtilCPbeYG1u/CNrtnMi1rdfiagyMHSX9r9lqhEUeu4zZ6OBYLnyrEYmzj'
        b'FeKIdfybVefwodqaFeqwEBb4FN8+GIcuTiWOYhB+qhLvhxYeTPkuMLsRxlboxCo+Uk4zyrOFPLlKfBb7nleJvWCWW6F+DgyxERyO8aFLmgTzxClSIe+zvZMRyCohbwtm'
        b'VR5vGBOo7IwOczVerl3DcVKVFHpSGj7QxgmhMxQIHbBdHbuV1bFnAzeHnS+MG+/1VxyKGraIoNwORrgglBrW7/d3gLvmXPsTKNt2lOspvtZbCdpJtedbyse5xyYSURMU'
        b'dhHNCFSxS6SG+aelTOifOkJ6Eydk+2CQhCw8yuJAmJmFox42sio0jPAIgoabxcQ5hvA294Q7jGbZB3mcZk84BWI5qfU0Md5VgrZMTY5u3clUKOaGCHYgrQEHwuhERALT'
        b'XUoHoAILeWDPkVVRxc8DBZdXKWgajo0cAu6Duv1c3n85O4k0yFcWaMJtEZlPp7ldWkJJCOcHL3MgcAdBD86ILMLWc/gdArOMzFj6NM5GcRnU8vRpMtO56LYaLGzAad0s'
        b'zkkegksigToOimCU9MRabnwNvbOHcugYHG23MoSJFZGeNQiDtrr//p2xp97g/8OW4svD45KoqBXh8V8zdezLOch3a3FNvVW4Linyeth8fjGrem0mNBDpKDKQ1UQirua1'
        b'SJZ5TL89091FQ6wkXP6jI1bjRmKzaAh5n7YaVztbiXPFa3C1e1hlbT1uDTpCHZEBd+1R3ullDVfJR4fLftbh6m3rccH8VaKjy8Ahc+Or8754hZM8fR3zzyvc4+nrV7r2'
        b'/73q5qqy7GrFwNyM3GR2irm5sMAm+q1cU1ag8kuFBfIEf3N6WSB2GQhsxW+ryeOgT29cRirxSrtARcA7xjjn2DGBgL9fxUcD1GXRACEXD2DRAFGJfolBibjEMMZQFgtQ'
        b'KlUpFOQq56iwCG2I4LoyFwtQuqEsiwXE2ir9PES0SiwgNFWWYb0yFMA5xSUyp64igPtiB7v8iZVXsKQy//SyIRxkbupISfKqvssIFoaw5JobMT/ji4MOr+KPZxGOVWe1'
        b'ky/PzpK7ZsW5TuXr4B3h/JJYVIOWnsw7n1f3hVt6pURFu7haRkjSOectv+H06NT06IxobuwvF5jmACgLXTxbgmm1mAMNv3oOssyjLffnMxf657l8v4yDl7Uq0hU86+Dd'
        b'wAemLffu8Je1dd9rTMrH8ZeEpqts1XEcCmExk91PToB+mFruR/VlnkUsDQ556lCFyhA/ZUEO3leH21AdyjnosBBHId/eD5/AsIgPasMClHFG9L1sDcFX4hwFZEQnDl/a'
        b'y/edcfjWWyHaqWlRsXzfmfivZB6hT4/aQ489DDAtuRTvhDA/aGAAJ0xPP5emu9IPIA6FhbXa2L8Vuzlb2hbuOeE0yxXFBTVBoEcAXzkg58o/BHoigdnvTeOizU4Nnebt'
        b'+J80H+R76mSanBO8IxBs/+7huwnZ4r3n+K+9u/leotsuXRbmXRxWFliGr307agtfSBSrbM65KLFm4gWX6D+TMMM1BjoKj2Fm+YU9LHX0C8Q65s8lffCozFfuy2Dtf9zX'
        b'z8GP1/FY9Vc1fKTtd3AXdyAZqew8vlCKgTrWqydgtamtkPPynHfdwif3tLBafzIFiO8egF02vOMw34IObbm7MxjnRdeSdDkskhJezDw3t9y3vFXxGuST1TYCeeq5a6Ca'
        b'A1SZiUhQuYm19Ax3+LvTFZnb5GACD8a9e04JZghJO8Oacu5aXvFWNGzlnOW2ynxeQ76VO+dPuYql0Cu46g0D/OdjcP8Up+7lpECzIEcHunnXzyP2w3wq2XjfXJANXSe4'
        b'z2NhgJCJeVXicQAbBPGJTpx76gq2wyTTbQmHKjxggEyq3UIYv47V3Nc22BHi77SikqqtrvjCRSjgfaqFWLyP1/ihBO7JtH4yuvriW36doJzRRIgXoH1hf/VC+skdWsXW'
        b'P/3wFxl/+eBb34hW3xWasEXZ2njdsYM1XW8ey4490RZou2dH0axaoudrf/q9nrtfwvs49Z73jz47+qn1rzYfNmpKu/LncN8ezdf/VmqQNf7Vw62SDb/78Zt+1Zm73xt9'
        b'wyrqnRLbyF1/CjokLXrzs6+m/NffjuxrHvS3qar/dIdVeKnxryyGZrf83MYyW3fDuy7b16f+9WzqX//U1Z8zBG9Z/MTI5xsTZY67vv76z5qj6np2hyZ+4zdtB96c6Kn6'
        b'7S6tX5/ddc/hz0P7Wgb/NTLf57rQkxzfH/C9YXFV+19+cDbrUmCz5cXcd15v+/OV2L94/PC8fWbPyeCKutZfluUOnxvbsuTx7f8RXbT7w1RpdWBC1Lz98BVrH+vCv70X'
        b'fTl54P6f676X+/b7c33T2h/1XvLTtrH76tXi7sVmp53/agw9X/r9KhXPxndSz3X/4xORuYHz16zbm5ocRRd6q/Zliet/2ttxbf6d+ULz/LFv3hm1yzHu2z72k3q3X157'
        b'+7sV99dkRmh97BL0vbP/8on99Yc54v9JF3/9jU6nfx35MPp05gcHCj77i+mIV/XMz8JsTfi7ht3roJ0zTrOgQZ5EWoCynLc26Dm33DyFSegmEzUxkC9JOeMUszwhBWeP'
        b'y+9fLlpwdmoQNm9RlNdQSdwXKtrkFcVbsG0WUM/o6YK2zIKFzljum1NQYsWcCslYIPMrJGG11ErARS0KcHBFfmls7rL8Uvp2gdtULC6xFtbbyJI6QaYB3+PyMpbyrX92'
        b'ei/rcWmTqYmtYpHmGR4aPVuhn+sL5AcVu2WNgaDnKO8weYS3YJH12pG38LmUKYK6dFnG7S1nHLOn1XA2uTrrcF4kgmodY25T26Eu295R3iUARoxFjqY7+KuThXgnmjfX'
        b'CQYLK032a5e5cwg8zdwTVdtgIEDmitHdbbhFfN5Nk3MJaV3K5MwuvBMYCsPEQUlQ2KsI1kIr2Y5YDOO8K6LfmXZQIWspqGLhgZMipVNYwq1CF+9ACTdINnY9YyY24gz3'
        b'jASHoJO375zMVFfaiXqYz6FEODRg/TJDsXTbLiYImaEY7suZiRHYhTX8KCuaxbXjhMxMxFtevFumDlqwdpmdtms3s9TqDvybSrrh/6Fl9ox5prU8+YCzz4YYj/9y9tlN'
        b'gZMWZy1pyPpcqsksIzOuGxF9IqZvROw3Pc7ikv/Lehix/kWsKqoGZ1vJrTg9zpbS4robsctNOrKOmUpcRyMNLk2K/Tdn7bO3DJbtR2ZgqfCmzWaFucNsjGUWld7/Nnxt'
        b'lZZNZqeYkTOrbJm5oSVvNvHlzCoyrLYvN6xetnd5spcmW4iW6BmjStE/85CAy8pWJjOK7z4g4gwrMTOtYrQUZpTSS80ollLluVq6q9yMetqCQJG9yiW9/i/navPvyIvy'
        b'8O+tUkzTydKLz5bhlvKCLCAutZvZWvTo0ZDgvbu372C2TZJEynI9MqTsBucLl8BXA3qa+fJsuUP++y99NUQtiEsmwKk0zRdqmlCMzc9omwlnsdmbUyNtcBg7V9ahOhZ0'
        b'hsQJpyvtOq6IPeM01snjzypYxgcj7+KDnbL49rLo9o5Nh2AYB+KVbYXijFx67kiEl2P5DlbVQemTHwWVdn0oLI219KhxzwPldKtbWn3ff7/llz8+3yt1WcCvdAyWSvTX'
        b'lxslRXw6d6Om4Z9vXQ39WtK5+tfvluR8582dJa2PnQ7nTmzOdv5BmVjyqfh4wW+1Yz+2/s+2X7e2+lxx/F7UZ/v+GpnhPHClp/fDDRt+ten2Vy7ZKnOi5BhOXOUd2mQm'
        b'9cqUhjks56uul0L7eXkaqwY8kt89gTKo5GQEidg1vNrgabPi9gn0QgUnac7BZJrcg40Th1Y4sauxk5OoN7CYublJPPCu8STzUHWLFfdL/i0psYyJ62RydLaCjQe9Chu/'
        b'KVgjv4vCtyuWs3LGsHPWPcNuVs66ktmu5D3LmO2XK+VNnJR7X3MlO+Uvp9NnV1+Zk5ZtWs5JX741Vss2Jz6VeVz+VwpfylxPnw4+n4OaHhkXnyWriSQrvbuiCtMqrNKL'
        b'd2AkXuU8HvFJqYnRzGcTHbXxhWxVtplnKwPRx5/X3UWwKmNSCspkICCFGar4SNOzRihjSPPnZWp6hKlaPFlz3fFvHnAUZbD0MsNMU3a7+/WIj8MTYmrUHWq3SvyEU181'
        b'azFvNfO/22reYhZiVmC+9/vC9no1i9e22CrxkZXH+kIcUV5RH6UfJ3ltty3RhBkG9TeXh662wBLHArSwzVnTHxq0lyWr8yRuZyxlFQRMD5MROs103UmsZL0r8XYgafVH'
        b'A9PSsUP2vD8Mq8KEePfn9oPTk/DHKsenDI5C974ahboy+lSUGlX4VJ+ZYeXNG4eVNLhKrVEHhd/XiSUcMLI6+CpklSf41YpLoJ+3TlaCQjko6KR3kK0oiP+/3ucU5nta'
        b'I0TC/mPG8Qf2G0tk59zWnJLF8QduNzwozP+vleovyK3TWTVMHU3ZjTg1TSWRpeXyqnt6eloiCz0TTQ2hyRrGhAXCLbkGQqdkA6HlBq4t305cwofyy9BYe/HpfWiRYKuN'
        b'chaUQmfmH0Us1eUIGWztULs/BVu365Fm8BAXjPfshrxIHFdxIzFYA7VqZJW1Y8EGbZJbRay7BtQdPgzdmlAL5cK1+AQe4hNtaHbDGaiCKQk8wMGT2iIcg0Ic3+8OT2DC'
        b'F5740FN3sPwqPIRBGHG6Dj0BMOZ+HRfxvipOwBD9zO+CPujB/tg0Z2ts3oF52JUMHXgLB3EKW6/vhwoi3TKYNPVJcw82gYrNmOeVm+CCt3ERHsa7Y/FlnzUbJGu83fyV'
        b'w5yvOQVDT5iFI9ThA3eYw/swDdXJMIQ1NMysL8y6JtnhHedLWKmN/VE4YWgFvaTYdEItdtPPAjaGe2HLMZcEuB2JoyrQAbNYnAKTWIMdITgKE1eSsBee5JK123QSasyx'
        b'+/I5bITePcY45gsL26GStl8DVfqHYTwECm38aQ2z2LIXxnNx+Dg0C7GfLMMCrIc2+vdOHAxgC3RfWS/WJA45g/ecHbAHZ+P2arjjAyiJtIA8nyS4FUXDNgXCY9tI75QN'
        b'3lgVj0+w1Q8bwsxgNNsTH8EUs0H3q8Dd47ahtPUKaIAijS0ncdqMTNZu+ushc3K1nSF4NECTAz7c62G938rIEKdO0Qdt12zOsWD6kJ4hlmA1PDiZQZ/W6GhsIoS6T8Cb'
        b'hHFazoQAm1yi92HzeWh1hscGeE8nIhCqYqUemHcCm9ZDxaXdargEjywM4VEiLK2F4lh6fSSVjOm7OyywO2rTqbP7t5FtPAiPoD9DQljXiC0ntczP5yTvu4YzFhfWQUsQ'
        b'dJufw3GCTxMOqNFmZgilWrD7IFaqQckRnN9OJ9kIw660yxGG8FB4hk7gjuMBwojybJgyXYvlBJ8F7NS5IcbHWOZjpbI/8zahPXZBeSS0n/CEKkJ7LXiM08bXD9Lh3j8C'
        b'eeuhDe86au1E5kOahA7xEeiPlGy2heo4JaiwvLkN+vZm5sTpYgMhYzfJgC6sTA0/DYvGZ6DlILTAJOmAhRKWZNBkvwUf4Tw8FMOEOtavxVmJciq2w0xo2JUD2Jobkkh6'
        b'cSvBYXErbYLQA0eT/ffREB0W0Ir5x87Q2LVnoGkP3IWSCCK9fJFrINbChCM9M4UDMJR7LtdQ78zNiJ0+sdimf3WnPo7STisIjwuJKgp2EVmV+WwIsLq6hTDtDjTjyA7C'
        b'8GHCzEdYKsHaRNYN7DFt6wguQJkq9nlg7TW4l+nvGY+jNliylQyGpet7nG5C8UX1EHhktp6VjMP7+nuVUnApHKdEWJ1tIjmCt2BaAypv+MJdzLfwgaowyMOiKF3iLgPB'
        b'IaHOkQZbzHHQ00fDyMBpu/Jal1AiofYALA2hA76LQ2bEkUYgT4L9u+kkF6AAi8RYGwQ1OGmJbUFYfgaHYFpJn5Cv3BS6aSeMMxVdcmbAhVIcgZkr2eZwez3NN0o4NZBN'
        b'6FCSo69G5DAdg/U4d93ZCOoIjLfoeCaIcz1Qi9Xxw3vmpPR3nj2Fw0R1RfhwwwVYDPSHJbivbgW1GcQQ+qHYNRqnk7DsDCw6rWE+u/PB8HAtodww88zV+vvpn7+CD2g+'
        b'Vhus4xzkEwEt0bbynXHY0CbEyjgY8gnmD8KwL5FANxAMU7b4SBnuRlhBFz7yy/wBw8jhbYQX7Sf2wx2GkbTsOXuYyXTFtvNKNGwn3kqWQCcZdSXYtOuYA/TrhfvDoAdU'
        b'4iwB6zE2rSVMegLltLMpGD8KxeeIWos24aKvh8d+vOsHPVF6GlhEGNtHOPUQbm2GFsssQuEmkQc8virY7XQU6y5L7dl1PLKHRrEc5olyaonkWiPOXUgm3tHtgK0JBO0F'
        b'AaFSOeHqEPRAI9afP0I8ccne9LT0wkXoDKQV9mI1zmwl2qg5sMk5GyuN1GFuOcYSfTQeM6d1PLiChY7qN2EmmWOX9TpXoZn4ZL9nwO6cjZEwEXTtuon4og9UmEJ+DG1s'
        b'iV1OIL5UuNuD8PeuahLchvuXoE6bTnjQUhvq9mKzL3RK6ZF8ZDu5hx0kk+5Dnq4IC/cTB+kzVoWHe3HebAvhwhTMO+MToyvYk2x8VSkuEfOggei1GOt1CVC9tL1+fAzT'
        b'x+gwu/WxPGxdHKFaIU4eJFHxGB+ft2HNB8OyLQh1u5L2Y3U4ya8mWxi8QtRQ6URH0e3pTCyujJCS5Ob5nZd3Yc3WBBzIPaSTQwsshDxC5G6Y3mG5NUoC08RuHmoZYR3O'
        b'Y6EWlnpDh/NJwgfoukoLKMM7W+EBK8EHd3KwW3WtFQF5AXu9w7bBE2zT8LajDRcTf+yEjh0kt1sPw7RP7Ak6y2koyAijE2124pyzOayn1N0LqtHYuD/Gx4mT6Xf8pSRt'
        b'ijOJLVTTM43uPqZnsAlaL0O5KMsM2gi/CYiE39BxNoEWukRGvXWKnzeWJWtjTfRp1XUXcXQNNDHk2kb03O2tDzWHMr/PNIxHu0mEEKtN5hSMxzhuj7PCI+vDoVMVm09o'
        b'CGGS5QJXEdHchWopTAmI3VoZY94OVuTS4hqOqcI89Eb7bIUWLxg2JGHQYk6PV+lgm2qSRQKhTYsuEeNdZ1t8EurkC63Hr2G9BVT6rd9DcuChRpwnwecJVqgeg8FwRi8S'
        b'Yep5pg+1J+M4Llw4TQyDseAR4gSkg6TshlbDg/YnDHA8DGrCD0PBEZjXw06fm+eYe3/PNUOoDAkIg0FrnLm5ziucOMcQnclwEoFlGFrPXRVio7cLzJ3cfk3HC/OhFe56'
        b'RJJgLqCD7jbTJ3AXY68YlvSxNtRUbw1JvnIjqL4QIDlJxLvoctwtkci47gzUOUFhgNE2IxxIhJGDRH6lCVC/BQu8hJinfAzmow5Bg3c8THsEwQKUHnL1OnJjDTYT/hNf'
        b'7KP5SgRJhArdOKkCnUQIZSZEMFMErDtk1sAiVJoTnbZZw0IuzqZ5EN7eJVFXhY3uadjtSTwlL+p4NhT7pBANdOZCY64xYdaDqKs4GGuGd4kJdhGjKN+Ht0/r70ZC+Wrs'
        b'9SG9iJC6z3IPraGdfus5uCfbR4/E4uE1MB1CaPgQZq7uJKpfxCEvrCSwFZHQu7dnPVPJ0qEyxtKGoSLWGB3guEE3a1sHHfHQGKGfkxWIbTTLDFFWE9TG02oGSSMoFEFV'
        b'JgG+0vwaba+VJOgwCc6MM9DlhB3YaxasHUKC4n6CCXZFY8NROt9+XDgP7eG0xDEPMgV7sdQVbiEj9EVsDKUhSi7GZTERhPlJ5jidSgxmCousvM9q4MTaHd7H1wVBSWYN'
        b'w2sSJgcIr2kLCh3CHh8Jk7CKdIj9e+3h4XaYyNK0cVVNJxX2rvcprD1EW4FOTzrgRZp5Op2ANMuY0JlNUOyChTsk0E5Tl8NE6rX9Wuv9YRHHI/AePTNG/KPp5gbIsz9F'
        b'p/1IaS9xwkaYs9t9AIcvEHk14Fw0aZdVJMSGSD4/QOJrhTcdsd6AcLb00AXo9MPGEwdJsFZHH4TmUDtSOnphwY1mqyKx0wmPdYm226FrA3Tr4aAvVO3IxlqdwA2xScTv'
        b'8lVZ89JrGpdgwtrtcIDZfm3CsRFo0HFcp0Rga9cwcMWZDVvUxN5YsJEgmWdNeN+nv5ZEfBUNO3oeCy9AvScQd/IgQdhJ5J5vgfOXsA079qUR02qA+yROeknXn6CDEh5z'
        b'PAUV1skkqFthJBgLz2L3eTcoD3AIJMgVQplXwtpgn+NMjym/cAP6I2yxIBLyDK9ZYhMJrJpzOJtOyNN4HIfDsdRxOzSJCNPuBWCJJ+HXEnH20dgLZJVUE/cuMzcjKM+E'
        b'Y90+LIF7KXsJ+gPOUOxBaNOLNTvCjGJ2uwZHQG84Pko5T6y5c5+uhrXLHiNzF1vi6zNaWGZ4OMiGxOGSNbSF0qi12oRbT5Kg/MQpIpL589C5BfqNonAymSZspW22XyRS'
        b'6DsXbUzcpxZGnWBck4BZjk2xULYBpi6kXjQ9AEOJ9NAoNMcQf2gWJ9Cq8kII42dc4M5+WLQhgTuHt24a4RNBIrbaY2MWVGf+hKkRnWeJjRBW5idzSLlISJmNw9E4cFWN'
        b'1J5Cw2sEwPwt60jFnbHYboB1eqRLnj6R4wvVNzdYX8uEYonZsUtaJ0iE97AfKNxFrL+R+Ai9tp+pTdf1tGEkmw52Hu+dOqBJ4nIWlnTDsQ+bE0jc3lfGvExsOBkNi9eS'
        b'6avWiAuky4xx6gOQ+rAAi/GE/dMRZliUvgH7thJWdBPtDJ9MxprrlsQd2pi+G0cLKL3olmSmSW/UEOdoJGhUBIaRojeUG5J7Oi57k1YQkr7ag32biHHfP++RrUPArQBG'
        b'utXwKDnVwwBmdaVEJvnppFJUnwlyUbfCiYggLIDGEHpkFm6p4pB2NJYeZx1i6eOSVGjRJTvlFnRk49QlQtSJbVr2fsSemuP1vBOuepDlxCLNJI0fYcXarUoEy4btpG1W'
        b'mxpBfbLlhiNErCPrcM6H+NZtMk5mSCTPJ7MMeaxNs8b+zWTdDuGtXGjZ6kjs75EqTVaI/S4+0S7ZG8/HEJnnEy0UZhIZtGhA7Q6suuyCrQHWRAnThvoZEcT+HuPQWRy6'
        b'QETTu5EQsG0P6SwPXaAEH6UmQ4+UTPBSMpVNtxsRu2w6QDx+et9mWnZ1HNwmpUEZB0JJVpYSntZ5XMYHoeZYpAT1OB7NZDThWotg85X9qWczTI7R+U5usiNiaYeaKCm0'
        b'eWRD+WYsUz6PFQnQ7E7PTsEM6ZxNWHaKhEQFaSZtRgE6cM9vy81gws8RHMsJSyRNsSnE48geZpgNu0KfZ7rdeXhIKHUnECavxRvFEAdq1iX0nnHEnuPXfYjCuvy97Qgp'
        b'xkw3Yf62gIRQrErBKlsV/lbroDss+h+FPKmyQLhNQObdEg7x33QRcs77420da9l1IQ8s4r4xyYYWf3uGZiKB8KCAqLMXlvh3emNgyJ9FwqdUBMID9FUG3OebNZeq6jC3'
        b'/EFVoUDoJ8BWI1nGij3MXsEKh2ChkMuL6vDHhUwfMdFdcdoWglQd3ibKaDmoRYAfv6Gx4Zw6NO47oSsxJMlU40T40E2gamAq+xa8ddQ7EIoTPExsidc8xD7zHBJPXdBx'
        b'VM/zHHHwamiLwDukrxAJ473dzOlCtndNtlOmFwyZME0vF/qiJViiCV3pEqKbOljygLzTx7EhiA6TvidqLDpCv/bCfQEx2JJQA9LhWrfRmbU7n7Ui1MtfRwbBpF0YjXtH'
        b'EExzFkUTTx0nEVxHh002Tvx1KHYi8VpzEqq3kK0wRShxlvSXmi0ExVGodSVDqUh6KRCe+BO+97Ki5oRZUxZkNBWSYVbqansdSlxIfZsnNjFB4qATJjaSQjwAzXuj92aJ'
        b'8Y5qtC7e9b0Mg7vxUbr9Bpy7iMNnjxrDoOr1zOjA9EvEQmugV535DeCuhTnmE2CHiRvlE3vsP3+WxqokeDaGGSUQ1c7REqp30Vb796/ROK2FHZHhnOXVIsZCZzJk8ggq'
        b'o0iMdMkZKsU4EWYX7IxFZwhxuvbhxBainPsu9sBuVwxC9T7Sh+7QfvLSTTOVSDJVZ9AeemHx8DlSJutYynuHKo7EY7UvNBzAzlCyqSrJeFlUNcaK8I2Rtl5rseUAjqhB'
        b'Qzg0pBOxLNrqZOJgZHo69tNPba42rbhs96kzZEaOEjuuccEpL5/r+jFR8GCrNszq4D1fIq6CPTi67SjR9yAUI3PulOmSET8D+Wug7RLxAmg84Hs26Fz66bOmpBOVkjCf'
        b'M92L9enbXIhZTGWJiUf0wYijCaF8HA7vIXOg2s4QW0wZKyeJV7L9JlHqg12kMJYxd5RtUAxJVHi4DVqlhFMl8PAclCSTEO+FocNEw6P+N2H0Ell9HXSqo35unAfmsZjk'
        b'zL1zsWRR9cGdPaZrb9iT6jkTxCwJrImBBezeTv9ZwkVLE2iMznCQmpHONeyBjy5qY742PhZCx0VSr2eSM1mFeQf7Nc+6ZoiPjnlYHtTNwhETlTVXsCuKSCM/gjjz5LFz'
        b'WO5nZOJJhssSNKUTJIs1jZTPXgo4Qbyn2mUNIU4jjJtj/w4z/43uMM169pScMQt2jPRUJaH26PgpzkczFbyBJmmBut0Ej8catP6pZGJL3SRTFuNwNhNmbWEcKtxZwe9+'
        b'bEumP+6k4ZOsndBCco1YSDXD1R6YtIOx7Smk7Xe44VTUOQJzceApU6ZuIvHqvtNC0vkeE1XnWxABTfqQmOtQssD79sR9p7HH8BQMbCLWWgWtB9MDSNHuiGXtfg8yDjsJ'
        b'+bmJpOGvPUjKQo+5LvNtBeD9HAMvDRhKukDMuJL3BGREEglUX7amZZFMw64bxArmLIgS2snQhfuBFwUJWHIokXhO28VDsSQcprEtmlZYKyVJXEhvFLFMlsgoGE88tgdn'
        b'TPXgyeazhAp3jbDP04kBxQ4HTaNxLp6whin6Q2Q8PE7HxYvK7nrYvHYH1ganEk+rNMRuAzLB6q6xMgOwlEbqzswBGNQP3nrAxYrkbyc2hKlhl08Kwb11q03mett4k2M+'
        b'BvrYaXgz000big+Jggjjhwj9yqD/BnGCrsxTvlBxjvhsgT08MoomunxMVDGbezqJxGUyVIlxkv4eIT1vTpJF3LZt//Uz2BfmSGypBYdtYeHQRRjdYH2UuEIdO2M6hCfE'
        b'2JqJO4zq0zYWcenGsQAatHcX1CYZ+wTT3PNrCR4LXvDIk1hwySXlTQek9Fxp5o8IV0MhTwPaQ7BCYd2eptlvQ9PODczADTuhKYQHBlgaBOMqjjB6TsUEBpF44MwuwoJx'
        b'11O4COVO8a6EojWc12RokyOxMeana9Z3gCLiaoSjxTBB1gE+uRLsaEvHNYyPPTxh0AKadS3WEPArYSaKaLXngDvJR3PiKkPW0OyKeRuJ2U3ByBm8FwqtzmHEdEqOQltU'
        b'GImE8VNMRenGrrB0G2VxnDs2bsO+bCxzgqnNJ7EweTv0JhwisdBLO75PemubN7EbmAvAcocwEhytdkTMtxw3no7Dvj3GZ9PxSRAhWyOJjqKdRmpwLyEZJoh3ddAME0Gq'
        b'RANLqcFkt9cQvlRCbw5tmoTVGuzfBg2ZJE6aghIIm8hyaXLQToYiDUs3HHWNx7t+JknwGAYzsdUV5j3TsYlgdwcnTq2HpZOCvXhLWw2XxLTK4kBjmFNm3pEeV+iPNfGF'
        b'xiNr17iS1VVOW8LRfcTGHxNKjBMNPCQ8WEwj63PEkIDeHBHJ6CYmbiux1Nui856xaVrw4Bz2JwQHxcdcZLfedWgJLSRuhzVwyh8qIqHplL0pkIVRgLcTtCQ4chLuGB4M'
        b'v3ANO/wC1+3Amu04uS7uPFa5iJjiSkyoiKzoe/g4IPs67b4iQo9EVxc+Wa9kDY2GJ7A4EmY3nPG5eCjQm0i8cj82ZOyNwrlNxJPGWJMEsg5VLhF3GNEMs+A4DGPb9QTL'
        b'u5E7YRIfbLIl0r2LPVeJ4qpgYitLNtNXJQE5lHrGmOatiMLFY2l0PLeR9INqdZg12OdEXK3jquFNXRsir2biN08csPQSdOxJIj2lEeczDzOVphUrA1bgNtm3s2KRKQ5g'
        b'zUHddOg1UkmwIbbbThuaJKbYuEPod/IoM6Ai8VEkTmsTaT2g/Xc57NPBaouz65QIyVtIgFeSFj+SQxBv2HlSPRTGdmPLGcLvFuLd85rMKIdhi1ACOVnWUGWCRSHeTPcx'
        b'pMFGL22APmccPWKHpND4rSMQVWyCe04biEIb3KHVmGDTmkFS5340TJ6xIExvEZ3YuRZ6zF0hLwLKtpECvJ/44YZQ27XEKWrjsFAdJqPTb5LgKoSZsN0kVqajGROvUJUe'
        b'c4FBrT3AmlE0m10iKM0ZYHesMY6pbc3xdE8zhfY9MB5wnRCrjyRfLzab46zUDwcNSNW5Q0J0IY5kQY6GVzodYgfraLFprxR69yntwNEDVjDgoYFtUhzRi7lgBv36emlQ'
        b'Z4yV/rE0UD7UO6g6B9KBkqZBYHmkZBmYenDPiQQc20S8YZDIqC18Ey55E/dqgvajnvsFRBvlRJikgxPvqoVZzRgs2UXSmXWQ94KJNepCYgYPL50nvtdHR/KINX/RNz5N'
        b'Qvw29KjBrTgodsVBRxIApTeyoHbveWR+8m4BTF/ct5ZYyjwUx9sQqd03gy5HovNmoooJsqrbwtXNd+GCKTSd3Ouf6kMidAAGcFSJXimAaUsjVzI7eqDfE4aULYia2mDJ'
        b'2ticdNnbdlh9HasZaMquwJQ4dcs++rTGHbptTuMcCUps1Ldyt8KOvXA3+gzhTSk2ppNgWsw+h+M73UOhMFFKnLHeSbAb+iXZRhERBPXEOFyA2xEwkUbacw3pb7cJWpNu'
        b'xFiLrFzJLJzDknQ3/5j9xAhKCU1HQ685EnyntISEfENaTDmms2yOysjOhUfB9GcPtASQkX4PxlN9cew0JxlncMH9nAc0bSWpSRawz36c8SP9bVwzagcpcnfDiDiWVCNI'
        b'W8vbFIxjmWIiJOPLLJsohI6VxDoR0iIu2BMzvkvYOeuKM2ak7J7BOo14Lxi2wlavbVAjJgHXqc2e2K8XTzbj42uxvr6kDRT6hbpaYnFOCinYi3jfk85/ikh8CJrU8fFu'
        b'1UQSPcNC7ArBeetcyCMLsGGLt65mCDZGcQG2Uebuv3kN6mGe+bV6YO4E7ZJIpZ/5jEjb7YN+XxNsvnrC5uw22l8DDrlj/k2swgcWJCBLz8O9UFK5HjiqxKU4m8GEL4k+'
        b'OrVpvO1M0C1OJDpY1MXOC1BESsEECZiqHVi9VpX22afuiGPX40gJLI7Ihlv7STJXQacYp8zUsfWUmbcZIc3IVmW9dfjoQChU6xxUI945j3k+pNEMM7a2C8cEJMMb8M52'
        b'nehjUHTOf+teaYIGLuqdzrEhNk+quUfSMbiTinXOIWRaM0102jXuOuFImQ1M6Lv5Ex13mcK8BsyeuZpohwPWxLkeYisUXcT5bA0sPhJCtFFEpskA8Z0aMls2EsCb1mO7'
        b'loY4xhQrzibEX7jkgi3+OsIjJvTeKNSoQK2+KdFcHTxM0Dpqvw1n1zMHKAnvPHi8Bh6yGN59i3Vk9lVGHNhP+nvHToJFF4ytc0yGmoDNRBlVZP1kZELzTjqD4qP4wF2T'
        b'NPgF0g3ajuSYYrfWDWXaQa03tBiqXyeiq6W/amDJPjn8KnRsJGZdaLA3GB6YQZvenv1aV7DAD4ssLqni/ZNQGwcdMEyIVHUijDlN8X4m83nRuS8Q+50gMVGIvU5YeuPS'
        b'RhLVpAadomfbg2gzBadxNseJdDPoI5KpI2ldqhkWkXmWiPIeMHHC+kfupr0t5bICQrXRpHg/SCNsGb1iRkg1nIslN6GMWDlpHwVnoCmTBMrPRKxgM9uYnBAOMufUndMk'
        b'iYmJJRywPKFrhdVEBKetrtHXbeaxkepm2Gu+14oz8sdiYUTVN5wmmSUtqU+0G2fXwhLe35OgSTsqwk4psCBw/ll3qFWCRjPi5o+vYLM/dIvp136YjyZxM3CDmOMdoqd6'
        b'OosajfXY40fMdJhAX4m113EJFtyNsGw3LDhit1UgViSyYNdR5q2KOkbAKdpCbKVMSwmHotcQ2s9ctSQyn9sRnEL41mvoTGur3W6CjZs32GLrliOkNBBpeBEyLBrF4QMt'
        b'bNm3Efu0yXQsOg+FXjh3EIbVs4m91JEG1EDcuUdAGD+vAu0WvtCkSSZC33Zd6PLcAc0upC8UmZ00xoHNO1VUsPS4F5ZpYoHXMTKLF5xIySpxxUndVHywTcvfGbpdsM7T'
        b'7SABZRpalIjoe4ndF+eEW+qxu1hzrKQl5FsSqo8KSTW7mbWDDqXuBBRpckgxd4k4+NLlLcQN2rAkhaDWz7jAg+2ke9TFxEHPXkJn5oWvw3JTnN5Ndk1NLJSqQHecJQwo'
        b'wbiHG84yAx3zjhMDmwm4QgL9iYsKacw9ULkVCx0IMOMm0J0LTfqElaWbWDRZ+brK7tiTNHK9uw42ku6gcoWpQIWGu5LJ4iONvoAYRA30G2LzYdNsllgRQpBrgfmLOjCU'
        b'ZQ1DjvDYG3pslaF5IylZrWdg8DJZPaPQ43iJGCSJ7t1uKTth3s8mDbut4a4f9NtvP4LTyiRXmo5uJMO2Had2kJQbZETSHGJw2IXU7GEnXAq1IqxtOhGucyn35Jowwp1S'
        b'zNsVQHPc3bx/w8FcVvqm9DIOquGQLd/fOM0J8mV1cA5iJ1cKB8f28F6le9AJVRnO6ZFXZcXaAnL5C3csFNIqe8vkIveSLYxwL/nDYzdW4A3qZO9o4DTfSLmR4DXl70CH'
        b'1i4UCPeyDrK9ytxXl5Ow3p+MyNvQKhAItwuQOUn4Qk1kdrVwFRnKUtnle6EXvbYzTVZw54TY/ygdaLfMuWZ5ll92szY0+wfT3itpCc70hdo1zn8WQtQ+gBUBa7PoBVcB'
        b'qTgPoJkvCDRnid3+ZAeRpJe542BYixvNhNT0KaywxVJveitYgN0qztw7e0jhbMeKwL3whPfG1eBDuMOvgDTeXH97Q0+5B+8O3OLu6x1xvebvB5XhNJK9AEtNYYp37C2K'
        b'bJn7Dod2yfx3UGBrK/Tmmhlx19YsLnCt69Q6BOEO3/E0F9iKuY8r1LiPs/+uE+4Q4XSDrxukfkPEPowb0QzXSopPFrAUNG9uNP6OG9/xGhczcEl2hHqe3BGKkvlvqomR'
        b'0xGSyloqO0P1i7ZiDuYJ1039HYh/VMlPcEyLL69WRofLrssQ7U7LzhCXDvCFyUh1IXJi190KoUp2hjjlJ1sIi/8H+AffhAHZaRHalXDfHCYWVU/nBbVqsgMzxUZ6i4EY'
        b'ay+QOKkgrNOTHUuiDCtG1p+kU9nlITuUALxjK+S+yUk4T8BfCpQBHx5BQ/zUqQ6ljCUCi/Y9l9y6t4INj5v9xydvSFVvHfKPf+s/n3zyjyfjf+zccUS5L8ei28rKTvfu'
        b'wQiHb+x5ry7YQ/+zU995J6j8l6/tnGv+5PqHVz6Z87+Z+CDrxr6M/vaqAuF78GnOx7kYYP+jxjHd8l2ijg8sfmKx/59+Dddfu3Voa5/exT/v/NRpZFvsaZVNyu+V1IQ0'
        b'aRf/8ca3f95QFvfa73/Q9GvnrI+/826W5Qd2Pl2b+t7RiH2/rkE3VesDLwv8e6n0GzVJ3QahV/Qf6o/3FXwz5KeHdiX8rjvZMehM8H+6N+xNGHTX/6XtyG+qLUNCfm1z'
        b'/Dtu33Yb+4ftzomxr9k2uL3VU+td7LLzXe2GjfGdJgc3twxYe9jtOZJ57IRz0P7SmJnqsZ8ejzjxyeb/Kp9dUHu77Z8Fv2z59vzvlN76TaPH1U27okp6T30tquBqTNSR'
        b'rKifVfWsCzvxVkHY9vMYdsXk9bA3rX5b++e3Npr/suVIwimT6Ir3xy5U6EhrP/4f36kfzaXb5/73u99sPPlNpYysrtax5J8Z//CfA3vWGv61s2nx4mJWQEaggWTP1xrs'
        b'//z2D92HI36nVHeg97u/6qu5Uue54VNX/5uvSTfn/Lj42z9z2Hjg/2/u2qOauPLwJDN58EgI+EZE7LqWEALykJeCWnkYQwC3Kr7HEAJEQhIyCVW0VdGiEBHxsb66WqiC'
        b'SkUQQUXdtffW7T5ce1z0qHNaTz1V665atqfVHqiue+8dUNvuP7tnz2HPnHyZydyZ3Ll3Ht8vud/3e77MItu+d2n3w7rfXKCkOmVSXcVFpj466elUvgWqKv+o/MF6Y6pd'
        b'L750QHu3Z9ftE1ebTxzpHZ8+cdY7c3qSQ47dGtN3WTF5c9Tmb8u6V2hKUO2OZ7bFfHKZmdAbfNSRfr46kvPu/vDBs+XS9jvRf2gP3mre/03QvZvZfatint+81nqVO2/u'
        b'CX8UFr6sbuVw9/73e2zGls6/jg67NWPbVWgIt6RoR928F24JN+5pD1/V/lnYh8uGFc//RBrX5h4L4spaPckPv5x2feP3BSnlz2Q9cdf+1rPoyyTP90//9Nne3Cuj1z/v'
        b'K7TMfdoVNeLa8QtfpWZdWR/9qSdj/4JHvTn3Et+5k3gl+Oylb/9e99Wqy6NNiZLHi9M+fS5uu5FbUFyn9hZ8evZpcIiZGQdqhAt0CzhZREb3YyoKd/jo56X8bHgwNicj'
        b'bihBoKvgR0I/VIbLfJFIooTkBYLrQkC7j1MRhEJRBWJMHj+n2xexnFM0FVTO4D/tNpO8QIWwqRwVE8q8BTvfKlXgX5qk1MhpNLpne+BBYuWCAsBmWMuV+Za64Sk/UB2G'
        b'mISfXOENW/3QXVqtZNBGazkX8ev0oDvSdq4MHggeKP2yLKgRvkNKGRgpOIOe/UQ0Qc8HTd5DfF7sUA6bxJErUdyLR+Gie8BZcIhDId9xeFaO6neCQ/yh6t/sEnZIwW/d'
        b'4DwR041Sj3/VfAY2wJofGdA0SLymx/48mVDM4A7WHXRQB5HHz/8LCLniWdZqN+azLBm93kjhf8zEYrEoVhRChHoBYjnNiOS0VIwmWikJCAjwUgWrZCppgPfQIYx4qG7k'
        b'a3FrqFixKAmPY2cYtG3IGio8cEIqXmbjRHJhhLspVpjLTRGWZSMXBE5X0Uo6QBWxhhqfLnyqF6vFYWINQo00isyRyVeCZYGBr7yckS/GgNPOP+PDeTkSPnrwu3rQTjGR'
        b'0BhkTDpuIpzskVPibr3ueDX/FtZ+pcSloBisFt0WqxBdr8nORBymVkYpR9FjwDmnpeDJuzQ3UkRRuo66STUZWfR0VVrz6xnZzs4o+bg6Rj4kNUHqs2xqnrHrfOu5NkYT'
        b'/vb1Rwnyje9/7nv04g+HcuuHT9L1HfTbW3Xo8S8Tbn0cc7bT1clcW/TAsfy+03i/9IhFz/Y+bF6bPMxpLhgz6sjuJTtbux82Bo3qTIi6dNq0m1vUvfPdsD1zLq753ZSb'
        b'88YoDU/cXztDiiYtudvll5/9eIG8vLH3Rv3dL5IXrvbhf33m8Oeavxzbdawn/p9N33zX811+6MblH5+5WX1n/iNH85mJt303RJSr7kNAxVWO/Gidx6usTeaX8sT/C2qc'
        b'snSDKTXhI3Xe+ASYGOGoGrrUllt0OzD+dFplkOTrnAaQHPyPTSgW6U5q2e6+8OT37zQ4nvnEtyx++HqdeizxldKaYAf0LImAVdnZRFYso3zACTE8vCiQeEcpUTx7VJ+t'
        b'hW2LUCSPCuEx/f7wHA3q5fA9UkQCOs1CV+hjUay22YB/CEM9EUAHF4NOIcVCI2gC72EbWIMMrB9BSRmxPGCKoJhpAhVgK/REIsL3Jh6mRcEPdOAcqVw62BeqgVtCsSp6'
        b's4jyigDb4D4xiuh2J5JtQ8Emf+FpB9aJJBSTJQKtErCJ6GmWwA8iSGq25lxtvz2ZElbTWWAHOCgYlFVMBB5SYlfggCFcNUXUdv5w/wxhv36ZBh2sUesYKgBup0GXEm2M'
        b'v1mrhwf0s8KzJsWIKBncBhoy0C0GHBV0PnX+I/TRMbrYN2GNvt99bRw9ee5Mckxwu0OF1+YodAZhpRK20FGwDW1N5PSVhXrowbl7a9HjvxUFCLNF4KxzqdBYngnYyQvW'
        b'GLCSkmKiRCjk2RVKLOjKi1ZqtLAmc8gYEcWUiBA/7gwl/cO6scUxohX46wyIdp9HB81Qo99mQEX8QtJY4EAh7NSHwWO4TuiwcWv7qMUolKgIIrXOxKOJONileaWAt04M'
        b'Wme/QWiFAtQvh4fhIR94wg92cKAKnnLAk6WIXigQMfkFI3OrBI9FFJ0v16N4vosYxeC9UeiE2yuGDZHwiOBleBQcxyEjNsyDOxYPeObBUyoXziMOTssUenAsVKclVmjE'
        b'DTJbB2ois7RqKZWRFg93ylb7J5K2nIEiuQ4f2ApPisAGWEeJ0As2UuMFqfxJcDoOjy7H2v58sJOSrBbBg2BPGSFT0cEuvE6LzchLtejUqBIoV6CbAZUGUE9aBdUDtKNG'
        b'r8bOjIhpeU3Ig3vE+C/9cWQ9aEfn6gYNOAjWztKGG7Soz3yH0d5gC2gTnPp2jDXoUd/oS0EtugJRj9eiYxgSQ8P91GtCx1SUgQ4NaBfPDA/DGlfcL3CrGLbMQ6QPh6Tq'
        b'DNComYViIv1qUEnB3XLdQBaj0MG/of+PHgvDB4FbvMw/7cDPH6WcqP/lZBpKPN7k/SJULH7D3m7YXy2g33ENlaRt/7mQbmCaKGjLCEEI42mr2ebMQZc7L3G5HVYzz1gt'
        b'nItn8i0mhHaH2cbTnMvJS/JWuswcz+TZ7VaetthcvKQA0SP05jTaCs28xGJzuF08bSpy8rTdmc9LCyxWlxktlBgdPF1ucfASI2eyWHi6yLwCFUG797ZwOH2w0WYy81KH'
        b'O89qMfG+aYKc02AsRhv7Opxml8tSsJJdUWLl5Zl2U3G6BVXSKy8mzmzDvlq8wsLZWZelxIx2VOLgmfSc1HRe4TA6OTOLVmEhO+9fYs9PjBdykrD5lkKLi5cZTSazw8Xx'
        b'CnJgrMuO2J6tkKfnGzJ5H67IUuBizU6n3ckr3DZTkdFiM+ez5hUm3otlOTNqKpbllTY7a88rcHMmkg6K9xpYQIfjtmFjrZfUS2jvUGc6Jmd6DDMx5GDAlmzOLAzTMegw'
        b'xGOIw5CNYQqGGAwpGBIxvIFhMoYEDKkYZmGYiCEaw1QMBgxziKIYwwwMsRiSMWRiyMCQhiEJw2wMkzBEkUpiteGv8Nw8DNNeaCfxieT1gkb1LnyFRpF1ffICdKaYTUUR'
        b'vIpl++f7WXVfYP9yiMNoKsaualjOi9eZ87PUcqKC5GUsa7RaWVY4ZYlO8gH+XCqkbXVexp/MH+C7P0nnzcunoH53W80peInDeVUZMeIG//2lM3cosUr8F1RKDN8='
    ))))
