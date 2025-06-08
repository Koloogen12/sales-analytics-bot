import logging
from openai import AsyncOpenAI, OpenAIError
from loader.config import config

logger = logging.getLogger(__name__)

def load_prompt() -> str:
    try:
        with open(config.openai_promt_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"⚠️ Не удалось загрузить promt.txt: {e}")
        return "Ты — эксперт по клиентскому сервису. Дай краткую обратную связь по диалогу менеджера."

async def generate_feedback(dialog: list[dict]) -> str:
    try:
        if not config.openai_token:
            raise OpenAIError("❌ OpenAI API ключ не найден.")

        client = AsyncOpenAI(
            api_key=config.openai_token.strip(),
            base_url="https://openrouter.ai/api/v1"
        )

        prompt = load_prompt()
        messages = [{"role": "system", "content": prompt}]

        for d in dialog:
            text = d.get("text", "").strip()
            if text:
                # GPT должен анализировать как однонаправленный поток от менеджера
                messages.append({"role": "user", "content": text})

        if len(messages) <= 1:
            return "Диалог слишком короткий для анализа."

        logger.info(f"[GPT INPUT]: {messages}")

        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=messages,
            temperature=0.6
        )

        result = response.choices[0].message.content.strip()
        logger.info(f"[GPT RESPONSE]: {result}")
        return result

    except OpenAIError as e:
        logger.error(f"❌ GPT ошибка: {e}")
        return "Ошибка генерации обратной связи."
    except Exception as e:
        logger.exception("❌ Непредвиденная ошибка GPT")
        return "Ошибка генерации обратной связи."
