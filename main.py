from flask import Flask, request
import pandas as pd
import numpy as np
from pycaret.classification import load_model, predict_model
import time

app = Flask(__name__)
model = load_model('./models/14dec_MA_lr')
df = pd.DataFrame(columns=['stat1', 'stat2', 'stat3', 'stat4', 'stat5', 'stat6', 'stat7', 'stat8', 'stat9', 'stat10',
                           'stat1.1', 'stat2.1', 'stat3.1', 'stat4.1', 'stat5.1', 'stat6.1', 'stat7.1', 'stat8.1',
                           'stat9.1', 'stat10.1'])

dict_tag_id = {}

moving_avg_count = 10

mapping_dict = {'zone1': 0, 'zone2': 1, 'zone3': 2, 'zone4': 3, 'zone5': 4, 'zone6': 5, 'zone7': 6, 'zone8': 7,
                'zone9': 8, 'zone10': 9, 'zone11': 10, 'zone12': 11, 'zone13': 12, 'zone14': 13, 'zone15': 14,
                'zone16': 15, 'zone17': 16, 'zone18': 17, 'zone19': 18, 'zone20': 19}
reverse_mapping_dict = {value: key for key, value in mapping_dict.items()}


def get_moving_average(dataframe):
    """
    :param dataframe: accepts a dataframe with moving_avg_count number of records
    :return: a dataframe with one record with the mean of all moving_avg_count records
    """

    dicts = {}
    for column in dataframe.columns:
        value = dataframe[column].values
        dicts[column] = int(np.mean(value))
    df = pd.DataFrame([dicts])
    return df


def get_prediction(dataframe):
    """

    :param dataframe: accepts a dataframe
    :return: label came from the model
    """

    preds = predict_model(model, data=dataframe)
    return preds['Label'].values[0]


@app.route('/get_all_running_tags', methods=["GET", "POST"])
def view_all_tags():
    return f'<p>{list(dict_tag_id.keys())}</p>'


@app.route('/return_zone', methods=["GET", "POST"])
def return_zone():
    """
    Creates a container for every new tag and stores the value in the backend in dict_tag_id variable.

    Checks if it has sufficient data for the moving average if it has
            call the get_moving_average
            then calls the get_prediction and returns the prediction label
        else
            returns how many more data points to be filled in that tag_id

    :return: either the zone name or the output for how many more records to fill on that tag
    """
    start = time.time()
    data = request.json
    tag_id = data['tag_id']
    if tag_id is None:
        return '!!!! Tag id is missing'
    if tag_id not in dict_tag_id:
        # if tag not present create a new key with the name of the tag else uses previous tags

        dict_tag_id[tag_id] = pd.DataFrame(columns=
                                           ['stat1', 'stat2', 'stat3', 'stat4', 'stat5', 'stat6', 'stat7', 'stat8',
                                            'stat9', 'stat10', 'stat1.1', 'stat2.1', 'stat3.1', 'stat4.1', 'stat5.1',
                                            'stat6.1', 'stat7.1', 'stat8.1',
                                            'stat9.1', 'stat10.1'])
        print('Tag created')

    # appends the incoming data at the last

    dict_tag_id[tag_id].loc[len(dict_tag_id[tag_id].index)] = [int(data['station1']),
                                                               int(data['station2']),
                                                               int(data['station3']),
                                                               int(data['station4']),
                                                               int(data['station5']),
                                                               int(data['station6']),
                                                               int(data['station7']),
                                                               int(data['station8']),
                                                               int(data['station9']),
                                                               int(data['station10']),
                                                               int(data['station1.1']),
                                                               int(data['station2.1']),
                                                               int(data['station3.1']),
                                                               int(data['station4.1']),
                                                               int(data['station5.1']),
                                                               int(data['station6.1']),
                                                               int(data['station7.1']),
                                                               int(data['station8.1']),
                                                               int(data['station9.1']),
                                                               int(data['station10.1'])]

    # checks if we have required amount of data point for the Moving average else return how many still needed.

    if dict_tag_id[tag_id].shape[0] == moving_avg_count:
        preprocessed_df = get_moving_average(dict_tag_id[tag_id])
        dict_tag_id[tag_id] = dict_tag_id[tag_id].iloc[1:, :]
        dict_tag_id[tag_id].reset_index(drop=True, inplace=True)
        pred = get_prediction(preprocessed_df)
        return f'{reverse_mapping_dict[pred]}'
    else:
        return f"Needed {moving_avg_count} data point, currently have {dict_tag_id[tag_id].shape[0]} datapoints in tag {tag_id}."


# request type
# curl -i -H "Content-Type: application/json" -X POST -d'{"station1":"-58", "station1.1":"-58","station2":"-58", "station2.1":"-58","station3":"-58", "station3.1":"-58",  "station4":"-58", "station4.1":"-58","station5":"-58", "station5.1":"-58","station6":"-58", "station6.1":"-58","station7":"-58", "station7.1":"-58","station8":"-58", "station8.1":"-58","station9":"-58", "station9.1":"-58","station10":"-58", "station10.1":"-58", "tag_id":"ee:72:32:32:21"}' http://localhost:5000/return_zone

if __name__ == "__main__":
    app.run(port=5000, debug=True)
