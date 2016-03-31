# coding=utf-8
from __future__ import unicode_literals

from decimal import Decimal

from test_helper import db_sqlite_uri, db_sqlite, new_book, new_book_USD, book_uri, book_people
# dummy line to avoid removing unused symbols
from piecash import Address, Employee, Account, Invoice, Entry
from piecash.business import Taxtable, TaxtableEntry

a = db_sqlite_uri, db_sqlite, new_book, new_book_USD, book_uri, book_people

#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class TestInvoice_create_Invoice(object):
    """
    At a late stage this should perhaps be parameterised like business person
    to deal with Purchase and Sales Invoices and perhaps credit notes.
    """

    def test_create_invoice_noid_nobook(self, book_people):
        EUR = book_people.commodities(namespace="CURRENCY")
        customer = book_people.customers(id='000001')
        inv = Invoice(EUR, 2, customer.guid, id='TestInvoice')

        # flushing should not set the id as person not added to book
        book_people.flush()

        # adding the person to the book does not per se set the id
        book_people.add(inv)
        # but validation sets the id if still to None
        book_people.validate()
        assert inv.id == "TestInvoice"
        assert len(inv.guid) == 32, 'Guid is |{}|'.format(inv.guid)

        # Now add the entry - line items of the invoice

        sales_account = book_people.accounts(name="asset")


        entry_1 = inv.add_sales_entry('Material', 9.95, sales_account)

        # Then post the entry which will create the transaction and splits

        # Should then be able to use the invoice

