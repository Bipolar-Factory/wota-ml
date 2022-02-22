import json
from csv import writer

with open("rtls_data_log1.json") as file:
    dictdump = json.load(file)
# print([d['name'] for d in data])

with open('14feb9station.csv', 'a') as f_object:
    writer_object = writer(f_object)
    writer_object.writerow(['collection_name',"id_name", "station_name", "time","value"])
    
    for dictionary in dictdump:
        name = dictionary['name']
        print(name)
        # continue
        for station in dictionary['stations']:
            station_name = station['stationName']
            datas = station['data']
            for data in datas:
                time = data["_id"].split('T')[-1][:-1]
                tags = data['tags']
                if len(tags) == 0:
                    continue
                else:
                    for tag in tags:
                        device_id = tag["_id"]
                        if device_id=='':
                            continue
                        value = tag['rssi']
                        writer_object.writerow([name,device_id, station_name, time,value])
  
    #Close the file object
    f_object.close()
