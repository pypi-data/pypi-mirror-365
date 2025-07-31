# cli-qr-watermark

![demo](https://i.imgur.com/XXXX.gif)

## Установка
```bash
pip install cli-qr-watermark

Быстрый старт

qrmark "photos/*.jpg" --url https://t.me/my_channel

Результат появится в папке ready.
Free tier
До 50 файлов бесплатно.
Больше — поддержите автора ☕ Buy me a coffee и установите переменную окружения QRMARK_PRO=1.
Лицензия
MIT
Copy

────────────────────────
9. Лицензия и .gitignore
────────────────────────
9.1 LICENSE  
Скопируй MIT: https://choosealicense.com/licenses/mit/ → сохрани как `LICENSE`.

9.2 .gitignore
pycache/
*.pyc
venv/
build/
dist/
*.egg-info
Copy

────────────────────────
10. GitHub-репозиторий
────────────────────────
10.1 Создай репо на GitHub  
• Зайди в https://github.com/new  
• Repository name: `cli-qr-watermark`  
• Public, Add README (не ставь, у нас уже есть), Add .gitignore (не выбирай), License (не выбирай).  
• Нажми «Create repository».

10.2 Заливаем код
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ВАШ_НИК/cli-qr-watermark.git
git push -u origin main