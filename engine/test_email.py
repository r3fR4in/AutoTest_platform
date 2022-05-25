import smtplib
from email.mime.text import MIMEText

smtp_host = 'smtp.163.com'
smtp_port = 465
pwd = '34tf2chainz'
sender = 'gsj785930404@163.com'
receiver = ['Niko.sj.guan@teleone.cn']
authorization_code = 'WZWYEQIKABLVBPIV'

message = MIMEText('content', 'plain', 'utf-8')
message['Subject'] = 'title'
message['From'] = sender
message['To'] = receiver[0]
conn = None

try:
    conn = smtplib.SMTP_SSL(smtp_host, smtp_port)
    conn.login(sender, authorization_code)
    conn.sendmail(sender, receiver, message.as_string())
    print('success')
except Exception as e:
    print(e)
finally:
    if conn:
        conn.quit()
