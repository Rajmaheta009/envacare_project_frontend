from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import date

env = Environment(loader=FileSystemLoader('template'))
template = env.get_template('quotation.html')
html = template.render(
    # static or dynamic data...
)
HTML(string=html, base_url='.').write_pdf('envacare_quotation_with_watermark.pdf')
