import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import socket

def generate_qr_code():
    ip = socket.gethostbyname(socket.gethostname())
    url = f'http://{ip}:5000'
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill='black', back_color='white')

def display_qr_code():
    # Khởi tạo cửa sổ Tkinter
    root = tk.Tk()
    root.title("QR Code")

    # Tạo mã QR
    qr_code = generate_qr_code()

    # Chuyển mã QR thành ảnh Tkinter
    qr_code_image = ImageTk.PhotoImage(qr_code)

    # Tạo label để hiển thị mã QR
    label = tk.Label(root, image=qr_code_image)
    label.pack(padx=10, pady=10)

    # Giữ cửa sổ hiển thị
    root.mainloop()

# Chạy ứng dụng hiển thị QR Code
display_qr_code()
