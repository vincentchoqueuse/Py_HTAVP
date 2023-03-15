import json
import matplotlib.pyplot as plt
import seaborn as sns

filename = "full_data.json"
groups = ['LFI-NUPES', 'GDR-NUPES', 'ECOLO', 'SOC', 'RE', 'DEM', 'LIOT', 'HOR', 'LR', 'RN', 'NI']
must_include = "total"

with open(filename, "r") as file:
    content = json.load(file)

mean_list = []

for group in groups:

    nb_elements = 0
    total = 0
    for data in content:
        if data["groupe2"] == group:
            nb_elements += 1
            group_name = data["groupe1"]
            for actions in data["participation"]["data"]:
                if must_include in actions[0].lower():
                    print(actions)
                    total += actions[1]
    mean = total/nb_elements
    mean_list.append(mean)
    print("group: {} {}. {} {} {}".format(group, group_name, nb_elements, total, total/nb_elements))

sns.set_theme()
sns.set(rc={'figure.figsize': (20, 7)})
sns.barplot(x=groups, y=mean_list)
plt.xlabel("Groupe politique")
plt.ylabel("portefeuille d'actions chez '{}' moyen (euros/député)".format(must_include.capitalize()))
plt.grid()
plt.savefig("firm_{}.jpg".format(must_include))
plt.show()
