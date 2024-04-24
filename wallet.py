import pandas as pd

def create_wallet(session):
    data = session.get_spot_asset_info()
    assets = data['result']['spot']['assets']

    wallet = {
        "coin" : [],
        "frozen": [],
        "free": [],
    }

    def form_assets_wallet(assets, wallet):
        for i in assets:
            wallet["coin"].append(i['coin'])
            wallet["frozen"].append(i["frozen"])
            wallet["free"].append(i["free"])

    form_assets_wallet(assets, wallet)
    
    wallet = pd.DataFrame.from_dict(wallet)
    return wallet 