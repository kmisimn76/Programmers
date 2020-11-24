import datetime

def solution(lines):
    answer = 0
    time = []
    for data in lines:
        splited_data = data.split(' ')
        time_end = int((datetime.datetime.strptime(splited_data[0] + ' ' + splited_data[1], '%Y-%m-%d %H:%M:%S.%f')).timestamp()*1000)
        #print(time_end)
        time_start = int(time_end - int(float(splited_data[2][:-1])*1000))
        #print(time_start)
        time.append((time_start, 0))
        time.append((time_end, 1))
    time.sort()
    #print([datetime.datetime.fromtimestamp(t[0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for t in time])
    #print(time)
    
    max = 0
    n = 0
    
    for i in range(len(time)):
        if time[i][1] == 0:
            #start
            n += 1
            k = n
            for j in range(i-1, -1, -1):
                if (time[i][0] - time[j][0]) >= 999:
                    break
                if time[j][1] == 1:
                    k += 1
            if max < k:
                max = k
        else :
            #end
            n -= 1
            k = n
            for j in range(i+1, len(time)):
                if (time[j][0] - time[i][0]) >= 999:
                    break
                if time[j][1] == 0:
                    k += 1
            if max < k:
                max = k
    answer = max
    return answer