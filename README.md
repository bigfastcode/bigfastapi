# BigFastAPI

BigFastAPI is an extension of [FastAPI](https://github.com/tiangolo/fastapi) that adds a bunch of things that are commonly used in APIs.

---
**BigFastAPI Documentation**: <a href="https://bigfastapi.com/docs/" target="_blank">https://bigfastapi.com/docs/</a>,
      <a href="https://bigfa.st/" target="_blank">https://bigfa.st/</a>


**FastAPI Documentation**: <a href="https://fastapi.tiangolo.com" target="_blank">https://fastapi.tiangolo.com</a>

---

## Features

### Implemented
- Authentication (login, logout)
- Users
- Organizations
- Comments
- Blog
- FAQ
- Countries
- Pages
- Contact
- Files
- Notifications
- Image
- Wallet
- PDF Converter
- Credits
- Products


### In Progress
- Transactional Email sending + templates
- Plans
- Bank Accounts
- Subscriptions
- Settings


### Planned
- Currency Rates
- Marketing Emails
- Research bank format providers to build on
- Analytics
- ActivityLog


# How to use BigFastAPI
- Create a new python project
- Create a main.py file and set it up as described in the fastapi documentation
- install the latest version of bigfastapi by running `pip install bigfastapi`
- In your main.py, import FastAPI, CORSMiddleware and the create_database function (from bigfastapi.db.database.py). 
  You can look into the bigfastapi main.py to see everything you should import
- create a .env file and provide all the required environment variables.
  check check .env.sample file for a sample of what the env should contain
- Make sure you have a main that calls uvicorn in the bottom of your file
- You now have access to all the functions in bigfastapi. You can include any of them by importing (from bigfastapi.countries import app as countries) and then including a router app.include_router(countries, tags=["Countries"])
- Run the main.py file `python main.py` to start up your server. 
- learn more about how to use bigfastapi at <a href="https://bigfa.st/" target="_blank">https://bigfa.st/</a>


# How to contribute to BigFastAPI

1. Fork and clone the bigfastapi repository.
2. Create a virtual environment with `python3 -m venv env` or `python -m venv env`
3. Activate the virtual environment using `.\env\Scripts\Activate.ps1` (windows-powershell) 
    or `./env/Scripts/activate.bat` (windows-command prompt) or `source /path/to/venv/bin/activate` (linux/mac)
4. run `pip install -r requirements.txt`
5. Create a .env file by copying the .env.sample file
6. Run `python main.py`. Check the code to understand how to use the library
7. **commands for building bigfastapi into a library**: `python setup.py sdist bdist_wheel`
8. You can install your local version of the library into another project run: `pip install <path to local bigfastapi>\dist\<name of whl file>`
9. **update on pypi** using `twine upload dist/*` (first install twine using `pip install twine`)

# Documentation

When you run the sample code, visit http://127.0.0.1:7001/docs to view the documentation for all endpoints

## License

This project is licensed under the terms of the MIT license.