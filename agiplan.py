import campusmap
import os
import pandas as pd


class _LoadPlans:
    def __init__(self):
        self._plans = self.read_multiple_plan_files()

    @staticmethod
    def read_multiple_plan_files():
        folder = r'C:\Users\12skd\Dev\PycharmProjects\agitation\data\plan'
        files = os.listdir(folder)

        _plans = {}
        for file in files:
            if file.endswith('.xlsx'):
                college = file[:-5]
                df = pd.read_excel(os.path.join(folder, file))
                # plans[college] = df.loc[:, '요일':'수강인원']
                _plans[college] = df.loc[:, '요일':'수강인원'].dropna()

        return _plans

    @property
    def plans(self):
        return self._plans


class _AgiList:
    def __init__(self):
        _col = ['개설대학', '개설학과', '교과목번호', '강좌번호', '교과목명', '부제명',
                '수업교시', '강의실(동-호)(#연건, *평창)', '수강신청인원']
        self._SUGANG = pd.read_excel(r"data\강좌검색.xls")[_col]
        self._check_plans()
        self._AGILIST = self._SUGANG.loc[self._SUGANG.check == 1].drop(columns='check').reset_index(drop=True)

    def _check_plans(self):
        _plans = _LoadPlans().plans
        for college, plan in _plans.items():
            for index, row in plan.iterrows():
                condition1 = self._SUGANG.교과목명.str.replace(' ', '').str.contains(row['수업이름'].replace(' ', ''))
                try:
                    condition2 = self._SUGANG['강의실(동-호)(#연건, *평창)'].str.contains(row['장소'].upper())
                except AttributeError:
                    condition2 = self._SUGANG['강의실(동-호)(#연건, *평창)'].str.contains(str(row['장소']))
                condition3 = self._SUGANG['수업교시'].str.contains(row['요일'][0])
                condition4 = self._SUGANG['수업교시'].str.contains(row['요일'][-1])
                self._SUGANG.loc[condition1 & condition2 & condition3 & condition4, 'check'] = 1
            print(college, " done")

    def save_agilist(self):
        self._AGILIST.to_csv(r"csv\agilist.csv", index=False)

    @property
    def agilist(self):
        return self._AGILIST


class ModifiedAgiList:
    def __init__(self):
        if os.path.isfile(r'csv\agilist.csv'):
            self._agilist = pd.read_csv(r"csv\agilist.csv")
        else:
            self._agilist = _AgiList().agilist
        self._m_agilist = self._modify_agilist()

    def _day_and_time(self) -> pd.DataFrame:
        split_daytime = self._agilist.수업교시.str.split(pat='/')

        def extract_day(element: list[str]) -> list:
            _day_list = []
            for data in element:
                _day_list.append(data[0])
            return _day_list

        def extract_time(element: list[str]) -> list:
            _time_list = []
            for data in element:
                _time_list.append(int(data[2:7].replace(':', '')))
            return _time_list

        day_series = split_daytime.map(extract_day)
        day_series.name = 'day'
        time_series = split_daytime.map(extract_time)
        time_series.name = 'time'

        if day_series.size != time_series.size:
            raise ValueError('수업요일과 수업시간이 대응되지 않습니다.')

        return pd.merge(day_series, time_series, left_index=True, right_index=True)

    def _zone(self) -> pd.Series:
        split_zone = self._agilist['강의실(동-호)(#연건, *평창)'].str.split(pat='/')

        def extract_zone(element: list[str]) -> list:
            _zone_list = []
            for data in element:
                try:
                    building = int(data.split('-')[0])
                    _zone_list.append(campusmap.CampusMap.zone(building))
                except ValueError:
                    _zone_list.append('Y')
            # from collections import OrderedDict
            # _zone_list = list(OrderedDict.fromkeys(_zone_list))
            return _zone_list

        zone_series = split_zone.map(extract_zone)
        zone_series.name = 'zone'

        return zone_series

    def _modify_agilist(self) -> pd.DataFrame:
        col_college = self._agilist.개설대학
        col_college.name = 'college'
        col_daytime = self._day_and_time()
        col_zone = self._zone()
        col_many = self._agilist.수강신청인원
        col_many.name = 'many'
        return pd.concat([col_college, col_daytime, col_zone, col_many], axis='columns')

    @property
    def m_agilist(self):
        return self._m_agilist


# class PlanAppend:
#     if not os.path.isfile(r'csv\agilist.csv'):
#         AgiList().save_agilist()
#     campus_map = campusmap.CampusMap.MAP
#
#     @classmethod
#     def append_zone(cls, _plans: dict[str, pd.DataFrame]):
#         def map_zone(row: pd.Series):
#             building = str(row.loc['장소']).split('-')[0]
#             try:
#                 return campusmap.CampusMap.zone(int(building))
#             except ValueError:
#                 return 'Y'
#
#         for college, plan in _plans.items():
#             _plans[college]['구역'] = plan.apply(map_zone, axis=1)
#
#         return _plans
#
#     @classmethod
#     def append_start(cls, _plans: dict[str, pd.DataFrame]):
#         def map_start(row: pd.Series):
#             lecture_time = str(row.loc['시간'])
#
# PlanAppend()


if __name__ == '__main__':
    agilist = ModifiedAgiList().m_agilist
    print(agilist)
