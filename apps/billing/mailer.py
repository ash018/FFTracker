import boto3
from jinja2 import Environment, PackageLoader
from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from weasyprint import HTML

env = Environment(loader=PackageLoader('apps', 'billing/templates/billing'))


class Email(object):
    def __init__(self, mail_from, subject):
        self.mail_from = mail_from
        self.subject = subject
        self._html = None
        self._text = None
        self._format = 'html'

    def _render(self, filename, context):
        template = env.get_template(filename)
        return template.render(context)

    def html(self, filename, context):
        self._html = self._render(filename, context)

    def text(self, filename, context):
        self._text = self._render(filename, context)

    def send(self, mail_to):
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'

        connection = boto3.client(
            'ses',
            region_name=settings.AWS_SES_REGION_NAME,
            aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY
        )

        msg = MIMEMultipart('mixed')
        msg['Subject'] = self.subject
        msg['From'] = settings.SENDER_EMAIL
        msg['To'] = mail_to[0]

        msg_body = MIMEMultipart('alternative')
        html_part = MIMEText(self._html.encode("utf-8"), 'html', "utf-8")
        msg_body.attach(html_part)
        msg.attach(msg_body)

        # pdf = pdfkit.from_string(self._html, output_path=False)
        pdf = HTML(string=self._html).write_pdf()
        att = MIMEApplication(pdf)
        att.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
        msg.attach(att)

        return connection.send_raw_email(
            Source=self.mail_from,
            Destinations=mail_to,
            RawMessage={
                'Data': msg.as_string(),
            },
        )
