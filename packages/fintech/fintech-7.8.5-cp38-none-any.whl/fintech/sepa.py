
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
        b'eJy0vQlgE8fVOD67Om3LsjG2Mbe4LVuSzU3AEMxp+cYHEAeQZK9sC3yhg9MQwA7CGGPuOxwJEO7L3JCkmUmTfG2+Hmm/70uUtmnaJk2aNE2b9AhNm/+b2ZUs+QLS3x/j'
        b'8c7s7sybmTfvmjdvf4s6/JPB73T4daVBIqASVIFKOIET+EZUwttlx+WC7ATnHC7I7YoGtEzpMj3N25WCooHbxNlVdr6B45CgLERhjXrVg6XhhbPz03XVtYKnyq6rLde5'
        b'K+26/NXuytoa3RxHjdteVqmrs5Uts1XYTeHhRZUOl/9ZwV7uqLG7dOWemjK3o7bGpbPVCLqyKpvLBaXuWt3KWucy3UqHu1JHmzCFl40K6kMS/CbCbwTtx3pIvMjLeXmv'
        b'zCv3KrxKr8qr9oZ5w70RXo030qv1Rnmjvb28Md7e3lhvnDfe28eb4O3r7eft7x3gHegd5B3s1XmHeId6h3mHe0d4R3pHlSeyEVGvS9wib0Dr9GvC6xMb0AL0PF+I6vUN'
        b'iEPrE9frF8L4wUhU6GW5ZcFDzMHvGPjtTcGTs2EuRPqo3Co1XP95tAzJFw2DK2vVj7Va5BkJl/iEhtwlzaQpL3se2UJa8vTheC9pMRfnG5Vo1Gw5eQU/j+/rZZ7+8DA5'
        b'UoJ3ZJkNZiNpIttyFEiLX+hHtspyE+d64uB+KXm2nN5WILmcSyD78bF4fMkzmL55lJxamMzeIjdX5phJi94sRzFktwzfXYX36HlW/1p8aFXWmLFmfA+fIC1ZZHseVBU1'
        b'RDZl5Ryx/Z1TVrP7l/Alc454W0suyUabjFINeF/SEBe9RRvaxqFwS56Zx1fws3iXh/a8BDp3I4Jci8odTW64cBO5VUeuL8fNUZEIDRgmV00gzXrO04cOn3Yoac7OJNtk'
        b'SEZe5sjVpfgw3vYk3NXD3WJ8sCgLX0yEkdiaRbbhpjwKDT5HNuKWlFyjXonmzlbVjyHX4fkEeH41uUd2kjaAasHE7DwFUtRz5CRUIt3G93EbPp+caTTkGE0c0uBjyjhZ'
        b'eMUAuM36fc8Wl5xhSCJN2bRTEYsA8B08uTQUXyrjOqywsf7p30OxMxQ30X+Knd5Er96b5E32GrxGr8mb4k31jvaOKR8r4Sy3JQxwlgec5QI4yzOc5dbzEs42dsRZCnT/'
        b'TjhrEXF24Vwl0qD89XKd1VC8mEOs8N54HsnRP5bKkdXw55w0sTBdr0bRSFceabVqmkdni4V8tAKp0RdL5NOtmj16GTqLqsKh+FZhgvyrGDT9i96rufcSlGFPrH8VVYXB'
        b'DZPjAHdFhXSpT/Sd8IsxP17fIBY7hv8lak8Ul/iFLibh3ws/EH6OfMiTDDdswwph7TSnzEtMJFtTMgAZ8NmixMwc0mowmY2ZqswcDtVEhU0ltyo9s+D5VHwEv+hyO1cs'
        b'97jILXKFXCfXyE1yldwgbVFqfHWmJlwbFhmBW/EWvG1M6rgxE0aPH4tv4StyhF9+OoxcxJuQJxMqqhxDjmRlZ+aac7JIK6zbbWQr4HwTaQFgEg1JJr0xGV/GZ/CFAnj7'
        b'GqzE05MA//aSHWQf2U32LECoT2pkDGnDu0MQiA6/Cn7ZAhjnJ2+ycpk0wfwWmM51MphgPjDBMjbB/HqZNMHlXREleacJluc66cw7/nI0mXc9AVenMvpm2RZ97yevXtlx'
        b'dd8QxZvnbAu/dzv6zeTEp793fceJfScaHJxLVRZJZpw2xO/ISJVVRKDMrZGTcqfpFe5+8P6UaUA2TuNNMCFbYUxg3cqf4PBVfGg8u40PwNI/k2yKWgrD1WTgkBJv543k'
        b'DN7t7gu3p8Hw3Us2ktv4aGKGkYe7h3gj9uLr7nj68nE13ppsnFJEWrJHK5CyhCMX6/q66dItJM+TF0lzBr4I6LYO78BbuDkYplTP+fhEvV7mpD0OSnhIHsSllTtr19hr'
        b'dOUirzK57HW2aT6ZxyHQ+y4lHbeZ4VwM51T6X9LLfWE1tmq7C/ia3Se3OStcPpXF4vTUWCy+CIulrMpuq/HUWSx6vr05uKbrwEkn1amgCa1vFqNvtI2Xo3klx3PhLPXE'
        b'0CWjzU0mLerUbA7x+AA3c45uThnfBYqw2ZxAUYRnSCIvlweQRPZQJOmSCoR3QpLeuYyvcJb+rmwFIrfwi4icRfhFDHPsiYU7g0rw1ix66wWyh9Mj4h2AD7BXyHN9FpA2'
        b'oLRkcwanQPgG2Uguszt4ixtvIM1wKw/majYieyPJBVYZ2bl6eQRwNbLDxvVCgE0nyWk2JvhMVnUy3Fht4OYhcjiT3GQ19YcFdijZpETAj57nnkbkRXzK7qE9SCBNgG27'
        b'5yE0BJ9Ga1COoZpV5AF820h2K8mZpxAyIMO6An2YCO5BLXluCk924nOQeRb+W8gtVhXxWvDNtXz9Irg8Bf9Ji8hriRefJRfwPSW5BDNM9sP/gkliBy9H4W0EbjQUwY1b'
        b'8L8f1EU7iL0r8Fl8T6abSAcI/q/EhxhcvSx9yT0Z2ZoN5S/Bf71SbOM6OUJewPeiyM01kDsO/9UVrKYSQPE28gKPj+LrVBqKwJsSxDG8D3Rte6FsOX4WoVFoFCyhrawf'
        b'+NZooHW7Vb3JIaCDKJXcWOOhS4vcW0gagSbtVyGyZwjCrciixfsZCyaNuTbS5iJtKzjkWMaTM9xwcg17Gd0IIVt8MIWhi70C1aPF0eu4em4LSJJOeT23k18up3jHlhJL'
        b'zvI+3pTq48rOcu0rk60RX3halcPlLqutrpu20L8cldCKGnmmweUEoKc7siQBhfH7DLIHtwH5bcqrx2dyyTY9vikbMwY3Z+Fd0IEIcgE4PLkbga9oyAHHV6O+4VxboJ7q'
        b'65+OaJmixeN/lxo9a+WoIa9FT1NUfCDXfzIj7JfqIfO4i4s3vvaRNvZvOU05E8fmHapYdXNz+hl58v8eufrBEePAPpY+r0WP+C/1z94YUmHavd1acXu8fd6Kn23u9feX'
        b'9m8Z/tKRlaPkkW/+/PzcE3PPl35/797XPReedM6rub0u799Llhx65tub6b/4q+rktVGFz64BAkqHew0+hp9PNunJVsNcYG5KfIEfSzb2YeSRXNAbydX5IKGQLebsXAVM'
        b'+FUe8Geem0760wlPkmYDCHVGhUWJlEv4YebJbir2PYnvrmMMkmwFcQwWxYVMBepf0XucjOyaSq6wqp8aCGJTgGavJLsY2R5EtnSinXp5R2LaYd4i7DVltYLdQqkpo6NU'
        b'wkUZck7OqTkesR+O/7dSpoaScCjT8tGcltNwCZwzOojOci5feE2txQVKQaXd5aQigJMSp84Q8U66fJy9AuSVVmMOkNc7McHklY5IwkJbO+bg5nyKPHLUD3q9Em/Eex9C'
        b'ahk3DiG1D+fHnUht1/w4TBS4drp6o+HwN3XJtCnrjWZRjJoan4F2QFnqCEefwQPdaI4oXAm9kA6hSalzzjiei5kgPrpifgQClFCnrphXMi4+ETGiMJcciB5LbuDrqdAc'
        b'3o1K8cHpjo0/b5W7gAyiI2m/+9T6B2tlebbtrfLEfR9vuHLw2lNbhYIDDX0nJ8SnGoSPhY+thjGya32nJPQZE384XShYWPmbgoSSg8PTDZtj50dnHaHiwR2lwD89oZAJ'
        b'BsO+iju697aeZxx6LNCd88nGxIxYfDXA2V/B990D4eYAvJO8mExOyk1mQ5LeBIIbaYJZ0smXGMlmPfdoeNerrNJetsxS5rQLDnet0yJxcYYCJQkM+7SQApb1DsIyWZlD'
        b'8KnKaj01bufqnpGMDqIzLoBktJanAy28GIJkVEPF+8kLSwHHMkARwtvzTCCQ7raD0EOaUjCsM2DtU/FhJTk98slO6kMA35j0xwHGtUt/HMO2nsX7yo7YRgEe0QnbhorY'
        b'tssRQ7Et8ZdR1gGDFSYJsZ6MYoiVv3aN1XB5lBUVsdJaTg4EGNW9nmnVfL40RUQ3PFBGcXnVoTBr9r7qOWKhY2kkohOfn2/Nbhk3ViyckBlLNffKSWZrmt71jFh4dvQA'
        b'NAmmO7vAmnYtIl8sPDZpCLVT6NY8Yx1wf6FBLNyTPQJlwOvymdYZn+iWioXrVHqUDyB9WmPlt4zxaydmIwKukaCaZx3aKzJdLBy7RAV6DNINNFqzGyY6xMJRdeFsrfTu'
        b'Z9XMHN5fLHwtexQCNmxtTLGWmuf0EwvjJiQhYOY6Z4J1xoqsdWLhoPS+wEhR/vBl1kXvz60XC1umhoEahDLa7NaqBtDwWSEH2v4AGCVPmrXqTpw0IIsq+yM6yco464Cf'
        b'Tp8uFn67fDBKA5DujrUOqFMWiIXJpcOoyDh9TZS1NG6w1KNVuniQYFD08eHWRf9IGSIWztemIBBUJoWNsZb+Y6ZMLMyeNQ5VwutfZFgLTPOlkY9PGgOYgBJGa6xOV73U'
        b'+jFHKrICOux1WYc6x0xB+uEeSllBvz731FgUD6R2NBoNMqCHUtlB5JBhrHydilo8xkzAx1lhAb7ceyyvmUj14LFR+ASTbnJwA94wVkmOgswDXR4XI0q6I3jcOJbrS4Cy'
        b'jUfj8T2/wLUHX8MXxirIHnIJ0AZNeHo5e5xsXEsOjZVV4bMITUQTZfgsKx4OrH2sCh8G4QxQaRK+slJ8uhkficVtqBhW7RPoidX4MCuO4EkrbpP3wXcQmowmuwFCCja+'
        b'a3G75MNA8EMz0IxKsyhK3cS3cauLt+BboAygmeQ2QEjHw4pvaEEmGUUF+Vkg195idUQUjHFx+BagyWw0G+9Ts0cVuNHgUkSTDQjNQXPwDoUI3AlQlLa7ZE9SpWUumjtY'
        b'EMXc0+RcpEsVS64AAqEMcqtILN5CXkgmbUhDgTYjs2Mkq9pO7hWQNvlaDIOaiTJnrhLFvJv4cDlp41X4AkJZKIvsU4mi5L7FMEZtShjbNkAJlI0PgtTNxrtJR+9w+AqI'
        b'gzkoZyp+0RNF+zO0hLQpBgF5yEW5xZmsTdN0sp+0yZTkLkJ5KC+smAHYL2wxaVPhF0E2y0f5IGccE0HZDHL5zgiEtwMxmYfmzSJ72UCRSyPJtgh52SpAF1SQYWA1m0Fd'
        b'3hjBu+jsFqJCz2IRts34OXI5QkmeI9D3IlRU7mRPJ659IoIjZ2HtF6NichrfF/G0qag8QkE2RcJCQPOn4ZusdBw+Q65GAMwvIiCaC7g1rHdzRqgjVGQbsIKFaOGSJ8Rp'
        b'uQEi5FncjKaXg1iEnnLHMiB0ePt43Cwn5/F5YCcget+bLsr5N4Cx7cTNMNbnKT94mryML1b949tvvy3MZKQyf5TZahB6lYqL6ykTsGhAnuYh1oLjruXI8T37Zc71Ntyp'
        b'UmurW6fkytKjZ52vUDZEJnz59MJpK34j27Gcq5lu3aFbG7NxxPD4uZUjr+3YvE0W/dmvNsqWa2b8bXiCataZ59cPLHrps2vGyMP/LG+8N39C4zOeGyWeNUdjwpdd/Nnh'
        b'q3NaPWn9v+p75b/i3/v22pAp296xt67TpmrPTvrNgUO9c5/47Tdlh2alvBsRcWvpgP2vn1r8yb9/86MR++vdmuTxx356rWTwuorspMVJ7/5s7fUzH3/6yvn6gje3njD9'
        b'840b66tfLk+aNnbq/PTm1MHj3j+96724V+aN/vTJb9BvLk6ecO8VkGgH0RHaho8tAckUX4nIpbazVlD7I/B5nlzCL5I7TLNfgq+qqWwAggFpLRZlg33T3TrKrQggPghr'
        b'oA7jTXhDjjGTWjZjyG0Z6F5HSRMzK4wl20kDiK/bssx0MZGL5KhyEt8X717MBOACvANvcuGLGbm4qdqYSA2gpFWGepEdMnwltkyv6FKykHclBgTJG1pJ3vCUWai8y4SN'
        b'KspsBQ0nB5EWBA5eEneDf7jvUPaNUikHsSIBaoyVaUGQiQbBmf51xvth0stAlPGU9STBcM4+fuDZewLyCy9HQwwQVPLE58aMCpJdciARLb16l0A2KPBuctT9ELGF2jxR'
        b'kNjCPb7Y0rWQrBLFltf1GhAwEsLC8q2Gm3krJLFlRy8q+n4vkou2GnYUpyFxTbfm5I8VxV58fBAqrcx0XIpTyV0z6Yo8UPipteR7V3ac2H224UTD2YOjnx19+ETG0Gf1'
        b'CW9mle625doq7bvkVxMKDqQblm8u2ax9vZ/y+OR9Vcf7/ciNfvxV5LG/L9BzTHUjZ8hzI5JnDja2267IBtzql197QKV+Iiq53E5PmdsDAqzFaS+3O0GREtFKQwfjGcSr'
        b'QUtiEmxC0LTLXfBwz/PeNzDv9MVNgXnfEDLv1GhNnidb8Wlp5uWL8PYUkz4px6Q3ZubgppTMnCxjJihOoHrinXhrONnYFzc9FA1CpdeHo0EnXclfcSgaKEWzFN5ENtVF'
        b'OMnZ1TKqISN8EO+vYahgz2cijy6174rkishSNMfxA80nCheIJahie9Gn1kVs0q82LOfKwn874/Whd7Snta+Xvx772q3TVfuGnor9yLpZq4x+8sDGsZFIuy1i1NUvQZeh'
        b'E423zokQyRU5bpIm+hy5IFK7q8DDXkwOUmTwdnxEVGaqnpbmrHtMSOigxITiQbiIB2FqLh7wwNkvGAvKHooF/QNYQF9sohVGMyxAX4fgAZ024LV3yd5Q7UVSXVIyyctV'
        b'7YiwGp8NI1vwS+TGQ9VmWQcL5cPV5i731rpCBTbh49YyCTshtfwfMf3iBZHjTu9Fdx8AC+YvS9lQahELXx/OMwhTy99QrHlGgRx1GyPlriwomVC26VPrZ9Y3SyvLL9g/'
        b'tp6xvVmeMuZj66HKhd+7vWMIkAbuzfJM2y7rxwL/9lu69ScWq2aqXOGFY1+YNHPUzCH5eUzzza+J9p4eBtjCEPT0tFx8PjvHAE1mVZBtHL62OIKpvSM1ySayAVgj2Z6S'
        b'l0Nacs34ghz1KZBPIE1rH1Xtjayxr3JbBI/dItjcIppEi2gSHc7FAo9Qw5xqOeeAALLIfXL6qC+sym4T4K3VDzGuUFCdgwLIQytqDUKeL0M036FQVqmi3JjuzOGmPH0O'
        b'bskzG8zJgCsjyDVFCT6O75TJguZUEYwqk0VUkbNNM4VXWa6U0EXGDNpyQBdZAF3kDF1k6+U96b3KTuiiENEldv1YyE9PUyGr8ye5ehEztg6hUtsBQ9R0q2bWrKnIUfNF'
        b'DecqhTtL39wycNvVyA2pGvn7KwpS0//3v7TX95w9PlP/x6TY8uYr+vnnfvZp3u/H/fnV4wdih7+xeMqUfpHT3nnntdl3fh33fX3SgpfP7/r96w1bXs/8x9TVW40NDec/'
        b'ePf/Jj5vNf9s+x+/5qYu7/sEf1UyAaYNHsnMdSqEj+JWHj/PFZNWcp4hU7EzX9zbHUjOy+UcPkaeJfvcbNPVS64syAJy88JgA7zekschNYi2uLE/xwwwpNVNTsONLSlU'
        b'ytq+Wp7D4VfI8Wh2Ex8h5/B+0pxDFQZ8qRhe4+bmkXs9iUbKbm91RFFNhb0DhvYTMbQvYCcvZ5JMOKfheV7Nx3wjVzoHB3BVQXEVEJSin09Z5nHXlgdTuS4XB+DwEHqt'
        b'C8VbWunBILz9JL6jWZDcn5KRlWdsR1pFEoz0YPy8nByegl/qntFNQpK8Q/d4UbniMZhdp4060FtQXCeUHSyi7MElP0R7FD4liraaxyetEFH23XE6NN3t5lGdtf7P/SUT'
        b'xI9Hq1F0/ZcyZLVWfT4mRizcmR2OYg3H6OuGn7pGi4X5ICINr7wCHbKmPSlIVHNa4QA0KTZLgfKt9Y0DJ4mF3wwfjyo1fwaaai0wxUqkVFasRJrU+zzSWTVbJ60XC/ch'
        b'PcpPw1CldeiWCK1YuM0xDdWroX+pVuc0U4RYOGztVLTKHclDQ2M+jpRMELcnTEHuSX/nAM6C8/0nioXvT+2LUqdPpz1a9II1SyxcstCAFqb+gMI5VJuuEgsjk6ORrkgn'
        b'hwHJbu6/XLJHGaejDeOm0FFyps+NFwsb5MAcViXKoEdV+zKLxEJTXiRKWNhAQaoaN+tpsfAHnv5o3KyveABp0dwEqXDSUIAt1aWCvo+Z8UyuWHhw7Tx0PPoD2lBmtN8i'
        b'VBxuR2/Kv6eEhkYmZCaJhX+oLkdvZf9OCa/P+UXlKrGwYnofZFhURgvT+lsrxMLNS6PQgFkODobOsN0SLhbeyV2LvqoHJIy2rvjbaKmhnNQxSJg+HhDHWvCT9ZKB7t1F'
        b'w9CsoghYBtYZqnorcsT99U+8awTgM64JK96ZU0BSNc9++M7Xy3+z63TjyPEDnn36q/B+C4XNfa/tW/DugcWtP1m0YXed9kcbq36hqfrdn742/+XwaxVLjL+ZufrD7xe9'
        b'9UKfJc/9WrPkxJVfo7F75FOPD0B7FZdW/1xR6LDJR1158D5ZeT/ur72OzMq5por57OcX4vRVhrrxVyecODz8c8OPo37tvD9sPPrwLcXNI5n/ejmzb21lq21lkzGuaPvE'
        b'xVfP3bbsfv1fJz+qHfz2+eNzFp48/372/Z0nG7b+wnYr49xLry3tdeTTDce3/8J4ZOwD76/n3n3D+cK0/05rfDnjjZbN1StmHRw5Oe1U2L07T5T/18Dlxyr//vsbb7S8'
        b's27q7ZGetOUrZn4UnvzM781LXvtm9kf73j3YvOrbkx8lvXlhBiq8OWMS+bb+oy81Dz5UrdjmOF8/SC8TRbubK8gliVv3N4fy6xMeRkezePJcliExA0QjIL9TyHOg565+'
        b'gtwQxcZjKbgpGd5O4pB8EGnwcKTJhpv0kQ8hpA9PeiDTwQZySoZLbTXLLJW1VQ5KVhktni/S4ifUMqDG8DucSQ3RnI5tyUQzCSKG18jDgUYDuRR/ZB3+ile/lw/QADUH'
        b'7RQoOWinQwN0HATU1XabM4h098BZOOewANWmVVwKoto/jw2m2gYoG4GvFIlUOxP0+ma8nbQOTCZbgGU2ZcMEGZRoKrmqJLfxcXK2k1qhkP66yiGxU1c4VMILEczmzoPW'
        b'wguyxrASmV0uyAVFI2rgShRwrZSulXCtkq5VcK2WrtV2OWUH5bwQJoQ3qqEkzAvyZkk4I/ganypdEJx2lyu3TBkEi1r6ZZSfbnFK7kIB96FytcRYlFvUwFhUwFiUAcai'
        b'YoxFuV7VHWOhHKuzMq3IZWbONHwH3yYH8c1CyAxBQ8hOckp0DXl9Xx+Zyw1XBYe5gVuv9sJn/js1Wv5t3r7GQu9rs2LTFT9K3DCr7MVB6f/YmnFJc7bwV8PXuqbcy+p9'
        b'+u4B9/snkrb9KXne4Nn3xgy6xf/mdp+qBN9Xn2VP2fzNe4sWTNz4df2xJvzF7FbNSFnkEc3lWZPGvvAl/t2RyLyDtwa/eWnw+N139OFsWRXjy/osQ98V/oVFVxXeStrY'
        b'1uWYDABW2rokN2v8HidtuUxgAtY9Ljmjkm2oStupgwYzoxHZPmMxyKj9yPlEs1gtucfjJnxiCrNJFU6qSMZN5IjJKGrzJ/lU/GI2k9sn4WsgLjXjVtKaZcStuFX1RCKK'
        b'iOeJdynZxJ4g5/Tk4sAU3JwHy520JOvxOTmKCpO58V18SvSE8ZLzBqjjlenwiAGflSOlmu+Lj+DnmNlrIWiNp3FzCohrJrNoeYkhp2T4TgHZiM/gZjeVwjl8iOyHh0z6'
        b'zBwjNxvvQRGkmSe38GlypbMgr35kktJOMlQWS419pcXCCMUgkVCsk0v7tvFsP436xyilnzVREmKbpPfExa/2ycqqXGzrDPRUh3u1T11XS7f2BbtP6XI77Xa3T+OpaTd/'
        b'9KSPKJ3UFdRJN5XFzTjqCeqk7oDOpADVoHtd3wRRjc39gqhGJyhDBDtO+qULwUWXYz1aKloluNyznE9tkfYK4VrusleVt/syiEOmTquyVZcKtmmRUMuXtMY10f72/Lce'
        b'qcFKaFDP+RQWOmJOY6CVQFPOFEi08KozFXXwxXhInWEW//h3W2/UY9XbKNarsoiz2W2t0V3WGiJLU89ZajQC4vkfmox41JHYyXIdlvf6yF2UbNTlHPzU+rH1LVD0NeW/'
        b'rvvmLXj4L/xr/16s5xhZ6UWOwQK/rmFrOLBAl5OLIk7zXa6XSIcryIrX7kX2DPzEr4nz40HIU6IfjMxporW0I35wA8bAIFLbTAyMnStGROwN6AttMGp33QRQefpPHwHo'
        b'a6HuaxaLL9xiEZ2x4VpjsSz32KrEO2zxwAp11tbZnYB5bJGxNde+0saxzlJ3N5vLVWavqvIv9Y7L9SxFNvExeIR1gZqX/05HhvIdtYLh07cxvTQc++GBqzNfl+29kCvb'
        b'rM80mpQoHO8jx5YCfX0GX+40zRHSX9c2LoiFcyWyPbI9UXui4TdyT5SDL+fhSvoR+BalYKAsPsgTNxrYK2XyYcCu5XYFMHlVIwKWHtbCA6NXCOEsH8HyKshrWD6S5dWQ'
        b'17J8FMuHQT6a5XuxfDjkY1i+N8tHQD6W5eNYXgP5eJbvw/KRAFk4rIAEoW+jukRLeyJQcaJfC8dg1oBo0l8YwESLKHh3IH3XHiUMgrdlJdGs51HC4BZeMEpmFJmgE4aw'
        b'vvWC54eytoaxtmIgP5zlR7B8b/HtPao96nLZHrkwskUmmJgQIvrV09HSeqPKw4REQc9qjIUaklgNyayGOEHGaE0KCDpljFw+GBWuC/onlYoO/yF39Eqf3AEyqk9OkbEr'
        b'3MstUwVNPl0vWv86pz65ksQURgdQmli/67W2XCuRFBWTn9RAUlQBkqJmJEW1Xg0kRcZIivyDrwGnQ8Cj/8w1DrfDVuVYQ08qVNp1NqkzDmBgtpoyetSh4yuT62xOW7WO'
        b'dmyybrYD3nKyV80z0nN1tU6dTTfG6PbUVdmhEnajvNZZrast71QR/WcX30+kLxt0M8wz9bSKxPSZM/OKc4ssucU5M2YXwI303CzLzLxZs/WmLqspgmaqbG43VLXSUVWl'
        b'K7XrymprVsCStwv0BAYFo6zWCcSkrrZGcNRUdFkL64HN466ttrkdZbaqqtUmXXqNWOxw6Zg1G+qD/uhWwJgJwMo6gyMND53xyQwueuU/T+IfXtBZgF11+7LElcX3pQyM'
        b'UWGecezoCRN06dn5Gem6MfoOtXbZJ7ElXWJtHT2aYqvqYgD9jUJ3pBbhqmuIH6UePzcW6/Lnvnt9IhcWaxOvv0NdnezunQ2pmlx2fGU1fpY0UZujwUTPfGQtIFuyyM3Z'
        b'7HAKtZ7h++Q8fp5ZIv7Jb0cDwv7Go1SraVxSKvJQ0xm5EI4bmfExn2yhsngKaYKrvEJaz/U+UE9xBt29zckx53AIBP/nw8jNKNLKasxbrkKaqlPU/mRoMw5ATCdMyk+l'
        b'28HJWdTfMXteRrsUvozsIrv0+CwqTFeR/QDueVbLh+U8kq/6CZAWq+Gb/nLRbDLDLEdqQ6EcTbdmvzNoJfJQPjwM3xkaXDfZQs+nFOLr+BgI6wUZZGu2Es0lp5TkqiZV'
        b'9LrY1L9yHrnlWq6gVlgKv5dcc6RuiOJdP4HbjbbkEa1TamaMjp79xt/ut37dqPvpjjih72cbJxT0ax6aEbv57XHLXe9rC6ZNvNBw6kPfuIrfud5Y0G/SP6pGRj3zy18O'
        b'P1C1PnLzHzZNXfbNSdd/v7vq+K2v1qz48/T3iwf/zvTxiYVlae9WlW3arL66PqVNH1P7cfkP/35l/37jird/qP7Xb3735HOLd5rvnPrJa189eONXV/82sql1+PhXfvhh'
        b'w+HFX3z/tVF3j73sHHT8+z/XGl55Y/jwWl2fK78bU9S2dNHEl8fX6N4auGrUncpF9t3Lfrj2vXeUT2x98l+y3+/OHLkkXx/DNBiyDZ/Cu/FF0hwBI6XP8RiTyNYUHsVh'
        b'r1zdh+xiRuuCeuoZEOIWUBxLLpEL+CbTo3DbstwsU2aOwTyawy2kVTwK1A9fl9eUDmNqWgI+OpntxZFX5NKm63ryIoNg2ZA80kh2Bjax/K/HkUYZuV09jbWwtphcxBfw'
        b'puROrofk7Bo3FVXJrkxyCmYc3k8m9IiRWFtKFnRoO96fIzoTzMVXVSAveskd1jEXaZwuGiUYPkTM4/E5uLndRPaL6t+uAfNxswgRbs2SIQU5xJG7mWS3qJs2kr24jYqe'
        b'9G0ZOUw24RMc3s4/wWonjfhuHn0dRjYHb8YHFfD+XZ4rgNaZpeoePhovKZ9nyelgBZRsneCmvBTeuomPUw2zRc9OhBnwGYWZjnEWW7fJuE1Bnq1KYLJw0TD6KFSXzQEw'
        b'x8hmspHDO6aRZnFnYbN7Otw15VBIb5Lj+C6HD5MX1zJQo2aRUxRSGCZ8s1jcu9BWyCbjvTWsp5H4ngtezjaTU/1FYU87UzYHbyRn2fQMB4W5mb5vwNvD0kU/XS0+I5uF'
        b'n8ON/i0y7X9sQOsox4OY7AA2Lym+GX4RfrSauZFqeDWzi8k5La/h4nlqIdNwojsz9cxQdvjh4YddfaNUgjIokmCTv4lcUXIOExWAJ2kyHfmV2w5yd7t68MjavF4lVhIX'
        b'Wjur0xSomEnmMyAZHKJc/HZksHLRCfTHUZwVFir+dKsZLvRrhu2t+LXlByOKArIS5WIgV/jZWKLTbhOMtTVVq/UmaEMm1JY9sh5MFXhLqaOsW5Ce9oP0YDgFACStHtt/'
        b'pIbL/YPBxNvuWl4SaDm5Z3HouwHgpKfmum3cFmjcFCxL/Sfth0vtL+UkCPQ8LDGbqKqK6NkdNELoUPQkZ31XUJx5gQXRHRQVAShSHkVC+88g0fcEydIAJMaHS3ePixwV'
        b'DDtFKLoDoDoAQGoRU1mg7WDbnU6aVl0VO+HdLQz/mdFHVDDlD57vJLbOpCqHS+fosFJddns1O1kOeg7TRDq9SE+bS+pXIag70LPZHmetLt+2utpe43bp0qEnnaXkROgu'
        b'dBpeXDHBNMaUqu9Zjqb/FKizEb5Iz7GDWC58HrclMzYnn86R/Un43CT8iuPb2T/h2SA1fjzkU+tbpRm2Nz9KLPjY+mbpZ5DjSz+KfT329JKPtK+v+vp9pa51yIGNYwei'
        b'106HjXvhS72c2YrxK9n4oMRIJTbKRVFGuhbfZdISfmEI3t2lrDRxBrmdopROIK2gxvagE9mH8Wl8uK5ePKB5Dfj+HnK3OouJLfwSLmUkfrYne5mKmqn854Qk76Zn0Ipw'
        b'Lp5aaSU+ID0j8knn+I61tRvH6E5WXQj/2qUNtfuG1gjyw3R48CF+S9R8gLzcI/stydhCkj/wdsKEQrtbNBl4qtwOUJglyu5xSRoyi6bgdtpqXLagqAilqztVROuYzIwn'
        b'k6058AxUBX9sFXan9SF6HP3X2S4qOcR4elPlLFEBylnNn/TDkYe6ys0OIwe7082CFbNBFQHVDJ8kux3mps1y5hgx6kvPp9ZMQFhDwSfWj61Lyz8T/mCV/1S/7V3D7KQR'
        b'Gv30Fb3zTzY8cXT0s815IuIm/THiwB8f6HkRcXdw44M0CC2541ci9ANESfaCaVmwHOsXYhOD5FhykhySnJ8etknqsrst/vlhXDrYpYr+cH5xb01fPz51eifX3xiTsCiS'
        b'9exixZ4wBRCZnndcE4LIW4KdrHpo+HGkH23oq91S/M2hLOdRkdfkPzJF9767d/hivjPMb4baGAO+Mw9z95Ixpin/ADSSzia6wEKrdToqHDU2N8DnELrjkjX2lRL9Hm0a'
        b'3YUhpHvrjyCaWFjX/S6b0JBJV2Bf7nE4pZER4KrMrRPspQ63q0uLE13mAIGrttovbzmAddqqXLWsArFqcXDL7U5X9/YoT5kI0cwZZmDKjuUeWh/IKYmUAeucfqigLbPb'
        b'Rlnyw6lFZ29Lda5nClwPiHwmK5fuuLPQC7nGeRkBJ9ECsiV7XoasQI/PmnVLSp3O9Y4lYWhGxSp8K6oaHxvvoazMQ+7jphArTeB98hJfANyE7C0GjrWXW05uqBfgGwOZ'
        b'NWVKDd351XAonbQicgbho8+QBg9VXYw5eL9L65mfQfdLi8kWw3zmBdCMzxZlGGgb28zZZCsHr5/Ur8L7hpPTRTw9KnMAdO1bmnyyIZ6Fk1iQiy8Hg1UnVUlO4gvm4vwF'
        b'xvkqlP+MEp/MFhzb/timcNXASxc2Fxvfund7H3UPnD3vGVzLzbFFJ2x4/Xkgrjb+7bSbG3Ku8i32rz/uV3rd888NV97+1eCqI18LbxqjFvObblfuGzfgVfnbhcuNxe7z'
        b'n/u++mDcXe+PM89/YXRtXX/5+DO/f/8j5R/axh868/SSp1/X7d00Rx8mksbt+PpKoM303IPBDIr3SwoUUcOTwyPJfTfdZunVi7RFJNHDE/TIw01yOWCFGYzb5OQyuU6a'
        b'mAq/Au8lt5PpeYwg5/Vksk20Nlwgp+dmBUxo8QvlSBMtiyObyXmmo2fJ8kNNPCbSyAg0fha3MMFgbdRkv9BQvYaKDSAnNNUyU0XvKvxSqO2FbMP3qf0F7ybnRFvJXuLF'
        b'F/z2B3wgU0aOcXjHEHKDyST4FNk+UbI/kHPkpIzchPodeJvkQfhIrjGUkLYTC//Z0aHtVL+3GhR4kfJrJPov5pQdyHFILbl+GBhtD1DDnpiBLOixdo6wGJImTto0Yxxh'
        b'A/o6tlueEALEY4j+oBEDVeuWE5wIcILRTBlrJ3k9aSCPoYBI+9NyeqqmWyhOBqCY0iWtm1k8s6Odvwt4qEtStdNe7lO6HBU1dsEXBlTa43SCrD+nTB4EKzV7a/xEcI7I'
        b'rdpjTCFvhOSgoynXSLxLvkUBvEsBvEse4F0Kxrvk6xVBvOtgj7xLjK0lSneMDQTrM91vMtE+iUzA/27gDEH3+wVsBMS32CswerTMRjU6k26mrYaqTTbpXulSYGdd8jG6'
        b'lQWspTBv0oTU0WwTi24wCVRLBY2q2+YDAz9ZN6fKVqFbWWmXtsigw7TP7U/4O9Vd8zW17i6acdqhIzWuybr0jmKzVerOIzDCzmpbeC7jO+vwidJQTki2SDS5OAOKCihj'
        b'y8XnacCbMTF4NxC2tizSlolGkJNacsiKL3uo13tewVNZJmNSJlDZ4AoCFWdkFidKkR9yOKB0NeTUQA05gzeNZML73yZm5P+I13HIas38UjsKeaiiRDbmkDudpfcacoUK'
        b'8MbMnMLgjZXmwjDySn8HC6+BXyL7e5Fm9ggzfZtBDbhCmWgyZavBWysZhsxsk9mYBOS3Wa9ZTvaT3ews0UzyMgll8LRDVHdIBEoOMrpBb8xUoDXJGvJiGAjt1/EtvYx5'
        b'o4XP17OmZYiLl0/jYOjOj/ZQjkfuAffejK/gfcliFTnUbesgvxbvkYsPnCavwABm5sBIRmTSseRQ71Eycng1Oe+4cO4dmYuee4l/9dcDf3QvkqRq5PkFlmZuzLPeN6M/'
        b'efu9lg3I2XvoxOijusxXP9sxwzduz6HkQXXe3UUbLo8qv/CPOebvfzH52sIlxf9dlHKi9Kb3t+99cu1w/GvaqYb3/+ebcaOG71+6andi0Z+zCrf9IOvM19qk4e/MUP3y'
        b'QWXKW4M+7nfjnfR9A565+YfWdX1TBu04+szew8mz51UDI6f8UY5fTse3yeYsxuH4Um402QcsnHqxk4tzzeRcXYCLd+Dg5lGMRT81BTfi8xMDsoAkB+D75KjIQu+Pw15y'
        b'PTrLnJME8hWP1LiZxxszyDEmSOgriTeUhY/vxTg42ddfcl3FO/F2seZ+I9nBA9xINjPgScuCBcm42USa8pg/rLKKHzpyKDt4KRtM9jCH2TwafWQXPki25hhgQlJkIHJt'
        b'6ctAzyR7qTMd2yHIMrvIbv8OwfS1IvPU/D+y6UdQxiiRD8bdTe3cfZySRYdQB3h7uPSrYcdnqPme/1e4Yk3vYCYr1SXxeKXIrSnZcAo0sYcy+rDH8+iVizXZA2KAEOCB'
        b'FZC82EEWeG9osCzQFZiPLAXoqZOb9FK3PPjNAA8eQpkGkFTGQgI8J9jsp5cz5yMefrk5+ngntao4qWnBSXU/6mMo1JZZLGz7wUmDkLFtCp+M2uan02wXOyE+ld96TI0+'
        b'TGH2RYaqs1RkCpKlKthb/n6xKev1/2jfqDuUc06FpC+dqc1woebl8ljxVO+3ch6J0/HtoAkMuf6tlH3Hv3JtuIaLCYecGFZHHs7Fxnd8JobTDRavPaJNpYxscWXnijI9'
        b'h8LJ1ZQ1PLP7NXbie+HSX9e/O/hXCXyJXJCVKByoRCnIS1TwqxYUJWGCsiRcUJVE7FHsUe+J3sOVy/ZEC+oWXsgDSSnCG10uY27R1HNIY48UIgQN86PStvAlWshHsXw0'
        b'y0dBvhfLx7B89B6tvZcYfgckMOrcE+XtVa4Wegux1BcKaozZo4V2o4W4FubCzZ7rVU69q/pIT/SGOqlfFXXUjoVnqJ9VP6F/o7okDmDjhAHCQLiOFwYJgxtRSR/mN4VK'
        b'EoShwjD421d6Y7gwAp7qJ4wURkFpf+YLhUoGCElCMvwd6FVCTQbBCM8M8iK4NgkpcD1YSBVGw30dKxsjjIWyIcI4YTyUDZVqniBMhNJhwiThCSgdLpVOFqZA6QgplyZM'
        b'hdxIKTdNeBJyo6TcdCEdcomshRnCTLjWs+tZwmy4TmLXc4S5cJ3sDYPrDMEM1wavGq4zhSy4Ngr5kjVGJuQIuY1hJSaBxe3Sz/Mp06uZQ9e5EIGJ0gDxhujTJYZuBVmQ'
        b'RtarcNqoEChKcGWrA25GHZx5Qj3EnFBBtd3tKNNRN0SbaA4tEwVRKKCyJdQpmlaqVutqa0RpsStpTs/7lJYVtiqP3Rdm8UPhk80uLsh9kFbpdtdNTklZuXKlyV5WarJ7'
        b'nLV1NviT4nLb3K4Umi9fBRJ0+5VRsDmqVptWVVfplT7ZzOx8nyyjeI5PZp5V4JNl5j/lk2UVLPDJiucunHOW9ynEhtX+dkMMYSF7IPWUDPOucEqK1/FbuHq+gRO4ZTLX'
        b'oHr+OHcCuZLcvMDX8/GIBuPdwtcDMq/jBFk9t0zpLKnnqPMivMUdl9EQvoKyLzyXgGLRRLSOq1HDfRW92oLoe/XIIodaFSeA8FuUgppNbtgHlq4Uko7+btI8t7u7dXyh'
        b'OzGfjYSoZNjEOlhJD9YsccgmM4+ywjzjuDGjJwajkQC6ibmcyvw6V529zFHusAuGLjUDh5vqEcAN/Z5trGW/kiiiLKgqTkeppxvdYjK9Pdkq2MttwGYCaGQFZcVRVklr'
        b'd4jjBMgotQMI1rlvn9A5fxDnqGGbUO29GTXCNcrHmXxc6ieUf3zyLfx7IDOlpubqVb7ojs3SjRNbVV2lzRc+n/ZkttNZ6/QpXHVVDrdzOeV0Ck8dLBOnEzGTApMgKII5'
        b'16EeD6AzJvyrgHARLgemEStZO3Q8lYnWRIkI8HhOAKJgwUDrVqb4a8AFwN9EwAPA2BFp2NStrrPrrDAlZcD1q0yzxL9Wq8lJtfTH8E1go9QtWP8IiDr9mR9C14jYqTne'
        b'31y01Bxdw0v5iICZQ8YmxKe2uSzM99Ontq+qq60BJbdbUP4ZAKWM+QV4qktBTYahkMZAV1dlK6Obrja3rspuc7l1Y/QmXbHLztC81OOochsdNTBmThhJwWqlWGoTlnrg'
        b'QfpAaC2dt2tDDydxLLRDIOJ24HASxyz3PW/dUuvH510Rm+I6Kp6JhMa+qqzSVlNh1zlZUamNbjXUiju08JRNV+esXeGgu6+lq2lhp8ro/m2dHXjGTDqo0LEZtpplzNju'
        b'cteC8MjIQs0jkQBp+ftBsjCQrHRsPWzJiwSGUqKAkR3GljrEdrF5R+Og292Vte38y6BzOYCWStXQ1+hGerBbbXd9lCqaTCOpT7ZKrLWLXcAejSKltbU0bq2uPNj64mFT'
        b'IXSYhi6J40q7E5bnCuCLtlLqEdCNHSZEtKTIJEcdTSraXOZkmU3OrE82ZpgNVOXNWkCNFGR7BlzmFSdmGsxGJao244sxavLKYPISi7anwBtwK6iRV8iNeYmZRhM1/Sfn'
        b'4hvk+QKyKddITvNo3FxFBdmz0COehu/Vx2XKAeVzpQefU8agKLxfZlKnsdZlE0BZDrJbJOYak7KMBf5qsxTkKLkMIqoa31sVw4Kk2pdUuxJXkRNSRHYFbuXIlYrVHmoe'
        b'n1dNLhTiFrKnmLSQvcU5XDnehtR5HLmuJDvmsD2NPnOGuBLJcwCPAsnwAQ5vICf7syPpvfEe3OiykyMZomkoC1+So14AK75ADpATYoTWg3iXB95vwpdZcCTFOo5cNIwv'
        b'crg2zVC43oAn4n45MK5lSs2MeZpZf/znh+kxBUNeemnH9oH5w/ol75yhMMe9GzluyWaj/QnDhg9//V5LWsX2G/2iJw+tHPvzr54bYJyirrwxo+nVQvebdTM55fk9AxV9'
        b'n1nxSssPIi+feXfysP/pe2b1tdkXdq84PGDcwP0fLDKfNn0YcXKML8I4YFjflXXvaCNyxmYUbrl+5I3WH7275M4Tzic//OGTF0/W/eJ29cbzL7UoP/jmDf39T3WfDxv4'
        b'fw0/i3lvZVTWOxPfvr186l9/WHbhSWv071X7p2Yfyxsz7sl1n/5K30s0+L9MLoCm0kzOpANGkGYVkhs5fFE3mN1NfcKTbCRbSVNKRjjeRFpkSDNHplThW6IDw2myk1wH'
        b'PNk3MwWe4pA8hcNt5M4wFkI1NmZE8iLcmJmTDTeGcPg5vOcpdoowkzRlZZnd5GJOUo4KKeW82kx2iZaRBnLLnTWVxvwGYOC1Phx+fuAENz1Egw+SU3mdLDfkKPZK1ht8'
        b'nTwrOmyeJBeHJZv0SYkiBuFj+CUURa7JVpPNuJWBANXEZY1G/sD++Bi5hVsYCJnrJifTk8YS8slzOXyFtOqZBWaeo4jaVswGE25KoQvKrEjCZ5FOJyc38akRbJeINE0n'
        b'd7LalxhuScmsxJfYMksi9xVk06I00Rt3C/QtS4yzRbbNJ7dIE4ciBJ4cJodcbrqQw+ePz8ozcrBsTiN+BZeOL9SwYV+FD+ND/oPR5MIi6QjnmUo2TuTSQnI/KycrK8dE'
        b'mgxZuCWPtJHNrKdJeLsCXya7yEVx6mFh4JukefX0XHzRoETyWRx+iZzDGx/DH/K7nIOME4mhJZT+835eKFmRnkFa6gAq2o+oo2gscwal5yVF25JWdB+VSqkLKTs1OUAS'
        b'd7psJNd/sIqdePwuDqCc+CqTInZB8m0H21FDyOHIHoGBuqgA2b3HDAvfwiJ/gVzABYVv4dmXNHr2mqkEqeB/u5IKZopsTTpvI4qBVHQBLkM5VUASk4QDKim4JOG+MxOS'
        b'NhI6SBcdZImuZYfOLK2os5xio7wwhHX7OWktZfF0F2U1FUI6Q2YrqxQ356vt1bXO1WzTp9zjFLmxi31F5eFsvaPuFCqzBjktum3OClBU/E/2uG1SE9g3EbHDv23iF5+o'
        b'0GN3BWv5D+H+XR9GV4t+SA+iWejYxB0Thewji6XwxyYVixKb+IVi9YDney8QC2eOvolWAcYcn7R83TujKqez3YMpqfiuKzKSR2PJfY5sR+SircRDfbgn18/K6iBJ+Ddo'
        b'/MwVXyRtRXSPfwFwerrp0u44ANRozaDoyfjmUEd6w+fI9SLUmFyyPocGD0+NnlXxf9oh9ZNjey2/8FXR/K232xInRjr2be6d/86tX6MBmvfGuWvn1I77Qa+wqPnzp+z+'
        b'/U/OD9x5sM+ZppG2Iem3P3o9/PsjXx2WfXBC2Pb1abe2vxS5e8Lywz+4OYUc9L1zO+v423/c/+DXFyZ+UJzx6/e+uD9wUWFB697Phxu+f4rrIxw732fTv+Zd+vze3W8q'
        b'/rKh8G+Nv72aljjiR8kZSy6lPX/45VWNk+79UanXipGodi4ZQM9KjHL5t/hVZKu4P3ADX63NSpkYJGREzZdV4btPu2kohqfwycoQBjGK7ErJDGIQ/XJF8txIrgMzEIMX'
        b'VeAdLHYRsOoNjM9MwpvDgqj8LnxcjAwVoPIX8QXxQME9EOU2Br5hQ27jy8DuWlLYXgU5WaJODkTLIq14O4rA13hyPg36QvcjnsZ38R1/oCN5Dpdeil8xzRYrPk+OTEwO'
        b'4pMH5uAr8N9NN/rJWXxfkJglud0/wC8lZrmNNLqTGHCIbGKyqRnAD+GaPLk2fyneyllS1PjkyjlszMmlbHyLCpL68r7QqHIpP6j/KMZNk4asjMA78dnOp2NIYyyblYSR'
        b'Y5IrEg05IIlKUduj8G6Zczl+satj8Y/Ky1SSksC4V1ow95og8i0lO8qg+Zbnw//N8+p/87Lof/FyyqvCWdhJbcAPQsut0UrsQqo01PFtXSjL6iHkBy8+2+7wQD+ckwh1'
        b'ueLbGdUG5AuO2dSx7U4qOCUyTAWn1VIVHH6psayfwLl5uJY1cPHwgMCH5PznyR/wIxwP5CNMY0BZZdD5NJaaWoukJLt8MlupS7SpdKGu+6Itge1v0faYyfsPg/MwcPya'
        b'Pn4zSofnOhkIA/vO2ZBsYV9TaOCdc+o51h+0TOacTvvlTKrnjtN+oBPcOq4m3i0TuHqWp0+Wy0SzIVzL6RcZmA7O5z4YFeCd1Q4XgFFWybjOCCD61CLFlGV6AXPHhqC3'
        b'o7quylHmcFvEQXc5amvYXPnCilbXiXYoNiiS0cmnYCzapxatuLXObhyBtZY6px1Yl93Cnp/H+50faWAwwDwtTzFSCfO+Js4/cCFvdDn5bNhYqFNq94ShoJbPpVw5Hy9a'
        b'YWAAYsTaEmknDWJXnWsDk6oNhVJtsUCbTotlEYWPCUHB9jDxXvdoGMMg8SOiBEUFhUJF0QxGPajpDvikstDz/BZ2IsnfsjbQMrsVIpXRa7m/4QSG/8cBEwTuBL+ODUI9'
        b'twz5sYBLO8s7jyHJRgjXbB0+1wUYSoulym2xlPIS20YwO2siA3DQe48NRgAZ+bSpzlO0qdPdtGy3WMq7a9neRcsBHDAFL52h/kWxjK/ViTAAWaACKSunV8xCJ04GhaUb'
        b'pAWQ7MstlqW833mdIWs4EM4gwOgTnQALGAc1bEhoo5rA6Ry+hyGogW7WBaFAezs1XQ3Aw4Ze7l8G3LQeR74C5tXVzchXfJc5VwTmfFrPcw6ah2Vldy3bu1htAe92OrT+'
        b'Vd9+tqWdYHde29QMZrGs7XJti/dC+hkiww7vsp996E4OYmSYb+ADyy35rKx9uTHC6o//8VygtAN4sP5tgmCxrA+wEaZHBtEAdrvLJRCEaRTAE1zAB9x5o7uhp6SO1djQ'
        b'Nanr3NojDEdCx+FgxI8zOttou9e77rbLU2qxbO622+x2993WMkAi2jtOTf7Omz11m9XY3HW3O7cmQ0F0hiraATqjdSNGUyAf27Hj4g6AT5tb6zYDR7XTI0Z2oR0f2GB0'
        b'd2jGYqn2ADJu56XNDMTEtpBRYQ88FjKAan+/p1FhNe7pelQ6txaCDGnBo6LrjBb9A+PUv8M4CQEOyaW0I0k34xJhsbidHrvgWGGx7O9Ak3kYnZgAwIHHvjvM/QIw9+sW'
        b'Zj7l4UBrgKVV1dY6GTjHuoC6dwDq9ue+O9jxAbDjuwJbJE8jHgq1igUPslhe7ALgICSs7Ugj5MGw5qNQptwOq5tCSze4Aa7260X8On6dTIJZ1kChl4lX5X74KS/zKWGM'
        b'oGmQ2hmNfQ0FE1q/akIJrU+xsrK2yk49f6ttjhrB3p10Gm6xiHVaLJd5f/B01mMNTw98h3+7pleg1/4nu5dIqRwocqYINhkSZ/BLHF1xJxaIrcJiud2l+MduPUp74e3t'
        b'VT6svbpal8Vyr8v22K3u24tl7bnFtrgONM95IGQ+umsdlCuL5eUuW2e3Hpnvs3G90kNLjhoQYF7tsiV265FbquyxpTC2gG1Q4WtBbUUHr25609mAurCvhqxvukqWIWe0'
        b'GzRX5grCCTJBTplMHwBkHV0dVBPkt/AnxPUirRI2GIrcT2ilD4ayLWBHTYWurnaluIk8OlV0pfDU1dXSKEAP+FSTjxsNK2aLf8p86uUeW43bscYevJh8KqipwuEGndi+'
        b'qs6v/nVrgICRYI1bLG+0kw81izmqDR4R6SGRN9Fh0ad08B10LpXqc1XVummAMepn59OG2qwhX15uL3M7VogBqIHkVtlcbotolfXJLR5nlXM/re0wTagDhOiFGMBRnzqg'
        b'9EcwM6i46cqM6Uz5ddK40iK1OUGTF2hC7YPOszQ5R5PzNLlIk8s0uUoTJn3doskdmtylCWPCL9HkFZq8ShNCE7qR53yTJv9Fkx/Q5Ic0eYsmP/ePsT7m/x+vxg5+IrWQ'
        b'vEU3EqjvhFomV8h5ORf0A3QxNq4bl0UF9agdNIqHKU/Q8Vy4UhuhkallarlarlWKfzUyjULNfmmJVs1+wqBU+vFQ+1gaaSFbXWQbaUmBqybSlswhdQLvqVrbyYlRLv11'
        b'vdPBidEfXbVczmK9qlnoNxbrlQaAk0K/sbiuQhjLq1goOAULBaeSQr9pWD6S5cNYKDgFCwWnkkK/RbN8L5aPYKHgFCwUnEoK/RbL8nEsH8lCwSlYKDgVc4lUCAks35fl'
        b'abi3fizfn+WjIT+A5QeyPA3vNojlB7M8De+mY/khLN+bhX9TsPBvNB/Lwr8pWPg3mo+D/EiWH8Xy8ZBPZHk9y/dhwd4ULNgbzSdA3sDyRpbvC3kTy6ewfD/Ip7L8aJbv'
        b'D/kxLD+W5QdAfhzLj2f5gZCfwPITWV50n6TOkNR9krpBohIdc4BEJUOY6yMqGSpMZ5J9ui+Knpopaj+F+sGVjvtJ/gObQQ9Jceg6PEYdMZhXSJmthtLFUrvk8+Z2sN0c'
        b'v+8GC3jm94aj7hvitok9dINH2lYKddegSlTQkVkrpcI28eCPUFvmoUpBoOaQ2mqd/godbtGuJr7q36WZmZ5TNEuqwdqNq15Ixlwu+Z7YdKXMCgjViZtrwUd6DWKT/r5K'
        b'7phup50OSEh9Nhfz/qTAMY+QFVCTrapK56FSVtVqyndCzgqHvBzCcanSRykO3c12lXKU/TmjKQvsi7bwy8KcCX426GbmzxPcOpkALM8ipnKWKliqZKmKpWqWhrE0HARQ'
        b'+jeC5TQsjWSpVpBBGsWuo1nai6UxLO3N0liWxrE0nqV9WJrA0r4s7cfS/iwdwNKBLB3E0sHAvGUWncBBOoSVDK3njw87gWahxYtA6JWvU9TLj8MaPcHt4FxAe+rlfdA6'
        b'eU0/Vqqkpc7hggqY/Ih6ObUqrpO7RwLTlzfw8Hyae5SgrpeL5l93Ii2vVzTIOLT8sy3Qu6XaLRx7bpFbvwkgYLpLWK7zv6mQMF5cAJ2WS88LgnGJOT7O4uMtlgcKywjX'
        b'CNeDER0rqbRRf6l2lyvR9prk0xQA93dUSy6NSnGfUYxJKrM4BJ/C4rG7nTR8jHjGwRclxjQPnHJzzqL8iX7+1Ukt5k4aD04MaVLCpIPQw5EgAYobylBjnccJkq0dmmCS'
        b'gYoZ5N02n9JS7apgTS+jBwYVFrv4hx0fjPS/xr4CBi+VVdLNUBYL1+b2uEA8cdqppdxWRWMg1ZTXAsRsXB3ljjLm2AwSiUgzArdt1e72DvliLVW1Zbaq0OP6NBJxJd3C'
        b'dQF8bM1CNeyvGKHYN8DSYchBnoX1KD2rgOtqly8cgHS6XdRdm8lWPhXMC50TnzbdPzPiTKhcdrd0w+WyO2mF7IZeKboXUEOET7lsJf0kelDYg3r08KALbHbfp7JgCZMF'
        b'o5kDRccoWupOJd388OLfaGYp0rBPC9M0hlvTp8OIPFYAaMmF9WOEuvcVjQEdSHRhTejYVMCXNa2IuSjULGs/mGkQwyi4a6WDrNShUADS7ShfDQQ5iFA+hmsr00Zm9gRs'
        b'nB/YByNDA2zR/fzqWnf76VkWa/QRj/Ay+1pGT+0mBNoNjavVuVka3PTRIxc5s3pqtX9ob4NjanVoVoo0+ujt9hhOa1CgXX0X4bT+g6aZYlvYU9NDAk2/l64T48u6PKXS'
        b'AQ3mtk7bk7xqpKhNPcLFhCexIrZXSWWdOniNyiksrk0XcaBMusL2snKHnTYoCQ5QOzzQ7nMT4AUuXZI0TkkGuHS42V9/1K0ktiuZJIa+SnoMrHyqp8FKDAzWuM5RTrrB'
        b'z/QZC9JTIJn9GFgKJOSTnuBIDsCRFnLGngYSsZeGnrbvCM/MgtmzUmbNnlH0WMftnX/oCR5TAJ4CNvtBLFzyxPK74ndwETLpZrGIJ6JDVNVK22qXdNBcV2OvsFF9/LFG'
        b'7dOeoBwTgDLJj+p+N6cggCVOrUssnL+g5DEC5kHrn/XU+vhA66MYca+tXUYlXPG4PAi+dXW19CAUiEge8YD9YzX9x56anhRoOqoocK7l0ZsQA/c7P++piSmhFKwa1qyt'
        b'wh6EhnWVq13U1U2Xn27OhTVe9Rj9O8s5/9RT49NCh7a90araitA2dYlZBbPnPN6sftFT0+mBpkU3vxrB6K41wp92xq1LnP3obUpbbn/uqc1ZgTYHdhnCQZeY83gNQif/'
        b'0lODcwMNDhF9GUFErKFnQKSlIobUyC8uyH8M/g+NftlTo5mBRmMYjWMSs3Sc5bFQ5289tZLTThM6Ui4qZ1OvG3qdOCMvL8ucO7do9sJHpZtSH//eU+v5gdb/1LH1UOnf'
        b'pJsDNGKuHeCpYXKhK6CKdxUTHojXAvOcIhrZ3aCbO3+mQZdfYM5Jz80rSjfoaB+yZj+lNzAvnjkUZSqlOrurbVZeDqwgsbo56Tnm7KfE68LiGcHZooL03ML0mUXmPPYs'
        b'tMDMAysdLurSWldlo/GrxDAfj0PU/9HTEM4PDOHQIKIuqkoiYtrYYrS5YBQfZ+K+6qnVpwKtTug4caJGZ9Kltx9CM+fOyYMpmJU7l1J6ikqP1f+/9gTJogAkfYoYtxfV'
        b'SJhCgeJO7SOuFemQ2zc9NWVpp/FSCBZ2qlFsyN5uFgrWRR6H0H7dU+OloUSvndhRH28dtWV1wVT8XiZsW2S+1KArl7nCJbAtQ+ZjVTeAXovnXuk2CPzKGyC10OcVzHVO'
        b'Qd+0sPS4ElLVCY4LAv/BlALRD5patAIyjihytdvWuhbJTHq18/e0m8to0iG2M7NJ0MgFzmrEdlrbA0B32DuKoF9uk6q0y/wbkKDnJrCPL1GnzDX9OyqcQe90P1PUuiZw'
        b'0s5pkdhkV9NEtytqZe37Vp3U24CHTLfnIBOkOXJq6VbvCUS3diva9+ig//+mfZVTI0WXLnBqyYBhoR8mk5xBqFmgK2DEB7vvd2wQMGIIXsHvhsZMX35oFKIe0o1HXpW9'
        b'xmJZ2QGaLowM7Llc/bCutq+Y8YNtOPm0HQxZTwYwpx1pqvz44osMtWMpJTOWSuLc7LO9PqVkwlKIFiw5M2DJqf2KxRfxaUKMV0rJdiVndihtBytVRLCRSilZt9Ttxi3R'
        b'sKQNNV45h3MS+jhH0qtEThrERwrM5vwFJD+lliG6v6WWySNixjxmfAxVd3Ez/sO4G939VT5q3A5NuFqmVnhoXBPcSBrwrYgVkXUafSbZlpybbWIR+1plCG9dkFSpwFfw'
        b'UdLUZWxG+s+1CgXvagl8I2LfLJQJ8sA3CxXStZJ9v1C8VgkqQQ3Pqr18OSd+q7AkTAzIURLOgt7yNDAHlEawJ6KEaLjWCL2EGHgiUujNCEesr3cHlM92gKYuDwJUHkwI'
        b'6IE3SowtzJPDwtH9aQtfQUMRyIQAz5AzvcAXFvhwMFxW1wq2Kvr9uKEdbZu0RUvwXorL7+iRwrENXH8lan8dHSkc3ffdIAt4VEkftBvQRTuPd/KdmWl6cz2wv80Bo2GX'
        b'rX2Hj8Y5p/TUntff3uMw8LSeatzSbY2BSae+En6PkHaKTz9B65zaXdWUYGwNYjrdTUbXtL47Nw1JBmxvNZTZMgrVEtRqR8Yqtcpo+iMw1vKHM9YdD++jxFw7ng0IuNzk'
        b'onZfKleMG5qWvP2Z39cymWscXDO/KXZNr+TLZM40t0LcPIO88riKugNy7Z9Sf2AMFn6raZiA0vbIC6M6QDoq9HGh1i4eiBdPFbCAMP6zd4xTgGh0BEkLVPzG/DR69SRN'
        b'mMMJnSFga3V1oHL7jxNEBDXBHu3GY0tmE4TdsqBDBGrJM5seZ+mCSbNhhne6x6JwCYsCOBQ0px0waBS8eCRoTvt21VjXglnAQzOWrReRltejWaiBk7yYZbmdxODAS/So'
        b'A6WjizX0jAeVa3byy1nkHpHl8s5kOrr14jVdFz7O3REjoyA5LpM8rpXQwBpjV/C7a922KiBOdGfKNQ0uKM2vra6bpud8MpenukuZScHeOvawsWFP5eq1HeWldt8chjTt'
        b'+NIuWjBJYxYnzYJzbkDc6CHmyWR4aJ1MGnRgykrxS4RqGfVKoV4nLC4wbhy8OJRFnyPnRTZN2kiTwcShWeSiKlvAOzsx6njpr2s7F8KoYXrZj+yIokRG3U6o0wn95qAQ'
        b'Ttkw/bqgoKVsV+h1RFtCPyqsAJYcI/QGNqxgZ2zVNAKWN8bbt1wlxApxUK60q1i0K/FDxCohgV4LfYV+zDlFJfRn+QEsHw75gSw/iOUjID+Y5XUsr4H8EJYfyvKRkB/G'
        b'8sNZXgv5ESw/kuWjRIjKZcIoIRFgibarypE9ugFt50qi4V4MQK8XkuBOL+gJJyQLBriOYddGwQTXvYUnpPheNK5I+9cZtdDPaNbT3t5Yb5w33tvHm1Aex+JphZXE7lHt'
        b'iRfGtHDCZNoKjIaMRdWiMcbi6JcMhQlwbwprZ6IwiZXHC2MZeU7zaSgO+t0lfFy+j8vTK3z83Bk+3jzbx88uhL9FPn5mhk82Y26uTzYrK8snmzsj3yczF8JVRgEkMzPm'
        b'+GS5eXCVnw2PFORBUjib3ijJcq5gJGmuOV+v9fEz5vr4WVnOLErdeDPUnVHg47PNPj43z8fnZ/v4AvhbONuZxx6YWQIPFAMw5pBl7w+hzrwipM8UiCG75IEA6vIeA6ij'
        b'rr4RjVBXAb/luez4bD5+mZylK8BNmvJMpCWHRiptj0/KooKazOywYrbBvJa8lDMvA9ZFJj3vSb+fOo1sisLXY55yfJaokbtoFL+DP8/41PoH65sfJcYk2jJsVeVVpQbb'
        b'ou/1bf35q9d3jD6wsU2BKieqIkYMlL7APgafJVci8FlDhseYNBLfZUcme5G7MnxRhVvYEdSJy8lzhH43K7N3/xwT/Vb0YX4VuYxvs3AI0INX8O6QTzezDzefyidesqva'
        b'f3jx4bvVvJ9GBw5Pij+TqB/jmthghAr9FrKifbfcqaDEqcsvvgK1Yk+MDDwWaPkaJVT0IGzgUKT485OQLwR0CUGZOmiaaZOhX85UMwwKl742Li47MbhP+5cz1VvCAKvC'
        b'AKvUAawKY1ilXh+20O/73gGrREbSEasG5Iohag8UJ2b5QxECEhmNpnkZac9kioFi6VwX56/EjRn4jAyR7XURZIeHXPFQJjBxvKL9RcC0PON86dB2JnMHbM1akEiaFqjn'
        b'4iuAtHKE7+DLEZFko3h0/NshKhrWOTp1zqea9+ZlITGUym6ycRU7O84BTb/IDo8nkbPsheF2NYpGKDV1ZFTv8OR+iDGFcnwTcCkkiL3/CHWRGCr+KXtqoWp1NrnDXBbJ'
        b'8RKyMcucMxzfzjKQFj2HInJ5crqcbPYMhdsjyImUZPIiuZhBT52T3WNTU3GjNQsNxTdkgLtevM9D5W3SbMhMzqUHj1tyioNOqyeajIlkSwp+idxKohF9a/Vq0ha1kH1Z'
        b'Bp9y4rt5U7JIszk7RYmUfXjtRHyaISWDrBYfxTfIRvxcMh1zIzyB7/IT8E5yk8UDLq/Bd5PF2ejUXhJ5/mlzzrxEFsA9P1EEDD+bIUOD8LOR+FZSPYPgabJV7VpBrslh'
        b'cLeF4YOItOKLQz3TKXDbJ84O/oBk3Qq8lWwi14oSaWAVgyGnWAzqL57Wbw9cSU7KNKR1VI2HUocZ5MRMf5h6sjXbSC7HKlHvuTIgCJfISwxl8F18tKB95IztXwjwd8VM'
        b'iVZzCo+38gjfmD0AvxIxXk0OeCjuktPFhWS3eto8uF6DcoBknPHo4DqVHCsBdLm6cgW5jptWkmtu0pKtRJH9eXwQSg6xj1xmkOPkvgvuzadfJkjMNML0GzLJLnJXbLEg'
        b'sR0sJcK7ye1wRC6TfexbCeQubkpPZkFmttNQuq2FiYnGJIA3VxqYfNxQwdANb8Bnw1Afh4eewMKnyW58P4LcJNdd5NZy3LLSqVlObiLUB18hx8fKcGP5bNYDco/conST'
        b'ftLFaKIDfJA8r0AxeK8MXyKNVrYAFgxV0KhNulTlxPSkRfmIBVsAaQdfdeG2EYGvWw7KduyMLeRcy4Bs5SzTFRdkFTRMj35uUIL62Ddv9vn2IzTo1d7CqbVtn7ytLl7K'
        b'fbj02uiS/3l3ubz8TzvT5mitM6cVv5v28epjnzuOx3NNN956YYbuwgcR6qTUocfiYuyF5785uum1c1WbZp2Y/unc1/n/j733AIvqyt/H750ZhjI0ARE7doaOWFFsiAJD'
        b'UYpd6SAIUobBrogoXREBpSioIEVEioAoQnI+6TFtUzZrmtnNpm/6ZqMp/k+ZGQYY1GR3v8//+T0bIgzce889/Xzq+77emjhtft7iwB3LSjfdEza+EP6B+c8TAiNf2/1r'
        b'7/Sj6bYdma5b0iK//Tb3SmnD5ddXOix47YPqn8XraqY8+PucE79srTj2wqrJwmnri1FT9FMza9cIj7V5vfflic5Eg+cPlWV/VZo9UfiXsp9/uld27yuX+mcn2ieWFr13'
        b'1je8bueBZ+4suWcVcrjLcIJZSk30585LYwM2rFgS+943zpP/ctv+ecc7fs8U94z6y75Pdn/9y6X0N12mfvbW90Gtn95a+Pbiuc4/3pt36nrLtD7vVivTpCiXBIuL4mcX'
        b'Le33273+VOTLJfGHfI3/Ntb7GXnV7G1FL+1+PjS2/ubeK9/er3tmfPtzfjtl9ya9uehu4tPHHvAxMTaTjnb/ois9e3zRpCTpNHpEJsAFlKE6IvH5mDJadULCSSilsAKB'
        b'whV4TaHjYSsYEZQEXcUnIOqCXgqwYGqAGiVz1w2HJRiHGukrJH7oOsrfZWxkkAqdcuhKM4KWXWLOIkUY5IhyKQ6QkcSI4ABxgrlwicAAlaMiClW0bIH/IPaom9CEKsMm'
        b'0fdORbf8CBkoKgnEr4YcWrMWAVyEotUM+eFWBHSjfJN06EqGToW/tZGYk4wRbIdLcJ2BOzVCJ/5XMNlOg8UC3UItjC0jWwcdt0PnFw5j+uTTKPoTug7VE2WERkKQhAr3'
        b'8IshbyuDjWhEJXZ46eXhvQLXXLSQn+KK2hz9aVMn2xxS0l2tXrONd0KdqCGNqKrQsEAsTzdMUUC3CcpDBSZ6RgbQapKOFyF07UrBm04mrr+fSIx6ktFNhsKRh2pR0yZU'
        b'ZOeANxAXnhNv5KEZ1aBuBrR9LnId5HuhK1j8QMeg+wC/CnUYUIAOURo0EIKMfNTs5Yfw0UeoVI5CDuFK7RTtwqNbR8G290XpUh4N3DLCkZTvi8WfZQIoM8F9NIW84jhq'
        b'I4MLF1ElYwKlu4EOZ+krMsKbWTXDvDph7oRq1qB8JzLPdDhxmGAq6gulb4hDF1AlvuK/awrbznQ4SYAASlHhHIb1VIGaFEoesgBySOM34HNTzE1Gp8RQJ4KOSegak9UI'
        b'PUn2AGUZPjlU5J9Qg6poTdxR9ypn6MTvIz2GO8xbMAZa5jFCs64ASrGKX+DvG0DZY1E5z3PjoEqUAsfkDNKqEzc0jxCQsjNlATThY8U4SOhnDmV0UNI9TAi5yCzU4oBF'
        b'DJkQT8o8AdSjWgYpMl4PXcTXfey9sbCApc1rSQsEEdAnTSOiGzo/D66rrqIc3PGo2oucT954dtra6MBhPKdq6aLyXbcA3+hvj3KdlDu7DjcZevdBt47OqFBa12kH5pKa'
        b'qOSL/dAgwjt0ixDPzFs70sjxFgLHcDuPEYAzk8FyOspFJ5wG25bt8ClTOM0AVTvDpTQn2mFwcjF5cjQqGf4wFr1zfKVizpfTRe24IeX0mWA8y5oGk+OGQcYAP64mOa47'
        b'FDNm4NL5Ajww+SZOuM+RilFXjJVkIfQHwCXtAvh/nuWVmhOoIE9yWIYI8u4GvB4hdhWIeCuCgIp/WvJWAkOCjEIJYA15U4Epvm7Aj8N/E3B6D/SEZjQf0FBgIMTCuECs'
        b'EcRKXHRijd+ocXn0ECGdWZVpBRsNlJlVqihnEbG5pZI1mrqAKIaSyPA0dcCyWB65PToxeijeiu5jdEejXmocryw0lRzZrBD6ogTyKzWix/OafdY9ggry4iC2WO2t+z2U'
        b'sbqhynaNCM2qtpwPftnvNpmn7nyYefu+2j9tQxlSVKkZrHbWShiUQZj3jx+nqyTekYQq46pCH8K/86u6IvbaIrHi5AN1+6Pcn9RbPdL7iSbH3j8pmIZgkQCsf4sLV0pG'
        b'OVKRlhQTM+Jbheq3UvJVfLcDvt2aJAkMBIORmtCg6j/U8FTrh42/WF0BWxocERejjIZIJDEouNejd5Isl6g/9m7cBYahGqt5xGroq6tBQ7VIYEYsgYlTRzX+3rdTK3bB'
        b'wwbcUP3KWSNjHw9+scZ76eaqhgacg7+pYeWZNYEjmTcH+L0G+zm1NYGn1gTuID+SNUFl8R4KHTcyu6wzfXMM/zu4ZQlAsYLXAkVI/htEUjQ44ENuLd+epEiIojSz0akU'
        b'ktw6PDachIloLUvN9OSREB1OwqesV9I0GjKwShxdGn2oRBdXBh7FacfhVQKPh4UFpyqiw8IYCW60te2OpJ1pSZGEGNfWOiEuIjUcF04CzFSIvSOSEqYNW+UEY18Zd8Cw'
        b'Clng2h6NeLBHI7CHha0KT5DjGg5HCaT5X9yQ//hhwy30j1t+8gkdOYmJMPvY74uw5yL0jL6IuXsby2B5fHfmi1KegbrdQjU+KB8V7NEmbGCJv46Z5fihDiRRTGw0hUj7'
        b'nnqQDg35mrR3+qATRx6ZEEo7eMAjQgrQ4KxlTqIBstoDuFGmIqU7fMhBmsF9Z6hxlCo88R226GbCEOMrnLTTbBSUoQ4s2uUG+GP9CQtzp2RUB9sDHdAK3UbO6ITgP0x1'
        b'O6INWe0107QhEzYUXJd6l8HyIhwnVphcX1sfe9QUzAxL6NQ28rcAX8pLdRnlShbCdVFcmewloZxGBbvZfxHmaPZ52O0IG0vbcF9qOv4y7NOwnTFfhuXF+oTrxdzF0kuZ'
        b'Tfrf9Zyk86VCKqzCKVSyaejLh0mq6JwfFlYPQRvVrKAK5YZoZV+Co24EwrfHhGorhqhtKlF76HgscRw8za6EPpZlGU86uXLSWWqbdFOIG/MxJh4uhAmRIg3g/5EpB1V4'
        b'X/vVc/MQnpvjRpybn5oNnZvo8Eoo+72T084fT06oRAXQNt5ocbyZVECthA54ilxgM1dkgq768Kge3TSkMNmmKBtrPvQ5kasMsnjUsSgi7sZsCU8PlzULKnbEekX64ukQ'
        b'/2FD9PbY7bEJsT6R/uH+ZyeF89+N3WEVbxW04RNnHdfkS0LuaTv9sG93q/yimpb3kYEL1J1NtQatY2RpaGAq2mupfYzYqAgeMhYa5+8RPAgmIw7C96aasvYI7/sPEq5r'
        b'PYq1L3W8NxetGc/LiUlGeND8C7wsb0fcM9geY0gXpYWx4K5JJ96fyZaTHmT1WLqqB7Sp1NVl0DZs1IaEb9Dh0bpv2wzzjNA4joFtegRqcVLqlBEH40Pjh/lehkeK/DvS'
        b'yYh77vBDUuQfHCex1Ofl5M/dU8Nk4XgEfIUrLnOiWbzNzHEDEt+w84/60Uc+/uyGaXcsQGXk446UN33EDnzf8GGao5bI0n+3B7c/nucTT+XIZ14Ryon55UYdbxf+KRY0'
        b'tjxxreh8uQulKp92/+g94XdFgfiEof6jyygHXYB8e2LgEW2LWMajTpS5MI30yLRdYx7bLBO/gcx0G3SCmqDgImqxIg6mNdAv9XMQc3pwU4BOQpN4hMGb+dA14DhcNWdh'
        b'tSMOHilv1oiD985DB28gZJcb5n+coOrwGI76H4m735DqCCqHvyB7FJVKBrn9s3Wyx1K/5Ljs8dkTYiaofZOSR/oms4aOOwmCsRg27vb+9CzagvpMZZC/Hp1S+8yEKIP5'
        b'zIh0ibr93SWp0Im/6iHPhDhYoD1NjA+qWgHcwGdbH2X2nI96xNTz44XPvgDUPOD+8VsLtZbDvT9wbLcEdQZCk1RM3ZJxkIWK5cRxA0VwCn/jUAE6M4P59Y6bwlHoUIg5'
        b'h1QOqjk8L25BHfNmXoBCyJRAlw4XFM9BJ4fOQxU0KcisWOW5VZ6Gz9+CKRzkcOiYlQk7fVEvypPgjsAzuYuDqxw6A1X7qfcLnZ68XL5LwAksOSjmUJ4vFkjJgCa7iKkj'
        b'9dXNyYav2FkwR+qm0SiDuMRwQTmReAJzqAx3UTU9xqHTWp82JgmqWFugPl1Bonzi0LnRcjfoJn010EW0f6A1LRWuBXnZESs8c5EVoTP6B6AJXWCMHlehD7W6QpGrs4hD'
        b'nQk87gvImL1QQXYHfehOHOSlJaAx7qiPuo7XrIdSV58gXS4EzojxUF6GCgUh7VnjlewKN3fhTy6cSyB0Mh9gJi6nE05tC8Ez2olzgtP6CT89ePAgZIWIOseKJkYafpzi'
        b'x1FmWAUWXYtkSoAa4tw2gEtelJa80MknxAZycT2CbKRwYr2XN5GRCvyocBRImifeabQ1cgz1jvIiNxJioXkTmUpEnHIKUPYP8TtvhFMq1zOZRJex3ATtk6FREU4qfgxP'
        b'kwwj/NBJI5ThrKcDGSFwTgzHg41WmY3TWxyIbqJbhNjEM3a3Pr6rNWZMigH0infpoTz9AEPUCkeg1hlu7ZNOhpxFjlAhRqc9pKhjyRwot0JnItMVxLyAClGWiNi1Dxtx'
        b'LnBLV0+IWkNQ+yYoFaNcyEaltigLz88T6Hjw+LiDqAEyxqNb8VPHo248o4+irph9kCV0scH1KJwMbSvN/SIW0q2DzrQT4eP4OQJOL8N9+8S2Wd4cc+nmHILG4RS3AWoP'
        b'KbriH6LJctsC3ZLIrXCEFhk7zpsr4jhnbs0h25Ux8ZwikBR5BPVBB2lFuT5nbYg/rNu2AxWjZrymz/MuKBPqFrniETkVhjqhGSpCZsHFTbjKGaODUeY4VBmNcmKhBq7r'
        b'bke9pnugFtUriKzjkYCqtVXUy8FHx2w0iZFBjVL8P15bcNkdVeJJOw+uBkt56qJF12ZCG5kGxBbfbgDHve3xjoHHeYyeyHkqXKdO5ojFC2SalL0FUCDe9zDC3jypYRz0'
        b'TVHMoWu/ChU/1Mms9jCjJtSkz02GDFw5iix/PgjV2fmv4+E4zwnQcd4jCk87L7pFwuUFdl647/C8LdyKSsgycPLxdghksR2DAwmI9x0rgclkA1gT6LBOwO0JNtkDJdDC'
        b'ZlcGunSQufi91ypjPZQqpJdvACUndlyrlw5da718/PztHfxD9uIhyyFcxxqxBXSLhoLAUahuWzKdBSelQqoNtwbusn+V34RPVLal5KHTYpmj0u/julIPWgUoJ2WbgiAX'
        b'rtsK1UEBUj+GYR+yXhm5QuJW1sNZVegKh2d9E94Kc1ExFGyxxvvBdVTrNQX1e01xRVfx7tgOh81Q+QS4Qel+UA70WeB9swPV7DbR14N2E+hIS1FgoVkuDLA2p1urzRbI'
        b'CyI7lpDbAkd4aOag2ReaaTiK7p5RMqkDVaf9caVstqJLQxMKtlrr4QlcPIEGfeAVXwe5QagwGApD8OLgVujY8qhiG8qjzv3t/pAtSZ8OWcY8x0MZ3lJme9I6oCuoZjSu'
        b'5zU5dOhy4TMFcIV3cFgkHUUfc1hiAvm+eKndhBx+AQfHF6EcxjtaCV2Qqw7aSUQlPCfZJIAWqBGx+hSiBrnKQ2wAfcRJjB86C+dpwah3CeqUQd4GaCIO12280+g5bKQu'
        b'HUR1LHxBB+/6EtEkHothxzxYod3uqFkVGIKadqJrIs7QVDg6IEZBPJIOE13wpJdS9Z5g+lO/J7oMt3BRM1GGTgw6ApWMXDoHnV+s3s5x+9ot9eCMAJWuhB4FdUAfQ8Xe'
        b'dspFsxdl6nCGsUITuLyandRNKG8tYzWAslWUw2cMPlVIf7o646M538FwrT+cIG7MrYLRqBVdY20rQLljId+R0GHDKSgSzeNRI9ROpGVCpyvqlVGq7G1epNUX4aSqMnno'
        b'FipX8mjbw1lKpI2n3zEFce6YwIVQO7zPOis3ycIAssR1uCnolI4+1rNLadyJCIuzhGmJqu1YWG1H5U7D+gr3kz86rItFkxI4xqp8A26gW3aO3vZSvEH5zNFfKEB16Kp+'
        b'3Jzr7+rID2D5af8sL8+gmzvNl1ucLT97YPc/FGb9b/kLUiYt9jxrO3nZ8sMZZmu3em5f336h88WN0gidG6vaPyqe+vRXJmu+H2ujMzf0Cd3av95++zA6t+8V90/eLV/U'
        b'sfjllQ7exfHB0g2x8Qf9zo3as2Zx6O7aPVWfnWz4aJb3QenJexuXZWa+Ej/VR+e3B7ddX9jds35LRwussohaPO1DeaLF0R5by2cu2mQv3b/5mXeut7+S+Vefjy/8JO59'
        b'6TfL6tZqz9LmzW/ERTVKXcZt27Xqzy4zCmsd3e6/63pwhvQ5xbeSzyde/Hqr64LoifXffPHUXotdYV/eeaGs41np1/IHgSHxDvmSr1I+710cFZT8rwl2B66+EFaeuj3T'
        b'p+Xvv0y0dd9cXriw1aA1VL5J/EboJVe/X2c7Lz8758JX8y6I4JlXux3GfHHpRes/v3rg8J9fVXy2cde4hT+It3/+qnH7Zhu3B/FL14xPik/+8tWsH9e/8I+fLEuF672L'
        b'fv0wqu1U9jzBweee//H23xJ2Xcn7/iWjxAu+4QeeXPSXc4VPfvrakdGt9xaWmDh0vfZyxKQ3DrjF11pM8PjezLxgT3f7fZN3O99+c3wFCl/2rF1nQazw2TMLVj057Rl3'
        b'p8jszgnPTPizh+8n58ZuTDvYYfVa7jv/4HsDf37GWV/xz7P+n93uM/F3uVJj6Jdzf4HJ3R/M9x245v6h6F7SzbLXvkz+wuXJBwdn7Mk5rvvD9ZOljtN2vTWrZ9O+p3NW'
        b'/iWi+oaw7YfYUXsnxZhkeP34qudN97c/+/S2/0d6/dKfZ2Z8V/rkxFD0N4OrdwP/avG3L99e+a6Lg/+7/5pdV/9Dwpt2iX+vLZuJ9u2s/PFO5aFonZjbi0vhhQ6vA/Gm'
        b'830MXu/aYr5Vbx+6fzsr/fOZB+02TX4gaCvX+fWnMdIZLMDgIl5OV1g8BA2GQJWGyngIqMb7LhGTLbBkIgsY40RiWdL55UbQS0NFoF9XhvchuLJfuQ9B1XLqo4d6e0vK'
        b'pI43kOrB4TMh45gydwuvpDZVDJoO5+ishzoF6TvhMiug2xX61DskFtcblFskXvPVLEqkIhafGso9MhFdVe6RFVDMCijGkkgVDfAh4T2oDVWpQnzSxzFKkv4dcNVOJlpH'
        b'InwYJYm7iKmvldLVdraOUsiz57jVqF5/I163s+JocE0EZKBqO0dohR5yvtjjXQodFzgk+tNKrZoCp2Xq0ASodVISyFxfSKM+jGPgMInFQJ3RRIAJGBBkxdxkmQjOoTLU'
        b'TuMpTNcn2jmiIrjAKiFGzQJXdAbl05qbmU+wc9g3QyO4pwqO0mgbVGuzVY4K9VKMoF0O16JkKHdIwA0JtoFOMZbsrs+lsS5YszmGeu0GuwUgG06aeQtRDWraTB0IWH+/'
        b'jGpkKltxAA31wTti2yjIFmKZtdqShm8EQBkqR1hoynNyoJyFcGKGLmcSINyOZ1kGHRiJNX5bgD2eNYRADfJs8VyDPgF0o7NQQGNnoA+/vlctcNijC0zigKNLaaiRSxoc'
        b'Z+eHu5QeH9GetORx09E1jZAvAYlkalaGRcvpwAbit7Tj6sVA1UCgzMS1aQQbzRuOBWs3TLCQj6WRyqAPdMOVdpwPlmXq8bJZbzoo3kgVa1Q4nrL9WOi6DIp8UYW9zII6'
        b'FvnSDOdZCM5hVAI9do5SH2ZiX4radPDxlCFMioUrtF/4eHxzvh+hncOHzo1wHU6yk5DOlaEOFo9U5o56lQcdKk+lBx1UbqbzaRqeS10qyWAT6qKSQQJexnQtdu20GBAM'
        b'8H2XmGSQzjH+vqKxU7SIBk1wWSUa4CFi/H3V8bhF+X4Oju4mqmAjnrOEYyIzQziWRnTbCVjWInE5G3c8fmQOlKyhu1CU6zKZL7oGld54GwrkbbmptN1eY2eqOPU4OLOL'
        b'curBuTSp4b8THyOd8F/Ej/393was7yZD0DKpgYtAFw0zcM0m5lg9yhljStmKxA8E5J9A/Bv9JzQUkAwfAjPHwOEs8b3kTgEveCASEvA5gmQu4sWEdYZCExuzf7hc8skM'
        b'fyJxPmaU48+UxPvgMgyV3H74J75CMqdwaQJDZRyRMY0REglJBJGBQE9AMHDJ1wBmrgCXJaA/2ZeYF3wltiTsN4bKcll2oNq4NqRDmDGQBQ6xoB6a7WVPvjnTmKHo3QNR'
        b'BgPJUwPeiNH/Z+Mq1dOo4RJVDVOz1ZWyV8ceUQvkMfyr7YgWyLdXDGIwfFgnSXmaO+b/CE8o8YXyFBX48TyhQmpbFH34F4GWmIHlMWmEpTA8IYHinmrw/+LKxZFahScM'
        b'gkNlkFlRUQwTMNx6Z/SuYYWyCBSbsLA1iWneO2PCwqwjEpIid0gdldC1qigEhTw6RpFAQgH2JCmsd4Uz6sSoOMJ2OJybWLMScTvpjTE0k1+ZtBktZ5mcDKfQmiAuWcdF'
        b'yR+fmJAAELhZe9NoADwP5XEEHha/h0QGhFtHKuRpSYmsWHXTvKPCwqQEsGbEAArcP6r+IB/jdlqnz3ck1NcrcDfuIp2Ztj08TV3bgRgNrSUq20Yxa2mQEYuEwAUQBNtB'
        b'XaTKiY1NTVIkUyA7rSXipqfFRSoSwlNZrIeSrZ7hKsitbUhmuj3uAvxaCnuyJxn/Gp0W6SilgzBCrAfp0LRo1bgox53GgO0cykCpHP2oJJqRm0zQjrWVOWgAHsHgyHPa'
        b'GBwN/Kk+exC63EmmCarcqzKcQxWq1rCcN04fL4GuefOGZSaQrAR0Em4qCDwKtKF26FPaE631hMRmeSPFGUqsoGzcJC/zGSkH4GogOoqueKCSzSu80/DBfx616rn720/E'
        b'QvB5qFqJbk7ei5pMndEFdJEae9628aImP+e5f9koXRfCUSPAZriKbmAlW4y6fPyCCAvvCZLjQpKIdLmp8SK4PAqLDeTxSH9m6HWe2eyoFynk4hIONnFykuF3xqB1xgtN'
        b'P94cdcTZ1PO1brspS3Su682/m+VoPXXKnpNeVsu3z3rmyT8dfaOxfMpN+ccVq6LOr8k/uOxfz5gFJo2b675r9aHSQ3eLrlp1vb+lxSDiOcWT+h7j/vGdxwaHJYX7ILn6'
        b'i5VnXr7SuPrLDf01ZxZFLPv5Z+GxTeNvmoukEiqBQC1cm6mhyxDhsjaW6DJYSD1NpedULH/kyQJQORQp1ZlQqEkjZkPUcwhpjRnusxlZOJmCCuibzTf4yIl51cFGZWIa'
        b'BUVC1LgXtRqga0ywzUT16PCAzoMy9KnSA+c9WOB+M2pFzSTqfRM6ow58Hwd1VNma4WUJ+V4L4RKNfD/Ar4LLq5jcd34BnLNzsHFG59QaQQj0UOUOt7seuiSDshjg6hSq'
        b'iQVjIYlGuxfBFZ+hYfNYhLwlp5Ls7NksYr1qG76BiLKoMnyoNEtF2YNwROmDe2SEhz5JxKMrloovttrEl0PcAiq0EED9B/i7kAgnRCgZ4uZXFzWYdNFp8Jk+jClSwO4Y'
        b'OFtz8a8Xydlqre1szeA+MBs51EBdBxLIiY+aUHzWDEIpUCWqjhQCKMwRPjRNVRWM95NIy8EaFL1TCV86GDNdIWcHbTTd6vC+7LnC2yNIAwd9pNMpOiIuUh4amRCHS2HU'
        b'uSrApxgC4Bi53ZHe4ehJvnvQ20aCV9coVdkvbjRw0F4dOUjgfuXRtJpJqVHkD3jf17ovK+HiR6yD46oQ3zAK+aZITkgKj1K1XtUhWgslmKJqCDdyZChjaeWKuDQG2q6u'
        b'lPbT4pG18vAIDrP/o4+G/OFHvdf80UeXb9j0h9+6cuUff3TFH310g+fsP/6oa5j1CDLVYzw8Z4TYTe8YRiLDJJzoKHtrW+X0tx0UADo4QpWGrmkXSUaKO12VGk6Rswfm'
        b'8O8JMV1PhFi2K6S7OjoPWi00NJbh1bLlhF+YHhf+x3pqRXCIlioMUGuTPYbVgy23uKhHyF0iToMSVi13mTPmbPdQXe6n8IlYPAnzPTZlBcecc8VwyUAO7TYSAUlA5lB5'
        b'OLRTMc0DNUMldAhRvrOzsw4n8ObgHCpdzXwt5e4L7Pwd56MW4tEr42Wo1oRGDiTYoYt2/j779LF+izL5BWvNmVc/Fx2Os/P3Ri0+5IEcfrE/nJKKmD+gA51BtdBhjKW5'
        b'DhNo1+GE43h33cXsYj8qRAXQsWMdtKZBNz7ioZSfErWU1uIgqoyQz8aSS5KA45OIN7FjD3OmFNt6y+H6KugywaeYAC7xtkuhjD5jDGdQIxD0Fyd0fBv+VoHalc4SKDGS'
        b'o6JkImiyyIMgqJYKaF8kwNVw6MBiVLlGFUM8qCvFFR3bjNvQbKdZQyiEalrsOiyeZsttIzSqsgNaaVWgw28nrr4jalZWfxI6IxXSMk3QNdIvR+G6xvvQJdRKO8XIEPKg'
        b'Iw31DHpjlj+NQRjrGyVJhvp0fTz+Qn3eaS/0MuJz6OAlIrhoRDBchPb80oNQyMamWQInocPUAq5JjHlOaMgvHWWqIHDYWFo+i3JlRNANohAOxPOLJV8OLqDi/ViwLoAs'
        b'1ItKUFUw/qUEenEHFWPJugT1mulAaYSOEf7mh45OROegYLG1OZYNzUxQQ7giTn/jWKGcAG3+6Hci5NVF/k85m4rvlqfMq/zSVWJm1hg4cXT9Xcu4BU9sz7fqabXpSrbZ'
        b'7XXpYk1tspvx4YaGxoVcfc1fA9qfbnm3oP+ee9nEnvPHSkuqP6ralHchSnJolNfTL3Ss/NYxcFp887f+rs25H7sdeLE4992oid0T3v5g+8mZb39yuFtw6rm4O2t3TK2b'
        b'6uV89o2P+p5tPPhJ35rShiU/j3Xr6Dnk2V7wborfkZdeO5D9knEC/3PGS6vlu444ptwf8yZ6UNP97ifSKz82fjGls/27Fb+Z9C05c/1Y+9WaN79971XZpx//lP7p6B+i'
        b'3ngn6Mr9+f96b9lm+SqT/Sf6mxv3/6J77PLWd77tkTICbzzdTy+mxnwfA+YyZN7OqtlU7LXBIm0F5C9BdQMpsajSDYvrRGhGfcvgsp3MwVaCLqjCkw3thbre0Js2Cl+3'
        b'cN4oC3DYCJeZLO84nYnSVbFQbBeAB4umZopQFg9HUA2cYGWWQjnqgnzFVo1kVtSG7zhLraWhqH/UgJiutxxL0VhMT5jCxO1TYybYEQM/EXz1vFIgX4AO2wey3NRb+oFy'
        b'CXTqoEbiKs7noAFyfdljOR6oGOUnz4XqZQRXIZvI3b0BzOFwdbw5vXQaTojxNTzvTs6BBlrkDOiBCnIR9eiSMnM5KF5iQU3GQnyhWZUZitq30zRmlhna5U8f1p3kKE83'
        b'RmfgCH4UXeLwNteI20jrc2Q99MixVpRjs4fUp4iDa9BgQNtviI6jQvwgVKJGHfxgPYn/Pgu17MF+6Nothy7Dubj7edTCwVl0BIrp+8Kge5k8PQUv52zywjPEa1vMUfVl'
        b'+bp0fGUrNOGXoTIOd3zNbmXI+GHoU6pOqXsGKU+t6LTfCGmQD4lPFsmxPEz1igjtekUY0SOIKZIkLAoeiLF+IaJGUmbgFFAtQ/VlSNMUDQQq46P6H34C3/tA8GDvqMFh'
        b'x/jt/iqUE5q9aKgpT6fmDVJMaIwhbk2hWhnJUycZFuBPTz5EI3lyUPDz8FpgbYzoIDS5yl86ZgiM1B1RaIC3/x1JqEdIYKCnv4e3ZxAD4VTDS92RJIfH7VRlH5I0yDsG'
        b'Gul51HKpTsXUyJo8MhiGiqJSEcslVbFoq1j3jPv/k2E91Yvof0IliqSerqlQwCm/+GGffhWLjXWslhFzukjwBxEyRaamhgJjQuMm4h7M26PHW0zU41n4S91ClDM4jwB1'
        b'zMHb5rjVorgpc4cF7Boqf8pt+cGsbgRSi8FpVYmUgFrsM4HV0sdf5DOB1yLgWuzvA59NCb5llDn9bBE1Wv3ZMmoM/mxFP4+NGhc1PmpClYTwxWWLY/ioiVGTsvQIvmaJ'
        b'bgkfJSkxLNErMSNfUZMLdaNcsglclxirvdOjZlD4KV3KszYri4uyiZISHjnyXImkRBAjwE+Z43+mJWZx7DczXJpZiX6JQYwoyjbKDpc3m0CBkRKz9bONss2yLWL0KIAW'
        b'KVmfRsyKaQTtqBhxlFOUc5YewfMUcZskVJ12vWNG1owH5Zag4Gsx0an3Zw8SPIffoKRJ07zpviOWYt3i5Elu8rQo+nO2s/Ps2W5EGHbbLY9yI+vI0dnZBf/DYrarVHhH'
        b'5B8Q6HdH5OW92uuOKCRw9ZpG/o5gpSf+rk9eGRrg77uxUZRKbAZ3dKjyeUefgfDG4Y86MViFlv+e17qQ14pSS8niKyPfTpPlLPL2D2KojL+zrIV4bxtcVup5WmDQynXL'
        b'76/YnpaW7ObktGvXLkd53G4HohakkrRUh0hlep9jZFKiU1S005AaOmLlwXm2I36fVDBQfqOAooClhhGgQ9xBvgEey31DsbZwfyaptMcKb1pD/HNN+B6y+wUSE7I8DRfq'
        b'6DwHf8cbISmskU/1Z1iJlaSuhkHe/qt9PUNXLA/28HrMolzwVl06qMn35w950CM1SS5fQdWYwWX4JsX6yWNpSS6kJMFASbiCjaQskyH9cX/cyI26P1pr50klg0oh0y21'
        b'WUvZC1NbyF+HFLKQFuKaeoVcG/nlLvftfkdL7+hGRceEKxLSaPfTsfyPZjFoTcjRlgfCwsHLk+Ac5KEbknR1PB8cnRBn058moikin1647O3DkkR0OZENL72l85AUkTt6'
        b'hKE1Dc/pkbOhyNdqhqA6eC9xVD07ctJBJ26IO/4kn6pdCMjgnh6UePCwtzTqskM7XsvJnaA+vsms/IzUIth/WKqCgapXiZBAUxU4FXUoA0mLMVCnIRg8NA1B5SrM1NVi'
        b'0fRmab5xe6M17JqMA4h5nsg+/BA7ZpCKvNc6mTIyUAlG7jb8RgfrIWvF2malp/Tht5G19sg7Flrb2MrjiBsrfb7jPNvHKJItX2sbD69H36xcpuRme+tHvWfkLcTaxjv4'
        b'dz3h8pAnHnc3IEUMrfRIJmOl2YvZh1gGtpL9ScUsMNKT5Mhkjw2dNsmpcUmpcWl7GHyvjS05iAmvFjmKbbVbEW3JAU3uIcelLTEZ25JzzlbqOOBpnec429HZTXmL9mIG'
        b'nLLO9FZlqQN/nkf/zIoeqWEMJULZNC0YEKx/ZskpDMSI3UOdFW6DU/jpItOO6KBMwR+xTgOwDW5qZtnhyAwEJUHtl9fidif/4WuUBJBY8an1lMYERIenkQklV1GkaQBd'
        b'EK/0CDgAxAKLy9kVnqoMIdBgpqC9Yx0UHU3aqkjQYF3TWpTH8mDP1QGBG0MJBVBAkGcoYX8JorVUu+8ZF9yIncQ2IdY/lK1JiZuiGjeV5qa0HWv3dg/Yk6mPgpUwYO61'
        b'HbKn2I4YL0BHKJmtUzljkhuyxdiy1qluidupHaSAQWBgoVRFlLs9fKe1Z0jgCHbxndZBu+LS9mJ1kg5c2kMqzzbEEdYSXjDeaeEJe+iDI+9wtiPPWSV2BxuQAUgPMvOV'
        b'Q6KG92AuqhFalMbCHzTwvQc9OwiaZcRdi5Y0zGeAu0cpOclV03dIudrHREmuOPBeSmoZEZ2QtDOWlPQI2zqRRfSHiU8mTHwai2qM4ZQMjkORkAuEfgFc5G12z1Kw+Mqr'
        b'KE+GMt010DXjUSaLdyClBU6fR2BFjS2x3EVARdHNdVTj1XHbKUlHLVjlRQXQjb86UK6IM4IsAeRPhSIFIfCMQsdRtUwDV1SFc6qRNaPE3pTuV+UR6vgIuLnoiDFkkehZ'
        b'qYB5Ao7s0iNZG8QIPNGHmIFdoZyltfWEjJdQu7EHdBLT8daJNACDh5p1GiCrA5VQp7skGxkFEphVG4f9m/1DbGwgDwqcIM+eYGoyvFAHYtk7bc4nQPcqaqdeo1hMcUDD'
        b'4QLHUxzQddHUfdERInbcLrSi7ouKiTGcYhH+45wlNAVBmb8DF51l670IvF0ubrBTIOT4rvUSBqJckg0HPahuzwwO9YskcOYQaoubp5+iI6/GhWyboTOj0N3gyDLTo7ti'
        b'FIfecCuat95nvJfrBpus1k22WV53614c9YPBOecOb9dvDpz4V8wcZz3JVdGqrCOe/InU72v7/tY9JvPr96qeb4kpP9r6dmFsoG3dp4l7vRau/fpP0Wl/bT+adC/Mcq/Z'
        b'he2u783Vzzk0v/zDKaM+/PzQfJuvv9lREn/xh56zT2ydserzMZO/f3bTzzdvxLytqHteEvHyzK5QabzT90dflhpR4y0qQk2owg5Vr3N0YBENtQJnOIXqWbx6A2/PoIsJ'
        b'5LL9DNRCYkd1OeNAoctkdIUaMGNFqErDgIs6w+GmIH3qehqpsQlqidlUM0ZkGTqK2gVQFgQnaYjxNFTuQrAX4LSMWpVHQzYDT7yEB+GGchLCSVSC5wAL8d4QyCzLdaMm'
        b'KqMtZDM0w96dvWgByzevVEP5oTK4prbYeqJzLNi2z3+B8g7898HQgBQXEJWjKmWEu9jMjoI4Qh3kawI5bkHlyn48QLKwmVV9C7rMDOuoZj+L+r26YjJ+E1lt14TEqpsh'
        b'9ONXQRMUMBjICt0teJX78gKo4QQRvEsUqh2EEGHwb1nb1KBzK0dSmPabMWvbA5GQhbES2A8Rr/dALCA/BSQmhPIcGwsE/LgRFB8l3JoSgGY7r81ynDgI1c3vobpW56RH'
        b'6lp/AOFNJ5TC2o0EP1Wowynx3bS9UM2o7PgY0u5QbDZiiQryWh54R0T4Uu+ICHWqVFdb2CwLSiUxqnd0lYzbqb28lmx2E9XJ4cups9mZkmioVBONGJp2tkmMyWPmrKuU'
        b'xQZtyuLyqCj5YH5o1WGpxXinFrOG65wx1m5ECHQLUwOHhGnx1dsrhRY1rBUJiRweQTqU65BR/RI9fEAUTSO9mKYU1B9LBVIKr2o23EdpQYwMiz2rhbI2XG4dk5AUTkwD'
        b'1pSbVUk+OVKgTPjOQURvQ5luR6rFINVAGxFtWvRuJvemqblbE1k45wjxmfieuCgitA10xQBdHmuDtQ3ldCdNo0LZ1MBVjo6OU6UjiJMs3IHGGoeT2aTB4KwumVFUMjF3'
        b'4LrW8tTPDDBOKqeAMhRrMP+k1jJsAj1XeRLPjGeof4jfCs9Ae2uV9sFIOkcM36LBxSOTtSYls2Drh5SwW5tCNwIr6kOKI/+p9T3Sww9Tx9RQa8pZrbU0FQW3Ns3NGveK'
        b'Z6D/ct/hWpr2eOTH1NxUrFmsK9TkxWTCKucNWRdY2Y2m/NRhYf5JO8lO8ZBA7d1pA2+n1Lakj8ITSHA02SDUUzcmNSkRd1VU+AgR1QkKZiCLjUuP3qma+XhpRpGwHZvI'
        b'pJ3yONxdpCTccXH0r7iXR6wYK0bTrCDVbKaSyjkiPjoyje0H2hWZoIAF85xdrBm5LGsPqYO9EpxT2V6q55O1iTdFreXEKFLpWqOrnZHEjqjNsRPJzTpIqT2pqN1JzPke'
        b'/JaEBLz4wlOZDsVu1r63yOVJkXF0ENS6XHJqEmFoJ72Iu1Y52HghsGmvvTM1iA+t/bFWF56cnBAXSQMKiVpN15NmDL32teOhZIgfIFolh7W1Df4utbcmR7a1TUBIoJQM'
        b'Bjm6rW1WePqPsA5tNZIC5kltHyNVQR2dtVy91Q+hKXpY1OcglVJPq0o52Z/qY8uheg4Jk5/Pq5TGcNREZSCqDlluJMgqrxJ1yPDu1OkcjTaSoRwoJtAqSpoKok0uEDPF'
        b'atz4VAKsgqqw5Mrim0Ki6EP2cERB4VjQieWcEo6lYl8wpU2IhUqpZJACus9epYJuHaPwIyJxDTq2G+tgjCpBD98cbMOiwmUOtuu87H1ChquiKkUU6gMZXMtVz1Eo3wMO'
        b'0wr5oHOHVJoo1kMXoZ6l+1CVIpiIUubQ9zvfBTnms1TkM2ttVGATdlIx5+ZsAa1T51MdV7KJl6hCo+Aa6l662EdBXN6odwFJVnBCTbJAGwefAKLpskJ0cE8fNZgxFjUa'
        b'DCiYy+AwVOELF8yw7lQbjGqi1qLcFQdRBcpEl/HXRfzz2I7dWJe7tCJiG8pbkRq3dm38ttQZWDvZsd2Ug+PuE1AVajKjHXFgCWqTQFeyIRb4oZeHCkMn1JZM0S7g1v6x'
        b'MooNpKVSkDsW5S5DJyPQ0UG1OQoXoIR8JtFbYSaQbc2h5rWj4AYct5LMZkA+V0wXSlTBY6udnPZBiYLMWX1HlKnW9aXrlFA7yag0RKEIhqJkIxMoDlb2uIYlgBgAyLCo'
        b'8DhUuDToMGrQo68xhhxLuIJ6UT+Fs4GGaFQyEh4SAbNZg2oCyZPBg4YSOlG20WpUNolBDp6G4kSZJvlQIWpeQ6cLLlWGe7+fIoTgeXRKR+6D8szwzM6DU4FYg87joT/F'
        b'aLX3boWMlNTCWQ8pqGUNLstrQAUlFZWpi0NHJajEYgZcGo3qUZ3laJJ06jcK1Tm7U4jL+GB0XT4cwUgA56EEv+XaYjw4mZCFO7fKZy8JpEPFERxkBxoGusJVutyslkIb'
        b'HohlkKmyu/h6S30cHAcxh6hwkZSVMhq8UHB3nVWYoZP6IYoQ0sYb9ptVMA5rvQbsOb+33JmOuORAHwvUaw5tNFAR1UAb6lOgeiWzCzXnrERVNACHAtfMlfnbDaaz2Qw5'
        b'SkYb1AklhB8xbt+teUJ5Hdaq+Bah39pFO99ZZvrexNSe2pUvdCXYfasr3fKx6cLltvUnuMi7mZLnxJ9Nfbo9NyzsS5/V1vvGLFxRZBtSJKy1SBVB9Pst262NYt+PPeba'
        b'Mftk8BsVd47aREUX/jJl5XvmOy4ddtMpeUNq5//VZysVm35bLXrzh4/+WXNz5Z82pXx+akdqV0/E63WXd22Tf9xw76+5iTlVR1669eNHDbIZn3Usfy8hvTTs/FOGY7b1'
        b'NO/57tKBGx2Llz/Yf/6t+5dXrfvGwv2gx8/8lYLmxEPebwWI/xm2/vRrQU9+L3gldHfMa5G7X5nxkus3B5+4/K/Xdt3dfrFSkvTNWY/K1UmBAfNv3OKWTHhw/0aQ+INp'
        b'yc+/MPq5HUmCVO/bfzv3XMsTIVPuWxyI/2HhuJ9LErZM2vtT8oe2b7mvWGq898yF956pSOz1X9P9tzkf3N1U8PpLTxxa/a7wgfkvlW0/+98z76hJPH9rYmfvB5+cWu5x'
        b'aNTr0ZdLAm5++dWymiuN1ZJt/peKZVPeij3yj2arpNPZkX8fa9t4L0e/8d43ez98wmtGx2/bn/jiiQMT0v8q35Jb8Uo4RI/e9b5L94frXvzTOwFN13/TtVze9qPoFakl'
        b'NbM4LI6WOTqEr1DuBMweBDWomGXg1EbiRX8anRxicSLwCkdRM01sXq8DXZAVyrhC0vnlG7Yx+83h6Qd3Q7NsgOiHxk0uOUDj8MztZ2uSiAhQGapE9YksDer44rjB3CRi'
        b'X7hKuUnmQT01H7lCK8o4SFH6GESCCh4BzqMWZmCqPmQ8KHMIda5gxiw4OotWcCy6ZU/MbLgpt9SmNkH6VE8aDBgUhWrsBuIvl0EhHHEMZlQiNejkYgI+i5pivVGziBMn'
        b'CKbyUM1QJRo3wqnJO5V0Itt4J2PoZBXqQNehilnHbripak3NZxZSaj0zQnk7BrNq+MGlQdazRmhjLCpX4GrEYmgayHtnOe94eypmMZk5gQp80Z5QtonsedS8A91YgJqo'
        b'lW/FHpRlp8mfIoFsanlbs1jJDILy9OwcHeYtHjBftqLLjAyjn9OX+XpDHepBuU5DYYmc0XWxEyqOY/li/Qooo9NmFmrAZ0sAlh+MVwrdUcFumskW6OBOksVQ9mh1stj2'
        b'7bTrUUmwB8p38puDKhykuAbuAusIlCnVe+y8ZJP/TozdMRUiYxkRCrVZ/Q5xSwx4QwFNRBcY8iSF3VQgFurxZqYkZVz0QCwkKemEkIIlp5O0chKdKVYmmJsKrQRW+Cf5'
        b'Z0mT1gk9hQWvp2NMcskEGlZFkoz+gFgURQJjAUswFwv2TtViYxuSPe3/qBzzAWNZav/gPLTHHwLN1PB+LfnhWlLDi4jtcjrpWm22ywzuOxtN6+VjNHTkMB0C6EiNeizu'
        b'g4sRqwN2hI8DK38/bJjCEBi9E+uq8kdZ7qiZQKmaEMU0XG69wc/3EfoHiRSfNEz/sPdXEHL5sTPhsEyTzHEANo6CxuWvtxma/AlNqSQm+orR6K1x9Hif5LxBebz3aWGs'
        b'K4inUm7YXpRBBYQwHaWIADVwguHanU51IpfSHPFO65iOv/mMmkgizKdv05kfiI4wx1WpN6oghYvgnILjJ3GoyGoFC2rKMMc79ymZ7RjmmKNeuVVLqP7UvlLAiaw/w3Mj'
        b'zF6xbivHYLFKZ0CdKxShYpTl6kw8XOeID6CApVZEIIJTTXJHoGuXE+c0HY6z1JFMSxeJfqoQygLxE43Eg9eIclgNLsLRQDspVECvLT4IRHt4OJyEmqlCZoguiGTkJNkS'
        b'6q/DiS0FhnNtWPrKdVvoC4JCEbcgmEOdeOOEDKihFUQl+CCqDIJSPABHCcobg3jTVyhzWFA5nJYYRUCvKstjD8pnotg1J1OC9T4KMjRyRop2s1pWuqJ6iix32VedbuLu'
        b'yNDcmqEBXZekQy3qJESJ+JW2cMJRqW5mOxNFbRK6qkodWYgbR/1Rh4nKGIQKoSQEnyn4lCslGHJ6AVi7MoPzdAje3HKCm+D+pi7nHOb4voUV02uXT5vGrbSPw50cNnXT'
        b'vrnsj0bJ3lyR6XohFxbm89wGC24Yy7F6BZJZQ1mOLfGa42q4/XwUF8UfFYzlzqv4jmOxUPkZMfMTFpnlUam+cTujG5WMx6IE/MtQymZiu98q1iA9pkqGOZ7RrUQ3huP+'
        b'acznqK8ShaGY5kLwgfMWQg/kotyFcDR92aqYFO/UgzvR4Ync/tmmqA11HKStu+FoyFlx+gJuTVjC36fOY00O327J2UcF62L9fv+PW0042qsx6GwqGSc1/F88HFUhAKKO'
        b'1Www+6ELncdq48SlKsXRaTq6qpw+KAfV4GvoIpxIMcIykgW/CP+WS19ZnybmDFeeEeNX2hcaGHBSAXP/lrikSoyg3E01pyIYHCw0WKEqSXosZKpyjdAtKKJLMsGSwM5K'
        b'lrkbpepywpm8O1ZoTkp5lvZ09uA2uT+WCFGrMSeQ8NYCuPBvj2cqIvs+kG9P89ww0m0yglcGjSCp5aJFZACl5tBlIiD1XwAn0AmmBefOspBgLSV1GV5cWIODjuUKKntk'
        b'YOk0HzoMoUsXS11FePmdIgnqxSiPosIqRKhPQvY927XcWnR5EVt6dZAZLrGxxVJJCbT54kXgI9gELa704nyUAy3Q4eQD3Sb78DUddISHsv2r49ImRAnlq3B9D3zvGR0i'
        b'O2ERYtHXfe7Xiq+OHT426dhYq2fCn5g/zWTUs39uaLh4PHPa1CN567f99kZF1M4gvxyX7i2vXrTUnzk6ssDlqeB/5KR8iEbLIrd8M/4XnSydHYC+rmraWR+ecvPle31X'
        b'X+lRfLWwO2LWj3vb3+m1Kfny+Rdn/ygo3/TCC1HTDd459t6zE98uO3l/wc9dqa5vP9OU+9y6SeGXt2XlHL5YmvLDwg2OC9bfOzlGFvL588+dcKh5bo+n1djfJnyycX/I'
        b'y7XfvSPIK5Z6/r1znf2fzNYtNB8b+dSqv7+92TT3ZuqspjM+m55fGTz3XOMky5O72gxqy9ZmVXzrZ3Qm6YXP9CLeaBt3yWyOq/6OU03fyF1nn5g5u7khfuqiuSEv1p6c'
        b'e9LLXSc9f5zLm2VWYdkZiSGKoMjbflG7XtOLuJH/Q9mad49dCGnoF3T5zV2X2OV54+yvHzcd3R/aNPO7sZ2NOacsNiXf37X9nQ2RDyI/vNrE/5oUL5/p+vxPNjuSVnQf'
        b'uRZfcmbq9w42z9yT/umsZ23KX1113886P/GDuekRR/1+OtXwQkta950VeU99XpD4w5NBM360RmnfcJ+cM44xkz0wSnOauvG+fWRHQm5a6FfS810HEzsb/Wt7bn96sGvl'
        b'/bCvlr9+p6ZH/PGUmEniDofYDPfiT6aHFKYdOmD3sqxza+efZbcX38j4/uV3b2f+6NL8bJuxs+v8hty6r7HA8OnysNrajsUJURHZ5q3Hw9zLH6wubJy4Z2cwfFUV84NN'
        b'2oIdv7zscS/4+OherxP//HXu5+31cSa2V7s/+r7zJh/9p/6M8slVTRO31eW8l2T4TvysC1unKX46VRF202zxEb2QH37Laaz55ErpoYt7vzyz95uEgCbv4ymnel3XvZFT'
        b'sUMx44L43uJZfq7o7IMJb32/wSlj4928Pr0vZkRdl918atKE9wTfzXZ/ctKs8XsSYw7OObNt78fy25Z797/6zvEl7m+843+94P10t/qG7my3PX9u0v3R7C93+9fczN82'
        b'aXXB5K++CB4/Wv5DYWb/kwu/fnPNL+sjRvXmTey3tP/u6+Vz/3n26ZBdbg+++cuixaXfh4XqbjN532uLn/ybmf+ce2+/zz/D9Ou/jG96Y/O7469H3gg6YzZ/8bLYc3bJ'
        b'H+/M3nt3wwdOP36bPiox91JWtWtO+s0zZuuvus6TWfp5f2Xkl3v5quuNavuK4nfHV5itf+AdhG67BxV/Yn/pqTe7d/v8+GqJc0eKj/8P9VnlPRcCnl9Svnv/97dcd1ee'
        b'0uk2/Njm1V2fiZ5zev/nkrjp235yb/5Xa8OY9591g11/mvOg+3CSOD7zQfay9W/4uhyO9Tti/7pIPvo33UveB/+q+MbTa2lUQMz1kzMufYT+KTl0d+YDr3t3Xw4/UOC4'
        b'pvdIQMTN03/O+GrH1dJ30gJ+Pnrgt77xCcadlbV3nvzZ4sBnX8ieWf7eN7d3ePzU2u7wxrYfuidPCuzI/WDhhR//GTvx7OfZsubfDG/P3lz9+ktHdp9dYpz//vuXdn25'
        b'8QdZ/RTPL8ftN69zrpvz3FP6a7c9MHnnvZX1N9+U7qCMJahsA7pMGUs2Q+1Q0hLCWNIbRVVRe5Q3hoWK1CYOqLALNlGN0ywaKoiihzIhfzBZJqo0oSqw/ZgFMnz+SXd4'
        b'q66aOAtj0dlYpof3Qb+uUiGFftSjobGi6kNUH4QjqBpdVt6jhzq0hHx4o2xWWj9cIyyPFH8tYLMmKWU81lrHMxmmguIT5uCzuArqVPiEcGUUbVDqfDgtJ6Iu2ciZuMtz'
        b'RtAvXIauJabNwndEQ+9cuSMRdBuhyCHVX0qO+g4aagO5Qm4OXBZjoWwPUzOPT4tkCnS0OS5HHCqwhV7GIoprmrlH5msrng9HOcFWfj5qTqS68YLoUVjxd/JGLZOhgNTu'
        b'hGCGB+qmnblkE3QSKDd0NomiuTEot2Ool46UwkMigRwHaEPNS6BAJuR04ZogYKYZNbPsxSfOFeXlq4T9VAYd+JAxQjlYLIg7yKwOJdBrAvmONqiMAJxQBFl0Es6xcJgj'
        b's9EtZQFZlg7e+O0GgvXQgkoYW+MJI2O5rTccT6Ypo4XoHJzw1+VMUaswDZ1H/fQFKBtVGMh87L1Ro5jwYOrALYHQBJ2gXT8vAFesQwbtARLUaCOGCz4Ej12Az8xTiAEf'
        b'rl6EjsgJ7KQ+1kR0glA1ZwDHBZAPZaHUZmGHOlAPqaJ+PHRKoZV2ghHqFZrvC2cNzEd5tnao0U4z65Xkk1MNAwtCqJQMpZ2j1IAwSp+3JcYNMyshZKD8zczklMFBhcRR'
        b'hiWlEwekkI97wViwWQrddFDDD6AiuT/PQdZ8Ki00pEE5nZkxFtF4mmLVo42UDq2oHrdChxtlKUTl8e4MQfImZC6UDTB7omzG7jkeZYrQJbgAh5nN4yrU2MsdvdFV1AWl'
        b'hvhWjjMWC5fuVK4Bxd59Eh8H3xR0xYvM0VPojFzKc2ODRavxoB9l1pfSxdBB/gr1eO5BH2E8Pw/McgOX0fkYGYGrhkyoDqAoksaoRLj4wHbaxd54XE8REEZo38lwGJUg'
        b'jJvhFrW5uEBtitwbXTO3lWJJCpXwqNDSNo3lv5fgseyAfB0OtcElXsKh3og1tFdDg1DOgBVPbymz442FM3TULPFsqoF82VbcdvI+is04Ca7QR7fjnunSMFIFzqBmKvNV'
        b'LB7tHDprIbHBPZHiKxWshAY8YyoEuKvzUD1boUXoZjhpj/8ePwee03cRoDP7JawrClDjNImj1BYrMDcIpjre+uIEcagW6un17baQZYfHyFEB3d4MFdkEFQojUL4Oy3XO'
        b'kS7Hr06ZAIf9iTRXz0P1fns2i8oUoRIpXiYdUCojBevAGR46DRaz3OyatEUkfrQWXVVb126gBryD0WdPoyOQI3cMQrnUKCeEXB5dnIA6aF/JUeZcGTPXi1NCOYmPAA9y'
        b'MzpMB36ec7rc2xaroCg71dffEa9+J6EeH0Rrmw7nzemOgPfbHg6uc6glFrWwVduLWsZgDcMbMlJJKJwA9fHjUe4GtunoR0K+L1xHGRq56ehoKJ0M89EpuEwl/MlQTyX8'
        b'yXg3IZ0XNAdRIFgs8zYOMgtniNhuU4JbeZjUNtXXiUdVVpzBMgHejS6lssVyFYos5AQhlaBFHKaLKpdW3wJvwnB66hi6pJeJ9OVwXGqAWuyhi+zmp1OgHd801lRki4qg'
        b'gY1zMxR64pHAl9uxSn2MiN7reMhbjdrpot6CikTU1orXZAW1t+5iGevTD84jDpx0VLkcOvAwjeK34WnSyAa/L2UMuSiGknUcj84REvuKpWx4633HYTFfhs/MXBu8RuAc'
        b'vg74LKINn4uPwTZcaRsfvBRv7bIVcLrolGBhGGSx4M4MvE1dJ3GuAd6TVxMnGp0iJgJhFJ4j7fQFc/E2V6eCF9fxgJsUXhyd30r7RAbnnOX01MLbLN4jL+CFTvZJK3RZ'
        b'5MKhPtonc/D5WMU2e+i1pMpIJZ6+qBuV0nUVSTAylFsl6VF0ZileWZ14ZvgwhhtUGYZ3/XyCbwrH0WVOsI53CIdmRrZ3ZDTCh2yhTB+XcBRyd+GPVBsyh1NCVA1tFqwL'
        b'W0LdZQ5xUEzPIopZ3ooPG6rYNsdjoSDfyc9hqVBpvkUVUEHnHMqZCg0SxWzoMsJ6tHAKv9wSrrK1fgGv5FY5FDjwWLwp4QQW/DRnO9oez32ogzUHzi3yTiG34FO/UTgj'
        b'AC9GFrcKxQ4M0910ExUKGKR7HHRRw3q6AGjIbD7eh5Igz89e6u2Hd3IZw05esFiMLoTp0gGWoBYCokaghG1cB2zWUL2OIhTP9XYj3aaCUneSwg1tSOoh0KLntDqZzYnr'
        b'eE9oltDbHFK84dhosveOwksVXVwA/fRwtSasFIy/OtNE5S0h/NW4J6roQja2QE14XrD11r2KM/AUoCbISqGdug1vRuVyfx0DKd3Vy3h0fKUB7VSPSd7kqYnqLWWuUH8T'
        b'Q3P2laLy4bi4BHn/ClykuLjQuIIJbo1u0K5qgL8bKpPSBnQJCRpMDJs0l1AurjSZ1YRHZxgWfehoNu/yoHqfxGYrukoORiF086hBjC6znbMHLrlJIA9P6tEmdM7rcYK1'
        b'E1Atkw1OobPomMQR9S+V+vD40Wt4WZqgatp9Ts5i0krUuM3Ax49MFPywBcoS4i3h1hIaET0e72RnJVKO89nPj+PwtD6lS2eW3jaUL/eHNicDG1tUiI7QPds0XojyDs6i'
        b'XWu1MgA67APtHR3JXlCOj7Z1cIEWCS2T4LQEz350IZ4TSPlJbpvoCt7nA6VyvMdDrj5tTFQSW8BQJHLDs4WRr8PZRNQgcXCUomNwEbdHPElgfhCVs821fjdqpzw3/iHQ'
        b'7WBLJjNeu2Ubp7DLFdC/Qu5kC60T0BEvKdmBegVeeIvPopf3oCsEJcbBH7qhzYrsDQd4KMXyeykdS/LCkxTjWDJ2CMYxOstUivDFcrmjj0KqD7k64/HOLhCgErwbVtGV'
        b'tu2gSpzeOM7bxIbsbkbQI1yIytzYON3wsCBh2WMJtz05jmhUdv0Y6igMXWEsc/QTQ+UiTrCHXwwnZ9Oe3GstoqHa+CijodqpKIedbIWzRNQ85+NDwUooVMkaKJeO+u+g'
        b'2YofcZ3hUbC0WXEqNfdTb9A6YhTT7g06xNnqUUBhBlBswJtR3A2CvmFBsQHFBKqYxobrKUGKyWdLfNVCMI6Qlj8QCC35cQ8EeuN46+8FJqa86QORwOA3gYiAGhvz0wXT'
        b'+XH404T7gt8ERgSA2BA/YfaLQEw+TxeIH9jwxr8K8POm/CTe9DfBi+JFBhT2mAIYExhj3pS3+lUgnoB/kreJ+An4u9U9gb4Zfhf5Hf/VyArXhSCO2DzAZek85N346gR8'
        b'LymXASLr4TIscH30cInGP4olej8InjaUqdBJGBW7Nf4+k7yZt/pNQGr7q+BnsYUev3esFicP63kNUtZHDZxGOvKzeKgmEPsi0V1HcDNlcB9bajqaRq4DfjHNge/mSbax'
        b'v79UhL/RsPJGwyFwJanxHE22DvLw8vTzDKIAJTQ5muGVxKtBRkgNU4l7ijnpLP5PYEQWqTuomMxlHaWLU08gEitxrH8R6f4HP90WzxfwxiZ6KkASPKU5Zll+YOGuAhix'
        b'olcN8GeRUHV10iHOgEK9joFjLgxjpBKVDzHqC7jFm8SQt3jhsKx6A+VPucHDoUaEUXrKz/oanw3wZ0mUIf1shD8bK/9uovFZCTtSpa+GFLGIGq0BKSLUgBSxLNSNmqmG'
        b'FBkfNUENKUJgSLioyVHWvwNSZEqhOGqWGlDEKEYnamrUNK1QIgS8RBNKJEtqc8eEwu9Q0uqV0RFxafedhuGIaFz9N0BEFrBM9dlSwR2RR0Cg5x3hitkrUs+QWV9BvlXx'
        b'j4/msYClWs7+XRAgyocW/H6YD9XraGanC4H5SK1jKTkEkCP1EkUYCvT0Cwj2pPAe04dAawStXBkYnTI4n9w5tYE0+HFudVFjYKgqct9qpFLVwBiD6yzVH1QGGYfUNzXR'
        b'NVSdk/pn0qK3yKWR3uGSeo3c89/BxNDK7DmcpFaHMTzGQslBOXSZmAeroPvQWahkvq9GyLKRoMPR6Sk8gyarskEdcctfLxDICYTEfe/phHbcK/x29lMxtn+VhRvEfMp9'
        b'lzl2gSu3MFF0rS1ZyjPJtWYJqiSGqYAItWkK8jaOQN3ZqQoUoZlYI4kG5MuaHJN7rYasr8cE1jDTVaEPj3SSka9vBgFsjPyqLjKSLxH0DBKD8V9HzyB4wFPEj4ueEUVr'
        b'TOABSDD/fxI6Q7UQHgGdoVpIj7xjwWNDZwxemyNBZ4y0xB+CZaF1uWq//3dAVwxN22IZBuE7SXIAyb4aIZdI/Zg2UNRhcBeDxlkJcUGOCQZbgY8K25HTfh6FLaGqye9B'
        b'l4iL+R+wxP87wBKqFacFV4H89zjwDoMX7WPCO2hdwP8Dd/gD4A7kv+GZODr+wTQUDp2D+hkDMAOaGANQDIW+6Ag6rGTaHYhKRv2QLYE6uLIgLsg2QyAnaA37l0whNOGf'
        b'3t0es+mJt59848m//Nb35FtPvvvkn558/8kbRWdPTjnadmTaucYj0vyet2uyZhxtLG/LdTk65czhDh3u8J+N1ubmSXWYESMX+ibZMSQAqN9Do2kJnRu1DXq56g9gAaB6'
        b'aLEfAAOAdgdmfatAeVCqSrt3Qjc1cFLPj6M2cDfInsIsKILl8yN4F8iAM8z2eGEUKiBB0N5QKh1MZIdqUa4qDvTfiYlVZ8LbP0rUWaWZES/WJon8/nR3q8eSgD6f9HAJ'
        b'6PfmvKf28CpZTEu++wpdTpnvPuxN6mT3qSOcdcMS3MUPj8+N1B2yLiSqtbGSyGi6Q6Q0CZHTYiRKKU2XSml6WErTVUtpelRK0z2op5TSYrGUdkCblPbwtHVNXfH/iZz1'
        b'wbhdStFHmcidiA8LklH7vzT2/6WxW/8vjf1/aeyPTmO3H1FASsAngCZh2e/Kan/IlvF/mdX+X83FFmqVAM2U6KjV46EZZabLNCC80LlpDMKL2NzhGpxayBLPgrwgN1wa'
        b'oMLh8iKYSIQqbD0BwiI5qCKOQN7roxvQg1ppWHf0VvGgJOtrdgNAX6moklYhmHA+yI2gz1Kd2Y06IU9BaJNQDiqep+Yep0hcsR5asLgEHDoF1frQixqcFUTOgCYD6B2A'
        b'8IIcL3uW2gE5SkZVHS50lt4+uLrczUpBRDGLAF42WPiFvliaGGsPx/0IoSvHBUp0odAdLrCE3nPbSZygsriQNesdNqCsdetJdq+Pny9qDPZCV7z8HB28/XApTgLULpmN'
        b'8gODuEmoyjgBnWGR2uNQLxyXz96GMlKVXBkoP0hBpCLv0U6DCl+3nuSrJs9OJUmqJyB/JqojzsQwlK+LShNNFC6ku8rQOdQXhG+eBzn0fuVQBbPn1E3fHKOL6lagC4wn'
        b'4xLqXyFJNU5E2bgjhaN4dxuUwaLqi3yIbxS6dx2EQjlJM+nn7dANdJVG1X80TjTvOm/KccvCEhaYBHJxX/v56chfxVeStl4NOdFmhJxNPV9J//Kpw8tWP29x++QxHZuW'
        b'1OkWC6Vnj63Zsmmm14/PTW8cNcM12fKk6Uvv/evWg/6oF2ymfIrPnrDSRW95vBtRYrPGv10YeLGiZmGnftO2d0Uzedu/yXwm1LSUOJWf8fJa+F6udYUk9E+79dHYyX/9'
        b'6OU3xqZnz4MvX1z14i2Tg5vTP9LdYD4+64X7M2yXynfmL/wk5sfEg31fuHwXs2XMxp4fJN//IzTgw+oNbzi9qyhO+/WZX2vemaj/wr6FX3l/e8hhrI+37sK62NZ/mWS+'
        b'7FNomSk1ZUmEBUK4PABJR0N8oMgwAa+RHOrsFSaigiF5nw7+AiizgQLqz92jmCkLgNNyZd4nOpJOVZ6kKSmD0zIPeAmgbtNuqs746KMjgwndiDqCThKa5IIZ1IWdAr1T'
        b'1HOF0ARPRVUCqNyGMqm72HwRuoG1HXSWRL4Qf/HEcFrbsegs9A/KNoVKlCuAlnlzWOpiF16HZ2hM7UBALboMPeqgWjinzB1FOT7hrAlksebi9xjDTSG+Id9XfwmzB/eh'
        b'7ijCVoxurCEBMIStGB1n6Yv2O8bKZkM/3PAhG8BVDm8VxaiLXkqGivnEigwXndVmZIUebbV4bpqdj58Sm+2WBW6A+SwhVMqhn+p4+2MEqHOpnQak3GYrStGMGlGtgczX'
        b'e4R0TONYJ5cNw/njJP/BbMg1j9L8kmlOpFCPUurqicXEK8xbKCl5if+ZfBkLjAV66vzGvZOH6k7akxj1HyeJcSB/UWdk777uyFy2WnIVPR9L8bxlral4PqpJ/6V0RazC'
        b'3d/6yHRFbRrbH8pVJH6K4bmK0/wpCiZ0o1x0SYaq4dTvy1hUpitC9gEFcdukz5tm5wWX/VWIBKiVi/BwF0q4qdAshKygCcz507QHXaMZi26WyoxF1DeJXbq524KlIt5E'
        b'2SwXcQrcoueAIB6vZ24ZntVhhs9MmMsAW3SgMMkVikiuoRMcZ+mGzkaUSgt1QAU6RtIN8YRw4pzM59NjKBafQx1wBmXKU3iS0s6h3Bh7mrQ0OW6jnZRkGSpG0zxDVDCG'
        b'JlzFHwxFhctppqEyz3CLHc09CoIKqIFcdJ3mGiozDbPhIktCzJvhHgSlJMcQXYhgaYZhk2iBizlnCZVj4AL0k3xAIzhL0WJ4dDZSmfKnzPeDdlROc/5QgR7the83Hecm'
        b'8G+nGjiHGR8We7JcNy+bqdxKrsbamAtbscZ5A/vj69u8uSLubqh+WJhPtkz87+X8ZT1ejtgNXc0cMWIpgYqwsUrSEXu8jaZ4+0GePZxUUh3hDbiDIJqQsD0p6hLOxrKL'
        b'DBVjQU2CO2x1rAfkmASvhw7aoFIvI86K0wsUrglLiNyqz1p5yd2Ss+eSeZF12IQe/dUMFQPLVfWGg/L8UhTcRGWaXwtihF5QlJoigS6SxbfBmeTxoc41tMhnTXU5Q07P'
        b'29g6zN7TUsEp8+5moMrdLO+uhQRESXhrmyX/F30q1NPsUzK1jEgwnySdpt3BDQOSeTcXddPZPQ81eKIOdJok37HUu92oWUHj0y5CPTQoU+/OhCsz7/AANNDVMh53V72E'
        b'4/ZBFkdy787OZdmrrRHpJPVOZ9NA5t1hqKdiWzSUQaM3LpVm36lz72bI48JulInkZbgGX5R8oQiWyUd7Wnz11WflP1dkfeP1nJHpsm2ZV3OWLdOxuCCIX8OP9tu/LN/5'
        b'8KLT+n9viv1b4exN0W/ab9zwxu3JbVvWOm7c4LilJ/1Dk1b7F7+u+mrHjEDHl89+f/brqncO3N//3lHHC4e3TLo5rWDCc07Ro2a0B656c/aY903uyuxen1YgvHi4VP/7'
        b'miJxZ4+jhZV70Qd6dh2VRy9L/C6WzfzSICpr3u2L76+c0qT3VoPnSy4R3zfkfLyyccyD2+O71s7dcXJ+Ylhlx1STG3/K2PyEw+VEyYZ3GuIv9gnzE6eNbZzRu/b1j752'
        b'a3Yr+zVh06+hvjefORh58rfjP+19ve0l/Q+nHZrS/uRTXZ6jfhofXhn2N/GDZ0bd+fuC33Z0PHtqQ+MXTbLyc7zr06FrE78tDyrZuKPmynPvrfOrXBt6c2KXcOyiU8/G'
        b'P//B1jofqby77tDP5yL3vW3+5rbsAucv+gK33nH5+y/PvXbgy9zPU7KLXLtsP1nv/HP5Qi7mVqTpPnTFe+Pbt3ze3Jry//H2HXBVHcv/55x7uZRLFxAQFbHRQVGxd5Su'
        b'FFGx0EEUaRcQG9I7qBSlSBFEsCO9iCQ7aZpiYhKTmJiYahJjyksx3f+WeymWvOS99/+FT5A9Z8+W2TazM98ZjyqN8I9dSyun37GvmX9WP74ufZHG3uxKoy9T9/pZONU5'
        b'/WAaXPaLyVeHypuuGtwenz0+bnZ4qdGuHW8F/nZ/7vyCSzEX3co3hk5InHGt4Mu3te+vSqttXlShunjNrnS7ipd/3//aN1//bF9w19N+l+5PJdUB5/btVM/q3Cm66l1w'
        b'/3vP4zun795t+vInJZYZ7jr+a3cfO/jDqqIXQtDZ53TeDS+qSa/Jfjltd9b63frv7wh7dckzv/l8vsR57AaNHxJd/c+o+E6NWJs4Z97zg8oe9xfMH3wrKOap91cmLJ5X'
        b'd+nZBw+6Vn9z9vo1Je/4ot+Uvza78Qt/0e2EBVo46XSlTcanOQutajwz9h+987FhzbNzfwv8Rctt/wOPMbHq0+p/85mVNunPOtVLd96qnq7x/a6xN365smNDc11slNbu'
        b'E0E5N7ZtaLYyubV6QuTbx2cb3/hi/3V7hwevtW56HefR2gA+J4LC/Xb8/Mfx7MrKuEWtB4zK3/hD+UGS7B3ZxCNBrrtqw+d6vn1/YNvHM1/a8+3i9P3qjX8u/rQ7WPrW'
        b'c8njuj8ygYQJr1mFVw9OXL/zJTUjXjb+7Q3XT1rCn2OX1m1sfsPTZuobu3/rfjfg4y394ctj6+D8iiWOycouOurvGb06zuDnsQVb7e790bT6/aNGx25NqRn/6stNLYXX'
        b'ZV+7q1x4+XM1h6J3tcN2tg8U/nrxnRnHlnSMD+uf95tBhQj6V32XEG2Ys3qL8hvvLv3uFuidMP+2TevVao0zW21sc29cXWKS88XnnYcsYhiWLRUG4BJlvF1R/2PAbIYc'
        b'5YAt9SIolI06wxrCsmGJMpX5TymHQjSAssNG+S6hcLZpSlSg2T/Tg6LZFK8IJJ7g2aAG9dIiLFDZWgNLOQRtJAANnw4dVHYxF5xRG8pnEDQF/MwDcphYkOO7RTbMt/Bc'
        b'Epxk6LMqdCbBguxuqBvOUPyZTbyFKz6FLAmmSA4+C41YgDIluKojcIbphk5MFTYghRMXOQKtBI5QUWGRc6y1QLFmQ0AzE7lhbCTKiSVAMxJSfQhoZgrHqB31RMiJY9iA'
        b'CJVhnJkq1NAuxECaixw5IMeYof7ZDGY2K4VKNqFJ6BAU0BjaC1EvRZlBAbpMK443ghL51/1WQyCzQhXmKmjQDZpkqDp0GGc2hDHTQUdp4S7opIA6IIugzIYgZj4HmKKr'
        b'dqEXASCh40MoMwXErBFO0BkyaR0v24Zqh0BmcoSZCKqYQJuqBtUUYaaAl4kCKMAMtW5goRzxUKym+LB5cHAIH4ZPlmYqY6ngr9p0UA8BiTGEmOMyBp9Lh7wwaA+FnCGU'
        b'2DBCzB0dpH0bC6XmcuiaL+TITYTKZtN3MlUeNXpKPW3U8SxRQo08nAe8KhgKqm+vD4OMDAFGZkMPwYzssaaEmYrOqoyAntl5jp87BDzrXEs7tg+d8aawMwY5gxxUR2Bn'
        b'AaiPxkiPSTIksDO8Ds7GEV4b8iwgj2DMJojF6CIq9KACtCYWoC9RdBlDls3Qo9gy/EEdbaijOaQSMJYCWYbOQTVFl1miE9RYfhe0pxBDfAGz4V0Mh7Anis30MpQPnegY'
        b'gQERRBWFl0GBN1vY9egIOuOGmYTch3xF4VVI14KzbDUUMHRCJLRThBk0bGX4oFLUtckNdbg/5AlpFzQwc/laVA1lUoMpCpiZHGMmODG4z0FUiw5RyFyFZAhjpofrJcO2'
        b'bg86SzBm0v3DCLO10MOmaxlqQXUUYibHl+2FZgYxOwP5tNnLIFXXJJigzIYgZiuhmM1EzJyeNEZpcpzZEMhsxSxmRj+wkle4b8L7UQ0FmUGPN325VRtKZLa0p5ierQxi'
        b'hg6H0zr1Jk9ym+Qtx5gxhJkSukC/84OGGQxDQqAgU1EFQYOsRcxtFUpD6VNNxHRLYACzAzNogXt3J2C+lkLL5sFRii6bic6zTlzEUlmuwo0XuoAuMICZlhGNbWrrzfxH'
        b'LDSnXGyUVYKcP7xgMvLWCSrWEGzZqkS2Goow01krw2LZYTnchWFdUB5kMnBZNmqEtg1j5PiyR8BlJmZ0N9qX5DsaXNbmjo7qyMFl+VLWlIFZKGf9LDm6TIEsQ5fQAAMB'
        b'V87AUgLBlpkDg5aZhNBpscAYy0kHYZDiyxTgsnmT6TvM80IPw5Ydspdjy0ygSx4qtgkqMBdLkWWQ7sXAZZ5QSt8GozrUR7FlInRsCFqWglrZ7pqWjKrJ6KkRj2W5HtDp'
        b'rou3GM4QWsVWnBqD0JT7QzvhopfiI1TBRqPLqIB2Z8Uy1EqtBByhhN6bRaJ8OpO3KkO6lGAYFSWT6aiGSgR01g0Os+uuwhmSreg8LptOOyybmgGBHtNaz+AJf8kK5c1W'
        b'gNooos1Yn249+GyEVBk+C9EhAR+HqhTVRrbm8QvIrV+mO1vF6agEL8RLxI0mOV6GMG17YtnOXsvjYSL+OxWYNjmgDQaVGKCmGQaxhEwhbeg0GS4/3sY+ioGTBqBxnC6k'
        b'M1DbI4C2Y6id0kcwjXOzIcceKnSggDZ02kfuuG09amUzTQ4+WwvVFH/mCnm0+Stwn46we/0l5iPwZ6hLmaLS4SImUS5cdpOD0B6LQJvuQsvaG49SZTK4yNgHTC+O04Z0'
        b'UQJUJFFuCg5KgeCgMZ+jCvkWLvQkR6U4C2eE0sSrIXUHndxBqDiRZXPA+zrprzIcE5YthnQ6ajOmKTPAmXy/HYNyCOBskj0bj14osIKCVbIRt7ACVGNa1cvxS+uhilx/'
        b'YnJJ0XF6/Qm5O+m349FxLxnqQoUWcHGN1BMOWuFNV3u3aJ+ZDdtyuw9sssLzEG+9RT5uxNcQVApYtPBnJitn4JyKjIcs4jKUYMpo/3hOR1+0H7UkJxC9QOBmVD4KhjcE'
        b'Y8NLveVhHB5q9KdzaGMiOiRdvEeBYxsGsZlg5oQ0zAOKUZNsEuqR41oZqBWyddmWfBaVbCeQVwHzlZinoeDphcBCLhuNQbUMDku2VlQvJthdVGbFgmLUYvJbQRGchNxH'
        b'4XYUaqezhJ0px8NQE+Z8UK8CLjiMFRy7ma4ndH4TaiRAOx28Az2Cs4N0Hzo+/qgCVUgpL4DOqjOgHapdxTpSo72O4exUcSsUQDtrP3qEw2nXNfjEcyWHQAND2W1XZgOT'
        b'udRxHFygW9DDKLtzUE6v5o1SPIJhkODsKMoO5aFsSnpbOOEhmwZn5Ui7YZQdqtnN9pd2nyBopyi7KaiZAe2gdg5dl/qYcjUEaOeNTlCgXSwqptSahaqTRiLtcItU18qR'
        b'do4rGdw0HQa09nkTpJ0cZQdpznSw95lDHwPZoeP7hkF2MWrsZMjyhjQKsluBKodBdoOQRc/EaC9vfBhSkN0Qwu68Dm0U3g2z9htHU4jdQwC7ZFRGB8BwNqqR6aNGBciO'
        b'QeycrdhmU6ChLkfYyfF1+FMKsYP0MPr5dFs854cin6iupAi743BJjkr0hXoCsjMbQzF24/DI0KM6C7NX7DZsL2oZhtN5cxaa//fwOYpyYrqDv8LOsR8jBYJOW/Rk7JzK'
        b'EHZOl/6IeU1eG6dNfxck2vw/xMopq8ixa2KKT1N5gPM/oD9vS+Y8gp77UxAzpJwe/UKTaDYo4s6QN+DFuFRbXpN8L/kvUXNvqC8cjZozfBJqzuBhRcN/C5nLVVYY+P2V'
        b'tiOV+3UUcO4JzcB1E5RB/LsK1JyIoOZe4OUXkhZj/u/QbldxpR8SOOA+7n+EdntbYiXwmkqPRbZNfwjZpnj3wHBZIr0n6ZkBHY/cYWOW1ckcDSrtxOzN5UdsYTXl/8rS'
        b'H0G0+YvLlMtUy8aEC+R3mab8bz35v2rs30hRuChUVCSEWg4pmEjIG/UcjRzNHG0alFqdIOMokkwpTBIqCVXO5Egw7iLBXxmn1WhaStMqOK1O0xo0rYrTmjStRdNqOK1N'
        b'0zo0LcVpXZoeQ9PqOK1H0/o0rYHTBjQ9lqY1cdqQpo1oWgunjWl6HE1r47QJTY+naR2cnkDTE2laF6dNaXoSTY/BaTOankzTejlK4bwcH6dP/ybBvVX8DagNpYgq31Ry'
        b'pJg2Wpg2OpQ25qEWOMfYUIHClqxuqq9Y5uGrCGT/YZfwkO0kMV4amYNB6YZMbxJiSMwHGcsze6Y1+9eBRkggf80aVZhCUSezNV02wipQbuRG8QFyUzr8NiEsngZwiEki'
        b'0WcTRlv1jQzmYG0aFhSyzTQ+LDY+TBYWPaKIEWaHxF51VAlPsusZrS4clfCMIeZcLuGmNOyqzHRXWHyYqSwxeGckNVCKjB4Bu6AWU/h1EP4/YVt82OjKd4YlbIsJpZbo'
        b'uM0xUUlhVLGZSPabqN3E8mpUtApTp0hqxGS+zEJuhRs12rSLWEDJjQPZQNjJx0FBcWtT8+UWimxBprIwYqSWEPZXg0TG0HyFBcFqBI0wBJSb4MXER0ZERgdFEdCAHGWM'
        b'SUAAEQ91VCYLiqBwkTAWlQPnYr03DQ2LxRuszDSGNZxa85nL3y0nM2xnjGy0UVdIzM6dxNqYzr2HLAc9LYSbouSdUTclIUE7E2bPChGN2HaU5FsPVUG54l9yEJhyjiJm'
        b'lpRuITzeRIRwTbm2WpQryeD2i/eo7RMNaavFVFstShGPgIX9yv8NWNioRfRk27EnmRPinjFLwg0e7nJTOBoehZY7PGZ4dKi5KF6Sj7cxNQ9jU+lJ6/Uv4EqUrPMJ6iQk'
        b'CK/4QNykQGbSxwobKmTktHtC0Jqg0NBIZgAqr3fUtCMTNC4xTL50ZYl4TQ1tHY+HaYwyk2WxaMjKC0pMiNkZlBAZQifqzrD4iBGRZp4A+IjHKzI2JjqUUJit57+OHDPq'
        b'jNOQT7bR1gTjPWWEVw5HLu2v3beyOJ1gccWiq8DiRluajIvcv3yWSlPQfmqCn2hFeOKyHQaoHQ5DN7keTMDyggUWTwss4AhqQ/QLdBllq6CmqRqURfVNJLdXoXMPoDMk'
        b'TMd5jkvhUqL8qM72K1tiHMAl66sEuidLzThmAdCqr4faMQ8PhzluAbfAVSnq5wcPHrwwW4lEjjGc4BKofnqeNpdI77e6UdcM5mE5CzVCmYO9wCnN49dCHcq0EBLpbUEt'
        b'Fls6ZZCvCXm7mC4Bi5WqluY8NxPKZqJMiRXUQj21JbBPQW1SS3M4D408J3jwjiHrcSlUUOxDlWYjC1Ejv3jObL7SuAQz1Mac0G71d5baQj0WOMk7EfTx6JQnqsRlEHbP'
        b'YvHkUc1wscRyM1y0cnHDSZSNikWcH1SomBDDQWqpEGGzG9rlry/BeSxazhaid6JaCxF1y4pOckpunqgOZUChDRx2sJ8tcOr7hR3QM4HqjlEOyo1285xKADHsvYRTTxGi'
        b'kkwp7aAG2ra6eVqhcsVrnlM/IOxEA6g2kRjjoC4vfRYBxNnX2RNn8nJWqGvqvOk1x0ot5bGQCoep+v6AdDaTH73gMDpvA11Uph2Du4XqoBs1MMOCY1PJvdmwtYoieArk'
        b'ubu52Qhxi1BNAgyYwADK14c2aHPTQ/luUjVoQwWu3j5cWLi2o9q6KKKwz5LSCeFcvyrQ+o3ARH/S4hO7UM9jSodcEToFRXau68whzxkKfYiVpNs6aB2awtRQBgv+ulPV'
        b'sKTdpKQEvU5T0SkLzmmXHtSIkjDJ2Z3gStQB7VqYRh2x8XiOQA8/DVOgj5nB1G9IkqqgPGiMT8LDL+YtUTUqoq+wGD2baPGrNsTRz85iyQXTjZqcDDoZy2JhAIrI9S5x'
        b'Jx0YLf9qJ2SjPlncZDgCberks1R+irI7nk5ksq3d4yyDLpQKxbRIdIk3wIJuCf3QHC7hF+3qGxYPVYeqV9EuTEUDu9w8pbqjBx0qpycS9xpwNEh5ZOQXj91+Nq5r1tHh'
        b'p9nlJCWlc1AXJUUtkA4nqVltUgTUjvqWfLnWxo99waFSHSjhQqFHhYPeA5HZr7SJZWmYoVv3VtjO0gWyMTO0n59as+/y9zV2eaVz41TqSj8s2i3JySkNLF37ybhXs13a'
        b'Q5aGz0zRUJo8e/Pka/aVZ1rM9y0C5cAW8xbzU4aurqfVS6vK4+NQY+ul3z54sP1ASdi9LxuSgm9sejVLh1dzH+sTseG9oqivuSUvzf7yUEGlWcnngTmuZm+/wDs2Hbqg'
        b'Xbiw8Pf8U3HjVRZfbVp9UXri3o9b/WdrZZVln/xoOTdJb9Keu+aWX7zgdsVg96XOl/V8ihO+rT7z3lNHV8afeLf9ltIV75sPTCvf+aXlZG6RerWby/29u2K0n1rpHmD0'
        b'3NpPw7bqOWWOH3N99tng6+E+G/10vZYvaLKu7uo0uhfy1tnc4PyNRh/Pu3tzbsLTJ14qV+0r2rX47tnbl6U3lKaX+bzT8ezFJH/rPIcb93/Vunf2x5pxO+48q3Rms4nV'
        b'0agUo3/1+DUVdP+4efd1B1mZ3R9RvzoWtp0KvnhvSsd9WazSya/2J39kmWRzKv2VF9N7DHzMO+fN/+m1GTtNVO99fTd1jJeTcl9In6vhO6ca/vTqm3t//vsvTbqmEeez'
        b'8jOn+r6odR+c7n5uu43s/O2XxloeSuux+Tq3f0NdZL/q3c5Zy+7V5r6k1q4f3P9lxbmG5vfCP98dE/nl7QvjiufXRs4L+uPCXDvtHcHj17w0PyDqUpL7ChfUt+Tb14Xv'
        b'r3+Z8dvNF3/2CzZ+/UDyZ9bXnj6w23h68rH3sz+NDF2o8cmpqZ4TPb+dW3NvMHn7Cx8nKL8gC9xtfO2lm28s/HDR9w+S7S2f2ucad98xQ6Ol4oNl/VU7vlp1r+azxpfL'
        b'1H+Jfud0reaml3x/rZt1YHnOZtnCNT5ZVVftT1qWffhd8R8BPR+nVwa9YWA15jfN5b5VLQujjNuuLZ2g8+CLmNn7dZZn3rVYxnywZc9DJ6xsPaAmCAuUqIV3Q61whKmq'
        b'+/csRgXoAjH4XjkV7y+QL3BSdAkvLOk+pvDp2eZk5eIOnfbK+NtcflEMNMjdLk0LHqn/RrnrBZsF0MEub9vxLlmBCuyYolMSiKpQh2C2wJN+us/IjwQosltDbFRTcM4C'
        b'wRIftaUJZLEZhMMp/CHRnLrborw1VAWMcu2crS0pWFPXWJkL2K+CzkEN6qLXhtsWQq4bFMEh6BxW6lOFfrcqa+oA5BB/e7ikIhsJJ9nqmChM9pQri9GR2dDgtsbGBQ2u'
        b'sCa3vVLcUrg0AZoYhfJR71R5BOI61DnSnGCZM7uKS9sMOXJb5USNUeDJk8HsGrx4fDK9JXS2gOwN8lvCbQa0bWrboHfEFeFOVM9DOeSYsvvOAjFKs3JBvSvQOXysiyN4'
        b'yPYE5qvVYCUJ9k296A5dIKLmaM4YjonjxqEqVnMB5O9XKOuWojQOYQ4AypmG4CJqDMSUdvVwsyEXfp7yS8gpUK40G44sgO6ZTC9SmoiqZVDkQobETdPTBjrcIA21CdyE'
        b'VWLUNA3l01FYRYKBQ7uL13w4qEozCZyGk4B7lyGhV9KbUNt8XJ2njbXHUG2zLXnOdIYYmlAPtNKZMx7l7yd+xXBpuSOuPbX12GAdQ70TUcEaDdRq6+ph7eLBc5rbRHO1'
        b'8HSmmrM9O2TuYyeTs5re84qIJzvleXKjDSduHFUHFLpBgTInUbWeI+BzC4rYjXaFHeqXucPReeRqXrSD36cE2ewivBazPW3QnjAFqoddZyq7yptLDAbb7aBk0QhHkNsU'
        b'lgbFmIXJpuomqvtUwtWd3M9DH5xdS8cnGRqgFXNW56HcjbqOO82juuBNlO4T8ZTNHVZf+q4ercBEZxLYHClJRueIJhF1bZDINYmOuH7a9JxgODJC/eg+nd+KSkDuNy2P'
        b'nOIFa1J8aQwiEVTzqNgB9VBCK6Hj+ABst5uP0uCgFWlZO55dmNtJo9RavcdaoaFPQDVESZ+HmLGKr+YEheEMUVb3ofwtAr8Lati18wVUpkeUvYEOYqrs3RNPl5AOnBbh'
        b'lozQ9upGktBsIigYH00pGYjnwykKMiB6KDSwmZizVAkoD5VMYfbtfagddT5ktm8XjUoU1kNzUA67s+/HU/I8Zj/90VG579VOHi+LPF9m3ZCAcvFLOOGu4KAknGaoyMkK'
        b'Bun2hBnzVhdUsCsJOjTihhkyAsi2g2JnDxuLeEiTcD5OKprjpjE6X7SH0zIrNcweW8ggjeeU9wuzItEJujdvNF4ps4onEx1vNM1KnHKYMHP3JLrAtUNRD+6xC9ECLYQT'
        b'a2iIPiVOH06LdSAb2DihU2jAXkqKJkU0huMS0Glh0RSFp+xSqLHEhaCzC2g5dpCnzGl6ipa6GtJxnJ/gKMMzE9OkgPi96ea1IcuTDdVJyLBlKhroU+MgS+bHdE+FgHde'
        b'2SgVDaTKiJYGBpbSI0Nn82a5aQycQYc51IJyVOhUDYFSdIy47sSL8AxPXXeictRNtV8bY2m4elcCQi9ku4OdMxSJuMlwUmkNOuaIee2TTOlYpW0j87SQG0258Zw2KrIa'
        b'L/Lyh3RavdG+dcRmhYPLqNGD+Is8jpg6Bk6nWMgsIHM+3VZEKIvfgxpT2HmVDidQvZXrpLU2bjaWnnhb0YoQBaHmA7RtyihTA7dtLiofbh6Bu+QRJbbFViW8jI4uSiCS'
        b'EMqYjfssnx2oD6pHz5A1czBXugCdl3hCM7P4Weqkb4VOrYPiYVfWmM0eZOZEvXAKLkjJEaowhNOBUmiBPhE+/QrDGTXO40V5wYoePzYJMyScCvQL6DBKR2V0vFZunCVX'
        b'MqGToaMdOZ5GNRYa/71C53+kGHqcs4Aujvt3ap8DXJgary0QgIiEN+HViapFoHfsf0iUtKmyhwS9IgoRiaBC/9LE+TT5Cfw03pzXFbRJUC38Y0LzalOFiYQ34A1wmbr4'
        b'X038o4JzqwkSweDhJzz50aSKJ/KtRA5W0eP36I+8eHrIZ4GFEoOJfESUGR+Php6o/1djIWLFDZc+RE8XYrZNnv8b3Uwq1zttpHbm8f34Wz4Qwv+tD4RzKpzcB8LoaoYc'
        b'IMxQ3IPTi2Rr07AIW1NLciNmaz/bQeGl5VF/CH+redtI8+L+qnmtiub9Oo60Q36pahoZOqrGv02LU/xNlYAQdtv+xDrbh+qcRAHMFLUbbko/IzD8f1xzBK7Zgr+pETB0'
        b'lxwQ+eTqu4aqn7bMNDE6Mi4x7DFo/X/ahm2sDeoBivvFv2pC71ATLAkFZAmYBPSGcuhy8j9tBnXKYfxXI35pqG5bnxjiGyg6PIZ6PDANCo5JTBjlaug/mwTxBN/0xPoH'
        b'R8+4Ea5v/qNxj3f+q8rQUGXGw5Utd1nxH9bl9ld1PauoK54Evf37o1X4V4W+MNQBc9/HOCxSeOH4T6erGnUkEEBg/U9swoujB4z6AmCL9j9dqCqs1oSYJ9b5ylCdRnK/'
        b'Ef9hjdsUW0NwUBRRiwTExIZFP7Ha14aqnUuqJXnZXX3USGXfw45G/uNWaQ61KiQqRhb2xGa9MbpZJPN/1az/1idl5uN8UvLcw7oJkWfksdY3xTLChadkvXI3MDP4hWCV'
        b'8NvuypxKHt8VusWCZ/z2OWhB5x1Q9pDwo5B84BjqfoJjSXOF3QyRjP4tA3WAi9ij99AxHxUWHRDwZLeSpIK3VOQE+rccRSp3ZpRzycdW9j8dhPC/NwhiT9/I5Kc+FcnI'
        b'4wUF6m5B6uHj/rj9EseJLXjLsxuG59ujNL7IMRrHZ/GP8C8BAcExMVF/RUDy9c1/QMAW9b9iylhtoyhIWkvqJDICU70Oe+BUeHxi6lc+R2NI9SrkKmHaijBthSHaiiht'
        b'hRSRnLYRD9OW6LZItEWHUbSd6Mmi5WVClZUsjlzze6AGdtMPHaiSqr6qfMVTlETUl4L6Na0xHAU2eqMqZZlmvCpvMg9nb+BtodaAKtWmuSjZ6nPM88LBQJybOn84iaog'
        b'l96QMBA+cV5R6Ib/SIBCT+LVwnutt42fwG1dqoyOQ6d3IrlbiYGMzW6u1J1acahk+ApMibMMUUJn5qEMBjfswlLngCyW6C+MlKkGA9WjXBY7sAMVqCqcdKihqiFrXvEG'
        b'poXqIJBkcn1DrptQDxRzYhsenUP1kM4oU2EBFRThC2cgncUSRQNQzFRc9VP3W7lSYZTgerA0Cn1mYVCPLvjSj/U4aKdCnw0PHS5iTlVZQMXo0H6qJEmeDG3UHBeqDDmx'
        b'mMedaEGD9NVm1GJKbjMttu+0kXCq8wTUZADnmAroOHShDIbpgTrIZKGjFqA8Fkq1H1pRLRTYeFIJUrJF2Ad9+n6oOpE4TVBdg4rdoNjF2pYEciJWuwXuhPjMwYDVIiUo'
        b'skZHHpmgUsUEXTk8QUdPT37IDdnfmZqPLHvSZdVHpqatJ519vLWY6NlMbwfssl7hasXArKhvbZgMlS/xHA6SAZVzKZjVYnWwDE66uAwHRUKF7pQ4sdCuYzUR6kcNWJhE'
        b'geytQoNrZPxed8XNogxlMhckxyEb5cqIDbGgAjn2/Hhn/Al9M4gazRWxwVGJF28nhko68HFYhO+GAktL95Ghego20JfqqICYZPtBpdtwkCU0MCtRfsfRMWk4yJL2XIaA'
        b'cd9EtdksTmY/ugS5PpCPzuPUJG7STn0LJfqx/mTD4U/3m8nDiB9EJXSduCLiEccGXRwRSrxvuTlbJxV7ZlvBRXR6BASG4l9mraclz4HT8wmwxgMvjmx0jCFrUBm0Uwi6'
        b'RBfVWOFabfE6MQ61tbBx9eA5M5SlNA9ToYUWEIhyUZY8XFIwOiVHsyRBEyXJarhwQB6UhLdDRziJijAW+tGRRHI0rokb+9jYJtNQkwkNbXIZeul+gSqFcGqR707vj8m2'
        b'gvLpQpimvni90g4zNeq9Bp2cCeeJauNhg3Natr42K90TpSnDoVAoZ3tMMwx4yiAVjsQOqUlRxj5mBdCBjiwbcgSE6QM18k3GUZ92AA6hHOhR7GRsH0PZwSO2MrM5lAzO'
        b'oXAUN6xBJr/9plsRZGnR2WYJp8e44XnebjMUpWedD32zfEkgFESHsOfUev8E9LDdohXvB5mK/WA9NJAtQR+69egqkgQjXB2qMbcdikEHp5i3gQPoMErD2wPvKOX4uRwU'
        b'rwC2TJbDyYVWUOfuQYK5i4PwbiikUArFw0A8nnzONtYeSqhLhNmfI8I+04nUfAEOo4GtijBJwTNGm7mjbmigvSfHg68i1wodhjyBtnmJ5qQnOXi1HZfvXoqdq2nqqM0L'
        b'juLdWqDNdJ8zEa+ytiQxx0PL3GkcNO/Tp7TyXbJeBhcleKs9R1CoHDo0GdOKHI4GU/Sg1AAOSjjOmrPGs+8oPc9e8ZPifZxTeXV7nHqVnhZzIJC3iFqOcE/5JaqvEG9m'
        b'DxcZUYsA06dUg9UHtP3ZQ8s1JMwwZ34ocY/62FkO7OFrySrkhLR/1VpmfV19/6NeFihbSP6nijhui+Z+fh8fqx7K+eGtNE4IHZJTKdcjD6PMJz3Eed9UXRgRFh2WHBu/'
        b'OExVvrWKiT8AYqwAAyt2yxT349AcJ78AxUNFnZhau9igfPzH0VG+FqBUBO2oVNcNlThoB8+BU+jUbnRKX8kpCR+UXvp4BM+hWuqBCnUb4+OpAIgqp9TG1mW3EQWfuHqt'
        b'tfFzHj2KdAhRu6DGE6OQ0+qBkIMu0AVt5YFO4PPVwgbO4gM5f4ReyGSdGJ1F7fqR/dfXimXP4S7fqqsK8+mNfnepds2WkhLzLy9HXf2XzQevfHosK1/P9rqyynXDSIOZ'
        b'rYJ6pcRb3F4uynDS/Vy0ee0SnU/GFe5bevqNZV/uWxqe0xH8fNYL99+/VPlOzfGPPprk/l7jB5JgxzQLQ52xZYZXWi6cOHx1xisuabUlFRn1WXFe5o6Z7UefCf2B31J2'
        b'tTpDu6Nxy72iN22mrl5yLfnzZ3fXTNw4mOGd7nJG/4XKkOYLBWXVvzcr3WyM/oV/74v4xG7pPOmp0o4S29K765+7avJjxGv5V4I812+00bxt6F6bfE/b9fXiX0+mKt3z'
        b'eKanOf3E4qy8XMuKNcZ+NWrLfu/QzXhZmhZf5Tu5edNNn6YTHi3QG7NuaXLxRe+n13o6+e8wsXjqkuWBrhqrnxaezi+JeXr6tNXxK9yubamuefe179v7b7RH3fH76do4'
        b'/6pbphM/X7vrR+HZB9pb7Rf/Osbox1ebTfY8j8x+WOeQKTMa6/9Tis0rdyvNDH5s+LFIy3lnzpwbn72te+ZC7q4N9w75v/Hie4nF36l9vPu5M1+lrFkYuuuFL43P1OXu'
        b'2nivre+V3dLC3wr3Fjoa2sXf9xh4tnd9Yfe8tmcOjx9j8q7/i88IA2fu/7B4f8ZUa49jzv6LxDcjrkQ/E1226P62+1t8ap0ik976Lk/mP+Xa/iTf8OKrNs+nfNV8WHY4'
        b'UfLH0phqS79fjr2S7P6r2gdxYZxFbc9rU5+deP2t9vlXZ4Qs2n3ixkn0RrDWjjvLzx1sWfGDxg6XFUobB93Onlo8T+tkl2vO25KLzztu/PLQ7xPevvMc15ZfPbny15Lp'
        b'Pxy8ENGfcG3+hjX3596N2j/2yDv+D8rO7r35jdndFPuQTZNanpp/zdM7aXzB/s5zSYuvR2qeMr6WfzLuep7sik9n9StmNU+/oZOUfX1W6/G679Rvfbf+uY4dr0/54dj7'
        b'NlHeR795u+HLJa15547f+nbCraXPvXLoywM6J4tS7+2ya/1DIj7Wp7Y1Y8nvUpPoOf7X51jMYwEcxTDoZh+Gz3LUIqY78yVUFEV1bJsx51Yq1RMIXEzVHHPQmEPUQc0i'
        b'dGxrMoPwDcyBVKmlBbQR3Sre/89yKuMEP0d1FpmtwNyV6CejUbYcGgqXUKkcdmenDu1JCxKG9acwAHnsXQY59q3gtMhlWMltP4NV2A91+ORoR0c32o1Qr2rtZcqt43AI'
        b'8BGEBYCCkdyQOcjdc9Wh4mQplOI8uEdx7nYWEk4DZ5uGBlAZVUlrmED3IwBR2Ty5hhUuCFShJDNxp0hNolzdAXUcHOSnMM1eC945Tij0qztTKMAzEdUybVMv9KA+KcXm'
        b'CL7TUR6/GMo2MLjR4Ma9VH26E7UxjPNSOEPVeYaoCrUpQl3yqxUoZChdx/S5x1Em6petsrMdETUS6uyZsrnOAepl7mR08gjW7ySkKnFq6gKqjwlhusLzBDJGMenWHGpC'
        b'JZwEnRUcUIGYkfMI6rYk/gKIswC8wxYyhwHoCLCIhCt8fYZgyCgd6uVQZB0/poY+OiWGQZiXoctyFPN6ecTYA6jfAFO5xYSi/fE4iefx6KJsO1O9nQyxI+BpCp1GzaiK'
        b'wqfh4GT66Q4YmCiDfBcX6HYTUK0epxwnWIZBNqVjErTpExwrgS1OE1EYqyBhWrEizBR3E1VjHLXjHJwq4dTWC6hPaTWjVR8W385I0alYGkiwFuXhJlfxcCEZDwSdzBfQ'
        b'uQQaZZAT9Kagfn4yHoUM2lMN1DNOiufsYVcPKwkWBPp4dDgK2in6TQe1oGoZMcNENZBu62arRvgfQ9QpdoRq6KR5JkfYyOFoCpAruojqOT3ME0NpTAxT/ZWsnvgQDhWd'
        b'tJRDUQVUxwZsEEqmMewmzdAD+Qy86WFAKbsIpW5RmJbgsS+UI9DyV7AqTqI6XopXz8AoPw/MyYMhMOwcbuFRfDYOxYhEDVOGILWFCxilBvF0y5TCoF2iIlYjZJmw9ZHt'
        b'hMUbKDYnxiBBEZySEw9FPqiTre0WZciVQh5qMB+O8oeOQSEDVffNQlkyTx4G9sl9LHj40+oC8MDWywHGu7wZxDhzDENGe8EZqQLiJ/KfQwGLePM4RYdtHmRDhdTRxXY4'
        b'MCAcgwG5pjV2+SjEIpbLMuSoRTgFl6lGXA3VoosEYMgJFo6oiZ8wYT6DWpZDG7rAhjQ0bAhjqIjlN6gmtwLAMk0LQxjCBciiKENfeTQ+vI91EDh4viaekZ68C94WlN2E'
        b'SSg3Tm6pMckO96OCGxFfEDcmm367HB1EGQpDLEg3YL5I0HHUxTbBphQTKLD2xNs5Zr2WQirPSfGyxmJKL56PJMda1GFHcxRaQK4zHu1B4o3xvACN6IgfG+I01LGJuDDA'
        b'7COzC+HXGqrShSSdjI5brbHGC5tedGQsUeakcFmAbtSczAbyIGTslVpCMSabhxbeOmfF7GVLsD8C5cn2b3N/yFoHGvDBQNoVi7pNFbZp1DJtkqbCNm3qdguD/9/wr4c0'
        b'q/+9J8SbagRbE0Bt2ykX/j7hyf/95ewBTo+BF8UUzkh+a/LTqEbbmrckemgK9FPjdXltXuCZTpoA/9T/VBcJEuF7NS1z3oA3F3R5Td5QoLpteaBB9q+6YEw01wLRk+sS'
        b'/Tfmlw15bYEEGDRU0RSIvttEZEz13Lglgimv9kBM/hfU/qT/i0ipEk5CXfYbMBimQC4s91g8rD0mFAiwXUh1TbLFtsMUYfKG+KZqQnJoWEJQZJTspnJAQnJwkCxshHb8'
        b'PwhCgGWYP4nK748hdfjv+C8RkVpmkgH493evqdyDkQ4aE8ltqg40L5Y9ZAP09wQcOAvniZDDzYFKLevFcRYiKuSuhnI4M9Lfja0IczM2VMpHxagElbnJLSGH1ADGqFGM'
        b'F1o5KtgNp6iluieUb1a0IcYZt2KNvMCJC8RQFj4bi7B0663B3NeJkZVBmqsIlY9liIBWR/XH19W1BheerclcDTeiulArYq11ztzZw9bFwys2idhgYZLQ0BnEeQHPBeqr'
        b'TEHp/vQyYwNKhQo3z1Hm2cTJD2aCTJggfgFzar1uUGSDmSbfWELdGbO9nElTqnVJS+dPkeC9cDytH7M3FXBuZBAP+oHXhHHmI25zN6MqFa3VKhQ3iffchQriQKXOw9TB'
        b'52F3IjGQCIKCzXRovTb6DZe1Tu5TmAYHduO58AMqqGE/5EemnRaJZHV49j71W3qYT3/0mGV6NZXjL+y696OV1nRPZLU0WXlljZrTG87OermBqkWbC6d+vFotv1Ky+mZT'
        b'Xle6nsVX2bpen0l/FlwX805vnJ97/7x0StWP3827X7v365ei/do/WvvJ068h6fSzob+/+6L1sVO93151GbdhZ2hAUZ3xjy7qSUfduc9e3Wb/8sclFvpRm9w/Xa1q4r9o'
        b'lufLV6cdc2t2Tzad+a/8syebLXY94xsW7LG0QFPcYzi+rnfyZ8UV71z95IzON4Nj0EuuActOoTNqJ7ePib1S1mO8/q1coz+DfbtvKrdIW4KTXWaPr/K7czV7p3/Ni0Ev'
        b'bMiIsf+gzWrrgp3rN976eKHHK69nnr9nvNntfNmL38nWX92eNHAhNSB2yw5blxU7d3zxZte4WcovqTnsnKj7de5mT9vNuZ4L701769WYOxM7nt0WUlnqmRoX88WRq75N'
        b'y06/7m3cXN5xJL/j/TMV69qTdH+ZueaDiYd/8jKY9L3mgt+vBI/1+NT3V8PeC59sf++lq55rws5n5xUUfb0jwCgqreCrdXuLotWuTviTP37mI8vP5zXeOxSgUbes1/PO'
        b'xffGTn/m9x2fra98vjIsLyNEa1eC5f7OF26fvjVu46HyPdcD285U/fj9U6fsfA/3vDD11q2n323QPaV38s+5l6/YtjkXdtyTrUsw3Tgz+aOGzR620msPdty2fGc2qu5b'
        b'FmPuefvGV13vHHtxYYV1rP/e3fZnF9zbcX7Vgk+fTk6Lcrmv+a+pt/oDvwmafKPV7fpAQODPCz/P8fVouT0fvbXl1uKvVG/+stak5ldJV6R75A3lKZ9/63i99eC3D9Rd'
        b'a+6fqPygPvrw/G2l0bef/WbDUv8Jhe/3PvP1tQnXvnt2wr1Br8tfbDoftnJJ+utr2u9VHftUGPhNs3vZm5q7Ul+RulxT2h34nOZ0562qFqusGl/NPWq2+Bdp4kHtI58+'
        b'Y2FP7Re1od7mceaLW/cNGTAy60U0iPop96ExDlKhnbpMQge95eaSqMqD8lyaqAu1uzFpEvWI5AJlNWpU2L82GVFbPShfPGSuN17kBRUulIMPREfhuBUV/AK3MtHPcAez'
        b'Tu6Ag/5yc87YdY/4goNjiLnF0h8LpynDPZLZXjHLEXpRDmXbpkALte/msTw4jfiftp7MGJMMaHJnHL7uFmKKqAm51O42ImYBY+ZssZRwkfSbqHKIKxooF6OOQEwWwn1P'
        b'QqnTpVj2oI6+3GLQIcxYjRFwqblLmEDUvQzKiVl4nAXPKe3ik1ArHJtiwt41QiXqkxEPNMxSkZgptjMDVOn4WJncK9ouC7whlmOGe5eAzqD8EMqM7TbBbBOzjIYMZsUI'
        b'OeOpJ6Wolc5YkpJwflbCen7BNlRFO+psj6pkPlA+5K0M0mXMcL0BylTZyA4buq6GVifcUia4meLDJV1GHLVh6R4dYvqQdC8v5unjMGTbSh8RHlA3ZqsvORgxOaw5XBFm'
        b'Wu4Boxf/lONuMe9YKAMORmAZJM3yUT8Y80xpGxZj5rhXzhqjg5NwLwhrrGNPCekeBIMjvA1B9jozlA+1lDGeiFtyWkZ89UORSMcDN/4Uj3nlJszOU2m4zdOCyP5FWEBH'
        b'aRr4NRYJKrFAz3wAosJwOCu19YiHgg2I5krAVevoibbvhwpaQDw6uJtIkIR9vYT6MPlUNIRQXMMZRt3sKWTdKJzUzUCpCj916LSMLkXIQUc8HgN1WIzahtAOcqyDH3N5'
        b'Pi3KZ0imtUP9cpkWmtFRJhAOhAQpZFoqz2KBqgEuIOKonYoZragCCqREbgXMxstlV3QUVVNKL8fLumykl0GERUTLCE862kprUc4obnzVHAU3jvJw/VROqcInciYUEJ6A'
        b'94AmTryGh9T9m9nLXic4xRzfTcVHMbN1XQMn2EZxUNXKClPqEZeNkBpBhSwYcJohGxYVqJTGc4ZhYtQMWWaoxpvuRhJ0cDkxIsZ0zHIjJ7vKXCEYFUIH8+yeDpfhvPz9'
        b'KXRoFIMz0VAMp1E2lntN2LxMd5KHRy+ATved6Axehu4COqQ5iznrqbDDI11AeDsblDdSgWzvL8HdGYPOw8UEAjbcbIvOPN5efM0caIKLCovgOdpsDPM37x3FRipzmv6i'
        b'uTNmGG1jdu6DRnDRjVWLmsJHqa4hVwmPdc8OtjzTdqNzpKQ1WPSzlQcMIzwlDExC+QvZfVLzOKLxHcLFCE7QjQW6YAvd/4+S1P/KkcxIRzHTFAYvN/6eTLVTnYZRJxIP'
        b'/l/QFgx4Eyy5GJOA6kTqwbKPIXUSQ+QdXcz2E2mISFx6v6soT4jHkhFO64mMsXjFQp6rEYvjBwLx2EEiUQvEf4cKr4nlNfJUIn+mJpJgKUt4QJ5KRCqCikhTpE4tlyUC'
        b'kd6YMxoVJebwXpcX46ekRWo476OWuFSWkstNzOT3z/+lLbFcbrIdReRb/8BmpemvDYlp84mtl+Fjg6DrBxC4fUgCEw8DCLaehJ+lcdBpWHQaDP0w/nVTWW5Ue1N9pI3r'
        b'TelIa1MHkpsE/4vfQX4tJb/2k3pUh4z8birLLe9uqo80iLupMdoQjdg+UfsdShBGf/3/u9uIYQuk27h6RzIeKRx1S6MpFqz5acFy9zGi/6N/xeoidRETU4tQKkp7SCre'
        b'Aj14dzWCFnEYnENNT7byWshxzHsKNxQnWHnI4kv452Z3ZDO14R62+FrtmUgMUOGUcayD/ayZc2bMdiCInoSE+KS4RBne7Vsxs9cGXfiU6YR2LRV1NU1VDSnKM8K7fS4+'
        b'SUqg3GctZmmO+ikR6EWvVGowjplOtGCOs5bYmczQ2c3NgHJURnW/kKEFXQ64/pkaqJWbCeXhidr4cXJMhAMeSQdjF84BNaKDzEHAMWjd4SDhuFlO+PybZYwu0McaUL6X'
        b'TN/ZcBAV49950bSINV6aDkrExfqpidwc6F9AH/qoRjhgsjpKcWWOkL6OFhCBz7VGB0zpuahtDv51aSXVZEcqQz1q58jVaCvUcPNw93ppX3ygbC7msknEyAJL/Csfsmjh'
        b'a6E+mJByeSS6zC3ft4M1ugQzEM0ygbg3HJjArTCzo2VAJjoB9TLcmZW7Mee4ErK20Ow7oWuVjETGILYNnBPUJ1M3CqgHUg/IcHdWbdLkVqH+SfSpGqq0luHurEaXdnGr'
        b't8Ex2gzo9Zsmw71xnjWVc96M6mi5uGv7gHTGZQrq4VxQTRhrRgHK3ELAb5yr3xTOFRWic6y+rgnboB032m3GIs4N+iLY06JFEdCO2+yur8q5K0MOVexPw2TCnBxutAe6'
        b'jOrx71RURPMvxud/O260J+pQ4Tw1UDbNj0oheym043avQVg64NbAEShnkyHLFZ2Fdtz2tWobubU+kMlIWAuFcIkYQ3lBWQjn5XCAlg5N5lAhFROLuO5gzjt5Gh01PBHb'
        b'IFcqkGGqRzWcz3TcGOKYH11SEqS47b7rlDhfz82s+x2oyViKW74OGiO4dSgXmHv96dDgKcUN9+PhEudHqUKzl8M5fylu+Hos+qRz6zEPwdrdirKgSorbvQFadLgNpqvp'
        b'4y2oE78pwH9tXDSf2+iMG0Iem2pgqhfgdvvP2cz5Qw8MMpf+LgmoADd7EzRO4TZhGtawzqdbTYdS3BZbQ8yx2eItgzWlZw+mY6mIBNLoCeTs1GGADVHeznXEYniSG14i'
        b'kyToCCNVVaAOlOLCraDJkbOSjmHNTt9m6MMTzwCF07mp0IXKaeY96KQ3lOLO2POon7M3nsfacdEfVUMpsdFYEcBZQ/4E2o6VmKnN8FEis6AGz/ppxqjawppeto2BLLxX'
        b'FEDBzmAosLKDg1bE3E+En9eIoC9cg9ovQR+qhy76xmr7BjgoQunxOMcFnGMjJhcRFBIgTYUUY2W3zn0oAykCKqGYmRKeRM1oEBdCaoGz0CPiOb2pOIctqqJFbEbHZdQi'
        b'osDKnZgdHRTp4jIKcA4DOEHtCXfEwgBrBTrsSjIInN4Y/F5XjxppGaC2iawNklXytzxpQRE6xDxy1KJmTl6D8p556DhuI+rFOcaz28sN+ugIK155MvnUzBoXjXopCSYY'
        b'ENfgpGwsXuVRGpnJSaAFGayDqTuxbMA6jzn0NlNBTgLUa0Y7CEftCEaReBs9KJrM+nYMy3d9qATS2Z1m8eotVnQMRNEW6PhC1j3UEM1ceKB6VACKn1os9NopB8u7QJwG'
        b'01aYTKKNoFnOeOIcuowKJIoKNRrBolTWVvJ6JkGIstEoYENOeoOqrGhl6LAKHiTyAqWHLSC+PtAlQq9mkqcCOmmMuHUHYJD1eCaWS2iehfJyIBe1sclTEwv18l7vgeOE'
        b'usFywuAjiTmDO4FyIIPkQWVmjMp2imlIxh/1CMwKr1cP1dP6MqAtnr7Eu049nqcRtDmoZhJUyKuSmIpIkxRDjOXvOjoIVugS6mY0ngGXaZ6FcgqVrmLD1AnZcxRkDhlr'
        b'pYwaFB2PmMHakb9uhZzGVvgYbVOeJO900jb2/jJU72bTbLkDnBiaCHDcgbYzBG8n5Yy2aZhq51A7a2g5zjMd2mgrbOEER7uKcyzGG1fbQkUhqaiWcSqHUDYxXsNUK4Wj'
        b'ivaQiS8n2yqUQ0dgjGMkeRU5VU4aeR5Kl7FuLJZg5vZo+hhlxBNq7NEl006Hzqi4WahLXjDqQ3UoTbH2DfGpRS5zxhmjJjpiIhGn5yiyxHJtn74S/Va8MZRWCQXOy0Wo'
        b'gU4h2otgOMlmRwUuPJNNQpShTvMsZPsC5G+lZUzDY3qZNQDK9lgNL3vUqM3KwGKhPVtVk9AxMqKsHkIDrV2Jcu/dWZq0CwIUw1lTnpUAjQcosVH7eqhmVTgCJakoWD4p'
        b'elNojsmzPeUdgcwAK2VIH5rnh1EniwXTqrycNQLSVrnSXpACFuFlQMZ8F2bGjjLym5ELIlqFvIhUdJhWokSuBFgthI8h00dOrjjoYbaURzEDd0ixh62gnVyrjJt5DPIt'
        b'eGomOAO6HN1oKERnN2/i+xRdEFDarE13KEN5KH6phRo1sjseLXA9LsS6PlC9kotllndougZn7TgDH+2B6q6bVrCHLlNVOepdOjBQ3cRjHUf9+yxbpMtpr3Mnny8UJdJ8'
        b'v60Xc6966VHT9nmYU6UPV7hpcj/HYZnFPtC6wTqBPSxRkXChS3GXTQPVf4v3YA9DUnS4uVNWcFxsYFRRkCZ7+N5aNW5zrBXHaQdGXeOmsIeNvB7XMs2HVLSv2N2PPXwH'
        b'swK568dQM/zX4vexh5tXClxCEHGsFRh1V0uXoybTJXYGnFi2ldRucsfWFwuJvqvoi9cwX2iorUs78KmlC8v943wJl+loRHJHve3mw92pqiT/XVlCK5jho8zlRhjTt/ci'
        b'Vbg7DvS/75fQ49gQdaELZB/jYmbqcTFw3Jw+9kGt6KgVpmJyJOrlkrXhHLNepr7PDxpi1kg+1Zqhc+Rck8BhWqkxN5Zz99hCO+C8djHrapuqHvdUynrS+IVJQfaPGk0O'
        b'uRajzqvkZpMsjNJw+CQ5TuSmUmR0aFhyPGHnHhc/SUttZPwkErLNaIeJlacn9dZ7EAo93Ndg4WGk5lCy7KFAVJgwVdJloZBLW//AdCNXGBXE4zlmrDLdCo+Jp2fkh5lV'
        b'vGwd8Sp5/GUP7xejxyzT/qqyc+CnX40iBu6uTs6KMBXHmqoeSuUfLIvOjbVUslimkxR/+1XZTdNpylMOcDk/ll97odLu9lNp15aaN0RkWGs21pw6/+WXtjZvqC6DFZq7'
        b'9W435uoKZV7L9Ge/8dpTJlUVq3MNzJ7Z1phhu2fDU0qbn5m6+Tl9648sz384P/r2tOgg1e445Rd7CsovvJgd9f4ev3teDVpL/Mst73q8mRcxsChO/z0YsJu/98772xoL'
        b'u7ZW1ZV8F1U8++v75l7TcpRXVH1ek3dlU8CrKdVzr/Ueupm5bmFC9zMvGn7j8eF4o4ANll4rbn5RZfZbZNoi21a1vIIZidtO6xWlfOR18m37qV5iU5+uyzatdeZvLfEZ'
        b'nKP/U+/1ST6fXl9Z5HhLuv8teEMzfvPs2efjd39Qatwzp18pkt9/x6zwX8syRGc/dcr4c/7uDpcxs/21C5fWdSScli36sXnKV32Bd+9UvHzFOrEybHKC6qyeVzQWHtEw'
        b'/rRye4PmmtURq52e/+35q1+nXG+cUNkbVWo671qgV5fKewYLu+3e//iD5PleE/8MfP34O7MGW8uPzK2wfL3sHZHji+qVz1ep9l75vt//X94LlD7MtBWNCX6zozXMLPpk'
        b'2MKPb/hWG3S3Wtru+T2pYbXVhpkXTa9l3Tpywadz7pEvU9+dGeTgZbTL9I93bROvfP7F5cUXQky/0vTxj1v3dc+5i1MnzHh+w9UNzR99lzG5OMsoz+x7nSjriFjf3937'
        b'1ey+/VfPC4en9H82X/1KU/p6nUrb1ZFv6u66NfHw7lc2+MkqWracm5r34Nqc3lei21975/PfPh+X/a7v/D+lXwddb5B9YqHJrg/7JkaTm1g8ZZU4pX08KtCEEzuR3AVQ'
        b'ugE0QgFz4iCGU+isM4/aUZcbu+bsi7Fyo/H8ULGWG3GsLYVqfMI0Awsh48LhTb+dBGGVEVcNg6hdjZ8xC7KZ+qRoLeb1itFZVyVc8rkZoUTnVKPBogPtRa3Emw8MQoGL'
        b'tYuYkyYRj/S9kMGsjqqUTZiNWwrKUcTEgYvoGFVHKaPLc3DBdrg5YlPrRB4vwnwH1ptLmKUrt6LRZOAE9AmonffDrWV+3ackuBJPO3LjNscNxLyNXJazYDaWeMdytXGb'
        b'ydtYkqAHEgEGTKGNvrPwRBVu1HQG1whdcGYsjxrGM4fmW6B6DNNbFaJ2orjSRWVMqVLvuo8FMELHE0e4O9JFly3G/d+axTz59lD5H17h3lSThQRFB0TuDIoIoze5P5PN'
        b'9+9YxxzgPMQC9aLM/89/fyfRYZ4d1Kh9jJrITO5Smzng1sNPJfSWV4/6l9CT3ypr87rkckykh/8ype7G1ajLbxVeLIiprwjqvBv/TKMhTtVoirgLN8NfzOTjiXjPzhPR'
        b'TVHkzogRl7p/k7DqguLQIWX1E3MXElr6b1zbkp/nDUcavBD2KXhxuOKQyl4oP6eUOIOtYhU940d8vqopzktyWzsCdsjLkV1CuNqQr1fxX/p6fezVHsEkPBrbe7znky8X'
        b'iaUPrl8IF/4BiPQRoCP5T3ikXiVPegwvFgsUuBEbEqku1Y3nEomaaNOS9YTfXG8uxyaaO7v4OGN2/dhkKHRR4hz3Ssxdl0f6fezBy4gL0gbXr+8GOge9FG5e8nng5qda'
        b'D6UdPp45I+tUpX/0xbyLGZMq0hxEXMybkvfeHLAQ6AayAzrxXlCsiaUZ6o1GslAYCyesqc5s72zUyjToteseE05t7gQFxuMxl8s3pSHbwkJ2BFBehq5H+7+/Hg9w5szR'
        b'/p6JAcTlcQBxozBs9DWiZMUc5yNHzHBh1ETWHJrIGvgvfcI9zfn7EzmVu6c5ciovxV+i1E1TLXdQV2TOqFAO/HjEWosgjjygWILyURM64Ue0q4ZSqIlHTVTsIxawOW7W'
        b'nvu2Ez2tmJMYC2rQItALQGU4b7YbGq2gxBPvITo8cRp1nE6SA7FskgTuCXHfKNHh5IIHasRSSKU/Ounm7ulJAjKprBFktiidfuOmymBCsVP2qBev287JyB3Wd3aTfTRi'
        b'46rHikgIG67jbcpwx49jiMbWaYHqeer2XBQh6iVtJYIT4rhVUe5f2aQv+YSTEU66damzz7rEp51/3CXiREr81KfzaG1nOQY1StUIiypRXc3JCAubEqH2cWe1QACb0rAs'
        b'mq/JWULWofZTJmFRvyZbs3wD+r4f33lbiSCPNQM4GWF3S5+t+/hTget34KZxhp9Gy8jJ9vZnL/ms00jSiI3K9MV8sA1fNqVKRsThJu4CdbV3ytzVo9MPC9oXRZ/c/IAe'
        b'EhSiPfjCuL7q17WuWF/Bi0eZF2am/ELrbZq09PUvk8l84Sx+7KeP1vePeb36E0xrS85y6jT6SDMzpmDpEbxHbOG2KF+grXtuZlzBaxx341nuIy6r/Dn6TLdlb8FrYs65'
        b'lfuYy37ndzpAwgFdF1/CUJB15ICJjAoEV3TGMtLXLEVJdhKXeePGNCfvZZ63lqp3Rsy84v6nslpZ3dq4bNtDV08frbf+3Hhjy84Tp1daL/Ju0ptxwOuwk9ahzamlvos8'
        b'xm4JXnP5DY/n9qSkpCT9vm3Chze0S375cLL2SvfieukfTqenOUc/d84tennbPMuScT886+szo0Kn7k+nUjQWwtscDpX21P+r+dZy3dmnJ7xkceibqA8c1hpqK9W9p/7a'
        b'+0c/edv7FgoMfjp/fcdHwXNEq46mjj+36ZfTy617Twy88sOgw+UPvm7b+MfSuD3l83I0nnEt7/Fu+vyd0ruBz6S0J2i/4iXqty0pmjTvSq1d55XZrYkB196efu3N1IbP'
        b'ZDV3Svaf3/jzB8+urn9vyY0rd/3mtsYcz+rRTQl88YwkvOatOJurpp6ZD7a++aXR2q7JNbX6d+rnv77doO6DlP0GC8sbv/jg+sXfi579/u6zstrpCVnhb+rXtFj5R9TN'
        b'Lwgep4nU3zkebX/G5/WN3/2xa9Yuo6P59h/dqnvwx+SZnju2f7Hy9NGfy+b0Jx98/6WKW1+dub8jWfnot/ziqwkffTrtnVtb5gbZHvX2UH7xR/svF6ne3Tonrfsz1+3n'
        b'Tfe9c3QPX1hSe6ezx0KbGTRnoVJfNwsoQg1+NuYSThIhWKpYUlYuACrRoU0rCX/FkIQq6JAQs3gDY3hLlwvEZMTDGnWiMo4Tz+DRWXSBZwYfFagCSuEklFOOzgWKCJxM'
        b'BR0XUpwEqpKPgMxIdN5RlpCUpKGJ+V4taFOPw4co1IpQzf5oymiqaUMp422hEhowf0uZ22ooZ9gDKdTBqVAo8EBnyR6Uya/GAnEm7dQ0OB9iRfjQusWUn5R4C3qRAm33'
        b'XHuUztjMBdCCOU3CZaIsqGfs5FHJUixRDmIeVc5Tq0oFVIryUA2tU4rK9fDHFpCxwobYVEgChckCOkgLFqFKwEvWwhx1EFAJA5RooCZm1FEGl1E+KTbXxX0SpOHjSYou'
        b'ClCzXx50D52ADlQPpXZuLh5yYm8RwnBnuxiCpngvXCZCQt5mbcXZ5qDL2PhSf9RJgbaW6Ji7BR7BBYIedELDf6nz/k/si0cxscPnHT00j/yTQ3O6phKNXEOZTU3egNeW'
        b'uxPTpmykWO5mjMSPIUynOnU4pi43G1DhiXsyYvitTRlWsUAMvMXMwJt+p0vdk7HYMCp8vNYQi6l0UxwblLDtpjg0KCHopmpEWEJAQmRCVNg/ZTpF8TqkTF3yS3vo1Cb1'
        b'6P3jU/vrCSNPbXq70zyRRG4jh/aEkKFjW5kz8BDrrUJFIcIIJo00Z4j3I2wvVSvz4aIhXwLCv/UlsO1x3J+Ye9SFiAVrnwsqQ4ewvEb0L3nWkLUD8vCE1kXdIkhXRkcj'
        b'/7XZlJeR9XZ7e8vdwFVzPg/8MtA96KswNerzZdxhkc+zOSP8jYieqPe/qUFGaPQ8s/wn82xb/JihsRezkaJj9ngOTHh4QMnH6/7xgJ7THjmghD3dp4kuM3qN5MM8oVaZ'
        b'm7pCydfP+38+pI9l6EWPDKnIM/K29hSBxg7ILD95N5AMVVR4cKhz0C+fERc9Im7iOyLn9ef/5nDJ/rvh2hGv9/Bw6fzVcOmMHi7y8YZ/PFynRw3XFLL+snzhlJXnw+Nl'
        b'loKHC+qUAuECynjyiJHKc8iY8TnicPE/GLNHhD8yXo+GelDzZD4uClAGanQLhx5rz2G+HJVtYoh5bqKwTz1Ak4v98MBcG4vV9OHPTgxwX68dFnXKKYLdCI+ZwhFGPfn2'
        b'3tiJbx6IYI5pVkyZ70Ow/URJVQuZHKpdzaI9NLgyXvj21ARry6hEjrKMa1G9pY8NHLFydhFxEnzIbhR4KEPHIt/cgDhZIs6RlfTp+JcWaCJ77cwPK+MmfCQ4v5f6selr'
        b'3udzyzRX9p5/z1pj9dKfPD4+8UfKy5mWxpfVzm3NtiwqyjKaOM/d6YjtCxsOfZH8geb4/AlXX4i/Edp4t3D+22/8WpK8pb9Y4xmvO58n3ne+2/FK2vSaA3/8tOT9OP85'
        b'JyrGt9z80EKFHtxRWOQoI4iVVBtzZ+KGG1UJNlDmR89l9XjoHsEAwRHoJEwQal7LGIYKlBpI9SQkHDHPqSTjQ7wQMyMuB+jngepQpcCREl9VUEdxpGdRD+NwoIpDZxYE'
        b'uVLgbR5mVFIEM2iEZmYmmjkdnbRCFz2YLxX5fVnyFHo/Z4mOR1s5U5/7tfs5sSOPzk+UI4XPoktWQ3dwSvoMYorOxT6yMvEaetwJNrxe1cn2GhsaHkAORbpcF/+T5RpN'
        b'zP40yQUPPcPJ+a3Lx+uPWMJkOt8UP4RseqSZQrwB+SZE0S5axKZ/vJCbdR/ed9ElGJSyjdfZBR+oztbLxpErxImQKcbca+usR7ZIVfm/MoOHooeVicrUy5TDhVChiKfX'
        b'O8Kw655wlVBRqDhTJYP3F4cphSqFSjK5UOVQlSLBX4LTqjStRtPKOC2laXWaVsFpDZrWpGlVnNaiaW2aVsNpHZrWpWkpTo+haT2aVsdpfZo2oGkNnB5L04Y0rYnTRjRt'
        b'TNNaOD2Opk1oWptEOMO9Gh86IVPFXydMKZwL08nginl/HfyGXGWp4j1sYqgpfqsbOol6zDC7qewRFE0MCH+1GRWrhgS6Mt3JXrEoXqNj2WD+kWzWj2ydQxdcSzm5byRq'
        b'FEfJSw4+1aFNVPyXm6iI8jLiXzP+baikUS0dDpX0pMBEZHmw2EjkLxICKYgVsXblKtPwyKjHRFkaNbPIpFZ5ZCOf4JloQfaYdDPUa6Xq4yyPobLGxk8OwELnINfaludW'
        b'88qOkO5CwWC+avbS2Dgf/EKRy1clSSPWl4QpJr5B5krxPhZiqqIODVDA3DxleKyFAnvoGuHaJtubaqPdoBWyWeRZNw8eGgNY5FlIW8NsHAahI94K1aJuVw/msJyExZ0u'
        b'gupZkE+vhjahATToNtNV4Hi44AUHOejGMk0nNSdarT2RBlfmhGArOMXPgP7pzEPNJTsbN4VLe2lMynwBy6FpkMOq7ImixhlFxJQbCtw9+Bg0wGlCnWj5rgPs3LuMSiRu'
        b'6JwzbhIuAe8aWpNFG6aiZvrWfsVkN+au2oNHZdCEN+VuYe88uMAU4/3oMFRiEcwS5xCgCQbp9QZK80WnaduS1de7DUcKJ17pBWiejwlJZbgOOI5KicGX4SiPVH0ujM55'
        b'qGSJwpEVFgjP8nZQvYm+muW+gp4A+SN8Va2fTQu1jkGlbqMitUMrJ9JHvSvpNVeGHb3m4vzdAq19JvIctQq0xYfraR/O1Js6rnLTY0psKc1p7rwsUL3Taywn59XVJ6Ni'
        b'hVcpfyge5VaqH2WwqzplelWn/aY40NpdYsq8g0X6oSI3d+lIN1fK6CBt8+IZ40dEeUe9WszLFZyfQyeFJqQmKdxcHYQ+5uYqSYneEmP65Vo9wRFVL7GqVQpPSmIzoXws'
        b'pgyeJ9RKwU5YhCpwyfWiLZjtyYlU3nSThUr9PUdpf0l/NNirO7lUXjS580fXzQ9eUE746v1zBWOPm3vXZ5R6bf3Sycj/kzFfNX2wMd9r4tJ3rd8YEJ86E/J26VtbZ5/2'
        b'37MlI6sx5f1f39f0/6EPGg3Opb8fo5X3rCTg1elbHTdkZPxxL+2s2iLlOTNut7fd8bkRWr8s6eymnXu3vFr5uW9CQIdBzW/f+944/pV6wzerlxQuPpgyJdq0P2TczOnX'
        b'jZI2NMIYv2+SPvnWIizxm6ePj69eO10yQa/OJ84hJcisf9tqyVfvLV3QKe3/yvfcwue+/lL/7icL75XEf+ZbETI7otOgM7c0ojth351o7/M/W211/qzvsL/z7N+PzLo0'
        b'9auuHV9vNvpcu9Ij+l2VsEllb7m7FHue3hPiGuy67lasgYvBs9Yl1r82WG944OSyxPwLs6l/NFibfTq4wu7KZkdv6am6Mqe3w1x/Pfnep/EBrzwI9jOW7nr1wO/cT6FH'
        b'f7LmLYyZErBzGrEQq0WXKA/CGBAoQe3MwcB4sZu7pS17JY2CDh0BTkS7sruh04vw2BKQPbkZUkJ16BiNrLsf1aNKBtcoQO2oQB5GxGaRwcgwIjXQQrEf4yEDKodDHMSi'
        b'9NE3+ugo6mZRi+EIOk7MCejuJjFGDQ6YCy6EIsq/iaFSFZ/7ih2Ok8oEOChAlTdqYsi4fkMLqngUkrxRNr8M199JP5w3hXiDsKP7nnIc2/kMoFY8P2k182vSBD37cEe6'
        b'RGvI7ieK4v0sfRl7lo6K4/Cbtk1r6O4ngjoeHUJ1uynPl+CuSqI/sN1vFsqjMT0W4dYS0m2ciWmjgjfugyP2P07XUYSOJ0Yz0tWhJlSJu3tszZqhLZDT3StC3ZhPv5TA'
        b'LKEyJdSDKtsFOakXNKAG3OlYyKMZzNFZOEbCLbBtkJNioWaBAPXQBYcoV7sMXUIXRgW8ycZMr81WlCMPhR62fchFK9m0VJQ5LVVRAnRvp5/PR314kyYZ6NYhUYEWOCYY'
        b'TULFtJfRULMbFXhBnd0IN3m60CSCtMCJlIRe9u7/j7nvgKvyvhq+i72HgIqKmy2CA1FURAGZCgiiKHvKkiWiKEP2BmWLsvdesiQ5J2maZjRt0jZNmzZN3zZJk+42Sfu2'
        b'yXf+z3NBUMyw7/t9X/hF8d7n+c+zJ5crxiiIQAmLNxmyKguDeIu3tfXTr6yBgpRQQ4OVQNVe7ICVdACMoW6HKpzh1bclQmMCXctozdEUOQ1o3skNdx16bnDNZaR93YkI'
        b'jQlUI8Q2kOXOJe4ZErUlCIPszR6PqJFA01oMc2uhi3vEiLSCTChWhsxFOZMhhqaqGDozoMpI5umGJIVnzYhYahzwgAkY31RivylQVOTKKvBJQfJC3grHUnO4ftLcDytn'
        b'wBJ1FEUikuhlhbL/lpXT5tJ0FLmWAkuf8z//lJVX55zD3/YdRWG6ulSQfLxrgDTJR32l8i//jQ2VIv5V8xXHlfCtNYoq/eVpPU8s9psXDNf5qkrsr9G6+NYASzMsdQXY'
        b'wlXjlwqqj6rTP1sbgHC+3LRcQFJURNxXFOZ/Y3FB/PSLhfnZW0HJKYnPXvBbEhBsGfzUad9cmtbQISYowiAq3CAqmW//eczy2NIpPFst+ouCr7iBHy/NrM8V1k4MC41K'
        b'jk98pvYH3H1/8FX3/dOl2TZKZ+P7HfxHlc0VAmLjQ6PCo77iWn++NO9Orgh+UFKyAf9SyH+ygIjFBYSlhYWkfFXDh18uLWDb0gL4l/7j7cvxGWtPn/v9pbmNF4EreRlq'
        b'EZTxAzwbeHErCA0LJqB56gp+s7SCTRxWcU8/e+X+W4vHvgitT534w6WJN6+A7v986kXT0VOn/nhp6u3LtWd28ouq88rpl83OsbfHw1qES2EtggJBjiBDmK54XbBkDBBy'
        b'xgDBDeHTLKpsyCet4PJfEU7zLSuyi7lZJf88u2rrXw7yrkSGcf2RkyNZA+pH8JcYxnd14PoTx8UnP2lTeMKusHhJTxj1/T1EMly9fa/LuR8HfjdY/EfemC9fIJwQ5xnx'
        b'Xtwz0LV5UcaV6vZYwQm5MKv2lFLwGYvZx1x/nW8udtwUyKVvWuRuSzt9FCgTHhGW7P70GvJs2j8y9s2SZr8x+84UVC+vJZ/CjJtroPwajkmFPbxjsrR7rHw8KoaPSKwh'
        b'fXNeVgnmMRuG/+/4aZ4MvKIr/eK5f4o5P43j64HMT7OxJDr8k8CSCKcg/mq3TIo7/vbCYiuFITOcWXm3dLGKWCyxMcScr/PjJN585ltW+upbTgpL5qfJEj4WjpUtXD75'
        b'p89w1yUr/Dgsx1b3LGs4+Y3umtQFoeAsK7FszAr1Ze42EvHtgAvDsNbFBToVGDBI1ITQBS1b+GrWC6yMpIvJ3u3sXYkVC/kthqyot/7gJ+bI1QXv4UsRTiGuQa5B0b/q'
        b'DouMiIxwDXEOcg8S/kWv1eqSXrSe19kPLGSsEiYFguFp+b+qv/JElNrqEWuJYVIg4ct6fZv7ESvLqYrSNZ64I37wW4/fysop//AMt3J7eUzaKhM/nfJyfjS+UL5gyY/2'
        b'TegvMwG7PUE87VkoXhLP94narrQAJxkkJUfFxBikBsVEhX6NMVcoWI2HyLp7O3DGtOzj1wS3dZgr0iD17QuCzVEOG4OESQH0jcEl948DXw82/K1zkHL4h/Sbqaa4yvWE'
        b'p5Fr4OGkEZ2KUKMfZv/FT9H1aG/0Wpu6aD0bvcb6okPRejrD5qGCIgvTwPPfPYUGz1e8+O7OZmh6zVNb7odiy1qrDYIffqB31PqfRvJ8PY9JLNbxxiKTZZqoKkyKHeHB'
        b'Bc4EsVVJfdHki63qQqnJd/A8H/bzUIF13+ZtBwpRQt5+enUDp9ibHfchHArChZXGYJjay/uzepWg+7j4kW2Ws8zeDOXbL0LtKU6/FkgkOGkshHuueJ8zJtlCF3abEDKe'
        b'tFWAfolANka0ZQsOcvaZ6zvSXE5Cv6msQKIPHU5CGN0sK2VKX+vcko9KCuDuk8OU498WU7T4yoLc/ywemquRIVmmBS4Ov4xtPWVNj/jYLnr0v58Bi/I1V1VEl5ZgpLVa'
        b'YYllFSQ431ooOxYxU8HY2SYyEvKO/KLa8I78ovz+jiwvCr8jy8uo78gviozvyC9JfGGL2+Fp1n/eXHEZrdGlXy+xU2ILlhdJxMpC/fP/WzUdVJWU+VKB29TNlpiFjEDx'
        b'VCqUsXrEtxSf4M+a0r+Tsh93Esre1rstCBWVMteZXL5Kvma+VrjMN3cO8m+RAKEUqnxLnjkHwwVh8pw7Tp6NHapSKuQizJVoXEmoaqgaN67C0ncyJKiqh2pwnypyq9EL'
        b'1SwVhW7j3tHk3tIOXXNLgb5Xou8F7InbcvSjF6pTKhu6nStLISPtSKKSr5qvnq+Rr5WvF64cujZ0HfeeMj8u/cjfVqC1ri8Vh+7gHKIynMeONdpRzVdjs+Vr56/J18nX'
        b'pffVQ/VDN3Dvq0jf596+LRe6kd7fyc3J3lTj3tKhNxQ4tyN7Q5Xb32a2P9qBKHRL6FZuh2qhWpy4bfiOqhQj6K+giLDEX+2hi1lBxe0MVj7BSD/9nWQQRFR/OS9g/sGg'
        b'ZIOgRGZuuZwSRZC/YqBwEs6550Ppq5BkpsZFJRskJwbFJQWFMD026TE34slk4i3xidKplmYJSlrSgIgpxRkEGUREpYbFSYeNT7z62DDm5gZXghJZGzIbmyf9lEy5emyD'
        b'Szzt2AlvO3OD4/FxO5MNUpLCuB0kJMaHpnDL3bzSQys1nBHhFzyR6rCyfslS7RJ29Uv1S8QF4q9McpDqR7869/gFcUf1mJd2kT3HLm7pmRy1SyfKNC+61uXXsKqKxe6e'
        b'u7JQc4OTnA0qNJ5WRCqZQVhaVFIy++QKO9lgqfEmbBWRQbogqY7Nr+kJzftKFFskfROeQsMFhYYSmDxlTXGh9L9BUEJCfFQcTbjcRvU18gq7xidTSFTcU2zpdzVDHF1e'
        b'WdRp0cRNH87twiosdeUKgXo6ubov1g+DBcxXwo5Q3xSmHEM+PXp/1THYWyeNzLw4d2oq5itk4EwS52dNxBwcx2qSup0kAqiykNkpxDpXfMC5N62g5pzNfi7zVZDmguOc'
        b'z1GX5pjyMsNOWm+HpUD2pthcoHZItE31DF9QdRhuHb6G2cu7YxlyHnW+JdZ+IxmoPAmz3ARB63EI7iuZiFh/kKR0O05u+691fHCUxQ7jg2cu+AtSuCbHQ+v8XcydWQr9'
        b'4pawgOu7VWqKZW58TdXT8XKYuVOBy4eIwRKvpMsyWB7DknQFUATTWBr1ptJWSdJL9PVvXq84Uc7ioJTzbna5tRz6nkuv5P11Mf6iiszS7ZqelUdbSz4SFfu9p/hyirVy'
        b'xHMvQ+ArC5vuxTrkzjyobJF7t/B0T7q584k7PoUuftfSf6d36cc7/txr5+3X/dZ+9wsmxyXupq7/PPXH0c0ug7Hjfzq15a3Us4G5ez+1jv91ctz2gIXQ2gTnWxkfhG0b'
        b'v2VRfKss/+Oivx9yvVbk8G+HvxllxfzIaPrGrYqXLu2NyH+Y+3l2ziaLkd682qG/lf387eS5fxn+o/B52X/8We6zwSM+yj8z0ub7GYxiAdThGLQtOvqFu7E5gS8qeFsn'
        b'hbn4IBc7jJbScTgnn08c97YWjKi5uJ6081p0t4uwK57kPvbdOlZqxyQMy5Z7H3MUOPdTBoxDvYurMUxDy5ILUoTtBtAsrRLevxOLj+LEihL8JKYW8+mYdfAQK11YbMV2'
        b'LDdlRSQVtEXQckLqMrwO99SwmOQAd3bjF7HSWJbk53Hx6WR7bmnX4UGsyS4sYkICDrvIQrfIFG6JedfUXSgFzvkJ+aa8/1Pq+yyL5Cp0bsAxHRPDfc5udFqSzUK4a6DK'
        b'ebzcoBGKpO0KBJhrwXcruA0zXJlOqDCDJuaPg3ubeORkXQ/MZAW6MClxYhVruEGiYTJ+SeSHZuyV1RKp0B095Gu3T8EdbGd1/Fyg3GMT9krXpwG1Yih3wkzet5dtCN3M'
        b't8ZjuwRbCOFVvcRuBzKSGbbjfdW19GIZlkMJ5DCpnc8dgrJdLmZcHUdWNcIRRuSgHDJxnj/yjrWsUAHO4sDywAmchBreZTzoc9HE/CTe2vF4ScQG6OOq1kO5CnaxiGic'
        b'vkKTLc4qK9ChsRZMXJ+MKfsmYdyrudO8Gcn8NnrCARZqLssFrKtywefKXG9uFrS+kdMaeJdXuu5K/vyUPtlL3HeZ2+sr3Idi/tlVnF3rlWgzLOX+W2gZmYIPlidDPnXJ'
        b'38YtIPPVBuJDSlID8ROTLbnArJbY+ZP8exmv/k9aYyd/lbvmyOISE41Z8Npy1rrCQs1ZALnIwCUL4DexUT8RfP9/y0adeF342HYWz+kJ26P31LyQMyd/97ebmDl5sXmr'
        b'7GfCyd1bjYRcbIK31mYOQ8siYf5xDHXA7K8xKCfeYL1FdzwGBEkhMQFcDuW3shTbPxPsL6ywFTMAghGYdntkQJxgv7h6mGGVifsyIoQ1jxsToe86ZzvW26hqu9v2ayLF'
        b'OftWvvBbRYp/Q6uxxD2FlYE8QMz0Fk+0HxFsFj1YiFlw19XY2RR6vflgQvahhysz3UAfFCqxRiK1Ubs+NZNJYpiwx7Dg40Bzzd8FvhpsqGMc5BoUEx4T/Engh4FxvxoL'
        b'/ySwKMKZ2aJfFQhqlOW1ovcYiTmWAbUkut1fPj8dUt/TmMaFtXzt1zzWx1MJ6+HWUhDQygggbVeeNy7shVEe7lYCHWRBES6E4sJiRMFXM4BFk3di5jeFw5W27Ces6SsN'
        b'2m7PBJITKyKaT9DbJ3F83zNApKMNZ+DWO6Z6MhhrjES8AfsODqtwXg7i5nm8cdsVZjg5VgcerOOM4r4evGkbp7EialdUupCjc4e3+j1u2o6JcA5x54zbaxdN279o543b'
        b'LzopZPSse9K4/RUeiBzhs1q4fZUV1SXpek+7wGWG7q+Z/tgzXdlzy70QT1+GkZAzyT2dNjAjHovNJtogQ9RBZok6iL82BJr5Hzuf0Akdw5JJGZbyyuUWj6dr07GJYeG8'
        b'5vpEBMoqCm9iWHJKYlySjYHdUgdy6e4DDeKDo0kH/xpFdXXGJ+OewiAuYgPOEA15CDlS4D9zytfMx3fVeGnI3KMQHQrjXKNSbNsFJY/iSLGFBHROrV2pxHkqyWEpPtCK'
        b'OnYtVpzkQS9GBY9+HPhJ4O8CXw6ODP84vDeMmezPPncWhytGznbcMpIx3PqdN159+4W3nz8lbr9EQD9WlxXtN1o3Vl/c5HzWq+7o6N6S55WbogTVJhpXhiaMZPmCLg02'
        b'lnxeBynBrbxiMyfVXDRJl657FDrJVAesSxdlnF/Dicl6pIZWK7lE+PGBk8s0Kgnw5vL9G51dYIZE/yVtrEOfk8BdTp11WVLgSUvOFyidY42RekgpYlR0Tdo1pRV0tsFl'
        b'eQeCPlhYgbhPl0iXl1VgySVSwOFQ2ebbonICH5Umz5UTSV/3GC4tG56XB3qkUWOcrfuR+Lwq5e8R8Y89EpptaQjvZ0L5Qe3lKP8Vy3w6tj8R3fB1UsCin2tiVTxPfjK+'
        b'JD58MWfhfx/t7fg5vyHar+5PI6mzQlgnSmKSpUXssY8D/Z974/nhCsfSkZqWvM3Fu+uyrFQEu56XpKsTaPKdzQphcDuX7LMYzAmTOoRF6/CuJH03NvD6bb9e3GL8P9dj'
        b'kI//xyboWvQrre7/3PbMDOmmgEU6rgYW0ruRSrOHRYvS7BHR8llDnwkom1W/DiilsxvxmPCOXFJQalhAUJL70+2+bBFSjiTL6Tmy38LqG24k+VXwalbfRYBl5vBQadH0'
        b'bwSudkum+7DkIBY+FsSH0cTGpxKLY2XOF8f9n4J1/h3pQdkw4zBntDdlFuHYlKRkZhHmcS8pOSqOD6pjmuuqJl1em10RCsVs9jT4aubkJTRja00MusIfF+35a7CLgfGT'
        b'1l9F9xQGx5sSzDhT10p+CndSV2epOKDMZYemb4HbIdBpwtJ+nAR4B3qgjita8ovS91i1ky9+oZIgEUjqhckvPs/ZVn/ty1daecMkStkuIkHgzenTnKApghxF7MF6Ew8a'
        b'zFOADfgA86NOXZ8VJxXR14dTv+f2qpnqMTt18XvuH/xbYn9K/ZDvewaZgiz9v28ziFBRetn6UPRnnaaGricab2RVfLgzdMctaHE3fL878d2fR2qOHq+ZlWz4zqs/OVTo'
        b'8oOiF7ZOvh1UrtXUYTUx+JdXX2gf7Jh66Oy5/nvvxe4+NP2dqcszg+8cnHnl4Ll33n7rRY8Nd89IvvyDcOwluaPXt//yT/HSbFKoMocBjoGT1lIrNU1CphffwEXNnmff'
        b'EZbLbH+ZAr4BTC4WnrWKXsx7WJ710ID3OCe5vRfeM3F2c5WHcql98DzybWXtAzRMjM2xQNuDi8lXOCiCexK8zSneJ22gDO8mSQP2H7MOpulxtkET7NmwmDOqESu1icI0'
        b'TPHdUu5Caxhv1IR8KJQRcFZNUiNKV+eeRrLf1LD2jpw0xZSjnU7fnnaqL1Z10BSpc5Ud5DmXvLYwXWcVmkYTrbSncUzeTvT1AgFpA4+efSQV2NM/45+JAFfrLCfAT1ks'
        b'HSRnwOMosMJSgDXvXbdg/nlJTFBchLdDiNwynGZb0VzEaU9GlFmuJDM9KXI+VOa3FeWr5avni/M1pG46zXBNKbGWK1AgYi1PxFpuiVjLc8Ra7ob8I9HiVzckqxBru9BQ'
        b'Fo8dF3ZlZQQN80/xvjDedRcSn5gYlpQQHxcaFRfxFWmSREJtgpKTE20Cl1SjQI4MMqYQbxAY6J2YEhYYaCqNBE8NS+SCFTgn7RODBT3VKWsQEhTHiHNiPAtwWAxBTQ5K'
        b'pHswCA6Ku/R0DrHCg/eYULWq/+6pfOOreA07COZgTEoIC+F2aMqf8qqc41EeQFxKbHBY4jf2Ri4BGL+MRwH9VyKjQiJXsDBuR3FBsWGrriCej55ePIfI+JhQAuplDPGx'
        b'2OrYoMRLjznSly4tyYBPRzA38GBxsVeikvgVEFePjA81sAlPiQsh8KBnFuXowFUHWlx9SFBMDN1xcFh4vJS/LqUk80CQwsK8mRc8aNVxlsPQU09yKX7NxuDxXIVHcbyL'
        b'8z4tnlc6VrBl8JOjLM94+Jr3GYUgYcTLw2Cf1QGz3dy/U4jKEBKGhi1e1eJYBPo8lKweXnw8LDwoJSY5aRFFlsZa9cZ3Jhlw/2TRCk8sboXEIoVMtpUE0hHot28gb60Q'
        b'ZNSkBG+lILPTnZMitkC2GHM2JFkS8RfGM19XDzzks40HYHAHDuOgUuploUCIBQJswofYbSTkk3bv44K/CCaZ/YxUZigT2h+GgpTd9NUBNVV65zQvCBmamxliwS7jk24k'
        b'E/V675NNwNFkH963DLeNFayvQjvXUtPoKk5AK1e4/ZFDnFc4OG845+sMuSgPLdAvrWp8ZY0Kq1pnaOHzQ6G+wEjAZ4VnkehVyQwBS+5sPmjP1CgD582cZQS2JrLYEGPK'
        b'bSMGWKn/BZg1wSpZgVCDuf8qN3GjN8nzFTssdALDXnGVVtF++RBfPc9iX9XGV85r8x/O2vAV+yx8frdBUbRJwGVx60C5GvbpY5uIK4mHvZDNFYHi3ugKURCo0wsWPvsO'
        b'v3FaQcBF3WLhmV1YbObs5uXEmXxP0vJLTJhAKd2KF3axoIIyJ1NnV/OTZsayAiw2Ur5MX/WlMJM+jiErcPGYXFpiRIIR9Hif2C4VSo1kBaS4TStAG+ZCh4ORPHff4VAd'
        b'j8W8m/EM1ktTtFsvcpuJEkelyS6maAt3ERy0cy/thTs0SjGfHAh9CVyCNra5c3X6baEPuV5xu+Deoyxt8RqccObMqPE4gx0u0mRHNRzjUqU9znNJzBKaYpKW27gsX1qa'
        b'LP3Aj4fPW9CoKQeD0oRpPlkaq4z5bOmS7TBkArOpqydMZ8qEn8EhIyXemptNEFDAHbxYcP4ql+cPbVekrQhwIRY78f5Srr806rP2HJ/ZnrfRi4+O9oCBZZGdlhIeujZA'
        b'pjvcW8zzZ0n+TdDCId4FbMQsR1h4FAAQj5Xcxg5BRaKLuTNmixcz/UVYj1PRXCK+daD1brbY5XmuXJJ/AEzwWf45vp7Qq/1YLGkA1vNV9Bew4AjMX1tK9efDVKFIwG+3'
        b'QxZnz+HCsuxxPnXcypwffBI7DEKwdckQwBsBNGL5wWtYBzkWauJJQrQ4TAhN2H8QM6GX7w8ygsNQ7WXmA6WqWHHmFOsmZyaEZqg7zGXsv+HG6zoWPve1Q1UP8sn0J67D'
        b'LRy1pg1Xe0gEImXaQSDOGSnyTTTuHFVKUk1MwRFlHFHDHMyGIpxKpjuIFp+EAme+j0OrRnQSDGQsPceeScLxFGbg6BSTBN/vxbXJOAv9zknLnrqyDmeTLyskqqjKCgzF'
        b'EsyODeb6IcBdKLqBYyk4nnRZ+TKU7r6qlpgiFmjpi/cfgvsprG7TXuxVTbqcosiNo4YTCjhCE7KH5fYuTn7koqyM8QauZ4gmDEHL0vMEJP3YxD+kFSa2w9tQxm3Xyyh+'
        b'6aEriyuDHpzbCIOSHVvPcg+dwTxsXTbWxZPJiThOyzshtoF8bOFqG2zGOczCbuVHwxFRlhWoy4pwEJrUuOs6puWlhJPJtFxlB+xUUCGxXuWGCMbSsZsDU2stGKHL9FM9'
        b'dYpdpQxOsz6R00ncKnxJR+rEeVzwcsNKLyzFO15QykpiNggJrWcsuRnEftsWZ2A9Jh5NcdOKu/u1BE4lSTipRp+r3RBhp9AYOpQ5/dt03UUsJvrossvN1eMM4yaeUr3b'
        b'1EWPZibCedIVi4hmQPYZhSQfrOGQbjtU46Qg2YWVGxfaCOhk78A8XzluClu0cMyJ6IWLGQ4GEnK5SwQa0CSGmjAc5Yj2thvrBXsEAnmLjZuj/r1BxFPyP3qZCLzZh0E/'
        b'T/zcLkTA94EQfH5E+ovhUSMJ11FIh3Wd6FkHffT7VcFVrUC+b5dsBkxCLfQR/0gXpMdADt/ZqAJKoDnOWxrLBTWwwA3iJNkLhdiOrJ9SlCDKJybq/sVPhUkxxGO+8Dod'
        b'63kw7mdH1e9e8Hw/oPVfla5fhh18fWF31esnyiqshe8LzOXMDY+qR/o+PzqiGXjh7R8I/SsOHC8yiPjuac925/opF5sziqq/fPXawYMHrWbueV1uDzMPnPdf1343uPrF'
        b'mMbtB/f/5f0Pfxj0kxfy9+j6ir47n5Z79qV0oze3Gb6e3P3m9Ht/uFVkldD8m+CEG392VHr3+wc/+f5vav1OFvXGud3J//5Qj7aNd3aO8rRLj9w7C59Z6z/vk1U1YTES'
        b'kmT5X906cL/g18Y+rToD997a5rTzjNqDgOrCh121f8tz//C29e5zqtOf+YW/Nxiy4eOysg+C3zc9/gP7FzPOX9b9843m18M++nCbR19WYrTwRSVDzw1TGxL6tnv/4Vhj'
        b'9sHTcRMlP+l/a1x97IrrTNeGUL/X8gPVY021Tv1eLSY5dGA49bV3Xn0n5dL+/nfHU4tr/3D9b9dCu7a01LzhbLg9WdP4p5Fp/zA3Puj2ndGfNZ0IW0jreL73mnm+ZMfo'
        b'w+KL1+be+fnAoY3hoWk5ZQrrotYc1n7g8Y8v0375l9demZn88mKpUaOxTuKnMwMJr1neMPuDiVztXwu0Ls4qvSKwrX7RLOLD7+0bsr/zzs+F8Qb7X+tRnhCfePG3P/f9'
        b'henWDc992ZMT3dX58VG52lnj70W+v/mf65N++kM7q9qPsqY1MlRfvf1l129///GPf/L2iKXPyE/t//r9lz7o/pWPIP9HzUVX868c6HnX8nTQw3K3jb+++dyvNf688Y9/'
        b'fd5N7ryuj5o3nA6fUvlFS9n5vw3Xn/jY1nNDzicOtvvWn/nU9EZr+tvmH7z/kuPnP/L6df3A3Y0zyf+I0TRven/WwO73L1/7+5TJP496XY22PLL/p8+9FG/0+d90DR3/'
        b'5Zf5hZE551c5qwejS/7TG668B1nzpBjuh0IXX0R1FvocsAC6HskOqURVGRlVgYqjLosxUP6bPbgHNDBfDCWYo8yNf1AGR1yhfTXDT9d6PusiU3jNxZVoPVQtC4a7cIC3'
        b'aw9gLfEkaeAWZJ1cEbjl78aH4nXIk/DHxZWl4EPOdESibT9fy2MoCnIWg8tYZBm2wYIV9npx1iN/AVZbYPXq1iNNH26ERGJ55dC3vIyZxdot0L6bN4kNn8cyE3c3LCXa'
        b'C4WSPUKi5iO4wFc2LYd2wWK8HDMrWSiY+m/hrU6FpuGPeglA9jY+UK8GC/hDyYUxzGHlWBdrscLtm1sP8icGjQ5Y6WICg7RYYsBXRTdwaJs+1vOWtkIscoRsyHmiOi02'
        b'QA13Xr5KUCZ1w0FhFG/EG8R5voLH5EaccldxWRIzufhA7LDnNhScBhMOfAOpXXKkMbQKz8hgJ2e+S0iGGj57AOu8JBIh3IPsAP4OW/Ah3MZiU5IA6T0o8cEiN1Pi8LvE'
        b'pCp0RvHnUYKzKi6u7jCruRhqy3nptCVc7OAWaJNcsnskaCVADn/1eZcPLEq8p7GXl3j3eXDfXcFat0W59gLM8XJt9hXeFVLvHc9VHuqC8eVy7X6s4j2VRVBnuCjXQqM/'
        b'J9f6JnIgHU/3Ow93lJ8Qa+kQ7/MXVAhZdlB+boVcGwu1yTt5Cb8fm01Imeh+qmR7ACr4Zd7eeRQacZYNxPsnaSrMFMev2c7dh/9G1pSJxDgPVtvvhsgfWoyd/LlCICS4'
        b'dZGA0EKzPJJz1C7jhAoOCy0hW2iKrTIKAVDJXft667BEVgmweBd/N/LYIIKidIIprivzBPRDqbTWHxTuWh/HtXIXrHeQwF2cxTy+cgm0pO6DPK6c4F5CIIEctojk98A8'
        b'd4PYQbpn61kYXeSTIa5c2KgejClL65UUrpU15aqpam0VY5kNjPPhj91YY8Y/Ye6GRSHbSVanqbFOQoL4IPJRlCrYoxKHFdxjHqZmdFQFRGd090qOYOsJbg+ukOlrEnrp'
        b'icKW0rKW66L4aMxq1WOs5CHUPqpYpQSlImxJgyFp9+xWqOEM3YWmdObuIkMdfazCEr5ETTZMQ68DUZ+lINrFCFoSVIqkJWoyPXBMLdUGGqXkUAF7RIRv1dDCo2Ap9B5L'
        b'YS28d5kZGTLwiRDBaAb0Gan954lGj2y+/4u9n5c7woNCQ1c4wv/CJKpvZwbfp8z1XpblemgslkrmI0xZQWQ9oaZIdSkGVV4kEuqwLs3S2FP6TSQrXPHzuURJIlzx87nk'
        b'E9lN8tx4fNcP3n4tT/8rc2ViJKzz86eyyrJCVnxZnVuLqlBVpClU5UzyfDeQdVzRF1UuDlZVKOLWqcoVmXnCCbnsWKRGewXe8r5kEk88zqzxS8bwxBMrDfn/WQFsOX6e'
        b'RwNzM3KTmS/NzTkBTtJvRUrSxJdv5QTIFHxu/lV+2GVHYCR+R37R/fkoXS9EInj0n6xgmQmMBSpztn3e9q8gtf0LOes/s/2L8jXyNfPF+VrhWlLLv6RANkeQIZOuyJyz'
        b'Usu/DGf5l9yQWeam9RKtYvk/kyCNuF1p+OdM4EFSE+6S//bp5vTFJ1Zm6SRLrdHLhjCVGqVDguJWtVQGM6eDAddEh1kVn+5ieBbrO/NnrDqr8eLyjA24TBzOULq4Dt7s'
        b'zS+J+TBo6XG8qXl1y7eBfXxomNUBg+CgRM5Uy284MSwhMSwpjBv72/mluQOUOioer9mzmoeBhl+9xoTUfr1ovWcG868z8H5bc+7qjW028cFeph4yLqytdspGrrG2yemv'
        b'iPUqM1LAob04nsIaUp+CjvDlNlMn7IMqZkTEAg+vJQMqs56mY5cCSRxdfL1jbDCAPObPxiI5zqXthIOcXlx3WFHw3CVz1lnQ9L5ZJN+R5IuA37COJJfe5zuS/PkLLjQT'
        b'MrFaYgLdTIYuwHIvZvB0c+VYrC+TrVcE2pKCv0y7F5+J8lTBzuPQz/fnrTm4T9qE+Q52CNzCI/jU8nbV/xaoi7qj1SwCw/SsP4ridfO36496810Q950T/FwgcFQLzIy2'
        b'VhWu5b92aD3KfWviekn4QnK3jMAg8OC/157mrbuGWASlXMtuLIFMgSVUqafYsxVUnPBZbsHGAjNnN6xmVlsSTE9KjeJOXJ+F007Ops68CIhTWH4A8lSc1SGbM3BAg1ny'
        b'KhEGi7e4z2VlgAHkJUjLVmIFDPpwwTzhUM9VmX9UYt5e2gcXMyHXmLdoQnHwklFTPYgDBT8sED7ViGyIUyRcLNpCIQseKmQE8P0pPUPEgpjTXMdL15dI9OFP8Wg0f4rP'
        b'OfoIxgWfuwmOZqbryWTfSJRjXIIZxI1k+OboI3uhj7eO7MVhwdUN0Mnf6SRO6vNy39Z4QTqU+/INvnOv6nLWERxyEqRJwjn7jgo2wwxvHCH5rlYQRafRyhsfb5OewrwC'
        b'LPqg2BELZAWSfUIYgp5jnF1VjbTQO4+ZPXEiVXwBFzx5c3PJUYIpTiPQglZpKVJ3nI2SVEfIJN0jmCt+/hXbCtukn/9Ly045r+Pd+fL5v/7kQK26VnTvuIX2be/kbSc8'
        b'Q7v3KId8v9266619/lt1hbpGhp99oXgk+16VzTuYNvmD32Vsm69661KBYdxzv/9HzubS1++/tMnwtU8H6iLl3t77mYtRR2VY/IyaZWXnSxeswvvDD7toXWj925G/rP9J'
        b'xo/cwz/xLNzacWNCqBfsYJM/WqqQJv7je0r+z5tZ/OHyf19M+O+/VXgd9gkyrWoLfPuFqqKbP3jnl/WBOW2WoTEvf9y04DncVvR7mfHfndu7yfRHvQcbur/on+kwms2J'
        b'i2p1/eGYbeqd1J+cS/2la4PBxQz/793+0T/u/vQfFUmDb3V47n2tLO63jp9Wx03r/fuf1j9QSnv5hVdiVOYVckuuhP19MLQrdOsXCT9tUuqN+kdk8j3LNPOPQmVsPpry'
        b'/H1l9PvJme0Z+rve+nfliabCN8tk7X7rn/DTS8lfet3Pzyy57N71kYpO1uvHXlwzq/PD2GOv7Z1/58H8R5mvv1k+YJy+piNhPrD6d7eHok4MbUp6q3Ak6Mh7ema/uZnc'
        b'esPc52i8T8J3x/03tr453mfz15+8t7Ag6P6k5h9Knxvp8N1R7DCb019JUn6wmCBXasaJ51ex1INXXtOwaEl/dbjO5+XVX8IczhSxV36lMQJvW3CytxEpquXYco0rybBY'
        b'kIFGb+F0XBzZ48Mwah0+ZKUcSMfFUV4xhm5ohx5mg7hxXBq9ogW3uWj+dEK3Lj7A9DYpQU8G82NpJK/zt0GxM99JUQbbxAIJa6QYgsOcJmhsyzoIltHiumHC5FEnRZg7'
        b'wy1NE7q0+H4yxknSbjLp+znNOgMGPPieL8U4/qjvSyrpdpy2MWedbEKrOYm15kx7V9ggggpsxwe8JjuB+ViNtzaYLKsfv4mUZEan5DSwR6rWN7Mki13L9frGLZy2Y35Z'
        b'n+nZ0O0qtdyo7YuBB2J/emKK1y07cdKD09su7MFyN6KmxDRMZAXroZGUy+0wzZ3v2sPXcdyQDcH1o5PVF0kisJybYR+U23HvXzm3RCs5BRIeaHIz7MBKLtuWtPIJKOeU'
        b'yGUqpAOpbmyYk7IskYAeirJZqUBC60HuHjEX52D6yc4IcoJNWMLpkOd8uRPdSxMVcsobzGgs6W8aOPMfyuxa/4sK22Nam/LyiANObetljODbqW03BebKnPqkKG2NKC9V'
        b'lPS4/jX0iZi+EbHf1KWNEvm/Wdcb1vGGVdRU5FStReVOnVOtlLl+OCxjiVe+FLk/dbh5NLk/09c/nnuwbD9SfUuW13Scl7QfpnIsU7DU/6fP10iybDLzpRk5LcuDaR3K'
        b'iz0Ivp2WRXqWxXI966v2vhjpZckWYiVaRcdisiknl7IkMD4BQ1qPXsTpWWKmaYUrL2lVkq/VqiJIq7JbLfh1Uat6VJR+KZaVC4H9Hw7W5t9ZLPTCv7dKGUZzA3s+VIZb'
        b'ylNCgLjYbqZ60aMnvTys91nsZqpObFAyC/RISk6Miot46hL4CjOPwl4eL4bHf/9MCSPy7ikssQ6mIceeFwCxDfu+QcYIycL3HTgpKQiyryy6nvfjXan3OdGel8Ga3LHz'
        b'UZH5Pizgvc9KUMPJYObYeWGZZ3u97aJvG2Y2Rf1VcEKSlEVP/STvRbOiERWw0D7+x4CmQJG6/fcFBbvVXZ4TaJuf2rI51PCu7P6XdD7t1DP60btvXvvdnu96fNf//mu3'
        b'ghV+dPGl/TlRb2/92Uv/5fmzF1947mrJB5mhLQd/dVn9127z3RfC56K1xzKMagYHS9Ut/vvzt+5dCDEZDP57xq9jo3e9ee5K1sKXgrjtW9994wMjGd563G+eaoJ5JssT'
        b'7cdxhmObF+Jod0vpKE5QIQ1ozTvOfb19XRoTJFL1H/NqXD7HGS3PYysxzmINOmHe6r2MNTJrO8fUHKGdecXLGRddNKdrn1qRbPIfcYxlBF01hcO1FSTd/VlI+k3BusXE'
        b'FL7b7SJZZ8Q7fcNjpGflrCsJ70o6tIzwfruy0ERVufctV5JWjqqeps+uPjNVLdyynKp+9dZYDdT0qARmhPkfLZO4mOrS82QwamJIZFSqtLKOtHzrilo+q5BNe962EXOV'
        b'M4ZExSbEhDFzTljo5qeSWOmmHq8rQx9/k94fglWJlMSdS04jfa4V8nk31eM66qMwp2Bd+cvOUdhgGPXLV+yFXLr3vZLnWSL22efefn68YsSp9ZaRzHc1QyLDY4JNg+LC'
        b'I4Ndg8558HUhuxrl450fGEk4dNsYihWPUB0rIggRSy7wHQofYjaOrnB6mWA9tMSZcrLhCZwSPunB3IzZ8g5GyQzcLLDfGscYmo9gCeuDyJtuTrpd5p6HWbwvErhAnxwM'
        b'G2Ph17YSUw/iL3cRupI4fLV+Nnw9wLB1qTLlkvH1sRlW1h73XImRK4syPnqCQzJv+q1eWdrA5lsjWabgoxVJo1+3TlZYQcbd3dvB3Ujkzv+v/jXl3x6VlWCZrVyuG5db'
        b'xMW3c/ZtTvziqAW3G/4o1v5vi9vfkHYn7qdfVZWkEpm8SKKkKNTZ9HglN3V1ZZG8UFtNXqiqSN+vk+ebm38pEQn40glf7rihKTSP0xQabJIX8gF2k6TQDD+ZUC0SGELT'
        b'tZ0yqXgbJlL+LmLNumAEquAuVNnGY6OFOuThFM6u2b8PMkNwSNYGC6ASquRJ67mL2ZtUSH/MhfvQD9XHj0OrEr1ZJFyPD2EKH6pAvQ1poWUwGkSqZY+3CotWysEh20Pw'
        b'EIad4KEjPVWORVe5KNZ+8+vQ5gqDh67jPHbJ4TD00s/MXuiANuyMuGy5Het3Yya2xEEz3iI2OoqN122hGDqxEEZ0HS8f8tCB4q2YaZ8RbYWlOA9TUYcw75Ljuk1B6xxs'
        b'XGT8LK+Ze0Cbn74ZVOPEIZjGLhiDijjoxUrW4MIJJg/EGmO5ZQCWqGBnKA5rkexzH6qIvbfiLNYE2mPDKatoKA3BAVlopiPNi4cRUjibvXAAhq/EYjs8zCD8r/WGyrXY'
        b'euk81kD7/jU46ASzFqyMDE1UpnEchrwgZ6cLLWASG6xhKAP7TkO9EDuhgSjTbWiiv8sjoRsboPXKRrES0c5xvGdpStLdZKS14iGcgPwQfch0jIVboTRsrRvMGYU4xG9y'
        b'wLIofIiNznjHTw8G0uzwAYzSNQ3bykLdaaMzXE+fO5CruMMbx/SwBVvpX1NukA9NZ+kw7kCtKU5ZH95uu01bC0d96AMCjfNEHLFXXYtEnAq6xllo9k6ibypVFbfgAr3V'
        b'iyMwREsaFmCtVdhBrPeHRkuY08R7qsFuUBaRfBgzPbF2IxQH7JPHBXigrwUPYmBhPeRF0Ov9CaR+1+3Wx9bQLT7nbHdhNcHCA+hMCiKwq8EGb+W1/ulxB6/huP6FDdDg'
        b'Dq1rz+MQsxZitzxtaJxgqgFbj2KJPOSfwBkLusoa6DtAO+2n9U1Bzlm6hXKzIwQSRWkwqrsei+iMiEir3hDjHBY6bnPEspRSEQvkrD0Ddz3toIzgXhnmcGzN9aN0wV0n'
        b'IHMjNGGdmfIeHKQrGoFm8QnoDAnaagQVkRIoNri5CzqsU9Ij1fAOQWMrdtPhliQE+sL8mrPQcBQaCKfaIScIm4yx1mQHPsAZmBLDsALeXo+TQTIJeBfGz/hdOYKNGV4x'
        b'JIw20jnMG9ImCERwIM7lIA3RrA+NmHXqLI1ddRZq90Md5AcT7mWJDrhhFQyb0TOj2A29GecztNTP3gze4xiBTRpX92jgAO20mGA5h9Aiey/hVaHjJtdtV3cQtJVDPfbv'
        b'JijvI+h8gAVBWBUDc7SnE3TXhXLYcRirrsG9FBe7KBzYifmGpFEsXN9vfhPyLip4wQO9jawUGXZpWEviWbDnqAgr0nSCTuAtGFOEkhtOUIdZ+o5Q5geZmBuqBveg28Pr'
        b'jGWI5o612GPnqKitaW4hs97qDOHQXVcs8KLbrcNePSggopIZhJ376BpnIRtzxVjlDpU4YoCkmBSdxV4Yk2gQ5BXpkmxRDowu5QZYspOFAuyH8Stpa6F0I803QADVnUaw'
        b'kJ+uIU/4MBaOt3H6uqU2VNMZMno3THRrQj5C1RnvrWWRHed8sI/QLhenNl2AeTcXWIAuhW1QlUQUoRPyDoThWCwWnoV583XMyOfvAVPrCd76sNQTqlycNfyv4ATN10mA'
        b'0HwesgiDFmhbWZbYp7XTa9saD8iiA5/wwxIiAh0xdHzdHjBqhA9koC54G7Rgg2vKj0Vc+G83zBJM2kI5g0la+7QJjKccwCZ/CY19H2/FBcH9y0qEnLV7T5lCp3qgC/Qc'
        b'hhKcpBObw9r1BEsPoYi2NwpDJyHvPOFr7hacdzp82BbrnKEtVF0RcwlmOwiqpuDWVmgwSCUgrhUdhrmrgn3mJ7H6UrIJXd0YdJLIVAQzhDtVhHSNwecvxLGGO6bYGE1H'
        b'PsvCM4sIWnuhDWrwtv8JoowLJrq+yRcuwn03WmE7VuC4IWFH5ZEtlmlYoq0A08thljCk5tRaWsfEFcwxU7gJ43Ec0bytehXq6aA67Vz3pW8OgWH3a9d1xBcdoVgXssJp'
        b'Y+yUOok65ew7TBBcJxcLpdAVANUqdM09BipQbY31TnA/mR7JQraTe9hMbKkLMtVEmGNLNKRjjRxMWeOM3g4CiFGYscSH2lewLW7NVUlkDGbCHcLYPLytRgfVTtvrJGY6'
        b'doputFUDi/w2RBK85eDIUWinI5/z30nMadAvTZ/gtyXWFisCiYXVGkHPFUKJEnO6ilY7SyJyhQSZxDr991zai5WG0didcUw1nRaYA5kEza0wttvAMDQIxojgTClrYzXO'
        b'YI4yFjhAs6U3wQO0XKUFFGK5IUxAC/RBeTq2yq3fRoc8i+0OfrtIzm1SdDCmDecRhbxPfLvxOIw5RnjSRY5BdpIfXWc9ccR7MJuOxalQd0EuDGtswx3NOZ5e7pJMDCcv'
        b'hahCBT1Tc2g95jjqnsVaaLwERaJUPWgiIKdDJCCH5nPRtNAFUv63xzs7YGGcClaG+cptuIgD66CWAdcuQupWBw0chZGUNwm09++gcyRiG8fJGHM4ZIKTwhMbA+G+HNZ7'
        b'KgphhEUIlxHm1EFFMowKiOBuW4OZu+mI6/Sv4aAczEB7mKMhNNhDnxaxg4a19HiZKjbJxepHE9g0qBFG1lka4cMz5k7QePoa3taHEueN+4kTTCnS6TzEYrlT0BPIsCVI'
        b'mODPhKK7cTiEsxd8iWYwEsw6MJEQEr8PGrWOmnhq4pAfVAYeh+wTMKOO9x1vnqejub//mhaUeLn6Qc92HL+5wT6QiEcvc47F0qH0QeP5q0KscbCCaW+La6r2mAWNUHc4'
        b'hJhzNl1zq54GnXcetothQQOrzuiqryPOV6QNFRdcg7wJdeetTtvEEBJXn4Vqc8hx1d6ljd0x0H+UkK8gGm7vwGx7IWbKnIKZ0GNwxyEKxg67E9UoOHbA/sSNdVhP0E+k'
        b'sYPmyxfEEhNoxRFZuE9oUKhD6DJKR1WOTZYwDyVrCUubtsNsBk5ePkxQW0esrgxrDl3GVjuiKJmhp9MgzzGebu5+BtRkrCG4mgi9ij0RelhHdLCFyETRQSz11diHBPAV'
        b'2O5IshGBdIfBflrDXfqt7ej+NEd1YovH18GYF8HhFIxf3UM4P4+99kQOe4nmFsO9/RuZTJYIJeEGOxksYqX2EY4WtNIyi+UJQ5qjoCZYIz3VDZtoonFCrVqoiqIF9ZBQ'
        b'kCOCshQ6+5K112iHjawME/HOpLPQYo7N2K7noeJF7KIrWgdbwvDOSbriTpz1h7uBtMrBw6QqtmPBAbiFbVxQfM0ZGiL/YmQqY0SYFbsWxxKIwoxi7jaHc4o4vH63w+kN'
        b'0HIhpYKJz/nXCW7uetIulsQIE3wgjMUyEiNsrU1gygKGU5V2HpBLJDG2zsEHq47RVuC+Hd3xPM08lkjnNMmo0NktkGeFObuD4C5NXQTDCddslTe6wDwOBeM9emaQCEjt'
        b'zU2QaeJDF/5AYk2ksAamjfcdwb4LJKTdwekwEjLLiJX1EpeeQCJsOTfN8LYmgW3BsQtw3xlrPI8Se60IOwr1Z4xJ7miHWRuarYwkkvswp0bIfRda1LHHCcp2p2GVqtum'
        b'iFiidllyhCDN1xQDYHi7zXFXPVsVgrF+uKNqtkFCZ3ZXUfMAjm/aIS92wOzNdIyZ2wnuOzTWE5cvozEH/DHnAty2A6JNh4kXEnkiKQFnArAJmw9eJpJ1B7qImbSTsD9M'
        b'tyQ8ZeYDxdvjiFc3Qr8H5pzDVn8bKHI1dWOlcqDQPnq9h+NpJscUXbgBncFGmB0CmVrXDLCW2FXleZxMJOCpOY19gVhgZgG1IoK0e66Yb0fwtUB0fSDiAqklFUS7C9fq'
        b'0RGPB2L1QcyHe/HWdPTdlpB3mGCmHSt3+2mH7zvgEQztgfgg3p8I8/2DaorbrfZrr7UyIqo+royFWsfdd7KqXNuh6QyNWqVCgPUwFoo8fQhJZvzh/g7o1A7FkTiasBEb'
        b'Tqvh3YuEDB3nw9YQ/amCAXMYUqLjLMLaCCjcBKMXEi7qHoHeGHpoAOrDiULUi5kdN9OLAH7cCsptYX4nMdxpvHVTGx8KYlgmVk0Qzqf8lMkRhTpWDCaz4jiQnCeQTMO+'
        b'MOy+Kk+iT47WNTrBrB0bSMYd17fQxGp1EiZ9PdOdoOLmpu3XUiAvSO9UgLIncfA29gM5e4ny1xAhoddsmeh0XV0F+tPoZmfwns8RJeKWk7CgFogdWB9N3LZLBjNT8I53'
        b'GMxfi6OvGoMvkCgzyEkPQNLDLMxHEeyPBethbuIm7DAksGglzOnzjsPK6wZEHpqYwBtJCyi4aBOrp8T6mxLpqKHDKHbzI2GvN8MrwzcybYuyO5LM2oYdzJHb5X84TZWA'
        b'qBgY4lbAg7iEw5owqZZMSJKVSBJFxVl3K4VtOBzsjtlQ40WPTMItOexVCcOC06yZKH2cnwANaqSo3ILmNBwNIEgd3qVs4kz0qT5K3SH66mFSn1o3EIYOEakpXm8oobO8'
        b'Y0ESZ4WuNtyOM9h0glC1fwNOOxLVKiXtZJw48kwci8LHqsvbsXMr6be9eCsDGgzNiP49kKPJcrDTyjHMKm2zfzgheRYhQ04K4UGDIlTtxrJLVtjoup1QYUxLIymYiN8c'
        b'9p7D3guENe2bCQKb9tMUvURBpqwgHx8kxEFbMiniBaQw61poE8GsPUKEfuzgVlp6RSSUktwgg91nWJ4mAWv14Us4cWYt5krgNg6F0dx3CdwaBFuv2CacS9I5RXc8ssWY'
        b'MOYuVIYmQ9PhNCjaioUy/lgcDfWH6NlRGCexsxYLfYhTFJNw0qTtqgr3nHfc9CAQ7cfBdL8YEhZrvQ6f2M+0s74D0GGXaOwPUwRW5W4wci1KO5xoUL0aQfi4Gbadvu6I'
        b'1Q7GBBWDulswa5dr9Bk6vzZsMJLlopogLxUrXU7KCIRhbrsEDF1JyuACke9E7eWzh2K1Wf5QKmRzn5vqQrGLiUgghKxTRwUkZNw6xYdHTbMAdpYVICQicoS+cdfnIlVc'
        b'oP4qi4QX0itteMdZgI0qMtwru/exmn+m9EUg1DsJiL8U+6WcFLNENlfa211iR6WEGA1HlenMh24objqvADUHPdWCtIgtVZoTOLTSKd1hAvsOvHXSwQ3yog/rGBGtmcKO'
        b'tel0jy3QfFLd7jyR7wpoCmYFaYnAjuG9fczqQrp3ZZp5ij306jA5LwM6woIwXwlaEoNoK9WwcBgyfU/jHXe6R/qekDH3BP3aDl0CIrD5ZzRJgmvcRdd11/LcNoK8rA2k'
        b'DowY+9G45QIPmjM3jGjqELHgarpnUnOirkOeOfHWSm+o2EGawihBwzmSXyp3EI0bgKoDpCvlJge4wUMXIm2NBPLtxCmKCbBG9Ul3yiH9rOCA0XXItyIBboYoxTCxhPsw'
        b'vJlE4m6otw6zThVjuVyYGtY5XYKeffgg0WQTTl/EvnMn10CP3PWUMLfEACKjldCuwGwHUKe/FrPocPuIIGURgez0P0djldCZ1vhpRxPiTtMSKvbSdjtt1yn6KmNzSCCn'
        b'gDWIMceSVJlMOpkBJFK6YAklYhz2M/awxNyzRNhaDuLwDkKcLisTYAkcPVBxkGSictpPZqJuioS4U0US7aEd5o+fJ4GyGoqMoVkO+6OwwgnuHMH7Z0irKiH1ZV5uDRYH'
        b'bg4xsl+P/fJwJxDuJBKizBuppmBPSGIidtJPVYYKLbdwn89ZUiUHiBxXWuGoveN1jfBQmDBUgUlVvOdEiJW9Hwd2nSTc7oE8ZBaeQjXS4schax00BRAtgJojTufczyf6'
        b'ntMliaiAWPm0rjXeTtxlRcRiNFVMNKID+s10YCElEvv2k0JQYayFDbqMlBPLy7e4SVg6sZckxkJmkzJyDydsgKld0JhMQJUPU+chPw5ZGEzvcYLxAZebMBBASl8zXemA'
        b'sw1ngpkTE5+5dz6CFKoOKN+vu/6GCcme4+5Ml8DKcJjFVgv6YwHnDXSgJizJNFmPJK6+w/jgogpmqeCcEJov3jyPs0opXYyFDZraPm6cISo3eNjgqFoq9uvIrruCLaGE'
        b'HFnBRJpHTp3HImdtHTvSXRagNpGOMk9JW+ZcgKsnEZ4Kq3UENjUwtBY7d+u5bD4EY9dIH8g/q+dhFmInR1ztwWkfzkoz6rGJJmmA6n10IHOKtIHROCIvrcRU5iNxMgUm'
        b'jWAIig+ZEGp0YlMc/aM8dQ80EFcjAlXBwLQNRoxh0CKehP1mGxwNPU+HnOfmo8tETSRK3eFLRIj0yRKSfwh/RhyJyTVL9LHLhOjuGLZp+UD3FiKqZdB4NNGV5OzmCBI9'
        b'c44y2joCWRkxJOCvP0qSQttaNWbacsWudE17ReiNvUBkuIQ3AySFEPRXXNpOy8pmWaU3iBJM6xMS3CUtF7rcLgqiMf9YDJGcpovHIogtjGFTGK2wKpn4cA69QVI53g0J'
        b'haGYU/txXFcdHm49R4BQp40ddubsRIyxRzcMp6MIZpic30u6w1wizl+UOaSO9et3Y5VHApG0Ei1s1ST9q/oaSVKZsHCZZJ3xI9Cj4WF4xGobcd/7eMdPnkhSF7Y4xtPB'
        b'NxruTNloFKVzylFTA+9r3UyxUYG8YyJ3gvleAsBC6LxBhKAlxccJis8Tqc02gQfaYYSWc4QXkxm+scQw46BMjCP0734S9aaDUongNtleP4sdfmZElRqwzwhmj12EgU3b'
        b'TxJRqGaXTBfxkGhbPRGHAQ3ayjwu3DjlSoO274Wq2DWOHjT3zHpW6dseHtgRFc4PkNlyJHm9L2e20YSSfXDXC4uXlFtfmrsUavdsYvqtn6eSECY0scAdhmTNYOC8rA70'
        b'IBHA8b0EB0MHfHAeisyjDhCEVnJGk94tZkTDmKGuXsMUcomkEYjmwTDpBvjwioeZEV1YH84dtoMefahX019Hx18C46GEq21HDgmgZy1Rld7tUH8AMzcTpRuF/rN47ww0'
        b'WvoR0ck/CU2hfsQThnyYiNKKLX6JO2XEkYewZhd2pGGhOYxu9cacOAtojz5GfKGd9ttFgmuTA5EbmHbFIlM/4hyNxoTMt8w2+0Zix/415xLxoTuBWw3xjtw92vJwLzoO'
        b'hol2NdMMw+5yhAULCR6ktlcSxJRAezptmrjVOuzcBXdSWDle92iCJ9Jbak1V4iBX0cAGBw5EYZ2zTizMQU8KNh6AGbtErKWzK8dhn42w4C2wxlsq8rggplXmua2BaRlm'
        b'HGk7AJ0ROk5Qc2L9ugOkcxXRlnDgINHwOQKIIcKCKYKC+cukfvZr0aHXB4cwzAmPNCSSWiryt4u4rAwT57Ez2sM9KvwiCaqjqrSEBuK3fYrMk1gcArU++6HSRBdIy8jG'
        b'0mjlIOz3hnKto4EXrmGzs9uG3VhpgSMbIv2xzErEZFciQ7mkSd/DOde063QAxcHqxLpI+Ngo2Q41Wp6YF3LW8eIxNwdC8hJbvJNkHYrTW4gkDdKtFpNuKBtA9KFfyU+f'
        b'ozGMbN+ms6wL2QMjOLHFiJC3DtuuEs6VwbAhqUDFGnLEHXsTzq6hSYtDcf7UZbqeUiQBoUIBJjUPmhNRa76qdVNtJyFXPVGch6ZYEADN+2MJL6fwQcoxEmqOWR9aAdmk'
        b'206KRbrYjZVH1RKhXVs2eifR3Lu0F5ZRXrNb6Ox9kglkIfggBMdUCK0mWJtp04OqWKF/boOEQLyBeHcJyfD96XTed/Z4K5yBwX3YcJagu4EI94wSU8ihT/8MHThp1VCm'
        b'g7leDkz00aLBBgI2QYclDpwwRpJnnDfQARVvgXvmmwg77xyCxjV0Mo1JxHO6wmDkrD7BeYPIc896aFt7ADKDoXAXib62RA83nTFaT1SiKhJzFGAkLPEmsa0cGPfbRzxl'
        b'LIwR8WK55FNW0KO8n064HOv1AuiMpjWxNWINDsobptsduqwLd/fDkOt1VqeD+F471q/FyWRn7NEkKaecWOhsJPGCdEX7RLrCZhqkaot1MrQflOzGgSPboPuwIjYlY796'
        b'+AU96NRQvwzVa7DEJYIGyoLbpnKWbnSdJGTQsTyQGLglHN3vGY2DW4gy9BASNQVuwQUHoly1cPekna2AMKOI0JKkb6JbVTCpFI75e4k3E4AW28PwOgUhkYKpAH+ieR10'
        b'JQ9o1FyNNb7EwkuhTR5uRULeAewxIwZQcCMVqqz9kVnKWwUwdvHgeiIoM5AXtZMQrUsPWswIy+sJJ4ZJqW4KVFi7F2d1odbb2iXBkfhnN3TjgIReyYYxA+0DpHC0Qacd'
        b'9MroEy41wcL2NWtZzqExVlzHCjoabdpu4RUYFSfsOEhfVB6C1p2+OE28Ems0th3ahs3WUBd2lkCnAGsSiTfNp53HoT2HzkBOTDKRxtvmgn3QGZSmHRxMBx8TibNQGgzD'
        b'l0l+riTprZQObMSGKGvutgOkF05jfqKNS7gtUYICLLpmRuc7qiwk4OtVZrIx3WV9aFJaBjzwoH+2QYMraej3YCjBCQd9Oc44jrOHzh+GWkPimqT/OtriuDNJb0NKobtJ'
        b'jKvzI+RYkAsmWS1zC9y6liImNLoEI+sZHmURODNEmsdZEyLFdQSdkwdwXI/k3LNYrRhlD33bsNF+F1SKibndV2FP2KpHkQoydy3CyYmkgRznMwcMMC89nmTreeyyo/sf'
        b'hXsKOLdPLoaYTp8QW7xwZnsGZJLed2eHg5qSF9aEcr61AWbnv3mNdd9g9qw2mPZknDeM8HaMKWLYAZ1OOlh/1XPnuV20tzvYewizbmIZTugTYyzwh3tnSNaaMJONjLfU'
        b'g2EnRcL7fnqw1JLlicYQDsyr4f0LkEsCwTCxlrLdWLFejvbYoWCGg9cjSfzLC06DW7bEkcvgvhhH9RSw0UfPQY8Apt9QRn0DPjhyBipUj8oTyZzBTEeSZvoYQduLgwLi'
        b'3Xew3EI17BTknncxtE6OVsR5dd/0nUTgSSI/HHsKyhOw2tKLlGomg44diLxOwFG4E4Y1bFwIh1t0YUYRJs9ejTHG7u1EtaZIXcm9iDNpiph3wovwIpc0km6iOZWkrWym'
        b'w67diHeVFcXhulh8LjrqQoAVNrioCk/o0HsDUCkLVRq6hG/VMBWtfNJkF05uZLZPYtuZMLcOppj7rkt/A2l8JcFHbElyb95DZ9ECgxvM4qDSdSthRRkpPUkpUL+H7iDv'
        b'JE4cUiLZfZakgqYT6brYqnxDhnZQ5QANWgrXCeGq6F+VsGASF3gVmjeTPpmjae0BE3rQpL7fVvkKZjtjrn6AHHZ5Q1UkNEMfAVGZpx8zlmJXCjN30b3PEukdJgaRg+3m'
        b'WHAjYDMx6QrCLBKBfOj5u+60oWxfnEw3J9kMOghfqolXFyj5BaecI4y8B4yZkEjavo/2t5ABtzdiVRhJ3ROXCWIGrugRYPVlYP5NKCRSTrJH9llmrL+Q8h5JSnugVbiE'
        b'B0eZZarcl9gw0bDoIwaeatuwgnDAd9s1+rppbUSIgh62r7Xexqr84GAE9Ms5BdIck7TcDtE+nFwPC9i1P1qJNpWL95OBuYCzzh2CKgnU6BExn7uC9S7QKqZfO2EmjLhN'
        b'9w2ijeWETrfpOioVN2KbM9HSPq4iSdV1VmfqkDYW7oNZM2zd5obFMczRdZKZqkJP0dnk7iCSUqgswd6wdQT541cNCMund3vEE8i1a1nS2qosdLBm6yYjbNxxgiQGwg57'
        b'god57UicUMaGg5uxQ4WUxlx/FsI5fRT6FNKIulST+HOHiHObgIB+Rhbu6jtBrRJpCB0WatBitxvqrUhSyNXzXoPdW/fIymLBaXssVMJs+1OkEM+ak4SVfwBH1BJwYpey'
        b'iyW0WmG1nc1ROpQxaJAQ3rcTtc9LDzRQZ0lc00QKpiHLgKB9QEhy2c3U3QRw1Z6Qq8TBxXQA61BwaQcRhCbMj6dT62SEYMKCBI/q8EhosyaIZgb4aizSxbF9pNZURkCB'
        b'LLRGGkC3BIYO2+AkU80x8zTRr3HXK8TPH1rJklBdQZy/DUoMMceUDmdIB1ozoFaDwKNgC3Mpy1yX3RfhTaPfPqSKNSQ+yF5hMlCO1t440vhIoM8mOlEJnVpYf1w3jYVX'
        b'eNHpNcDMxdTt0GsGcw7QZiQD9ZtJvmo8Cz2XSOsZgDazAJKAiHXvs4nfAzPOOy9j63aoc4ZOE4sTOCZDoF97cjMz3eDobuJyPQxR6r00j1uRkN1njgtnthF5q/UMVA3I'
        b'8F7nR8BTgJl7XWmOuq22m45mCEjELLiEPfgQ7hqJOOuRAt5JlxbGEcmZsMI4STjNG5y6lLEgyXIjdC8WdLsWZSTmXqLL6tvswgxL6pBjzao1zUA19w1pSTVuLqxWhBAH'
        b'rlsIsOQQznHDmZ07wHKmJALhcRyyp3d0cZTLyvKmg+MMZCZwn1nI7B1paewNsQNUubCStNARYyngdNscrpqPLTH+eSx2lWG15GDgACtwUW7LvUPgrctb1bZiCzOr2WOu'
        b'dKdCxkOx2IjegplTHgJsPQFD3DdXcU4fi91k6YsanDkiIGG1W577xpPwaZq3xg3gfWaOOw6DRkKu2BddbyZUujiz8cpg1kRAaxmCWu6940kEU7xNzl2VWeRIkn9gJHTg'
        b'+vFwSWyvy7FCb2mbFAWBpu5mOwRGYu7j921YB7T3YsWCQNcI0wi+MNAVOfbh8E0hfRhnEiVg8WYO3Ghc1lvUi4O/FSYNEc26/IfhjGpfj/V22rkRV94d6ZHVTR/q/OwX'
        b'B2/d2na06FbH1i6DFu3mLWkvt/783UO/kftTSFLqnOVutcrf/P0XSX/Yn9T5+ZWflLtEvPPRuIqe748/S/rjhnCHkcnkjFP9Gn/a84HA7vxn73Z7Bhj2qLsbHfexLc3w'
        b'/fHUK+vFp3/2eVRTz8fjLXPlSWkhW8LXN6e3DIZ88IV83E5j/98YvuD1vYEEh8Pn/yG49/z1gu8nHN7ybqK/ReXR32S8EPvCpZ77id7Dp0ob/rv7fLHVj9+09OjQSfE2'
        b'PnFV8eNtv3vZu/Zfsu1nfzI8+IMb69b++Ix1l+fOa96jkf8lH+V/6uWTDecEbpGdNf9q/7n2jzaffNn67wbn3nCeiXMsPDl/L3n9O3/cGnnl09hX9t5N+b3ko787LXg7'
        b'7/1p01vfq3O1+H5J/3fLPtGNfiPL3fPuZNT6wV/1H1T6L9OoqtSP/vTTppLE17fsNSkePZE4darYPLn6k0+dRn8s95vvZPzivVdrXgjLPnDtjVcGLy6Y9P67e/86rc9a'
        b'7l1caD7YOb2j8I3Sy7990DxbdO3Mq3dD//KSts38nr/EjOo9Z+C4dtxtf6tv7If/ek3zL39Vu+Nj0fPR3tc26lbpHSsLfb3wbR2tW9/78E9ffnhsQ97uY6kvROAXN85r'
        b'Bn5R5vmFcK25y7xxY8PQS4bf+W75RxNy7T86aL+Q1Kb+HesdaTNr5yr32cz/cKdX8m8/dA0u+mxz1tRbWnP1b9YFvSv+/Xu+Y3Vba188+OOc0Vdtm18S/Tv9Zuxvj/St'
        b'q5F9feqT34dtzjphuvv7Va9r/W32fF3fQHJ+0QenPH735201e+5V9sck3VauGYHTPnOn/6DtM5KXEhOodf7tG/JBcrNv42HVhO6P2+SsNr34g870Lz9+/bndN8eu/Nbt'
        b'bz9+78gXfg5rfhn32om/7/zTxLqdYV/8decXhhdv/6PL419ac6Z/DbD988Kf1mfZnPlB+U3hw/nTc4ofGClyOWNRLkTPil2Z/bodK4iclF2CUr6FeiY2q/ERr6mGKxPl'
        b'+nAqmZVak8VO/5VtE4pIpMpbympLxkI+baqXmMSCUqKKggox+mK1xBRl4s6sPtqgWKCfLpF3gQ4uTcuFpO/Rpeeu4OSVy6Q/q8gK9I6KWakbi+QdjM6VYt/epFTlyyk4'
        b'pQZFUKImT7yqWEURh9VSZQRGqhLsj1ybzHoihfjC2Mon+aeg1AXnuPFpcDeJLExfhFa+CE0tKZW5SvKLo8njhBd2iXbtM0xmRTHVma8pCUrlL9MSk4jpFT4aEusclobE'
        b'CVlSyYiDciu+ScJO0VNqsHhAHleG5WLck03crP7fxp/+P//DSJ8jsv+//MG31Q4IiIkPCg0I4AKy32BxtSYikUi4R7jxS5GI5aVpiuTFEqG8WFZEP2JVGU1NTQX1jepy'
        b'6rKaitpaEpH2Sb0t9PxNgRUrUWLNArTFEhH7feNNGkuot/04+yxAJDzEh2+HiIQ27G/fpU9k9fzW2amLVcWa6iKh6U3BVpHwOP/NVpHx/ynu2mOiOOLw3u1yD0+oT/CB'
        b'4qNa4TgQiIrWtioFxOOwtlUUtetxt3Arx92yu6eAYmolVVF8Y60VH/jCRxWfqFhrZ6qJSVObmMY6bYyNrTXqH02bNlET2/nNHmr6X5smZnMftze7e/Na5pvb+b6fOZm+'
        b'nBTf5w4L7GhzKvsEtve5fQIsuX5seeowbmMGKs9e6vSnC6B59RYU/Nky8MwX3yleWGc0GZXBFmRDFTmhA4BQnruuPB+niun34Uf6w3SqsRavhZBiYKlp5eKCqLEvP8AR'
        b'Jzc7sEnrb+I465lpoxrzi/iJ3XIPvZJ/9bvbI+P61K+bbK63D0lcFtOWVJPTnrC5OP7Bugv34+/kJdbnfHOt68FLj/cW7+rRu+DRzoWkoemPYdk3v5zdcVw/LUw/Fcke'
        b'pZ+tvFuVf23zhd9uFJsWpfyEvhqX+XZGR4p3/w3P2Jv3MoNVpVuqro785cg+5/cH8Z4uTx7/fOXIvarA8aPaDn7i/RvjrtcNsh70D777cXzP5TNwe+ChqzVNm9ZRXDIz'
        b'/VR6/7+uVT9aWJu5aeioOz8Ec9WWBWe+nbNFtUxK4m2b2kbWN3a/rNwqbZj74Itla+uE7AkrchJ/7NO9SGnoY/9aWeOYM+RS75Izl2ND6wfn9194d+fF1wb+uiKt9vdZ'
        b'vYuvlF/88/KSFuWJw3lgbnVCU3ISkz0X5XuAvE6dysS2Vs4RH4eOm3ErXjqaSZApFzyAWtxTXfgY2i/DgbB+vTs+z9NJ9GmdDWaTVTolZo0Byn/4qYc2BtozrAc/EO/w'
        b'sJGwejg+5S7wOFFrisfKWQSzDR9MYSloiwXsntKBo+5/+R0QaR8pZFkTC/FhJ27ui9eMALnwahNnTzPDMxR0jonL0tEmvLHTtEsoMrksqA01Wti5CfhCIqy5d0WT4+jE'
        b'oBU38EU149m53jK83TBTEwQTHWhOoB10DtrMimPFe1G7cd0q3OApwI3JBQLXA2/k0TnbHMO97ESC323HrVNSi0ZlmegZG8yWQXgb07KwR68n3JlZBejCWLD8MvzLBvOv'
        b'jqkz4riuX1DCklctLvAYqXF0rM6AIZSNkknFlASsgtB1ayk9nmaiU8AO1IG3oaOG497qXCOssieV44QME62Qs3S0P1ZnZO38FLzV6cKNEAS2kk4IAujMIMoWoDErQNHv'
        b'BMe6QvheVzcPrQKB618noA8i6DOWu1p8PskN+aLFhzp30KlFU7KZzrlXCYaDVzOQGe25Q7rA4+UCM2orf5dp8/ok5Djw8ZdiJuFTGlqJ2xV8sooSk1iOSxwqWOcNYC2U'
        b'wU1jyiQnXIjjHBPwIbTVjFvceIchm2/GbZM7nefAdq6WNtInWXirDhGZs1LRUjf6dARtYDARY+aKUwtseB9qTC9yJVu4/FzrYjNujHrN4aUJDrQ5G7fhk2DTvZ7D+wJG'
        b'6Aq0XsO7YDG1B28bAsr3mMUmvCcHf85KkjEQN0GiC9y5q1BDepSp9YsI6EO0apHR4C14V9CJP7K64CkHXllo5uzDzfSGWB6NN5xOa6rVOcWV6nGlmbiu6Rm9+S4lqN24'
        b'v5YPGOJ2guvbOdyWRk+ndxHNfs8sHm9H7f3YF2SjlSbn5NQUkHyyFmnHW/E6Mz7SD+1m1m9odx7e4IT52hvj3BzeIqGmznhDI178v/b/aYCIfwF85FnkXgVGojgbk8fb'
        b'2NaLeaPZospM0IAByQA/sh5RhzJ6JB/693qyzm2kIbFiVCGF8EEppM6nYxqJ0SNKUCJCUNZ0IvhlH8WwIoUIr+kqiSmt0SWNCKXhcJDwckgnMWWUUtE/qjdULpEYOaRE'
        b'dML7Airhw6qfWMrkoC7RnUqvQvhaWSExXs0ny4QPSNX0EHr5LrImhzTdG/JJxKJESoOyj3TNNbSNHm8FPbmrokq6LpfViNWVQWIrDPsq8mSaSXtp1mgpBP5TJFbWwqIu'
        b'V0r0QpUKEfLeejOPxCpeVZNEmgQKb9K9MuwfO8aI1CH65XJZJ1avzycpukZiWcFEPUwZYqic8DM9hcShBeQyXZRUNayS2EjIF/DKIckvStU+YhdFTaJVJYokLhQWw6Vl'
        b'Ec3HoiYRe+cOLU4kBAZUz0iYUd8jVLALVqsAQgALAGoAdIBygDDAXIA5ABGAUoBZAH4A4LFqAMAL8B7AfAAFYAbATOZCBwAqRLUWYBFT1AGUMNUtAGRMrQSoAJgHsBBg'
        b'NkAxuzKI7qrh3WKAsqcSQuhI9qeE6mHJc4SKpT2yldGeIvkCaaSbKEbfR5n4o37R/UGK11cB7mOgbYU0yV+UbGNiQGIVRW8wKIpGl2VyQZDFEYsR0FS9DZ8s6WS+/wiE'
        b'TGzjabtHgtLroKRjKjwBKMJ/v3Wm92Lmgn8D3ZATPQ=='
    ))))
