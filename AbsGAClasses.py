from abc import ABC, abstractmethod


class Objective(ABC):
    @abstractmethod
    def evaluation(self):
        pass


class Solution(ABC):

    objective = None

    @abstractmethod
    def mutation(self):
        pass

    @abstractmethod
    def cross_over(self):
        pass

    @abstractmethod
    def string_table(self):
        pass
