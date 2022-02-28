import random

import requests

import syllables

from nltk.corpus import words
greater_word_list = words.words()

word_list_link = requests.get("https://raw.githubusercontent.com/first20hours/google-10000-english/master"
                              "/20k.txt", stream=True)
with open('common_words.txt', 'w') as W:
    W.write(word_list_link.text)
with open('common_words.txt', 'r') as f:
    word_list_bad = f.readlines()

word_list = []
for j in word_list_bad:
    word_list.append(j.replace("\n", ""))

file_output = "\n"


def make_rhyme_list(word):
    list_of_rhyming_words = []
    parameter = {"rel_rhy": word}
    request = requests.get("https://api.datamuse.com/words", parameter)

    if request.status_code != 200:
        print("There may have been an issue getting the request")
        exit(1)

    # loads all the rhymes into a list
    rhymes = request.json()
    for i in rhymes:
        list_of_rhyming_words.append(i["word"])

    print(f"Returning {len(list_of_rhyming_words)} words rhyming with {word}")
    return list_of_rhyming_words


def safe_rhyme_word(rhyme_list):  # finds a rhyme that does not contain a space
    out = rhyme_list[random.randrange(len(rhyme_list)) - 1]
    while " " in out or out == "":
        out = rhyme_list[random.randrange(len(rhyme_list)) - 1]

    print(f"Found safe rhyme '{out}'")
    return out


def rhyme_list_safe(rhyme_list):  # ensures that the list has at least one word without a space
    print(f"verifying safety of list: {rhyme_list}")
    if len(rhyme_list) == 0:
        return False
    for i in rhyme_list:
        if " " not in i:
            return True
    return False


def write_line():
    chosen_word = word_list[random.randrange(len(word_list)) - 1]
    chosen_word = write_line_input(chosen_word, False)
    return chosen_word  # allows word to be used to generate the next line


def write_line_input(given_word, use_word_passed):
    total_syl = 0

    if use_word_passed is False:
        # accesses the rhyme API for a random word (ensures that there are rhymes)
        rhyme_list = []
        layer_two_rhyme_list = []
        word = ""
        end_word = ""
        # checks rhyme safety two layers deep
        while len(layer_two_rhyme_list) <= 1 and not rhyme_list_safe(layer_two_rhyme_list):
            rhyme_list = []
            while len(rhyme_list) <= 1 and not rhyme_list_safe(rhyme_list):
                word = word_list[random.randrange(len(word_list)) - 1]
                rhyme_list = make_rhyme_list(word)
            if rhyme_list_safe(rhyme_list):
                print("List is safe, proceeding to layer two checks")
                end_word = safe_rhyme_word(rhyme_list)
                layer_two_rhyme_list = make_rhyme_list(end_word)
            else:
                continue

        print(f"Finding safe rhyme for {word}")
        print(f"Rhyme found! ({end_word})")
    else:
        word = given_word
        rhyme_list = make_rhyme_list(word)

        print(f"Finding safe rhyme for {word}")
        end_word = safe_rhyme_word(rhyme_list)
        print(f"Rhyme found! ({end_word})")

    total_syl += syllables.estimate(end_word)

    out = ""

    # fills rest of the line with random words up to 10 syllables
    while total_syl < 10:
        new_word = word_list[random.randrange(len(word_list)) - 1]
        new_word_syl = syllables.estimate(new_word)
        if new_word_syl + total_syl <= 10:
            out = out + " " + new_word
            total_syl += new_word_syl

    out = out + " " + end_word
    print(f"Finished creating new line: {out}")
    global file_output
    file_output = file_output + out + "\n"

    return end_word


def main(iterations):
    sonnet_list = []
    global file_output
    for k in range(iterations):
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
    main(1000)
