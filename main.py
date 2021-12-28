import gc
import time

import numpy as np
import pandas as pd
from flask import Flask, request
from pycaret.classification import load_model, predict_model

from config import MOVING_AVG_CONSTANT, SUPER_ZONE1_MODEL_PATH, SUPER_ZONE2_MODEL_PATH, ZONE_IN_EACH_SUPER_ZONE, \
    ZONE1_STATIONS, ZONE2_STATIONS

app = Flask(__name__)
super_zone1_model = None
super_zone2_model = None

dict_tag_id = {}
dict_zone_counter = {}

moving_avg_count = MOVING_AVG_CONSTANT


def add_output_to_counter(tag_id: str, zone_name: str) -> None:
    """
    adds the zone to the counter how many times a zone is detected by the output
    :param tag_id:  name of the tag
    :param zone_name:  name of the zone
    :return:
    """
    global dict_zone_counter

    # if that tag is not present in the tag list creates the new dictionary key of that tag to process the allocation

    dict_zone_counter[tag_id] = dict_zone_counter.get(tag_id, {})
    dict_zone_counter[tag_id][zone_name] = dict_zone_counter[tag_id].get(zone_name, 0) + 1


def load_models(models_path: dict) -> None:
    """
    Loads both the model to inference later

    :param models_path: takes model path as an argument to load the model
    :return: None
    """
    global super_zone1_model, super_zone2_model

    super_zone1_model = load_model(models_path['super_zone1'])
    super_zone2_model = load_model(models_path['super_zone2'])


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
    predict the output based on the model and the inputs

    :param dataframe: accepts a dataframe
    :return: label came from the model
    """

    values = dataframe.values
    index = np.argmin(values[0])

    # checks if it lies in the first zone or second
    # since first zone has 18 stations and index starts with zero we are subtracting 1 from zone_in_each_super_zone
    # if present in first zone the dataframe is trimmed into the specific stations that are necessary for the model prediction
    # i.e for zone 1 we will have from station 1-station 10 and for zone 2 we will have dataframe station 11-station20
    if index <= ZONE_IN_EACH_SUPER_ZONE - 1:
        model = super_zone1_model
        dataframe = dataframe[ZONE1_STATIONS]
    else:
        model = super_zone2_model
        dataframe = dataframe[ZONE2_STATIONS]

    preds = predict_model(model, data=dataframe)
    return preds['Label'].values[0]


@app.route('/delete_allocation', methods=["GET", "POST"])
def flush():
    global dict_zone_counter, dict_tag_id

    # clearing both the on the run dictionary objects
    dict_zone_counter = {}
    dict_tag_id = {}
    gc.collect()
    return "Cleared Zone Allocation from memory, ready to start new Session"


@app.route('/zone_allocation', methods=["GET", "POST"])
def return_zone_allocation():
    # request type
    # curl -i http://localhost:5000/zone_allocation
    return dict_zone_counter


@app.route('/zone_allocation_by_id', methods=["GET", "POST"])
def return_zone_allocation_by_id():
    # request type
    # curl -i -H "Content-Type: application/json" -X POST -d'{"tag_id":"ee:72:32:32:21"}' http://localhost:5000/zone_allocation_by_id

    global dict_zone_counter
    data = request.json
    tag_id = str(data['tag_id'])

    return dict_zone_counter.get(tag_id, {})


@app.route('/get_all_running_tags', methods=["GET", "POST"])
def view_all_tags():
    # request type
    # curl -i http://localhost:5000/get_all_running_tags

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
    global dict_tag_id, dict_zone_counter

    start = time.time()
    data = request.json
    tag_id = str(data['tag_id'])

    if tag_id is None:
        return '!!!! Tag id is missing'
    if tag_id not in dict_tag_id:
        # if tag not present create a new key with the name of the tag else uses previous tags

        dict_tag_id[tag_id] = pd.DataFrame(columns=
                                           ['stat1', 'stat2', 'stat3', 'stat4', 'stat5', 'stat6', 'stat7', 'stat8',
                                            'stat9', 'stat10', 'stat1.1', 'stat2.1', 'stat3.1', 'stat4.1',
                                            'stat6.1', 'stat7.1', 'stat8.1', 'stat9.1',
                                            'stat11', 'stat12', 'stat13', 'stat14', 'stat15', 'stat16', 'stat17',
                                            'stat18',
                                            'stat19', 'stat20', 'stat11.1', 'stat12.1', 'stat13.1', 'stat14.1',
                                            'stat16.1', 'stat17.1', 'stat18.1', 'stat19.1',
                                            ])
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
                                                               int(data['station6.1']),
                                                               int(data['station7.1']),
                                                               int(data['station8.1']),
                                                               int(data['station9.1']),

                                                               int(data['station11']),
                                                               int(data['station12']),
                                                               int(data['station13']),
                                                               int(data['station14']),
                                                               int(data['station15']),
                                                               int(data['station16']),
                                                               int(data['station17']),
                                                               int(data['station18']),
                                                               int(data['station19']),
                                                               int(data['station20']),
                                                               int(data['station11.1']),
                                                               int(data['station12.1']),
                                                               int(data['station13.1']),
                                                               int(data['station14.1']),
                                                               int(data['station16.1']),
                                                               int(data['station17.1']),
                                                               int(data['station18.1']),
                                                               int(data['station19.1']),
                                                               ]

    # checks if we have required amount of data point for the Moving average else return how many still needed.

    if dict_tag_id[tag_id].shape[0] == moving_avg_count:
        # preprocess the input into the moving average
        preprocessed_df = get_moving_average(dict_tag_id[tag_id])

        # removing the top element for moving average and resetting the index
        dict_tag_id[tag_id] = dict_tag_id[tag_id].iloc[1:, :]
        dict_tag_id[tag_id].reset_index(drop=True, inplace=True)

        pred = get_prediction(preprocessed_df)

        # add output to the zone allocation
        add_output_to_counter(tag_id, pred)

        end = time.time()
        print(end - start)
        return pred
    else:
        return f"Needed {moving_avg_count} data point, currently have {dict_tag_id[tag_id].shape[0]} data-points in tag {tag_id}."


# request type
# curl -i -H "Content-Type: application/json" -X POST -d'{"station1":"-58", "station1.1":"-58","station2":"-58", "station2.1":"-58","station3":"-58", "station3.1":"-58",  "station4":"-58", "station4.1":"-58","station5":"-58","station6":"-58", "station6.1":"-58","station7":"-58", "station7.1":"-58","station8":"-58", "station8.1":"-58","station9":"-58", "station9.1":"-58","station10":"-58","station11":"-58", "station11.1":"-58","station12":"-58", "station12.1":"-58","station13":"-58", "station13.1":"-58",  "station14":"-58", "station14.1":"-58","station15":"-58","station16":"-58", "station16.1":"-58","station17":"-58", "station17.1":"-58","station18":"-58", "station18.1":"-58","station19":"-58", "station19.1":"-58","station20":"-58","tag_id":"ee:72:32:32:21"}' http://localhost:5000/return_zone

if __name__ == "__main__":
    load_models(models_path={'super_zone1': SUPER_ZONE1_MODEL_PATH, "super_zone2": SUPER_ZONE2_MODEL_PATH})
    app.run(port=5000, debug=True)
