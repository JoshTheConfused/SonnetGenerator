import random

import requests

import syllables

word_list_link = requests.get("https://raw.githubusercontent.com/first20hours/google-10000-english/master"
                              "/20k.txt", stream=True)
with open('common_words.txt', 'w') as W:
    W.write(word_list_link.text)
with open('common_words.txt', 'r') as f:
    word_list_bad = f.readlines()

word_list = []
for j in word_list_bad:
    word_list.append(j.replace("\n", ""))

file_output = ""


def make_rhyme_list(word):
    list_of_rhyming_words = []
    parameter = {"rel_rhy": word}
    request = requests.get("https://api.datamuse.com/words", parameter)

    if request.status_code == 200:
        print()
    else:
        print("There may have been an issue getting the request")
        exit(1)

    # loads all the rhymes into a list
    rhymes = request.json()
    for i in rhymes:
        list_of_rhyming_words.append(i["word"])

    return list_of_rhyming_words


def safe_rhyme_word(rhyme_list):  # finds a rhyme that does not contain a space
    out = rhyme_list[random.randrange(len(rhyme_list) - 1)]
    while " " in out:
        out = rhyme_list[random.randrange(len(rhyme_list) - 1)]
    return out


def write_line():
    chosen_word = word_list[random.randrange(len(word_list) - 1)]
    chosen_word = write_line_input(chosen_word, False)
    return chosen_word  # allows word to be used to generate the next line


def write_line_input(given_word, use_word_passed):
    total_syl = 0

    if use_word_passed is False:
        # accesses the rhyme API for a random word (ensures that there are rhymes)
        rhyme_list = []
        while len(rhyme_list) <= 1:
            word = word_list[random.randrange(len(word_list) - 1)]
            rhyme_list = make_rhyme_list(word)

        end_word = safe_rhyme_word(rhyme_list)
    else:
        word = given_word
        rhyme_list = make_rhyme_list(word)

        end_word = safe_rhyme_word(rhyme_list)

    total_syl += syllables.estimate(end_word)

    out = ""

    # fills rest of the line with random words up to 10 syllables
    while total_syl < 10:
        new_word = word_list[random.randrange(len(word_list) - 1)]
        new_word_syl = syllables.estimate(new_word)
        if new_word_syl + total_syl <= 10:
            out = out + " " + new_word
            total_syl += new_word_syl

    out = out + " " + end_word
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
        rhyme_one = write_line()
        write_line_input(rhyme_one, True)
        sonnet_list.append(file_output)
        file_output = ""

    with open('sonnet_out.txt', 'w') as Writer:
        for i in range(len(sonnet_list)):
            Writer.write(f"Sonnet #{i}")
            Writer.write("\n")
            Writer.write(sonnet_list[i])
            Writer.write("\n\n")


if __name__ == "__main__":
    main(1000)
