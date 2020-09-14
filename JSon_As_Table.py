import json

def filter_nones(phone_table):
    phone_table_without_nones =[]
    for phone in phone_table:
        if phone != None:
            phone_table_without_nones = phone_table_without_nones + [phone]
    return phone_table_without_nones

def __give_back_phones(word):
    # if case != "success", the word has not been detected, and shall return None
    try:
        if word["case"] != "success":
            return None
    except KeyError:
        return None

    phones = word["phones"]
    #the result is created in the following
    result = []
    try:
        result = [word["alignedWord"]]
    except KeyError:
        return None
    start_time = word["start"]
    #for every phone a triple is created containing (description, start_time, duration)
    for index in range(len(phones)):
        phone = phones[index]
        phone_start_time = start_time
        phone_start_time = round(phone_start_time, 2) #round to 3 digits
        start_time = start_time + phone["duration"]
        phone_duration = phone["duration"]
        phone_expl = phone["phone"]
        result = result + [(phone_expl, phone_start_time, phone_duration)]
    return result

def create_table(source_path):
    table = []
    with open(source_path, "r") as f: 
        json_file = json.load(f)
    try:
        words = json_file["words"]#assign aligned words from Json file
    except:
        return []
    for index in range(len(words)):#for every word give_back_n is started
        word = words[index]
        table.append(__give_back_phones(word))#every word is now added to the result
    return table


#if you want to know ho many words werde not detected by gentle, run the following
# generally not used within LST
def count_not_recognized_words(source_path):
    with open(source_path, "r") as f:#Json File in iO Wrapper packen
        json_file = json.load(f)#Json File als String mit dem Namen json_file einlesen
    words = json_file["words"]#alle aligned Words als String zuweisen aus json
    not_recognized = 0
    for index in range(len(words)):#für jedes Wort soll give_back_n gestartet werden
        word = words[index]
        try:
            if word["case"] != "success":
                not_recognized += 1
        except KeyError:
            not_recognized = not_recognized
    return not_recognized