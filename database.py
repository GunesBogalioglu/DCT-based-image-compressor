import sqlite3 as sql
from logger import log
from config import *

# TODO args kısmında dbye kaydet var ise dosyaya kaydet yoksa kaydetme.
db = sql.connect(SQL_FILE)
db.execute(
    "CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT,filename TEXT,before_size INTEGER,before_crc INTEGER,after_size INTEGER,after_crc INTEGER)"
)
# db crc index oluşturma
db.execute(
    'CREATE INDEX IF NOT EXISTS "optimized_crc_index" ON "history" (after_crc ASC)'
)


def insert_to_history(file):
    """DB dosyasına file objesinden gelen isim,boyut ve crc değerini girer.

    Args:
        file (inputfile): Temel file objesini alır.
    """
    # TODO we could use file.processed too. This way it can be more performant
    if not isoptimized(file):  # dbye tekrar tekrar aynı şeyin kaydını engeller.
        db.execute(
            'INSERT INTO history (filename,before_size,before_crc,after_size,after_crc) values("{filename}","{before_size}","{before_crc}","{after_size}","{after_crc}")'.format(
                filename=file.name,
                before_size=file.inputsize,
                before_crc=file.inputcrc,
                after_size=file.outputsize,
                after_crc=file.outputcrc,
            )
        )
        db.commit()
        log(file.name + " dosyası geçmişe kaydedildi.", "debug", "insert_to_history")


def isoptimized(file):
    """DB'den dosyanın daha önce optimize edilip edilmediğini kontrol eder.

    Args:
        file (inputfile): Temel file objesini alır.

    Returns:
        bool:True ise optimize edilmiş. False ise optimize edilmemiş.
    """
    count = db.execute(
        "SELECT count(*) FROM history WHERE after_size={after_size} AND after_crc={after_crc}".format(
            after_size=file.inputsize, after_crc=file.inputcrc
        )
    )
    result = count.fetchone()[0]
    if result == 0:
        return False
    else:
        return True
