import time
from fileutil import write_to_file, create_directory
from config import *

create_directory(LOG_FOLDER_PATH)

# logfileloc = ".\\logs\\log.log"
log_levels = ["info", "error", "debug"]
# log_level = "debug"


# TODO args kısmında logging var ise dosyaya kaydet yoksa kaydetme.
# log_level info ise [][][] ksımlarını gizle ve mümkünse enuma çevir
def log(msg, level, function_name):
    """Mesaj loglaması yapar.

    Args:
        msg (string): Mesaj
        level (string): Mesajın seviyesi ["info", "error", "debug"]
        function_name (string): Mesajın gönderildiği fonksiyonun ismi
    """
    if log_levels.index(LOG_LEVEL) > 0:
        tmp_msg = "[{level}][{time}][{function_name}] {msg}".format(
            level=level, function_name=function_name, msg=msg, time=time.ctime()
        )
        print(tmp_msg)
        if LOG_LEVEL == "debug":
            write_to_file(LOG_FOLDER_PATH + "\\" + LOG_FILE, tmp_msg)
    elif level == "info":
        print(msg)


# log("Logger test", "debug", "test")
