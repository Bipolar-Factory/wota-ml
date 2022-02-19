import gc
# import time

import numpy as np
from flask import Flask, request



app = Flask(__name__)

dict_tag_id_previous_value = {}
dict_zone_counter = {}
stations = [
            'station21','station22','station23',
            'station24','station25','station26',
            'station41','station43','station45'
            ]
dict_tag_id_queue = {}
queue_length = 5

# if tag hasn't pinged 10 times 
prev_value_threshold = 10

rejection_threshold = -85

# counts the number of times the tag wasn't pinged
dict_tag_id_counter = {}

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



def return_mode(values:list)-> str:
    return max(set(values), key=values.count)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/delete_allocation', methods=["GET", "POST"])
def flush():
    # request type
    # curl -i http://localhost:4001/delete_allocation
    global dict_zone_counter, dict_tag_id_previous_value,dict_tag_id_queue,dict_tag_id_counter

    # clearing both the on the run dictionary objects
    dict_zone_counter = {}
    dict_tag_id_previous_value = {}
    dict_tag_id_queue = {}
    dict_tag_id_counter = {}
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
    global dict_tag_id_queue,dict_tag_id_previous_value,dict_tag_id_counter

    # start = time.time()
    data = request.json
    tag_id = str(data['tag_id'])

    if tag_id is None:
        return '!!!! Tag id is missing'
    if tag_id not in dict_tag_id_previous_value:
        # if tag not present create a new key with the name of the tag else uses previous tags

        dict_tag_id_previous_value[tag_id]  = [-100,-100,-100,-100,-100,-100,-100,-100,-100]

        print('Tag created')

    # appends the incoming data at the last
    station_values = [
        int(data['station21']),int(data['station22']),int(data['station22']),
        int(data['station24']),int(data['station25']),int(data['station26']),
        int(data['station41']),int(data['station43']),int(data['station45'])
        ]
    
    dict_tag_id_counter[tag_id] = dict_tag_id_counter.get(tag_id,[0,0,0,0,0,0,0,0,0])
    #if any tag has empty values(-120) then it will consider last triggered values.
    for index,value in enumerate(station_values):
        if value == -120:
            station_values[index] = dict_tag_id_previous_value[tag_id][index]
        if value < rejection_threshold:
            dict_tag_id_counter[tag_id][index] += 1
        else:
            dict_tag_id_counter[tag_id][index] = 0



    # change the previous values with current values for next batch of inputs
    dict_tag_id_previous_value[tag_id] = station_values

    res = all(ele >=prev_value_threshold  for ele in dict_tag_id_counter[tag_id])
    if res == True:
        lowest_station = 'OUT'
    else:
        #returning the station name with the max rssi value
        lowest_station = stations[np.argmax(station_values)]

    # retriving the list bythe name tag is if not create a new list
    dict_tag_id_queue[tag_id] = dict_tag_id_queue.get(tag_id,[])
    
    # appending the result to return the mode of the queue
    dict_tag_id_queue[tag_id].append(lowest_station)
    if len(dict_tag_id_queue[tag_id]) > queue_length:
        dict_tag_id_queue[tag_id] = dict_tag_id_queue[tag_id][-queue_length:]
    
    
    print(dict_tag_id_queue[tag_id])

    prediction = return_mode(dict_tag_id_queue[tag_id])
    add_output_to_counter(tag_id, prediction)
    # checks if we have required amount of data point for the Moving average else return how many still needed.

    return prediction


# request type
# curl -i -H "Content-Type: application/json" -X POST -d'{"station21":"-51","station22":"-63","station23":"-64","station24":"-67","station25":"-68","station26":"-81","station41":"-81","station43":"-89","station45":"-91","tag_id":"ee:72:32:32:21"}' http://localhost:4001/return_zone

if __name__ == "__main__":
    # load_models(models_path={'super_zone1': SUPER_ZONE1_MODEL_PATH, "super_zone2": SUPER_ZONE2_MODEL_PATH})
    app.run(port=4001, debug=True)