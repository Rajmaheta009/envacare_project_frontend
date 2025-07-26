#!/usr/bin/env python3
"""
Quotation PDF Generator
Generates A4-sized PDF quotations with dynamic content using Jinja2 and WeasyPrint
"""

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from datetime import datetime
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# Set up API endpoints
API_BASE_URL = os.getenv('API_BASE_URL')
CUSTOMER_API = f"{API_BASE_URL}/customer_request/"
PARAMETER_URL = f"{API_BASE_URL}/parameter"


class QuotationGenerator:
    """Generate PDF quotations with dynamic content"""

    def __init__(self, template_dir='pdf_converter_files/template'):
        """Initialize the generator with template directory"""
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def number_to_words(self, num):
        """Convert number to words in Indian format"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
                 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        units = ['', 'Thousand', 'Lakh', 'Crore']

        if num == 0:
            return 'Zero'

        num_str = str(int(num))
        if len(num_str) > 8:
            return "Number too large"

        groups = []
        if len(num_str) >= 3:
            groups.append(num_str[-3:])
            num_str = num_str[:-3]
        else:
            groups.append(num_str)
            num_str = ''

        while num_str:
            if len(num_str) >= 2:
                groups.append(num_str[-2:])
                num_str = num_str[:-2]
            else:
                groups.append(num_str)
                num_str = ''

        result = []
        for i, group in enumerate(groups):
            if int(group) == 0:
                continue
            group_words = []
            group_int = int(group)
            if len(group) == 3:
                hundreds = group_int // 100
                if hundreds > 0:
                    group_words.append(ones[hundreds] + ' Hundred')
                group_int = group_int % 100

            if group_int >= 20:
                tens_digit = group_int // 10
                ones_digit = group_int % 10
                group_words.append(tens[tens_digit])
                if ones_digit > 0:
                    group_words.append(ones[ones_digit])
            elif group_int >= 10:
                group_words.append(teens[group_int - 10])
            elif group_int > 0:
                group_words.append(ones[group_int])

            if i > 0 and group_words:
                group_words.append(units[i])

            if group_words:
                result.insert(0, ' '.join(group_words))

        return ' '.join(result)

    def format_amount_in_words(self, amount):
        """Format amount in words with rupees and paise"""
        rupees = int(amount)
        paise = int(round((amount - rupees) * 100))

        words = "Rupees " + self.number_to_words(rupees)
        if paise > 0:
            words += " and " + self.number_to_words(paise) + " Paise"
        words += " Only"
        return words

    def calculate_totals(self, items, sgst_rate=9, cgst_rate=9):
        """Calculate subtotal, taxes, and total"""
        subtotal = sum(item['amount'] for item in items)
        sgst_amount = round(subtotal * sgst_rate / 100, 1)
        cgst_amount = round(subtotal * cgst_rate / 100, 1)
        total_with_tax = subtotal + sgst_amount + cgst_amount
        total_amount = round(total_with_tax)
        round_off = round(total_amount - total_with_tax, 1)

        return {
            'subtotal': int(subtotal),
            'sgst_rate': sgst_rate,
            'sgst_amount': sgst_amount,
            'cgst_rate': cgst_rate,
            'cgst_amount': cgst_amount,
            'round_off': round_off,
            'total_amount': int(total_amount),
            'amount_in_words': self.format_amount_in_words(total_amount)
        }

    def get_default_data(self):
        """Get default quotation data"""
        return {
            'quotation_number': 'EC/2425/QU/017',
            'date': datetime.now().strftime('%d-%m-%Y'),
            'logo_path': '../static/logo.png',
            'show_watermark': True,
            'watermark_opacity': 0.2,
            'company_name': 'Envacare Laboratory LLP',
            'company_address': 'Shop No-51,52, Shree Sharan Business Park<br>Sanand Changodar GIDC<br>Ahmedabad-382213',
            'company_gstin': '24AAKFE7625D1ZL',
            'company_email': 'info@envacarelaboratoryllp.in',
            'buyer_name': '',
            'buyer_address': '',
            'buyer_gstin': '',
            'buyer_email': '',
            'bank_account_name': 'ENVACARE LABORATORY LLP',
            'bank_name': 'BANK OF BARODA',
            'bank_account_number': '03200200001364',
            'bank_ifsc': 'BARBOAMBAWA',
            'pan_number': 'AAKFE7625D',
            'phone': '+91 99240 85245',
            'email': 'info@envacarelaboratoryllp.in',
            'website': 'www.envacarelaboratoryllp.in',
            'address_line1': 'Shop No.51–52, Shree Sharan Business Park,',
            'address_line2': 'Changodar, Sanand, Ahmedabad,',
            'address_line3': 'Gujarat – 382213',
            'unit_label': 'Unit',
            'company_name_short': 'Envacare laboratory LLP',
            'items': [],
            'terms_conditions': [
                {'label': 'Delivery Term', 'value': '15 days after monitoring'},
                {'label': 'Terms of Payment', 'value': 'Immediate upon report submission'},
                {'label': 'Taxes', 'value': '18% GST (SGST 9% + CGST 9%)'},
                {'label': 'Jurisdiction', 'value': 'Ahmedabad courts'},
                {'label': 'Validity', 'value': '30 days from quote date'},
                {'label': 'Sample Collection', 'value': 'As per standard protocols'},
                {'label': 'Reporting', 'value': 'Digital and hard copy reports provided'},
            ]
        }

    def generate_pdf(self, data=None, output_filename='quotation.pdf'):
        """Generate PDF quotation"""
        if data is None:
            data = self.get_default_data()
        totals = self.calculate_totals(data['items'])
        data.update(totals)
        template = self.env.get_template('quotation.html')
        template.globals['abs'] = abs
        html_content = template.render(**data)
        base_url = os.path.abspath('.')
        HTML(string=html_content, base_url=base_url).write_pdf(output_filename)
        return output_filename


def fetch_customer_by_id(customer_id):
    try:
        response = requests.get(f"{CUSTOMER_API}{customer_id}")
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching customer details: {e}")
        return None


def fetch_parameter_name_and_price_by_id(pid):
    try:
        response = requests.get(f"{PARAMETER_URL}/p_id/{pid}")
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching parameter: {e}")
        return None

def main(c_id, parameter_info):
    """Main function to demonstrate usage"""
    # Setup
    os.makedirs('template', exist_ok=True)
    generator = QuotationGenerator()

    print("\nGenerating custom quotation...")

    customer_id = c_id
    customer_info = fetch_customer_by_id(customer_id)

    # Extract parameter IDs and quantities from the passed parameter_info
    parameter_ids_and_qty = [
        {'parameter_id': param['parameter_id'], 'quantity': param['quantity']}
        for param in parameter_info
    ]

    # Fetch detailed parameter data and merge quantity into each
    full_parameter_info = []
    for param in parameter_ids_and_qty:
        param_data = fetch_parameter_name_and_price_by_id(param['parameter_id'])
        if param_data:
            param_data = param_data[0]  # FIX: Get the first dictionary in the list
            param_data['quantity'] = param['quantity']
            full_parameter_info.append(param_data)

    custom_data = generator.get_default_data()
    custom_data['quotation_number'] = 'EC/2425/QU/CUSTOM-001'

    if not customer_info:
        custom_data['buyer_name'] = 'raj'
        custom_data['buyer_address'] = "Address"
        custom_data['buyer_gstin'] = "24AAQCM2685Q1ZK"
        custom_data['buyer_email'] = "r@gmail.com"
    else:
        custom_data['buyer_name'] = customer_info.get('name', 'N/A')
        custom_data['buyer_address'] = customer_info.get('address', 'N/A')
        custom_data['buyer_gstin'] = "24AAQCM2685Q1ZK"
        custom_data['buyer_email'] = customer_info.get('email', 'N/A')

    if not full_parameter_info:
        custom_data['items'] = [
            {'product': 'Environmental Compliance Audit',
             'unit_price': 50000, 'quantity': 1, 'amount': 50000},
            {'product': 'Annual Air Quality Monitoring',
             'unit_price': 120000, 'quantity': 1, 'amount': 120000},
            {'product': 'Water Treatment Plant Assessment',
             'unit_price': 75000, 'quantity': 1, 'amount': 75000},
        ]
    else:
        custom_data['items'] = [
            {
                'product': p['name'],
                'unit_price': p['price'],
                'quantity': p['quantity'],
                'amount': p['price'] * p['quantity']
            }
            for p in full_parameter_info if p is not None
        ]

    custom_file = generator.generate_pdf(custom_data, 'custom_quotation.pdf')
    print(f"✅ Generated: {custom_file}")



if __name__ == "__main__":
    main()
