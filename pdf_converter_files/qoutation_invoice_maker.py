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
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">

    <style>
        @page {
            margin: 0;
        }

        html, body {
            margin-bottom: 5%;
            padding: 0;
            height: 100%;
            background: url('frontend/static/pdf_back.png') no-repeat center center;
            background-size: cover;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .container {
            position: relative;
            z-index: 1;
            top:6%;
            margin: auto;
            # height:800px;
            padding: 30px 50px;
        }

        .top-logo {
            position: absolute;
            top: 20px;
            left: 30px;
        }

        .top-logo img {
            width: 100px;
            opacity: 0.8;
        }

        .quotation-header {
            display: flex;
            justify-content: space-between;
            font-size: 15px;
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            background: transparent;
        }

        tbody tr {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }

        table, tr, td, th {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }

        th, td {
            border: 1px solid #000;
            padding: 5px;
            vertical-align: top;
            text-align: left;
        }

        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }

        .terms-container {
            display: flex;
            border: 1px solid #000;
            page-break-inside: avoid;
            break-inside: avoid;
            orphans: 3;
            widows: 3;
            margin-top: 20px;
        }

        .terms-left,
        .terms-right {
            padding: 15px;
            text-align: center;
        }

        .terms-left {
            width: 70%;
            border-right: 1px solid #000;
        }

        .terms-left b {
            display: block;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .terms-left p {
            margin: 5px 0;
        }

        .terms-right {
            width: 30%;
            # text-align: center;
        }

        .terms-right img {
            max-width: 70%;
        }

        .signature-label {
            font-weight: bold;
        }

        .table-section {
            page-break-inside: avoid;
            break-inside: avoid;
            overflow: hidden;
        }

        .bank-details,
        .footer-text {
            font-size: 14px;
            margin-top: 20px;
        }

        .content-wrapper {
            page-break-inside: avoid;
            break-inside: avoid;
        }
    </style>
</head>

<body>
    <div class="container" id="quotation">
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
                    Shop No-51,52, Shree Sharan Business Park<br />
                    Sanand Changodar GIDC<br />
                    Ahmedabad-382213<br /><br />
                    <strong>GSTIN/UIN:</strong> 24AAKFE7625D1ZL<br />
                    <strong>E-Mail:</strong> info@envacarelaboratoryllp.in
                </td>
                <td>
                    <strong>METTUBE COPPER INDIA PRIVATE LIMITED</strong><br />
                    Plot No.SM-9/5, Sanand - II Industrial Estate, Village Bol, Taluka Sanand,<br />
                    District Ahmedabad, Gujarat - 382170<br /><br />
                    <strong>GSTIN/UIN:</strong> 24AAQCM2685Q1ZK<br />
                    <strong>E-Mail:</strong> rajagopal@mettubeindia.com
                </td>
            </tr>
        </table>

        <div class="content-wrapper">
            <div class="table-section">
                <table>
                    <thead>
                        <tr>
                            <th>Sr. No.</th>
                            <th>Product</th>
                            <th>Charges Per Unit</th>
                            <th>Quantity</th>
                            <th>Amount (Rs.)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>Ambient sample Analysis of Work Place Air Quality</td>
                            <td>12000</td>
                            <td>4</td>
                            <td>48000</td>
                        </tr>
                        <tr>
                            <td>2</td>
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
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td><strong>TOTAL</strong></td>
                                    <td>1164200</td>
                                </tr>
                                <tr>
                                    <td>SGST @9% Tax</td>
                                    <td>104778</td>
                                </tr>
                                <tr>
                                    <td>CGST @9% Tax</td>
                                    <td>104778</td>
                                </tr>
                                <tr>
                                    <td>Balance round off (+)</td>
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
                        <td colspan="5"><strong>In Words:</strong> Rupees thirteen lakh seventy-three thousand seven hundred fifty-Six Only</td>
                    </tr>
                </table>
            </div>

            <div class="terms-container">
                <div class="terms-left">
                    <b>Terms & Conditions</b>
                    <p><strong>Delivery Term:</strong> 15 days after monitoring</p>
                    <p><strong>Terms of Payment:</strong> Analysis charges will be immediate against submission of reports.</p>
                    <p><strong>Taxes & Duties:</strong> 18% GST</p>
                    <p><strong>Jurisdiction:</strong> Subjected to the jurisdiction of Ahmedabad (India) courts.</p>
                    <p><strong>Validity:</strong> Quotation is valid for 30 days. Extension requires written confirmation.</p>
                </div>
                <div class="terms-right">
                    <p><strong>For Envacare Laboratory LLP</strong></p>
                    <img src="frontend/static/img.png" alt="Stamp" />
                    <div class="signature-label">Authorized Signature</div>
                </div>
            </div>
        </div>
    </div>
</body>

</html>
"""

# Render HTML
template = Template(template_str)
html_out = template.render()

# Generate PDF
pdf_path = "envacare_quotation.pdf"
HTML(string=html_out, base_url=".").write_pdf(pdf_path)
