import numpy as np
import os
from utils import *
from imageprocess import *
from UpNet import UpNet
from MiddleNet import MiddleNet
from DownNet import DownNet
from MetaNet import MetaNet
from NoteProcess import *
from Kanade import Kanade


def get_metadata(model, image_list):
    key, speed = MetaNet(model, image_list)
    return key, int(speed)

def notes_separation(model, adjusted_melody_lines, index):
    score = []
    cross_line_ties = []
    accompany = False
    with open(f'output/up/output{index}.txt', 'w') as fu:
        with open(f'output/middle/output{index}.txt', 'w') as fm:
            with open(f'output/down/output{index}.txt', 'w') as fd:
                for line_idx, (line, upper_bound, lower_bound) in enumerate(adjusted_melody_lines):
                    note_line = []
                    up_image = line[0 : upper_bound -2, :]
                    cropped_image = line[upper_bound : lower_bound, :]
                    column_ranges = vertical_protection(cropped_image)
                    
                    for i, (left, right) in enumerate(column_ranges):
                        middle_image = line[upper_bound:lower_bound,left:right]
                        middle_symbol = MiddleNet(model, middle_image)
                        
                        fm.write(f"{middle_symbol}\n")
                        note = NumberNote(middle_symbol)

                        down_image = line[lower_bound + 1:,left:right]
                        if(np.mean(down_image) < 254.5):
                            down_symbols = DownNet(down_image)
                            for down_symbol in down_symbols:
                                fd.write(f"{down_symbol}\n")
                            note.setDown(down_symbols)

                        note_line.append(note)

                    note_line, accompany = ArrangeLine(note_line, accompany)
                    if(np.mean(up_image) < 254.8):
                        up_symbols = UpNet(up_image, column_ranges)
                        for (target, up_symbol) in up_symbols:
                            fu.write(f"{up_symbol}\n")
                        note_line, cross_line_tie = SetUp(note_line, up_symbols)

                        if len(cross_line_tie) > 0:
                            base = len(score)
                            for cross in cross_line_tie:
                                if cross[0] != -1:
                                    cross_line_ties.append((cross[0]+base, -1))
                                elif cross[1] != -1:
                                    cross_line_ties.append((-1, cross[1]+base))

                    score += note_line
                print(f"{index} finished!")

    score = wholeprocess(score, cross_line_ties)
    return score

def image2midi(image_path, index, meta_model, middle_model):  
    lines = image_segmentation(image_path)
    melody_lines, metadata_lines = melody_line_identification(lines)
    music_key, speed = get_metadata(meta_model, metadata_lines)
    print(music_key, speed)
    adjusted_melody_lines = symbols_adjustment(melody_lines)
    music_score = notes_separation(middle_model, adjusted_melody_lines, index)
    midifile = Kanade(music_key, speed, music_score, index)
    return midifile
        

if __name__ == "__main__":

    train_folder = 'final_test'

    score_index = 0
    meta_model, middle_model = LoadModel(model_type="CNN")

    for score in os.listdir(train_folder):
        if not score.endswith('.jpg'):
            continue
        score_index += 1
        image_path = os.path.join(train_folder, score)
        image2midi(image_path, score.split('.')[0], meta_model, middle_model)