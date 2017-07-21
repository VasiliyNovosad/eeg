# -*- coding: utf-8 -*-
import ctypes
from ctypes import *
from numpy import *
import scipy.signal as s_signal
import os
import time
import sys
from ctypes.util import find_library
print ctypes.util.find_library('edk.dll')
print os.path.exists('.\\edk.dll')
libEDK = cdll.LoadLibrary(".\\edk.dll")

ED_COUNTER = 0
ED_INTERPOLATED = 1
ED_RAW_CQ = 2
ED_AF3 = 3
ED_F7 = 4
ED_F3 = 5
ED_FC5 = 6
ED_T7 = 7
ED_P7 = 8
ED_O1 = 9
ED_O2 = 10
ED_P8 = 11
ED_T8 = 12
ED_FC6 = 13
ED_F4 = 14
ED_F8 = 15
ED_AF4 = 16
ED_GYROX = 17
ED_GYROY = 18
ED_TIMESTAMP = 19
ED_ES_TIMESTAMP = 20
ED_FUNC_ID = 21
ED_FUNC_VALUE = 22
ED_MARKER = 23
ED_SYNC_SIGNAL = 24

EDK_OK = 0

targetChannelList = [ED_COUNTER, ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, ED_P7, ED_O1, ED_O2, ED_P8, ED_T8, ED_FC6, ED_F4, ED_F8, ED_AF4, ED_GYROX, ED_GYROY, ED_TIMESTAMP, ED_FUNC_ID, ED_FUNC_VALUE, ED_MARKER, ED_SYNC_SIGNAL]
header = ['COUNTER', 'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4', 'GYROX', 'GYROY', 'TIMESTAMP', 'FUNC_ID', 'FUNC_VALUE', 'MARKER', 'SYNC_SIGNAL']
channels = ['F3', 'F4']
channelsList = [ED_F3, ED_F4]
eEvent = libEDK.EE_EmoEngineEventCreate()
eState = libEDK.EE_EmoStateCreate()
userID = c_uint(0)
nSamples = c_uint(0)
nSamplesTaken = pointer(nSamples)
data = pointer(c_double(0))
user = pointer(userID)
secs = c_float(1)
datarate = c_uint(0)
readytocollect = False
write = sys.stdout.write

print libEDK.EE_EngineConnect("Emotiv Systems-5")
if libEDK.EE_EngineConnect("Emotiv Systems-5") != 0:
    print "Emotiv Engine start up failed."

print "Start receiving EEG Data! Press any key to stop logging...\n"
f = open('EEG.csv', 'w')
print >> f, channels
result = {}

hData = libEDK.EE_DataCreate()
libEDK.EE_DataSetBufferSizeInSec(secs)


while True:
    state = libEDK.EE_EngineGetNextEvent(eEvent)
    if state == EDK_OK:
        eventType = libEDK.EE_EmoEngineEventGetType(eEvent)
        libEDK.EE_EmoEngineEventGetUserId(eEvent, user)
        if eventType == 16: # libEDK.EE_Event_enum.EE_UserAdded:
            print "User added"
            libEDK.EE_DataAcquisitionEnable(userID, True)
            readytocollect = True

    if readytocollect:
        # TODO
        # отримати дані за 30 секунд
        # повіднімати середні значення по каналах
        # розрахувати потужність альфа, тета, бета
        # eeg.get_power_features()
        # отримувати дані за останні 4 секунди
        # повіднімати середні значення по каналах
        # розрахувати потужність альфа, тета, бета за останні 4 секунди
        # фильтровать в альфа-диапазоне
        # додати параметри (поріг спрацювання)

        libEDK.EE_DataUpdateHandle(0, hData)
        libEDK.EE_DataGetNumberOfSample(hData, nSamplesTaken)
        # print "Updated :", nSamplesTaken[0]
        if nSamplesTaken[0] != 0:
            nSam = nSamplesTaken[0]
            arr = (ctypes.c_double * nSamplesTaken[0])()
            ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))
            data = array('d') # zeros(nSamplesTaken[0], double)
            for i in range(22):
                libEDK.EE_DataGet(hData, targetChannelList[i], byref(arr), nSam)
                avg_el = 0
                if header[i] in channels:
                    values = []
                    for x in arr:
                        values.append(x - avg_el)
                    avg_el = sum(values) / len(values)
                    # print header[i], avg_el
                    # print >> f, avg_el, ",",
                    for x in values:
                        if header[i] in result.keys():
                            result[header[i]].append(x - avg_el)
                        else:
                            result[header[i]] = [x - avg_el]
            # print >> f, '\n'
        if len(result['F3']) > 512:
            new_result = {}
            new_result['F3'] = result['F3'][-512:]
            new_result['F4'] = result['F4'][-512:]
            result = new_result

            freq_x, Pxx_den = s_signal.welch(x=result['F3'], fs=128.0, nperseg=128, nfft=512, detrend=False,
                                       return_onesided=True, scaling='spectrum')
            freq_y, Pyy_den = s_signal.welch(x=result['F4'], fs=128.0, nperseg=128, nfft=512, detrend=False,
                                       return_onesided=True, scaling='spectrum')

            # print >> f, 'num,freq,F3,F4'
            # for i in range(len(freq_x)):
            #     print >> f, i, ",", freq_x[i], ",", Pxx_den[i], ",", Pyy_den[i]
            #
            # f.close()

            sum_f3 = sum(Pxx_den[32:52])
            sum_f4 = sum(Pyy_den[32:52])

            koef = log((sum_f3 - sum_f4) / (sum_f3 + sum_f4))
            print koef

    time.sleep(1)
libEDK.EE_DataFree(hData)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
libEDK.EE_EngineDisconnect()
libEDK.EE_EmoStateFree(eState)
libEDK.EE_EmoEngineEventFree(eEvent)

# print result

# signal = []
# for i in range(512):
#     signal.append([result['F3'][i], result['F4'][i]])
# print signal
#
# f = open('EEG_Filtered_20170622.csv', 'w')
# print >> f, 'F3,F4'
# for i in range(len(signal)):
#     print >> f, signal[i][0], ",", signal[i][1]
#
# print >> f, '\n'
#
# result_new = eeg.get_power_features(signal=signal, sampling_rate=128., size=4.0)
#
# print >> f, 'theta,alpha_low,alpha_high,beta,gamma'
# print >> f, result_new['theta'], ",", result_new['alpha_low'], ",", result_new['alpha_high'], ",", result_new['beta'], ",", result_new['gamma']
#
# print result_new
#
# print >> f, '\n'
#
# # signal = []
# # for i in range(512):
# #     signal.append([result['F3'][i], result['F4'][i]/2.0])
# # print signal
# #
# # print >> f, 'F3,F4'
# # for i in range(len(signal)):
# #     print >> f, signal[i][0], ",", signal[i][1]
# #
# # print >> f, '\n'
# #
# # result_new = eeg.get_power_features(signal=signal, sampling_rate=128., size=4.0)
# #
# # print >> f, 'theta,alpha_low,alpha_high,beta,gamma'
# # print >> f, result_new['theta'], ",", result_new['alpha_low'], ",", result_new['alpha_high'], ",", result_new['beta'], ",", result_new['gamma']
#
# x, Pxx_den = ssignal.welch(x=result['F3'][0:512], fs=128.0, nperseg=128, nfft=512, detrend=False, return_onesided=True, scaling='spectrum')
# y, Pyy_den = ssignal.welch(x=result['F4'][0:512], fs=128.0, nperseg=128, nfft=512, detrend=False, return_onesided=True, scaling='spectrum')
#
# print >> f, 'num,freq,F3,F4'
# for i in range(len(x)):
#     print >> f, i, ",", x[i], ",", Pxx_den[i], ",", Pyy_den[i]
#
# f.close()


