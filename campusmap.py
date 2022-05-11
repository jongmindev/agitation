import pandas as pd


ADJACENT_ZONE = {
    'A': "BI",
    'I': "ABH",
    'B': "AIH",
    'C': "DEH",
    'D': "CE",
    'H': "BCI",
    'E': "DCG",
    'G': "E",
    'F': ""
}


class CampusMap:
    @staticmethod
    def draw_campus_map() -> dict:
        # 단과대 등 소속별 건물
        f = pd.read_excel(r'data\buildings.xlsx', index_col='구역', usecols=list(range(1, 16)))
        # campus_map = campus_map.astype(int, errors='ignore')

        pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.expand_frame_repr', False)
        # print(campus_map)

        _campus_map = {}

        for row in f.iterrows():
            zone = row[0]
            buildings = row[1].dropna().astype(int)
            if zone not in _campus_map:
                _campus_map[zone] = set(buildings)
            else:
                _campus_map[zone] = _campus_map[zone] | set(buildings)

        return _campus_map

    MAP = draw_campus_map()

    @classmethod
    def zone(cls, _building: int):
        zone = None
        for z, b in cls.MAP.items():
            if _building in b:
                zone = z
                break
        if zone is None:
            raise ValueError(f"해당 건물의 구역을 찾을 수 없습니다. : {_building}", )
        return zone


if __name__ == "__main__":
    for building in range(200):
        try:
            print(building, " : ", CampusMap.zone(building))
        except ValueError:
            print(building, " : 해당 건물의 구역을 찾을 수 없습니다.")

    print(CampusMap.MAP)
