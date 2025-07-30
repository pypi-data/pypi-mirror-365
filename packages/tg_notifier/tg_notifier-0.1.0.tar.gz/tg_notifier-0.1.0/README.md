# tg_notifier

```bash
pip install git+https://imbecility:github_pat_***@github.com/imbecility/tg_notifier

pip install git+https://github.com/imbecility/tg_notifier

uv pip install git+https://github.com/imbecility/tg_notifier

uv add git+https://github.com/imbecility/tg_notifier
```


```python
from pathlib import Path
from tg_notifier import send_message_to_telegram

bot_token = '7036427666:R38OyUtA1ze20vXu8JcxmD_bfSQiIBhi0R1'
chat_id = '656000000'

msg = 'Господи, Иисусе Христе, Сыне Божий, помилуй мя, грешнаго'

tests = [
    (f'> _{msg}_', 'MarkdownV2'),
    (f'`{msg}`', 'Markdown'),
    (f'<blockquote><i>{msg}</i></blockquote>', 'HTML'),
    (msg, None)
]

# отправка только текста
for message, mode in tests:
    result = send_message_to_telegram(bot_token, chat_id, message, parse_mode=mode)
    # print(result)
    print(f"Text ({mode}): {'OK' if result.get('ok') else 'FAIL'}")


# ----------------------------------------------------------------

# отправка с изображением

def whatever_image():
    """
    просто выдаст путь до первой попавшейся картинки
    чтобы для теста не указывать вручную.
    """
    from os import scandir
    from collections import deque
    queue = deque([Path.home().resolve()])
    while queue:
        folder = queue.popleft()
        try:
            with scandir(folder) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        return Path(entry.path)
                    elif entry.is_dir():
                        queue.append(Path(entry.path))
        except:
            pass
    return None


image_path = whatever_image()

for message, mode in tests:
    result = send_message_to_telegram(bot_token, chat_id, message, parse_mode=mode, photo_path=image_path)
    # print(result)
    print(f"Image ({mode}): {'OK' if result.get('ok') else 'FAIL'}")
```