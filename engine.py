from PIL import Image
import fileutil
import imgutil
from config import *
import numpy as np
from scipy import fftpack
from logger import log
import database as db


class File:
    name = None
    tmp_file = None
    output_file = None
    location = None
    inputsize = None
    outputsize = None
    inputcrc = None
    outputcrc = None
    processed = None
    quality = DEFAULT_QUALITY
    raw = None
    encoded = None
    jpg_array = None
    compare_type = None
    try_count = 1
    max_trys = DEFAULT_MAX_TRYS
    best_quality = 0
    best_file = None
    best_score = 0
    force_iter = False

    def __init__(self, location):
        self.name = fileutil.get_filename(location)
        self.tmp_file = (
            fileutil.get_filename(location).split(".")[0]
            + "_"
            + TMP_FILE_SUFFIX
            + fileutil.get_fileext(location)
        )
        self.output_file = (
            fileutil.get_path(location)
            + "\\"
            + fileutil.get_filename(location).split(".")[0]
            + "_"
            + OUTPUT_FILE_SUFFIX
            + fileutil.get_fileext(location)
        )
        self.location = location
        self.inputsize = fileutil.get_filesize(location)
        self.outputsize = 0
        self.inputcrc = fileutil.crc32(location)
        self.outputcrc = 0
        self.processed = False
        self.raw = Image.open(location)
        self.jpg_array = imgutil.img_to_array(Image.open(location))
        self.force_iter = FORCE_ITER


def compress(file):
    converted_image = file.raw.convert("YCbCr")
    tmp_matris = np.array(converted_image, dtype=np.uint8)
    rows, cols, _ = tmp_matris.shape
    rows = (rows // 8) * 8
    cols = (cols // 8) * 8
    tmp_matris = tmp_matris[:rows, :cols, :]
    blocks_count = (rows // 8) * (cols // 8)
    dc = np.empty((blocks_count, 3), dtype=np.int32)
    ac = np.empty((blocks_count, 63, 3), dtype=np.int32)
    block_index = 0
    for i in range(0, rows, 8):
        for j in range(0, cols, 8):
            for k in range(3):
                block = tmp_matris[i : i + 8, j : j + 8, k] - 128
                dct_matrix = fftpack.dct(block, norm="ortho")
                if k == 0:
                    quant_matrix = imgutil.quantize(dct_matrix, file.quality)
                else:
                    quant_matrix = imgutil.quantize(
                        dct_matrix, file.quality - QUALITY_RISE
                    )
                zigzag = imgutil.block_to_zigzag(quant_matrix)
                dc[block_index, k] = zigzag[0]
                ac[block_index, :, k] = zigzag[1:]
            block_index += 1
    tmp_matris = np.empty(file.jpg_array.shape, dtype=np.uint8)
    compressed_block = 0
    for i in range(0, rows, 8):
        for j in range(0, cols, 8):
            for c in range(3):
                zigzag = [dc[compressed_block, c]] + list(ac[compressed_block, :, c])
                quant_matrix = imgutil.zigzag_to_block(zigzag)
                if c == 0:
                    dct_matrix = imgutil.dequantize(quant_matrix, file.quality)
                else:
                    dct_matrix = imgutil.dequantize(
                        quant_matrix, file.quality - QUALITY_RISE
                    )
                block = fftpack.idct(dct_matrix, norm="ortho")
                tmp_matris[i : i + 8, j : j + 8, c] = block + 128
            compressed_block += 1
    file.encoded = Image.fromarray(tmp_matris, "YCbCr").convert("RGB")
    file.encoded.save(file.tmp_file)
    file.outputsize = fileutil.get_filesize(file.tmp_file)
    ssim_result = compare(file.compare_type, file)
    print(imgutil.calculate_psnr(file.raw, file.encoded))
    print(imgutil.calculate_ssim(file.raw, file.encoded))
    log(
        "{trys}/{try_limits} {filename} compressed to {filesize} bytes with {compare_type} score:{ssim_score}".format(
            trys=file.try_count,
            compare_type=file.compare_type,
            try_limits=file.max_trys,
            filename=file.name,
            filesize=file.outputsize,
            ssim_score=ssim_result,
        ),
        "info",
        "compress",
    )
    if file.best_score < ssim_result:
        file.best_quality = file.quality
        file.best_score = ssim_result
        file.best_file = file.encoded
    if file.best_score > MIN_QUALITY_PERCENTAGE and not file.force_iter:
        save_image(file)
    else:
        file.quality += QUALITY_RISE
        if file.try_count == file.max_trys:
            log("File reached maximum try limit.", "debug", "compress")
            save_image(file)
        else:
            file.try_count += 1
            compress(file)


def save_image(file):
    file.best_file.save(file.output_file)
    file.outputsize = fileutil.get_filesize(file.output_file)
    if compare("size", file) < 0:
        log(
            "Output file size is bigger than the input file size. We cant compress this file.",
            "info",
            "save_image",
        )
        fileutil.remove_file(file.output_file)
    else:
        log(
            "{filename} compressed to {filesize} bytes with {compare_type} score:{ssim_score}".format(
                compare_type=file.compare_type,
                filename=file.name,
                filesize=file.outputsize,
                ssim_score=file.best_score,
            ),
            "info",
            "compress",
        )
        file.outputcrc = fileutil.crc32(file.output_file)
        db.insert_to_history(file)
    fileutil.remove_file(file.tmp_file)


def compare(case, file1, file2="None"):
    result = 0
    match case:
        case "ssim":
            if file2 == "None":
                img1 = file1.raw
                img2 = file1.encoded
                result = int((imgutil.calculate_ssim(img1, img2) * 100).round())
            else:
                img1 = file1.raw
                img2 = file2.raw
                result = int((imgutil.calculate_ssim(img1, img2) * 100).round())
        case "size":
            if file2 == "None":
                size1 = file1.inputsize
                size2 = file1.outputsize
                result = size1 - size2
            else:
                size1 = file1.inputsize
                size2 = file2.inputsize
                result = size1 - size2
        case "psnr":
            if file2 == "None":
                img1 = file1.raw
                img2 = file1.encoded
                result = imgutil.calculate_psnr(img1, img2)
            else:
                img1 = file1.raw
                img2 = file2.raw
                result = imgutil.calculate_psnr(img1, img2)
    return result
