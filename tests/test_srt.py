import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_srt import ms, inspect

class TestSRT(unittest.TestCase):
    def test_stamp(self):
        self.assertEqual(ms('00:01:00,000'), 60000)
    def test_valid(self):
        s = '1\n00:00:01,000 --> 00:00:02,000\nHello\n'
        self.assertEqual(inspect(s), [])
    def test_overlap(self):
        s = '1\n00:00:01,000 --> 00:00:03,000\nHello\n\n2\n00:00:02,000 --> 00:00:04,000\nWorld'
        self.assertTrue(any(x['issue'] == 'Overlapping cues' for x in inspect(s)))
    def test_bad_time(self):
        s = '1\n00:00:03,000 --> 00:00:02,000\nHello'
        self.assertTrue(any(x['level']=='ERROR' for x in inspect(s)))
    def test_long_line(self):
        s = '1\n00:00:01,000 --> 00:00:03,000\n' + 'A'*50
        self.assertTrue(any('characters' in x['issue'] for x in inspect(s)))
    def test_source_cue_index_is_reported(self):
        s = '10\n00:00:01,000 --> 00:00:03,000\nHello\n\n20\n00:00:02,000 --> 00:00:04,000\nWorld'
        overlap = [x for x in inspect(s) if x['issue'] == 'Overlapping cues']
        self.assertEqual(overlap, [{'cue': 20, 'level': 'WARNING', 'issue': 'Overlapping cues'}])
    def test_empty_text_has_specific_warning(self):
        s = '7\n00:00:01,000 --> 00:00:02,000\n'
        self.assertEqual(inspect(s), [{'cue': 7, 'level': 'WARNING', 'issue': 'No subtitle text'}])
if __name__ == '__main__': unittest.main()
