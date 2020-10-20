import smtplib
import os

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import logging


class EmailAlertDispatcher:
    """
    Utility class that wraps MIME initialization and smtp server handling
    """

    def __init__(self, email: str, password: str, send_to: str, subject: str, message: str,
                 attachment_file_path: str) -> None:
        """
        Email alert dispatcher constructor
        :param email: senders email
        :param password: senders password -> REPLACE WITH API KEY !
        :param send_to: recipient address
        :param subject: email subject
        :param message: message text
        :param attachment_file_path: path for the attachment file
        """
        self._msg = MIMEMultipart()
        self.subject = subject
        self.send_to = send_to
        self.password = password
        self.email = email
        self.message = message
        self.attachment_file_path = attachment_file_path

        self._filename = os.path.basename(self.attachment_file_path)
        self._attachment = open(self.attachment_file_path)

    def compose_msg(self) -> None:
        """
        MIME multipart message initialization with class parameters
        """
        self._msg['From'] = self.email
        self._msg['To'] = self.send_to
        self._msg['Subject'] = self.subject
        self._msg.attach(MIMEText(self.message, 'plain'))

        _part = MIMEBase('backup script', 'octet-stream')
        _part.set_payload(self._attachment.read())
        encoders.encode_base64(_part)
        _part.add_header('Content-Disposition', f"attachment; filename={self._filename}")
        self._msg.attach(_part)
        logging.info(f"email sent to {self._msg['To']}")  # import log class

    def smtp_send(self) -> None:
        """
        Method that sends the generated message via google smtp
        """
        # TODO fix DNS table @home -> KILL FIDO
        _server = smtplib.SMTP('64.233.184.108', 587)
        _server.starttls()
        _server.login(user=self.email, password=self.password)
        _text = self._msg.as_string()
        _server.sendmail(self.email, self.send_to, _text)
        _server.quit()


if __name__ == '__main__':
    # test
    _email = "alert.dispatcher.6883674@gmail.com"
    # TODO replace with API key in REAL production env!
    _password = "SecurePasswordsAsPlainText!1"  # BEST SECURITY PRACTICE EVER!
    _send_to = "alert.dispatcher.6883674@gmail.com"
    _subject = "Exception during alert execution !"
    _message = "most recent log attached "
    _file_attachment_path = "C:\\Users\\Art3m15\\Desktop\\local_dev_new\\local_dev\\interviews\\Oanda\\production\\backup_logs\\backup_service.log"

    ead = EmailAlertDispatcher(_email, _password, _send_to, _subject, _message, _file_attachment_path)
    ead.compose_msg()
    ead.smtp_send()
