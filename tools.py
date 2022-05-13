import pandas as pd
import numpy as np


class RandomSplitDataFrame:
    @staticmethod
    def split(dataframe: pd.DataFrame, partition_size: int) -> list[pd.DataFrame]:
        total_index = list(dataframe.index)
        np.random.shuffle(total_index)
        partitioned_indices = np.array_split(total_index, partition_size)

        list_of_split_df = []
        for index in partitioned_indices:
            list_of_split_df.append(dataframe.loc[index])

        return list_of_split_df
