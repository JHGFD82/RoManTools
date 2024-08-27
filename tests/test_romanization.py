import unittest
from Tools.utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator
from io import StringIO
from unittest.mock import patch


class TestRomanization(unittest.TestCase):

    # PINYIN CHUNK GENERATION TESTING #
    def test_segment_text_basic_valid_syllable_vowel(self):
        result = segment_text('a, e, o, ai, ou', method='py')
        self.assertEqual(result, [['a'], ['e'], ['o'], ['ai'], ['ou']])

    def test_segment_text_basic_valid_syllable_initial(self):
        result = segment_text('ba gu zhi ying kai lou yan', method='py')
        self.assertEqual(result, [['ba'], ['gu'], ['zhi'], ['ying'], ['kai'], ['lou'], ['yan']])

    def test_segment_text_complex_finals_er_n_ng(self):
        result = segment_text('han xiang ran ling er', method='py')
        self.assertEqual(result, [['han'], ['xiang'], ['ran'], ['ling'], ['er']])

    def test_segment_text_complex_edge_cases(self):
        result = segment_text('chen chong zhen', method='py')
        self.assertEqual(result, [['chen'], ['chong'], ['zhen']])

    def test_segment_text_multi_syllable_no_apostrophe(self):
        result = segment_text('xiaoming changan wenxin liangxiao', method='py')
        self.assertEqual(result, [['xiao', 'ming'], ['chan', 'gan'], ['wen', 'xin'], ['liang', 'xiao']])

    def test_segment_text_multi_syllable_apostrophe(self):
        result = segment_text("chang'an shan'er li'an", method='py')
        self.assertEqual(result, [['chang', 'an'], ['shan', 'er'], ['li', 'an']])

    def test_segment_text_multi_syllable_vowel_start(self):
        result = segment_text('anwei aiai ouyang ewei', method='py')
        self.assertEqual(result, [['an', 'wei'], ['ai', 'ai'], ['ou', 'yang'], ['e', 'wei']])

    def test_segment_text_invalid_initials(self):
        result = segment_text('xa qo vei', method='py')
        self.assertEqual(result, [['xa'], ['qo'], ['v', 'ei']])

    def test_segment_text_invalid_finals(self):
        result = segment_text('banp zhirr mingk', method='py')
        self.assertEqual(result, [['ban', 'p'], ['zhi', 'rr'], ['ming', 'k']])

    def test_segment_text_special_cases_er_n_ng(self):
        result = segment_text('sheng deng er han shier', method='py')
        self.assertEqual(result, [['sheng'], ['deng'], ['er'], ['han'], ['shi', 'er']])

    def test_segment_text_special_cases_combined_initials(self):
        result = segment_text('shuang huang shun', method='py')
        self.assertEqual(result, [['shuang'], ['huang'], ['shun']])

    def test_segment_text_edge_cases_ambiguous_finals(self):
        result = segment_text('wenti linping gangzhi', method='py')
        self.assertEqual(result, [['wen', 'ti'], ['lin', 'ping'], ['gang', 'zhi']])

    def test_segment_text_no_valid_finals(self):
        result = segment_text('blar ziang shoing', method='py')
        self.assertEqual(result, [['bla', 'r'], ['zi', 'ang'], ['sho', 'ing']])

    def test_segment_text_multi_vowel_combinations(self):
        result = segment_text('ai ei ou uan ie', method='py')
        self.assertEqual(result, [['ai'], ['ei'], ['ou'], ['u', 'an'], ['ie']])

    def test_segment_text_one_syllable_edge_case(self):
        result = segment_text('a e ou yi', method='py')
        self.assertEqual(result, [['a'], ['e'], ['ou'], ['yi']])

    def test_segment_text_multi_syllable_edge_case_er_n_ng(self):
        result = segment_text('zhuangyuan wenxiang gangren', method='py')
        self.assertEqual(result, [['zhuang', 'yuan'], ['wen', 'xiang'], ['gang', 'ren']])

    def test_segment_text_wade_giles(self):
        result = segment_text('ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang '
                              'jenmin', method='wg')
        self.assertEqual(result, [['ni'], ['lin', 'p’ing'], ['shang'], ['ch’an', 'kan'], ['hsiao', 'ming'],
                                  ['yüan', 'yang'], ['erh'], ['shih', 'erh'], ['hsiung'], ['an', 'wei'],
                                  ['feng', 'huang'], ['jen', 'min']])

    def test_segment_text_ignore_capitalization(self):
        result = segment_text('Ni linp’ing SHANG ch’ankan Hsiaoming yüanyang erh SHIHERH hsiung Anwei fenghuang '
                              'jenmin', method='wg')
        self.assertEqual(result, [['ni'], ['lin', 'p’ing'], ['shang'], ['ch’an', 'kan'], ['hsiao', 'ming'],
                                  ['yüan', 'yang'], ['erh'], ['shih', 'erh'], ['hsiung'], ['an', 'wei'],
                                  ['feng', 'huang'], ['jen', 'min']])

    # SYLLABLE VALIDATION TESTING #
    def test_validator_true(self):
        result = validator('ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang',
                           method='wg')
        self.assertEqual(result, True)

    def test_validator_false(self):
        result = validator('ni linp’ing shang ch’anzkan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang',
                           method='wg')
        self.assertEqual(result, False)

    def test_validator_per_word(self):
        result = validator("ni linpzing shangz chazng'an iaoming yuanng er shizer xiongew anwei fengghuang",
                           method='py', per_word=True)
        self.assertEqual(result, [
            {'word': 'ni', 'syllables': ['ni'], 'valid': [True]},
            {'word': 'linpzing', 'syllables': ['lin', 'pzing'], 'valid': [True, False]},
            {'word': 'shangz', 'syllables': ['shang', 'z'], 'valid': [True, False]},
            {'word': 'chazngan', 'syllables': ['cha', 'zng', 'an'], 'valid': [True, False, True]},
            {'word': 'iaoming', 'syllables': ['i', 'ao', 'ming'], 'valid': [False, True, True]},
            {'word': 'yuanng', 'syllables': ['yuan', 'ng'], 'valid': [True, False]},
            {'word': 'er', 'syllables': ['er'], 'valid': [True]},
            {'word': 'shizer', 'syllables': ['shi', 'zer'], 'valid': [True, False]},
            {'word': 'xiongew', 'syllables': ['xiong', 'e', 'w'], 'valid': [True, True, False]},
            {'word': 'anwei', 'syllables': ['an', 'wei'], 'valid': [True, True]},
            {'word': 'fengghuang', 'syllables': ['feng', 'ghu', 'ang'], 'valid': [True, False, True]}]
                         )

    # ROMANIZATON CONVERSION TESTING #
    def test_convert_text(self):
        result = convert_text('ni hao chang\'an yuan', method_combination='py_wg')
        self.assertEqual(result, 'ni hao ch’angan yüan')

    def test_convert_text_titlecase(self):
        result = convert_text('Ni hao Chang\'an Yuan', method_combination='py_wg')
        self.assertEqual(result, 'Ni hao Ch’angan Yüan')

    def test_convert_text_uppercase(self):
        result = convert_text('NI HAO Chang\'an YUAN', method_combination='py_wg')
        self.assertEqual(result, 'NI HAO Ch’angan YÜAN')

    def test_cherry_pick(self):
        result = cherry_pick("Bai Juyi lived during the Middle Tang period. This was a period of rebuilding and "
                             "recovery for the Tang Empire, following the An Lushan Rebellion, and following the "
                             "poetically flourishing era famous for Li Bai (701－762), Wang Wei (701－761), and Du Fu "
                             "(712－770). Bai Juyi lived through the reigns of eight or nine emperors, being born in "
                             "the Dali regnal era (766-779) of Emperor Daizong of Tang. He had a long and successful "
                             "career both as a government official and a poet, although these two facets of his career "
                             "seemed to have come in conflict with each other at certain points. Bai Juyi was also a "
                             "devoted Chan Buddhist.", method_combination="py_wg")
        self.assertEqual(result, "Pai Chüi lived during the Middle T’ang period. This was a period of rebuilding and "
                                 "recovery for the T’ang Empire, following the An Lushan Rebellion, and following the "
                                 "poetically flourishing era famous for Li Pai (701－762), Wang Wei (701－761), "
                                 "and Tu Fu (712－770). Pai Chüi lived through the reigns of eight or nine emperors, "
                                 "being born in the Dali regnal era (766-779) of Emperor Taitsung of T’ang. He had a "
                                 "long and successful career both as a government official and a poet, although these "
                                 "two facets of his career seemed to have come in conflict with each other at certain "
                                 "points. Pai Chüi was also a devoted Ch’an Buddhist.")

    # SYLLABLE_COUNT TESTING #
    def test_syllable_count(self):
        result = syllable_count(f"'ni linping shang chang'an xiaoming yuanyang er shier xiong anwei fenghuang "
                                f"renmin shuang yingyong zhongguo qingdao ping'an guangdong hongkong changjiang shen "
                                f"tingma yia shoiji yiin", method='py')
        self.assertEqual(result, [1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 0, 0, 0])

    # METHOD DETECTION TESTING #
    def test_detect_method_py(self):
        result = detect_method(f"'ni linping shang chang'an xiaoming yuanyang er shier xiong anwei fenghuang renmin "
                               f"shuang yingyong zhongguo qingdao ping'an guangdong hongkong changjiang shen tingma")
        self.assertEqual(result, ['py'])

    def test_detect_method_wg(self):
        result = detect_method(
            f"ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang jenmin ")
        self.assertEqual(result, ['wg'])

    def test_detect_method_per_word(self):
        result = detect_method(f"ni linping shang chang'an xiaoming yuanyang er shier xiong anwei fenghuang "
                               f"renmin shuang yingyong zhongguo qingdao ping'an guangdong hongkong changjiang shen "
                               f"tingma yia shoiji yiin", per_word=True)
        self.assertEqual(result, [{'word': 'ni', 'methods': ['py', 'wg']},
                                  {'word': 'linping', 'methods': ['py', 'wg']},
                                  {'word': 'shang', 'methods': ['py', 'wg']},
                                  {'word': "chang'an", 'methods': ['py']},
                                  {'word': 'xiaoming', 'methods': ['py']},
                                  {'word': 'yuanyang', 'methods': ['py', 'wg']},
                                  {'word': 'er', 'methods': ['py']},
                                  {'word': 'shier', 'methods': ['py']},
                                  {'word': 'xiong', 'methods': ['py']},
                                  {'word': 'anwei', 'methods': ['py', 'wg']},
                                  {'word': 'fenghuang', 'methods': ['py', 'wg']},
                                  {'word': 'renmin', 'methods': ['py']},
                                  {'word': 'shuang', 'methods': ['py', 'wg']},
                                  {'word': 'yingyong', 'methods': ['py']},
                                  {'word': 'zhongguo', 'methods': ['py']},
                                  {'word': 'qingdao', 'methods': ['py']},
                                  {'word': "ping'an", 'methods': ['py']},
                                  {'word': 'guangdong', 'methods': ['py']},
                                  {'word': 'hongkong', 'methods': ['py']},
                                  {'word': 'changjiang', 'methods': ['py']},
                                  {'word': 'shen', 'methods': ['py', 'wg']},
                                  {'word': 'tingma', 'methods': ['py', 'wg']},
                                  {'word': 'yia', 'methods': []},
                                  {'word': 'shoiji', 'methods': []},
                                  {'word': 'yiin', 'methods': []}]
                         )

    # ERROR_SKIP TESTING #
    def test_segment_text_error_skip(self):
        result = segment_text("Bai Juyi lived during the Middle Tang period.", method='py', error_skip=True)
        self.assertEqual(result, [['bai'], ' ', ['ju', 'yi'], ' ', ['li', 'v', 'e', 'd'], ' ', ['du', 'ring'], ' ',
                                  ['the'], ' ', ['mi', 'ddle'], ' ', ['tang'], ' ', ['pe', 'ri', 'o', 'd'], '.'])

    # CRUMBS TESTING #
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_syllable_count_output(self, mock_stdout):
    #     syllable_count('ni hao', method='py', crumbs=True)
    #     expected_output = ('# Analyzing ni hao #\n'
    #                        '# PY romanization data loaded #\n'
    #                        'n [initial]\n'
    #                        'n|i [final]\n'
    #                        'ni valid: True\n'
    #                        'ni syllable count: 1\n'
    #                        '-----------\n'
    #                        'h [initial]\n'
    #                        'h|ao [final]\n'
    #                        'hao valid: True\n'
    #                        'hao syllable count: 1\n'
    #                        '-----------\n')
    #     self.assertEqual(mock_stdout.getvalue(), expected_output)
    #
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_syllable_count_half_output(self, mock_stdout):
    #     syllable_count('ni haa', method='py', crumbs=True)
    #     expected_output = ('# Analyzing ni haa #\n'
    #                        '# PY romanization data loaded #\n'
    #                        'n [initial]\n'
    #                        'n|i [final]\n'
    #                        'ni valid: True\n'
    #                        'ni syllable count: 1\n'
    #                        '-----------\n'
    #                        'h [initial]\n'
    #                        'h|aa [final]\n'
    #                        'haa valid: False\n'
    #                        'haa syllable count: 0\n'
    #                        '-----------\n')
    #     self.assertEqual(mock_stdout.getvalue(), expected_output)
    #
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_syllable_count_failed_output(self, mock_stdout):
    #     syllable_count('noi haa', method='py', crumbs=True)
    #     expected_output = ('# Analyzing noi haa #\n'
    #                        '# PY romanization data loaded #\n'
    #                        'n [initial]\n'
    #                        'n|oi [final]\n'
    #                        'noi valid: False\n'
    #                        'noi syllable count: 0\n'
    #                        '-----------\n'
    #                        'h [initial]\n'
    #                        'h|aa [final]\n'
    #                        'haa valid: False\n'
    #                        'haa syllable count: 0\n'
    #                        '-----------\n')
    #     self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
