import lectureslistup
import members
import pandas as pd
import numpy as np
import os


class Counter:
    def __init__(self, agi_plan: pd.DataFrame):
        self.assigned_lecture_by_members = self._initialize_lecture()
        self.assigned_number_by_members = self._initialize_number()
        self.assigned_members_by_lecture = self._initialize_members(agi_plan)

    @staticmethod
    def _initialize_lecture() -> dict[str, list[int]]:
        """

        :return: key : name of a member, value : list of index of assigned lecture
        """
        board = {}
        names = os.listdir(r"C:\Users\12skd\Dev\PycharmProjects\agitation\data\members")
        for filename in names:
            name = filename[:-4]
            board[name] = []
        return board

    @staticmethod
    def _initialize_number() -> dict[str, int]:
        """

        :return: key : name of a member, value : number of his/her participation
        """
        num = {}
        names = os.listdir(r"C:\Users\12skd\Dev\PycharmProjects\agitation\data\members")
        for filename in names:
            name = filename[:-4]
            num[name] = 0
        return num

    @staticmethod
    def _initialize_members(agi_plan: pd.DataFrame) -> dict[int, list[str]]:
        mem = {}
        for index in list(agi_plan.index):
            mem[index] = []
        return mem

    def update_assignment(self, assigned_members: list[str], lecture_index: int, when: int):
        self.assigned_members_by_lecture[lecture_index].append(when)
        for name in assigned_members:
            self.assigned_lecture_by_members[name].append(lecture_index)
            self.assigned_number_by_members[name] += 1
            self.assigned_members_by_lecture[lecture_index].append(name)


class NoSolutionError(Exception):
    def __init__(self, message="Fail to get a solution! It's need to rerun."):
        super().__init__(message)


class RandomChoice:
    @staticmethod
    def choice_weighted_inversely(required: int, assigned_number: dict[str, int]) -> np.ndarray:
        """
        sampling without replacement

        :param required: how many members required of the agitation?
        :param assigned_number: current assigned numbers of available members
        :return: weighted random sample without replacement
        """

        # choice_weighted_inversely.counter += 1

        if len(assigned_number.values()) < required:
            raise NoSolutionError(f"Fail to get a solution! It's need to rerun.")

        all_values = assigned_number.values()
        max_value = max(all_values)
        reversed_number = assigned_number.copy()
        for key, value in reversed_number.items():
            reversed_number[key] = (max_value + 1 - value) ** 3

        population = []
        weight = []
        for key, value in reversed_number.items():
            population.append(key)
            weight.append(value)
        weight = np.array(weight)/sum(weight)
        return np.random.choice(a=population, size=required, replace=False, p=weight)


class Assign:
    @staticmethod
    def _available_members_listup(day: str, time: int, zone: str, timetables: dict[str, pd.DataFrame]) -> list[str]:
        """
        Who can participate in the lecture agitation?

        :param day: day of target lecture
        :param time: start time of target lecture
        :param zone: zone of target lecture
        :return: list of available members
        """
        available_members = []
        if (time >= 1800) | (day == '토'):
            available_members = list(timetables.keys())
        else:
            for name, timetable in timetables.items():
                if zone in timetable.loc[time, day]:
                    available_members.append(name)
        return available_members

    @staticmethod
    def _number_of_members_required(students: int) -> int:
        if students <= 50:
            required = 2
        elif students <= 100:
            required = 3
        else:
            required = 4
        return required

    @staticmethod
    def _make_sub_dictionary(dictionary: dict, key_list: list) -> dict:
        return {key: value for key, value in dictionary.items() if (key in key_list)}

    @classmethod
    def assign_members(cls, day: str, time: int, zone: str, students: int,
                       timetables: dict[str, pd.DataFrame], assigned_number: dict[str, int]) -> list[str]:
        available = cls._available_members_listup(day, time, zone, timetables)
        assigned_number_of_available = cls._make_sub_dictionary(dictionary=assigned_number, key_list=available)
        required = cls._number_of_members_required(students)
        assigned_members = RandomChoice.choice_weighted_inversely(required, assigned_number_of_available)
        return list(assigned_members)

    @staticmethod
    def updated_members_timetable(assigned_members: list[str], day: str, time: int,
                                  timetables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for member in assigned_members:
            timetables[member].loc[time, day] = 'x'
        return timetables


class Distribution:
    def __init__(self, agilist: pd.DataFrame):
        self._agilist = agilist
        self._counter = Counter(agilist)
        self._timetables = members.LoadTimetables.read_multiple_timetables()

    def assign_a_lecture(self, agilist: pd.DataFrame, lecture_index: int):
        lecture = agilist.loc[lecture_index]

        when = np.random.randint(0, len(lecture.day))
        day = lecture.day[when]
        time = lecture.time[when]
        zone = lecture.zone[when]
        students = lecture.many
        assigned_members = Assign.assign_members(day, time, zone, students,
                                                 self._timetables, self._counter.assigned_number_by_members)

        self._counter.update_assignment(assigned_members, lecture_index, when)
        self._timetables = Assign.updated_members_timetable(assigned_members, day, time, self._timetables)

    def assign_all_lectures(self, agilist: pd.DataFrame):
        indices = list(agilist.index)
        for lecture_index in indices:
            # print(lecture_index)
            # print(agilist.loc[lecture_index, :])
            self.assign_a_lecture(agilist, lecture_index)

    def assign_until_success(self, max_iter: int = 20):
        cnt = 0
        while cnt < max_iter:
            try:
                self.assign_all_lectures(self._agilist)
            except NoSolutionError:
                # print(self._counter.assigned_members_by_lecture)
                # print(list(self._agilist.index))
                print("RETRY!")
                cnt += 1
                self._counter = Counter(self._agilist)
                self._timetables = members.LoadTimetables.read_multiple_timetables()
                if cnt == max_iter:
                    raise NoSolutionError
                continue
            break

    @property
    def assigned_lecture_by_members(self):
        return self._counter.assigned_lecture_by_members

    @property
    def assigned_number_by_members(self):
        return self._counter.assigned_number_by_members

    @property
    def assigned_members_by_lecture(self):
        return self._counter.assigned_members_by_lecture


if __name__ == "__main__":
    partition_size = 4
    ga_agilist = lectureslistup.AgilistPartitionGA(partition_size)
    first = Distribution(ga_agilist.ga_only_partition_agilist[0])
    # gayg_agilist = lectureslistup.AgiListPartition(partition_size)
    # first = Distribution(gayg_agilist.partition_agilist[0])
    # first.assign_until_success(20)

    for step, partition in enumerate(ga_agilist.ga_only_partition_agilist, 1):
        print(f"STEP {step} / {partition_size}")
        sub_planner = Distribution(partition)
        sub_planner.assign_until_success(20)
        print(sub_planner.assigned_members_by_lecture)
        print(sub_planner.assigned_lecture_by_members)
