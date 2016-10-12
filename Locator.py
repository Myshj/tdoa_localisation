import numpy


class Locator(object):
    def __init__(self, microphone_positions: list, speed_of_sound=340.29):
        self._speed_of_sound = speed_of_sound
        self._inverted_speed_of_sound = 1 / self._speed_of_sound
        self._count_of_microphones = len(microphone_positions)
        # self._initialize_source_position(source_position)
        self._initialize_microphone_positions(microphone_positions)
        # self._initialize_distances()
        #self._initialize_transit_times()
        #self._initialize_differences_in_transit_times()
        self._initialize_squared_microphone_positions()

        self._initialize_sums_for_abc()

    def locate(self, transit_times: list):
        self._initialize_transit_times(transit_times)
        self._initialize_differences_in_transit_times()

        self._initialize_column_a()
        self._initialize_column_b()
        self._initialize_column_c()
        self._initialize_column_d()

        self._left_matrix = numpy.column_stack((self._column_a, self._column_b, self._column_c))

        new_m = numpy.linalg.pinv(self._left_matrix)
        self._result = numpy.dot(new_m, self._column_d)

        return Locator.vector_to_dictionary(self._result)

    @staticmethod
    def dictionary_to_vector(dictionary: dict):
        return numpy.array([
            dictionary.get('x', 0.0),
            dictionary.get('y', 0.0),
            dictionary.get('z', 0.0)
        ])

    @staticmethod
    def vector_to_dictionary(vector: numpy.array):
        return {
            'x': vector[0],
            'y': vector[1],
            'z': vector[2]
        }

    # def _initialize_source_position(self, source_position: dict):
    #     self._source_position = Locator.dictionary_to_vector(source_position)

    def _initialize_microphone_positions(self, microphone_positions: list):
        self._microphone_positions = numpy.matrix([
                                                      Locator.dictionary_to_vector(microphone_position) for
                                                      microphone_position in microphone_positions
                                                      ])

    # def _initialize_distances(self):
    #     self._distances_between_microphones_and_source = numpy.array([
    #                                                                      numpy.linalg.norm(
    #                                                                          self._source_position - microphone_position
    #                                                                      ) for microphone_position in
    #                                                                      self._microphone_positions
    #                                                                      ])
    #
    def _initialize_transit_times(self, transit_times: list):
        self._transit_times_between_microphones_and_source = numpy.array(transit_times)
        self._transit_times_between_microphones_and_source / self._speed_of_sound

    def _initialize_differences_in_transit_times(self):
        self._differences_in_transit_times = numpy.array([
                                                             transit_time -
                                                             self._transit_times_between_microphones_and_source[0] for
                                                             transit_time in
                                                             self._transit_times_between_microphones_and_source
                                                             ])

    def _initialize_squared_microphone_positions(self):
        squared_microphone_positions = numpy.square(self._microphone_positions)
        self._sums_for_d = numpy.array([
                                           numpy.sum(squared_microphone_positions[i]) for i in
                                           range(0, self._count_of_microphones)
                                           ])

    def _initialize_sums_for_abc(self):
        self._sums_for_abc = 2 * self._microphone_positions - 2 * self._microphone_positions[0]

    def _initialize_column_a(self):
        self._column_a = numpy.zeros(self._count_of_microphones - 2)
        for i in range(2, self._count_of_microphones):
            self._column_a[i - 2] = self._calculate_element_for_column_a(i)

    def _calculate_element_for_column_a(self, i):
        return self._inverted_speed_of_sound / self._differences_in_transit_times[i] * self._sums_for_abc[i, 0] - \
               self._inverted_speed_of_sound / self._differences_in_transit_times[1] * self._sums_for_abc[1, 0]

    def _initialize_column_b(self):
        self._column_b = numpy.zeros(self._count_of_microphones - 2)
        for i in range(2, self._count_of_microphones):
            self._column_b[i - 2] = self._calculate_element_for_column_b(i)

    def _calculate_element_for_column_b(self, i):
        return self._inverted_speed_of_sound / self._differences_in_transit_times[i] * self._sums_for_abc[i, 1] - \
               self._inverted_speed_of_sound / self._differences_in_transit_times[1] * self._sums_for_abc[1, 1]

    def _initialize_column_c(self):
        self._column_c = numpy.zeros(self._count_of_microphones - 2)
        for i in range(2, self._count_of_microphones):
            self._column_c[i - 2] = self._calculate_element_for_column_c(i)

    def _calculate_element_for_column_c(self, i):
        return self._inverted_speed_of_sound / self._differences_in_transit_times[i] * self._sums_for_abc[i, 2] - \
               self._inverted_speed_of_sound / self._differences_in_transit_times[1] * self._sums_for_abc[1, 2]

    def _initialize_column_d(self):
        self._column_d = numpy.zeros(self._count_of_microphones - 2)
        for i in range(2, self._count_of_microphones):
            self._column_d[i - 2] = self._calculate_element_for_column_d(i)

    def _calculate_element_for_column_d(self, i):
        return -(
            self._speed_of_sound * (self._differences_in_transit_times[i] - self._differences_in_transit_times[1]) +
            self._inverted_speed_of_sound / self._differences_in_transit_times[i] * (
                self._sums_for_d[0] - self._sums_for_d[i]) - self._inverted_speed_of_sound /
            self._differences_in_transit_times[1] * (self._sums_for_d[0] - self._sums_for_d[1])
        )
