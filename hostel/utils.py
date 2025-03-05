import qrcode
from io import BytesIO


def generate_hosteller_qr_code(data):
    """
    Generates a QR code for the given data.

    :param data: The data to encode in the QR code.
    :return: The generated QR code image in bytes format.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate the QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the image to bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
