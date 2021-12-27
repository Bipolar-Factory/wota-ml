#configuration constants used in main.py

MOVING_AVG_CONSTANT = 7
SUPER_ZONE1_MODEL_PATH = './models/26dec_avg_lr'
SUPER_ZONE2_MODEL_PATH = './models/27dec_zone2_avg_lr'
ZONE1_STATIONS = ['stat1', 'stat2', 'stat3', 'stat4', 'stat5', 'stat6', 'stat7', 'stat8',
                  'stat9', 'stat10', 'stat1.1', 'stat2.1', 'stat3.1', 'stat4.1',
                  'stat6.1', 'stat7.1', 'stat8.1', 'stat9.1']
ZONE_IN_EACH_SUPER_ZONE = len(ZONE1_STATIONS)
# print(ZONE_IN_EACH_SUPER_ZONE)
ZONE2_STATIONS = ['stat11', 'stat12', 'stat13', 'stat14', 'stat15', 'stat16', 'stat17', 'stat18',
                  'stat19', 'stat20', 'stat11.1', 'stat12.1', 'stat13.1', 'stat14.1',
                  'stat16.1', 'stat17.1', 'stat18.1', 'stat19.1', ]
