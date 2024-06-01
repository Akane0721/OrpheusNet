import os

output_dir = "output/score"
standard_answer_dir = "eval/scores"

up_output_dir = "output/up"
up_answer_dir = "eval/up"

middle_output_dir = "output/middle"
middle_answer_dir = "eval/middle"

down_output_dir = "output/down"
down_answer_dir = "eval/down"

def RA_evaluate(i, output_path, standard_answer_path):
    correct_notes = []
    wrong_notes = []

    with open(output_path, "r") as f1, open(standard_answer_path, "r") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

        if len(lines1) != len(lines2):
            raise ValueError(f"{i} Number of lines does not match: {len(lines1)}, {len(lines2)}") 

        for index, (line1, line2) in enumerate(zip(lines1, lines2)):
            data1 = line1.strip().split(' ')
            data2 = line2.strip().split(' ')

            if data1 == data2:
                correct_notes.append((index, data1))
            
            else:
                wrong_notes.append((index, data1))

        if len(correct_notes) < len(lines1):
            print(f"{i}:")
        if len(wrong_notes):
            print(f"Wrong pitch: {wrong_notes}")
    
    return len(lines1), len(correct_notes)

def SA_evaluate(i, output_path, standard_answer_path):
    correct_notes = []
    half_correct_notes = []
    wrong_notes = []

    with open(output_path, "r") as f1, open(standard_answer_path, "r") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

        if len(lines1) != len(lines2):
            raise ValueError(f"{i} Number of lines does not match: {len(lines1)}, {len(lines2)}") 

        for index, (line1, line2) in enumerate(zip(lines1, lines2)):
            data1 = line1.strip().split(' ')
            data2 = line2.strip().split(' ')

            if data1[0] == data2[0] and float(data1[1]) == float(data2[1]):
                correct_notes.append((index, data1))
            
            elif data1[0] == data2[0] and float(data1[1]) != float(data2[1]):
                half_correct_notes.append((index, data1))
            
            else:
                wrong_notes.append((index, data1))

        if len(correct_notes) < len(lines1):
            print(f"{i}-RA:")
        if len(half_correct_notes):
            print(f"Correct pitch but incorrect duration: {half_correct_notes}")
        if len(wrong_notes):
            print(f"Wrong pitch: {wrong_notes}")
    
    return len(lines1), len(correct_notes), len(half_correct_notes)
        
up_total = 0
up_correct = 0

middle_total = 0
middle_correct = 0

down_total = 0
down_correct = 0

total = 0
total_correct = 0
total_half_correct = 0

for i, file in enumerate(os.listdir(output_dir)):
    if not file.endswith(".txt"):
        continue
    
    up_output_path = os.path.join(up_output_dir, file)
    up_answer_path = os.path.join(up_answer_dir, file)
    middle_output_path = os.path.join(middle_output_dir, file)
    middle_answer_path = os.path.join(middle_answer_dir, file)
    down_output_path = os.path.join(down_output_dir, file)
    down_answer_path = os.path.join(down_answer_dir, file)
    
    output_path = os.path.join(output_dir, file)
    standard_answer_path = os.path.join(standard_answer_dir, file.split('.')[0][6:]+".txt")

    try:
        ut,uc = RA_evaluate(file.split('.')[0][6:], up_output_path, up_answer_path)
    except Exception as e:
        print("up: ", e)
        ut = 0
        uc = 0

    try:
        mt,mc = RA_evaluate(file.split('.')[0][6:], middle_output_path, middle_answer_path)
    except Exception as e:
        print("middle: ", e)
        mt = 0
        mc = 0
    
    try:
        dt,dc = RA_evaluate(file.split('.')[0][6:], down_output_path, down_answer_path)
    except Exception as e:
        print("down: ", e)
        dt = 0
        dc = 0

    try:
        t, tc, th = SA_evaluate(file.split('.')[0][6:], output_path, standard_answer_path)
    except Exception as e:
        print("score: ", e)
        t = mt
        tc = mc
        th = 0

    up_total += ut
    up_correct += uc

    middle_total += mt
    middle_correct += mc

    down_total += dt
    down_correct += dc

    total += t
    total_correct += tc
    total_half_correct += th

print("\nRA-up: ", (up_correct / up_total) * 100, "%")
print("RA-middle: ", (middle_correct / middle_total) * 100, "%")
print("RA-down: ", (down_correct / down_total) * 100, "%")
print("SA: ", (total_correct / total + 0.5 * total_half_correct / total) * 100, "%")

