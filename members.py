import campusmap
import pandas as pd


class TimetableBy30Min:
    # 시간표가 15분 단위 구분인 것을 30분 단위로 변경
    @staticmethod
    def _fill_last_15mins(day: pd.Series):
        for i in range(1, 36, 2):
            try:
                int(day.iloc[i-1])
                day.iloc[i] = day.iloc[i-1]
            except ValueError:
                pass

    @classmethod
    def modify_by_30min(cls, timetable: pd.DataFrame) -> pd.DataFrame:
        timetable.apply(cls._fill_last_15mins, axis=0)
        timetable['시간'] = timetable['시간'].map(lambda x: int(str(x)[:-4]))
        timetable.rename(columns={'시간': '시작시간'}, inplace=True)
        return timetable.iloc[::2].reset_index(drop=True)

# example = TimetableBy30Min.modify_by_30min(example)


class ModifyTimetable:
    # ① 그 날의 첫 강의 시작시간 이전(등교 전) : 배분 불가 (x)
    @classmethod
    def before_school(cls, row: pd.Series):
        row.loc[:row.first_valid_index() - 1] = 'x'
    # tt_30mins.apply(before_school)

    # ③ 강의 종료시간 직후(30분 이내) : 인접 지역 아지테이션만 배분 가능(△)
    @classmethod
    def right_after_lecture(cls, day: pd.Series):
        for i in range(1, 18):
            if pd.isna(day.iloc[i]):
                try:
                    building = int(day.iloc[i-1])
                    lecture_zone = campusmap.CampusMap.zone(building)
                    adjacent_zone = campusmap.ADJACENT_ZONE[lecture_zone]
                    day.iloc[i] = adjacent_zone
                except ValueError:
                    pass
    # tt_30mins.apply(right_after_lecture)

    # ⑤ 그날의 마지막 강의 종료시간에서 1시간 초과 경과(하교 후) (④의 예외) : 배분 불가(×)
    @classmethod
    def after_school(cls, row: pd.Series):
        row.loc[row.last_valid_index() + 4:] = 'x'
    # tt_30mins.apply(after_school)

    # ④ 강의 종료시간에서 30분 이상 경과(공강) : 전 지역 배분 가능(○)
    @classmethod
    def between_lecture(cls, time_table: pd.DataFrame):
        return time_table.fillna('ABCDEFGHIJK')
    # tt_30mins = between_lecture(tt_30mins)

    # ② 강의시간 중 : 배분 불가(×)
    @classmethod
    def during_lecture(cls, entry):
        try:
            int(entry)
            return 'x'
        except ValueError:
            return entry
    # tt_30mins.loc[:, '월':'금'] = tt_30mins.loc[:, '월':'금'].applymap(during_lecture)


class PreprocessedTimetable:
    @ staticmethod
    def preprocess(filepath: str):
        _timetable = pd.read_csv(filepath)
        tt_30min = TimetableBy30Min.modify_by_30min(_timetable)
        tt_30min.apply(ModifyTimetable.before_school)
        tt_30min.apply(ModifyTimetable.right_after_lecture)
        tt_30min.apply(ModifyTimetable.after_school)
        tt_30min = ModifyTimetable.between_lecture(tt_30min)
        tt_30min.loc[:, '월':'금'] = tt_30min.loc[:, '월':'금'].applymap(ModifyTimetable.during_lecture)
        return tt_30min


if __name__ == '__main__':
    timetable = PreprocessedTimetable.preprocess(r"data\members\고나영.csv")
    # timetable = PreprocessedTimetable.preprocess(r"data\members\김민정.csv")
    # timetable = PreprocessedTimetable.preprocess(r"data\members\권세린.csv")

    # merged = pd.merge(timetable, raw_table, on='시작시간', suffixes=('', 'raw'))
    # col = merged.columns.tolist()
    # col.sort()
    # print(merged[col])

    print(timetable)
