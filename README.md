# BigFastAPI

BigFastAPI is an extension of [FastAPI](https://github.com/tiangolo/fastapi) that adds a bunch of things that are commonly used in APIs.

---
**BigFastAPI Documentation**: <a href="" target="_blank">---</a>

**FastAPI Documentation**: <a href="https://fastapi.tiangolo.com" target="_blank">https://fastapi.tiangolo.com</a>

---

## Features

### Implemented
- Authentication (login, logout)
- Users
- Organisations

### Planned
- Transactional Email sending + templates
- Wallet/Credits
- Subscriptions & Plans
- Notifications
- Plans
- Blog
- Countries
- Contact


# How to use it 

1. Create a virtual environment with python3 -m venv 
2. Activate the virtual environment using .\env\bin\Activate.ps1 (windows) or source /path/to/venv/bin/activate (linux/mac)
3. Pull latest code.
4. run "pip install -r requirements.txt"
   - On Windows be sure to install microsoft visual c++ build tools https://go.microsoft.com/fwlink/?LinkId=691126
   - Install PostgresQL before
5. Create a .env file and add following DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

## License

This project is licensed under the terms of the MIT license.