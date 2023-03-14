import logging
import re

from datasets import load_dataset
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Word_Cleaner:
    def __init__(
        self,
        counting_avg: float = 0.65,
        number_ratio: float = 0.7,
        short_word_threshold: int = 7,
    ):
        self.number_ratio = number_ratio
        self.counting_avg = counting_avg
        self.short_word_threshold = short_word_threshold

    def clean_pipe(self, sent_list: list) -> list:
        """Runs first counting_length_of_letters_and_if_to_many_remove
            and than counting_sequence_length_of_numbers

        Args:
            sent_list (list): List of sentences with text

        Returns:
            list: Reduced list of sentences
        """

        logging.info(f"Before filtering by length counter: {len(sent_list)}")

        length_filter_sent_list = self.counting_length_of_letters_and_if_to_many_remove(
            sent_list
        )
        logging.info(
            f"After filtering by length counter: {len(length_filter_sent_list)}"
        )

        number_and_length_filter_sent_list = self.counting_sequence_length_of_numbers(
            length_filter_sent_list
        )

        logging.info(
            f"After filtering by length counter: {len(number_and_length_filter_sent_list)}"
        )

        return number_and_length_filter_sent_list

    def counting_length_of_letters_and_if_to_many_remove(self, sent_list: list) -> list:
        """This function takes a list of sentences and counts the number of long and short words in each sentence.
        If the average length of words in a sentence is greater than the threshold value or the length of the sentence
        (each word) is less than 10, the sentence is added to a new list.

        Args:
            sent_list (list): A list of sentences to be processed.

        Returns:
            list: A new list containing the sentences with a number ratio less than the threshold or less than the
            short_word_threshold (default 7) words
        """

        new_sent_list = []
        for sent in tqdm(sent_list, desc="Length counter filtering in progress"):
            splitted_sent = sent.split()
            counter_word_length = {"long": 0, "short": 0}
            for word in splitted_sent:
                if len(word) > 1:
                    counter_word_length["long"] += 1
                else:
                    counter_word_length["short"] += 1
            counter_ratio = (counter_word_length["long"] + 0.5) / (
                counter_word_length["short"] + 0.001
            )
            counter_ratio_len = 1 - (
                counter_word_length["short"] / (len(splitted_sent) + 0.1)
            )
            counter_avg = (counter_ratio + counter_ratio_len) / 2

            if counter_avg > self.counting_avg:
                new_sent_list.append(sent)

            elif len(splitted_sent) < self.short_word_threshold:
                new_sent_list.append(sent)

        return new_sent_list

    def counting_sequence_length_of_numbers(self, sent_list) -> list:
        """This function takes a list of sentences and counts the number of words that contain digits in each sentence.
        If the ratio of the number of words containing digits to the number of words not containing digits in a sentence
        is less than the threshold value, the sentence is added to a new list.

        Args:
            sent_list (list): A list of sentences to be processed.

        Returns:
            list: A new list containing the sentences with a number ratio less than the threshold.
        """

        new_sent_list = []
        for sent in tqdm(sent_list, desc="Number counter filtering in progress"):
            if not self._has_numbers(sent):
                new_sent_list.append(sent)
            else:
                splitted_sent = sent.split()
                counter_word_length = {"digit": 0, "not_digit": 0}
                for word in splitted_sent:
                    if self._has_numbers(word):
                        counter_word_length["digit"] += 1
                    else:
                        counter_word_length["not_digit"] += 1
                number_ratio = counter_word_length["digit"] / (
                    counter_word_length["not_digit"] + 0.01
                )
                if number_ratio < self.number_ratio:
                    new_sent_list.append(sent)
        return new_sent_list

    def _has_numbers(self, inputString):
        return bool(re.search(r"\d", inputString))


if __name__ == "__main__":

    # dataset = load_dataset("Riksarkivet/mini_raw_diachronic_swe")
    # dataset_list = dataset["train"].select(range(100000))["text"]

    test_sent_length = [
        "Psykologiska g å t o r hej hej ",
        "En q w e r t q e t u q t h d s  rättegång för sextio år sedan.\n",
        "I en vacker salon på ett litet l a n d t s t ä l l e nära floden, ett par mil ifrån London",
        "— Nej, troligen icke, — svarade Astley förvånad och kännande sina misstankar.",
        "— Gott Godt!",
        "heJ »» HEJ» The     quick brown    fox, Augusta på 	Isa, o c h Isa p å A u g u s t",
        "I en vac k e r s a l o n på e t t l i t e t l a n d t s t älle nära floden, ett par mil ifrån London.",
        "— God t !",
    ]

    cleaner = Word_Cleaner()
    cl_sent_list = cleaner.clean_pipe(sent_list=test_sent_length)
    print(cl_sent_list)