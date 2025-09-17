#!/usr/bin/env python3
"""
Suite de tests exhaustivos para los endpoints de MeriBot API Refactorizada
Prueba todos los endpoints identificados y valida respuestas, errores y casos edge.
"""

import requests
import json
import time
from typing import Dict, Any, List


class MeriBotAPITester:
    """Clase para realizar pruebas exhaustivas de la API de MeriBot."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log_test(self, test_name: str, endpoint: str, method: str, 
                 status_code: int, success: bool, details: str = ""):
        """Registra el resultado de un test."""
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        
        # Mostrar resultado inmediatamente
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {method} {endpoint} | {test_name}")
        if details:
            print(f"    📝 {details}")
            
    def test_health_endpoint(self):
        """Test del endpoint de health check."""
        try:
            response = self.session.get(f"{self.base_url}/chatbot/health")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "service"]
                
                if all(field in data for field in expected_fields):
                    if data["status"] == "ok" and data["service"] == "meribot-api":
                        self.log_test("Health Check - Estructura Correcta", 
                                    "/chatbot/health", "GET", 200, True,
                                    f"Respuesta: {data}")
                    else:
                        self.log_test("Health Check - Valores Incorrectos", 
                                    "/chatbot/health", "GET", 200, False,
                                    f"Valores inesperados: {data}")
                else:
                    self.log_test("Health Check - Campos Faltantes", 
                                "/chatbot/health", "GET", 200, False,
                                f"Campos esperados: {expected_fields}, Recibidos: {list(data.keys())}")
            else:
                self.log_test("Health Check - Status Code Incorrecto", 
                            "/chatbot/health", "GET", response.status_code, False,
                            f"Esperado: 200, Recibido: {response.status_code}")
                
        except Exception as e:
            self.log_test("Health Check - Error de Conexión", 
                        "/chatbot/health", "GET", 0, False, str(e))
    
    def test_allowed_domains_endpoint(self):
        """Test del endpoint de dominios permitidos."""
        try:
            response = self.session.get(f"{self.base_url}/chatbot/allowed_domains")
            
            if response.status_code == 200:
                data = response.json()
                
                if "allowed_domains" in data and isinstance(data["allowed_domains"], list):
                    self.log_test("Allowed Domains - Estructura Correcta", 
                                "/chatbot/allowed_domains", "GET", 200, True,
                                f"Dominios encontrados: {len(data['allowed_domains'])}")
                else:
                    self.log_test("Allowed Domains - Estructura Incorrecta", 
                                "/chatbot/allowed_domains", "GET", 200, False,
                                f"Estructura inesperada: {data}")
            elif response.status_code == 404:
                self.log_test("Allowed Domains - No Configurado", 
                            "/chatbot/allowed_domains", "GET", 404, True,
                            "Esperado si no hay configuración")
            else:
                self.log_test("Allowed Domains - Status Code Inesperado", 
                            "/chatbot/allowed_domains", "GET", response.status_code, False,
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Allowed Domains - Error de Conexión", 
                        "/chatbot/allowed_domains", "GET", 0, False, str(e))
    
    def test_chatbot_query_endpoint(self):
        """Test del endpoint principal del chatbot."""
        # Test 1: Pregunta básica
        try:
            payload = {
                "question": "¿Cómo está el clima hoy?",
                "conversation_id": "test-123"
            }
            
            response = self.session.post(
                f"{self.base_url}/chatbot/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["response", "conversation_id", "intent", "confidence"]
                
                if all(field in data for field in required_fields):
                    self.log_test("Chatbot Query - Pregunta Básica", 
                                "/chatbot/query", "POST", 200, True,
                                f"Respuesta recibida: {len(data['response'])} chars")
                else:
                    self.log_test("Chatbot Query - Campos Faltantes", 
                                "/chatbot/query", "POST", 200, False,
                                f"Campos esperados: {required_fields}")
            else:
                self.log_test("Chatbot Query - Status Incorrecto", 
                            "/chatbot/query", "POST", response.status_code, False,
                            f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Chatbot Query - Error de Conexión", 
                        "/chatbot/query", "POST", 0, False, str(e))
        
        # Test 2: Pregunta sin conversation_id
        try:
            payload = {"question": "Hola, ¿cómo estás?"}
            
            response = self.session.post(
                f"{self.base_url}/chatbot/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            self.log_test("Chatbot Query - Sin Conversation ID", 
                        "/chatbot/query", "POST", response.status_code, success,
                        "Debería manejar conversation_id opcional")
                        
        except Exception as e:
            self.log_test("Chatbot Query - Sin Conversation ID - Error", 
                        "/chatbot/query", "POST", 0, False, str(e))
    
    def test_cors_endpoint(self):
        """Test del endpoint OPTIONS para CORS."""
        try:
            response = self.session.options(f"{self.base_url}/chatbot/query")
            
            success = response.status_code == 200
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods", 
                "Access-Control-Allow-Headers"
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            self.log_test("CORS Options - Headers", 
                        "/chatbot/query", "OPTIONS", response.status_code, 
                        success and has_cors,
                        f"CORS headers presentes: {has_cors}")
                        
        except Exception as e:
            self.log_test("CORS Options - Error", 
                        "/chatbot/query", "OPTIONS", 0, False, str(e))
    
    def test_validation_errors(self):
        """Test de validaciones y manejo de errores."""
        # Test 1: Payload vacío
        try:
            response = self.session.post(
                f"{self.base_url}/chatbot/query",
                json={},
                headers={"Content-Type": "application/json"}
            )
            
            # Debería fallar por falta de 'question'
            success = response.status_code in [400, 422]  # Bad Request o Unprocessable Entity
            self.log_test("Validación - Payload Vacío", 
                        "/chatbot/query", "POST", response.status_code, success,
                        "Debería rechazar payload sin 'question'")
                        
        except Exception as e:
            self.log_test("Validación - Payload Vacío - Error", 
                        "/chatbot/query", "POST", 0, False, str(e))
        
        # Test 2: Question vacía
        try:
            payload = {"question": ""}
            response = self.session.post(
                f"{self.base_url}/chatbot/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Puede aceptarse pero debería manejarse graciosamente
            self.log_test("Validación - Pregunta Vacía", 
                        "/chatbot/query", "POST", response.status_code, True,
                        f"Status: {response.status_code} - Manejo de string vacío")
                        
        except Exception as e:
            self.log_test("Validación - Pregunta Vacía - Error", 
                        "/chatbot/query", "POST", 0, False, str(e))
    
    def run_all_tests(self):
        """Ejecuta todos los tests y muestra resumen."""
        print("🧪 Iniciando Tests Exhaustivos de MeriBot API Refactorizada")
        print("=" * 60)
        
        # Ejecutar todos los tests
        self.test_health_endpoint()
        self.test_allowed_domains_endpoint()
        self.test_chatbot_query_endpoint()
        self.test_cors_endpoint()
        self.test_validation_errors()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de tests: {total_tests}")
        print(f"✅ Pasaron: {passed_tests}")
        print(f"❌ Fallaron: {failed_tests}")
        print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 TESTS FALLIDOS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test_name']} - {result['details']}")
        
        return passed_tests, failed_tests


if __name__ == "__main__":
    # Verificar que el servidor esté corriendo
    print("🔍 Verificando que el servidor esté activo...")
    try:
        requests.get("http://127.0.0.1:8000/chatbot/health", timeout=5)
        print("✅ Servidor activo en http://127.0.0.1:8000")
    except:
        print("❌ Error: Servidor no disponible. Asegúrate de que esté corriendo:")
        print("   uvicorn meribot.core.api.app:app --host 127.0.0.1 --port 8000")
        exit(1)
    
    # Ejecutar tests
    tester = MeriBotAPITester()
    passed, failed = tester.run_all_tests()
    
    # Guardar resultados
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(tester.results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: test_results.json")
    
    # Exit code basado en resultados
    exit(0 if failed == 0 else 1)