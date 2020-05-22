import collections
import itertools
from datetime import datetime, timedelta

from datetimerange import DateTimeRange

MINUTES = 30


def merge_schedules(players, required, start):

    if not start:
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
    candidates = DateTimeRange(start, start + timedelta(days=7))

    potentials = collections.defaultdict(list)

    for candidate_times in candidates.range(timedelta(minutes=MINUTES)):
        candidate_players = []
        for player, timeranges in players.items():
            for timerange in timeranges:
                if timerange.start_datetime <= candidate_times < timerange.end_datetime:
                    candidate_players.append(player)

        for combination_length in range(required, len(candidate_players) + 1):
            potentials[candidate_times].extend(
                itertools.combinations(candidate_players, combination_length)
            )

    return potentials


def find_times(players, required, start=None):

    schedules = merge_schedules(players, required, start)
    potentials = collections.defaultdict(list)

    for viable_time, player_sets in schedules.items():
        for player_set in player_sets:

            current_players = frozenset(player_set)

            if not potentials[current_players]:
                potentials[current_players].append(DateTimeRange(viable_time))

            current_time = potentials[current_players][-1]

            if (
                viable_time - current_time.start_datetime
            ).total_seconds() <= MINUTES * 60:
                current_time.set_end_datetime(viable_time)
            elif (
                viable_time - current_time.end_datetime
            ).total_seconds() <= MINUTES * 60:
                current_time.set_end_datetime(viable_time)
            else:
                potentials[current_players].append(DateTimeRange(viable_time))

    for time_ranges in potentials.values():
        for time_range in time_ranges:
            time_range.set_end_datetime(
                time_range.end_datetime + timedelta(minutes=MINUTES)
            )

    return potentials


def filter_times(potentials, duration):

    filtered = collections.defaultdict(list)

    for players, time_ranges in potentials.items():
        for time_range in time_ranges:
            if time_range.get_timedelta_second() >= duration * 60 * 60:
                filtered[players].append(time_range)

    return filtered
