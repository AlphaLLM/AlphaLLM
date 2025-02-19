#ai_process.py

import logging
from cerebras_api import cerebras_response
from polli_text_model import pollinations_text_response
from pplx import perplexity_response
import re

logger = logging.getLogger('AlphaLLM')

async def process_ai_response(message, query, ai_choice):
    if ai_choice["model_name"] == "perplexity":
        response = await perplexity_response(query)
    elif ai_choice["model_name"] == "llama 3.3 70b (fastest)":
        response = cerebras_response(query)
    else:
        response = await pollinations_text_response(query, ai_choice["model_name"])
    await smart_long_messages(message.channel, response)
    logger.info(f"Réponse envoyée pour {ai_choice['role_name']}")

async def smart_long_messages(channel, text: str, max_length: int = 2000):
    if len(text) <= max_length:
        await channel.send(text)
        return

    code_block_regex = r"``````"
    code_blocks = list(re.finditer(code_block_regex, text))
    last_cut = 0
    in_code_block = False
    current_code_block = ""

    for i, match in enumerate(code_blocks):
        start, end = match.span()

        if not in_code_block:
            if start > last_cut:
                text_to_send = text[last_cut:start].strip()
                if text_to_send:
                    await send_text_in_chunks(channel, text_to_send, max_length)

            in_code_block = True
            current_code_block = text[start:end]
            last_cut = end
        else:
            in_code_block = False
            current_code_block += text[last_cut:end]
            await channel.send(current_code_block)
            last_cut = end

    if in_code_block:
        current_code_block += text[last_cut:]
        await channel.send(current_code_block)
    elif last_cut < len(text):
        text_to_send = text[last_cut:].strip()
        if text_to_send:
            await send_text_in_chunks(channel, text_to_send, max_length)

async def send_text_in_chunks(channel, text: str, max_length: int):
    lines = text.splitlines()
    current_message = ""
    for line in lines:
        if len(current_message) + len(line) + 1 > max_length:
            if current_message:
                await channel.send(current_message)
            current_message = ""
        current_message += line + "\n"

    if current_message:
        await channel.send(current_message)
