import scipy.signal as ssignal
import string

f = open("EEG_test.csv", "rb")
result = {'F3': [], 'F4': []}
for line in f.xreadlines():
    print line
    row = string.split(line, ',')
    result['F3'].append(float(row[0]))
    result['F4'].append(float(row[1]))

x, Pxx_den = ssignal.welch(x=result['F3'][0:512], fs=128.0, nperseg=128, nfft=512, detrend=False, return_onesided=True, scaling='spectrum')
y, Pyy_den = ssignal.welch(x=result['F4'][0:512], fs=128.0, nperseg=128, nfft=512, detrend=False, return_onesided=True, scaling='spectrum')
f.close()

f = open('EEG_Filtered_20170621.csv', 'w')
print >> f, 'num,freq,F3,F4'
for i in range(len(x)):
    print >> f, i, ",", x[i], ",", Pxx_den[i], ",", Pyy_den[i]

f.close()
print x