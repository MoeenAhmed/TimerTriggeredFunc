import logging
import azure.functions as func
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientAssertionCredential
import datetime
import smtplib

def SendEmail(notificationMsg) :
    gmail_user = 'moeenahmed769@gmail.com'
    gmail_password = 'Moeen@123'

    sent_from = gmail_user
    to = ['moeenahmed769@gmail.com']
    subject = 'Secret Expired Notification'
    body = notificationMsg

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    tenantId = ""
    clientId = ""
    clientSecret = ""

    KVUri = "https://moeentestkv.vault.azure.net/"

    credential = ClientAssertionCredential(
        tenant_id=tenantId,
        client_id=clientId,
        clientSecret = clientSecret
    )
    client = SecretClient(vault_url=KVUri, credential=credential)

    secrets = client.list_properties_of_secrets()
    notificationMsg = ""

    for secret in  secrets:
        secretInfo = client.get_secret(secret.name)
        expiryDate = secretInfo.properties.expires_on
        expiryDate = secret.expires_on
        today = datetime.datetime.utcnow()
        diff = expiryDate - today
        if(diff < 30):
            msg = "Secret : {0}, Expiry Date : {0} \n"
            notificationMsg += msg.format(secret.name,secret.expires_on)

    if not notificationMsg:
        print ("Secret that expired….",notificationMsg)
        SendEmail("notificationMsg")
