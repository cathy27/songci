from unittest import TestCase

from nlp.verse import Verse


class TestNlp(TestCase):
    def test_all(self):
        verses = ['春花秋月何时了？往事知多少。小楼昨夜又东风，故国不堪回首月明中。',
                  '雕栏玉砌应犹在，只是朱颜改。问君能有几多愁？恰似一江春水向东流。(雕 通：阑)']
        processor = Verse(verses)
        print(processor.emblem_cut())
