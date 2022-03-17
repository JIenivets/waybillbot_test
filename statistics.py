stat = {'cout_new_messages': 0,
        'truck':
            {'last_number': 0,
             'number_of_new_messages': 0,
             'time_last_message': None,
             'last_recipients_name': None},
        'car':
            {'last_number': 0,
             'number_of_new_messages': 0,
             'time_last_message': None,
             'last_recipients_name': None}
        }


def statistics(type, number, time, name):
    stat['cout_new_messages'] += 1
    stat[type]['number_of_new_messages'] += 1
    stat[type]['last_number'] = number
    stat[type]['time_last_message'] = time
    stat[type]['last_recipients_name'] = name