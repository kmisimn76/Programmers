from operator import itemgetter

def next_ticket(tickets, disable, start, answer):
    if len(answer) == len(tickets)+1:
        return answer
    i = 0
    for ticket in tickets:
        if disable[i] == 0 and start == ticket[0]:
            answer.append(ticket[1])
            disable[i] = 1
            ret = next_ticket(tickets, disable, ticket[1], answer)
            if ret is not None:
                return ret
            disable[i] = 0
            answer.pop()
        i = i+1
    return None

def solution(tickets):
    answer = []
    disable = [0 for i in range(len(tickets))]
    tickets.sort(key=itemgetter(1))
    tickets.sort(key=itemgetter(0))
    print(tickets)
    answer.append("ICN")
    answer = next_ticket(tickets, disable, "ICN", answer)
    return answer
