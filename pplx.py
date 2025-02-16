from typing import Dict, Generator, List, Any
from uuid import uuid4
from time import sleep, time
from threading import Thread
from json import loads, dumps
from random import getrandbits
from websocket import WebSocketApp
from requests import Session
import logging
import json
import asyncio

logger = logging.getLogger('AlphaLLM')

class Perplexity:
    def __init__(self, *args, **kwargs) -> None:
        self.session: Session = Session()
        self.request_headers: Dict[str, str] = {
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.session.headers.update(self.request_headers)
        self.timestamp: str = format(getrandbits(32), "08x")
        self.session_id: str = loads(self.session.get(url=f"https://www.perplexity.ai/socket.io/?EIO=4&transport=polling&t={self.timestamp}").text[1:])["sid"]
        self.message_counter: int = 1
        self.base_message_number: int = 420
        self.is_request_finished: bool = True
        self.last_request_id: str = None
        assert (lambda: self.session.post(url=f"https://www.perplexity.ai/socket.io/?EIO=4&transport=polling&t={self.timestamp}&sid={self.session_id}", data='40{"jwt":"anonymous-ask-user"}').text == "OK")(), "Échec de la demande de l'utilisateur anonyme."
        self.websocket: WebSocketApp = self._initialize_websocket()
        self.websocket_thread: Thread = Thread(target=self.websocket.run_forever).start()
        while not (self.websocket.sock and self.websocket.sock.connected):
            sleep(0.1)

    def _initialize_websocket(self) -> WebSocketApp:
        def on_open(ws: WebSocketApp) -> None:
            ws.send("2probe")
            ws.send("5")

        def on_message(ws: WebSocketApp, message: str) -> None:
            if message == "2":
                ws.send("3")
            elif not self.is_request_finished:
                if message.startswith("42"):
                    message_data: Dict[str, Any] = loads(message[2:])
                    content: Dict[str, Any] = message_data[1]
                    if "mode" in content:
                        content.update(loads(content["text"]))
                        content.pop("text")
                    if (not ("final" in content and content["final"])) or ("status" in content and content["status"] == "completed"):
                        self.response_queue.append(content)
                    if message_data[0] == "query_answered":
                        self.last_request_id = content["uuid"]
                        self.is_request_finished = True
                elif message.startswith("43"):
                    message_data: List[Dict[str, Any]] = loads(message[3:])[0]
                    if ("uuid" in message_data and message_data["uuid"] != self.last_request_id) or "uuid" not in message_data:
                        self.response_queue.append(message_data)
                        self.is_request_finished = True

        cookies: str = "; ".join([f"{key}={value}" for key, value in self.session.cookies.get_dict().items()])
        return WebSocketApp(
            url=f"wss://www.perplexity.ai/socket.io/?EIO=4&transport=websocket&sid={self.session_id}",
            header=self.request_headers,
            cookie=cookies,
            on_open=on_open,
            on_message=on_message,
            on_error=lambda ws, err: logger.error(f"Erreur WebSocket : {err}")
        )

    def generate_answer(self, query: str) -> Generator[Dict[str, Any], None, None]:
        self.is_request_finished = False
        self.message_counter = (self.message_counter + 1) % 9 or self.base_message_number * 10
        self.response_queue: List[Dict[str, Any]] = []
        self.websocket.send(str(self.base_message_number + self.message_counter) + dumps(["perplexity_ask", query, {"frontend_session_id": str(uuid4()), "language": "fr-FR", "timezone": "UTC+1", "search_focus": "internet", "frontend_uuid": str(uuid4()), "mode": "concise"}]))
        start_time: float = time()
        while (not self.is_request_finished) or len(self.response_queue) != 0:
            if time() - start_time > 30:
                self.is_request_finished = True
                return {"error": "Délai d'attente dépassé."}
            if len(self.response_queue) != 0:
                yield self.response_queue.pop(0)
        self.websocket.close()

async def perplexity_response(query: str) -> str:
    perplexity_client = Perplexity()
    answers = perplexity_client.generate_answer(query)
    final_response = ""
    final_json = None
    
    for answer in answers:
        try:
            answer_dict = answer if isinstance(answer, dict) else json.loads(answer)
            
            if answer_dict.get('status') == 'completed':
                final_json = answer_dict
                if 'text' in answer_dict:
                    text_dict = json.loads(answer_dict['text']) if isinstance(answer_dict['text'], str) else answer_dict['text']
                    final_response = text_dict.get('answer', '')
                else:
                    final_response = answer_dict.get('answer', '')
                
                if final_response:
                    break
            
            await asyncio.sleep(0)
                            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du décodage JSON de la réponse : {e}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse Perplexity : {e}")
    
    if not final_response:
        logger.warning("Aucune réponse valide n'a été générée")
        final_response = "Désolé, je n'ai pas pu générer une réponse valide."
    
    return final_response
