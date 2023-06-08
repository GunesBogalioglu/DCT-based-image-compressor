import numpy as np


def dequantize(matris, quality):
    return matris * generate_dct_matrix(quality)


def quantize(matris, quality):
    q = generate_dct_matrix(quality)
    with np.errstate(divide="ignore", invalid="ignore"):
        tmp_matris = np.true_divide(matris, q).astype(np.int32)
        tmp_matris[tmp_matris == np.inf] = 0
        tmp_matris = np.nan_to_num(tmp_matris)
    return tmp_matris


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def img_to_array(img):
    tmp_array = np.fromstring(img.tobytes(), dtype=np.uint8)
    ptr = (int)(tmp_array.size / (img.size[0] * img.size[1]))
    if ptr > 1:
        tmp_array = tmp_array.reshape((img.size[1], img.size[0], ptr))
    else:
        tmp_array = tmp_array.reshape((img.size[1], img.size[0]))
    return tmp_array


def matrix_to_array(matrix):
    tmp_array = []
    for array in matrix:
        for item in array:
            tmp_array.append(item)
    return tmp_array


def block_to_zigzag(block):
    return np.array([block[point] for point in zigzag_points(*block.shape)])


def zigzag_to_block(zigzag):
    # rows=cols
    rows = int(np.sqrt(len(zigzag)))
    cols = int(np.sqrt(len(zigzag)))
    tmp_matris = np.empty((rows, cols), np.int32)
    for i, point in enumerate(zigzag_points(rows, cols)):
        tmp_matris[point] = zigzag[i]
    return tmp_matris


def zigzag_points(rows, cols):
    UP, DOWN, RIGHT, LEFT, UP_RIGHT, DOWN_LEFT = range(6)

    def move(direction, point):
        x, y = point
        if direction == UP:
            return x - 1, y
        elif direction == DOWN:
            return x + 1, y
        elif direction == LEFT:
            return x, y - 1
        elif direction == RIGHT:
            return x, y + 1
        elif direction == UP_RIGHT:
            return x - 1, y + 1
        elif direction == DOWN_LEFT:
            return x + 1, y - 1

    def check_valid(point):
        x, y = point
        return 0 <= x < rows and 0 <= y < cols

    point = (0, 0)
    move_up = True
    for _ in range(rows * cols):
        yield point
        if move_up:
            next_point = move(UP_RIGHT, point)
            if check_valid(next_point):
                point = next_point
            else:
                move_up = False
                next_point = move(RIGHT, point)
                if check_valid(next_point):
                    point = next_point
                else:
                    point = move(DOWN, point)
        else:
            next_point = move(DOWN_LEFT, point)
            if check_valid(next_point):
                point = next_point
            else:
                move_up = True
                next_point = move(DOWN, point)
                if check_valid(next_point):
                    point = next_point
                else:
                    point = move(RIGHT, point)


def generate_dct_matrix(quality_factor):
    N = 8
    dct_matrix = np.zeros((N, N))
    if quality_factor < 1:
        quality_factor = 1
    elif quality_factor >= 100:
        quality_factor = 100
    # Calc part
    for i in range(N):
        for j in range(N):
            if i == 0:
                alpha_i = 1
            else:
                alpha_i = np.sqrt(2 / N)
            if j == 0:
                alpha_j = 1
            else:
                alpha_j = np.sqrt(2 / N)
            if quality_factor < 50:
                adjustment_factor = (quality_factor - 50) * 2
            else:
                adjustment_factor = -1 * (quality_factor - 50) / 51

            quality_adjustment = 1 + adjustment_factor

            dct_matrix[i, j] = (
                alpha_i
                * alpha_j
                * quality_adjustment
                * np.cos(((2 * i + 1) * np.pi * j) / (2 * N))
            )

    return dct_matrix


def calculate_psnr(source, target):
    img_original = source
    img_compressed = target
    img_original_gray = img_original.convert("L")
    img_compressed_gray = img_compressed.convert("L")
    original_array = np.array(img_original_gray).astype(np.float64)
    compressed_array = np.array(img_compressed_gray).astype(np.float64)
    mse = np.mean((original_array - compressed_array) ** 2)
    max_pixel = np.max(original_array)
    if mse == 0:
        psnr = float("inf")
    else:
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


def calculate_ssim(source, target, L=255):
    img_original = source
    img_compressed = target
    img1_array = np.array(img_original)
    img2_array = np.array(img_compressed)
    channel_scores = []
    for channel in range(3):
        mu1 = np.mean(img1_array[:, :, channel])
        mu2 = np.mean(img2_array[:, :, channel])
        sigma1 = np.std(img1_array[:, :, channel])
        sigma2 = np.std(img2_array[:, :, channel])
        sigma12 = np.cov(
            img1_array[:, :, channel].flatten(), img2_array[:, :, channel].flatten()
        )[0, 1]
        k1 = 0.01
        k2 = 0.03
        L = 255
        c1 = (k1 * L) ** 2
        c2 = (k2 * L) ** 2
        numerator = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
        denominator = (mu1**2 + mu2**2 + c1) * (sigma1**2 + sigma2**2 + c2)
        channel_score = numerator / denominator
        channel_scores.append(channel_score)
    ssim_score = np.mean(channel_scores)
    return ssim_score
