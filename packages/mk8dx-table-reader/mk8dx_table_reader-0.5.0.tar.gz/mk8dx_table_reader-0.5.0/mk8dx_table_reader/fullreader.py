import cv2
import os
from pathlib import Path
import keras
import mk8dx_table_reader.kerasUseModelScores as KS
# import cogs.kerasUseModelPosition as KP
import mk8dx_table_reader.yoloUseModelTable as YTable
import mk8dx_table_reader.yoloUseModelPlayers as YPlayers
import easyocr
import time
import PIL
import numpy as np
from ultralytics import YOLO



class Fullreader:
    """
    Fullreader class to handle the full OCR process for a given image.
    NOTE: As for now the program only works with grayscale images.
       
    Attributes:
        readerEasyOcr (easyocr.Reader): EasyOCR reader instance for text recognition. 
            Used to read player and team names from cropped images of players.
            
        modelScore (keras.Model): Custom Keras model for recognizing scores.
            Used to recognize scores from cropped images of players.
        
        modelPosition (keras.Model): Custom Keras model for recognizing positions.
            Used to recognize positions from cropped images of players. 
            (NOTE: This model is currently NULL because esayocr worked just fine)
        
        modelTablePath (str): Path to the custom YOLO model for table detection.
            Used to recognize the table area in the image, and the number of players in that table if there is one
        
        modelPlayersPath (str): Path to the custom YOLO model for player detection.
            Used to recognize player areas in the image, such as their positions, tags, names, and scores.
    """
    def __init__(self):
        # Initialize the EasyOCR reader for English language
        self.readerEasyOcr = easyocr.Reader(['en'], gpu=True)
        self.modelScore = keras.models.load_model('models/number_recognition_model.h5', compile=False)  # compile=False if custom loss was used
        self.modelTablePath = YOLO('models/detectTable/weights/best.pt')
        self.modelPlayersPath = YOLO('models/detectPlayers/weights/best.pt')
    
    def fullOCR(self, img, teams = "FFA"):
        """_summary_

        :param img: PIL Image object to be processed.
        :type img: PIL.Image.Image

        :raises ValueError: If the image cannot be processed, a ValueError is raised.
        """
        
        # Keep the original PIL Image for cropping operations
        img_pil = img
        
        # Convert PIL Image to RGB (in case it's RGBA or other format)
        try:
            img_rgb = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Image conversion failed: {e}")
        # Convert to numpy array (OpenCV format is BGR, so we need to convert)
        img_np = np.array(img_rgb)
        # Convert RGB to BGR for OpenCV
        img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # Convert the image to grayscale (this was the original failing line)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Convert grayscale back to PIL Image for YOLO processing
        img_gray_pil = PIL.Image.fromarray(img_gray)
        
        players_data = []
        
        # Use grayscale image for YOLO table detection
        first_found, second_boxes = YTable.process_detections(img_gray_pil, self.modelTablePath)
        box = first_found
        
        
        if first_found is not None: 
            tableIMG = img_gray_pil.crop(box)
            
            player_names = []
            player_tags = []
            player_scores = []
            # player_positions = []
            for i, box in enumerate(second_boxes):
                playerIMG = img_gray_pil.crop(box)
                name, score = YPlayers.process_detections(playerIMG, self.modelPlayersPath)
                
                name_results = self.readerEasyOcr.readtext(np.array(playerIMG.crop(name)))
                if name_results:
                    player_names.append(name_results[0][1])
                else: # if easyOCR fails to recognize the name
                    player_names.append("Error")  
                try: 
                    player_scores.append(self.getScores(playerIMG.crop(score)))
                except ValueError as e:
                    player_scores.append("Error")
        else :
            return None # use exceptions
        if teams == "FFA":
            return player_names, player_scores
        return player_names, player_scores

    def getScores(self, tableIMG):
        """
        :param tableIMG: Cropped score image of one player (grayscale needed).
        :type tableIMG: PIL.Image.Image
        
        :return: The recognized single score from the cropped player image.
        :rtype: str
        """
        # Use the model to predict the scores
        # The kerasUseModelScores module will handle grayscale conversion internally
        try :
            scores = KS.recognize_number_from_image(self.modelScore, tableIMG)
            return scores
        except ValueError as e:
            raise ValueError(f"Error processing scores: {e}")

if __name__ == "__main__":
    # Example usage of Fullreader
    
    fullreader = Fullreader()
    folder_path = "dataset/endScreenData"  # Replace with your folder path
    # Get all image files from the folder
    image_extensions = {'.png'}
    image_files = [f for f in os.listdir(folder_path) 
                   if Path(f).suffix.lower() in image_extensions]
    num_img_files = len(image_files)
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        print(f"Processing: {image_file}, Image {i+1}/{num_img_files}")
        # Load the image using PIL
        img = PIL.Image.open(image_path)
        try :
            extractedTableString= fullreader.fullOCR(img)
        except ValueError as e:
            print(f"Error processing {image_file}: {e}")
            continue
        if extractedTableString is None:
            print(f"No table found in {image_file}")
            continue
        for i,player in enumerate(extractedTableString[0]):
            # Assuming result is a list of player data
            print (player + " |" + str(extractedTableString[1][i]))
        