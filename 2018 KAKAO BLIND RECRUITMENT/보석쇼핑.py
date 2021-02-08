def solution(gems):
    answer = []
    gem_type = {}
    for item in gems:
        gem_type[item] = 1
    print(len(gem_type.keys()))
    
    gem_count = {}
    for key in gem_type.keys():
        gem_count[key] = 0
    print(gem_count)
    
    start = 0
    end = 0
    num = 0
    min = [9999999,0]
    for i in range(len(gems)):
        item = gems[i]
        if gem_count[item] == 0:
            num += 1
        gem_count[item] += 1
        #print(start, end)
        if num == len(gem_type.keys()):
            for j in range(start, i):
                if gem_count[gems[j]] == 1:
                    break
                gem_count[gems[j]] -= 1
                start += 1
                #print(start, end)
            if min[0]-min[1] > end-start:
                min = [end, start]
                print(start, end)
                
        end += 1
    answer = [min[1]+1, min[0]+1]
    return answer
