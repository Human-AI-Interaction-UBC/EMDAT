"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2011-08-25

Commonly used helper methods.

Authors: Samad Kardan (creator), Sebastien Lalle.
Institution: The University of British Columbia.
"""

from EMDAT_core.data_structures import Fixation
import params
import math


def point_inside_polygon(x,y,poly):
    """Determines if a point is inside a given polygon or not

        The algorithm is called "Ray Casting Method".

    Args:
        poly: is a list of (x,y) pairs defining the polgon

    Returns:
        True or False.
    """
    n = len(poly)

    if n==0:
        return False

    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def get_chunk(data, ind, start, end):
    """Returns index of first and last records in data that fall within a time interval (start-end)
    Args:
        data: a list of subsequent Fixations or Datapoints
        ind: an integer indicating the starting index in data for search, if not known
            should be set to zero.
        start: an integer indicating the start of interval in milliseconds
        end: an integer indicating the end of interval in milliseconds

    Returns:
        curr_ind: an integer indicating the index of the next record for search.
            This is useful if you are performing a series searches in a sequential manner.
            The method can start the next search from this index instead of beginning of the list.
        start_ind: an integer indicating the index of first record in the list that falls within
            the given time interval
        end_ind: an integer indicating the index of last record in the list that falls within
            the given time interval
    """
    datalen = len(data)
    curr_ind = ind
    if curr_ind < datalen:
        if isinstance(data[curr_ind],Fixation): #if it is a fixation
            if params.INCLUDE_HALF_FIXATIONS:
                while curr_ind < datalen and data[curr_ind].timestamp < start:
                    curr_ind += 1

                if data[curr_ind-1].fixationduration!= None: # if the last fixation before, is mostly in this segment
                    if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > start:
                        curr_ind -=1
                start_ind = curr_ind
                while curr_ind < datalen and (data[curr_ind].timestamp + (data[curr_ind].fixationduration)) <= end:
                    curr_ind += 1


                if curr_ind == start_ind:   # an empty chunk!
                    end_ind = curr_ind -1
                elif data[curr_ind-1].fixationduration!= None: # if the last fixation is mostly outside this segment
                    if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > end:
                        end_ind = curr_ind - 2
                    else:
                        end_ind = curr_ind -1
                else:
                    end_ind = curr_ind -1
            else:   #No half fixation inclusion
                while curr_ind < datalen and data[curr_ind].timestamp < start:
                    curr_ind += 1

                start_ind = curr_ind
                while curr_ind < datalen and (data[curr_ind].timestamp + (data[curr_ind].fixationduration)) <= end:
                    curr_ind += 1


                if curr_ind == start_ind:   # a no point chunk!
                    end_ind = curr_ind -1
                elif data[curr_ind-1].fixationduration!= None: # if the last fixation is mostly outside this segment
                    if (data[curr_ind-1].timestamp + (data[curr_ind-1].fixationduration)/2.0) > end:
                        end_ind = curr_ind - 2
                    else:
                        end_ind = curr_ind -1
                else:
                    end_ind = curr_ind -1
        else: # if this is not a Fixation we do not have to worry about half fixations
            while curr_ind < datalen and data[curr_ind].timestamp < start:
                curr_ind += 1

            start_ind = curr_ind
            while curr_ind < datalen and data[curr_ind].timestamp <= end:
                curr_ind += 1

            end_ind = curr_ind -1

        end_ind +=1 #because the last index is not inclusive in Python!
    else:
        curr_ind = start_ind = end_ind = datalen

    return curr_ind, start_ind, end_ind

def stddev(data):
    """Returns the standard deviation of a list of numbers

    Args:
        data: a list of numbers

    returns:
        a float that is the std deviation of the list of numbers or NAN if it is undefined
    """
    if len(data)< 2:
        return float('nan')
    m = mean(data)
    return math.sqrt(sum(map(lambda x: (x-m)**2, data))/float(len(data)-1))


def mean(data):
    """Returns the average of a list of numbers

    Args:
        data: a list of numbers

    returns:
        a float that is the average of the list of numbers
    """
    if len(data)==0:
        return 0
    return sum(data) / float(len(data))

def generate_event_lists(event_data):
    """Returns separate list per type of events. Format:
    Args:
        event_data: a list of "Event"s
    Returns:
        lists of left clics, right clics, double clics and keys pressed
    """
    leftc = []
    rightc = []
    doublec = []
    keyp = []
    double_clic_current = False
    time_prev_clic = -10000
    x_prev_clic = -10000
    y_prev_clic = -10000
    for e in event_data:
        if e.event == "KeyPress":
            keyp.append(e)
        elif e.event == "LeftMouseClick":
            if double_clic_current and (e.timestamp - time_prev_clic) <= 700 and (e.data1-x_prev_clic)<=10 and (e.data2-y_prev_clic)<=10: #We define here a a double clic as two clics in no more than 700ms in a same area
                doublec.append(e)
                double_clic_current = False
                leftc.pop()
            else: #no double clic
                leftc.append(e)
                double_clic_current = True
                time_prev_clic = e.timestamp
                x_prev_clic = e.data1
                y_prev_clic = e.data2
        elif e.event == "RightMouseClick":
            rightc.append(e)

    return (leftc, rightc, doublec, keyp)


def cast_float(string, invalid_value=None):
    """a helper method for converting strings to their float value

    Args:
        str: a string containing a number

    Returns:
        the float value of the string given or None if not a float
    """
    try:
        string_as_float = float(string)
        if string_as_float == invalid_value:
            return None
    except ValueError:
        return None
    return string_as_float


def cast_int(string, invalid_value=None):
    """a helper method for converting strings to their integer value

    Args:
        str: a string containing a number

    Returns:
        the integer value of the string given or None if not an integer
    """
    try:
        string_as_int = int(string)
        if string_as_int == invalid_value:
            return None
    except ValueError:
        return None
    return string_as_int

def list_to_string(list, separator = "\t"):
    """
    Converts a list of values to a string using SEPARATOR for joints

    Args:
        list: a list of values to be converted to a string

        separator:  a separator to be used for joints

    Returns:
        a string

    """
    return separator.join(map(str, list))+ "\n"
