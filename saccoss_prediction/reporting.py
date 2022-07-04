from pathlib import Path
from flask import Blueprint, make_response, render_template, request, send_file, send_from_directory

from saccoss_prediction.models import Evaluations, Saccos
import pdfkit


reporting = Blueprint("reporting", __name__)


@reporting.context_processor
def utility_processor():
    def format_performnce(key):
        if key == 'DP':
            result = 'Doubtful Performance'
        elif key == 'UP':
            result = 'Under Performance'
        elif key == 'AP':
            result = 'Avarage Performance'
        elif key == 'SP':
            result = 'Superior Performance'
        else:
            result = 'Outstanding Performance'
        return result
    return dict(format_performnce=format_performnce)


@reporting.route("/report/<int:report_id>")
def report(report_id):
    evaluation_data = Evaluations.query.get_or_404(report_id)
    saccoss_data = Saccos.query.get_or_404(evaluation_data.saccoss_id)
    rendered = render_template(
        "report.html", saccos=saccoss_data, evaluation=evaluation_data)

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '1.0in',
        'margin-bottom': '1.0in',
        'margin-left': '1.0in',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(rendered, False, options=options)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=output.pdf"
    return response
