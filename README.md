# Flairspace PDF API

A simple free-deployable PDF generation API for Flairspace Solutions.

## How to use

POST /api/generate

Body:
{
  "templateType": "rent_receipt",
  "data": {
    "tenantName": "Jane Doe",
    "amount": 5000
  }
}

Response:
{
  "pdfUrl": "https://yourapp.onrender.com/files/<uuid>.pdf"
}
