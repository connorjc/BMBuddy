# BMBuddy
A web-based tool to help the Business Managers (BM) of the [Southern
Scholarship Foundation][] (SSF) better effectively buy groceries on a budget for
all of the residents. BMBuddy will help track shopping the running total of 
groceries, a live shopping list, as well as a wish list for the other residents
to suggest food items.

[Southern Scholarship Foundation]: https://www.southernscholarship.org/
## Getting Started

### Prerequisites

Python3

virtualenv

MySQL

### Installing

Create the virtualenv
```sh
python3 -m venv <DIRECTORY>
```

Enter and activate the virtualenv
```sh
cd <DIRECTORY>
source bin/activate
```

Clone the repository and enter the repo
```sh
git clone https://github.com/connorjc/bmbuddy.git
cd BMBuddy
```

Install modules
```sh
pip install -r requirements.txt
```

### Running
```sh
python3 bmbuddy.py
```
or
```sh
./bmbuddy.py
```

## Authors

* **Connor Christian** - [connorjc](https://github.com/connorjc)
* **Ronald Franco** - [Francoded](https://github.com/Francoded)
* **Biing-Jiun Charles** - [BeejCoding](https://github.com/BeejCoding)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
