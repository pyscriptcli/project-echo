"""Tests for modularized MoM exports and audio format detection."""
import unittest
import pandas as pd
from io import BytesIO

from utils.mom_export import (
    export_to_word_template_1,
    export_to_pdf_template_1,
    export_to_word_template_2,
    export_to_pdf_template_2
)
from utils.mom_audio import detect_audio_format


class MoMExportTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            {
                "Discussion Points": "Finalize Q3 Budget and resource allocation.",
                "Action Plan": "Submit revised budget sheets to finance.",
                "Indicative Delivery Date": "October 15, 2026",
                "Person-in-charge": "Dave Policarpio"
            },
            {
                "Discussion Points": "Review client feedback on pilot phase.",
                "Action Plan": "Schedule follow-up call with stakeholder team.",
                "Indicative Delivery Date": "TBD",
                "Person-in-charge": "Carlo Medina"
            }
        ])
        self.meeting_details = {
            "date": "October 10, 2026",
            "time_range": "10:00 AM to 11:00 AM",
            "location": "GreatWork Mega Tower 32F - Board Room",
            "company_name": "Acme Holdings",
            "prime_attendees": ["Dave Policarpio", "Carlo Medina"],
            "external_attendees": ["Jane Doe", "John Smith"],
            "prep_name": "Dave Policarpio",
            "prep_desig": "PRIME Philippines",
            "conf_name": "Jane Doe",
            "conf_desig": "Acme Holdings"
        }
        self.other_discussions = "General team updates and calendar sync for next quarter."

    def test_export_word_template_1(self):
        bio = export_to_word_template_1(self.df, self.meeting_details, self.other_discussions)
        self.assertIsInstance(bio, BytesIO)
        self.assertGreater(len(bio.getvalue()), 1000)

    def test_export_pdf_template_1(self):
        bio = export_to_pdf_template_1(self.df, self.meeting_details, self.other_discussions)
        self.assertIsInstance(bio, BytesIO)
        self.assertGreater(len(bio.getvalue()), 1000)

    def test_export_word_template_2(self):
        bio = export_to_word_template_2(self.df, self.meeting_details, self.other_discussions)
        self.assertIsInstance(bio, BytesIO)
        self.assertGreater(len(bio.getvalue()), 1000)

    def test_export_pdf_template_2(self):
        bio = export_to_pdf_template_2(self.df, self.meeting_details, self.other_discussions)
        self.assertIsInstance(bio, BytesIO)
        self.assertGreater(len(bio.getvalue()), 1000)

    def test_detect_audio_format(self):
        self.assertEqual(detect_audio_format(b"RIFF\x00\x00\x00\x00WAVE"), "wav")
        self.assertEqual(detect_audio_format(b"\x1a\x45\xdf\xa3dummy"), "webm")
        self.assertEqual(detect_audio_format(b"ID3\x03dummy"), "mp3")
        self.assertEqual(detect_audio_format(b"OggSdummy"), "ogg")


if __name__ == "__main__":
    unittest.main()
