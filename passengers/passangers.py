# -*- encoding: utf-8 -*-


def move_passenger(data, name, distance):
    for i in range(len(data)):
        for j in range(len(data[i]['cars'])):
            if name in data[i]['cars'][j]['people']:
                passenger_place = {'train': i, 'car': j}
                cars_count = len(data[i]['cars'])
    if not passenger_place:
        return False
    if distance != 0:
        new_passenger_place = passenger_place['car'] + distance
        if new_passenger_place in range(cars_count):
            data[passenger_place['train']]['cars'][passenger_place['car']]['people'].remove(name)
            data[passenger_place['train']]['cars'][new_passenger_place]['people'].append(name)
            return True
        else:
            pass
    else:
        return False


def move_car(data, count, train_from, train_to):
    moving_cars = []
    for train in data:
        if train['name'] == train_from:
            train_cars_count = len(train['cars'])
            if train_cars_count >= count:
                for i in range(count, 0, -1):
                    moving_cars.append(train['cars'].pop(-i))
            else:
                return False
    if not moving_cars:
        return False
    for train in data:
        if train['name'] == train_to:
            train['cars'].extend(moving_cars)
            moving_cars.clear()
            return True
    if moving_cars:
        return False


def passengers_count(data, name):
    for train in data:
        for car in train['cars']:
            if car['name'] == name:
                passengers_count = len(car['people'])
    if passengers_count:
        return passengers_count
    else:
        return -1


def process(data, events, car):
    for i in range(len(events)):
        event_type = events[i]['type']
        if event_type == 'walk':
            event_passenger_name = events[i]['passenger']
            event_distance = events[i]['distance']
            passenger_move_result = move_passenger(data, event_passenger_name, event_distance)
            if not passenger_move_result:
                return -1
        elif event_type == 'switch':
            event_cars_count = events[i]['cars']
            event_train_from = events[i]['train_from']
            event_train_to = events[i]['train_to']
            car_move_result = move_car(data, event_cars_count, event_train_from, event_train_to)
            if not car_move_result:
                return -1
        else:
            return -1
    return passengers_count(data, car)
