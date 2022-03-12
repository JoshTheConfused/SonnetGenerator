import random

from json import JSONDecodeError

from os.path import exists

import json

import requests

import syllables

word_list = []
word_list_json = []
file_output = "\n"


def make_word_list():  # creates a list of words which may safely be used to generate the words available for the poem
    if not exists('common_words.txt'):  # only creates file once
        word_list_link = requests.get("https://raw.githubusercontent.com/hugsy/stuff/main/random-word/english-nouns.txt"
                                      , stream=True)
        with open('common_words.txt', 'w') as W:
            W.write(word_list_link.text)
        with open('common_words.txt', 'r') as f:
            word_list_bad = f.readlines()

        reduced_word_list = []
        with open('common_words.txt', 'w') as W:
            for word in word_list_bad:
                stripped_word = word.strip("\n")
                request = requests.get(f"https://api.datamuse.com/words?rel_trg={stripped_word}&md=ps", stream=True)
                try:
                    _json = request.json()
                except JSONDecodeError:
                    continue
                if len(_json) > 5:
                    reduced_word_list.append(stripped_word)
                    W.write(word)
    else:  # if file exists, simply read all data from it
        with open('common_words.txt', 'r') as f:
            word_list_bad = f.readlines()

        reduced_word_list = []
        for word in word_list_bad:
            reduced_word_list.append(word.strip("\n"))

    return reduced_word_list


def make_test_json():
    # not called during typical program run, just creates a json file that doesn't have to be re-generated every time
    line_fill_words = json.dumps(make_line_fill_json("love", False))
    with open('test_json.json', 'w') as W:
        for word in line_fill_words:
            W.write(word)


def make_line_fill_json(seed_word, use_test):
    line_fill_words = []
    if not use_test:
        request = requests.get(f"https://api.datamuse.com/words?rel_trg={seed_word}&md=ps", stream=True)

        if request.status_code != 200:
            print("There may have been an issue getting the request")
            exit(1)

        # loads all the rhymes into a list
        line_fill_words_base = request.json()
        _ = "word"
        for word in line_fill_words_base:
            _json = requests.get(f"https://api.datamuse.com/words?rel_trg={word[_]}"f"&md=ps", stream=True).json()
            for element in _json:
                line_fill_words.append(element)
            _json = requests.get(f"https://api.datamuse.com/words?rel_jja={word[_]}"f"&md=ps", stream=True).json()
            for element in _json:
                line_fill_words.append(element)
            _json = requests.get(f"https://api.datamuse.com/words?rel_jjb={word[_]}"f"&md=ps", stream=True).json()
            for element in _json:
                line_fill_words.append(element)
    else:
        with open('test_json.json', 'r') as R:
            line_fill_words = json.load(R)

    return line_fill_words


def make_rhyme_list(word):
    request = requests.get(f"https://api.datamuse.com/words?rel_rhy={word}"f"&md=p", stream=True)

    if request.status_code != 200:
        print("There may have been an issue getting the request")
        exit(1)

    # loads all the rhymes into a list
    rhymes = request.json()
    list_of_rhyming_words = []
    for i in rhymes:
        try:
            list_of_rhyming_words.append(i)
        except AttributeError:
            continue

    print(f"Returning {len(list_of_rhyming_words)} words rhyming with {word}")
    return list_of_rhyming_words


def safe_rhyme_word_index(rhyme_list):  # finds a rhyme that does not contain a space
    index = random.randrange(len(rhyme_list)) - 1
    out = rhyme_list[index]
    while " " in out['word'] or out['word'] == "":
        index = random.randrange(len(rhyme_list)) - 1
        out = rhyme_list[index]

    print(f"Found safe rhyme '{rhyme_list[index]}'")
    return index


def rhyme_list_safe(rhyme_list):  # ensures that the list has at least one word without a space
    print(f"verifying safety of list: {rhyme_list}")
    if len(rhyme_list) == 0:
        return False
    for i in rhyme_list:
        if " " not in i['word']:
            return True
    return False


def write_line():
    global word_list_json
    chosen_word = ""
    iterations = random.randrange(len(word_list_json)) - 1
    cycles = 0
    for i in word_list_json:
        if cycles == iterations:
            chosen_word = i
            break
        cycles += 1

    print("chosen word: ", chosen_word)
    chosen_word = write_line_input(chosen_word, False)
    return chosen_word  # allows word to be used to generate the next line


def fill_line_grammatically(end_word):
    out = ""
    syllable_count = end_word['numSyllables']

    out += end_word['word']
    return out


def write_line_input(given_word, use_word_passed):
    total_syl = 0
    end_word_index = 0
    rhyme_list = []

    if use_word_passed is False:
        # accesses the rhyme API for a random word (ensures that there are rhymes)
        layer_two_rhyme_list = []
        word = ""
        end_word = ""
        # checks rhyme safety two layers deep
        while len(layer_two_rhyme_list) <= 1 and not rhyme_list_safe(layer_two_rhyme_list):
            while len(rhyme_list) <= 1 and not rhyme_list_safe(rhyme_list):
                word = word_list_json[random.randrange(len(word_list_json)) - 1]["word"]
                rhyme_list = make_rhyme_list(word)
            if rhyme_list_safe(rhyme_list):
                print("List is safe, proceeding to layer two checks")
                end_word_index = safe_rhyme_word_index(rhyme_list)
                end_word = rhyme_list[end_word_index]['word']
                layer_two_rhyme_list = make_rhyme_list(end_word)
            else:
                continue

        print(f"Finding safe rhyme for {word}")
        print(f"Rhyme found! ({end_word})")
    else:
        word = given_word["word"]
        rhyme_list = make_rhyme_list(word)

        print(f"Finding safe rhyme for {word}")
        end_word_index = safe_rhyme_word_index(rhyme_list)
        end_word = rhyme_list[end_word_index]['word']
        print(f"Rhyme found! ({end_word})")

    total_syl += rhyme_list[end_word_index]['numSyllables']

    out = ""

    # fills rest of the line with random words up to 10 syllables
    while total_syl < 10:
        new_word = word_list_json[random.randrange(len(word_list_json)) - 1]["word"]
        new_word_syl = syllables.estimate(new_word)
        if new_word_syl + total_syl <= 10:
            out = out + " " + new_word
            total_syl += new_word_syl

    out = out + " " + end_word
    print(f"Finished creating new line: {out}")
    global file_output
    file_output = file_output + out + "\n"

    return rhyme_list[end_word_index]


def main(iterations):
    word_list_base = make_word_list()
    sonnet_list = []
    global file_output
    for k in range(iterations):
        if k % 100 == 0:  # changes the seed every 100 poems
            seed = word_list_base[random.randrange(len(word_list_base)) - 1]
            global word_list_json
            word_list_json = make_line_fill_json(seed, True)  # TODO remember to set this to false
        for i in range(3):
            rhyme_one = write_line()
            rhyme_two = write_line()
            write_line_input(rhyme_one, True)
            write_line_input(rhyme_two, True)
            file_output = file_output + "\n"
        rhyme_one = write_line()
        write_line_input(rhyme_one, True)
        sonnet_list.append(file_output)
        file_output = ""
        with open(f'sonnet_out_#{k}.txt', 'w') as Writer:
            Writer.write(f"Sonnet #{k} \n")
            Writer.write(sonnet_list[k])


if __name__ == "__main__":
    # make_test_json()  # not necessary except for debugging purposes
    main(10)
