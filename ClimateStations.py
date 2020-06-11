from datetime import date, timedelta
import datetime
import os
import numpy
from qgis.core import QgsProcessingException


class ClimateStations():

    def __init__(self, stations_filename):
        if os.path.isfile(stations_filename):
            self.station_filename = stations_filename
            self.station_id = []
            self.station_lati = []
            self.station_long = []
            self.station_elev = []

            # Reading station file
            with open(stations_filename, 'r') as station_file:
                for line in station_file.readlines()[1:]:
                    info = line.split(",")
                    try:
                        self.station_id.append(info[1][0:6])
                        self.station_lati.append(float(info[2][0:6]))
                        self.station_long.append(float(info[3][0:6]))
                        self.station_elev.append(int(info[4][0:4]))
                    except ValueError:
                        pass

            # Convert id's to dictionary
            self.station_id_dict = {}
            for i in self.station_id:
                self.station_id_dict[int(i)] = i
        else:
            raise QgsProcessingException('No such file: \"' + stations_filename + '\" ')

    def readPcpFiles(self, log_file):
        """Reading the Budyko .pcp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)
        # Reading .pcp files to numpy array
        pcp_array = None
        pcp_dates = []
        for i in station_id_sorted:
            station_pcp_filename = os.path.join(station_folder, self.station_id_dict[i] + '.txt')
            if os.path.isfile(station_pcp_filename):
                with open(station_pcp_filename, 'r') as pcp_file:
                    lines = pcp_file.readlines()
                    lines_number = len(lines)
                    if pcp_array is None:
                        pcp_array = numpy.zeros([lines_number - 1, len(station_id_sorted)],
                                                dtype=numpy.float)
                    for n in range(lines_number):
                        if (n == 0 and i == 1):
                            t = datetime.datetime.strptime(lines[0][0:8], '%Y%m%d')
                            if lines_number == 1:
                                tt_first = (t-timedelta(days=1)).timetuple()
                                julian_tfirst = ('%d%03d' % (tt_first.tm_year, tt_first.tm_yday))
                                tt = t.timetuple()
                                julian_t = ('%d%03d' % (tt.tm_year, tt.tm_yday))
                            else:
                                tt = t.timetuple()
                                julian_t = ('%d%03d' % (tt.tm_year, tt.tm_yday))
                                pcp_dates.append(julian_t)
                        else:
                            if i == 1:
                                tt = (t+timedelta(days=n)).timetuple()
                                julian_t = ('%d%03d' % (tt.tm_year, tt.tm_yday))
                                pcp_dates.append(julian_t)
                            if n > 0:
                                pcp_array[n-1, i-1] = float(lines[n])
            else:
                raise QgsProcessingException('No pcp file found: \"' +
                                                     station_pcp_filename + '\" ')

        if pcp_dates:
            # From Julian day to date
            last_pcp_date = date(int(pcp_dates[-1][0:4]), 1, 1) +\
                            timedelta(days=int(pcp_dates[-1][4:7]) - 1)
            first_pcp_date = date(int(pcp_dates[0][0:4]), 1, 1) +\
                             timedelta(days=int(pcp_dates[0][4:7]) - 1)
            log_file.write("First day of pcp in .pcp file: %s \n" %
                           first_pcp_date.strftime('%Y%m%d'))
            log_file.write("Last day of pcp in .pcp file: %s \n" %
                           last_pcp_date.strftime('%Y%m%d'))

        else:
            last_pcp_date = date(int(julian_tfirst[0:4]), 1, 1) +\
                            timedelta(days=int(julian_tfirst[4:7]) - 1)
            first_pcp_date = date(int(julian_t[0:4]), 1, 1) +\
                             timedelta(days=int(julian_t[4:7]) - 1)
            pcp_dates.append(julian_t)

        return pcp_dates, first_pcp_date, last_pcp_date, pcp_array

    def readTmpFiles(self, log_file):
        """Reading the Budyko .tmp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)
        # Reading old .tmp files to numpy array
        tmp_max_array = None
        tmp_min_array = None
        tmp_dates = []
        for i in station_id_sorted:
            station_tmp_filename = os.path.join(station_folder,
                                                self.station_id_dict[i] + 'temp.txt')
            if os.path.isfile(station_tmp_filename):
                with open(station_tmp_filename, 'r') as tmp_file:
                    lines = tmp_file.readlines()
                    lines_number = len(lines)
                if tmp_max_array is None:
                    tmp_max_array = numpy.zeros([lines_number-1, len(station_id_sorted)],
                                                dtype=numpy.float)
                    tmp_min_array = numpy.zeros([lines_number-1, len(station_id_sorted)],
                                                dtype=numpy.float)
                for n in range(lines_number):
                    if (n == 0 and i == 1):
                        t = datetime.datetime.strptime(lines[0][0:8], '%Y%m%d')
                        if lines_number == 1:
                            tt_first = (t-timedelta(days=1)).timetuple()
                            julian_tfirst = ('%d%03d' % (tt_first.tm_year, tt_first.tm_yday))
                            tt = t.timetuple()
                            julian_t = ('%d%03d' % (tt.tm_year, tt.tm_yday))
                        else:
                            tt = t.timetuple()
                            julian_t = ('%d%03d' % (tt.tm_year, tt.tm_yday))
                            tmp_dates.append(julian_t)
                    else:
                        #  t=time.strptime('20110531','%Y%m%d')
                        if i == 1:
                            tt_next = (t+timedelta(days=n)).timetuple()
                            julian_t = ('%d%03d' % (tt_next.tm_year, tt_next.tm_yday))
                            tmp_dates.append(julian_t)
                        if n > 0:
                            tmp_max_array[n-1, i-1] = float(lines[n][0:5])
                            tmp_min_array[n-1, i-1] = float(lines[n][6:13])
            else:
                raise QgsProcessingException('No tmp file found: \"' +
                                                     station_tmp_filename + '\" ')

        if tmp_dates:
            # From Julian day to date
            last_tmp_date = date(int(tmp_dates[-1][0:4]), 1, 1) +\
                            timedelta(days=int(tmp_dates[-1][4:7]) - 1)
            first_tmp_date = date(int(tmp_dates[0][0:4]), 1, 1) +\
                             timedelta(days=int(tmp_dates[0][4:7]) - 1)
            log_file.write("First day of tmp in .tmp file: %s \n" %
                           first_tmp_date.strftime('%Y%m%d'))
            log_file.write("Last day of tmp in .tmp file: %s \n" %
                           last_tmp_date.strftime('%Y%m%d'))
        else:
            last_tmp_date = date(int(julian_tfirst[0:4]), 1, 1) +\
                            timedelta(days=int(julian_tfirst[4:7]) - 1)
            first_tmp_date = date(int(julian_t[0:4]), 1, 1) +\
                             timedelta(days=int(julian_t[4:7]) - 1)
            tmp_dates.append(julian_t)

        return tmp_dates, first_tmp_date, last_tmp_date, tmp_max_array, tmp_min_array

    def writePcpFiles(self, first_pcp_date, pcp_array, log_file):
        """Write the Budyko .pcp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)
        # Writing .pcp files
        for i in station_id_sorted:
            station_pcp_filename = os.path.join(station_folder, self.station_id_dict[i] + '.txt')
            if os.path.isfile(station_pcp_filename):
                with open(station_pcp_filename, "w") as f:
                    # Write startdate
                    f.write("%s\n" % (first_pcp_date).strftime('%Y%m%d'))
                    # Write array to file
                    for l in range(len(pcp_array)):
                        f.write(("%.1f" % pcp_array[l, i-1]))
                        f.write('\n')
            else:
                raise QgsProcessingException('No .pcp file found:: \"' +
                                                     station_pcp_filename + '\" ')

    def writeTmpFiles(self, first_tmp_date, tmp_max_array, tmp_min_array, log_file):
        """Write the Budyko temp.txt files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)
        # Writing .pcp files
        for i in station_id_sorted:
            station_tmp_filename = os.path.join(station_folder,
                                                self.station_id_dict[i] + 'temp.txt')
            if os.path.isfile(station_tmp_filename):
                with open(station_tmp_filename, "w") as f:
                    # Write header
                    f.write("%s\n" % (first_tmp_date).strftime('%Y%m%d'))
                    # Write array to file
                    for l in range(len(tmp_max_array)):
                        f.write("%05.1f" % tmp_max_array[l, i-1])
                        f.write(',')
                        f.write(("%05.1f" % tmp_min_array[l, i-1]))
                        f.write('\n')
            else:
                raise QgsProcessingException('No .tmp file found: \"' +
                                                     station_tmp_filename + '\" ')
