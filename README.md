
## How to use the bot
1. Склонувти або скачати репозиторій
2. встановити віртуальне середовище в папці де всі модулі бота (`api bot` ~~admin_panel~~)```python3.11 -m venv venv```
3. активувати віртуальне середовище ```source venv/bin/activate``` (на unix системах) або ```venv\Scripts\activate``` (на windows)
4. встановити залежності ```pip install -r requirements.txt```
5. перейменувати файл ```.env.example``` в ```.env```
6. заповнити файл ```.env``` необхідними даними
7. запустити бота ```python3.11 main.py``` для теста



## DEPLOY
1. Для деплоя потрібно вміст папки systemd скопіювати в /etc/systemd/system/.
2. В файлах ```.service``` треба прописати шлях до вашого бота|адмінки|апі саме до папки де зберігається `venv`.
3. запуск через systemctl ```sudo systemctl start bot``` ~~sudo systemctl start admin_panel~~ ```sudo systemctl start api```
4. автозапуск ```sudo systemctl enable bot``` ~~sudo systemctl enable admin_panel~~ ```sudo systemctl enable api```
5. перезапуск ```sudo systemctl restart bot``` ~~sudo systemctl restart admin_panel~~ ```sudo systemctl restart api```
6. статус ```sudo systemctl status bot``` ~~sudo systemctl status admin_panel~~ ```sudo systemctl status api```
7. логи ```sudo journalctl -u bot``` ~~sudo journalctl -u admin_panel~~ ```sudo journalctl -u api```

# !ОБОВЯЗКОВО!
1. На продовій стадії в .env `bot_mode` змінити значення на `prod`