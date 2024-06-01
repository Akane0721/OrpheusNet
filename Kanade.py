from music21 import *

def Kanade(key, speed, score, index): 
    music = stream.Stream()

    major_scale = scale.MajorScale(key)
    pitches = major_scale.getPitches(key, key + '5')  
    pitch_list = []
    for pitch in pitches:
        pitch_list.append(str(pitch))
    
    with open(f'output/score/output{index}.txt', 'w') as f:
        for s in score:
            if(s.name == "0"):  # 休止符
                n = note.Rest()
                n.duration = duration.Duration(s.duration)

            else:
                note_pitch = pitch_list[int(s.name) - 1]
                note_name = note_pitch[0]
                note_octave = int(note_pitch[-1])
                note_shift = 0
                for char in note_pitch[1:-1]:
                    if char == "#":
                        note_shift += 1
                    elif char == "-":
                        note_shift -= 1
                note_shift += s.shift
                
                real_shift = "#" * note_shift if note_shift > 0 else "-" * abs(note_shift)
                real_octave = str(note_octave + s.octave - 4)
                real_note = note_name + real_shift + real_octave

                n = note.Note(real_note)
                n.duration = duration.Duration(s.duration)

            if isinstance(n, note.Note):
                x = n.pitch
                y = n.duration.quarterLength
            elif isinstance(n, note.Rest):
                x = n.name 
                y = n.duration.quarterLength
            
            f.write(f"{x} {y}\n")
            music.append(n)
        
    
    music.insert(0, tempo.MetronomeMark(number=speed))
    midifile = f"output/midi/output{index}.mid"
    music.write('midi', fp=midifile)

    print(f"MIDI Generated: output{index}.mid")

    return midifile

