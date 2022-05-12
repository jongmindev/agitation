import agiplan
import members
import pandas as pd
import random
import numpy as np
import os


class Counter:
    def __init__(self, agi_plans: pd.DataFrame):
        self.assigned_lecture_by_members = self._initialize_lecture()
        self.assigned_number_by_members = self._initialize_number()
        self.assigned_members_by_lecture = self._initialize_members(agi_plans)

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
    def _initialize_members(agi_plans: pd.DataFrame) -> dict[int, list]:
        mem = {}
        for index in list(agi_plans.index):
            mem[index] = []
        return mem

    def update_assignment(self, assigned_members: list[str], lecture_index: int):
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
            # raise NoSolutionError(f"Fail to get a solution at step {choice_weighted_inversely.counter}! "
            #                       f"It's need to rerun.")
            raise NoSolutionError(f"Fail to get a solution! It's need to rerun.")

        all_values = assigned_number.values()
        max_value = max(all_values)
        reversed_number = assigned_number.copy()
        for key, value in reversed_number.items():
            reversed_number[key] = (max_value + 1 - value) ** 2

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
        if time >= 1800:
            available_members = list(timetables.keys())
        else:
            for name, timetable in timetables.items():
                if zone in timetable.loc[time, day]:
                    available_members.append(name)
        return available_members

    @staticmethod
    def _number_of_members_required(students: int) -> int:
        if students <= 30:
            required = 2
        elif students <= 50:
            required = 3
        elif students <= 100:
            required = 4
        else:
            required = 5
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


class PartialDistribution:
    def __init__(self, agi_plans: pd.DataFrame):
        self.AGI_PLANS = agi_plans
        self._counter = Counter(agi_plans)
        self._timetables = members.LoadTimetables.read_multiple_timetables()
        # choice_weighted_inversely.counter = 0

    def assign_a_lecture(self, lecture_index: int):
        lecture = self.AGI_PLANS.loc[lecture_index]

        when = random.randint(0, len(lecture.day) - 1)
        day = lecture.day[when]
        time = lecture.time[when]
        zone = lecture.zone[when]
        students = lecture.many
        assigned_members = Assign.assign_members(day, time, zone, students,
                                                 self._timetables, self._counter.assigned_number_by_members)

        self._counter.update_assignment(assigned_members, lecture_index)
        self._timetables = Assign.updated_members_timetable(assigned_members, day, time, self._timetables)

    def assign_all_lectures(self):
        indices = list(self.AGI_PLANS.index)
        for lecture_index in indices:
            print(lecture_index)
            print(indices)
            self.assign_a_lecture(lecture_index)

    @property
    def assigned_lecture_by_members(self):
        return self._counter.assigned_lecture_by_members

    @property
    def assigned_number_by_members(self):
        return self._counter.assigned_number_by_members

    @property
    def assigned_members_by_lecture(self):
        return self._counter.assigned_members_by_lecture


class TotalDistribution:
    AGI_PLANS = agiplan.ModifiedAgiList().m_agilist

    def __init__(self, partition: int):
        self.split_plans = self._partition_plans(partition)

    @classmethod
    def _partition_plans(cls, partition: int) -> list[pd.DataFrame]:
        lecture_indices = list(cls.AGI_PLANS.index)
        np.random.shuffle(lecture_indices)

        list_of_split_indices = np.array_split(lecture_indices, partition)
        split_plans = []
        for indices in list_of_split_indices:
            split_plans.append(cls.AGI_PLANS.loc[indices])

        return split_plans

    @staticmethod
    def assign_until_success(agi_plans: pd.DataFrame, max_iter: int = 20):
        cnt = 0
        while cnt < max_iter:
            try:
                dist = PartialDistribution(agi_plans)
                dist.assign_all_lectures()
            except NoSolutionError:
                cnt += 1
                if cnt == max_iter:
                    raise NoSolutionError
                continue
            break
        return (list[agi_plans.index],
                dist.assigned_lecture_by_members, dist.assigned_number_by_members, dist.assigned_members_by_lecture)

    def total_assign(self, max_iter):
        results = []
        for partition_plan in self.split_plans:
            partition_result = self.assign_until_success(partition_plan, max_iter)
            results.append(partition_result)
        return results


if __name__ == "__main__":
    AGI_PLANS = agiplan.ModifiedAgiList().m_agilist
    # dist = PartialDistribution(AGI_PLANS)
    # # dist.assign_a_lecture(5)
    # dist.assign_all_lectures()
    # print(dist.assigned_lecture_by_members)
    # print(dist.assigned_number_by_members)
    # print(dist.assigned_members_by_lecture)

    total_dist = TotalDistribution(4)
    results = total_dist.total_assign(max_iter=20)
    for sub_result in results:
        print("index : ", sub_result[0])
        print("lecture by members", sub_result[1])
        print("numbers by members", sub_result[2])
        print("members by lecture", sub_result[3])

