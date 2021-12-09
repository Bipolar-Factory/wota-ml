from flask import Flask, request
import pandas as pd
from pycaret.classification import load_model, predict_model

app = Flask(__name__)
model = load_model('./models/knn_model_8dec2021')

mapping_dict = {'zone1': 0,
                'zone2': 1,
                'zone3': 2,
                'zone4': 3,
                'zone5': 4,
                'zone6': 5,
                'zone7': 6,
                'zone8': 7,
                'zone9': 8,
                'zone10': 9,
                'zone11': 10,
                'zone12': 11,
                'zone13': 12,
                'zone14': 13,
                'zone15': 14,
                'zone16': 15,
                'zone17': 16,
                'zone18': 17,
                'zone19': 18,
                'zone20': 19}
reverse_map = {y: x for x, y in mapping_dict.items()}


@app.route('/return_zone', methods=["GET", "POST"])
def return_zone():
    data = request.json
    df = pd.DataFrame({
        'stat1': int(data['station1']),
        'stat2': int(data['station2']),
        'stat3': int(data['station3']),
        'stat4': int(data['station4']),
        'stat5': int(data['station5']),
        'stat6': int(data['station6']),
        'stat7': int(data['station7']),
        'stat8': int(data['station8']),
        'stat9': int(data['station9']),
        'stat10': int(data['station10']),
        'stat1.1': int(data['station1.1']),
        'stat2.1': int(data['station2.1']),
        'stat3.1': int(data['station3.1']),
        'stat4.1': int(data['station4.1']),
        'stat5.1': int(data['station5.1']),
        'stat6.1': int(data['station6.1']),
        'stat7.1': int(data['station7.1']),
        'stat8.1': int(data['station8.1']),
        'stat9.1': int(data['station9.1']),
        'stat10.1': int(data['station10.1']),
    }, index=[0])
    df.replace({0: -120}, inplace=True)
    preds = predict_model(model, data=df)
    return reverse_map[preds['Label'].values[0]]


# request type
# curl -i -H "Content-Type: application/json" -X POST -d'{"station1":"-58", "station1.1":"-58","station2":"-58", "station2.1":"-58","station3":"-58", "station3.1":"-58",  "station4":"-58", "station4.1":"-58","station5":"-58", "station5.1":"-58","station6":"-58", "station6.1":"-58","station7":"-58", "station7.1":"-58","station8":"-58", "station8.1":"-58","station9":"-58", "station9.1":"-58","station10":"-58", "station10.1":"-58"}' http://localhost:5000/return_zone

if __name__ == "__main__":
    app.run(port=5000, debug=True)
