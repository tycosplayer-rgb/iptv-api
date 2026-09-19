import unittest
from unittest.mock import patch, PropertyMock

from utils.channel import append_total_data
from utils.config import config
from utils.i18n import t


class RetainUnmatchedChannelsTests(unittest.TestCase):
    def test_append_total_data_keeps_template_misses_when_flag_off(self):
        """Subscribe names that miss the template must still enter channel_data."""
        items = [
            (
                "测试",
                {
                    "CCTV1": [],
                },
            )
        ]
        data = {
            "测试": {
                "CCTV1": [],
            }
        }
        subscribe_result = {
            "CCTV-1": [
                {
                    "url": "http://example.com/cctv1.m3u8",
                    "origin": "subscribe",
                    "ipv_type": "ipv4",
                }
            ],
            "NHK World": [
                {
                    "url": "http://example.com/nhk.m3u8",
                    "origin": "subscribe",
                    "ipv_type": "ipv4",
                }
            ],
            "BBC News": [
                {
                    "url": "http://example.com/bbc.m3u8",
                    "origin": "subscribe",
                    "ipv_type": "ipv4",
                }
            ],
        }
        unmatch_category = t("content.unmatch_channel")
        original_method = dict(config.open_method)

        with patch.object(type(config), "open_method", new_callable=PropertyMock) as method_prop:
            method_prop.return_value = {**original_method, "subscribe": True}
            with patch.object(
                type(config), "open_unmatch_category", new_callable=PropertyMock
            ) as flag_prop:
                flag_prop.return_value = False
                append_total_data(
                    items,
                    data,
                    subscribe_result=subscribe_result,
                    whitelist_maps=None,
                    blacklist=None,
                    reporter=None,
                )

        self.assertIn(unmatch_category, data)
        self.assertIn("NHK World", data[unmatch_category])
        self.assertIn("BBC News", data[unmatch_category])
        self.assertEqual(
            data[unmatch_category]["NHK World"][0]["url"],
            "http://example.com/nhk.m3u8",
        )
        self.assertTrue(
            any(
                item.get("url") == "http://example.com/cctv1.m3u8"
                for item in data["测试"]["CCTV1"]
            )
        )
        self.assertNotIn("CCTV-1", data.get(unmatch_category, {}))


if __name__ == "__main__":
    unittest.main()
