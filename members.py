import numpy as np
import campusmap
import pandas as pd


ALL = 'ABCDEFGHIJK'


class TimetableBy30Min:
    # 시간표가 15분 단위 구분인 것을 30분 단위로 변경
    @staticmethod
    def _fill_last_15min(day: pd.Series):
        for i in range(1, 36, 2):
            try:
                int(day.iloc[i-1])
                day.iloc[i] = day.iloc[i-1]
            except ValueError:
                pass

    @classmethod
    def modify_by_30min(cls, _timetable: pd.DataFrame) -> pd.DataFrame:
        _timetable.apply(cls._fill_last_15min, axis=0)
        _timetable['시간'] = _timetable['시간'].map(lambda x: int(str(x)[:-4]))
        _timetable.rename(columns={'시간': '시작시간'}, inplace=True)
        return _timetable.iloc[::2].reset_index(drop=True)

# example = TimetableBy30Min.modify_by_30min(example)


class ModifyTimetable:
    # ① 수업이 없는 날(공강일)
    @staticmethod
    def no_school(day: pd.Series):
        # all nan column
        if day.isna().all():
            day.fillna(ALL, inplace=True)
        # 시간표 상 'x' 와 nan 뿐인 날
        if set(day.unique()) - {'x', np.NAN} == set():
            day.fillna(ALL, inplace=True)
        return day

    # ② 연건캠퍼스 수업이 있는 날
    @staticmethod
    def at_yeongeon(day: pd.Series):
        non_nan_values = day.loc[day.notna()]
        if non_nan_values.str.contains('#').all():
            day.fillna('Y', inplace=True)
        return day

    # ③ 강의 종료시간 직후(30분 이내) : 인접 지역만 배분 가능(△)
    @staticmethod
    def right_after_lecture(_timetable: pd.DataFrame):
        for col in range(1, 6):
            for row in range(1, 18):
                if pd.isna(_timetable.iloc[row, col]) & str(_timetable.iloc[row-1, col]).isdigit():
                    building = int(_timetable.iloc[row-1, col])
                    zone = campusmap.CampusMap.zone(building)
                    _timetable.iloc[row, col] = campusmap.ADJACENT_ZONE[zone]

    # ④ 그날의 마지막 강의 종료시간에서 1시간 초과 경과(하교 후) (④의 예외) : 배분 불가(×)
    @staticmethod
    def after_school(day: pd.Series):
        day.loc[day.last_valid_index() + 4:] = 'x'
        return day

    # ⑤ 강의 종료시간에서 30분 이상 경과(공강) : 전 지역 배분 가능(○)
    @staticmethod
    def between_lecture(time_table: pd.DataFrame):
        return time_table.fillna(ALL)

    # ⑥ 강의시간 중 : 배분 불가(×)
    @staticmethod
    def during_lecture(element):
        all_possible = list(campusmap.CampusMap.MAP.keys()) + list(campusmap.ADJACENT_ZONE.values())[:-2]\
                       + ['ABCDEFGHIJK']
        if element not in all_possible:
            return 'x'
        else:
            return element


class PreprocessedTimetable:
    @ staticmethod
    def preprocess(_filepath: str):
        _timetable = pd.read_csv(_filepath, dtype=object)
        tt_30min = TimetableBy30Min.modify_by_30min(_timetable)
        # print('raw', tt_30min)
        # print()
        tt_30min.loc[:, '월':'금'] = tt_30min.loc[:, '월':'금'].apply(ModifyTimetable.no_school, axis=0)
        # print('no school', tt_30min)
        # print()
        tt_30min.loc[:, '월':'금'] = tt_30min.loc[:, '월':'금'].apply(ModifyTimetable.at_yeongeon, axis=0)
        # print('yeongeon', tt_30min)
        # print()
        ModifyTimetable.right_after_lecture(tt_30min)
        # print('right after', tt_30min)
        # print()
        tt_30min.loc[:, '월':'금'] = tt_30min.loc[:, '월':'금'].apply(ModifyTimetable.after_school, axis=0)
        # print('after school', tt_30min)
        # print()
        tt_30min.loc[:, '월':'금'] = ModifyTimetable.between_lecture(tt_30min.loc[:, '월':'금'])
        # print('between', tt_30min)
        # print()
        tt_30min.loc[:, '월':'금'] = tt_30min.loc[:, '월':'금'].applymap(ModifyTimetable.during_lecture)
        return tt_30min


if __name__ == '__main__':

    # filepath = r"data\members\고나영.csv"
    # filepath = r"data\members\김민정.csv"
    filepath = r"data\members\권세린.csv"

    raw = TimetableBy30Min.modify_by_30min(pd.read_csv(filepath, dtype=object))
    try:
        timetable = PreprocessedTimetable.preprocess(filepath)
        print(pd.concat([timetable, raw], axis='columns'))
    except Exception as e:
        print(raw)
        print(e)
