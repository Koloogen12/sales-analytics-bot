import asyncio
from services.gpt_feedback import generate_feedback

async def test():
    dialog = [
        {"author": "manager", "text": "Добрый день! Чем могу помочь?"},
        {"author": "client", "text": "Хочу узнать статус моего заказа."},
        {"author": "manager", "text": "Заказ уже в пути, доставим завтра."}
    ]
    feedback = await generate_feedback(dialog)
    print("📣 GPT Feedback:\n", feedback)

if __name__ == "__main__":
    asyncio.run(test())
