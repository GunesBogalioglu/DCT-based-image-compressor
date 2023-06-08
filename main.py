from config import *
import engine
from logger import log
import argparse
from database import isoptimized
import fileutil


######ARGS######
# -input -i
# -quality -q
# -iter (iterasyon sayısı)
# -check -crc (will check db for that file)
# -compare -c (will compare 2 different files)(will return ssim or psnr)
# -target -t (compare true olduğu zaman 2.input)
# -mode -m compare mode "psnr" "ssim" "size"
# -force -f (otomatik iter tamamlama özelliğini kapatır) # disables min_quality threshold)


def main():
    file1 = None
    file2 = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-input", "-i", required=True, help="Kullanılacak dosya")
    parser.add_argument(
        "-quality",
        "-q",
        type=int,
        default=DEFAULT_QUALITY,
        help="Sıkıştırılacak dosyanın kalitesi",
    )
    parser.add_argument(
        "-iter", type=int, default=DEFAULT_MAX_TRYS, help="Maksimum iterasyon sayısı"
    )
    parser.add_argument(
        "-check", "-crc", action="store_true", default=False, help="DB'de o dosyayı ara"
    )
    parser.add_argument(
        "-compare",
        "-c",
        default=False,
        action="store_true",
        help="compare 2 different files",
    )
    parser.add_argument(
        "-mode", "-m", default="ssim", help="Karşılaştırma yöntemi:psnr,ssim,size"
    )
    parser.add_argument(
        "-force",
        "-f",
        action="store_true",
        default=False,
        help="min_quality limitini kapatır",
    )
    parser.add_argument("-target", "-t", help="karşılaştırma yapılacak 2. dosya")
    args = parser.parse_args()
    ############## Args to data
    if args.quality > 100:
        args.quality = 100
    elif args.quality <= 0:
        args.quality = 0
    if args.iter <= 0:
        args.iter = 1
    # Create first file
    if not fileutil.check_file_exists(args.input):
        parser.error("File does not exist")
    else:
        file1 = engine.File(args.input)
        file1.compare_type = args.mode
        file1.force_iter = args.force
    if args.target is not None:
        if not fileutil.check_file_exists(args.target):
            parser.error("File does not exist")
        else:
            file2 = engine.File(args.target)
            file2.compare_type = args.mode  # Gerek yok ama yinede bulunsun
    if args.compare and args.target is None:
        parser.error(
            "-crc komutu için 2. bir dosya gerekmektedir. -t veya -target ile 2. dosyayı gösterebilirsiniz."
        )
    if args.compare and args.target is not None:
        print(engine.compare(args.mode, file1, file2))

    if file1 != None and not args.compare:
        file1.max_trys = args.iter
        file1.quality = args.quality
        file1.processed = isoptimized(file1)
        if file1.processed and args.check:
            log(
                "{filename} is already optimized.".format(filename=file1.name),
                "info",
                "isoptimized",
            )
        else:
            log(
                "This process can take a few minutes to complete. Please stand by.",
                "info",
                "main",
            )
            engine.compress(file1)

    return 0


main()
