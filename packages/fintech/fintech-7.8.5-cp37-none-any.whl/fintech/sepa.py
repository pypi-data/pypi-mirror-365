
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
        b'eJy0vQdcVFf2OH7fm0obigjYx84AA4i9RlSUDlIsaJwZeDMyOjA4xRY0CipYEGM3akRj7zWa2JJ7s1l3N9/sN9nd7Ga2JNl8N303ZWvM7jf/c+97M8zAiCTf3x8+PN69'
        b'7757bjn3tHvueR8gvx8Z/E2FP+ckuAioAi1GFZzACfwGVMGbZW1yQXaUcwwR5GZFI1qqdKYu4M1KQdHINXBmlZlv5DgkKEtRSLVO9XBJaGlWcaa2xi64bWat3aJ1VZu1'
        b'xatc1fZa7UxrrctcVa2tM1UtNS02p4aGllVbnd6ygtlirTU7tRZ3bZXLaq91ak21grbKZnI6Iddl166wO5ZqV1hd1VoKIjW0arjU/iT4S4S/MNqH1XBpQk1cE98ka5I3'
        b'KZqUTaomdVNIU2hTWFN4U0STpimyKaopuimmqUdTbFPPprim+KaEpl5NvZv6NPVt6tfUv2lAk7ZpYNOgpsFNQ5qGNg1rGm5JZKOhXpPYLG9Ea3SrlfWJjagU1esaEYfW'
        b'Jq7VzYNxgxGw6GSFVd5h5eAvA/560GbJ2dCWIl1koU0N91/IZQjyouI0Rts/l8cg9xDIJGfxrlVkK9lclD+bNJOWIh1pySkv1isLp6LhWXJyPxOf1cnc/aEoPkNu4Pt5'
        b'OSk5erKZbCtQ4NvRSEO2yArxRnLHHUuLXMBbJtASirg+SC7n8BEu290PHgweRM4ks7cKdOE5pEWXI0cxZJcMvzQHr9fx7l705U1ZMXkZI+Fpelwe2V6Uo0CRA2UTlfWs'
        b'htA+5Ah9mkNO4jsF4mMNuSgbQfaQ3VBDHygTn0TuOHPgIcAh2zi8g9xFoTk8vuxWugdRCC+4EsPI1Uhyw4k3k5t15PoyvDUyAqG+9p6D5aoY3KDj3Am04GWukmzNzyXb'
        b'ZMPwViQj9zh8cDTZDI/prJvspXn4QiKMw5Y8sg1vLiLb8Q2ysygHt6QV6nVKNCtLVV+Jr0Px3qxjeDc5R65Bq/KLFEiONyrqOXJ8HjkLBeKhwPieQ5Nz9SkF+lRuItmA'
        b'wnvKQqH0AXhKe+4iZ8mJ5OyUJLI5n/bqADmLwsgOnlycRm5WcX4raqR36ndQjAzER/R/xcimxCZdU1JTclNKk74ptSmtKb1pRFOGZaSEp1xzCOApD3jKMTzlGZ5ya3kJ'
        b'Tzf44yltbJ9OeGoQ8fTLKBX6d9UAhLTG/N+sKkYsc0qyDO1Po3fG/K/Vg8TMfw5To75jBkOeMeXNsUPEzJ9oFKgtH4Z1qtH2Ws++6AyyhUJ2c49e8r8pd2gRen/41/wL'
        b'I4omRnC2EHigTjrAXVYhbXqv2lX6+rmjTyOWXR//deTuSC7xS/R0/sXYCdYByIPc6XTFHCHHcQMsma1psxMTyZa0bEADfKZsKdmfmFtAWlNSc/S5BRyqjQyZTFrxJvcM'
        b'igIN/chxp8uxfJnbSW6Sy+Q6uUpewLuTyRVyg1yLVIeHakIiwnArbsbbMtJHZYwZMXokvokvyxG+tyCEXCDnSt25UFE0aarPy88tzCnII62wYLeRLYDum0kLNCcxJSlV'
        b'p0/Gl/BpfL4E3r5K9pFnYH3sIHvJLrJ7LqyQdLwZn4+IIfdSfZhDx19FVw+djHQvLZNZZNLM8s0wl2tkMLM8m1kZm1l+rUya2eqOFEjeaWblhQ465dYnfnuac46Huw2f'
        b'L88zLXz5v1+5vOPK3oGKB2dN816+FfVgwcvXdxzde7TRyjlVVRFk2smUuB3ZG/elyxb3Rrm2iN7339MpXHRJLdQvhhl4AW+A7rfCKkXy8Ry+gq/iA+zxRHIGNySnwvhs'
        b'tuObKRxS4u28Ht/FV1yU0pCTA8mxZH1iNmkjd/U8PH2W15OT5JQrDp6uIZdjk/WkJX/YkyMUSFnBkQv4Zj9XT/riTnJsLdmKm53Z+AJC/BpuZtlCHefhE3U6mYN21+/C'
        b'w+Vhz0kWh321uVZrETlRqtNcZ5rikbmtAn3uVNJBmx7KxXAOpfclndwTUmuqMTuBa5k9cpNjsdOjMhgc7lqDwRNmMFTZzKZad53BoOPbwcE9xX4HnUmHgl5ofRT3nBoK'
        b'414Ur+R4TsmujMiR5wrwXnyHPJsMfeUQj/dz0wG1L8ys4jtgBptMyleAolDckFvkPtyQdYkbizuu+tBOuNGj0E0zBs3SO/PxHXwI2k7OIHyqMMYdQ1fOAXJmcl5++WAF'
        b'4nSINFmsrLh10HhyrciGz0G2AuEbuDWHcaAKfElHthbhvQgeZCFA/pZQN526p8n9SWEF+BjZBw+iEb6Nz5EtDMKKBdOSC2BF34EHsxE5mDKV1TTDiduSU+vwdiXiFiBy'
        b'ipwhFxhoctC1hOyaHYevQ2I1KiC7F7qj4XaWcxHZBYOegsbj4ykcuakLcVN8Infws+TmRBhUshEBkh4mGweSFvYKWT9x8lP0wQmUO4+cGFfDIJM9Y/rj21AT2YfIlllk'
        b'H95UzSDzaU8Sln8TAcdpIjdNKYx/kBfI5UX4NowvOYyAsFwgh8kGfJH1exZuG0fYo7uUg18nd8nOHuwtvB/vAGpwOxKetSF8C68jbQK5xyAZhuCL5HmeCjj4OL4RRvb1'
        b'ZWOlHIobSqGy4Qi6cXz4JHyMFZ9Erj5NdgGqpMPAktPp+EUnA14fA/i1i+xLnQHPcCsyAIxtIrM/bH2KXHOSa8s5hPeQezw5zQ2Btl1lhMJHm3h/ckJX9mJUj56MWsPV'
        b'c80gFzrk9dwz/DI5lYPY0hHXD+/hU9M9XJWOa1+JbE08DJ1kszpdVfaauinzaJX0iRK5qRS6ijT0yyMtTPKonc84eTbZja8Bcd1cVEi26fALsowMvDUP74SGh5HzCPr2'
        b'Uhi+PI3ssiadmsQ791A06/uzodvvahqKYxt//kmW/EdHXnnlzR9/ye1vCZFtfvOCaVlMvHL/qK++1Gj2jd2zdcFv661LVw7bNO20vN/gNxKcb2zQxb97/S+zejTuy1y9'
        b'/+2P2l7se33WtcWWWz/+u/X13e/sP/bjD+blOqt/VLVjYe3t5Al/jmqesyD/1ROxzj8sM+/6yDNrwJndfWrf/aB14aLeD787t/H4ryLfs+tG728AoskW/AbSsjQ5VUe2'
        b'9O+RAv3G5/mR5Fl8lZHM2CfISRBCSHNOfqEChQGePhvOk8P4fk/x3Xt4XQ+yNQWkswnleiVSLuIH4/3knovJVVfZqosBIWhrGtkCshcBLpOrQD1GychOvB03MBBrlfgu'
        b'UG2JYuOT+Daj2uRmZSfiqZN3pKaBE+kJM9dW2QWzgZJTRkiphIqy5ZycU0u/ci4UfqP4GC6KC+cSOIfGj8ByTk9ord3gBFm/2ux0UI7voLSpc0t4RxS9j/TRVVpNjo+u'
        b'vhjjT1fZaFwkz+EmLypJiHSFk6PeZKd8BT5KLndBYBnrDSCw/2fmGyKKVXOfjEGnnUVwZ5zUlpoiCksRednofPQQDiSopB2zlqGZLHdGZDRKnJ2FUJ0xRT1xhFj0/tow'
        b'1BaZDAqEMfxtFagPjFRtlONjI9PlZA9QXIR3oUq13PrZ8LO8cz48/cPKv35m/NRYbck3vW5J3PvxussHrs7fIpTsb+w1ISEudHR6ivCx8LExJUN2tdfEhPiMuIOZQsm8'
        b'koSKA0MyUzbFzonKO0SlgReVAr9gTCmTAga/3XOdETQGESkbSENfcjWFsnIfG9+Nb7iobIlP4ZfWJqfmpCTpUkEqI5vRE4tRgla+qKJSoguPRbLoqmpz1VJDlcMsWF12'
        b'h0Hi2WzeKxIYqmngCqgV7Ydasiqr4FFV2d21LseqrjGLklRHDx9m0VoW+CCcCsCsJNYleSYgVTZoOHh7USpIm5uhX2l4i5U0kVbg4ZPxQSU5mY9vB6gFPgxjwh0HONYu'
        b'3HEMv7opttNGDu2EX4NE/MJPxSCqUabXnhv/RoJeQqXbdVFIi9C4dMuF7MuFfVEZy+VsCgT/tenDBg5sHDtFRLC+FUw/ReljJs34nSZLzNzHRSCY6sR0y2F71fy1Ymat'
        b'JZZq39r0RV9GvFQuFzPfTu6HxtGS/Z2qF2ExsczzlVpqZxiXvnZpbp5jqJRZMBRl09eXjRy31KISMxt76lAxAE/nLvf+99MSoLmTU9A8Wqfp98INV7WYWVKtQuGwDNKV'
        b'/xP+3lMzxcwfTQ1DsCDU6XE/dXy3coyYiXoPQ/m0ZHRC5OUe5WJmXH0SKqMlTQauedhcMXNzbALwToBe2yevKTdezHw4So2iaOZyS1bFsAIx889rIlFfhBLSl8cpv7JI'
        b'0GfG9EGjaJ21bVWqOWli5vF+/dEkWrLWtnz35P7SKo4bzITC9OgJi1YvlFSmT+fEg9QC7Vx0ZsHFxDIx81UuFS2krw98RTmhRhrk96tGo2o6dDlva6IGzRAzt40aCZgA'
        b'deoOyG5XS4C0I0cgIx35ZSOHZEaGId0QJimAJnyC7BibTFXVEWgEvo6vivlbyb35GeTwSDm1YGSAXPKcm9JdF2mYp8DXRvJUux1Zn8gKr52Lt4EadmYkyEKj0Ch8mhx0'
        b'U/pcHE+2pQ0aCbg/Go22i/IjOYp3mub0GAm4OwaNAW7TxopG4/sp/SNHwvIYi8amlzBYs+Jn46MLRsJyGYfGReA2Uf68ZyfrM1T4GtyPR+PJtomM8JWS22rcQk7ja9Dg'
        b'CWgCkKL7rLxBB2xxWwJdHtPQNPwMflYSGskOfCQ0mkoc09F0UM7E6k0RWrKe7KV6wAw0A18nz4qtvgoC57Gynk7oSxbKwg1Pi43Zmwja3d5SJ/RmJpoJAyNS4b349lS8'
        b'i2x0Qn9mgci3Fd8Ry7dVDbSSO07oUjbKBk3zrjjY1/HmjKQ8QvuUg3JAZNvH8p8mNwX8PGhNtFO5KBfvVohmnV34Kt+PXCTXoPV5KI8cwvfFB8+QdXhfn6HkGrQ/H+XD'
        b'yzvZg3TShs/iRryDXIMeFKCCOZJgqSG3SAtM9iZyDfpQiAr1o8SaDoJEfhJkcgAOnShCRfk5TEQ2gPz50sJe5Br0oRgVG4wsd/iS3DpyjFrfZqPZIHbcZ7l4Lzm5KJ4L'
        b'g9aXoBK8daxY9fP4hVB8i9wIg9aXwsydx/vYfE/InY0bTWHQ9DJUVgAiORuyg+RF3EbOTQ6Dhpej8tIR4pAdxidTQFg6FgbNnoPmqPBWll9ODuBT0Nn1YdDquWjuIiLi'
        b'bZgN75iOr4dBq+eheUumiOJ+2xpZ1DS8FW7no/mkQcOK2tYMGww1b4VWV6CK8AmsGUMq8WkHqGdbecoSFkwmV23/+u677w4+LRcJZ9y0QTcHLBWXWvlTQG/o8h0fPfJa'
        b'rRxZW8/8UeZ8C5589M3HNa0Ta/kRCRs+uhkhj1kUkjLi0qi+67aH1clCE9v6nMic9tNNDdnLs3YcGjP6R38ZOi7qVPYf5DnbEt8s+2vBiIcNoVfjf1pxKuJsr4aoX6rM'
        b'zwz88UfNw67mO/6tDku5OuO/VHvnvz/4yLy7P1ty/torw458g+M21gz7/Ms9e5/8x28+em/c18Y3f/brb2tfKv/1z03//t3PYs99VbLqTzdKzw/NLirkM/7sSq3PS1+/'
        b'r9UwXFP42wUHyZNj7fyhK2+aqr+yu7bPdNoqlAuuXTz+dMP+7Phmy5++CFPdnHD3Xz+R9H9yJbsOpNFCsjl/dSlwdw4k1nM8udhjjYuqNmWg592jUkE6OeIVDCxkq4sK'
        b'ibnkEmnMg/V6mbSA5lugz03JUaAYcktGmjRW9jo5Nq4PCKrb8nL6FVM9XzmO70XujHQNgGeF5PhAp1aNL2QX6hOpRZO0ylA02SHDl6ktR6cIKlPIgwkAfpKGRpI03FUG'
        b'KtYyMYNyfCSEc3I+iooafCxHf2N4OYgDvWlaFgUCSBQTQpScI9Zbo04GIoi7qivJg3P09AkdsYyPe4WO5wLMBJTZk11V+ISf1FEAFybYnh+jQDqyToF3Pa3tQt6gRkjk'
        b'J29w3Zc3gsuzKlHeKJ8RjqozAUSxMWXgE8MleeM5Vyj6pS2JSqkpX67RI7ZILZPIfRBSYe7xeiqjLiWN1sOLxvPO6fDwp5mGz4wVL1/ecXTXmcajjWcOjNg44uDR7EEb'
        b'dQkPvnolz1RoqjbvlF9JKNmfmbJsU8UmzWu9lW0T9traer8Rh/47OuLO+MU6jhmOIufiy0wUDSWnJaRzAkZwj5393uLsO10Od5XLDdKmwWG2mB2g4oiYEE4H42nEq0GP'
        b'YeJmnN9cy51QuOvJjvdNNn2xwTfZ6wImm7JksnEAvuib7LRUXVJBqk6fW4A3p+UW5OmX4Mu5oNeAggiMbUsoWY83Te5y6gNFze8x9d4KA6deKdqK6p+whcEqfpbaCqge'
        b'fqCwF5v8rwpGUemkXD3VmPF2dQ6aaV024orCORYe3eix5zPjQjbLVxqXcVWhH0x77Yteg17UnNS8Znkt9qRt76ATsR8aN2mUUU/sXw9ygWZ7mO67F0HRoEOGN4bh/T4t'
        b'4+pQOrVLTIycpJIT+clkF27w1zSYnoEv4KPSJD166hM6qBiBEx8qTnyImouDiXck+E971WOnvZdv2umLm2mFUWza0TcBE08VTyvZOCyoasHmnU06OQ+LHa3CZ0JIM0+O'
        b'dKnEyjpYCbtWYjst+mAzz2b48AAq/ab3j0w32koWloj876fZVJt4uUA51ZjSc5VDzDycyLSJeB4ZbecmzkHW3//uvtxZCE/63n/yXN3Hxs+NDyqrLefNHxtPmx5Y0jI+'
        b'Nc57+daOgbD4uQeWXNNO48cC/9br2rWouFzlHM+Flo58ftz04dMHlo7bMeD1l9/h0eFJ0U/M/7sXQw6Nrsfn8J2y/IIUHsnzOHw1k+xiGPKEi+wFXkW2pxWBkFEIhFOO'
        b'4vGtiSXyMbilvru6aESteaXLILjNBsHkErEjRsSOSJ4LBcZATR48sANHbx+WyD1yWtgTYjObBHhv1WMMHVRtdvT1YQ2tqNUPa/4aoJCy3cPLIM+3kK10NwxvLtIV4JYi'
        b'uvuHhpJWvIdcVVRkxVXJpIlV+OPJGBFP5GyXStGktCglXJExi7IccEXGcEXOcEW2Vv4ohVTZCVcUIq4MnZhBGdvKOIUx5tdKq4gW5iSmeaIhucbwVq0TWUfNPc05KyHn'
        b'ki2/37YrEevSw+XvLi9Jz3z7J5rru5/Z0ba1xFPe+1rWb2K3fvq3h78Yr7+Tnhin+MmbnxlnPf8TVZ+DtxLjJx27NeNPb9xNWlU76cyGJ3ae+k3G+H+NnfTtd3kf/Ffi'
        b'vLeuV018YnJZr77lvUB2YZsItwbzdPtIFZamQjw+xpUj3OSibLg/2W1ju6dILs9ZxuEj8WQnE3cSHNF5dEFuJS1FHEojN9VkG4834ObpTF6ZgdeVwbPmNCBP8oIyfJfD'
        b'95XkMIMW78D3ydYCvGkUPo8A3AZu1vSMrqQU5SMfdUTJ8MXmDhiZIGJkL8BFEFM0gJGhXDjP82o+jnf08+GlguIlICNFNY+yyu2yW/xJWdClAPhKxS9H/0AcpZUe8MPR'
        b'T+L8cZS+kUhODosfmlekD0DQAfiYnByswXuDs69RSJJc6PYpsii6ycICrHER8NezE3IOEJFzguxnaDf3cZQmyhhSN0grIme+dSCair6MltcZ65dPXCRmbjRQK0Bxjcxo'
        b'DK+2RIqZeFQoikUPMkNBzClTSXaNn42mFpgdqxUIXh/SWzI38H1BnW1bGFFsrN+TnyRmjh9O1fiXc0OBUYZl14uZs5XMrtE/XGtM8USNEjMTcxNB7Rq3WmM0DvpujGSY'
        b'+KN9CqpHO+aEpBsdP3qyp5j5etFktBJVj1MUGx2mCMn+crR0InKhddWKKGPGXwZLr78WQ40dH/eINBonvRIr9UjN60FTehCtLjYOqq6tEjN/r6fWo3GLQuqM+ccTJBvE'
        b'f4ZOhYm+NRMyYwZWDxAzI8OoYjRvSPhUY/7rqqlipjOMGo8e1EYWG/NLLIvFzMLhvdEo9KCUjzL2vRDaV8zc3ZOqULd6Qt9LLs+VeoRCi1EbenmurM4Y+kVyuJi5osqM'
        b'HqB/qQCQ8s4QiaqMUFnQ6ygqHmmNlrBiyVITaY5DKWiHRa41ThqfVSlm3qnTAANrK9WkG1OK1SPFzP1ZT6G/odOpyihj3LInpG4eKqTk65ZeiYwZEcYVYmb/8dR886Ve'
        b'joz8b7ieyHp72HHOqQccrhv9afkzBYUkPWrjj6/89YNXhxaE5PSeVxdV+2ZWWnpM9jM7Hmz50co9Le/8Xf3niHEhP36v77aWPq9Y/j35/oGvSv8Ycyruq6OHHJU//fCV'
        b'kFP/qEOnircZuR675fq2z7lfqRf+om3kyfoN3PmX//h05Ltfzfllv3mbnxXChvxGNz+5ZF7Ly7/aUPFN7c5bvVbdUx38Y8SZ/onmNy5/WPbpP8tzV07//Te/H//27tlT'
        b'FrpfOfve2oLeN3c9e/9w0aWvp97pbXzmhfrR78/c+Y+kusb/GnTGFbM1q64ho+5a3RvvfXFnwMdxf93jGef86Fvenfz3zz5fl1E46lZrjw8+Pbl/xoqXa47/15Ff/2Vu'
        b'5T9XLT73m69efue/vh18YOTCf+UVfT3kw7SMX//y7UOv/vaj6NMTwjLiB04aGv/lqe9OFdX3n3r/32hQ7JI2wxqdjOly4/H5iA6cGeTacygeWDO5FyfuFR+qfiIvJRFf'
        b'xyezQQrikBoUzVXkgLgtkk+ukmvJUEESR7aEIrmbA5WwlbTqIh5DRR9/6YJG+5uoKQ2uNNUuNVTbbVZKVRkhLhMJ8Xi1DEgx/A1hAkIUp2U7IVFMWIjhw+V0h4Rn+yTw'
        b'K+vwn91pZOFQPoYLBSKu5hxaHxEHEXSV2eTwo9tdMBXOMdBHsmkVF/1I9i9j/Ul2Gh3zg/g+bhBJdi5o2Fvxdubs0Arqfg7euQKfT1GiyeSKktzC+/HmAKVBIf13WuBi'
        b'pl5lqIIXwpjZmwddhBdkG0IqZGa5IBcUG1AjV6GAe6V0r4R7lXSvgnu1dK82yyk7sPBCiBC6QQ05IU0gXlaEMg+scI8qUxAcZqezsEopwVdLf4z6T6DsRPTC8XnlWNQS'
        b'U1E2q4GpqICpKBlTUTGmolyrCsZUKJfqrBIrCkX70pmnHKWUO+xfMhANtJPtotfFX3ovUDhdFFvuZPTbciUap0fJvyvau6G06dUZsZmKNxLXzag61T/zX1uyL4afKf3D'
        b'kKecE2/n9Tj50n7Xu0eTtn2RPHtA1u2M/jf5P96KtyV4/vZ5/sRN//7twrlj139Tf2Qz/jKrNXyYLOJQ+KUZVavHjXz+r/h/DkUUHbg54MHFAaN799WFsmVUQC6OgWVE'
        b'lxBuJJulZVSHj4iL7MUYJbkwoH1zUHTn2IjYInuatJHbbN8yZbhN2rfEz5DLbJsnj9zLYc5YdL/tUDhUTG7zeDNpIOeZYF5D7kxKTtVn6834JlXejvPpeSBVUbnBBrDO'
        b'4K0Y1mueHrfiVhWaTXaFxfGkKW6ci8oYeN3Cery1CNY3OUU2kpZkHT4rR5EhMtc8PWv4NBCuDrASKfjMk7hRjpRqvhduHckATJuPD9bE4a1pIJql5og+azHkhIysJ8eq'
        b'RQCH8E1yAkqk6nILgIxnRIeRrTy5ideTdZ0ldHW3CUg7gVAZDLXmFQZD+ybp0yBes81RqlVq2F0Mp5R+V0dKmJwqvScudrVHVmVzsq0q0DytrlUedZ2dbqQLZo/S6XKY'
        b'zS5PuLu23YLRlaKhdFC7koMqEOLm1zB6oa6VjkQflRgMl3/7UYlNvf2oRKdW+qQ4Tvqjy8BJ1189WiIuIq5Qx3nUBmlfDu7lTrPNz2tAHC71JJupplIwTYmAWv5Ka1wd'
        b'5YXlfdRdYAoDHSmgfUk+GD5AjmS4aOBlRwry83d4TI0hBu+od1FrZLdrtYi1qgziDHZRZ1SnOgPE5VQkWnuAPnZPULZ0tPXwqCNNkxVanxwOuhldZiP6/PUz48fG10Fh'
        b'D7e8Z+NufYtiNfx7vzqs49gyxA2LyUWyCxRwaSmK61A5WfIHCa5RW51+Jrd2b6yn4TdudU/vrAeU8tpz2Di1ozgfwOqSfENHrWAxnFdVXwe/X2r80Tg4ECDn9EcXBuhq'
        b'oI5gBoMn1GAQnZbhPtxgWOY22cQnbKHAanTY68wO1ypxQQ0NXFXprLvUcczkdFaZbTbvsu5sNAIUE4tBEdYF6tHwTyRZDNUKxMVEhXPsV/S5xS+RTXijMz9Hl6tPVSJ8'
        b'e3noEiCg+DzZGDDBYdJ/5zbOjy9zFbLdst2Ru6PgL2J3pJW38HAn/Qp8i1JIoXzbz3M1Cvgm5dwhwIPlZgVwbtUGBHw6pIUH7q0QQlk6jKVVkA5n6QiWVkNaw9KRLB0C'
        b'6SiWjmbpUEjHsHQPlg6DdCxL92TpcEjHsXQ8S0dAy0IB5xOEXhvUFRraE4HKCL1bONbmcJA3+gh9mbwQCe/2o++aI4X+8LasIor1PFIY0MILeskKIhO0wkDWt2goP4jB'
        b'GsxgxUB6CEsPZeke4tu7VbvVFtluuTCsRSakMulC9D2no6VpirSECImCjtUYCzUksRqSWQ09BRlbiWkgvVQxsvhweKjW70fKFR3iA57olB65FaROj5wiYTCcK6xSSRNO'
        b'V4nGu7pnUkIhikEhdPCkSfW6KWssGomAqJhQpAYComIERM0IiGqtGgiI2Gz5+98ADgc0i/7k1FpdVpPNupp68FebtSapE1ZgTqbaKnoEoOMrE+pMDlONlnZogjbLCm85'
        b'2Ks50zILtXaH1qTN0LvcdTYzVMIeWOyOGq3d0qki+mMW30+kL6dop+VM19EqEjOnTy8qLywzFJYXTMsqgQeZhXmG6UUzsnSpQaspAzA2k8sFVa2w2mzaSrO2yl67HJa4'
        b'WaAnE2gzquwOIB519lrBWrs4aC2sBya3y15jclmrTDbbqlRtZq2YbXVqme0Z6oP+aJfDmAnArjo3RxoeOtMTWLvonfechXd4QfsQzI5HvixxXfF9KQFjVFqkHzlizBht'
        b'Zn5xdqY2Q9eh1qB9EiFpE+119MiGyRZkAL1AoTsSRLgL3uLu1OPluWJd3tQPr0/ktmJt4v0PqCvAXt7ZBhpe6KbLEG/Bl8hRajfsR7alpNKTEXlzSXMePb7BbGD4Dt5G'
        b'TjLbwhs1ragvhxLaCmoKWzLnITfdNyEv2DhqPjxfTJqpiJ1GNsNdUalYR3k23QctKMghL1YXcACNHAshL+Bt2axC/mnRUea/xzjDL6b0RG4qQIwhjfgFurmanEfdBPNn'
        b'Z1PpGiTrMODeZ+Vkpw6fQaWZKrIvejWrpU8azzSey5ErbI2rJYtJv3niPvjUxDU2Xf1s5NZD5qBe1AGxvWbSnE8uUgUSWptWkk225CvRLHJCSa7guyvZLrsQr3Iuow7H'
        b'rU/iTdB8+Xirpgfinf8Nz363Jm5o68TaaSOisn78jzut32yYcWxgsrHX5+vHlPRO3tIww5RY0Hjw2+U7vn7R1G9+xcUC58wpK+pPrG/8ueXrL/f9ubzhJx/WppfFf57z'
        b'wXNvjF78wfo/vPXZT34kWzN3zY6DbU2VLV/9zNKnx6i/TTxQ8MzKrLEL7jUdnlRzZddzsz5WDf/uk8+35P9Uv3HYyX2Gf2y/MTanfsiZbwre+OJ3nzekDfvfox/nfPtJ'
        b'8kdcRf6fX/7amT/ta6WDy0udPvrca+4P8j5Q4t+tX7Fz62vlY1584c4LLTe1s75697uP9uQmjr2ii2G7EeTydHI4DEZIV+DWJ5EtMLo9cZMjS67Gd8lesciWpaATibvr'
        b'eBMoK+376zBXLi0UmUwugYKOmzJScwtScnALaWWHZVBvfF1em4dPuUQHY3J3Cd01w7dJg3cbfv4MZnpxDar1bTd5X+5JNmjGycgtsn6S2I7b+E6gBx9K0M4iF+SL8Fay'
        b'x0WnvHx6f5hxqCGZ0FM40rZlnv4pcjGJIjvdnJ+Fr6hw60pylWlcS/rjl0TLAj6M9zKcCJvNQ9nL+BpTKMl90swBAGgUPjuLtktBnuXIS+QgL8qaB/CFVBN+gYqa9G0Z'
        b'Ocjh7dG4ib29BPTJPfRtejDoZgysMgV5iefIfnxe7FMD2VIhqZRMnYSKXhRVymGkzcW8/K6DSrmeao0tOnZkig3wdi2rEypMxtcUoIwexM8y7biWnMe7+mlZnfkcNOcI'
        b'Pfi0YZDoIbkJN9sn4PvwNLWAtvUFDh+cgzewoUh34/20qQXU0wGA3CpRIM1i2QT8LL7Cth3wPhk5Ba+Kwh05OUaJNNNlM7NwAxuJUp2Svp4CI16oz35quRxp8GnZjOhl'
        b'3j0tzf/ZCNZRZgeB2AoMXlJnZ3rF9RFq5owZzov+EHJOw4dzcTy1coVLnsBR8Kfs8MtTSRx+w3lQ8kTSm+oFUChKyCGiNE/PrDioFSeofN2uCHRbQ9epxEp6BNbO6kzy'
        b'VcwkcOqcPiBAifhgmL8S0anpj9X7Nnj1UyrydKH1zfNqfe0wvDrww6FlPgmJ8i6QJrzMK9FhNgl6e61tlS4VoMgEe9VjW7RYbJHcUGmt6qJBC7wNejiEggfpqkvo3VWA'
        b'FUzL6gLuIh/c5K4FoO8HXpwHhw61q41BgJt8wFP9pacfCj9Ugr+E8w4AD8vKJCqiDCm7aIsQOBBdyVXfryEMAXhHlncRdNGGxb42pHVHHvt+7djg147hXbdjia8d+sdL'
        b'ct8HLURjD2tDF+BrfODTy5hyApD9LXBaaUq1NnbGOWgLfrgRR8bGSv7wWCfBdDpVKpxaa4d16TSba9iZatBkmK7R6UV6zlpSsEpBoYEeZbkddm2xaVWNudbl1GZCDzrL'
        b'wYnQTegsvLh8TGpGarru0ZIy/VGgzrbzMh0nHtS6VogPJgMrkyM52TZrKofPlpHT1u9yeY75tczXh3xmfL0y2/Tgw8SSj40PKj+HFF/5YUJ57GuxJxd9qHltpVLbOnD/'
        b'+pH90KsnQ0adnK6TM6EgjtyiDB1YpdBPZJYSqywqZcLQAsv0YMKQbHEsuZVMdkqnEp/NkI4kI5kxhJ1IthewLf44kC4a8pgwwi/iIpRp5BK53JXlS0XNTd6DM5KP0dNo'
        b'eSgXRy2rEqWXyhR+T5NXHlzqArjVTk2g5TawfniZcr4uvImocQA1cd3yJpKx5SN/2NQJC0rNLtEg4La5rKAOS1Tc7ZT0XxZDwOUw1TpNfrEAKld1qojWMYGZRCYYC6AM'
        b'VAX/TIvNDmMXWhr96WzjlDxV/iZqXtkDJhtTdfPUyD0OMnNl5PKjNS9yfpFP+fLTvI7gRuvvp4QonLSGq/I+nxlzAVtTSj4xfmxcYvlc+NQof1O37R3l6ylZSUPDdVOX'
        b'9yg+3jj+uREbBzKnt6S/hB24XabjmYxfj9eR1o6aQiNpxk1yNXmRXHElsjWDW0GH7CCs+iTVBhMTVgvqJYekx+1mOs0ug3eCGFNmKBrlRdGnEeeV6Vb38iJSp3cKvcAY'
        b'Vk4IxNsgbk+sRDsGF8BldQAGN/s7PnUBuLtmfE3ga10Q+U2BPKa7uJvqPVtEyUNwByzm4cK8W6jR0Ofh0pX7lYzxafn7oGV0trv51pfdYV1srTW5oF1W4VHssNa8QiLZ'
        b'I1JHBLFuPNqkI4h2E9Zlr9ckAErVlpiXua0OaUQEuKtyaQVzpdXlDGpGoqsbWuC013hFKitwSZPNaWcViFWLg2oxO5yPNjK5q8QWTZ+WA/zXusxN6wNxJJHyWq3D2yqA'
        b'leMyUe7bNZHo7PqoLnRPRNQHFTeE5BXS7XAWeqBQP3v6xGyfp2YJac6fnS0r0eEzOdpFlQ7HWuuiEDRtcWQNN0X08MTbQJn3N7y0v4vwVbKnnGrVHNkzZBm5oZ5L9uay'
        b'I7xk97Dyp8l1ci0cZp2cRvi5LHzRPQ2ehOL75IJT456TTXc2+5aVk+aUOWyXfis+U5adQsFsy8knWzigTsd1K/HeIeRkGY/IHnwzvBg038vMaoNPZsX7N6vOWyMAPVNe'
        b'PFc/R4WKn1bi4zTShtX4y0LeWQuvLUkq1b9+m7rrZc1+Gtu5maaohHWvKXidwvTeKP6tSS+sK7jCt5i/+bh35XX3t+suv/WHAbZD3wgP9JFP8g23qveO6vuK/K3SZfpy'
        b'17m/eP72/qiXmn6ee+5LvXPL2kttT3/07ofKT6+Nfvb0gkULHmj3pSzShTCNd+wTZA/QZNCXp5ALzI8srJYnB+dWMoI5TZcVlkQPFVA66CWZA/A1vL1WTi7pXOLZgssT'
        b'yMlkfWLsCt+RRbwH72X6tnMcuZXHLAPzyCVxrzk8StYTXylj9ZM26lNZR/Z0Mt/I1fgSOSFupd8Jxwd8ggK5N6kQBAVyD55SlZ8cw/tWzCRbOlpV5ItmzxWtG8/OAoLe'
        b'bkvADVTS2DFZYEJIMrk7s92UYEuHqvHzVZJTX7fcVSjNbKcQ3hOVg9oJfA81KOQikQ+XSL2YUnagvAG1FHrbwAipj/R1RfdlfsXaif9suGymxD/WS/zXoW9iH0n+AxrR'
        b'Xb1bbgAy1gXRP+oj+iOYktVO5brSLr6XckHb4O5K0z7ua8PEoMRtevn0jtb6IK2hTkI1DrPFo3RaF9eaBU8IkGW3wwHy/MwqudRSarwO91K9aSJbao+ghJrCJJ+ZcEu4'
        b'xKTkzQpgUgpgUnLGpBSMScnXKtoVk/cPdMmkxIhRovTG6L2/rvLoLSLaF5Hae9/1+es/2trPei6+xV6BUaN5JqqlpWqnm2qpSmSSnlUuAb4VlGHRjSjgIaVF48akj2Bb'
        b'UHR7SKB6J2hLjwTvG/AJ2pk202LtimqztMEFHaZ9bi/h7dSjwNfaXUHAOMzQkVrnBG1mR7HYKHXnMRyvs0oWWuimJ3PwuqzZwPD2k4v+TI80S/bK8mzIKpG4GJcRg3fh'
        b'XeRaHrmWi4aS4xry7Hi8V+Scm+txW16qPikXiLP/+z5mmk02W3LLE6XwByBPkxP9wslph0I8hxudXZwp09JD8qEzLemieI4vkmfI+uACuj63oLRdOMfPk1aEt5aGkPv4'
        b'8lD3FNYzcofGQmAFmfk6hzLLZMo+/TdGslNy81Nz9ElKRLbqyPGl4cvwHbKXsXNySzHAn21OxHuzaadoCxKBeoMMnqLT5yrQanIqBLckkCM6mRgs5JnwVAY5Fj8jQ/Ip'
        b'HD6H9+JLYqSqjbPwsWT2Nj48PK+AelMd4J/Ct/JYJCp8jtzD65NzC1JH4wPicHKox3AZOUiPzl1enSZ30lMmkfMP9HvjdgRJD5cXlxi2chkbmx5EffLWb1t2TKvlcY8Z'
        b'uv39SrIPbipx/kj2l7qdoV/+/dVtPd9NPJOw6PL5WXE/O3f2wKdDy17/R139xCeX/6LhN0eb/nT72SMfbvifkgh7zMaktdYts1eFjH43c6N8wcdtCwb8eeM7siefj5v4'
        b'YOcHP5/znytpH/xI9tZfI/c8mzzj8x7AtSl5x7tL8ek8xtH4SjU5yY3oSe66qPsRPj+Y3A3Osw/UAM/G2yWzPj6hDKdzvT5ExB2J8cPUHmd8lSNnyOa8nIIk3IBPg0TF'
        b'IzXeyuP15Cq5KNr91w8gRzPJS8FY9yk9a+Ygcm8es8OfKFaIwdM0eJ24kXLehnfRHQ7qoUo2rEFKGz8okWexN8iL+DBpY16sRXg/vixG4EiBeUmTgaTVijeJuxr7F5Cb'
        b'PmM/uTif9oEa+wdLrDP8/5GFPoyyRYmQMN6e0s7bRynZYUW1j7OHSn/h7OwKL5rie/gzWKkmqZFKkV/NoZe59DIvkMmHfD8PW7lY0zyfCDDXxwMr4HKqgxzw20H+ckCw'
        b'ZnbX4Kz2vtAFB37g48ADKesAwsoYiY/zBJjZ5cxhiIc/bqYuzjGCVkKphIMe6qM+gIK9ymBgWwkOqvmxLQePrNJa9chdDY/KaxOmJh2mFXsiAvRWJiz5SVEV7C2pfeKE'
        b'Rf8/2gF6FLo56B51LzpPi+BGLZfzsYBQiOs/mmdiZLevvCa0fxhPRU0+lIuN838Sw2kH0DsWNGvR6nHO/EJx945DQ/Ch0NU82R5mCeBoodJ/5/928HUS+Aq5IKtQWFGF'
        b'UpBXqOBPLSgqQgRlRaigqgjbrdit3h21m7PIdkcJ6hZeKALZJ6wpyiJjfsfUiyfcHCGECeHMp0nTwldoIB3J0lEsHQnpaJaOYemo3RpztBhUBmQq6mwT2RRtUQs9hFjq'
        b'lwQ1xuzWANwooWcL85Fm5aIt1NMpXirRA+qkPk7UEzoWylCfp95Cnw3qip7QNk7oK/SD+zihvzBgA6qIZz5MqCJBGCQMhv+9pDeGCEOhVG9hmDAccvswvyRU0VdIEpLh'
        b'f78mJdSUIuihTP8mBPepQhrcDxDShRHwXMvyMoSRkDdQGCWMhrxBUs1jhLGQO1gYJ4yH3CFS7gRhIuQOlVKThMmQGialpghPQGq4lJoqZEIqkUGYJkyHex27nyFkwX0S'
        b'u58pzIL75KYQuM8WcuA+pUkN97lCHtzrhWLJkCITCoTCDSEVqYKcSduzPcrMGuZcdTZADKJrWnwg+leJYUZBwqNx4hY7TFS0E+WyqlU+158ODjaB3loOqKDG7LJWaakr'
        b'oEk0YlaJ4iVkUIkR6hQtI7ZVWnutKAMGk9F0vEdpWG6yuc2eEIO3FR5ZVnlJ4cNJ1S5X3YS0tBUrVqSaqypTzW6Hvc4E/9KcLpPLmUbTlpUgF7ff6QWT1bYqdWWNTaf0'
        b'yKbnF3tk2eUzPbKcGSUeWW7xfI8sr2SuR1Y+a95MgKwQAau9cH32q4DdinpKVHlnKCWsa/hmrp5v5ARuqczZv55v444iZ5KLF/h6Pg7RoLHNfD0g8hpOkNVzS5WOinqO'
        b'OhHCW1ybjIaaFZS9oFwCikVj0RquVg3PVfSuGdH36pFBDrUqjgIZNygFNbODhbxvCKZidPQ/k+a43f2s4wuPEtzZKIhqg0msg+V0YYgSh2sC8/AqLdKPyhgx1h+FBNA2'
        b'cixUitc668xVVovVLKQElfWtLqoZAF/zepoxyF51T0RXUD4c1kr3I7SFCfTxBKNgtpiAZfhQyAjqh7WqmtZuFccJEFGCA8jVuW+f0Dl/2NNay7aM2nszfKhzuIdL9XDp'
        b'n1Be8Ml38PNQlpqeXqhTeaI6gqUbHiZbXbXJEzqH9iTL4bA7PApnnc3qcgiUayncdbBEHGbUvtVBjUwOO+ry+DZjqH/wiQmhcmATsZLNQstT2WZ1pIgA3d+cl3b/aLO6'
        b'kA7+7tua9wLw7czrO6IMm7hVdWatESakCvi3LXWG+N9oTAUYT6Bue6CLI/ToZv3LJ7T0Yf4BwdEwABjvBRYlAaOrdwkf5nMLkLGp8KhNTgPzwvSozSvr7LWgsHbRkG99'
        b'DaliO/bumkpQemEgpBHQ1tlMVXRb1OTS2swmp0uboUvVljvNDMUr3VabS2+thRFzwDgKRiPFUJOwxA0FaYHAWgI3VANP/XAsCoIvKrTv1A/HDO2P3lyt1snf/0swAlNe'
        b'R8UrkbiYV1ZVm2oXm7UOllVpojsCdnEPFUqZtHUO+3Ir3R+tXEUzO1VGd1jrzMAjpsNwOqBD00y1S5lt3Omyg/DHSEFtt5a9tOS9TTKwJhnpmLrZMheJCqU+Pps4jCl1'
        b'Sg2yxUZjdJtd1fZ2fpWidVqBfkrV0NfoFre/a+uj+ihVNIFG+Z5glFhpkL26Lk0blXY7jbqqtfjbUNxsKoQO0xCUIK4wO2BRLgc+aKqke/WPsKb4xEiKRHLU0TCiKRRN'
        b'5jfwgcHJetD3qdqaN5faGsj2bPziWEgVlSfmpuTolagmRk3uu1VuuhyiyU1yFdS/y+TG7ETqy9VMWpMLoZ6T48mxEj05yaNRsxSL8UFyhIm58rk2Z2pBLtmzQhmDIvE+'
        b'mRXfSiV36tzUSQBfB4XzeX/jQ2KhPilPX5KI706UKs9TgECqxrftKhbuUxUf4kwUo4YjfJacVuBWjkZBrhPtChvznyzFLan4JtldTlrInnJqeSjiyHWOPDeTbUMYx5J1'
        b'tEXw+s5KGd7P4XWz+rIDCOSszODMptadqTPo6bKLchQNDcbnQ/oze8cgsgPfdSayKD+x5IxiDUcukAtRZdYhm/I4FiVpzo5BPVsmljRkRm146h8/iUyaOec/8e/F7o8+'
        b'0Dth/pBS854ZbdwrNl751LYDr/51Jf/GH21v/6r10lNz0ntFr5796fsjE6yjRv3t/ObGlxsWDym5dKukcerIWc/PnGa4/QX+JDf+09nnoj7qtTDlY/zro3MPh0/+fN8b'
        b'C288uHEi8nr92ui3Ji5K+POX9/r1fc5y/a33l4xv3Zc0+4sTCTmTX/1F2qWKmH8etw2cP2DmtHE/7TNk3FN/Pnz/6D8+e3OSffXX/3l+/E8GPFfxzKBviotuZq587eO+'
        b'9nsFl/av/V+ueGXm3df66qLFvYBreMNKFsiIbFWhJ/FLcj2HL1SRi8wkkBFGjibryRayOS2btMhQ+EwZOU7uKZ8gL4i+g8fIehqrKw3KcKiwXJ7G4Wv4xRwWqmAWPjY6'
        b'Obcgn0NzNPKBHD6cQV5itoqlFtJMDSEFKoTX4RtKOa8m5/Fz4ubCLY4cz2MN4hC+WimP5/AxfAtfZZYMhSWfbMf3g5pj5OQSeUbNKlnOk2vJqUWcLsmLUJHkqmyV9mm2'
        b'QwFNvvqEaKEhx/F+ZkYpGi+ORhu+j59Jll4id/F5eSGHLwthLno2dR45toQcDacmkpyUVLw5jS4vqEWrlZMXyG28TTQYtQ7BjXnicqNrDbekiYuNHKHB5xWkYc48Nrjy'
        b'jDCxo9Swt5lDYQKPW63k4Cx8go0f2Z1nmILP5hXpOcQv5zLxc+Qca2W/cHJmLG6RzkpK5yTxERgjetAHH51OnssryMsrSCWbU/K80QwKSGMS3q7Al1LwTjYLxeR6Adla'
        b'iC+kKNFU0iifweG7pDn+e/gn/pCzhj1FgmgI5AHMCkStnpIV6GmkCWUhWal8RN02Y5lrJj2TGMVsQRopsqaYG8OJO0Kr+0qCTlAgPjcVOks/yCGTE19lEkQjXL7rYP1p'
        b'DDiA2GVjoC4qOAb3aWGRT1hQLJAJOL/IJzz70sOj/VrorsbbwSSC6SJLk867iIIfFVeAw1Au5ZO9JMGASglOSZjvzICkrYAOkkUHOSK43NCZnZV1llFMlA8GsG0vF7VT'
        b'9k73QVZRAaRzy0xV1eI+eo25xu5YxbZtLG6HyImd7Osej2fpHXWlQCnVz43QZXIsBsXEW7LLjY9a386HiBXejQ+v6EQFHrPTX6PvgvMHP+GtFj2Frs6mES1OD4ssNqb8'
        b'daYUp+LKAhri472xocXGhcfL14iZp3vdRCs5lPBnzdRlv9En92AebjPJTnLCGYF34JcieMSR7Yhc0CvcNJoxvoK3kOf9SBsTI7x7LMzYD7y1jO7HzwUGTzdN2nf4yYX5'
        b'QIVW94+aYDJYw5Z8xDtPQ5WfKPmClokanB41Y/GvNQPrJ8RGLzv/t7I5W25dG7AwcWxEcUrE8LbL9le4cQkvWD/+w7Y/VO8eHNP//Pnlw35+dO7EQSPTinsU4GkNdW+0'
        b'9NxS0DBrf8aFmL7/WVnb76k+w2r+OGFPzYoNI29cWbZr6onfpv79lfl2fG7HyzffX/XOiyeP9x/70s7LsfuUh3asufiPWS++9MWnXx/5iUzzTo/t337dtnvcJe2qVR9E'
        b'//4/YSuPjXvHek2nEfldKz4e0h5KGF8kB3l9EZBlFnDwXCo5mZeqr3FJIyFHkXNktmRyw0XNpvgZ8uLKIHyhP76LRL6Az/cT9/8vkFvUsYtsnbTIG/9nHt4i2vK3k1Z1'
        b'J+r+RAESiTtufVKMNXWuDF9mPA4fws3iVoEulrEdPTk6Lbk9zFQGXh+Gr/LkXA4+K0Lfha/NlUIFlc9C8gIO308lt1j/8XV8EUusVzERP48Ye6zSi027BXJZQyB3JDcS'
        b'vQwSPz+BnV0w4itjmWCaA40PGA4e5M8txbmcIU2Nj+OD40SQzbiZHE9meyIKpFyC11v5/vPxBtaXUYvlAbslmdXifgm5vohtqQDGHsQNySkFZPskEEWlkOOReJfMMRM3'
        b'BDt23l0+ppKUBMa5Mvw51xiRZynFQwZcnMSdaLAMDdvZEP0WNNxqjcQgpKoCfdLsgUyqi8AZvFi23UFhI1wSoS5nXDtrWoc8/mGPOsIOULcpeWHqNpXkqboNf9Qk1lvg'
        b'XDzcyxq5OCgg8AEp77ccHvJDrQ/lQ1MzLNAV2jJPuKHWbpDUYadHZqp0MnU9uGruiTL4Nq5F+2Iu7z12zcOw8avjveaSDuUCjIC+HeN8uDSzbwE08o6Z9RzrDVoqc0yl'
        b'vXIk1XNttBfoKLeGq41zyQSunqVpSYtMNA3CvZx+T4D1kC98ONzHL2usTmhCVTXjNEOB0FOrE1OO6Q3MGhuAHtaaOpu1yuoyiMPttNpr2Sx5QspW1Ym2JnFIRMOSR8HY'
        b'skctWmntjkc46WoMdQ4zsCuzgZWfzXsdIWlMLcA5DS9ncRtW9/QOWUD5TpPOBowijUCtmjAI1K65hLPwceLGFHQ9RqwpkXYvRewkNK7dECbOaaevKtBTOQDaYTAs5KVv'
        b'KiB/w5f4LDgWslN4nBcPpcZsoI1RUSyDYQ/Sgo5YpTLQ0/MGdirIC17jA88e+WQx+l/uhZ7A1kAb4IPAHeXXsAGp55aK9i5oAzcJoNOPKYkTyIvQtwdpgtJgsLkMhkpe'
        b'YtoI5mh1hK8N9Nn3aoIPHflJk79PG8wGg+VRbTB3aIMPK1L9l9Eg7wJZytu1YmuAQPClIrFgd97TGu3z4teqR6AzNM68zGBYwktmRRGNAxpInwc00GcaDGeDRIGHe3dR'
        b'vf7tXY1GLfS4zg8n2kHVdhyLx82H3IcSU77HdCyGaXc+YjoWf1+UUHhXBj/l+6AEKCWGFY9qg7nDuvS5qNMR95IJ3/ksf8oelApQK5nB8FRQKiA+8/U4QMwdErTH8XRj'
        b'BzGKzTfy3t5zyUBIfZ33WujbR6A2aOOARJgEwWBY6+M3MBKh/mSCPe60PvzQjzbvKNduCj/6mLGnVJFV2hicKgYC7MZ4JAQfD/0PHA+nu9Jg2PTI8WCPg4+HhjUvrH1E'
        b'Fnd/RFi1W4OPSCBIGfIjUdQtwUeiNC7EyBGkYzuOCZscmUdTaHflAGM207NDZqGrsXnEGRmDocYNCLvdn2DJA4eIFfg+KHOqGwPEKt0dfIACAQagzCT/AdJ2Rp4+viHr'
        b'02HIhHZ2l9YNVAo+XGEGg8vhNgvW5QbDPt57rIjR+FAeBi3G1wlfsR/Wj96+fvR+ZD/4tB/ekXBgoDa73cGaeCRIT3r4etJe7od1Jc7XlbhgXWEiGTf0B/dExUIGGQyn'
        b'gnTCD4ft/lRI7t/+YhQoFrS330V7QLfUoa3t9wv5NfwamdQPWSPtkUy8s3j7RCmWRwljBmBBg2AduxTYO3l77zyKFdV2m5l6DdeYrLWC+VGycqjBINZpMFzivQHTRQGD'
        b'pwe/V0f7+ustF1w+puKoyPbC2NQwkmLpKO08igOyWGuLDYZbQeVQ9uhxYEPbwW74HmDr7E6D4XZQsOxRcLCxDKxLBMn5SKhF3HXdHDgvXUAHpc9guBcUOnvULRHD0g0R'
        b'Q0V30UFueiUoLPaoW7CquwErhC1wE1T5qh+0KP/VTx863KiDpTdg/dMVsxQ5olygUTNHFE6QCXLKt+KhKWvoSqE6Kt/MHxXXjrRiWCMVhZ/QSh8OYpvQ1trF2jr7CnEb'
        b'e0S66Mjhrquz05hAD/n0VA83AlbPau+0edTL3KZal3W12X9heVRQ02KrC3R188o6r2L6SFMIjAIDbjD8uJ2MqFksUY3/aEiFxHGlQ6JL6+CF6HhSqs9ps7toeLGVNK0J'
        b'tJxD2mIxV7msy8Wo0kCObSanyyDaiD1yg9thczTT2rbRS7s/ow9PPWqfMSKMGWXF7V9m0mdquWMLvTDKs5NedtPLXnrZTy80mLTjWXo5RC/P0csReqHCjeMYvRynlxP0'
        b'Qvm5g5o6HWfp5Ty90NCmjqv0Qj+v46AfiXTcoJcX6OUmvdz3jrEu5v8f/8gOXiqVcHmdk2KiqlVyTs7LOb9foJGxPTu5RMp4TpsIfwPDVZqwcJlappar5Rql+D9cFq5Q'
        b'sz+ao1Gz3xDIlX7Z1mwtPkeec5JtpIW6S+K75CCH1Am8m7TmBvhLyqX/zt908Jf0Rku1yFncVjWL+MbittK4b1LENxajVQhhaRWLAKdgEeBUUsS3cJaOYOkQFgFOwSLA'
        b'qaSIb1EsHc3SYSwCnIJFgFNJEd9iWbonS0ewCHAKFgFOxbwvFUICS/diaRrlrTdL92HpKEj3Zel+LE2juvVn6QEsTaO6aVl6IEv3YFHfFCzqG03HsqhvChb1jaZ7QnoY'
        b'Sw9n6ThIJ7K0jqXjWYw3BYvxRtMJkE5haT1L94J0KkunsXRvSKez9AiW7gPpDJYeydJ9IT2KpUezdD9Ij2HpsSwtempSv0vqqUk9LlGFlvlaooqBzMsSVQwSpjJqlumJ'
        b'pMduytrPqb5/ueN2lvdop18hKfxch2LUB4Q5pFSZaikhrDRLLnYuK9tM8rqNsHhnXuc76jki7tqYA/eXpF2tQE8Rqp/5Hao1UrJrEk8OCfYqN1UsfDUH1GZ3eCu0ukQT'
        b'n/iqd5NoemZB2QypBuMjPAMDEjkWye3FpK1kBkmoTtzb8z/0myKC9PZV8vx0Ocx0QALqMzmZoyltHHNGWQ41mWw2rZuKWLZVlNEEnCYOeNnHYKnWSMkLjWDgtHCU1zmi'
        b'KL/rhZr5pSGOBC/PczEr7FFujUwA/mYQr3J2VbCrkl1V7Kpm1xB2DQXJk/4PY6lwdo1gV40gg2sku49i12h2jWHXHuway6492TWOXePZNYFde7Frb3btw6592bUfu/Zn'
        b'1wHAqWUGrcDBdSDLGbSyup5vG3wUzUBPLgR5V75GUS9vgxV6lNvBOYHS1Mvj0Rp5bW+Wq6S5jmGCCnj60Ho5tW6ukbuGAY+XN/JQfopruKCul4t2aFciza9XNMo4tOwv'
        b'c1Ez9HCJppljJY0uXQO0gkmFIYWOW1QqGC0ugE7LpesFwdjCTA9n8PAGw0OFYahzqPPh0I6VVJuoq1a7t5doDE7yhJcAu7fWSB6USnGbUwxBKjNYBY/C4Da7HDSejHg4'
        b'whMpBif3HZNzTKYMaSq9TKMXGvtGjLZSyMSBwBOVIPCJ+9lQY53bAaKsGUAwUUDF9gVcJo/SUONczEAvpScNFQaz+I+dO4zwvsY+qwUvVVXTvVgW8tbkcjtBHnGYqdHe'
        b'ZKPhkGotdmgxG1erxVrFfKhBBBFphu+xqcbV3iFPrMFmrzLZAo/000DD1XQH2QntY2sWqmH/xQDEnr6GDkMO4iusR6msAu5rnJ5QaKTD5aSe4UyY8qhgXuiceDSZ3pkR'
        b'Z0LlNLukB06n2UErZA90StGrgRowPMqlK+i3xP3CItSixwdlYLP7LhX+KpjwF8X8NjqG0lJ3ynnELy/+j2HmJrpTRo3ANMD86vgOI9Lt2M5SGKVfoC5dU2NA7RE9ZhM6'
        b'AvK5zk4qY/4RtUvbz3WmiGEWXHbp/Cv1ZBSAcFstq4Ac+5HJbnvSSs2d3HVze3qb+3BYYKQt6k5QY3e1H7tloUa7H1ZoatdwE3xwA0NsdQZLY5t2N8QWW+xdQO0T2Fv/'
        b'AFsdwEqBRrsL9zGxtfr74OqCxNb6gaC7F79poA/0bzO1YnhZp7tSOgvCvOQpPMmpRwrl1GW7mPAkVsS2TKmsUwevUTmFBb4JEhwqVVvanmexmilASXCA2qFAu8uPjxc4'
        b'tUnSOCWlwK3Vxf57w3AlsQ3SJDEaVtLjB0syHRd2PViJvsEa1TkOyiPwM3Pa3Mw0uGR1PxLbL7tuRbKvFZMCDubTgCPmysAj+h1bM70ka0bajKxpZd1fM7/qujWpvtaU'
        b'sJn3Y9+SE5jX77+Dd1KqdgaLiyL6YtlWmFY5pVPq2lrzYhNVvrs9b2933cYMXxuTvEju9a/ya67Eo7WJpXPmVnR/tn7dNezRPtjDGVm325dSyVY8Zw8Cb12dnZ61AtHI'
        b'LZ7M7/bK/k3XgMf5AEeW+Q7PdA+ANPPvdA1gYiDVqoF1alps9kO+uupVTupdpy3OzCmEdW3rBmhpUD1dg54SOKjtIG32xYEQtYl5JVkzuz+bv+0acKYPsOhVWCvoXXY9'
        b'/Gtn1drErO8F8XddQ5zhg9gvaMQHbWJB98BJWPP7rsHN8oEbKLpNgjhYS4+YSItDjLtRXF5S3A2Q0ur8Q9cgc30gYxg9Y7KxdFam2zDe7xpGQTsF6EilqDxNnXzofeK0'
        b'oqK8nMJZZVnzukMhpSH9Y9ewi32wv+gIO1DGT9XOBIowywytqWXyn9OncAcL/A6Eam7OzDIavj1FO2vO9BRtcUlOQWZhUVlmipb2IC9rvi6FuQ3NpKhSLdX5qNpmFBXA'
        b'qhGrm5lZkJM/X7wvLZ/mnywrySwszZxellPEygIEZgRYYXVSv9k6m4nGsxKjgXSX0HzQ9QDO8Q3gID/yLapDIkKa2AI0OWEMu4sw73YNc74P5piOkybqbKnazPZzbTmF'
        b'M4tg+GcUzqI0nSJRt5Hnva7bsdDXjvgyxs9FNREmT6BYY+/GCpHozEddAzK0U3MpQgs7IimCMbcbffx1je6C/p+uQVcGkrh20kbdx7XUTtWBedDXffsbcyRwzkLmbZfA'
        b'9gGZF1ddX3ovHp+l+xnwJ2+Eq4GWVzDvPAV908CubUq4qo5ynB9yPpxYIrpXU0uVT34Rhal2m1lwYStVp3bQcz0OGhOgY+hmZmugwQwcRtS+GT8eBdsCCqMfV5MqNcsk'
        b'xwcEGmwC87yjPp+r+3RUJv3eCT5L1G4mcNJmaJm4DxB8iui+g13WvvnUSXH1edUEPVCZIM2PQ0P3bo8iule72G+zjXfQ7SWPnBoeHuFZp5bMEgb6JTHJT4QdxgjSFLFg'
        b'8D7H+jVFjLQreD3cmDHL2xYFG7dHu/nZzLUGw4oObQliOGDlCnWDg+1BMYMG2zXyaDoYp8b7sKYdYQxeXPFEBNqmlJJpSiVxaPb5XI9SMkspRKuUnBml5NQmxYKNeMID'
        b'DFJKyR4lZ7YlTQfLU5i/4UkpWazU7QYr0VikCTRIOcI4CXUc9BtWDvY5KIZk3YnQ5vgxXN6k1h661aUOl/MxGd0In6HoHFDjewbg6HyVdx2wIzxULVMr3NQxiGzDzbgx'
        b'bHlEXbgul2xLLsxPHU32UEd2Gv8/qVqBL8fim53CLNIfJ92FbN9yEvgNiH0cUCbIfR8HVEj3SvahQPFeJagENZRVN/EWTvwoYEWIGJijIpSFq+VpgA7IDWMlIoUouA8X'
        b'ooUYKBEh9GB8KNbTowPu5ltBjfbuh8n9VzN1eafU1MD8Kwwc3Sk28ItpSAKZ4GPpcibAe0J83+WF2xq7YLLRb7YN6mh0pNAM/pscTq/7RRzHtlK9lai9dXQkUXQHdp3M'
        b'5yIlfUSubxA43T8Bb+mWJrLJZ88LCq3bH2uTpJJBXJfQmrzQulvf4K7raw5an2+yqb+C1y+j3RWEhuB0DHl0xXS9b/HjF4+ahs6E+jGOEn4wO3FJRmBa/KB25IgSVEaS'
        b'H8MRq7vDEXc8vocSV/Q/M+BzeqGWJq9XkzPGBYClUwDMK2upzDkK7pkHE7und/KlMsckl0LczYK0sk1F/fq49u9zPtT7y6k1NExAZXvcheEdWjk8sLhgN4sH48XTBiwQ'
        b'jPccHiPxIM+0eBel+JH2ofRuGL0wdw86P8CP6upAH/YeMwjzA8GKPsJ3SmYShF0+4UYKxxXO/nfirGx4oXxw3AmVcMfnMew/k53xhn798JDfXPYKBqyzHOVzsYxla0Sk'
        b'2fVoBmrkJMCywgB51fcCPfxA6eWT4fS8BxVDnuGXMcdurzM5/Vaf16WOfrDOw7k6rTG4tHlbrUSr9cFa7bK7TDYgQXRjyDkFbihVt9fUTaHfw3C6ax4h4CjYe0ceNyas'
        b'VKFO01G4afeGYYjSjiPtcgATC5I5afQdqT7ZoIsYJwOh0BqZNODAc5Xi1//UMuoTQn0+WIQB3JhBLlMWTDaSiz42LPJgco1sTgFYM8gFVX7YEwGMOE7679zOBTBimFb2'
        b'KzukqJBRnw/q8UG/8yeEUjZLv+gnaChbFaIPaSro13kVwHJjhB7AZhXsbK2aRrpqimnqZVEJsUJPyFeaVSyqlfhFX5WQQO+FXkJv5hmiEvqwdF+WDoV0P5buz9JhkB7A'
        b'0lqWDof0QJYexNIRkB7M0kNYWgPpoSw9jKUjxRZZZMJwIRHaEmVWWZA5qhFt5yqi4FkMtF4nJMGTaOgJJyQLKXAfw+71Qirc9xDGS3G8aCyR9i8iaqCfUaynPZpim3o2'
        b'xTXFNyVYerK4WSEVsbtVu+OEjBZOmEChwGjIWPQsGkusJ/16oDAGnk1kcMYK41h+nDCSseFJnnCKf15fBQ9X7OGKdAoPP2uah8/J8vBZpfC/zMNPz/bIps0q9Mhm5OV5'
        b'ZLOmFXtkOaVwl10Cl+nZMz2ywiK4K86HIiVFcCnNog8q8hxWRoJm5RTrNB5+2iwPPyPPkUGpGZ8DdWeXePj8HA9fWOThi/M9fAn8L81yjGEFpldAgXJoTI5vuXsjnDOX'
        b'BOnjAWJYLrkvvrn8kfHNUbAPk3aOxy0vdGfDfeRT5CzFdxfZXJQaQU6RlgIaXrQ9qCiL5Zmaw44m5qfkFNAooym59Ggn/T7pFNIQia+TPcOs9pCfcU66T3VH+fxnbz80'
        b'fmp88GFiTKIp22Sz2CpTTAtf/uUr13eMYAH6q/sov9ierJOxzwsvwi8NCcNnUrLFA5Lk8jAeRZOXZPgCuZfFToourykl9DNV80sALo0lcJBfmSkGq8abyGVyOvDrx+Q0'
        b'Oc4+f0wOyrznFR+/N8x7ibHvlKT4O466Ca6O9cegwI8KK9r3ph1f0kvwr0vIxBJDfMV8kK9SqkTDb/rOQYq//x0Qrz9oC6rU0vxScIGfp1QzlAmVvtMtrjExek/75ynV'
        b'zSGARiGARmqGRiEMjdRrQ4KhkRwF+0Jf30IWR5Ycmk5O53lDCgLS6PWps7NzxTiudHLLi1fgDdn4NNkwSIbI9rowsoM0kltuqqHqC8jJ9ncBv4r0c1LxIel8di5poV+j'
        b'z5ubSDbPVQOqyhF+EV8Ki8CnhrAz4vuWKNkH+tpWu1LGjA5FYsD3i+SG1hkRwU8okE6Ik01u8TMVlWoUhVD65Sp3yunMcOSmSFuexQcGldcn5erx9vbT4io0v1S1ao6d'
        b'BZglF6cl5eUU5KWQFh3ehs9xKKyQJyfxzWluhpRXI1ckZ9NT5WTXyPR0vMGYh5x4/SB8Q4bvyfFtN/2SLdnzZGxyIT1Z3FJQXjx3Lt7vO5KemKpPJM1pSfSTGHadGvjO'
        b'VnKF9Sodn1qNG3LzyNac/DQlUsbzGj6GoSGLdzODHCPb+qck0wHXw2P8Ej+G7CUX3XRHf6iePJssTsXczqDILtxQMDuRhVIvThTbhTdmy1B/vDEC37RFM/h4hzHUuZxc'
        b'leMLkYjDBxBpjRjrngpPVpCDeCP9QqP384x1UKwsEeZua0pKQTkLhS8dw28PPEmOy8JTyCHSOjSDRdDJjMBHxcjxBXhLso5syYde9JglI4fx9mkinr0wLYGNWmU4Gzd9'
        b'e6j+9lGbTeHweAtPQwzdDxutwxfYdxLJ8wVPkF2zEZodilajArKr3E2X3Up1PxjiKyuWz1tDruPNK8hVlxJF9OHxgTnj3aPp4sLP2JyQO4d+GiAxVw/TDhSQQSlJ9E2h'
        b'PoYcUSK8i9wKRbPILjcVa9T4fv9kOgYwJlvTSGtp4uinEoHMNacVSkMi4hZeh8+EoEr8vJuFR2mtIo1h5AVy3VmAXyI3l+GWFY7wZeQFhOJHyvCGBLzOPYDhmZk0kK3s'
        b'QyqnyS19KgytAsXgPTJ8kSNtDNtXTBE/Mfmloib8J31CEAuggC+R5pH0k5H4DtmCaFznLSPxc9aF6zLkzqXAhX48iSsvyStpnBp1uH+C+si/H8R/9yHq/0oP4cRT1z55'
        b'S12+hPvTkqsjKn71zjK55YtnJs3UGKdPKX9n0serjvzF2hbHbb7x+vPTtOffD1MnpQ860jPGXHru3881vHrW1jDj6NTPZr3G1wweu2VSydKpeyq+kZ35qendHt/2Lal6'
        b'c+V/7gzZuDzpWsPIha6qr77afGHP6XO/mKEf9+a7R75Vzmkb+N2fRrX++8lnN/105gDZ4Lk78Vnzq8OOF8s2/X/sfQdYU+nW7t5JqKGL2DV2Qscu6lgQpKMUuwLSRJEW'
        b'iqgoqPSiUlTELhYUEUFArMe1po/TzpTjOL2daZ6ZOdPHafcrSUgQ0Jlz/vvc5z6/SBKy9/56WWt9a73vRZ+37+1q22D6zLa9hV/WFA6TvrH3l59+3vvzl+6nnxrmtKFm'
        b'99uHAqJOJuU8efexnweG57WbDbVJPRr7udvs+OCl8x6Lf/trtxFv3HZ6xuVu4JOVndZvbP5k41e/nsp8zX3UZ69/G9r86fXpd2ZOdvvh5ylVl5tG3/BtHmiVHOOeaHvC'
        b'8KkZs28GblxSFe1n/0L1um0BFh8O8n1SdXDC6t3Pb3wmIv701U3n/33/5JNDWp4OTPL/efhrM97b8ETBH2JcnP3w/I5fjZSHKmb0f0c5mqEE+JlOYHvgrPkauCC+BY7G'
        b'UwxiYIgih0wkzrokzpYJcrggwZNh2QxCYADsg0p9SGY8PYmhDETiEU660ATN5Lc0yxKKLcxN07BNhe3p5oaCbao0FE+kp9P5ASVRWECxfIwNGJqP03CWd3YMZdygVAwk'
        b'nzxGxyBC3exANXwBHh/DWDbLlFjkg4fTaeGaJHgCG/AS2+ChNBR2Q6llJranYFuGOeRihaEgHyBZC+fGsg3eIgFuuOGlLtQKiXMmHOZUD3l4bLQ+z0My3qBUD0sCWKEH'
        b'rzP3dwk0TIHTgiRbnInbzRkA0XwByNTAErI4lIWHSgXZdBEukp9aBlIdCnXWjGoKWqGD0k254gkhnRoy5mJhmirTLDUDOyxJewyBMktjc1NstswkkxDbs1JJmwXKDKHT'
        b'E8+x1jGHQ1hnBfmOzlge4C4KhstEbIQdE1k+OQnuWOoD54UcbBAkOaI3WQc6OQRSNZY8BqXB4+g6DI0+gUD2OBe/QEo+2ibLgjpo55Ddu7EyhTFZUDqi0oBhqUaCfI4E'
        b'985I44jcB7EeC9VUnYHqJcAk2y5AZj4f21ghZllvXE4WwlJXOsAMBMNIyagp2Szx4YutyNfqFQzLthgI8mAJ1kAtVqQzi+T1BdCkJsdcinuD6T5M8iA7pKEwAk/KyLKZ'
        b'Dy18HJwna0mBDpEmNsSo6cGgfDVrqZV4KsSQpudKm4q0lK9kAFyBMi7IndkUR5+GDswlWQQFBDM6VlEYjAdlqcbT2WCYAeURlMhTvYH44jVRsAiV0ra7wW6AejwYT6k9'
        b'nIkQ4Y+dzlIyGEskeHoV1DDkEIk1lpDrfk5DRvsSqUAwniZZs4YUgaGfHEsawK7hBWgnV6FIzW/qSwalg70B5q3CC7zRD9iuJ3cGOaUmQbGrekE3IE3SYWCwbg0D4oIq'
        b'qIXtrCh0vGvhVmygSUoF6/np1EoPR6xJ75OpoRbAufQNxbDLVa17EuH6uFr/dCS7S/loUziynoxiOlYzsDKz54ehAYsClFizxVAIEIygxSwx3ZWWu6g/EyYoVD90ZuiT'
        b'zXZjmsWjPozVLQCrJvFBAprbDQXR344sAzc3YFvPsvV/nzOVmQWYjJ70oIw+y1Q0pjSpEpk4kCKXknc7caDETJRxHZ/6ZkqsGCj2YIrFJbFhEXVmElMpkbElhjqeoPQ0'
        b'zFDnL2YI7t9N9uYWYC7+m6rjkTSuwjJqK0ujLZdG6U7vyqOj0rVev4aq6LWxG2K7I6cYPRqUWbCoTjRtEX1hibCMQuifzBSzUNRtr45eNIvn9JhXe67do5KdGkXwOvUF'
        b'p6q1cetn9cjGbfUxcGjfxuj72mNge8ZSoolu4OVTqEFNuhG7/hln17vyCLWTUkSfzDe/aQvi1JNjU4Kqq2x/hVGTHgr3kTtV1Hjuw8OYRxP1Z/pPeGWNIqIz0pPj4vrI'
        b'U6rNk5GZkvudyQMK6mPf5VlFy8G8kv9UIeIfyfvAUFsAB+Z9kBCndjfYQN07SIvHJtEgkZi/kvddswidOdxHIUy0hWC+T9TvIZ5CvGkdA/8Cq+5DkIrNtFmO7x2pWD9j'
        b'db5sMdXC+VGNVAv9zo0DAg1byRE3GW4RmHFAZMYBYau4tOvAQC+xnjjfeuZodWK5xYmPyNBKQYQzxB4gA+k/PTogfQ8KlUK1NjkjMYaRtcamMahwRVR8FPW76DEtLaeS'
        b'Z2JsFPVAUsxn8Sa0E9VYt8xtT436rfbfSegZK1cNCB4ZGZaWERsZyalkYxUO65OT0pOjKb2sgyIxYU1aFEmc+mhpUHV75flLf2A2U9x79WE+xxTkvl/ZOi5VD0dGj4z0'
        b'jkpUkRI+iObHAqUEnX/iA10sDUoYuNNdoqKC5nnp5S8in15jHPfe7RFeRLYqETuiwpQiE5ncF+AeXTHCOocJEkyMGLpNc8TS7VBHFhcfy+HLGInltm4/wzeN0dtPVNGJ'
        b'Eaxhu84saAK9cb+KGsTMLlgyioVvJVMfU3fbNHOFb8x0ts0M6oKzBs4NluvLX7jHUVdWwr12VtBKBLjiYKoiQTtW+TO4VGzGDnM3opVd+S+RxvZo99WeaunafSmKaRBe'
        b'VNsldjlq5UBqTCkOcPBzopTBRdz6C7uggtwQwPhZz0GxfDqWpSa898N4AxUVKVe/afFFpIvN55G319jbOUQFMGvvvchPI5PiypruRZbE+0WR8RBgJOyVG9ssL1VKmSA6'
        b'IQv2dM9cI4QSPWKfriAK+8cx7L4NS6P1QXUbPXRwdaEQtnPBux1ac2KZmqEvs7Khtgz3PZJJmAw9lXro2fU09Eayg8WHDz+SiCa/Ljj+Pmlcu25jIzKSjMjBvY7IT226'
        b'j0gxHg48bERCtaL7kHQMokPy4hDzmZAHZ5WSDGoJXwE3oZqMVtU6clFmKcLpqAXsQuaq6eSJpdhEv58oQmsQViac+HeKhPGxTl+Ttj7eJzqADIZ175+JXRu/Nj4x3i86'
        b'KCrouZ+jxG8GrR+4bmDo0k/cDCamxAnCE04mUcddNEeXuvbyXvvGRNvSvXeQnZmplWyTXc8dpMmt947Q2WajSA9Y9toD31rpitK95PdfYCrnIsFDZzdZjv81Ll2ioiaQ'
        b'cf+a8AWZiLfXrI0zI0syubXq228kj2dvIEsys6UeWCHtU/fU1TvhtBdVPSEX+uLkZsezvS/Y9g+cYjB3il7W5964uWkeI3vtkPct+jo10Xff+KtCSY+d8eDeKAsKS7B1'
        b'my6q6NfPjv3g5d/9o0hPBEgF2XjRfs3iLoHuQbeCI0JfDen4gNLGfUUefaej6Y/ptRHfMetLQezmrfmftGL8ww8qyZA+eznBQEVNiUqLYscoylm/8m+Xdh+rdd+f12og'
        b'jLE7YSqzTK0hewsDwD0FpydiqZOvM1Y5SwTZHBHaoA1L0iezMW8zuo8xv8xSf9TTIR+qZMmmGAc6+kelUCOrs6FgjFclsAfOw8Fe+s+8z4ng8qDSzf1TH7n/aPrje+2/'
        b'N/vsvy5fWEHvAHGopu3XCOwAkR7OmzGtQHM8Lym0ZjKJ3iF9oUHhIHawOLhwSOHQuKHaw0X5ox8uUoct2we63imI0S5gqScU0JO5CzrnXngcS/nJl4K8wFX/LfI0bNsC'
        b'B7DNkh6YsFMcK6iX4BVTKOYMmiehdBU7yPEh3RgMjdrTHDzj3MOBjqGABRvlZOxcf0xpyDa+mH52KmwXoJZkjLsFKIPmhexEJQxPw2lszTDEfYPJpSMUSnnnQPYMXMtQ'
        b'yLHdYBO5D9sEODYVj7MLeHQM1KjSRdzpQU1zAhSYumRwokRS1xa5SkbkrV3k0gUB9ofiVXaGZZ0zQpUlwfy15PtKAUrmTGfHPLe2GPr1k5Jxqoh0CpntLHCOzMsrbOnJ'
        b'lgzOR9LTLwH2QilW8SOgihgfWhUiBp5T1wUvjc6gsO7kkYMLWDN1O+vC5vQ06Wi8FOrjSA3rrIVgN+w3yYFTnixVZ2/jibh7optszWRBJK2AuXgdDjG6DecsOKh3xEoB'
        b'VVYksCPfhUuwZqJfqJEQjvsNsU0B+RnWtIzN2DqH+gS5C9lw0d1kPG+2S3gOriN19nIVEqDGdRLuSPzpjz/+iB5vMO8APdqdE5k4z3q+kDGX3O3laOSvgW4h0qwP4/Yu'
        b'd/WDWqgJt8diUoxQeyXuWuLjS2WjskAmEYXQqhkmma9asZSRhJNn2rCQ2m1176PDiIpRrsGBEptFD2CM0/FzDq6aYQtcWpNB5xTenA0V5uSRPeaQ62ZsgLnheNgQK8LM'
        b'vW0GG8/Eq9AUAldJ5Q7jBa/4jSZxA1JN8ZphljGUmASbkebYgfVueH2zcgQWzXDBA4awz1MJrY9NwtqBsB/y8WRGGMlmMDZgpQHmYZ654G4sheZwaFmONYZQjIVQ4wA7'
        b'8ToSqT5sSMJWOIO5Q+D6ulFDoIOM5nxoj9uMO6Xu9qQI5SvxwAi8OL9f4Bw8x1YLNtQ6pg5ZtlG6ViZYRa76KsxTyKDkhdIsLOjOIhthzk7/teedWipZyjrbIY/GQ7NY'
        b'gqUhPovdODGtw1nZUiEjmPb96SQ8TutQayIozMiHxauh2HM9VJLJcQWPie6wHU/OIOs8VkWSGdqIB8LH44nlpNi5/cNgeywUxeNRvGy0Fq5ZZQ/OYIWEvZgv15TSCo/r'
        b'0t36OPsZ2PSnTi3QoCT/ydTCcybYAednEBWWrzH7SDfQMUB0kst40xUrfJ3IWkG6eYCxzC3Hj/ky4PX+sN3/kRlxDX0ELFGaJWDBvAw60jfjDTilPTGGK5DHTo17PzNe'
        b'NE/JKR3J4NkFdY5BsG84VoiCBCpET+zAIxkLaNEboAAuOvrQlSWQzwRXP19KdUP9Abp7HSzyIfpfCl0AFoY4L5asHCVkh1lm4yXrjHCaVsG4EH5I77tI7aKh1h59AoJZ'
        b'bV0WGWdiO1zA7Yt8/AKDnJyDwjmjsI53AFuesSzEmizKO7GKDQSD6RLj16X0U2TAN76LBHXNRq7CAn9+oiMlG2+zJAAroSg0JiOEluYmWfHLQ4OVgRxnPnxJD74nAhn5'
        b'ZyGX9G4llq1UkGX1MtT7jISbPrg/c+REuCATsAXzbKB2LbZksOOsPSZ09cFWSxNjbLHE1vTUDDF7kWCrkgbPWJbBgeZxv2coXbikjtBMlrtGARth+zzmR7hwEzb5K52Z'
        b'Ph1ESmUPBYP1pWqpsEphDNvDB7LEti0aGArlYVhOOYMMHMT1ElKtMjzFfVn2ZSnkmTOx0kIk2ewlqwq2rOCsQXtg11JSzEsqbDXCGjwmSPC86AyFeFJpzfeAUji3EksD'
        b'RLgOJwRxmkA0wdNQxTK1nDyAud2sXMzdMeTLJdgE+7M4iXIN7E7kx77SAbBffepLOvUIL9POrVDojyVL4WSAIT9BvenMcnwM6frCvBIMcPc2QTZchOPjN7PyGsIpOMsH'
        b'Dx6Dg45KOCsTzKyk/b1TMsYIVOMsjCKjX8l0fIq+z481DRKxWBgHuQZxK/A88xTB3akB2nWd8jvvl5AkT0MNXoGbbCsajYWCI5k39m78cM4sXmopRrGye+IJd048cAyb'
        b'OfFAZCJrkY2LsYlMvUtY7xzETh8NV0n6w5Hh7DEbrNuGpfSMNidakE0RoUGEGr7FN07BHXTSS8fNY/U9sXEjKwTWxVCWBHrFWuQs1ZGYy1eTPDcsdlRPbDJ2ycxO8vc1'
        b'EEZClYEJlHlxJ6FzpDRnyS9T1aHYtYe2cZ0qBEGeEeWHWsIynYZXIuiJuZKsTCbTJQPwMpwcrkyY6Pa5RJVDBJdPX/7JK/RqUr+5todqD+Vs/FeGzc3XgySpw2d6HXIY'
        b'MWduXq7NolVea5e0HG97bplyjcEV75aPKkc98aXlwm8H2RtMjvibUf0Ht+/kweHNL8765K3aGa0zX5jv7Fu5Lky5NH7d1sDD1tkLZ0ZsrM8++NmeMx+N992q3PPzsjnb'
        b't7+4bpSfwe9/3J747MbOJStbm9DbNmbm6PdVG2zzOx3snjxhXzh7y4on37zc8uL2D/z+efwnw2vP/253pPmIV03jilcTYhqU7oNXZ3n/w31seb2Lx/23Jm4dq3w649/y'
        b'z4ed+GrVxGmxw05//cXjm2yzIu/dfXZv61PKr1R/hISvcy6Vf5n6+bWZMaEpPw51zLnwbGRt2trtfk0f/zrMYdaK2vLpzabNEarlhq9GnJoY+NsEt7mHJh3/cspxGT75'
        b'UofzgC9OPaf4x0s5ef94KeOzZVmDp39nuPbzlyxaVth7/LFu9sIhyetS7r2084clz/7rh89/squRLvHd/dv7MRerCqdItj79zA+3P0zMOl/y7fPmG44HROXcmvHG4fJb'
        b'n768o3/zz9OrLZ3bX35hzfBXczzW1dsO9fzWpl9ZdkfLfcu32u68NuQARM15yrGtLF761P5p3rdGPznLNbqwbeiTQ//hGfDJ4UHL0re2Dny5+M1/iddCfnnSzSTj+0NB'
        b'n92+YRnkfv6oWWDR/WmW733Xb3POpVnvy35Ovrr35XspX7jf+mPr2OyiCqPvLu+pcRmd9fr4zuWbnyia/8aaI1ekF7+Lt940PM4y1+eHl7yuzrrz2ae3gz4yvqn8ZVzu'
        b'NzW3hkXAh6YX3gv5wPbDe3fmv+XuHPTWjxNOnv4u8TXHDR/X7x0Hm5Pqfrhbty3WIO42Ptvqk7POaqqf6SvtK/utMt4M92/vzPx83FbH5SP+kFysNfjtpWDlWHZQHxkK'
        b'J9ReDWQJp44NarcG2D6Vs503roUS/2A4AtfV3FKbsI1zYx0hUmUHWXqwaKJ66YGyx5inyWi8sYX6wUwM70ZOjsfwAtPiNobgCY3XnYFgDG2SORaZcHw5Zxc/mwk72Yo4'
        b'AFp1l8TjK9nD1mQbyVMviVFEZOZL4uQxzOFkjLeCe+gocG+Qs4/GRWfoQK6UNmHDBsdIumSqSUIkw/EonOD8IZ3YOczRwUWJJUR9NlkmcVgJJ5fBTUbZAvvxEJ503AoH'
        b'KSNdsRNZk6BC4gwnU1m2phbJ/lqZk7G5QHFWIhyTMqKvLLgIjdStggotwVrJNQELlYbCCH8ZHh7Uj5fvwmzqHVg3RF0IQ2iUTJyPZ3mLl4YPcUwcq+OdQ1bao+lsgdpl'
        b'A6dUUG6cao4tKuo+14O7DLYZYsEyuGEFB9hZAGnaRWqT5Ew8o7HP2vhK4WgmnuRELZfwBNspmGW4wAwqgqm7jmCNhVKiqVyG/dzfY89cJVCqeFdnxiFoJFgGS6F08lpS'
        b'PO4+VOI/wjHYCUtUWMeIzMgwwxsSItdVRbGKD1qLRXrCBXb4QFGMAaM3W70ab/KNoiGa7xO29swpYi7sgHPcaXkNbtfz2CL75hFOd18AeyOhdCYrnMbfJcM8nXEP7k2c'
        b'0avnxmW8Rr031K4b2Mqpa+DiEMyjU0bPW8iDbOrMYQiL57AeVxknMh+Wbv4rRPNr5j4sWLyRt8x2OAP1ji5KP0ctAV2udAHuSZ41k5V/6ixzIitTkruFjJ1NniTBuugl'
        b'7JojlMBxvq9ZEYGEbWxwaBOvd7VlkHr7n070Xbb9b4EaNsPkoYP47g9NsKNr94dWqGMuOOZweX5P+386FPD9n2g2N7m/0Q3YE0HK57we9+l4C9lhgczGeBV3rmmBCiIe'
        b'9mnhnAB13cw9TnCR0xMdwtOp/gHYDPW+ZAEKER3wAFziBIBn4fISPWo7PGWTDQc9lWb/ibOLcuj/IIzqn3/psrdbdsOQZHatlwThQbvWBGp8NWakLlaMSMiKUuRJODia'
        b'sRomzY5cp1epfYqCsFEobxn5LFNTDlvwX5IS/WRDPtE0bBjFnhV12SEpmLH4Lgq9RpntLdg7dQCyIGlTtx9TCQ3d5T9dELESkoKEvfMfGp5LSWjM1GnxQDytpaxbtXX9'
        b'fbgvDgu06kdfBjBXn9iNWjcBnbilLjte//9rvafxFrLRhlDREjI6HV6oflqXIY6tS/506NWceGeeHmlgX42kFFnYVlAfh5r0WFNkaLgPP9SUMkOh7P03JD0c/8+NS6fE'
        b'gFGJiQzrU4dulxQqgZYmKlEPApRDRcXEcCS8KEVSbNYDiXK3EfvIyIUb0n2T4iIjFWsSk6PXK13UcK0ah4IMVWxcRiI91c9OzlBkRXG2wpgESjD4IBWwbiESktiNcSzS'
        b'XR0bGaviAZMcnU9BMYcUCTGqR+cCpAH6HgpfdrBPxp8qgUKiknzoIX+UIjpDlZ68gSerrZpvTGSkksK39OoLQdpH0x70Y0KSInOqC2WYnkeaMYs2ZvraqHRtabvcLXpM'
        b'UV03htPKPIO4UwNJgKK26jWRJvQ0Pi05I4WBt/WYIql6ekJ0RmJUGnfbUBPCc9wBlcKeBn07kSYg2TI4kOwU8mdserSLknVCL24btEHTYzX9ou535rSV1J30Ud37Mcks'
        b'8DWFIvz2lKZeB/RBmigKPZEmmgYx9XMhnk5ch026sR/Ga7ss4HP64wUeM8ACBuYE64UMhMZlBDC5A1pM1JZBhbGU2h+vpLph9eDhPv3GpubghRDIh/PT4LwnVK+Y55sO'
        b'54ia3mw8K8hpGB4kQvTB+XB1xCY4a+XWP4CZbFYM8xF2C/vtjSMjTZ9wnSdk0F082hJOE0WZyK1FfoGhlN92Fw03oUE8RsKodTI8Nwbq2OMXQml0Qq6b0ZxIsx+UgUJC'
        b'lstFmSqTXOl/9cTYZ6+b73Cz9Xr/l8PlPw9SeMbkTUoU+5s/77w7Ybdn7aRj2YlRyYPHXDkR/NSkUfL85d/Jr1i+vnvTK2c+65xx/9yv0sJfH//6y+c/PqsoWDngoFv9'
        b'yy6zd772+SuXp5r92Bm487O3Dmx6/OKAiu/lJZ2jDS89N6LgsSFHNsxRyrlsdGRCEhW1ygZr3K412sm5IUwwtIwboea8xQJoEufCKSIaUBPjqAgiGfYlccxe0/18iQh0'
        b'+UyoXIbnR6hcyM3nfYKc7TVWImvcLYXmNNzD3cEridynVWDw+kSmw2TCYdjHxNmtgdAyGg/rOaNjC1al0yEVtMCee6MLkhw4IorekgFqMkcogv1Zw3X97zeRBJmhpZEI'
        b'elc1wQWK8TpK1Tgn5sk+C9rxSJdgWmer78mO5VjCPd6PTsKy7rJpcL8u72p5vOag62HOGSY0+I3NTyaK2PckimwTplHxgYoVRLyQUpGDChvdjui1CekzG9rp79s9uGnY'
        b'6e+fseTPE3T/VPS0f+YK79r07iagLQP1tSTbSgTZV7RB/5pY0N689KRF0l4jQTWb50+yHjbP0NgkNSynPhZ4hopvprFsOSNrr9c8X89QHXzv3nag2DUJ0aqI6MQEkgpn'
        b'pNUAHsVRgMLotS7sDhcv+urJbusNNlwnVXV7eDA/Pyetox8FslXFsmImp8XQL8ja3uPaq4ZB77UMLt7hAZEM5CwjJTE5KkZTe02D9JgoRcvUgpbRbUHt5KrKSEjnYOTa'
        b'QvW8Izy0VJ6eYZFOf/XR8L/8qO/Cv/ro3KXL/3Ku8+f/9Ufn/dVHl3pN+OuPToxU9CI3PcLDk3pxtfSN42woXIqJjXFSOKiHv4Oev6a+QynzNetZ7OjNTdQ7LYphQneN'
        b'4T/jEbqECqp8Vcic6OKmN1uYJyvHYuXTiWSYmRD111pqXlh4D0XoYqymawwvB59uCTF9yFYyQYdxVStb9eOE1COcjAQzW6KzKCLNfhm5XGBW/UGr5qqgBRvl9LD/qAC1'
        b'iXBaHT4ZmYStbm5uBoLEV5iHV/BwDlzOoClDq2OIY5CLKIwJkcBe0R9rPJjwZr4A2x2D/CTUdnBNAtvFaQuwkJ8dtBuZOQb5ioI7tEqgSJwJxzyUMub3EIg1UM0OobDF'
        b'QJAOFvGg0SzYhy3srCJwyVRyrTkdO8h+jjUiHIPDI/GqH0t13iYsVE0ge9oMuCgmC9CxGlp42a9g/VwVtluSfUuCp8SALAds7cfDY3dBPlayg/XhJq6Cq300L2D5loUq'
        b'FR6msiR3FJg9SynhjgoluN1et4DTsHLWtDBWeCI2HF6jV0DRYCSRNG7yJ1vgOFzVKUdMigM0ePMg4xseeENd+Ous8J7QopSy54Kgbo1ei5zG6lluY7mbyE684anfJIfm'
        b'jMyAYtYzI2eNkWeakJ6XmohwAqtd04JY9Tywc5vcPM1SEKRO4iA8PBsrVvOTs+NYaEPP1uQWoiA1EyHPZHYQXMmg+PFbSJ/X+lOJNpQhJNDoXiLikmegcgsRoctIWfI3'
        b'wTWohoNh5O9qvIb1pG0PYjVcszHAmjUG5uQlkDR42UxFP9LGNpZwBs7jpYS5QR1S1Xckj11zZOEvzQp63M3K4L3a1Cl195LtxozxcAi65fyR3d9Tcl82feLpfK+L+Z7i'
        b'vAnDDMbmv5JqPN8r8HlxmkF/12fsrqZN/P2f2U4z0jzNHZWzn5neZuv1jN3vo3aX1MQXf7Cq3vvVpR8eilva7/mM+3vH9ut8xiNpevPN10YFNr8oTTYYt+eVSyden+/n'
        b'tTvSo+GZnF2hv72Qc8xhUc4PE9PjVH+UxAzq/PCAYd2JXyzqht2R/CDW7frnl0arPvjO9Wz+H3OTO18MXf6v0H94rov9OP/XEVty3FLNYyPmnvvw6rF9Lz3/73+95Pjp'
        b'M2eyTi//PvnLq3nt/ywb/rO4bVlo9reWBbtW3Xz1e6Utpyk/PmODBhDgMbyhscPjgRxuf2tPx061HZ4Z4acTAbQODqzgwnsBlGOdozqgLT6SCtFmTlIjbIVcJrzjDiLu'
        b'XmHye+pwerIwAFp4unm4B6848jBJGewUqUf0Dtxtz65ukBOFRh1RyuJJ4/A0XLSGg9yGXz9jjVouXww71WcLmS6becI74IjKkdrofZPNibhrjKUSyIN6Jy5+FxFJv1Ul'
        b'xzZRwNNDRSwV8ExYOitrIOb5QWnKZImwJUfEQjL/+s1i5yMbcdd6esFQiFsr0pG3B4tH8BBHPBdEr4jCFmgTsVjAStiFl5j6sBYKRujEaMoEi6UCDdEMwk6WncciyFVl'
        b'kvE+ikySUwLWwfn5/HzgGBmchSoogyKJEBMlknUAL2H+cn4+cGI9XCOPGVCbd4UIpwU8aBXJirmB6DctZJqbCcImLxGaBDzka8FBPaJwlyozlVR5u6cI+wXSBnuxg6dX'
        b'i8c8yDWyWh5QirBXwBIz4JGXfkm4T/WgghQxHJrx9MpeghH7cCWWqYgYzJSIxT0rEZFUbaB2RUpTLVNbMSl4H7Ncqn/MWKCgqURjR9T+EuXDWNxkre8VTHIM0kCHsNhB'
        b'M13ROS1OX/cQNXVI0Goccdogv7Xk060+1I5bet7JD5aDpC5lmQTR/wO6QTHdlUUE+wbdlUd4hoeEeAV5+nqFctRJLUTTXXlKVEKSOgKQhSHeNe0KkVMHLNKbu0UtRulD'
        b'OTFkJ2qCZHoUqxVvoMH/L9nB01ypkidVg68ZG1lJad9bSC0MBs6RkE+PDAkpsbIyk1hQgjHZlI3Gou0wY+5gtBQvr4BreKGb/74oDF4gSwiBy3qOsmbqd5WDqM82RtGm'
        b'ONLUQZkaa4p/pohTJuSHfqbIUxR3in/f9dmKQjvG9GOfbWP6az/bxQwgnweyz4NiBscMiRl6UE55zAoN48SYYTHDdxpTaMlqo2oxRl5tVm1cbUN/YkaUG8W4F1IkK0Oi'
        b'so6JGcuQmYwY/9f4nUKMfYyS8pvR56rl1ZI4CXmqH/m1qrZJ4H/ZkNRsqk2qTeNkMQ4xjiS9CRQli6ZYaFJoXmhTaBtnzLClaMomzD3VkLmrWscZxrjGuO00plCWMmG5'
        b'nHltT7xrQ6eBJ2M9YJhkcbFp9yfoCY4P3qCm79K96b4LkUI9ElTJHqr0GPY+wc1twgQPKsx6bFTFeNCp4eLm5k5+iZg8USm9KwsKDgm8K/PxXeBzVxYesmAh0fgl873I'
        b'qwnNMiI4KGAZWcOovn/XgCmPd004SUUC+WgQR1Rg1Z/J1p1mK0tLpfMpjb6o6AyV+QaFcnjCP5nWdLJg6aeVtoklGDp/8dz789amp6d4uLpmZWW5qBI2OlOxPo3GezpH'
        b'q6PpXKKTN7jGxLp2K6ELEf7dJriQ/JSSrvTJZwqQlbaABf3eNQkI9pwbEEGk/fvjaKE95/myEpL3hVHZdEELoWZeVTpJ1MVtEnkla1sqDxiezJOjIYR3zUJ9gxYEeEXM'
        b'mxvm6fOISbmT1TdVr8r3p3Z70DMtWaWax9QQ/TQCkuMDVfEsJXeakqQrJVKyXJqWZbf2uD+490rd799j4ynleqnQ4fZgst2+mN5LWt2/ns6+7rtUvV9zv+/4J5rnrlFM'
        b'bFxURmI66zM2AP4rYQYPxMX1FKzB9aPTKXBJnqn2tIPCWDwH2zMSdvvNMmBhHDNKPXkQh5HgaC6zF5XDn+gjjOOuMaUUTSdjv/dIJfqzgMON6q85LppnHz0qYBep1yzy'
        b'STWqZ3kgV3hCLzKgr1yVRnz/XtjDJh6i3cnpaP6MIo+FBenFEphqGpgGG7JYAkFDg8lhyOJMtXECpr3GCXCqONn72416sGD68ijchE2xOnZMzmbDT5Pout2H3TJUwzqr'
        b'SGGcA0yIUXk8eKOzotvcUtiTRbvv2+h8eugd0xX2DqoEejSVOdVlisMjJMmnqMLe0+fhN6snLr3ZSfGwfHqf3Ap737A/9YR7H0886kJAk+he6N5MxGozF7cH8QBpNY+R'
        b'Bkm/tyfpFssf6z5sUtISktMS0rM58q29A924KT8U3boderYaOtANnd5Dt1cHaiJ2oPuig9Kl6/R0issEFzcP9S09J9N10OrGblWn2vX1FPY1T7q3inHABnXVegBj4O0z'
        b'XsXwGHptHnYo4aEfYc8mWc/QCuoI+V7L1IWh4KFlSH0QJIECFmjP2ns4Sqf/yDVGZ0et9sxays75Y6PS6YBSaai+dBAn6ElzL2H61OJK0smKSlO7BegwMbDWUYTGxtK6'
        b'ZiTqsIf1mJTn3DCvBcEhyyIovU1wqFcE5TcJZaXUHslzTrNeG4kvQrx9GAeRGrxE028a5U1tK+75BLvLfszOJHgKXeZdh25rikOvPgCsh1L4PFVxRrRuS4wDr53mloSk'
        b'njEEOBoFEWI1hK9ro5IUXuEhvdjBkxShWQnpm2LTElnHpfdReL4g9jKXyITxTY9KzGYP9r7COfQ+ZtUwGrxDutA16MhXd4kWaYMfSfVSo3Tu0qADja33rB5GSq+rFkvp'
        b'gTMC0jxqoUmlGb7d0u25T9QkgV35MnLGNbGJyUnxNKU+bOlUHjF5QIKyDGJ20xkDaFCOP1bE4yHcLRUkeEK0XxXIrgWvw70aBwa4BA3UicEPznAvBmYLK6Du9xS3k5rp'
        b'Gjhy54pUBnc4KBUqqWoMZdhBflqhaSMUywRz3CnB0sWreaBWDVyN8NcNwlqsH90CRUm+3XEuAw38JMJk2GGBO9euU0qYEdofzoYy46/bJG7+nT1Ybf2XCVAjN0+DdjzB'
        b'jcaz8RJ0ZlD8FrgAO7BaB8q0qyDaqJQUc/MQimRq7xwEe7E23N4eS7DMFUucKIYlx+d0NiTS575+ItRu8eZS6bllRgx3U4C2ERx3Exsj2dFFxXKOfuo27ulZT01xEXgU'
        b'UiHmTtFF4/Rx8QvEYlJn1xAsCljkIw2BYhq6hp1wcmNi9lgBbsrkuH+iYcIF0z+kKmqViXWfNbbc3xTmWM0/vbny5zHL5EnXK1fcCjyxO/fpMc8Z31JUz9i1e+XI8ZcW'
        b'TDX/qn/4rIEDd9YOkIyGW8dzF3RuCnn3mzflt7K+3POMS37znZoR9WF+Lw91fWOS7/SQT/6ekPJBS/7Nr1+4/d2Y+S/HXVlvY/VH0qTfxli/f2/bVPvkr/2r1538rnPY'
        b'3zaM9f58wFffPrX8l7orp95NP/mMfE3FuNU3letdv/vHOKU5s1jOjVnr6OJM3RagJtUQ6iVuAas4DkQnkdyPc2RgimXsBMUmUEDxgS1CpO7z4DIzlmYOd9F3B4/Cwsxh'
        b'g7jrw1F6VKOF3oNSrNX4gaSmsswnBmIRsyOHYhM1JMMJOMwM2F4k55OaYbhopNozO1GA48yKuXIMVujjNVKHCriA142h3YrdkgZnoLDLVGuH1T4aOL1KuMk8gh+LzlLf'
        b'ELxM2gM039mBzB4+2hiL9QEUBypka7xW4024yGy7tribpFMa4Bcq0RjUoS4B6rnpei9eRNKMdMrBZRe8RG4IFL37z+BOso0L4RSZ6gGigMewXLJGdA+DFr3IfdP/yOSm'
        b'RX3z6E112mIjmqqdTikmh4yZZ2Xsl/L0Wkgk4uBeFB010lnQg46dfes8fTiG/AWQtsA+9bW24Q/V1/4cIcldgwgq0/aBKVVOPnG4tp6y07IMuzyC3Pwg1Bq1goX6zA25'
        b'K6MsondllFBUo2nqu9NyZ1Xqu3rXSM1CnVYtdgtZt9TsQj6CNmSdK5pmalXTnGNeF1rGWT5CYLoGbupMTwrn3JgYlT5bsmbD7cFgqBXVHtRb4xQeVJD0iNQChET2cL7v'
        b'pBZ8tMhV1FXyQc/S7oyAnPaW6vBd4mw6bb10tbD/SGqUWgDWcsM+TJPiJFL82R4oXKNUirjE5ChqVlAwvlI1PWNvzjVRSXrkaN2ZX3srhZ560RM1a3rsRi47p2sZTTdw'
        b'N89e/DbJPQkxVPDraoouejleB4U94zenVWOC3agQbxcXl1HKXkRS7iLBfJCj6GjSYTPWpsyJHLmo3HW9x/S0z3TxMqqHgNp9S5+lscc07EO8vL3oAY9XRFB44DyvECeF'
        b'RoPhRJa9unwxp+PeiUyTU7gTdh8pbOxJKeyFNbSP5Og/rc5IW7gvlU6LpqYe1T2mpqGj7kn7U5BW8QoJmhvwoKbXs5/yI2p/GqIq3hRaQl86YNXjhs4LojDHMrbmyMig'
        b'5CS6UvThwL0xvSt3RvxK2ygqkTpN0wVCO3Tj0pI3kKaKierF0zoxgxvZ4hMyY5M0I59MzRjq6mMfnZykSiDNRVMiDZfAviWt3GvBeDK6pgmlbjXV9MZr1sVGp/P1oGdl'
        b'KDR42hQ3dwUnYOX1oWVwUqNsquvLbAV0bpJFscd04jLS2Fxjs51TqfaqEfKdyEMRqtbANDTn1Bc9m+SSmEgmX1Qa18P4zT2vLSpVcnQC6wStPpiSlkzZymkrkqZVdzaZ'
        b'CHzY99yYOoSBiiCiGUalpCQmRDMnRKqas/mk61vf89zxVLOld1GS0k1aYU9elU4KulUr7IPDQ5S0M+iWrbCf5xXUyzx00AkWmKJ0eIQQBq1H11ztUt+NMagvT1GtWmrc'
        b'o1o6gqul0IZHt2Ghja7/PFYZM9mHKVI/56hpJFZEJQZvduU+YIZwI01ljvljiULKldF51t7Mn8gzzUCldomKoZAwZe5x7Anb2f0Y5gp1i+gHNUSA3jggjMP6V2ETHNTT'
        b'YIn6agTnuAYLu2BnBqX0jIiAq0ihsM8NYMQGlPMizJ77j/s7Oyz2cfIL1wFr6KbLclSWC17WRGY/gMVcfSyDliUaVyaomEvV2fXrMpaQS1aYh1ewVM2h0FtW66FeP7cu'
        b'VphF9lpUCaWh4OFmi83YmswxAhpToYj7Vs2A7VRThoYJGZSqMA46FP4MbcfZL5hqyjwRA6zEfNOxg6AhB8pMuzTUOaSQB8m14zaQD/VhcDRmERTP2woHYDucIz8nyHvB'
        b'+o2wG07NW7MaSualJSxatG512tiVULt+rZWAFbOGwkGoDmGOczMwH0rl2J5iJhGwBTokeE10DYeTDE9iAJ4Z3mvJsHgQFM+BPWsgX688+Xgcq/0S6V/U/SvSEgsVRDda'
        b'ZD0QW6eyHnCC47iX+59h2UipiegK++BGRhS5NNQfdmhNBsrFamydlIyMMNydYm6JlWHqNtexJlAjAu0bDf6GBoYG8uDMFOgwZhlZYJEdnl8fkjGL5JI8bEuPyEcabB/6'
        b'SJimK48t572JbVBoviBkWYY31wTLVvtreIEg14s6vpUTDZANGpKuP4MDISOpykDlByU2ZHyXYFUIUcFLRLyZar6AhiJn+NHuz1nvr0swRFOxhes+XUrsYr30IF8O1bZj'
        b'8VR/OA0n7fpLBagNtIaTqyazuvni9mhSOZ/o7ohFEqKUVpN8Ls0kPbMdd5KWZR54ULlGwMIQs5CpsI+hzdivwTYds02Ar9LP2UVD9wE7humhIKkLZa4/V0hrHcqwgT1Y'
        b'hUcZTsoozPVVIzfscsCyRT69pf9IiYf42cK1qMlsMC3HI6mqTKwKowYhbg2Csn7Mk4ctNCSJNijTMtDgObygZqHhFDRwwpQyFCbsrTtloDpJVKpPg38KXHQ96dU5Vu8M'
        b'23z9h0M5+1ZWjs6z9/Ibvn28j8Gs8V6jd1/7e949W+Xr5uPrfc9ull0NvjVa4eDwuLR+5r+N7ce+++V0m/L4G0cGvXj72fkhi4as23d8d83kb65aZQQ31hp+brsw5HTj'
        b'tJ/94s++8s3sUWdOjb9g9PbYytdLQo9sUcTXrZ+y6sqNr39YeGDigufPj28fmWYx5ce7VSdcaupfNPw+4eoFWfTlr5+NfX7H1H9h+ccm9z/xb3s5YlLL9tOf/nvIXcu1'
        b'sTEbfvFv2TrhzIyrW4fM6j8z+Otf8+LtZhV84pLwu2SE7NrWYTmFFe1XOr8zfNfgktd3475PP/em/3sn/n3hxRmxX78t3de4Mu/aD+MU+x6f+WXxvcEr+x8Pfvm095EP'
        b'LwY/8+THxwotBzSteXvWd1VHC5V3VzW+8cQXsoypQd+aN3087W2zX7Men/7Tkfciyt7+8dno29vbd2R6rMve9rf4HQW/jzn13OvKm/da6jzz2o9tHblxeq2fS/7SI+bt'
        b'rWuurRpWXnNhoe/z/cfV//P5b/Olo2tu3/9QvCD90fdO8YupY9e9U2i+JPyt7Be3WHQsr3nnRugTT22zm3fxx8h1Sjt1yHsQtHRZOMladpYbl8Khnd9waLGoQxgheqtt'
        b'VlgGucwnbzBcDPMPJmOmUY2sANfwBscaaFkCx7XzAKuXqR0vw9z45RLct03jd2mHldxSRFI+z+KXrPECVhjGQGnWAwwjkIt5rHDxcHKdlsjEAvdqYBLgFF7icd01Htik'
        b'to0thmu6IA6QN4zDNDSGYrNjEJ6M1DXcZUI1XuW+isV4bKrai5PstO3Mk3OHcTJ3trwm9ZqLxyjsrC80ygTDRMkoO2hkDSPdgqf9scQMyzS4EruRtymWL43T8ZuEs2vV'
        b'xrgppNEpU8ZqsrtepnfI4CQ1yPVgjjuIHTyEqw7r4LS/er2Hs1uwmkfBS6Zx59cjsAdKyXUnSrBGlpODMieR0gA9xoqSBB1ruDkvCip1LHqrt0ABq/5wstLd8IVTarMo'
        b's4liPZxi5UzFPdH+Ab5QzOLRsMhfF5DIDS4bumI9cm/YgCUGbBiRfSbYeRkUGgoW86WzoHkj93fNG4WNZIxd1Qs1W5rBzIIjI/EoXJ8Gpa6BzkpShFkShQdcVBo/cvSy'
        b'5f+MA98aDShjUW/WxG3CY6aimYQFqEvMRBrObiUxlBqLNlY8rJyGqlOeCc0nY+b2aagOP7eSDpQMJO/0144Fs1PWCVvR2MCCRqJJmK1SYiHasNRp4LmhZNOoHqxs3aKq'
        b'ezBR9mYsS9un7z/66I2uGzK+r4e48R5CxndT2+WY3myXucI39rrWy0eoaM/ePhSVkBn1uO+IEGeo9fuR9okcH6+U3Y98QGEIiU0iuqrqYZY7ZiZQqyZUMY1SKZYGBvSh'
        b'f1DMwuEP6B9OQQyI0MIDmvw1Tp2dUMSp7vQh4kqX2D8AvYsH4bx5//FEUFHQaVfrATcdByzoxi7H93VsG8+h4E7CBTjFz4tEd9zLz4tqN7MUpLADrtNr6S5kaXXJTPMm'
        b'b340CHPMaoOp3oZMwiCy9BmaOnkeC7B5OIV5PBHNEh9Mlzp6vKc525P72BNdpoDpUM8PkbBAGzfvlZOe7N+Ps41h+TY8ymAhBZLcYeGxzXAzwoqHy1yB/X72UKtGc3SF'
        b'a9u4spYHRelyEyLSiHCTbB4NRPFaC3tYct6+cNFR6UCWfVm2CNVuRDdohE72mFE/IkxfpicSZcogA8HQTmKGNbCdXQuE9n6h5OJRLJdRbVAg+tZF3M+uqUYM5kBuDMVN'
        b'wJskxQKijdEiJkKHvzY+BNrls0eP4I3csSVRL9hkJRHsB2Erv1gPp+fqxqlAnnQWlqdzAMt9Y/rJGY8hyW8qtDlAyUimLw3xiNGJN1lmOBuO4Q0GRyeD3XGhUI7V4ViO'
        b'NURXiQoUBeNgES9hJ1azpi+I3CUMFYWBbgvWj3tJtZjrtK2mo4X5tD/cPe0q5iXyL4+M9RV2k+/cwsM8JybKBD2aYe2co2OF0QzbkVkmHBW2iDFCjJgvGSQc0xAOxxMp'
        b'8jOqGtDA1bkxaQEJSbEaymFZIv3jQVhc8rLKUMs7zBSLxXA5lrk88zNKE43Ui5UsZEIMmTKd1LIYiqdjfia0YNkc77hU37StSUQgELZMsCLdeBkvsao9NtJcIO1v72b3'
        b'zIS2yfG8vgdJHzvRE9LVe2M/mOoksBYNT1xA+4fotdW6EH8M4C98Dj+Lrh2I9Wo9keqIUBjsaoIHWVflwCEbcinVXCpIbcUkrJ8RhcdZbh9PM+LnsZll6+44TBXUoVJ4'
        b'fINGFybjCE9g7Ww8ibvZEMuG1tHa2KR4lasLGek0k/5kelzGVvKUkSAdJ5rj0VnRq5Uie2ZbNNSogujBoiQTC+WiQpz3l/uR8pWnHeAeqXWiljY67aDYI7IxeTmv04XM'
        b'wLDdPkueie2WEloFLIGKaZjvy0b7UryokDtANVVPyOSCWigYwbFiM5dhqxm2GwniEuoxQEPNb3px2wocI/cdgjO0GIuERTOgjqPsjlwot3dwxIsBFPLvqIWfZPlkuMmC'
        b'v4LJuoit0Rtd/bCDXDWAHSITeSsTrJ9/R1AtIpVYO7sxNtxfZRtue6PjyLfP3p4zT2FlM9x9Z5FlWdH242vmP77EdtJjlUWbxtxt8LOc5WT/xRSv2C2X9i7+fnuN17K3'
        b'fxcc5QOali1zWfnTkJUr9np1pnycFfTjTpld1v2DX/1y/603P0kdn2pz4fTVfzmWpAdf+OxxeXrcnpovlta0m1/dNaPZ+QS2fvDmR/9sLn9t4cXA4dGOq8uK8vpVpoJl'
        b'VOd7K7+Jdn057LPP7gQ7Hb3z7frY9O9yQu59EDr5Hx/tsrd3OGWzZElhv5rw5rOdzxpET2k69U74NfdzIVn/fvdy3LplzktS3954auvKJ96p8djt/cKiwU9ONY+80RAn'
        b'LXrl8XW1y196YXLjhrCqTzLvPbb/8zO+34dl3X316baXzWs+T7G5Z2W+/37z3b8FCW/ODXzFqsTmdmBG1gv2cVdUv55c+Kv5EykNq6XtVcsd2+84vDl26+YnYOs/zpT/'
        b'1vRK+4QXykPkLr8Oumvd+HZW86fj1829GfSm6tD6W0Zev8xI37zUf8ft6hl/GDxxZmZ4e0fZpGe3fPm3IRMd2q48e6ehv/mtEQsW/xD7S0JR/4bXBr15b8fs3Awr63Hb'
        b'f4n5qjhyQhu8mzv8A5+Qj4sj/ZxqhrnMDLn0oXz9zm8fP+BqcMjOP/bHAcMnYd2kQftHw0whLv6WsLn5TlW4+eu/3a+5Up8woHzLaut/Hlv26owslfxu4cWKNbNG3b7t'
        b'HdT49ZSXFuQNlz757FPNFUMO3bXe9u6HS4Ntv3op6W7ovfLEO4fGzg2eU7j8wx8nVY+XN34U/kPMuxEfu2wueXGO1422V//xZdM3Qe/vigzaEPZaRUjFnd+eLArcbO0c'
        b'nZFe9eTjTQbBo+cN+2327rtLhoV6vrui9I8nnn/c/fn3ag+fSi3+1mizfPFbJW+eCwxJLc2p3dc+aPeX2+xKg38fun/ZM59/2/xCfdBT71d9MDRomuFHBlu3z3puyg/t'
        b'+T/fiiz5ednt1qWfflv+e2b9N1n33yze+9K7QZ+M+vHHvUnvdHyQd/3JKT99cenmvU8WPX45O7jj7tMH+r3j8POKlk/eHlzxx5rj21XT/u1/67lvNpdZbIn3/eehF46E'
        b'bFvw+TbTe45/q7t1rmHIlNxrT15//kbY2UG3j/09aaPFp1/8fcTl+Cuv7Led+sEbs5fZL8zqUBV88c6Pz6muLfKu+9B3zydjjr/tMv4J85v9E0ucD1fDmxOUSZddPp20'
        b'YqYyvyM2ZGXt9dHw1mTlE4c/rr/8/uwJSqPskJ1vzFR+8kvVqNsBb5xLjPC5njL4dt2QCNWxj96R4KpJL/aPvPnrlx2Bjt//5PLiO7c2DfhiVqNB575xH71t9/uM3f2u'
        b'/THoJa8DTqdTnrl0Z8IGt6nv3Uy+e+/06sL4j49v9HjqfKO7ct8/Pnnt44h/9k/6zvJpoxdX/WjtkfeR7YjxmReelr775jspUd/m/GvfDyc3J7UM+ij54LdGyYOuf1a4'
        b'/sm5X27pvLjr2ZuvfLP446Ljnp+mzvYIDG14t/Yk/la7oOP+y9vPzBZD3yo98o35zo2nduEHZnd+PTSrdFvnqOVjm279cWLxqUqDTo8LZ5/7Q7rwyoLix+4o1zM/jK2Q'
        b'l6jPTMJoSTalcmKSvVjBPSnOm2KejrOJJTRQtdW1H9MKI7Ow1BFrN3R31Fht0o9r9eUWWOdPtkN+cc8wet3STRo/HFq4t8rehVjVpaNuxiaNwwjm92PQcJZ4Wa5xGNHX'
        b'T2/ImIqaBIWsLCazraF0joUepSQllMTr01lN8IzzcEciERbpIRIGQx0nR9wF53CHShu/hDtxh6MomONN6Zy0TenjyS3JU7BOhZW424WUwDktSEn3/FbmpYPFUmESnjMM'
        b'nYlVXGEv84Vr/g72Gs5gwwiJAxQEM0CTTTlwwz/AgSjrZMMoXyVOjYxnKnQmFEKVI5HwsNiVSNe0gLskY/Es7mZJBkO1DnzbRmyHc5LsIVO4caEa9sNBORY540Us85cK'
        b'Rko4iZckwTEKVrstuCNLexVbhzLfF3MoIgLCLDzNwxdPhsIODhRLYWKHToCGObiPtZwd5k7gTzv7UuS4A4tMJUtwB+xifWyVMUvl4IsVKSzIdFfQCrhuJFhBszR90hhW'
        b'cA8V7PHH+gkMQkUQDPC6RAqnVrOHFw4g+12rP7YEy6HB0tDeUDDBDgkpe4s69hNvBmCViuI7mriMWYXlBoIpVkjoqNvP+63OhIi3pHAmSmwmfVECuaT65nBN2g87PTi0'
        b'33mVuU54rDM24g4stGGPz8GdQbQPHV2UpvYO0IAVsFsm2AyUYm4WyYGNm2uuKrmLP7YrsZRu4ORpC8kKyF/PrC/TiUB+QYVNmBskclHhzNIhzLBEFIDTUdhK6kxb3ZFW'
        b'AY6MNRCs7aRQ6z2NTcI5eBWv+AdBKx3fOpycQ2C7DE7BASLe0ZERjoe9VC6+cMHM3tkeyok2a2EonY3XgJuwsMAcyuR+WIWFzgGpcN6HjE+VUhQGhckWOEE1c/qKJXOn'
        b'ULUODytpMW8I0Kkazat3SDrZX41DLYc9vgZk+lVLZwaYsJzjoWmVFm1xtYcabzGZPM4GzVTId1b5OiiJAAXV4kIyJsrhwFLe6jsdiTbWCvvwBpYaCKKc0jbvHMNSjR4z'
        b'Q2Ovg5PQqomUXg3tfM2pxksWajBGisTowuB8dpDRSEfESNwRp7VDXXDRojEShYo9vQAP+MvtSROkBqxMJiUzxQMSuOoDBXyYX4amAbRGgc6iYOL5mLsE9m8z4obC3MFQ'
        b'KXdROpD+KqXmuQN4LEGSYI8HWbpb+g12JL3jQjo0eJ47aSdLKJeuyYAb3LJ02shEjhfW2rukBlFB7rTIortLeBu345GZcsVkJZkgrTRtA9wvYluiH2upbCiDAxrLmcxJ'
        b'VMTBFWOo4Mk2ZnuQ0U8rKcVicSvmwwm4DvksWUssXO/PrPLQjPtcDAW5nwRPw9UoVp3lWIsFtHPSAoI2QqcLmfCuUmNogjK2CmXbmGDrBDgXQMfDZQGafOz4ynVDYk2G'
        b'XRr1mZPADXGM/RCyHdTz0pybjHt0Q9i3rIc6L9zBE3RXqkX77AFEsocmbOBWyCayrp3S2H4zh2jcCklJi3nrlECHPS9oBu5yFQXTORKyyzRmMwAmZygiExjavSkQKp+q'
        b'ZCy2kmLbklUX9y2Do8xzEo+RVi5QYcUaS6UpNDmRv8g63kLuG2Qlc8ADbnw52YFFRMWNwULNVYPFVPLfC8c4gO8hb7jCOJaJ8pSL21eLrjInDXxm42aS/BxsSc/EVtJT'
        b'1uJq3Af71GsMHoCjKoYPLy4YAoeZr+sW3mrX5kMbtrpisT2ZJ3hYzFwJh6Ejgid7EY6EkGTt/bIcJIKRJR6CKsl0LN3AlicF1E6mDrHB1NpS7DQCOugYsZRIYyAPylk3'
        b'z8AG3KdG5LaHKjVmOLTDNZZC8MYFqiDPiXSvIissXSLJ8jgQzsnciZp2mpXPMBY75XA+jq3wTAupI4M3O45t0AFQvFG9QJI1+YIxuW6KbWRgkCps501WjG0pdIcOoPj9'
        b'h80Xi84GybxLyvA87ZJ2kXS8CRZnkTeWQz+sksIRAxc+I9tm+jMUcjrVSR5NZISf9OStepBMoVNQOt+xyySLFZvYcIvBprHyDHMT0qQjRR+on+thy753zR6rwjJ6RoAX'
        b'TWzF0VDlxhpiDNRACa+JbyopWSPUO9P9vUE6FvIGciv+WTgCRboA7dBOMdrJk43Qmq5kqyUZZ8VQ6gE3gpFC+AY6KX0DydKtRkieNtOQLFUNWM6HfjteHqk1R0+EFmdu'
        b'jiZ7elv6JLa7wTm4yqCOe8VKJyLLDpJyODYZuxLpQy2uVAXDBTm71zmVTB3IC6RQvpekpPFy3djIkgmbu1inbaDRkbNOz1vI7fWHyCp7SBWkJLMuKoJOOi8JnMX92M46'
        b'ZR0cGEwv0oV9rwitzlABrZlsuCTGxvLHgqCQrDqkDSdLTXCvgkHhKvHQUF0o3IuwUwuHy7FwoTqEb48noAqKNFUgCa4XaA3apVBPemEPp9e+nuyiDzZPoeaxhYzuKgOT'
        b'jGg2SCJxP5yTk7sEMrk6xMFUA8eDQ1gb+EP5dDmWaKQi4+nYIkgW4YEsPjFPABmhZMX3E8mjl8Rk0iiHNxCBkPG/58HN5aq0RFIyU79AOnBIArawU4pFAa5s4Bs6wTU5'
        b'duIuMjDEwQJZmjvxHBd7W6HcSxWEF12JUEEW75CZMsFqnRRKHoOT/LDnPJwnQk6rk4sLXRJqxVQFHIdqOduq56dCk5zOBwlU4XGlOByqA5i0EEUW0iOqANgZ7ksazaSr'
        b'XgNxt8wDj+BOVi48DoXR8sGiM6uY4XBJvzTM59L2GdIhexmfTZCzAxnfK8hDbRRm+aKaF550Vy1Zx1wdsNmHdL6RTRBck/i48B1lFilPO9nSTwxxDuL2ihwRa3AfXue9'
        b'dXEt5mPpYDytR4XOwI3hEjSyNEaMgHaVi1+G0oR0fwcWE3lOIiFDscGLtdxkSgKjFqp9Le2jrOl6Z46d0umbrVkBg6F5AvfrVjt1r5B4kwl5kbXcDLwO9f4ugVS0Jstx'
        b'tjgzy5td8Jw7lPt7S8bj/jWiOx7GUr7nV2FNNMc4oQgnULiGgZw44gWl9f8MxK3hQ65zbAseh2uYxmz+7PDHmNrJej782SY4GDNkYY5TbCraMAQPiuNhy6EEJRQLhN9j'
        b'zDBAjMl9tqKtZLA4ULST2IlDjQaLoyRWahpyM9FCHCMZIw4mnxQGFIPYQmIroe9jJHNkVuJwcaDMguEbs7TpEZNoJQ6WDiWvduS74ZLBEhtWCjuzgSQHikPiJO0pXSvy'
        b'zED2PMc6NpXYSUwltuJgmQajhNOhK8jrOJLCUHGcobG4aVAPZzK8rXqjTX14s3edER0iTT2U2grp2WMvZ0S5wj/tdE+Jei8RyZoFz+8WabhxUJBSRl6YT7jSrBt0Sdoq'
        b'gUVfh3r6eAV6hTKwEhYdzbFLFmoBR2gJ0ygzHK+t7f8NSBHSRFO0TZRERyM9Rosj78YymUwNTS39T96NpVZWdIgKou1MDjkykPHaC+LwbYJJBu0Nbzwq51Z3yPfWN7xL'
        b'hJnLDYkodxV36QXNm6rfVaZ9Q45IY4zVn010PpuSz/IYM/bZnHy2UH9vqfNZDT9y0EQLLWIb018HWkSqAy1iV24UM04LLTIkZqgWWoTCkQgxI2IUfwJaZGS5Ycx4LbCI'
        b'eZxBzKiY0T1CilAQE11IkXil/V1LhqzDuKLnx65JSL/v+gCeiM7V/wBMZBqPQJ+glNyVeQaHeN2Vzpswj4yndG6qpxAXagCRtEw6srPoy0bx0aE+pvG4ygl/Ch9E/dC0'
        b'P48BosmOhXG6qzFAunA/pKxGaVsZsFCIV2BwmBeDABnTDX4jdP78kNhU/RhyNzXyxyPd7K5Fx9CU6P7A3tLVAmToF15popcG7aUHE7Xs3mI9p9VH5r1dcU+rYEvZfxU3'
        b'4wF6zgcZZw3U7rWVmDeN4/lZwiEG6eeAJ634tYNYGwO5znIK98XAyg4SwfJKwpBz52Uqqt6EWyopcbhP1O04hxU5H/hHmcZ9KnyzfdC0V8TpibLWrSuUItdv88ZjHTdA'
        b'YWMYh2jbgZexpBcSzl0afw8WXtXblk9/FHTb3DSw20T9iwgcNkYUlqmvHY/+fK2HxNFr1o8Gw3GcwnBQI+//GAxHvFL2/kjDR4XhiGE1oTgD1KP/v4nBoZlbD8Hg0Myn'
        b'h94x7ZExOPSnaG8YHL1N3D5AMXqczj3f/ycwMLrHbvEwg6gkGiFAQ7B6CSjSPtYTmuoDuBl6/azGyqD7Ese/IHuTQ++xPw8DqdCU5M/AVCTE/S9Cxf8/CBWaGdcDQAP9'
        b'9yg4EfqT9hFxInqcwP+LEvEnUSLovwfDcQyCwjKoDoZN68f2jFCAlVgeoKbTpUa3LE9uQ4SbWCjHkyZwLMHwVJ2BypOkEvD8t45RJzZ9Gvnpe2vjlv/tzq1Xb71x6/Vb'
        b'b936+613bl3ZfWjPyPyLO0YfbtihLO28c3Tn2PyG2ovF7vkjGXF43j/MF40eqDRgxq9h2LRUx2UWr+MxtxzYzi1s1dA5SA9KgOMIROAOqbswkVsoG7Fmhj62KpxZ6i2d'
        b'n4p1PFa+AU9lcduJF9bTUHk8BGdZ+v1wL1apnZ5hx1A95rrL2KBx/vxPXF+1gfTjHiYKefOAesOeZJL/NyLmBz6SfPX58L7lq0cNm49nYfNplWKXpNdD0Pw8UiYeNP9A'
        b'TtqI+VG97Jg9RMkb9u3kG22kM7/kmjk2h8p4Rt2kPDmV8+LkainPiEl5xkTKM2JSnjGT8oy2GutIeTk9SXl9x77rKrf/XwS+6wOIqUUndTT4BrLZ0LDc/42F/99YeMX/'
        b'xsL/byz8w2PhnXoVsBLJ2q/LhvanQuP7WDL+b4bG/48FdEt7lCBt1BanXcH0FFwbzb1hkgX1AeJYYhQuCJodoIX7WIT6YHGwBgrMxw/LGRnZEorDZcw88aESSk1W4Em4'
        b'gmeghsGNbYge3z1W2xx3JntLiNR6Hs5xkos6bMNTFK4M9sB1dYQ4lkF7Bj1SSICD2K49BKdoYHhc3hMgmISenh0xwWvZUMl4vyEXLgV2BaRikY8Tjw/BokCspoBhjJZW'
        b'iBhvPBfy4RLjnJ+XsMi/mxBNY2udsCKQ+4uFYFO63AjLrRZlzGES60TqURTIEwtfuMR58RIaHuwXGAANYdiADT5w3ifQxdk3kCTkKoEW+QQoDQkVhsNBi0T5lAwa77J5'
        b'6xBK1ZFpKzCmjpWKDHr8MgCKSRvrJw1nIY9GvKZMSKNhrizgXCZEQqkR1KSQFqNnN1hIuyCU3k5vVfdXGH8kENuxSlPzFXFGcBJr5jEfcyM85CVPs8ALUtKUUmtx1lq4'
        b'yOIw4MLaQdiKHVmwG06raLzKTdFxJBxmnvrZUw0EY+EnT9mcSDP0ny4kBDZskapeJldWZn4avuuiObhZeb2Yee9xX8Uqv1ORFZOc5qTaVI4e+VF9+uCzF/4+1LnfmM1u'
        b'vuvmP2N20GvMfNWPOV/94Vo7wc/Y+43XZI1pT92369g/xrS6dWjuq/Vxn/6Qs32d7ZI839zXfyqwMTqz4uMh48bZhARZjir68ul9k1ZvT3mycFrnxIyCt4+96PZLyzNp'
        b'Xx16d++wbPP1x+esPR9x/BvLF2r2q768deODT2Z8NeqrvTX+N91c/9g05ffiuufkHTvG5GRHZ7zy217ZxycOOoT8GuFfEPL3uS98Jt77TLr9ol/KewFKK66jnOsHTf4u'
        b'zoZQqssYnQhnkJNND9iaoxM6aiTI48IY7V2RXzpjiCmLWU7xzhYMYHGjgcA9WzMXWmhjOmWCHMsSWUznNlPmYDHOEJq6gZ3RwAaq2xyFBuZLFADN0KEdLgaCfJgLJRvG'
        b'm9jBPFFSF6qY4hSBFwSqOI2CfO4dcAEKfLXTRBTkSjjBCLtb8CJzeVoK+Zj3gG8uUbGEEcw514Xcx6AF4TJFHiR1CIRc6oGCxURNI+uJNAAPQjNzBvDHkhxKeYzt1tTD'
        b'hlIeKxK5382uINjnP8FPgpU0YOqCgB2j8CzTKpfi1TRqsB6DZzWcIjvcsII7yTTA+amOfoHcn4sUv994vA4dUqwjU+Uqq/jY+FE6Oqn/SrflDiyME4qsKc6gJo7TMUjE'
        b'Xd3iODdjwYPKlvy/GEPp9zBFMoVFUkqNGUWvsaEhQ2WzVVP8mjJqYBplaSGh1zeN6K429RwCafIoIZBd6qZB74ewRr0z5PYQ6ej1SDrndYWuzvmwKv0PBDuuemiwY0+q'
        b'2p+OdKSA3w9GOo4OYhickBeFh/y7+Ct6CHOEw0t7i3TEm1CVQU8yrLEej2hBDNygWVjjOUsKp7BMLozCRinuXBzIwqSiBkHDtjnqcEeOhrDPge0LC23wpDvZM3gkI41i'
        b'HD+QLf12c2mcoowoupGJU+XZHHsUiuBmNo9TDNjMIhXhph0RBlig4nUoGM2iFB2hzFVwlWEnhzip3wyFqunQRh0TyB5L9r09bhmc+ebkOhamaBZLAxUxD8phF8+ncAVc'
        b'Xb/NXydKkdqGWIRThApOh0IbNnVFKU6FPCZrhNBoMB6miJdsWaQiNuJluMGqGkHaLZ9FFfriFRpY6GCTmkE9lTwT03UiB2nYIO7ADho6OAQaWWP0V+wShg4LlwlukRaV'
        b'y7fwoLmatFHC/LCxpBCRktL+3kIiHZ9rF/gKu1fGke8i173l95fjzeL+dLzZFaOueLMFtMuhbrSaJcWJLKCpvoFY4oR71O5HWAmtFBCF+QFWrldCu3QCkVz8oZLRLDUK'
        b'nlhkGaaEGlbTDTPNhIEbV4nCwsjEap85vPqVOXaCk1uFKCgih04bvElgTZmKO1IU81hYZ/eQwTH+PMrvEB6ASh4YOCSdhgbOgNPYwpI0HGkomDn9JqMccz+tDCc1ZR1n'
        b'nI0X13qo/X2pt+9lqP6PIjL/XMtKjbtaltWgGE6oQ/nI3llIw/mm4d5NbEi7p2GHHM5ilTaWbxBc4/Gu5XgEL6URWVkd0cfC+dYrmIiIV+TQSosRj82LhEUb4zlbW2Ea'
        b'1upE851d5SdZDhVYnUEFkSSoNdgEhdiqF88HN+FEgnLfDJnqECnBAOXijLBn0mwXWJ0/uzrO+xWbNXteKgq8V7dhp1nRE7kbZKv/JtkxN3J03UmrU/mveT5nNOzsaOMn'
        b'ZebWmd8NsHr7sX+PlS0oDLYIOjj9p3snIuJes7KRFd57dp9r6zmHL8I/3jo886Mtf1yY91zFFsW3bntP/v1sZW3KDaOIwbVDI+8ljFj6meLbtIZFdT93Sj7M+ig6KmbT'
        b'1I6MvKbwECPnvLK/yZZNm7q/dMLO1xwWpZbdcXLanm9vOX6+dcC5xrh1sddtlr298dRjLhMsL4tvud1IEH4Z57T5613jnCa0Xe6o/Pp++qGnYvd3zv5twdS7rhnB+ZMX'
        b'jPp5wL8/vpLw+Q7wNq21f3zxp09PsjfcNjaxf+KcD7cNPdZm8V7yuWHDYeX5qd9XRRZk2348eN/0gNoay0t2nV88+/2VF19Lyi1XREdfa6icmeQSNu/qnTWfJm9LS3Tc'
        b'fPytuD12m97wfO345NAXVBVJ8cHVM5zmBf1x/OCSyMwJrfLbac8p2t98wXfZ0ut+n+96vOxVx++efffz21vc8iae3V5y5ZuR90bfGR7nnWB0Lb7mnme66/HookX/fKo5'
        b'x9vO4bqYPPte7vmXz32Xe+iq5M2tz76c+lH/pSf9Rii+PVo+fXV14ZWNTZafup2fa5k2e4PRrk9fm7l15O8fLM66VPdExlP7Z1j88urhiJMrN8gOfW+77v3ahrkR6+4n'
        b'vH4755Wy2V/4zJp0ztS13HhV+LLq71/4PmGPe9yqHw4MX3z3k+Z+zSZu47NPhX59w/7aD+6rT8yzvBZT0H/uifBX/g9v3wEX1ZX9/+bNDG1o0kQRRLEwVBVFwYadjohY'
        b'EKQ3pQ9gLyhFpChFBBEQBBREUEClqcm5aW5MVtNjqsZEk5iya3rR/y2PYVDjJtn9/+InwH3vvtvLad9zVgQes3lgEBj6fOj9Td4Xdp6wqM2tydqx927Udud5Lz58+Fb9'
        b'/YLp6VnfBd+ctOdX3fsDbvfGf75/Sp3Bm4UjP/zNa57j/HdFPxjUlUT/lq7/+4+fPXTS2lnj++y0WdLLF3N86ws+UmgFJF3yeG3qgeqp//zI98WdBooE2y2NkQUVd9/x'
        b'e/Dx3cx/u79oYn/9bN0cK3On+xXFXx3Fef498svNlelXr0aYh379RWWVf7/6Dx1GCxb2P3zwSlL7rK/Vp1jtW9/UZXXvh7mJDePdR378u8avmpk6mTUfFcwINrt5KLhg'
        b'nprmK9sWdSg23W7OXzPuYtiKsET3ulaNGz9mJY069VbMxIlvbPnm+/KeH6M8P86pvi766b0zdfX1swf2z/rR9bzed0e2fP1pw+qrmx7cm/3NVetfZi7+Xdw328wk/NYv'
        b'CzfHL/W6+33PiHDXxplG4dvWHEifwe3I+9w09iH/WdiPr/rPcfmoCB2v2dZ9ufjW7H1lB8e/OPujZx94L3818NaeuPcfjI3v/bKtvlaeTAlwtB/OohZVCtxcQ8DHUQLc'
        b'B1VQFmIJaoSzKuA4xViCjTNBZYxv6ZZC55APY02HQXDcSkxm0wzZ0Jc6hI4j0Lh4aJoijoWmpUyD04J58WqinhnEtCWiM4OwtssTmHXJETfUgFmhXtthuLZx3sxOvAp6'
        b'4ZBCNSyXziioJKi2DCiisLZZC1CWgkHaQsfJPfG1RAAwg6i22ZCtBl2QJ6AVzlhAHdRCl9cwYFtjAoOOXJRMWbjGdhh8LUkYKpQXj/qG4Gv4PN5P8GtqDBCEdo9GA6rw'
        b'NdQ3hsDXFu+ilsWoHp2CZhUAG0GvoZPoIEWwKeKYTXUFakIXGIIN9UI7QbFBi+VW9rIPypaqYNjs07T41ZGYpSGMnPqmLVHzh2HYBACbkS37uAOOcWvkXqoANpSFehg/'
        b'dGk25CohbNZquGfdAojNF+XT8jMghxcgbKhI6gyXBQwb6pCwdZBv7TAEYSPwtc0olyDYpiDmmNtrJtSoQNDgMBTq8uswRXSU8njEhVGlYjbqUkLQoNuEuRMvn6MPB9Hp'
        b'4TA0AYOGecccZvR9EmrwK2qhZG04aKBUIWMvq8ImQwlclvnaa8tx5+G4iCC1+qhBuVyBibkhfAoFp6Dyqbw4ajnmsskSHrnGGKr0vXyfAG9DJeg4XRtS1LZ8EN5GsG2x'
        b'cFpNPB9y3VkE9o6RjjJPe+9UQo+jfDnmrysZvs1CIsH7tBedpIOktRQGBoFsBMUWhOoIkA0urKevkxdArRLJRnFsLYYEyua9ga7dJLzCLlHEA15DlxnqoTjMi46vNlRq'
        b'YvqpFrUqkWwz9GmhCSZQN8TJo2x0kiHZvFkcyYgdKwUYm+UWgm6BhnhUQj+cDIe5IWdKkvmomoLY3CGLmaXXJWKGgYHY5PwiWwHENkJAZ0hXxSkhbOhINMGwQaMrW6s9'
        b'DsYqGDaUvz2ej4fD7rRYQ0znHVKC2AiEbb4fAbGZiugYTIyFBi87mSqEDfVDFWvRmTVOqFNT9giEzQ2y6afBaGCzAGGDQieO+n6ajc9BuoK64eQ6BmLzRucpjg2OwwFH'
        b'2hXt8CgGYXNQgzYFQ7CpTWSHTQfsixKgJgRmgk5tmCHWhGZ9hg1qhibIQl3BqFIJYfPE40OPk3y0l8Qgpig2OACNFMlmBoX+9FMbyE0RUGxBEYLneGc4SGUXCY4woL9h'
        b'iLC1Rf1sdQXrDbkvw6s8BIoIhu0AEnB6ZwzQedZWR5F9OkPTeKD9dBfax6EOxXD4mgjtVyLYQhMpugOfKK0oZxsqUKDiJyDYoCSKjooh7LPHbCUuShXAhi5tps3f5Yo6'
        b'5oYKALb1IseVUMeEPWczdlqvUQzDrrWps1O7dzYq1fMXsGsUuYZ3VZ2A/sYHQamAXZvvRNFrUGsGAjK2D85D6RB4DdWOJ+C11B3s0G5Bra6oGjMvBEKD9wiRhZ7DDTZF'
        b'ZyS2C+Qs7CtkyYbIaSibi8lpcrgQHkOODi7JDBJwGxGiqVCGLrMjt3PtQtlggXgtotNwnNOCUh7a4Ow41qmiADhloS+j8BsJ4VbHY+6KeVpLx0xn1SCsSGqlxgBzxQns'
        b'6i+DBjioYPegJr6AT+0UDmXz2RIoQeegnQEJzyXDftiDqYThsDnInsbaWIr2OCiBc94i1GozCJzLQz0CQhb2jMB31u5B8NwqkX0wXoZ08LLitytUUXM70WklcA6V6NLj'
        b'JRQOeVPkXAw6RY+X41DpyVpXMD96COtGcG7rUAOBupkxMGO0j0QV5ua4haLc1sB5BnJrQTW4cwXDEG7oiGwYyA2OQTO9vXZAKTSv2jk0ZMQ96x5xOr5TTtGFrQnH3dEl'
        b'uvoxqaOJ9ss9hGt+FGRJlkHlIraaTvGLWBY6nOpLoAMd5RdEbKY9WoBqpg3B2QiWDR8PjQFiH6ddbH9OhONDslio9eRkRBjrAWfpUMU76REpKKYM9tsxKSgqWECb7z4T'
        b'L582qFPgav3wqjpgK+c5/S3i7dAhZ7fzRbQbnbXFyxCTYUQSgSmqIlTFb/PB/aPw62ZMgFUao5MK4oU0nxCNpHsiboSxeIe2STpVjew1xTTJU3F+PlIDTDlQmN/6MFZz'
        b'mQ26uGSZCkZuECG3eQVdycFw3pEBZx1FsycKuNnDqIqF+fCUUmh2AORRdDYULZ9B190c1KYp4ILJsepi4yjW4DFJSkS02yHHyvbxpmFa6+Qgfq8ZHaGt85uBmpbuUMEg'
        b'DgIQdQRJ8SR3PVXwXpO7gN8j2D13J9pGDRcXitybu41i9+Ck+eB1cxgVjVFF7mmgGo73hzO+bOu0L3KmuL0IOEKhe1CLqQlmlrTB0UQxBNpDZei8ErhHwIjpTPWSjzBF'
        b'hZoHoXvocjiTzRduQGUWvAp2T0DuwQVDdrC0xU1iuD1MBjdR7B40hCcwRUPnLpHzZgbdI7C9owzkvxmfobmQtVDh/STYHuRADW1TBDohdkcHZUOwvYxYtpkPTYMWFdCe'
        b'J74pCGgPZU+iYzUd9kDnEGQP9iQSzB4cQ/vYhYH6ZqzGE9mlCtqDekyXEwpu8TpMvRYMAfYyUM4gZo+3osXPGgHZDLGH8qWQC3sFxF7XBoaTzJ0bNwTYo3A9v0AC2MOD'
        b'vZsOmY+rhxKxBxekNBLLenQhnUpZavhQ41UMsrdFNGdWBJv93PClQ6A8dIyc8iT0eM4Gue7/PQyPoq2o8oB/GgaP/Rs1iMTTF/8RBk9DicEzwP+MaPAXfZwm+Lv/gL0T'
        b'awg4OQnFxZlqPIrCM6C4OyOaQ5eg+SSmIhORhF/6X6HvTIej70we1RD8b6F3+9QFyMdTlRa7uV+GAfD+oFG4doIySOsaRN+JyY8nAu/SaknGP4u5M/y/hNvV4bpvEkQi'
        b'cfb9d+F2GmJ9NQFeN2kQXmeAU6Zu1P/yIkwg7RsmnoaDs4iEWsRZw2VpImoabiSrK/xW7HkMVxckKVcv1yw3jOHJz3Jd4W8j4bcW+x0vjhFHiYv4KBul4ogEwtHO08nT'
        b'zdOnIbK1CT6P4tmk0WpRalHq2RwJDV7EB6njtBZNy2haA6e1aVqHpjVxWpem9WhaC6f1aXoETctw2oCmDWlaG6eNaNqYpnVw2oSmR9K0Lk6b0vQomtbD6dE0bUbT+jg9'
        b'hqbNaXoETlvQ9FiaNsBpS5oeR9OGOD2epq1o2ihPGiMSUHrG9G8SalwjyIQaRYqpUk0jT4bHRg+PzQg6NtZRcpxjZBRPZei2N7QXLfBZuVjQjt08zz9iEEksklRzMECf'
        b'0p4mPZlEg1CwPDOm2bHfTjR2Avlr+rDCBpVwCgfLBSqmfoLlGgUNCPZx+G16dBoN7ZCcSWLbpg831VMN82BnGR0eGWeZFp2SFq2ITlIpQsWWkJifDivhj4x1hqsChyV8'
        b'k4mNlkeMJQ3qqrDcFJ0WbanIiEiMp1ZH8UkqWAxqBoVfh+P/0+PSoodXnhidHpccRc3TcZuTEzKjqdIygxw+CVuIOdWwOBaWS+KpZZL1ArlgVJsw3F6LmDUJFn9sIhyF'
        b'eRgccTtL64XywWzhlopoYnmWHv20SSJzaL1ITgAc4SrWfYJdXXJafGx8UngCQRII0GU8BAQl8UhHFYrwWIohiWbxOnAu1nvLqOgUfNoqLJNZw6mJnrXwbiFZYYnJiuGW'
        b'WpHJiYnEeJiuvUfMAX3l/A3x5sSEG2qR4YnpM6ZHioWjRiocO1SxRJxwCogw9bzBKFoyenyI8AHCx+gKGmjxPrW93A7JVrXtYqqBllANtHinRNBAx8glN38R/QmM2LDN'
        b'88eGYH9kG4h7xMwC1/h4C3ZtNGAKLXdorvCsUNtPvBWfbDBqHc2W0B/t06dgl+hwuhIISmQ43ulhuElhzD6PFaYsRHW5/UEYm/CoqHhmzSnUO2y5kYWZmhEtbFlFBt5L'
        b'yiPjyZiNYTavLDoN2XHhGenJieHp8ZF0gSZGp8WqxJ75A/RHGt6JKclJUWSE2T5+eiwZ5b2mIyyy4RYC5r4KQunOSzLvuv6jrbw1fcJ++RX5+QL5W51ZCi5+h0bTNXNq'
        b'RZ9hz1GnNZV++C4tQReIbC8deiAX0/1yOA8FclQBncA+gqYQ1E2pzJXMwe5B6I7AtG4FnMJN2MntXI6yqQrWzk7M3BNPSlnvZrOVyyC8BlTIpqKaJdCFT/nZ3GxUEZPw'
        b'08OHDyFFQgLKWE6ZhCzPLLXjMqjv9gOYf8jyxzQ/cb2Myp2m8JzURbR8KeqW8xnEbQvqh6NRCrRfF+VvcnBA2euJNgCzh5o21iJuGipXs0UDa6k2FZqtoUyGCkaRN7yP'
        b'aCZmGhpxKZb43frQLUNl5NtrkR8iD6jixrtKx6MGBVXVTliNLsjoG8w89YnQQXQYWtYZ4yKINSBxuwc9qqWkedhgzhcz4B5eAWsdiEpiFarUGBNkKuhjV6J61IVfklcj'
        b'N3AaM/gkzFJdkIupijfA247E7LBHJU5TfF1m8Jz2Dn4jOrCUjssyuAzVyteYrb8wQ43T3sknBGTSj9UkqEP5Wn/DDBGnvYtPtHbJIHMNZ6ESz3IBs/VzJ9n8ib0mnCIG'
        b'WoKuZbGe+siJqJVaZi7fivYxFtDfHp2nDKAhFIvhgJRIe3szSCxAOGcB3cQIBTOX2YOGKIOBVFC+t5eXPZ86F2rGoIuw3xh1ok4vI9jvJdNCnVDguSKAi47Rnwm9LnTd'
        b'VGyWsrWwaoIh0h/NZazBDzW3oFJVK5ehyDhFjp6B1ijfHRUGEENHr0B0hq5fsnap/YueL2bfDSZqoRxokkpR75KJ0CLnlmwyQjVjLfB4M6MydDoRdemlpBEHTD2i2JGT'
        b'IlENW98VmVAt0yAIf8xKzIAKm4wR9Bvp+ljUpZ1Kv2gTQQv0TJgBe+mrHaPhsiKFCmPF2sT/cEsYFJoxI8kL6yMUqahTm3y2WwT5cGgCHIZSvJCoHHw3HsJLCnSelgsD'
        b'ItQpMoG9a2ixOrGoUbXKau8JqNWUqvBRMxyboJx0a1Nh0uOgJ8OF1NoL+eNUosBgnhTt87H39At0H/xmhjCmsBt1caguQQYnx6FOdjQ0prqphpChHy63X0U+0EM1KJ9D'
        b'pVwU6tHgIMcyfr7UlFcU4/391cgViWUvJ73uZpR7x+TFYvMfa52bymfbX3gtzWOdwbGFIWdbsxc7H0taKvdutEntPHPtqppXXF/Lb5zdvcNhWWu+5drWnF04h3/ZwcUp'
        b'Y1Fvwgt3frszX3Fp1Hs3rgf6GBq88qVn7qzPFq9WbF3+gV6ir8vsV2fcHSjXz5nw2gOHCveDhWmTXxwIXqbfq78lIyDyxkg7208nn0X+bxd9uObcVVsXXe/nb87T23wo'
        b'75sW+Jci32nmsvfuflo2cvGIJRNzJgc01U8uiXrm8I0H+ye4WGwvfe7ejhUBLy3NffXdBb93F+XOG+v17bpFo0522hW0atRHervmrip8L6HhpUlLKm99mF7i8+6N7h+O'
        b'bVyarZnbpvavtoxE8/6feuze1O8p2tR+tw1duv/Wmy5NR+XN9oXdXRH+R7suofnd99/aFN4YYnS4LW1LY/DZnwPX52bIi5vEP74Z0J7+yoRPPToqH5o3RLSvufua0bL5'
        b'eS9vh/fdB7S/3njtwkmbPjvbW1v3/Bx1OOuOxpyAF8puPfA3+3DEogjNOR/7fes6Pm6Tpk3de+6uUx6qvX9t6ts+qV7Zn73HZTzfWhuYfOCNN38KuRmy97dvr5T8u8nx'
        b'6339tyxmNff7eja4W137uuBa2/bm4oRQcWfGt2/0SeaMtfffu606t0kUu87jysfq3t89n/tOdlnZhzPNkn/77N0F8s+XJT73ysy39+nl6XWv02+fOOvZh99e5fWKXtq1'
        b'5ciJzXHfvfHv6bLaSd+2Nadfm/38om0dD26tlVrcmCz1u39u7bojTXZHsh/krc3556emP7yae2DzBwOyr+Ka60d26x2JPqBIf+aHjasyMq6Na572U8O7FvPC/nU+JqW2'
        b'Qmt6xYI9gZZ7r9cm7A775xan50+ar1j0g56mW3xW55vTokJ13nW6/dXv/Bt3DPINZsgXUHEVKoMSfCrHbnTw4fEGOyny2jSNia7PoPZVZugQFEAHOVbwYYP285wMBvBe'
        b'c4M6JsA7B2fROdsRqMfDWx1/vk80F45ADxMEn10Be5XabFQEl6hGe3sylXk6ohOoHAochUgpLRpqYfx4PzhNX0bCACol4Ysc/ex5DpXEqe3kbTKgP52w+/huLUVd+FOi'
        b'A/V2gHw/qtCFfY7udjb4dy004FNZnQvFd/NpfKB2MIlg7WQ4qFTSh6DaQRe2uDe0K/PQiXgi/EJF9mpc3Ea19bwVbuJeKsgyxsdDVdJCLz97DzsivZVBN48GYD+qY/64'
        b'OtE5uPhYmGN0cP16LQ9a+6wxox4PuRxjoIHPkDym6joGe3YNCv+gZDOnToR/qA0O0catm4xylZI/24lU9qcDZ5hypwUqttp6wGl8k0tiRZhuOYVyoR2qqN9dVIjHcj8R'
        b'WSuFg5fwqUkUFaPRUUkq6oaTVOWE8hdJqEae6OCkAdA+WUblsA4jtuKx9vTxsieSPF/mDWzHWm4COiSd7TKS5hkzBRUqUtahIg8yJ166vvao24vnLJZKoMkEspgmpRef'
        b'+21Eg31Ak7x3DcE5dJbwqBdKoZI5GswhQs8CdCrG0dfezmeoOs5yqgQ1mXsLvkwLoGEpnFUKMwVB5qUtTMxaCI1wEgr8HDwJ8mAfyvERcbpx4ll6EsFVcRi0sQucyG9H'
        b'oktEUz9DrI4HLpst3CrcRCrkL/RCBercCjitpslrZxrRDQOnRTsUVOQu3ihC1SbbIXs6U4GiPZNVPW4aozYzkRub3aP+0K7qOhKdmwa1mEhqY2uzIcWGKo+oQ0585TVJ'
        b'0RER6sOX4RFapye0R8scvKiTuVZRgj/UxYSxETsKvfGKJ7rUnGGIDjtZ0ZYt35GigB7UrqIaHAsFgsITHUGnlQpFqHEhOkUtjr4cD/1yoj4iWkgxqhahStyi4uA1rE/t'
        b'E1E36dMBW9KsLhG6jOmwE3NRNzsZKlPhIlMxE037xR0wAPmDRiSV6fqD1jBSbiPaLUV9vGgU5DAd5zHUBP0KdHSJUnuLSq3YGrpgDAfJ1NprByl1uAbQLsYjcGwas7XJ'
        b'x0s/n+IIqIIJ9kEZ8QHL49r3oxKqHJSgfVIZ3gb9j/vNZl6zT4XRdmoumI9pUsFr6zkRXEbteBo74TJdaEmoEp1j7wlxJQqXq3G6UeIlY9CFdEfSj+44TBMXbMpE3Tqp'
        b'Q6QagW87omJ3H9RuZo8/CViioQtVgnoaHUZ7zRS2Wphqlosw/dvGqe/gp6NSqGZWAefhspHCNo0ue/tYTj2anwZ90MzWQi/K24w77kH0PX40kJ+UM0ateFcHj4A96ADt'
        b'k7EZ7JWR4kkR6LwNPmha+bmjhfojZuBKhSIcoQ3Tkeqcrq/YbYk2XYc+3skK1Cj1JGZBInRBpA+7N9DDQ0NiKBN0MEW4qhw7tEc4daFHn2phUHfKMEXM3EQ22ft2od0K'
        b'weAFndCBk2gA1dAVZIvP8iYFPnlbmB9Q4gQ0G5roqQbnvPxxO3FDPPAmpaeEozsqEsNhQ84KNUtnLkPZdJIm6RkrfOWpVlDFzKG8RJy+udgfKlAZq/8oaoROxaA35T2Y'
        b'u+vdNYK+8jLEhCc7YMSQI9oKzVs1UAeLolWCLqMqW097L3sb3/VoNz5h9GLF4egsHEu3JqU2EgvgYQ0kuJZ8YjQjXy8dDzVQjf8vSbehpKoYX6PKdYJyNVSXip8zJl1n'
        b'Q7ua7yYjuga0/NB5FTfY+Kg7hPaitm3MO6oxlMvIy7moZXBNj0B9YjiNuca99PutUKJtS+8ie7X5zpwG6sf3Dao1p98HoL2TVNVIgg6JgzKDZGiX6/z34vD/keLnSc4F'
        b'uvGP/6DW2cVFa4n0eYIAURONEWkTJAhPheoEJUJVJWpUZaLGa9C/dHEuXZGFaJLIWmTA69NnGvgZEcDr4zej8RMTkQl+Y4B/64qIasgCl6ZGhfLDnojIP136JcGfsJKI'
        b'cmersapE6lE/B1KmVukjaov+4fgS7f9qJsSsuKHSlaPpQcyyHchoPl1zs5vrnaSqu3lyP/5HPg5O4y+Yj4Ph1SgdHEwdFIxTybKdZXSsg6UNEZU5TJnhNOjL5Un+Dv5j'
        b'A+NYAwOf3sAzgw38xYy0RJCzWsZHDavzT47GDY3QSCZ8f0qNXcoax1GYMsXmxljSDwnY/i/Vyzp5QydUKVgOjX9a5eeVlU9aYJmRFJ+aEf0ERP5faUEMa4F26KDI8ekN'
        b'6FU2wIb0XpGOu0/FlkqJ5d9pRDab65vcU+d6QFm3Q0Ay8R6UFJNMfRpYhkckZ6QPc0b0dwYhbe7T6788fK2pOMf5O511e3ploKxs9FBlCz0W/Z31lbbw6XU9r6zLltSV'
        b'FD7k3GnQHQbzB/B3NlVa9NMrf0lZufXKJ7g+GmzA39nOWtSdQCgB9z+lAS8Pn1bqE4Bt6793hNA605OfUuOryhpHCd4j/kZ9MYNHR0R4AtGlhCanRCc9pdLrykpnkUpJ'
        b'bibiT1DVDT7qbORvjYGusk2RCcmK6Kc06o3hjSLZ/3aj/huvl3GPer0UcY8qMsS+8c8tmcYriCC/crRNm4j4r9SI+dhbndPIF50fXyMXMdTAYVQBl4Z4IcySkJAUhBey'
        b'hTN/4LZSb9BKhtDZ/5Gc2sXFbjV65NpPiE4KDf3zTitJhW8TioMY2P1HimM3d2qY68onVv4/mYiY/zwREt+V8S+ZT5QoyONX47TWl3uFa9N5kFiL5DZXh9bZ4+Ncx/21'
        b'cd7wGHkVkZyc8FcGmtR44y8M9EntpxF3rHblSJPaiE6XsEdMpzvk53PQLxTT64rydJQ6XX6fFM+BGM8BT+dATOeA3yl+0mYg+jJt/L/TsDkY60t1AZPkaP+QHsFoiWgC'
        b'akc9VJmmMBaUaSbdU43X7hTwtnWwG4oUumma5IMGVLVY5AAtW6nGZUG68MGqvuBn1rpzGUTs6CsnRtCo0JYB9Il3i0Iv/IcvakaNxOnFiuUr7Ffx3Ho3dcxrlaI86uga'
        b'5UE31HmRcMcFUDwkRpNyNpEr4YIUTqEq1EYVK65Qo6NUksSGi8KWQU8GYaKNjVCjqpkvqnRD1SSaRTn0Mu1ZNpzAXGCBIK+S2FugXBGcnjuOjswWOIIaB2OWukKvCGWh'
        b'3jhaMtq9GJ8PrahMYGUJX48Z2WjYj+pX0mFKSFxJmUV7DwmnqR6DDvNQLIGTLO5iO2r0Zz4TJJJpqFwEdbvgMn21DrPXRB4qt1fjNF1WoHYemuam0hI1oTxQGZ8KnYBC'
        b'EbQYQBWblDNQNg4VeGva+1LeUy2EN4Z6X4rIllqhg16o2IO47PPGeXztBj0O2M5dZiNFReio+rDVKBtcjYuHVuPwtShSeiYbXIdabB2uxkvr6WuRdFLzsbXo4EsX3NGF'
        b'RGO3Zpe2W1gCeMWxKJXTF2mhPlSsEo2jeA2cZ0quemgK2YGahkIwQRHko9305bidkK0yPcEudIJ67diAnSJiegPoU0okt6MSKGMq3o4NcEzh7YiHEdVidtYc8iGXqfD6'
        b'gpMYtgD6oYrgCwxj6EJy9IBquEjihw3FBoJq1MneootQvtOZeG1RhnSCBryP6qjGLS52igoSZgp0USQM6oNLVDlOgey+RKYfQK3qj3LjuHFwxF8uzRAinx2EHJUCdmix'
        b'77NGCgpiqJwHOXBOJcAS9KHjIhpPFR2BYnREFRGDLkMLDewEXdvoSIVILQaxNqjaVJNibVpRJVXpeviG2+JqHfAecZDbe/rgLO3o5HjIkbqgI6iCfj8X9kHTIMTFx4ch'
        b'XKa4sfm7tJPA3qgFtQidQEWcmgY/kh9D7fFW20GV0hQb+marGIozS2y7JLq+oRc6zailvjeRPO9EnV7kVMFbkeyESaulG0P8qfbRfaIaGcY/tj+HPhnnC1nq6GCUPYNV'
        b'twE+slythlSwYXAWuum0jVuLmlQOF801QqScAg/a+oV4qvYnoXNPPsHw8eUvocVAvxZqhDMoT+UUwkcQXB7Njooj0LkFLq5XBgiC45AfQhvnmmmDivBUFrBX1Kb/NJyh'
        b'sz4fLkMzfkNPA7wELrET4VIMLdR5ZDAqw2etMtgdtDij/WyF79dbhBexiEsJF83iUDEcxYcsC/+E9uBTpgd12dJQRJJwchx2QzN965wAe/ECc7e3w5ODdkOpBlTw2zNR'
        b'IbWL0ENdEx8LYyNfRA3h8eAX0LUwBRqhW4lKWWdAUSkhkE9vgwnQtAav84t/dI6RU6xzppxnKux96BSqhQLUmSnhTPE5iU5yeHGdR2W0905Qg08MdFaNW7OTQ4dIkOwy'
        b'3AaqyqlCZetRmRrnOJ2z4+zgmOBrIW+pjDPiPh4p0g+zez94FnM2kGRGzFKW+3NcmPa05SPYw+cV5AR7KU3dLUx7vMFW9vDX6dqcKXd3jmx5mN07433ZQ5ulmpw+lxKt'
        b'FRbmHevnPjyeM6VvyP9kZLZzIbo7RNtFKdpR3Cp8tKbyUYOEOqNhhODNosxHyPNfNOfERidFb05JmxetKTgMkDAzCHzzHZMrHpGw4xOQeku187CH/fiPw0MOGeSAh0+M'
        b'uqDMwAtKnfQjnFELtGyBFmPpkkwuMwgq/Y1R19oFGfPpMYmy8RQUIKIKKrPHR0uhjym+7zz9l9uvcn/CFEIXryUibhhatcNWxGUQofx070BbfKKWetrL7ZkaTtgeYwIl'
        b'0IYGrOONvJ/hFZ/gPikMPoteOTv59eVG8y6dN5z96mzfoBNN/+z2CbBeXts67TN1y3HXW/bcbD2dtPxQs1f216f1o7/l//3MG1dKTCv1Lx8Xiy/vzm+5zE1N+fqsWZDr'
        b'cw8ufbP9Tuo3Zw3etbK9+r1lZ+YuW43Tpi8cK7x2c2mdzntH5S/4RFu4/hT1krcmLK+Y3mP8TKreKLNad69pSX4LODCqOKOu/na59oOEaK/ZV/cnhP7qc8X0ZOORva9q'
        b'u4SUoPf/+TC+9szZdedlM/u2X35XWuN7a7G9o9bdPve1WQ1fTwhaOapqxMQVipB31A+ZJzas+PrZJC+X10ZkRmlX9Ixc/YL+qEWhMZ+0rnoxN+u3lz7K0k9P4ioDkeuo'
        b'm7LqO5+4NqhFX75lcUsOHb0XXnxh6YrEb3P3Xv03qH9w8WTsrYlX7k6YPsP1UvD10ndfLnvXZ+pcl+SJrzh3RD/sa5j4buB3WRqLA66G/aZ3a9SnnjMjUEX6VPWP6utL'
        b'0rfY7w4wcb00r85vS5fNZMWtih90zvufVndddeKdMS3/PDjTPfHYEcP7b2Ts/5a/GQ8Ft+ctsDg42zIj/w2/l6obnT1CmgdGgT10Za/W+Kjh61MRRWm79JMCoorHf/mP'
        b'994+91nJlgYr5+cSf9O9P21sFTr6lviZos++X/qd77JTt/v2/prcChOKL2z6fJ/3xe/9ZTuqb9v4Bj+/sT3xN+f3J2RuaDTc3WN7o3WC1/QOl80Fv/A1GfUyzeK2mzML'
        b'P0IdcWfrxi3dur3OsUgn0OKVnPN2daO39x4Iyb3TOWZ17+EfZk77rU/ceXXd3Q9Hf+lpHmX7kkVwdP7e6/2n6mxD3De2/7D2VsHYW/PdJn5wKuP9kkNRJ8o+vLGpuar9'
        b'ez+P/sm/v/ra1+sMz5twP3bf/ykEHCLrX35v++9zfV9HG9JDN1vlFU0xnH+r5va80m2m1bmXljW3dtpYvD43aK8CejYFLvpO8tGltvDDda+9+MXIzkm/z8392Wwzb3Jk'
        b'25qHx+u/MIj6/dOAtbtEamNcZj9z06VHfZfoo7K5zy0/JnehKK550B4Qt5pc9nBSQg/ugfAMqpxNR+c0ZARZpomOrLPG1DWmH0fACTEc3QJMUQ5ZUJghsyFR7IjpFcqH'
        b'Sxpm/Cpd1MSguoluVAOKr618BiZNQZ1UnaQzExNN+ExV0dCaQVMQ/WqZL6remjykQ0e5DnCKqsvWQgWchAveqspbqJ0oYHI2QkVmGjr4CLl0GHKolmgGOga1tDep3o5y'
        b'NW4JtOjgbJPQfmcaZA135STqE7S3KaRDj8RERPtRH0O6pqJaBuxE5+EA0+BmCBpcQ1QNvYMKXFQ+l4FCL9oxZXWPBTono3CeBdDGrxTNm+xJX6zDV2ANU8/uWE2h0NtX'
        b'0/FNQ312SsSyMabiGGR5vgBAXbYI5bhBh0osSzguCmO6y861JgpvMjH4MPSSeuA7SUubh2M7E2k7RckTKGrdjoMaKOPUcHOcME3FQtPCYdQiU7oVgJpNGsSrgAeqZnN+'
        b'UG6tRCzjS14ALQcKlhtmqAFyGNx5rqMAePaAbNaoy+gC9KKCSDzKxCcAniWJiwjOTmdB8FxQbdoQzNoxRCOej8d0RjNTU5fqod0KtN/DA13w4rkVyeqpvA2eqx6mi23H'
        b'xHOREvQaYqHhyQeh0vm02jUJ0EbCF6YSqzs1F2jitFbz0Ac1DkKrML26WwYtKUS1CQ1zcauPiFDHBHdmk4MJ020s+qE3yiOKT7NVTFvfB8cT0T5fmaePrRpmFPpEUIJJ'
        b'm4tU1zoXL9ULio3+xN7TwctBixBFpnBOMhMO2DEFcYMv1BLLh7nQgfI1lWEkjTCdjMqmQzUL/3beDl2gmNXtUPFYsEexmM1Is4+DCsgTSg3UCcgzEM4x1akketBaxQzt'
        b'YVC1HX7MrGgvOmU23AXEOMhhMYzRMTRAj4EgOGyrCrq9oCGAblEpnKcKZ3XYJ82QKANHLnACps+V2GUQIDMxP7Hw56RLRJiiOpzO4uk1e6QleA1FGMT7uliXgQGb3FE7'
        b'UULj3dUoeF7IQ+3MqQHmcqsE/DHmssspBhnVoRo2kTkuUK6Cb4STazUIvrEknXldPw2Xxo3SHQpNCLWZcITK5qzUURXhBTGnd+HRwISa6ykOcRJqGU1RiBqjCQ7RAzrY'
        b'CJ6zNVAQKvOJOMSAmbTmUajFiUEQoRPOURjieqgVFu4uS2KZi1efL5k6N3UvfpwxnjnycpEvpiOrOJWQhpjF6wLm6ASTVW2YcBZMuki0P+akBFPseQxEeATlW6ICO198'
        b'cmP6SzTfhpPhjYy5qWJoYkVUQtdqmqNQjva5S+TWOEc7j46noT3MbqR/qjlh5Kgh9XEe6kXLMXvMPDUmO8JuWz87vJEJk6Fut4OToUs83uANVnRRwKmIRTIbVCzmlmry'
        b'PqLpMXiWaKU9eOdfGLL5wWPlgEqJzc9kOYP+Xl5IVPCqhm7acFywdeNT5Sb/n0Fij6pm/3tPiTe0CFonlFrNUyr8H4Qm/89Sxl2cEUM3SijakfzUFU2iKnE7kY3IgqrI'
        b'CZaQYB55EVNqM2whr6bNW4tMRNa8gUhXZMpTxbgQy5D91uZHU7waUbKTPKPxX6NF+jyJYsgwkPqiMeLRVEmuhfNZisbgf6QkfVoaRWTyRCq5Vf6oqpn0NtRhDlVOKeY5'
        b'DPWe8RaSG5rpm6Oi08PjExQ31EPTN0eEK6JVxKV/I74B5lfeImrzN5W68zfwX2LCoRBA4p8QsO7mHjKXjVr0Z4Y3OzIGVj3C0WAepekvcDWcM6rSs/OFTsF4nkTJnOkF'
        b'ReuGRW4/xVMGBY47QbeX55wlzIZSqSoYDcclmF056USBBZiquZykUr+fpx1qRCdocWNnY7ID9cNhwWRbbQxxo9MKh4dVd8iUVde2ALq8PLerP7m6vb4ZRF6tNhtO2hLz'
        b'rtPW7j4OHj7+KXhAUKW1Dg3MQXwZiLgwY40JU6ZTtn2bVgC+Mvcpzb0FY+9VQRnEGAcG8MVY4IWK7DEdtJKUpDN1hr+70DrXCXAR7VXjdOdmEKMtOKFIUQ0MQrP7W+Pr'
        b'uldF8hEMRzT04DLkURkJNC+Cs8MHR0q8hgyODZzOoH6VtaERtSlYgcrCAgU3w6RfhPaJ2bUVHdTAh26eUXyxj0isuIDXL/o8PzqgP8lwgVHN4bf7vzx30XfMZOebxh86'
        b'Lipa0bxQY9y4cK3CidPTphZffcH3ZkRzfklmfMNXceOjApavONHo/srM5d+KVo6QSmNjQiyv3/vQ5cf3Ff+82FVdsPZooPG7Vr13ZYvS5v16PL9h1v0Hjouckp+teG6K'
        b'j/Hqha+NqJ5TcU886ps2fd3bLUZut1CpnXFcwdXPRyy5Jy+5t/G8tVeyx4yyDx2utFV0ZO/4R1r11bVLj0hcdh3mZMv/dSVQ0j4+JW7W7zZX+gPM6mNnRby08ligaIX/'
        b'iDNxSWdbI1fbl/6W7u+jiZ79pKLk6Drf9zJPucSEPO95e3pL7xquY/ZA/VuF1xae7k94++f8mjrTLfVHltt/vsJ38j/TNX99z3Tqcx1jOs42OqsnRTa9uaL6vN7BGXnd'
        b'hbGfOF/5/LvqH5bnn7iRNubXpIeGGcHdvf+On/nxrZue9k1yry02r60Y3Rge5OMRZJabFuL80a/N9/pCp+z8DN0/H/BTjfRG3esuM0TbQ6++G2Vru3HqCRevI64HIyZ4'
        b'z/qau//mxIx3PzSaFnJUv95mt/kb4zaYZLr+FHvFMKr9nR1tnz2fO+bBWze/1H3x1U73Ran7Zrs2N6/YfO3Qs28WxjaNO1Sim74k6WjKK/OCljbuMNfJfCFZa1Lw1PTf'
        b'd25+peUaTH3/vO8af1Hs9Z9KflA4z3Wc/vCO2yHXwLGhXzT/vvBs1pcFZmkbPRRTvz9zutrFLyiosrX9RlXa1H99bD/6/T2X41LM7pp7306rnDj6ffuIu++bbalIPM5v'
        b'NAyo3nF9RsYu93tvbGvclfBF5YnikPufj5jT/UHoitV6KQ8KvV/xsUmb57LkfGTXJxWveJ3s7Sh8L/hVvR9i+11XfPA8mvjg/Z0/znA6G383d4LV2KD5t6XmSK/uaH3f'
        b'qVSritOpeifnflly54eLH1nd7fxqzmJHzYnqNRYuGtsWl46cYPpA+ipvkK01Rj4lnUJsji0wfood5CzUMGgHmeDNWIWJa1XsLpfAHhEhwoA5NbZRh9Yh1hGqiAJhYLQL'
        b'oz8OYRJtPzH4U7H2Q/uhXezvu4ASgRNSMAkxyOdFhmBOLw7aqXsH2K81a5izZny+NqoYhSbPYaTCXlSFehXemImpeZTQRmeZS2Y4hi5Bpxc6EONHDBczRZj3AsaFQi2m'
        b'r/Yp0Fm3IaPGPMyrkHNEDR0askwm3UfdW6OZzxp0SALdazFZScggHzdjGeY6ioUerkIFMkOeeBGDXFq9I35RKwtO8UKFqXIRJ90kQket7CiFtAkT2ZcFa8c1Zhz0rp5G'
        b'i/QDTNIpBK9pm/B7PARam3g4lSw4ZTuDabx9Q9aQsAeyRFsTDSiduhzOTZZB1lgHPIv8atHs0GTBEUYlXBZMO6eiekwbj5PQyuJQb+zW0CHLWcFuFl0UuOoolIfKqR83'
        b'jihKDKFDhOvbDd3MwPciDESgIih4xI8c5SA01egoe6OLM/F1mLdO1VdGJqP1rGAvnH7cxnGVtcQAs+P9tAXrTaFsiERW9/KGIn4cXkeMx1iKLqySYY71gIpXonGRjGUs'
        b'd01TEPf+qEiM296ya50IDuCLYjd9qw6F0YTdLyL8uBi68Zg2iaBquQXlCLbg6S+XOfiksRzpuOYRRngoisUbUNsixm4Qnd8BwjeyYdPQQZfn8FHL4DIzbe9BxwlXr3Ri'
        b'x41ezVzYwcXZ6UR3gDrg6Ng/hk4c3DyEnBhpQKtMz0QlQ5wsUZvWU1Z2/DxGWp/GXHCjzA2dE5hZgZPF9/EAHaz5sH+2kl2FU36YYw3A651ys3sxH9XnBSWWql4Il7vR'
        b'0dBdhgseDj2ZG8UIctTAFliAZAQq8GJ72c9khQhz1J50+jdBjuuQiWygiLjBO4CqmE1EP6amsh/FauApOixZv0jG+OQ9uFy8wxvjlQwDZc9EnGm0ZDyq8GCt74yBXGLi'
        b'y+gIjVnjjPiIJFRLDxNzyDYefMeoHDipRbs41lSCaaN9i1hjcvB5cIaxynjWiVctKNHT8ubxIXFyHLN0PgZZaA8uixA3kO/ouV2FDpkSpGa4ArP/xH4lwmzOkw/ZQQti'
        b'vHEOqvlCBx59UvfstExUjdqGEZXqnG6QeCrm4uqZgKoBHZB5DVasovjBk7IfFUuhOxBvCVKYAf6mAC+zVlKcH+b+HIQoZWLxOI1MupCCoBtV4Ez9qFUA2VCITSE6KDf4'
        b'/8hK/a8czag6ktEZNJHp+XNMVSJhbDSobTH+n9cngdoxOzOahG4nrA9mgEypGxnC9BhQdkeDslxjxBZpmDnCKSPxaGpTbEq91/PEcpgn/1NnMbhMbZLmNcS6Ym1q26yG'
        b'mTBin0zLlDKf9wYiCc9q1BBr8I9b61IWSmCXmNnIW/9Le2OBXbIZNowf/AV7lKanGxvT5hOrL9MnhmM3DiVY/ch0xhWGEmA+ia1LvcNQZzHURUwi/nFDXTC9vaGtagt7'
        b'Q6Zil5o2muQmUNK09eQHCflCg8fd0FQa+t1QF+zvbmirGsbd0Blmkkbtn6htDh0QNv7G/3cChyGLpB5c/UwyHxE4paEr4SW8nWhSBPUxI/qf/uS1xdpiyjuhA/gSrF2H'
        b'KapHTi4RNwqdlERDi/aTjblmcRzzqMIpgwmrKw27+D8fV5oQJPbco4Zdy3wpMy7bqOs0YtmU6dOcp85wggtwJj09LTM1Q4FP6zOYIe1E5/HtcA516Wloa+lq6sjwXb8P'
        b'ClEpOhSwHJWgw6ukxJKgVyZDNZYU7h/mhsqd8Hf78N9Tuan6qIc5KS/xSnTCpGs3bsA0bpp3IlNiX8T3aLsT5sF5YmjihC+hgxl6+EVgor+Ta4Yax03npqPDk2kRpsmo'
        b'2QkzmGV4tGZwM9a40vrcoAWVOeErFk+wM+cMF3xp5nVWqMEJehfhEZ3JzYQKiwx9ctzXO+90soaLeIxncbNi3GgJhr74BurSR8fw3y6cy2g4IPgPgAE/6MLdbcBtduWI'
        b'/7M9tOzI5U4Kgo7BjxdyC/1QDn2qQGWY9CmBdtyVRdyiTUb0KdQlYhLRDlXivizmFm9cSp8GGWxQoArIJoEvuCXopAXLWxgMNYokA9yTpdxSN5RNmzcOqlEPzu2Lu7KM'
        b'W4YGZrDMJ2CvncJBjrvizrmj/iAWR+EQarLEo9hP7iMPzgPVT6MDnY5nsRg/r/DAjfbkPDGtOUBLz0wjDmPrMnCjvTgv6IV2Vs4ldDQYdcWjWtxub85bF51hzhyOkFia'
        b'XTO1cMt9OB+oDaPFQ9E6gv5Dx2xw2305X0w25DE9/VnUicvqQvXLcfP9OL/pctb6w4pZqEs+Bbd+Oaauc1ey3M3xxGVDD+rDCX/OHx3dQldDXKy2LBxO4aav4FYYprO8'
        b'RXPhrMwfkeEO4AIwKVVLS5ZIgvBanI+bvZJbCdXQxerLQi2oSTYtGLc7kAuM9mTL7zC+sUtk6NBI3OxVmM3Ihkq2WkvVZ8oy3HCTV3OrUT3k0s5jMq3JSIYKFuNWr+HW'
        b'oNPT6OOkxdugAB1FpfjvtdxaCyhiDTy4ENMCBejgWNzuIC4oDPWzsbqA6twxEdGIGnHT13HroHIFLScBTkEZKou1xo1x4Bygcysb8kp0JAyV7UKVuDmOnKNFJJshzG9B'
        b'bQAcI/QcMTTKMmM9bUofh8oM6bjYcrbOtnQEbWB/TIC7Gu79RG6iXTAtIZyAuMpMUTbuzhRuCrQh1vAIvPILUBle+gN4FO04OycdoUMob1QAtCpw+yZxk/BSr5PbZRBa'
        b'UGM+ZFMjggLbkZifRAdsSfgpMWeIasTEIgw10vgO4XMS6Qv8Qwx70jjDpfh06SA5GqGeWjnBmQm4TaQcx8E86KyUlpIMp5mZVAGqGItLoDlEc9M5o4mkhLxdtAoDGxLo'
        b'SFmCAWeol4JbgjN0osM0Bx75ItTP2kGy8JzRyGRDnAMwS0YNtTxhYD4rQXjvmCQi79vgAi3BF52YJdShDvVpsNuYM4ReUkcf9FKDn5VRJkJH90C/uhVnRL5fOY1+PR3n'
        b'Oz/YQNy08ZzhVpRNh2GVGmthhRFcFMbIksj+qwcHshZvWtLCXXPYeONMk+G02Aq/p30sQ8xQLdkYam3pLIihfg7si+SMSA/RQAitYCyU4zO7YHCc1CM4w4CZtAez4CKb'
        b'h1bMRlXQPtAcBpwR7Amko9AJJ6mpEJ6q8UIblmuwvrApJz0R47OLcKLTrVAvfQ57iAsQGMATugPfMidwHgOopnVZoFPOrLcsyxzSG7hIy9kwgxazBHVaCHWRQcftRZcI'
        b'H0jaU4TXBb1mC3fC7sFOob36dPZYi+jYFKATzCA0F/q20fr24kLwukgbzNHMArqg7owUoTLaJvxe34+OzlY4wmzxmtEJl8HxxTnmcEa41FYRnQIWysQE1VkpR1gdGnAh'
        b'jnCc9js1mK7jJVtnDY6v+jjzicLAbUdH6QzPW0aEpuTdQrwELuG7SVgCe1fSJoTvxBcnHdgsMmppqB324FV4CGcZAxW0CVao1o62kOaYg/mgLKEQD9hNt+121IAnmnV1'
        b'Gx0itiWEATHHFyEV/p5Bhx0GOwM9dG0K+eiwpKBO2iMv1IAG6IswzMPvTWPLHtrt2bg3ovrkwY2dlRYEOUKXo/D9SVWUA3PhFJ21lWPFYs5oJnW600EXG2qyx+clm38x'
        b'NNB1NIXAaMV0N9UxA8vCGNQk7CqSB0+LyJkcDl6udEDWQ4Uha4At29eYUTtDd/5ZOEFH1VaPbM3BaaW1uKB6Ohjr8AVIWpnpjWrYuWEpWjqN7asIdIh+bonOrRzc1/ij'
        b'CLwsGuEwXRaXUDttgzPuRpZyIaM9ZLHvSaXjoLOZSfrXrmZNQFm4C+i8mA2jJ1tXqFDXnL5mQ4F3AnRMpJ+PgxraiMUhxEJRubQW4hylW9lAlaMq5mXpGNTDeWFxLpSp'
        b'LxIm3B9K5SLaCF8rdNiLBjp0t+dR31hOAzp4yNpqf4dSlAfT3ORa1DZucQJPLZHd/DYk9G4PYgZz2610OFOOs96dsEnbMDCGPXzFiljRcVOe0cqwS58wgz3UnGXAERGA'
        b'vvOW7ddXrGQPp41j3oDcFJu1L5rPYw/1MnW5MUSOMWVjQpH9WvZw3AQ1Yi6vf21XqvcE3DX68DvfERxeM7PcPDd6X00VDPv01mtx+PLVuLZwq/f98HHsoVaEMWeNK+Lm'
        b'JAfvsV3KHo52YrXrW0YnGI3QZQ9/c2fdnKKeYacX4sdRG2iXOSPx7cjpT5kdM2ftPFPM/q1cSl+8PIcVcXB8qt1Uq5ks9y9+6qytG3bYuWKO+c6RKvLflfm0Ao901pPl'
        b'O5IT7JxGc3ec6H/359Obd9NI6omnF+oxCZDMJaOcOPrcBJpRhS1kQwO+wjdzm+ehi8wSmSwVfcgilqOqSw2T7GSprEXFtNKQeBPagd3hkcGbNyxhXS1wNaKDsjtuw3Zv'
        b'vR3DrR2VHseIeChWsHdksZKGYiQJaJAb0vikqOjNgyGStLk/CpGkpzUUIonwqlBrB+dt4ZChL7H/pfaEPt5+6NAwbeAjEaegAx2RLVjtR7vA71zDncGTdWxt0uh4ixA8'
        b'Mb6+8b++9oJUkY6riXr9pyUrXvY18tc/vW1bzNbmO1eu3X9uss3+8V8c+1i83Td41CKIMLBq833GbeEYy+ZFX7QHRXZN+Vwv7HpZz2cbg3vS4oO7oqI/eOHjBkVyYI1r'
        b'4J33c10t42a9ZFkwJvi2/+688Z7Wx/fYbDBdZP7Jt9fdDO27ry8YaTgr737P7oKe7JcrnzMOfn6G903XpLDRM1NlTj1F76JRi/yd08af86j/UGf8oZMvjWoRT05zjm69'
        b'bf7+z82vz7q/3iw6/faEd0eMmvyPMy98oKl16Mpzrvienvf81u/7r3imm/au+OpcftfRf7X4VKId22Q1RueS08yi3g/zTLFZuSPoqyNz+j2KzV89++/8+/ZfXHOXj34w'
        b'yn3Zt6P1Xnt1ScBBX72o/c9m3l7qkrkoenKT3Tfe+SEOGS+V9+qfqrngvPCfaVX/yMx9uRmiHZJcVvz63KGu6sO3r3W9LvF/v/1s3s9t3x274KZrv6Itt0tcapd1Ke5m'
        b'a9qM1GUTfmq9beKr8F96vuUfzno7vvQsOhWMrK6vsK3NeH7DjyfOBP7wb5Of9R5u3jPppULpxZUHRta6TpMHzTmV8+L5xT/7mvtF/H79xYZXmmfXaGt4eWRdLJmWcf3j'
        b'd4tenfZJ5cydbXvGvL1le4jsk/xj27/M/dfU2NHPJttVTXq7bHxtWmSjz16zyl39XrFfORo2+3jdit2T9HJ8/+hn1ZM8vq98rzN27kr5D2t+eu8H6XMdk9f90l18Z883'
        b'UyZOXPdp8ZsHJlZdv2XSHPBGR/StSRckbxttd538Fnrn0g8piY4PD71lvP7jT+/Mmfn8J1tevjb5S531M66k91aVW91q/90rO/Gr+Tav3cvbENLR6C3/qDrr+1PTjt3U'
        b'+7n4uQsPtIydH/Brp314JsJJzqxwZsGJOUTO6uO9KsZPykm3i1DjLDhEha1WczEHVUBdPHASd9EGfHV04Zu3jEoW9Raiai8a5c+LONaWmctRtZhHRcK3NtA/jYRNQxcw'
        b'bS7WEulC81S8W1qZqqYxbiVxNNHmKeUkUaJlzjAgF6T1GnAKHSAufzzsMF8oC4GeTB5VQz+T9EMJNIwYtFjj13HUYA3vx3ymLzk4GfJxuY64PZIMkQUuKh9TbRepDgr2'
        b'6KF9tiSGDMdDl5W7aFUQOkM/2x63cLid2j5MI5/1WkrHZ1qws4ADkXLa6LxEjUcXE+CE4NShDcq8qFkMrnCkaKIBvuOrIZ8qfSwmowIvpolCFUtEC1CrO9OWtUMV7PPS'
        b'ht5hsYumiGPl6LTc7P/W5uWP5Ybqf1E8e0NLERmeFBqfGB4bTaW0l8gB/WdMX3ZxPhLBT8OT/2nxzHeDFjVi0RVPou65icEKMZUxoV4edKmrcOJBghi9MD8RBsRIRmyE'
        b'f4+nXh+Io259amTDU+MZLfqbmN1Y0yilgxJeCc6vL3IQpX2ilAyKb4jjE2NVhLJ/cnhuK61USFn9xEqFSD3/hNiV/HvRVEX0ymitvNh5toN3kJ4avYWknMl6icYCqBjm'
        b'6VVr8Fqcxyk9vapRd8gMicXHaCk9vEr+0MPrY4I7cmU+Hp7b3PfJ4kLizQLXycfwfxL9mf0o+pN/rC6pL71QD1oIfj1tUr3BPoKjBjOz7AhOChWsthbggtbuHgHuqMA3'
        b'ChV6SLmZ29Sskw3jf29YKFEQ5U3b7vAvw9zDr8ZYl94NC37mzMGskvqP12dPzWmpOpt/du+4yqwuKZf8L7WfjobKeWazuM8bDqHKUK9BvzJqc/iR87ZTvQ3KwyTsocci'
        b'D1NFNhTqIKJUyxvEXDxBEnxDFhkXHbkxlJIodAtN+fNbaBdnzTzjbx0bSpwahxLfCEOGWSolDy5oUbzKcuaHrdrPlKv2U/yXsZYQofZPrtrd3Fe6quuW+B4wgSN4eApI'
        b'tGgoFNAYqrZUk1AnNafyoi6aitVgPzRB4yqidzaVoRopOsxsqnJ0TLzsSPCaQgmnNnop7Oa1ADMRVIiVmJpqi0p9eY4fIUK9dhw+xJvoUhm5QaCUTZJWP2u9mkThpIUd'
        b'Rtnokpe3r6891K5xUOM0/HgF6pPSb3ZPYsT5lMyEkZWSFE5B5Fi6AcsCdFL0C1LFJNwMd7GCUtFLEwVPoc5LnHSdNnMJZFgLLaSSWp5OoPa7pmGy45yCCM6+vTUyIDDj'
        b'+01iTix9rlI08aoJi7yqK0BfMz8zDg+TcQqC6V0qjZzXRyAqMk6WqaD5NgQxknzKpKuzUx3GsXwfNZZVbP5ESoDAuravKYhobW1i4Cef4i+/+W4SZ/r8KwoyPFYeMwIC'
        b'dTJ1UlZiqnb7HXtR+aGfFeQy/kjrGFXMtlh7HurywRz0WfHtr9ToyU4R1mh/wut6V+yumN3HW0hdxE9rXEPrff718uj3XycrhpOPCaGPNu5TmOS/jsfahrPZ8Dt9VLzq'
        b'zfDbBXgZhXAh621o68YdXVlAQq7f2n2Ly2k1pM9MnykvuI4/nK7xCZc7kEl5wkjoQZWowIPhfMqhzgmPEhTwniL1+MSXI8SKFlzsoqDqJSueTXrDTftc7LQr3pnvLXw5'
        b'acUbB05u/fi5Zdzccr0zq2xKWp0XnlQ/sFK+pGau5Q/PqE/YdU3vpn77My+mfKG5rdPgcOH3v/32272frsx59gX90i3fjdAYP2nZtZwHIa1L3ZPgtFfS4k4Xm1Kz755f'
        b'GTC10vzB9vxJOY65r8RNtpycuuBTvf6cCRtW7ph5wu1S145/uoW7GW1PN1z867kJL1Z8YaJmKFs10CAdWTZqSp/kXty7/1htHHFlonl688Oaf6HMule+WLb/9VNXt3zg'
        b'1rYy3zZwf+3cXt3Mdzru6IJLUthHSzqnTpj8bkGvc6/a+a8/K9zx72Ad6w3z3t7i8C5m0x5azuM/fXDWd/0FyNohs38u51vxuvXTp3w+ULzRXy11/G8/tq7y291p/vl3'
        b'bbPU3xw1suyngd8z7DfbbGqef8LwZ7OuOzO77szxu6v1SqttUIttUEzdtJd/X7L07THZZp3LPgh/60Rz163fvskr9Fzyzs0P6mx/+sZy/Cc9jRWrVsx98UT3hy+qf5cJ'
        b'9+4s/yA0/+GBbzXnvbz9Vm7pB6G5hp9tt31z8/SP9I6vLz9z6YpDSqRD02cG8Mn8V6rqitENuT4jw/ZPTvSSE7NANU4tdgm6xNuYGjDartCEYFyL8Bngh0rc8WLTgIN8'
        b'smK28BYd1CY2Gj7Q5Ik5RMlUEbThRdFDiSr9kQRPWUD8fhWhSmJpoo6/rud3wkEhlF4QN0+RnpmpowvFenqoUzsVX5uoVrwNc6o1qH4Ms6/fNxtKKF2KL9hyRpvCANoL'
        b'hcyKqBSyN6MCH2gjobeyRah427JAxFxFBs0JsPUUKEG1Fa4EP4Bq0Xn23Xk4bU9bZ+XACEVosEPdzG9iLqpHRzCFyWqdhyvVlPFQFo262IVTBeWW+Fu5PTF3UAtD57bw'
        b'VrHp9J1lEpwSwB0E2BGATvJO0CgEHqx0dSKl7vPwxreULEMHzvKoZpmt4H7QcZmXhw8Z5zy8v/BAh/DRW/BAkYF2JQGUVe43dBQd4EfCYTZJM9ExIn3Cp7a3XI1YjBZB'
        b'HW8ErXb/pZr671gCD6M+h249enVW/pWrc7KulIaboRSmLqYo9YWI9cSCwJLSiIRaJIFhCKWpTf2IMU9kJCehOdUobUmoVEJdEuNrHr+l5tfMVkAon9ChaXeUdKX0hiQl'
        b'PD3uhiQqPD38hmZsdHpoenx6QvRfpTTFaZ+TMr8gP+4qb29Sj9Ffvr2/tlC9vcneCcjEt7Fwea/bpgRTmvhIjOAQDETyArFGmqKk/cjdRxXFohixEu/PP9XvxGPUn4R7'
        b'3PeHnLUJsrShAvNXBIxNhIIeUrRbxhnABTHa44dy4nWsXxcpyA478eo7X4bdDftiekeYd/i9aK2YjxNEnFm7OOWFPBVHIeI/VNDf0CGzMnx12fyV1RWX9qVyviVsdr4Y'
        b'buGhSn3xj04i+TjwL0/iaX3VSaTKiONQqM0GTJUKU+cmQhmUL5KuNAr5n03kY05cxI9NpNg3/sbCqyIaG8DoK5svwxaU4EkKS4iJiHIP16CTNPZHcUxY4p+cJMV/N0kb'
        b'0+49OkmfP22SPh8+SeTjNX95klofmyRPuLTG1vcJc4TqTVCdNAxVGz95kojZTR6ZJlGeJEbyJ6dpmG8NMkWPR2/Q8qW0snwd6hUIbzjnQmhvXgu1QC2lSuUrLPjtEm7z'
        b't/MH1sYuPBXCxNMKSnSveUcjTHtA4c8EuRt0ReTpcsX28Pm6m32Zi46d6KAZ6kR7A+A0WabZRNiKOmj+cDtK71ovtwpL2LrAg+XfBv2oJsAeVdiOmeHuIebU1vKi9LXx'
        b'cfYnpYqt+P1nW83Nr87WhSlGi69Xpc77h9rBdxZWiKU+nrYlr2VZW9fazjyQO9Fy24nK7h/jXghc/q+K1wNN11ZVfVs+zsY218nAecKlGPRJ2ncOG/0Xlp7Nfqfa1zpk'
        b'zIb3DH78OfetX7Vufet273r1w+fRvHvHI5v+dcrv1+nrp56eLzeyaFxbJddg3k0rQnfY2lu726NSex7fzEd4e6ixYtEzPVExI3Gs7PwGKRzUM5n5N61C58RUxVFggsmO'
        b'Ij/idaYQUxohq5kTWdQN+VT4dXGTEAiaSL8qXSnxMh6zWANwihIhKH8LOoYJkZ38eMifL+DP9K2JIAvaRjBZFhFkQc5I2uIN6Bh027objKGyKMlMEbTDCWcWpdsMCPBr'
        b'/yZ0UQXICW3bHtuNeN886X4a2qPa5CBNiYoJJVce3aLz/soWTSKyGV0BHGVK72cDUdpXKtt2FalF8gjG6LFm8mlfk29WDbaLFrHuL2/eEwaqm5cKAHoxqViDd8hZdsy6'
        b'e+BL050O6ViULUHNqBtdGHYsagq/FSaPRAErF5drl6vH8FF8kYgKbfghBzoxGlHiKEm2xl5RkCRaGiWNUsvmotSjNIr4IDWc1qRpLZpWx2kZTWvTtAZO69C0Lk1r4rQe'
        b'TevTtBZOj6BpA5qW4bQhTRvRtDZOG9O0CU3r4PRImjalaV2cHkXTo2laD6fNaHoMTeuTSGW4V+ZRFtkaQSOipTFc9Ii9XLEoaAR+QwRUmvjwGhtlid8aRI2jwqfxN9R9'
        b'wpOITd8v9sNiz5CAVZaJ7BWLxjU8Ng2mD8kBPey8VIquiFKHeieiRmx0aMkFp6k8OSV/eHKK6ckp+WXvfwx5NKyFQyGP/ijAENkWLMYR+YuEMgpnRSxfvNQyJj7hCdGS'
        b'lKuJLGSNx05vCwbsglM6UG5LVuJyG28SZsV+lYB/wpzSPjsHEbdMpD4Tc9m1GURiB8WoHJ2Rpfh4pgbg14N5V2oQ4QEJG8zCxHKRlhrasgnUMM0cVXlPHjHMm8wxS6q2'
        b'HYHKR6AaOKASApaEfx1hQFn8BNQDZRPQRVtPHxYf2lbEGU4Wo+qAmbRcVLQhPh4fetM8eU6EOjh0AU6aMVO4YjgnR6WioQjHa2A/VYfrBWt4US/0PiJoNeBkyTyqWo5y'
        b'qPx0DuZXsmnMdYKVLfDGzXFCR3VRnXhhYCyzCWhHB6HPC0674xZ5EKdEhahbz0q8Rh+PDg0nPy8Y85h7BA6JhrS9wG9DmI2kN+VS71g4bIK5Kxv8mqfyCsiaDvm0aVJU'
        b'7T8UsHs8c2e0wSJDCLvdY4WaVg93awCF0EylW2oZU+Cy91BsajxJ/bRCW9Sb4IG5smHuocpRGy1UaoiJ5CH3TmgfVFEHT46Lqejqw4lEdHXNTcstLOG++VQWHAnVwV6D'
        b'AHKhDBAjLtSpyVzORBIZ1cHpJK8Bv4YT6HDvGGs4Bx2PeHJiXpzOCNe4vi259cNSNbkw7eWYlh00miqDffguPzTMuZSIo9MA+EJKHeZaqgCdo66lgl1pz4LwaVuK+qFL'
        b'GcudOJfCD7IYdLITSlGD0gOUBFoe8wCV4Ehr2oz52WqyYCgbgacMymfqomPiEHTaKf6dA7FiBTFRvv1D8Y7S/rBtSWiK9hKPqrNj7vx+/sZHL6mn3/vwdMHIeumKY3vL'
        b'/Nd/sWRU0G3De00frd3vP9btPbs3LkpaTkW+U/b2+hmtQVtD9uYc3/nhLx/qBn3Xh46bnN7zYbJe/vNqodcmr5+5Zu/e37/KatOaq+489eOuzjsBb0UdW5DZti5xW8i1'
        b'qrsr00O7TWp+vb/yrfp72g3fLJtfOO/AzglJlv2RZtMmvzYqc81xZLjqm8zb38qjM755tt68evlkNQujuoBUp53h4/vjlqnde99t9jlZ/72Vp+e88PUXxl/envNVadpn'
        b'KysjZ8SeMzm3ryz2Qvr2O0kr2n+yXe/+WV9JkPuM3yqmD0y8d37j18Gj7upX+SS9pxE9rvxtb49i39atkZ4RnoEfpJh4mDxvV2r3S4PdmodLPOZbfz5+4u8NduM/vXwl'
        b'eOYKWUtd+ZJ3oj1/aX7/07TQVx9GrBot23Rt12/cD5GHv6+6IR8t+CQ5apFibus+RHd4wwClO1ZtCPbytnGgb1A5HOJkCTxqhEtRjFQ6vBnVoQ5MMRFQewGV7mugAn7H'
        b'hmgG8SAhuHuUwT92yJThPzSgKY0C+qdEJKDGyCeL61HHCG0mKdkNLcZE12Jvs4wcbYTuhQOonKJwphKPT/iKHzzZ4CQc4GQKHh2ZGkNVgP7EuCpvodcgHm0EOk4/3Axn'
        b'pTS6Bznz4HQMPfZMUK3Edac9oyA74WAGZDlDgR85+cQJolVr0WkmEKoNMocjsdS9qDdxb1AngoMzllAS0AGVWAyG4CAn1+UdJAIHHEfVDGFzDp12xKdbFzVgUDkCDWaK'
        b'oX4tOsngTIehnQSVUOCShk5Bg21iuCDfwTSY+2APtNEWsCMQZz/Kyfxxx6dbC6E1MDF6kYQ0YMfg5AhONpHHh9RR1MmkeQOr3YlHAzi3jsapoQ4N8HDW0tlLRgUBSv+p'
        b'FOxFjgM9TXE6uoxy6DAEztGhOTbr0aNDTYMfBfmIxTxxRwfTPFEOmZmh88MANYlRFqpOoA30RV2okiKyyNlhgXo5GV49+Ha5hCrpUCZBYQSJmM7OauJA4YDuIvFS6PWh'
        b'kb61QuMZm/YER3CcGzo+OUN9hIUtrSoUWjF1TSLBDN6bmEI8qRsrdtUcw8JrdJuhaisC4vFTOYUMZolhIA72MPRdXRg+KE/LCD05RFQa6IqhGU9Wrlz6x5Ihzb+LS1A6'
        b'+D/zV4j0XZyWFiXRtakaVkPEBGsEIEPjOtN/xJeAFlXsEiGZmkhbYkShMlrU9f/gU/ZPm9enCt6/kl9LtFVfoBkf9esvQGzuDuftNf60zJFnn9oMG6aUv8w8lI5RBdU8'
        b'1tg/61n7fe6pnrVfwe1izvuVNSj99o+n3vIF2nTIg/zfcdQvOH1WD1XExyY91XX+tcEGseoHXeeT78LTM9L+nsNtSWjEtIinVPq6slLrpQnhsZbxMZbx6Sxu58JpC5Vj'
        b'8Hf8xa94+vi/pax5DHVunRYdFZ+enPaXgxMItV1+eiSEd5W1WQi1sXgEf713QlACzdDE5Kj4mPinTun7ylonUzf14Yp0S/ZZ5N+tPnaw+ujN0ZEZTw/G8JGy+gnK6tln'
        b'/1XX1RlK7Gk131LWbDO4rNJVthReX6yIv+XUXT30/zH3HnBZnufi8DvYewkoqDjZoKAsQcXBHsoQcLGnLBkqoIIiW5C9QdkyZC8FJLmutGnatEmbNk3Spjlp2mY2SUd6'
        b'miZt/9f9PC8Iilk95ztf/EXhfZ/nnteeUdERBCpfMf/vl+ffzOES9/x3q5Yfs3TgSxD6FdO+tzztllUw/Z9NvGQV+oqJP1yeeMdKFZmd+ZJ+vHpyydwcE3s8IkW4HJEi'
        b'KBaQpi8kTV/AafpCTtMXXBWu5ZNgQz1pypZ7SvTLt6h8Lumk/I/gNXvycvB1MS6aa1ycEcc6Qj+CsrRovmMC1zg4OSXjSSPBKkPB0nU8YY1/3vqPAq62/Vt/+IOksv2L'
        b'gldeEsiVCmes3jEW8nL3mN6lJck1y8DjkeDq6vGUguuhS1m7XGebby5G5Apkszcvca3lPT6KaImJjc7w+eZV2NkyPlGQZDB+YzadJ6hZWY2dCwW2xl7WCVEizWHdI9MF'
        b'Vj1WHMiTk/xhQUYxHG/AgrTL/56D5ck4KbpS5dAXpDgHy4sDMcwHlhDzUdjNWM698lZ8ImnpPxfjn35DV8uV2CjDPJhcVkv4q3UlDYtuNwmqvs4Dkxb2nS9a8asvOj06'
        b'Y5Xslrz6slf7ZR49sbyov32Ha7+5yjPD2sJgSyA0fMNrJ9WAXbuJIuZ5YckRvGEs4tPs7tpCPgcUIesEUqpC6AtO4oxZZ/BuEveWDT4USFkLmYp2IF52T7OIc+yM9r92'
        b'LtYt0ivcKzzh7bvRcbFxsV6RHuE+4cI/657TTdD1PzQb/O4uaevUXqFgtEXuF+Z2T4SZrR1ylhYsAR2+dta3uTSxkqyKKFv9iYtbmnnNC3ps5o+/w83UrowtW2P+tUkx'
        b'5x7ji9ELlt1jX0eQY4kgez9BTQ+zULp0nt0T+V1t4003SM+IT0w0uBCeGB/1FeZaoWAtRiLjE+DCGcxcvbMFcvSMmt6p9OBd09viPze+LJUeSt+8+v30D58vCftJhNEf'
        b'PMKVYt6jn8w0xNVeR/2MvcL2p49pV0YZ/+z6n0MUvA4OJKx3aEzQddBtaSp1TNDVHrWIEpTuMgs79YNjaPBs5ffaofXHflqyPxNbNVhvFPzsXd2DZiJjOT4qZcwOFk0l'
        b'qmZiClM2VWBa7Io1RrxZpMM/3jSXgH6VTfdKgET5x2KcZ/Eu+Y/ZSCfU+TCbISiPWm3xlT0pxhbj3bxtoDzNZsn+SnpzI2vzt00cfHw3bxrJC1tHGAgFV7gGCEK4DdXQ'
        b'ya0q0R2umcIItBIuusOQlEAmUbQVrvMuLl0sNvGkTw/BDTMZgZS+EMaxOHmJVXyd60ouPj2Uu1MOWY58W2TR5Kv1cf9zwcys7ITUCsVvafincbQ117eKwcnSi198B3wq'
        b'0lhTE11ekLHmWnUdVhRw4PxoQeyQxKSHpTELctprrJ6D3JL28IbckiD/hgwvE78hw4urb8gtyY9vyC2JgBxl4LbDn8V/3v1wBdX5hBZ2jp0SqzMgR+BjdPo/L6ugoqgk'
        b'4qOzZ2EcupaZhLQArmOzAlSIYE576yp2rSH5N/36444/mVrdWkGUqJy5w2SLlIs0ijRjpL+5w49/i+QIxSilG3LM4RcjiJbjXGxybOwo5XIhFwuuSONKRalEqXLjyi9/'
        b'J03yqlqUOvepArca3SiNclHUdu4dDe4trah1N+Tpe0X6XsCeqJWlP7pR2uUyUTu48hDSkl4fykUqRWpF6kWaRboxSlHrozZw7ynx49IfuVp5WqteuThqJ+fklOY8caxf'
        b'jUqRKputSKtoXZF2kQ69rxalH7WRe19Z8j73dq1s1CZ635Cbk72pyr2lTW/Ic65E9oYKt78tbH+0A1HU1qht3A5VozQ5acroDRUJ5NM/4bHRaW/voYtZRb+dDVY/wYg+'
        b'/ZtuEE70fiUXYL6/8AyD8DRmVzmfGU8QvmqgGJLTueej6KvIDKa5xWcYZKSFJ6eHRzK1Nf0xF6F7BnGVlDTJVMuzhKcvKz7EjpINwg1i4y9EJ0uGTUnLemwYCwuDi+Fp'
        b'rOeXg8OTPkimUz22wWVuduhogLOFwZGUZMMMg8z0aG4HqWkpUZnccres9rpKLGS+zPW6MiFhdQ2R5foh7NqXa4iIi8VPTUWQqEhvn3z8YrgjeszzusSQk5a28p2cr8sn'
        b'yZQvus6Vx7+mlsXunLuqKAsDd87MFJVCKyKtzCD6Unx6BvvkIjvRCIl9JnoNIUGyIIlCza/pCTX7YjxbJH0Tk0nDhUdFEXg8ZU3JUfS/QXhqakp8Mk240gz1FRIKu7on'
        b'Ez2UfTgdyNjeemW5TrdluzVpRuVeXFlNPzcvn6UCY7CIRWH6itiDi9jNdVORUmWZZWwEeZ3Hx6A3JVb3C1gkf0UtnnOdBmPlaawhGdlNCnq3C6QNhdjoDA+5nFMhjprA'
        b'LRg35VNOcQEneCfivA1Ma67zNyeVbRx7rARiC4Gqo2g75MFopiEj2GUh2MS3l0qDsqWUEeYn57tK2RpLQ5WRkKvTsiMC7+ANoSnrGSFIj93GJwsLJKkFO68IWhS0BJlM'
        b'57+ShA+ZQ1EXGyQ7wmKuc1W5GVZ484XLjqfIkrp1X8yJ/2ex1Dj9PLGLnigB3hJAKTRAZfx8zAZx+vfo6/l73kdvsYAmpcLcPuWkrAPdHgYVsEMg/1qw1Z2t60qsehXN'
        b'Yq6Zbv/l27tahYaK+eb/vnp5ev265rfLlZze87npsdfzuMnApMfpH77xiv/zwRM2JUHmnR/c8Eh/5+fRW7amRoT/rCi7wTwk7f5P4XDJsV9hWLmyyt2L5x+MVqecHfe0'
        b'2wEPs9fJN6lpV738WarT2MOiF96N+8VtjR+caKv50FXu6PyJ9HftRtUO/O6/XL2GBv70e9MFTVun03vPWB7wuBozevT8P4SbnzswdcjAWIurWmgsslvy2HsdEu62xg5O'
        b'4NxzJmTZWcd54WDqAOets8jgRLuwXG3mN1eGTg4wOL85NsAoV5EuK92K8yDifOaSE1GZL9w3R/A4zNyImpq8y4RzImLxKU5QDYc7MLeU+QetMLQU3NQHC9z7MVi+y5ML'
        b'kYASuMYKLcpriVibsQTeD3aDhM2xHJqjjDi+DwNfExkSlCfFxwUOfGHCUWwNMbXEUhIGsMFMIAN3RWZwBwd5Y0rjgXSJ/zIfbzzyYfpAI+ccPexwlKRkLyiRFQqktgih'
        b'DbtwhncCNh/WkkR+X8Fpvqo/DuziiuDhA+y6IqkWztRSQi5zGQHOY7EOTEu5WcEEN3j8iZglR9KeAIGMpkgZr9txhgAZrD3AKt95qsAcKyvHe1fVoUEMtxLgNm8sGIBJ'
        b'1k4b25iTbBnRVfzF3nAPKrlO7KbQAYX0NksRjYZ5Vk6QS+6BCktPuuUKvv2OK4zJwi0sluUPrGsXFPAREOfZt5IgiKI47j6ueKatLiGYaaVrIHUWez04/+YJfBDNwpRp'
        b'iqW5aOMt8to0zCIOYM+TsWDfJLh6LZ9YwLfVAOyZuCjDBZKrcCHhSlwjbBZMvonTB3jvVbbOah78lLbUyxx2hYrwFT5AMf/sGp4rPUXajMO30xjyBO+uzEt86pK/qZ1f'
        b'+ussv46KEsvvE1Mte7Oslxn3k5x6BVf+Tu4tifflZ4Kv9L4cWFrkN7GLLzHZVabpXbxcxOQh8Tc0Tsf8f2acjiPJK3MtyYv9t8o+nRadlJKx3LaXRMi4lMzEKCbxXIhO'
        b'4/RBg/DYcCaQrTnWctzc4cTo8DTWC/bIshQmMXBzElE8L/ExS0smM7ysOVh6dAaT5MLCAtIyo8PClnw0JudSkjNSuJxIE4PE+Ii0cBqcOQQvhMcnhkckRj9VkMpY7sS8'
        b'dK/0WkpafGx8MhPmmBjuGp1GkJdlZpDCjuNifPrao/EuyOUFuoQnptMKv6vxPqb7XSnOeH+l14033uf8ioXQy/UKX2GVh/layz1Qg+OPKOTIMpHkKGQOXP8ft+GHZu98'
        b'DGXTIxNDuZP/j0z5h78T3VpcZcxn7VKhmmTTUonGLlAm2WyK/ejla47VpisZCdavadvX3aTi5L7hK0LyOYtjkfAbh+R/gwRoKR/eID0B9dAl4a/LzJUFa5Z4mXiYwUAA'
        b'H7eJxYaGLF2LRfHAIJQo2kOXb7xJwVVxOuPS2X51H4ZZaHwQ9mKEkbZJuFd4YkxixEdh74Ulx3wUVhrrwZwFXj3vyArqFeU0uj8xFmcwIHAJhLHHp4YHGmuxdk0o4ups'
        b'Q5cHVq0u9b1IQtyjkCtTR46LQzFUYv5jfDwS6iRQKs5acgZ8Natedkd8a8t2BGPH3whuv8YzsUbk+RruCe/vBMpTq6LP3QRcpmD9Zgkk43TAtwFlzl+he0jFnRSjNmMR'
        b'p5PEm2MnB+PY5sf7KrZhO+fF2JmLg9wrOL6Dd1bIb4g/vveENFfa4I+Gxq9GPe6tSIz1iPTh/BXrOX/FsrfieybyobqjT3orvsLPFP6dLzZISUFNKlv3aRf7pOfia1Zx'
        b'6Dvd3DMrXUtPXw2RPGZZXZu0sINmofREWqSJuEgvExfx10at9z7BYVyJB4UvCUgrDVlPN5YkpUXH8IaJJyKI1rBnpEVnZKYlpzsYOC/3cZfsOswgJSKBmPtX2CHWlmqk'
        b'fTJZvJU/jOMwNpJeVCaxuQYeCzI/EbRmjDvk7ZFPgH4c4oLcjYnGLHg+ZrjAYui+ulJN91OUxfIk6Ivv+6mKON2X3muX/vmHYR+FfRD2QkRczED0e2E/+WViRPAzwTha'
        b'ORbcc8NY2mjb919+8bXnXnv2mLj7HIH7ROO1hJDxxommslaPYP/Gg+N7bz6r1LpeUGOunhX9qbEMXxCnx0iTdFiYDlwOhMW7fNZPOnQcY1qiPWuo9khJdEvmdMiT0ruW'
        b'FOfgMJMVUa6zlnwruk6nWInCfc4zQrgbaiQtp1IczyVIez5S3RRPinAYqtw5GmyWu2GtwNh5Y45QX4H2Vcj6dM1jZXELlvwjgRYOfR2+Lfqm8iGEclyjouwNjyHOiuFX'
        b'h/qdWE2U1/akiPjHHgkZOjREwHfC72Gtlfj9FctcG7WfCFD5KolhCamn1kTqjCfDglJilnJK/vdx3Jmf8xvg+NreUBJrFyN+L0pn9obZw14fhp1+5uVnR61/WzlW31G4'
        b'pWw3V53F8i2pxgl5YxHfRG8MG3CKS75aCreFWk3CmA3YJpUd5MPh02br0OXsDJyTJGggyYFLsuba/mrF78x2cgUsIHUtQJDcylfCq/ApAMrWE/WdALRd5esAVLIuyaRv'
        b'yKaHX4gODU/3WduezwixhBXJcNqrzDe05t8gnTJiLZ1yCXiZeyNKUmv+G4Gu87IrJjojnEX/hfMRUkkpF4i3serwS+P+T8E9/47kgByY0Z9zwpgx/S4pMz2D6b08HqZn'
        b'MB2RRSUyO8Waeh5vu1gV0cZ0RBp8LTfBMsqxtaaFX+SPi/b8FZjGYOlJq76CT+Zujgnttn86I5Xe/hgrPbKDs4vnyKWbqkWz/Cw3AdZpXuJqxuw5N8QXm5ESSPkPNwkz'
        b'1PgE4OdyJYVudn7s//wReUEAZzLhjPhZ0Klkao7dvjSSnwCbDaAn/m2raVE6MUTBL3/r6/1ihwocVJN6+fXXz+kpOTt/+qWawUGDoEBR2kvHmoew6+N/1YoL1u+uybpW'
        b'+Z6L14tyG48/d/z303OvbI8qd9+kkaFr+LA+5HTpiaj2sNfeybNuFV/Y0XRyYH6X9eC594cGq3/xj5/lnFKynvm7jc8vvXNcHzzs6lH2PvPPnz8bcvTTTzaNXboqCPzB'
        b'TqdiFiDBZ2HswLlHaSs6ljAMN/ABHxxRHuawMi3FKIHx66zjfGJKXgAUKEIB3Fhl7uZ4dtw+zjLrFY0zzO7LG31bcBTarjhwswanuJiaSPpACuShM3ufCG5LZ3Is251F'
        b'bGCpw+OGX87oi82wyI3gsB1GV9W6CwyDMSc9TgZRtdCUmKo5OzX0wR2zdcFPYZgy39Rm+oasJOuXI55u3554qilJymhocJH9GlxOgZJQS5itvQbpoolWm0o5srle9A1k'
        b'APGKZx/RWT36NeU70dka7ZV09imLpYP0XcpGfkN+ORCeD4KQE7F85sTw5NgAl0hZCQqzbWgsobAPo70sfZXZDRU49zdzuYuKVIvUisRF6hIvq0aMhoQmyxbLE02WI5os'
        b'y9FkOY4my16VW2Hnuyq1Bk12jopiEfPJ0RdXhzwxqxjvyuQ9r5EpaWnR6akpyVHMdvf0zFWilA7hGRlpDmHLKk/YKosYb7IzkxjKlm2HzLf+xGDhT/WlG0SGJzManJbC'
        b'4k+WAoYzwtPo/A0iwpPPPZ0RrHLAPiZHrel+fSp7+CqWwg6C+YfTU6MjuR2a8ae8JoN4lKeRnJkUEZ32jZ3Jy4DFL+NRwsXFuPjIuFWcittRcnjS2mbLFN6CunQOcSmJ'
        b'UQTMK/jeYzHwSeFp5x6Lf1i+tHQDPmHEwsB3yVTKvx6dEZcSZeAQk5kcSeBBzyyJzGFrDrS0+sjwxMRoZmmOSZGw0eXscB4IMlk4PgteCF9znJUw9NSTXA40dDB4PJvk'
        b'UST20rxPi8iWjBVhFfHkKCtzUr7mfUYZSObw9zWwsbY33839nknUhZAwKnrpqpbGItDnoWRtG/OR6JjwzMSM9CUUWR5rzRs3TDfgfmVBJk8sbpVgIoFMtpVUUgvop28g'
        b'Vi3LK6oSQrdaXjH04VPAu7FLPt0qTQvzSWZIEcAMzJ/jvym8BH2KF85DU6pQIMRiAbaqJRgLuUACqMBO6GEWsW04QmoxVAgP+2NlJrOpGGG9PL12HIvlsZYZD4wszI2w'
        b'2NLE3ZuEn4EA1tX+BB8aALUm8naYh2Wcy18MnfbLERG12MFFNPBaxqNwhsizctAhcOYEoYFoZUGr416B4FhYYvwRsYDL07eFQj8mNZguVa8kxR0GYQBveZoZm3tIC5xM'
        b'ZbAZB3CRbxVyLVnXVESsvFpGIFRnTQ6rD3KDp0XICLT89EnOCjPbYxHIi15tKtKC1w7R6RwMM0s9eoz/MJSmfu4MO+UwpW5dLQGfdH8P2khE6GKlB6FSnf66DuNcrS3u'
        b'HSlbeYFBGulbYWGJ4GMvyGSc0TQX+rn0f383zirsTju4acokx+Xd0BduZh7nIr0s3M1NZARYZqx03h4muYOHcSecfEL2vGnM3N/9AZzcaXrVjHngSVe7Lw9dudjtYizH'
        b'13FcDImXJM1DJdyX+Iwdr/J7ub8N6ljWPE7q84nz3nifKyMDzTvDJEnz0LmDz5s/r8LllkOPEB9I0uZ1ArkEVJY0n41j3IRQZXdSkrMObTDD563DzHHu3XO+OMvnrUOl'
        b'Gp96yqWtO+/jst5T8R7OL6es09VeZ2nr+7Ajk6WVQj70epuuyClt5FqDrMxah+ogY0V+3zXYrcSXXIApzOfLLvhCIfelvk3aiooLdH5tLELXdRu3RmHoWSy/8ETNBR+c'
        b'4bFnWh/yPa08jjsuFV3YQqOyM1PCIRxn5qRwHOeLLsAtbOc2BjNaMMLVXcDyY8zXwNVdgPYoLjJy/VkSZJfKLtQG8mnHXNkFDazj3jeiafioXw1Y4FKOWdAvLPpy36Zj'
        b'j/+KigvY5sICiqE5mIvzScB7ubwpDxugls+f5VL4z0MNv7gREdasqMlQuYHT+p328RRhxAXu+ZtDI97FXj+SmcXRwn0CXR4UFsNg3J9UoMrAE/7HWPs8cyG04wg2cQUU'
        b'9mpKCezO6zCk8koLVOELFEEh1otYeQPf8CQpgUiJIBRG4owV+FbMxTigmK6SlgntJ3FMCcdUoRRnMugKEsTu2IMNfPmC/L1O7CHJEw14lz2VjpOZzJjRK8Y2beznn+yB'
        b'4o0rHi29mHFefivUpimryAiMxFJ4PRQW+RYhtw844UQmTqa7Qd55pfNQrpqWKRZo6ott8XYwF5aFRXgdmtLPZyoQqCfRYKo4JY9jNC17fGkBB87KSEdgNVf+AUe8MZ+9'
        b'AD2qkr3wD2lGi503+HNbxsVInOMHlXKWrJBb3iYYltrpAZ1885Zx7AjnnirGwaVjScNJWuFRscNuC24PLhHwIB3uQy83GhuLKLKMQE1GhMMb/PhWNXehFaY1dRRxOoMW'
        b'oySvTIK88lURTEDlUQ4aRNgDk3Snx465XmBXKo33hVC1AUr4C5rG29ju741V/liO+XTVdf5QziqPNgtxOgjmuVlc4DreloXmNWapTeB7h4xgIbSk47RqmrQ0ltGsvUIT'
        b'af9MFkMNtRu5yqZE7iy9vXwDGUvxk5irzRi5vOnudNELS7kQ4kD5dCgJlvRdCpf23CLL6rELHQRYS0SOXcJVqLY+z5pduRHp8DQnHPOREqhDqxjqIQ9qOao9rb5BsMcv'
        b'RSBQCzv9kWIqT8r/67SpQGndCPtQ9Lm9k4BvpSH4+wHJD0YHjaX4icexJQIG6acs26uCLJqC/7jOy4TrgZVtCaOCbBjYyee5PMQ7cIeLxoNRD/qrnoCVPW+LPXZ0FAJB'
        b'vAAWBPFuUBn/tunLUunniNU8e/S5JL99yVrOavc+bnrz808qcuc2/ervtz5XNzbU7hBXCGTkt9mb2TfWDf3iNXk/399K92987SOh/l9T5UTPrbdTEKpvGcn5/hEp/78M'
        b'/ObDDz4Y+BlWDxw29xTq1f5s6x8D9cx6W8xen6vSKWrY9IXN/s6mWY2D//qe6XPZP/lR087jmQORbS9J/bdhQNt1Rf2G64qDB06+F/76O6k7F73O+UX9Q7lJEPraMfOM'
        b'ISlX6bRf+lm+9+lv3rmkdG7rDr3wSNe/Rb3ovu3GUfm+nYGd6m239253i40ROCb+wOUtzVf0HHo1f/tigv0fno0NyZvzyRzIcWgrKbHV+YVgneqZ7115rih6f81U34SV'
        b'reIPz0lpWXb8IPONzGdsy+7+ushG9uLQ5YkbvzSz3aPzykWv7DtOUSHGrmFqSeaalrPvvRby9kcDEwUT534yvG/u7Y/EZ+cVf/rJWEvpjZOHTDtqX3a/GzX4ds9c98dT'
        b'6z+8mqNd98/f/l578F9N+uqNz32+P3vjpx45MwqXAip/b+6wNa7b/8ax/9q/7l/vHH5+xvLDuX/JKvcmDjb+6P0PhyHw+RvlsyP6p1+I/MmlzyyGt/3V68TM6TumLfMy'
        b'gR+nuc5X/HpPl8Orm7QK/3h/ZP64ocP1f/u7xgx2fOjm2vArE+M4DYN/6KVn3em6YPHuF39z+av9uP+/bjfbjuwLjXz+g4CeC6p/XPy1/WHlGZGdzZzJ781/84ehP33o'
        b'9b3fb7LJkv33ld+s1/zkz5s+eeuvo5ljWXetfBRmkj5VyXijw/WPZg6fjH0Q8jubD0revJv9X5/6733mQpbOgf1g+9JQ7Mzfvnym70fv1lz6OPAtafkPfH4zuHjmp7IO'
        b'DYY2f1FsUb78j/pO31zh2MSXRYbbjC14T/MoLNhCKVSZrg4Z03AXwx1sgXnOHKOpyIr9lHptxH5J5Z1pzOffL4cOrMPig55LgW2+XHkedSwSw01oSOajBGfxNtxR1NZ6'
        b'0uATy9dUxaqz1lxVIKjBvuXwxg3QylmMdll7HoFmLiDv8Wi8SGjjC8x2YAHMczYjPwc+VJCG6uK+sziXaWrBuiUu14kVWUPFMb7L7SjkY4Upsb0ba5qNiKT0cys8HQD3'
        b'YNDj9Cm+uJykstwILvIGr2qidLOmPt5YLpON7QKpPULoT4IH3PxJaZGmlh407LJhyYxE2ipuWH3ocl+2RgUZS6IvB7GPezMAZ6HAE8u2Y9NS9VvRNi9rPguowfGcp6mM'
        b'Aq3wpicx5SzRdlzYn8G3fHqgslwKmJUBjohmhYCdgnh/2PCBS7zdzj+V97OFSeoLD4ZgNx/syQV67rZjoZ42cJ8DAnlduM0Ky1setpYllaFTGAh9ztxKTImQ3+ayPfAh'
        b'XOczkvaF80GSXc7YZpiEZWas0m6ZJZZ6mxGftxRjHXH0If7uixWNeS8c3N36yBGnbs1Nu4uOdobJWwRCI7zAtT6RN0CWu2+UCL0qbhKRF6dtue/SHXIlgi1WWvCCLXG8'
        b'Mc5fuBOKsEMi2mpBxbJsCzfUeEckXdyURLg1kJRkumrMA3KfMRRKRNtFEpYeybZQs4sHhLmtcG1ZuN2GvVxJpgo3DtiwRCV7hWhrDDWPSbbYFMmF5RpikxIbxBT7iIeW'
        b'cA+oYp44Be67cWu0CMF2VoIY+qMtfVmFxasik5PiDEMOFKEKyngphxdxzuOU8iFPHBVawXWhGXZKy0OLEXcUkWIs9ly+FjlSLOqwWURix4A2501iXQKzWLlFdYIkTyix'
        b'5BvY67mQ1I8zcJO/v9tG51jBave9hDAC2R1bsEMkR2z3Pgdt5wmcW3kGaY5tgmzsJqLC9ijE4e2X0yUlZPjytQLNbWKScAcO8bV6mgipF7gHoC7b0sIbS0lcp9mxUYqG'
        b'vBHFXcmJcLxhGrOOPeVrRkyZLkck0NkrdQCroJY7dUcc8n9UUDQPHq4qKnpbOgzy9nOnsSVJyJWeLPXEHi3uzBWhXIQdhtDCHXq0yWECZGg96UNP0Zn7iPTh+gHu1QtY'
        b't1MSAn3AbkUQNJQYLNW4vqmKE6oXzE1soJIjf/LYL4J7YVIc2LhdOk7XYG5sxKDGH3pjRSRutOGCsep/nvr1yLz7v9jueqWbOzwqapWb+wMmR307i7eNEtdwWoZrSrJU'
        b'iJqPE2blpnWFGiKV5UhiOZGIKzYtkkQQ00+PNVNREEsJV/5REctxI7FZFIS8kVqOK1otxdnWFbh6O6yktRq3BhWhikiDa7ay1FhlA1d9R4WLYlbhCl2rcU75NdycK45D'
        b'YpeX543ry1bvNH1mcF+2d6dtXG2r/8/Kisvy8zwamJuRm8xkeW7Ozr+FfipVlFSG/FZ2/jzB3y2+yqO64giMxW/ILTk0HyVORkrx0rZARrDC2nVMIOCTpHjzvrzEvC/k'
        b'DPzMvC8qUi/SKBIXacZoSoz7UsUy+YIr0tkyzNXqL7gszRn3pa5KrzDu+4vWMO4HpkoipVfb9jkrd7jESrvsiX26xXzpidV5VBkSg/OKIcwkdufI8OQ1jZERzK9gwPUS'
        b'YobDp3sRvouBnbks1pzVZGl5JgZcrhRnC11aB2/Z5pfE3BS09GTemry2cdvgcEpUtLW9QUR4GmeN5TecFp2aFp0ezY397TzM3AFKfBGPl01ay4lAw68dSywxUS8Z6JlN'
        b'/OtsuN/GYrt2g6DNPpks7W8TzuOE56N248dXOZlh0WZ1wFaFsTxJAL1QxbmncdTOdaV11M39WK6ZeyAW+/ob8aYu3kiajX3yJJq3xHBu5VMpUIfT2GK65KHemMCpvlUm'
        b'iqzBi12cXphSxjZFvsHLp6Jof+VUrr3Lb/8mFDRqZh6lT/c6+JvCXZZBxgTkYrzlz8ya3l4cIw16IuB2SYPn9XdxoDL2YpGQs6xpYz/044QQrkEB16war8N1PuW/1fgL'
        b'gZpIoDtqNRSRm/nLTF4Df63pYAD3tXL6ScGvSSA8uPdL8+ft/n2K/9qlkzf4vqGdIPy5SGAg2B526hlBpKSO533o1rOWwhGo4Pqbu8VnHqaPnUje5kqgQsXppQQ+LDb3'
        b'8MYaZqIlwdD9uGQjXD+L424eZh6SGpwzeEvZY782Z8M4ACOwwmSLQ+5fE3q3L9tYyJnrTsilrijcb3KeVefj6vbLwzBv2Sy9uumR9VLzIFddAMuzM/cyEW+IDnFFwF8w'
        b'PHzMXGy0/Cqd80P5K5txnjulyK18sl6+TJjZT9YdkVg7DibwZxiSGSSYZC0+nW7qa8iqXFpuK8pZvo2luTN1JIWpFgYFRqkCQZYgC3s1uI+v2EMPiXl0ItdI1BNkpwfx'
        b'5pGZRJwylT2ew6UlQgX0ce2wM7A5B8tI+9JlhpB46WjOKiUP1ZZMqmVtNWUEUjbiICFpWI1wn7dD1rtv9bTAwaRHFQI5C2fcZr6Y6gS24NCjGrDJcqwK7BzOxx+bbxel'
        b'txETjBv50qnSKV1rt1Lhjl998fabX/w5WjPtRrPJ3sPO7kdltY5F3d2jlG5bE2HZ8+vR8mG5087O7//T9Eu5qwp7/5z269mqz/ZXn3V/w3y7lu1v//WPZytdgnb9V1Dt'
        b'aK7FztfVVd6+aj4lFaLam2tsLS/eBLVjzVnbttz3ej/3t6G9F4f/3d324s971F09rnyydVf39QyVdfs0/yRWmy+4+Km67q3Z3C2z//7TMT/7wPCB8a6417qbB3J/+upb'
        b'TXFdXQ7aiS982PqW31hX4R+VMz44uXez+dTAvub+f7lmeqZfMHzzZ15NQzquH+n9cXjqo/0tjs7z/5itsx/8y770T8d+59d/qufkydY3zV766NybaXs//yy+V+dTv+KG'
        b'72nLaJo2ffzDD868cPYFg39lvF5tmhD/z7iM2w7Zw+9HiB3e7/N7s0khfv+hV89663yQ+4KJ+XPxrvkGnsOzm/Y8+PfOXQePfH+y+0dfupQdDBp7u/CM7Oc2Y7+vb//o'
        b'1z/968Fffv78iXULpX6zZ8ZeyPzhzGRH360dHzyn9dotu6PnPt985u7tFuWXJ5RbrTb+su89q08GfvJlzqeh/xIJQhuMdv7OWJvXvqq2YcFyWIkmTJN+GuLH5zLexnxs'
        b'e6SgBuXyuYjXt3AKxR7znTCdo/ikjUEfb0h6FQ47mS4XxoABLE8Ubd2HA5yeqbIRuvmKBVJSBEb1pMPKRPEFWt2hZykYJWk/y0GswTy+3VkZDkDzk2Giu+EaH89PQnw3'
        b'r6tOuhJ8LveRhCYfIUyoJHPb0oPK8yu7SGKLONJKBLVQLmm5E2P8qFGk2ybWjqcOrvEV7QsvQ4ekcw597X2Ca5xzzob70oM0KFNaD7cpIjTyG0WkenRc4o55R+pFrj4/'
        b'K87fBU2sQD/p0Xx8zj0YClqpsR/GviWlPUiP190cddmK+2GBdHYviUFG1UZ8GsdSuUwHDxrkFlO6ugh9WSQi0U9iFaYytNsWpjyOnebV5SZ1WlOZpImfzKbD+iIpGMYC'
        b'viroHAyeX6EgwrUNSzoizCvx4Y6zHlhKj9gTSSp5XEXEGT2+nGufgWwQr2k+piIWYg+3XOxeD5OPNZ2whNZHKqJTBA+BZTAMRcuaGjbqyjNNzQ3G/kMhXfN/UTN7TD1T'
        b'WhlNwOlnA4zKfzv9LFdgocRpSwqStpJyEs1Il2sDRJ+I6RsR+0mN07iW/mXNg1jjIFbJVIHTrZa0ODVOl1Li2gqxJCUVSYNKKa6VkAIX98T+ztZ7PF9gxX4kCpYMr9ps'
        b'XVZ3mI6xQqNS+58+X2OpFZOZLM/IqVVGTN1QWmr18O3UKlKsdq1UrL5q70vRWwpsIYqix5QqJpRyAukhARddLU1qFF/2X8QpVmKmWsUoLatRUl+pRrEqFM5rxa0uqVGP'
        b'av8vh6Fy0av/wzHX/DtLtXX499YogGlhcJgPf+GW8pSwHi5Em+la9Ki7v6+dza7dTLdJCs9gwRvpGSwT86lL4Iv6PAplebxEIf/9t07ykPPhYgOw5RxrObZmXKpG1JNy'
        b'JjbhkAvXXQAndYi6DwWsqObPOZUL8DYnZ9rBdWZhZm7l3XHLZarOGvJ+xGt4V6RrtrpZAOey3gFt8S8bviNMJ2FPsO5OjnnpmDLrNvNJaKva4ZcExbvVPJ8RaGkf3bol'
        b'yqhNxvZ57b/16hr/4s1Xcj7Y8wPfH5y+8+MbEfK/OPu8bX78a9t+9fzv/H71veeeybr5bl5Ux763z6slpb7jvXD3TMx8gtbEFeP64eFytV1f/P3nt89Emg5HfHblnaQE'
        b'y1dOXry2+G9B8rZtvzI9ZSzNG0XxQTJWY8PKWupRSny9reEs1vSARaTakj61nEKiGMibqWczcRA7o9YQHrAVb3LPHIRyHFhtyIahyzxbxNk9vIVQVpVYRDHU0BNLRvKh'
        b'nasyRf4jPrGCjKtkcpi2ipD7fBdCnivYsJRVwvcHXiLmjGRnb3yM4KyedTW5XU19VpDbb1eAm2gp977CaoLK0VIT+izrO9PSkq0raelXb41VoM2OT2U2l/+RkpVL1fT6'
        b'nwwrTYuMi78gKW0kKZi7qpjSGsTyMG/CSMzibB7xSamJ0cxqEx215amEVbKZxwv80Mdf11hFsCZpkvLhksiOHsX7vK9pzZAlTlA/jgsROnLxYiyIv37zC/7onDY/y7K0'
        b'g5957dnJyjG3zhvG0j/QiIyLeSsmMcIsPDkmLsKLy7uVFfS1yqWeTDWW4qXhZnzgJ0FwGITrHJKHnuAcEcKzOER0DiYDljxYnHqQv47H8Wta2KToCWWY9ySST+pwOb04'
        b'kZjFyek4hjdJeD2Exe68mcbd+7zkBU8YlIVRaID8r+3IphbOX+0STKVzWGr33bDUnuHocpnQZcvqYzOsTqQxXY2Ha9QJNV22/pIqIGhiqHXwu6BWnuD9VUmdX7dOVlBC'
        b'2scnwMXHWOTD/6/2NVX2HlX8CGd/6XCEhv3E4tM54zUnanE0gtsNfxTr/7dF629IsdNU6UcVRUl+m5yilMjAYGUJPTU1JZG+mraiglB7AyPEAuHOKxpCi2QNocFmvnvh'
        b'XMjKqrtLqc0CmBYJjAylL0DDhsy/iJg/FboUoA2qnVKwZZcaFOIMzq2ztYG8SByRcaCvq6BajrSyNry+WZnUrwK4A0NQc+QIdCpCNZQK9fAhzOBDZWhywEmogPFwmML+'
        b'AGWWHpmPI06O8BBG3eChKz11C0uzYAb6YcjiMnR5wbDjZVzAPlkchQH682Av9JAS2Bt73moHNu0m3OtIhna8gf04ji2XnaAMekmzG9NxPe/oqw1l2zDv8JUEayzHBZiJ'
        b'd8TCc64bNodvcHHwlA6xyrHwha4QfXPir1OOcB/7WEBTMinyVTTMtBtM2yeZ4C2rULypjL1ROKpJcs0d1gSH/sxhfdhhbD5mnQDlkXhPBtphGgtTYAyrsN2f1NXRi0ms'
        b'ucoVmMOGAKhaj53nTmE9dNuuw2E3mNsFN2nvVVChfgRG/CHf0JMWMI3NdjByBQePQ5MQe4k4XSdFtJX+vRUHd7EZOi9uEiuSKj+Jt63MsAun4+wUHHEKiiL1Ic81CW5E'
        b'sSgJb5g3jnRJ2eyCFfH4EFs8sC5EF+5dcmbVFOmaRp1koPG4cSCTK6AOChR2BuCELkmEnfTbjDcUQWswHUYdNJjhjN3+HU7btTRx/AR90JpjeMqUpMEBNU0swkqYCkin'
        b'T6tUFLbiIr0xgGMwQssZFWCDdfQ+bDoNLVYwr2Fpi7dVIryhIjZjP+b5YcMmKAu1kcNFmNXXhNlEWNSDwlgaYCiV1OnG3fokO209cdLJEmsIEmahNz2cgK4emwOU1p/O'
        b'Tt6Xg5P6ZzZCsw90rj+FI3RCDXhXjrYzSRDVjJ0H8aYcFB3FB7voIuth0J72OUQrnIH8YLqDW+YHCCBKL8G4jh6W0gnN4R2Vq2KcxxLX7TAOU5nlIlbLqhJ6oc3PGSoI'
        b'7pVgHifWXT5IF9x3FPI2QSs2mivtwWG6ojFoFx+F3sjwbcZQGScFZQa5ltBjl5kdp0qyXAl04l0Wv5waFgQL64Kh+SA0wxh0Q344tpqQfLkTZ/EBzIhhVB5r9XA6XDoV'
        b'22AyEAcCQy4ewJYr/okwiC10GAtGtBOCEryX7LmPRmnXhxa8diyYhq8OhgZbaISiCEK/ayJ7b6yGUXN6ZhzvwsCVU1c01YJzI/a4xmKretYedRY0S2z2DgHhAlzfS6hV'
        b'4rrZa3vWTgK4W0Dy/m4C9EEC0FksDsfqRJinbR3FOSiRxZ79WJ0DtzM9nePxniEWGWExLl62tciFwrPy/jCru4kVgMM+dTupFFwMw3ERVl7SDj+KN2BCAW5edYNGvKbv'
        b'ChUhkIcFUapwG+76+gdaRWrsXI/9zq4KWhoWu6T1rANZ2LQXFvvTFTfigC5JwkOQF469NnSXc3AdC8RY7QNVOGaArT5YGowDMCGlTgBYqgOdtA1GmgpCrdjhQjEOweTF'
        b'S+uhfBPNd4+g6u4lAoiibHU5QomJGKzF+5ettKCGzvAGXc8oka4puVgVD7y9HobxzskTOEiYV4Azm8/AgrcnLEKf/HaoTiei0AuF9tE4kYQlwbBgsYEZ7077woweAd0g'
        b'lvtBtaeH+umLOEXz9RIstJ8iTaiJ9jAC16xwUNPQf/s6X7hGBz4Vgj2JdHR3fWHcGGeloTFiO3TsgpLMVxklHoU62kWbnxPcYiBJ675vCpOZ9th6WorGvYM3ksPhznlF'
        b'ws2GvcfMoFctzBP698NNnKbTmscGPYKjh1BKWxuHEXcoPEUoW7AVF9z273fCRg/oilJTwAIC2R6CqBm4sQ2aDS4QDDeI9sN8lsDGwh1rzmWY0rVNEG7cw1J4wFeEg5aI'
        b'U2eSiYB0mmFLAh33HGsxVcpC66EL6rH29FEijIumOkEZZ87CHW9aYTdW4qQRIUfVga1Wl/CmljzcXwmvhCD1x9bTOqYuYr65fC5MJnM0s1Yli1TQ+9jr7GWTvSUSRn1y'
        b'LmuLz7pCmQ5ci6GNLdIAvUSc8m32s3b3sklQDn2hUKNMV9xvoAw1dtjkBncy6JFryHZyG9uZJwHyVEWYz6Lme9bJwowdPtDdScAwDg+s8KHWRexKXpclFZeIeXQLs1iI'
        b'tap0UN20vV6ch4ljdJud6lgasjGOYC0fxw5CNx35/GlD4k3DIZf0CXY7kpywMow4WIMx9F8kdLhpwUotO1sRlSshqCTOeXrPub1YZZSAd68cUsmmBeZDHkFyJ0zsNjCK'
        b'CocJojczSlpYgw8wXwmLXaDdKoDgATqyaAEleIsIcAHrH9dB4uytbOyU1dtOBz2H3S4hlvAQWxVcTGjThUQm7xDrbjkCE66xfnSZE3A9PYSutImY4m2Yy8ayC9B4RjYa'
        b'651iXC04tn7LM4N4TmEmUYVKeqbe0VUnGBug5RyUii7oQitBOJ0iQTi0n0yglS6Sar8jxcMFS5KVsSo6SHbjWby3gURdgi5LwuhOF3WcF2X+nIH2jOcORmuTORFjHkdM'
        b'cVp4dFMY3JHFJj8FIYyxYN4KwppGqMyAcQHR2+3rMG83HXGjfg4Oy8ID6I52NYLmwzCoSfygeT09XqGCrbJJ+gkENs2qhI2NVsb4MNDCDVqO52CtPtz02GRLrGBGgU7m'
        b'IZbJHoP+MIYt4cLU00wiaksm7X7uTBDRC0Z+h4gQkAySYgMtmgdN/TRwJASqwo7A9aPwQA3vuOaeomO5Y5ujCTf9vUKgfwdO5m48HEaEY4BuYzCJzmQQWk5lCbHexRru'
        b'B+zKUTmM16AFGvdHEm++Ttfcqcss2IXYLYZFdawO1FHbQKyvVAsqz3iFBxDqLlgfd0gkJK4JhhoLyPfSstTCu4kwdJCQrzgBanfi9cNCzJM+Bg+iDkGdSzxM7PeBOSg+'
        b'ZH/46NUN2ETQT2Sxh+YrEiQRA+jEMRm4Q2hQok3oMk5HdQtbrWABbq4nLG3dAXNXcPr8foLaRuJ0FVjveB47nYmi5EUdvwSFrimEAXeuQP2VdQRTU1FZ2B+ri41EAzuI'
        b'TJTuw/IgdRskgK/EblcSjQikewxsCfbHaR1t9FvXQdtLrmrEGY9sgAl/gsMZmMzaQ3i/gAOH8SYdXQExvdu2m5hYlgY3YwwMGSxildYBjh500lLzoD0e6iPUsy94YyvN'
        b'NEnjN0B1PK2on8SCfBFUZNLh31yfQ1tsIQ46SIwzPRg6LLAdu3V9lf2JV/QlaGNHNNa50x334txpaAujJQ7vh2HC5GJ7uIEM1RewPpCGKDobd4FxIbyWtB4nUonEjGPB'
        b'dpeTCjiqt9vl+EZ4oJdZSYAthIcuBNi0g2UpwhRnhUlYQVKEk50pzOyC0QuKhvayaSTFNrqcwOpDtBO440x3vEATT6TRGU0zKhS8FQqtMX93OLTRzKUwmprjpLTJExZw'
        b'JAJv0zPDREAacjdDnukJuvBZKTsihfVw38TmAA6eITmtDu9Hk4xZQWxsgDj0FBJhy881x1oNAtviQ2fgjgfW+x0k1loZfRCaAk1I5uiGOQearYIEkjswr0q43QYdatjv'
        b'BhW7L2G1ivfm2CSidtdkCUHacxRCYXSHwxEvXSdlgrEhqFMx3yhFR9amoGGPk5t3yold8PoWOsW8HQT3Pep6xOEraMx7pzH/DNQ6A9Gl/cQHiTSRhIAPQrEV2/edJ3JV'
        b'B33ETLpJ1h+lS4JWBeEx8xNQtiOZWHULDPli/knsPO0ApV5m3nRy+VByOEHP1/U4E2NKz1yF3ghjvB4JeZo5BthAHKvqFE6nEezUH8fBMCw23wUNImbF9MIiZwKvRSLt'
        b'92LPkGJSSeS7ZL0unfJkGNbswyK4nWJHp3/XCgr3E9R0Y9XuEK0YG3vfCOgOw9mU00Sb7+xTVdhhbau13tqYCPukEpZoHvExJH64uANaA2nUamUCrYdJUOp3gvDkwWm4'
        b'sxN6taJwLJkmbKGdtp0lTOg5Fb2OCFA13LOAEUU6z1JsiIWSzTB+JvWszgEYSKSH7kFTDJGIJnECrSrPnwB+0hpuOcGCIXHc+3gjVwsfChKxxRTr18ENTpDYAaWxDCiv'
        b'JXMwuUAweQkHo/FulhwLYNbMofO7tnMjybiT+rs0sEaNJMkgv2w3qMzdvCMnEwrDdY+FKvkRC+9ifyB/L1H+eqIk9JoTk5suqynD0CW62gd4+8QBRWKX07CoGoY92JRA'
        b'7LZPGvMysS4gGhZykumrlogzJMsMc+IDkPgwBwvxBPwTEbpYkLYZe4wILjoJdQYDkrHqsgHRhlYm7caxwrNnHZJ0FemNKqIb9XQYZd4hJCMNXPG/EhR3aauSD5LA2oU9'
        b'W4l0953ef0mFzrYMGOJWwmxy6n4NmFbNICy5lkYiRWWwj7X8dhyN8MHrUO9Pj0zDDVkcUI7G4uOsHyt9XJQKzaqkqtyA9ks4Hkqg2qWEo5ZKph5En5ri1VwSsvaTBtW5'
        b'kbB0hKhNmZ6RFB1n3S6SOCt1tKA22WDzUULXoY1435UIVzmpKJPEkR8ks4h5rD6/A3u3kYo7gDeuQLOROdG/WVmaLx97rV2jrS9tOR1DiH6NECI/k3ChWQGqd2PFOWts'
        b'8dpBuDChqZ4eQfRvHgdO4sAZwpzuLQSCrbYktsxYQxHOpiZDVwbp4cWkL+vs0iJ62XCACP3Evm207Mo4KCeZQRrvBhK7LCZIrdl/DqcC12OBFNTiSDTN20bQ1izYdtEp'
        b'9WS69jG64rGtJoQubVAVlQGt+y9B6TYskT6NZQnQ5EjPjsMkiZ0NWHKCOEUZCSatWl4qcNtjZ64vQegQDmeHJJKw2OC//6gtU88G7aHHOc3kNMwQVN3yhrGceK0YokFN'
        b'qgTgk+bYdfyyK9a4mBBQDOtsxWuWXgmBWLH/rLEMn8NZBvdzPd2lBULLSLgjIAXvZgAXt4Q3NsKIJ5/ps+sgyafOfvzn1VBh5GkqEggPboUBATZd1OM+TzgD/SxwX3jg'
        b'gi+LHn4IVXwuzpBWJotcFwqEHlDuIcAWd2d+oDz9M1hmRp+7+cGUANvVwjNdxUy4SZDi8gfKCSOaDyrRaY9cVdh8Sh7q9/mphmsSP6qyICDopPOpY6L6Trzh7uINhQn7'
        b'tY2JxMxgz/psYkod0O6u5nyKCHcltEaQqHeT1eXG2zbM3EJyX9Uli8zDMKDNpLsr0BMdjkWK0JEWTvhSA4v7IS/oONb50A3S94SFBUfpx27oExBpLQrUINGtxZIuqs3q'
        b'5HaCt2sbSREYMwmhcW8JfGnOgmgipSPEeGvohkm5ib8MhRbEVKsCoHIn6QjjBAcnSXKp2klndQ+q7UlDKsgI9YaHngTk3SxbkY5wXJ+0pXzSyIrtjS9DkTWJbQ+IPIwS'
        b'I7gDo1tIEL4LTXbRdhfEeEs2WhUb3c5Bvw3OppluxvtncfCk+zrol72cGe2dFkqUswq65ZnJABr11+M1OthBokLXiCr2nj5JY92k86wP0UogbL1PS6jcS1vtddqgEKSE'
        b'7ZFhnMrVLMZ8K1Jg8uhU7iHRz0UruCnG0RATXyssCCZq1rEPR3cSuvRZmwJLreiHyn0kCd2i/eSl6WRKEU+qTKc9dMPCkVMkRtZAqQm0y+JQPFa6Qd0BvBPIgttJaVmQ'
        b'XYdlYVsijQ/r4ZAc1IVBXRqhx4KxSib2R6alYS/rhHVFmZZbYnMimJTHe0SDq6wdiY6PH3a9rB4TBVNGyjCtgrfdCKOu2+I9S3dC6n4oRGbZKVEl1X0Srm2A1lAiAFB/'
        b'wO2kz6m0oJM6JAkVEw+/r2OHtWmW1kQhxi+IiTD0wJC5NixmxuGgLWkBlSaa2KzDSDgxuqJduYSeU3tJVCxhtihjnxhipDBjCS0ZBFNFMHMKipKJfXfDwBFC3HueuXAv'
        b'lLS9drrVex4OnPFlXkz85fapWNKkeuCWrY7eVVMSOid9mAKBVTEwh5276K9FXDDQhvrodLMMXZK0Bvfj7FllvKaM80JoP0uC9fzpzLsiLkM9n8jpY2YZop/D+w0Oql7A'
        b'IW2ZDRexI4qw41oEUeSxY6ew1ENL25lUlkVoSKPzLFTUkj4Z6uVHNKfSesMBa4KeehhZj727dT23OMJEDikDRcG6vuaRzrI02ezxE5yFZtx3M03TDDU2dCjzCrSJ8WQi'
        b'SJ3EUBbicDoTpo1hBMocTQk7erE1mX65dWEPNBNHI8peyaC1C8ZMYHhXCkn67Q44HnWKDrrQ+4QOEzORSHRPkJCEvXnC62v6hEJjrsTg2qX0sc+UiO4EdmmeYCktMzRc'
        b'y8E0LxKy22NJ7Mw/yAjrGFy7kkjSvd5BkhK61qsyw5YX9mVrHFaAgaQzRINv8jaA9EhCgspzO2hZ11nqylUiBvf1CRfaSMWFPu+zggQsOpRIVKf17KFY4gkT2BpNK6zO'
        b'IB6cT2+QOI5tkVEwknjMFid11ODhtpMEDI1a2ONswU7EBPt1ovF+PMENE/AHSHGYT8OFs9KOatiktxurfVOJqt3UxE4NUr5qcuhO82DxPNHhyQPQr+5rdMB6O3HeO1gX'
        b'Iocdril06C1GhpmbjOO1j7lqqOMdzdxMB2UoPCTyIZgfIAAsgd6rRAs6Mk+4QdkporTXTWFWK5owc57wYvpKUBJxyWSoEOMY/T5EAt798AtEb1udLgdjT4g5EaZmHDSG'
        b'uUNn4d7mHe5EF2rYBdMlPCTS1kT04Z46bWMBF68e86JBu/dCddI6V1+a+4EencfcYZh1JiJcFCq99UBGOoxnvkLAarrjALT5Y9myVhtEc5dDw57NTLEN8VMUwpQGFvvA'
        b'iIw53Dslow39SDRwci/BwIj9CVyAUot4e4LOKs5aMrDVnMgYs841qZtBAVE1As9CGCWlAB9e9DU3pssaxPn9ztCvD02q+hvo6G/CZBThatcBRwH0ryfCMrADmuwxbwsR'
        b'u3EYCsbbgdBiFcICat2hNSqEWMLICSaXdGJHSJqhtDjOEestsecSlljA+LYAzE/eBd0Jh4gtdNN++0hcbXUhcgP3vbDULIQYR4sJIfMN8y1Bcdhju+5kGj70IVCrJ9ZR'
        b'sEdLDm4nJMMo0a52mmHUR5aVC071JX29iqDlJnRn06aJWW3AXkuoyyR20uCTQLBECkuDmXIyFCgYOOA9+3hs9NBOgnnoz8QWe3jgnIYNdHa3cPTEJlgMENjhDWU5XBTT'
        b'Kgu918F9aWYR6bKH3lhtN6g/qrfBnpStUtoS3ttHZHyeAGKEMGCG9dg+TzrnkCYdelNEJMOamDgjIqnlotPOseeVWHft3gRfn/iYsySgjqvQEpqJ3Q4q4LgnlEVCwwlT'
        b'HSDF4jqWJyiF41AA3NI8GHYmB9s9vDfuxqpdOLYx7jRWWIuYwEoUqID059s473XpMu2+LEKNWFcHPtwktQPqNf2wMDLY9ewhbxfC7ptOWJduF4X3txItGmbhG6QRyoQS'
        b'YRhSDNHniAuj2bV0kI2Re2AMp7YaE9Y2YlcWIVsFjBqxrgrqssQdB1KD17HkuyhcOHae7qYcSTiolIdpjX0WRM3aszRzVQ1ZeQMiNQ/NsDjUmxTedtskmI45kHmUCTQl'
        b'dG0PVoE2abXTYpEO3sWqg6pp0K0lk2BIJLeN9jNG5LB+t9AjwJ2pTZE4G4kTyoRXU7T9DrN9Klipf3KjFMF4M/HvmyS8D2XTgdftCZAPhGEbbA4m8G4muv1AkWniMKgf'
        b'SCdO+jRUaGOBvwsTfTRZI/bQzdBjhfeOmiDJMx4b6ZDKtsJti82EnnWO0LKOTqclnZhOXzSMBesToDeL/PboQdd6e8iLgBJLEnqdiBhuDjTWIzJRHYf58jAWnZZLfCsf'
        b'JkNsiKVMRDMKXiabccwa+pVs6ZRvYZNuKJ3TfQ3sjF2Hw3JG2c6O53WgzRZGvC4TXPUQ4+vGpvU4neGB/Rok6dwiHjoXR4wgW+FwGl1jO6s3stUuA7r3Se3Gewe2w939'
        b'CtiagUNqMWd0oVdd7TzUrMObnrE00DWoNZO18qYrJUGDjmVWysA79aCtXwIObyXS0E9Y1Bq2FRddiHQ1QJu7sxNrP19KeElyNxGuaphWjMGivcScCUjLDsPoBnkh0YKZ'
        b'0NNE9HroSmZp1AL1dUF0weXQJQc34qDQHvvNifoXX70A1XankdnHOwUwcXafHlGUB1AYb0iY1qcLHeaE5k2EFKOkS7eGya/fi3M60BBg55nqSszzLtzFe1L0ynWYMNCy'
        b'J1WjC3qdYUBan5CpFRZ3rFvPOtmZYOVlrGRHU3IRxsWpO/fRp1WO0GkYhPeJS2K9+nbH7dhuB43RwQQ3xVifRlxp4dIpHNnjGAj5iRlEGGstBDbQG35JKyKCTj0xDueg'
        b'PAJGz5PwXEXiWzmd1pgD0dWC7fakDd7HojQHzxgnogPFWJpjToc7riQkyBtQYoIxXWRTVPqlKzC6CWZ96ZMuaPYi1fw2jKS64XAQxxYncc7x1H5oMCKWSYqvqxNOssDV'
        b'EcWo3STKNYYQcizKRpCwlrcVygwyhYRJ5xOwjuHRNQJnhkgLOGdKtLiRoHPaHid1SdYNxhqF+MMwuB1bDltClZi42x1l9oSTWjzpifM5sW5uJArkewTaG2BhdgrJ1wvY'
        b'50z3Pw635XHeRjaRuM6gEDv88cGOK5BHGl/dThdVRX+sj+LcaveYhT83B2rhATNkdcF9P9ohoUkvsxKRoNsDvW7a2JTlZ3jSkvZWhwOOeC0XK3BKnzhj8Wm4HUii1pS5'
        b'TFyKlS6MujF38RA9WG5FJ1uYSDiwoIp3zkABSQOjxFsqdmOlniztsUfeHIcvx5H8VxhxCW44EUuugDtiHNeVx5YTui66BDBDRtJqG3H2QCBUqhyUI7L5APNcSZQZZERt'
        b'Lw4LiHnX4a1dKtHHoOCUp5FdRoICLqgFZRsShSepfH/SMbiVijVW/qRKMyF0wj7uMsFHiSGMqjt4Eg536MADBZgOzko0wbs7iGrNEL0rOIsPLilg4VF/wosC0kruEs2p'
        b'Io1lCx12wyZsU1IQx+hg2cmE+DOh1tjsqSI8qhSpTW/egyoZqFbXIYyrgZkEJXdTS5zexOyexLnzYH4DzDC3XZ/+RtL5bkYccCLhvX0PnUYHDG80T4Yqr22EFxWk+qRn'
        b'QtMeuoVCd5xyVCTxfY4Eg9aj2TrYqXRVmvZQ7QLNmvKXCeWq6bcqWDRNDsuC9i0soV7DzhemdKFVzdZJ6SJe98AC/VBZ7AuA6jhoh0ECowq/EGYnxb5MZueim58j4jtK'
        b'bCIfuy2w+GroFuLTJAGdoGfbfGgz14NwOtuCxDLoIYSpIVZdrBgSkXmSUPI2MHbCAtRtaG+LV6B2E1ZHk8g9dZ7g5d5FXQKrwStYlAslRMhJ9LgeTPTpxpHMN0lOOhhF'
        b'nGEJCw4yg9StIOLCRMESDhj4qW7HSsKAoO059HXr+thIeV3sXm+3na53EYdjYUjWLQxZRlIl9ohscFqPVcG3TVCkDRXgnQxgvt9rJx2hWgrqdYmUz1/EJk/oFLPSQPAg'
        b'mnjN3atEGW8RMtXSVVQpbMIuD6Kkg3TyN7H6Mi7CnKMWltjAnDl2bvfGskTm4HJnFqqoY3Q2BTuJppQoSeFA9AaC+8ksA8Lx+7t9UwjgujWtaG3Vu7SxfttmY2zZeZQE'
        b'BsKNwwQLC1pxOKWEzfu2YI8yqY0FpyH/MN4/CIPyl4i21JD0U0ekuUtAIP9ABtr03aBBkZSDnl2q0OG8G5qsWZkC3YB1eHfbHhkZLD5+GEsU8frhY6QSz1mQgFVkj2Oq'
        b'qThlqeRpBZ3WWOPscJAOZQKapQjru4nWF2aHGajBXTO6z3oSs64ZEKzfE5JYlnthNwFbjR+rrclg4n4oke/FczuJHLRiUQqdWi8jA1O7SPSoiYmDLjuCZmZ3r8FSHZyw'
        b'IY2mKhaKZaAzzgDuSsHIfgecZso55h0n6jXpdZG4+UNrGZKpu+CmEeab0cGMaEPnFWhQJ6As3spcyNKXZWxiA2jkWkcVrCfBQeYik4DyNfcmk6pHsvx1ohBV0KuJTUd0'
        b'LrGICn86uWZ4cPbCDhgwh3kX6DKWhqYtJF21BEP/OVJ27kGXeSjJP8S0bRxS9sADD8Pz2LkDGj2g13TXUZyQJo7S4L6FNNo2HN9N/K2fIUiTv8YRa5KvBy1wMXA7EbYG'
        b'vzCV0CsBG0IIcIoxb68XzdG4zWnzwSsCbx2SL4vPYT/2HDIW8RlY5Qx3ueI1uLhbmi9eowGFnOXIyS8BJrelW6UtVV0riDEW8zalWq+LnsykZKceJaAVkYLAVUQKJ+gv'
        b'82Q1HIS7iI/2Cei0xqX4YloV0GzI8p6kBEICJyhi7+VhJTcejOrF8sYxfHhCQGhXdo4WyBWAWCAiUubJisVaEX7epC9PwBhn8ToDsyRYlnnRa/ZYdkaAtw568aubUDgv'
        b'sajR1mmxWVKS0YREz+5imTG94ktUt0uAnanwkC/j0x5NiFvmzSxrdHTlApZaD4388m554QPeFqdtxoxus+HGQolxjQBu0tODBjQ9u0OAxd6G3GiaULZuyRpHSkWlAFtI'
        b'jGwxFrpwTYa4RLTbumJBI5dDGWZ2NkFOYCzmPt67TyTQPc4i2cOUDNQV+AI+b0iJBHLbuPptif+0sxOwYDIXbjQuay3eJstNlP4sES1924grNUG+es5aBbEX33w/LDLR'
        b'4K8Rz/z1NzlFWtW6GluvZfxOa3v3dkc1+W6jsoyLf6ntc+z48tXWjSNeLx6Oip/671//5U1764l/vf75H19synBIFH+/4LPPXsspavIbMj/zyboEKccfv3745Vcfmgb+'
        b'teC3Cm93H4p6/ZX35kYftp5ZX/zG91W39VnoKf3+n63/NNXc/atPf66ZuX7f3wxnNxql13Udaw9IbrL+6wsOqp+ud1T90/r9t9wa9P/gHXDnzxa/tfntVO1x+x+cuuvy'
        b'4zM/v3e04rPuF/36j26s8zjeDg4VUk0fRCxucn9179C5jEWh8auBdr1+hvsCfhb3uxsyrcde8BBPCZpf9jL/1/H77gPi6trjHzg7Oiu+/8B8x87PlN4/Mfnm0Zf/8NEb'
        b'9eccBh9oRo2csvIz/kXUhJ/pNqvvO/qPbz813jLivM/BLfO13qTZwokPXqya6HZ/o/vN2AmrF/cq/nzyxR/JvPDHy+YOPz06/qNtL5z8pO7Ux3+RCZruPv39xgk9p4zP'
        b'/j5892PXhXivX5cp5axfuOCV7q0Rbvv9uh999kag4+Chj+1qDnS//H5P1cUal83/sO95y+bN4t9MdfzF1vMHLx049utnZ3uD9uQ03ooUhFSHGEac8lIz6cB/d/0lU/c5'
        b'tde33Fb+4t0k97zPf1X2+RdRo9s/Gx86t/9a+M3KzT/NUXUru1j0MN188/eNvn9pzni+6sSF7O6gna81hcfqa365yeTT+mzpxRfdvcaG/3sw/sVKz3dqMxfN/nwzdvfz'
        b'V+Gtls9fGpbpaf/QPDu2aeQZR+3GWOd35f/xseGLvzj5ZaHCf1cafJaqqdjs637Sxn5HwVGz8z+stv39ifD1psHf2/Dq2LUfW5Z8oTY9Wr7xowjVLx7sn7V9qeuXuamj'
        b'w7/558O9w786/4OZv97LWrew++8juc1+BTN66Wf/qXC54l0tp5c8HF/anNU79e7Rknffq3o3IOds/aWzTn++/FLWS8E+zhv73yta/NN/Be18/gfGClxFDWzYSTS4zIvR'
        b'GCjOEWDFZQsuz0k/FBskEezriPWtiG9VgB4uXerCnp0XHNdqa8CS1TZDGfeQky3UKaYpyyuzRkmqaZlKxKlnxAL9w+rZUnJhOMRF08ridbfteHf5uYs4ffG8soxA96AY'
        b'hqNTM7hSfg+x+XT6BaXzmTijCqWXsBxuqsopK+Co6gVpgbGKFA4FYksGq7rmBLUhj5589BiULw3sLWWDhTJAXG2KC/Y95YstisuDacCcHPaJLAOxLYMVoxQmbkyHcrnz'
        b'tLZ04nwla4yHU+ddZeCh4pkMI3aolSSt5T1eNYXF+K0om4KNW5/saGP9fxtf+n/+l7E+R2f///IX36s8NDQxJTwqNJQLuO6lvwSmIpFIuEdowGWYaYjkxFJCObGMiP6I'
        b'VaQ1NDTk1TapyarJaChoaUqJtNx1t9rkCvaIhA4s9FpKit41yBWYbdh5hP0eaiOU44OyI/fwPwXt53+X1Q3Z4KwmVhFrqFnkCra78J96ioxFJiJT+ttUZjf3E/dHSZrl'
        b's21Y8X+axXLYsjjtR2w7j4K3rf7vr/r/DMSE/GFwYdTsiFi3wXQVdq2/TF3ZBIpRJuhSJEWljMTeW6znF5TALVl46CZQWS/eqAuT8e/k3hKn6wsFgi89I/aWu/qIndWO'
        b'Dhq65ji+s0tF90alm+iG/Fb9fOnRzc9eT7Y0SzF7VuX9ueTw5Oec7aScfnzn5Hxo9jqT41Xdqtl95cEnQ6+/kzk/ZuoZ63ks8FSR/+GGfYWb3m2e/mvdSw8VXvPfohPz'
        b'alVV6euB8vt+nPzDqvAyTbT5byXrjxMejHel7Qz89C1L3wuBtw7XXGn7Ql/u5I9PNH0stj+2Q9H51p7bz2yym9R/eLQsxTmzqewNp1d+nT1w5fW/3/7+K4uv/L/iri42'
        b'iioKz+7M/nXbLZSKWomiJaTLdltK5ae2lEppabvdLj8ihBTG7e5sd2R/hpld25JCCkG0LeWnaATUBGiCC6RakCoS6cO9Ud58bi4+AA+GRN80QXgwnnNnC8Y3jYnZ5Ove'
        b'vTN3Z+49s+ec6XzfOXV+0aWa3phvfMH0d5M/kQ/uLP6tZqjJ5W6efS5c6Ki6OPu9p+H32ZahtYdnb1s88+85b79/8q702Rpat6X73LuB7ntlyeiDu/a6gh/vex4+uPBw'
        b'xZX7yx4Vzu6+U1w684fV+8uuvl8Pel/iskWB7fswLg2FuM6Do5sOCW5yzUpztfM4Q7eenK0LhPz0KriTHBkKhVCLaj79VoQ8Z9LOHUU1JEWHzOVAZj7exnEsahc8JeKL'
        b'eOODM6yLvAdQmTToEGDlJuyS1Uluvsl93Vs6pFKj1fZmekWwbBXoRDM5ZhK6Tj7b4qPHKpDOe9QiuKqspWScnC2nx01i9BA93Go6ORud2C1IXRZIiiZMsaay4jg+Qe83'
        b'u0luQPDQEbELsqwx08EOe8s5FZzknKaamX2JqXZ3oYBeNkcNQtCO8mredkkooadETDrIiMlpvgRZ03Sgo7JrZa0FHOW4tarNTqfspoLYezBZucCKWtgX8v/pQF5D7GWx'
        b'vnwD51YvnUcPYn87uUpmgma3h34u1pBvGjgFRsnuoqNYYe64OEgPC9JmC94HMOkx9MROFBGmY8FK4cASQaqxQH77VZzPstZHT/v8dKzTUpwUpKSF3CgB77sY9xojH2/1'
        b'oVZcJ34fnSSXg3D+kvDCfokc2tXEj7zYS87DKqFaRhCmnN6EHMHttUImfZWc5vOaIufIl8bTTcjMDqGg3UqmBvo4yzr+juGm14rptEGG6dcavb4X4osi1MAbJjfKJQe5'
        b'OMhnYGUU8n0uc4JjCaoHjO6sFR82oaPm4p+hOcga84LHw2RqTvB4P1dAqwk3BshkBSzwCJgcVzWs7A61k7HqLr/XLmxscQyCX/+UL9Yr+FvhplP0jECvo1D2SQHM8ot+'
        b'3hmoX48PRnNuOjmy0TZowf/vgZWg7T9PP6zHXj+KY+/Vl+RjqbKsRI4s7DCV0WbIkXqY8hEUFey0Cq6l1gGNjNauM+3kRIh+4uvwVwb9VRZySRcKnxELaO5tftnsJ5dD'
        b'AViSQJULznUYrr/jcOgLakX4/nH6ER++qbHN11a5DJmZRy19bsFNTyBD49ZevtyQok3QW74OW4gOC5aAQE9nyeRcLZ2K//9H/T9yDQv/h/jiaRFkDX2Qx8mp607+KuUC'
        b'Zc48fxI5WyhMhuJgJXm5MNhSTP1z/tfca7lJieJBwjImJpSUvgm8GbNlslpCYVJCNTJMiqoRwLSmpJhoZHRm6xnIKAaTetLpBBPVVIbZYhAiwR89nOpVmE1NadkMEyNx'
        b'nYlpPcrsMTWRUaCRDGtM3KdqzBY2IqrKxLjSD5vA8AWqgTVsw6mIwuxatiehRlhhi8lEDIb3wM6Fmq5kMmpsQO5PJpizMx3Z06rCQbp6alcpKRSFYkWqkZYzalKBgZIa'
        b'k1o3bWhlRVpYNxQZupCFzeYn09G61WaFDDmq9qoZ5ghHIpBmGKyIn5icSUPEl+pl4o5gJ3MbcTWWkRVdT+usKJuKxMNqSonKSn+EuWTZUGCqZJl5Umk53RPLGhFelIi5'
        b'5hpwOtkUqkI9Db/M+a7QWzBA60DYiBBC2IIQRGhCaENYhbASoQuhHmEFwlqENQivI7yGsBqhGaEdoRqhBqERoRMBNcv0NxDWI9QiNCAEEFoRNiDUIWxCeBVhOW8iSW4z'
        b'vtuGsO4J5Q8NyfUklHq08y+hFO977IyBpSiReBWbJ8v59/nI+nFZvr1YC0f2oCQYMlGxT4l2eZ2cvMccshxOJGTZNFlO7/sZP7eb9UP1H/CT7XMx799qSjNnA6x7NqE0'
        b'YsvAWrWSFWKDf3/pbCvlOn9/ArsF5WY='
    ))))
