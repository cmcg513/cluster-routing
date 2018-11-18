"""
Author: Casey McGinley

Reports similar entries in name/address found in CSV data
"""

from difflib import SequenceMatcher
import csv
import string


def sim(a, b):
    """
    Relatively naive similarity check on two strings

    Returns true if the similarity ration is above 0.5
    """
    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio > 0.5


def read_file(filename):
    """
    Read a CSV and parse out the name and address from each line

    Returns a list of parsed entries from the CSV (the line number, the name
    and the address)
    """
    # iterate over the CSV
    data = []
    with open(filename, 'r') as data_file:
        i = 0
        reader = csv.reader(data_file, delimiter=",", quotechar="\"")
        for row in reader:
            # skip header
            if i == 0:
                i += 1
                continue
            i += 1

            # grab just the name and adress
            name = row[5]
            address = row[9]
            # zip_code = row[8]
            # town = row[7]
            # apt = row[10]
            data.append([i, name, address])  # ,town,zip_code,apt])

    return data


def replace_all(s, strip_words):
    """
    Given a string and a list of words to strip, remove these words from the
    string

    Returns the scrubbed string
    """
    for w in strip_words:
        s = s.replace(w, "")
    return s


def process(data):
    """
    Given a list of name and address data, identify and report possible
    duplicates
    """
    # words to scrub from data
    strip_words = [
        'avenue',
        'ave',
        'street',
        'boulevard',
        'blvd',
        'st',
        'road',
        'rd',
        'court',
        'ct',
        'guest',
        'guests',
        'family',
        'spouse',
        'spouses'
    ]
    # quick and dirty translator for scrubbing punctuation from data
    translator = str.maketrans({key: None for key in string.punctuation})
    for i in range(len(data)):
        indx, name, addr = data[i]  # ,zipc,twn,apt

        # scrub the data and normalize to lowercase
        name = name.translate(translator)
        addr = addr.translate(translator)
        name = name.lower()
        addr = addr.lower()
        name = replace_all(name, strip_words)
        addr = replace_all(addr, strip_words)

        # identify similar entries from the remainder of the data
        matches = []
        for j in range(i + 1, len(data)):

            # scrub the data
            n_indx, n_name, n_addr = data[j]  # ,n_zipc,n_twn,n_apt
            n_name = n_name.translate(translator)
            n_addr = n_addr.translate(translator)
            n_name = n_name.lower()
            n_addr = n_addr.lower()
            n_name = replace_all(n_name, strip_words)
            n_addr = replace_all(n_addr, strip_words)
            # print(addr, n_addr)

            # check for similarity
            # TODO: should a report be made if only one of these is similar?
            if sim(name, n_name) and sim(addr, n_addr):
                matches.append(data[j])

        # report the matches found
        if len(matches) > 0:
            tmp = "%d: %s, %s"
            s1 = tmp % tuple(data[i])
            s2 = "*" * 15
            print(s1)
            print(s2)
            for m in matches:
                print(tmp % tuple(m))
            print("\n")


def main():
    """
    Main routine
    """
    # read data from CSV
    data = read_file("raw_data.csv")

    # check data for duplicates
    process(data)


if __name__ == "__main__":
    main()
