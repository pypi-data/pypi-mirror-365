"""
Testes para o módulo core do PYREST-FRAMEWORK
"""

import unittest
import json
from unittest.mock import Mock, patch
from pyrest.core import PyRestFramework
from pyrest.request import Request
from pyrest.response import Response

class TestPyRestFramework(unittest.TestCase):
    """Testes para a classe PyRestFramework"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = PyRestFramework()
    
    def test_init(self):
        """Testa inicialização do framework"""
        self.assertEqual(len(self.app.routes), 0)
        self.assertEqual(len(self.app.middlewares), 0)
        self.assertEqual(len(self.app.error_handlers), 0)
    
    def test_get_route_decorator(self):
        """Testa criação de rota GET usando decorator"""
        @self.app.get('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'GET')
        self.assertEqual(route.path, '/test')
        self.assertEqual(route.handler, test_handler)
    
    def test_get_route_direct(self):
        """Testa criação de rota GET usando chamada direta"""
        def test_handler(req, res):
            pass
        
        self.app.get('/test', test_handler)
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'GET')
        self.assertEqual(route.path, '/test')
        self.assertEqual(route.handler, test_handler)
    
    def test_post_route(self):
        """Testa criação de rota POST"""
        @self.app.post('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'POST')
        self.assertEqual(route.path, '/test')
    
    def test_put_route(self):
        """Testa criação de rota PUT"""
        @self.app.put('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'PUT')
        self.assertEqual(route.path, '/test')
    
    def test_delete_route(self):
        """Testa criação de rota DELETE"""
        @self.app.delete('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'DELETE')
        self.assertEqual(route.path, '/test')
    
    def test_patch_route(self):
        """Testa criação de rota PATCH"""
        @self.app.patch('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'PATCH')
        self.assertEqual(route.path, '/test')
    
    def test_options_route(self):
        """Testa criação de rota OPTIONS"""
        @self.app.options('/test')
        def test_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.routes), 1)
        route = self.app.routes[0]
        self.assertEqual(route.method, 'OPTIONS')
        self.assertEqual(route.path, '/test')
    
    def test_use_middleware(self):
        """Testa adição de middleware"""
        def test_middleware(req, res):
            pass
        
        self.app.use(test_middleware)
        
        self.assertEqual(len(self.app.middlewares), 1)
        self.assertEqual(self.app.middlewares[0], test_middleware)
    
    def test_error_handler(self):
        """Testa registro de handler de erro"""
        @self.app.error_handler(404)
        def not_found_handler(req, res):
            pass
        
        self.assertEqual(len(self.app.error_handlers), 1)
        self.assertIn(404, self.app.error_handlers)
        self.assertEqual(self.app.error_handlers[404], not_found_handler)
    
    def test_find_route_exact_match(self):
        """Testa busca de rota com match exato"""
        @self.app.get('/test')
        def test_handler(req, res):
            pass
        
        route = self.app._find_route('GET', '/test')
        self.assertIsNotNone(route)
        self.assertEqual(route.path, '/test')
        self.assertEqual(route.method, 'GET')
    
    def test_find_route_with_params(self):
        """Testa busca de rota com parâmetros"""
        @self.app.get('/users/:id')
        def user_handler(req, res):
            pass
        
        route = self.app._find_route('GET', '/users/123')
        self.assertIsNotNone(route)
        self.assertEqual(route.path, '/users/:id')
        self.assertEqual(route.method, 'GET')
    
    def test_find_route_not_found(self):
        """Testa busca de rota inexistente"""
        @self.app.get('/test')
        def test_handler(req, res):
            pass
        
        route = self.app._find_route('GET', '/notfound')
        self.assertIsNone(route)
    
    def test_find_route_wrong_method(self):
        """Testa busca de rota com método errado"""
        @self.app.get('/test')
        def test_handler(req, res):
            pass
        
        route = self.app._find_route('POST', '/test')
        self.assertIsNone(route)
    
    def test_execute_middlewares_success(self):
        """Testa execução bem-sucedida de middlewares"""
        def middleware1(req, res):
            return True
        
        def middleware2(req, res):
            return True
        
        self.app.use(middleware1)
        self.app.use(middleware2)
        
        req = Mock()
        res = Mock()
        
        result = self.app._execute_middlewares(req, res)
        self.assertTrue(result)
    
    def test_execute_middlewares_stop(self):
        """Testa execução de middlewares que param a execução"""
        def middleware1(req, res):
            return True
        
        def middleware2(req, res):
            return False  # Para a execução
        
        self.app.use(middleware1)
        self.app.use(middleware2)
        
        req = Mock()
        res = Mock()
        
        result = self.app._execute_middlewares(req, res)
        self.assertFalse(result)
    
    def test_execute_middlewares_exception(self):
        """Testa execução de middlewares com exceção"""
        def middleware1(req, res):
            return True
        
        def middleware2(req, res):
            raise Exception("Test error")
        
        self.app.use(middleware1)
        self.app.use(middleware2)
        
        req = Mock()
        res = Mock()
        
        result = self.app._execute_middlewares(req, res)
        self.assertFalse(result)
    
    def test_handle_error_with_custom_handler(self):
        """Testa tratamento de erro com handler personalizado"""
        @self.app.error_handler(404)
        def custom_404_handler(req, res):
            res.json({"custom": "404 handler"})
        
        req = Mock()
        res = Mock()
        res.json = Mock()
        
        self.app._handle_error(404, req, res)
        
        res.json.assert_called_once_with({"custom": "404 handler"})
    
    def test_handle_error_default(self):
        """Testa tratamento de erro padrão"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(404, req, res, "Custom message")
        
        res.status.assert_called_once_with(404)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Not Found")
        self.assertEqual(call_args["message"], "Custom message")
    
    def test_handle_error_500(self):
        """Testa tratamento de erro 500"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(500, req, res)
        
        res.status.assert_called_once_with(500)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Internal Server Error")
    
    def test_handle_error_400(self):
        """Testa tratamento de erro 400"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(400, req, res)
        
        res.status.assert_called_once_with(400)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Bad Request")
    
    def test_handle_error_401(self):
        """Testa tratamento de erro 401"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(401, req, res)
        
        res.status.assert_called_once_with(401)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Unauthorized")
    
    def test_handle_error_403(self):
        """Testa tratamento de erro 403"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(403, req, res)
        
        res.status.assert_called_once_with(403)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Forbidden")
    
    def test_handle_error_unknown(self):
        """Testa tratamento de erro desconhecido"""
        req = Mock()
        res = Mock()
        res.status = Mock(return_value=res)
        res.json = Mock()
        
        self.app._handle_error(999, req, res)
        
        res.status.assert_called_once_with(999)
        res.json.assert_called_once()
        call_args = res.json.call_args[0][0]
        self.assertEqual(call_args["error"], "Error")
    
    @patch('pyrest.core.HTTPServer')
    def test_listen(self, mock_httpserver):
        """Testa inicialização do servidor"""
        mock_server = Mock()
        mock_httpserver.return_value = mock_server
        
        @self.app.get('/')
        def home(req, res):
            pass
        
        # Testa com debug=True
        with patch('builtins.print') as mock_print:
            self.app.listen(port=3000, host='localhost', debug=True)
            
            mock_httpserver.assert_called_once_with(('localhost', 3000), unittest.mock.ANY)
            mock_server.serve_forever.assert_called_once()
            mock_print.assert_called()
    
    def test_run_alias(self):
        """Testa que run() é um alias para listen()"""
        with patch.object(self.app, 'listen') as mock_listen:
            self.app.run(port=3000)
            mock_listen.assert_called_once_with(port=3000)

if __name__ == '__main__':
    unittest.main()
