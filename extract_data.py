import pandas as pd
import requests
import xmltodict
from tqdm import tqdm
import json


def get_list(url_deputes, url_hatvp):
    df_deputes = pd.read_csv(url_deputes)
    df_hatvp = pd.read_csv(url_hatvp, on_bad_lines='skip', delimiter=";")

    df_deputes['nom'] = df_deputes['nom'].str.upper()
    df_deputes = df_deputes[['prenom', 'nom', 'groupe', 'groupeAbrev', 'experienceDepute']]
    df_hatvp_filtered = df_hatvp.loc[(df_hatvp['type_mandat'] == 'depute') & (df_hatvp['type_document'] == 'diam')]
    df_hatvp_filtered = df_hatvp_filtered[['prenom', 'nom', 'open_data', 'date_publication']].sort_values(by=['nom', 'prenom', 'date_publication']).drop_duplicates(['prenom', 'nom'], keep="last")
    df_tot = pd.merge(df_deputes, df_hatvp_filtered, how="inner", on=["nom", "prenom"])
    return df_tot.values.tolist()


def load_data(row, add_name=True):

    prenom = row[0]
    nom = row[1]
    groupe1 = row[2]
    groupe2 = row[3]
    xml_file = row[5]
    participation_financiere = []
    total = 0

    filename = "https://www.hatvp.fr/livraison/dossiers/{}".format(xml_file)

    if xml_file != xml_file:
        status = False
    else:
        response = requests.get(filename)
        xml_content = response.content
        content = xmltodict.parse(xml_content)
        status = True
        try:
            if content["declaration"]["participationFinanciereDto"]["neant"] == "false":
                data = content["declaration"]["participationFinanciereDto"]["items"]["items"]
                if not isinstance(data, list):
                    data = [data]

                for content in data:
                    item = [content["nomSociete"], float(content["evaluation"])]
                    participation_financiere.append(item)
                    total += float(content["evaluation"])
        except:
            print("cannot read data for {} {}".format(nom, prenom))

    if add_name:
        output = {"nom": nom, "prenom": prenom, "groupe1": groupe1, "groupe2": groupe2, "participation": {"data": participation_financiere, "total": total}}
    else:
        output = {"groupe1": groupe1, "groupe2": groupe2, "participation": {"data": participation_financiere, "total": total, "status": status}}

    return output


if __name__ == "__main__":
    url_deputes = "https://www.data.gouv.fr/fr/datasets/r/092bd7bb-1543-405b-b53c-932ebb49bb8e"
    url_hatvp = "https://www.hatvp.fr/livraison/opendata/liste.csv"
    output_filename = "full_data.json"
    data_list = get_list(url_deputes, url_hatvp)

    N_elem = len(data_list)
    full_data = []
    for index in tqdm(range(N_elem)):
        content = data_list[index]
        full_data.append(load_data(data_list[index], add_name=False))

    with open(output_filename, "w") as file:
        json.dump(full_data, file, indent=4, ensure_ascii=False)
