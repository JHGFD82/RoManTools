import unittest
from src.utils import convert_text, cherry_pick, segment_text, syllable_count, detect_method, validator
from io import StringIO
from unittest.mock import patch
import time


def timeit_decorator(repeats=10):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total_time = 0.0
            result = 0
            for _ in range(repeats):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                total_time += end_time - start_time
            average_time = total_time / repeats
            print(f"Function {func.__name__} executed in average: {average_time:.4f} seconds over {repeats} runs")
            return result

        return wrapper

    return decorator


class TestRomanization(unittest.TestCase):

    # PINYIN CHUNK GENERATION TESTING #
    @timeit_decorator(repeats=100)
    def test_segment_text_basic_valid_syllable_vowel(self):
        result = segment_text('a, e, o, ai, ou', method='py')
        self.assertEqual(result, [['a'], ['e'], ['o'], ['ai'], ['ou']])

    @timeit_decorator(repeats=100)
    def test_segment_text_basic_valid_syllable_initial(self):
        result = segment_text('ba gu zhi ying kai lou yan', method='py')
        self.assertEqual(result, [['ba'], ['gu'], ['zhi'], ['ying'], ['kai'], ['lou'], ['yan']])

    @timeit_decorator(repeats=100)
    def test_segment_text_complex_finals_er_n_ng(self):
        result = segment_text('han xiang ran ling er', method='py')
        self.assertEqual(result, [['han'], ['xiang'], ['ran'], ['ling'], ['er']])

    @timeit_decorator(repeats=100)
    def test_segment_text_complex_edge_cases(self):
        result = segment_text('chen chong zhen', method='py')
        self.assertEqual(result, [['chen'], ['chong'], ['zhen']])

    @timeit_decorator(repeats=100)
    def test_segment_text_multi_syllable_no_apostrophe(self):
        result = segment_text('xiaoming changan wenxin liangxiao', method='py')
        self.assertEqual(result, [['xiao', 'ming'], ['chan', 'gan'], ['wen', 'xin'], ['liang', 'xiao']])

    @timeit_decorator(repeats=100)
    def test_segment_text_multi_syllable_apostrophe(self):
        result = segment_text("chang'an shan'er li'an", method='py')
        self.assertEqual(result, [['chang', 'an'], ['shan', 'er'], ['li', 'an']])

    @timeit_decorator(repeats=100)
    def test_segment_text_multi_syllable_vowel_start(self):
        result = segment_text('anwei aiai ouyang ewei', method='py')
        self.assertEqual(result, [['an', 'wei'], ['ai', 'ai'], ['ou', 'yang'], ['e', 'wei']])

    @timeit_decorator(repeats=100)
    def test_segment_text_invalid_initials(self):
        result = segment_text('xa qo vei', method='py')
        self.assertEqual(result, [['xa'], ['qo'], ['v', 'ei']])

    @timeit_decorator(repeats=100)
    def test_segment_text_invalid_finals(self):
        result = segment_text('banp zhirr mingk', method='py')
        self.assertEqual(result, [['ban', 'p'], ['zhi', 'rr'], ['ming', 'k']])

    @timeit_decorator(repeats=100)
    def test_segment_text_special_cases_er_n_ng(self):
        result = segment_text('sheng deng er han shier', method='py')
        self.assertEqual(result, [['sheng'], ['deng'], ['er'], ['han'], ['shi', 'er']])

    @timeit_decorator(repeats=100)
    def test_segment_text_special_cases_combined_initials(self):
        result = segment_text('shuang huang shun', method='py')
        self.assertEqual(result, [['shuang'], ['huang'], ['shun']])

    @timeit_decorator(repeats=100)
    def test_segment_text_edge_cases_ambiguous_finals(self):
        result = segment_text('wenti linping gangzhi', method='py')
        self.assertEqual(result, [['wen', 'ti'], ['lin', 'ping'], ['gang', 'zhi']])

    @timeit_decorator(repeats=100)
    def test_segment_text_no_valid_finals(self):
        result = segment_text('blar ziang shoing', method='py')
        self.assertEqual(result, [['bla', 'r'], ['zi', 'ang'], ['sho', 'ing']])

    @timeit_decorator(repeats=100)
    def test_segment_text_multi_vowel_combinations(self):
        result = segment_text('ai ei ou uan ie', method='py')
        self.assertEqual(result, [['ai'], ['ei'], ['ou'], ['u', 'an'], ['ie']])

    @timeit_decorator(repeats=100)
    def test_segment_text_one_syllable_edge_case(self):
        result = segment_text('a e ou yi', method='py')
        self.assertEqual(result, [['a'], ['e'], ['ou'], ['yi']])

    @timeit_decorator(repeats=100)
    def test_segment_text_multi_syllable_edge_case_er_n_ng(self):
        result = segment_text('zhuangyuan wenxiang gangren', method='py')
        self.assertEqual(result, [['zhuang', 'yuan'], ['wen', 'xiang'], ['gang', 'ren']])

    @timeit_decorator(repeats=100)
    def test_segment_text_wade_giles(self):
        result = segment_text('ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang '
                              'jenmin', method='wg')
        self.assertEqual(result, [['ni'], ['lin', 'p’ing'], ['shang'], ['ch’an', 'kan'], ['hsiao', 'ming'],
                                  ['yüan', 'yang'], ['erh'], ['shih', 'erh'], ['hsiung'], ['an', 'wei'],
                                  ['feng', 'huang'], ['jen', 'min']])

    @timeit_decorator(repeats=100)
    def test_segment_text_ignore_capitalization(self):
        result = segment_text('Ni linp’ing SHANG ch’ankan Hsiaoming yüanyang erh SHIHERH hsiung Anwei fenghuang '
                              'jenmin', method='wg')
        self.assertEqual(result, [['ni'], ['lin', 'p’ing'], ['shang'], ['ch’an', 'kan'], ['hsiao', 'ming'],
                                  ['yüan', 'yang'], ['erh'], ['shih', 'erh'], ['hsiung'], ['an', 'wei'],
                                  ['feng', 'huang'], ['jen', 'min']])

    # SYLLABLE VALIDATION TESTING #
    @timeit_decorator(repeats=100)
    def test_validator_true(self):
        result = validator('ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang',
                           method='wg')
        self.assertEqual(result, True)

    @timeit_decorator(repeats=100)
    def test_validator_false(self):
        result = validator('ni linp’ing shang ch’anzkan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang',
                           method='wg')
        self.assertEqual(result, False)

    @timeit_decorator(repeats=100)
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
    @timeit_decorator(repeats=100)
    def test_convert_text(self):
        result = convert_text('ni hao chang\'an yuan', method_combination='py_wg')
        self.assertEqual(result, 'ni hao ch’angan yüan')

    @timeit_decorator(repeats=100)
    def test_convert_text_titlecase(self):
        result = convert_text('Ni hao Chang\'an Yuan', method_combination='py_wg')
        self.assertEqual(result, 'Ni hao Ch’angan Yüan')

    @timeit_decorator(repeats=100)
    def test_convert_text_uppercase(self):
        result = convert_text('NI HAO Chang\'an YUAN', method_combination='py_wg')
        self.assertEqual(result, 'NI HAO Ch’angan YÜAN')

    @timeit_decorator(repeats=100)
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

    @timeit_decorator(repeats=100)
    def test_cherry_pick_long(self):
        result = cherry_pick("Bai Juyi lived during the Middle Tang period. This was a period of rebuilding and "
                             "recovery for the Tang Empire, following the An Lushan Rebellion, and following the "
                             "poetically flourishing era famous for Li Bai (701－762), Wang Wei (701－761), and Du Fu ("
                             "712－770). Bai Juyi lived through the reigns of eight or nine emperors, being born in "
                             "the Dali regnal era (766-779) of Emperor Daizong of Tang. He had a long and successful "
                             "career both as a government official and a poet, although these two facets of his "
                             "career seemed to have come in conflict with each other at certain points. Bai Juyi was "
                             "also a devoted Chan Buddhist. Bai Juyi was born in 772 in Taiyuan, Shanxi, "
                             "which was then a few miles from location of the modern city, although he was in "
                             "Zhengyang, Henan for most of his childhood. His family was poor but scholarly, "
                             "his father being an Assistant Department Magistrate of the second-class. At the age of "
                             "ten he was sent away from his family to avoid a war that broke out in the north of "
                             "China, and went to live with relatives in the area known as Jiangnan, more specifically "
                             "Xuzhou. Bai Juyi's official career was initially successful. He passed the jinshi "
                             "examinations in 800. Bai Juyi may have taken up residence in the western capital city "
                             "of Chang'an, in 801. Not long after this, Bai Juyi formed a long friendship with a "
                             "scholar Yuan Zhen. Bai Juyi's father died in 804, and the young Bai spent the "
                             "traditional period of retirement mourning the death of his parent, which he did along "
                             "the Wei River, near to the capital. 806, the first full year of the reign of Emperor "
                             "Xianzong of Tang, was the year when Bai Juyi was appointed to a minor post as a "
                             "government official, at Zhouzhi, which was not far from Chang'an (and also in Shaanxi "
                             "province). He was made a member (scholar) of the Hanlin Academy, in 807, and Reminder "
                             "of the Left from 807 until 815, except when in 811 his mother died, and he spent the "
                             "traditional three-year mourning period again along the Wei River, before returning to "
                             "court in the winter of 814, where he held the title of Assistant Secretary to the "
                             "Prince's Tutor. It was not a high-ranking position, but nevertheless one which he was "
                             "soon to lose. While serving as a minor palace official in 814, Bai managed to get "
                             "himself in official trouble. He made enemies at court and with certain individuals in "
                             "other positions. It was partly his written works which led him into trouble. He wrote "
                             "two long memorials, translated by Arthur Waley as \"On Stopping the War\", "
                             "regarding what he considered to be an overly lengthy campaign against a minor group of "
                             "Tatars; and he wrote a series of poems, in which he satirized the actions of greedy "
                             "officials and highlighting the sufferings of the common folk. At this time, one of the "
                             "post-An Lushan warlords (jiedushi), Wu Yuanji in Henan, had seized control of Zhangyi "
                             "Circuit (centered in Zhumadian), an act for which he sought reconciliation with the "
                             "imperial government, trying to get an imperial pardon as a necessary prerequisite. "
                             "Despite the intercession of influential friends, Wu was denied, thus officially putting "
                             "him in the position of rebellion. Still seeking a pardon, Wu turned to assassination, "
                             "blaming the Prime Minister, Wu Yuanheng, and other officials: the imperial court "
                             "generally began by dawn, requiring the ministers to rise early in order to attend in a "
                             "timely manner; and, on July 13, 815, before dawn, the Tang Prime Minister Wu Yuanheng "
                             "was set to go to the palace for a meeting with Emperor Xianzong. As he left his house, "
                             "arrows were fired at his retinue. His servants all fled, and the assassins seized Wu "
                             "Yuanheng and his horse, and then decapitated him, taking his head with them. The "
                             "assassins also attacked another official who favored the campaign against the "
                             "rebellious warlords, Pei Du, but was unable to kill him. The people at the capital were "
                             "shocked and there was turmoil, with officials refusing to leave their personal "
                             "residences until after dawn. In this context, Bai Juyi overstepped his minor position "
                             "by memorializing the emperor. As Assistant Secretary to the Prince's Tutor, "
                             "Bai's memorial was a breach of protocol — he should have waited for those of censorial "
                             "authority to take the lead before offering his own criticism. This was not the only "
                             "charge which his opponents used against him. His mother had died, apparently caused by "
                             "falling into a well while looking at some flowers, and two poems written by Bai Juyi — "
                             "the titles of which Waley translates as \"In Praise of Flowers\" and \"The New Well\" — "
                             "were used against him as a sign of lack of Filial Piety, one of the Confucian ideals. "
                             "The result was exile. Bai Juyi was demoted to the rank of Sub-Prefect and banished from "
                             "the court and the capital city to Jiujiang, then known as Xun Yang, on the southern "
                             "shores of the Yangtze River in northwest Jiangxi Province. After three years, "
                             "he was sent as Governor of a remote place in Sichuan. At the time, the main travel "
                             "route there was up the Yangzi River. This trip allowed Bai Juyi a few days to visit his "
                             "friend Yuan Zhen, who was also in exile and with whom he explored the rock caves "
                             "located at Yichang. Bai Juyi was delighted by the flowers and trees for which his new "
                             "location was noted. In 819, he was recalled back to the capital, ending his exile.",
                             method_combination='py_wg')
        self.assertEqual(result, "Pai Chüi lived during the Middle T’ang period. This was a period of rebuilding and "
                                 "recovery for the T’ang Empire, following the An Lushan Rebellion, and following the "
                                 "poetically flourishing era famous for Li Pai (701－762), Wang Wei (701－761), "
                                 "and Tu Fu (712－770). Pai Chüi lived through the reigns of eight or nine emperors, "
                                 "being born in the Dali regnal era (766-779) of Emperor Taitsung of T’ang. He had a "
                                 "long and successful career both as a government official and a poet, although these "
                                 "two facets of his career seemed to have come in conflict with each other at certain "
                                 "points. Pai Chüi was also a devoted Ch’an Buddhist. Pai Chüi was born in 772 in "
                                 "T’aiyüan, Shanhsi, which was then a few miles from location of the modern city, "
                                 "although he was in Chengyang, Honan for most of his childhood. His family was poor "
                                 "but scholarly, his father being an Assistant Department Magistrate of the "
                                 "secondclass. At the age of ten he was sent away from his family to avoid a war that "
                                 "broke out in the north of China, and went to live with relatives in the area known "
                                 "as Chiangnan, more specifically Hsüchou. Pai Juyis official career was initially "
                                 "successful. He passed the chinshih examinations in 800. Pai Chüi may have taken up "
                                 "residence in the western capital city of Ch’angan, in 801. Not long after this, "
                                 "Pai Chüi formed a long friendship with a scholar Yüan Chen. Pai Juyis father died "
                                 "in 804, and the young Pai spent the traditional period of retirement mourning the "
                                 "death of his parent, which he did along the Wei River, near to the capital. 806, "
                                 "the first full year of the reign of Emperor Hsientsung of T’ang, was the year when "
                                 "Pai Chüi was appointed to a minor post as a government official, at Chouchih, "
                                 "which was not far from Ch’angan (and also in Shaanxi province). He was made a "
                                 "member (scholar) of the Hanlin Academy, in 807, and Reminder of the Left from 807 "
                                 "until 815, except when in 811 his mother died, and he spent the traditional "
                                 "threeyear mourning period again along the Wei River, before returning to court in "
                                 "the winter of 814, where he held the title of Assistant Secretary to the Princes "
                                 "Tutor. It was not a highranking position, but nevertheless one which he was soon to "
                                 "lose. While serving as a minor palace official in 814, Pai managed to get himself "
                                 "in official trouble. He made enemies at court and with certain individuals in other "
                                 "positions. It was partly his written works which led him into trouble. He wrote two "
                                 "long memorials, translated by Arthur Waley as \"On Stopping the War\", "
                                 "regarding what he considered to be an overly lengthy campaign against a minor group "
                                 "of Tatars; and he wrote a series of poems, in which he satirized the actions of "
                                 "greedy officials and highlighting the sufferings of the common folk. At this time, "
                                 "one of the postAn Lushan warlords (chiehtushih), Wu Yüanchi in Honan, had seized "
                                 "control of Changi Circuit (centered in Chumatien), an act for which he sought "
                                 "reconciliation with the imperial government, trying to get an imperial pardon as a "
                                 "necessary prerequisite. Despite the intercession of influential friends, "
                                 "Wu was denied, thus officially putting him in the position of rebellion. Still "
                                 "seeking a pardon, Wu turned to assassination, blaming the Prime Minister, "
                                 "Wu Yüanheng, and other officials: the imperial court generally began by dawn, "
                                 "requiring the ministers to rise early in order to attend in a timely manner; and, "
                                 "on July 13, 815, before dawn, the T’ang Prime Minister Wu Yüanheng was set to go to "
                                 "the palace for a meeting with Emperor Hsientsung. As he left his house, arrows were "
                                 "fired at his retinue. His servants all fled, and the assassins seized Wu Yüanheng "
                                 "and his horse, and then decapitated him, taking his head with them. The assassins "
                                 "also attacked another official who favored the campaign against the rebellious "
                                 "warlords, P’ei Tu, but was unable to kill him. The people at the capital were "
                                 "shocked and there was turmoil, with officials refusing to leave their personal "
                                 "residences until after dawn. In this context, Pai Chüi overstepped his minor "
                                 "position by memorializing the emperor. As Assistant Secretary to the Princes Tutor, "
                                 "Bais memorial was a breach of protocol — he should have waited for those of "
                                 "censorial authority to take the lead before offering his own criticism. This was "
                                 "not the only charge which his opponents used against him. His mother had died, "
                                 "apparently caused by falling into a well while looking at some flowers, "
                                 "and two poems written by Pai Chüi — the titles of which Waley translates as \"In "
                                 "Praise of Flowers\" and \"The New Well\" — were used against him as a sign of lack "
                                 "of Filial Piety, one of the Confucian ideals. The result was exile. Pai Chüi was "
                                 "demoted to the rank of SubPrefect and banished from the court and the capital city "
                                 "to Chiuchiang, then known as Hsün Yang, on the southern shores of the Yangtze River "
                                 "in northwest Chianghsi Province. After three years, he was sent as Governor of a "
                                 "remote place in Ssuch’uan. At the time, the main travel jout’e there was up the "
                                 "Yangtzu River. This trip allowed Pai Chüi a few days to visit his friend Yüan Chen, "
                                 "who was also in exile and with whom he explored the rock caves located at Ich’ang. "
                                 "Pai Chüi was delighted by the flowers and trees for which his new location was "
                                 "noted. In 819, he was recalled back to the capital, ending his exile.")

    # SYLLABLE_COUNT TESTING #
    @timeit_decorator(repeats=100)
    def test_syllable_count(self):
        result = syllable_count(f"'ni linping shang chang'an xiaoming yuanyang er shier xiong anwei fenghuang "
                                f"renmin shuang yingyong zhongguo qingdao ping'an guangdong hongkong changjiang shen "
                                f"tingma yia shoiji yiin", method='py')
        self.assertEqual(result, [1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 0, 0, 0])

    # METHOD DETECTION TESTING #
    @timeit_decorator(repeats=100)
    def test_detect_method_py(self):
        result = detect_method(f"'ni linping shang chang'an xiaoming yuanyang er shier xiong anwei fenghuang renmin "
                               f"shuang yingyong zhongguo qingdao ping'an guangdong hongkong changjiang shen tingma")
        self.assertEqual(result, ['py'])

    @timeit_decorator(repeats=100)
    def test_detect_method_wg(self):
        result = detect_method(
            f"ni linp’ing shang ch’ankan hsiaoming yüanyang erh shiherh hsiung anwei fenghuang jenmin ")
        self.assertEqual(result, ['wg'])

    @timeit_decorator(repeats=100)
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
    @timeit_decorator(repeats=100)
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
