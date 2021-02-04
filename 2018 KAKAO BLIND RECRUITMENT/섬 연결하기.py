from operator import itemgetter
import copy

def solution(n, costs):
    answer = 0
    adj_mat = [[0 for j in range(n)] for i in range(n)]
    costs.sort(key=itemgetter(2))
    tot_cost = 0
    for i in range(n):
        adj_mat[i][i] = 1
    for cost in costs:
        if next((i for i, x in enumerate([adj_mat[cost[0]][k]*adj_mat[cost[1]][k] for k in range(n)]) if x), None) is not None: # unnecessary bridge: neither cost[0] and cost[1] element is zero means two islands were already connected
            continue
        # Connect between two islands
        adj_mat[cost[0]][cost[1]] = 1
        adj_mat[cost[1]][cost[0]] = 1
        for i in range(n):
            if adj_mat[cost[0]][i]!=0:
                # Connect between one island and islands connected another one
                adj_mat[cost[1]][i] = 1
                adj_mat[i][cost[1]] = 1
                # Connect between islands that each connected two islands
                for j in range(n):
                    if adj_mat[cost[1]][j]!=0:
                        adj_mat[i][j] = 1
                        adj_mat[j][i] = 1
            if adj_mat[cost[1]][i]!=0:
                adj_mat[cost[0]][i] = 1
                adj_mat[i][cost[0]] = 1
                for j in range(n):
                    if adj_mat[cost[0]][j]!=0:
                        adj_mat[i][j] = 1
                        adj_mat[j][i] = 1
        tot_cost += cost[2]

    answer = tot_cost
    return answer
