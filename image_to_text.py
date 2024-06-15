import PIL.Image
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

genai.configure(api_key="AIzaSyDRX69l3YJyJMBvLjnWQ2dqzwi6_bgnGrM")
model = genai.GenerativeModel('gemini-pro-vision')

def generate_and_send_report(image_path, email_recipients):
    image = PIL.Image.open(image_path)
    response = model.generate_content([image, "Assume yourself as Ai Agent monitoring the accidents on roads, u should make a message to report to police and hospital include severity and time and location and description only"])
    message_text = response.text

    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login("nutshell.accident@outlook.com", "Nutshell@1234")

    msg = MIMEMultipart()
    msg['Subject'] = 'Accident Report - Nutshell AI Agent'
    msg['From'] = 'nutshell.accident@outlook.com'
    msg['To'] = ", ".join(email_recipients)

    text = MIMEText(message_text)
    msg.attach(text)

    with open(image_path, 'rb') as img:
        mime_img = MIMEImage(img.read())
        msg.attach(mime_img)

    server.sendmail(msg['From'], email_recipients, msg.as_string())

    server.quit()

