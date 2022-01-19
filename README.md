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
5. Create a .env file by copying the .env.sample file
6. Run python main.py. This will show you how the libary can be used
7. Create your own app in another folder and import the bigfastapi folder

# Documentation

When you run the sample code, visit http://127.0.0.1:7001/docs to view the documentation for all endpoints

## License

This project is licensed under the terms of the MIT license.