import json
from collections import defaultdict
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from src.utils.io import read_json, dump_json
from wordcloud_fa import WordCloudFa


class wordcloud_generator:

    """Genenrate wordcloud from a chat telegram chat exported json file  
    """

    def __init__(self, json_file_path: Union[str, Path]):
        """json_file_path : path to telegram chat json file               
        """
        logger.info(f"loading json file from {json_file_path}...")
        self.data = read_json(json_file_path)

        # extracting pure text messgaes from json file
        self.text_content = self.extract_text_messages()
        self.normalizer = Normalizer()
        # loading stop words
        stop_words = open(DATA_DIR / 'PersianStopWords.txt',
                          encoding='utf-8').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))
        self.users_activites = {}

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
        output_dir : Path to output wordcloud image
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


class users_activity:

    """
    extract all users activities such as : 
        - number of questions asked (q_nums)
        - number of general content shared (nq_nums)
        - number of replies in response to other member's questions (ans_replies)
    and store all the info in a json file 
    """

    def __init__(self, json_file_path: Union[str, Path]):
        self.data = read_json(json_file_path)

    @staticmethod
    def is_question(msg):
        text_content = ""
        if isinstance(msg, str):
            text_content = msg
        else:
            text_content.join(
                list(f' {text}' for text in msg if isinstance(text, str)))
        return True if '?' in text_content or '؟' in text_content else False

    def record_user_activities(self, output_file_path: Union[str, Path]):

        user_info = {}
        msg_info = {}
        chat_content = [record for record in self.data['messages']
                        if record['type'] == 'message']

        logger.info("Examining all messages sent in Group Chat")
        for msg in chat_content:

            msg_id = msg['id']
            msg_info[msg_id] = msg_info.get(msg_id, {})
            msg_info[msg_id]['text'] = msg['text']

            user_id = msg['from_id']
            user_info[user_id] = user_info.get(user_id, defaultdict(int))
            user_info[user_id]['name'] = msg['from']

            # checking number of times each user has replied to other's questions
            if 'reply_to_message_id' in msg:
                if msg['reply_to_message_id'] in msg_info and \
                        self.is_question(msg_info[msg['reply_to_message_id']]['text']):
                    user_info[user_id]['ans_replies'] += 1

            # checking number of questions(q_nums) and
            # general content(nq_nums) shared by each user
            else:
                if self.is_question(msg['text']):
                    user_info[user_id]['q_numbers'] += 1
                else:
                    user_info[user_id]['nq_numbers'] += 1

        logger.info(f"""storing all users activity record in : 
                    {output_file_path/'users_activity.json'}""")
        dump_json(user_info, output_file_path/'users_activity.json')


if __name__ == '__main__':

    WC_gen = wordcloud_generator(json_file_path = DATA_DIR / 'cs_stack.json')
    WC_gen.generate_WordCloud(output_dir = DATA_DIR)

    usr_act = users_activity(json_file_path = DATA_DIR / 'cs_stack.json')
    usr_act.record_user_activities(output_file_path = DATA_DIR)
