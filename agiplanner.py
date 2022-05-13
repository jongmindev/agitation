import distribution
import lectureslistup
import numpy as np
import pandas as pd


class AgitationPlannerGA:
    def __init__(self, partition_size: int):
        self._lectures_listup = lectureslistup.AgilistPartitionGA(partition_size)
        self._lectures_board, self.members_board = self._make_plan(partition_size)

    def _make_plan(self, partition_size: int) -> tuple[dict[int, dict[int, list]], dict[int, dict[str, list]]]:
        partition_of_ga_lectures = self._lectures_listup.ga_only_partition_agilist

        lectures_board = {}
        members_board = {}
        for week, partition in enumerate(partition_of_ga_lectures, 1):
            print(f"WEEK : {week}/{partition_size}")
            sub_planner = distribution.Distribution(partition)
            sub_planner.assign_until_success(20)
            print(sub_planner.assigned_members_by_lecture)
            print(sub_planner.assigned_lecture_by_members)
            print()

            lectures_board[week] = sub_planner.assigned_members_by_lecture
            members_board[week] = sub_planner.assigned_lecture_by_members

        return lectures_board, members_board

    def visualized_lecture_board(self):
        ga_agilist = self._lectures_listup.ga_only_total_agilist.copy()
        ga_agilist['week'] = 0
        ga_agilist['members'] = ga_agilist.apply(lambda _: [].copy(), axis=1)

        for week, sub_planner in self._lectures_board.items():
            for lecture_index, assignment_list in sub_planner.items():
                # 여러 수업 시간 중 아지테이션 하도록 선택된 수업 시간에 관한 정보
                # 기존 agilist 의 정보를 위 정보로 대체
                when = assignment_list[0]
                ga_agilist.loc[lecture_index, 'day':'zone'] = \
                    np.stack(ga_agilist.loc[lecture_index, 'day':'zone'])[:, when]

                ga_agilist.loc[lecture_index, 'week'] = week

                members_list = assignment_list[1:]
                for name in members_list:
                    ga_agilist.loc[lecture_index, 'members'].append(name)

        return ga_agilist

    def visualized_members_board(self):
        members_board = self.members_board.copy()
        for week_assignments in members_board.values():
            for member_assignment in week_assignments.values():
                member_assignment.sort()
        v_board = pd.DataFrame(members_board)
        v_board['total'] = v_board.apply(axis=1, func=lambda row: sum(row.map(len)))
        column_label_map = {before: str(before)+'(th) week' for before in range(1, len(v_board.iloc[0])+1)}
        v_board.rename(columns=column_label_map, inplace=True)
        return v_board


if __name__ == "__main__":
    planner = AgitationPlannerGA(partition_size=4)
    print(planner.visualized_lecture_board().head(10))
    print(planner.visualized_members_board().head(10))

    print(lectureslistup.ModifiedAgiList().m_agilist.head(10))
