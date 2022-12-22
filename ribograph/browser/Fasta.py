import gzip
import django


class FastaEntry:
    """
    Given a header and a sequence, creates a fasta entry.
    The string representation of the fasta entry consists
    of 50 nts per line.
    Do not change the chunk size (= 50)
    TODO : Consider making header and sequence properties
    Also consider putting more checks here for the input
    """

    def __init__(self, header, sequence):
        self.header = header
        self.sequence = sequence

    def reverse_complement(self):
        complements = {
            "A": "T",
            "a": "t",
            "C": "G",
            "c": "g",
            "G": "C",
            "g": "c",
            "T": "A",
            "t": "a",
            "N": "N",
            "n": "n",
        }
        result = list()

        for i in range(len(self.sequence) - 1, -1, -1):
            try:
                result.append(complements[self.sequence[i]])
            except IndexError:
                error_message = (
                    "Invalid character (%s) in the fasta sequence with header \n"
                    "%s" % (self.sequence[i], self.header)
                )
                raise IOError(error_message)
        self.sequence = "".join(result)

    def __str__(self):
        chunk_size = 50  # Do not change this!
        result_list = [">" + self.header]
        sequence_size = len(self.sequence)
        number_of_remaining_letters = sequence_size
        number_of_processed_letters = 0

        while number_of_remaining_letters > 0:
            if number_of_remaining_letters <= chunk_size:
                result_list.append(self.sequence[number_of_processed_letters:])
                number_of_remaining_letters = 0
                number_of_processed_letters = sequence_size
            else:
                new_number_of_processed_letters = (
                    number_of_processed_letters + chunk_size
                )
                result_list.append(
                    self.sequence[
                        number_of_processed_letters:new_number_of_processed_letters
                    ]
                )
                number_of_remaining_letters -= chunk_size
                number_of_processed_letters = new_number_of_processed_letters

        return "\n".join(result_list)


############################################################################################


class FastaFile:
    """
    This object is used to read fasta files into FastaEntry objects.
    For writing fasta files, we only need FastaEntry objects and using
    their str function, we can convert them to string and write to files.
    Note that it can be used as a context manager as well.
    """

    def __init__(self, file):
        myopen = open
        if file.endswith(".gz"):
            myopen = gzip.open
        if file:
            self.f = myopen(file, "rt")
        else:
            self.f = stdin

        self.current_header = ""
        self.current_sequence = list()

    #####################################################

    def __enter__(self):
        return self

    #####################################################

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    ######################################################

    def __getitem__(self, index):

        for raw_line in self.f:
            line = raw_line.strip()
            if not line:
                continue

            if line[0] == ">":
                if not self.current_header:
                    self.current_header = (line[1:].split())[0]
                    self.current_sequence = list()
                else:
                    this_entry = FastaEntry(
                        header=self.current_header,
                        sequence="".join(self.current_sequence),
                    )
                    self.current_header = (line[1:].split())[0]
                    self.current_sequence = list()
                    return this_entry
            else:
                self.current_sequence.append(line)

        # this returns the last entry
        if len(self.current_sequence) > 0:
            this_entry = FastaEntry(
                header=self.current_header, sequence="".join(self.current_sequence)
            )
            self.current_sequence = list()
            return this_entry

        raise IndexError

    #########################################################

    def __del__(self):
        self.f.close()
