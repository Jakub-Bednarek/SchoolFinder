import pathlib
import os
from web3 import Web3
import json
import requests
import dotenv
from datetime import datetime

PATH_PREFIX = "script_outputs/"

dotenv.load_dotenv()

def fetch_gas_prices():
    etherscan_key = os.getenv("ETHERSCAN_KEY")
    req = requests.get(f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscan_key}')
    return json.loads(req.content)

def get_current_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# This is function that returns value passed to our program, write your code inside and don't forget about return
def perform_script():
    gas_prices = fetch_gas_prices()
    safe_price = gas_prices['result']['SafeGasPrice']
    propose_gas_price = gas_prices['result']['ProposeGasPrice']
    fast_gas_price = gas_prices['result']['FastGasPrice']
    time = get_current_time()
    msg = f"#ETH #GasPrice #NFTCommunity\n\nTime: {time}\n\n🐇 - {fast_gas_price}\n🧍 - {propose_gas_price}\n🐢 - {safe_price}\n\nStay safe!"
    return msg


# Don't touch this part of code as it may break functionality
def create_dir_if_not_existing():
    p = pathlib.Path(PATH_PREFIX)
    if not p.exists():
        os.mkdir(f"./{PATH_PREFIX}")


def save_to_file():
    values = perform_script()
    filename = os.path.basename(__file__)[:-3]
    create_dir_if_not_existing()

    with open(f"{PATH_PREFIX}{filename}.txt", "w") as file:
        file.write(values)
        file.flush()


try:
    save_to_file()
except Exception as e:
    print(e)
