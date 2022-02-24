import gc
# import time

import numpy as np
from flask import Flask, request
import pandas as pd
import logging
import sys
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(message)s ',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('werkzeug')
logger.addHandler(logging.FileHandler('test.log', 'a'))
logger.setLevel(logging.ERROR)


tag_mapping_list = {
"e2:24:f4:21:f6:f5":"tag1",
"f3:7a:4c:4d:f1:6a":"tag2",
"e2:3e:a9:07:1d:e0":"tag3",
"cc:50:89:7a:14:3d":"tag5",
"ff:7b:dc:aa:7a:11":"tag6",
"d7:88:8e:03:c2:b3":"tag7",
"dd:07:6f:02:93:cf":"tag8",
"cf:7c:6c:36:76:95":"tag9",
"e0:d4:09:da:e3:0a":"tag10",
"df:78:21:27:20:37":"tag11",
"ed:52:c1:89:82:df":"tag12",
"d9:22:fd:70:c2:af":"tag13",
"ca:b0:3a:86:77:ef":"tag14",
"ee:30:14:01:b6:db":"tag16",
"de:74:2e:82:5e:05":"tag18",
}
app = Flask(__name__)

dict_tag_id_previous_value = {}
dict_zone_counter = {}
stations = [
            'station21','station22','station23',
            'station24','station25','station26',
            'station41','station43','station45'
            ]
dict_tag_id_queue = {}
queue_length = 3
moving_average_count = 3

# if tag hasn't pinged to all stations 5 times 
prev_value_threshold = 5

rejection_threshold = -75

# number of nan values 
num_nan_values = 2

# counts the number of times the tag wasn't pinged
dict_tag_id_counter = {}

# dictionary to store tag values and moving average
dict_tag_id = {}

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


def moving_average(dataframe)->list:
    means = []
    for column in dataframe.columns:
        value = dataframe[column].values
        means.append(np.mean(value))
    return means

def return_mode(values:list)-> str:
    return max(set(values), key=values.count)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/delete_allocation', methods=["GET", "POST"])
def flush():
    # request type
    # curl -i http://localhost:4001/delete_allocation
    global dict_zone_counter, dict_tag_id_previous_value,dict_tag_id_queue,dict_tag_id_counter, dict_tag_id

    # clearing both the on the run dictionary objects
    dict_zone_counter = {}
    dict_tag_id_previous_value = {}
    dict_tag_id_queue = {}
    dict_tag_id_counter = {}
    dict_tag_id = {}
    gc.collect()
    return "Cleared Zone Allocation from memory, ready to start new Session"


@app.route('/zone_allocation', methods=["GET", "POST"])
def return_zone_allocation():
    # request type
    # curl -i http://localhost:4001/zone_allocation
    return dict_zone_counter


@app.route('/zone_allocation_by_id', methods=["GET", "POST"])
def return_zone_allocation_by_id():
    # request type
    # curl -i -H "Content-Type: application/json" -X POST -d'{"tag_id":"ee:72:32:32:21"}' http://localhost:4001/zone_allocation_by_id

    global dict_zone_counter
    data = request.json
    tag_id = str(data['tag_id'])

    return dict_zone_counter.get(tag_id, {})


@app.route('/get_all_running_tags', methods=["GET", "POST"])
def view_all_tags():
    # request type
    # curl -i http://localhost:4001/get_all_running_tags

    return f'<p>{list(dict_tag_id_queue.keys())}</p>'


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
    global dict_tag_id_queue,dict_tag_id_previous_value,dict_tag_id_counter, dict_tag_id

    # start = time.time()
    data = request.json
    tag_id = str(data['tag_id'])

    if tag_id is None:
        return '!!!! Tag id is missing'
    if tag_id not in dict_tag_id_previous_value:
        # if tag not present create a new key with the name of the tag else uses previous tags

        dict_tag_id_previous_value[tag_id]  = [-100,-100,-100,-100,-100,-100,-100,-100,-100]
        dict_tag_id[tag_id] = pd.DataFrame(columns = ['station21','station22','station23','station24',
                                                'station25','station26','station41','station43',
                                                'station45'])

        print('Tag created')


    dict_tag_id_counter[tag_id] = dict_tag_id_counter.get(tag_id,[0,0,0,0,0,0,0,0,0])
    # appends the incoming data at the last
    station_values = [
        int(data['station21']),int(data['station22']),int(data['station23']),
        int(data['station24']),int(data['station25']),int(data['station26']),
        int(data['station41']),int(data['station43']),int(data['station45'])
        ]
    
    
    raw_values = station_values
    # print(station_values,tag_id)
    #if any tag has empty values(-120) then it will consider last triggered values.
    for index,value in enumerate(station_values):
        if value == -120:
            station_values[index] = dict_tag_id_previous_value[tag_id][index]
        if value < rejection_threshold:
            dict_tag_id_counter[tag_id][index] += 1
        else:
            dict_tag_id_counter[tag_id][index] = 0
    
    # if num of nans greater then the specific sattion threshold it will be assigned to -100
    for index,value in enumerate(station_values):
        if dict_tag_id_counter[tag_id][index] > num_nan_values:
            station_values[index] = -100

    dict_tag_id[tag_id].loc[len(dict_tag_id[tag_id].index)] = station_values
    avg_mean_for_tag = moving_average(dict_tag_id[tag_id])

    # change the previous values with current values for next batch of inputs
    dict_tag_id_previous_value[tag_id] = station_values

    res = all(ele >=prev_value_threshold  for ele in dict_tag_id_counter[tag_id])
    if res == True:
        lowest_station = 'OUT'
    else:
        #returning the station name with the max rssi value
        lowest_station = stations[np.argmax(avg_mean_for_tag)]

    # retriving the list bythe name tag is if not create a new list
    dict_tag_id_queue[tag_id] = dict_tag_id_queue.get(tag_id,[])
    

    # 
    if np.array_equal(np.array(raw_values),avg_mean_for_tag):
        lowest_station = 'OUT'

    # appending the result to return the mode of the queue
    dict_tag_id_queue[tag_id].append(lowest_station)
    if len(dict_tag_id_queue[tag_id]) > queue_length:
        dict_tag_id_queue[tag_id] = dict_tag_id_queue[tag_id][-queue_length:]
    
    
    # print(dict_tag_id_queue[tag_id])
    # print(avg_mean_for_tag)

    prediction = return_mode(dict_tag_id_queue[tag_id])
    add_output_to_counter(tag_id, prediction)
    # checks if we have required amount of data point for the Moving average else return how many still needed.
    if  dict_tag_id[tag_id].shape[0] >= moving_average_count:

         # removing the top element for moving average and resetting the index
        dict_tag_id[tag_id] = dict_tag_id[tag_id].iloc[-(moving_average_count-1):, :]

        # resetting the index
        dict_tag_id[tag_id].reset_index(drop=True, inplace=True)
    logger.error(str(prediction)+" "+str(tag_mapping_list.get(tag_id,tag_id))+" "+" ".join(str(x) for x in avg_mean_for_tag))
    return prediction


# request type
# curl -i -H "Content-Type: application/json" -X POST -d'{"station21":"-51","station22":"-63","station23":"-64","station24":"-67","station25":"-68","station26":"-81","station41":"-81","station43":"-89","station45":"-91","tag_id":"ee:72:32:32:21"}' http://localhost:4001/return_zone

if __name__ == "__main__":
    # load_models(models_path={'super_zone1': SUPER_ZONE1_MODEL_PATH, "super_zone2": SUPER_ZONE2_MODEL_PATH})
    app.run(port=4001, debug=True)