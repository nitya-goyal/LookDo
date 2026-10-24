"""Offline regression checks: python -m unittest test_demo_reliability (from backend)."""
import asyncio
import json
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch
import io
from fastapi import HTTPException, UploadFile
from app.routes.locate import locate_element

from app.services.ai_service import GemmaAIService, MockAIService


class DemoReliabilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_boxes_only_returned_for_built_in_samples(self):
        for sample_id in ('software-portal', 'account-settings', '', 'unknown'):
            with self.subTest(sample_id=sample_id):
                with patch('app.routes.locate.get_ai_service', return_value=MockAIService()):
                    # Filename alone never grants sample fallback.
                    image = UploadFile(filename='software-portal.png', file=io.BytesIO(b'image'))
                    if sample_id in ('software-portal', 'account-settings'):
                        result = await locate_element(instruction='Open settings', image=image, sample_id=sample_id)
                        self.assertEqual(result.source, 'mock')
                    else:
                        with self.assertRaises(HTTPException) as caught:
                            await locate_element(instruction='Open settings', image=image, sample_id=sample_id)
                        self.assertEqual(caught.exception.status_code, 503)
                        self.assertEqual(caught.exception.detail, 'Live Gemma inference unavailable — please retry')

    async def test_both_demo_commands(self):
        for instruction in ('Open settings', 'Where do I download this?'):
            payload = (await MockAIService().locate_element(b'', instruction)).model_dump()
            valid = NS(text='```json\n' + json.dumps(payload) + '\n```')
            transient = RuntimeError('temporary')
            transient.code = 503
            denied = RuntimeError('denied')
            denied.code = 403
            cases = [
                ([valid], 'gemma', 1),
                ([NS(text=''), valid], 'gemma', 2),
                ([NS(text='{broken'), NS(text='')], 'mock', 2),
                ([transient, valid], 'gemma', 2),
                ([transient, NS(text='{}')], 'mock', 2),
                ([TimeoutError(), TimeoutError()], 'mock', 2),
                ([denied], 'mock', 1),
            ]
            for replies, source, count in cases:
                with self.subTest(instruction=instruction, source=source, count=count):
                    service = GemmaAIService.__new__(GemmaAIService)
                    service.api_key = 'test'
                    service.model = 'gemma-4-31b-it'
                    generate = AsyncMock(side_effect=replies)
                    service._client = NS(aio=NS(models=NS(generate_content=generate)))
                    with patch('app.services.ai_service._downscale_image_for_gemma', return_value=b'image'):
                        result = await service.locate_element(b'image', instruction)
                    self.assertEqual(result.source, source)
                    self.assertEqual(generate.await_count, count)
                    self.assertEqual(result.bounding_box.model_dump(), payload['bounding_box'])
                    self.assertTrue(all(c.kwargs['model'] == service.model for c in generate.await_args_list))
                    if source == 'mock':
                        self.assertIn('Mock fallback', result.explanation)

    async def test_timeout_is_enforced(self):
        service = GemmaAIService.__new__(GemmaAIService)
        service.api_key = 'test'
        service.model = 'gemma-4-31b-it'
        async def stalled(**kwargs):
            await asyncio.sleep(60)
        service._client = NS(aio=NS(models=NS(generate_content=stalled)))
        real_wait = asyncio.wait_for
        async def short_wait(awaitable, timeout):
            self.assertEqual(timeout, 20)
            return await real_wait(awaitable, timeout=0.001)
        with patch('app.services.ai_service._downscale_image_for_gemma', return_value=b'image'), patch('app.services.ai_service.asyncio.wait_for', side_effect=short_wait):
            result = await service.locate_element(b'image', 'Open settings')
        self.assertEqual(result.source, 'mock')
