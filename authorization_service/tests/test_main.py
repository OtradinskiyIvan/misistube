import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMainApp(unittest.TestCase):

    @patch('shared.database.session.init_engine')
    @patch('shared.database.session.Base', new_callable=MagicMock)
    def test_app_imports_and_routes(self, mock_base, mock_init_engine):
        """Тест без реального подключения к БД"""
        from src.main import app

        self.assertTrue(hasattr(app, "title"))
        routes = [route.path for route in app.routes]
        self.assertTrue(any(r.startswith('/api/v1/auth') for r in routes))
