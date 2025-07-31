import os
from pyrfc import Connection, ConnectionParameters

def po_getdetail(sappconn: Connection, po_number: str):
    """Fetches purchase order details from SAP."""
    result = sappconn.call(
        'BAPI_PO_GETDETAIL',
        PURCHASEORDER=po_number,
        ITEMS='X',
        SCHEDULES='X',
        HISTORY='X',
    )
    return result