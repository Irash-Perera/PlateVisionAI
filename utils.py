import string
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

# Mapping dictionaries for misclassified characters
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}


def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_no', 'car_id', 'car_coordinates',
                                                'license_plate_coordinates', 'license_plate_coordinate_score', 'license_number',
                                                'license_number_score'))

        for frame_no in results.keys():
            for car_id in results[frame_no].keys():
                print(results[frame_no][car_id])
                if 'vehicle' in results[frame_no][car_id].keys() and \
                   'license_plate' in results[frame_no][car_id].keys() and \
                   'text' in results[frame_no][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_no,car_id,                                                  '[{} {} {} {}]'.format(
                                                                results[frame_no][car_id]['vehicle']['coordinates'][0],
                                                                results[frame_no][car_id]['vehicle']['coordinates'][1],
                                                                results[frame_no][car_id]['vehicle']['coordinates'][2],
                                                                results[frame_no][car_id]['vehicle']['coordinates'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_no][car_id]['license_plate']['coordinates'][0],
                                                                results[frame_no][car_id]['license_plate']['coordinates'][1],
                                                                results[frame_no][car_id]['license_plate']['coordinates'][2],
                                                                results[frame_no][car_id]['license_plate']['coordinates'][3]),
                                                            
                                                                results[frame_no][car_id]['license_plate']['coordinates_confidence'],
                                                                results[frame_no][car_id]['license_plate']['text'],
                                                                results[frame_no][car_id]['license_plate']['text_confidence']))
        f.close()


def license_complies_format(text): 
    """
    Check if the license plate text complies with the required format.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text) != 7:
        return False

    if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
       (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
       (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
       (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
       (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
       (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
       (text[6] in string.ascii_uppercase or text[6] in dict_int_to_char.keys()):
        return True
    else:
        return False


def format_license(text):
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = ''
    mapping = {0: dict_int_to_char, 1: dict_int_to_char, 4: dict_int_to_char, 5: dict_int_to_char, 6: dict_int_to_char,
               2: dict_char_to_int, 3: dict_char_to_int}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if text[j] in mapping[j].keys():
            license_plate_ += mapping[j][text[j]]
        else:
            license_plate_ += text[j]

    return license_plate_


def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """

    detections = reader.readtext(license_plate_crop)
    
    for detection in detections:
        text = detection[1]
        confidence = detection[2]
        
        text=text.upper().replace(' ','')
        
        if license_complies_format(text):
            return format_license(text), confidence
    
    return None, None   
        
        
    


def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2 = license_plate

    for track_id in vehicle_track_ids:
        car_x1, car_y1, car_x2, car_y2 = track_id[:4]
        
        if x1 >= car_x1 and y1 >= car_y1 and x2 <= car_x2 and y2 <= car_y2:
            return car_x1, car_y1, car_x2, car_y2, track_id[4]
    
    return -1, -1, -1, -1, -1