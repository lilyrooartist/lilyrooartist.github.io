#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import post_meta_from_queue as posts


class FacebookPostTests(unittest.TestCase):
    ENV = {'META_LONG_LIVED_TOKEN': 'token', 'FB_PAGE_ID': 'page'}

    def test_video_extensions_ignore_query_string(self):
        self.assertTrue(posts.is_video_url('https://www.lilyroo.com/clip.MP4?fresh=1'))
        self.assertTrue(posts.is_video_url('https://www.lilyroo.com/clip.m4v'))
        self.assertFalse(posts.is_video_url('https://www.lilyroo.com/cover.jpg?format=mp4'))

    def test_dry_run_reports_reel_and_preserves_caption(self):
        result = posts.facebook_post({
            'clip_url': 'https://www.lilyroo.com/clip.mp4?fresh=1',
            'reply_text': 'Watch it',
            'post_type': 'video',
        }, 'The clip', self.ENV, True)

        self.assertEqual(result['mode'], 'video')
        self.assertEqual(result['native_format'], 'reel')
        self.assertEqual(result['text'], 'The clip\n\nWatch it')
        self.assertTrue(result['dry_run'])

    @patch.object(posts, 'append_published_log')
    @patch.object(posts, 'facebook_permalink_url', return_value='https://facebook.com/reel')
    @patch.object(posts, 'api_post_hosted_video', return_value={'success': True})
    @patch.object(posts, 'api_post')
    def test_video_uses_page_reels_flow_and_logs_permalink(self, api_post, hosted_upload, permalink, log):
        api_post.side_effect = [
            {'video_id': 'video-1', 'upload_url': 'https://rupload.facebook.com/upload/video-1'},
            {'success': True},
        ]
        row = {
            'id': 'FP-VIDEO-1',
            'clip_url': 'https://www.lilyroo.com/clip.mp4',
            'reply_text': 'Watch it',
            'post_type': 'video',
            'song': 'The Clip',
        }

        result = posts.facebook_post(row, 'The clip', self.ENV, False)

        self.assertEqual(result['post_id'], 'video-1')
        self.assertEqual(result['post_url'], 'https://facebook.com/reel')
        self.assertEqual(api_post.call_args_list[0].args[0], 'https://graph.facebook.com/v25.0/page/video_reels')
        self.assertEqual(api_post.call_args_list[0].args[1]['upload_phase'], 'start')
        hosted_upload.assert_called_once_with('https://rupload.facebook.com/upload/video-1', row['clip_url'], 'token')
        self.assertEqual(api_post.call_args_list[1].args[1]['upload_phase'], 'finish')
        self.assertEqual(api_post.call_args_list[1].args[1]['video_state'], 'PUBLISHED')
        log.assert_called_once_with(
            'Facebook', 'https://facebook.com/reel', 'The Clip', 'The clip',
            'posted via Meta Graph API', content_id='FP-VIDEO-1',
        )

    @patch.object(posts, 'append_published_log')
    @patch.object(posts, 'facebook_permalink_url', return_value='https://facebook.com/photo')
    @patch.object(posts, 'api_post', return_value={'id': 'photo-1'})
    def test_image_still_uses_photos(self, api_post, permalink, log):
        posts.facebook_post({
            'imagery_url': 'https://www.lilyroo.com/cover.jpg',
            'post_type': 'image',
        }, 'The image', self.ENV, False)

        self.assertTrue(api_post.call_args.args[0].endswith('/page/photos'))
        self.assertEqual(api_post.call_args.args[1]['url'], 'https://www.lilyroo.com/cover.jpg')

    @patch.object(posts, 'append_published_log')
    @patch.object(posts, 'facebook_permalink_url', return_value='https://facebook.com/feed')
    @patch.object(posts, 'api_post', return_value={'id': 'feed-1'})
    def test_text_still_uses_feed(self, api_post, permalink, log):
        posts.facebook_post({'post_type': 'text', 'reply_text': 'Read more'}, 'The post', self.ENV, False)

        self.assertTrue(api_post.call_args.args[0].endswith('/page/feed'))
        self.assertEqual(api_post.call_args.args[1]['message'], 'The post\n\nRead more')


if __name__ == '__main__':
    unittest.main()
