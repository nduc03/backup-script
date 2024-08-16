from PIL import Image
import sys, os


def webp_to_jpg_path(path):
    if not path.endswith(".webp"):
        return
    return path[:-5] + ".jpg"


def convert_image(image_path, delete_old=False):
    if not image_path.endswith(".webp"):
        return
    Image.open(image_path).convert("RGB").save(
        webp_to_jpg_path(image_path), "jpeg")
    # Todo: Remove old file when delete_old is True


def select_file_then_convert(path):
    if not os.path.exists(path):
        print("Not found")
        return
    if os.path.isdir(path):
        for webp_file in os.listdir(path):
            if os.path.isfile(os.path.join(path, webp_file)) and webp_file.endswith(".webp"):
                convert_image(os.path.join(path, webp_file))
    else:
        convert_image(path)


def manual_input():
    select_file_then_convert(input("Enter file path: "))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        manual_input()
    elif os.path.exists(sys.argv[1]):
        select_file_then_convert(sys.argv[1])

