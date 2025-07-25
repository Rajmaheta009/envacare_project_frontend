from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def quotation_pdf_maker(c_id,q_id):
    # Jinja2 environment
    env = Environment(loader=FileSystemLoader('template'))
    template = env.get_template('quotation.html')

    # If no variables needed, just render as-is
    html_rendered = template.render()

    HTML(string=html_rendered, base_url='.').write_pdf('envacare_quotation_with_watermark.pdf')
    print("✅ PDF generated: envacare_quotation_with_watermark.pdf")
