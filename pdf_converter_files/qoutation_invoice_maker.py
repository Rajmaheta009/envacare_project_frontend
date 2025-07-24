from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import date

env = Environment(loader=FileSystemLoader('template'))
template = env.get_template('quotation.html')

html = template.render(
    logo_url='static/logo.png',
    phone_icon_url='static/phone.png',
    email_icon_url='static/email.png',
    address_icon_url='static/address.png',
    phone='+91 99240 85245',
    email='info@envacarelaboratoryllp.in',
    website='www.envacarelaboratoryllp.in',
    quotation_no='EC/2425/QU/017',
    date=date.today().strftime('%d-%m-%Y'),
    seller_name='Envacare Laboratory LLP',
    seller_address='Shop No‑51,52, Shree Sharan Business Park, Changodar, Ahmedabad‑382213',
    seller_gst='24AAKFE7625D1ZL',
    seller_email='info@envacarelaboratoryllp.in',
    buyer_name='METTUBE COPPER INDIA PRIVATE LIMITED',
    buyer_address='Plot No.SM‑9/5, Sanand - II Industrial Estate, Village Bol, Taluka Sanand, District Ahmedabad, Gujarat - 382170',
    buyer_gst='24AAQCM2685Q1ZK',
    buyer_email='rajagopal@mettubeindia.com',
    items=[
        {"product": "Ambient sample Analysis of Work Place Air Quality", "rate": "12000", "quantity": "4", "amount": "48000"},
        # add more items as needed
    ],
    bank={
        "name": "ENVACARE LABORATORY LLP",
        "bank": "BANK OF BARODA",
        "account": "03200200001364",
        "ifsc": "BARBOAMBAWA",
        "pan": "AAKFE7625D"
    },
    totals=[
        {"label": "Total", "value": "1164200"},
        {"label": "SGST @9%", "value": "104778"},
        {"label": "CGST @9%", "value": "104778"},
        {"label": "Round Off", "value": "0"},
        {"label": "Balance Due", "value": "1373756"},
    ],
    in_words='Rupees thirteen lakh seventy-three thousand seven hundred fifty-six only',
    terms=[
        {"title": "Delivery Term", "text": "15 days after monitoring"},
        {"title": "Terms of Payment", "text": "Immediate upon report submission"},
        {"title": "Taxes", "text": "18% GST"},
        {"title": "Jurisdiction", "text": "Ahmedabad courts"},
        {"title": "Validity", "text": "30 days (extension requires written confirmation)"},
    ],
    stamp_url='static/stamp.png',
)

HTML(string=html, base_url='.').write_pdf('envacare_quotation.pdf')
