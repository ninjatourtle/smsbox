# SMSBox Telegram Contract Analyzer

Этот репозиторий содержит Telegram‑бота для анализа договоров на русском языке.
Он оценивает риски, находит «подводные камни» и делает краткое резюме с помощью API OpenAI.

## Установка

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Укажите учётные данные в переменных окружения:
   - `TELEGRAM_TOKEN` – токен вашего бота Telegram.
   - `OPENAI_API_KEY` – API‑ключ OpenAI.
   - `BOT_PASSWORD` – пароль для входа пользователей в бот.

## Использование

Запустите бота:

```bash
python bot.py
```

При первом запуске выполните команду `/login <пароль>`.
Затем отправьте боту файл договора (PDF, DOCX, изображение или текст). Бот вернёт краткое резюме и найденные риски.

Команда `/history` покажет последние анализы, а `/export <id>` пришлёт PDF‑отчёт.


## Terraform Modules

В каталоге `terraform` находятся модули для развертывания инфраструктуры:

- `modules/s3-storage` — S3‑совместимое хранилище с включённым шифрованием и правилом удаления файлов через 30 дней.
- `modules/rds-postgres` — база данных Postgres в Amazon RDS с шифрованием.
- `modules/message-queue` — кластер Kafka (Amazon MSK) с шифрованием данных.
- `modules/ecs` — кластер ECS для запуска контейнеров.

Пример использования модулей находится в `terraform/main.tf`. Перед запуском инициализируйте и примените Terraform:

```bash
cd terraform
terraform init
terraform apply
```
