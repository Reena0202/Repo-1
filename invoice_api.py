from enum import IntEnum
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

app = FastAPI()

all_invoices = pd.read_excel("/Users/Reenu/Desktop/Magipedia/Artificial_Intelligence/Invoices.xlsx")
all_invoices = all_invoices.replace([np.inf, -np.inf], np.nan)
all_invoices = all_invoices.fillna("")

@app.get('/invoices')
def get_invoices():
    return all_invoices.to_dict(orient="records")

@app.get('/invoiceid/{invoice_id}')
def get_invoiceid(invoice_id:int):
    data = all_invoices.to_dict(orient="records")

    if invoice_id:
        for row in data:
            if int(row['invoice_id']) == invoice_id:
                return row
        return {'error' : 'invalid invoice_id'}
    return {'error' : 'enter invoice_id'}

@app.get('/invoicegstin/{gstin}')
def get_invoicegstin(gstin:str):
    data = all_invoices.to_dict(orient="records")

    if gstin:
        for row in data:
            if str(row['gstin']) == gstin:
                return row
        return {'error' : 'no record for this gstin'}

@app.get('/invoicegstins')
def get_invoicegstins():
    data = all_invoices.to_dict(orient="records")

    new = []
    for row in data:
            if str(row['gstin']) != 'NIL':
                new.append(row)
    return new

@app.post('/invoices')
def post_invoice(invoice: dict):
    global all_invoices
    data = all_invoices.to_dict(orient="records")

    invoice_id = invoice.get('invoice_id')
    if not invoice_id:
        invoice_id = str(max([int(row['invoice_id']) for row in data if str(row['invoice_id']).isdigit()], default=0) + 1)

    new_invoice = {
        'invoice_id' : invoice_id,
        'customer_name' : invoice['customer_name'],
        'gst_treatment' : invoice['gst_treatment'],
        'gstin' : invoice['gstin'],
        'place_of_supply' : invoice['place_of_supply'],
        'country' : invoice['country']
    }
    new_allinvoice = pd.DataFrame([new_invoice])
    all_invoices = pd.concat([all_invoices, new_allinvoice], ignore_index=True)

    excel_path = "/Users/Reenu/Desktop/Magipedia/Artificial_Intelligence/Invoices.xlsx"
    all_invoices.to_excel(excel_path, index=False)

    return {"message" : "Invoice added successfully", "invoice": new_invoice}

@app.put('/invoiceupdate/{invoice_id}')
def put_invoices(invoice_id: str, invoice : dict):
    global all_invoices
    data = all_invoices.to_dict(orient="records")

    for i, row in enumerate(data):
        if str(row["invoice_id"]) == str(invoice_id):
            data[i].update(invoice)
            all_invoices = pd.DataFrame(data)
            excel_path = "/Users/Reenu/Desktop/Magipedia/Artificial_Intelligence/Invoices.xlsx"
            all_invoices.to_excel(excel_path, index=False)

            return {"message":"Invoice updated", "invoice":data[i]}
    return JSONResponse(status_code=404, content="message : Invoice ID not found")

@app.delete('/invoicedelete/{invoice_id}')
def delete_invoice(invoice_id : str):
    global all_invoices
    data = all_invoices.to_dict(orient="records")

    for i, row in enumerate(data):
        if str(row["invoice_id"]) == str(invoice_id):
            deleted_invoice = data[i]
            del data[i]
            all_invoices = pd.DataFrame(data)

            excel_path = "/Users/Reenu/Desktop/Magipedia/Artificial_Intelligence/Invoices.xlsx"
            all_invoices.to_excel(excel_path, index=False)

            return {"message": "Invoice deleted", "invoice": deleted_invoice}
    return JSONResponse(status_code=404, content="message : invalid invoice_id")








