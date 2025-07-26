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


class QuotationGenerator:
    """Generate PDF quotations with dynamic content"""

    def __init__(self, template_dir='template'):
        """Initialize the generator with template directory"""
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def number_to_words(self, num):
        """Convert number to words in Indian format"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
                 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']

        # Indian numbering system units
        units = ['', 'Thousand', 'Lakh', 'Crore']

        if num == 0:
            return 'Zero'

        # Convert to string
        num_str = str(int(num))

        # Handle up to 9,99,99,999 (under 10 crore)
        if len(num_str) > 8:
            return "Number too large"

        # Indian format grouping
        groups = []

        # First group of 3 (ones, tens, hundreds)
        if len(num_str) >= 3:
            groups.append(num_str[-3:])
            num_str = num_str[:-3]
        else:
            groups.append(num_str)
            num_str = ''

        # Subsequent groups of 2
        while num_str:
            if len(num_str) >= 2:
                groups.append(num_str[-2:])
                num_str = num_str[:-2]
            else:
                groups.append(num_str)
                num_str = ''

        # Convert each group to words
        result = []
        for i, group in enumerate(groups):
            if int(group) == 0:
                continue

            group_words = []
            group_int = int(group)

            # Handle hundreds
            if len(group) == 3:
                hundreds = group_int // 100
                if hundreds > 0:
                    group_words.append(ones[hundreds] + ' Hundred')
                group_int = group_int % 100

            # Handle tens and ones
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

            # Add unit
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

        # Round off calculation
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

            # Logo path
            'logo_path': '../static/logo.png',

            # Watermark settings (optional)
            'show_watermark': True,  # Set to False to hide watermark
            'watermark_opacity': 0.2,  # Adjust opacity (0.0 to 1.0)

            # Company details
            'company_name': 'Envacare Laboratory LLP',
            'company_address': 'Shop No-51,52, Shree Sharan Business Park<br>Sanand Changodar GIDC<br>Ahmedabad-382213',
            'company_gstin': '24AAKFE7625D1ZL',
            'company_email': 'info@envacarelaboratoryllp.in',

            # Buyer details
            'buyer_name': 'METTUBE COPPER INDIA PRIVATE LIMITED',
            'buyer_address': 'Plot No.SM-9/5, Sanand - II Industrial Estate,<br>Village Bol, Taluka Sanand, District Ahmedabad,<br>Gujarat - 382170',
            'buyer_gstin': '24AAQCM2685Q1ZK',
            'buyer_email': 'rajagopal@mettubeindia.com',

            # Bank details
            'bank_account_name': 'ENVACARE LABORATORY LLP',
            'bank_name': 'BANK OF BARODA',
            'bank_account_number': '03200200001364',
            'bank_ifsc': 'BARBOAMBAWA',
            'pan_number': 'AAKFE7625D',

            # Contact details
            'phone': '+91 99240 85245',
            'email': 'info@envacarelaboratoryllp.in',
            'website': 'www.envacarelaboratoryllp.in',
            'address_line1': 'Shop No.51–52, Shree Sharan Business Park,',
            'address_line2': 'Changodar, Sanand, Ahmedabad,',
            'address_line3': 'Gujarat – 382213',

            # Items
            'items': [
                {'product': 'Ambient sample Analysis of Work Place Air Quality',
                 'unit_price': 12000, 'quantity': 4, 'amount': 48000},
                {'product': 'Water Quality Testing - Physical & Chemical Parameters',
                 'unit_price': 8500, 'quantity': 6, 'amount': 51000},
                {'product': 'Soil Contamination Analysis',
                 'unit_price': 15000, 'quantity': 3, 'amount': 45000},
                {'product': 'Noise Level Monitoring & Assessment',
                 'unit_price': 6000, 'quantity': 8, 'amount': 48000},
                {'product': 'Indoor Air Quality Assessment',
                 'unit_price': 10000, 'quantity': 5, 'amount': 50000},
                {'product': 'Stack Emission Monitoring',
                 'unit_price': 18000, 'quantity': 2, 'amount': 36000},
                {'product': 'Hazardous Waste Characterization',
                 'unit_price': 22000, 'quantity': 3, 'amount': 66000},
                {'product': 'Environmental Impact Assessment Support',
                 'unit_price': 25000, 'quantity': 2, 'amount': 50000},
            ],

            # Additional fields
            'unit_label': 'Unit',  # Can be 'Sample', 'Unit', etc.
            'company_name_short': 'Envacare laboratory LLP',

            # Terms and conditions
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
        # Use default data if none provided
        if data is None:
            data = self.get_default_data()

        # Calculate totals
        totals = self.calculate_totals(data['items'])
        data.update(totals)

        # Load and render template
        template = self.env.get_template('quotation.html')

        # Add built-in functions to template context
        template.globals['abs'] = abs

        html_content = template.render(**data)

        # Set base URL to the file system root for proper image loading
        base_url = 'pdf_converter_files'

        # Generate PDF
        HTML(string=html_content, base_url=base_url).write_pdf(
            output_filename,
            stylesheets=[],  # CSS is embedded in HTML
        )

        return output_filename

    # def generate_test_multipage(self, output_filename='quotation_multipage.pdf'):
    #     """Generate a multi-page quotation for testing"""
    #     data = self.get_default_data()
    #
    #     # Generate many items to test pagination
    #     test_items = []
    #     products = [
    #         'Air Quality Monitoring - Location {}',
    #         'Water Sample Analysis - Point {}',
    #         'Soil Testing - Sample {}',
    #         'Noise Assessment - Area {}',
    #         'Environmental Audit - Section {}',
    #         'Emission Testing - Stack {}',
    #         'Waste Analysis - Batch {}',
    #         'Contamination Study - Site {}',
    #     ]
    #
    #     # Create 40 items to ensure multi-page
    #     for i in range(40):
    #         product_template = products[i % len(products)]
    #         test_items.append({
    #             'product': product_template.format(i + 1),
    #             'unit_price': 5000 + (i * 500),
    #             'quantity': 2 + (i % 5),
    #             'amount': (5000 + (i * 500)) * (2 + (i % 5))
    #         })
    #
    #     data['items'] = test_items
    #     data['quotation_number'] = 'EC/2425/QU/TEST-MULTIPAGE'
    #
    #     return self.generate_pdf(data, output_filename)


def main():
    """Main function to demonstrate usage"""
    # Create template directory if it doesn't exist
    os.makedirs('template', exist_ok=True)

    # Initialize generator
    generator = QuotationGenerator()

    # Generate standard quotation
    # print("Generating standard quotation...")
    # pdf_file = generator.generate_pdf(output_filename='../envacare_quotation.pdf')
    # print(f"✅ Generated: {pdf_file}")

    # Generate multi-page quotation
    # print("\nGenerating multi-page test quotation...")
    # multipage_file = generator.generate_test_multipage()
    # print(f"✅ Generated: {multipage_file}")

    # Example with custom data
    print("\nGenerating custom quotation...")
    custom_data = generator.get_default_data()
    custom_data['quotation_number'] = 'EC/2425/QU/CUSTOM-001'
    custom_data['buyer_name'] = 'ACME Corporation Ltd.'
    custom_data['buyer_address'] = "Address"
    custom_data['buyer_gstin'] = "24AAQCM2685Q1ZK"
    custom_data['buyer_email'] = "r@gmail.com"
    custom_data['items'] = [
        {'product': 'Environmental Compliance Audit',
         'unit_price': 50000, 'quantity': 1, 'amount': 50000},
        {'product': 'Annual Air Quality Monitoring',
         'unit_price': 120000, 'quantity': 1, 'amount': 120000},
        {'product': 'Water Treatment Plant Assessment',
         'unit_price': 75000, 'quantity': 1, 'amount': 75000},
    ]

    custom_file = generator.generate_pdf(custom_data, 'custom_quotation.pdf')
    print(f"✅ Generated: {custom_file}")


if __name__ == "__main__":
    main()