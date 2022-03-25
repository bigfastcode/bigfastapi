# BigFastAPI

BigFastAPI is an extension of [FastAPI](https://github.com/tiangolo/fastapi) that adds a bunch of things that are commonly used in APIs.

---
**BigFastAPI Documentation**: <a href="https://bigfastapi.com/docs/" target="_blank">https://bigfastapi.com/docs/</a>

**FastAPI Documentation**: <a href="https://fastapi.tiangolo.com" target="_blank">https://fastapi.tiangolo.com</a>

---

## Features

### Implemented
- Authentication (login, logout)
- Users
- Organisations
- Comments
- Blog
- FAQ
- Countries
- Pages
- Contact
- Files
- Notifications
- Image

### In Progress
- Transactional Email sending + templates
- Plans
- Bank Accounts
- QR Codes
- Wallet
- Credits
- Subscriptions
- Settings
- PDF Converter

### Planned
- Currency Rates
- Customers
- Marketing Emails
- Research bank format providers to build on
- Analytics
- ActivityLog
- Products

# How to use BigFastAPI
- Create a new python project
- Create a main.py file
- Create the requirements.txt and copy the content from here. Install all requirements
- Make a folder called db and copy the database.py file from here
- In your main.py, import FastAPI and the create_database function (in database.py). Import
  CORSMiddleware too. You can look in the main.py here to see everything you should import
- Copy the env file sample from here into your new project
- Clone the BigFastAPI repo. Cut out the BigFastAPI folder (the one with users.py only) and paste in your new project
- Make sure you have a main that calls uvicorn in the bottom of your file
- Run the main.py file. You now have a project where you can add all your endpoints. You also have
  access to all the functions in bigfastapi. You can include any of them by importing (from bigfastapi.countries import app as countries) and then including a router app.include_router(countries, tags=["Countries"])

# How to contribute to BigFastAPI

1. Create a virtual environment with `python3 -m venv env`
2. Activate the virtual environment using `.\env\bin\Activate.ps1` (windows) or `source /path/to/venv/bin/activate` (linux/mac)
3. Pull the latest commits from origin.
4. run `pip install -r requirements.txt`
5. Create a .env file by copying the .env.sample file
6. Run `python main.py`. Check the code to understand how to use the library
7. Build the library using python setup.py sdist bdist_wheel
8. Install the library using pip install <path to local bigfastapi>\dist\<name of whl file>
9. twine upload dist/* (install pip install twine)

# Documentation

When you run the sample code, visit http://127.0.0.1:7001/docs to view the documentation for all endpoints

## License

This project is licensed under the terms of the MIT license.