
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
        b'eJy0fQdcVEf++Lz3tgHLgoCIfe0sLAuKXWNEBKkLgljQuLvwFlilucWKFXVRRI29l8QaS+w10WQml8tdcr1vcpfkciV3yd3lLtfi3SX/78x7uyxVvd/94cPjzbx5M9+Z'
        b'+c63zXe+7yPU7keAv6nw55oMFxGVokpUyomcyG9EpbxdOKEQhZOcc6iosCsb0VLkMs3n7SpR2cht4OxqO9/IcUhUFaOQCoP60aLQ4ozCNH1NneiptuvrKvTuKru+cIW7'
        b'qq5Wn+moddvLq/T1tvLFtkq7KTR0VpXD5S8r2isctXaXvsJTW+521NW69LZaUV9ebXO5INddp19W51ysX+ZwV+lpE6bQ8hFBfUiAv3j4C6P92AwXL/JyXt4reBVepVfl'
        b'VXs13hBvqDfMq/WGe3XeCG+kt4c3yhvtjfH29MZ6e3njvL29fbx9vf28/b0DvAO9eu8g72DvEO9Q7zDvcO+Iing2IprV8U2KRrTasDKqIb4RzUENhkbEoTXxawzFQfcp'
        b'MI5sRARzefBQc/A3Cv6iKZgKNtzFyBBhrtbA/ZwQHkFe1qhQq/HAWCvyDIVMFdmVQZrJFtKM1xXkzSRNpKXAQFqySwqTVGhEhoI8NA4wCJ7+UBQ3W4y52WQXXm/MToI3'
        b'tuUrkY5sFczkJN7miYUSJTPw6dzsPHLTmK1ECgWHj5OH+JhnADxaWUquJLKX8rNJy0K83ZCtQFFkt4DvCfiagff0paCH9ModlQrPc8l2fHJiAdQSMUiYhDfik55+8FxR'
        b'FEKfZ+fD46MAbzYF4LIwkrxCjkIVtEhFFdnuogWgJbKNQ6G4JS6bx1fwAdLiGUx7sWNWTRi5FkFuuvCWEhW5XU9uLMHNEeEI9RuiUOMdVQbO0xsKppJ1q0hz3rN4Zw7Z'
        b'JiCBPODwYfIq2QLPDbSia5XkZi6+FA+DsTWXbMNbCsiFxWR7QTZuSTYnGVRoRoa6Aa8vhfK9oHyhq4xcB6jyCpQog2xUNnDk1DN4HzyNg6dj8XpTYk6SMT/JxCFtBmnp'
        b'KYTiDeQ6PKZjT1rmkA2JWcYEsiWPdiuM3CItZCdPLpMzpnKu3WpL9aPAEYqpbfEU/V8x1RvvNXgTvIleozfJa/Ime1O8I72jKlJl/OWaQgB/ecBfjuEvz3CWW8MXB93L'
        b'+FvVHn8p8H074K9Fwt9Vz6qRFqG5f4i3ao8WKRHLtEYJFKkjb2isectXz5Uy36/VoEh4dla0aj9X5kuZLoMCwf+4gelWLZfRE51H1aGQ3XttnOKvUUg/M/TDEX/hb438'
        b'fVEEVx0CD76lPMgdWFgWgaZaR73nXJhTi1j2MffnEXsyEgfyhR9wX86N6v8p8iGPER5kpg2HhdScTPbmzoyPJ1uTswAv8PlZ8Tn5ZIfRlJ2Uk8+h2oiQZ/DuSk86ndNT'
        b'k8gNl9u5dInHRW6TK+QGuQbTepXcJNcjNNpQXUh4GN6Bm/C2USmjR40dOSYV38ZXFAnkAsIP5oeQS7Xpnhw6LvDaydy8HHN2fi7ZASt4G9kK+L8FEKQ5Od6YYDIkJeKX'
        b'8Tl8sQgquEb2k+fJXrKT7CO7yZ45CPVKScXbw6Pw82PbIBIdfjX89fKTbkbyhApBnmi+CaZztQATzbOJFtjk8muE4qB7eaI3dkaoFB0mWmF2UgxwWA+W8q4JcDf7bHau'
        b'bcFr3339ys6r+wYp33rJNve1O5FvzX/txs6T+042OjiXujycTAt594wxdmdWilAZhnK2ho/37TMo3XQNk0ZypRJmZSuMC6zhfKSYwOGrBnycPXWQO/ha7qpEE4zZFiOH'
        b'VHg7n4Qb8RV3T9r2gMXcvMSk+KwkHp4c4pNg4LxuulbJyTyyiVwbmJhEWvJGKpGqlCOXVpId7hg2q4NHk+YsfAkhfjW3qE9mHj5o4Hx8vMEgOGlPgy48XB71nFzhrFtp'
        b'r9VXSPzL5LLX26b4BI9DpM9dKjpe6aFcFOdU+V8yKHwhtbYauwt4nd2nsDkrXT61xeL01FosvjCLpbzabqv11FssBr61Obin68BJJ9WppBda33TaBqWc6EEkr+J4TsWu'
        b'/L95HmaJQ1/SFKPuZNdKfDERuswhHh8o8XDp5Dp+ObOc7wRp2LxOoUjDM7RRVCgCaCM8Mdp04G8UO0I7oE20mZFQmM2b+KYrD7pGzpOz5GWEz+Jm3Ohh07JuAD6WC884'
        b'Qx1+gIiX7Fnp6UGXrXIeuQ4kmVMqihG+ObHCQyvvNwUoazPNzsCHoxHZu2gZy7fi++4w4HtcD3yXXEf4vsXgiYJ8PU/uJtL8mepsRA4Tr5FlD6lEiSYV4ubj85mInDXg'
        b'/QwYfI4cw01k90y4XzkX30b5YQWs+kXkKDlBdsO8AEF41YiME3WGEOmV57EX35sEY43vl5NNiGzqlc0eZOPTxLsK8u34BjmNyGl8YBXjN+QKvtgX36d1vUIOkf0I8PcQ'
        b'viqNxkuVPQh9hCkZuA2tjR7A5ngsPgy88j6MM96Hb5OjiBzNJ1c8PdnUmgh9QA7jjeRVBJzwAN4uwXYMHxuO70fAs30h5AQiJ3gP6w55CaSFbeRFgG68LgyFjcIH2LCU'
        b'm8i9YtrGGXJyBBqBj6tZtnb5DLIbsAdvT0lBKWQ/XsdgWkZenQykaj99soPcNSMLeQnvZn0chV8YRq67yPWlHJqu4sk5bihuJmcYFWlDzPhgetMHLpWoAT0XuZpr4JpA'
        b'5nQqGrjn+SUKSqrYAmOX87yPN6X4uPLzXOt6ZSvHFzq52uFyl9fV1E+ZC+nPaRseSiTJg8iSXCbAyHJAFr4ygOzB14Eebykwk20GfEsYNQo35+JdAHkYuYjwK+ReGL4y'
        b'aIxDNe4lJZMudf/5+bCWkTqcEpP+1bKw0YXxQuWHiv4/+6bm8I/67zywK2Tomj+9tvO9PcOrbx3/VeXy0ZvTzikSf7yg/hs9+068/NDUNChnV8iZfxR/+72hR1/78Wdv'
        b'puy5Fv/uCrLx3e/lTt+18LI3bINK/P2PXvzu9ZKrv/xxzkemHw/svbf/P/70s/ffzv38T++Pbeq79sy2EbP/eFomovhF3IIfJJoMZCvwORW+yPcn51LX4u3s6XI12ZaY'
        b'Q45PSSJN2XlmJQrDV3lydFQxI5XAdRrJQ9JsBKEOBErVQn4GOT1kymT3IPrwIr6Fn5eY5laQ1sgWfDFHCdw0erRAdg3EL7mpLLCUnMB7Wmk4uZ7JiDhZh7d1oKgGRXsS'
        b'227ewuy15XWi3UJpLKOuejpzWQpOwWngl/9SJWjgPhTudXwkp+O0XBzn7BFEdzmXL7S2zuICxaHK7nJSkcBJSVJHWHgnxTZnVIDc0mqyA+T2blTX5HYgPI9NmxGMSCXk'
        b'WFKWAvUhuxTLgLvvfgzZZby6Ddn9n3PrEEksG2yJQqBJ6D0Ka7/whCxJ2LLMykI7Eaq6vtiasH9NJMpkuQPTeiAY8Cz3Umve0uRFUtHS0FBEqYglzlq9eRWHJF5zjNye'
        b'kpqiAIGlERBlNyrDm8hJx0evv4hc8+D5sWf+/In199aqirzNxbZ3KuL3fbzuysFr87aKRQcae0+Mi00xih+LH1uNo4RrvSfF9RoVezhNLJpbFFd6cGiacXPM7MjcI1SA'
        b'uKsS+flji0FwUKEhP+25IafOwLtp+/hwIV4vM3/cNITx/yqPewCjdumkJdGUje/iU8YEgwmEO7IF5Eq9YiFI6QbuyRCxR3mVvXyxpdxpFx3uOqdFZvY6OtylcQwddXAF'
        b'5IsJQj6h3CH61OV1nlq3c0X3uEdJtjM2gHu0lvkB3DvbDe5R3YYcIZcXAOplUU1re4EJRNgt0MtkvFVtJTtAAHgGH1aRM7q6DqpHAAuZxMgBHrZKjBzDwSdTDTqwftqL'
        b'YR1wcLCEg28nMRyMT1FbJ09JMcno1j+aodv4iQ1W43LzGjSL5e7nlFQPqH9rmtX455EWCQlnpDI1ov4vIdbqH/fVSZmOJeEIiFjWtJnWvIXKqVLmsaEx1BKQ8tt8a7/+'
        b'o8dJmWUr+6Hx0H7yAuuC3iWFUuaNhEHU7lG4yWNd0HeArK/oo4ahLMCWd6dap70zXpRLhhpQITT0Nau1zDl+mZTZZ0wSAt6yfNJc67QP+tRKmfPjVFQH0r9rtGp1S8xS'
        b'5sV5YXQF6V+PtlafLJNX4E+Nw1EetF6VYJ2WMs8kZf5neSKaBVJMTm/rtPXFeimzJjEOpQBIcyut/RoT66TMwgSmQs1dLlrzVCkxUubry3QI8Kdw0FirkXcXSJnZc/ug'
        b'0fB/TQ9rP31EupR5afVABBgQuX2SteFs6GIpc8WIIVTczPpAYR1sSHhOyvzU1QsBWxk/N9k6+Rd8kpSZNzoZLYCGhj1rHbyoaKaU+a5uDKqCOXqUYXUaJ8klfZNSAROQ'
        b'JktpLfpRmTyex0emICtQn9fXWvm7z45GhqGeSLpyDzljUlHIYoRGopH4xHQmdOCW2PhUBWhd66npZNQMfFOSafYp8YupPL6OD1B9OpWcIns8IOGgURGTU1UNgGyj0Why'
        b'fAaTIcvygSFy5P5ChMagMePJDpabii/gTanKVJjEsWgsCEhSxV7QMBpTBQ8+jtA4NA5vAqGIVlxZ80yqetpzMBRoPH5okYDbnIgf4usgdh5EaAKa0EchZZ+cVIqvK8hB'
        b'6ORENBHf7c0aBDL1wKVoIHsQmoamzSPXWG7REnzFxZMrY0CLQOkJ+FU2FuS8qdClwrdzqAYwvbgvKzoIFNZXXRw5PxKhDJQxQccAiyjt5VLOBXqSiTJTyX0GwUx8YIVL'
        b'6IuhqRloBnDjqyt1a6aNc6kX1MAEoyxzL9ZZJdmHr4Cc7CQPKevLxrfIZiYZDsAb8QFyXbEYUDQH5UCx7QyCJQ1ULOLV8A7KRblD+jDRkzTjDfgOua7Ce2CI81AeaLzb'
        b'GBwKrZ5c57LJXQTKXT7IWXelQd6MW0rJdSVeh88iZEZmfKAHq38YvjebXBdWkFsIFaCCVSuk8Wwmh+aQ6+ryTMA5VEgulUvi6yWyhxwNQ0p8FXoMfb6ml/IP98L3whQr'
        b'yAswuqiInCanWeX4Prm0NIwfD9y7GBWTbeGsNL7Qn1wKU5EXgUDMQrPwHnxRavSGGzeHceQILIkSVEJup0nFt5CNRWHKofg8qKBoNj6Pj7HK4+PxnTDh2VUIKOcc/Apu'
        b'ZnOzWPlcmJq82AArFc1dOkQarZfwrsm4GZH7GGTJeWgeiEpHJQBvzp6LmxVq8gowGVSqmywpAy+Q8/gl3Mzjk2Mpk5iPN/eq/udXX331umQxiZ+Rac17VaGQ1lZqKdA8'
        b'ICFfJFuL7g0TkaNssJd3fY/SkcPDa3ZMMgtpkdMvVMb2/Xyk6h382dXoga8dTH4tXGMc+tbCdRs3blzCH9piPDXoI6S4v+yDqUc2xL3J9XjpnEVdkny/OpH88T9l6+4X'
        b'jd241pPWUvpM/rnQxRd/dPhqWs9VXtOx/JXVV7+lu//VtSmrtD/97br0zXEzftjPNe2DPanfvvvPA0O/l/13/P1LfWecXmLff+/oL+78ateO7Wsufa3yxsU3Z7zf56PS'
        b'1GGrGnbE9lz9z/vfHFEy72qo/av4j3/ym8WXf5n6E3Ll+9dWfjl274KXfzfraxeW/UNYPHnC0c94kH+p7c2Dz/UBCdZMTW+nq4HdcyDjXuDJZXwIn2KmAvxi9mxJWJhd'
        b'JtkK4vA6t54+uQvS7x6Q40Bvzk/KoXbRKHJH6AcY58X7yC031UVAtDlB1oGIuy03G19CDSuQajzfm9wkV9wDGc6e1rrwpSxzUjw1oJIdAupBdgr4WhKoatfVBmWnooai'
        b'M7kgSADRyQKIp9xCJWImfVAzFhK1nAJEX5BA+BiO/mr/rVIpQDKIozmCDiSTSBCQtfDf2ctfp0EA2cRT3p1IwjnjAtJIL8a//dLIsW4MDyPYaia7yG4qjjw7SRZI8uFC'
        b'JWMlMpB1SrybPMT7HyOLUCMoCpJFuP9eFulcHlZLssjfsrQozv1AhQqt1ZaVSlkW+YxKuf0ylCjSavyXZQ2S1vo+cgqfBzGXibhDVpZVGB1rrRN4FzUP6je3fGItfe3K'
        b'zpO7zzeebDx/cOSmkYdPZg3eZIh7K9f2oxlmW5V9l+JqXNGBNOOSzaWbdW/2UZ2YuK/6RJ9vj0bf+Tz82LeJgXP3YnwP1Py7gKAac8CYJZI7flG1GyTpIyGJy+30lLs9'
        b'IKtanPYKuxOUKAlhtHQ01iJeA+jAhNXeQQihcEHh7jGiTwAj6IsbAhixrhuMSIbnCTGugHSabDIk5JsMSTmjHfl4S3JOfm5SDuhNoIni5/HWULL+mcGPxYy2UuqTY0Zl'
        b'e8zwN9AWM1RmRpgjyBX8Yhg1TuB7U6nif3ASvsKwY1bCaCrazH05w1p0tyoWZTryv/Y+co2DR39X/fIT6wKGBlcbl3DloR9Ne3PwXd0Z3ZsVb8acqd7nemPw6ZjfWDfr'
        b'VJHPHlifGo5028JGnJ/k12OOTiIHE5NG5AeZMbf3YmQNVPNdk0GPCdZhQnRUi9lENstz2DVmxLXTX9riRaiEFyEaLhbwwtk3GCvKH4sV/QJYQV/cQiscwLACfdENXtBN'
        b'D7JhAd7WUW/BZ52gugSjxgp8PoQ04dN422P1aKGd+fLJ9egO2MF1gR0MB85MiEAbPc+AamHVTpg2QOK2+55RoF+lQPmp1ryvpckyry5FQJppdCvSmrcjNgU5bniOK125'
        b'kF7/8/xPrJ9a3yqrqrho/9h6zhZfbhz1sXXua3d2DgLqwb1VkWPbZf3YcFzkv/+Ofs3J59TpaldoceqL49NHpA8qLGAW9JkbIrd99owfgV5ZDfLEhbx8I4+mL1bkcvha'
        b'LT7GECg8RQdskWxPVuMNBfmkxZyNLypQryLFWEQuP6keHF5rX+62iB67RbS5JeSJlJAnMhR4DzPKgCbs7B9AIYVPQYv6QqrtNhHeWvEYIwxFHefAAErRinYEodTn3ajC'
        b'Q6DE8Dx8ijTTfT68pcCQj1sKsikXJ96MYeSashSfxVfKhaA5Vgaj0DQJhRRsD07pVVWoZDQSmBVcAWgkMDRSMNQR1iiKg+67U4VVHdBIKaHRrzNHQfrckhBkjdo7XVZv'
        b'v9+T6rwpzygBjfovVIHQtnWm4CqDJ70m2vtvuxq+LkWreH9pUUraj7+hu7Gnh9I9M+d+TvktzeGymUcXrp14dlMv1dde0E9Y2f/TqtFfWMuj31rZ69cbZsTsP/fe3TnD'
        b'vtMyYu9nM/4SM3+4+qvNlV897K3MPbS0+rfqZ4p79612ghTFZKQ9U53M1KdGY/FNHr/AlRjL2I5J3RxdMhV9ApvG+MRkN6UB+CroC1dyyRbTKiO82lLAIQ3ZxoPq0GKU'
        b'rIsXNPicOw+eNSUDeVPkc6At3cTbpIc3ooC/Nufji9RunAWvcTNICz7Ynbyk6vJRe7zVVtrboW0fCW17A8ryCo6KSSAk8Tyv4aP+rVA59QEEVlIEBqylOOlTlXvcdRXB'
        b'BLHTFQOITTevnYPaIjOt9GAQMv8utmtkpu8nkpdAGi1IklD5At7vR+eB+AUFOUyOJXTNKqciWYiiO8moQvm/EKTC4a9nB0weKGHy2si30R7uxIiISGvItyKLZKtILjWq'
        b'fDdXW2+dPPnZnlJmvJUaKz5exlmteVpBVlTO9KF2xUJBGWnVblg2RcpcNz0aDUUfqARk7VcxU87ck02tN3EzdYXWyXcyq6TMqw2UJc9VcVOtRb+aNFjK3D2Oml++O4rT'
        b'W7W3EmSzRkIPar2pClNZrWVL+oZLmbWFz6IGZF0QlmItslgXSpl/mPcMWo6sOk2hNerWYNlQ81vbRORG6FlFpNX5dk+5m+dW9EYp6J/joUf9nDPkbe3nHUZQ8w5MDSu0'
        b'Dv6ucZiUmZIVifRIoxHqrdq/TxooZb7JpQE2HKjn6q3OxALZnJU0khKBD+YDEageVrlCylxUAdIq+mc+gJQ3fIhspEowUpNOXKYq0trw5pjZUuZfYseC4hc5X9Bbi1LN'
        b'xVLmrRUz0Qn0mVNXb81ZUyCX3DhSRG/B4CmmWisqJo2QMivrK9E7qFDL662ZPVbJBqVtE2OREX3XEa63Ti7MrZcyH6yMQP3QW5PUKda8/5TIPO/Pq1ahv6KUXCHSGmty'
        b'hUmZRENp3dy1Ecg6aoWlRrZcwUqZjgpHccg6zdhvHnJ8+J0TvGsE4PVnI/mS59PMJCUy4+tXf/DGltxDUbt+WB9T+73EbT/MGDb0mnXMwk2/tW/62d8031KOD/ntB/22'
        b'tfR9veLfD75655+Jfz445/o/Cxeu+LPqBx9vmqMev2FOvHH8a9phaep49VT7+sUD/rb5/JWUDdFzv/zTh5N+sfWeesTM3Z+uU0zquTgjdHHYgvyLno+Hb5n/9ufCnX5/'
        b'ygqfOuFzVV/z6TWW09vGjV790+es6X0T3jxsmrf3vZezP/rjxTN1A79/4UTmgdMXFua98vypxq3vlU3KfemVN5yxR05sfe/bR1If/euDGfe+Xnba9K3JGx9k/SeHTJz0'
        b'Ql500oDvb3zu5/2u/2r7ndwb//nc91HOp8f+ftncv+DIz3fexfj9L4zJZY8Gu97+9J2MV9YUre4pxg5aZ5ivP/Lh2imfr1D850thXaTj22ETDIKkuu6IxidJMz6Cj1Im'
        b'35bDR5NGprqSbfj6/FxjfBaIVUCdgXZvBdV4Bbk1n2keEdRykwhvJ3BI4eFw40CyRUluG8IfQ2cff+mGigdb2SmVLrPVLrZU1VU7KNVlpHq2RKonaAQg1vA3lEkakZye'
        b'bfdEMqkjitcqQoGE81yo9Cu0+y/d/VbRTwvEHjRiIPSgEQ8JkHkQdVfYbc4gyt4N4+GcQwNEnVZxOYio/zCma6KeROdgMzk8QyLqOWQbjPh25gWyg2zJy34mEV80qtAz'
        b'5KqK3MGvkO0dtBWl/N9VARc79cxDpbwYxkz3PChFvChsDCkV7ApRISo3okauVAn3KvleBfdq+V4N9xr5XmNXUF5RwYshYuhGDeSEeEG6Lg1lXj9anzpNFJ12l8tcrgqC'
        b'RSP/MXaQSfmN5LEU8GCq0MhcR9WkAa6jBq6jYlxHzTiNao26OOi+Oy+Cjuq70sxsZDBMe3FLMeUqgwehQUMWSy4pRbt28i4g02j9t37Qf+vVHjglUvFVwb6Nxd43pv8u'
        b'OiZN+e34ddPLzw5I++fWrMva88W/GLrKNel+bvSZewfc759M2PanxJkDM+6PGnCb/+WdXtVxvr9+mjdp87/fXTBn3PovGo5vwZ9l7NAOF8KPaF+ePj71xc/xr46EFxz8'
        b'x8C3Xh449r1IQyhbTVPJAX2ucejSwGqDldaXXGa7pLDybk7x75L2JQ8FydUF5KFG9q5Z06+ceIM3cVPxdnyQvUuex034Loi4aeREfLZUN7nP4y2qQsl+cIWc6lGUnGhK'
        b'kpTIU3wKOUlOsndVY3JxM95BduQm4R14hxqF1eFNsTzxCmvZ81R8R8DNBUACKsaRlkQDfkmBIkIEtwa/Ktm+GsmFbAd5yMoY8XkFUmn43vgWPsU228h5dz1uTgb5zpQt'
        b'2XuiyGmBnMUPyfrnbKwGI7lODkEZkyEnP4lDYSso1eLJ7fDJHbUBzRPTmFYaorZYau3LLBY+sCTXguQubxLHsl066pyjkn9XRsiobZLfk6iBxieUV7vYhhyowA73Cp+m'
        b'vo56EIh2n8rldtrtbp/WU9tqaelOqVE5qS+qk9rGpC0+umfnpD6qzsQAGRkOl38HkZHNfbokIx1gbiMFcvIfXRMuujwb0CLJe48zn+d8Gou8Hwn3Cpe9uqLVgUIaQM3k'
        b'altNmWibEg61OKl2tzLS357/0RM3aOB8SgsdP6cp0EqgKWcKXHT+Vp6mzhCLfza6rDfiqeqtkOpVW6S57bLWyE5rbSN4T0SSjQqI6dOL3B328ukPj9oTP8Hs2LUigXdR'
        b'M9y3D33+ifVj6ztlVRVntmsrPsgTUPRnPF7X28BJ/iAv49P4xcCCnUUuszW7SCthOt/pKgp3uILMiK2ObWvhN3ZlTz8+tCklOeEITmrxC1oOwQ2YAoNJtyCjOL9Hxzr4'
        b'/UzXNcJ33iDwAPpjCAOktlD/OovFF2qxSB7kcK+1WJZ4bNXSE7bAYBU76+rtTsBHthDZumxdjaNZ16k/ns3lKrdXV/vJQfslfZ6ioFQMirAO0c3uf9BxoptFGiWA/lVU'
        b'Dy3Hfnle8hrG94RsV172CHzEkJNkUqHQRUB58dayDjMeJv93beOCuDxXKuwR9kTsiYS/8D0RDr6Chzv5V+RbVKKRSgFB/sKRwIGpHBACHF1hV4IcoN6IgOuHtPAgCyjF'
        b'UJYOY2k1pLUsHc7SGkjrWDqCpUMgHcnSPVg6FNJRLB3N0mGQjmHpniythXQsS/di6XCALBQWRZzYe6OmVEd7IlKJo08Lx2DWgvTSV+zHpI8IeLc/fdceIQ6At4XSSNbz'
        b'CHFgCy8mydYZQdSLg1jfekD5waytIaytKEgPZelhLB0tvb1HvUdTIexRiMNbBNHE5BTpJAAdLZ03oiJEjBcNrMYYqCGB1ZDIaugpCsxEmAyyUDmjoI9GhOqDfuRc6YhC'
        b'mycGlU/hAKnWp6CY2BnimcvVQZNPl47Ov+SLKDWRhKoQOoDyxPodxHUVOpnKqJmIpQEqo2ZURsMoi3qNpjjoHqiMwKid4sMvALHbgEl/smsdboet2rGSnrGosuttcqcc'
        b'wOlsteX0kEb7VybW25y2Gj3t4ER9hgPecrJXs6elmfV1Tr1NPyrJ7amvtkMl7EFFnbNGX1fRoSL6Y5fej6cvG/XTstMNtIr4tPT0ghLzLIu5JH9aRhE8SDPnWtILpmcY'
        b'TJ1WMwuaqba53VDVMkd1tb7Mri+vq10K694u0rMjFIzyOidQlPq6WtFRW9lpLawHNo+7rsbmdpTbqqtXmPRptVK2w6VnFnWoD/qjXwpjJgKX6wiOPDx05icyuOid/ySM'
        b'f3hB26GcrKuXZYYtvS8nYIyKC5JSR44dq0/LK8xK048ytKu10z5JLenj6+rpoRpbdScD6G8UuiO3CHedQ/wk9fgZtVSXP/Xf1ycxaKk26f6/qKuDmb+jfVZr9lDrXZW9'
        b'D7VlGk3KZHpIJXcOacplR2moCQ6/UlHPjBij63c4a9F4HqVYddtmFyPPGMhMpv6v1KBZSJqomJ5MtgxfAvcFxVIdJVl0lzg/PzufQ3greSGE3OqTyqoLH6iu2sEBx9Bb'
        b'87jsGchDxcTU6ni655yYSz0v82ZmgYwuS+ikeTTZZcDnUXGamuzvT7azSj6pEIyneHboQrt3baJsKkpX5p0RItkGxZ/KAFDKkcmWVLwxuG7SlAeqKYCZbDcWZZGteSo0'
        b'g5xWkav4Hn5Vcvi7mjqK7MJbXUuo+/YOgB9fwg8cO8ftV7q+C8/fWlc8bMek2mkjIzO+/vdXdnyxUX96UKK196frxxb1SczYGa897Sjb+q+lO/9y9xsT5/b5idmVOWVZ'
        b'w+n1jd+p+Mtn+29fUOz+1o7XC5+7MqJl1cSfHGlRr8x9eUSviL8+97e02g0Dto55M/lwTd53v/sncWzGL3v+vPqLAUv/Utd89K+Tpz07/ouCyjliUa1h9MhX/31t2cVX'
        b's39p2XXo/V/9+9vfMv2z7JfCz5dZJkR8t2yRet/x8qhd43aGzXX2fmnemMt9LX3GRf5G98ruBaMvX/vGzV/frKluPPduv6+9f/y3V3Om39xiiGLq0bgcvLtPWBgMkyHf'
        b'k5RAtibzqCf2KjRz6phyYxvrlF0P8JZRQa4HeXOYawA5gu9E55py8o3ZuIXsyGMnlfrgG/jqeEXt2FhmB8/FJ/H+oHMM5EV8MYncmuumBmFy5bkqsp/sC+yZ+SvpSTYK'
        b'1KF+LNvqIa+UQlOH57fbLqSbhdufc1M5Fp9IJvtgyqGCRLKlILA5mwud2o7v4jOS48IMfFWNd/TFL0iS5O5FBslwkYebGFaEzeTJdlTBzP+R5CzZipv9ECnJIY5sLib3'
        b'8GWyU9IdH5KzDZPJHiqK0pcFcpgDpfY+bpLU2vP4ACSgAmmBKck9nuy2cdPIcWkD9OF4vEfSTQHv8bX+AeWUXItysyNeL4wkF/FB/ICqoC0GdnxNGmmpxkR8XUk2kect'
        b'DJz5+Cx+sQheoFXmcQDOcQ7vJKfIy2we8nuQw+QIuQCPTfkU2FscPpxD9rO+xuP1+DAFNZ/uhJCjBmqU11UKE/uRc6xyPT6KT8CredmGHBs+T4U9XbqQia+UM2MdeZHs'
        b'xBdoBUYYdDMoxPept7AOnxOm46P0GJmkOer+z4a39oI9SMoOYPKyfpzll+lHapgPq5bXMHuagtPxWi6Wp5Y1LSe5WFMvElW7X54K7PT33yoVaIkSATb5mzBLwnOIpBE8'
        b'Sy9TkV8Hbid6t+oLT6z0G9RSJbFta2d1JgcqZsI53dgb2Ebb+Gh419pGh448sQp5nqq7VBTqUoGcG6RUy634lepHw2YF5CbK0UDG8LO0eKfdJibV1VavMJigDUGsK38i'
        b'mColmBSWMkd5lyDN94P0aCgFAKSubtt/usFgIm9XLS8MtJzYvWj09ABsBACc1EGqy8ZtgcZNwXLV/6X9ULn9RZw89gYeFpxN0l0lZO0KGrHtUHQncz09KMxqwjsLAsuj'
        b'KygqA1AkP4m09vSQbAyCJKE7SBYFIEl6vKT3tMghmcIkKLoCoCYAQMospr5A28EGP708rfpqdk69Sxj+N7YhgUGtePRCB1E2naohLr2j3Yp12e017Jw86D5MO+nwIj07'
        b'L6tkxaACQQ8zPM46faFtRY291u3Sp0GPOkrO8dBt6Dy8uHSsaZQpxdC9bE1/lKij7X6WQTqkiDeQ++TlRDNwv8mkGSmmcvglT6qjJLeH4KIn440f9f7E+k5Zli3eHl/0'
        b'sfWtsk8hxZf9Juay+s2YMwt/o3tzuUq/Y9CB9deV6GsRIcXXGw0KJi2Mxi8sC/BXqJ1cwVcl/jqXnHfTPRt8aDC5KQtSk/G69rIUeZWclPbMrpPb+BBpZg/x5ZXy0XJ8'
        b'QOWmpp7aceW5IM6kj1chfiGXPJes786upqYGLP9hJtntai1aGsrFUquuzBDkMhL7dI5pX1urEY1ujNW3YWu7ujGita8fhIyp8NpjPKqopQF5uaf2qBLYalc88nZAkGK7'
        b'W7IueKrdDtCtZcLvccnKNAsZ4Xbaal22oNAPZSs6VETrmMjsLROt+VAGqoJ/tkq70/oYlY/+dLSqyi45P+m3HfXjUNyJnCrTggnzkGc8xZZr1DM4oM6Z8XpJo+ten7NN'
        b'dEx19hFctIb+PxjxiTUHENlY9Dvrx9ZFFZ+Kv7cqvmfY9jNjRsIwrWHoxqlLowtPNU44NnLTIOYamJgXdnBErIFnIudachM/HzWtE92jfJybGh+Lw0s6yr1CTrDk29Qg'
        b'+2Q9bh/WZXdb/LPDWHiwpxf95fyS4crefqzq8I7Z3xgTxiiqde/5xUokB5CbHtRc2Qa5m7r2/eoGjKfZHNG1fbVL5rC5LXd6UkQ2+Q96UQWjazc0OhCS2w41UQZcd57U'
        b'CU1eeR+CTtPRwhdYfHVOR6Wj1uYGOB1iV4y11r5MJvUjTSM7saN0bTwSJQsNGwK/1yk0ZNIX2Zd4HE55hES4A41ItJc53K5ODVZ06QMErroav4jmAG5rq3bVsQqkqqVB'
        b'rrA7XV2bszzlEkTp07KBjzuWeGh9INrEU56td/qhgray3TbKxR9PQTr6hmrMHhoH4ZlMc66Z7u2T5uSZ8eakmVmBI3lFpClvZpZQZMDns/ULy5zONY6FDlsImlYZURP1'
        b'rOQVewDvIYfa2Hr8r5trkosoKdoLS53s5ZaQm5o5oIqfZP7KwMH2kR3kuhbmnZxDmfPxseLJHqr64KNTyE2XzjM7i27KlpAm42zmcdCMz8/KMtJGtmVb8Z08spUDwnXK'
        b'sBzvG0rOzOIR2YtvawvJwUXsmCGfAk+DwKoP1Fg4p0dd0mw1Klyrwqe0tY79jxKUrlp4RaM5kPTOfeqvmDFzLa7jMm2Rceve7Jnxa0soHxa59euxVwyzT1w1DnwufdvS'
        b'heqNm368pvyjd9TptSs+jop8I+P6KVvY8J3Hti4+/8J8z0/ORJz93jMNs0s31R0s/usq5X8mfTV2XOHxS9+b/vMv+OeW629PvWYIkTj2xTJyE0i130sxbPjAWp4crid3'
        b'pHPMD3BjTlh/YwI95kFppZ+aDqSHtF6eNENygNy1tr9khknEGyVX7PTZzDJQpJib22p8Q1q8xRop9Fy2iO2A55LT+K6fSFdXB5FpcoRsYPvz5GFWPRUnQp1BgWr2JTMq'
        b'T85WlchWG7xtdZDhZjzZzBrvibdEM4vFcHInYLSIIueY9++CXHyX2ivwkUEBk4UiWnZjfCIHHEo9WymD/5jr4FbCH60BdV8i/lqZBUgpVTsa3KYWsx8GRt4DJLA7fiAE'
        b'FWtlCs/BZQvnB2kd+/2ia4ebbkB6GjVWYQGC1iUzOBlgBiOZ6tZK7brTV55SmTYwKDxda/GnAlBM6pTMpZekt98h6AQe6gZV47RX+FQuR2WtXfSFAIH2OJ2gEWSWK4Jg'
        b'pQZzrZ/+mSWG1RpXC3nDZC8gbYVWZl+KJiWwLyWwLwVjX0rGshRrlMVB90EbVAe7ZV9SXDFJ6GOcIFj76XqbivZN4gP+dwMnIbrecWAjIb3FXoFRpHk2qgea9Om2Wqpk'
        b'2eRnZYuAo3XKyuhmGHCX4oLxY1NGsm0wukUlUt0W9K8umw9MwER9ZrWtUr+syi5vskGHaZ9bS/g71VXztXXuTppx2qEjta6J+rT20rRV7s4T8MKOSl6omfGeWHx5Ultm'
        b'SJpkylySBVlFMnPjRkXh3Xg3uZ5LruegYeTUArxLRw65yE0P1Zrx4TXYm2tKSsgBuhtcRaDqrJyS+Bwa1UIzIc8MIjg53V9LzkVPZjJ9fSYLcJCSMsazalL/BuShZ3Xw'
        b'MXIW+GjbLRpZoE/KyS9ulef7pyDcXBwCKsA1fIMe+qBhVa4uIs2sGLOiZ1Mumgh8lSO32+zSZBlz8kzZSQkqRJoN2iX4Er7I2HwaOQmsO5jL0/7Q1uPJ9jyQ3Y2GpBwl'
        b'WknOhkypxS34PLlsECRGvz9sKWmux9ugdQEppnD4Qv8MFmDFShrtidLb+VzqKKQhB/lVhgUspBs5B5VsSiQnns3Jl8eRQ9EjBOjJTdzsGMfNV7jo4Z0dLT/o/+374SRF'
        b'qygssjRzozZ534r83fffbdk5rZbH0dMNB/oXZR3eXOT6mvDH+l2hn/3tjW09348/H7dwRuzbF146+Pths975e33DpOeW/mDDT096f33/0PHfbHyw9VdF4XVRmxLWOLbO'
        b'XBEy5v20TYr5H5+YP/APm34mPPdi7KS3dn30ndn/uZr80deE738esfdQ4vSbXwE3Z4eDD5Cr+lxmoufLpovcSLzBwzZDlpHdz4UFmDi+Jrbl42vxMSYNpK6Zw2SBxeSh'
        b'LA5QYYDsJTukUwuXgGeey83OTwDpjM/Bm5GGnq1dT06T21IAiXVWfN7P0ckDvD6Ipz87SYpbdYgcx/tzyQOyJ+hYxFZ8k7HsyKhKusdCnXFJC2lCqmp+MD6Kj7BdD/Os'
        b'YaS5odwIYpQUV8UIk5IskL0zBrPnJeUDA/sMRtzYU95nwBeIFPnGoP0fbQyEUQ4p0w/G9E2tTH+0isW30ARYfqj8p2XnfegeAP+fUOXK6GBuK9cls36VxMQp3XCK9GJv'
        b'y/9Dns6dWCHVZA9IB2KAGVbC5Ww7EeHdwV2LCJ0B/TS+aBr/S12y5rcCrHkQ5SFAYRlHCbCgYNuhQcFcmnj44zINsc6xtBJKrJzUhkC9G8W6couF7Wg4qa7Bdj58AjXw'
        b'T6XJTjZXfGq/CZoajJhi7Qtvq+hSuSpI4Kpkb/n7xSawx/9oK6orBHRSqtqbzlsD3Gh4hSKGU32loDP11YCxDMW+VAn/5X+FLlTLRYXyUswgRSgXE9u+RBSnHyjds3CS'
        b'5IAx05VnVo2RJH0Oha7kyfYMfLAD5wuV/7u+bOerJfKlClEoVTpQqUpUlKrhTyMqS0NEVWmoqC4N26Pco9kTuYerEPZEipoWXiwAmSnMG1khMC9s6oWktYeLYaKW+WTp'
        b'WvhSHaQjWDqSpSMg3YOlo1g6co/O3kMKJQSyGHUUivD2qNCI0WIM9auCGqP26KDdSLFnC/MYZ+V6VFBPrV5yiWiok/poUb/wGChDfbb6iH03akp7Amyc2E/sD/ex4gBx'
        b'4EZU2ov5YKHSOHGwOAT+95bfGCoOg1J9xOHiCMjty/yqUGk/MUFMhP/9vSqoySgmQZkBXgT3JjEZ7geKKeJIeK5neaPEVMgbJI4Wx0DeYLnmseI4yB0ijhcnQO5QOXei'
        b'OAlyh8mpyeIzkBoup6aIz0JqhJyaKqZBKp61ME1Mh3sDu58uZsB9ArvPFGfAfaI3BO6zxGy4N3o1cJ8j5sJ9klgom2YEMV80bwwpNYksFplhpk+VVsOcw15qIzLRZS89'
        b'kPzDpMC1IA3SGIKVThsVAyUZrnxFwFWpnUNQW28zJ1RQY3c7yvXUn9Em2UnLJVEUMqh0CXVK9pXqFfq6Wkle7EyeM/A+lWWprdpj94VY/FD4hIySIvOjyVVud/3E5ORl'
        b'y5aZ7OVlJrvHWVdvg3/JLrfN7Uqm6YrlIEO33iWJNkf1CtPymmqDyiek5xX6hKySTJ+QPb3IJ+QUzvMJuUVzfELJjLmZ53mfUmpY42+3jVWszd4JJQsNvCuUUt/VfBPX'
        b'wDdyIrdYcA1o4E9wJ5Erwc2LfAMfi2go4ia+AZB5NScKDdxS5Cxt4KgjJLzFnRBoAGNR1RvKxaEYNA6t5mo18FxN75oQfa8BWRRQq/Ik0HqLStQwlSTkQ0tnKkl7nzl5'
        b'nltd5tq/0JWgz0ZCUjNsUh0spxuTljRkE5lXWnFB0uhRI8cFo5EI2kl2BZX69a56e7mjwmEXjZ3qBg431SSAAfq941jLfnVRQllQVpyOMk8X2sVE+niiVbRX2ICzBNDI'
        b'CuqKo7yK1u6QxgmQUW4HEKxj335H5/xRT0ct27Rq7c2IYa4RPs7k41J+R1nG776Cn0eCKSXFbFD7Its3S/dZbNX1VTZf6Gzakwyns87pU7rqqx1u5xLK3JSeelgmTidi'
        b'pgYmQlAEc65G3R6kZ3z3F5RLxTDarwCOESNbQfQ8FYpWRkgI8PTOAwaOgdalGPG3gOuAv4mA50BSe6RhU7ei3q63wpSUA6OvNk2X/lutJic9q/MU/gNslLoE658B6aYv'
        b'81/oHBE7NMf7m4uUm6NreBEfFhgNgU2IT2NzWZj/qE9jX15fVwtqbpeg/CsASjnzJ/DUlIGiDEMhj4G+vtpWTjdrbW59td3mcutHGUz6EpedoXmZx1HtTnLUwpg5YSRF'
        b'q5ViqU1c5IGCtEDbWjpu87Y9C8WxQBWBeOOBs1AcM+M/2ZZvpUHx4R87Izol9VQykwiOfXl5la220q53sqwyG91/qJN2dqGUTV/vrFvqoLu2ZStoZofK6L5vvR14Rzod'
        b'XOjgNFvtYmZ5d7nrQG5k5KH2iUiBTAb8IFkYSFY6xh629CVCQylSwOIOY0ydazvZ3aPR4O3uqrpWPmbUuxxAU+Vq6Gt0Iz7YRberPsoVTaTx5CdaZRbbyTZht+aRsro6'
        b'GqlXXxFsh/GwqRDbTUOnRHKZ3QnLdCnwR1sZ9SjowiLTRsSkSKVA7Y0rOjMLYl02gtxKTMrKNlIVOHcOvqOkNguyPQtSBSXxOcbsJBWqidKQh7Z5UhT0s8tWgz55hdyc'
        b'GZ+TRCMp70g045vkhaIkcoZHo2conyWnK/GRaCYEryW7Glym/Byyd5kqZ3YUisD7BRO5QNYxt1HPUurf2mq/iDcnJeQmFcXjV6LkqnOVIKhq8H18i+z3MBfAS+QaedkV'
        b'L2nsJ2uVSIl3cOTKmkzmbEv24Ffw0WLcgq9DlXtKQF3eW5LPIU0BR26ARv0wk1k5psPDlyhcvfBBJRLwAQ6vI80xLAxnBj4+0JUl2Tdy8WVyg5xToB4AN76I95DDkmzf'
        b'hG/hhy46PP1pDcrVHLlEbuN1sxyvLd6mdL0FZWp7be7ZMql22kzt9D/869dpUed2/mJh1td1RUP65E7PVm6J3/nzjW++feW0cUSYdcKf/5B5LPXrpeGa/j1u9F70KGv7'
        b'vv6KG6Un3/jAMFG88yJqLPnm9g3bLP/6U+avtz977mcTh/yo97kV1zIu7l56uN/o/vs/XJB9xvRrRVHvP2yJ3b5q/KebN53pfcowvfTbH834bfV33ut3d+1v3k6+dKr+'
        b'vTt/WHfh1W2qDxs+ivmFJ3LtkP4/afxB1Lst3mGfznf8lbx3Z+Gf/xL3yZy4N754/dfhZ/6xdtRLz278VT9DD+m84SX8AO9lMatIM76Rp0aKJA4yb5PDknPlodnklcQk'
        b'spVsSc4iLXgTOS8gbaagwgfwFbZrsYI09sPNyVBEhY9zSJHM4et49yg3xcv5NabEnPw8tBbyB3H4KG50sf0IA0zgBmpaySe7tGqkUvCaBWS9ZDI5QW57chlAQ/A+eK8X'
        b'h1/Az5MzbIsmPb0mrN32DDmED/lNO5l5rFMjFbpEE97c25AQL3/fIIJcE1bgC+QiA2sEvqmhJp+BNtkkk9tH8jS9gc+QvVLl5Cy5AU/NHL5CdpFmaYPIO4dsplaXbKMJ'
        b'b0mm6yt7FNmkRHq9gtwaQB66h9JSV814fS5bbj3JVrbicEuytOQSyCtKsoHPkMb+yNS1Uk+pjXDL/JUcChN5crgYH5ZCkF8gGwblFiQ9S17kEL+USxtHWiQ4T+Dt+LKI'
        b'bwed2KantY/gXW56mgkfI9fx9tz83Fw6ufkmssWY648QkYC3K/HLgOfr2EwM7U0OkGYzvmSsJQdVSDGdw6/OLH0KX8v/5ihmT4k0WtpyA2Zcoq4lsnFpLdJR51LJrESd'
        b'UGOYoyk9simZnHSSa6qcS91T2cHNfrIQ1GkjZv+5LXbo8r9xLuWkV5lssQsuX7UzKTV2cz6zW9CgZipkdu12w6LQsPBnIDtwQVFoePatkSd2vfnwx51JDukS65PP90gi'
        b'IxVzgBNRbhaQ2mQBgkoTLlkR6Mio5G2HdhJIO3mjc/miI9ub1VGWsVF+2Ya9+7ltHRUD6J7LCiqodITMVl4l7ebX2GvqnCvYFlGFxylxbBf73szjWX97PautfBvkGOm2'
        b'OStBqfGX7HaTpTawyyJhiX+TxS9iUcHI7gq2CDxGQuj8fLxGcmY6OliL4hQRHA1v91XpHOkUSGb/fmj8+GlKyGz4V7Qcw8TJ30bLAWNOLF9vjRuxWCUF6d8KJOS2qx7v'
        b'Cw8HDCfbEbmEN5CdHuo5HoYPjM9tJ2/IezrkEhfgwbMK5yTNngPyAN2kkb0N8shWIFIrB0ROJI1GRxr/pcJ1jsrt38rLb5mku1KPUyKnV/5EFzml/9am8bNXJiRmvDev'
        b'6ZuOrOujj6zDq8J0r71+JT/9HxV/zRxy5MTyK1d+umWy1/zpuncmp+eN2npwMB42bmzRopgBtnduFI1/9OcbSz+tiTud3Tfp3b8rKheV/2B22ul3v/W31+fV4QuFb7Tg'
        b'z+8ty8/uH3uv+FdzF/x+Sebf7/oGfvj7BxfeXjv8H+Mrkp0T96gH/fqVae+8vUl946Neq5rGf+2rzww6KWZRC95OXkwcjS8GfXcCHyqQtvKb5wDHCYyCAqSnV/GW2UL1'
        b'GPw8I99kB35piDx+wH3Od8JByLHhjPlWk7sFpJnGmKQBmVg0JvIi3sS2QWbgfXgjZQL5c8ndTniAbqbkdXAbH6tmGyDAH5skfjiIHJW4/6U6vC2RhgzBN8huKWxIGL7G'
        b'A2dqLmD8I21wqBy2aWSYFLiJ7MabWcVFlfihxEuVc/FRiZXiff0lH8sD+MUi3IzPQr3B3FRmpfga2e2mZ5vItmeWMjk2G2CHEQER4nkZq2BEeHINb+UsyRp8ylTDBt6E'
        b'T4DciZ9fwrZllEi1iB9ATuHjUhCCpjmKMLKhuKOnHDmLD7AOJ+MDSxON+VCHHMQ+Yj4+g3cLThjVjZ0d4H9SlqeWNQvG5CYHM7mxEntTsdMU2q94PvRLntd8yQuR/+EV'
        b'lKXRGCU6xvIk5wodt1In8xG50rYOdavbcrZuopXwUtlWL4o9cImHulxDW/nZOuTrOhpVe0g6aPOUBjFtnioGVJuHP2p36yNybh7uhUYuFgqIfJuUP+reI36Y45FimGlU'
        b'BXSOwurTWmrrLLK+7fIJtjKXZJ7pRPP3RVoCe+mSGTOH9x9X52EY+ZW9/BaZduU62BoDm9h5cGliH5to5J2ZDRzrD1osOKfSfjkTGrgTtB/oJLeaq411CyLXwNK0ZIUg'
        b'WSDhXkE/WMF2injzoxEB1lrjcAEY5VWMKQ0DnkCNW0zfpjcwk2wIoh019dWOcofbIg26y1FXy2bOFzJrRb1k0mKDItuvfErGwX0aySBc5+zCBVlnqXfagbPZLaz8TF4+'
        b's45YlFgVDBjFT4oFK3v6B67NG51OPhs2SilEakKFoaBG1EVcBR+L/AMQJdUWTztplLrqXBWYVF1bKDUWC7TptFgWUPiYrBRsWpOedY2GUQwSPyLKUFRQKNQUzWDUg5pu'
        b'h09qC40xYGFHpPwt6wIts0dthDd6r/A3HMfw/wRggsid5FezQWjgFgcGgZt8nnceR7K5Ee7ZqjzaCRgqi6XabbGU8TJXRzA7K8MDcNBnTw0G5x8FfvIzztO0qTNdtGy3'
        b'WCq6atneScsBHDAFL53B/kWxmK/TSzAs4hZTSxfLp3fSSZ1Vfli6QFoAyb7EYlnE+93mGbKGAhkNAoyW6ABYwM6oZUNCG9X6bYxSA10MQS10sz4IBVrbqe1sAB439Ar/'
        b'0HNTuh35SphXVxcjX/nfzLmSjTGd8yndzzkoKJZlXbVs72S1BTzo6dD6V32r1biVYHdc29SSZrGs6nRtS8/a9LONiDu00372optCiJFhvpH395lLPC+0LjdGWP0RSo4G'
        b'ctuBB+vfJooWy5oAG2HKZxANYI87XQJBmEYBPOk/8wTDcbOroaekjtXY2Dmp69jaEwxHXPvhkKhPkvM6bfdG5912ecosls1ddps97rrbOgZIWNuOO291121WY3Pn3e7Y'
        b'moCC6AyVoAN0RudGjKZAOqZ9x9k5PMGnM9e5s4Gj2unpJrvYig9sMLo6rmOx1HgAGbfz8r4IYkJcm1FhBZ4YGeSNnle6GxVW457OR6Vja22QYXLwqOg7okXfwDj1bTdO'
        b'sjBGkSS5FUm6GJcwi8Xt9NhFx1KLZX87mszD6EQFAA4U++9h7hOAuU+XMPPJjwdaCyytuq7OycA53gnU0QGoW8v992DHBsCO7QxsiTwNeyzUahbQyGI52wnAQUhY155G'
        b'KIJhLURtmXIrrG4KLd0rB7ha7xfwq/nVggyz0EihF6S7Cj/8lJ74VDBG0DRI7YzGvoGCCa1fUaGE1qdcVlVXbafuxDU2R61o70o6DbVYpDotlpd5mahIPdby9AR66Fcr'
        b'ewR67S/ZtURK5UCJM4WxyWAUoSIgcXTGnVgAuUqL5U6n4h979CTthba2t/Fx7dXXuSyW+522xx513V4Ma88ttcUF8T62gXqgzXx01TooVxbLg05bZ4+emO+zfl7ppiVH'
        b'LQgwr3faEnv0P2ophC1gG1T4RlBbkcGrmz50NqJOzLBt1jddJYuRM9INmivzKuFEQVRQJtMLAFlNVwfVBPkm/qS0XuRVwpBMaf4drfTRYLab7Kit1NfXLZP2o0emSF4Z'
        b'nvr6OhqU6BGfYvJxI2HFNPmnzKdZ4rHVuh0r7cGLyaeGmiodbtCJ7cvr/epfl+YIGAnWuMXy9VbyoWHBU3XBIyIXkngTHRZDcjvPQ+ciuT5XdZ2bBj2j3z306dqatiFd'
        b'UWEvdzuWSoG2geRW21xui2S09SksHme1cz+t7TC9UEO35MMYwFGfJqD0hzErqbRvyyzwTPl10vjZErU5SS8v0stZejlPLy/RywV6uUQvL9PLVXph0tdterlLL/fohTHh'
        b'V+nlIb28Ti+EXr5OL3QX0PkNevkmvbxNL+/Qyw/9Y2yI+v/jE9nO5aQOLu/Q3QfqhqERFEoFr+CCfoEuxvTswvFRSb1zB4ygjo9xep4LVenCtIJG0Cg0Cp1K+q8VtEoN'
        b'+6M5Og37DYFc+VfauD2GD5FbLrKNtDB3yOxeSBPHe9LIvQ7+kAr5v+un7fwh/XFhKxQsSq2GRaRjUWppXDo5Ih2LSCuGsLSaRahTsgh1ajkinZalw1k6hEWoU7IIdWo5'
        b'Il0kS/dg6TAWoU7JItSp5Yh0MSzdk6XDWYQ6JYtQp2belUoxjqV7szSNQteHpfuydCSk+7F0f5amUecGsPRAlqZR5/QsPYilo1lUOiWLSkfTMSwqnZJFpaPpnpAeztIj'
        b'WDoW0vEsbWDpXiwGnZLFoKPpOEgbWTqJpXtD2sTSySzdB9IpLD2SpftCehRLp7J0P0iPZukxLN0f0mNZehxLS56Y1K+SemJSj0pUqme+lKh0EPOiRKWDxamM+af5IugR'
        b'nFmtp1s/vNJ+u8l/ADSokBwer10x6svBHEvKbbWULpbZZfc5t4Nt9vjdP1j8Nb9jHfUAkXZV7G33f+Rdp7YeH1SJCjqKa6VU2CadIhLryj1UKQjU3Ka2Oqe/QodbsqtJ'
        b'r/o3cdLT8mdNl2uwduH11yaRXSG7r9j0ZcwKCNVJe2/BR4WNUpP+vsqenW6nnQ5Im/psLuZISoFjTiVLoSZbdbXeQ6Ws6hWU77Q5g9zm5TYclyp9lOJQPwpXGUfZnzOS'
        b'ssDeqIn3cM44Pxt0M/PnSW61IALLs0hXBbsq2VXFrmp21bBrCLuGggBK/4exlJZdw9lVJwpwjWD3kezag12j2DWaXWPYtSe7xrJrL3aNY9fe7NqHXfuyaz927c+uA9h1'
        b'IDBvwaIXObgOYjmDG/gTQ06i6ei5BSD0KlYrGxQnYI2e5HZyLqA9DYpeaLWitg/LVdFc51BRDUx+WIOCWhVXK9zDgekrGnkoP9k9QtQ0KCTzrzue5jcoGwUOLfm0CXq3'
        b'SNfEsXILctAGgICtoxCz81tUSBgjLYAOy6X7BcG4RKaPs/h4i+WR0jLMNcz1aFj7Sqps1OWq1WtLsr0afNoi4P6OGtk7UiVtQ0pxUgWLQ/QpLR6720kj2EgnJHwRUnD2'
        b'wJE553TKn+g3cp3UYu6k4c2lqCqlTDpoe+ISJEBpvxlqrPc4QbK1QxNMMlAzg7zb5lNZalyVrOnF9BSi0mKX/rEzieH+19gn0OCl8iq6V8qi9trcHheIJ047tZTbqmkY'
        b'ptqKOoCYjaujwlHOfKRBIpFoRuCxrcbd2iFfjKW6rtxW3TYMAI2ZXEV3eF0AH1uzUA37L8VS9vWztBtykGdhPcpllXBf4/KFApBOt4t6fjPZyqeGeaFz4tOl+WdGmgm1'
        b'y+6mDwwqyQeBfThTtXgZ/W58UDCFBvT4UA5sNt+nsl8pk/0imZdF+zBemg45Xfzy0v9IZhnSsu8t02sUt7JXuxF4qtDUslHkY4S6djONAp1H8n6Na99UwA128izmsVC7'
        b'uPVUp1EKx+Cuk0/DUh9EEUi1o2IFEOAgwvgUXrFM+0jvDtiefmAfDW8b04tu79fUuVuP4LJQp08T0yqru3bjAu22DeXVsVkaW/XJgyU5c7trtW/b3gaH8WrXrBzo9H8U'
        b'wWtAoF1DJxG8/g9NU5Ohs7i7pgcFmn43TS+Ft3V5yuSzHczjnbYnO9nIgaK6hYsJS1JFbG+Syjb18BqVS1isnE5CT5n0xa15FQ47bVAWFKB2KNDqghOg/S59gjxOCUa4'
        b'dbjZf3+grwS2C5kgRdtKeIrBmtfdYMUHBmt0x2gpXeBn2rQ5aclwyXhCLK2USMjvuoMjMQDH5DYH9WkgEntZ2yP77eFJL8qYnjw9Y9qsp1irAM/vu4PHFICniM1+EMuW'
        b'HbP8XvztPIZM+uksYorkH1W9zLbCJZ9S19faK21U/34qKD/pDspRASgT/Kju93oKAljmzPr44tlzSp9ujD7trvUxgdZHMOJeV7eYSrTSWXsQdOvr6+gZKhCJPNLp/Kdq'
        b'+g/dNT0+0HTErMCRmCdvQmZqf+yuiUltKVgNrFlbpT0IDeurVrio55u+MC3bDGu8+gkbl7fg/tRd41PaDm1ro9V1lW3b1MfnFmVkPt2sftZd02mBpiWvv1oxyV2XBP9a'
        b'Gbc+PuPp2oTu/rm7NqcH2uzfafwHfXz+U3fyL901OCPQ4CDJtRFEwlp6fEReKlJcjsKSosKna/Tz7hrNCTQaxWgck5DlkzBPFRzx7921kt9KE9pTLipXUy8beh8/raAg'
        b'N9s8Y1bG3Kekm//orvXCQOt/at96W2nfpM8EGjHDDvDUMrnQFVC9OwtJD8RrTnbmLBpY3qifMTvdqC8sys5PMxfMSjPqaR9yM+YZjMxrJ5OiTJVcZ1e1TS/IhxUkVZeZ'
        b'lp+dN0+6Ly6ZFpycVZRmLk5Ln5VdwMpCC8wcsMzhoh6u9dU2Gv9KihHyNKzwn90N4ezAEA4OIuqSaiQhpo0tRpsLRvFpyN1fu2t1XqDVse0nTtLgTPq01vNr2ebMApiC'
        b'6eYZlNJTVHqq/v+tO0gWBCDpNYtxe0lthCkUKe7UPYWMCmvl3901ZWml8XL8FnYgUmrI3moGCtZFnqafX3TXeFlbotdK7KjLt57arjphKn6vErYNMltu0GVmrm9xbIuQ'
        b'+VTV96P30pFZuu0Bf4pGuFpoeSVzlVPSNy3sekIFV/VJjguiM48mFUlu0dSCFZBxJJGr1ZbWuUhmMmicv6XdXEwv7YJLMxsEjXPgrEFsZ7U1AnW7vaIw+sk5uUq74N9w'
        b'BD03jn0kirpkruzbXuEMeqfrmaLWNJGTN6hnSU12Nk10e6JOaN2n6qDeBjxiujxCGSfPkVNHt3ZPIrqVWyntlFVIAXe/pH1VUKNEpy5vGtlgYaFfT5OdP6hZoDNgpIJd'
        b'9zsmCBgp6q/odztjpi4/NEpJD+nCA6/aXmuxLGsHTSdGBlbObBjS2XYVM36wDSafrp3h6tkA5rQiTbUfX3zhbe1WKtlspZY5N/tGsU8lm6yUksVKwQxWCmqvYrFJfNo2'
        b'xiqVbKtSMLuTrp1VKizYKKWSrVmaVmOWZEjStTVWOYdwMvo4h9E7+s1Mf5y1J9hWeg8u36OWIbqfpREUYVGjnjKqhrqraBv/x2gdXf1XPWm0D22oRtAoPdR4Rq7PIifD'
        b'lobXaw05ZFuiOc9EXdXJDoHcIHdQQpUSX6GxWjuN7Uh/XMtR8C6WyG9E7OuKgqgIfF1RKd+r2JcWpXu1qBY1UFbj5Ss46auKpSFSLI/SUBZQl6cxPSA3jJWIECPhXiv2'
        b'EKOgRLgYzShkjC+6HcrnOUBTVwQBqggmBBQxKTG2MM8NC0f3oy18JY1iIIgBLq1geoEvJPBBZLitqRNt1fQ7d4Pb2zJpi5bgvROX37HDxLENW38lGn8d7Skc3eddJwQ8'
        b'qOQP7/XrpJ2nPzTvpB8R6zpOa8Bo2GlrT/U5O1kyndhde15/e08jMk3qrsamLmsMTDr1jfB7gLSGWB9Ka53cVdWUYGwNYjpdTUbntL4rtwy5Q62ttmW2jEK1BLXanrHK'
        b'rTKa/r9hrDsf30eZubY/CxBwsaHBDf2+U64oNzQte/czP6/Fgms03DM/KXZP7xSLBedkt1LaLIO06oSauv9xrR84fZQULPzW0AgDZa1BG0a0g3RE2+JinV06Qy+dImCx'
        b'ZPxH8RinANHoCJIXKGNWzmfo3RR6YQ4mdIaArdXXg8rtPz4QFtQEK9qFh5ZgE8XdQtChAY3siU0Ps3TCpNkwwztdY1GojEWN/m8VBM1pOwwaDi8eCZrT3p011rlgFvDI'
        b'jGHrRaLlDWg6auRkr2XB3EEMDrxEJQRKR5/T0jMdVK55nl/CfLollss7E+joNkj3dF34OHd7jIyAy4kASUrqDHZ3ndtWDYSJ7kK5psANpfd1NfVTDJxPcHlqOpWXlOyt'
        b'448bF1bKbNC1l5Va/XAYwrTiSqtYwaSMdE6eAWdmQNToJlTKBCi0WpAHHBiySvoWokagHijUw4RFJJhGjq8M8Ofc1a0cmlwnW4wA0HRySZ2nwR1ZdKz837WLa8OiYWLZ'
        b'r3BEWSpQBxPqXkI/eiiGUgZMP28o6ijDFXsc0ZXSDx8rgRlHidHAgJXs0K2Ghs3yRnl7V6jFGLEn5KvsahYiS/pYslqMo/dib7EPc0NRi31Zuh9Lh0K6P0sPYOkwSA9k'
        b'aT1LayE9iKUHs3Q4pIew9FCW1kF6GEsPZ+kICaIKQRwhxgMskXZ1BXIge2QjOsVt50oj4XkU9MAgJsDTHtAbTkwUjXAfxe6TRBPcR4sT5MBgNCBJ6yciddDXSNbbaG+M'
        b't6c31tvLG1fRkwXiCimN2aPeEyuOauHEibQVGBGBheOiwcl60s8pimPh2STWzjhxPMuPFVMZG5rs01Is9DtH+LhCH1dgUPr4GdN8fHaGj88ohv+zfHx6lk+YNsPsE6bn'
        b'5vqEGdMKfUJ2MdxlFcElPSvTJ5gL4K4wD4oUFcClOIM+KM11LmUEaUZ2oUHn46fN8PHTc505lLbx2VB3VpGPz8v28eYCH1+Y5+OL4H9xhtPMCqSXQoESACa7zaL3B2Jn'
        b'PhDyBxCkWF+KQBh2xROFYfeT+icIG64we+gmOo2OsYSuBTfZUmAiLfk01GlrgFPSBAKsKZsdWswjF8k5Y3b+zCxYJDn06D/9FvMUsiEC3xhc5HhbGMi76Oq6+/a8T15+'
        b'yfp7a7w9PirelmWrrqguM9oWvPbD12/sHHlgfaqAqopVf46eYxCkYJdXC/D5MHzemOU/ONmD3BPITrINX1oaJ4UzOEpuRRP6DS9ol4YkOMyTB/XL8Um8lVWhwevIoWWT'
        b'2n1mmn5jmrxENvmPMD5+15r30+rAEUrpdzz1X1wZE4xabb/drGzdNXcqKKHq9Fu0QLlYiRGBYoGWr1GiRQMnBo5GSr/f7eb7A53CU64JmnYKQNvPemoYZoXKX0uXlqMU'
        b'Laj1s56aphDAthDANg3DthCGYZo1IcVB911hG+1nxy8b9jOzzxOuJof75OaZpfiGgFxJSaaZWTmFZikELUWBksJleGMWPicgsr0+jOzshc95qFds/0R8pvVNwMCCpNny'
        b'8e4c0gLUe0funHiyZY4GUFkBD3YifBe/HBZOrpCj7Kj58Ao1DR4dqS8pz/tO/mzkYWEwLuETrglVrtaD5upIVnqSWYOAYaZ8pl+r/WBxKGKRb3ATVNzYJnzuAry97Zlz'
        b'NZpXrF4hSN/ezcYnBuZm5+caSYuBQ2GOJDNPzqSTXR49rW1vGr6TmEWPppPdqSkpeKM1d0AdGoxvCviBhzz0MM8Wcigy0UyPJbfkl7Az7UtMUrfjTUnxpCk5gX75o86g'
        b'IdezS6TT87thmT6fS5qz85JVCO6vqHrxOms4w1MWigYG5nJGIh3sJCjQMlyF7/FjyQnywDOVPr1DTkxJlKai9Qx9PL6B9wVanBnPosQXxkuQ4U1ZAhqAN4Xj27FyEw/w'
        b'VryrlhxxLSXXFIjDB+nJ80a8lzUxfxo5In3gMhHfk75wWQ/lZsXDRDYbjfklUoB/6VS/f845RE4JWrJjILnhoSThmQnGkqH+mPhkax70JXqGQI7iA1PZ9xD0WeRk68gl'
        b'tX58oHXgAI2ayX58PpnHW3mEb+KHYWNG9/JEM4KTiJ8nu2eiFYANK1E+2WhkoX7mp+AXqueCmHB12VJyA29ZRq65VSi8L48PYi++56Ffc27Al6a4IH82/eZBfE4SzD6Q'
        b'yx4LZ7IOxbfCpEJ4N7kTilTkEHsxjhwcnEjHAMakOZnsKI6PT0rALwN+NCWbS/xfPaA4htfh8yEICOTzHnrknezEh/qGkVvkhovcXoJbljkHJ2qXkFsI9UoV8Ea8CV/1'
        b'0CPog/ChUHxyHmmmn45JMsHYKlEU3ivgywK+xvD+V/OVNPqTXp9Vq7X1SUcs9hG5vgqvcy1R4hfINfnLm+Qq2eH4l2Ov0rUYyNhE362SomwzmRp5ZEDylq/rftbr+m71'
        b'Z4qFO6Pf+8Zp5evPoxXG40fCuPOuz6MnLzv2Rupf0MojGd88/emx0ntnaxZF7Zyb+/O3FbjPg3Un+CF/Hb07/hPfDyL+H3vfARbVlYZ978wwDAxNROyK2Bg69t4QpSPF'
        b'HhWkCIq0oVgRUaRXsaBYsYAUUQRUVOL3JZueTTG7iSlrsonJGtPrpvmfMjPUUZMt///8z4YIA/fec8499avvazXG/yPLUcOMk9MjHF+ZmPT3wDnvDXpl5bSfSq89v+5v'
        b'43/e9vWCk9/bryrL/jzozMB1Exr75P95yGGHsNrXn5qXcPL2MQepg92cB0kr5qw/sGTORyfhlWf3napeP+hCrp29ULXsw5LfLrR49Knpv/mT1QabomzeTRp+uvXF1uKp'
        b'Qz+/Y+Vv9I9fn7PyN/u+oHlV0Ju1AG4Jnk+lj1Df/KVgZqDRlj9d3Xr/ZtispIrlJYeb7xUYqN2Tfnj51ff+6Vd/78WcUxs/Ppvw3uYfLqRbP/nmR28XhK/84ccx718L'
        b'uFb6z+NLTDYM+eyXXybdXVVYPLXvxd8ObvuTuqyg/5Swa6MOfJXX/rJ/2q9RX9194wOnqbc8P/f+56tN0+9sfHrPAzHqjN3R+Y0/Gs6tKgpx9lKNZAeeK+Z6kjEo6HFs'
        b'Qv06vMFBpndF4VGynjRkVIIyEuvgvARPw/5ljBk0Bs/juS7cPmQz0oAW7IdSDkvUaE+m4z44CflpZqbGSdisxpZkU7lglSgNhjKsYEgNcBzqyOZ4GYp9Apw4ntAmcjIz'
        b'zKUMOBGlJbKqgyoN90TgeM25Lvdn5KUFKsyhbYzfAQ2UfrR5IMPRNoLDmAP564LMU7ElAZtTSM3K/pLoSWEcX6IODqRpeEsDoYBDYWT7cT5SIp0EdyEjTSEzl9JahGEe'
        b'Y9Ga778jGg77UKZNyWZxRgjUMJwHg2Uh5JXzyG5RICU/9gqyqSJcGGTHGDooB9MuaJ/hw9hEKfnWVPIY3amd3aBNnWqSmIKt5mTzKzBXmBpjozkeTEglCxJb0hJJ2/1k'
        b'crgihUzeNXnQvtrBCQt93URS8BH5cpG80A04x2paOgTPmDljvifUE7lku7gAb2ADJ2RtXwZnbaGMUnLkQ52nH5DTz5nCsg+CZlkanjNifesIBUaMtYNSkeb7Enlok3yO'
        b'BPfL4AQbftgTSnYwDfUp3wxSoFGw9pWZ4l7I4E1swGIDyHehs8xAcIJGeajEFq9AMx+9PKyNIVc1O5qBoDSA0gAJ7ptgw9ih4IzbFA0fWgA9of2c4CrsJHIj6brheFqG'
        b'TWuxhpUUti4A8tOxooM7jfOmWWMpm2CxI1YzHLBCX3IMnFXIvST9oUrFZug6UsMBPEVGhUKWOzn7+wYwnltRGISVskTfLWy9eEMT7iR33MCygI4TxSxY6kfepoKtFyc8'
        b'sZYSmTgR2cJHKhDZA86ScwHP4o1+bLZtgBpbcoM31Ng5ehFhQVBMkaxdG8lf9QRenEEv0iuQoyGM9XKSwKEJgr2dAe40h2Os222gzpvc6O8IuS5kex9LDl6yuxuQDmk1'
        b'MFDMZvf4kXE9MBdKWXN0WC6WZJvGfBPMT6ailLuwDPLNuwrukAvFLipv9/6drc4O5JgpHGkMxzZiNuPhxQo4NrH3Z6EGc3xVcsEXz5Ij2xAuktPnWrIb2ywK8DAn7yVd'
        b'eb0ngW9n8l5yGBYwzlk7zIZTfIaA9gG57wyiRkuxHUv9exfK//0UtMzcwIT7hJ7C/UxjUUFZZyUycQAFViU/rcUBEhOKmcLYaU1EC4kFuW4sDqKJuA8UUkuWGWgiMZYS'
        b'8Vwi7xTeSp138k6/MbNzv26COrc3s+bVGGtyrLTxzjJqjUui6zxpMlUaleFhybrQZbk6PDpyY2R3HBbDx+iMGkVStKgpNIkxXbJCWEX0DOfm9Rixc4+16lFKXngIkW3v'
        b'7/p7mGMN12jeUi/6q86c1bWy32VaZ4b8jQ8zg/+k82PbMRoWbcoGb52NBh6lC5L+48fzalh+lGs08VdrHkL286uuIY69RWzFqDva9rtpSTVBW8yrra9+qtPx+oeFsFAt'
        b'Gqj1h2l6NRQGhmvCU5Ljo6L01irV1cp4YcndTuR2G5o80BE0RlvCgq//GFnv8IeNv1zXAHsWRBETpYma2EhjVUivR8bR7JeIP8ZUTLrAZE2nta23GUa6ZrCQLhrAsY6i'
        b'y+miH//IACQVPGzATXRVjtUPr9y14k71so1WhyxIlXcdcj23Lwg0I2e7uMVym8DsCyKzKQjpYnCnz67alO9u9gWthbw78px+AtwprAVR4h+jv30/RewF0ZD+14UZqWug'
        b'iNpGHR2fEhvBmHAjkxgKuk3YujAaXtJrWTp6KffYyDAadmUzn6Xb0IHWQPayqEUNoLkmYCmmd8hfDdZ5aGhIUkpkaCjn6Y20sd8QH5ccH065e+1tYmPWJoWRwmlgmhYc'
        b'WC8ZYnKPVU9h/TXxChzykAe8be4UR/Zo0PfQ0AVhsWrSwp5ggyxPTOj2n9hj2KX+MQNKW0U1FZhff3D909Bn1yqi7sSKguLM2TfF1y2OqUQmMsMlyCDqSSdBBE4tobII'
        b'l0Tgkhs344ndHU+yqHWRDFjtG+Z52tHta9iWUV1OIHV47BrWwR3eFFpAJ1Zd7lzqoNPdRl7KglSqpgambsdshvC1id6DNsWD3G8VBsWdjLfL8QYV5bDUobPARZS5JiIK'
        b'5gZQNQtacK8P09KwEVtNXYdA7X+IjFevLVrng+tsi6ZMLHBoCO7nMmaHfEkNN7m+9t6OcC6E26Lg2Cj6twBfRnpbC7nKqduwPcYhc4aBmgoxOVutPw11nhhkeS/0xbV2'
        b'1vZhvswCfT/0k9C4qPuheeu8w8gkeVEQ9pso+v7VVCVNpsMBuYu3da+7i2wL16BOI98Gp3Hl+EC4cycyqKz5XcmgrFI1MvAlaOkuAyfM1My81kmPZZ0mE1GtmYjWvU3E'
        b'EdQl+hiTkRTCxU5ZJ/4B/YyIWqywbbr5mk7m6yC98/UT/dZqNl9XQfWsTvM1Ha881nx18Kfz9cJg0xnQijtVEs5IdhFb4SSby4pBgsxchLNrrdkVLzKO/CEHPCrIxovQ'
        b'NHdqzJFKewM1NbNNG+F7S7ZhnWe4L5kZ69+vjoxeF70udp13uH+Yf5j49cANA9YPCF72savB+IQzUuFpB6PQH1Rah2tnU75+BARdzzOVo9cBszYxtpBtse59wPgQSR4y'
        b'MJ0O7EwyIuZ6R+QbC/2iup7a/wNU8lzgeqy9gGzp6+eMlKqp+SHZpP1TsmpfXBsdZRJ1x1cq9P3yk6sSkHuRbZ2e6uZwOJko9Qen9K4H96oFk2vlPUazW7wIG7ZeN3y7'
        b'Hk4XFjjSsb/rYU2npY7QO0jvP4RBvdf6/u3Cjt4B6nnmyvxDYt48uMdATf+syEoPO+cTRkfHUJDZiao/Xe8QKHscp8ylr/80deihPPI4Gf2nJy1vlN5ufU//6amnpv9e'
        b'v/YUYcnEzwm7KKip8fKdtNMOYZ8QaeaJJy+VnKigTtPojabCyB+lXy37jRxYdJfDg34SzHf0cpIIUOAomyNC83ZFMuOYPAs7J+gzDnVZFCPMtcsCCzYyi589FEDdPD8H'
        b'ZhZ2kgsKbJNAaRyU6hnR0Q9dLs49zQE85FfviNLyxuod0bd/x4h2BBcLPXyiQ7S9T/miNfyxJkxL0QYnSLL7MMmnS4hCtkH2QOYrHZQ9OHtI1BCdv1T52P7SHvoMDdux'
        b'6jEZHP2Z58XMFbK0rjx5fwm0uJkRQXYn9+Uxz08ZnjLHG3BGmYTN2GxOnT/MJWUBpyR4FRuwgblPsWQN1jGnlCcZ2ACo6+SZ6uaXgpIU6prCPZuU0Iy7sVIlT6FHGB7v'
        b'BxfhoLua+pUE6mAtwKwJ/NLlpZCVDEXYlCInvx0TKJKyDTuLsXHHjHFQpcQWMrzYLMCJCGjgvteT0ACNwQHqZJHiJwuwx0fFD/YqqFoxH9uVtDvwPCXjbDZJofNLmrYW'
        b'KhzUFDASywTIs13BnFZufnLSjTnTFDahsaNHrhZYKY4OKbB7AfXU0VKqBNgP9RHcnXV5PFxfyjwZuhcpxuvMBWe7Poj2kh/kd+8fbExOwkvBng7UNcCddyVw0Gj7tv7s'
        b'bfyiN47HkvGuMkHEY/NsBcxYJU0ZR8vPWYmZXXzGWkCbwEVLcd94qMcG72BDYTEelGMzXMYDKVTztsUrtuMFYWWI4Ca4QRuvxBz2ROFeKRV9MgQXwQUuYGvsjw8ePMDN'
        b'1G0X7SabE2pSM9FF4Azsu6Yt9tFVhjmejIG90MV7sR31HhUE26mweKmnFxW5CvyYrBVE30seB5fhrOmq5TJezF48Sp1A+Y4DO99MJxKV0lwCNB3k2ckRTudPLbSZ4EXM'
        b'g/MpYXQ8oBQaTckTpaaQ4aowwIzFuA/24FE5FoWYLrAcpJgRBG1wHY/ieY91m4yi+ica4zV5mgLyjAJMoBF34SlXvL5VNRxzpjvjITkccFdB06wJWDEADirxUAqNb1jk'
        b'Ai0GuBN3mgpuCik0LoaLK3CfHHIxG/bZw268jsVQFDI4Jh2qMWMwXF9vOxhayZ6XBS1RW3G31M2ONKBwOF6YH72or58f1rINhE2ziXMGiRMkzxpLLUJX3U+0EVLomRBo'
        b'i9d6Y/OlrlvutuWEvmvgClNXGrBVGT4H9vGJa+0llAjHY8xCQ9erpgYK7BXwOlyBnfQlKowEGxPyYcnqDVAGdWQ5n6BMtHh6+ngq4dK4gVCyROvw0OKxWLWCNDyjXwhk'
        b'RkLOOjyOlw2j4ZrFZjhjwIiHDfEEDerp2VJPJ28Dy37UXQY1KvI/c+sYGc8k0vU5uBiiEpnjez0c86KbAZ0I5BzBIi9Hsl+Qce6vkLlum5IyndyziugzNT7d6ImhIpgy'
        b'FOujJ85TmcRg7QK2+MhcaYb9PTzgvXu/t8NesmbaSPPoyhg0IcBhO5aQPUwUJFAkusNJ2xRqjIWdcMLfwZP0XoEfXwYu3l6UMIgGOHSPpAj0JEpmAt0lFwU5LZEIm0Pw'
        b'0ALzzZNTUxbToirToJxHHHgFamJPNDqqp28Ao2J2DsR6C0UqtgR6evv5OzrxwBa66hydNYEObHfGgqA+cJq0rYDNA8vlEqJ4lywxEEJ90ceQHLMsxMEQz0ORD3VIwa4t'
        b'1CelwEYJ5GAVHkuh2UYK65HBASo/Dr2/eKk2nKZTMA3RavEcOTFyoQwLnrAhyvJlOOU5Ato9R+BpKBoP52UCWaM7LaFiQEQKcy42wf7FZNdsMjdS4EVzbEpOTCFbZ7ko'
        b'WKmlAdiGZ1mUCdStwmPBZPvylpINrw4Pr6ChJi2zUxiyfhk0T/VROTHN3Z80za5D7Bg5hTuKVtkoINM6gAN9HZrqFAyFIVgIR7Ceki8Z2ItwCC9yRc8bzmGbsn+/VDNy'
        b'2ON+srM8AQU81uXIskmkrZfU2GQoSLAeb6SKTlA4QtWHBXEMGWHcfwrm+5LHpghEwawkmzyVccZ54nUeSxRJpjR1BCpXSLDBz5f1Oh7Ak9iqcVlTdzW2YL4Ih6FoIw8N'
        b'OQgXlD7WUp0H2CSSHYLQZLqFR1YYCLJhMVgqwknHCazIzXGQqQlVIaptuwrOyQQTC2k/3L8+hXoPbciUbyfzXsUMCZSQgHllcTfsJoWNgQyDqK2urKR4Z1YF2cWhJJg1'
        b'XYEHJbBvOOTwHmkaBA0ObNHI8Rz1K5qsk5pvt+MtzA+M89GQRc/BMyKR+nbjZT6ebXCenCb5Tv7MdSpfJYmBjH4rfdhzIWRD2of5zMUsm7Q6TYSaVVjPOmOya6QPZwQf'
        b'hvsWi1A1bDMbs0HD1jGickoVDnlSEWrXQx7bSDAzcaaDZlWTmYtFtnYBpEUjYK+BEZSFpFB7w0JoSCJ7ALMAQK5Lj44hneJPFk+egyGWyOA4O9UXycnW4ezluBB2qci2'
        b'ZDRVAqeHY26McCVUot5BJIbn7/TxCG6Le3uOxbXpw1R5lpErXbzTn/p6ZMCp1I/MPUttPYPkNdbOnnNc7W6+0ccVRi0zsDg+Lkv5tWHQx+Ml/Wu+MfhNWFox/TmvEe9+'
        b'dv/F+5+9V7qwpnqUV1CzvezTkJcanhv/gfeHLneHxQw7vcXO+59eZWs856cPKjl+J39Q/rydD2Z/XTBu9d2P/lpXu8ApadzR0i+vTMobVGEQ9/zHf6py3TV72+E/rWy7'
        b'+OfMk0FRtg/Mrj39m3x407E9p+sO3WqIPKGaNGj1DwuW9nm6+ZSZ/U/vTExXqZ5N/m3wPaeq4U8ETzm98eyXtW9u+fCH0Ni3X9zThEZfJH0xb9/60d+oP0/64NqM+X0T'
        b'0oY4/PN4XmhpAspOP/HcW1sjrk4aPzQxtF9o+/unFNWtnmcObfEIzbRv8HijxkPc86773y4+Ufep/a++7j/0Wy1denrDuzGfvDL4eK772zlxJ6IfvPDr/LhLL9+84Bd+'
        b'e5V92gcrI75/YsyC5Ge+2vbp80c/M/tx1jOHjy78x/feH637dPCKL4Kyvhsdf3p6qvmCA2b7n4xat2jWxTdXTC+8vOa7Txr3ByXIXnLwdf3gs9fuzU56Zu2B+BhJ9qyh'
        b'Tm/YHvp+aPj9AVPNB/5wLWfIX5IHqENMXY8YRkW/+tZL2zyf+fzS1i+97w/GUbc+Mp92IvjnWVNuXso8GTbo2eKG2OHtCX955rDZMzkP3mxWnP15cLHbb2k+z0lD3qka'
        b'2+yY0ufq6mNR6z/6yN3SY+/2e98+Dcf2VF85NkwovX8iL3Vd4+uv1hx5dkR63+/9hI827Jp+I+OZ0atvZs3vX/Xts7vfmeRX9O4P406s+3bbW06xdy+XjXlqa1zFX54/'
        b'vD3cIOqpXa81eaasbTy/z+pM5JUxM/q34L1bE+7f8vvWf8LsBwYP9sknD+urGs0iHZzUSdqgDJNpPCyDBmWQ/TmH8YcRaeuGrw/WDtYG0qwLZIRdT0hwl4/lKt2mQ7by'
        b'fBYrQNZJndoLGpU9qUeIWFPIlLolRGDMZMFwcCCARWoooFmS+sQOFvAyCQ6u4tvhqGkdu+GKaPYo1ApY3WkzhNOmZC80guPsbZZAFR7SxBj1w9MszIjFGAUtYjrqHONw'
        b'hw66lBlmw4gElsEie7DGEG442Dur4DwexDyi7RktJysWrzixap2xLNSBRjrmOpLdCIokcH6eEzRBMbvaJw33dWa5cQk0XyKNnYe1jCSt73gac8Ci/YoDtALr3nTSDLkw'
        b'3EdGxKRME96GIxvgvIOzilUvhzoJHob68dgGtazLp1sNcOjg2IGM4U4bZCwWArOwrJ8aChWJpnhRTcMANcE+nSJ94ISrHzbL4QaRXOs18Ta2xl3snHLB0gsrpkjhOLbA'
        b'SX5P1vC+PlrbcwAb7D6YTUTBq1IoGDGHtXrU1nAgslGeixMjYDQULJeaB0ijITOWhbFs8YVyhwBHoqXkL4N2doMSb0jIiVY/i3XeUpUTkynwzNYOmYIobMVsxCatoex5'
        b'/IwgDdtFDgkvO84tVDlifPdws3kWUqK/5C/izERFeAqKdXE6ci/JtHX98dIIZl63gRtE3NcbdEKEIR54QoNOBszgTptj2Dy6e5ATFG/QxDl5Y1Uyy7Y8TET5nE6xN6FE'
        b'4NGG3/DYG3J6neXsduU7sJSMuLeGPIjIR7bmmCGNn8xne2iQORGRKWseVEymnaCMI5PCAi+xF/TGw8Edp1oh5JJjjUisLewilg6nzgvt+Q/HyDF5cjVw5kEihrRrBICo'
        b'aN3xr4RdnFPvAGQt6nn8e+FR7elPZTQW1Ra6Dg85GpM2dg50ssY9MiLB72M2UaiyW9eln7ESdj7KKIpn5rDdJwGb+vvgKXtfL7L5BIn22+Eie7nRTqRFjnZk+yDvqCMF'
        b'jI1Vmfwr8TmqIf9BLNvf/63DgG/eDbmTGbg+JN96GLjGUcutgvHXWDAeJfkDCf0nkf/G/klNJDQDiULgceA6a3IvvVMiSh7IpBQYj6Kqy0Q5ZcBhMMlm/B8pl36yJJ9o'
        b'pJElIym0oBFHpAwTDTkh+UmuGD+QSUw0MUxm9DcpjV0yligkFImXfnUg90pIKRL2k3/JRcnncmvKwWOiKZHnLOoMad26gpsBedASDyhiOWgOLIKIxStFbuqIaehI6+pw'
        b'ZfT7r42oStGphTO1LUzao2uUgy7uidkes8iv9nptj2/Oewj54sO6TCWyHDf/R/hZqadVZEjFv8/PqmVefEvSS5zC3KhkSrAYFhvLMFk70RuTRsbQ1oXFdoFq5fBeEREc'
        b'vzDMJi4yrUehPArGLjR00cZkr7io0FCbtbHx4RtUzhpYXW3kQ4o6MiolloYfbI5PsUkL46yPETGUqLEn9XLnRsTEsRujGOqAJsE0Us2zTjmmog1Fh7KJiVA/PqciBUuY'
        b'ZuPFIhDI7FTHUOhaUg+NRgizCU9RJ8dv5MXqXs0rIjRURcF19AZtkP7R9gf9GBNnkzrZmTJ8zyPdmEY7Mzk6LFnX2o64kF5L1Lwbw9NlgU48+oIUQNF1u3SRNn93XVJ8'
        b'SgID3eu1RPLqyTHhKbFhSTy+RJ0QGa7DgFDb2NEsekfSBaRaBtGyOYH8Gpkc7qxig6AnvoR2aHKkdlw0487i0OK6k2dqRj8inmUPJ1Ak5t7K7DIAjyCfFIXeyCeNucl8'
        b'3tgRGos51sBuajU3g1NYwE3mVDyESwvhNE+WSCTSNs+X6JwtkQMtKRRadulm3KmxJdoopNReeTXRFcsHDfPsOzpxO54Pgiyod4fylfO8kqEWT0CjwhSbZvo7DsVKPIGV'
        b'86Ft+BY4Z+G6DY4xM8/WwdTcJ7i69pNv/lGWLDDdf0EIHmC6dTAlFC6m+TY0mckQ9mCOYLtehrUrsYE9XmLLczNcrU/YeFh6CzHv9JfK1DQdMWyoOPr566a7XK083v/5'
        b'6EtfCANtla80GoTERDfsjjj07Nya4zvvRiq3vm7z6tDt086IXna36qZ/Mmlbn62vH//qyrSfan+Rnh2y9sdv7wY9G1Da5/mQyF9Cc6pWpRvnP/1MYv3y9z7+2eOgf2HN'
        b'wujlKYt8ndyOVzzIGTm46nulSsmJHAuhAY90jTSfY51IlZpzy5kgDXVO2ED99EQmL2dKzawFzFE1ddqwx3JTySF7jNZ9ex5PsLAKbFrkoqa2VSc7DbqGKR4mMmmJlEjc'
        b'12E3j1Avwat4iKcBnffv0HygWGCyNDQQiea4JgYfzsMhgQXhT4YsFnbuBgVYxUPw4TqeZGH4NgEsGNyWiGTFXD3Ai3Se0dyDhZ68R46qBnZVx/CSP9fIDjkxjsotk2no'
        b'fbfwfSKltnDRFs5AHQ8rP5q2DS/69hZYziVbbIACjVPukSEkRjQ/kC1ZJs/Y9ybP7BCmMCmGov0/IN+lVFqhUkq3YAFdUV35IZ27HvU9SC0l/I6OIzeH/FpFj1zn3o7c'
        b'DOFvD0l/1NMiGltKTp415OjpArCgzbLVF5UozZE+Vo6tlEXNyt7/UdbLeRscGadBYO0K856i5udvJNsByXbtMc/LPbgTdLu+QytybUy4ek14bAwphZMBazGroigGZXi0'
        b'M7vD2YN+d2e36UOE71Sqpn+msRhGR10QI0UsVkeyZsYnRdA/kOOg1+1ag3Cvtw3OCxb7hjLUupSE2PiwCO3bazuk10IpLKoOhY6eJJowX3VKTDLHmdc1qvdD5JGtcncP'
        b'CXX8o48u/sOPei36o4/OXbbiD9c6f/4ff3TeH310mce4P/7o+FAbPaLWYzw8QU8YqVcU573hgk9khKONvWb623eJRe0aLMsi5nqXVPSFwC5ICmPg3x1z+PdEuy6lsi3f'
        b'FVLHO7t2WS0sSpdD7vLlRCpMjQn7Yz01L2RxL03oIAunewxvB19uMRGPEMdkQicWW5041pdzgYcaGApfLhxGxJZQkxGrFQLzGoQpJ6uVWyCD+vGPC1CRgNe59yJnKeZh'
        b'k6urq4GA57BZ4iXgUTiSzlx8Iu6LdPAn5wc583ZJYL/oM0jNLsCxHeQo9veWCAmDJZApTpkFrcwJIYO2ZQ7+XqIAJ1ZLIEecgfm4SyVjPiDcBRVQxRxdeNFA6GslHSTO'
        b'hKPYzoRIr7GYTa41JmMr+WWEBPeJI6KhmAUhREDbNPU4cuypZ4rxArRumsYqC1+yRY0t5uRY20zRCc6I9lg4m73tCKhlXnvBBXZBueCShs3cHVOG5YvJM1BKe4/FIaRC'
        b'nkrCu6IW6vCYrn3YPII2cFA/HsFwbOtwXfNWbmPNC8ezrNSNWJGmaciyIawdpJ46HqZxyBsusqYPwjbWdhqaqpKyMiEnfXxHdXU7WH/kerNrTlg6QFffjEGsPqxy5h4g'
        b'k9HKVCMy7uYOUiPRBcshi4/KbmyDK0pTCkCzfKzUUZxtvJy3otkDTlCvndJMFMwspSbi7NFwI4VyBWB5Ghz1ofJvMIOeoE5gIhDTUJGybUTaph6xa1AOlSHkl3K8hqew'
        b'jMja5XDN0gD3rTUwJd/8IAsLZtj0FbCedG2hpTlUw42oGNuXfpKoKVBozbUDi1+Z7v+Uq4X8TkXi96Xb5SUln1RPMWj1RHFBfrlN/5FzrMwMFM8lW5Vb+T8zwqLfxImG'
        b'd6xCfvFqeXPf4a8mtz8z+rmLI5eGXCj7em/lIvfA8rhn/aU1t752DHxx4bn5qz57ccOeia9d8H/v4oe2S5e/YGrY4nDkTJ/v//7k4J1eH06IqUksfW2CZ0J9+Yft2TWp'
        b'H7cv+qh6VtvAaW2jt3qMK34nyev6S69uz34pNVb8OeMlw29+uO6c+FP/NyD9lZVx35QvefuWx7EVb3w973vDNV/4PuH+lnH0hR2TvzXZ0rhj+rdDtkz55LtS63cPt8Ud'
        b'L5x+ZmH6k2v2l6/5TVpit+p521CVFZOGw2F/Ijf0R1MXotbSD2exkJsw2yBjm9bWD3npPFXXdzhPJ66LSHXg0dDlcIg7cU0cpYbYiJksnXbmPGhngeVToZzK+GtXcwfC'
        b'Tmie58ATSPEyHJDBbhF34QWBVTkWM8fpsm0F3wCWazsbr/Ls0/1qTyK714do80uZ7I4lQ7lsnwE54xy8MYvMpUIfKhErMF8CO2dDM5PQZ+BlzFMrsVkUYrBCxHwBq5WY'
        b'y66ZY24E5CdMlFBbPmlPNll+K/AQN2NfNgmg1+QCHCabBp1+pVCBB9jFZVgHl+lVsg0dDxExl0ZgnYRTTO5fg/lOmnxXXQ4r7LGSzocT0MKs69AUv1ZN/dhj8bgIZwQ8'
        b'jDe28RTq7PEz1FAAORJhCuaKZDfAS1Z92UMr0qGEPES6L2OaCGcFrIQCe97U8glQSha7CU0KxhwRGgQ8gm2hrERTvGCsTk0UhTlwQYSDAh1yOMIuYSYU0WzlRImwAatF'
        b'2C9gXnQU80AswmKhq1olxI/hWhWUEl2j94TNhwRDy9REJGYKR2jvCkcoVTCo4ZKpHOSfjBlTuSFUwpQP7ZcJS6g0lmhNlbp/5Aly7wPJgy19usY0k7r9tQgtLM/SpLNA'
        b'nZTbRV9hsYjkXQp0OkquLh0yn3y6+RBF5eZD4qx7tomobFQ1YWlg/qr+3cCxbsvWBHj531aucV8cFOTh7+7lEcxhRXWgWbeVCWExcdo8SZq+edu4UyIhs3rqUkg7ZXtm'
        b'dgXXYlhbWaJGD2PvyDtr0P9L5vikhVRJpKmoa8lvCkMLKZ0Lil/lcjODAXOouV0m+YPonjILCwuJGaWckwkPJm1WiFZDFTzeCTLwbIA2VWG1tcY4IQqDFspioGBHj3he'
        b'E81Ptb3YlYGOgoJxQLBKmQYSjH+mwGBG5It+pgBhFB6M/73jswXF5ozoyz5bRfTTfbaO6E8+D2CfB0YMihgcMaRSSbntsuVRYsTQiGG7FRQbtNywXIxQlpuUK8ot6VfE'
        b'8ELDCLdsCjgmJ3rvqIjRDDzLkHHCjd0tRNhFqCjnHX2uXFkuiZKQp/qSfxblljH8N0tSmmW5UblxlCzCPsKBlDeOgpnRErONsk2zLbOtohQM/ouWbMRiaOUsprZPlDzC'
        b'JcJ1t4JikcqEFUpmtx5/25KuDnfGi8HA46Iik34a10Xi7HmDhtKt800/ORPxdVqMOn6aOjmC/Rzn6jpu3DQqBU/bpI6YRleMs6urG/lH5OvxKultmX9AkN9tmafXQs/b'
        b'ssVBCxfViLcl8z3IdyNa5ZoAf9/lNbIkajS4bcC0zttGHEA4hnw0iCK6s/r3VOtGq5UlldNlto9+208XrszLP5gjSv7OsqaSPa1rWUnHWYHB85fM/WledHJywjQXl7S0'
        b'NGd1zCYnqg8k0VRZp3BNiqFzePxGl4hIl24tdCZag+s4Z1KfStJRfo2EYZglraEgjaSDfAPc5/quIWrCT2Noo93nebEWkp+LwjbTfS6ImpTVyaRQZ9cJ5DvZ8mhhNWKS'
        b'H8d5PETbahLs5b/Q12PNvLkh7p6PWZQb2aLLu7zyT5O7PeieFK9Wz2P6S9cyfOPX+anXsZLcaEmSjpJIA6tpWebd+uOnQfpf6qd+vXaeStmlFDrdkmp7KXtqUj39a7dC'
        b'prJCxifV0Wv6K3f7yeF3vOltw4jIqLCU2GTW/Wws/+8mkXBdIDMF25VE65msi+2DcqsY/2IiNtAH7pvN8QmznMOTf2RjRbsn0x6SXnJbQUllk8nU1p93Rb8WchDYrluK'
        b's/ZZ/bkJl8h7zCSf1K69ywAZwtMPyU94WJ01hvzMjunl4N6gO73pVP0HbVOIf4+MBmNtF3sLmowGQct9yvHdoox12QrGj5WtoLVzZhr2Yuf04nnIMVsiO1k7ObkRd1PR'
        b'Tfoh1s1gLQuxTQKjmmCCjHpazxudbLotJBu7+R6qh99GF+Ij75hqY2evjqE+r9TJzpPsH6NIvrZt7Nw9H32zZg3Tmx1tHlWP/v3Fxs4r5Hc94faQJx53q6BFdG+0PkOy'
        b'xhjGrUY8RVxDa6WlTND3JD1P+WPdp01CUkx8UkzyZo5LbGdPT2lKGEbPafvebYv29PSm99Cz1J4aku3pIWivcu5wy05yHufsOk1zS+/FdHhwXdmtmlI7/jyJ/ZkXre/F'
        b'OKyF5tV6Aa3g/TNWzXAr9HYPc2VM64oxwBZZ7xAUGowAvW3qwJmYpqPI7QklQWEddE78Xnz09D9yjbEbUts+s6myAILIsGQ6odRa7rdOyBzUha0HqIDaZUk5aWFJmniD'
        b'TpQbrHdsgiMj6bumxHaik+u1KPe5IR4LA4KWr6HcRgHBHmsorU0wa6XO189J7vR2Et+EeP8wGioN0It23LQKnMai3LtrvMPKzDwXvIQOI7B9tz3FXm9wARuhBL5O1Zwi'
        b'r9sWY8/fTntLTFzvKAocs4NIrFrG3+iwOBuPxUF6rOVxNsFpMclbIpNi2cAlP6TxfEPUs5bIgvFKDovdzB7Uv8PZ65+zGrARPiAdGCR05muGRIdHwh1Xet4omcdKdAIu'
        b'7/JsFywZvbsWK6mHJ4F0j0asUmunb7dyex8TDWtkR72MrXNtZGx83Dpa0iMs7lRCMeohU5n7M8t2Kh7ehnt9sAibsRFLpIIEq0Q7OLOa25V3QS2chspVndIKzZR4msdH'
        b'UJFpbOA2jocKWXCUYaLCdSzjySElcBz3Eq0YTk1PgAJsJV9NkCsTTHG3BPNFvJQylzZpKh7y6ZwNtqRHoo0OQDR8nMa45y0RJsIuM9y9FK9rMvwjpo9gdmJomEXEQ2oo'
        b'xgtrmdEZL0ebKU2TIvGQORFdHcXZ8/umUJgbPE4EyNZOOLEdrdBlxySYmgZRpFg7U9zj5L/Yzg7zsMAF8xwpNijHPXWSE2H0QF8Rq6ByAbOAxwxN0EKZHoL9HM60DU4z'
        b'F8ff1hsOKRcHMBfHRZNUgWFZ4DGshDyOcsozfzydvf0wF8v7kBd3CcIc30BPaRDk0hw6vAKnN48WoF2mxINLoTZGbPhWpj5Oiimf8droQjdjmGPhsS5q7/24shWz5jR+'
        b'592S+ZKN5dyIvkGjLUyg9RvFc/2S5qU1D9z0xTcPkmWZhyPDFDOMB0Q0Prv0hVcnf93yfOPMwtwXy2qql0d+6HklanLfMS8Zfq6qvDovPyLM5WJVxTGT8xcGDnNL/HLH'
        b'5EXTa7Knv/23lNLJbz694UrSj++Yl5wJee3e6J+/vZD3q9PVq+9+4H3Eurzow/NrXJ91NXr6osqUGRRdoH1j5FAHZyceLX1K4gpXoJgZRRXjvDksM80+c6TRHYaCWZB0'
        b'jq8bZK1hQRiBkOPn4N9h462FRmrnVcAlZuddDPsX0liJirGdA0wkuH/JYBZdgvlwGes48CRWhKaKc6MdmflYET2jc5C4+RIpVi+L9YELPG7+tAlcUUINHu4ZOL8ZDnAM'
        b'yfLV0d0NulLMgur5UL6aBWhYYBtc7YpxqME3nAyNDOJQCvsZAuFQU6hywCqs7AxJyfAooQwzuTm3MdSTmd/bR2mi7UU4HIBH2ds8Afv8SEV0yVXiPrxErvuJC6ZgNbMR'
        b'TyetKiNr3pd0wvCha0U3PAfZXfAqjP8lE5wOP2+OPqVqmyU1xEl5NCxFI5GJigdyCf0poZEkjMrZTCIRB+lRhTRIcRqsnHVib2bl2C7wdH4P1cWah/1OXez30sDUiLcN'
        b'1jC0Pn04WoXkEweq661CHYW082NIwd1B5qj5KthzbtBtGSWIvS2jXLEqw94icnm8Kw1/vW2ooRRPahN7SYo3154oIYIuKZ4rkSYaNdKUA4Vnm0eZ/87Udy2YVnVvyuTc'
        b'iAh1V2Js7WHai+VPJ4b11EmjbKZRIXFaqA7KJLQXD7+jRqjR4XLR+Mqe4ajdSR45xzHV1ztE1WTam8kaQf6xVCSNcKujAX6UlsRZwPizvXD1hqltomLjw6gJwYaR0mpY'
        b'N/WF14TFdWG4607xq68VXVSH3hh4kyM3cbk4WUdau5HHhuoJ9iT3xERQoa6jKzp4Avk72Ngx8nr6akxosw1a4OzsbKvSI27yIAkWuBxGZ1Mn6mpdyZybk4vBHdd7LU/3'
        b'TAfVpmYKaAK4uhJv9lqGXZDHAg/qwPFY47/Yb55HkKONVjvh7KR6g75YpLJ+ltr4BB65/ZASNvWm8Omhg31IcfQ/nT5Ie/hh6poOK04zq3stTcs93ptmZ0N6xSPIf65v'
        b'Ty2u9+Dmx9TstHRhvCt0rM10wmrmDV0XRBmOZMTcoaH+8XF0p3hI1Pem5I7aGacv7aOwWBppTTcI3dSNSorfSLoqIkxPeHZsCjegrYtJjYzTznyyNCNosI9deHycOoZ0'
        b'Fy2JdFwM+yvpZb0N48V0NjuoOr+mhsN67frI8GS+H/Su6AQHTJnk6mbDWXX5+9A2OGrQRjXvy+wAdG2STbHXcqJSkthaY6uds+Pq1fb4yTTNJlijXWk57WkA+2ZSS2ws'
        b'WXxhSVzH4jf3vreo1fHhMWwQdLpeQlI8paanvUi6VjPYZCHwad97Z3ZifLTxJ1pfWEJCbEw4C0OkajdbT50D8ntfO+58zwjrYJilh7aNHfmucrShR7eNXcDiIBUdDHqE'
        b'29jN8/DXsw7tO2UYTFLZP0begy6ma65uq+/G0fSwWNEuKqeiV5VzuD/PHr+Ie+w7KZSz8ZwZtuFRJg4xHem7rYbClxsHUh3J94votRpegQrci9Va8g3MmEh0zS1YyjUu'
        b'cuksjY7CfdAmaMKj4Iw9j1Wqwlq8RLFd+rvINOguprA3JIWh8p2n6ZRKPGCcatqLkuq8hAX3GyXgFczXUEJQ0pAQDUiBj5P9Ek9H78WdlFWiBpd0ZbzQsDec9+gD+cac'
        b'8gKvYR3u1MY14VnMpgqrimjOS2mjDpgQVe8x69PU1cG9E2inBbCAC3DFQSUXprlaYaOvE1PYg/AylPNAK2jD61QdxmJVSppA+VYabH0Yuo+TdwBViHlBBliGWcajB0KN'
        b'cYcCOoe0vpJGs1gSxf9UCByPCITceelE380kKlktVJGfezZsghI4s2TQvLWrIW9eUkxg4PrVSaOfgIoN0RYCFs0cApV+eJFbGqrxMOxTYkuCiURYOlCC10SiZUNVCmX3'
        b'xbO+UKO3ZZg7EHLnQOlayMIzpFGdm5WFJ7GcfqYRYaHmmG0jQF1gnwFQCqe4T6nMFc7ykLQZ2E5j0qAF2xkGjecqOKkzDqiWeJoFcDSfhJSUECxJMDXHshBN53eyHFCD'
        b'AR0hLeSHFvYGdkK1gtVjhjnWWO+NRYzeZMR6PPdQqCUFVsFF8mCIbljpkGIzZJsulGItQ0okc+X4Qp/OPEyFULeITRxSrA/DHyGzaa+BGm8YeUOeJZnjebg3iOjaeSK2'
        b'J5ounIP1KT506jXPTOpRkCfXVV3gFFVXl3QpErKUUG41Gs/0g7Nw2rqfVIAKvz5w2t2TWXdisAR2s/fr+loSPIHlpJpLM8jgZOJu0rMsNA/K1gqYHYTXoMUkCOtxJ1t/'
        b'jp6mncw0vl4qbyfnLoQpcGWbFnlJ0y7TrquG9NiRFEso7T+ar7CdZPIf1aJGBHo+tPCHl2w/Ty4EeVuRpjeF8kjNU9iOR3VcNqMnC1g8bwUL4WFUPlhtjOcdPE0XdiHz'
        b'0VD54CFTyhkZU5b3ikx9iiheXw9e6Rd43f+dORbvDd16/cb0nzOkziPmWpXPkAWUGG/xnzfSeOU028GL8lL2Bp/aeW/Yzc9V7k2biJrX7yMx6Cj58Fzr1gUnv3rxh/F/'
        b'r1g+0Ntx/dzvQqwu1s1J/7QqLndi8MJCSV7ewX4Ld0QHTFwxa2Tm+hVJV1/3G5V4YkrqqwbvfnKv0q/vn80r7546de/AyJZZScaTUm4Hevk5Bh5Ovpd0pUEWvunOrcJz'
        b'nx+p+eK8o/mrs4+cy/qtvtR00+5hD47PnPuCZMOn7WWX0P/d2//0+vLDL6/d/Eby5ymbTOLLA78zvvaPr36x+7HFe8W9e68M3Db2lTE3B/erOt1gvrP15/b0+6futElf'
        b'XrZqw4dZ44ftC3wWjz778s2PZl0dsN3427f+8XNEbIO7+cculdlXp3/StvqH4Fu1i5qM//rVvXPH7ooNMbPfHfDLyA/kP677cs1Pn2/4aMez11oyv2/+62upe3+YNvub'
        b'wwfHVDzzS71XQ4vsdubt3DsfRYyqMXnq6qmmwn5/vx/bdv6XIu9z6aHzzhXNdr4/8LnIdz5P3jT0ctqv/teKHQJT7k6u/Cjs44nfvP639funbj0n7//FpI0X+766S2XN'
        b'TFMT4cKWrjYkKPWRxuIFc2bTwdxQsmrzoXRRQDfbFLRiLjPMGEM1XNKwopCD6Jw4F6tUWoKSMhsfsq2e6iCkYPGY2IztHJ/gElyFRm1AJh7DHG4S2q5mBUyFcrKR5KeZ'
        b'xa3qzsyyfRBnVqujsZ00ywgrOnhgGEAD7pvCW3FlPZxX+pj59jCCYZPAozCbsX5WZ/tcs62HJHU7nmRXzchJfEgb3llqxaM7oQZPMIuWexrspnC6XlAnE+SxFJGu1Rbq'
        b'0zmAYQk2LNESqUD9LHI8lHnz0M4Dfjbd7W7xztL5HniVp0UdhCMUU7cXsxueVlvIyF7Y6Me6cFD/cT54Gi5rtnxt5j1Uy3gPn8Zseg4VOVIqO6yGEpmjCFe3QTaLeRUD'
        b'yGnrTIbtUneb3eCtzO4ZDFdgTyezp0Oy6xLIYUn9ZEaofXy9ILdbMptUcCXNOYOH5S7RUMJRCU5DcR+WQEeOmQAiWJjNn4CV0pnQPIhFq46yJruLhidGvlw0SqUMX1DE'
        b'w2ur4QpDtvZzUpE2zJRg5iAbbIdileKx06TN/zNhe1laaMgyKkD2ZjPcIcwyFk0kLCNeYiLSXHoLiVyqEC0tTHg4qJTmxlNmDp4lT3PcafinXJPtbiEdIBlAftJ/1ix7'
        b'nvJ0WIkKAzOawybR2CQlZjTbXlQ8kEnMJDzXXS7ZYtuLTa5b6rb/o9LdO4xrSTe65r49fvd3zlK/0Uuqei9Z6iXU8knRBXu1fGYIX9vpt30+xmvrjwyiZldmEuRRJUKU'
        b'XBcjJH1sVP0oleyn0B7qRlBkHNF01Y+y+zEjg0axoWptmNpmmZ/vI7SXPuTfsB7ai6M/E2hgF1ak+nSmv+xAr2PQdflL7cjWcKIHdgZWQr1pP1MpkwGCsRb2dqPz2zRX'
        b'IwOk424um2YFLtSJER7QROQIDzjKkTyzsTWOXkt2Jnuwcyr55u3lJJkN7cKo1QaT4RpeZkUEYgbsoTWQMoYRUWy/ACWuM9ilNFeo5J6/Eul2O+73mz2V6V/q0RRh7k0T'
        b'pRAa+4/AcQKX0JtDYT9DrRTUWEB0sKMCtPeFFpbm4uZApJ69lNHnCIWaxHPbuSh0wAZrlEZJFPatBvLNiMqmxgyulZ2F41DqoLL3M0iHa4Jss4g7F2Iuq2ownhjtQx0t'
        b'/gZ0o4Raa4kJUdQaOeDnORvMCMZC2ZpkKq4KUDwBuA7B6L80OHOjYDeFmqO5KRLWlOFE4DvC9B68ZMC8gETby2GIckHzybBpElawjnQhT1m5DMWaxKBdW7W5LqtHCDTV'
        b'ZWQcy1qZD80JNOpX5obFZOaL9qT9vK8OQ3m0RrtzhxPMGwnFkM1Q2Uzx9PRgKMTyNSmLyXm7j0LYKQJEvGTrxBO/FxUJQ8RlRqauof5f+M7iKvGAPrbCfCFhhKEQutbZ'
        b'eQn/49OzaYr4HbVBaKhxeKSL0IMcWrcS6Zxj5NDWZO0Jx4VtYoQQIWZJBgontDTRu4nc+Q/qLKCkOnMjknxj4iJrNETRsljyS3ema+oBWCXX+CyYGgKXopQsCpo5Lx2N'
        b'tDIyljlQmUgMmjSV6NG5kDsVs1LnLIhK9EpKj4OdQ82gQdg2zgIuEPGglL3Zn2JNhQHCokXiolCTN6wW89ctnmYtOApPKhU2oUPuLSbTkinwucuhuBsEoUiO9L0MghDq'
        b'+7IBcYdsLOba5XjMELh62YrZfJ1dcZlJriWaSsnZuk+QWonTF0AZq/LuCsoDamFrZhPqu3v9JEHjaw6EUlM+l/LhGJ9MlaN5IlOtbAVTJ+F0qEDVyVlE72DT9jK0x2IT'
        b'ecpwEVwXpGPEmfHuKpE5qDfC8YVqfyoySpRG80SbaMz9l4Yymgxl0k16EAD99pQo9KApp4NXrxs81gs1jnhVmYot5pIRmEnbPiUMdrKXChkPtcokKV6dRFn0iIIXBgXc'
        b'jFGUAs3YZIIthmS17SW7Ug5FdswYyl5LJCrdSaUgDMQ2IZBsRRfwAuf7bMMGqFPa2TvgBV9xMJ4TFN6SFatgN0dU3DOcKO1NLt7Y6isKBlAVALtE3E+G5lzM1j/XSdUe'
        b'ZEsO/OvyyMU+xVaLrW60Hv310Od7du4ZuGfggD+FPTl5pHmfZ/5aXV1VlDnSdlfewldsK9afe+6pgyudo2+Nu3lqbYHbnoPnhro5P3F5bUyBMn1Xe0Zj6MZlPx4JfmOk'
        b'NP/tlJd/2J7ycr36z1eOTMn961+vf+/hcfW8yz+eUiZHle77dNm+FtOtGdMbnaqw6oO3P7zbWPjGogt+w8Jr7Rc89aTRc1PeH7jMecqBX970mbD4p2nf91XaJaXXFhSl'
        b'++c5zlqs9vstJ/PkWvvElNN7q+syF7+02HlAU+LEr+4uvuf8t6INZ/a/kdTvr4Xr7hkuvr+qThrz4ZATYdteF+4eXj9p9wC/uv01Bp89gbfnTNwcN//u+yELJ547e/Xt'
        b'4wsaCuOqQ7L3hk5+taQm7dagVOHNqPWH9oTGnduqXOD2+so753d/YG11JOjX0Y1Ot6bF59dfrP+g9c8rn/3BoLn0z6/sGee/Yv3NrHb36ZkTf5pt/au30yc7qgqvvNx8'
        b'B09eF9+d9JfXXMdH3j28qOC54Mi3X/AMf/Fjs2uJOP1G+P1bebe/HLto39C3/G8/9drHebfuFb332a6Pve/P211zR3xuZj/fs0t+nPzKuzkRWWcNDvfxidxqXGy18bfn'
        b'B70/7cLdsuNbnw56a1eWod/Hzi8tdjU3+sb1oJOB9H6p7djaQXU/fzo4ZcnrSwZdeaLP3Vc3V6Z9ftf6UnHYzKLmgINvNR9a9v7G4wHCu+YF+7btNyz0/yx6yF9G1I3N'
        b'T4sub+l3JdC0bWvQK/jK+3VfTTf8KNhgydf208d9ufTyC0fvzlwUGO/08YYfJC9b/SaJivss5LNPjBfe377xqTOf5aTue+PVgAnOqU6b5H3uffLriGD3P6984cGfXnrK'
        b'7aU7b904Y5SbuOt68JJ38t528AtKzN9esbdlYNnLO8w+3VzX/8kXfTzW7P7Octw7769aa+7/pvj1uNk3h0UO3rwxLH3CwdXp1mpH6y3b6luPfPnh1fdST47+tuX1mTev'
        b'X2/Ym1b3wWfR+zZ+eez1ly8eeMbi79k/T3tjwdOVX255bs2Byh/WT/nNIdd49dNFa5TWH6bN9ktf5/XGkc9nJ31f5PvRkDf/unPyrslBkz+cumnvz4e2Tz0d1ZgTnOre'
        b'cGvla4Mvh2/Ze9By8u1n1q22S7gbd2DrnWefdPnhq9SBG0vPzj/6ek5qbaXl5GuOb5qsnDE6qzXO+50vDx3f+tYHKtW1lOAP9uz4ulyh/nO51dQXVIl4eNzotk3eu69s'
        b'9S4yPTP/4FsXA96adXRL0jfXm76f+IxPnNGLYce/+NqocU36D0ave1//ZOuyL8ISXa4Vp3h/fkq1uTXrgckt2RcL5xyIuVr55Otnnt4fs+uK5IH09ajZ3139ceGzs6wC'
        b'Pr5cOvHMh9Cs3HFnzIOcbQnrGmct6F9y/87epz7vP/HOz7c/tZr0t9fTY45d/0J+2OOzMZdTv3z5hMuvCW9MMd1s3Ry27XrS/Ffjvm0dPvR4xa0vhp2cuWv5wrM/vXqy'
        b'erZB06i/rNv2jc3qtAz84HzrPwf/bP3g65jofZflD3JXVHhbf3jv4LmjP5tbXplf8aqXagOD14CdfaC0EzPLCTzYlZpltQtT/2xtsVqn2eINqNOggzQmcnSQNn+7Lgyi'
        b'A4KZ8hdsxtW2qpkTfcghaDJDpxqau0rXYQbWc9W6YPoYrqPugWtdaC0nYAnTEX2IPny2sxpLZIhDnVRZosjisQBuajiA+6Z3ZescupWTdZZjOVfUz3krOjATsQiyoEji'
        b'FIzNTJcdiZUz1ETIhYqOZCZTbJfOwdIhDEfPDA9BsdqZVO6U5K+iJ30TC9nBXKkwYQUexlp5sCOcYHqvQb9NPlqbhXwYXFojsR8EZ1k4Tl/M2eLja090+lVEQGwRJwfC'
        b'bk7WmmFnSMbDhcjV5KHJeB6KJaPnjudabGU4ZlOAOSpTQEkIx5dLwesaJlu4BEeUmONEKW99pH2wSTDES5IAd2hnsTwJo3APvexHNGt6BzaRc8YUcohQgCcgkzV5C+zc'
        b'wjFsYS8WCbJJItS4cCvP1jgs4aU7eYlwgojUCmPJUjIfjrNx9JYuUNt7YVECS1Mt9jeEKjwhWECjNNljLE+cbSJCeaaPN6cFNUjBg3hdIp2/gOMmVi0iIlKTD14MUEKN'
        b'nVxInGSErRI4Dcfs+DxpN4RyNYWhNCIjY0Dxt/cZY5EE88dADQeUOY6ZSbSFcNbXSIWNtBPI+12T9sV2V96C+ghKWU3NMNCOjQK3w/jNYY8HRY6mY+ngrDK2s4caWRru'
        b'FCwHSMlEvYB5rHOGhEQrnX2wRYX5YiCRXc0kK/HgSp4reoxCVqr9xQmYxWWF6lGwj/Mf1ZiRGdlEXpr2OgPSNJgOpUIfaylUQC2cYkA9kOkBO320fKeM7BQO4X5hMGTK'
        b'4IwrZ/KF2sHL1M5e85fBeRNyF5mNcunsJcF86hdjaYTS28k3Eeo9yfRUq8SNcFgYGCJbiHmbGW6h8TZoJn+GajKZ8IYAV5aPZiO7YcQ0H5UfHoAjHCTbgKy/cumMgXCG'
        b'25nORQ0nzQ520OFBMjBIol/Vs1ZFESHlmNrLXiXBA6MEKZSLZIFeTWDWq1kuRLRtwnyDMZgviEoBri2Gy6zUBNIb13w6jHqrFNysdwMu8nc9PpZMEI4UOWWgIBsmwknY'
        b'u1oLplSEZ3w6mauwHs8xrOhLq9h0CoIyOKu0I/2Q6KuSCHBmmzEekkAbmbcHWMMipCkU4dLPSVTgBcHITQIHLWbyFbhfDk1KZ5U9aWC+wYTVgiJGErMyhBXrD5esHcjg'
        b'BONhZy+KtU76Agqla7Fes+RdxxuSWhP9iQCH7WR4z4p4zIabGYlQeAouKlVYzDqESHgtUIYHRWzGi5jPnt6BeVCksbPNkQvMyrZYYJdmjxxJJj951ZVjBCnmilBFpjs3'
        b'LmKhB9b5cPu9XJCuUHpTOt4jcI5dtcIyvEZGZyIUq5J8KTKEqYtUEY07WTcMMMF8ug8YQBmNF6VQT3nufK0cITOfjB3lc5AuGyxI4IY4GC5bsD4aj0fhisbkOnGgJgYv'
        b'dAnb2mZCfohWqN8OBaLNaGjjZsTKSXYUUzVL1TnaMHYSlvHdrRxb8BCdR0m+LqIwfozxHAnUWGEtO6xwv+sCNSWI4GuUTETSajiJV8kL5krJ3C2PZHCo/kRePqTGIpUx'
        b'NDiSAskeftFXxCylMNBCZs94o+kLbO0/gSbEs4uCgcRniYh5SWSfpDr9iiUBWntrwGDRxRbqWFeNiFNTf04qNskE2SiXPuLqEDJs/VmdF+GGmkHWi3AUT7LA1+SpPFrx'
        b'FJSsIlI95tpJ4Px60lVHyT1brNjFdCyH66Sxdt5p9hKiwQuGsFcy1SCaT/I966bRyNiA2ZBBrSy5zPpqLpFGYNkM3mMZ/Zy0IOEMCuQghTGHy/3Ydi9Zg9fV7Iii8Zts'
        b'N3TCQmEA0dTc3CCDH87VeBUq+K7OlI59FnCYTFm8MYbN2Xg4RWYB3xVZV4XgfmNsJnMBLpDtjTXiGDQhQxKmUZVLiIZzVHSC61DItrVReHmmmgy2EeamkR+0lng8RY6/'
        b'vVI4Nhmv8BVXNIKcCxQxdiOcZSu9inTbBdbrweQg0ZptYf/YmRIbrJzPt9yq7ZivTDE1kmCOgSAdIc4ly/sie8h5PhxQYwF1J1hhBR4WR3pgNpuDcXY+7HUkls5eiewO'
        b'U6yRjsYjy9nLrJ2/WccFIm6aoYGNd4dmjqF7cFk8wyNzwTw/R5WXH9msNbjNU8jKvTZDTraoo478ND5K1l0tx3vbY6KzWEtnYplfMrVJbiSyykEGwNwB4D4b83tiuC/G'
        b'BoULnNZA2/Z1xRYlA8F1SmRb7o0BQh+yQqFqCObwZXbWkTo8AnzTLbtQeK+czebcWiLANJF5wVfZpihjDwmcwxMpfNE3kIpy6FWJLR4ie/l+EYrCcD8bprkDsJlcMoQc'
        b'7UYyUWq02pKD89aTddfaE52XQ/NixVSDKNg9g825pcp07QvQeia4kfa3SMmA71nGzsv+UA452mlth0cY/L0O/B7zJ/OWZuLlAUp6COKRELKqWsmxBnlQo5E5iZDYqsQ8'
        b'jSiEhRGCQpAEBsEuDehFVSzZ4b1FyJ9Jnr1EV20OVvKI51Y8HUV7wNjbj04VH6kSLghWsFuKObBHzoOpL2KrTKkS4OxWQRxE0TGaNrBRd4XGdLU/XnAhIgTdrKFIFCzW'
        b'S4mscpxDJ+MZss0dwyZHZ2fJXMgjlVfQXSxzAwe+KJkOe5UUOVmigv1QLQ6bhMc5jl91GlxTkz0ec410r7VyujAAS2TT8PoMtiL6YM04pRN9L0E+Ds8Pk/Qls+ukdpW2'
        b'j2P8Ov5O9mLwE2Rmk1W8f9US1h+TRkWpXeyx0ZPMp33kODSEaxLPRJF19FbcQ48IJ39ulvCatV3EfcOJaMA6q2QkXu+KswxXlRxqGc/HsqpFS7I5OnunqMgeYCDMhtPG'
        b'EgmUW2hKgIJgJiFQx3uWh6OXuR3d5UzxinQqnCEnAxNA6shKydKEdV+SBsE1FtVNtqBsjpyYOaafj7Mf2bA3Y/VScQaZw0V8i6iGtjmaeO+148lguOENLOX7co4dFDHr'
        b'nJeTZN1MDSqKxSpVn/8MyK78Edc51AVP0JUnMSM/8wotofaw3r1COwR7BUM45ojJxqIlA/igMB9WDJuQenUULMpcoUFNpp+tyVUrySDK4v5AIrUWBz2QKAaJNt9IzC1E'
        b'iwcyifFvEhlFWTYTR0lGiYPIpyE/SX6TmFJcZBPyhOUvEjn9PEoif2Anmv0qIc9biMNEi98kL8inGzMcZoarTNGVRQtxwK8S+RDyk9YmE4eQ7wP+KTGyJHXR38lfTQeQ'
        b'tlBgE7sHpCyDh9RNrg4h99JyOU6zgpRhRdqjICWafS9XKr6VPG3io4VB4dz0NuT7GFqzOOA3CW3tr5Kf5VYKccvAXlw8vOc7MdE+auA6JT7/iQzVEDkZM8rSo8fllCHc'
        b'tdbvdNLfItIMloLfItK8Zn9/lYx8YwHqNSbdcFGS1gssyTvY3dPDzyOYIaGwpGwOjBKjQzOh7U2iZJXcfWf1X8Erma7rrlI6s6mHbjf5qZDI5Bqw7V9khv/GTy/KJ0tE'
        b'M3MFc2uSjn5gNVOLakInneQ3mZT+ddgOwTiFHmR2eHKFxpRPDvPqLuZ8iTBjhRzzNuDeHrn7xpqfauOHA5tIIxSaz0adPhuTz8oIE/bZlHw20/zdvNNnDchJpZEOwMQq'
        b'ol8nABNpJwAT60LDiDE6AJPBEUN0ACYU9ESIGB5h8zsATEYUyiPG6uBLTKMMImwjRvYKXEKhUjoDl0Sr7G6bM1gfRtM9P3JtTPJPLj1QSzpd/RcgS6bw1PdxKsltmXtA'
        b'kMdt6bxx85IO0EleQb8dFh8fO2QKz90c97sARzQPTfn9oCLa6liqqBsFFUk6xTN7KPxH0mmGXBTk4RcQ4sHAREZ1A/IInj8/KDKxa4K6a9JZ+sKPc6ubDnFD25CfBugr'
        b'VQfD0bXNKqMuZdBxSLrVGctD2zlJf6Fv9Aa9pK8Ot6Qmes//BQSOnjy7Bv7MERS9MIWjBRpuFRha4FjI4d7ctqXY4Iu7lRRCjKGgVcJB3BWz/L33ZWoqzd6L+hvlW/cM'
        b'ezHK/gOfMOOoT4SvMwdOGS9Mvf6PjbJLb32gEpmUZGkKudwyhfVQrLFMYTYc1cMoekkbNkKVXr0CAv2yoYfllgHdFtpjAnlYGmq6We95Rr++fAigh/6Km+kAv0jROkYJ'
        b'/0W0jiiV7P0R8sdF64hgLadwBDQ54N8J1aFdJ4+A6tCus0feMeWxoTq6Ll19UB36doCHYGf0upp7v/93QGV0TwPjGQthcTTZgGZz6clN0j3WGzRrD3iNLuOsgdSgpwiH'
        b'ySAnib3+NKJHYVloW/J70Cxiov4HZPH/D5CFdsX1guNA/3scOImui/Yx4SR6XcD/A5P4A2AS9L+emT0G/iGcODp7/DTMnyXvjmNAQQywDAt9NeS/He4OaMdsJQ27mR7j'
        b'Io6Qqt1JKbcmT6d85p/ciY5a8eSbN2/dfOvmX26+c/O1m+/dvFpypHRE1oVdI4/W7FLlX/E5/ebx3aOzaiou5LpljTi4c7xU2NlmOvHbHJUBMySFL8NTnQJu3ZJd4egA'
        b'Zl3D4s1YQv1Ra3qiDbjhTjzBnW3N5I+ZkK+End3y+udH7GA1DMO9WzWWlTg8tlZ0g0PQyj15h0K29qTZG4XNCmdDbaDovxIwq0uyt3uU5LNAm2wv700M+f2Z9AMeSxi6'
        b'95CMer2teKx0+nUq0T/psqgV0npJpZ9nqIls6lmTLo/eVs9x1yN3Xv7wUN5ww25LQ6ldHjRzJduwm8CmpCJblFIjsBkygU1BBDZDJrApmJBmmK4I7vS5E7za9t4Etodn'
        b'xHfWKv+/SIfvChmmkYI0OeIbyblBk3X/lyH/vwx5m/9lyP8vQ/7RGfKOemWlWHISdCZW+10J8w/ZMv6bCfP/0TRvaa/CoCWnVmOJZJc68rzh8CiJWThHZE2hxvhhkO/N'
        b'YyeCPTE3QIv75emNhYzUbCnF3VKkmmIjHEuQCVAG+UZwNR0zOOT2OTwQ5myt7DVte1MwD8O/BlexkKeM20MDhyfLxPwUauaZEguHdU7uQE/nRXCpV/gvCWVZPmZEyqrE'
        b'lhQqcfjCeaznITubiJRLnsYcT0ee+4E5jBCWBg+tGauYC+VL2SN4KRBO+jBZeCie7hCHaYKtIxb58ViwIKUhFlrCqZTZ5JEnItZq2GUdvRYvwhtwcKnTkqU0S9jbzxdq'
        b'Qjyh3tPP2cnLjxTiIoGLynGQHxRMerXSLBYrHTj7fA0UrmAcHuLIsZTCw8IwhTrdsYJ6xztKpyVjjqMMy5YkjEuima4s9VwmhEK+IezDvZYpVKwionIrXg/W3K0drxD+'
        b'iO69VyqwIMoQTsfZ8oj4Ejzrr0wyM5UMChKkfcSZlljKw8CLYSclCmlNU0tXsayLdtEBSqCdRd5vmi0T5sRaCsKcUN/K9HghxnRmtET9Crkyd/OPi4tnmoGrSdZnp/4x'
        b'Ozn8Q6vKXVlK101z5s5bvOLga1nOUR/JPps5xWvdU88OTJg/+qm17T9u/cLr/fKRe1ZPdJAHXum3XTnY0MNzfcjQxmHfKl46U+j5w6GnNnnkzXjiyY1TL865W/3uEs8h'
        b'ig0bpn375v2PynbnLxw8ffiZ5DGTrFvjg73bY5899YPzF75D/ml8d/7chAWTDT4aVuagOvCO+7an/5y2wvA93/FL4yxX//ad4zt7rb/L339kbXB7zdWK1Oee3Xx+T17z'
        b'L5P/frDvpNWFz5ldRMPs296b/v60yoLFK2wkc/UgSx81xVOd4oIWDefZmVlQiCe0xHnT0juyR/EAXGUBO7g/EA7y7NExNqni3DW+zG08vN9cDek25Q7slNR5LIS7nsux'
        b'Or6bpoJXsJ1R0FVb8dr3wjXyhIbt+BKU6uiOyVRq5AmapXBQrlGFDLGUqELj4Riz6bokYiNfLtAidmSu+pmw9My1pLjGjvBbXegtXsUcFn5LWlLDGmE2AS7wN/EZiRdp'
        b'KBCpywzbpL5EPaviFOKYgSWcddlSLshmiVAbb8B84ES9m+EzzpuCR1yCo3hewFY4PkODpAbFMRqj8wF/jc0ZWmZwNS4rHapHwwUHbz+e2kua33eslLz4LgtWcOI8bOrQ'
        b'MaFuicQVLq9g3OLRCeu7JnUuIWPckdcpd4HTM3rS3in/jcmUvo/SDRNYSqVUwaiBFXI5dSaLVhpqYeq2pl9mEjOJgqVHbhneXZ/qPQfS6HFyIDvSHw30BwQY6mfl7SXV'
        b'0eOxVNPrNvpV00e94H8423G3SvbTqkdmO/am0/2hVEfq6uiZ6jiSpzpiuxHsfESqY+9pjtg4sd9yrGWpiv3hgmVHpiM0CmvdZ0JWoFQp2GKdFHdDC6eUIusxYwhPd4xN'
        b'F1nsIDbDcZ5HeB6PLeJpjBPTxGHkTIErWM/OiYhpUsFiK01nCnV8PXUIx4pZNBQP8lRFmqfog9cEaB+AO1NoZudIEa5zgq3IhYILVMWx9KyphpihTsTLQB2O5CyGXDid'
        b'wK7E0i2F5SkKss2L/ETcCQUjeb7h3jm4R5unSE5hubXEBDOxgDXZdyvUBBNJZicRXXiaItnn8rmzLNcA9/I0RZqjGL9YwLp+eIOniZXCHrjEkgrJ7MLcKNFe7pRCh4ji'
        b'ubSzvMFOWYPQtoTsZ6ZwkvXFqLhi4ZNhsySCa6h/7AwbnjW3PNlWuDakmHaQbXjqAv7H8UaewsGwEaIQGmrvuHnxv5Y5uO7x0s2uao0yKdSs4mWUrCFMcSQ7a6KXH+Y5'
        b'YqkmEgnLoIniptCIQBWZIOPGma+CfB8owya1EusEd8wxD8E2rGEvU29gIvwin0SGPTQ23i6Uv2HRGGuhbuhqiiE0I3W6j8D6cAwcWabNFWw20aULslRBM0s2AFs9BvJc'
        b'QEFqBUewTpzuound9jS5kLOJIbc6BsaHCyqRz81arIVrPNKXDKpEKdpEQP1/o0OlCqFz/l4ONmAGT+ATpEZwZr44ZZUlv9SGB9KVSVuhSKpJ4CMrq5nN4XS4Cgc0GXxY'
        b'h4Ui7iU/N6/m4uMNMggZ1J4VCAcGk2/XR7EJvBmqtijtLOAGz+Bj6XtQ1o9Ldedmmeiy97ApwYBl78Fpi5ikLyfL1PtJC758/kZKiNfefh4WDecaPm/9zgTH4TVRXuLX'
        b'J3F+xBMWy+VvPWMwOWLBE95DBm/79RO3KYvXbLOp77Pg21elc5Mf9MG+77+66/2be9eZ/SagzY/jaoe5Vb0/Ys3HB9bcrX3++fPnXvGYUPJC+BrlSMOvBy+fn1tXHtj8'
        b'YtYP0h9fe/5bi78/GR0aCTPsTs3d2KA0WGD+YRo8f3/L+/fmvV592qhNMvCE6TfVkwNz7DMnrg9UF7w5w/7k1MB7T7d/s2djyEsrPvQb/Obdumeld6wTXlj/tuQvk87d'
        b'rv7iybVvey5YbxR/a8I/2+S1RZHtFe/eWvIg7fWGC39bdsrcYs2GaS1TR2z7cPj8v1S82WIn2TEzVhr7zp2/TZnXNuSZHRu/3WTpkLIqRfX666FnfnQ45zdLnTdug+ml'
        b'gVdWnosZf29DK7SMCN/69Xynf7ZVhagiP7/0bXza1Jb8mYGfpT6r+D+8fQdcVcfy/znnFnoHRUUEC3LpNuyKBeTSRJpKVIoUUQThAoqK0qWJSFFAUCkiRZGiIIKSzKb5'
        b'YkwvmpjEmDyTaIpppup/y6VpzEvy3v8nH+HuPXu27+zMznxnOv/d9cXrhbLbkYVfhaz0Wzkvs6rdaO7e1OS8iovBb8+Ttp+8UVmadaPF74be6hNrI9/+cPP0zljtN5pQ'
        b'oPn9Me/uebfzyhVvlfc73WS/mNSq6NZduR2ictrGv4v7WvKu+eqNjuVx3UlaXQ8nrYg8eH9hUtP0/Cuj11/5rnZnVM6uOif7N0yviI+dnP/M6isuD0x/7N2VWP5c4ory'
        b'XVpJb758JuCSYzZc7+LDm57blXzy1a4Sk3GuM5I9y5Y0qNo2Lri6YmedyyfTQgJu5WztfL4QeT3976erPvHfsG97s+YvKsl71X9X+VxoSbvkJW8xSmv+ZGbz1cmRP99P'
        b'/fyB0+3t2kmmSfxrP3+y/xPPBw+7F+zclbXHrrh4y/uLt30dXH1Md9fhmc7lU5fP6gxv+836FbeTbwR/eOvnOS6R064uWvPgJZ8PdaKEwmfECXvzLByefTgj7f7vO7+r'
        b'D3nw1dPz+ndo3fl+Y+GXEw/MvPuqFf48asX9ohVjkzaVZSfuPDDzypX+mXff/n7s25+nvP2NYVR5RdnYB8GNIRER63TuBi2dkvjw5q0Yu+Sv4sc0JNyOyr6VmfJhvqMd'
        b'OqXy9aR3jYx/uK/Wb3TkvOPz750fc9u44bucPZu7fvr1XsX+teaTgg+l7p+ytXn63Q/Fv7w/70TSZlnN1XF7P/hp1NfX/Q3SfxW6xL/vvjzfNS/4o6upH7Q93b/m+51R'
        b'Xwf9+sqv0zM6j9R3ii7s8S1dtfPtarWbb41ZH9IQN6721NauQ6sWO76X/d2+rrroqZF7JRFff9O6akH1uOdvrnqH/8HRe/d9B4lMve+u6PsI1Lw6P7/23PeqE8Z8/lp0'
        b'hyyWAgymW+Hj5zFuHGpUGRYO8lE744tzYB80WXtBN5wbEXEPCnWY8fERlO5obWcz8VFvKFsYIG46ugB1BBE3DA9n5iKKDIIWZlPbuBcfhfnoAJZ8Dg/h2BiK7YAHlSzU'
        b'd6BLgyA2dFEuJRg2LKm3U+2NJRb5exRD/AuFsGFa1CNy8pFRS3Yn1DhOCWKTueFDKMKYoF0GcGzzIVMKnVDkyEyWT6KLqGIQyGYPadIgwWo9sFB/KGNH1CBeDdWtlhK8'
        b'GurSoq8aQ7a2uw06AqcZZo0B1qDVi9kkdwV4aKCcmXOU5swMreaMSugwhMBp1DKIZhvAqkHnIgJXK9CklY/HrEUDg6txYkcSyZ6HJi/opQ9NTWG/BhGl0HGGWaN4tRWj'
        b'qUi1HKpQ3nC8GhyO8VJhcLVFvvR9zDepDIDViEG5hKDVJiixLFNQ+rLhaDWCVYuOgxN+PnSRWMAJdGAYWI0A1cagFpSPjvA0g0x3MunbcJga1LuIDIDAIimPdRZK1TTs'
        b'Rnko8WYUbeaNmqjBs8QDVSq8AoH4QaFYM2jbS9Ev6BKcEIZjzSALH455EgY2Q+fQfiq6JSVAsdIbERb6di3BYl8yFDAsRq01VGt42WrKiFH/fAnU8ajVMYUhmIqgdz2F'
        b'pAzHo+AqqkRhY63Y4i2YIWcoNsgbBLIpQWzrIJ+O3ebF6JzCTj6EYVsBxaLFkI6lXcIjwMX4tRTHRphulCujUDZu/URTsRja4UI424XNuNpSd5nnMMTaJg3RAnQUsmgl'
        b'xqPHEXzXMMTaAkgXxcJRDbaoj0PJNIpzICAH3Bu8cgrhIjTSwfdFWdBGUFpQSGaP4tbwfs9l+7sEKuG8+wh3VKIA1BqFLtDB3Q4lVkrcGic2hfq9PNT6zKCvRjmgk+4j'
        b'nSzBCcgxQhnGDEp7cZzKEGiNINbQQQ3oRbV6zI/SVNRkbefsTWFrDLOGmsfSR26Tl2rY7fFTgtYoZM0BXaKVeqEaXYJZGwZYm00wa8tQP53x1ahwjxKzBmc9JBSyJlFO'
        b'FaqU7x5CrEGxmYQB1ooYNgCOLEHFA36hxDa7CQrjArRNoE0S2TkxxBrBq2mhQh7qApTji2qgf88gYk3DTZDi2TxpOJnVWTAGlTGACgOZQOEazNadQh20WAMoJuywxy7U'
        b'wSsha3p45dC1m05czDHEGsGrLUfF/Dg1bVrlOmgOGPARJkKXHNABgliDC/T2ZEEwFDBG1gPtI4wsXowFdJ24zoSuka7N4heKolGFJ6uwetyEQSiNurOwGo5As3k8VbQL'
        b'JjEKlL8Nk+IRkDUlXE0HLyaSax46DXVKuBpqGw5Zo3i1ybqMUtbCOYshvNo8DQnBq6EaV9aKTGiCDAZZI9UJG3h7b6igz6bboDODqLVklCnW4zfMQwwFgypnLmGoNXRy'
        b'Jw9HieBZibrY/iheipqUsDWCWcPLqhNnWeTJ3JlBF7TiVm9G7RS6xnBrEyGV0oAlqCKUAmh2o0N4k5Ab0nO41caoTWyNGvbQEragLsjUsDSB9uGsdAMmflS0OAGtM9mV'
        b'GnSoCcS64CIcoTRoN1Rt1RgolSxKdSgW4BiqhFMb4BDbRc1wElo1GAKHwzSjEwuoE1ENXu/s+nUSShuCzWlGiqB1lg5qD6bUZ/2UZAU9Eq3UBlBzHGqH7PHzxXAQdW6i'
        b'NYzb6TmImSP+NiUUNAfnoI9hvw7BEdlw1ByBzCViAnLpKbZbTfHxnqWEzO11FQJ4W/z2KVq/BNWuUKD9QXhCh2HmlIA5aAum61WKToymeDlMYMZCEd5Z05TDow5lqJFV'
        b'PYRvm4m6RFNQLcqm9MAqxJxc/7dCthLnpkS5CXj6CG8ANcu0noByw+PcNoei3Hr2MNdvSejswHAhvCuhiQR7SBclQKcLO5Cq1NbSyMMyNXxKlaM8mVx52I+BNPGKJNRC'
        b'B3Q7Jm04F5SK3GW0vyqoSliCepQk13sxnCGItmF4Ntz+0yJP+TJ2MDWRYBiD9/r0hhYPdztmxc7jI5Psf3/MTpxjF6SceBHkBvLQglfxPlr+6GTUp8AVr8Qr64B1LJzC'
        b'1Fc3WbQb8qazCS2AEtRujQohe7YHOuBOriBQhbALN7CKclw8Pi6qFcRJaS7hIHEPV+zA7I6ekSjFxyfBgc5rrvgRtB+FygmQ/zjaD/Xp02LVJ48bgspBK+TjdjGwnDHm'
        b'Q8bQlZQ6fxAyq+4kYFqQiqlB+1S6TtygYisFZhNU9s6pBJedocMod6XPPPYeQwSjFlORKuTG0uvbjdAy5XEoH8qawNB8kohEJauKWYo2ODUER4Rm/FFQ4hFdZXRBR7ig'
        b'ooHdNgjlQyVSiuZbCedYcypWL6ZgPoLkw+u8j4dGdAra6OwE4fWGObk8KSoa4BQJmA91QBfdTRtmLaBgPoLkg44JmExBGkqnC2ObDupUeLngCR2C8ymxfCaojYLiMafW'
        b'FofPuApnjmH59mrQsZ+GDtsOQfkyMUnCxIRi+VQRC52tC6ftGJKPwPiS4AxBqJ+bRlUSo1HLagrk2wBdgow3dQqkg7EKndZhKL5Z6PgQkI/B+KAimjnDNIQ0JYwPnVeR'
        b'mgoGwVDKWI9eB8ggKD44YkOBfEoYX5QyFDjmZGpDFPbQpcPAfAzIh+oj6CBHjp05iOPDhL5HQpB8cjhJR8oS9S3FG0iK9g3D8jEgH1RGstLLQlyGgHzqgjBeDUoxsT1B'
        b'x8tptInSFcYQho9HhaK5+LBXhhP3QrWDID5O5Dmb513Q0W10FhIgK5ZC+KA9SEjmF7hiaYvUGW2jbu2GObOsEcHL0SEfmfb/PTCPIqaoesH7z1B57GfMADZPV/RkVJ7q'
        b'ICpPn/6IeW1eF6fNfhOkuvzfROGpqCpRcWKKfFN9iPM/pD/vSh0fw+U9EMQMg2dI39Amyg+K5TPmR/FiXKodr03el/6XeLw3NReMxOMZPwmPN+pRDcR/C8bLIUoRAnD7'
        b'U6VIKvfLn0DyntAo3BKCXIi/PoDHExE83gu88q5SZvB/h6O7jCu9SWCH0dz/CEf3rtRa4LUlwzBzU4dh5pTfGS+hWg4zU1Tx2H02D+VwlrOEfslW1JP8mB2ttvKvIv0x'
        b'sFyguFSlVK3UIEIgv0u1lZ8NlX/V2d8oUYQoTLRfCLMa1DuRMDya+7T2ae/TpdG1NQnojoLUJOHSMGmYSiZHoorvFwJVcFqdpjVoWhWnNWlai6bVcFqbpnVoWh2ndWla'
        b'j6Y1cFqfpg1oWhOnDWnaiKa1cHoUTY+maW2cNqbpMTStg9NjaXocTevitAlNj6dpPZw2pekJNK2P02Y0bU7TBjg9kaYn0bThPkkEr4TeGdHPJEq5auAoanwpojo51X0a'
        b'eGx08Njo0bGxDJPhHKPDBKp5s76uuWyJp99ypULtZpfwiLElsXYanoOh9AZtdRJiSfwJBcsza7oN+zuDRmsgn2aOKGxAb6ewM1syzIxQaRVHsQVK2zv8NCE8ngaTiE0i'
        b'kXITRpoBDg8sYWMWHrJxk1l8+Lb4cEV4zLAihtkpEkPXESU8yRBopPZwRMIrlth/ySPMaIhYhdn28PhwM0Vi6NYoatEUFTMMskFNrPDjEPw/YVN8+MjKt4YnbIoNo1bs'
        b'uM2x0UnhVM+ZSOhLdDIx1RoROcPMOYpaPVkukSnNd6NH2oIRkymlNSGbCHvlPAyMuI2Z5VLZQLYQM0U4sWpLCP+zSSJzaLlMRnAeIcMsB5U2e7HxUZFRMSHRBHCgxCvj'
        b'ISBgikc6qlCERFKoSTiLEIJzsd6bhYVvwwRVYRbLGk7N/yyVz5aSFbY1VjHSCmxj7NatxEyZrr1HTA29ZMJ10Y6t0delG0O2JsyauVE0jOxIlKSHaqN88C8lkExl30Ac'
        b'Lw1KQnhMRIQIbaUSW5QjzeBSxDv1d4uoEltMFdeiPWLfYZ+HlNg3f+H/ArRsxGZ6stHZk+wQcQ+ZCeIaTw+lDR0N2ULLHZo7PEvUzhRvzT82TrUMZ0vqSfv2TyBPdHjn'
        b'EeTKxhC884Nxk4KZLSArbLCQ4cvvCYF0QsLCopjlqLLeEcuPLNS4xHDlFlYk4r01SEL+GOoxwr6WxcchOzAkMSF2a0hC1Ea6YLeGx0cOi37zBNBIPN6Z22JjwsgIs339'
        b'59FsRpx1WspFN9LIYLyXgvDLsfaXO1+7by1rTpBdlnXly97uSFNwUSk1X6ieCJvKtJtWhOm+tFENOtFB1E2uDBOw5CAjPt1l6BB0AH1j0kRVLJx0baB8qh9V9ft4L4MW'
        b'dHwbrnwPt0eO6qgeNzyJeDfmuGB5cvRUvW0cdWBsM3EHLv4wEJo/n5u/EOVE//Tw4cMDoyUkmI3ZR9HbPZ5JkXCJ7HoSKi2p22ZUOsNB4CQSODWX90b16jKBguexlN4A'
        b'ZQqUp41ytzP1ApYv1awseW46KuW3SK2hBtpovZAeOFMDP1iizwme/Gx0NAiXQW8MSgJQxvAi1O0i4/Afnps4TzKR2EQxD6wnIRtd0rALRJfoQxG6wENTJJzAxdiQ5+UR'
        b'riMaIrfCMjQW4uXuOCmCIjjMBaByVRN0NJoW6IiOYJmzEz9HvXCc5OFUZwkxrnEyEe08OmwMBSRCiC06OMNhViKkCpxmirBFfxH13mphiI4OPcXzVS/lNPcI0eiYDxu7'
        b'E5sgZyjDVmjmOc29wtaNyYky8rh4lhELPeLq50pyrXIlsuEwFc5yHZXRVnCc2YCeTlGjYmQ5uVBYZYu6qBRpAIUiOBYQQO0MdkajC8NtWAYitqBcD3d3WyhOEeIWQrUJ'
        b'ugh5RqgDdbgbQp67hjqWqvPdfHy58Ajd2ah0L3OL7ckWQ9uMaI+p03W4xEAyHpkujn9QPjHstHfzt0S5rqjAlxhUuvujtsG1S61nVsol+lPUURackEhQj/MUaJL5juKc'
        b'txuiapSLWmVKu5jDqAFloE4dr03b4knU0vO8xRxUyWwPMtBRlKmhmugXn4TnXsxb4dVQQR9FTGeeeavRmTj62il+stVsZg5w1kKu2AalqJLe9Yo0+WCoFtFHM6E2WhEH'
        b'ZzaiDk3yUio/GfYZK70ex6M21K5AXYGhtETo40fNeIq1o2ArtOLaTFQH64K0TYn0zug4HEdFQzPusIZNOLTiSZxNd5PxrOERZzxt3Vb6uw7mVw4opKJODh2LNoZuDWiE'
        b'XD9mVlsIpfqPvextG8Be4lAxccjEhaHzqpzz4iix9utiRRre4ftfTdxaMl9hME33hSnVuy99V22fWzInTvWm547szH0lwSXen4x7NVveudEpYvqeg+kHx7auiii/4u9n'
        b'eOnoTZGDn6FfqZ/mlCn+2fKX84+4XZrz71VrPvj9Tn/v4ssdSYmr5k+7c+Xzpcc4SUN+U2fQ+/ujv+ImfDI28cXnPPTkCW3Lpuid+jr1iM+Lq1VdTF32PHc3brzqB6+c'
        b'eKFd4xPJ531nN5uqy7ReLtTgM70zPztd11ifYj/lqU/uve3o6zH39WdiW+MXBulfPvjV0wGjJ7tH3c8Ia/ju3tGJjtOj7aZ8+fWXGRu4jdNSwo2XlR1OXmWoF1Agf6ct'
        b'L+6IZ9ha+XK1rWUd0a9/5Rk1oaXB2dD3yr+MX1nzzvNPS25NX23xmeMH1051pKfcPqXhUup77ezPNUmBNjkz3r7/i86Xp36oHrf59nOSlnUmVoej94z59ryd2+jYOz3f'
        b'1kf+2zLol2vfxxqH+z63+w35ptuRX6t7vPvrN8/6nwr0llQflsTZNnhvjk8wqd34+hz964ve5KeG6o3/rPBzq5CwSL0fDrz+XM879yKkC2Y/66lXMTrti2L/lJYPxja/'
        b'VKGQRH7V5CT9uOv8pK8+fvCmqXzNyRq1zfeXhwWUt+o+5f9ctNHCTy2WvbLL3Vey98Y2v3se7mp39jyXnLbG4M6O0Ld/Cb11zmBs3o33Fn/zBvfd680Xf73+0k8BoWPf'
        b'2LsjwuaV1/Ymb560wCsSffvm9KNjv7WZ6jXaZUfV2z8GLXjpxVtnd72oCEve/MqVwHcW3Bz/3cMdr9o/He3W/uuRD6R+V74+vv7lWQF1P3p99yDC7cefY641H9Ued+Vu'
        b'wuKoB5lfKV6+tyDRaLMVKm/2zp46vre/7VZVRcibUmuDX7WX+n3RuODUuI5XnEz1Hn4eK39Nz8t5rGwJve7xTJ5kbecpeEMd3k6NvPs8uMAuFKtXE6docIaQEUxcUJ7A'
        b'aSQuhT68tQKgh74bsCHBWu6hgpqhF7+cwy9c4cyup9IhVT7k2RUKUTpkCLbhO5hSoAeKiZs6e6b2lAZDDzohTFwDzLfZpHiURaIi2a8k5qx7ULmaYAWFfAKxssS7Px9I'
        b'8BCiz/Wwg9yVVCsMOfauNlYU7akihhouKEUVb7oaO3pjrEsc5w1T8iejDub3FmrXsKu8S5AD+eS2DO23lXLSDZhaFAiTIA/YxRfkr5vovtJWbkNUlBo70XE4K6C+nVBB'
        b'L9uC0EV0kTjdhYItI40M0ElXmsMc1aHT1Lh5G6obGbJGfSa7cz3lEEW9fqFzJoN3hQHA4igbQCWqGPL6lWKzhEdlmBpl0xvK0Sh1qrXcwBlO45NdHMmjbDeUQfVZoeEc'
        b'ueUe5hAMn2IHeW4sqhLHwSXUzUymC3CnqTYszE7pdbI3juoLPOCQDI+0m6e7LVG5ecF+yJlEryInozLJfAM4w7xBtkM36lag/XI7OGiAp8Vd28sWnXUXOFMXMZzAc5nG'
        b'Lu7blxK1hBwdUKPPt8BBgdNyFlCP4QTmA7kMHYvFFXrZQjN023iyOmmFZtPE6IQY+uj6mGmZPOzqE2VMIj7M1obSsYqDxqcgf6Wdm6eN3NMe5fGc9iYRPqk2s4nuMN3F'
        b'rnzpXe8S1CwijvNUXJUeCZ+Cw5BLNQMF7ihfhZOqBaJyQROqljElXTkegkyFB/RDCbmqF23hd0PRGKZGPYRqo1FnAmTuHFB58uOgbidzmpYLmdBHVHj1+IhSqvHI3XhV'
        b'Iq13/kY4RlVQVCUqQZXo+DoeXUAXjNnq6INiqNSwg35nd3rB3czDsc2oh85SBBzbpnTGOWXFY7pNOAiNzIVrzmxVqmBEWbacUsFYD8foEojasmLIm6YeSvXiN6j40+t8'
        b'HcKT5K+cFEEVmiJ0hIdCXXNaoEgnCncIyuAwOmBNGtXJw8ldc6lNRDTqGcfU1AuDmMI+U0476gAFxB/igIJFgi7sgWKB36O8xYcq/KyXan/hLMcR7S/Kwy0zIwOc7R5K'
        b'Zpbqf9E5dJ7qgPWhVYQ7j7lwOtAui3QpOsEeclA206dBpYCHv2EZQ1y326LD1LIoYsJIS39qWDR5A1O45sDpXZj9XIROKnXm53g8b8eslU6y4RSuv3OQj1o8R8pph4mc'
        b'4QIqS7AlooWJB+RvT0JnteKGmDKC7LZHha6etjIpJkjlnK+zqjY0W9GOY1ZMS2Gtjjd1TfR2Gc+ppAgz10M6fTYOz9NRhXW8TEBpdMmrhAvT12nTtoRIXXF/5TbbveWw'
        b'n4UGlHBGqFmsNx8doW8Hqio0MN8t2zqZvQvNwsJlqILORhwc0aWv45ftUW5Isgqn7SVygn3qdNk54XE+osBLkpCbdI5H3bwu2o+JEiUbLXAEs0HEMiUzgfldPDKKtmki'
        b'9CUOKGswMTkqG1TWOEM9VchYo0OzFF48Z2LJLGa8ZzLXgY3+6AR1FQr18ZxgyE9y3ER1YCY7USZuJ26JHG9MShPsoW+ZK9ov4iahBslsdC6CkpipmuiMwksWJyemF6Wx'
        b'ODPP6Y4XrYIiVELPq4V62sSABRXMZU6XIX0MXeeLUIe5QoZ6J9JBEkEWvxOd38ZMILIxZ19g7Wbrbmvl5Ym3WQ/P6USKQuwDqbNNsj+4EY0j4JhcM3SIKLRlGyRwBGXp'
        b'JFDxsQllG7CFsc350aWx0nEWz82HVqkX9DL/n8nGqNwav9MK55XGQTzKsEbH2UIuxOShX4McoGQJt+FdSJaxHrogwgffIbSftp1H9T7W5NxJhmJPfLKpol4BUwR8ptOZ'
        b'StmFBTbiMFILHXpEzxQyRab13+tz/kd6oT9yONCFf/0Hrc9eLlyd1xUIhETKm/CaRNMi0Ev136USXarrIZG1iD5EKqjST9o4nzZvylvwlry+oEuiduEfE5pXl+pLpPwo'
        b'fhQuUx//1cY/qji3uiAVRj36DU9+tKneibwrVcJZDPmdRsNvnB7xfSCTMDDJTaK9+HgkQEXzv5oLEStuqPTB8ZRjeVJBPGf8B9VMKtdj8WTlzB/36n/kS+H0gJX5I9UM'
        b'OlKYNnAtTu+VbczCI+3MrMjFmJ3DrBkDDl8e96vwl5q3iTRv2581r22geb+MI+1Q3rGaRYWNqPEvVZaJK2vir6sGbWSX70+ss3OwTnMKgKao3wgz+hqB8f+jmmX8da2g'
        b'wavloKgnV981WL3FErPEmKi4xPA/QPv/3TZsYm3QDBq4ZvyzJvQMNsGKjIAiAQ8BvagcvKP8b5oRP+bPZrxvsG4731jiZigmIpZ6TDALCY1NTBjhtejv1x9B6ideaJ5Y'
        b'f//IFTfMi84/mvd41z+rDAYrGztU2VL5sr9fF93p7n9W13MDdcV7cn9xf9JCC/6s0BcHO2Dp9we+jwa8ePzT5apOHREEEbcAT2zCSyMnjPoSYJv2n9aqympNiH1inVcH'
        b'6xyj9DvxD2uMGCANoSHRRDsSFLstPOaJ1b42WO0cUi3Jy67so4fr/h51VPKPx0F7sFUbo2MV4U9s1psjm0Uy/1fN+l95v9z0R94vee5RVYXIK2rJfG+xgjDfr0ap3Ql+'
        b'0eX1UNWIjzxEnGoOf641V8ZTps5zGb216UUHVw5Y6DEZCJWivCc4sJw6YEtDuO3/yFXt5SJ3Gj5y2keHxwQFPdl9JangHcJmLCIV/Cc2I5Vr+RMnln9Y9f+XmYn8azMj'
        b'9vKL0h5vwSvI12UFL7uHaEZ8FM1zYueYF3gXPcnQYnx85Ns5NvLxmfxjzE1QUGhsbPSfDSt5+/rfGNbGPxnWP657xLiStpMWEEmbKW2H/H8OOJliilt+n9ag0lbIkeAR'
        b'F+ERF+iIi+goC3tEvsM+P2kvEHGRRH+cMWLEJ3ixG/+TZlCl2IEq4oY0BbM9qM5s7lrJAhmvSz03NJhu4BiudT+UbFH4oyzteDWSvZa3c5xMtSpfj5bMvM7R7Daf79jK'
        b'JU7jSEjGSCih9rvuFOdPHGUUuOMPXsR3ho+3j22AwG1wUsHFXoSaKHSI6szcUOEEdzeiDYBCdndmBjXkKkvCWW2UQIuHDWv78SWoXoFqUOa2QQXIlClUPeWhB91DkS+o'
        b'RfB4qIcyCy2mvepHRavpnUeH8ppKjCXm06NRGfM3koHbc9gaLqF0JV6YR2koy4Qpzqqmb1SKsgQjhOVYVIJOhqMLUj+qeIudpkHlRVu5mFNTEaALVUEhOoKLpjqbbsiB'
        b'w+4JkE4Ne8ViHo7pLWS1ng5HaeQSVIbFTLW5AmqVwAlIldL3dsFBfdzgg55KcBCPpdrGeVSxZCKHOpRv60UlT+l6T+gUjLZDFdVgojNrododFcqJHz8PlI/HfQGUDvgu'
        b'sF4oQftR8dTHVqjGwAr1GFqhI9cnP+j67L9am6Rrao+tTTsvugA9nameLvhbl2CbON09DB6rQE3WFOgCuZuUAT3coJ6uzaekqJWaB68OVIZtgrwJdGgFdCZ6aM6C9Mis'
        b'hU+A0/S1LfPgtILYDcMBG3YfWYf6mMuTCnQWFSuILTIWbh0sx0P6PAqodYESqBwIqsMnzLd30aNzHwB9qFsJy4B2KFVGErL0YRrABos9SiQNOkTCdZEYUCu0Gdw2xxNl'
        b'DsPSSDbQkOWj9lI1eCKBCaPa1UG+nMd0jjPnzK1cZBIWZrMW9dIpHngzYj19cwkqpeM1GvavUEJabANZCKapsJ+q9Dx3wulhSBrIgnQW/gk6/eiwRSYG0KBS6Aw0DCB0'
        b'IBtdpEpbbQ8ossZ12uEtYiezdfPkuYmQJUG1cHEuOjGB9jgRHVwzgIvxHcXRSE5ToZrtwRa8v6qVxtYkdF0PqlIVRkOGUyJ1J4KOQuojVtvojOdgDBZJhDaUsTXeETaO'
        b'Wvd70EtnQljgFByCPLohLFZLtsAhVEMd36BOKLAlepGRRuu0+CVQP3Cn6gVpKqjIayB8c4+ln4JSGEwt8iiVcYAjrA91cG7iAJ0ZPX4Qe6DyFDUmDEdlBgN0bGrgkBZA'
        b'ScYwyWtixfROILg/RopwmR2MHIWiHrpAx+HuHKH4CJQzhcUTStBiJOP43jUMBIDpSiHzkwKd6AJbbpUb3YfoAnSjnvWCkacqfXEBuoiqlIHxslA6IygSaGYdzsQEqxYv'
        b'Y3yyycLnEO1sEeQowelwCqVak/hFO9AhThyCCePGQNqJ+TwcxAvN1dYGKmEfRZEeEnZj4ldKI2WrBGg8ZjZPbOZRebAauoSaaLNmo6Ixg1AWBx8CZtFBhag/kQI5KnkN'
        b'RsqAuKRSkrORtCwP0mUCc85wUFMN8lFHkpjjUSNnboFOkitMOqD2s+C4ArVLcX+6DFEZB0V2Azv+OO7sKVQinQkVHGfD4eI1mEuGxeoczuD6jXFw9BjNhcw3QeZUaoGi'
        b'e1kr2OOuky/7MmyMmFAt4/wlwZq8+Qb2pYaPJoc76N23JtjDe3IU+3LvSjVyXjpIQoOj09fPfdx5A+UnyX8yNru59dop/G5+m2YYF4DJapwQNihnU8ZIGeOZT3qEc7+u'
        b'tiAyPCZ8x7b4ReFqSv498SnS2T6UjqoVj1yyI3K5eQAdsJHbQh7+cHiECwdUIiJBmfVDPd2heIZuKEGpNiVDk5HEOYmD8lVGZIuhE4nkUgzaUDucICp9vDFLbO0IyrIc'
        b'Mt3lNm6rvG0DXEccS2we8dmlzpNYbc2awRGQSbmBWei4BnTvwvRbZosneEi1ZOIvxnPVCFVRNwISecVLuMcPyx+E+/bEvOeke2N9cbHlF5ei//Wt7YdXP63KyjO0e11F'
        b'9X3jqFHTOwTNCuk6cWeZKMNZ/zPROm+nS+Yvzjb+OdWvyffEv1TCkg5F3D2v+/MHR2bP6J3ht+79SIP733RHtB9pk72xwM51kf6qIPUFn9rW11XfEhZJpquUf3xdYnej'
        b'qPrScova+x+lF32gqVERX9rS19534pNvbkfp9M058+2kW9udVBu2nhPmKT753l9PUfLwrFPyu7aLg7dfWHfjy/Sr6Ym1AT7hCb+7ra2o3TPq9Gcmn/iVvflx6vhp1Ss2'
        b'vBe5L2V9avq3FrvfL1nic6xD7YBV0cqxLtXxhb/V688oGT39SlTo/qrNspWHih1rtT81fZG7pxkiy6gpj39qi4lcmrz2Qdi81VeSw4zEN9K9Cgo/yY54Zf1LV79svHa3'
        b'9YeZ7/WU/f5ddkTnuM82Wvmtn7Xv3uKc22d1HixfvvCbaSofTputuvua5rWeHA1bRf+oT39I0Mvb/MFPz+9q7FpmsMU3Ou3N1S/Or0/ytm12/mLesh2539jcDI8/Zq5z'
        b'eXzxhaVfrPhkvU9vfavPByY3F900vTkLvnszZf1W76+Mbnrm2XiHuausaHh7YofT1pbx5/I/DFZzM5iq76Iz5qvOMMdQR7eju87/2moXuarqRuLuj6sMX1McMym7sqrn'
        b'03f3p4ybezsqssG00XN9llX1G2MOrAqqnW+nVf6cwewLz/607Ledh16xmbQwefLqhnXvhOpsvr2utbBt2fdam+XLpFH97o2XF82732BxJiNa69qtI1fmiS+q/LvHMTjq'
        b'uR8Otl36RO3BrTuf2914Q/vNL007rz6/PaS86YeV8t739oyOun+xYGumh/T55J3R1xJtfvy04f1fUk9ee2HzTOuq5+OmXp2y8tOu6qzqZ968GZG9dPbxmqOvad64txrO'
        b'b7mx/HuTD203hR7++lX4YvFxtdM1177R/sDp2atF/Ui+9+axnhhRxo/vjX51D5ozP27Krpd/uxk0+qfZcT/2y+ZS5dMezKQ2kuMdGsXLUR+l1H1zHZk3r1JTAlfKk8nV'
        b'5kGDJWarMeeoBydFUBWPTjA7gTMLUamGlYz42YKyhQRrNE4IgDI4Rku3Q/tEVNXJwVHYR1XXmJ/OorokLT8zJfjUaCHTxfquZWG9TqAybWs50ZYnTWX68nHrmAb3IhRG'
        b'K2GWLqYDGtpqFdoUb5Shr+SNMC1OVfJGmOKy2H1Qo2ZL+xLnYS+TwkVMl7VwVgsBaqiSNnlMyGMBEzkSTpEpac9DKVVDeWO+oXsweCFnHo0OqKMDtN36KnOHdLRQYqzH'
        b'bzC0YJq4cyFwQoPCfAQ/HpOY5kWBDKPsh0UMpobl0Ul0hChiA1Aja3A7KpgzCG9GfUYci8mJyiKZJjYdZfsxyLD/soEgl8URzDDkApxH+QoPMi+Y8LlLsJTUw6lrCng4'
        b'GlEDC5EZFU6jq9oQgGSzDE4JM1DGWDrOduiMIwuciwWLQUcE0Txtlx5cgtrhcTlr4RyFOa8yZKrZ6kB0cjCqZ2oQRUijLNStjK+ZHY+HmTgRKBCNhRpOPJeH9nDE8MNE'
        b'SoN+Fk105pwBaDZqYP4RUHfcDAXKk8tR9yp00F3gVOIEK3ygMhcA6Dx0QwELF58weQAjmzWTmRWcw0xAD9FcxhF9sBRqwjn11QJcSNrLVIg1eioa0LSNYkAlkOuEuQHC'
        b'lqJCulbdIH/RQIRELMBOwmzHWTYJhdDsouHmaS3FA34IiwUXMJuyZBubwJ7pi7CgRHh/NTt3O3UiWRnDOfHsQEeqM4VzcACOKaPUDaJnDQm2G3PJWOprRhV0Nrdb848E'
        b'heQMpqAminF1w4uPjI2z8wQGHEXtqMR1ABIKJ/Ro91KgGdUN2afgCsoImi0QTwp1Q5AFR9GBEd4jrH0HYh3Xz2HxNVsWwdlhKF1ohX0cC265NZ6uci/MYhfSCJOh+jTA'
        b'JMqFWjpKi3w9SNhOanEigT4dZx6vrMOubLdnx+9igQn7fZSBCRM200EPV4VGooPm0DFzqoRG3bYsHiEUpQzglaWboZzAlcvwqqZrpA3lWgyEMlRNUoIfpXCJVXYKMkdT'
        b'9KONjjKSYYwl2zE9Rnhfe40EPhbhFUXAj9EuVCkeidJClOEG+fESU8iYxF4974L39uFHww0ylOI6pr1Gh1G2fCDYIKpdayoYjEdHlbjI/THE9JasvsLZuL8q7oK5aBIz'
        b'KzkjJuh9AprEO7hFGf/QgXncUFkZMCwydyfmnYlXky4ttqAv+m9E+TZemGhjXoufuJ7TwHsYtUrNWMBflIYJAXleIEM5rmLZIvy8VUB18yGDNng3Xs+niPSG2USo4VEd'
        b'dHpHrWXHQibm7c9Yr7TBu5gIFSqQvYfTQJcELJvmLKbjrDXBXAPvTBExVsbkrn4mXEAMnQodmE0+O8zCR2RhRQ18VrnQwmcZTxhp0LZ3LW4ZMWjDvNgJ2aj/30CxR1Sy'
        b'/72TxevqBJUTRK3hKcP9PmG///MF7l7OkIEexRQGSX5r8xZUFW7DWxEFNgUIqvP6vC65MKQ/BDCo+UBTJEiF79R1LPlRvKWgz2vzxgJViitDH7K/msJYovIWiIJdnyjO'
        b'MWtszOsKJOShsaq2QBTlJqKxVEGOWyKY8eoPxeS/oP6A/heRUjVpxIBRDLwp6OJvdsoeVTOT/gfZLaBKKcUiu6HxYIKF+Lpawo6w8ISQqGjFdZWghB2hIYrwYUr1fxD/'
        b'AAsrvxPd4G+DWvRf8ScRLlPhRIb/P9/DpnIPn+z9MZFEWILcSXDiH0k3qMhbn4g3nCOq0LHRm6+04CaObrnBeO/o4m6UI4gWzGJm/odnojL8bDXqobaUg4qDsVAnhnwd'
        b'OEtvBKSYC7sw0ALUgHpxK1YqS5wwX4xK54/F8iulLCd3Q/uwylAtJ4igzjSRmK7MVJ+AH+Hz79QfVWaIK7MmRVQtQiXWxNPHaUtXTzu556ptZDRo7A7iC4Hngo1UJ82Y'
        b'nIROUgneBB9tQwbe1LwbnZm3Fc6upvI3KtixyR3tt8Vskh8taBo0Q+esVa7KRs6bLOXssSBPzLfMx3PEsc5A9BBWr+WwC5B1UIl5Fting86toCOjhipQ/sDIwAkofnRk'
        b'HOPYFU66HDoUw8rbgc6TIv2VXoxJ3whHFLFXFWpR364oX3mjoKjHC9kn5ulw35di3nAyrD48/r12g6lb32j4dO3xPo3QG0bNayaZtztlRrscKnd9Rq7eMkZNb/IRz0+N'
        b'Wuz01dojstYkvTz7+3G6S3dzkc8vWRpasu6Y4que24UvhNe+aN70bOqY2tzaxp8/6q450R/sHlrekGdt/nmO5wTXH9MKtq9WVYm3lBR9/2LJhv0/vlh1qa4xZUp807Va'
        b'89+nvOXxi0r92Q1p+j+udvwl7Kpbh9fTEhXxmpzCA62TEsbXLKu7FinfkNJuFOEySdqgdsaiqCEv7TlF/hSv6jWTFyv8Mb9Rcyvg4MO2ykvVb8f/q8utrHHTV72BXOz8'
        b'vroLLptq3jbpvf1tvd1K9Q2Nied3Xm/57PuDP/5r+dYC4y9e8Hpnrc9LS95bm/zDmw3Vovo7RUfvbb0x1ag65Y1F8+61dFU9/+D+w6au9ed6/hW18um3rv3r9HGJ9Q5z'
        b'9TOq+Y2u6j5nO1xbL/9wPy3q/OfzLSxFYYtum+w5VKP97wQvz5z3b1s7er6UPUoR2L7g7RrDSSG19xzbnNZ7j/7yiNC5b6rfZ3kJmUcNesd/2/mbebn7jwsCfv040+TB'
        b'lZtbtF+oKGvP3vj8hqX3uuW5pr5vnFJ89u9v4i+729fpv5HoG1P1TdnEt9MK9/XeGn1O/7Kxxd7FFz6u2lQ9NnfX1FNfOV3YsTtIxejI780LH77zdNm8d7juxDc+8KmC'
        b't56b1XOuvqz8Wm/P6nt9LVnyhND7zc+Wmj+1oK9w971vpK8eefdfcWNE8S2tNxW/arVvfuqtNcfKD8U0zR/zc+998zEmRxwdN9969ue7tj7f3+h+PWD7vT7ujfjevLyV'
        b'/ek3uu6ej0xWW7z9nfOfWi1aNS/g1/xd7rt7Mn6/faW+oW5+cd/z3fPnl8yf52y6aKHz15eef6p98/7taVd98+oNIhY63Kpy1108pdTjgkFQ8dTJVx5wZ3W0V+VIZA4J'
        b'BO0zBR0P+SPzx+UobcgCklo/bnVWchPoUBRmMaqg23qYvSVkiSgnMhMdCnb3hDYmRjIZEu+2fsZ696FUo0GTP2LvtymcWvxlL6IGf7ZRKtaiZfIh42gbY2Zr3J0gKD3M'
        b'4f169DFLUCNUxxjT/dAPhzCXLYf8RxjtRYwbgRZnyKAOr4kjHiGJXzIFnaZ1x6KieMbXx+4k1oz+0EzrnuADFUoepTAMtZM+o7OUqRuPysSYD+7YwTyp5KJDkKaBRY5C'
        b'Zd80DDTgoIAysMBzno6NFHUbE8PyOBlmvLfDEeLmoQqd3s4iY/dC8wKFjEfVmhwzd9QRsQFvtUSVCuZrzYuYm6pvd1knQMvMUUzWKRoNxxXQC/myIXNIuOTGXHQUo9OB'
        b'mMmVcglOwmp+vh8WYukwHEMVqzFDrSFRukFDx6CQuQc7BftUh5nLUmNZzThnPMMtTMy5hPLDFEZqVpReUrVI+lzIoeyvFeShvMc8zwmofQ/q84dU2t7Rc0jU6kHz+Pko'
        b'G0sfG6GIDuICdCCF2DiiTrPHfGn0JdH6Q1VWK1lkxh+bBpqji3BYGca7YPugNDAKte4WJkKOOh1F23hUoIAubxIngFiiiqCJxydAM7pAH+/BS6dZYbiUHCVENhcBFggq'
        b'iFUyW1g9KBVLunae8SxDAnH5VSHVMxRtnmjCbj/KoBSKidzIRk1VS8Bz2xC2QkQL2Kxt/IjTO8iGDgGv5j7IpFiJkMWo+Q+QEljqzhpCSyihEhUol1Yqils7JMdSIbYO'
        b'y7H4cSYTGc7FrB0myVaGIix/n9FYRpfAmA3LNHQiibiqFFXhLJ5F8tpChGXRQa+F0iA4DgWClWcSneKJKGvZozAT6JuxCnPlKBOqWb29UD8a5bv7u7OdvJLHo1eIDjG5'
        b'Phcv/AxrG7dBL3okXGeB0pkKqoiDTms7Od7kzY84gYxDOXQot/G2eD/OmTYgNVARjeeMw8UTlycxwe8SHNhMrHzZma46R4BD0Btqv4IZ43bpS9jDJZA2gqeZYCxGzSuX'
        b'MBf4O6GbLVM848QJl7qHk4WABZbirUxib0P9TrgYwsRA7nCFi0OgVI6KDaxQfgJhjaajIsz6jaSwu7CM+qghsQsqpxtw6/KkEXyjCqcdKEK1ydPi4Bht/wp9aHUfXq2G'
        b'kVLTg3IkcHbvOjaQtQSpiQtaicU+O2WgMpEIUlGZubaMCaLlKYuHwWgmTBImjYI2mf7/Rxnqf+V6ZrhrmSkD5jBv/jVpaqsmDelOZB38H8spo3gTLLWMJcHdibyDpR5j'
        b'6laGSDr6mOUnchCRtQx/U1UxjccyEU4bisZiwYqEXyf5sFDwUMASl4ClIeLrQ5XXxnIa+U6q/E5dJMXSlfCQfCsVqQqqIm2RJjV1lgpEaiOmxrg+CfOhr8+L8bekPeo4'
        b'7+PGulSKUkpMzEb49/+l8bFSYrIfMcQ3/oblyom/Y3lMO0OMw4z/MBy7URCB6W9MYGJiEMHkkxC4NCI7DdBOw7IX4V/XVZRWuNc1hxvFXtcYbp46neQmwVLit5BfRASM'
        b'TyH1qA1aBV5XUZrqXdccbkF3XWuk5RqxkqI2PXR42GwY/d/dSQxZJX2Iq59NZmcPR93YaIsFG94iVOl4RvR/9FesKdIUUX06PjVzUeqgOIwaMTM2gMUegxrF4ZgfPPJk'
        b'E7DlHMfcr3CDwYpVBs3BhH9uqEeoui33qDnYCq9EYnmSONVphsPM6Y7TZs2AbmhLSIhPiktUYOLfhpm9DtSFT5pzqFNHVVNdW01LA4vnOVCAilGZLyqb6Y0OosMBEsyo'
        b'oR4Nje0GFKWPsgO2E1MT6JgyjZsGtdBH/QuYmBvOEJO74vnT8cnQiVqpkQc6C1WoboZAvTvO4GagA840N+YSLuEvpBynGzqTm2mvn0g0qma7tGbwFMffOoubJY2mWVWg'
        b'dt0MvBxi4KAj5wg9IuYr4KIqyppBXLjvnzybm70RdbLGnZFMn4EHfBOcncPNgU4sSlMWtBLScdc6yYt5anO5uehoEM2/FjUnY0abMvBl87h5Ep45e88LRDVkKCEbNSzl'
        b'lm6BXppdE07PUQjUq2j3Mm4ZyhhHrUr8UUeAAvdF6rCcWx6xh/YF9aLmdQrcGxuRM+csm0XLjUM9kKfAnRkDvS6cCyoB1j48MyeMFSKKp6lfwa3AjMkpNqpW6KgC90cF'
        b'dbtyrsugh2Z3gHKiUeEIYKhCzskxm5FJ27cQ1W4imhnOEvW7cW4hqIgZnB2ORJWoEzccj0ijO+eOJzifNmh1JGYAO3HT3SHbg/NAfVDDvkf9JIoUbv5isSfnifubTb+X'
        b'boVq1Ckhihs9L84L5y+l7XREB+E46sQ98JmyklspnUybE+65DHXi1i+Ccm/OG1VANmtOPua5q4l9FObHDq7iVgFeh7QYOboA6Rq4/dtQlQ/nM34+WyxlmCnWwK3ftdWX'
        b'87WHZjrA0Ki3VwO3XFPTj/OLgtNsWRyNwtwsT+w9mv05f7gopl+7Ypmok4gEItQTwAWg+olsjlIdoV8DN9p122putU0ArS0QasdoqJD1vWANtyYBtdFv/Q2CIZ8QQshc'
        b'y62F8+PY8s5CFaGQjxsslgdygXiQz9Pv16GSNZAvUI1g71PcU5NRB+tJp3MUKsHtWOhjx9mtRWl0OsdCO2aHSRgOVIrK7Tn7YDikzI7OQCexN1bVM+fMpVb0211Qg7nU'
        b'Elz6+ghrzjrGkq38fHTKzRf3XG43Bcu+jYhNpDH0BKISFRpM47gD5+AIZ1n2Ux6eqIRYb1SuJCYa+V5s/I5DLmr2xS2cPNuCs5iJTshs6N0cNKBqaKV2CPnW9uiANYmK'
        b'JeIM5JhxrBahC9ZiGlRi9WIosMZLpJs8xnlEkB7PGaAzOAdqiKEWU6hrA5Z+8ndsYQUpc5AyJDr01k4nxg2/SZ8R5WSB6xQRcY/uk0h45MWoZxNuQ6tkoCEiffx2Pik/'
        b'n3ndQIfG7rFG7fa0BSSDwBka4OeTYR8tAZO9MmhB+ZtRA8mgzMHjHGJUmcg4TNypdGVfVaAGt28V1GHKgy7MgsPMhqdjx0LcSO0QkmMSez1pLe2fIzqMJb2nlrPacdMm'
        b'KgcAekfTBk5FjTOVQ2MmcAYRuEGk9ygTldPnWigLE01SexfqIxknKXs4z5kZT2ahahtrOgUiqFnAGboHkv5FwUXW+mrcsUJ8Eh3kBqZLJZQzoM13WEeHACrRGWtrLNUf'
        b'Jg2kOfRZH1Dpdno5uhaOBNMnbCLIRzzZxlicJj0ZC/00F96+51aifB4Lbvm4O8RlCPTh0YKTpLvZcJ41qNgGXbIWpLTLLM8C5ZDIoYVlaYfWBFxJqgutkgxqqHJRrEAZ'
        b'1PZpWnIw645y0miDoGAuHZlguECHxsqdWOMdSIaDIshAHfEDS6N/EfORcmzNClxAd+LA2qRZ6MjgIy6HNmW7BKqtcaZ05QDjPAvY2OASu2lTkrBE2EeEJ35wjdQO9joD'
        b'k3S6zGqJAtJaOcAq5vh582TaaTEqZt5AclGmLnu6lCwEOM2zhZAPBbS5uJIedJGOPZbnOmhj54yGMpJnPzpGmwu5M6GNNpTmIANbj2V/Uo4uJqoUGN+EWk2Ukzm4a3B1'
        b'RBlLRgcumdNu+eHTPnNwjJU7kDNY40oHKHY5tbFchfM3WNtDKdSSSjPi2dhoWdAuzdiNDxjltk7DrSU+CejSP4Fy2fV/ByqX4+cdviSPiDOcjZ9GRCcy//stmMHKR5cc'
        b'GXEhrMUAadjmRbeGGB3wtR493n7wOZ4aQh20URmd/7laMSg/fq6SQA3sfCy+19AB3QHNAspfAZUDM8sqoINwAvKYHWE5nEQ1jHCYEfpT7kzKEKCOLaH9poR6QR5qGtwY'
        b'ocr1kYkHnG6Lo0B6jEVUKFWuZpQ+sOShDToYHbxgOI+tQ5RGO7IINdJieqCNZlggwaOVry62HqC2ocoiRqNCOmACuoTOoPwxKHVwmS1VjlcYHhBKDI/BKTM6o814ueEM'
        b'y5T9dVgu4xk1ORiCstxpWHIStk01ORDOCJAGpea3KXNZFO8kU6emdn0JIk684Bz+FKx5ImETs7/7LliLM14wVYXzDvZwFU9nX94co8rpGrqpcMHB0RJDpU3f6UB9brJN'
        b'Gj4rg00ipMrXd0sknOrMpSqcU3C01Xh/9mXsah3OxKFXyjkEa37HJylNAuUqnKZxqsCZBXvEzAxiX1aO1eXMHLaIuW3Bmtq6kcogT5bqnOGaZ8ScbrDHrDnKJlWIDTnL'
        b'OU4SXNGC4pBo9mVnnJhTNXYRSO2iiEXsyy1bBE6seZW0U9N2twVHzahVlo7ibNYsIPGO1iGtWCxJ+rnQBwuDcQeMvXli4D9NZzXL/bMpbmv007StB0ZN4G5XVpB/lxfT'
        b'Cu4swE8tLaX4aXTt2snc7Rn033eL6YEtx3sgjRA3zGIZxnKxqGI8YzVOrUal1vggR3Woage3Yy6cZGbNZKnsMYNDKH9n6GOrbS06Sut8xwe3fzJmR82CTQ4tTmA9DbUz'
        b'4iw9LEnbTTbHGj1uOznoqIwaMiutJ1mcpsH4TJlKRMl1SVRMWPiOeMLW/VGAJh0svjOzSSJqj0IV+EzwIhbE1BbR02MlPpVHxrmCvrnThwe6wkxPpcYS4vaMtv618Wu4'
        b'Nic8ecHBO1eYBOMp8fKKKjuuKyj8cc2v9gR5+rwUY7BE927F+q+v34msOvfOgW/UX3FS/chJ31WQ/qbSY36lKaxe7Pzu5bRlr0QtidZ2fcBp37E+dnBG0NNpomNp3stf'
        b'ka41cZnvu/6tt9YHNhqkZ4tGz93xzcEVPJ9nWVOg3twYwifaTFwu8ly+qWa/9oU1IFn37JR1zxvZ3LJqvTkv5iOLmBBJd5xKy/n8c2dasovXfTx587HQlO/NVzW5VVXM'
        b'i9OPDFon2b7t6/yrH3y1ZWvpa7kl/44Iq3o2fP+v6/PK4u4FO/kurKpc97HG9S16t9/VanJe88KyXfnVBfeu7oi9/BP4tI99tW3jt3dPms6/266e+53euagGw/17P17V'
        b'8O50ySqxma/Hb89uXBzQtbdhT7jbXUWTZ8OVrKbKu++O3tm1r8nkwjpHIzvFvacPjj0/vV/StO9oop7Lvbbnecf42iWxJSbXa5rG2qu5HF8ZOM+/p/KXGfpJ/m0vK2zi'
        b'wg81X+kwui7evO7TsaYvSc99vG6W/4qTtzpv9X36+8bFn/scvrK0S657LLLN5ilxksaGObpfX46NXvnWr4vfbd/k+LL93QaJdsS/3gz/8emr01eMag9Z2vrdx67uGzZ/'
        b'pjb17Jhy3TsNaevf+GRn4LO+MVfORm0T3fm4dmpsw86+bCMDtW893rX9OdA/Y1LTjz1TDN7eWBb36+v94b6HC7p0vk8enxLSXfF68enSZfHvxexffy9nDrg9P8/owIT3'
        b'P3Et91wVtijd85PvD3x3LKr+GxP7Rf/ukV2OeVdb1NH0UXiJx74jUXPNv3p38cTvqjr1Xw455RLorv/w2MKO6i8jbnXeu39vtuaPjQ6/aHy17PXMIyEybXoLGwxHqGFY'
        b'Aap2xgtXwkl286jeFU4yDUTdeD2Ub0+9QojHTHblodOKuVeBfnRS1d3XnUYOdCeuujXQEZGAiqYwfUd2ElnrJAqsgmo7otX5aXbKq2toQzlwhribP+Um4cTu4jAe+jYg'
        b'di2ND5y8We5wJmmlrVxuIxdzGkkCOmK8ld0ZXzSGYmboRo3cOucROzfUYMiuSisDzHGp9rgx4mDISeTxFjwyi3YkBs5BvrUd2r+UBDwRoJMPMDal9RmgY+jkoIEbJ04M'
        b'IPZtu2bRXq6C7KnWqAjOM6yIhNOUCugiPhyVESYyhZnu1KQG1yhDZ0fzmJM4PoppivpU0VH3lbYoLZTniAprDO4gOca26VqMjI4El9BxB1GkHPXKxv3fWss8+XJR5W/e'
        b'715XV2wMiQmK2hoSGU6veS8RuvtXjGb2cp5ipWeHP/4R35PqMX8P6tT4RV00Uelnm3nlNsTfSulVriH1OmGovDjW5fXJnZfIEH8yoz7I1akfcFVeLIipBwnq0Rv/WNDQ'
        b'qOo0RXyIT8RvTOfj1YWBC0PRdVHU1shhN7d/cXiInM9ODVJWr5oymOhfuJslPy8YP9mehfK4cAzvvRHnjoQbtUFsgLJUoQDKH3MOqz5wBBJrmGEoQ16J4xIi1Aedwor/'
        b'klNYBmR+5AqPoA5Uucfdgj75MpH4MMftECKE/xWiVHisfokXPWl1TQhEo3wpPmo1S6w0uURL/KXrFlRCGMvVlkpUoqWr3NeVbGy5hEtB6bN3SS2xlFIQlaD/hURB9EWm'
        b'Jl/eCXYNSfzxSoRl8WfB655uK0o7WJM5Laupoj23PcO8PG2GiIt9S/p+3XGZQGnFHDgG5zC5nI0F1Vzix0a6QBidtJYqi/w8DaniXBv2/YEHJTimPQDo+IOL5esaGzeF'
        b'b9wSRDkWuvUc/vrW28tZMhf9OycEEXfJQcTnwpDh17CSBzYCHzVsGwgjVrvW4GrXxJ+M1JW3xH9xtadyX2o/eb2TgjbAOeKzyN7L1hWLAkVQoAR+PGazRVBHnqhQCnlY'
        b'EqoPoK4oNVA1OoKlFQqQhIwN7jaoAdWTQDsFYk46VlDXd2Ws6WFbLLIVewlciomgh8k65DEfoX7MuazDqHgrnRXJA0FCw1BbkruHl5ftbqi0k3KqKwUFSh1H3yhV0yAI'
        b'IVUHlwspB2OWcQpy35VteNBXa1uciBOsNwTw3HZTymPnrWAOSB2SEiLAzI6LJkO8RSbhjLnz+ITkNK8Z25oYcQpyq/WJ2wJf/5c0E3/YLuJEEn5KWyyt7cIWZRHS/o03'
        b'3FU5BWFbM5Zu+KjjlkDwmxperFX901TIBtV1cLka9c0iR5Zvc3XFRtdbEoJE1r6/W0FY3NtLP7p16dtP8bsWnPGVLxXkSGttK/L110rS2ubH1f3ASW350m/NFWQU3rm+'
        b'z9ou8ZrcxqrJkthyGLSLPjmdRU8HCuA+M+b2GzqXbS7PacT7SYUXpuc8oPVar0h5qPsGWT2cLL6RftXq/6Wi5Q080laclVYM/Uo3e7HVv/Ix8VjPrXeyoK3z2diT7/j5'
        b'a/jTx1zWAXf6nRNMzN9//jX86i0ue9tRdi3RCl3QjPLlFE6ExdXUGVhKgnzBzXh0VNru7RLFWVxuyjyps49nzFtOml2R0y97fHBHJ+tSfc4Ms+Bnmld81pqfd9F/1UT/'
        b'mbb6GgcyDb1vm5t3fMRdlsyRv/XGttTrJVNrXHN/uPbh7VcKv3554bqxS6d/mCJOz7mst/uZBynNFq4xz592j1naMdeqeNz3+U0NoQ51P2+tld8sCZlxbcyL8nXeP78U'
        b'Y5471n/xFbWir6M/nOFtrCs59r7max+UffKuzw0IDn0mb/XZj0MdRS6HU8effiq5ZalNT/3Fq9/rjPkwdvu1U3uOzxn/78pIrWfdys77nPjsWsmd4Gf3dCYUVdZJk9ZP'
        b'Hrcsvjile1vJluA7rUHtK4+28M4vRx69XZzyb5sfPnx2xfH3F799+U7AnLbYmqzzxb88fWi11pV5Z24Fli6pcv29qfmtGcejV8z73b8q4wuPlrW79zxQTNlhteKN/obb'
        b'384e9Yr9qFeSj75qVOm/OuFU66bqlC9s8rbOcQ1/UTsxY2115dW8r/fW9Vw+7wA5sw88/HVFWNXbb77e3nb4p0zH3h0HNlwtv3G35b5GXNCLM9Zk3qnrdqh8r3N2+p3v'
        b'+ISIuJ9mXbtRk3tuzk37+76eKi95TvuiTP7Wyms6GyoVN6uW/fST2Hf78YSOOJku5evkO0TuMhGcImaIUk4aKVihxmAWOzHAmbBZqHAlFkHb5QR+WCTEevlQTjE8Fs4S'
        b'GxFPG44TW/lP43EJtcnM+ilrIUqjTJ0c7Z+FmgmwTBVqhD16Y1j4vi4L1KhISErSWgsN2lCoo4M6NOPwwYuOiqA6fB1tVgpcCBnkb3dGE/7WRIuF/iqy0kL5nnAKH8n+'
        b'AmTyK3DVB2mL/VIEazfIgGolRyn1EQzRUcxqUvfN0A99g7zmJFRCeE2oAWZDooFq1lq72ZIaJyhwnWoaApSI4CKzBboQjc7jV3fMkNkSSwtpsDAJsnUZK95ovwGzxVlQ'
        b'qwSWEFTJNlRLuV/FFFRJSs2Re3hJZOg4pwHtAqajtXZMBGiHA+i0u9yTjHEf6iRjvF4I344qmQkQNDsR8eAcah068CZ50GcOvpoEdQu9CSs9ZHje5uOeXoSS/1Ij/k/s'
        b'jkfwsENnID1ID/2dg3SqtoTGwaFcqjY/itdVeifTpfynWOm1jESjIdyqJvVfpkmNCkhO4u2MmIPrUk5XLBCzbzEz+6bvWVJvZyzSjCofrz3Im0qui7eFJGy6Lg4LSQi5'
        b'rhYZnhCUEJUQHf53uVVRvC4pU4/80hk8yUk9hn/7JP/K9MknObnssw9ewM7xwTNchRvlKYZL8w3lKHWjMIyRI20b5BOJQzWqcuYjRIPeBoS/7G3gDzlFMfe47xEZa6YY'
        b'HxppWIQjwHBypyg395Zw+tAtQulQqh/1ZUa/REFIhvqYqXeCPwv+Itgj5G7w7HB16qlkXKto21MvDPNTInqibcB1LTJrI9ee1d9Ze5vi9QfXg5jNHp3HP+bUhEcnmbzs'
        b'/7cn+bTun4snznDClA3eyImWL5iyTOK3QOv/dppFj00zcf7jaSumwQqyq75nMxgdERrmGqJKZtAB89/3RRF+JX9xDhX/3RxuiTd4dA51/2wOdUfOIXl5zd+ew+Y/mUMa'
        b'NBr6plh7PT6H6LDPFHRMErwNzj15Gsnd6D4ykfw+cYT4H0zkY5IlmcTHA06oe1Gu3gZO+LjbKDl6fDYVEK4+eiblen8aa7qtSPKTKrft5t7zCTdn0S9XOom4gimEwwzW'
        b'fME+nt0jq+/lhQR7Ec4ZsnfM4gCOYS9qNsMJXzjNkSsfDmoxK3kULkEDfeNNbymXGjeeXKdHL1jrwlHVkt4edNHXFh2ydpWLOOlagoZq5Elgi6jF98JEiiScZfIS8fgr'
        b'vVrCNN3MmxX31r+4cLnINcFprqoPlGmvl0783sXrUObYaKvntn9+f4uF32vfrHLwi4q2SegrC7HqSEjfmDbjVuK1RMsLL93816nLz5+a9EWw7x33j5O/mueou6u67p2X'
        b'J51+Y57KqIgHO57bvusTrX0vTPgwYvzD67UyVcaG9M5xsLa1JFqSnei0FCoFW9g/nh3rqRLoUrJOSrbJF47EWqJjzMi2ldxaUyULiZRMPFwUCKhvLmTqQRtDKCtQy7A7'
        b'uhaBhwPJdnMpG7Newx5a3ChsN5fn9FG9dI8wEfpRPeVGtkDuWsiZbz3itk0HFTNWJQeVo6PWrvTSTKyCpXLiQLiNGQ4vQJfWD7vEg33R5BYP7Yf8x/Ys3l1/dAgO7WRN'
        b'Qo23hUUEkXNVGFjJf3kjxxC7Qm1yuUTZAOagNN5w2OYma/q6+BHQ1GPNFOKNyDsbB9pFi3jqb2/xk/pP3uLEGGIFtKAiRqdd5VC0DB/MbIgnoEwxajBGRx+jpWrKv4qx'
        b'j8Q3KxWVapaqRAhhwn6e3isJQx6CIlTDRGHiTNUMPlAcLgmThEkzuTCVMNX9QqAUp9VoWp2mVXBag6Y1aVoVp7VoWpum1XBah6Z1aVodp/VoWp+mNXDagKYNaVoTp41o'
        b'ehRNa+H0aJo2pmltnB5D02NpWgenx9G0CU3rkhhsuFfjw0wzVQP1wiURXBQXrpfB1fOFfKAefkru0dQwjZsQZoZz6IeZU+o18bqKZ0gMMVP8xXZEJB0SjstsK3vEYo2N'
        b'jLSDuVJC2R8jrWoDtI+4lqRumKjlHR1iclqqDRJZ8V8issqYTr9k/MeATiNaPBTQ6Unhk8jOYRGcyCcSqCmEFeG93MUsIir6D2JBjVhlZL0/foVo6sVCBrWhwyiNEgIS'
        b'7mWlbYAS6gWnUY6NHc9B/9oVvMrsdeEUegYZ8XM1tsX54mcDGf1UySWGBnSSKMvKkLobzVQ1JyYyxX4qytmN8qEKapXxdHlo4fwSmVeC7VHWxEfJAXcsVx4cjJTbCPuZ'
        b'qcQ5dBIuWLt5Mqfq1jznD90GU0XoCMpbyQ6TLtQFFe7TUTlku+HdiM5wqBsdtaLXT/FQj6ow5bWw8OA5Ehh6/U56nqwchQ67Uw/8cMkOV6oRK6AKuAiFTP1+eqktyk/B'
        b'FJfYkaN8D5xDGx0TLYXWBcwvUKVpsvtTq+C0K26XHD/VmSRag9K304fei1E5EdTwIW+0jnQIunGHzi2lD+MgJwWLeFYod4KDvUDvTiDNE/Jpq2ygT4O5c4Iq1MhCnaOT'
        b'1iiHPh0LzXiq8hEezcG45Dwc8TGlhmKxoWHumF4XQi5zmmW/CC4oRxiV0GAVtVAyEGWe6FUKUAsb4V4oCBnwb4XPohplpHkjEuCeXqdBNLsL814Wa2PjH8kxE7tLcgff'
        b'+YjYvZlz5qOn0bM7NZr65jF7evx2j7MWEZyS8ddB3V7DXVmhc5ChdGc1V+JO3/xtFLsPdFKJ1Px5/GrGJ6Ca0ajHXbFrMGI8DxfQSVSQqIQeFUG6NWSGjgxWLwpF2egk'
        b'XXgTxsMx6mBrEewb8K/lj9oondbVRT2PBy1W+r4KWBGh68pMPtoc8eBcXIbXCpVZ8Jxpo+Oi9dGTot5KOyhW4AObKzmhnlLc64McdJ23f+r5yZyvuyX9B3WO15+si6uT'
        b'30yHy96XtWJKBYtjwbN3T23Zv+MKFxVw/6u7X3yx4+7lLWfG+p/ua30G5Iu/3H0mc9TFr76pN9ro3HJcp3djaPszo7/PfUfr7Y8+2rZ3csvSV9I8NX86+9nPi7ZMf9Vs'
        b'/tunuy7afeaXEPS909lR1T+/5He95q5m3YTli/MW5e+xibHsNRg3/eTrYxLX1KEZAV8n3f1mzJqFO7dtmmrxZlPaxY8VFjFX7T3CRn/5bup6402RSVGrq5vLXnh3fX9o'
        b'9bqG9T5XqtUVp0adcqw9FPftxwGFX9ucfK6y/+OysNanmnr8UOzn+7ozbySh6nGi8RM7L299quZK1reHZJdfW+sf6yH3aGqef3Xi5dpy52LnoNK5d/otP1eZsv5EfVBp'
        b'cv1vsyvuBGy2+6Fkuk6vh/zD0nCL++G/2TdktX/DZfyuItp7+AH6TcaCnqPTM2ZYo1IdJYNCuJMIdIpyPbs5d3cPKztXmyACCuI4jWgB1UOdMji4byjaT5H9hCtqhhbC'
        b'dKF8ISVgF2O4KvBOL6KhTjxjRo+IdLJiC0O55HuibiXybkB7ACV+QwqENGUsCJRtBaehWpPoiyhlIyzyhnUMUlaM91ghPv0ZcYOKSEJmFAKqNDNhCs0Csa37SpQZasv0'
        b'mXjL97MbsZwAElXLHtM8/F3BAN0bhY6K5+E+KWNlHEOnFkM+NED/yumY7Imi+QAJ6qGcnTYqRaXw/4h7D7gsz6t//Hl42CB7g4ILQZaCA1AQRdlDQRSc7CUCsgUVENl7'
        b'T0GmDNlDpjTntE36NklHkjZJR9q0bzrSJl1p07dJ8z/XfT8gKJrE/vr5y0cFnvu+5hnfM65zlbrgnC91zu466xBC1YEYHo7W4TxMQmn8YfENJPz1I3Avi7/CogrzJbj4'
        b'1xrZhyOSagdF0OmEeZxPTwlmrkKp72Px52WoliWCh3jHhO+jz8qfu+OCyUACv2zmp2jmmvp8CYRlrGeXifhyctAmhRZWYacE3sOGK9zcNKOUXOD+2qt5JCyw6xi/rJM2'
        b'WAylsVDj+7gkn0BZTpQic4ajjUvxOKOKuVz3nNSQlpXQhWVY4l63j77OtuSxwMD7V9WwV4S5bvu4BzzIsmjlTqQRw09zZ8gUiHhIo/QG8QcTGwgl50CpLUz7iivvCZSc'
        b'RS72LinsYjasPwC5vIm3RrjMYMdjAeOUKqOaKMc7R6uCoAtKlWhTKlc1p1KUyN5ena+sUYR9cJ+/LGZF/OyHh2q2Ilg8Dw3ciOVIry4wlOm+CjVTw9WURNBnamIq9WwH'
        b'ldyLnrxgIVcOxs8yaPFVYXy2QF6eK+LAH0SSFfLePXYgiLv1mvtitV/Z8SB5CQmC+dJC6c+lZTS4w0Hy3M0Hq7/nv/5PWlaFi1Z/3XfkhZkqYij55OUG4qNFyut9BbJf'
        b'2QEqwb9qtW65Er+2mVFj8OzDRE8N/avXUNd8XsH411bSsB73sHp5wTbu0gAxYH1cRP/FbyswFb4rczk5Jir+OfcHfH9lQHz3K/cHsLdCUlKTXrwuueTlUOvQZ3b7xmq3'
        b'Ji5xIVFGMZFGMSn8ZaXHrI+trsKLlcy/JHjODvxotWcDrv53UkR4TEpC0gvd0sD19sHz9vud1d62iHvjr2V4sdmJ72aQu3w1ITwmMuY52/rT1X53cbX6Q5JTjPiXwv6T'
        b'AUSuDCAiIyIs9Xn3Ury3OoAdqwPgX/qPpy/Dn5N7dt/vr/a9e4W4UtawFlEZ38B/MILwiFAimmeO4H9XR2DIcRX39H98wYDc5RVqfWbHv13teOs66n7hrqNWul7xLj2z'
        b'6w9Xu9651opmK79iQq/vfk3vnLJ7MrdGuJpbIygS5AluCjPVbgg454CQcwgIbgn913z/LA8sa/ppV7rsc3J7XrBW/IprInDDi4s5SkyPjuBud06JZtdoP6bHpAj+Mgru'
        b'duX4hJSnfQ1P+RtWNu2pCMFW2Twhdz1AmJHTh8GvPL4cYEA4HSNjKuQwqBEO4jBh0EJ4YLXG8OcB8H2sfUad+hsrR6IZEXwNXJItkMk0XFF4q5N9nLUTGRWR4vPsAves'
        b'24+Zfmfq7yvr9xxB7bML3ac6UEtYm3INJ8WoEOsfu0Cw+nF+Dtk37XyODl/eY0laAZagRPRfCwZteBPE09lhtNURf0rng0GvCIUsGBQb+YfgMvdPosThIMG2N0V4qJy2'
        b'nDuqMoVtTrzNswUq1+/4ndAvCxYl3XrhrVd4/tYnR6Tw3eQIn0gYyxWu7fzvL0AAZc8JFrFdglw5spS+jALg0RWeAMjoYASwWwGL4xXFNxHDGNwz8vSUhmpGHZLKQrhv'
        b'yt9LsAMWyB4xMwpmb0naCKnBe9Ae82aaqlSyNX3uIn/xSpRbWOlVrxCvkNhf9kdER0VHeYV5hPiECP+ic0UnVsc/8Dd7pGwSIwWCsbuyP35D9qmcuo3z65IixATDdfO1'
        b'9kqkKKMkkan61H7xjec9uUPru/zoBXao7tkZdBsM49kym4vc8VX+BauRu68juSNJcns/JXadWTphMo8gSE6v9yknGyWnxMTFGaWFxMWEf4l7WCjYSAtJ+5x24Xxz7+hn'
        b'CmSFRgpyAqO0tyUy7WJe9TMRJl+mT5Regg+DXw81+cAjRDHyt8G/aXo91FxNVON1ws/UK9gxeVyrKtz0h7f/EiTv5TQYq2vfFKtjr9PaXHI4VkdrzDJcULLHPPj8KyfR'
        b'6KWqb7VD22t+GjI/FFk32mwW/PA3Ok66aaay/I2c2LzFjJm3XnvEBq4SzIhcoXgr97GrCOewAAbFbuRVF3LHZs6bcCMizs9R7I9d8cZmw13OF+RFb46tdS6rw6MM5lyG'
        b'Cmzh3AnaSdaezM+BVdj92NUrhVX8dZDtEkGe7lk4snrXhMVB3nmVi4X7zRy2EY+6wwNJgXScxLaQo9x4DK/TIN2hllWXM5cWSBoIYeIkFoj12ZdG02Rjki9ze8rx0PGv'
        b'y0PqfI1E7i9L/uZqfkiusSlXml+j8Z4xpscq0JIe/dcL8Ffhs2NpGwzIVH2jUhlramJwob1wtkgiZt5xV7F/wUpkyK6YJO/KrtgG70rzMPtdaR7/viu7AkfflV1FkxEr'
        b'k+Nl239+2+QamaTF6h6wNWMDlpWQFCkKDc7/t6pUKCmoSPCnewe8MI/TKTB1inc3yUMFK6qcB/ef0utq4v+TC54MTErX6dQJwiXKWahOpnBToVqheqTUVw9I8m8RAFEI'
        b'V7wjywKSXAhQVhwClGXth28qF3Ip9QrUtmS4Urgy17bc6mdSBIJVwlW538pzI9IJVyuXCN/BvaPGvaURrnlHjj5XoM8F7Ik6GfrSCdcqlw7fydXbkBJfuLKpUKlQpVC1'
        b'UL1QJ1IxXDdcj3tPkW+XvmTr5Gi8+uWicGMuECvFRQnZRUJKhcqst0KNQs1CrUJtel8l3CB8M/f+JvH73Nt1MuFb6P1dXJ/sTWXuLS16Q44LdbI3lLj5bWXzoxlIhG8L'
        b'387NUDlcnYPwJu8qiTmD/guJikj65T7anHXy/ajR+ieYUqD/k41CSB+s1RIsFhmSYhSSxFw611JjiAPWNRRJgJ97Ppw+CkthpmJMilFKUkh8ckgYs5WTnwhZuqeQ1klI'
        b'Ene12ktI8qqVReoq3ijEKComLSJe3GxC0vUnmrG0NEoPSWI3stnbPx0TZQbcExNc1XbHTpw+aml0PCF+V4pRanIEN4PEpITwVG64W9dHhcWuumhav6fOdqwvzLJalIVt'
        b'/WphFlGR6Cud6hBr8F+ee3KjuCV7IjK8osCvrkzthYLDqyvLrDra3rXbsaH5xmiA27pwSyN3zt8VnkAjInPPKCIjJjmF/SadrXCo2FEUsQGoEA9IbM/zY3rKyk+PYYOk'
        b'TyJTqbmQ8HAil2eMKT6c/hqFJCYmxMRTh2v9YV+CaNh2Ph3w3uTDWVYwinnaa8unuq2617EGy724Iqd+bl4+XIQBZrPMWAwcCxWwNz00lXl2WdKO3sYt0Hvu9vCADwyk'
        b'YaHczWT+jiQbY+jHWughwOFj4SYpkNolxCZYEheVyXWGVjPsiSK6yxBkwLQ4eKsQjA3+FtiHE9hrLRBl4X1LgfJhiR0JMMDVjE1Uhe7H13/BnSPsrA0L5PM3fx00lWKX'
        b'xkxxtUEgB2t2mCXtl2CXniTDyHkO3MlkiQOvacmKC/LGAq6ybbLkLk9LXIDh1VlhEXe3WLk5VnjzBeZOJchgjuNh/qawcW2YgjaoTr7GaitWCqAEqm/EBCZ1CZN/Rp+/'
        b'1BfgXeUQL7FXJf+9T2UCa/5ktrXKr+cVYU3rcQ/VXo9f/Y9b6TdMl7wbQvtrtr9tUJKXeLvsYucPyj74Xfkj3dZfqhq/9+v++4ahGZpbTgwMlv34O7t3jb2WMjH9MO7u'
        b'64POAXnvS0bWFvRuH6tI7Du77Lv5hMf2qPxCzZJ/CGW2/+AK/Pv/SlQuO+133Hn+crF33TuJDZ/Dpc6ffv9RwO9P9n+v3v51t/Saf+jGTx29H/+dP3q90ng+ac5ocNjx'
        b'Qv67b54N2nLD4bjb3cQBf+Mzt/7uujDt9b03oHzyswJbz8L0fS9nf3Hz+Ft1jqYaXI56aITAkwu34UPMZ6kG2A+POOP2JvZAAR9wTLXYLQHTjyOO0KTFgUJ188ueXidg'
        b'SRxQ4uL+0djLNaylnoizumZr4qDb8R4X+oFZ6Ic5Ty9sTGDR0NVQKPZiAx9fmiS6rdaEgjW5XCyRC0bTOOgcDpVY6snneZhKCwTmchoS0EnNznHwWBWGkrCUwIIPI4Pd'
        b'8nhPmqD3FCtdCnxdw+BtMGGGJZBjhSUMTEhDv4Q53sZaLhAplZ2yEoilz4R8GBbHnXns3KQPTdaWhL5pzSS3CuGuZyB/YvU2dm42k7OxXJNCT3h6iK/U32qO7eLQIDOB'
        b'sSwtxdNCWqANM5Ju5oHcYp7GfksoPWgsNhak1SU24RAs8PHNWW1WIdDXxxMqSQ70+IoHpwqNIqi0UOIDlAVQtpUeEksAM1xMEAqU/EXePru4qpUnyUB4QC+ys7qs1leF'
        b'GyxCvzdWQIWVpwVXtZKVx3CFcRmolE/ndvHa0bTUMPH1HOLMDa3L3Boqn5Znt9JxdR/Tzq1Wfrykzl3LQTMd92HZ3Sy1g+uqGKfYaSyBFjWzrI7LT6e6fZUE9Y0CeqeZ'
        b'6Pw61oQdS6KX5lLxlbi0ekXhHvY9WRbWnG3BB90ytdfr62dcKL6qjdcE3p4TwBTxz24QbtNXEOd0fQ1bJEfwm2efD33mBL6Oh1zq+S7qwwpiF/VTna0G4WxWlfzTWn2N'
        b'Bv9P7hBPfl7A6MjKEJNMWTrdWoW7zkfO+Ri5fMVVH+PX8ZLf+f/VSx5F5m6W8InprazbU15OpZ4YEefQLrTsWnFoC37K33d7dthUyJ1HzYSWI2tZWMy+TlBHHAw1WP0l'
        b'Hu2km+zmVeMnyCI5LO4yd6L0a7mqnV+IN5af46xmjWGXD5Q89lVOMwOzFsc9vXwtsMZs7cSx4cnTpZznWmeLksNmuPMl2e+cB61Q+ELZ709R1QplPXlahcOIdlAnsU7C'
        b'09BZumOx124Pcxg8zWc+sl/4erl7Qz4+FLIbF4sV7LDDNiZs90OpZCaT2l/764fBlmq/D3411ERrd4hXSFxkXOgf3vwk+LfB8ZF/CC6J8gjhQyAN8rKq1VKmohSWYmmP'
        b'ZXFPdg4V0G31tHaRUE5h1SdJjy+mrqQsDULT04eeZ7GGLwTcuAO7GDFGw90n6JGIcSfWraRBPF9nrHjck7K/Kmmud6U/5czPXedP934hKp1+Tm72CWrLEzvV1xMpVup9'
        b'JRrlnOs6x5TcVU+bSnD5lrbYBg2enqZeq5519WS+XmM9dGzzNLN0XvWs20bExGr0CZL3Cdg15/HMr+4V4jX351W/elyUR5gP51nXXeNZnxEIvuUmd/O21dOe9eeEQm4L'
        b'X9S9flZRXkUyU+dZW7nGy/4l3R97oc37xrPDIc8eFMlMxtPPFhtOAs71zsSGFAkOqVXBIfrKGd3M+d73lLnpGpFCdrZY4a51qjzbUL+aFBHJG8VPJdJsYEsnRaSkJsUn'
        b'2xsdXb3vXbwKwUYJobFk3n+JDbyx1pTySWWqAceITmc5cM+YIeDkWYszZ5/I/ob7xuIE8Jx9crEykMfZvvtgEO57PmExrzcNsdrQT0GGTOd+7Iz5aKxZlOxLLzZLfPxh'
        b'8B+Cfx/8ndDoyMGI3wa/Hhr4jUAcqxoP7L1jKmWy/dvff/Xtb7790klRzxXig8mm3NigiabJ5tKTjm0egf5NThP7y15SbNMV1FqoXv97uKk0h6sVYChkM+SsNY/snflU'
        b'wTbjC6vmB+TAtDgPFKdxjK8W3kG2TuOqYbZilUGBjaTs5UC+YM9DyHPyvcUbdsyog0WSo5yNMLmJLJYVC0HIaro2KJyTwJETQu4GBZIhzfpQkPBEHumqQE7AxnUs/Wyg'
        b'u7Y2BTtKIyYejsntvy6TJ/LpdrJc4ZZMvSf4ak3zPIwYEKfDca71x6h8Q+0wIME/9hiLH6YmTr+QMBjReLYweM6gny0Hnkrb+KrQYSVxYnpDCZDydAJNQuTK4Yz/vkA4'
        b'yvf5FQXCxmE+ArG5CrtEycy6/v5L//gw+MI3vv8SMWVDZ8HW0r1NuaY/t9kssALJLGUdUwkOQkAp3IY57ozT47RVbxgU6OFdyUyYO8eZtRJaZ/iDDjiGBatHHS7g4kqk'
        b'a+NY7fYX1l/ZApbXuRF1iLdGjIwdJFaQsaPE2l7DX4hS258TI37OWEx5ZnlXJjkkLeJySLLPsz3QzKIVKzBpzqaSfgH/c7Sp5C9DN/I/r1Axc9CHiwvUfyUaProaTIhI'
        b'CWFJcyF8stDVhDTSiKyk/Eq7/68YgH9HvGD2zE3NhRHMmW/6ampyCvNN8wyZnBITz6cSMmt5Q+cyb0GvSwBjUQRqfCPH9irvsbEmhaTzy0Vz/hKWY8T9tB9a3ieVq5Je'
        b'hPOp61QwNJ94SguvUcH7YviaOkXuMH1jjxk77eQmwHoY386VhXlg9glfT0ZScMFHslmYcteMc/Fq7RbXsjmjFt1y5qLgNF9rkb2y+0QENEGZmS815SfAlnjIifnTqU5R'
        b'cjt9aPlZWUS5mZLEUZXjQwtR6XnOf37DQPBRrrOKWviQpqzWO2E6bu/+xO1afvP5e3a6aH9sd0DX7oHfJP6lz/V92cYtzYr5BZ/U17dFuqVsj8pLev8322pONdx+Rcbk'
        b'WIAaXJ//1thPclw2D5Unn/zByU+/Wd3d9GuX1mOnpl4bfuvEn3+x81H5+HcWHTNnF5f60uqn9NzvXtsKhh9+8t13w5K+EER8slv0+X5TWc7Z54/5B7Ebq9cCAMyR5t2f'
        b'ddjus8YD6QIDHAKAAf5+Gr1r3lCT+hQAkJTlbrvl0UWpKrU+uMZLKc1X5LPJgmaz3StnFG5dlTskAR1G2MsbWYXn4P4laF3nqFx1U+KIEw8hqmE5Ee9C7hPe2b1Qz3UR'
        b'd1kfp6iRtb5VKIORjdWvqfRXdfi9KyM+kcvJWbevL2dVVupoGEuocBd3yHIJBSbCTK0NJB51tN7Px6EEJ4kvRxRkaDx+do2Lj35MeCFhXav1bGH9jKHTsnJuRk5ay62m'
        b'nvO5AUQvgncl40Lio067hMms4Xs2MbUVvj/HBDg7VcpcYvJc5JdFmyUKlQtVCkWFquLgolqkmliwyxTJkWCXJcEuwwl2WU6Yy9yS9V/z/WN31S9vSW4g2I+Gh7OM9fiI'
        b'9PWZQSyqxkfw+IBjWEJSUkRyYkJ8eEx81HMOlJK4tQ9JSUmyD161voI5kckUSIJRcPDppNSI4GBzca58WkQSl3LBhZifaizkmSFlo7CQeCbIkxJYmsZKkm5KSBLth1Fo'
        b'SPyVZ2uTdXHHJ1DZhlHHZ+qY5+klthAsLJqcGBHGzdCcX+UNtczjkxLxqVdDI5K+cgx1ldD4YTw+8pAeHRMWvU7dcTOKD7kaseEIEvj88pV1iE6ICyfiXqM8n8g+vxqS'
        b'dOWJNIDVTUs24g9sWBr5skzh9JhkfgSEAKITwo3sI1Pjw4g86JkVQB68YUMrow8LiYujPQ6NiEwQ6+LVQ9w8EaSyRHgWww/ZsJ21NPTMlVzNz7M3evI0x+PM5pV+n5Xh'
        b'LG4r1Dr06VbWngn5kveZpCDg4u9rdMDGzmIv93MqSRtiwvCIla1aaYtIn6eSjROuj0dEhqTGpSSvsMhqWxvu+K5kI+5Hlmvx1ODWoRsxZbKpJJKRQd99BWy2DvQoiwXf'
        b'etCzy4c/kX0RCpOtfVxJIwgTyL4+BPf4Y9y3sQ0WFdJOYsc1EspYRPY7LkOLqZDLZNW5AV1mPjgUihVkiEOF0DkBHqYyG0GI8zIKaddOYdFFSQaZTCwtTLDIare7N6Gn'
        b'wdOJOJFyho+GQ91uOVvoz+BC3E44c2NdBJ+zVbjwvamsFxeFDbskC51CqOFAVNLuTYILGvsFrJh5inomHyeXIv2cw8CF2UqhSz4H0dzUAheh2UNK4GAmjS2whOXcLBIw'
        b'n/l0a6ShKUYgVBVA+zYo55q/pCQtaEsw5Kqe7IkIFhdP2SopqDqlKmA1yMOdxdXKFeMkBN9QZ98Fx9mmbeZxHFbjVDR2SzDE0i6if6r8uEJc3Bs2unKCOI8d9EKw+b/c'
        b'pASpLFvO9rQbllp4ePu7cX5mdxp/mRlDnatzoQ/czD1gOdTL0t1it7QAS00Vr22L4d1HC342TzmPykw98E64txcMnHZbjSkTupmTg26owAIXU1nuWDZOywvFkdADkCcO'
        b'hmZr85dnNMACjHhiyVVYEB9kx6m93Gs3JfEBlnJnKFkEmz/GfmALRz160GMiPsN+w9R05QT7fv5FS6w+5MmfBk3CXPEx8nonvsT9pOdVM+486A28veYMebafeKhYywod'
        b'm3p48wfILbZAk/4NrpS/SZzSmgPkAZHrj5BHBtqaKvDJEWUXBNxSi84F87UPiGbK+N7nr51Yn7aKI9CQhdMX+Qr9D7Y7c9mpurCwkqDKlT6YU+ZaltwJtZ7WcDthte4B'
        b'NGAzRxC+N7GC5hy0S+y3ksNxbkImMA9tXOWDzCT3lcIHqVu55MC4G9DKFaGh3af9ql9T+OB0CD/eeqjaxuXDWsrqPi588BDyeB5eMoU761NtjzpkmfJ3n3hADszwfkNs'
        b'gpI1Z+mj5bjGj2CZIe8xEHsLHHEWcmEG+JHbmQArAdTnZyENk9AoEEUID0GlMT+uYk2Y8SejqSqAzJm7J9nVfhZCaL90hitgYH9OUmDko834SFE+dJOAW7xUWmp2kUvt'
        b'4Ru+kgIJRQEuW2K7qTx/TUO3CIaTlZJScVwRx3EOq5ShBB+m0AbEitwjYDF1B3uqD2stV59S9nRkzyTjVKqUQA/7RHgX74i4uk966pGPH4OS9JRrckmblKTPHBSYiCSJ'
        b'7kqgmS+U4EkkPpmKU8nXFK8pEtYvV05KFQnUDUQHcWlTqrmY0xOTr6XKU2MXqS1lnKa9pT4VrxEBins/cklaajPc5+qGkRitwhb+DXr+0OaVh9QjREe3wW3+HpAWqJBc'
        b'fWZlfFAsI9gCI5LG8AhyucaIcVqha/XBU2a0Jkk4RUM8IbKPxn6+xxrsx1x6SGOPuD2SwdICFWmibszDJo7YDI2xWAFnUthoclQV5TYRtt90S4ILvPRw9S4iYSCN9vTk'
        b'ySMX2YZK4ZwQqrEGRvkLUOo8oNHfG6v9sRwGM7HeH8pZLdIWIc7AQ2/+ApS5W1gv7gTmTq3pBDqxi6MCewe4nYwzyklSYdAgkMA+4W4/qOLMc6yGIZKRJBk9rby9fAOY'
        b'EvHjzHJT21Nu5kxKlrl7YQmJDLgdIEeLepNjvcw07PDEchF0mgqE9jRQUxVuxEpHWFVHNxIZnliXakFM5iMpUIU2ETHtMs5yorpUQ09gbhkrEKgEG7hkHeLl9yVjM8Fh'
        b'lQfsl8ekju0V8JdvCD49Iv7GxMlUkr/KbAJKNGGIvruOCzvpn0Gc565uMr2IuTBEqjjTDEsEmY7Qw9/o9AhL9rB7IzKwkgRqhrk6N4EgfUmurkcMcV8//dsB5TEY/R1B'
        b'8k3SL59p1F7182SXJwx/pPuTv06//M+3mz878oGy3yv2Cj+KCzLqMfdU9drxXT2ZHV1b5CKcYq0kHJ20bPxez7GVUvimqq1w1y9SK/Pu3HHxvxjwcWpq+ltvLJX9ZbuF'
        b'jfAn3+n581RtwkRT3GT4bzx8Kl/fnOZ9y6l3VuNPP/2dza/PHfBo+nnJZ8dl7E2lHn7P5IjwR+OBkmUfbPs4tjMrqHTJ79acidupt0YGfv+Lf8TuvqNUF3zkxCfHfv/o'
        b'7/HblQrG6kfDLbw+evsPirYP8vdceuWUpump0hMGP97h9nKA9q1R49qb7l6Wj36ous+n/Yd/+8dW2w+y8jvCJjtEH92qMf100s11vrfbr81u9hPZj3/7TvpU9ccR7qYK'
        b'ri8H+X1S76+wpz2v+rfRP9B+eA6uXEhUDx6tP2/xq3yz/fZ7vtOUcvZQ/0TLphyjnwQaf/STP3z/XMgfW6YHpj/8UXzgQswftawuZjXB91/3uG3xUn2wx592BE788k9/'
        b'SQ2caik5sfDOoca575qVj757P8nJ6Zj+wm+zC8+2TgYUypjq/jTjZcmKKUVlxbb7i8uzUX/+IOLqoVqf8ndaz7/6v79OuYb7SzOmZ5fsxpQP/7qptvDHI3ng+r3wW2g6'
        b'P/Hah8E7Z2a+p9/vvVMzN+0bn/5P5HsHf25+7I/b/937eez9vubRz/96UbPvbz6v3v0pXpiZeu/ViMPWu7q+96j5L1+8vehw/pt682bbNHWvtuz/yaHeg7PfKv/UXEXm'
        b'rUclGYXpdiM/23bmaJqg/OOQzX/+eVVGh3JGylu39fJ+X1Fi5zUsr/qzt34ACz9+NUz1Z2ctfhUU4LBncPf8j7L750822Xx+PXc2M3xb9wd/fqX3ry8n/+bzSpdvfZG4'
        b'fPnYW2HXo3/vuHc6x9XqlS8+lRG4fX6+JtzUkgvc7IdBC3HAdqtwJX6t5i6Ce+yCFL4+xhjUx7CCODnYL8YRhEQGuBwwAxg9LK5pDXU4BBW+WELPqGKhCMqwcCdfJmQS'
        b'b6cz15Ao8AnnENaJL08YS4IhrlyPwrbVpD3iswE+uNTvqy/OM9NLX59lBl22nH/nJD7COs6zRPK1iPcu4SRWcSdILt4IM+Mz4PbhrDgJ7mEyN35zeBjPPEtx2LSBc6nJ'
        b'nc8NXMBc18e14XCUWJkVh8Mc4G/D3hmMhWY+3lgurXBOILlPCAMwLsONywrztomdTtDrv+p3yudvMr6NIyqrDqubcrzLCu9lrdSwncZuT4KKrDTuNhjhq+PmYT//8kN7'
        b'LPE0gxEasDTchm6B9HWJHWYr902XSGDhSqnglTrBOAd5t07BtLj0rhzc4T19tHN3eG+fAn9KCBY2n3mcyiinIYGPoB46ocSIW880wjZVXFF6MysZsiC6hAHnsZNbCbfN'
        b'0MLFMK5I8od4SE3l8scS78HAZiw1ZxV5S33P0Jp4mxMEsBIREJrfwfsYWx0T+TAgjNtwEI2LAuIC7SMTpsFnoZ2IzdFmJYDYnsqX36tPOCUGwVAYJAbBwfCAG+wF7GAX'
        b'yHNo0luZR7rWcfy+lrPMEDHWxebwVbCLswf5NR6CotNiuItDbjzchfu4xH0qktbg4e61gDVoF6r4yitaicxnuQp2Ywm3N8VgExfQlMKKTWvwLo7seALwHvTnFmQX5KSy'
        b'NsyytbhHqQvMESVANUxwExdtJ7ItJZDnayGBBTDLqHI3tKmksJsDoBmqhWIEFI1dDNMoX8PpTTgmJJwrNMcuKTkYxEdcT3Z4DwaJXsTbIostNOJRKIF7m/jqKTVHYFpc'
        b'ORGKPWDJyp27mlvfRRLuZktwo1HDAk+uMuN+Yh6BDHZKOHvJYm1gCsuYlk+HIl5tGpDdkHksgiNTK1w+wld4IRw/x1eyJTS1XYQVscZcxxp424N/wtL7AsHhEsLw1C02'
        b'SUIb1Bnxiaz1hOSW6SlbmCI5Zk54gPZFQqC9X/JIKE5zuZ9GJ7FktVyorMaagqFctVBbGOVFTRkMwhRXQrLE05YVyKJFV4ByCey8BePctidjkYhzhBebS2AvzAmkfSQM'
        b'SFhO8gtVjf32K4m+DTSuYvPd4kxf7BIXzJbDdiWcVE6z2G18g5OFcjggAcMKenzObjUObqWdsDA1YaQTJSHjSduNHabK//mZqcfu4P/iJd1rg+wh4eHrgux/YSDr63nI'
        b'D7D7VJS41FgNvs4Nq24j3MJVo5YVmgvVJJRW02ZlJSSEWswhLU6Xpe+evMHlU0kFSeG6r08l/yBtKMu1x9/dwru2ZemvIldbR5Jd0f13aUVpIauErcKNRUmoJKEmVOK8'
        b'9bJcxR09rlKOEpe6qyRklXKUuNSADSKpa5ZF7M+X453yq/7xJGfmqF/1jCcdX+/j/8+qkcvw/TxumOuR72y1by4+4EbflSiI72X5WvGBHMGnll89nLtmQUxF78quRE8f'
        b'n0MMkxQ8/iMtWOMVuyAQ8GeK+LCAnDgsIOQCAywsIFGoWqhWKCpUj1QXBwUki6TzBDelMtVYbPes4IYUFwiQvCXlv+b7NdFef4kNggIBieJk4fUxAc47HiL27q6GgZ/t'
        b'aV95Yv2xoxSxo3pNE+Zif3VYSPyGTsxQFo8w4q45Yg7HZ0cfXsQxz0IdG/a6e2V4u424o0WcD3VlHLxHnB8SC2/Q0ON5L/TGTnEj54TwCBs7o9CQJM6Ly084KSIxKSI5'
        b'gmv764W3uQUUxzCeLHi0UfCBmt+4IIfYtb3i2Ge+9C/z/X5dT+/GVxMZ8ilmUjCDDxJjSS/5im9CP7VRlpk4vl1hKoejaodTWZJkFo7LrfWqujEnIxb5+j92r3pICcjO'
        b'r8rE+3IEQ5YIVXFu0AIo0ODj4mqxpGKVgTerTQLl2d0xGb/eEmyuJmvA3x3TckZBfHfMmbf/KRS858TliEKtFI0U+hmuLsJKf+YR9fbiFO/Zp/J/3cw9oTZyjSNAFLAJ'
        b'+wyTufNWzrBMMHZSKJciEHgLvF2T+dP037L+l+AV422Sgj3BEW+7JV7jjfi3m51Ocx/7B50T/DprXigIzonN0Bz04D926XLivdBnY4VvSgiM3jMO1t9qJS/gOrqBs7hg'
        b'I7nVUyCwFlibwSNuIjhCsDtnrYsbiyw8vLGWOXYJPLqfEs+BuwTjlJtHloe5h7go3kOs3OSBJbDAbQfWqzLHIO/tZTfAb5wuuCZRITJEXPkT71/GJk9CeptXi/6vlPy/'
        b'iR18hc07ZjtWfKDY7SE+vU/wt4Nz74dEZ6x0jT3QsdbZzHmaTVbdp5ALj+RuHrXhFuqHydyxNicUBit+FKIt9pk4xfLLmHb8jMA8O04ocMrJ1LG4FZQkzZQHc5ibSvHn'
        b'8YpvEnkNCRzJghFcF1zXhTJuqU2M8A4hwv30aKYgMxnG+aersBCKzWQgL507vmcATeJ7OROhHUsFMEy/jxHEnMJZvr7sBLYDK8lK+BhLpQWSB6AQWoQwGk0NMmR7hX6e'
        b'9LSUxuUnyo4KVbk4ghWzMEpXqrnuMSDzIDM7Rks5UTJ5mJTkVU1/h+rlijecVL4d9eMPj+gfym77br5CoYrm/hSN02e32ctL2p8qN1EzzU/+37g8U2M1mX/IflhR8ptf'
        b'6mbIP9q/9VxQy91//vHVgx3TP/fb93vp5Nn5ybJo76V/hk45HD6rP5lb8cdbA/Uz83+4+g8P/atZyXEvexW8qn+121Pjo+3LyT/blTIR1lhsL/3Jr2KMOptsPkh8NPnS'
        b'olrHLuPCN6IK/l7amPLp32+/muH4C/W/BislvGVw6+eaF8ruepnX/k/wt75d8t3sH/zovXerpF4OeGVnWOU72VMaL6t/ZyQm3/vkX7f+Si/15dded2gaEVb/+fRPi1+Z'
        b'FdYXGbwV9dvKH7/v+JN9zg51P/3t6bHvDTv830k34e+lT782Odn+z+bPi36m3R1qqP/p+/vPjk5afHKgzn7e4qSy39GZ3/ve0vZLeu27WaXlg7/ofb90U8gPrU4O2bz1'
        b'7d85Dfw982/9/xoutfUvrPhR1eu9dYOuU1+MvOm/J/T9Nqs3dH9hM4rHjd8/U/dTuek3P5OteDv+tbO/M9bdnShV947lN/vSf3Hl53/61b+2fV7/donhqzoWn2SnCB1+'
        b'rP/+Ln37iDN+d7u+O2VW98/0Xy//W2rfvuYJjzRT/gQg1MZD5WoSS2YcS2PpgXsc9jaCtpsrpi32K3DWLVm2BZacRbjrxEo501SVM2sdFRFkgnKFg7PZrcZ8JQoivHqu'
        b'GgVZ6uOc9ZukjbN8JQBJSewNJvMXqsQH8cbI3lrJfKH+KoVwF2qhiztxgEPYjT2r2a1YrfdEgiuJzAWuAw9Dj9U7L90kA1ipmSZNPkN3CCp0uCsvyWipXnPt5S54xI9g'
        b'OBiLVi/+CYcaFyEsRoqrryoE4Zz4kh6PBCnxJT2Gcrx13aKWZkaDYTdeYjd9tlkCqszxPmdd33DCYb5YP+mLSgFXrd/UkLOEQvZxtWNpSK3Y5rtqWvIW/6NbfNpOWYIS'
        b'G3R+kBX0e4k9O8oHRBf0VPjM39uwgPkwYMuZbljpTWKV1IeZtEAfWsnyxAFjfow18PAQe51dNAg9OCKQNpCQvBbFuxWKHezp/Yhja+QmZ2La7ud8QHuuklE/G7piZa4z'
        b'MWljKrnZ3FTBbu4JX3NcxO61JiY+guoUY9ZRz2Uo4h6CWRh84l4Kzsykvanj1i0KWwPENl6cJmflwYSj8n8I69X/izbdE4ad4trMBM6yG2RK4etZdtkCS0XOwpIX34Ep'
        b'K74f05y7b4h+I6JPJCQ5+0qSe47/n91SxG4oYpVK5TlrbMX+U+GsL0Xu/iJ2zoq3z+S5f7W4ftS4fzP1nzwGsWY+YpNMmjeG3FcNJGaHrLHBVP5fr6+p5JrOrFZ75Awx'
        b'H2aCEEZM9mLr/PUMMTLF9jzbFHveSqxkje1lw7KW2MAMY7CVg6w+Ai4rXIoML77uvwRniomYMRapuGp4SX4tw+voRmm2K4bX4+L/q1mzXLLt/+Nccf6dlWI3/HsblLm0'
        b'NHLmE224oTwjgYhLLWfWGT3q7u9re2DPXmYNXQ1JYWkiySlJMfFRzxwCX2XncdLMk8UF+c9f6CSLLJ9Fi7cvqj7/HMsqMMWxU3KxsHTBhUdhBTCOtZ7rivjjTEYgdEMH'
        b'H85uCzvtGW65vnTUWZjjYKvbFf+VWPnjOLnurWNJCjH537gjSs6hZ/b+3dCiZHwT7NE4/nHHXad7UYJv6hTtDHZWEMifNVWx7knWa3v/bfi5xvbe+axMX5+lAtVmmynd'
        b'U+ad7374t8g9n8iE/6vpRuyhVh3brZckaqTSv/0rk28v2J/616sZb5x59e+9gRcu6m8Nnvj0zY6bYWaPQj+5+KuLsVZvnEv/1thngoSY7Z9/YGQqxUOLdu/NPLIgqd/K'
        b'O811MJfDBn6KLKlih9pqjix/RGbCkPfI12s58tACcpPXBUHS8A6nYhK3srsFeAc5ryzlsZ/XlziFA7wWHyAVUo+l2XH0jNj3DpX4cN35l/9Ii6wR8kqpHKetE/M+LyLm'
        b'swV6K2dl+KuOV0Q9E+yZm58QQOt7XS+M10ujNcL465XgJknLvb93vbjlJO1J+t31F5a0xdueLWmfP1FWbzYzJpH5bP4rJSfFMvX/Bp5Ob00Ki45JE1caEpfMXVfbaANR'
        b'6sy7ROKucz6UmKuJcRHMCxQRvvWZYlc8uSfr69Cvv8q9K4INBZekD5fJcdgYp/ho15M2LcksVyVxICtUWzbGJCYmXs9IgruJ+O5LN9k588BvvP3SVNW4W9cdU6lX1MKi'
        b'I+NCzUPiI6NDvbgDxa9biwT3W2UTtrxmKslhtytQp4blWmuz5A/AKB8wmrLCFhKDxMqrsTPoxJzrnAhwOw7jTx+R64Q7krJ79bjTyvAQpqDQ1Q4nmQgYxzJ2wyXv8HH3'
        b'viZ+yROGZGBsc+SX3vumEsJv7AqFJXMcbPtiHGzH+He1wueq3/aJHtZXfj+1nkfXF7R8/ATHdszH2qy4ImG+LtvlCH73nDOvXzZqVlRCysfntIuPqYQP/1flSwrkPS6w'
        b'wY7pcsfzuJNPXEY95zbnIBsnTbi58Quj+9+G6F9RticdoG+VFMTFAGQlJBXkhVqGT9a6U1FRkZAVaijLCpXk6XM9WaH0F5JsYb8wvqUmtIxXExoZygr5/K12aBHx1fBy'
        b't6yeCWcHwiUEJruk0rAER1P/IsGCrlC1nYzfGocEbN2jAgX4EBc0Dx6AnDAclbbHIqiGGlky9u7ibcNNUEXm3z14ALXHj0OXAtl5JUJ9Ur0P8dEmaLbHKaiAiRCYxoHT'
        b'myQ4N92ow2F4BGNu8MiVnqrEkuvEVAPwwPIGdHvByOEbuIT3ZXAMBulrfj/0Qjf2RV2z3onNezEHO+OhHe+Qmp3A1hsO7FYQLIZxbddrh321oHQ75jjfjLVB5iZ9GHMY'
        b'C6646hmG6LnYe0oFWWdZ+kJ3kIEF1OL0YZjD+zAJVfEwiNXUzIwbzNhd3Y2V1pexbBP2heOYOqGhe1CDXfS1gA3Bzthy0iYWysPYrXftMIMFCYSqqrHdH4dhLP0q9sCj'
        b'm2QPN56Gal3sunIeG6DnoCaOuMHCHiijuVdDhepxGPWHvF2eNICZXe7YYgujN3HoFDQLsQ9a8DbWQRv9XxkN/dgCXelbRApQB1PYYW1Oxu5MtK38YZyGwjADyHG9CnfC'
        b'qeFGb1g0DXNJMHTBihh8hK0eWB+kA8MZR3EWJmijxhykoemUaQDNvBTqIV/e+DRO6mAndtFPD71JyLUF0nLUQ6M5PrR13OmwQ0MdJ87QL9qydp03w2YcVFHHQqyC6dPJ'
        b'9NtqJfltuExvDOI4jNJwxgTYaBNxCJsvQKs1LKphh1KoN1REpThijh82boHSywdkcRlmDdRhNg6W9aEgil5/kMgSJPcaYFf4tjPnHKywlihhFvqSQ4joGrDltKLuhcz4'
        b'Q1k4ZXBxM7T4QJfueRyl9WnEflmazBRRVAt2OWGZLBSewPk9tJENMGRHs3xA43sIeYG0B5UWR4ggSjJgQlufyPwRbeY9pVsiXMRi1x3wwD21gsiePmjAVrjrdxQqiO4V'
        b'YREnNW840QbfPwE5W6ANmywU9+EIbdA4tItOQF9YyHZTqIqWhFKjbCvotU3NjFYm6FcMXdhPS1uWGHwWljQDocUJWmAceiAvBNt2Y6OZMc7iPDwUwZgc1unjTIgUOxk1'
        b'FRCUfgRbb/rHwRC20kosmdA0ZrAFh+M9D1ET7QbQirknA6ntmkBoPAhNUBhKvJcrYeeNNTBmQc9MYD8M3jx/U10lMDt0n2sUtqle36eKwzTXUqLlPGKL2/uJr4pdDb12'
        b'XDcmWquEZnywl6h8iKhzFotCsCYOFmlOJ3ABimWw1xFrsshI8Dwag8O7sNCETI3lGwcts6Hgkpw/zOpsYTXZ8L6qJPTYSibgcjBOSGBVhlbICbwDk/JQdssNmjDXwBUq'
        b'giAH88OVoQP6ff0DrMPUjHVx4KirvIaa5R4pfZsAYqO7XljkT1vchIM6UERyJScE+w7QXi7AbcwXYY0PVOO4Ebb5YEkgDsKkpCqRX4k2dNFMmGjKv2zNFheK8AFMpWfo'
        b'QvkW6m+YlQ/LIIIozFSVJYaYjMQ6nLthrQG1tIx3aHvGSHRNy0YpeWCHLozgvXNncIj4Lh8fGl6EJW9PWIb7cjugJpmEQh8U2EXg5FUsDoQlSz3mE7zgCw/1ieiGsNwP'
        b'ajw9VC+k4zT110e00H4ecomFltltStY4pL7Lf4emL+TSmk8HYW8crV6/L0yY4qwUNIXugM4LuJj6pgSXgFpIovSunwNZEESSNO45M5hKtcO2C5LU7j28Ex8C964p0GON'
        b'+0+aQ59KsCcMOEIZztBqLWKjPpHSIyihqU3AqDsUnCeGzd+GS26Ojg7Y5AHd4SryZNMUQy8R1UO4sx1ajNKIhhslHGHxuuCApTvWXkkxo22bhD4yLktoSAtYQ1zXGnr+'
        b'YjyJjy5zbI2l5V4QEC2VELEOkknZgHUXTnApH9pnUy5egnveNMIerMIpE2KO6iPbrDOwTEMO5taSLDFIw0ldGsd0OuZZyGXDVDwnM+uUrkMzCcu+o14HMreGwZhP1g0t'
        b'0SVXKNWG3Eia2DI10EeiKe+AIxFwk8xV0mD3L0PtJtriAaNNUGuLzW5wL4UeyUU2kw7ShRVwH3KUJTDPgYRIr6YMPLTFeR1jIoYJmLfGRxrp2B2veV0yOi6QhZagnni2'
        b'AOuUaa16aIZ9uAiTJ2lDu1SxJGhzNJFbHo47QQ+t+uKFXaSeRoIyDIh8O686YFUwKbFGUxhIJ44os6Td6DpqTYKumAiTlOeFfVf2Y7VJLPbfPKaUSWPMgxyWOAeTe41M'
        b'wkNYch4+VNTAWpzHPEUscoF269NEEtB5nQZQjJUmME0gdQgqM7FLRn8HrfMC9rgEWcEjbJN32U1zLiApeY80d+txmHSN8qO9nITbyUG0o82kEztgIRNL06DpokwENjhE'
        b'ulpyWr3SM4UUTkEqyYUqeqbhsKt2IDZC6xUokUjTgTYicFpEInBoPxdLo1zGDtHOBA8XLI7fhNURZ2U2X8JhPWhkxGVFDN3lonokPfUtJmuL9tNbJGrjOYSxiKNmOCM8'
        b'sSUY7slgs5+8EMZZ8nEFMU0TVKXAhIDE7Q5NzNlLy9tkkIUjMjAPPRGuJtDiDEPqpA5adOnxCiVsk7lqEEs71qJMzNhkbYqPAizdoPVUFtYZQJnHloOkCR7K08o8wlKZ'
        b'kzAQzJglRJh4gcGhu/E4igsXz5K4YAL4AckBgiAJB6BV3cnMTw1Hg6A6+DjcPgHzKnjPNfs8Lcu9g1nqUObvFQQDO3Eqe7NzMMmNQdqNoau0JkPQev66EBtcbGDu9J4s'
        b'JWfMhVZocgwjxXybtrhLR5XWugB7RLCsijUB2ip6pPlKNKDqolfIaeLcJZtT9nHEw7WBUGsJeV4aVhrYHwcPnIj3imKhzhhvOwsxR+okzIcfg3qXGJh09IEFKDpm53wC'
        b'OzJv6WEz0T8Jxl7qslBwlbRAF45Lwz1ihGItYpgJWq1KbLOGJSjTJT5t2wkLN3HmmiMRbRPpugpsOHwNu46STMkJP5UBBa4JxAD3bkLDTU0iq+nw6zgQpcPSM7GTBEXJ'
        b'ISw/q3oAid6rsMeVwBFRdK/RQRoDO/3b7XQww1WF9OJxPZj0JzIkg+r6PuL6JRx05pK78knrdRzcwkBZEpRFGu1ipIjVGkc4adBFw8yB9hhoCFXNTPPGNuplitiqEWpi'
        b'aDQDBAryJKAilda+TDeLptdKKnSINGdyIHRaYjv26Phu8idNcT9WCzsjsN6dtrgPFy7A3WAa4ogjjBATF9nBHWRcvoQNAdRE4aXoNKaDMPeqLk4mkoCZwPwdLufkcUx/'
        b'r8upzSTCb6fWSnDxkFLsINKmSazCCDOcFV7FCoIRDrZm8HAPjKUp7LKTSSIY2+RyBmuO0WTg3lHa5SXqezKJlmmGiaHAbVBgg3l7Q+AudV4CY4lZDopbPGEJR0Oxg54Z'
        b'IfHRmG0IOWZnaMtnJW1JFjbA3O4DR3DoIsG0epyLwBmW+Utyf5L0EUm2vGwLrFMjwi06dhHueWCDnxPp1qoIJ2gO2E24owcW7Km3CkIk92BRmfEpdKrggBtU7M3AGiVv'
        b'w6irJOtyZYhF2rPkL8PYTvvjXjoOm4jEHkC9ksVmSVq1u/JqdjhlaCwrcsHbW2khc3YS5feq6pOKr6A2hy9g3kWoOwokmRxJEZJwIoiA85exDdsPXSOBVQ/3SZv0ENgf'
        b'o30SnrQ4A6U740lRt8IDX8w7h10X7KHEy9ybli0Pip1j9X1dTzEcU3LxFvSFmuLtMMhRzzLCRtJX1edxJolop+EUDgVjkcUeaJQgQuvwwsKjRF7LJNWHoy6SWVJFkrtY'
        b'V4eWeCoYaw9hIXQk2NLS91tDgSNRTQ9W7w3SiDxg5xsKPcE4m3CBxPK9Q8ryO20OaujamJJMn1LEYvXjPrtIGy7vhLYAkjXTWlCziajr0VUo8TtDbDJ/Ae4ZQ59GOI7H'
        b'U5+tNNO7l4gZes9HaJIIqoFhSxhVoPUswcYoKDaEiYuJl7SPwGAcPTQMzZEkJJpFsawYqT/R/JQNVDrA0i5SuXN4J1sDHwnisNWMAG0d5qW+TXTpQCuZz8gyN56jyiWi'
        b'ygwcisD+67IEffLUs2gRc403E8ydMtijhrUqhCfP+mW6QVW24c6sVCgI0Tl5WdGPtHg3+4K8/ST9G0iU0GsODDrdUNkEDzJoc+ex48wRBVKXM7CsHIy92BxLGve+FOak'
        b'Yv3pCFjKiqePWkMvEpwZ4RAEEIJYgKUYIv/JUB3MTzLEXhOijC5inqHT8Vh9w4gERBvDvNE0gKJL9ld1FOiNahIeDbQcpd5BBPYGb/rfPBudsU3RBwm2dmPvNhLf9y84'
        b'ZijR6pYC494qmI1PdFSDGeUU4pPcJEIVVYE+NnI7cCzUh1i3wZ8emYE7Mji4KQKLTrF7XOnXhYnQokzWyh1oz8CJy0SsY1aKZh4koZpjVFxirzuS/dS1mZiUVZ4r1TeR'
        b'pLWs30OIs0pbA+rijQxJEOODzTjnSqKrnEyUKVLJ8xKK8SyrH2uu7cS+7WTkDuKdm9BiYkEycFaGusvDPhvXCJuMrRciidNziSPyUokZWuShZi9WXLHBVq+dxA+T6qrJ'
        b'oSQDF3HwHA5eJNbp2Upk2HaQUMtDGyjE2cR46E4hS7yILGbtPRokMxuPkKCfPLSdBl4VDeUEG6SwP4A0ZhHxQK3jFZwO0MV8SajD0Qjq9y6RW4tge7pD4rlkrZO0w+Pb'
        b'dhPL3IXq8BRoc8yAku1YLHUBS2Oh+TA9OwFTBDwbsfgMaYpSwiZtGl5K0OFhnO1LJPoARzKD4gguNvo7njjIDLQhO+g9mrT7Ajwkoqr0hvGsGI1IEkLNykThUxbYfeqG'
        b'K9a67CaaGNHehrlWXrEBtHZFpGSk+cNAxaTPijxZ4V0rQaQm2XLl0ny2SrW2OTufxA4n7SQpXbclSZzFogJtnmYSAqGT4BKNqDlEjks2IdHVi6PsgIHwiADHIrH5IAFu'
        b'9omdiMipFEuFAqGHgFFYqzku8BfP9B8lAFJqLmQVSqxJ6LbDbGqqq0ggkNbmVqkWy9kdG06KtOijt+QNz8tBwyE/5RB1Uk3VlkQNXbRM9QyzG+MddxdvKIh11DIlafMQ'
        b'e3UzST91Qru7ytHzJMCroC0UKwmzEANjxwHmdyH7uzrDMtUZBrUYzrsJvREhWKgAnUkhxDW1sOwIOWdPYb0PbSR9TryYf4K+7YH7AhKxhQFqBOJarWi/7lqf20Fkl7uZ'
        b'LILx3UHUbqXAl/rMjyCpOko6uJY2mqycmBtQYEn6tfo0VBmTsTBB5HCOMEy1MYm4YaixI1MpP+WyNzzyJGrvYelURFUTBmQ25ZFpVmRnegMKbQjAzZOQGCOFcA/GthIc'
        b'7odm2wjbNBFWykQoY5PbFRg4gLNJZoY4dwmHzrlrwoDMjdQI76TLJEGroUeOO1zZZKDLLiAhpNVFGobMlAvnqK0yWs+GII1Y4tk5GkLVfppqn4Oe/FlFbA8L5myvFhHm'
        b'WZMlk0OrMowkR5etoUyEY0G7fa0xP5BkWuchHDMmKrtvYwbsEMgAVB0iQFRJ88lJ0k6VJN1UlUxz6IGl4+cJUNZCyW5ol8EHMVjlBvVH8F4AGVVlZL0syWhiafDWMFNn'
        b'fXwgC/XBUJ9EXLJkqpSKA2FJSdhHXzU3N9Fwiw+cCSQrcpgkcbUNTji73lCNDIdpk00wo4QdbsRVtw/isJU7MfYAFCDz7hQrkw0/Bbl60HaZhAA0HHE753M+6ew5bUJE'
        b'RaTI57RtsS7JyoakxESaiIRDLzyw0ILl1GgcOkjGQNVudWzRZlKcFF7hnmxiiOn9BBeLmT/K1CeSFCo8tILWFCKoQnh4HgrjSYf3wOBxYt5hz2wYvkw2Xztt6bCHPeeC'
        b'WRSRiuk4H0X2VC9UkijCZW39W2YEPqd8mC2B1ZGwgF176J9lXDLSgoaIZPMUHUJdQ444e2kT5m7CRXaoNfv8Fr3UPtJgnlDr/KR3hpodcTRyUk7DB1rSeunYGU68kRtK'
        b'gnn85Hks8dDQOkqmyzI0JtFqFihoSJ277OVHgqfKRo8opwFGdbFvr47n1sMwmUVqujBQx9ci7KgM6bTZU2c4N82EryF10gK1B2hNFuVp/BPxJJO6SKUsReNMKsyYwiiU'
        b'HjYjzujDtnj6oTJtH7SQTiMBVcUotRvGd8PIngTC++32OBF+nta5wPuMNkObSFK696yQAN8i8XSuAbHPuCupuHZJA7xvxp2Q6lY/A/3bSKhWQKtTkhfh7PYoQp95Tky2'
        b'jkPuzTgC+PpOhBS6dZWZd8sL72eqOcvD4NWLJIbLeEdAchgxQNWVnTQs0mfsrEQLzBkQH9wlOxfue18SxGLhsTiSOG2XjkWxjDxsi6AR1qSQFs6jN1gG392wcBiNO3kQ'
        b'p7RV4NH2c0QLTRrYe9SSrchuHNCOwLkYIhuG81ld1sUkXLokdVgFm/X3Yo1vIkm0MnXsUtt7i4yw2iwCUzmwfI3QztQRGFD1NTlis4O07z2sD5LFTtcEWvZWk12pW0xj'
        b'tE66qqniPfXsVPtNUHBMwoeIfpAosBj6bpEk6Ew94wal50nO3jaDWY0I4stFYoyZm2evkqqMhwoRjtPPDwjpzYWkkbRtc7gRiL1BFiSWWnDIFBaOXYJhw53uJBVq2RbT'
        b'NjwiwdZM0mFYlSayhMu3TnpRoz37oeaqpqsv9T2vTyuy4AyzR0kEF16W2nYkBcYkOL8NjlipwV1/LF01b89S5+XQuM+QWbhBfgpCmFbDIh8YlbaA4fPSWjCAJAKn9hMZ'
        b'jNqdwSUosYyxIwKt5rwmg9ssSIoxR12zqjnkk1AjCi2AMbIN8FG6r4Up7dcQLjoehQEDaFY20KPVL4OpcOLW7iOHBTCgS3JlcCc022HOVpJ1E/AgEDsCoNU6iMROoTu0'
        b'hQeRRhg9w/BJF3YGJe2SEkUfxgYr7M3AYkuY2H4a8+L3QE/sMVZHniZ8n1BrmwsJHJjzwhLzINIbrbuJle9YbD0bjb0HNc8l4SMforYG0hz5+zRkoSM2HsZIerVTD2M+'
        b'MsQEy4m+pDeriWDKoCeTJk26Sg/7rKA+lbRJo08skRPZLY3mm+IhX97IHoftYrDJQ+sqLMJAKrbawfzRJGyktavEsTNbYPm0wBbvbJLFZRGNssBbE+akmGuk2w76orTc'
        b'oOGEvoOvnh1ZXSU0KRw+RHJ8kWhilNjgIRHC0jWyPx+o07I3h4Yx1omMNiGxWi5x4WjUNUWYPo99sb4+MZGXCKdOKNEgWkjfDsnjhCeUhkHjGTNtICPjNpbHKobgg9NQ'
        b'qe4UfDEL2z28N+/F6j04vjn6AlbYSDDcSkIon+zoDlz0yrhB8y8NVeEOaj/aIrkTGtT9sCAs0PXSMW8XYvEyB6xPtg3HuW0kkEZoU0vJNJS+TNLhgUKQASdhmNyuo6Vs'
        b'CtsH4zi9zZRYtwm7rxPHVcCYCVlApaoypB4HEwM1qdPScFw6eY12pxwJHVTJwYzaIUsSae3X1bOVdxFzNZO8eWSORZeh/eBVmNmGJaknRMxvQ7POW0faZNzOiCS0sR+r'
        b'nZSToEdDOnYXydy7NJtxkogNe4Uep92ZARWGs2E4uYlZQzT5TvNDSlhlcG6zJNF4C6nvMkLwDzJpuev3nZYLgJED2BJI5N1CgntegdnkMGQQQOtNZjVUaGG+vwtDPurU'
        b'2PBlQ+i1xuETu5HgjMdmli28DTosDYk/6w9DqyatTWsyqZz7ETAeaECE3iLht08funXtICcUiq0I+jqQPDQMMNUnOVETjXlyMB6RlE2aKw+mgg6QTpmMYEK8VCblpA0M'
        b'KB6kNa7EZp3LtEpzatgVpYkjsiaZRw9f04a7B2HU6wZRVS+pvh5s1sWZFA8cUCOgU0ladCGadEGmvHMSbWI7NVKzzTYFeg5J7sXhIzi8eQf0O8pjWwo+UIm8qAN9qirX'
        b'oFYTyzyjqK1cqDOXsfamPSWoQSszK2nkneh00C8WR7aRdBggRmoL3obLLiS+GuGu+1EHAXFHCbEmAXASXjUwoxCJhftJQxOVljrDmJ6ckMTBw8sXSPD10q7MUqv5qppn'
        b'SZGXQ7cs3ImGAjscsCAdUHQrDWpsLyBzlXcJYPLSIX0SKvNQELOLmO2+DnRaEKc3E32MkWHdFiynux8XtKHxtK1nois7mAz9OCxJr9yGSSMNO7I5uqHvKAxKGRA3tcHy'
        b'Tk1dArPlu7HqBlax1SlOhwlRovEh+m31YejadRbnDrK7PlR3HN6B7bbQFBFIpFOEDUmkm5YyzuPovsMBkBeXQrKxzlJwAPpCMjRCQ2nh46JxAcpDYewawedqAnDltFrj'
        b'9iRa83fYkVU4h4VJ9p6RDiQIirAky4IWd0JRSMQ3qMigMe1lc3hyxk2Y9aUfu6HFiyz0DhhNdMORs5xmnMKFw+cdodGEtCZZv64OOOVBAG5UIXwvIbmmIGKOZZlQgms5'
        b'27xhNFWCOCntVDRjo1wyDMeJohkvLeGCGYnjJiLQGTuc0iG0G4i18jHOMLQDW52toFpEGu7eJvaEg0oMGYyLWVFubgQI8jwC7IywIDOBEPYS3j9K+z8BHXK4eEAmjhTP'
        b'kBA7/XF+503IIdOv3thFWcEfG8K5CNswc/ZnZ0EdzDOvVjfM+dEkiVP6mL+IoG4v9LlpYfN1v13nrGh69Th4GHOzsQKnDUg7Fl2AjgCCW9MW0tEJ1jow5iZPrP+AHiy3'
        b'ppUtiCM2WFLGexchnzDBGKmXir1YpS9Dc+yVs8CRG9EEAAtCM+COA6nlCrgnwgkdOWw9o+OiQwTzwERKZTPOHgmAKiUnWZKb85jjSoBmiEm1/TgiIAVej5V7lCJOQv55'
        b'TxPblFh5XFI5m7mLRDzhcserJ6EyEWut/cmmZkh00i76BtFH8S4YU7X3JDbu1IZ5eZgJvB63G/t3kuB6iK2QfwnnM+Sx4IQ/8UU+2SX9JHaqyWbZSovduAXvKsqLIrWx'
        b'9FxszMXLNtjiqSQ8oUXvDUO1NNSoahO/1cLDWEV3Myuc2cLcn6S6c2BRDx6yEN59g81k85WFHnEg/N6+jzu4PbLZIh6qvbYjKx7U5JacCs37aA8K3HH6sAIh+AVCBm0n'
        b'MrWxS/GWFM2gxgVa1OVuEMPV0E/VsGwWH3wd2reSRZmnZusL0zrQpnLQQTEdb3tgvsFlGbx/GmqioR2GiIgq/IKYyxTvpzKXF+37AknfMdISedhjiUW3Lm8lRU0Y6Aw9'
        b'e9eHJnP7LM5kWhIwg15il1rS1UUKQaGp54ghO4BpE0KkPQdobss3oW4L1kQQ6J6+RtQynK5DRDV0EwuzoZgkOWGP24HU8+KW1PcIKZFhcJrjA8YDTswtVXmWlDDJr9gj'
        b'Rn7KO7CK6P/sjiz6uE03KkxOB3t0bXfQ5i7jSBQ8kHELpj5mCCL1ShzAGX1YxvsHYxVoQvl4LwVYEDj33GGokYQGHZLli+nY7AldIvq2D+YjSNn03yK5WEmsVEdbUS2/'
        b'Bbs9SI4O0cqXYc0NXIaFwxpYfAAWLLBrhzeWxrFIlzvzU4WfpLXJNyaJUqwoiYMRekT1U9eNiMnn9vomELn1qFvT2Gr2aGHDdkNTbDU+QXiBOMOZaGFJIxqnFbHl0Fbs'
        b'3URmY/4FyHPGOScYkssg4VJL8KeeBHM3iwDOS8NdAzdoVCADoXePMnQe3QvNNgQV8nVOa2L/9n3S0lh0ypkVmLntfJJM4gVLQliFdjiunIjTVoqe1tBlg7VH7Z1oUSah'
        b'RZJ4vockfUFmsJEKO/o1R2JgDnKNiNKHhYTLstP2ErHV+kH+cRhW4Mhi7jLJ7+UrxiQP2rAwgRauj8mB6T0EPmojo6HblgiaeeFrsUQbJw+wK8OioEgauqKNoF8SRh3t'
        b'cYbZ55hzisTXlFc6afRHNtIErLuhzATzzGltRrWg6yY0qhJ1FG1jEWWpG9IHok5Ty3WHlbCBwIN0OsNAeer748neI0B/m0RENfSpY/Nx7QyWXeFPi9cC85fSdsKgBSy6'
        b'QLepFDRvJXzVGggDV8jmGYZui8uEgEhxH7BP2AfzHruuYddOaPKAPrM9J3BSilRKo/tWsmvv4sReUnADjEea/dWO2xDGHrLE5YAdJNka/YKVLt88rRdEtFOEOfu9qI+m'
        b'7Q6GTjcFhC+LrhAd1EGNqQRfWKvlrB+ru0OmRUOSFF94Bws2cc6jPduhJdmaKxBHKKlCAA+1oc5UxN+u0EkEU+HJHEu2Ahi7jg1xLvxZq6pAfU9WfF64RxBGT5V5XeBe'
        b'0DiznR20khQInQWBLBawg9QN5x9rgQeGYvcYtm3BEluso8FxbQ0QtJjwZEVxrQVH/LAkMo57ZRvU6GGpF71iJyB92YiV8bu5D6wO+a141IiNirBOETvEVzDjhOoNLDWl'
        b'd3wFBEEmsSsD2/lSZ3N4j/6WenOONQXmR8cpT24A53FYTuyJS9tKuLUTx0yFXE9OrASXpwc1Z0ZGDIm2Ii9Zrh9ZU6xb9cWpOnA3VD0yFbpwdw9xh96cnLkjcW7mssFe'
        b'OtduCkxF3K/fdxJx6ZoH5YK9XDMS+ZJDWTLcs0bzomDzlxVCBSy/zIVrjTslF/Px+Z9IJo+RtCoyi71Ze9ZX/6hGflT6xd8dkA4TdaZ7fbyULivnnqMh5+mqv9PN5Fu+'
        b'qovhpz6Kb/+L6NNxu0OXmpsKX/lL5sd2/2i18/9s4V8v1x/6VZqddNmVD/+V/4WSTXfg+XlH8x/J/rMlq2is+1/yg29qu5sef0N+fP/lsPemP/njYLDRRzpHypNT3wg3'
        b'+eJXWzS9TtsWjF4abC0ZD5YcVahvT9Ic/OH/DKW4Hjn/T5WOX964871oR2OHpNDWfpfXbr565dv6Az1Jcef7nd93/GjntdczXbT6d5zy7XWpGx3z6cz1uvidhOMtqbdT'
        b'j/3L+5WxkW9J1We+c7/mhI1rNOysb9t3SqFTavhNv466xj5785jme1u+bTNVPfJeQKifodHPKir+pWP/U9HLf/FKdz4UkrlkbbTfz/XALnfdRvcPmusD3qkXHcr1San+'
        b'fZLXy38iJXRxR5R7aYpb1Dc+CC9L1hqwC6q5WpOVpvaz325951e14cOV/zMkn5Fnc95vZ+2r75Q6pn0idfHaH1/+/AdNs4aiv0n/7aeaLVeqdX4m//qF3t+M/O8lzeT7'
        b'TZ/tzfexeu1wq7n03m+eKjB4ozTuZ78L0LfPHjp++zPs1fSKybw4uStNHl+pfnVu78uht910N39uePXHYZLd4a6iA3p/eLhz6wcfm/+vYV31xJtXJnr/KV0W0vbZ7KUs'
        b't3c/s1G0P/hHE+M933njtV8MT73xu9pbzX02vlHybywqv5XhutRyMFl68oF+XqzSX389kfG9TLczsy8rBPa8p/Lgtc+iArb/8JV/nvlsaWpo/E7EB0E/ug5H/2HzQazV'
        b'zzrft9tXlXm4OOK1qB1mhwx25mk+SKoLyK47lL//QZio9W04kLZl29vf2vL3aznOBr/7v09fevXla4u9jp/N2yTCe3+4G1T0nt5nLx/5Xv/7Pxme6/n3nUc/+uXUq9l/'
        b'/qYhftf6iz8UZ5ecjfj3h7v+rX0r7GTU7vgvpPTOn6oJzjSV5y6fixKQuiz1EksRSazQhHa+lkaDD/T/f81da1Ab1xXeF3ogJGQZJ4AptosdI8TDvFwcx3ZMMC4IgeNH'
        b'/Uw2Qlpgg5DEagXYsWsgIY7AGLtuIKnTcYMLfhAIOPGL2JC5d9JOJi3Or7qzM514ptN2msyEH/WkTfqjvecuxmnc/GinM3R29Gm19+zV7t2rveeuzvedhxWh0dQqEzq3'
        b'hqpyWPFl/4OsDqhj6zcy7Vx0UDPUHkYdFsVqJvaoJ1GJJpBR+RrPoJe2pR0STOtwFzVzkpv0O/NmxDEYa8VXW5utBib5SXi8fjpZhUSP5NYZw8ciLQnNUXwtEXWj44km'
        b'azweT2yJw2MexmkT8FvL0Q0VAouT8ITz31mi3rmqSzcwHsGAbgRxjBIE8EjAaDFZt7XoFTImfJ7LyyhS86FsVESnIqjX1EwOMEKGudhD1aEzTzEefMVABoUh1E8P108G'
        b'xYF5Jbt/EXFBU3t0HRf8yr6HU9cVLmys6YKDM43eYP9fQE85LoqBkNcvijQU+2MCjIvjOLaITf8HxwFvzcGZeIE18QaOLLwtzuFwmO3pdqPd4IhPWixwSRXJ3yX2R5lC'
        b'UDkpgdBsXuBgPf0oqYtNXlUG20SOfUIP3PZx7OPwvnt+iyF5b+pmO2/jHXaOzT7KZHBsmV6SwWVxTvJyEWxn3hKoNZdNt8DSzgwLEGz9d8O8fjmQOJK/9lJ2zgc788pd'
        b'OPEHAeAFC98pFqwzsnpj0OBraCKaGxa4U8yd8Len2qLKWZNbfeR21pdCbgR9kCQNxVCfkbGl8N85jN+UKz8qj4skswzz3kRLce+6an6zfctI/SeB239sSjCsWLmWrVvy'
        b'Ub7J/qVpkbpeqbUU/Hx2suuG/U93k+8VvZjVNn3v09Y7g49VLLtXvXRifEr45Wdtvjv9M/0/m5ywtSY8M5OwYaa46c+us0eWjJ8vzf3VaEbGkndGHC1a8FgGzl398obP'
        b'lw4feH6yYMe601l/m82r6b90+80Pp2Z4mzBaN7JztiPt0iLL5ttFb6ftOz7wSedP8mflv5RGGn/z246JTaNDR8/Nlu69aD4/vPjDnCu//t3VTX9IN/EJK9Z0duUHdr72'
        b'/t1PO3qcLeOWxI1f2J9btsIWfiWjrOQX5tqVJR+kzDR32MY+/qA4GO5J3+6//tQJ7q9t72dU3hPzPrtevZG/eueLxV2h6cHmA6WWz53LdAGyCTLhGgIHtqaGsnKNjGW1'
        b'F13m8AU8FU8JGiyaXuOuycETYGN/FGLXF+GbPJlAx3A/5Qqj9lbiZpOLsZx46VSxCx73kIvh4NPRKdxLWdquVc+C+KrHyMBfVQaBMz2KbtGx0o9grt2TtwH/mHiqOxh8'
        b'rvBxylEmTtEpFz6RCbzi4yxjzl2Jujgya3kdTVDOCT6TlEMGyQKfrlNQzaLxKtRJmd9r8UX8hrsCverMrsiZkwmz4W6+Go/+UOesjaAho7siF9/QmelAS7+FdFU23LV9'
        b'tT74eipwL3rJ56wQGAc+zZOp4c0auvse1ItH3JXZ1cWFLGPEP8qu5wzo1pO0wWBygtvdBYVkZzJjkPAk1UFbwa9HZ2uolNwLu5ZCcQUIBHZnQqkNj/H5eMhN+WzGjaRT'
        b'92RlEg/7BGTiE55mSQPF9tNv3t8CT5ZxL46VeMhgLOSzEPF4gDaIE1/wuHK278C9QKlvYtF1MnvU89pasktcQD2vAgUOD9DW4akws/SIgDrx5VTaaDKHOtxwUOTMocEt'
        b'ZPbV4eTwyUzUQw02kVadjnzNIh73ZFZwaBy9XUyp6Qc34wELvpyIr0RQLOTE18L43WbinFgZJi1DMJLjvkRbOAUNpFJqkgsqA1HpsxCAz+FB3IXP6uz1waJD5HBXgsTg'
        b'fEbbNDSgOhlIjncBX3ej0UxycbtJh0Oxmt3ElyGnhnrzqnOcBmbrFuNhdLVcdz8mMrZY8Dh+l63NZ1h8isHD6Ap6VZe76yFz8xEIpwaWPJkzoWNxh1l4TonO0Yarz22G'
        b'0hyQ/J4jG+H3okxqVEAvP4279Ss+SJq23ZUDf3LgWBXHmB9D19A4h3rW45/qHKj2R/BNV2VOticnl2USGvD0Ej4ed5IfENVHex29sdFNro87l1TQtx9P4j5yDosLeXjq'
        b'2qd3ykEyazzj+n52FjBC4epwuB+fBH7HMG6nUoCkA5+MuirL0BiZvrkZ/FpZyv1cSJkLf7P/Hw0ZjyyAh/Igg3EYxiabiRLqTXRJooJrpjneJvDBwO2ANcdcxmJiyQf/'
        b'c27Z/WWNTrCizkOWxgekoCKTgU2LU6PhgKQJATmiaoJf9hEMhaWgxkdURYurPahKEU2oDYUCGi8HVS2ujjhZ5E3xBuslLU4OhqOqxvsaFI0PKX7NUCcHVIl8aPKGNf6Q'
        b'HNbivBGfLGt8g9RGTEj18XJEDkZUb9AnaYZwtDYg+7SELTrH0eNtJDsnhBVJVeW6g2JbU0AzVYV8jeUyOUhzbeFaKQjyVZpVjoREVW6SSEVNYU0o31ZWrlnDXiUiiaQI'
        b'2N/aoqaQf9339Bwgol+ul1XN6PX5pLAa0az0xEQ1RHzGYL3G7/FUaZZIg1ynipKihBTNGg36GrxyUPKLUptPM4tiRCJNJYqaLRgSQ7V10YiP5m7SzPc/kNOJBkG/6oFb'
        b'prd3ptIIjlsYoAkgCtAGALxBBTLcKEGAAwD7AVQAL8AeSqQFeBagHuA5gGcAZIAQwC6A3QB+APhq5SDAIcqnA9gLUAvQDBAAeB4AfGalBWAfwA9ozUC5a4W1F6he3jyd'
        b'EDqSed7F+nLft7pY1PIrUx3pN5KvIVezi+Lc+pyn/lXq3OflYa+vEaTMgPEKZZK/2mmixEDNKIreQEAU9Q5MqYOQI04z6Dlbld/DliP3PeNvJITWTE+QXhANSBshrVwE'
        b'skwL4DX89z+kXUlUv/CfbAMoSw=='
    ))))
