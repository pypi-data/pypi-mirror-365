from smartmailer import SmartMailer, TemplateModel, TemplateEngine
from typing import List, Optional

class MySchema(TemplateModel):
    name: str
    committee: str
    allotment: str
    email: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

body = """
Dear {{ name }},
This is a test email for the Model UN 2025 conference. You are assigned to the {{ committee }} committee with the allotment of {{ allotment }}.
Regards,
The Organizing Committee"""

subject = "SSNSNUCMUN 2025 Conference Assignment"

template = TemplateEngine(subject=subject, body_text=body)

recipients = [
    {"name": "Arjun", "committee": "UNDP", "allotment": "India", "email": "tjkamlesh@gmail.com", 'cc': ['reverseindian7@gmail.com'], 'bcc': ['vjshasu1309@gmail.com'], 'attachments': [r"C:\Users\Nithya\Desktop\CS1001 Programming in C.pdf"]},
]


obj_recipients = [MySchema(name=recipient['name'], committee=recipient['committee'], allotment=recipient['allotment'], email= recipient['email'], cc= recipient['cc'], bcc= recipient['bcc'], attachments= recipient['attachments'] ) for recipient in recipients]
for recipient in obj_recipients:
    print("Hash:", recipient.hash_string)


smartmailer = SmartMailer(
    sender_email="kamlesh24110001@snuchennai.edu.in",
    password="SilverMoon!92River",
    provider="outlook",
    session_name="attachments_cc_test"
)

print("Mailer object created")

smartmailer.send_emails(
    recipients=obj_recipients,
    email_field="email",
    template=template,
    cc_field= "cc",
    bcc_field= "bcc",
    attachment_field="attachments"
)