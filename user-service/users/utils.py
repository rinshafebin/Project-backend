import pyotp
import qrcode
from io import BytesIO
import base64

def generate_totp_secret():
    return pyotp.random_base32()

def generate_totp_uri(user):
    totp =pyotp.TOTP(user.mfa_secret)
    return totp.provisioning_uri(
        name=user.email,
        issuer_name="CaseBridge"
    )

def generate_totp_qr(user):
    uri = generate_totp_uri(user)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')  
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"