from unittest import TestCase

from main import generate_dictionary_of_run_summary


class Test(TestCase):
    def test_generate_dictionary_of_run_summary(self):
        summary = generate_dictionary_of_run_summary("MiSeqDemo/", 2)

        self.assertIsNotNone(summary)
        self.assertIsNotNone(['total_summary'])
        self.assertIsNotNone(['nonindex_summary'])

        self.assertEqual(summary['total_summary']['reads'], 33427731)
        self.assertEqual(summary['total_summary']['reads_pf'], 31275807)
        self.assertEqual(summary['total_summary']['reads_pf__percent'], 93.56)
