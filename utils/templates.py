import base64


with open('utils/voucher.html', 'r') as f:
    voucher_template = f.read()

with open('utils/stact.png', 'rb') as f:
    stact = base64.b64encode(f.read()).decode('utf-8')


with open('utils/paradox_new_logo.png', 'rb') as f:
    paradox_new_logo = base64.b64encode(f.read()).decode('utf-8')


with open('utils/sign.png', 'rb') as f:
    sign = base64.b64encode(f.read()).decode('utf-8')
