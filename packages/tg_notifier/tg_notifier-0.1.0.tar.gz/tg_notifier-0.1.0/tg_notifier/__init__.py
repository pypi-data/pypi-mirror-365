from json import loads, dumps
from mimetypes import guess_type
from os import urandom
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def send_message_to_telegram(
        bot_token: str,
        chat_id: int | str,
        text: str | None = None,
        photo_path: Path | str | None = None,
        parse_mode: Literal['Markdown', 'HTML', 'MarkdownV2', None] = None,
        tg_api_proxy: bool = False,
) -> dict:
    tg_api_url = 'https://api.telegram.org' if not tg_api_proxy else 'https://tgbtapi.vercel.app'
    if (not photo_path and not text) or (photo_path and not isinstance(photo_path, (str, Path))):
        raise ValueError(f'нужно указать путь к изображению и/или текст!')
    if text and photo_path:
        if len(text) > 1024:
            raise ValueError(f'описание к изображению не должно превышать 1024 символов!')
    if text and not photo_path:
        if len(text) > 4096:
            raise ValueError(f'текст сообщения не должен превышать 4096 символов!')
    if not photo_path and text:
        request = Request(
            url=f'{tg_api_url}/bot{bot_token}/sendMessage',
            data=dumps({'chat_id': str(chat_id), 'text': text, 'parse_mode': str(parse_mode)}).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
    else:
        photo_path = Path(photo_path)
        if not photo_path.is_file():
            raise ValueError(f'изображение по пути {photo_path.resolve().as_posix()} не найдено!')
        if photo_path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError(f'изображение по пути {photo_path.resolve().as_posix()} > 10 МБ!')
        boundary = '----WebKitFormBoundary' + urandom(16).hex()
        body = [f'--{boundary}', 'Content-Disposition: form-data; name="chat_id"', '', str(chat_id)]

        if text:
            for part in [
                f'--{boundary}', 'Content-Disposition: form-data; name="caption"', '', text,
                f'--{boundary}',
                'Content-Disposition: form-data; name="parse_mode"', '', str(parse_mode)
            ]:
                body.append(part)

        for part in [
            f'--{boundary}',
            f'Content-Disposition: form-data; name="photo"; filename="{photo_path.name}"',
            f'Content-Type: {guess_type(photo_path)[0] or "application/octet-stream"}', ''
        ]:
            body.append(part)

        request = Request(
            url=f'{tg_api_url}/bot{bot_token}/sendPhoto',
            data=b'\r\n'.join(
                [part.encode('utf-8') for part in body] +
                [photo_path.read_bytes()] +
                [f'--{boundary}--'.encode('utf-8')]
            ),
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
            method='POST'
        )
    try:
        with urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            return loads(response_data)
    except HTTPError as e:
        error_response = e.read().decode('utf-8')
        return loads(error_response)
    except URLError as e:
        return {'ok': False, 'error': str(e.reason)}
