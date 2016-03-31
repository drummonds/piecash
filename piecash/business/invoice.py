import datetime
import uuid

from sqlalchemy import Column, INTEGER, BIGINT, VARCHAR, ForeignKey
from sqlalchemy.orm import composite, relation

# change of the __doc__ string as getting error in sphinx ==> should be reported to SA project
composite.__doc__ = None  # composite.__doc__.replace(":ref:`mapper_composite`", "")

from ..sa_extra import _DateTime
from .._common import CallableList, hybrid_property_gncnumeric
from .._declbase import DeclarativeBaseGuid


class Billterm(DeclarativeBaseGuid):
    __tablename__ = 'billterms'

    __table_args__ = {}

    # column definitions
    guid = Column('guid', VARCHAR(length=32), primary_key=True, nullable=False, default=lambda: uuid.uuid4().hex)
    name = Column('name', VARCHAR(length=2048), nullable=False)
    description = Column('description', VARCHAR(length=2048), nullable=False)
    refcount = Column('refcount', INTEGER(), nullable=False)
    invisible = Column('invisible', INTEGER(), nullable=False)
    parent_guid = Column('parent', VARCHAR(length=32), ForeignKey('billterms.guid'))
    type = Column('type', VARCHAR(length=2048), nullable=False)
    duedays = Column('duedays', INTEGER())
    discountdays = Column('discountdays', INTEGER())
    _discount_num = Column('discount_num', BIGINT())
    _discount_denom = Column('discount_denom', BIGINT())
    discount = hybrid_property_gncnumeric(_discount_num, _discount_denom)
    cutoff = Column('cutoff', INTEGER())

    # relation definitions
    children = relation('Billterm',
                        back_populates='parent',
                        cascade='all, delete-orphan',
                        collection_class=CallableList,
                        )
    parent = relation('Billterm',
                      back_populates='children',
                      remote_side=guid,
                      )


class Entry(DeclarativeBaseGuid):
    __tablename__ = 'entries'

    __table_args__ = {}

    # column definitions
    date = Column('date', _DateTime(), nullable=False)
    date_entered = Column('date_entered', _DateTime())
    description = Column('description', VARCHAR(length=2048))
    action = Column('action', VARCHAR(length=2048))
    notes = Column('notes', VARCHAR(length=2048))
    quantity_num = Column('quantity_num', BIGINT())
    quantity_denom = Column('quantity_denom', BIGINT())

    i_acct = Column('i_acct', VARCHAR(length=32))
    i_price_num = Column('i_price_num', BIGINT())
    i_price_denom = Column('i_price_denom', BIGINT())
    i_discount_num = Column('i_discount_num', BIGINT())
    i_discount_denom = Column('i_discount_denom', BIGINT())
    invoice = Column('invoice', VARCHAR(length=32))
    i_disc_type = Column('i_disc_type', VARCHAR(length=2048))
    i_disc_how = Column('i_disc_how', VARCHAR(length=2048))
    i_taxable = Column('i_taxable', INTEGER())
    i_taxincluded = Column('i_taxincluded', INTEGER())
    i_taxtable = Column('i_taxtable', VARCHAR(length=32))

    b_acct = Column('b_acct', VARCHAR(length=32))
    b_price_num = Column('b_price_num', BIGINT())
    b_price_denom = Column('b_price_denom', BIGINT())
    bill = Column('bill', VARCHAR(length=32))
    b_taxable = Column('b_taxable', INTEGER())
    b_taxincluded = Column('b_taxincluded', INTEGER())
    b_taxtable = Column('b_taxtable', VARCHAR(length=32))
    b_paytype = Column('b_paytype', INTEGER())
    billable = Column('billable', INTEGER())
    billto_type = Column('billto_type', INTEGER())
    billto_guid = Column('billto_guid', VARCHAR(length=32))
    order_guid = Column('order_guid', VARCHAR(length=32), ForeignKey("orders.guid"))

    # relation definitions
    order = relation('Order', back_populates="entries")

    def __init__(self,
                 description, i_acct,
                 date=datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
                 date_entered=datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
                 action='', notes='', invoice=None,
                 quantity_num=0, quantity_denom=1,
                 i_price_num=0, i_price_denom=1,
                 i_discount_num=0, i_discount_denom=1, i_disc_type='PERCENT', i_disc_how='PRETAX',
                 i_taxable=1, i_taxincluded=0, i_taxtable=None,
                 b_acct=None, bill=None,
                 b_price_num=0, b_price_denom=1,
                 b_taxable=1, b_taxincluded=0, b_taxtable=None,
                 b_paytype=1, billable=0,  billto_type=2, billto_guid=None, order_guid=None):

        self.date=date,
        self.date_entered=date_entered
        self.description=description,
        self.action=action
        self.notes=notes
        self.quantity_num=quantity_num,
        self.quantity_denom=quantity_denom
        self.i_acct=i_acct
        self.i_price_num=i_price_num
        self.i_price_denom=i_price_denom
        self.i_discount_num=i_discount_num
        self.i_discount_denom=i_discount_denom
        self.invoice=invoice
        self.i_disc_type=i_disc_type
        self.i_disc_how=i_disc_how
        self.i_taxable=i_taxable
        self.i_taxincluded=i_taxincluded
        self.i_taxtable=i_taxtable
        self.b_acct=b_acct
        self.b_price_num=b_price_num
        self.b_price_denom=b_price_denom
        self.bill=bill
        self.b_taxable=b_taxable
        self.b_taxincluded=b_taxincluded
        self.b_taxtable=b_taxtable
        self.b_paytype=b_paytype
        self.billable=billable
        self.billto_type=billto_type
        self.billto_guid=billto_guid
        self.order_guid=order_guid

    def __unirepr__(self):
        return u"Entry<{}>".format(self.id)


class Invoice(DeclarativeBaseGuid):
    """Object to represent an Invoice#
    TODO:
      - Add post method which will deal with posting the invoice and creating transactions
    """
    __tablename__ = 'invoices'

    __table_args__ = {}

    # column definitions
    id = Column('id', VARCHAR(length=2048), nullable=False)
    date_opened = Column('date_opened', _DateTime())
    date_posted = Column('date_posted', _DateTime())
    notes = Column('notes', VARCHAR(length=2048), nullable=False)
    active = Column('active', INTEGER(), nullable=False)
    currency_guid = Column('currency', VARCHAR(length=32), ForeignKey('commodities.guid'), nullable=False)
    owner_type = Column('owner_type', INTEGER())
    owner_guid = Column('owner_guid', VARCHAR(length=32))  # This is a variable table foreign key
    term_guid = Column('terms', VARCHAR(length=32), ForeignKey('billterms.guid'))
    billing_id = Column('billing_id', VARCHAR(length=2048))
    post_txn_guid = Column('post_txn', VARCHAR(length=32), ForeignKey('lots.guid'))
    post_lot_guid = Column('post_lot', VARCHAR(length=32), ForeignKey('transactions.guid'))
    post_acc_guid = Column('post_acc', VARCHAR(length=32), ForeignKey('accounts.guid'))
    billto_type = Column('billto_type', INTEGER())
    billto_guid = Column('billto_guid', VARCHAR(length=32))
    _charge_amt_num = Column('charge_amt_num', BIGINT())
    _charge_amt_denom = Column('charge_amt_denom', BIGINT())
    charge_amt = hybrid_property_gncnumeric(_charge_amt_num, _charge_amt_denom)

    # relation definitions
    currency = relation('Commodity')
    # owner = relation('Person')
    # todo: check all relations and understanding of types...
    term = relation('Billterm')
    post_account = relation('Account')
    post_lot = relation('Lot')
    post_txn = relation('Transaction')

    def __init__(self,
                 currency,
                 owner_type,
                 owner_guid,
                 id=None,
                 notes='',
                 active=1,
                 date_opened=None,
                 book=None):  # Not sure that this parameter should be here
        """To create a new invoice you need to
        - Create a new entry in the entries table
        - create a new entry in the invoices table
        - update the KVP slots

        owner_type = (2 = customer for an invoice receivable. ? for a purchase invoice
        owner = customer or supplier
        On posting -
        - Create a Transactions and splits to match the entries table.

        """
        self.currency = currency
        self.notes = notes
        self.active = active
        self.owner_type = owner_type
        self.owner_guid = owner_guid
        if date_opened is None:
            d = datetime.datetime.today()
            self.date_opened = datetime.datetime(d.year, d.month, d.day)  # Not very elegant
        else:
            self.date_opened = date_opened
        # billto_type = Column('billto_type', INTEGER())
        #  billto_guid = Column('billto_guid', VARCHAR(length=32))
        #  _charge_amt_num = Column('charge_amt_num', BIGINT())
        #   _charge_amt_denom = Column('charge_amt_denom', BIGINT())
        # charge_amt = hybrid_property_gncnumeric(_charge_amt_num, _charge_amt_denom)

        if book and id is None:
            self._assign_id(book)
            book.add(self)
        elif id is not None:
            if isinstance(id, int):
                self.id = str(id)
            else:
                self.id = id

    def _assign_id(self, book):
        book.counter_invoice = cnt = book.counter_invoice + 1
        self.id = "{:06d}".format(cnt)

    def __unirepr__(self):
        return u"Invoice<{}>".format(self.id)

    def add_sales_entry(self, description, price, account, action='', notes='',
                        quantity_num=0, quantity_denom=1, price_num=None, price_denom=None,
                        discount_num=0, discount_denom=1, disc_type='PERCENT', disc_how='PRETAX',
                        taxable=1, taxincluded=0, taxtable=None,
                        ):
        """Add a line item to a sales invoice
        Either use the price or the price_num, price_denom notation for setting the price.
        """
        if price_denom is None:
            # Assume is to allow pricing in 1 ppm of currency or 1/10000 of a (cent, pence, ...)
            price_denom = 1000000
        if price_num is None:
            assert price is not None
            price_num = int(price * price_denom)

        ent = Entry(date=self.date_opened,
                    date_entered=datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
                    description=description,
                    action=action,
                    notes=notes,
                    quantity_num=quantity_num,
                    quantity_denom=quantity_denom,
                    i_acct=account,
                    i_price_num=price_num,
                    i_price_denom=price_denom,
                    i_discount_num=discount_num,
                    i_discount_denom=discount_denom,
                    invoice=self.guid,
                    i_disc_type=disc_type,
                    i_disc_how=disc_how,
                    i_taxable=taxable,
                    i_taxincluded=taxincluded,
                    i_taxtable=taxtable)


class Job(DeclarativeBaseGuid):
    __tablename__ = 'jobs'

    __table_args__ = {}

    # column definitions
    id = Column('id', VARCHAR(length=2048), nullable=False)
    name = Column('name', VARCHAR(length=2048), nullable=False)
    reference = Column('reference', VARCHAR(length=2048), nullable=False)
    active = Column('active', INTEGER(), nullable=False)
    owner_type = Column('owner_type', INTEGER())
    owner_guid = Column('owner_guid', VARCHAR(length=32))

    # relation definitions
    # todo: owner_guid/type links to Vendor or Customer

    # This class exists in code but not in the GUI (to confirm?)


class Order(DeclarativeBaseGuid):
    __tablename__ = 'orders'

    __table_args__ = {}

    # column definitions
    id = Column('id', VARCHAR(length=2048), nullable=False)
    notes = Column('notes', VARCHAR(length=2048), nullable=False)
    reference = Column('reference', VARCHAR(length=2048), nullable=False)
    active = Column('active', INTEGER(), nullable=False)

    date_opened = Column('date_opened', _DateTime(), nullable=False)
    date_closed = Column('date_closed', _DateTime(), nullable=False)
    owner_type = Column('owner_type', INTEGER(), nullable=False)
    owner_guid = Column('owner_guid', VARCHAR(length=32), nullable=False)

    # relation definitions
    # todo: owner_guid/type links to Vendor or Customer
    entries = relation('Entry',
                       back_populates='order',
                       cascade='all, delete-orphan',
                       collection_class=CallableList,
                       )
