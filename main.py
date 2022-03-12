import random

from datetime import datetime

from json import JSONDecodeError

from os.path import exists

import json

import requests

word_list = []
word_list_json = []
file_output = ""


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

    # print(f"Returning {len(list_of_rhyming_words)} words rhyming with {word}")
    return list_of_rhyming_words


def safe_rhyme_word_index(rhyme_list):  # finds a rhyme that does not contain a space
    index = random.randrange(len(rhyme_list)) - 1
    # makes sure word is easy to use part of speech
    unsafe = True
    while unsafe:
        index = random.randrange(len(rhyme_list)) - 1
        out = rhyme_list[index]
        try:
            unsafe = " " in out['word'] or out['word'] == "" or out['numSyllables'] > 8 or "n" not in out['tags'] and "v" not in \
                     out['tags'] and "adj" not in out['tags'] and "adv" not in out['tags'] and \
                     'tags' not in out
        except KeyError:
            continue

    # print(f"Found safe rhyme '{rhyme_list[index]}'")
    return index


def rhyme_list_safe(rhyme_list):  # ensures that the list has at least one word without a space
    # print(f"verifying safety of list: {rhyme_list}")
    if len(rhyme_list) == 0:
        return False
    for i in rhyme_list:
        try:  # verifies usable parts of speech, accounting for sometimes no data given for that
            has_right_speech_part = "n" in i['tags'] or "v" in i['tags'] or "adj" in i['tags'] or "adv" in i['tags']
        except KeyError:
            continue

        if " " not in i['word'] and has_right_speech_part and i['numSyllables'] < 9:
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

    # print("chosen word: ", chosen_word)
    chosen_word = write_line_input(chosen_word, False)
    return chosen_word  # allows word to be used to generate the next line


def proper_line_word_chooser(part_of_speech, syllable_count, to_ten):
    new_word = {'word': '', 'numSyllables': 10, 'tags': []}
    n_1_syl = new_word['numSyllables']
    tags = new_word['tags']

    iterations = 0

    if to_ten:
        while n_1_syl + syllable_count > 10 or part_of_speech not in tags:
            new_word = word_list_json[random.randrange(len(word_list_json)) - 1]
            try:
                n_1_syl = new_word['numSyllables']
                tags = new_word['tags']
            except KeyError:
                continue
            iterations += 1
            # print(iterations, new_word)
    else:
        while n_1_syl + syllable_count > 10 or part_of_speech not in tags:
            new_word = word_list_json[random.randrange(len(word_list_json)) - 1]
            try:
                n_1_syl = new_word['numSyllables']
                tags = new_word['tags']
            except KeyError:
                continue
            iterations += 1

            cheating_words = {'n': 'dog', 'v': 'run', 'adj': 'smooth', 'adv': 'hard'}
            if iterations > 200:
                new_word = {'word': cheating_words[part_of_speech], 'numSyllables': 1, 'tags': [part_of_speech]}
                break
            # print(iterations, new_word)

    # bool_check = part_of_speech in tags
    # print("part of speech:", part_of_speech, "tags:", tags, "bool:", bool_check)
    # print("iterations", iterations)
    return new_word


def choose_new_word_for_line_fill_to_ten(part_of_speech, syllable_count):
    out = proper_line_word_chooser(part_of_speech, syllable_count, True)
    return out


def choose_new_word_for_line_fill(part_of_speech, syllable_count):
    out = proper_line_word_chooser(part_of_speech, syllable_count, False)
    return out


def fill_line_grammatically(end_word):
    out = ""
    out_list = []
    syllable_count = end_word['numSyllables']

    # get the parts of speech tag from the end word
    part_of_speech_tags = []
    for tag in end_word['tags']:
        if tag == 'n' or tag == 'v' or tag == 'adj' or tag == 'adv':
            part_of_speech_tags.append(tag)
    if len(part_of_speech_tags) > 1:
        part_of_speech = part_of_speech_tags[random.randrange(len(part_of_speech_tags)) - 1]
    else:
        part_of_speech = part_of_speech_tags[0]

    # noun: fill line as noun-verb-noun and then add adjectives/adverbs to fill syllables
    if part_of_speech == 'n':
        new_word = choose_new_word_for_line_fill('n', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        new_word = choose_new_word_for_line_fill('v', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        if syllable_count < 10:
            # print(syllable_count)
            new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
            out_list.insert(2, new_word)
            syllable_count += new_word['numSyllables']

            if syllable_count < 10:
                new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                out_list.insert(1, new_word)
                syllable_count += new_word['numSyllables']

                if syllable_count < 10:
                    new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
                    out_list.insert(0, new_word)
                    syllable_count += new_word['numSyllables']

                    reference = [4, 2, 0]
                    for i in range(3):
                        # print(syllable_count)
                        if syllable_count >= 10:
                            break
                        else:
                            new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                            out_list.insert(reference[i], new_word)
                            syllable_count += new_word['numSyllables']

                    if syllable_count < 10:
                        # print(syllable_count)
                        is_was = random.random()
                        if is_was > 0.5:
                            out_list.insert(0, {'word': 'is', 'numSyllables': 1, 'tags': ['p']})
                        else:
                            out_list.insert(0, {'word': 'was', 'numSyllables': 1, 'tags': ['p']})
                        syllable_count += 1

    # verb: fill line as noun-noun-verb and then add adjectives/adverbs to fill syllables
    if part_of_speech == 'v':
        new_word = choose_new_word_for_line_fill('n', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        new_word = choose_new_word_for_line_fill('n', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        if syllable_count < 10:
            # print(syllable_count)
            new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
            out_list.insert(0, new_word)
            syllable_count += new_word['numSyllables']

            if syllable_count < 10:
                new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                out_list.insert(3, new_word)
                syllable_count += new_word['numSyllables']

                if syllable_count < 10:
                    new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
                    out_list.insert(2, new_word)
                    syllable_count += new_word['numSyllables']

                    reference = [4, 2, 0]
                    for i in range(3):
                        # print(syllable_count)
                        if syllable_count >= 10:
                            break
                        else:
                            new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                            out_list.insert(reference[i], new_word)
                            syllable_count += new_word['numSyllables']

                    if syllable_count < 10:
                        # print(syllable_count)
                        is_was = random.random()
                        if is_was > 0.5:
                            out_list.insert(0, {'word': 'is', 'numSyllables': 1, 'tags': ['p']})
                        else:
                            out_list.insert(0, {'word': 'was', 'numSyllables': 1, 'tags': ['p']})
                        syllable_count += 1

    # adjective: fill line as noun-[is/was]-adjective and adjectives/adverbs to fill syllables
    if part_of_speech == 'adj':
        new_word = choose_new_word_for_line_fill('n', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        is_was = random.random()
        if is_was > 0.5:
            out_list.append({'word': 'is', 'numSyllables': 1, 'tags': ['p']})
        else:
            out_list.append({'word': 'was', 'numSyllables': 1, 'tags': ['p']})
        syllable_count += 1

        if syllable_count < 10:
            # print(syllable_count)
            new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
            out_list.insert(0, new_word)
            syllable_count += new_word['numSyllables']

            if syllable_count < 10:
                new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                out_list.insert(3, new_word)
                syllable_count += new_word['numSyllables']

                if syllable_count < 10:
                    new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                    out_list.insert(0, new_word)
                    syllable_count += new_word['numSyllables']

                    reference = [4, 3, 0]
                    for i in range(3):
                        # print(syllable_count)
                        if syllable_count >= 10:
                            break
                        else:
                            new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                            out_list.insert(reference[i], new_word)
                            syllable_count += new_word['numSyllables']

                    if syllable_count < 10:
                        # print(syllable_count)
                        is_was = random.random()
                        if is_was > 0.5:
                            out_list.insert(0, {'word': 'is', 'numSyllables': 1, 'tags': ['p']})
                        else:
                            out_list.insert(0, {'word': 'was', 'numSyllables': 1, 'tags': ['p']})
                        syllable_count += 1

    # adverb: fill line as noun-[[is/was]-adjective/verb]-adverb and add adjectives/adverbs to fill syllables
    if part_of_speech == 'adv':
        new_word = choose_new_word_for_line_fill('n', syllable_count)
        out_list.append(new_word)
        syllable_count += new_word['numSyllables']

        is_was = random.random()
        if is_was > 0.5:
            out_list.append({'word': 'is', 'numSyllables': 1, 'tags': ['p']})
        else:
            out_list.append({'word': 'was', 'numSyllables': 1, 'tags': ['p']})
        syllable_count += 1

        if syllable_count < 10:
            # print(syllable_count)
            new_word = choose_new_word_for_line_fill_to_ten('v', syllable_count)
            out_list.insert(2, new_word)
            syllable_count += new_word['numSyllables']

            if syllable_count < 10:
                new_word = choose_new_word_for_line_fill_to_ten('adj', syllable_count)
                out_list.insert(0, new_word)
                syllable_count += new_word['numSyllables']

                if syllable_count < 10:
                    new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                    out_list.insert(3, new_word)
                    syllable_count += new_word['numSyllables']

                    reference = [4, 3, 0]
                    for i in range(3):
                        # print(syllable_count)
                        if syllable_count >= 10:
                            break
                        else:
                            new_word = choose_new_word_for_line_fill_to_ten('adv', syllable_count)
                            out_list.insert(reference[i], new_word)
                            syllable_count += new_word['numSyllables']

                    if syllable_count < 10:
                        # print(syllable_count)
                        is_was = random.random()
                        if is_was > 0.5:
                            out_list.insert(0, {'word': 'is', 'numSyllables': 1, 'tags': ['p']})
                        else:
                            out_list.insert(0, {'word': 'was', 'numSyllables': 1, 'tags': ['p']})
                        syllable_count += 1

    # all (at the end or in each section): correct noun and verb pluralization

    if not syllable_count == 10:
        print(f"potential issue, line made with {syllable_count} syllables")
    out_list.append(end_word)
    for word in out_list:
        out += word['word']
        out += " "

    type_list = []
    for word in out_list:
        try:
            type_list.append(word['tags'])
        except KeyError:
            continue
    # print(type_list)
    # print(part_of_speech_tags)
    return out


def write_line_input(given_word, use_word_passed):
    total_syl = 0
    end_word_index = 0
    rhyme_list = []

    if use_word_passed is False:
        # accesses the rhyme API for a random word (ensures that there are rhymes)
        layer_two_rhyme_list = []
        # word = ""
        # end_word = ""
        # checks rhyme safety two layers deep
        while len(layer_two_rhyme_list) <= 1 and not rhyme_list_safe(layer_two_rhyme_list):
            word = word_list_json[random.randrange(len(word_list_json)) - 1]["word"]
            rhyme_list = make_rhyme_list(word)
            while len(rhyme_list) <= 1 and not rhyme_list_safe(rhyme_list):
                word = word_list_json[random.randrange(len(word_list_json)) - 1]["word"]
                rhyme_list = make_rhyme_list(word)
            if rhyme_list_safe(rhyme_list):
                # print("List is safe, proceeding to layer two checks")
                end_word_index = safe_rhyme_word_index(rhyme_list)
                end_word = rhyme_list[end_word_index]['word']
                layer_two_rhyme_list = make_rhyme_list(end_word)
            else:
                continue

        # print(f"Finding safe rhyme for {word}")
        # print(f"Rhyme found! ({end_word})")
    else:
        word = given_word["word"]
        rhyme_list = make_rhyme_list(word)

        # print(f"Finding safe rhyme for {word}")
        end_word_index = safe_rhyme_word_index(rhyme_list)
        end_word = rhyme_list[end_word_index]['word']
        # print(f"Rhyme found! ({end_word})")

    total_syl += rhyme_list[end_word_index]['numSyllables']

    out = fill_line_grammatically(rhyme_list[end_word_index])

    # print(f"Finished creating new line: {out}")
    global file_output
    file_output = file_output + out + "\n"

    return rhyme_list[end_word_index]


def main(iterations):
    start = datetime.now()
    word_list_base = make_word_list()
    sonnet_list = []
    global file_output
    for i in range(iterations):
        if i % 100 == 0:  # changes the seed every 100 poems
            print("Finding new theme for next 100 poems...")
            seed = word_list_base[random.randrange(len(word_list_base)) - 1]
            global word_list_json
            word_list_json = make_line_fill_json(seed, False)  # set to true for debugging
            print("Theme found and successfully loaded!\n")

        print(f"Writing sonnet #{i + 1}:")

        rhyme_one = write_line()
        print("1/14 lines complete")
        rhyme_two = write_line()
        print("2/14 lines complete")
        write_line_input(rhyme_one, True)
        print("3/14 lines complete")
        write_line_input(rhyme_two, True)
        print("4/14 lines complete")
        file_output = file_output + "\n"
        rhyme_one = write_line()
        print("5/14 lines complete")
        rhyme_two = write_line()
        print("6/14 lines complete")
        write_line_input(rhyme_one, True)
        print("7/14 lines complete")
        write_line_input(rhyme_two, True)
        print("8/14 lines complete")
        file_output = file_output + "\n"
        rhyme_one = write_line()
        print("9/14 lines complete")
        rhyme_two = write_line()
        print("10/14 lines complete")
        write_line_input(rhyme_one, True)
        print("11/14 lines complete")
        write_line_input(rhyme_two, True)
        print("12/14 lines complete")
        file_output = file_output + "\n"
        rhyme_one = write_line()
        print("13/14 lines complete")
        write_line_input(rhyme_one, True)
        print("14/14 lines complete \n")
        file_output = "\n" + file_output
        sonnet_list.append(file_output)
        file_output = ""
        with open(f'sonnet_out_#{i + 1}.txt', 'w') as Writer:
            Writer.write(f"Sonnet #{i + 1} \n")
            Writer.write(sonnet_list[i])
    end = datetime.now()

    total_time = end - start
    time_per_poem = total_time.total_seconds() / iterations
    poems_per_hour = round(3600 / time_per_poem)
    print(f'{iterations} sonnet(s) written in {total_time} \n({time_per_poem} seconds per poem) '
          f'\n(about {poems_per_hour} poems per hour)')

    with open('sonnet_out_all.txt', 'w') as Writer:
        Writer.write(f'{iterations} sonnet(s) written in {total_time} \n({time_per_poem} seconds per poem) '
                     f'\n(about {poems_per_hour} poems per hour)')
        Writer.write("\n-------------------------------------------------\n")
        for i in range(len(sonnet_list)):
            Writer.write(f"Sonnet #{i+1} \n")
            Writer.write(sonnet_list[i])
            Writer.write("\n-------------------------------------------------\n")


if __name__ == "__main__":
    # make_test_json()  # not necessary except for debugging purposes
    main(1000)
