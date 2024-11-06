from PIL import Image, ImageDraw, ImageFont

class ImageDesigner:
    def __init__(self):
        pass

    def draw_clues_horizontal(self, data):
        width, height = 450, 220
        font_size = 14
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        # Writing numbers and lines on the empty image
        x, y = 0, 0
        for index, line in enumerate(data):
            y = 190
            if line == []:
                line = [0]  # Adds a zero in case tesseract couldn't detect any number
            for number in line[::-1]:
                draw.text((x + 15, 15), str(index + 1), fill='black', font=ImageFont.truetype("arial.ttf", font_size),
                          anchor='mm')
                draw.line([(x, 30), (x + 30, 30)], fill="black", width=1)  # Draw a line below the index
                draw.text((x + 15, y + 15), str(number), fill='black',
                          font=ImageFont.truetype("arial.ttf", font_size), anchor='mm')
                draw.rectangle([(x, y), (x + 30, y + 30)], outline='gray',
                               fill=None)  # Draw a rectangle around the numbers
                y -= 30
            x += 30

        return image

    def draw_clues_vertical(self, data):
        width, height = 220, 450
        font_size = 14
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        # Writing numbers and lines on the empty image
        x, y = 0, 0
        for index, line in enumerate(data):
            x = 190
            if line == []:
                line = [0]  # Adds a zero in case tesseract couldn't detect any number
            for number in line[::-1]:
                draw.text((15, y + 15), str(index + 1), fill='black',
                          font=ImageFont.truetype("arial.ttf", font_size), anchor='mm')
                draw.line([(30, y), (30, y + 30)], fill="black", width=1)  # Draw a line on the right of the index
                draw.text((x + 15, y + 15), str(number), fill='black',
                          font=ImageFont.truetype("arial.ttf", font_size), anchor='mm')
                draw.rectangle([(x, y), (x + 30, y + 30)], outline='gray',
                               fill=None)  # Draw a rectangle around the numbers
                x -= 30
            y += 30

        return image

    def draw_final_result(self, info):
        lines = info.strip().split('\n')
        square_size = 40
        height, width = 600, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        for y, line in enumerate(lines):
            x = 0
            for number in line:
                if number == 'O':
                    draw.rectangle([(x, y * square_size), (x + square_size, (y + 1) * square_size)], outline='gray',
                                   fill='black')
                elif number == 'X':
                    draw.rectangle([(x, y * square_size), (x + square_size, (y + 1) * square_size)], outline='gray',
                                   fill='white')
                x += square_size
            y += 1

        return image

    def image_combiner_horizontal(self, global_image_buffer, image_buffer):
        original_image = Image.open(global_image_buffer)
        drawed_image = Image.open(image_buffer)

        width_o, height_o = original_image.size
        width_d, height_d = drawed_image.size

        dimensions_top = (
            int(width_o / 100 * 24.5),  # left
            int(height_o / 100 * 28.5),  # top
            int(width_o),  # width
            int(height_o / 100 * 39.4)  # height
        )

        original_img_crop = original_image.crop(dimensions_top)
        width_o, height_o = original_img_crop.size

        max_width = max(width_o, width_d)
        max_height = height_o + height_d

        final_image = Image.new('RGB', (max_width, max_height), color='white')
        final_image.paste(drawed_image, (0, 0))
        final_image.paste(original_img_crop, (0, height_d))

        return final_image

    def image_combiner_vertical(self, global_image_buffer, image_buffer):
        original_image = Image.open(global_image_buffer)
        drawed_image = Image.open(image_buffer)

        width_o, height_o = original_image.size
        width_d, height_d = drawed_image.size

        dimensions_top = (
            int(width_o / 100 * 0.2),  # left
            int(height_o / 100 * 39.5),  # top
            int(width_o / 100 * 25),  # width
            int(height_o / 100 * 74)  # height
        )

        original_img_crop = original_image.crop(dimensions_top)
        width_o, height_o = original_img_crop.size

        max_width = width_o + width_d
        max_height = max(height_o, height_d)

        final_image = Image.new('RGB', (max_width, max_height), color='white')
        final_image.paste(drawed_image, (0, 0))
        final_image.paste(original_img_crop, (width_d, 0))

        return final_image

# data = [[1, 2], [7, 1, 1, 1], [2, 1, 1], [5, 1, 1], [8, 1], [10], [10], [10, 1], [11, 1], [10, 1], [10, 1], [10, 1], [8, 1], [6, 1], []]
# draw_clues_horizontal(data).save('table_hor.jpg')

# data = [[1, 4], [1, 6], [1, 8], [1, 9], [1, 11], [1, 11], [1, 11], [11], [11], [10], [1, 6], [1, 1, 3], [1, 1, 1], [1, 1, 1, 8], [2, 1]]
# draw_clues_vertical(data).save('table_ver.jpg')

# data = 'XOXXXXXXOOOOXXX\nXOXXXXXOOOOOOXX\nXOXXXXOOOOOOOOX\nXOXXXOOOOOOOOOX\nXOXXOOOOOOOOOOO\nXOXXOOOOOOOOOOO\nXOXOOOOOOOOOOOX\nXXXOOOOOOOOOOOX\nXXOOOOOOOOOOOXX\nXXOOOOOOOOOOXXX\nXOXOOOOOOXXXXXX\nOXOXOOOXXXXXXXX\nXOXOXOXXXXXXXXX\nOXOXOXXOOOOOOOO\nOOXOXXXXXXXXXXX\n'
# draw_final_result(data).save('grid_image.png')
