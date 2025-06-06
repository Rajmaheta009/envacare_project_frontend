from weasyprint import HTML, CSS
from jinja2 import Template
from datetime import date

# HTML Template (fixed version with terms section positioned correctly)
template_str = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <title>Quotation Format</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        @page {
            margin: 0;
        }
        
        html,
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        header,
        footer {
            position: fixed;
            left: 0;
            right: 0;
            background: #fff;
            z-index: 999;
        }
        
        header {
            top: 0;
            padding: 20px;
            text-align: center;
            height: 100px;
        }
        
        footer {
            bottom: 0;
            padding: 0px 40px 0;
            border-top: 3px solid #003d1a;
            height: 100px;
        }
        
        .top-logo {
            position: absolute;
            top: 10px;
            left: 30px;
        }
        
        .top-logo img {
            width: 200px;
            opacity: 0.8;
        }
        
        .content {
            padding: 130px 50px 130px;
        }
        
        .quotation-header {
            display: flex;
            justify-content: space-between;
            font-size: 15px;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            background: transparent;
        }
        
        th,
        td {
            border: 1px solid #000;
            padding: 6px;
            vertical-align: top;
            text-align: left;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        
        thead {
            display: table-header-group;
        }
        
        table,
        tr,
        td,
        th {
            page-break-inside: avoid !important;
            break-inside: avoid;
        }
        
        .terms-container {
            display: flex;
            border: 1px solid #000;
            margin-top: 25px;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            page-break-before: auto !important;
        }
        
        .terms-left,
        .terms-right {
            padding: 15px;
            text-align: center;
            /*break-inside: avoid;
            page-break-inside: avoid;*/
        }
        
        .terms-left {
            width: 70%;
            border-right: 1px solid #000;
        }
        
        .terms-left b {
            display: block;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .terms-left p {
            margin: 5px 0;
        }
        
        .terms-right {
            width: 30%;
        }
        
        .terms-right img {
            max-width: 70%;
        }
        
        .signature-label {
            font-weight: bold;
            margin-top: 10px;
        }
        
        .footer-content {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            border-bottom: 3px solid #003d1a;
            padding-bottom: 15px;
        }
        
        .footer-column {
            flex: 1;
            min-width: 50px;
        }
        
        .footer-header {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            color: #003d1a;
        }
        
        .footer-header img {
            width: 20px;
            margin-right: 8px;
        }
        
        .footer-text {
            margin-left: 28px;
            color: #999;
            line-height: 1.4;
        }
        
        .footer-accreditation {
            background-color: #003d1a;
            color: white;
            text-align: center;
            padding: 8px;
            border-radius: 0 0 25px 25px;
            font-weight: bold;
            font-size: 14px;
            margin-top: 10px;
        }
        
        @media print {
            body {
                margin-bottom: 150px;
            }
            header,
            footer {
                position: fixed;
            }
            .content {
                padding-top: 130px;
                padding-bottom: 130px;
            }
            table,
            tr,
            td,
            th {
                page-break-inside: avoid !important;
                break-inside: avoid;
            }
            .terms-container {
                page-break-before: always;
            }
        }
    </style>
</head>

<body>
    <header>
        <div class="top-logo">
            <img src="static/logo.png" alt="Logo">
        </div>
        <h4 style="margin: 0; padding-top: 10px; font-size: 45px">Quotation</h4>
    </header>

    <div class="content">
        <div class="quotation-header">
            <div><strong>Quo. No.:</strong> EC/2425/QU/017</div>
            <div><strong>Dated:</strong> 23-09-2024</div>
        </div>

        <table>
            <tr>
                <th>Envacare Laboratory LLP</th>
                <th>Buyer</th>
            </tr>
            <tr>
                <td>
                    Shop No-51,52, Shree Sharan Business Park<br> Sanand Changodar GIDC<br> Ahmedabad-382213
                    <br><br>
                    <strong>GSTIN/UIN:</strong> 24AAKFE7625D1ZL<br>
                    <strong>Email:</strong> info@envacarelaboratoryllp.in
                </td>
                <td>
                    <strong>METTUBE COPPER INDIA PRIVATE LIMITED</strong><br> Plot No.SM-9/5, Sanand - II Industrial Estate, Village Bol,<br> Taluka Sanand, District Ahmedabad, Gujarat - 382170<br><br>
                    <strong>GSTIN/UIN:</strong> 24AAQCM2685Q1ZK<br>
                    <strong>Email:</strong> rajagopal@mettubeindia.com
                </td>
            </tr>
        </table>

        <table class="mt-4">
            <thead>
                <tr>
                    <th>Sr. No.</th>
                    <th>Product</th>
                    <th>Charges Per Unit</th>
                    <th>Quantity</th>
                    <th>Amount (Rs.)</th>
                </tr>
            </thead>
            <tbody id="quotation-body">
                <!-- You can insert rows dynamically here -->
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Ambient sample Analysis of Work Place Air Quality</td>
                    <td>12000</td>
                    <td>4</td>
                    <td>48000</td>
                </tr>
            </tbody>
            <tr>
                <td colspan="2">
                    <strong>Bank Details</strong><br><br>
                    <strong>A/c Name:</strong> ENVACARE LABORATORY LLP<br>
                    <strong>Bank:</strong> BANK OF BARODA<br>
                    <strong>A/c No.:</strong> 03200200001364<br>
                    <strong>IFSC:</strong> BARBOAMBAWA<br>
                    <strong>PAN:</strong> AAKFE7625D
                </td>
                <td colspan="3">
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Total</strong></td>
                            <td>1164200</td>
                        </tr>
                        <tr>
                            <td>SGST @9%</td>
                            <td>104778</td>
                        </tr>
                        <tr>
                            <td>CGST @9%</td>
                            <td>104778</td>
                        </tr>
                        <tr>
                            <td>Round Off</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td><strong>Balance Due</strong></td>
                            <td><strong>1373756</strong></td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td colspan="5"><strong>In Words:</strong> Rupees thirteen lakh seventy-three thousand seven hundred fifty-six only</td>
            </tr>
        </table>

        <!-- <div style="page-break-inside: avoid; break-inside: avoid;"> -->
        <div class="terms-container">
            <div class="terms-left">
                <b>Terms & Conditions</b>
                <p><strong>Delivery Term:</strong> 15 days after monitoring</p>
                <p><strong>Terms of Payment:</strong> Immediate upon report submission</p>
                <p><strong>Taxes:</strong> 18% GST</p>
                <p><strong>Jurisdiction:</strong> Ahmedabad courts</p>
                <p><strong>Validity:</strong> 30 days (extension requires written confirmation)</p>
            </div>
            <div class="terms-right">
                <p><strong>For Envacare Laboratory LLP</strong></p>
                <img src="static/img.png" alt="Stamp">
                <div class="signature-label">Authorized Signature</div>
            </div>
        </div>
    </div>
    <!-- </div> -->

    <footer>
        <div class="footer-content">
            <div class="footer-column">
                <div class="footer-header">
                    <img src="https://cdn-icons-png.flaticon.com/512/3670/3670051.png" alt="Phone Icon">
                    <strong>Phone</strong>
                </div>
                <div class="footer-text">+91 99240 85245</div>
            </div>
            <div class="footer-column">
                <div class="footer-header">
                    <img src="https://cdn-icons-png.flaticon.com/512/561/561127.png" alt="Email Icon">
                    <strong>Email & Website</strong>
                </div>
                <div class="footer-text">info@envacarelaboratoryllp.in<br>www.envacarelaboratoryllp.in</div>
            </div>
            <div class="footer-column address-column">
                <div class="footer-header">
                    <img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="Address Icon">
                    <strong>Address</strong>
                </div>
                <div class="footer-text">Shop No.51–52, Shree Sharan Business Park,Changodar, Sanand, Ahmedabad,<br>Gujarat – 382213</div>
            </div>
        </div>
        <div class="footer-accreditation">(NABL ACCREDITATION LABORATORY)</div>
    </footer>
</body>

</html>
"""

# Render HTML
template = Template(template_str)
html_out = template.render()

# Generate PDF
pdf_path = "envacare_quotation.pdf"
HTML(string=html_out, base_url=".").write_pdf(pdf_path)
