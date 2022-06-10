from pathlib import Path
from flask import Blueprint, make_response, request, send_file, send_from_directory

from saccoss_prediction import REPORTS_FOLDER
from saccoss_prediction.models import Evaluations
from fpdf import FPDF


reporting = Blueprint("reporting", __name__)


class PDF(FPDF):
    def header(self):
        # Logo
        self.image(REPORTS_FOLDER+'/header-image.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Title', 1, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


def report_title():
    current_saccos_name = 'SACCOS A'
    evaluation_month = 'Mei 31'
    header = f"TAARIFA YA UKAGUZI WA NJE YA MAHALA PA CHAMA " \
        f"(OFF-SITE REPORT) YA CHAMA CHA USHIRIKA WA AKIBA NA " \
        f"MIKOPO CHA {current_saccos_name} KUISHIA TAREHE {evaluation_month }."
    return header


def first_section():
    initial_saccos_name = 'SACCOS HERUFI A'
    current_saccos_name = 'SACCOS A'
    saccos_register_date = "Jan 12"
    certificate_number = 'AZH1229'
    cooperative_act_no = 7
    cooperative_act_year = 1998
    initial_members = 29
    current_members = 347
    male_members = 199
    evaluation_month = 'Mei 31'
    female_members = current_members - male_members
    saccos_residency_title = 'Manispaa'
    saccos_residency_name = 'Manispaa A'
    region = 'Mkoa A'
    services = {
        "kupokea akiba",
        "amana", "hisa za hiyari",
        "huduma za kutoa mikopo kwa Wanachama",
        "uwakala wa mitandao ya simu",
        "uwakala wa bima",
        "na uwakala wa mabenki"
    }
    main_heading = 'SEHEMU YA KWANZA'
    heading = 'UTANGULIZI'
    content = f"Chama cha Ushirika wa Akiba na Mikopo cha {current_saccos_name}, kilisajiliwa " \
        f"tarehe {saccos_register_date} kikiwa na jina la {initial_saccos_name} {services} " \
        f"na kupewa hati yenye usajili Na. {certificate_number} chini ya sheria ya Ushirika " \
        f"Na {cooperative_act_no} ya mwaka {cooperative_act_year}. SACCOS hii ilianza na " \
        f"jumla ya wanachama {initial_members}, na hadi kufikia tarehe {evaluation_month} " \
        f"chama kilikuwa na jumla ya wanachama {current_members} ambapo wanaume ni " \
        f"{male_members}  na wanawake ni {female_members}. Aidha chama hiki kinafanya shughuli " \
        f"zake katika {saccos_residency_title} ya {saccos_residency_name} mkoani {region}, " \
        f"na shughuli za chama hiki kwa ujumla ni pamoja na {services} kwa kuzingatia " \
        f"masharti ya Chama yaliyopitishwa na mkutano mkuu."
    return main_heading, heading, content


def second_section():
    main_heading = 'SEHEMU YA PILI'
    heading = 'MAELEZO YA UWASILISHAJI WA FOMU'

    content = f"Sehemu hii ni muhimu, lengo na dhumuni kuu kutoa tathmini ya namna fomu " \
        f"zilivyopokelewa kutoka katika SACCOS, kuonyesha kama SACCOS imewasilisha fomu hizo " \
        f"kikamilifu, kufanya uhakiki wa kila fomu kubaini kama kuna mapungufu katika fomu hizo. " \
        f"Hivyo wakati wa tatahmini mtiririko ufuatao utazingatiwa ili kuwezesha taarifa za tathmini " \
        f"kufanyika na kuwa na mwonekano unaofafana kwa maana ya kutoa taarifa ya tathmini ambapo " \
        f"jumla ya fomu kumi na mbili(12) zitapitiwa na afisa atapaswa kuainisha kila fomu na " \
        f"kuonyesha mapungufu kama yapo na mwisho kutoa maoni kwa hatua za maboresho kwa SACCOS " \
        f"husika. Aidha, Fomu kuni nambili(12) zitakzopitiwa ni kama ifuatavyo: "

    content_list = {
        "Taarifa Ya Hali Ya Fedha - Statement of Financial Position",
        "Taarifa Ya Mapato Na Matumizi - Statement Of Comprehsive Income And Expenditure",
        "Mgawanyiko wa Mikopo Kisekta - Sectorial Loan Classification",
        "Interest Rate Sructure for Loan - Muundo wa Viwango vya Riba vya Mikopo",
        "Mikopo iliyolewa - Loan Disbursed",
        "Mgawanyiko wa Matawi, Watendaji na mikopo kwa Umri - Geographical Distribution of Branches, Employees and Loans by Age",
        "Ukokotozi wa Ukwasihaji wa Mali - Computation of Liquidi Asset",
        "Ukokotozi wa Utoshelevu wa Mali - Computation of Capital Adequacy",
        "Taarifa ya Malalmiko - Complaint Report",
        "Amana na Mikopo kwenye Benki na taasisi za Fedha - Deposit, Loan in Banks and Financiala Institutions"
    }
    return main_heading, heading, content, content_list


def third_section():
    main_heading = 'SEHEMU YA TATU'
    heading = 'TATHMINI YA VIWIANISHI VYA PRUDENTIAL STANDARDS - CAMEL RATIOS'

    content = f"Sehemu hii itafafanua viwianishi vya kupima ubora wa SACCOS vilivyowekwa kwa " \
        f"mujibu wa muongozo wa Sheria ya Huduma Ndogo za Fedha ambapo jumla ya viwianishi vitano (5) vitapimwa. " \
        f"kikamilifu, kufanya uhakiki wa kila fomu kubaini kama kuna mapungufu katika fomu hizo. " \
        f"Aidha katika kila Afisa anayefanya tathmini atapaswa kuonyesha matokeo ya kila kiwianishi, " \
        f"kuonyesha kama kuna mapungufu na kutoa maoni kwa chama kwa kila kiwianishi kwa lengo " \
        f"la kuboresha utendaji wa Chama kwa siku za mbeleni, hivyo viwianishi vitakavyopimwa ni;"

    content_list = {
        "Utoshelevu wa Mtaji - Capital Adequacy",
        "Ubora wa Mali - Asset Quality",
        "Utawala - Management",
        "Mapato - Earning Annualized",
        "Ukwasi Na Mali - Liqidity Asset",
    }
    return heading, main_heading, content, content_list


def fourth_section():
    main_heading = 'SEHEMU YA NNE'
    heading = 'TATHMINI YA JUMLA'
    content = f"Baada ya kufanyika kwa tathmini ya kila eneo kwenye sehemu ya tatu ya muundo huu " \
        f"wa uwasilishaji wa taarifa, kila Afisa atapaswa kueleza tathmini ya jumla ya SACCOS " \
        f"husika, ikiwa ni pamoja na kuonyesha daraja ambalo SACCOS imepata kwa kuzingatia " \
        f"Tathmini iliyofanyika na kueleza kwa mapana sababu zilizopelekea SACCOS kupata daraja husika."
    return heading, main_heading, content


def fifth_section():
    main_heading = 'SEHEMU YA TANO'
    heading = 'MAMBO YANAYOTAKIWA KUFANYIWA KAZI KWA HARAKA'
    content = f"Ili kuhakikisha hali ya Chama ina imaimarika na kuwa na matokeo chanya kwa siku " \
        f"za usoni, Baada ya kufanyika kwa tathmini na kubaini hali ya chama, Afisa aliyefanya " \
        f"tathmini ataweka kwa muhtasari mambo ya msingi yanayopaswa kufanyiwa kazi kwa haraka " \
        f"ili bodi na menejiment ya Chama iweze kuyafanyia kazi kwa haraka. Aidha, ikitokea " \
        f"mapungufu ni mengi Afisa aliyefanya tathmini anaweza kushauri chama " \
        f"husika kuandikiwa barua ya maelekezo."
    return heading, main_heading, content


def sixth_section():
    main_heading = 'SEHEMU YA SITA'
    heading = 'HITIMISHO'
    content = f"Katika sehemu hii, Afisa atatoa hitimisho kwa namna ya kushukuru waliompa " \
        f"ushirikiano katika kuhakikisha taarifa imeandaliwa na kukamilika na mwisho atatoa " \
        f"msisitizo kwa SACCOS husika kuzingatia matakwa ya Sheria katika kuwasilisha taarifa " \
        f"na fomu kwa wakati kama maelekezo ya ofisi yanavyosema."
    return heading, main_heading, content


def sevnth_section():
    main_heading = 'SEHEMU YA SABA'
    heading = 'VIELELEZO'
    content = f"Sehemu hii itaonyesha viambatisho mbalimbali kama ikiwa wakati wa tathmini " \
        f"Afisa aliona kuna umuhimu wa kuomba chama kitume baadhi ya taarifa kwa lengo la " \
        f"kujiridhisha. Aidha, EXCEL FORMAT ilitumika kuonyesha ukokotozi wa Prudential " \
        f"standards utakuwa ni sehemu ya kiambatisho."
    return heading, main_heading, content


@reporting.route("/report", methods=['POST'])
def report():
    evaluation_id = request.form.get('evaluation_id')
    if evaluation_id is None:
        print("No data supplied")
    else:
        title = f"Performance Report for {evaluation_id}"
        evaluation = Evaluations.query.get_or_404(evaluation_id)

        pdf = FPDF()

        # Add a page
        pdf.add_page()

        # set style and size of font
        # that you want in the pdf
        pdf.set_font("Arial", size=15)

       # create a cell
        pdf.cell(40, 10, txt=report_title(),
                 ln=1, align='C')

        # add another cell
        pdf.cell(200, 10, txt=first_section()[0],
                 ln=2, align='C')

        # save the pdf with name .pdf

        response = make_response(pdf.output(
            evaluation_id+".pdf").encode('latin-1'))
        response.headers.set('Content-Disposition',
                             'attachment', filename=evaluation_id + '.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response

        # return send_file('static/reports/'+evaluation_id+".pdf", mimetype='application/pdf', download_name="report.pdf")
