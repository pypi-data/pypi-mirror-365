import cv2
import numpy as np


def main(input_path:str, output_path:str):
	transparent_image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
	not_transparent_mask = transparent_image[:, :, 3] != 0

	hsv_im = cv2.imread(input_path)
	hsv_im = cv2.cvtColor(hsv_im, cv2.COLOR_BGR2HSV)
	new_im = hsv_im.copy()

	# Convert white to black
	white_mask = (hsv_im[:, :, 1] < 2) & (hsv_im[:, :, 2] > 100)
	white_mask &= not_transparent_mask
	new_im[white_mask, 2] = 255 - hsv_im[white_mask, 2]
	# new_im[white_mask, :2] = [0, 0]

	# Convert black to white
	black_mask = hsv_im[:, :, 2] < 140
	black_mask &= not_transparent_mask
	new_im[black_mask, 2] = 255 - hsv_im[black_mask, 2]
	new_im[black_mask, :2] = [0, 0]

	# Convert HSV into BGRA
	new_im = cv2.cvtColor(new_im, cv2.COLOR_HSV2BGR)
	new_im = cv2.cvtColor(new_im, cv2.COLOR_BGR2BGRA)
	new_im[:, :, 3] = transparent_image[:, :, 3]

	cv2.imwrite(output_path, new_im)


def anl(input_path:str, output_path:str):
	transparent = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
	img = cv2.imread(input_path, cv2.IMREAD_COLOR_BGR)

	black_bgr = np.array([32, 31, 35])

	mask = img[:, :, :] == black_bgr
	img[mask] = 255 - img[mask]
	img = np.dstack([img, transparent[:, :, 3]])

	img[64:270, 901:1133] = transparent[64:270, 901:1133]

	cv2.imwrite(output_path, img)


if __name__ == "__main__":
	# main("ExsclaimLogo.png", "ExsclaimLogo-Inverted.png")
	anl("Argonnelablogo.png", "Argonnelablogo-White.png")
