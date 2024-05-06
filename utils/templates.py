import base64


# with open('utils/voucher.html', 'r') as f:
#     voucher_template = f.read()

with open('utils/voucher_template.html', 'r') as f:
    voucher_template = f.read()

with open('utils/stact.png', 'rb') as f:
    stact = base64.b64encode(f.read()).decode('utf-8')


with open('utils/paradox_new_logo.png', 'rb') as f:
    paradox_new_logo = base64.b64encode(f.read()).decode('utf-8')


# with open('utils/sign.png', 'rb') as f:
#     sign = base64.b64encode(f.read()).decode('utf-8')

with open('utils/subhash.png', 'rb') as f:
    sign = base64.b64encode(f.read()).decode('utf-8')

req_approved_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Request Approved by {{ role }}</title>
</head>
<body>
<p>Hi {{ name }},</p>
<p> Your request for {{ requirement }} has been approved by {{ role }}.</p>
<p> The same has been updated in the FR portal.</p>

<p> Regards,</p>
<p> Finance and Operations,</p>
<p> Paradox 2024</p>
</body>
</html>
"""

req_rejected_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Request Rejected by {{ role }}</title>
</head>
<body>
<p>Hi {{ name }},</p>
<p> Your request for {{ requirement }} has been rejected by {{ role }} for the following reason:</p>
<p> {{ reason }} </p>
<p> The same has been updated in the FR portal.</p>
<p> You can edit and resubmit the request if needed in the portal.</p>

<p> Regards,</p>
<p> Finance and Operations,</p>
<p> Paradox 2024</p>
</body>
</html>
"""


fest_reg_template = '''
<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradox'24 Updates</title>
</head>
<body>
    <div>
        <p>Dear {{ student_name }},</p>
        <p>Congratulations for successfully registering for Paradox'24! Get set for an exhilarating experience on our campus from May 30th to June 2nd.</p>
        <p>And guess what?  We've got an electrifying surprise event in store for everyone, and details will be unveiled shortly. Stay tuned to our social media channels for the latest updates and sneak peeks!</p>
        <p>Please note that this email serves as confirmation of your festival registration. As for accommodation, fret not, registration form will soon be rolled out on our website. But bear in mind, accommodation slots are limited and will be allocated on a first-come, first-served basis.</p>
        <p>The check-in desk for accommodation opens its doors on May 29th and remains accessible until June 2nd. Operating hours are from 8:00 AM to 8:00 PM daily. Plan your travel arrangements accordingly to ensure a seamless check-in process.</p>
        <p>Should you have any inquiries or doubts, please don't hesitate to reach out to us at <a href="mailto:support@iitmparadox.org">support@iitmparadox.org</a>.</p>

        <p>Warm Regards,</p>
        <p>Team Paradox</p>
    </div>
</body>
</html>
'''

fest_update_template = '''
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradox'24 Registration Update</title>
</head>
<body>
    <div>
        <p>Dear {{ student_name }},</p>
        <p>We've received your update/edit for Paradox'24 registration. Your changes have been successfully captured. Thank you for keeping us informed!</p>
        <p>If you have any further questions or concerns, feel free to reach out to us at <a href="mailto:support@iitmparadox.org">support@iitmparadox.org</a>.</p>
        <p>Best Regards,</p>
        <p>Team Paradox</p>
    </div>
</body>
</html>
'''


event_reg_conf_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Paradox'24 Registration Confirmation</title>
</head>
<body>
    <p>Dear {{ student_name }},</p>
    
    <p>We are pleased to inform you that your registration for the {{ event_name }} event at Paradox'24 has been captured successfully.</p>
    <p>You can find all the events you have registered for and edit if needed in your profile page under "Registered Events".</p>
    
    <p>Thank you for participating! We look forward to seeing you at the event.</p>
    
    <p>Best regards,<br>
    Paradox'24 Team</p>
</body>
</html>

'''
