from pandas import DataFrame

class Data():
    dataset: DataFrame
    def __init__(self, df: DataFrame) -> None:
        self.dataset = df

    def getIdsColumns(self, pattern: str = r'^id$|_id$') -> list[str]:
        """
        Return the name of column that are ids column or contain 'id' not as a part of a word.
        """
        return self.dataset.columns[
                self.dataset.columns.str.contains(pattern, regex=True)
            ].tolist()