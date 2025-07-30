# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from operator import gt, lt

from slice_to_offset_range import slice_to_offset_range
from split_interval import split_interval


class SliceAssignmentAction: pass


class NoAction(SliceAssignmentAction): pass


class ConcatenateLeft(SliceAssignmentAction):
    __slots__ = ('reverse',)

    def __new__(cls, reverse):
        instance = super(ConcatenateLeft, cls).__new__(cls)
        instance.reverse = reverse
        return instance


class ConcatenateRight(SliceAssignmentAction):
    __slots__ = ('reverse',)

    def __new__(cls, reverse):
        instance = super(ConcatenateRight, cls).__new__(cls)
        instance.reverse = reverse
        return instance


class ReplaceRange(SliceAssignmentAction):
    __slots__ = ('replaced_range',)

    def __new__(cls, replaced_range):
        instance = super(ReplaceRange, cls).__new__(cls)
        instance.replaced_range = replaced_range
        return instance


class Insert(SliceAssignmentAction):
    __slots__ = ('index', 'reverse')

    def __new__(cls, index, reverse):
        instance = super(Insert, cls).__new__(cls)
        instance.index = index
        instance.reverse = reverse
        return instance


def determine_slice_assignment_action(sequence_length, slice_object):
    # type: (int, slice) -> SliceAssignmentAction
    if sequence_length < 0:
        raise ValueError('sequence length must be non-negative')

    # `step > 0, start_index <= stop_index; step < 0, start_index >= stop_index`
    start_index, stop_index, step = slice_to_offset_range(slice_object, sequence_length)

    # No indices selected
    if start_index == stop_index:
        if start_index < 0:
            return ConcatenateLeft(reverse=step < 0)
        elif start_index < sequence_length:
            return Insert(start_index, reverse=step < 0)
        else:
            return ConcatenateRight(reverse=step < 0)
    # The sequence is empty
    elif sequence_length == 0:
        return ConcatenateRight(reverse=step < 0)
    else:
        if step > 0:
            # `start_index < stop_index`
            left, intersection, right = split_interval((0, sequence_length), (start_index, stop_index), lt)
            if intersection is not None:
                intersection_start, intersection_stop = intersection
                return ReplaceRange(range(intersection_start, intersection_stop, step))
            elif left is not None:
                return ConcatenateLeft(reverse=False)
            else:
                return ConcatenateRight(reverse=False)
        else:
            # `start_index > stop_index`
            reverse_left, reverse_intersection, reverse_right = split_interval((sequence_length - 1, -1),
                                                                               (start_index, stop_index), gt)
            if reverse_intersection is not None:
                reverse_intersection_start, reverse_intersection_stop = reverse_intersection
                return ReplaceRange(range(reverse_intersection_start, reverse_intersection_stop, step))
            elif reverse_left is not None:
                return ConcatenateRight(reverse=True)
            else:
                return ConcatenateLeft(reverse=True)
