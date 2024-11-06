import pytesseract
import cv2
import numpy as np

class Image_reader:
    def __init__(self,):

        self.custom_config =  r'--psm 7 outputbase digits'
        pytesseract.pytesseract.tesseract_cmd =  r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def cleaning(self, image):
        def white_background(image):
            for y in range(image.shape[0]):
                for x in range(image.shape[1]):
                    if all(image[y, x] >= 195):
                        image[y, x] = [255, 255, 255]
            return image

        white_back_image = white_background(image)
        denoised_image = cv2.fastNlMeansDenoisingColored(white_back_image, None, 20, 10, 7, 50)

        return white_background(denoised_image)

    #Horizontal clues reading (left clues).
    def read_horizontal_clues(self, image):
        width, height = image.size
        
        #Splits the image by digits to make it easier to read. 
        def horizonal_clues_separator(image_separator):
            altura, _, _ = image_separator.shape
            cor_branca = (250, 250, 250)
            imagens_divididas = []

            start = 0
            for y in range(altura - 4):

                for index in range(4):
                    white_column = all(all(pixel >= cor_branca) for pixel in image_separator[y+index, :])

                    if not white_column:
                        break

                if white_column:
                    image_dividida = image_separator[start:y, :]

                    if image_dividida.size > 0:
                        image_dividida = image_separator[start:y+4, :]
                        imagens_divididas.append(image_dividida)
                    start = y + 1

            text = ''
            for img in imagens_divididas:
                text += pytesseract.image_to_string(img, config=self.custom_config)

            text = [int(num) for num in text.split('\n') if num.strip()]
            return text
            
        dimensions_top_pre_cut = (
            int(width / 100 *25.5), #left
            int(height / 100 *28.5), #top
            int(width / 100 *99.8), #width
            int(height / 100 *39.4) #height
        )

        #Cuting only the top clues to remove the background
        pre_cut = image.crop(dimensions_top_pre_cut)
        image_array = np.array(pre_cut)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        final_image = self.cleaning(image_array)

        #Removing vertical lines from the cutted image
        gray = cv2.cvtColor(final_image,cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,10))
        remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(final_image, [c], -1, (255,255,255), 5)

        left_width = 0
        boarder = 0.73
        clue_size = 5.95

        result = []
        for _ in range(15):
            dimensions_top = (
                int(image_array.shape[1] / 100 * left_width),  # left
                int(image_array.shape[1] / 100 * (left_width + clue_size)),  # width
            )

            image_recortada = final_image[:, dimensions_top[0]:dimensions_top[1]] 
            left_width += (clue_size + boarder)  

            result.append(horizonal_clues_separator(image_recortada))

        return result

    #Vertical clues reading (left clues).
    def read_vertical_clues(self, image):
        width, height = image.size
        
        #Splits the image by digits to make it easier to read. 
        def vertical_clues_separator(image_separator):
            _, width, _ = image_separator.shape
            cor_branca = (250, 250, 250)
            imagens_divididas = []

            start = 0
            for x in range(width - 6):

                for index in range(6):
                    white_column = all(all(pixel >= cor_branca) for pixel in image_separator[:, x+index])

                    if not white_column:
                        break

                if white_column:
                    image_dividida = image_separator[:, start:x]
                        
                    if image_dividida.size > 0:
                        image_dividida = image_separator[:, start:x+3]
                        imagens_divididas.append(image_dividida)
                    start = x + 1

            text = ''
            for img in imagens_divididas:
                text += pytesseract.image_to_string(img, config=self.custom_config)

            text = [int(num) for num in text.split('\n') if num.strip()]
            return text
            
        dimensions_left_pre_cut = (
            int(width / 100 *0.2), #left
            int(height / 100 *40), #top
            int(width / 100 *25), #width
            int(height / 100 *74) #height
        )

        #Cuting only the left clues to remove the background
        pre_cut = image.crop(dimensions_left_pre_cut)
        image_array = np.array(pre_cut)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        final_image = self.cleaning(image_array)

        # Removing vertical lines from the cutted image
        gray = cv2.cvtColor(final_image,cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1))
        remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(final_image, [c], -1, (255,255,255), 5)

        top_height = 0
        boarder = 0.73
        clue_size = 5.95

        result = []
        for _ in range(15):
            dimensions_left = (
                int(image_array.shape[0] / 100 * top_height),  # top
                int(image_array.shape[0] / 100 * (top_height + clue_size)),  # height
            )

            image_recortada = final_image[dimensions_left[0]:dimensions_left[1] ,:] 
            top_height += (clue_size + boarder)  

            result.append(vertical_clues_separator(image_recortada))

        return result

    # image = Image.open('img.jpg')

    # print(read_horizontal_clues(image))
    # print(read_vertical_clues(image))
