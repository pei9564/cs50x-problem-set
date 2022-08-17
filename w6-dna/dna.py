import csv
import sys


def main():

    # Check for command-line usage
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py data.csv sequence.txt")

    # Read database file into a variable
    people = []
    with open(sys.argv[1]) as csvfile:
        datas = csv.DictReader(csvfile)
        for person in datas:
            people.append(person)

    # Read DNA sequence file into a variable
    with open(sys.argv[2]) as dnafile:
        dna_data = dnafile.read()

    # Find longest match of each STR in DNA sequence
    for person_data in people:

        dna_match = []

        for subsequence in person_data:
            if subsequence != "name":
                dna_match.append(longest_match(dna_data, subsequence) == int(person_data[subsequence]))

        if not False in dna_match:
            print(person_data['name'])
            return

    print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
