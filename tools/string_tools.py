import re

class StringTools:
    @staticmethod
    def extract_numbers(s):
        return re.findall(r'[-+]?\d*\.?\d+%?', s)

    @staticmethod
    def extract_percentages(s):
        return re.findall(r'(\d+(\.\d+)?)\s*%', s)
