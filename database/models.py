from tortoise import Model, fields


class Assignment(Model):
    """Задание, назначенное пользователю"""
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(description="ID пользователя Telegram")
    title = fields.CharField(max_length=255, description="Название задания")
    deadline = fields.DatetimeField(description="Дедлайн по заданию")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"<Assignment '{self.title}' для {self.user_id}>"


class Chat(Model):
    """Пользовательский чат с историей сообщений"""
    id = fields.IntField(pk=True)
    telegram_user_id = fields.BigIntField(unique=True, description="Telegram ID")
    name = fields.CharField(max_length=100, description="Имя пользователя")
    username = fields.CharField(max_length=100, null=True, description="Telegram username")  # ✅ добавлено
    messages = fields.JSONField(default=list, description="История сообщений (JSON)")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"<Chat {self.name} ({self.telegram_user_id})>"