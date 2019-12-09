from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.conf import settings
import hashlib
import smtplib
import os.path

def url_for_confirm_mail( hash, id ):
    return "http://bioinfo.imd.ufrn.br/cursosdcd_userarea/2020-1/user/registration/confirm/" + hash + "/" + str(id) + "/"

def url_for_forgot_my_password( hash, id ):
    return "http://bioinfo.imd.ufrn.br/cursosdcd_userarea/2020-1/user/changepassword/authenticate/" + hash + "/" + str(id) + "/"

# =============================================================================

def send_mail( msg ):
    server = smtplib.SMTP( settings.EMAIL_HOST )
    server.starttls()
    server.login( settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD )
    server.sendmail( settings.EMAIL_HOST_USER, msg['To'], msg.as_string() )
    server.quit()

def send_mail_for_user_confirm_mail( nome, email_user, link ):
    base = os.path.dirname(os.path.abspath(__file__))

    # Criando cabeçalho do email
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Biome - Cursos de curta duração 2020'
    msgRoot['From'] = settings.EMAIL_HOST_USER
    msgRoot['To'] = email_user

    # Corpo html
    fhtml = open(os.path.join(base, 'templates/user/email.html'), 'r', encoding="utf-8")
    body  = fhtml.read()
    fhtml.close()
    
    body = MIMEText( body.replace("nome_user", nome)
                        .replace("link_user", link)
                        .replace("title_user", "Muito obrigado por demonstrar o seu interesse nos cursos de curta duração 2020")
                        .replace("msg_user", "Por favor clique no botão abaixo para ativar sua conta")
                        .replace("confirm_btn", "Confirmar"), 'html')
    msgRoot.attach( body )

    # Img Patrocinadores
    fp = open(os.path.join(base, 'static/user/images/logos/biome_small.jpg'), 'rb')
    msgImage = MIMEImage( fp.read() )
    fp.close()
    msgImage.add_header('Content-ID', '<img_logo>')
    msgRoot.attach(msgImage)

    send_mail(msgRoot)

def send_mail_for_user_forgot_my_password( nome, email_user, link ):
    base = os.path.dirname( os.path.abspath(__file__) )

    # Criando cabeçalho do email
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Biome - Cursos de curta duração 2020'
    msgRoot['From'] = settings.EMAIL_HOST_USER
    msgRoot['To'] = email_user

    # Corpo html
    fhtml = open( os.path.join( base, 'templates/user/email.html' ), 'r', encoding="utf-8" )
    body = MIMEText( fhtml.read().replace("link_user", link)
                                 .replace("title_user", "Mudança de senha")
                                 .replace("msg_user", "Para mudar sua senha, por favor clique no botão abaixo")
                                 .replace("nome_user", nome)
                                 .replace("confirm_btn", "Mudar senha"), 'html')
    fhtml.close()
    msgRoot.attach(body)

    # Img Patrocinadores
    fp = open( os.path.join( base, 'static/user/images/logos/biome_small.jpg'), 'rb' )
    msgImage = MIMEImage( fp.read() )
    fp.close()
    msgImage.add_header('Content-ID', '<img_logo>')
    msgRoot.attach( msgImage )

    send_mail( msgRoot )

def send_mail_notification_for_user( email_user, nome_user, texto, titulo ):
    base = os.path.dirname(os.path.abspath(__file__))

    # Criando cabeçalho do email
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Cursos de curta duração 2020'
    msgRoot['From'] = settings.EMAIL_HOST_USER
    msgRoot['To'] = email_user

    # Corpo html
    fhtml = open(os.path.join(base, 'templates/user/email_html.html'), 'r', encoding="utf-8")
    body = MIMEText(fhtml.read().replace("link_user", "https://bioinfo.imd.ufrn.br/cursosdcd_userarea/2020-1/user/login/")
                    .replace("title_user", titulo)
                    .replace("msg_user", texto)
                    .replace("nome_user", nome_user).replace("confirm_btn", "Login"), 'html')
    fhtml.close()
    msgRoot.attach(body)

    # Img Patrocinadores
    fp = open(os.path.join(base, 'static/user/images/logos/biome_small.jpg'), 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<img_logo>')
    msgRoot.attach(msgImage)

    send_mail(msgRoot)
