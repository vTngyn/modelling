from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from PIL import Image, ImageDraw, ImageTk

class ImageUtils(LEC):
    @staticmethod
    def getImages(self, filename):
        img = Image.open(filename)
        return img

    @staticmethod
    def getMinResizeScale(self, width, height, new_width, new_height):
        ratio = int(new_width / width)
        ratio2 = int(new_height / height)
        if ratio < ratio2:
            return ratio, new_width, ratio * height
        else:
            return ratio2, width * ratio2, new_height
    @staticmethod
    def generate_label_images(self):
        label_images = {}
        labels = self.speakers
        labelExtraHeight = 30
        resizeFactor = 1
        iconHeight = 45
        iconWidth = 30

        for label in labels:
            # Load the image file corresponding to the label
            img = Image.open(f'{label}_image.png')  # Replace with the actual image file path

            # Resize the image to a specific width (adjust as needed)
            width, height = img.size
            ratio, new_width, new_height = ImageUtils.getMinResizeScale(width, height, iconWidth,
                                                                  iconHeight)  # Adjust this value based on your requirement
            # new_height = int(height + labelExtraHeight)
            # new_height = int((new_width / width) * height)
            img = img.resize((new_width, new_height))

            # Create a transparent image with a label
            transparent_label_img = Image.new('RGBA', (new_width, new_height + labelExtraHeight), (255, 255, 255, 0))
            transparent_label_draw = ImageDraw.Draw(transparent_label_img)
            transparent_label_draw.text((new_width, labelExtraHeight), f'Speaker {label}', fill=(255, 255, 255, 255))

            # Combine the original image with the label
            combined_img = Image.alpha_composite(
                Image.alpha_composite(Image.new('RGBA', transparent_label_img.size), img.convert('RGBA')),
                transparent_label_img)

            label_images[label] = ImageTk.PhotoImage(combined_img)

        return label_images

    @staticmethod
    def createTransparentImg(speakerLabel, labelExtraHeight, new_width, new_height, fill=(255, 255, 255, 255), color=(255, 255, 255, 0)):
        # Create a transparent image with a label
        transparent_label_img = Image.new('RGBA', (new_width, new_height + labelExtraHeight), (255, 255, 255, 0))
        transparent_label_draw = ImageDraw.Draw(transparent_label_img)
        transparent_label_draw.text((new_width, labelExtraHeight), f'Speaker {speakerLabel}', fill=fill)
        return transparent_label_img
