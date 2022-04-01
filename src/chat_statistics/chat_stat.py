import codecs
import json
import os
from collections import Counter
from pathlib import Path
from typing import Union

from hazm import Normalizer, word_tokenize
from loguru import logger
from matplotlib import pyplot as plt
from src.chat_statistics.reshape_farsi import reshape_fa
from src.data import DATA_DIR
from wordcloud_fa import WordCloudFa


class wordcloud_generator:
    """Genenrate wordcloud from a chat telegram chat exported json file  
    """

    def __init__(self, json_file_path: Union[str, Path]):
        """
        Args:
        json_file_path (Union[str,Path]): path to telegram chat exported json file

        """

        logger.info(f"loading json file from {json_file_path}...")
        with open(json_file_path) as f:
            self.data = json.load(f)

        # extracting pure text messgaes from json file
        self.text_content = self.extract_text_messages()
        self.normalizer = Normalizer()
        # loading stop words
        stop_words = open(DATA_DIR / 'PersianStopWords.txt',
                          encoding='utf-8').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))

    @reshape_fa
    def extract_text_messages(self):
        logger.info("extracting text messages...")
        text_content = ""
        for msg in self.data['messages']:
            if isinstance(msg['text'], str):
                text_content += f" {msg['text']}"
            else:
                text_content.join(
                    f" {item}" for item in msg['text'] if isinstance(item, str))
        return text_content

    def generate_WordCloud(self, output_dir: Union[str, Path]):
        """
        Args:
            output_dir: Path to output wordcloud image
        """

        normailized_text = self.normalizer.normalize(self.text_content)
        tokens = word_tokenize(normailized_text)
        filtered_tokens = list(
            filter(lambda word: word not in self.stop_words, tokens))
        filtered_text_msg = ' '.join(filtered_tokens)

        wordcloud = WordCloudFa(persian_normalize=True,
                                background_color='white',
                                max_words=200,
                                width=500,
                                height=600)

        logger.info("generating word cloud...")
        wc = wordcloud.generate(filtered_text_msg)
        logger.info(
            f"saving output word cloud image to {output_dir / 'wordcloud.png'}")
        wc.to_file(output_dir / 'wordcloud.png')
        return wc


if __name__ == '__main__':
    WC_gen = wordcloud_generator(json_file_path=DATA_DIR / 'cs_stack.json')
    wc = WC_gen.generate_WordCloud(DATA_DIR)
